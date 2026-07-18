"""Build a no-promotion contiguous-region candidate pilot from exact evidence.

The pilot creates review candidates, not labels. Private owner-response mappings
remain in ignored storage; public artifacts expose only new candidate IDs and
aggregate, source-bound evidence.
"""

from __future__ import annotations

from collections import Counter, deque
from hashlib import sha256
from html import escape
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import rasterio
from rasterio.transform import Affine

from .cross_event_label_transfer import build_report as build_cross_event_report
from .label_proposal import STATE_CODES, STATE_NAMES, build_proposal, dilate_mask


SOFTWARE_VERSION = "0.29.0"
REPORT_ID = "REGION-CANDIDATE-PILOT-2026-001"
REPORT_VERSION = "no-promotion-region-candidate-pilot-v0.1.0"
GENERATOR_VERSION = "region-candidate-generator-v0.1.0"
REVIEW_PROTOCOL_VERSION = "owner-confirmed-contiguous-region-review-v0.1.0"
LABEL_SET_VERSION = "owner-approved-prototype-labels-v0.1.0"
LABEL_SCHEMA_VERSION = "burn-scar-five-state-schema-v0.1.0"
TARGET_VERSION = "target-burn-scar-v0.2.0"
TASK_ISSUE = 453
DNBR_BIN_WIDTH = 0.05
DNBR_OFFSET = 2.0
TARGET_REVIEW_PIXELS = 25
MIN_CORE_PIXELS = 2
MAX_CORE_PIXELS = 250
PIXEL_AREA_HA = 0.04
EVENT_ORDER = (
    "event-darlene3-or-2024",
    "event-mckay-1035-ne-2017",
    "event-tepee-1144-ne-2018",
)
CLASS_ORDER = ("background", "burned")
WARNING = (
    "Experimental BurnLens candidate evidence. Not a label, dataset, ground truth, "
    "official wildfire information, or emergency guidance. Official sources govern."
)


class RegionCandidatePilotError(RuntimeError):
    """A deterministic, secret-safe pilot failure."""


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    return ImageFont.load_default(size=size)


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _binding(path: Path, **extra: Any) -> dict[str, Any]:
    value = {"path": path.name, "bytes": path.stat().st_size, "sha256": _sha256_file(path)}
    value.update(extra)
    return value


def _write_json(path: Path, value: dict[str, Any]) -> None:
    if path.exists():
        raise RegionCandidatePilotError(f"refusing to overwrite {path.name}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")


def _component(mask: np.ndarray, row: int, column: int) -> np.ndarray:
    if mask.ndim != 2 or not (0 <= row < mask.shape[0] and 0 <= column < mask.shape[1]):
        raise RegionCandidatePilotError("seed lies outside its native grid")
    output = np.zeros(mask.shape, dtype=bool)
    if not bool(mask[row, column]):
        return output
    output[row, column] = True
    queue: deque[tuple[int, int]] = deque([(row, column)])
    height, width = mask.shape
    while queue:
        current_row, current_column = queue.popleft()
        for delta_row in (-1, 0, 1):
            for delta_column in (-1, 0, 1):
                if not (delta_row or delta_column):
                    continue
                next_row = current_row + delta_row
                next_column = current_column + delta_column
                if (
                    0 <= next_row < height
                    and 0 <= next_column < width
                    and bool(mask[next_row, next_column])
                    and not bool(output[next_row, next_column])
                ):
                    output[next_row, next_column] = True
                    queue.append((next_row, next_column))
    return output


def _bbox(mask: np.ndarray) -> list[int]:
    rows, columns = np.where(mask)
    if not len(rows):
        raise RegionCandidatePilotError("candidate mask is empty")
    return [int(rows.min()), int(columns.min()), int(rows.max()) + 1, int(columns.max()) + 1]


def _touches_edge(mask: np.ndarray) -> bool:
    return bool(mask[0, :].any() or mask[-1, :].any() or mask[:, 0].any() or mask[:, -1].any())


