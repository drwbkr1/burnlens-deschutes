"""Build a proposal-blinded label-review readiness packet from exact BurnLens evidence.

This module prepares deterministic source-pixel review material.  It does not
claim that an independent reviewer has completed the packet, create accepted
ground truth, or authorize a dataset, split, baseline, model, or accuracy claim.
"""

from __future__ import annotations

from collections import Counter
from hashlib import sha256
from html import escape
import json
import math
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

import numpy as np
from PIL import Image, ImageDraw
import rasterio

from .cross_event_label_transfer import build_report as build_cross_event_report
from .label_proposal import (
    IGNORE_VALUE,
    LABEL_SCHEMA_VERSION,
    STATE_CODES,
    STATE_NAMES,
    build_proposal as build_darlene_proposal,
)
from .optical_pair_evidence import AOI_VERSION, LABEL_PROTOCOL_VERSION, TARGET_VERSION, WARNING, _font


SOFTWARE_VERSION = "0.13.0"
REPORT_ID = "LABEL-REVIEW-PACKET-2026-001"
REPORT_SCHEMA_VERSION = "0.1.0"
REPORT_VERSION = "proposal-blinded-label-review-readiness-evidence-v0.1.0"
REVIEW_PROTOCOL_VERSION = "proposal-blinded-label-review-readiness-v0.1.0"
RESPONSE_SCHEMA_VERSION = "burnlens-label-review-response-v0.1.0"
ADJUDICATION_PROTOCOL_VERSION = "burnlens-label-adjudication-v0.1.0"
TASK_ISSUE = 375
SAMPLES_PER_PRESENT_STATE = 4
PREFERRED_MIN_SEPARATION_PX = 8
BLIND_UNITS_PER_PAGE = 7
CHIP_RADIUS_STATE_PX = 8

DARLENE_EVENT_ID = "event-darlene3-or-2024"
EXPECTED_CROSS_EVENTS = (
    "event-tepee-1144-ne-2018",
    "event-mckay-1035-ne-2017",
)
EVENT_ORDER = (DARLENE_EVENT_ID, *EXPECTED_CROSS_EVENTS)

FIRST_PASS_LABELS = ("burned", "background", "uncertain", "unusable")
EVIDENCE_SUFFICIENCY = ("sufficient", "limited", "insufficient")
CONFIDENCE_LEVELS = ("low", "medium", "high")
REASON_CODES = (
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
)

PRIMARY_SOURCES = (
    {
        "title": "MTBS mapping methods",
        "url": "https://www.mtbs.gov/mapping-methods",
        "use": "MTBS documents analyst interpretation, multitemporal imagery, scene-quality limits, and uncertainty.",
    },
    {
        "title": "Stratification and sample allocation for reference burned area data",
        "doi": "10.1016/j.rse.2017.06.041",
        "url": "https://doi.org/10.1016/j.rse.2017.06.041",
        "use": "Predeclared stratification improves the efficiency and objectivity of burned-area reference sampling.",
    },
    {
        "title": "Validation of the USGS Landsat Burned Area Essential Climate Variable",
        "doi": "10.1016/j.rse.2017.06.025",
        "url": "https://doi.org/10.1016/j.rse.2017.06.025",
        "use": "Independent analyst references and explicit agreement rules can reduce reference error.",
    },
    {
        "title": "Reference Data Accuracy Impacts Burned Area Product Validation",
        "doi": "10.3390/rs14174354",
        "url": "https://doi.org/10.3390/rs14174354",
        "use": "Interpreter experience and low-severity ambiguity materially affect burned-area reference data.",
    },
)


class LabelReviewPacketError(RuntimeError):
    """A deterministic, secret-free review-packet failure."""


def _write_utf8_lf(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    path.write_bytes(normalized.encode("utf-8"))


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
        raise LabelReviewPacketError(f"invalid JSON input {path.name}") from error
    if not isinstance(value, dict):
        raise LabelReviewPacketError(f"JSON input {path.name} is not an object")
    return value


def _canonical_sha256(value: Any) -> str:
    return sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    ).hexdigest()


def _read_bound_raster(
    path: Path,
    expected: dict[str, Any],
    *,
    kind: str,
) -> tuple[np.ndarray, rasterio.Affine]:
    expected_hash = expected.get("sha256")
    if _sha256_file(path) != expected_hash:
        raise LabelReviewPacketError(f"{kind} raster hash mismatch")
    with rasterio.open(path) as source:
        values = source.read(1)
        observed = {
            "width": source.width,
            "height": source.height,
            "dtype": source.dtypes[0],
            "crs": source.crs.to_string() if source.crs else None,
            "transform": [round(float(value), 9) for value in source.transform[:6]],
            "nodata": source.nodata,
        }
        wanted = {
            "width": expected["width"],
            "height": expected["height"],
            "dtype": expected["dtype"],
            "crs": expected["crs"],
            "transform": expected["transform"],
            "nodata": expected.get("nodata"),
        }
        if observed != wanted:
            raise LabelReviewPacketError(f"{kind} raster grid contract mismatch")
        return values, source.transform


def _proposal_output_path(directory: Path, item: dict[str, Any]) -> Path:
    filename = item.get("filename")
    if not isinstance(filename, str) or Path(filename).name != filename:
        raise LabelReviewPacketError("proposal output filename is unsafe")
    return directory / filename


def _event_record(
    *,
    event_group_id: str,
    fire_name: str,
    proposal_report_id: str,
    proposal_run_id: str,
    proposal_git_source_commit: str,
    proposal_version: str,
    proposal_report_sha256: str,
    state_raster_sha256: str,
    target_raster_sha256: str,
    transform: rasterio.Affine,
    states: np.ndarray,
    target: np.ndarray,
    pre_tci: np.ndarray,
    post_tci: np.ndarray,
    dnbr: np.ndarray,
    reference: np.ndarray,
    reference_kind: str,
    reference_detail: str,
    source_trace: dict[str, Any],
) -> dict[str, Any]:
    shape = states.shape
    arrays = (target, dnbr, reference)
    if any(item.shape != shape for item in arrays):
        raise LabelReviewPacketError(f"{event_group_id} review arrays do not share one grid")
    if (
        pre_tci.ndim != 3
        or pre_tci.shape[0] != 3
        or abs(pre_tci.shape[1] - shape[0] * 2) > 2
        or abs(pre_tci.shape[2] - shape[1] * 2) > 2
    ):
        raise LabelReviewPacketError(f"{event_group_id} pre true-color grid is not near-native 10 m")
    if post_tci.shape != pre_tci.shape:
        raise LabelReviewPacketError(f"{event_group_id} pre/post true-color grids differ")
    if set(int(value) for value in np.unique(states)) - set(STATE_NAMES):
        raise LabelReviewPacketError(f"{event_group_id} proposal contains an unknown state")
    if np.any((target != IGNORE_VALUE) & ~np.isin(states, (0, 1))):
        raise LabelReviewPacketError(f"{event_group_id} ignored proposal state entered target")
    if not np.array_equal(target[states == 0], np.zeros(int((states == 0).sum()), dtype=np.uint8)):
        raise LabelReviewPacketError(f"{event_group_id} background target mapping changed")
    if not np.array_equal(target[states == 1], np.ones(int((states == 1).sum()), dtype=np.uint8)):
        raise LabelReviewPacketError(f"{event_group_id} burned target mapping changed")
    counts = Counter(int(value) for value in states.reshape(-1))
    return {
        "event_group_id": event_group_id,
        "fire_name": fire_name,
        "grid": {
            "crs": "EPSG:32610",
            "transform": [round(float(value), 9) for value in transform[:6]],
            "width": shape[1],
            "height": shape[0],
            "pixel_size_m": 20,
        },
        "proposal": {
            "report_id": proposal_report_id,
            "run_id": proposal_run_id,
            "git_source_commit": proposal_git_source_commit,
            "label_proposal_version": proposal_version,
            "report_sha256": proposal_report_sha256,
            "state_raster_sha256": state_raster_sha256,
            "target_raster_sha256": target_raster_sha256,
            "state_counts": {
                STATE_NAMES[code]: counts.get(code, 0) for code in sorted(STATE_NAMES)
            },
        },
        "reference_context": {
            "kind": reference_kind,
            "detail": reference_detail,
            "role": "review context; never sufficient truth alone",
        },
        "source_trace": source_trace,
        "_arrays": {
            "states": states,
            "target": target,
            "pre_tci": pre_tci,
            "post_tci": post_tci,
            "dnbr": dnbr,
            "reference": reference,
        },
    }


