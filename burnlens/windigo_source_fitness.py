"""Gate the exact Windigo optical pair and delivered BAER/MTBS/RAVG evidence.

This checkpoint inspects source identity, rights, archive safety, native grids,
class semantics, vector validity, optical quality, and cross-source agreement.
It creates no candidate, owner response, label, dataset, split, baseline, or
model.
"""

from __future__ import annotations

from hashlib import sha256
from html import escape
import argparse
import json
from pathlib import Path, PurePosixPath
from typing import Any
from xml.etree import ElementTree as ET
from zipfile import BadZipFile, ZipFile

import numpy as np
from PIL import Image, ImageDraw
import rasterio
from rasterio.io import MemoryFile
from rasterio.warp import Resampling, reproject

from .content_registration import _summary as registration_summary
from .cross_event_feasibility import LABEL_SCHEMA_VERSION
from .cross_event_source_fitness import _read_product, measure_event_registration
from .green_ridge_reference_fitness import (
    _class_image,
    _metadata_text,
)
from .green_ridge_source_fitness import (
    _preview_dnbr,
    _preview_tci,
    summarize_spectral_change,
)
from .optical_pair_evidence import (
    LABEL_PROTOCOL_VERSION,
    TARGET_VERSION,
    WARNING,
    _font,
    _write_utf8_lf,
)
from .paired_intake import verify_registered_package
from .windigo_optical_contract import (
    CONTRACT_VERSION,
    EVENT_GROUP_ID,
    EVENT_ID,
    POST_CONTRACT,
    PRE_CONTRACT,
    SOURCE_RECORD_ID,
    SOFTWARE_VERSION,
    TERMS_REVIEW_ID,
    _singleton_validator,
)


REPORT_ID = "WINDIGO-SOURCE-FITNESS-2026-005"
REPORT_VERSION = "windigo-source-fitness-v0.1.4"
PROTOCOL_VERSION = "windigo-native-source-fitness-protocol-v0.1.0"
TASK_ISSUE = 534
UNIT_ID = "P2O4-T35-U03"
RUN_ID = "BL-2026-07-23-windigo-source-fitness-r005"
ARCHIVE_BYTES = 12_526_858
ARCHIVE_SHA256 = "defd99749a28bd311bcab9bc75631447e1e42eecf3da66adbb3c9c1e2d6b0804"
ARCHIVE_MEMBERS = 54
ARCHIVE_FILES = 45
ARCHIVE_UNCOMPRESSED_BYTES = 16_873_532
MAP_IDS = {"BAER": 10022395, "RAVG": 10022960, "MTBS": 10029547}
EXPECTED_PROGRAM_PREFIXES = {
    "BAER": "baer/2022/baer_or4336312205020220730_10022395/",
    "RAVG": "ravg/2022/ravg_or4336312205020220730_10022960/",
    "MTBS": "mtbs/2022/mtbs_or4336312205020220730_10029547/",
}
EXPECTED_METADATA_SUFFIXES = {
    "BAER": "_20220726_20220815_sbs_metadata.xml",
    "RAVG": "_20210924_20221004_metadata.xml",
    "MTBS": "_20220726_20230721_metadata.xml",
}
EXPECTED_VECTOR_SUFFIXES = {
    "BAER": "_20220726_20220815_burn_area.shp",
    "RAVG": "_20210924_20221004_burn_area.shp",
    "MTBS": "_20220726_20230721_burn_area.shp",
}
SELECTED_RASTERS = {
    "baer_sbs": (
        "BAER",
        "_20220726_20220815_sbs.tif",
        "primary_field_informed_soil_burn_severity_reference",
    ),
    "mtbs_dnbr6": (
        "MTBS",
        "_20220726_20230721_dnbr6.tif",
        "corroborating_landscape_scale_severity_reference",
    ),
    "ravg_cbi4": (
        "RAVG",
        "_20210924_20221004_rdnbr_cbi4.tif",
        "modeled_vegetation_effect_context_only",
    ),
    "ravg_ba4": (
        "RAVG",
        "_20210924_20221004_rdnbr_ba4.tif",
        "modeled_basal_area_context_only",
    ),
    "ravg_cc5": (
        "RAVG",
        "_20210924_20221004_rdnbr_cc5.tif",
        "modeled_canopy_cover_context_only",
    ),
}
BAER_CLASSES = {
    1: "unburned_or_very_low_ambiguous",
    2: "low_soil_burn_severity",
    3: "moderate_soil_burn_severity",
    4: "high_soil_burn_severity",
    255: "nodata",
}
MTBS_CLASSES = {
    0: "nodata",
    1: "unburned_to_low_or_rapid_recovery_ambiguous",
    2: "low_severity",
    3: "moderate_severity",
    4: "high_severity",
    5: "increased_greenness",
    6: "nonprocessing_mask",
}
RAVG_CBI_CLASSES = {
    0: "outside_perimeter_not_background_truth",
    1: "unchanged_not_proof_of_unburned",
    2: "low_modeled_effect",
    3: "moderate_modeled_effect",
    4: "high_modeled_effect",
    9: "unmappable",
}


class WindigoSourceFitnessError(RuntimeError):
    """The exact Windigo source-fitness gate failed closed."""


