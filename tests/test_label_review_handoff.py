from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import zipfile

import burnlens
from burnlens.label_review_handoff import (
    ARCHIVE_ROOT,
    BLIND_PAGE_NAMES,
    HANDOFF_HTML_NAME,
    HANDOFF_JSON_NAME,
    HANDOFF_README_NAME,
    RESPONSE_TEMPLATE_NAME,
    LabelReviewHandoffError,
    build_handoff,
)
from burnlens.lock_label_review_response import (
    LabelReviewResponseLockError,
    RETURNED_INDEPENDENT_RESPONSE,
    SOFTWARE_BROWSER_FIXTURE,
    build_response_lock,
    write_response_lock,
)
from burnlens.verify_label_review_handoff import (
    LabelReviewHandoffVerificationError,
    build_qa_report,
)


ROOT = Path(__file__).resolve().parents[1]
PACKET_DIRECTORY = ROOT / "samples" / "labels" / "review" / "phase-two"
PACKET_PATH = PACKET_DIRECTORY / "LABEL-REVIEW-PACKET-2026-001.json"
SOURCE_COMMIT = "1" * 40
GENERATED_AT = "2026-07-16T17:00:00Z"
RUN_ID = "BL-TEST-LABEL-REVIEW-HANDOFF"


def _sha256_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _build(directory: Path, name: str = "handoff") -> tuple[dict, dict, dict[str, Path]]:
    output = directory / name
    archive = directory / f"{name}.zip"
    return build_handoff(
        packet_path=PACKET_PATH,
        output_directory=output,
        archive_path=archive,
        generated_at_utc=GENERATED_AT,
        run_id=RUN_ID,
        git_source_commit=SOURCE_COMMIT,
    )


def _completed_response() -> dict:
    response = json.loads(
        (PACKET_DIRECTORY / RESPONSE_TEMPLATE_NAME).read_text(encoding="utf-8")
    )
    response["reviewer"] = {
        "reviewer_id": "opaque-reviewer-test-only",
        "independent_from_proposal_author": True,
        "burned_area_interpretation_experience": "synthetic software fixture",
        "proposal_seen_before_first_pass": False,
        "attestation": "Synthetic fixture only; not a human response.",
    }
    response["review_started_at_utc"] = "2026-07-16T17:10:00Z"
    response["review_completed_at_utc"] = "2026-07-16T17:20:00Z"
    response["completed"] = True
    for item in response["responses"]:
        item.update(
            {
                "first_pass_label": "uncertain",
                "evidence_sufficiency": "limited",
                "confidence": "low",
                "reason_codes": ["low-severity-ambiguity"],
                "notes": None,
            }
        )
    return response


def _rewrite_archive(
    source: Path,
    target: Path,
    *,
    payload_updates: dict[str, bytes] | None = None,
    member_name_updates: dict[str, str] | None = None,
) -> None:
    payload_updates = payload_updates or {}
    member_name_updates = member_name_updates or {}
    with zipfile.ZipFile(source, "r") as original:
        infos = original.infolist()
        payloads = {info.filename: original.read(info) for info in infos}
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_STORED) as rewritten:
        for info in infos:
            name = member_name_updates.get(info.filename, info.filename)
            replacement = zipfile.ZipInfo(name, date_time=info.date_time)
            replacement.compress_type = zipfile.ZIP_STORED
            replacement.create_system = 3
            replacement.external_attr = 0o100644 << 16
            payload = payload_updates.get(info.filename, payloads[info.filename])
            rewritten.writestr(replacement, payload)


