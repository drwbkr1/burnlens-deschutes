"""Build and validate the frozen Phase Five baseline-first candidate."""

from __future__ import annotations

import argparse
from hashlib import sha256
import io
import json
from pathlib import Path, PurePosixPath
import re
from typing import Any
import zipfile


CANDIDATE_VERSION = "burnlens-phase-five-baseline-first-candidate-v0.1.0"
CANDIDATE_ID = "BURNLENS-PHASE-FIVE-BASELINE-FIRST-CANDIDATE-2026-001"
ARCHIVE_NAME = f"{CANDIDATE_ID}.zip"
RECEIPT_NAME = f"{CANDIDATE_ID}-RECEIPT.json"
SOFTWARE_VERSION = "0.55.0"
ROUTE = "baseline-primary-with-rejected-model-diagnostic"
ACCEPTED_METHOD = "burnlens-baseline-v0.1.0"
REJECTED_MODEL = "burnlens-unet-binary-v0.1.0"
FIXED_ZIP_DATETIME = (2026, 1, 1, 0, 0, 0)
MAX_ARCHIVE_BYTES = 1_500_000
MAX_EXTRACTED_BYTES = 3_500_000
MAX_ARCHIVE_MEMBERS = 24
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")
RUN_ID_PATTERN = re.compile(
    r"^BL-[0-9]{4}-[0-9]{2}-[0-9]{2}-p5o1-t01-u06-release-candidate-r[0-9]{3}$"
)

