"""Gate exact Green Ridge BAER, MTBS, and RAVG pixels as bounded evidence.

This module re-verifies the exact optical package and delivered reference
archive. It renders source-fitness evidence only: no candidate, owner response,
label, dataset, split, baseline, or model is created.
"""

from __future__ import annotations

from collections import Counter
from hashlib import sha256
from html import escape
import json
from pathlib import Path, PurePosixPath
import struct
from typing import Any
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import numpy as np
from PIL import Image, ImageDraw
import rasterio
from rasterio.io import MemoryFile
from rasterio.warp import Resampling, reproject

from .green_ridge_reference_delivery import inspect_delivery
from .green_ridge_source_fitness import (
    build_report as build_optical_report,
    _preview_dnbr,
    _preview_tci,
)
from .optical_pair_evidence import WARNING, _font, _write_utf8_lf


SOFTWARE_VERSION = "0.34.0"
REPORT_ID = "GREEN-RIDGE-REFERENCE-FITNESS-2026-001"
REPORT_VERSION = "green-ridge-reference-fitness-v0.1.0"
PROTOCOL_VERSION = "green-ridge-reference-fitness-protocol-v0.1.0"
TASK_ISSUE = 477
ARCHIVE_BYTES = 20_969_722
ARCHIVE_SHA256 = "63c072850dfc284e863a57c55b1c0defea315d988ac9f51a2c5bcb946b6d4843"
ARCHIVE_MEMBERS = 53
EVENT_ID = "OR4446712160520200817"
MAP_IDS = {"BAER": 10015623, "MTBS": 10021333, "RAVG": 10016049}
SOURCE_RECORD_ID = "SOURCE-2026-022"
TERMS_REVIEW_ID = "TERMS-2026-018"
ACCESS_RECORD_ID = "ACCESS-2026-013"

PRODUCTS = {
    "baer_dnbr": ("BAER", "_20200731_20200901_dnbr.tif", "continuous_change_context_only"),
    "mtbs_dnbr6": ("MTBS", "_20200715_20210718_dnbr6.tif", "categorical_owner_review_evidence"),
    "ravg_ba4": ("RAVG", "_20200929_rdnbr_ba4.tif", "forested_vegetation_effect_context"),
    "ravg_cc5": ("RAVG", "_20200929_rdnbr_cc5.tif", "forested_vegetation_effect_context"),
    "ravg_cbi4": ("RAVG", "_20200929_rdnbr_cbi4.tif", "categorical_owner_review_evidence"),
}

MTBS_CLASSES = {
    0: "background_or_nodata",
    1: "unburned_to_low_or_rapid_recovery",
    2: "low_severity",
    3: "moderate_severity",
    4: "high_severity",
    5: "increased_greenness",
    6: "nonprocessing_mask",
}
RAVG_CBI_CLASSES = {
    0: "outside_perimeter",
    1: "unchanged_not_proof_of_unburned",
    2: "low_severity",
    3: "moderate_severity",
    4: "high_severity",
    9: "unmappable",
}


class GreenRidgeReferenceFitnessError(RuntimeError):
    """Exact reference fitness failed closed."""