def rebuild_exact_events(
    *,
    darlene_optical_package: Path,
    darlene_aoi_report: Path,
    darlene_reference_geojson: Path,
    darlene_optical_report: Path,
    darlene_registration_report: Path,
    darlene_proposal_report_path: Path,
    darlene_proposal_directory: Path,
    cross_event_optical_package: Path,
    mtbs_package: Path,
    cross_event_feasibility_report: Path,
    cross_event_source_fitness_report: Path,
    cross_event_proposal_report_path: Path,
    cross_event_proposal_directory: Path,
    git_source_commit: str,
) -> list[dict[str, Any]]:
    darlene_public = _load_json(darlene_proposal_report_path)
    if darlene_public.get("report_id") != "LABEL-PROPOSAL-2026-001":
        raise LabelReviewPacketError("unexpected Darlene proposal identity")
    darlene_state_path = _proposal_output_path(
        darlene_proposal_directory, darlene_public["output_rasters"]["state"]
    )
    darlene_target_path = _proposal_output_path(
        darlene_proposal_directory, darlene_public["output_rasters"]["target"]
    )
    committed_states, committed_transform = _read_bound_raster(
        darlene_state_path, darlene_public["output_rasters"]["state"], kind="Darlene state"
    )
    committed_target, target_transform = _read_bound_raster(
        darlene_target_path, darlene_public["output_rasters"]["target"], kind="Darlene target"
    )
    if committed_transform != target_transform:
        raise LabelReviewPacketError("Darlene state and target transforms differ")
    _, darlene_arrays, rebuilt_transform = build_darlene_proposal(
        package=darlene_optical_package,
        aoi_report_path=darlene_aoi_report,
        reference_geojson_path=darlene_reference_geojson,
        optical_report_path=darlene_optical_report,
        registration_report_path=darlene_registration_report,
        generated_at_utc="1970-01-01T00:00:00Z",
        run_id="BL-REVIEW-REBUILD-DARLENE",
        git_source_commit=git_source_commit,
    )
    if rebuilt_transform != committed_transform:
        raise LabelReviewPacketError("Darlene rebuilt transform differs from committed proposal")
    if not np.array_equal(darlene_arrays["states"], committed_states):
        raise LabelReviewPacketError("Darlene rebuilt states differ from committed proposal")
    if not np.array_equal(darlene_arrays["target"], committed_target):
        raise LabelReviewPacketError("Darlene rebuilt target differs from committed proposal")

    events = [
        _event_record(
            event_group_id=DARLENE_EVENT_ID,
            fire_name="Darlene 3",
            proposal_report_id=darlene_public["report_id"],
            proposal_run_id=darlene_public["run_id"],
            proposal_git_source_commit=darlene_public["git_source_commit"],
            proposal_version=darlene_public["label_proposal_version"],
            proposal_report_sha256=_sha256_file(darlene_proposal_report_path),
            state_raster_sha256=_sha256_file(darlene_state_path),
            target_raster_sha256=_sha256_file(darlene_target_path),
            transform=committed_transform,
            states=committed_states,
            target=committed_target,
            pre_tci=darlene_arrays["pre_tci"],
            post_tci=darlene_arrays["post_tci"],
            dnbr=darlene_arrays["dnbr"],
            reference=darlene_arrays["reference_mask"].astype(np.uint8),
            reference_kind="NIFC later incident-reference perimeter context",
            reference_detail="Binary later perimeter context on the 20 m proposal grid; not pixel-perfect truth.",
            source_trace={
                "optical_package_id": darlene_public["package_id"],
                "optical_registration_manifest_sha256": _sha256_file(
                    darlene_optical_package / ".burnlens-registration.json"
                ),
                "aoi_version": darlene_public["aoi_version"],
                "terms_review_ids": darlene_public["terms_review_ids"],
            },
        )
    ]

    cross_public = _load_json(cross_event_proposal_report_path)
    if cross_public.get("report_id") != "CROSS-EVENT-LABEL-TRANSFER-2026-002":
        raise LabelReviewPacketError("unexpected cross-event proposal identity")
    with TemporaryDirectory(prefix="burnlens-label-review-") as directory:
        rebuilt_report, visuals = build_cross_event_report(
            optical_package=cross_event_optical_package,
            mtbs_package=mtbs_package,
            feasibility_report_path=cross_event_feasibility_report,
            source_fitness_report_path=cross_event_source_fitness_report,
            output_directory=Path(directory),
            generated_at_utc="1970-01-01T00:00:00Z",
            run_id="BL-REVIEW-REBUILD-CROSS-EVENT",
            git_source_commit=git_source_commit,
        )
    if rebuilt_report.get("decision") != cross_public.get("decision"):
        raise LabelReviewPacketError("cross-event rebuilt decision differs from committed proposal")
    public_by_id = {item["event_group_id"]: item for item in cross_public["events"]}
    visual_by_id = {item["event_group_id"]: item for item in visuals}
    if tuple(public_by_id) != EXPECTED_CROSS_EVENTS or tuple(visual_by_id) != EXPECTED_CROSS_EVENTS:
        raise LabelReviewPacketError("cross-event proposal order changed")
    for event_id in EXPECTED_CROSS_EVENTS:
        public_event = public_by_id[event_id]
        visual = visual_by_id[event_id]
        state_path = _proposal_output_path(
            cross_event_proposal_directory, public_event["outputs"]["state"]
        )
        target_path = _proposal_output_path(
            cross_event_proposal_directory, public_event["outputs"]["target"]
        )
        committed_state, state_transform = _read_bound_raster(
            state_path, public_event["outputs"]["state"], kind=f"{event_id} state"
        )
        committed_target, target_transform = _read_bound_raster(
            target_path, public_event["outputs"]["target"], kind=f"{event_id} target"
        )
        if state_transform != target_transform:
            raise LabelReviewPacketError(f"{event_id} state and target transforms differ")
        if not np.array_equal(committed_state, visual["states"]):
            raise LabelReviewPacketError(f"{event_id} rebuilt states differ from committed proposal")
        if not np.array_equal(committed_target, visual["target"]):
            raise LabelReviewPacketError(f"{event_id} rebuilt target differs from committed proposal")
        events.append(
            _event_record(
                event_group_id=event_id,
                fire_name=public_event["fire_name"],
                proposal_report_id=cross_public["report_id"],
                proposal_run_id=cross_public["run_id"],
                proposal_git_source_commit=cross_public["git_source_commit"],
                proposal_version=cross_public["label_proposal_version"],
                proposal_report_sha256=_sha256_file(cross_event_proposal_report_path),
                state_raster_sha256=_sha256_file(state_path),
                target_raster_sha256=_sha256_file(target_path),
                transform=state_transform,
                states=committed_state,
                target=committed_target,
                pre_tci=visual["pre_tci"],
                post_tci=visual["post_tci"],
                dnbr=visual["dnbr"],
                reference=visual["mtbs"],
                reference_kind="MTBS annual thematic burn-severity reference",
                reference_detail="Nearest-neighbor MTBS 0-6 context; analyst-interpreted and never automatic truth.",
                source_trace={
                    "optical_package_id": cross_public["source_lineage"]["optical"]["package_id"],
                    "optical_registration_manifest_sha256": cross_public["input_hashes"][
                        "optical_registration_manifest_sha256"
                    ],
                    "mtbs_package_id": cross_public["source_lineage"]["mtbs"]["package_id"],
                    "mtbs_registration_manifest_sha256": cross_public["input_hashes"][
                        "mtbs_registration_manifest_sha256"
                    ],
                    "terms_review_ids": [
                        cross_public["source_lineage"]["optical"]["terms_review_id"],
                        cross_public["source_lineage"]["mtbs"]["terms_review_id"],
                    ],
                },
            )
        )
    return events


