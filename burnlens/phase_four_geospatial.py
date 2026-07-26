"""Create deterministic geospatial products from the accepted U02 analysis."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import io
import json
import math
import os
from pathlib import Path
import re
import sqlite3
import struct
import subprocess
from typing import Any, Iterable
import warnings

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import rasterio
from rasterio.features import shapes
from rasterio.io import MemoryFile
from rasterio.transform import Affine

from burnlens.phase_four_contract import load_contract


GEOSPATIAL_VERSION = "burnlens-phase-four-geospatial-v0.1.0"
SOFTWARE_VERSION = "0.53.0"
RUN_ROOT = Path("runs/phase-four")
U02_RECORD_PATH = Path(
    "records/phase-four/analyses/PHASE-FOUR-ANALYSIS-RECORD-2026-001.json"
)
U02_RECORD_SHA256 = (
    "0b242293b63b502ea66cf35393a50eb7c81bcbea22550c677c074023f0bea94c"
)
RUN_ID_PATTERN = re.compile(
    r"^BL-[0-9]{4}-[0-9]{2}-[0-9]{2}-p4o1-t01-u03-geospatial-r[0-9]{3}$"
)
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")
FLOAT_NODATA = -9999.0
BYTE_NODATA = 255
GPKG_LAYER = "rbr_accepted"


class PhaseFourGeospatialError(RuntimeError):
    """An analytical binding or geospatial product gate failed."""


@dataclass(frozen=True)
class VectorFeature:
    """One deterministic accepted-RBR polygon component."""

    fid: int
    candidate_id: str
    component_id: str
    pixel_count: int
    area_m2: float
    geometry: Any


@dataclass(frozen=True)
class GeospatialBuild:
    """Deterministic bytes for one U03 geospatial attempt."""

    manifest: dict[str, Any]
    outputs: dict[str, bytes]


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(8 * 1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(
        "utf-8"
    )


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PhaseFourGeospatialError(f"invalid JSON: {path}") from exc
    if not isinstance(value, dict):
        raise PhaseFourGeospatialError(f"JSON object required: {path}")
    return value


def _receipt(path: str, payload: bytes) -> dict[str, Any]:
    return {
        "path": path,
        "bytes": len(payload),
        "sha256": sha256(payload).hexdigest(),
    }


def _npy(path: Path, *, shape: tuple[int, ...], dtype: np.dtype[Any]) -> np.ndarray:
    if not path.is_file():
        raise PhaseFourGeospatialError(f"U02 array absent: {path}")
    value = np.load(path, allow_pickle=False)
    if not isinstance(value, np.ndarray):
        raise PhaseFourGeospatialError(f"U02 array invalid: {path}")
    if value.shape != shape or value.dtype != dtype:
        raise PhaseFourGeospatialError(f"U02 array schema drift: {path}")
    return value


def _verify_u02_run(root: Path) -> tuple[dict[str, Any], Path]:
    record_path = root / U02_RECORD_PATH
    if not record_path.is_file():
        raise PhaseFourGeospatialError("U02 analysis record is absent")
    observed_record_hash = _sha256_file(record_path)
    if observed_record_hash != U02_RECORD_SHA256:
        raise PhaseFourGeospatialError(
            f"U02 analysis record hash drift: {observed_record_hash}"
        )
    record = _read_json(record_path)
    inventory = record.get("ignored_run_inventory", {})
    run = root / inventory.get("path", "")
    if not run.is_dir() or run.is_symlink():
        raise PhaseFourGeospatialError("exact U02 run is absent")
    rows: list[str] = []
    files = sorted(
        (path for path in run.rglob("*") if path.is_file()),
        key=lambda path: path.relative_to(run).as_posix().casefold(),
    )
    expected_files = inventory.get("files", [])
    if len(files) != inventory.get("file_count") or len(files) != len(
        expected_files
    ):
        raise PhaseFourGeospatialError("U02 run file-count drift")
    for path, expected in zip(files, expected_files, strict=True):
        relative = path.relative_to(run).as_posix()
        digest = _sha256_file(path)
        if (
            relative != expected.get("path")
            or path.stat().st_size != expected.get("bytes")
            or digest != expected.get("sha256")
        ):
            raise PhaseFourGeospatialError(f"U02 run file drift: {relative}")
        rows.append(f"{relative}\t{path.stat().st_size}\t{digest}\n")
    serialized = "".join(rows).encode("utf-8")
    if (
        sum(path.stat().st_size for path in files) != inventory.get("bytes")
        or len(serialized) != inventory.get("inventory_bytes")
        or sha256(serialized).hexdigest() != inventory.get("inventory_sha256")
    ):
        raise PhaseFourGeospatialError("U02 run inventory drift")
    manifest = _read_json(run / "ANALYSIS-MANIFEST.json")
    if manifest.get("state") != "accepted-baseline":
        raise PhaseFourGeospatialError("U02 run is not accepted-baseline")
    if (
        manifest.get("methods", {})
        .get("rejected_diagnostic", {})
        .get("accepted")
        is not False
    ):
        raise PhaseFourGeospatialError("U02 rejected-model boundary drift")
    return record, run


def _geotiff_bytes(
    array: np.ndarray,
    *,
    crs: str,
    transform: list[float],
    nodata: float | int,
    role: str,
    run_id: str,
) -> bytes:
    if array.shape != (64, 64) or array.dtype not in (
        np.dtype("float32"),
        np.dtype("uint8"),
    ):
        raise PhaseFourGeospatialError("GeoTIFF array schema drift")
    profile = {
        "driver": "GTiff",
        "width": 64,
        "height": 64,
        "count": 1,
        "dtype": array.dtype.name,
        "crs": crs,
        "transform": Affine(*transform),
        "nodata": nodata,
        "compress": "DEFLATE",
        "zlevel": 9,
        "predictor": 2,
        "tiled": True,
        "blockxsize": 64,
        "blockysize": 64,
        "interleave": "band",
    }
    with MemoryFile() as memory:
        with memory.open(**profile) as dataset:
            dataset.write(array, 1)
            dataset.update_tags(
                AREA_OR_POINT="Area",
                ANALYTICAL_STATUS=(
                    "accepted-baseline"
                    if role.startswith("rbr") or role == "exclusion"
                    else "rejected-model-diagnostic"
                ),
                BURNLENS_ROLE=role,
                RUN_ID=run_id,
                SOURCE_PRECEDENCE="Official sources govern",
            )
        payload = memory.read()
    with MemoryFile(payload) as memory:
        with memory.open() as dataset:
            with warnings.catch_warnings():
                warnings.filterwarnings(
                    "ignore",
                    message=r"Setting the shape on a NumPy array has been deprecated.*",
                    category=DeprecationWarning,
                )
                observed = dataset.read(1).copy()
            if (
                dataset.count != 1
                or dataset.width != 64
                or dataset.height != 64
                or dataset.crs.to_string() != crs
                or tuple(dataset.transform)[:6] != tuple(transform)
                or dataset.nodata != nodata
                or dataset.dtypes[0] != array.dtype.name
                or observed.dtype != array.dtype
                or observed.tobytes(order="C") != array.tobytes(order="C")
            ):
                raise PhaseFourGeospatialError(
                    f"GeoTIFF readback failed: {role}"
                )
    return payload


def _polygon_features(
    patch_arrays: dict[str, dict[str, np.ndarray]],
    contract: dict[str, Any],
) -> list[VectorFeature]:
    try:
        from shapely.geometry import MultiPolygon, Polygon, shape
        from shapely.validation import make_valid
    except ImportError as exc:
        raise PhaseFourGeospatialError(
            "U03 requires the locked geo-research profile with Shapely"
        ) from exc

    by_candidate = {
        item["candidate_id"]: item for item in contract["integration_roster"]
    }
    pending: list[tuple[str, Any]] = []
    for candidate_id in sorted(patch_arrays):
        binary = patch_arrays[candidate_id]["rbr-binary"]
        valid = patch_arrays[candidate_id]["exclusion"] == 0
        transform = Affine(*by_candidate[candidate_id]["transform"])
        for mapping, value in shapes(
            binary,
            mask=valid & (binary == 1),
            transform=transform,
            connectivity=4,
        ):
            if int(value) != 1:
                continue
            geometry = make_valid(shape(mapping))
            polygons: list[Any] = []
            if isinstance(geometry, Polygon):
                polygons = [geometry]
            elif isinstance(geometry, MultiPolygon):
                polygons = list(geometry.geoms)
            elif geometry.geom_type == "GeometryCollection":
                polygons = [
                    part
                    for part in geometry.geoms
                    if isinstance(part, Polygon) and not part.is_empty
                ]
            if not polygons:
                raise PhaseFourGeospatialError(
                    f"polygonization produced no polygon: {candidate_id}"
                )
            normalized = MultiPolygon(polygons)
            if normalized.is_empty or not normalized.is_valid:
                raise PhaseFourGeospatialError(
                    f"invalid polygon geometry: {candidate_id}"
                )
            pending.append((candidate_id, normalized))
    pending.sort(
        key=lambda item: (
            item[0],
            tuple(float(value) for value in item[1].bounds),
            item[1].wkb_hex,
        )
    )
    features: list[VectorFeature] = []
    counters: dict[str, int] = {}
    for fid, (candidate_id, geometry) in enumerate(pending, start=1):
        counters[candidate_id] = counters.get(candidate_id, 0) + 1
        pixel_count = int(round(float(geometry.area) / 400.0))
        if pixel_count <= 0 or not math.isclose(
            float(geometry.area),
            pixel_count * 400.0,
            rel_tol=0.0,
            abs_tol=1e-6,
        ):
            raise PhaseFourGeospatialError(
                f"polygon area is not a 20 m pixel multiple: {candidate_id}"
            )
        features.append(
            VectorFeature(
                fid=fid,
                candidate_id=candidate_id,
                component_id=f"{candidate_id}-RBR-{counters[candidate_id]:03d}",
                pixel_count=pixel_count,
                area_m2=float(geometry.area),
                geometry=geometry,
            )
        )
    if not features:
        raise PhaseFourGeospatialError("accepted RBR polygon roster is empty")
    return features


def _gpkg_geometry_blob(geometry: Any, srs_id: int) -> bytes:
    try:
        from shapely import to_wkb
    except ImportError as exc:
        raise PhaseFourGeospatialError(
            "U03 requires the locked geo-research profile with Shapely"
        ) from exc
    minimum_x, minimum_y, maximum_x, maximum_y = geometry.bounds
    header = (
        b"GP"
        + bytes((0, 3))
        + struct.pack(
            "<i4d",
            srs_id,
            minimum_x,
            maximum_x,
            minimum_y,
            maximum_y,
        )
    )
    return header + to_wkb(
        geometry,
        hex=False,
        byte_order=1,
        include_srid=False,
    )


def _gpkg_bytes(
    features: Iterable[VectorFeature],
    *,
    generated_at_utc: str,
) -> bytes:
    features = list(features)
    minimum_x = min(item.geometry.bounds[0] for item in features)
    minimum_y = min(item.geometry.bounds[1] for item in features)
    maximum_x = max(item.geometry.bounds[2] for item in features)
    maximum_y = max(item.geometry.bounds[3] for item in features)
    timestamp = generated_at_utc.replace("Z", ".000Z")
    definition_32610 = rasterio.crs.CRS.from_epsg(32610).to_wkt(
        version="WKT1_GDAL"
    )
    definition_4326 = rasterio.crs.CRS.from_epsg(4326).to_wkt(
        version="WKT1_GDAL"
    )
    connection = sqlite3.connect(":memory:")
    try:
        connection.execute("PRAGMA application_id = 1196444487")
        connection.execute("PRAGMA user_version = 10300")
        connection.execute("PRAGMA page_size = 4096")
        connection.execute(
            """
            CREATE TABLE gpkg_spatial_ref_sys (
              srs_name TEXT NOT NULL,
              srs_id INTEGER NOT NULL PRIMARY KEY,
              organization TEXT NOT NULL,
              organization_coordsys_id INTEGER NOT NULL,
              definition TEXT NOT NULL,
              description TEXT
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE gpkg_contents (
              table_name TEXT NOT NULL PRIMARY KEY,
              data_type TEXT NOT NULL,
              identifier TEXT UNIQUE,
              description TEXT DEFAULT '',
              last_change DATETIME NOT NULL,
              min_x DOUBLE,
              min_y DOUBLE,
              max_x DOUBLE,
              max_y DOUBLE,
              srs_id INTEGER
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE gpkg_geometry_columns (
              table_name TEXT NOT NULL,
              column_name TEXT NOT NULL,
              geometry_type_name TEXT NOT NULL,
              srs_id INTEGER NOT NULL,
              z TINYINT NOT NULL,
              m TINYINT NOT NULL,
              PRIMARY KEY (table_name, column_name)
            )
            """
        )
        connection.executemany(
            "INSERT INTO gpkg_spatial_ref_sys VALUES (?, ?, ?, ?, ?, ?)",
            [
                (
                    "Undefined Cartesian",
                    -1,
                    "NONE",
                    -1,
                    "undefined",
                    "undefined Cartesian coordinate reference system",
                ),
                (
                    "Undefined Geographic",
                    0,
                    "NONE",
                    0,
                    "undefined",
                    "undefined geographic coordinate reference system",
                ),
                (
                    "WGS 84 geodetic",
                    4326,
                    "EPSG",
                    4326,
                    definition_4326,
                    "longitude/latitude",
                ),
                (
                    "WGS 84 / UTM zone 10N",
                    32610,
                    "EPSG",
                    32610,
                    definition_32610,
                    "Ward Creek native projected grid",
                ),
            ],
        )
        connection.execute(
            """
            CREATE TABLE rbr_accepted (
              fid INTEGER PRIMARY KEY NOT NULL,
              geom BLOB NOT NULL,
              candidate_id TEXT NOT NULL,
              component_id TEXT NOT NULL UNIQUE,
              pixel_count INTEGER NOT NULL,
              area_m2 DOUBLE NOT NULL,
              analytical_method TEXT NOT NULL,
              analytical_status TEXT NOT NULL
            )
            """
        )
        connection.execute(
            "INSERT INTO gpkg_geometry_columns VALUES (?, ?, ?, ?, ?, ?)",
            (GPKG_LAYER, "geom", "MULTIPOLYGON", 32610, 0, 0),
        )
        connection.execute(
            """
            INSERT INTO gpkg_contents
            (table_name, data_type, identifier, description, last_change,
             min_x, min_y, max_x, max_y, srs_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                GPKG_LAYER,
                "features",
                "BurnLens accepted RBR polygons",
                (
                    "Experimental accepted-baseline polygons. Not official "
                    "wildfire information or emergency guidance."
                ),
                timestamp,
                minimum_x,
                minimum_y,
                maximum_x,
                maximum_y,
                32610,
            ),
        )
        for item in features:
            connection.execute(
                """
                INSERT INTO rbr_accepted
                (fid, geom, candidate_id, component_id, pixel_count, area_m2,
                 analytical_method, analytical_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item.fid,
                    sqlite3.Binary(_gpkg_geometry_blob(item.geometry, 32610)),
                    item.candidate_id,
                    item.component_id,
                    item.pixel_count,
                    item.area_m2,
                    "burnlens-baseline-v0.1.0 rbr-threshold",
                    "accepted-baseline",
                ),
            )
        connection.commit()
        integrity = connection.execute("PRAGMA integrity_check").fetchone()
        if integrity != ("ok",):
            raise PhaseFourGeospatialError(
                f"GeoPackage integrity check failed: {integrity}"
            )
        connection.execute("VACUUM")
        payload = connection.serialize()
    finally:
        connection.close()
    if not payload.startswith(b"SQLite format 3\x00"):
        raise PhaseFourGeospatialError("GeoPackage is not SQLite")
    return payload


def _round_coordinates(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_round_coordinates(item) for item in value]
    if isinstance(value, list):
        return [_round_coordinates(item) for item in value]
    if isinstance(value, float):
        return round(value, 8)
    return value


def _geojson_bytes(features: Iterable[VectorFeature]) -> bytes:
    try:
        from pyproj import Transformer
        from shapely.geometry import mapping
        from shapely.ops import transform
    except ImportError as exc:
        raise PhaseFourGeospatialError(
            "U03 requires the locked geo-research profile with PyProj and Shapely"
        ) from exc
    transformer = Transformer.from_crs(32610, 4326, always_xy=True)
    records: list[dict[str, Any]] = []
    all_bounds: list[tuple[float, float, float, float]] = []
    for item in features:
        projected = transform(transformer.transform, item.geometry)
        all_bounds.append(projected.bounds)
        geometry = mapping(projected)
        geometry["coordinates"] = _round_coordinates(geometry["coordinates"])
        records.append(
            {
                "type": "Feature",
                "id": item.component_id,
                "geometry": geometry,
                "properties": {
                    "candidate_id": item.candidate_id,
                    "component_id": item.component_id,
                    "pixel_count": item.pixel_count,
                    "area_m2": item.area_m2,
                    "analytical_method": "burnlens-baseline-v0.1.0 rbr-threshold",
                    "analytical_status": "accepted-baseline",
                    "source_precedence": "Official sources govern",
                },
            }
        )
    bbox = [
        round(min(item[0] for item in all_bounds), 8),
        round(min(item[1] for item in all_bounds), 8),
        round(max(item[2] for item in all_bounds), 8),
        round(max(item[3] for item in all_bounds), 8),
    ]
    payload = {
        "type": "FeatureCollection",
        "name": "BurnLens accepted RBR polygons",
        "bbox": bbox,
        "features": records,
        "warning": (
            "Experimental BurnLens accepted-baseline output. Not official "
            "wildfire information or emergency guidance. Official sources govern."
        ),
    }
    return _json_bytes(payload)


def _quicklook_bytes(
    patch_arrays: dict[str, dict[str, np.ndarray]],
    facts: dict[str, dict[str, Any]],
) -> bytes:
    width, height = 1280, 720
    canvas = Image.new("RGB", (width, height), "#101820")
    draw = ImageDraw.Draw(canvas)
    try:
        title_font = ImageFont.truetype("DejaVuSans-Bold.ttf", 34)
        body_font = ImageFont.truetype("DejaVuSans.ttf", 20)
        small_font = ImageFont.truetype("DejaVuSans.ttf", 16)
    except OSError:
        title_font = ImageFont.load_default(size=34)
        body_font = ImageFont.load_default(size=20)
        small_font = ImageFont.load_default(size=16)
    draw.text(
        (40, 28),
        "BurnLens Ward Creek - accepted RBR vs rejected U-Net",
        fill="#f5f1e8",
        font=title_font,
    )
    draw.text(
        (40, 78),
        "Diagnostic comparison only. Official sources govern.",
        fill="#f5c56b",
        font=body_font,
    )
    panels = [
        ("WCP-001", "RBR accepted", "rbr-binary", "#ff9d42"),
        ("WCP-001", "U-Net rejected", "unet-binary", "#e267c5"),
        ("WCP-002", "RBR accepted", "rbr-binary", "#ff9d42"),
        ("WCP-002", "U-Net rejected", "unet-binary", "#e267c5"),
    ]
    for index, (candidate, label, key, color) in enumerate(panels):
        x = 40 + index * 305
        y = 145
        array = patch_arrays[candidate][key]
        rgb = np.zeros((64, 64, 3), dtype=np.uint8)
        rgb[:, :] = np.array([37, 50, 58], dtype=np.uint8)
        selected = array == 1
        hex_color = color.lstrip("#")
        rgb[selected] = np.array(
            [int(hex_color[i : i + 2], 16) for i in (0, 2, 4)],
            dtype=np.uint8,
        )
        image = Image.fromarray(rgb, mode="RGB").resize(
            (256, 256), resample=Image.Resampling.NEAREST
        )
        canvas.paste(image, (x, y))
        draw.rectangle((x, y, x + 256, y + 256), outline="#d8d2c4", width=2)
        draw.text((x, y + 272), candidate, fill="#f5f1e8", font=body_font)
        draw.text((x, y + 302), label, fill=color, font=body_font)
        count_key = (
            "rbr_positive_pixels"
            if key == "rbr-binary"
            else "unet_diagnostic_positive_pixels"
        )
        draw.text(
            (x, y + 336),
            f"{facts[candidate][count_key]:,} / 4,096 pixels",
            fill="#c7d1d8",
            font=small_font,
        )
    draw.rounded_rectangle(
        (40, 575, 1240, 680),
        radius=12,
        fill="#242f35",
        outline="#58656b",
        width=2,
    )
    draw.text(
        (60, 592),
        (
            "The U-Net failed its frozen evaluation and remains a descriptive "
            "diagnostic. It is not the accepted perimeter."
        ),
        fill="#f5f1e8",
        font=body_font,
    )
    draw.text(
        (60, 630),
        (
            "Experimental output - not official, operational, field-validated, "
            "or suitable for emergency decisions."
        ),
        fill="#f5c56b",
        font=small_font,
    )
    buffer = io.BytesIO()
    canvas.save(buffer, format="PNG", optimize=False, compress_level=9)
    return buffer.getvalue()


def build_geospatial_products(
    *,
    repository_root: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> GeospatialBuild:
    """Build exact U03 bytes from the accepted U02 run."""

    root = repository_root.resolve()
    if not RUN_ID_PATTERN.fullmatch(run_id):
        raise PhaseFourGeospatialError("run ID does not match the U03 contract")
    if not COMMIT_PATTERN.fullmatch(git_source_commit):
        raise PhaseFourGeospatialError("git source commit is invalid")
    contract = load_contract(root)
    u02_record, u02_run = _verify_u02_run(root)
    u02_manifest = _read_json(u02_run / "ANALYSIS-MANIFEST.json")
    by_candidate = {
        item["candidate_id"]: item for item in contract["integration_roster"]
    }
    patch_arrays: dict[str, dict[str, np.ndarray]] = {}
    output_bytes: dict[str, bytes] = {}
    raster_records: list[dict[str, Any]] = []
    definitions = [
        ("rbr-score", "rbr-score.npy", np.dtype("float32"), FLOAT_NODATA),
        ("rbr-binary", "rbr-binary.npy", np.dtype("uint8"), BYTE_NODATA),
        ("exclusion", "exclusion.npy", np.dtype("uint8"), BYTE_NODATA),
        (
            "unet-probability",
            "unet-probability-diagnostic.npy",
            np.dtype("float32"),
            FLOAT_NODATA,
        ),
        (
            "unet-binary",
            "unet-binary-diagnostic.npy",
            np.dtype("uint8"),
            BYTE_NODATA,
        ),
    ]
    for candidate_id in sorted(by_candidate):
        source = u02_run / "patches" / candidate_id
        patch_arrays[candidate_id] = {}
        for role, source_name, dtype, nodata in definitions:
            array = _npy(source / source_name, shape=(64, 64), dtype=dtype)
            patch_arrays[candidate_id][role] = array
            name = (
                f"{role}-diagnostic.tif"
                if role.startswith("unet")
                else f"{role}.tif"
            )
            relative = f"patches/{candidate_id}/{name}"
            payload = _geotiff_bytes(
                array,
                crs=by_candidate[candidate_id]["crs"],
                transform=by_candidate[candidate_id]["transform"],
                nodata=nodata,
                role=role,
                run_id=run_id,
            )
            output_bytes[relative] = payload
            raster_records.append(
                {
                    **_receipt(relative, payload),
                    "candidate_id": candidate_id,
                    "role": role,
                    "crs": by_candidate[candidate_id]["crs"],
                    "transform": by_candidate[candidate_id]["transform"],
                    "shape": [64, 64],
                    "dtype": dtype.name,
                    "nodata": nodata,
                }
            )

    features = _polygon_features(patch_arrays, contract)
    gpkg_relative = "vectors/rbr-accepted-polygons.gpkg"
    geojson_relative = "vectors/rbr-accepted-polygons.geojson"
    gpkg = _gpkg_bytes(features, generated_at_utc=generated_at_utc)
    geojson = _geojson_bytes(features)
    output_bytes[gpkg_relative] = gpkg
    output_bytes[geojson_relative] = geojson
    facts = {
        item["candidate_id"]: item["facts"]
        for item in u02_manifest["patches"]
    }
    quicklook_relative = "GEOSPATIAL-QUICKLOOK.png"
    quicklook = _quicklook_bytes(patch_arrays, facts)
    output_bytes[quicklook_relative] = quicklook
    vector_summary = {
        candidate_id: {
            "component_count": sum(
                item.candidate_id == candidate_id for item in features
            ),
            "pixel_count": sum(
                item.pixel_count
                for item in features
                if item.candidate_id == candidate_id
            ),
            "area_m2": sum(
                item.area_m2
                for item in features
                if item.candidate_id == candidate_id
            ),
        }
        for candidate_id in sorted(by_candidate)
    }
    for candidate_id in vector_summary:
        if (
            vector_summary[candidate_id]["pixel_count"]
            != facts[candidate_id]["rbr_positive_pixels"]
        ):
            raise PhaseFourGeospatialError(
                f"vector/raster pixel-count mismatch: {candidate_id}"
            )
    validation = {
        "validation_version": "burnlens-phase-four-geospatial-validation-v0.1.0",
        "run_id": run_id,
        "raster_count": len(raster_records),
        "all_rasters_read_back_exact": True,
        "native_crs": "EPSG:32610",
        "native_resolution_m": 20,
        "vector_layer": GPKG_LAYER,
        "geometry_type": "MULTIPOLYGON",
        "geometry_count": len(features),
        "all_geometries_valid": True,
        "polygonization_connectivity": 4,
        "raw_binary_polygonization": True,
        "simplification": "none",
        "vector_summary": vector_summary,
        "web_representation_crs": "EPSG:4326",
        "web_coordinate_rounding_decimal_places": 8,
        "raster_vector_pixel_counts_match": True,
    }
    validation_relative = "GEOSPATIAL-VALIDATION.json"
    output_bytes[validation_relative] = _json_bytes(validation)
    status = {
        "status_version": "burnlens-phase-four-geospatial-status-v0.1.0",
        "run_id": run_id,
        "state": "accepted-baseline",
        "accepted_method": "burnlens-baseline-v0.1.0",
        "rejected_model": "burnlens-unet-binary-v0.1.0",
        "model_accepted": False,
        "model_outperformed_rbr": False,
        "geospatial_products_complete": True,
        "context_complete": False,
        "publishable": False,
        "next_dependency": "P4O1-T01-U04 context source and terms gate",
    }
    output_bytes["STATUS.json"] = _json_bytes(status)
    inventory = [
        _receipt(path, payload)
        for path, payload in sorted(
            output_bytes.items(), key=lambda item: item[0].casefold()
        )
    ]
    manifest = {
        "geospatial_version": GEOSPATIAL_VERSION,
        "geospatial_id": "PHASE-FOUR-GEOSPATIAL-PRODUCTS-2026-001",
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "issue": 570,
        "unit_id": "P4O1-T01-U03",
        "git_source_commit": git_source_commit,
        "software_version_at_execution": SOFTWARE_VERSION,
        "state": "accepted-baseline",
        "route": "baseline-primary-with-rejected-model-diagnostic",
        "contract": {
            "path": (
                "records/phase-four/contracts/"
                "PHASE-FOUR-INTEGRATION-CONTRACT-2026-001.json"
            ),
            "sha256": _sha256_file(
                root
                / "records/phase-four/contracts/"
                "PHASE-FOUR-INTEGRATION-CONTRACT-2026-001.json"
            ),
        },
        "u02_analysis": {
            "record_path": U02_RECORD_PATH.as_posix(),
            "record_sha256": U02_RECORD_SHA256,
            "run_id": u02_record["run_id"],
            "inventory_sha256": u02_record["ignored_run_inventory"][
                "inventory_sha256"
            ],
            "manifest_sha256": u02_record["ignored_run_inventory"]["files"][0][
                "sha256"
            ],
        },
        "accepted_method": "burnlens-baseline-v0.1.0 rbr-threshold",
        "rejected_diagnostic": {
            "model_version": "burnlens-unet-binary-v0.1.0",
            "accepted": False,
            "outperformed_rbr": False,
            "probability_calibrated": False,
        },
        "rasters": raster_records,
        "vectors": {
            "authoritative": _receipt(gpkg_relative, gpkg),
            "web": _receipt(geojson_relative, geojson),
            "summary": vector_summary,
        },
        "quicklook": _receipt(quicklook_relative, quicklook),
        "validation": validation,
        "output_inventory": inventory,
        "warnings": [
            "Experimental BurnLens CV output; official sources govern.",
            "RBR is the accepted method only for this bounded demonstration.",
            "The U-Net is a rejected diagnostic and did not outperform RBR.",
            "Polygons are raw 4-connected representations of accepted RBR pixels, not official fire perimeters.",
            "No context source, exposure-style summary, or public interface is accepted at U03."
        ],
        "boundaries": {
            "model_accepted": False,
            "model_outperformed_rbr": False,
            "retraining": False,
            "retuning": False,
            "phase_3b_created": False,
            "second_experiment_planned": False,
            "context_source_used": False,
            "context_complete": False,
            "summary_complete": False,
            "interface_complete": False,
            "deployment": False,
            "official_operational_or_emergency_claim": False,
        },
        "disposition": "pass-geospatial-products-pending-context",
        "next_dependency": "P4O1-T01-U04 context source and terms gate",
    }
    output_bytes["GEOSPATIAL-MANIFEST.json"] = _json_bytes(manifest)
    return GeospatialBuild(manifest=manifest, outputs=output_bytes)


def _require_exact_clean_head(root: Path, git_source_commit: str) -> None:
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if head != git_source_commit:
        raise PhaseFourGeospatialError("git source commit differs from HEAD")
    status = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    if status:
        raise PhaseFourGeospatialError("working tree must be clean before U03")


def _write_new(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    created = False
    try:
        with path.open("xb") as stream:
            created = True
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        if path.read_bytes() != payload:
            raise PhaseFourGeospatialError(f"output readback differs: {path}")
    except Exception:
        if created and path.exists():
            path.unlink()
        raise


def run_geospatial_products(
    *,
    repository_root: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> GeospatialBuild:
    """Write one no-overwrite immutable U03 geospatial attempt."""

    root = repository_root.resolve()
    _require_exact_clean_head(root, git_source_commit)
    run_directory = root / RUN_ROOT / run_id
    if run_directory.exists() or run_directory.is_symlink():
        raise PhaseFourGeospatialError(f"run already exists: {run_id}")
    run_directory.mkdir(parents=True)
    started = {
        "attempt_version": "burnlens-phase-four-attempt-v0.1.0",
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "git_source_commit": git_source_commit,
        "status": "STARTED",
    }
    _write_new(run_directory / "RUN-STARTED.json", _json_bytes(started))
    try:
        build = build_geospatial_products(
            repository_root=root,
            generated_at_utc=generated_at_utc,
            run_id=run_id,
            git_source_commit=git_source_commit,
        )
        for relative, payload in sorted(
            build.outputs.items(), key=lambda item: item[0].casefold()
        ):
            _write_new(run_directory / relative, payload)
        complete = {
            **started,
            "status": "COMPLETE",
            "state": build.manifest["state"],
            "output_count": len(build.outputs),
            "manifest_sha256": sha256(
                build.outputs["GEOSPATIAL-MANIFEST.json"]
            ).hexdigest(),
        }
        _write_new(run_directory / "RUN-COMPLETE.json", _json_bytes(complete))
        return build
    except Exception as exc:
        failure = {
            **started,
            "status": "FAILED",
            "error_type": type(exc).__name__,
            "error": str(exc),
        }
        try:
            _write_new(run_directory / "FAILURE.json", _json_bytes(failure))
        except Exception:
            pass
        raise
