"""Deterministic Phase Five package failure injection and recovery evidence."""

from __future__ import annotations

import argparse
from hashlib import sha256
from html import escape
import io
import json
import os
from pathlib import Path
import subprocess
from typing import Any
import zipfile

from burnlens.phase_five_contract import load_contract
from burnlens.phase_four_package import (
    FIXED_ZIP_DATETIME,
    PACKAGE_VERSION,
    PhaseFourPackageError,
    validate_package,
)


REPORT_ID = "PHASE-FIVE-FAILURE-INJECTION-2026-001"
REPORT_VERSION = "burnlens-phase-five-failure-injection-v0.1.0"
RECORD_PATH = Path(
    "records/phase-five/failure-injections/"
    "PHASE-FIVE-FAILURE-INJECTION-RECORD-2026-001.json"
)
RUN_ID_PATTERN = (
    "BL-2026-07-26-p5o1-t01-u02-failure-injection-r"
)
CANONICAL_DIRECTORY = Path(
    "samples/runs/phase-four/burnlens-ward-creek-rbr-run-v0.1.0"
)
CANONICAL_ARCHIVE = Path(
    "portfolio/phase-four/BURNLENS-WARD-CREEK-RBR-RUN-2026-001.zip"
)
EXPECTED_ERRORS = {
    "missing-required-member": "checksum mismatch: interface/index.html",
    "corrupt-required-member": "checksum mismatch: interface/index.html",
    "archive-path-traversal": "archive member path unsafe",
    "binding-mismatch": "package manifest binding drift",
    "partial-package": "archive member-count drift",
}


class PhaseFiveFailureInjectionError(RuntimeError):
    """Failure injection could not produce trustworthy retained evidence."""


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(
        "utf-8"
    )


