"""Measure exact Petes Lake optical, MTBS, and NWI reference fitness.

This U05 evidence accepts bounded reference pixels only for later candidate
proposal.  It never creates a candidate, label, background truth, dataset,
split, baseline, model, or operational product.
"""

from __future__ import annotations

from collections import Counter
from datetime import date, datetime
from hashlib import sha256
from html import escape
from io import BytesIO
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
from typing import Any, Iterable
from zipfile import ZipFile

import numpy as np
from PIL import Image, ImageDraw
import pyogrio
from pyproj import Transformer
import rasterio
from rasterio.features import rasterize
from rasterio.io import MemoryFile
from shapely.geometry import LinearRing, MultiPolygon, Polygon, mapping
from shapely.ops import transform as transform_geometry, unary_union

from .green_ridge_source_fitness import _preview_dnbr, _preview_tci
from .optical_pair_evidence import WARNING, _font, classify_pair_quality
from .petes_lake_reference_native_contract import (
    ARCHIVE_BYTES,
    ARCHIVE_SHA256,
    EXPECTED_MEMBERS,
    MTBS_CLASS_SEMANTICS,
    build_report as build_u04_report,
    inspect_native_archive,
)
from .petes_lake_reference_request import CUSTODY_PATHS
from .petes_lake_replacement_source_fitness import (
    build_report as build_u03_report,
)
from .petes_lake_source_fitness import _render_png_bytes as render_u03_png_bytes
from .petes_lake_wetland_custody import (
    CONTRACT_PATH as NWI_CONTRACT_PATH,
    CUSTODY_ROOT as NWI_CUSTODY_ROOT,
    LIMITATIONS_REFERENCE,
    MAX_ACCEPTED_SOURCE_SCALE,
    QUERY_CONTEXT_BUFFER_METERS,
    RUN_ID as NWI_RUN_ID,
    SOURCE_TYPE_RENDERER_VALUES,
    TERMS_REFERENCE as NWI_TERMS_REFERENCE,
    USER_CAUTION_REFERENCE,
    UNIT_ID as NWI_CUSTODY_UNIT_ID,
    WEB_SERVICE_REFERENCE,
    _normalize_attributes,
    _validate_layer_metadata,
    validate_finalized_contract,
)


SOFTWARE_VERSION = "0.44.0"
REPORT_ID = "PETES-LAKE-REFERENCE-FITNESS-2026-001"
REPORT_VERSION = "petes-lake-reference-fitness-v0.1.0"
PROTOCOL_VERSION = "petes-lake-reference-fitness-protocol-v0.1.0"
UNIT_ID = "P2O4-T33-U05"
RUN_ID = "BL-2026-07-21-petes-lake-reference-fitness-r001"
PREVIEW_RUN_ID = "BL-2026-07-21-petes-lake-reference-fitness-preview-r001"
BRANCH = "codex/p2o4-t33-petes-lake-milestone"
TASK_ISSUE = 521
GRID_SHAPE = (259, 349)
GRID_TRANSFORM = rasterio.Affine(20, 0, 584_560, 0, -20, 4_871_520)
GRID_CRS = "EPSG:32610"
UNCOVERED = 255
PIXEL_HALF_DIAGONAL_METERS = float(np.hypot(GRID_TRANSFORM.a, GRID_TRANSFORM.e) / 2.0)
PLAN_PATH = Path("samples/cross-event/phase-two/ADDITIONAL-EVENT-GROUP-PLAN-2026-001.json")
U03_CUSTODY_PATH = Path(
    "samples/cross-event/phase-two/petes-lake/"
    "PETES-LAKE-OPTICAL-REMEDIATION-CUSTODY-2026-001.json"
)
U03_FAILED_PATH = Path(
    "samples/cross-event/phase-two/petes-lake/PETES-LAKE-SOURCE-FITNESS-2026-001.json"
)
U03_SELECTION_PATH = Path(
    "samples/cross-event/phase-two/petes-lake/PETES-LAKE-SOURCE-REMEDIATION-2026-001.json"
)
U03_JSON_PATH = Path(
    "samples/cross-event/phase-two/petes-lake/"
    "PETES-LAKE-REPLACEMENT-SOURCE-FITNESS-2026-001.json"
)
U03_PNG_PATH = U03_JSON_PATH.with_suffix(".png")
U03_JSON_BYTES = 60_069
U03_JSON_SHA256 = "1aa88c0021c610e492d2645e3f2c49a4afe96d9d907e2ee4481948a4c58f2ebd"
U03_PNG_BYTES = 588_891
U03_PNG_SHA256 = "fd5b9ae54e1b9c3e0d495e337387d874ae911bd0f586e835b4184312d486d931"
U04_JSON_PATH = Path(
    "samples/cross-event/phase-two/petes-lake/"
    "PETES-LAKE-REFERENCE-NATIVE-CONTRACT-2026-001.json"
)
U04_JSON_BYTES = 32_991
U04_JSON_SHA256 = "b489bd30b467ab38f7320c9b313f904e0bbe9a33e2bed8b346230b9f48a6053c"
FINAL_DIRECTORY = Path("samples/cross-event/phase-two/petes-lake")
PREVIEW_DIRECTORY = Path(
    "downloads/phase-two/runs/P2O4-T33-U05/petes-lake-reference-fitness-preview-r001"
)
NWI_CATALOG_DOI = "10.7944/usfws.nwi.202605"
NWI_CATALOG_RELEASE = "2026-05-08"
VISUAL_PENDING = "PENDING_ACTUAL_PETES_LAKE_REFERENCE_RENDER_REVIEW"
VISUAL_PASS = "PASS_ACTUAL_PETES_LAKE_REFERENCE_RENDER_REVIEW"
VISUAL_FAIL = "FAIL_ACTUAL_PETES_LAKE_REFERENCE_RENDER_REVIEW"
VISUAL_PASS_NOTE = (
    "PASS_ORIGINAL_RESOLUTION_U05_RENDER_LEGIBLE_CONSISTENT_UNCLIPPED_"
    "AND_WITHOUT_MISLEADING_DISPLAY_ARTIFACT"
)
VISUAL_FAIL_NOTE = (
    "FAIL_ORIGINAL_RESOLUTION_U05_RENDER_REVIEW_WITH_EXACT_FAILURE_"
    "RETAINED_IN_THE_ASSOCIATED_REVIEW_RECORD"
)


class PetesLakeReferenceFitnessError(RuntimeError):
    """Exact U05 reference fitness failed closed."""


def _digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def _exact_bytes(path: Path, size: int, digest: str, label: str) -> bytes:
    try:
        data = path.read_bytes()
    except OSError as error:
        raise PetesLakeReferenceFitnessError(f"{label} is unreadable") from error
    if len(data) != size or _digest(data) != digest:
        raise PetesLakeReferenceFitnessError(f"{label} byte identity changed")
    return data


