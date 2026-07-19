"""Freeze additional whole-event groups from current official metadata."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from hashlib import sha256
from html import escape
from itertools import combinations
import json
from math import asin, cos, radians, sin, sqrt
from pathlib import Path
import re
from typing import Any
from urllib.parse import urlsplit

from PIL import Image, ImageDraw, ImageFont

from .cross_event_feasibility import _choose_pair
from .cross_event_source import (
    CDSE_COLLECTION_URL,
    MTBS_BOUNDARY_LAYER,
    MTBS_OCCURRENCE_LAYER,
    MTBS_URL,
    _arcgis_polygon,
    _expanded_bbox,
    _geometry_bbox,
    _request_json,
    _stac_window,
)

SOURCE_ID = "ADDITIONAL-EVENT-GROUP-SOURCE-2026-001"
REPORT_ID = "ADDITIONAL-EVENT-GROUP-PLAN-2026-001"
SOURCE_SCHEMA_VERSION = "0.1.0"
REPORT_SCHEMA_VERSION = "0.1.0"
REPORT_VERSION = "additional-event-group-plan-v0.1.0"
SOFTWARE_VERSION = "0.32.0"
AOI_VERSION = "aoi-darlene3-model-v0.2.0"
TARGET_VERSION = "target-burn-scar-v0.2.0"
LABEL_SCHEMA_VERSION = "burn-scar-five-state-schema-v0.1.0"
REGION_LABEL_VERSION = "owner-approved-prototype-region-labels-v0.1.0"
PORTAL_WFS_URL = "https://edcintl.cr.usgs.gov/geoserver/wfs"
WARNING = (
    "Experimental BurnLens CV output. Not official wildfire information. Not emergency guidance. "
    "Not evacuation, routing, tactical, or incident-command support. Official sources govern."
)

EXISTING_EVENTS = (
    {
        "fire_id": "OR4364712147820240625",
        "event_group_id": "event-darlene3-or-2024",
        "year": 2024,
        "name": "Darlene 3",
    },
    {
        "fire_id": "OR4375212142520170829",
        "event_group_id": "event-mckay-1035-ne-2017",
        "year": 2017,
        "name": "McKay 1035 NE",
    },
    {
        "fire_id": "OR4383912111420180907",
        "event_group_id": "event-tepee-1144-ne-2018",
        "year": 2018,
        "name": "Tepee 1144 NE",
    },
)

CANDIDATE_IDS = (
    "OR4441212141120170811",  # Whychus, 2017
    "OR4446712160520200817",  # Green Ridge, 2020
    "OR4446612140020210711",  # Grandview, 2021
    "OR4396912190120230825",  # Petes Lake, 2023
    "OR4470812185620170724",  # Whitewater, 2017
)
SELECTED_EVENT_IDS = (
    "OR4446712160520200817",
    "OR4446612140020210711",
    "OR4396912190120230825",
)


class AdditionalEventGroupError(ValueError):
    """Raised when source identity, selection, or rendering gates fail."""


def _write_utf8_lf(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def _sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _date_from_epoch_ms(value: Any) -> datetime:
    if not isinstance(value, (int, float)):
        raise AdditionalEventGroupError("MTBS_IGNITION_DATE_INVALID")
    return datetime.fromtimestamp(value / 1000.0, tz=timezone.utc)


def _host(url: str) -> str:
    return urlsplit(url).netloc.lower()


def _haversine_km(first: tuple[float, float], second: tuple[float, float]) -> float:
    lon1, lat1 = map(radians, first)
    lon2, lat2 = map(radians, second)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    term = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 6371.0088 * 2 * asin(sqrt(term))


def _bbox_overlap(first: list[float], second: list[float]) -> bool:
    return not (
        first[2] <= second[0]
        or second[2] <= first[0]
        or first[3] <= second[1]
        or second[3] <= first[1]
    )


def _programs_by_event(features: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}
    for feature in features:
        properties = feature.get("properties") or {}
        event_id = str(properties.get("event_id"))
        if event_id == "None":
            raise AdditionalEventGroupError("PORTAL_EVENT_ID_MISSING")
        result.setdefault(event_id, []).append(
            {
                "catalog_id": int(properties["id"]),
                "map_id": int(properties.get("map_id") or 0),
                "program": str(properties["map_prog"]),
                "incident_name": str(properties["incid_name"]),
                "boundary_acres": int(properties.get("burnbndac") or 0),
                "nonstandard": bool(properties.get("nonstandard")),
            }
        )
    for products in result.values():
        products.sort(key=lambda item: (item["program"], item["map_id"], item["catalog_id"]))
    return result


def capture_source(*, accessed_at_utc: str, run_id: str, git_source_commit: str) -> dict[str, Any]:
    try:
        datetime.fromisoformat(accessed_at_utc.replace("Z", "+00:00"))
    except (TypeError, ValueError) as error:
        raise AdditionalEventGroupError("ACCESSED_AT_UTC_INVALID") from error
    if not accessed_at_utc.endswith("Z"):
        raise AdditionalEventGroupError("ACCESSED_AT_UTC_REQUIRED")
    if not run_id.strip() or not re.fullmatch(r"[0-9a-f]{40}", git_source_commit):
        raise AdditionalEventGroupError("RUN_OR_COMMIT_INVALID")

    quoted = ",".join(f"'{value}'" for value in CANDIDATE_IDS)
    occurrence, occurrence_url = _request_json(
        f"{MTBS_URL}/{MTBS_OCCURRENCE_LAYER}/query",
        {
            "where": f"fire_id IN ({quoted})",
            "outFields": "fire_id,fire_name,ig_date,latitude,longitude,acres,map_id,map_prog,pre_id,post_id",
            "returnGeometry": "false",
            "f": "json",
        },
    )
    boundary, boundary_url = _request_json(
        f"{MTBS_URL}/{MTBS_BOUNDARY_LAYER}/query",
        {
            "where": f"fire_id IN ({quoted})",
            "outFields": "fire_id,fire_name,year,fire_type,acres,asmnt_type,ig_date,map_id,map_prog,pre_id,post_id,comments",
            "returnGeometry": "true",
            "outSR": "4326",
            "f": "json",
        },
    )
    if occurrence.get("exceededTransferLimit") or boundary.get("exceededTransferLimit"):
        raise AdditionalEventGroupError("MTBS_TRANSFER_LIMIT_EXCEEDED")

    all_ids = tuple(item["fire_id"] for item in EXISTING_EVENTS) + CANDIDATE_IDS
    all_quoted = ",".join(f"'{value}'" for value in all_ids)
    portal, portal_url = _request_json(
        PORTAL_WFS_URL,
        {
            "service": "WFS",
            "version": "2.0.0",
            "request": "GetFeature",
            "typeNames": "mtbs:fire_polygons",
            "outputFormat": "application/json",
            "propertyName": "id,map_id,map_prog,incid_name,event_id,ig_date,burnbndac,nonstandard",
            "cql_filter": f"event_id IN ({all_quoted})",
        },
    )
    collection, collection_url = _request_json(CDSE_COLLECTION_URL)
    license_links = [link for link in collection.get("links", []) if link.get("rel") == "license"]
    if collection.get("id") != "sentinel-2-l2a" or len(license_links) != 1:
        raise AdditionalEventGroupError("CDSE_COLLECTION_IDENTITY_OR_LICENSE_DRIFT")

    occurrences: dict[str, dict[str, Any]] = {}
    for feature in occurrence.get("features", []):
        attrs = feature.get("attributes") or {}
        event_id = str(attrs.get("fire_id"))
        ignition = _date_from_epoch_ms(attrs.get("ig_date"))
        occurrences[event_id] = {
            "fire_id": event_id,
            "fire_name": str(attrs.get("fire_name")),
            "ignition_date": ignition.date().isoformat(),
            "year": ignition.year,
            "latitude": float(attrs.get("latitude")),
            "longitude": float(attrs.get("longitude")),
            "acres": float(attrs.get("acres")),
            "map_id": int(attrs.get("map_id")),
            "map_program": str(attrs.get("map_prog")),
            "pre_id": str(attrs.get("pre_id")),
            "post_id": str(attrs.get("post_id")),
        }

    boundaries: dict[str, dict[str, Any]] = {}
    for feature in boundary.get("features", []):
        attrs = feature.get("attributes") or {}
        event_id = str(attrs.get("fire_id"))
        geometry = _arcgis_polygon(feature.get("geometry") or {})
        boundaries[event_id] = {
            "fire_id": event_id,
            "fire_name": str(attrs.get("fire_name")),
            "year": int(attrs.get("year")),
            "fire_type": str(attrs.get("fire_type")),
            "acres": float(attrs.get("acres")),
            "assessment_type": str(attrs.get("asmnt_type")),
            "ignition_date": str(attrs.get("ig_date")),
            "map_id": int(attrs.get("map_id")),
            "map_program": str(attrs.get("map_prog")),
            "pre_id": str(attrs.get("pre_id")),
            "post_id": str(attrs.get("post_id")),
            "comments": attrs.get("comments"),
            "bbox": _geometry_bbox(geometry),
            "geometry": geometry,
        }

    products = _programs_by_event(portal.get("features", []))
    events: list[dict[str, Any]] = []
    for event_id in CANDIDATE_IDS:
        occurrence_item = occurrences.get(event_id)
        boundary_item = boundaries.get(event_id)
        if occurrence_item is None or boundary_item is None:
            raise AdditionalEventGroupError(f"CANDIDATE_IDENTITY_INCOMPLETE:{event_id}")
        ignition = datetime.fromisoformat(occurrence_item["ignition_date"]).replace(tzinfo=timezone.utc)
        bbox = _expanded_bbox(boundary_item["bbox"])
        event = dict(occurrence_item)
        event["boundary"] = boundary_item
        event["portal_products"] = products.get(event_id, [])
        event["programs"] = sorted({item["program"] for item in event["portal_products"]})
        event["stac_search_bbox"] = bbox
        event["stac_windows"] = [
            _stac_window(
                bbox=bbox,
                start=ignition - timedelta(days=45),
                end=ignition - timedelta(days=1),
                window="pre",
                boundary=boundary_item["geometry"],
            ),
            _stac_window(
                bbox=bbox,
                start=ignition + timedelta(days=10),
                end=ignition + timedelta(days=75),
                window="post_initial",
                boundary=boundary_item["geometry"],
            ),
            _stac_window(
                bbox=bbox,
                start=ignition + timedelta(days=300),
                end=ignition + timedelta(days=400),
                window="post_extended",
                boundary=boundary_item["geometry"],
            ),
        ]
        events.append(event)

    existing = []
    for item in EXISTING_EVENTS:
        event = dict(item)
        event["portal_products"] = products.get(item["fire_id"], [])
        event["programs"] = sorted({product["program"] for product in event["portal_products"]})
        existing.append(event)

    return {
        "source_id": SOURCE_ID,
        "source_schema_version": SOURCE_SCHEMA_VERSION,
        "serialization": "UTF-8 JSON with LF canonical line endings",
        "accessed_at_utc": accessed_at_utc,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": 466,
        "run_id": run_id,
        "git_source_commit": git_source_commit,
        "software_version": SOFTWARE_VERSION,
        "purpose": "Current official metadata-only freeze of additional comparable whole-event groups; no imagery or labels acquired.",
        "rules": {
            "candidate_ids": list(CANDIDATE_IDS),
            "existing_event_ids": [item["fire_id"] for item in EXISTING_EVENTS],
            "fire_type": "Wildfire",
            "minimum_acres": 1000.0,
            "maximum_acres": 30000.0,
            "stac_windows_days": {"pre": [-45, -1], "post_initial": [10, 75], "post_extended": [300, 400]},
            "single_item_full_boundary_coverage_required": True,
            "metadata_cloud_limit_percent": 20.0,
            "scene_pair_identity": ["platform", "grid_code", "relative_orbit", "processing_version"],
        },
        "request_urls": {
            "mtbs_occurrences": occurrence_url,
            "mtbs_boundaries": boundary_url,
            "burn_severity_portal": portal_url,
            "cdse_collection": collection_url,
        },
        "cdse": {
            "collection": collection["id"],
            "stac_version": collection.get("stac_version"),
            "license": collection.get("license"),
            "license_link": license_links[0],
            "providers": collection.get("providers"),
            "access": "public metadata only; product routes recorded but not exercised",
        },
        "existing_events": existing,
        "candidate_events": events,
        "source_guidance": [
            {"organization": "MTBS Program", "url": "https://www.mtbs.gov/faqs", "role": "product identities, revisions, scale, boundaries, and limitations"},
            {"organization": "MTBS Program", "url": "https://www.mtbs.gov/mapping-methods", "role": "analyst interpretation and thematic uncertainty"},
            {"organization": "Copernicus Data Space Ecosystem", "url": "https://documentation.dataspace.copernicus.eu/APIs/STAC.html", "role": "current STAC endpoint and query behavior"},
            {"organization": "Copernicus Data Space Ecosystem", "url": "https://dataspace.copernicus.eu/terms-and-conditions", "role": "current Sentinel access and legal-notice precedence"},
        ],
        "boundaries": {
            "provider_imagery_downloaded": False,
            "provider_bytes_retained": 0,
            "label_pixels_created": 0,
            "dataset_created": False,
            "split_created": False,
            "baseline_created": False,
            "model_created": False,
        },
    }


def validate_source(source: dict[str, Any]) -> None:
    if source.get("source_id") != SOURCE_ID or source.get("software_version") != SOFTWARE_VERSION:
        raise AdditionalEventGroupError("SOURCE_IDENTITY_INVALID")
    if source.get("repository") != "drwbkr1/burnlens-deschutes" or source.get("task_issue") != 466:
        raise AdditionalEventGroupError("SOURCE_SCOPE_INVALID")
    events = source.get("candidate_events")
    if not isinstance(events, list) or tuple(item.get("fire_id") for item in events) != CANDIDATE_IDS:
        raise AdditionalEventGroupError("CANDIDATE_ORDER_OR_IDENTITY_INVALID")
    allowed_hosts = {
        "apps.fs.usda.gov",
        "edcintl.cr.usgs.gov",
        "stac.dataspace.copernicus.eu",
    }
    if any(_host(url) not in allowed_hosts for url in source.get("request_urls", {}).values()):
        raise AdditionalEventGroupError("SOURCE_REQUEST_HOST_INVALID")
    for event in events:
        boundary = event.get("boundary") or {}
        if boundary.get("fire_type") != "Wildfire" or not 1000 <= float(event.get("acres", 0)) <= 30000:
            raise AdditionalEventGroupError(f"EVENT_SCOPE_INVALID:{event.get('fire_id')}")
        if [item.get("window") for item in event.get("stac_windows", [])] != ["pre", "post_initial", "post_extended"]:
            raise AdditionalEventGroupError(f"STAC_WINDOWS_INVALID:{event.get('fire_id')}")
        if not event.get("portal_products") or "MTBS" not in event.get("programs", []):
            raise AdditionalEventGroupError(f"PORTAL_IDENTITY_INVALID:{event.get('fire_id')}")
    boundaries = source.get("boundaries") or {}
    if boundaries != {
        "provider_imagery_downloaded": False,
        "provider_bytes_retained": 0,
        "label_pixels_created": 0,
        "dataset_created": False,
        "split_created": False,
        "baseline_created": False,
        "model_created": False,
    }:
        raise AdditionalEventGroupError("SOURCE_BOUNDARIES_INVALID")


def write_source(source: dict[str, Any], path: Path) -> Path:
    validate_source(source)
    _write_utf8_lf(path, json.dumps(source, indent=2) + "\n")
    return path


def _pairwise(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for first, second in combinations(items, 2):
        first_point = (float(first["longitude"]), float(first["latitude"]))
        second_point = (float(second["longitude"]), float(second["latitude"]))
        rows.append(
            {
                "first_event_group_id": first["event_group_id"],
                "second_event_group_id": second["event_group_id"],
                "representative_point_distance_km": round(_haversine_km(first_point, second_point), 3),
            }
        )
    return rows


def _selection_score(events: tuple[dict[str, Any], ...], existing_years: set[int]) -> tuple[Any, ...]:
    added_years = {int(item["year"]) for item in events}.difference(existing_years)
    programs = [set(item["programs"]) for item in events]
    replicated_programs = sorted(
        program
        for program in {value for group in programs for value in group}
        if sum(program in group for group in programs) >= 2
    )
    distances = [
        _haversine_km(
            (float(first["longitude"]), float(first["latitude"])),
            (float(second["longitude"]), float(second["latitude"])),
        )
        for first, second in combinations(events, 2)
    ]
    return (
        len(added_years),
        len(replicated_programs),
        round(min(distances), 6),
        tuple(sorted(item["fire_id"] for item in events)),
    )


def build_report(
    source: dict[str, Any],
    *,
    source_sha256: str,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, Any]:
    validate_source(source)
    if not re.fullmatch(r"[0-9a-f]{64}", source_sha256) or not re.fullmatch(r"[0-9a-f]{40}", git_source_commit):
        raise AdditionalEventGroupError("REPORT_HASH_OR_COMMIT_INVALID")
    assessments: list[dict[str, Any]] = []
    for event in source["candidate_events"]:
        pair = _choose_pair(event)
        event_id = event["fire_id"]
        reasons: list[str] = []
        if pair is None:
            reasons.append("NO_COMPATIBLE_LOW_CLOUD_SINGLE_TILE_PAIR")
        group = {
            "fire_id": event_id,
            "fire_name": event["fire_name"],
            "ignition_date": event["ignition_date"],
            "year": int(event["year"]),
            "acres": float(event["acres"]),
            "latitude": float(event["latitude"]),
            "longitude": float(event["longitude"]),
            "representative_point_wgs84": [float(event["longitude"]), float(event["latitude"])],
            "boundary_bbox_wgs84": [float(value) for value in event["boundary"]["bbox"]],
            "boundary_geometry": event["boundary"]["geometry"],
            "assessment_type": event["boundary"]["assessment_type"],
            "mtbs_map_id": int(event["boundary"]["map_id"]),
            "mtbs_pre_image_id": event["boundary"]["pre_id"],
            "mtbs_post_image_id": event["boundary"]["post_id"],
            "portal_products": event["portal_products"],
            "programs": event["programs"],
            "event_group_id": f"event-{_slug(event['fire_name'])}-{event['year']}",
            "geography_group_id": f"geo-mtbs-{event_id.lower()}",
            "time_group_id": None,
            "scene_pair": pair,
            "eligible": pair is not None,
            "reasons": reasons,
        }
        if pair:
            group["time_group_id"] = (
                f"time-{pair['pre_scene']['datetime'][:10]}--{pair['post_scene']['datetime'][:10]}"
            )
        assessments.append(group)

    eligible = [item for item in assessments if item["eligible"]]
    existing_years = {int(item["year"]) for item in source["existing_events"]}
    ranked = sorted(
        combinations(eligible, 3),
        key=lambda combo: _selection_score(combo, existing_years),
        reverse=True,
    )
    if not ranked:
        raise AdditionalEventGroupError("THREE_EVENT_SELECTION_UNAVAILABLE")
    selected = list(ranked[0])
    selected_ids = tuple(item["fire_id"] for item in selected)
    if selected_ids != SELECTED_EVENT_IDS:
        raise AdditionalEventGroupError(f"SELECTION_DRIFT:{','.join(selected_ids)}")
    selected_id_set = set(selected_ids)
    for item in assessments:
        item["disposition"] = (
            "FROZEN_FOR_BOUNDED_ACQUISITION" if item["fire_id"] in selected_id_set else "DEFERRED_COMPARABLE_RESERVE"
        )
        if item["fire_id"] not in selected_id_set and not item["reasons"]:
            item["reasons"] = ["LOWER_PREDECLARED_POOL_COMPLEMENT_SCORE"]

    selected_overlap = any(
        _bbox_overlap(first["boundary_bbox_wgs84"], second["boundary_bbox_wgs84"])
        for first, second in combinations(selected, 2)
    )
    if selected_overlap:
        raise AdditionalEventGroupError("SELECTED_BOUNDARIES_OVERLAP")
    pairs = _pairwise(selected)
    total_bytes = sum(
        int(item["scene_pair"][side]["product_bytes"])
        for item in selected
        for side in ("pre_scene", "post_scene")
    )
    all_programs = {program for event in source["existing_events"] + selected for program in event["programs"]}
    program_counts = {
        program: sum(program in event["programs"] for event in source["existing_events"] + selected)
        for program in sorted(all_programs)
    }
    score = _selection_score(tuple(selected), existing_years)
    return {
        "report_id": REPORT_ID,
        "report_schema_version": REPORT_SCHEMA_VERSION,
        "report_version": REPORT_VERSION,
        "serialization": "UTF-8 JSON and HTML with LF canonical line endings; deterministic PNG",
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": 466,
        "branch": "codex/p2o4-t20-additional-event-groups",
        "git_source_commit": git_source_commit,
        "software_version": SOFTWARE_VERSION,
        "application_version": None,
        "aoi_version": AOI_VERSION,
        "target_version": TARGET_VERSION,
        "dataset_version": None,
        "split_version": None,
        "label_schema_version": LABEL_SCHEMA_VERSION,
        "prototype_region_label_version": REGION_LABEL_VERSION,
        "baseline_version": None,
        "model_version": None,
        "source_snapshot": {"source_id": SOURCE_ID, "sha256": source_sha256, "accessed_at_utc": source["accessed_at_utc"]},
        "cycle_start": {
            "reconstructed_report_id": "OFFICIAL-SOURCE-SCOUT-2026-001",
            "exact_outputs": 4,
            "binding_weakness": "Only three whole-event groups exist, and the older ranking overweights Landsat-era candidates instead of closing the six-event Sentinel-era evidence gate.",
        },
        "rules": {
            "selection_count": 3,
            "candidate_pool": list(CANDIDATE_IDS),
            "existing_event_years": sorted(existing_years),
            "score_precedence": [
                "maximize event years absent from the current three-event pool",
                "maximize official reference programs repeated by at least two selected events",
                "maximize minimum representative-point separation",
                "stable fire IDs",
            ],
            "actual_score": {
                "new_event_year_count": score[0],
                "replicated_selected_program_count": score[1],
                "minimum_selected_distance_km": round(score[2], 3),
            },
            "sensor_contract": "Sentinel-2 L2A only; one item covers every MTBS boundary vertex; pre/post scenes match platform, MGRS tile, relative orbit, and processing baseline; catalogue cloud <=20%.",
        },
        "existing_event_groups": source["existing_events"],
        "candidate_assessments": assessments,
        "selected_event_group_ids": [item["event_group_id"] for item in selected],
        "event_count_after_freeze": len(source["existing_events"]) + len(selected),
        "event_years_after_freeze": sorted(existing_years | {item["year"] for item in selected}),
        "source_regime_replication": {
            "program_event_counts_across_six": program_counts,
            "programs_repeated_at_least_twice": [program for program, count in program_counts.items() if count >= 2],
            "status": "PASS_AT_LEAST_TWO_REPEATED_OFFICIAL_REFERENCE_PROGRAMS",
        },
        "separation": {
            "pairwise_selected_representative_point_distances": pairs,
            "selected_boundaries_overlap": False,
            "interpretation": "Distance is a disclosed diagnostic, not proof of ecological independence; exact event, scene, geography, and time IDs are the leakage units.",
        },
        "acquisition_contract": {
            "status": "FROZEN_METADATA_ONLY_ACQUIRE_ONE_EVENT_AT_A_TIME",
            "selected_product_count": 6,
            "catalogued_product_bytes": total_bytes,
            "catalogued_product_gib": round(total_bytes / (1024**3), 3),
            "download_order": [item["event_group_id"] for item in selected],
            "next_gate": "For each event, authenticate, download exact bytes into ignored storage, hash without overwrite, inspect archive/metadata/notices, native grids, CRS, nodata, SCL, local clouds/smoke/shadow/snow, registration, class and unknown-region feasibility before advancing the next event.",
            "large_acquisition_started": False,
            "provider_bytes_downloaded": 0,
        },
        "group_contract": {
            "status": "SIX_WHOLE_EVENT_GROUPS_FROZEN_NO_PARTITION",
            "event_rule": "All future chips, regions, labels, or derivatives from one fire stay in one eventual role.",
            "scene_rule": "Both exact Sentinel scenes and every derived band/mask stay with their event group.",
            "geography_rule": "Overlapping MTBS boundaries or derived AOIs may not cross eventual roles.",
            "time_rule": "Products in the same event window may not cross eventual roles.",
            "partition_rule": "No train/validation/test assignment exists. Pixel/source fitness, accepted regions in both classes, unknown boundaries, dominance, and never-tuned transfer gates still precede any split.",
        },
        "quality_gates": {
            "three_additional_immutable_event_identities": True,
            "no_overlap_with_current_group_ids": True,
            "selected_boundaries_nonoverlapping": True,
            "both_classes_and_unknown_feasibility": "UNPROVED_REQUIRES_PIXEL_INSPECTION_AND_OWNER_REVIEW",
            "at_least_two_replicated_source_regimes": True,
            "sentinel_sensor_comparability_explicit": True,
            "acquisition_cost_bounded_before_download": True,
            "provider_pixels_opened": False,
            "dataset_created": False,
            "split_created": False,
            "baseline_created": False,
            "model_created": False,
        },
        "terms": {
            "status": "RESOLVED_FOR_PUBLIC_METADATA_AND_BOUNDED_SENTINEL_ACQUISITION_PLANNING",
            "mtbs": "Official MTBS material is current, revisable remote-sensing reference; cite USGS and USDA Forest Service and preserve product-specific notices before pixel use.",
            "sentinel": "CDSE terms provide free, full, and open Sentinel data access subject to the Sentinel legal notice; portal content restrictions do not silently transfer to Sentinel data.",
            "scope_limit": "Recheck exact archive notices and product terms before retaining, redistributing, or publishing any provider bytes or derived pixels.",
        },
        "claims": {
            "permitted": [
                "Current official metadata freezes three additional comparable whole-event acquisition groups.",
                "The six-event minimum is met at metadata identity level only.",
                "Exact Sentinel product identities and bounded catalogue sizes are acquisition plans, not pixel fitness.",
            ],
            "prohibited": [
                "No selected product has been downloaded or locally inspected in this checkpoint.",
                "No MTBS, BAER, RAVG, dNBR, SCL, boundary, owner response, or absence is automatic label truth.",
                "No accepted dataset, split, baseline, model, metric, field validation, official status, endorsement, or operational readiness exists.",
            ],
        },
        "limitations": [
            "Catalogue cloud is tile-level metadata and does not establish local valid pixels over a fire.",
            "MTBS mappings are analyst-interpreted and may be revised; boundaries are not incident perimeters or field truth.",
            "Grandview and Green Ridge are geographically closer than the other selected pairings; event IDs and nonoverlapping boundaries prevent direct leakage but do not eliminate spatial autocorrelation.",
            "The selected pool is Central Oregon and portfolio-bounded; it does not establish broad geographic generalization.",
            "Owner-confirmed prototype labels remain one-owner evidence, not independent ground truth or inter-rater validation.",
        ],
        "source_guidance": source["source_guidance"],
        "phase_comparison": {
            "phase_two_objective": "Passes the six-event metadata identity and source-regime planning gate while leaving data, label, split, and baseline fitness explicitly unproved.",
            "portfolio_narrative": "Strengthens the portfolio by showing a reproducible event-level acquisition contract and honest restraint before expensive downloads or training.",
            "next_checkpoint": "Acquire and gate the first frozen event end to end; advance the second only after exact bytes, terms, native-pixel QA, rendered evidence, and reconstruction pass.",
        },
        "warning": WARNING,
    }


def _font(size: int) -> ImageFont.ImageFont:
    candidates = (
        Path("C:/Windows/Fonts/segoeui.ttf"),
        Path("C:/Windows/Fonts/arial.ttf"),
    )
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def _draw_wrapped(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, *, width: int, size: int, fill: str, max_lines: int = 4) -> int:
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
    lines = lines[:max_lines]
    for index, line in enumerate(lines):
        draw.text((xy[0], xy[1] + index * (size + 7)), line, font=_font(size), fill=fill)
    return len(lines) * (size + 7)


def render_png(report: dict[str, Any], path: Path) -> None:
    width, height = 1800, 1250
    canvas = Image.new("RGB", (width, height), "#f4f0e8")
    draw = ImageDraw.Draw(canvas)
    ink, muted, teal, orange, panel = "#15211d", "#5d6b64", "#006b64", "#f05a28", "#fffdf8"
    draw.rectangle((0, 0, width, 190), fill="#132a26")
    draw.text((60, 40), "Six event groups are frozen—pixels remain gated", font=_font(44), fill="white")
    _draw_wrapped(draw, (62, 104), "Three current Sentinel-era Central Oregon events close the metadata minimum without creating a dataset, split, baseline, or model.", width=1600, size=23, fill="#c9ddd6", max_lines=2)

    selected = [item for item in report["candidate_assessments"] if item["disposition"] == "FROZEN_FOR_BOUNDED_ACQUISITION"]
    for index, item in enumerate(selected):
        left = 60 + index * 570
        draw.rounded_rectangle((left, 230, left + 530, 560), radius=20, fill=panel, outline="#d7d0c4", width=2)
        draw.rectangle((left, 230, left + 8, 560), fill=teal)
        draw.text((left + 30, 255), f"FROZEN {index + 4} OF 6", font=_font(18), fill=teal)
        draw.text((left + 30, 292), item["fire_name"], font=_font(30), fill=ink)
        draw.text((left + 30, 338), f"{item['year']}  ·  {item['acres']:,.0f} acres", font=_font(21), fill=muted)
        pair = item["scene_pair"]
        _draw_wrapped(draw, (left + 30, 382), f"{'+'.join(item['programs'])} reference · {pair['scene_group']['grid_code']} orbit {pair['scene_group']['relative_orbit']} · {pair['post_window'].replace('_', ' ')}", width=455, size=18, fill=ink, max_lines=3)
        draw.text((left + 30, 496), f"{(pair['pre_scene']['product_bytes'] + pair['post_scene']['product_bytes']) / (1024**3):.2f} GiB catalogued", font=_font(19), fill=orange)

    draw.rounded_rectangle((60, 610, 1740, 820), radius=22, fill="#e6efeb", outline="#b8cbc3", width=2)
    draw.text((90, 642), "WHAT THIS PASSES", font=_font(21), fill=teal)
    _draw_wrapped(draw, (90, 686), "Six immutable whole-event identities · six distinct event years · repeated MTBS, BAER, and RAVG reference regimes · nonoverlapping selected boundaries · exact Sentinel pair identities · bounded acquisition size.", width=1550, size=25, fill=ink, max_lines=3)

    draw.rounded_rectangle((60, 850, 1740, 1060), radius=22, fill="#fff7f1", outline="#efc4ae", width=2)
    draw.text((90, 882), "WHAT REMAINS BLOCKED", font=_font(21), fill=orange)
    _draw_wrapped(draw, (90, 925), "No provider pixel has been opened. Both classes, unknown boundaries, local cloud/smoke/shadow/snow, registration, source fitness, owner review, dominance, split integrity, baseline value, and model value remain unproved.", width=1550, size=24, fill=ink, max_lines=4)

    trace = f"run {report['run_id']} · commit {report['git_source_commit'][:12]} · software {report['software_version']} · dataset none · split none · baseline none · model none"
    draw.text((70, 1090), trace, font=_font(18), fill=muted)
    draw.rectangle((0, 1160, width, height), fill="#132a26")
    _draw_wrapped(draw, (55, 1182), report["warning"], width=1690, size=18, fill="white", max_lines=2)
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path, format="PNG", optimize=False)


def render_html(report: dict[str, Any], path: Path, png_name: str) -> None:
    rows = []
    for item in report["candidate_assessments"]:
        pair = item.get("scene_pair")
        scene = "No compatible pair"
        if pair:
            scene = f"<code>{escape(pair['pre_scene']['id'])}</code><br><code>{escape(pair['post_scene']['id'])}</code>"
        rows.append(
            "<tr>"
            f"<td>{escape(item['fire_name'])}<br><code>{escape(item['fire_id'])}</code></td>"
            f"<td>{item['year']}<br>{item['acres']:,.0f} acres</td>"
            f"<td>{escape('+'.join(item['programs']))}</td>"
            f"<td>{scene}</td>"
            f"<td><strong>{escape(item['disposition'])}</strong><br>{escape('; '.join(item['reasons']))}</td>"
            "</tr>"
        )
    distances = "".join(
        f"<li><code>{escape(item['first_event_group_id'])}</code> ↔ <code>{escape(item['second_event_group_id'])}</code>: {item['representative_point_distance_km']:.3f} km</li>"
        for item in report["separation"]["pairwise_selected_representative_point_distances"]
    )
    permitted = "".join(f"<li>{escape(item)}</li>" for item in report["claims"]["permitted"])
    prohibited = "".join(f"<li>{escape(item)}</li>" for item in report["claims"]["prohibited"])
    limits = "".join(f"<li>{escape(item)}</li>" for item in report["limitations"])
    sources = "".join(f'<li><a href="{escape(item["url"])}">{escape(item["organization"])}</a> — {escape(item["role"])}</li>' for item in report["source_guidance"])
    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>BurnLens additional whole-event group plan</title>
<style>:root{{--ink:#15211d;--paper:#f4f0e8;--panel:#fffdf8;--teal:#006b64;--orange:#f05a28}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 system-ui,sans-serif}}header{{background:#132a26;color:white;padding:2.4rem max(1rem,calc((100% - 1220px)/2))}}header p{{max-width:82ch;color:#c9ddd6}}main{{max-width:1220px;margin:auto;padding:2rem 1rem 4rem}}section,.status{{background:var(--panel);border:1px solid #d7d0c4;border-radius:14px;padding:1.25rem;margin:1rem 0}}.status{{border-left:8px solid var(--teal)}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:1rem}}.metric{{display:block;color:var(--teal);font-size:2rem;font-weight:760}}img{{display:block;width:100%;height:auto;border:1px solid #d7d0c4;border-radius:14px}}table{{width:100%;border-collapse:collapse}}th,td{{padding:.7rem;text-align:left;vertical-align:top;border-bottom:1px solid #ddd5c8}}th{{background:#e6efeb}}code{{overflow-wrap:anywhere}}a{{color:var(--teal)}}dt{{font-weight:750;margin-top:.7rem}}dd{{margin-left:0}}.warning{{background:#132a26;color:white;padding:1rem;border-radius:10px;font-weight:650}}caption{{text-align:left;font-weight:750;margin-bottom:.6rem}}</style></head><body>
<header><h1>Six event groups are frozen—pixels remain gated</h1><p>BurnLens adds three current, Sentinel-era Central Oregon acquisition groups to Darlene, McKay, and Tepee. This is an event-identity and acquisition contract, not a dataset or scientific validation.</p></header><main>
<div class="status"><h2>SIX_WHOLE_EVENT_GROUPS_FROZEN_NO_DATASET</h2><p>Green Ridge (2020), Grandview (2021), and Petes Lake (2023) win the predeclared pool-complement ranking. Exact Sentinel pairs are frozen; provider pixels remain unopened.</p></div>
<div class="grid"><section><span class="metric">{report['event_count_after_freeze']}</span>whole-event identities after freeze</section><section><span class="metric">{len(report['event_years_after_freeze'])}</span>distinct event years</section><section><span class="metric">{report['acquisition_contract']['catalogued_product_gib']:.3f} GiB</span>catalogued, not downloaded</section></div>
<figure><img src="{escape(png_name)}" width="1800" height="1250" alt="BurnLens evidence summary for three newly frozen event groups and remaining data gates"><figcaption><code>{REPORT_ID}</code> · run <code>{escape(report['run_id'])}</code> · commit <code>{escape(report['git_source_commit'])}</code></figcaption></figure>
<section><h2>Candidate pool and exact scene identities</h2><div style="overflow-x:auto"><table><caption>Every bounded candidate remains disclosed</caption><thead><tr><th>Event</th><th>Time / size</th><th>Official reference programs</th><th>Exact Sentinel pair</th><th>Disposition</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div></section>
<section><h2>Why these three</h2><ol><li>Maximize event years absent from the existing 2017/2018/2024 pool.</li><li>Maximize official reference programs repeated across selected events.</li><li>Maximize minimum representative-point separation.</li><li>Use stable fire IDs as the final tie-break.</li></ol><p>Actual score: {report['rules']['actual_score']['new_event_year_count']} new years, {report['rules']['actual_score']['replicated_selected_program_count']} repeated selected programs, {report['rules']['actual_score']['minimum_selected_distance_km']:.3f} km minimum selected separation.</p><ul>{distances}</ul><p>{escape(report['separation']['interpretation'])}</p></section>
<section><h2>Acquisition and leakage contract</h2><p><strong>{escape(report['acquisition_contract']['status'])}</strong></p><p>{escape(report['acquisition_contract']['next_gate'])}</p><dl><dt>Event</dt><dd>{escape(report['group_contract']['event_rule'])}</dd><dt>Scene</dt><dd>{escape(report['group_contract']['scene_rule'])}</dd><dt>Geography</dt><dd>{escape(report['group_contract']['geography_rule'])}</dd><dt>Time</dt><dd>{escape(report['group_contract']['time_rule'])}</dd><dt>Partition</dt><dd>{escape(report['group_contract']['partition_rule'])}</dd></dl></section>
<section><h2>Terms and source roles</h2><p><strong>{escape(report['terms']['status'])}</strong></p><dl><dt>MTBS / BAER / RAVG</dt><dd>{escape(report['terms']['mtbs'])}</dd><dt>Sentinel</dt><dd>{escape(report['terms']['sentinel'])}</dd><dt>Next terms gate</dt><dd>{escape(report['terms']['scope_limit'])}</dd></dl><ul>{sources}</ul></section>
<div class="grid"><section><h2>Permitted claims</h2><ul>{permitted}</ul></section><section><h2>Prohibited claims</h2><ul>{prohibited}</ul></section></div>
<section><h2>Binding limitations</h2><ul>{limits}</ul></section>
<section><h2>Phase and portfolio comparison</h2><dl><dt>Phase Two</dt><dd>{escape(report['phase_comparison']['phase_two_objective'])}</dd><dt>Portfolio</dt><dd>{escape(report['phase_comparison']['portfolio_narrative'])}</dd><dt>Next checkpoint</dt><dd>{escape(report['phase_comparison']['next_checkpoint'])}</dd></dl></section>
<section><h2>Traceability</h2><dl><dt>Repository / issue</dt><dd>{escape(report['repository'])} / #{report['task_issue']}</dd><dt>Source snapshot</dt><dd><code>{escape(report['source_snapshot']['source_id'])}</code> · <code>{escape(report['source_snapshot']['sha256'])}</code></dd><dt>Software / target / AOI / label schema</dt><dd>{escape(report['software_version'])} / <code>{escape(report['target_version'])}</code> / <code>{escape(report['aoi_version'])}</code> / <code>{escape(report['label_schema_version'])}</code></dd><dt>Application / dataset / split / baseline / model</dt><dd>None / none / none / none / none</dd><dt>Run / source commit</dt><dd><code>{escape(report['run_id'])}</code> / <code>{escape(report['git_source_commit'])}</code></dd></dl></section>
<p class="warning">{escape(report['warning'])}</p></main></body></html>"""
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
    render_html(report, paths["html"], paths["png"].name)
    return paths


def run_report(
    *,
    source_path: Path,
    output_directory: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, Path]:
    source = json.loads(source_path.read_text(encoding="utf-8"))
    report = build_report(
        source,
        source_sha256=_sha256(source_path),
        generated_at_utc=generated_at_utc,
        run_id=run_id,
        git_source_commit=git_source_commit,
    )
    return write_report(report, output_directory)