def _sha256_bytes(payload: bytes) -> str:
    return sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(8 * 1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _receipt(path: str, payload: bytes) -> dict[str, Any]:
    return {
        "path": path,
        "bytes": len(payload),
        "sha256": _sha256_bytes(payload),
    }


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
            raise PhaseFiveFailureInjectionError(
                f"output readback differs: {path}"
            )
    except Exception:
        if created and path.exists():
            path.unlink()
        raise


def _require_clean_head(root: Path, git_source_commit: str) -> None:
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if head != git_source_commit:
        raise PhaseFiveFailureInjectionError(
            "git source commit differs from HEAD"
        )
    status = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    if status:
        raise PhaseFiveFailureInjectionError(
            "working tree must be clean before U02 evidence execution"
        )


def _canonical_payloads(archive_path: Path) -> dict[str, bytes]:
    with zipfile.ZipFile(archive_path) as archive:
        payloads: dict[str, bytes] = {}
        prefix = f"{PACKAGE_VERSION}/"
        for info in archive.infolist():
            if not info.filename.startswith(prefix):
                raise PhaseFiveFailureInjectionError(
                    "canonical archive root drift"
                )
            relative = info.filename[len(prefix) :]
            payloads[relative] = archive.read(info)
    if len(payloads) != 66:
        raise PhaseFiveFailureInjectionError(
            "canonical archive member-count drift"
        )
    return payloads


def _archive(payloads: dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(
        buffer,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as archive:
        for relative, payload in sorted(
            payloads.items(), key=lambda item: item[0].casefold()
        ):
            info = zipfile.ZipInfo(
                f"{PACKAGE_VERSION}/{relative}",
                FIXED_ZIP_DATETIME,
            )
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, payload)
    return buffer.getvalue()


def build_injection_archives(
    canonical_archive: Path,
) -> dict[str, bytes]:
    """Build exact invalid archives from the tracked canonical archive."""

    source = _canonical_payloads(canonical_archive)
    fixtures: dict[str, bytes] = {}

    missing = dict(source)
    del missing["interface/index.html"]
    missing["retained/missing-interface-marker.txt"] = (
        b"interface/index.html intentionally absent\n"
    )
    fixtures["missing-required-member"] = _archive(missing)

    corrupt = dict(source)
    corrupt["interface/index.html"] = b"corrupt interface fixture\n"
    fixtures["corrupt-required-member"] = _archive(corrupt)

    traversal = dict(source)
    del traversal["README.md"]
    traversal["../escape.txt"] = b"must never escape extraction root\n"
    fixtures["archive-path-traversal"] = _archive(traversal)

    mismatch = dict(source)
    manifest = json.loads(mismatch["PACKAGE-MANIFEST.json"])
    manifest["accepted_method"] = "unapproved-method-v9"
    manifest["route"] = "model-primary"
    manifest["run_id"] = "BL-WRONG-RUN"
    mismatch["PACKAGE-MANIFEST.json"] = _json_bytes(manifest)
    fixtures["binding-mismatch"] = _archive(mismatch)

    partial = {
        "PACKAGE-MANIFEST.json": source["PACKAGE-MANIFEST.json"],
    }
    fixtures["partial-package"] = _archive(partial)
    return fixtures


def _canonical_identity(root: Path) -> dict[str, Any]:
    directory = root / CANONICAL_DIRECTORY
    archive = root / CANONICAL_ARCHIVE
    return {
        "directory_validation": validate_package(directory)["result"],
        "archive_validation": validate_package(archive)["result"],
        "archive": {
            "path": CANONICAL_ARCHIVE.as_posix(),
            "bytes": archive.stat().st_size,
            "sha256": _sha256_file(archive),
        },
        "interface": {
            "path": (
                CANONICAL_DIRECTORY / "interface/index.html"
            ).as_posix(),
            "bytes": (directory / "interface/index.html").stat().st_size,
            "sha256": _sha256_file(directory / "interface/index.html"),
        },
    }


def _html_report(result: dict[str, Any]) -> bytes:
    rows = []
    for item in result["injections"]:
        rows.append(
            "<tr>"
            f"<th scope=\"row\">{escape(item['injection_id'])}</th>"
            f"<td>{escape(item['actual_error'])}</td>"
            f"<td><code>{escape(item['fixture']['sha256'])}</code></td>"
            "<td><strong>Rejected</strong></td>"
            "</tr>"
        )
    body = "\n".join(rows)
    return (
        "<!doctype html>\n"
        "<html lang=\"en\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
        "<meta http-equiv=\"Content-Security-Policy\" "
        "content=\"default-src 'none'; style-src 'unsafe-inline'; "
        "img-src data:; connect-src 'none'\">"
        "<title>BurnLens Phase Five failure injection</title>"
        "<style>"
        ":root{color-scheme:dark;--bg:#0c1614;--panel:#14221f;"
        "--line:#405b52;--ink:#eef6f1;--muted:#b9c8c1;"
        "--pass:#42d9cc;--fail:#ff9d42;--focus:#fff27a}"
        "*{box-sizing:border-box}body{margin:0;background:var(--bg);"
        "color:var(--ink);font:16px/1.55 system-ui,sans-serif}"
        "main{max-width:1100px;margin:auto;padding:2.5rem 1rem 4rem}"
        "h1{font-size:clamp(2.2rem,6vw,4.8rem);line-height:.98;"
        "letter-spacing:-.04em;margin:.4rem 0 1rem}"
        ".eyebrow{color:var(--pass);font-weight:800;text-transform:uppercase;"
        "letter-spacing:.08em}.warning,.recovery{padding:1rem 1.2rem;"
        "border-radius:14px;margin:1.4rem 0}.warning{background:#33271b;"
        "border:1px solid #9f6b30}.recovery{background:var(--panel);"
        "border:1px solid var(--pass)}table{width:100%;border-collapse:collapse;"
        "background:var(--panel);border:1px solid var(--line)}th,td{padding:.8rem;"
        "text-align:left;border-bottom:1px solid var(--line);vertical-align:top}"
        "th{color:var(--muted)}code{overflow-wrap:anywhere}"
        "strong{color:var(--fail)}.recovery strong{color:var(--pass)}"
        "@media(max-width:700px){th,td{display:block;width:100%}"
        "thead{position:absolute;left:-9999px}tr{display:block;"
        "border-bottom:2px solid var(--line)}}"
        "</style></head><body><main>"
        "<p class=\"eyebrow\">Phase Five reliability evidence</p>"
        "<h1>Failure is rejected before it can look accepted.</h1>"
        "<p>This report exercises five invalid forms of the exact BurnLens "
        "Phase Four package. It changes no analytical output.</p>"
        "<div class=\"warning\" role=\"note\"><strong>Experimental and "
        "non-operational.</strong> Not official wildfire information, "
        "emergency guidance, routing, tactical, or incident-command support. "
        "Official sources govern.</div>"
        "<table><thead><tr><th>Injection</th><th>Visible diagnosis</th>"
        "<th>Fixture SHA-256</th><th>Result</th></tr></thead><tbody>"
        f"{body}</tbody></table>"
        "<div class=\"recovery\"><strong>Canonical recovery passed.</strong> "
        "After every invalid fixture, both untouched canonical package forms "
        "validated and their exact archive/interface hashes remained stable."
        "</div>"
        "<p>RBR remains the accepted analytical method. The U-Net remains a "
        "rejected diagnostic and is not used for measurements.</p>"
        f"<p><code>{escape(result['run_id'])}</code> · source "
        f"<code>{escape(result['git_source_commit'])}</code></p>"
        "</main></body></html>\n"
    ).encode("utf-8")


def run_failure_injections(
    *,
    repository_root: Path,
    output_directory: Path,
    report_directory: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
    require_clean: bool = True,
) -> dict[str, Any]:
    """Execute five invalid fixtures and revalidate canonical bytes each time."""

    root = repository_root.resolve()
    if not run_id.startswith(RUN_ID_PATTERN):
        raise PhaseFiveFailureInjectionError("run ID drift")
    if require_clean:
        _require_clean_head(root, git_source_commit)
    contract = load_contract(root)
    output = output_directory.resolve()
    report = report_directory.resolve()
    if output.exists() and any(output.iterdir()):
        raise PhaseFiveFailureInjectionError(
            f"refusing to overwrite nonempty output: {output}"
        )
    if report.exists() and any(report.iterdir()):
        raise PhaseFiveFailureInjectionError(
            f"refusing to overwrite nonempty report: {report}"
        )

    canonical_before = _canonical_identity(root)
    fixtures = build_injection_archives(root / CANONICAL_ARCHIVE)
    injections = []
    for injection_id in EXPECTED_ERRORS:
        payload = fixtures[injection_id]
        relative = f"fixtures/{injection_id}.zip"
        path = output / relative
        _write_new(path, payload)
        try:
            validate_package(path)
        except PhaseFourPackageError as exc:
            actual_error = str(exc)
        else:
            raise PhaseFiveFailureInjectionError(
                f"invalid fixture unexpectedly passed: {injection_id}"
            )
        if actual_error != EXPECTED_ERRORS[injection_id]:
            raise PhaseFiveFailureInjectionError(
                f"diagnosis drift for {injection_id}: {actual_error}"
            )
        recovery = _canonical_identity(root)
        if recovery != canonical_before:
            raise PhaseFiveFailureInjectionError(
                f"canonical recovery drift after {injection_id}"
            )
        injections.append(
            {
                "injection_id": injection_id,
                "fixture": _receipt(relative, payload),
                "expected_error": EXPECTED_ERRORS[injection_id],
                "actual_error": actual_error,
                "exception": "PhaseFourPackageError",
                "accepted": False,
                "canonical_recovery": "pass",
            }
        )

    result = {
        "report_version": REPORT_VERSION,
        "report_id": REPORT_ID,
        "milestone_id": "P5O1-T01",
        "unit_id": "P5O1-T01-U02",
        "run_id": run_id,
        "generated_at_utc": generated_at_utc,
        "git_source_commit": git_source_commit,
        "contract_id": contract["contract_id"],
        "canonical_before": canonical_before,
        "injections": injections,
        "canonical_after": _canonical_identity(root),
        "checks": {
            "all_invalid_fixtures_rejected": True,
            "all_diagnoses_exact": True,
            "canonical_validated_after_every_injection": True,
            "canonical_archive_hash_unchanged": True,
            "canonical_interface_hash_unchanged": True,
            "path_escape_created": False,
            "accepted_output_created": False,
        },
        "analytical_posture": {
            "accepted_method": "burnlens-baseline-v0.1.0",
            "rejected_diagnostic_model": "burnlens-unet-binary-v0.1.0",
            "rejected_model_accepted": False,
            "rejected_model_outperformed_rbr": False,
        },
        "disposition": "pass",
        "next_dependency": "P5O1-T01-U03 accessibility and reviewer clarity",
    }
    result_bytes = _json_bytes(result)
    html_bytes = _html_report(result)
    _write_new(output / f"{REPORT_ID}.json", result_bytes)
    _write_new(report / f"{REPORT_ID}.json", result_bytes)
    _write_new(report / f"{REPORT_ID}.html", html_bytes)
    complete = {
        "run_id": run_id,
        "unit_id": "P5O1-T01-U02",
        "result": "PHASE_FIVE_FAILURE_INJECTION_PASS",
        "report": _receipt(f"{REPORT_ID}.json", result_bytes),
        "html": _receipt(f"{REPORT_ID}.html", html_bytes),
        "fixture_count": len(injections),
    }
    _write_new(output / "RUN-COMPLETE.json", _json_bytes(complete))
    return {
        "result": result,
        "result_bytes": result_bytes,
        "html_bytes": html_bytes,
        "complete": complete,
    }


def validate_failure_record(repository_root: Path) -> dict[str, Any]:
    """Reconstruct fixture identities and validate tracked U02 evidence."""

    root = repository_root.resolve()
    try:
        record = json.loads((root / RECORD_PATH).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PhaseFiveFailureInjectionError(
            "invalid failure-injection record"
        ) from exc
    if (
        not isinstance(record, dict)
        or record.get("record_id")
        != "PHASE-FIVE-FAILURE-INJECTION-RECORD-2026-001"
        or record.get("implementation_commit")
        != "b868ff007670b98b385eaeb2060b942fb38c7a4c"
        or record.get("disposition") != "pass"
    ):
        raise PhaseFiveFailureInjectionError(
            "failure-injection record binding drift"
        )
    attempts = record.get("attempts")
    if (
        not isinstance(attempts, list)
        or len(attempts) != 2
        or attempts[0].get("disposition") != "remediate"
        or attempts[1].get("disposition") != "pass"
    ):
        raise PhaseFiveFailureInjectionError(
            "failure-injection attempt ledger drift"
        )
    passed = attempts[1]
    fixtures = build_injection_archives(root / CANONICAL_ARCHIVE)
    inventory = {
        item["path"].removeprefix("fixtures/"): item
        for item in passed["ignored_run_inventory"]["files"]
        if item["path"].startswith("fixtures/")
    }
    if len(inventory) != len(EXPECTED_ERRORS):
        raise PhaseFiveFailureInjectionError(
            "failure fixture inventory drift"
        )
    for injection_id, payload in fixtures.items():
        item = inventory.get(f"{injection_id}.zip")
        if (
            item is None
            or item.get("bytes") != len(payload)
            or item.get("sha256") != _sha256_bytes(payload)
        ):
            raise PhaseFiveFailureInjectionError(
                f"failure fixture identity drift: {injection_id}"
            )
    for item in passed.get("public_outputs", []):
        path = root / item["path"]
        if (
            not path.is_file()
            or path.stat().st_size != item["bytes"]
            or _sha256_file(path) != item["sha256"]
        ):
            raise PhaseFiveFailureInjectionError(
                f"public failure evidence drift: {item['path']}"
            )
    public_json = root / (
        "samples/qa/phase-five/failure-injection-v0.1.0/"
        f"{REPORT_ID}.json"
    )
    public_html = public_json.with_suffix(".html")
    result = json.loads(public_json.read_text(encoding="utf-8"))
    html = public_html.read_text(encoding="utf-8")
    if (
        result.get("disposition") != "pass"
        or len(result.get("injections", [])) != 5
        or not all(
            item.get("accepted") is False
            and item.get("actual_error") == EXPECTED_ERRORS[item["injection_id"]]
            for item in result["injections"]
        )
        or "connect-src 'none'" not in html
        or "Failure is rejected before it can look accepted." not in html
        or "rejected diagnostic" not in html
        or "operational readiness" in html.lower()
    ):
        raise PhaseFiveFailureInjectionError(
            "public failure evidence semantic drift"
        )
    canonical = _canonical_identity(root)
    if canonical != result.get("canonical_before"):
        raise PhaseFiveFailureInjectionError(
            "canonical recovery identity drift"
        )
    return {
        "result": "PHASE_FIVE_FAILURE_RECORD_VALIDATION_PASS",
        "fixture_count": len(fixtures),
        "public_output_count": len(passed["public_outputs"]),
        "canonical_archive_sha256": canonical["archive"]["sha256"],
        "canonical_interface_sha256": canonical["interface"]["sha256"],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Execute five deterministic invalid Phase Four package fixtures, "
            "prove fail-closed diagnosis, and revalidate canonical recovery."
        )
    )
    parser.add_argument("--repository-root", type=Path, default=Path.cwd())
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--report-directory", type=Path, required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    build = run_failure_injections(
        repository_root=args.repository_root,
        output_directory=args.output_directory,
        report_directory=args.report_directory,
        generated_at_utc=args.generated_at_utc,
        run_id=args.run_id,
        git_source_commit=args.git_source_commit,
    )
    print("PHASE_FIVE_FAILURE_INJECTION_PASS")
    print(f"RUN_ID={build['result']['run_id']}")
    print(f"INJECTION_COUNT={len(build['result']['injections'])}")
    print("CANONICAL_RECOVERY=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
