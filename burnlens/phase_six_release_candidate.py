"""Build and validate the deterministic Phase Six pre-publication package."""

from __future__ import annotations

import argparse
from collections import deque
from hashlib import sha256
import html
import io
import json
from pathlib import Path, PurePosixPath
import posixpath
import re
import subprocess
from typing import Any
from urllib.parse import unquote, urlsplit
import zipfile


PACKAGE_VERSION = "burnlens-phase-six-baseline-first-candidate-v0.1.0"
PACKAGE_ID = "BURNLENS-PHASE-SIX-BASELINE-FIRST-CANDIDATE-2026-001"
ARCHIVE_NAME = f"{PACKAGE_ID}.zip"
RECEIPT_NAME = f"{PACKAGE_ID}-RECEIPT.json"
SOFTWARE_VERSION = "0.56.0"
ROUTE = "baseline-primary-with-rejected-model-diagnostic"
ACCEPTED_METHOD = "burnlens-baseline-v0.1.0"
REJECTED_MODEL = "burnlens-unet-binary-v0.1.0"
DATASET_VERSION = "burnlens-dataset-v0.1.0"
SPLIT_VERSION = "burnlens-whole-event-split-v0.1.0"
LABEL_SCHEMA_VERSION = "burn-scar-binary-region-label-schema-v0.3.0"
LABEL_SET_VERSION = "owner-approved-prototype-region-labels-v0.5.0"
AOI_VERSION = "aoi-darlene3-model-v0.2.0"
ACCEPTED_RUN_ID = "BL-2026-07-26-p4o1-t01-u07-package-r001"
FIXED_ZIP_DATETIME = (2026, 1, 1, 0, 0, 0)
MAX_ARCHIVE_BYTES = 25_000_000
MAX_EXTRACTED_BYTES = 30_000_000
MAX_ARCHIVE_MEMBERS = 160
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")
RUN_ID_PATTERN = re.compile(
    r"^BL-[0-9]{4}-[0-9]{2}-[0-9]{2}-p6o1-t01-u05-"
    r"pre-publication-package-r[0-9]{3}$"
)
HTML_LINK_PATTERN = re.compile(
    r"""(?:href|src)\s*=\s*["']([^"'<>]+)["']""",
    flags=re.IGNORECASE,
)
MARKDOWN_LINK_PATTERN = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
PHASE_FIVE_DIRECTORY = (
    "samples/runs/phase-five/"
    "burnlens-phase-five-baseline-first-candidate-v0.1.1"
)
CANONICAL_ENTRYPOINT = (
    "samples/runs/phase-six/"
    "burnlens-baseline-first-portfolio-surface-v0.1.0/index.html"
)
PRESENTATION_PATH = (
    "portfolio/phase-six/"
    "BURNLENS-BASELINE-FIRST-PRESENTATION-2026-001.html"
)
REVIEWER_JOURNEY_PATH = "docs/phase-six/REVIEWER_JOURNEY.md"
CASE_STUDY_PATH = "docs/case-study/BURNLENS_CASE_STUDY.md"
LINK_CLOSURE_SEEDS = (
    CANONICAL_ENTRYPOINT,
    PRESENTATION_PATH,
    REVIEWER_JOURNEY_PATH,
    CASE_STUDY_PATH,
)

