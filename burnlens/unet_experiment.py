"""Freeze and preflight the one authorized BurnLens U-Net experiment."""

from __future__ import annotations

from hashlib import sha256
from html import escape
import json
import math
import os
from pathlib import Path
from typing import Any, Iterable

from PIL import Image, ImageDraw, ImageFont
import torch

from burnlens.bounded_unet import (
    BoundedUNet,
    BoundedUNetError,
    CHANNEL_ORDER,
    DATASET_MANIFEST_PATH,
    DATASET_MANIFEST_SHA256,
    EARLY_STOPPING_MIN_DELTA,
    EARLY_STOPPING_PATIENCE,
    EarlyStoppingState,
    LEARNING_RATE,
    MODEL_VERSION,
    NORMALIZATION_PATH,
    NORMALIZATION_SHA256,
    SEED,
    TRAINING_CONTRACT_PATH,
    TRAINING_CONTRACT_SHA256,
    TestAccessGrant,
    architecture_record,
    configure_deterministic_execution,
    load_model_examples,
    make_optimizer,
    masked_bce_with_logits,
    masked_binary_metrics,
    require_finite_training_state,
    stack_examples,
)


PROTOCOL_VERSION = "burnlens-bounded-unet-experiment-protocol-v0.1.0"
PROTOCOL_ID = "BOUNDED-UNET-EXPERIMENT-PROTOCOL-2026-001"
PREFLIGHT_VERSION = "burnlens-bounded-unet-preflight-v0.1.0"
PREFLIGHT_ID = "BOUNDED-UNET-PREFLIGHT-2026-001"
TEST_AUTHORIZATION_VERSION = "burnlens-sealed-test-authorization-v0.1.0"
TEST_OPENING_UNIT = "P3O1-T01-U05"
TEST_AUTHORIZATION_DIRECTORY = Path("records/phase-three/test-openings")
TRAIN_EVENT_IDS = (
    "event-green-ridge-0684-cs-2020",
    "event-tepee-1144-ne-2018",
)
VALIDATION_EVENT_IDS = (
    "event-grandview-0558-od-2021",
    "event-mckay-1035-ne-2017",
)
TEST_EVENT_IDS = (
    "event-ward-creek-2019",
    "event-windigo-2022",
)


