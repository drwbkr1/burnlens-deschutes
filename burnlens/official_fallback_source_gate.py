"""Build the offline P2O4-T34 official-fallback comparison evidence."""

from __future__ import annotations

from collections import Counter
from datetime import datetime
from hashlib import sha256
from html import escape
import json
from pathlib import Path
import re
import subprocess
import textwrap
from typing import Any

from PIL import Image, ImageDraw, ImageFont


SOURCE_ID = "OFFICIAL-FALLBACK-SOURCE-GATE-SOURCE-2026-001"
REPORT_ID = "OFFICIAL-FALLBACK-SOURCE-GATE-2026-001"
SOURCE_SCHEMA_VERSION = "0.1.0"
REPORT_SCHEMA_VERSION = "0.1.0"
REPORT_VERSION = "official-fallback-source-gate-v0.1.0"
SOFTWARE_VERSION = "0.46.0"
TASK_ISSUE = 532
DECISION = "DEFER_BOTH_OFFICIAL_FALLBACK_CANDIDATES_SELECT_NEITHER_NO_PROVIDER_BYTES_AUTHORIZED"
WARNING = (
    "Experimental BurnLens portfolio evidence. Not official wildfire information. Not emergency "
    "guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern."
)

FROZEN_INPUTS = {
    "entry_precheck": {
        "path": "records/phase-two/prechecks/PRECHECK-2026-057.md",
        "bytes": 9419,
        "sha256": "f2faf834f6851fbeb942f1c5e142dd9d99129e11f9949926175c1ba678bf4e56",
    },
    "mckenzie_source": {
        "path": "records/phase-two/sources/SOURCE-2026-034.md",
        "bytes": 10519,
        "sha256": "3a69b160627c20e851bd3d2137389528d341fb8839e9782e6423c48c71f9e868",
    },
    "mckenzie_terms": {
        "path": "records/phase-two/terms/TERMS-2026-029.md",
        "bytes": 3899,
        "sha256": "e59478ccd0769dcd71d57f09c1456eedde9ac8e25794776a6a7239a277d87048",
    },
    "mckenzie_gate": {
        "path": "samples/reference/phase-two/OFFICIAL-FALLBACK-SOURCE-GATE-MCKENZIE-2026-001.json",
        "bytes": 10533,
        "sha256": "730db939118c3f5b855a608e45f4d47cc45bb076f27acfc9fb0f8ba6526f19e2",
    },
    "milli_source": {
        "path": "records/phase-two/sources/SOURCE-2026-035.md",
        "bytes": 8969,
        "sha256": "5855319f656172808f9638430f1ee661763c1ebbffce5b1cc7acee72f814de7a",
    },
    "milli_terms": {
        "path": "records/phase-two/terms/TERMS-2026-030.md",
        "bytes": 5154,
        "sha256": "aaa3eb30103cd17e878679ef7614ed88913270720c783f1be74c076edb1fb7bb",
    },
    "milli_gate": {
        "path": "samples/reference/phase-two/OFFICIAL-FALLBACK-SOURCE-GATE-MILLI-2026-001.json",
        "bytes": 19634,
        "sha256": "ab4d0ad9c598f5950b5ae0e6aff2ac1c6ccae3c37622746ec501bd3cd417a40f",
    },
    "accepted_label_reference": {
        "path": "samples/labels/review/grandview/phase-two/intake/GRANDVIEW-OWNER-RESPONSE-INTAKE-2026-001.json",
        "bytes": 9112,
        "sha256": "2897656ad13164295ad2fda78887d8a41b920dfe73e39c12396e55a034b081b5",
    },
    "phase_two_objectives": {
        "path": "docs/phases/phase-02/PHASE_02_OBJECTIVES.md",
        "bytes": 15018,
        "sha256": "3faac18bbdccf223b585e1a03829d4e115be6c1bc88afc6650eef4f3bc599d62",
    },
    "historical_milli_source": {
        "path": "samples/cross-event/phase-two/CROSS-EVENT-SOURCE-2026-001.json",
        "bytes": 921818,
        "sha256": "2c78984d790046db73de68b25e2e0c87a062e2b63a5b957ed10f72382687f6ba",
    },
    "verified_lifecycle_manifest": {
        "path": "records/phase-two/manifests/MANIFEST-2026-047.json",
        "bytes": 8698,
        "sha256": "8391a20b2bd5e9b0bccd3f2f731ff32ea44c64770fd25ba629c9ea19810e573d",
    },
}
REQUIRED_INPUTS = {role: str(spec["path"]) for role, spec in FROZEN_INPUTS.items()}
TRACE_PATHS = tuple(
    sorted(
        {
            *REQUIRED_INPUTS.values(),
            "burnlens/__init__.py",
            "burnlens/build_official_fallback_source_gate.py",
            "burnlens/official_fallback_source_gate.py",
            "pyproject.toml",
            "records/phase-two/prechecks/PRECHECK-2026-058.md",
            "uv.lock",
        }
    )
)

