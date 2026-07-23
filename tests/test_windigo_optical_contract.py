import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from burnlens.provider_acquisition import AcquisitionError
from burnlens.windigo_optical_contract import (
    CONTRACT_VERSION,
    EVENT_ID,
    POST_CONTRACT,
    PRE_CONTRACT,
    REPORT_ID,
    WINDIGO_CONTRACTS,
    WindigoOpticalRun,
    WindigoTrace,
    _acquire_singleton,
    _resumable_pre_bytes,
    acquire_windigo_optical_pair,
    refresh_windigo_metadata,
    validate_windigo_contracts,
    validate_windigo_metadata,
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


class WindigoOpticalContractTests(unittest.TestCase):
    def test_exact_pair_contract_and_identity(self):
        self.assertEqual(CONTRACT_VERSION, "windigo-optical-intake-contract-v0.1.0")
        self.assertEqual(EVENT_ID, "OR4336312205020220730")
        self.assertEqual(REPORT_ID, "WINDIGO-OPTICAL-CUSTODY-2026-001")
        self.assertEqual(validate_windigo_contracts(), [])
        self.assertEqual(sum(item.expected_size_bytes for item in WINDIGO_CONTRACTS), 2_373_112_076)
        self.assertEqual(PRE_CONTRACT.provider_id, "f1111cd2-acb1-4324-9b48-854e2e71a384")
        self.assertEqual(POST_CONTRACT.provider_id, "10bb27c6-5df5-44f1-9a72-517c696cb5e1")

    def test_live_metadata_must_match_both_exact_products(self):
        opener = SequenceOpen(
            [
                metadata_payload(
                    PRE_CONTRACT,
                    "2022-07-26T18:59:31.024000Z",
                    "2024-12-24T07:06:56.947635Z",
                ),
                metadata_payload(
                    POST_CONTRACT,
                    "2022-08-15T18:59:31.024000Z",
                    "2025-03-18T00:52:08.078142Z",
                ),
            ]
        )
        snapshot = refresh_windigo_metadata(
            observed_at_utc="2026-07-23T18:00:00Z",
            urlopen_fn=opener,
        )
        self.assertEqual(validate_windigo_metadata(snapshot), [])
        snapshot["records"][1]["online"] = False
        self.assertIn("windigo-2022-post:OFFLINE", validate_windigo_metadata(snapshot))

    def test_run_paths_are_disjoint_and_repository_local(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            run = WindigoOpticalRun.create(
                repository_root=root,
                generated_at_utc="2026-07-23T18:00:00Z",
            )
            self.assertNotEqual(run.pre_quarantine, run.post_quarantine)
            self.assertNotEqual(run.pre_destination, run.post_destination)
            self.assertIn("P2O4-T35-U02", run.aggregate_state.as_posix())
            self.assertEqual(run.tracked_report.name, f"{REPORT_ID}.json")

    def test_post_is_unreachable_when_pre_transaction_fails(self):
        with tempfile.TemporaryDirectory() as temporary:
            run = WindigoOpticalRun.create(
                repository_root=Path(temporary),
                generated_at_utc="2026-07-23T18:00:00Z",
            )
            snapshot = {
                "observed_at_utc": "2026-07-23T18:00:00Z",
                "source_record_id": "SOURCE-2026-036",
                "terms_review_id": "TERMS-2026-031",
                "live_refresh_performed": True,
                "records": [
                    {
                        "role": PRE_CONTRACT.role,
                        "event_id": EVENT_ID,
                        "event_group_id": "event-windigo-2022",
                        "provider_id": PRE_CONTRACT.provider_id,
                        "native_id": PRE_CONTRACT.native_id,
                        "size_bytes": PRE_CONTRACT.expected_size_bytes,
                        "online": True,
                        "acquisition_utc": "2022-07-26T18:59:31.024000Z",
                        "publication_utc": "2024-12-24T07:06:56.947635Z",
                        "s3_path": f"/x/{PRE_CONTRACT.native_id}",
                        "provider_checksums": {
                            "MD5": PRE_CONTRACT.provider_md5,
                            "BLAKE3": PRE_CONTRACT.provider_blake3,
                        },
                    },
                    {
                        "role": POST_CONTRACT.role,
                        "event_id": EVENT_ID,
                        "event_group_id": "event-windigo-2022",
                        "provider_id": POST_CONTRACT.provider_id,
                        "native_id": POST_CONTRACT.native_id,
                        "size_bytes": POST_CONTRACT.expected_size_bytes,
                        "online": True,
                        "acquisition_utc": "2022-08-15T18:59:31.024000Z",
                        "publication_utc": "2025-03-18T00:52:08.078142Z",
                        "s3_path": f"/x/{POST_CONTRACT.native_id}",
                        "provider_checksums": {
                            "MD5": POST_CONTRACT.provider_md5,
                            "BLAKE3": POST_CONTRACT.provider_blake3,
                        },
                    },
                ],
            }
            calls = []
            with patch(
                "burnlens.windigo_optical_contract._acquire_singleton",
                side_effect=lambda **kwargs: calls.append(kwargs["contract"].role)
                or (_ for _ in ()).throw(AcquisitionError("TEST_PRE_FAILURE")),
            ):
                with self.assertRaisesRegex(AcquisitionError, "TEST_PRE_FAILURE"):
                    acquire_windigo_optical_pair(
                        run=run,
                        trace=type("Trace", (), {"as_dict": lambda self: {}})(),
                        credentials=type("Credentials", (), {"username": "x", "password": "y"})(),
                        metadata_snapshot=snapshot,
                    )
            self.assertEqual(calls, [PRE_CONTRACT.role])

    def test_singleton_retains_each_retryable_failure_before_success(self):
        with tempfile.TemporaryDirectory() as temporary:
            run = WindigoOpticalRun.create(
                repository_root=Path(temporary),
                generated_at_utc="2026-07-23T18:00:00Z",
            )
            run.pre_state.parent.mkdir(parents=True)
            results = [
                AcquisitionError("DOWNLOAD_EARLY_EOF", role=PRE_CONTRACT.role),
                AcquisitionError("DOWNLOAD_REQUEST_FAILED", role=PRE_CONTRACT.role),
                {"status": "DOWNLOADED", "bytes": PRE_CONTRACT.expected_size_bytes},
            ]
            verification = {
                "accepted_as_unchanged_registered_package": True,
                "observations": [],
                "registration": {},
                "registration_manifest_sha256": "a" * 64,
            }
            with patch(
                "burnlens.windigo_optical_contract.stream_cdse_asset_with_retries",
                side_effect=results,
            ), patch(
                "burnlens.windigo_optical_contract.promote_quarantine_no_overwrite",
                return_value={"run_id": "run"},
            ), patch(
                "burnlens.windigo_optical_contract.verify_registered_package",
                return_value=verification,
            ), patch(
                "burnlens.windigo_optical_contract.write_private_state"
            ) as writer:
                state = _acquire_singleton(
                    run=run,
                    trace=WindigoTrace(git_source_commit="a" * 40),
                    credentials=type("Credentials", (), {"username": "x", "password": "y"})(),
                    contract=PRE_CONTRACT,
                    metadata_record={"role": PRE_CONTRACT.role},
                    quarantine=run.pre_quarantine,
                    destination=run.pre_destination,
                    state_path=run.pre_state,
                    run_id="BL-2026-07-23-windigo-optical-pre-r001",
                    progress=None,
                )
            self.assertEqual([item["outcome"] for item in state["attempts"]], ["failed", "failed", "succeeded"])
            self.assertEqual(state["download"]["attempt_count"], 3)
            writer.assert_called_once()

    def test_only_exact_single_link_pre_partial_is_resumable(self):
        with tempfile.TemporaryDirectory() as temporary:
            run = WindigoOpticalRun.create(
                repository_root=Path(temporary),
                generated_at_utc="2026-07-23T18:00:00Z",
            )
            run.pre_quarantine.mkdir(parents=True)
            part = run.pre_quarantine / f"{PRE_CONTRACT.expected_filename}.part"
            part.write_bytes(b"PK\x03\x04" + b"x" * 12)
            self.assertEqual(_resumable_pre_bytes(run), 16)
            (run.pre_quarantine / "unexpected").write_bytes(b"x")
            with self.assertRaisesRegex(AcquisitionError, "RESUME_ROSTER"):
                _resumable_pre_bytes(run)


if __name__ == "__main__":
    unittest.main()
