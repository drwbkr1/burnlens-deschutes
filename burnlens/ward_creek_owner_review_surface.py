"""Build the exact blank two-card Ward Creek owner-review surface."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from PIL import Image

from .owner_review_batch import (
    MANIFEST_SCHEMA_VERSION,
    OwnerReviewBatchError,
    build_surface,
    write_surface,
)


SURFACE_ID = "WARD-CREEK-OWNER-REVIEW-SURFACE-2026-001"
MILESTONE_ID = "P2O4-T39"
TASK_ISSUE = 554
EVENT_GROUP_ID = "event-ward-creek-2019"
PROPOSAL_ID = "WARD-CREEK-REGION-PROPOSAL-2026-001"
PROPOSAL_RUN_ID = "BL-2026-07-24-ward-creek-region-proposal-r001"
PROPOSAL_JSON_SHA256 = "06100de3df058b397f3a797069a2705eea3d7f79c71dfa333a11698331b13638"
PROPOSAL_PNG_SHA256 = "78ccc856def6e8b0551a553daa80e0ae2bf9f1736c90e4d938ab907dab292498"
EXPECTED_CANDIDATES = {
    "WCP-001": {
        "proposed_class": "burned",
        "proposal_binding_sha256": "eadf744a1a48db77ce9a7d76ca222cdfa4df6c0f8f19752aa61a4184b17ed735",
        "raster_sha256": "a9b525cca8461fb9550988b045878cae41e17b9fa0c4d5db55de87ebeabdeccc",
        "crop": (45, 158, 1756, 500),
        "basis": (
            "Usable paired optical change passes the frozen coherent burn screen, "
            "and native MTBS dNBR6 classes 2-4 provide separate reference support."
        ),
    },
    "WCP-002": {
        "proposed_class": "background",
        "proposal_binding_sha256": "6ec5ab221aa7ca559d87621c1ea3817e864530dd12beda5b85c845d4573159dd",
        "raster_sha256": "787bf4455104bbc5ac34b56f409db27b60417b96d5b551687e375bc302c6dfe3",
        "crop": (45, 529, 1756, 870),
        "basis": (
            "Usable paired optical stability passes the frozen multi-signal "
            "coherence rule outside the complete native MTBS domain plus 60 meters."
        ),
    },
}


def _digest(path: Path) -> str:
    value = sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            value.update(chunk)
    return value.hexdigest()


def _binding(path: Path, *, relative_path: str | None = None) -> dict[str, Any]:
    return {
        "path": relative_path or path.name,
        "bytes": path.stat().st_size,
        "sha256": _digest(path),
    }


def _load_proposal(directory: Path) -> tuple[dict[str, Any], dict[str, Path]]:
    json_path = directory / f"{PROPOSAL_ID}.json"
    png_path = directory / f"{PROPOSAL_ID}.png"
    if not json_path.is_file() or not png_path.is_file():
        raise OwnerReviewBatchError("exact Ward Creek proposal artifacts are missing")
    if _digest(json_path) != PROPOSAL_JSON_SHA256 or _digest(png_path) != PROPOSAL_PNG_SHA256:
        raise OwnerReviewBatchError("exact Ward Creek proposal artifact hash changed")
    try:
        report = json.loads(json_path.read_text(encoding="utf-8"))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise OwnerReviewBatchError("Ward Creek proposal JSON is invalid") from error
    if (
        report.get("report_id") != PROPOSAL_ID
        or report.get("run_id") != PROPOSAL_RUN_ID
        or report.get("decision")
        != "PROPOSE_EXACT_WARD_CREEK_TWO_CLASS_REGIONS_KEEP_OWNER_REVIEW_AND_PROMOTION_CLOSED"
        or report.get("summary", {}).get("class_counts") != {"burned": 1, "background": 1}
        or report.get("summary", {}).get("owner_responses") != 0
        or report.get("summary", {}).get("labels_created") != 0
        or report.get("output_label_set_version") is not None
        or report.get("dataset_version") is not None
        or report.get("split_version") is not None
        or report.get("baseline_version") is not None
        or report.get("model_version") is not None
    ):
        raise OwnerReviewBatchError("Ward Creek proposal state changed")
    candidates = report.get("candidates")
    if not isinstance(candidates, list) or [
        item.get("candidate_id") for item in candidates
    ] != list(EXPECTED_CANDIDATES):
        raise OwnerReviewBatchError("Ward Creek proposal candidate roster changed")
    rasters: dict[str, Path] = {}
    for candidate in candidates:
        candidate_id = candidate["candidate_id"]
        expected = EXPECTED_CANDIDATES[candidate_id]
        raster = directory / candidate["candidate_raster"]
        if (
            candidate.get("proposed_class") != expected["proposed_class"]
            or candidate.get("proposal_binding_sha256") != expected["proposal_binding_sha256"]
            or candidate.get("candidate_raster_sha256") != expected["raster_sha256"]
            or not raster.is_file()
            or raster.stat().st_size != candidate.get("candidate_raster_bytes")
            or _digest(raster) != expected["raster_sha256"]
        ):
            raise OwnerReviewBatchError(
                f"Ward Creek candidate binding changed: {candidate_id}"
            )
        rasters[candidate_id] = raster
    return report, {"json": json_path, "png": png_path, **rasters}


def _write_candidate_evidence(
    proposal_png: Path,
    evidence_root: Path,
) -> dict[str, dict[str, Any]]:
    with Image.open(proposal_png) as image:
        image.load()
        if image.size != (1800, 1040):
            raise OwnerReviewBatchError("Ward Creek proposal render dimensions changed")
        evidence: dict[str, dict[str, Any]] = {}
        for candidate_id, expected in EXPECTED_CANDIDATES.items():
            relative = f"{SURFACE_ID}-{candidate_id}.png"
            output = evidence_root / relative
            output.parent.mkdir(parents=True, exist_ok=True)
            image.crop(expected["crop"]).save(output, format="PNG", optimize=False)
            evidence[candidate_id] = {
                **_binding(output, relative_path=relative),
                "alt": (
                    f"Exact {candidate_id} proposed {expected['proposed_class']} evidence: "
                    "pre and post optical views, candidate core, unknown ring, and permitted source evidence."
                ),
            }
    return evidence


def build_manifest(
    proposal_directory: Path,
    evidence_root: Path,
    *,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, Any]:
    report, paths = _load_proposal(proposal_directory)
    evidence = _write_candidate_evidence(paths["png"], evidence_root)
    candidates: list[dict[str, Any]] = []
    for candidate in report["candidates"]:
        candidate_id = candidate["candidate_id"]
        proposed_class = candidate["proposed_class"]
        expected = EXPECTED_CANDIDATES[candidate_id]
        limitations = [
            "This is disclosed prototype evidence, not ground truth or independent validation.",
            "A yes is necessary but insufficient; every non-owner gate must still pass.",
        ]
        if proposed_class == "background":
            limitations.append(
                "The background proposal shows stability in this exact fire-window pair; "
                "it does not prove the land was never burned."
            )
        else:
            limitations.append(
                "The burned core is 14 pixels, not the 25-pixel target; BurnLens "
                "preserves the nearest eligible intact component instead of forcing it."
            )
            limitations.append(
                "MTBS is official mapping evidence; BurnLens is not field validated."
            )
        candidates.append(
            {
                "candidate_id": candidate_id,
                "event_group_id": EVENT_GROUP_ID,
                "proposed_class": proposed_class,
                "question": (
                    f"Should this exact region become an owner-approved prototype {proposed_class} label?"
                ),
                "proposition_basis": expected["basis"],
                "limitations": limitations,
                "facts": [
                    {
                        "label": "Event",
                        "value": "Ward Creek 2019 / OR4494912090120190812",
                    },
                    {
                        "label": "Core",
                        "value": (
                            f"{candidate['core_pixels']} native 20 m pixels / "
                            f"{candidate['core_area_hectares']:.2f} ha"
                        ),
                    },
                    {
                        "label": "Unknown ring",
                        "value": f"{candidate['unknown_ring_pixels']} excluded pixels",
                    },
                    {
                        "label": "Target",
                        "value": (
                            f"{candidate['target_pixels']} pixels; "
                            f"actual gap {candidate['target_gap_pixels']:+d}"
                        ),
                    },
                    {
                        "label": "Selection",
                        "value": (
                            f"fixed dNBR interval {candidate['dnbr_interval']}; "
                            f"tie {candidate['selection_tie_sha256']}"
                        ),
                    },
                ],
                "proposal_binding": {
                    "record_id": PROPOSAL_ID,
                    "bytes": paths["json"].stat().st_size,
                    "sha256": PROPOSAL_JSON_SHA256,
                },
                "candidate_raster_binding": _binding(
                    paths[candidate_id],
                    relative_path=paths[candidate_id].name,
                ),
                "evidence_images": [evidence[candidate_id]],
            }
        )
    return {
        "manifest_schema_version": MANIFEST_SCHEMA_VERSION,
        "surface_id": SURFACE_ID,
        "surface_revision": 1,
        "surface_run_id": run_id,
        "milestone_id": MILESTONE_ID,
        "task_issue": TASK_ISSUE,
        "generated_at_utc": generated_at_utc,
        "git_source_commit": git_source_commit,
        "title": "Ward Creek exact two-card owner review",
        "review_groups": [
            {
                "event_group_id": EVENT_GROUP_ID,
                "event_label": "Ward Creek 2019",
                "context": (
                    "Review both disclosed proposals independently. One is proposed burned "
                    "and one background; neither is a label before exact response lock and "
                    "non-owner reconciliation."
                ),
                "candidate_ids": list(EXPECTED_CANDIDATES),
            }
        ],
        "candidates": candidates,
        "batch_size_exception": "single-event-pair",
        "supersedes_surface_id": None,
    }


def write_ward_creek_surface(
    proposal_directory: Path,
    output_directory: Path,
    *,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> list[dict[str, Any]]:
    if output_directory.exists():
        raise OwnerReviewBatchError("output directory already exists")
    with TemporaryDirectory(prefix="burnlens-ward-creek-review-") as temporary:
        evidence_root = Path(temporary)
        manifest = build_manifest(
            proposal_directory,
            evidence_root,
            generated_at_utc=generated_at_utc,
            run_id=run_id,
            git_source_commit=git_source_commit,
        )
        surface = build_surface(manifest)
        return write_surface(surface, evidence_root, output_directory)