GATE_IDS = {
    "mckenzie": "OFFICIAL-FALLBACK-SOURCE-GATE-MCKENZIE-2026-001",
    "milli": "OFFICIAL-FALLBACK-SOURCE-GATE-MILLI-2026-001",
}

REQUIRED_CRITERIA = {
    "identity",
    "authority",
    "access",
    "rights",
    "provenance",
    "integrity",
    "fitness",
    "privacy-security",
}


class OfficialFallbackGateError(ValueError):
    """Raised when comparison inputs or outputs violate the frozen contract."""


def _write_utf8_lf(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(value)


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise OfficialFallbackGateError(f"INPUT_JSON_INVALID:{path.name}") from error
    if not isinstance(value, dict):
        raise OfficialFallbackGateError(f"INPUT_JSON_OBJECT_REQUIRED:{path.name}")
    return value


def _sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _parse_utc(value: str) -> None:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError) as error:
        raise OfficialFallbackGateError("GENERATED_AT_INVALID") from error
    if not value.endswith("Z") or parsed.tzinfo is None:
        raise OfficialFallbackGateError("GENERATED_AT_UTC_REQUIRED")


def _input_binding(root: Path, role: str, spec: dict[str, Any]) -> dict[str, Any]:
    relative = str(spec["path"])
    path = root / relative
    if not path.is_file():
        raise OfficialFallbackGateError(f"INPUT_MISSING:{relative}")
    binding = {
        "path": relative.replace("\\", "/"),
        "bytes": path.stat().st_size,
        "sha256": _sha256(path),
    }
    if binding["bytes"] != spec["bytes"]:
        raise OfficialFallbackGateError(f"INPUT_BYTES_DRIFT:{role}")
    if binding["sha256"] != spec["sha256"]:
        raise OfficialFallbackGateError(f"INPUT_SHA256_DRIFT:{role}")
    return binding


def _git(root: Path, *arguments: str) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), *arguments],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError) as error:
        raise OfficialFallbackGateError("GIT_TRACE_UNAVAILABLE") from error
    if result.returncode != 0:
        raise OfficialFallbackGateError(f"GIT_TRACE_FAILED:{arguments[0]}")
    return result.stdout.strip()


def _validate_repository_trace(root: Path, git_source_commit: str) -> None:
    top_level = Path(_git(root, "rev-parse", "--show-toplevel")).resolve()
    if top_level != root:
        raise OfficialFallbackGateError("REPOSITORY_ROOT_MISMATCH")
    head = _git(root, "rev-parse", "HEAD")
    if head != git_source_commit:
        raise OfficialFallbackGateError("GIT_SOURCE_COMMIT_MISMATCH")
    tracked = set(
        _git(root, "ls-files", "--", *TRACE_PATHS).replace("\\", "/").splitlines()
    )
    missing = [path for path in TRACE_PATHS if path not in tracked]
    if missing:
        raise OfficialFallbackGateError(f"GIT_TRACE_PATH_UNTRACKED:{missing[0]}")
    status = _git(root, "status", "--porcelain=v1", "--untracked-files=all", "--", *TRACE_PATHS)
    if status:
        raise OfficialFallbackGateError("GIT_RELEVANT_WORKTREE_DIRTY")


