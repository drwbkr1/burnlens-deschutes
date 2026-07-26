"""Build and validate the immutable Phase Four Ward Creek run package."""

from __future__ import annotations

from hashlib import sha256
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
from tempfile import TemporaryDirectory
from typing import Any
import zipfile


PACKAGE_VERSION = "burnlens-ward-creek-rbr-run-v0.1.0"
PACKAGE_ID = "BURNLENS-WARD-CREEK-RBR-RUN-2026-001"
ARCHIVE_NAME = f"{PACKAGE_ID}.zip"
RECEIPT_NAME = f"{PACKAGE_ID}-RECEIPT.json"
SOFTWARE_VERSION = "0.53.0"
RUN_ID_PATTERN = re.compile(
    r"^BL-[0-9]{4}-[0-9]{2}-[0-9]{2}-p4o1-t01-u07-package-r[0-9]{3}$"
)
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")
FIXED_ZIP_DATETIME = (2026, 1, 1, 0, 0, 0)
RECORDS = (
    (
        Path(
            "records/phase-four/contracts/"
            "PHASE-FOUR-INTEGRATION-CONTRACT-2026-001.json"
        ),
        19991,
        "a50966b3f9d082bc5700c001e3f3d3f0dbc372ad775d3e95ddcec8261ad631ec",
        "u01-contract",
    ),
    (
        Path(
            "records/phase-four/analyses/"
            "PHASE-FOUR-ANALYSIS-RECORD-2026-001.json"
        ),
        7100,
        "0b242293b63b502ea66cf35393a50eb7c81bcbea22550c677c074023f0bea94c",
        "u02-analysis",
    ),
    (
        Path(
            "records/phase-four/geospatial/"
            "PHASE-FOUR-GEOSPATIAL-RECORD-2026-001.json"
        ),
        9119,
        "002860f20df5a2441e71e4b5b27dffdc238c0269a67493900d847e9af9b2e5c9",
        "u03-geospatial",
    ),
    (
        Path(
            "records/phase-four/sources/"
            "PHASE-FOUR-CONTEXT-SOURCE-GATE-2026-001.json"
        ),
        25265,
        "12c273f24565d4899517d64408654128c62a0b8ba9e8f58d3dd898dacaef7a28",
        "u04-source-gate",
    ),
    (
        Path(
            "records/phase-four/intake/"
            "P4O1-T01-U04-context-intake.json"
        ),
        17290,
        "3cc26f5be2fcb811dfe46a95dbdd9daf828457b7b10d6918a307b30450abfdcd",
        "u04-intake",
    ),
    (
        Path(
            "records/phase-four/context/"
            "PHASE-FOUR-CONTEXT-CUSTODY-RECORD-2026-001.json"
        ),
        7449,
        "1ced1aa1ddf950f4bc70f4217d2d6a5139df82a7bae9a65aa8d88928d65f0547",
        "u04-context",
    ),
    (
        Path(
            "records/phase-four/overlays/"
            "PHASE-FOUR-OVERLAY-RECORD-2026-001.json"
        ),
        8555,
        "48556442dd519fe7300f8793b47778ac628fc8c16fbb61bda85cde57cf0bbd59",
        "u05-overlay",
    ),
    (
        Path(
            "records/phase-four/interfaces/"
            "PHASE-FOUR-INTERFACE-RECORD-2026-001.json"
        ),
        9809,
        "84ecf5553a91e1cf4f2e81899a80dd5c5e64b4972199c650ac13b4e472a40bda",
        "u06-interface",
    ),
)
RUN_RECORDS = (
    (
        Path(
            "records/phase-four/analyses/"
            "PHASE-FOUR-ANALYSIS-RECORD-2026-001.json"
        ),
        "u02-analysis",
    ),
    (
        Path(
            "records/phase-four/geospatial/"
            "PHASE-FOUR-GEOSPATIAL-RECORD-2026-001.json"
        ),
        "u03-geospatial",
    ),
    (
        Path(
            "records/phase-four/context/"
            "PHASE-FOUR-CONTEXT-CUSTODY-RECORD-2026-001.json"
        ),
        "u04-context",
    ),
    (
        Path(
            "records/phase-four/overlays/"
            "PHASE-FOUR-OVERLAY-RECORD-2026-001.json"
        ),
        "u05-overlay",
    ),
)
INTERFACE_ROOT = Path(
    "samples/runs/phase-four/burnlens-geoint-evidence-interface-v0.1.0"
)
INTERFACE_FILES = (
    (
        "PHASE-FOUR-EVIDENCE-INTERFACE-2026-001.html",
        177666,
        "7a657ad772b34ff42cf4f4024a585b70fb8e7f41bab363cd056fcf8059825fb7",
        "interface/index.html",
    ),
    (
        "PHASE-FOUR-EVIDENCE-INTERFACE-2026-001.json",
        12429,
        "8686766d026d413e0075eb974a0c08ba870c9110b006ba26abe28d505bf6313c",
        "interface/interface-manifest.json",
    ),
)


