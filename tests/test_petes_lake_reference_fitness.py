from __future__ import annotations

from datetime import datetime, timedelta, timezone
import importlib.util
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch


GEO_RESEARCH_MODULES = ("geopandas", "pyogrio", "pyproj", "shapely")
MISSING_GEO_RESEARCH_MODULES = [
    module
    for module in GEO_RESEARCH_MODULES
    if importlib.util.find_spec(module) is None
]
if MISSING_GEO_RESEARCH_MODULES:
    raise unittest.SkipTest(
        "geo-research optional dependencies are not installed: "
        + ", ".join(MISSING_GEO_RESEARCH_MODULES)
    )

import numpy as np
import rasterio
from shapely.geometry import box

import burnlens.petes_lake_reference_fitness as reference_fitness
from burnlens.petes_lake_wetland_custody import PACKAGE_DIRECTORY

from burnlens.petes_lake_reference_fitness import (
    NWI_CONTRACT_PATH,
    REPORT_ID,
    VISUAL_PENDING,
    VISUAL_PASS,
    VISUAL_PASS_NOTE,
    _decision_outcome,
    _esri_rings_geometry,
    _full_pixel_source_coverage,
    _rasterize,
    _registration_masks,
    _render_headline,
    _sample_nearest,
    _source_project_summary,
    _validate_nwi_report_binding,
    build_report,
    write_outputs,
)


ROOT = Path(__file__).resolve().parents[1]
NWI_PACKAGE = ROOT / "downloads/phase-two/raw" / PACKAGE_DIRECTORY


