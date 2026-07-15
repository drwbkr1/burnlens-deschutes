"""Exact, fail-closed contract and acquisition for the BurnLens optical pair.

Only the two owner-authorized Copernicus Sentinel-2 products named here may
enter the package. Credentials arrive through short-lived environment values
created by the Windows DPAPI wrapper and are removed immediately. Provider
bytes remain in ignored local storage.
"""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import re
from typing import Any, Callable, Iterable
from urllib.request import Request, urlopen

from .paired_intake import (
    AssetContract,
    evaluate_quarantine,
    promote_quarantine,
    validate_asset_contracts,
    verify_registered_package,
)
from .provider_acquisition import (
    AcquisitionError,
    USER_AGENT,
    _open_json,
    build_cdse_opener,
    request_cdse_access_token,
    stream_asset,
)


SOFTWARE_VERSION = "0.7.0"
PACKAGE_ID = "darlene3-s2-optical-pair-v0.1.0"
CONTRACT_VERSION = "optical-pair-intake-contract-v0.1.0"
TERMS_REVIEW_ID = "TERMS-2026-004"
SOURCE_OBSERVED_AT_UTC = "2026-07-15T16:00:59Z"

PRE_SAFE = "S2A_MSIL2A_20240625T185941_N0510_R013_T10TFP_20240626T012349.SAFE"
POST_SAFE = "S2A_MSIL2A_20240705T185921_N0510_R013_T10TFP_20240706T015448.SAFE"


OPTICAL_CONTRACTS = (
    AssetContract(
        role="sentinel-2-l2a-pre",
        provider="Copernicus Data Space Ecosystem",
        source_record_id="SOURCE-2026-009",
        provider_id="0303a812-1242-4a09-ae9d-cf905049ca0f",
        native_id=PRE_SAFE,
        expected_filename=f"{PRE_SAFE}.zip",
        stable_route=(
            "https://download.dataspace.copernicus.eu/odata/v1/"
            "Products(0303a812-1242-4a09-ae9d-cf905049ca0f)/$value"
        ),
        expected_size_bytes=1_126_185_170,
        container="zip-safe",
        package_id=PACKAGE_ID,
        provider_md5="50e66c4667d8c8f012532cf06ae3cde3",
        provider_blake3="7ecba67455786570b2f836e7f2752d2b917bf0ee200831c9ac92de0e694a86a9",
        expected_zip_root=PRE_SAFE,
    ),
    AssetContract(
        role="sentinel-2-l2a-post",
        provider="Copernicus Data Space Ecosystem",
        source_record_id="SOURCE-2026-010",
        provider_id="71429c5a-60f9-4c28-9982-752f8ab1c9fd",
        native_id=POST_SAFE,
        expected_filename=f"{POST_SAFE}.zip",
        stable_route=(
            "https://download.dataspace.copernicus.eu/odata/v1/"
            "Products(71429c5a-60f9-4c28-9982-752f8ab1c9fd)/$value"
        ),
        expected_size_bytes=1_128_620_461,
        container="zip-safe",
        package_id=PACKAGE_ID,
        provider_md5="329397ed46a25a78d7c4ece8b10e0df0",
        provider_blake3="35c8e710d47e8c1a5a3ef7c2751537f519ff77574db583801450bd3b4d270ee0",
        expected_zip_root=POST_SAFE,
    ),
)


EXPECTED_METADATA = {
    "sentinel-2-l2a-pre": {
        "acquisition_utc": "2024-06-25T18:59:41.024000Z",
        "platform_serial_identifier": "A",
        "tile_id": "10TFP",
        "relative_orbit_number": 13,
        "processor_version": "05.10",
        "product_type": "S2MSI2A",
        "cloud_cover_percent": 0.775318,
    },
    "sentinel-2-l2a-post": {
        "acquisition_utc": "2024-07-05T18:59:21.024000Z",
        "platform_serial_identifier": "A",
        "tile_id": "10TFP",
        "relative_orbit_number": 13,
        "processor_version": "05.10",
        "product_type": "S2MSI2A",
        "cloud_cover_percent": 0.008776,
    },
}