class PhaseFourPackageError(RuntimeError):
    """The U07 package build or validation gate failed."""


def _sha256_bytes(payload: bytes) -> str:
    return sha256(payload).hexdigest()


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


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PhaseFourPackageError(f"invalid JSON: {path}") from exc
    if not isinstance(value, dict):
        raise PhaseFourPackageError(f"JSON object required: {path}")
    return value


def _validate_exact(
    path: Path, expected_bytes: int, expected_hash: str
) -> bytes:
    if not path.is_file():
        raise PhaseFourPackageError(f"source missing: {path}")
    payload = path.read_bytes()
    if len(payload) != expected_bytes or _sha256_bytes(payload) != expected_hash:
        raise PhaseFourPackageError(f"source drift: {path}")
    return payload


def _receipt(path: str, payload: bytes) -> dict[str, Any]:
    return {
        "path": path,
        "bytes": len(payload),
        "sha256": _sha256_bytes(payload),
    }


def _source_payloads(
    root: Path,
) -> tuple[dict[str, bytes], list[dict[str, Any]]]:
    package: dict[str, bytes] = {}
    sources: list[dict[str, Any]] = []
    for relative, expected_bytes, expected_hash, unit in RECORDS:
        payload = _validate_exact(
            root / relative, expected_bytes, expected_hash
        )
        target = f"evidence/records/{unit}/{relative.name}"
        package[target] = payload
        sources.append(
            {
                **_receipt(relative.as_posix(), payload),
                "package_path": target,
                "tracked": True,
                "role": f"{unit} controlling evidence",
            }
        )
    for record_relative, unit in RUN_RECORDS:
        record = _load_json(root / record_relative)
        inventory = record.get("ignored_run_inventory")
        if not isinstance(inventory, dict):
            raise PhaseFourPackageError(
                f"run inventory missing: {record_relative}"
            )
        base = Path(inventory["path"])
        files = inventory.get("files")
        if not isinstance(files, list) or not files:
            raise PhaseFourPackageError(
                f"run inventory empty: {record_relative}"
            )
        for item in files:
            relative = base / item["path"]
            payload = _validate_exact(
                root / relative, item["bytes"], item["sha256"]
            )
            target = f"evidence/{unit}/run/{item['path']}"
            if target in package:
                raise PhaseFourPackageError(f"duplicate package path: {target}")
            package[target] = payload
            sources.append(
                {
                    **_receipt(relative.as_posix(), payload),
                    "package_path": target,
                    "tracked": False,
                    "role": f"{unit} immutable run artifact",
                }
            )
    for name, expected_bytes, expected_hash, target in INTERFACE_FILES:
        relative = INTERFACE_ROOT / name
        payload = _validate_exact(
            root / relative, expected_bytes, expected_hash
        )
        package[target] = payload
        sources.append(
            {
                **_receipt(relative.as_posix(), payload),
                "package_path": target,
                "tracked": True,
                "role": "u06 accepted repository-owned interface",
            }
        )
    sources.sort(key=lambda item: item["package_path"].casefold())
    return package, sources


def _readme() -> bytes:
    return (
        "# BurnLens Ward Creek RBR run v0.1.0\n\n"
        "This is the immutable extract-and-open Phase Four run package.\n\n"
        "1. Open `interface/index.html` in a modern browser.\n"
        "2. Keep **Accepted RBR** on. Turn **Rejected U-Net** on only to "
        "inspect the rejected diagnostic.\n"
        "3. Use the WCP-001 and WCP-002 focus controls, then read the textual "
        "equivalent and lineage below the map.\n"
        "4. Read `REPORT.md` and `WARNINGS.md` before interpreting any map.\n"
        "5. Run the validator command in `REPLAY.md` to verify every byte and "
        "geospatial product.\n\n"
        "The package is self-contained and performs no external request. "
        "RBR is the accepted analytical output for this bounded demonstration. "
        "The trained U-Net is reproducible and rejected. WCP-002 preserves "
        "visible baseline false-positive-risk evidence.\n"
    ).encode("utf-8")


