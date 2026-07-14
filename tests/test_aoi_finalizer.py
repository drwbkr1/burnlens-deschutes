from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from PIL import Image

from burnlens.aoi_finalizer import (
    AOI_VERSION,
    SOURCE_SHA256,
    build_aoi_evidence,
    file_sha256,
    load_and_validate_source,
    utm10n_to_wgs84,
    wgs84_to_utm10n,
    write_outputs,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "samples/reference/phase-two/NIFC-DARLENE3-PERIMETER-2026-001.geojson"


def evidence() -> tuple[dict, list]:
    return build_aoi_evidence(
        SOURCE,
        generated_at_utc="2026-07-14T01:30:00Z",
        run_id="BL-2026-07-14-aoi-final-r001",
        source_commit="a" * 40,
    )


class AoiFinalizerTests(unittest.TestCase):
    def test_exact_source_identity_and_checksum(self) -> None:
        collection, feature = load_and_validate_source(SOURCE)
        self.assertEqual(file_sha256(SOURCE), SOURCE_SHA256)
        self.assertEqual(collection["type"], "FeatureCollection")
        self.assertEqual(feature["properties"]["attr_UniqueFireIdentifier"], "2024-ORPRD-000289")
        self.assertEqual(feature["properties"]["poly_FeatureCategory"], "Wildfire Final Fire Perimeter")
        self.assertEqual(feature["geometry"]["type"], "MultiPolygon")

    def test_tampered_source_fails_closed(self) -> None:
        with TemporaryDirectory() as directory:
            changed = Path(directory) / "changed.geojson"
            changed.write_bytes(SOURCE.read_bytes() + b"\n")
            with self.assertRaisesRegex(ValueError, "SOURCE_CHECKSUM_MISMATCH"):
                load_and_validate_source(changed)

    def test_utm_round_trip_at_la_pine(self) -> None:
        original = (-121.4853152, 43.6868499)
        projected = wgs84_to_utm10n(*original)
        recovered = utm10n_to_wgs84(*projected)
        self.assertAlmostEqual(recovered[0], original[0], places=7)
        self.assertAlmostEqual(recovered[1], original[1], places=7)

    def test_projection_matches_independent_nifc_extent(self) -> None:
        report, _ = evidence()
        self.assertLessEqual(report["source"]["reference_extent_check_max_delta_m"], 0.0003)
        self.assertEqual(
            report["source"]["bbox_utm10n"],
            [622519.473, 4833503.355, 629489.216, 4837710.667],
        )

    def test_aoi_derivation_is_bounded_and_complete(self) -> None:
        report, _ = evidence()
        derivation = report["derivation"]
        self.assertEqual(report["aoi_version"], AOI_VERSION)
        self.assertEqual(derivation["aoi_bbox_utm10n"], [620000, 4831000, 632000, 4840000])
        self.assertEqual(derivation["width_m"], 12000)
        self.assertEqual(derivation["height_m"], 9000)
        self.assertEqual(derivation["area_km2"], 108.0)
        self.assertTrue(report["checks"]["aoi_contains_complete_reference_geometry"])
        self.assertTrue(report["checks"]["aoi_truthfully_supersedes_discovery_envelope"])
        self.assertTrue(report["checks"]["aoi_within_deschutes_county"])
        self.assertTrue(report["checks"]["selected_sentinel_metadata_footprint_contains_aoi"])
        self.assertTrue(report["checks"]["selected_viirs_pair_metadata_footprints_contain_aoi"])
        self.assertGreater(derivation["eastward_extension_beyond_discovery_m"], 2800)
        self.assertGreater(derivation["area_reduction_from_discovery_percent"], 48)

    def test_traceability_and_claim_boundaries_are_explicit(self) -> None:
        report, _ = evidence()
        self.assertEqual(report["source_commit"], "a" * 40)
        self.assertIsNone(report["dataset_version"])
        self.assertIsNone(report["label_schema_version"])
        self.assertIsNone(report["model_version"])
        prohibited = " ".join(report["claims"]["prohibited"])
        self.assertIn("BurnLens detection or label", prohibited)
        self.assertIn("operational product", prohibited)

    def test_outputs_are_semantic_and_render_at_expected_size(self) -> None:
        report, polygons = evidence()
        with TemporaryDirectory() as directory:
            root = Path(directory)
            json_path = root / "report.json"
            html_path = root / "report.html"
            png_path = root / "report.png"
            write_outputs(
                report,
                polygons,
                json_path=json_path,
                html_path=html_path,
                png_path=png_path,
            )
            parsed = json.loads(json_path.read_text(encoding="utf-8"))
            html = html_path.read_text(encoding="utf-8")
            self.assertEqual(parsed["decision"], "ACCEPT_FINAL_MODELING_AOI")
            self.assertIn('role="img"', html)
            self.assertIn("No imagery, label, detection", html)
            self.assertIn("NIFC final-perimeter reference", html)
            with Image.open(png_path) as image:
                self.assertEqual(image.size, (1600, 1200))
                self.assertEqual(image.mode, "RGB")

    def test_outputs_are_byte_deterministic(self) -> None:
        report, polygons = evidence()
        with TemporaryDirectory() as directory:
            root = Path(directory)
            hashes = []
            for index in (1, 2):
                output = root / str(index)
                write_outputs(
                    report,
                    polygons,
                    json_path=output / "report.json",
                    html_path=output / "report.html",
                    png_path=output / "report.png",
                )
                hashes.append(
                    tuple(file_sha256(output / name) for name in ("report.json", "report.html", "report.png"))
                )
            self.assertEqual(hashes[0], hashes[1])


if __name__ == "__main__":
    unittest.main()
