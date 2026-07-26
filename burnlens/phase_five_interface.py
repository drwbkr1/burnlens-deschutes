"""Build the Phase Five reliability-hardened reviewer interface."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import subprocess
from typing import Any


INTERFACE_VERSION = "burnlens-phase-five-reliability-interface-v0.1.0"
REPORT_ID = "PHASE-FIVE-RELIABILITY-INTERFACE-2026-001"
OUTPUT_HTML = f"{REPORT_ID}.html"
OUTPUT_JSON = f"{REPORT_ID}.json"
RUN_ID_PATTERN = re.compile(
    r"^BL-2026-07-26-p5o1-t01-u03-reliability-interface-r[0-9]{3}$"
)
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")
BASE_INTERFACE = Path(
    "samples/runs/phase-four/"
    "burnlens-geoint-evidence-interface-v0.1.0/"
    "PHASE-FOUR-EVIDENCE-INTERFACE-2026-001.html"
)
BASE_INTERFACE_BYTES = 177_666
BASE_INTERFACE_SHA256 = (
    "7a657ad772b34ff42cf4f4024a585b70fb8e7f41bab363cd056fcf8059825fb7"
)
FAILURE_REPORT = Path(
    "samples/qa/phase-five/failure-injection-v0.1.0/"
    "PHASE-FIVE-FAILURE-INJECTION-2026-001.json"
)
FAILURE_REPORT_BYTES = 4_590
FAILURE_REPORT_SHA256 = (
    "1c00be85907aa8e965b16a8520b5493cf8421b52f6c6abf7f225aeee0c7ee4b4"
)


class PhaseFiveInterfaceError(RuntimeError):
    """The reliability interface could not be built without drift."""


def _sha256_bytes(payload: bytes) -> str:
    return sha256(payload).hexdigest()


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(
        "utf-8"
    )


def _exact(path: Path, expected_bytes: int, expected_hash: str) -> bytes:
    if not path.is_file():
        raise PhaseFiveInterfaceError(f"input missing: {path}")
    payload = path.read_bytes()
    if len(payload) != expected_bytes or _sha256_bytes(payload) != expected_hash:
        raise PhaseFiveInterfaceError(f"input drift: {path}")
    return payload


def _replace_once(value: str, old: str, new: str) -> str:
    if value.count(old) != 1:
        raise PhaseFiveInterfaceError(f"expected one interface token: {old}")
    return value.replace(old, new)


def _linear(channel: int) -> float:
    value = channel / 255
    return value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4


def _luminance(color: str) -> float:
    red, green, blue = (
        int(color[index : index + 2], 16) for index in (1, 3, 5)
    )
    return (
        0.2126 * _linear(red)
        + 0.7152 * _linear(green)
        + 0.0722 * _linear(blue)
    )


def _contrast(foreground: str, background: str) -> float:
    first, second = sorted(
        (_luminance(foreground), _luminance(background)),
        reverse=True,
    )
    return round((first + 0.05) / (second + 0.05), 3)


def build_interface(
    *,
    repository_root: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, Any]:
    root = repository_root.resolve()
    if not RUN_ID_PATTERN.fullmatch(run_id):
        raise PhaseFiveInterfaceError("run ID drift")
    if not COMMIT_PATTERN.fullmatch(git_source_commit):
        raise PhaseFiveInterfaceError("git source commit drift")
    base_bytes = _exact(
        root / BASE_INTERFACE,
        BASE_INTERFACE_BYTES,
        BASE_INTERFACE_SHA256,
    )
    failure_bytes = _exact(
        root / FAILURE_REPORT,
        FAILURE_REPORT_BYTES,
        FAILURE_REPORT_SHA256,
    )
    failure = json.loads(failure_bytes)
    if (
        failure.get("disposition") != "pass"
        or len(failure.get("injections", [])) != 5
    ):
        raise PhaseFiveInterfaceError("failure report semantic drift")

    html = base_bytes.decode("utf-8")
    html = _replace_once(
        html,
        '<a class="skip" href="#map">Skip to map</a>',
        '<a class="skip" href="#main-content">Skip to main evidence</a>',
    )
    html = _replace_once(
        html,
        "<main>",
        '<main id="main-content" tabindex="-1">',
    )
    html = _replace_once(
        html,
        '<g id="rejected-unet" data-layer="rejected-unet">',
        '<g id="rejected-unet" data-layer="rejected-unet" hidden>',
    )
    html = _replace_once(
        html,
        "</style>",
        ".review-path{background:#102a25;border:1px solid var(--teal);"
        "border-radius:14px;padding:1rem 1.2rem;margin:0 0 1.4rem}"
        ".review-path h2{margin:.1rem 0 .4rem;font-size:1.25rem}"
        ".review-path ol{margin:.4rem 0;padding-left:1.3rem}"
        ".review-path li+li{margin-top:.35rem}"
        "[hidden]{display:none!important}"
        "#main-content:focus{outline:4px solid var(--focus);outline-offset:4px}"
        "</style>",
    )
    warning = (
        '<div class="warning" role="note"><strong>Experimental and '
        "non-operational.</strong>Owner-approved prototype regions are not "
        "independent ground truth. This interface is not official, "
        "field-validated, endorsed, operational, or suitable for routing, "
        "closure, tactical, property, legal, safety, or emergency decisions. "
        "Official sources govern their own facts.</div>"
    )
    review = (
        warning
        + '<section class="review-path" aria-labelledby="review-path-heading">'
        '<h2 id="review-path-heading">Four-step reviewer path</h2><ol>'
        "<li>Read the experimental-use warning and analytical posture.</li>"
        "<li>Compare WCP-001 with the visible WCP-002 false-positive case.</li>"
        "<li>Turn on the rejected U-Net only if you want diagnostic context.</li>"
        "<li>Inspect run states, exact lineage, and failure-injection evidence."
        "</li></ol></section>"
        "<noscript><div class=\"warning\" role=\"alert\"><strong>Interactive "
        "controls are unavailable because JavaScript is off.</strong> "
        "Accepted RBR and the complete textual equivalent remain visible. "
        "The rejected U-Net stays hidden and is not promoted.</div></noscript>"
    )
    html = _replace_once(html, warning, review)

    reliability_section = (
        '<section id="reliability" aria-labelledby="reliability-heading">'
        '<div class="section-head"><p class="eyebrow">Phase Five reliability'
        '</p><h2 id="reliability-heading">Five invalid packages fail before '
        "they can look accepted.</h2><p>Missing, corrupt, path-traversal, "
        "binding-mismatched, and partial fixtures are all rejected with exact "
        "diagnoses. Both untouched canonical package forms revalidate after "
        "every injection.</p></div><div class=\"compare\"><article "
        "class=\"panel\"><h3>Safe recovery</h3><ul><li>Zero path escape.</li>"
        "<li>Zero accepted output from invalid input.</li><li>Canonical ZIP "
        "<code>91308a2f...</code> remains unchanged.</li></ul></article>"
        '<article class="panel failure"><h3>Retained pre-fix defects</h3><ul>'
        "<li>A partial package leaked an uncontrolled filesystem error.</li>"
        "<li>A wrong method, route, and run binding unexpectedly passed.</li>"
        "<li>Both defects are fixed and remain visible in the U02 record.</li>"
        "</ul></article></div></section>"
    )
    html = _replace_once(
        html,
        '<section id="trace" aria-labelledby="trace-heading">',
        reliability_section
        + '<section id="trace" aria-labelledby="trace-heading">',
    )
    html = html.replace(
        "Phase Four - local/offline evidence interface",
        "Phase Five - reliability-hardened local/offline interface",
        1,
    )
    html = html.replace(
        "burnlens-phase-four-interface-v0.1.0",
        INTERFACE_VERSION,
    )
    html = html.replace(
        "BL-2026-07-26-p4o1-t01-u06-interface-r002",
        run_id,
    )
    html = html.replace(
        "5072a57bc75f63ebb9b66dd5a2173b6b290473d8",
        git_source_commit,
    )
    html = _replace_once(
        html,
        "<strong>BurnLens 0.53.0</strong>",
        "<strong>BurnLens 0.54.0 reliability candidate</strong>",
    )
    html_bytes = html.encode("utf-8")

    contrast_pairs = [
        ("body-text", "#eaf1ec", "#0c1614", 4.5),
        ("muted-text", "#aebdb6", "#14221f", 4.5),
        ("focus-indicator", "#fff27a", "#14221f", 3.0),
        ("accepted-accent", "#ff9d42", "#14221f", 3.0),
        ("rejected-accent", "#ff66c4", "#14221f", 3.0),
    ]
    contrast = [
        {
            "name": name,
            "foreground": foreground,
            "background": background,
            "ratio": _contrast(foreground, background),
            "minimum": minimum,
            "pass": _contrast(foreground, background) >= minimum,
        }
        for name, foreground, background, minimum in contrast_pairs
    ]
    if not all(item["pass"] for item in contrast):
        raise PhaseFiveInterfaceError("declared contrast pair failed")
    checks = {
        "skip_target_focusable": 'id="main-content" tabindex="-1"' in html,
        "rejected_unet_hidden_without_script": (
            'id="rejected-unet" data-layer="rejected-unet" hidden' in html
        ),
        "no_script_explanation": "<noscript>" in html,
        "keyboard_native_controls": (
            html.count('<button type="button"') == 3
            and html.count('type="checkbox"') == 6
            and html.count('type="range"') == 6
        ),
        "focus_visible": "outline:4px solid var(--focus)" in html,
        "text_equivalent": 'id="text-equivalent"' in html,
        "non_color_failure_language": (
            "visible baseline failure evidence" in html
            and "Retained pre-fix defects" in html
        ),
        "narrow_reflow": "@media(max-width:620px)" in html,
        "reduced_motion": "@media(prefers-reduced-motion:reduce)" in html,
        "offline_csp": "connect-src 'none'" in html,
        "external_runtime_reference": bool(
            re.search(r'(?:src|href)="https?://', html.lower())
        ),
    }
    if (
        not all(value for key, value in checks.items() if key != "external_runtime_reference")
        or checks["external_runtime_reference"]
    ):
        raise PhaseFiveInterfaceError("interface accessibility/offline drift")
    report = {
        "report_version": INTERFACE_VERSION,
        "report_id": REPORT_ID,
        "milestone_id": "P5O1-T01",
        "unit_id": "P5O1-T01-U03",
        "run_id": run_id,
        "generated_at_utc": generated_at_utc,
        "git_source_commit": git_source_commit,
        "base_interface": {
            "path": BASE_INTERFACE.as_posix(),
            "bytes": len(base_bytes),
            "sha256": _sha256_bytes(base_bytes),
        },
        "failure_report": {
            "path": FAILURE_REPORT.as_posix(),
            "bytes": len(failure_bytes),
            "sha256": _sha256_bytes(failure_bytes),
        },
        "output_html": {
            "path": OUTPUT_HTML,
            "bytes": len(html_bytes),
            "sha256": _sha256_bytes(html_bytes),
        },
        "checks": checks,
        "contrast": contrast,
        "owner_render_evidence": {
            "canonical_interface_sha256": BASE_INTERFACE_SHA256,
            "canonical_render_confirmed": True,
            "hardened_interface_render": "pending exact owner/browser review",
            "automation_file_url_block_retained": True,
            "browser_policy_bypass_prohibited": True,
        },
        "boundaries": {
            "analytical_output_changed": False,
            "accepted_method_changed": False,
            "rejected_model_promoted": False,
            "model_outperformed_rbr": False,
            "deployment": False,
            "public_sharing_change": False,
        },
        "disposition": "pending-render-review",
        "next_dependency": "Exact desktop and narrow rendered/keyboard review"
    }
    return {
        "report": report,
        "outputs": {
            OUTPUT_HTML: html_bytes,
            OUTPUT_JSON: _json_bytes(report),
        },
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
    except Exception:
        if created and path.exists():
            path.unlink()
        raise


def run_interface(
    *,
    repository_root: Path,
    output_directory: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
    require_clean: bool = True,
) -> dict[str, Any]:
    root = repository_root.resolve()
    output = output_directory.resolve()
    if output.exists() and any(output.iterdir()):
        raise PhaseFiveInterfaceError(
            f"refusing to overwrite nonempty output: {output}"
        )
    if require_clean:
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        status = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=all"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        if head != git_source_commit or status:
            raise PhaseFiveInterfaceError(
                "clean exact HEAD required for U03 execution"
            )
    build = build_interface(
        repository_root=root,
        generated_at_utc=generated_at_utc,
        run_id=run_id,
        git_source_commit=git_source_commit,
    )
    for name, payload in build["outputs"].items():
        _write_new(output / name, payload)
    return build


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build the Phase Five reliability-hardened interface."
    )
    parser.add_argument("--repository-root", type=Path, default=Path.cwd())
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    build = run_interface(
        repository_root=args.repository_root,
        output_directory=args.output_directory,
        generated_at_utc=args.generated_at_utc,
        run_id=args.run_id,
        git_source_commit=args.git_source_commit,
    )
    print("PHASE_FIVE_RELIABILITY_INTERFACE_BUILD_PASS")
    print(f"RUN_ID={build['report']['run_id']}")
    print(f"HTML_BYTES={build['report']['output_html']['bytes']}")
    print(f"HTML_SHA256={build['report']['output_html']['sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