class LabelReviewHandoffTests(unittest.TestCase):
    def test_current_package_version_preserves_reviewer_handoff_contract(self) -> None:
        self.assertEqual(burnlens.__version__, "0.40.0")

    def test_repeated_handoff_build_is_byte_identical_and_allowlisted(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest_one, archive_one, paths_one = _build(root, "one")
            manifest_two, archive_two, paths_two = _build(root, "two")
            self.assertEqual(archive_one["sha256"], archive_two["sha256"])
            self.assertEqual(archive_one["bytes"], archive_two["bytes"])
            self.assertEqual((root / "one.zip").read_bytes(), (root / "two.zip").read_bytes())
            for key in ("html", "json", "png", "readme"):
                self.assertEqual(paths_one[key].read_bytes(), paths_two[key].read_bytes())
            self.assertEqual(
                manifest_one["decision"],
                "READY_FOR_ISOLATED_INDEPENDENT_REVIEW_DEFER_DATASET",
            )
            self.assertEqual(manifest_one, manifest_two)
            with zipfile.ZipFile(root / "one.zip", "r") as archive:
                names = [Path(info.filename).name for info in archive.infolist()]
                self.assertEqual(
                    names,
                    [
                        HANDOFF_JSON_NAME,
                        HANDOFF_HTML_NAME,
                        HANDOFF_README_NAME,
                        RESPONSE_TEMPLATE_NAME,
                        *BLIND_PAGE_NAMES,
                    ],
                )
                self.assertTrue(
                    all(
                        Path(info.filename).parent.as_posix() == ARCHIVE_ROOT
                        for info in archive.infolist()
                    )
                )
                self.assertNotIn("LABEL-REVIEW-PACKET-2026-001-REVEAL.html", names)
                self.assertNotIn("LABEL-REVIEW-PACKET-2026-001.json", names)
                self.assertNotIn(
                    "LABEL-REVIEW-PACKET-2026-001-ADJUDICATION-TEMPLATE.json",
                    names,
                )

    def test_independent_handoff_verifier_accepts_exact_archive(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            _, archive, _ = _build(root)
            report = build_qa_report(
                archive_path=root / "handoff.zip",
                generated_at_utc="2026-07-16T17:05:00Z",
                run_id="BL-TEST-LABEL-REVIEW-HANDOFF-QA",
                git_source_commit=SOURCE_COMMIT,
            )
            self.assertEqual(
                report["decision"],
                "PASS_HANDOFF_INTEGRITY_READY_FOR_INDEPENDENT_REVIEW_DEFER_DATASET",
            )
            self.assertEqual(report["archive_binding"]["sha256"], archive["sha256"])
            self.assertEqual(report["checks"]["workbench"]["unit_fieldsets"], 56)
            self.assertEqual(report["checks"]["blind_pages"]["count"], 8)
            self.assertEqual(report["completed_independent_responses"], 0)
            self.assertIsNone(report["dataset_version"])

    def test_verifier_rejects_unsafe_member_path(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            _build(root)
            source = root / "handoff.zip"
            with zipfile.ZipFile(source, "r") as archive:
                first = archive.infolist()[0].filename
            tampered = root / "unsafe.zip"
            _rewrite_archive(
                source,
                tampered,
                member_name_updates={first: "../HANDOFF.json"},
            )
            with self.assertRaisesRegex(
                LabelReviewHandoffVerificationError,
                "allowlist or order",
            ):
                build_qa_report(
                    archive_path=tampered,
                    generated_at_utc="2026-07-16T17:05:00Z",
                    run_id="BL-TEST-UNSAFE",
                    git_source_commit=SOURCE_COMMIT,
                )

    def test_verifier_rejects_network_enabled_workbench_even_with_updated_binding(
        self,
    ) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            _build(root)
            source = root / "handoff.zip"
            html_member = f"{ARCHIVE_ROOT}/{HANDOFF_HTML_NAME}"
            manifest_member = f"{ARCHIVE_ROOT}/{HANDOFF_JSON_NAME}"
            with zipfile.ZipFile(source, "r") as archive:
                html_payload = archive.read(html_member) + b"\n<!-- https://example.com -->\n"
                manifest = json.loads(archive.read(manifest_member).decode("utf-8"))
            for item in manifest["members"]:
                if item["path"] == HANDOFF_HTML_NAME:
                    item["bytes"] = len(html_payload)
                    item["sha256"] = sha256(html_payload).hexdigest()
            manifest_payload = (json.dumps(manifest, indent=2) + "\n").encode("utf-8")
            tampered = root / "network.zip"
            _rewrite_archive(
                source,
                tampered,
                payload_updates={
                    html_member: html_payload,
                    manifest_member: manifest_payload,
                },
            )
            with self.assertRaisesRegex(
                LabelReviewHandoffVerificationError,
                "network tokens",
            ):
                build_qa_report(
                    archive_path=tampered,
                    generated_at_utc="2026-07-16T17:05:00Z",
                    run_id="BL-TEST-NETWORK",
                    git_source_commit=SOURCE_COMMIT,
                )

    def test_response_lock_accepts_only_actual_complete_contract_bytes(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            response_path = root / "synthetic-response.json"
            response_path.write_text(
                json.dumps(_completed_response(), indent=2) + "\n",
                encoding="utf-8",
                newline="\n",
            )
            report = build_response_lock(
                packet_path=PACKET_PATH,
                response_path=response_path,
                receipt_id="LABEL-REVIEW-RESPONSE-LOCK-TEST-001",
                received_at_utc="2026-07-16T17:21:00Z",
                run_id="BL-TEST-LABEL-REVIEW-RESPONSE-LOCK",
                git_source_commit=SOURCE_COMMIT,
                evidence_origin=RETURNED_INDEPENDENT_RESPONSE,
                task_issue=379,
            )
            self.assertEqual(
                report["decision"],
                "PASS_RESPONSE_CONTRACT_AND_HASH_LOCK_DEFER_SCIENTIFIC_USE",
            )
            self.assertEqual(report["response_binding"]["sha256"], _sha256_file(response_path))
            self.assertFalse(report["human_identity_verified_by_software"])
            self.assertFalse(report["scientific_label_fitness_established"])
            self.assertEqual(report["evidence_origin"], RETURNED_INDEPENDENT_RESPONSE)
            self.assertIsNone(report["qualifying_independent_human_response"])
            output = root / "lock.json"
            write_response_lock(report, output)
            with self.assertRaisesRegex(
                LabelReviewResponseLockError,
                "refusing to overwrite",
            ):
                write_response_lock(report, output)

            tampered = _completed_response()
            tampered["responses"][0]["proposal_state"] = "unknown"
            response_path = root / "tampered-response.json"
            response_path.write_text(
                json.dumps(tampered, indent=2) + "\n",
                encoding="utf-8",
                newline="\n",
            )
            with self.assertRaisesRegex(
                LabelReviewResponseLockError,
                "proposal-value fields",
            ):
                build_response_lock(
                    packet_path=PACKET_PATH,
                    response_path=response_path,
                    receipt_id="LABEL-REVIEW-RESPONSE-LOCK-TEST-002",
                    received_at_utc="2026-07-16T17:22:00Z",
                    run_id="BL-TEST-LABEL-REVIEW-RESPONSE-LOCK-TAMPER",
                    git_source_commit=SOURCE_COMMIT,
                    evidence_origin=RETURNED_INDEPENDENT_RESPONSE,
                    task_issue=379,
                )

            fixture_path = root / "fixture-response.json"
            fixture_path.write_text(
                json.dumps(_completed_response(), indent=2) + "\n",
                encoding="utf-8",
                newline="\n",
            )
            fixture = build_response_lock(
                packet_path=PACKET_PATH,
                response_path=fixture_path,
                receipt_id="LABEL-REVIEW-RESPONSE-LOCK-TEST-003",
                received_at_utc="2026-07-16T17:23:00Z",
                run_id="BL-TEST-LABEL-REVIEW-RESPONSE-LOCK-FIXTURE",
                git_source_commit=SOURCE_COMMIT,
                evidence_origin=SOFTWARE_BROWSER_FIXTURE,
                task_issue=383,
            )
            self.assertEqual(
                fixture["decision"],
                "PASS_SOFTWARE_FIXTURE_CONTRACT_AND_HASH_LOCK_NO_REVEAL",
            )
            self.assertTrue(fixture["software_browser_fixture"])
            self.assertFalse(fixture["qualifying_independent_human_response"])
            self.assertTrue(fixture["reveal_release"].startswith("prohibited:"))

            with self.assertRaisesRegex(
                LabelReviewResponseLockError,
                "predates response completion",
            ):
                build_response_lock(
                    packet_path=PACKET_PATH,
                    response_path=fixture_path,
                    receipt_id="LABEL-REVIEW-RESPONSE-LOCK-TEST-004",
                    received_at_utc="2026-07-16T17:19:59Z",
                    run_id="BL-TEST-LABEL-REVIEW-RESPONSE-LOCK-EARLY",
                    git_source_commit=SOURCE_COMMIT,
                    evidence_origin=RETURNED_INDEPENDENT_RESPONSE,
                    task_issue=384,
                )

    def test_builder_refuses_packet_hash_drift_and_output_overwrite(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            _build(root)
            with self.assertRaisesRegex(LabelReviewHandoffError, "overwrite"):
                _build(root)
            packet_copy = root / PACKET_PATH.name
            packet = json.loads(PACKET_PATH.read_text(encoding="utf-8"))
            packet["decision"] = "TAMPERED"
            packet_copy.write_text(json.dumps(packet), encoding="utf-8")
            with self.assertRaisesRegex(LabelReviewHandoffError, "SHA-256 differs"):
                build_handoff(
                    packet_path=packet_copy,
                    output_directory=root / "tampered",
                    archive_path=root / "tampered.zip",
                    generated_at_utc=GENERATED_AT,
                    run_id=RUN_ID,
                    git_source_commit=SOURCE_COMMIT,
                )


if __name__ == "__main__":
    unittest.main()
