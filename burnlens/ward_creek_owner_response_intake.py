"""Fail-closed Ward Creek owner-response reconciliation."""

from __future__ import annotations

from collections import Counter
from datetime import datetime
from hashlib import sha256
from html import escape
import json
import os
from pathlib import Path
import subprocess
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import rasterio

import burnlens
from .optical_pair_evidence import _font
from .owner_review_batch import build_surface, validate_completed_response
from .owner_review_batch_lock import LOCK_VERSION
from .ward_creek_owner_review_surface import (
    EVENT_GROUP_ID as REVIEW_EVENT_GROUP_ID,
    EXPECTED_CANDIDATES,
    SURFACE_ID,
)
from .ward_creek_region_proposal import (
    EXPECTED_ROUTE_COUNTS,
    LABEL_SCHEMA_VERSION,
    REPORT_ID as PROPOSAL_ID,
    RUN_ID as PROPOSAL_RUN_ID,
    TARGET_VERSION,
    build_report as rebuild_proposal,
)


REPORT_ID = "WARD-CREEK-OWNER-RESPONSE-INTAKE-2026-001"
REPORT_VERSION = "ward-creek-owner-response-intake-v0.1.0"
PRIVATE_REPORT_VERSION = "ward-creek-owner-response-private-reconciliation-v0.1.0"
LABEL_SET_VERSION = "owner-approved-prototype-region-labels-v0.5.0"
PRIOR_LABEL_SET_VERSION = "owner-approved-prototype-region-labels-v0.4.0"
AOI_VERSION = "multi-event-native-grids-v0.5.0"
TASK_ISSUE = 554
UNIT_ID = "P2O4-T39-U07"
EXPECTED_EVENT_GROUP_ID = "event-ward-creek-2019"
EXPECTED_SURFACE_BYTES = 14_344
EXPECTED_SURFACE_SHA256 = "416b36127015820285c0dfd53592b6391530a6a610f532589a68ef06dc0ba57e"
EXPECTED_PROPOSAL_BYTES = 8_433
EXPECTED_PROPOSAL_SHA256 = "06100de3df058b397f3a797069a2705eea3d7f79c71dfa333a11698331b13638"
EXPECTED_RESPONSE_BYTES = 1_041
EXPECTED_RESPONSE_SHA256 = "aadd221da037ab7fc89bd04fb4532651b917190ac55e97ee7f4d5ce4eb951dbc"
EXPECTED_RECEIPT_BYTES = 2_692
EXPECTED_RECEIPT_SHA256 = "dba7d81aa21dde09b21d549dba7440363906ab3cebfb4d14e958588fb2efc4bf"
PRIOR_INTAKE_BYTES = 6_787
PRIOR_INTAKE_SHA256 = "f948b69c20fe02a166c51a4856e319860a2d0c112922a5bbfef6f002717da2f7"
EXPECTED_CORE_PIXELS = {"WCP-001": 14, "WCP-002": 25}
EXPECTED_RING_PIXELS = {"WCP-001": 26, "WCP-002": 40}
RECORD_BINDINGS = {
    "SOURCE-2026-038": (5_103, "239192c10e16f69ed6218c8e8766ba2a79826618095c30b6ab5561cbaed740c3"),
    "TERMS-2026-033": (4_058, "e8f55e33c67edad1462676812ec20663e96e239e45fa908ef13c33571fede268"),
    "PRECHECK-2026-073": (5_322, "9bac466cdeeb9c11067ac3e4cd3ddf7a549bd16d07242715af6a7e40912496cb"),
    "PRECHECK-2026-074": (5_117, "f1b23a223937de6049d6df9766c93d97073f8d810a35788a523ba5c7349a88cd"),
    "PRECHECK-2026-076": (2_315, "f87ee52b14ffb757148e98b79014e0b356a735aefa3475fc6ee499d7f5eb9393"),
    "PRECHECK-2026-078": (1_841, "761999c941ad079f7677f1e53cc0624495c3db0f5c5f873c6aca31715c61ed5b"),
    "PRECHECK-2026-079": (3_879, "2920b3fd816df19c7e00671d695ad99441d615b2614fda261d287b03cca6708d"),
    "PRECHECK-2026-080": (4_129, "9964b9f4f2b1733bfc826b51dd30bdd5fe88e19b626be9b8d35efb54feba9b2c"),
    "PRECHECK-2026-081": (2_294, "057355ae3939cbe08403b9002faf3797220a250d4339ea122fc2c40b2872e865"),
    "PRECHECK-2026-082": (4_893, "ced071f5188c7e856719b1b2f299d531d4e102ddb4b9e47e8e456f67f21072e6"),
    "PRECHECK-2026-083": (3_950, "31e3796fba82abb459b7d1aece17e4b2558d89fa915d21f5f6c8d199e72cb56f"),
    "PRECHECK-2026-084": (2_278, "3da9ef5bfcadc5f09c8b9765695968ed42689ae40c203d3802aabfc9303ad01e"),
}
REQUIRED_RECORD_TEXT = {
    "SOURCE-2026-038": ("Ward Creek", "Disposition", "pass"),
    "TERMS-2026-033": ("Ward Creek", "Sentinel", "MTBS"),
    "PRECHECK-2026-073": ("P2O4-T39-U01", "Disposition", "pass"),
    "PRECHECK-2026-074": ("P2O4-T39-U02", "Disposition", "pass"),
    "PRECHECK-2026-076": ("P2O4-T39-U03", "custody-pass-source-fitness-pending"),
    "PRECHECK-2026-078": ("P2O4-T39-U03", "failed-retained"),
    "PRECHECK-2026-079": ("P2O4-T39-U03", "Disposition", "pass"),
    "PRECHECK-2026-080": ("P2O4-T39-U04", "machine-pass-render-pending"),
    "PRECHECK-2026-081": ("P2O4-T39-U04", "Disposition", "pass"),
    "PRECHECK-2026-082": ("P2O4-T39-U05", "Disposition", "pass"),
    "PRECHECK-2026-083": ("P2O4-T39-U06", "prepare-pass-owner-response-pending"),
    "PRECHECK-2026-084": ("P2O4-T39-U06", "pass-decisions-unrevealed"),
}
WARNING = (
    "Experimental owner-approved prototype regions, not ground truth, a dataset, "
    "official wildfire information, emergency guidance, or field validation. "
    "Official sources govern."
)
EVIDENCE_ORIGIN = "owner-returned-batch-response"


