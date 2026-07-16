"""Run and render a real-browser acceptance check for the offline review handoff."""

from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from html import escape
import json
from pathlib import Path
import subprocess
from typing import Any
import zipfile

from PIL import Image, ImageDraw, ImageOps

from .label_review_handoff import (
    ARCHIVE_ROOT,
    EXPECTED_PACKET_ID,
    EXPECTED_PACKET_RUN_ID,
    HANDOFF_HTML_NAME,
    WORKBENCH_VERSION,
)
from .lock_label_review_response import (
    LEGACY_LOCK_REPORT_VERSION,
    LEGACY_SOFTWARE_VERSION,
    SOFTWARE_BROWSER_FIXTURE,
    build_response_lock,
    write_response_lock,
)
from .optical_pair_evidence import WARNING, _font
from .verify_label_review_handoff import (
    LabelReviewHandoffVerificationError,
    build_qa_report as verify_handoff,
)
from .verify_label_review_packet import validate_completed_response


SOFTWARE_VERSION = "0.15.0"
TASK_ISSUE = 383
BROWSER_QA_ID = "LABEL-REVIEW-BROWSER-QA-2026-001"
BROWSER_QA_SCHEMA_VERSION = "0.1.0"
BROWSER_QA_VERSION = "label-review-live-browser-qa-v0.1.0"
OBSERVATION_SCHEMA_VERSION = "burnlens-label-review-browser-observation-v0.1.0"
EXPECTED_REVIEWER_ID = "browser-qa-fixture-not-human"
EXPECTED_EXPERIENCE = "Automated browser QA fixture; not a human response."
EXPECTED_UNIT_COUNT = 56
EXPECTED_BLIND_PAGE_COUNT = 8
EXPECTED_EMPTY_ERROR_COUNT = 61
EXPECTED_PARTIAL_PROGRESS = "7 of 56 units complete"
EXPECTED_COMPLETE_PROGRESS = "56 of 56 units complete"
EXPECTED_LABEL_COUNTS = {
    "background": 14,
    "burned": 14,
    "uncertain": 14,
    "unusable": 14,
}
PUBLIC_DESKTOP_NAME = f"{BROWSER_QA_ID}-DESKTOP.png"
PUBLIC_MOBILE_NAME = f"{BROWSER_QA_ID}-MOBILE.png"


class LabelReviewBrowserQaError(RuntimeError):
    """A secret-free live-browser QA failure."""


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise LabelReviewBrowserQaError(f"invalid JSON input {path.name}") from error
    if not isinstance(value, dict):
        raise LabelReviewBrowserQaError(f"JSON input {path.name} is not an object")
    return value


def _write_utf8_lf(path: Path, text: str) -> None:
    if path.exists():
        raise LabelReviewBrowserQaError(f"refusing to overwrite existing output {path.name}")
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")
    path.write_bytes(payload)


