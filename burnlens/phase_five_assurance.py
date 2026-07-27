"""Run the Phase Five release-scoped assurance and performance gate."""

from __future__ import annotations

import argparse
from hashlib import sha256
from html import escape
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import re
import subprocess
from time import perf_counter
from typing import Any, Iterable
import unicodedata
import zipfile

from burnlens.phase_four_package import validate_package


REPORT_NAME = "PHASE-FIVE-ASSURANCE-2026-001.json"
HTML_NAME = "PHASE-FIVE-ASSURANCE-2026-001.html"
PACKAGE_DIRECTORY = Path(
    "samples/runs/phase-four/burnlens-ward-creek-rbr-run-v0.1.0"
)
PACKAGE_ARCHIVE = Path(
    "portfolio/phase-four/BURNLENS-WARD-CREEK-RBR-RUN-2026-001.zip"
)
INTERFACE_PATH = Path(
    "samples/qa/phase-five/reliability-interface-v0.1.0/"
    "PHASE-FIVE-RELIABILITY-INTERFACE-2026-001.html"
)
RUN_ID_PATTERN = re.compile(
    r"^BL-2026-07-26-p5o1-t01-u04-assurance-r[0-9]{3}$"
)
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")
SECRET_RULES = {
    "private-key-header": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "credential-assignment": re.compile(
        r"(?i)(?:api[_-]?key|client[_-]?secret|password|access[_-]?token|"
        r"authorization)[\"']?\s*[=:]\s*[\"']?[A-Za-z0-9+/_.=-]{12,}"
    ),
    "signed-or-tokenized-url": re.compile(
        r"(?i)https://[^\s\"'<>]+[?&](?:token|signature|sig|key|auth)="
    ),
}
PRIVACY_RULES = {
    "local-user-path": re.compile(r"(?i)(?:[A-Z]:\\Users\\|file:///C:/Users/)"),
    "email-address": re.compile(
        r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b"
    ),
    "private-delivery-marker": re.compile(
        r"(?i)(?:private retrieval url|recipient email|message[_ -]?id)"
        r"\s*[=:]\s*[\"']?(?!withheld|redacted)"
    ),
}
UNSUPPORTED_CLAIM_RULES = {
    "model-superiority": re.compile(r"(?i)\bU-Net outperformed RBR\b"),
    "operational-readiness": re.compile(
        r"(?i)\bBurnLens is (?:operational|emergency[- ]ready)\b"
    ),
    "field-validation": re.compile(r"(?i)\bBurnLens is field[- ]validated\b"),
    "official-status": re.compile(
        r"(?i)\bBurnLens is (?:official|endorsed)\b"
    ),
}
TRUE_BOUNDARY_KEYS = {
    "model_accepted",
    "model_outperformed_rbr",
    "official_operational_field_validated_endorsed_or_emergency_claim",
}


