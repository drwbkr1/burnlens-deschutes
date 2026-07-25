"""Rank and lock one leakage-resistant whole-event BurnLens split."""

from __future__ import annotations

from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
import os
from pathlib import Path
from typing import Any

RANKING_ID = "WHOLE-EVENT-SPLIT-RANKING-2026-001"
SOFTWARE_VERSION = "0.51.0"
SPLIT_ID = "WHOLE-EVENT-SPLIT-2026-001"
SPLIT_VERSION = "burnlens-whole-event-split-v0.1.0"
RANKING_VERSION = "burnlens-whole-event-split-ranking-v0.1.0"
TASK_ISSUE = 562
UNIT_ID = "P2O5-T03-U02"
CONTRACT_PATH = Path(
    "records/phase-two/manifests/DATASET-BUILD-CONTRACT-2026-001.json"
)
CONTRACT_SHA256 = (
    "f6106691d42692f39684ed43c35f7c097d51f08b13c3dc3bf1e030ca9687b67f"
)
CANDIDATE_PATH = Path(
    "records/phase-two/readiness/DATASET-CANDIDATE-2026-002.json"
)
CANDIDATE_SHA256 = (
    "4a9646af493cdce81d0cd57405ebccf0dfecf5ca77c96930d0837c3b7d4e65f2"
)
ROLES = ("train", "validation", "test")
RANKING_CRITERIA = (
    "source_regime_role_deviation_ascending",
    "transfer_status_role_deviation_ascending",
    "train_core_pixels_descending",
    "validation_test_core_pixel_difference_ascending",
    "test_minimum_event_year_descending",
    "test_event_year_sum_descending",
    "train_event_year_span_ascending",
    "validation_event_year_span_ascending",
    "canonical_role_event_ids_ascending",
)


class WholeEventSplitError(RuntimeError):
    """A deterministic split-ranking or locking failure."""


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(
        "utf-8"
    )


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _binding(root: Path, relative: Path) -> dict[str, Any]:
    path = root / relative
    if not path.is_file():
        raise WholeEventSplitError(
            f"required input is absent: {relative.as_posix()}"
        )
    return {
        "path": relative.as_posix(),
        "bytes": path.stat().st_size,
        "sha256": _sha256_file(path),
    }


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise WholeEventSplitError(f"JSON root is not an object: {path}")
    return value


def _validate_inputs(
    root: Path,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, dict[str, Any]]]:
    contract_binding = _binding(root, CONTRACT_PATH)
    candidate_binding = _binding(root, CANDIDATE_PATH)
    if contract_binding["sha256"] != CONTRACT_SHA256:
        raise WholeEventSplitError("dataset contract hash drift")
    if candidate_binding["sha256"] != CANDIDATE_SHA256:
        raise WholeEventSplitError("dataset candidate hash drift")
    contract = _read_json(root / CONTRACT_PATH)
    candidate = _read_json(root / CANDIDATE_PATH)
    if contract.get("split_contract", {}).get("valid_assignment_count") != 54:
        raise WholeEventSplitError("contract assignment-count drift")
    if contract.get("boundaries", {}).get("split_created") is not False:
        raise WholeEventSplitError("entry contract already claims a split")
    by_id = {
        event["event_group_id"]: event for event in candidate["events"]
    }
    if sorted(by_id) != sorted(contract["eligible_event_group_ids"]):
        raise WholeEventSplitError("candidate and contract rosters differ")
    if len(by_id) != 6:
        raise WholeEventSplitError("exactly six event groups are required")
    return contract, candidate, by_id


