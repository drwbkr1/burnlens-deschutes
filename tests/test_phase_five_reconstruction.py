from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from burnlens.phase_five_reconstruction import (
    _array_contracts,
    _semantic_contracts,
    _tracked_files,
    render_html,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = (
    ROOT
    / "samples/runs/phase-four/"
    "burnlens-ward-creek-rbr-run-v0.1.0"
)


class PhaseFiveReconstructionTests(unittest.TestCase):
    def test_tracked_package_roster_is_exact(self) -> None:
        files = _tracked_files(PACKAGE)
        self.assertEqual(len(files), 66)
        self.assertIn("PACKAGE-MANIFEST.json", files)
        self.assertIn("status/STATUS.json", files)

    def test_array_and_raster_contracts_pass(self) -> None:
        result = _array_contracts(ROOT)
        self.assertEqual(result["comparison_count"], 10)
        self.assertEqual(result["status"], "pass")
        self.assertTrue(
            all(item["crs"] == "EPSG:32610" for item in result["comparisons"])
        )

    def test_semantic_contract_keeps_rejected_model_boundary(self) -> None:
        result = _semantic_contracts(ROOT)
        self.assertEqual(
            result["accepted_method"], "burnlens-baseline-v0.1.0"
        )
        self.assertFalse(result["model_accepted"])
        self.assertFalse(result["model_outperformed_rbr"])
        self.assertEqual(
            result["observed_metrics"]["WCP-002"][
                "accepted_rbr_inside_mtbs_pct"
            ],
            0.0,
        )

    def test_tracked_roster_rejects_an_extra_file(self) -> None:
        with TemporaryDirectory() as temporary:
            target = Path(temporary) / "package"
            target.mkdir()
            for relative, payload in _tracked_files(PACKAGE).items():
                path = target / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(payload)
            (target / "unexpected.txt").write_text("unexpected")
            with self.assertRaisesRegex(
                RuntimeError, "tracked package file count differs"
            ):
                _tracked_files(target)

    def test_html_is_offline_and_preserves_release_boundaries(self) -> None:
        report = {
            "git_source_commit": "a" * 40,
            "disposition": "pass",
            "checks": {
                "source": {"status": "pass"},
                "frozen_bindings": {"status": "pass"},
                "exact_archive_reconstruction": {
                    "status": "pass",
                    "bytes": 487893,
                    "sha256": "b" * 64,
                },
                "arrays": {"status": "pass"},
                "semantic_contracts": {"status": "pass"},
                "installed_roster": {
                    "status": "pass",
                    "software_version": "0.54.0",
                    "command_count": 119,
                },
                "rollback_identity": {
                    "status": "pass",
                    "tag": "v0.54.0-rbr-geoint-milestone",
                    "tag_object": "c" * 40,
                    "peeled_commit": "d" * 40,
                },
            },
        }
        html = render_html(deepcopy(report)).decode("utf-8")
        self.assertIn("default-src 'none'", html)
        self.assertIn("did not outperform RBR", html)
        self.assertIn("WCP-002", html)
        self.assertNotIn("<script", html)
        self.assertNotIn("https://", html)


if __name__ == "__main__":
    unittest.main()