SOURCE_FILES = (
    (
        "portfolio/phase-four/BURNLENS-WARD-CREEK-RBR-RUN-2026-001.zip",
        "phase-four/BURNLENS-WARD-CREEK-RBR-RUN-2026-001.zip",
        487893,
        "91308a2ffe7095d89843edeb1634d6b1e972eb65bf1f67f38f1da0279102d84e",
    ),
    (
        "samples/runs/phase-four/burnlens-geoint-evidence-interface-v0.1.0/"
        "PHASE-FOUR-EVIDENCE-INTERFACE-2026-001.html",
        "interfaces/phase-four-evidence.html",
        177666,
        "7a657ad772b34ff42cf4f4024a585b70fb8e7f41bab363cd056fcf8059825fb7",
    ),
    (
        "records/phase-four/release-audits/RELEASE-AUDIT-2026-001.json",
        "evidence/phase-four-release-audit.json",
        14840,
        "3942190b72e6711e7bc7bfa136c45b12b7d36a3ff05243bb72f6dc41029684c7",
    ),
    (
        "records/phase-five/contracts/"
        "PHASE-FIVE-QA-RELEASE-CONTRACT-2026-001.json",
        "evidence/u01-qa-release-contract.json",
        10836,
        "a187a9d12adea288700b25c0e3a9c18ce08dee7f5f45c46a7989ca8dc588bc4c",
    ),
    (
        "records/phase-five/failure-injections/"
        "PHASE-FIVE-FAILURE-INJECTION-RECORD-2026-001.json",
        "evidence/u02-failure-injection-record.json",
        7104,
        "c5ff046ebd864751bb0fac9d160331d6ee4fcb505619af036fdbeae7b216c835",
    ),
    (
        "samples/qa/phase-five/failure-injection-v0.1.0/"
        "PHASE-FIVE-FAILURE-INJECTION-2026-001.html",
        "evidence/u02-failure-injection.html",
        3610,
        "9aef845e97ea40ffd845f3b9fbbcfb071f95853138a8ff6878a7ca2d47811a61",
    ),
    (
        "samples/qa/phase-five/failure-injection-v0.1.0/"
        "PHASE-FIVE-FAILURE-INJECTION-2026-001.json",
        "evidence/u02-failure-injection.json",
        4590,
        "1c00be85907aa8e965b16a8520b5493cf8421b52f6c6abf7f225aeee0c7ee4b4",
    ),
    (
        "records/phase-five/interfaces/"
        "PHASE-FIVE-RELIABILITY-INTERFACE-RECORD-2026-001.json",
        "evidence/u03-reliability-interface-record.json",
        3795,
        "c97811c81bc085aead30a80fe8de5eb0f2fe7a93b6620ed0da936c717af63118",
    ),
    (
        "records/phase-five/interfaces/"
        "PHASE-FIVE-RELIABILITY-INTERFACE-OWNER-RENDER-RECEIPT-2026-001.json",
        "evidence/u03-owner-render-receipt.json",
        1346,
        "9487263767cb6260fce4170dc3e1b432c530b3f489de605e6c2d5c74f4971787",
    ),
    (
        "samples/qa/phase-five/reliability-interface-v0.1.0/"
        "PHASE-FIVE-RELIABILITY-INTERFACE-2026-001.html",
        "interfaces/phase-five-reliability.html",
        179808,
        "9c5b65dd5b3b83645ff59a502718c960cd8d70ed8d45628dcae8d907dafc4316",
    ),
    (
        "samples/qa/phase-five/reliability-interface-v0.1.0/"
        "PHASE-FIVE-RELIABILITY-INTERFACE-2026-001.json",
        "evidence/u03-reliability-interface.json",
        3000,
        "33a9cf2f8b630cf49285683c39745f01f4c52fe8aa90b9811a1c6aab87b6d2dc",
    ),
    (
        "records/phase-five/assurance/"
        "PHASE-FIVE-ASSURANCE-RECORD-2026-001.json",
        "evidence/u04-assurance-record.json",
        7928,
        "752148bfcfd24ef4c6c2daf627f2974a27b890fc793a5cf8c8d2ac578597b195",
    ),
    (
        "samples/qa/phase-five/assurance-v0.1.0/"
        "PHASE-FIVE-ASSURANCE-2026-001.html",
        "evidence/u04-assurance.html",
        3974,
        "ef666ae359896815dd234eec2171d42f93cb0b6e2ebb1dfd66445ff3bea572e8",
    ),
    (
        "samples/qa/phase-five/assurance-v0.1.0/"
        "PHASE-FIVE-ASSURANCE-2026-001.json",
        "evidence/u04-assurance.json",
        31276,
        "89c0c7896d94ae41157367cb1b6111d0d5b93a9e0bcd49f57155cd47ae808674",
    ),
    (
        "records/phase-five/reconstruction/"
        "PHASE-FIVE-CLEAN-RECONSTRUCTION-RECORD-2026-001.json",
        "evidence/u05-clean-reconstruction-record.json",
        12248,
        "ebe09e24add8d5d1a03a47e8faa61f4d159eea7ccab78fd4a05e65979397ab9a",
    ),
    (
        "samples/qa/phase-five/reconstruction-v0.1.0/"
        "PHASE-FIVE-CLEAN-RECONSTRUCTION-2026-001.html",
        "evidence/u05-clean-reconstruction.html",
        6048,
        "9227c6af6000479b37f3480df7d85b3e4a2906971066fcbcb9fa02e2b7b7cd14",
    ),
    (
        "samples/qa/phase-five/reconstruction-v0.1.0/"
        "PHASE-FIVE-CLEAN-RECONSTRUCTION-2026-001.json",
        "evidence/u05-clean-reconstruction.json",
        9135,
        "510eec2ea8f2c75afe491c4d001d81f4453a19b96f4a3f295fcb9cfd770844c0",
    ),
)


class PhaseFiveCandidateError(RuntimeError):
    """The Phase Five candidate build or validation failed."""


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
        raise PhaseFiveCandidateError(f"invalid JSON: {label}") from exc
    if not isinstance(value, dict):
        raise PhaseFiveCandidateError(f"JSON root must be object: {label}")
    return value


def _source_payloads(repository_root: Path) -> dict[str, bytes]:
    payloads: dict[str, bytes] = {}
    for source, target, expected_bytes, expected_sha256 in SOURCE_FILES:
        path = repository_root / source
        if not path.is_file():
            raise PhaseFiveCandidateError(f"missing frozen source: {source}")
        payload = path.read_bytes()
        if len(payload) != expected_bytes:
            raise PhaseFiveCandidateError(
                f"frozen source byte mismatch: {source}"
            )
        if _sha256_bytes(payload) != expected_sha256:
            raise PhaseFiveCandidateError(
                f"frozen source hash mismatch: {source}"
            )
        payloads[target] = payload
    return payloads