def _violations(
    roles: dict[str, list[str]],
    by_id: dict[str, dict[str, Any]],
) -> list[str]:
    violations: list[str] = []
    for role in ROLES:
        if len(roles[role]) != 2:
            violations.append(f"{role}_does_not_have_two_events")
    for role in ("validation", "test"):
        if not any(
            by_id[event_id]["never_tuned_transfer"]
            for event_id in roles[role]
        ):
            violations.append(f"{role}_lacks_never_tuned_transfer_event")
    regimes = sorted({event["source_regime"] for event in by_id.values()})
    for regime in regimes:
        role_count = sum(
            any(
                by_id[event_id]["source_regime"] == regime
                for event_id in event_ids
            )
            for event_ids in roles.values()
        )
        if role_count < 2:
            violations.append(f"regime_unique_to_one_role:{regime}")
    programs = sorted(
        {
            program
            for event in by_id.values()
            for program in event["source_programs"]
        }
    )
    for program in programs:
        role_count = sum(
            any(
                program in by_id[event_id]["source_programs"]
                for event_id in event_ids
            )
            for event_ids in roles.values()
        )
        if role_count < 2:
            violations.append(f"program_unique_to_one_role:{program}")
    flattened = [event_id for values in roles.values() for event_id in values]
    if len(flattened) != 6 or len(set(flattened)) != 6:
        violations.append("event_group_reused_or_absent")
    return sorted(violations)


def _role_summary(
    event_ids: list[str], by_id: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    events = [by_id[event_id] for event_id in event_ids]
    years = [event["year"] for event in events]
    class_core_pixels = Counter()
    for event in events:
        for candidate in event["candidates"]:
            class_core_pixels[candidate["class"]] += candidate["core_pixels"]
    return {
        "event_group_ids": list(event_ids),
        "event_years": years,
        "core_pixels": sum(event["core_pixels"] for event in events),
        "class_core_pixels": {
            "background": class_core_pixels["background"],
            "burned": class_core_pixels["burned"],
        },
        "unknown_ring_pixels": sum(
            event["unknown_ring_pixels"] for event in events
        ),
        "source_regime_counts": dict(
            sorted(Counter(event["source_regime"] for event in events).items())
        ),
        "source_programs": sorted(
            {
                program
                for event in events
                for program in event["source_programs"]
            }
        ),
        "never_tuned_transfer_events": sum(
            bool(event["never_tuned_transfer"]) for event in events
        ),
    }


def _score(
    roles: dict[str, list[str]],
    by_id: dict[str, dict[str, Any]],
) -> tuple[tuple[Any, ...], dict[str, Any], dict[str, dict[str, Any]]]:
    summaries = {
        role: _role_summary(roles[role], by_id) for role in ROLES
    }
    regimes = sorted({event["source_regime"] for event in by_id.values()})
    regime_deviation = sum(
        abs(summary["source_regime_counts"].get(regime, 0) - 1)
        for summary in summaries.values()
        for regime in regimes
    )
    transfer_deviation = sum(
        abs(summary["never_tuned_transfer_events"] - 1)
        for summary in summaries.values()
    )
    train_years = summaries["train"]["event_years"]
    validation_years = summaries["validation"]["event_years"]
    test_years = summaries["test"]["event_years"]
    canonical = json.dumps(roles, sort_keys=True, separators=(",", ":"))
    key = (
        regime_deviation,
        transfer_deviation,
        -summaries["train"]["core_pixels"],
        abs(
            summaries["validation"]["core_pixels"]
            - summaries["test"]["core_pixels"]
        ),
        -min(test_years),
        -sum(test_years),
        max(train_years) - min(train_years),
        max(validation_years) - min(validation_years),
        canonical,
    )
    components = {
        "source_regime_role_deviation": regime_deviation,
        "transfer_status_role_deviation": transfer_deviation,
        "train_core_pixels": summaries["train"]["core_pixels"],
        "validation_test_core_pixel_difference": abs(
            summaries["validation"]["core_pixels"]
            - summaries["test"]["core_pixels"]
        ),
        "test_minimum_event_year": min(test_years),
        "test_event_year_sum": sum(test_years),
        "train_event_year_span": max(train_years) - min(train_years),
        "validation_event_year_span": (
            max(validation_years) - min(validation_years)
        ),
        "canonical_role_event_ids": canonical,
    }
    return key, components, summaries


def _all_assignments(
    by_id: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], Counter[str]]:
    identifiers = sorted(by_id)
    valid: list[dict[str, Any]] = []
    violation_counts: Counter[str] = Counter()
    assignment_count = 0
    for train_values in combinations(identifiers, 2):
        remaining = [
            event_id for event_id in identifiers if event_id not in train_values
        ]
        for validation_values in combinations(remaining, 2):
            test_values = [
                event_id
                for event_id in remaining
                if event_id not in validation_values
            ]
            roles = {
                "train": sorted(train_values),
                "validation": sorted(validation_values),
                "test": sorted(test_values),
            }
            assignment_count += 1
            violations = _violations(roles, by_id)
            violation_counts.update(violations)
            if violations:
                continue
            key, components, summaries = _score(roles, by_id)
            valid.append(
                {
                    "_sort_key": key,
                    "roles": roles,
                    "score_components": components,
                    "role_summaries": summaries,
                }
            )
    if assignment_count != 90 or len(valid) != 54:
        raise WholeEventSplitError(
            f"assignment inventory drift: {assignment_count} / {len(valid)}"
        )
    valid.sort(key=lambda item: item["_sort_key"])
    for rank, assignment in enumerate(valid, start=1):
        assignment["rank"] = rank
        del assignment["_sort_key"]
    return valid, violation_counts


