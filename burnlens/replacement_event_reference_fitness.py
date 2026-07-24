"""Inspect exact Ward Creek MTBS evidence against the verified optical pair.

This unit resolves embedded terms, verifies every native product and boundary
component, reruns optical registration, and compares MTBS classes on the
verified 20 m grid. It creates no candidate, label, dataset, split, baseline,
model, metric, or readiness claim.
"""

from __future__ import annotations

from hashlib import sha256
from html import escape
import json
from pathlib import Path, PurePosixPath
import subprocess
from typing import Any
from xml.etree import ElementTree as ET
from zipfile import BadZipFile, ZipFile

import geopandas as gpd
import numpy as np
from PIL import Image, ImageDraw
import rasterio
from rasterio.io import MemoryFile
from rasterio.warp import Resampling, reproject
from shapely.geometry import mapping

from .content_registration import _summary as registration_summary
from .cross_event_source_fitness import _read_product, measure_event_registration
from .green_ridge_reference_fitness import _class_image
from .green_ridge_source_fitness import _preview_dnbr, _preview_tci, summarize_spectral_change
from .optical_pair_evidence import WARNING, _font
from .paired_intake import verify_registered_package
from .replacement_event_optical_contract import (
    CONTRACT_VERSION,
    EVENT_GROUP_ID,
    EVENT_ID,
    POST_CONTRACT,
    PRE_CONTRACT,
    SOFTWARE_VERSION,
    _singleton_validator,
)


REPORT_ID = "WARD-CREEK-REFERENCE-FITNESS-2026-001"
REPORT_VERSION = "ward-creek-reference-fitness-v0.1.0"
PROTOCOL_VERSION = "ward-creek-reference-fitness-protocol-v0.1.0"
UNIT_ID = "P2O4-T39-U03"
TASK_ISSUE = 554
RUN_ID = "BL-2026-07-24-ward-creek-reference-fitness-r002"
ARCHIVE_BYTES = 4_385_952
ARCHIVE_SHA256 = "d94dfb1609c882fdd26119b2be03cea486af1bbb85e4c9607f108f9455f61d18"
ARCHIVE_MEMBERS = 16
ARCHIVE_FILES = 13
ARCHIVE_UNCOMPRESSED_BYTES = 5_462_721
MAP_ID = 10_016_337
ROOT = "mtbs/2019/mtbs_or4494912090120190812_10016337/"
PAIR = "mtbs_or4494912090120190812_10016337_20190729_20190830"
EXPECTED_RASTERS = {
    "pre_reflectance": ROOT + "mtbs_or4494912090120190812_10016337_20190729_l8_refl.tif",
    "post_reflectance": ROOT + "mtbs_or4494912090120190812_10016337_20190830_l8_refl.tif",
    "dnbr": ROOT + f"{PAIR}_dnbr.tif",
    "rdnbr": ROOT + f"{PAIR}_rdnbr.tif",
    "dnbr6": ROOT + f"{PAIR}_dnbr6.tif",
}
VECTOR_MEMBERS = {
    extension: ROOT + f"{PAIR}_burn_area.{extension}"
    for extension in ("shp", "shx", "dbf", "prj")
}
FGDC_MEMBER = ROOT + f"{PAIR}_metadata.xml"
ISO_MEMBER = ROOT + f"{PAIR}_iso_metadata.xml"
PDF_MEMBER = ROOT + f"{PAIR}.pdf"
KMZ_MEMBER = ROOT + f"{PAIR}.kmz"
MTBS_CLASSES = {
    0: "outside_or_nodata_not_background_truth",
    1: "unburned_to_low_or_rapid_recovery_ambiguous_not_background_truth",
    2: "low_severity_reference_evidence",
    3: "moderate_severity_reference_evidence",
    4: "high_severity_reference_evidence",
    5: "increased_greenness_reference_evidence",
    6: "nonprocessing_mask_excluded",
}
EXPECTED_DNBR6_DOMAIN = {"0": 103_122, "1": 460, "2": 8_287, "3": 558, "5": 1}


class ReplacementEventReferenceFitnessError(RuntimeError):
    """The exact Ward Creek source-fitness contract failed closed."""