_PRODUCT_PATTERN = re.compile(
    r"^(?P<platform>S2[ABCD])_MSIL2A_\d{8}T\d{6}_"
    r"N(?P<baseline>\d{4})_R(?P<orbit>\d{3})_T(?P<tile>[0-9A-Z]{5})_"
    r"\d{8}T\d{6}\.SAFE$"
)


@dataclass(repr=False)
class CdseCredentials:
    """In-memory CDSE credential pair with a deliberately redacted repr."""

    username: str
    password: str

    def __repr__(self) -> str:
        return "CdseCredentials(<redacted>)"

    @classmethod
    def from_environment(cls) -> "CdseCredentials":
        names = ("BURNLENS_CDSE_USERNAME", "BURNLENS_CDSE_PASSWORD")
        values = {name: os.environ.pop(name, None) for name in names}
        missing = [name for name, value in values.items() if not value]
        if missing:
            values.clear()
            raise AcquisitionError("CREDENTIAL_ENV_MISSING", detail=",".join(missing))
        return cls(
            username=values["BURNLENS_CDSE_USERNAME"] or "",
            password=values["BURNLENS_CDSE_PASSWORD"] or "",
        )


def validate_optical_contracts(contracts: Iterable[AssetContract]) -> list[str]:
    """Validate the exact same-platform, same-tile, same-orbit pair contract."""

    items = list(contracts)
    reasons = validate_asset_contracts(items)
    if len(items) != 2:
        reasons.append("CONTRACT_REQUIRES_TWO_ASSETS")
        return reasons
    if {item.role for item in items} != {
        "sentinel-2-l2a-pre",
        "sentinel-2-l2a-post",
    }:
        reasons.append("OPTICAL_PAIR_ROLE_SET_MISMATCH")
    parsed = [_PRODUCT_PATTERN.fullmatch(item.native_id) for item in items]
    if any(item is None for item in parsed):
        reasons.append("OPTICAL_PRODUCT_ID_INVALID")
        return reasons
    identities = {
        (
            item.group("platform"),
            item.group("baseline"),
            item.group("orbit"),
            item.group("tile"),
        )
        for item in parsed
        if item is not None
    }
    if len(identities) != 1:
        reasons.append("OPTICAL_PAIR_GEOMETRY_IDENTITY_MISMATCH")
    if identities != {("S2A", "0510", "013", "10TFP")}:
        reasons.append("OPTICAL_PAIR_FROZEN_IDENTITY_MISMATCH")
    return reasons


def _metadata_url(contract: AssetContract) -> str:
    return (
        "https://catalogue.dataspace.copernicus.eu/odata/v1/"
        f"Products({contract.provider_id})"
        "?$select=Id,Name,ContentLength,Online,Checksum,ContentDate,PublicationDate,S3Path,Attributes"
        "&$expand=Attributes"
    )


def _normalize_metadata(payload: dict[str, Any], *, role: str) -> dict[str, Any]:
    checksums = {
        str(item.get("Algorithm", "")).upper(): str(item.get("Value", "")).lower()
        for item in payload.get("Checksum") or []
        if isinstance(item, dict)
    }
    attributes = {
        str(item.get("Name")): item.get("Value")
        for item in payload.get("Attributes") or []
        if isinstance(item, dict) and item.get("Name") is not None
    }
    content_date = payload.get("ContentDate") or {}
    return {
        "role": role,
        "provider_id": payload.get("Id"),
        "native_id": payload.get("Name"),
        "size_bytes": payload.get("ContentLength"),
        "online": payload.get("Online"),
        "acquisition_utc": content_date.get("Start"),
        "publication_utc": payload.get("PublicationDate"),
        "s3_path": payload.get("S3Path"),
        "provider_checksums": checksums,
        "platform_serial_identifier": attributes.get("platformSerialIdentifier"),
        "tile_id": attributes.get("tileId"),
        "relative_orbit_number": attributes.get("relativeOrbitNumber"),
        "processor_version": attributes.get("processorVersion"),
        "product_type": attributes.get("productType"),
        "cloud_cover_percent": attributes.get("cloudCover"),
    }


