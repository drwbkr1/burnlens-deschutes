from __future__ import annotations

from collections import Counter, deque
from hashlib import sha256
from html import escape
from itertools import combinations
import json
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import rasterio

from . import __version__


REPORT_ID = "SIX-EVENT-DATASET-SUFFICIENCY-2026-001"
CANDIDATE_ID = "DATASET-CANDIDATE-2026-001"
AUDIT_ID = "DATASET-READINESS-AUDIT-2026-001"
DECISION_ID = "DATASET-READINESS-DECISION-2026-001"
REPORT_VERSION = "six-event-dataset-sufficiency-v0.1.0"
AUDIT_CONTRACT_VERSION = "dataset-readiness-audit-v1"
LABEL_SET_VERSION = "owner-approved-prototype-region-labels-v0.4.0"
LABEL_SCHEMA_VERSION = "burn-scar-five-state-schema-v0.1.0"
TARGET_VERSION = "target-burn-scar-v0.2.0"
AOI_VERSION = "multi-event-native-grids-v0.4.0"
DECISION = "BLOCK_DATASET_CANDIDATE_REMEDIATE_SOURCE_REGIME_SPLIT_FITNESS"
WARNING = (
    "Experimental BurnLens owner-approved prototype evidence. Not independent ground truth, "
    "official wildfire information, emergency guidance, or field validation. Official sources govern."
)


EVENTS: tuple[dict[str, Any], ...] = (
    {
        "event_group_id": "event-darlene3-or-2024",
        "fire_name": "Darlene 3",
        "year": 2024,
        "proposal": "samples/labels/pilot/phase-two/REGION-CANDIDATE-PILOT-2026-001.json",
        "intake": "samples/labels/review/regions/phase-two/intake/REGION-OWNER-RESPONSE-INTAKE-2026-001.json",
        "candidate_ids": ("RCP-001", "RCP-002"),
        "source_regime": "sentinel2-nifc-incident-context-v1",
        "source_programs": ("COPERNICUS_SENTINEL_2", "NIFC_WFIGS"),
        "never_tuned_transfer": False,
    },
    {
        "event_group_id": "event-mckay-1035-ne-2017",
        "fire_name": "McKay 1035 NE",
        "year": 2017,
        "proposal": "samples/labels/pilot/phase-two/REGION-CANDIDATE-PILOT-2026-001.json",
        "intake": "samples/labels/review/regions/phase-two/intake/REGION-OWNER-RESPONSE-INTAKE-2026-001.json",
        "candidate_ids": ("RCP-003", "RCP-004"),
        "source_regime": "sentinel2-mtbs-current-v1",
        "source_programs": ("COPERNICUS_SENTINEL_2", "MTBS"),
        "never_tuned_transfer": False,
    },
    {
        "event_group_id": "event-tepee-1144-ne-2018",
        "fire_name": "Tepee 1144 NE",
        "year": 2018,
        "proposal": "samples/labels/pilot/phase-two/REGION-CANDIDATE-PILOT-2026-001.json",
        "intake": "samples/labels/review/regions/phase-two/intake/REGION-OWNER-RESPONSE-INTAKE-2026-001.json",
        "candidate_ids": ("RCP-005", "RCP-006"),
        "source_regime": "sentinel2-mtbs-current-v1",
        "source_programs": ("COPERNICUS_SENTINEL_2", "MTBS"),
        "never_tuned_transfer": False,
    },
    {
        "event_group_id": "event-green-ridge-0684-cs-2020",
        "fire_name": "Green Ridge 0684 CS",
        "year": 2020,
        "proposal": "samples/labels/pilot/green-ridge/phase-two/GREEN-RIDGE-REGION-PROPOSAL-2026-001.json",
        "intake": "samples/labels/review/green-ridge/phase-two/intake/GREEN-RIDGE-OWNER-RESPONSE-INTAKE-2026-001.json",
        "candidate_ids": ("GRP-001", "GRP-002"),
        "source_regime": "sentinel2-baer-mtbs-ravg-current-v1",
        "source_programs": ("COPERNICUS_SENTINEL_2", "BAER", "MTBS", "RAVG"),
        "never_tuned_transfer": True,
    },
    {
        "event_group_id": "event-grandview-0558-od-2021",
        "fire_name": "Grandview 0558 OD",
        "year": 2021,
        "proposal": "samples/labels/pilot/grandview/phase-two/GRANDVIEW-REGION-PROPOSAL-2026-001.json",
        "intake": "samples/labels/review/grandview/phase-two/intake/GRANDVIEW-OWNER-RESPONSE-INTAKE-2026-001.json",
        "candidate_ids": ("GVP-001", "GVP-002"),
        "source_regime": "sentinel2-baer-mtbs-ravg-current-v1",
        "source_programs": ("COPERNICUS_SENTINEL_2", "BAER", "MTBS", "RAVG"),
        "never_tuned_transfer": True,
    },
    {
        "event_group_id": "event-windigo-2022",
        "fire_name": "Windigo",
        "year": 2022,
        "proposal": "samples/labels/pilot/windigo/phase-two/WINDIGO-REGION-PROPOSAL-2026-001.json",
        "intake": "samples/labels/review/windigo/phase-two/intake/WINDIGO-OWNER-RESPONSE-INTAKE-2026-001.json",
        "candidate_ids": ("WDP-001", "WDP-002"),
        "source_regime": "sentinel2-baer-mtbs-ravg-current-v1",
        "source_programs": ("COPERNICUS_SENTINEL_2", "BAER", "MTBS", "RAVG"),
        "never_tuned_transfer": True,
    },
)


