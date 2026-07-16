"""Acquire and verify two exact public MTBS annual-severity reference clips.

The clips are analyst-interpreted reference evidence for the frozen Tepee and
McKay events.  They are not field truth, operational perimeters, or automatic
burned-pixel labels.  Provider bytes remain in ignored local storage.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
from typing import Any, Iterable
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import numpy as np
import rasterio
from rasterio.io import MemoryFile

from .provider_acquisition import USER_AGENT


SOFTWARE_VERSION = "0.12.0"
PACKAGE_ID = "burnlens-mtbs-cross-event-reference-v0.1.0"
CONTRACT_VERSION = "mtbs-cross-event-reference-contract-v0.1.0"
SOURCE_RECORD_ID = "SOURCE-2026-013"
TERMS_REVIEW_ID = "TERMS-2026-008"
REGISTRATION_MANIFEST_NAME = ".burnlens-registration.json"
IMAGE_SERVICE_URL = (
    "https://imagery.geoplatform.gov/iipp/rest/services/Fire_Aviation/"
    "USFS_EDW_MTBS_CONUS/ImageServer"
)
SERVICE_ITEM_ID = "b84dc1dbb08149aca566adaaa78c1442"
SERVICE_VERSION = 12
PIXEL_SIZE_M = 30.0
ALLOWED_VALUES = frozenset(range(7))
MAX_CLIP_BYTES = 10 * 1024 * 1024


class MtbsReferenceError(RuntimeError):
    """A deterministic, secret-free MTBS reference failure."""


@dataclass(frozen=True)
class MtbsReferenceContract:
    event_group_id: str
    fire_id: str
    year: int
    filename: str
    bbox_3857: tuple[float, float, float, float]
    width: int
    height: int
    expected_size_bytes: int
    expected_sha256: str
    expected_value_counts: tuple[tuple[int, int], ...]


CONTRACTS = (
    MtbsReferenceContract(
        event_group_id="event-tepee-1144-ne-2018",
        fire_id="OR4383912111420180907",
        year=2018,
        filename="event-tepee-1144-ne-2018-mtbs-2018.tif",
        bbox_3857=(-13483488.8586, 5439388.999, -13473648.8586, 5443138.999),
        width=328,
        height=125,
        expected_size_bytes=50_316,
        expected_sha256="7414409447cf2abe21ebc1060b3724e49937900b7fcc821207f7211babc51dfa",
        expected_value_counts=((0, 21912), (1, 2121), (2, 10763), (3, 5556), (4, 636), (5, 12)),
    ),
    MtbsReferenceContract(
        event_group_id="event-mckay-1035-ne-2017",
        fire_id="OR4375212142520170829",
        year=2017,
        filename="event-mckay-1035-ne-2017-mtbs-2017.tif",
        bbox_3857=(-13517118.8586, 5426458.999, -13511748.8586, 5429488.999),
        width=179,
        height=101,
        expected_size_bytes=33_922,
        expected_sha256="7122729aa63018b934774fa4f47b034a15e44f7324487f813533202ad5cefb96",
        expected_value_counts=((0, 7188), (1, 178), (2, 3631), (3, 3391), (4, 3691)),
    ),
)


def _write_utf8_lf(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8"))


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_sha256(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return sha256(payload.encode("utf-8")).hexdigest()


def export_url(contract: MtbsReferenceContract) -> str:
    rule = {
        "mosaicMethod": "esriMosaicAttribute",
        "sortField": "Year",
        "sortValue": str(contract.year),
        "ascending": True,
        "where": f"Year={contract.year}",
    }
    params = (
        ("bbox", ",".join(str(value) for value in contract.bbox_3857)),
        ("bboxSR", "3857"),
        ("size", f"{contract.width},{contract.height}"),
        ("imageSR", "3857"),
        ("format", "tiff"),
        ("pixelType", "U8"),
        ("interpolation", "RSP_NearestNeighbor"),
        ("mosaicRule", json.dumps(rule, separators=(",", ":"))),
        ("f", "image"),
    )
    return f"{IMAGE_SERVICE_URL}/exportImage?{urlencode(params)}"


def validate_contracts(contracts: Iterable[MtbsReferenceContract] = CONTRACTS) -> list[str]:
    items = list(contracts)
    reasons: list[str] = []
    if len(items) != 2:
        reasons.append("CONTRACT_REQUIRES_TWO_CLIPS")
        return reasons
    if len({item.event_group_id for item in items}) != 2 or len({item.filename for item in items}) != 2:
        reasons.append("CONTRACT_IDENTITY_NOT_UNIQUE")
    for item in items:
        xmin, ymin, xmax, ymax = item.bbox_3857
        if item.width <= 0 or item.height <= 0 or xmax <= xmin or ymax <= ymin:
            reasons.append(f"INVALID_GRID:{item.event_group_id}")
            continue
        if abs((xmax - xmin) / item.width - PIXEL_SIZE_M) > 1e-9:
            reasons.append(f"X_RESOLUTION_MISMATCH:{item.event_group_id}")
        if abs((ymax - ymin) / item.height - PIXEL_SIZE_M) > 1e-9:
            reasons.append(f"Y_RESOLUTION_MISMATCH:{item.event_group_id}")
        if len(item.expected_sha256) != 64 or item.expected_size_bytes <= 0:
            reasons.append(f"BYTE_CONTRACT_INVALID:{item.event_group_id}")
        counts = dict(item.expected_value_counts)
        if not set(counts).issubset(ALLOWED_VALUES) or sum(counts.values()) != item.width * item.height:
            reasons.append(f"VALUE_CONTRACT_INVALID:{item.event_group_id}")
    return reasons


def inspect_clip(path: Path, contract: MtbsReferenceContract) -> dict[str, Any]:
    if not path.is_file():
        raise MtbsReferenceError(f"MTBS clip is missing: {contract.filename}")
    stat = path.stat()
    if stat.st_nlink not in {1, 2}:
        raise MtbsReferenceError(f"MTBS provider clip link count is unsupported: {contract.filename}")
    if stat.st_size != contract.expected_size_bytes:
        raise MtbsReferenceError(f"MTBS clip size mismatch: {contract.filename}")
    provider_bytes = path.read_bytes()
    if len(provider_bytes) != contract.expected_size_bytes:
        raise MtbsReferenceError(f"MTBS clip bounded-read size mismatch: {contract.filename}")
    digest = sha256(provider_bytes).hexdigest()
    if digest != contract.expected_sha256:
        raise MtbsReferenceError(f"MTBS clip hash mismatch: {contract.filename}")
    with MemoryFile(provider_bytes) as memory:
        with memory.open() as source:
            if source.driver != "GTiff" or source.crs is None or source.crs.to_epsg() != 3857:
                raise MtbsReferenceError(f"MTBS clip format/CRS mismatch: {contract.filename}")
            if source.count != 1 or source.dtypes != ("uint8",):
                raise MtbsReferenceError(f"MTBS clip band/dtype mismatch: {contract.filename}")
            if source.width != contract.width or source.height != contract.height:
                raise MtbsReferenceError(f"MTBS clip dimensions mismatch: {contract.filename}")
            expected_transform = (
                PIXEL_SIZE_M,
                0.0,
                contract.bbox_3857[0],
                0.0,
                -PIXEL_SIZE_M,
                contract.bbox_3857[3],
            )
            observed_transform = tuple(float(value) for value in source.transform[:6])
            if any(abs(a - b) > 1e-6 for a, b in zip(observed_transform, expected_transform)):
                raise MtbsReferenceError(f"MTBS clip transform mismatch: {contract.filename}")
            # Rasterio's two-dimensional band-read path currently mutates
            # ndarray.shape, which NumPy 2.5 deprecates. A pre-sized
            # three-dimensional output avoids that library warning.
            values = source.read(
                out=np.empty((1, source.height, source.width), dtype=np.uint8)
            )[0]
            counts = {int(value): int((values == value).sum()) for value in np.unique(values)}
    if not set(counts).issubset(ALLOWED_VALUES) or counts != dict(contract.expected_value_counts):
        raise MtbsReferenceError(f"MTBS clip value-domain mismatch: {contract.filename}")
    return {
        "event_group_id": contract.event_group_id,
        "fire_id": contract.fire_id,
        "year": contract.year,
        "filename": contract.filename,
        "size_bytes": stat.st_size,
        "sha256": digest,
        "link_count": stat.st_nlink,
        "link_gate": (
            "pass: single linked"
            if stat.st_nlink == 1
            else "pass by exact two-link OneDrive exception: one bounded read, SHA-256, and in-memory raster inspection"
        ),
        "driver": "GTiff",
        "crs": "EPSG:3857",
        "dtype": "uint8",
        "width": contract.width,
        "height": contract.height,
        "transform": [round(value, 9) for value in expected_transform],
        "bbox_3857": list(contract.bbox_3857),
        "pixel_size_m": PIXEL_SIZE_M,
        "value_counts": {str(key): value for key, value in sorted(counts.items())},
        "request_url": export_url(contract),
    }


def _service_snapshot() -> dict[str, Any]:
    request = Request(f"{IMAGE_SERVICE_URL}?f=pjson", headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(request, timeout=60) as response:
            payload = json.loads(response.read(MAX_CLIP_BYTES).decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise MtbsReferenceError("MTBS image-service metadata is unavailable") from error
    selected = {
        "name": payload.get("name"),
        "current_version": payload.get("currentVersion"),
        "service_item_id": payload.get("serviceItemId"),
        "band_count": payload.get("bandCount"),
        "pixel_type": payload.get("pixelType"),
        "pixel_size_x": payload.get("pixelSizeX"),
        "pixel_size_y": payload.get("pixelSizeY"),
        "min_values": payload.get("minValues"),
        "max_values": payload.get("maxValues"),
        "default_resampling_method": payload.get("defaultResamplingMethod"),
        "copyright_text": payload.get("copyrightText"),
    }
    if (
        selected["current_version"] != SERVICE_VERSION
        or selected["service_item_id"] != SERVICE_ITEM_ID
        or selected["band_count"] != 1
        or selected["pixel_type"] != "U8"
        or selected["pixel_size_x"] != PIXEL_SIZE_M
        or selected["pixel_size_y"] != PIXEL_SIZE_M
        or selected["min_values"] != [1]
        or selected["max_values"] != [6]
        or selected["default_resampling_method"] != "Nearest"
    ):
        raise MtbsReferenceError("MTBS image-service contract drifted")
    selected["canonical_sha256"] = _canonical_sha256(selected)
    return selected


def _download(path: Path, contract: MtbsReferenceContract) -> None:
    request = Request(export_url(contract), headers={"User-Agent": USER_AGENT, "Accept": "image/tiff"})
    temporary = path.with_suffix(path.suffix + ".part")
    if temporary.exists():
        if temporary.stat().st_nlink != 1:
            raise MtbsReferenceError("MTBS temporary clip has multiple filesystem links")
        temporary.unlink()
    total = 0
    try:
        with urlopen(request, timeout=180) as response, temporary.open("xb") as handle:
            while chunk := response.read(1024 * 1024):
                total += len(chunk)
                if total > MAX_CLIP_BYTES:
                    raise MtbsReferenceError("MTBS clip exceeds the bounded transfer limit")
                handle.write(chunk)
        os.replace(temporary, path)
    except Exception:
        if temporary.exists() and temporary.stat().st_nlink == 1:
            temporary.unlink()
        raise


def _restore_single_link(path: Path, contract: MtbsReferenceContract) -> bool:
    """Replace only the repo pathname when OneDrive adds an external alias."""
    if not path.is_file() or path.stat().st_nlink == 1:
        return False
    if path.stat().st_size != contract.expected_size_bytes or _sha256_file(path) != contract.expected_sha256:
        raise MtbsReferenceError(f"multiply linked MTBS clip changed: {contract.filename}")
    replacement = path.with_suffix(path.suffix + ".single-link")
    if replacement.exists():
        if replacement.stat().st_nlink != 1:
            raise MtbsReferenceError("MTBS single-link replacement was externally aliased")
        replacement.unlink()
    with path.open("rb") as source, replacement.open("xb") as destination:
        shutil.copyfileobj(source, destination, length=1024 * 1024)
    if replacement.stat().st_nlink != 1:
        raise MtbsReferenceError("MTBS single-link replacement was externally aliased")
    if replacement.stat().st_size != contract.expected_size_bytes or _sha256_file(replacement) != contract.expected_sha256:
        raise MtbsReferenceError("MTBS single-link replacement changed content")
    os.replace(replacement, path)
    if path.stat().st_nlink != 1:
        raise MtbsReferenceError("MTBS clip remains multiply linked after safe replacement")
    return True


def acquire_package(
    destination: Path,
    *,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, Any]:
    reasons = validate_contracts()
    if reasons:
        raise MtbsReferenceError("invalid MTBS reference contract: " + ",".join(reasons))
    destination.mkdir(parents=True, exist_ok=True)
    service = _service_snapshot()
    assets: list[dict[str, Any]] = []
    for contract in CONTRACTS:
        path = destination / contract.filename
        single_link_restored = _restore_single_link(path, contract)
        try:
            asset = inspect_clip(path, contract)
        except MtbsReferenceError:
            if path.exists():
                raise
            _download(path, contract)
            asset = inspect_clip(path, contract)
        asset["single_link_restored_during_acquisition"] = single_link_restored
        assets.append(asset)
    manifest = {
        "package_id": PACKAGE_ID,
        "contract_version": CONTRACT_VERSION,
        "source_record_id": SOURCE_RECORD_ID,
        "terms_review_id": TERMS_REVIEW_ID,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": 367,
        "git_source_commit": git_source_commit,
        "software_version": SOFTWARE_VERSION,
        "source": {
            "organization": "Monitoring Trends in Burn Severity Program (USGS and USDA Forest Service)",
            "image_service_url": IMAGE_SERVICE_URL,
            "service": service,
            "access_route": "public ArcGIS ImageServer exportImage; no credential or email queue",
            "reference_role": "analyst-interpreted annual thematic severity; never automatic truth",
        },
        "contracts": [asdict(item) for item in CONTRACTS],
        "assets": assets,
    }
    _write_utf8_lf(
        destination / REGISTRATION_MANIFEST_NAME,
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
    )
    return verify_package(destination)


def verify_package(destination: Path) -> dict[str, Any]:
    manifest_path = destination / REGISTRATION_MANIFEST_NAME
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise MtbsReferenceError("MTBS registration manifest is unreadable") from error
    if (
        manifest.get("package_id") != PACKAGE_ID
        or manifest.get("contract_version") != CONTRACT_VERSION
        or manifest.get("source_record_id") != SOURCE_RECORD_ID
        or manifest.get("terms_review_id") != TERMS_REVIEW_ID
    ):
        raise MtbsReferenceError("MTBS registration manifest identity mismatch")
    assets = [inspect_clip(destination / contract.filename, contract) for contract in CONTRACTS]
    declared = {item.get("event_group_id"): item for item in manifest.get("assets", []) if isinstance(item, dict)}
    if len(declared) != 2:
        raise MtbsReferenceError("MTBS registration manifest assets are incomplete")
    for asset in assets:
        item = declared.get(asset["event_group_id"])
        if not item or item.get("sha256") != asset["sha256"] or item.get("size_bytes") != asset["size_bytes"]:
            raise MtbsReferenceError("MTBS registration manifest asset mismatch")
    return {
        "accepted_as_unchanged_registered_package": True,
        "package_id": PACKAGE_ID,
        "contract_version": CONTRACT_VERSION,
        "source_record_id": SOURCE_RECORD_ID,
        "terms_review_id": TERMS_REVIEW_ID,
        "registration_manifest_name": REGISTRATION_MANIFEST_NAME,
        "registration_manifest_sha256": _sha256_file(manifest_path),
        "registration_manifest_link_count": manifest_path.stat().st_nlink,
        "registration": manifest,
        "assets": assets,
    }
