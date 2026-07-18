"""Inspect exact current BAER, RAVG, and MTBS bundles against frozen proposals.

The checkpoint produces review evidence only. It never changes a proposal,
accepts an owner decision, creates a dataset, or trains a model.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
from html import escape
import io
import json
from pathlib import Path, PurePosixPath
from typing import Any
from zipfile import BadZipFile, ZipFile

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import rasterio
from rasterio.io import MemoryFile
from rasterio.warp import Resampling, reproject


SOFTWARE_VERSION = "0.24.0"
REPORT_ID = "CURRENT-REFERENCE-BUNDLE-FITNESS-2026-001"
REPORT_VERSION = "current-reference-bundle-fitness-v0.1.0"
PROTOCOL_VERSION = "current-reference-bundle-fitness-protocol-v0.1.0"
SOURCE_RECORD_ID = "SOURCE-2026-017"
TERMS_REVIEW_ID = "TERMS-2026-012"
SOURCE_PRECEDENCE_ID = "SOURCE_PRECEDENCE-2026-010"
OWNER_REVIEW_PROTOCOL = "owner-confirmed-prototype-label-review-v0.1.0"
TASK_ISSUE = 416
DECISION = "ACCEPT_CURRENT_BUNDLES_AS_BOUNDED_OWNER_REVIEW_EVIDENCE_DEFER_LABELS_DATASET_MODEL"
WARNING = (
    "Experimental BurnLens CV evidence. Not official wildfire information. "
    "Not emergency guidance. Not evacuation, routing, tactical, or "
    "incident-command support. Official sources govern."
)
STATE_NAMES = {
    0: "background-candidate",
    1: "burned",
    2: "unknown",
    3: "excluded",
    4: "review-needed",
}
ARCHIVE_CONTRACT = {
    "usgs-delivery-20260717171845Z.zip": {
        "bytes": 8_184_622,
        "sha256": "72775e8feb44d52a03923919a2080c2e3c268e1dd7ac37dd5e4f314e639256f8",
        "members": 31,
    },
    "usgs-delivery-20260717235821Z.zip": {
        "bytes": 27_705_810,
        "sha256": "138d80b4ac2c7a438b128676e26f3f7b2cfe08c58518d4770692bc12f41ca22d",
        "members": 133,
    },
}


class CurrentReferenceBundleFitnessError(RuntimeError):
    """A deterministic, secret-free bundle-fitness failure."""


@dataclass(frozen=True)
class EventContract:
    event_group_id: str
    event_id: str
    display_name: str
    proposal: str
    mtbs_token: str | None
    ravg_token: str
    baer_token: str


EVENTS = (
    EventContract(
        "event-darlene3-or-2024",
        "OR4364712147820240625",
        "Darlene 3",
        "samples/labels/phase-two/LABEL-PROPOSAL-2026-001-state.tif",
        None,
        "ravg_or4364712147820240625_10030383",
        "baer_or4364712147820240625_10030231",
    ),
    EventContract(
        "event-mckay-1035-ne-2017",
        "OR4375212142520170829",
        "McKay 1035 NE",
        "samples/labels/cross-event/phase-two/CROSS-EVENT-LABEL-TRANSFER-2026-002-mckay-1035-ne-2017-state.tif",
        "mtbs_or4375212142520170829_10007931",
        "ravg_or4375212142520170829_10004989",
        "",
    ),
    EventContract(
        "event-tepee-1144-ne-2018",
        "OR4383912111420180907",
        "Tepee 1144 NE",
        "samples/labels/cross-event/phase-two/CROSS-EVENT-LABEL-TRANSFER-2026-002-tepee-1144-ne-2018-state.tif",
        "mtbs_or4383912111420180907_10011986",
        "ravg_or4383912111420180907_10008484",
        "or4383912111420180907_20180905_20181007",
    ),
)


def _digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def _write_lf(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8"))


def _safe_member(name: str) -> bool:
    path = PurePosixPath(name)
    return bool(name) and not path.is_absolute() and ".." not in path.parts and "\\" not in name


def validate_archives(archive_dir: Path) -> tuple[dict[str, ZipFile], list[dict[str, Any]]]:
    opened: dict[str, ZipFile] = {}
    summaries: list[dict[str, Any]] = []
    try:
        for name, expected in ARCHIVE_CONTRACT.items():
            path = archive_dir / name
            if not path.is_file():
                raise CurrentReferenceBundleFitnessError(f"required archive missing: {name}")
            data = path.read_bytes()
            if len(data) != expected["bytes"] or _digest(data) != expected["sha256"]:
                raise CurrentReferenceBundleFitnessError(f"archive identity mismatch: {name}")
            archive = ZipFile(io.BytesIO(data))
            infos = archive.infolist()
            if len(infos) != expected["members"]:
                raise CurrentReferenceBundleFitnessError(f"archive member-count mismatch: {name}")
            names = [item.filename for item in infos]
            if any(not _safe_member(item) for item in names):
                raise CurrentReferenceBundleFitnessError(f"unsafe archive path: {name}")
            if len({item.casefold() for item in names}) != len(names):
                raise CurrentReferenceBundleFitnessError(f"case-insensitive duplicate archive path: {name}")
            if any(item.flag_bits & 0x1 for item in infos):
                raise CurrentReferenceBundleFitnessError(f"encrypted archive member: {name}")
            if any((item.external_attr >> 16) & 0o170000 == 0o120000 for item in infos):
                raise CurrentReferenceBundleFitnessError(f"archive symlink member: {name}")
            if any(item.lower().endswith(".zip") for item in names):
                raise CurrentReferenceBundleFitnessError(f"nested archive member: {name}")
            bad = archive.testzip()
            if bad is not None:
                raise CurrentReferenceBundleFitnessError(f"archive CRC failure: {name}")
            opened[name] = archive
            summaries.append({
                "filename": name,
                "bytes": len(data),
                "sha256": _digest(data),
                "member_count": len(infos),
                "uncompressed_bytes": sum(item.file_size for item in infos),
                "crc_pass": True,
                "safe_structure_pass": True,
            })
        return opened, summaries
    except (BadZipFile, OSError) as error:
        for archive in opened.values():
            archive.close()
        raise CurrentReferenceBundleFitnessError("delivered archive is unreadable") from error


def _find_member(archives: dict[str, ZipFile], token: str, suffix: str) -> tuple[ZipFile, str]:
    matches: list[tuple[ZipFile, str]] = []
    for archive in archives.values():
        for name in archive.namelist():
            if token.lower() in name.lower() and name.lower().endswith(suffix.lower()):
                matches.append((archive, name))
    if len(matches) != 1:
        raise CurrentReferenceBundleFitnessError(
            f"expected one {suffix} member for reviewed product identity; found {len(matches)}"
        )
    return matches[0]


def _read_raster(archive: ZipFile, member: str) -> tuple[bytes, dict[str, Any]]:
    data = archive.read(member)
    try:
        with MemoryFile(data) as memory, memory.open() as source:
            array = source.read(1)
            profile = {
                "crs": source.crs.to_string() if source.crs else None,
                "transform": list(source.transform)[:6],
                "width": source.width,
                "height": source.height,
                "dtype": source.dtypes[0],
                "nodata": source.nodata,
                "resolution": [abs(source.transform.a), abs(source.transform.e)],
                "array": array,
                "source_transform": source.transform,
                "source_crs": source.crs,
            }
    except rasterio.errors.RasterioError as error:
        raise CurrentReferenceBundleFitnessError("reviewed GeoTIFF is unreadable") from error
    return data, profile


def _reproject_to_proposal(profile: dict[str, Any], proposal: rasterio.DatasetReader, fill: float) -> np.ndarray:
    destination = np.full((proposal.height, proposal.width), fill, dtype=np.float32)
    reproject(
        source=profile["array"],
        destination=destination,
        src_transform=profile["source_transform"],
        src_crs=profile["source_crs"],
        src_nodata=profile["nodata"],
        dst_transform=proposal.transform,
        dst_crs=proposal.crs,
        dst_nodata=fill,
        resampling=Resampling.nearest,
    )
    return destination


def _class_counts(array: np.ndarray, nodata: float | int | None) -> dict[str, int]:
    del nodata  # Keep the full encoded domain, including explicit outside/nodata classes.
    values, counts = np.unique(array[np.isfinite(array)], return_counts=True)
    return {str(int(value)): int(count) for value, count in zip(values, counts, strict=True)}


def _cross_tab(proposal: np.ndarray, evidence: np.ndarray, categories: dict[str, np.ndarray]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for state_code, state_name in STATE_NAMES.items():
        state_mask = proposal == state_code
        counts = {name: int(np.count_nonzero(mask & state_mask)) for name, mask in categories.items()}
        denominator = int(np.count_nonzero(state_mask))
        result[state_name] = {
            "proposal_pixels": denominator,
            "evidence_counts": counts,
            "evidence_percent": {
                name: round(100 * value / denominator, 4) if denominator else 0.0
                for name, value in counts.items()
            },
        }
    return result


def _categorical_product(
    archives: dict[str, ZipFile],
    proposal_ds: rasterio.DatasetReader,
    proposal: np.ndarray,
    *,
    token: str,
    suffix: str,
    program: str,
    affirmative_values: tuple[int, ...],
    ambiguous_values: tuple[int, ...],
    invalid_values: tuple[int, ...],
) -> tuple[dict[str, Any], np.ndarray, dict[str, np.ndarray]]:
    archive, member = _find_member(archives, token, suffix)
    data, profile = _read_raster(archive, member)
    sampled = _reproject_to_proposal(profile, proposal_ds, 255)
    affirmative = np.isin(sampled, affirmative_values)
    ambiguous = np.isin(sampled, ambiguous_values)
    invalid = np.isin(sampled, invalid_values) | (sampled == 255)
    categories = {
        "affirmative": affirmative,
        "ambiguous_or_unchanged": ambiguous,
        "outside_mask_or_nodata": invalid,
    }
    record = {
        "program": program,
        "role": "categorical_owner_review_evidence",
        "member": member,
        "member_sha256": _digest(data),
        "profile": {key: value for key, value in profile.items() if key not in {"array", "source_transform", "source_crs"}},
        "native_class_counts": _class_counts(profile["array"], profile["nodata"]),
        "semantic_contract": {
            "affirmative_values": list(affirmative_values),
            "ambiguous_or_unchanged_values": list(ambiguous_values),
            "outside_mask_or_nodata_values": list(invalid_values),
            "nearest_neighbor_only": True,
            "creates_label": False,
        },
        "proposal_grid_comparison": _cross_tab(proposal, sampled, categories),
    }
    return record, sampled, categories


def _continuous_product(
    archives: dict[str, ZipFile],
    proposal_ds: rasterio.DatasetReader,
    proposal: np.ndarray,
    *,
    token: str,
    suffix: str,
) -> tuple[dict[str, Any], np.ndarray]:
    archive, member = _find_member(archives, token, suffix)
    data, profile = _read_raster(archive, member)
    sampled = _reproject_to_proposal(profile, proposal_ds, np.nan)
    state_statistics: dict[str, Any] = {}
    for code, name in STATE_NAMES.items():
        values = sampled[(proposal == code) & np.isfinite(sampled)]
        state_statistics[name] = {
            "valid_pixels": int(values.size),
            "median": round(float(np.median(values)), 3) if values.size else None,
            "q25": round(float(np.quantile(values, 0.25)), 3) if values.size else None,
            "q75": round(float(np.quantile(values, 0.75)), 3) if values.size else None,
            "positive_change_percent": round(float(100 * np.count_nonzero(values > 0) / values.size), 4) if values.size else None,
        }
    return {
        "program": "BAER",
        "role": "continuous_change_context_only",
        "member": member,
        "member_sha256": _digest(data),
        "profile": {key: value for key, value in profile.items() if key not in {"array", "source_transform", "source_crs"}},
        "state_statistics": state_statistics,
        "semantic_contract": {
            "nearest_neighbor_sampling": True,
            "positive_dnbr_is_change_evidence_not_a_burned_threshold": True,
            "creates_label": False,
        },
    }, sampled


def _agreement(proposal: np.ndarray, mtbs: dict[str, np.ndarray], ravg: dict[str, np.ndarray]) -> dict[str, Any]:
    categories = {
        "both_affirmative": mtbs["affirmative"] & ravg["affirmative"],
        "mtbs_only_affirmative": mtbs["affirmative"] & ~ravg["affirmative"],
        "ravg_only_affirmative": ravg["affirmative"] & ~mtbs["affirmative"],
        "neither_or_ambiguous_invalid": ~(mtbs["affirmative"] | ravg["affirmative"]),
    }
    return {
        "method": "MTBS dNBR6 and RAVG CBI4 sampled independently to the frozen proposal grid with nearest neighbor; no resolution gain is claimed.",
        "proposal_state_comparison": _cross_tab(proposal, np.zeros_like(proposal), categories),
        "overall_counts": {name: int(np.count_nonzero(mask)) for name, mask in categories.items()},
    }


def build_report(
    *,
    repository_root: Path,
    archive_dir: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    archives, archive_summaries = validate_archives(archive_dir)
    event_reports: list[dict[str, Any]] = []
    previews: list[dict[str, Any]] = []
    try:
        for event in EVENTS:
            proposal_path = repository_root / event.proposal
            with rasterio.open(proposal_path) as proposal_ds:
                proposal = proposal_ds.read(1)
                if set(np.unique(proposal).tolist()) - set(STATE_NAMES):
                    raise CurrentReferenceBundleFitnessError("proposal state domain drift")
                proposal_record = {
                    "path": event.proposal,
                    "sha256": _digest(proposal_path.read_bytes()),
                    "crs": proposal_ds.crs.to_string(),
                    "width": proposal_ds.width,
                    "height": proposal_ds.height,
                    "resolution": [abs(proposal_ds.transform.a), abs(proposal_ds.transform.e)],
                    "state_counts": {
                        STATE_NAMES[code]: int(np.count_nonzero(proposal == code)) for code in STATE_NAMES
                    },
                }
                products: list[dict[str, Any]] = []
                mtbs_categories = None
                mtbs_sampled = None
                if event.mtbs_token:
                    mtbs_record, mtbs_sampled, mtbs_categories = _categorical_product(
                        archives, proposal_ds, proposal,
                        token=event.mtbs_token, suffix="_dnbr6.tif", program="MTBS",
                        affirmative_values=(2, 3, 4, 5), ambiguous_values=(1,), invalid_values=(0, 6),
                    )
                    products.append(mtbs_record)
                ravg_record, ravg_sampled, ravg_categories = _categorical_product(
                    archives, proposal_ds, proposal,
                    token=event.ravg_token, suffix="_rdnbr_cbi4.tif", program="RAVG",
                    affirmative_values=(2, 3, 4), ambiguous_values=(1,), invalid_values=(0, 9),
                )
                products.append(ravg_record)
                baer_record = None
                baer_sampled = np.full(proposal.shape, np.nan, dtype=np.float32)
                if event.baer_token:
                    baer_record, baer_sampled = _continuous_product(
                        archives, proposal_ds, proposal,
                        token=event.baer_token,
                        suffix="_dnbr.tif" if event.display_name == "Darlene 3" else "_dnbr_utm.tif",
                    )
                    products.append(baer_record)
                agreement = _agreement(proposal, mtbs_categories, ravg_categories) if mtbs_categories else None
                event_reports.append({
                    "event_group_id": event.event_group_id,
                    "event_id": event.event_id,
                    "display_name": event.display_name,
                    "proposal": proposal_record,
                    "products": products,
                    "cross_program_categorical_agreement": agreement,
                    "categorical_cross_program_confirmation_available": agreement is not None,
                })
                previews.append({
                    "display_name": event.display_name,
                    "proposal": proposal,
                    "mtbs": mtbs_sampled,
                    "ravg": ravg_sampled,
                    "baer": baer_sampled,
                })
    finally:
        for archive in archives.values():
            archive.close()

    report = {
        "report_id": REPORT_ID,
        "report_version": REPORT_VERSION,
        "protocol_version": PROTOCOL_VERSION,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": TASK_ISSUE,
        "git_source_commit": git_source_commit,
        "software_version": SOFTWARE_VERSION,
        "provenance": {
            "aoi_version": "aoi-darlene3-model-v0.2.0",
            "target_version": "target-burn-scar-v0.2.0",
            "label_schema_version": "burn-scar-five-state-schema-v0.1.0",
            "owner_review_protocol": OWNER_REVIEW_PROTOCOL,
            "dataset_version": None,
            "split_version": None,
            "baseline_version": None,
            "model_version": None,
        },
        "source_controls": {
            "source_record_id": SOURCE_RECORD_ID,
            "terms_review_id": TERMS_REVIEW_ID,
            "source_precedence_id": SOURCE_PRECEDENCE_ID,
            "archive_count": len(archive_summaries),
            "product_count": 7,
            "archives": archive_summaries,
            "recipient_and_retrieval_details_retained": False,
        },
        "terms_and_semantic_boundaries": {
            "mtbs": "Analyst-interpreted thematic burn-severity evidence; thresholds are subjective and not comprehensive field validation.",
            "ravg": "Forest-calibrated vegetation-condition evidence; applicability is limited in mixed and non-forest settings and acquisition timing matters.",
            "baer": "BARC is preliminary input to BAER assessment. Final soil burn severity, when available, is the preferred field-informed BAER product.",
            "darlene_baer_delivery": "The delivered current BAER folder contains reflectance, dNBR, and RdNBR plus SBS metadata, but no classified BARC or SBS raster.",
            "tepee_baer_restriction": "Thresholded legacy BARC4/BARC256 distribution is at BAER team-leader discretion. BurnLens excludes those pixels from public output and label promotion; only the separately public unthresholded dNBR is summarized as preliminary context.",
            "resolved_for_this_checkpoint": True,
        },
        "method": {
            "proposal_preservation": "Every frozen five-state proposal pixel remains unchanged.",
            "categorical_sampling": "Nearest-neighbor sampling onto each frozen 20 m proposal grid; source products remain 30 m and no resolution gain is claimed.",
            "mtbs_affirmative": "dNBR6 classes 2-5; class 1 ambiguous; 0/6 outside, mask, or nonprocessing.",
            "ravg_affirmative": "CBI4 classes 2-4; class 1 unchanged; 0/9 outside or unmappable.",
            "baer_continuous": "Unthresholded dNBR median, interquartile range, and positive-change share by proposal state; no burned threshold.",
        "owner_review_effect": "Evidence may be shown to the owner with optical context in a later yes/no/uncertain review surface. This run records zero owner responses.",
        },
        "events": event_reports,
        "historical_review_context": {
            "units": 56,
            "burned": 6,
            "background": 0,
            "ignored": 50,
            "status": "immutable historical single-reviewer evidence; not a final exclusion decision under the owner-confirmed route",
            "spatial_join_performed": False,
        },
        "claim_boundaries": {
            "labels_promoted": False,
            "owner_responses_recorded": 0,
            "dataset_created": False,
            "split_created": False,
            "baseline_created": False,
            "model_created": False,
            "independent_ground_truth_claimed": False,
            "inter_rater_agreement_claimed": False,
            "field_validation_claimed": False,
            "official_operational_or_endorsed_status_claimed": False,
        },
        "decision": DECISION,
        "next_checkpoint": "Build the owner yes/no/uncertain review surface for all original 56 units, pairing each candidate with optical and permitted current-reference evidence. Keep no/uncertain excluded and gate every yes before prototype-label acceptance.",
        "warning": WARNING,
    }
    return report, previews


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for candidate in ("C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/segoeui.ttf"):
        if Path(candidate).is_file():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def _map_image(array: np.ndarray | None, kind: str, size: tuple[int, int]) -> Image.Image:
    if array is None:
        image = Image.new("RGB", size, "#172237")
        draw = ImageDraw.Draw(image)
        draw.text((30, size[1] // 2 - 14), "not available", fill="#a9b8ce", font=_font(22))
        return image
    if kind == "proposal":
        palette = np.array([[70, 125, 88], [209, 75, 62], [78, 91, 107], [25, 28, 36], [225, 160, 66]], dtype=np.uint8)
        rgb = palette[np.clip(array.astype(int), 0, 4)]
    elif kind == "mtbs":
        colors = {0:(15,22,32),1:(73,180,185),2:(250,222,78),3:(230,140,47),4:(177,36,33),5:(76,165,83),6:(120,120,120),255:(15,22,32)}
        rgb = np.zeros((*array.shape, 3), dtype=np.uint8)
        for value, color in colors.items(): rgb[array == value] = color
    else:
        colors = {0:(15,22,32),1:(36,139,141),2:(95,198,193),3:(249,220,67),4:(211,56,45),9:(150,150,150),255:(15,22,32)}
        rgb = np.zeros((*array.shape, 3), dtype=np.uint8)
        for value, color in colors.items(): rgb[array == value] = color
    image = Image.fromarray(rgb, mode="RGB")
    image.thumbnail(size, Image.Resampling.NEAREST)
    canvas = Image.new("RGB", size, "#0b1220")
    canvas.paste(image, ((size[0]-image.width)//2, (size[1]-image.height)//2))
    return canvas


def render_png(report: dict[str, Any], previews: list[dict[str, Any]], path: Path) -> None:
    canvas = Image.new("RGB", (1800, 1580), "#08111e")
    draw = ImageDraw.Draw(canvas)
    draw.text((60, 38), "BURNLENS  /  CURRENT OFFICIAL REFERENCE FITNESS", fill="#84d6b0", font=_font(24))
    draw.text((60, 82), "Seven products are useful review evidence. Zero labels move.", fill="#f2f5f9", font=_font(38))
    draw.text((60, 135), report["decision"], fill="#f1bb65", font=_font(23))
    y = 200
    event_by_name = {item["display_name"]: item for item in report["events"]}
    for preview in previews:
        event = event_by_name[preview["display_name"]]
        draw.rounded_rectangle((45, y, 1755, y+375), radius=18, fill="#111d30", outline="#31465f", width=2)
        draw.text((70, y+20), preview["display_name"], fill="#f2f5f9", font=_font(28))
        for index, (label, key, kind) in enumerate((("Frozen proposal", "proposal", "proposal"), ("Current MTBS dNBR6", "mtbs", "mtbs"), ("Current RAVG CBI4", "ravg", "ravg"))):
            x = 70 + index*500
            draw.text((x, y+62), label, fill="#b8c8d9", font=_font(18))
            canvas.paste(_map_image(preview[key], kind, (455, 245)), (x, y+95))
        cross = event["cross_program_categorical_agreement"]
        x = 1560
        if cross:
            total = sum(cross["overall_counts"].values())
            both = cross["overall_counts"]["both_affirmative"]
            draw.text((x, y+88), f"{100*both/total:.1f}%", fill="#84d6b0", font=_font(31))
            draw.text((x, y+128), "both affirmative", fill="#b8c8d9", font=_font(15))
            draw.text((x, y+178), f"{both:,}", fill="#f2f5f9", font=_font(26))
            draw.text((x, y+212), "proposal-grid pixels", fill="#b8c8d9", font=_font(15))
        else:
            draw.text((x, y+90), "RAVG +", fill="#f1bb65", font=_font(25))
            draw.text((x, y+125), "BAER dNBR", fill="#f1bb65", font=_font(25))
            draw.text((x, y+170), "no categorical", fill="#b8c8d9", font=_font(15))
            draw.text((x, y+193), "cross-program", fill="#b8c8d9", font=_font(15))
            draw.text((x, y+216), "confirmation", fill="#b8c8d9", font=_font(15))
        y += 400
    draw.rounded_rectangle((45, 1410, 1755, 1515), radius=15, fill="#2a2113", outline="#c28d3b", width=2)
    draw.text((70, 1432), "BAER boundary: thresholded Tepee BARC pixels remain private and excluded; Darlene delivered no classified BAER raster.", fill="#ffd693", font=_font(19))
    draw.text((70, 1470), WARNING, fill="#ffd693", font=_font(18))
    draw.text((55, 1540), f"TRACE  commit {report['git_source_commit'][:12]} / BurnLens {report['software_version']} / run {report['run_id']} / dataset none / model none", fill="#a9b8ce", font=_font(15))
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path, format="PNG", optimize=False)


def render_html(report: dict[str, Any], png_name: str, path: Path) -> None:
    rows = []
    for event in report["events"]:
        programs = ", ".join(item["program"] for item in event["products"])
        rows.append(f"<tr><td>{escape(event['display_name'])}</td><td>{escape(programs)}</td><td>{'yes' if event['categorical_cross_program_confirmation_available'] else 'no'}</td><td>{sum(event['proposal']['state_counts'].values()):,}</td></tr>")
    html = f"""<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><title>{REPORT_ID}</title><style>
