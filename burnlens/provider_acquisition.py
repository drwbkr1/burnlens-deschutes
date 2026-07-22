"""Secret-safe authenticated acquisition for the exact BurnLens provider package.

Credentials enter through short-lived child-process environment variables created
by the Windows DPAPI wrapper.  This module removes those variables immediately,
never logs secret-bearing URLs or headers, downloads only the frozen contracts,
and delegates registration to :mod:`burnlens.paired_intake`.
"""

from __future__ import annotations

import ctypes
from dataclasses import dataclass
import errno
from http.cookiejar import CookieJar
import io
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
from typing import Any, Callable, Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import (
    HTTPBasicAuthHandler,
    HTTPPasswordMgrWithDefaultRealm,
    HTTPRedirectHandler,
    HTTPCookieProcessor,
    Request,
    build_opener,
    urlopen,
)

from .paired_intake import (
    CONTRACT_VERSION as PAIRED_INTAKE_CONTRACT_VERSION,
    EXACT_CONTRACTS,
    HDF5_MAGIC,
    PACKAGE_ID,
    ZIP_MAGICS,
    AssetContract,
    ContractValidator,
    _is_link_like,
    contract_digest,
    evaluate_quarantine,
    inspect_asset,
    validate_contract_set,
    verify_registered_package,
)


SOFTWARE_VERSION = "0.4.0"
CHUNK_BYTES = 1024 * 1024
MAX_JSON_BYTES = 4 * 1024 * 1024
MAX_BOUNDED_TRANSFER_ATTEMPTS = 5
USER_AGENT = "BurnLens/0.4.0 experimental-research"
CDSE_TOKEN_URL = (
    "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/"
    "protocol/openid-connect/token"
)
CDSE_METADATA_URL = (
    "https://catalogue.dataspace.copernicus.eu/odata/v1/"
    "Products(58cebcf0-c417-4384-a93a-2d6b15344117)"
    "?$select=Id,Name,ContentLength,Online,Checksum"
)
NASA_CMR_URLS = {
    "G3944882727-LPCLOUD": (
        "https://cmr.earthdata.nasa.gov/search/granules.umm_json"
        "?concept_id=G3944882727-LPCLOUD"
    ),
    "G4037038741-LPCLOUD": (
        "https://cmr.earthdata.nasa.gov/search/granules.umm_json"
        "?concept_id=G4037038741-LPCLOUD"
    ),
}
SECRET_ENV_NAMES = (
    "BURNLENS_CDSE_USERNAME",
    "BURNLENS_CDSE_PASSWORD",
    "BURNLENS_EARTHDATA_USERNAME",
    "BURNLENS_EARTHDATA_PASSWORD",
)
NONRETRYABLE_HTTP_STATUSES = frozenset({401, 403, 404, 429})
RETRYABLE_TRANSFER_REASONS = frozenset(
    {
        "DOWNLOAD_REQUEST_FAILED",
        "DOWNLOAD_STREAM_FAILED",
        "DOWNLOAD_EARLY_EOF",
        "JSON_REQUEST_FAILED",
    }
)
HTTP_STATUS_REASON_CODES = frozenset(
    {"DOWNLOAD_HTTP_STATUS_REJECTED", "JSON_HTTP_STATUS_REJECTED"}
)


class AcquisitionError(RuntimeError):
    """A bounded failure that is safe to expose without provider secrets."""

    def __init__(self, reason_code: str, *, role: str | None = None, detail: str | None = None):
        self.reason_code = reason_code
        self.role = role
        self.detail = detail
        parts = [reason_code]
        if role:
            parts.append(f"role={role}")
        if detail:
            parts.append(f"detail={detail}")
        super().__init__("; ".join(parts))


@dataclass(repr=False)
class ProviderCredentials:
    cdse_username: str
    cdse_password: str
    earthdata_username: str
    earthdata_password: str

    def __repr__(self) -> str:
        return "ProviderCredentials(<redacted>)"

    @classmethod
    def from_environment(cls) -> "ProviderCredentials":
        values = {name: os.environ.pop(name, None) for name in SECRET_ENV_NAMES}
        missing = [name for name, value in values.items() if not value]
        if missing:
            values.clear()
            raise AcquisitionError("CREDENTIAL_ENV_MISSING", detail=",".join(sorted(missing)))
        return cls(
            cdse_username=values["BURNLENS_CDSE_USERNAME"] or "",
            cdse_password=values["BURNLENS_CDSE_PASSWORD"] or "",
            earthdata_username=values["BURNLENS_EARTHDATA_USERNAME"] or "",
            earthdata_password=values["BURNLENS_EARTHDATA_PASSWORD"] or "",
        )


