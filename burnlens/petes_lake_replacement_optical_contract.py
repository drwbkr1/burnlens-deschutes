"""Fail-closed custody for the exact Petes Lake replacement post archive.

The original U02 pair and failed U03 source-fitness run are immutable evidence.
This module reopens the already registered pre scene, acquires only the exact
October 19 replacement post scene, and writes a separately bound custody report
that can authorize a new U03 source-fitness run.  It never rewrites the original
post archive or its custody report.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import subprocess
from typing import Any, Callable, Iterable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .cross_event_optical_contract import CdseCredentials
from .paired_intake import (
    AssetContract,
    evaluate_quarantine,
    validate_asset_contracts,
    verify_registered_package,
)
from .petes_lake_optical_contract import (
    CONTRACT_VERSION as ORIGINAL_CONTRACT_VERSION,
    PRE_CONTRACT,
)
from .provider_acquisition import (
    AcquisitionError,
    USER_AGENT,
    _open_json,
    promote_quarantine_no_overwrite,
    stream_cdse_asset_with_retries,
    write_private_state,
)


SOFTWARE_VERSION = "0.44.0"
UNIT_ID = "P2O4-T33-U03"
TASK_ISSUE = 521
EVENT_ID = "OR4396912190120230825"
EVENT_GROUP_ID = "event-petes-lake-2023"
SOURCE_RECORD_ID = "SOURCE-2026-030"
TERMS_REVIEW_ID = "TERMS-2026-026"
SELECTION_REPORT_ID = "PETES-LAKE-SOURCE-REMEDIATION-2026-001"
FAILED_SOURCE_FITNESS_REPORT_ID = "PETES-LAKE-SOURCE-FITNESS-2026-001"
ORIGINAL_CUSTODY_REPORT_ID = "PETES-LAKE-OPTICAL-CUSTODY-2026-001"
CONTRACT_VERSION = "petes-lake-optical-post-remediation-contract-v0.1.0"
PACKAGE_ID = "petes-lake-s2-optical-post-remediation-v0.2.0"
PAIR_ID = "petes-lake-s2-optical-remediation-pair-v0.1.0"
REPORT_ID = "PETES-LAKE-OPTICAL-REMEDIATION-CUSTODY-2026-001"
REPORT_SCHEMA_VERSION = "0.1.0"
REPOSITORY = "drwbkr1/burnlens-deschutes"
BRANCH = "codex/p2o4-t33-petes-lake-milestone"
GIT_BASE_COMMIT = "0d41942dc6c3c307a9a146a2d38fb816e038bb42"
SELECTION_EVIDENCE_COMMIT = "32c1b6761919ca9721edfe87b98d913f3a5dd23e"
ORIGINAL_CUSTODY_EVIDENCE_COMMIT = "11580b28e5b8dd4be0b68420d0baf096c95b7e9b"
PRODUCTION_RUN_DATE = "2026-07-21"
INITIAL_REVISION = "r001"
MAX_TRANSFER_ATTEMPTS = 5
TEMPORARY_SUFFIX = ".tmp"
TEMPORARY_PREFIX = "~$"
WARNING = (
    "Experimental BurnLens CV evidence. Not official wildfire information. "
    "Not emergency guidance. Not evacuation, routing, tactical, or "
    "incident-command support. Official sources govern."
)
ATTRIBUTION = "Contains modified Copernicus Sentinel data 2023, accessed through CDSE."

SOURCE_PATH = Path("records/phase-two/sources/SOURCE-2026-030.md")
TERMS_PATH = Path("records/phase-two/terms/TERMS-2026-026.md")
ORIGINAL_TERMS_PATH = Path("records/phase-two/terms/TERMS-2026-024.md")
SELECTION_REPORT_PATH = Path(
    "samples/cross-event/phase-two/petes-lake/"
    f"{SELECTION_REPORT_ID}.json"
)
FAILED_SOURCE_FITNESS_REPORT_PATH = Path(
    "samples/cross-event/phase-two/petes-lake/"
    f"{FAILED_SOURCE_FITNESS_REPORT_ID}.json"
)
ORIGINAL_CUSTODY_REPORT_PATH = Path(
    "samples/cross-event/phase-two/petes-lake/"
    f"{ORIGINAL_CUSTODY_REPORT_ID}.json"
)

BOUND_TRACKED_FILES: dict[Path, tuple[int, str, str]] = {
    SOURCE_PATH: (
        3_544,
        "8a79758b2059f1cf240963b28c86a1ac69edd27626652d16fcc7323bdc160b8d",
        "replacement source and timing decision",
    ),
    TERMS_PATH: (
        3_322,
        "abcfc1ac94b5f886131f46049c9e98ae503ea7e1b6a12bc87c8d6e26073888d9",
        "exact replacement archive terms decision",
    ),
    ORIGINAL_TERMS_PATH: (
        1_982,
        "31179a8ce2754da7e73248e0fe667fd9a928c38d759d2b5f47db918028559d61",
        "immutable original two-archive terms decision",
    ),
    SELECTION_REPORT_PATH: (
        10_127,
        "7fa82a61fa70d47364db29493700beedd60c9114a4b3a6d8ddbafdf77aecfc8c",
        "deterministic replacement selection",
    ),
    FAILED_SOURCE_FITNESS_REPORT_PATH: (
        56_285,
        "ac9befd021d71ff779ec56ddefc894f4e39b92e64e65c2c4afb815663d1ad443",
        "retained failed planned-pair evidence",
    ),
    ORIGINAL_CUSTODY_REPORT_PATH: (
        23_521,
        "46f72f7fa7dc3b6fc3f96f6023b0d7b14f6990bcef8945a878ae04600d2e571d",
        "immutable original pre/post custody evidence",
    ),
}

TERMS_SOURCES = (
    {
        "title": "CDSE Terms and Conditions",
        "url": "https://dataspace.copernicus.eu/terms-and-conditions",
        "bytes": 77_530,
        "sha256": "e17c490e30a0544880e0ead78dcc4f749409d8ca4de67f003b2823203f864948",
    },
    {
        "title": "Sentinel Data Legal Notice",
        "url": (
            "https://sentinels.copernicus.eu/documents/247904/690755/"
            "Sentinel_Data_Legal_Notice"
        ),
        "bytes": 115_881,
        "sha256": "fa2955ff48a1d82e77fc7296d63681670ecdb9d2811a0505ae60d0683b62fa64",
    },
)


def _replacement_contract() -> AssetContract:
    safe_name = "S2A_MSIL2A_20231019T190411_N0510_R013_T10TEP_20241107T024526.SAFE"
    provider_id = "31fa8699-175b-4fd7-91c3-dd727a1576f5"
    return AssetContract(
        role="optical-post-remediation",
        provider="Copernicus Data Space Ecosystem",
        source_record_id=SOURCE_RECORD_ID,
        provider_id=provider_id,
        native_id=safe_name,
        expected_filename=f"{safe_name}.zip",
        stable_route=(
            "https://download.dataspace.copernicus.eu/odata/v1/"
            f"Products({provider_id})/$value"
        ),
        expected_size_bytes=1_195_226_823,
        container="zip-safe",
        package_id=PACKAGE_ID,
        provider_md5="4cf05a073b4c67f5e92e052ed1eb32bc",
        provider_blake3=(
            "1b28f566aee5619ea9a48c8dd042f209194a40989ba4b54cfe4e14904a0ad878"
        ),
        expected_zip_root=safe_name,
    )


REPLACEMENT_POST_CONTRACT = _replacement_contract()
EXPECTED_METADATA = {
    "acquisition_utc": "2023-10-19T19:04:11.024000Z",
    "publication_utc": "2025-04-25T03:03:39.050779Z",
    "platform_serial_identifier": "A",
    "tile_id": "10TEP",
    "relative_orbit_number": 13,
    "processor_version": "05.10",
    "product_type": "S2MSI2A",
    "odata_cloud_cover_percent": 0.098782,
    "stac_cloud_cover_percent": 0.1,
    "stac_snow_cover_percent": 0.564076,
}
ORIGINAL_PRE_RUN_ID = "BL-2026-07-21-petes-lake-optical-pre-r001"
ORIGINAL_PRE_LOCAL_SHA256 = (
    "c5b6ededc5a264fcc617f2712093b847351c5b8ed78f2ea9ce0ebc3a33e1bc34"
)
_REVISION_PATTERN = re.compile(r"^r(?P<number>\d{3})$")
_REPLACEMENT_RUN_ID_PATTERN = re.compile(
    rf"^BL-{PRODUCTION_RUN_DATE}-petes-lake-optical-post-remediation-"
    r"r(?:00[1-9]|0[1-9]\d|[1-9]\d{2})$"
)


def validate_replacement_contracts(contracts: Iterable[AssetContract]) -> list[str]:
    """Accept only the one exact selected replacement archive."""

    items = list(contracts)
    reasons = validate_asset_contracts(items)
    if items != [REPLACEMENT_POST_CONTRACT]:
        reasons.append("PETES_LAKE_REPLACEMENT_SINGLETON_CONTRACT_MISMATCH")
    return list(dict.fromkeys(reasons))


def _metadata_url() -> str:
    return (
        "https://catalogue.dataspace.copernicus.eu/odata/v1/"
        f"Products({REPLACEMENT_POST_CONTRACT.provider_id})"
        "?$select=Id,Name,ContentLength,Online,Checksum,ContentDate,"
        "PublicationDate,S3Path,Attributes&$expand=Attributes"
    )


def _normalize_metadata(payload: dict[str, Any], *, observed_at_utc: str) -> dict[str, Any]:
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
    s3_path = payload.get("S3Path")
    return {
        "observed_at_utc": observed_at_utc,
        "live_refresh_performed": True,
        "source_record_id": SOURCE_RECORD_ID,
        "terms_review_id": TERMS_REVIEW_ID,
        "role": REPLACEMENT_POST_CONTRACT.role,
        "event_id": EVENT_ID,
        "event_group_id": EVENT_GROUP_ID,
        "provider_id": payload.get("Id"),
        "native_id": payload.get("Name"),
        "size_bytes": payload.get("ContentLength"),
        "online": payload.get("Online"),
        "acquisition_utc": content_date.get("Start"),
        "publication_utc": payload.get("PublicationDate"),
        "provider_checksums": checksums,
        "platform_serial_identifier": attributes.get("platformSerialIdentifier"),
        "tile_id": attributes.get("tileId"),
        "relative_orbit_number": attributes.get("relativeOrbitNumber"),
        "processor_version": attributes.get("processorVersion"),
        "product_type": attributes.get("productType"),
        "odata_cloud_cover_percent": attributes.get("cloudCover"),
        "stac_cloud_cover_percent": EXPECTED_METADATA["stac_cloud_cover_percent"],
        "stac_snow_cover_percent": EXPECTED_METADATA["stac_snow_cover_percent"],
        "s3_identity_suffix_verified_without_retaining_path": (
            isinstance(s3_path, str)
            and s3_path.endswith(f"/{REPLACEMENT_POST_CONTRACT.native_id}")
        ),
        "local_pixel_fitness": "not executed; replacement U03 source-fitness run required",
    }


def validate_replacement_metadata(snapshot: dict[str, Any]) -> list[str]:
    reasons = validate_replacement_contracts((REPLACEMENT_POST_CONTRACT,))
    expected = {
        "source_record_id": SOURCE_RECORD_ID,
        "terms_review_id": TERMS_REVIEW_ID,
        "role": REPLACEMENT_POST_CONTRACT.role,
        "event_id": EVENT_ID,
        "event_group_id": EVENT_GROUP_ID,
        "provider_id": REPLACEMENT_POST_CONTRACT.provider_id,
        "native_id": REPLACEMENT_POST_CONTRACT.native_id,
        "size_bytes": REPLACEMENT_POST_CONTRACT.expected_size_bytes,
        "online": True,
        "acquisition_utc": EXPECTED_METADATA["acquisition_utc"],
        "publication_utc": EXPECTED_METADATA["publication_utc"],
        "platform_serial_identifier": EXPECTED_METADATA["platform_serial_identifier"],
        "tile_id": EXPECTED_METADATA["tile_id"],
        "relative_orbit_number": EXPECTED_METADATA["relative_orbit_number"],
        "processor_version": EXPECTED_METADATA["processor_version"],
        "product_type": EXPECTED_METADATA["product_type"],
        "odata_cloud_cover_percent": EXPECTED_METADATA["odata_cloud_cover_percent"],
        "stac_cloud_cover_percent": EXPECTED_METADATA["stac_cloud_cover_percent"],
        "stac_snow_cover_percent": EXPECTED_METADATA["stac_snow_cover_percent"],
        "s3_identity_suffix_verified_without_retaining_path": True,
    }
    for name, value in expected.items():
        if snapshot.get(name) != value:
            reasons.append(f"REPLACEMENT_METADATA_{name.upper()}_MISMATCH")
    if snapshot.get("live_refresh_performed") is not True:
        reasons.append("REPLACEMENT_LIVE_METADATA_REFRESH_REQUIRED")
    if not isinstance(snapshot.get("observed_at_utc"), str) or not snapshot["observed_at_utc"]:
        reasons.append("REPLACEMENT_METADATA_OBSERVED_AT_MISSING")
    checksums = snapshot.get("provider_checksums") or {}
    if checksums.get("MD5") != REPLACEMENT_POST_CONTRACT.provider_md5:
        reasons.append("REPLACEMENT_METADATA_MD5_MISMATCH")
    if checksums.get("BLAKE3") != REPLACEMENT_POST_CONTRACT.provider_blake3:
        reasons.append("REPLACEMENT_METADATA_BLAKE3_MISMATCH")
    if "s3_path" in snapshot or "stable_route" in snapshot:
        reasons.append("REPLACEMENT_METADATA_PRIVATE_ROUTE_RETAINED")
    return list(dict.fromkeys(reasons))


def refresh_replacement_metadata(
    *,
    observed_at_utc: str,
    urlopen_fn: Callable[..., Any] = urlopen,
) -> dict[str, Any]:
    payload = _open_json(
        Request(
            _metadata_url(),
            headers={"Accept": "application/json", "User-Agent": USER_AGENT},
        ),
        urlopen_fn=urlopen_fn,
    )
    snapshot = _normalize_metadata(payload, observed_at_utc=observed_at_utc)
    reasons = validate_replacement_metadata(snapshot)
    if reasons:
        raise AcquisitionError("PETES_LAKE_REPLACEMENT_METADATA_DRIFT", detail=",".join(reasons))
    return snapshot


def _fetch_exact_public_bytes(
    source: dict[str, Any],
    *,
    urlopen_fn: Callable[..., Any] = urlopen,
) -> dict[str, Any]:
    request = Request(
        source["url"],
        headers={"Accept": "*/*", "User-Agent": USER_AGENT},
    )
    try:
        with urlopen_fn(request, timeout=60) as response:
            status = getattr(response, "status", None)
            if status is None:
                status = response.getcode()
            if status != 200:
                raise AcquisitionError(
                    "PETES_LAKE_REPLACEMENT_TERMS_HTTP_STATUS",
                    detail=str(status),
                )
            payload = response.read(int(source["bytes"]) + 1)
    except AcquisitionError:
        raise
    except HTTPError as error:
        raise AcquisitionError(
            "PETES_LAKE_REPLACEMENT_TERMS_HTTP_STATUS",
            detail=str(error.code),
        ) from None
    except (URLError, TimeoutError, OSError) as error:
        raise AcquisitionError(
            "PETES_LAKE_REPLACEMENT_TERMS_REQUEST_FAILED",
            detail=type(error).__name__,
        ) from None
    observed_sha = sha256(payload).hexdigest()
    if len(payload) != source["bytes"] or observed_sha != source["sha256"]:
        raise AcquisitionError(
            "PETES_LAKE_REPLACEMENT_TERMS_SOURCE_DRIFT",
            detail=str(source["title"]),
        )
    return {
        "title": source["title"],
        "url": source["url"],
        "bytes": len(payload),
        "sha256": observed_sha,
        "disposition": "exact-current-source-bytes-pass",
    }


def refresh_replacement_terms(
    *,
    observed_at_utc: str,
    urlopen_fn: Callable[..., Any] = urlopen,
) -> dict[str, Any]:
    sources = [
        _fetch_exact_public_bytes(source, urlopen_fn=urlopen_fn)
        for source in TERMS_SOURCES
    ]
    return {
        "terms_review_id": TERMS_REVIEW_ID,
        "observed_at_utc": observed_at_utc,
        "live_refresh_performed": True,
        "sources": sources,
        "decision": (
            "RESOLVED_FOR_ONE_EXACT_REPLACEMENT_SENTINEL_ARCHIVE, "
            "LOCAL_ANALYSIS, AND BOUNDED_DERIVED_EVIDENCE"
        ),
        "exact_authorized_provider_id": REPLACEMENT_POST_CONTRACT.provider_id,
        "native_provider_bytes_redistribution": False,
        "attribution": ATTRIBUTION,
    }


@dataclass(frozen=True)
class ReplacementOpticalRun:
    repository_root: Path
    generated_at_utc: str
    revision: str
    mode: str

    @classmethod
    def create(
        cls,
        *,
        repository_root: Path,
        generated_at_utc: str,
        revision: str,
        mode: str = "acquire",
    ) -> "ReplacementOpticalRun":
        if not generated_at_utc.endswith("Z"):
            raise ValueError("generated_at_utc must be an explicit UTC Z timestamp")
        try:
            parsed = datetime.fromisoformat(generated_at_utc[:-1] + "+00:00")
        except ValueError:
            raise ValueError("generated_at_utc must be ISO-8601") from None
        if parsed.tzinfo != timezone.utc:
            raise ValueError("generated_at_utc must be UTC")
        match = _REVISION_PATTERN.fullmatch(revision)
        if match is None or int(match.group("number")) == 0:
            raise ValueError("revision must be r001 through r999")
        if mode not in {"acquire", "finalize"}:
            raise ValueError("mode must be acquire or finalize")
        if mode == "acquire" and revision != INITIAL_REVISION:
            raise ValueError("the provider transaction is hard-bound to r001")
        if mode == "finalize" and int(match.group("number")) <= 1:
            raise ValueError("finalize remediation requires r002 or later")
        return cls(
            repository_root=repository_root.resolve(),
            generated_at_utc=generated_at_utc,
            revision=revision,
            mode=mode,
        )

    @property
    def original_pre_destination(self) -> Path:
        return (
            self.repository_root
            / "downloads"
            / "phase-two"
            / "raw"
            / "petes-lake-s2-optical-pre-v0.1.0"
        )

    @property
    def replacement_destination(self) -> Path:
        return (
            self.repository_root
            / "downloads"
            / "phase-two"
            / "raw"
            / PACKAGE_ID
        )

    @property
    def quarantine(self) -> Path:
        return (
            self.repository_root
            / "downloads"
            / "phase-two"
            / "quarantine"
            / UNIT_ID
            / f"petes-lake-optical-post-remediation-{self.revision}"
        )

    @property
    def run_state_parent(self) -> Path:
        return self.repository_root / "downloads" / "phase-two" / "runs" / UNIT_ID

    @property
    def transaction_run_id(self) -> str:
        return (
            f"BL-{PRODUCTION_RUN_DATE}-petes-lake-optical-post-remediation-"
            f"{self.revision}"
        )

    @property
    def aggregate_run_id(self) -> str:
        return (
            f"BL-{PRODUCTION_RUN_DATE}-petes-lake-optical-remediation-intake-"
            f"{self.revision}"
        )

    @property
    def transaction_state(self) -> Path:
        return self.run_state_parent / f"{self.transaction_run_id}.json"

    @property
    def aggregate_state(self) -> Path:
        return self.run_state_parent / f"{self.aggregate_run_id}.json"

    @property
    def tracked_report(self) -> Path:
        return (
            self.repository_root
            / "samples"
            / "cross-event"
            / "phase-two"
            / "petes-lake"
            / f"{REPORT_ID}.json"
        )


@dataclass(frozen=True)
class ReplacementTrace:
    git_source_commit: str
    remote_branch_commit: str
    branch: str
    bound_tracked_files: tuple[dict[str, Any], ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "repository": REPOSITORY,
            "git_source_commit": self.git_source_commit,
            "remote_branch_commit": self.remote_branch_commit,
            "branch": self.branch,
            "task_issue": TASK_ISSUE,
            "git_base_commit": GIT_BASE_COMMIT,
            "selection_evidence_commit": SELECTION_EVIDENCE_COMMIT,
            "original_custody_evidence_commit": ORIGINAL_CUSTODY_EVIDENCE_COMMIT,
            "bound_tracked_files": list(self.bound_tracked_files),
        }


@dataclass(frozen=True)
class ReplacementPreflight:
    trace: ReplacementTrace
    metadata_snapshot: dict[str, Any]
    terms_snapshot: dict[str, Any]
    original_pre_verification: dict[str, Any]


def _git(repository_root: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repository_root), *arguments],
        check=False,
        capture_output=True,
        text=True,
    )


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _path_present(path: Path) -> bool:
    is_junction = getattr(path, "is_junction", None)
    return path.exists() or path.is_symlink() or bool(is_junction and is_junction())


def _relative(run: ReplacementOpticalRun, path: Path) -> str:
    return path.relative_to(run.repository_root).as_posix()


def _now_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _canonical_json_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _without_observed_at(payload: dict[str, Any]) -> dict[str, Any]:
    comparable = dict(payload)
    comparable.pop("observed_at_utc", None)
    return comparable


def _tracked_bindings(repository_root: Path) -> tuple[dict[str, Any], ...]:
    bindings: list[dict[str, Any]] = []
    for relative, (expected_bytes, expected_sha, role) in BOUND_TRACKED_FILES.items():
        path = repository_root / relative
        if (
            not path.is_file()
            or path.stat().st_size != expected_bytes
            or _sha256_file(path) != expected_sha
        ):
            raise AcquisitionError(
                "PETES_LAKE_REPLACEMENT_TRACKED_BINDING_MISMATCH",
                detail=relative.as_posix(),
            )
        bindings.append(
            {
                "path": relative.as_posix(),
                "bytes": expected_bytes,
                "sha256": expected_sha,
                "role": role,
            }
        )
    return tuple(bindings)


def _validate_selection_report(repository_root: Path) -> None:
    try:
        payload = json.loads((repository_root / SELECTION_REPORT_PATH).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        raise AcquisitionError("PETES_LAKE_REPLACEMENT_SELECTION_REPORT_INVALID") from None
    selected = payload.get("selected_contract") if isinstance(payload, dict) else None
    if not isinstance(selected, dict):
        raise AcquisitionError("PETES_LAKE_REPLACEMENT_SELECTION_CONTRACT_MISSING")
    expected = {
        "provider_id": REPLACEMENT_POST_CONTRACT.provider_id,
        "native_id": REPLACEMENT_POST_CONTRACT.native_id.removesuffix(".SAFE"),
        "expected_filename": REPLACEMENT_POST_CONTRACT.expected_filename,
        "package_id": PACKAGE_ID,
        "role": REPLACEMENT_POST_CONTRACT.role,
        "size_bytes": REPLACEMENT_POST_CONTRACT.expected_size_bytes,
        "online": True,
        "acquisition_utc": EXPECTED_METADATA["acquisition_utc"],
        "publication_utc": EXPECTED_METADATA["publication_utc"],
        "provider_md5": REPLACEMENT_POST_CONTRACT.provider_md5,
        "provider_blake3": REPLACEMENT_POST_CONTRACT.provider_blake3,
        "platform_serial_identifier": EXPECTED_METADATA["platform_serial_identifier"],
        "tile_id": EXPECTED_METADATA["tile_id"],
        "relative_orbit_number": EXPECTED_METADATA["relative_orbit_number"],
        "processor_version": EXPECTED_METADATA["processor_version"],
        "product_type": EXPECTED_METADATA["product_type"],
        "odata_cloud_cover_percent": EXPECTED_METADATA["odata_cloud_cover_percent"],
        "stac_cloud_cover_percent": EXPECTED_METADATA["stac_cloud_cover_percent"],
        "stac_snow_cover_percent": EXPECTED_METADATA["stac_snow_cover_percent"],
        "s3_identity_verified_without_retaining_path": True,
    }
    mismatches = [name for name, value in expected.items() if selected.get(name) != value]
    if (
        payload.get("decision") != "SELECT_REPLACEMENT_POST_AUTHORIZE_CONTRACT_REVISION_ONLY"
        or mismatches
    ):
        raise AcquisitionError(
            "PETES_LAKE_REPLACEMENT_SELECTION_BINDING_MISMATCH",
            detail=",".join(mismatches) if mismatches else "decision",
        )


def _validate_original_pre(run: ReplacementOpticalRun) -> dict[str, Any]:
    verification = verify_registered_package(
        run.original_pre_destination,
        (PRE_CONTRACT,),
        contract_validator=lambda items: (
            [] if list(items) == [PRE_CONTRACT] else ["ORIGINAL_PRE_CONTRACT_MISMATCH"]
        ),
        contract_version=ORIGINAL_CONTRACT_VERSION,
        allow_multilink_registration_manifest=True,
    )
    registration = verification.get("registration") or {}
    assets = registration.get("assets") or []
    observed = assets[0] if len(assets) == 1 and isinstance(assets[0], dict) else {}
    reasons = []
    if verification.get("accepted_as_unchanged_registered_package") is not True:
        reasons.append("ORIGINAL_PRE_REGISTERED_PACKAGE_NOT_ACCEPTED")
    if verification.get("registration_manifest_link_count") != 1:
        reasons.append("ORIGINAL_PRE_REGISTRATION_MANIFEST_NOT_SINGLE_LINK")
    if registration.get("run_id") != ORIGINAL_PRE_RUN_ID:
        reasons.append("ORIGINAL_PRE_RUN_ID_MISMATCH")
    if observed.get("sha256") != ORIGINAL_PRE_LOCAL_SHA256:
        reasons.append("ORIGINAL_PRE_LOCAL_SHA256_MISMATCH")
    if observed.get("md5") != PRE_CONTRACT.provider_md5:
        reasons.append("ORIGINAL_PRE_LOCAL_MD5_MISMATCH")
    if observed.get("blake3") != PRE_CONTRACT.provider_blake3:
        reasons.append("ORIGINAL_PRE_LOCAL_BLAKE3_MISMATCH")
    for entry in run.original_pre_destination.iterdir() if run.original_pre_destination.is_dir() else ():
        if entry.is_symlink() or not entry.is_file() or entry.stat().st_nlink != 1:
            reasons.append(f"ORIGINAL_PRE_ENTRY_NOT_SINGLE_REGULAR_FILE:{entry.name}")
    if reasons:
        raise AcquisitionError(
            "PETES_LAKE_REPLACEMENT_ORIGINAL_PRE_VERIFICATION_FAILED",
            detail=",".join(reasons),
        )
    return {
        "package_id": PRE_CONTRACT.package_id,
        "role": PRE_CONTRACT.role,
        "destination_path": _relative(run, run.original_pre_destination),
        "registration_run_id": registration["run_id"],
        "registration_manifest_sha256": verification["registration_manifest_sha256"],
        "registration_manifest_link_count": verification["registration_manifest_link_count"],
        "asset": observed,
        "fresh_verification_decision": "pass",
        "provider_archive_request_performed": False,
    }


def _verify_private_path(run: ReplacementOpticalRun, path: Path) -> None:
    relative = _relative(run, path)
    ignored = _git(run.repository_root, "check-ignore", "--quiet", "--no-index", "--", relative)
    tracked = _git(run.repository_root, "ls-files", "--error-unmatch", "--", relative)
    if ignored.returncode != 0 or tracked.returncode != 1:
        raise AcquisitionError(
            "PETES_LAKE_REPLACEMENT_PRIVATE_PATH_GATE_FAILED",
            detail=relative,
        )


def _verify_report_path(run: ReplacementOpticalRun, *, existing_report: bool) -> None:
    relative = _relative(run, run.tracked_report)
    if _git(
        run.repository_root,
        "check-ignore",
        "--quiet",
        "--no-index",
        "--",
        relative,
    ).returncode != 1:
        raise AcquisitionError("PETES_LAKE_REPLACEMENT_TRACKED_REPORT_IGNORED")
    tracked = _git(run.repository_root, "ls-files", "--error-unmatch", "--", relative)
    if not existing_report and tracked.returncode != 1:
        raise AcquisitionError("PETES_LAKE_REPLACEMENT_TRACKED_REPORT_ALREADY_TRACKED")


def _assert_path_mode(run: ReplacementOpticalRun, *, existing_success_outputs: bool) -> None:
    if existing_success_outputs:
        required = (run.original_pre_destination, run.replacement_destination, run.aggregate_state, run.tracked_report)
        missing = [_relative(run, path) for path in required if not _path_present(path)]
        if missing:
            raise AcquisitionError(
                "PETES_LAKE_REPLACEMENT_SUCCESS_OUTPUTS_MISSING",
                detail=",".join(missing),
            )
        return
    if run.mode == "acquire":
        targets = (
            run.quarantine,
            run.replacement_destination,
            run.transaction_state,
            run.aggregate_state,
            run.tracked_report,
        )
    else:
        if not _path_present(run.replacement_destination):
            raise AcquisitionError("PETES_LAKE_REPLACEMENT_FINALIZE_PACKAGE_MISSING")
        targets = (run.quarantine, run.transaction_state, run.aggregate_state, run.tracked_report)
    present = [_relative(run, path) for path in targets if _path_present(path)]
    if present:
        raise AcquisitionError(
            "PETES_LAKE_REPLACEMENT_NO_OVERWRITE_TARGET_EXISTS",
            detail=",".join(present),
        )


def verify_replacement_repository_preflight(
    run: ReplacementOpticalRun,
    *,
    existing_success_outputs: bool = False,
    metadata_refresh_fn: Callable[..., dict[str, Any]] = refresh_replacement_metadata,
    terms_refresh_fn: Callable[..., dict[str, Any]] = refresh_replacement_terms,
    observed_at_fn: Callable[[], str] = _now_utc,
) -> ReplacementPreflight:
    """Pass every credential-free repository, terms, source, and custody gate."""

    root = run.repository_root
    top = _git(root, "rev-parse", "--show-toplevel")
    if top.returncode != 0 or Path(top.stdout.strip()).resolve() != root:
        raise AcquisitionError("PETES_LAKE_REPLACEMENT_REPOSITORY_ROOT_MISMATCH")
    branch = _git(root, "branch", "--show-current")
    if branch.returncode != 0 or branch.stdout.strip() != BRANCH:
        raise AcquisitionError("PETES_LAKE_REPLACEMENT_BRANCH_MISMATCH")
    origin = _git(root, "config", "--get", "remote.origin.url")
    normalized_origin = origin.stdout.strip().lower().replace("\\", "/")
    if origin.returncode != 0 or "drwbkr1/burnlens-deschutes" not in normalized_origin:
        raise AcquisitionError("PETES_LAKE_REPLACEMENT_ORIGIN_MISMATCH")

    head_result = _git(root, "rev-parse", "HEAD")
    head = head_result.stdout.strip()
    if head_result.returncode != 0 or re.fullmatch(r"[0-9a-f]{40}", head) is None:
        raise AcquisitionError("PETES_LAKE_REPLACEMENT_COMMITTED_HEAD_REQUIRED")
    status = _git(root, "status", "--porcelain=v1", "--untracked-files=all")
    observed_status = status.stdout.strip().replace("\\", "/")
    report_relative = _relative(run, run.tracked_report)
    allowed_status = f"?? {report_relative}" if existing_success_outputs else ""
    if status.returncode != 0 or observed_status not in {"", allowed_status}:
        raise AcquisitionError("PETES_LAKE_REPLACEMENT_WORKTREE_NOT_CLEAN")

    remote = _git(
        root,
        "-c",
        "credential.interactive=never",
        "ls-remote",
        "--heads",
        "origin",
        BRANCH,
    )
    remote_lines = [line.split() for line in remote.stdout.splitlines() if line.strip()]
    if (
        remote.returncode != 0
        or len(remote_lines) != 1
        or len(remote_lines[0]) != 2
        or remote_lines[0][0] != head
        or remote_lines[0][1] != f"refs/heads/{BRANCH}"
    ):
        raise AcquisitionError("PETES_LAKE_REPLACEMENT_REMOTE_HEAD_MISMATCH")

    for ancestor, reason in (
        (GIT_BASE_COMMIT, "PETES_LAKE_REPLACEMENT_BASE_NOT_ANCESTOR"),
        (SELECTION_EVIDENCE_COMMIT, "PETES_LAKE_REPLACEMENT_SELECTION_NOT_ANCESTOR"),
        (ORIGINAL_CUSTODY_EVIDENCE_COMMIT, "PETES_LAKE_REPLACEMENT_CUSTODY_NOT_ANCESTOR"),
    ):
        if _git(root, "merge-base", "--is-ancestor", ancestor, head).returncode != 0:
            raise AcquisitionError(reason)

    bindings = _tracked_bindings(root)
    _validate_selection_report(root)
    private_paths = {
        run.original_pre_destination,
        run.replacement_destination,
        run.quarantine,
        run.transaction_state,
        run.aggregate_state,
    }
    for path in sorted(private_paths, key=str):
        _verify_private_path(run, path)
    _verify_report_path(run, existing_report=existing_success_outputs)
    _assert_path_mode(run, existing_success_outputs=existing_success_outputs)

    original_pre = _validate_original_pre(run)
    terms_observed = observed_at_fn()
    terms_snapshot = terms_refresh_fn(observed_at_utc=terms_observed)
    metadata_observed = observed_at_fn()
    if metadata_observed == terms_observed:
        raise AcquisitionError("PETES_LAKE_REPLACEMENT_PREFLIGHT_TIMESTAMPS_NOT_DISTINCT")
    metadata_snapshot = metadata_refresh_fn(observed_at_utc=metadata_observed)
    metadata_reasons = validate_replacement_metadata(metadata_snapshot)
    if metadata_reasons:
        raise AcquisitionError(
            "PETES_LAKE_REPLACEMENT_METADATA_CONTRACT_REJECTED",
            detail=",".join(metadata_reasons),
        )
    trace = ReplacementTrace(
        git_source_commit=head,
        remote_branch_commit=remote_lines[0][0],
        branch=BRANCH,
        bound_tracked_files=bindings,
    )
    return ReplacementPreflight(
        trace=trace,
        metadata_snapshot=metadata_snapshot,
        terms_snapshot=terms_snapshot,
        original_pre_verification=original_pre,
    )


def _contract_summary() -> dict[str, Any]:
    contract = REPLACEMENT_POST_CONTRACT
    return {
        "role": contract.role,
        "provider": contract.provider,
        "source_record_id": contract.source_record_id,
        "provider_id": contract.provider_id,
        "native_id": contract.native_id,
        "selection_native_id": contract.native_id.removesuffix(".SAFE"),
        "expected_filename": contract.expected_filename,
        "expected_size_bytes": contract.expected_size_bytes,
        "package_id": contract.package_id,
        "provider_md5": contract.provider_md5,
        "provider_blake3": contract.provider_blake3,
        "expected_zip_root": contract.expected_zip_root,
    }


def _fresh_verify_replacement(run: ReplacementOpticalRun) -> dict[str, Any]:
    verification = verify_registered_package(
        run.replacement_destination,
        (REPLACEMENT_POST_CONTRACT,),
        contract_validator=validate_replacement_contracts,
        contract_version=CONTRACT_VERSION,
    )
    if verification.get("accepted_as_unchanged_registered_package") is not True:
        raise AcquisitionError("PETES_LAKE_REPLACEMENT_REGISTERED_PACKAGE_INVALID")
    if verification.get("registration_manifest_link_count") != 1:
        raise AcquisitionError("PETES_LAKE_REPLACEMENT_MANIFEST_NOT_SINGLE_LINK")
    for entry in run.replacement_destination.iterdir():
        if entry.is_symlink() or not entry.is_file() or entry.stat().st_nlink != 1:
            raise AcquisitionError(
                "PETES_LAKE_REPLACEMENT_ENTRY_NOT_SINGLE_REGULAR_FILE",
                detail=entry.name,
            )
    return verification


def _write_tracked_report_no_overwrite(
    run: ReplacementOpticalRun,
    payload: dict[str, Any],
) -> None:
    path = run.tracked_report
    path.parent.mkdir(parents=True, exist_ok=True)
    relative = _relative(run, path)
    if path.parent.is_symlink() or _path_present(path):
        raise AcquisitionError("PETES_LAKE_REPLACEMENT_TRACKED_REPORT_EXISTS")
    if (run.repository_root / ".git").exists():
        if _git(
            run.repository_root,
            "check-ignore",
            "--quiet",
            "--no-index",
            "--",
            relative,
        ).returncode != 1:
            raise AcquisitionError("PETES_LAKE_REPLACEMENT_TRACKED_REPORT_IGNORED")
        if _git(
            run.repository_root,
            "ls-files",
            "--error-unmatch",
            "--",
            relative,
        ).returncode != 1:
            raise AcquisitionError("PETES_LAKE_REPLACEMENT_TRACKED_REPORT_ALREADY_TRACKED")
    data = (json.dumps(payload, indent=2) + "\n").encode("utf-8")
    flags = os.O_RDWR | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0)
    try:
        descriptor = os.open(path, flags, 0o600)
    except FileExistsError:
        raise AcquisitionError("PETES_LAKE_REPLACEMENT_TRACKED_REPORT_EXISTS") from None
    opened: os.stat_result | None = None
    try:
        opened = os.fstat(descriptor)
        with os.fdopen(descriptor, "w+b") as handle:
            if handle.write(data) != len(data):
                raise AcquisitionError("PETES_LAKE_REPLACEMENT_REPORT_SHORT_WRITE")
            handle.flush()
            os.fsync(handle.fileno())
            handle.seek(0)
            if handle.read() != data:
                raise AcquisitionError("PETES_LAKE_REPLACEMENT_REPORT_READBACK_MISMATCH")
        observed = path.lstat()
        if not path.is_file() or path.is_symlink() or observed.st_nlink != 1:
            raise AcquisitionError("PETES_LAKE_REPLACEMENT_REPORT_NOT_SINGLE_FILE")
        if opened is None or not os.path.samestat(opened, observed):
            raise AcquisitionError("PETES_LAKE_REPLACEMENT_REPORT_IDENTITY_MISMATCH")
    except BaseException:
        try:
            os.close(descriptor)
        except OSError:
            pass
        try:
            observed = path.lstat()
            if opened is not None and os.path.samestat(opened, observed):
                path.unlink()
        except OSError:
            pass
        raise


def _write_private(run: ReplacementOpticalRun, path: Path, payload: dict[str, Any]) -> None:
    write_private_state(path, payload, repo_root=run.repository_root)


def _custody_observation(path: Path) -> dict[str, Any]:
    if not _path_present(path):
        return {"present": False, "entries": []}
    if path.is_symlink() or not path.is_dir():
        return {"present": True, "plain_directory": False, "entries": []}
    return {
        "present": True,
        "plain_directory": True,
        "entries": [
            {
                "name": item.name,
                "regular_file": item.is_file() and not item.is_symlink(),
                "bytes": item.stat().st_size if item.is_file() and not item.is_symlink() else None,
                "link_count": item.stat().st_nlink if item.is_file() and not item.is_symlink() else None,
            }
            for item in sorted(path.iterdir(), key=lambda value: value.name)
        ],
    }


def _failure_state(
    run: ReplacementOpticalRun,
    preflight: ReplacementPreflight,
    error: AcquisitionError,
    *,
    stage: str,
    credentials_exercised: bool,
) -> dict[str, Any]:
    return {
        "unit_id": UNIT_ID,
        "run_id": run.transaction_run_id,
        "aggregate_run_id": run.aggregate_run_id,
        "generated_at_utc": run.generated_at_utc,
        "event_id": EVENT_ID,
        "event_group_id": EVENT_GROUP_ID,
        "trace": preflight.trace.as_dict(),
        "stage": stage,
        "decision": "PETES_LAKE_REPLACEMENT_OPTICAL_CUSTODY_FAILED",
        "reason_code": error.reason_code,
        "role": error.role,
        "safe_status_detail": error.detail,
        "credentials_exercised": credentials_exercised,
        "quarantine_observation": _custody_observation(run.quarantine),
        "destination_observation": _custody_observation(run.replacement_destination),
        "disposition": "remediate",
        "replacement_u03_source_fitness_authorized": False,
        "next_dependency": "P2O4-T33-U03_REPLACEMENT_CUSTODY_REMEDIATION",
    }


def _try_write_failure(
    run: ReplacementOpticalRun,
    preflight: ReplacementPreflight,
    error: AcquisitionError,
    *,
    stage: str,
    credentials_exercised: bool,
) -> None:
    failure = _failure_state(
        run,
        preflight,
        error,
        stage=stage,
        credentials_exercised=credentials_exercised,
    )
    for path in (run.transaction_state, run.aggregate_state):
        if _path_present(path):
            continue
        try:
            _write_private(run, path, failure)
        except AcquisitionError:
            pass


def _transaction_state(
    run: ReplacementOpticalRun,
    preflight: ReplacementPreflight,
    *,
    download: dict[str, Any],
    registration: dict[str, Any],
    verification: dict[str, Any],
    credentials_exercised: bool,
    reconstructed: bool = False,
) -> dict[str, Any]:
    return {
        "unit_id": UNIT_ID,
        "generated_at_utc": run.generated_at_utc,
        "event_id": EVENT_ID,
        "event_group_id": EVENT_GROUP_ID,
        "pair_id": PAIR_ID,
        "run_id": registration.get("run_id"),
        "aggregate_run_id": run.aggregate_run_id,
        "role": REPLACEMENT_POST_CONTRACT.role,
        "package_id": PACKAGE_ID,
        "contract_version": CONTRACT_VERSION,
        "trace": preflight.trace.as_dict(),
        "contract": _contract_summary(),
        "metadata_snapshot": preflight.metadata_snapshot,
        "terms_snapshot": preflight.terms_snapshot,
        "original_pre_verification": preflight.original_pre_verification,
        "quarantine_path": None if reconstructed else _relative(run, run.quarantine),
        "destination_path": _relative(run, run.replacement_destination),
        "decision": "REGISTERED_EXACT_PETES_LAKE_REPLACEMENT_POST",
        "credentials_exercised": credentials_exercised,
        "reconstructed_from_immutable_registration": reconstructed,
        "download": download,
        "registration": registration,
        "verification": verification,
        "disposition": "pass",
        "next_dependency": "P2O4-T33-U03_REPLACEMENT_SOURCE_FITNESS_R002",
    }


def _registration_asset(transaction: dict[str, Any]) -> dict[str, Any] | None:
    registration = transaction.get("registration") or {}
    assets = registration.get("assets") or []
    if len(assets) != 1 or not isinstance(assets[0], dict):
        return None
    return assets[0]


def _transaction_matches_verification(
    transaction: dict[str, Any],
    verification: dict[str, Any],
) -> bool:
    registration = verification.get("registration") or {}
    run_id = registration.get("run_id")
    asset = _registration_asset(transaction)
    verified_assets = registration.get("assets") or []
    terms = transaction.get("terms_snapshot") or {}
    metadata = transaction.get("metadata_snapshot") or {}
    return bool(
        transaction.get("decision") == "REGISTERED_EXACT_PETES_LAKE_REPLACEMENT_POST"
        and transaction.get("role") == REPLACEMENT_POST_CONTRACT.role
        and transaction.get("package_id") == PACKAGE_ID
        and transaction.get("contract_version") == CONTRACT_VERSION
        and isinstance(run_id, str)
        and _REPLACEMENT_RUN_ID_PATTERN.fullmatch(run_id)
        and transaction.get("run_id") == run_id
        and transaction.get("registration") == registration
        and transaction.get("contract") == _contract_summary()
        and not _validate_trace(transaction.get("trace"))
        and not validate_replacement_metadata(metadata)
        and terms.get("terms_review_id") == TERMS_REVIEW_ID
        and terms.get("exact_authorized_provider_id")
        == REPLACEMENT_POST_CONTRACT.provider_id
        and terms.get("live_refresh_performed") is True
        and transaction.get("original_pre_verification", {}).get("asset", {}).get(
            "sha256"
        )
        == ORIGINAL_PRE_LOCAL_SHA256
        and transaction.get("verification", {}).get("accepted_as_unchanged_registered_package")
        is True
        and asset is not None
        and verified_assets == [asset]
        and asset.get("md5") == REPLACEMENT_POST_CONTRACT.provider_md5
        and asset.get("blake3") == REPLACEMENT_POST_CONTRACT.provider_blake3
        and isinstance(asset.get("sha256"), str)
        and len(asset["sha256"]) == 64
    )


def _validate_trace(trace: Any, repository_root: Path | None = None) -> list[str]:
    if not isinstance(trace, dict):
        return ["REPLACEMENT_TRACE_MISSING"]
    expected = {
        "repository": REPOSITORY,
        "branch": BRANCH,
        "task_issue": TASK_ISSUE,
        "git_base_commit": GIT_BASE_COMMIT,
        "selection_evidence_commit": SELECTION_EVIDENCE_COMMIT,
        "original_custody_evidence_commit": ORIGINAL_CUSTODY_EVIDENCE_COMMIT,
    }
    reasons = [
        f"REPLACEMENT_TRACE_{name.upper()}_MISMATCH"
        for name, value in expected.items()
        if trace.get(name) != value
    ]
    source = trace.get("git_source_commit")
    remote = trace.get("remote_branch_commit")
    if not isinstance(source, str) or re.fullmatch(r"[0-9a-f]{40}", source) is None:
        reasons.append("REPLACEMENT_TRACE_SOURCE_COMMIT_INVALID")
    if remote != source:
        reasons.append("REPLACEMENT_TRACE_REMOTE_COMMIT_MISMATCH")
    expected_bindings = [
        {
            "path": path.as_posix(),
            "bytes": details[0],
            "sha256": details[1],
            "role": details[2],
        }
        for path, details in BOUND_TRACKED_FILES.items()
    ]
    if trace.get("bound_tracked_files") != expected_bindings:
        reasons.append("REPLACEMENT_TRACE_TRACKED_BINDINGS_MISMATCH")
    if repository_root is not None and isinstance(source, str):
        if _git(repository_root, "cat-file", "-e", f"{source}^{{commit}}").returncode != 0:
            reasons.append("REPLACEMENT_TRACE_SOURCE_COMMIT_MISSING")
    return reasons


def _semantic_core(
    run: ReplacementOpticalRun,
    preflight: ReplacementPreflight,
    transaction: dict[str, Any],
) -> dict[str, Any]:
    core = {
        "unit_id": UNIT_ID,
        "generated_at_utc": run.generated_at_utc,
        "run_id": run.aggregate_run_id,
        "software_version": SOFTWARE_VERSION,
        "event_id": EVENT_ID,
        "event_group_id": EVENT_GROUP_ID,
        "pair_id": PAIR_ID,
        "contract_version": CONTRACT_VERSION,
        "source_record_id": SOURCE_RECORD_ID,
        "terms_review_id": TERMS_REVIEW_ID,
        "selection_report_id": SELECTION_REPORT_ID,
        "failed_source_fitness_report_id": FAILED_SOURCE_FITNESS_REPORT_ID,
        "original_custody_report_id": ORIGINAL_CUSTODY_REPORT_ID,
        "trace": preflight.trace.as_dict(),
        "original_pre_verification": preflight.original_pre_verification,
        "replacement_contract": _contract_summary(),
        "replacement_transaction": transaction,
        "metadata_snapshot": preflight.metadata_snapshot,
        "terms_snapshot": preflight.terms_snapshot,
        "gate_results": {
            "exact_tracked_input_bytes": "pass",
            "current_official_terms_exact_bytes": "pass",
            "replacement_specific_terms_decision": "pass",
            "remote_equal_committed_contract": "pass",
            "exact_current_odata_identity": "pass",
            "original_pre_fresh_registration_and_hash_verification": "pass",
            "replacement_singleton_promotion_reopen_and_hash_verification": "pass",
            "no_overwrite_revisioned_private_state": "pass",
            "single_link_private_custody": "pass",
            "original_post_and_failed_u03_evidence_preserved": "pass",
            "archive_pixel_fitness": "not executed; replacement U03 source-fitness r002 required",
        },
        "decision": (
            "PASS_PETES_LAKE_REPLACEMENT_OPTICAL_CUSTODY_"
            "AUTHORIZE_U03_SOURCE_FITNESS_R002_ONLY"
        ),
        "disposition": "pass",
        "replacement_u03_source_fitness_authorized": True,
        "u04_authorized": False,
        "next_dependency": "P2O4-T33-U03_REPLACEMENT_SOURCE_FITNESS_R002",
        "attribution": ATTRIBUTION,
        "limitations": [
            "Custody and exact metadata identity do not establish local cloud, snow, shadow, smoke, registration, or burn-change fitness.",
            "The October 19 catalogue snow value remains a mandatory local SCL/SNW and rendered-evidence risk.",
            "The September 23 selection boundary is conservative scene-selection logic, not an official containment or fire-end claim.",
            "No reference, candidate, owner response, label, sixth accepted event, dataset, split, baseline, or model advances through this custody report.",
        ],
        "warning": WARNING,
    }
    reasons = _validate_semantic_core(core)
    if reasons:
        raise AcquisitionError(
            "PETES_LAKE_REPLACEMENT_SEMANTIC_CORE_REJECTED",
            detail=",".join(reasons),
        )
    return core


def _validate_semantic_core(core: dict[str, Any]) -> list[str]:
    reasons = _validate_trace(core.get("trace"))
    expected = {
        "unit_id": UNIT_ID,
        "event_id": EVENT_ID,
        "event_group_id": EVENT_GROUP_ID,
        "pair_id": PAIR_ID,
        "contract_version": CONTRACT_VERSION,
        "source_record_id": SOURCE_RECORD_ID,
        "terms_review_id": TERMS_REVIEW_ID,
        "decision": (
            "PASS_PETES_LAKE_REPLACEMENT_OPTICAL_CUSTODY_"
            "AUTHORIZE_U03_SOURCE_FITNESS_R002_ONLY"
        ),
        "disposition": "pass",
        "replacement_u03_source_fitness_authorized": True,
        "u04_authorized": False,
        "next_dependency": "P2O4-T33-U03_REPLACEMENT_SOURCE_FITNESS_R002",
    }
    for name, value in expected.items():
        if core.get(name) != value:
            reasons.append(f"REPLACEMENT_CORE_{name.upper()}_MISMATCH")
    transaction = core.get("replacement_transaction")
    if not isinstance(transaction, dict):
        reasons.append("REPLACEMENT_CORE_TRANSACTION_MISSING")
    elif transaction.get("decision") != "REGISTERED_EXACT_PETES_LAKE_REPLACEMENT_POST":
        reasons.append("REPLACEMENT_CORE_TRANSACTION_NOT_PASS")
    else:
        if transaction.get("trace") != core.get("trace"):
            reasons.append("REPLACEMENT_CORE_TRANSACTION_TRACE_MISMATCH")
        if transaction.get("metadata_snapshot") != core.get("metadata_snapshot"):
            reasons.append("REPLACEMENT_CORE_TRANSACTION_METADATA_MISMATCH")
        if transaction.get("terms_snapshot") != core.get("terms_snapshot"):
            reasons.append("REPLACEMENT_CORE_TRANSACTION_TERMS_MISMATCH")
        if transaction.get("original_pre_verification") != core.get(
            "original_pre_verification"
        ):
            reasons.append("REPLACEMENT_CORE_TRANSACTION_PRE_MISMATCH")
        if transaction.get("contract") != core.get("replacement_contract"):
            reasons.append("REPLACEMENT_CORE_TRANSACTION_CONTRACT_MISMATCH")
    if validate_replacement_metadata(core.get("metadata_snapshot") or {}):
        reasons.append("REPLACEMENT_CORE_METADATA_MISMATCH")
    terms = core.get("terms_snapshot") or {}
    if (
        terms.get("terms_review_id") != TERMS_REVIEW_ID
        or terms.get("exact_authorized_provider_id") != REPLACEMENT_POST_CONTRACT.provider_id
        or terms.get("live_refresh_performed") is not True
    ):
        reasons.append("REPLACEMENT_CORE_TERMS_MISMATCH")
    return list(dict.fromkeys(reasons))


def _aggregate_payloads(
    run: ReplacementOpticalRun,
    preflight: ReplacementPreflight,
    transaction: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    core = _semantic_core(run, preflight, transaction)
    semantic_sha = sha256(_canonical_json_bytes(core)).hexdigest()
    report = {
        "report_id": REPORT_ID,
        "report_schema_version": REPORT_SCHEMA_VERSION,
        "semantic_sha256": semantic_sha,
        "semantic_record": core,
    }
    report_bytes = (json.dumps(report, indent=2) + "\n").encode("utf-8")
    private = {
        "run_id": run.aggregate_run_id,
        "trace": preflight.trace.as_dict(),
        "semantic_sha256": semantic_sha,
        "semantic_record": core,
        "tracked_report_binding": {
            "path": _relative(run, run.tracked_report),
            "bytes": len(report_bytes),
            "sha256": sha256(report_bytes).hexdigest(),
        },
        "decision": "PRIVATE_AGGREGATE_BINDS_TRACKED_REPLACEMENT_CUSTODY_REPORT",
    }
    return private, report


def _write_success_outputs(
    run: ReplacementOpticalRun,
    preflight: ReplacementPreflight,
    transaction: dict[str, Any],
) -> dict[str, Any]:
    verification = _fresh_verify_replacement(run)
    if not _transaction_matches_verification(transaction, verification):
        raise AcquisitionError("PETES_LAKE_REPLACEMENT_PREPUBLICATION_BINDING_MISMATCH")
    current_pre = _validate_original_pre(run)
    if current_pre != preflight.original_pre_verification:
        raise AcquisitionError("PETES_LAKE_REPLACEMENT_PREPUBLICATION_PRE_DRIFT")
    private, report = _aggregate_payloads(run, preflight, transaction)
    _write_private(run, run.aggregate_state, private)
    _write_tracked_report_no_overwrite(run, report)
    return report


def acquire_replacement_post(
    *,
    credentials: CdseCredentials,
    run: ReplacementOpticalRun,
    preflight: ReplacementPreflight,
    progress: Callable[[str, int, int], None] | None = None,
) -> dict[str, Any]:
    """Acquire, promote, verify, and bind only the exact replacement post."""

    if run.mode != "acquire" or run.revision != INITIAL_REVISION:
        raise AcquisitionError("PETES_LAKE_REPLACEMENT_ACQUIRE_R001_REQUIRED")
    _assert_path_mode(run, existing_success_outputs=False)
    if validate_replacement_contracts((REPLACEMENT_POST_CONTRACT,)):
        raise AcquisitionError("PETES_LAKE_REPLACEMENT_CONTRACT_REJECTED")
    credentials_exercised = False
    try:
        run.quarantine.parent.mkdir(parents=True, exist_ok=True)
        run.replacement_destination.parent.mkdir(parents=True, exist_ok=True)
        credentials_exercised = True
        download = stream_cdse_asset_with_retries(
            REPLACEMENT_POST_CONTRACT,
            run.quarantine,
            username=credentials.username,
            password=credentials.password,
            max_attempts=MAX_TRANSFER_ATTEMPTS,
            timeout_seconds=180,
            progress=progress,
            part_suffix=TEMPORARY_SUFFIX,
            part_prefix=TEMPORARY_PREFIX,
        )
        try:
            registration = promote_quarantine_no_overwrite(
                run.quarantine,
                run.replacement_destination,
                (REPLACEMENT_POST_CONTRACT,),
                generated_at_utc=run.generated_at_utc,
                run_id=run.transaction_run_id,
                synthetic_fixture=False,
                contract_validator=validate_replacement_contracts,
                contract_version=CONTRACT_VERSION,
            )
        except ValueError:
            evaluation = evaluate_quarantine(
                run.quarantine,
                (REPLACEMENT_POST_CONTRACT,),
                contract_validator=validate_replacement_contracts,
            )
            raise AcquisitionError(
                "PETES_LAKE_REPLACEMENT_QUARANTINE_PROMOTION_REJECTED",
                role=REPLACEMENT_POST_CONTRACT.role,
                detail=",".join(evaluation["reason_codes"]),
            ) from None
        except OSError as error:
            raise AcquisitionError(
                "PETES_LAKE_REPLACEMENT_QUARANTINE_PROMOTION_FAILED",
                role=REPLACEMENT_POST_CONTRACT.role,
                detail=type(error).__name__,
            ) from None
        verification = _fresh_verify_replacement(run)
        transaction = _transaction_state(
            run,
            preflight,
            download=download,
            registration=registration,
            verification=verification,
            credentials_exercised=True,
        )
        if not _transaction_matches_verification(transaction, verification):
            raise AcquisitionError("PETES_LAKE_REPLACEMENT_TRANSACTION_BINDING_MISMATCH")
        _write_private(run, run.transaction_state, transaction)
        return _write_success_outputs(run, preflight, transaction)
    except AcquisitionError as error:
        _try_write_failure(
            run,
            preflight,
            error,
            stage="replacement-post-acquisition",
            credentials_exercised=credentials_exercised,
        )
        raise


def _read_json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise AcquisitionError(
            "PETES_LAKE_REPLACEMENT_STATE_READ_FAILED",
            detail=f"{path.name}:{type(error).__name__}",
        ) from None
    if not isinstance(payload, dict):
        raise AcquisitionError("PETES_LAKE_REPLACEMENT_STATE_NOT_OBJECT", detail=path.name)
    return payload


def _load_existing_transaction(
    run: ReplacementOpticalRun,
    verification: dict[str, Any],
) -> dict[str, Any] | None:
    candidates: dict[str, dict[str, Any]] = {}
    if run.run_state_parent.is_dir():
        for path in sorted(run.run_state_parent.glob("*.json")):
            payload = _read_json_object(path)
            possible: list[Any] = [payload, payload.get("replacement_transaction")]
            semantic = payload.get("semantic_record") or {}
            if isinstance(semantic, dict):
                possible.append(semantic.get("replacement_transaction"))
            for item in possible:
                if isinstance(item, dict) and _transaction_matches_verification(item, verification):
                    candidates[sha256(_canonical_json_bytes(item)).hexdigest()] = item
    if len(candidates) > 1:
        raise AcquisitionError("PETES_LAKE_REPLACEMENT_TRANSACTION_EVIDENCE_AMBIGUOUS")
    return next(iter(candidates.values())) if candidates else None


def finalize_replacement_custody(
    *,
    run: ReplacementOpticalRun,
    preflight: ReplacementPreflight,
) -> dict[str, Any]:
    """Finish custody binding after promotion without another provider request."""

    if run.mode != "finalize":
        raise AcquisitionError("PETES_LAKE_REPLACEMENT_FINALIZE_MODE_REQUIRED")
    _assert_path_mode(run, existing_success_outputs=False)
    try:
        verification = _fresh_verify_replacement(run)
        transaction = _load_existing_transaction(run, verification)
        if transaction is None:
            registration = verification.get("registration") or {}
            transaction = _transaction_state(
                run,
                preflight,
                download={
                    "status": "RECONSTRUCTED_FROM_IMMUTABLE_REGISTRATION",
                    "provider_archive_request_performed": False,
                },
                registration=registration,
                verification=verification,
                credentials_exercised=False,
                reconstructed=True,
            )
        _write_private(run, run.transaction_state, transaction)
        return _write_success_outputs(run, preflight, transaction)
    except AcquisitionError as error:
        _try_write_failure(
            run,
            preflight,
            error,
            stage="replacement-post-finalize",
            credentials_exercised=False,
        )
        raise


def verify_replacement_custody(
    *,
    run: ReplacementOpticalRun,
    preflight: ReplacementPreflight,
) -> list[str]:
    """Recompute public/private bindings and both exact archive registrations."""

    reasons: list[str] = []
    try:
        private_bytes = run.aggregate_state.read_bytes()
        report_bytes = run.tracked_report.read_bytes()
        private = json.loads(private_bytes.decode("utf-8"))
        report = json.loads(report_bytes.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return ["PETES_LAKE_REPLACEMENT_AGGREGATE_READ_FAILED"]
    if not isinstance(private, dict) or not isinstance(report, dict):
        return ["PETES_LAKE_REPLACEMENT_AGGREGATE_NOT_OBJECT"]
    binding = private.get("tracked_report_binding") or {}
    if binding.get("path") != _relative(run, run.tracked_report):
        reasons.append("PETES_LAKE_REPLACEMENT_REPORT_PATH_BINDING_MISMATCH")
    if binding.get("bytes") != len(report_bytes):
        reasons.append("PETES_LAKE_REPLACEMENT_REPORT_SIZE_BINDING_MISMATCH")
    if binding.get("sha256") != sha256(report_bytes).hexdigest():
        reasons.append("PETES_LAKE_REPLACEMENT_REPORT_HASH_BINDING_MISMATCH")
    private_core = private.get("semantic_record")
    report_core = report.get("semantic_record")
    if not isinstance(private_core, dict) or private_core != report_core:
        return [*reasons, "PETES_LAKE_REPLACEMENT_SEMANTIC_BINDING_MISMATCH"]
    semantic_sha = sha256(_canonical_json_bytes(private_core)).hexdigest()
    if private.get("semantic_sha256") != semantic_sha or report.get("semantic_sha256") != semantic_sha:
        reasons.append("PETES_LAKE_REPLACEMENT_SEMANTIC_HASH_MISMATCH")
    reasons.extend(_validate_semantic_core(private_core))
    reasons.extend(_validate_trace(private_core.get("trace"), run.repository_root))
    if private_core.get("trace") != preflight.trace.as_dict():
        reasons.append("PETES_LAKE_REPLACEMENT_CURRENT_TRACE_MISMATCH")
    if _without_observed_at(private_core.get("metadata_snapshot") or {}) != _without_observed_at(
        preflight.metadata_snapshot
    ):
        reasons.append("PETES_LAKE_REPLACEMENT_CURRENT_METADATA_MISMATCH")
    if _without_observed_at(private_core.get("terms_snapshot") or {}) != _without_observed_at(
        preflight.terms_snapshot
    ):
        reasons.append("PETES_LAKE_REPLACEMENT_CURRENT_TERMS_MISMATCH")
    if private_core.get("original_pre_verification") != preflight.original_pre_verification:
        reasons.append("PETES_LAKE_REPLACEMENT_CURRENT_PRE_MISMATCH")
    try:
        verification = _fresh_verify_replacement(run)
    except AcquisitionError:
        reasons.append("PETES_LAKE_REPLACEMENT_FRESH_PACKAGE_VERIFICATION_FAILED")
    else:
        transaction = private_core.get("replacement_transaction")
        if not isinstance(transaction, dict) or not _transaction_matches_verification(
            transaction, verification
        ):
            reasons.append("PETES_LAKE_REPLACEMENT_FRESH_TRANSACTION_BINDING_MISMATCH")
    return list(dict.fromkeys(reasons))