def validate_optical_metadata(
    snapshot: dict[str, Any],
    contracts: Iterable[AssetContract] = OPTICAL_CONTRACTS,
) -> list[str]:
    """Return stable reason codes for any exact-product metadata drift."""

    records = snapshot.get("records")
    if not isinstance(records, list):
        return ["METADATA_RECORDS_MISSING"]
    by_role = {item.get("role"): item for item in records if isinstance(item, dict)}
    reasons: list[str] = []
    for contract in contracts:
        record = by_role.get(contract.role)
        if record is None:
            reasons.append(f"{contract.role}:MISSING")
            continue
        expected = EXPECTED_METADATA[contract.role]
        checksums = record.get("provider_checksums") or {}
        comparisons = {
            "PROVIDER_ID": contract.provider_id,
            "NATIVE_ID": contract.native_id,
            "SIZE": contract.expected_size_bytes,
            "ACQUISITION": expected["acquisition_utc"],
            "PLATFORM": expected["platform_serial_identifier"],
            "TILE": expected["tile_id"],
            "ORBIT": expected["relative_orbit_number"],
            "BASELINE": expected["processor_version"],
            "PRODUCT_TYPE": expected["product_type"],
            "CLOUD_COVER": expected["cloud_cover_percent"],
        }
        fields = {
            "PROVIDER_ID": record.get("provider_id"),
            "NATIVE_ID": record.get("native_id"),
            "SIZE": record.get("size_bytes"),
            "ACQUISITION": record.get("acquisition_utc"),
            "PLATFORM": record.get("platform_serial_identifier"),
            "TILE": record.get("tile_id"),
            "ORBIT": record.get("relative_orbit_number"),
            "BASELINE": record.get("processor_version"),
            "PRODUCT_TYPE": record.get("product_type"),
            "CLOUD_COVER": record.get("cloud_cover_percent"),
        }
        for code, expected_value in comparisons.items():
            if fields[code] != expected_value:
                reasons.append(f"{contract.role}:{code}")
        if record.get("online") is not True:
            reasons.append(f"{contract.role}:OFFLINE")
        if checksums.get("MD5") != contract.provider_md5:
            reasons.append(f"{contract.role}:MD5")
        if checksums.get("BLAKE3") != contract.provider_blake3:
            reasons.append(f"{contract.role}:BLAKE3")
        s3_path = record.get("s3_path")
        if not isinstance(s3_path, str) or not s3_path.endswith(f"/{contract.native_id}"):
            reasons.append(f"{contract.role}:S3_PATH")
    return reasons


def refresh_optical_metadata(
    *,
    observed_at_utc: str,
    urlopen_fn: Callable[..., Any] = urlopen,
) -> dict[str, Any]:
    """Refresh public metadata for only the two frozen products."""

    headers = {"Accept": "application/json", "User-Agent": USER_AGENT}
    records = []
    for contract in OPTICAL_CONTRACTS:
        payload = _open_json(
            Request(_metadata_url(contract), headers=headers),
            urlopen_fn=urlopen_fn,
        )
        records.append(_normalize_metadata(payload, role=contract.role))
    snapshot = {
        "observed_at_utc": observed_at_utc,
        "terms_review_id": TERMS_REVIEW_ID,
        "live_refresh_performed": True,
        "records": records,
    }
    reasons = validate_optical_metadata(snapshot)
    if reasons:
        raise AcquisitionError("PUBLIC_METADATA_DRIFT", detail=",".join(reasons))
    return snapshot


