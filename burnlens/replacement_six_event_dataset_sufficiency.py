"""Audit the replacement six-event prototype pool without mutating v0.50 evidence."""

from __future__ import annotations

from collections import Counter
from hashlib import sha256
from html import escape
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from . import __version__
from .six_event_dataset_sufficiency import (
    SixEventDatasetSufficiencyError,
    _binding,
    _canonical_binding,
    _candidate_class,
    _inspect_raster,
    _json_bytes,
    _read_json,
    _validate_record_bindings,
    _write_new,
    prospective_partitions,
)


REPORT_ID = "SIX-EVENT-DATASET-SUFFICIENCY-2026-002"
CANDIDATE_ID = "DATASET-CANDIDATE-2026-002"
AUDIT_ID = "DATASET-READINESS-AUDIT-2026-002"
DECISION_ID = "DATASET-READINESS-DECISION-2026-002"
REPORT_VERSION = "six-event-dataset-sufficiency-v0.2.0"
AUDIT_CONTRACT_VERSION = "dataset-readiness-audit-v1"
LABEL_SET_VERSION = "owner-approved-prototype-region-labels-v0.5.0"
LABEL_SCHEMA_VERSION = "burn-scar-binary-region-label-schema-v0.3.0"
TARGET_VERSION = "target-burn-scar-v0.2.0"
AOI_VERSION = "multi-event-native-grids-v0.5.0"
TASK_ISSUE = 554
UNIT_ID = "P2O4-T39-U08"
DECISION = (
    "PASS_SIX_EVENT_DATASET_SUFFICIENCY_"
    "AUTHORIZE_DATASET_SPLIT_QA_BASELINE_CHECKPOINT"
)
WARNING = (
    "Experimental BurnLens owner-approved prototype evidence. Not independent "
    "ground truth, official wildfire information, emergency guidance, or field "
    "validation. Official sources govern."
)


