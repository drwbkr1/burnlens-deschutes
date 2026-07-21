from __future__ import annotations

from dataclasses import replace
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from urllib.request import Request

from burnlens import acquire_petes_lake_optical as acquire_cli
from burnlens.petes_lake_optical_contract import (
    CONTRACT_VERSION,
    EXPECTED_METADATA,
    PAIR_ID,
    PETES_LAKE_CONTRACTS,
    POST_CONTRACT,
    PRE_CONTRACT,
    REPORT_ID,
    CdseCredentials,
    PetesLakeOpticalRun,
    PetesLakeTrace,
    _transaction_matches_fresh_verification,
    _write_success_outputs,
    acquire_petes_lake_optical_pair,
    assert_no_overwrite_targets,
    finalize_petes_lake_aggregate_only,
    refresh_petes_lake_metadata,
    resume_petes_lake_post_only,
    validate_petes_lake_contracts,
    validate_petes_lake_metadata,
    validate_u03_prerequisite,
)
from burnlens.provider_acquisition import AcquisitionError
from burnlens.provider_acquisition import write_private_state as provider_write_private_state


class FakeResponse:
    def __init__(self, payload: dict) -> None:
        self._stream = io.BytesIO(json.dumps(payload).encode("utf-8"))
        self.status = 200

    def read(self, size: int = -1) -> bytes:
        return self._stream.read(size)

    def getcode(self) -> int:
        return self.status

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        return None


def metadata_payload(contract=PRE_CONTRACT) -> dict:
    expected = EXPECTED_METADATA[contract.role]
    return {
        "Id": contract.provider_id,
        "Name": contract.native_id,
        "ContentLength": contract.expected_size_bytes,
        "Online": True,
        "ContentDate": {"Start": expected["acquisition_utc"]},
        "PublicationDate": "2026-07-21T00:00:00Z",
        "S3Path": f"/eodata/Sentinel-2/MSI/L2A/{contract.native_id}",
        "Checksum": [
            {"Algorithm": "MD5", "Value": contract.provider_md5},
            {"Algorithm": "BLAKE3", "Value": contract.provider_blake3},
        ],
        "Attributes": [
            {"Name": "platformSerialIdentifier", "Value": expected["platform_serial_identifier"]},
            {"Name": "tileId", "Value": expected["tile_id"]},
            {"Name": "relativeOrbitNumber", "Value": expected["relative_orbit_number"]},
            {"Name": "processorVersion", "Value": expected["processor_version"]},
            {"Name": "productType", "Value": expected["product_type"]},
            {"Name": "cloudCover", "Value": expected["cloud_cover_percent"]},
        ],
    }


def exact_metadata_snapshot() -> dict:
    payloads = {item.provider_id: metadata_payload(item) for item in PETES_LAKE_CONTRACTS}

    def fake_urlopen(request: Request, timeout: float) -> FakeResponse:
        provider_id = next(key for key in payloads if key in request.full_url)
        return FakeResponse(payloads[provider_id])

    return refresh_petes_lake_metadata(
        observed_at_utc="2026-07-21T16:30:00Z",
        urlopen_fn=fake_urlopen,
    )


def role_metadata_snapshot(contract, *, observed_at_utc: str) -> dict:
    snapshot = exact_metadata_snapshot()
    snapshot["observed_at_utc"] = observed_at_utc
    snapshot["records"] = [
        item for item in snapshot["records"] if item["role"] == contract.role
    ]
    return snapshot


def synthetic_trace() -> PetesLakeTrace:
    return PetesLakeTrace(
        git_source_commit="1" * 40,
        branch="codex/p2o4-t33-petes-lake-milestone",
        task_issue=521,
        git_base_commit="0d41942dc6c3c307a9a146a2d38fb816e038bb42",
        u01_entry_commit="f59b874d92a0e86d0121759d1c40fbe8ba5c2edc",
        entry_gate_path="samples/cross-event/phase-two/petes-lake/PETES-LAKE-ENTRY-GATE-2026-001.json",
        entry_gate_bytes=18_270,
        entry_gate_sha256="ac5d7498f847e0df973c58445188b422d919dc5c195e832e518ba5dbf11d6bec",
    )


