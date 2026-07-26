"""Replay and package the valid rejected BurnLens U-Net without reopening test data."""

from __future__ import annotations

from hashlib import sha256
from html import escape
import io
import json
import os
from pathlib import Path
import shutil
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from burnlens.bounded_unet import load_model_examples
from burnlens.bounded_unet_evaluation import _require_exact_git_source
from burnlens.bounded_unet_training import _run_training_loop


PACKAGE_VERSION = "burnlens-unet-rejected-package-v0.1.0"
PACKAGE_ID = "BURNLENS-UNET-REJECTED-PACKAGE-2026-001"
MODEL_VERSION = "burnlens-unet-binary-v0.1.0"
DATASET_VERSION = "burnlens-dataset-v0.1.0"
SPLIT_VERSION = "burnlens-whole-event-split-v0.1.0"
NORMALIZATION_VERSION = "burnlens-train-normalization-v0.1.0"
LABEL_SCHEMA_VERSION = "burn-scar-binary-region-label-schema-v0.3.0"
BASELINE_VERSION = "burnlens-baseline-v0.1.0"
MODEL_DIRECTORY = Path("samples/models") / MODEL_VERSION
WEIGHTS_PATH = MODEL_DIRECTORY / f"{MODEL_VERSION}.pt"
WEIGHTS_SHA256 = "703d92577e2b82a4cfdec0c5e43b8d7a064253483de4ccea909209f54b802334"
TRAINING_HISTORY_PATH = MODEL_DIRECTORY / "TRAINING-HISTORY-2026-001.json"
TRAINING_HISTORY_SHA256 = (
    "94195a92fac24ca087d977f3957106aa3b92dc3b18aec06746bd6a72ea70a2a8"
)
TRAINING_REPORT_PATH = MODEL_DIRECTORY / "BOUNDED-UNET-TRAINING-2026-001.json"
TRAINING_REPORT_SHA256 = (
    "53a454bd082314c33e8249fdc98c62f89e7c0bb6ecc35d800dfa4f15df1fdf57"
)
EVALUATION_DIRECTORY = Path(
    "samples/evaluation/phase-three/bounded-unet-test-v0.1.0"
)
EVALUATION_PATH = EVALUATION_DIRECTORY / "BOUNDED-UNET-TEST-EVALUATION-2026-001.json"
EVALUATION_SHA256 = (
    "8d3e0652b71f0052ea54ac67caa280eaa15aad3e4055568948e58306b4c72e35"
)
OPENING_RECEIPT_PATH = (
    EVALUATION_DIRECTORY / "BOUNDED-UNET-TEST-OPENING-RECEIPT-2026-001.json"
)
OPENING_RECEIPT_SHA256 = (
    "2613172f06478801aadf51ea63cd4ee0b00e87ba47f81a9f7d53f3c4eb605ab1"
)
U05_RECORD_PATH = Path(
    "records/phase-three/evaluations/"
    "BOUNDED-UNET-TEST-EVALUATION-RECORD-2026-001.json"
)
U05_RECORD_SHA256 = (
    "1d02b26535ef492eedc8ef5211ffafdbcb3a605f76aee2ef95eb1949bff1e2cc"
)
BASELINE_PATH = Path(
    "samples/baselines/burnlens-baseline-v0.1.0/"
    "BASELINE-EVALUATION-2026-001.json"
)
BASELINE_SHA256 = (
    "a8ba82f999a87a8114c7fc417126b96c1f031e7eb9e24311df20fe32d7edb221"
)
PACKAGE_DIRECTORY = Path("samples/model-packages") / MODEL_VERSION
RUN_DIRECTORY_ROOT = Path("runs/phase-three")


