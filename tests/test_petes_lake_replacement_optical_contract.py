from __future__ import annotations

import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from burnlens import acquire_petes_lake_replacement_post as replacement_cli
from burnlens import petes_lake_replacement_optical_contract as replacement
from burnlens.petes_lake_optical_contract import POST_CONTRACT, PRE_CONTRACT
from burnlens.petes_lake_replacement_optical_contract import (
    ATTRIBUTION,
    BOUND_TRACKED_FILES,
    BRANCH,
    CONTRACT_VERSION,
    EXPECTED_METADATA,
    PACKAGE_ID,
    REPLACEMENT_POST_CONTRACT,
    REPORT_ID,
    TERMS_PATH,
    CdseCredentials,
    ReplacementOpticalRun,
    ReplacementPreflight,
    ReplacementTrace,
    acquire_replacement_post,
    finalize_replacement_custody,
    refresh_replacement_metadata,
    refresh_replacement_terms,
    validate_replacement_contracts,
    validate_replacement_metadata,
    verify_replacement_custody,
    verify_replacement_repository_preflight,
)
from burnlens.provider_acquisition import AcquisitionError


class FakeResponse:
    def __init__(self, payload: bytes, status: int = 200) -> None:
        self._stream = io.BytesIO(payload)
        self.status = status

    def read(self, size: int = -1) -> bytes:
        return self._stream.read(size)

    def getcode(self) -> int:
        return self.status

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        return None


def metadata_payload() -> dict:
    return {
        "Id": REPLACEMENT_POST_CONTRACT.provider_id,
        "Name": REPLACEMENT_POST_CONTRACT.native_id,
        "ContentLength": REPLACEMENT_POST_CONTRACT.expected_size_bytes,
        "Online": True,
        "ContentDate": {"Start": EXPECTED_METADATA["acquisition_utc"]},
        "PublicationDate": EXPECTED_METADATA["publication_utc"],
        "S3Path": f"/not-retained/{REPLACEMENT_POST_CONTRACT.native_id}",
        "Checksum": [
            {"Algorithm": "MD5", "Value": REPLACEMENT_POST_CONTRACT.provider_md5},
            {"Algorithm": "BLAKE3", "Value": REPLACEMENT_POST_CONTRACT.provider_blake3},
        ],
        "Attributes": [
            {"Name": "platformSerialIdentifier", "Value": "A"},
            {"Name": "tileId", "Value": "10TEP"},
            {"Name": "relativeOrbitNumber", "Value": 13},
            {"Name": "processorVersion", "Value": "05.10"},
            {"Name": "productType", "Value": "S2MSI2A"},
            {"Name": "cloudCover", "Value": 0.098782},
        ],
    }


def exact_metadata(observed_at_utc: str = "2026-07-21T21:00:01Z") -> dict:
    payload = json.dumps(metadata_payload()).encode("utf-8")
    return refresh_replacement_metadata(
        observed_at_utc=observed_at_utc,
        urlopen_fn=lambda request, timeout: FakeResponse(payload),
    )


def synthetic_terms(observed_at_utc: str = "2026-07-21T21:00:00Z") -> dict:
    return {
        "terms_review_id": "TERMS-2026-026",
        "observed_at_utc": observed_at_utc,
        "live_refresh_performed": True,
        "sources": [
            {
                "title": "synthetic terms",
                "url": "https://example.invalid/terms",
                "bytes": 5,
                "sha256": "a" * 64,
                "disposition": "exact-current-source-bytes-pass",
            }
        ],
        "decision": (
            "RESOLVED_FOR_ONE_EXACT_REPLACEMENT_SENTINEL_ARCHIVE, "
            "LOCAL_ANALYSIS, AND BOUNDED_DERIVED_EVIDENCE"
        ),
        "exact_authorized_provider_id": REPLACEMENT_POST_CONTRACT.provider_id,
        "native_provider_bytes_redistribution": False,
        "attribution": ATTRIBUTION,
    }


def synthetic_trace(commit: str = "a" * 40) -> ReplacementTrace:
    bindings = tuple(
        {
            "path": path.as_posix(),
            "bytes": details[0],
            "sha256": details[1],
            "role": details[2],
        }
        for path, details in BOUND_TRACKED_FILES.items()
    )
    return ReplacementTrace(
        git_source_commit=commit,
        remote_branch_commit=commit,
        branch=BRANCH,
        bound_tracked_files=bindings,
    )


