"""Freeze the exact Phase Two dataset, preprocessing, and evaluation contract."""

from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
from typing import Any

import rasterio

from . import __version__


CONTRACT_ID = "DATASET-BUILD-CONTRACT-2026-001"
CONTRACT_VERSION = "burnlens-dataset-build-contract-v0.1.0"
AUDIT_ID = "DATASET-READINESS-AUDIT-2026-003"
CANDIDATE_ID = "DATASET-CANDIDATE-2026-002"
CANDIDATE_PATH = Path("records/phase-two/readiness") / f"{CANDIDATE_ID}.json"
PRIOR_AUDIT_PATH = Path(
    "records/phase-two/readiness/DATASET-READINESS-AUDIT-2026-002.json"
)
PRIOR_DECISION_PATH = Path(
    "records/phase-two/readiness/DATASET-READINESS-DECISION-2026-002.json"
)
CANDIDATE_SHA256 = (
    "4a9646af493cdce81d0cd57405ebccf0dfecf5ca77c96930d0837c3b7d4e65f2"
)
PRIOR_AUDIT_SHA256 = (
    "50e3b9f3c6c33a9f8cd36cf0952bf5033c039e68ffc864bf952ddec5442e6ed4"
)
TASK_ISSUE = 562
UNIT_ID = "P2O5-T03-U01"
EXPECTED_EVENT_IDS = (
    "event-mckay-1035-ne-2017",
    "event-tepee-1144-ne-2018",
    "event-green-ridge-0684-cs-2020",
    "event-grandview-0558-od-2021",
    "event-windigo-2022",
    "event-ward-creek-2019",
)
FEATURE_BANDS = ("B04", "B8A", "B12")
FEATURE_CHANNELS = tuple(
    f"{temporal}_{band}"
    for temporal in ("pre", "post")
    for band in FEATURE_BANDS
)
SOURCE_REPORTS = {
    "event-mckay-1035-ne-2017": (
        "samples/cross-event/phase-two/"
        "CROSS-EVENT-SOURCE-FITNESS-2026-001.json"
    ),
    "event-tepee-1144-ne-2018": (
        "samples/cross-event/phase-two/"
        "CROSS-EVENT-SOURCE-FITNESS-2026-001.json"
    ),
    "event-green-ridge-0684-cs-2020": (
        "samples/cross-event/phase-two/"
        "GREEN-RIDGE-SOURCE-FITNESS-2026-001.json"
    ),
    "event-grandview-0558-od-2021": (
        "samples/cross-event/phase-two/"
        "GRANDVIEW-SOURCE-FITNESS-2026-001.json"
    ),
    "event-windigo-2022": (
        "samples/cross-event/phase-two/windigo/"
        "WINDIGO-SOURCE-FITNESS-2026-006.json"
    ),
    "event-ward-creek-2019": (
        "samples/reference/phase-two/ward-creek/"
        "reference-fitness-v0.1.1/"
        "WARD-CREEK-REFERENCE-FITNESS-2026-002.json"
    ),
}


class DatasetBuildContractError(RuntimeError):
    """A deterministic dataset-contract validation failure."""


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


def _binding(root: Path, relative: str | Path) -> dict[str, Any]:
    relative_path = Path(relative)
    path = root / relative_path
    if not path.is_file():
        raise DatasetBuildContractError(
            f"required input is absent: {relative_path.as_posix()}"
        )
    return {
        "path": relative_path.as_posix(),
        "bytes": path.stat().st_size,
        "sha256": _sha256_file(path),
    }


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise DatasetBuildContractError(f"JSON root is not an object: {path}")
    return value


def _verify_binding(root: Path, binding: dict[str, Any]) -> None:
    observed = _binding(root, binding["path"])
    if observed != {
        "path": binding["path"],
        "bytes": binding["bytes"],
        "sha256": binding["sha256"],
    }:
        raise DatasetBuildContractError(
            f"binding drift: {binding['path']}"
        )


def _walk_products(value: Any) -> list[dict[str, Any]]:
    products: list[dict[str, Any]] = []
    if isinstance(value, dict):
        if isinstance(value.get("role"), str) and isinstance(
            value.get("rasters"), dict
        ):
            products.append(value)
        for child in value.values():
            products.extend(_walk_products(child))
    elif isinstance(value, list):
        for child in value:
            products.extend(_walk_products(child))
    return products