def _read_json_response(response: Any) -> dict[str, Any]:
    payload = response.read(MAX_JSON_BYTES + 1)
    if len(payload) > MAX_JSON_BYTES:
        raise AcquisitionError("JSON_RESPONSE_TOO_LARGE")
    try:
        parsed = json.loads(payload.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise AcquisitionError("JSON_RESPONSE_INVALID", detail=type(error).__name__) from None
    if not isinstance(parsed, dict):
        raise AcquisitionError("JSON_RESPONSE_NOT_OBJECT")
    return parsed


def _open_json(
    request: Request,
    *,
    urlopen_fn: Callable[..., Any] = urlopen,
    timeout_seconds: float = 60,
) -> dict[str, Any]:
    try:
        with urlopen_fn(request, timeout=timeout_seconds) as response:
            status = getattr(response, "status", None)
            if status is None:
                status = response.getcode()
            if status != 200:
                raise AcquisitionError("JSON_HTTP_STATUS_REJECTED", detail=str(status))
            return _read_json_response(response)
    except AcquisitionError:
        raise
    except HTTPError as error:
        raise AcquisitionError("JSON_HTTP_STATUS_REJECTED", detail=str(error.code)) from None
    except (URLError, TimeoutError, OSError) as error:
        raise AcquisitionError("JSON_REQUEST_FAILED", detail=type(error).__name__) from None


def _normalized_cdse_metadata(payload: dict[str, Any]) -> dict[str, Any]:
    checksums: dict[str, str] = {}
    for item in payload.get("Checksum") or []:
        if isinstance(item, dict) and isinstance(item.get("Algorithm"), str) and isinstance(item.get("Value"), str):
            checksums[item["Algorithm"].upper()] = item["Value"].lower()
    return {
        "role": "sentinel-2-l2a",
        "provider_id": payload.get("Id"),
        "native_id": payload.get("Name"),
        "size_bytes": payload.get("ContentLength"),
        "online": payload.get("Online"),
        "provider_checksums": checksums,
    }


def _normalized_cmr_metadata(payload: dict[str, Any], *, role: str) -> dict[str, Any]:
    items = payload.get("items")
    if not isinstance(items, list) or len(items) != 1 or not isinstance(items[0], dict):
        raise AcquisitionError("CMR_EXACT_GRANULE_COUNT_MISMATCH", role=role)
    item = items[0]
    meta = item.get("meta") or {}
    umm = item.get("umm") or {}
    distribution = (umm.get("DataGranule") or {}).get("ArchiveAndDistributionInformation") or []
    if not isinstance(distribution, list) or not distribution:
        raise AcquisitionError("CMR_SIZE_METADATA_MISSING", role=role)
    size_record = distribution[0]
    if not isinstance(size_record, dict) or size_record.get("SizeUnit") != "MB":
        raise AcquisitionError("CMR_SIZE_UNIT_UNEXPECTED", role=role)
    try:
        size_bytes = round(float(size_record["Size"]) * 1024 * 1024)
    except (KeyError, TypeError, ValueError):
        raise AcquisitionError("CMR_SIZE_METADATA_INVALID", role=role) from None
    checksum = size_record.get("Checksum") if isinstance(size_record, dict) else None
    return {
        "role": role,
        "provider_id": meta.get("concept-id"),
        "native_id": umm.get("GranuleUR"),
        "size_bytes": size_bytes,
        "revision_date": meta.get("revision-date"),
        "provider_checksum": checksum if checksum else None,
    }


def refresh_public_metadata(
    *,
    observed_at_utc: str,
    urlopen_fn: Callable[..., Any] = urlopen,
) -> dict[str, Any]:
    headers = {"Accept": "application/json", "User-Agent": USER_AGENT}
    cdse = _open_json(Request(CDSE_METADATA_URL, headers=headers), urlopen_fn=urlopen_fn)
    records = [_normalized_cdse_metadata(cdse)]
    role_by_id = {
        "G3944882727-LPCLOUD": "viirs-active-fire",
        "G4037038741-LPCLOUD": "viirs-geolocation",
    }
    for provider_id, metadata_url in NASA_CMR_URLS.items():
        payload = _open_json(Request(metadata_url, headers=headers), urlopen_fn=urlopen_fn)
        records.append(_normalized_cmr_metadata(payload, role=role_by_id[provider_id]))
    snapshot = {
        "observed_at_utc": observed_at_utc,
        "live_refresh_performed": True,
        "records": records,
    }
    reasons = validate_metadata_snapshot(snapshot)
    if reasons:
        raise AcquisitionError("PUBLIC_METADATA_DRIFT", detail=",".join(reasons))
    return snapshot


def validate_metadata_snapshot(
    snapshot: dict[str, Any],
    contracts: Iterable[AssetContract] = EXACT_CONTRACTS,
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
        if record.get("provider_id") != contract.provider_id:
            reasons.append(f"{contract.role}:PROVIDER_ID")
        if record.get("native_id") != contract.native_id:
            reasons.append(f"{contract.role}:NATIVE_ID")
        if record.get("size_bytes") != contract.expected_size_bytes:
            reasons.append(f"{contract.role}:SIZE")
        if contract.role == "sentinel-2-l2a":
            checksums = record.get("provider_checksums") or {}
            if record.get("online") is not True:
                reasons.append(f"{contract.role}:OFFLINE")
            if checksums.get("MD5") != contract.provider_md5:
                reasons.append(f"{contract.role}:MD5")
            if checksums.get("BLAKE3") != contract.provider_blake3:
                reasons.append(f"{contract.role}:BLAKE3")
        elif record.get("provider_checksum") is not None:
            reasons.append(f"{contract.role}:UNEXPECTED_PROVIDER_CHECKSUM")
    return reasons


class SafeRedirectHandler(HTTPRedirectHandler):
    """Follow only HTTPS provider redirects and prevent cross-host auth leakage."""

    def __init__(
        self,
        *,
        allowed_host_suffixes: tuple[str, ...],
        authorization_host_suffixes: tuple[str, ...] = (),
    ) -> None:
        super().__init__()
        self.allowed_host_suffixes = tuple(item.lower() for item in allowed_host_suffixes)
        self.authorization_host_suffixes = tuple(item.lower() for item in authorization_host_suffixes)

    @staticmethod
    def _matches(host: str, suffixes: tuple[str, ...]) -> bool:
        for suffix in suffixes:
            if suffix.startswith("."):
                if host == suffix[1:] or host.endswith(suffix):
                    return True
            elif host == suffix:
                return True
        return False

    def redirect_request(
        self,
        req: Request,
        fp: Any,
        code: int,
        msg: str,
        headers: Any,
        newurl: str,
    ) -> Request | None:
        parts = urlsplit(newurl)
        host = (parts.hostname or "").lower()
        if parts.scheme.lower() != "https" or not self._matches(host, self.allowed_host_suffixes):
            raise AcquisitionError("UNTRUSTED_REDIRECT_HOST")
        redirected = super().redirect_request(req, fp, code, msg, headers, newurl)
        if redirected is None:
            return None
        if not self._matches(host, self.authorization_host_suffixes):
            redirected.headers.pop("Authorization", None)
            redirected.unredirected_hdrs.pop("Authorization", None)
        return redirected


def build_cdse_opener() -> Any:
    return build_opener(
        SafeRedirectHandler(
            allowed_host_suffixes=(".dataspace.copernicus.eu",),
            authorization_host_suffixes=(".dataspace.copernicus.eu",),
        )
    )


def build_earthdata_opener(username: str, password: str) -> Any:
    manager = HTTPPasswordMgrWithDefaultRealm()
    manager.add_password(None, "https://urs.earthdata.nasa.gov", username, password)
    return build_opener(
        SafeRedirectHandler(
            allowed_host_suffixes=(".nasa.gov", ".usgs.gov", ".amazonaws.com", ".cloudfront.net"),
            authorization_host_suffixes=("urs.earthdata.nasa.gov",),
        ),
        HTTPBasicAuthHandler(manager),
        HTTPCookieProcessor(CookieJar()),
    )


def request_cdse_access_token(
    username: str,
    password: str,
    *,
    urlopen_fn: Callable[..., Any] | None = None,
) -> str:
    body = urlencode(
        {
            "client_id": "cdse-public",
            "grant_type": "password",
            "username": username,
            "password": password,
        }
    ).encode("utf-8")
    request = Request(
        CDSE_TOKEN_URL,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "User-Agent": USER_AGENT,
        },
    )
    token_open = urlopen_fn or build_cdse_opener().open
    payload = _open_json(request, urlopen_fn=token_open)
    token = payload.get("access_token")
    if not isinstance(token, str) or not token:
        raise AcquisitionError("CDSE_ACCESS_TOKEN_MISSING")
    return token


def safe_endpoint(url: str) -> str:
    parts = urlsplit(url)
    if parts.scheme.lower() != "https" or not parts.hostname:
        raise AcquisitionError("FINAL_ENDPOINT_NOT_HTTPS")
    return f"https://{parts.hostname}{parts.path}"


def classify_transfer_failure(error: AcquisitionError) -> str:
    """Classify a provider failure without turning an unknown failure into a retry.

    Authentication, authorization, missing-object, and quota responses are
    explicitly terminal.  Every other 4xx, redirects surfaced as status
    failures, malformed status detail, local I/O failure, and unknown reason
    also fail closed.  Only transport failures, HTTP 408, and HTTP 5xx are
    retryable.
    """

    if not isinstance(error, AcquisitionError):
        raise TypeError("error must be an AcquisitionError")
    if error.reason_code in RETRYABLE_TRANSFER_REASONS:
        return "RETRYABLE_TRANSPORT"
    if error.reason_code not in HTTP_STATUS_REASON_CODES:
        return "NONRETRYABLE"
    try:
        status = int(error.detail or "")
    except ValueError:
        return "NONRETRYABLE"
    if status in NONRETRYABLE_HTTP_STATUSES:
        return "NONRETRYABLE_HTTP_STATUS"
    if status == 408 or 500 <= status <= 599:
        return "RETRYABLE_HTTP_STATUS"
    return "NONRETRYABLE_HTTP_STATUS"


def _part_path(target: Path, suffix: str = ".part", prefix: str = "") -> Path:
    if not suffix.startswith(".") or suffix in {".", ".."} or any(
        separator in suffix for separator in ("/", "\\")
    ):
        raise AcquisitionError("PART_FILE_SUFFIX_INVALID")
    if prefix in {".", ".."} or any(separator in prefix for separator in ("/", "\\")):
        raise AcquisitionError("PART_FILE_PREFIX_INVALID")
    return target.with_name(f"{prefix}{target.name}{suffix}")


def _validate_part_magic(magic: bytes, contract: AssetContract) -> None:
    if contract.container == "hdf5" and magic != HDF5_MAGIC:
        raise AcquisitionError("DOWNLOADED_HDF5_SIGNATURE_MISSING", role=contract.role)
    if contract.container == "zip-safe" and not any(magic.startswith(prefix) for prefix in ZIP_MAGICS):
        raise AcquisitionError("DOWNLOADED_ZIP_SIGNATURE_MISSING", role=contract.role)


def _assert_part_file_stat(observed: os.stat_result, *, role: str) -> None:
    if not stat.S_ISREG(observed.st_mode):
        raise AcquisitionError("PART_FILE_NOT_REGULAR", role=role)
    if observed.st_nlink != 1:
        raise AcquisitionError("PART_FILE_MULTILINK_NOT_ALLOWED", role=role)


def _assert_part_path_identity(
    part: Path,
    opened: os.stat_result,
    *,
    role: str,
) -> None:
    if _is_link_like(part):
        raise AcquisitionError("PART_FILE_LINK_NOT_ALLOWED", role=role)
    try:
        observed = part.lstat()
    except OSError as error:
        raise AcquisitionError(
            "PART_FILE_PATH_IDENTITY_MISSING",
            role=role,
            detail=type(error).__name__,
        ) from None
    _assert_part_file_stat(observed, role=role)
    if not os.path.samestat(opened, observed):
        raise AcquisitionError("PART_FILE_PATH_IDENTITY_MISMATCH", role=role)


def _open_part_descriptor(part: Path, *, role: str) -> tuple[int, os.stat_result]:
    """Exclusively create or safely reopen one resumable partial file."""

    present = os.path.lexists(part)
    prior: os.stat_result | None = None
    if present:
        if _is_link_like(part):
            raise AcquisitionError("PART_FILE_LINK_NOT_ALLOWED", role=role)
        prior = part.lstat()
        _assert_part_file_stat(prior, role=role)

    flags = (
        os.O_RDWR
        | getattr(os, "O_BINARY", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    if not present:
        flags |= os.O_CREAT | os.O_EXCL
    try:
        descriptor = os.open(part, flags, 0o600)
    except FileExistsError:
        raise AcquisitionError("PART_FILE_RACE_CREATED", role=role) from None
    except OSError as error:
        raise AcquisitionError(
            "PART_FILE_OPEN_FAILED",
            role=role,
            detail=type(error).__name__,
        ) from None
    try:
        opened = os.fstat(descriptor)
        _assert_part_file_stat(opened, role=role)
        if prior is not None and not os.path.samestat(prior, opened):
            raise AcquisitionError("PART_FILE_OPEN_IDENTITY_MISMATCH", role=role)
        _assert_part_path_identity(part, opened, role=role)
    except BaseException:
        os.close(descriptor)
        raise
    return descriptor, opened


def _unlink_part_if_same(part: Path, opened: os.stat_result) -> None:
    try:
        observed = part.lstat()
        if stat.S_ISREG(observed.st_mode) and os.path.samestat(opened, observed):
            part.unlink()
    except OSError:
        return


def stream_asset(
    contract: AssetContract,
    quarantine: Path,
    *,
    opener: Any,
    headers: dict[str, str] | None = None,
    timeout_seconds: float = 120,
    progress: Callable[[str, int, int], None] | None = None,
    part_suffix: str = ".part",
    part_prefix: str = "",
) -> dict[str, Any]:
    if _is_link_like(quarantine):
        raise AcquisitionError("QUARANTINE_LINK_NOT_ALLOWED")
    quarantine.mkdir(parents=True, exist_ok=True)
    if _is_link_like(quarantine) or not quarantine.is_dir():
        raise AcquisitionError("QUARANTINE_LINK_NOT_ALLOWED")
    target = quarantine / contract.expected_filename
    part = _part_path(target, part_suffix, part_prefix)
    if os.path.lexists(target):
        if _is_link_like(target):
            raise AcquisitionError("EXISTING_QUARANTINE_ASSET_LINK_NOT_ALLOWED", role=contract.role)
        observation = inspect_asset(quarantine, contract)
        if observation["accepted"]:
            return {
                "role": contract.role,
                "status": "REUSED_VERIFIED_QUARANTINE_ASSET",
                "bytes": observation["observed_bytes"],
                "resumed_from_bytes": observation["observed_bytes"],
                "safe_final_endpoint": None,
            }
        raise AcquisitionError("EXISTING_QUARANTINE_ASSET_INVALID", role=contract.role)
    descriptor, opened_identity = _open_part_descriptor(part, role=contract.role)
    offset = opened_identity.st_size
    if offset > contract.expected_size_bytes:
        os.close(descriptor)
        _unlink_part_if_same(part, opened_identity)
        raise AcquisitionError("PART_FILE_OVERSIZED", role=contract.role)
    request_headers = {"Accept": "application/octet-stream", "User-Agent": USER_AGENT}
    request_headers.update(headers or {})
    if offset:
        request_headers["Range"] = f"bytes={offset}-"
    request = Request(contract.stable_route, headers=request_headers)

    delete_part_on_failure = False
    try:
        with os.fdopen(descriptor, "r+b") as handle:
            try:
                response = opener.open(request, timeout=timeout_seconds)
            except AcquisitionError:
                raise
            except HTTPError as error:
                if error.code == 408 or 500 <= error.code <= 599:
                    # Preserve the legacy bounded-retry contract while retaining the
                    # exact safe status needed to audit the attempt.
                    raise AcquisitionError(
                        "DOWNLOAD_REQUEST_FAILED",
                        role=contract.role,
                        detail=f"HTTPError:{error.code}",
                    ) from None
                raise AcquisitionError(
                    "DOWNLOAD_HTTP_STATUS_REJECTED",
                    role=contract.role,
                    detail=str(error.code),
                ) from None
            except (URLError, TimeoutError, OSError) as error:
                raise AcquisitionError(
                    "DOWNLOAD_REQUEST_FAILED",
                    role=contract.role,
                    detail=type(error).__name__,
                ) from None

            with response:
                status = getattr(response, "status", None)
                if status is None:
                    status = response.getcode()
                if status not in (200, 206):
                    raise AcquisitionError(
                        "DOWNLOAD_HTTP_STATUS_REJECTED",
                        role=contract.role,
                        detail=str(status),
                    )
                content_type = (response.headers.get("Content-Type") or "").lower()
                if content_type.startswith("text/") or "html" in content_type:
                    raise AcquisitionError("DOWNLOAD_TEXT_RESPONSE_REJECTED", role=contract.role)
                effective_offset = 0
                if offset and status == 206:
                    content_range = response.headers.get("Content-Range") or ""
                    if not content_range.startswith(f"bytes {offset}-"):
                        raise AcquisitionError("RESUME_CONTENT_RANGE_MISMATCH", role=contract.role)
                    handle.seek(0, os.SEEK_END)
                    if handle.tell() != offset:
                        raise AcquisitionError("PART_FILE_RESUME_SIZE_CHANGED", role=contract.role)
                    effective_offset = offset
                else:
                    handle.seek(0)
                    handle.truncate(0)
                _assert_part_path_identity(part, opened_identity, role=contract.role)
                total = effective_offset
                next_progress = total + 64 * CHUNK_BYTES
                while True:
                    try:
                        chunk = response.read(CHUNK_BYTES)
                    except (URLError, TimeoutError, OSError) as error:
                        raise AcquisitionError(
                            "DOWNLOAD_STREAM_FAILED",
                            role=contract.role,
                            detail=type(error).__name__,
                        ) from None
                    if not chunk:
                        break
                    try:
                        written = handle.write(chunk)
                    except OSError as error:
                        raise AcquisitionError(
                            "DOWNLOAD_WRITE_FAILED",
                            role=contract.role,
                            detail=type(error).__name__,
                        ) from None
                    if written != len(chunk):
                        raise AcquisitionError("DOWNLOAD_SHORT_WRITE", role=contract.role)
                    total += len(chunk)
                    if total > contract.expected_size_bytes:
                        delete_part_on_failure = True
                        raise AcquisitionError("DOWNLOAD_EXCEEDS_EXPECTED_SIZE", role=contract.role)
                    if progress and total >= next_progress:
                        progress(contract.role, total, contract.expected_size_bytes)
                        next_progress = total + 64 * CHUNK_BYTES
                handle.flush()
                os.fsync(handle.fileno())
                final_endpoint = safe_endpoint(response.geturl())

            final_descriptor_state = os.fstat(handle.fileno())
            _assert_part_file_stat(final_descriptor_state, role=contract.role)
            if not os.path.samestat(opened_identity, final_descriptor_state):
                raise AcquisitionError("PART_FILE_DESCRIPTOR_IDENTITY_MISMATCH", role=contract.role)
            observed_size = final_descriptor_state.st_size
            if observed_size < contract.expected_size_bytes:
                raise AcquisitionError(
                    "DOWNLOAD_EARLY_EOF",
                    role=contract.role,
                    detail=f"observed={observed_size},expected={contract.expected_size_bytes}",
                )
            if observed_size != contract.expected_size_bytes:
                raise AcquisitionError(
                    "DOWNLOAD_SIZE_MISMATCH",
                    role=contract.role,
                    detail=f"observed={observed_size},expected={contract.expected_size_bytes}",
                )
            handle.seek(0)
            try:
                _validate_part_magic(handle.read(8), contract)
            except AcquisitionError:
                delete_part_on_failure = True
                raise
            _assert_part_path_identity(part, opened_identity, role=contract.role)
    except AcquisitionError:
        if delete_part_on_failure:
            _unlink_part_if_same(part, opened_identity)
        raise
    except TimeoutError as error:
        raise AcquisitionError("DOWNLOAD_STREAM_FAILED", role=contract.role, detail=type(error).__name__) from None
    except OSError as error:
        raise AcquisitionError("DOWNLOAD_WRITE_FAILED", role=contract.role, detail=type(error).__name__) from None

    _assert_part_path_identity(part, opened_identity, role=contract.role)
    if os.path.lexists(target):
        raise AcquisitionError("FINAL_ASSET_ALREADY_EXISTS", role=contract.role)
    try:
        _rename_path_no_overwrite(part, target)
    except FileExistsError:
        raise AcquisitionError("FINAL_ASSET_RACE_CREATED", role=contract.role) from None
    except OSError as error:
        raise AcquisitionError(
            "FINAL_ASSET_NO_REPLACE_FAILED",
            role=contract.role,
            detail=type(error).__name__,
        ) from None
    if os.path.lexists(part):
        raise AcquisitionError("PART_FILE_REMAINED_AFTER_FINALIZATION", role=contract.role)
    if _is_link_like(target):
        raise AcquisitionError("FINAL_ASSET_LINK_NOT_ALLOWED", role=contract.role)
    finalized = target.lstat()
    if not stat.S_ISREG(finalized.st_mode):
        raise AcquisitionError("FINAL_ASSET_NOT_REGULAR", role=contract.role)
    if finalized.st_nlink != 1:
        raise AcquisitionError("FINAL_ASSET_MULTILINK_NOT_ALLOWED", role=contract.role)
    if not os.path.samestat(opened_identity, finalized):
        raise AcquisitionError("FINAL_ASSET_IDENTITY_MISMATCH", role=contract.role)
    if progress:
        progress(contract.role, contract.expected_size_bytes, contract.expected_size_bytes)
    return {
        "role": contract.role,
        "status": "DOWNLOADED",
        "bytes": contract.expected_size_bytes,
        "resumed_from_bytes": effective_offset,
        "safe_final_endpoint": final_endpoint,
    }


def stream_cdse_asset_with_retries(
    contract: AssetContract,
    quarantine: Path,
    *,
    username: str,
    password: str,
    max_attempts: int = MAX_BOUNDED_TRANSFER_ATTEMPTS,
    timeout_seconds: float = 120,
    progress: Callable[[str, int, int], None] | None = None,
    part_suffix: str = ".part",
    part_prefix: str = "",
    token_request_fn: Callable[[str, str], str] = request_cdse_access_token,
    opener_factory: Callable[[], Any] = build_cdse_opener,
    stream_fn: Callable[..., dict[str, Any]] = stream_asset,
) -> dict[str, Any]:
    """Download one exact CDSE asset with bounded, fresh-token retries."""

    if isinstance(max_attempts, bool) or not isinstance(max_attempts, int):
        raise AcquisitionError("TRANSFER_ATTEMPT_LIMIT_INVALID")
    if not 1 <= max_attempts <= MAX_BOUNDED_TRANSFER_ATTEMPTS:
        raise AcquisitionError(
            "TRANSFER_ATTEMPT_LIMIT_INVALID",
            detail=f"allowed=1-{MAX_BOUNDED_TRANSFER_ATTEMPTS}",
        )
    completed_target = quarantine / contract.expected_filename
    if os.path.lexists(completed_target):
        raise AcquisitionError(
            "PRIOR_COMPLETED_QUARANTINE_ASSET_NOT_ALLOWED",
            role=contract.role,
        )

    for attempt in range(1, max_attempts + 1):
        token: str | None = None
        try:
            token = token_request_fn(username, password)
            result = stream_fn(
                contract,
                quarantine,
                opener=opener_factory(),
                headers={"Authorization": f"Bearer {token}"},
                timeout_seconds=timeout_seconds,
                progress=progress,
                part_suffix=part_suffix,
                part_prefix=part_prefix,
            )
        except AcquisitionError as error:
            if classify_transfer_failure(error).startswith("RETRYABLE_") and attempt < max_attempts:
                continue
            raise
        finally:
            token = None
        result = dict(result)
        result["attempt_count"] = attempt
        return result

    raise AcquisitionError("TRANSFER_ATTEMPTS_EXHAUSTED", role=contract.role)


def _validate_working_entries(quarantine: Path, contracts: Iterable[AssetContract]) -> None:
    if not quarantine.exists():
        return
    expected: set[str] = set()
    for contract in contracts:
        expected.add(contract.expected_filename)
        expected.add(f"{contract.expected_filename}.part")
    unexpected = sorted(entry.name for entry in quarantine.iterdir() if entry.name not in expected)
    if unexpected:
        raise AcquisitionError("UNEXPECTED_ACQUISITION_WORKING_ENTRY", detail=",".join(unexpected))


def _rename_path_no_overwrite(source: Path, destination: Path) -> None:
    """Atomically rename a file or directory without replacing the target."""

    if os.name == "nt":
        # Windows rename is atomic on one volume and never replaces an existing
        # destination.  os.replace must not be used for custody promotion.
        os.rename(source, destination)
        return
    if sys.platform.startswith("linux"):
        try:
            renameat2 = ctypes.CDLL(None, use_errno=True).renameat2
        except AttributeError as error:
            raise OSError(
                errno.ENOTSUP,
                "atomic no-replace directory rename is unavailable",
            ) from error
        renameat2.argtypes = (
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_uint,
        )
        renameat2.restype = ctypes.c_int
        result = renameat2(
            -100,  # AT_FDCWD
            os.fsencode(source),
            -100,
            os.fsencode(destination),
            1,  # RENAME_NOREPLACE
        )
        if result == 0:
            return
        code = ctypes.get_errno()
        if code in {errno.EEXIST, errno.ENOTEMPTY}:
            raise FileExistsError(code, os.strerror(code), destination)
        raise OSError(code, os.strerror(code), destination)
    raise OSError(
        errno.ENOTSUP,
        "atomic no-replace path rename is unsupported on this platform",
    )


def _rename_directory_no_overwrite(source: Path, destination: Path) -> None:
    """Backward-compatible name for the path-level no-replace primitive."""

    _rename_path_no_overwrite(source, destination)


def promote_quarantine_no_overwrite(
    quarantine: Path,
    destination: Path,
    contracts: Iterable[AssetContract],
    *,
    generated_at_utc: str,
    run_id: str,
    synthetic_fixture: bool,
    contract_validator: ContractValidator = validate_contract_set,
    contract_version: str = PAIRED_INTAKE_CONTRACT_VERSION,
) -> dict[str, Any]:
    """Promote a complete package atomically without a replacement race."""

    items = list(contracts)
    evaluation = evaluate_quarantine(
        quarantine,
        items,
        contract_validator=contract_validator,
    )
    if not evaluation["accepted_for_atomic_promotion"]:
        raise ValueError("quarantine failed the paired-intake contract")
    if os.path.lexists(destination):
        raise FileExistsError(f"destination already exists: {destination.name}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if _is_link_like(destination.parent):
        raise OSError("destination parent must not be a filesystem link or junction")
    if quarantine.stat().st_dev != destination.parent.stat().st_dev:
        raise OSError("quarantine and destination must be on the same filesystem")

    registration = {
        "registration_schema_version": "0.2.0",
        "contract_version": contract_version,
        "contract_sha256": contract_digest(items),
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
    registration_path = quarantine / ".burnlens-registration.json"
    payload = (json.dumps(registration, indent=2) + "\n").encode("utf-8")
    manifest_created = False
    promoted = False
    try:
        with registration_path.open("xb") as handle:
            manifest_created = True
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        if registration_path.read_bytes() != payload:
            raise OSError("registration manifest readback mismatch")
        _rename_path_no_overwrite(quarantine, destination)
        promoted = True
        if os.path.lexists(quarantine):
            raise OSError("quarantine remained after promotion")
        if not destination.is_dir() or _is_link_like(destination):
            raise OSError("promoted destination is not a regular directory")
    finally:
        if manifest_created and not promoted and quarantine.is_dir():
            registration_path.unlink(missing_ok=True)
    return registration


def acquire_exact_package(
    *,
    credentials: ProviderCredentials,
    quarantine: Path,
    raw_parent: Path,
    generated_at_utc: str,
    run_id: str,
    metadata_snapshot: dict[str, Any],
    progress: Callable[[str, int, int], None] | None = None,
) -> dict[str, Any]:
    reasons = validate_metadata_snapshot(metadata_snapshot)
    if reasons:
        raise AcquisitionError("PUBLIC_METADATA_DRIFT", detail=",".join(reasons))
    destination = raw_parent / PACKAGE_ID
    if destination.exists():
        verification = verify_registered_package(destination, EXACT_CONTRACTS)
        if not verification["accepted_as_unchanged_registered_package"]:
            raise AcquisitionError("EXISTING_REGISTERED_PACKAGE_INVALID")
        return {
            "decision": "REUSED_VERIFIED_REGISTERED_PACKAGE",
            "credentials_exercised": False,
            "metadata_snapshot": metadata_snapshot,
            "downloads": [],
            "registration": None,
            "verification": verification,
        }

    quarantine.parent.mkdir(parents=True, exist_ok=True)
    raw_parent.mkdir(parents=True, exist_ok=True)
    _validate_working_entries(quarantine, EXACT_CONTRACTS)
    earthdata_opener = build_earthdata_opener(
        credentials.earthdata_username,
        credentials.earthdata_password,
    )
    by_role = {item.role: item for item in EXACT_CONTRACTS}
    order = ("viirs-active-fire", "viirs-geolocation", "sentinel-2-l2a")
    downloads: list[dict[str, Any]] = []
    for role in order:
        contract = by_role[role]
        if role == "sentinel-2-l2a":
            token = request_cdse_access_token(credentials.cdse_username, credentials.cdse_password)
            downloads.append(
                stream_asset(
                    contract,
                    quarantine,
                    opener=build_cdse_opener(),
                    headers={"Authorization": f"Bearer {token}"},
                    progress=progress,
                )
            )
            token = ""
        else:
            downloads.append(
                stream_asset(
                    contract,
                    quarantine,
                    opener=earthdata_opener,
                    progress=progress,
                )
            )

    registration = promote_quarantine_no_overwrite(
        quarantine,
        destination,
        EXACT_CONTRACTS,
        generated_at_utc=generated_at_utc,
        run_id=run_id,
        synthetic_fixture=False,
    )
    verification = verify_registered_package(destination, EXACT_CONTRACTS)
    if not verification["accepted_as_unchanged_registered_package"]:
        raise AcquisitionError("POST_PROMOTION_VERIFICATION_FAILED")
    return {
        "decision": "REGISTERED_EXACT_PROVIDER_PACKAGE",
        "credentials_exercised": True,
        "metadata_snapshot": metadata_snapshot,
        "downloads": downloads,
        "registration": registration,
        "verification": verification,
    }


def _absolute_lexical_path(path: Path) -> Path:
    """Make a path absolute without following filesystem indirection."""

    return Path(os.path.abspath(os.fspath(path)))


def _assert_no_link_like_path_components(path: Path) -> None:
    """Reject every existing symlink or junction from the anchor to ``path``."""

    lexical_path = _absolute_lexical_path(path)
    for component in (*reversed(lexical_path.parents), lexical_path):
        if os.path.lexists(component) and _is_link_like(component):
            raise AcquisitionError("PRIVATE_STATE_LINK_NOT_ALLOWED")


def _assert_private_state_contained(repo_root: Path, path: Path) -> None:
    """Require both lexical and resolved state paths to remain in one worktree."""

    lexical_root = _absolute_lexical_path(repo_root)
    lexical_path = _absolute_lexical_path(path)
    try:
        lexical_path.relative_to(lexical_root)
    except ValueError:
        raise AcquisitionError("PRIVATE_STATE_OUTSIDE_REPOSITORY") from None

    resolved_root = lexical_root.resolve(strict=False)
    for resolved_candidate in (
        lexical_path.parent.resolve(strict=False),
        lexical_path.resolve(strict=False),
    ):
        try:
            resolved_candidate.relative_to(resolved_root)
        except ValueError:
            raise AcquisitionError("PRIVATE_STATE_OUTSIDE_REPOSITORY") from None


def _private_state_repository_root(path: Path, repo_root: Path | None) -> Path | None:
    """Return the lexical containing worktree, or ``None`` outside Git.

    Worktree discovery deliberately happens before resolving the requested
    path.  Otherwise a repository-local symlink to an external directory can
    make a private state path appear to be an ordinary non-repository path.
    """

    lexical_path = _absolute_lexical_path(path)
    _assert_no_link_like_path_components(lexical_path)
    if repo_root is not None:
        candidate = _absolute_lexical_path(repo_root)
        _assert_no_link_like_path_components(candidate)
        if not os.path.lexists(candidate / ".git"):
            raise AcquisitionError("PRIVATE_STATE_REPOSITORY_INVALID")
        _assert_private_state_contained(candidate, lexical_path)
    else:
        candidate = next(
            (
                item
                for item in (lexical_path.parent, *lexical_path.parent.parents)
                if os.path.lexists(item / ".git")
            ),
            None,
        )
        if candidate is None:
            # A path lexically outside every Git worktree cannot be committed.
            # This preserves isolated TemporaryDirectory callers while the
            # link checks above still prohibit indirect external writes.
            return None
        _assert_private_state_contained(candidate, lexical_path)

    try:
        result = subprocess.run(
            ["git", "-C", str(candidate), "rev-parse", "--show-toplevel"],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as error:
        raise AcquisitionError(
            "PRIVATE_STATE_GIT_VERIFICATION_FAILED",
            detail=type(error).__name__,
        ) from None
    if result.returncode != 0:
        raise AcquisitionError("PRIVATE_STATE_REPOSITORY_INVALID")
    observed_root = _absolute_lexical_path(Path(result.stdout.strip()))
    if observed_root.resolve(strict=False) != candidate.resolve(strict=False):
        raise AcquisitionError("PRIVATE_STATE_REPOSITORY_IDENTITY_MISMATCH")
    _assert_no_link_like_path_components(lexical_path)
    _assert_private_state_contained(observed_root, lexical_path)
    return observed_root


def _assert_private_state_ignored_untracked(repo_root: Path, path: Path) -> None:
    try:
        relative = _absolute_lexical_path(path).relative_to(
            _absolute_lexical_path(repo_root)
        ).as_posix()
    except ValueError:
        raise AcquisitionError("PRIVATE_STATE_OUTSIDE_REPOSITORY") from None
    try:
        ignored = subprocess.run(
            [
                "git",
                "-C",
                str(repo_root),
                "check-ignore",
                "--quiet",
                "--no-index",
                "--",
                relative,
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        tracked = subprocess.run(
            [
                "git",
                "-C",
                str(repo_root),
                "ls-files",
                "--error-unmatch",
                "--",
                relative,
            ],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as error:
        raise AcquisitionError(
            "PRIVATE_STATE_GIT_VERIFICATION_FAILED",
            detail=type(error).__name__,
        ) from None
    if ignored.returncode == 1:
        raise AcquisitionError("PRIVATE_STATE_NOT_IGNORED")
    if ignored.returncode != 0:
        raise AcquisitionError("PRIVATE_STATE_GIT_VERIFICATION_FAILED")
    if tracked.returncode == 0:
        raise AcquisitionError("PRIVATE_STATE_TRACKED")
    if tracked.returncode != 1:
        raise AcquisitionError("PRIVATE_STATE_GIT_VERIFICATION_FAILED")


def _assert_private_state_path_safety(
    path: Path,
    repository: Path | None,
) -> None:
    _assert_no_link_like_path_components(path)
    if repository is not None:
        _assert_private_state_contained(repository, path)


def _assert_private_state_file_stat(observed: os.stat_result) -> None:
    if not stat.S_ISREG(observed.st_mode):
        raise AcquisitionError("PRIVATE_STATE_NOT_REGULAR_FILE")
    if observed.st_nlink != 1:
        raise AcquisitionError("PRIVATE_STATE_MULTILINK_NOT_ALLOWED")


def _assert_private_state_path_identity(
    path: Path,
    opened: os.stat_result,
) -> None:
    if _is_link_like(path):
        raise AcquisitionError("PRIVATE_STATE_LINK_NOT_ALLOWED")
    observed = path.lstat()
    _assert_private_state_file_stat(observed)
    if not os.path.samestat(opened, observed):
        raise AcquisitionError("PRIVATE_STATE_PATH_IDENTITY_MISMATCH")


def _read_private_state_from_handle(handle: Any) -> bytes:
    handle.seek(0)
    return handle.read()


def _fsync_private_state_parent(parent: Path) -> bool:
    """Persist the directory entry on POSIX; report unsupported Windows honestly."""

    if os.name != "posix":
        return False
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(parent, flags)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
    except OSError as error:
        raise AcquisitionError(
            "PRIVATE_STATE_DIRECTORY_FSYNC_FAILED",
            detail=type(error).__name__,
        ) from None
    return True


def _remove_created_private_state(path: Path, opened: os.stat_result | None) -> None:
    """Remove only the same inode this transaction created."""

    if opened is None:
        return
    try:
        observed = path.lstat()
        if stat.S_ISREG(observed.st_mode) and os.path.samestat(opened, observed):
            path.unlink()
    except OSError:
        # Never risk unlinking a path that no longer proves its identity merely
        # to hide the original fail-closed write error.
        return


def write_private_state(
    path: Path,
    state: dict[str, Any],
    *,
    repo_root: Path | None = None,
) -> None:
    """Write exact private state once, then fsync and read it back.

    Repository-local output must be both ignored and untracked.  Registration
    manifests have a separately verified, tightly bounded OneDrive link-count
    exception; private state deliberately does not inherit that exception.
    """

    path = _absolute_lexical_path(Path(path))
    repository = _private_state_repository_root(path, repo_root)
    _assert_private_state_path_safety(path, repository)
    if repository is not None:
        _assert_private_state_ignored_untracked(repository, path)
    if os.path.lexists(path):
        raise AcquisitionError("PRIVATE_STATE_OVERWRITE_REFUSED")

    payload = (json.dumps(state, indent=2) + "\n").encode("utf-8")
    created = False
    opened_identity: os.stat_result | None = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        _assert_private_state_path_safety(path, repository)
        if repository is not None:
            _assert_private_state_ignored_untracked(repository, path)
        with path.open("x+b") as handle:
            created = True
            opened_identity = os.fstat(handle.fileno())
            _assert_private_state_file_stat(opened_identity)
            _assert_private_state_path_identity(path, opened_identity)
            _assert_private_state_path_safety(path, repository)
            written = handle.write(payload)
            if written != len(payload):
                raise AcquisitionError("PRIVATE_STATE_SHORT_WRITE")
            handle.flush()
            os.fsync(handle.fileno())
            observed_bytes = _read_private_state_from_handle(handle)
            if observed_bytes != payload:
                raise AcquisitionError("PRIVATE_STATE_READBACK_MISMATCH")
            final_descriptor_state = os.fstat(handle.fileno())
            _assert_private_state_file_stat(final_descriptor_state)
            if not os.path.samestat(opened_identity, final_descriptor_state):
                raise AcquisitionError("PRIVATE_STATE_DESCRIPTOR_IDENTITY_MISMATCH")
            _assert_private_state_path_safety(path, repository)
            _assert_private_state_path_identity(path, opened_identity)
            if repository is not None:
                _assert_private_state_ignored_untracked(repository, path)
            _fsync_private_state_parent(path.parent)
            _assert_private_state_path_safety(path, repository)
            _assert_private_state_path_identity(path, opened_identity)
    except FileExistsError:
        raise AcquisitionError("PRIVATE_STATE_OVERWRITE_REFUSED") from None
    except AcquisitionError:
        if created:
            _remove_created_private_state(path, opened_identity)
        raise
    except OSError as error:
        if created:
            _remove_created_private_state(path, opened_identity)
        raise AcquisitionError(
            "PRIVATE_STATE_WRITE_FAILED",
            detail=type(error).__name__,
        ) from None
