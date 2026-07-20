"""Gate exact Grandview BAER, MTBS, and RAVG pixels as bounded evidence.

The exact optical package and official delivery are re-verified. RAVG is
rendered only as model-limited context because the delivered source warns that
much of this event has sparse to no pre-fire tree cover. No candidate, label,
dataset, split, baseline, or model is created.
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

from .grandview_reference_delivery import inspect_delivery
from .grandview_source_fitness import (
    build_report as build_optical_report,
    _preview_dnbr,
    _preview_tci,
)
from .green_ridge_reference_fitness import (
    GreenRidgeReferenceFitnessError,
    _class_image,
    _digest,
    _file_digest,
    _find,
    _inspect_raster,
    _metadata_text,
    _sample,
    _shapefile_record_count,
)
from .optical_pair_evidence import WARNING, _font, _write_utf8_lf


SOFTWARE_VERSION = "0.40.0"
REPORT_ID = "GRANDVIEW-REFERENCE-FITNESS-2026-001"
REPORT_VERSION = "grandview-reference-fitness-v0.1.0"
PROTOCOL_VERSION = "grandview-reference-fitness-protocol-v0.1.0"
TASK_ISSUE = 499
ARCHIVE_BYTES = 22_076_790
ARCHIVE_SHA256 = "ea30fe613931d9b90c1405a653ac01fe6bfaa7ee80f3ed02480422271ff874bf"
ARCHIVE_MEMBERS = 53
EVENT_ID = "OR4446612140020210711"
MAP_IDS = {"BAER": 10019092, "MTBS": 10023989, "RAVG": 10019464}
SOURCE_RECORD_ID = "SOURCE-2026-026"
TERMS_REVIEW_ID = "TERMS-2026-022"
ACCESS_RECORD_ID = "ACCESS-2026-016"

PRODUCTS = {
    "baer_dnbr": ("BAER", "_20210711_20210718_dnbr.tif", "preliminary_continuous_change_context_only"),
    "mtbs_dnbr6": ("MTBS", "_20210702_20210718_dnbr6.tif", "categorical_owner_review_evidence"),
    "ravg_ba4": ("RAVG", "_20200810_20210815_rdnbr_ba4.tif", "sparse_cover_model_limited_context_only"),
    "ravg_cc5": ("RAVG", "_20200810_20210815_rdnbr_cc5.tif", "sparse_cover_model_limited_context_only"),
    "ravg_cbi4": ("RAVG", "_20200810_20210815_rdnbr_cbi4.tif", "sparse_cover_model_limited_context_only"),
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
    2: "low_modeled_effect",
    3: "moderate_modeled_effect",
    4: "high_modeled_effect",
    9: "unmappable",
}


class GrandviewReferenceFitnessError(GreenRidgeReferenceFitnessError):
    """Exact Grandview reference fitness failed closed."""


def _inspect_metadata(archive: ZipFile, program: str) -> dict[str, Any]:
    stem = f"/{program.casefold()}_{EVENT_ID.casefold()}_{MAP_IDS[program]}" + ({
        "BAER": "_20210711_20210718_metadata.xml",
        "MTBS": "_20210702_20210718_metadata.xml",
        "RAVG": "_20200810_20210815_metadata.xml",
    }[program])
    member = _find(archive, stem)
    data = archive.read(member)
    root = ET.fromstring(data)
    iso_member = _find(archive, stem.replace("_metadata.xml", "_iso_metadata.xml"))
    iso_data = archive.read(iso_member)
    iso_root = ET.fromstring(iso_data)
    iso_text = " ".join(" ".join(iso_root.itertext()).split())
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
        "iso_metadata": {
            "member": iso_member,
            "bytes": len(iso_data),
            "sha256": _digest(iso_data),
            "xml_root": iso_root.tag.split("}")[-1],
            "access_and_use_language_present": (
                "reasonable and proper acknowledgement" in iso_text
                and (program != "BAER" or "BARC4 and BARC256" in iso_text)
            ),
        },
    }
    if program == "BAER":
        required = "Thresholded, preliminary severity estimates (BARC4 and BARC256) are only delivered to BAER teams."
        if required not in result["access_constraints"]:
            raise GrandviewReferenceFitnessError("BAER distribution restriction drifted")
        if "preliminary/draft data" not in result["use_constraints"]:
            raise GrandviewReferenceFitnessError("BAER preliminary-use limitation drifted")
    elif result["access_constraints"] != "None":
        raise GrandviewReferenceFitnessError(f"{program} access constraint drifted")
    if "reasonable and proper acknowledgement" not in result["use_constraints"]:
        raise GrandviewReferenceFitnessError(f"{program} acknowledgement requirement drifted")
    if not result["iso_metadata"]["access_and_use_language_present"]:
        raise GrandviewReferenceFitnessError(f"{program} ISO constraint language drifted")
    return result


def _dbf_records(data: bytes) -> list[dict[str, str]]:
    if len(data) < 33:
        raise GrandviewReferenceFitnessError("truncated DBF header")
    record_count = struct.unpack("<I", data[4:8])[0]
    header_bytes = struct.unpack("<H", data[8:10])[0]
    record_bytes = struct.unpack("<H", data[10:12])[0]
    fields: list[tuple[str, int]] = []
    position = 32
    while position < header_bytes and data[position] != 13:
        descriptor = data[position:position + 32]
        if len(descriptor) != 32:
            raise GrandviewReferenceFitnessError("truncated DBF field descriptor")
        name = descriptor[:11].split(b"\0", 1)[0].decode("ascii", "strict")
        fields.append((name, descriptor[16]))
        position += 32
    rows: list[dict[str, str]] = []
    for index in range(record_count):
        start = header_bytes + index * record_bytes
        record = data[start:start + record_bytes]
        if len(record) != record_bytes:
            raise GrandviewReferenceFitnessError("truncated DBF record")
        if record[:1] == b"*":
            continue
        offset = 1
        row: dict[str, str] = {}
        for name, width in fields:
            row[name] = record[offset:offset + width].decode("cp1252", "replace").strip()
            offset += width
        rows.append(row)
    return rows


def _vector_contract(archive: ZipFile, program: str) -> dict[str, Any]:
    prefix = {
        "BAER": "_20210711_20210718_burn_area",
        "MTBS": "_20210702_20210718_burn_area",
        "RAVG": "_20200810_20210815_burn_area",
    }[program]
    parts: dict[str, Any] = {}
    record: dict[str, str] | None = None
    for extension in (".shp", ".shx", ".dbf", ".prj"):
        member = _find(archive, prefix + extension)
        data = archive.read(member)
        parts[extension[1:]] = {"member": member, "bytes": len(data), "sha256": _digest(data)}
        if extension == ".shp":
            parts["shp"]["bbox"] = [round(item, 9) for item in struct.unpack("<4d", data[36:68])]
            parts["shp"]["record_count"] = _shapefile_record_count(data)
        elif extension == ".prj" and "UTM_Zone_10N" not in data.decode("ascii", "replace"):
            raise GrandviewReferenceFitnessError(f"{program} boundary CRS drifted")
        elif extension == ".dbf":
            records = _dbf_records(data)
            if len(records) != 1:
                raise GrandviewReferenceFitnessError(f"{program} expected one DBF record")
            record = records[0]
    if record is None:
        raise GrandviewReferenceFitnessError(f"{program} DBF record absent")
    expected = {"EVENT_ID": EVENT_ID, "MAP_ID": str(MAP_IDS[program]), "MAP_PROG": program, "INCID_NAME": "GRANDVIEW 0558 OD"}
    if any(record.get(key) != value for key, value in expected.items()):
        raise GrandviewReferenceFitnessError(f"{program} delivered attribute identity mismatch")
    if program == "RAVG":
        required = "Much of this burned area has very sparse to no pre-fire tree cover."
        if required not in record.get("COMMENT", ""):
            raise GrandviewReferenceFitnessError("RAVG sparse-cover warning absent from delivered attributes")
    return {"program": program, "parts": parts, "attributes": record}


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
        raise GrandviewReferenceFitnessError("delivered archive identity mismatch")
    if preflight["archives"][0]["member_count"] != ARCHIVE_MEMBERS:
        raise GrandviewReferenceFitnessError("delivered archive member count mismatch")
    shape = previews["dnbr"].shape
    transform = rasterio.Affine(*optical["products"][0]["rasters"]["B04"]["crop_transform"])
    boundary = previews["boundary_mask20"]
    if boundary.shape != shape or int(boundary.sum()) != 62_588:
        raise GrandviewReferenceFitnessError("optical boundary grid drifted")

    with ZipFile(archive_path) as archive:
        names = archive.namelist()
        restricted = [name for name in names if any(token in PurePosixPath(name).stem.casefold() for token in ("barc4", "barc256", "_sbs"))]
        if restricted:
            raise GrandviewReferenceFitnessError("restricted BAER classified product unexpectedly delivered")
        metadata = [_inspect_metadata(archive, program) for program in ("BAER", "MTBS", "RAVG")]
        vectors = [_vector_contract(archive, program) for program in ("BAER", "MTBS", "RAVG")]
        rasters: list[dict[str, Any]] = []
        runtime: dict[str, dict[str, Any]] = {}
        for name in names:
            if name.casefold().endswith((".tif", ".tiff")):
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
    mtbs_increased_green = boundary & (mtbs == 5)
    mtbs_covered = boundary & (mtbs != 255)
    ravg_modeled_effect = boundary & np.isin(ravg, (2, 3, 4))
    valid_pair = previews["dnbr_valid"]
    evidence = {
        "optical_boundary_pixels": int(boundary.sum()),
        "optical_pair_valid_pixels": int(valid_pair.sum()),
        "mtbs_dnbr6_on_optical_boundary": _counts(mtbs, boundary),
        "ravg_cbi4_on_optical_boundary": _counts(ravg, boundary),
        "ravg_ba4_on_optical_boundary": _counts(sampled["ravg_ba4"], boundary),
        "ravg_cc5_on_optical_boundary": _counts(sampled["ravg_cc5"], boundary),
        "mtbs_affirmative_pixels": int(mtbs_affirmative.sum()),
        "mtbs_reference_covered_pixels": int(mtbs_covered.sum()),
        "mtbs_reference_uncovered_pixels": int((boundary & ~mtbs_covered).sum()),
        "mtbs_reference_coverage_percent": round(100 * float(mtbs_covered.sum()) / float(boundary.sum()), 4),
        "mtbs_affirmative_percent_of_covered": round(100 * float(mtbs_affirmative.sum()) / float(mtbs_covered.sum()), 4),
        "mtbs_affirmative_and_optical_valid_pixels": int((mtbs_affirmative & valid_pair).sum()),
        "mtbs_increased_greenness_pixels": int(mtbs_increased_green.sum()),
        "mtbs_affirmative_with_ravg_modeled_effect_pixels": int((mtbs_affirmative & ravg_modeled_effect).sum()),
        "ravg_modeled_effect_pixels_context_only": int(ravg_modeled_effect.sum()),
        "categorical_sampling": "nearest neighbor from native 30 m onto the verified 20 m optical grid; no resolution gain claimed",
        "mtbs_class_semantics": {str(key): value for key, value in MTBS_CLASSES.items()},
        "ravg_cbi_class_semantics": {str(key): value for key, value in RAVG_CBI_CLASSES.items()},
        "ravg_fitness_limit": "The delivered RAVG record warns that much of this event has sparse to no pre-fire tree cover. RAVG pixels are context only and do not independently qualify any candidate.",
        "background_finding": "No product supplies affirmative background truth. MTBS class 1 and RAVG class 1 can include burned, low-effect, recovered, or model-limited areas; outside-perimeter class 0 is nodata, not verified background.",
    }
    grid_groups = Counter(tuple(item["transform"]) for item in rasters)
    transform_by_key = {key: selected[key]["transform"] for key in selected}
    vector_by_program = {item["program"]: item for item in vectors}
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
        "event": {"event_group_id": optical["event"]["event_group_id"], "event_id": EVENT_ID, "fire_name": "GRANDVIEW 0558 OD", "map_ids": MAP_IDS},
        "trace": {
            "source_record_id": SOURCE_RECORD_ID, "terms_review_id": TERMS_REVIEW_ID,
            "access_record_id": ACCESS_RECORD_ID, "label_schema_version": optical["label_schema_version"],
            "dataset_version": None, "split_version": None, "baseline_version": None, "model_version": None,
            "optical_acquisition_run_id": optical["package"]["acquisition_run_id"],
            "reference_request_run_id": "BL-2026-07-20-grandview-reference-request-r001",
            "reference_delivery_run_id": "BL-2026-07-20-grandview-reference-delivery-r001",
        },
        "archive": {**preflight["archives"][0], "exact_contract_pass": True, "restricted_baer_classified_members": [], "private_delivery_route_retained": False},
        "metadata": metadata,
        "boundary_vectors": vectors,
        "native_rasters": rasters,
        "selected_evidence_products": selected,
        "grid_relationship": {
            "crs": "EPSG:32610", "resolution_m": 30,
            "distinct_native_transforms": len(grid_groups),
            "selected_transforms": transform_by_key,
            "all_native_pixels_sampled_without_interpolation": True,
        },
        "boundary_relationship": {
            "all_programs_same_bbox_and_crs": len({tuple(item["parts"]["shp"]["bbox"]) for item in vectors}) == 1
            and len({item["parts"]["prj"]["sha256"] for item in vectors}) == 1,
            "geometry_hashes": {program: vector_by_program[program]["parts"]["shp"]["sha256"] for program in ("BAER", "MTBS", "RAVG")},
            "attribute_tables_program_specific": len({vector_by_program[p]["parts"]["dbf"]["sha256"] for p in ("BAER", "MTBS", "RAVG")}) == 3,
        },
        "optical_reverification": {
            "source_report_id": optical["report_id"],
            "source_package_id": optical["package"]["package_id"],
            "boundary_pixels": optical["pair_quality_inside_full_boundary"]["pixel_count_inside_full_boundary"],
            "registration_summary": optical["registration"]["summary"],
        },
        "evidence_comparison": evidence,
        "terms_and_roles": {
            "resolved_for_this_checkpoint": True,
            "baer": "Only reflectance and unthresholded continuous dNBR/RdNBR are present. They are preliminary change context, not a class or label. Restricted BARC4/BARC256/SBS pixels are absent.",
            "mtbs": "Analyst-interpreted thematic severity evidence with acknowledgement required; classes 2-4 may support candidate proposal but are not independent ground truth or field validation.",
            "ravg": "Forest-calibrated modeled vegetation-effect context only. The exact sparse/non-tree warning prevents RAVG from independently supporting a candidate for this event.",
            "attribution": "Monitoring Trends in Burn Severity Project (U.S. Geological Survey and USDA Forest Service); USDA Forest Service; ESA (Contains modified Copernicus Sentinel data 2021); Contains modified Copernicus Sentinel data 2021, accessed through CDSE.",
        },
        "fitness_decision": {
            "reference_pixels": "PASS_EXACT_GRANDVIEW_REFERENCE_SOURCE_FITNESS_WITH_RAVG_LIMIT",
            "burned_candidate_route": "OPEN_FOR_SEPARATE_MTBS_BACKED_PROPOSAL_AND_OWNER_REVIEW",
            "background_candidate_route": "BLOCKED_PENDING_AFFIRMATIVE_BACKGROUND_EVIDENCE",
            "checkpoint": "ACCEPT_MTBS_AS_BOUNDED_EVIDENCE_RAVG_AS_LIMITED_CONTEXT_DEFER_CANDIDATES_LABELS_DATASET_MODEL",
        },
        "claims": {
            "proven": [
                "The exact delivered archive, metadata, native grids, nodata, class domains, and boundary components passed deterministic inspection.",
                "MTBS dNBR6 provides traceable categorical burned-candidate evidence after nearest-neighbor comparison on the verified optical grid.",
                "The BAER delivery contains no restricted classified BARC or SBS raster, and the exact RAVG sparse-cover caution is enforced.",
            ],
            "not_proven": [
                "RAVG is not independent affirmative evidence for this sparse/non-tree event, and no program supplies affirmative background truth.",
                "No candidate, owner decision, label, dataset, split, baseline, model, metric, official status, endorsement, or operational readiness is created.",
            ],
        },
        "warning": WARNING,
    }
    previews.update(sampled)
    return report, previews


def render_png(report: dict[str, Any], previews: dict[str, np.ndarray], path: Path) -> None:
    canvas = Image.new("RGB", (1800, 1260), "#07110f")
    draw = ImageDraw.Draw(canvas)
    draw.text((60, 38), "BURNLENS  /  GRANDVIEW REFERENCE FITNESS", fill="#b9d8cf", font=_font(21))
    draw.text((60, 76), "MTBS evidence passes; RAVG is context-limited.", fill="#eef7f3", font=_font(31))
    draw.text((60, 128), report["fitness_decision"]["checkpoint"], fill="#ffca73", font=_font(18))
    boundary = previews["boundary_mask20"]
    panels = [
        ("PRE OPTICAL", _preview_tci(previews["pre_tci"], previews["pre_mask"], (520, 315))),
        ("POST OPTICAL", _preview_tci(previews["post_tci"], previews["post_mask"], (520, 315))),
        ("CONTINUOUS dNBR", _preview_dnbr(previews["dnbr"], previews["dnbr_valid"], (520, 315))),
        ("MTBS dNBR6", _class_image(previews["mtbs_dnbr6"], boundary, {1:(160,168,145),2:(244,213,112),3:(235,144,70),4:(190,63,45),5:(80,170,100)}, (520,315))),
        ("RAVG CBI4 / LIMITED", _class_image(previews["ravg_cbi4"], boundary, {1:(160,168,145),2:(244,213,112),3:(235,144,70),4:(190,63,45)}, (520,315))),
        ("RAVG BASAL AREA / LIMITED", _class_image(previews["ravg_ba4"], boundary, {1:(160,168,145),2:(244,213,112),3:(235,144,70),4:(190,63,45)}, (520,315))),
    ]
    for index, (label, image) in enumerate(panels):
        column, row = index % 3, index // 3
        x, y = 60 + column * 575, 180 + row * 405
        draw.rounded_rectangle((x, y, x + 535, y + 375), radius=16, fill="#0e1d1a", outline="#315b50", width=2)
        draw.text((x + 18, y + 14), label, fill="#eef7f3", font=_font(18))
        canvas.paste(image, (x + 8, y + 48))
    evidence = report["evidence_comparison"]
    metrics = [
        (f"{evidence['mtbs_affirmative_pixels']:,}", "MTBS classes 2-4"),
        (f"{evidence['mtbs_affirmative_and_optical_valid_pixels']:,}", "plus valid optical pair"),
        (f"{evidence['mtbs_reference_coverage_percent']:.4f}%", "MTBS grid coverage"),
        ("0", "background truth / labels"),
    ]
    for index, (value, label) in enumerate(metrics):
        x = 60 + index * 430
        draw.rounded_rectangle((x, 1015, x + 395, 1128), radius=14, fill="#0e1d1a", outline="#315b50", width=2)
        draw.text((x + 20, 1035), value, fill="#78e0bd", font=_font(27))
        draw.text((x + 20, 1082), label, fill="#b9d8cf", font=_font(14))
    draw.rounded_rectangle((60, 1152, 1740, 1218), radius=14, fill="#261f12", outline="#be8a36", width=2)
    draw.text((82, 1164), "RAVG warning: sparse/no pre-fire tree cover makes forest-calibrated modeled values less reliable.", fill="#ffd997", font=_font(15))
    draw.text((82, 1190), WARNING, fill="#ffd997", font=_font(14))
    draw.text((60, 1232), f"TRACE commit {report['git_source_commit'][:12]} / run {report['run_id']} / BurnLens {SOFTWARE_VERSION} / dataset-model none", fill="#b9d8cf", font=_font(13))
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path, format="PNG", optimize=False)


def render_html(report: dict[str, Any], png_name: str, path: Path) -> None:
    evidence = report["evidence_comparison"]
    rows = "".join(
        f"<tr><td>{escape(item['program'])}</td><td><code>{escape(PurePosixPath(item['member']).name)}</code></td><td>{item['width']}×{item['height']}</td><td>{escape(str(item['nodata']))}</td><td>{escape(str(item['native_value_domain'] or 'continuous'))}</td><td>{escape(item['role'])}</td></tr>"
        for item in report["selected_evidence_products"].values()
    )
    html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Grandview reference fitness</title><style>
body{{margin:0;background:#07110f;color:#eef7f3;font:16px/1.55 system-ui,sans-serif}}main{{max-width:1200px;margin:auto;padding:32px}}h1{{font-size:clamp(2rem,5vw,4rem);line-height:1.02}}.card{{background:#0e1d1a;border:1px solid #315b50;border-radius:16px;padding:20px;margin:18px 0}}.warn{{background:#261f12;border-color:#be8a36;color:#ffd997}}img{{width:100%;height:auto;border-radius:16px}}table{{width:100%;border-collapse:collapse}}th,td{{text-align:left;padding:10px;border-bottom:1px solid #315b50;vertical-align:top}}code{{overflow-wrap:anywhere}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px}}.metric strong{{display:block;font-size:2rem;color:#78e0bd}}
</style></head><body><main><p>BURNLENS / PHASE TWO / ISSUE #499</p><h1>MTBS evidence passes; RAVG is context-limited.</h1><div class="card warn">{escape(report['warning'])}</div><img src="{escape(png_name)}" width="1800" height="1260" alt="Actual Grandview optical, MTBS, and limited RAVG evidence"><div class="grid"><div class="card metric"><strong>{evidence['mtbs_affirmative_pixels']:,}</strong>MTBS classes 2–4</div><div class="card metric"><strong>{evidence['mtbs_affirmative_and_optical_valid_pixels']:,}</strong>plus valid optical pair</div><div class="card metric"><strong>{evidence['mtbs_reference_coverage_percent']:.4f}%</strong>MTBS grid coverage</div><div class="card metric"><strong>0</strong>labels or background truth</div></div><h2>Exact selected products</h2><div class="card"><table><thead><tr><th>Program</th><th>Member</th><th>Native grid</th><th>Nodata</th><th>Domain</th><th>Role</th></tr></thead><tbody>{rows}</tbody></table><p>All categorical comparisons use nearest-neighbor sampling from native 30 m to the verified 20 m optical grid. No resolution gain is claimed. The MTBS grid covers {evidence['mtbs_reference_covered_pixels']:,} of {evidence['optical_boundary_pixels']:,} optical-boundary pixel centers; {evidence['mtbs_reference_uncovered_pixels']:,} are explicitly unresolved rather than inferred.</p></div><h2>Source roles</h2><div class="card"><p><strong>MTBS:</strong> classes 2–4 are categorical burned-candidate evidence; class 1 remains ambiguous and class 5 is reported separately.</p><p><strong>RAVG:</strong> the delivered record explicitly warns that sparse/no pre-fire tree cover makes these forest-calibrated models less reliable. RAVG is context only and cannot independently qualify a candidate here.</p><p><strong>BAER:</strong> only unthresholded continuous change context is present. Restricted classified BARC/SBS rasters are absent.</p></div><h2>Gate result</h2><div class="card"><p><strong>{escape(report['fitness_decision']['checkpoint'])}</strong></p><p>MTBS-backed burned-candidate proposal may proceed only in a separate bounded checkpoint with actual optical/reference evidence and owner yes/no/uncertain review. Affirmative background evidence remains unresolved.</p></div><div class="card warn"><p>{escape(report['terms_and_roles']['attribution'])}</p><p>No independent ground truth, field validation, official status, endorsement, operational readiness, dataset, split, baseline, model, or accuracy claim exists.</p></div><p>Trace: commit <code>{escape(report['git_source_commit'])}</code> · BurnLens <code>{SOFTWARE_VERSION}</code> · run <code>{escape(report['run_id'])}</code> · label schema <code>{escape(report['trace']['label_schema_version'])}</code> · dataset/model none.</p></main></body></html>"""
    _write_utf8_lf(path, html)


def write_outputs(report: dict[str, Any], previews: dict[str, np.ndarray], directory: Path) -> dict[str, Path]:
    directory.mkdir(parents=True, exist_ok=True)
    paths = {name: directory / f"{REPORT_ID}.{name}" for name in ("json", "html", "png")}
    _write_utf8_lf(paths["json"], json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    render_png(report, previews, paths["png"])
    render_html(report, paths["png"].name, paths["html"])
    return paths