def _pair_products(
    report: dict[str, Any], event_id: str
) -> tuple[dict[str, Any], dict[str, Any]]:
    event_token = {
        "event-mckay-1035-ne-2017": "mckay-2017",
        "event-tepee-1144-ne-2018": "tepee-2018",
        "event-green-ridge-0684-cs-2020": "green-ridge-2020",
        "event-grandview-0558-od-2021": "grandview-2021",
        "event-windigo-2022": "windigo-2022",
        "event-ward-creek-2019": "ward-creek-2019",
    }[event_id]
    selected = [
        product
        for product in _walk_products(report)
        if product["role"].startswith(event_token)
    ]
    by_temporal = {
        temporal: [
            product
            for product in selected
            if product["role"].endswith(f"-{temporal}")
        ]
        for temporal in ("pre", "post")
    }
    if any(len(products) != 1 for products in by_temporal.values()):
        raise DatasetBuildContractError(
            f"exact pre/post source pair is not unique: {event_id}"
        )
    return by_temporal["pre"][0], by_temporal["post"][0]


def _product_contract(
    product: dict[str, Any], temporal: str
) -> dict[str, Any]:
    metadata = product.get("product_metadata", {})
    rasters = product["rasters"]
    required = set(FEATURE_BANDS) | {"SCL"}
    if not required.issubset(rasters):
        raise DatasetBuildContractError(
            f"source product lacks common native bands: {product['role']}"
        )
    reference = rasters["B04"]
    grid_fields = ("crs", "resolution_m", "source_width", "source_height")
    for band in required:
        raster = rasters[band]
        if any(raster.get(field) != reference.get(field) for field in grid_fields):
            raise DatasetBuildContractError(
                f"native band grid mismatch: {product['role']} {band}"
            )
        if raster.get("source_transform") != reference.get("source_transform"):
            raise DatasetBuildContractError(
                f"native band transform mismatch: {product['role']} {band}"
            )
    if reference.get("crs") != "EPSG:32610" or reference.get(
        "resolution_m"
    ) != 20:
        raise DatasetBuildContractError(
            f"source product is not native EPSG:32610 at 20 m: {product['role']}"
        )
    quantification = metadata.get("boa_quantification_value")
    offsets = metadata.get("boa_offsets", {})
    if quantification != 10000.0 or any(
        band not in offsets for band in FEATURE_BANDS
    ):
        raise DatasetBuildContractError(
            f"reflectance metadata is incomplete: {product['role']}"
        )
    return {
        "temporal_role": temporal,
        "role": product["role"],
        "provider_id": product.get("provider_id"),
        "native_id": product.get("native_id"),
        "filename": product.get("filename"),
        "processing_baseline": metadata.get("processing_baseline"),
        "sensing_time_utc": metadata.get("sensing_time_utc"),
        "crs": reference["crs"],
        "resolution_m": reference["resolution_m"],
        "source_shape": [
            reference["source_height"],
            reference["source_width"],
        ],
        "source_transform": reference["source_transform"],
        "boa_quantification_value": quantification,
        "boa_offsets": {
            band: offsets[band] for band in FEATURE_BANDS
        },
        "nodata_dn": metadata.get("nodata_dn"),
        "saturated_dn": metadata.get("saturated_dn"),
        "members": {
            band: rasters[band]["member"]
            for band in (*FEATURE_BANDS, "SCL")
        },
    }


def _validate_candidate(root: Path) -> dict[str, Any]:
    candidate_binding = _binding(root, CANDIDATE_PATH)
    if candidate_binding["sha256"] != CANDIDATE_SHA256:
        raise DatasetBuildContractError("candidate manifest hash drift")
    candidate = _read_json(root / CANDIDATE_PATH)
    if candidate.get("candidate_id") != CANDIDATE_ID:
        raise DatasetBuildContractError("candidate identity drift")
    event_ids = tuple(event["event_group_id"] for event in candidate["events"])
    if event_ids != EXPECTED_EVENT_IDS:
        raise DatasetBuildContractError("eligible event roster drift")
    for group in candidate["input_bindings"].values():
        for binding in group:
            _verify_binding(root, binding)
    seen_rasters: set[str] = set()
    for event in candidate["events"]:
        if event["class_counts"] != {"background": 1, "burned": 1}:
            raise DatasetBuildContractError(
                f"binary candidate roster drift: {event['event_group_id']}"
            )
        for candidate_region in event["candidates"]:
            binding = candidate_region["raster"]
            _verify_binding(root, binding)
            if binding["sha256"] in seen_rasters:
                raise DatasetBuildContractError("duplicate candidate raster")
            seen_rasters.add(binding["sha256"])
            with rasterio.open(root / binding["path"]) as dataset:
                observed = {
                    "crs": str(dataset.crs),
                    "shape": [dataset.height, dataset.width],
                    "transform": list(dataset.transform)[:6],
                    "nodata": dataset.nodata,
                    "dtype": dataset.dtypes[0],
                }
            expected = candidate_region["raster_contract"]
            for key, value in observed.items():
                if value != expected[key]:
                    raise DatasetBuildContractError(
                        f"raster contract drift: {binding['path']} {key}"
                    )
    if len(seen_rasters) != 12:
        raise DatasetBuildContractError("candidate raster count drift")
    return candidate


