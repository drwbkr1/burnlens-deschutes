from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from burnlens.owner_review_batch import (
    OwnerReviewBatchError,
    build_surface,
    response_template,
    validate_response,
)
from burnlens.serve_review_surface import prepare_review_surface
from burnlens.windigo_owner_review_surface import (
    EXPECTED_CANDIDATES,
    PROPOSAL_JSON_SHA256,
    SURFACE_ID,
    build_manifest,
    write_windigo_surface,
)


ROOT = Path(__file__).resolve().parents[1]
PROPOSAL = ROOT / "samples" / "labels" / "pilot" / "windigo" / "phase-two"


@unittest.skipUnless(PROPOSAL.is_dir(), "tracked Windigo proposal unavailable")
class WindigoOwnerReviewSurfaceTests(unittest.TestCase):
    def test_manifest_is_exact_blank_single_event_pair(self) -> None:
        with TemporaryDirectory() as temporary:
            manifest = build_manifest(
                PROPOSAL,
                Path(temporary),
                generated_at_utc="2026-07-23T22:30:00Z",
                run_id="BL-TEST-WINDIGO-OWNER-REVIEW",
                git_source_commit="a" * 40,
            )
            surface = build_surface(manifest)
            template = response_template(surface)
            self.assertEqual(surface["report_id"], SURFACE_ID)
            self.assertEqual(surface["batch_manifest"]["batch_size_exception"], "single-event-pair")
            self.assertEqual(
                [(item["candidate_id"], item["proposed_class"]) for item in surface["candidates"]],
                [("WDP-001", "burned"), ("WDP-002", "background")],
            )
            self.assertEqual(
                {item["proposal_binding"]["sha256"] for item in surface["candidates"]},
                {PROPOSAL_JSON_SHA256},
            )
            self.assertEqual(
                {item["candidate_raster_binding"]["sha256"] for item in surface["candidates"]},
                {value["raster_sha256"] for value in EXPECTED_CANDIDATES.values()},
            )
            self.assertFalse(template["completed"])
            self.assertFalse(template["owner"]["attestation"])
            self.assertTrue(all(item["decision"] is None for item in template["responses"]))
            summary = validate_response(surface, template, require_completed=False)
            self.assertEqual(summary["answered_count"], 0)

    def test_outputs_are_no_overwrite_and_have_no_bulk_or_prefilled_controls(self) -> None:
        with TemporaryDirectory() as temporary:
            output = Path(temporary) / "surface"
            bindings = write_windigo_surface(
                PROPOSAL,
                output,
                generated_at_utc="2026-07-23T22:30:00Z",
                run_id="BL-TEST-WINDIGO-OWNER-REVIEW",
                git_source_commit="a" * 40,
            )
            self.assertEqual(len(bindings), 6)
            report = json.loads((output / f"{SURFACE_ID}.json").read_text(encoding="utf-8"))
            html = (output / f"{SURFACE_ID}.html").read_text(encoding="utf-8")
            template = json.loads(
                (output / f"{SURFACE_ID}-RESPONSE-TEMPLATE.json").read_text(encoding="utf-8")
            )
            self.assertEqual(report["summary"]["candidate_count"], 2)
            self.assertEqual(report["summary"]["owner_responses"], 0)
            self.assertEqual(report["summary"]["labels_created"], 0)
            self.assertEqual(html.count('value="yes"'), 2)
            self.assertEqual(html.count('value="no"'), 2)
            self.assertEqual(html.count('value="uncertain"'), 2)
            self.assertNotIn(" checked", html)
            self.assertNotIn("approve all", html.lower())
            self.assertNotIn("confidence", html.lower())
            self.assertNotIn("prior decision", html.lower())
            self.assertNotIn("Â", html)
            self.assertTrue(all(item["decision"] is None for item in template["responses"]))
            self.assertEqual(len([item for item in bindings if item["media_type"] == "image/png"]), 2)
            snapshot = prepare_review_surface(output / f"{SURFACE_ID}.html")
            self.assertEqual(len(snapshot.resources), 3)
            with self.assertRaisesRegex(OwnerReviewBatchError, "already exists"):
                write_windigo_surface(
                    PROPOSAL,
                    output,
                    generated_at_utc="2026-07-23T22:30:00Z",
                    run_id="BL-TEST-WINDIGO-OWNER-REVIEW",
                    git_source_commit="a" * 40,
                )

    def test_exact_proposal_hash_is_fail_closed(self) -> None:
        self.assertEqual(PROPOSAL_JSON_SHA256, "612143b0d54f6203026f00cc7848ea4d073b219967c75014b5d119ed85ec7365")