class PhaseFiveAssuranceError(RuntimeError):
    """The assurance gate failed closed."""


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
    with path.open("xb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())


def _run_checked(command: list[str], *, root: Path) -> dict[str, Any]:
    result = subprocess.run(
        command,
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )
    if result.returncode != 0:
        raise PhaseFiveAssuranceError(
            f"dependency-health command failed ({result.returncode}): "
            f"{' '.join(command)}"
        )
    return {"command": command, "exit_code": result.returncode, "status": "pass"}


def _text_payloads(package_root: Path) -> Iterable[tuple[str, str]]:
    for path in sorted(
        (item for item in package_root.rglob("*") if item.is_file()),
        key=lambda item: item.relative_to(package_root).as_posix().casefold(),
    ):
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        yield path.relative_to(package_root).as_posix(), text


def _scan_rules(
    payloads: list[tuple[str, str]], rules: dict[str, re.Pattern[str]]
) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for path, text in payloads:
        for rule_id, pattern in rules.items():
            if pattern.search(text):
                findings.append({"path": path, "rule_id": rule_id})
    return findings


def _walk_true_boundaries(value: Any, *, path: str = "$") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in TRUE_BOUNDARY_KEYS and child is True:
                findings.append(child_path)
            findings.extend(_walk_true_boundaries(child, path=child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(
                _walk_true_boundaries(child, path=f"{path}[{index}]")
            )
    return findings


def _claim_scan(payloads: list[tuple[str, str]]) -> dict[str, Any]:
    phrase_findings = _scan_rules(payloads, UNSUPPORTED_CLAIM_RULES)
    boundary_findings: list[dict[str, str]] = []
    for path, text in payloads:
        if not path.casefold().endswith((".json", ".geojson")):
            continue
        try:
            value = json.loads(text)
        except json.JSONDecodeError:
            continue
        for location in _walk_true_boundaries(value):
            boundary_findings.append({"path": path, "json_path": location})
    if phrase_findings or boundary_findings:
        raise PhaseFiveAssuranceError("unsupported public claim detected")
    return {
        "affirmative_phrase_findings": phrase_findings,
        "true_prohibited_boundary_findings": boundary_findings,
        "status": "pass",
    }


def _external_runtime_scan(interface_path: Path) -> dict[str, Any]:
    text = interface_path.read_text(encoding="utf-8")
    patterns = {
        "script-src": re.compile(
            r"(?is)<script\b[^>]*\bsrc\s*=\s*[\"'](?!data:)[^\"']+"
        ),
        "media-src": re.compile(
            r"(?is)<(?:img|iframe|audio|video|source)\b[^>]*\bsrc\s*="
            r"\s*[\"'](?!data:)[^\"']+"
        ),
        "stylesheet-href": re.compile(
            r"(?is)<link\b(?=[^>]*\brel\s*=\s*[\"']stylesheet[\"'])"
            r"[^>]*\bhref\s*=\s*[\"'](?!data:)[^\"']+"
        ),
        "css-url": re.compile(r"(?i)url\(\s*[\"']?(?!data:|#)[^)\"']+"),
        "network-api": re.compile(
            r"(?i)\b(?:fetch|XMLHttpRequest|WebSocket|EventSource)\s*\("
        ),
    }
    findings = [
        rule_id for rule_id, pattern in patterns.items() if pattern.search(text)
    ]
    if findings:
        raise PhaseFiveAssuranceError("external runtime request path detected")
    return {"finding_count": 0, "rules": sorted(patterns), "status": "pass"}


def _license_inventory(root: Path) -> dict[str, Any]:
    packages: list[dict[str, Any]] = []
    for distribution in importlib.metadata.distributions():
        name = distribution.metadata.get("Name")
        version = distribution.version
        if not name:
            continue
        expression = distribution.metadata.get("License-Expression")
        license_text = distribution.metadata.get("License")
        classifiers = sorted(
            item
            for item in distribution.metadata.get_all("Classifier", [])
            if item.startswith("License ::")
        )
        packages.append(
            {
                "name": name,
                "version": version,
                "license_expression": expression,
                "license": license_text,
                "license_classifiers": classifiers,
                "metadata_present": bool(expression or license_text or classifiers),
            }
        )
    packages.sort(key=lambda item: (item["name"].casefold(), item["version"]))
    project_license = root / "LICENSE"
    if not project_license.is_file():
        raise PhaseFiveAssuranceError("repository LICENSE is missing")
    return {
        "format": "release-scoped component and rights inventory; not SPDX",
        "project": {
            "name": "burnlens-deschutes",
            "license_expression": "MIT",
            "license_path": "LICENSE",
            "license_bytes": project_license.stat().st_size,
            "license_sha256": _sha256_file(project_license),
        },
        "environment_distribution_count": len(packages),
        "environment_distributions": packages,
        "missing_distribution_metadata_count": sum(
            not item["metadata_present"] for item in packages
        ),
        "dependencies_redistributed_in_phase_four_zip": False,
        "source_rights_evidence": (
            "evidence/records/u04-source-gate/"
            "PHASE-FOUR-CONTEXT-SOURCE-GATE-2026-001.json"
        ),
        "limitation": (
            "Installed-distribution metadata is supplier-provided inventory "
            "evidence, not legal advice or a claim that every transitive "
            "license obligation has been independently adjudicated."
        ),
    }


def _source_rights(package_root: Path) -> dict[str, Any]:
    relative = Path(
        "evidence/records/u04-source-gate/"
        "PHASE-FOUR-CONTEXT-SOURCE-GATE-2026-001.json"
    )
    record = json.loads((package_root / relative).read_text(encoding="utf-8"))
    sources = record.get("sources", [])
    rights = []
    for source in sources:
        criteria = {
            item.get("id"): item.get("status")
            for item in source.get("criteria", [])
        }
        rights.append(
            {
                "source_id": source.get("source_id"),
                "rights": criteria.get("rights"),
                "privacy_security": criteria.get("privacy-security"),
            }
        )
    if (
        record.get("decision", {}).get("status") != "ready"
        or not rights
        or any(
            item["rights"] != "pass"
            or item["privacy_security"] != "pass"
            for item in rights
        )
    ):
        raise PhaseFiveAssuranceError("source rights or privacy gate is unresolved")
    return {
        "record_path": relative.as_posix(),
        "record_sha256": _sha256_file(package_root / relative),
        "source_count": len(rights),
        "sources": rights,
        "status": "pass",
    }


def _vulnerability_classification(
    audit_path: Path, advisory_path: Path, *, root: Path, package_root: Path
) -> dict[str, Any]:
    audit = json.loads(audit_path.read_text(encoding="utf-8-sig"))
    advisory = json.loads(advisory_path.read_text(encoding="utf-8-sig"))
    expected_ghsa = advisory.get("ghsa_id")
    findings: dict[str, dict[str, Any]] = {}
    raw_vulnerability_count = 0
    for dependency in audit.get("dependencies", []):
        for vulnerability in dependency.get("vulns", []):
            raw_vulnerability_count += 1
            aliases = set(vulnerability.get("aliases", []))
            key = next(
                (
                    item
                    for item in sorted(aliases)
                    if item.startswith("GHSA-")
                ),
                vulnerability.get("id"),
            )
            findings.setdefault(
                key,
                {
                    "package": dependency.get("name"),
                    "version": dependency.get("version"),
                    "id": vulnerability.get("id"),
                    "aliases": sorted(aliases),
                    "fix_versions": vulnerability.get("fix_versions", []),
                },
            )
    if set(findings) != {expected_ghsa}:
        raise PhaseFiveAssuranceError(
            f"unclassified vulnerability roster: {sorted(findings)}"
        )
    tracked = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=root,
        capture_output=True,
        check=True,
    ).stdout.decode("utf-8").split("\0")
    tracked = [item for item in tracked if item]
    mitigation = {
        "windows_ntfs_route": platform.system() == "Windows",
        "manifest_in_absent": not (root / "MANIFEST.in").exists(),
        "tracked_paths_unicode_normalized": all(
            item == unicodedata.normalize("NFC", item) for item in tracked
        ),
        "tracked_paths_ascii_only": all(item.isascii() for item in tracked),
        "sdist_absent_from_release_package": not any(
            path.name.endswith((".tar.gz", ".tar.bz2"))
            for path in package_root.rglob("*")
        ),
        "release_format_zip_only": True,
    }
    if not all(mitigation.values()):
        raise PhaseFiveAssuranceError("setuptools advisory mitigation drift")
    severity = advisory.get("severity")
    if severity in {"critical", "high"}:
        raise PhaseFiveAssuranceError(
            f"unresolved {severity} vulnerability in release scope"
        )
    return {
        "scanner": "pip-audit 2.10.1",
        "audit_path": audit_path.name,
        "audit_bytes": audit_path.stat().st_size,
        "audit_sha256": _sha256_file(audit_path),
        "dependency_count": len(audit.get("dependencies", [])),
        "raw_vulnerability_count": raw_vulnerability_count,
        "unique_advisory_count": len(findings),
        "findings": list(findings.values()),
        "classification": {
            "ghsa_id": advisory.get("ghsa_id"),
            "cve_id": advisory.get("cve_id"),
            "severity": severity,
            "cvss": advisory.get("cvss"),
            "published_at": advisory.get("published_at"),
            "fixed_version": advisory.get("vulnerabilities", [{}])[0].get(
                "first_patched_version"
            ),
            "advisory_bytes": advisory_path.stat().st_size,
            "advisory_sha256": _sha256_file(advisory_path),
            "mitigation": mitigation,
            "disposition": (
                "disclosed medium finding; current Windows ZIP-only release "
                "route does not exercise the macOS sdist exclusion path"
            ),
        },
        "known_vulnerability_free_claim": False,
        "status": "pass-with-disclosed-medium-finding",
    }


def _performance(
    package_directory: Path, package_archive: Path, interface_path: Path
) -> dict[str, Any]:
    samples: dict[str, list[float]] = {"directory": [], "archive": []}
    for label, path in (
        ("directory", package_directory),
        ("archive", package_archive),
    ):
        for _ in range(3):
            started = perf_counter()
            result = validate_package(path)
            elapsed = perf_counter() - started
            if result.get("result") != "PACKAGE_VALIDATION_PASS":
                raise PhaseFiveAssuranceError("canonical package validation failed")
            samples[label].append(round(elapsed, 6))
    extracted_bytes = sum(
        item.stat().st_size
        for item in package_directory.rglob("*")
        if item.is_file()
    )
    maximum = max(value for values in samples.values() for value in values)
    budgets = {
        "archive_bytes": {
            "actual": package_archive.stat().st_size,
            "maximum": 750_000,
        },
        "extracted_bytes": {"actual": extracted_bytes, "maximum": 2_500_000},
        "interface_html_bytes": {
            "actual": interface_path.stat().st_size,
            "maximum": 250_000,
        },
        "package_validation_seconds": {"actual_max": maximum, "maximum": 5.0},
    }
    if any(
        item.get("actual", item.get("actual_max")) > item["maximum"]
        for item in budgets.values()
    ):
        raise PhaseFiveAssuranceError("performance budget exceeded")
    return {
        "samples_seconds": samples,
        "budgets": budgets,
        "status": "pass",
        "basis": (
            "Project-specific offline reviewer-path budgets; not universal "
            "web performance standards."
        ),
    }


def build_report(
    *,
    repository_root: Path,
    audit_path: Path,
    advisory_path: Path,
    run_id: str,
    generated_at_utc: str,
    git_source_commit: str,
) -> dict[str, Any]:
    root = repository_root.resolve()
    if not RUN_ID_PATTERN.fullmatch(run_id):
        raise PhaseFiveAssuranceError("run ID does not match U04 contract")
    if not COMMIT_PATTERN.fullmatch(git_source_commit):
        raise PhaseFiveAssuranceError("git source commit is invalid")
    package_root = root / PACKAGE_DIRECTORY
    archive = root / PACKAGE_ARCHIVE
    interface = root / INTERFACE_PATH
    for path in (package_root, archive, interface, audit_path, advisory_path):
        if not path.exists():
            raise PhaseFiveAssuranceError(f"required input missing: {path}")
    payloads = list(_text_payloads(package_root))
    secret_findings = _scan_rules(payloads, SECRET_RULES)
    privacy_findings = _scan_rules(payloads, PRIVACY_RULES)
    if secret_findings:
        raise PhaseFiveAssuranceError("secret-like material detected")
    if privacy_findings:
        raise PhaseFiveAssuranceError("private material detected")
    dependency_health = [
        _run_checked(["uv", "lock", "--check"], root=root),
        _run_checked(
            [
                "uv",
                "pip",
                "check",
                "--python",
                str(root / ".venv/Scripts/python.exe"),
            ],
            root=root,
        ),
    ]
    report = {
        "report_version": "burnlens-phase-five-assurance-v0.1.0",
        "report_id": "PHASE-FIVE-ASSURANCE-2026-001",
        "milestone_id": "P5O1-T01",
        "unit_id": "P5O1-T01-U04",
        "issue": 574,
        "run_id": run_id,
        "generated_at_utc": generated_at_utc,
        "git_source_commit": git_source_commit,
        "release_scope": {
            "archive": {
                "path": PACKAGE_ARCHIVE.as_posix(),
                "bytes": archive.stat().st_size,
                "sha256": _sha256_file(archive),
            },
            "extracted": PACKAGE_DIRECTORY.as_posix(),
            "interface": {
                "path": INTERFACE_PATH.as_posix(),
                "bytes": interface.stat().st_size,
                "sha256": _sha256_file(interface),
            },
            "accepted_method": "burnlens-baseline-v0.1.0",
            "rejected_diagnostic": "burnlens-unet-binary-v0.1.0",
        },
        "checks": {
            "dependency_health": {
                "commands": dependency_health,
                "status": "pass",
            },
            "known_vulnerability_classification": _vulnerability_classification(
                audit_path,
                advisory_path,
                root=root,
                package_root=package_root,
            ),
            "secret_scan": {
                "finding_count": 0,
                "rules": sorted(SECRET_RULES),
                "scope": "text-decodable files in the canonical release package",
                "status": "pass",
            },
            "license_inventory": _license_inventory(root),
            "source_rights": _source_rights(package_root),
            "unsupported_claim_scan": _claim_scan(payloads),
            "public_artifact_privacy": {
                "finding_count": 0,
                "rules": sorted(PRIVACY_RULES),
                "scope": "text-decodable files in the canonical release package",
                "status": "pass",
            },
            "safe_archive_structure": {
                "validator": "burnlens.phase_four_package.validate_package",
                "status": "pass",
            },
            "schema_and_binding_validation": {
                "validator": "burnlens.phase_four_package.validate_package",
                "status": "pass",
            },
            "checksum_validation": {
                "validator": "burnlens.phase_four_package.validate_package",
                "status": "pass",
            },
            "no_external_runtime_request": _external_runtime_scan(interface),
            "performance": _performance(package_root, archive, interface),
        },
        "limitations": [
            "The dependency scan reports known advisories present in its configured feeds at scan time; it is not a vulnerability-free claim.",
            "The license inventory records supplier metadata and source-rights evidence; it is not legal advice.",
            "Pattern-based secret, privacy, and claim scans supplement rather than replace exact package bindings and human review.",
            "Performance timings describe this machine and bounded offline package, not a universal browser or service benchmark.",
            "The U-Net remains a rejected diagnostic and did not outperform RBR.",
        ],
        "boundaries": {
            "analytical_output_changed": False,
            "model_accepted": False,
            "model_outperformed_rbr": False,
            "operational_claim": False,
            "field_validation_claim": False,
            "official_or_endorsed_claim": False,
            "deployment": False,
            "public_sharing_change": False,
        },
        "disposition": "pass-with-disclosed-medium-finding",
        "next_dependency": "P5O1-T01-U05",
    }
    return report


def render_html(report: dict[str, Any]) -> bytes:
    vulnerability = report["checks"]["known_vulnerability_classification"]
    performance = report["checks"]["performance"]
    rows = []
    for name, value in report["checks"].items():
        status = value.get("status", "recorded")
        rows.append(
            f"<tr><th scope=\"row\">{escape(name.replace('_', ' '))}</th>"
            f"<td>{escape(status)}</td></tr>"
        )
    budgets = []
    for name, value in performance["budgets"].items():
        actual = value.get("actual", value.get("actual_max"))
        budgets.append(
            f"<tr><th scope=\"row\">{escape(name.replace('_', ' '))}</th>"
            f"<td>{escape(str(actual))}</td><td>{escape(str(value['maximum']))}</td></tr>"
        )
    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; img-src data:">
<title>BurnLens Phase Five assurance</title>
<style>
body{{margin:0;background:#0b1115;color:#eef5f7;font:16px/1.55 system-ui,sans-serif}}
main{{max-width:960px;margin:auto;padding:2rem 1rem 4rem}}h1,h2{{line-height:1.15}}
.card{{background:#142028;border:1px solid #486171;border-radius:12px;padding:1rem;margin:1rem 0}}
.pass{{color:#9ee6b8;font-weight:700}}.warn{{color:#ffd27d;font-weight:700}}
table{{width:100%;border-collapse:collapse}}th,td{{padding:.55rem;border-bottom:1px solid #486171;text-align:left;vertical-align:top}}
code{{overflow-wrap:anywhere}}a{{color:#9bd7ff}}:focus-visible{{outline:3px solid #ffdc73;outline-offset:3px}}
@media(max-width:480px){{main{{padding:1rem .7rem 3rem}}th,td{{padding:.45rem .3rem}}}}
</style></head><body><main>
<h1>BurnLens Phase Five assurance</h1>
<p class="pass">PASS with one disclosed medium dependency finding.</p>
<section class="card"><h2>Release route</h2>
<p>Accepted: <code>burnlens-baseline-v0.1.0</code>. The trained U-Net remains a rejected diagnostic and did not outperform RBR.</p>
<p>Run: <code>{escape(report['run_id'])}</code><br>Source commit: <code>{escape(report['git_source_commit'])}</code><br>Archive SHA-256: <code>{escape(report['release_scope']['archive']['sha256'])}</code></p></section>
<section class="card"><h2>Assurance checks</h2><table><tbody>{''.join(rows)}</tbody></table></section>
<section class="card"><h2>Known dependency finding</h2>
<p class="warn">{escape(vulnerability['classification']['ghsa_id'])} / {escape(vulnerability['classification']['cve_id'])}, severity {escape(vulnerability['classification']['severity'])}.</p>
<p>{escape(vulnerability['classification']['disposition'])}. This is disclosed, not suppressed, and no vulnerability-free claim is made.</p></section>
<section class="card"><h2>Performance budgets</h2><table><thead><tr><th>Measure</th><th>Observed</th><th>Maximum</th></tr></thead><tbody>{''.join(budgets)}</tbody></table>
<p>{escape(performance['basis'])}</p></section>
<section class="card"><h2>Interpretation limits</h2><ul>{''.join(f'<li>{escape(item)}</li>' for item in report['limitations'])}</ul></section>
</main></body></html>"""
    return html.encode("utf-8")


def run_assurance(
    *,
    repository_root: Path,
    audit_path: Path,
    advisory_path: Path,
    run_id: str,
    generated_at_utc: str,
    git_source_commit: str,
    output_directory: Path,
) -> dict[str, Any]:
    report = build_report(
        repository_root=repository_root,
        audit_path=audit_path,
        advisory_path=advisory_path,
        run_id=run_id,
        generated_at_utc=generated_at_utc,
        git_source_commit=git_source_commit,
    )
    report_bytes = _json_bytes(report)
    html_bytes = render_html(report)
    _write_new(output_directory / REPORT_NAME, report_bytes)
    _write_new(output_directory / HTML_NAME, html_bytes)
    return {
        "report": report,
        "json": {
            "bytes": len(report_bytes),
            "sha256": sha256(report_bytes).hexdigest(),
        },
        "html": {
            "bytes": len(html_bytes),
            "sha256": sha256(html_bytes).hexdigest(),
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--audit-json", type=Path, required=True)
    parser.add_argument("--advisory-json", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--git-source-commit", required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = run_assurance(
            repository_root=args.repository_root,
            audit_path=args.audit_json.resolve(),
            advisory_path=args.advisory_json.resolve(),
            run_id=args.run_id,
            generated_at_utc=args.generated_at_utc,
            git_source_commit=args.git_source_commit,
            output_directory=args.output_directory.resolve(),
        )
    except (OSError, ValueError, PhaseFiveAssuranceError) as exc:
        print(f"PHASE_FIVE_ASSURANCE_FAIL: {exc}")
        return 1
    print("PHASE_FIVE_ASSURANCE_PASS")
    print(f"JSON_SHA256={result['json']['sha256']}")
    print(f"HTML_SHA256={result['html']['sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