def _criterion_summary(gate: dict[str, Any]) -> dict[str, Any]:
    statuses: Counter[str] = Counter()
    sources = gate.get("sources")
    if not isinstance(sources, list) or not sources:
        raise OfficialFallbackGateError("GATE_SOURCES_EMPTY")
    for source in sources:
        criteria = source.get("criteria") if isinstance(source, dict) else None
        if not isinstance(criteria, list):
            raise OfficialFallbackGateError("GATE_CRITERIA_INVALID")
        ids = {item.get("id") for item in criteria if isinstance(item, dict)}
        if ids != REQUIRED_CRITERIA:
            raise OfficialFallbackGateError("GATE_REQUIRED_CRITERIA_DRIFT")
        for criterion in criteria:
            status = criterion.get("status")
            if status not in {"pass", "fail", "unknown", "not-applicable"}:
                raise OfficialFallbackGateError("GATE_CRITERION_STATUS_INVALID")
            statuses[str(status)] += 1
    return {
        "source_count": len(sources),
        "criterion_count": sum(statuses.values()),
        "status_counts": dict(sorted(statuses.items())),
    }


def _validate_gate(gate: dict[str, Any], *, expected_id: str) -> dict[str, Any]:
    if gate.get("contract_version") != "source-gate/v1":
        raise OfficialFallbackGateError("GATE_CONTRACT_VERSION_INVALID")
    if gate.get("assessment_id") != expected_id:
        raise OfficialFallbackGateError("GATE_ASSESSMENT_ID_INVALID")
    if gate.get("provider_bytes_authorized") is not False:
        raise OfficialFallbackGateError("PROVIDER_BYTES_AUTHORIZED_DRIFT")
    decision = gate.get("decision")
    if not isinstance(decision, dict) or decision.get("status") != "blocked":
        raise OfficialFallbackGateError("GATE_DECISION_MUST_BE_BLOCKED")
    blockers = decision.get("blocking_reasons")
    if not isinstance(blockers, list) or not blockers or not all(
        isinstance(item, str) and item.strip() for item in blockers
    ):
        raise OfficialFallbackGateError("GATE_BLOCKERS_REQUIRED")
    approved = decision.get("approved_actions")
    if approved != ["metadata review", "record assessment evidence"]:
        raise OfficialFallbackGateError("GATE_APPROVED_ACTIONS_DRIFT")
    summary = _criterion_summary(gate)
    summary["blocking_reasons"] = blockers
    summary["live_verification_pending"] = decision.get("live_verification_pending") or []
    return summary


def _require_text(path: Path, required: tuple[str, ...], label: str) -> None:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise OfficialFallbackGateError(f"{label}_TEXT_INVALID") from error
    missing = [value for value in required if value not in text]
    if missing:
        raise OfficialFallbackGateError(f"{label}_SEMANTICS_MISSING:{missing[0]}")