PINNED_SOURCES = (
    (
        CANONICAL_ENTRYPOINT,
        14798,
        "f0fb4b57f3be1ae9690b2252c3ecd9f0a7e125bd6e67ce8b0f4f242752cb09f8",
    ),
    (
        "samples/runs/phase-six/"
        "burnlens-baseline-first-portfolio-surface-v0.1.0/MANIFEST.json",
        6247,
        "31c68cd8e7fc1ac4d9a5ef82c0701bbfd8b50feb202b84d9f6bf62fdf977d7c1",
    ),
    (
        "samples/runs/phase-six/"
        "burnlens-baseline-first-portfolio-surface-v0.1.0/README.md",
        859,
        "c8cee600712f963649655cfe91ab4dcb1971a02808a7d9d3cd94a3deaf5f095f",
    ),
    (
        REVIEWER_JOURNEY_PATH,
        10842,
        "74b072903c56603e390803a1eea0e1f72a2a9f019c8d2ee5a946941e645bee3f",
    ),
    (
        CASE_STUDY_PATH,
        104961,
        "2ed82149759b7aed11634e73476b835bdc7604e88ac848aa1929ed0427947c54",
    ),
    (
        "docs/phase-six/DEMO_SCRIPT.md",
        3925,
        "b95d12e4aaf3501030af944f356a48c23f7e32fcee004366c43eee14cd4ca558",
    ),
    (
        "docs/phase-six/CLAIM_MATRIX.md",
        4122,
        "2ac5280f7783688e73edbd21703b5b9d61810f589ad7c5635b7837e57e7ac54a",
    ),
    (
        "docs/phase-six/MAINTENANCE_AND_ARCHIVE.md",
        4132,
        "8389e0c2e4762b90596f369be9f23cc17ef7b862b89b2879834933d2b6a31c7a",
    ),
    (
        PRESENTATION_PATH,
        11203,
        "5b16c00d1bee7dd0ef5302bc1a0aeb61fd60a4756b214dc6517630722c0b8e98",
    ),
    (
        "portfolio/phase-six/CITATION.json",
        3001,
        "ea5b51ef442bb169353ee3c245413ff55cb2d71a16e6aa7a0b7ac4b8af13777a",
    ),
    (
        "portfolio/phase-six/CITATION.md",
        1002,
        "f9595d7a9f8093bda6f2d68b7a2aa4510134a7ab6e1a0b06980849809cea5710",
    ),
    (
        "samples/runs/phase-four/"
        "burnlens-geoint-evidence-interface-v0.1.0/"
        "PHASE-FOUR-EVIDENCE-INTERFACE-2026-001.html",
        177666,
        "7a657ad772b34ff42cf4f4024a585b70fb8e7f41bab363cd056fcf8059825fb7",
    ),
    (
        "samples/model-packages/burnlens-unet-binary-v0.1.0/"
        "PHASE-THREE-MODEL-DECISION.html",
        3981,
        "36986bcfa4ab22ded2ed7b736730a769f2223fdaf70318e1b5bf60e537aafc1e",
    ),
    (
        "samples/baselines/burnlens-baseline-v0.1.0/"
        "BASELINE-EVALUATION-2026-001.html",
        3921,
        "109075ca31cb1c01137bdccff5786c862105eb15dc1cbe15c8603dcf3d15fd99",
    ),
    (
        "portfolio/phase-four/BURNLENS-WARD-CREEK-RBR-RUN-2026-001.zip",
        487893,
        "91308a2ffe7095d89843edeb1634d6b1e972eb65bf1f67f38f1da0279102d84e",
    ),
    (
        "portfolio/phase-five/"
        "BURNLENS-PHASE-FIVE-BASELINE-FIRST-CANDIDATE-2026-002.zip",
        646513,
        "691c4bddb6754d74ca858a0b801fb21e62103032184425d2ba1b1648df1b0c26",
    ),
    (
        "LICENSE",
        1067,
        "accec00dfaedd030895e2c9cd0c7038380265fec320e6d94429ee1978ebd97d8",
    ),
)


class PhaseSixCandidateError(RuntimeError):
    """The Phase Six candidate build or validation failed."""


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


