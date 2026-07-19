from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

import burnlens
from burnlens.region_owner_review_surface import (
    RESPONSE_SCHEMA_VERSION,
    SURFACE_ID,
    _response_template,
    build_surface,
    write_surface,
)


ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "samples" / "labels" / "review" / "regions" / "phase-two" / f"{SURFACE_ID}.json"


class RegionOwnerReviewSurfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report, cls.pilot_png = build_surface(
            ROOT,
            "2026-07-18T16:00:00Z",
            "BL-TEST-REGION-OWNER-REVIEW-SURFACE",
            "a" * 40,
        )

    def test_version_identity_and_no_promotion_state(self) -> None:
        self.assertEqual(burnlens.__version__, "0.31.0")
        self.assertEqual(self.report["report_id"], SURFACE_ID)
        self.assertEqual(self.report["summary"]["candidate_count"], 6)
        self.assertEqual(self.report["summary"]["owner_region_responses"], 0)
        self.assertEqual(self.report["summary"]["owner_approved_region_labels"], 0)
        self.assertFalse(any(self.report["claim_boundaries"].values()))

    def test_exact_candidates_and_rasters_are_bound(self) -> None:
        candidates = self.report["candidates"]
        self.assertEqual([item["candidate_id"] for item in candidates], [f"RCP-{index:03d}" for index in range(1, 7)])
        self.assertEqual({item["proposed_class"] for item in candidates}, {"background", "burned"})
        self.assertEqual(sum(item["core_pixels"] for item in candidates), 136)
        self.assertEqual(sum(item["unknown_ring_pixels"] for item in candidates), 246)
        self.assertTrue(all(item["raster_contract"]["crs"] == "EPSG:32610" for item in candidates))
        self.assertTrue(all(item["owner_decision"] is None for item in candidates))

    def test_blank_template_has_exact_candidate_bindings(self) -> None:
        template = _response_template(self.report)
        self.assertEqual(template["response_schema_version"], RESPONSE_SCHEMA_VERSION)
        self.assertFalse(template["completed"])
        self.assertFalse(template["owner"]["attestation"])
        self.assertEqual(len(template["responses"]), 6)
        self.assertTrue(all(item["decision"] is None for item in template["responses"]))
        self.assertEqual(
            [item["candidate_raster_sha256"] for item in template["responses"]],
            [item["candidate_raster_sha256"] for item in self.report["candidates"]],
        )

    def test_rendered_surface_is_local_interactive_and_syntax_valid(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "surface"
            bindings = write_surface(json.loads(json.dumps(self.report)), self.pilot_png, output)
            self.assertEqual(len(bindings), 10)
            html = (output / f"{SURFACE_ID}.html").read_text(encoding="utf-8")
            self.assertEqual(html.count('value="yes"'), 6)
            self.assertEqual(html.count('value="no"'), 6)
            self.assertEqual(html.count('value="uncertain"'), 6)
            self.assertEqual(html.count('data-candidate="RCP-'), 6)
            self.assertNotIn("http://", html)
            self.assertNotIn("https://", html)
            self.assertIn("#save-draft,#load-response,#review-complete,#export-complete", html)
            controller = html.rsplit("<script>", 1)[1].split("</script>", 1)[0]
            script = Path(temporary) / "controller.js"
            script.write_text(controller, encoding="utf-8", newline="\n")
            subprocess.run(["node", "--check", str(script)], check=True, capture_output=True, text=True)
            template = json.loads((output / f"{SURFACE_ID}-RESPONSE-TEMPLATE.json").read_text(encoding="utf-8"))
            self.assertEqual(template, _response_template(self.report))


@unittest.skipUnless(PUBLIC.exists(), "tracked region owner review surface not published yet")
class TrackedRegionOwnerReviewSurfaceTests(unittest.TestCase):
    def test_public_outputs_match_bindings_and_remain_response_free(self) -> None:
        report = json.loads(PUBLIC.read_text(encoding="utf-8"))
        self.assertEqual(report["summary"]["owner_region_responses"], 0)
        self.assertFalse(any(report["claim_boundaries"].values()))
        for output in report["outputs"]:
            payload = (PUBLIC.parent / output["path"]).read_bytes()
            self.assertEqual(len(payload), output["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), output["sha256"])


if __name__ == "__main__":
    unittest.main()
