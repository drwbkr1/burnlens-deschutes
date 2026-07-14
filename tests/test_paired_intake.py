from __future__ import annotations

from dataclasses import replace
import json
import os
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
import zipfile

from PIL import Image

from burnlens.paired_intake import (
    CONTRACT_VERSION,
    EXACT_CONTRACTS,
    PACKAGE_ID,
    PUBLIC_METADATA_OBSERVED_AT_UTC,
    REPORT_ID,
    TRANSACTION_INVARIANTS,
    AssetContract,
    _stream_hashes,
    _synthetic_contracts,
    build_report,
    contract_digest,
    evaluate_quarantine,
    inspect_asset,
    promote_quarantine,
    render_html,
    run_synthetic_rehearsal,
    validate_asset_contracts,
    verify_registered_package,
    write_report,
)


GENERATED = "2026-07-14T02:30:00Z"
RUN_ID = "BL-TEST-PAIR-INTAKE"
SOURCE_COMMIT = "a" * 40


class PairedIntakeTests(unittest.TestCase):
    def _copy_all(self, source: Path, destination: Path, contracts: tuple[AssetContract, ...]) -> None:
        destination.mkdir()
        for contract in contracts:
            shutil.copy2(source / contract.expected_filename, destination / contract.expected_filename)

    def test_exact_contract_freezes_three_current_provider_assets(self) -> None:
        self.assertEqual(len(EXACT_CONTRACTS), 3)
        self.assertEqual({item.package_id for item in EXACT_CONTRACTS}, {PACKAGE_ID})
        self.assertEqual(EXACT_CONTRACTS[0].provider_id, "58cebcf0-c417-4384-a93a-2d6b15344117")
        self.assertEqual(EXACT_CONTRACTS[0].expected_size_bytes, 1_127_031_562)
        self.assertEqual(EXACT_CONTRACTS[0].provider_md5, "3806a834a97ab2eb41f1edf5496b433c")
        self.assertEqual(EXACT_CONTRACTS[1].provider_id, "G3944882727-LPCLOUD")
        self.assertEqual(EXACT_CONTRACTS[1].expected_size_bytes, 2_710_616)
        self.assertEqual(EXACT_CONTRACTS[2].provider_id, "G4037038741-LPCLOUD")
        self.assertEqual(EXACT_CONTRACTS[2].expected_size_bytes, 40_255_764)
        self.assertEqual(
            {item.native_pair_token for item in EXACT_CONTRACTS if item.native_pair_token},
            {"A2024179.1936"},
        )
        self.assertEqual(len(contract_digest()), 64)

    def test_contract_digest_covers_transaction_invariants(self) -> None:
        changed = (*TRANSACTION_INVARIANTS, "A future invariant must change the digest.")
        self.assertNotEqual(contract_digest(), contract_digest(transaction_invariants=changed))

    def test_generic_exact_asset_package_reuses_atomic_registration(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            seed = root / "seed"
            seed.mkdir()
            contracts = _synthetic_contracts(seed)[1:]
            quarantine = root / "quarantine"
            self._copy_all(seed, quarantine, contracts)
            destination = root / "raw" / contracts[0].package_id

            evaluation = evaluate_quarantine(
                quarantine,
                contracts,
                contract_validator=validate_asset_contracts,
            )
            self.assertTrue(evaluation["accepted_for_atomic_promotion"])
            promote_quarantine(
                quarantine,
                destination,
                contracts,
                generated_at_utc=GENERATED,
                run_id=RUN_ID,
                synthetic_fixture=True,
                contract_validator=validate_asset_contracts,
                contract_version="generic-exact-package-v0.1.0",
            )
            verification = verify_registered_package(
                destination,
                contracts,
                contract_validator=validate_asset_contracts,
                contract_version="generic-exact-package-v0.1.0",
            )

        self.assertTrue(verification["accepted_as_unchanged_registered_package"])

    def test_missing_provider_quarantine_fails_closed(self) -> None:
        with TemporaryDirectory() as directory:
            evaluation = evaluate_quarantine(Path(directory) / "missing", EXACT_CONTRACTS)

        self.assertFalse(evaluation["accepted_for_atomic_promotion"])
        self.assertEqual(evaluation["accepted_asset_count"], 0)
        self.assertIn("QUARANTINE_MISSING", evaluation["reason_codes"])
        self.assertTrue(all(item["reason_codes"] == ["ASSET_MISSING"] for item in evaluation["observations"]))

    def test_viirs_pair_token_must_be_present_in_both_native_ids(self) -> None:
        broken = tuple(
            replace(item, native_id="VJ214IMG.WRONG") if item.role == "viirs-active-fire" else item
            for item in EXACT_CONTRACTS
        )
        with TemporaryDirectory() as directory:
            evaluation = evaluate_quarantine(Path(directory) / "missing", broken)

        self.assertIn("VIIRS_NATIVE_ID_TOKEN_MISMATCH", evaluation["reason_codes"])

    def test_valid_synthetic_assets_pass_exact_size_container_and_checksum(self) -> None:
        with TemporaryDirectory() as directory:
            quarantine = Path(directory)
            contracts = _synthetic_contracts(quarantine)
            evaluation = evaluate_quarantine(quarantine, contracts)

        self.assertTrue(evaluation["accepted_for_atomic_promotion"])
        self.assertEqual(evaluation["accepted_asset_count"], 3)
        self.assertTrue(all(item["local_hashes"]["sha256"] for item in evaluation["observations"]))
        sentinel = evaluation["observations"][0]
        self.assertTrue(sentinel["container_details"]["manifest_present"])
        self.assertTrue(sentinel["container_details"]["crc_test_passed"])

    def test_checksum_tamper_fails_even_when_size_and_signature_match(self) -> None:
        with TemporaryDirectory() as directory:
            quarantine = Path(directory)
            contracts = _synthetic_contracts(quarantine)
            fire = quarantine / contracts[1].expected_filename
            payload = bytearray(fire.read_bytes())
            payload[-1] ^= 0x01
            fire.write_bytes(payload)
            observation = inspect_asset(quarantine, contracts[1])

        self.assertFalse(observation["accepted"])
        self.assertIn("PROVIDER_MD5_MISMATCH", observation["reason_codes"])
        self.assertIn("PROVIDER_BLAKE3_MISMATCH", observation["reason_codes"])

    def test_wrong_zip_root_and_unsafe_member_fail(self) -> None:
        with TemporaryDirectory() as directory:
            quarantine = Path(directory)
            path = quarantine / "unsafe.zip"
            with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_STORED) as archive:
                archive.writestr("EXPECTED.SAFE/manifest.safe", b"synthetic")
                archive.writestr("../escape.txt", b"never extract")
            hashes = _stream_hashes(path)
            contract = AssetContract(
                role="sentinel",
                provider="synthetic",
                source_record_id="SYNTHETIC",
                provider_id="SYNTHETIC",
                native_id="EXPECTED.SAFE",
                expected_filename=path.name,
                stable_route="not-applicable://synthetic",
                expected_size_bytes=path.stat().st_size,
                container="zip-safe",
                package_id="synthetic-pair-v0.1.0",
                provider_md5=hashes["md5"],
                provider_blake3=hashes["blake3"],
                expected_zip_root="EXPECTED.SAFE",
            )
            observation = inspect_asset(quarantine, contract)

        self.assertFalse(observation["accepted"])
        self.assertIn("ZIP_UNSAFE_MEMBER_PATH", observation["reason_codes"])
        self.assertIn("ZIP_UNEXPECTED_ROOT", observation["reason_codes"])

    def test_unexpected_quarantine_entry_fails_transaction(self) -> None:
        with TemporaryDirectory() as directory:
            quarantine = Path(directory)
            contracts = _synthetic_contracts(quarantine)
            (quarantine / "unplanned.txt").write_text("not allowed", encoding="utf-8")
            evaluation = evaluate_quarantine(quarantine, contracts)

        self.assertFalse(evaluation["accepted_for_atomic_promotion"])
        self.assertEqual(evaluation["unexpected_entries"], ["unplanned.txt"])
        self.assertIn("UNEXPECTED_QUARANTINE_ENTRY", evaluation["reason_codes"])

    def test_multiply_linked_asset_cannot_enter_registration(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            seed = root / "seed"
            seed.mkdir()
            contracts = _synthetic_contracts(seed)
            quarantine = root / "linked-asset"
            quarantine.mkdir()
            shutil.copy2(seed / contracts[0].expected_filename, quarantine / contracts[0].expected_filename)
            os.link(seed / contracts[1].expected_filename, quarantine / contracts[1].expected_filename)
            shutil.copy2(seed / contracts[2].expected_filename, quarantine / contracts[2].expected_filename)

            evaluation = evaluate_quarantine(quarantine, contracts)

        fire = next(item for item in evaluation["observations"] if item["role"] == "fire")
        self.assertFalse(evaluation["accepted_for_atomic_promotion"])
        self.assertEqual(fire["reason_codes"], ["ASSET_MULTILINK_NOT_ALLOWED"])
        self.assertIsNone(fire["local_hashes"])

    def test_linked_quarantine_is_rejected_when_supported(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target"
            target.mkdir()
            contracts = _synthetic_contracts(target)
            linked = root / "linked-quarantine"
            try:
                linked.symlink_to(target, target_is_directory=True)
            except OSError as error:
                self.skipTest(f"directory symlink unavailable: {error}")

            evaluation = evaluate_quarantine(linked, contracts)

        self.assertFalse(evaluation["accepted_for_atomic_promotion"])
        self.assertTrue(evaluation["quarantine_present"])
        self.assertIn("QUARANTINE_LINK_NOT_ALLOWED", evaluation["reason_codes"])

    def test_partial_set_cannot_create_raw_destination(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            seed = root / "seed"
            seed.mkdir()
            contracts = _synthetic_contracts(seed)
            quarantine = root / "partial"
            quarantine.mkdir()
            for contract in contracts[:2]:
                shutil.copy2(seed / contract.expected_filename, quarantine / contract.expected_filename)
            destination = root / "raw" / "package"

            with self.assertRaises(ValueError):
                promote_quarantine(
                    quarantine,
                    destination,
                    contracts,
                    generated_at_utc=GENERATED,
                    run_id=RUN_ID,
                    synthetic_fixture=True,
                )

            self.assertFalse(destination.exists())
            self.assertTrue(quarantine.exists())

    def test_complete_set_is_atomically_promoted_with_registration(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            quarantine = root / "complete"
            quarantine.mkdir()
            contracts = _synthetic_contracts(quarantine)
            destination = root / "raw" / "package"
            registration = promote_quarantine(
                quarantine,
                destination,
                contracts,
                generated_at_utc=GENERATED,
                run_id=RUN_ID,
                synthetic_fixture=True,
            )

            self.assertFalse(quarantine.exists())
            self.assertTrue(destination.is_dir())
            self.assertEqual(registration["asset_count"], 3)
            self.assertTrue(registration["synthetic_fixture"])
            persisted = json.loads((destination / ".burnlens-registration.json").read_text(encoding="utf-8"))
            self.assertEqual(persisted, registration)
            self.assertEqual(len(persisted["assets"]), 3)
            verification = verify_registered_package(destination, contracts)
            self.assertTrue(verification["accepted_as_unchanged_registered_package"])
            self.assertEqual(verification["reason_codes"], ["REGISTERED_PACKAGE_VERIFIED"])

    def test_registered_package_verifier_detects_later_tamper(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            quarantine = root / "complete"
            quarantine.mkdir()
            contracts = _synthetic_contracts(quarantine)
            destination = root / "raw" / "package"
            promote_quarantine(
                quarantine,
                destination,
                contracts,
                generated_at_utc=GENERATED,
                run_id=RUN_ID,
                synthetic_fixture=True,
            )
            fire = destination / contracts[1].expected_filename
            payload = bytearray(fire.read_bytes())
            payload[-1] ^= 0x01
            fire.write_bytes(payload)

            verification = verify_registered_package(destination, contracts)

        self.assertFalse(verification["accepted_as_unchanged_registered_package"])
        self.assertIn("REGISTERED_ASSET_VALIDATION_FAILED", verification["reason_codes"])
        self.assertIn("REGISTRATION_ASSET_MISMATCH", verification["reason_codes"])

    def test_existing_destination_is_never_replaced(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            quarantine = root / "complete"
            quarantine.mkdir()
            contracts = _synthetic_contracts(quarantine)
            destination = root / "raw" / "package"
            destination.mkdir(parents=True)
            marker = destination / "keep.txt"
            marker.write_text("existing", encoding="utf-8")

            with self.assertRaises(FileExistsError):
                promote_quarantine(
                    quarantine,
                    destination,
                    contracts,
                    generated_at_utc=GENERATED,
                    run_id=RUN_ID,
                    synthetic_fixture=True,
                )

            self.assertEqual(marker.read_text(encoding="utf-8"), "existing")
            self.assertTrue(quarantine.exists())

    def test_failed_atomic_rename_rolls_back_registration_and_allows_retry(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            quarantine = root / "complete"
            quarantine.mkdir()
            contracts = _synthetic_contracts(quarantine)
            destination = root / "raw" / "package"

            with patch("burnlens.paired_intake.os.replace", side_effect=OSError("synthetic rename failure")):
                with self.assertRaisesRegex(OSError, "synthetic rename failure"):
                    promote_quarantine(
                        quarantine,
                        destination,
                        contracts,
                        generated_at_utc=GENERATED,
                        run_id=RUN_ID,
                        synthetic_fixture=True,
                    )

            self.assertTrue(quarantine.is_dir())
            self.assertFalse(destination.exists())
            self.assertFalse((quarantine / ".burnlens-registration.json").exists())
            self.assertTrue(evaluate_quarantine(quarantine, contracts)["accepted_for_atomic_promotion"])

            registration = promote_quarantine(
                quarantine,
                destination,
                contracts,
                generated_at_utc=GENERATED,
                run_id=RUN_ID,
                synthetic_fixture=True,
            )
            self.assertEqual(registration["asset_count"], 3)
            self.assertTrue(destination.is_dir())

    def test_synthetic_rehearsal_is_explicit_and_passes(self) -> None:
        result = run_synthetic_rehearsal(generated_at_utc=GENERATED, run_id=RUN_ID)
        self.assertEqual(result["fixture_class"], "SYNTHETIC_TEST_ONLY")
        self.assertFalse(result["provider_data"])
        self.assertFalse(result["credential_used"])
        self.assertTrue(result["passed"])
        self.assertTrue(all(result["checks"].values()))
        self.assertTrue(result["checks"]["post_promotion_tamper_detected"])
        self.assertEqual(result["retained_fixture_bytes"], 0)

    def test_real_report_is_blocked_and_does_not_inflate_claims(self) -> None:
        report = build_report(generated_at_utc=GENERATED, run_id=RUN_ID, source_commit=SOURCE_COMMIT)
        self.assertEqual(report["decision"], "BLOCKED_OWNER_CREDENTIAL")
        self.assertEqual(report["provider_package"]["provider_source_asset_count"], 0)
        self.assertEqual(report["provider_package"]["provider_source_asset_bytes"], 0)
        self.assertEqual(report["provider_package"]["promoted_raw_package_count"], 0)
        self.assertFalse(report["provider_package"]["credentials_used"])
        self.assertIsNone(report["dataset_version"])
        self.assertIn("provider data were acquired", report["claims"]["prohibited"][0].lower())

    def test_metadata_observation_time_is_not_inflated_to_run_time(self) -> None:
        report = build_report(
            generated_at_utc="2030-01-01T00:00:00Z",
            run_id=RUN_ID,
            source_commit=SOURCE_COMMIT,
        )
        snapshot = report["public_metadata_snapshot"]
        self.assertEqual(snapshot["observed_at_utc"], PUBLIC_METADATA_OBSERVED_AT_UTC)
        self.assertFalse(snapshot["live_refresh_performed_by_this_run"])
        self.assertEqual(snapshot["evidence_record"], "ACCESS-2026-005")
        self.assertNotIn("public_metadata_refresh", report)

    def test_report_and_outputs_are_byte_deterministic(self) -> None:
        first = build_report(generated_at_utc=GENERATED, run_id=RUN_ID, source_commit=SOURCE_COMMIT)
        second = build_report(generated_at_utc=GENERATED, run_id=RUN_ID, source_commit=SOURCE_COMMIT)
        self.assertEqual(json.dumps(first, sort_keys=True), json.dumps(second, sort_keys=True))

        with TemporaryDirectory() as directory:
            root = Path(directory)
            first_paths = write_report(first, root / "first")
            second_paths = write_report(second, root / "second")
            for key in ("json", "html", "png"):
                self.assertEqual(first_paths[key].read_bytes(), second_paths[key].read_bytes())

    def test_html_is_semantic_and_distinguishes_synthetic_evidence(self) -> None:
        report = build_report(generated_at_utc=GENERATED, run_id=RUN_ID, source_commit=SOURCE_COMMIT)
        html = render_html(report)
        self.assertIn("<main>", html)
        self.assertIn("<table>", html)
        self.assertIn("Synthetic transaction rehearsal — test fixture only", html)
        self.assertIn("No provider data is used", html)
        self.assertIn("No live provider request was performed by this run", html)
        self.assertIn("Not official wildfire information", html)
        self.assertNotIn("provider data were acquired</p>", html.lower())

    def test_png_has_expected_original_resolution(self) -> None:
        report = build_report(generated_at_utc=GENERATED, run_id=RUN_ID, source_commit=SOURCE_COMMIT)
        with TemporaryDirectory() as directory:
            paths = write_report(report, Path(directory))
            with Image.open(paths["png"]) as image:
                self.assertEqual(image.size, (1600, 1200))
                self.assertEqual(image.mode, "RGB")


if __name__ == "__main__":
    unittest.main()