def _digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def _file_digest(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _metadata_values(root: ET.Element, tag: str) -> list[str]:
    values: list[str] = []
    for item in root.iter():
        if item.tag.split("}")[-1].casefold() == tag.casefold():
            value = " ".join(" ".join(item.itertext()).split())
            if value and value not in values:
                values.append(value)
    return values


def _inspect_metadata(archive: ZipFile) -> dict[str, Any]:
    fgdc = archive.read(FGDC_MEMBER)
    iso = archive.read(ISO_MEMBER)
    fgdc_root = ET.fromstring(fgdc)
    iso_root = ET.fromstring(iso)
    access = _metadata_values(fgdc_root, "accconst")
    use = _metadata_values(fgdc_root, "useconst")
    liability = _metadata_values(fgdc_root, "distliab")
    iso_use = _metadata_values(iso_root, "useLimitation")
    if access != ["None"]:
        raise ReplacementEventReferenceFitnessError("MTBS access constraint drifted")
    if len(use) != 1 or "reasonable and proper acknowledgement" not in use[0]:
        raise ReplacementEventReferenceFitnessError("MTBS use constraint drifted")
    if len(liability) != 1 or "no warranty expressed or implied" not in liability[0]:
        raise ReplacementEventReferenceFitnessError("MTBS liability language drifted")
    if len(iso_use) != 2:
        raise ReplacementEventReferenceFitnessError("MTBS ISO use-limitation roster drifted")
    joined = " ".join(iso_use)
    for text in (
        "reasonable and proper acknowledgement",
        "data may be updated",
        "may not be in an accurate geographic location",
        "no expressed or implied warranty",
    ):
        if text not in joined:
            raise ReplacementEventReferenceFitnessError(f"MTBS ISO caution missing: {text}")
    return {
        "fgdc": {
            "member": FGDC_MEMBER,
            "bytes": len(fgdc),
            "sha256": _digest(fgdc),
            "title": _metadata_values(fgdc_root, "title")[0],
            "abstract": _metadata_values(fgdc_root, "abstract")[0],
            "purpose": _metadata_values(fgdc_root, "purpose")[0],
            "access_constraints": access[0],
            "use_constraints": use[0],
            "distribution_liability": liability[0],
        },
        "iso": {
            "member": ISO_MEMBER,
            "bytes": len(iso),
            "sha256": _digest(iso),
            "use_limitations": iso_use,
            "credit": _metadata_values(iso_root, "credit")[0],
        },
        "decision": "PASS_MTBS_EMBEDDED_TERMS_FOR_BOUNDED_ACKNOWLEDGED_EVIDENCE",
    }


def _inspect_archive(path: Path) -> dict[str, Any]:
    if not path.is_file() or path.stat().st_size != ARCHIVE_BYTES:
        raise ReplacementEventReferenceFitnessError("archive byte contract mismatch")
    if _file_digest(path) != ARCHIVE_SHA256:
        raise ReplacementEventReferenceFitnessError("archive SHA-256 mismatch")
    expected_files = {
        *EXPECTED_RASTERS.values(),
        *VECTOR_MEMBERS.values(),
        FGDC_MEMBER,
        ISO_MEMBER,
        PDF_MEMBER,
        KMZ_MEMBER,
    }
    try:
        with ZipFile(path) as archive:
            infos = archive.infolist()
            files = {item.filename for item in infos if not item.is_dir()}
            if len(infos) != ARCHIVE_MEMBERS or len(files) != ARCHIVE_FILES:
                raise ReplacementEventReferenceFitnessError("archive member roster drifted")
            if files != expected_files:
                raise ReplacementEventReferenceFitnessError("archive exact file roster drifted")
            if sum(item.file_size for item in infos) != ARCHIVE_UNCOMPRESSED_BYTES:
                raise ReplacementEventReferenceFitnessError("archive uncompressed bytes drifted")
            if any(item.flag_bits & 0x1 for item in infos):
                raise ReplacementEventReferenceFitnessError("encrypted archive member")
            for item in infos:
                pure = PurePosixPath(item.filename)
                if pure.is_absolute() or ".." in pure.parts or "\\" in item.filename:
                    raise ReplacementEventReferenceFitnessError("unsafe archive path")
            if archive.testzip() is not None:
                raise ReplacementEventReferenceFitnessError("archive CRC failed")
    except BadZipFile as error:
        raise ReplacementEventReferenceFitnessError("archive is not a readable ZIP") from error
    return {
        "bytes": ARCHIVE_BYTES,
        "sha256": ARCHIVE_SHA256,
        "member_count": ARCHIVE_MEMBERS,
        "file_count": ARCHIVE_FILES,
        "uncompressed_bytes": ARCHIVE_UNCOMPRESSED_BYTES,
        "safe_unique_unencrypted_no_symlink_zip": True,
        "full_crc": True,
        "private_delivery_route_retained": False,
    }


def _write_exact_extraction(archive: ZipFile, root: Path) -> dict[str, Any]:
    root.mkdir(parents=True, exist_ok=False)
    parts: dict[str, Any] = {}
    for extension, member in VECTOR_MEMBERS.items():
        data = archive.read(member)
        path = root / f"{PAIR}_burn_area.{extension}"
        with path.open("xb") as target:
            target.write(data)
        parts[extension] = {
            "member": member,
            "path": path.as_posix(),
            "bytes": len(data),
            "sha256": _digest(data),
        }
    return parts


def _load_boundary(archive: ZipFile, extracted_root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    parts = _write_exact_extraction(archive, extracted_root)
    frame = gpd.read_file(extracted_root / f"{PAIR}_burn_area.shp")
    if len(frame) != 1 or frame.crs is None or frame.crs.to_epsg() != 32610:
        raise ReplacementEventReferenceFitnessError("boundary roster or CRS drifted")
    geometry = frame.geometry.iloc[0]
    if geometry.geom_type != "Polygon" or geometry.is_empty or not geometry.is_valid:
        raise ReplacementEventReferenceFitnessError("boundary topology failed")
    row = frame.drop(columns="geometry").iloc[0].to_dict()
    expected = {
        "EVENT_ID": EVENT_ID,
        "MAP_ID": MAP_ID,
        "MAP_PROG": "MTBS",
        "INCID_NAME": "WARD CREEK 0769 RN",
        "INCID_TYPE": "Wildfire",
        "ASMNT_TYPE": "Initial",
        "BURNBNDAC": 2070,
        "PRE_ID": "804502920190729",
        "POST_ID": "804502920190830",
    }
    for field, value in expected.items():
        if row.get(field) != value:
            raise ReplacementEventReferenceFitnessError(f"boundary attribute drifted: {field}")
    thresholds = {
        key: int(row[key])
        for key in ("DNBR_OFFST", "DNBR_STDDV", "NODATA_T", "INCGREEN_T", "LOW_T", "MOD_T", "HIGH_T")
    }
    if thresholds != {
        "DNBR_OFFST": 21,
        "DNBR_STDDV": 23,
        "NODATA_T": -970,
        "INCGREEN_T": -150,
        "LOW_T": 45,
        "MOD_T": 350,
        "HIGH_T": 9999,
    }:
        raise ReplacementEventReferenceFitnessError("analyst threshold contract drifted")
    wgs84 = frame.to_crs(4326).geometry.iloc[0]
    return mapping(wgs84), {
        "components": parts,
        "feature_count": 1,
        "crs": "EPSG:32610",
        "geometry_type": geometry.geom_type,
        "valid": True,
        "bounds_utm10n": [round(float(value), 9) for value in geometry.bounds],
        "area_square_meters": round(float(geometry.area), 3),
        "attributes": {**expected, "IG_DATE": "2019-08-12"},
        "analyst_thresholds": thresholds,
    }


def _inspect_raster(archive: ZipFile, member: str) -> tuple[dict[str, Any], np.ndarray]:
    data = archive.read(member)
    try:
        with MemoryFile(data) as memory, memory.open() as source:
            stack = source.read()
            nodata = source.nodata
            valid = np.isfinite(stack)
            if nodata is not None:
                valid &= stack != nodata
            observed = stack[valid]
            encoded_values, encoded_counts = np.unique(stack, return_counts=True)
            domain = (
                {str(int(value)): int(count) for value, count in zip(encoded_values, encoded_counts, strict=True)}
                if len(encoded_values) <= 32
                else None
            )
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
                "resolution_m": [abs(float(source.transform.a)), abs(float(source.transform.e))],
                "transform": [float(value) for value in source.transform[:6]],
                "bounds": [float(value) for value in source.bounds],
                "valid_pixels": int(observed.size),
                "nodata_pixels": int(stack.size - observed.size),
                "native_value_domain": domain,
                "valid_quantiles": (
                    None
                    if domain is not None
                    else {
                        key: round(float(value), 3)
                        for key, value in zip(
                            ("min", "p01", "p50", "p99", "max"),
                            np.percentile(observed, (0, 1, 50, 99, 100)),
                            strict=True,
                        )
                    }
                ),
                "all_bands_read": True,
            }
    except rasterio.errors.RasterioError as error:
        raise ReplacementEventReferenceFitnessError(f"unreadable raster: {member}") from error
    if (
        profile["crs"] != "EPSG:32610"
        or profile["width"] != 324
        or profile["height"] != 347
        or profile["resolution_m"] != [30.0, 30.0]
        or profile["transform"] != [30.0, 0.0, 662460.0, 0.0, -30.0, 4983150.0]
    ):
        raise ReplacementEventReferenceFitnessError(f"native raster grid drifted: {member}")
    return profile, stack[0]


def _verify_optical_package(package: Path, contract: Any) -> dict[str, Any]:
    result = verify_registered_package(
        package,
        (contract,),
        contract_validator=_singleton_validator(contract),
        contract_version=CONTRACT_VERSION,
        allow_multilink_registration_manifest=True,
    )
    if not result["accepted_as_unchanged_registered_package"]:
        raise ReplacementEventReferenceFitnessError(f"{contract.role} package verification failed")
    return result


def _sample_reference(
    values: np.ndarray,
    profile: dict[str, Any],
    shape: tuple[int, int],
    transform: rasterio.Affine,
) -> np.ndarray:
    destination = np.zeros(shape, dtype=np.uint8)
    reproject(
        values,
        destination,
        src_transform=rasterio.Affine(*profile["transform"]),
        src_crs=profile["crs"],
        src_nodata=profile["nodata"],
        dst_transform=transform,
        dst_crs="EPSG:32610",
        dst_nodata=0,
        resampling=Resampling.nearest,
    )
    return destination


def build_report(
    *,
    repository_root: Path,
    pre_package: Path,
    post_package: Path,
    archive_path: Path,
    extracted_root: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    if run_id != RUN_ID:
        raise ReplacementEventReferenceFitnessError("run ID drifted")
    repository_root = repository_root.resolve()
    top = subprocess.run(
        ["git", "-C", str(repository_root), "rev-parse", "--show-toplevel"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    head = subprocess.run(
        ["git", "-C", str(repository_root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if Path(top).resolve() != repository_root or git_source_commit != head:
        raise ReplacementEventReferenceFitnessError(
            "git source commit does not match repository HEAD"
        )
    archive_summary = _inspect_archive(archive_path)
    with ZipFile(archive_path) as archive:
        metadata = _inspect_metadata(archive)
        geometry, boundary = _load_boundary(archive, extracted_root)
        native_rasters: list[dict[str, Any]] = []
        runtime: dict[str, np.ndarray] = {}
        for role, member in EXPECTED_RASTERS.items():
            profile, values = _inspect_raster(archive, member)
            native_rasters.append({"role": role, **profile})
            runtime[role] = values
        if next(item for item in native_rasters if item["role"] == "dnbr6")["native_value_domain"] != EXPECTED_DNBR6_DOMAIN:
            raise ReplacementEventReferenceFitnessError("dNBR6 class domain drifted")
        presentation_members = {
            "pdf": {
                "member": PDF_MEMBER,
                "bytes": len(archive.read(PDF_MEMBER)),
                "sha256": _digest(archive.read(PDF_MEMBER)),
            },
            "kmz": {
                "member": KMZ_MEMBER,
                "bytes": len(archive.read(KMZ_MEMBER)),
                "sha256": _digest(archive.read(KMZ_MEMBER)),
            },
        }
    pre_verification = _verify_optical_package(pre_package, PRE_CONTRACT)
    post_verification = _verify_optical_package(post_package, POST_CONTRACT)
    pre_scene, pre = _read_product(
        pre_package, PRE_CONTRACT, geometry, expected_processing_baseline="05.00"
    )
    post_scene, post = _read_product(
        post_package, POST_CONTRACT, geometry, expected_processing_baseline="05.00"
    )
    windows, quality = measure_event_registration(pre_scene, pre, post_scene, post)
    registration = registration_summary(windows)
    if registration["machine_decision"] != "PASS_LOCAL_CONTENT_REGISTRATION_GATE":
        raise ReplacementEventReferenceFitnessError("optical registration gate failed")
    spectral, dnbr, optical_valid = summarize_spectral_change(pre_scene, pre, post_scene, post)
    optical_boundary = pre["MASK20"]
    if optical_boundary.shape != (219, 183) or int(optical_boundary.sum()) != 20_943:
        raise ReplacementEventReferenceFitnessError("optical boundary grid drifted")
    sampled = _sample_reference(
        runtime["dnbr6"],
        next(item for item in native_rasters if item["role"] == "dnbr6"),
        optical_boundary.shape,
        rasterio.Affine(*pre_scene["rasters"]["B04"]["crop_transform"]),
    )
    values, counts = np.unique(sampled[optical_boundary], return_counts=True)
    class_counts = {str(int(value)): int(count) for value, count in zip(values, counts, strict=True)}
    if class_counts != {"0": 389, "1": 853, "2": 18_440, "3": 1_260, "5": 1}:
        raise ReplacementEventReferenceFitnessError("MTBS-on-optical class counts drifted")
    affirmative = optical_boundary & np.isin(sampled, (2, 3, 4))
    report = {
        "report_id": REPORT_ID,
        "report_version": REPORT_VERSION,
        "protocol_version": PROTOCOL_VERSION,
        "unit_id": UNIT_ID,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": TASK_ISSUE,
        "git_source_commit": git_source_commit,
        "software_version": SOFTWARE_VERSION,
        "application_version": None,
        "label_schema_version": "burn-scar-binary-region-label-schema-v0.3.0",
        "dataset_version": None,
        "split_version": None,
        "baseline_version": None,
        "model_version": None,
        "event": {
            "event_group_id": EVENT_GROUP_ID,
            "event_id": EVENT_ID,
            "fire_name": "WARD CREEK 0769 RN",
            "ignition_date": "2019-08-12",
            "map_id": MAP_ID,
        },
        "archive": archive_summary,
        "metadata_and_terms": metadata,
        "boundary": boundary,
        "native_rasters": native_rasters,
        "presentation_members": presentation_members,
        "optical_reverification": {
            "pre_package": {
                "package_id": PRE_CONTRACT.package_id,
                "registration_manifest_sha256": pre_verification["registration_manifest_sha256"],
            },
            "post_package": {
                "package_id": POST_CONTRACT.package_id,
                "registration_manifest_sha256": post_verification["registration_manifest_sha256"],
            },
            "products": [pre_scene, post_scene],
            "pair_quality_inside_full_boundary": quality["inside_boundary"],
            "registration": {"summary": registration, "windows": windows},
            "spectral_change": spectral,
        },
        "evidence_comparison": {
            "optical_boundary_pixels": int(optical_boundary.sum()),
            "optical_pair_valid_pixels": int(optical_valid.sum()),
            "mtbs_dnbr6_on_optical_boundary": class_counts,
            "mtbs_affirmative_pixels": int(affirmative.sum()),
            "mtbs_affirmative_and_optical_valid_pixels": int((affirmative & optical_valid).sum()),
            "mtbs_covered_pixels": int((optical_boundary & (sampled != 0)).sum()),
            "mtbs_uncovered_pixels": int((optical_boundary & (sampled == 0)).sum()),
            "categorical_sampling": "nearest neighbor from native 30 m onto the verified 20 m optical grid; no resolution gain claimed",
            "class_semantics": {str(key): value for key, value in MTBS_CLASSES.items()},
            "background_finding": "No MTBS class supplies affirmative background truth. Class 1 remains ambiguous; class 0 is outside or nodata.",
        },
        "source_precedence": {
            "topology": "The valid delivered MTBS boundary governs this exact source-fitness comparison.",
            "positive_reference": "MTBS analyst-interpreted classes 2-4 may support a separate burned-candidate proposal.",
            "background": "A separate affirmative optical-stability route remains required.",
        },
        "terms_and_roles": {
            "resolved_for_bounded_prototype_evidence": True,
            "use": "Use with reasonable and proper acknowledgement of MTBS, USGS, and USDA Forest Service.",
            "cautions": "Data may be updated; represented locations may be inaccurate; no warranty or fitness is supplied.",
            "attribution": "Monitoring Trends in Burn Severity Project (U.S. Geological Survey and USDA Forest Service); Contains modified Copernicus Sentinel data 2019, accessed through CDSE.",
        },
        "fitness_decision": {
            "source": "PASS_EXACT_WARD_CREEK_MTBS_SOURCE_FITNESS",
            "burned_candidate_route": "OPEN_FOR_SEPARATE_BOUNDED_MTBS_SUPPORTED_PROPOSAL",
            "background_candidate_route": "OPEN_ONLY_FOR_SEPARATE_AFFIRMATIVE_OPTICAL_STABILITY_PROPOSAL",
            "next_dependency": "P2O4-T39-U04_AFFIRMATIVE_BACKGROUND",
            "checkpoint": "ACCEPT_REFERENCE_FITNESS_DEFER_CANDIDATES_OWNER_DECISIONS_LABELS_DATASET_SPLIT_BASELINE_MODEL",
        },
        "claims": {
            "proven": [
                "The exact delivery, embedded notices, safe archive, identities, valid boundary, native rasters, grids, nodata, and class domain passed deterministic inspection.",
                "The exact Sentinel pair is fully eligible and passes all nine local registration windows on the delivered boundary.",
                "MTBS classes 2-3 cover 19,700 verified optical-grid pixel centers as bounded candidate evidence.",
            ],
            "not_proven": [
                "MTBS is not independent ground truth, affirmative background truth, BurnLens field validation, or an operational label.",
                "No candidate, owner decision, label, dataset, split, baseline, model, metric, accuracy, official status, endorsement, operational readiness, or emergency suitability is created.",
            ],
        },
        "warning": WARNING,
    }
    previews = {
        "pre_tci": pre["TCI"],
        "post_tci": post["TCI"],
        "pre_mask": pre["MASK10"],
        "post_mask": post["MASK10"],
        "dnbr": dnbr,
        "dnbr_valid": optical_valid,
        "boundary_mask20": optical_boundary,
        "mtbs_dnbr6": sampled,
    }
    return report, previews


def render_png(report: dict[str, Any], previews: dict[str, np.ndarray], path: Path) -> None:
    canvas = Image.new("RGB", (1600, 1120), "#07110f")
    draw = ImageDraw.Draw(canvas)
    draw.text((55, 35), "BURNLENS  /  WARD CREEK REFERENCE FITNESS", fill="#b9d8cf", font=_font(20))
    draw.text((55, 72), "Exact MTBS evidence passes. No labels are created.", fill="#eef7f3", font=_font(30))
    boundary = previews["boundary_mask20"]
    panels = [
        ("PRE SENTINEL-2", _preview_tci(previews["pre_tci"], previews["pre_mask"], (470, 320))),
        ("POST SENTINEL-2", _preview_tci(previews["post_tci"], previews["post_mask"], (470, 320))),
        ("CONTINUOUS dNBR", _preview_dnbr(previews["dnbr"], previews["dnbr_valid"], (470, 320))),
        (
            "MTBS dNBR6",
            _class_image(
                previews["mtbs_dnbr6"],
                boundary,
                {1: (160, 168, 145), 2: (244, 213, 112), 3: (235, 144, 70), 4: (190, 63, 45), 5: (80, 170, 100)},
                (470, 320),
            ),
        ),
    ]
    for index, (label, image) in enumerate(panels):
        x = 55 + (index % 2) * 760
        y = 145 + (index // 2) * 390
        draw.rounded_rectangle((x, y, x + 700, y + 360), radius=15, fill="#0e1d1a", outline="#315b50", width=2)
        draw.text((x + 18, y + 14), label, fill="#eef7f3", font=_font(18))
        canvas.paste(image, (x + 115, y + 38))
    evidence = report["evidence_comparison"]
    metrics = [
        (f"{evidence['mtbs_affirmative_pixels']:,}", "MTBS affirmative"),
        ("9 / 9", "registration windows"),
        ("100%", "pair eligible"),
        ("0", "labels or dataset"),
    ]
    for index, (value, label) in enumerate(metrics):
        x = 55 + index * 380
        draw.rounded_rectangle((x, 930, x + 340, 1030), radius=13, fill="#0e1d1a", outline="#315b50", width=2)
        draw.text((x + 18, 946), value, fill="#78e0bd", font=_font(26))
        draw.text((x + 18, 990), label, fill="#b9d8cf", font=_font(14))
    draw.text((55, 1060), WARNING, fill="#ffd997", font=_font(14))
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path, format="PNG", optimize=False)


def render_html(report: dict[str, Any], png_name: str) -> str:
    evidence = report["evidence_comparison"]
    proven = "".join(f"<li>{escape(item)}</li>" for item in report["claims"]["proven"])
    not_proven = "".join(f"<li>{escape(item)}</li>" for item in report["claims"]["not_proven"])
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Ward Creek reference fitness</title><style>
:root{{--bg:#07110f;--card:#0e1d1a;--ink:#eef7f3;--muted:#b9d8cf;--line:#315b50;--ok:#78e0bd;--warn:#ffd997}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 system-ui,sans-serif}}
main{{max-width:1100px;margin:auto;padding:32px 20px 64px}}h1{{font-size:clamp(2rem,6vw,4rem);line-height:1;margin:.2em 0}}
.eyebrow{{color:var(--ok);font-weight:800;letter-spacing:.12em}}.lede{{font-size:1.2rem;color:var(--muted)}}
.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:24px 0}}.card{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px}}
.metric{{font-size:1.8rem;color:var(--ok);font-weight:800}}img{{width:100%;height:auto;border-radius:14px;border:1px solid var(--line)}}
section{{margin-top:28px}}li{{margin:.5em 0}}.warn{{border-color:#be8a36;color:var(--warn)}}code{{overflow-wrap:anywhere}}
@media(max-width:760px){{.grid{{grid-template-columns:1fr 1fr}}}}
</style></head><body><main>
<p class="eyebrow">P2O4-T39-U03 / EXACT SOURCE FITNESS</p>
<h1>Ward Creek MTBS evidence passes.</h1>
<p class="lede">The exact delivery, embedded notices, native products, boundary, and optical registration pass. This checkpoint creates no candidate or label.</p>
<div class="grid">
<div class="card"><div class="metric">{evidence['mtbs_affirmative_pixels']:,}</div>MTBS affirmative pixel centers</div>
<div class="card"><div class="metric">9 / 9</div>registration windows pass</div>
<div class="card"><div class="metric">100%</div>optical pair eligible</div>
<div class="card"><div class="metric">0</div>labels, datasets, or models</div>
</div>
<img src="{escape(png_name)}" alt="Four-panel Ward Creek comparison with pre and post Sentinel-2 imagery, continuous dNBR, and categorical MTBS evidence.">
<section class="card"><h2>What this proves</h2><ul>{proven}</ul></section>
<section class="card warn"><h2>What this does not prove</h2><ul>{not_proven}</ul></section>
<section class="card"><h2>Binding limitations</h2><p>{escape(report['terms_and_roles']['cautions'])}</p>
<p>MTBS classes 2-4 may support a later burned-candidate proposal. No class is affirmative background truth.</p></section>
<section><p><code>{escape(report['run_id'])}</code><br><code>{escape(report['git_source_commit'])}</code></p></section>
</main></body></html>
"""


def write_outputs(
    report: dict[str, Any],
    previews: dict[str, np.ndarray],
    output_directory: Path,
) -> dict[str, Path]:
    output_directory.mkdir(parents=True, exist_ok=False)
    json_path = output_directory / f"{REPORT_ID}.json"
    png_path = output_directory / f"{REPORT_ID}.png"
    html_path = output_directory / f"{REPORT_ID}.html"
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    render_png(report, previews, png_path)
    html_path.write_text(render_html(report, png_path.name), encoding="utf-8", newline="\n")
    return {"json": json_path, "png": png_path, "html": html_path}
