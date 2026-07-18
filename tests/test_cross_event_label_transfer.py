from __future__ import annotations

import ast
from hashlib import sha256
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import numpy as np
import rasterio
from rasterio.transform import Affine

import burnlens
from burnlens.cross_event_label_transfer import (
    _registration_state,
    classify_transfer_states,
    summarize_states,
)
from burnlens.mtbs_cross_event_reference import (
    MtbsReferenceContract,
    MtbsReferenceError,
    export_url,
    inspect_clip,
    public_verification_summary,
    validate_contracts,
)


class CrossEventLabelTransferTests(unittest.TestCase):
    def test_current_package_version_is_cross_event_label_transfer_version(self) -> None:
        self.assertEqual(burnlens.__version__, "0.29.0")

    def test_cross_event_text_artifacts_have_checkout_stable_lf_contract(self) -> None:
        root = Path(__file__).resolve().parents[1]
        attributes = (root / ".gitattributes").read_text(encoding="utf-8").splitlines()
        self.assertIn("*.py text eol=lf", attributes)
        self.assertIn("pyproject.toml text eol=lf", attributes)
        self.assertIn("LICENSE text eol=lf", attributes)
        self.assertIn(
            "samples/labels/cross-event/phase-two/*.json text eol=lf", attributes
        )
        self.assertIn(
            "samples/labels/cross-event/phase-two/*.html text eol=lf", attributes
        )

    def test_mtbs_contracts_and_url_are_exact_and_public(self) -> None:
        self.assertEqual(validate_contracts(), [])
        contract = MtbsReferenceContract(
            event_group_id="event-test",
            fire_id="TEST",
            year=2018,
            filename="test.tif",
            bbox_3857=(0.0, 0.0, 60.0, 30.0),
            width=2,
            height=1,
            expected_size_bytes=1,
            expected_sha256="0" * 64,
            expected_value_counts=((0, 1), (2, 1)),
        )
        url = export_url(contract)
        self.assertIn("USFS_EDW_MTBS_CONUS/ImageServer/exportImage", url)
        self.assertIn("Year%3D2018", url)
        self.assertIn("RSP_NearestNeighbor", url)
        self.assertNotIn("email", url.lower())
        self.assertNotIn("token", url.lower())

    def test_clip_inspection_checks_bytes_grid_domain_and_link_count(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.tif"
            values = np.array([[0, 2], [3, 4]], dtype=np.uint8)
            transform = Affine(30, 0, 1000, 0, -30, 2060)
            with rasterio.open(
                path,
                "w",
                driver="GTiff",
                width=2,
                height=2,
                count=1,
                dtype="uint8",
                crs="EPSG:3857",
                transform=transform,
            ) as destination:
                destination.write(values, 1)
            contract = MtbsReferenceContract(
                event_group_id="event-test",
                fire_id="TEST",
                year=2018,
                filename=path.name,
                bbox_3857=(1000.0, 2000.0, 1060.0, 2060.0),
                width=2,
                height=2,
                expected_size_bytes=path.stat().st_size,
                expected_sha256=sha256(path.read_bytes()).hexdigest(),
                expected_value_counts=((0, 1), (2, 1), (3, 1), (4, 1)),
            )
            result = inspect_clip(path, contract)
            self.assertEqual(result["value_counts"], {"0": 1, "2": 1, "3": 1, "4": 1})
            self.assertEqual(result["link_count"], 1)

            one_link = public_verification_summary({
                "accepted_as_unchanged_registered_package": True,
                "registration_manifest_sha256": "a" * 64,
                "registration_manifest_link_count": 1,
                "assets": [result],
            })
            first_alias = path.with_name("fixture-first-alias.tif")
            os.link(path, first_alias)
            two_link_result = inspect_clip(path, contract)
            self.assertEqual(two_link_result["link_count"], 2)
            two_link = public_verification_summary({
                "accepted_as_unchanged_registered_package": True,
                "registration_manifest_sha256": "a" * 64,
                "registration_manifest_link_count": 2,
                "assets": [two_link_result],
            })
            self.assertEqual(one_link, two_link)
            self.assertTrue(
                all("link_count" not in asset and "link_gate" not in asset for asset in one_link["assets"])
            )
            self.assertEqual(
                one_link["link_policy"]["result"],
                "PASS_APPROVED_CONTENT_VERIFIED_TOPOLOGY",
            )

            second_alias = path.with_name("fixture-second-alias.tif")
            os.link(path, second_alias)
            with self.assertRaisesRegex(MtbsReferenceError, "link count is unsupported"):
                inspect_clip(path, contract)

    def test_registration_window_precedence_preserves_tepee_exclusions(self) -> None:
        windows = [
            {"state": "excluded", "pixel_window": {"row_offset": 0, "column_offset": 0, "height": 4, "width": 4}},
            {"state": "review-needed", "pixel_window": {"row_offset": 0, "column_offset": 3, "height": 4, "width": 4}},
            {"state": "pass", "pixel_window": {"row_offset": 0, "column_offset": 6, "height": 4, "width": 4}},
        ]
        states = _registration_state((4, 10), windows)
        self.assertTrue(np.all(states[:, :4] == 2))
        self.assertTrue(np.all(states[:, 4:7] == 1))
        self.assertTrue(np.all(states[:, 7:] == 0))

    def test_transfer_preserves_all_five_states_and_binary_ignore_contract(self) -> None:
        shape = (24, 48)
        pair_quality = np.zeros(shape, dtype=np.uint8)
        pair_quality[:, :2] = 2
        pair_quality[:, 2:4] = 1
        registration = np.zeros(shape, dtype=np.uint8)
        reference = np.zeros(shape, dtype=bool)
        reference[4:20, 17:34] = True
        mtbs = np.zeros(shape, dtype=np.uint8)
        mtbs[reference] = 3
        mtbs[7:10, 20:23] = 1
        evidence = {
            "dnbr": np.zeros(shape, dtype=np.float32),
            "ndvi_loss": np.zeros(shape, dtype=np.float32),
            "swir_gain": np.zeros(shape, dtype=np.float32),
            "nir_loss": np.zeros(shape, dtype=np.float32),
        }
        for name in evidence:
            evidence[name][reference] = 0.20
        evidence["dnbr"][11:14, 25:28] = 0.05
        evidence["ndvi_loss"][11:14, 25:28] = 0.04
        evidence["swir_gain"][11:14, 25:28] = 0.015
        evidence["nir_loss"][11:14, 25:28] = 0.015
        states, target, _ = classify_transfer_states(
            pair_quality=pair_quality,
            registration_state=registration,
            reference_mask=reference,
            mtbs=mtbs,
            evidence=evidence,
            numeric_valid=np.ones(shape, dtype=bool),
        )
        summary = summarize_states(states)
        counts = {item["state"]: item["pixels"] for item in summary["states"]}
        self.assertTrue(all(counts[name] > 0 for name in counts))
        self.assertTrue(np.all(target[np.isin(states, [2, 3, 4])] == 255))
        self.assertTrue(np.all(target[states == 0] == 0))
        self.assertTrue(np.all(target[states == 1] == 1))

    def test_authorized_stability_fallback_recovers_coherent_background(self) -> None:
        shape = (20, 20)
        low_change = np.zeros(shape, dtype=bool)
        low_change[6:14, 6:14] = True
        evidence = {
            "dnbr": np.full(shape, -0.30, dtype=np.float32),
            "ndvi_loss": np.full(shape, -0.20, dtype=np.float32),
            "swir_gain": np.full(shape, -0.15, dtype=np.float32),
            "nir_loss": np.full(shape, -0.15, dtype=np.float32),
        }
        evidence["dnbr"][low_change] = -0.06
        evidence["ndvi_loss"][low_change] = -0.06
        evidence["swir_gain"][low_change] = -0.02
        evidence["nir_loss"][low_change] = -0.02
        states, target, diagnostics = classify_transfer_states(
            pair_quality=np.zeros(shape, dtype=np.uint8),
            registration_state=np.zeros(shape, dtype=np.uint8),
            reference_mask=np.zeros(shape, dtype=bool),
            mtbs=np.zeros(shape, dtype=np.uint8),
            evidence=evidence,
            numeric_valid=np.ones(shape, dtype=bool),
        )
        self.assertEqual(int(diagnostics["stable_primary"].sum()), 0)
        self.assertEqual(
            diagnostics["stability_fallback_threshold_normalized"], 4.0
        )
        self.assertGreater(int(diagnostics["stable_fallback_coherent"].sum()), 0)
        self.assertGreater(int((states == 0).sum()), 0)
        self.assertTrue(np.all(target[states == 0] == 0))
        self.assertFalse(np.any(target[states != 0] != 255))

    def test_qa_module_does_not_import_transfer_module_or_classifier(self) -> None:
        source = (
            Path(__file__).resolve().parents[1]
            / "burnlens/cross_event_label_transfer_qa.py"
        ).read_text(encoding="utf-8")
        tree = ast.parse(source)
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                imports.append(node.module or "")
            elif isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
        self.assertFalse(any(name.endswith("cross_event_label_transfer") for name in imports))
        self.assertNotIn("classify_transfer_states", source)


if __name__ == "__main__":
    unittest.main()
