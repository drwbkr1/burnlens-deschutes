"""Exact fail-closed acquisition contract for Green Ridge extended optical evidence."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Iterable
from urllib.request import Request, urlopen

from .cross_event_optical_contract import CdseCredentials
from .green_ridge_optical_contract import _metadata_url, _normalize_metadata
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


SOFTWARE_VERSION = "0.35.0"
PACKAGE_ID = "green-ridge-s2-background-extended-v0.1.0"
CONTRACT_VERSION = "green-ridge-background-optical-intake-contract-v0.1.0"
SOURCE_RECORD_ID = "SOURCE-2026-023"
TERMS_REVIEW_ID = "TERMS-2026-019"
EVENT_GROUP_ID = "event-green-ridge-0684-cs-2020"
TEMPORARY_SUFFIX = ".tmp"
TEMPORARY_PREFIX = "~$"
MAX_TRANSFER_ATTEMPTS = 5
RETRYABLE_TRANSFER_REASONS = {
    "DOWNLOAD_REQUEST_FAILED",
    "DOWNLOAD_STREAM_FAILED",
    "DOWNLOAD_SIZE_MISMATCH",
}

EXTENDED_CONTRACT = AssetContract(
    role="green-ridge-2021-extended",
    provider="Copernicus Data Space Ecosystem",
    source_record_id=SOURCE_RECORD_ID,
    provider_id="328ecb9e-129d-4c8a-8e61-83516102f16e",
    native_id="S2B_MSIL2A_20210815T185919_N0500_R013_T10TFQ_20230119T130649.SAFE",
    expected_filename="S2B_MSIL2A_20210815T185919_N0500_R013_T10TFQ_20230119T130649.SAFE.zip",
    stable_route=(
        "https://download.dataspace.copernicus.eu/odata/v1/"
        "Products(328ecb9e-129d-4c8a-8e61-83516102f16e)/$value"
    ),
    expected_size_bytes=1_193_992_663,
    container="zip-safe",
    package_id=PACKAGE_ID,
    provider_md5="0d1d794b0d02bc7c96bb4f0c2f7671d9",
    provider_blake3="361fb269a330c8866c3c499f7954b242040abf528efbcb6f9008a5aab2455d26",
    expected_zip_root="S2B_MSIL2A_20210815T185919_N0500_R013_T10TFQ_20230119T130649.SAFE",
)
BACKGROUND_OPTICAL_CONTRACTS = (EXTENDED_CONTRACT,)

EXPECTED_METADATA = {
    "acquisition_utc": "2021-08-15T18:59:19.024000Z",
    "platform_serial_identifier": "B",
    "tile_id": "10TFQ",
    "relative_orbit_number": 13,
    "processor_version": "05.00",
    "product_type": "S2MSI2A",
    "cloud_cover_percent": 0.985365,
}

ROUTE_PRECEDENCE = {
    "selection": (
        "Current CDSE STAC full-boundary coverage; same Sentinel-2B platform, MGRS-10TFQ tile, "
        "relative orbit 13, processing baseline 05.00; closest near-anniversary acquisition to the "
        "2020-08-10 pre-fire scene after cloud metadata is below 20 percent."
    ),
    "identity_authority": "Frozen STAC item, CDSE product UUID, SAFE name, and OData metadata must agree.",
    "archive_authority": "Current CDSE OData size plus MD5 and BLAKE3 govern acquired bytes.",
    "use_boundary": "Extended optical stability is candidate evidence only and cannot create background truth or a label.",
}


def validate_background_optical_contracts(contracts: Iterable[AssetContract]) -> list[str]:
    items = list(contracts)
    reasons = validate_asset_contracts(items)
    if items != [EXTENDED_CONTRACT]:
        reasons.append("CONTRACT_REQUIRES_EXACT_EXTENDED_ASSET")
    if any(item.package_id != PACKAGE_ID for item in items):
        reasons.append("PACKAGE_ID_MISMATCH")
    if any("S2B_MSIL2A_20210815T185919_N0500_R013_T10TFQ" not in item.native_id for item in items):
        reasons.append("EXTENDED_SCENE_IDENTITY_MISMATCH")
    return reasons


def validate_background_optical_metadata(snapshot: dict[str, Any]) -> list[str]:
    records = snapshot.get("records")
    if not isinstance(records, list) or len(records) != 1:
        return ["METADATA_RECORD_SET_MISMATCH"]
    record = records[0]
    contract = EXTENDED_CONTRACT
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
    expected = {
        "EVENT_GROUP": EVENT_GROUP_ID,
        "PROVIDER_ID": contract.provider_id,
        "NATIVE_ID": contract.native_id,
        "SIZE": contract.expected_size_bytes,
        "ACQUISITION": EXPECTED_METADATA["acquisition_utc"],
        "PLATFORM": EXPECTED_METADATA["platform_serial_identifier"],
        "TILE": EXPECTED_METADATA["tile_id"],
        "ORBIT": EXPECTED_METADATA["relative_orbit_number"],
        "BASELINE": EXPECTED_METADATA["processor_version"],
        "PRODUCT_TYPE": EXPECTED_METADATA["product_type"],
        "CLOUD_COVER": EXPECTED_METADATA["cloud_cover_percent"],
    }
    reasons = [code for code, value in expected.items() if fields[code] != value]
    checksums = record.get("provider_checksums") or {}
    if record.get("online") is not True:
        reasons.append("OFFLINE")
    if checksums.get("MD5") != contract.provider_md5:
        reasons.append("MD5")
    if checksums.get("BLAKE3") != contract.provider_blake3:
        reasons.append("BLAKE3")
    s3_path = record.get("s3_path")
    if not isinstance(s3_path, str) or not s3_path.endswith(f"/{contract.native_id}"):
        reasons.append("S3_PATH")
    return reasons


def refresh_background_optical_metadata(
    *, observed_at_utc: str, urlopen_fn: Callable[..., Any] = urlopen
) -> dict[str, Any]:
    headers = {"Accept": "application/json", "User-Agent": USER_AGENT}
    payload = _open_json(Request(_metadata_url(EXTENDED_CONTRACT), headers=headers), urlopen_fn=urlopen_fn)
    record = _normalize_metadata(payload, role=EXTENDED_CONTRACT.role)
    record["event_group_id"] = EVENT_GROUP_ID
    snapshot = {
        "observed_at_utc": observed_at_utc,
        "source_record_id": SOURCE_RECORD_ID,
        "terms_review_id": TERMS_REVIEW_ID,
        "live_refresh_performed": True,
        "route_precedence": ROUTE_PRECEDENCE,
        "records": [record],
    }
    reasons = validate_background_optical_metadata(snapshot)
    if reasons:
        raise AcquisitionError("PUBLIC_METADATA_DRIFT", detail=",".join(reasons))
    return snapshot


def _validate_working_entries(quarantine: Path) -> None:
    if not quarantine.exists():
        return
    expected = {
        EXTENDED_CONTRACT.expected_filename,
        f"{TEMPORARY_PREFIX}{EXTENDED_CONTRACT.expected_filename}{TEMPORARY_SUFFIX}",
    }
    unexpected = sorted(entry.name for entry in quarantine.iterdir() if entry.name not in expected)
    if unexpected:
        raise AcquisitionError("UNEXPECTED_ACQUISITION_WORKING_ENTRY", detail=",".join(unexpected))


def acquire_background_optical_package(
    *,
    credentials: CdseCredentials,
    quarantine: Path,
    raw_parent: Path,
    generated_at_utc: str,
    run_id: str,
    metadata_snapshot: dict[str, Any],
    progress: Callable[[str, int, int], None] | None = None,
) -> dict[str, Any]:
    reasons = validate_background_optical_contracts(BACKGROUND_OPTICAL_CONTRACTS)
    reasons.extend(validate_background_optical_metadata(metadata_snapshot))
    if reasons:
        raise AcquisitionError("BACKGROUND_OPTICAL_PACKAGE_CONTRACT_REJECTED", detail=",".join(reasons))
    destination = raw_parent / PACKAGE_ID
    if destination.exists():
        verification = verify_registered_package(
            destination,
            BACKGROUND_OPTICAL_CONTRACTS,
            contract_validator=validate_background_optical_contracts,
            contract_version=CONTRACT_VERSION,
            allow_multilink_registration_manifest=True,
        )
        if not verification["accepted_as_unchanged_registered_package"]:
            raise AcquisitionError("EXISTING_REGISTERED_PACKAGE_INVALID")
        return {
            "decision": "REUSED_VERIFIED_REGISTERED_BACKGROUND_OPTICAL_PACKAGE",
            "credentials_exercised": False,
            "metadata_snapshot": metadata_snapshot,
            "downloads": [],
            "registration": None,
            "verification": verification,
        }
    quarantine.parent.mkdir(parents=True, exist_ok=True)
    raw_parent.mkdir(parents=True, exist_ok=True)
    _validate_working_entries(quarantine)
    result: dict[str, Any] | None = None
    for attempt in range(1, MAX_TRANSFER_ATTEMPTS + 1):
        token: str | None = request_cdse_access_token(credentials.username, credentials.password)
        try:
            result = stream_asset(
                EXTENDED_CONTRACT,
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
        break
    if result is None:
        raise AcquisitionError("BACKGROUND_OPTICAL_DOWNLOAD_MISSING")
    try:
        registration = promote_quarantine(
            quarantine,
            destination,
            BACKGROUND_OPTICAL_CONTRACTS,
            generated_at_utc=generated_at_utc,
            run_id=run_id,
            synthetic_fixture=False,
            contract_validator=validate_background_optical_contracts,
            contract_version=CONTRACT_VERSION,
        )
    except ValueError:
        evaluation = evaluate_quarantine(
            quarantine,
            BACKGROUND_OPTICAL_CONTRACTS,
            contract_validator=validate_background_optical_contracts,
        )
        raise AcquisitionError(
            "QUARANTINE_PROMOTION_REJECTED", detail=",".join(evaluation["reason_codes"])
        ) from None
    except OSError as error:
        raise AcquisitionError("QUARANTINE_ATOMIC_PROMOTION_FAILED", detail=type(error).__name__) from None
    verification = verify_registered_package(
        destination,
        BACKGROUND_OPTICAL_CONTRACTS,
        contract_validator=validate_background_optical_contracts,
        contract_version=CONTRACT_VERSION,
        allow_multilink_registration_manifest=True,
    )
    if not verification["accepted_as_unchanged_registered_package"]:
        raise AcquisitionError("POST_PROMOTION_VERIFICATION_FAILED")
    return {
        "decision": "REGISTERED_EXACT_BACKGROUND_OPTICAL_PACKAGE",
        "credentials_exercised": True,
        "metadata_snapshot": metadata_snapshot,
        "downloads": [result],
        "registration": registration,
        "verification": verification,
    }
