"""Secret-safe authenticated acquisition for the exact BurnLens provider package.

Credentials enter through short-lived child-process environment variables created
by the Windows DPAPI wrapper.  This module removes those variables immediately,
never logs secret-bearing URLs or headers, downloads only the frozen contracts,
and delegates registration to :mod:`burnlens.paired_intake`.
"""

from __future__ import annotations

from dataclasses import dataclass
from http.cookiejar import CookieJar
import io
import json
import os
from pathlib import Path
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
    EXACT_CONTRACTS,
    HDF5_MAGIC,
    PACKAGE_ID,
    ZIP_MAGICS,
    AssetContract,
    _is_link_like,
    inspect_asset,
    promote_quarantine,
    verify_registered_package,
)


SOFTWARE_VERSION = "0.4.0"
CHUNK_BYTES = 1024 * 1024
MAX_JSON_BYTES = 4 * 1024 * 1024
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
    except (HTTPError, URLError, TimeoutError, OSError) as error:
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


def _part_path(target: Path) -> Path:
    return target.with_name(f"{target.name}.part")


def _validate_part_magic(path: Path, contract: AssetContract) -> None:
    with path.open("rb") as handle:
        magic = handle.read(8)
    if contract.container == "hdf5" and magic != HDF5_MAGIC:
        path.unlink(missing_ok=True)
        raise AcquisitionError("DOWNLOADED_HDF5_SIGNATURE_MISSING", role=contract.role)
    if contract.container == "zip-safe" and not any(magic.startswith(prefix) for prefix in ZIP_MAGICS):
        path.unlink(missing_ok=True)
        raise AcquisitionError("DOWNLOADED_ZIP_SIGNATURE_MISSING", role=contract.role)


def stream_asset(
    contract: AssetContract,
    quarantine: Path,
    *,
    opener: Any,
    headers: dict[str, str] | None = None,
    timeout_seconds: float = 120,
    progress: Callable[[str, int, int], None] | None = None,
) -> dict[str, Any]:
    if _is_link_like(quarantine):
        raise AcquisitionError("QUARANTINE_LINK_NOT_ALLOWED")
    quarantine.mkdir(parents=True, exist_ok=True)
    target = quarantine / contract.expected_filename
    part = _part_path(target)
    if target.exists():
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
    if _is_link_like(part):
        raise AcquisitionError("PART_FILE_LINK_NOT_ALLOWED", role=contract.role)
    if part.exists() and part.stat().st_nlink != 1:
        raise AcquisitionError("PART_FILE_MULTILINK_NOT_ALLOWED", role=contract.role)

    offset = part.stat().st_size if part.exists() else 0
    if offset > contract.expected_size_bytes:
        part.unlink()
        raise AcquisitionError("PART_FILE_OVERSIZED", role=contract.role)
    request_headers = {"Accept": "application/octet-stream", "User-Agent": USER_AGENT}
    request_headers.update(headers or {})
    if offset:
        request_headers["Range"] = f"bytes={offset}-"
    request = Request(contract.stable_route, headers=request_headers)

    try:
        response = opener.open(request, timeout=timeout_seconds)
    except AcquisitionError:
        raise
    except (HTTPError, URLError, TimeoutError, OSError) as error:
        raise AcquisitionError("DOWNLOAD_REQUEST_FAILED", role=contract.role, detail=type(error).__name__) from None

    try:
        with response:
            status = getattr(response, "status", None)
            if status is None:
                status = response.getcode()
            if status not in (200, 206):
                raise AcquisitionError("DOWNLOAD_HTTP_STATUS_REJECTED", role=contract.role, detail=str(status))
            content_type = (response.headers.get("Content-Type") or "").lower()
            if content_type.startswith("text/") or "html" in content_type:
                raise AcquisitionError("DOWNLOAD_TEXT_RESPONSE_REJECTED", role=contract.role)
            mode = "wb"
            effective_offset = 0
            if offset and status == 206:
                content_range = response.headers.get("Content-Range") or ""
                if not content_range.startswith(f"bytes {offset}-"):
                    raise AcquisitionError("RESUME_CONTENT_RANGE_MISMATCH", role=contract.role)
                mode = "ab"
                effective_offset = offset
            total = effective_offset
            next_progress = total + 64 * CHUNK_BYTES
            with part.open(mode) as handle:
                while True:
                    chunk = response.read(CHUNK_BYTES)
                    if not chunk:
                        break
                    handle.write(chunk)
                    total += len(chunk)
                    if total > contract.expected_size_bytes:
                        handle.close()
                        part.unlink(missing_ok=True)
                        raise AcquisitionError("DOWNLOAD_EXCEEDS_EXPECTED_SIZE", role=contract.role)
                    if progress and total >= next_progress:
                        progress(contract.role, total, contract.expected_size_bytes)
                        next_progress = total + 64 * CHUNK_BYTES
                handle.flush()
                os.fsync(handle.fileno())
            final_endpoint = safe_endpoint(response.geturl())
    except AcquisitionError:
        raise
    except OSError as error:
        raise AcquisitionError("DOWNLOAD_WRITE_FAILED", role=contract.role, detail=type(error).__name__) from None

    if part.stat().st_size != contract.expected_size_bytes:
        raise AcquisitionError(
            "DOWNLOAD_SIZE_MISMATCH",
            role=contract.role,
            detail=f"observed={part.stat().st_size},expected={contract.expected_size_bytes}",
        )
    _validate_part_magic(part, contract)
    os.replace(part, target)
    if progress:
        progress(contract.role, contract.expected_size_bytes, contract.expected_size_bytes)
    return {
        "role": contract.role,
        "status": "DOWNLOADED",
        "bytes": contract.expected_size_bytes,
        "resumed_from_bytes": effective_offset,
        "safe_final_endpoint": final_endpoint,
    }


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

    registration = promote_quarantine(
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


def write_private_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
