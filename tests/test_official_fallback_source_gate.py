from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from burnlens.official_fallback_source_gate import (
    DECISION,
    FROZEN_INPUTS,
    GATE_IDS,
    REPORT_ID,
    SOURCE_ID,
    TRACE_PATHS,
    OfficialFallbackGateError,
    _validate_gate,
    _validate_repository_trace,
    build_report,
    build_source,
    run_report,
)


ROOT = Path(__file__).resolve().parents[1]
GENERATED = "2026-07-23T04:30:00Z"
RUN_ID = "BL-2026-07-23-official-fallback-comparison-r001"
COMMIT = "a" * 40
T34_MERGE_COMMIT = "0e58459ea45f509eca537223d872fd6992efb291"


class OfficialFallbackSourceGateTests(unittest.TestCase):
    def _materialize_frozen_inputs(self, root: Path) -> None:
        for spec in FROZEN_INPUTS.values():
            relative = str(spec["path"])
            result = subprocess.run(
                ["git", "-C", str(ROOT), "show", f"{T34_MERGE_COMMIT}:{relative}"],
                check=False,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, relative)
            payload = result.stdout
            expected_bytes = int(spec["bytes"])
            expected_sha256 = str(spec["sha256"])
            if len(payload) != expected_bytes or sha256(payload).hexdigest() != expected_sha256:
                # The frozen T34 bindings captured the Windows checkout bytes.
                # Reproduce Git's LF-to-CRLF worktree conversion without reading
                # later-mutated live files.
                payload = payload.replace(b"\n", b"\r\n")
            self.assertEqual(len(payload), expected_bytes, relative)
            self.assertEqual(sha256(payload).hexdigest(), expected_sha256, relative)
            destination = root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(payload)

    def _source(self) -> dict:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            self._materialize_frozen_inputs(root)
            return build_source(
                repository_root=root,
                generated_at_utc=GENERATED,
                run_id=RUN_ID,
                git_source_commit=COMMIT,
            )

    def test_source_selects_neither_and_preserves_boundaries(self) -> None:
        source = self._source()
        self.assertEqual(source["source_id"], SOURCE_ID)
        self.assertEqual([item["unit_disposition"] for item in source["candidates"]], ["defer", "defer"])
        self.assertTrue(all(item["selected"] is False for item in source["candidates"]))
        self.assertIsNone(source["boundaries"]["selected_candidate"])
        self.assertFalse(source["boundaries"]["provider_bytes_authorized"])
        self.assertEqual(source["boundaries"]["provider_bytes_acquired"], 0)
        self.assertFalse(source["reference_state"]["dataset_created"])
        self.assertEqual(source["reference_state"]["event_group_count"], 5)
        self.assertEqual(source["reference_state"]["minimum_event_group_count"], 6)

    def test_report_rejects_selection_or_provider_authorization(self) -> None:
        source = self._source()
        selected = deepcopy(source)
        selected["candidates"][0]["selected"] = True
        with self.assertRaisesRegex(OfficialFallbackGateError, "DISPOSITION_DRIFT"):
            build_report(selected, source_bytes=1, source_sha256="0" * 64)
        authorized = deepcopy(source)
        authorized["boundaries"]["provider_bytes_authorized"] = True
        with self.assertRaisesRegex(OfficialFallbackGateError, "BOUNDARY_DRIFT"):
            build_report(authorized, source_bytes=1, source_sha256="0" * 64)

    def test_gate_rejects_tampered_provider_permission(self) -> None:
        path = ROOT / (
            "samples/reference/phase-two/"
            "OFFICIAL-FALLBACK-SOURCE-GATE-MCKENZIE-2026-001.json"
        )
        gate = json.loads(path.read_text(encoding="utf-8"))
        gate["provider_bytes_authorized"] = True
        with self.assertRaisesRegex(OfficialFallbackGateError, "PROVIDER_BYTES_AUTHORIZED_DRIFT"):
            _validate_gate(gate, expected_id=GATE_IDS["mckenzie"])

    def test_frozen_input_bytes_and_hashes_reject_tamper(self) -> None:
        for role in ("milli_terms", "verified_lifecycle_manifest"):
            with self.subTest(role=role), TemporaryDirectory() as directory:
                root = Path(directory)
                self._materialize_frozen_inputs(root)
                tampered = root / str(FROZEN_INPUTS[role]["path"])
                tampered.write_bytes(tampered.read_bytes() + b"\nUNREVIEWED_DRIFT\n")
                with self.assertRaisesRegex(OfficialFallbackGateError, f"INPUT_BYTES_DRIFT:{role}"):
                    build_source(
                        repository_root=root,
                        generated_at_utc=GENERATED,
                        run_id=RUN_ID,
                        git_source_commit=COMMIT,
                    )

    def test_repository_trace_rejects_commit_mismatch_and_relevant_drift(self) -> None:
        with self.assertRaisesRegex(OfficialFallbackGateError, "GIT_SOURCE_COMMIT_MISMATCH"):
            _validate_repository_trace(ROOT, COMMIT)
        tracked = "\n".join(TRACE_PATHS)
        with patch(
            "burnlens.official_fallback_source_gate._git",
            side_effect=[str(ROOT.resolve()), COMMIT, tracked, " M burnlens/official_fallback_source_gate.py"],
        ):
            with self.assertRaisesRegex(OfficialFallbackGateError, "GIT_RELEVANT_WORKTREE_DIRTY"):
                _validate_repository_trace(ROOT, COMMIT)

    def test_exact_output_is_deterministic_and_mobile_safe(self) -> None:
        with TemporaryDirectory() as directory, patch(
            "burnlens.official_fallback_source_gate._validate_repository_trace"
        ):
            root = Path(directory)
            frozen = root / "frozen"
            self._materialize_frozen_inputs(frozen)
            first = run_report(
                repository_root=frozen,
                output_directory=root / "first",
                generated_at_utc=GENERATED,
                run_id=RUN_ID,
                git_source_commit=COMMIT,
            )
            second = run_report(
                repository_root=frozen,
                output_directory=root / "second",
                generated_at_utc=GENERATED,
                run_id=RUN_ID,
                git_source_commit=COMMIT,
            )
            for key in ("source", "json", "html", "png"):
                self.assertEqual(first[key].read_bytes(), second[key].read_bytes(), key)
            report = json.loads(first["json"].read_text(encoding="utf-8"))
            self.assertEqual(report["report_id"], REPORT_ID)
            self.assertEqual(report["decision"], DECISION)
            self.assertIsNone(report["selected_candidate"])
            self.assertEqual(report["outputs"]["png"]["width"], 1600)
            self.assertEqual(report["outputs"]["png"]["height"], 1940)
            self.assertEqual(len(report["comparison"]), 10)
            html = first["html"].read_text(encoding="utf-8")
            self.assertIn('name="viewport"', html)
            self.assertIn("@media(max-width:760px)", html)
            self.assertIn('data-label="McKenzie HUC8 NWI"', html)
            self.assertIn('data-label="Milli 0843 CS"', html)
            self.assertIn("content:attr(data-label)", html)
            self.assertIn("Select neither", html)
            self.assertNotIn("<script", html.lower())

    def test_existing_output_directory_fails_closed(self) -> None:
        with TemporaryDirectory() as directory:
            output = Path(directory) / "existing"
            output.mkdir()
            with self.assertRaisesRegex(OfficialFallbackGateError, "OUTPUT_DIRECTORY_ALREADY_EXISTS"):
                run_report(
                    repository_root=ROOT,
                    output_directory=output,
                    generated_at_utc=GENERATED,
                    run_id=RUN_ID,
                    git_source_commit=COMMIT,
                )


if __name__ == "__main__":
    unittest.main()