def _distance(a: tuple[int, int], b: tuple[int, int]) -> int:
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def _select_for_stratum(
    coordinates: np.ndarray,
    *,
    seed: str,
    event_group_id: str,
    state_code: int,
    count: int,
) -> tuple[list[tuple[int, int, str]], int | None]:
    ranked = []
    for row_value, column_value in coordinates:
        row, column = int(row_value), int(column_value)
        token = sha256(
            f"{seed}|{event_group_id}|{state_code}|{row}|{column}".encode("utf-8")
        ).hexdigest()
        ranked.append((token, row, column))
    ranked.sort()
    chosen: list[tuple[int, int, str]] = []
    chosen_coordinates: list[tuple[int, int]] = []
    for separation in (PREFERRED_MIN_SEPARATION_PX, 4, 0):
        for token, row, column in ranked:
            point = (row, column)
            if point in chosen_coordinates:
                continue
            if separation and any(_distance(point, existing) < separation for existing in chosen_coordinates):
                continue
            chosen.append((row, column, token))
            chosen_coordinates.append(point)
            if len(chosen) == count:
                break
        if len(chosen) == count:
            break
    if len(chosen_coordinates) < 2:
        minimum = None
    else:
        minimum = min(
            _distance(first, second)
            for index, first in enumerate(chosen_coordinates)
            for second in chosen_coordinates[index + 1 :]
        )
    return chosen, minimum