def _report() -> bytes:
    return (
        "# Ward Creek bounded CV-to-GEOINT report\n\n"
        "## Result\n\n"
        "- WCP-001 accepted RBR: 141.44 ha; 94.19% overlaps the exact "
        "analyst-interpreted MTBS boundary.\n"
        "- WCP-002 accepted RBR: 66.76 ha; 0.00% MTBS overlap; this is "
        "first-class false-positive-risk evidence.\n"
        "- No selected TNM road, selected facility point, or BLM boundary "
        "intersects either accepted RBR footprint.\n\n"
        "## Analytical decision\n\n"
        "RBR remains the accepted method. The one frozen U-Net predicts all "
        "89 selected test cores as burned and scores macro Dice 0.298742 "
        "against RBR 1.0. It remains a valid trained, evaluated, reproducible, "
        "and rejected diagnostic. It is not used for package measurements.\n\n"
        "## Interpretation boundary\n\n"
        "These are bounded prototype observations, not independent ground "
        "truth, natural prevalence, complete-scar accuracy, field validation, "
        "generalization, or operational wildfire information.\n"
    ).encode("utf-8")


def _warnings() -> bytes:
    return (
        "# Warnings and source roles\n\n"
        "- Experimental owner-approved prototype evidence; not independent "
        "ground truth.\n"
        "- Not official, field-validated, endorsed, operational, or suitable "
        "for routing, closure, tactical, property, legal, safety, or emergency "
        "decisions.\n"
        "- MTBS is analyst-interpreted official-program reference context, "
        "not an operational incident perimeter or endorsement.\n"
        "- Selected TNM roads are not access, routing, closure, or safety "
        "authority.\n"
        "- Selected TNM facilities do not establish operation, availability, "
        "capacity, or emergency suitability.\n"
        "- The generalized BLM layer is not a cadastral, survey, access, "
        "ownership, or legal determination.\n"
        "- The rejected U-Net is diagnostic only and did not outperform RBR.\n"
        "- No Phase 3B or follow-on experiment is part of this project.\n"
    ).encode("utf-8")


def _replay() -> bytes:
    return (
        "# Exact replay\n\n"
        "From a BurnLens checkout with the locked geospatial profile:\n\n"
        "```powershell\n"
        "uv run --locked --extra model --extra geo-research "
        "burnlens-validate-phase-four-package "
        "--package-path samples/runs/phase-four/"
        "burnlens-ward-creek-rbr-run-v0.1.0\n"
        "uv run --locked --extra model --extra geo-research "
        "burnlens-validate-phase-four-package "
        "--package-path portfolio/phase-four/"
        "BURNLENS-WARD-CREEK-RBR-RUN-2026-001.zip\n"
        "```\n\n"
        "Both commands must report `PACKAGE_VALIDATION_PASS`. The validator "
        "checks the manifest, checksum roster, safe archive structure, actual "
        "GeoTIFF/GeoPackage/GeoJSON products, interface boundaries, and "
        "accepted-versus-rejected analytical status.\n"
    ).encode("utf-8")


