"""Offline functional verification for the locked BurnLens environments."""

from __future__ import annotations

import argparse
import importlib
import importlib.metadata
import json
import platform
import shutil
import subprocess
import sys
import tempfile
import tomllib
import warnings
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROFILES = ("runtime", "dev", "geo-research")
IMPORT_NAMES = {
    "Pillow": "PIL",
    "pystac-client": "pystac_client",
}


def _load_project() -> dict[str, Any]:
    with (ROOT / "pyproject.toml").open("rb") as stream:
        return tomllib.load(stream)


def _parse_exact_requirement(requirement: str) -> tuple[str, str]:
    if requirement.count("==") != 1:
        raise ValueError(f"Environment dependency is not exactly pinned: {requirement}")
    name, version = requirement.split("==", 1)
    if not name or not version or any(token in version for token in (";", " ", "*")):
        raise ValueError(f"Environment dependency is not a simple exact pin: {requirement}")
    return name, version


def _requirements(profile: str) -> list[tuple[str, str]]:
    project = _load_project()["project"]
    raw = list(project["dependencies"])
    optional = project.get("optional-dependencies", {})
    if profile in {"dev", "geo-research"}:
        raw.extend(optional["dev"])
    if profile == "geo-research":
        raw.extend(optional["geo-research"])
    return [_parse_exact_requirement(item) for item in raw]


def _verify_python_pin() -> None:
    expected = (ROOT / ".python-version").read_text(encoding="utf-8").strip()
    actual = platform.python_version()
    if actual != expected:
        raise RuntimeError(f"Python version mismatch: expected {expected}, found {actual}")


def _verify_versions(profile: str) -> dict[str, str]:
    import burnlens

    expected_project = _load_project()["project"]["version"]
    installed_project = importlib.metadata.version("burnlens-deschutes")
    source_project = burnlens.__version__
    if installed_project != expected_project or source_project != expected_project:
        raise RuntimeError(
            "BurnLens version mismatch: "
            f"pyproject={expected_project}, distribution={installed_project}, source={source_project}"
        )

    versions: dict[str, str] = {}
    for distribution, expected in _requirements(profile):
        actual = importlib.metadata.version(distribution)
        if actual != expected:
            raise RuntimeError(
                f"Package version mismatch for {distribution}: expected {expected}, found {actual}"
            )
        importlib.import_module(IMPORT_NAMES.get(distribution, distribution.replace("-", "_")))
        versions[distribution] = actual
    versions["burnlens-deschutes"] = expected_project
    return dict(sorted(versions.items(), key=lambda item: item[0].lower()))


def _verify_console_entry_points() -> dict[str, Any]:
    expected = _load_project()["project"]["scripts"]
    distribution = importlib.metadata.distribution("burnlens-deschutes")
    candidates = [
        entry_point
        for entry_point in distribution.entry_points
        if entry_point.group == "console_scripts"
    ]
    installed = {entry_point.name: entry_point for entry_point in candidates}
    if len(installed) != len(candidates):
        raise RuntimeError("Installed BurnLens console entry points contain duplicates")
    if set(installed) != set(expected):
        missing = sorted(set(expected) - set(installed))
        unexpected = sorted(set(installed) - set(expected))
        raise RuntimeError(
            "Installed BurnLens console entry-point roster mismatch: "
            f"missing={missing}, unexpected={unexpected}"
        )
    script_directory = str(Path(sys.executable).resolve().parent)
    help_checked: list[str] = []
    for name in sorted(expected):
        entry_point = installed[name]
        if entry_point.value != expected[name]:
            raise RuntimeError(
                f"Installed BurnLens console entry-point target mismatch for {name}: "
                f"expected {expected[name]}, found {entry_point.value}"
            )
        loaded = entry_point.load()
        if not callable(loaded):
            raise RuntimeError(f"Installed BurnLens console entry point is not callable: {name}")
        executable = shutil.which(name, path=script_directory)
        if executable is None:
            raise RuntimeError(f"Installed BurnLens console entry-point launcher is missing: {name}")
        help_result = subprocess.run(
            [executable, "--help"],
            cwd=ROOT,
            capture_output=True,
            check=False,
            text=True,
            timeout=30,
        )
        if help_result.returncode != 0:
            raise RuntimeError(
                f"Installed BurnLens console entry-point help failed for {name}: "
                f"exit={help_result.returncode}"
            )
        help_checked.append(name)
    names = sorted(installed)
    return {"count": len(names), "help_count": len(help_checked), "names": names}


