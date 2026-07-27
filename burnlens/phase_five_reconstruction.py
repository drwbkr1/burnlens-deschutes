"""Prove the tracked Phase Four package reconstructs and rolls back exactly."""

from __future__ import annotations

import argparse
from hashlib import sha256
from html import escape
import importlib.metadata
import json
import os
from pathlib import Path
import re
import subprocess
import tomllib
from typing import Any

import numpy as np
import rasterio

from burnlens.phase_four_package import _archive, validate_package


PACKAGE_DIRECTORY = Path(
    "samples/runs/phase-four/burnlens-ward-creek-rbr-run-v0.1.0"
)
PACKAGE_ARCHIVE = Path(
    "portfolio/phase-four/BURNLENS-WARD-CREEK-RBR-RUN-2026-001.zip"
)
CONTRACT_PATH = Path(
    "records/phase-five/contracts/"
    "PHASE-FIVE-QA-RELEASE-CONTRACT-2026-001.json"
)
ROLLBACK_TAG = "v0.54.0-rbr-geoint-milestone"
ROLLBACK_TAG_OBJECT = "4a7a54b7fea0cba3a1c7151630e7d4ecf2d8bf82"
ROLLBACK_COMMIT = "8660ccba893b7e3acfdc361e663a6b8d59d52a34"
ROLLBACK_ARCHIVE_SHA256 = (
    "91308a2ffe7095d89843edeb1634d6b1e972eb65bf1f67f38f1da0279102d84e"
)
RUN_ID_PATTERN = re.compile(
    r"^BL-2026-07-26-p5o1-t01-u05-clean-reconstruction-r[0-9]{3}$"
)
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")
FLOAT_LAYERS = {
    "rbr-score",
    "unet-probability-diagnostic",
}
BINARY_LAYERS = {
    "exclusion",
    "rbr-binary",
    "unet-binary-diagnostic",
}


class PhaseFiveReconstructionError(RuntimeError):
    """The clean reconstruction gate failed closed."""


