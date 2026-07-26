"""Deterministic Phase Four RBR-primary and rejected-U-Net analysis."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import io
import json
import math
import os
from pathlib import Path
import re
import subprocess
from typing import Any

import numpy as np
import torch

from burnlens.baseline_evaluation import score as baseline_score
from burnlens.bounded_unet import (
    BoundedUNet,
    configure_deterministic_execution,
)
from burnlens.bounded_unet_training import load_model_weights
from burnlens.phase_four_contract import (
    CONTRACT_PATH,
    MODEL_THRESHOLD,
    RBR_THRESHOLD,
    load_contract,
)


ANALYSIS_VERSION = "burnlens-phase-four-analysis-v0.1.0"
SOFTWARE_VERSION = "0.53.0"
RUN_ROOT = Path("runs/phase-four")
DATASET_ROOT = Path("samples/datasets/burnlens-dataset-v0.1.0")
NORMALIZATION_PATH = Path(
    "records/phase-two/manifests/TRAIN-NORMALIZATION-2026-001.json"
)
MODEL_WEIGHTS_PATH = Path(
    "samples/model-packages/burnlens-unet-binary-v0.1.0/"
    "burnlens-unet-binary-v0.1.0.pt"
)
RUN_ID_PATTERN = re.compile(
    r"^BL-[0-9]{4}-[0-9]{2}-[0-9]{2}-p4o1-t01-u02-analysis-r[0-9]{3}$"
)
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")
FLOAT_NODATA = np.float32(-9999.0)
BYTE_NODATA = np.uint8(255)


class PhaseFourRunnerError(RuntimeError):
    """A frozen analytical input, execution, or output gate failed."""


@dataclass(frozen=True)
class AnalysisBuild:
    """Deterministic bytes for one Phase Four analytical attempt."""

    manifest: dict[str, Any]
    outputs: dict[str, bytes]


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(8 * 1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(
        "utf-8"
    )


def _npy_bytes(value: np.ndarray) -> bytes:
    buffer = io.BytesIO()
    np.save(buffer, value, allow_pickle=False)
    return buffer.getvalue()


def _receipt(path: str, payload: bytes) -> dict[str, Any]:
    return {
        "path": path,
        "bytes": len(payload),
        "sha256": sha256(payload).hexdigest(),
    }


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PhaseFourRunnerError(f"invalid JSON: {path}") from exc
    if not isinstance(value, dict):
        raise PhaseFourRunnerError(f"JSON object required: {path}")
    return value


def _verified_array(path: Path, binding: dict[str, Any]) -> np.ndarray:
    if not path.is_file():
        raise PhaseFourRunnerError(f"bound array is absent: {binding['path']}")
    if path.stat().st_size != binding["bytes"]:
        raise PhaseFourRunnerError(f"bound array size drift: {binding['path']}")
    if _sha256_file(path) != binding["sha256"]:
        raise PhaseFourRunnerError(f"bound array hash drift: {binding['path']}")
    value = np.load(path, allow_pickle=False)
    if not isinstance(value, np.ndarray):
        raise PhaseFourRunnerError(f"invalid bound array: {binding['path']}")
    return value


def _normalization(root: Path) -> tuple[np.ndarray, np.ndarray]:
    value = _read_json(root / NORMALIZATION_PATH)
    channels = value.get("channels")
    if not isinstance(channels, list) or len(channels) != 6:
        raise PhaseFourRunnerError("normalization channel schema drift")
    means = np.array([item["mean"] for item in channels], dtype=np.float32)
    stds = np.array(
        [max(float(item["population_std"]), 1e-6) for item in channels],
        dtype=np.float32,
    )
    if (
        means.shape != (6,)
        or stds.shape != (6,)
        or not np.isfinite(means).all()
        or not np.isfinite(stds).all()
        or np.any(stds <= 0)
    ):
        raise PhaseFourRunnerError("normalization statistics are invalid")
    return means, stds


def _patch_arrays(
    root: Path,
    patch: dict[str, Any],
) -> tuple[np.ndarray, np.ndarray]:
    bindings = {Path(item["path"]).name: item for item in patch["files"]}
    if set(bindings) != {
        "features.npy",
        "input_valid.npy",
        "loss_mask.npy",
        "state.npy",
    }:
        raise PhaseFourRunnerError("patch file roster drift")
    features = _verified_array(
        root / bindings["features.npy"]["path"],
        bindings["features.npy"],
    )
    input_valid = _verified_array(
        root / bindings["input_valid.npy"]["path"],
        bindings["input_valid.npy"],
    )
    if features.shape != (6, 64, 64) or features.dtype != np.float32:
        raise PhaseFourRunnerError("feature array schema drift")
    if input_valid.shape != (64, 64):
        raise PhaseFourRunnerError("input-valid array shape drift")
    if input_valid.dtype not in (np.dtype("uint8"), np.dtype("bool")):
        raise PhaseFourRunnerError("input-valid array dtype drift")
    input_valid = input_valid.astype(bool, copy=False)
    if not np.isfinite(features[:, input_valid]).all():
        raise PhaseFourRunnerError("valid feature pixel is nonfinite")
    return features, input_valid


def _patch_outputs(
    *,
    features: np.ndarray,
    input_valid: np.ndarray,
    model: BoundedUNet,
    means: np.ndarray,
    stds: np.ndarray,
) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    rbr = baseline_score(features, "rbr-threshold").astype(
        np.float32, copy=False
    )
    if rbr.shape != (64, 64) or not np.isfinite(rbr[input_valid]).all():
        raise PhaseFourRunnerError("RBR score schema or finite gate failed")
    rbr_output = np.full((64, 64), FLOAT_NODATA, dtype=np.float32)
    rbr_output[input_valid] = rbr[input_valid]
    rbr_binary = np.full((64, 64), BYTE_NODATA, dtype=np.uint8)
    rbr_binary[input_valid] = (
        rbr[input_valid] >= RBR_THRESHOLD
    ).astype(np.uint8)

    normalized = (features - means[:, None, None]) / stds[:, None, None]
    normalized[:, ~input_valid] = 0.0
    if not np.isfinite(normalized).all():
        raise PhaseFourRunnerError("normalized model input is nonfinite")
    with torch.no_grad():
        logits = model(torch.from_numpy(normalized[None, ...].copy()))
        probabilities = torch.sigmoid(logits)[0, 0].cpu().numpy().astype(
            np.float32, copy=False
        )
    if (
        probabilities.shape != (64, 64)
        or not np.isfinite(probabilities[input_valid]).all()
        or np.any(probabilities[input_valid] < 0)
        or np.any(probabilities[input_valid] > 1)
    ):
        raise PhaseFourRunnerError("U-Net probability schema or domain failed")
    probability_output = np.full(
        (64, 64), FLOAT_NODATA, dtype=np.float32
    )
    probability_output[input_valid] = probabilities[input_valid]
    model_binary = np.full((64, 64), BYTE_NODATA, dtype=np.uint8)
    model_binary[input_valid] = (
        probabilities[input_valid] >= MODEL_THRESHOLD
    ).astype(np.uint8)
    exclusion = (~input_valid).astype(np.uint8)

    valid_rbr = rbr_binary[input_valid]
    valid_model = model_binary[input_valid]
    facts = {
        "valid_pixels": int(input_valid.sum()),
        "excluded_pixels": int((~input_valid).sum()),
        "rbr_positive_pixels": int(np.count_nonzero(valid_rbr == 1)),
        "unet_diagnostic_positive_pixels": int(
            np.count_nonzero(valid_model == 1)
        ),
        "agreement_pixels": int(np.count_nonzero(valid_rbr == valid_model)),
        "rbr_only_positive_pixels": int(
            np.count_nonzero((valid_rbr == 1) & (valid_model == 0))
        ),
        "unet_only_positive_pixels": int(
            np.count_nonzero((valid_rbr == 0) & (valid_model == 1))
        ),
        "rbr_min": float(np.min(rbr[input_valid])),
        "rbr_max": float(np.max(rbr[input_valid])),
        "unet_probability_min": float(
            np.min(probabilities[input_valid])
        ),
        "unet_probability_max": float(
            np.max(probabilities[input_valid])
        ),
    }
    for key, value in facts.items():
        if isinstance(value, float) and not math.isfinite(value):
            raise PhaseFourRunnerError(f"nonfinite analytical fact: {key}")
    return {
        "rbr-score.npy": rbr_output,
        "rbr-binary.npy": rbr_binary,
        "exclusion.npy": exclusion,
        "unet-probability-diagnostic.npy": probability_output,
        "unet-binary-diagnostic.npy": model_binary,
    }, facts


def build_analysis(
    *,
    repository_root: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> AnalysisBuild:
    """Build deterministic U02 bytes from the exact contract-bound inputs."""

    root = repository_root.resolve()
    if not RUN_ID_PATTERN.fullmatch(run_id):
        raise PhaseFourRunnerError("run ID does not match the U02 contract")
    if not COMMIT_PATTERN.fullmatch(git_source_commit):
        raise PhaseFourRunnerError("git source commit is invalid")
    contract = load_contract(root)
    settings = configure_deterministic_execution()
    means, stds = _normalization(root)
    model = BoundedUNet()
    load_model_weights(root / MODEL_WEIGHTS_PATH, model)
    model.eval()

    output_bytes: dict[str, bytes] = {}
    patch_records: list[dict[str, Any]] = []
    for patch in contract["integration_roster"]:
        features, input_valid = _patch_arrays(root, patch)
        arrays, facts = _patch_outputs(
            features=features,
            input_valid=input_valid,
            model=model,
            means=means,
            stds=stds,
        )
        patch_output_receipts: list[dict[str, Any]] = []
        for name, value in arrays.items():
            relative = f"patches/{patch['candidate_id']}/{name}"
            payload = _npy_bytes(value)
            output_bytes[relative] = payload
            patch_output_receipts.append(_receipt(relative, payload))
        patch_records.append(
            {
                "patch_id": patch["patch_id"],
                "event_group_id": patch["event_group_id"],
                "candidate_id": patch["candidate_id"],
                "prototype_class": patch["class"],
                "crs": patch["crs"],
                "transform": patch["transform"],
                "shape": patch["shape"],
                "input_bindings": patch["files"],
                "outputs": patch_output_receipts,
                "facts": facts,
            }
        )

    total_rbr = sum(
        item["facts"]["rbr_positive_pixels"] for item in patch_records
    )
    status = "accepted-baseline" if total_rbr > 0 else "no-detection"
    status_payload = {
        "status_version": "burnlens-phase-four-run-status-v0.1.0",
        "run_id": run_id,
        "state": status,
        "accepted_method": "burnlens-baseline-v0.1.0",
        "rejected_model": "burnlens-unet-binary-v0.1.0",
        "model_accepted": False,
        "model_outperformed_rbr": False,
        "complete": True,
        "publishable": False,
        "next_dependency": "P4O1-T01-U03 geospatial products",
    }
    output_bytes["STATUS.json"] = _json_bytes(status_payload)
    output_receipts = [
        _receipt(path, payload)
        for path, payload in sorted(output_bytes.items(), key=lambda item: item[0])
    ]
    manifest = {
        "analysis_version": ANALYSIS_VERSION,
        "analysis_id": "PHASE-FOUR-ANALYSIS-2026-001",
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "issue": 570,
        "unit_id": "P4O1-T01-U02",
        "git_source_commit": git_source_commit,
        "software_version_at_execution": SOFTWARE_VERSION,
        "state": status,
        "route": "baseline-primary-with-rejected-model-diagnostic",
        "contract": {
            "path": CONTRACT_PATH.as_posix(),
            "bytes": (root / CONTRACT_PATH).stat().st_size,
            "sha256": _sha256_file(root / CONTRACT_PATH),
        },
        "versions": contract["versions"],
        "methods": contract["analytical_methods"],
        "execution": {
            **settings,
            "device": "cpu",
            "dtype": "float32",
            "model_training": False,
            "threshold_tuning": False,
            "model_selection": False,
            "metric_selection": False,
            "source_test_role_arrays_read_for_fixed_integration": True,
            "phase_three_model_selection_test_open_count": 1,
            "phase_four_integration_read_count": 1,
        },
        "patches": patch_records,
        "output_inventory": output_receipts,
        "warnings": [
            "Prototype labels are owner-approved sparse evidence, not independent ground truth.",
            "RBR is the accepted analytical method only for this bounded demonstration.",
            "The U-Net probability is a rejected-model descriptive score, not calibrated confidence.",
            "A no-detection state would not mean safe, no fire, or no risk.",
            "No geospatial raster/vector product, context overlay, summary, or public interface is accepted at U02."
        ],
        "boundaries": {
            "model_accepted": False,
            "model_outperformed_rbr": False,
            "model_retrained": False,
            "threshold_changed": False,
            "phase_3b_created": False,
            "second_experiment_planned": False,
            "second_experiment_implemented": False,
            "dataset_changed": False,
            "split_changed": False,
            "label_changed": False,
            "aoi_changed": False,
            "context_source_used": False,
            "geospatial_product_accepted": False,
            "deployment": False,
            "official_operational_or_emergency_claim": False,
        },
        "disposition": "pass-analytical-arrays-pending-geospatial-products",
        "next_dependency": "P4O1-T01-U03 geospatial products",
    }
    output_bytes["ANALYSIS-MANIFEST.json"] = _json_bytes(manifest)
    return AnalysisBuild(manifest=manifest, outputs=output_bytes)


def _require_exact_clean_head(root: Path, git_source_commit: str) -> None:
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if head != git_source_commit:
        raise PhaseFourRunnerError("git source commit differs from HEAD")
    status = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    if status:
        raise PhaseFourRunnerError("working tree must be clean before U02")


def _write_new(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    created = False
    try:
        with path.open("xb") as stream:
            created = True
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        if path.read_bytes() != payload:
            raise PhaseFourRunnerError(f"output readback differs: {path}")
    except Exception:
        if created and path.exists():
            path.unlink()
        raise


def run_analysis(
    *,
    repository_root: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> AnalysisBuild:
    """Write one no-overwrite immutable U02 analytical attempt."""

    root = repository_root.resolve()
    _require_exact_clean_head(root, git_source_commit)
    run_directory = root / RUN_ROOT / run_id
    if run_directory.exists() or run_directory.is_symlink():
        raise PhaseFourRunnerError(f"run already exists: {run_id}")
    run_directory.mkdir(parents=True)
    started = {
        "attempt_version": "burnlens-phase-four-attempt-v0.1.0",
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "git_source_commit": git_source_commit,
        "status": "STARTED",
    }
    _write_new(run_directory / "RUN-STARTED.json", _json_bytes(started))
    try:
        build = build_analysis(
            repository_root=root,
            generated_at_utc=generated_at_utc,
            run_id=run_id,
            git_source_commit=git_source_commit,
        )
        for relative, payload in sorted(build.outputs.items()):
            _write_new(run_directory / relative, payload)
        complete = {
            **started,
            "status": "COMPLETE",
            "state": build.manifest["state"],
            "output_count": len(build.outputs),
            "manifest_sha256": sha256(
                build.outputs["ANALYSIS-MANIFEST.json"]
            ).hexdigest(),
        }
        _write_new(run_directory / "RUN-COMPLETE.json", _json_bytes(complete))
        return build
    except Exception as exc:
        failure = {
            **started,
            "status": "FAILED",
            "error_type": type(exc).__name__,
            "error": str(exc),
        }
        try:
            _write_new(run_directory / "FAILURE.json", _json_bytes(failure))
        except Exception:
            pass
        raise