def _digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def _file_digest(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as source:
        while block := source.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def _find(archive: ZipFile, suffix: str) -> str:
    matches = [name for name in archive.namelist() if name.casefold().endswith(suffix.casefold())]
    if len(matches) != 1:
        raise GreenRidgeReferenceFitnessError(f"expected one archive member ending {suffix}; found {len(matches)}")
    return matches[0]


def _metadata_text(root: ET.Element, tag: str) -> str:
    matches = []
    for item in root.iter():
        if item.tag.split("}")[-1].casefold() == tag.casefold():
            value = " ".join("".join(item.itertext()).split())
            if value:
                matches.append(value)
    if len(matches) != 1:
        raise GreenRidgeReferenceFitnessError(f"expected one {tag} metadata value; found {len(matches)}")
    return matches[0]


def _inspect_metadata(archive: ZipFile, program: str) -> dict[str, Any]:
    member = _find(archive, f"/{program.casefold()}_or4446712160520200817_{MAP_IDS[program]}" + ({
        "BAER": "_20200731_20200901_metadata.xml",
        "MTBS": "_20200715_20210718_metadata.xml",
        "RAVG": "_20190925_20200929_metadata.xml",
    }[program]))
    data = archive.read(member)
    root = ET.fromstring(data)
    result = {
        "program": program,
        "member": member,
        "bytes": len(data),
        "sha256": _digest(data),
        "abstract": _metadata_text(root, "abstract"),
        "purpose": _metadata_text(root, "purpose"),
        "access_constraints": _metadata_text(root, "accconst"),
        "use_constraints": _metadata_text(root, "useconst"),
        "credit": _metadata_text(root, "datacred"),
        "distribution_liability": _metadata_text(root, "distliab"),
    }
    if program == "BAER":
        required = "Thresholded, preliminary severity estimates (BARC4 and BARC256) are only delivered to BAER teams."
        if required not in result["access_constraints"]:
            raise GreenRidgeReferenceFitnessError("BAER distribution restriction drifted")
    elif result["access_constraints"] != "None":
        raise GreenRidgeReferenceFitnessError(f"{program} access constraint drifted")
    if "reasonable and proper acknowledgement" not in result["use_constraints"]:
        raise GreenRidgeReferenceFitnessError(f"{program} acknowledgement requirement drifted")
    return result


def _inspect_raster(archive: ZipFile, member: str) -> tuple[dict[str, Any], dict[str, Any]]:
    data = archive.read(member)
    try:
        with MemoryFile(data) as memory, memory.open() as source:
            array = source.read(1)
            nodata = source.nodata
            valid = np.isfinite(array)
            if nodata is not None:
                valid &= array != nodata
            observed = array[valid]
            values, counts = np.unique(observed, return_counts=True)
            encoded_values, encoded_counts = np.unique(array[np.isfinite(array)], return_counts=True)
            profile = {
                "member": member,
                "bytes": len(data),
                "sha256": _digest(data),
                "driver": source.driver,
                "crs": source.crs.to_string() if source.crs else None,
                "width": source.width,
                "height": source.height,
                "band_count": source.count,
                "dtype": source.dtypes[0],
                "nodata": nodata,
                "resolution_m": [abs(source.transform.a), abs(source.transform.e)],
                "transform": list(source.transform)[:6],
                "bounds": list(source.bounds),
                "valid_pixels": int(observed.size),
                "nodata_pixels": int(array.size - observed.size),
                "native_value_domain": (
                    {str(int(value)): int(count) for value, count in zip(encoded_values, encoded_counts, strict=True)}
                    if len(encoded_values) <= 32 else None
                ),
                "valid_quantiles": (
                    None if len(values) <= 32 else {
                        name: round(float(value), 4)
                        for name, value in zip(
                            ("min", "p01", "p10", "p50", "p90", "p99", "max"),
                            np.percentile(observed, (0, 1, 10, 50, 90, 99, 100)), strict=True,
                        )
                    }
                ),
            }
            runtime = {
                "array": array,
                "transform": source.transform,
                "crs": source.crs,
                "nodata": nodata,
            }
    except rasterio.errors.RasterioError as error:
        raise GreenRidgeReferenceFitnessError(f"unreadable reference raster: {member}") from error
    if profile["crs"] != "EPSG:32610" or profile["resolution_m"] != [30.0, 30.0]:
        raise GreenRidgeReferenceFitnessError(f"reference grid drifted: {member}")
    return profile, runtime


def _sample(runtime: dict[str, Any], shape: tuple[int, int], transform: rasterio.Affine, *, continuous: bool) -> np.ndarray:
    fill = np.nan if continuous else 255
    dtype = np.float32 if continuous else np.uint8
    destination = np.full(shape, fill, dtype=dtype)
    reproject(
        source=runtime["array"], destination=destination,
        src_transform=runtime["transform"], src_crs=runtime["crs"], src_nodata=runtime["nodata"],
        dst_transform=transform, dst_crs="EPSG:32610", dst_nodata=fill,
        resampling=Resampling.nearest,
    )
    return destination


def _shapefile_record_count(data: bytes) -> int:
    if len(data) < 100 or struct.unpack(">i", data[:4])[0] != 9994:
        raise GreenRidgeReferenceFitnessError("invalid shapefile header")
    position = 100
    count = 0
    while position < len(data):
        if position + 8 > len(data):
            raise GreenRidgeReferenceFitnessError("truncated shapefile record header")
        length = struct.unpack(">i", data[position + 4:position + 8])[0] * 2
        position += 8 + length
        count += 1
    if position != len(data):
        raise GreenRidgeReferenceFitnessError("invalid shapefile record length")
    return count


def _vector_contract(archive: ZipFile, program: str) -> dict[str, Any]:
    prefix = {"BAER": "_20200731_20200901_burn_area", "MTBS": "_20200715_20210718_burn_area", "RAVG": "_20190925_20200929_burn_area"}[program]
    parts = {}
    for extension in (".shp", ".shx", ".dbf", ".prj"):
        member = _find(archive, prefix + extension)
        data = archive.read(member)
        parts[extension[1:]] = {"member": member, "bytes": len(data), "sha256": _digest(data)}
        if extension == ".shp":
            bbox = struct.unpack("<4d", data[36:68])
            parts[extension[1:]]["bbox"] = [round(item, 9) for item in bbox]
            parts[extension[1:]]["record_count"] = _shapefile_record_count(data)
        if extension == ".prj" and "UTM_Zone_10N" not in data.decode("ascii", "replace"):
            raise GreenRidgeReferenceFitnessError(f"{program} boundary CRS drifted")
    return {"program": program, "parts": parts}


def _counts(array: np.ndarray, mask: np.ndarray) -> dict[str, int]:
    values, counts = np.unique(array[mask], return_counts=True)
    return {str(int(value)): int(count) for value, count in zip(values, counts, strict=True)}


def build_report(
    *, package: Path, plan_path: Path, archive_path: Path,
    generated_at_utc: str, run_id: str, git_source_commit: str,
) -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    optical, previews = build_optical_report(
        package=package, plan_path=plan_path, generated_at_utc=generated_at_utc,
        run_id=run_id + "-optical-reverification", git_source_commit=git_source_commit,
    )
    preflight = inspect_delivery([archive_path])
    if archive_path.stat().st_size != ARCHIVE_BYTES or _file_digest(archive_path) != ARCHIVE_SHA256:
        raise GreenRidgeReferenceFitnessError("delivered archive identity mismatch")
    if preflight["archives"][0]["member_count"] != ARCHIVE_MEMBERS:
        raise GreenRidgeReferenceFitnessError("delivered archive member count mismatch")
    shape = previews["dnbr"].shape
    transform = rasterio.Affine(*optical["products"][0]["rasters"]["B04"]["crop_transform"])
    boundary = previews["boundary_mask20"]
    if boundary.shape != shape or int(boundary.sum()) != 44_110:
        raise GreenRidgeReferenceFitnessError("optical boundary grid drifted")

    with ZipFile(archive_path) as archive:
        names = archive.namelist()
        restricted = [name for name in names if any(token in PurePosixPath(name).stem.casefold() for token in ("barc4", "barc256", "_sbs"))]
        if restricted:
            raise GreenRidgeReferenceFitnessError("restricted BAER classified product unexpectedly delivered")
        metadata = [_inspect_metadata(archive, program) for program in ("BAER", "MTBS", "RAVG")]
        vectors = [_vector_contract(archive, program) for program in ("BAER", "MTBS", "RAVG")]
        rasters: list[dict[str, Any]] = []
        runtime: dict[str, dict[str, Any]] = {}
        for name in names:
            if name.casefold().endswith(('.tif', '.tiff')):
                profile, values = _inspect_raster(archive, name)
                rasters.append(profile)
                runtime[name] = values
        selected: dict[str, dict[str, Any]] = {}
        sampled: dict[str, np.ndarray] = {}
        for key, (program, suffix, role) in PRODUCTS.items():
            member = _find(archive, suffix)
            profile = next(item for item in rasters if item["member"] == member)
            selected[key] = {"program": program, "role": role, **profile}
            sampled[key] = _sample(runtime[member], shape, transform, continuous=key == "baer_dnbr")

    mtbs = sampled["mtbs_dnbr6"]
    ravg = sampled["ravg_cbi4"]
    mtbs_affirmative = boundary & np.isin(mtbs, (2, 3, 4))
    ravg_affirmative = boundary & np.isin(ravg, (2, 3, 4))
    both = mtbs_affirmative & ravg_affirmative
    any_affirmative = mtbs_affirmative | ravg_affirmative
    valid_pair = previews["dnbr_valid"]
    evidence = {
        "optical_boundary_pixels": int(boundary.sum()),
        "optical_pair_valid_pixels": int(valid_pair.sum()),
        "mtbs_dnbr6_on_optical_boundary": _counts(mtbs, boundary),
        "ravg_cbi4_on_optical_boundary": _counts(ravg, boundary),
        "ravg_ba4_on_optical_boundary": _counts(sampled["ravg_ba4"], boundary),
        "ravg_cc5_on_optical_boundary": _counts(sampled["ravg_cc5"], boundary),
        "both_programs_affirmative_pixels": int(both.sum()),
        "either_program_affirmative_pixels": int(any_affirmative.sum()),
        "both_programs_affirmative_and_optical_valid_pixels": int((both & valid_pair).sum()),
        "categorical_sampling": "nearest neighbor from native 30 m onto the verified 20 m optical grid; no resolution gain claimed",
        "mtbs_class_semantics": {str(key): value for key, value in MTBS_CLASSES.items()},
        "ravg_cbi_class_semantics": {str(key): value for key, value in RAVG_CBI_CLASSES.items()},
        "background_finding": "Neither program supplies affirmative background truth. MTBS class 1 and RAVG class 1 may include burned, low-effect, recovered, or model-limited areas.",
    }
    grid_groups = Counter(tuple(item["transform"]) for item in rasters)
    baer_transform = selected["baer_dnbr"]["transform"]
    mtbs_transform = selected["mtbs_dnbr6"]["transform"]
    ravg_transform = selected["ravg_cbi4"]["transform"]
    if baer_transform != mtbs_transform:
        raise GreenRidgeReferenceFitnessError("BAER and MTBS grids unexpectedly differ")
    ravg_offset = [ravg_transform[2] - baer_transform[2], ravg_transform[5] - baer_transform[5]]
    if ravg_offset != [30.0, 30.0]:
        raise GreenRidgeReferenceFitnessError("RAVG grid offset drifted")
    vector_by_program = {item["program"]: item for item in vectors}
    baer_parts = vector_by_program["BAER"]["parts"]
    mtbs_parts = vector_by_program["MTBS"]["parts"]
    ravg_parts = vector_by_program["RAVG"]["parts"]
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
        "application_version": None,
        "event": {"event_group_id": optical["event"]["event_group_id"], "event_id": EVENT_ID, "fire_name": "GREEN RIDGE 0684 CS", "map_ids": MAP_IDS},
        "trace": {
            "source_record_id": SOURCE_RECORD_ID, "terms_review_id": TERMS_REVIEW_ID,
            "access_record_id": ACCESS_RECORD_ID, "label_schema_version": optical["label_schema_version"],
            "dataset_version": None, "split_version": None, "baseline_version": None, "model_version": None,
            "optical_acquisition_run_id": optical["package"]["acquisition_run_id"],
            "reference_request_run_id": "BL-2026-07-19-green-ridge-reference-request-r001",
        },
        "archive": {**preflight["archives"][0], "exact_contract_pass": True, "restricted_baer_classified_members": [], "private_delivery_route_retained": False},
        "metadata": metadata,
        "boundary_vectors": vectors,
        "native_rasters": rasters,
        "selected_evidence_products": selected,
        "grid_relationship": {
            "crs": "EPSG:32610", "resolution_m": 30,
            "distinct_native_transforms": len(grid_groups),
            "baer_mtbs_same_grid": True,
            "ravg_offset_from_baer_mtbs_m": ravg_offset,
        },
        "boundary_relationship": {
            "all_programs_same_bbox_and_crs": all(
                item["parts"]["shp"]["bbox"] == baer_parts["shp"]["bbox"]
                and item["parts"]["prj"]["sha256"] == baer_parts["prj"]["sha256"]
                for item in vector_by_program.values()
            ),
            "baer_mtbs_geometry_bytes_identical": all(
                baer_parts[extension]["sha256"] == mtbs_parts[extension]["sha256"]
                for extension in ("shp", "shx", "prj")
            ),
            "ravg_geometry_bytes_differ": any(
                ravg_parts[extension]["sha256"] != baer_parts[extension]["sha256"]
                for extension in ("shp", "shx")
            ),
            "attribute_tables_program_specific": len({
                baer_parts["dbf"]["sha256"], mtbs_parts["dbf"]["sha256"], ravg_parts["dbf"]["sha256"]
            }) == 3,
        },
        "optical_reverification": {
            "source_report_id": optical["report_id"],
            "source_package_id": optical["package"]["package_id"],
            "boundary_pixels": optical["pair_quality_inside_full_boundary"]["pixel_count_inside_full_boundary"],
            "pair_eligible_percent": next(
                item["percent"] for item in optical["pair_quality_inside_full_boundary"]["states"]
                if item["state"] == "eligible-comparison"
            ),
            "registration_summary": optical["registration"]["summary"],
        },
        "evidence_comparison": evidence,
        "terms_and_roles": {
            "resolved_for_this_checkpoint": True,
            "baer": "Only reflectance and unthresholded continuous dNBR/RdNBR are present. They are preliminary change context, not a class or label. Restricted BARC4/BARC256/SBS pixels are absent.",
            "mtbs": "Analyst-interpreted thematic severity evidence with acknowledgement required; not independent ground truth or field validation.",
            "ravg": "Forest-calibrated modeled vegetation-effect evidence with acknowledgement and modified-Copernicus notice required; applicability and timing limits bind.",
            "attribution": "Monitoring Trends in Burn Severity Project (U.S. Geological Survey and USDA Forest Service); USDA Forest Service; ESA (Contains modified Copernicus Sentinel data 2020); Contains modified Copernicus Sentinel data 2020, accessed through CDSE.",
        },
        "fitness_decision": {
            "reference_pixels": "PASS_EXACT_GREEN_RIDGE_REFERENCE_SOURCE_FITNESS",
            "burned_candidate_route": "OPEN_FOR_SEPARATE_BOUNDED_PROPOSAL_AND_OWNER_REVIEW",
            "background_candidate_route": "BLOCKED_PENDING_AFFIRMATIVE_BACKGROUND_EVIDENCE",
            "checkpoint": "ACCEPT_REFERENCE_PIXELS_AS_BOUNDED_EVIDENCE_DEFER_CANDIDATES_LABELS_DATASET_MODEL",
        },
        "claims": {
            "proven": [
                "The exact delivered archive, metadata, native raster grids, nodata, class domains, and boundary components passed deterministic inspection.",
                "MTBS dNBR6 and RAVG CBI4 provide independently traceable categorical burned-candidate evidence after nearest-neighbor comparison on the verified optical grid.",
                "The BAER delivery contains no restricted classified BARC or SBS raster.",
            ],
            "not_proven": [
                "No reference product is independent ground truth, affirmative background truth, or field validation for BurnLens.",
                "No candidate, owner decision, label, dataset, split, baseline, model, metric, official status, endorsement, or operational readiness is created.",
            ],
        },
        "warning": WARNING,
    }
    previews.update(sampled)
    return report, previews


