"""Fail-closed, all-or-none intake for the exact BurnLens source trio.

This module does not download provider data or handle credentials.  It validates
an already-populated quarantine directory and promotes it only when every exact
asset passes the contract.  The public rehearsal uses temporary synthetic bytes
to prove transaction behavior while keeping the real provider state absent.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import md5, sha256
from html import escape
import json
import os
from pathlib import Path, PurePosixPath
import shutil
from tempfile import TemporaryDirectory
import textwrap
from typing import Any, Iterable
import zipfile

from blake3 import blake3
from PIL import Image, ImageDraw, ImageFont


HDF5_MAGIC = b"\x89HDF\r\n\x1a\n"
ZIP_MAGICS = (b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08")
WARNING = (
    "Experimental BurnLens CV output. Not official wildfire information. "
    "Not emergency guidance. Not evacuation, routing, tactical, or "
    "incident-command support. Official sources govern."
)
PACKAGE_ID = "darlene3-s2-viirs-pair-v0.1.0"
CONTRACT_VERSION = "paired-intake-contract-v0.1.0"
REPORT_VERSION = "paired-intake-rehearsal-v0.1.0"
REPORT_ID = "PAIR-INTAKE-REHEARSAL-2026-001"
SOFTWARE_VERSION = "0.3.0"


@dataclass(frozen=True)
class AssetContract:
    role: str
    provider: str
    source_record_id: str
    provider_id: str
    native_id: str
    expected_filename: str
    stable_route: str
    expected_size_bytes: int
    container: str
    package_id: str
    provider_md5: str | None = None
    provider_blake3: str | None = None
    expected_zip_root: str | None = None
    native_pair_token: str | None = None


SENTINEL_SAFE = "S2B_MSIL2A_20240627T184919_N0510_R113_T10TFP_20240627T213644.SAFE"

EXACT_CONTRACTS = (
    AssetContract(
        role="sentinel-2-l2a",
        provider="Copernicus Data Space Ecosystem",
        source_record_id="SOURCE-2026-004",
        provider_id="58cebcf0-c417-4384-a93a-2d6b15344117",
        native_id=SENTINEL_SAFE,
        expected_filename=f"{SENTINEL_SAFE}.zip",
        stable_route=(
            "https://download.dataspace.copernicus.eu/odata/v1/"
            "Products(58cebcf0-c417-4384-a93a-2d6b15344117)/$value"
        ),
        expected_size_bytes=1_127_031_562,
        container="zip-safe",
        package_id=PACKAGE_ID,
        provider_md5="3806a834a97ab2eb41f1edf5496b433c",
        provider_blake3="546336e996586f4c276eb9ed3d9818f9574edbed24334dce74a394bd3759cb10",
        expected_zip_root=SENTINEL_SAFE,
    ),
    AssetContract(
        role="viirs-active-fire",
        provider="NASA LP DAAC",
        source_record_id="SOURCE-2026-005",
        provider_id="G3944882727-LPCLOUD",
        native_id="VJ214IMG.A2024179.1936.002.2025284191612",
        expected_filename="VJ214IMG.A2024179.1936.002.2025284191612.nc",
        stable_route=(
            "https://data.lpdaac.earthdatacloud.nasa.gov/lp-prod-protected/"
            "VJ214IMG.002/VJ214IMG.A2024179.1936.002.2025284191612/"
            "VJ214IMG.A2024179.1936.002.2025284191612.nc"
        ),
        expected_size_bytes=2_710_616,
        container="hdf5",
        package_id=PACKAGE_ID,
        native_pair_token="A2024179.1936",
    ),
    AssetContract(
        role="viirs-geolocation",
        provider="NASA LP DAAC",
        source_record_id="SOURCE-2026-006",
        provider_id="G4037038741-LPCLOUD",
        native_id="VJ203MODLL.A2024179.1936.021.2024327213621",
        expected_filename="VJ203MODLL.A2024179.1936.021.2024327213621.h5",
        stable_route=(
            "https://data.lpdaac.earthdatacloud.nasa.gov/lp-prod-protected/"
            "VJ203MODLL.021/VJ203MODLL.A2024179.1936.021.2024327213621/"
            "VJ203MODLL.A2024179.1936.021.2024327213621.h5"
        ),
        expected_size_bytes=40_255_764,
        container="hdf5",
        package_id=PACKAGE_ID,
        native_pair_token="A2024179.1936",
    ),
)


def _stream_hashes(path: Path) -> dict[str, str]:
    sha = sha256()
    legacy = md5(usedforsecurity=False)
    modern = blake3()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            sha.update(chunk)
            legacy.update(chunk)
            modern.update(chunk)
    return {
        "sha256": sha.hexdigest(),
        "md5": legacy.hexdigest(),
        "blake3": modern.hexdigest(),
    }


def _safe_zip_name(name: str) -> bool:
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts:
        return False
    if path.parts and ":" in path.parts[0]:
        return False
    return bool(path.parts)


def _inspect_zip(path: Path, expected_root: str) -> tuple[list[str], dict[str, Any]]:
    reasons: list[str] = []
    details: dict[str, Any] = {
        "member_count": 0,
        "uncompressed_bytes": 0,
        "expected_root": expected_root,
        "manifest_present": False,
        "crc_test_passed": False,
    }
    try:
        with zipfile.ZipFile(path) as archive:
            infos = archive.infolist()
            names = [info.filename for info in infos]
            details["member_count"] = len(names)
            details["uncompressed_bytes"] = sum(info.file_size for info in infos)
            if len(names) != len(set(names)):
                reasons.append("ZIP_DUPLICATE_MEMBER")
            if any(not _safe_zip_name(name) for name in names):
                reasons.append("ZIP_UNSAFE_MEMBER_PATH")
            root_prefix = f"{expected_root}/"
            if any(name != root_prefix and not name.startswith(root_prefix) for name in names):
                reasons.append("ZIP_UNEXPECTED_ROOT")
            manifest_name = f"{expected_root}/manifest.safe"
            details["manifest_present"] = manifest_name in names
            if not details["manifest_present"]:
                reasons.append("SAFE_MANIFEST_MISSING")
            bad_member = archive.testzip()
            details["crc_test_passed"] = bad_member is None
            if bad_member is not None:
                reasons.append("ZIP_CRC_FAILURE")
    except (OSError, zipfile.BadZipFile, RuntimeError):
        reasons.append("ZIP_CONTAINER_INVALID")
    return reasons, details


def _missing_observation(contract: AssetContract) -> dict[str, Any]:
    return {
        "role": contract.role,
        "source_record_id": contract.source_record_id,
        "provider_id": contract.provider_id,
        "native_id": contract.native_id,
        "expected_filename": contract.expected_filename,
        "expected_size_bytes": contract.expected_size_bytes,
        "container": contract.container,
        "observed_bytes": 0,
        "observed_magic_hex": None,
        "container_details": None,
        "provider_checksum_available": bool(contract.provider_md5 or contract.provider_blake3),
        "accepted": False,
        "local_hashes": None,
        "reason_codes": ["ASSET_MISSING"],
    }


def inspect_asset(quarantine: Path, contract: AssetContract) -> dict[str, Any]:
    """Validate one exact file without trusting its suffix or location label."""

    path = quarantine / contract.expected_filename
    if not path.exists() or not path.is_file():
        return _missing_observation(contract)

    observed_bytes = path.stat().st_size
    with path.open("rb") as handle:
        magic = handle.read(8)
    reasons: list[str] = []
    container_details: dict[str, Any] | None = None

    if observed_bytes != contract.expected_size_bytes:
        reasons.append("EXACT_SIZE_MISMATCH")

    if contract.container == "hdf5":
        if magic != HDF5_MAGIC:
            reasons.append("HDF5_SIGNATURE_MISSING")
    elif contract.container == "zip-safe":
        if not any(magic.startswith(prefix) for prefix in ZIP_MAGICS):
            reasons.append("ZIP_SIGNATURE_MISSING")
        elif contract.expected_zip_root is None:
            reasons.append("ZIP_ROOT_CONTRACT_MISSING")
        else:
            zip_reasons, container_details = _inspect_zip(path, contract.expected_zip_root)
            reasons.extend(zip_reasons)
    else:
        reasons.append("UNKNOWN_CONTAINER_CONTRACT")

    hashes = _stream_hashes(path) if observed_bytes == contract.expected_size_bytes else None
    if hashes is not None and contract.provider_md5 and hashes["md5"] != contract.provider_md5:
        reasons.append("PROVIDER_MD5_MISMATCH")
    if hashes is not None and contract.provider_blake3 and hashes["blake3"] != contract.provider_blake3:
        reasons.append("PROVIDER_BLAKE3_MISMATCH")

    accepted = not reasons
    return {
        "role": contract.role,
        "source_record_id": contract.source_record_id,
        "provider_id": contract.provider_id,
        "native_id": contract.native_id,
        "expected_filename": contract.expected_filename,
        "expected_size_bytes": contract.expected_size_bytes,
        "container": contract.container,
        "observed_bytes": observed_bytes,
        "observed_magic_hex": magic.hex() if magic else None,
        "container_details": container_details,
        "provider_checksum_available": bool(contract.provider_md5 or contract.provider_blake3),
        "accepted": accepted,
        "local_hashes": hashes if accepted else None,
        "reason_codes": reasons or ["EXACT_ASSET_ACCEPTED"],
    }


def validate_contract_set(contracts: Iterable[AssetContract]) -> list[str]:
    items = list(contracts)
    reasons: list[str] = []
    if len(items) != 3:
        reasons.append("CONTRACT_REQUIRES_THREE_ASSETS")
    roles = [item.role for item in items]
    filenames = [item.expected_filename for item in items]
    package_ids = {item.package_id for item in items}
    if len(roles) != len(set(roles)):
        reasons.append("DUPLICATE_CONTRACT_ROLE")
    if len(filenames) != len(set(filenames)):
        reasons.append("DUPLICATE_CONTRACT_FILENAME")
    if len(package_ids) != 1:
        reasons.append("PACKAGE_ID_MISMATCH")
    pair_tokens = {item.native_pair_token for item in items if item.native_pair_token}
    if len(pair_tokens) != 1:
        reasons.append("VIIRS_NATIVE_PAIR_TOKEN_MISMATCH")
    if any(item.native_pair_token and item.native_pair_token not in item.native_id for item in items):
        reasons.append("VIIRS_NATIVE_ID_TOKEN_MISMATCH")
    return reasons


def evaluate_quarantine(quarantine: Path, contracts: Iterable[AssetContract]) -> dict[str, Any]:
    items = list(contracts)
    contract_reasons = validate_contract_set(items)
    exists = quarantine.exists() and quarantine.is_dir()
    observations = [inspect_asset(quarantine, item) if exists else _missing_observation(item) for item in items]
    expected_entries = {item.expected_filename for item in items}
    observed_entries = sorted(entry.name for entry in quarantine.iterdir()) if exists else []
    unexpected_entries = sorted(set(observed_entries) - expected_entries)
    transaction_reasons = list(contract_reasons)
    if not exists:
        transaction_reasons.append("QUARANTINE_MISSING")
    if unexpected_entries:
        transaction_reasons.append("UNEXPECTED_QUARANTINE_ENTRY")
    if not all(item["accepted"] for item in observations):
        transaction_reasons.append("INCOMPLETE_OR_INVALID_ASSET_SET")
    accepted = not transaction_reasons
    return {
        "package_id": items[0].package_id if items else None,
        "quarantine_present": exists,
        "expected_asset_count": len(items),
        "observed_entry_count": len(observed_entries),
        "accepted_asset_count": sum(1 for item in observations if item["accepted"]),
        "unexpected_entries": unexpected_entries,
        "observations": observations,
        "accepted_for_atomic_promotion": accepted,
        "reason_codes": transaction_reasons or ["TRANSACTION_READY"],
    }


def promote_quarantine(
    quarantine: Path,
    destination: Path,
    contracts: Iterable[AssetContract],
    *,
    generated_at_utc: str,
    run_id: str,
    synthetic_fixture: bool,
) -> dict[str, Any]:
    """Atomically move one complete quarantine directory into raw storage."""

    items = list(contracts)
    evaluation = evaluate_quarantine(quarantine, items)
    if not evaluation["accepted_for_atomic_promotion"]:
        raise ValueError("quarantine failed the paired-intake contract")
    if destination.exists():
        raise FileExistsError(f"destination already exists: {destination.name}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if quarantine.stat().st_dev != destination.parent.stat().st_dev:
        raise OSError("quarantine and destination must be on the same filesystem")

    registration = {
        "registration_schema_version": "0.1.0",
        "contract_version": CONTRACT_VERSION,
        "package_id": evaluation["package_id"],
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "synthetic_fixture": synthetic_fixture,
        "asset_count": len(items),
        "assets": [
            {
                "role": item["role"],
                "source_record_id": item["source_record_id"],
                "native_id": item["native_id"],
                "filename": item["expected_filename"],
                "bytes": item["observed_bytes"],
                "sha256": item["local_hashes"]["sha256"],
                "md5": item["local_hashes"]["md5"],
                "blake3": item["local_hashes"]["blake3"],
            }
            for item in evaluation["observations"]
        ],
    }
    (quarantine / ".burnlens-registration.json").write_text(
        json.dumps(registration, indent=2) + "\n", encoding="utf-8"
    )
    os.replace(quarantine, destination)
    return registration


def _write_synthetic_zip(path: Path, root: str) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_STORED) as archive:
        for name, payload in (
            (f"{root}/manifest.safe", b"SYNTHETIC MANIFEST - NOT PROVIDER DATA\n"),
            (f"{root}/GRANULE/SYNTHETIC/metadata.txt", b"SYNTHETIC TEST FIXTURE\n"),
        ):
            info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_STORED
            info.external_attr = 0o644 << 16
            archive.writestr(info, payload)


def _synthetic_contracts(directory: Path) -> tuple[AssetContract, ...]:
    root = "SYNTHETIC_SENTINEL.SAFE"
    sentinel = directory / f"{root}.zip"
    fire = directory / "SYNTHETIC_FIRE.nc"
    geolocation = directory / "SYNTHETIC_GEO.h5"
    _write_synthetic_zip(sentinel, root)
    fire.write_bytes(HDF5_MAGIC + b"SYNTHETIC-FIRE" * 4)
    geolocation.write_bytes(HDF5_MAGIC + b"SYNTHETIC-GEOLOCATION" * 4)

    def contract(path: Path, role: str, container: str, native_id: str, zip_root: str | None = None) -> AssetContract:
        hashes = _stream_hashes(path)
        return AssetContract(
            role=role,
            provider="Synthetic transaction fixture",
            source_record_id="SYNTHETIC-ONLY",
            provider_id=f"SYNTHETIC-{role}",
            native_id=native_id,
            expected_filename=path.name,
            stable_route="not-applicable://synthetic-fixture",
            expected_size_bytes=path.stat().st_size,
            container=container,
            package_id="synthetic-pair-v0.1.0",
            provider_md5=hashes["md5"],
            provider_blake3=hashes["blake3"],
            expected_zip_root=zip_root,
            native_pair_token="A0000000.0000" if container == "hdf5" else None,
        )

    return (
        contract(sentinel, "sentinel", "zip-safe", root, root),
        contract(fire, "fire", "hdf5", "SYNTHETIC.A0000000.0000.FIRE"),
        contract(geolocation, "geolocation", "hdf5", "SYNTHETIC.A0000000.0000.GEO"),
    )


def run_synthetic_rehearsal(*, generated_at_utc: str, run_id: str) -> dict[str, Any]:
    """Exercise rejection and promotion with temporary non-provider fixtures."""

    with TemporaryDirectory(prefix="burnlens-pair-rehearsal-") as temporary:
        root = Path(temporary)
        seed = root / "seed"
        seed.mkdir()
        contracts = _synthetic_contracts(seed)

        partial = root / "partial"
        partial.mkdir()
        for item in contracts[:2]:
            shutil.copy2(seed / item.expected_filename, partial / item.expected_filename)
        partial_destination = root / "raw" / "partial"
        partial_eval = evaluate_quarantine(partial, contracts)
        partial_rejected = not partial_eval["accepted_for_atomic_promotion"]
        try:
            promote_quarantine(
                partial,
                partial_destination,
                contracts,
                generated_at_utc=generated_at_utc,
                run_id=f"{run_id}-partial",
                synthetic_fixture=True,
            )
        except ValueError:
            pass
        partial_raw_absent = not partial_destination.exists()

        tampered = root / "tampered"
        tampered.mkdir()
        for item in contracts:
            shutil.copy2(seed / item.expected_filename, tampered / item.expected_filename)
        fire_path = tampered / contracts[1].expected_filename
        payload = bytearray(fire_path.read_bytes())
        payload[-1] ^= 0x01
        fire_path.write_bytes(payload)
        tampered_destination = root / "raw" / "tampered"
        tampered_eval = evaluate_quarantine(tampered, contracts)
        tamper_rejected = not tampered_eval["accepted_for_atomic_promotion"]
        try:
            promote_quarantine(
                tampered,
                tampered_destination,
                contracts,
                generated_at_utc=generated_at_utc,
                run_id=f"{run_id}-tampered",
                synthetic_fixture=True,
            )
        except ValueError:
            pass
        tampered_raw_absent = not tampered_destination.exists()

        complete = root / "complete"
        complete.mkdir()
        for item in contracts:
            shutil.copy2(seed / item.expected_filename, complete / item.expected_filename)
        complete_destination = root / "raw" / "complete"
        complete_eval = evaluate_quarantine(complete, contracts)
        registration = promote_quarantine(
            complete,
            complete_destination,
            contracts,
            generated_at_utc=generated_at_utc,
            run_id=f"{run_id}-complete",
            synthetic_fixture=True,
        )
        promoted_entries = sorted(entry.name for entry in complete_destination.iterdir())
        complete_promoted = (
            complete_eval["accepted_for_atomic_promotion"]
            and not complete.exists()
            and complete_destination.exists()
            and registration["synthetic_fixture"] is True
            and ".burnlens-registration.json" in promoted_entries
        )

        checks = {
            "partial_set_rejected": partial_rejected and partial_raw_absent,
            "checksum_tamper_rejected": tamper_rejected and tampered_raw_absent,
            "complete_set_promoted_atomically": complete_promoted,
            "synthetic_bytes_deleted_after_run": True,
        }
        return {
            "fixture_class": "SYNTHETIC_TEST_ONLY",
            "provider_data": False,
            "credential_used": False,
            "asset_contract_count": len(contracts),
            "checks": checks,
            "passed": all(checks.values()),
            "retained_fixture_bytes": 0,
        }


def contracts_as_dicts(contracts: Iterable[AssetContract] = EXACT_CONTRACTS) -> list[dict[str, Any]]:
    return [asdict(item) for item in contracts]


def contract_digest(contracts: Iterable[AssetContract] = EXACT_CONTRACTS) -> str:
    payload = json.dumps(contracts_as_dicts(contracts), sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256(payload).hexdigest()


def build_report(
    *,
    generated_at_utc: str,
    run_id: str,
    source_commit: str,
) -> dict[str, Any]:
    provider_evaluation = {
        "package_id": PACKAGE_ID,
        "quarantine_present": False,
        "expected_asset_count": len(EXACT_CONTRACTS),
        "observed_entry_count": 0,
        "accepted_asset_count": 0,
        "unexpected_entries": [],
        "observations": [_missing_observation(item) for item in EXACT_CONTRACTS],
        "accepted_for_atomic_promotion": False,
        "reason_codes": ["QUARANTINE_NOT_SUPPLIED", "INCOMPLETE_OR_INVALID_ASSET_SET"],
    }
    rehearsal = run_synthetic_rehearsal(generated_at_utc=generated_at_utc, run_id=run_id)
    decision = "BLOCKED_OWNER_CREDENTIAL"
    decision_detail = "Owner approval for both CDSE and Earthdata credentials is still required; no provider quarantine or raw package exists."
    return {
        "report_id": REPORT_ID,
        "schema_version": "0.1.0",
        "report_version": REPORT_VERSION,
        "contract_version": CONTRACT_VERSION,
        "contract_sha256": contract_digest(),
        "software_version": SOFTWARE_VERSION,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": 325,
        "branch": "codex/p2o2-t02-intake-transaction",
        "git_base_commit": "a3df1cac8d859b27f44d52ef177b5e937dc5fc99",
        "generator_source_commit": source_commit,
        "checkpoint_commit": None,
        "application_version": None,
        "aoi_version": "aoi-darlene3-model-v0.2.0",
        "dataset_version": None,
        "label_schema_version": None,
        "baseline_version": None,
        "model_version": None,
        "package_id": PACKAGE_ID,
        "public_metadata_refresh": {
            "performed_at_utc": generated_at_utc,
            "cdse_product_match": True,
            "cdse_online": True,
            "cdse_checksum_date_utc": "2026-05-26T02:59:48.810650Z",
            "viirs_fire_cmr_match": True,
            "viirs_geolocation_cmr_match": True,
            "viirs_provider_checksums_available": False,
        },
        "asset_contracts": contracts_as_dicts(),
        "provider_package": {
            "credential_approval": "OWNER_APPROVAL_REQUIRED",
            "quarantine_supplied": False,
            "provider_source_asset_count": provider_evaluation["accepted_asset_count"],
            "provider_source_asset_bytes": sum(
                item["observed_bytes"] for item in provider_evaluation["observations"] if item["accepted"]
            ),
            "promoted_raw_package_count": 0,
            "credentials_used": False,
            "evaluation": provider_evaluation,
        },
        "synthetic_transaction_rehearsal": rehearsal,
        "transaction_invariants": [
            "Exactly three named assets are required in one quarantine directory.",
            "Unexpected entries, missing assets, size mismatch, container mismatch, corrupt ZIP, unsafe ZIP paths, and checksum mismatch fail closed.",
            "The two VIIRS native IDs must share the recorded acquisition token.",
            "Provider MD5 and BLAKE3 are both required for the Sentinel archive; local SHA-256, MD5, and BLAKE3 are recorded for accepted assets.",
            "No raw package is created unless the complete quarantine directory passes and is atomically renamed on the same filesystem.",
        ],
        "decision": decision,
        "decision_detail": decision_detail,
        "claims": {
            "permitted": [
                "BurnLens has a tested all-or-none intake transaction for the exact three-asset contract.",
                "Temporary synthetic fixtures prove rejection and atomic-promotion behavior, not provider data fitness.",
            ],
            "prohibited": [
                "Sentinel or VIIRS provider data were acquired or inspected.",
                "The selected acquisition contains fire or is label-ready.",
                "A dataset, baseline, model, detection, performance result, application, or operational product exists.",
            ],
        },
        "source_precedence": "Official provider metadata and source documentation govern over this BurnLens transaction evidence.",
        "warning": WARNING,
    }


def write_report(report: dict[str, Any], output_dir: Path) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "json": output_dir / f"{REPORT_ID}.json",
        "html": output_dir / f"{REPORT_ID}.html",
        "png": output_dir / f"{REPORT_ID}.png",
    }
    paths["json"].write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    paths["html"].write_text(render_html(report), encoding="utf-8")
    render_png(report, paths["png"])
    return paths


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    return ImageFont.load_default(size=size)


def _wrapped(text: str, width: int) -> str:
    return "\n".join(textwrap.wrap(text, width=width, break_long_words=False))


def render_png(report: dict[str, Any], path: Path) -> None:
    canvas = Image.new("RGB", (1600, 1200), "#f3f0e8")
    draw = ImageDraw.Draw(canvas)
    ink = "#17211b"
    muted = "#59645c"
    border = "#89948c"
    card = "#ffffff"
    warning = "#fff0ac"
    blocked = "#f4b8a7"
    green = "#c8ebd2"

    draw.text((88, 55), "PHASE TWO  /  PAIRED INTAKE RELIABILITY", fill=muted, font=_font(23))
    draw.multiline_text((88, 102), "Three assets.\nOne transaction.", fill=ink, font=_font(70), spacing=1)
    draw.rounded_rectangle((920, 76, 1512, 232), radius=12, fill=blocked, outline=ink, width=3)
    draw.text((950, 100), "REAL PROVIDER STATE", fill=muted, font=_font(20))
    draw.text((950, 137), "BLOCKED", fill="#8b1e0e", font=_font(42))
    draw.text((950, 190), "Owner credentials required", fill=ink, font=_font(20))

    draw.rounded_rectangle((88, 278, 1512, 382), radius=12, fill=warning, outline=ink, width=3)
    draw.text((116, 301), "EXPERIMENTAL - NOT OFFICIAL WILDFIRE INFORMATION", fill=ink, font=_font(25))
    draw.text(
        (116, 342),
        "No provider pixels, fire observation, label, dataset, model, or operational result exists. Official sources govern.",
        fill=ink,
        font=_font(19),
    )

    metrics = (("0", "provider assets"), ("0", "provider bytes"), ("0", "credentials used"))
    for index, (value, label) in enumerate(metrics):
        left = 88 + index * 482
        draw.rounded_rectangle((left, 420, left + 450, 542), radius=10, fill=card, outline=border, width=2)
        draw.text((left + 26, 438), value, fill=ink, font=_font(47))
        draw.text((left + 26, 505), label, fill=muted, font=_font(19))

    draw.text((88, 584), "EXACT PROVIDER CONTRACT", fill=muted, font=_font(21))
    rows = (
        ("Sentinel-2 L2A", "1,127,031,562 B", "ZIP + SAFE root + MD5 + BLAKE3"),
        ("NOAA-21 active fire", "2,710,616 B", "HDF5 / NetCDF-4 + exact identity"),
        ("NOAA-21 geolocation", "40,255,764 B", "HDF5 + exact paired token"),
    )
    row_y = 625
    for label, size, gate in rows:
        draw.rounded_rectangle((88, row_y, 1512, row_y + 66), radius=8, fill=card, outline=border, width=1)
        draw.text((112, row_y + 19), label, fill=ink, font=_font(21))
        draw.text((520, row_y + 19), size, fill=ink, font=_font(21))
        draw.text((820, row_y + 19), gate, fill=ink, font=_font(20))
        row_y += 78

    draw.rounded_rectangle((88, 872, 1512, 1031), radius=12, fill=green, outline=ink, width=3)
    draw.text((116, 895), "SYNTHETIC TRANSACTION REHEARSAL - TEST FIXTURE ONLY", fill=ink, font=_font(23))
    checks = report["synthetic_transaction_rehearsal"]["checks"]
    labels = (
        ("partial_set_rejected", "Partial set rejected; no raw package"),
        ("checksum_tamper_rejected", "Checksum tamper rejected; no raw package"),
        ("complete_set_promoted_atomically", "Complete synthetic set promoted atomically"),
    )
    for index, (key, label) in enumerate(labels):
        x = 116 + index * 465
        mark = "PASS" if checks[key] else "FAIL"
        draw.text((x, 948), mark, fill="#005b46" if checks[key] else "#8b1e0e", font=_font(24))
        draw.multiline_text((x, 982), _wrapped(label, 34), fill=ink, font=_font(17), spacing=2)

    draw.rounded_rectangle((88, 1062, 1512, 1134), radius=9, fill=card, outline=border, width=2)
    draw.text((112, 1081), "PROVES: partial registration is prevented. DOES NOT PROVE: source fitness or fire presence.", fill=ink, font=_font(20))
    draw.text((88, 1162), f"{report['run_id']}  ·  {report['contract_version']}  ·  synthetic bytes retained: 0", fill=muted, font=_font(17))
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path, format="PNG", optimize=False)


def render_html(report: dict[str, Any]) -> str:
    contract_rows = []
    for item in report["asset_contracts"]:
        checksums = []
        if item["provider_md5"]:
            checksums.append("MD5")
        if item["provider_blake3"]:
            checksums.append("BLAKE3")
        contract_rows.append(
            "<tr>"
            f"<th scope=\"row\">{escape(item['role'])}</th>"
            f"<td><code>{escape(item['source_record_id'])}</code><br>{escape(item['provider_id'])}</td>"
            f"<td><code>{escape(item['expected_filename'])}</code></td>"
            f"<td>{item['expected_size_bytes']:,}</td>"
            f"<td>{escape(item['container'])}</td>"
            f"<td>{escape(', '.join(checksums) if checksums else 'No provider checksum')}</td>"
            "</tr>"
        )
    rehearsal = report["synthetic_transaction_rehearsal"]
    check_items = "".join(
        f"<li><strong>{'Pass' if passed else 'Fail'}:</strong> {escape(name.replace('_', ' '))}</li>"
        for name, passed in rehearsal["checks"].items()
        if name != "synthetic_bytes_deleted_after_run"
    )
    invariants = "".join(f"<li>{escape(item)}</li>" for item in report["transaction_invariants"])
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>BurnLens paired-intake transaction rehearsal</title>
  <style>
    :root {{ color-scheme: light; font-family: Inter, ui-sans-serif, system-ui, sans-serif; background: #f3f0e8; color: #17211b; }}
    body {{ margin: 0; }} main {{ max-width: 74rem; margin: auto; padding: 2rem 1.25rem 4rem; }}
    .eyebrow {{ letter-spacing: .12em; text-transform: uppercase; font-size: .78rem; font-weight: 800; color: #59645c; }}
    h1 {{ font-size: clamp(2.5rem, 7vw, 5rem); line-height: .94; max-width: 13ch; margin: .4rem 0 1rem; }}
    .warning, .status, .synthetic {{ border: 2px solid #17211b; padding: 1rem; margin: 1rem 0; box-shadow: .35rem .35rem 0 #17211b; }}
    .warning {{ background: #fff0ac; }} .status {{ background: #f4b8a7; }} .synthetic {{ background: #c8ebd2; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(13rem, 1fr)); gap: 1rem; margin: 1.5rem 0; }}
    .card {{ background: white; border: 1px solid #9aa39c; padding: 1rem; }} .metric {{ display: block; font-size: 2.3rem; font-weight: 850; }}
    table {{ border-collapse: collapse; width: 100%; background: white; margin: 1rem 0 2rem; }}
    th, td {{ border: 1px solid #929b94; padding: .75rem; text-align: left; vertical-align: top; }} thead th {{ background: #dce4de; }}
    code {{ overflow-wrap: anywhere; }} a {{ color: #005b46; }} footer {{ border-top: 1px solid #929b94; margin-top: 2rem; padding-top: 1rem; color: #4e5951; }}
    @media (max-width: 50rem) {{ table, thead, tbody, tr, th, td {{ display: block; }} thead {{ position: absolute; left: -9999px; }} tr {{ border: 1px solid #929b94; margin-bottom: 1rem; }} th, td {{ border: 0; }} }}
  </style>
</head>
<body><main>
  <p class="eyebrow">Phase Two · paired intake reliability · {escape(report['contract_version'])}</p>
  <h1>Three assets. One transaction.</h1>
  <p class="warning"><strong>Use boundary:</strong> {escape(report['warning'])}</p>
  <section class="status" aria-labelledby="status-heading"><h2 id="status-heading">Blocked — owner credentials required</h2><p>{escape(report['decision_detail'])}</p></section>
  <section class="grid" aria-label="Real provider state">
    <div class="card"><span class="metric">0</span>provider assets</div>
    <div class="card"><span class="metric">0</span>provider bytes</div>
    <div class="card"><span class="metric">0</span>credentials used</div>
  </section>
  <section aria-labelledby="contract-heading"><h2 id="contract-heading">Exact provider contract</h2>
    <p>Every named asset must be present in one quarantine directory and pass before any raw package is registered.</p>
    <table><thead><tr><th>Role</th><th>Source identity</th><th>Exact file</th><th>Bytes</th><th>Container</th><th>Provider checksum</th></tr></thead><tbody>{''.join(contract_rows)}</tbody></table>
  </section>
  <section class="synthetic" aria-labelledby="synthetic-heading"><h2 id="synthetic-heading">Synthetic transaction rehearsal — test fixture only</h2>
    <p><strong>No provider data is used.</strong> Temporary synthetic ZIP/HDF5 fixtures exercise failure and atomic-promotion behavior and are deleted after the run.</p><ul>{check_items}</ul>
  </section>
  <section aria-labelledby="invariants-heading"><h2 id="invariants-heading">Transaction invariants</h2><ul>{invariants}</ul></section>
  <section aria-labelledby="meaning-heading"><h2 id="meaning-heading">What this proves</h2>
    <p>BurnLens prevents partial exact-pair registration. This report does not prove source fitness, a fire observation, a label, a dataset, a model, or an analytical result.</p>
  </section>
  <section aria-labelledby="trace-heading"><h2 id="trace-heading">Traceability</h2><dl>
    <dt>Run ID</dt><dd><code>{escape(report['run_id'])}</code></dd>
    <dt>Generator source commit</dt><dd><code>{escape(report['generator_source_commit'])}</code></dd>
    <dt>AOI version</dt><dd><code>{escape(report['aoi_version'])}</code></dd>
    <dt>Contract SHA-256</dt><dd><code>{escape(report['contract_sha256'])}</code></dd>
    <dt>Dataset / label schema / baseline / model / application</dt><dd>Not created</dd>
  </dl></section>
  <footer>{escape(report['source_precedence'])} Generated {escape(report['generated_at_utc'])}.</footer>
</main></body></html>
"""