def _load_json_bytes(payload: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PhaseSixCandidateError(f"invalid JSON: {label}") from exc
    if not isinstance(value, dict):
        raise PhaseSixCandidateError(f"JSON root must be object: {label}")
    return value


def _safe_repository_file(repository_root: Path, relative: str) -> Path:
    pure = PurePosixPath(relative)
    if pure.is_absolute() or ".." in pure.parts or not pure.parts:
        raise PhaseSixCandidateError(f"unsafe repository path: {relative}")
    path = repository_root.joinpath(*pure.parts)
    if not path.is_file() or path.is_symlink():
        raise PhaseSixCandidateError(f"missing or linked source: {relative}")
    try:
        path.resolve().relative_to(repository_root.resolve())
    except ValueError as exc:
        raise PhaseSixCandidateError(
            f"source escapes repository: {relative}"
        ) from exc
    return path


def _tracked_paths(repository_root: Path) -> set[str]:
    try:
        completed = subprocess.run(
            ["git", "ls-files", "-z"],
            cwd=repository_root,
            check=True,
            capture_output=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise PhaseSixCandidateError("unable to verify tracked source roster") from exc
    return {
        item.decode("utf-8").replace("\\", "/")
        for item in completed.stdout.split(b"\0")
        if item
    }


def _local_link_target(source_path: str, raw_target: str) -> str | None:
    target = html.unescape(raw_target.strip())
    if not target or target.startswith("#"):
        return None
    parsed = urlsplit(target)
    if parsed.scheme == "data":
        return None
    if parsed.scheme == "file":
        raise PhaseSixCandidateError(
            f"file locator in package source {source_path}: {raw_target}"
        )
    if parsed.scheme or parsed.netloc:
        return None
    if not parsed.path:
        return None
    decoded = unquote(parsed.path).replace("\\", "/")
    if decoded.startswith("/"):
        raise PhaseSixCandidateError(
            f"root-absolute package link in {source_path}: {raw_target}"
        )
    normalized = posixpath.normpath(
        posixpath.join(posixpath.dirname(source_path), decoded)
    )
    pure = PurePosixPath(normalized)
    if normalized in {"", "."} or pure.is_absolute() or ".." in pure.parts:
        raise PhaseSixCandidateError(
            f"package link escapes root in {source_path}: {raw_target}"
        )
    return pure.as_posix()


def _link_targets(source_path: str, payload: bytes) -> list[str]:
    suffix = PurePosixPath(source_path).suffix.lower()
    if suffix not in {".html", ".md"}:
        return []
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise PhaseSixCandidateError(
            f"invalid UTF-8 review source: {source_path}"
        ) from exc
    pattern = HTML_LINK_PATTERN if suffix == ".html" else MARKDOWN_LINK_PATTERN
    targets: list[str] = []
    for match in pattern.finditer(text):
        target = _local_link_target(source_path, match.group(1))
        if target is not None:
            targets.append(target)
    return targets


def _verify_pinned_sources(repository_root: Path) -> None:
    for relative, expected_bytes, expected_sha256 in PINNED_SOURCES:
        path = _safe_repository_file(repository_root, relative)
        if path.stat().st_size != expected_bytes:
            raise PhaseSixCandidateError(
                f"pinned source byte mismatch: {relative}"
            )
        if _sha256_file(path) != expected_sha256:
            raise PhaseSixCandidateError(
                f"pinned source hash mismatch: {relative}"
            )


def _phase_five_roster(repository_root: Path) -> set[str]:
    directory = repository_root / PHASE_FIVE_DIRECTORY
    archive_path = (
        repository_root
        / "portfolio/phase-five/"
        "BURNLENS-PHASE-FIVE-BASELINE-FIRST-CANDIDATE-2026-002.zip"
    )
    prefix = "burnlens-phase-five-baseline-first-candidate-v0.1.1/"
    archive_files: dict[str, bytes] = {}
    try:
        with zipfile.ZipFile(archive_path) as archive:
            for info in archive.infolist():
                if info.is_dir() or not info.filename.startswith(prefix):
                    raise PhaseSixCandidateError(
                        "Phase Five archive roster mismatch"
                    )
                relative = info.filename[len(prefix) :]
                archive_files[relative] = archive.read(info)
            if archive.testzip() is not None:
                raise PhaseSixCandidateError("Phase Five archive CRC failure")
    except (zipfile.BadZipFile, OSError) as exc:
        raise PhaseSixCandidateError("invalid Phase Five archive") from exc
    directory_files = {
        path.relative_to(directory).as_posix(): path.read_bytes()
        for path in sorted(directory.rglob("*"))
        if path.is_file() and not path.is_symlink()
    }
    if directory_files != archive_files:
        raise PhaseSixCandidateError(
            "Phase Five directory/archive exact-byte mismatch"
        )
    return {
        f"{PHASE_FIVE_DIRECTORY}/{relative}"
        for relative in directory_files
    }


def _source_payloads(repository_root: Path) -> dict[str, bytes]:
    _verify_pinned_sources(repository_root)
    tracked = _tracked_paths(repository_root)
    selected = set(_phase_five_roster(repository_root))
    selected.update(relative for relative, _, _ in PINNED_SOURCES)
    queue: deque[str] = deque(LINK_CLOSURE_SEEDS)
    visited: set[str] = set()
    while queue:
        relative = queue.popleft()
        if relative in visited:
            continue
        visited.add(relative)
        path = _safe_repository_file(repository_root, relative)
        payload = path.read_bytes()
        selected.add(relative)
        for target in _link_targets(relative, payload):
            if target not in visited:
                queue.append(target)
    untracked = sorted(selected - tracked)
    if untracked:
        raise PhaseSixCandidateError(
            "package source is not tracked: " + ", ".join(untracked[:3])
        )
    return {
        relative: _safe_repository_file(repository_root, relative).read_bytes()
        for relative in sorted(selected)
    }


def _open_first(
    *,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> bytes:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'">
<title>Open BurnLens — Phase Six pre-publication candidate</title>
<style>
:root{{color-scheme:dark;font-family:system-ui,sans-serif;background:#081315;color:#edf7f4}}
*{{box-sizing:border-box}}
body{{margin:0 auto;max-width:980px;padding:clamp(1rem,5vw,4rem);line-height:1.55}}
.skip{{position:absolute;left:-9999px}}.skip:focus{{left:1rem;top:1rem;background:#fff;color:#000;padding:.75rem;z-index:2}}
.eyebrow{{color:#8edbc6;text-transform:uppercase;letter-spacing:.09em;font-weight:800}}
h1{{font-size:clamp(2rem,7vw,4.5rem);line-height:1.02;max-width:17ch;margin:.35rem 0 1rem}}
.lede{{font-size:1.15rem;max-width:70ch}}.grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1rem}}
.card{{background:#122427;border:1px solid #31545a;border-radius:14px;padding:1rem 1.2rem;margin:1rem 0}}
a{{color:#a5e5f1}}code{{overflow-wrap:anywhere;color:#b8eadc}}
.warning{{border-left:4px solid #f2bd63;padding-left:1rem;color:#ffe0a3}}
@media(max-width:680px){{.grid{{grid-template-columns:1fr}}}}
</style>
</head>
<body>
<a class="skip" href="#main">Skip to package guide</a>
<main id="main" tabindex="-1">
<p class="eyebrow">P6O1-T01-U05 · local pre-publication package</p>
<h1>BurnLens, baseline first and evidence visible.</h1>
<p class="lede">Start with the exact Phase Six reviewer surface. The accepted RBR result, rejected U-Net diagnostic, WCP-002 failure evidence, reliability record, case study, presentation, citation, and limitations are preserved without changing their bytes.</p>
<section class="card">
<h2>Open first</h2>
<p><a href="{CANONICAL_ENTRYPOINT}">Open the canonical BurnLens reviewer surface</a>.</p>
<p><a href="{PRESENTATION_PATH}">Open the seven-slide presentation</a>.</p>
</section>
<div class="grid">
<section class="card"><h2>Review paths</h2><ul>
<li><a href="{REVIEWER_JOURNEY_PATH}">30-second, 2-minute, and 5-minute reviewer journey</a></li>
<li><a href="{CASE_STUDY_PATH}">Full case study</a></li>
<li><a href="docs/phase-six/DEMO_SCRIPT.md">Fixed demo script</a></li>
</ul></section>
<section class="card"><h2>Trust and reuse</h2><ul>
<li><a href="docs/phase-six/CLAIM_MATRIX.md">Claim matrix</a></li>
<li><a href="KNOWN-ISSUES.md">Package known issues</a></li>
<li><a href="portfolio/phase-six/CITATION.md">Citation</a></li>
<li><a href="PACKAGE-MANIFEST.json">Manifest</a> and <a href="CHECKSUMS.sha256">checksums</a></li>
</ul></section>
</div>
<p class="warning"><strong>Use boundary:</strong> Experimental BurnLens CV output. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.</p>
<p>RBR remains accepted. The U-Net remains rejected and did not outperform RBR. Owner-approved prototype labels are not independent ground truth. This local package is not a GitHub Release, deployment, publication, public-sharing change, or external submission.</p>
<p><small>Run <code>{html.escape(run_id)}</code> · source <code>{html.escape(git_source_commit)}</code> · generated <code>{html.escape(generated_at_utc)}</code>.</small></p>
</main>
</body>
</html>
""".encode("utf-8")


def _readme(
    *,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> bytes:
    return f"""# BurnLens Phase Six pre-publication candidate

Package: `{PACKAGE_VERSION}`

Software: `{SOFTWARE_VERSION}`

Run: `{run_id}`

Source commit: `{git_source_commit}`

Generated: `{generated_at_utc}`

Open `OPEN-FIRST.html`, then use the canonical Phase Six reviewer surface. The
package preserves repository-relative paths and includes the complete link
closure for the reviewer journey and case study plus the exact validated Phase
Five directory.

RBR is the accepted analytical method for one bounded Ward Creek
demonstration. The trained U-Net is a rejected diagnostic and did not
outperform RBR. WCP-002 remains visible false-positive-risk evidence.

Read `KNOWN-ISSUES.md`, `PACKAGE-MANIFEST.json`, and `CHECKSUMS.sha256`.

This is a deterministic local pre-publication package. It is not official
wildfire information, emergency guidance, independent ground truth, field
validation, generalization evidence, an operational system, a deployment, a
GitHub Release, a publication, a public-sharing change, or an external
submission.
""".encode("utf-8")


def _known_issues() -> bytes:
    return (
        "# BurnLens Phase Six package known issues\n\n"
        "This package preserves, rather than resolves or hides, the exact "
        "Phase Five known-issues register at "
        f"`{PHASE_FIVE_DIRECTORY}/KNOWN-ISSUES.md`.\n\n"
        "## Current interpretation limits\n\n"
        "- RBR remains accepted only for one bounded Ward Creek "
        "demonstration. WCP-002 remains visible false-positive-risk "
        "evidence.\n"
        "- The trained U-Net is reproducible but rejected. It predicted all "
        "89 selected test cores burned and did not outperform RBR.\n"
        "- Owner-approved prototype labels are not independent ground truth, "
        "inter-rater agreement, or field validation.\n"
        "- Twelve balanced patches and 89 selected test cores do not estimate "
        "natural prevalence or generalization.\n"
        "- Repository-linked Markdown is included for offline review. Browser "
        "rendering of Markdown depends on the recipient's local viewer; the "
        "canonical HTML surfaces require no script or external asset.\n"
        "- The package is local and pre-publication. It creates no deployment, "
        "GitHub Release, domain, access, ownership, public-sharing, "
        "publication, or external-submission change.\n\n"
        "## Required source precedence\n\n"
        "Official sources govern. BurnLens outputs are experimental portfolio "
        "evidence and are not emergency, evacuation, routing, tactical, "
        "incident-command, property, insurance, legal, or regulatory "
        "guidance.\n"
    ).encode("utf-8")


def _manifest_entries(
    files: dict[str, bytes],
    source_paths: set[str],
) -> list[dict[str, Any]]:
    return [
        {
            "path": path,
            "bytes": len(payload),
            "sha256": _sha256_bytes(payload),
            "origin": (
                "repository-tracked-exact-byte"
                if path in source_paths
                else "u05-generated-package-control"
            ),
        }
        for path, payload in sorted(files.items())
    ]


def _archive(files: dict[str, bytes]) -> bytes:
    stream = io.BytesIO()
    with zipfile.ZipFile(
        stream,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
        strict_timestamps=True,
    ) as archive:
        for relative, payload in sorted(files.items()):
            info = zipfile.ZipInfo(
                f"{PACKAGE_VERSION}/{relative}",
                date_time=FIXED_ZIP_DATETIME,
            )
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, payload)
    return stream.getvalue()


def build_candidate(
    *,
    repository_root: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, Any]:
    if not generated_at_utc.endswith("Z"):
        raise PhaseSixCandidateError("generated_at_utc must end with Z")
    if not RUN_ID_PATTERN.fullmatch(run_id):
        raise PhaseSixCandidateError("invalid U05 run ID")
    if not COMMIT_PATTERN.fullmatch(git_source_commit):
        raise PhaseSixCandidateError("invalid Git source commit")
    source_files = _source_payloads(repository_root)
    files = dict(source_files)
    files.update(
        {
            "OPEN-FIRST.html": _open_first(
                generated_at_utc=generated_at_utc,
                run_id=run_id,
                git_source_commit=git_source_commit,
            ),
            "README.md": _readme(
                generated_at_utc=generated_at_utc,
                run_id=run_id,
                git_source_commit=git_source_commit,
            ),
            "KNOWN-ISSUES.md": _known_issues(),
        }
    )
    manifest = {
        "manifest_version": "burnlens-phase-six-candidate-manifest-v0.1.0",
        "package_id": PACKAGE_ID,
        "package_version": PACKAGE_VERSION,
        "software_version": SOFTWARE_VERSION,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "git_source_commit": git_source_commit,
        "state": "local-pre-publication-candidate",
        "route": ROUTE,
        "canonical_entrypoint": CANONICAL_ENTRYPOINT,
        "accepted_method": ACCEPTED_METHOD,
        "rejected_model": REJECTED_MODEL,
        "model_accepted": False,
        "model_outperformed_rbr": False,
        "public_action_authorized": False,
        "traceability": {
            "application_version": SOFTWARE_VERSION,
            "aoi_version": AOI_VERSION,
            "dataset_version": DATASET_VERSION,
            "split_version": SPLIT_VERSION,
            "label_schema_version": LABEL_SCHEMA_VERSION,
            "label_set_version": LABEL_SET_VERSION,
            "baseline_version": ACCEPTED_METHOD,
            "model_version": REJECTED_MODEL,
            "accepted_run_id": ACCEPTED_RUN_ID,
            "package_run_id": run_id,
            "git_source_commit": git_source_commit,
        },
        "attribution": [
            "Contains modified Copernicus Sentinel data 2019.",
            (
                "Map services and data available from U.S. Geological Survey, "
                "National Geospatial Program."
            ),
            (
                "Monitoring Trends in Burn Severity (MTBS), U.S. Geological "
                "Survey and USDA Forest Service."
            ),
        ],
        "closure": {
            "seed_paths": list(LINK_CLOSURE_SEEDS),
            "repository_source_files": len(source_files),
            "complete_local_link_closure": True,
            "complete_phase_five_directory": True,
        },
        "files": _manifest_entries(files, set(source_files)),
        "boundaries": {
            "analytical_output_changed": False,
            "dataset_split_label_threshold_or_source_changed": False,
            "model_decision_changed": False,
            "phase_3b_or_second_experiment": False,
            "provider_or_private_owner_response_included": False,
            "deployment": False,
            "github_release": False,
            "access_ownership_public_sharing_publication_or_submission_change": False,
        },
        "next_dependency": "P6O1-T01-U06 real rendered and recipient QA",
    }
    files["PACKAGE-MANIFEST.json"] = _json_bytes(manifest)
    files["CHECKSUMS.sha256"] = (
        "\n".join(
            f"{_sha256_bytes(payload)}  {path}"
            for path, payload in sorted(files.items())
        )
        + "\n"
    ).encode("utf-8")
    archive = _archive(files)
    extracted_bytes = sum(map(len, files.values()))
    if len(files) > MAX_ARCHIVE_MEMBERS:
        raise PhaseSixCandidateError("candidate member budget exceeded")
    if extracted_bytes > MAX_EXTRACTED_BYTES:
        raise PhaseSixCandidateError("candidate extracted-byte budget exceeded")
    if len(archive) > MAX_ARCHIVE_BYTES:
        raise PhaseSixCandidateError("candidate archive-byte budget exceeded")
    return {
        "files": files,
        "archive": archive,
        "manifest": manifest,
        "archive_bytes": len(archive),
        "archive_sha256": _sha256_bytes(archive),
        "extracted_bytes": extracted_bytes,
        "file_count": len(files),
        "repository_source_files": len(source_files),
    }


def _safe_archive_files(payload: bytes) -> dict[str, bytes]:
    try:
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            infos = archive.infolist()
            names = [info.filename for info in infos]
            if len(names) != len(set(names)):
                raise PhaseSixCandidateError("duplicate archive member")
            if len(names) > MAX_ARCHIVE_MEMBERS:
                raise PhaseSixCandidateError("archive member budget exceeded")
            prefix = f"{PACKAGE_VERSION}/"
            files: dict[str, bytes] = {}
            for info in infos:
                pure = PurePosixPath(info.filename)
                mode = (info.external_attr >> 16) & 0o170000
                if (
                    info.is_dir()
                    or info.flag_bits & 0x1
                    or pure.is_absolute()
                    or ".." in pure.parts
                    or not info.filename.startswith(prefix)
                    or mode not in {0, 0o100000}
                ):
                    raise PhaseSixCandidateError(
                        f"unsafe archive member: {info.filename}"
                    )
                relative = info.filename[len(prefix) :]
                if not relative:
                    raise PhaseSixCandidateError("empty archive member path")
                files[relative] = archive.read(info)
            if archive.testzip() is not None:
                raise PhaseSixCandidateError("archive CRC failure")
            return files
    except (zipfile.BadZipFile, RuntimeError, OSError) as exc:
        if isinstance(exc, PhaseSixCandidateError):
            raise
        raise PhaseSixCandidateError("unsafe or corrupt candidate archive") from exc


def _directory_files(root: Path) -> dict[str, bytes]:
    if not root.is_dir() or root.is_symlink():
        raise PhaseSixCandidateError("candidate directory is missing or linked")
    files: dict[str, bytes] = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise PhaseSixCandidateError(
                f"linked candidate member: {path.relative_to(root).as_posix()}"
            )
        if path.is_file():
            files[path.relative_to(root).as_posix()] = path.read_bytes()
    return files


def _validate_manifest_and_checksums(files: dict[str, bytes]) -> dict[str, Any]:
    required = {
        "OPEN-FIRST.html",
        "README.md",
        "KNOWN-ISSUES.md",
        "PACKAGE-MANIFEST.json",
        "CHECKSUMS.sha256",
        CANONICAL_ENTRYPOINT,
        PRESENTATION_PATH,
        "portfolio/phase-four/BURNLENS-WARD-CREEK-RBR-RUN-2026-001.zip",
        (
            "portfolio/phase-five/"
            "BURNLENS-PHASE-FIVE-BASELINE-FIRST-CANDIDATE-2026-002.zip"
        ),
    }
    if not required.issubset(files):
        raise PhaseSixCandidateError(
            "missing candidate members: "
            + ", ".join(sorted(required - set(files)))
        )
    manifest = _load_json_bytes(
        files["PACKAGE-MANIFEST.json"],
        "PACKAGE-MANIFEST.json",
    )
    expected = {
        "package_id": PACKAGE_ID,
        "package_version": PACKAGE_VERSION,
        "software_version": SOFTWARE_VERSION,
        "state": "local-pre-publication-candidate",
        "route": ROUTE,
        "canonical_entrypoint": CANONICAL_ENTRYPOINT,
        "accepted_method": ACCEPTED_METHOD,
        "rejected_model": REJECTED_MODEL,
        "model_accepted": False,
        "model_outperformed_rbr": False,
        "public_action_authorized": False,
    }
    for key, value in expected.items():
        if manifest.get(key) != value:
            raise PhaseSixCandidateError(
                f"candidate manifest binding mismatch: {key}"
            )
    if not RUN_ID_PATTERN.fullmatch(str(manifest.get("run_id", ""))):
        raise PhaseSixCandidateError("candidate manifest run ID mismatch")
    if not COMMIT_PATTERN.fullmatch(
        str(manifest.get("git_source_commit", ""))
    ):
        raise PhaseSixCandidateError("candidate manifest commit mismatch")
    entries = manifest.get("files")
    if not isinstance(entries, list):
        raise PhaseSixCandidateError("candidate manifest files missing")
    roster: dict[str, tuple[Any, Any]] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            raise PhaseSixCandidateError("invalid candidate manifest entry")
        relative = entry.get("path")
        if not isinstance(relative, str) or relative in roster:
            raise PhaseSixCandidateError("duplicate candidate manifest path")
        roster[relative] = (entry.get("bytes"), entry.get("sha256"))
    expected_paths = set(files) - {
        "PACKAGE-MANIFEST.json",
        "CHECKSUMS.sha256",
    }
    if set(roster) != expected_paths:
        raise PhaseSixCandidateError("candidate manifest roster mismatch")
    for relative, (expected_bytes, expected_sha256) in roster.items():
        payload = files[relative]
        if len(payload) != expected_bytes:
            raise PhaseSixCandidateError(
                f"candidate manifest byte mismatch: {relative}"
            )
        if _sha256_bytes(payload) != expected_sha256:
            raise PhaseSixCandidateError(
                f"candidate manifest hash mismatch: {relative}"
            )
    try:
        checksum_text = files["CHECKSUMS.sha256"].decode("utf-8")
    except UnicodeDecodeError as exc:
        raise PhaseSixCandidateError("invalid checksum encoding") from exc
    checksums: dict[str, str] = {}
    for line in checksum_text.splitlines():
        digest, separator, relative = line.partition("  ")
        if (
            not separator
            or not re.fullmatch(r"[0-9a-f]{64}", digest)
            or relative in checksums
        ):
            raise PhaseSixCandidateError("invalid checksum roster")
        checksums[relative] = digest
    if set(checksums) != set(files) - {"CHECKSUMS.sha256"}:
        raise PhaseSixCandidateError("checksum roster mismatch")
    for relative, expected_sha256 in checksums.items():
        if _sha256_bytes(files[relative]) != expected_sha256:
            raise PhaseSixCandidateError(f"checksum mismatch: {relative}")
    return manifest


def _validate_links(files: dict[str, bytes]) -> int:
    local_links = 0
    for relative, payload in sorted(files.items()):
        for target in _link_targets(relative, payload):
            local_links += 1
            if target not in files:
                raise PhaseSixCandidateError(
                    f"missing package link target from {relative}: {target}"
                )
    return local_links


def validate_candidate(path: Path) -> dict[str, Any]:
    if path.is_dir():
        files = _directory_files(path)
        archive_bytes = None
        archive_sha256 = None
    else:
        payload = path.read_bytes()
        if len(payload) > MAX_ARCHIVE_BYTES:
            raise PhaseSixCandidateError("candidate archive-byte budget exceeded")
        files = _safe_archive_files(payload)
        archive_bytes = len(payload)
        archive_sha256 = _sha256_bytes(payload)
    if len(files) > MAX_ARCHIVE_MEMBERS:
        raise PhaseSixCandidateError("candidate member budget exceeded")
    extracted_bytes = sum(map(len, files.values()))
    if extracted_bytes > MAX_EXTRACTED_BYTES:
        raise PhaseSixCandidateError("candidate extracted-byte budget exceeded")
    manifest = _validate_manifest_and_checksums(files)
    local_links = _validate_links(files)
    for relative, expected_bytes, expected_sha256 in PINNED_SOURCES:
        payload = files.get(relative)
        if payload is None:
            raise PhaseSixCandidateError(
                f"missing pinned package source: {relative}"
            )
        if len(payload) != expected_bytes:
            raise PhaseSixCandidateError(
                f"pinned package source byte mismatch: {relative}"
            )
        if _sha256_bytes(payload) != expected_sha256:
            raise PhaseSixCandidateError(
                f"pinned package source hash mismatch: {relative}"
            )
    for relative in files:
        lower = relative.lower()
        if (
            any(part in {"raw", "quarantine", "custody", "downloads"} for part in PurePosixPath(lower).parts)
            or lower.endswith((".pt", ".pth", ".onnx", ".ckpt", ".safetensors"))
        ):
            raise PhaseSixCandidateError(
                f"prohibited package member: {relative}"
            )
    serialized = b"\n".join(files.values()).lower()
    for forbidden in (
        b"c:\\users",
        b"c:\\projects",
        b"begin rsa private key",
        b"begin openssh private key",
        b"recipient retrieval url",
        b"owner-review-surface-2026-001-response",
    ):
        if forbidden in serialized:
            raise PhaseSixCandidateError(
                "candidate contains prohibited private material"
            )
    if b"model_outperformed_rbr\": true" in serialized:
        raise PhaseSixCandidateError("candidate promotes rejected model")
    return {
        "result": "PHASE_SIX_CANDIDATE_VALIDATION_PASS",
        "package_id": manifest["package_id"],
        "package_version": manifest["package_version"],
        "software_version": manifest["software_version"],
        "run_id": manifest["run_id"],
        "git_source_commit": manifest["git_source_commit"],
        "file_count": len(files),
        "extracted_bytes": extracted_bytes,
        "archive_bytes": archive_bytes,
        "archive_sha256": archive_sha256,
        "local_links": local_links,
        "public_action_authorized": manifest["public_action_authorized"],
        "next_dependency": manifest["next_dependency"],
    }


def write_candidate(
    *,
    repository_root: Path,
    output_root: Path,
    archive_root: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, Any]:
    for parent in (output_root, archive_root):
        try:
            parent.resolve().relative_to(repository_root.resolve())
        except ValueError as exc:
            raise PhaseSixCandidateError(
                "candidate output must remain inside the repository"
            ) from exc
    package_root = output_root / PACKAGE_VERSION
    archive_path = archive_root / ARCHIVE_NAME
    receipt_path = archive_root / RECEIPT_NAME
    for target in (package_root, archive_path, receipt_path):
        if target.exists():
            raise PhaseSixCandidateError(
                f"refusing to overwrite candidate output: {target}"
            )
    candidate = build_candidate(
        repository_root=repository_root,
        generated_at_utc=generated_at_utc,
        run_id=run_id,
        git_source_commit=git_source_commit,
    )
    package_root.mkdir(parents=True)
    for relative, payload in candidate["files"].items():
        target = package_root.joinpath(*PurePosixPath(relative).parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
    archive_root.mkdir(parents=True, exist_ok=True)
    archive_path.write_bytes(candidate["archive"])
    directory_validation = validate_candidate(package_root)
    archive_validation = validate_candidate(archive_path)
    comparable = (
        "package_id",
        "package_version",
        "software_version",
        "run_id",
        "git_source_commit",
        "file_count",
        "extracted_bytes",
        "local_links",
        "public_action_authorized",
        "next_dependency",
    )
    if any(
        directory_validation[key] != archive_validation[key]
        for key in comparable
    ):
        raise PhaseSixCandidateError("candidate forms disagree")
    receipt = {
        "receipt_version": "burnlens-phase-six-candidate-receipt-v0.1.0",
        "package_id": PACKAGE_ID,
        "package_version": PACKAGE_VERSION,
        "software_version": SOFTWARE_VERSION,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "git_source_commit": git_source_commit,
        "archive": {
            "path": archive_path.name,
            "bytes": candidate["archive_bytes"],
            "sha256": candidate["archive_sha256"],
        },
        "package": {
            "path": package_root.relative_to(repository_root).as_posix(),
            "file_count": candidate["file_count"],
            "bytes": candidate["extracted_bytes"],
            "repository_source_files": candidate["repository_source_files"],
        },
        "directory_validation": directory_validation["result"],
        "archive_validation": archive_validation["result"],
        "local_links": directory_validation["local_links"],
        "disposition": "pass-local-pre-publication-only",
        "public_action_authorized": False,
        "next_dependency": "P6O1-T01-U06 real rendered and recipient QA",
    }
    receipt_path.write_bytes(_json_bytes(receipt))
    return {
        "package_root": package_root.as_posix(),
        "archive_path": archive_path.as_posix(),
        "receipt_path": receipt_path.as_posix(),
        "archive_bytes": candidate["archive_bytes"],
        "archive_sha256": candidate["archive_sha256"],
        "file_count": candidate["file_count"],
        "extracted_bytes": candidate["extracted_bytes"],
        "repository_source_files": candidate["repository_source_files"],
        "local_links": directory_validation["local_links"],
        "result": "PHASE_SIX_CANDIDATE_WRITE_PASS",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build or validate the BurnLens Phase Six candidate."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    build = subparsers.add_parser("build")
    build.add_argument("--repository-root", type=Path, required=True)
    build.add_argument("--output-root", type=Path, required=True)
    build.add_argument("--archive-root", type=Path, required=True)
    build.add_argument("--generated-at-utc", required=True)
    build.add_argument("--run-id", required=True)
    build.add_argument("--git-source-commit", required=True)
    validate = subparsers.add_parser("validate")
    validate.add_argument("path", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "build":
            result = write_candidate(
                repository_root=args.repository_root.resolve(),
                output_root=args.output_root.resolve(),
                archive_root=args.archive_root.resolve(),
                generated_at_utc=args.generated_at_utc,
                run_id=args.run_id,
                git_source_commit=args.git_source_commit,
            )
        else:
            result = validate_candidate(args.path.resolve())
    except PhaseSixCandidateError as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