def _candidate_from_seed(event: dict[str, Any], unit: dict[str, Any]) -> dict[str, Any]:
    row = int(unit["row"])
    column = int(unit["column"])
    expected_state = STATE_CODES["burned" if unit["candidate_label"] == "burned" else "background-candidate"]
    states = event["states"]
    if int(states[row, column]) != expected_state:
        raise RegionCandidatePilotError("approved seed no longer matches its frozen proposal state")
    dnbr = event["dnbr"]
    seed_dnbr = float(dnbr[row, column])
    if not math.isfinite(seed_dnbr):
        raise RegionCandidatePilotError("approved seed has invalid dNBR evidence")
    bucket = math.floor((seed_dnbr + DNBR_OFFSET) / DNBR_BIN_WIDTH)
    binned = np.floor((dnbr + DNBR_OFFSET) / DNBR_BIN_WIDTH) == bucket
    reference_value = int(event["reference"][row, column])
    growth_mask = (
        (states == expected_state)
        & event["eligible"]
        & np.isfinite(dnbr)
        & binned
        & (event["reference"] == reference_value)
    )
    core = _component(growth_mask, row, column)
    ring = dilate_mask(core, 1) & ~core
    core_pixels = int(core.sum())
    ring_pixels = int(ring.sum())
    box = _bbox(core)
    values = dnbr[core]
    return {
        "sample_id": unit["sample_id"],
        "event_group_id": unit["event_group_id"],
        "candidate_class": unit["candidate_label"],
        "seed_row": row,
        "seed_column": column,
        "reference_value": reference_value,
        "dnbr_bucket": bucket,
        "dnbr_interval": [
            round(bucket * DNBR_BIN_WIDTH - DNBR_OFFSET, 6),
            round((bucket + 1) * DNBR_BIN_WIDTH - DNBR_OFFSET, 6),
        ],
        "core": core,
        "ring": ring,
        "core_pixels": core_pixels,
        "ring_pixels": ring_pixels,
        "bbox": box,
        "extent_rows": box[2] - box[0],
        "extent_columns": box[3] - box[1],
        "dnbr_min": round(float(values.min()), 6),
        "dnbr_max": round(float(values.max()), 6),
        "dnbr_mean": round(float(values.mean()), 6),
        "touches_grid_edge": _touches_edge(core),
        "selection_distance_pixels": abs(core_pixels - TARGET_REVIEW_PIXELS),
        "selection_tie_hash": sha256(unit["selection_hash"].encode("ascii")).hexdigest(),
    }


