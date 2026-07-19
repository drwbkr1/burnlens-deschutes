"""Exact fail-closed acquisition contract for the Green Ridge Sentinel pair."""

from __future__ import annotations

from pathlib import Path
import re
from typing import Any, Callable, Iterable
from urllib.request import Request, urlopen

from .cross_event_optical_contract import CdseCredentials
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


SOFTWARE_VERSION = "0.32.0"
PACKAGE_ID = "green-ridge-s2-optical-pair-v0.1.0"
CONTRACT_VERSION = "green-ridge-optical-intake-contract-v0.1.0"
SOURCE_RECORD_ID = "SOURCE-2026-020"
TERMS_REVIEW_ID = "TERMS-2026-016"
EVENT_GROUP_ID = "event-green-ridge-0684-cs-2020"
TEMPORARY_SUFFIX = ".tmp"
TEMPORARY_PREFIX = "~$"
MAX_TRANSFER_ATTEMPTS = 5
RETRYABLE_TRANSFER_REASONS = {
    "DOWNLOAD_REQUEST_FAILED",
    "DOWNLOAD_STREAM_FAILED",
    "DOWNLOAD_SIZE_MISMATCH",
}


def _contract(
    *, role: str, provider_id: str, safe_name: str, size_bytes: int, md5: str, blake3: str
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


GREEN_RIDGE_CONTRACTS = (
    _contract(
        role="green-ridge-2020-pre",
        provider_id="13b49b0d-390d-4a1b-90a6-c06fc5feac75",
        safe_name="S2B_MSIL2A_20200810T185919_N0500_R013_T10TFQ_20230509T050550.SAFE",
        size_bytes=1_190_832_495,
        md5="42e951ef3b0bbdefc652a9c3009b7b81",
        blake3="e1dacd034aa05af169af627a664142750d9220297b7cb8d5c7b67b4122cb2794",
    ),
    _contract(
        role="green-ridge-2020-post",
        provider_id="bfb174db-0438-45c8-b59d-feb76f58c029",
        safe_name="S2B_MSIL2A_20200929T190109_N0500_R013_T10TFQ_20230427T010543.SAFE",
        size_bytes=1_197_623_643,
        md5="c4621bad458e78bc660fe9cbbda37fda",
        blake3="4ec71a9af55cb84a1eec8c174a96fa5689841aa8771bf86f6c655ac9e7046be9",
    ),
)


EXPECTED_METADATA = {
    "green-ridge-2020-pre": {
        "acquisition_utc": "2020-08-10T18:59:19.024000Z",
        "platform_serial_identifier": "B",
        "tile_id": "10TFQ",
        "relative_orbit_number": 13,
        "processor_version": "05.00",
        "product_type": "S2MSI2A",
        "cloud_cover_percent": 0.00357,
    },
    "green-ridge-2020-post": {
        "acquisition_utc": "2020-09-29T19:01:09.024000Z",
        "platform_serial_identifier": "B",
        "tile_id": "10TFQ",
        "relative_orbit_number": 13,
        "processor_version": "05.00",
        "product_type": "S2MSI2A",
        "cloud_cover_percent": 0.000176,
    },
}


ROUTE_PRECEDENCE = {
    "identity_authority": "Frozen STAC item ID plus CDSE product UUID and SAFE name must agree.",
    "archive_authority": "Current CDSE OData size and checksums govern acquired archive bytes.",
    "stac_asset_role": "The STAC Product asset is discovery provenance, not the OData byte contract.",
}


_PRODUCT_PATTERN = re.compile(
    r"^(?P<platform>S2[ABCD])_MSIL2A_\d{8}T\d{6}_"
    r"N(?P<baseline>\d{4})_R(?P<orbit>\d{3})_T(?P<tile>[0-9A-Z]{5})_"
    r"\d{8}T\d{6}\.SAFE$"
)


def validate_green_ridge_contracts(contracts: Iterable[AssetContract]) -> list[str]:
    items = list(contracts)
    reasons = validate_asset_contracts(items)
    if len(items) != 2:
        return [*reasons, "CONTRACT_REQUIRES_TWO_ASSETS"]
    if {item.role for item in items} != set(EXPECTED_METADATA):
        return [*reasons, "GREEN_RIDGE_ROLE_SET_MISMATCH"]
    if any(item.package_id != PACKAGE_ID for item in items):
        reasons.append("PACKAGE_ID_MISMATCH")
    parsed = [_PRODUCT_PATTERN.fullmatch(item.native_id) for item in items]
    if any(value is None for value in parsed):
        return [*reasons, "OPTICAL_PRODUCT_ID_INVALID"]
    identities = {
        (match.group("platform"), match.group("baseline"), match.group("orbit"), match.group("tile"))
        for match in parsed
        if match is not None
    }
    if identities != {("S2B", "0500", "013", "10TFQ")}:
        reasons.append("GREEN_RIDGE_PAIR_GEOMETRY_IDENTITY_MISMATCH")
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
        "event_group_id": EVENT_GROUP_ID,
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


def validate_green_ridge_metadata(
    snapshot: dict[str, Any], contracts: Iterable[AssetContract] = GREEN_RIDGE_CONTRACTS
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
            "EVENT_GROUP": EVENT_GROUP_ID,
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


def refresh_green_ridge_metadata(
    *, observed_at_utc: str, urlopen_fn: Callable[..., Any] = urlopen
) -> dict[str, Any]:
    headers = {"Accept": "application/json", "User-Agent": USER_AGENT}
    records = []
    for contract in GREEN_RIDGE_CONTRACTS:
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
    reasons = validate_green_ridge_metadata(snapshot)
    if reasons:
        raise AcquisitionError("PUBLIC_METADATA_DRIFT", detail=",".join(reasons))
    return snapshot


def _validate_working_entries(quarantine: Path) -> None:
    if not quarantine.exists():
        return
    expected = {
        name
        for contract in GREEN_RIDGE_CONTRACTS
        for name in (
            contract.expected_filename,
            f"{TEMPORARY_PREFIX}{contract.expected_filename}{TEMPORARY_SUFFIX}",
        )
    }
    unexpected = sorted(entry.name for entry in quarantine.iterdir() if entry.name not in expected)
    if unexpected:
        raise AcquisitionError("UNEXPECTED_ACQUISITION_WORKING_ENTRY", detail=",".join(unexpected))


def acquire_green_ridge_package(
    *,
    credentials: CdseCredentials,
    quarantine: Path,
    raw_parent: Path,
    generated_at_utc: str,
    run_id: str,
    metadata_snapshot: dict[str, Any],
    progress: Callable[[str, int, int], None] | None = None,
) -> dict[str, Any]:
    reasons = validate_green_ridge_contracts(GREEN_RIDGE_CONTRACTS)
    reasons.extend(validate_green_ridge_metadata(metadata_snapshot))
    if reasons:
        raise AcquisitionError("GREEN_RIDGE_PACKAGE_CONTRACT_REJECTED", detail=",".join(reasons))

    destination = raw_parent / PACKAGE_ID
    if destination.exists():
        verification = verify_registered_package(
            destination,
            GREEN_RIDGE_CONTRACTS,
            contract_validator=validate_green_ridge_contracts,
            contract_version=CONTRACT_VERSION,
            allow_multilink_registration_manifest=True,
        )
        if not verification["accepted_as_unchanged_registered_package"]:
            raise AcquisitionError("EXISTING_REGISTERED_PACKAGE_INVALID")
        return {
            "decision": "REUSED_VERIFIED_REGISTERED_GREEN_RIDGE_PACKAGE",
            "credentials_exercised": False,
            "metadata_snapshot": metadata_snapshot,
            "downloads": [],
            "registration": None,
            "verification": verification,
        }

    quarantine.parent.mkdir(parents=True, exist_ok=True)
    raw_parent.mkdir(parents=True, exist_ok=True)
    _validate_working_entries(quarantine)
    downloads = []
    for contract in GREEN_RIDGE_CONTRACTS:
        for attempt in range(1, MAX_TRANSFER_ATTEMPTS + 1):
            token: str | None = request_cdse_access_token(credentials.username, credentials.password)
            try:
                result = stream_asset(
                    contract,
                    quarantine,
                    opener=build_cdse_opener(),
                    headers={"Authorization": f"Bearer {token}"},
                    timeout_seconds=180,
                    progress=progress,
                    part_suffix=TEMPORARY_SUFFIX,
                    part_prefix=TEMPORARY_PREFIX,
                )
            except AcquisitionError as error:
                if error.reason_code in RETRYABLE_TRANSFER_REASONS and attempt < MAX_TRANSFER_ATTEMPTS:
                    continue
                raise
            finally:
                token = None
            result["attempt_count"] = attempt
            downloads.append(result)
            break

    try:
        registration = promote_quarantine(
            quarantine,
            destination,
            GREEN_RIDGE_CONTRACTS,
            generated_at_utc=generated_at_utc,
            run_id=run_id,
            synthetic_fixture=False,
            contract_validator=validate_green_ridge_contracts,
            contract_version=CONTRACT_VERSION,
        )
    except ValueError:
        evaluation = evaluate_quarantine(
            quarantine, GREEN_RIDGE_CONTRACTS, contract_validator=validate_green_ridge_contracts
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
        GREEN_RIDGE_CONTRACTS,
        contract_validator=validate_green_ridge_contracts,
        contract_version=CONTRACT_VERSION,
        allow_multilink_registration_manifest=True,
    )
    if not verification["accepted_as_unchanged_registered_package"]:
        raise AcquisitionError("POST_PROMOTION_VERIFICATION_FAILED")
    return {
        "decision": "REGISTERED_EXACT_GREEN_RIDGE_PACKAGE",
        "credentials_exercised": True,
        "metadata_snapshot": metadata_snapshot,
        "downloads": downloads,
        "registration": registration,
        "verification": verification,
    }