def _sha256_bytes(payload: bytes) -> str:
    return sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(8 * 1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(
        "utf-8"
    )


def _write_new(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    created = False
    try:
        with path.open("xb") as stream:
            created = True
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        if path.read_bytes() != payload:
            raise PhaseFiveReconstructionError(
                f"output readback differs: {path}"
            )
    except Exception:
        if created and path.exists():
            path.unlink()
        raise


def _git(root: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", *arguments],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )
    if result.returncode != 0:
        raise PhaseFiveReconstructionError(
            f"git {' '.join(arguments)} failed ({result.returncode})"
        )
    return result.stdout.strip()


def _require_clean_source(root: Path, source_commit: str) -> dict[str, Any]:
    if not COMMIT_PATTERN.fullmatch(source_commit):
        raise PhaseFiveReconstructionError("source commit is invalid")
    head = _git(root, "rev-parse", "HEAD")
    if head != source_commit:
        raise PhaseFiveReconstructionError("source commit differs from HEAD")
    status = _git(root, "status", "--porcelain", "--untracked-files=all")
    if status:
        raise PhaseFiveReconstructionError("working tree is not clean")
    branch = _git(root, "branch", "--show-current")
    remote_ref = f"origin/{branch}" if branch else ""
    remote_commit = _git(root, "rev-parse", remote_ref) if remote_ref else None
    if remote_commit != source_commit:
        raise PhaseFiveReconstructionError(
            "clean source is not remote-equal on a named branch"
        )
    return {
        "branch": branch,
        "head": head,
        "remote_ref": remote_ref,
        "remote_commit": remote_commit,
        "status": "pass",
    }


def _binding_checks(root: Path) -> dict[str, Any]:
    contract = json.loads((root / CONTRACT_PATH).read_text(encoding="utf-8"))
    checked: list[dict[str, Any]] = []
    for binding in contract["frozen_release_bindings"]:
        path = root / binding["path"]
        if not path.is_file():
            raise PhaseFiveReconstructionError(
                f"frozen release binding missing: {binding['path']}"
            )
        actual = {
            "path": binding["path"],
            "bytes": path.stat().st_size,
            "sha256": _sha256_file(path),
        }
        if (
            actual["bytes"] != binding["bytes"]
            or actual["sha256"] != binding["sha256"]
        ):
            raise PhaseFiveReconstructionError(
                f"frozen release binding differs: {binding['path']}"
            )
        checked.append(actual)
    return {
        "contract_path": CONTRACT_PATH.as_posix(),
        "contract_sha256": _sha256_file(root / CONTRACT_PATH),
        "binding_count": len(checked),
        "bindings": checked,
        "status": "pass",
    }


def _tracked_files(package_root: Path) -> dict[str, bytes]:
    files = {
        path.relative_to(package_root).as_posix(): path.read_bytes()
        for path in package_root.rglob("*")
        if path.is_file()
    }
    if len(files) != 66:
        raise PhaseFiveReconstructionError(
            f"tracked package file count differs: {len(files)}"
        )
    return files


def _reconstruct_archive(
    root: Path, output_path: Path
) -> dict[str, Any]:
    files = _tracked_files(root / PACKAGE_DIRECTORY)
    payload = _archive(files)
    canonical = root / PACKAGE_ARCHIVE
    if payload != canonical.read_bytes():
        raise PhaseFiveReconstructionError(
            "reconstructed archive differs from canonical archive"
        )
    _write_new(output_path, payload)
    return {
        "source_directory": PACKAGE_DIRECTORY.as_posix(),
        "source_file_count": len(files),
        "output_path": output_path.as_posix(),
        "bytes": len(payload),
        "sha256": _sha256_bytes(payload),
        "canonical_path": PACKAGE_ARCHIVE.as_posix(),
        "canonical_sha256": _sha256_file(canonical),
        "byte_identical": True,
        "status": "pass",
    }


def _array_contracts(root: Path) -> dict[str, Any]:
    package = root / PACKAGE_DIRECTORY
    results: list[dict[str, Any]] = []
    for candidate in ("WCP-001", "WCP-002"):
        for layer in sorted(FLOAT_LAYERS | BINARY_LAYERS):
            array_path = (
                package
                / "evidence/u02-analysis/run/patches"
                / candidate
                / f"{layer}.npy"
            )
            raster_path = (
                package
                / "evidence/u03-geospatial/run/patches"
                / candidate
                / f"{layer}.tif"
            )
            array = np.load(array_path, allow_pickle=False)
            with rasterio.open(raster_path) as dataset:
                raster = dataset.read(1)
                crs = dataset.crs.to_string() if dataset.crs else None
                transform = tuple(float(value) for value in dataset.transform)
            if array.shape != (64, 64) or raster.shape != array.shape:
                raise PhaseFiveReconstructionError(
                    f"array shape differs: {candidate}/{layer}"
                )
            if layer in BINARY_LAYERS:
                equal = bool(np.array_equal(array, raster))
                maximum_absolute_difference = 0.0 if equal else None
                tolerance = 0.0
            else:
                difference = np.abs(
                    array.astype(np.float64) - raster.astype(np.float64)
                )
                maximum_absolute_difference = float(difference.max())
                tolerance = 1e-6
                equal = bool(
                    np.allclose(array, raster, rtol=0.0, atol=tolerance)
                )
            if not equal or crs != "EPSG:32610":
                raise PhaseFiveReconstructionError(
                    f"array/raster contract differs: {candidate}/{layer}"
                )
            results.append(
                {
                    "candidate_id": candidate,
                    "layer": layer,
                    "comparison": (
                        "exact" if layer in BINARY_LAYERS else "absolute"
                    ),
                    "tolerance": tolerance,
                    "maximum_absolute_difference": (
                        maximum_absolute_difference
                    ),
                    "crs": crs,
                    "transform": transform,
                    "status": "pass",
                }
            )
    return {
        "comparison_count": len(results),
        "comparisons": results,
        "status": "pass",
    }


def _semantic_contracts(root: Path) -> dict[str, Any]:
    package = root / PACKAGE_DIRECTORY
    status = json.loads(
        (package / "status/STATUS.json").read_text(encoding="utf-8")
    )
    summary = json.loads(
        (
            package
            / "evidence/u05-overlay/run/analysis/OVERLAY-SUMMARY.json"
        ).read_text(encoding="utf-8")
    )
    patches = summary["metrics"]["patches"]
    expected = {
        "WCP-001": {
            "accepted_rbr_area_ha": 141.44,
            "accepted_rbr_inside_mtbs_pct": 94.19,
        },
        "WCP-002": {
            "accepted_rbr_area_ha": 66.76,
            "accepted_rbr_inside_mtbs_pct": 0.0,
        },
    }
    observed = {
        candidate: {
            key: patches[candidate][key] for key in values
        }
        for candidate, values in expected.items()
    }
    if observed != expected:
        raise PhaseFiveReconstructionError("overlay semantic values differ")
    required_status = {
        "state": "accepted-baseline",
        "accepted_method": "burnlens-baseline-v0.1.0",
        "rejected_diagnostic": "burnlens-unet-binary-v0.1.0",
        "model_accepted": False,
        "model_outperformed_rbr": False,
        "phase_3b_created": False,
        "second_experiment_planned": False,
        "deployment": False,
        "external_requests": False,
    }
    if any(status.get(key) != value for key, value in required_status.items()):
        raise PhaseFiveReconstructionError("release semantic status differs")
    return {
        "accepted_method": status["accepted_method"],
        "rejected_diagnostic": status["rejected_diagnostic"],
        "model_accepted": status["model_accepted"],
        "model_outperformed_rbr": status["model_outperformed_rbr"],
        "observed_metrics": observed,
        "interpretation": (
            "Exact package observations retain bounded RBR evidence and the "
            "visible WCP-002 false-positive-risk result; they are not accuracy, "
            "ground-truth, field-validation, or operational claims."
        ),
        "status": "pass",
    }


def _installed_roster(root: Path) -> dict[str, Any]:
    with (root / "pyproject.toml").open("rb") as stream:
        project = tomllib.load(stream)["project"]
    expected = project["scripts"]
    distribution = importlib.metadata.distribution("burnlens-deschutes")
    installed = {
        item.name: item.value
        for item in distribution.entry_points
        if item.group == "console_scripts"
    }
    if installed != expected:
        raise PhaseFiveReconstructionError(
            "installed console-command roster differs from pyproject"
        )
    return {
        "software_version": project["version"],
        "distribution_version": distribution.version,
        "command_count": len(installed),
        "commands": sorted(installed),
        "targets_match": True,
        "help_execution": (
            "The clean-room and installed-wheel environment receipts execute "
            "every command help route separately."
        ),
        "status": "pass",
    }


def _rollback_identity(root: Path) -> dict[str, Any]:
    tag_type = _git(root, "cat-file", "-t", ROLLBACK_TAG)
    tag_object = _git(root, "rev-parse", ROLLBACK_TAG)
    peeled = _git(root, "rev-parse", f"{ROLLBACK_TAG}^{{}}")
    if (
        tag_type != "tag"
        or tag_object != ROLLBACK_TAG_OBJECT
        or peeled != ROLLBACK_COMMIT
    ):
        raise PhaseFiveReconstructionError("rollback tag identity differs")
    archive_at_tag = subprocess.run(
        ["git", "show", f"{ROLLBACK_TAG}:{PACKAGE_ARCHIVE.as_posix()}"],
        cwd=root,
        capture_output=True,
        check=False,
        timeout=60,
    )
    if archive_at_tag.returncode != 0:
        raise PhaseFiveReconstructionError(
            "rollback archive cannot be read from tag"
        )
    tag_archive_sha256 = _sha256_bytes(archive_at_tag.stdout)
    if tag_archive_sha256 != ROLLBACK_ARCHIVE_SHA256:
        raise PhaseFiveReconstructionError("rollback archive hash differs")
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", ROLLBACK_COMMIT, "HEAD"],
        cwd=root,
        capture_output=True,
        check=False,
        timeout=60,
    )
    if ancestor.returncode != 0:
        raise PhaseFiveReconstructionError(
            "rollback commit is not an ancestor of the candidate"
        )
    return {
        "tag": ROLLBACK_TAG,
        "tag_type": tag_type,
        "tag_object": tag_object,
        "peeled_commit": peeled,
        "archive_sha256_at_tag": tag_archive_sha256,
        "candidate_descends_from_rollback": True,
        "canonical_branch_moved": False,
        "status": "pass",
    }


def render_html(report: dict[str, Any]) -> bytes:
    semantic = report["checks"]["semantic_contracts"]
    reconstruction = report["checks"]["exact_archive_reconstruction"]
    rollback = report["checks"]["rollback_identity"]
    commands = report["checks"]["installed_roster"]
    rows = [
        ("Clean remote-equal source", report["checks"]["source"]["status"]),
        (
            "Frozen release bindings",
            report["checks"]["frozen_bindings"]["status"],
        ),
        (
            "Exact archive reconstruction",
            reconstruction["status"],
        ),
        ("Exact and tolerance array contracts", report["checks"]["arrays"]["status"]),
        ("Semantic release contracts", semantic["status"]),
        ("Installed command roster", commands["status"]),
        ("v0.54 rollback identity", rollback["status"]),
    ]
    table = "".join(
        f"<tr><th>{escape(label)}</th><td>{escape(value)}</td></tr>"
        for label, value in rows
    )
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; img-src data:">
<title>BurnLens Phase Five clean reconstruction</title>
<style>
:root {{ color-scheme: dark; font-family: system-ui, sans-serif; background:#0d1517; color:#eef7f4; }}
body {{ margin:0 auto; max-width:980px; padding:clamp(1rem,4vw,3rem); line-height:1.55; }}
.eyebrow {{ color:#92d6c4; text-transform:uppercase; letter-spacing:.08em; font-weight:700; }}
h1 {{ line-height:1.08; max-width:18ch; }}
.card {{ background:#142326; border:1px solid #315055; border-radius:14px; padding:1rem 1.2rem; margin:1rem 0; }}
.pass {{ color:#9ee7b5; font-weight:800; }}
table {{ border-collapse:collapse; width:100%; }}
th,td {{ border-bottom:1px solid #315055; padding:.7rem; text-align:left; vertical-align:top; }}
code {{ overflow-wrap:anywhere; color:#b8e9dc; }}
@media (max-width:520px) {{ th,td {{ display:block; }} th {{ border-bottom:0; padding-bottom:.1rem; }} td {{ padding-top:.1rem; }} }}
</style>
</head>
<body>
<p class="eyebrow">P5O1-T01-U05 · clean reconstruction and rollback</p>
<h1>Exact package bytes and release meaning survive a clean checkout.</h1>
<div class="card">
<p class="pass">Disposition: {escape(report["disposition"])}</p>
<p>Tracked package files rebuild the {reconstruction["bytes"]:,}-byte archive byte-for-byte at <code>{escape(reconstruction["sha256"])}</code>.</p>
<p>The accepted method remains RBR. The trained U-Net remains a rejected diagnostic and did not outperform RBR.</p>
</div>
<div class="card"><h2>Gate results</h2><table>{table}</table></div>
<div class="card">
<h2>Release and rollback identity</h2>
<p>Candidate source: <code>{escape(report["git_source_commit"])}</code></p>
<p>Installed software version: <code>{escape(commands["software_version"])}</code>; exact console-command roster: {commands["command_count"]}.</p>
<p>Rollback tag <code>{escape(rollback["tag"])}</code> is annotated object <code>{escape(rollback["tag_object"])}</code> and peels to <code>{escape(rollback["peeled_commit"])}</code>.</p>
</div>
<div class="card">
<h2>Visible limitations</h2>
<ul>
<li>This reconstructs the immutable tracked package and verifies exact, tolerance, and semantic contracts. It does not retrain or retune any analytical method.</li>
<li>WCP-002 remains visible false-positive-risk evidence for RBR.</li>
<li>No accuracy, independent-ground-truth, field-validation, official, operational, endorsed, emergency-ready, or model-superiority claim is made.</li>
<li>The current branch is a commit-bound Phase Five candidate until U06 freezes a release identity; it is not a new v0.54 release.</li>
</ul>
</div>
</body>
</html>
"""
    return html.encode("utf-8")


def run(
    *,
    repository_root: Path,
    output_directory: Path,
    run_id: str,
    git_source_commit: str,
) -> dict[str, Any]:
    if not RUN_ID_PATTERN.fullmatch(run_id):
        raise PhaseFiveReconstructionError("run ID differs from U05 contract")
    root = repository_root.resolve()
    output = output_directory.resolve()
    output.mkdir(parents=True, exist_ok=True)
    archive_path = output / "reconstructed-phase-four-package.zip"
    checks = {
        "source": _require_clean_source(root, git_source_commit),
        "frozen_bindings": _binding_checks(root),
        "exact_archive_reconstruction": _reconstruct_archive(
            root, archive_path
        ),
        "arrays": _array_contracts(root),
        "semantic_contracts": _semantic_contracts(root),
        "installed_roster": _installed_roster(root),
        "rollback_identity": _rollback_identity(root),
    }
    validation = {
        "directory": validate_package(root / PACKAGE_DIRECTORY),
        "canonical_archive": validate_package(root / PACKAGE_ARCHIVE),
        "reconstructed_archive": validate_package(archive_path),
    }
    if any(
        item.get("result") != "PACKAGE_VALIDATION_PASS"
        for item in validation.values()
    ):
        raise PhaseFiveReconstructionError("package validation did not pass")
    report = {
        "report_version": "burnlens-phase-five-reconstruction-v0.1.0",
        "report_id": "PHASE-FIVE-CLEAN-RECONSTRUCTION-2026-001",
        "milestone_id": "P5O1-T01",
        "unit_id": "P5O1-T01-U05",
        "issue": 574,
        "run_id": run_id,
        "git_source_commit": git_source_commit,
        "route": "baseline-primary-with-rejected-model-diagnostic",
        "checks": checks,
        "package_validation": validation,
        "boundaries": {
            "analytical_output_changed": False,
            "dataset_changed": False,
            "split_changed": False,
            "threshold_changed": False,
            "model_accepted": False,
            "model_outperformed_rbr": False,
            "phase_3b_created": False,
            "second_experiment_planned": False,
            "deployment": False,
            "public_sharing_change": False,
            "burnlens_site_used": False,
        },
        "limitations": [
            "This is tracked-package reconstruction, not analytical retraining.",
            "The clean checkout intentionally does not contain ignored provider or intermediate custody.",
            "Full installed-command help evidence and the detached rollback exercise are recorded by the surrounding U05 clean-room run.",
            "The current branch remains a commit-bound candidate until U06 freezes a release identity.",
        ],
        "disposition": "pass-pending-environment-and-detached-rollback-receipts",
        "next_dependency": (
            "P5O1-T01-U05 clean environment, installed-wheel, and detached "
            "rollback receipts"
        ),
    }
    report_path = output / "PHASE-FIVE-CLEAN-RECONSTRUCTION-2026-001.json"
    html_path = output / "PHASE-FIVE-CLEAN-RECONSTRUCTION-2026-001.html"
    _write_new(report_path, _json_bytes(report))
    _write_new(html_path, render_html(report))
    return {
        "report": report,
        "report_path": report_path,
        "html_path": html_path,
        "archive_path": archive_path,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = run(
        repository_root=args.repository_root,
        output_directory=args.output_directory,
        run_id=args.run_id,
        git_source_commit=args.git_source_commit,
    )
    print("PHASE_FIVE_RECONSTRUCTION_PASS")
    print(f"REPORT={result['report_path']}")
    print(f"HTML={result['html_path']}")
    print(f"ARCHIVE={result['archive_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
