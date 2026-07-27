from __future__ import annotations

from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
P2O4_T39_BASE = "657ba657ab9d23964dcaf76d377aec3a10e814da"
TEXT_SUFFIXES = {
    ".html",
    ".json",
    ".lock",
    ".md",
    ".mjs",
    ".ps1",
    ".py",
    ".toml",
}
CRLF_PATHS = {
    "records/phase-two/prechecks/PRECHECK-2026-081.md",
}
CHECK_ATTR_BATCH_SIZE = 100


def _changed_paths() -> list[str]:
    completed = subprocess.run(
        ["git", "diff", "--name-only", f"{P2O4_T39_BASE}...HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.splitlines()


class V051CheckoutContractTests(unittest.TestCase):
    def test_every_p2o4_t39_text_file_has_an_explicit_checkout_contract(
        self,
    ) -> None:
        text_paths = [
            path
            for path in _changed_paths()
            if Path(path).suffix in TEXT_SUFFIXES or path == ".gitattributes"
        ]
        self.assertGreater(len(text_paths), 100)

        attributes: list[str] = []
        for start in range(0, len(text_paths), CHECK_ATTR_BATCH_SIZE):
            completed = subprocess.run(
                [
                    "git",
                    "check-attr",
                    "text",
                    "eol",
                    "--",
                    *text_paths[start : start + CHECK_ATTR_BATCH_SIZE],
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            attributes.extend(completed.stdout.splitlines())
        for path in text_paths:
            self.assertIn(f"{path}: text: set", attributes)
            expected_eol = "crlf" if path in CRLF_PATHS else "lf"
            self.assertIn(f"{path}: eol: {expected_eol}", attributes)

    def test_p2o4_t39_worktree_bytes_match_declared_checkout_bytes(self) -> None:
        mismatches: list[str] = []
        for path in _changed_paths():
            working_path = ROOT / path
            if not working_path.is_file():
                continue
            committed = subprocess.run(
                ["git", "show", f"HEAD:{path}"],
                cwd=ROOT,
                check=True,
                capture_output=True,
            ).stdout
            expected = (
                committed.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
                if path in CRLF_PATHS
                else committed
            )
            if working_path.read_bytes() != expected:
                mismatches.append(path)

        self.assertEqual(mismatches, [])


if __name__ == "__main__":
    unittest.main()