def original_pre_verification() -> dict:
    return {
        "package_id": PRE_CONTRACT.package_id,
        "role": PRE_CONTRACT.role,
        "destination_path": "downloads/phase-two/raw/petes-lake-s2-optical-pre-v0.1.0",
        "registration_run_id": "BL-2026-07-21-petes-lake-optical-pre-r001",
        "registration_manifest_sha256": "b" * 64,
        "registration_manifest_link_count": 1,
        "asset": {
            "role": PRE_CONTRACT.role,
            "sha256": replacement.ORIGINAL_PRE_LOCAL_SHA256,
            "md5": PRE_CONTRACT.provider_md5,
            "blake3": PRE_CONTRACT.provider_blake3,
        },
        "fresh_verification_decision": "pass",
        "provider_archive_request_performed": False,
    }


def synthetic_preflight(commit: str = "a" * 40) -> ReplacementPreflight:
    return ReplacementPreflight(
        trace=synthetic_trace(commit),
        metadata_snapshot=exact_metadata(),
        terms_snapshot=synthetic_terms(),
        original_pre_verification=original_pre_verification(),
    )


def fake_registration(run_id: str) -> dict:
    return {
        "registration_schema_version": "0.2.0",
        "contract_version": CONTRACT_VERSION,
        "contract_sha256": "c" * 64,
        "package_id": PACKAGE_ID,
        "generated_at_utc": "2026-07-21T21:00:02Z",
        "run_id": run_id,
        "synthetic_fixture": False,
        "asset_count": 1,
        "assets": [
            {
                "role": REPLACEMENT_POST_CONTRACT.role,
                "source_record_id": REPLACEMENT_POST_CONTRACT.source_record_id,
                "native_id": REPLACEMENT_POST_CONTRACT.native_id,
                "filename": REPLACEMENT_POST_CONTRACT.expected_filename,
                "bytes": REPLACEMENT_POST_CONTRACT.expected_size_bytes,
                "sha256": "d" * 64,
                "md5": REPLACEMENT_POST_CONTRACT.provider_md5,
                "blake3": REPLACEMENT_POST_CONTRACT.provider_blake3,
            }
        ],
    }


def fake_verification(run_id: str) -> dict:
    registration = fake_registration(run_id)
    return {
        "registration_manifest_name": ".burnlens-registration.json",
        "registration_manifest_link_count": 1,
        "registration_manifest_sha256": "e" * 64,
        "registration": registration,
        "accepted_as_unchanged_registered_package": True,
        "reason_codes": ["REGISTERED_PACKAGE_VERIFIED"],
    }


def local_private_writer(run, path: Path, payload: dict) -> None:
    replacement.write_private_state(path, payload)


