"""Independently verify an isolated BurnLens offline reviewer handoff.

This verifier does not import the handoff builder.  It checks archive safety,
the exact allowlist and byte bindings, response-contract compatibility, the
offline workbench structure, and absence of proposal reveal material.  It
cannot turn a software fixture into independent human evidence.
"""

from __future__ import annotations

from hashlib import sha256
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path, PurePosixPath
import stat
from typing import Any
import zipfile

from PIL import Image, ImageDraw

from .optical_pair_evidence import WARNING, _font


SOFTWARE_VERSION = "0.14.0"
EXPECTED_HANDOFF_ID = "LABEL-REVIEW-HANDOFF-2026-001"
EXPECTED_HANDOFF_SCHEMA = "0.1.0"
EXPECTED_HANDOFF_VERSION = "proposal-safe-offline-label-review-handoff-v0.1.0"
EXPECTED_WORKBENCH_VERSION = "label-review-handoff-workbench-v0.1.0"
EXPECTED_PACKET_ID = "LABEL-REVIEW-PACKET-2026-001"
EXPECTED_PACKET_RUN_ID = "BL-2026-07-16-label-review-packet-r001"
EXPECTED_PACKET_SHA256 = "77067063a769645af13886b6c87cc236a10e06199d091743908d63556e07637c"
EXPECTED_RESPONSE_SCHEMA = "burnlens-label-review-response-v0.1.0"
EXPECTED_UNIT_IDS = tuple(f"LRU-{index:03d}" for index in range(1, 57))
EXPECTED_BLIND_NAMES = tuple(
    f"{EXPECTED_PACKET_ID}-BLIND-{index:02d}.png" for index in range(1, 9)
)
EXPECTED_HTML_NAME = f"{EXPECTED_HANDOFF_ID}.html"
EXPECTED_JSON_NAME = f"{EXPECTED_HANDOFF_ID}.json"
EXPECTED_README_NAME = f"{EXPECTED_HANDOFF_ID}-README.txt"
EXPECTED_RESPONSE_TEMPLATE_NAME = f"{EXPECTED_PACKET_ID}-RESPONSE-TEMPLATE.json"
EXPECTED_ARCHIVE_ROOT = "BurnLens-Label-Review-Handoff-2026-001"
EXPECTED_MEMBER_ORDER = (
    EXPECTED_JSON_NAME,
    EXPECTED_HTML_NAME,
    EXPECTED_README_NAME,
    EXPECTED_RESPONSE_TEMPLATE_NAME,
    *EXPECTED_BLIND_NAMES,
)
EXPECTED_MEMBER_NAMES = tuple(
    str(PurePosixPath(EXPECTED_ARCHIVE_ROOT) / name) for name in EXPECTED_MEMBER_ORDER
)

EXPECTED_FIRST_PASS_LABELS = {"burned", "background", "uncertain", "unusable"}
EXPECTED_EVIDENCE_SUFFICIENCY = {"sufficient", "limited", "insufficient"}
EXPECTED_CONFIDENCE = {"low", "medium", "high"}
EXPECTED_REASONS = {
    "pre-post-change",
    "persistent-darkening",
    "vegetation-loss",
    "source-context-support",
    "source-context-conflict",
    "cloud-smoke-shadow",
    "registration-concern",
    "boundary-ambiguity",
    "low-severity-ambiguity",
    "non-fire-change-possible",
    "other",
}
FORBIDDEN_TEXT_TOKENS = (
    f"{EXPECTED_PACKET_ID}-REVEAL.html",
    f"{EXPECTED_PACKET_ID}.json",
    f"{EXPECTED_PACKET_ID}-ADJUDICATION-TEMPLATE.json",
    "LABEL-REVIEW-PACKET-QA-2026-001",
    '"proposal_state"',
    '"proposal_state_code"',
    '"proposal_target_value"',
    '"dnbr_center"',
    "fetch(",
    "XMLHttpRequest",
    "WebSocket",
    "EventSource",
    "sendBeacon",
    "http://",
    "https://",
)

