import json
from hashlib import sha256
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from burnlens.provider_acquisition import AcquisitionError
from burnlens.replacement_event_optical_contract import (
    CONTRACT_VERSION,
    EVENT_ID,
    POST_CONTRACT,
    PRE_CONTRACT,
    REPORT_ID,
    U01_BINDINGS,
    WARD_CREEK_CONTRACTS,
    WardCreekOpticalRun,
    acquire_ward_creek_optical_pair,
    build_intake_contract,
    refresh_ward_creek_metadata,
    _update_intake_contract_asset,
    validate_ward_creek_contracts,
    validate_ward_creek_metadata,
)


def metadata_payload(contract, acquisition, publication):
    return {
        "Id": contract.provider_id,
        "Name": contract.native_id,
        "ContentLength": contract.expected_size_bytes,
        "Online": True,
        "PublicationDate": publication,
        "S3Path": f"/eodata/test/{contract.native_id}",
        "ContentDate": {"Start": acquisition, "End": acquisition},
        "Checksum": [
            {"Algorithm": "MD5", "Value": contract.provider_md5},
            {"Algorithm": "BLAKE3", "Value": contract.provider_blake3},
        ],
    }


class FakeResponse:
    status = 200

    def __init__(self, payload):
        self.payload = json.dumps(payload).encode()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, _size):
        return self.payload

    def getcode(self):
        return 200


class SequenceOpen:
    def __init__(self, payloads):
        self.payloads = list(payloads)

    def __call__(self, _request, timeout=60):
        del timeout
        return FakeResponse(self.payloads.pop(0))