def _validate_working_entries(quarantine: Path) -> None:
    if not quarantine.exists():
        return
    expected: set[str] = set()
    for contract in OPTICAL_CONTRACTS:
        expected.add(contract.expected_filename)
        expected.add(f"{contract.expected_filename}.part")
    unexpected = sorted(entry.name for entry in quarantine.iterdir() if entry.name not in expected)
    if unexpected:
        raise AcquisitionError("UNEXPECTED_ACQUISITION_WORKING_ENTRY", detail=",".join(unexpected))


def acquire_optical_pair(
    *,
    credentials: CdseCredentials,
    quarantine: Path,
    raw_parent: Path,
    generated_at_utc: str,
    run_id: str,
    metadata_snapshot: dict[str, Any],
    progress: Callable[[str, int, int], None] | None = None,
) -> dict[str, Any]:
    """Download, validate, atomically register, and independently recheck the pair."""

    reasons = validate_optical_contracts(OPTICAL_CONTRACTS)
    reasons.extend(validate_optical_metadata(metadata_snapshot))
    if reasons:
        raise AcquisitionError("OPTICAL_PAIR_CONTRACT_REJECTED", detail=",".join(reasons))

    destination = raw_parent / PACKAGE_ID
    if destination.exists():
        verification = verify_registered_package(
            destination,
            OPTICAL_CONTRACTS,
            contract_validator=validate_optical_contracts,
            contract_version=CONTRACT_VERSION,
        )
        if not verification["accepted_as_unchanged_registered_package"]:
            raise AcquisitionError("EXISTING_REGISTERED_PACKAGE_INVALID")
        return {
            "decision": "REUSED_VERIFIED_REGISTERED_OPTICAL_PAIR",
            "credentials_exercised": False,
            "metadata_snapshot": metadata_snapshot,
            "downloads": [],
            "registration": None,
            "verification": verification,
        }

    quarantine.parent.mkdir(parents=True, exist_ok=True)
    raw_parent.mkdir(parents=True, exist_ok=True)
    _validate_working_entries(quarantine)
    downloads: list[dict[str, Any]] = []
    for contract in OPTICAL_CONTRACTS:
        token: str | None = request_cdse_access_token(
            credentials.username,
            credentials.password,
        )
        try:
            downloads.append(
                stream_asset(
                    contract,
                    quarantine,
                    opener=build_cdse_opener(),
                    headers={"Authorization": f"Bearer {token}"},
                    timeout_seconds=180,
                    progress=progress,
                )
            )
        finally:
            token = None

    try:
        registration = promote_quarantine(
            quarantine,
            destination,
            OPTICAL_CONTRACTS,
            generated_at_utc=generated_at_utc,
            run_id=run_id,
            synthetic_fixture=False,
            contract_validator=validate_optical_contracts,
            contract_version=CONTRACT_VERSION,
        )
    except ValueError:
        evaluation = evaluate_quarantine(
            quarantine,
            OPTICAL_CONTRACTS,
            contract_validator=validate_optical_contracts,
        )
        details = list(evaluation["reason_codes"])
        details.extend(
            f"{observation['role']}:{reason}"
            for observation in evaluation["observations"]
            for reason in observation["reason_codes"]
            if reason != "EXACT_ASSET_ACCEPTED"
        )
        raise AcquisitionError(
            "QUARANTINE_PROMOTION_REJECTED",
            detail=",".join(details),
        ) from None
    except OSError as error:
        raise AcquisitionError(
            "QUARANTINE_ATOMIC_PROMOTION_FAILED",
            detail=type(error).__name__,
        ) from None
    verification = verify_registered_package(
        destination,
        OPTICAL_CONTRACTS,
        contract_validator=validate_optical_contracts,
        contract_version=CONTRACT_VERSION,
    )
    if not verification["accepted_as_unchanged_registered_package"]:
        raise AcquisitionError("POST_PROMOTION_VERIFICATION_FAILED")
    return {
        "decision": "REGISTERED_EXACT_OPTICAL_PAIR",
        "credentials_exercised": True,
        "metadata_snapshot": metadata_snapshot,
        "downloads": downloads,
        "registration": registration,
        "verification": verification,
    }