def _generated_payloads(
    *,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
    sources: list[dict[str, Any]],
) -> dict[str, bytes]:
    return {
        "README.md": _readme(),
        "REPORT.md": _report(),
        "WARNINGS.md": _warnings(),
        "REPLAY.md": _replay(),
        "config/MAP-CONFIG.json": _json_bytes(
            {
                "map_config_version": "burnlens-phase-four-map-config-v0.1.0",
                "measurement_crs": "EPSG:32610",
                "web_crs": "EPSG:4326",
                "default_focus": "all",
                "layers": [
                    {
                        "id": "accepted-rbr",
                        "role": "accepted analytical output",
                        "default_visible": True,
                        "default_opacity": 0.78,
                    },
                    {
                        "id": "rejected-unet",
                        "role": "rejected model diagnostic only",
                        "default_visible": False,
                        "default_opacity": 0.60,
                    },
                    {
                        "id": "mtbs",
                        "role": "official-program reference context",
                        "default_visible": True,
                        "default_opacity": 1.0,
                    },
                    {
                        "id": "roads",
                        "role": "selected official context; not routing",
                        "default_visible": True,
                        "default_opacity": 0.72,
                    },
                    {
                        "id": "facilities",
                        "role": "selected official context; not availability",
                        "default_visible": True,
                        "default_opacity": 1.0,
                    },
                    {
                        "id": "blm",
                        "role": "generalized planning context",
                        "default_visible": True,
                        "default_opacity": 0.75,
                    },
                ],
            }
        ),
        "inventory/SOURCE-INVENTORY.json": _json_bytes(
            {
                "inventory_version": "burnlens-phase-four-source-inventory-v0.1.0",
                "generated_at_utc": generated_at_utc,
                "run_id": run_id,
                "git_source_commit": git_source_commit,
                "source_count": len(sources),
                "sources": sources,
            }
        ),
        "status/STATUS.json": _json_bytes(
            {
                "status_version": "burnlens-phase-four-package-status-v0.1.0",
                "package_version": PACKAGE_VERSION,
                "state": "accepted-baseline",
                "accepted_method": "burnlens-baseline-v0.1.0",
                "rejected_diagnostic": "burnlens-unet-binary-v0.1.0",
                "model_accepted": False,
                "model_outperformed_rbr": False,
                "phase_3b_created": False,
                "second_experiment_planned": False,
                "deployment": False,
                "external_requests": False,
            }
        ),
        "replay/REPLAY-CONTRACT.json": _json_bytes(
            {
                "replay_contract_version": "burnlens-phase-four-replay-v0.1.0",
                "package_version": PACKAGE_VERSION,
                "validator": "burnlens-validate-phase-four-package",
                "required_profile": [
                    "model",
                    "geo-research",
                ],
                "expected_result": "PACKAGE_VALIDATION_PASS",
                "directory_and_archive_validation_required": True,
                "fresh_environment_required": True,
            }
        ),
    }


def _checksums(files: dict[str, bytes]) -> bytes:
    return "".join(
        f"{_sha256_bytes(payload)}  {path}\n"
        for path, payload in sorted(
            files.items(), key=lambda item: item[0].casefold()
        )
    ).encode("utf-8")