class ReplacementEventOpticalContractTests(unittest.TestCase):
    def test_exact_pair_contract_and_identity(self):
        self.assertEqual(CONTRACT_VERSION, "ward-creek-optical-intake-contract-v0.1.0")
        self.assertEqual(EVENT_ID, "OR4494912090120190812")
        self.assertEqual(REPORT_ID, "WARD-CREEK-OPTICAL-CUSTODY-2026-001")
        self.assertEqual(validate_ward_creek_contracts(), [])
        self.assertEqual(sum(item.expected_size_bytes for item in WARD_CREEK_CONTRACTS), 2_396_820_201)
        self.assertEqual(PRE_CONTRACT.provider_id, "f6b6697d-5b7d-4049-8caf-8b0c7fdad4b7")
        self.assertEqual(POST_CONTRACT.provider_id, "51ddb0b7-8456-40a2-8301-e1651c951116")

    def test_every_u01_binding_matches_the_exact_repository_bytes(self):
        root = Path(__file__).resolve().parents[1]
        for relative, (expected_size, expected_sha256) in U01_BINDINGS.items():
            payload = (root / relative).read_bytes()
            self.assertEqual(len(payload), expected_size, relative)
            self.assertEqual(sha256(payload).hexdigest(), expected_sha256, relative)

    def test_live_metadata_must_match_both_exact_products(self):
        opener = SequenceOpen(
            [
                metadata_payload(
                    PRE_CONTRACT,
                    "2019-08-01T18:59:21.024000Z",
                    "2024-04-13T14:52:27.028094Z",
                ),
                metadata_payload(
                    POST_CONTRACT,
                    "2019-08-31T18:59:21.024000Z",
                    "2023-11-30T19:34:35.294111Z",
                ),
            ]
        )
        snapshot = refresh_ward_creek_metadata(
            observed_at_utc="2026-07-24T20:00:00Z",
            urlopen_fn=opener,
        )
        self.assertEqual(validate_ward_creek_metadata(snapshot), [])
        snapshot["records"][1]["online"] = False
        self.assertIn("ward-creek-2019-post:OFFLINE", validate_ward_creek_metadata(snapshot))

    def test_run_paths_are_disjoint_and_repository_local(self):
        with tempfile.TemporaryDirectory() as temporary:
            run = WardCreekOpticalRun.create(
                repository_root=Path(temporary),
                generated_at_utc="2026-07-24T20:00:00Z",
            )
            self.assertNotEqual(run.quarantine(PRE_CONTRACT.role), run.quarantine(POST_CONTRACT.role))
            self.assertNotEqual(run.destination(PRE_CONTRACT), run.destination(POST_CONTRACT))
            self.assertIn("P2O4-T39-U02", run.aggregate_state.as_posix())
            self.assertEqual(run.tracked_report.name, f"{REPORT_ID}.json")

    def test_controlled_intake_contract_is_exact_and_secret_free(self):
        with tempfile.TemporaryDirectory() as temporary:
            run = WardCreekOpticalRun.create(
                repository_root=Path(temporary),
                generated_at_utc="2026-07-24T20:00:00Z",
            )
            contract = build_intake_contract(run)
            self.assertEqual(contract["intake_id"], "p2o4-t39-u02-ward-creek-optical-r001")
            self.assertEqual([item["asset_id"] for item in contract["assets"]], [PRE_CONTRACT.role, POST_CONTRACT.role])
            self.assertTrue(all(item["state"] == "authorized" for item in contract["assets"]))
            self.assertNotIn("password", json.dumps(contract).lower())
            self.assertNotIn("token", json.dumps(contract).lower())

    def test_controlled_intake_contract_records_exact_promoted_identity(self):
        with tempfile.TemporaryDirectory() as temporary:
            run = WardCreekOpticalRun.create(
                repository_root=Path(temporary),
                generated_at_utc="2026-07-24T20:00:00Z",
            )
            run.intake_contract.parent.mkdir(parents=True)
            run.intake_contract.write_text(
                json.dumps(build_intake_contract(run)) + "\n",
                encoding="utf-8",
            )
            _update_intake_contract_asset(
                run=run,
                contract=PRE_CONTRACT,
                attempts=[{"outcome": "succeeded"}],
                state="promoted",
                local_sha256="a" * 64,
            )
            payload = json.loads(run.intake_contract.read_text(encoding="utf-8"))
            asset = payload["assets"][0]
            self.assertEqual(asset["state"], "promoted")
            self.assertEqual(asset["observed"]["promoted_sha256"], "a" * 64)
            self.assertEqual(asset["attempts"][0]["outcome"], "succeeded")

    def test_post_is_unreachable_when_pre_transaction_fails(self):
        with tempfile.TemporaryDirectory() as temporary:
            run = WardCreekOpticalRun.create(
                repository_root=Path(temporary),
                generated_at_utc="2026-07-24T20:00:00Z",
            )
            snapshot = {
                "observed_at_utc": "2026-07-24T20:00:00Z",
                "source_record_id": "SOURCE-2026-038",
                "terms_review_id": "TERMS-2026-033",
                "live_refresh_performed": True,
                "records": [
                    {
                        "role": contract.role,
                        "event_id": EVENT_ID,
                        "event_group_id": "event-ward-creek-2019",
                        "provider_id": contract.provider_id,
                        "native_id": contract.native_id,
                        "size_bytes": contract.expected_size_bytes,
                        "online": True,
                        "acquisition_utc": (
                            "2019-08-01T18:59:21.024000Z"
                            if contract == PRE_CONTRACT
                            else "2019-08-31T18:59:21.024000Z"
                        ),
                        "publication_utc": (
                            "2024-04-13T14:52:27.028094Z"
                            if contract == PRE_CONTRACT
                            else "2023-11-30T19:34:35.294111Z"
                        ),
                        "s3_path": f"/x/{contract.native_id}",
                        "provider_checksums": {
                            "MD5": contract.provider_md5,
                            "BLAKE3": contract.provider_blake3,
                        },
                    }
                    for contract in WARD_CREEK_CONTRACTS
                ],
            }
            calls = []
            with patch(
                "burnlens.replacement_event_optical_contract._acquire_singleton",
                side_effect=lambda **kwargs: calls.append(kwargs["contract"].role)
                or (_ for _ in ()).throw(AcquisitionError("TEST_PRE_FAILURE")),
            ):
                with self.assertRaisesRegex(AcquisitionError, "TEST_PRE_FAILURE"):
                    acquire_ward_creek_optical_pair(
                        run=run,
                        commit="a" * 40,
                        credentials=type("Credentials", (), {"username": "x", "password": "y"})(),
                        metadata_snapshot=snapshot,
                    )
            self.assertEqual(calls, [PRE_CONTRACT.role])


if __name__ == "__main__":
    unittest.main()