def build_source(
    *,
    repository_root: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, Any]:
    _parse_utc(generated_at_utc)
    if run_id != "BL-2026-07-23-official-fallback-comparison-r001":
        raise OfficialFallbackGateError("RUN_ID_INVALID")
    if not re.fullmatch(r"[0-9a-f]{40}", git_source_commit):
        raise OfficialFallbackGateError("GIT_SOURCE_COMMIT_INVALID")
    root = repository_root.resolve()
    bindings = {role: _input_binding(root, role, spec) for role, spec in FROZEN_INPUTS.items()}
    mckenzie_gate = _read_json(root / REQUIRED_INPUTS["mckenzie_gate"])
    milli_gate = _read_json(root / REQUIRED_INPUTS["milli_gate"])
    mckenzie_summary = _validate_gate(mckenzie_gate, expected_id=GATE_IDS["mckenzie"])
    milli_summary = _validate_gate(milli_gate, expected_id=GATE_IDS["milli"])

    accepted = _read_json(root / REQUIRED_INPUTS["accepted_label_reference"])
    if accepted.get("report_id") != "GRANDVIEW-OWNER-RESPONSE-INTAKE-2026-001":
        raise OfficialFallbackGateError("ACCEPTED_LABEL_REFERENCE_ID_INVALID")
    outcome = accepted.get("outcome") or {}
    boundaries = accepted.get("boundaries") or {}
    expected_outcome = {
        "event_group_count": 5,
        "minimum_event_group_count": 6,
        "minimum_event_group_gate_passed": False,
        "dataset_fitness_reopened": False,
        "cumulative_owner_approved_region_labels": 10,
        "cumulative_accepted_core_pixels": 236,
        "cumulative_accepted_core_area_ha": 9.44,
        "cumulative_excluded_unknown_ring_pixels": 431,
    }
    if any(outcome.get(key) != value for key, value in expected_outcome.items()):
        raise OfficialFallbackGateError("ACCEPTED_LABEL_REFERENCE_STATE_DRIFT")
    if any(
        boundaries.get(key) is not False
        for key in ("dataset_created", "split_created", "baseline_created", "model_created")
    ):
        raise OfficialFallbackGateError("ACCEPTED_LABEL_BOUNDARY_DRIFT")

    lifecycle = _read_json(root / REQUIRED_INPUTS["verified_lifecycle_manifest"])
    expected_lifecycle = {
        "manifest_id": "MANIFEST-2026-047",
        "manifest_version": "0.47.0",
        "manifest_role": "verified-release-lifecycle-reconciliation",
        "repository": "drwbkr1/burnlens-deschutes",
        "software_version": "0.45.0",
        "checkpoint_commit": "d65c24f59ce0c854ba230aa977eaf718d881d952",
        "version_tag": "v0.45.0-petes-lake-material-defer",
        "label_set_version": "owner-approved-prototype-region-labels-v0.3.0",
        "dataset_version": None,
        "split_version": None,
        "baseline_version": None,
        "model_version": None,
    }
    if any(lifecycle.get(key) != value for key, value in expected_lifecycle.items()):
        raise OfficialFallbackGateError("VERIFIED_LIFECYCLE_MANIFEST_DRIFT")

    _require_text(
        root / REQUIRED_INPUTS["phase_two_objectives"],
        (
            "Both binary classes and explicit unknown boundaries must pass in at least six complete whole-event groups",
            "Owner yes is necessary but insufficient.",
            "Phase Two does not train the U-Net model.",
        ),
        "PHASE_OBJECTIVE",
    )
    _require_text(
        root / REQUIRED_INPUTS["mckenzie_source"],
        ("U02 disposition is `defer`", "28,966,292", "NWI cannot establish burned pixels"),
        "MCKENZIE_SOURCE",
    )
    _require_text(
        root / REQUIRED_INPUTS["milli_source"],
        ("DEFER_MILLI_BEFORE_CURRENT_EVENT_GEOMETRY_OR_SENTINEL_SELECTION", "no current Milli geometry was processed"),
        "MILLI_SOURCE",
    )

    candidates = [
        {
            "candidate_id": "candidate-petes-lake-mckenzie-hu8-17090004",
            "display_name": "McKenzie HUC8 NWI",
            "gate_id": GATE_IDS["mckenzie"],
            "unit_disposition": "defer",
            "gate_status": "blocked",
            "selected": False,
            "provider_bytes_authorized": False,
            "gate_summary": mckenzie_summary,
        },
        {
            "candidate_id": "candidate-milli-0843-cs-2017",
            "display_name": "Milli 0843 CS",
            "gate_id": GATE_IDS["milli"],
            "unit_disposition": "defer",
            "gate_status": "blocked",
            "selected": False,
            "provider_bytes_authorized": False,
            "gate_summary": milli_summary,
        },
    ]
    return {
        "source_id": SOURCE_ID,
        "source_schema_version": SOURCE_SCHEMA_VERSION,
        "serialization": "UTF-8 JSON with LF canonical line endings",
        "generated_at_utc": generated_at_utc,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": TASK_ISSUE,
        "run_id": run_id,
        "git_source_commit": git_source_commit,
        "software_version": SOFTWARE_VERSION,
        "input_bindings": bindings,
        "candidate_order": [item["candidate_id"] for item in candidates],
        "candidates": candidates,
        "reference_state": {
            **expected_outcome,
            "prototype_class_counts": {"background": 5, "burned": 5},
            "dataset_created": False,
            "split_created": False,
            "baseline_created": False,
            "model_created": False,
        },
        "phase_objective": {
            "phase": 2,
            "objective": 4,
            "minimum_complete_event_groups": 6,
            "current_complete_event_groups": 5,
            "result": "blocked_before_six_complete_whole_event_groups",
            "owner_yes_is_necessary_but_insufficient": True,
        },
        "comparison_dimensions": [
            "scientific_role",
            "rights",
            "uncertainty",
            "leakage",
            "custody",
            "privacy_security",
            "reproducibility",
            "acquisition_cost",
            "phase_objective_value",
            "portfolio_value",
        ],
        "boundaries": {
            "provider_bytes_authorized": False,
            "provider_bytes_acquired": 0,
            "custody_mutated": False,
            "selected_candidate": None,
            "candidate_created": False,
            "owner_response_created": False,
            "label_created": False,
            "sixth_event_created": False,
            "dataset_created": False,
            "split_created": False,
            "baseline_created": False,
            "model_created": False,
            "metric_created": False,
            "deployment_created": False,
        },
    }


