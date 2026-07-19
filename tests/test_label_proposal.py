from __future__ import annotations

import ast
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import numpy as np
import rasterio
from rasterio.transform import Affine

import burnlens
from burnlens.label_proposal import (
    HEIGHT,
    IGNORE_VALUE,
    LABEL_PROPOSAL_VERSION,
    LABEL_SCHEMA_VERSION,
    STATE_CODES,
    WIDTH,
    LabelProposalError,
    _write_raster,
    boundary_band,
    classify_label_states,
    dilate_mask,
    erode_mask,
    neighbor_support,
    summarize_states,
)
from burnlens.label_proposal_qa import (
    LabelProposalQaError,
    _qa_classify,
    _read_proposal_raster,
    _select_coordinates,
    _validate_visual_decision,
)


def _synthetic_contract() -> tuple[np.ndarray, np.ndarray, dict[str, np.ndarray], np.ndarray]:
    shape = (HEIGHT, WIDTH)
    pair_quality = np.zeros(shape, dtype=np.uint8)
    reference = np.zeros(shape, dtype=bool)
    reference[100:300, 200:400] = True
    evidence = {
        "dnbr": np.zeros(shape, dtype=np.float32),
        "ndvi_loss": np.zeros(shape, dtype=np.float32),
        "swir_gain": np.zeros(shape, dtype=np.float32),
        "nir_loss": np.zeros(shape, dtype=np.float32),
    }
    evidence["dnbr"][130:270, 230:370] = 0.20
    evidence["ndvi_loss"][130:270, 230:370] = 0.10
    evidence["swir_gain"][130:270, 230:370] = 0.03
    evidence["nir_loss"][130:270, 230:370] = 0.03
    # Valid, non-stable evidence outside the reference remains unknown.
    evidence["dnbr"][10:40, 10:40] = 0.05
    evidence["ndvi_loss"][10:40, 10:40] = 0.04
    pair_quality[50:60, 50:60] = 1
    pair_quality[70:80, 70:80] = 2
    numeric_valid = np.ones(shape, dtype=bool)
    return pair_quality, reference, evidence, numeric_valid


