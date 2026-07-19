"""Fail-closed intake for the exact six-candidate owner region response."""

from __future__ import annotations

from collections import Counter, deque
from datetime import datetime
from hashlib import sha256
from html import escape
import json
import os
from pathlib import Path
import subprocess
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import rasterio

import burnlens
from .region_owner_review_surface import (
    ALLOWED_DECISIONS,
    EXPECTED_PILOT_RUN,
    EXPECTED_PILOT_SHA256,
    PILOT_ID,
    PILOT_REPORT_VERSION,
    RESPONSE_SCHEMA_VERSION,
    SURFACE_ID,
    SURFACE_VERSION,
)


REPORT_ID = "REGION-OWNER-RESPONSE-INTAKE-2026-001"
REPORT_VERSION = "region-owner-response-intake-v0.1.0"
PRIVATE_REPORT_VERSION = "region-owner-response-private-reconciliation-v0.1.0"
LOCK_VERSION = "region-owner-response-exact-byte-lock-v0.1.0"
LABEL_SET_VERSION = "owner-approved-prototype-region-labels-v0.1.0"
LABEL_SCHEMA_VERSION = "burn-scar-five-state-schema-v0.1.0"
AOI_VERSION = "multi-event-native-grids-v0.1.0"
TARGET_VERSION = "target-burn-scar-v0.2.0"
TASK_ISSUE = 461
MINIMUM_EVENT_GROUPS = 6
TERMS_RECORDS = (
    "TERMS-2026-003",
    "TERMS-2026-005",
    "TERMS-2026-013",
    "TERMS-2026-014",
)
SOURCE_RECORDS = ("SOURCE-2026-007", "SOURCE-2026-010", "SOURCE-2026-018")
REVIEW_RECORDS = (
    "PRECHECK-2026-030",
    "LABEL-FITNESS-2026-018",
    "SOURCE-PRECEDENCE-2026-014",
    "USE-BOUNDARY-2026-028",
)
WARNING = (
    "Experimental BurnLens owner-approved prototype region labels. Not ground truth, "
    "official wildfire information, emergency guidance, or a dataset. Official sources govern."
)


class RegionOwnerResponseIntakeError(RuntimeError):
    """Raised when custody, binding, raster, or promotion evidence fails."""


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise RegionOwnerResponseIntakeError(message)


def _sha256_bytes(data: bytes) -> str:
    return sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _binding(path: Path, **extra: Any) -> dict[str, Any]:
    value = {"bytes": path.stat().st_size, "sha256": _sha256_file(path)}
    value.update(extra)
    return value