def _comparison_rows() -> list[dict[str, str]]:
    return [
        {
            "dimension": "Scientific role",
            "mckenzie": "Approximate wetlands/deepwater context and conservative exclusion for Petes Lake only.",
            "milli": "Prospective Sentinel optical plus program-limited BAER, MTBS, and RAVG reference evidence.",
        },
        {
            "dimension": "Rights",
            "mckenzie": "Local retention, processing, and derived-publication rights remain unknown; raw redistribution blocked.",
            "milli": "Sentinel grant is supportable in principle; exact future BAER/MTBS/RAVG delivery rights remain unknown.",
        },
        {
            "dimension": "Uncertainty",
            "mckenzie": "Package members, project dates, scale, coverage, omissions, and Petes relationship are unopened.",
            "milli": "Complete-boundary union, seams, grids, cloud/snow, registration, and both-class evidence are unproved.",
        },
        {
            "dimension": "Leakage",
            "mckenzie": "Same Petes event; adds no independent event and cannot establish either class.",
            "milli": "Historically separate by 61.035 km, but current event/time/geography grouping was not refreshed.",
        },
        {
            "dimension": "Custody",
            "mckenzie": "Zero bytes; prospective one 28,966,292-byte ZIP through a new controlled intake.",
            "milli": "Zero bytes; prospective multi-tile Sentinel plus three program-source transactions.",
        },
        {
            "dimension": "Privacy / security",
            "mckenzie": "Public metadata only; future archive remains untrusted and must screen notices, attributes, contacts, and logos.",
            "milli": "Public metadata only; future provider archives and queue/email delivery details remain private and untrusted.",
        },
        {
            "dimension": "Reproducibility",
            "mckenzie": "Strong live asset HEAD identity, but member provenance and incomplete failed-attempt trace block reproduction.",
            "milli": "Historical planning snapshot only; current source roster stopped and the legacy vertex-only predicate is insufficient.",
        },
        {
            "dimension": "Acquisition cost",
            "mckenzie": "Known prospective body: 28.97 MB (27.62 MiB), one ZIP; no fee/account observed at metadata stage.",
            "milli": "Higher and unquantified; exact Sentinel roster, OData sizes, and program-delivery transactions were not refreshed.",
        },
        {
            "dimension": "Objective Four value",
            "mckenzie": "Could improve exclusions but cannot provide burned plus affirmative-background cores or complete Petes.",
            "milli": "Higher theoretical sixth-event value, but no class, unknown ring, owner review, or non-owner promotion gate exists.",
        },
        {
            "dimension": "Portfolio value",
            "mckenzie": "Shows disciplined source precedence and honest exclusion-context limits.",
            "milli": "Could show cross-event transfer and seam handling; current unresolved complexity outweighs evidence value.",
        },
    ]


