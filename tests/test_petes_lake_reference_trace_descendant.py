from __future__ import annotations

from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest

from burnlens import petes_lake_reference_native_contract as native_contract
from burnlens.petes_lake_reference_native_contract import (
    EXCEPTION_BRANCH,
    MILESTONE_BRANCH,
    NATIVE_CLI_PATH,
    NATIVE_MODULE_PATH,
    NATIVE_TEST_PATH,
    PetesLakeReferenceNativeContractError,
    TRACE_SCRIPT_NAME,
    TRACE_SCRIPT_TARGET,
    _scientific_source_fingerprint,
    validate_repository_trace,
)


ROOT = Path(__file__).resolve().parents[1]
HISTORICAL_SOURCE = "20d6991cbc079f87db6a789717ebd01595c0b05c"


def _run(root: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *arguments],
        check=True,
        capture_output=True,
        text=True,
    )


def _historical(path: str) -> bytes:
    return subprocess.check_output(
        ["git", "-C", str(ROOT), "show", f"{HISTORICAL_SOURCE}:{path}"]
    )


def _write(root: Path, path: str, data: bytes | str) -> None:
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data.encode("utf-8") if isinstance(data, str) else data)


def _pyproject(*, version: str, target: str = TRACE_SCRIPT_TARGET, extra: bool = False) -> str:
    lines = [
        "[project]",
        'name = "burnlens-deschutes"',
        f'version = "{version}"',
        "[project.scripts]",
        f'{TRACE_SCRIPT_NAME} = "{target}"',
    ]
    if extra:
        lines.append('burnlens-unrelated-descendant-command = "burnlens.example:main"')
    return "\n".join(lines) + "\n"


def _attributes(*, native_eol: str = "lf", extra: bool = False) -> str:
    lines = [
        f"{NATIVE_MODULE_PATH} text eol={native_eol}",
        f"{NATIVE_CLI_PATH} text eol=lf",
        f"{NATIVE_TEST_PATH} text eol=lf",
    ]
    if extra:
        lines.append("records/unrelated-descendant.md text eol=lf")
    return "\n".join(lines) + "\n"


class PetesLakeReferenceDescendantTraceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = TemporaryDirectory()
        self.base = Path(self.temporary.name).resolve()
        self.root = self.base / "worktree"
        self.origin = self.base / "origin.git"
        self.root.mkdir()
        _run(self.base, "init", "--bare", str(self.origin))
        _run(self.root, "init", "-b", MILESTONE_BRANCH)
        _run(self.root, "config", "user.name", "BurnLens Trace Test")
        _run(self.root, "config", "user.email", "trace-test@example.invalid")
        _run(self.root, "remote", "add", "origin", str(self.origin))

        _write(self.root, NATIVE_MODULE_PATH, _historical(NATIVE_MODULE_PATH))
        _write(self.root, NATIVE_CLI_PATH, _historical(NATIVE_CLI_PATH))
        _write(self.root, NATIVE_TEST_PATH, _historical(NATIVE_TEST_PATH))
        _write(self.root, "pyproject.toml", _pyproject(version="0.44.0"))
        _write(self.root, ".gitattributes", _attributes())
        _run(self.root, "add", "--all")
        _run(self.root, "commit", "-m", "historical U04 source")
        self.source = _run(self.root, "rev-parse", "HEAD").stdout.strip()

        _write(self.root, NATIVE_MODULE_PATH, Path(native_contract.__file__).read_bytes())
        _write(self.root, "pyproject.toml", _pyproject(version="0.45.0", extra=True))
        _write(self.root, ".gitattributes", _attributes(extra=True))
        _run(self.root, "add", "--all")
        _run(self.root, "commit", "-m", "descendant trace remediation")
        self._synchronize_remote()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _synchronize_remote(self) -> None:
        branch = _run(self.root, "branch", "--show-current").stdout.strip()
        _run(self.root, "push", "origin", f"HEAD:refs/heads/{branch}")

    def _commit(self, message: str, *, synchronize: bool = True) -> None:
        _run(self.root, "add", "--all")
        _run(self.root, "commit", "-m", message)
        if synchronize:
            self._synchronize_remote()

    def test_allows_only_registered_milestone_exception_and_main_branches(self) -> None:
        self.assertEqual(
            native_contract.SUPPORTED_REPLAY_BRANCHES,
            (MILESTONE_BRANCH, EXCEPTION_BRANCH, "main"),
        )
        validate_repository_trace(self.root, self.source)
        _run(self.root, "switch", "-c", EXCEPTION_BRANCH)
        self._synchronize_remote()
        validate_repository_trace(self.root, self.source)
        _run(self.root, "switch", "-c", "main")
        self._synchronize_remote()
        validate_repository_trace(self.root, self.source)

    def test_scientific_fingerprint_excludes_only_trace_mechanics(self) -> None:
        historical = _historical(NATIVE_MODULE_PATH).decode("utf-8")
        current = Path(native_contract.__file__).read_text(encoding="utf-8")
        expected = _scientific_source_fingerprint(historical, "historical")
        self.assertEqual(expected, _scientific_source_fingerprint(current, "current"))
        mutations = (
            historical + "\nSCIENTIFIC_DRIFT = 1\n",
            current.replace(
                f'NATIVE_CLI_PATH = "{NATIVE_CLI_PATH}"',
                'NATIVE_CLI_PATH = "burnlens/unrelated.py"',
            ),
            current.replace(
                f'NATIVE_MODULE_PATH = "{NATIVE_MODULE_PATH}"',
                'NATIVE_MODULE_PATH = globals()["ARCHIVE_SHA256"] = "0" * 64',
            ),
            current + "\nimport ast as np\n",
        )
        for index, mutated in enumerate(mutations):
            with self.subTest(index=index):
                self.assertNotEqual(
                    expected,
                    _scientific_source_fingerprint(mutated, f"drifted-{index}"),
                )
        with self.assertRaisesRegex(
            PetesLakeReferenceNativeContractError, "trace-function roster drifted"
        ):
            _scientific_source_fingerprint(
                current
                + "\ndef validate_repository_trace(repository_root, git_source_commit):\n"
                + "    return None\n",
                "duplicate-trace-function",
            )
        with self.assertRaisesRegex(
            PetesLakeReferenceNativeContractError, "trace-function definition is unsafe"
        ):
            _scientific_source_fingerprint(
                current.replace(
                    "*arguments: str, check: bool = True",
                    '*arguments: str, check: bool = globals()["ARCHIVE_SHA256"]',
                    1,
                ),
                "unsafe-trace-default",
            )

    def test_rejects_console_mapping_drift(self) -> None:
        _write(
            self.root,
            "pyproject.toml",
            _pyproject(version="0.45.0", target="burnlens.wrong:main", extra=True),
        )
        self._commit("drift console mapping")
        with self.assertRaisesRegex(
            PetesLakeReferenceNativeContractError, "console mapping drifted"
        ):
            validate_repository_trace(self.root, self.source)

    def test_rejects_checkout_attribute_drift(self) -> None:
        _write(self.root, ".gitattributes", _attributes(native_eol="crlf", extra=True))
        self._commit("drift native checkout attribute")
        with self.assertRaisesRegex(
            PetesLakeReferenceNativeContractError, "checkout attributes drifted"
        ):
            validate_repository_trace(self.root, self.source)

    def test_rejects_repository_local_attribute_override(self) -> None:
        _write(self.root, ".gitattributes", _attributes(native_eol="crlf", extra=True))
        self._commit("drift committed native checkout attribute")
        info_attributes = Path(
            _run(self.root, "rev-parse", "--git-path", "info/attributes").stdout.strip()
        )
        if not info_attributes.is_absolute():
            info_attributes = self.root / info_attributes
        info_attributes.parent.mkdir(parents=True, exist_ok=True)
        info_attributes.write_text(
            f"{NATIVE_MODULE_PATH} text eol=lf\n", encoding="utf-8"
        )
        with self.assertRaisesRegex(
            PetesLakeReferenceNativeContractError, "attribute overrides"
        ):
            validate_repository_trace(self.root, self.source)

    def test_rejects_immutable_cli_drift(self) -> None:
        cli = (self.root / NATIVE_CLI_PATH).read_bytes() + b"\n# drift\n"
        _write(self.root, NATIVE_CLI_PATH, cli)
        self._commit("drift native CLI")
        with self.assertRaisesRegex(
            PetesLakeReferenceNativeContractError, "source bytes differ"
        ):
            validate_repository_trace(self.root, self.source)

    def test_rejects_immutable_original_test_drift(self) -> None:
        test_source = (self.root / NATIVE_TEST_PATH).read_bytes() + b"\n# drift\n"
        _write(self.root, NATIVE_TEST_PATH, test_source)
        self._commit("drift original native-contract test")
        with self.assertRaisesRegex(
            PetesLakeReferenceNativeContractError, "source bytes differ"
        ):
            validate_repository_trace(self.root, self.source)

    def test_rejects_hidden_cli_checkout_drift(self) -> None:
        _run(self.root, "update-index", "--assume-unchanged", NATIVE_CLI_PATH)
        cli = (self.root / NATIVE_CLI_PATH).read_bytes() + b"\n# hidden drift\n"
        _write(self.root, NATIVE_CLI_PATH, cli)
        with self.assertRaisesRegex(
            PetesLakeReferenceNativeContractError, "CLI checkout bytes differ"
        ):
            validate_repository_trace(self.root, self.source)

    def test_rejects_executing_module_mismatch(self) -> None:
        module = (self.root / NATIVE_MODULE_PATH).read_bytes() + b"\n# trace-only drift\n"
        _write(self.root, NATIVE_MODULE_PATH, module)
        self._commit("drift executing module bytes")
        with self.assertRaisesRegex(
            PetesLakeReferenceNativeContractError, "executing native-contract module"
        ):
            validate_repository_trace(self.root, self.source)

    def test_rejects_hidden_module_or_pyproject_checkout_drift(self) -> None:
        _run(self.root, "update-index", "--assume-unchanged", NATIVE_MODULE_PATH)
        module = (self.root / NATIVE_MODULE_PATH).read_bytes() + b"\n# hidden trace drift\n"
        _write(self.root, NATIVE_MODULE_PATH, module)
        with self.assertRaisesRegex(
            PetesLakeReferenceNativeContractError, "module checkout bytes differ from HEAD"
        ):
            validate_repository_trace(self.root, self.source)

        _write(self.root, NATIVE_MODULE_PATH, Path(native_contract.__file__).read_bytes())
        _run(self.root, "update-index", "--no-assume-unchanged", NATIVE_MODULE_PATH)
        _run(self.root, "update-index", "--assume-unchanged", "pyproject.toml")
        _write(self.root, "pyproject.toml", _pyproject(version="0.45.1", extra=True))
        with self.assertRaisesRegex(
            PetesLakeReferenceNativeContractError, "pyproject checkout bytes differ from HEAD"
        ):
            validate_repository_trace(self.root, self.source)

    def test_rejects_unregistered_replay_branch(self) -> None:
        _run(self.root, "switch", "-c", "unregistered-replay")
        self._synchronize_remote()
        with self.assertRaisesRegex(
            PetesLakeReferenceNativeContractError, "branch identity drifted"
        ):
            validate_repository_trace(self.root, self.source)

    def test_rejects_squash_like_main_without_source_ancestry(self) -> None:
        tree = _run(self.root, "rev-parse", "HEAD^{tree}").stdout.strip()
        squash = _run(
            self.root,
            "commit-tree",
            tree,
            "-m",
            "squash-like main",
        ).stdout.strip()
        _run(self.root, "switch", "-C", "main", squash)
        _run(self.root, "push", "--force", "origin", "HEAD:refs/heads/main")
        with self.assertRaisesRegex(
            PetesLakeReferenceNativeContractError, "not an ancestor"
        ):
            validate_repository_trace(self.root, self.source)

    def test_rejects_dirty_or_non_remote_equal_state(self) -> None:
        _write(self.root, "untracked.txt", "retained dirty state\n")
        with self.assertRaisesRegex(
            PetesLakeReferenceNativeContractError, "worktree is not clean"
        ):
            validate_repository_trace(self.root, self.source)
        (self.root / "untracked.txt").unlink()

        _write(self.root, "pyproject.toml", _pyproject(version="0.45.1", extra=True))
        self._commit("unsynchronized descendant", synchronize=False)
        with self.assertRaisesRegex(
            PetesLakeReferenceNativeContractError, "not remote-equal"
        ):
            validate_repository_trace(self.root, self.source)


if __name__ == "__main__":
    unittest.main()