body{{margin:0;background:#08111e;color:#eef3f8;font:16px/1.55 system-ui,sans-serif}}main{{max-width:1180px;margin:auto;padding:45px 24px 80px}}h1{{font-size:42px;line-height:1.1}}.hero{{box-sizing:border-box;width:100%;height:auto;border:1px solid #31465f;border-radius:12px}}.card{{box-sizing:border-box;max-width:100%;padding:18px;background:#111d30;border:1px solid #31465f;border-radius:12px;margin:16px 0}}.warning{{background:#2a2113;border-color:#c28d3b;color:#ffd693}}.table-wrap{{max-width:100%;overflow-x:auto}}table{{width:100%;min-width:720px;border-collapse:collapse}}th,td{{text-align:left;padding:10px;border-bottom:1px solid #31465f}}strong,code{{overflow-wrap:anywhere}}code{{color:#84d6b0}}a{{color:#84d6b0}}@media(max-width:520px){{h1{{font-size:34px}}}}
</style></head><body><main><p>BURNLENS / PHASE TWO / ISSUE #{TASK_ISSUE}</p><h1>Current bundles strengthen owner review, not labels.</h1><p class=\"card warning\">{escape(WARNING)}</p><img class=\"hero\" src=\"{escape(png_name)}\" alt=\"Frozen proposals beside current MTBS and RAVG categorical evidence for three fires\"><div class=\"card\"><strong>{escape(report['decision'])}</strong><p>Seven delivered products passed exact-byte, archive, metadata, raster, CRS, nodata, and class-domain inspection. Zero labels move: this checkpoint records zero owner decisions and changes zero proposal pixels.</p><p>The next surface reopens all 56 units for owner yes/no/uncertain decisions; it does not inherit historical exclusions.</p></div><h2>Event evidence</h2><div class=\"table-wrap\"><table><thead><tr><th>Event</th><th>Permitted evidence</th><th>MTBS/RAVG categorical comparison</th><th>Frozen pixels</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div><h2>Interpretation</h2><div class=\"card\"><p>MTBS classes 2-5 and RAVG CBI classes 2-4 are affirmative review evidence, not independent ground truth. Nearest-neighbor sampling preserves source categories and does not claim 20 m source resolution.</p><p>BAER dNBR remains continuous change context. Positive change is not a burned threshold. Thresholded legacy Tepee BARC is excluded from public output and promotion under its distribution restriction. The current Darlene BAER delivery contains no classified BARC or SBS raster.</p><p>RAVG is forest-calibrated and timing-sensitive. MTBS thresholds are analyst interpreted. No product establishes field validation.</p></div><h2>Next checkpoint</h2><div class=\"card\"><p>{escape(report['next_checkpoint'])}</p></div><p>Trace: source commit <code>{escape(report['git_source_commit'])}</code> · BurnLens <code>{report['software_version']}</code> · run <code>{escape(report['run_id'])}</code> · label schema <code>{escape(report['provenance']['label_schema_version'])}</code> · dataset/model none.</p></main></body></html>"""
    _write_lf(path, html)


def write_report(report: dict[str, Any], previews: list[dict[str, Any]], *, json_path: Path, html_path: Path, png_path: Path) -> None:
    _write_lf(json_path, json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    render_png(report, previews, png_path)
    render_html(report, png_path.name, html_path)
