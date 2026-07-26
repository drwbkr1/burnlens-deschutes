# BurnLens bounded-model environment

## Outcome

BurnLens has one opt-in Windows CPU profile for the bounded U-Net milestone.
The profile binds CPython 3.12.10, PyTorch 2.13.0, setuptools 82.0.0, the
existing runtime dependencies, and the development test runner through
`pyproject.toml` and `uv.lock`. It does not authorize a second model,
architecture or hyperparameter search, GPU execution, augmentation, test
tuning, deployment, or any dataset, split, label, normalization, or baseline
change.

The model profile is separate from `geo-research`. Model training needs the
accepted native-grid NumPy arrays and ordinary raster/runtime packages, not the
optional source-scouting stack. A development checkout may synchronize both
profiles for the complete regression suite, but a clean model reproduction
must prove the smaller `model-research` profile by itself.

## Locked distribution and execution boundary

The Windows CPython 3.12 lock selects:

- `torch-2.13.0-cp312-cp312-win_amd64.whl`;
- 122,057,313 bytes;
- SHA-256 `024c6cc0c1b085f2f91f20a3dc27b0471d021c31ce84b81be3afdc39f791fd9d`;
- PyTorch runtime `2.13.0+cpu`; and
- setuptools `82.0.0`, as frozen by the Phase Two training contract.

The repository verifier refuses a different direct dependency version. Its
model check runs entirely offline, requires `torch.cuda.is_available()` to be
false, enables deterministic algorithms with `warn_only=False`, fixes intra-op
and inter-op threads to one, and requires two synthetic CPU convolutions to be
byte-identical and finite. The synthetic tensor is not a BurnLens dataset
sample and the verifier never opens train, validation, or test arrays.

PyTorch documents determinism as environment-specific: identical seeds and
deterministic algorithms do not establish cross-release or cross-platform
reproducibility. BurnLens therefore requires exact replay only on the same
locked Windows CPU environment and makes no cross-platform exactness claim.

## Setup and verification

Codex worktrees can select **BurnLens bounded U-Net research (Windows CPU)**,
which runs:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File scripts/setup_worktree.ps1 `
  -Profile model-research
```

Manual verification is:

```powershell
uv lock --check
uv pip check --python .\.venv\Scripts\python.exe
.\.venv\Scripts\python.exe scripts\verify_environment.py `
  --profile model-research
.\.venv\Scripts\python.exe -m pytest -q tests\test_environment_profiles.py
```

`setup_worktree.ps1` retains the existing repository-root, Python-pin,
stale-lock, wrong/incomplete-environment, and per-worktree mutex gates. It uses
`uv sync --locked --extra dev --extra model`, then runs dependency integrity
and the offline model smoke.

## Security disposition

The required setuptools 82.0.0 pin is reported by `pip-audit` under
GHSA-h35f-9h28-mq5c / CVE-2026-59890. The advisory concerns Unicode
normalization bypasses in `MANIFEST.in` exclusions while building source
distributions on normalization-preserving macOS filesystems. This milestone
uses Windows/NTFS, has no `MANIFEST.in`, has no tracked non-ASCII or non-NFC
path, and neither builds nor publishes an sdist. Those controls make the
reported path inapplicable to this checkpoint; the audit is still recorded as
a disclosed finding rather than reported as vulnerability-free.

If BurnLens later builds an sdist, moves the evidence environment to macOS, or
introduces a manifest exclusion, model execution must stop until the training
contract is intentionally amended to a fixed setuptools release or an
equivalent reviewed mitigation is in place.