def build_report(source: dict[str, Any], *, source_bytes: int, source_sha256: str) -> dict[str, Any]:
    if source.get("source_id") != SOURCE_ID or source.get("source_schema_version") != SOURCE_SCHEMA_VERSION:
        raise OfficialFallbackGateError("SOURCE_IDENTITY_INVALID")
    boundaries = source.get("boundaries") or {}
    expected_false = (
        "provider_bytes_authorized",
        "custody_mutated",
        "candidate_created",
        "owner_response_created",
        "label_created",
        "sixth_event_created",
        "dataset_created",
        "split_created",
        "baseline_created",
        "model_created",
        "metric_created",
        "deployment_created",
    )
    if any(boundaries.get(key) is not False for key in expected_false):
        raise OfficialFallbackGateError("SOURCE_BOUNDARY_DRIFT")
    if boundaries.get("provider_bytes_acquired") != 0 or boundaries.get("selected_candidate") is not None:
        raise OfficialFallbackGateError("SOURCE_BYTES_OR_SELECTION_DRIFT")
    candidates = source.get("candidates")
    if not isinstance(candidates, list) or [item.get("candidate_id") for item in candidates] != [
        "candidate-petes-lake-mckenzie-hu8-17090004",
        "candidate-milli-0843-cs-2017",
    ]:
        raise OfficialFallbackGateError("SOURCE_CANDIDATE_ORDER_DRIFT")
    if any(
        item.get("gate_status") != "blocked"
        or item.get("unit_disposition") != "defer"
        or item.get("selected") is not False
        or item.get("provider_bytes_authorized") is not False
        for item in candidates
    ):
        raise OfficialFallbackGateError("SOURCE_CANDIDATE_DISPOSITION_DRIFT")
    return {
        "report_id": REPORT_ID,
        "report_schema_version": REPORT_SCHEMA_VERSION,
        "report_version": REPORT_VERSION,
        "generated_at_utc": source["generated_at_utc"],
        "repository": source["repository"],
        "task_issue": source["task_issue"],
        "run_id": source["run_id"],
        "git_source_commit": source["git_source_commit"],
        "software_version": source["software_version"],
        "source_binding": {
            "source_id": SOURCE_ID,
            "bytes": source_bytes,
            "sha256": source_sha256,
        },
        "warning": WARNING,
        "decision": DECISION,
        "decision_summary": (
            "Select neither route. McKenzie HUC8 NWI and Milli 0843 CS both remain deferred because "
            "required rights and evidence gates have not passed."
        ),
        "selected_candidate": None,
        "candidate_results": [
            {
                "candidate_id": item["candidate_id"],
                "display_name": item["display_name"],
                "gate_id": item["gate_id"],
                "gate_status": item["gate_status"],
                "disposition": item["unit_disposition"],
                "selected": False,
                "source_count": item["gate_summary"]["source_count"],
                "criterion_count": item["gate_summary"]["criterion_count"],
                "criterion_status_counts": item["gate_summary"]["status_counts"],
                "blocking_reasons": item["gate_summary"]["blocking_reasons"],
            }
            for item in candidates
        ],
        "comparison": _comparison_rows(),
        "reference_state": source["reference_state"],
        "phase_objective": source["phase_objective"],
        "portfolio_narrative": (
            "The portfolio-strengthening result is disciplined refusal: BurnLens identifies the next source "
            "weakness, tests the smallest legal and evidentiary route, retains failures, and does not turn "
            "available metadata into a sixth event or a dataset."
        ),
        "reconsideration": (
            "Neither route is permanently rejected. Reconsideration requires a new issue and immutable run, "
            "stronger exact rights evidence, fresh source identities, and every applicable scientific and custody gate."
        ),
        "boundaries": dict(boundaries),
        "attribution": [
            "U.S. Fish and Wildlife Service National Wetlands Inventory",
            "Monitoring Trends in Burn Severity Project (U.S. Geological Survey and USDA Forest Service)",
            "Copernicus Sentinel programme / European Union; no Sentinel pixels are reproduced here",
        ],
        "outputs": {},
    }


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    return ImageFont.load_default(size=size)


def _draw_wrapped(
    draw: ImageDraw.ImageDraw,
    text: str,
    *,
    xy: tuple[int, int],
    width_chars: int,
    font: ImageFont.ImageFont,
    fill: str,
    line_height: int,
) -> int:
    x, y = xy
    lines: list[str] = []
    for paragraph in text.splitlines() or [""]:
        lines.extend(textwrap.wrap(paragraph, width=width_chars) or [""])
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += line_height
    return y