class PetesLakeReplacementContractTests(unittest.TestCase):
    def test_exact_contract_is_one_selected_october_19_archive(self) -> None:
        self.assertEqual(validate_replacement_contracts((REPLACEMENT_POST_CONTRACT,)), [])
        self.assertEqual(CONTRACT_VERSION, "petes-lake-optical-post-remediation-contract-v0.1.0")
        self.assertEqual(REPLACEMENT_POST_CONTRACT.provider_id, "31fa8699-175b-4fd7-91c3-dd727a1576f5")
        self.assertEqual(REPLACEMENT_POST_CONTRACT.expected_size_bytes, 1_195_226_823)
        self.assertEqual(REPLACEMENT_POST_CONTRACT.package_id, PACKAGE_ID)
        self.assertNotEqual(REPLACEMENT_POST_CONTRACT, POST_CONTRACT)
        self.assertEqual(BOUND_TRACKED_FILES[TERMS_PATH][1], "abcfc1ac94b5f886131f46049c9e98ae503ea7e1b6a12bc87c8d6e26073888d9")

    def test_metadata_preserves_exact_values_but_not_s3_or_download_route(self) -> None:
        snapshot = exact_metadata()
        self.assertEqual(validate_replacement_metadata(snapshot), [])
        self.assertEqual(snapshot["odata_cloud_cover_percent"], 0.098782)
        self.assertEqual(snapshot["stac_snow_cover_percent"], 0.564076)
        serialized = json.dumps(snapshot)
        self.assertNotIn("/not-retained/", serialized)
        self.assertNotIn("stable_route", serialized)

    def test_metadata_identity_or_cloud_drift_fails_closed(self) -> None:
        snapshot = exact_metadata()
        snapshot["provider_id"] = "wrong"
        snapshot["odata_cloud_cover_percent"] = 0.1
        reasons = validate_replacement_metadata(snapshot)
        self.assertIn("REPLACEMENT_METADATA_PROVIDER_ID_MISMATCH", reasons)
        self.assertIn("REPLACEMENT_METADATA_ODATA_CLOUD_COVER_PERCENT_MISMATCH", reasons)

    def test_terms_refresh_requires_exact_source_bytes_and_hash(self) -> None:
        payloads = (b"first", b"second")
        sources = tuple(
            {
                "title": f"source-{index}",
                "url": f"https://example.invalid/{index}",
                "bytes": len(payload),
                "sha256": replacement.sha256(payload).hexdigest(),
            }
            for index, payload in enumerate(payloads)
        )

        def fake_open(request, timeout):
            index = int(request.full_url.rsplit("/", 1)[1])
            return FakeResponse(payloads[index])

        with patch.object(replacement, "TERMS_SOURCES", sources):
            snapshot = refresh_replacement_terms(
                observed_at_utc="2026-07-21T21:00:00Z",
                urlopen_fn=fake_open,
            )
            self.assertEqual(len(snapshot["sources"]), 2)
            self.assertFalse(snapshot["native_provider_bytes_redistribution"])

            changed = list(sources)
            changed[0] = dict(changed[0], sha256="0" * 64)
            with patch.object(replacement, "TERMS_SOURCES", tuple(changed)):
                with self.assertRaisesRegex(AcquisitionError, "TERMS_SOURCE_DRIFT"):
                    refresh_replacement_terms(
                        observed_at_utc="2026-07-21T21:00:00Z",
                        urlopen_fn=fake_open,
                    )

    def test_run_ids_paths_and_modes_are_revisioned_without_touching_original_post(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            run = ReplacementOpticalRun.create(
                repository_root=root,
                generated_at_utc="2026-07-21T21:00:00Z",
                revision="r001",
                mode="acquire",
            )
            self.assertEqual(run.transaction_run_id, "BL-2026-07-21-petes-lake-optical-post-remediation-r001")
            self.assertEqual(run.aggregate_run_id, "BL-2026-07-21-petes-lake-optical-remediation-intake-r001")
            self.assertEqual(run.replacement_destination.name, PACKAGE_ID)
            self.assertEqual(run.tracked_report.name, f"{REPORT_ID}.json")
            self.assertNotEqual(run.replacement_destination.name, POST_CONTRACT.package_id)
            with self.assertRaisesRegex(ValueError, "hard-bound to r001"):
                ReplacementOpticalRun.create(
                    repository_root=root,
                    generated_at_utc="2026-07-21T21:00:00Z",
                    revision="r002",
                    mode="acquire",
                )
            ReplacementOpticalRun.create(
                repository_root=root,
                generated_at_utc="2026-07-21T21:00:00Z",
                revision="r002",
                mode="finalize",
            )

    def test_preflight_requires_remote_equality_before_live_gates(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            run = ReplacementOpticalRun.create(
                repository_root=root,
                generated_at_utc="2026-07-21T21:00:00Z",
                revision="r001",
                mode="acquire",
            )
            head = "a" * 40

            def fake_git(repository_root, *arguments):
                args = tuple(arguments)
                if args == ("rev-parse", "--show-toplevel"):
                    return SimpleNamespace(returncode=0, stdout=str(root) + "\n")
                if args == ("branch", "--show-current"):
                    return SimpleNamespace(returncode=0, stdout=BRANCH + "\n")
                if args == ("config", "--get", "remote.origin.url"):
                    return SimpleNamespace(returncode=0, stdout="https://github.com/drwbkr1/burnlens-deschutes.git\n")
                if args == ("rev-parse", "HEAD"):
                    return SimpleNamespace(returncode=0, stdout=head + "\n")
                if args[:2] == ("status", "--porcelain=v1"):
                    return SimpleNamespace(returncode=0, stdout="")
                if "ls-remote" in args:
                    return SimpleNamespace(
                        returncode=0,
                        stdout=f"{'b' * 40}\trefs/heads/{BRANCH}\n",
                    )
                return SimpleNamespace(returncode=0, stdout="")

            with patch.object(replacement, "_git", side_effect=fake_git):
                with self.assertRaisesRegex(AcquisitionError, "REMOTE_HEAD_MISMATCH"):
                    verify_replacement_repository_preflight(
                        run,
                        metadata_refresh_fn=lambda **kwargs: exact_metadata(),
                        terms_refresh_fn=lambda **kwargs: synthetic_terms(),
                    )

    def test_acquisition_requests_only_replacement_and_writes_bound_report(self) -> None:
        with TemporaryDirectory() as directory:
            run = ReplacementOpticalRun.create(
                repository_root=Path(directory),
                generated_at_utc="2026-07-21T21:00:02Z",
                revision="r001",
                mode="acquire",
            )
            preflight = synthetic_preflight()
            calls: list[str] = []
            verification = fake_verification(run.transaction_run_id)

            def fake_stream(contract, quarantine, **kwargs):
                calls.append(f"stream:{contract.role}")
                return {
                    "role": contract.role,
                    "status": "SYNTHETIC_TEST_DOUBLE",
                    "bytes": contract.expected_size_bytes,
                    "provider_archive_request_performed": True,
                }

            with patch.object(replacement, "stream_cdse_asset_with_retries", side_effect=fake_stream), patch.object(
                replacement,
                "promote_quarantine_no_overwrite",
                return_value=verification["registration"],
            ), patch.object(
                replacement,
                "_fresh_verify_replacement",
                return_value=verification,
            ), patch.object(
                replacement,
                "_validate_original_pre",
                return_value=preflight.original_pre_verification,
            ), patch.object(
                replacement,
                "_write_private",
                side_effect=local_private_writer,
            ):
                report = acquire_replacement_post(
                    credentials=CdseCredentials("synthetic-user", "synthetic-secret"),
                    run=run,
                    preflight=preflight,
                )

            self.assertEqual(calls, [f"stream:{REPLACEMENT_POST_CONTRACT.role}"])
            self.assertTrue(run.transaction_state.exists())
            self.assertTrue(run.aggregate_state.exists())
            self.assertTrue(run.tracked_report.exists())
            self.assertEqual(
                report["semantic_record"]["decision"],
                "PASS_PETES_LAKE_REPLACEMENT_OPTICAL_CUSTODY_AUTHORIZE_U03_SOURCE_FITNESS_R002_ONLY",
            )
            serialized = run.aggregate_state.read_text(encoding="utf-8")
            self.assertNotIn("synthetic-secret", serialized)
            self.assertFalse(report["semantic_record"]["u04_authorized"])

    def test_provider_failure_is_retained_and_never_writes_pass_report(self) -> None:
        with TemporaryDirectory() as directory:
            run = ReplacementOpticalRun.create(
                repository_root=Path(directory),
                generated_at_utc="2026-07-21T21:00:02Z",
                revision="r001",
                mode="acquire",
            )
            preflight = synthetic_preflight()
            with patch.object(
                replacement,
                "stream_cdse_asset_with_retries",
                side_effect=AcquisitionError("DOWNLOAD_HTTP_STATUS_REJECTED", detail="503"),
            ), patch.object(
                replacement,
                "_write_private",
                side_effect=local_private_writer,
            ):
                with self.assertRaisesRegex(AcquisitionError, "DOWNLOAD_HTTP_STATUS_REJECTED"):
                    acquire_replacement_post(
                        credentials=CdseCredentials("synthetic-user", "synthetic-secret"),
                        run=run,
                        preflight=preflight,
                    )
            self.assertTrue(run.transaction_state.exists())
            self.assertTrue(run.aggregate_state.exists())
            self.assertFalse(run.tracked_report.exists())
            failure = json.loads(run.transaction_state.read_text(encoding="utf-8"))
            self.assertEqual(failure["disposition"], "remediate")
            self.assertFalse(failure["replacement_u03_source_fitness_authorized"])

    def test_finalize_reconstructs_without_provider_or_credentials(self) -> None:
        with TemporaryDirectory() as directory:
            run = ReplacementOpticalRun.create(
                repository_root=Path(directory),
                generated_at_utc="2026-07-21T21:30:00Z",
                revision="r002",
                mode="finalize",
            )
            run.replacement_destination.mkdir(parents=True)
            verification = fake_verification(
                "BL-2026-07-21-petes-lake-optical-post-remediation-r001"
            )
            preflight = synthetic_preflight()
            with patch.object(
                replacement,
                "_fresh_verify_replacement",
                return_value=verification,
            ), patch.object(
                replacement,
                "_validate_original_pre",
                return_value=preflight.original_pre_verification,
            ), patch.object(
                replacement,
                "stream_cdse_asset_with_retries",
                side_effect=AssertionError("provider must not be called"),
            ), patch.object(
                replacement,
                "_write_private",
                side_effect=local_private_writer,
            ):
                report = finalize_replacement_custody(run=run, preflight=preflight)
            transaction = report["semantic_record"]["replacement_transaction"]
            self.assertEqual(
                transaction["download"]["status"],
                "RECONSTRUCTED_FROM_IMMUTABLE_REGISTRATION",
            )
            self.assertFalse(transaction["credentials_exercised"])
            self.assertTrue(run.tracked_report.exists())

    def test_verify_only_tolerates_new_observation_times_but_rejects_tampering(self) -> None:
        with TemporaryDirectory() as directory:
            run = ReplacementOpticalRun.create(
                repository_root=Path(directory),
                generated_at_utc="2026-07-21T21:00:02Z",
                revision="r001",
                mode="acquire",
            )
            preflight = synthetic_preflight()
            verification = fake_verification(run.transaction_run_id)
            transaction = replacement._transaction_state(
                run,
                preflight,
                download={"status": "SYNTHETIC_TEST_DOUBLE"},
                registration=verification["registration"],
                verification=verification,
                credentials_exercised=True,
            )
            with patch.object(replacement, "_fresh_verify_replacement", return_value=verification), patch.object(
                replacement,
                "_validate_original_pre",
                return_value=preflight.original_pre_verification,
            ), patch.object(
                replacement,
                "_write_private",
                side_effect=local_private_writer,
            ):
                replacement._write_success_outputs(run, preflight, transaction)

            refreshed = ReplacementPreflight(
                trace=preflight.trace,
                metadata_snapshot=dict(preflight.metadata_snapshot, observed_at_utc="2026-07-21T22:00:01Z"),
                terms_snapshot=dict(preflight.terms_snapshot, observed_at_utc="2026-07-21T22:00:00Z"),
                original_pre_verification=preflight.original_pre_verification,
            )
            with patch.object(replacement, "_fresh_verify_replacement", return_value=verification), patch.object(
                replacement,
                "_validate_trace",
                return_value=[],
            ):
                self.assertEqual(verify_replacement_custody(run=run, preflight=refreshed), [])
                report = json.loads(run.tracked_report.read_text(encoding="utf-8"))
                report["semantic_record"]["u04_authorized"] = True
                run.tracked_report.write_text(json.dumps(report) + "\n", encoding="utf-8")
                reasons = verify_replacement_custody(run=run, preflight=refreshed)
                self.assertTrue(reasons)

    def test_cli_preflight_precedes_credentials_and_flags_are_credential_free(self) -> None:
        with TemporaryDirectory() as directory:
            base = {
                "repository_root": Path(directory),
                "generated_at_utc": "2026-07-21T21:00:00Z",
                "revision": "r001",
                "mode": "acquire",
            }
            events: list[str] = []
            with patch.object(
                replacement_cli,
                "parse_args",
                return_value=SimpleNamespace(**base, preflight_only=False, verify_only=False),
            ), patch.object(
                replacement_cli,
                "verify_replacement_repository_preflight",
                side_effect=lambda *args, **kwargs: events.append("preflight") or synthetic_preflight(),
            ), patch.object(
                replacement_cli.CdseCredentials,
                "from_environment",
                side_effect=lambda: events.append("credentials") or CdseCredentials("user", "secret"),
            ), patch.object(
                replacement_cli,
                "acquire_replacement_post",
                side_effect=lambda **kwargs: events.append("acquire") or {
                    "semantic_record": {"decision": "SYNTHETIC_PASS"}
                },
            ):
                self.assertEqual(replacement_cli.main(), 0)
            self.assertEqual(events, ["preflight", "credentials", "acquire"])

            for flag in ("preflight_only", "verify_only"):
                args = SimpleNamespace(
                    **base,
                    preflight_only=flag == "preflight_only",
                    verify_only=flag == "verify_only",
                )
                with patch.object(replacement_cli, "parse_args", return_value=args), patch.object(
                    replacement_cli,
                    "verify_replacement_repository_preflight",
                    return_value=synthetic_preflight(),
                ), patch.object(
                    replacement_cli.CdseCredentials,
                    "from_environment",
                    side_effect=AssertionError("credentials must not load"),
                ), patch.object(
                    replacement_cli,
                    "verify_replacement_custody",
                    return_value=[],
                ):
                    self.assertEqual(replacement_cli.main(), 0)

    def test_wrapper_hard_binds_r001_and_clears_credentials(self) -> None:
        repository_root = Path(__file__).resolve().parents[1]
        source = (
            repository_root / "scripts" / "invoke_petes_lake_replacement_post_intake.ps1"
        ).read_text(encoding="utf-8")
        self.assertGreaterEqual(source.count("--revision r001"), 3)
        self.assertGreaterEqual(source.count("--mode acquire"), 3)
        self.assertLess(source.index("--preflight-only"), source.index("Import-Clixml"))
        self.assertGreaterEqual(source.count("Remove-Item Env:BURNLENS_CDSE_USERNAME"), 2)
        self.assertGreaterEqual(source.count("Remove-Item Env:BURNLENS_CDSE_PASSWORD"), 2)
        self.assertNotIn("--password", source.lower())
        self.assertIn("--verify-only", source)


if __name__ == "__main__":
    unittest.main()