def _verify_runtime_functions() -> dict[str, Any]:
    import blake3
    import h5py
    import numpy as np
    import rasterio
    from PIL import Image
    from rasterio.io import MemoryFile
    from rasterio.transform import from_origin

    array = np.arange(16, dtype=np.uint8).reshape(4, 4)
    transform = from_origin(600_000, 4_890_000, 20, 20)
    with MemoryFile() as memory_file:
        with memory_file.open(
            driver="GTiff",
            height=4,
            width=4,
            count=1,
            dtype=array.dtype,
            crs="EPSG:32610",
            transform=transform,
        ) as dataset:
            dataset.write(array, 1)
        with memory_file.open() as dataset:
            # Rasterio 1.5.0 uses a deprecated ndarray shape setter under the
            # canonical NumPy 2.5.1. Keep the existing compatibility warning
            # from obscuring setup output while allowing every other warning.
            with warnings.catch_warnings():
                warnings.filterwarnings(
                    "ignore",
                    message="Setting the shape on a NumPy array has been deprecated.*",
                    category=DeprecationWarning,
                )
                reopened = dataset.read(1)
            if dataset.crs.to_epsg() != 32610 or int(reopened.sum()) != 120:
                raise RuntimeError("Rasterio in-memory GeoTIFF round trip failed")

    with tempfile.TemporaryDirectory(prefix="burnlens-env-") as temp_directory:
        h5_path = Path(temp_directory) / "smoke.h5"
        with h5py.File(h5_path, "w") as output:
            output.create_dataset("values", data=array)
        with h5py.File(h5_path, "r") as reopened:
            if int(reopened["values"][:].sum()) != 120:
                raise RuntimeError("HDF5 round trip failed")

    image = Image.new("RGB", (2, 2), color=(12, 34, 56))
    if image.getpixel((0, 0)) != (12, 34, 56):
        raise RuntimeError("Pillow pixel round trip failed")

    digest = blake3.blake3(b"burnlens-environment-smoke").hexdigest()
    if len(digest) != 64:
        raise RuntimeError("BLAKE3 digest check failed")

    return {
        "blake3_digest_length": len(digest),
        "gdal": rasterio.__gdal_version__,
        "raster_sum": int(array.sum()),
        "rasterio": rasterio.__version__,
    }


