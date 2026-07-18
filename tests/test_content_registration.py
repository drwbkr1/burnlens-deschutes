from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
import zipfile

import numpy as np
from PIL import Image

import burnlens
from burnlens.content_registration import (
    SOFTWARE_VERSION as CONTENT_REGISTRATION_SOFTWARE_VERSION,
    ContentRegistrationError,
    _geometric_quality_metadata,
    _validate_visual_decision,
    estimate_subpixel_shift,
    measure_registration_windows,
    render_html,
    render_png,
)


def _fourier_shift(values: np.ndarray, shift: tuple[float, float]) -> np.ndarray:
    row_frequency = np.fft.fftfreq(values.shape[0])[:, None]
    column_frequency = np.fft.fftfreq(values.shape[1])[None, :]
    phase = np.exp(-2j * np.pi * (row_frequency * shift[0] + column_frequency * shift[1]))
    return np.fft.ifftn(np.fft.fftn(values) * phase).real


class ContentRegistrationTests(unittest.TestCase):
    def test_registration_artifacts_have_explicit_lf_checkout_contract(self) -> None:
        root = Path(__file__).resolve().parents[1]
        attributes = (root / ".gitattributes").read_text(encoding="utf-8").splitlines()
        self.assertIn("samples/registration/phase-two/*.json text eol=lf", attributes)
        self.assertIn("samples/registration/phase-two/*.html text eol=lf", attributes)

    def test_current_import_version_preserves_historical_registration_version(self) -> None:
        self.assertEqual(burnlens.__version__, "0.29.0")
        self.assertEqual(CONTENT_REGISTRATION_SOFTWARE_VERSION, "0.8.0")

    def test_localized_dft_recovers_subpixel_shift_to_apply(self) -> None:
        reference = np.random.default_rng(7).normal(size=(96, 96))
        for injected in ((0.30, -0.40), (-0.17, 0.22), (1.25, -2.10), (0.0, 0.0)):
            measured = estimate_subpixel_shift(reference, _fourier_shift(reference, injected))
            self.assertAlmostEqual(measured["row_shift_to_apply_px"], -injected[0], delta=0.02)
            self.assertAlmostEqual(measured["column_shift_to_apply_px"], -injected[1], delta=0.02)
            self.assertEqual(measured["sample_resolution_px"], 0.01)

    def test_textureless_signal_fails_closed(self) -> None:
        values = np.ones((64, 64), dtype=np.float64)
        with self.assertRaisesRegex(ContentRegistrationError, "insufficient texture"):
            estimate_subpixel_shift(values, values)

    def test_window_gate_covers_aoi_once_and_never_assigns_a_label(self) -> None:
        signals = {band: np.zeros((450, 600), dtype=np.float64) for band in ("B04", "B8A", "B12")}
        pair_state = np.zeros((450, 600), dtype=np.uint8)
        pair_state[:150, :150] = 2
        measurement = {
            "row_shift_to_apply_px": 0.02,
            "column_shift_to_apply_px": -0.01,
            "magnitude_px": 0.0224,
            "coarse_peak_ratio": 8.0,
            "sample_resolution_px": 0.01,
            "reference_energy": 1.0,
            "moving_energy": 1.0,
        }
        with patch("burnlens.content_registration.estimate_subpixel_shift", return_value=measurement):
            windows = measure_registration_windows(
                signals,
                signals,
                pair_state,
                [620000.0, 4831000.0, 632000.0, 4840000.0],
            )
        self.assertEqual(len(windows), 12)
        self.assertEqual(windows[0]["state"], "excluded")
        self.assertEqual(windows[1]["state"], "pass")
        self.assertEqual(windows[0]["bounds_utm10n"], [620000.0, 4837000.0, 623000.0, 4840000.0])
        self.assertIn("never assigns burned or background", windows[1]["label_effect"])
        covered = sum(item["pixel_window"]["height"] * item["pixel_window"]["width"] for item in windows)
        self.assertEqual(covered, 450 * 600)

    def test_packaged_product_qc_is_preserved_as_context_not_pair_proof(self) -> None:
        document = """<root><report globalStatus="PASSED" date="2024-07-06T02:50:27Z"><checkList>
        <check><inspection id="Geometric_Refining_Vnir_Swir_Registration" status="PASSED" processingStatus="done" />
        <message>VNIR / SWIR bands have not been registered.</message></check>
        <check><inspection id="Geometric_Refining_Spatio_Residual_Histograms" status="PASSED" processingStatus="done" />
        <message>Geometric Spatio Residual Histograms not computed.</message><extraValues><value name="EXPECTED">none</value></extraValues></check>
        </checkList></report></root>"""
        with TemporaryDirectory() as directory:
            path = Path(directory) / "scene.zip"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("S2A.SAFE/DATASTRIP/DS/QI_DATA/GEOMETRIC_QUALITY.xml", document)
            metadata = _geometric_quality_metadata(path)
        self.assertEqual(metadata["report_global_status"], "PASSED")
        self.assertIn(
            "have not been registered",
            metadata["inspections"]["Geometric_Refining_Vnir_Swir_Registration"]["message"],
        )
        self.assertEqual(
            metadata["inspections"]["Geometric_Refining_Spatio_Residual_Histograms"]["values"],
            {"EXPECTED": "none"},
        )
        self.assertIn("does not prove pair-local", metadata["interpretation"])

    def test_visual_decision_cannot_overrule_failed_machine_gate(self) -> None:
        with self.assertRaisesRegex(ContentRegistrationError, "incompatible"):
            _validate_visual_decision(
                "REJECT_REGISTRATION_REMEDIATE",
                "ACCEPT_LOCAL_CONTENT_REGISTRATION",
                "reviewed",
            )

    def test_registration_render_is_deterministic_and_semantic(self) -> None:
        report = self._minimal_report()
        rgb = np.zeros((3, 900, 1200), dtype=np.uint8)
        with TemporaryDirectory() as directory:
            root = Path(directory)
            first = root / "first.png"
            second = root / "second.png"
            html = root / "report.html"
            render_png(report, rgb, rgb, first)
            render_png(report, rgb, rgb, second)
            render_html(report, first.name, html)
            with Image.open(first) as image:
                self.assertEqual(image.size, (1800, 1250))
            self.assertEqual(first.read_bytes(), second.read_bytes())
            text = html.read_text(encoding="utf-8")
            self.assertIn("Window evidence", text)
            self.assertIn("Product QC caveat", text)
            self.assertIn("0 labels", text)
            self.assertNotIn(b"\r\n", html.read_bytes())

    @staticmethod
    def _minimal_report() -> dict:
        windows = []
        for row in range(1, 4):
            for column in range(1, 5):
                windows.append(
                    {
                        "window_id": f"W-R{row:02d}-C{column:02d}",
                        "grid_row": row,
                        "grid_column": column,
                        "state": "pass",
                        "reason_code": "CONTENT_REGISTRATION_PASS",
                        "pair_quality": {"eligible_fraction": 0.99},
                        "consensus": {
                            "row_shift_to_apply_px": -0.02,
                            "column_shift_to_apply_px": -0.01,
                            "magnitude_px": 0.0224,
                        },
                    }
                )
        return {
            "decision": "PENDING_VISUAL_REVIEW",
            "decision_detail": "Rendered review remains pending.",
            "summary": {
                "machine_decision": "PASS_LOCAL_CONTENT_REGISTRATION_GATE",
                "state_counts": {"pass": 12, "review-needed": 0, "excluded": 0, "fail-registration": 0},
                "p50_px": 0.0224,
                "p95_px": 0.0224,
                "max_px": 0.0224,
                "max_m": 0.448,
            },
            "method": {
                "signals": "Independent spectral gradients.",
                "estimator": "Localized upsampled DFT.",
                "upsample_factor": 100,
                "window_grid": "4 by 3 windows.",
                "shared_mask_rationale": "No shared mask.",
                "selection_boundaries": "No labels steer the estimate.",
            },
            "windows": windows,
            "run_id": "BL-TEST-REGISTRATION",
            "git_source_commit": "a" * 40,
            "software_version": "0.8.0",
            "report_version": "content-registration-evidence-v0.1.0",
            "registration_protocol_version": "local-content-registration-v0.1.0",
            "aoi_version": "aoi-darlene3-model-v0.2.0",
            "target_version": "target-burn-scar-v0.2.0",
            "label_schema_version": "burn-scar-label-protocol-v0.1.0",
            "package_id": "darlene3-s2-optical-pair-v0.1.0",
            "package_contract_version": "optical-pair-intake-contract-v0.1.0",
        }


if __name__ == "__main__":
    unittest.main()