def local_private_state_writer(run, path: Path, payload: dict) -> None:
    provider_write_private_state(path, payload)


def fake_registration(contract, run_id: str) -> dict:
    return {
        "registration_schema_version": "0.2.0",
        "contract_version": CONTRACT_VERSION,
        "package_id": contract.package_id,
        "generated_at_utc": "2026-07-21T16:30:00Z",
        "run_id": run_id,
        "asset_count": 1,
        "assets": [
            {
                "role": contract.role,
                "source_record_id": contract.source_record_id,
                "native_id": contract.native_id,
                "filename": contract.expected_filename,
                "bytes": contract.expected_size_bytes,
                "sha256": "a" * 64,
                "md5": contract.provider_md5,
                "blake3": contract.provider_blake3,
            }
        ],
    }


def synthetic_transaction(run, contract, run_id: str, observed_at_utc: str) -> dict:
    registration = fake_registration(contract, run_id)
    return {
        "unit_id": "P2O4-T33-U02",
        "generated_at_utc": run.generated_at_utc,
        "event_id": "OR4396912190120230825",
        "event_group_id": "event-petes-lake-2023",
        "pair_id": PAIR_ID,
        "run_id": run_id,
        "role": contract.role,
        "package_id": contract.package_id,
        "contract_version": CONTRACT_VERSION,
        "trace": synthetic_trace().as_dict(),
        "metadata_snapshot": role_metadata_snapshot(
            contract, observed_at_utc=observed_at_utc
        ),
        "contract": {"role": contract.role, "package_id": contract.package_id},
        "quarantine_path": "downloads/phase-two/quarantine/synthetic",
        "destination_path": f"downloads/phase-two/raw/{contract.package_id}",
        "decision": "REGISTERED_EXACT_PETES_LAKE_SINGLETON",
        "credentials_exercised": True,
        "download": {"status": "SYNTHETIC_TEST_DOUBLE"},
        "registration": registration,
        "verification": {
            "accepted_as_unchanged_registered_package": True,
            "registration": registration,
        },
        "disposition": "pass",
        "next_dependency": "P2O4-T33-U03",
    }