def _verify_geo_functions() -> dict[str, Any]:
    import boto3
    import geopandas as gpd
    import numpy as np
    import pyogrio
    import pyproj
    import pystac_client
    import rasterio
    import rioxarray
    import shapely
    import xarray
    from rasterio.transform import from_origin
    from shapely.geometry import box

    geometry = box(600_000, 4_889_960, 600_040, 4_890_000)
    frame = gpd.GeoDataFrame(
        {"candidate_id": ["offline-smoke"]}, geometry=[geometry], crs="EPSG:32610"
    )
    projected_area = float(frame.geometry.area.iloc[0])
    if projected_area != 1_600.0:
        raise RuntimeError(f"Projected area check failed: {projected_area}")
    overlap_area = float(geometry.intersection(box(600_020, 4_889_960, 600_060, 4_890_000)).area)
    if overlap_area != 800.0:
        raise RuntimeError(f"Shapely overlap check failed: {overlap_area}")

    geographic = frame.to_crs("EPSG:4326")
    min_x, min_y, max_x, max_y = (float(value) for value in geographic.total_bounds)
    if not (-123.0 < min_x < -120.0 and 43.0 < min_y < 46.0):
        raise RuntimeError("CRS transformation did not land in the expected Oregon range")
    if max_x <= min_x or max_y <= min_y:
        raise RuntimeError("CRS transformation produced invalid bounds")

    transformer = pyproj.Transformer.from_crs(32610, 4326, always_xy=True)
    longitude, latitude = transformer.transform(600_020, 4_889_980)
    if not (-123.0 < longitude < -120.0 and 43.0 < latitude < 46.0):
        raise RuntimeError("Direct PROJ transformation failed")

    with tempfile.TemporaryDirectory(prefix="burnlens-geo-env-") as temp_directory:
        directory = Path(temp_directory)
        vector_path = directory / "candidate.gpkg"
        raster_path = directory / "candidate.tif"

        pyogrio.write_dataframe(frame, vector_path, layer="candidates", driver="GPKG")
        reopened_vector = pyogrio.read_dataframe(vector_path, layer="candidates")
        if len(reopened_vector) != 1 or reopened_vector.crs.to_epsg() != 32610:
            raise RuntimeError("Pyogrio GeoPackage round trip failed")

        array = np.arange(16, dtype=np.uint8).reshape(4, 4)
        with rasterio.open(
            raster_path,
            "w",
            driver="GTiff",
            height=4,
            width=4,
            count=1,
            dtype=array.dtype,
            crs="EPSG:32610",
            transform=from_origin(600_000, 4_890_000, 20, 20),
        ) as dataset:
            dataset.write(array, 1)

        data_array = rioxarray.open_rasterio(raster_path, masked=False)
        try:
            if data_array.rio.crs.to_epsg() != 32610 or int(data_array.sum().item()) != 120:
                raise RuntimeError("Rioxarray raster round trip failed")
        finally:
            data_array.close()

    stac_client = pystac_client.Client.from_dict(
        {
            "type": "Catalog",
            "id": "offline-smoke",
            "stac_version": "1.0.0",
            "description": "BurnLens offline environment smoke catalog",
            "links": [],
        },
        href="https://example.invalid/stac",
    )
    if (
        stac_client.id != "offline-smoke"
        or stac_client.get_self_href() != "https://example.invalid/stac"
    ):
        raise RuntimeError("PySTAC offline client construction failed")

    offline_session = boto3.Session(
        aws_access_key_id="offline-smoke",
        aws_secret_access_key="offline-smoke",
        region_name="us-west-2",
    )
    if offline_session.region_name != "us-west-2":
        raise RuntimeError("Boto3 offline session check failed")
    s3_client = offline_session.client("s3", endpoint_url="https://example.invalid")
    if (
        s3_client.meta.service_model.service_name != "s3"
        or s3_client.meta.region_name != "us-west-2"
        or s3_client.meta.endpoint_url != "https://example.invalid"
    ):
        raise RuntimeError("Boto3 offline client construction failed")

    return {
        "aws_service": s3_client.meta.service_model.service_name,
        "geopackage_rows": 1,
        "overlap_area_m2": overlap_area,
        "projected_area_m2": projected_area,
        "pyogrio_gdal": ".".join(str(value) for value in pyogrio.__gdal_version__),
        "pyproj": pyproj.__version__,
        "rioxarray": rioxarray.__version__,
        "shapely": shapely.__version__,
        "stac_catalog_id": stac_client.id,
        "stac_client": pystac_client.__version__,
        "xarray": xarray.__version__,
    }


def verify(profile: str) -> dict[str, Any]:
    _verify_python_pin()
    versions = _verify_versions(profile)
    checks: dict[str, Any] = {
        "console_entry_points": _verify_console_entry_points(),
        "runtime": _verify_runtime_functions(),
    }
    if profile == "geo-research":
        checks["geo_research"] = _verify_geo_functions()
    return {
        "checks": checks,
        "packages": versions,
        "profile": profile,
        "python": platform.python_version(),
        "status": "PASS",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=PROFILES, default="runtime")
    args = parser.parse_args(argv)
    try:
        result = verify(args.profile)
    except Exception as exc:  # pragma: no cover - exercised by operator failures
        result = {
            "error": str(exc),
            "error_type": type(exc).__name__,
            "profile": args.profile,
            "python": platform.python_version(),
            "status": "FAIL",
        }
        print(json.dumps(result, indent=2, sort_keys=True))
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
