"""Fail-closed loader for the Phase Four RBR-primary integration contract."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Mapping


CONTRACT_PATH = Path(
    "records/phase-four/contracts/"
    "PHASE-FOUR-INTEGRATION-CONTRACT-2026-001.json"
)
CONTRACT_VERSION = "burnlens-phase-four-integration-contract-v0.1.0"
CONTRACT_ID = "PHASE-FOUR-INTEGRATION-CONTRACT-2026-001"
BASE_COMMIT = "e8745b70c4cfe0d070e08e399efbab09e74cd06f"
ROUTE = "baseline-primary-with-rejected-model-diagnostic"
ACCEPTED_METHOD = "burnlens-baseline-v0.1.0"
REJECTED_MODEL = "burnlens-unet-binary-v0.1.0"
RBR_THRESHOLD = 0.041043221950531006
MODEL_THRESHOLD = 0.5
CHANNEL_ORDER = [
    "pre_B04",
    "pre_B8A",
    "pre_B12",
    "post_B04",
    "post_B8A",
    "post_B12",
]
RUN_STATES = {
    "accepted-baseline",
    "degraded",
    "no-detection",
    "fallback-baseline",
    "failed",
    "withheld",
}
WARD_CANDIDATES = {
    "WCP-001": {
        "class": "burned",
        "patch_id": "test--event-ward-creek-2019--WCP-001--r168c236h64w64",
        "transform": [20.0, 0.0, 667220.0, 0.0, -20.0, 4979800.0],
    },
    "WCP-002": {
        "class": "background",
        "patch_id": "test--event-ward-creek-2019--WCP-002--r68c401h64w64",
        "transform": [20.0, 0.0, 670520.0, 0.0, -20.0, 4981800.0],
    },
}


class PhaseFourContractError(RuntimeError):
    """The tracked Phase Four contract or a frozen input has drifted."""


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(8 * 1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise PhaseFourContractError(message)


def validate_contract(
    contract: Mapping[str, Any],
    *,
    repository_root: Path,
) -> dict[str, Any]:
    """Validate control semantics and byte identities without opening arrays."""

    root = repository_root.resolve()
    _require(
        contract.get("contract_version") == CONTRACT_VERSION,
        "contract version drift",
    )
    _require(contract.get("contract_id") == CONTRACT_ID, "contract id drift")
    _require(
        contract.get("exact_branch_base") == BASE_COMMIT,
        "branch base drift",
    )
    _require(contract.get("route") == ROUTE, "Phase Four route drift")

    methods = contract.get("analytical_methods", {})
    _require(
        methods.get("accepted", {}).get("version") == ACCEPTED_METHOD,
        "accepted analytical method drift",
    )
    _require(
        methods.get("accepted", {}).get("threshold") == RBR_THRESHOLD,
        "RBR threshold drift",
    )
    _require(
        methods.get("rejected_diagnostic", {}).get("version")
        == REJECTED_MODEL,
        "rejected model drift",
    )
    _require(
        methods.get("rejected_diagnostic", {}).get("threshold")
        == MODEL_THRESHOLD,
        "rejected-model threshold drift",
    )
    _require(
        methods.get("rejected_diagnostic", {}).get("accepted") is False,
        "rejected model cannot be accepted",
    )
    _require(
        methods.get("rejected_diagnostic", {}).get("outperformed_rbr") is False,
        "model-superiority claim is prohibited",
    )

    bindings = contract.get("frozen_bindings", [])
    _require(isinstance(bindings, list) and bindings, "frozen bindings required")
    for binding in bindings:
        path = root / binding["path"]
        _require(path.is_file(), f"frozen input absent: {binding['path']}")
        _require(
            path.stat().st_size == binding["bytes"],
            f"frozen input size drift: {binding['path']}",
        )
        _require(
            _sha256_file(path) == binding["sha256"],
            f"frozen input hash drift: {binding['path']}",
        )

    inventory_binding = contract.get("package_inventory_binding", {})
    package_record_path = root / (
        "records/phase-three/packages/"
        "BOUNDED-UNET-REJECTED-PACKAGE-RECORD-2026-001.json"
    )
    try:
        package_record = json.loads(
            package_record_path.read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError) as exc:
        raise PhaseFourContractError("invalid rejected-model package record") from exc
    package_root = root / inventory_binding.get("path", "")
    outputs = package_record.get("tracked_package_inventory", {}).get(
        "outputs", {}
    )
    _require(
        len(outputs) == inventory_binding.get("file_count"),
        "package inventory file-count drift",
    )
    rows: list[str] = []
    total_bytes = 0
    for name in sorted(outputs, key=str.casefold):
        metadata = outputs[name]
        path = package_root / name
        _require(path.is_file(), f"package member absent: {name}")
        _require(
            path.stat().st_size == metadata["bytes"],
            f"package member size drift: {name}",
        )
        _require(
            _sha256_file(path) == metadata["sha256"],
            f"package member hash drift: {name}",
        )
        total_bytes += metadata["bytes"]
        rows.append(
            f"{inventory_binding['path']}/{name}\t"
            f"{metadata['bytes']}\t{metadata['sha256']}\n"
        )
    inventory = "".join(rows).encode("utf-8")
    _require(
        total_bytes == inventory_binding.get("bytes"),
        "package inventory byte-total drift",
    )
    _require(
        len(inventory) == inventory_binding.get("inventory_bytes"),
        "package inventory serialization drift",
    )
    _require(
        sha256(inventory).hexdigest()
        == inventory_binding.get("inventory_sha256"),
        "package inventory hash drift",
    )

    roster = contract.get("integration_roster", [])
    _require(len(roster) == 2, "exact two-patch Ward Creek roster required")
    _require(
        {item.get("candidate_id") for item in roster}
        == set(WARD_CANDIDATES),
        "Ward Creek candidate roster drift",
    )
    for item in roster:
        expected = WARD_CANDIDATES[item["candidate_id"]]
        _require(item.get("class") == expected["class"], "candidate class drift")
        _require(item.get("patch_id") == expected["patch_id"], "patch id drift")
        _require(item.get("crs") == "EPSG:32610", "patch CRS drift")
        _require(item.get("transform") == expected["transform"], "transform drift")
        _require(item.get("shape") == [64, 64], "patch shape drift")
        _require(item.get("channel_order") == CHANNEL_ORDER, "channel order drift")
        _require(
            item.get("input_valid_pixels") == 4096,
            "Ward Creek integration patch must be fully input-valid",
        )
        files = item.get("files", [])
        _require(len(files) == 4, "four frozen arrays required per patch")
        for file_binding in files:
            path = root / file_binding["path"]
            _require(path.is_file(), f"patch input absent: {file_binding['path']}")
            _require(
                path.stat().st_size == file_binding["bytes"],
                f"patch input size drift: {file_binding['path']}",
            )
            _require(
                _sha256_file(path) == file_binding["sha256"],
                f"patch input hash drift: {file_binding['path']}",
            )

    taxonomy = contract.get("run_state_taxonomy", {})
    _require(set(taxonomy) == RUN_STATES, "run-state taxonomy drift")
    _require(
        taxonomy["accepted-baseline"]["analytical_method"] == ACCEPTED_METHOD,
        "accepted-baseline state must identify RBR",
    )
    _require(
        taxonomy["no-detection"]["does_not_mean_safe"] is True,
        "no-detection safety boundary missing",
    )

    output_contract = contract.get("output_contract", {})
    required_outputs = {
        "rbr_score_raster",
        "rbr_binary_raster",
        "exclusion_raster",
        "unet_probability_diagnostic_raster",
        "unet_binary_diagnostic_raster",
        "rbr_polygon_vector",
        "summary",
        "run_manifest",
        "checksums",
        "interface",
    }
    _require(
        set(output_contract) == required_outputs,
        "Phase Four output roster drift",
    )

    boundaries = contract.get("boundaries", {})
    for key in (
        "phase_3b_created",
        "second_experiment_planned",
        "second_experiment_implemented",
        "retraining",
        "retuning",
        "dataset_changed",
        "split_changed",
        "label_changed",
        "aoi_changed",
        "model_superiority_claim",
        "operational_claim",
    ):
        _require(boundaries.get(key) is False, f"prohibited boundary enabled: {key}")

    return dict(contract)


def load_contract(repository_root: Path) -> dict[str, Any]:
    """Load and validate the exact tracked Phase Four contract."""

    path = repository_root.resolve() / CONTRACT_PATH
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PhaseFourContractError(f"invalid contract JSON: {path}") from exc
    _require(isinstance(value, dict), "contract must be a JSON object")
    return validate_contract(value, repository_root=repository_root)
