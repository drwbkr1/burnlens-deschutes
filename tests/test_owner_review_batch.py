from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from PIL import Image
import burnlens.owner_review_batch as owner_review_batch

from burnlens.owner_review_batch import (
    DEFAULT_BATCH_MAX,
    DEFAULT_BATCH_MIN,
    HARD_BATCH_MAX,
    MANIFEST_SCHEMA_VERSION,
    REGISTRY_SCHEMA_VERSION,
    OwnerReviewBatchError,
    add_registry_entry,
    build_surface,
    response_template,
    validate_completed_response,
    validate_manifest,
    validate_registry,
    validate_response,
    write_surface,
)


class OwnerReviewBatchTests(unittest.TestCase):
    def _evidence(self, root: Path, count: int) -> list[dict[str, object]]:
        values: list[dict[str, object]] = []
        for index in range(count):
            path = root / f"evidence-{index + 1:03d}.png"
            Image.new("RGB", (80, 40), (20 + index, 70, 60)).save(path, format="PNG", optimize=False)
            data = path.read_bytes()
            values.append(
                {
                    "path": path.name,
                    "bytes": len(data),
                    "sha256": sha256(data).hexdigest(),
                    "alt": f"Synthetic evidence for candidate {index + 1}; no owner or label evidence.",
                }
            )
        return values

    def _manifest(
        self,
        root: Path,
        count: int,
        *,
        exception: str | None = None,
        surface_id: str = "OWNER-REVIEW-BATCH-TEST-001",
        revision: int = 1,
        supersedes: str | None = None,
    ) -> dict:
        evidence = self._evidence(root, count)
        candidates = []
        groups = []
        cursor = 0
        group_sizes = [2] if exception == "single-event-pair" else [2] * (count // 2) + ([1] if count % 2 else [])
        for group_index, group_size in enumerate(group_sizes, start=1):
            event_id = "event-petes-lake-2023" if exception == "single-event-pair" else f"event-fixture-{group_index:02d}"
            ids = []
            class_order = ("burned", "background") if group_index % 2 else ("background", "burned")
            for member in range(group_size):
                index = cursor
                candidate_id = f"CAND-{index + 1:03d}"
                proposed_class = class_order[member] if member < 2 else "burned"
                ids.append(candidate_id)
                candidates.append(
                    {
                        "candidate_id": candidate_id,
                        "event_group_id": event_id,
                        "proposed_class": proposed_class,
                        "question": f"Is this exact region a usable prototype {proposed_class} label candidate?",
                        "proposition_basis": "Synthetic deterministic fixture basis for contract testing only.",
                        "limitations": ["Synthetic fixture; not owner evidence and not a label."],
                        "facts": [
                            {"label": "Core", "value": "25 native-grid pixels"},
                            {"label": "Unknown ring", "value": "excluded"},
                        ],
                        "proposal_binding": {
                            "record_id": f"PROPOSAL-{index + 1:03d}",
                            "bytes": 100 + index,
                            "sha256": sha256(f"proposal-{index}".encode()).hexdigest(),
                        },
                        "candidate_raster_binding": {
                            "path": f"candidate-{index + 1:03d}.tif",
                            "bytes": 200 + index,
                            "sha256": sha256(f"raster-{index}".encode()).hexdigest(),
                        },
                        "evidence_images": [evidence[index]],
                    }
                )
                cursor += 1
            groups.append(
                {
                    "event_group_id": event_id,
                    "event_label": "Petes Lake 2023" if exception == "single-event-pair" else f"Fixture event {group_index}",
                    "context": "Shared event context; proposed classes remain separate decisions.",
                    "candidate_ids": ids,
                }
            )
        return {
            "manifest_schema_version": MANIFEST_SCHEMA_VERSION,
            "surface_id": surface_id,
            "surface_revision": revision,
            "surface_run_id": f"BL-TEST-{surface_id}-R{revision:03d}",
            "milestone_id": "P2O4-T33",
            "task_issue": 521,
            "generated_at_utc": "2026-07-21T15:00:00Z",
            "git_source_commit": "a" * 40,
            "title": "Synthetic owner-review batch contract",
            "review_groups": groups,
            "candidates": candidates,
            "batch_size_exception": exception,
            "supersedes_surface_id": supersedes,
        }

    def test_batch_size_contract_and_single_event_pair(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            for count in range(DEFAULT_BATCH_MIN, DEFAULT_BATCH_MAX + 1):
                with self.subTest(normal_count=count):
                    surface = build_surface(self._manifest(root, count))
                    self.assertEqual(surface["summary"]["candidate_count"], count)
            petes = build_surface(self._manifest(root, 2, exception="single-event-pair"))
            self.assertEqual(petes["summary"]["event_group_count"], 1)
            self.assertEqual({item["proposed_class"] for item in petes["candidates"]}, {"burned", "background"})
            for count in (1, 3, 7, HARD_BATCH_MAX):
                with self.subTest(exception_count=count):
                    surface = build_surface(self._manifest(root, count, exception="recorded-size-exception"))
                    self.assertEqual(surface["summary"]["candidate_count"], count)
            with self.assertRaisesRegex(OwnerReviewBatchError, "explicit exception"):
                build_surface(self._manifest(root, 7))
            with self.assertRaisesRegex(OwnerReviewBatchError, "between 1 and"):
                build_surface(self._manifest(root, HARD_BATCH_MAX + 1, exception="recorded-size-exception"))
            with self.assertRaisesRegex(OwnerReviewBatchError, "do not use a size exception"):
                build_surface(self._manifest(root, 4, exception="unneeded-exception"))
            broken_pair = self._manifest(root, 2, exception="single-event-pair")
            broken_pair["candidates"][1]["proposed_class"] = "burned"
            with self.assertRaisesRegex(OwnerReviewBatchError, "one burned and one background"):
                build_surface(broken_pair)
            with self.assertRaisesRegex(OwnerReviewBatchError, "single-event-pair"):
                build_surface(self._manifest(root, 2, exception="not-a-pair"))
            with self.assertRaisesRegex(OwnerReviewBatchError, "invalid"):
                build_surface(self._manifest(root, 1, exception="   "))

    def test_manifest_rejects_duplicate_identity_order_and_hidden_bias_fields(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest = self._manifest(root, 4)
            duplicate = deepcopy(manifest)
            duplicate["candidates"][1]["candidate_id"] = duplicate["candidates"][0]["candidate_id"]
            duplicate["review_groups"][0]["candidate_ids"][1] = duplicate["review_groups"][0]["candidate_ids"][0]
            with self.assertRaisesRegex(OwnerReviewBatchError, "duplicate candidate"):
                validate_manifest(duplicate)
            reordered = deepcopy(manifest)
            reordered["review_groups"][0]["candidate_ids"].reverse()
            with self.assertRaisesRegex(OwnerReviewBatchError, "exactly match"):
                validate_manifest(reordered)
            mixed = deepcopy(manifest)
            mixed["candidates"][0]["event_group_id"] = "event-other-milestone"
            with self.assertRaisesRegex(OwnerReviewBatchError, "event group binding"):
                validate_manifest(mixed)
            biased = deepcopy(manifest)
            biased["candidates"][0]["confidence"] = 0.99
            with self.assertRaisesRegex(OwnerReviewBatchError, "fields changed"):
                validate_manifest(biased)
            aliased = deepcopy(manifest)
            aliased["candidates"][1]["evidence_images"][0]["path"] = "./evidence-001.png"
            with self.assertRaisesRegex(OwnerReviewBatchError, "not canonical"):
                validate_manifest(aliased)

    def test_ordered_manifest_and_candidate_hashes_change_on_bound_evidence(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest = self._manifest(root, 4)
            first = build_surface(manifest)
            repeat = build_surface(manifest)
            reconstructed = build_surface(first["batch_manifest"])
            self.assertEqual(first["ordered_manifest_sha256"], repeat["ordered_manifest_sha256"])
            self.assertEqual(first["ordered_manifest_sha256"], reconstructed["ordered_manifest_sha256"])
            self.assertEqual(
                [item["candidate_binding_sha256"] for item in first["candidates"]],
                [item["candidate_binding_sha256"] for item in repeat["candidates"]],
            )
            changed = deepcopy(manifest)
            changed["candidates"][0]["evidence_images"][0]["sha256"] = "f" * 64
            revised = build_surface(changed)
            self.assertNotEqual(first["ordered_manifest_sha256"], revised["ordered_manifest_sha256"])
            self.assertNotEqual(first["candidates"][0]["candidate_binding_sha256"], revised["candidates"][0]["candidate_binding_sha256"])

    def test_response_template_draft_and_completed_contract(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            surface = build_surface(self._manifest(root, 2, exception="single-event-pair"))
            template = response_template(surface)
            self.assertFalse(template["completed"])
            self.assertFalse(template["owner"]["attestation"])
            self.assertTrue(all(item["decision"] is None for item in template["responses"]))
            draft = validate_response(surface, deepcopy(template), require_completed=False)
            self.assertEqual(draft["answered_count"], 0)
            with self.assertRaisesRegex(OwnerReviewBatchError, "incomplete"):
                validate_completed_response(surface, deepcopy(template))
            completed = deepcopy(template)
            completed.update(
                completed=True,
                review_started_at_utc="2026-07-21T15:01:00Z",
                review_completed_at_utc="2026-07-21T15:03:00Z",
            )
            completed["owner"]["attestation"] = True
            completed["responses"][0]["decision"] = "yes"
            completed["responses"][1]["decision"] = "uncertain"
            summary = validate_completed_response(surface, completed)
            self.assertEqual(summary["decision_counts"], {"yes": 1, "no": 0, "uncertain": 1})
            incomplete = deepcopy(completed)
            incomplete["responses"][1]["decision"] = None
            with self.assertRaisesRegex(OwnerReviewBatchError, "missing"):
                validate_completed_response(surface, incomplete)
            reordered = deepcopy(completed)
            reordered["responses"].reverse()
            with self.assertRaisesRegex(OwnerReviewBatchError, "order or identity"):
                validate_completed_response(surface, reordered)
            boolean_revision = deepcopy(completed)
            boolean_revision["surface_revision"] = True
            with self.assertRaisesRegex(OwnerReviewBatchError, "surface revision"):
                validate_completed_response(surface, boolean_revision)

    def test_surface_output_has_candidate_navigation_summary_and_no_bulk_controls(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            evidence_root = root / "evidence"
            evidence_root.mkdir()
            surface = build_surface(self._manifest(evidence_root, 5))
            output = root / "surface"
            bindings = write_surface(surface, evidence_root, output)
            self.assertEqual(len(bindings), 1 + 3 + 5)
            html_path = output / f"{surface['report_id']}.html"
            html = html_path.read_text(encoding="utf-8")
            self.assertEqual(html.count('value="yes"'), 5)
            self.assertEqual(html.count('value="no"'), 5)
            self.assertEqual(html.count('value="uncertain"'), 5)
            self.assertNotIn(" checked", html)
            self.assertNotIn("approve all", html.lower())
            self.assertNotIn("confidence", html.lower())
            self.assertNotIn("prior decision", html.lower())
            self.assertNotIn("http://", html)
            self.assertNotIn("https://", html)
            self.assertIn("Resume at first unanswered", html)
            self.assertIn("Review final decisions", html)
            self.assertIn("This is not a bulk approval", html)
            self.assertIn("Response is locked in this browser session", html)
            self.assertIn("function zonedTime", html)
            self.assertIn("draft timestamps are invalid", html)
            controller = html.rsplit("<script>", 1)[1].split("</script>", 1)[0]
            controller_path = root / "controller.js"
            controller_path.write_text(controller, encoding="utf-8", newline="\n")
            checked = subprocess.run(["node", "--check", str(controller_path)], capture_output=True, text=True)
            self.assertEqual(checked.returncode, 0, checked.stderr)
            timestamp_functions = controller[
                controller.index("function zonedTime") : controller.index("function validateLoaded")
            ]
            timestamp_probe = root / "timestamp-probe.js"
            timestamp_probe.write_text(
                timestamp_functions
                + """
const valid = ['2026-02-28T12:00:00Z', '2024-02-29T12:00:00.123+00:00'];
const invalid = ['2026-02-29T12:00:00Z', '2026-02-30T12:00:00Z', '2026-04-31T12:00:00Z', '0000-01-01T00:00:00Z', '2026-01-01T00:00:00', '2026-01-01T00:00:00+24:00'];
if (valid.some(value => !Number.isFinite(zonedTime(value)))) throw new Error('valid timestamp rejected');
if (invalid.some(value => Number.isFinite(zonedTime(value)))) throw new Error('invalid timestamp accepted');
if (!validCompletionOrder('2026-01-01T00:00:00Z', '2026-01-01T00:00:01Z')) throw new Error('valid order rejected');
if (validCompletionOrder('2099-01-01T00:00:00Z', '2026-01-01T00:00:00Z')) throw new Error('reversed order accepted');
""",
                encoding="utf-8",
                newline="\n",
            )
            probed = subprocess.run(["node", str(timestamp_probe)], capture_output=True, text=True)
            self.assertEqual(probed.returncode, 0, probed.stderr)
            report = json.loads((output / f"{surface['report_id']}.json").read_text(encoding="utf-8"))
            self.assertEqual(report["summary"]["owner_responses"], 0)
            self.assertEqual(report["summary"]["labels_created"], 0)
            with self.assertRaisesRegex(OwnerReviewBatchError, "already exists"):
                write_surface(surface, evidence_root, output)

    def test_surface_write_fails_before_output_on_evidence_drift(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            evidence_root = root / "evidence"
            evidence_root.mkdir()
            surface = build_surface(self._manifest(evidence_root, 4))
            (evidence_root / "evidence-001.png").write_bytes(b"changed")
            output = root / "surface"
            with self.assertRaisesRegex(OwnerReviewBatchError, "byte count changed"):
                write_surface(surface, evidence_root, output)
            self.assertFalse(output.exists())

    def test_surface_write_rejects_stale_contract_and_rolls_back_partial_output(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            evidence_root = root / "evidence"
            evidence_root.mkdir()
            surface = build_surface(self._manifest(evidence_root, 4))
            stale = deepcopy(surface)
            stale["decision_contract"]["yes"] = "mutated after manifest freeze"
            with self.assertRaisesRegex(OwnerReviewBatchError, "does not reconstruct"):
                write_surface(stale, evidence_root, root / "stale")
            self.assertFalse((root / "stale").exists())

            output = root / "partial"
            original_write = owner_review_batch._write_bytes
            call_count = 0

            def fail_on_third_write(path: Path, data: bytes) -> None:
                nonlocal call_count
                call_count += 1
                if call_count == 3:
                    raise OSError("synthetic write failure")
                original_write(path, data)

            with patch.object(owner_review_batch, "_write_bytes", side_effect=fail_on_third_write):
                with self.assertRaisesRegex(OSError, "synthetic write failure"):
                    write_surface(surface, evidence_root, output)
            self.assertFalse(output.exists())

    def test_surface_files_reconstruct_byte_for_byte(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            evidence_root = root / "evidence"
            evidence_root.mkdir()
            surface = build_surface(self._manifest(evidence_root, 6))
            first = root / "first"
            second = root / "second"
            first_bindings = write_surface(surface, evidence_root, first)
            second_bindings = write_surface(surface, evidence_root, second)
            self.assertEqual(first_bindings, second_bindings)
            for binding in first_bindings:
                self.assertEqual(
                    (first / binding["path"]).read_bytes(),
                    (second / binding["path"]).read_bytes(),
                )

    def test_registry_rejects_duplicate_active_membership_and_revision(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            first = build_surface(self._manifest(root, 4, surface_id="OWNER-REVIEW-BATCH-TEST-001"))
            second = build_surface(self._manifest(root, 4, surface_id="OWNER-REVIEW-BATCH-TEST-002"))
            registry = {"registry_schema_version": REGISTRY_SCHEMA_VERSION, "entries": []}
            registry = add_registry_entry(registry, first)
            with self.assertRaisesRegex(OwnerReviewBatchError, "two active surfaces"):
                add_registry_entry(registry, second)
            completed_registry = deepcopy(registry)
            completed_registry["entries"][0]["state"] = "completed"
            combined = add_registry_entry(completed_registry, second)
            self.assertEqual(len(combined["entries"]), 2)
            duplicate_revision = deepcopy(combined)
            duplicate_revision["entries"].append(deepcopy(duplicate_revision["entries"][1]))
            with self.assertRaisesRegex(OwnerReviewBatchError, "already registered"):
                validate_registry(duplicate_revision)

            mutated = deepcopy(first)
            mutated["candidates"] = mutated["candidates"][:1]
            with self.assertRaisesRegex(OwnerReviewBatchError, "does not reconstruct"):
                add_registry_entry({"registry_schema_version": REGISTRY_SCHEMA_VERSION, "entries": []}, mutated)

            invalid_size = deepcopy(registry)
            invalid_size["entries"][0]["candidate_ids"] = invalid_size["entries"][0]["candidate_ids"][:1]
            invalid_size["entries"][0]["candidate_count"] = 1
            invalid_size["entries"][0]["batch_size_exception"] = None
            with self.assertRaisesRegex(OwnerReviewBatchError, "explicit exception"):
                validate_registry(invalid_size)

            boolean_revision = deepcopy(registry)
            boolean_revision["entries"][0]["surface_revision"] = True
            with self.assertRaisesRegex(OwnerReviewBatchError, "revision is invalid"):
                validate_registry(boolean_revision)

    def test_registry_requires_a_coherent_supersession_chain(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            surface_id = "OWNER-REVIEW-BATCH-REVISION-TEST"
            first = build_surface(self._manifest(root, 4, surface_id=surface_id))
            second = build_surface(
                self._manifest(root, 4, surface_id=surface_id, revision=2, supersedes=surface_id)
            )
            empty = {"registry_schema_version": REGISTRY_SCHEMA_VERSION, "entries": []}
            with self.assertRaisesRegex(OwnerReviewBatchError, "predecessor is not registered"):
                add_registry_entry(empty, second)

            active_first = add_registry_entry(empty, first)
            with self.assertRaisesRegex(OwnerReviewBatchError, "superseded predecessor"):
                add_registry_entry(active_first, second, state="completed")

            superseded_first = add_registry_entry(empty, first, state="superseded")
            complete_chain = add_registry_entry(superseded_first, second)
            self.assertEqual([entry["surface_revision"] for entry in complete_chain["entries"]], [1, 2])


if __name__ == "__main__":
    unittest.main()