def _json(data: bytes, name: str) -> dict[str, Any]:
    try:
        value = json.loads(data.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise RegionOwnerResponseIntakeError(f"invalid UTF-8 JSON: {name}") from error
    _assert(isinstance(value, dict), f"JSON is not an object: {name}")
    return value


def _timestamp(value: Any, name: str) -> datetime:
    _assert(isinstance(value, str), f"{name} is not a timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise RegionOwnerResponseIntakeError(f"{name} is invalid") from error
    _assert(parsed.tzinfo is not None, f"{name} lacks timezone")
    return parsed


def _exact_keys(value: dict[str, Any], keys: set[str], name: str) -> None:
    _assert(set(value) == keys, f"{name} fields changed")


def validate_response(surface: dict[str, Any], response: dict[str, Any]) -> dict[str, Any]:
    """Validate exact order, identities, hashes, decisions, timestamps, and attestation."""
    _exact_keys(
        response,
        {
            "response_schema_version",
            "surface_id",
            "surface_run_id",
            "pilot_report_sha256",
            "completed",
            "review_started_at_utc",
            "review_completed_at_utc",
            "owner",
            "responses",
        },
        "response",
    )
    _assert(response["response_schema_version"] == RESPONSE_SCHEMA_VERSION, "response schema mismatch")
    _assert(response["surface_id"] == SURFACE_ID, "response surface mismatch")
    _assert(response["surface_run_id"] == surface["run_id"], "response surface run mismatch")
    _assert(
        response["pilot_report_sha256"] == surface["input_bindings"]["pilot_report"]["sha256"],
        "response pilot binding mismatch",
    )
    _assert(response["completed"] is True, "response is incomplete")
    owner = response["owner"]
    _assert(isinstance(owner, dict), "owner attestation is not an object")
    _exact_keys(owner, {"attestation"}, "owner attestation")
    _assert(owner["attestation"] is True, "owner attestation is incomplete")
    started = _timestamp(response["review_started_at_utc"], "review start")
    completed = _timestamp(response["review_completed_at_utc"], "review completion")
    _assert(completed >= started, "review completion predates start")

    candidates = surface.get("candidates")
    items = response["responses"]
    _assert(isinstance(candidates, list) and len(candidates) == 6, "surface candidates changed")
    _assert(isinstance(items, list) and len(items) == 6, "response must contain six decisions")
    counts = Counter({decision: 0 for decision in ALLOWED_DECISIONS})
    seen: set[str] = set()
    for candidate, item in zip(candidates, items, strict=True):
        _assert(isinstance(item, dict), "response item is not an object")
        _exact_keys(item, {"candidate_id", "candidate_raster_sha256", "decision", "notes"}, "response item")
        candidate_id = item["candidate_id"]
        _assert(candidate_id not in seen, "duplicate candidate response")
        seen.add(candidate_id)
        _assert(candidate_id == candidate["candidate_id"], "candidate order or identity changed")
        _assert(
            item["candidate_raster_sha256"] == candidate["candidate_raster_sha256"],
            "candidate raster binding changed",
        )
        _assert(item["decision"] in ALLOWED_DECISIONS, "decision is outside yes/no/uncertain")
        counts[item["decision"]] += 1
        notes = item["notes"]
        _assert(isinstance(notes, str) and len(notes) <= 1000, "response notes violate the bounded string contract")
    return {
        "decision_counts": {decision: counts[decision] for decision in ALLOWED_DECISIONS},
        "started_at_utc": response["review_started_at_utc"],
        "completed_at_utc": response["review_completed_at_utc"],
        "candidate_bindings": [
            {
                "candidate_id": item["candidate_id"],
                "candidate_raster_sha256": item["candidate_raster_sha256"],
            }
            for item in items
        ],
    }


def _validate_surface(surface_path: Path) -> tuple[dict[str, Any], bytes]:
    data = surface_path.read_bytes()
    surface = _json(data, surface_path.name)
    _assert(surface.get("report_id") == SURFACE_ID, "surface identity changed")
    _assert(surface.get("report_version") == SURFACE_VERSION, "surface version changed")
    _assert(surface.get("response_schema_version") == RESPONSE_SCHEMA_VERSION, "surface schema changed")
    _assert(surface.get("input_bindings", {}).get("pilot_report", {}).get("sha256") == EXPECTED_PILOT_SHA256, "surface pilot hash changed")
    _assert(surface.get("input_bindings", {}).get("pilot_report", {}).get("run_id") == EXPECTED_PILOT_RUN, "surface pilot run changed")
    _assert(surface.get("summary", {}).get("owner_region_responses") == 0, "surface already contains responses")
    _assert(surface.get("summary", {}).get("owner_approved_region_labels") == 0, "surface already contains labels")
    return surface, data


def preserve_response(
    *,
    repository_root: Path,
    surface_path: Path,
    source_response_path: Path,
    destination_directory: Path,
    received_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> tuple[Path, Path, dict[str, Any]]:
    """Validate and preserve response plus receipt with no overwrite and rollback."""
    _assert(len(git_source_commit) == 40, "git source commit must be a full SHA")
    surface, surface_bytes = _validate_surface(surface_path)
    before = source_response_path.read_bytes()
    _assert(len(before) <= 1_000_000, "response exceeds bounded byte contract")
    response = _json(before, source_response_path.name)
    summary = validate_response(surface, response)
    response_sha = _sha256_bytes(before)
    expected_name = f"{SURFACE_ID}-RESPONSE-{response_sha[:16]}.json"
    _assert(source_response_path.name == expected_name, "response filename does not match its exact byte hash")
    received = _timestamp(received_at_utc, "received time")
    completed = _timestamp(summary["completed_at_utc"], "review completion")
    _assert(received >= completed, "received time predates review completion")

    destination_directory.mkdir(parents=True, exist_ok=True)
    exact_path = destination_directory / expected_name
    receipt_path = destination_directory / f"{SURFACE_ID}-RECEIPT-{response_sha[:16]}.json"
    try:
        exact_path.relative_to(repository_root)
        receipt_path.relative_to(repository_root)
    except ValueError as error:
        raise RegionOwnerResponseIntakeError("custody destination is outside the repository") from error
    _assert_ignored(repository_root, exact_path)
    _assert_ignored(repository_root, receipt_path)
    receipt = {
        "report_id": f"{SURFACE_ID}-RECEIPT",
        "report_version": LOCK_VERSION,
        "received_at_utc": received_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": TASK_ISSUE,
        "git_source_commit": git_source_commit,
        "software_version": burnlens.__version__,
        "evidence_origin": "owner-returned-region-response",
        "origin_declared_by_operator": True,
        "surface_binding": {"report_id": SURFACE_ID, "run_id": surface["run_id"], "bytes": len(surface_bytes), "sha256": _sha256_bytes(surface_bytes)},
        "response_binding": {"bytes": len(before), "sha256": response_sha, **summary},
        "exact_response_preserved_without_overwrite": True,
        "owner_yes_is_sufficient_without_other_gates": False,
        "dataset_version": None,
        "split_version": None,
        "baseline_version": None,
        "model_version": None,
        "decision": "PASS_EXACT_OWNER_REGION_RESPONSE_LOCK_DEFER_PROMOTION_GATES",
    }
    receipt_bytes = (json.dumps(receipt, indent=2) + "\n").encode("utf-8")
    wrote_response = False
    try:
        with exact_path.open("xb") as handle:
            handle.write(before)
            handle.flush()
            os.fsync(handle.fileno())
        wrote_response = True
        after = source_response_path.read_bytes()
        _assert(after == before, "response source changed during preservation")
        _assert(exact_path.read_bytes() == before, "preserved response differs from source")
        with receipt_path.open("xb") as handle:
            handle.write(receipt_bytes)
            handle.flush()
            os.fsync(handle.fileno())
    except Exception:
        if wrote_response and exact_path.exists():
            exact_path.unlink()
        if receipt_path.exists():
            receipt_path.unlink()
        raise
    return exact_path, receipt_path, receipt


def _record_path(repository_root: Path, record_id: str) -> Path:
    if record_id.startswith(("SOURCE-PRECEDENCE-", "LABEL-FITNESS-", "USE-BOUNDARY-")):
        root = repository_root / "records/phase-two/reviews"
    elif record_id.startswith("SOURCE-"):
        root = repository_root / "records/phase-two/sources"
    elif record_id.startswith("TERMS-"):
        root = repository_root / "records/phase-two/terms"
    elif record_id.startswith("PRECHECK-"):
        root = repository_root / "records/phase-two/prechecks"
    else:
        root = repository_root / "records/phase-two/reviews"
    file_stem = (
        record_id.replace("SOURCE-PRECEDENCE", "SOURCE_PRECEDENCE")
        .replace("USE-BOUNDARY", "USE_BOUNDARY")
        .replace("LABEL-FITNESS", "LABEL_FITNESS")
    )
    matches = list(root.glob(f"{file_stem}.*"))
    _assert(len(matches) == 1 and matches[0].is_file(), f"record binding missing or ambiguous: {record_id}")
    return matches[0]


def _record_bindings(repository_root: Path) -> list[dict[str, Any]]:
    values: list[dict[str, Any]] = []
    for record_id in (*SOURCE_RECORDS, *TERMS_RECORDS, *REVIEW_RECORDS):
        path = _record_path(repository_root, record_id)
        text = path.read_text(encoding="utf-8")
        if record_id.startswith("TERMS-"):
            lines = text.splitlines()
            decisions = [line.split(":", 1)[1].strip(" `.*") for line in lines if line.startswith("**Decision:**")]
            for index, line in enumerate(lines):
                if line.strip() == "## Decision":
                    following = next((value.strip(" `.*") for value in lines[index + 1 :] if value.strip()), "")
                    decisions.append(following)
            _assert(len(decisions) == 1, f"terms decision field missing or ambiguous: {record_id}")
            _assert(not decisions[0].upper().startswith("UNRESOLVED"), f"unresolved terms record: {record_id}")
        values.append({"record_id": record_id, **_binding(path)})
    return values


def _connected(mask: np.ndarray) -> bool:
    points = np.argwhere(mask)
    if not len(points):
        return False
    start = tuple(int(value) for value in points[0])
    seen = {start}
    queue: deque[tuple[int, int]] = deque([start])
    height, width = mask.shape
    while queue:
        row, column = queue.popleft()
        for delta_row in (-1, 0, 1):
            for delta_column in (-1, 0, 1):
                if not (delta_row or delta_column):
                    continue
                candidate = (row + delta_row, column + delta_column)
                if 0 <= candidate[0] < height and 0 <= candidate[1] < width and mask[candidate] and candidate not in seen:
                    seen.add(candidate)
                    queue.append(candidate)
    return len(seen) == int(mask.sum())


def _one_pixel_ring(core: np.ndarray) -> np.ndarray:
    padded = np.pad(core, 1, constant_values=False)
    output = np.zeros_like(core, dtype=bool)
    for row_offset in range(3):
        for column_offset in range(3):
            output |= padded[row_offset : row_offset + core.shape[0], column_offset : column_offset + core.shape[1]]
    return output & ~core


def _verify_candidate_raster(path: Path, candidate: dict[str, Any]) -> dict[str, Any]:
    _assert(path.is_file(), f"candidate raster missing: {path.name}")
    _assert(path.stat().st_size == candidate["candidate_raster_bytes"], f"candidate raster size changed: {path.name}")
    _assert(_sha256_file(path) == candidate["candidate_raster_sha256"], f"candidate raster hash changed: {path.name}")
    contract = candidate["raster_contract"]
    with rasterio.open(path) as dataset:
        values = dataset.read()[0]
        tags = dataset.tags()
        _assert(dataset.count == 1 and dataset.dtypes == ("uint8",), f"candidate raster dtype changed: {path.name}")
        _assert(dataset.crs is not None and dataset.crs.to_epsg() == 32610, f"candidate raster CRS changed: {path.name}")
        _assert(dataset.width == contract["width"] and dataset.height == contract["height"], f"candidate raster dimensions changed: {path.name}")
        _assert(np.allclose(list(dataset.transform)[:6], contract["transform"], rtol=0, atol=0), f"candidate raster transform changed: {path.name}")
        _assert(dataset.nodata == contract["nodata"] == 255.0, f"candidate raster nodata changed: {path.name}")
        _assert(set(int(value) for value in np.unique(values)) <= {0, 1, 2}, f"candidate raster domain changed: {path.name}")
        core = values == 1
        ring = values == 2
        _assert(int(core.sum()) == candidate["core_pixels"], f"candidate core count changed: {path.name}")
        _assert(int(ring.sum()) == candidate["unknown_ring_pixels"], f"candidate ring count changed: {path.name}")
        _assert(_connected(core), f"candidate core is not intact 8-connected evidence: {path.name}")
        _assert(np.array_equal(ring, _one_pixel_ring(core)), f"candidate unknown ring changed: {path.name}")
        _assert(tags.get("candidate_id") == candidate["candidate_id"], f"candidate raster identity tag changed: {path.name}")
        _assert(tags.get("event_group_id") == candidate["event_group_id"], f"candidate event tag changed: {path.name}")
        _assert(tags.get("proposed_class") == candidate["proposed_class"], f"candidate class tag changed: {path.name}")
        _assert(tags.get("region_label_created") == "false" and tags.get("dataset_created") == "false", f"candidate raster no-promotion tags changed: {path.name}")
    return {
        "bytes": path.stat().st_size,
        "sha256": _sha256_file(path),
        "core_pixels": int(core.sum()),
        "unknown_ring_pixels": int(ring.sum()),
        "crs": "EPSG:32610",
        "class_domain": [0, 1, 2],
        "core_connected_8": True,
        "ring_exactly_one_pixel": True,
    }


def _validate_receipt(receipt: dict[str, Any], response_bytes: bytes, surface_bytes: bytes) -> None:
    _assert(receipt.get("report_id") == f"{SURFACE_ID}-RECEIPT", "receipt identity changed")
    _assert(receipt.get("report_version") == LOCK_VERSION, "receipt version changed")
    _assert(receipt.get("task_issue") == TASK_ISSUE, "receipt issue changed")
    _assert(receipt.get("evidence_origin") == "owner-returned-region-response", "receipt origin changed")
    _assert(receipt.get("exact_response_preserved_without_overwrite") is True, "receipt lacks no-overwrite custody")
    _assert(receipt.get("response_binding", {}).get("bytes") == len(response_bytes), "receipt response size changed")
    _assert(receipt.get("response_binding", {}).get("sha256") == _sha256_bytes(response_bytes), "receipt response hash changed")
    _assert(receipt.get("surface_binding", {}).get("bytes") == len(surface_bytes), "receipt surface size changed")
    _assert(receipt.get("surface_binding", {}).get("sha256") == _sha256_bytes(surface_bytes), "receipt surface hash changed")


def build_private_reconciliation(
    *,
    repository_root: Path,
    pilot_path: Path,
    surface_path: Path,
    response_path: Path,
    receipt_path: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, Any]:
    """Re-run response, source, raster, uncertainty, and leakage gates privately."""
    _assert(len(git_source_commit) == 40, "git source commit must be a full SHA")
    _timestamp(generated_at_utc, "generated time")
    surface, surface_bytes = _validate_surface(surface_path)
    response_bytes = response_path.read_bytes()
    response = _json(response_bytes, response_path.name)
    validation = validate_response(surface, response)
    receipt_bytes = receipt_path.read_bytes()
    receipt = _json(receipt_bytes, receipt_path.name)
    _validate_receipt(receipt, response_bytes, surface_bytes)

    pilot_bytes = pilot_path.read_bytes()
    _assert(_sha256_bytes(pilot_bytes) == EXPECTED_PILOT_SHA256, "pilot report hash changed")
    pilot = _json(pilot_bytes, pilot_path.name)
    _assert(pilot.get("report_id") == PILOT_ID and pilot.get("report_version") == PILOT_REPORT_VERSION, "pilot identity changed")
    _assert(pilot.get("run_id") == EXPECTED_PILOT_RUN, "pilot run changed")
    _assert(tuple(pilot.get("source_records", [])) == SOURCE_RECORDS, "pilot source records changed")
    _assert(tuple(pilot.get("terms_records", [])) == TERMS_RECORDS[:3], "pilot terms records changed")
    pilot_candidates = {item["candidate_id"]: item for item in pilot.get("candidates", [])}
    _assert(len(pilot_candidates) == 6, "pilot candidate count changed")

    event_masks: dict[str, np.ndarray] = {}
    units: list[dict[str, Any]] = []
    class_counts: Counter[str] = Counter()
    event_counts: Counter[str] = Counter()
    accepted_core_pixels = 0
    excluded_ring_pixels = 0
    for surface_candidate, response_item in zip(surface["candidates"], response["responses"], strict=True):
        candidate_id = surface_candidate["candidate_id"]
        pilot_candidate = pilot_candidates.get(candidate_id)
        _assert(pilot_candidate is not None, "candidate absent from pilot")
        _assert(pilot_candidate["candidate_class"] == surface_candidate["proposed_class"], "pilot/surface class mismatch")
        _assert(pilot_candidate["event_group_id"] == surface_candidate["event_group_id"], "pilot/surface event mismatch")
        raster_path = pilot_path.parent / surface_candidate["candidate_raster"]
        raster_gate = _verify_candidate_raster(raster_path, surface_candidate)
        with rasterio.open(raster_path) as dataset:
            occupied = dataset.read()[0] > 0
        previous = event_masks.get(surface_candidate["event_group_id"])
        if previous is None:
            event_masks[surface_candidate["event_group_id"]] = occupied
        else:
            _assert(previous.shape == occupied.shape and not np.any(previous & occupied), "candidate regions overlap within an event")
            event_masks[surface_candidate["event_group_id"]] = previous | occupied

        gates = {
            "owner_response": response_item["decision"] == "yes",
            "reproducibility": True,
            "source_and_terms": True,
            "quality_and_registration": True,
            "uncertainty_ring_excluded": True,
            "event_level_leakage_control": True,
        }
        accepted = all(gates.values())
        disposition = "OWNER_APPROVED_PROTOTYPE_REGION_LABEL" if accepted else "EXCLUDED_OWNER_NO_OR_UNCERTAIN"
        if accepted:
            class_counts[surface_candidate["proposed_class"]] += 1
            event_counts[surface_candidate["event_group_id"]] += 1
            accepted_core_pixels += raster_gate["core_pixels"]
        excluded_ring_pixels += raster_gate["unknown_ring_pixels"]
        units.append(
            {
                "candidate_id": candidate_id,
                "candidate_raster_sha256": surface_candidate["candidate_raster_sha256"],
                "event_group_id": surface_candidate["event_group_id"],
                "proposed_class": surface_candidate["proposed_class"],
                "owner_decision": response_item["decision"],
                "note_present": bool(response_item["notes"]),
                "note_sha256": _sha256_bytes(response_item["notes"].encode("utf-8")),
                "gates": gates,
                "disposition": disposition,
                "accepted_core_pixels": raster_gate["core_pixels"] if accepted else 0,
                "excluded_unknown_ring_pixels": raster_gate["unknown_ring_pixels"],
                "raster_gate": raster_gate,
            }
        )

    accepted_labels = sum(1 for item in units if item["disposition"] == "OWNER_APPROVED_PROTOTYPE_REGION_LABEL")
    event_group_count = len(event_counts)
    _assert(excluded_ring_pixels == pilot["summary"]["unknown_ring_pixels"], "unknown-ring aggregate changed")
    _assert(accepted_core_pixels <= pilot["summary"]["core_pixels"], "accepted core aggregate exceeds pilot")
    return {
        "report_id": f"{REPORT_ID}-PRIVATE",
        "report_version": PRIVATE_REPORT_VERSION,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": TASK_ISSUE,
        "git_source_commit": git_source_commit,
        "software_version": burnlens.__version__,
        "aoi_version": AOI_VERSION,
        "target_version": TARGET_VERSION,
        "label_schema_version": LABEL_SCHEMA_VERSION,
        "label_set_version": LABEL_SET_VERSION if accepted_labels else None,
        "dataset_version": None,
        "split_version": None,
        "baseline_version": None,
        "model_version": None,
        "input_bindings": {
            "pilot": {"report_id": PILOT_ID, "run_id": pilot["run_id"], "bytes": len(pilot_bytes), "sha256": _sha256_bytes(pilot_bytes)},
            "surface": {"report_id": SURFACE_ID, "run_id": surface["run_id"], "bytes": len(surface_bytes), "sha256": _sha256_bytes(surface_bytes)},
            "response": {"bytes": len(response_bytes), "sha256": _sha256_bytes(response_bytes)},
            "receipt": {"bytes": len(receipt_bytes), "sha256": _sha256_bytes(receipt_bytes)},
        },
        "record_bindings": _record_bindings(repository_root),
        "decision_counts": validation["decision_counts"],
        "outcome": {
            "owner_approved_region_labels": accepted_labels,
            "prototype_label_class_counts": dict(sorted(class_counts.items())),
            "prototype_label_event_counts": dict(sorted(event_counts.items())),
            "accepted_core_pixels": accepted_core_pixels,
            "accepted_core_area_ha": round(accepted_core_pixels * 0.04, 2),
            "excluded_unknown_ring_pixels": excluded_ring_pixels,
            "event_group_count": event_group_count,
            "minimum_event_group_count": MINIMUM_EVENT_GROUPS,
            "dataset_fitness_reopened": event_group_count >= MINIMUM_EVENT_GROUPS,
        },
        "units": units,
        "boundaries": {
            "owner_review_is_independent_ground_truth": False,
            "unknown_ring_is_background": False,
            "dataset_created": False,
            "split_created": False,
            "baseline_created": False,
            "model_created": False,
            "accuracy_or_operational_claim_created": False,
        },
        "decision": (
            "ACCEPT_OWNER_APPROVED_PROTOTYPE_REGION_LABELS_DEFER_DATASET_SPLIT_BASELINE_MODEL"
            if accepted_labels
            else "NO_OWNER_APPROVED_PROTOTYPE_REGION_LABELS"
        ),
    }


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for candidate in ("C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/segoeui.ttf"):
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            pass
    return ImageFont.load_default()


def _render_png(report: dict[str, Any], path: Path) -> None:
    image = Image.new("RGB", (1600, 1100), "#f4f0e8")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 1600, 220), fill="#132a26")
    draw.text((70, 42), "BurnLens owner region response intake", fill="white", font=_font(42))
    draw.text((70, 108), "Exact custody / six gate families / prototype labels / dataset still deferred", fill="#c6ddd6", font=_font(22))
    draw.text((70, 165), WARNING, fill="#f2c48c", font=_font(16))
    metrics = (
        (str(sum(report["decision_counts"].values())), "owner responses"),
        (str(report["outcome"]["owner_approved_region_labels"]), "prototype region labels"),
        (str(report["outcome"]["accepted_core_pixels"]), "accepted core pixels"),
        (str(report["outcome"]["excluded_unknown_ring_pixels"]), "ring pixels excluded"),
    )
    for index, (value, label) in enumerate(metrics):
        left = 70 + index * 375
        draw.rounded_rectangle((left, 270, left + 330, 440), radius=14, fill="white", outline="#c9c0b4")
        draw.text((left + 24, 300), value, fill="#006b64", font=_font(42))
        draw.text((left + 24, 370), label, fill="#263932", font=_font(18))
    draw.text((70, 500), "Gate result", fill="#132a26", font=_font(28))
    gate_rows = (
        "PASS  exact completed owner response and no-overwrite custody",
        "PASS  candidate bytes, native grids, 8-connected cores, and one-pixel rings",
        "PASS  source, terms, quality, uncertainty, and event identity bindings",
        "BLOCK dataset: 3 event groups remain below the required 6",
    )
    for index, line in enumerate(gate_rows):
        color = "#8a521c" if line.startswith("BLOCK") else "#006b64"
        draw.text((95, 565 + index * 75), line, fill=color, font=_font(22))
    draw.rounded_rectangle((70, 900, 1530, 1030), radius=14, fill="#fff8dd", outline="#d87618")
    draw.text((95, 930), "Decision", fill="#8a521c", font=_font(20))
    draw.text((95, 975), report["decision"], fill="#132a26", font=_font(19))
    image.save(path, format="PNG", optimize=False)


def _render_html(report: dict[str, Any]) -> str:
    counts = report["decision_counts"]
    outcome = report["outcome"]
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>BurnLens owner region response intake</title><style>
*{{box-sizing:border-box}}body{{margin:0;background:#f4f0e8;color:#17251f;font:16px/1.55 system-ui,sans-serif;overflow-wrap:anywhere}}header{{background:#132a26;color:white;padding:2.4rem max(5vw,1rem)}}header p{{max-width:900px;color:#c6ddd6}}main{{max-width:1120px;margin:auto;padding:1.2rem}}.warning,.card{{background:#fffdf8;border:1px solid #d7cec1;border-radius:14px;padding:1.1rem;margin:1rem 0}}.warning{{border-left:7px solid #d87618;font-weight:650}}.metrics{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:1rem}}.metric{{background:white;border:1px solid #d7cec1;border-radius:12px;padding:1rem}}.metric strong{{display:block;color:#006b64;font-size:2rem}}img{{display:block;width:100%;height:auto;border:1px solid #d7cec1}}code{{word-break:break-word}}@media(max-width:700px){{.metrics{{grid-template-columns:1fr 1fr}}header{{padding:1.4rem 1rem}}main{{padding:.65rem}}}}
</style></head><body><header><p>BURNLENS / PHASE TWO / ISSUE #461</p><h1>Owner region response intake</h1><p>Exact private custody, deterministic gate evaluation, and content-safe public aggregates.</p></header><main>
<p class="warning">{escape(report['warning'])}</p><section class="metrics"><div class="metric"><strong>{sum(counts.values())}</strong>owner responses</div><div class="metric"><strong>{outcome['owner_approved_region_labels']}</strong>prototype region labels</div><div class="metric"><strong>{outcome['accepted_core_pixels']}</strong>accepted core pixels</div><div class="metric"><strong>{outcome['excluded_unknown_ring_pixels']}</strong>ring pixels excluded</div></section>
<section class="card"><h2>Aggregate result</h2><p>Owner decisions: {counts['yes']} yes / {counts['no']} no / {counts['uncertain']} uncertain. Passed labels: {outcome['prototype_label_class_counts'].get('burned',0)} burned and {outcome['prototype_label_class_counts'].get('background',0)} background across {outcome['event_group_count']} immutable event groups.</p><p>Every admitted core passed exact-byte reconstruction, source and terms, native-grid quality, explicit uncertainty-ring exclusion, and event-identity gates. Notes and unit decisions remain private.</p></section>
<img src="{REPORT_ID}.png" alt="BurnLens owner region response intake shows exact custody and evidence gate results">
<section class="card"><h2>Why the dataset remains blocked</h2><p>Only {outcome['event_group_count']} event groups are represented; the frozen minimum is {outcome['minimum_event_group_count']}. No split exists, no event has been assigned across roles, and no ring or outside pixel becomes background.</p></section>
<section class="card"><h2>Decision</h2><p><strong>{escape(report['decision'])}</strong></p><p>Label set <code>{escape(report['label_set_version'] or 'none')}</code> · schema <code>{escape(report['label_schema_version'])}</code> · run <code>{escape(report['run_id'])}</code> · source <code>{escape(report['git_source_commit'])}</code>. Dataset, split, baseline, and model remain absent.</p></section>
</main></body></html>'''


def public_report(private: dict[str, Any], private_binding: dict[str, Any]) -> dict[str, Any]:
    """Create a path-free, notes-free, unit-free aggregate public report."""
    return {
        "report_id": REPORT_ID,
        "report_version": REPORT_VERSION,
        "generated_at_utc": private["generated_at_utc"],
        "run_id": private["run_id"],
        "repository": private["repository"],
        "task_issue": TASK_ISSUE,
        "git_source_commit": private["git_source_commit"],
        "software_version": private["software_version"],
        "aoi_version": private["aoi_version"],
        "target_version": private["target_version"],
        "label_schema_version": private["label_schema_version"],
        "label_set_version": private["label_set_version"],
        "dataset_version": None,
        "split_version": None,
        "baseline_version": None,
        "model_version": None,
        "input_bindings": {**private["input_bindings"], "private_reconciliation": private_binding},
        "record_bindings": private["record_bindings"],
        "source_records": list(SOURCE_RECORDS),
        "terms_records": list(TERMS_RECORDS),
        "review_records": list(REVIEW_RECORDS),
        "decision_counts": private["decision_counts"],
        "outcome": private["outcome"],
        "promotion_gates": {
            "exact_response_and_custody": True,
            "candidate_reproducibility": True,
            "source_and_terms": True,
            "quality_and_registration": True,
            "unknown_ring_excluded": True,
            "event_level_leakage_control": True,
        },
        "privacy": {
            "notes_public": False,
            "unit_decisions_public": False,
            "private_paths_public": False,
            "private_seed_identity_public": False,
        },
        "boundaries": private["boundaries"],
        "attribution": [
            "Contains modified Copernicus Sentinel data 2017, 2018, and 2024.",
            "NIFC WFIGS and MTBS evidence remains contextual and is not pixel-perfect truth.",
        ],
        "warning": WARNING,
        "decision": private["decision"],
        "next_gate": "Acquire and gate at least three additional comparable whole-event groups before dataset fitness, split, or baseline work can reopen.",
    }


def _assert_ignored(repository_root: Path, path: Path) -> None:
    relative = path.relative_to(repository_root)
    result = subprocess.run(
        ["git", "-C", str(repository_root), "check-ignore", "--quiet", "--no-index", "--", str(relative)],
        check=False,
    )
    _assert(result.returncode == 0, "private output is not ignored")


def write_private_no_overwrite(repository_root: Path, path: Path, report: dict[str, Any]) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    _assert_ignored(repository_root, path)
    payload = (json.dumps(report, indent=2) + "\n").encode("utf-8")
    try:
        with path.open("xb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as error:
        raise RegionOwnerResponseIntakeError("refusing to overwrite private reconciliation") from error
    return {"bytes": len(payload), "sha256": _sha256_bytes(payload), "committed": False, "ignored": True}


def write_public_no_overwrite(report: dict[str, Any], output_directory: Path) -> list[dict[str, Any]]:
    if output_directory.exists():
        raise RegionOwnerResponseIntakeError("public output directory already exists")
    output_directory.mkdir(parents=True)
    png_path = output_directory / f"{REPORT_ID}.png"
    html_path = output_directory / f"{REPORT_ID}.html"
    json_path = output_directory / f"{REPORT_ID}.json"
    _render_png(report, png_path)
    html_path.write_text(_render_html(report), encoding="utf-8", newline="\n")
    report["outputs"] = [
        {"path": html_path.name, **_binding(html_path), "media_type": "text/html"},
        {"path": png_path.name, **_binding(png_path), "media_type": "image/png"},
    ]
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    return [{"path": json_path.name, **_binding(json_path), "media_type": "application/json"}, *report["outputs"]]