EVENTS: tuple[dict[str, Any], ...] = (
    {
        "event_group_id": "event-mckay-1035-ne-2017",
        "fire_name": "McKay 1035 NE",
        "year": 2017,
        "proposal": (
            "samples/labels/pilot/phase-two/"
            "REGION-CANDIDATE-PILOT-2026-001.json"
        ),
        "intake": (
            "samples/labels/review/regions/phase-two/intake/"
            "REGION-OWNER-RESPONSE-INTAKE-2026-001.json"
        ),
        "candidate_ids": ("RCP-003", "RCP-004"),
        "source_regime": "sentinel2-mtbs-current-v1",
        "source_programs": ("COPERNICUS_SENTINEL_2", "MTBS"),
        "never_tuned_transfer": False,
    },
    {
        "event_group_id": "event-tepee-1144-ne-2018",
        "fire_name": "Tepee 1144 NE",
        "year": 2018,
        "proposal": (
            "samples/labels/pilot/phase-two/"
            "REGION-CANDIDATE-PILOT-2026-001.json"
        ),
        "intake": (
            "samples/labels/review/regions/phase-two/intake/"
            "REGION-OWNER-RESPONSE-INTAKE-2026-001.json"
        ),
        "candidate_ids": ("RCP-005", "RCP-006"),
        "source_regime": "sentinel2-mtbs-current-v1",
        "source_programs": ("COPERNICUS_SENTINEL_2", "MTBS"),
        "never_tuned_transfer": False,
    },
    {
        "event_group_id": "event-green-ridge-0684-cs-2020",
        "fire_name": "Green Ridge 0684 CS",
        "year": 2020,
        "proposal": (
            "samples/labels/pilot/green-ridge/phase-two/"
            "GREEN-RIDGE-REGION-PROPOSAL-2026-001.json"
        ),
        "intake": (
            "samples/labels/review/green-ridge/phase-two/intake/"
            "GREEN-RIDGE-OWNER-RESPONSE-INTAKE-2026-001.json"
        ),
        "candidate_ids": ("GRP-001", "GRP-002"),
        "source_regime": "sentinel2-baer-mtbs-ravg-current-v1",
        "source_programs": (
            "COPERNICUS_SENTINEL_2",
            "BAER",
            "MTBS",
            "RAVG",
        ),
        "never_tuned_transfer": True,
    },
    {
        "event_group_id": "event-grandview-0558-od-2021",
        "fire_name": "Grandview 0558 OD",
        "year": 2021,
        "proposal": (
            "samples/labels/pilot/grandview/phase-two/"
            "GRANDVIEW-REGION-PROPOSAL-2026-001.json"
        ),
        "intake": (
            "samples/labels/review/grandview/phase-two/intake/"
            "GRANDVIEW-OWNER-RESPONSE-INTAKE-2026-001.json"
        ),
        "candidate_ids": ("GVP-001", "GVP-002"),
        "source_regime": "sentinel2-baer-mtbs-ravg-current-v1",
        "source_programs": (
            "COPERNICUS_SENTINEL_2",
            "BAER",
            "MTBS",
            "RAVG",
        ),
        "never_tuned_transfer": True,
    },
    {
        "event_group_id": "event-windigo-2022",
        "fire_name": "Windigo",
        "year": 2022,
        "proposal": (
            "samples/labels/pilot/windigo/phase-two/"
            "WINDIGO-REGION-PROPOSAL-2026-001.json"
        ),
        "intake": (
            "samples/labels/review/windigo/phase-two/intake/"
            "WINDIGO-OWNER-RESPONSE-INTAKE-2026-001.json"
        ),
        "candidate_ids": ("WDP-001", "WDP-002"),
        "source_regime": "sentinel2-baer-mtbs-ravg-current-v1",
        "source_programs": (
            "COPERNICUS_SENTINEL_2",
            "BAER",
            "MTBS",
            "RAVG",
        ),
        "never_tuned_transfer": True,
    },
    {
        "event_group_id": "event-ward-creek-2019",
        "fire_name": "Ward Creek",
        "year": 2019,
        "proposal": (
            "samples/labels/pilot/ward-creek/phase-two/"
            "region-proposal-v0.1.0/"
            "WARD-CREEK-REGION-PROPOSAL-2026-001.json"
        ),
        "intake": (
            "samples/labels/review/ward-creek/phase-two/intake/"
            "WARD-CREEK-OWNER-RESPONSE-INTAKE-2026-001.json"
        ),
        "candidate_ids": ("WCP-001", "WCP-002"),
        "source_regime": "sentinel2-mtbs-current-v1",
        "source_programs": ("COPERNICUS_SENTINEL_2", "MTBS"),
        "never_tuned_transfer": False,
    },
)


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
            proposal_bindings[config["proposal"]] = _binding(
                repository_root,
                proposal_path,
            )
        if config["intake"] not in intakes:
            intakes[config["intake"]] = _read_json(intake_path)
            intake_bindings[config["intake"]] = _binding(
                repository_root,
                intake_path,
            )
            intake = intakes[config["intake"]]
            if any(
                value is not True
                for value in intake.get("promotion_gates", {}).values()
            ):
                raise SixEventDatasetSufficiencyError(
                    f"promotion gate is not passed: {intake_path.name}"
                )
            if int(intake.get("decision_counts", {}).get("yes", 0)) <= 0:
                raise SixEventDatasetSufficiencyError(
                    f"owner yes evidence is absent: {intake_path.name}"
                )
            boundary_keys = (
                "owner_review_is_independent_ground_truth",
                "unknown_ring_is_background",
                "dataset_created",
                "split_created",
                "baseline_created",
                "model_created",
                "accuracy_or_operational_claim_created",
            )
            if any(
                intake.get("boundaries", {}).get(key) is not False
                for key in boundary_keys
            ):
                raise SixEventDatasetSufficiencyError(
                    f"intake boundary drift: {intake_path.name}"
                )
            sources, terms = _validate_record_bindings(
                repository_root,
                intake,
            )
            source_records.update(
                (item["record_id"], item) for item in sources
            )
            terms_records.update(
                (item["record_id"], item) for item in terms
            )

        proposal = proposals[config["proposal"]]
        candidates_by_id = {
            candidate["candidate_id"]: candidate
            for candidate in proposal["candidates"]
        }
        event_candidates: list[dict[str, Any]] = []
        for candidate_id in config["candidate_ids"]:
            if candidate_id not in candidates_by_id:
                raise SixEventDatasetSufficiencyError(
                    f"candidate missing from proposal: {candidate_id}"
                )
            candidate = candidates_by_id[candidate_id]
            candidate_class = _candidate_class(candidate)
            raster_path = proposal_path.parent / candidate["candidate_raster"]
            raster_binding = _binding(repository_root, raster_path)
            if raster_binding["sha256"] in raster_hashes:
                raise SixEventDatasetSufficiencyError(
                    "duplicate candidate raster bytes"
                )
            raster_hashes.add(raster_binding["sha256"])
            event_candidates.append(
                {
                    "candidate_id": candidate_id,
                    "class": candidate_class,
                    "core_pixels": int(candidate["core_pixels"]),
                    "core_area_hectares": round(
                        int(candidate["core_pixels"]) * 0.04,
                        2,
                    ),
                    "unknown_ring_pixels": int(
                        candidate["unknown_ring_pixels"]
                    ),
                    "raster": raster_binding,
                    "raster_contract": _inspect_raster(
                        raster_path,
                        candidate,
                    ),
                }
            )
        class_counts = Counter(
            candidate["class"] for candidate in event_candidates
        )
        if class_counts != {"background": 1, "burned": 1}:
            raise SixEventDatasetSufficiencyError(
                f"event class roster drift: {config['event_group_id']}"
            )
        events.append(
            {
                "event_group_id": config["event_group_id"],
                "fire_name": config["fire_name"],
                "year": config["year"],
                "source_regime": config["source_regime"],
                "source_programs": list(config["source_programs"]),
                "never_tuned_transfer": config["never_tuned_transfer"],
                "class_counts": dict(sorted(class_counts.items())),
                "core_pixels": sum(
                    candidate["core_pixels"]
                    for candidate in event_candidates
                ),
                "unknown_ring_pixels": sum(
                    candidate["unknown_ring_pixels"]
                    for candidate in event_candidates
                ),
                "candidates": event_candidates,
                "proposal": proposal_bindings[config["proposal"]],
                "owner_intake": intake_bindings[config["intake"]],
            }
        )

    if len(events) != 6:
        raise SixEventDatasetSufficiencyError(
            "exactly six event groups are required"
        )
    if any(
        event["event_group_id"] == "event-darlene3-or-2024"
        for event in events
    ):
        raise SixEventDatasetSufficiencyError(
            "Darlene is forbidden in the replacement candidate"
        )
    final_intake_path = (
        "samples/labels/review/ward-creek/phase-two/intake/"
        "WARD-CREEK-OWNER-RESPONSE-INTAKE-2026-001.json"
    )
    final_intake = intakes[final_intake_path]
    final_outcome = final_intake["outcome"]
    if (
        final_intake.get("label_set_version") != LABEL_SET_VERSION
        or int(
            final_outcome.get(
                "cumulative_owner_approved_region_labels",
                0,
            )
        )
        != 14
        or int(
            final_outcome.get("cumulative_accepted_core_pixels", 0)
        )
        != 325
        or int(
            final_outcome.get(
                "cumulative_excluded_unknown_ring_pixels",
                0,
            )
        )
        != 599
    ):
        raise SixEventDatasetSufficiencyError(
            "final label-set aggregate drift"
        )

    total_core = sum(event["core_pixels"] for event in events)
    total_ring = sum(event["unknown_ring_pixels"] for event in events)
    if total_core != 287 or total_ring != 531:
        raise SixEventDatasetSufficiencyError(
            "replacement candidate aggregate drift"
        )
    for event in events:
        event["accepted_core_share_percent"] = round(
            100 * event["core_pixels"] / total_core,
            4,
        )

    regimes = Counter(event["source_regime"] for event in events)
    programs = Counter(
        program
        for event in events
        for program in event["source_programs"]
    )
    expected_regimes = {
        "sentinel2-baer-mtbs-ravg-current-v1": 3,
        "sentinel2-mtbs-current-v1": 3,
    }
    if dict(sorted(regimes.items())) != expected_regimes:
        raise SixEventDatasetSufficiencyError(
            "replacement source-regime roster drift"
        )
    partitions = prospective_partitions(events)
    return {
        "candidate_manifest_version": (
            "burnlens-dataset-candidate-v0.2.0"
        ),
        "candidate_id": CANDIDATE_ID,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": TASK_ISSUE,
        "unit_id": UNIT_ID,
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
            "source_records": sorted(
                source_records.values(),
                key=lambda item: item["record_id"],
            ),
            "terms_records": sorted(
                terms_records.values(),
                key=lambda item: item["record_id"],
            ),
        },
        "inventory": {
            "event_groups": len(events),
            "owner_approved_regions": sum(
                len(event["candidates"]) for event in events
            ),
            "class_counts": {"background": 6, "burned": 6},
            "accepted_core_pixels": total_core,
            "accepted_core_area_hectares": round(total_core * 0.04, 2),
            "excluded_unknown_ring_pixels": total_ring,
            "maximum_event_core_share_percent": max(
                event["accepted_core_share_percent"]
                for event in events
            ),
            "balanced_review_roster_is_natural_prevalence": False,
        },
        "events": events,
        "source_regime_counts": dict(sorted(regimes.items())),
        "source_program_counts": dict(sorted(programs.items())),
        "partition_feasibility": partitions,
        "excluded_event_groups": [
            {
                "event_group_id": "event-darlene3-or-2024",
                "reason": (
                    "Unique NIFC context regime excluded under issue #554; "
                    "historical evidence remains immutable."
                ),
            }
        ],
        "limitations": [
            (
                "The labels are disclosed owner-approved prototype regions, "
                "not independent ground truth."
            ),
            (
                "The balanced review roster does not estimate natural "
                "burned/background prevalence."
            ),
            (
                "Only 287 native 20 m core pixels are accepted; any later "
                "model is a small-data experiment."
            ),
            (
                "Darlene remains immutable prototype evidence but is excluded "
                "from this candidate to remove its unique NIFC source regime."
            ),
            (
                "A sufficiency pass authorizes only a separate dataset, split, "
                "QA, and baseline checkpoint; it does not authorize training."
            ),
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


def build_audit_contract(
    candidate: dict[str, Any],
    candidate_sha256: str,
) -> dict[str, Any]:
    inventory = candidate["inventory"]
    partitions = candidate["partition_feasibility"]
    unique_regimes = sorted(
        regime
        for regime, count in candidate["source_regime_counts"].items()
        if count < 2
    )
    unique_programs = sorted(
        program
        for program, count in candidate["source_program_counts"].items()
        if count < 2
    )
    valid_split = (
        partitions["valid_assignments"] > 0
        and not unique_regimes
        and not unique_programs
    )
    if not valid_split:
        raise SixEventDatasetSufficiencyError(
            "replacement split fitness unexpectedly failed"
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
            "finding": (
                "Every intake binds exact current source and terms records; "
                "provider bytes remain private and official sources govern."
            ),
            "remediation": "",
        },
        {
            "gate_id": "provenance-and-custody",
            "category": "provenance_and_custody",
            "required": True,
            "status": "pass",
            "evidence_refs": [
                f"{CANDIDATE_ID}.json input_bindings",
                "five aggregate owner-intake reports covering six events",
            ],
            "finding": (
                "All proposals, rasters, aggregate intakes, source records, "
                "and terms records match immutable byte and SHA-256 identities."
            ),
            "remediation": "",
        },
        {
            "gate_id": "schema-and-quality",
            "category": "schema_and_quality",
            "required": True,
            "status": "pass",
            "evidence_refs": [
                f"{CANDIDATE_ID}.json events[].candidates[].raster_contract",
                "owner intake promotion_gates.quality_and_registration",
            ],
            "finding": (
                "All 12 EPSG:32610 rasters are single-band, nodata 255, "
                "domain 0/1/2/255, count-exact, and contain one 8-connected core."
            ),
            "remediation": "",
        },
        {
            "gate_id": "coverage-and-balance",
            "category": "coverage_and_balance",
            "required": True,
            "status": "pass",
            "evidence_refs": [
                f"{CANDIDATE_ID}.json inventory",
                "issue #554 success exit",
            ],
            "finding": (
                "Six events each contribute one burned and one background "
                f"region; no event exceeds "
                f"{inventory['maximum_event_core_share_percent']:.4f}% of "
                f"{inventory['accepted_core_pixels']} accepted core pixels. "
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
                f"{CANDIDATE_ID}.json inventory.excluded_unknown_ring_pixels",
                "candidate raster value 2 contracts",
            ],
            "finding": (
                f"All {inventory['excluded_unknown_ring_pixels']} reviewed "
                "unknown-ring pixels remain explicit value-2 exclusions and "
                "are never background."
            ),
            "remediation": "",
        },
        {
            "gate_id": "leakage-and-split-fitness",
            "category": "leakage_and_split_fitness",
            "required": True,
            "status": "pass",
            "evidence_refs": [
                f"{CANDIDATE_ID}.json partition_feasibility",
                "issue #554 exact six-event roster",
            ],
            "finding": (
                f"{partitions['valid_assignments']} of "
                f"{partitions['total_2_2_2_assignments']} whole-event 2/2/2 "
                "assignments satisfy transfer reservation and exact "
                "source-program/regime replication. Darlene is excluded."
            ),
            "remediation": "",
        },
        {
            "gate_id": "reproducibility",
            "category": "reproducibility",
            "required": True,
            "status": "pass",
            "evidence_refs": [
                "locked uv environment",
                f"{CANDIDATE_ID}.json exact reconstruction",
            ],
            "finding": (
                "The evaluator reopens and validates every tracked input and "
                "raster under the locked repository environment."
            ),
            "remediation": "",
        },
        {
            "gate_id": "evaluation-design",
            "category": "evaluation_design",
            "required": True,
            "status": "pass",
            "evidence_refs": [
                f"{CANDIDATE_ID}.json partition_feasibility",
                "three never-tuned transfer events",
            ],
            "finding": (
                "Three never-tuned transfer events exist and 54 whole-event "
                "assignments can reserve transfer evidence in validation and "
                "test while replicating both exact source regimes."
            ),
            "remediation": "",
        },
        {
            "gate_id": "human-review",
            "category": "human_review",
            "required": True,
            "status": "pass",
            "evidence_refs": [
                "five aggregate owner-response intake reports",
                "owner intake promotion_gates",
            ],
            "finding": (
                "Every accepted region has exact owner-yes custody plus passed "
                "non-owner gates; yes remains necessary but insufficient."
            ),
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
            "finding": (
                "The audit exposes only aggregate tracked evidence and "
                "preserves null dataset/split/baseline/model versions and "
                "prototype-label limitations."
            ),
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
            {
                "check_id": "minimum-event-groups",
                "observed": inventory["event_groups"],
                "operator": ">=",
                "threshold": 6,
                "on_failure": "block",
            },
            {
                "check_id": "binary-classes-per-event",
                "observed": 2,
                "operator": ">=",
                "threshold": 2,
                "on_failure": "block",
            },
            {
                "check_id": "unknown-ring-pixels",
                "observed": inventory["excluded_unknown_ring_pixels"],
                "operator": ">",
                "threshold": 0,
                "on_failure": "block",
            },
            {
                "check_id": "maximum-event-core-share-percent",
                "observed": inventory["maximum_event_core_share_percent"],
                "operator": "<=",
                "threshold": 50,
                "on_failure": "block",
            },
            {
                "check_id": "never-tuned-transfer-events",
                "observed": sum(
                    bool(event["never_tuned_transfer"])
                    for event in candidate["events"]
                ),
                "operator": ">=",
                "threshold": 2,
                "on_failure": "block",
            },
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


def build_audit_decision(
    contract: dict[str, Any],
    contract_sha256: str,
) -> dict[str, Any]:
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
        satisfied = {
            ">=": observed >= threshold,
            ">": observed > threshold,
            "<=": observed <= threshold,
            "<": observed < threshold,
            "==": observed == threshold,
        }[check["operator"]]
        count_results.append(
            {
                **check,
                "satisfied": satisfied,
                "can_authorize_training": False,
            }
        )
        if not satisfied and check["on_failure"] == "block":
            failed_counts.append(check["check_id"])
    if blocking_gates or failed_counts:
        decision = "block"
    elif deferred_gates:
        decision = "defer"
    else:
        decision = "pass"
    if decision != "pass":
        raise SixEventDatasetSufficiencyError(
            "replacement readiness audit did not pass"
        )
    return {
        "audit_result_version": "dataset-readiness-result-v1",
        "decision_id": DECISION_ID,
        "audit_id": contract["audit_id"],
        "candidate_id": contract["candidate_id"],
        "candidate_manifest_sha256": contract[
            "candidate_manifest_sha256"
        ],
        "audit_input_sha256": contract_sha256,
        "decision": decision,
        "blocking_required_gate_ids": blocking_gates,
        "deferred_required_gate_ids": deferred_gates,
        "count_results": count_results,
        "failed_blocking_count_checks": sorted(failed_counts),
        "count_thresholds_can_establish_readiness_alone": False,
        "training_authorized": False,
        "training_authorization_reason": (
            "Dataset-readiness evidence never substitutes for the separate "
            "dataset/split/QA/baseline and model-readiness checkpoints."
        ),
        "next_action": (
            "Open the separately authorized dataset, whole-event split, QA, "
            "and strongest non-model baseline checkpoint. Training remains closed."
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
        "task_issue": TASK_ISSUE,
        "unit_id": UNIT_ID,
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
        "excluded_event_groups": candidate["excluded_event_groups"],
        "source_regime_counts": candidate["source_regime_counts"],
        "source_program_counts": candidate["source_program_counts"],
        "partition_feasibility": candidate["partition_feasibility"],
        "gate_results": {
            gate["gate_id"]: {
                "status": gate["status"],
                "finding": gate["finding"],
                "remediation": gate["remediation"],
            }
            for gate in contract["gates"]
        },
        "decision": DECISION,
        "audit_decision": decision["decision"],
        "blocking_gate_ids": decision[
            "blocking_required_gate_ids"
        ],
        "failed_count_checks": decision[
            "failed_blocking_count_checks"
        ],
        "next_checkpoint": {
            "scope": (
                "Create the accepted versioned dataset, lock one of the valid "
                "whole-event splits before patching, run dataset QA, and "
                "evaluate strongest justified non-model baselines."
            ),
            "training_authorized": False,
            "dataset_created_here": False,
            "split_created_here": False,
        },
        "schedule": {
            "target_date": "2026-08-06",
            "risk": "critical",
            "impact": (
                "Dataset/split/QA/baselines, model readiness, U-Net training, "
                "evaluation, and the GEOINT vertical slice remain on the "
                "critical path."
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
        f"<td class='{escape(value['status'])}'>"
        f"{escape(value['status'].upper())}</td>"
        f"<td>{escape(value['finding'])}</td>"
        "</tr>"
        for gate_id, value in report["gate_results"].items()
    )
    event_rows = "".join(
        "<tr>"
        f"<td>{escape(event['fire_name'])}</td><td>{event['year']}</td>"
        f"<td>{event['core_pixels']}</td>"
        f"<td>{event['unknown_ring_pixels']}</td>"
        f"<td>{escape(event['source_regime'])}</td>"
        f"<td>{'yes' if event['never_tuned_transfer'] else 'no'}</td>"
        "</tr>"
        for event in report["events"]
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>BurnLens replacement six-event dataset sufficiency</title><style>
:root{{--ink:#123f3a;--muted:#526763;--paper:#f5f0e6;--card:#fff;--line:#b9ccc8;--pass:#14665d}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.5 system-ui,sans-serif;overflow-wrap:anywhere}}
header{{background:#103f39;color:white;padding:42px max(24px,5vw)}}main{{max-width:1180px;margin:auto;padding:32px 24px 56px}}
h1{{margin:0 0 8px;font-size:clamp(2rem,5vw,3.2rem)}}h2{{margin-top:36px}}.metrics{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px}}
.card{{min-width:0;background:var(--card);border:1px solid var(--line);border-radius:14px;padding:20px}}.big{{font-size:2.35rem;font-weight:700}}
.scroll{{max-width:100%;overflow:auto}}table{{width:100%;border-collapse:collapse;background:white}}th,td{{text-align:left;padding:12px;border-bottom:1px solid #d8e1df;vertical-align:top}}
.pass{{color:var(--pass);font-weight:800}}code{{overflow-wrap:anywhere}}
.decision{{border-left:8px solid var(--pass)}}@media(max-width:760px){{.metrics{{grid-template-columns:repeat(2,minmax(0,1fr))}}}}
@media(max-width:430px){{.metrics{{grid-template-columns:1fr}}th,td{{min-width:145px}}main{{padding:20px 12px 42px}}}}
</style></head><body><header><h1>Replacement six-event sufficiency passes</h1>
<p>Full Phase Two audit · owner-approved prototype regions · training remains closed</p></header><main>
<section class="metrics" aria-label="Candidate inventory">
<div class="card"><div class="big">{inventory['owner_approved_regions']}</div>prototype regions</div>
<div class="card"><div class="big">{inventory['event_groups']}</div>whole events</div>
<div class="card"><div class="big">{inventory['accepted_core_pixels']}</div>accepted core pixels</div>
<div class="card"><div class="big">{report['partition_feasibility']['valid_assignments']}</div>valid 2/2/2 assignments</div>
</section>
<h2>Readiness gates</h2><div class="scroll"><table><thead><tr><th>Gate</th><th>Status</th><th>Finding</th></tr></thead><tbody>{gate_rows}</tbody></table></div>
<h2>Event evidence</h2><div class="scroll"><table><thead><tr><th>Event</th><th>Year</th><th>Core pixels</th><th>Unknown ring</th><th>Exact regime</th><th>Never-tuned transfer</th></tr></thead><tbody>{event_rows}</tbody></table></div>
<section class="card decision"><h2>Decision</h2><p><code>{escape(report['decision'])}</code></p>
<p>All ten required non-count gates pass. Three MTBS-current events and three BAER/MTBS/RAVG-current events yield {report['partition_feasibility']['valid_assignments']} valid whole-event assignments. Darlene is excluded from this candidate while its historical evidence remains immutable.</p>
<p><strong>Next checkpoint:</strong> {escape(report['next_checkpoint']['scope'])}</p>
<p>This pass creates no dataset, split, baseline, model, metric, or training authorization.</p></section>
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
    draw.text(
        (70, 42),
        "BurnLens replacement six-event sufficiency",
        fill="white",
        font=title,
    )
    draw.text(
        (70, 112),
        "All required gates pass; dataset and training remain separate",
        fill="#c8ddd8",
        font=font,
    )
    inventory = report["inventory"]
    metrics = [
        (str(inventory["owner_approved_regions"]), "prototype regions"),
        (str(inventory["event_groups"]), "whole events"),
        (str(inventory["accepted_core_pixels"]), "accepted core pixels"),
        (
            str(report["partition_feasibility"]["valid_assignments"]),
            "valid 2/2/2 assignments",
        ),
    ]
    for index, (value, label) in enumerate(metrics):
        x = 70 + index * 420
        draw.rounded_rectangle(
            (x, 225, x + 360, 375),
            radius=16,
            fill="white",
            outline="#b9ccc8",
            width=2,
        )
        draw.text((x + 24, 252), value, fill="#123f3a", font=big)
        draw.text((x + 24, 320), label, fill="#526763", font=font)
    draw.text((70, 425), "Readiness gates", fill="#123f3a", font=big)
    y = 495
    for gate_id, value in report["gate_results"].items():
        draw.rounded_rectangle(
            (70, y, 1730, y + 62),
            radius=12,
            fill="white",
            outline="#d1ddda",
            width=2,
        )
        draw.text(
            (92, y + 17),
            gate_id.replace("-", " ").title(),
            fill="#123f3a",
            font=small,
        )
        draw.text(
            (655, y + 17),
            value["status"].upper(),
            fill="#14665d",
            font=small,
        )
        y += 72
    draw.rounded_rectangle(
        (70, 1230, 1730, 1290),
        radius=12,
        fill="#eef8f5",
        outline="#14665d",
        width=3,
    )
    draw.text(
        (92, 1246),
        (
            "PASS: 54 whole-event assignments satisfy the frozen regime, "
            "program, and transfer rules. Training remains closed."
        ),
        fill="#123f3a",
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
    candidate = build_candidate_manifest(
        repository_root,
        generated_at_utc,
        run_id,
        git_source_commit,
    )
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
    existing = [path for path in requested_paths if path.exists()]
    if existing:
        raise SixEventDatasetSufficiencyError(
            "output already exists: "
            + ", ".join(str(path) for path in existing)
        )
    candidate_bytes = _json_bytes(candidate)
    _write_new(candidate_path, candidate_bytes)
    contract = build_audit_contract(
        candidate,
        sha256(candidate_bytes).hexdigest(),
    )
    audit_bytes = _json_bytes(contract)
    _write_new(audit_path, audit_bytes)
    decision = build_audit_decision(
        contract,
        sha256(audit_bytes).hexdigest(),
    )
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
