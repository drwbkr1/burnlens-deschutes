from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

import burnlens
from burnlens.green_ridge_owner_review_surface import (
    RESPONSE_SCHEMA_VERSION,
    SURFACE_ID,
    _response_template,
    build_surface,
    write_surface,
)


ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = ROOT / "downloads/phase-two/raw/green-ridge-s2-optical-pair-v0.1.0"
EXTENDED = ROOT / "downloads/phase-two/raw/green-ridge-s2-background-extended-v0.1.0"
REFERENCE = ROOT / "downloads/phase-two/quarantine/BL-2026-07-19-green-ridge-reference-delivery-r001/usgs-delivery-20260719232840Z.zip"
PLAN = ROOT / "samples/cross-event/phase-two/ADDITIONAL-EVENT-GROUP-PLAN-2026-001.json"
PUBLIC = ROOT / "samples/labels/review/green-ridge/phase-two" / f"{SURFACE_ID}.json"


@unittest.skipUnless(ORIGINAL.is_dir() and EXTENDED.is_dir() and REFERENCE.is_file(), "ignored exact custody unavailable")
class GreenRidgeOwnerReviewSurfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report, cls.selected, cls.previews = build_surface(
            repository_root=ROOT, original_package=ORIGINAL, extended_package=EXTENDED,
            plan_path=PLAN, reference_archive=REFERENCE,
            generated_at_utc="2026-07-20T02:15:00Z",
            run_id="BL-TEST-GREEN-RIDGE-OWNER-REVIEW-SURFACE",
            git_source_commit="a" * 40,
        )

    def test_exact_proposals_are_bound_without_promotion(self) -> None:
        self.assertEqual(burnlens.__version__, "0.45.0")
        self.assertEqual(self.report["report_id"], SURFACE_ID)
        self.assertEqual(self.report["summary"], {"candidate_count": 2, "owner_responses": 0, "labels_created": 0, "dataset_count": 0, "model_count": 0})
        self.assertEqual([item["candidate_id"] for item in self.report["candidates"]], ["GRP-001", "GRP-002"])
        self.assertEqual({item["proposed_class"] for item in self.report["candidates"]}, {"burned", "background"})
        self.assertTrue(all(item["owner_decision"] is None for item in self.report["candidates"]))
        self.assertFalse(any(self.report["claim_boundaries"].values()))
        self.assertTrue(self.report["response_custody_contract"]["no_overwrite"])

    def test_blank_template_binds_both_rasters(self) -> None:
        template = _response_template(self.report)
        self.assertEqual(template["response_schema_version"], RESPONSE_SCHEMA_VERSION)
        self.assertFalse(template["completed"])
        self.assertFalse(template["owner"]["attestation"])
        self.assertEqual(len(template["responses"]), 2)
        self.assertTrue(all(item["decision"] is None for item in template["responses"]))

    def test_surface_has_five_panel_evidence_and_valid_controller(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "surface"
            bindings = write_surface(json.loads(json.dumps(self.report)), self.selected, self.previews, output)
            self.assertEqual(len(bindings), 6)
            html = (output / f"{SURFACE_ID}.html").read_text(encoding="utf-8")
            self.assertEqual(html.count('value="yes"'), 2)
            self.assertEqual(html.count('value="no"'), 2)
            self.assertEqual(html.count('value="uncertain"'), 2)
            self.assertEqual(html.count('data-candidate="GRP-'), 2)
            self.assertIn("pre-fire, post-fire, extended optical, dNBR, MTBS, and RAVG", html)
            self.assertIn("Do not overwrite, rename, or edit it", html)
            self.assertIn("querySelectorAll('input[type=radio]').forEach(input=>input.checked=false)", html)
            self.assertNotIn("http://", html)
            self.assertNotIn("https://", html)
            controller = html.rsplit("<script>", 1)[1].split("</script>", 1)[0]
            script = Path(temporary) / "controller.js"
            script.write_text(controller, encoding="utf-8", newline="\n")
            checked = subprocess.run(["node", "--check", str(script)], capture_output=True, text=True)
            self.assertEqual(checked.returncode, 0, checked.stderr)


@unittest.skipUnless(PUBLIC.exists(), "tracked Green Ridge owner review surface not published yet")
class TrackedGreenRidgeOwnerReviewSurfaceTests(unittest.TestCase):
    def test_public_outputs_match_bindings_and_remain_blank(self) -> None:
        report = json.loads(PUBLIC.read_text(encoding="utf-8"))
        self.assertEqual(report["summary"]["owner_responses"], 0)
        self.assertEqual(report["summary"]["labels_created"], 0)
        for output in report["outputs"]:
            payload = (PUBLIC.parent / output["path"]).read_bytes()
            self.assertEqual(len(payload), output["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), output["sha256"])


if __name__ == "__main__":
    unittest.main()