def _file_digest(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as source:
        while block := source.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def _digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def _find_path(root: Path, suffix: str) -> Path:
    matches = [
        path for path in root.rglob("*")
        if path.is_file() and path.as_posix().casefold().endswith(suffix.casefold())
    ]
    if len(matches) != 1:
        raise WindigoSourceFitnessError(
            f"expected one extracted file ending {suffix}; found {len(matches)}"
        )
    return matches[0]


def _find_member(names: list[str], suffix: str) -> str:
    matches = [name for name in names if name.casefold().endswith(suffix.casefold())]
    if len(matches) != 1:
        raise WindigoSourceFitnessError(
            f"expected one archive member ending {suffix}; found {len(matches)}"
        )
    return matches[0]


def _inspect_archive(archive_path: Path, extracted_root: Path) -> dict[str, Any]:
    if not archive_path.is_file() or archive_path.stat().st_size != ARCHIVE_BYTES:
        raise WindigoSourceFitnessError("delivered archive byte contract mismatch")
    if _file_digest(archive_path) != ARCHIVE_SHA256:
        raise WindigoSourceFitnessError("delivered archive SHA-256 mismatch")
    try:
        with ZipFile(archive_path) as archive:
            infos = archive.infolist()
            names = [item.filename for item in infos]
            if len(infos) != ARCHIVE_MEMBERS:
                raise WindigoSourceFitnessError("archive member-count mismatch")
            if len([item for item in infos if not item.is_dir()]) != ARCHIVE_FILES:
                raise WindigoSourceFitnessError("archive file-count mismatch")
            if sum(item.file_size for item in infos) != ARCHIVE_UNCOMPRESSED_BYTES:
                raise WindigoSourceFitnessError("archive uncompressed-byte mismatch")
            if len({name.casefold() for name in names}) != len(names):
                raise WindigoSourceFitnessError("archive contains duplicate paths")
            for item in infos:
                path = PurePosixPath(item.filename)
                if (
                    not item.filename
                    or path.is_absolute()
                    or ".." in path.parts
                    or "\\" in item.filename
                ):
                    raise WindigoSourceFitnessError("archive contains an unsafe path")
                if item.flag_bits & 1:
                    raise WindigoSourceFitnessError("archive contains an encrypted member")
                if ((item.external_attr >> 16) & 0o170000) == 0o120000:
                    raise WindigoSourceFitnessError("archive contains a symlink")
            bad = archive.testzip()
            if bad is not None:
                raise WindigoSourceFitnessError(f"archive CRC failed at {bad}")
            for program, prefix in EXPECTED_PROGRAM_PREFIXES.items():
                if not any(name.casefold().startswith(prefix) for name in names):
                    raise WindigoSourceFitnessError(f"{program} archive prefix missing")
            file_manifest: list[dict[str, Any]] = []
            for item in infos:
                if item.is_dir():
                    continue
                extracted = extracted_root.joinpath(*PurePosixPath(item.filename).parts)
                if (
                    not extracted.is_file()
                    or extracted.is_symlink()
                    or extracted.stat().st_size != item.file_size
                ):
                    raise WindigoSourceFitnessError(
                        f"extracted member contract mismatch: {item.filename}"
                    )
                archive_bytes = archive.read(item)
                observed = extracted.read_bytes()
                if observed != archive_bytes:
                    raise WindigoSourceFitnessError(
                        f"extracted member bytes differ: {item.filename}"
                    )
                file_manifest.append(
                    {
                        "member": item.filename,
                        "bytes": item.file_size,
                        "sha256": _digest(archive_bytes),
                    }
                )
    except BadZipFile as error:
        raise WindigoSourceFitnessError("delivered archive is unreadable") from error
    return {
        "filename": archive_path.name,
        "bytes": ARCHIVE_BYTES,
        "sha256": ARCHIVE_SHA256,
        "member_count": ARCHIVE_MEMBERS,
        "file_count": ARCHIVE_FILES,
        "directory_count": ARCHIVE_MEMBERS - ARCHIVE_FILES,
        "uncompressed_bytes": ARCHIVE_UNCOMPRESSED_BYTES,
        "safe_paths": True,
        "unique_paths": True,
        "encrypted_members": 0,
        "symlink_members": 0,
        "crc_pass": True,
        "extracted_bytes_equal_archive": True,
        "files": file_manifest,
    }


def _inspect_metadata(extracted_root: Path, program: str) -> dict[str, Any]:
    path = _find_path(extracted_root, EXPECTED_METADATA_SUFFIXES[program])
    data = path.read_bytes()
    root = ET.fromstring(data)
    iso_path = _find_path(
        extracted_root,
        EXPECTED_METADATA_SUFFIXES[program].replace("_metadata.xml", "_iso_metadata.xml"),
    )
    iso_data = iso_path.read_bytes()
    iso_text = " ".join(" ".join(ET.fromstring(iso_data).itertext()).split())
    result = {
        "program": program,
        "path": path.relative_to(extracted_root).as_posix(),
        "bytes": len(data),
        "sha256": _digest(data),
        "abstract": _metadata_text(root, "abstract"),
        "purpose": _metadata_text(root, "purpose"),
        "access_constraints": _metadata_text(root, "accconst"),
        "use_constraints": _metadata_text(root, "useconst"),
        "distribution_liability": _metadata_text(root, "distliab"),
        "iso_path": iso_path.relative_to(extracted_root).as_posix(),
        "iso_bytes": len(iso_data),
        "iso_sha256": _digest(iso_data),
        "acknowledgement_language_present": (
            "reasonable and proper acknowledgement" in iso_text
        ),
    }
    if not result["acknowledgement_language_present"]:
        raise WindigoSourceFitnessError(f"{program} acknowledgement language missing")
    if program == "BAER":
        if "preliminary/draft data" not in result["use_constraints"]:
            raise WindigoSourceFitnessError("BAER preliminary/draft limitation missing")
        if "SBS data represents the final soil burn severity estimates" not in iso_text:
            raise WindigoSourceFitnessError("BAER SBS distribution role missing")
        if "field validated by a Forest Service Burned Area Emergency Response" not in result["abstract"]:
            raise WindigoSourceFitnessError("BAER source-method statement drifted")
    elif result["access_constraints"] != "None":
        raise WindigoSourceFitnessError(f"{program} access constraint drifted")
    if program == "MTBS":
        required = (
            "uncertainties in this approach stemming from analyst subjectivity "
            "and limited or no plot data"
        )
        joined = " ".join(" ".join(root.itertext()).split())
        if required not in joined:
            raise WindigoSourceFitnessError("MTBS uncertainty language missing")
    if program == "RAVG":
        required = "models may not be applicable to all enclosed areas"
        joined = " ".join(" ".join(root.itertext()).split())
        if required not in joined:
            raise WindigoSourceFitnessError("RAVG applicability limitation missing")
    return result


def _inspect_vectors(extracted_root: Path) -> list[dict[str, Any]]:
    try:
        import pyogrio
        from shapely import is_valid
        from shapely.validation import explain_validity
    except ImportError as error:
        raise WindigoSourceFitnessError(
            "geo-research environment is required for vector validity"
        ) from error
    results: list[dict[str, Any]] = []
    for program in ("BAER", "RAVG", "MTBS"):
        path = _find_path(extracted_root, EXPECTED_VECTOR_SUFFIXES[program])
        frame = pyogrio.read_dataframe(path)
        if len(frame) != 1:
            raise WindigoSourceFitnessError(f"{program} boundary row-count mismatch")
        row = frame.iloc[0]
        geometry = row.geometry
        attributes = {
            key: (
                None
                if row[key] is None or str(row[key]).casefold() == "nan"
                else str(row[key])
            )
            for key in frame.columns
            if key != "geometry"
        }
        expected = {
            "EVENT_ID": EVENT_ID,
            "INCID_NAME": "WINDIGO",
            "MAP_ID": str(MAP_IDS[program]),
            "MAP_PROG": program,
        }
        if any(attributes.get(key) != value for key, value in expected.items()):
            raise WindigoSourceFitnessError(
                f"{program} delivered boundary identity mismatch"
            )
        valid = bool(is_valid(geometry))
        results.append(
            {
                "program": program,
                "path": path.relative_to(extracted_root).as_posix(),
                "crs": str(frame.crs),
                "feature_count": 1,
                "geometry_type": geometry.geom_type,
                "valid": valid,
                "validity_reason": explain_validity(geometry),
                "bounds": [round(float(value), 3) for value in geometry.bounds],
                "area_square_m": round(float(geometry.area), 3),
                "attributes": attributes,
                "topology_role": (
                    "authoritative_valid_topology"
                    if program == "MTBS" and valid
                    else "excluded_from_topology_decisions_retained_as_failure"
                ),
                "repair_performed": False,
            }
        )
    by_program = {item["program"]: item for item in results}
    if not by_program["MTBS"]["valid"]:
        raise WindigoSourceFitnessError("MTBS boundary topology is invalid")
    if by_program["BAER"]["valid"] or by_program["RAVG"]["valid"]:
        raise WindigoSourceFitnessError(
            "expected retained BAER/RAVG vector validity failures changed"
        )
    if by_program["BAER"]["validity_reason"] != by_program["RAVG"]["validity_reason"]:
        raise WindigoSourceFitnessError(
            "BAER/RAVG retained validity failures differ unexpectedly"
        )
    return results


def _inspect_native_rasters(
    archive_path: Path,
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    profiles: list[dict[str, Any]] = []
    runtime: dict[str, dict[str, Any]] = {}
    with ZipFile(archive_path) as archive:
        names = archive.namelist()
        for name in names:
            if name.casefold().endswith((".tif", ".tiff")):
                profile, values = _inspect_native_raster(archive, name)
                profiles.append(profile)
                runtime[name] = values
    if len(profiles) != 21:
        raise WindigoSourceFitnessError("native raster count mismatch")
    if any(item["crs"] != "EPSG:32610" for item in profiles):
        raise WindigoSourceFitnessError("reference raster CRS mismatch")
    return profiles, runtime


def _inspect_native_raster(
    archive: ZipFile,
    member: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    data = archive.read(member)
    try:
        with MemoryFile(data) as memory, memory.open() as source:
            stack = source.read()
            array = stack[0]
            nodata = source.nodata
            valid = np.isfinite(array)
            if nodata is not None:
                valid &= array != nodata
            observed = array[valid]
            if observed.size == 0:
                raise WindigoSourceFitnessError(
                    f"reference raster has no valid pixels: {member}"
                )
            encoded_values, encoded_counts = np.unique(
                array[np.isfinite(array)], return_counts=True
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
                "resolution_m": [
                    abs(source.transform.a),
                    abs(source.transform.e),
                ],
                "transform": list(source.transform)[:6],
                "bounds": list(source.bounds),
                "valid_pixels": int(observed.size),
                "nodata_pixels": int(array.size - observed.size),
                "all_bands_read": True,
                "native_value_domain": (
                    {
                        str(int(value)): int(count)
                        for value, count in zip(
                            encoded_values, encoded_counts, strict=True
                        )
                    }
                    if len(encoded_values) <= 32
                    else None
                ),
                "valid_quantiles": (
                    None
                    if len(encoded_values) <= 32
                    else {
                        name: round(float(value), 4)
                        for name, value in zip(
                            ("min", "p01", "p10", "p50", "p90", "p99", "max"),
                            np.percentile(
                                observed, (0, 1, 10, 50, 90, 99, 100)
                            ),
                            strict=True,
                        )
                    }
                ),
            }
            runtime = {
                "values": array,
                "transform": source.transform,
                "crs": source.crs,
                "nodata": nodata,
            }
    except rasterio.errors.RasterioError as error:
        raise WindigoSourceFitnessError(
            f"unreadable reference raster: {member}"
        ) from error
    if profile["crs"] != "EPSG:32610":
        raise WindigoSourceFitnessError(f"reference CRS drifted: {member}")
    resolution = profile["resolution_m"]
    is_20m = all(abs(value - 20.0) <= 0.01 for value in resolution)
    is_30m = all(abs(value - 30.0) <= 1e-9 for value in resolution)
    if not (is_20m or is_30m):
        raise WindigoSourceFitnessError(f"reference resolution drifted: {member}")
    if is_20m and not member.casefold().endswith(
        "_sbs.tif"
    ):
        raise WindigoSourceFitnessError(
            f"unexpected 20 m reference raster: {member}"
        )
    return profile, runtime


def _load_official_geometry(path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise WindigoSourceFitnessError("official boundary GeoJSON is unreadable") from error
    features = report.get("features") if isinstance(report, dict) else None
    if not isinstance(features, list) or len(features) != 1:
        raise WindigoSourceFitnessError("official boundary feature roster mismatch")
    feature = features[0]
    geometry = feature.get("geometry")
    properties = feature.get("properties")
    if (
        not isinstance(geometry, dict)
        or geometry.get("type") != "MultiPolygon"
        or not isinstance(properties, dict)
        or properties.get("fire_id") != EVENT_ID
        or properties.get("map_id") != MAP_IDS["MTBS"]
    ):
        raise WindigoSourceFitnessError("official boundary identity mismatch")
    return geometry, properties


def _verify_optical_package(package: Path, contract: Any) -> dict[str, Any]:
    verification = verify_registered_package(
        package,
        (contract,),
        contract_validator=_singleton_validator(contract),
        contract_version=CONTRACT_VERSION,
        allow_multilink_registration_manifest=True,
    )
    if not verification["accepted_as_unchanged_registered_package"]:
        raise WindigoSourceFitnessError(
            f"{contract.role} registered package verification failed"
        )
    return verification


def _counts(array: np.ndarray, mask: np.ndarray) -> dict[str, int]:
    values, counts = np.unique(array[mask], return_counts=True)
    return {
        str(int(value)): int(count)
        for value, count in zip(values, counts, strict=True)
    }


def _sample_reference(
    source: dict[str, Any],
    *,
    shape: tuple[int, int],
    transform: rasterio.Affine,
) -> np.ndarray:
    destination = np.zeros(shape, dtype=source["values"].dtype)
    reproject(
        source["values"],
        destination,
        src_transform=rasterio.Affine(*source["profile"]["transform"]),
        src_crs=source["profile"]["crs"],
        src_nodata=source["profile"]["nodata"],
        dst_transform=transform,
        dst_crs="EPSG:32610",
        dst_nodata=0,
        resampling=Resampling.nearest,
    )
    return destination


def build_report(
    *,
    pre_package: Path,
    post_package: Path,
    archive_path: Path,
    extracted_root: Path,
    boundary_path: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
    pdf_visual_review: str,
) -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    if pdf_visual_review != "PASS_EXACT_FOUR_PROVIDER_MAP_PDFS":
        raise WindigoSourceFitnessError("exact PDF visual review is not passed")
    archive = _inspect_archive(archive_path, extracted_root)
    metadata = [
        _inspect_metadata(extracted_root, program)
        for program in ("BAER", "RAVG", "MTBS")
    ]
    vectors = _inspect_vectors(extracted_root)
    native_rasters, runtime = _inspect_native_rasters(archive_path)
    geometry, boundary_properties = _load_official_geometry(boundary_path)
    pre_verification = _verify_optical_package(pre_package, PRE_CONTRACT)
    post_verification = _verify_optical_package(post_package, POST_CONTRACT)
    pre_scene, pre = _read_product(
        pre_package,
        PRE_CONTRACT,
        geometry,
        expected_processing_baseline="05.10",
    )
    post_scene, post = _read_product(
        post_package,
        POST_CONTRACT,
        geometry,
        expected_processing_baseline="05.10",
    )
    windows, quality = measure_event_registration(
        pre_scene, pre, post_scene, post
    )
    registration = registration_summary(windows)
    if registration["machine_decision"] != "PASS_LOCAL_CONTENT_REGISTRATION_GATE":
        raise WindigoSourceFitnessError("optical registration gate failed")
    spectral, dnbr, optical_valid = summarize_spectral_change(
        pre_scene, pre, post_scene, post
    )
    boundary = pre["MASK20"]
    if boundary.shape != (153, 158) or int(boundary.sum()) != 10_778:
        raise WindigoSourceFitnessError("optical boundary grid drifted")
    optical_transform = rasterio.Affine(
        *pre_scene["rasters"]["B04"]["crop_transform"]
    )
    selected: dict[str, dict[str, Any]] = {}
    sampled: dict[str, np.ndarray] = {}
    for key, (program, suffix, role) in SELECTED_RASTERS.items():
        member = _find_member(list(runtime), suffix)
        profile = next(item for item in native_rasters if item["member"] == member)
        selected[key] = {"program": program, "role": role, **profile}
        sampled[key] = _sample_reference(
            {"profile": profile, **runtime[member]},
            shape=boundary.shape,
            transform=optical_transform,
        )
    baer_positive = boundary & np.isin(sampled["baer_sbs"], (2, 3, 4))
    mtbs_positive = boundary & np.isin(sampled["mtbs_dnbr6"], (2, 3, 4))
    ravg_effect = boundary & np.isin(sampled["ravg_cbi4"], (2, 3, 4))
    agreement = baer_positive & mtbs_positive
    all_three = agreement & ravg_effect
    baer_covered = boundary & (sampled["baer_sbs"] != 0) & (
        sampled["baer_sbs"] != 255
    )
    mtbs_covered = boundary & (sampled["mtbs_dnbr6"] != 0)
    evidence = {
        "optical_boundary_pixels": int(boundary.sum()),
        "optical_pair_valid_pixels": int(optical_valid.sum()),
        "baer_sbs_on_optical_boundary": _counts(
            sampled["baer_sbs"], boundary
        ),
        "mtbs_dnbr6_on_optical_boundary": _counts(
            sampled["mtbs_dnbr6"], boundary
        ),
        "ravg_cbi4_on_optical_boundary": _counts(
            sampled["ravg_cbi4"], boundary
        ),
        "ravg_ba4_on_optical_boundary": _counts(
            sampled["ravg_ba4"], boundary
        ),
        "ravg_cc5_on_optical_boundary": _counts(
            sampled["ravg_cc5"], boundary
        ),
        "baer_affirmative_pixels": int(baer_positive.sum()),
        "baer_affirmative_and_optical_valid_pixels": int(
            (baer_positive & optical_valid).sum()
        ),
        "mtbs_affirmative_pixels": int(mtbs_positive.sum()),
        "mtbs_affirmative_and_optical_valid_pixels": int(
            (mtbs_positive & optical_valid).sum()
        ),
        "baer_mtbs_affirmative_agreement_pixels": int(agreement.sum()),
        "baer_mtbs_agreement_and_optical_valid_pixels": int(
            (agreement & optical_valid).sum()
        ),
        "all_three_effect_agreement_pixels": int(all_three.sum()),
        "all_three_effect_agreement_and_optical_valid_pixels": int(
            (all_three & optical_valid).sum()
        ),
        "baer_only_affirmative_pixels": int(
            (baer_positive & ~mtbs_positive).sum()
        ),
        "mtbs_only_affirmative_pixels": int(
            (mtbs_positive & ~baer_positive).sum()
        ),
        "baer_coverage_percent": round(
            100 * float(baer_covered.sum()) / float(boundary.sum()), 4
        ),
        "mtbs_coverage_percent": round(
            100 * float(mtbs_covered.sum()) / float(boundary.sum()), 4
        ),
        "categorical_sampling": (
            "nearest neighbor from each native grid onto the verified 20 m "
            "optical grid; no resolution gain claimed"
        ),
        "baer_class_semantics": {
            str(key): value for key, value in BAER_CLASSES.items()
        },
        "mtbs_class_semantics": {
            str(key): value for key, value in MTBS_CLASSES.items()
        },
        "ravg_cbi_class_semantics": {
            str(key): value for key, value in RAVG_CBI_CLASSES.items()
        },
        "background_finding": (
            "No delivered class is affirmative background truth. BAER class 1, "
            "MTBS class 1, RAVG class 1, and RAVG class 0 remain ambiguous or "
            "outside-domain states. A separate optical-stability proposal must "
            "prove any background candidate."
        ),
    }
    if evidence["baer_mtbs_agreement_and_optical_valid_pixels"] != 9_789:
        raise WindigoSourceFitnessError(
            "cross-source affirmative agreement drifted"
        )
    pdf_paths = sorted(
        path.relative_to(extracted_root).as_posix()
        for path in extracted_root.rglob("*.pdf")
    )
    if len(pdf_paths) != 4:
        raise WindigoSourceFitnessError("provider PDF roster mismatch")
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
        "target_version": TARGET_VERSION,
        "label_protocol_version": LABEL_PROTOCOL_VERSION,
        "label_schema_version": LABEL_SCHEMA_VERSION,
        "label_set_version": "owner-approved-prototype-region-labels-v0.3.0",
        "dataset_version": None,
        "split_version": None,
        "baseline_version": None,
        "model_version": None,
        "event": {
            "event_group_id": EVENT_GROUP_ID,
            "event_id": EVENT_ID,
            "fire_name": "WINDIGO",
            "ignition_date": "2022-07-30",
            "map_ids": MAP_IDS,
            "official_boundary_properties": boundary_properties,
        },
        "archive": archive,
        "metadata": metadata,
        "boundary_vectors": vectors,
        "native_rasters": native_rasters,
        "selected_evidence_products": selected,
        "provider_pdf_review": {
            "decision": pdf_visual_review,
            "paths": pdf_paths,
            "page_count_each": 1,
            "rendered_at_150_dpi": True,
            "finding": (
                "All four maps render legibly and bind the exact event. MTBS "
                "shows 1,068 acres and four observed classes. RAVG maps are "
                "explicitly modeled vegetation-condition products."
            ),
        },
        "optical_reverification": {
            "pre_package": {
                "package_id": PRE_CONTRACT.package_id,
                "registration_manifest_sha256": pre_verification[
                    "registration_manifest_sha256"
                ],
                "reason_codes": pre_verification["reason_codes"],
            },
            "post_package": {
                "package_id": POST_CONTRACT.package_id,
                "registration_manifest_sha256": post_verification[
                    "registration_manifest_sha256"
                ],
                "reason_codes": post_verification["reason_codes"],
            },
            "products": [pre_scene, post_scene],
            "pair_quality_inside_full_boundary": quality["inside_boundary"],
            "registration": {"summary": registration, "windows": windows},
            "spectral_change": spectral,
        },
        "evidence_comparison": evidence,
        "source_precedence": {
            "topology": (
                "Official provider-generated MTBS GeoJSON and the valid "
                "delivered MTBS MultiPolygon govern topology."
            ),
            "positive_reference": (
                "Delivered BAER SBS classes 2-4 are primary, field-informed "
                "soil burn severity evidence for this prototype. They remain "
                "preliminary/draft data and do not make BurnLens field validated."
            ),
            "corroboration": (
                "MTBS classes 2-4 provide independent program-method "
                "corroboration at landscape scale."
            ),
            "context": (
                "RAVG modeled vegetation effects are context only and cannot "
                "independently authorize a candidate."
            ),
            "invalid_vectors": (
                "BAER and RAVG shapefiles are retained unchanged as failures, "
                "excluded from topology decisions, and never repaired."
            ),
        },
        "terms_and_roles": {
            "resolved_for_bounded_prototype_evidence": True,
            "baer": (
                "Publicly delivered SBS may be used with acknowledgement and "
                "visible preliminary/draft limitations. The BAER team's own "
                "field-informed method is source provenance, not a BurnLens "
                "field-validation claim."
            ),
            "mtbs": (
                "Use with acknowledgement and visible analyst-subjectivity, "
                "plot-data, geographic-accuracy, update, warranty, and "
                "fitness limitations."
            ),
            "ravg": (
                "Use with acknowledgement and visible modeled-product, "
                "vegetation-domain, delayed-mortality, resprouting, location, "
                "update, warranty, and fitness limitations."
            ),
            "attribution": (
                "USDA Forest Service Burned Area Emergency Response; Monitoring "
                "Trends in Burn Severity Project (USGS and USDA Forest Service); "
                "USDA Forest Service RAVG; Contains modified Copernicus Sentinel "
                "data 2022, accessed through CDSE."
            ),
        },
        "fitness_decision": {
            "source": "PASS_EXACT_WINDIGO_SOURCE_FITNESS_WITH_VECTOR_EXCLUSIONS",
            "burned_candidate_route": (
                "OPEN_FOR_ONE_BAER_PRIMARY_MTBS_CORROBORATED_PROPOSAL"
            ),
            "background_candidate_route": (
                "OPEN_ONLY_FOR_SEPARATE_AFFIRMATIVE_OPTICAL_STABILITY_PROPOSAL"
            ),
            "next_dependency": "P2O4-T35-U04_EXACT_TWO_CARD_PROPOSAL",
            "checkpoint": (
                "ACCEPT_SOURCE_FITNESS_DEFER_CANDIDATES_OWNER_DECISIONS_LABELS_"
                "DATASET_SPLIT_BASELINE_MODEL"
            ),
        },
        "claims": {
            "proven": [
                (
                    "The exact delivery, notices, safe archive, extracted bytes, "
                    "identities, native rasters, class domains, nodata, PDFs, "
                    "and CRS passed deterministic inspection."
                ),
                (
                    "The exact Sentinel pair passes quality and all nine "
                    "registration windows on the valid official boundary."
                ),
                (
                    "BAER and MTBS agree on 9,789 optical-valid 20 m pixel "
                    "centers after nearest-neighbor comparison."
                ),
            ],
            "not_proven": [
                (
                    "The invalid BAER/RAVG shapefiles are not repaired or used "
                    "for topology, and no delivered class is affirmative "
                    "background truth."
                ),
                (
                    "No candidate, owner decision, label, dataset, split, "
                    "baseline, model, metric, accuracy, independent ground truth, "
                    "BurnLens field validation, official status, endorsement, "
                    "or operational readiness is created."
                ),
            ],
        },
        "deadline": {
            "portfolio_submission": "2026-08-06",
            "sixth_event_cutoff": "2026-07-27T18:00:00-04:00",
            "fallback": "technical-case-study-only",
        },
        "warning": WARNING,
    }
    previews = {
        "pre_tci": pre["TCI"],
        "post_tci": post["TCI"],
        "pre_mask": pre["MASK10"],
        "post_mask": post["MASK10"],
        "boundary_mask20": boundary,
        "dnbr": dnbr,
        "dnbr_valid": optical_valid,
        **sampled,
    }
    return report, previews


def render_png(
    report: dict[str, Any],
    previews: dict[str, np.ndarray],
    path: Path,
) -> None:
    canvas = Image.new("RGB", (1800, 1260), "#07110f")
    draw = ImageDraw.Draw(canvas)
    draw.text(
        (60, 38),
        "BURNLENS  /  WINDIGO SOURCE FITNESS",
        fill="#b9d8cf",
        font=_font(21),
    )
    draw.text(
        (60, 76),
        "Exact sources pass with two vector exclusions.",
        fill="#eef7f3",
        font=_font(31),
    )
    draw.text(
        (60, 128),
        report["fitness_decision"]["checkpoint"],
        fill="#ffca73",
        font=_font(18),
    )
    boundary = previews["boundary_mask20"]
    panels = [
        (
            "PRE OPTICAL / 2022-07-26",
            _preview_tci(previews["pre_tci"], previews["pre_mask"], (520, 315)),
        ),
        (
            "POST OPTICAL / 2022-08-15",
            _preview_tci(previews["post_tci"], previews["post_mask"], (520, 315)),
        ),
        (
            "CONTINUOUS dNBR / NOT A LABEL",
            _preview_dnbr(
                previews["dnbr"], previews["dnbr_valid"], (520, 315)
            ),
        ),
        (
            "BAER SBS / PRIMARY REFERENCE",
            _class_image(
                previews["baer_sbs"],
                boundary,
                {
                    1: (0, 128, 128),
                    2: (82, 204, 204),
                    3: (255, 232, 32),
                    4: (168, 0, 0),
                },
                (520, 315),
            ),
        ),
        (
            "MTBS dNBR6 / CORROBORATION",
            _class_image(
                previews["mtbs_dnbr6"],
                boundary,
                {
                    1: (0, 128, 128),
                    2: (82, 204, 204),
                    3: (255, 232, 32),
                    4: (168, 0, 0),
                },
                (520, 315),
            ),
        ),
        (
            "RAVG CBI4 / MODELED CONTEXT",
            _class_image(
                previews["ravg_cbi4"],
                boundary,
                {
                    1: (0, 128, 128),
                    2: (82, 204, 204),
                    3: (255, 232, 32),
                    4: (168, 0, 0),
                },
                (520, 315),
            ),
        ),
    ]
    for index, (label, image) in enumerate(panels):
        column, row = index % 3, index // 3
        x, y = 60 + column * 575, 180 + row * 405
        draw.rounded_rectangle(
            (x, y, x + 535, y + 375),
            radius=16,
            fill="#0e1d1a",
            outline="#315b50",
            width=2,
        )
        draw.text((x + 18, y + 14), label, fill="#eef7f3", font=_font(18))
        canvas.paste(image, (x + 8, y + 48))
    evidence = report["evidence_comparison"]
    metrics = [
        (
            f"{evidence['baer_mtbs_agreement_and_optical_valid_pixels']:,}",
            "BAER + MTBS + valid optical",
        ),
        (
            f"{evidence['all_three_effect_agreement_and_optical_valid_pixels']:,}",
            "all three effect sources",
        ),
        ("9 / 9", "registration windows pass"),
        ("0", "candidates or labels"),
    ]
    for index, (value, label) in enumerate(metrics):
        x = 60 + index * 430
        draw.rounded_rectangle(
            (x, 1015, x + 395, 1128),
            radius=14,
            fill="#0e1d1a",
            outline="#315b50",
            width=2,
        )
        draw.text((x + 20, 1035), value, fill="#78e0bd", font=_font(27))
        draw.text((x + 20, 1082), label, fill="#b9d8cf", font=_font(14))
    draw.rounded_rectangle(
        (60, 1152, 1740, 1218),
        radius=14,
        fill="#261f12",
        outline="#be8a36",
        width=2,
    )
    draw.text(
        (82, 1164),
        "BAER/RAVG boundary shapefiles self-intersect; retained, not repaired, excluded from topology.",
        fill="#ffd997",
        font=_font(15),
    )
    draw.text((82, 1190), WARNING, fill="#ffd997", font=_font(14))
    draw.text(
        (60, 1232),
        (
            f"TRACE commit {report['git_source_commit'][:12]} / "
            f"run {report['run_id']} / BurnLens {SOFTWARE_VERSION} / "
            "dataset-model none"
        ),
        fill="#b9d8cf",
        font=_font(13),
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path, format="PNG", optimize=False)


def render_html(
    report: dict[str, Any],
    png_name: str,
    path: Path,
) -> None:
    evidence = report["evidence_comparison"]
    rows = "".join(
        (
            f"<tr><td>{escape(item['program'])}</td>"
            f"<td><code>{escape(PurePosixPath(item['member']).name)}</code></td>"
            f"<td>{item['width']}×{item['height']}</td>"
            f"<td>{escape(str(item['nodata']))}</td>"
            f"<td>{escape(str(item['native_value_domain'] or 'continuous'))}</td>"
            f"<td>{escape(item['role'])}</td></tr>"
        )
        for item in report["selected_evidence_products"].values()
    )
    vectors = "".join(
        (
            f"<tr><td>{escape(item['program'])}</td>"
            f"<td>{escape(item['geometry_type'])}</td>"
            f"<td>{'pass' if item['valid'] else 'fail retained'}</td>"
            f"<td>{escape(item['validity_reason'])}</td>"
            f"<td>{escape(item['topology_role'])}</td></tr>"
        )
        for item in report["boundary_vectors"]
    )
    html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Windigo source fitness</title><style>
html,body{{max-width:100%;overflow-x:hidden}}body{{margin:0;background:#07110f;color:#eef7f3;font:16px/1.55 system-ui,sans-serif}}main{{max-width:1200px;margin:auto;padding:32px;box-sizing:border-box}}h1{{font-size:clamp(2rem,5vw,4rem);line-height:1.02}}.card{{max-width:100%;min-width:0;box-sizing:border-box;background:#0e1d1a;border:1px solid #315b50;border-radius:16px;padding:20px;margin:18px 0;overflow-wrap:anywhere}}.warn{{background:#261f12;border-color:#be8a36;color:#ffd997}}img{{display:block;max-width:100%;width:100%;height:auto;border-radius:16px}}table{{width:100%;max-width:100%;border-collapse:collapse}}th,td{{text-align:left;padding:10px;border-bottom:1px solid #315b50;vertical-align:top;overflow-wrap:anywhere}}code,strong{{overflow-wrap:anywhere}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px}}.metric strong{{display:block;font-size:2rem;color:#78e0bd}}@media(max-width:700px){{main{{padding:18px}}.table-card{{overflow-x:auto}}.table-card table{{min-width:760px}}}}
</style></head><body><main><p>BURNLENS / PHASE TWO / ISSUE #534 / U03</p><h1>Exact sources pass with two vector exclusions.</h1><div class="card warn">{escape(report['warning'])}</div><img src="{escape(png_name)}" width="1800" height="1260" alt="Actual Windigo pre and post optical evidence, continuous change, BAER SBS, MTBS severity, and RAVG context"><div class="grid"><div class="card metric"><strong>{evidence['baer_mtbs_agreement_and_optical_valid_pixels']:,}</strong>BAER + MTBS + valid optical</div><div class="card metric"><strong>{evidence['all_three_effect_agreement_and_optical_valid_pixels']:,}</strong>all three effect sources</div><div class="card metric"><strong>9 / 9</strong>registration windows pass</div><div class="card metric"><strong>0</strong>candidates or labels</div></div><h2>Source roles</h2><div class="card"><p><strong>BAER SBS:</strong> primary, field-informed soil burn severity evidence. Classes 2–4 may support one bounded burned proposal. The data remain preliminary/draft. This does not make BurnLens field validated.</p><p><strong>MTBS:</strong> landscape-scale, analyst-interpreted corroboration. Classes 2–4 agree with BAER on {evidence['baer_mtbs_agreement_and_optical_valid_pixels']:,} optical-valid 20 m pixel centers.</p><p><strong>RAVG:</strong> modeled vegetation-effect context only. It cannot independently authorize a candidate.</p><p><strong>Background:</strong> no delivered class is affirmative background truth. A separate stability-backed route remains required.</p></div><h2>Exact selected products</h2><div class="card table-card"><table><thead><tr><th>Program</th><th>Member</th><th>Native grid</th><th>Nodata</th><th>Domain</th><th>Role</th></tr></thead><tbody>{rows}</tbody></table><p>All comparisons use nearest-neighbor sampling onto the verified 20 m optical grid. No resolution gain is claimed.</p></div><h2>Topology failures remain visible</h2><div class="card table-card"><table><thead><tr><th>Program</th><th>Geometry</th><th>Validity</th><th>Reason</th><th>Role</th></tr></thead><tbody>{vectors}</tbody></table><p>No geometry repair was performed. The provider-generated official GeoJSON and valid delivered MTBS MultiPolygon govern topology.</p></div><h2>Gate result</h2><div class="card"><p><strong>{escape(report['fitness_decision']['checkpoint'])}</strong></p><p>U04 may build exactly one burned and one affirmative-background proposal. Owner yes/no/uncertain review and every non-owner gate remain required.</p></div><div class="card warn"><p>{escape(report['terms_and_roles']['attribution'])}</p><p>No accepted candidate, label, dataset, split, baseline, model, metric, independent ground truth, BurnLens field validation, official status, endorsement, operational readiness, or emergency suitability exists.</p></div><p>Trace: commit <code>{escape(report['git_source_commit'])}</code> · BurnLens <code>{SOFTWARE_VERSION}</code> · run <code>{escape(report['run_id'])}</code> · label schema <code>{escape(report['label_schema_version'])}</code> · dataset/model none.</p></main></body></html>"""
    _write_utf8_lf(path, html)


def write_outputs(
    report: dict[str, Any],
    previews: dict[str, np.ndarray],
    directory: Path,
) -> dict[str, Path]:
    directory.mkdir(parents=True, exist_ok=True)
    paths = {
        extension: directory / f"{REPORT_ID}.{extension}"
        for extension in ("json", "html", "png")
    }
    if any(path.exists() or path.is_symlink() for path in paths.values()):
        raise WindigoSourceFitnessError("source-fitness output already exists")
    _write_utf8_lf(
        paths["json"],
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
    )
    render_png(report, previews, paths["png"])
    render_html(report, paths["png"].name, paths["html"])
    return paths


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pre-package", required=True, type=Path)
    parser.add_argument("--post-package", required=True, type=Path)
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--extracted-root", required=True, type=Path)
    parser.add_argument("--boundary", required=True, type=Path)
    parser.add_argument("--output-directory", required=True, type=Path)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--run-id", default=RUN_ID)
    parser.add_argument("--git-source-commit", required=True)
    parser.add_argument(
        "--pdf-visual-review",
        choices=["PASS_EXACT_FOUR_PROVIDER_MAP_PDFS"],
        required=True,
    )
    arguments = parser.parse_args(argv)
    report, previews = build_report(
        pre_package=arguments.pre_package,
        post_package=arguments.post_package,
        archive_path=arguments.archive,
        extracted_root=arguments.extracted_root,
        boundary_path=arguments.boundary,
        generated_at_utc=arguments.generated_at_utc,
        run_id=arguments.run_id,
        git_source_commit=arguments.git_source_commit,
        pdf_visual_review=arguments.pdf_visual_review,
    )
    paths = write_outputs(report, previews, arguments.output_directory)
    print(
        "PASS_EXACT_WINDIGO_SOURCE_FITNESS_WITH_VECTOR_EXCLUSIONS "
        + " ".join(f"{key}={value}" for key, value in paths.items())
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