class SixEventDatasetSufficiencyError(RuntimeError):
    pass


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SixEventDatasetSufficiencyError(f"invalid JSON input: {path}") from exc
    if not isinstance(value, dict):
        raise SixEventDatasetSufficiencyError(f"JSON object required: {path}")
    return value


def _binding(repository_root: Path, path: Path) -> dict[str, Any]:
    payload = path.read_bytes()
    try:
        relative = path.resolve().relative_to(repository_root.resolve()).as_posix()
    except ValueError as exc:
        raise SixEventDatasetSufficiencyError(f"input escaped repository: {path}") from exc
    return {"path": relative, "bytes": len(payload), "sha256": sha256(payload).hexdigest()}


def _canonical_binding(path: Path, canonical_path: str) -> dict[str, Any]:
    payload = path.read_bytes()
    return {
        "path": canonical_path,
        "bytes": len(payload),
        "sha256": sha256(payload).hexdigest(),
    }


def _write_new(path: Path, payload: bytes) -> None:
    if path.exists():
        raise SixEventDatasetSufficiencyError(f"output already exists: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)


def _candidate_class(candidate: dict[str, Any]) -> str:
    value = candidate.get("candidate_class", candidate.get("proposed_class"))
    if value not in {"background", "burned"}:
        raise SixEventDatasetSufficiencyError("candidate class is not binary")
    return str(value)


def _connected(mask: np.ndarray) -> bool:
    positions = np.argwhere(mask)
    if not len(positions):
        return False
    start = tuple(int(value) for value in positions[0])
    queue: deque[tuple[int, int]] = deque([start])
    seen = {start}
    rows, columns = mask.shape
    while queue:
        row, column = queue.popleft()
        for row_delta in (-1, 0, 1):
            for column_delta in (-1, 0, 1):
                if row_delta == 0 and column_delta == 0:
                    continue
                neighbor = (row + row_delta, column + column_delta)
                if (
                    0 <= neighbor[0] < rows
                    and 0 <= neighbor[1] < columns
                    and bool(mask[neighbor])
                    and neighbor not in seen
                ):
                    seen.add(neighbor)
                    queue.append(neighbor)
    return len(seen) == int(mask.sum())


def _inspect_raster(path: Path, candidate: dict[str, Any]) -> dict[str, Any]:
    with rasterio.open(path) as dataset:
        if dataset.count != 1:
            raise SixEventDatasetSufficiencyError(f"candidate raster is not single-band: {path.name}")
        if dataset.crs is None or dataset.crs.to_epsg() != 32610:
            raise SixEventDatasetSufficiencyError(f"candidate raster CRS drift: {path.name}")
        if dataset.nodata != 255:
            raise SixEventDatasetSufficiencyError(f"candidate raster nodata drift: {path.name}")
        values = dataset.read(1)
        domain = {int(value) for value in np.unique(values)}
        if not domain.issubset({0, 1, 2, 255}) or not {1, 2}.issubset(domain):
            raise SixEventDatasetSufficiencyError(f"candidate raster class domain drift: {path.name}")
        core_pixels = int(np.count_nonzero(values == 1))
        ring_pixels = int(np.count_nonzero(values == 2))
        if core_pixels != int(candidate["core_pixels"]):
            raise SixEventDatasetSufficiencyError(f"candidate core count drift: {path.name}")
        if ring_pixels != int(candidate["unknown_ring_pixels"]):
            raise SixEventDatasetSufficiencyError(f"candidate ring count drift: {path.name}")
        if not _connected(values == 1):
            raise SixEventDatasetSufficiencyError(f"candidate core is not one 8-connected region: {path.name}")
        result = {
            "crs": dataset.crs.to_string(),
            "shape": [dataset.height, dataset.width],
            "transform": [float(value) for value in dataset.transform[:6]],
            "nodata": int(dataset.nodata),
            "dtype": dataset.dtypes[0],
            "class_domain": sorted(domain),
            "core_pixels": core_pixels,
            "unknown_ring_pixels": ring_pixels,
            "core_is_one_8_connected_component": True,
        }
    expected_bytes = candidate.get("candidate_raster_bytes")
    expected_sha256 = candidate.get("candidate_raster_sha256")
    payload = path.read_bytes()
    if expected_bytes is not None and int(expected_bytes) != len(payload):
        raise SixEventDatasetSufficiencyError(f"candidate raster byte drift: {path.name}")
    if expected_sha256 is not None and str(expected_sha256) != sha256(payload).hexdigest():
        raise SixEventDatasetSufficiencyError(f"candidate raster hash drift: {path.name}")
    return result


def _record_path(repository_root: Path, record_id: str) -> Path:
    matches = list((repository_root / "records" / "phase-two").rglob(f"{record_id}.md"))
    if len(matches) != 1:
        raise SixEventDatasetSufficiencyError(f"record identity is not unique: {record_id}")
    return matches[0]


def _validate_record_bindings(
    repository_root: Path, intake: dict[str, Any]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    source_bindings: list[dict[str, Any]] = []
    terms_bindings: list[dict[str, Any]] = []
    for record in intake.get("record_bindings", []):
        record_id = str(record.get("record_id", ""))
        if not (record_id.startswith("SOURCE-2026-") or record_id.startswith("TERMS-2026-")):
            continue
        path = _record_path(repository_root, record_id)
        binding = _binding(repository_root, path)
        if binding["bytes"] != int(record["bytes"]) or binding["sha256"] != str(record["sha256"]):
            raise SixEventDatasetSufficiencyError(f"record binding drift: {record_id}")
        output = {"record_id": record_id, **binding}
        if record_id.startswith("SOURCE-2026-"):
            source_bindings.append(output)
        else:
            terms_bindings.append(output)
    if not source_bindings or not terms_bindings:
        raise SixEventDatasetSufficiencyError("each intake requires exact source and terms records")
    return source_bindings, terms_bindings


def prospective_partitions(events: list[dict[str, Any]]) -> dict[str, Any]:
    identifiers = [event["event_group_id"] for event in events]
    by_id = {event["event_group_id"]: event for event in events}
    assignments: list[dict[str, Any]] = []
    for train_values in combinations(identifiers, 2):
        after_train = [value for value in identifiers if value not in train_values]
        for validation_values in combinations(after_train, 2):
            test_values = tuple(value for value in after_train if value not in validation_values)
            roles = {
                "train": tuple(sorted(train_values)),
                "validation": tuple(sorted(validation_values)),
                "test": tuple(sorted(test_values)),
            }
            violations: list[str] = []
            for role in ("validation", "test"):
                if not any(by_id[value]["never_tuned_transfer"] for value in roles[role]):
                    violations.append(f"{role}_lacks_never_tuned_transfer_event")
            regimes = sorted({event["source_regime"] for event in events})
            for regime in regimes:
                role_count = sum(
                    any(by_id[value]["source_regime"] == regime for value in values)
                    for values in roles.values()
                )
                if role_count < 2:
                    violations.append(f"regime_unique_to_one_role:{regime}")
            programs = sorted(
                {
                    program
                    for event in events
                    for program in event["source_programs"]
                }
            )
            for program in programs:
                role_count = sum(
                    any(
                        program in by_id[value]["source_programs"]
                        for value in values
                    )
                    for values in roles.values()
                )
                if role_count < 2:
                    violations.append(f"program_unique_to_one_role:{program}")
            assignments.append({"roles": {key: list(value) for key, value in roles.items()}, "violations": violations})
    valid = [assignment for assignment in assignments if not assignment["violations"]]
    closest = min(
        assignments,
        key=lambda item: (
            len(item["violations"]),
            json.dumps(item["roles"], sort_keys=True),
        ),
    )
    return {
        "total_2_2_2_assignments": len(assignments),
        "valid_assignments": len(valid),
        "closest_assignment": closest,
        "required_rules": [
            "two whole event groups in each role before patching",
            "at least one never-tuned transfer event in validation and test",
            "every source program represented in at least two split roles",
            "every exact source regime represented in at least two split roles",
        ],
    }


def build_candidate_manifest(
    repository_root: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, Any]:
    proposals: dict[str, dict[str, Any]] = {}
    intakes: dict[str, dict[str, Any]] = {}
    proposal_bindings: dict[str, dict[str, Any]] = {}
    intake_bindings: dict[str, dict[str, Any]] = {}
    source_records: dict[str, dict[str, Any]] = {}
    terms_records: dict[str, dict[str, Any]] = {}
    events: list[dict[str, Any]] = []
    raster_hashes: set[str] = set()

    for config in EVENTS:
        proposal_path = repository_root / config["proposal"]
        intake_path = repository_root / config["intake"]
        if config["proposal"] not in proposals:
            proposals[config["proposal"]] = _read_json(proposal_path)
            proposal_bindings[config["proposal"]] = _binding(repository_root, proposal_path)
        if config["intake"] not in intakes:
            intakes[config["intake"]] = _read_json(intake_path)
            intake_bindings[config["intake"]] = _binding(repository_root, intake_path)
            intake = intakes[config["intake"]]
            if any(value is not True for value in intake.get("promotion_gates", {}).values()):
                raise SixEventDatasetSufficiencyError(f"promotion gate is not passed: {intake_path.name}")
            if int(intake.get("decision_counts", {}).get("yes", 0)) <= 0:
                raise SixEventDatasetSufficiencyError(f"owner yes evidence is absent: {intake_path.name}")
            if any(
                intake.get("boundaries", {}).get(key) is not False
                for key in (
                    "owner_review_is_independent_ground_truth",
                    "unknown_ring_is_background",
                    "dataset_created",
                    "split_created",
                    "baseline_created",
                    "model_created",
                    "accuracy_or_operational_claim_created",
                )
            ):
                raise SixEventDatasetSufficiencyError(f"intake boundary drift: {intake_path.name}")
            sources, terms = _validate_record_bindings(repository_root, intake)
            source_records.update((item["record_id"], item) for item in sources)
            terms_records.update((item["record_id"], item) for item in terms)

        proposal = proposals[config["proposal"]]
        candidates_by_id = {candidate["candidate_id"]: candidate for candidate in proposal["candidates"]}
        event_candidates: list[dict[str, Any]] = []
        for candidate_id in config["candidate_ids"]:
            if candidate_id not in candidates_by_id:
                raise SixEventDatasetSufficiencyError(f"candidate missing from proposal: {candidate_id}")
            candidate = candidates_by_id[candidate_id]
            candidate_class = _candidate_class(candidate)
            raster_path = proposal_path.parent / candidate["candidate_raster"]
            raster_binding = _binding(repository_root, raster_path)
            if raster_binding["sha256"] in raster_hashes:
                raise SixEventDatasetSufficiencyError("duplicate candidate raster bytes")
            raster_hashes.add(raster_binding["sha256"])
            event_candidates.append(
                {
                    "candidate_id": candidate_id,
                    "class": candidate_class,
                    "core_pixels": int(candidate["core_pixels"]),
                    "core_area_hectares": round(int(candidate["core_pixels"]) * 0.04, 2),
                    "unknown_ring_pixels": int(candidate["unknown_ring_pixels"]),
                    "raster": raster_binding,
                    "raster_contract": _inspect_raster(raster_path, candidate),
                }
            )
        class_counts = Counter(candidate["class"] for candidate in event_candidates)
        if class_counts != {"background": 1, "burned": 1}:
            raise SixEventDatasetSufficiencyError(f"event class roster drift: {config['event_group_id']}")
        core_pixels = sum(candidate["core_pixels"] for candidate in event_candidates)
        ring_pixels = sum(candidate["unknown_ring_pixels"] for candidate in event_candidates)
        events.append(
            {
                "event_group_id": config["event_group_id"],
                "fire_name": config["fire_name"],
                "year": config["year"],
                "source_regime": config["source_regime"],
                "source_programs": list(config["source_programs"]),
                "never_tuned_transfer": config["never_tuned_transfer"],
                "class_counts": dict(sorted(class_counts.items())),
                "core_pixels": core_pixels,
                "unknown_ring_pixels": ring_pixels,
                "candidates": event_candidates,
                "proposal": proposal_bindings[config["proposal"]],
                "owner_intake": intake_bindings[config["intake"]],
            }
        )

    if len(events) != 6:
        raise SixEventDatasetSufficiencyError("exactly six event groups are required")
    final_intake = intakes["samples/labels/review/windigo/phase-two/intake/WINDIGO-OWNER-RESPONSE-INTAKE-2026-001.json"]
    final_outcome = final_intake["outcome"]
    if (
        final_intake.get("label_set_version") != LABEL_SET_VERSION
        or int(final_outcome.get("cumulative_owner_approved_region_labels", 0)) != 12
        or int(final_outcome.get("cumulative_accepted_core_pixels", 0)) != 286
        or int(final_outcome.get("cumulative_excluded_unknown_ring_pixels", 0)) != 533
    ):
        raise SixEventDatasetSufficiencyError("final label-set aggregate drift")

    total_core = sum(event["core_pixels"] for event in events)
    total_ring = sum(event["unknown_ring_pixels"] for event in events)
    if total_core != 286 or total_ring != 533:
        raise SixEventDatasetSufficiencyError("reconstructed region aggregate drift")
    for event in events:
        event["accepted_core_share_percent"] = round(100 * event["core_pixels"] / total_core, 4)

    regimes = Counter(event["source_regime"] for event in events)
    programs = Counter(
        program
        for event in events
        for program in event["source_programs"]
    )
    partitions = prospective_partitions(events)
    return {
        "candidate_manifest_version": "burnlens-dataset-candidate-v0.1.0",
        "candidate_id": CANDIDATE_ID,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": 552,
        "git_source_commit": git_source_commit,
        "software_version": __version__,
        "aoi_version": AOI_VERSION,
        "target_version": TARGET_VERSION,
        "label_schema_version": LABEL_SCHEMA_VERSION,
        "label_set_version": LABEL_SET_VERSION,
        "dataset_version": None,
        "split_version": None,
        "baseline_version": None,
        "model_version": None,
        "input_bindings": {
            "proposals": list(proposal_bindings.values()),
            "owner_intakes": list(intake_bindings.values()),
            "source_records": sorted(source_records.values(), key=lambda item: item["record_id"]),
            "terms_records": sorted(terms_records.values(), key=lambda item: item["record_id"]),
        },
        "inventory": {
            "event_groups": len(events),
            "owner_approved_regions": sum(len(event["candidates"]) for event in events),
            "class_counts": {"background": 6, "burned": 6},
            "accepted_core_pixels": total_core,
            "accepted_core_area_hectares": round(total_core * 0.04, 2),
            "excluded_unknown_ring_pixels": total_ring,
            "maximum_event_core_share_percent": max(event["accepted_core_share_percent"] for event in events),
            "balanced_review_roster_is_natural_prevalence": False,
        },
        "events": events,
        "source_regime_counts": dict(sorted(regimes.items())),
        "source_program_counts": dict(sorted(programs.items())),
        "partition_feasibility": partitions,
        "limitations": [
            "The labels are disclosed owner-approved prototype regions, not independent ground truth.",
            "The balanced review roster does not estimate natural burned/background prevalence.",
            "Only 286 native 20 m core pixels are accepted; any later model is a small-data experiment.",
            "Darlene 3 is the sole NIFC incident-context event, so its exact source-program regime and the NIFC program can occur in only one split role.",
        ],
        "boundaries": {
            "dataset_created": False,
            "split_created": False,
            "baseline_created": False,
            "model_created": False,
            "training_authorized": False,
            "independent_ground_truth_claimed": False,
        },
    }


def build_audit_contract(candidate: dict[str, Any], candidate_sha256: str) -> dict[str, Any]:
    inventory = candidate["inventory"]
    partitions = candidate["partition_feasibility"]
    unique_regimes = sorted(
        regime for regime, count in candidate["source_regime_counts"].items() if count < 2
    )
    unique_programs = sorted(
        program for program, count in candidate["source_program_counts"].items() if count < 2
    )
    required_gate_ids = [
        "source-and-terms",
        "provenance-and-custody",
        "schema-and-quality",
        "coverage-and-balance",
        "uncertainty-and-exclusions",
        "leakage-and-split-fitness",
        "reproducibility",
        "evaluation-design",
        "human-review",
        "claims-and-privacy",
    ]
    gates = [
        {
            "gate_id": "source-and-terms",
            "category": "source_and_terms",
            "required": True,
            "status": "pass",
            "evidence_refs": [
                "records/phase-two/sources",
                "records/phase-two/terms",
                "owner intake promotion_gates.source_and_terms",
            ],
            "finding": "Every intake binds exact current source and terms records; provider bytes remain private and official sources govern.",
            "remediation": "",
        },
        {
            "gate_id": "provenance-and-custody",
            "category": "provenance_and_custody",
            "required": True,
            "status": "pass",
            "evidence_refs": [
                "DATASET-CANDIDATE-2026-001.json input_bindings",
                "four tracked aggregate owner-intake reports covering six event outcomes",
            ],
            "finding": "All proposals, rasters, aggregate intakes, source records, and terms records match immutable byte and SHA-256 identities.",
            "remediation": "",
        },
        {
            "gate_id": "schema-and-quality",
            "category": "schema_and_quality",
            "required": True,
            "status": "pass",
            "evidence_refs": [
                "DATASET-CANDIDATE-2026-001.json events[].candidates[].raster_contract",
                "owner intake promotion_gates.quality_and_registration",
            ],
            "finding": "All 12 EPSG:32610 rasters are single-band, nodata 255, domain 0/1/2/255, count-exact, and contain one 8-connected core.",
            "remediation": "",
        },
        {
            "gate_id": "coverage-and-balance",
            "category": "coverage_and_balance",
            "required": True,
            "status": "pass",
            "evidence_refs": [
                "DATASET-CANDIDATE-2026-001.json inventory",
                "LABEL-REGION-REMEDIATION-PLAN-2026-001 advancement_gates",
            ],
            "finding": (
                f"Six events each contribute one burned and one background region; no event exceeds "
                f"{inventory['maximum_event_core_share_percent']:.4f}% of 286 accepted core pixels. "
                "Balanced review sampling remains explicitly non-prevalence."
            ),
            "remediation": "",
        },
        {
            "gate_id": "uncertainty-and-exclusions",
            "category": "uncertainty_and_exclusions",
            "required": True,
            "status": "pass",
            "evidence_refs": [
                "DATASET-CANDIDATE-2026-001.json inventory.excluded_unknown_ring_pixels",
                "candidate raster value 2 contracts",
            ],
            "finding": "All 533 reviewed unknown-ring pixels remain explicit value-2 exclusions and are never background.",
            "remediation": "",
        },
        {
            "gate_id": "leakage-and-split-fitness",
            "category": "leakage_and_split_fitness",
            "required": True,
            "status": "block",
            "evidence_refs": [
                "DATASET-CANDIDATE-2026-001.json partition_feasibility",
                "LABEL-REGION-REMEDIATION-PLAN-2026-001 event_plan.requirements",
            ],
            "finding": (
                f"All {partitions['total_2_2_2_assignments']} whole-event 2/2/2 assignments fail the frozen "
                f"source-program/regime replication rule. Unique program(s): {', '.join(unique_programs)}. "
                f"Unique exact regime(s): {', '.join(unique_regimes)}."
            ),
            "remediation": (
                "Add and fully gate one comparable event under either replicated MTBS-current or "
                "BAER+MTBS+RAVG-current regime, then exclude the unique Darlene NIFC-regime event from "
                "the six-event dataset candidate; or add a second fully equivalent NIFC-regime event. "
                "Re-run every gate before split creation."
            ),
        },
        {
            "gate_id": "reproducibility",
            "category": "reproducibility",
            "required": True,
            "status": "pass",
            "evidence_refs": [
                "locked uv environment",
                "DATASET-CANDIDATE-2026-001.json exact reconstruction",
            ],
            "finding": "The evaluator reopens and validates every tracked input and raster under the locked repository environment.",
            "remediation": "",
        },
        {
            "gate_id": "evaluation-design",
            "category": "evaluation_design",
            "required": True,
            "status": "block",
            "evidence_refs": [
                "DATASET-CANDIDATE-2026-001.json partition_feasibility",
                "three never-tuned transfer events",
            ],
            "finding": (
                "Three never-tuned transfer events exist, but no split can satisfy both transfer reservation and "
                "the frozen exact-regime replication rule. Held-out evaluation therefore cannot be locked yet."
            ),
            "remediation": "Resolve split fitness, then lock train/validation/test before any patch generation or method selection.",
        },
        {
            "gate_id": "human-review",
            "category": "human_review",
            "required": True,
            "status": "pass",
            "evidence_refs": [
                "four aggregate owner-response intake reports",
                "owner intake promotion_gates",
            ],
            "finding": "Every accepted region has exact owner-yes custody plus passed non-owner gates; yes remains necessary but insufficient.",
            "remediation": "",
        },
        {
            "gate_id": "claims-and-privacy",
            "category": "claims_and_privacy",
            "required": True,
            "status": "pass",
            "evidence_refs": [
                "owner intake privacy and boundaries",
                "BurnLens use boundary and source precedence",
            ],
            "finding": "The audit exposes only aggregate tracked evidence and preserves null dataset/split/baseline/model versions and prototype-label limitations.",
            "remediation": "",
        },
    ]
    return {
        "audit_contract_version": AUDIT_CONTRACT_VERSION,
        "template": False,
        "audit_id": AUDIT_ID,
        "candidate_id": CANDIDATE_ID,
        "candidate_manifest_sha256": candidate_sha256,
        "required_gate_ids": required_gate_ids,
        "gates": gates,
        "count_checks": [
            {"check_id": "minimum-event-groups", "observed": 6, "operator": ">=", "threshold": 6, "on_failure": "block"},
            {"check_id": "binary-classes-per-event", "observed": 2, "operator": ">=", "threshold": 2, "on_failure": "block"},
            {"check_id": "unknown-ring-pixels", "observed": 533, "operator": ">", "threshold": 0, "on_failure": "block"},
            {
                "check_id": "maximum-event-core-share-percent",
                "observed": inventory["maximum_event_core_share_percent"],
                "operator": "<=",
                "threshold": 50,
                "on_failure": "block",
            },
            {"check_id": "never-tuned-transfer-events", "observed": 3, "operator": ">=", "threshold": 2, "on_failure": "block"},
            {
                "check_id": "valid-2-2-2-assignments",
                "observed": partitions["valid_assignments"],
                "operator": ">=",
                "threshold": 1,
                "on_failure": "block",
            },
            {
                "check_id": "unique-exact-source-regimes",
                "observed": len(unique_regimes),
                "operator": "==",
                "threshold": 0,
                "on_failure": "block",
            },
            {
                "check_id": "unique-source-programs",
                "observed": len(unique_programs),
                "operator": "==",
                "threshold": 0,
                "on_failure": "block",
            },
        ],
        "training_authorization": {
            "separate_approval_required": True,
            "authorized_by_this_audit": False,
        },
    }


def build_audit_decision(contract: dict[str, Any], contract_sha256: str) -> dict[str, Any]:
    required = set(contract["required_gate_ids"])
    blocking_gates = sorted(
        gate["gate_id"]
        for gate in contract["gates"]
        if gate["gate_id"] in required and gate["status"] == "block"
    )
    deferred_gates = sorted(
        gate["gate_id"]
        for gate in contract["gates"]
        if gate["gate_id"] in required and gate["status"] == "defer"
    )
    count_results: list[dict[str, Any]] = []
    failed_counts: list[str] = []
    for check in contract["count_checks"]:
        observed = check["observed"]
        threshold = check["threshold"]
        operator = check["operator"]
        satisfied = {
            ">=": observed >= threshold,
            ">": observed > threshold,
            "<=": observed <= threshold,
            "<": observed < threshold,
            "==": observed == threshold,
        }[operator]
        count_results.append({**check, "satisfied": satisfied, "can_authorize_training": False})
        if not satisfied and check["on_failure"] == "block":
            failed_counts.append(check["check_id"])
    if blocking_gates or failed_counts:
        decision = "block"
    elif deferred_gates:
        decision = "defer"
    else:
        decision = "pass"
    return {
        "audit_result_version": "dataset-readiness-result-v1",
        "decision_id": DECISION_ID,
        "audit_id": contract["audit_id"],
        "candidate_id": contract["candidate_id"],
        "candidate_manifest_sha256": contract["candidate_manifest_sha256"],
        "audit_input_sha256": contract_sha256,
        "decision": decision,
        "blocking_required_gate_ids": blocking_gates,
        "deferred_required_gate_ids": deferred_gates,
        "count_results": count_results,
        "failed_blocking_count_checks": sorted(failed_counts),
        "count_thresholds_can_establish_readiness_alone": False,
        "training_authorized": False,
        "training_authorization_reason": "Dataset-readiness evidence never substitutes for a separate model-readiness decision.",
        "next_action": (
            "Execute one bounded regime-replication remediation before reassessment."
            if decision == "block"
            else "Open a separately authorized dataset-and-split checkpoint."
        ),
    }


def build_report(
    candidate: dict[str, Any],
    contract: dict[str, Any],
    decision: dict[str, Any],
    bindings: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    return {
        "report_id": REPORT_ID,
        "report_version": REPORT_VERSION,
        "generated_at_utc": candidate["generated_at_utc"],
        "run_id": candidate["run_id"],
        "repository": candidate["repository"],
        "task_issue": 552,
        "git_source_commit": candidate["git_source_commit"],
        "software_version": candidate["software_version"],
        "aoi_version": AOI_VERSION,
        "target_version": TARGET_VERSION,
        "label_schema_version": LABEL_SCHEMA_VERSION,
        "label_set_version": LABEL_SET_VERSION,
        "dataset_version": None,
        "split_version": None,
        "baseline_version": None,
        "model_version": None,
        "bindings": bindings,
        "inventory": candidate["inventory"],
        "events": [
            {
                key: event[key]
                for key in (
                    "event_group_id",
                    "fire_name",
                    "year",
                    "source_regime",
                    "never_tuned_transfer",
                    "class_counts",
                    "core_pixels",
                    "unknown_ring_pixels",
                    "accepted_core_share_percent",
                )
            }
            for event in candidate["events"]
        ],
        "partition_feasibility": candidate["partition_feasibility"],
        "gate_results": {
            gate["gate_id"]: {"status": gate["status"], "finding": gate["finding"], "remediation": gate["remediation"]}
            for gate in contract["gates"]
        },
        "decision": DECISION,
        "audit_decision": decision["decision"],
        "blocking_gate_ids": decision["blocking_required_gate_ids"],
        "failed_count_checks": decision["failed_blocking_count_checks"],
        "minimum_remediation": {
            "action": (
                "Add and fully gate one event under the existing MTBS-current or BAER+MTBS+RAVG-current "
                "regime, exclude Darlene's unique NIFC-regime event from the dataset candidate, and rerun "
                "sufficiency."
            ),
            "why_smallest": (
                "The remaining five events already cover two replicated source-program regimes, both classes, "
                "unknown rings, three never-tuned transfers, and event dominance. One replacement event can "
                "restore six-event split fitness if every source, terms, quality, owner, and leakage gate passes."
            ),
            "terminal_fallback_activated": False,
        },
        "schedule": {
            "target_date": "2026-08-06",
            "risk": "critical",
            "impact": (
                "A new event requires source/terms verification, two-scene custody, raster fitness, two-class proposal, "
                "owner review, response intake, rerun sufficiency, dataset/splits/baselines, and U-Net work. Delay directly "
                "compresses model evaluation and GEOINT integration."
            ),
        },
        "boundaries": candidate["boundaries"],
        "warning": WARNING,
    }


def render_html(report: dict[str, Any]) -> str:
    inventory = report["inventory"]
    gate_rows = "".join(
        "<tr>"
        f"<th scope='row'>{escape(gate_id.replace('-', ' ').title())}</th>"
        f"<td class='{escape(value['status'])}'>{escape(value['status'].upper())}</td>"
        f"<td>{escape(value['finding'])}</td>"
        "</tr>"
        for gate_id, value in report["gate_results"].items()
    )
    event_rows = "".join(
        "<tr>"
        f"<td>{escape(event['fire_name'])}</td><td>{event['year']}</td>"
        f"<td>{event['core_pixels']}</td><td>{event['unknown_ring_pixels']}</td>"
        f"<td>{escape(event['source_regime'])}</td>"
        f"<td>{'yes' if event['never_tuned_transfer'] else 'no'}</td>"
        "</tr>"
        for event in report["events"]
    )
    blocker = report["gate_results"]["leakage-and-split-fitness"]
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>BurnLens six-event dataset sufficiency</title><style>
:root{{--ink:#123f3a;--muted:#526763;--paper:#f5f0e6;--card:#fff;--line:#b9ccc8;--pass:#14665d;--block:#9b3f24}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.5 system-ui,sans-serif}}
header{{background:#103f39;color:white;padding:42px max(24px,5vw)}}main{{max-width:1180px;margin:auto;padding:32px 24px 56px}}
h1{{margin:0 0 8px;font-size:clamp(2rem,5vw,3.2rem)}}h2{{margin-top:36px}}.metrics{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:20px}}.big{{font-size:2.35rem;font-weight:700}}
.scroll{{overflow:auto}}table{{width:100%;border-collapse:collapse;background:white}}th,td{{text-align:left;padding:12px;border-bottom:1px solid #d8e1df;vertical-align:top}}
.pass{{color:var(--pass);font-weight:800}}.block{{color:var(--block);font-weight:800}}code{{overflow-wrap:anywhere}}
.decision{{border-left:8px solid var(--block)}}@media(max-width:760px){{.metrics{{grid-template-columns:repeat(2,minmax(0,1fr))}}}}
@media(max-width:430px){{.metrics{{grid-template-columns:1fr}}th,td{{min-width:145px}}}}
</style></head><body><header><h1>Six-event dataset sufficiency</h1>
<p>Full Phase Two audit · owner-approved prototype regions · dataset remains closed</p></header><main>
<section class="metrics" aria-label="Candidate inventory">
<div class="card"><div class="big">{inventory['owner_approved_regions']}</div>prototype regions</div>
<div class="card"><div class="big">{inventory['event_groups']}</div>whole events</div>
<div class="card"><div class="big">{inventory['accepted_core_pixels']}</div>accepted core pixels</div>
<div class="card"><div class="big">{report['partition_feasibility']['valid_assignments']}</div>valid 2/2/2 splits</div>
</section>
<h2>Readiness gates</h2><div class="scroll"><table><thead><tr><th>Gate</th><th>Status</th><th>Finding</th></tr></thead><tbody>{gate_rows}</tbody></table></div>
<h2>Event evidence</h2><div class="scroll"><table><thead><tr><th>Event</th><th>Year</th><th>Core pixels</th><th>Unknown ring</th><th>Exact regime</th><th>Never-tuned transfer</th></tr></thead><tbody>{event_rows}</tbody></table></div>
<section class="card decision"><h2>Decision</h2><p><code>{escape(report['decision'])}</code></p>
<p>{escape(blocker['finding'])}</p><p><strong>Smallest credible remediation:</strong> {escape(report['minimum_remediation']['action'])}</p>
<p>The verified August 6 ZIP remains an interim contingency case study. No terminal fallback is activated.</p></section>
<p>Trace: source <code>{escape(report['git_source_commit'])}</code> · BurnLens <code>{escape(report['software_version'])}</code> · labels <code>{LABEL_SET_VERSION}</code> · run <code>{escape(report['run_id'])}</code> · dataset/split/baseline/model <code>null</code>.</p>
<p>{escape(report['warning'])}</p></main></body></html>"""


def render_png(report: dict[str, Any], path: Path) -> None:
    image = Image.new("RGB", (1800, 1320), "#f5f0e6")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default(size=26)
    small = ImageFont.load_default(size=22)
    title = ImageFont.load_default(size=48)
    big = ImageFont.load_default(size=42)
    draw.rectangle((0, 0, 1800, 180), fill="#103f39")
    draw.text((70, 42), "BurnLens six-event dataset sufficiency", fill="white", font=title)
    draw.text((70, 112), "Full Phase Two audit · dataset, split, baseline, and model remain closed", fill="#c8ddd8", font=font)
    metrics = [
        ("12", "prototype regions"),
        ("6", "whole events"),
        ("286", "accepted core pixels"),
        ("0", "valid 2/2/2 splits"),
    ]
    for index, (value, label) in enumerate(metrics):
        x = 70 + index * 420
        draw.rounded_rectangle((x, 225, x + 360, 375), radius=16, fill="white", outline="#b9ccc8", width=2)
        draw.text((x + 24, 252), value, fill="#123f3a", font=big)
        draw.text((x + 24, 320), label, fill="#526763", font=font)
    draw.text((70, 425), "Readiness gates", fill="#123f3a", font=big)
    y = 495
    for gate_id, value in report["gate_results"].items():
        status = value["status"]
        draw.rounded_rectangle((70, y, 1730, y + 62), radius=12, fill="white", outline="#d1ddda", width=2)
        draw.text((92, y + 17), gate_id.replace("-", " ").title(), fill="#123f3a", font=small)
        draw.text((655, y + 17), status.upper(), fill="#14665d" if status == "pass" else "#9b3f24", font=small)
        y += 72
    draw.rounded_rectangle((70, 1230, 1730, 1290), radius=12, fill="#fff7f2", outline="#9b3f24", width=3)
    draw.text(
        (92, 1246),
        "BLOCK: Darlene's exact NIFC evidence regime occurs in one event, so no frozen 2/2/2 split is valid.",
        fill="#7f3524",
        font=small,
    )
    image.save(path, format="PNG", optimize=False)


def write_outputs(
    repository_root: Path,
    records_directory: Path,
    public_directory: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, Path]:
    candidate = build_candidate_manifest(repository_root, generated_at_utc, run_id, git_source_commit)
    candidate_path = records_directory / f"{CANDIDATE_ID}.json"
    audit_path = records_directory / f"{AUDIT_ID}.json"
    decision_path = records_directory / f"{DECISION_ID}.json"
    json_path = public_directory / f"{REPORT_ID}.json"
    html_path = public_directory / f"{REPORT_ID}.html"
    png_path = public_directory / f"{REPORT_ID}.png"
    requested_paths = (
        candidate_path,
        audit_path,
        decision_path,
        json_path,
        html_path,
        png_path,
    )
    existing_paths = [path for path in requested_paths if path.exists()]
    if existing_paths:
        raise SixEventDatasetSufficiencyError(
            "output already exists: "
            + ", ".join(str(path) for path in existing_paths)
        )
    candidate_bytes = _json_bytes(candidate)
    _write_new(candidate_path, candidate_bytes)

    contract = build_audit_contract(candidate, sha256(candidate_bytes).hexdigest())
    audit_bytes = _json_bytes(contract)
    _write_new(audit_path, audit_bytes)

    decision = build_audit_decision(contract, sha256(audit_bytes).hexdigest())
    decision_bytes = _json_bytes(decision)
    _write_new(decision_path, decision_bytes)

    bindings = {
        "candidate_manifest": _canonical_binding(
            candidate_path,
            f"records/phase-two/readiness/{candidate_path.name}",
        ),
        "audit_contract": _canonical_binding(
            audit_path,
            f"records/phase-two/readiness/{audit_path.name}",
        ),
        "audit_decision": _canonical_binding(
            decision_path,
            f"records/phase-two/readiness/{decision_path.name}",
        ),
    }
    report = build_report(candidate, contract, decision, bindings)
    public_directory.mkdir(parents=True, exist_ok=True)
    _write_new(html_path, render_html(report).encode("utf-8"))
    render_png(report, png_path)
    report["outputs"] = [
        _canonical_binding(
            html_path,
            f"samples/labels/readiness/phase-two/{html_path.name}",
        ),
        _canonical_binding(
            png_path,
            f"samples/labels/readiness/phase-two/{png_path.name}",
        ),
    ]
    _write_new(json_path, _json_bytes(report))
    return {
        "candidate": candidate_path,
        "audit": audit_path,
        "decision": decision_path,
        "json": json_path,
        "html": html_path,
        "png": png_path,
    }
