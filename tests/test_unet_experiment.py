from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import numpy as np
from PIL import Image

from burnlens.unet_experiment import (
    PROTOCOL_ID,
    TEST_AUTHORIZATION_VERSION,
    TEST_EVENT_IDS,
    TEST_OPENING_UNIT,
    UNetExperimentError,
    build_protocol,
    load_test_access_grant,
    render_preflight_html,
    render_preflight_png,
    run_preflight,
    write_preflight_outputs,
    write_protocol,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE_COMMIT = "a" * 40
GENERATED_AT = "2026-07-26T01:00:00Z"
RUN_ID = "BL-TEST-P3O1-T01-U03"


class UNetExperimentTests(unittest.TestCase):
    def test_protocol_freezes_exact_contract_without_array_access(self) -> None:
        with mock.patch("numpy.load") as load:
            protocol = build_protocol(
                ROOT, GENERATED_AT, RUN_ID, SOURCE_COMMIT
            )
            load.assert_not_called()
        self.assertEqual(protocol["protocol_id"], PROTOCOL_ID)
        self.assertEqual(protocol["data"]["input_shape"], [6, 64, 64])
        self.assertEqual(protocol["architecture"]["encoder_channels"], [16, 32])
        self.assertEqual(protocol["optimization"]["seed"], 20260725)
        self.assertEqual(protocol["compute_budget"]["substantive_run_count"], 1)
        self.assertEqual(protocol["compute_budget"]["preflight_epochs"], 2)
        self.assertEqual(len(protocol["data"]["sealed_test_roster"]), 4)
        self.assertFalse(protocol["boundaries"]["test_arrays_opened"])
        self.assertEqual(protocol["test_opening"]["open_count_authorized"], 1)

    def test_test_authorization_requires_exact_bindings_and_directory(self) -> None:
        with tempfile.TemporaryDirectory(prefix="burnlens-test-grant-") as directory:
            root = Path(directory)
            parent = root / "records/phase-three/test-openings"
            parent.mkdir(parents=True)
            authorization = parent / "authorization.json"
            value = {
                "authorization_version": TEST_AUTHORIZATION_VERSION,
                "opening_id": "TEST-OPEN-2026-001",
                "authorization_unit": TEST_OPENING_UNIT,
                "status": "AUTHORIZED_NOT_OPENED",
                "open_count_before": 0,
                "open_count_authorized": 1,
                "config_sha256": "a" * 64,
                "weights_sha256": "b" * 64,
                "selection_sha256": "c" * 64,
                "environment_capture_sha256": "d" * 64,
                "test_event_group_ids": list(TEST_EVENT_IDS),
                "test_patch_ids": ["a", "b", "c", "d"],
            }
            authorization.write_text(
                json.dumps(value), encoding="utf-8", newline="\n"
            )
            roster = [{"patch_id": item} for item in ["a", "b", "c", "d"]]
            with (
                mock.patch("burnlens.unet_experiment._bound_json", return_value={}),
                mock.patch("burnlens.unet_experiment._test_roster", return_value=roster),
            ):
                grant = load_test_access_grant(
                    root,
                    authorization,
                    config_sha256="a" * 64,
                    weights_sha256="b" * 64,
                    selection_sha256="c" * 64,
                    environment_capture_sha256="d" * 64,
                )
            self.assertTrue(grant.authorized)
            self.assertEqual(grant.opening_id, "TEST-OPEN-2026-001")
            with (
                self.assertRaisesRegex(UNetExperimentError, "weights_sha256"),
                mock.patch("burnlens.unet_experiment._bound_json", return_value={}),
                mock.patch("burnlens.unet_experiment._test_roster", return_value=roster),
            ):
                    load_test_access_grant(
                        root,
                        authorization,
                        config_sha256="a" * 64,
                        weights_sha256="e" * 64,
                        selection_sha256="c" * 64,
                        environment_capture_sha256="d" * 64,
                    )
            value["test_patch_ids"] = ["a", "b", "c", "wrong"]
            authorization.write_text(
                json.dumps(value), encoding="utf-8", newline="\n"
            )
            with (
                self.assertRaisesRegex(UNetExperimentError, "patch roster"),
                mock.patch("burnlens.unet_experiment._bound_json", return_value={}),
                mock.patch("burnlens.unet_experiment._test_roster", return_value=roster),
                mock.patch("numpy.load") as array_load,
            ):
                load_test_access_grant(
                    root,
                    authorization,
                    config_sha256="a" * 64,
                    weights_sha256="b" * 64,
                    selection_sha256="c" * 64,
                    environment_capture_sha256="d" * 64,
                )
            array_load.assert_not_called()

    def test_two_epoch_preflight_is_exact_and_never_loads_test_arrays(self) -> None:
        with tempfile.TemporaryDirectory(prefix="burnlens-preflight-") as directory:
            protocol_path = Path(directory) / "protocol.json"
            write_protocol(
                ROOT,
                protocol_path,
                GENERATED_AT,
                RUN_ID,
                SOURCE_COMMIT,
            )
            original_load = np.load
            opened: list[str] = []

            def guarded_load(path: object, *args: object, **kwargs: object) -> np.ndarray:
                normalized = str(path).replace("\\", "/")
                if "/test--" in normalized:
                    raise AssertionError(f"sealed test array opened: {normalized}")
                opened.append(normalized)
                return original_load(path, *args, **kwargs)

            with mock.patch("numpy.load", side_effect=guarded_load):
                first = run_preflight(
                    ROOT,
                    protocol_path,
                    GENERATED_AT,
                    RUN_ID,
                    SOURCE_COMMIT,
                )
                second = run_preflight(
                    ROOT,
                    protocol_path,
                    GENERATED_AT,
                    RUN_ID,
                    SOURCE_COMMIT,
                )
            self.assertEqual(first, second)
            self.assertEqual(len(first["history"]), 2)
            self.assertEqual(first["roster"]["train_core_pixels"], 109)
            self.assertEqual(first["roster"]["validation_core_pixels"], 89)
            self.assertEqual(first["roster"]["test_patch_ids_opened"], [])
            self.assertTrue(first["gates"]["finite"])
            self.assertTrue(opened)
            self.assertFalse(any("/test--" in path for path in opened))

    def test_rendered_outputs_are_deterministic_local_and_no_overwrite(self) -> None:
        with tempfile.TemporaryDirectory(prefix="burnlens-preflight-render-") as directory:
            base = Path(directory)
            protocol_path = base / "protocol.json"
            write_protocol(
                ROOT,
                protocol_path,
                GENERATED_AT,
                RUN_ID,
                SOURCE_COMMIT,
            )
            report = run_preflight(
                ROOT,
                protocol_path,
                GENERATED_AT,
                RUN_ID,
                SOURCE_COMMIT,
            )
            first_png = render_preflight_png(report)
            second_png = render_preflight_png(report)
            self.assertEqual(first_png, second_png)
            image_path = base / "preview.png"
            image_path.write_bytes(first_png)
            with Image.open(image_path) as image:
                self.assertEqual(image.size, (1800, 1120))
                self.assertEqual(image.mode, "RGB")
            html = render_preflight_html(report, "preview.png")
            self.assertIn(b"Skip to evidence", html)
            self.assertIn(b"test arrays remain unopened", html)
            self.assertIn(b"not independent ground truth", html)
            self.assertNotIn(b"http://", html)
            self.assertNotIn(b"https://", html)

            output_directory = base / "outputs"
            receipts = write_preflight_outputs(
                ROOT,
                protocol_path,
                output_directory,
                GENERATED_AT,
                RUN_ID,
                SOURCE_COMMIT,
            )
            self.assertEqual(set(receipts), {"json", "html", "png"})
            with self.assertRaisesRegex(UNetExperimentError, "already exists"):
                write_preflight_outputs(
                    ROOT,
                    protocol_path,
                    output_directory,
                    GENERATED_AT,
                    RUN_ID,
                    SOURCE_COMMIT,
                )


if __name__ == "__main__":
    unittest.main()