def _archive(files: dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(
        buffer,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as archive:
        for relative, payload in sorted(
            files.items(), key=lambda item: item[0].casefold()
        ):
            info = zipfile.ZipInfo(
                f"{PACKAGE_VERSION}/{relative}", FIXED_ZIP_DATETIME
            )
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, payload)
    return buffer.getvalue()


def build_package(
    *,
    repository_root: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, Any]:
    root = repository_root.resolve()
    if not RUN_ID_PATTERN.fullmatch(run_id):
        raise PhaseFourPackageError("run ID does not match U07 contract")
    if not COMMIT_PATTERN.fullmatch(git_source_commit):
        raise PhaseFourPackageError("git source commit is invalid")
    files, sources = _source_payloads(root)
    files.update(
        _generated_payloads(
            generated_at_utc=generated_at_utc,
            run_id=run_id,
            git_source_commit=git_source_commit,
            sources=sources,
        )
    )
    files["CHECKSUMS.sha256"] = _checksums(files)
    payload_inventory = [
        _receipt(path, payload)
        for path, payload in sorted(
            files.items(), key=lambda item: item[0].casefold()
        )
    ]
    manifest = {
        "package_manifest_version": "burnlens-phase-four-package-manifest-v0.1.0",
        "package_id": PACKAGE_ID,
        "package_version": PACKAGE_VERSION,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "issue": 570,
        "unit_id": "P4O1-T01-U07",
        "git_source_commit": git_source_commit,
        "software_version_at_execution": SOFTWARE_VERSION,
        "state": "accepted-baseline",
        "route": "baseline-primary-with-rejected-model-diagnostic",
        "accepted_method": "burnlens-baseline-v0.1.0",
        "rejected_diagnostic": "burnlens-unet-binary-v0.1.0",
        "source_count": len(sources),
        "payload_file_count_excluding_manifest": len(payload_inventory),
        "payload_inventory": payload_inventory,
        "entrypoint": "interface/index.html",
        "validation_entrypoint": "burnlens-validate-phase-four-package",
        "warnings": "WARNINGS.md",
        "report": "REPORT.md",
        "map_config": "config/MAP-CONFIG.json",
        "source_inventory": "inventory/SOURCE-INVENTORY.json",
        "checksums": "CHECKSUMS.sha256",
        "boundaries": {
            "model_accepted": False,
            "model_outperformed_rbr": False,
            "context_is_label_truth": False,
            "context_is_model_input": False,
            "phase_3b_created": False,
            "second_experiment_planned": False,
            "external_request": False,
            "deployment": False,
            "public_sharing_change": False,
            "official_operational_field_validated_endorsed_or_emergency_claim": False,
        },
        "disposition": "package-candidate-pending-clean-reproduction",
        "next_dependency": "P4O1-T01-U07 clean environment reproduction",
    }
    files["PACKAGE-MANIFEST.json"] = _json_bytes(manifest)
    archive = _archive(files)
    receipt = {
        "receipt_version": "burnlens-phase-four-package-receipt-v0.1.0",
        "package_id": PACKAGE_ID,
        "package_version": PACKAGE_VERSION,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "git_source_commit": git_source_commit,
        "archive": {
            "path": ARCHIVE_NAME,
            "bytes": len(archive),
            "sha256": _sha256_bytes(archive),
            "member_count": len(files),
            "root": PACKAGE_VERSION,
        },
        "extracted": {
            "file_count": len(files),
            "bytes": sum(len(payload) for payload in files.values()),
            "manifest_sha256": _sha256_bytes(
                files["PACKAGE-MANIFEST.json"]
            ),
            "checksums_sha256": _sha256_bytes(files["CHECKSUMS.sha256"]),
        },
        "state": "package-candidate-pending-clean-reproduction",
    }
    return {
        "files": files,
        "archive": archive,
        "receipt": receipt,
        "receipt_bytes": _json_bytes(receipt),
    }


def _safe_member(name: str) -> bool:
    pure = PurePosixPath(name)
    return (
        not pure.is_absolute()
        and "\\" not in name
        and all(part not in {"", ".", ".."} for part in pure.parts)
        and len(pure.parts) >= 2
        and pure.parts[0] == PACKAGE_VERSION
    )


def _validate_extracted(root: Path) -> dict[str, Any]:
    import geopandas as gpd
    import numpy as np
    import pyogrio
    import rasterio

    manifest = _load_json(root / "PACKAGE-MANIFEST.json")
    if (
        manifest.get("package_version") != PACKAGE_VERSION
        or manifest.get("state") != "accepted-baseline"
        or manifest.get("boundaries", {}).get("model_accepted") is not False
        or manifest.get("boundaries", {}).get("model_outperformed_rbr")
        is not False
    ):
        raise PhaseFourPackageError("package manifest state drift")
    checksum_lines = (root / "CHECKSUMS.sha256").read_text(
        encoding="utf-8"
    ).splitlines()
    expected_checksums = {}
    for line in checksum_lines:
        digest, separator, relative = line.partition("  ")
        if (
            separator != "  "
            or not re.fullmatch(r"[0-9a-f]{64}", digest)
            or relative in expected_checksums
        ):
            raise PhaseFourPackageError("invalid checksum roster")
        expected_checksums[relative] = digest
    for relative, digest in expected_checksums.items():
        path = root / relative
        if not path.is_file() or _sha256_file(path) != digest:
            raise PhaseFourPackageError(f"checksum mismatch: {relative}")
    inventory = manifest.get("payload_inventory")
    if not isinstance(inventory, list):
        raise PhaseFourPackageError("payload inventory missing")
    for item in inventory:
        path = root / item["path"]
        if (
            not path.is_file()
            or path.stat().st_size != item["bytes"]
            or _sha256_file(path) != item["sha256"]
        ):
            raise PhaseFourPackageError(
                f"manifest receipt mismatch: {item['path']}"
            )
    interface = (root / "interface/index.html").read_text(encoding="utf-8")
    lower = interface.lower()
    if (
        'connect-src \'none\'' not in lower
        or re.search(r'(?:src|href)="https?://', lower)
        or "fetch(" in lower
        or "xmlhttprequest" in lower
        or "rejected u-net" not in lower
        or "accepted rbr" not in lower
    ):
        raise PhaseFourPackageError("interface offline/status drift")
    raster_root = root / "evidence/u03-geospatial/run/patches"
    rasters = sorted(raster_root.rglob("*.tif"))
    if len(rasters) != 10:
        raise PhaseFourPackageError("expected ten GeoTIFFs")
    for path in rasters:
        with rasterio.open(path) as dataset:
            array = dataset.read(1)
            if (
                dataset.crs is None
                or dataset.crs.to_string() != "EPSG:32610"
                or dataset.shape != (64, 64)
                or dataset.transform.a != 20.0
                or dataset.transform.e != -20.0
            ):
                raise PhaseFourPackageError(f"GeoTIFF grid drift: {path}")
            valid = array[array != dataset.nodata]
            if not np.isfinite(valid).all():
                raise PhaseFourPackageError(
                    f"GeoTIFF nonfinite values: {path}"
                )
            if "binary" in path.name or "exclusion" in path.name:
                if set(np.unique(valid).tolist()) - {0, 1}:
                    raise PhaseFourPackageError(
                        f"GeoTIFF binary domain drift: {path}"
                    )
    vector_root = root / "evidence/u03-geospatial/run/vectors"
    gpkg = vector_root / "rbr-accepted-polygons.gpkg"
    frame = pyogrio.read_dataframe(gpkg, layer="rbr_accepted")
    if (
        len(frame) != 202
        or frame.crs.to_string() != "EPSG:32610"
        or not bool(frame.geometry.is_valid.all())
    ):
        raise PhaseFourPackageError("GeoPackage drift")
    geojson_paths = [
        vector_root / "rbr-accepted-polygons.geojson",
        root / "evidence/u05-overlay/run/context/roads.geojson",
        root / "evidence/u05-overlay/run/context/facilities.geojson",
        root / "evidence/u05-overlay/run/context/blm-boundary.geojson",
        root
        / "evidence/u05-overlay/run/reference/"
        "mtbs-ward-creek-boundary.geojson",
    ]
    for path in geojson_paths:
        data = gpd.read_file(path)
        if (
            data.crs.to_string() != "EPSG:4326"
            or data.empty
            or not bool(data.geometry.is_valid.all())
        ):
            raise PhaseFourPackageError(f"GeoJSON drift: {path}")
    return {
        "package_version": PACKAGE_VERSION,
        "state": manifest["state"],
        "payload_file_count": len(inventory) + 1,
        "checksum_file_count": len(expected_checksums),
        "geotiff_count": len(rasters),
        "accepted_vector_feature_count": len(frame),
        "geojson_count": len(geojson_paths),
        "interface_offline": True,
        "model_accepted": False,
        "model_outperformed_rbr": False,
        "result": "PACKAGE_VALIDATION_PASS",
    }


def validate_package(package_path: Path) -> dict[str, Any]:
    source = package_path.resolve()
    if source.is_dir():
        return _validate_extracted(source)
    if not source.is_file() or source.suffix.casefold() != ".zip":
        raise PhaseFourPackageError("package path must be a directory or ZIP")
    with zipfile.ZipFile(source) as archive:
        infos = archive.infolist()
        names = [info.filename for info in infos]
        if (
            not infos
            or len(names) != len(set(names))
            or any(not _safe_member(name) for name in names)
            or any(info.flag_bits & 0x1 for info in infos)
            or archive.testzip() is not None
        ):
            raise PhaseFourPackageError("unsafe or corrupt archive")
        with TemporaryDirectory(prefix="burnlens-phase-four-") as temporary:
            destination = Path(temporary)
            archive.extractall(destination)
            return _validate_extracted(destination / PACKAGE_VERSION)


def _require_clean_head(root: Path, git_source_commit: str) -> None:
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if head != git_source_commit:
        raise PhaseFourPackageError("git source commit differs from HEAD")
    status = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    if status:
        raise PhaseFourPackageError("working tree must be clean before U07")


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
            raise PhaseFourPackageError(f"output readback differs: {path}")
    except Exception:
        if created and path.exists():
            path.unlink()
        raise


def run_package(
    *,
    repository_root: Path,
    extracted_directory: Path,
    archive_directory: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, Any]:
    root = repository_root.resolve()
    extracted = extracted_directory.resolve()
    archives = archive_directory.resolve()
    if extracted.exists() and any(extracted.iterdir()):
        raise PhaseFourPackageError(
            f"refusing to overwrite nonempty extracted directory: {extracted}"
        )
    for target in (archives / ARCHIVE_NAME, archives / RECEIPT_NAME):
        if target.exists() or target.is_symlink():
            raise PhaseFourPackageError(f"refusing to overwrite: {target}")
    _require_clean_head(root, git_source_commit)
    build = build_package(
        repository_root=root,
        generated_at_utc=generated_at_utc,
        run_id=run_id,
        git_source_commit=git_source_commit,
    )
    for relative, payload in sorted(
        build["files"].items(), key=lambda item: item[0].casefold()
    ):
        _write_new(extracted / relative, payload)
    _write_new(archives / ARCHIVE_NAME, build["archive"])
    _write_new(archives / RECEIPT_NAME, build["receipt_bytes"])
    return build