def build_contract(
    root: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, Any]:
    candidate = _validate_candidate(root)
    prior_audit = _binding(root, PRIOR_AUDIT_PATH)
    if prior_audit["sha256"] != PRIOR_AUDIT_SHA256:
        raise DatasetBuildContractError("accepted readiness audit hash drift")
    prior_decision = _binding(root, PRIOR_DECISION_PATH)
    decision = _read_json(root / PRIOR_DECISION_PATH)
    if decision.get("decision") != "pass" or decision.get(
        "training_authorized"
    ) is not False:
        raise DatasetBuildContractError("accepted readiness decision drift")

    source_reports: dict[str, dict[str, Any]] = {}
    source_pairs: list[dict[str, Any]] = []
    for event_id in EXPECTED_EVENT_IDS:
        report_path = SOURCE_REPORTS[event_id]
        if report_path not in source_reports:
            source_reports[report_path] = _binding(root, report_path)
        report = _read_json(root / report_path)
        pre, post = _pair_products(report, event_id)
        source_pairs.append(
            {
                "event_group_id": event_id,
                "source_report": source_reports[report_path],
                "products": [
                    _product_contract(pre, "pre"),
                    _product_contract(post, "post"),
                ],
            }
        )

    return {
        "contract_version": CONTRACT_VERSION,
        "contract_id": CONTRACT_ID,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": TASK_ISSUE,
        "unit_id": UNIT_ID,
        "git_source_commit": git_source_commit,
        "software_version": __version__,
        "candidate": _binding(root, CANDIDATE_PATH),
        "accepted_readiness": {
            "audit": prior_audit,
            "decision": prior_decision,
            "decision_value": "pass",
            "training_authorized": False,
        },
        "output_versions": {
            "dataset_version": "burnlens-dataset-v0.1.0",
            "split_version": "burnlens-whole-event-split-v0.1.0",
            "baseline_version": None,
            "model_version": None,
        },
        "eligible_event_group_ids": list(EXPECTED_EVENT_IDS),
        "source_pairs": source_pairs,
        "input_contract": {
            "channel_order": list(FEATURE_CHANNELS),
            "channel_units": "Sentinel-2 L2A bottom-of-atmosphere reflectance",
            "reflectance_formula": (
                "(DN + band-specific BOA_ADD_OFFSET) / "
                "BOA_QUANTIFICATION_VALUE"
            ),
            "dtype": "float32",
            "native_grid": {
                "crs": "EPSG:32610",
                "resolution_m": 20,
                "resampling": "prohibited",
                "reprojection": "prohibited",
                "mosaicking": "prohibited",
            },
            "pair_validity": {
                "eligible_scl_classes": [4, 5],
                "review_scl_classes": [7],
                "excluded_scl_classes": [0, 1, 2, 3, 6, 8, 9, 10, 11],
                "review_pixels_in_loss_or_metrics": False,
                "all_six_reflectance_channels_must_be_numeric_valid": True,
                "nodata_and_saturated_dn_are_invalid": True,
            },
        },
        "label_contract": {
            "source_candidate_value_meaning": {
                "0": "outside this candidate; unreviewed and excluded",
                "1": "owner-approved candidate core",
                "2": "explicit unknown ring; excluded",
                "255": "source nodata if present; excluded",
            },
            "combined_state_values": {
                "0": "owner-approved background core",
                "1": "owner-approved burned core",
                "2": "union of explicit unknown rings",
                "255": "unreviewed, source-invalid, or nodata",
            },
            "loss_mask": (
                "combined state is 0 or 1 AND pair validity passes; no other "
                "pixel contributes to loss"
            ),
            "metric_mask": "byte-identical to loss_mask",
            "unknown_is_background": False,
            "outside_candidate_is_background": False,
            "class_assignment_source": "candidate class plus exact owner-yes intake",
        },
        "patch_contract": {
            "split_before_patch": True,
            "patch_size_pixels": [64, 64],
            "patch_size_meters": [1280, 1280],
            "one_patch_per_candidate": True,
            "candidate_count": 12,
            "placement": (
                "center on the integer floor of the value-1 core centroid, "
                "then shift the fixed window minimally inside the native "
                "event grid without padding"
            ),
            "core_clipping": "prohibited",
            "augmentation": "not part of dataset bytes",
            "cross_event_mixing": "prohibited",
            "patch_id": (
                "dataset version + split role + event group + candidate ID + "
                "native integer window"
            ),
        },
        "normalization_contract": {
            "stored_features": "unstandardized float32 reflectance",
            "statistics_owner": "locked training events only",
            "eligible_statistics_pixels": (
                "pair-valid pixels inside training patches; labels are not "
                "required for normalization statistics"
            ),
            "method": "per-channel global mean and population standard deviation",
            "standardization": "(value - train_mean) / max(train_std, 1e-6)",
            "validation_or_test_statistics": "prohibited",
            "clipping": "none",
        },
        "split_contract": {
            "roles": ["train", "validation", "test"],
            "whole_event_groups_per_role": 2,
            "group_before_patch": True,
            "group_keys": [
                "event_group_id",
                "scene_group",
                "geography_group",
                "time_group",
                "exact source regime",
            ],
            "valid_assignment_count": candidate["partition_feasibility"][
                "valid_assignments"
            ],
            "selection": (
                "U02 must predeclare and apply one deterministic ranking over "
                "all 54 valid assignments; this contract selects none"
            ),
            "test_sealed_until": (
                "baseline families, preprocessing, thresholds, patch roster, "
                "and selection rule are frozen"
            ),
        },
        "evaluation_contract": {
            "unit_of_independence": "whole event group",
            "primary_metrics": ["masked burned-class Dice", "masked burned-class IoU"],
            "required_slices": [
                "per event",
                "per class",
                "source regime",
                "never-tuned transfer status",
            ],
            "required_denominators": [
                "evaluated core pixels",
                "burned core pixels",
                "background core pixels",
                "events",
            ],
            "aggregation": (
                "report per-event metrics and macro event mean; pixel-pooled "
                "results are secondary and explicitly identified"
            ),
            "test_open_count": 1,
            "threshold_or_method_tuning_on_test": "prohibited",
            "uncertainty": (
                "report exact event results and small-n limitations; do not "
                "claim population generalization"
            ),
        },
        "reproducibility_and_custody": {
            "raw_provider_archives": (
                "remain ignored repository-local custody and must pass exact "
                "registration/hash verification before U03 reads them"
            ),
            "tracked_outputs": (
                "manifests, contracts, checksums, QA, and bounded derived "
                "samples only"
            ),
            "no_overwrite": True,
            "retained_failures": True,
        },
        "limitations": [
            "Only 287 owner-approved prototype core pixels exist across six events.",
            "The 531 unknown-ring pixels and every unreviewed pixel remain excluded.",
            "Owner approval is not independent ground truth or field validation.",
            "Balanced reviewed regions do not estimate natural class prevalence.",
            "A later dataset pass cannot itself authorize model training.",
        ],
        "boundaries": {
            "dataset_created": False,
            "split_created": False,
            "baseline_created": False,
            "model_created": False,
            "training_authorized": False,
            "independent_ground_truth_claimed": False,
            "generalization_claimed": False,
        },
        "next_dependency": "P2O5-T03-U02",
    }