def render_png(report: dict[str, Any], path: Path) -> None:
    image = Image.new("RGB", (1600, 1940), "#f5f2ea")
    draw = ImageDraw.Draw(image)
    navy, rust, ink, muted, white = "#19324a", "#a84b32", "#1f2933", "#59636e", "#ffffff"
    draw.rectangle((0, 0, 1600, 190), fill=navy)
    draw.text((64, 38), "BURNLENS / PHASE TWO / OBJECTIVE FOUR", font=_font(24), fill="#b9d4e8")
    draw.text((64, 78), "Official fallback source gate", font=_font(48), fill=white)
    draw.text((64, 139), "SELECT NEITHER  /  BOTH ROUTES DEFERRED", font=_font(26), fill="#ffd2bf")

    draw.rounded_rectangle((52, 218, 1548, 322), radius=18, fill="#fff1eb", outline=rust, width=3)
    _draw_wrapped(
        draw,
        report["decision_summary"],
        xy=(78, 240),
        width_chars=105,
        font=_font(23),
        fill=ink,
        line_height=29,
    )

    cards = [
        (52, 354, 784, 750, report["candidate_results"][0]),
        (816, 354, 1548, 750, report["candidate_results"][1]),
    ]
    for left, top, right, bottom, candidate in cards:
        draw.rounded_rectangle((left, top, right, bottom), radius=18, fill=white, outline="#c9c2b6", width=2)
        draw.text((left + 28, top + 24), candidate["display_name"], font=_font(30), fill=navy)
        draw.text((left + 28, top + 68), "DEFER / BLOCKED / UNSELECTED", font=_font(20), fill=rust)
        counts = candidate["criterion_status_counts"]
        draw.text(
            (left + 28, top + 104),
            f"{candidate['source_count']} source(s)  |  {candidate['criterion_count']} criteria  |  "
            f"pass {counts.get('pass', 0)} / unknown {counts.get('unknown', 0)} / fail {counts.get('fail', 0)}",
            font=_font(17),
            fill=muted,
        )
        y = top + 143
        for blocker in candidate["blocking_reasons"][:3]:
            y = _draw_wrapped(
                draw,
                f"- {blocker}",
                xy=(left + 28, y),
                width_chars=64,
                font=_font(16),
                fill=ink,
                line_height=21,
            ) + 4

    draw.text((54, 780), "FULL DECISION COMPARISON", font=_font(24), fill=navy)
    draw.text((300, 812), "MCKENZIE HUC8 NWI", font=_font(16), fill=muted)
    draw.text((940, 812), "MILLI 0843 CS", font=_font(16), fill=muted)
    y = 840
    for row in report["comparison"]:
        draw.rounded_rectangle((52, y, 1548, y + 82), radius=10, fill=white, outline="#ddd7cd", width=1)
        draw.text((70, y + 14), row["dimension"].upper(), font=_font(15), fill=rust)
        _draw_wrapped(draw, row["mckenzie"], xy=(300, y + 12), width_chars=54, font=_font(14), fill=ink, line_height=18)
        _draw_wrapped(draw, row["milli"], xy=(940, y + 12), width_chars=54, font=_font(14), fill=ink, line_height=18)
        y += 91

    draw.rounded_rectangle((52, 1770, 1548, 1832), radius=12, fill=navy)
    draw.text(
        (70, 1790),
        "5 / 6 complete events  |  provider bytes 0  |  selected candidate none  |  dataset / split / baseline / model absent",
        font=_font(18),
        fill=white,
    )
    draw.text((54, 1862), report["warning"], font=_font(13), fill=muted)
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, format="PNG", optimize=False, compress_level=9)


def render_html(report: dict[str, Any], path: Path, png_name: str) -> None:
    candidates = "".join(
        f"""<article class="card"><p class="eyebrow">{escape(item['disposition'].upper())} / {escape(item['gate_status'].upper())}</p>
<h2>{escape(item['display_name'])}</h2><p><code>{escape(item['candidate_id'])}</code></p>
<p>{item['source_count']} source(s), {item['criterion_count']} criteria; selected: no.</p>
<ul>{''.join(f'<li>{escape(reason)}</li>' for reason in item['blocking_reasons'])}</ul></article>"""
        for item in report["candidate_results"]
    )
    rows = "".join(
        f'<tr><th scope="row">{escape(row["dimension"])}</th>'
        f'<td data-label="McKenzie HUC8 NWI">{escape(row["mckenzie"])}</td>'
        f'<td data-label="Milli 0843 CS">{escape(row["milli"])}</td></tr>'
        for row in report["comparison"]
    )
    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>BurnLens official fallback source gate</title><style>
