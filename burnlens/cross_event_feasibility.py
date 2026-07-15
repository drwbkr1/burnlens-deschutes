"""Assess and render cross-event feasibility from one frozen metadata snapshot."""

from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from html import escape
from itertools import combinations
import json
from math import asin, cos, radians, sin, sqrt
from pathlib import Path
import re
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from .cross_event_source import SOURCE_ID, SOURCE_SCHEMA_VERSION


REPORT_ID = "CROSS-EVENT-FITNESS-2026-001"
REPORT_SCHEMA_VERSION = "0.1.0"
REPORT_VERSION = "cross-event-feasibility-v0.1.0"
SOFTWARE_VERSION = "0.10.0"
AOI_VERSION = "aoi-darlene3-model-v0.2.0"
TARGET_VERSION = "target-burn-scar-v0.2.0"
LABEL_SCHEMA_VERSION = "burn-scar-five-state-schema-v0.1.0"
CLOUD_LIMIT_PERCENT = 20.0
SELECTION_COUNT = 2
WARNING = (
    "Experimental BurnLens portfolio evidence. Not official wildfire information. Not emergency "
    "guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern."
)


class CrossEventFeasibilityError(ValueError):
    """Raised when frozen feasibility evidence is incomplete or contradictory."""


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    return ImageFont.load_default(size=size)


