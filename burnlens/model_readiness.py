"""Audit the Phase Two package and bind one bounded U-Net experiment."""

from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from html import escape
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from . import __version__


AUDIT_ID = "MODEL-READINESS-AUDIT-2026-001"
DECISION_ID = "MODEL-READINESS-DECISION-2026-001"
CONTRACT_ID = "BOUNDED-UNET-TRAINING-CONTRACT-2026-001"
AUDIT_VERSION = "burnlens-model-readiness-audit-v0.1.0"
CONTRACT_VERSION = "burnlens-bounded-unet-training-contract-v0.1.0"
TASK_ISSUE = 562
UNIT_ID = "P2O5-T03-U06"
DEADLINE = "2026-08-06"
WARNING = (
    "Owner-approved prototype evidence, not independent ground truth, field "
    "validation, generalization, official information, or operational guidance."
)

INPUTS = {
    "dataset_manifest": (
        Path("samples/datasets/burnlens-dataset-v0.1.0/DATASET-MANIFEST.json"),
        "e0b7ac666a70e96f979c386a9d503ad45ed0baea8f21e3838ba4530d5e3d2d16",
    ),
    "dataset_candidate": (
        Path("records/phase-two/readiness/DATASET-CANDIDATE-2026-002.json"),
        "4a9646af493cdce81d0cd57405ebccf0dfecf5ca77c96930d0837c3b7d4e65f2",
    ),
    "split_manifest": (
        Path("records/phase-two/manifests/WHOLE-EVENT-SPLIT-2026-001.json"),
        "a62e66f4f81a95a56a727b29bb382cb87369306f11e2f2a4527d1c7fb68d0b99",
    ),
    "dataset_qa": (
        Path("samples/qa/phase-two/dataset-v0.1.0/DATASET-QA-2026-001.json"),
        "90aafef4c9deb8e9d06c2c2dc63f4f238e0229e4615dc29e1686803efa342f5a",
    ),
    "normalization": (
        Path("records/phase-two/manifests/TRAIN-NORMALIZATION-2026-001.json"),
        "6344861677753e9c96840f47e7a038a15f12a0c29759285c073f5cc6ea4bc255",
    ),
    "baseline_protocol": (
        Path("records/phase-two/manifests/BASELINE-PREREGISTRATION-2026-001.json"),
        "31eb08ae88ee0b4425dce8af3e47475e38a4d9adb9249af7381fc5d608799bb5",
    ),
    "baseline_selection": (
        Path("records/phase-two/manifests/BASELINE-SELECTION-2026-001.json"),
        "061596f7df68844319cc3c5a5d8d0b19124cecc812e59c3a7eda9d5d3e68c1c3",
    ),
    "baseline_evaluation": (
        Path(
            "samples/baselines/burnlens-baseline-v0.1.0/"
            "BASELINE-EVALUATION-2026-001.json"
        ),
        "a8ba82f999a87a8114c7fc417126b96c1f031e7eb9e24311df20fe32d7edb221",
    ),
    "model_family_decision": (
        Path("docs/phase-one/objective-two/MODEL_FAMILY_DECISION.md"),
        "3e4ac46a0e046d9c678f5ee10faecfb8e457b70fb909926bdd61916914789f56",
    ),
    "phase_two_objective": (
        Path("docs/phases/phase-02/PHASE_02_OBJECTIVES.md"),
        "9e5150976d8a1af531c5cb320059111d019fcd1d07ab60753de0bfc18edad18e",
    ),
    "tooling_sources": (
        Path("records/phase-two/sources/MODEL-TOOLING-SOURCES-2026-001.json"),
        "5e55f5fb5572a9ccfaef79d1c91f0b965771d1a99a047540598fc158ed190ffc",
    ),
}


