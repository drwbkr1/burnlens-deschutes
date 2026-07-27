"""Fail-closed loader for the Phase Five reliability milestone contract."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Mapping


CONTRACT_PATH = Path(
    "records/phase-five/contracts/"
    "PHASE-FIVE-QA-RELEASE-CONTRACT-2026-001.json"
)
CONTRACT_VERSION = "burnlens-phase-five-qa-release-contract-v0.1.0"
CONTRACT_ID = "PHASE-FIVE-QA-RELEASE-CONTRACT-2026-001"
MILESTONE_ID = "P5O1-T01"
BASE_COMMIT = "3c0ec9ef893b0e610c6c38c70a191e5e67c09ca9"
ISSUE = 574
ROUTE = "baseline-primary-with-rejected-model-diagnostic"
ACCEPTED_METHOD = "burnlens-baseline-v0.1.0"
REJECTED_MODEL = "burnlens-unet-binary-v0.1.0"
UNITS = [f"P5O1-T01-U{number:02d}" for number in range(1, 7)]
INJECTION_IDS = {
    "missing-required-member",
    "corrupt-required-member",
    "archive-path-traversal",
    "binding-mismatch",
    "partial-package",
}
ACCESSIBILITY_CRITERIA = {
    "keyboard-operable",
    "no-keyboard-trap",
    "focus-order",
    "focus-visible",
    "focus-not-obscured",
    "non-color-communication",
    "text-equivalent",
    "reflow-zoom",
    "reduced-motion",
    "name-role-value",
}
RESEARCH_AUTHORITIES = {"W3C", "OWASP", "CISA"}


class PhaseFiveContractError(RuntimeError):
    """The tracked Phase Five contract or frozen release input has drifted."""


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(8 * 1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise PhaseFiveContractError(message)


def validate_contract(
    contract: Mapping[str, Any],
    *,
    repository_root: Path,
) -> dict[str, Any]:
    """Validate frozen inputs, QA semantics, budgets, and project boundaries."""

    root = repository_root.resolve()
    _require(
        contract.get("contract_version") == CONTRACT_VERSION,
        "contract version drift",
    )
    _require(contract.get("contract_id") == CONTRACT_ID, "contract id drift")
    _require(contract.get("milestone_id") == MILESTONE_ID, "milestone id drift")
    _require(contract.get("issue") == ISSUE, "issue binding drift")
    _require(contract.get("exact_branch_base") == BASE_COMMIT, "base drift")
    _require(contract.get("route") == ROUTE, "analytical route drift")

    analytical = contract.get("analytical_posture", {})
    _require(
        analytical.get("accepted_method") == ACCEPTED_METHOD,
        "accepted method drift",
    )
    _require(
        analytical.get("rejected_diagnostic_model") == REJECTED_MODEL,
        "rejected model drift",
    )
    _require(
        analytical.get("rejected_model_accepted") is False,
        "rejected model cannot be accepted",
    )
    _require(
        analytical.get("rejected_model_outperformed_rbr") is False,
        "model-superiority claim is prohibited",
    )

    bindings = contract.get("frozen_release_bindings", [])
    _require(isinstance(bindings, list) and len(bindings) >= 7, "bindings absent")
    for binding in bindings:
        relative = binding.get("path")
        _require(isinstance(relative, str) and relative, "binding path absent")
        path = root / relative
        _require(path.is_file(), f"frozen release input absent: {relative}")
        _require(
            path.stat().st_size == binding.get("bytes"),
            f"frozen release input size drift: {relative}",
        )
        _require(
            _sha256_file(path) == binding.get("sha256"),
            f"frozen release input hash drift: {relative}",
        )

    units = contract.get("evidence_units", [])
    _require(
        [unit.get("unit_id") for unit in units] == UNITS,
        "evidence unit roster drift",
    )
    _require(
        units[0].get("dependencies") == [],
        "U01 must have no milestone-unit dependency",
    )
    for index, unit in enumerate(units[1:], start=1):
        _require(
            unit.get("dependencies") == [UNITS[index - 1]],
            f"{unit.get('unit_id')} dependency drift",
        )

    failure_standard = contract.get("failure_injection_standard", {})
    injections = failure_standard.get("required_injections", [])
    _require(
        {item.get("injection_id") for item in injections} == INJECTION_IDS,
        "failure injection roster drift",
    )
    _require(
        failure_standard.get("canonical_bytes_must_not_change") is True,
        "canonical byte immutability is required",
    )
    _require(
        failure_standard.get("silent_acceptance_prohibited") is True,
        "silent acceptance must be prohibited",
    )

    accessibility = contract.get("accessibility_standard", {})
    _require(
        set(accessibility.get("criteria", [])) == ACCESSIBILITY_CRITERIA,
        "accessibility criteria drift",
    )
    _require(
        accessibility.get("target") == "WCAG-2.2-AA-bounded-review",
        "accessibility target drift",
    )
    _require(
        accessibility.get("automation_file_url_block_retained") is True,
        "browser automation limitation must remain visible",
    )
    _require(
        accessibility.get("browser_policy_bypass_prohibited") is True,
        "browser policy bypass must remain prohibited",
    )

    budgets = contract.get("performance_budgets", {})
    _require(budgets.get("zip_bytes_max") == 750_000, "ZIP budget drift")
    _require(
        budgets.get("extracted_bytes_max") == 2_500_000,
        "extracted package budget drift",
    )
    _require(
        budgets.get("interface_html_bytes_max") == 250_000,
        "interface budget drift",
    )
    _require(
        budgets.get("external_runtime_requests_max") == 0,
        "offline request budget drift",
    )
    _require(
        budgets.get("package_validation_seconds_max") == 5.0,
        "validation runtime budget drift",
    )

    severity = contract.get("defect_severity", {})
    _require(
        set(severity) == {"critical", "high", "medium", "low"},
        "severity taxonomy drift",
    )
    _require(
        severity["critical"]["phase_six_effect"] == "block",
        "critical defects must block Phase Six",
    )
    _require(
        severity["high"]["phase_six_effect"] == "block-or-remove-scope",
        "high defect treatment drift",
    )

    research = contract.get("research_basis", [])
    _require(
        {item.get("authority") for item in research} == RESEARCH_AUTHORITIES,
        "research authority roster drift",
    )
    for item in research:
        _require(item.get("checked_at_utc") == "2026-07-26", "research date drift")
        _require(
            str(item.get("url", "")).startswith("https://"),
            "research source must use HTTPS",
        )

    boundaries = contract.get("boundaries", {})
    for key in (
        "retraining",
        "retuning",
        "dataset_changed",
        "split_changed",
        "label_changed",
        "aoi_changed",
        "threshold_changed",
        "phase_3b_created",
        "second_experiment_planned",
        "second_experiment_implemented",
        "model_superiority_claim",
        "operational_claim",
        "field_validation_claim",
        "official_or_endorsed_claim",
        "public_sharing_change",
        "burnlens_site_used",
    ):
        _require(boundaries.get(key) is False, f"prohibited boundary enabled: {key}")

    return dict(contract)


def load_contract(repository_root: Path) -> dict[str, Any]:
    """Load and validate the exact tracked Phase Five contract."""

    path = repository_root.resolve() / CONTRACT_PATH
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PhaseFiveContractError(f"invalid contract JSON: {path}") from exc
    _require(isinstance(value, dict), "contract must be a JSON object")
    return validate_contract(value, repository_root=repository_root)