def build_audit(
    root: Path, contract: dict[str, Any], contract_sha256: str
) -> dict[str, Any]:
    candidate = _read_json(root / CANDIDATE_PATH)
    gate_specs = (
        (
            "source-and-terms",
            "source_and_terms",
            "Every exact source and terms binding in the candidate was rehashed; the six optical source reports are separately byte-bound.",
        ),
        (
            "provenance-and-custody",
            "provenance_and_custody",
            "Five proposal, five owner-intake, 27 source/terms, 12 raster, prior readiness, and six-event optical lineages remain exact; raw archives stay ignored and require U03 reverification.",
        ),
        (
            "schema-and-quality",
            "schema_and_quality",
            "All candidate rasters retain their exact EPSG:32610 20 m contracts; every optical pair exposes aligned native B04/B8A/B12/SCL grids and complete reflectance metadata.",
        ),
        (
            "coverage-and-balance",
            "coverage_and_balance",
            "The roster remains six events with one approved core per class per event, 287 total core pixels, and an explicit non-prevalence limitation.",
        ),
        (
            "uncertainty-and-exclusions",
            "uncertainty_and_exclusions",
            "The contract excludes value-2 rings, source-invalid pixels, and all unreviewed zero-valued candidate-raster context from loss and metrics.",
        ),
        (
            "leakage-and-split-fitness",
            "leakage_and_split_fitness",
            "Split-before-patch, whole-event grouping, sealed-test rules, and all event/scene/geography/time/source-regime group keys are frozen; no split is selected.",
        ),
        (
            "reproducibility",
            "reproducibility",
            "The deterministic contract builder reopens every tracked binding and refuses roster, hash, raster, band, grid, or reflectance-metadata drift.",
        ),
        (
            "evaluation-design",
            "evaluation_design",
            "Masked core-only Dice/IoU, per-event and class slices, exact denominators, macro aggregation, and one-time test opening are frozen before split selection.",
        ),
        (
            "human-review",
            "human_review",
            "Every candidate core retains owner-yes custody plus non-owner promotion gates; owner approval remains necessary but not independent truth.",
        ),
        (
            "claims-and-privacy",
            "claims_and_privacy",
            "The contract contains no private response bytes or routes and keeps all dataset, split, baseline, model, training, validation, and generalization claims false.",
        ),
    )
    return {
        "audit_contract_version": "dataset-readiness-audit-v1",
        "template": False,
        "audit_id": AUDIT_ID,
        "candidate_id": CANDIDATE_ID,
        "candidate_manifest_sha256": CANDIDATE_SHA256,
        "required_gate_ids": [item[0] for item in gate_specs],
        "gates": [
            {
                "gate_id": gate_id,
                "category": category,
                "required": True,
                "status": "pass",
                "evidence_refs": [
                    f"records/phase-two/manifests/{CONTRACT_ID}.json",
                    f"contract-sha256:{contract_sha256}",
                    f"{CANDIDATE_PATH.as_posix()}",
                ],
                "finding": finding,
                "remediation": "",
            }
            for gate_id, category, finding in gate_specs
        ],
        "count_checks": [
            {
                "check_id": "exact-event-groups",
                "observed": candidate["inventory"]["event_groups"],
                "operator": "==",
                "threshold": 6,
                "on_failure": "block",
            },
            {
                "check_id": "exact-owner-approved-regions",
                "observed": candidate["inventory"]["owner_approved_regions"],
                "operator": "==",
                "threshold": 12,
                "on_failure": "block",
            },
            {
                "check_id": "accepted-core-pixels",
                "observed": candidate["inventory"]["accepted_core_pixels"],
                "operator": "==",
                "threshold": 287,
                "on_failure": "block",
            },
            {
                "check_id": "explicit-unknown-ring-pixels",
                "observed": candidate["inventory"][
                    "excluded_unknown_ring_pixels"
                ],
                "operator": "==",
                "threshold": 531,
                "on_failure": "block",
            },
            {
                "check_id": "common-input-channels",
                "observed": len(contract["input_contract"]["channel_order"]),
                "operator": "==",
                "threshold": 6,
                "on_failure": "block",
            },
            {
                "check_id": "valid-whole-event-assignments",
                "observed": contract["split_contract"]["valid_assignment_count"],
                "operator": "==",
                "threshold": 54,
                "on_failure": "block",
            },
        ],
        "training_authorization": {
            "separate_approval_required": True,
            "authorized_by_this_audit": False,
        },
    }


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
            raise DatasetBuildContractError(
                f"exact output readback failed: {path}"
            )
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
    contract = build_contract(
        root, generated_at_utc, run_id, git_source_commit
    )
    contract_bytes = _json_bytes(contract)
    audit = build_audit(root, contract, sha256(contract_bytes).hexdigest())
    audit_bytes = _json_bytes(audit)
    outputs = {
        "contract": (
            root
            / "records/phase-two/manifests"
            / f"{CONTRACT_ID}.json"
        ),
        "audit": (
            root
            / "records/phase-two/readiness"
            / f"{AUDIT_ID}.json"
        ),
    }
    _write_new(outputs["contract"], contract_bytes)
    _write_new(outputs["audit"], audit_bytes)
    return outputs