def select_candidates(
    approved_units: list[dict[str, Any]], event_arrays: dict[str, dict[str, Any]]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Select one intact component per event/class and return private audit rows."""
    candidates: list[dict[str, Any]] = []
    audit: list[dict[str, Any]] = []
    for event_id in EVENT_ORDER:
        if event_id not in event_arrays:
            raise RegionCandidatePilotError(f"missing event arrays: {event_id}")
        for candidate_class in CLASS_ORDER:
            units = [
                unit
                for unit in approved_units
                if unit["event_group_id"] == event_id and unit["candidate_label"] == candidate_class
            ]
            if not units:
                raise RegionCandidatePilotError(f"missing approved {event_id} {candidate_class} seeds")
            evaluated = [_candidate_from_seed(event_arrays[event_id], unit) for unit in units]
            for item in evaluated:
                item["eligible_for_pilot"] = (
                    MIN_CORE_PIXELS <= item["core_pixels"] <= MAX_CORE_PIXELS
                    and item["ring_pixels"] > 0
                    and not item["touches_grid_edge"]
                )
                audit.append(item)
            eligible = [item for item in evaluated if item["eligible_for_pilot"]]
            if not eligible:
                raise RegionCandidatePilotError(f"no reviewable {event_id} {candidate_class} component")
            selected = min(
                eligible,
                key=lambda item: (item["selection_distance_pixels"], item["selection_tie_hash"]),
            )
            candidates.append(selected)

    for index, item in enumerate(candidates, start=1):
        item["candidate_id"] = f"RCP-{index:03d}"

    for left_index, left in enumerate(candidates):
        for right in candidates[left_index + 1 :]:
            if left["event_group_id"] != right["event_group_id"]:
                continue
            if np.any((left["core"] | left["ring"]) & (right["core"] | right["ring"])):
                raise RegionCandidatePilotError("selected candidate regions overlap")
    return candidates, audit


def _approved_units(private: dict[str, Any], surface: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if private.get("label_set_version") != LABEL_SET_VERSION:
        raise RegionCandidatePilotError("private label-set version changed")
    if surface.get("report_id") != "OWNER-REVIEW-SURFACE-2026-001":
        raise RegionCandidatePilotError("owner surface identity changed")
    surface_units = {unit["sample_id"]: unit for unit in surface.get("units", [])}
    approved_private = [
        unit
        for unit in private.get("units", [])
        if unit.get("disposition") == "ELIGIBLE_OWNER_APPROVED_PROTOTYPE_LABEL"
    ]
    if len(approved_private) != 24:
        raise RegionCandidatePilotError("expected exactly 24 approved prototype seeds")
    approved: list[dict[str, Any]] = []
    for item in approved_private:
        public = surface_units.get(item["sample_id"])
        if public is None:
            raise RegionCandidatePilotError("approved seed is absent from the frozen surface")
        if item.get("prototype_target") != (1 if public["candidate_label"] == "burned" else 0):
            raise RegionCandidatePilotError("private/public candidate direction mismatch")
        approved.append(public)
    return approved, approved_private


def load_actual_event_arrays(repository_root: Path, scratch_directory: Path, generated_at_utc: str, run_id: str, git_source_commit: str) -> dict[str, dict[str, Any]]:
    if scratch_directory.exists():
        raise RegionCandidatePilotError("scratch directory already exists")
    darlene_report, darlene, darlene_transform = build_proposal(
        package=repository_root / "downloads/phase-two/raw/darlene3-s2-optical-pair-v0.1.0",
        aoi_report_path=repository_root / "samples/aoi/phase-two/AOI-FINAL-2026-001.json",
        reference_geojson_path=repository_root / "samples/reference/phase-two/NIFC-DARLENE3-PERIMETER-2026-001.geojson",
        optical_report_path=repository_root / "samples/optical/phase-two/OPTICAL-PAIR-2026-001.json",
        registration_report_path=repository_root / "samples/registration/phase-two/CONTENT-REGISTRATION-2026-001.json",
        generated_at_utc=generated_at_utc,
        run_id=f"{run_id}-darlene-rebuild",
        git_source_commit=git_source_commit,
    )
    cross_report, visuals = build_cross_event_report(
        optical_package=repository_root / "downloads/phase-two/raw/burnlens-cross-event-optical-package-v0.1.0",
        mtbs_package=repository_root / "downloads/mtbs-cross-event-reference-v0.1.0",
        feasibility_report_path=repository_root / "samples/cross-event/phase-two/CROSS-EVENT-FITNESS-2026-001.json",
        source_fitness_report_path=repository_root / "samples/cross-event/phase-two/CROSS-EVENT-SOURCE-FITNESS-2026-001.json",
        output_directory=scratch_directory,
        generated_at_utc=generated_at_utc,
        run_id=f"{run_id}-cross-rebuild",
        git_source_commit=git_source_commit,
    )
    events: dict[str, dict[str, Any]] = {
        "event-darlene3-or-2024": {
            "event_group_id": "event-darlene3-or-2024",
            "fire_name": "Darlene 3",
            "pre_tci": darlene["pre_tci"],
            "post_tci": darlene["post_tci"],
            "states": darlene["states"],
            "dnbr": darlene["dnbr"],
            "reference": darlene["reference_mask"].astype(np.uint8),
            "reference_kind": "NIFC incident-reference context",
            "eligible": np.isin(darlene["states"], [STATE_CODES["background-candidate"], STATE_CODES["burned"]]),
            "transform": darlene_transform,
            "crs": "EPSG:32610",
            "source_report_id": darlene_report["report_id"],
        }
    }
    cross_by_id = {item["event_group_id"]: item for item in cross_report["events"]}
    for visual in visuals:
        event_id = visual["event_group_id"]
        event_report = cross_by_id[event_id]
        events[event_id] = {
            "event_group_id": event_id,
            "fire_name": visual["fire_name"],
            "pre_tci": visual["pre_tci"],
            "post_tci": visual["post_tci"],
            "states": visual["states"],
            "dnbr": visual["dnbr"],
            "reference": visual["mtbs"].astype(np.uint8),
            "reference_kind": "MTBS thematic context",
            "eligible": (visual["pair_quality"] == 0) & (visual["registration_state"] == 0),
            "transform": Affine(*event_report["grid"]["transform"]),
            "crs": event_report["grid"]["crs"],
            "source_report_id": cross_report["report_id"],
        }
    return events


def _public_candidate(item: dict[str, Any], event: dict[str, Any], raster_name: str) -> dict[str, Any]:
    ring_states = Counter(STATE_NAMES[int(value)] for value in event["states"][item["ring"]])
    return {
        "candidate_id": item["candidate_id"],
        "event_group_id": item["event_group_id"],
        "fire_name": event["fire_name"],
        "candidate_class": item["candidate_class"],
        "review_state": "unreviewed-no-promotion",
        "core_pixels": item["core_pixels"],
        "core_area_ha": round(item["core_pixels"] * PIXEL_AREA_HA, 4),
        "unknown_ring_pixels": item["ring_pixels"],
        "extent_pixels": {"rows": item["extent_rows"], "columns": item["extent_columns"]},
        "dnbr_interval": item["dnbr_interval"],
        "dnbr_observed": {"min": item["dnbr_min"], "max": item["dnbr_max"], "mean": item["dnbr_mean"]},
        "reference_context": {"kind": event["reference_kind"], "value": item["reference_value"]},
        "unknown_ring_source_state_counts": {name: ring_states[name] for name in sorted(ring_states)},
        "candidate_raster": raster_name,
        "seed_identity_and_position": "withheld in ignored private mapping",
        "owner_region_decision": None,
    }


def build_pilot_report(
    *, repository_root: Path, private_intake_path: Path, scratch_directory: Path,
    generated_at_utc: str, run_id: str, git_source_commit: str,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], dict[str, dict[str, Any]], dict[str, Any]]:
    surface_path = repository_root / "samples/labels/review/phase-two/OWNER-REVIEW-SURFACE-2026-001.json"
    surface = json.loads(surface_path.read_text(encoding="utf-8"))
    private = json.loads(private_intake_path.read_text(encoding="utf-8"))
    approved, approved_private = _approved_units(private, surface)
    events = load_actual_event_arrays(repository_root, scratch_directory, generated_at_utc, run_id, git_source_commit)
    selected, audit = select_candidates(approved, events)
    public_candidates = [
        _public_candidate(
            item,
            events[item["event_group_id"]],
            f"{REPORT_ID}-{item['candidate_id']}.tif",
        )
        for item in selected
    ]
    report: dict[str, Any] = {
        "report_id": REPORT_ID,
        "report_version": REPORT_VERSION,
        "generator_version": GENERATOR_VERSION,
        "review_protocol_version": REVIEW_PROTOCOL_VERSION,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": TASK_ISSUE,
        "git_source_commit": git_source_commit,
        "software_version": SOFTWARE_VERSION,
        "aoi_version": "multi-event-native-grids-v0.1.0",
        "target_version": TARGET_VERSION,
        "label_schema_version": LABEL_SCHEMA_VERSION,
        "input_label_set_version": LABEL_SET_VERSION,
        "output_label_set_version": None,
        "dataset_version": None,
        "split_version": None,
        "baseline_version": None,
        "model_version": None,
        "input_bindings": {
            "owner_surface": {"bytes": surface_path.stat().st_size, "sha256": _sha256_file(surface_path)},
            "private_approved_seed_intake": {"bytes": private_intake_path.stat().st_size, "sha256": _sha256_file(private_intake_path), "path_public": False},
            "darlene_proposal": {"sha256": _sha256_file(repository_root / "samples/labels/phase-two/LABEL-PROPOSAL-2026-001.json")},
            "cross_event_proposal": {"sha256": _sha256_file(repository_root / "samples/labels/cross-event/phase-two/CROSS-EVENT-LABEL-TRANSFER-2026-002.json")},
            "region_plan": {"sha256": _sha256_file(repository_root / "samples/labels/readiness/phase-two/LABEL-REGION-REMEDIATION-PLAN-2026-001.json")},
        },
        "source_records": ["SOURCE-2026-007", "SOURCE-2026-010", "SOURCE-2026-018"],
        "terms_records": ["TERMS-2026-003", "TERMS-2026-005", "TERMS-2026-013"],
        "method": {
            "unit": "one intact 8-connected native-grid component",
            "growth": "same frozen five-state class, eligible quality/registration state, exact categorical reference context, and fixed 0.05 dNBR bin",
            "dnbr_bin_width": DNBR_BIN_WIDTH,
            "review_selection_target_pixels": TARGET_REVIEW_PIXELS,
            "review_selection_target_area_ha": TARGET_REVIEW_PIXELS * PIXEL_AREA_HA,
            "selection_scope": "target chooses among intact eligible components only; it never clips or expands a component",
            "core_pixel_gate": [MIN_CORE_PIXELS, MAX_CORE_PIXELS],
            "unknown_ring": "exactly one native pixel around the intact core",
            "overlap": "any selected core/ring overlap fails the run; no pixel is reassigned",
            "presentation_crop": "display-only padding around the complete core/ring; not part of candidate generation",
        },
        "summary": {
            "approved_seed_count_private": len(approved_private),
            "event_count": len(EVENT_ORDER),
            "candidate_count": len(public_candidates),
            "candidates_per_event": 2,
            "candidate_class_counts": {candidate_class: 3 for candidate_class in CLASS_ORDER},
            "core_pixels": sum(item["core_pixels"] for item in public_candidates),
            "unknown_ring_pixels": sum(item["unknown_ring_pixels"] for item in public_candidates),
            "owner_region_responses": 0,
            "owner_approved_region_labels": 0,
        },
        "candidates": public_candidates,
        "quality_gates": {
            "exact_raw_packages_reverified": True,
            "actual_native_optical_pixels_opened": True,
            "actual_reference_pixels_opened": True,
            "every_event_and_class_represented": len(public_candidates) == 6,
            "components_intact_not_clipped": True,
            "one_pixel_unknown_rings": True,
            "selected_regions_nonoverlapping": True,
            "private_seed_mapping_public": False,
            "owner_region_responses_collected": False,
            "region_labels_promoted": False,
            "dataset_created": False,
            "split_created": False,
            "baseline_created": False,
            "model_created": False,
        },
        "decision": "PILOT_REGION_CANDIDATES_REVIEWABLE_KEEP_PROMOTION_CLOSED",
        "next_gate": "Validate rendered/runtime and exact reconstruction; only a later separately versioned owner-review surface may collect yes/no/uncertain decisions.",
        "limitations": [
            "The 0.05 dNBR partition is a frozen pilot evidence-coherence parameter, not a universal burn or severity threshold.",
            "The one-hectare target affects seed selection only and has no label or ecological meaning.",
            "The same historical proposal logic helps define and display these regions; this is not independent ground truth.",
            "Only three events are represented, so event diversity and dataset fitness remain blocked.",
            "Candidate evidence may still be rejected or marked uncertain by the owner in a later workflow.",
        ],
        "claim_boundaries": {
            "owner_region_responses": 0,
            "region_labels_created": False,
            "dataset_created": False,
            "split_created": False,
            "baseline_created": False,
            "model_created": False,
            "accuracy_ground_truth_inter_rater_field_official_or_operational_claimed": False,
        },
        "attribution": [
            "Contains modified Copernicus Sentinel data 2017, 2018, and 2024.",
            "NIFC WFIGS and MTBS reference evidence remains contextual and is not pixel-perfect truth.",
        ],
        "warning": WARNING,
    }
    private_mapping = {
        "report_id": f"{REPORT_ID}-PRIVATE-SEED-MAPPING",
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "git_source_commit": git_source_commit,
        "public_path": False,
        "private_intake_binding": report["input_bindings"]["private_approved_seed_intake"],
        "selected": [
            {
                "candidate_id": item["candidate_id"],
                "sample_id": item["sample_id"],
                "event_group_id": item["event_group_id"],
                "candidate_class": item["candidate_class"],
                "seed_row": item["seed_row"],
                "seed_column": item["seed_column"],
            }
            for item in selected
        ],
        "audit": [
            {
                "sample_id": item["sample_id"],
                "event_group_id": item["event_group_id"],
                "candidate_class": item["candidate_class"],
                "core_pixels": item["core_pixels"],
                "ring_pixels": item["ring_pixels"],
                "eligible_for_pilot": item["eligible_for_pilot"],
                "selection_distance_pixels": item["selection_distance_pixels"],
            }
            for item in audit
        ],
    }
    return report, selected, audit, events, private_mapping


def _overlay(image: Image.Image, core: np.ndarray, ring: np.ndarray, candidate_class: str) -> Image.Image:
    base = image.convert("RGBA")
    layer = np.zeros((core.shape[0], core.shape[1], 4), dtype=np.uint8)
    core_color = (0, 130, 122, 150) if candidate_class == "background" else (240, 90, 40, 150)
    layer[core] = core_color
    layer[ring] = (240, 190, 70, 165)
    return Image.alpha_composite(base, Image.fromarray(layer, mode="RGBA"))


def _dnbr_image(values: np.ndarray) -> Image.Image:
    clipped = np.clip((values + 0.2) / 1.0, 0.0, 1.0)
    red = (255 * clipped).astype(np.uint8)
    blue = (255 * (1.0 - clipped)).astype(np.uint8)
    green = (150 * (1.0 - np.abs(clipped - 0.5) * 2)).astype(np.uint8)
    return Image.fromarray(np.dstack([red, green, blue]), mode="RGB")


def _reference_image(values: np.ndarray, kind: str) -> Image.Image:
    if kind.startswith("NIFC"):
        rgb = np.where(values[..., None] > 0, np.array([240, 90, 40], dtype=np.uint8), np.array([70, 82, 78], dtype=np.uint8))
    else:
        palette = np.array([
            [92, 102, 96], [188, 191, 100], [238, 199, 90], [236, 133, 63],
            [186, 62, 48], [92, 151, 91], [45, 45, 45], [30, 30, 30],
        ], dtype=np.uint8)
        rgb = palette[np.clip(values.astype(np.int16), 0, 7)]
    return Image.fromarray(rgb.astype(np.uint8), mode="RGB")


def _tci_image(values: np.ndarray) -> Image.Image:
    if values.ndim != 3 or values.shape[0] != 3:
        raise RegionCandidatePilotError("Sentinel TCI is not a three-band band-first array")
    return Image.fromarray(np.moveaxis(values, 0, 2).astype(np.uint8), mode="RGB")


def _panel(source: Image.Image, core: np.ndarray, ring: np.ndarray, box: list[int], candidate_class: str, size: tuple[int, int]) -> Image.Image:
    top, left, bottom, right = box
    padding = 5
    top = max(0, top - padding)
    left = max(0, left - padding)
    bottom = min(core.shape[0], bottom + padding)
    right = min(core.shape[1], right + padding)
    overlaid = _overlay(source, core, ring, candidate_class)
    return overlaid.crop((left, top, right, bottom)).resize(size, Image.Resampling.NEAREST).convert("RGB")


def render_png(report: dict[str, Any], selected: list[dict[str, Any]], events: dict[str, dict[str, Any]], path: Path) -> None:
    width = 1800
    row_height = 285
    image = Image.new("RGB", (width, 250 + row_height * len(selected)), "#f3efe5")
    draw = ImageDraw.Draw(image)
    draw.text((55, 35), "BurnLens no-promotion contiguous-region candidate pilot", fill="#123f3a", font=_font(30))
    draw.text((55, 82), "Actual native optical and official reference context / 6 unreviewed candidates / 0 labels", fill="#7f3524", font=_font(18))
    draw.text((55, 120), WARNING, fill="#7f3524", font=_font(15))
    draw.rectangle((55, 170, 85, 200), fill="#00827a")
    draw.text((95, 175), "background core", fill="#123f3a", font=_font(14))
    draw.rectangle((270, 170, 300, 200), fill="#f05a28")
    draw.text((310, 175), "burned core", fill="#123f3a", font=_font(14))
    draw.rectangle((460, 170, 490, 200), fill="#f0be46")
    draw.text((500, 175), "one-pixel unknown ring", fill="#123f3a", font=_font(14))
    labels = ("pre optical", "post optical", "dNBR", "official reference context")
    for index, item in enumerate(selected):
        event = events[item["event_group_id"]]
        top = 230 + index * row_height
        fill = "#ffffff" if index % 2 == 0 else "#e7eee9"
        draw.rounded_rectangle((45, top, width - 45, top + row_height - 15), radius=14, fill=fill, outline="#b6c5bd")
        draw.text((65, top + 18), f"{item['candidate_id']} / {event['fire_name']} / proposed {item['candidate_class']}", fill="#123f3a", font=_font(19))
        draw.text((65, top + 50), f"core {item['core_pixels']} px ({item['core_pixels'] * PIXEL_AREA_HA:.2f} ha) / ring {item['ring_pixels']} px / dNBR [{item['dnbr_interval'][0]:.2f}, {item['dnbr_interval'][1]:.2f})", fill="#42534d", font=_font(14))
        sources = (
            _tci_image(event["pre_tci"]),
            _tci_image(event["post_tci"]),
            _dnbr_image(event["dnbr"]),
            _reference_image(event["reference"], event["reference_kind"]),
        )
        panel_width, panel_height = 360, 165
        for panel_index, (label, source) in enumerate(zip(labels, sources, strict=True)):
            left = 65 + panel_index * 425
            panel = _panel(source, item["core"], item["ring"], item["bbox"], item["candidate_class"], (panel_width, panel_height))
            image.paste(panel, (left, top + 82))
            draw.text((left, top + 252), label, fill="#42534d", font=_font(13))
    image.save(path, format="PNG", optimize=False)


def render_html(report: dict[str, Any]) -> str:
    rows = "".join(
        f"<tr><td>{escape(item['candidate_id'])}</td><td>{escape(item['fire_name'])}</td><td>{escape(item['candidate_class'])}</td><td>{item['core_pixels']}</td><td>{item['core_area_ha']:.2f}</td><td>{item['unknown_ring_pixels']}</td><td>[{item['dnbr_interval'][0]:.2f}, {item['dnbr_interval'][1]:.2f})</td><td><a href=\"{escape(item['candidate_raster'])}\">candidate raster</a></td></tr>"
        for item in report["candidates"]
    )
    limitations = "".join(f"<li>{escape(item)}</li>" for item in report["limitations"])
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>BurnLens Region Candidate Pilot</title>
<style>body{{margin:0;background:#f3efe5;color:#123f3a;font:16px/1.5 Arial,sans-serif}}header,main{{max-width:1180px;margin:auto;padding:28px}}header{{background:#123f3a;color:white;max-width:none}}header div{{max-width:1180px;margin:auto}}.warning{{background:#fff4d2;border-left:6px solid #f05a28;padding:16px}}.hero{{width:100%;height:auto;border:1px solid #b6c5bd}}.metrics{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}}.metric,.card{{background:white;border:1px solid #c7d2cc;border-radius:10px;padding:16px}}.metric strong{{display:block;font-size:1.7rem}}.table{{overflow-x:auto}}table{{border-collapse:collapse;width:100%;background:white}}th,td{{padding:10px;border:1px solid #c7d2cc;text-align:left}}code{{overflow-wrap:anywhere}}@media(max-width:700px){{.metrics{{grid-template-columns:1fr 1fr}}header,main{{padding:18px}}}}</style></head>
<body><header><div><p>BurnLens / Phase Two / Objective Four</p><h1>No-promotion contiguous-region candidate pilot</h1><p>Actual optical and reference evidence for intact native-grid review candidates.</p></div></header><main>
<p class="warning">{escape(report['warning'])}</p>
<div class="metrics"><div class="metric"><strong>6</strong>unreviewed candidates</div><div class="metric"><strong>3</strong>immutable events</div><div class="metric"><strong>0</strong>region labels</div><div class="metric"><strong>0</strong>datasets / models</div></div>
<h2>Rendered evidence</h2><img class="hero" src="{REPORT_ID}.png" alt="Six candidate rows show pre and post optical imagery, dNBR, official reference context, intact candidate cores, and one-pixel unknown rings">
<h2>Candidate inventory</h2><div class="table"><table><thead><tr><th>ID</th><th>Event</th><th>Proposed class</th><th>Core px</th><th>Core ha</th><th>Ring px</th><th>dNBR bin</th><th>Output</th></tr></thead><tbody>{rows}</tbody></table></div>
<section class="card"><h2>Frozen generator</h2><p>{escape(report['method']['growth'])}. The one-hectare target selects among intact components only; it never clips or expands them. Any overlap or grid-edge truncation fails closed.</p><p>Generator <code>{escape(report['generator_version'])}</code> / run <code>{escape(report['run_id'])}</code> / source <code>{escape(report['git_source_commit'])}</code>.</p></section>
<section class="card"><h2>Decision</h2><p><strong>{escape(report['decision'])}</strong></p><p>{escape(report['next_gate'])}</p></section>
<section class="card"><h2>Limitations</h2><ul>{limitations}</ul></section>
</main></body></html>"""


def _write_candidate_raster(path: Path, item: dict[str, Any], event: dict[str, Any], run_id: str, git_source_commit: str) -> None:
    if path.exists():
        raise RegionCandidatePilotError(f"refusing to overwrite {path.name}")
    array = np.zeros(item["core"].shape, dtype=np.uint8)
    array[item["core"]] = 1
    array[item["ring"]] = 2
    with rasterio.open(
        path, "w", driver="GTiff", width=array.shape[1], height=array.shape[0], count=1,
        dtype="uint8", crs=event["crs"], transform=event["transform"], nodata=255,
        compress="DEFLATE", predictor=2,
    ) as dataset:
        dataset.write(array, 1)
        dataset.update_tags(
            candidate_id=item["candidate_id"], event_group_id=item["event_group_id"],
            proposed_class=item["candidate_class"], kind="unreviewed-region-candidate-core-and-unknown-ring",
            generator_version=GENERATOR_VERSION, run_id=run_id, git_source_commit=git_source_commit,
            region_label_created="false", dataset_created="false",
        )


def write_pilot_outputs(
    *, report: dict[str, Any], selected: list[dict[str, Any]], events: dict[str, dict[str, Any]],
    private_mapping: dict[str, Any], output_directory: Path, private_mapping_path: Path,
) -> list[dict[str, Any]]:
    if output_directory.exists():
        raise RegionCandidatePilotError("output directory already exists")
    output_directory.mkdir(parents=True)
    outputs: list[dict[str, Any]] = []
    for item in selected:
        path = output_directory / f"{REPORT_ID}-{item['candidate_id']}.tif"
        _write_candidate_raster(path, item, events[item["event_group_id"]], report["run_id"], report["git_source_commit"])
        outputs.append(_binding(path, media_type="image/tiff", candidate_id=item["candidate_id"]))
    png_path = output_directory / f"{REPORT_ID}.png"
    html_path = output_directory / f"{REPORT_ID}.html"
    json_path = output_directory / f"{REPORT_ID}.json"
    render_png(report, selected, events, png_path)
    html_path.write_text(render_html(report), encoding="utf-8", newline="\n")
    outputs.extend([
        _binding(html_path, media_type="text/html"),
        _binding(png_path, media_type="image/png"),
    ])
    report["outputs"] = outputs
    _write_json(json_path, report)
    private_mapping["public_report_binding"] = _binding(json_path, media_type="application/json")
    _write_json(private_mapping_path, private_mapping)
    return [_binding(json_path, media_type="application/json"), *outputs]