def _write_utf8_lf(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise CrossEventFeasibilityError(f"INPUT_JSON_INVALID:{path.name}") from error
    if not isinstance(value, dict):
        raise CrossEventFeasibilityError(f"INPUT_JSON_OBJECT_REQUIRED:{path.name}")
    return value


def _sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sha256_lf_text(path: Path) -> str:
    try:
        with path.open("r", encoding="utf-8", newline=None) as handle:
            return sha256(handle.read().encode("utf-8")).hexdigest()
    except (OSError, UnicodeError) as error:
        raise CrossEventFeasibilityError(f"INPUT_TEXT_INVALID:{path.name}") from error


def _parse_time(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError) as error:
        raise CrossEventFeasibilityError(f"DATETIME_INVALID:{value}") from error
    if parsed.tzinfo is None:
        raise CrossEventFeasibilityError(f"DATETIME_TIMEZONE_REQUIRED:{value}")
    return parsed.astimezone(timezone.utc)


def _haversine_km(first: tuple[float, float], second: tuple[float, float]) -> float:
    lon1, lat1 = map(radians, first)
    lon2, lat2 = map(radians, second)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    value = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 6371.0088 * 2 * asin(sqrt(value))


def _bbox_overlap(first: list[float], second: list[float]) -> bool:
    return not (
        first[2] <= second[0]
        or second[2] <= first[0]
        or first[3] <= second[1]
        or second[3] <= first[1]
    )


def _slug(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not normalized:
        raise CrossEventFeasibilityError("GROUP_SLUG_EMPTY")
    return normalized


def _validate_inputs(
    source: dict[str, Any],
    aoi: dict[str, Any],
    optical: dict[str, Any],
    label_qa: dict[str, Any],
) -> None:
    if source.get("record_id") != SOURCE_ID or source.get("schema_version") != SOURCE_SCHEMA_VERSION:
        raise CrossEventFeasibilityError("SOURCE_SNAPSHOT_IDENTITY_UNEXPECTED")
    if source.get("repository") != "drwbkr1/burnlens-deschutes" or source.get("task_issue") != 357:
        raise CrossEventFeasibilityError("SOURCE_SNAPSHOT_SCOPE_UNEXPECTED")
    boundaries = source.get("boundaries") or {}
    required_false = (
        "provider_imagery_downloaded",
        "dataset_created",
        "split_created",
        "baseline_created",
        "model_created",
    )
    if any(boundaries.get(name) is not False for name in required_false):
        raise CrossEventFeasibilityError("SOURCE_SNAPSHOT_BOUNDARY_UNEXPECTED")
    if boundaries.get("raw_provider_bytes_retained") != 0 or boundaries.get("label_pixels_created") != 0:
        raise CrossEventFeasibilityError("SOURCE_SNAPSHOT_BYTES_OR_LABELS_UNEXPECTED")
    events = source.get("events")
    if not isinstance(events, list) or not events:
        raise CrossEventFeasibilityError("SOURCE_EVENTS_EMPTY")
    ids = [str(item.get("fire_id")) for item in events]
    if len(ids) != len(set(ids)):
        raise CrossEventFeasibilityError("SOURCE_EVENT_IDS_DUPLICATE")
    if aoi.get("report_id") != "AOI-FINAL-2026-001" or aoi.get("decision") != "ACCEPT_FINAL_MODELING_AOI":
        raise CrossEventFeasibilityError("AOI_REPORT_UNEXPECTED")
    if aoi.get("aoi_version") != AOI_VERSION:
        raise CrossEventFeasibilityError("AOI_VERSION_UNEXPECTED")
    if optical.get("report_id") != "OPTICAL-PAIR-2026-001":
        raise CrossEventFeasibilityError("OPTICAL_REPORT_UNEXPECTED")
    if optical.get("decision") != "ACCEPT_OPTICAL_PAIR_FOR_PROTOCOL_DEFER_LABELS":
        raise CrossEventFeasibilityError("OPTICAL_DECISION_UNEXPECTED")
    if optical.get("target_version") != TARGET_VERSION:
        raise CrossEventFeasibilityError("TARGET_VERSION_UNEXPECTED")
    if label_qa.get("report_id") != "LABEL-QA-2026-001":
        raise CrossEventFeasibilityError("LABEL_QA_REPORT_UNEXPECTED")
    if label_qa.get("decision") != "ACCEPT_REVIEWABLE_LABEL_PROPOSAL_DEFER_DATASET":
        raise CrossEventFeasibilityError("LABEL_QA_DECISION_UNEXPECTED")
    if label_qa.get("label_schema_version") != LABEL_SCHEMA_VERSION:
        raise CrossEventFeasibilityError("LABEL_SCHEMA_VERSION_UNEXPECTED")


def _scene_group_key(item: dict[str, Any]) -> tuple[str, str, int, str]:
    try:
        return (
            str(item["platform"]),
            str(item["grid_code"]),
            int(item["relative_orbit"]),
            str(item["processing_version"]),
        )
    except (KeyError, TypeError, ValueError) as error:
        raise CrossEventFeasibilityError("STAC_SCENE_GROUP_FIELDS_INVALID") from error


def _validated_scene(item: dict[str, Any]) -> dict[str, Any]:
    required_text = ("id", "datetime", "platform", "grid_code", "processing_version", "product_href")
    if any(not isinstance(item.get(name), str) or not item[name] for name in required_text):
        raise CrossEventFeasibilityError("STAC_SCENE_IDENTITY_INCOMPLETE")
    if int(item.get("product_bytes") or 0) <= 0:
        raise CrossEventFeasibilityError("STAC_PRODUCT_SIZE_INVALID")
    if not item.get("product_filename") or not item.get("provider_checksum"):
        raise CrossEventFeasibilityError("STAC_PRODUCT_INTEGRITY_METADATA_INCOMPLETE")
    _parse_time(item["datetime"])
    _scene_group_key(item)
    return item


def _choose_pair(event: dict[str, Any]) -> dict[str, Any] | None:
    windows = {item.get("window"): item for item in event.get("stac_windows", [])}
    if "pre" not in windows:
        return None
    ignition = _parse_time(f"{event['ignition_date']}T00:00:00Z")
    pre_items = [
        _validated_scene(item)
        for item in windows["pre"].get("items", [])
        if float(item.get("cloud_cover_percent", 101.0)) <= CLOUD_LIMIT_PERCENT
    ]
    for post_name in ("post_initial", "post_extended"):
        post_items = [
            _validated_scene(item)
            for item in (windows.get(post_name) or {}).get("items", [])
            if float(item.get("cloud_cover_percent", 101.0)) <= CLOUD_LIMIT_PERCENT
        ]
        pairs: list[tuple[tuple[Any, ...], dict[str, Any], dict[str, Any]]] = []
        for pre in pre_items:
            for post in post_items:
                if _scene_group_key(pre) != _scene_group_key(post):
                    continue
                pre_time = _parse_time(pre["datetime"])
                post_time = _parse_time(post["datetime"])
                if pre_time >= ignition or post_time <= ignition:
                    continue
                pre_lag = (ignition - pre_time).total_seconds() / 86400.0
                post_lag = (post_time - ignition).total_seconds() / 86400.0
                score = (
                    float(pre["cloud_cover_percent"]) + float(post["cloud_cover_percent"]),
                    max(float(pre["cloud_cover_percent"]), float(post["cloud_cover_percent"])),
                    pre_lag + post_lag,
                    post_lag,
                    pre_lag,
                    str(pre["id"]),
                    str(post["id"]),
                )
                pairs.append((score, pre, post))
        if pairs:
            _, pre, post = min(pairs, key=lambda item: item[0])
            key = _scene_group_key(pre)
            digest = sha256(f"{pre['id']}|{post['id']}".encode("utf-8")).hexdigest()[:12]
            return {
                "post_window": post_name,
                "pre_scene": pre,
                "post_scene": post,
                "scene_group": {
                    "platform": key[0],
                    "grid_code": key[1],
                    "relative_orbit": key[2],
                    "processing_version": key[3],
                },
                "scene_group_id": f"scene-{_slug(str(event['fire_id']))}-{digest}",
                "elapsed_days": round(
                    (_parse_time(post["datetime"]) - _parse_time(pre["datetime"])).total_seconds()
                    / 86400.0,
                    4,
                ),
                "metadata_cloud_limit_percent": CLOUD_LIMIT_PERCENT,
                "selection_rule": (
                    "Prefer the initial post-fire window; require the same platform, MGRS tile, relative orbit, "
                    "and processing baseline; reject product cloud metadata above 20%; then minimize combined "
                    "cloud, maximum cloud, temporal span, and stable scene IDs."
                ),
            }
    return None


def _event_assessment(event: dict[str, Any], darlene_bbox: list[float]) -> dict[str, Any]:
    reasons: list[str] = []
    boundary = event.get("boundary")
    if not event.get("boundary_available") or not isinstance(boundary, dict):
        reasons.append("MTBS_BOUNDARY_ABSENT")
    if not event.get("pre_stac_eligible"):
        reasons.append("DATE_TYPE_OR_SIZE_FILTER_FAILED")
    pair = _choose_pair(event) if not reasons else None
    bbox = [float(value) for value in boundary.get("bbox", [])] if boundary else []
    if len(bbox) != 4:
        reasons.append("BOUNDARY_BBOX_INVALID")
    elif _bbox_overlap(bbox, darlene_bbox):
        reasons.append("BOUNDARY_OVERLAPS_DARLENE_AOI")
    if pair is None and "DATE_TYPE_OR_SIZE_FILTER_FAILED" not in reasons:
        reasons.append("NO_COMPATIBLE_LOW_CLOUD_SINGLE_TILE_PAIR")
    slug = _slug(f"{event['fire_name']}-{event['year']}")
    center = (float(event["longitude"]), float(event["latitude"]))
    darlene_center = (
        (darlene_bbox[0] + darlene_bbox[2]) / 2,
        (darlene_bbox[1] + darlene_bbox[3]) / 2,
    )
    return {
        "fire_id": event["fire_id"],
        "fire_name": event["fire_name"],
        "ignition_date": event["ignition_date"],
        "year": int(event["year"]),
        "acres": float(event["acres"]),
        "representative_point_wgs84": [center[0], center[1]],
        "county_membership": "REPRESENTATIVE_POINT_INSIDE_CENSUS_GEOID_41017",
        "boundary_bbox_wgs84": bbox,
        "assessment_type": boundary.get("assessment_type") if boundary else None,
        "distance_from_darlene_center_km": round(_haversine_km(darlene_center, center), 3),
        "event_group_id": f"event-{slug}",
        "geography_group_id": f"geo-{slug}-mtbs-boundary",
        "time_group_id": f"time-{event['ignition_date']}",
        "scene_pair": pair,
        "eligible": not reasons,
        "reasons": reasons or ["ALL_METADATA_FEASIBILITY_RULES_PASS"],
        "source_geometry": boundary.get("geometry") if boundary else None,
    }


def _select_candidates(
    assessments: list[dict[str, Any]], darlene_center: tuple[float, float]
) -> list[dict[str, Any]]:
    eligible = [item for item in assessments if item["eligible"]]
    if len(eligible) <= SELECTION_COUNT:
        return sorted(eligible, key=lambda item: str(item["fire_id"]))
    ranked: list[tuple[float, tuple[str, ...], tuple[dict[str, Any], ...]]] = []
    for group in combinations(eligible, SELECTION_COUNT):
        points = [darlene_center] + [tuple(item["representative_point_wgs84"]) for item in group]
        distances = [
            _haversine_km(first, second) for first, second in combinations(points, 2)
        ]
        ids = tuple(sorted(str(item["fire_id"]) for item in group))
        ranked.append((min(distances), ids, group))
    _, _, selected = sorted(ranked, key=lambda item: (-item[0], item[1]))[0]
    return sorted(selected, key=lambda item: str(item["fire_id"]))


def build_report(
    *,
    source: dict[str, Any],
    aoi: dict[str, Any],
    optical: dict[str, Any],
    label_qa: dict[str, Any],
    input_hashes: dict[str, str],
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
    visual_review_decision: str,
    visual_review_notes: str,
) -> dict[str, Any]:
    _validate_inputs(source, aoi, optical, label_qa)
    _parse_time(generated_at_utc)
    allowed_visual_decisions = {
        "PENDING_VISUAL_REVIEW",
        "ACCEPT_METADATA_FEASIBILITY",
        "ACCEPT_WITH_REMEDIATION",
        "REJECT_METADATA_FEASIBILITY",
    }
    if visual_review_decision not in allowed_visual_decisions:
        raise CrossEventFeasibilityError("VISUAL_REVIEW_DECISION_INVALID")
    if not re.fullmatch(r"[0-9a-f]{40}", git_source_commit):
        raise CrossEventFeasibilityError("GIT_SOURCE_COMMIT_INVALID")
    if not run_id.strip():
        raise CrossEventFeasibilityError("RUN_ID_REQUIRED")
    darlene_bbox = [float(value) for value in aoi["derivation"]["aoi_bbox_wgs84"]]
    darlene_center = (
        (darlene_bbox[0] + darlene_bbox[2]) / 2,
        (darlene_bbox[1] + darlene_bbox[3]) / 2,
    )
    assessments = [_event_assessment(event, darlene_bbox) for event in source["events"]]
    selected = _select_candidates(assessments, darlene_center)
    selected_ids = {str(item["fire_id"]) for item in selected}
    for item in assessments:
        if str(item["fire_id"]) in selected_ids:
            item["disposition"] = "SELECTED_FOR_EXACT_SOURCE_ACQUISITION"
        elif item["eligible"]:
            item["disposition"] = "ELIGIBLE_NOT_SELECTED_WITHIN_BOUNDED_COUNT"
        else:
            item["disposition"] = "EXCLUDED_FROM_ACQUISITION"
    pairwise: list[dict[str, Any]] = []
    group_points = [
        ("event-darlene3-2024", darlene_center),
        *[
            (item["event_group_id"], tuple(item["representative_point_wgs84"]))
            for item in selected
        ],
    ]
    for first, second in combinations(group_points, 2):
        pairwise.append(
            {
                "first_event_group_id": first[0],
                "second_event_group_id": second[0],
                "representative_point_distance_km": round(_haversine_km(first[1], second[1]), 3),
            }
        )
    selected_overlap = any(
        _bbox_overlap(first["boundary_bbox_wgs84"], second["boundary_bbox_wgs84"])
        for first, second in combinations(selected, 2)
    )
    if len(selected) >= SELECTION_COUNT and not selected_overlap:
        decision = "SELECT_CROSS_EVENT_ACQUISITION_CANDIDATES"
        detail = (
            "Two current MTBS event groups inside Deschutes County have non-overlapping boundaries and exact, "
            "compatible Sentinel-2 metadata pairs. Acquire only these frozen products next; availability is not pixel fitness."
        )
    elif selected:
        decision = "REMEDIATE_CROSS_EVENT_FEASIBILITY"
        detail = "Only one eligible independent event group remains; revise the bounded search before acquisition."
    else:
        decision = "STOP_DATASET_PATH"
        detail = "No eligible independent cross-event group remains under the frozen rules."
    darlene_scene_ids = [
        optical["pre_scene"]["native_id"],
        optical["post_scene"]["native_id"],
    ]
    return {
        "report_id": REPORT_ID,
        "schema_version": REPORT_SCHEMA_VERSION,
        "report_version": REPORT_VERSION,
        "serialization": "UTF-8 JSON and HTML with LF canonical line endings; deterministic PNG",
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": 357,
        "branch": "codex/p2o4-t02-cross-event-feasibility",
        "git_source_commit": git_source_commit,
        "software_version": SOFTWARE_VERSION,
        "application_version": None,
        "aoi_version": AOI_VERSION,
        "target_version": TARGET_VERSION,
        "dataset_version": None,
        "label_schema_version": LABEL_SCHEMA_VERSION,
        "baseline_version": None,
        "model_version": None,
        "source_snapshot_id": SOURCE_ID,
        "source_snapshot_accessed_at_utc": source["accessed_at_utc"],
        "input_hashes": input_hashes,
        "current_checkpoint": {
            "label_qa_report_id": label_qa["report_id"],
            "label_qa_decision": label_qa["decision"],
            "binding_weakness": (
                "The accepted proposal uses one event and one exact scene pair, so it cannot yet support "
                "leakage-resistant cross-event evaluation evidence."
            ),
        },
        "rules": {
            "candidate_source": "Current MTBS all-years occurrence and burned-area boundary services",
            "county_membership": source["rules"]["county_membership_method"],
            "minimum_year": source["rules"]["minimum_year"],
            "fire_type": source["rules"]["fire_type"],
            "acre_range": [source["rules"]["minimum_acres"], source["rules"]["maximum_acres"]],
            "darlene_aoi_overlap_allowed": False,
            "selected_candidate_boundary_overlap_allowed": False,
            "single_sentinel_item_must_cover_full_mtbs_boundary": True,
            "metadata_cloud_limit_percent": CLOUD_LIMIT_PERCENT,
            "selected_candidate_count": SELECTION_COUNT,
            "selection": (
                "Select two eligible events. If more than two pass, maximize the minimum representative-point "
                "distance across Darlene and the candidate pair, then break ties by stable MTBS fire IDs."
            ),
        },
        "inventory": {
            "search_envelope_feature_count": source["mtbs"]["search_envelope_feature_count"],
            "deschutes_county_feature_count": source["mtbs"]["deschutes_county_feature_count"],
            "recent_candidate_count": len(assessments),
            "eligible_candidate_count": sum(item["eligible"] for item in assessments),
            "selected_candidate_count": len(selected),
        },
        "darlene_reference_group": {
            "event_group_id": "event-darlene3-2024",
            "geography_group_id": f"geo-darlene3-{AOI_VERSION}",
            "scene_group_id": "scene-darlene3-s2a-t10tfp-r013-20240625-20240705",
            "time_group_id": "time-2024-06-25--2024-07-05",
            "aoi_bbox_wgs84": darlene_bbox,
            "representative_point_wgs84": [round(darlene_center[0], 7), round(darlene_center[1], 7)],
            "exact_scene_ids": darlene_scene_ids,
            "role": "Current proposal evidence group; not a training, validation, or test partition.",
        },
        "candidate_assessments": assessments,
        "selected_event_group_ids": [item["event_group_id"] for item in selected],
        "separation": {
            "pairwise_representative_point_distances": pairwise,
            "selected_boundaries_overlap_each_other": selected_overlap,
            "all_selected_boundaries_nonoverlapping": len(selected) >= SELECTION_COUNT and not selected_overlap,
            "interpretation": (
                "Distance is a disclosed spatial-separation diagnostic, not proof of ecological independence. "
                "Exact event, scene, geography, and time groups are the leakage-control units."
            ),
        },
        "group_contract": {
            "status": "GROUPS_FROZEN_PARTITIONS_NOT_CREATED",
            "event_rule": "All future tiles or chips derived from one MTBS fire ID stay in one evaluation role.",
            "scene_rule": "All derivatives from either scene in one exact pre/post pair stay with that event group.",
            "geography_rule": "Overlapping AOIs or MTBS boundaries may not cross evaluation roles.",
            "time_rule": "Acquisitions from the same event window may not cross evaluation roles.",
            "partition_rule": (
                "No train/validation/test partition exists. A later checkpoint must assign whole groups, prove "
                "zero group overlap, and keep Darlene and both selected events indivisible."
            ),
        },
        "visual_review": {
            "decision": visual_review_decision,
            "notes": visual_review_notes,
            "scope": "Original-resolution PNG and live semantic HTML; metadata evidence only.",
        },
        "decision": decision,
        "decision_detail": detail,
        "quality_gates": {
            "source_snapshot_current_and_frozen": True,
            "county_membership_deterministic": True,
            "event_ids_unique": True,
            "boundaries_nonoverlapping": len(selected) >= SELECTION_COUNT and not selected_overlap,
            "exact_scene_pairs_frozen": all(item.get("scene_pair") for item in selected),
            "provider_imagery_downloaded": False,
            "label_pixels_created": 0,
            "dataset_created": False,
            "partition_created": False,
            "baseline_created": False,
            "model_created": False,
        },
        "terms": {
            "status": "RESOLVED_FOR_METADATA_FEASIBILITY_AND_SENTINEL_ACQUISITION_PLANNING",
            "census": (
                "U.S. Census TIGER technical guidance says Census government works may be reproduced and asks "
                "that the Census Bureau be cited as source."
            ),
            "mtbs": (
                "USGS public-domain guidance applies to USGS-authored material while preserving third-party "
                "exceptions; BurnLens attributes both MTBS partner agencies and makes no endorsement claim."
            ),
            "sentinel": (
                "CDSE terms state Sentinel access and use are free, full, and open subject to the Sentinel legal "
                "notice; the current STAC collection exposes that legal notice as its license link."
            ),
            "scope_limit": "Recheck exact terms before any new source family, redistribution mode, or paid service.",
        },
        "claims": {
            "permitted": [
                "Current official metadata supports exact source acquisition planning for two additional Deschutes County fire events.",
                "The event, scene, geography, and time groups are frozen before any future tiling or partitioning.",
                "MTBS is analyst-interpreted cross-fire reference evidence and Sentinel STAC metadata is availability evidence.",
            ],
            "prohibited": [
                "No selected Sentinel product has been downloaded or inspected for local pixel fitness in this checkpoint.",
                "No MTBS boundary is field truth or an automatic burned-pixel label.",
                "No dataset, train/validation/test split, baseline, model, accuracy, or generalization claim exists.",
                "No official, endorsed, operational, emergency-ready, or field-validated status is implied.",
            ],
        },
        "limitations": [
            "Sentinel product cloud cover is tile-level catalogue metadata, not local cloud, smoke, shadow, snow, or valid-pixel QA over each fire boundary.",
            "MTBS boundaries and severity products are analyst-interpreted remotely sensed reference evidence and may be revised in later quarterly releases.",
            "Representative-point distance does not prove ecological independence or eliminate spatial autocorrelation.",
            "County membership uses the MTBS representative point; selected fire boundaries may cross jurisdiction lines.",
            "Metadata availability does not prove authenticated download success, archive integrity, local registration, label fitness, or model generalization.",
            "The current label proposal and its QA were produced by the same Codex director and have no independent human inter-rater validation.",
        ],
        "source_guidance": source["source_guidance"],
        "attribution": (
            "MTBS: Monitoring Trends in Burn Severity program, jointly administered by the U.S. Geological "
            "Survey and USDA Forest Service. County geometry: U.S. Census Bureau TIGERweb. Sentinel-2 metadata: "
            "Copernicus Data Space Ecosystem / European Union Copernicus programme. No endorsement implied."
        ),
        "source_precedence": (
            "Official emergency and incident sources govern public-safety decisions. Within this experiment, "
            "frozen exact source bytes and provider metadata govern derived evidence; MTBS remains cross-fire "
            "reference, not automatic truth."
        ),
        "phase_comparison": {
            "phase_two_objective_four": (
                "Improves reproducibility and model-readiness evidence by proving candidate event groups before "
                "source acquisition; it does not yet prove a versioned dataset or leakage-resistant partition."
            ),
            "phase_two_objective_five": (
                "Makes a future baseline comparison more credible by freezing independent evaluation units; no "
                "baseline or model exists yet."
            ),
            "portfolio_narrative": (
                "Shows disciplined restraint: BurnLens exposes one-event risk and sources the next two events "
                "before claiming dataset breadth or generalization."
            ),
        },
        "warning": WARNING,
    }


def _wrapped_lines(draw: ImageDraw.ImageDraw, text: str, width: int, size: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if current and draw.textbbox((0, 0), candidate, font=_font(size))[2] > width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def _draw_wrapped(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    *,
    width: int,
    size: int,
    fill: str,
    max_lines: int,
    line_height: int,
) -> None:
    for index, line in enumerate(_wrapped_lines(draw, text, width, size)[:max_lines]):
        draw.text((xy[0], xy[1] + index * line_height), line, fill=fill, font=_font(size))


def _geometry_lines(geometry: dict[str, Any] | None) -> list[list[list[float]]]:
    if not geometry:
        return []
    if geometry.get("type") == "Polygon":
        return geometry.get("coordinates") or []
    if geometry.get("type") == "MultiPolygon":
        return [ring for polygon in geometry.get("coordinates") or [] for ring in polygon]
    return []


def render_png(report: dict[str, Any], path: Path) -> None:
    width, height = 1800, 1250
    canvas = Image.new("RGB", (width, height), "#f4f0e8")
    draw = ImageDraw.Draw(canvas)
    ink, muted, teal, orange, panel = "#15211d", "#5d6b64", "#006b64", "#f05a28", "#fffdf8"
    draw.rectangle((0, 0, width, 190), fill="#132a26")
    draw.text((70, 36), "BURNLENS  /  CROSS-EVENT EVIDENCE", fill="#b9d8cf", font=_font(22))
    draw.text((70, 80), "LEAKAGE GROUPS FROZEN BEFORE ACQUISITION", fill="white", font=_font(38))
    draw.text((70, 138), report["decision"], fill="#ffd166", font=_font(23))
    draw.text((1410, 48), "SOURCE", fill="#b9d8cf", font=_font(18))
    draw.text((1410, 82), report["source_snapshot_id"], fill="white", font=_font(18))
    draw.text((1410, 122), "imagery: 0 bytes", fill="#ffd166", font=_font(19))

    map_box = (60, 235, 1115, 885)
    draw.rounded_rectangle(map_box, radius=22, fill=panel, outline="#d7d0c4", width=2)
    draw.text((90, 263), "DESCHUTES EVENT SEPARATION / WGS 84", fill=teal, font=_font(21))
    bounds = report["rules"].get("search_envelope_wgs84")
    if bounds is None:
        all_boxes = [report["darlene_reference_group"]["aoi_bbox_wgs84"]] + [
            item["boundary_bbox_wgs84"]
            for item in report["candidate_assessments"]
            if len(item["boundary_bbox_wgs84"]) == 4
        ]
        bounds = [
            min(item[0] for item in all_boxes) - 0.05,
            min(item[1] for item in all_boxes) - 0.05,
            max(item[2] for item in all_boxes) + 0.05,
            max(item[3] for item in all_boxes) + 0.05,
        ]
    west, south, east, north = bounds
    plot = (100, 315, 1075, 835)

    def project(point: list[float] | tuple[float, float]) -> tuple[int, int]:
        x = plot[0] + (float(point[0]) - west) / (east - west) * (plot[2] - plot[0])
        y = plot[3] - (float(point[1]) - south) / (north - south) * (plot[3] - plot[1])
        return int(round(x)), int(round(y))

    for fraction in (0.0, 0.25, 0.5, 0.75, 1.0):
        x = int(plot[0] + fraction * (plot[2] - plot[0]))
        y = int(plot[1] + fraction * (plot[3] - plot[1]))
        draw.line((x, plot[1], x, plot[3]), fill="#e5dfd3", width=1)
        draw.line((plot[0], y, plot[2], y), fill="#e5dfd3", width=1)
    draw.rectangle(plot, outline="#b8b0a3", width=2)
    dbox = report["darlene_reference_group"]["aoi_bbox_wgs84"]
    dfirst, dsecond = project((dbox[0], dbox[3])), project((dbox[2], dbox[1]))
    draw.rectangle((*dfirst, *dsecond), outline=orange, width=5)
    dcenter = project(report["darlene_reference_group"]["representative_point_wgs84"])
    draw.ellipse((dcenter[0] - 8, dcenter[1] - 8, dcenter[0] + 8, dcenter[1] + 8), fill=orange)
    draw.text((dcenter[0] + 12, dcenter[1] - 22), "Darlene 3 / current", fill=orange, font=_font(17))
    for item in report["candidate_assessments"]:
        selected = item["disposition"] == "SELECTED_FOR_EXACT_SOURCE_ACQUISITION"
        color = teal if selected else "#87918c"
        for ring in _geometry_lines(item.get("source_geometry")):
            points = [project(point) for point in ring]
            if len(points) > 1:
                draw.line(points, fill=color, width=4 if selected else 2, joint="curve")
        point = project(item["representative_point_wgs84"])
        draw.ellipse((point[0] - 7, point[1] - 7, point[0] + 7, point[1] + 7), fill=color)
        label = f"{item['fire_name']} / {'SELECT' if selected else 'EXCLUDE'}"
        draw.text((point[0] + 11, point[1] - 20), label, fill=color, font=_font(16))
    draw.text((100, 852), "Orange = current Darlene AOI. Teal = selected exact-source candidate. Gray = disclosed exclusion.", fill=muted, font=_font(16))

    selected = [
        item for item in report["candidate_assessments"]
        if item["disposition"] == "SELECTED_FOR_EXACT_SOURCE_ACQUISITION"
    ]
    cards = [
        (
            "CURRENT WEAKNESS",
            "One event cannot prove split integrity",
            report["current_checkpoint"]["binding_weakness"],
            orange,
        ),
        *[
            (
                f"SELECTED / {item['fire_name']}",
                f"{item['year']}  /  {item['acres']:,.0f} acres  /  {item['distance_from_darlene_center_km']:.1f} km",
                f"{item['scene_pair']['scene_group']['platform']} {item['scene_pair']['scene_group']['grid_code']} orbit {item['scene_pair']['scene_group']['relative_orbit']}; {item['scene_pair']['post_window'].replace('_', ' ')}.",
                teal,
            )
            for item in selected
        ],
    ]
    for index, (eyebrow, title, body, accent) in enumerate(cards):
        top = 235 + index * 215
        draw.rounded_rectangle((1160, top, 1740, top + 185), radius=20, fill=panel, outline="#d7d0c4", width=2)
        draw.rectangle((1160, top, 1168, top + 185), fill=accent)
        draw.text((1192, top + 22), eyebrow, fill=accent, font=_font(17))
        _draw_wrapped(draw, (1192, top + 55), title, width=505, size=24, fill=ink, max_lines=2, line_height=31)
        _draw_wrapped(draw, (1192, top + 112), body, width=505, size=17, fill=muted, max_lines=3, line_height=24)

    draw.rounded_rectangle((60, 925, 1740, 1118), radius=22, fill="#e6efeb", outline="#b8cbc3", width=2)
    draw.text((90, 953), "FROZEN GROUP CONTRACT / PARTITIONS STILL DO NOT EXIST", fill=teal, font=_font(21))
    _draw_wrapped(draw, (90, 994), report["group_contract"]["partition_rule"], width=1560, size=19, fill=ink, max_lines=3, line_height=28)
    trace = (
        f"run {report['run_id']}  /  commit {report['git_source_commit'][:12]}  /  software {report['software_version']}  /  "
        f"label schema {report['label_schema_version']}  /  app none  /  dataset none  /  baseline none  /  model none"
    )
    _draw_wrapped(draw, (90, 1080), trace, width=1560, size=16, fill=muted, max_lines=2, line_height=23)
    draw.rectangle((0, 1170, width, height), fill="#132a26")
    _draw_wrapped(draw, (55, 1193), report["warning"], width=1690, size=17, fill="white", max_lines=2, line_height=25)
    canvas.save(path, format="PNG", optimize=False)


def render_html(report: dict[str, Any], png_name: str, path: Path) -> None:
    rows = []
    for item in report["candidate_assessments"]:
        pair = item.get("scene_pair")
        scene = "None"
        if pair:
            scene = (
                f"<code>{escape(pair['pre_scene']['id'])}</code><br>"
                f"<code>{escape(pair['post_scene']['id'])}</code>"
            )
        rows.append(
            "<tr>"
            f"<td>{escape(str(item['fire_name']))}<br><code>{escape(str(item['fire_id']))}</code></td>"
            f"<td>{item['year']}<br>{item['acres']:,.0f} acres</td>"
            f"<td>{item['distance_from_darlene_center_km']:.3f} km</td>"
            f"<td>{scene}</td>"
            f"<td><strong>{escape(item['disposition'])}</strong><br>{escape('; '.join(item['reasons']))}</td>"
            "</tr>"
        )
    distances = "".join(
        f"<li><code>{escape(item['first_event_group_id'])}</code> to <code>{escape(item['second_event_group_id'])}</code>: {item['representative_point_distance_km']:.3f} km</li>"
        for item in report["separation"]["pairwise_representative_point_distances"]
    )
    permitted = "".join(f"<li>{escape(item)}</li>" for item in report["claims"]["permitted"])
    prohibited = "".join(f"<li>{escape(item)}</li>" for item in report["claims"]["prohibited"])
    limitations = "".join(f"<li>{escape(item)}</li>" for item in report["limitations"])
    sources = "".join(
        f'<li><a href="{escape(item["url"])}">{escape(item["organization"])}</a> — {escape(item["role"])}</li>'
        for item in report["source_guidance"]
    )
    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>BurnLens cross-event feasibility and leakage groups</title>
<style>
:root{{--ink:#15211d;--muted:#5d6b64;--paper:#f4f0e8;--panel:#fffdf8;--teal:#006b64;--orange:#f05a28}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 system-ui,sans-serif}}
header{{background:#132a26;color:white;padding:2.4rem max(1rem,calc((100% - 1220px)/2))}} header p{{max-width:78ch;color:#c9ddd6}}
main{{max-width:1220px;margin:auto;padding:2rem 1rem 4rem}} section,.status{{background:var(--panel);border:1px solid #d7d0c4;border-radius:14px;padding:1.25rem;margin:1rem 0}}
.status{{border-left:8px solid var(--teal)}} .grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1rem}}
.metric{{display:block;color:var(--teal);font-size:2rem;font-weight:760}} img{{display:block;width:100%;height:auto;border:1px solid #d7d0c4;border-radius:14px}}
table{{width:100%;border-collapse:collapse}} th,td{{padding:.7rem;text-align:left;vertical-align:top;border-bottom:1px solid #ddd5c8}} th{{background:#e6efeb}}
code{{overflow-wrap:anywhere}} a{{color:var(--teal)}} dt{{font-weight:750;margin-top:.7rem}} dd{{margin-left:0;color:var(--muted)}}
.warning{{background:#132a26;color:white;padding:1rem;border-radius:10px;font-weight:650}} .no{{color:var(--orange);font-weight:760}} caption{{text-align:left;font-weight:750;margin-bottom:.6rem}}
</style></head><body>
<header><h1>Cross-event groups are feasible—and frozen before acquisition</h1><p>BurnLens starts from the accepted Darlene 3 label-proposal checkpoint, exposes its one-event limitation, and selects only source identities that current official metadata can support. No provider imagery, labels, dataset, partition, baseline, or model is created here.</p></header>
<main>
<div class="status"><h2>{escape(report['decision'])}</h2><p>{escape(report['decision_detail'])}</p><p><strong>Visual review:</strong> {escape(report['visual_review']['decision'])} — {escape(report['visual_review']['notes'])}</p></div>
<div class="grid"><section><span class="metric">{report['inventory']['deschutes_county_feature_count']}</span>MTBS occurrences with representative points in Deschutes County</section><section><span class="metric">{report['inventory']['eligible_candidate_count']}</span>metadata-feasible independent candidates</section><section><span class="metric">0 bytes</span>provider imagery acquired in this checkpoint</section></div>
<figure><img src="{escape(png_name)}" width="1800" height="1250" alt="BurnLens map and evidence cards showing Darlene 3, selected Tepee and McKay cross-event candidates, and excluded Milli"><figcaption>Report <code>{escape(report['report_id'])}</code>; run <code>{escape(report['run_id'])}</code>; source commit <code>{escape(report['git_source_commit'])}</code>.</figcaption></figure>
<section><h2>Candidate inventory and exact scene identities</h2><div style="overflow-x:auto"><table><caption>Every event passing the frozen date, type, and size screen</caption><thead><tr><th>Event</th><th>Time / size</th><th>From Darlene</th><th>Exact Sentinel pair</th><th>Disposition / reason</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div><p>Scene selection uses catalogue-level cloud metadata only. Local pixels remain uninspected.</p></section>
<section><h2>Leakage groups, not data partitions</h2><p><strong>{escape(report['group_contract']['status'])}</strong></p><dl><dt>Event</dt><dd>{escape(report['group_contract']['event_rule'])}</dd><dt>Scene</dt><dd>{escape(report['group_contract']['scene_rule'])}</dd><dt>Geography</dt><dd>{escape(report['group_contract']['geography_rule'])}</dd><dt>Time</dt><dd>{escape(report['group_contract']['time_rule'])}</dd><dt>Partition gate</dt><dd>{escape(report['group_contract']['partition_rule'])}</dd></dl><ul>{distances}</ul><p>{escape(report['separation']['interpretation'])}</p></section>
<section><h2>Terms and source roles</h2><p><strong>{escape(report['terms']['status'])}</strong></p><dl><dt>Census TIGER</dt><dd>{escape(report['terms']['census'])}</dd><dt>MTBS</dt><dd>{escape(report['terms']['mtbs'])}</dd><dt>Copernicus Sentinel</dt><dd>{escape(report['terms']['sentinel'])}</dd></dl><p>{escape(report['attribution'])}</p><ul>{sources}</ul></section>
<div class="grid"><section><h2>Permitted claims</h2><ul>{permitted}</ul></section><section><h2>Prohibited claims</h2><ul>{prohibited}</ul></section></div>
<section><h2>Limitations that remain binding</h2><ul>{limitations}</ul></section>
<section><h2>Phase and portfolio comparison</h2><dl><dt>Phase Two Objective Four</dt><dd>{escape(report['phase_comparison']['phase_two_objective_four'])}</dd><dt>Phase Two Objective Five</dt><dd>{escape(report['phase_comparison']['phase_two_objective_five'])}</dd><dt>Portfolio narrative</dt><dd>{escape(report['phase_comparison']['portfolio_narrative'])}</dd></dl></section>
<section><h2>Traceability</h2><dl><dt>Repository / issue</dt><dd>{escape(report['repository'])} / #{report['task_issue']}</dd><dt>Source snapshot</dt><dd><code>{escape(report['source_snapshot_id'])}</code>, accessed {escape(report['source_snapshot_accessed_at_utc'])}</dd><dt>Software / target / AOI / label schema</dt><dd>{escape(report['software_version'])} / <code>{escape(report['target_version'])}</code> / <code>{escape(report['aoi_version'])}</code> / <code>{escape(report['label_schema_version'])}</code></dd><dt>Application / dataset / baseline / model</dt><dd>Not created / not created / not created / not created</dd><dt>Run / source commit</dt><dd><code>{escape(report['run_id'])}</code> / <code>{escape(report['git_source_commit'])}</code></dd></dl></section>
<p>{escape(report['source_precedence'])}</p><p class="warning">{escape(report['warning'])}</p>
</main></body></html>"""
    _write_utf8_lf(path, html)


def write_report(report: dict[str, Any], output_directory: Path) -> dict[str, Path]:
    output_directory.mkdir(parents=True, exist_ok=True)
    paths = {
        "json": output_directory / f"{REPORT_ID}.json",
        "html": output_directory / f"{REPORT_ID}.html",
        "png": output_directory / f"{REPORT_ID}.png",
    }
    render_png(report, paths["png"])
    report["rendered_outputs"] = {
        "json": paths["json"].name,
        "html": paths["html"].name,
        "png": paths["png"].name,
        "png_sha256": _sha256(paths["png"]),
    }
    _write_utf8_lf(paths["json"], json.dumps(report, indent=2) + "\n")
    render_html(report, paths["png"].name, paths["html"])
    return paths


def run_cross_event_feasibility(
    *,
    source_snapshot_path: Path,
    aoi_report_path: Path,
    optical_report_path: Path,
    label_qa_report_path: Path,
    output_directory: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
    visual_review_decision: str,
    visual_review_notes: str,
) -> dict[str, Path]:
    source = _read_json(source_snapshot_path)
    aoi = _read_json(aoi_report_path)
    optical = _read_json(optical_report_path)
    label_qa = _read_json(label_qa_report_path)
    input_hashes = {
        "source_snapshot_sha256": _sha256_lf_text(source_snapshot_path),
        "aoi_report_sha256": _sha256_lf_text(aoi_report_path),
        "optical_report_sha256": _sha256_lf_text(optical_report_path),
        "label_qa_report_sha256": _sha256_lf_text(label_qa_report_path),
    }
    report = build_report(
        source=source,
        aoi=aoi,
        optical=optical,
        label_qa=label_qa,
        input_hashes=input_hashes,
        generated_at_utc=generated_at_utc,
        run_id=run_id,
        git_source_commit=git_source_commit,
        visual_review_decision=visual_review_decision,
        visual_review_notes=visual_review_notes,
    )
    report["rules"]["search_envelope_wgs84"] = source["rules"]["search_envelope_wgs84"]
    return write_report(report, output_directory)
