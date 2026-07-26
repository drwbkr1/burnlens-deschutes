from __future__ import annotations

import json
from pathlib import Path
import re
from tempfile import TemporaryDirectory
import unittest

import burnlens
from burnlens.portfolio_reviewer_experience import (
    BOUND_INPUTS,
    PortfolioReviewerExperienceError,
    REPORT_ID,
    build_report,
    write_outputs_no_overwrite,
)


ROOT = Path(__file__).resolve().parents[1]


class PortfolioReviewerExperienceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.report = build_report(
            repository_root=ROOT,
            generated_at_utc="2026-07-24T03:00:00Z",
            run_id="BL-TEST-PORTFOLIO-REVIEWER-EXPERIENCE",
            git_source_commit="a" * 40,
        )

    def test_version_and_exact_inputs(self) -> None:
        self.assertEqual(burnlens.__version__, "0.53.0")
        self.assertEqual(self.report["software_version"], "0.53.0")
        self.assertEqual(
            self.report["checkpoint_status"],
            "candidate-pr-release-pending",
        )
        self.assertEqual(
            self.report["release_tag"],
            "v0.52.0-dataset-baseline-model-readiness",
        )
        self.assertEqual(
            self.report["release_commit"],
            "dfb11c8b823e224aceb76be74003464973e33c2d",
        )
        self.assertEqual(
            self.report["release_tag_object"],
            "7041ef76ff4aac17f3bc2f8ba07b427dc858d2bf",
        )
        self.assertEqual(len(self.report["bound_inputs"]), len(BOUND_INPUTS))

    def test_report_preserves_claim_and_data_boundaries(self) -> None:
        self.assertEqual(self.report["metrics"]["event_groups"], 6)
        self.assertEqual(self.report["metrics"]["prototype_regions"], 12)
        self.assertEqual(
            self.report["metrics"]["prototype_regions_by_class"],
            {"background": 6, "burned": 6},
        )
        self.assertEqual(self.report["metrics"]["accepted_core_pixels"], 287)
        self.assertEqual(self.report["metrics"]["excluded_unknown_ring_pixels"], 531)
        self.assertEqual(
            self.report["metrics"]["patches_by_role"],
            {"test": 4, "train": 4, "validation": 4},
        )
        self.assertEqual(self.report["metrics"]["readiness_gates_passed"], 9)
        self.assertEqual(
            self.report["metrics"]["baseline_test_event_class_macro_dice"],
            1.0,
        )
        self.assertNotIn("Darlene", self.report["accepted_events"])
        self.assertIn("Ward Creek", self.report["accepted_events"])
        self.assertEqual(
            self.report["dataset_version"], "burnlens-dataset-v0.1.0"
        )
        self.assertEqual(
            self.report["split_version"],
            "burnlens-whole-event-split-v0.1.0",
        )
        self.assertEqual(
            self.report["baseline_version"], "burnlens-baseline-v0.1.0"
        )
        self.assertEqual(
            self.report["model_version"],
            "burnlens-unet-binary-v0.1.0",
        )
        self.assertEqual(
            self.report["model_status"],
            "valid-trained-evaluated-rejected-model",
        )
        self.assertEqual(
            self.report["model_package_version"],
            "burnlens-unet-rejected-package-v0.1.1",
        )
        self.assertEqual(
            self.report["metrics"]["model_test_event_class_macro_dice"],
            0.29874213836477986,
        )
        self.assertEqual(self.report["metrics"]["model_test_open_count"], 1)
        self.assertEqual(
            self.report["retained_failure"]["preview_path"],
            (
                "samples/cross-event/phase-two/petes-lake/"
                "PETES-LAKE-SOURCE-FITNESS-2026-001.png"
            ),
        )
        self.assertEqual(
            self.report["retained_failure"]["detail_path"],
            (
                "docs/phase-two/objective-four/"
                "PETES_LAKE_MATERIAL_DEFER_DECISION.md"
            ),
        )
        self.assertEqual(
            self.report["strongest_result"]["baseline_detail_path"],
            (
                "samples/baselines/burnlens-baseline-v0.1.0/"
                "BASELINE-EVALUATION-2026-001.html"
            ),
        )
        limitations = " ".join(self.report["limitations"]).lower()
        for phrase in (
            "not independent ground truth",
            "twelve 64 by 64",
            "may favor the measured spectral separability",
            "valid trained and evaluated",
            "no georeferenced model inference",
            "not official",
        ):
            self.assertIn(phrase, limitations)

    def test_outputs_are_deterministic_semantic_private_safe_and_no_overwrite(self) -> None:
        with TemporaryDirectory(dir=ROOT / "downloads") as first_dir:
            first = Path(first_dir)
            first_outputs = write_outputs_no_overwrite(
                report=self.report,
                output_directory=first,
            )
            html = (first / f"{REPORT_ID}.html").read_text(encoding="utf-8")
            payload = json.loads((first / f"{REPORT_ID}.json").read_text(encoding="utf-8"))
            self.assertEqual([item["path"] for item in first_outputs], [
                f"{REPORT_ID}.json",
                f"{REPORT_ID}.html",
            ])
            self.assertIn('id="result"', html)
            self.assertIn('id="failure"', html)
            self.assertIn('id="trace"', html)
            self.assertIn('class="skip"', html)
            self.assertIn('<link rel="icon" href="data:,">', html)
            self.assertIn("@media(max-width:430px)", html)
            self.assertIn("@media(prefers-reduced-motion:reduce)", html)
            self.assertIn(
                "One complete model experiment, with an honest rejection.",
                html,
            )
            self.assertIn("U-Net 0.299", html)
            self.assertIn("Valid rejected model", html)
            for image_target in re.findall(r'<img src="([^"]+)"', html):
                self.assertTrue(image_target.endswith(".png"), image_target)
            self.assertEqual(payload["outputs"][0]["path"], f"{REPORT_ID}.html")
            serialized = (html + json.dumps(payload)).lower()
            for forbidden in (
                "c:\\users",
                "downloads/phase-two/review-responses",
                "recipient",
                "retrieval url",
                "signed url",
            ):
                self.assertNotIn(forbidden, serialized)
            with self.assertRaisesRegex(
                PortfolioReviewerExperienceError, "refusing to overwrite"
            ):
                write_outputs_no_overwrite(report=self.report, output_directory=first)

            with TemporaryDirectory(dir=ROOT / "downloads") as second_dir:
                second = Path(second_dir)
                second_outputs = write_outputs_no_overwrite(
                    report=self.report,
                    output_directory=second,
                )
                self.assertEqual(first_outputs, second_outputs)
                for suffix in ("json", "html"):
                    self.assertEqual(
                        (first / f"{REPORT_ID}.{suffix}").read_bytes(),
                        (second / f"{REPORT_ID}.{suffix}").read_bytes(),
                    )

    def test_every_local_link_resolves_from_tracked_output_location(self) -> None:
        html = (
            __import__(
                "burnlens.portfolio_reviewer_experience",
                fromlist=["render_html"],
            )
            .render_html(self.report)
        )
        output_directory = ROOT / "portfolio"
        links = re.findall(r'(?:href|src)="([^"]+)"', html)
        self.assertGreaterEqual(len(links), 16)
        for target in links:
            if target.startswith(("#", "data:", "http://", "https://")):
                continue
            if target == f"{REPORT_ID}.json":
                continue
            self.assertTrue((output_directory / target).resolve().exists(), target)