class PetesLakeOpticalContractTests(unittest.TestCase):
    def test_exact_pair_is_ordered_and_uses_two_singleton_packages(self) -> None:
        self.assertEqual(validate_petes_lake_contracts(PETES_LAKE_CONTRACTS), [])
        self.assertEqual([item.role for item in PETES_LAKE_CONTRACTS], [
            "petes-lake-2023-pre",
            "petes-lake-2023-post",
        ])
        self.assertNotEqual(PRE_CONTRACT.package_id, POST_CONTRACT.package_id)
        self.assertEqual(
            sum(item.expected_size_bytes for item in PETES_LAKE_CONTRACTS),
            2_428_352_361,
        )

    def test_reorder_identity_or_checksum_drift_fails_closed(self) -> None:
        self.assertIn(
            "PETES_LAKE_ORDERED_PAIR_CONTRACT_MISMATCH",
            validate_petes_lake_contracts(tuple(reversed(PETES_LAKE_CONTRACTS))),
        )
        changed = replace(POST_CONTRACT, provider_md5="0" * 32)
        self.assertIn(
            "PETES_LAKE_ORDERED_PAIR_CONTRACT_MISMATCH",
            validate_petes_lake_contracts((PRE_CONTRACT, changed)),
        )

    def test_live_metadata_accepts_only_exact_ordered_odata_contract(self) -> None:
        snapshot = exact_metadata_snapshot()
        self.assertEqual(validate_petes_lake_metadata(snapshot), [])
        self.assertEqual(
            [item["role"] for item in snapshot["records"]],
            [PRE_CONTRACT.role, POST_CONTRACT.role],
        )
        self.assertEqual(snapshot["records"][1]["catalogue_snow_percent"], 9.841206)
        self.assertNotIn("stable_route", json.dumps(snapshot))

    def test_metadata_checksum_and_role_order_drift_fail_closed(self) -> None:
        snapshot = exact_metadata_snapshot()
        snapshot["records"][0]["provider_checksums"]["MD5"] = "0" * 32
        self.assertIn(f"{PRE_CONTRACT.role}:MD5", validate_petes_lake_metadata(snapshot))
        snapshot = exact_metadata_snapshot()
        snapshot["records"].reverse()
        self.assertIn("METADATA_ORDERED_ROLE_SET_MISMATCH", validate_petes_lake_metadata(snapshot))

    def test_run_contract_derives_exact_bound_r001_paths_and_ids(self) -> None:
        with TemporaryDirectory() as directory:
            run = PetesLakeOpticalRun.create(
                repository_root=Path(directory),
                generated_at_utc="2026-07-21T16:30:00Z",
                revision="r001",
            )
            self.assertEqual(run.pre_run_id, "BL-2026-07-21-petes-lake-optical-pre-r001")
            self.assertEqual(run.post_run_id, "BL-2026-07-21-petes-lake-optical-post-r001")
            self.assertEqual(
                run.aggregate_run_id,
                "BL-2026-07-21-petes-lake-optical-intake-r001",
            )
            self.assertEqual(run.pre_destination.name, "petes-lake-s2-optical-pre-v0.1.0")
            self.assertEqual(run.post_destination.name, "petes-lake-s2-optical-post-v0.1.0")
            self.assertEqual(run.tracked_report.name, f"{REPORT_ID}.json")

    def test_run_contract_rejects_ambiguous_timestamp_and_revision(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaisesRegex(ValueError, "UTC Z"):
                PetesLakeOpticalRun.create(
                    repository_root=root,
                    generated_at_utc="2026-07-21T16:30:00+00:00",
                    revision="r001",
                )
            with self.assertRaisesRegex(ValueError, "r001 through r999"):
                PetesLakeOpticalRun.create(
                    repository_root=root,
                    generated_at_utc="2026-07-21T16:30:00Z",
                    revision="r000",
                )

    def test_full_remediation_uses_new_ids_without_overwriting_retained_r001_failure(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            retained_quarantine = (
                root
                / "downloads"
                / "phase-two"
                / "quarantine"
                / "P2O4-T33-U02"
                / "petes-lake-optical-pre-r001"
            )
            retained_quarantine.mkdir(parents=True)
            retained_state = (
                root
                / "downloads"
                / "phase-two"
                / "runs"
                / "P2O4-T33-U02"
                / "BL-2026-07-21-petes-lake-optical-pre-r001.json"
            )
            retained_state.parent.mkdir(parents=True, exist_ok=True)
            retained_state.write_text("retained failure\n", encoding="utf-8")
            run = PetesLakeOpticalRun.create(
                repository_root=root,
                generated_at_utc="2026-07-21T20:00:00Z",
                revision="r002",
                mode="full-remediation",
            )
            self.assertTrue(run.pre_run_id.endswith("-r002"))
            self.assertTrue(run.pre_quarantine.name.endswith("-r002"))
            assert_no_overwrite_targets(run)

    def test_preflight_rejects_any_bound_quarantine_raw_state_or_report_path(self) -> None:
        with TemporaryDirectory() as directory:
            for attribute in (
                "pre_quarantine",
                "post_quarantine",
                "pre_destination",
                "post_destination",
                "pre_state",
                "post_state",
                "aggregate_state",
                "tracked_report",
            ):
                run = PetesLakeOpticalRun.create(
                    repository_root=Path(directory) / attribute,
                    generated_at_utc="2026-07-21T16:30:00Z",
                    revision="r001",
                )
                target = getattr(run, attribute)
                if attribute.endswith("state") or attribute == "tracked_report":
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text("occupied", encoding="utf-8")
                else:
                    target.mkdir(parents=True, exist_ok=True)
                with self.assertRaisesRegex(AcquisitionError, "NO_OVERWRITE_TARGET_EXISTS"):
                    assert_no_overwrite_targets(run)

    def test_pre_transaction_is_verified_and_state_is_complete_before_post_request(self) -> None:
        with TemporaryDirectory() as directory:
            run = PetesLakeOpticalRun.create(
                repository_root=Path(directory),
                generated_at_utc="2026-07-21T16:30:00Z",
                revision="r001",
            )
            calls: list[str] = []

            def fake_stream(contract, quarantine, **kwargs):
                if contract == POST_CONTRACT:
                    self.assertTrue(run.pre_state.exists())
                calls.append(f"stream:{contract.role}")
                return {
                    "role": contract.role,
                    "status": "SYNTHETIC_TEST_DOUBLE",
                    "bytes": contract.expected_size_bytes,
                    "resumed_from_bytes": 0,
                    "safe_final_endpoint": "https://example.invalid/value",
                }

            def fake_promote(**kwargs):
                contract = kwargs["contract"]
                calls.append(f"promote:{contract.role}")
                return fake_registration(contract, kwargs["run_id"])

            def fake_verify(destination, contracts, **kwargs):
                contract = tuple(contracts)[0]
                calls.append(f"verify:{contract.role}")
                run_id = run.pre_run_id if contract == PRE_CONTRACT else run.post_run_id
                return {
                    "accepted_as_unchanged_registered_package": True,
                    "registration": fake_registration(contract, run_id),
                }

            def fake_metadata(contract, *, observed_at_utc):
                if contract == POST_CONTRACT:
                    self.assertTrue(run.pre_state.exists())
                calls.append(f"metadata:{contract.role}")
                return role_metadata_snapshot(contract, observed_at_utc=observed_at_utc)

            with patch(
                "burnlens.petes_lake_optical_contract.stream_cdse_asset_with_retries",
                side_effect=fake_stream,
            ), patch(
                "burnlens.petes_lake_optical_contract._promote_quarantine_no_replace",
                side_effect=fake_promote,
            ), patch(
                "burnlens.petes_lake_optical_contract.verify_registered_package",
                side_effect=fake_verify,
            ), patch(
                "burnlens.petes_lake_optical_contract._write_private_run_state",
                side_effect=local_private_state_writer,
            ):
                report = acquire_petes_lake_optical_pair(
                    credentials=CdseCredentials("synthetic-user", "synthetic-secret"),
                    run=run,
                    trace=synthetic_trace(),
                    metadata_refresh_fn=fake_metadata,
                    observed_at_fn=iter(
                        ("2026-07-21T16:30:01Z", "2026-07-21T16:30:02Z")
                    ).__next__,
                )

            self.assertEqual(calls, [
                f"metadata:{PRE_CONTRACT.role}",
                f"stream:{PRE_CONTRACT.role}",
                f"promote:{PRE_CONTRACT.role}",
                f"verify:{PRE_CONTRACT.role}",
                f"metadata:{POST_CONTRACT.role}",
                f"stream:{POST_CONTRACT.role}",
                f"promote:{POST_CONTRACT.role}",
                f"verify:{POST_CONTRACT.role}",
                f"verify:{PRE_CONTRACT.role}",
                f"verify:{POST_CONTRACT.role}",
            ])
            self.assertTrue(report["semantic_record"]["u03_authorized"])
            self.assertTrue(run.pre_state.exists())
            self.assertTrue(run.post_state.exists())
            self.assertTrue(run.aggregate_state.exists())
            self.assertTrue(run.tracked_report.exists())

    def test_pre_post_verification_failure_blocks_post_and_retains_failure_states(self) -> None:
        with TemporaryDirectory() as directory:
            run = PetesLakeOpticalRun.create(
                repository_root=Path(directory),
                generated_at_utc="2026-07-21T16:30:00Z",
                revision="r001",
            )
            streamed_roles: list[str] = []

            def fake_stream(contract, quarantine, **kwargs):
                streamed_roles.append(contract.role)
                return {"role": contract.role, "status": "SYNTHETIC_TEST_DOUBLE"}

            with patch(
                "burnlens.petes_lake_optical_contract.stream_cdse_asset_with_retries",
                side_effect=fake_stream,
            ), patch(
                "burnlens.petes_lake_optical_contract._promote_quarantine_no_replace",
                return_value=fake_registration(PRE_CONTRACT, run.pre_run_id),
            ), patch(
                "burnlens.petes_lake_optical_contract.verify_registered_package",
                return_value={"accepted_as_unchanged_registered_package": False},
            ), patch(
                "burnlens.petes_lake_optical_contract._write_private_run_state",
                side_effect=local_private_state_writer,
            ):
                with self.assertRaisesRegex(AcquisitionError, "POST_PROMOTION_VERIFICATION_FAILED"):
                    acquire_petes_lake_optical_pair(
                        credentials=CdseCredentials("synthetic-user", "synthetic-secret"),
                        run=run,
                        trace=synthetic_trace(),
                        metadata_refresh_fn=role_metadata_snapshot,
                        observed_at_fn=lambda: "2026-07-21T16:30:01Z",
                    )

            self.assertEqual(streamed_roles, [PRE_CONTRACT.role])
            pre_failure = json.loads(run.pre_state.read_text(encoding="utf-8"))
            aggregate_failure = json.loads(run.aggregate_state.read_text(encoding="utf-8"))
            self.assertFalse(pre_failure["u03_authorized"])
            self.assertFalse(aggregate_failure["u03_authorized"])
            self.assertFalse(run.post_state.exists())
            self.assertFalse(run.tracked_report.exists())

    def test_post_failure_preserves_pre_pass_and_blocks_aggregate_promotion(self) -> None:
        with TemporaryDirectory() as directory:
            run = PetesLakeOpticalRun.create(
                repository_root=Path(directory),
                generated_at_utc="2026-07-21T16:30:00Z",
                revision="r001",
            )

            def fake_stream(contract, quarantine, **kwargs):
                if contract == POST_CONTRACT:
                    raise AcquisitionError("DOWNLOAD_HTTP_STATUS_REJECTED", role=contract.role)
                return {"role": contract.role, "status": "SYNTHETIC_TEST_DOUBLE"}

            def fake_promote(**kwargs):
                return fake_registration(kwargs["contract"], kwargs["run_id"])

            def fake_verify(destination, contracts, **kwargs):
                contract = tuple(contracts)[0]
                run_id = run.pre_run_id if contract == PRE_CONTRACT else run.post_run_id
                return {
                    "accepted_as_unchanged_registered_package": True,
                    "registration": fake_registration(contract, run_id),
                }

            with patch(
                "burnlens.petes_lake_optical_contract.stream_cdse_asset_with_retries",
                side_effect=fake_stream,
            ), patch(
                "burnlens.petes_lake_optical_contract._promote_quarantine_no_replace",
                side_effect=fake_promote,
            ), patch(
                "burnlens.petes_lake_optical_contract.verify_registered_package",
                side_effect=fake_verify,
            ), patch(
                "burnlens.petes_lake_optical_contract._write_private_run_state",
                side_effect=local_private_state_writer,
            ):
                with self.assertRaisesRegex(AcquisitionError, "DOWNLOAD_HTTP_STATUS_REJECTED"):
                    acquire_petes_lake_optical_pair(
                        credentials=CdseCredentials("synthetic-user", "synthetic-secret"),
                        run=run,
                        trace=synthetic_trace(),
                        metadata_refresh_fn=role_metadata_snapshot,
                        observed_at_fn=iter(
                            ("2026-07-21T16:30:01Z", "2026-07-21T16:30:02Z")
                        ).__next__,
                    )

            self.assertEqual(
                json.loads(run.pre_state.read_text(encoding="utf-8"))["disposition"],
                "pass",
            )
            post_failure = json.loads(run.post_state.read_text(encoding="utf-8"))
            aggregate_failure = json.loads(run.aggregate_state.read_text(encoding="utf-8"))
            self.assertEqual(post_failure["disposition"], "remediate")
            self.assertIn("pre_transaction", aggregate_failure)
            self.assertFalse(aggregate_failure["u03_authorized"])
            self.assertNotIn("synthetic-secret", json.dumps(aggregate_failure))
            self.assertFalse(run.tracked_report.exists())

    def test_post_only_remediation_freshly_verifies_pre_and_never_reacquires_it(self) -> None:
        with TemporaryDirectory() as directory:
            run = PetesLakeOpticalRun.create(
                repository_root=Path(directory),
                generated_at_utc="2026-07-21T18:00:00Z",
                revision="r002",
                mode="post-only",
            )
            pre = synthetic_transaction(
                run,
                PRE_CONTRACT,
                run.pre_run_id,
                "2026-07-21T16:30:01Z",
            )
            provider_write_private_state(run.pre_state, pre)
            calls: list[str] = []

            def fake_stream(contract, quarantine, **kwargs):
                calls.append(f"stream:{contract.role}")
                return {"role": contract.role, "status": "SYNTHETIC_TEST_DOUBLE"}

            def fake_promote(**kwargs):
                return fake_registration(kwargs["contract"], kwargs["run_id"])

            def fake_verify(destination, contracts, **kwargs):
                contract = tuple(contracts)[0]
                calls.append(f"verify:{contract.role}")
                run_id = run.pre_run_id if contract == PRE_CONTRACT else run.post_run_id
                registration = fake_registration(contract, run_id)
                return {
                    "accepted_as_unchanged_registered_package": True,
                    "registration": registration,
                }

            with patch(
                "burnlens.petes_lake_optical_contract.stream_cdse_asset_with_retries",
                side_effect=fake_stream,
            ), patch(
                "burnlens.petes_lake_optical_contract._promote_quarantine_no_replace",
                side_effect=fake_promote,
            ), patch(
                "burnlens.petes_lake_optical_contract.verify_registered_package",
                side_effect=fake_verify,
            ), patch(
                "burnlens.petes_lake_optical_contract._write_private_run_state",
                side_effect=local_private_state_writer,
            ):
                report = resume_petes_lake_post_only(
                    credentials=CdseCredentials("synthetic-user", "synthetic-secret"),
                    run=run,
                    trace=synthetic_trace(),
                    metadata_refresh_fn=role_metadata_snapshot,
                    observed_at_fn=lambda: "2026-07-21T18:00:01Z",
                )

            self.assertNotIn(f"stream:{PRE_CONTRACT.role}", calls)
            self.assertEqual(calls[0], f"verify:{PRE_CONTRACT.role}")
            self.assertIn(f"stream:{POST_CONTRACT.role}", calls)
            self.assertEqual(
                report["semantic_record"]["transactions"][0]["run_id"],
                run.pre_run_id,
            )
            self.assertEqual(
                report["semantic_record"]["transactions"][1]["run_id"],
                run.post_run_id,
            )

    def test_aggregate_only_remediation_uses_two_registered_packages_without_credentials(self) -> None:
        with TemporaryDirectory() as directory:
            run = PetesLakeOpticalRun.create(
                repository_root=Path(directory),
                generated_at_utc="2026-07-21T18:30:00Z",
                revision="r002",
                mode="aggregate-only",
            )
            post_r001 = "BL-2026-07-21-petes-lake-optical-post-r001"
            verified_roles: list[str] = []

            def fake_verify(destination, contracts, **kwargs):
                contract = tuple(contracts)[0]
                verified_roles.append(contract.role)
                run_id = run.pre_run_id if contract == PRE_CONTRACT else post_r001
                registration = fake_registration(contract, run_id)
                return {
                    "accepted_as_unchanged_registered_package": True,
                    "registration": registration,
                }

            with patch(
                "burnlens.petes_lake_optical_contract.verify_registered_package",
                side_effect=fake_verify,
            ), patch(
                "burnlens.petes_lake_optical_contract._write_private_run_state",
                side_effect=local_private_state_writer,
            ):
                report = finalize_petes_lake_aggregate_only(
                    run=run,
                    trace=synthetic_trace(),
                    metadata_refresh_fn=role_metadata_snapshot,
                    observed_at_fn=iter(
                        ("2026-07-21T18:30:01Z", "2026-07-21T18:30:02Z")
                    ).__next__,
                )

            self.assertEqual(
                report["semantic_record"]["decision"],
                "PASS_PETES_LAKE_OPTICAL_CUSTODY_AUTHORIZE_U03_ONLY",
            )
            self.assertGreaterEqual(verified_roles.count(PRE_CONTRACT.role), 2)
            self.assertGreaterEqual(verified_roles.count(POST_CONTRACT.role), 2)
            self.assertEqual(
                report["semantic_record"]["transactions"][0]["download"]["status"],
                "RECONSTRUCTED_FROM_IMMUTABLE_REGISTRATION",
            )
            self.assertTrue(run.aggregate_state.exists())
            self.assertTrue(run.tracked_report.exists())

    def test_prepublication_verification_failure_never_writes_pass_report(self) -> None:
        with TemporaryDirectory() as directory:
            run = PetesLakeOpticalRun.create(
                repository_root=Path(directory),
                generated_at_utc="2026-07-21T19:00:00Z",
                revision="r001",
            )
            pre = synthetic_transaction(
                run, PRE_CONTRACT, run.pre_run_id, "2026-07-21T19:00:01Z"
            )
            post = synthetic_transaction(
                run, POST_CONTRACT, run.post_run_id, "2026-07-21T19:00:02Z"
            )
            with patch(
                "burnlens.petes_lake_optical_contract.verify_registered_package",
                return_value={"accepted_as_unchanged_registered_package": False},
            ), patch(
                "burnlens.petes_lake_optical_contract._write_private_run_state",
                side_effect=local_private_state_writer,
            ):
                with self.assertRaisesRegex(
                    AcquisitionError, "REMEDIATION_REGISTERED_PACKAGE_INVALID"
                ):
                    _write_success_outputs(run, synthetic_trace(), pre, post)
            self.assertFalse(run.tracked_report.exists())
            self.assertEqual(
                json.loads(run.aggregate_state.read_text(encoding="utf-8"))["disposition"],
                "remediate",
            )

    def test_trace_tampering_is_not_accepted_as_remediation_evidence(self) -> None:
        with TemporaryDirectory() as directory:
            run = PetesLakeOpticalRun.create(
                repository_root=Path(directory),
                generated_at_utc="2026-07-21T19:00:00Z",
                revision="r002",
                mode="post-only",
            )
            transaction = synthetic_transaction(
                run, PRE_CONTRACT, run.pre_run_id, "2026-07-21T19:00:01Z"
            )
            transaction["trace"]["branch"] = "tampered"
            registration = fake_registration(PRE_CONTRACT, run.pre_run_id)
            verification = {
                "accepted_as_unchanged_registered_package": True,
                "registration": registration,
            }
            self.assertFalse(
                _transaction_matches_fresh_verification(
                    transaction, PRE_CONTRACT, verification
                )
            )

    def test_u03_validation_rejects_partial_or_tampered_pair(self) -> None:
        with TemporaryDirectory() as directory:
            run = PetesLakeOpticalRun.create(
                repository_root=Path(directory),
                generated_at_utc="2026-07-21T16:30:00Z",
                revision="r001",
            )
            run.tracked_report.parent.mkdir(parents=True, exist_ok=True)
            run.tracked_report.write_text("{}\n", encoding="utf-8")
            self.assertIn(
                "U03_PRIVATE_AGGREGATE_STATE_REQUIRED",
                validate_u03_prerequisite(run),
            )

    def test_cli_preflight_completes_before_credentials_are_loaded(self) -> None:
        with TemporaryDirectory() as directory:
            args = SimpleNamespace(
                repository_root=Path(directory),
                generated_at_utc="2026-07-21T19:00:00Z",
                revision="r001",
                mode="full",
            )
            events: list[str] = []
            with patch.object(acquire_cli, "parse_args", return_value=args), patch.object(
                acquire_cli,
                "verify_petes_lake_repository_preflight",
                side_effect=lambda run, **kwargs: events.append("preflight") or synthetic_trace(),
            ), patch.object(
                acquire_cli.CdseCredentials,
                "from_environment",
                side_effect=lambda: events.append("credentials")
                or CdseCredentials("synthetic-user", "synthetic-secret"),
            ), patch.object(
                acquire_cli,
                "acquire_petes_lake_optical_pair",
                side_effect=lambda **kwargs: events.append("acquire")
                or {"decision": "SYNTHETIC_PASS"},
            ):
                self.assertEqual(acquire_cli.main(), 0)
            self.assertEqual(events, ["preflight", "credentials", "acquire"])

    def test_cli_preflight_and_verify_only_are_credential_free(self) -> None:
        with TemporaryDirectory() as directory:
            base = {
                "repository_root": Path(directory),
                "generated_at_utc": "2026-07-21T19:00:00Z",
                "revision": "r001",
                "mode": "full",
            }
            for flag in ("preflight_only", "verify_only"):
                args = SimpleNamespace(
                    **base,
                    preflight_only=flag == "preflight_only",
                    verify_only=flag == "verify_only",
                )
                with patch.object(acquire_cli, "parse_args", return_value=args), patch.object(
                    acquire_cli,
                    "verify_petes_lake_repository_preflight",
                    return_value=synthetic_trace(),
                ), patch.object(
                    acquire_cli.CdseCredentials,
                    "from_environment",
                    side_effect=AssertionError("credentials must not be loaded"),
                ), patch.object(
                    acquire_cli,
                    "validate_u03_prerequisite",
                    return_value=[],
                ):
                    self.assertEqual(acquire_cli.main(), 0)

    def test_cli_aggregate_only_remediation_never_loads_credentials(self) -> None:
        with TemporaryDirectory() as directory:
            args = SimpleNamespace(
                repository_root=Path(directory),
                generated_at_utc="2026-07-21T19:00:00Z",
                revision="r002",
                mode="aggregate-only",
            )
            with patch.object(acquire_cli, "parse_args", return_value=args), patch.object(
                acquire_cli,
                "verify_petes_lake_repository_preflight",
                return_value=synthetic_trace(),
            ), patch.object(
                acquire_cli.CdseCredentials,
                "from_environment",
                side_effect=AssertionError("credentials must not be loaded"),
            ), patch.object(
                acquire_cli,
                "finalize_petes_lake_aggregate_only",
                return_value={"decision": "SYNTHETIC_AGGREGATE_PASS"},
            ):
                self.assertEqual(acquire_cli.main(), 0)

    def test_production_wrapper_hard_binds_r001_and_clears_credentials(self) -> None:
        repository_root = Path(__file__).resolve().parents[1]
        wrapper = repository_root / "scripts" / "invoke_petes_lake_optical_intake.ps1"
        source = wrapper.read_text(encoding="utf-8")

        self.assertIn("[string]$GeneratedAtUtc", source)
        self.assertNotIn("[string]$RunId", source)
        self.assertNotIn("[string]$Revision", source)
        self.assertNotIn("[string]$Mode", source)
        self.assertGreaterEqual(source.count("--revision r001"), 3)
        self.assertGreaterEqual(source.count("--mode full"), 3)
        self.assertLess(source.index("--preflight-only"), source.index("Import-Clixml"))
        self.assertLess(source.index("Import-Clixml"), source.index("BURNLENS_CDSE_USERNAME ="))
        self.assertGreaterEqual(
            source.count("Remove-Item Env:BURNLENS_CDSE_USERNAME"), 2
        )
        self.assertGreaterEqual(
            source.count("Remove-Item Env:BURNLENS_CDSE_PASSWORD"), 2
        )
        self.assertNotIn("BURNLENS_EARTHDATA", source)
        self.assertNotIn("--password", source.lower())
        self.assertIn("--verify-only", source)


if __name__ == "__main__":
    unittest.main()