class ModelReadinessError(RuntimeError):
    """A fail-closed model-readiness audit error."""


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(
        "utf-8"
    )


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(8 * 1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ModelReadinessError(f"JSON root is not an object: {path}")
    return value


def _load_inputs(
    root: Path,
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    bindings: dict[str, dict[str, Any]] = {}
    values: dict[str, dict[str, Any]] = {}
    for name, (relative, expected_sha256) in INPUTS.items():
        path = root / relative
        if not path.is_file():
            raise ModelReadinessError(
                f"required input is absent: {relative.as_posix()}"
            )
        observed = _sha256_file(path)
        if observed != expected_sha256:
            raise ModelReadinessError(f"{name} input hash drift")
        bindings[name] = {
            "path": relative.as_posix(),
            "bytes": path.stat().st_size,
            "sha256": observed,
        }
        if path.suffix == ".json":
            values[name] = _read_json(path)
    return bindings, values


def _require(condition: bool, message: str) -> dict[str, Any]:
    if not condition:
        raise ModelReadinessError(message)
    return {"status": "pass", "finding": message}


def _days_to_deadline(generated_at_utc: str) -> int:
    generated = datetime.fromisoformat(generated_at_utc.replace("Z", "+00:00"))
    if generated.tzinfo is None:
        generated = generated.replace(tzinfo=timezone.utc)
    deadline = datetime(2026, 8, 7, tzinfo=timezone.utc)
    return max(0, (deadline - generated).days)


def training_contract(
    bindings: dict[str, dict[str, Any]],
    values: dict[str, dict[str, Any]],
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, Any]:
    split = values["split_manifest"]
    dataset = values["dataset_manifest"]
    candidate = values["dataset_candidate"]
    baseline = values["baseline_evaluation"]
    normalization = values["normalization"]
    return {
        "training_contract_version": CONTRACT_VERSION,
        "training_contract_id": CONTRACT_ID,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": TASK_ISSUE,
        "unit_id": UNIT_ID,
        "git_source_commit": git_source_commit,
        "software_version_at_decision": __version__,
        "authorization": {
            "decision": "AUTHORIZE_BOUNDED_UNET",
            "scope": "one rejection-first CPU-only U-Net training/evaluation milestone",
            "model_code_authorized_after_verified_u07_release": True,
            "training_authorized_after_verified_u07_release": True,
            "architecture_search_authorized": False,
            "hyperparameter_search_authorized": False,
            "test_tuning_authorized": False,
            "deployment_authorized": False,
            "claim_of_model_value_authorized": False,
        },
        "exact_inputs": {
            "dataset_id": dataset["dataset_id"],
            "dataset_version": dataset["dataset_version"],
            "dataset_manifest": bindings["dataset_manifest"],
            "split_id": split["split_id"],
            "split_version": split["split_version"],
            "split_manifest": bindings["split_manifest"],
            "normalization": bindings["normalization"],
            "normalization_id": normalization["normalization_id"],
            "label_schema_version": candidate["label_schema_version"],
            "label_set_version": candidate["label_set_version"],
            "baseline_version": baseline["baseline_version"],
            "baseline_evaluation": bindings["baseline_evaluation"],
            "baseline_family": baseline["selected"]["family_id"],
            "baseline_threshold": baseline["selected"]["threshold"],
        },
        "data_contract": {
            "input_channels": [
                "pre_B04",
                "pre_B8A",
                "pre_B12",
                "post_B04",
                "post_B8A",
                "post_B12",
            ],
            "input_channel_count": 6,
            "input_shape": [6, 64, 64],
            "input_dtype": "float32",
            "source_resolution_m": 20,
            "local_resampling": "none",
            "normalization": "frozen per-channel train-only mean/std",
            "target_shape": [1, 64, 64],
            "target_classes": {"background": 0, "burned": 1},
            "excluded_states": {"unknown": 2, "nodata": 255},
            "loss_and_metric_mask": (
                "exact dataset loss mask; unknown, nodata, and invalid pixels "
                "never contribute"
            ),
            "train_patch_count": dataset["inventory"]["patches_by_role"]["train"],
            "validation_patch_count": dataset["inventory"]["patches_by_role"][
                "validation"
            ],
            "test_patch_count": dataset["inventory"]["patches_by_role"]["test"],
            "batch_order": "canonical manifest order",
            "augmentation": "none",
            "shuffle": False,
        },
        "architecture": {
            "family": "U-Net-style binary semantic segmentation",
            "model_version_candidate": "burnlens-unet-binary-v0.1.0",
            "encoder_channels": [16, 32],
            "bottleneck_channels": 64,
            "decoder_channels": [32, 16],
            "convolution_blocks": (
                "two 3x3 stride-1 padding-1 convolutions with ReLU per block"
            ),
            "downsampling": "2x2 max pooling",
            "upsampling": "2x2 transposed convolution with skip concatenation",
            "output_head": "1x1 convolution to one logit channel",
            "batch_normalization": False,
            "dropout": False,
            "pretrained_weights": False,
            "model_count": 1,
        },
        "optimization": {
            "framework": "torch==2.13.0",
            "python": "CPython 3.12.10",
            "device": "cpu",
            "dtype": "float32",
            "seed": 20260725,
            "seed_python": True,
            "seed_numpy": True,
            "seed_torch": True,
            "deterministic_algorithms": True,
            "deterministic_warn_only": False,
            "loss": "BCEWithLogitsLoss(reduction='none')",
            "loss_reduction": "mean over exact loss-mask pixels only",
            "positive_class_weight": None,
            "optimizer": "Adam",
            "learning_rate": 0.001,
            "weight_decay": 0.0,
            "batch_size": 4,
            "maximum_epochs": 200,
            "early_stopping_patience": 25,
            "early_stopping_min_delta": 0.000001,
            "gradient_clipping": None,
            "mixed_precision": False,
        },
        "checkpoint_selection": {
            "probability_threshold": 0.5,
            "primary": "maximize validation event-class macro Dice",
            "tie_break_1": "maximize validation event-class macro IoU",
            "tie_break_2": "minimize validation masked BCE",
            "tie_break_3": "earliest epoch",
            "test_access": (
                "one model-evaluation opening only after code, environment, "
                "weights checkpoint, and selection are frozen"
            ),
            "post_test_changes": "none; any change requires a new model version and leaves the original result immutable",
        },
        "evaluation": {
            "primary_metrics": [
                "event-class macro Dice",
                "event-class macro IoU",
                "worst-event macro Dice",
            ],
            "required_breakdowns": [
                "event",
                "class",
                "support",
                "TP",
                "FP",
                "FN",
                "Dice denominator",
                "IoU denominator",
            ],
            "strongest_baseline": {
                "family": baseline["selected"]["family_id"],
                "test_event_class_macro_dice": baseline[
                    "selected_test_metrics"
                ]["event_class_macro_dice"],
                "test_event_class_macro_iou": baseline[
                    "selected_test_metrics"
                ]["event_class_macro_iou"],
                "test_core_pixels": baseline["selected_test_metrics"][
                    "core_pixels"
                ],
            },
            "analytical_winner_rule": (
                "The model must exceed the RBR baseline on event-class macro "
                "Dice and not be lower on event-class macro IoU or worst-event "
                "macro Dice. Because the baseline is already 1.0 on all three, "
                "the model cannot become the analytical winner on this frozen "
                "test metric."
            ),
            "matching_rule": (
                "Matching the baseline is a valid trained-model result but does "
                "not establish added value, generalization, or model superiority."
            ),
            "rejection_rule": (
                "A lower, invalid, contaminated, nonfinite, or irreproducible "
                "result rejects the model as the analytical winner; the baseline "
                "remains the accepted method."
            ),
        },
        "reproducibility_gates": {
            "dependency_gate": (
                "add torch 2.13.0 to the appropriate profile, resolve with "
                "setuptools 82.0.0, lock, uv sync --locked, pip check, audit, "
                "and isolated setup smoke test"
            ),
            "environment_capture": [
                "uv.lock SHA-256",
                "Python version",
                "torch version and build",
                "CPU identity",
                "thread settings",
                "torch configuration",
            ],
            "finite_checks": [
                "normalized inputs",
                "logits",
                "unreduced loss",
                "masked loss",
                "gradients",
                "weights",
                "probabilities",
            ],
            "replay": (
                "repeat the complete training and evaluation on the same locked "
                "CPU environment; require identical selected epoch, weights "
                "SHA-256, predictions, and metrics"
            ),
            "cross_platform_claim": False,
        },
        "stop_conditions": [
            "locked dependency resolution or isolated setup fails",
            "exact dataset, split, normalization, or baseline binding drifts",
            "any train/validation/test event or patch crosses roles",
            "unknown, nodata, or invalid pixels enter loss or metrics",
            "test data influences architecture, hyperparameters, stopping, or checkpoint selection",
            "any required tensor, loss, gradient, weight, probability, or metric is nonfinite",
            "same-environment replay differs",
            "a result cannot be rendered and inspected",
            "a claim exceeds the evidence or established use boundaries",
        ],
        "required_outputs": [
            "locked environment and dependency evidence",
            "architecture/config manifest",
            "training history and selected-checkpoint record",
            "weights with exact byte count and SHA-256",
            "model card",
            "train/validation diagnostics",
            "single frozen-test evaluation against RBR",
            "event/class denominator table",
            "inspectable error and prediction renders",
            "same-environment exact replay",
            "explicit model-accepted or model-rejected decision",
        ],
        "limitations": [
            WARNING,
            "Only four train patches and two train events exist.",
            "The 89-core test set is selected prototype evidence, not natural prevalence.",
            "Candidate construction used optical and official-reference evidence and may favor spectral separability.",
            "The RBR baseline already reaches the metric ceiling on the frozen test cores.",
            "The experiment can satisfy the requirement to build, train, and evaluate a U-Net while still rejecting it as the analytical winner.",
        ],
        "next_dependency": (
            "P2O5-T03-U07 verified milestone release, followed by a separate "
            "issue-backed Phase Three training/evaluation checkpoint"
        ),
    }


def audit(
    root: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    bindings, values = _load_inputs(root)
    dataset = values["dataset_manifest"]
    split = values["split_manifest"]
    qa = values["dataset_qa"]
    normalization = values["normalization"]
    selection = values["baseline_selection"]
    baseline = values["baseline_evaluation"]
    tooling = values["tooling_sources"]

    gates = {
        "exact_package_identity": _require(
            dataset["dataset_version"] == "burnlens-dataset-v0.1.0"
            and split["split_version"]
            == "burnlens-whole-event-split-v0.1.0",
            "exact dataset and whole-event split identities match",
        ),
        "dataset_scope": _require(
            dataset["inventory"]["event_groups"] == 6
            and dataset["inventory"]["patches"] == 12
            and dataset["inventory"]["accepted_core_pixels"] == 287
            and dataset["inventory"]["source_unknown_ring_pixels"] == 531,
            "six events, twelve patches, 287 cores, and 531 unknown-ring pixels match",
        ),
        "whole_event_split": _require(
            split["boundaries"]["split_locked"] is True
            and dataset["inventory"]["patches_by_role"]
            == {"test": 4, "train": 4, "validation": 4},
            "locked whole-event 4/4/4 patch split remains exact",
        ),
        "independent_dataset_qa": _require(
            qa["decision"]
            == "PASS_INDEPENDENT_DATASET_QA_AUTHORIZE_BASELINE_PREREGISTRATION_ONLY"
            and qa["boundaries"]["dataset_qa_passed"] is True,
            "independent dataset QA passed",
        ),
        "train_only_normalization": _require(
            normalization["validation_pixels_used"] is False
            and normalization["test_pixels_used"] is False
            and normalization["boundaries"]["training_authorized"] is False,
            "normalization is owned by training events only",
        ),
        "baseline_selection_integrity": _require(
            selection["selected"]["family_id"] == "rbr-threshold"
            and selection["boundaries"]["test_pixels_read"] is False
            and selection["boundaries"]["selection_frozen"] is True,
            "RBR selection was frozen from train and validation before test",
        ),
        "single_baseline_test_open": _require(
            baseline["decision"]
            == "PASS_REPRODUCIBLE_NON_MODEL_BASELINE_EVALUATION"
            and baseline["boundaries"]["test_analytical_open_count_after"] == 1
            and baseline["boundaries"]["test_tuning"] is False
            and baseline["boundaries"]["selection_changed_after_test"] is False,
            "baseline test opening is single, frozen, and untuned",
        ),
        "baseline_ceiling_visible": _require(
            baseline["selected_test_metrics"]["event_class_macro_dice"] == 1.0
            and baseline["selected_test_metrics"]["event_class_macro_iou"] == 1.0
            and baseline["selected_test_metrics"]["worst_event_macro_dice"]
            == 1.0,
            "RBR reaches the frozen selected-core metric ceiling and cannot be numerically exceeded",
        ),
        "tooling_feasibility": _require(
            tooling["local_feasibility_probe"]["result"] == "pass"
            and tooling["local_feasibility_probe"][
                "installed_packages_changed"
            ]
            is False
            and tooling["local_compute_observation"]["selected_device"] == "cpu"
            and not any(tooling["stop_conditions"].values()),
            "official tooling research and local CPU-only dry-run pass without installation",
        ),
    }
    contract = training_contract(
        bindings, values, generated_at_utc, run_id, git_source_commit
    )
    decision = {
        "decision_version": "burnlens-model-readiness-decision-v0.1.0",
        "decision_id": DECISION_ID,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": TASK_ISSUE,
        "unit_id": UNIT_ID,
        "git_source_commit": git_source_commit,
        "decision": "AUTHORIZE_BOUNDED_UNET",
        "qualifier": "REJECTION_FIRST_SINGLE_MODEL_EXPERIMENT",
        "training_authorized": True,
        "authorization_effective_after": (
            "P2O5-T03-U07 milestone release is merged, tagged, and verified"
        ),
        "training_contract_id": CONTRACT_ID,
        "rationale": [
            "All exact Phase Two dataset, split, QA, normalization, and baseline gates pass.",
            "The selected U-Net family fits the established binary mask-first CV task.",
            "A compatible CPU-only PyTorch resolution exists within the locked Python and setuptools constraints.",
            "The experiment is bounded to one model and can honestly reject the model if it does not add value.",
            "The strongest RBR baseline already reaches 1.0 on every frozen primary test metric, so the model cannot be claimed as the analytical winner on this evidence.",
        ],
        "claims": {
            "phase_two_package_ready_for_bounded_training": True,
            "model_exists": False,
            "model_trained": False,
            "model_evaluated": False,
            "model_adds_value": False,
            "generalization": False,
            "independent_validation": False,
            "field_validation": False,
            "operational_readiness": False,
            "final_submission_ready": False,
        },
        "fallback_if_phase_three_fails": (
            "retain RBR as the accepted analytical method, preserve the trained "
            "U-Net as an honestly rejected experiment if its run is valid, and "
            "do not advance model-value claims"
        ),
        "next_dependency": contract["next_dependency"],
    }
    audit_report = {
        "audit_version": AUDIT_VERSION,
        "audit_id": AUDIT_ID,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": TASK_ISSUE,
        "unit_id": UNIT_ID,
        "git_source_commit": git_source_commit,
        "software_version": __version__,
        "inputs": bindings,
        "gates": gates,
        "evidence_summary": {
            "dataset_version": dataset["dataset_version"],
            "split_version": split["split_version"],
            "event_groups": dataset["inventory"]["event_groups"],
            "patches_by_role": dataset["inventory"]["patches_by_role"],
            "accepted_core_pixels": dataset["inventory"][
                "accepted_core_pixels"
            ],
            "unknown_ring_pixels": dataset["inventory"][
                "source_unknown_ring_pixels"
            ],
            "strongest_baseline": baseline["selected"]["family_id"],
            "baseline_test_event_class_macro_dice": baseline[
                "selected_test_metrics"
            ]["event_class_macro_dice"],
            "baseline_test_event_class_macro_iou": baseline[
                "selected_test_metrics"
            ]["event_class_macro_iou"],
            "baseline_test_core_pixels": baseline["selected_test_metrics"][
                "core_pixels"
            ],
            "baseline_test_analytical_open_count": baseline["boundaries"][
                "test_analytical_open_count_after"
            ],
            "model_count": 0,
            "training_run_count": 0,
        },
        "portfolio_and_schedule": {
            "portfolio_promise": (
                "trained binary segmentation model in a reproducible "
                "imagery-to-GEOINT workflow"
            ),
            "deadline": DEADLINE,
            "days_remaining_at_audit": _days_to_deadline(generated_at_utc),
            "status": "aggressive; model and GEOINT outputs do not yet exist",
            "critical_path": [
                "verified U07 Phase Two release",
                "locked Phase Three environment and model implementation",
                "single U-Net training and exact replay",
                "frozen-test evaluation against RBR",
                "honest model acceptance or rejection",
                "smallest georeferenced inference-to-overlay vertical slice",
                "repository-owned application, case study, and release QA",
            ],
        },
        "decision": decision["decision"],
        "decision_qualifier": decision["qualifier"],
        "training_contract_id": CONTRACT_ID,
        "limitations": contract["limitations"],
        "boundaries": {
            "all_gates_passed": True,
            "test_analytical_open_count": 1,
            "model_created": False,
            "model_trained": False,
            "metric_result_created": True,
            "training_authorized": True,
            "deployment_authorized": False,
            "final_submission_ready": False,
        },
        "next_dependency": contract["next_dependency"],
        "warning": WARNING,
    }
    return audit_report, decision, contract


def render_html(
    report: dict[str, Any], decision: dict[str, Any], image_name: str
) -> str:
    summary = report["evidence_summary"]
    gates = "".join(
        "<tr><td>{}</td><td><span class='pass'>PASS</span></td><td>{}</td></tr>".format(
            escape(name.replace("_", " ").title()),
            escape(gate["finding"]),
        )
        for name, gate in report["gates"].items()
    )
    limitations = "".join(
        f"<li>{escape(item)}</li>" for item in report["limitations"]
    )
    rationale = "".join(
        f"<li>{escape(item)}</li>" for item in decision["rationale"]
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>BurnLens model-readiness decision</title>
<style>
:root{{--ink:#17201d;--muted:#58635f;--paper:#f3efe5;--card:#fffdf8;--green:#175b47;--gold:#b87920;--line:#d7d0c2}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.5 system-ui,sans-serif}}
main{{max-width:1120px;margin:auto;padding:28px}}h1{{font-size:clamp(2rem,6vw,4.5rem);line-height:.95;margin:.25rem 0 1rem}}
h2{{margin-top:0}}.eyebrow{{font-weight:800;letter-spacing:.1em;text-transform:uppercase;color:var(--green)}}
.grid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin:22px 0}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:20px;min-width:0}}
.decision{{border-left:8px solid var(--green)}}.metric{{font-size:2rem;font-weight:850}}.muted{{color:var(--muted)}}
.pass{{display:inline-block;background:#dcefe6;color:#104a39;border-radius:999px;padding:.1rem .55rem;font-weight:800}}
.table-wrap{{overflow-x:auto}}table{{width:100%;border-collapse:collapse;min-width:720px}}th,td{{padding:10px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}
img{{display:block;width:100%;height:auto;border:1px solid var(--line);border-radius:10px;background:#fff}}
code{{overflow-wrap:anywhere}}footer{{margin-top:22px;color:var(--muted);font-size:.9rem}}
@media(max-width:760px){{main{{padding:18px}}.grid{{grid-template-columns:1fr}}h1{{font-size:2.4rem}}.metric{{font-size:1.7rem}}}}
</style>
</head>
<body><main>
<p class="eyebrow">P2O5-T03 · U06 · Phase Two</p>
<h1>Bounded U-Net authorized.<br>The baseline still leads.</h1>
<section class="card decision">
<h2>{escape(decision["decision"])}</h2>
<p><strong>{escape(decision["qualifier"])}</strong></p>
<p>One CPU-only model experiment may start only after the U07 release is merged, tagged, and verified. The experiment is designed to produce a valid trained-model evaluation and to reject the model honestly if it does not beat the transparent baseline.</p>
<p><strong>No model-value, generalization, or final-readiness claim is authorized.</strong></p>
</section>
<section class="grid">
<div class="card"><div class="metric">{summary["event_groups"]} events</div><div class="muted">whole-event 2 / 2 / 2 split</div></div>
<div class="card"><div class="metric">{summary["accepted_core_pixels"]} cores</div><div class="muted">{summary["unknown_ring_pixels"]} unknown-ring pixels excluded</div></div>
<div class="card"><div class="metric">RBR {summary["baseline_test_event_class_macro_dice"]:.3f}</div><div class="muted">Dice and IoU on {summary["baseline_test_core_pixels"]} selected test cores</div></div>
</section>
<section class="card"><h2>Why proceed</h2><ul>{rationale}</ul></section>
<section class="card"><h2>Exact readiness gates</h2><div class="table-wrap"><table><thead><tr><th>Gate</th><th>State</th><th>Finding</th></tr></thead><tbody>{gates}</tbody></table></div></section>
<section class="card"><h2>Frozen experiment</h2>
<img src="{escape(image_name)}" alt="Bounded U-Net training contract diagram">
<p>The test already served one frozen baseline evaluation. It may not tune the model. Model checkpoint selection is validation-only, followed by one final model evaluation against the unchanged RBR result.</p>
</section>
<section class="card"><h2>Limits that control the claim</h2><ul>{limitations}</ul></section>
<footer>
Run <code>{escape(report["run_id"])}</code> · source <code>{escape(report["git_source_commit"])}</code> · contract <code>{CONTRACT_ID}</code><br>
{escape(WARNING)}
</footer>
</main></body></html>
"""


def render_contract_png(contract: dict[str, Any], path: Path) -> None:
    image = Image.new("RGB", (1800, 1040), "#f3efe5")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default(size=28)
    small = ImageFont.load_default(size=21)
    draw.text((70, 55), "ONE BOUNDED U-NET EXPERIMENT", fill="#175b47", font=font)
    draw.text(
        (70, 105),
        "train 4 patches  ->  validate 4 patches  ->  evaluate 4 patches once",
        fill="#17201d",
        font=font,
    )
    cards = [
        (
            70,
            "INPUT",
            [
                "6 x 64 x 64 float32",
                "pre/post B04, B8A, B12",
                "train-only normalization",
                "unknown/nodata masked",
            ],
        ),
        (
            625,
            "MODEL",
            [
                "U-Net 16 / 32 / 64",
                "one logit per pixel",
                "CPU, seed 20260725",
                "no search or augmentation",
            ],
        ),
        (
            1180,
            "DECISION",
            [
                "compare with RBR = 1.000",
                "matching is not added value",
                "lower means model rejected",
                "baseline remains accepted",
            ],
        ),
    ]
    for x, title, lines in cards:
        draw.rounded_rectangle(
            (x, 210, x + 500, 650),
            radius=24,
            fill="#fffdf8",
            outline="#d7d0c2",
            width=3,
        )
        draw.text((x + 35, 245), title, fill="#b87920", font=font)
        y = 325
        for line in lines:
            draw.text((x + 35, y), f"• {line}", fill="#17201d", font=small)
            y += 65
    draw.line((570, 430, 625, 430), fill="#175b47", width=8)
    draw.polygon([(625, 430), (595, 412), (595, 448)], fill="#175b47")
    draw.line((1125, 430, 1180, 430), fill="#175b47", width=8)
    draw.polygon([(1180, 430), (1150, 412), (1150, 448)], fill="#175b47")
    draw.rounded_rectangle(
        (70, 720, 1680, 940),
        radius=24,
        fill="#17201d",
    )
    draw.text(
        (110, 760),
        "AUTHORIZATION IS REJECTION-FIRST",
        fill="#f3efe5",
        font=font,
    )
    draw.text(
        (110, 820),
        "A valid trained model may still lose. No model-value or generalization claim follows from training.",
        fill="#f3efe5",
        font=small,
    )
    draw.text(
        (110, 870),
        f"Contract: {contract['training_contract_id']}  |  CPU-only  |  PyTorch 2.13.0",
        fill="#c8ded5",
        font=small,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, optimize=False)


def write_outputs(
    repository_root: Path,
    output_directory: Path,
    readiness_directory: Path,
    contract_path: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, Path]:
    report, decision, contract = audit(
        repository_root, generated_at_utc, run_id, git_source_commit
    )
    output_directory.mkdir(parents=True, exist_ok=True)
    readiness_directory.mkdir(parents=True, exist_ok=True)
    contract_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path = readiness_directory / f"{AUDIT_ID}.json"
    decision_path = readiness_directory / f"{DECISION_ID}.json"
    html_path = output_directory / f"{DECISION_ID}.html"
    image_path = output_directory / f"{DECISION_ID}.png"
    audit_path.write_bytes(_json_bytes(report))
    decision_path.write_bytes(_json_bytes(decision))
    contract_path.write_bytes(_json_bytes(contract))
    render_contract_png(contract, image_path)
    html_path.write_text(
        render_html(report, decision, image_path.name),
        encoding="utf-8",
        newline="\n",
    )
    return {
        "audit": audit_path,
        "decision": decision_path,
        "contract": contract_path,
        "html": html_path,
        "png": image_path,
    }
