"""Exact, fail-closed acquisition contract for two BurnLens cross-event pairs.

The four products were selected by the shipped metadata-feasibility checkpoint.
Their STAC Product assets remain discovery provenance; current CDSE OData
metadata and the documented download route govern the archive bytes acquired
here. Credentials remain short-lived and provider bytes stay in ignored local
storage.
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


SOFTWARE_VERSION = "0.11.0"
PACKAGE_ID = "burnlens-cross-event-optical-package-v0.1.0"
CONTRACT_VERSION = "cross-event-optical-intake-contract-v0.1.0"
SOURCE_RECORD_ID = "SOURCE-2026-012"
TERMS_REVIEW_ID = "TERMS-2026-007"


def _contract(
    *,
    role: str,
    provider_id: str,
    safe_name: str,
    size_bytes: int,
    md5: str,
    blake3: str,
) -> AssetContract:
    return AssetContract(
        role=role,
        provider="Copernicus Data Space Ecosystem",
        source_record_id=SOURCE_RECORD_ID,
        provider_id=provider_id,
        native_id=safe_name,
        expected_filename=f"{safe_name}.zip",
        stable_route=(
            "https://download.dataspace.copernicus.eu/odata/v1/"
            f"Products({provider_id})/$value"
        ),
        expected_size_bytes=size_bytes,
        container="zip-safe",
        package_id=PACKAGE_ID,
        provider_md5=md5,
        provider_blake3=blake3,
        expected_zip_root=safe_name,
    )


CROSS_EVENT_CONTRACTS = (
    _contract(
        role="tepee-2018-pre",
        provider_id="637dfcb9-6a28-487e-b6b3-9645ddc40dcc",
        safe_name="S2B_MSIL2A_20180811T185909_N0500_R013_T10TFP_20230815T160827.SAFE",
        size_bytes=1_129_978_013,
        md5="d88c6f1bdc9e9108c64cb95eaa0da5c9",
        blake3="5c1b3c25b7d2e3e22f1eb474054396a2fb87d0d1748ca7a50edbb9799d523f46",
    ),
    _contract(
        role="tepee-2018-post",
        provider_id="84d6af81-f343-4410-a09e-711b553f2f11",
        safe_name="S2B_MSIL2A_20180920T190049_N0500_R013_T10TFP_20230803T120358.SAFE",
        size_bytes=1_144_413_287,
        md5="f65b6a470713ee0599df8d16f3ba6e92",
        blake3="87602ae65a1821f0d50bab85fb6775cdcba9ee48a839a96a4d654f28f078829f",
    ),
    _contract(
        role="mckay-2017-pre",
        provider_id="a50825f5-3169-42a7-ae55-2eea540e7330",
        safe_name="S2A_MSIL2A_20170729T184921_N0500_R113_T10TFP_20230917T022841.SAFE",
        size_bytes=1_132_353_399,
        md5="1bd2d39175ac50d2982c806275a57063",
        blake3="20fbb16b1611f9592cb437823f6834ffc8eea57f63866ac2515c7f4e86f020d2",
    ),
    _contract(
        role="mckay-2017-post",
        provider_id="53af4b67-470d-4421-8901-54064d9aab1d",
        safe_name="S2A_MSIL2A_20170927T185131_N0500_R113_T10TFP_20230824T183525.SAFE",
        size_bytes=1_144_426_057,
        md5="cb4501abcb2af4b05d7f5b1c55fe6c48",
        blake3="0a68c875b5303a823e44887617c77ea439c39b3e0517d4cc457bf7edf98aa8da",
    ),
)


EXPECTED_METADATA = {
    "tepee-2018-pre": {
        "event_group_id": "event-tepee-1144-ne-2018",
        "acquisition_utc": "2018-08-11T18:59:09.024000Z",
        "platform_serial_identifier": "B",
        "tile_id": "10TFP",
        "relative_orbit_number": 13,
        "processor_version": "05.00",
        "product_type": "S2MSI2A",
        "cloud_cover_percent": 0.004738,
        "stac_product_bytes": 1_129_973_855,
        "stac_product_checksum": "d50110c9f0c53ff153bb15a61713905dbfa9dc",
    },
    "tepee-2018-post": {
        "event_group_id": "event-tepee-1144-ne-2018",
        "acquisition_utc": "2018-09-20T19:00:49.024000Z",
        "platform_serial_identifier": "B",
        "tile_id": "10TFP",
        "relative_orbit_number": 13,
        "processor_version": "05.00",
        "product_type": "S2MSI2A",
        "cloud_cover_percent": 0.001779,
        "stac_product_bytes": 1_144_409_129,
        "stac_product_checksum": "d50110b462c336e489f7e9f21663e1cdff9987",
    },
    "mckay-2017-pre": {
        "event_group_id": "event-mckay-1035-ne-2017",
        "acquisition_utc": "2017-07-29T18:49:21.026000Z",
        "platform_serial_identifier": "A",
        "tile_id": "10TFP",
        "relative_orbit_number": 113,
        "processor_version": "05.00",
        "product_type": "S2MSI2A",
        "cloud_cover_percent": 0.057289,
        "stac_product_bytes": 1_132_353_399,
        "stac_product_checksum": "d50110393480e3a2f6c3a2d8f5ea85e7930703",
    },
    "mckay-2017-post": {
        "event_group_id": "event-mckay-1035-ne-2017",
        "acquisition_utc": "2017-09-27T18:51:31.026000Z",
        "platform_serial_identifier": "A",
        "tile_id": "10TFP",
        "relative_orbit_number": 113,
        "processor_version": "05.00",
        "product_type": "S2MSI2A",
        "cloud_cover_percent": 0.001033,
        "stac_product_bytes": 1_144_426_057,
        "stac_product_checksum": "d501101da5d40191343b8595740bd92d817037",
    },
}


ROUTE_PRECEDENCE = {
    "identity_authority": "Frozen STAC item ID plus CDSE product UUID and SAFE name must agree.",
    "archive_authority": "Current CDSE OData metadata and documented download route govern acquired archive size and checksums.",
    "stac_asset_role": "The STAC Product asset is discovery provenance for a distinct zipper route, not the byte contract for the OData archive.",
}


_PRODUCT_PATTERN = re.compile(
    r"^(?P<platform>S2[ABCD])_MSIL2A_\d{8}T\d{6}_"
    r"N(?P<baseline>\d{4})_R(?P<orbit>\d{3})_T(?P<tile>[0-9A-Z]{5})_"
    r"\d{8}T\d{6}\.SAFE$"
)


@dataclass(repr=False)
class CdseCredentials:
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


def validate_cross_event_contracts(contracts: Iterable[AssetContract]) -> list[str]:
    items = list(contracts)
    reasons = validate_asset_contracts(items)
    expected_roles = set(EXPECTED_METADATA)
    if len(items) != 4:
        reasons.append("CONTRACT_REQUIRES_FOUR_ASSETS")
        return reasons
    if {item.role for item in items} != expected_roles:
        reasons.append("CROSS_EVENT_ROLE_SET_MISMATCH")
        return reasons
    if any(item.package_id != PACKAGE_ID for item in items):
        reasons.append("PACKAGE_ID_MISMATCH")
    parsed = {item.role: _PRODUCT_PATTERN.fullmatch(item.native_id) for item in items}
    if any(value is None for value in parsed.values()):
        reasons.append("OPTICAL_PRODUCT_ID_INVALID")
        return reasons
    by_event: dict[str, set[tuple[str, str, str, str]]] = {}
    for item in items:
        match = parsed[item.role]
        assert match is not None
        event_id = str(EXPECTED_METADATA[item.role]["event_group_id"])
        by_event.setdefault(event_id, set()).add(
            (match.group("platform"), match.group("baseline"), match.group("orbit"), match.group("tile"))
        )
    if any(len(identities) != 1 for identities in by_event.values()):
        reasons.append("EVENT_PAIR_GEOMETRY_IDENTITY_MISMATCH")
    expected = {
        "event-tepee-1144-ne-2018": {("S2B", "0500", "013", "10TFP")},
        "event-mckay-1035-ne-2017": {("S2A", "0500", "113", "10TFP")},
    }
    if by_event != expected:
        reasons.append("CROSS_EVENT_FROZEN_IDENTITY_MISMATCH")
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
    expected = EXPECTED_METADATA[role]
    return {
        "role": role,
        "event_group_id": expected["event_group_id"],
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
        "stac_reference": {
            "product_bytes": expected["stac_product_bytes"],
            "product_checksum": expected["stac_product_checksum"],
            "route_class": "STAC Product asset / zipper packaging",
        },
    }


def validate_cross_event_metadata(
    snapshot: dict[str, Any],
    contracts: Iterable[AssetContract] = CROSS_EVENT_CONTRACTS,
) -> list[str]:
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
        comparisons = {
            "EVENT_GROUP": expected["event_group_id"],
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
            "EVENT_GROUP": record.get("event_group_id"),
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
        checksums = record.get("provider_checksums") or {}
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


def refresh_cross_event_metadata(
    *,
    observed_at_utc: str,
    urlopen_fn: Callable[..., Any] = urlopen,
) -> dict[str, Any]:
    headers = {"Accept": "application/json", "User-Agent": USER_AGENT}
    records = []
    for contract in CROSS_EVENT_CONTRACTS:
        payload = _open_json(Request(_metadata_url(contract), headers=headers), urlopen_fn=urlopen_fn)
        records.append(_normalize_metadata(payload, role=contract.role))
    snapshot = {
        "observed_at_utc": observed_at_utc,
        "source_record_id": SOURCE_RECORD_ID,
        "terms_review_id": TERMS_REVIEW_ID,
        "live_refresh_performed": True,
        "route_precedence": ROUTE_PRECEDENCE,
        "records": records,
    }
    reasons = validate_cross_event_metadata(snapshot)
    if reasons:
        raise AcquisitionError("PUBLIC_METADATA_DRIFT", detail=",".join(reasons))
    return snapshot


def _validate_working_entries(quarantine: Path) -> None:
    if not quarantine.exists():
        return
    expected: set[str] = set()
    for contract in CROSS_EVENT_CONTRACTS:
        expected.add(contract.expected_filename)
        expected.add(f"{contract.expected_filename}.part")
    unexpected = sorted(entry.name for entry in quarantine.iterdir() if entry.name not in expected)
    if unexpected:
        raise AcquisitionError("UNEXPECTED_ACQUISITION_WORKING_ENTRY", detail=",".join(unexpected))


def acquire_cross_event_package(
    *,
    credentials: CdseCredentials,
    quarantine: Path,
    raw_parent: Path,
    generated_at_utc: str,
    run_id: str,
    metadata_snapshot: dict[str, Any],
    progress: Callable[[str, int, int], None] | None = None,
) -> dict[str, Any]:
    reasons = validate_cross_event_contracts(CROSS_EVENT_CONTRACTS)
    reasons.extend(validate_cross_event_metadata(metadata_snapshot))
    if reasons:
        raise AcquisitionError("CROSS_EVENT_PACKAGE_CONTRACT_REJECTED", detail=",".join(reasons))

    destination = raw_parent / PACKAGE_ID
    if destination.exists():
        verification = verify_registered_package(
            destination,
            CROSS_EVENT_CONTRACTS,
            contract_validator=validate_cross_event_contracts,
            contract_version=CONTRACT_VERSION,
        )
        if not verification["accepted_as_unchanged_registered_package"]:
            raise AcquisitionError("EXISTING_REGISTERED_PACKAGE_INVALID")
        return {
            "decision": "REUSED_VERIFIED_REGISTERED_CROSS_EVENT_PACKAGE",
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
    for contract in CROSS_EVENT_CONTRACTS:
        token: str | None = request_cdse_access_token(credentials.username, credentials.password)
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
            CROSS_EVENT_CONTRACTS,
            generated_at_utc=generated_at_utc,
            run_id=run_id,
            synthetic_fixture=False,
            contract_validator=validate_cross_event_contracts,
            contract_version=CONTRACT_VERSION,
        )
    except ValueError:
        evaluation = evaluate_quarantine(
            quarantine,
            CROSS_EVENT_CONTRACTS,
            contract_validator=validate_cross_event_contracts,
        )
        details = list(evaluation["reason_codes"])
        details.extend(
            f"{observation['role']}:{reason}"
            for observation in evaluation["observations"]
            for reason in observation["reason_codes"]
            if reason != "EXACT_ASSET_ACCEPTED"
        )
        raise AcquisitionError("QUARANTINE_PROMOTION_REJECTED", detail=",".join(details)) from None
    except OSError as error:
        raise AcquisitionError("QUARANTINE_ATOMIC_PROMOTION_FAILED", detail=type(error).__name__) from None
    verification = verify_registered_package(
        destination,
        CROSS_EVENT_CONTRACTS,
        contract_validator=validate_cross_event_contracts,
        contract_version=CONTRACT_VERSION,
    )
    if not verification["accepted_as_unchanged_registered_package"]:
        raise AcquisitionError("POST_PROMOTION_VERIFICATION_FAILED")
    return {
        "decision": "REGISTERED_EXACT_CROSS_EVENT_PACKAGE",
        "credentials_exercised": True,
        "metadata_snapshot": metadata_snapshot,
        "downloads": downloads,
        "registration": registration,
        "verification": verification,
    }
