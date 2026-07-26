from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from burnlens.phase_four_interface import (
    OUTPUT_HTML,
    OUTPUT_JSON,
    PhaseFourInterfaceError,
    build_interface,
    run_interface,
)


ROOT = Path(__file__).resolve().parents[1]
RUN_ID = "BL-2026-07-26-p4o1-t01-u06-interface-r999"
COMMIT = "f" * 40


class PhaseFourInterfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.first = build_interface(
            repository_root=ROOT,
            generated_at_utc="2026-07-26T19:45:00Z",
            run_id=RUN_ID,
            git_source_commit=COMMIT,
        )

    def test_exact_route_lineage_and_measurements(self) -> None:
        report = self.first["report"]
        self.assertEqual(
            report["route"],
            "baseline-primary-with-rejected-model-diagnostic",
        )
        self.assertEqual(
            report["measurements"]["WCP-001"][
                "accepted_rbr_inside_mtbs_pct"
            ],
            94.19,
        )
        self.assertEqual(
            report["measurements"]["WCP-002"][
                "accepted_rbr_inside_mtbs_pct"
            ],
            0.0,
        )
        self.assertEqual(
            report["lineage"]["Rejected diagnostic model"],
            "burnlens-unet-binary-v0.1.0",
        )
        self.assertFalse(report["boundaries"]["model_accepted"])
        self.assertFalse(report["boundaries"]["model_outperformed_rbr"])
        self.assertFalse(report["boundaries"]["second_experiment_planned"])

    def test_interface_is_self_contained_accessible_and_interactive(self) -> None:
        html = self.first["outputs"][OUTPUT_HTML].decode("utf-8")
        for token in (
            'id="evidence-map"',
            'data-toggle="accepted-rbr"',
            'data-toggle="rejected-unet"',
            'data-opacity="mtbs"',
            'aria-labelledby="map-title map-desc"',
            'id="text-equivalent"',
            'class="skip"',
            "@media(max-width:620px)",
            "@media(prefers-reduced-motion:reduce)",
            "WCP-002 - visible baseline failure evidence",
            "No Phase 3B or follow-on experiment exists",
        ):
            self.assertIn(token, html)
        lower = html.lower()
        self.assertNotIn('src="http', lower)
        self.assertNotIn('href="http', lower)
        self.assertNotIn("fetch(", lower)
        self.assertNotIn("xmlhttprequest", lower)
        self.assertIn("connect-src 'none'", lower)
        self.assertGreater(
            self.first["report"]["map"][
                "rejected_unet_diagnostic_features"
            ],
            0,
        )

    def test_all_six_run_states_are_visible_and_honest(self) -> None:
        states = self.first["report"]["run_state_taxonomy"]
        self.assertEqual(
            [item["name"] for item in states],
            [
                "Accepted",
                "Degraded",
                "No detection",
                "Fallback",
                "Failed",
                "Withheld",
            ],
        )
        self.assertEqual(states[0]["status"], "active")
        self.assertEqual(states[4]["status"], "retained")
        self.assertIn("Not active", states[3]["current"])

    def test_determinism_and_bad_run_id(self) -> None:
        second = build_interface(
            repository_root=ROOT,
            generated_at_utc="2026-07-26T19:45:00Z",
            run_id=RUN_ID,
            git_source_commit=COMMIT,
        )
        self.assertEqual(self.first["outputs"], second["outputs"])
        with self.assertRaisesRegex(PhaseFourInterfaceError, "run ID"):
            build_interface(
                repository_root=ROOT,
                generated_at_utc="2026-07-26T19:45:00Z",
                run_id="bad-run",
                git_source_commit=COMMIT,
            )

    def test_no_overwrite_gate(self) -> None:
        with TemporaryDirectory(dir=ROOT / "downloads") as parent:
            output = Path(parent) / "interface"
            output.mkdir()
            (output / "occupied.txt").write_text("retained", encoding="utf-8")
            with self.assertRaisesRegex(
                PhaseFourInterfaceError, "refusing to overwrite"
            ):
                run_interface(
                    repository_root=ROOT,
                    output_directory=output,
                    generated_at_utc="2026-07-26T19:45:00Z",
                    run_id=RUN_ID,
                    git_source_commit=COMMIT,
                )
            self.assertEqual((output / "occupied.txt").read_text(), "retained")
            self.assertFalse((output / OUTPUT_HTML).exists())
            self.assertFalse((output / OUTPUT_JSON).exists())


if __name__ == "__main__":
    unittest.main()