def select_sample_units(
    events: list[dict[str, Any]],
    *,
    selection_seed: str,
    per_present_state: int = SAMPLES_PER_PRESENT_STATE,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    by_id = {item["event_group_id"]: item for item in events}
    if tuple(by_id) != EVENT_ORDER:
        raise LabelReviewPacketError("review event order changed")
    units: list[dict[str, Any]] = []
    coverage: list[dict[str, Any]] = []
    for event_id in EVENT_ORDER:
        event = by_id[event_id]
        arrays = event["_arrays"]
        states = arrays["states"]
        transform = rasterio.Affine(*event["grid"]["transform"])
        for state_code in sorted(STATE_NAMES):
            coordinates = np.argwhere(states == state_code)
            requested = per_present_state if len(coordinates) else 0
            selected, minimum = _select_for_stratum(
                coordinates,
                seed=selection_seed,
                event_group_id=event_id,
                state_code=state_code,
                count=min(requested, len(coordinates)),
            )
            coverage.append(
                {
                    "event_group_id": event_id,
                    "proposal_state": STATE_NAMES[state_code],
                    "population_pixels": int(len(coordinates)),
                    "requested_units": requested,
                    "selected_units": len(selected),
                    "structural_absence": len(coordinates) == 0,
                    "minimum_selected_separation_px": minimum,
                    "minimum_selected_separation_m": None if minimum is None else minimum * 20,
                }
            )
            for row, column, selection_hash in selected:
                x, y = transform * (column + 0.5, row + 0.5)
                target_value = int(arrays["target"][row, column])
                reference_value = int(arrays["reference"][row, column])
                units.append(
                    {
                        "event_group_id": event_id,
                        "fire_name": event["fire_name"],
                        "row": row,
                        "column": column,
                        "pixel_center_utm10n": [round(float(x), 3), round(float(y), 3)],
                        "proposal_state": STATE_NAMES[state_code],
                        "proposal_state_code": state_code,
                        "proposal_target_value": None if target_value == IGNORE_VALUE else target_value,
                        "dnbr_center": round(float(arrays["dnbr"][row, column]), 6),
                        "reference_context_value": reference_value,
                        "selection_hash": selection_hash,
                    }
                )
    for unit in units:
        unit["presentation_hash"] = sha256(
            (
                f"{selection_seed}|presentation|{unit['event_group_id']}|"
                f"{unit['row']}|{unit['column']}"
            ).encode("utf-8")
        ).hexdigest()
    units.sort(key=lambda item: item["presentation_hash"])
    for index, unit in enumerate(units, start=1):
        unit["sample_id"] = f"LRU-{index:03d}"
        unit["blind_page"] = (
            f"{REPORT_ID}-BLIND-{math.ceil(index / BLIND_UNITS_PER_PAGE):02d}.png"
        )
        unit["blind_page_position"] = ((index - 1) % BLIND_UNITS_PER_PAGE) + 1
    return units, coverage


def response_template(packet_id: str, packet_run_id: str, units: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "response_schema_version": RESPONSE_SCHEMA_VERSION,
        "packet_id": packet_id,
        "packet_run_id": packet_run_id,
        "reviewer": {
            "reviewer_id": None,
            "independent_from_proposal_author": None,
            "burned_area_interpretation_experience": None,
            "proposal_seen_before_first_pass": None,
            "attestation": None,
        },
        "review_started_at_utc": None,
        "review_completed_at_utc": None,
        "responses": [
            {
                "sample_id": unit["sample_id"],
                "first_pass_label": None,
                "evidence_sufficiency": None,
                "confidence": None,
                "reason_codes": [],
                "notes": None,
            }
            for unit in units
        ],
        "completed": False,
        "instructions": {
            "order": "Complete this first-pass response before opening the reveal page.",
            "allowed_first_pass_labels": list(FIRST_PASS_LABELS),
            "allowed_evidence_sufficiency": list(EVIDENCE_SUFFICIENCY),
            "allowed_confidence": list(CONFIDENCE_LEVELS),
            "allowed_reason_codes": list(REASON_CODES),
            "privacy": "Use an opaque reviewer ID. Do not enter credentials, secrets, or unnecessary personal data.",
        },
    }


def adjudication_template(packet_id: str, packet_run_id: str, units: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "adjudication_protocol_version": ADJUDICATION_PROTOCOL_VERSION,
        "packet_id": packet_id,
        "packet_run_id": packet_run_id,
        "input_response_sha256": [],
        "adjudicator": {
            "adjudicator_id": None,
            "independent_from_proposal_author": None,
            "attestation": None,
        },
        "adjudicated_at_utc": None,
        "decisions": [
            {
                "sample_id": unit["sample_id"],
                "required": None,
                "final_label": None,
                "evidence_sufficiency": None,
                "reason": None,
            }
            for unit in units
        ],
        "completed": False,
        "allowed_final_labels": list(FIRST_PASS_LABELS),
        "privacy": "Use an opaque adjudicator ID. Do not enter credentials, secrets, or unnecessary personal data.",
    }


def _crop(array: np.ndarray, row: int, column: int, radius: int, *, scale: int = 1) -> np.ndarray:
    center_row = row * scale + (scale // 2)
    center_column = column * scale + (scale // 2)
    scaled_radius = radius * scale
    top, bottom = center_row - scaled_radius, center_row + scaled_radius + 1
    left, right = center_column - scaled_radius, center_column + scaled_radius + 1
    if array.ndim == 3:
        output = np.zeros((array.shape[0], bottom - top, right - left), dtype=array.dtype)
        source_top, source_bottom = max(0, top), min(array.shape[1], bottom)
        source_left, source_right = max(0, left), min(array.shape[2], right)
        output[:, source_top - top : source_bottom - top, source_left - left : source_right - left] = (
            array[:, source_top:source_bottom, source_left:source_right]
        )
    else:
        output = np.zeros((bottom - top, right - left), dtype=array.dtype)
        source_top, source_bottom = max(0, top), min(array.shape[0], bottom)
        source_left, source_right = max(0, left), min(array.shape[1], right)
        output[source_top - top : source_bottom - top, source_left - left : source_right - left] = (
            array[source_top:source_bottom, source_left:source_right]
        )
    return output


def _mark_center(image: Image.Image, *, color: str = "#00d4c7") -> Image.Image:
    marked = image.copy()
    draw = ImageDraw.Draw(marked)
    x, y = marked.width // 2, marked.height // 2
    draw.ellipse((x - 9, y - 9, x + 9, y + 9), outline=color, width=4)
    draw.line((x - 18, y, x - 11, y), fill=color, width=3)
    draw.line((x + 11, y, x + 18, y), fill=color, width=3)
    draw.line((x, y - 18, x, y - 11), fill=color, width=3)
    draw.line((x, y + 11, x, y + 18), fill=color, width=3)
    return marked


def _crop_center(
    array: np.ndarray,
    *,
    center_row: float,
    center_column: float,
    radius_row: int,
    radius_column: int,
) -> np.ndarray:
    center_row_int = int(round(center_row))
    center_column_int = int(round(center_column))
    top, bottom = center_row_int - radius_row, center_row_int + radius_row + 1
    left, right = center_column_int - radius_column, center_column_int + radius_column + 1
    output = np.zeros((array.shape[0], bottom - top, right - left), dtype=array.dtype)
    source_top, source_bottom = max(0, top), min(array.shape[1], bottom)
    source_left, source_right = max(0, left), min(array.shape[2], right)
    output[:, source_top - top : source_bottom - top, source_left - left : source_right - left] = (
        array[:, source_top:source_bottom, source_left:source_right]
    )
    return output


def _true_color_chip(
    array: np.ndarray,
    row: int,
    column: int,
    *,
    state_shape: tuple[int, int],
) -> Image.Image:
    row_scale = array.shape[1] / state_shape[0]
    column_scale = array.shape[2] / state_shape[1]
    chip = _crop_center(
        array,
        center_row=(row + 0.5) * row_scale - 0.5,
        center_column=(column + 0.5) * column_scale - 0.5,
        radius_row=max(1, round(CHIP_RADIUS_STATE_PX * row_scale)),
        radius_column=max(1, round(CHIP_RADIUS_STATE_PX * column_scale)),
    )
    image = Image.fromarray(np.moveaxis(chip, 0, 2), mode="RGB")
    return _mark_center(image.resize((360, 360), Image.Resampling.LANCZOS))


def _dnbr_chip(values: np.ndarray, row: int, column: int) -> Image.Image:
    chip = _crop(values, row, column, CHIP_RADIUS_STATE_PX)
    normalized = np.clip((chip + 0.25) / 0.75, 0.0, 1.0)
    rgb = np.zeros((*chip.shape, 3), dtype=np.uint8)
    low = normalized <= 1 / 3
    high = normalized >= 1 / 3
    low_mix = np.clip(normalized * 3, 0, 1)
    high_mix = np.clip((normalized - 1 / 3) * 1.5, 0, 1)
    blue = np.array([42, 93, 133], dtype=np.float32)
    neutral = np.array([239, 231, 207], dtype=np.float32)
    orange = np.array([184, 54, 31], dtype=np.float32)
    rgb[low] = (
        blue[None, :] * (1 - low_mix[low, None])
        + neutral[None, :] * low_mix[low, None]
    ).astype(np.uint8)
    rgb[high] = (
        neutral[None, :] * (1 - high_mix[high, None])
        + orange[None, :] * high_mix[high, None]
    ).astype(np.uint8)
    image = Image.fromarray(rgb, mode="RGB")
    return _mark_center(image.resize((360, 360), Image.Resampling.NEAREST))


def _reference_chip(values: np.ndarray, row: int, column: int, *, kind: str) -> Image.Image:
    chip = _crop(values, row, column, CHIP_RADIUS_STATE_PX)
    if kind.startswith("NIFC"):
        rgb = np.full((*chip.shape, 3), (237, 232, 218), dtype=np.uint8)
        rgb[chip.astype(bool)] = (55, 111, 102)
    else:
        colors = {
            0: (235, 232, 221),
            1: (222, 214, 151),
            2: (244, 183, 88),
            3: (224, 112, 52),
            4: (151, 48, 31),
            5: (85, 155, 89),
            6: (70, 70, 70),
        }
        rgb = np.full((*chip.shape, 3), (30, 30, 30), dtype=np.uint8)
        for code, color in colors.items():
            rgb[chip == code] = color
    image = Image.fromarray(rgb, mode="RGB")
    return _mark_center(image.resize((360, 360), Image.Resampling.NEAREST))


def _draw_panel(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    image: Image.Image,
    x: int,
    y: int,
    title: str,
    subtitle: str,
) -> None:
    canvas.paste(image, (x, y))
    draw.rectangle((x, y, x + image.width, y + image.height), outline="#18312b", width=3)
    draw.rectangle((x, y, x + image.width, y + 58), fill="#18312b")
    draw.text((x + 12, y + 7), title, fill="white", font=_font(15))
    draw.text((x + 12, y + 31), subtitle, fill="#b9d8cf", font=_font(11))


def render_blind_pages(
    events: list[dict[str, Any]],
    units: list[dict[str, Any]],
    output_directory: Path,
) -> list[Path]:
    event_by_id = {item["event_group_id"]: item for item in events}
    paths: list[Path] = []
    for page_index in range(math.ceil(len(units) / BLIND_UNITS_PER_PAGE)):
        page_units = units[
            page_index * BLIND_UNITS_PER_PAGE : (page_index + 1) * BLIND_UNITS_PER_PAGE
        ]
        height = 175 + len(page_units) * 445 + 85
        canvas = Image.new("RGB", (1800, height), "#f4f0e8")
        draw = ImageDraw.Draw(canvas)
        draw.rectangle((0, 0, 1800, 145), fill="#132a26")
        draw.text((48, 25), "BURNLENS / PROPOSAL-BLINDED FIRST PASS", fill="#b9d8cf", font=_font(18))
        draw.text((48, 61), f"LABEL REVIEW PAGE {page_index + 1:02d}", fill="white", font=_font(34))
        draw.text(
            (48, 108),
            "Review exact pre/post imagery, continuous dNBR, and official-source context before opening the reveal.",
            fill="#b9d8cf",
            font=_font(14),
        )
        for row_index, unit in enumerate(page_units):
            event = event_by_id[unit["event_group_id"]]
            arrays = event["_arrays"]
            top = 175 + row_index * 445
            draw.text(
                (45, top),
                f"{unit['sample_id']}  /  {event['fire_name']}  /  20 m center ({unit['row']}, {unit['column']})",
                fill="#006b64",
                font=_font(17),
            )
            _draw_panel(
                canvas,
                draw,
                _true_color_chip(
                    arrays["pre_tci"],
                    unit["row"],
                    unit["column"],
                    state_shape=arrays["states"].shape,
                ),
                45,
                top + 38,
                "PRE",
                "Sentinel-2 true color / 10 m",
            )
            _draw_panel(
                canvas,
                draw,
                _true_color_chip(
                    arrays["post_tci"],
                    unit["row"],
                    unit["column"],
                    state_shape=arrays["states"].shape,
                ),
                470,
                top + 38,
                "POST",
                "Sentinel-2 true color / 10 m",
            )
            _draw_panel(
                canvas,
                draw,
                _dnbr_chip(arrays["dnbr"], unit["row"], unit["column"]),
                895,
                top + 38,
                "dNBR",
                "fixed -0.25 to +0.50 display",
            )
            _draw_panel(
                canvas,
                draw,
                _reference_chip(
                    arrays["reference"],
                    unit["row"],
                    unit["column"],
                    kind=event["reference_context"]["kind"],
                ),
                1320,
                top + 38,
                "SOURCE CONTEXT",
                "NIFC or MTBS / not truth alone",
            )
        draw.text(
            (45, height - 58),
            "The cyan marker identifies one proposal-grid pixel. No BurnLens proposed state or target is shown on this page.",
            fill="#5d6b64",
            font=_font(13),
        )
        path = output_directory / f"{REPORT_ID}-BLIND-{page_index + 1:02d}.png"
        path.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(path, format="PNG", optimize=False)
        paths.append(path)
    return paths


def _coverage_summary(coverage: list[dict[str, Any]]) -> dict[str, Any]:
    absent = [
        {"event_group_id": item["event_group_id"], "proposal_state": item["proposal_state"]}
        for item in coverage
        if item["structural_absence"]
    ]
    return {
        "strata_total": len(coverage),
        "strata_present": sum(not item["structural_absence"] for item in coverage),
        "strata_structurally_absent": len(absent),
        "structural_absences": absent,
        "selected_units": sum(item["selected_units"] for item in coverage),
        "requested_units_for_present_strata": sum(item["requested_units"] for item in coverage),
    }


def _public_event(event: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in event.items() if key != "_arrays"}


def build_packet(
    *,
    events: list[dict[str, Any]],
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    seed_inputs = {
        "protocol": REVIEW_PROTOCOL_VERSION,
        "event_order": list(EVENT_ORDER),
        "proposal_bindings": [
            {
                "event_group_id": item["event_group_id"],
                "report_sha256": item["proposal"]["report_sha256"],
                "state_raster_sha256": item["proposal"]["state_raster_sha256"],
                "target_raster_sha256": item["proposal"]["target_raster_sha256"],
            }
            for item in events
        ],
    }
    selection_seed = _canonical_sha256(seed_inputs)
    units, coverage = select_sample_units(events, selection_seed=selection_seed)
    coverage_summary = _coverage_summary(coverage)
    packet = {
        "report_id": REPORT_ID,
        "schema_version": REPORT_SCHEMA_VERSION,
        "report_version": REPORT_VERSION,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": TASK_ISSUE,
        "git_source_commit": git_source_commit,
        "software_version": SOFTWARE_VERSION,
        "application_version": None,
        "aoi_version": AOI_VERSION,
        "target_version": TARGET_VERSION,
        "dataset_version": None,
        "split_version": None,
        "label_protocol_version": LABEL_PROTOCOL_VERSION,
        "label_schema_version": LABEL_SCHEMA_VERSION,
        "review_protocol_version": REVIEW_PROTOCOL_VERSION,
        "response_schema_version": RESPONSE_SCHEMA_VERSION,
        "adjudication_protocol_version": ADJUDICATION_PROTOCOL_VERSION,
        "baseline_version": None,
        "model_version": None,
        "selection": {
            "seed_sha256": selection_seed,
            "seed_inputs": seed_inputs,
            "method": (
                "Within every present event-by-proposal-state stratum, rank every pixel by SHA-256 "
                "of the immutable seed, event, state, row, and column; greedily select four with an "
                "8-pixel preferred separation, relaxing to 4 then 0 only if required. Assign the "
                "first-pass presentation order with a second deterministic hash so state and event "
                "strata are not shown as contiguous blocks."
            ),
            "samples_per_present_state": SAMPLES_PER_PRESENT_STATE,
            "preferred_minimum_separation_px": PREFERRED_MIN_SEPARATION_PX,
            "preferred_minimum_separation_m": PREFERRED_MIN_SEPARATION_PX * 20,
            "sampling_scope": (
                "Bounded coverage probe for label-fitness review readiness. It is not a probability "
                "sample, accuracy estimate, representative validation study, or field reference."
            ),
        },
        "events": [_public_event(item) for item in events],
        "coverage": coverage,
        "coverage_summary": coverage_summary,
        "units": units,
        "review_workflow": {
            "first_pass": (
                "Review the blind pages and complete the response template without opening the reveal. "
                "The blind material contains exact pre/post imagery, continuous dNBR, and official-source "
                "context but no sample-specific BurnLens proposal state or binary target."
            ),
            "reveal": (
                "After first-pass responses are locked and hashed, open the reveal page, compare against "
                "the proposal, and use the adjudication template only for disagreements or insufficient evidence."
            ),
            "independence": (
                "A qualifying response must come from a reviewer who did not author the proposal, attests "
                "that the reveal was not seen before first pass, and uses an opaque reviewer identifier."
            ),
            "privacy": "No credentials, secrets, or unnecessary personal data belong in a response.",
        },
        "predeclared_decision_rule": {
            "current_decision": "READY_FOR_INDEPENDENT_REVIEW_DEFER_DATASET",
            "minimum_before_adjudication": [
                "Two qualifying independent reviewers complete every selected unit.",
                "First-pass response files are immutable and hashed before proposal reveal.",
                "Every present candidate class in every event has completed evidence-sufficiency judgments.",
            ],
            "minimum_before_dataset_candidacy": [
                "Every reviewer disagreement is resolved by a qualifying independent adjudicator or the unit remains ignored.",
                "Only units with sufficient or explicitly limited evidence and resolved binary agreement may support candidate labels.",
                "Uncertain, unusable, insufficient, source-conflicted, or unresolved units remain unknown, excluded, or review-needed.",
                "Any systematic event/class contradiction requires proposal-method revision and a new packet rather than threshold shopping.",
                "This bounded packet alone cannot establish statistical accuracy or field validation.",
            ],
            "automatic_deferral_conditions": [
                "Fewer than two qualifying complete independent responses.",
                "Proposal exposure before first-pass completion.",
                "Missing response hashes, duplicate sample IDs, altered packet bindings, or out-of-domain values.",
                "Any unresolved disagreement, insufficient evidence, or unsupported public claim.",
            ],
        },
        "research_basis": list(PRIMARY_SOURCES),
        "quality_gates": {
            "registered_source_packages_reopened": True,
            "committed_proposal_rasters_hash_reverified": True,
            "proposal_pixels_recomputed_and_exactly_matched": True,
            "all_present_event_state_strata_sampled": coverage_summary["selected_units"]
            == coverage_summary["requested_units_for_present_strata"],
            "structural_absence_reported": True,
            "proposal_blinded_first_pass_material_created": True,
            "completed_independent_responses": 0,
            "completed_adjudications": 0,
            "dataset_created": False,
            "split_created": False,
            "baseline_created": False,
            "model_created": False,
            "accuracy_claim_created": False,
            "field_validation_claim_created": False,
        },
        "decision": "READY_FOR_INDEPENDENT_REVIEW_DEFER_DATASET",
        "decision_detail": (
            f"{coverage_summary['selected_units']} deterministic units cover every proposal state present "
            "across Darlene 3, Tepee, and McKay. The packet makes independent review executable, but no "
            "independent response or adjudication is supplied, so dataset candidacy remains deferred."
        ),
        "claims": {
            "proven": [
                "Exact registered source pixels and committed proposal rasters can be bound into a deterministic review packet.",
                "Every proposal state present in each event is represented, and structural absences are explicit.",
                "The first-pass material separates source context from the later proposal reveal.",
            ],
            "not_proven": [
                "No independent human review, inter-rater agreement, adjudication, accepted ground truth, or field validation has occurred.",
                "The bounded sample is not a probability sample and supports no accuracy, generalization, or operational claim.",
                "No dataset, split, baseline, model, application, deployment, official status, or endorsement exists.",
            ],
        },
        "attribution": (
            "Contains modified Copernicus Sentinel-2 data (2017, 2018, 2024), accessed through CDSE. "
            "Includes NIFC incident-reference context and MTBS reference from USGS/USDA Forest Service. "
            "No endorsement implied."
        ),
        "source_precedence": (
            "Official sources govern over BurnLens-derived evidence. NIFC, MTBS, Sentinel imagery, dNBR, "
            "and the BurnLens proposal each retain their documented roles and limitations."
        ),
        "warning": WARNING,
        "outputs": {},
    }
    return packet, units, response_template(REPORT_ID, run_id, units), adjudication_template(
        REPORT_ID, run_id, units
    )


def render_summary_png(
    packet: dict[str, Any],
    events: list[dict[str, Any]],
    units: list[dict[str, Any]],
    path: Path,
) -> None:
    canvas = Image.new("RGB", (1800, 1840), "#f4f0e8")
    draw = ImageDraw.Draw(canvas)
    ink, muted, teal, orange = "#15211d", "#5d6b64", "#006b64", "#f05a28"
    draw.rectangle((0, 0, 1800, 190), fill="#132a26")
    draw.text((55, 30), "BURNLENS / PHASE TWO / OBJECTIVE FOUR", fill="#b9d8cf", font=_font(19))
    draw.text((55, 70), "LABEL REVIEW READINESS", fill="white", font=_font(38))
    draw.text(
        (55, 126),
        "Proposal-blinded first pass / exact three-event evidence / no human response claimed",
        fill="#b9d8cf",
        font=_font(16),
    )
    draw.text((1420, 48), "STATUS", fill="#b9d8cf", font=_font(14))
    draw.text((1420, 78), "REVIEW READY", fill="#ffd166", font=_font(23))
    draw.text((1420, 119), "dataset deferred", fill="white", font=_font(14))

    metrics = [
        (str(packet["coverage_summary"]["selected_units"]), "review units"),
        (str(packet["coverage_summary"]["strata_present"]), "present event/state strata"),
        (str(packet["coverage_summary"]["strata_structurally_absent"]), "structural absences"),
        ("0", "independent responses"),
    ]
    for index, (value, label) in enumerate(metrics):
        left = 45 + index * 430
        draw.rounded_rectangle((left, 230, left + 390, 350), radius=15, fill="#e5efeb")
        draw.text((left + 24, 250), value, fill=teal, font=_font(31))
        draw.text((left + 24, 307), label, fill=muted, font=_font(14))

    draw.text((45, 395), "FIRST-PASS MATERIAL (proposal state concealed)", fill=teal, font=_font(20))
    event_by_id = {item["event_group_id"]: item for item in events}
    summary_units = [
        next(unit for unit in units if unit["event_group_id"] == event_id)
        for event_id in EVENT_ORDER
    ]
    for index, unit in enumerate(summary_units):
        event = event_by_id[unit["event_group_id"]]
        arrays = event["_arrays"]
        top = 445 + index * 350
        draw.text(
            (45, top - 28),
            f"{unit['sample_id']} / {event['fire_name']} / exact 20 m center",
            fill=ink,
            font=_font(16),
        )
        panels = (
            (
                _true_color_chip(
                    arrays["pre_tci"],
                    unit["row"],
                    unit["column"],
                    state_shape=arrays["states"].shape,
                ),
                "PRE",
            ),
            (
                _true_color_chip(
                    arrays["post_tci"],
                    unit["row"],
                    unit["column"],
                    state_shape=arrays["states"].shape,
                ),
                "POST",
            ),
            (_dnbr_chip(arrays["dnbr"], unit["row"], unit["column"]), "dNBR"),
            (
                _reference_chip(
                    arrays["reference"],
                    unit["row"],
                    unit["column"],
                    kind=event["reference_context"]["kind"],
                ),
                "SOURCE CONTEXT",
            ),
        )
        for panel_index, (image, title) in enumerate(panels):
            resized = image.resize((300, 300), Image.Resampling.LANCZOS)
            left = 45 + panel_index * 420
            canvas.paste(resized, (left, top))
            draw.rectangle((left, top, left + 300, top + 300), outline="#18312b", width=3)
            draw.rectangle((left, top, left + 300, top + 42), fill="#18312b")
            draw.text((left + 10, top + 11), title, fill="white", font=_font(13))

    box_top = 1505
    draw.rounded_rectangle((45, box_top, 1755, 1715), radius=16, fill="#fffdf8", outline="#d4cec1", width=2)
    draw.text((72, box_top + 23), "DECISION BOUNDARY", fill=orange, font=_font(20))
    lines = [
        "Two qualifying independent reviewers must complete every unit before adjudication.",
        "Disagreement, uncertainty, unusable evidence, or insufficient evidence keeps a unit ignored.",
        "This packet is a coverage probe, not an accuracy estimate, field reference, or validation study.",
        "No dataset, split, baseline, model, application, or operational result exists.",
    ]
    for index, line in enumerate(lines):
        draw.text((88, box_top + 65 + index * 34), f"{index + 1}. {line}", fill=ink, font=_font(14))
    trace = (
        f"run {packet['run_id']} / source {packet['git_source_commit'][:12]} / software {packet['software_version']} / "
        f"schema {packet['label_schema_version']} / review {packet['review_protocol_version']}"
    )
    draw.text((45, 1750), trace, fill=muted, font=_font(12))
    draw.text((45, 1785), packet["warning"], fill="#33443e", font=_font(10))
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path, format="PNG", optimize=False)


def render_blind_html(packet: dict[str, Any], blind_paths: list[Path], path: Path) -> None:
    pages = "".join(
        f'<section><h2>Page {index:02d}</h2><img src="{escape(item.name)}" alt="Proposal-blinded review page {index:02d}"></section>'
        for index, item in enumerate(blind_paths, start=1)
    )
    document = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>BurnLens proposal-blinded first pass</title><style>
body{{margin:0;background:#f4f0e8;color:#15211d;font:16px/1.55 system-ui,sans-serif}}header{{background:#132a26;color:white;padding:2.5rem max(5vw,2rem)}}header p{{color:#b9d8cf}}main{{max-width:1500px;margin:auto;padding:2rem}}.warning{{background:#fff1ca;border-left:6px solid #d87618;padding:1rem;font-weight:650}}section{{margin:2rem 0}}img{{width:100%;height:auto;border:1px solid #c8c0b2}}code{{overflow-wrap:anywhere}}
</style></head><body><header><p>BurnLens / independent label-review input</p><h1>Proposal-blinded first pass</h1><p>Complete the blank response template before opening any reveal material.</p></header><main>
<p class="warning">{escape(packet['warning'])}</p>
<p>Review the exact pre/post Sentinel imagery, fixed-display continuous dNBR, and NIFC or MTBS source context. The cyan marker identifies one 20 m proposal-grid pixel. Source context is not truth alone.</p>
<p><strong>Packet:</strong> <code>{escape(packet['report_id'])}</code> / <strong>run:</strong> <code>{escape(packet['run_id'])}</code> / <strong>units:</strong> {len(packet['units'])}</p>
{pages}
<p>No sample-specific BurnLens proposed state or binary target is presented in this first-pass document.</p>
</main></body></html>"""
    _write_utf8_lf(path, document)


def render_reveal_html(packet: dict[str, Any], path: Path) -> None:
    rows = "".join(
        f"<tr><td>{escape(unit['sample_id'])}</td><td>{escape(unit['fire_name'])}</td><td>{unit['row']}, {unit['column']}</td><td>{escape(unit['proposal_state'])}</td><td>{'ignore' if unit['proposal_target_value'] is None else unit['proposal_target_value']}</td><td>{unit['dnbr_center']:.6f}</td><td>{unit['reference_context_value']}</td></tr>"
        for unit in packet["units"]
    )
    document = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>BurnLens proposal reveal and adjudication key</title><style>
body{{margin:0;background:#f4f0e8;color:#15211d;font:16px/1.55 system-ui,sans-serif}}header{{background:#132a26;color:white;padding:2.5rem max(5vw,2rem)}}header p{{color:#b9d8cf}}main{{max-width:1400px;margin:auto;padding:2rem}}.warning{{background:#fff1ca;border-left:6px solid #d87618;padding:1rem;font-weight:650}}.card{{background:#fffdf8;border:1px solid #d9d1c4;border-radius:12px;padding:1.2rem;margin:1.2rem 0}}.table{{overflow-x:auto}}table{{width:100%;border-collapse:collapse}}th,td{{padding:.6rem;border-bottom:1px solid #ddd5c9;text-align:left}}code{{overflow-wrap:anywhere}}
</style></head><body><header><p>BurnLens / open only after first-pass response is locked</p><h1>Proposal reveal and adjudication key</h1><p>This page exposes the BurnLens proposal. It is not independent evidence.</p></header><main>
<p class="warning">{escape(packet['warning'])}</p>
<section class="card"><h2>Required order</h2><p>{escape(packet['review_workflow']['reveal'])}</p><p>Opening this page before first-pass completion disqualifies that response from proposal-blinded evidence.</p></section>
<section class="card"><h2>Proposal key</h2><div class="table"><table><thead><tr><th>Sample</th><th>Event</th><th>Row, column</th><th>Proposed state</th><th>Target</th><th>dNBR center</th><th>Source context value</th></tr></thead><tbody>{rows}</tbody></table></div></section>
<section class="card"><h2>Adjudication boundary</h2><ul>{''.join(f'<li>{escape(item)}</li>' for item in packet['predeclared_decision_rule']['minimum_before_dataset_candidacy'])}</ul><p><strong>Current decision:</strong> <code>{escape(packet['decision'])}</code></p></section>
</main></body></html>"""
    _write_utf8_lf(path, document)


def render_summary_html(packet: dict[str, Any], path: Path) -> None:
    coverage_rows = "".join(
        f"<tr><td>{escape(item['event_group_id'])}</td><td>{escape(item['proposal_state'])}</td><td>{item['population_pixels']:,}</td><td>{item['selected_units']}</td><td>{'yes' if item['structural_absence'] else 'no'}</td><td>{'n/a' if item['minimum_selected_separation_m'] is None else str(item['minimum_selected_separation_m']) + ' m'}</td></tr>"
        for item in packet["coverage"]
    )
    sources = "".join(
        f'<li><a href="{escape(item["url"])}">{escape(item["title"])}</a>: {escape(item["use"])}</li>'
        for item in packet["research_basis"]
    )
    document = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>BurnLens label-review readiness</title><style>
:root{{--ink:#15211d;--paper:#f4f0e8;--panel:#fffdf8;--teal:#006b64;--orange:#f05a28}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 system-ui,sans-serif}}header{{background:#132a26;color:white;padding:3rem max(5vw,2rem)}}header p{{color:#b9d8cf}}main{{max-width:1400px;margin:auto;padding:2.5rem 1.5rem 5rem}}.hero{{width:100%;height:auto;border:1px solid #c8c0b2}}.warning{{background:#fff1ca;border-left:6px solid #d87618;padding:1rem 1.2rem;font-weight:650}}.card{{background:var(--panel);border:1px solid #d9d1c4;border-radius:12px;padding:1.2rem;margin:1.2rem 0}}.decision{{border:2px solid var(--orange)}}.metrics{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:.8rem}}.metrics div{{background:#e5efeb;padding:1rem;border-radius:10px}}.metrics strong{{display:block;color:var(--teal);font-size:1.6rem}}.table{{overflow-x:auto}}table{{width:100%;border-collapse:collapse}}th,td{{padding:.6rem;border-bottom:1px solid #ddd5c9;text-align:left}}code{{overflow-wrap:anywhere}}
</style></head><body><header><p>BurnLens / Phase Two / Objective Four</p><h1>Label-review readiness</h1><p>Exact three-event source evidence, a proposal-blinded first pass, and explicit dataset deferral.</p></header><main>
<p class="warning">{escape(packet['warning'])}</p><img class="hero" src="{REPORT_ID}.png" alt="BurnLens label-review readiness evidence">
<section class="card decision"><h2>Decision</h2><p><strong>{escape(packet['decision'])}</strong></p><p>{escape(packet['decision_detail'])}</p></section>
<section class="card"><h2>Review surfaces</h2><p><a href="{REPORT_ID}-BLIND.html">Open proposal-blinded first pass</a> / <a href="{REPORT_ID}-REVEAL.html">Open proposal reveal only after response lock</a> / <a href="{REPORT_ID}-RESPONSE-TEMPLATE.json">Blank response template</a> / <a href="{REPORT_ID}-ADJUDICATION-TEMPLATE.json">Blank adjudication template</a></p></section>
<section class="card"><h2>Coverage</h2><div class="metrics"><div><strong>{packet['coverage_summary']['selected_units']}</strong><span>review units</span></div><div><strong>{packet['coverage_summary']['strata_present']}</strong><span>present strata</span></div><div><strong>{packet['coverage_summary']['strata_structurally_absent']}</strong><span>structural absences</span></div><div><strong>0</strong><span>independent responses</span></div></div><div class="table"><table><thead><tr><th>Event</th><th>Proposal state</th><th>Population</th><th>Selected</th><th>Absent</th><th>Minimum separation</th></tr></thead><tbody>{coverage_rows}</tbody></table></div></section>
<section class="card"><h2>Predeclared boundary</h2><h3>Before adjudication</h3><ul>{''.join(f'<li>{escape(item)}</li>' for item in packet['predeclared_decision_rule']['minimum_before_adjudication'])}</ul><h3>Before dataset candidacy</h3><ul>{''.join(f'<li>{escape(item)}</li>' for item in packet['predeclared_decision_rule']['minimum_before_dataset_candidacy'])}</ul></section>
<section class="card"><h2>Research basis</h2><ul>{sources}</ul><p>The sources inform the protocol. They do not turn this bounded portfolio packet into a representative accuracy assessment.</p></section>
<section class="card"><h2>Traceability and boundaries</h2><p><strong>Run:</strong> <code>{escape(packet['run_id'])}</code><br><strong>Git source:</strong> <code>{escape(packet['git_source_commit'])}</code><br><strong>Software / review protocol / response schema:</strong> <code>{escape(packet['software_version'])}</code> / <code>{escape(packet['review_protocol_version'])}</code> / <code>{escape(packet['response_schema_version'])}</code><br><strong>Dataset / split / baseline / model:</strong> none / none / none / none</p><ul>{''.join(f'<li><strong>Not proven:</strong> {escape(item)}</li>' for item in packet['claims']['not_proven'])}</ul><p>{escape(packet['attribution'])}</p></section>
</main></body></html>"""
    _write_utf8_lf(path, document)


def _output_metadata(paths: list[Path], base: Path) -> list[dict[str, Any]]:
    outputs = []
    for path in paths:
        outputs.append(
            {
                "path": path.relative_to(base).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": _sha256_file(path),
            }
        )
    return outputs


def write_packet(
    *,
    packet: dict[str, Any],
    events: list[dict[str, Any]],
    units: list[dict[str, Any]],
    response: dict[str, Any],
    adjudication: dict[str, Any],
    output_directory: Path,
) -> dict[str, Path]:
    output_directory.mkdir(parents=True, exist_ok=True)
    paths = {
        "json": output_directory / f"{REPORT_ID}.json",
        "html": output_directory / f"{REPORT_ID}.html",
        "png": output_directory / f"{REPORT_ID}.png",
        "blind_html": output_directory / f"{REPORT_ID}-BLIND.html",
        "reveal_html": output_directory / f"{REPORT_ID}-REVEAL.html",
        "response_template": output_directory / f"{REPORT_ID}-RESPONSE-TEMPLATE.json",
        "adjudication_template": output_directory
        / f"{REPORT_ID}-ADJUDICATION-TEMPLATE.json",
    }
    blind_paths = render_blind_pages(events, units, output_directory)
    render_summary_png(packet, events, units, paths["png"])
    render_blind_html(packet, blind_paths, paths["blind_html"])
    render_reveal_html(packet, paths["reveal_html"])
    render_summary_html(packet, paths["html"])
    _write_utf8_lf(paths["response_template"], json.dumps(response, indent=2) + "\n")
    _write_utf8_lf(paths["adjudication_template"], json.dumps(adjudication, indent=2) + "\n")
    non_json_outputs = [
        paths["html"],
        paths["png"],
        paths["blind_html"],
        paths["reveal_html"],
        paths["response_template"],
        paths["adjudication_template"],
        *blind_paths,
    ]
    packet["outputs"] = {
        "files": _output_metadata(non_json_outputs, output_directory),
        "blind_page_count": len(blind_paths),
        "response_template_contains_proposal_values": False,
        "adjudication_template_contains_proposal_values": False,
    }
    _write_utf8_lf(paths["json"], json.dumps(packet, indent=2) + "\n")
    paths["blind_pages"] = blind_paths[0].parent
    return paths