def _qa_matrix(
    *,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, Any]:
    return {
        "matrix_version": "burnlens-phase-five-qa-matrix-v0.1.0",
        "candidate_version": CANDIDATE_VERSION,
        "software_version": SOFTWARE_VERSION,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "git_source_commit": git_source_commit,
        "route": ROUTE,
        "accepted_method": ACCEPTED_METHOD,
        "rejected_model": REJECTED_MODEL,
        "model_accepted": False,
        "model_outperformed_rbr": False,
        "units": [
            {
                "unit_id": "P5O1-T01-U01",
                "status": "pass",
                "result": "QA and release-control contract locked.",
            },
            {
                "unit_id": "P5O1-T01-U02",
                "status": "pass",
                "result": "Five controlled package failures reject visibly and recover safely.",
            },
            {
                "unit_id": "P5O1-T01-U03",
                "status": "pass",
                "result": (
                    "Owner-confirmed desktop, narrow, and keyboard journey "
                    "on exact bytes; not formal accessibility certification."
                ),
            },
            {
                "unit_id": "P5O1-T01-U04",
                "status": "pass-with-disclosed-medium-finding",
                "result": (
                    "Security, integrity, rights, privacy, claims, "
                    "performance, and complete regression gates pass."
                ),
            },
            {
                "unit_id": "P5O1-T01-U05",
                "status": "pass-with-visible-medium-builder-identity-issue",
                "result": (
                    "Clean reconstruction, installed candidate proof, "
                    "portable regression, and exact rollback pass."
                ),
            },
            {
                "unit_id": "P5O1-T01-U06",
                "status": "candidate-freeze",
                "result": (
                    "This package freezes the baseline-first candidate for "
                    "milestone review and post-merge verification."
                ),
            },
        ],
        "open_findings": {
            "critical": 0,
            "high": 0,
            "medium": 2,
            "low": 0,
        },
        "phase_six_entry": {
            "critical_and_high_gates_pass": True,
            "medium_findings_visible_with_impact_and_workaround": True,
            "rollback_succeeds": True,
            "candidate_inspectable": True,
            "candidate_reproducible": True,
            "recommendation": "eligible-after-milestone-merge-tag-and-fresh-main-verification",
        },
    }


def _known_issues() -> bytes:
    return (
        "# BurnLens Phase Five known issues\n\n"
        "This register belongs to the baseline-first candidate. It is not a "
        "claim of vulnerability-free, accessibility-certified, operational, "
        "official, field-validated, endorsed, or emergency-ready status.\n\n"
        "## P5-U04-KI-001 — medium dependency advisory\n\n"
        "The locked runtime contains setuptools 82.0.0. The U04 snapshot "
        "records GHSA-h35f-9h28-mq5c / CVE-2026-59890 as medium. The public "
        "candidate is ZIP-only, has no `MANIFEST.in`, uses ASCII/NFC paths, "
        "and distributes no sdist. Impact is bounded to the advisory's "
        "affected package-discovery path. Workaround: keep the public route "
        "ZIP-only and do not add an sdist or `MANIFEST.in`; re-audit before "
        "any future packaging change. No vulnerability-free claim is made.\n\n"
        "## P5-U05-KI-001 — medium historical builder identity omission\n\n"
        "The Phase Four release audit recorded its fixed epoch and wheel hash "
        "but omitted the setuptools 82.0.1 builder identity embedded in the "
        "historical wheel. The locked v0.54 runtime alone produces a "
        "semantically equivalent but byte-different wheel. Workaround: use "
        "CPython 3.12.10, setuptools 82.0.1, "
        "`SOURCE_DATE_EPOCH=1785094504`, and `PYTHONHASHSEED=0` when exact "
        "historical wheel reconstruction is required. U05 verified two exact "
        "1,166,315-byte wheels at SHA-256 `ad3ae7c8...`.\n\n"
        "## Retained limitations\n\n"
        "- The naive clean clone lacks ignored custody required by five "
        "historical builder test files and two exact-custody assertions. The "
        "explicit portable roster passes 711 tests; the naive failure remains "
        "visible.\n"
        "- The exact U03 owner review is an internal rendered interaction "
        "check, not independent accessibility certification or formal WCAG "
        "conformance.\n"
        "- RBR remains the accepted method. WCP-002 remains visible "
        "false-positive-risk evidence. The trained U-Net remains rejected and "
        "did not outperform RBR.\n"
        "- This candidate is local and offline. It creates no deployment, "
        "GitHub Release, access, ownership, public-sharing, or external "
        "submission change.\n"
    ).encode("utf-8")