class WardCreekOwnerResponseIntakeError(RuntimeError):
    """Raised when response custody or any promotion gate fails closed."""


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise WardCreekOwnerResponseIntakeError(message)


def _sha256_bytes(data: bytes) -> str:
    return sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _binding(path: Path, **extra: Any) -> dict[str, Any]:
    value = {"bytes": path.stat().st_size, "sha256": _sha256_file(path)}
    value.update(extra)
    return value


def _json(data: bytes, name: str) -> dict[str, Any]:
    try:
        value = json.loads(data.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise WardCreekOwnerResponseIntakeError(
            f"invalid UTF-8 JSON: {name}"
        ) from error
    _assert(isinstance(value, dict), f"JSON is not an object: {name}")
    return value


def _timestamp(value: Any, name: str) -> datetime:
    _assert(isinstance(value, str), f"{name} is not a timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise WardCreekOwnerResponseIntakeError(f"{name} is invalid") from error
    _assert(parsed.tzinfo is not None, f"{name} lacks timezone")
    return parsed


def _assert_ignored(repository_root: Path, path: Path) -> None:
    try:
        relative = path.relative_to(repository_root)
    except ValueError as error:
        raise WardCreekOwnerResponseIntakeError(
            "private input or output is outside the repository"
        ) from error
    result = subprocess.run(
        [
            "git",
            "-C",
            str(repository_root),
            "check-ignore",
            "--quiet",
            "--no-index",
            "--",
            str(relative),
        ],
        check=False,
    )
    _assert(result.returncode == 0, "private input or output is not ignored")


def _record_path(repository_root: Path, record_id: str) -> Path:
    if record_id.startswith("SOURCE-"):
        root = repository_root / "records/phase-two/sources"
    elif record_id.startswith("TERMS-"):
        root = repository_root / "records/phase-two/terms"
    else:
        root = repository_root / "records/phase-two/prechecks"
    matches = list(root.glob(f"{record_id}.*"))
    _assert(
        len(matches) == 1 and matches[0].is_file(),
        f"record missing or ambiguous: {record_id}",
    )
    return matches[0]


def _record_bindings(repository_root: Path) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for record_id, (expected_bytes, expected_sha256) in RECORD_BINDINGS.items():
        path = _record_path(repository_root, record_id)
        text = path.read_text(encoding="utf-8")
        for required in REQUIRED_RECORD_TEXT[record_id]:
            _assert(required in text, f"required gate text changed: {record_id}")
        binding = _binding(path)
        _assert(binding["bytes"] == expected_bytes, f"record size changed: {record_id}")
        _assert(
            binding["sha256"] == expected_sha256,
            f"record hash changed: {record_id}",
        )
        result.append({"record_id": record_id, **binding})
    return result


def _validate_surface(path: Path) -> tuple[dict[str, Any], bytes]:
    data = path.read_bytes()
    _assert(len(data) == EXPECTED_SURFACE_BYTES, "surface size changed")
    _assert(_sha256_bytes(data) == EXPECTED_SURFACE_SHA256, "surface hash changed")
    surface = _json(data, path.name)
    try:
        rebuilt = build_surface(surface.get("batch_manifest"))
    except Exception as error:
        raise WardCreekOwnerResponseIntakeError(
            "surface reconstruction failed"
        ) from error
    rebuilt["software_version"] = surface.get("software_version")
    _assert(
        all(surface.get(key) == value for key, value in rebuilt.items()),
        "surface reconstruction changed",
    )
    _assert(surface.get("report_id") == SURFACE_ID, "surface identity changed")
    _assert(surface.get("task_issue") == TASK_ISSUE, "surface issue changed")
    _assert(
        surface.get("summary", {}).get("owner_responses") == 0,
        "surface already contains responses",
    )
    _assert(
        surface.get("summary", {}).get("labels_created") == 0,
        "surface already contains labels",
    )
    return surface, data


def _validate_receipt(
    receipt: dict[str, Any],
    *,
    response_bytes: bytes,
    surface_bytes: bytes,
) -> None:
    _assert(
        receipt.get("report_id") == f"{SURFACE_ID}-RECEIPT",
        "receipt identity changed",
    )
    _assert(receipt.get("report_version") == LOCK_VERSION, "receipt version changed")
    _assert(receipt.get("task_issue") == TASK_ISSUE, "receipt issue changed")
    _assert(
        receipt.get("evidence_origin") == EVIDENCE_ORIGIN,
        "receipt origin changed",
    )
    _assert(
        receipt.get("origin_declared_by_operator") is True,
        "receipt origin declaration changed",
    )
    _assert(
        receipt.get("exact_response_preserved_without_overwrite") is True,
        "receipt lacks no-overwrite custody",
    )
    _assert(
        receipt.get("decisions_revealed") is False,
        "receipt is not pre-reveal custody",
    )
    _assert(
        receipt.get("qualifying_owner_response") is None,
        "receipt pre-qualifies the response",
    )
    _assert(
        receipt.get("owner_yes_is_sufficient_without_other_gates") is False,
        "receipt weakens promotion gates",
    )
    response = receipt.get("response_binding", {})
    surface = receipt.get("surface_binding", {})
    _assert(response.get("bytes") == len(response_bytes), "receipt response size changed")
    _assert(
        response.get("sha256") == _sha256_bytes(response_bytes),
        "receipt response hash changed",
    )
    _assert(
        response.get("decision_values_read") is False,
        "receipt read decisions before lock",
    )
    _assert(
        response.get("note_values_read") is False,
        "receipt read notes before lock",
    )
    _assert(surface.get("bytes") == len(surface_bytes), "receipt surface size changed")
    _assert(
        surface.get("sha256") == _sha256_bytes(surface_bytes),
        "receipt surface hash changed",
    )


def _load_prior_intake(repository_root: Path) -> tuple[dict[str, Any], bytes]:
    path = repository_root / (
        "samples/labels/review/windigo/phase-two/intake/"
        "WINDIGO-OWNER-RESPONSE-INTAKE-2026-001.json"
    )
    data = path.read_bytes()
    _assert(len(data) == PRIOR_INTAKE_BYTES, "prior accepted-region report size changed")
    _assert(
        _sha256_bytes(data) == PRIOR_INTAKE_SHA256,
        "prior accepted-region report hash changed",
    )
    report = _json(data, path.name)
    outcome = report.get("outcome", {})
    _assert(
        report.get("label_set_version") == PRIOR_LABEL_SET_VERSION,
        "prior label set changed",
    )
    _assert(
        outcome.get("cumulative_owner_approved_region_labels") == 12,
        "prior label count changed",
    )
    _assert(outcome.get("event_group_count") == 6, "prior event count changed")
    _assert(report.get("dataset_version") is None, "prior report contains a dataset")
    return report, data


def _verify_candidate_raster(
    path: Path,
    surface_candidate: dict[str, Any],
    rebuilt_candidate: dict[str, Any],
    selected_candidate: dict[str, Any],
) -> dict[str, Any]:
    expected = surface_candidate["candidate_raster_binding"]
    candidate_id = surface_candidate["candidate_id"]
    _assert(path.is_file(), f"candidate raster missing: {path.name}")
    _assert(path.stat().st_size == expected["bytes"], "candidate raster size changed")
    _assert(_sha256_file(path) == expected["sha256"], "candidate raster hash changed")
    _assert(
        rebuilt_candidate["candidate_id"] == candidate_id,
        "candidate order changed",
    )
    _assert(
        rebuilt_candidate["proposal_binding_sha256"]
        == EXPECTED_CANDIDATES[candidate_id]["proposal_binding_sha256"],
        "proposal binding changed",
    )
    with rasterio.open(path) as dataset:
        values = dataset.read(1)
        tags = dataset.tags()
        _assert(
            dataset.count == 1 and dataset.dtypes == ("uint8",),
            "candidate dtype changed",
        )
        _assert(
            dataset.crs is not None and dataset.crs.to_epsg() == 32610,
            "candidate CRS changed",
        )
        _assert(dataset.nodata == 255.0, "candidate nodata changed")
        _assert(
            set(int(value) for value in np.unique(values)) <= {0, 1, 2},
            "candidate domain changed",
        )
        _assert(
            np.array_equal(values == 1, selected_candidate["core"]),
            "candidate core changed",
        )
        _assert(
            np.array_equal(values == 2, selected_candidate["ring"]),
            "candidate unknown ring changed",
        )
        _assert(tags.get("candidate_id") == candidate_id, "candidate tag changed")
        _assert(
            tags.get("proposed_class") == surface_candidate["proposed_class"],
            "candidate class tag changed",
        )
        _assert(tags.get("owner_decision") == "none", "raster embeds a decision")
        _assert(tags.get("label_created") == "false", "raster embeds a label")
    return {
        "bytes": path.stat().st_size,
        "sha256": _sha256_file(path),
        "core_pixels": int((values == 1).sum()),
        "unknown_ring_pixels": int((values == 2).sum()),
        "crs": "EPSG:32610",
        "class_domain": [0, 1, 2],
        "exact_recomputed_core": True,
        "exact_recomputed_unknown_ring": True,
    }


def _proposal_without_written_bindings(value: dict[str, Any]) -> dict[str, Any]:
    normalized = json.loads(json.dumps(value))
    normalized["git_source_commit"] = None
    normalized["bindings"]["fresh_background_reverification_source_commit"] = None
    for candidate in normalized["candidates"]:
        candidate["candidate_raster_bytes"] = None
        candidate["candidate_raster_sha256"] = None
    return normalized


def build_private_reconciliation(
    *,
    repository_root: Path,
    pre_package: Path,
    post_package: Path,
    archive_path: Path,
    extracted_root: Path,
    background_report_path: Path,
    sufficiency_report_path: Path,
    proposal_path: Path,
    surface_path: Path,
    response_path: Path,
    receipt_path: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, Any]:
    """Recompute response, source, raster, uncertainty, and leakage gates."""
    _assert(len(git_source_commit) == 40, "git source commit must be a full SHA")
    _timestamp(generated_at_utc, "generated time")
    for private_path in (
        pre_package,
        post_package,
        archive_path,
        extracted_root,
        response_path,
        receipt_path,
    ):
        _assert_ignored(repository_root, private_path)

    surface, surface_bytes = _validate_surface(surface_path)
    response_bytes = response_path.read_bytes()
    receipt_bytes = receipt_path.read_bytes()
    _assert(
        len(response_bytes) == EXPECTED_RESPONSE_BYTES,
        "production response size changed",
    )
    _assert(
        _sha256_bytes(response_bytes) == EXPECTED_RESPONSE_SHA256,
        "production response hash changed",
    )
    _assert(
        len(receipt_bytes) == EXPECTED_RECEIPT_BYTES,
        "production receipt size changed",
    )
    _assert(
        _sha256_bytes(receipt_bytes) == EXPECTED_RECEIPT_SHA256,
        "production receipt hash changed",
    )
    receipt = _json(receipt_bytes, receipt_path.name)
    _validate_receipt(
        receipt,
        response_bytes=response_bytes,
        surface_bytes=surface_bytes,
    )
    response = _json(response_bytes, response_path.name)
    try:
        validation = validate_completed_response(surface, response)
    except Exception as error:
        raise WardCreekOwnerResponseIntakeError(
            "completed owner response failed validation"
        ) from error

    proposal_bytes = proposal_path.read_bytes()
    _assert(
        len(proposal_bytes) == EXPECTED_PROPOSAL_BYTES,
        "proposal size changed",
    )
    _assert(
        _sha256_bytes(proposal_bytes) == EXPECTED_PROPOSAL_SHA256,
        "proposal hash changed",
    )
    proposal = _json(proposal_bytes, proposal_path.name)
    _assert(proposal.get("report_id") == PROPOSAL_ID, "proposal identity changed")
    _assert(proposal.get("run_id") == PROPOSAL_RUN_ID, "proposal run changed")
    _assert(
        proposal.get("summary", {}).get("labels_created") == 0,
        "proposal already contains labels",
    )

    rebuilt, selected, _ = rebuild_proposal(
        repository_root=repository_root,
        pre_package=pre_package,
        post_package=post_package,
        archive_path=archive_path,
        extracted_root=extracted_root,
        background_report_path=background_report_path,
        sufficiency_report_path=sufficiency_report_path,
        generated_at_utc=proposal["generated_at_utc"],
        run_id=proposal["run_id"],
        git_source_commit=git_source_commit,
    )
    _assert(
        _proposal_without_written_bindings(rebuilt)
        == _proposal_without_written_bindings(proposal),
        "proposal does not exactly reconstruct from controlled source bytes",
    )
    _assert(
        rebuilt["route_evidence"]["burned"]["pixels"]
        == EXPECTED_ROUTE_COUNTS["burned_route"],
        "burned route changed",
    )
    _assert(
        rebuilt["route_evidence"]["background"]["pixels"]
        == EXPECTED_ROUTE_COUNTS["background_route"],
        "background route changed",
    )
    _assert(
        rebuilt["leakage_gate"]["ward_creek_event_group_absent"] is True
        and rebuilt["leakage_gate"]["ward_creek_year_absent"] is True,
        "proposal-time leakage gate changed",
    )

    prior, prior_bytes = _load_prior_intake(repository_root)
    record_bindings = _record_bindings(repository_root)
    exact_record_gate = len(record_bindings) == len(RECORD_BINDINGS)
    proposal_candidates = {
        item["candidate_id"]: item for item in proposal["candidates"]
    }
    rebuilt_candidates = {
        item["candidate_id"]: item for item in rebuilt["candidates"]
    }
    selected_candidates = {
        item["candidate_id"]: item for item in selected
    }

    units: list[dict[str, Any]] = []
    provisional_class_counts: Counter[str] = Counter()
    provisional_core_pixels = 0
    reviewed_ring_pixels = 0
    for surface_candidate, response_item in zip(
        surface["candidates"],
        response["responses"],
        strict=True,
    ):
        candidate_id = surface_candidate["candidate_id"]
        _assert(
            surface_candidate["event_group_id"] == REVIEW_EVENT_GROUP_ID,
            "review event identity changed",
        )
        proposal_candidate = proposal_candidates[candidate_id]
        rebuilt_candidate = rebuilt_candidates[candidate_id]
        selected_candidate = selected_candidates[candidate_id]
        _assert(
            proposal_candidate["event_group_id"] == EXPECTED_EVENT_GROUP_ID,
            "proposal event identity changed",
        )
        _assert(
            proposal_candidate["proposed_class"]
            == surface_candidate["proposed_class"],
            "proposal class changed",
        )
        raster = _verify_candidate_raster(
            proposal_path.parent / proposal_candidate["candidate_raster"],
            surface_candidate,
            rebuilt_candidate,
            selected_candidate,
        )
        gates = {
            "owner_yes": response_item["decision"] == "yes",
            "exact_candidate_reconstruction": (
                raster["exact_recomputed_core"]
                and raster["exact_recomputed_unknown_ring"]
                and raster["sha256"]
                == surface_candidate["candidate_raster_binding"]["sha256"]
            ),
            "source_and_terms": exact_record_gate,
            "quality_and_registration": (
                raster["crs"] == "EPSG:32610"
                and raster["class_domain"] == [0, 1, 2]
                and rebuilt["bindings"]["accepted_background_report"]["sha256"]
                == proposal["bindings"]["accepted_background_report"]["sha256"]
            ),
            "uncertainty_ring_excluded": (
                raster["unknown_ring_pixels"]
                == EXPECTED_RING_PIXELS[candidate_id]
            ),
            "event_level_leakage_control": (
                proposal_candidate["event_group_id"] == EXPECTED_EVENT_GROUP_ID
                and surface_candidate["event_group_id"] == REVIEW_EVENT_GROUP_ID
                and rebuilt["leakage_gate"]["ward_creek_event_group_absent"]
                and rebuilt["leakage_gate"]["ward_creek_year_absent"]
            ),
        }
        candidate_pass = all(gates.values())
        if candidate_pass:
            provisional_class_counts[surface_candidate["proposed_class"]] += 1
            provisional_core_pixels += raster["core_pixels"]
        reviewed_ring_pixels += raster["unknown_ring_pixels"]
        units.append(
            {
                "candidate_id": candidate_id,
                "candidate_binding_sha256": surface_candidate[
                    "candidate_binding_sha256"
                ],
                "candidate_raster_sha256": raster["sha256"],
                "event_group_id": surface_candidate["event_group_id"],
                "proposed_class": surface_candidate["proposed_class"],
                "owner_decision": response_item["decision"],
                "note_present": bool(response_item["notes"]),
                "note_sha256": _sha256_bytes(
                    response_item["notes"].encode("utf-8")
                ),
                "gates": gates,
                "candidate_gate_passed": candidate_pass,
                "core_pixels": raster["core_pixels"],
                "unknown_ring_pixels": raster["unknown_ring_pixels"],
            }
        )

    event_complete = (
        len(units) == 2
        and all(item["candidate_gate_passed"] for item in units)
        and provisional_class_counts == Counter({"burned": 1, "background": 1})
        and provisional_core_pixels == 39
        and reviewed_ring_pixels == 66
    )
    for unit in units:
        unit["disposition"] = (
            "OWNER_APPROVED_PROTOTYPE_REGION_LABEL"
            if event_complete
            else "EXCLUDED_NO_PARTIAL_EVENT_PROMOTION"
        )
        unit["accepted_core_pixels"] = unit["core_pixels"] if event_complete else 0
        unit["excluded_unknown_ring_pixels"] = (
            unit["unknown_ring_pixels"] if event_complete else 0
        )

    prior_outcome = prior["outcome"]
    added_labels = 2 if event_complete else 0
    added_core_pixels = 39 if event_complete else 0
    added_ring_pixels = 66 if event_complete else 0
    classes = Counter(prior_outcome["cumulative_prototype_label_class_counts"])
    if event_complete:
        classes.update({"burned": 1, "background": 1})
    event_count = prior_outcome["event_group_count"] + (1 if event_complete else 0)
    cumulative_core_pixels = (
        prior_outcome["cumulative_accepted_core_pixels"] + added_core_pixels
    )
    decision = (
        "ACCEPT_WARD_CREEK_AS_SEVENTH_OWNER_APPROVED_PROTOTYPE_EVENT_AUTHORIZE_SIX_EVENT_SUFFICIENCY_RERUN"
        if event_complete
        else "REJECT_PARTIAL_OR_FAILED_WARD_CREEK_EVENT_RETAIN_EXISTING_BLOCK"
    )
    return {
        "report_id": f"{REPORT_ID}-PRIVATE",
        "report_version": PRIVATE_REPORT_VERSION,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": TASK_ISSUE,
        "unit_id": UNIT_ID,
        "git_source_commit": git_source_commit,
        "software_version": burnlens.__version__,
        "aoi_version": AOI_VERSION if event_complete else prior["aoi_version"],
        "target_version": TARGET_VERSION,
        "label_schema_version": LABEL_SCHEMA_VERSION,
        "label_set_version": (
            LABEL_SET_VERSION if event_complete else PRIOR_LABEL_SET_VERSION
        ),
        "dataset_version": None,
        "split_version": None,
        "baseline_version": None,
        "model_version": None,
        "input_bindings": {
            "prior_label_intake": {
                "report_id": prior["report_id"],
                "run_id": prior["run_id"],
                "bytes": len(prior_bytes),
                "sha256": _sha256_bytes(prior_bytes),
            },
            "background_report": _binding(
                background_report_path,
                report_id=rebuilt["bindings"]["accepted_background_report"][
                    "report_id"
                ],
            ),
            "sufficiency_report": _binding(
                sufficiency_report_path,
                report_id=rebuilt["bindings"]["accepted_sufficiency_report"][
                    "report_id"
                ],
            ),
            "proposal": {
                "report_id": proposal["report_id"],
                "run_id": proposal["run_id"],
                "bytes": len(proposal_bytes),
                "sha256": _sha256_bytes(proposal_bytes),
            },
            "surface": {
                "report_id": surface["report_id"],
                "run_id": surface["run_id"],
                "bytes": len(surface_bytes),
                "sha256": _sha256_bytes(surface_bytes),
                "ordered_manifest_sha256": surface["ordered_manifest_sha256"],
            },
            "response": {
                "bytes": len(response_bytes),
                "sha256": _sha256_bytes(response_bytes),
            },
            "receipt": {
                "bytes": len(receipt_bytes),
                "sha256": _sha256_bytes(receipt_bytes),
            },
        },
        "record_bindings": record_bindings,
        "response_validation": validation,
        "decision_counts": validation["decision_counts"],
        "private_units": units,
        "outcome": {
            "ward_creek_owner_approved_region_labels": added_labels,
            "ward_creek_class_counts": (
                {"background": 1, "burned": 1} if event_complete else {}
            ),
            "ward_creek_accepted_core_pixels": added_core_pixels,
            "ward_creek_reviewed_unknown_ring_pixels": reviewed_ring_pixels,
            "ward_creek_excluded_unknown_ring_pixels": added_ring_pixels,
            "ward_creek_event_complete": event_complete,
            "no_partial_event_promotion": True,
            "cumulative_owner_approved_region_labels": (
                prior_outcome["cumulative_owner_approved_region_labels"]
                + added_labels
            ),
            "cumulative_prototype_label_class_counts": dict(
                sorted(classes.items())
            ),
            "cumulative_accepted_core_pixels": cumulative_core_pixels,
            "cumulative_accepted_core_area_ha": round(
                cumulative_core_pixels * 0.04,
                2,
            ),
            "cumulative_excluded_unknown_ring_pixels": (
                prior_outcome["cumulative_excluded_unknown_ring_pixels"]
                + added_ring_pixels
            ),
            "event_group_count": event_count,
            "six_event_sufficiency_rerun_eligible": event_complete,
            "separate_sufficiency_evaluator_passed": False,
            "dataset_fitness_reopened": False,
            "training_authorized": False,
        },
        "promotion_gates": {
            "exact_response_and_pre_reveal_custody": True,
            "exact_source_pixel_recomputation": True,
            "candidate_raster_reconstruction": True,
            "source_and_terms": exact_record_gate,
            "quality_and_registration": True,
            "unknown_ring_excluded": True,
            "event_level_leakage_control": True,
            "both_classes_and_no_partial_promotion": event_complete,
        },
        "decision": decision,
        "next_gate": (
            "P2O4-T39-U08 must construct the exact six-event candidate that excludes "
            "Darlene, then rerun every Phase Two sufficiency gate. No dataset, split, "
            "baseline, or training action is authorized by this intake."
        ),
        "warning": WARNING,
    }


def public_report(
    private: dict[str, Any],
    private_binding: dict[str, Any],
) -> dict[str, Any]:
    """Remove unit decisions, notes, and private paths from public evidence."""
    return {
        "report_id": REPORT_ID,
        "report_version": REPORT_VERSION,
        "generated_at_utc": private["generated_at_utc"],
        "run_id": private["run_id"],
        "repository": private["repository"],
        "task_issue": private["task_issue"],
        "unit_id": private["unit_id"],
        "git_source_commit": private["git_source_commit"],
        "software_version": private["software_version"],
        "aoi_version": private["aoi_version"],
        "target_version": private["target_version"],
        "label_schema_version": private["label_schema_version"],
        "label_set_version": private["label_set_version"],
        "dataset_version": None,
        "split_version": None,
        "baseline_version": None,
        "model_version": None,
        "input_bindings": {
            **private["input_bindings"],
            "private_reconciliation": private_binding,
        },
        "record_bindings": private["record_bindings"],
        "decision_counts": private["decision_counts"],
        "outcome": private["outcome"],
        "promotion_gates": private["promotion_gates"],
        "privacy": {
            "notes_public": False,
            "unit_decisions_public": False,
            "private_paths_public": False,
        },
        "boundaries": {
            "owner_review_is_independent_ground_truth": False,
            "unknown_ring_is_background": False,
            "dataset_created": False,
            "split_created": False,
            "baseline_created": False,
            "model_created": False,
            "training_authorized": False,
            "accuracy_or_operational_claim_created": False,
        },
        "attribution": [
            "Contains modified Copernicus Sentinel data 2019, accessed through CDSE.",
            "MTBS is analyst-interpreted remotely sensed reference evidence from USGS and USDA Forest Service, not field truth.",
            "The affirmative-background route is specific to the exact paired optical window and conservative MTBS exclusion.",
        ],
        "warning": private["warning"],
        "decision": private["decision"],
        "next_gate": private["next_gate"],
    }


def _render_png(report: dict[str, Any], path: Path) -> None:
    canvas = Image.new("RGB", (1600, 1100), "#07110f")
    draw = ImageDraw.Draw(canvas)
    draw.text(
        (70, 55),
        "BURNLENS / WARD CREEK OWNER RESPONSE INTAKE",
        fill="#b9d8cf",
        font=_font(23),
    )
    draw.text(
        (70, 103),
        "Exact custody and every promotion gate pass.",
        fill="#eef7f3",
        font=_font(34),
    )
    counts = report["decision_counts"]
    outcome = report["outcome"]
    metrics = [
        ("OWNER RESPONSES", str(sum(counts.values()))),
        ("NEW REGIONS", str(outcome["ward_creek_owner_approved_region_labels"])),
        ("CUMULATIVE REGIONS", str(outcome["cumulative_owner_approved_region_labels"])),
        ("PROTOTYPE EVENTS", str(outcome["event_group_count"])),
    ]
    for index, (label, value) in enumerate(metrics):
        x = 70 + (index % 2) * 755
        y = 190 + (index // 2) * 185
        draw.rounded_rectangle(
            (x, y, x + 700, y + 145),
            radius=18,
            fill="#0e1d1a",
            outline="#315b50",
            width=2,
        )
        draw.text((x + 28, y + 25), label, fill="#b9d8cf", font=_font(18))
        draw.text((x + 28, y + 62), value, fill="#ffca73", font=_font(42))
    lines = [
        "Two yes decisions are reconciled only after exact pre-reveal custody.",
        "Both candidate rasters reconstruct from immutable source pixels.",
        "All 66 unknown-ring pixels remain excluded.",
        "Ward Creek adds one burned and one background prototype region.",
        "The next gate reruns six-event sufficiency without Darlene.",
        "No dataset, split, baseline, model, metric, or training authorization exists.",
    ]
    y = 590
    for line in lines:
        draw.text((90, y), f"• {line}", fill="#eef7f3", font=_font(21))
        y += 58
    draw.text(
        (70, 1012),
        "Experimental prototype evidence. Official sources govern.",
        fill="#ffca73",
        font=_font(19),
    )
    canvas.save(path, format="PNG", optimize=False)


def _render_html(report: dict[str, Any]) -> str:
    counts = report["decision_counts"]
    outcome = report["outcome"]
    attribution = "".join(
        f"<li>{escape(item)}</li>" for item in report["attribution"]
    )
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>BurnLens Ward Creek owner response intake</title><style>
:root{{color-scheme:dark}}*{{box-sizing:border-box}}body{{margin:0;background:#07110f;color:#eef7f3;font:17px/1.55 system-ui,sans-serif;overflow-wrap:anywhere}}header{{padding:2rem max(1rem,calc((100vw - 1040px)/2));background:#0e1d1a;border-bottom:1px solid #315b50}}header p{{color:#b9d8cf}}h1{{max-width:850px;font-size:clamp(2rem,5vw,4rem);line-height:1.05}}main{{max-width:1040px;margin:auto;padding:1rem}}.warning,.card{{min-width:0;padding:1.1rem;border:1px solid #315b50;border-radius:14px;background:#0e1d1a}}.warning{{border-color:#a06b28;color:#ffca73}}.metrics{{display:grid;grid-template-columns:repeat(4,1fr);gap:.8rem;margin:1rem 0}}.metric{{min-width:0;padding:1rem;background:#eef7f3;color:#07110f;border-radius:12px}}.metric strong{{display:block;color:#006b64;font-size:2rem}}img{{display:block;max-width:100%;height:auto;border:1px solid #315b50}}code{{word-break:break-word}}li+li{{margin-top:.45rem}}@media(max-width:700px){{.metrics{{grid-template-columns:1fr 1fr}}header{{padding:1.4rem 1rem}}main{{padding:.65rem}}}}
</style></head><body><header><p>BURNLENS / PHASE TWO / ISSUE #554</p><h1>Ward Creek passes the complete prototype-label gate.</h1><p>Exact private custody, source-pixel replay, and aggregate public evidence.</p></header><main>
<p class="warning">{escape(report['warning'])}</p><section class="metrics"><div class="metric"><strong>{sum(counts.values())}</strong>owner responses</div><div class="metric"><strong>{outcome['ward_creek_owner_approved_region_labels']}</strong>new regions</div><div class="metric"><strong>{outcome['cumulative_owner_approved_region_labels']}</strong>cumulative regions</div><div class="metric"><strong>{outcome['event_group_count']}</strong>prototype events</div></section>
<section class="card"><h2>Aggregate result</h2><p>Owner decisions: {counts['yes']} yes / {counts['no']} no / {counts['uncertain']} uncertain. Ward Creek adds one burned and one background prototype region only because every non-owner gate also passes.</p><p>The exact source pixels, proposal routes, candidate rasters, native grid, uncertainty rings, terms, and event identity reconstruct. Notes and unit decisions remain private.</p></section>
<img src="{REPORT_ID}.png" alt="Ward Creek owner response intake gate summary">
<section class="card"><h2>Sources and roles</h2><ul>{attribution}</ul></section>
<section class="card"><h2>What happens next</h2><p>The seven-event prototype pool is not a dataset. U08 must construct the exact six-event candidate that excludes Darlene and rerun every sufficiency gate before any dataset, split, baseline, or training step.</p></section>
<section class="card"><h2>Decision</h2><p><strong>{escape(report['decision'])}</strong></p><p>BurnLens <code>{escape(report['software_version'])}</code> &middot; label set <code>{escape(report['label_set_version'])}</code> &middot; schema <code>{escape(report['label_schema_version'])}</code> &middot; run <code>{escape(report['run_id'])}</code> &middot; source <code>{escape(report['git_source_commit'])}</code>.</p></section>
</main></body></html>'''


def write_private_no_overwrite(
    repository_root: Path,
    path: Path,
    report: dict[str, Any],
) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    _assert_ignored(repository_root, path)
    payload = (json.dumps(report, indent=2) + "\n").encode("utf-8")
    try:
        with path.open("xb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as error:
        raise WardCreekOwnerResponseIntakeError(
            "refusing to overwrite private reconciliation"
        ) from error
    return {
        "bytes": len(payload),
        "sha256": _sha256_bytes(payload),
        "committed": False,
        "ignored": True,
    }


def write_public_no_overwrite(
    report: dict[str, Any],
    output_directory: Path,
) -> list[dict[str, Any]]:
    if output_directory.exists():
        raise WardCreekOwnerResponseIntakeError(
            "public output directory already exists"
        )
    output_directory.mkdir(parents=True)
    png_path = output_directory / f"{REPORT_ID}.png"
    html_path = output_directory / f"{REPORT_ID}.html"
    json_path = output_directory / f"{REPORT_ID}.json"
    _render_png(report, png_path)
    html_path.write_text(_render_html(report), encoding="utf-8", newline="\n")
    report["outputs"] = [
        {"path": html_path.name, **_binding(html_path), "media_type": "text/html"},
        {"path": png_path.name, **_binding(png_path), "media_type": "image/png"},
    ]
    json_path.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return [
        {
            "path": json_path.name,
            **_binding(json_path),
            "media_type": "application/json",
        },
        *report["outputs"],
    ]