class PetesLakeReferenceFitnessTests(unittest.TestCase):
    def test_nearest_sample_uses_pixel_centers_and_distinct_uncovered(self) -> None:
        values = np.array([[1, 2], [3, 0]], dtype=np.uint8)
        transform = rasterio.Affine(30, 0, 584_560, 0, -30, 4_871_520)
        sampled = _sample_nearest(values, transform, 0)
        self.assertEqual(sampled.shape, (259, 349))
        self.assertEqual(int(sampled[0, 0]), 1)
        self.assertEqual(int(sampled[1, 1]), 0 if values[1, 1] != 0 else 255)
        self.assertEqual(int(sampled[-1, -1]), 255)

    def test_registration_nonpass_wins_over_pass_overlap(self) -> None:
        boundary = np.ones((259, 349), dtype=bool)
        report = {
            "registration": {
                "windows": [
                    {
                        "pixel_window": {
                            "row_offset": 0,
                            "column_offset": 0,
                            "height": 10,
                            "width": 10,
                        },
                        "state": "pass",
                    },
                    {
                        "pixel_window": {
                            "row_offset": 5,
                            "column_offset": 5,
                            "height": 10,
                            "width": 10,
                        },
                        "state": "review-needed",
                    },
                ]
            }
        }
        strict, nonpass, unobserved = _registration_masks(report, boundary)
        self.assertTrue(strict[2, 2])
        self.assertFalse(strict[7, 7])
        self.assertTrue(nonpass[7, 7])
        self.assertTrue(unobserved[20, 20])

    def test_esri_polygon_rings_preserve_hole(self) -> None:
        outer_clockwise = [[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]]
        hole_counterclockwise = [[2, 2], [8, 2], [8, 8], [2, 8], [2, 2]]
        geometry = _esri_rings_geometry([outer_clockwise, hole_counterclockwise])
        self.assertAlmostEqual(geometry.area, 64.0)
        with self.assertRaisesRegex(RuntimeError, "closed"):
            _esri_rings_geometry([outer_clockwise[:-1]])

    def test_any_touch_exclusion_captures_edge_without_center(self) -> None:
        edge = box(584_560, 4_871_519, 584_561, 4_871_520)
        center = _rasterize([edge], all_touched=False)
        any_touch = _rasterize([edge], all_touched=True)
        self.assertEqual(int(center.sum()), 0)
        self.assertGreater(int(any_touch.sum()), 0)

    def test_source_project_gate_is_explicit_temporal_scale_and_private_comment_safe(self) -> None:
        base = {
            "OBJECTID": 1,
            "PROJECT_NAME": "Example project",
            "STATUS": "Complete",
            "SUPPMAPINFO": "https://example.invalid/metadata",
            "FGDC_METADATA": None,
            "DATA_SOURCE": "NAIP",
            "IMAGE_YR": 2022,
            "IMAGE_DATE": "",
            "IMAGE_SCALE": 24_000,
            "ALL_SCALES": "1:24,000",
            "EMULSION": "CIR",
            "COMMENTS": "do not copy this provider comment",
            "SOURCE_TYPE": "CIR",
        }
        fit_geometry = box(0, 0, 1, 1)
        summaries, fit, unfit = _source_project_summary(
            [{"attributes": base, "geometry": fit_geometry}]
        )
        self.assertEqual(fit, [fit_geometry])
        self.assertEqual(unfit, [])
        self.assertEqual(summaries[0]["pre_ignition_context_gate"], "pass")
        self.assertEqual(len(summaries[0]["project_binding_sha256"]), 64)
        self.assertTrue(summaries[0]["project_id"].startswith("nwi-source-project-"))
        forbidden = {
            "object_id",
            "project_name",
            "status",
            "data_source",
            "emulsion",
            "source_type",
            "all_scales",
            "parsed_all_scales",
            "comments",
            "comments_present",
            "comments_sha256",
            "supplemental_map_info_present",
            "supplemental_map_info_sha256",
            "fgdc_metadata_locator_present",
            "fgdc_metadata_locator_sha256",
            "geometry_area_square_meters",
        }
        self.assertTrue(forbidden.isdisjoint(summaries[0]))

        ambiguous_2023 = dict(base, IMAGE_YR=2023, IMAGE_DATE="2023")
        unfit_geometry = box(2, 2, 3, 3)
        summaries, fit, unfit = _source_project_summary(
            [{"attributes": ambiguous_2023, "geometry": unfit_geometry}]
        )
        self.assertEqual(fit, [])
        self.assertEqual(unfit, [unfit_geometry])
        self.assertIn(
            "2023_IMAGE_DATE_NOT_EXACT_PREIGNITION",
            summaries[0]["gate_reasons"],
        )
        self.assertIn(
            "IMAGE_DATE_PRESENT_BUT_INVALID",
            summaries[0]["gate_reasons"],
        )

        invalid_older_date = dict(base, IMAGE_DATE="2022-07-01 trailing")
        summaries, fit, unfit = _source_project_summary(
            [{"attributes": invalid_older_date, "geometry": unfit_geometry}]
        )
        self.assertEqual(fit, [])
        self.assertEqual(unfit, [unfit_geometry])
        self.assertIn(
            "IMAGE_DATE_PRESENT_BUT_INVALID",
            summaries[0]["gate_reasons"],
        )

        trailing_date = dict(base, IMAGE_YR=2023, IMAGE_DATE="2023-08-01 trailing")
        summaries, fit, unfit = _source_project_summary(
            [{"attributes": trailing_date, "geometry": unfit_geometry}]
        )
        self.assertEqual(fit, [])
        self.assertEqual(unfit, [unfit_geometry])
        self.assertIn(
            "2023_IMAGE_DATE_NOT_EXACT_PREIGNITION",
            summaries[0]["gate_reasons"],
        )

        placeholder_metadata = dict(base, SUPPMAPINFO=" UNKNOWN ", FGDC_METADATA=" ")
        summaries, fit, unfit = _source_project_summary(
            [{"attributes": placeholder_metadata, "geometry": unfit_geometry}]
        )
        self.assertEqual(fit, [])
        self.assertEqual(unfit, [unfit_geometry])
        self.assertIn("PROJECT_METADATA_LOCATOR_MISSING", summaries[0]["gate_reasons"])

        inexact_status = dict(base, STATUS="complete")
        summaries, fit, unfit = _source_project_summary(
            [{"attributes": inexact_status, "geometry": unfit_geometry}]
        )
        self.assertEqual(fit, [])
        self.assertEqual(unfit, [unfit_geometry])
        self.assertIn("STATUS_NOT_EXACT_COMPLETE", summaries[0]["gate_reasons"])

    def test_full_pixel_source_coverage_rejects_center_only_sliver(self) -> None:
        tiny_center = box(584_569.9, 4_871_509.9, 584_570.1, 4_871_510.1)
        center_hit = _rasterize([tiny_center])
        strict = _full_pixel_source_coverage([tiny_center])
        self.assertTrue(center_hit[0, 0])
        self.assertFalse(strict[0, 0])

        wide_coverage = box(584_540, 4_871_480, 584_600, 4_871_540)
        strict = _full_pixel_source_coverage([wide_coverage])
        self.assertTrue(strict[0, 0])
        unfit_edge = box(584_560, 4_871_519, 584_561, 4_871_520)
        unfit_any_touch = _rasterize([unfit_edge], all_touched=True)
        self.assertTrue(unfit_any_touch[0, 0])
        self.assertFalse((strict & ~unfit_any_touch)[0, 0])

    def test_nwi_custody_binding_requires_same_commit_and_forward_time(self) -> None:
        commit = "a" * 40
        custody = {
            "unit_id": reference_fitness.NWI_CUSTODY_UNIT_ID,
            "branch": reference_fitness.BRANCH,
            "git_source_commit": commit,
            "completed_at_utc": "2026-07-22T01:00:00Z",
        }
        _validate_nwi_report_binding(
            custody,
            git_source_commit=commit,
            generated_at_utc="2026-07-22T01:00:01Z",
        )
        with self.assertRaisesRegex(RuntimeError, "unit binding"):
            _validate_nwi_report_binding(
                dict(custody, unit_id="P2O4-T33-U05R1"),
                git_source_commit=commit,
                generated_at_utc="2026-07-22T01:00:01Z",
            )
        with self.assertRaisesRegex(RuntimeError, "source commit"):
            _validate_nwi_report_binding(
                custody,
                git_source_commit="b" * 40,
                generated_at_utc="2026-07-22T01:00:01Z",
            )
        with self.assertRaisesRegex(RuntimeError, "branch binding"):
            _validate_nwi_report_binding(
                dict(custody, branch="wrong-branch"),
                git_source_commit=commit,
                generated_at_utc="2026-07-22T01:00:01Z",
            )
        with self.assertRaisesRegex(RuntimeError, "must follow"):
            _validate_nwi_report_binding(
                custody,
                git_source_commit=commit,
                generated_at_utc="2026-07-22T01:00:00Z",
            )

    def test_machine_failure_precedes_pending_render(self) -> None:
        disposition, code, next_dependency = _decision_outcome(False, VISUAL_PENDING)
        self.assertEqual(disposition, "remediate")
        self.assertIn("SOURCE_OR_SURVIVING_EVIDENCE_GATE", code)
        self.assertEqual(next_dependency, reference_fitness.UNIT_ID)

    def test_visual_notes_are_fixed_privacy_safe_codes(self) -> None:
        reference_fitness._validate_visual(VISUAL_PENDING, "")
        reference_fitness._validate_visual(VISUAL_PASS, VISUAL_PASS_NOTE)
        with self.assertRaisesRegex(RuntimeError, "privacy-safe controlled"):
            reference_fitness._validate_visual(
                VISUAL_PASS, "provider project name copied here"
            )

    def test_render_headline_tracks_disposition_and_visual_gate(self) -> None:
        def report(disposition: str, machine: str) -> dict[str, object]:
            return {
                "fitness_decision": {
                    "disposition": disposition,
                    "machine_source_gate": machine,
                }
            }

        self.assertIn("review is pending", _render_headline(report("pending-render-review", "pass")))
        self.assertIn("passes", _render_headline(report("pass", "pass")))
        self.assertIn("remediation", _render_headline(report("remediate", "pass")))
        self.assertIn("remediation", _render_headline(report("pending-render-review", "fail")))

    def test_output_roster_is_no_overwrite(self) -> None:
        with TemporaryDirectory() as directory, patch(
            "burnlens.petes_lake_reference_fitness._render_png_bytes",
            return_value=b"png",
        ), patch(
            "burnlens.petes_lake_reference_fitness._render_html",
            return_value=b"html",
        ):
            output = write_outputs({"report_id": REPORT_ID}, {}, Path(directory))
            self.assertEqual(set(output), {"json", "png", "html"})
            with self.assertRaisesRegex(RuntimeError, "already exists"):
                write_outputs({"report_id": REPORT_ID}, {}, Path(directory))

    def test_output_transaction_rolls_back_partial_roster(self) -> None:
        with TemporaryDirectory() as directory, patch(
            "burnlens.petes_lake_reference_fitness._render_png_bytes",
            return_value=b"png",
        ), patch(
            "burnlens.petes_lake_reference_fitness._render_html",
            return_value=b"html",
        ):
            calls = {"count": 0}
            real_write = reference_fitness._write_no_overwrite

            def fail_second(path: Path, data: bytes) -> os.stat_result:
                calls["count"] += 1
                if calls["count"] == 2:
                    raise OSError("synthetic second-output failure")
                return real_write(path, data)

            with patch(
                "burnlens.petes_lake_reference_fitness._write_no_overwrite",
                side_effect=fail_second,
            ), self.assertRaisesRegex(RuntimeError, "rolled back"):
                write_outputs({"report_id": REPORT_ID}, {}, Path(directory))
            self.assertEqual(list(Path(directory).iterdir()), [])

    def test_output_transaction_retains_and_reports_corrupt_partial_as_unsafe(self) -> None:
        with TemporaryDirectory() as directory, patch(
            "burnlens.petes_lake_reference_fitness._render_png_bytes",
            return_value=b"png",
        ), patch(
            "burnlens.petes_lake_reference_fitness._render_html",
            return_value=b"html",
        ):
            calls = {"count": 0}
            real_write = reference_fitness._write_no_overwrite

            def corrupt_second(path: Path, data: bytes) -> os.stat_result:
                calls["count"] += 1
                if calls["count"] == 2:
                    path.write_bytes(b"synthetic-corrupt-partial")
                    raise OSError("synthetic post-create failure")
                return real_write(path, data)

            with patch(
                "burnlens.petes_lake_reference_fitness._write_no_overwrite",
                side_effect=corrupt_second,
            ), self.assertRaisesRegex(RuntimeError, "exact rollback was unsafe"):
                write_outputs({"report_id": REPORT_ID}, {}, Path(directory))
            remaining = list(Path(directory).iterdir())
            self.assertEqual([item.suffix for item in remaining], [".png"])
            self.assertEqual(remaining[0].read_bytes(), b"synthetic-corrupt-partial")

    def test_output_transaction_never_deletes_identical_peer_file(self) -> None:
        with TemporaryDirectory() as directory, patch(
            "burnlens.petes_lake_reference_fitness._render_png_bytes",
            return_value=b"png",
        ), patch(
            "burnlens.petes_lake_reference_fitness._render_html",
            return_value=b"html",
        ):
            calls = {"count": 0}
            real_write = reference_fitness._write_no_overwrite

            def peer_second(path: Path, data: bytes) -> os.stat_result:
                calls["count"] += 1
                if calls["count"] == 2:
                    path.write_bytes(data)
                    raise FileExistsError("synthetic identical peer won the race")
                return real_write(path, data)

            with patch(
                "burnlens.petes_lake_reference_fitness._write_no_overwrite",
                side_effect=peer_second,
            ), self.assertRaisesRegex(RuntimeError, "exact rollback was unsafe"):
                write_outputs({"report_id": REPORT_ID}, {}, Path(directory))
            peer = Path(directory) / f"{REPORT_ID}.png"
            self.assertEqual(peer.read_bytes(), b"png")

    @unittest.skipUnless(
        (ROOT / NWI_CONTRACT_PATH).is_file() and NWI_PACKAGE.is_dir(),
        "requires exact ignored Petes Lake NWI custody",
    )
    def test_exact_u05_reproduces_upstream_and_measures_bounded_reference(self) -> None:
        contract = json.loads((ROOT / NWI_CONTRACT_PATH).read_bytes())
        if (
            contract.get("extensions", {}).get("state")
            != "PASS_EXACT_PUBLIC_NWI_CONTEXT_CUSTODY_FOR_U05"
        ):
            self.skipTest("exact ignored Petes Lake NWI custody is not finalized")
        commit = contract["extensions"]["git_source_commit"]
        completed = datetime.fromisoformat(
            contract["extensions"]["completed_at_utc"].replace("Z", "+00:00")
        )
        generated = (completed + timedelta(seconds=1)).astimezone(timezone.utc)
        report, _ = build_report(
            repository_root=ROOT,
            generated_at_utc=generated.isoformat(timespec="microseconds").replace(
                "+00:00", "Z"
            ),
            run_id="BL-TEST-PETES-LAKE-U05",
            git_source_commit=commit,
            visual_review_decision=VISUAL_PENDING,
            visual_review_notes="",
        )
        evidence = report["evidence"]
        self.assertTrue(report["upstream_reproduction"]["u03"]["byte_identical"])
        self.assertTrue(report["upstream_reproduction"]["u04"]["byte_identical"])
        self.assertEqual(evidence["frozen_optical_boundary_pixels"], 34_103)
        self.assertEqual(evidence["delivered_mtbs_boundary_pixels"], 34_101)
        self.assertEqual(evidence["boundary_symmetric_difference_pixels"], 52)
        self.assertEqual(
            evidence["mtbs_dnbr6_on_frozen_boundary"],
            {"1": 3036, "2": 7016, "3": 9819, "4": 13181, "6": 439, "255": 612},
        )
        self.assertEqual(evidence["registration_strict_pass_pixels"], 17_461)
        self.assertGreaterEqual(
            evidence["nonprocessing_union_pixels"],
            evidence["delivered_mask_vector_center_pixels"],
        )
        self.assertEqual(evidence["accepted_background_pixels"], 0)
        self.assertGreater(evidence["bounded_reference_pixels"], 0)
        self.assertTrue(evidence["source_project_context_full_eligible_coverage"])
        self.assertTrue(
            report["wetland_limitation"][
                "residual_unmapped_wetland_uncertainty_applies_to_all_surviving_pixels"
            ]
        )
        self.assertIsNone(report["trace"]["dataset_version"])
        self.assertIsNone(report["trace"]["model_version"])


if __name__ == "__main__":
    unittest.main()