class LabelProposalTests(unittest.TestCase):
    def test_current_version_and_lf_checkout_contract_are_explicit(self) -> None:
        self.assertEqual(burnlens.__version__, "0.32.0")
        root = Path(__file__).resolve().parents[1]
        attributes = (root / ".gitattributes").read_text(encoding="utf-8").splitlines()
        self.assertIn("samples/labels/phase-two/*.json text eol=lf", attributes)
        self.assertIn("samples/labels/phase-two/*.html text eol=lf", attributes)

    def test_binary_morphology_and_neighbor_support_are_eight_connected(self) -> None:
        mask = np.zeros((5, 5), dtype=bool)
        mask[2, 2] = True
        self.assertEqual(int(dilate_mask(mask).sum()), 9)
        self.assertEqual(int(neighbor_support(mask)[2, 2]), 1)
        self.assertEqual(int(neighbor_support(dilate_mask(mask))[2, 2]), 9)
        np.testing.assert_array_equal(erode_mask(dilate_mask(mask)), mask)
        self.assertTrue(boundary_band(mask)[2, 2])
        self.assertEqual(int(boundary_band(mask).sum()), 9)

    def test_five_state_proposal_preserves_uncertainty_and_target_ignore(self) -> None:
        pair_quality, reference, evidence, numeric_valid = _synthetic_contract()
        states, target, masks = classify_label_states(
            pair_quality=pair_quality,
            reference_mask=reference,
            evidence=evidence,
            numeric_valid=numeric_valid,
        )
        self.assertEqual(set(int(value) for value in np.unique(states)), set(STATE_CODES.values()))
        self.assertEqual(set(int(value) for value in np.unique(target)), {0, 1, IGNORE_VALUE})
        np.testing.assert_array_equal(target[states == STATE_CODES["background-candidate"]], 0)
        np.testing.assert_array_equal(target[states == STATE_CODES["burned"]], 1)
        np.testing.assert_array_equal(target[np.isin(states, [2, 3, 4])], IGNORE_VALUE)
        self.assertTrue(masks["burn_coherent"][200, 300])
        self.assertTrue(masks["stable_coherent"][400, 500])
        summary = summarize_states(states)
        self.assertEqual(summary["pixel_count"], HEIGHT * WIDTH)
        self.assertEqual(summary["machine_decision"], "PROPOSAL_READY_FOR_SEPARATE_QA")
        self.assertEqual(summary["candidate_target_pixels"] + summary["ignored_pixels"], HEIGHT * WIDTH)

    def test_summary_fails_closed_when_any_required_state_is_absent(self) -> None:
        with self.assertRaisesRegex(LabelProposalError, "every required state"):
            summarize_states(np.zeros((HEIGHT, WIDTH), dtype=np.uint8))

    def test_unknown_pair_quality_and_wrong_grid_fail_closed(self) -> None:
        pair_quality, reference, evidence, numeric_valid = _synthetic_contract()
        pair_quality[0, 0] = 9
        with self.assertRaisesRegex(LabelProposalError, "unknown state"):
            classify_label_states(
                pair_quality=pair_quality,
                reference_mask=reference,
                evidence=evidence,
                numeric_valid=numeric_valid,
            )
        with self.assertRaisesRegex(LabelProposalError, "frozen native"):
            classify_label_states(
                pair_quality=np.zeros((2, 2), dtype=np.uint8),
                reference_mask=np.zeros((2, 2), dtype=bool),
                evidence={name: np.zeros((2, 2)) for name in evidence},
                numeric_valid=np.ones((2, 2), dtype=bool),
            )

    def test_proposal_geotiffs_are_deterministic_and_traceable(self) -> None:
        values = np.zeros((HEIGHT, WIDTH), dtype=np.uint8)
        transform = Affine(20, 0, 620000, 0, -20, 4840000)
        with TemporaryDirectory() as directory:
            paths = [Path(directory) / f"state-{index}.tif" for index in range(2)]
            for path in paths:
                _write_raster(
                    path,
                    values,
                    transform,
                    nodata=None,
                    kind="five-state companion proposal",
                    run_id="BL-test-label-proposal-r001",
                    git_source_commit="a" * 40,
                )
            hashes = [sha256(path.read_bytes()).hexdigest() for path in paths]
            self.assertEqual(hashes[0], hashes[1])
            with rasterio.open(paths[0]) as source:
                self.assertEqual(source.crs.to_epsg(), 32610)
                self.assertEqual(source.transform, transform)
                self.assertIsNone(source.nodata)
                self.assertEqual(source.tags()["label_schema_version"], LABEL_SCHEMA_VERSION)
                self.assertEqual(source.tags()["label_proposal_version"], LABEL_PROPOSAL_VERSION)
                self.assertEqual(source.tags()["run_id"], "BL-test-label-proposal-r001")
                self.assertEqual(source.tags()["git_source_commit"], "a" * 40)

    def test_qa_reader_rejects_raster_trace_tag_drift(self) -> None:
        values = np.zeros((HEIGHT, WIDTH), dtype=np.uint8)
        transform = Affine(20, 0, 620000, 0, -20, 4840000)
        with TemporaryDirectory() as directory:
            path = Path(directory) / "state.tif"
            _write_raster(
                path,
                values,
                transform,
                nodata=None,
                kind="five-state companion proposal",
                run_id="BL-test-label-proposal-r001",
                git_source_commit="a" * 40,
            )
            _read_proposal_raster(
                path,
                expected_nodata=None,
                expected_transform=transform,
                expected_kind="five-state companion proposal",
                expected_run_id="BL-test-label-proposal-r001",
                expected_git_source_commit="a" * 40,
            )
            with rasterio.open(path, "r+") as target:
                target.update_tags(git_source_commit="b" * 40)
            with self.assertRaisesRegex(LabelProposalQaError, "trace tag mismatch"):
                _read_proposal_raster(
                    path,
                    expected_nodata=None,
                    expected_transform=transform,
                    expected_kind="five-state companion proposal",
                    expected_run_id="BL-test-label-proposal-r001",
                    expected_git_source_commit="a" * 40,
                )

    def test_separate_qa_reimplementation_matches_all_synthetic_pixels(self) -> None:
        pair_quality, reference, evidence, numeric_valid = _synthetic_contract()
        proposal_states, proposal_target, _ = classify_label_states(
            pair_quality=pair_quality,
            reference_mask=reference,
            evidence=evidence,
            numeric_valid=numeric_valid,
        )
        qa_states, qa_target, _ = _qa_classify(pair_quality, reference, evidence, numeric_valid)
        np.testing.assert_array_equal(proposal_states, qa_states)
        np.testing.assert_array_equal(proposal_target, qa_target)

    def test_qa_source_does_not_import_proposal_classifier(self) -> None:
        source_path = Path(__file__).resolve().parents[1] / "burnlens" / "label_proposal_qa.py"
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.append(node.module or "")
        self.assertFalse(any(name.endswith("label_proposal") for name in imports))

    def test_qa_visual_decision_fails_closed(self) -> None:
        _validate_visual_decision(True, "PENDING_QA_VISUAL_REVIEW", "")
        with self.assertRaisesRegex(LabelProposalQaError, "requires notes"):
            _validate_visual_decision(True, "ACCEPT_REVIEWABLE_LABEL_PROPOSAL_DEFER_DATASET", "")
        with self.assertRaisesRegex(LabelProposalQaError, "incompatible"):
            _validate_visual_decision(False, "ACCEPT_REVIEWABLE_LABEL_PROPOSAL_DEFER_DATASET", "reviewed")
        with self.assertRaisesRegex(LabelProposalQaError, "invalid"):
            _validate_visual_decision(True, "ACCEPT_DATASET", "reviewed")

    def test_audit_coordinate_selection_is_stable_and_unique(self) -> None:
        mask = np.zeros((HEIGHT, WIDTH), dtype=bool)
        mask[100:120, 200:240] = True
        first = _select_coordinates(mask, 20, "proposal-run:burned")
        second = _select_coordinates(mask, 20, "proposal-run:burned")
        self.assertEqual(first, second)
        self.assertEqual(len(first), 20)
        self.assertEqual(len(set(first)), 20)
        self.assertTrue(all(mask[row, column] for row, column in first))


if __name__ == "__main__":
    unittest.main()
