from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs

from burnlens.petes_lake_reference_request import (
    CROSS_PROGRAM_MAPPING_PRODUCTS,
    CUSTODY_PATHS,
    EVENT_ID,
    EXPECTED_PRODUCT,
    MAP_ID,
    MTBS_MAPPING_PRODUCTS,
    PetesLakeReferenceRequestError,
    acquire_request_receipt,
    normalize_metadata,
    request_payload,
)


def metadata_bytes() -> bytes:
    names = {
        "catalog_id": "id",
        "map_id": "map_id",
        "program": "map_prog",
        "incident_name": "incid_name",
        "event_id": "event_id",
        "assessment_type": "asmt_type",
        "boundary_acres": "burnbndac",
        "post_id": "post_id",
        "model": "model",
        "dnbr_offset": "dnbr_offst",
        "dnbr_stddev": "dnbr_stddv",
        "nodata_threshold": "nodata_t",
        "increased_greenness_threshold": "incgreen_t",
        "low_threshold": "low_t",
        "moderate_threshold": "mod_t",
        "high_threshold": "high_t",
        "provider_comment": "comment",
        "nonstandard": "nonstandard",
    }
    properties = {target: EXPECTED_PRODUCT[source] for source, target in names.items()}
    properties["ig_date"] = EXPECTED_PRODUCT["ignition_date"] + "Z"
    properties["postfire_date"] = EXPECTED_PRODUCT["postfire_date"] + "Z"
    return json.dumps(
        {
            "type": "FeatureCollection",
            "features": [{"type": "Feature", "geometry": None, "properties": properties}],
        }
    ).encode()


class Response:
    def __init__(self, data: bytes) -> None:
        self.data = data
        self.status = 200

    def __enter__(self) -> "Response":
        return self

    def __exit__(self, *_: object) -> None:
        return None

    def read(self, maximum: int) -> bytes:
        return self.data[:maximum]