def _class_image(array: np.ndarray, mask: np.ndarray, palette: dict[int, tuple[int, int, int]], size: tuple[int, int]) -> Image.Image:
    rgb = np.zeros((*array.shape, 3), dtype=np.uint8)
    rgb[:] = (12, 25, 22)
    for value, color in palette.items():
        rgb[(array == value) & mask] = color
    image = Image.fromarray(rgb, mode="RGB")
    image.thumbnail(size, Image.Resampling.NEAREST)
    canvas = Image.new("RGB", size, "#0c1916")
    canvas.paste(image, ((size[0] - image.width) // 2, (size[1] - image.height) // 2))
    return canvas


def render_png(report: dict[str, Any], previews: dict[str, np.ndarray], path: Path) -> None:
    canvas = Image.new("RGB", (1800, 1260), "#07110f")
    draw = ImageDraw.Draw(canvas)
    draw.text((60, 38), "BURNLENS  /  GREEN RIDGE REFERENCE FITNESS", fill="#b9d8cf", font=_font(21))
    draw.text((60, 76), "Exact reference pixels pass; candidates and labels do not.", fill="#eef7f3", font=_font(31))
    draw.text((60, 128), report["fitness_decision"]["checkpoint"], fill="#ffca73", font=_font(18))
    boundary = previews["boundary_mask20"]
    panels = [
        ("PRE OPTICAL", _preview_tci(previews["pre_tci"], previews["pre_mask"], (520, 315))),
        ("POST OPTICAL", _preview_tci(previews["post_tci"], previews["post_mask"], (520, 315))),
        ("CONTINUOUS dNBR", _preview_dnbr(previews["dnbr"], previews["dnbr_valid"], (520, 315))),
        ("MTBS dNBR6", _class_image(previews["mtbs_dnbr6"], boundary, {1:(160,168,145),2:(244,213,112),3:(235,144,70),4:(190,63,45),5:(80,170,100)}, (520,315))),
        ("RAVG CBI4", _class_image(previews["ravg_cbi4"], boundary, {1:(160,168,145),2:(244,213,112),3:(235,144,70),4:(190,63,45)}, (520,315))),
        ("RAVG BASAL AREA 4", _class_image(previews["ravg_ba4"], boundary, {1:(160,168,145),2:(244,213,112),3:(235,144,70),4:(190,63,45)}, (520,315))),
    ]
    for index, (label, image) in enumerate(panels):
        column, row = index % 3, index // 3
        x, y = 60 + column * 575, 180 + row * 405
        draw.rounded_rectangle((x, y, x + 535, y + 375), radius=16, fill="#0e1d1a", outline="#315b50", width=2)
        draw.text((x + 18, y + 14), label, fill="#eef7f3", font=_font(18))
        canvas.paste(image, (x + 8, y + 48))
    evidence = report["evidence_comparison"]
    metrics = [
        (f"{evidence['both_programs_affirmative_pixels']:,}", "MTBS + RAVG affirmative"),
        (f"{evidence['either_program_affirmative_pixels']:,}", "either program affirmative"),
        ("2 native grids", "RAVG offset 30 m east/north"),
        ("0", "background truth / labels"),
    ]
    for index, (value, label) in enumerate(metrics):
        x = 60 + index * 430
        draw.rounded_rectangle((x, 1015, x + 395, 1128), radius=14, fill="#0e1d1a", outline="#315b50", width=2)
        draw.text((x + 20, 1035), value, fill="#78e0bd", font=_font(27))
        draw.text((x + 20, 1082), label, fill="#b9d8cf", font=_font(14))
    draw.rounded_rectangle((60, 1152, 1740, 1218), radius=14, fill="#261f12", outline="#be8a36", width=2)
    draw.text((82, 1168), WARNING, fill="#ffd997", font=_font(15))
    draw.text((60, 1232), f"TRACE commit {report['git_source_commit'][:12]} / run {report['run_id']} / BurnLens {SOFTWARE_VERSION} / dataset-model none", fill="#b9d8cf", font=_font(13))
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path, format="PNG", optimize=False)


def render_html(report: dict[str, Any], png_name: str, path: Path) -> None:
    evidence = report["evidence_comparison"]
    rows = "".join(
        f"<tr><td>{escape(item['program'])}</td><td><code>{escape(PurePosixPath(item['member']).name)}</code></td><td>{item['width']}×{item['height']}</td><td>{escape(str(item['nodata']))}</td><td>{escape(str(item['native_value_domain'] or 'continuous'))}</td></tr>"
        for item in report["selected_evidence_products"].values()
    )
    html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Green Ridge reference fitness</title><style>
body{{margin:0;background:#07110f;color:#eef7f3;font:16px/1.55 system-ui,sans-serif}}main{{max-width:1200px;margin:auto;padding:32px}}h1{{font-size:clamp(2rem,5vw,4rem);line-height:1.02}}.card{{background:#0e1d1a;border:1px solid #315b50;border-radius:16px;padding:20px;margin:18px 0}}.warn{{background:#261f12;border-color:#be8a36;color:#ffd997}}img{{width:100%;height:auto;border-radius:16px}}table{{width:100%;border-collapse:collapse}}th,td{{text-align:left;padding:10px;border-bottom:1px solid #315b50;vertical-align:top}}code{{overflow-wrap:anywhere}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px}}.metric strong{{display:block;font-size:2rem;color:#78e0bd}}
</style></head><body><main><p>BURNLENS / PHASE TWO / ISSUE #477</p><h1>Reference pixels pass; candidates and labels do not.</h1><div class="card warn">{escape(report['warning'])}</div><img src="{escape(png_name)}" width="1800" height="1260" alt="Actual Green Ridge optical, MTBS, and RAVG evidence"><div class="grid"><div class="card metric"><strong>{evidence['both_programs_affirmative_pixels']:,}</strong>MTBS and RAVG affirmative pixels</div><div class="card metric"><strong>{evidence['either_program_affirmative_pixels']:,}</strong>either program affirmative</div><div class="card metric"><strong>44,110</strong>verified optical boundary pixels</div><div class="card metric"><strong>0</strong>labels or background truth</div></div><h2>Exact selected products</h2><div class="card"><table><thead><tr><th>Program</th><th>Member</th><th>Native grid</th><th>Nodata</th><th>Domain</th></tr></thead><tbody>{rows}</tbody></table><p>All categorical comparisons use nearest-neighbor sampling from native 30 m to the verified 20 m optical grid. No resolution gain is claimed.</p></div><h2>Source roles</h2><div class="card"><p><strong>MTBS:</strong> classes 2–4 are categorical burned-candidate evidence; class 1 is ambiguous, not background truth.</p><p><strong>RAVG:</strong> CBI classes 2–4 are forest-calibrated burned-candidate evidence; unchanged class 1 is ambiguous outside its model and timing limits.</p><p><strong>BAER:</strong> only unthresholded continuous change context is present. Restricted classified BARC/SBS rasters are absent.</p></div><h2>Gate result</h2><div class="card"><p><strong>{escape(report['fitness_decision']['checkpoint'])}</strong></p><p>Burned-candidate proposal may proceed only as a separate bounded checkpoint with actual optical/reference evidence and owner yes/no/uncertain review. Affirmative background evidence remains unresolved.</p></div><div class="card warn"><p>{escape(report['terms_and_roles']['attribution'])}</p><p>No independent ground truth, field validation, official status, endorsement, operational readiness, dataset, split, baseline, model, or accuracy claim exists.</p></div><p>Trace: commit <code>{escape(report['git_source_commit'])}</code> · BurnLens <code>{SOFTWARE_VERSION}</code> · run <code>{escape(report['run_id'])}</code> · label schema <code>{escape(report['trace']['label_schema_version'])}</code> · dataset/model none.</p></main></body></html>"""
    _write_utf8_lf(path, html)


def write_outputs(report: dict[str, Any], previews: dict[str, np.ndarray], directory: Path) -> dict[str, Path]:
    directory.mkdir(parents=True, exist_ok=True)
    paths = {
        "json": directory / f"{REPORT_ID}.json",
        "html": directory / f"{REPORT_ID}.html",
        "png": directory / f"{REPORT_ID}.png",
    }
    _write_utf8_lf(paths["json"], json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    render_png(report, previews, paths["png"])
    render_html(report, paths["png"].name, paths["html"])
    return paths