def _copy_new(source: Path, target: Path) -> None:
    if target.exists():
        raise LabelReviewBrowserQaError(f"refusing to overwrite existing output {target.name}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(source.read_bytes())


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _parse_timestamp(value: str, label: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise LabelReviewBrowserQaError(f"{label} timestamp is invalid") from error
    if parsed.tzinfo is None:
        raise LabelReviewBrowserQaError(f"{label} timestamp must be timezone-aware")
    return parsed


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise LabelReviewBrowserQaError(message)


def _snapshot_checks(snapshot: dict[str, Any], *, mobile: bool = False) -> None:
    _assert(snapshot.get("title") == "BurnLens offline label-review workbench", "browser title differs")
    _assert(snapshot.get("ready_state") == "complete", "browser document is not complete")
    _assert(snapshot.get("unit_fieldsets") == EXPECTED_UNIT_COUNT, "browser unit coverage differs")
    _assert(snapshot.get("blind_images") == EXPECTED_BLIND_PAGE_COUNT, "browser image count differs")
    _assert(
        snapshot.get("loaded_blind_images") == EXPECTED_BLIND_PAGE_COUNT,
        "not all blind images loaded in the browser",
    )
    _assert(snapshot.get("horizontal_overflow") is False, "browser viewport has horizontal overflow")
    _assert(snapshot.get("local_storage_entries") == 0, "browser workbench persisted local storage")
    _assert(snapshot.get("cookie") == "", "browser workbench created a cookie")
    if mobile:
        _assert(snapshot.get("viewport_width") == 390, "mobile viewport width differs")
        _assert(snapshot.get("viewport_height") == 844, "mobile viewport height differs")
    else:
        _assert(snapshot.get("viewport_width") == 1440, "desktop viewport width differs")
        _assert(snapshot.get("viewport_height") == 1000, "desktop viewport height differs")


def _validate_observation(
    observation: dict[str, Any],
    *,
    draft_path: Path,
    response_path: Path,
    desktop_path: Path,
    mobile_path: Path,
) -> dict[str, Any]:
    _assert(
        observation.get("observation_schema_version") == OBSERVATION_SCHEMA_VERSION,
        "browser observation schema differs",
    )
    browser = observation.get("browser")
    _assert(isinstance(browser, dict), "browser identity is missing")
    _assert(
        isinstance(browser.get("product"), str)
        and (
            browser["product"].startswith("Chrome/")
            or browser["product"].startswith("Edg/")
            or browser["product"].startswith("HeadlessChrome/")
        ),
        "browser product is not an accepted current Chromium identity",
    )
    _assert(
        isinstance(observation.get("node_version"), str)
        and observation["node_version"].startswith("v"),
        "Node runtime identity is missing",
    )
    input_binding = observation.get("input", {})
    _assert(input_binding.get("html_filename") == HANDOFF_HTML_NAME, "browser HTML binding differs")
    _assert(input_binding.get("packet_id") == EXPECTED_PACKET_ID, "browser packet binding differs")
    _assert(
        input_binding.get("packet_run_id") == EXPECTED_PACKET_RUN_ID,
        "browser packet run binding differs",
    )

    initial = observation.get("initial", {})
    _snapshot_checks(initial)
    _assert(initial.get("progress") == "0 of 56 units complete", "initial progress differs")

    invalid = observation.get("invalid_state", {})
    review = invalid.get("review", {})
    blocked = invalid.get("blocked_export", {})
    _assert(review.get("invalid_cards") == EXPECTED_UNIT_COUNT, "empty review did not flag all units")
    _assert(review.get("error_summary_visible") is True, "empty review did not show errors")
    _assert(
        f"{EXPECTED_EMPTY_ERROR_COUNT} issue(s)" in review.get("error_summary", ""),
        "empty review error count differs",
    )
    _assert(review.get("active_element_id") == "error-summary", "empty review did not focus errors")
    _assert(
        blocked.get("review_summary") == "Export blocked until all issues are corrected.",
        "incomplete export was not visibly blocked",
    )
    _assert(invalid.get("response_file_created") is False, "incomplete export created a response")

    draft = observation.get("draft_roundtrip", {})
    _assert(draft.get("partial_progress") == EXPECTED_PARTIAL_PROGRESS, "draft partial progress differs")
    _assert(draft.get("draft_completed") is False, "downloaded draft is marked complete")
    _assert(draft.get("draft_response_count") == EXPECTED_UNIT_COUNT, "draft coverage differs")
    _assert(draft.get("cleared", {}).get("progress") == "0 of 56 units complete", "form clear failed")
    restored = draft.get("restored", {})
    _assert(
        restored.get("snapshot", {}).get("progress") == EXPECTED_PARTIAL_PROGRESS,
        "draft load did not restore progress",
    )
    _assert(restored.get("reviewer_id") == EXPECTED_REVIEWER_ID, "draft reviewer ID did not restore")
    _assert(
        restored.get("reviewer_experience") == EXPECTED_EXPERIENCE,
        "draft reviewer experience did not restore",
    )
    _assert(restored.get("first_label") == "burned", "draft first unit did not restore")
    _assert(draft_path.is_file(), "browser draft file is missing")
    _assert(draft.get("draft_bytes") == draft_path.stat().st_size, "draft byte binding differs")
    _assert(draft.get("draft_sha256") == _sha256_file(draft_path), "draft SHA-256 differs")

    completed = observation.get("completed_roundtrip", {})
    _assert(
        completed.get("progress_before_review") == EXPECTED_COMPLETE_PROGRESS,
        "completed progress differs",
    )
    completed_review = completed.get("review", {})
    _assert(completed_review.get("progress") == EXPECTED_COMPLETE_PROGRESS, "review progress differs")
    _assert(completed_review.get("invalid_cards") == 0, "complete review retained invalid units")
    _assert(completed_review.get("error_summary_visible") is False, "complete review retained errors")
    _assert(
        completed_review.get("review_summary", "").startswith(
            "All 56 units and attestations are complete."
        ),
        "complete review summary differs",
    )
    _assert(completed.get("response_completed") is True, "exported response is not complete")
    _assert(completed.get("response_reviewer_id") == EXPECTED_REVIEWER_ID, "response reviewer differs")
    _assert(completed.get("response_count") == EXPECTED_UNIT_COUNT, "response coverage differs")
    _assert(completed.get("label_counts") == EXPECTED_LABEL_COUNTS, "fixture label counts differ")
    _assert(response_path.is_file(), "browser response file is missing")
    _assert(completed.get("response_bytes") == response_path.stat().st_size, "response bytes differ")
    _assert(completed.get("response_sha256") == _sha256_file(response_path), "response SHA-256 differs")

    viewports = observation.get("viewports", {})
    desktop = viewports.get("desktop", {})
    mobile = viewports.get("mobile", {})
    _snapshot_checks(desktop)
    _snapshot_checks(mobile, mobile=True)
    for path, key in (
        (desktop_path, "desktop_screenshot"),
        (mobile_path, "mobile_screenshot"),
    ):
        binding = viewports.get(key, {})
        _assert(path.is_file(), f"{key} is missing")
        _assert(binding.get("bytes") == path.stat().st_size, f"{key} byte binding differs")
        _assert(binding.get("sha256") == _sha256_file(path), f"{key} SHA-256 differs")
        with Image.open(path) as image:
            image.verify()

    runtime = observation.get("runtime", {})
    _assert(runtime.get("console_error_count") == 0, "browser console errors were observed")
    _assert(runtime.get("runtime_exception_count") == 0, "browser runtime exceptions were observed")
    _assert(runtime.get("log_error_count") == 0, "browser log errors were observed")
    external = runtime.get("external_request_schemes")
    _assert(external == {}, "browser workbench made an external network request")
    schemes = runtime.get("request_schemes")
    _assert(isinstance(schemes, dict) and schemes.get("file", 0) >= 1, "file navigation was not observed")
    _assert(set(schemes) <= {"file", "blob", "data"}, "unexpected browser request scheme observed")
    return {
        "browser_product": browser["product"],
        "protocol_version": browser.get("protocol_version"),
        "node_version": observation["node_version"],
        "unit_fieldsets": EXPECTED_UNIT_COUNT,
        "blind_images_loaded": EXPECTED_BLIND_PAGE_COUNT,
        "empty_review_errors": EXPECTED_EMPTY_ERROR_COUNT,
        "draft_progress_restored": EXPECTED_PARTIAL_PROGRESS,
        "completed_progress": EXPECTED_COMPLETE_PROGRESS,
        "label_counts": EXPECTED_LABEL_COUNTS,
        "desktop_horizontal_overflow": False,
        "mobile_horizontal_overflow": False,
        "console_errors": 0,
        "runtime_exceptions": 0,
        "external_request_schemes": {},
        "request_schemes": schemes,
        "network_observation_scope": (
            "inspected page-target resource requests; loopback DevTools controller transport excluded"
        ),
    }


def _extract_exact_archive(archive_path: Path, destination: Path) -> Path:
    if destination.exists():
        raise LabelReviewBrowserQaError(f"refusing to reuse extraction directory {destination.name}")
    destination.mkdir(parents=True)
    with zipfile.ZipFile(archive_path, "r") as archive:
        archive.extractall(destination)
    html_path = destination / ARCHIVE_ROOT / HANDOFF_HTML_NAME
    if not html_path.is_file():
        raise LabelReviewBrowserQaError("extracted workbench is missing")
    return html_path


def run_browser_qa(
    *,
    archive_path: Path,
    packet_path: Path,
    browser_executable: Path,
    node_executable: Path,
    work_directory: Path,
    run_id: str,
    git_source_commit: str,
) -> tuple[dict[str, Any], dict[str, Path]]:
    archive_path = archive_path.resolve()
    packet_path = packet_path.resolve()
    browser_executable = browser_executable.resolve()
    node_executable = node_executable.resolve()
    work_directory = work_directory.resolve()
    run_started_at_utc = _utc_now()
    if len(git_source_commit) != 40:
        raise LabelReviewBrowserQaError("git source commit must be a full 40-character SHA")
    for path, label in (
        (archive_path, "handoff archive"),
        (packet_path, "packet"),
        (browser_executable, "browser executable"),
        (node_executable, "Node executable"),
    ):
        if not path.is_file():
            raise LabelReviewBrowserQaError(f"{label} is missing")
    if work_directory.exists():
        raise LabelReviewBrowserQaError(
            f"refusing to reuse browser QA work directory {work_directory.name}"
        )
    work_directory.mkdir(parents=True)

    try:
        handoff_qa = verify_handoff(
            archive_path=archive_path,
            generated_at_utc=run_started_at_utc,
            run_id=f"{run_id}-HANDOFF-VERIFY",
            git_source_commit=git_source_commit,
        )
    except LabelReviewHandoffVerificationError as error:
        raise LabelReviewBrowserQaError(f"handoff verification failed: {error}") from error
    if handoff_qa["decision"] != "PASS_HANDOFF_INTEGRITY_READY_FOR_INDEPENDENT_REVIEW_DEFER_DATASET":
        raise LabelReviewBrowserQaError("handoff archive did not pass its independent verifier")

    html_path = _extract_exact_archive(archive_path, work_directory / "extracted")
    raw_directory = work_directory / "browser"
    controller = Path(__file__).with_name("label_review_browser_controller.mjs")
    if not controller.is_file():
        raise LabelReviewBrowserQaError("packaged browser controller is missing")
    try:
        process = subprocess.run(
            [
                str(node_executable),
                str(controller),
                "--browser",
                str(browser_executable),
                "--html",
                str(html_path),
                "--output-directory",
                str(raw_directory),
            ],
            cwd=work_directory,
            capture_output=True,
            text=True,
            timeout=180,
            check=False,
        )
    except subprocess.TimeoutExpired as error:
        raise LabelReviewBrowserQaError("browser controller exceeded 180 seconds") from error
    if process.returncode != 0:
        detail = (process.stderr or process.stdout).strip().splitlines()
        safe_detail = detail[-1] if detail else "browser controller returned no detail"
        raise LabelReviewBrowserQaError(f"browser controller failed: {safe_detail}")

    observation_path = raw_directory / "observation.json"
    draft_path = raw_directory / "downloads" / (
        f"{EXPECTED_PACKET_ID}-DRAFT-{EXPECTED_REVIEWER_ID}.json"
    )
    response_path = raw_directory / "downloads" / (
        f"{EXPECTED_PACKET_ID}-RESPONSE-{EXPECTED_REVIEWER_ID}.json"
    )
    desktop_path = raw_directory / "desktop.png"
    mobile_path = raw_directory / "mobile.png"
    observation = _load_json(observation_path)
    browser_checks = _validate_observation(
        observation,
        draft_path=draft_path,
        response_path=response_path,
        desktop_path=desktop_path,
        mobile_path=mobile_path,
    )

    packet = _load_json(packet_path)
    response = _load_json(response_path)
    response_summary = validate_completed_response(
        packet,
        response,
        response_sha256=_sha256_file(response_path),
    )
    if response_summary["reviewer_id"] != EXPECTED_REVIEWER_ID:
        raise LabelReviewBrowserQaError("browser response fixture identity differs")
    experience = response.get("reviewer", {}).get("burned_area_interpretation_experience")
    if experience != EXPECTED_EXPERIENCE:
        raise LabelReviewBrowserQaError("browser response fixture disclosure differs")
    review_completed_at = _parse_timestamp(
        response["review_completed_at_utc"],
        "browser response completion",
    )
    recorded_at_utc = _utc_now()
    recorded_at = _parse_timestamp(recorded_at_utc, "browser QA record")
    if recorded_at < review_completed_at:
        raise LabelReviewBrowserQaError(
            "browser response completion is later than the QA receipt clock"
        )

    lock_path = work_directory / "software-browser-fixture-lock.json"
    lock = build_response_lock(
        packet_path=packet_path,
        response_path=response_path,
        receipt_id="LABEL-REVIEW-BROWSER-FIXTURE-LOCK-2026-001",
        received_at_utc=recorded_at_utc,
        run_id=f"{run_id}-FIXTURE-LOCK",
        git_source_commit=git_source_commit,
        evidence_origin=SOFTWARE_BROWSER_FIXTURE,
        task_issue=TASK_ISSUE,
        report_version=LEGACY_LOCK_REPORT_VERSION,
        software_version=LEGACY_SOFTWARE_VERSION,
    )
    write_response_lock(lock, lock_path)
    if (
        lock["decision"] != "PASS_SOFTWARE_FIXTURE_CONTRACT_AND_HASH_LOCK_NO_REVEAL"
        or lock["software_browser_fixture"] is not True
        or lock["qualifying_independent_human_response"] is not False
        or not lock["reveal_release"].startswith("prohibited:")
    ):
        raise LabelReviewBrowserQaError("fixture response lock did not preserve the no-human boundary")

    report = {
        "report_id": BROWSER_QA_ID,
        "schema_version": BROWSER_QA_SCHEMA_VERSION,
        "report_version": BROWSER_QA_VERSION,
        "run_started_at_utc": run_started_at_utc,
        "generated_at_utc": recorded_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": TASK_ISSUE,
        "git_source_commit": git_source_commit,
        "software_version": SOFTWARE_VERSION,
        "application_version": WORKBENCH_VERSION,
        "browser_runtime": {
            "product": observation["browser"]["product"],
            "protocol_version": observation["browser"]["protocol_version"],
            "user_agent": observation["browser"]["user_agent"],
            "javascript_version": observation["browser"]["javascript_version"],
            "node_version": observation["node_version"],
            "browser_binary_filename": browser_executable.name,
            "browser_binary_bytes": browser_executable.stat().st_size,
            "browser_binary_sha256": _sha256_file(browser_executable),
            "controller_transport": (
                "short-lived HTTP/WebSocket DevTools control plane bound to 127.0.0.1 "
                "with an isolated browser profile"
            ),
        },
        "archive_binding": {
            "filename": archive_path.name,
            "bytes": archive_path.stat().st_size,
            "sha256": _sha256_file(archive_path),
            "handoff_decision": handoff_qa["decision"],
        },
        "packet_binding": {
            "report_id": packet["report_id"],
            "run_id": packet["run_id"],
            "git_source_commit": packet["git_source_commit"],
            "sha256": _sha256_file(packet_path),
            "label_schema_version": packet["label_schema_version"],
            "aoi_version": packet["aoi_version"],
        },
        "checks": {
            "live_browser": browser_checks,
            "draft_fixture": {
                "bytes": draft_path.stat().st_size,
                "sha256": _sha256_file(draft_path),
                "completed": False,
                "retained_as_human_evidence": False,
            },
            "response_fixture": {
                "bytes": response_path.stat().st_size,
                "sha256": _sha256_file(response_path),
                "completed_contract": True,
                "unit_count": response_summary["unit_count"],
                "label_counts": response_summary["label_counts"],
                "review_started_at_utc_client_clock": response["review_started_at_utc"],
                "review_completed_at_utc_client_clock": response["review_completed_at_utc"],
                "retained_as_human_evidence": False,
            },
            "fixture_lock": {
                "bytes": lock_path.stat().st_size,
                "sha256": _sha256_file(lock_path),
                "decision": lock["decision"],
                "evidence_origin": lock["evidence_origin"],
                "qualifying_independent_human_response": False,
                "reveal_release": lock["reveal_release"],
            },
        },
        "screenshots": {
            "desktop": {
                "path": PUBLIC_DESKTOP_NAME,
                "bytes": desktop_path.stat().st_size,
                "sha256": _sha256_file(desktop_path),
                "viewport": "1440x1000",
            },
            "mobile": {
                "path": PUBLIC_MOBILE_NAME,
                "bytes": mobile_path.stat().st_size,
                "sha256": _sha256_file(mobile_path),
                "viewport": "390x844",
            },
        },
        "software_browser_fixtures_executed": 1,
        "independent_human_responses_used_in_this_qa": 0,
        "adjudications_used_in_this_qa": 0,
        "dataset_version": None,
        "split_version": None,
        "baseline_version": None,
        "model_version": None,
        "decision": "PASS_LIVE_BROWSER_RESPONSE_ROUNDTRIP_NO_HUMAN_EVIDENCE_DEFER_DATASET",
        "decision_detail": (
            "The exact extracted offline workbench completed invalid-state, draft download/load, "
            "all-unit review, response export, responsive viewport, and fixture-only response-lock "
            "checks in the recorded current browser. The software fixture cannot count as an "
            "independent response or authorize reveal."
        ),
        "claims": {
            "proven": [
                "The exact isolated archive executes in the recorded current Chromium browser with all eight blind images and 56 response fieldsets loaded.",
                "The real browser blocks incomplete export, downloads and reloads a local draft, exports the exact completed response schema, and the inspected page target produces no external resource request, console error, runtime exception, cookie, or local-storage entry.",
                "The browser-generated response is locked only as an explicit software fixture; the receipt prohibits reveal and cannot count as human label evidence.",
            ],
            "not_proven": [
                "One recorded Chromium run is not cross-browser certification, formal accessibility conformance, reviewer identity or expertise verification, independent human review, label fitness, adjudication, field validation, or accuracy.",
                "No accepted label set, dataset, split, baseline, model, deployment, official status, endorsement, or operational readiness exists.",
            ],
        },
        "research_basis": [
            "https://developer.chrome.com/docs/chromium/headless",
            "https://chromedevtools.github.io/devtools-protocol/tot/",
            "https://nodejs.org/api/globals.html#class-websocket",
        ],
        "warning": WARNING,
    }
    return report, {
        "desktop_raw": desktop_path,
        "mobile_raw": mobile_path,
        "observation": observation_path,
        "draft": draft_path,
        "response": response_path,
        "fixture_lock": lock_path,
    }


def render_browser_qa_png(
    report: dict[str, Any],
    *,
    desktop_path: Path,
    mobile_path: Path,
    output_path: Path,
) -> None:
    if output_path.exists():
        raise LabelReviewBrowserQaError(f"refusing to overwrite existing output {output_path.name}")
    canvas = Image.new("RGB", (1800, 1540), "#f4f0e8")
    draw = ImageDraw.Draw(canvas)
    ink, muted, teal, orange = "#15211d", "#5d6b64", "#006b64", "#f05a28"
    draw.rectangle((0, 0, 1800, 190), fill="#132a26")
    draw.text((55, 28), "BURNLENS / PHASE TWO / OBJECTIVE FOUR", fill="#b9d8cf", font=_font(19))
    draw.text((55, 70), "LIVE-BROWSER REVIEWER HANDOFF QA", fill="white", font=_font(36))
    draw.text(
        (55, 125),
        "Real Chromium execution / draft roundtrip / response export / fixture-isolated lock",
        fill="#b9d8cf",
        font=_font(16),
    )
    metrics = [
        ("56/56", "browser-completed units"),
        ("8/8", "blind images loaded"),
        ("0", "external requests"),
        ("0", "human responses used in QA"),
    ]
    for index, (value, label) in enumerate(metrics):
        left = 45 + index * 430
        draw.rounded_rectangle((left, 225, left + 390, 345), radius=15, fill="#e5efeb")
        draw.text((left + 24, 246), value, fill=teal, font=_font(30))
        draw.text((left + 24, 302), label, fill=muted, font=_font(14))

    with Image.open(desktop_path) as desktop_source:
        desktop = ImageOps.fit(desktop_source.convert("RGB"), (1050, 590), method=Image.Resampling.LANCZOS)
    with Image.open(mobile_path) as mobile_source:
        mobile = ImageOps.fit(mobile_source.convert("RGB"), (305, 590), method=Image.Resampling.LANCZOS)
    draw.rounded_rectangle((45, 390, 1175, 1055), radius=16, fill="#fffdf8", outline="#d4cec1", width=2)
    draw.text((72, 414), "DESKTOP / 1440 x 1000", fill=teal, font=_font(17))
    canvas.paste(desktop, (85, 455))
    draw.rounded_rectangle((1215, 390, 1755, 1055), radius=16, fill="#fffdf8", outline="#d4cec1", width=2)
    draw.text((1242, 414), "MOBILE / 390 x 844", fill=teal, font=_font(17))
    canvas.paste(mobile, (1332, 455))

    draw.rounded_rectangle((45, 1100, 1755, 1370), radius=16, fill="#fffdf8", outline="#d4cec1", width=2)
    draw.text((72, 1125), "OBSERVED SOFTWARE ACCEPTANCE", fill=teal, font=_font(20))
    lines = [
        "Incomplete review and export were visibly blocked; the error summary received focus.",
        "A seven-unit draft downloaded, the form cleared, and native file input restored the exact progress and values.",
        "All 56 fixture units reviewed and exported; label counts were 14 each across the four response classes.",
        "The fixture receipt is explicitly non-human, prohibits reveal, and cannot support label fitness or dataset candidacy.",
    ]
    for index, line in enumerate(lines):
        draw.text((88, 1172 + index * 44), f"{index + 1}. {line}", fill=ink, font=_font(13))
    draw.text((72, 1332), report["decision"], fill=orange, font=_font(15))
    trace = (
        f"run {report['run_id']} / source {report['git_source_commit'][:12]} / "
        f"software {report['software_version']} / app {report['application_version']} / "
        f"browser {report['browser_runtime']['product']}"
    )
    draw.text((45, 1420), trace, fill=muted, font=_font(11))
    draw.text((45, 1460), report["warning"], fill="#33443e", font=_font(9))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path, format="PNG", optimize=False)


def render_browser_qa_html(report: dict[str, Any], *, output_path: Path) -> None:
    document = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>BurnLens live-browser reviewer-handoff QA</title>
<style>
body{{margin:0;background:#f4f0e8;color:#15211d;font:16px/1.55 system-ui,sans-serif}}header{{background:#132a26;color:white;padding:3rem max(5vw,2rem)}}header p{{color:#b9d8cf}}main{{max-width:1300px;margin:auto;padding:2.5rem 1.5rem 5rem}}.warning{{background:#fff1ca;border-left:6px solid #d87618;padding:1rem;font-weight:650}}.card{{background:#fffdf8;border:1px solid #d9d1c4;border-radius:12px;padding:1.2rem;margin:1.2rem 0}}.decision{{border:2px solid #f05a28}}.shots{{display:grid;grid-template-columns:minmax(0,3fr) minmax(240px,1fr);gap:1rem}}.shots img{{width:100%;height:auto;border:1px solid #c8c0b2}}code{{overflow-wrap:anywhere}}@media(max-width:760px){{.shots{{grid-template-columns:1fr}}}}
</style></head>
<body><header><p>BurnLens / Phase Two / Objective Four</p><h1>Live-browser reviewer-handoff QA</h1><p>Recorded software acceptance of the exact isolated offline workbench. Not human label evidence.</p></header>
<main><p class="warning">{escape(report['warning'])}</p>
<section class="card decision"><h2>Decision</h2><p><strong>{escape(report['decision'])}</strong></p><p>{escape(report['decision_detail'])}</p></section>
<section class="card"><h2>Actual browser evidence</h2><div class="shots"><figure><img src="{escape(report['screenshots']['desktop']['path'])}" alt="Desktop browser view of the completed BurnLens offline workbench"><figcaption>Desktop viewport {escape(report['screenshots']['desktop']['viewport'])}; no horizontal overflow.</figcaption></figure><figure><img src="{escape(report['screenshots']['mobile']['path'])}" alt="Mobile browser view of the BurnLens offline workbench"><figcaption>Mobile viewport {escape(report['screenshots']['mobile']['viewport'])}; no horizontal overflow.</figcaption></figure></div></section>
<section class="card"><h2>Observed roundtrip</h2><ul>
<li>Loaded 8 of 8 proposal-blinded images and all 56 labelled unit forms in <code>{escape(report['browser_runtime']['product'])}</code>.</li>
<li>Incomplete review reported 61 issues, highlighted all units, focused the error surface, and produced no response download.</li>
<li>A seven-unit draft downloaded, the form cleared, and the native file input restored the exact reviewer fields, first label, and 7-of-56 progress.</li>
<li>All 56 software-fixture entries reviewed and exported; exact label counts were 14 burned, 14 background, 14 uncertain, and 14 unusable.</li>
<li>Console errors: 0; runtime exceptions: 0; inspected-page external request schemes: 0; cookies and local-storage entries: 0. The QA controller itself uses a short-lived loopback DevTools connection outside the page-network observation boundary.</li>
<li>The response lock decision is <code>{escape(report['checks']['fixture_lock']['decision'])}</code>; the software fixture cannot authorize reveal.</li>
</ul></section>
<section class="card"><h2>Traceability and boundary</h2><p><strong>Run:</strong> <code>{escape(report['run_id'])}</code><br><strong>Git source:</strong> <code>{escape(report['git_source_commit'])}</code><br><strong>Archive SHA-256:</strong> <code>{escape(report['archive_binding']['sha256'])}</code><br><strong>Browser binary SHA-256:</strong> <code>{escape(report['browser_runtime']['browser_binary_sha256'])}</code><br><strong>Application:</strong> <code>{escape(report['application_version'])}</code><br><strong>Dataset / split / baseline / model:</strong> none / none / none / none<br><strong>Independent human responses / adjudications used in this QA:</strong> 0 / 0. This run does not establish the project-wide response count.</p><ul>{''.join(f'<li><strong>Not proven:</strong> {escape(item)}</li>' for item in report['claims']['not_proven'])}</ul></section>
</main></body></html>"""
    _write_utf8_lf(output_path, document)


def write_browser_qa_outputs(
    report: dict[str, Any],
    raw_paths: dict[str, Path],
    *,
    json_path: Path,
    html_path: Path,
    png_path: Path,
    desktop_path: Path,
    mobile_path: Path,
) -> None:
    _copy_new(raw_paths["desktop_raw"], desktop_path)
    _copy_new(raw_paths["mobile_raw"], mobile_path)
    if (
        report["screenshots"]["desktop"]["sha256"] != _sha256_file(desktop_path)
        or report["screenshots"]["mobile"]["sha256"] != _sha256_file(mobile_path)
    ):
        raise LabelReviewBrowserQaError("public screenshot copy differs from browser evidence")
    _write_utf8_lf(json_path, json.dumps(report, indent=2, ensure_ascii=True) + "\n")
    render_browser_qa_png(
        report,
        desktop_path=desktop_path,
        mobile_path=mobile_path,
        output_path=png_path,
    )
    render_browser_qa_html(report, output_path=html_path)