def _exact_json(path: Path, size: int, digest: str, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(_exact_bytes(path, size, digest, label))
    except json.JSONDecodeError as error:
        raise PetesLakeReferenceFitnessError(f"{label} is not JSON") from error
    if not isinstance(payload, dict):
        raise PetesLakeReferenceFitnessError(f"{label} is not an object")
    return payload


def _canonical_report_bytes(report: dict[str, Any]) -> bytes:
    return (json.dumps(report, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def _utc_z(value: Any, label: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise PetesLakeReferenceFitnessError(f"{label} must be an exact UTC Z timestamp")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as error:
        raise PetesLakeReferenceFitnessError(
            f"{label} must be an exact UTC Z timestamp"
        ) from error
    if parsed.utcoffset() is None or parsed.utcoffset().total_seconds() != 0:
        raise PetesLakeReferenceFitnessError(f"{label} must be UTC")
    return parsed


def _replay_u03(root: Path) -> tuple[dict[str, Any], dict[str, np.ndarray], dict[str, Any]]:
    tracked = _exact_json(root / U03_JSON_PATH, U03_JSON_BYTES, U03_JSON_SHA256, "U03 report")
    tracked_png = _exact_bytes(root / U03_PNG_PATH, U03_PNG_BYTES, U03_PNG_SHA256, "U03 render")
    visual = tracked.get("visual_review", {})
    replay, previews = build_u03_report(
        repository_root=root,
        plan_path=root / PLAN_PATH,
        custody_report_path=root / U03_CUSTODY_PATH,
        failed_report_path=root / U03_FAILED_PATH,
        selection_report_path=root / U03_SELECTION_PATH,
        generated_at_utc=tracked["generated_at_utc"],
        run_id=tracked["run_id"],
        git_source_commit=tracked["git_source_commit"],
        visual_review_decision=visual["decision"],
        visual_review_notes=visual["notes"],
    )
    replay_json = _canonical_report_bytes(replay)
    replay_png = render_u03_png_bytes(replay, previews)
    if replay_json != (root / U03_JSON_PATH).read_bytes() or replay_png != tracked_png:
        raise PetesLakeReferenceFitnessError("U03 exact JSON/PNG replay changed")
    if (
        replay["fitness_decision"]["optical_source"]
        != "PASS_EXACT_PETES_LAKE_REPLACEMENT_OPTICAL_SOURCE_FITNESS_WITH_SPATIAL_EXCLUSIONS"
        or replay["fitness_decision"]["u04_authorized"] is not True
    ):
        raise PetesLakeReferenceFitnessError("U03 pass-with-exclusions gate changed")
    return replay, previews, {
        "report_bytes": len(replay_json),
        "report_sha256": _digest(replay_json),
        "render_bytes": len(replay_png),
        "render_sha256": _digest(replay_png),
        "byte_identical": True,
    }


def _replay_u04(root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    tracked = _exact_json(root / U04_JSON_PATH, U04_JSON_BYTES, U04_JSON_SHA256, "U04 report")
    replay = build_u04_report(
        repository_root=root,
        generated_at_utc=tracked["generated_at_utc"],
        run_id=tracked["run_id"],
        git_source_commit=tracked["git_source_commit"],
    )
    data = _canonical_report_bytes(replay)
    if data != (root / U04_JSON_PATH).read_bytes():
        raise PetesLakeReferenceFitnessError("U04 exact JSON replay changed")
    if replay["decision"]["accepted_reference_pixels"] != 0:
        raise PetesLakeReferenceFitnessError("U04 zero-reference boundary changed")
    return replay, {"report_bytes": len(data), "report_sha256": _digest(data), "byte_identical": True}


def _sample_nearest(
    values: np.ndarray,
    source_transform: rasterio.Affine,
    source_nodata: int | float | None,
) -> np.ndarray:
    rows, columns = np.indices(GRID_SHAPE)
    xs = GRID_TRANSFORM.c + (columns + 0.5) * GRID_TRANSFORM.a
    ys = GRID_TRANSFORM.f + (rows + 0.5) * GRID_TRANSFORM.e
    source_columns = np.floor((xs - source_transform.c) / source_transform.a).astype(int)
    source_rows = np.floor((source_transform.f - ys) / abs(source_transform.e)).astype(int)
    inside = (
        (source_rows >= 0)
        & (source_rows < values.shape[0])
        & (source_columns >= 0)
        & (source_columns < values.shape[1])
    )
    sampled = np.full(GRID_SHAPE, UNCOVERED, dtype=np.uint8)
    sampled[inside] = values[source_rows[inside], source_columns[inside]].astype(np.uint8)
    if source_nodata is not None:
        sampled[sampled == int(source_nodata)] = UNCOVERED
    return sampled


def _vsi_path(archive: Path, member: str) -> str:
    return f"/vsizip/{archive.resolve().as_posix()}/{member}"


def _read_vector_geometries(archive: Path, member: str) -> list[Any]:
    frame = pyogrio.read_dataframe(_vsi_path(archive, member), columns=[])
    if frame.crs is None or frame.crs.to_epsg() != 32610 or frame.empty:
        raise PetesLakeReferenceFitnessError("MTBS vector CRS or geometry roster changed")
    geometries = [item for item in frame.geometry if item is not None and not item.is_empty]
    if len(geometries) != len(frame) or any(not item.is_valid for item in geometries):
        raise PetesLakeReferenceFitnessError("MTBS vector geometry is invalid")
    return geometries


def _rasterize(geometries: Iterable[Any], *, all_touched: bool = False) -> np.ndarray:
    shapes = [(mapping(item), 1) for item in geometries]
    if not shapes:
        return np.zeros(GRID_SHAPE, dtype=bool)
    return rasterize(
        shapes,
        out_shape=GRID_SHAPE,
        transform=GRID_TRANSFORM,
        fill=0,
        all_touched=all_touched,
        dtype="uint8",
    ).astype(bool)


def _esri_rings_geometry(rings: Any) -> Any:
    if not isinstance(rings, list) or not rings:
        raise PetesLakeReferenceFitnessError("NWI polygon rings are absent")
    outers: list[tuple[Polygon, list[list[float]]]] = []
    holes: list[tuple[Polygon, list[list[float]]]] = []
    for coordinates in rings:
        if not isinstance(coordinates, list) or len(coordinates) < 4:
            raise PetesLakeReferenceFitnessError("NWI polygon ring is malformed")
        points = [[float(point[0]), float(point[1])] for point in coordinates]
        if points[0] != points[-1]:
            raise PetesLakeReferenceFitnessError("NWI polygon ring is not closed")
        ring = LinearRing(points)
        polygon = Polygon(points)
        if not ring.is_valid or not polygon.is_valid or polygon.area <= 0:
            raise PetesLakeReferenceFitnessError("NWI polygon ring is invalid")
        (holes if ring.is_ccw else outers).append((polygon, points))
    if not outers:
        raise PetesLakeReferenceFitnessError("NWI Esri polygon has no clockwise outer ring")
    hole_assignments: list[list[list[list[float]]]] = [[] for _ in outers]
    for hole_polygon, hole_points in holes:
        containing = [
            (index, outer.area)
            for index, (outer, _points) in enumerate(outers)
            if outer.contains(hole_polygon.representative_point())
        ]
        if not containing:
            raise PetesLakeReferenceFitnessError("NWI polygon hole is unassigned")
        index = min(containing, key=lambda item: item[1])[0]
        hole_assignments[index].append(hole_points)
    polygons = [
        Polygon(points, holes=hole_assignments[index])
        for index, (_outer, points) in enumerate(outers)
    ]
    geometry = polygons[0] if len(polygons) == 1 else MultiPolygon(polygons)
    if geometry.is_empty or not geometry.is_valid:
        raise PetesLakeReferenceFitnessError("NWI polygon assembly is invalid")
    return geometry


def _load_nwi(
    root: Path,
) -> tuple[
    dict[str, Any],
    list[dict[str, Any]],
    list[dict[str, Any]],
    dict[str, Any],
]:
    contract = validate_finalized_contract(root)
    contract_path = root / NWI_CONTRACT_PATH
    asset_by_role = {
        item["extensions"]["logical_role"]: item for item in contract["assets"]
    }
    if len(asset_by_role) != len(contract["assets"]):
        raise PetesLakeReferenceFitnessError("NWI logical asset-role roster changed")
    payloads: dict[str, Any] = {}
    identities: dict[str, Any] = {}
    for logical_role, asset in asset_by_role.items():
        path = root / NWI_CUSTODY_ROOT / PurePosixPath(asset["destination_relative_path"])
        expected = asset["observed"]
        if (
            not path.is_file()
            or path.is_symlink()
            or path.stat().st_nlink != 1
            or path.stat().st_size != expected["promoted_size_bytes"]
            or _digest(path.read_bytes()) != expected["promoted_sha256"]
        ):
            raise PetesLakeReferenceFitnessError(
                f"NWI promoted identity changed: {logical_role}"
            )
        payloads[logical_role] = json.loads(path.read_bytes())
        identities[logical_role] = {
            "filename": path.name,
            "bytes": path.stat().st_size,
            "sha256": expected["promoted_sha256"],
        }
    source_metadata = _validate_layer_metadata(
        payloads["source-layer-metadata"], layer="source"
    )
    if set(source_metadata["source_type_renderer_values"]) != SOURCE_TYPE_RENDERER_VALUES:
        raise PetesLakeReferenceFitnessError("NWI source-type renderer contract changed")
    transformer = Transformer.from_crs(3857, 32610, always_xy=True)
    normalized: dict[str, list[dict[str, Any]]] = {"wetlands": [], "source": []}
    for layer in normalized:
        response = payloads[f"{layer}-features"]
        spatial = response.get("spatialReference", {})
        if not {spatial.get("wkid"), spatial.get("latestWkid")}.intersection({3857, 102100}):
            raise PetesLakeReferenceFitnessError("NWI feature CRS changed before local transform")
        for feature in response["features"]:
            if "curveRings" in feature.get("geometry", {}):
                raise PetesLakeReferenceFitnessError("NWI true curves cannot be silently densified")
            source_geometry = _esri_rings_geometry(feature["geometry"]["rings"])
            geometry = transform_geometry(transformer.transform, source_geometry)
            if geometry.is_empty or not geometry.is_valid:
                raise PetesLakeReferenceFitnessError("NWI local CRS transform produced invalid geometry")
            normalized[layer].append(
                {"attributes": _normalize_attributes(feature["attributes"]), "geometry": geometry}
            )
    contract_data = contract_path.read_bytes()
    custody = {
        "unit_id": NWI_CUSTODY_UNIT_ID,
        "run_id": NWI_RUN_ID,
        "branch": contract["extensions"]["branch"],
        "git_source_commit": contract["extensions"]["git_source_commit"],
        "completed_at_utc": contract["extensions"]["completed_at_utc"],
        "contract_path": NWI_CONTRACT_PATH.as_posix(),
        "contract_bytes": len(contract_data),
        "contract_sha256": _digest(contract_data),
        "asset_identities": identities,
        "bounded_transaction_consistency": contract["extensions"][
            "bounded_transaction_consistency"
        ],
        "tracked_source_gate": contract["extensions"]["tracked_source_gate"],
    }
    return custody, normalized["wetlands"], normalized["source"], source_metadata


def _registration_masks(report: dict[str, Any], boundary: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    passed = np.zeros(GRID_SHAPE, dtype=bool)
    nonpass = np.zeros(GRID_SHAPE, dtype=bool)
    for item in report["registration"]["windows"]:
        window = item["pixel_window"]
        rows = slice(window["row_offset"], window["row_offset"] + window["height"])
        columns = slice(window["column_offset"], window["column_offset"] + window["width"])
        target = passed if item["state"] == "pass" else nonpass
        target[rows, columns] = True
    strict = boundary & passed & ~nonpass
    return strict, boundary & nonpass, boundary & ~passed & ~nonpass


def _counts(values: np.ndarray, mask: np.ndarray) -> dict[str, int]:
    unique, counts = np.unique(values[mask], return_counts=True)
    return {str(int(value)): int(count) for value, count in zip(unique, counts, strict=True)}


def _continuous_by_class(values: np.ndarray, valid: np.ndarray, classes: np.ndarray) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for value in (1, 2, 3, 4, 6, UNCOVERED):
        mask = valid & (classes == value)
        selected = values[mask]
        result[str(value)] = {
            "valid_pixels": int(mask.sum()),
            "p10": round(float(np.percentile(selected, 10)), 6) if selected.size else None,
            "p50": round(float(np.percentile(selected, 50)), 6) if selected.size else None,
            "p90": round(float(np.percentile(selected, 90)), 6) if selected.size else None,
        }
    return result


def _parse_image_date(value: Any) -> date | None:
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    for pattern in ("%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%m-%d-%Y"):
        try:
            return datetime.strptime(text, pattern).date()
        except ValueError:
            continue
    return None


def _reported_scales(value: Any) -> set[int]:
    if not isinstance(value, str) or not value.strip():
        return set()
    matches = re.findall(r"1\s*:\s*([0-9][0-9,]*)", value)
    if not matches and re.fullmatch(r"[0-9][0-9,]*", value.strip()):
        matches = [value.strip()]
    return {int(item.replace(",", "")) for item in matches}


def _nonplaceholder_text(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    text = value.strip()
    if text.casefold() in {"", "unknown", "none", "null", "<null>", "n/a", "na"}:
        return ""
    return text


def _source_project_binding(attributes: dict[str, Any], geometry: Any) -> str:
    try:
        attribute_bytes = json.dumps(
            attributes,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    except (TypeError, ValueError) as error:
        raise PetesLakeReferenceFitnessError(
            "NWI source-project attributes are not deterministically serializable"
        ) from error
    return _digest(attribute_bytes + b"\0" + geometry.wkb)


def _full_pixel_source_coverage(geometries: Iterable[Any]) -> np.ndarray:
    items = list(geometries)
    if not items:
        return np.zeros(GRID_SHAPE, dtype=bool)
    merged = unary_union(items)
    if merged.is_empty or not merged.is_valid:
        raise PetesLakeReferenceFitnessError("NWI eligible source union is invalid")
    # A pixel center is accepted only when a circle containing its entire
    # 20 m square footprint remains inside eligible source coverage.  The
    # half-diagonal erosion is deliberately conservative at project edges.
    strict = merged.buffer(-PIXEL_HALF_DIAGONAL_METERS)
    if strict.is_empty:
        return np.zeros(GRID_SHAPE, dtype=bool)
    if not strict.is_valid:
        raise PetesLakeReferenceFitnessError("NWI strict source coverage is invalid")
    return _rasterize([strict])


def _validate_nwi_report_binding(
    custody: dict[str, Any], *, git_source_commit: str, generated_at_utc: str
) -> None:
    if custody.get("unit_id") != NWI_CUSTODY_UNIT_ID:
        raise PetesLakeReferenceFitnessError("NWI custody unit binding changed")
    if custody.get("branch") != BRANCH:
        raise PetesLakeReferenceFitnessError("NWI custody branch binding changed")
    if custody.get("git_source_commit") != git_source_commit:
        raise PetesLakeReferenceFitnessError(
            "NWI custody source commit does not equal the report source commit"
        )
    completed = _utc_z(custody.get("completed_at_utc"), "NWI custody completion")
    generated = _utc_z(generated_at_utc, "U05 report generation")
    if generated <= completed:
        raise PetesLakeReferenceFitnessError(
            "U05 report generation must follow NWI custody completion"
        )


def _source_project_summary(
    records: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[Any], list[Any]]:
    summaries: list[dict[str, Any]] = []
    fit: list[Any] = []
    unfit: list[Any] = []
    allowed_source_types = {"BW", "CIR", "TC"}
    if not allowed_source_types.issubset(SOURCE_TYPE_RENDERER_VALUES):
        raise PetesLakeReferenceFitnessError(
            "prospective NWI source-type allowlist is not provider-published"
        )
    ignition = date(2023, 8, 25)
    for record in records:
        attributes = record["attributes"]
        image_year = attributes.get("IMAGE_YR")
        raw_image_date = attributes.get("IMAGE_DATE")
        image_date_text = (
            raw_image_date.strip() if isinstance(raw_image_date, str) else ""
        )
        image_date = _parse_image_date(raw_image_date)
        status = str(attributes.get("STATUS") or "").strip()
        source_type = str(attributes.get("SOURCE_TYPE") or "").strip()
        project_name = _nonplaceholder_text(attributes.get("PROJECT_NAME"))
        data_source = _nonplaceholder_text(attributes.get("DATA_SOURCE"))
        emulsion = _nonplaceholder_text(attributes.get("EMULSION"))
        image_scale = attributes.get("IMAGE_SCALE")
        all_scales = _reported_scales(attributes.get("ALL_SCALES"))
        reasons: list[str] = []
        if not project_name:
            reasons.append("PROJECT_NAME_MISSING")
        if status != "Complete":
            reasons.append("STATUS_NOT_EXACT_COMPLETE")
        if source_type not in allowed_source_types:
            reasons.append("SOURCE_TYPE_NOT_EXPLICIT_NONSCALABLE_ALLOWLIST")
        if not data_source:
            reasons.append("DATA_SOURCE_MISSING_OR_UNKNOWN")
        if not emulsion:
            reasons.append("EMULSION_MISSING_OR_UNKNOWN")
        if not isinstance(image_year, int) or isinstance(image_year, bool) or image_year <= 0:
            reasons.append("IMAGE_YEAR_INVALID")
        elif image_year > ignition.year:
            reasons.append("IMAGE_YEAR_AFTER_IGNITION")
        elif image_year == ignition.year and (
            image_date is None or image_date >= ignition
        ):
            reasons.append("2023_IMAGE_DATE_NOT_EXACT_PREIGNITION")
        if image_date_text and image_date is None:
            reasons.append("IMAGE_DATE_PRESENT_BUT_INVALID")
        if image_date is not None and isinstance(image_year, int) and image_date.year != image_year:
            reasons.append("IMAGE_DATE_YEAR_DISAGREES_WITH_IMAGE_YEAR")
        if (
            not isinstance(image_scale, int)
            or isinstance(image_scale, bool)
            or not 0 < image_scale <= MAX_ACCEPTED_SOURCE_SCALE
        ):
            reasons.append("IMAGE_SCALE_MISSING_OR_ABOVE_1_TO_100000")
        elif image_scale not in all_scales:
            reasons.append("IMAGE_SCALE_NOT_BOUND_IN_ALL_SCALES")
        if not (
            _nonplaceholder_text(attributes.get("SUPPMAPINFO"))
            or _nonplaceholder_text(attributes.get("FGDC_METADATA"))
        ):
            reasons.append("PROJECT_METADATA_LOCATOR_MISSING")
        suitable = not reasons
        (fit if suitable else unfit).append(record["geometry"])
        binding = _source_project_binding(attributes, record["geometry"])
        summaries.append(
            {
                "project_id": f"nwi-source-project-{binding[:16]}",
                "project_binding_sha256": binding,
                "geometry_sha256": _digest(record["geometry"].wkb),
                "image_year": image_year,
                "parsed_image_date": image_date.isoformat() if image_date else None,
                "image_scale": image_scale,
                "pre_ignition_context_gate": "pass" if suitable else "fail",
                "gate_reasons": reasons,
            }
        )
    return summaries, fit, unfit


def _decision_outcome(
    machine_pass: bool, visual_review_decision: str
) -> tuple[str, str, str]:
    if not machine_pass:
        return (
            "remediate",
            "REMEDIATE_PETES_LAKE_REFERENCE_FITNESS_SOURCE_OR_SURVIVING_EVIDENCE_GATE",
            UNIT_ID,
        )
    if visual_review_decision == VISUAL_PENDING:
        return (
            "pending-render-review",
            "PENDING_ACTUAL_PETES_LAKE_REFERENCE_RENDER_REVIEW",
            UNIT_ID,
        )
    if visual_review_decision != VISUAL_PASS:
        return (
            "remediate",
            "REMEDIATE_PETES_LAKE_REFERENCE_FITNESS_RENDER_GATE",
            UNIT_ID,
        )
    return (
        "pass",
        "PASS_EXACT_PETES_LAKE_REFERENCE_FITNESS_WITH_MAPPED_WETLAND_EXCLUSIONS",
        "P2O4-T33-U06_AFFIRMATIVE_BACKGROUND_SOURCE_CONTRACT_AND_CUSTODY",
    )


def _validate_visual(decision: str, notes: str) -> None:
    if decision not in {VISUAL_PENDING, VISUAL_PASS, VISUAL_FAIL}:
        raise PetesLakeReferenceFitnessError("visual decision is invalid")
    expected_notes = {
        VISUAL_PENDING: "",
        VISUAL_PASS: VISUAL_PASS_NOTE,
        VISUAL_FAIL: VISUAL_FAIL_NOTE,
    }
    if notes != expected_notes[decision]:
        raise PetesLakeReferenceFitnessError(
            "visual review note must be the exact privacy-safe controlled value"
        )


def build_report(
    *,
    repository_root: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
    visual_review_decision: str,
    visual_review_notes: str,
) -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    root = repository_root.resolve()
    _validate_visual(visual_review_decision, visual_review_notes)
    if not re.fullmatch(r"[0-9a-f]{40}", git_source_commit):
        raise PetesLakeReferenceFitnessError("source commit must be an exact lowercase SHA-1")
    _utc_z(generated_at_utc, "U05 report generation")
    u03, optical, u03_replay = _replay_u03(root)
    u04, u04_replay = _replay_u04(root)
    boundary = optical["boundary_mask20"]
    if boundary.shape != GRID_SHAPE or int(boundary.sum()) != 34_103:
        raise PetesLakeReferenceFitnessError("frozen optical boundary grid changed")
    pair_state, _ = classify_pair_quality(optical["pre_scl20"], optical["post_scl20"])
    pair_counts = _counts(pair_state, boundary)
    if pair_counts != {"0": 33365, "1": 134, "2": 604}:
        raise PetesLakeReferenceFitnessError("U03 pair-quality reconstruction changed")
    registration_strict, registration_nonpass, registration_unobserved = _registration_masks(
        u03, boundary
    )

    archive_path = (
        root
        / CUSTODY_PATHS["raw_package"]
        / "petes-lake-mtbs-reference-delivery-001.zip"
    )
    native = inspect_native_archive(archive_path)
    if native != u04["native_contract"]:
        raise PetesLakeReferenceFitnessError("fresh U04 native archive inspection changed")
    with ZipFile(archive_path) as archive:
        raster_bytes = archive.read(EXPECTED_MEMBERS["dnbr6"])
    with MemoryFile(raster_bytes) as memory, memory.open() as dataset:
        if dataset.crs is None or dataset.crs.to_epsg() != 32610 or dataset.count != 1:
            raise PetesLakeReferenceFitnessError("MTBS dNBR6 grid changed")
        mtbs = _sample_nearest(dataset.read(1), dataset.transform, dataset.nodata)
    burn_geometries = _read_vector_geometries(archive_path, EXPECTED_MEMBERS["burn_area_shp"])
    mask_geometries = _read_vector_geometries(archive_path, EXPECTED_MEMBERS["mask_area_shp"])
    delivered_boundary = _rasterize(burn_geometries)
    delivered_mask_center = _rasterize(mask_geometries)
    delivered_mask_any_touch = _rasterize(mask_geometries, all_touched=True)
    nonprocessing = boundary & ((mtbs == 6) | delivered_mask_any_touch)

    nwi_custody, wetland_records, source_records, source_layer_metadata = _load_nwi(root)
    _validate_nwi_report_binding(
        nwi_custody,
        git_source_commit=git_source_commit,
        generated_at_utc=generated_at_utc,
    )
    wetland_center = _rasterize(
        [item["geometry"] for item in wetland_records], all_touched=False
    )
    wetland_any_touch = _rasterize(
        [item["geometry"] for item in wetland_records], all_touched=True
    )
    source_summaries, source_fit_geometries, source_unfit_geometries = _source_project_summary(
        source_records
    )
    source_fit_center = _rasterize(source_fit_geometries)
    source_fit_full_pixel = _full_pixel_source_coverage(source_fit_geometries)
    source_unfit_center = _rasterize(source_unfit_geometries)
    source_unfit_any_touch = _rasterize(source_unfit_geometries, all_touched=True)
    source_covered = source_fit_center | source_unfit_center
    source_fit = source_fit_full_pixel & ~source_unfit_any_touch
    source_gate = bool(
        wetland_records
        and source_records
        and np.all(source_fit[boundary])
    )
    eligible_scales = [
        item["image_scale"]
        for item in source_summaries
        if item["pre_ignition_context_gate"] == "pass"
    ]
    wetland_uncertainty_buffer_meters = max(
        20.0,
        max(eligible_scales, default=MAX_ACCEPTED_SOURCE_SCALE) / 1_000.0,
    )
    if wetland_uncertainty_buffer_meters > QUERY_CONTEXT_BUFFER_METERS:
        raise PetesLakeReferenceFitnessError(
            "NWI source-scale uncertainty buffer exceeds the acquired query halo"
        )
    wetland_buffered_geometries = [
        item["geometry"].buffer(wetland_uncertainty_buffer_meters)
        for item in wetland_records
    ]
    if any(item.is_empty or not item.is_valid for item in wetland_buffered_geometries):
        raise PetesLakeReferenceFitnessError(
            "NWI source-scale uncertainty buffering produced invalid geometry"
        )
    wetland_buffered_any_touch = _rasterize(
        wetland_buffered_geometries, all_touched=True
    )

    reference_affirmative = boundary & delivered_boundary & np.isin(mtbs, (2, 3, 4))
    sentinel_water = boundary & (
        (optical["pre_scl20"] == 6) | (optical["post_scl20"] == 6)
    )
    current = reference_affirmative.copy()
    disjoint: list[dict[str, Any]] = []
    ordered_exclusions = (
        ("NWI_SOURCE_METADATA_UNFIT_OR_UNCOVERED", ~source_fit),
        ("OPTICAL_PAIR_NOT_ELIGIBLE", pair_state != 0),
        ("REGISTRATION_NOT_STRICT_PASS", ~registration_strict),
        ("MTBS_NONPROCESSING_CLASS_OR_VECTOR", nonprocessing),
        (
            "MAPPED_NWI_WETLAND_OR_DEEPWATER_PLUS_SOURCE_SCALE_BUFFER",
            wetland_buffered_any_touch,
        ),
        ("SENTINEL_SCL_WATER", sentinel_water),
    )
    for code, exclusion in ordered_exclusions:
        removed = current & exclusion
        disjoint.append(
            {
                "reason": code,
                "removed_pixels": int(removed.sum()),
                "remaining_pixels": int((current & ~exclusion).sum()),
            }
        )
        current &= ~exclusion
    bounded = current
    class_counts = _counts(mtbs, bounded)
    machine_pass = source_gate and int(bounded.sum()) > 0
    visual_pass = visual_review_decision == VISUAL_PASS
    accepted = int(bounded.sum()) if machine_pass and visual_pass else 0
    disposition, code, next_dependency = _decision_outcome(
        machine_pass, visual_review_decision
    )

    ignition = date.fromisoformat("2023-08-25")
    sentinel_pre = date.fromisoformat("2023-07-21")
    sentinel_post = date.fromisoformat("2023-10-19")
    mtbs_pre = date.fromisoformat("2023-08-01")
    mtbs_post = date.fromisoformat("2024-08-11")
    evidence = {
        "frozen_optical_boundary_pixels": int(boundary.sum()),
        "delivered_mtbs_boundary_pixels": int(delivered_boundary.sum()),
        "boundary_intersection_pixels": int((boundary & delivered_boundary).sum()),
        "boundary_frozen_only_pixels": int((boundary & ~delivered_boundary).sum()),
        "boundary_delivered_only_pixels": int((delivered_boundary & ~boundary).sum()),
        "boundary_symmetric_difference_pixels": int(np.logical_xor(boundary, delivered_boundary).sum()),
        "mtbs_dnbr6_on_frozen_boundary": _counts(mtbs, boundary),
        "mtbs_reference_covered_pixels": int((boundary & (mtbs != UNCOVERED)).sum()),
        "mtbs_reference_uncovered_pixels": int((boundary & (mtbs == UNCOVERED)).sum()),
        "delivered_mask_vector_center_pixels": int(
            (boundary & delivered_mask_center).sum()
        ),
        "delivered_mask_vector_any_touch_pixels": int(
            (boundary & delivered_mask_any_touch).sum()
        ),
        "mtbs_class6_pixels": int((boundary & (mtbs == 6)).sum()),
        "nonprocessing_center_intersection_pixels": int(
            (boundary & delivered_mask_center & (mtbs == 6)).sum()
        ),
        "nonprocessing_any_touch_intersection_pixels": int(
            (boundary & delivered_mask_any_touch & (mtbs == 6)).sum()
        ),
        "nonprocessing_union_pixels": int(nonprocessing.sum()),
        "mask_vector_center_affirmative_pixels": int(
            (boundary & delivered_mask_center & np.isin(mtbs, (2, 3, 4))).sum()
        ),
        "mask_vector_any_touch_affirmative_pixels": int(
            (boundary & delivered_mask_any_touch & np.isin(mtbs, (2, 3, 4))).sum()
        ),
        "pair_quality_state_counts": pair_counts,
        "registration_strict_pass_pixels": int(registration_strict.sum()),
        "registration_nonpass_pixels": int(registration_nonpass.sum()),
        "registration_unobserved_pixels": int(registration_unobserved.sum()),
        "sentinel_scl_water_union_pixels": int(sentinel_water.sum()),
        "nwi_feature_count": len(wetland_records),
        "nwi_center_pixels": int((boundary & wetland_center).sum()),
        "nwi_any_touch_pixels": int((boundary & wetland_any_touch).sum()),
        "nwi_source_scale_uncertainty_buffer_meters": wetland_uncertainty_buffer_meters,
        "nwi_buffered_any_touch_pixels": int(
            (boundary & wetland_buffered_any_touch).sum()
        ),
        "nwi_affirmative_overlap_pixels": int((reference_affirmative & wetland_any_touch).sum()),
        "nwi_buffered_affirmative_overlap_pixels": int(
            (reference_affirmative & wetland_buffered_any_touch).sum()
        ),
        "nwi_nonprocessing_overlap_pixels": int((nonprocessing & wetland_any_touch).sum()),
        "source_project_feature_count": len(source_records),
        "source_metadata_covered_pixels": int((boundary & source_covered).sum()),
        "source_metadata_fit_center_pixels": int(
            (boundary & source_fit_center).sum()
        ),
        "source_metadata_full_pixel_fit_before_unfit_override_pixels": int(
            (boundary & source_fit_full_pixel).sum()
        ),
        "source_metadata_fit_pixels": int((boundary & source_fit).sum()),
        "source_project_unfit_center_pixels": int(
            (boundary & source_unfit_center).sum()
        ),
        "source_project_unfit_any_touch_pixels": int(
            (boundary & source_unfit_any_touch).sum()
        ),
        "source_project_context_full_eligible_coverage": source_gate,
        "source_layer_metadata_contract": source_layer_metadata,
        "raw_affirmative_with_delivered_boundary_pixels": int(reference_affirmative.sum()),
        "bounded_reference_pixels_by_mtbs_class": class_counts,
        "bounded_reference_pixels": int(bounded.sum()),
        "accepted_reference_pixels_after_render_gate": accepted,
        "accepted_background_pixels": 0,
        "disjoint_affirmative_exclusion_accounting": disjoint,
        "optical_dnbr_context_by_mtbs_class": _continuous_by_class(
            optical["dnbr"], optical["dnbr_valid"], mtbs
        ),
    }
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
        "event": {
            "event_id": "OR4396912190120230825",
            "event_name": "PETES LAKE",
            "event_group_id": "event-petes-lake-2023",
            "geography_group_id": "geo-mtbs-or4396912190120230825",
            "map_id": 10031414,
        },
        "trace": {
            "upstream_optical_run_id": u03["run_id"],
            "upstream_optical_report_bytes": U03_JSON_BYTES,
            "upstream_optical_report_sha256": U03_JSON_SHA256,
            "upstream_reference_run_id": u04["run_id"],
            "upstream_reference_report_bytes": U04_JSON_BYTES,
            "upstream_reference_report_sha256": U04_JSON_SHA256,
            "nwi_custody_run_id": NWI_RUN_ID,
            "nwi_contract_bytes": nwi_custody["contract_bytes"],
            "nwi_contract_sha256": nwi_custody["contract_sha256"],
            "aoi_version": "multi-event-native-grids-v0.3.0",
            "target_version": "target-burn-scar-v0.2.0",
            "label_schema_version": "burn-scar-five-state-schema-v0.1.0",
            "prior_label_set_version": "owner-approved-prototype-region-labels-v0.3.0",
            "petes_lake_label_set_version": None,
            "dataset_version": None,
            "split_version": None,
            "baseline_version": None,
            "model_version": None,
        },
        "upstream_reproduction": {"u03": u03_replay, "u04": u04_replay},
        "custody": {
            "mtbs_archive_bytes": ARCHIVE_BYTES,
            "mtbs_archive_sha256": ARCHIVE_SHA256,
            "nwi": nwi_custody,
        },
        "comparison_grid": {
            "crs": GRID_CRS,
            "width": GRID_SHAPE[1],
            "height": GRID_SHAPE[0],
            "transform": list(GRID_TRANSFORM)[:6],
            "categorical_sampling": "nearest neighbor from native 30 m MTBS to verified 20 m optical pixel centers; no resolution gain claimed",
            "nwi_geometry": "exact provider EPSG:3857 rings transformed locally to EPSG:32610 with the locked geospatial environment; mapped polygons plus a disclosed 1 mm-at-source-scale BurnLens policy buffer are exclusion context only",
            "nwi_source_coverage": "eligible source-project geometries are unioned and eroded by one optical-pixel half-diagonal before center sampling; any-touch unfit source geometry wins",
        },
        "temporal_relationship": {
            "ignition_date": ignition.isoformat(),
            "sentinel_pre": sentinel_pre.isoformat(),
            "sentinel_pre_days_from_ignition": (sentinel_pre - ignition).days,
            "sentinel_post": sentinel_post.isoformat(),
            "sentinel_post_days_from_ignition": (sentinel_post - ignition).days,
            "mtbs_pre": mtbs_pre.isoformat(),
            "mtbs_pre_days_from_ignition": (mtbs_pre - ignition).days,
            "mtbs_post": mtbs_post.isoformat(),
            "mtbs_post_days_from_ignition": (mtbs_post - ignition).days,
            "mtbs_post_days_after_sentinel_post": (mtbs_post - sentinel_post).days,
            "interpretation": "MTBS agreement is bounded corroboration, not co-temporal validation; BurnLens does not recompute or relabel MTBS classes.",
        },
        "source_projects": source_summaries,
        "source_terms_and_roles": {
            "mtbs": "Analyst-interpreted, revisable thematic severity evidence. Classes 2-4 may support bounded burned candidates; class 0 is outside/nodata, class 1 is ambiguous, and class 6 plus the delivered mask are excluded.",
            "nwi": "USFWS reconnaissance-level biological wetlands/deepwater mapping used only for conservative mapped-feature exclusion and uncertainty context. Absence never proves dry land or background.",
            "nwi_catalog_release": NWI_CATALOG_RELEASE,
            "nwi_catalog_doi": NWI_CATALOG_DOI,
            "nwi_catalog_identity_binding": next(
                item
                for item in nwi_custody["tracked_source_gate"]
                if item["record_id"] == "SOURCE-2026-032"
            ),
            "nwi_terms_record_binding": next(
                item
                for item in nwi_custody["tracked_source_gate"]
                if item["record_id"] == "TERMS-2026-028"
            ),
            "nwi_service_reference": WEB_SERVICE_REFERENCE,
            "nwi_terms_reference": NWI_TERMS_REFERENCE,
            "nwi_limitations_reference": LIMITATIONS_REFERENCE,
            "nwi_user_caution_reference": USER_CAUTION_REFERENCE,
            "raw_nwi_redistribution": "blocked pending stronger dataset-specific redistribution terms; exact payload remains ignored",
            "attribution": "Monitoring Trends in Burn Severity Project (U.S. Geological Survey and USDA Forest Service); U.S. Fish and Wildlife Service National Wetlands Inventory; Contains modified Copernicus Sentinel data 2023, accessed through CDSE.",
        },
        "source_precedence": [
            "Official emergency, evacuation, incident, and public-safety information governs.",
            "Exact delivered Sentinel pixels and SCL/CLD/SNW govern optical observability.",
            "The exact delivered MTBS bundle governs its mapped identity and class semantics.",
            "NWI constrains mapped wetland/deepwater applicability but cannot establish burn severity or background truth.",
            "BurnLens-derived comparisons are lower-precedence experimental evidence; later owner yes cannot override a non-owner exclusion.",
        ],
        "evidence": evidence,
        "wetland_limitation": {
            "mtbs_warning": "Fire severity could be misrepresented in wetland areas.",
            "status": "RETAINED_MAPPED_NWI_WETLAND_AND_DEEPWATER_CELLS_EXCLUDED_EXHAUSTIVE_WETLAND_ABSENCE_NOT_PROVEN",
            "nonprocessing_is_not_wetland_inventory": True,
            "nwi_absence_is_not_wetland_absence": True,
            "residual_unmapped_wetland_uncertainty_applies_to_all_surviving_pixels": True,
            "source_scale_buffer_policy": {
                "rule": "maximum eligible IMAGE_SCALE divided by 1000, with a 20 m minimum and 100 m hard maximum",
                "interpretation": "BurnLens conservative context policy; not an official positional-accuracy claim or proof against omitted wetlands",
                "applied_meters": wetland_uncertainty_buffer_meters,
            },
            "regulatory_or_legal_wetland_delineation": False,
            "field_validation": False,
        },
        "visual_review": {
            "decision": visual_review_decision,
            "notes": visual_review_notes,
            "reviewer_role": "AI-assisted author self-audit; not independent review",
        },
        "fitness_decision": {
            "code": code,
            "disposition": disposition,
            "machine_source_gate": "pass" if machine_pass else "fail",
            "reference_role": "bounded_analyst_interpreted_revisable_candidate_evidence",
            "accepted_reference_pixels": accepted,
            "accepted_background_pixels": 0,
            "candidate_or_label_created": False,
            "next_dependency": next_dependency,
        },
        "claim_boundaries": {
            "independent_ground_truth": False,
            "wetland_absence_proven": False,
            "official_or_operational_status": False,
            "field_validation_or_endorsement": False,
            "candidate_owner_response_or_label_created": False,
            "dataset_split_baseline_model_created": False,
        },
        "warning": WARNING,
    }
    exclusion_overlay = np.zeros(GRID_SHAPE, dtype=np.uint8)
    exclusion_overlay[boundary] = 1
    exclusion_overlay[boundary & ~delivered_boundary] = 2
    exclusion_overlay[nonprocessing] = 3
    exclusion_overlay[boundary & wetland_buffered_any_touch] = 4
    exclusion_overlay[bounded] = 5
    optical.update(
        {
            "mtbs_dnbr6": mtbs,
            "delivered_boundary": delivered_boundary,
            "delivered_mask_center": delivered_mask_center,
            "delivered_mask_any_touch": delivered_mask_any_touch,
            "nwi_wetland_any_touch": wetland_any_touch,
            "nwi_wetland_buffered_any_touch": wetland_buffered_any_touch,
            "bounded_reference": bounded,
            "exclusion_overlay": exclusion_overlay,
        }
    )
    return report, optical


def _class_image(values: np.ndarray, boundary: np.ndarray, size: tuple[int, int]) -> Image.Image:
    palette = {
        1: (150, 158, 140),
        2: (242, 211, 110),
        3: (233, 142, 68),
        4: (188, 62, 44),
        6: (92, 103, 117),
        UNCOVERED: (20, 30, 28),
    }
    rgb = np.full((*values.shape, 3), (12, 25, 22), dtype=np.uint8)
    for value, color in palette.items():
        rgb[(values == value) & boundary] = color
    image = Image.fromarray(rgb, mode="RGB")
    image.thumbnail(size, Image.Resampling.NEAREST)
    canvas = Image.new("RGB", size, "#0c1916")
    canvas.paste(image, ((size[0] - image.width) // 2, (size[1] - image.height) // 2))
    return canvas


def _overlay_image(values: np.ndarray, size: tuple[int, int]) -> Image.Image:
    palette = {
        0: (12, 25, 22),
        1: (80, 88, 84),
        2: (198, 90, 113),
        3: (236, 179, 80),
        4: (61, 137, 186),
        5: (56, 186, 137),
    }
    rgb = np.zeros((*values.shape, 3), dtype=np.uint8)
    for value, color in palette.items():
        rgb[values == value] = color
    image = Image.fromarray(rgb, mode="RGB")
    image.thumbnail(size, Image.Resampling.NEAREST)
    canvas = Image.new("RGB", size, "#0c1916")
    canvas.paste(image, ((size[0] - image.width) // 2, (size[1] - image.height) // 2))
    return canvas


def _render_headline(report: dict[str, Any]) -> str:
    decision = report["fitness_decision"]
    if decision["disposition"] == "pass":
        return "Bounded reference evidence passes; candidates and labels do not."
    if (
        decision["disposition"] == "pending-render-review"
        and decision["machine_source_gate"] == "pass"
    ):
        return "Machine evidence is bounded; rendered-evidence review is pending."
    return "Reference evidence needs remediation; downstream work stays closed."


def _render_png_bytes(report: dict[str, Any], previews: dict[str, np.ndarray]) -> bytes:
    canvas = Image.new("RGB", (1800, 1320), "#07110f")
    draw = ImageDraw.Draw(canvas)
    draw.text((60, 36), "BURNLENS  /  PETES LAKE U05 REFERENCE FITNESS", fill="#b9d8cf", font=_font(21))
    headline = _render_headline(report)
    draw.text((60, 74), headline, fill="#eef7f3", font=_font(30))
    draw.text((60, 119), "NWI is mapped exclusion context only; absence never proves dry land.", fill="#ffca73", font=_font(18))
    boundary = previews["boundary_mask20"]
    panels = (
        ("PRE SENTINEL 2023-07-21", _preview_tci(previews["pre_tci"], previews["pre_mask"], (520, 315))),
        ("POST SENTINEL 2023-10-19", _preview_tci(previews["post_tci"], previews["post_mask"], (520, 315))),
        ("CONTINUOUS OPTICAL dNBR", _preview_dnbr(previews["dnbr"], previews["dnbr_valid"], (520, 315))),
        ("SAMPLED MTBS dNBR6", _class_image(previews["mtbs_dnbr6"], boundary, (520, 315))),
        ("EXCLUSIONS / BOUNDARY / NWI", _overlay_image(previews["exclusion_overlay"], (520, 315))),
        ("BOUNDED REFERENCE PIXELS", _overlay_image(np.where(previews["bounded_reference"], 5, np.where(boundary, 1, 0)).astype(np.uint8), (520, 315))),
    )
    for index, (label, image) in enumerate(panels):
        column, row = index % 3, index // 3
        x, y = 60 + column * 575, 160 + row * 402
        draw.rounded_rectangle((x, y, x + 535, y + 372), radius=16, fill="#0e1d1a", outline="#315b50", width=2)
        draw.text((x + 18, y + 13), label, fill="#eef7f3", font=_font(17))
        canvas.paste(image, (x + 8, y + 46))
    draw.text(
        (60, 948),
        "MTBS legend: 1 gray ambiguous · 2 yellow low · 3 orange moderate · 4 red high · 6 slate non-processing · dark uncovered",
        fill="#b9d8cf",
        font=_font(12),
    )
    draw.text(
        (60, 970),
        "Overlay: gray boundary · rose boundary difference · amber non-processing · blue NWI+buffer exclusion · green bounded evidence",
        fill="#b9d8cf",
        font=_font(12),
    )
    evidence = report["evidence"]
    metrics = (
        (f"{evidence['bounded_reference_pixels']:,}", "bounded classes 2-4"),
        (f"{evidence['nwi_buffered_any_touch_pixels']:,}", "NWI + scale-buffer pixels"),
        (f"{evidence['nonprocessing_union_pixels']:,}", "MTBS non-processing union"),
        ("297 days", "MTBS post after Sentinel post"),
    )
    for index, (value, label) in enumerate(metrics):
        x = 60 + index * 430
        draw.rounded_rectangle((x, 994, x + 395, 1108), radius=14, fill="#0e1d1a", outline="#315b50", width=2)
        draw.text((x + 20, 1013), value, fill="#78e0bd", font=_font(25))
        draw.text((x + 20, 1060), label, fill="#b9d8cf", font=_font(14))
    draw.rounded_rectangle((60, 1132, 1740, 1238), radius=14, fill="#261f12", outline="#be8a36", width=2)
    draw.text((82, 1148), report["wetland_limitation"]["mtbs_warning"], fill="#ffd997", font=_font(16))
    draw.text((82, 1182), "Nearest-neighbor MTBS comparison; no resolution gain. NWI is non-regulatory reconnaissance context.", fill="#ffd997", font=_font(14))
    draw.text((82, 1210), "0 background truth / 0 candidates / 0 labels / dataset-split-baseline-model none", fill="#ffd997", font=_font(14))
    draw.text(
        (60, 1250),
        f"STATUS {report['fitness_decision']['disposition']} / visual {report['visual_review']['decision']}",
        fill="#ffca73",
        font=_font(12),
    )
    draw.text((60, 1277), f"TRACE commit {report['git_source_commit'][:12]} / run {report['run_id']} / BurnLens {SOFTWARE_VERSION}", fill="#b9d8cf", font=_font(13))
    buffer = BytesIO()
    canvas.save(buffer, format="PNG", optimize=False)
    return buffer.getvalue()


def _render_html(report: dict[str, Any], png_name: str) -> bytes:
    evidence = report["evidence"]
    headline = _render_headline(report)
    project_rows = "".join(
        "<tr>"
        f"<td><code>{escape(str(item['project_id']))}</code></td>"
        f"<td>{escape(str(item['image_year']))}</td>"
        f"<td>{escape(str(item['parsed_image_date']))}</td>"
        f"<td>{escape(str(item['image_scale']))}</td>"
        f"<td>{escape(item['pre_ignition_context_gate'])}</td>"
        f"<td>{escape(', '.join(item['gate_reasons']) or 'none')}</td>"
        "</tr>"
        for item in report["source_projects"]
    )
    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Petes Lake U05 reference fitness</title><style>
body{{margin:0;background:#07110f;color:#eef7f3;font:16px/1.55 system-ui,sans-serif}}main{{max-width:1200px;margin:auto;padding:32px}}h1{{font-size:clamp(2rem,5vw,4rem);line-height:1.02}}.card{{background:#0e1d1a;border:1px solid #315b50;border-radius:16px;padding:20px;margin:18px 0;overflow-wrap:anywhere}}.warn{{background:#261f12;border-color:#be8a36;color:#ffd997}}img{{width:100%;height:auto;border-radius:16px}}table{{width:100%;border-collapse:collapse}}th,td{{text-align:left;padding:10px;border-bottom:1px solid #315b50;vertical-align:top}}code{{overflow-wrap:anywhere}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:14px}}.metric strong{{display:block;font-size:2rem;color:#78e0bd}}
</style></head><body><main><p>BURNLENS / PHASE TWO / ISSUE #521 / U05</p><h1>{escape(headline)}</h1><div class="card warn">{escape(report['warning'])}</div><img src="{escape(png_name)}" width="1800" height="1320" alt="Actual Petes Lake pre and post Sentinel imagery, continuous dNBR, sampled MTBS classes, mapped NWI and non-processing exclusions, and bounded reference evidence"><div class="grid"><div class="card metric"><strong>{evidence['bounded_reference_pixels']:,}</strong>bounded MTBS class 2-4 pixels</div><div class="card metric"><strong>{evidence['nwi_buffered_any_touch_pixels']:,}</strong>NWI plus source-scale-buffer pixels excluded</div><div class="card metric"><strong>{evidence['nonprocessing_union_pixels']:,}</strong>MTBS non-processing union</div><div class="card metric"><strong>0</strong>background truth or labels</div></div><h2>Why the two boundaries stay separate</h2><div class="card"><p>The frozen optical boundary has {evidence['frozen_optical_boundary_pixels']:,} pixel centers; the delivered MTBS boundary has {evidence['delivered_mtbs_boundary_pixels']:,}. Their symmetric difference is {evidence['boundary_symmetric_difference_pixels']:,} pixels. BurnLens does not silently replace either geometry.</p><p>MTBS categorical values are sampled nearest-neighbor from native 30 m to the verified 20 m optical grid. No resolution gain is claimed.</p><p>MTBS legend: class 1 ambiguous; classes 2, 3, and 4 are bounded low, moderate, and high severity evidence; class 6 and the delivered mask are non-processing exclusions; uncovered pixels remain excluded.</p></div><h2>Wetland and source limitations</h2><div class="card warn"><p><strong>{escape(report['wetland_limitation']['mtbs_warning'])}</strong></p><p>NWI is reconnaissance-level biological mapping used only to conservatively exclude mapped wetland and deepwater cells plus a {evidence['nwi_source_scale_uncertainty_buffer_meters']:g} m BurnLens policy buffer. NWI absence does not prove wetland absence, dry land, or background. Residual unmapped-wetland uncertainty applies to every surviving pixel. NWI is not a regulatory or legal delineation, field validation, or current ground truth.</p><p>The MTBS class-6 raster and delivered mask polygon are non-processing evidence, not a complete wetland inventory.</p><p>Source-project coverage is accepted only where an eligible project union covers the full 20 m optical pixel under a conservative half-diagonal erosion; any-touch unfit source geometry wins.</p></div><h2>NWI source projects</h2><div class="card"><table><thead><tr><th>Neutral project ID</th><th>Image year</th><th>Image date</th><th>Scale</th><th>Gate</th><th>Reasons</th></tr></thead><tbody>{project_rows}</tbody></table><p>Only neutral project bindings, derived gates, and necessary normalized numeric/date facts are published. Provider project names, source descriptors, comments, locators, and exact raw feature payloads remain private ignored custody.</p><p>Catalog release {NWI_CATALOG_RELEASE}; DOI <code>{NWI_CATALOG_DOI}</code>, bound by tracked <code>SOURCE-2026-032</code>. Raw NWI payload republication remains blocked pending stronger dataset-specific redistribution terms.</p></div><h2>Temporal relationship</h2><div class="card"><p>Sentinel: 35 days before ignition and 55 days after. MTBS extended assessment: 24 days before and 352 days after. The MTBS post is 297 days later than the Sentinel post, so agreement is bounded corroboration rather than co-temporal validation.</p></div><h2>Gate result</h2><div class="card"><p><strong>{escape(report['fitness_decision']['code'])}</strong></p><p>Disposition <strong>{escape(report['fitness_decision']['disposition'])}</strong>; visual review <strong>{escape(report['visual_review']['decision'])}</strong>.</p><p>{evidence['accepted_reference_pixels_after_render_gate']:,} reference pixels are accepted only as bounded evidence for a separate deterministic candidate proposal. Owner review, label and all dataset/model gates remain closed.</p></div><div class="card warn"><p>{escape(report['source_terms_and_roles']['attribution'])}</p><p>No independent ground truth, affirmative background truth, candidate, owner decision, label, dataset, split, baseline, model, metric, field validation, official status, endorsement, operational readiness, or emergency-ready claim exists.</p></div><p>Trace: commit <code>{escape(report['git_source_commit'])}</code> · BurnLens <code>{SOFTWARE_VERSION}</code> · run <code>{escape(report['run_id'])}</code> · NWI custody <code>{NWI_RUN_ID}</code> at commit <code>{escape(report['custody']['nwi']['git_source_commit'])}</code> · dataset/model none.</p></main></body></html>"""
    return html.encode("utf-8")


def _write_no_overwrite(path: Path, data: bytes) -> os.stat_result:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() or path.is_symlink():
        raise PetesLakeReferenceFitnessError(f"output exists; no overwrite: {path.name}")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0)
    try:
        descriptor = os.open(path, flags, 0o600)
    except FileExistsError:
        raise PetesLakeReferenceFitnessError(f"output exists; no overwrite: {path.name}") from None
    opened = os.fstat(descriptor)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        observed = path.lstat()
        if (
            not stat.S_ISREG(observed.st_mode)
            or path.is_symlink()
            or observed.st_nlink != 1
            or not os.path.samestat(opened, observed)
            or path.read_bytes() != data
        ):
            raise PetesLakeReferenceFitnessError("output exact readback failed")
        return observed
    except Exception:
        try:
            if os.path.samestat(opened, path.lstat()):
                path.unlink()
        except OSError:
            pass
        raise


def write_outputs(
    report: dict[str, Any], previews: dict[str, np.ndarray], directory: Path
) -> dict[str, dict[str, Any]]:
    paths = {
        "json": directory / f"{REPORT_ID}.json",
        "png": directory / f"{REPORT_ID}.png",
        "html": directory / f"{REPORT_ID}.html",
    }
    payloads = {
        "json": _canonical_report_bytes(report),
        "png": _render_png_bytes(report, previews),
        "html": _render_html(report, paths["png"].name),
    }
    if any(path.exists() or path.is_symlink() for path in paths.values()):
        raise PetesLakeReferenceFitnessError("U05 output roster already exists")
    owned: dict[str, os.stat_result] = {}
    try:
        for name in ("json", "png", "html"):
            owned[name] = _write_no_overwrite(paths[name], payloads[name])
    except Exception as error:
        rollback_failed: list[str] = []
        # Delete only a file whose exact inode identity was returned by this
        # invocation. Matching bytes alone never establish ownership because a
        # peer may create the same path after the empty-roster preflight.
        for name in reversed(("json", "png", "html")):
            created_path = paths[name]
            try:
                if not created_path.exists() and not created_path.is_symlink():
                    continue
                observed = created_path.lstat()
                identity = owned.get(name)
                if (
                    identity is None
                    or not stat.S_ISREG(observed.st_mode)
                    or created_path.is_symlink()
                    or observed.st_nlink != 1
                    or not os.path.samestat(identity, observed)
                    or created_path.read_bytes() != payloads[name]
                ):
                    rollback_failed.append(name)
                    continue
                created_path.unlink()
            except OSError:
                rollback_failed.append(name)
        if rollback_failed:
            raise PetesLakeReferenceFitnessError(
                "U05 output transaction failed and exact rollback was unsafe: "
                + ",".join(sorted(rollback_failed))
            ) from error
        raise PetesLakeReferenceFitnessError(
            "U05 output transaction failed; invocation-created outputs were rolled back"
        ) from error
    return {
        name: {"path": path.as_posix(), "bytes": len(payloads[name]), "sha256": _digest(payloads[name])}
        for name, path in paths.items()
    }