QA_REPORT_ID = "LABEL-REVIEW-HANDOFF-QA-2026-001"
QA_SCHEMA_VERSION = "0.1.0"
QA_REPORT_VERSION = "label-review-handoff-integrity-qa-v0.1.0"
TASK_ISSUE = 379


class LabelReviewHandoffVerificationError(RuntimeError):
    """A deterministic handoff-verification failure."""


def _write_utf8_lf(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    path.write_bytes(normalized.encode("utf-8"))


def _sha256_bytes(payload: bytes) -> str:
    return sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _load_json_bytes(payload: bytes, *, label: str) -> dict[str, Any]:
    try:
        value = json.loads(payload.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise LabelReviewHandoffVerificationError(f"{label} is invalid UTF-8 JSON") from error
    if not isinstance(value, dict):
        raise LabelReviewHandoffVerificationError(f"{label} is not a JSON object")
    return value


def _walk_keys(value: Any) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            keys.add(str(key))
            keys.update(_walk_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.update(_walk_keys(child))
    return keys


def _basename(member_name: str) -> str:
    path = PurePosixPath(member_name)
    if len(path.parts) != 2 or path.parts[0] != EXPECTED_ARCHIVE_ROOT:
        raise LabelReviewHandoffVerificationError("archive member is outside the one-root contract")
    return path.name


class _WorkbenchParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.label_fors: set[str] = set()
        self.sample_ids: list[str] = []
        self.images: list[str] = []
        self.script_sources: list[str] = []
        self.links: list[str] = []
        self.form_count = 0
        self.button_ids: set[str] = set()
        self.meta_csp: list[str] = []
        self._template_depth = 0
        self.template_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value for key, value in attrs}
        element_id = values.get("id")
        if element_id:
            if element_id in self.ids:
                raise LabelReviewHandoffVerificationError(
                    f"workbench contains duplicate element ID {element_id}"
                )
            self.ids.add(element_id)
        if tag == "label" and values.get("for"):
            self.label_fors.add(str(values["for"]))
        if tag == "fieldset" and values.get("data-sample-id"):
            self.sample_ids.append(str(values["data-sample-id"]))
        if tag == "img" and values.get("src"):
            self.images.append(str(values["src"]))
        if tag == "script":
            if values.get("src"):
                self.script_sources.append(str(values["src"]))
            if element_id == "response-template":
                self._template_depth += 1
        if tag == "a" and values.get("href"):
            self.links.append(str(values["href"]))
        if tag == "form":
            self.form_count += 1
        if tag == "button" and element_id:
            self.button_ids.add(element_id)
        if (
            tag == "meta"
            and str(values.get("http-equiv", "")).lower() == "content-security-policy"
            and values.get("content")
        ):
            self.meta_csp.append(str(values["content"]))

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._template_depth:
            self._template_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._template_depth:
            self.template_text.append(data)


def _verify_response_template(template: dict[str, Any]) -> dict[str, Any]:
    if template.get("response_schema_version") != EXPECTED_RESPONSE_SCHEMA:
        raise LabelReviewHandoffVerificationError("response template schema is invalid")
    if template.get("packet_id") != EXPECTED_PACKET_ID:
        raise LabelReviewHandoffVerificationError("response template packet ID is invalid")
    if template.get("packet_run_id") != EXPECTED_PACKET_RUN_ID:
        raise LabelReviewHandoffVerificationError("response template packet run is invalid")
    if template.get("completed") is not False:
        raise LabelReviewHandoffVerificationError("response template is marked complete")
    reviewer = template.get("reviewer")
    if not isinstance(reviewer, dict) or any(value is not None for value in reviewer.values()):
        raise LabelReviewHandoffVerificationError("response template contains reviewer evidence")
    responses = template.get("responses")
    if not isinstance(responses, list):
        raise LabelReviewHandoffVerificationError("response template responses are invalid")
    if tuple(item.get("sample_id") for item in responses) != EXPECTED_UNIT_IDS:
        raise LabelReviewHandoffVerificationError("response template sample bindings are invalid")
    forbidden = {"proposal_state", "proposal_state_code", "proposal_target_value", "dnbr_center"}
    if forbidden.intersection(_walk_keys(template)):
        raise LabelReviewHandoffVerificationError("response template contains proposal values")
    for item in responses:
        if item.get("first_pass_label") is not None:
            raise LabelReviewHandoffVerificationError("response template contains a label")
        if item.get("evidence_sufficiency") is not None or item.get("confidence") is not None:
            raise LabelReviewHandoffVerificationError("response template contains a judgment")
        if item.get("reason_codes") != [] or item.get("notes") is not None:
            raise LabelReviewHandoffVerificationError("response template contains review content")
    instructions = template.get("instructions", {})
    if set(instructions.get("allowed_first_pass_labels", [])) != EXPECTED_FIRST_PASS_LABELS:
        raise LabelReviewHandoffVerificationError("response label domain is invalid")
    if (
        set(instructions.get("allowed_evidence_sufficiency", []))
        != EXPECTED_EVIDENCE_SUFFICIENCY
    ):
        raise LabelReviewHandoffVerificationError("response sufficiency domain is invalid")
    if set(instructions.get("allowed_confidence", [])) != EXPECTED_CONFIDENCE:
        raise LabelReviewHandoffVerificationError("response confidence domain is invalid")
    if set(instructions.get("allowed_reason_codes", [])) != EXPECTED_REASONS:
        raise LabelReviewHandoffVerificationError("response reason-code domain is invalid")
    return {
        "schema_version": template["response_schema_version"],
        "unit_count": len(responses),
        "completed": False,
        "proposal_value_fields": [],
    }


def _verify_workbench(html_payload: bytes, response_template: dict[str, Any]) -> dict[str, Any]:
    try:
        text = html_payload.decode("utf-8")
    except UnicodeError as error:
        raise LabelReviewHandoffVerificationError("workbench is not UTF-8") from error
    lowered = text.lower()
    found = [token for token in FORBIDDEN_TEXT_TOKENS if token.lower() in lowered]
    if found:
        raise LabelReviewHandoffVerificationError(
            f"workbench contains forbidden reveal, proposal, or network tokens: {', '.join(found)}"
        )
    parser = _WorkbenchParser()
    parser.feed(text)
    if parser.form_count != 1:
        raise LabelReviewHandoffVerificationError("workbench must contain exactly one form")
    if tuple(parser.sample_ids) != EXPECTED_UNIT_IDS:
        raise LabelReviewHandoffVerificationError("workbench sample fieldsets are invalid")
    if tuple(parser.images) != EXPECTED_BLIND_NAMES:
        raise LabelReviewHandoffVerificationError("workbench blind-page image bindings are invalid")
    if parser.script_sources or parser.links:
        raise LabelReviewHandoffVerificationError("workbench contains external script or link navigation")
    required_buttons = {
        "review-button",
        "save-draft-button",
        "export-button",
    }
    if not required_buttons.issubset(parser.button_ids):
        raise LabelReviewHandoffVerificationError("workbench response controls are incomplete")
    if len(parser.meta_csp) != 1 or "connect-src 'none'" not in parser.meta_csp[0]:
        raise LabelReviewHandoffVerificationError("workbench no-network policy is missing")
    required_reviewer_controls = {
        "reviewer-id",
        "reviewer-experience",
        "independent",
        "not-seen",
        "attestation",
        "load-draft",
    }
    if not required_reviewer_controls.issubset(parser.ids):
        raise LabelReviewHandoffVerificationError("workbench reviewer controls are incomplete")
    for sample_id in EXPECTED_UNIT_IDS:
        required_ids = {
            f"{sample_id}-label",
            f"{sample_id}-sufficiency",
            f"{sample_id}-confidence",
            f"{sample_id}-notes",
        }
        if not required_ids.issubset(parser.ids):
            raise LabelReviewHandoffVerificationError(
                f"workbench controls are incomplete for {sample_id}"
            )
        if not required_ids.issubset(parser.label_fors):
            raise LabelReviewHandoffVerificationError(
                f"workbench labels are incomplete for {sample_id}"
            )
    embedded_text = "".join(parser.template_text).strip()
    embedded = _load_json_bytes(embedded_text.encode("utf-8"), label="embedded response template")
    if embedded != response_template:
        raise LabelReviewHandoffVerificationError(
            "embedded workbench response template differs from the archive template"
        )
    return {
        "form_count": parser.form_count,
        "unit_fieldsets": len(parser.sample_ids),
        "blind_page_images": len(parser.images),
        "labelled_required_controls": True,
        "draft_save_load_controls": True,
        "review_and_export_controls": True,
        "network_navigation_or_script_dependencies": 0,
        "connect_src_none": True,
        "embedded_response_template_exact": True,
    }


def _verify_readme(payload: bytes) -> dict[str, Any]:
    try:
        text = payload.decode("utf-8")
    except UnicodeError as error:
        raise LabelReviewHandoffVerificationError("handoff README is not UTF-8") from error
    lowered = text.lower()
    found = [token for token in FORBIDDEN_TEXT_TOKENS if token.lower() in lowered]
    if found:
        raise LabelReviewHandoffVerificationError(
            f"handoff README contains forbidden material: {', '.join(found)}"
        )
    required = (
        EXPECTED_PACKET_ID,
        EXPECTED_PACKET_RUN_ID,
        EXPECTED_WORKBENCH_VERSION,
        "SHA-256",
        WARNING,
    )
    missing = [item for item in required if item not in text]
    if "no proposal-bearing packet json" not in lowered:
        missing.append("no proposal-bearing packet JSON")
    if missing:
        raise LabelReviewHandoffVerificationError(
            f"handoff README is missing required content: {', '.join(missing)}"
        )
    return {
        "utf8_lf": b"\r" not in payload,
        "warning_present": True,
        "hash_lock_instruction_present": True,
        "proposal_reveal_file_present": False,
    }


def _verify_manifest(
    manifest: dict[str, Any],
    payloads: dict[str, bytes],
) -> dict[str, Any]:
    if manifest.get("report_id") != EXPECTED_HANDOFF_ID:
        raise LabelReviewHandoffVerificationError("handoff manifest identity is invalid")
    if manifest.get("schema_version") != EXPECTED_HANDOFF_SCHEMA:
        raise LabelReviewHandoffVerificationError("handoff manifest schema is invalid")
    if manifest.get("report_version") != EXPECTED_HANDOFF_VERSION:
        raise LabelReviewHandoffVerificationError("handoff manifest version is invalid")
    if manifest.get("software_version") != SOFTWARE_VERSION:
        raise LabelReviewHandoffVerificationError("handoff software version is invalid")
    if manifest.get("application_version") != EXPECTED_WORKBENCH_VERSION:
        raise LabelReviewHandoffVerificationError("handoff workbench version is invalid")
    binding = manifest.get("packet_binding", {})
    if (
        binding.get("report_id") != EXPECTED_PACKET_ID
        or binding.get("run_id") != EXPECTED_PACKET_RUN_ID
        or binding.get("sha256") != EXPECTED_PACKET_SHA256
        or binding.get("response_schema_version") != EXPECTED_RESPONSE_SCHEMA
    ):
        raise LabelReviewHandoffVerificationError("handoff packet binding is invalid")
    archive = manifest.get("archive_contract", {})
    if archive.get("root_directory") != EXPECTED_ARCHIVE_ROOT:
        raise LabelReviewHandoffVerificationError("handoff archive root is invalid")
    if archive.get("compression") != "stored":
        raise LabelReviewHandoffVerificationError("handoff archive compression is invalid")
    if tuple(archive.get("member_order", [])) != EXPECTED_MEMBER_ORDER:
        raise LabelReviewHandoffVerificationError("handoff archive order is invalid")
    if archive.get("member_count") != len(EXPECTED_MEMBER_ORDER):
        raise LabelReviewHandoffVerificationError("handoff member count is invalid")
    if archive.get("network_dependencies") != 0:
        raise LabelReviewHandoffVerificationError("handoff declares a network dependency")
    members = manifest.get("members")
    if not isinstance(members, list):
        raise LabelReviewHandoffVerificationError("handoff member bindings are missing")
    expected_payload_names = set(EXPECTED_MEMBER_ORDER) - {EXPECTED_JSON_NAME}
    if {item.get("path") for item in members} != expected_payload_names:
        raise LabelReviewHandoffVerificationError("handoff member inventory is invalid")
    for item in members:
        name = item["path"]
        payload = payloads[name]
        if item.get("bytes") != len(payload) or item.get("sha256") != _sha256_bytes(payload):
            raise LabelReviewHandoffVerificationError(
                f"handoff member binding differs for {name}"
            )
    contract = manifest.get("review_contract", {})
    if contract.get("unit_count") != 56 or contract.get("blind_page_count") != 8:
        raise LabelReviewHandoffVerificationError("handoff review coverage is invalid")
    if set(contract.get("first_pass_labels", [])) != EXPECTED_FIRST_PASS_LABELS:
        raise LabelReviewHandoffVerificationError("handoff response label domain is invalid")
    if set(contract.get("evidence_sufficiency", [])) != EXPECTED_EVIDENCE_SUFFICIENCY:
        raise LabelReviewHandoffVerificationError("handoff sufficiency domain is invalid")
    if set(contract.get("confidence_levels", [])) != EXPECTED_CONFIDENCE:
        raise LabelReviewHandoffVerificationError("handoff confidence domain is invalid")
    if set(contract.get("reason_codes", [])) != EXPECTED_REASONS:
        raise LabelReviewHandoffVerificationError("handoff reason domain is invalid")
    if manifest.get("completed_independent_responses") != 0:
        raise LabelReviewHandoffVerificationError("handoff invents an independent response")
    if manifest.get("completed_adjudications") != 0:
        raise LabelReviewHandoffVerificationError("handoff invents an adjudication")
    if any(manifest.get(key) is not None for key in ("dataset_version", "split_version", "baseline_version", "model_version")):
        raise LabelReviewHandoffVerificationError("handoff invents a downstream version")
    return {
        "packet_sha256": binding["sha256"],
        "payload_member_count": len(members),
        "completed_independent_responses": 0,
        "completed_adjudications": 0,
        "downstream_versions": None,
    }


def build_qa_report(
    *,
    archive_path: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, Any]:
    if len(git_source_commit) != 40:
        raise LabelReviewHandoffVerificationError(
            "git source commit must be a full 40-character SHA"
        )
    try:
        archive = zipfile.ZipFile(archive_path, mode="r")
    except (OSError, zipfile.BadZipFile) as error:
        raise LabelReviewHandoffVerificationError("handoff archive is invalid") from error
    with archive:
        infos = archive.infolist()
        names = [info.filename for info in infos]
        if len(names) != len(set(names)):
            raise LabelReviewHandoffVerificationError("handoff archive contains duplicate members")
        if tuple(names) != EXPECTED_MEMBER_NAMES:
            raise LabelReviewHandoffVerificationError("handoff archive allowlist or order is invalid")
        total_bytes = 0
        member_checks = []
        payloads: dict[str, bytes] = {}
        timestamp = None
        for info in infos:
            if "\\" in info.filename:
                raise LabelReviewHandoffVerificationError("handoff member uses a backslash path")
            path = PurePosixPath(info.filename)
            if path.is_absolute() or ".." in path.parts:
                raise LabelReviewHandoffVerificationError("handoff member path is unsafe")
            if info.is_dir():
                raise LabelReviewHandoffVerificationError("handoff contains an unexpected directory entry")
            mode = info.external_attr >> 16
            if stat.S_ISLNK(mode):
                raise LabelReviewHandoffVerificationError("handoff contains a symbolic link")
            if mode != 0o100644:
                raise LabelReviewHandoffVerificationError("handoff member mode differs")
            if info.compress_type != zipfile.ZIP_STORED or info.compress_size != info.file_size:
                raise LabelReviewHandoffVerificationError("handoff member is not stored exactly")
            if info.flag_bits & 1:
                raise LabelReviewHandoffVerificationError("handoff member is encrypted")
            timestamp = timestamp or info.date_time
            if info.date_time != timestamp:
                raise LabelReviewHandoffVerificationError("handoff member timestamps differ")
            total_bytes += info.file_size
            if total_bytes > 25_000_000:
                raise LabelReviewHandoffVerificationError("handoff exceeds the bounded byte contract")
            payload = archive.read(info)
            name = _basename(info.filename)
            payloads[name] = payload
            member_checks.append(
                {
                    "path": name,
                    "bytes": len(payload),
                    "sha256": _sha256_bytes(payload),
                    "stored": True,
                    "mode": "100644",
                }
            )

    manifest = _load_json_bytes(payloads[EXPECTED_JSON_NAME], label="handoff manifest")
    response_template = _load_json_bytes(
        payloads[EXPECTED_RESPONSE_TEMPLATE_NAME],
        label="response template",
    )
    manifest_checks = _verify_manifest(manifest, payloads)
    response_checks = _verify_response_template(response_template)
    workbench_checks = _verify_workbench(payloads[EXPECTED_HTML_NAME], response_template)
    readme_checks = _verify_readme(payloads[EXPECTED_README_NAME])
    for name in EXPECTED_BLIND_NAMES:
        try:
            from io import BytesIO

            with Image.open(BytesIO(payloads[name])) as image:
                if image.format != "PNG" or image.width != 1800 or image.height < 2500:
                    raise LabelReviewHandoffVerificationError(
                        f"blind page image dimensions are invalid: {name}"
                    )
                image.verify()
        except (OSError, ValueError) as error:
            raise LabelReviewHandoffVerificationError(
                f"blind page image is invalid: {name}"
            ) from error

    return {
        "report_id": QA_REPORT_ID,
        "schema_version": QA_SCHEMA_VERSION,
        "report_version": QA_REPORT_VERSION,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": TASK_ISSUE,
        "git_source_commit": git_source_commit,
        "software_version": SOFTWARE_VERSION,
        "application_version": EXPECTED_WORKBENCH_VERSION,
        "archive_binding": {
            "filename": archive_path.name,
            "bytes": archive_path.stat().st_size,
            "sha256": _sha256_file(archive_path),
            "member_count": len(member_checks),
            "payload_bytes": total_bytes,
        },
        "packet_binding": manifest["packet_binding"],
        "checks": {
            "archive_members": member_checks,
            "manifest": manifest_checks,
            "response_template": response_checks,
            "workbench": workbench_checks,
            "readme": readme_checks,
            "blind_pages": {
                "count": len(EXPECTED_BLIND_NAMES),
                "png_decode": "pass",
                "minimum_height": 2500,
                "width": 1800,
            },
        },
        "synthetic_response_fixture_used": False,
        "completed_independent_responses": 0,
        "completed_adjudications": 0,
        "dataset_version": None,
        "split_version": None,
        "baseline_version": None,
        "model_version": None,
        "decision": "PASS_HANDOFF_INTEGRITY_READY_FOR_INDEPENDENT_REVIEW_DEFER_DATASET",
        "decision_detail": (
            "The deterministic archive contains only the allowlisted proposal-blinded handoff, "
            "the offline workbench is bound to the exact blank response schema, and no actual "
            "independent response or adjudication is present."
        ),
        "claims": {
            "proven": [
                "The ZIP member paths, order, modes, timestamps, storage method, byte lengths, and SHA-256 bindings pass.",
                "The offline workbench has labelled native controls for all 56 units, no network dependency, and an exact embedded blank response contract.",
                "The handoff contains no reveal file, proposal-bearing packet JSON, adjudication material, QA output, provider byte, or completed response.",
            ],
            "not_proven": [
                "Archive and interface integrity are not independent human review, reviewer identity verification, label fitness, adjudication, field validation, or accuracy.",
                "No accepted label set, dataset, split, baseline, model, deployment, official status, or endorsement exists.",
            ],
        },
        "warning": WARNING,
    }


def render_qa_png(report: dict[str, Any], path: Path) -> None:
    canvas = Image.new("RGB", (1800, 1320), "#f4f0e8")
    draw = ImageDraw.Draw(canvas)
    ink, muted, teal, orange = "#15211d", "#5d6b64", "#006b64", "#f05a28"
    draw.rectangle((0, 0, 1800, 185), fill="#132a26")
    draw.text((55, 30), "BURNLENS / REVIEWER HANDOFF", fill="#b9d8cf", font=_font(19))
    draw.text((55, 72), "ISOLATED HANDOFF INTEGRITY QA", fill="white", font=_font(37))
    draw.text(
        (55, 127),
        "Archive safety + exact bindings + offline workbench + zero-response boundary",
        fill="#b9d8cf",
        font=_font(16),
    )
    metrics = [
        (str(report["archive_binding"]["member_count"]), "archive members"),
        (str(report["checks"]["workbench"]["unit_fieldsets"]), "labelled unit forms"),
        ("0", "network dependencies"),
        ("0", "human responses"),
    ]
    for index, (value, label) in enumerate(metrics):
        left = 45 + index * 430
        draw.rounded_rectangle((left, 230, left + 390, 350), radius=15, fill="#e5efeb")
        draw.text((left + 24, 250), value, fill=teal, font=_font(31))
        draw.text((left + 24, 307), label, fill=muted, font=_font(14))
    draw.rounded_rectangle((45, 400, 1755, 955), radius=18, fill="#fffdf8", outline="#d4cec1", width=2)
    draw.text((72, 430), "VERIFIED HANDOFF CONTRACT", fill=teal, font=_font(21))
    lines = [
        "One fixed archive root; exact allowlist and order; no traversal, links, encryption, or duplicate names.",
        "Every stored member matches its declared byte length and SHA-256 binding.",
        "Eight 1800-pixel-wide blind pages decode and remain the only source imagery in the bundle.",
        "The offline workbench has one labelled form, 56 unit fieldsets, draft roundtrip, review, and export controls.",
        "No external script, link navigation, network request API, reveal file, or proposal-bearing JSON is present.",
        "No synthetic or actual response is included; dataset candidacy remains deferred.",
    ]
    for index, line in enumerate(lines):
        draw.text((88, 485 + index * 61), f"{index + 1}. {line}", fill=ink, font=_font(15))
    draw.text((72, 870), report["decision"], fill=orange, font=_font(18))
    draw.text((45, 1010), report["decision_detail"], fill=ink, font=_font(15))
    trace = (
        f"run {report['run_id']} / source {report['git_source_commit'][:12]} / "
        f"software {report['software_version']} / app {report['application_version']}"
    )
    draw.text((45, 1115), trace, fill=muted, font=_font(12))
    draw.text(
        (45, 1155),
        f"archive sha256 {report['archive_binding']['sha256']} / dataset none / split none / baseline none / model none",
        fill=orange,
        font=_font(12),
    )
    draw.text((45, 1200), report["warning"], fill="#33443e", font=_font(10))
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path, format="PNG", optimize=False)


def render_qa_html(report: dict[str, Any], png_name: str, path: Path) -> None:
    document = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>BurnLens reviewer-handoff integrity QA</title><style>
body{{margin:0;background:#f4f0e8;color:#15211d;font:16px/1.55 system-ui,sans-serif}}header{{background:#132a26;color:white;padding:3rem max(5vw,2rem)}}header p{{color:#b9d8cf}}main{{max-width:1300px;margin:auto;padding:2.5rem 1.5rem 5rem}}.hero{{width:100%;height:auto;border:1px solid #c8c0b2}}.warning{{background:#fff1ca;border-left:6px solid #d87618;padding:1rem;font-weight:650}}.card{{background:#fffdf8;border:1px solid #d9d1c4;border-radius:12px;padding:1.2rem;margin:1.2rem 0}}.decision{{border:2px solid #f05a28}}code{{overflow-wrap:anywhere}}
</style></head><body><header><p>BurnLens / Phase Two / Objective Four</p><h1>Reviewer-handoff integrity QA</h1><p>Independent archive and interface verification. Not human label evidence.</p></header><main>
<p class="warning">{escape(report['warning'])}</p><img class="hero" src="{escape(png_name)}" alt="BurnLens reviewer-handoff integrity QA">
<section class="card decision"><h2>Decision</h2><p><strong>{escape(report['decision'])}</strong></p><p>{escape(report['decision_detail'])}</p></section>
<section class="card"><h2>Verified bundle</h2><ul>
<li>{report['archive_binding']['member_count']} stored allowlisted members; SHA-256 <code>{escape(report['archive_binding']['sha256'])}</code>.</li>
<li>{report['checks']['blind_pages']['count']} proposal-blinded PNG pages and {report['checks']['workbench']['unit_fieldsets']} labelled unit fieldsets.</li>
<li>No reveal, proposal-bearing packet JSON, adjudication material, provider byte, external script, link navigation, or network dependency.</li>
<li>Completed independent responses: 0. Completed adjudications: 0.</li></ul></section>
<section class="card"><h2>Traceability and limits</h2><p><strong>Run:</strong> <code>{escape(report['run_id'])}</code><br><strong>Git source:</strong> <code>{escape(report['git_source_commit'])}</code><br><strong>Packet SHA-256:</strong> <code>{escape(report['packet_binding']['sha256'])}</code><br><strong>Software / interface:</strong> <code>{escape(report['software_version'])}</code> / <code>{escape(report['application_version'])}</code><br><strong>Dataset / split / baseline / model:</strong> none / none / none / none</p><ul>{''.join(f'<li><strong>Not proven:</strong> {escape(item)}</li>' for item in report['claims']['not_proven'])}</ul></section>
</main></body></html>"""
    _write_utf8_lf(path, document)


def write_qa_report(
    report: dict[str, Any],
    *,
    json_path: Path,
    html_path: Path,
    png_path: Path,
) -> None:
    _write_utf8_lf(json_path, json.dumps(report, indent=2, ensure_ascii=True) + "\n")
    render_qa_png(report, png_path)
    render_qa_html(report, png_path.name, html_path)


def parse_args() -> Any:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-html", type=Path, required=True)
    parser.add_argument("--output-png", type=Path, required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    return parser.parse_args()


def main() -> int:
    import sys

    args = parse_args()
    try:
        report = build_qa_report(
            archive_path=args.archive,
            generated_at_utc=args.generated_at_utc,
            run_id=args.run_id,
            git_source_commit=args.git_source_commit,
        )
        write_qa_report(
            report,
            json_path=args.output_json,
            html_path=args.output_html,
            png_path=args.output_png,
        )
        print(report["decision"])
        return 0
    except (
        LabelReviewHandoffVerificationError,
        OSError,
        ValueError,
        KeyError,
        zipfile.BadZipFile,
    ) as error:
        print(f"LABEL_REVIEW_HANDOFF_QA_FAILED: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