def _group_bindings(
    contract: dict[str, Any],
    by_id: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    pair_by_event = {
        pair["event_group_id"]: pair for pair in contract["source_pairs"]
    }
    output: dict[str, dict[str, Any]] = {}
    for event_id, event in sorted(by_id.items()):
        pair = pair_by_event[event_id]
        products = pair["products"]
        scene_value = "|".join(
            str(product["native_id"]) for product in products
        )
        transforms = {
            tuple(candidate["raster_contract"]["transform"])
            for candidate in event["candidates"]
        }
        if len(transforms) != 1:
            raise WholeEventSplitError(
                f"event candidate grids differ: {event_id}"
            )
        transform_value = ",".join(str(value) for value in next(iter(transforms)))
        time_value = "|".join(
            str(product["sensing_time_utc"]) for product in products
        )
        output[event_id] = {
            "event_group_id": event_id,
            "scene_group_id": (
                "scene-" + sha256(scene_value.encode("utf-8")).hexdigest()[:16]
            ),
            "geography_group_id": (
                "geography-"
                + sha256(
                    f"{event_id}|{transform_value}".encode("utf-8")
                ).hexdigest()[:16]
            ),
            "time_group_id": (
                "time-" + sha256(time_value.encode("utf-8")).hexdigest()[:16]
            ),
            "source_regime_group_id": event["source_regime"],
            "source_product_native_ids": [
                product["native_id"] for product in products
            ],
            "source_sensing_times_utc": [
                product["sensing_time_utc"] for product in products
            ],
        }
    return output


def build_outputs(
    root: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    contract, candidate, by_id = _validate_inputs(root)
    assignments, violation_counts = _all_assignments(by_id)
    selected = assignments[0]
    group_bindings = _group_bindings(contract, by_id)
    ranking = {
        "ranking_version": RANKING_VERSION,
        "ranking_id": RANKING_ID,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": TASK_ISSUE,
        "unit_id": UNIT_ID,
        "git_source_commit": git_source_commit,
        "software_version": SOFTWARE_VERSION,
        "inputs": {
            "dataset_contract": _binding(root, CONTRACT_PATH),
            "dataset_candidate": _binding(root, CANDIDATE_PATH),
        },
        "ranking_predeclaration": {
            "criteria_in_order": list(RANKING_CRITERIA),
            "direction_note": (
                "Every criterion is applied in the declared order; the final "
                "canonical role/event string is only a deterministic tie-break."
            ),
            "pixel_values_opened": False,
            "test_pixels_opened": False,
            "patches_created": False,
        },
        "assignment_inventory": {
            "total_assignments": 90,
            "valid_assignments": 54,
            "rejected_assignments": 36,
            "rejection_reason_counts": dict(sorted(violation_counts.items())),
        },
        "ranked_valid_assignments": assignments,
        "selected_rank": 1,
        "selected_roles": selected["roles"],
        "boundaries": {
            "dataset_created": False,
            "split_locked": True,
            "patches_created": False,
            "baseline_created": False,
            "model_created": False,
            "test_pixels_opened": False,
            "training_authorized": False,
        },
    }
    ranking_bytes = _json_bytes(ranking)
    split = {
        "split_manifest_version": SPLIT_VERSION,
        "split_id": SPLIT_ID,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": TASK_ISSUE,
        "unit_id": UNIT_ID,
        "git_source_commit": git_source_commit,
        "software_version": SOFTWARE_VERSION,
        "dataset_version": "burnlens-dataset-v0.1.0",
        "split_version": SPLIT_VERSION,
        "dataset_created": False,
        "inputs": {
            "dataset_contract": _binding(root, CONTRACT_PATH),
            "dataset_candidate": _binding(root, CANDIDATE_PATH),
            "ranking": {
                "path": (
                    "records/phase-two/manifests/"
                    f"{RANKING_ID}.json"
                ),
                "bytes": len(ranking_bytes),
                "sha256": sha256(ranking_bytes).hexdigest(),
            },
        },
        "selection": {
            "rank": 1,
            "criteria_in_order": list(RANKING_CRITERIA),
            "score_components": selected["score_components"],
            "roles": {
                role: selected["role_summaries"][role] for role in ROLES
            },
        },
        "group_bindings": group_bindings,
        "candidate_bindings": {
            event["event_group_id"]: [
                {
                    "candidate_id": region["candidate_id"],
                    "class": region["class"],
                    "core_pixels": region["core_pixels"],
                    "raster_sha256": region["raster"]["sha256"],
                }
                for region in event["candidates"]
            ]
            for event in candidate["events"]
        },
        "leakage_assertions": {
            "whole_event_group_crosses_roles": False,
            "scene_group_crosses_roles": False,
            "geography_group_crosses_roles": False,
            "time_group_crosses_roles": False,
            "candidate_crosses_roles": False,
            "patch_created_before_split": False,
            "validation_or_test_used_for_normalization": False,
            "test_used_for_method_or_threshold_selection": False,
        },
        "sealed_test": {
            "event_group_ids": selected["roles"]["test"],
            "pixel_values_opened": False,
            "open_count": 0,
            "maximum_open_count": 1,
            "may_open_only_after": (
                "U05 freezes baseline families, preprocessing, thresholds, "
                "patch roster, and selection rule"
            ),
        },
        "limitations": [
            "The split contains only two event groups per role.",
            "Training has 109 accepted core pixels; validation and test each have 89.",
            "Each role has one exact source regime and one never-tuned-transfer status event.",
            "Owner-approved prototype labels are not independent ground truth.",
            "The locked split does not authorize dataset materialization or training.",
        ],
        "boundaries": {
            "split_locked": True,
            "dataset_created": False,
            "patches_created": False,
            "normalization_statistics_created": False,
            "baseline_created": False,
            "model_created": False,
            "metric_result_created": False,
            "test_pixels_opened": False,
            "training_authorized": False,
        },
        "next_dependency": "P2O5-T03-U03",
    }
    return ranking, split


def _write_new(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    created = False
    try:
        with path.open("xb") as handle:
            created = True
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        if path.read_bytes() != data:
            raise WholeEventSplitError(f"exact output readback failed: {path}")
    except Exception:
        if created and path.exists():
            path.unlink()
        raise


def write_outputs(
    root: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, Path]:
    ranking, split = build_outputs(
        root, generated_at_utc, run_id, git_source_commit
    )
    outputs = {
        "ranking": (
            root
            / "records/phase-two/manifests"
            / f"{RANKING_ID}.json"
        ),
        "split": (
            root
            / "records/phase-two/manifests"
            / f"{SPLIT_ID}.json"
        ),
    }
    _write_new(outputs["ranking"], _json_bytes(ranking))
    _write_new(outputs["split"], _json_bytes(split))
    return outputs