:root{{--navy:#19324a;--rust:#a84b32;--paper:#f5f2ea;--ink:#1f2933;--muted:#59636e;}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 system-ui,sans-serif}}
header{{background:var(--navy);color:white;padding:2.6rem max(1.25rem,5vw)}}header p{{max-width:75rem}}main{{max-width:1180px;margin:auto;padding:2rem 1.25rem 4rem}}
.warning{{border-left:.4rem solid var(--rust);background:#fff1eb;padding:1rem 1.2rem}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:1.2rem;margin:1.5rem 0}}
.card{{background:white;border:1px solid #d8d1c6;border-radius:1rem;padding:1.3rem;min-width:0}}.eyebrow{{color:var(--rust);font-weight:800;letter-spacing:.08em}}
code{{overflow-wrap:anywhere}}table{{width:100%;border-collapse:collapse;background:white}}th,td{{padding:.8rem;vertical-align:top;border:1px solid #ddd7cd;text-align:left}}thead th{{background:var(--navy);color:white}}
.hero{{width:100%;height:auto;border:1px solid #c9c2b6}}.facts{{display:flex;flex-wrap:wrap;gap:.7rem;margin:1rem 0}}.facts span{{background:white;border-radius:999px;padding:.45rem .8rem;border:1px solid #d8d1c6}}
@media(max-width:760px){{.grid{{grid-template-columns:1fr}}table,thead,tbody,tr,th,td{{display:block}}thead{{display:none}}tr{{border-bottom:1rem solid var(--paper)}}th,td{{border-bottom:0}}td::before{{content:attr(data-label);display:block;color:var(--muted);font-size:.78rem;font-weight:800;letter-spacing:.04em;margin-bottom:.25rem;text-transform:uppercase}}}}
</style></head><body><header><p>BurnLens / Phase Two / Objective Four</p><h1>Official fallback source gate</h1>
<p><strong>Select neither.</strong> Both candidates remain deferred; no provider bytes or intake is authorized.</p></header><main>
<p class="warning">{escape(report['warning'])}</p><img class="hero" src="{escape(png_name)}" alt="BurnLens comparison showing McKenzie and Milli both deferred and unselected">
<section><h2>Decision</h2><p>{escape(report['decision_summary'])}</p><p>{escape(report['reconsideration'])}</p></section>
<section class="grid">{candidates}</section><section><h2>Evidence comparison</h2><table><thead><tr><th>Dimension</th><th>McKenzie HUC8 NWI</th><th>Milli 0843 CS</th></tr></thead><tbody>{rows}</tbody></table></section>
<section><h2>Phase objective and portfolio meaning</h2><div class="facts"><span>Complete events: 5 / 6</span><span>Provider bytes: 0</span><span>Selected candidate: none</span><span>Dataset / split / baseline / model: absent</span></div>
<p>{escape(report['portfolio_narrative'])}</p></section><section><h2>Trace</h2><p>Run <code>{escape(report['run_id'])}</code>; source commit <code>{escape(report['git_source_commit'])}</code>; software {escape(report['software_version'])}; report {escape(report['report_version'])}.</p>
<p>Official sources and exact source/terms records govern over this derived comparison.</p></section></main></body></html>"""
    _write_utf8_lf(path, html)


def run_report(
    *,
    repository_root: Path,
    output_directory: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, Path]:
    root = repository_root.resolve()
    if output_directory.exists():
        raise OfficialFallbackGateError("OUTPUT_DIRECTORY_ALREADY_EXISTS")
    _validate_repository_trace(root, git_source_commit)
    output_directory.mkdir(parents=True)
    source = build_source(
        repository_root=root,
        generated_at_utc=generated_at_utc,
        run_id=run_id,
        git_source_commit=git_source_commit,
    )
    source_path = output_directory / f"{SOURCE_ID}.json"
    _write_utf8_lf(source_path, json.dumps(source, indent=2) + "\n")
    report = build_report(source, source_bytes=source_path.stat().st_size, source_sha256=_sha256(source_path))
    html_path = output_directory / f"{REPORT_ID}.html"
    png_path = output_directory / f"{REPORT_ID}.png"
    render_png(report, png_path)
    render_html(report, html_path, png_path.name)
    report["outputs"] = {
        "html": {"path": html_path.name, "bytes": html_path.stat().st_size, "sha256": _sha256(html_path)},
        "png": {
            "path": png_path.name,
            "bytes": png_path.stat().st_size,
            "sha256": _sha256(png_path),
            "width": 1600,
            "height": 1940,
        },
    }
    report_path = output_directory / f"{REPORT_ID}.json"
    _write_utf8_lf(report_path, json.dumps(report, indent=2) + "\n")
    return {"source": source_path, "json": report_path, "html": html_path, "png": png_path}