class UNetExperimentError(BoundedUNetError):
    """A frozen experiment-protocol or preflight failure."""


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(8 * 1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def _write_new(path: Path, payload: bytes) -> dict[str, Any]:
    if path.exists():
        raise UNetExperimentError(f"output already exists: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())
    return {
        "path": path.as_posix(),
        "bytes": path.stat().st_size,
        "sha256": _sha256_file(path),
    }


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise UNetExperimentError(f"JSON root is not an object: {path}")
    return value


def _bound_json(root: Path, relative: Path, expected_sha256: str) -> dict[str, Any]:
    path = root / relative
    if not path.is_file() or _sha256_file(path) != expected_sha256:
        raise UNetExperimentError(f"bound input drift: {relative.as_posix()}")
    return _read_json(path)


def _test_roster(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    roster: list[dict[str, Any]] = []
    for patch in manifest.get("patches", []):
        if patch.get("split_role") != "test":
            continue
        files = [
            {
                "path": item["path"],
                "bytes": item["bytes"],
                "sha256": item["sha256"],
            }
            for item in patch.get("files", [])
        ]
        roster.append(
            {
                "patch_id": patch["patch_id"],
                "event_group_id": patch["event_group_id"],
                "files": files,
            }
        )
    if len(roster) != 4:
        raise UNetExperimentError(f"sealed test roster drift: {len(roster)}")
    if tuple(sorted({item["event_group_id"] for item in roster})) != tuple(
        sorted(TEST_EVENT_IDS)
    ):
        raise UNetExperimentError("sealed test event roster drift")
    return roster


def build_protocol(
    root: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, Any]:
    """Build the immutable pre-training protocol without opening any array."""

    manifest = _bound_json(
        root, DATASET_MANIFEST_PATH, DATASET_MANIFEST_SHA256
    )
    normalization = _bound_json(
        root, NORMALIZATION_PATH, NORMALIZATION_SHA256
    )
    contract = _bound_json(
        root, TRAINING_CONTRACT_PATH, TRAINING_CONTRACT_SHA256
    )
    if tuple(normalization["channel_order"]) != CHANNEL_ORDER:
        raise UNetExperimentError("normalization channel order drift")
    if contract["authorization"]["decision"] != "AUTHORIZE_BOUNDED_UNET":
        raise UNetExperimentError("model authorization drift")
    if contract["architecture"]["model_count"] != 1:
        raise UNetExperimentError("model count drift")
    return {
        "protocol_version": PROTOCOL_VERSION,
        "protocol_id": PROTOCOL_ID,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "issue": 566,
        "unit_id": "P3O1-T01-U03",
        "git_source_commit": git_source_commit,
        "software_version": "0.52.0",
        "model_version_candidate": MODEL_VERSION,
        "environment_capture_id": "MODEL-ENVIRONMENT-CAPTURE-2026-001",
        "exact_inputs": {
            "dataset_manifest": {
                "path": DATASET_MANIFEST_PATH.as_posix(),
                "bytes": (root / DATASET_MANIFEST_PATH).stat().st_size,
                "sha256": DATASET_MANIFEST_SHA256,
            },
            "normalization": {
                "path": NORMALIZATION_PATH.as_posix(),
                "bytes": (root / NORMALIZATION_PATH).stat().st_size,
                "sha256": NORMALIZATION_SHA256,
            },
            "training_contract": {
                "path": TRAINING_CONTRACT_PATH.as_posix(),
                "bytes": (root / TRAINING_CONTRACT_PATH).stat().st_size,
                "sha256": TRAINING_CONTRACT_SHA256,
            },
            "split_manifest": contract["exact_inputs"]["split_manifest"],
            "baseline_evaluation": contract["exact_inputs"]["baseline_evaluation"],
        },
        "data": {
            "channel_order": list(CHANNEL_ORDER),
            "input_shape": [6, 64, 64],
            "input_dtype": "float32",
            "target_shape": [1, 64, 64],
            "target": "state == 1",
            "loss_mask": "exact input_valid AND state in {0,1}",
            "normalization": "frozen train-only per-channel mean/population std",
            "batch_order": "canonical dataset-manifest order",
            "shuffle": False,
            "augmentation": "none",
            "train_events": list(TRAIN_EVENT_IDS),
            "validation_events": list(VALIDATION_EVENT_IDS),
            "test_events": list(TEST_EVENT_IDS),
            "sealed_test_roster": _test_roster(manifest),
        },
        "architecture": contract["architecture"],
        "optimization": {
            **contract["optimization"],
            "num_workers": 0,
            "intra_op_threads": 1,
            "interop_threads": 1,
        },
        "checkpoint_selection": contract["checkpoint_selection"],
        "compute_budget": {
            "device": "one local CPU",
            "substantive_run_count": 1,
            "batch_size": 4,
            "maximum_epochs": 200,
            "early_stopping_patience": EARLY_STOPPING_PATIENCE,
            "preflight_epochs": 2,
            "preflight_weights_retained": False,
            "architecture_or_hyperparameter_search": False,
        },
        "test_opening": {
            "authorization_version": TEST_AUTHORIZATION_VERSION,
            "authorization_directory": TEST_AUTHORIZATION_DIRECTORY.as_posix(),
            "authorization_unit": TEST_OPENING_UNIT,
            "authorization_status_required": "AUTHORIZED_NOT_OPENED",
            "open_count_before_required": 0,
            "open_count_authorized": 1,
            "required_candidate_bindings": [
                "config_sha256",
                "weights_sha256",
                "selection_sha256",
                "environment_capture_sha256",
            ],
            "missing_or_mismatched_authorization": "fail before numpy.load",
            "receipt": "no-overwrite exact-byte receipt after the single U05 evaluation",
            "post_test_change": "prohibited; any change creates a new model version and leaves the first result immutable",
        },
        "required_u04_outputs": [
            "frozen config",
            "complete training history",
            "validation per-event/class denominators and metrics",
            "selected epoch and tie-break evidence",
            "exact weights bytes and SHA-256",
            "finite-state ledger",
            "environment capture",
        ],
        "required_u05_outputs": contract["required_outputs"][5:8],
        "required_u06_outputs": [
            "same-environment exact replay",
            "model or rejected-model package",
            "model card",
            "inference contract",
            "baseline comparison",
            "Phase Four decision",
        ],
        "retention": {
            "preflight": "tracked samples/evaluation/phase-three/preflight-v0.1.0",
            "substantive_working": "ignored repository-local runs/phase-three",
            "candidate": "tracked samples/models/burnlens-unet-binary-v0.1.0 after U04 gates",
            "failed_attempts": "retained with immutable attempt IDs and dispositions",
            "overwrite": "prohibited",
        },
        "claims": {
            "prototype_labels_only": True,
            "independent_ground_truth": False,
            "field_validation": False,
            "generalization": False,
            "model_superiority": False,
            "official_or_operational": False,
            "final_submission_ready": False,
        },
        "stop_conditions": contract["stop_conditions"],
        "boundaries": {
            "model_count": 1,
            "test_arrays_opened": False,
            "test_open_count": 0,
            "substantive_training_started": False,
            "weights_created": False,
            "dataset_split_label_normalization_or_baseline_change": False,
            "inference_or_deployment": False,
        },
        "next_dependency": "two-epoch train/validation-only preflight and rendered diagnostics",
    }


def write_protocol(
    root: Path,
    output_path: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, Any]:
    protocol = build_protocol(
        root, generated_at_utc, run_id, git_source_commit
    )
    return _write_new(output_path, _json_bytes(protocol))


def load_test_access_grant(
    root: Path,
    authorization_path: Path,
    *,
    config_sha256: str,
    weights_sha256: str,
    selection_sha256: str,
    environment_capture_sha256: str,
) -> TestAccessGrant:
    """Validate the exact pre-open U05 authorization without opening arrays."""

    resolved_root = root.resolve()
    resolved_path = authorization_path.resolve()
    expected_parent = (root / TEST_AUTHORIZATION_DIRECTORY).resolve()
    if resolved_path.parent != expected_parent:
        raise UNetExperimentError("test authorization is outside the frozen directory")
    if not resolved_path.is_file():
        raise UNetExperimentError("test authorization is absent")
    value = _read_json(resolved_path)
    required = {
        "authorization_version",
        "opening_id",
        "authorization_unit",
        "status",
        "open_count_before",
        "open_count_authorized",
        "config_sha256",
        "weights_sha256",
        "selection_sha256",
        "environment_capture_sha256",
        "test_event_group_ids",
        "test_patch_ids",
    }
    if set(value) != required:
        raise UNetExperimentError("test authorization schema drift")
    expected = {
        "authorization_version": TEST_AUTHORIZATION_VERSION,
        "authorization_unit": TEST_OPENING_UNIT,
        "status": "AUTHORIZED_NOT_OPENED",
        "open_count_before": 0,
        "open_count_authorized": 1,
        "config_sha256": config_sha256,
        "weights_sha256": weights_sha256,
        "selection_sha256": selection_sha256,
        "environment_capture_sha256": environment_capture_sha256,
        "test_event_group_ids": list(TEST_EVENT_IDS),
    }
    for key, expected_value in expected.items():
        if value.get(key) != expected_value:
            raise UNetExperimentError(f"test authorization binding drift: {key}")
    opening_id = value.get("opening_id")
    if not isinstance(opening_id, str) or not opening_id.startswith("TEST-OPEN-"):
        raise UNetExperimentError("test opening ID is invalid")
    patch_ids = value.get("test_patch_ids")
    if not isinstance(patch_ids, list) or len(patch_ids) != 4:
        raise UNetExperimentError("test authorization patch roster drift")
    manifest = _bound_json(
        root, DATASET_MANIFEST_PATH, DATASET_MANIFEST_SHA256
    )
    expected_patch_ids = [
        item["patch_id"] for item in _test_roster(manifest)
    ]
    if patch_ids != expected_patch_ids:
        raise UNetExperimentError("test authorization patch roster drift")
    try:
        relative = resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise UNetExperimentError("test authorization is outside repository") from exc
    return TestAccessGrant(
        opening_id=opening_id,
        authorization_path=relative.as_posix(),
        authorization_sha256=_sha256_file(resolved_path),
        config_sha256=config_sha256,
        weights_sha256=weights_sha256,
        selection_sha256=selection_sha256,
        authorized=True,
    )


def _event_metrics(
    model: BoundedUNet,
    examples: Iterable[Any],
) -> dict[str, Any]:
    roster = list(examples)
    if not roster:
        raise UNetExperimentError("evaluation roster is empty")
    events: list[dict[str, Any]] = []
    total_loss_sum = 0.0
    total_pixels = 0
    for event_id in sorted({item.event_group_id for item in roster}):
        event_examples = [item for item in roster if item.event_group_id == event_id]
        inputs, targets, masks = stack_examples(event_examples)
        logits = model(inputs)
        event_loss = masked_bce_with_logits(logits, targets, masks)
        metrics = masked_binary_metrics(logits, targets, masks, threshold=0.5)
        core_pixels = metrics["core_pixels"]
        total_loss_sum += float(event_loss.detach().item()) * core_pixels
        total_pixels += core_pixels
        events.append(
            {
                "event_group_id": event_id,
                "patch_count": len(event_examples),
                "masked_bce": float(event_loss.detach().item()),
                **metrics,
            }
        )
    if total_pixels <= 0:
        raise UNetExperimentError("evaluation mask is empty")
    class_rows = [
        class_metric
        for event in events
        for class_metric in event["classes"]
    ]
    event_macro_dice = [
        sum(item["dice"] for item in event["classes"]) / 2 for event in events
    ]
    return {
        "event_count": len(events),
        "core_pixels": total_pixels,
        "masked_bce": total_loss_sum / total_pixels,
        "event_class_macro_dice": (
            sum(item["dice"] for item in class_rows) / len(class_rows)
        ),
        "event_class_macro_iou": (
            sum(item["iou"] for item in class_rows) / len(class_rows)
        ),
        "worst_event_macro_dice": min(event_macro_dice),
        "events": events,
    }


def run_preflight(
    root: Path,
    protocol_path: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, Any]:
    """Run exactly two ephemeral train/validation epochs with test sealed."""

    protocol = _read_json(protocol_path)
    if protocol.get("protocol_version") != PROTOCOL_VERSION:
        raise UNetExperimentError("protocol version drift")
    if protocol.get("git_source_commit") != git_source_commit:
        raise UNetExperimentError("protocol/source commit drift")
    if protocol["boundaries"]["test_arrays_opened"] is not False:
        raise UNetExperimentError("protocol test boundary drift")
    settings = configure_deterministic_execution(SEED, 1)
    training = load_model_examples(root, {"train"})
    validation = load_model_examples(root, {"validation"})
    if tuple(sorted({item.event_group_id for item in training})) != tuple(
        sorted(TRAIN_EVENT_IDS)
    ):
        raise UNetExperimentError("training event roster drift")
    if tuple(sorted({item.event_group_id for item in validation})) != tuple(
        sorted(VALIDATION_EVENT_IDS)
    ):
        raise UNetExperimentError("validation event roster drift")

    model = BoundedUNet()
    optimizer = make_optimizer(model)
    stopping = EarlyStoppingState()
    train_inputs, train_targets, train_masks = stack_examples(training)
    history: list[dict[str, Any]] = []
    for epoch in range(1, 3):
        model.train()
        optimizer.zero_grad(set_to_none=True)
        logits = model(train_inputs)
        train_loss = masked_bce_with_logits(
            logits, train_targets, train_masks
        )
        train_loss.backward()
        require_finite_training_state(model)
        optimizer.step()
        require_finite_training_state(model)
        model.eval()
        with torch.no_grad():
            validation_metrics = _event_metrics(model, validation)
        improved, would_stop = stopping.consider(
            epoch,
            validation_metrics["event_class_macro_dice"],
            validation_metrics["event_class_macro_iou"],
            validation_metrics["masked_bce"],
        )
        history.append(
            {
                "epoch": epoch,
                "train_masked_bce": float(train_loss.detach().item()),
                "validation": validation_metrics,
                "checkpoint_improved": improved,
                "would_early_stop": would_stop,
            }
        )
    return {
        "preflight_version": PREFLIGHT_VERSION,
        "preflight_id": PREFLIGHT_ID,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "issue": 566,
        "unit_id": "P3O1-T01-U03",
        "git_source_commit": git_source_commit,
        "software_version": "0.52.0",
        "model_version_candidate": MODEL_VERSION,
        "protocol": {
            "path": protocol_path.as_posix(),
            "bytes": protocol_path.stat().st_size,
            "sha256": _sha256_file(protocol_path),
        },
        "architecture": architecture_record(model),
        "environment": {
            "torch": torch.__version__,
            "device": "cpu",
            **settings,
        },
        "smoke_contract": {
            "epochs": 2,
            "batch_size": 4,
            "optimizer": "Adam",
            "learning_rate": LEARNING_RATE,
            "weights_retained": False,
            "checkpoint_retained": False,
            "substantive_training": False,
        },
        "roster": {
            "train_patch_ids": [item.patch_id for item in training],
            "train_event_group_ids": list(TRAIN_EVENT_IDS),
            "train_core_pixels": sum(
                int(item.loss_mask.sum().item()) for item in training
            ),
            "validation_patch_ids": [item.patch_id for item in validation],
            "validation_event_group_ids": list(VALIDATION_EVENT_IDS),
            "validation_core_pixels": sum(
                int(item.loss_mask.sum().item()) for item in validation
            ),
            "test_patch_ids_opened": [],
            "test_event_group_ids_opened": [],
        },
        "history": history,
        "selected_preflight_epoch": stopping.best_epoch,
        "warnings": [
            "Two-epoch train/validation connectivity smoke only; not the substantive U04 training run.",
            "No preflight weights or checkpoint may be used as the model candidate.",
            "Owner-approved prototype labels are not independent ground truth or field validation.",
            "The frozen RBR baseline remains at the selected-core metric ceiling.",
        ],
        "gates": {
            "protocol_bound": True,
            "train_and_validation_only": True,
            "test_arrays_opened": False,
            "finite": True,
            "exact_loss_mask": True,
            "optimizer_step": True,
            "render_required": True,
            "weights_retained": False,
        },
        "disposition": "pass-preflight-not-model",
        "next_dependency": "P3O1-T01-U04 one substantive training run after exact U03 freeze",
    }


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = (
        Path("C:/Windows/Fonts/segoeui.ttf"),
        Path("C:/Windows/Fonts/arial.ttf"),
    )
    for path in candidates:
        if path.is_file():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def render_preflight_png(report: dict[str, Any]) -> bytes:
    image = Image.new("RGB", (1800, 1120), "#f4f0e8")
    draw = ImageDraw.Draw(image)
    dark = "#17211d"
    green = "#23634c"
    amber = "#9a5b19"
    muted = "#5e6962"
    draw.rounded_rectangle((60, 50, 1740, 250), 28, fill=dark)
    draw.text((105, 88), "BurnLens bounded U-Net preflight", font=_font(54), fill="white")
    draw.text(
        (108, 166),
        "Two train/validation-only epochs • sealed test unopened • no weights retained",
        font=_font(28),
        fill="#d8e4dd",
    )
    history = report["history"]
    latest = history[-1]
    cards = [
        ("Train cores", str(report["roster"]["train_core_pixels"]), green),
        ("Validation cores", str(report["roster"]["validation_core_pixels"]), green),
        (
            "Epoch 2 val Dice",
            f"{latest['validation']['event_class_macro_dice']:.3f}",
            amber,
        ),
        (
            "Epoch 2 val BCE",
            f"{latest['validation']['masked_bce']:.3f}",
            amber,
        ),
    ]
    for index, (label, value, color) in enumerate(cards):
        left = 60 + index * 420
        draw.rounded_rectangle((left, 290, left + 390, 455), 22, fill="white")
        draw.text((left + 28, 320), label, font=_font(23), fill=muted)
        draw.text((left + 28, 362), value, font=_font(46), fill=color)
    draw.text((70, 510), "Preflight trajectory", font=_font(34), fill=dark)
    chart = (100, 575, 1120, 935)
    draw.rounded_rectangle(chart, 20, fill="white")
    x0, y0, x1, y1 = chart
    draw.line((x0 + 90, y1 - 70, x1 - 55, y1 - 70), fill="#bcc6bf", width=3)
    draw.line((x0 + 90, y0 + 45, x0 + 90, y1 - 70), fill="#bcc6bf", width=3)
    for idx, item in enumerate(history):
        x = x0 + 250 + idx * 470
        dice = item["validation"]["event_class_macro_dice"]
        bce = item["validation"]["masked_bce"]
        dice_height = int(dice * 230)
        bce_height = int(min(bce, 1.0) * 230)
        draw.rectangle(
            (x - 75, y1 - 70 - dice_height, x - 5, y1 - 70),
            fill=green,
        )
        draw.rectangle(
            (x + 20, y1 - 70 - bce_height, x + 90, y1 - 70),
            fill=amber,
        )
        draw.text((x - 40, y1 - 52), f"E{item['epoch']}", font=_font(22), fill=dark)
    draw.rectangle((160, 965, 195, 1000), fill=green)
    draw.text((210, 968), "validation event-class macro Dice", font=_font(22), fill=dark)
    draw.rectangle((650, 965, 685, 1000), fill=amber)
    draw.text((700, 968), "validation masked BCE", font=_font(22), fill=dark)
    draw.rounded_rectangle((1190, 510, 1740, 1010), 24, fill="#fffaf0")
    draw.text((1230, 550), "What this proves", font=_font(32), fill=dark)
    bullets = [
        "Exact arrays load and normalize",
        "Masked loss and optimizer connect",
        "Per-event validation metrics render",
        "Deterministic CPU controls hold",
        "Test roster remains metadata-only",
        "No checkpoint or model is promoted",
    ]
    y = 625
    for bullet in bullets:
        draw.ellipse((1232, y + 8, 1248, y + 24), fill=green)
        draw.text((1265, y), bullet, font=_font(22), fill=dark)
        y += 58
    import io

    output = io.BytesIO()
    image.save(output, format="PNG", optimize=False, compress_level=9)
    return output.getvalue()


def render_preflight_html(report: dict[str, Any], image_name: str) -> bytes:
    history_rows = "".join(
        "<tr>"
        f"<td>{item['epoch']}</td>"
        f"<td>{item['train_masked_bce']:.9f}</td>"
        f"<td>{item['validation']['masked_bce']:.9f}</td>"
        f"<td>{item['validation']['event_class_macro_dice']:.9f}</td>"
        f"<td>{item['validation']['event_class_macro_iou']:.9f}</td>"
        f"<td>{item['validation']['worst_event_macro_dice']:.9f}</td>"
        "</tr>"
        for item in report["history"]
    )
    warnings = "".join(
        f"<li>{escape(item)}</li>" for item in report["warnings"]
    )
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>BurnLens bounded U-Net preflight</title>
<style>
:root{{--ink:#17211d;--muted:#5e6962;--paper:#f4f0e8;--card:#fff;--green:#23634c;--amber:#9a5b19}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,sans-serif}}
a{{color:var(--green)}} .skip{{position:absolute;left:-999px}} .skip:focus{{left:1rem;top:1rem;background:#fff;padding:.7rem;z-index:2}}
main{{width:min(1120px,calc(100% - 2rem));margin:2rem auto 4rem}} header,.card{{background:var(--card);border-radius:18px;padding:clamp(1.1rem,3vw,2.2rem);margin-bottom:1.2rem}}
h1{{margin:.2rem 0;font-size:clamp(2rem,6vw,3.8rem);line-height:1.05}} h2{{margin-top:0}} .eyebrow{{color:var(--green);font-weight:800;letter-spacing:.08em;text-transform:uppercase}}
.warning{{border-left:6px solid var(--amber);background:#fffaf0}} img{{display:block;width:100%;height:auto;border-radius:14px}}
.table-wrap{{overflow-x:auto}} table{{border-collapse:collapse;width:100%;min-width:760px}} th,td{{padding:.65rem;border-bottom:1px solid #d9ddd9;text-align:right}} th:first-child,td:first-child{{text-align:left}}
code{{overflow-wrap:anywhere}} @media(max-width:520px){{main{{width:min(100% - 1rem,1120px);margin-top:.5rem}} header,.card{{border-radius:12px}}}}
</style>
</head>
<body>
<a class="skip" href="#evidence">Skip to evidence</a>
<main>
<header>
<p class="eyebrow">P3O1-T01-U03 • protocol preflight</p>
<h1>One model path, still before training</h1>
<p>Two deterministic train/validation-only epochs prove that the frozen data, model, loss, optimizer, metrics, and renderer connect. Ward Creek and Windigo test arrays remain unopened.</p>
</header>
<section class="card warning" aria-labelledby="boundary"><h2 id="boundary">Boundary</h2><ul>{warnings}</ul></section>
<section class="card" id="evidence" aria-labelledby="figure"><h2 id="figure">Rendered preflight evidence</h2><img src="{escape(image_name)}" alt="Two-epoch BurnLens preflight chart with train and validation core counts, validation Dice and BCE, and explicit no-model boundary."></section>
<section class="card" aria-labelledby="history"><h2 id="history">Exact two-epoch history</h2><div class="table-wrap"><table><thead><tr><th>Epoch</th><th>Train BCE</th><th>Validation BCE</th><th>Event-class macro Dice</th><th>Event-class macro IoU</th><th>Worst-event macro Dice</th></tr></thead><tbody>{history_rows}</tbody></table></div></section>
<section class="card" aria-labelledby="lineage"><h2 id="lineage">Lineage</h2><dl><dt>Run</dt><dd><code>{escape(report['run_id'])}</code></dd><dt>Source commit</dt><dd><code>{escape(report['git_source_commit'])}</code></dd><dt>Protocol SHA-256</dt><dd><code>{escape(report['protocol']['sha256'])}</code></dd><dt>Disposition</dt><dd><code>{escape(report['disposition'])}</code></dd></dl></section>
</main>
</body>
</html>
"""
    return html.encode("utf-8")


def write_preflight_outputs(
    root: Path,
    protocol_path: Path,
    output_directory: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, dict[str, Any]]:
    report = run_preflight(
        root,
        protocol_path,
        generated_at_utc,
        run_id,
        git_source_commit,
    )
    stem = "BOUNDED-UNET-PREFLIGHT-2026-001"
    png_path = output_directory / f"{stem}.png"
    html_path = output_directory / f"{stem}.html"
    json_path = output_directory / f"{stem}.json"
    png = _write_new(png_path, render_preflight_png(report))
    html = _write_new(
        html_path,
        render_preflight_html(report, png_path.name),
    )
    report["outputs"] = {
        "png": png,
        "html": html,
    }
    report["gates"]["render_required"] = True
    json_receipt = _write_new(json_path, _json_bytes(report))
    return {
        "json": json_receipt,
        "html": html,
        "png": png,
    }
