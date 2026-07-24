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
        self.assertEqual(burnlens.__version__, "0.49.0")
        self.assertEqual(self.report["software_version"], "0.48.0")
        self.assertEqual(len(self.report["bound_inputs"]), len(BOUND_INPUTS))

    def test_report_preserves_claim_and_data_boundaries(self) -> None:
        self.assertEqual(self.report["metrics"]["event_groups"], 6)
        self.assertEqual(self.report["metrics"]["prototype_regions"], 12)
        self.assertEqual(
            self.report["metrics"]["prototype_regions_by_class"],
            {"background": 6, "burned": 6},
        )
        for key in (
            "dataset_version",
            "split_version",
            "baseline_version",
            "model_version",
        ):
            self.assertIsNone(self.report[key])
        limitations = " ".join(self.report["limitations"]).lower()
        for phrase in ("not independent ground truth", "no dataset", "not official"):
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