def _readme(
    *,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> bytes:
    return (
        "# BurnLens Phase Five baseline-first candidate\n\n"
        f"Candidate: `{CANDIDATE_VERSION}`  \n"
        f"Software: `{SOFTWARE_VERSION}`  \n"
        f"Run: `{run_id}`  \n"
        f"Source commit: `{git_source_commit}`  \n"
        f"Generated: `{generated_at_utc}`\n\n"
        "Open `index.html` first. Then use the exact Phase Four evidence "
        "interface for the accepted RBR-primary result and the Phase Five "
        "reliability interface for failure, accessibility, and recovery "
        "evidence.\n\n"
        "RBR is the accepted analytical method. The trained U-Net is retained "
        "only as a rejected diagnostic and did not outperform RBR. This "
        "candidate does not change any analytical array, dataset, split, "
        "label, threshold, source, AOI, or model decision.\n\n"
        "The package is a Phase Five release candidate, not the final Phase "
        "Six portfolio release. It is not official wildfire information, "
        "emergency guidance, an operational system, field validation, "
        "endorsement, or a generalization claim.\n\n"
        "Use `CANDIDATE-MANIFEST.json` and `CHECKSUMS.sha256` for exact "
        "lineage. Read `KNOWN-ISSUES.md` before interpreting the QA result.\n"
    ).encode("utf-8")


def _index_html(
    *,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> bytes:
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; img-src data:; base-uri 'none'; form-action 'none'">
<title>BurnLens Phase Five baseline-first candidate</title>
<style>
:root{{color-scheme:dark;font-family:system-ui,sans-serif;background:#0b1417;color:#eef7f4}}
*{{box-sizing:border-box}}
body{{margin:0 auto;max-width:1040px;padding:clamp(1rem,4vw,3rem);line-height:1.55}}
.eyebrow{{color:#92d6c4;text-transform:uppercase;letter-spacing:.08em;font-weight:800}}
h1{{font-size:clamp(2rem,6vw,4.25rem);line-height:1.03;max-width:18ch;margin:.35rem 0 1rem}}
h2{{font-size:1.25rem;margin-top:0}}
.lede{{font-size:1.12rem;max-width:72ch}}
.grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1rem}}
.card{{background:#142326;border:1px solid #315055;border-radius:14px;padding:1rem 1.2rem;margin:1rem 0}}
.pass{{color:#9ee7b5;font-weight:800}}.warn{{color:#ffd486;font-weight:800}}
a{{color:#9edff0}} code{{overflow-wrap:anywhere;color:#b8e9dc}}
ul{{padding-left:1.3rem}}
@media(max-width:660px){{.grid{{grid-template-columns:1fr}}}}
</style>
</head>
<body>
<p class="eyebrow">P5O1-T01-U06 · baseline-first candidate</p>
<h1>One exact candidate. Every material caveat visible.</h1>
<p class="lede">BurnLens freezes the verified RBR-primary GEOINT run together with its failure, accessibility, assurance, reconstruction, and rollback evidence. The U-Net remains a rejected diagnostic and did not outperform RBR.</p>
<div class="grid">
<section class="card">
<h2>Candidate disposition</h2>
<p class="pass">Accepted baseline-first candidate, pending milestone merge, fresh-main verification, and annotated tag</p>
<p>Software <code>{SOFTWARE_VERSION}</code>; run <code>{run_id}</code>.</p>
</section>
<section class="card">
<h2>Phase Six recommendation</h2>
<p class="pass">Eligible after the exact milestone merge, fresh-main gates, and remote tag verification pass.</p>
<p>This page is not the final Phase Six publication or submission claim.</p>
</section>
</div>
<section class="card">
<h2>Inspect the evidence</h2>
<ul>
<li><a href="interfaces/phase-four-evidence.html">Open the accepted RBR-primary Phase Four evidence interface</a>.</li>
<li><a href="interfaces/phase-five-reliability.html">Open the Phase Five reliability and failure-state interface</a>.</li>
<li><a href="evidence/u04-assurance.html">Read security, rights, integrity, claims, and performance assurance</a>.</li>
<li><a href="evidence/u05-clean-reconstruction.html">Read clean reconstruction and rollback evidence</a>.</li>
<li><a href="KNOWN-ISSUES.md">Read the exact known-issues register</a>.</li>
<li><a href="QA-MATRIX.json">Inspect the machine-readable QA matrix</a>.</li>
</ul>
</section>
<section class="card">
<h2>What remains true</h2>
<ul>
<li>RBR is accepted; WCP-002 remains visible false-positive-risk evidence.</li>
<li>The trained U-Net is valid diagnostic evidence but rejected and excluded from accepted measurements.</li>
<li>Two medium issues are visible with impact and workaround; no critical or high finding remains open.</li>
<li>The exact Phase Four ZIP remains 487,893 bytes at SHA-256 <code>91308a2f...</code>.</li>
<li>No dataset, split, label, threshold, analytical output, model decision, deployment, access, ownership, sharing, or submission state changed.</li>
</ul>
</section>
<section class="card">
<h2>Lineage and limits</h2>
<p>Source commit <code>{git_source_commit}</code>; generated <code>{generated_at_utc}</code>. Exact hashes are in <code>CANDIDATE-MANIFEST.json</code> and <code>CHECKSUMS.sha256</code>.</p>
<p class="warn">Not ground truth, generalization, model superiority, independent accessibility certification, field validation, official information, operational readiness, endorsement, emergency guidance, or final-submission readiness.</p>
</section>
</body>
</html>
"""
    return html.encode("utf-8")


def _manifest_entries(files: dict[str, bytes]) -> list[dict[str, Any]]:
    return [
        {
            "path": path,
            "bytes": len(payload),
            "sha256": _sha256_bytes(payload),
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
                f"{CANDIDATE_VERSION}/{relative}",
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
    if not RUN_ID_PATTERN.fullmatch(run_id):
        raise PhaseFiveCandidateError("invalid U06 run ID")
    if not COMMIT_PATTERN.fullmatch(git_source_commit):
        raise PhaseFiveCandidateError("invalid Git source commit")

    files = _source_payloads(repository_root)
    qa_matrix = _qa_matrix(
        generated_at_utc=generated_at_utc,
        run_id=run_id,
        git_source_commit=git_source_commit,
    )
    files.update(
        {
            "README.md": _readme(
                generated_at_utc=generated_at_utc,
                run_id=run_id,
                git_source_commit=git_source_commit,
            ),
            "index.html": _index_html(
                generated_at_utc=generated_at_utc,
                run_id=run_id,
                git_source_commit=git_source_commit,
            ),
            "KNOWN-ISSUES.md": _known_issues(),
            "QA-MATRIX.json": _json_bytes(qa_matrix),
        }
    )
    manifest = {
        "manifest_version": "burnlens-phase-five-candidate-manifest-v0.1.0",
        "candidate_id": CANDIDATE_ID,
        "candidate_version": CANDIDATE_VERSION,
        "software_version": SOFTWARE_VERSION,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "git_source_commit": git_source_commit,
        "state": "accepted-baseline-first-candidate",
        "route": ROUTE,
        "accepted_method": ACCEPTED_METHOD,
        "rejected_model": REJECTED_MODEL,
        "model_accepted": False,
        "model_outperformed_rbr": False,
        "phase_six_recommendation": (
            "eligible-after-milestone-merge-tag-and-fresh-main-verification"
        ),
        "open_findings": {
            "critical": 0,
            "high": 0,
            "medium": 2,
            "low": 0,
        },
        "files": _manifest_entries(files),
        "boundaries": {
            "analytical_output_changed": False,
            "dataset_split_label_threshold_or_source_changed": False,
            "model_decision_changed": False,
            "phase_3b_or_second_experiment": False,
            "deployment": False,
            "github_release": False,
            "access_ownership_public_sharing_or_submission_change": False,
        },
    }
    files["CANDIDATE-MANIFEST.json"] = _json_bytes(manifest)
    checksum_lines = [
        f"{_sha256_bytes(payload)}  {path}"
        for path, payload in sorted(files.items())
    ]
    files["CHECKSUMS.sha256"] = (
        "\n".join(checksum_lines) + "\n"
    ).encode("utf-8")
    archive = _archive(files)
    if len(files) > MAX_ARCHIVE_MEMBERS:
        raise PhaseFiveCandidateError("candidate member budget exceeded")
    if sum(map(len, files.values())) > MAX_EXTRACTED_BYTES:
        raise PhaseFiveCandidateError("candidate extracted-byte budget exceeded")
    if len(archive) > MAX_ARCHIVE_BYTES:
        raise PhaseFiveCandidateError("candidate archive-byte budget exceeded")
    return {
        "files": files,
        "archive": archive,
        "manifest": manifest,
        "archive_bytes": len(archive),
        "archive_sha256": _sha256_bytes(archive),
        "extracted_bytes": sum(map(len, files.values())),
        "file_count": len(files),
    }


def _safe_archive_files(payload: bytes) -> dict[str, bytes]:
    try:
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            infos = archive.infolist()
            names = [info.filename for info in infos]
            if len(names) != len(set(names)):
                raise PhaseFiveCandidateError("duplicate archive member")
            if len(names) > MAX_ARCHIVE_MEMBERS:
                raise PhaseFiveCandidateError("archive member budget exceeded")
            prefix = f"{CANDIDATE_VERSION}/"
            files: dict[str, bytes] = {}
            for info in infos:
                pure = PurePosixPath(info.filename)
                if (
                    info.is_dir()
                    or info.flag_bits & 0x1
                    or pure.is_absolute()
                    or ".." in pure.parts
                    or not info.filename.startswith(prefix)
                ):
                    raise PhaseFiveCandidateError(
                        f"unsafe archive member: {info.filename}"
                    )
                relative = info.filename[len(prefix) :]
                if not relative:
                    raise PhaseFiveCandidateError("empty archive member path")
                files[relative] = archive.read(info)
            if archive.testzip() is not None:
                raise PhaseFiveCandidateError("archive CRC failure")
            return files
    except (zipfile.BadZipFile, RuntimeError, OSError) as exc:
        if isinstance(exc, PhaseFiveCandidateError):
            raise
        raise PhaseFiveCandidateError("unsafe or corrupt candidate archive") from exc


def _directory_files(root: Path) -> dict[str, bytes]:
    if not root.is_dir():
        raise PhaseFiveCandidateError("candidate directory is missing")
    files: dict[str, bytes] = {}
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            raise PhaseFiveCandidateError(f"linked candidate member: {relative}")
        files[relative] = path.read_bytes()
    return files


def validate_candidate(path: Path) -> dict[str, Any]:
    if path.is_dir():
        files = _directory_files(path)
        archive_bytes = None
        archive_sha256 = None
    else:
        payload = path.read_bytes()
        if len(payload) > MAX_ARCHIVE_BYTES:
            raise PhaseFiveCandidateError("candidate archive-byte budget exceeded")
        files = _safe_archive_files(payload)
        archive_bytes = len(payload)
        archive_sha256 = _sha256_bytes(payload)

    required = {
        "README.md",
        "index.html",
        "KNOWN-ISSUES.md",
        "QA-MATRIX.json",
        "CANDIDATE-MANIFEST.json",
        "CHECKSUMS.sha256",
    }
    if not required.issubset(files):
        missing = sorted(required - set(files))
        raise PhaseFiveCandidateError(
            "missing candidate members: " + ", ".join(missing)
        )
    if len(files) > MAX_ARCHIVE_MEMBERS:
        raise PhaseFiveCandidateError("candidate member budget exceeded")
    extracted_bytes = sum(map(len, files.values()))
    if extracted_bytes > MAX_EXTRACTED_BYTES:
        raise PhaseFiveCandidateError("candidate extracted-byte budget exceeded")

    manifest = _load_json_bytes(
        files["CANDIDATE-MANIFEST.json"],
        "CANDIDATE-MANIFEST.json",
    )
    qa = _load_json_bytes(files["QA-MATRIX.json"], "QA-MATRIX.json")
    expected_manifest = {
        "candidate_id": CANDIDATE_ID,
        "candidate_version": CANDIDATE_VERSION,
        "software_version": SOFTWARE_VERSION,
        "state": "accepted-baseline-first-candidate",
        "route": ROUTE,
        "accepted_method": ACCEPTED_METHOD,
        "rejected_model": REJECTED_MODEL,
        "model_accepted": False,
        "model_outperformed_rbr": False,
    }
    for key, expected in expected_manifest.items():
        if manifest.get(key) != expected:
            raise PhaseFiveCandidateError(
                f"candidate manifest binding mismatch: {key}"
            )
    if not RUN_ID_PATTERN.fullmatch(str(manifest.get("run_id", ""))):
        raise PhaseFiveCandidateError("candidate manifest run ID mismatch")
    if not COMMIT_PATTERN.fullmatch(
        str(manifest.get("git_source_commit", ""))
    ):
        raise PhaseFiveCandidateError("candidate manifest commit mismatch")
    if qa.get("run_id") != manifest["run_id"]:
        raise PhaseFiveCandidateError("QA matrix run binding mismatch")
    if qa.get("git_source_commit") != manifest["git_source_commit"]:
        raise PhaseFiveCandidateError("QA matrix commit binding mismatch")
    if qa.get("open_findings") != {
        "critical": 0,
        "high": 0,
        "medium": 2,
        "low": 0,
    }:
        raise PhaseFiveCandidateError("QA finding roster mismatch")

    entries = manifest.get("files")
    if not isinstance(entries, list):
        raise PhaseFiveCandidateError("candidate manifest files missing")
    manifest_roster: dict[str, tuple[int, str]] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            raise PhaseFiveCandidateError("invalid candidate manifest entry")
        relative = entry.get("path")
        if not isinstance(relative, str) or relative in manifest_roster:
            raise PhaseFiveCandidateError("duplicate candidate manifest path")
        manifest_roster[relative] = (
            entry.get("bytes"),
            entry.get("sha256"),
        )
    expected_manifest_paths = set(files) - {
        "CANDIDATE-MANIFEST.json",
        "CHECKSUMS.sha256",
    }
    if set(manifest_roster) != expected_manifest_paths:
        raise PhaseFiveCandidateError("candidate manifest roster mismatch")
    for relative, (expected_bytes, expected_sha256) in manifest_roster.items():
        payload = files[relative]
        if len(payload) != expected_bytes:
            raise PhaseFiveCandidateError(
                f"candidate manifest byte mismatch: {relative}"
            )
        if _sha256_bytes(payload) != expected_sha256:
            raise PhaseFiveCandidateError(
                f"candidate manifest hash mismatch: {relative}"
            )

    checksum_roster: dict[str, str] = {}
    try:
        checksum_text = files["CHECKSUMS.sha256"].decode("utf-8")
    except UnicodeDecodeError as exc:
        raise PhaseFiveCandidateError("invalid checksum encoding") from exc
    for line in checksum_text.splitlines():
        digest, separator, relative = line.partition("  ")
        if (
            not separator
            or not re.fullmatch(r"[0-9a-f]{64}", digest)
            or relative in checksum_roster
        ):
            raise PhaseFiveCandidateError("invalid checksum roster")
        checksum_roster[relative] = digest
    expected_checksum_paths = set(files) - {"CHECKSUMS.sha256"}
    if set(checksum_roster) != expected_checksum_paths:
        raise PhaseFiveCandidateError("checksum roster mismatch")
    for relative, expected_sha256 in checksum_roster.items():
        if _sha256_bytes(files[relative]) != expected_sha256:
            raise PhaseFiveCandidateError(
                f"checksum mismatch: {relative}"
            )

    serialized = b"\n".join(files.values()).lower()
    for forbidden in (
        b"c:\\users",
        b"c:\\projects",
        b"begin rsa private key",
        b"begin openssh private key",
        b"recipient retrieval url",
    ):
        if forbidden in serialized:
            raise PhaseFiveCandidateError(
                "candidate contains prohibited private material"
            )
    if b"model_outperformed_rbr\": true" in serialized:
        raise PhaseFiveCandidateError("candidate promotes rejected model")

    return {
        "result": "PHASE_FIVE_CANDIDATE_VALIDATION_PASS",
        "candidate_id": manifest["candidate_id"],
        "candidate_version": manifest["candidate_version"],
        "software_version": manifest["software_version"],
        "run_id": manifest["run_id"],
        "git_source_commit": manifest["git_source_commit"],
        "file_count": len(files),
        "extracted_bytes": extracted_bytes,
        "archive_bytes": archive_bytes,
        "archive_sha256": archive_sha256,
        "open_findings": qa["open_findings"],
        "phase_six_recommendation": manifest["phase_six_recommendation"],
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
    package_root = output_root / CANDIDATE_VERSION
    archive_path = archive_root / ARCHIVE_NAME
    receipt_path = archive_root / RECEIPT_NAME
    for path in (package_root, archive_path, receipt_path):
        if path.exists():
            raise PhaseFiveCandidateError(
                f"refusing to overwrite candidate output: {path}"
            )
    candidate = build_candidate(
        repository_root=repository_root,
        generated_at_utc=generated_at_utc,
        run_id=run_id,
        git_source_commit=git_source_commit,
    )
    package_root.mkdir(parents=True)
    for relative, payload in candidate["files"].items():
        path = package_root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
    archive_root.mkdir(parents=True, exist_ok=True)
    archive_path.write_bytes(candidate["archive"])
    directory_validation = validate_candidate(package_root)
    archive_validation = validate_candidate(archive_path)
    try:
        package_relative = package_root.relative_to(repository_root).as_posix()
    except ValueError as exc:
        raise PhaseFiveCandidateError(
            "candidate output must remain inside the repository"
        ) from exc
    comparable = (
        "candidate_id",
        "candidate_version",
        "software_version",
        "run_id",
        "git_source_commit",
        "file_count",
        "extracted_bytes",
        "open_findings",
        "phase_six_recommendation",
    )
    if any(
        directory_validation[key] != archive_validation[key]
        for key in comparable
    ):
        raise PhaseFiveCandidateError("candidate forms disagree")
    receipt = {
        "receipt_version": "burnlens-phase-five-candidate-receipt-v0.1.0",
        "candidate_id": CANDIDATE_ID,
        "candidate_version": CANDIDATE_VERSION,
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
            "path": package_relative,
            "file_count": candidate["file_count"],
            "bytes": candidate["extracted_bytes"],
        },
        "directory_validation": directory_validation["result"],
        "archive_validation": archive_validation["result"],
        "disposition": "accepted-baseline-first-candidate-pending-merge",
        "phase_six_recommendation": (
            "eligible-after-milestone-merge-tag-and-fresh-main-verification"
        ),
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
        "result": "PHASE_FIVE_CANDIDATE_WRITE_PASS",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build or validate the BurnLens Phase Five candidate."
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
    except PhaseFiveCandidateError as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