class BoundedUNetPackageError(RuntimeError):
    """An exact replay, immutable evaluation, package, or decision failure."""


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(8 * 1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BoundedUNetPackageError(f"invalid JSON: {path}") from exc
    if not isinstance(value, dict):
        raise BoundedUNetPackageError(f"JSON object required: {path}")
    return value


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def _identity(root: Path, relative: Path, expected_sha256: str) -> dict[str, Any]:
    path = root / relative
    if not path.is_file():
        raise BoundedUNetPackageError(f"bound input absent: {relative}")
    digest = _sha256_file(path)
    if digest != expected_sha256:
        raise BoundedUNetPackageError(f"bound input drift: {relative}")
    return {
        "path": relative.as_posix(),
        "bytes": path.stat().st_size,
        "sha256": digest,
    }


def _write_new(path: Path, payload: bytes) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() or path.is_symlink():
        raise BoundedUNetPackageError(f"refusing to overwrite: {path}")
    path.write_bytes(payload)
    if path.read_bytes() != payload:
        raise BoundedUNetPackageError(f"written bytes differ: {path}")
    return {
        "path": path.as_posix(),
        "bytes": len(payload),
        "sha256": sha256(payload).hexdigest(),
    }


def _copy_new(source: Path, destination: Path) -> dict[str, Any]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() or destination.is_symlink():
        raise BoundedUNetPackageError(f"refusing to overwrite: {destination}")
    shutil.copyfile(source, destination)
    if (
        destination.stat().st_size != source.stat().st_size
        or _sha256_file(destination) != _sha256_file(source)
    ):
        raise BoundedUNetPackageError("package copy drift")
    return {
        "path": destination.as_posix(),
        "bytes": destination.stat().st_size,
        "sha256": _sha256_file(destination),
    }


def _promote_tree(source: Path, destination: Path) -> None:
    if destination.exists() or destination.is_symlink():
        raise BoundedUNetPackageError("model package already exists")
    destination.parent.mkdir(parents=True, exist_ok=True)
    staging = destination.with_name(f".{destination.name}.staging")
    if staging.exists() or staging.is_symlink():
        raise BoundedUNetPackageError("model package staging path exists")
    shutil.copytree(source, staging)
    for original in sorted(path for path in source.rglob("*") if path.is_file()):
        relative = original.relative_to(source)
        copied = staging / relative
        if (
            copied.stat().st_size != original.stat().st_size
            or _sha256_file(copied) != _sha256_file(original)
        ):
            raise BoundedUNetPackageError(f"staging copy drift: {relative}")
    os.replace(staging, destination)


def verify_immutable_evaluation(root: Path) -> dict[str, Any]:
    """Verify U05 outputs only; never read a source dataset test array."""

    evaluation_identity = _identity(root, EVALUATION_PATH, EVALUATION_SHA256)
    receipt_identity = _identity(
        root, OPENING_RECEIPT_PATH, OPENING_RECEIPT_SHA256
    )
    u05_record_identity = _identity(root, U05_RECORD_PATH, U05_RECORD_SHA256)
    baseline_identity = _identity(root, BASELINE_PATH, BASELINE_SHA256)
    evaluation = _read_json(root / EVALUATION_PATH)
    receipt = _read_json(root / OPENING_RECEIPT_PATH)
    if evaluation.get("boundaries", {}).get("test_open_count") != 1:
        raise BoundedUNetPackageError("U05 test-open count drift")
    if evaluation.get("boundaries", {}).get("test_tuning") is not False:
        raise BoundedUNetPackageError("U05 test-tuning boundary drift")
    if receipt.get("retry_authorized") is not False:
        raise BoundedUNetPackageError("U05 retry boundary drift")
    for item in receipt.get("outputs", {}).values():
        path = root / item["path"]
        if (
            not path.is_file()
            or path.stat().st_size != item["bytes"]
            or _sha256_file(path) != item["sha256"]
        ):
            raise BoundedUNetPackageError(f"U05 output drift: {item['path']}")

    arrays_checked = 0
    for records in evaluation.get("prediction_outputs", {}).values():
        probability_path = root / records["probability"]["path"]
        prediction_path = root / records["prediction"]["path"]
        normalized_probability = probability_path.as_posix().lower()
        normalized_prediction = prediction_path.as_posix().lower()
        if "/samples/datasets/" in normalized_probability or "/samples/datasets/" in normalized_prediction:
            raise BoundedUNetPackageError("replay attempted a source test array")
        probability = np.load(probability_path, allow_pickle=False)
        prediction = np.load(prediction_path, allow_pickle=False)
        if (
            probability.shape != (64, 64)
            or probability.dtype != np.float32
            or prediction.shape != (64, 64)
            or prediction.dtype != np.uint8
            or not np.isfinite(probability).all()
            or not np.array_equal(
                prediction, (probability >= 0.5).astype(np.uint8)
            )
        ):
            raise BoundedUNetPackageError("immutable prediction output drift")
        arrays_checked += 2

    metrics = evaluation["test_metrics"]
    events = metrics["events"]
    classes = [row for event in events for row in event["classes"]]
    if sum(event["core_pixels"] for event in events) != metrics["core_pixels"]:
        raise BoundedUNetPackageError("event core denominator drift")
    if (
        sum(row["dice"] for row in classes) / len(classes)
        != metrics["event_class_macro_dice"]
        or sum(row["iou"] for row in classes) / len(classes)
        != metrics["event_class_macro_iou"]
        or min(event["class_macro_dice"] for event in events)
        != metrics["worst_event_macro_dice"]
    ):
        raise BoundedUNetPackageError("U05 macro metric drift")
    comparison = evaluation["baseline_comparison"]
    if (
        comparison.get("status") != "BELOW_RBR_REJECT_AS_ANALYTICAL_WINNER"
        or comparison.get("analytical_winner") is not False
    ):
        raise BoundedUNetPackageError("U05 baseline decision drift")
    return {
        "evaluation": evaluation_identity,
        "opening_receipt": receipt_identity,
        "u05_record": u05_record_identity,
        "baseline": baseline_identity,
        "prediction_arrays_checked": arrays_checked,
        "test_source_arrays_reopened": False,
        "test_open_count": 1,
        "retry_authorized": False,
        "metrics_recomputed_from_immutable_event_class_rows": True,
        "binary_predictions_recomputed_from_immutable_probabilities": True,
        "baseline_decision": comparison["status"],
        "test_metrics": {
            "core_pixels": metrics["core_pixels"],
            "masked_bce": metrics["masked_bce"],
            "event_class_macro_dice": metrics["event_class_macro_dice"],
            "event_class_macro_iou": metrics["event_class_macro_iou"],
            "worst_event_macro_dice": metrics["worst_event_macro_dice"],
            "true_burned_pixels": metrics["true_burned_pixels"],
            "predicted_burned_pixels": metrics["predicted_burned_pixels"],
        },
    }


def run_training_replay(root: Path, replay_directory: Path) -> dict[str, Any]:
    """Replay train/validation only and require exact history and weights."""

    history_identity = _identity(
        root, TRAINING_HISTORY_PATH, TRAINING_HISTORY_SHA256
    )
    report_identity = _identity(
        root, TRAINING_REPORT_PATH, TRAINING_REPORT_SHA256
    )
    weights_identity = _identity(root, WEIGHTS_PATH, WEIGHTS_SHA256)
    tracked_history = _read_json(root / TRAINING_HISTORY_PATH)
    tracked_report = _read_json(root / TRAINING_REPORT_PATH)
    training = load_model_examples(root, {"train"})
    validation = load_model_examples(root, {"validation"})
    result = _run_training_loop(
        replay_directory,
        training,
        validation,
        maximum_epochs=200,
    )
    replay_weights = Path(result["working_receipts"]["weights"]["path"])
    if (
        _sha256_file(replay_weights) != WEIGHTS_SHA256
        or replay_weights.read_bytes() != (root / WEIGHTS_PATH).read_bytes()
    ):
        raise BoundedUNetPackageError("training replay weights differ")
    if result["history"] != tracked_history["history"]:
        raise BoundedUNetPackageError("training replay history differs")
    if (
        result["epoch_count"] != tracked_history["epoch_count"]
        or result["selected_epoch"] != tracked_report["selection"]["selected_epoch"]
        or result["final_epoch"] != tracked_report["training"]["final_epoch"]
    ):
        raise BoundedUNetPackageError("training replay selection/stopping drift")
    return {
        "training_history": history_identity,
        "training_report": report_identity,
        "candidate_weights": weights_identity,
        "replay_weights": {
            "path": replay_weights.as_posix(),
            "bytes": replay_weights.stat().st_size,
            "sha256": _sha256_file(replay_weights),
        },
        "epoch_count": result["epoch_count"],
        "selected_epoch": result["selected_epoch"],
        "final_epoch": result["final_epoch"],
        "history_exact": True,
        "weights_bytes_exact": True,
        "test_patch_ids_opened": result["roster"]["test_patch_ids_opened"],
        "test_event_group_ids_opened": result["roster"][
            "test_event_group_ids_opened"
        ],
    }


def build_decision(
    training_replay: dict[str, Any],
    evaluation_verification: dict[str, Any],
) -> dict[str, Any]:
    if not (
        training_replay["history_exact"]
        and training_replay["weights_bytes_exact"]
        and evaluation_verification["test_source_arrays_reopened"] is False
        and evaluation_verification["baseline_decision"]
        == "BELOW_RBR_REJECT_AS_ANALYTICAL_WINNER"
    ):
        raise BoundedUNetPackageError("decision entry gate failed")
    return {
        "decision_version": "burnlens-phase-three-model-decision-v0.1.0",
        "decision_id": "PHASE-THREE-MODEL-DECISION-2026-001",
        "decision": "reject-model-retain-baseline",
        "candidate_classification": "valid-trained-evaluated-rejected-model",
        "analytical_method": "burnlens-baseline-v0.1.0 rbr-threshold",
        "model_analytical_winner": False,
        "model_accepted": False,
        "model_released": False,
        "reason": (
            "The exact U-Net replay is reproducible, but its frozen test predicts "
            "all 89 selected cores as burned and scores event-class macro Dice "
            "0.29874213836477986 versus RBR 1.0."
        ),
        "phase_four_recommendation": {
            "route": "baseline-primary-with-rejected-model-diagnostic",
            "analytical_output": "RBR remains the accepted method",
            "model_role": (
                "Show the frozen U-Net probability/error evidence as a visibly "
                "rejected model-bearing diagnostic, never as the accepted perimeter."
            ),
            "required_vertical_slice": [
                "georeferenced RBR analytical raster",
                "georeferenced rejected-U-Net probability diagnostic",
                "side-by-side error and uncertainty visibility",
                "immutable run package and repository-owned reviewer interface",
            ],
        },
        "claims": {
            "valid_trained_model_artifact": True,
            "model_added_value": False,
            "model_superiority": False,
            "independent_ground_truth": False,
            "field_validation": False,
            "generalization": False,
            "operational_or_emergency_ready": False,
            "final_submission_ready": False,
        },
    }


def build_inference_contract() -> dict[str, Any]:
    return {
        "inference_contract_version": "burnlens-unet-inference-contract-v0.1.0",
        "inference_contract_id": "BOUNDED-UNET-INFERENCE-CONTRACT-2026-001",
        "model_version": MODEL_VERSION,
        "analytical_status": "rejected-as-analytical-winner",
        "permitted_role": "reviewer-visible rejected-model diagnostic only",
        "inputs": {
            "channel_order": [
                "pre_B04",
                "pre_B8A",
                "pre_B12",
                "post_B04",
                "post_B8A",
                "post_B12",
            ],
            "shape": [6, 64, 64],
            "dtype": "float32",
            "grid": "one common native 20-metre projected grid",
            "normalization": NORMALIZATION_VERSION,
            "invalid_input": "set normalized values to zero and exclude downstream",
        },
        "outputs": {
            "logit": "one float32 binary logit per pixel",
            "probability": "sigmoid(logit)",
            "binary_diagnostic": "probability >= 0.5",
            "georeferencing": "copy exact source patch CRS, affine transform, extent, and nodata mask",
        },
        "required_co_display": {
            "accepted_method": "burnlens-baseline-v0.1.0 rbr-threshold",
            "model_status": "rejected",
            "failure": "all-selected-core burned collapse on frozen test",
            "unknown_and_invalid": "visibly excluded, never coerced to background",
        },
        "prohibited": [
            "use as the accepted analytical perimeter",
            "threshold retuning",
            "population/generalization claim",
            "complete-scar area claim",
            "official, field-validated, operational, or emergency use",
        ],
    }


def build_model_card(
    git_source_commit: str,
    run_id: str,
    decision: dict[str, Any],
) -> bytes:
    return f"""# BurnLens U-Net binary v0.1.0

## Status

Valid trained and evaluated prototype; **rejected as the analytical winner**.
The accepted analytical method remains `burnlens-baseline-v0.1.0`
relative-burn-ratio thresholding.

## Intended portfolio role

Demonstrate a reproducible six-channel U-Net training/evaluation path and make
its failure visible beside the accepted baseline. It may appear in the Phase
Four application only as a clearly labeled rejected-model diagnostic.

## Architecture and inputs

- 117,473-parameter U-Net-style binary segmentation model
- six 20-metre Sentinel-2 channels: pre/post B04, B8A, and B12
- 64-by-64 float32 patches
- train-only normalization `burnlens-train-normalization-v0.1.0`
- exact loss mask excludes unknown, invalid, nodata, and non-binary pixels
- CPU, seed 20260725, Adam 0.001, batch four, threshold 0.5

## Data and labels

Dataset `burnlens-dataset-v0.1.0`, whole-event split
`burnlens-whole-event-split-v0.1.0`, and label schema
`burn-scar-binary-region-label-schema-v0.3.0`. Labels are owner-approved
prototype cores, not independent ground truth or field validation.

## Evaluation

One Ward Creek/Windigo opening is consumed. The model predicts all 89 selected
cores as burned:

- event-class macro Dice: 0.29874213836477986
- event-class macro IoU: 0.21474358974358976
- worst-event macro Dice: 0.2641509433962264
- masked BCE: 0.7280717492103577
- RBR baseline Dice/IoU/worst-event: 1.0 / 1.0 / 1.0

Decision: `{decision['decision']}`.

## Reproducibility

The U06 train/validation replay reproduces all 35 history rows, selected epoch
10, final epoch 35, and the exact 479,573-byte model weights SHA-256
`{WEIGHTS_SHA256}`. U05 probabilities, predictions, denominators, and decision
are independently reverified from immutable outputs without a second source
test-array opening.

## Limitations and prohibited claims

Six events, 12 patches, and 287 selected prototype cores do not establish
population performance. The test has two events and 89 selected cores. The
result does not measure full burn scars, natural prevalence, field validity,
generalization, official status, operational readiness, or emergency fitness.
The model must not be used as the accepted perimeter or area estimator.

## Trace

- source commit: `{git_source_commit}`
- replay run: `{run_id}`
- model: `{MODEL_VERSION}`
- dataset: `{DATASET_VERSION}`
- split: `{SPLIT_VERSION}`
- label schema: `{LABEL_SCHEMA_VERSION}`
- baseline: `{BASELINE_VERSION}`
""".encode("utf-8")


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in (
        Path("C:/Windows/Fonts/segoeui.ttf"),
        Path("C:/Windows/Fonts/arial.ttf"),
    ):
        if path.is_file():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def render_decision_png(decision: dict[str, Any]) -> bytes:
    image = Image.new("RGB", (1800, 1120), "#f4f0e8")
    draw = ImageDraw.Draw(image)
    dark = "#17211d"
    green = "#23634c"
    red = "#9a3e32"
    muted = "#5e6962"
    draw.rounded_rectangle((55, 45, 1745, 245), 28, fill=dark)
    draw.text((105, 82), "BurnLens Phase Three decision", font=_font(51), fill="white")
    draw.text(
        (108, 162),
        "Exact replay passes • model value gate fails • baseline retained",
        font=_font(27),
        fill="#d8e4dd",
    )
    cards = [
        ("Model Dice", "0.299", red),
        ("RBR Dice", "1.000", green),
        ("Selected epoch", "10", green),
        ("Replay weights", "exact", green),
    ]
    for index, (label, value, color) in enumerate(cards):
        left = 55 + index * 425
        draw.rounded_rectangle((left, 285, left + 395, 450), 22, fill="white")
        draw.text((left + 28, 315), label, font=_font(22), fill=muted)
        draw.text((left + 28, 357), value, font=_font(42), fill=color)
    draw.rounded_rectangle((55, 495, 1745, 735), 24, fill="#fff")
    draw.text((95, 535), "Decision", font=_font(25), fill=muted)
    draw.text(
        (95, 585),
        "Reject model as analytical winner; retain RBR",
        font=_font(40),
        fill=red,
    )
    draw.text(
        (95, 655),
        "The model predicts all 89 frozen test cores as burned.",
        font=_font(26),
        fill=dark,
    )
    draw.rounded_rectangle((55, 775, 1745, 1045), 24, fill="#fffaf0")
    draw.text((95, 815), "Phase Four", font=_font(28), fill=muted)
    lines = [
        "• RBR remains the accepted analytical raster.",
        "• Show U-Net probability/error as a rejected diagnostic.",
        "• Preserve CRS, affine grid, unknowns, and immutable run lineage.",
        "• No superiority, generalization, field, operational, or emergency claim.",
    ]
    for index, line in enumerate(lines):
        draw.text((105, 870 + index * 42), line, font=_font(22), fill=dark)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG", optimize=False)
    return buffer.getvalue()


def render_decision_html(
    decision: dict[str, Any],
    replay: dict[str, Any],
    image_name: str,
    git_source_commit: str,
    run_id: str,
) -> bytes:
    route = decision["phase_four_recommendation"]
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>BurnLens Phase Three model decision</title>
<style>
:root{{--ink:#17211d;--paper:#f4f0e8;--card:#fff;--green:#23634c;--red:#9a3e32;--line:#d5d0c4}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 Arial,sans-serif;overflow-x:hidden}}
main{{max-width:1120px;margin:auto;padding:42px 24px 72px}}h1{{font-size:clamp(2.2rem,6vw,4.5rem);line-height:1.02;margin:.2em 0}}h2{{margin-top:2.2rem}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:20px;margin:18px 0;overflow-wrap:anywhere}}.reject{{border-left:7px solid var(--red)}}
.metrics{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}}.metric strong{{display:block;font-size:1.7rem;color:var(--green)}}
img{{display:block;width:100%;height:auto;border:1px solid var(--line);border-radius:14px;background:#fff}}code{{overflow-wrap:anywhere}}
a{{color:#165f4c}}a:focus{{outline:3px solid var(--green);outline-offset:3px}}
@media(max-width:600px){{main{{padding:24px 14px 50px}}}}
</style></head><body><main>
<p>BURNLENS / PHASE THREE / ISSUE #566 / U06</p>
<h1>The model is reproducible. It is not the winner.</h1>
<div class="card reject"><strong>Decision: reject model, retain baseline.</strong><br>
The U-Net predicts all 89 selected test cores as burned. This is a valid trained/evaluated artifact, not an accepted model, ground truth, generalization result, or operational product.</div>
<div class="metrics">
<div class="card metric">Model Dice<strong>0.2987</strong></div>
<div class="card metric">RBR Dice<strong>1.0000</strong></div>
<div class="card metric">Selected epoch<strong>{replay['selected_epoch']}</strong></div>
<div class="card metric">Replay weights<strong>exact</strong></div>
</div>
<img src="{escape(image_name)}" width="1800" height="1120" alt="BurnLens Phase Three decision: exact replay passes, the U-Net scores 0.299 against RBR 1.0, and RBR is retained">
<h2>What passed</h2><div class="card"><ul>
<li>All 35 train/validation history rows reproduce exactly.</li>
<li>Selected epoch 10, final epoch 35, and weights SHA-256 <code>{WEIGHTS_SHA256}</code> reproduce.</li>
<li>Immutable U05 probabilities, predictions, denominators, and baseline decision reverify without a second source test-array opening.</li>
</ul></div>
<h2>What failed</h2><div class="card"><p>The model-value gate. Event-class macro Dice is 0.2987, macro IoU 0.2147, and worst-event Dice 0.2642, versus RBR 1.0 on all three. The model is rejected as the analytical winner.</p></div>
<h2>Phase Four handoff</h2><div class="card"><strong>{escape(route['route'])}</strong><p>{escape(route['analytical_output'])}. {escape(route['model_role'])}</p></div>
<h2>Inspect the evidence</h2><div class="card">
<p><a href="../../models/{MODEL_VERSION}/BOUNDED-UNET-TRAINING-2026-001.html">Training history</a> ·
<a href="../../evaluation/phase-three/bounded-unet-test-v0.1.0/BOUNDED-UNET-TEST-EVALUATION-2026-001.html">One-time test evaluation</a> ·
<a href="MODEL-CARD.md">Model card</a></p></div>
<h2>Boundary</h2><div class="card"><p>No second test opening, model acceptance, model release, georeferenced inference, deployment, field validation, generalization, or operational/emergency claim exists.</p></div>
<p>Trace: commit <code>{git_source_commit}</code> · run <code>{run_id}</code> · model <code>{MODEL_VERSION}</code> · dataset <code>{DATASET_VERSION}</code> · split <code>{SPLIT_VERSION}</code>.</p>
</main></body></html>
""".encode("utf-8")


def run_replay_and_package(
    root: Path,
    run_directory: Path,
    package_directory: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, dict[str, Any]]:
    root = root.resolve()
    run_directory = run_directory.resolve()
    package_directory = package_directory.resolve()
    if run_directory.parent != (root / RUN_DIRECTORY_ROOT).resolve():
        raise BoundedUNetPackageError("replay run path drift")
    if package_directory != (root / PACKAGE_DIRECTORY).resolve():
        raise BoundedUNetPackageError("package output path drift")
    if run_directory.exists() or run_directory.is_symlink():
        raise BoundedUNetPackageError("replay run already exists")
    if package_directory.exists() or package_directory.is_symlink():
        raise BoundedUNetPackageError("package output already exists")
    _require_exact_git_source(root, git_source_commit)
    run_directory.mkdir(parents=True)
    work = run_directory / "candidate"
    work.mkdir()

    replay = run_training_replay(root, run_directory / "replay-training")
    evaluation = verify_immutable_evaluation(root)
    decision = build_decision(replay, evaluation)
    inference_contract = build_inference_contract()
    replay_report = {
        "reproducibility_version": "burnlens-unet-reproducibility-v0.1.0",
        "reproducibility_id": "BOUNDED-UNET-REPRODUCIBILITY-2026-001",
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "git_source_commit": git_source_commit,
        "model_version": MODEL_VERSION,
        "training_replay": replay,
        "immutable_evaluation_verification": evaluation,
        "gates": {
            "history_exact": "pass",
            "weights_bytes_exact": "pass",
            "selection_and_stopping_exact": "pass",
            "test_source_arrays_reopened": "pass-false",
            "immutable_prediction_integrity": "pass",
            "event_class_aggregation": "pass",
            "baseline_decision": "pass-model-rejected",
        },
        "boundaries": {
            "replay_is_hyperparameter_search": False,
            "test_source_arrays_reopened": False,
            "test_open_count": 1,
            "second_test_opening": False,
            "model_changed": False,
            "threshold_changed": False,
        },
    }
    weights_receipt = _copy_new(
        root / WEIGHTS_PATH, work / f"{MODEL_VERSION}.pt"
    )
    _write_new(
        work / "MODEL-CARD.md",
        build_model_card(git_source_commit, run_id, decision),
    )
    _write_new(
        work / "INFERENCE-CONTRACT.json", _json_bytes(inference_contract)
    )
    _write_new(
        work / "PHASE-THREE-DECISION.json", _json_bytes(decision)
    )
    _write_new(
        work / "REPRODUCIBILITY-REPORT.json", _json_bytes(replay_report)
    )
    png_name = "PHASE-THREE-MODEL-DECISION.png"
    _write_new(work / png_name, render_decision_png(decision))
    _write_new(
        work / "PHASE-THREE-MODEL-DECISION.html",
        render_decision_html(
            decision, replay, png_name, git_source_commit, run_id
        ),
    )
    output_receipts: dict[str, dict[str, Any]] = {}
    for path in sorted(item for item in work.iterdir() if item.is_file()):
        output_receipts[path.name] = {
            "path": (PACKAGE_DIRECTORY / path.name).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": _sha256_file(path),
        }
    manifest = {
        "package_version": PACKAGE_VERSION,
        "package_id": PACKAGE_ID,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "git_source_commit": git_source_commit,
        "model_version": MODEL_VERSION,
        "model_status": "valid-trained-evaluated-rejected-model",
        "dataset_version": DATASET_VERSION,
        "split_version": SPLIT_VERSION,
        "normalization_version": NORMALIZATION_VERSION,
        "label_schema_version": LABEL_SCHEMA_VERSION,
        "baseline_version": BASELINE_VERSION,
        "decision": decision["decision"],
        "weights": {
            **weights_receipt,
            "path": (PACKAGE_DIRECTORY / f"{MODEL_VERSION}.pt").as_posix(),
        },
        "outputs": output_receipts,
        "test_open_count": 1,
        "second_test_opening": False,
        "accepted_model": False,
        "released_model": False,
        "next_dependency": (
            "Phase Four issue-backed baseline-primary vertical slice with the "
            "rejected U-Net shown only as transparent diagnostic evidence"
        ),
    }
    _write_new(work / "MODEL-PACKAGE-MANIFEST.json", _json_bytes(manifest))
    _promote_tree(work, package_directory)
    receipts: dict[str, dict[str, Any]] = {}
    for path in sorted(item for item in package_directory.iterdir() if item.is_file()):
        receipts[path.name] = {
            "path": path.relative_to(root).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": _sha256_file(path),
        }
    return receipts


def record_failed_package(
    run_directory: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
    error: BaseException,
) -> None:
    run_directory.mkdir(parents=True, exist_ok=True)
    path = run_directory / "ATTEMPT-FAILED.json"
    if path.exists():
        return
    _write_new(
        path,
        _json_bytes(
            {
                "attempt_version": "burnlens-unet-package-attempt-v0.1.0",
                "generated_at_utc": generated_at_utc,
                "run_id": run_id,
                "git_source_commit": git_source_commit,
                "error_type": type(error).__name__,
                "error": str(error),
                "test_source_arrays_reopened": False,
                "test_open_count": 1,
                "retry_test_authorized": False,
                "disposition": "retain-and-stop-or-remediate-without-test-reopen",
            }
        ),
    )
