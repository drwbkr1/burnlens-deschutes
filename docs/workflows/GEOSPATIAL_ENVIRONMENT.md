# BurnLens geospatial environment

## Outcome

BurnLens has one reproducible Windows development environment for ordinary
repository work and an opt-in geospatial research profile for source scouting,
archive inspection, CRS work, raster/vector QA, and small exploratory
transformations. The project metadata pins every direct dependency, `uv.lock`
freezes the resolved dependency graph, and `.python-version` fixes the managed
Python interpreter at 3.12.10, the installed project interpreter verified for
this Windows host.

The package metadata now declares Python 3.12 or newer because the canonical
NumPy 2.5.1 dependency already requires Python 3.12; the former `>=3.11`
declaration was not installable as written.

The locked baseline also advances Pillow to 12.3.0 and the development runner
to pytest 9.0.3. A dependency audit found disclosed issues in the former
Pillow 12.2.0 and pytest 8.4.2 pins; these are the first fixed releases named
by that audit and must pass the complete BurnLens regression before handoff.
The package metadata also binds the repository's existing MIT `LICENSE`, so
installed-distribution license scans no longer report BurnLens itself as
unknown.

This environment improves execution speed and repeatability. It does not
approve a source, authorize a download, establish licensing, promote a label,
accept a dataset, define a split, or authorize model work. All BurnLens source,
custody, uncertainty, leakage, and human-review gates continue to apply.

## Profiles

| Profile | Contents | Intended use |
|---|---|---|
| `runtime` | BurnLens plus its five canonical runtime dependencies | Running shipped evidence commands with the smallest dependency surface |
| `dev` | `runtime` plus the pinned test runner | Repository implementation and regression testing |
| `geo-research` | `dev` plus GeoPandas, Pyogrio, PyProj, Shapely, PySTAC Client, Xarray, Rioxarray, and Boto3 | Official-source scouting and local geospatial inspection before controlled intake |

The geospatial profile deliberately omits notebooks, distributed computation,
database servers, desktop GIS, cloud credentials, and provider-specific secret
configuration. Those should be added only when a concrete evidence unit needs
them.

## Codex worktrees

The checked-in local environment is
`.codex/environments/geospatial.toml`. It is intentionally Windows-only because
the current BurnLens operator environment and repository setup entry point use
Windows PowerShell. Select **BurnLens geospatial research (Windows)** when
starting a Codex worktree. Codex then runs the repository setup script in that
new worktree and exposes actions for the offline environment check and the test
suite.

Codex-created worktrees run the selected setup automatically. A manually
created worktree can be prepared with the same repository-owned command:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File scripts/setup_worktree.ps1 `
  -Profile geo-research
```

The script:

1. confirms it is running at the current Git worktree root;
2. requires the checked-in `uv.lock` and an installed `uv` executable;
3. refuses to replace an existing `.venv` whose interpreter is missing or does
   not match the Python pin;
4. holds a per-worktree mutex so concurrent profile setup fails instead of
   racing over one `.venv`;
5. refuses a stale lock and synchronizes `.venv` from the checked-in lock
   without changing tracked files;
6. runs dependency integrity and matching offline functional verification; and
7. fails nonzero if Python, the BurnLens package version, a direct dependency,
   a raster operation, or a
   geospatial operation is wrong.

It never searches for, copies, prints, or imports credentials. Provider access
remains in the existing secret-safe acquisition wrappers.

## Manual commands

Prepare the lean development profile:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File scripts/setup_worktree.ps1 `
  -Profile dev
```

Rerun the geospatial check without changing the environment:

```powershell
.\.venv\Scripts\python.exe scripts\verify_environment.py `
  --profile geo-research
```

The check is network-free. It verifies exact direct package versions, an
in-memory GeoTIFF, HDF5 and image primitives, UTM-to-WGS84 transformation, a
GeoPackage round trip, a disk GeoTIFF opened through Rioxarray, and offline
STAC/AWS client construction. Temporary files are removed at exit.

Run repository tests:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## Updating the environment

Dependency updates are intentional repository changes:

1. update the exact direct pin in `pyproject.toml`;
2. run `uv lock` from the repository root;
3. rerun `scripts/setup_worktree.ps1 -Profile geo-research` in a clean
   worktree;
4. run the full test suite and `uv lock --check`; and
5. run `uvx pip-audit --path .\.venv\Lib\site-packages --skip-editable`; and
6. commit `pyproject.toml` and `uv.lock` together with the verification record.

Do not run an unlocked install in an evidence workflow. Do not copy `.venv`
between worktrees. The lock provides a reproducible package graph; the smoke
check provides platform-level evidence that the installed binary wheels and
their GDAL/PROJ/GEOS components actually work on the current machine.
