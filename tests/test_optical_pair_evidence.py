from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import warnings
import zipfile

import numpy as np
from PIL import Image
from rasterio import Affine

from burnlens.optical_pair_evidence import (
    LABEL_PROTOCOL_VERSION,
    OpticalPairEvidenceError,
    _dnbr_rgb,
    _integer_window,
    _label_protocol,
    _product_metadata,
    _sha256_lf_text,
    classify_pair_quality,
    render_html,
    render_png,
    summarize_scl,
)


class OpticalPairEvidenceTests(unittest.TestCase):
    def test_aoi_window_requires_exact_native_grid_alignment(self) -> None:
        transform = Affine(20, 0, 500_000, 0, -20, 4_900_000)
        window = _integer_window([500_000, 4_899_980, 500_020, 4_900_000], transform)
        self.assertEqual((window.col_off, window.row_off, window.width, window.height), (0, 0, 1, 1))
        with self.assertRaisesRegex(OpticalPairEvidenceError, "does not align"):
            _integer_window([500_000, 4_899_980, 500_019, 4_900_000], transform)

    def test_safe_metadata_maps_b04_filename_to_b4_physical_band(self) -> None:
        safe_name = "S2A_TEST.SAFE"
        product = """<root>
        <PRODUCT_URI>S2A_TEST.SAFE</PRODUCT_URI><PROCESSING_BASELINE>05.10</PROCESSING_BASELINE>
        <PRODUCT_START_TIME>2024-06-25T18:59:41.024Z</PRODUCT_START_TIME>
        <GENERATION_TIME>2024-06-26T01:23:49.000Z</GENERATION_TIME>
        <Spectral_Information bandId="3" physicalBand="B4" />
        <Spectral_Information bandId="8" physicalBand="B8A" />
        <Spectral_Information bandId="12" physicalBand="B12" />
        <BOA_ADD_OFFSET band_id="3">-1000</BOA_ADD_OFFSET>
        <BOA_ADD_OFFSET band_id="8">-1000</BOA_ADD_OFFSET>
        <BOA_ADD_OFFSET band_id="12">-1000</BOA_ADD_OFFSET>
        <BOA_QUANTIFICATION_VALUE>10000</BOA_QUANTIFICATION_VALUE>
        <SPECIAL_VALUE_TEXT>NODATA</SPECIAL_VALUE_TEXT><SPECIAL_VALUE_INDEX>0</SPECIAL_VALUE_INDEX>
        <SPECIAL_VALUE_TEXT>SATURATED</SPECIAL_VALUE_TEXT><SPECIAL_VALUE_INDEX>65535</SPECIAL_VALUE_INDEX>
        </root>"""
        tile = """<root><TILE_ID>S2A_OPER_MSI_L2A_TL_TEST</TILE_ID>
        <SENSING_TIME>2024-06-25T18:59:41.024Z</SENSING_TIME>
        <HORIZONTAL_CS_CODE>EPSG:32610</HORIZONTAL_CS_CODE></root>"""
        with TemporaryDirectory() as directory:
            path = Path(directory) / "safe.zip"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr(f"{safe_name}/MTD_MSIL2A.xml", product)
                archive.writestr(f"{safe_name}/GRANULE/T/MTD_TL.xml", tile)
            with zipfile.ZipFile(path) as archive:
                metadata = _product_metadata(archive, archive.namelist(), safe_name)
        self.assertEqual(metadata["boa_offsets"], {"B04": -1000.0, "B8A": -1000.0, "B12": -1000.0})

    def test_scl_summary_preserves_eligible_review_and_excluded_states(self) -> None:
        values = np.array([[4, 5, 7], [0, 3, 11]], dtype=np.uint8)
        summary = summarize_scl(values)
        self.assertEqual(summary["pixel_count"], 6)
        self.assertEqual(summary["eligible_land_pixels"], 2)
        self.assertEqual(summary["review_needed_pixels"], 1)
        self.assertEqual(summary["excluded_pixels"], 3)

    def test_unknown_scl_class_fails_closed(self) -> None:
        with self.assertRaisesRegex(OpticalPairEvidenceError, "unknown class"):
            summarize_scl(np.array([[12]], dtype=np.uint8))

    def test_pair_quality_never_coerces_review_or_excluded_to_eligible(self) -> None:
        pre = np.array([[4, 7, 4], [5, 5, 11]], dtype=np.uint8)
        post = np.array([[5, 4, 8], [4, 7, 5]], dtype=np.uint8)
        state, summary = classify_pair_quality(pre, post)
        np.testing.assert_array_equal(
            state,
            np.array([[0, 1, 2], [0, 1, 2]], dtype=np.uint8),
        )
        counts = {item["state"]: item["pixels"] for item in summary["states"]}
        self.assertEqual(counts, {"eligible-comparison": 2, "review-needed": 2, "excluded": 2})

    def test_label_protocol_has_binary_target_and_three_ignored_states(self) -> None:
        protocol = _label_protocol()
        self.assertEqual(protocol["version"], LABEL_PROTOCOL_VERSION)
        self.assertFalse(protocol["implemented"])
        targets = {item["state"]: item["target_value"] for item in protocol["states"]}
        self.assertEqual(targets["burned"], 1)
        self.assertEqual(targets["background-candidate"], 0)
        self.assertIsNone(targets["unknown"])
        self.assertIsNone(targets["excluded"])
        self.assertIsNone(targets["review-needed"])

    def test_dnbr_color_render_is_deterministic_and_nan_safe(self) -> None:
        dnbr = np.array([[np.nan, -0.5, 0.1], [0.8, 0.3, -0.2]], dtype=np.float32)
        quality = np.array([[0, 0, 1], [2, 0, 0]], dtype=np.uint8)
        with warnings.catch_warnings():
            warnings.simplefilter("error", RuntimeWarning)
            first = _dnbr_rgb(dnbr, quality)
            second = _dnbr_rgb(dnbr, quality)
        np.testing.assert_array_equal(first, second)
        np.testing.assert_array_equal(first[0, 0], np.array([78, 84, 82], dtype=np.uint8))
        np.testing.assert_array_equal(first[1, 0], np.array([78, 84, 82], dtype=np.uint8))

    def test_structured_input_hash_is_stable_across_line_endings(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            lf = root / "lf.json"
            crlf = root / "crlf.json"
            lf.write_bytes(b'{\n  "value": 1\n}\n')
            crlf.write_bytes(b'{\r\n  "value": 1\r\n}\r\n')
            self.assertEqual(_sha256_lf_text(lf), _sha256_lf_text(crlf))

    def test_rendered_pending_state_is_not_mislabeled_as_accepted_or_rejected(self) -> None:
        report = self._minimal_report("PENDING_VISUAL_REVIEW")
        geometry = {
            "type": "Polygon",
            "coordinates": [[[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]]],
        }
        tci = np.zeros((3, 3, 4), dtype=np.uint8)
        dnbr = np.zeros((3, 4), dtype=np.float32)
        quality = np.zeros((3, 4), dtype=np.uint8)
        with TemporaryDirectory() as directory:
            root = Path(directory)
            first = root / "first.png"
            second = root / "second.png"
            html_path = root / "report.html"
            render_png(report, tci, tci, dnbr, quality, geometry, first)
            render_png(report, tci, tci, dnbr, quality, geometry, second)
            render_html(report, first.name, html_path)
            with Image.open(first) as image:
                self.assertEqual(image.size, (1800, 1250))
            self.assertEqual(first.read_bytes(), second.read_bytes())
            html = html_path.read_text(encoding="utf-8")
            self.assertIn("visual review remains pending", html)
            self.assertNotIn("Pair accepted for protocol evidence", html)
            self.assertNotIn("Pair rejected after visual review", html)
            self.assertNotIn(b"\r\n", html_path.read_bytes())

    @staticmethod
    def _minimal_report(decision: str) -> dict:
        return {
            "decision": decision,
            "decision_detail": "Machine validation complete; visual review pending.",
            "aoi": {"bbox_utm10n": [0, 0, 10, 10]},
            "pair_quality": {
                "states": [
                    {"state": "eligible-comparison", "pixels": 12, "percent": 100.0},
                    {"state": "review-needed", "pixels": 0, "percent": 0.0},
                    {"state": "excluded", "pixels": 0, "percent": 0.0},
                ]
            },
            "label_protocol": _label_protocol(),
            "run_id": "BL-TEST-OPTICAL-PAIR",
            "git_source_commit": "a" * 40,
            "software_version": "0.7.0",
            "report_version": "optical-pair-protocol-evidence-v0.1.0",
            "aoi_version": "aoi-darlene3-model-v0.2.0",
            "target_version": "target-burn-scar-v0.2.0",
            "label_schema_version": LABEL_PROTOCOL_VERSION,
            "package_id": "darlene3-s2-optical-pair-v0.1.0",
            "package_contract_version": "sentinel2-pair-contract-v0.1.0",
            "terms_review_id": "TERMS-2026-004",
        }


if __name__ == "__main__":
    unittest.main()