class PetesLakeReferenceRequestTests(unittest.TestCase):
    def custody(self, root: Path) -> tuple[Path, Path]:
        (root / ".git").mkdir()
        (root / "pyproject.toml").write_text("[project]\nname='burnlens'\n")
        return root, root / CUSTODY_PATHS["request_directory"]

    def test_exact_metadata_and_mtbs_only_payload_pass(self) -> None:
        self.assertEqual(normalize_metadata(metadata_bytes()), EXPECTED_PRODUCT)
        payload = request_payload()
        self.assertEqual(payload["projection"], "UTM")
        self.assertEqual(payload["mapping_ids"], [MAP_ID])
        self.assertEqual(tuple(payload["mapping_products"]), MTBS_MAPPING_PRODUCTS)
        combined = " ".join(payload["mapping_products"]).casefold()
        for disallowed in ("soil burn", "basal area", "canopy cover", "composite burn"):
            self.assertNotIn(disallowed, combined)
        self.assertEqual(len(CROSS_PROGRAM_MAPPING_PRODUCTS), 8)

    def test_metadata_identity_or_warning_drift_fails_closed(self) -> None:
        for field, value in (("map_id", 1), ("comment", None), ("id", 50884)):
            changed = json.loads(metadata_bytes())
            changed["features"][0]["properties"][field] = value
            with self.assertRaisesRegex(PetesLakeReferenceRequestError, "drifted"):
                normalize_metadata(json.dumps(changed).encode())

    def test_receipt_is_atomic_private_and_no_overwrite(self) -> None:
        queue = b'{"success":true}'
        captured = []

        def open_response(request: object, **_: object) -> Response:
            captured.append(request)
            return Response(metadata_bytes() if len(captured) == 1 else queue)

        with TemporaryDirectory() as directory, patch(
            "burnlens.petes_lake_reference_request.urlopen", side_effect=open_response
        ):
            repository_root, output = self.custody(Path(directory))
            receipt = acquire_request_receipt(
                output,
                repository_root=repository_root,
                recipient="owner@example.com",
                requested_at_utc="2026-07-21T23:00:00Z",
                run_id="BL-TEST-PETES-LAKE-REFERENCE-REQUEST",
                git_source_commit="a" * 40,
            )
            self.assertEqual(receipt["event_id"], EVENT_ID)
            self.assertEqual(receipt["map_id"], MAP_ID)
            self.assertEqual(
                receipt["frozen_reference_identity"]["pre_image_id"],
                "904502920230801",
            )
            self.assertEqual(
                receipt["frozen_reference_identity"]["catalog_id_frozen"], 50884
            )
            self.assertEqual(receipt["custody_contract"]["request_directory"], CUSTODY_PATHS["request_directory"])
            self.assertEqual(
                receipt["request"]["excluded_cross_program_mapping_products"],
                list(CROSS_PROGRAM_MAPPING_PRODUCTS),
            )
            self.assertTrue(receipt["metadata"]["threshold_fields_are_raw_provider_fields"])
            self.assertEqual(receipt["request"]["recipient"], "WITHHELD_PRIVATE")
            self.assertEqual(receipt["git_source_commit"], "a" * 40)
            body = parse_qs(captured[1].data.decode())
            self.assertEqual(body["email"], ["owner@example.com"])
            products = json.loads(body["products"][0])
            self.assertEqual(products["mapping_ids"], [MAP_ID])
            combined = b"".join(path.read_bytes() for path in output.iterdir())
            self.assertNotIn(b"owner@example.com", combined)
            self.assertTrue((output / "request-prepared.json").is_file())
            self.assertTrue((output / "queue-attempt-started.json").is_file())
            with self.assertRaisesRegex(PetesLakeReferenceRequestError, "no overwrite"):
                acquire_request_receipt(
                    output,
                    repository_root=repository_root,
                    recipient="owner@example.com",
                    requested_at_utc="2026-07-21T23:00:00Z",
                    run_id="BL-TEST-PETES-LAKE-REFERENCE-REQUEST",
                    git_source_commit="a" * 40,
                )

    def test_ambiguous_queue_attempt_is_retained_and_never_overwritten(self) -> None:
        calls = 0

        def open_response(_: object, **__: object) -> Response:
            nonlocal calls
            calls += 1
            if calls == 1:
                return Response(metadata_bytes())
            raise OSError("synthetic timeout")

        with TemporaryDirectory() as directory, patch(
            "burnlens.petes_lake_reference_request.urlopen", side_effect=open_response
        ):
            repository_root, output = self.custody(Path(directory))
            with self.assertRaisesRegex(PetesLakeReferenceRequestError, "outcome is unknown"):
                acquire_request_receipt(
                    output,
                    repository_root=repository_root,
                    recipient="owner@example.com",
                    requested_at_utc="2026-07-21T23:00:00Z",
                    run_id="BL-TEST-PETES-LAKE-REFERENCE-REQUEST-AMBIGUOUS",
                    git_source_commit="b" * 40,
                )
            state = json.loads((output / "queue-outcome-unknown.json").read_text())
            self.assertEqual(state["state"], "QUEUE_OUTCOME_UNKNOWN_DO_NOT_RETRY")
            combined = b"".join(path.read_bytes() for path in output.iterdir())
            self.assertNotIn(b"owner@example.com", combined)
            with self.assertRaisesRegex(PetesLakeReferenceRequestError, "no overwrite"):
                acquire_request_receipt(
                    output,
                    repository_root=repository_root,
                    recipient="owner@example.com",
                    requested_at_utc="2026-07-21T23:00:00Z",
                    run_id="BL-TEST-PETES-LAKE-REFERENCE-REQUEST-AMBIGUOUS",
                    git_source_commit="b" * 40,
                )

    def test_explicit_queue_reject_is_retained_without_retry(self) -> None:
        responses = [Response(metadata_bytes()), Response(b'{"success":false}')]
        with TemporaryDirectory() as directory, patch(
            "burnlens.petes_lake_reference_request.urlopen", side_effect=responses
        ):
            repository_root, output = self.custody(Path(directory))
            with self.assertRaisesRegex(PetesLakeReferenceRequestError, "did not accept"):
                acquire_request_receipt(
                    output,
                    repository_root=repository_root,
                    recipient="owner@example.com",
                    requested_at_utc="2026-07-21T23:00:00Z",
                    run_id="BL-TEST-PETES-LAKE-REFERENCE-REQUEST-REJECTED",
                    git_source_commit="c" * 40,
                )
            failure = json.loads((output / "queue-explicit-failure.json").read_text())
            self.assertEqual(
                failure["state"],
                "QUEUE_EXPLICIT_RESPONSE_REJECTED_OR_INVALID_DO_NOT_RETRY",
            )
            self.assertEqual((output / "queue-response.json").read_bytes(), b'{"success":false}')
            self.assertFalse((output / "request-receipt.json").exists())

    def test_invalid_recipient_fails_before_creating_custody(self) -> None:
        with TemporaryDirectory() as directory:
            repository_root, output = self.custody(Path(directory))
            with self.assertRaisesRegex(PetesLakeReferenceRequestError, "recipient"):
                acquire_request_receipt(
                    output,
                    repository_root=repository_root,
                    recipient="",
                    requested_at_utc="2026-07-21T23:00:00Z",
                    run_id="BL-TEST-PETES-LAKE-REFERENCE-REQUEST-BAD-RECIPIENT",
                    git_source_commit="d" * 40,
                )
            self.assertFalse(output.exists())

    def test_noncontract_output_path_fails_before_network_or_custody(self) -> None:
        with TemporaryDirectory() as directory:
            repository_root, _ = self.custody(Path(directory))
            output = repository_root / "downloads" / "wrong"
            with self.assertRaisesRegex(PetesLakeReferenceRequestError, "custody contract"):
                acquire_request_receipt(
                    output,
                    repository_root=repository_root,
                    recipient="owner@example.com",
                    requested_at_utc="2026-07-21T23:00:00Z",
                    run_id="BL-TEST-PETES-LAKE-REFERENCE-REQUEST-WRONG-CUSTODY",
                    git_source_commit="e" * 40,
                )
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
