"""Fail-closed sequential custody for the exact Petes Lake Sentinel pair.

The two archives are intentionally *not* one atomic package.  U02 requires the
pre-fire archive to complete its own download, promotion, and post-promotion
verification before BurnLens may request the post-fire archive.  The
orchestrator below preserves that ordering while producing one aggregate gate
record that U03 can validate.
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
from urllib.request import Request, urlopen

from .cross_event_optical_contract import CdseCredentials
from .paired_intake import (
    AssetContract,
    evaluate_quarantine,
    validate_asset_contracts,
    verify_registered_package,
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
UNIT_ID = "P2O4-T33-U02"
TASK_ISSUE = 521
EVENT_ID = "OR4396912190120230825"
EVENT_GROUP_ID = "event-petes-lake-2023"
SOURCE_RECORD_ID = "SOURCE-2026-028"
TERMS_REVIEW_ID = "TERMS-2026-024"
PAIR_ID = "petes-lake-s2-optical-pair-v0.1.0"
PRE_PACKAGE_ID = "petes-lake-s2-optical-pre-v0.1.0"
POST_PACKAGE_ID = "petes-lake-s2-optical-post-v0.1.0"
CONTRACT_VERSION = "petes-lake-optical-intake-contract-v0.1.0"
REPORT_ID = "PETES-LAKE-OPTICAL-CUSTODY-2026-001"
REPORT_SCHEMA_VERSION = "0.1.0"
REPOSITORY = "drwbkr1/burnlens-deschutes"
BRANCH = "codex/p2o4-t33-petes-lake-milestone"
GIT_BASE_COMMIT = "0d41942dc6c3c307a9a146a2d38fb816e038bb42"
U01_ENTRY_COMMIT = "f59b874d92a0e86d0121759d1c40fbe8ba5c2edc"
ENTRY_GATE_PATH = Path(
    "samples/cross-event/phase-two/petes-lake/PETES-LAKE-ENTRY-GATE-2026-001.json"
)
ENTRY_GATE_BYTES = 18_270
ENTRY_GATE_SHA256 = "ac5d7498f847e0df973c58445188b422d919dc5c195e832e518ba5dbf11d6bec"
PRODUCTION_RUN_DATE = "2026-07-21"
INITIAL_REVISION = "r001"
WARNING = (
    "Experimental BurnLens CV output. Not official wildfire information. "
    "Not emergency guidance. Not evacuation, routing, tactical, or "
    "incident-command support. Official sources govern."
)
TEMPORARY_SUFFIX = ".tmp"
TEMPORARY_PREFIX = "~$"
MAX_TRANSFER_ATTEMPTS = 5
RETRYABLE_TRANSFER_REASONS = {
    "DOWNLOAD_REQUEST_FAILED",
    "DOWNLOAD_STREAM_FAILED",
    "DOWNLOAD_SIZE_MISMATCH",
}


def _contract(
    *,
    role: str,
    package_id: str,
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
        package_id=package_id,
        provider_md5=md5,
        provider_blake3=blake3,
        expected_zip_root=safe_name,
    )


PRE_CONTRACT = _contract(
    role="petes-lake-2023-pre",
    package_id=PRE_PACKAGE_ID,
    provider_id="bf275eb0-7e50-4d4d-a01b-fbaaa18e5142",
    safe_name="S2A_MSIL2A_20230721T185921_N0510_R013_T10TEP_20240911T103205.SAFE",
    size_bytes=1_185_284_273,
    md5="c41d10e4e895839132c0ad4ee47100e1",
    blake3="49d13b491c1e4a979d65dc870daf2d72f940bfc910abb19c00e1a485992ed17b",
)
POST_CONTRACT = _contract(
    role="petes-lake-2023-post",
    package_id=POST_PACKAGE_ID,
    provider_id="80363c3a-8c04-4ed3-8e2a-d1f35e7a62c6",
    safe_name="S2A_MSIL2A_20231029T190511_N0510_R013_T10TEP_20241106T074945.SAFE",
    size_bytes=1_243_068_088,
    md5="bf9383d434448998f5025494d0a43320",
    blake3="9814e80893321d86b9aec796651aaf811d8e31df6ed98413519bbeab1141d105",
)
PETES_LAKE_CONTRACTS = (PRE_CONTRACT, POST_CONTRACT)


EXPECTED_METADATA = {
    PRE_CONTRACT.role: {
        "acquisition_utc": "2023-07-21T18:59:21.024000Z",
        "platform_serial_identifier": "A",
        "tile_id": "10TEP",
        "relative_orbit_number": 13,
        "processor_version": "05.10",
        "product_type": "S2MSI2A",
        "cloud_cover_percent": 0.0,
        "catalogue_snow_percent": 0.226708,
    },
    POST_CONTRACT.role: {
        "acquisition_utc": "2023-10-29T19:05:11.024000Z",
        "platform_serial_identifier": "A",
        "tile_id": "10TEP",
        "relative_orbit_number": 13,
        "processor_version": "05.10",
        "product_type": "S2MSI2A",
        "cloud_cover_percent": 0.01,
        "catalogue_snow_percent": 9.841206,
    },
}


ROUTE_PRECEDENCE = {
    "identity_authority": (
        "Frozen STAC item, CDSE UUID, SAFE name, sensing time, tile, orbit, and "
        "processing baseline must agree."
    ),
    "archive_authority": (
        "Current CDSE OData content length plus MD5 and BLAKE3 govern each acquired archive."
    ),
    "transaction_order": (
        "The pre archive is one singleton transaction and must pass promotion plus "
        "post-promotion verification before the post archive may be requested."
    ),
    "quality_boundary": (
        "Tile-wide cloud and snow metadata are discovery context only; U03 must inspect "
        "local SCL, snow, cloud, shadow, smoke, pixels, and registration."
    ),
}


_PRODUCT_PATTERN = re.compile(
    r"^(?P<platform>S2[ABCD])_MSIL2A_\d{8}T\d{6}_"
    r"N(?P<baseline>\d{4})_R(?P<orbit>\d{3})_T(?P<tile>[0-9A-Z]{5})_"
    r"\d{8}T\d{6}\.SAFE$"
)
_REVISION_PATTERN = re.compile(r"^r(?P<number>\d{3})$")
_PRE_RUN_ID_PATTERN = re.compile(
    rf"^BL-{PRODUCTION_RUN_DATE}-petes-lake-optical-pre-r(?:00[1-9]|0[1-9]\d|[1-9]\d{{2}})$"
)
_POST_RUN_ID_PATTERN = re.compile(
    rf"^BL-{PRODUCTION_RUN_DATE}-petes-lake-optical-post-r(?:00[1-9]|0[1-9]\d|[1-9]\d{{2}})$"
)


def _singleton_validator(expected: AssetContract) -> Callable[[Iterable[AssetContract]], list[str]]:
    def validate(contracts: Iterable[AssetContract]) -> list[str]:
        items = list(contracts)
        reasons = validate_asset_contracts(items)
        if items != [expected]:
            reasons.append(f"{expected.role}:SINGLETON_CONTRACT_MISMATCH")
        return reasons

    return validate


def validate_petes_lake_contracts(contracts: Iterable[AssetContract]) -> list[str]:
    """Require the exact ordered pair while retaining separate package identities."""

    items = list(contracts)
    reasons: list[str] = []
    if items != list(PETES_LAKE_CONTRACTS):
        reasons.append("PETES_LAKE_ORDERED_PAIR_CONTRACT_MISMATCH")
    for expected, observed in zip(PETES_LAKE_CONTRACTS, items, strict=False):
        reasons.extend(_singleton_validator(expected)((observed,)))
    if len(items) != 2:
        reasons.append("CONTRACT_REQUIRES_EXACT_PRE_POST_PAIR")
        return list(dict.fromkeys(reasons))
    parsed = [_PRODUCT_PATTERN.fullmatch(item.native_id) for item in items]
    if any(value is None for value in parsed):
        reasons.append("OPTICAL_PRODUCT_ID_INVALID")
    else:
        identities = {
            (
                match.group("platform"),
                match.group("baseline"),
                match.group("orbit"),
                match.group("tile"),
            )
            for match in parsed
            if match is not None
        }
        if identities != {("S2A", "0510", "013", "10TEP")}:
            reasons.append("PETES_LAKE_PAIR_GEOMETRY_IDENTITY_MISMATCH")
    if [item.package_id for item in items] != [PRE_PACKAGE_ID, POST_PACKAGE_ID]:
        reasons.append("PETES_LAKE_SINGLETON_PACKAGE_IDS_MISMATCH")
    return list(dict.fromkeys(reasons))


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
        "event_id": EVENT_ID,
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
        "catalogue_snow_percent": EXPECTED_METADATA[role]["catalogue_snow_percent"],
        "catalogue_snow_source": "frozen current CDSE STAC identity from P2O4-T33-U01",
    }


def validate_petes_lake_metadata(
    snapshot: dict[str, Any],
    contracts: Iterable[AssetContract] = PETES_LAKE_CONTRACTS,
) -> list[str]:
    items = list(contracts)
    if items == list(PETES_LAKE_CONTRACTS):
        reasons = validate_petes_lake_contracts(items)
    elif len(items) == 1 and items[0] in PETES_LAKE_CONTRACTS:
        reasons = _singleton_validator(items[0])(items)
    else:
        reasons = ["PETES_LAKE_METADATA_CONTRACT_SCOPE_MISMATCH"]
    if snapshot.get("source_record_id") != SOURCE_RECORD_ID:
        reasons.append("METADATA_SOURCE_RECORD_MISMATCH")
    if snapshot.get("terms_review_id") != TERMS_REVIEW_ID:
        reasons.append("METADATA_TERMS_RECORD_MISMATCH")
    if snapshot.get("live_refresh_performed") is not True:
        reasons.append("LIVE_METADATA_REFRESH_REQUIRED")
    if not isinstance(snapshot.get("observed_at_utc"), str) or not snapshot["observed_at_utc"]:
        reasons.append("METADATA_OBSERVED_AT_MISSING")
    records = snapshot.get("records")
    if not isinstance(records, list):
        return [*reasons, "METADATA_RECORDS_MISSING"]
    expected_roles = [item.role for item in items]
    if [item.get("role") for item in records if isinstance(item, dict)] != expected_roles:
        reasons.append("METADATA_ORDERED_ROLE_SET_MISMATCH")
    if len(records) != len(items) or any(not isinstance(item, dict) for item in records):
        return [*reasons, "METADATA_RECORD_SET_MISMATCH"]
    by_role = {record["role"]: record for record in records}
    for contract in items:
        record = by_role.get(contract.role)
        if record is None:
            reasons.append(f"{contract.role}:MISSING")
            continue
        expected = EXPECTED_METADATA[contract.role]
        comparisons = {
            "EVENT_ID": EVENT_ID,
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
            "CATALOGUE_SNOW": expected["catalogue_snow_percent"],
        }
        fields = {
            "EVENT_ID": record.get("event_id"),
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
            "CATALOGUE_SNOW": record.get("catalogue_snow_percent"),
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
    return list(dict.fromkeys(reasons))


def refresh_petes_lake_metadata(
    *, observed_at_utc: str, urlopen_fn: Callable[..., Any] = urlopen
) -> dict[str, Any]:
    headers = {"Accept": "application/json", "User-Agent": USER_AGENT}
    records = []
    for contract in PETES_LAKE_CONTRACTS:
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
    reasons = validate_petes_lake_metadata(snapshot)
    if reasons:
        raise AcquisitionError("PUBLIC_METADATA_DRIFT", detail=",".join(reasons))
    return snapshot


def refresh_petes_lake_metadata_for_role(
    contract: AssetContract,
    *,
    observed_at_utc: str,
    urlopen_fn: Callable[..., Any] = urlopen,
) -> dict[str, Any]:
    """Refresh one exact archive immediately before its transaction."""

    if contract not in PETES_LAKE_CONTRACTS:
        raise AcquisitionError("PETES_LAKE_METADATA_ROLE_NOT_AUTHORIZED")
    headers = {"Accept": "application/json", "User-Agent": USER_AGENT}
    payload = _open_json(Request(_metadata_url(contract), headers=headers), urlopen_fn=urlopen_fn)
    snapshot = {
        "observed_at_utc": observed_at_utc,
        "source_record_id": SOURCE_RECORD_ID,
        "terms_review_id": TERMS_REVIEW_ID,
        "live_refresh_performed": True,
        "route_precedence": ROUTE_PRECEDENCE,
        "records": [_normalize_metadata(payload, role=contract.role)],
    }
    reasons = validate_petes_lake_metadata(snapshot, (contract,))
    if reasons:
        raise AcquisitionError(
            "PUBLIC_METADATA_DRIFT",
            role=contract.role,
            detail=",".join(reasons),
        )
    return snapshot


@dataclass(frozen=True)
class PetesLakeOpticalRun:
    """Exact immutable run IDs and repository-local custody destinations."""

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
        mode: str = "full",
    ) -> "PetesLakeOpticalRun":
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
        if mode not in {"full", "full-remediation", "post-only", "aggregate-only"}:
            raise ValueError(
                "mode must be full, full-remediation, post-only, or aggregate-only"
            )
        if mode == "full" and revision != INITIAL_REVISION:
            raise ValueError("full production acquisition is hard-bound to r001")
        if mode != "full" and int(match.group("number")) <= 1:
            raise ValueError("remediation modes require r002 or later")
        return cls(
            repository_root=repository_root.resolve(),
            generated_at_utc=generated_at_utc,
            revision=revision,
            mode=mode,
        )

    @property
    def pre_run_id(self) -> str:
        revision = self.revision if self.mode == "full-remediation" else INITIAL_REVISION
        return f"BL-{PRODUCTION_RUN_DATE}-petes-lake-optical-pre-{revision}"

    @property
    def post_run_id(self) -> str:
        return f"BL-{PRODUCTION_RUN_DATE}-petes-lake-optical-post-{self.revision}"

    @property
    def aggregate_run_id(self) -> str:
        return f"BL-{PRODUCTION_RUN_DATE}-petes-lake-optical-intake-{self.revision}"

    @property
    def pre_quarantine(self) -> Path:
        revision = self.revision if self.mode == "full-remediation" else INITIAL_REVISION
        return self.repository_root / "downloads" / "phase-two" / "quarantine" / UNIT_ID / f"petes-lake-optical-pre-{revision}"

    @property
    def post_quarantine(self) -> Path:
        return self.repository_root / "downloads" / "phase-two" / "quarantine" / UNIT_ID / f"petes-lake-optical-post-{self.revision}"

    @property
    def raw_parent(self) -> Path:
        return self.repository_root / "downloads" / "phase-two" / "raw"

    @property
    def pre_destination(self) -> Path:
        return self.raw_parent / PRE_PACKAGE_ID

    @property
    def post_destination(self) -> Path:
        return self.raw_parent / POST_PACKAGE_ID

    @property
    def run_state_parent(self) -> Path:
        return self.repository_root / "downloads" / "phase-two" / "runs" / UNIT_ID

    @property
    def pre_state(self) -> Path:
        return self.run_state_parent / f"{self.pre_run_id}.json"

    @property
    def post_state(self) -> Path:
        return self.run_state_parent / f"{self.post_run_id}.json"

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

    @property
    def entry_gate(self) -> Path:
        return self.repository_root / ENTRY_GATE_PATH

    def aggregate_state_for_revision(self, revision: str) -> Path:
        return self.run_state_parent / (
            f"BL-{PRODUCTION_RUN_DATE}-petes-lake-optical-intake-{revision}.json"
        )


@dataclass(frozen=True)
class PetesLakeTrace:
    git_source_commit: str
    branch: str
    task_issue: int
    git_base_commit: str
    u01_entry_commit: str
    entry_gate_path: str
    entry_gate_bytes: int
    entry_gate_sha256: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "repository": REPOSITORY,
            "git_source_commit": self.git_source_commit,
            "branch": self.branch,
            "task_issue": self.task_issue,
            "git_base_commit": self.git_base_commit,
            "u01_entry_commit": self.u01_entry_commit,
            "entry_gate_path": self.entry_gate_path,
            "entry_gate_bytes": self.entry_gate_bytes,
            "entry_gate_sha256": self.entry_gate_sha256,
        }


def _validate_trace_binding(trace: Any) -> list[str]:
    if not isinstance(trace, dict):
        return ["TRACE_BINDING_MISSING"]
    expected = {
        "repository": REPOSITORY,
        "branch": BRANCH,
        "task_issue": TASK_ISSUE,
        "git_base_commit": GIT_BASE_COMMIT,
        "u01_entry_commit": U01_ENTRY_COMMIT,
        "entry_gate_path": ENTRY_GATE_PATH.as_posix(),
        "entry_gate_bytes": ENTRY_GATE_BYTES,
        "entry_gate_sha256": ENTRY_GATE_SHA256,
    }
    reasons = [f"TRACE_{name.upper()}_MISMATCH" for name, value in expected.items() if trace.get(name) != value]
    if not isinstance(trace.get("git_source_commit"), str) or re.fullmatch(
        r"[0-9a-f]{40}", trace["git_source_commit"]
    ) is None:
        reasons.append("TRACE_GIT_SOURCE_COMMIT_INVALID")
    return reasons


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


def verify_petes_lake_repository_preflight(
    run: PetesLakeOpticalRun, *, existing_success_outputs: bool = False
) -> PetesLakeTrace:
    """Verify the exact clean issue branch and custody boundary before credentials."""

    root = run.repository_root
    top = _git(root, "rev-parse", "--show-toplevel")
    if top.returncode != 0 or Path(top.stdout.strip()).resolve() != root:
        raise AcquisitionError("PETES_LAKE_REPOSITORY_ROOT_MISMATCH")
    branch = _git(root, "branch", "--show-current")
    if branch.returncode != 0 or branch.stdout.strip() != BRANCH:
        raise AcquisitionError("PETES_LAKE_BRANCH_MISMATCH")
    origin = _git(root, "config", "--get", "remote.origin.url")
    normalized_origin = origin.stdout.strip().lower().replace("\\", "/")
    if origin.returncode != 0 or "drwbkr1/burnlens-deschutes" not in normalized_origin:
        raise AcquisitionError("PETES_LAKE_ORIGIN_MISMATCH")
    status = _git(root, "status", "--porcelain=v1", "--untracked-files=all")
    allowed_status = f"?? {_display_path(run, run.tracked_report)}" if existing_success_outputs else ""
    observed_status = status.stdout.strip().replace("\\", "/")
    if status.returncode != 0 or observed_status != allowed_status:
        raise AcquisitionError("PETES_LAKE_WORKTREE_NOT_CLEAN")
    head = _git(root, "rev-parse", "HEAD")
    if head.returncode != 0 or not re.fullmatch(r"[0-9a-f]{40}", head.stdout.strip()):
        raise AcquisitionError("PETES_LAKE_COMMITTED_HEAD_REQUIRED")
    for ancestor, reason in (
        (GIT_BASE_COMMIT, "PETES_LAKE_BASE_NOT_ANCESTOR"),
        (U01_ENTRY_COMMIT, "PETES_LAKE_U01_NOT_ANCESTOR"),
    ):
        check = _git(root, "merge-base", "--is-ancestor", ancestor, head.stdout.strip())
        if check.returncode != 0:
            raise AcquisitionError(reason)
    if (
        not run.entry_gate.is_file()
        or run.entry_gate.stat().st_size != ENTRY_GATE_BYTES
        or _sha256_file(run.entry_gate) != ENTRY_GATE_SHA256
    ):
        raise AcquisitionError("PETES_LAKE_ENTRY_GATE_BINDING_MISMATCH")
    private_paths = {
        run.pre_quarantine,
        run.post_quarantine,
        run.pre_destination,
        run.post_destination,
        run.pre_state,
        run.post_state,
        run.aggregate_state,
        run.aggregate_state_for_revision(INITIAL_REVISION),
    }
    for path in sorted(private_paths, key=str):
        relative = path.relative_to(root).as_posix()
        ignored = _git(root, "check-ignore", "--quiet", "--no-index", "--", relative)
        tracked = _git(root, "ls-files", "--error-unmatch", "--", relative)
        if ignored.returncode != 0 or tracked.returncode != 1:
            raise AcquisitionError("PETES_LAKE_PRIVATE_PATH_GATE_FAILED", detail=relative)
    report_relative = run.tracked_report.relative_to(root).as_posix()
    if _git(root, "check-ignore", "--quiet", "--no-index", "--", report_relative).returncode != 1:
        raise AcquisitionError("PETES_LAKE_TRACKED_REPORT_IGNORED")
    if _git(root, "ls-files", "--error-unmatch", "--", report_relative).returncode != 1:
        raise AcquisitionError("PETES_LAKE_TRACKED_REPORT_ALREADY_TRACKED")
    if existing_success_outputs:
        if not run.aggregate_state.is_file() or not run.tracked_report.is_file():
            raise AcquisitionError("PETES_LAKE_SUCCESS_OUTPUTS_MISSING")
    else:
        assert_no_overwrite_targets(run)
    return PetesLakeTrace(
        git_source_commit=head.stdout.strip(),
        branch=BRANCH,
        task_issue=TASK_ISSUE,
        git_base_commit=GIT_BASE_COMMIT,
        u01_entry_commit=U01_ENTRY_COMMIT,
        entry_gate_path=ENTRY_GATE_PATH.as_posix(),
        entry_gate_bytes=ENTRY_GATE_BYTES,
        entry_gate_sha256=ENTRY_GATE_SHA256,
    )


def _path_present(path: Path) -> bool:
    is_junction = getattr(path, "is_junction", None)
    return path.exists() or path.is_symlink() or bool(is_junction and is_junction())


def _display_path(run: PetesLakeOpticalRun, path: Path) -> str:
    return path.relative_to(run.repository_root).as_posix()


def assert_no_overwrite_targets(run: PetesLakeOpticalRun) -> None:
    """Reserve every output the selected mode is allowed to create."""

    if run.mode in {"full", "full-remediation"}:
        targets = (
            run.pre_quarantine,
            run.post_quarantine,
            run.pre_destination,
            run.post_destination,
            run.pre_state,
            run.post_state,
            run.aggregate_state,
            run.tracked_report,
        )
    elif run.mode == "post-only":
        targets = (
            run.post_quarantine,
            run.post_destination,
            run.post_state,
            run.aggregate_state,
            run.tracked_report,
        )
    else:
        targets = (run.aggregate_state, run.tracked_report)
    present = [_display_path(run, path) for path in targets if _path_present(path)]
    if present:
        raise AcquisitionError("NO_OVERWRITE_TARGET_EXISTS", detail=",".join(present))


def _write_tracked_report_no_overwrite(
    run: PetesLakeOpticalRun, path: Path, payload: dict[str, Any]
) -> None:
    """Create the tracked aggregate report once, separately from private state."""

    if path != run.tracked_report:
        raise AcquisitionError("TRACKED_REPORT_PATH_MISMATCH")
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        path.parent.resolve().relative_to(run.repository_root)
    except ValueError:
        raise AcquisitionError("TRACKED_REPORT_OUTSIDE_REPOSITORY") from None
    if _path_present(path):
        raise AcquisitionError("NO_OVERWRITE_STATE_EXISTS", detail=path.name)
    data = (json.dumps(payload, indent=2) + "\n").encode("utf-8")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0)
    try:
        descriptor = os.open(path, flags, 0o600)
    except FileExistsError:
        raise AcquisitionError("NO_OVERWRITE_STATE_EXISTS", detail=path.name) from None
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        observed = path.lstat()
        if not path.is_file() or path.is_symlink() or observed.st_nlink != 1:
            raise AcquisitionError("TRACKED_REPORT_NOT_SINGLE_REGULAR_FILE")
        if path.read_bytes() != data:
            raise AcquisitionError("TRACKED_REPORT_READBACK_MISMATCH")
    except BaseException:
        path.unlink(missing_ok=True)
        raise


def _write_private_run_state(
    run: PetesLakeOpticalRun, path: Path, payload: dict[str, Any]
) -> None:
    write_private_state(path, payload, repo_root=run.repository_root)


def _read_json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise AcquisitionError(
            "PETES_LAKE_STATE_READ_FAILED",
            detail=f"{path.name}:{type(error).__name__}",
        ) from None
    if not isinstance(payload, dict):
        raise AcquisitionError("PETES_LAKE_STATE_NOT_OBJECT", detail=path.name)
    return payload


def _validate_working_entries(quarantine: Path, contract: AssetContract) -> None:
    if not _path_present(quarantine):
        return
    if quarantine.is_symlink() or not quarantine.is_dir():
        raise AcquisitionError("QUARANTINE_NOT_PLAIN_DIRECTORY", role=contract.role)
    expected = {
        contract.expected_filename,
        f"{TEMPORARY_PREFIX}{contract.expected_filename}{TEMPORARY_SUFFIX}",
    }
    unexpected = sorted(entry.name for entry in quarantine.iterdir() if entry.name not in expected)
    if unexpected:
        raise AcquisitionError(
            "UNEXPECTED_ACQUISITION_WORKING_ENTRY",
            role=contract.role,
            detail=",".join(unexpected),
        )


def _promote_quarantine_no_replace(
    *,
    quarantine: Path,
    destination: Path,
    contract: AssetContract,
    generated_at_utc: str,
    run_id: str,
    validator: Callable[[Iterable[AssetContract]], list[str]],
) -> dict[str, Any]:
    """Delegate to the shared portable no-replace custody primitive."""

    return promote_quarantine_no_overwrite(
        quarantine,
        destination,
        (contract,),
        generated_at_utc=generated_at_utc,
        run_id=run_id,
        synthetic_fixture=False,
        contract_validator=validator,
        contract_version=CONTRACT_VERSION,
    )


def _acquire_singleton(
    *,
    contract: AssetContract,
    credentials: CdseCredentials,
    quarantine: Path,
    destination: Path,
    generated_at_utc: str,
    run_id: str,
    progress: Callable[[str, int, int], None] | None,
    activity: dict[str, bool],
) -> dict[str, Any]:
    validator = _singleton_validator(contract)
    contract_reasons = validator((contract,))
    if contract_reasons:
        raise AcquisitionError(
            "PETES_LAKE_SINGLETON_CONTRACT_REJECTED",
            role=contract.role,
            detail=",".join(contract_reasons),
        )
    if _path_present(destination):
        raise AcquisitionError("SINGLETON_DESTINATION_ALREADY_EXISTS", role=contract.role)
    _validate_working_entries(quarantine, contract)
    quarantine.parent.mkdir(parents=True, exist_ok=True)
    destination.parent.mkdir(parents=True, exist_ok=True)
    activity["credentials_exercised"] = True
    download = stream_cdse_asset_with_retries(
        contract,
        quarantine,
        username=credentials.username,
        password=credentials.password,
        max_attempts=MAX_TRANSFER_ATTEMPTS,
        timeout_seconds=180,
        progress=progress,
        part_suffix=TEMPORARY_SUFFIX,
        part_prefix=TEMPORARY_PREFIX,
    )
    try:
        registration = _promote_quarantine_no_replace(
            quarantine=quarantine,
            destination=destination,
            contract=contract,
            generated_at_utc=generated_at_utc,
            run_id=run_id,
            validator=validator,
        )
    except ValueError:
        evaluation = evaluate_quarantine(
            quarantine,
            (contract,),
            contract_validator=validator,
        )
        raise AcquisitionError(
            "QUARANTINE_PROMOTION_REJECTED",
            role=contract.role,
            detail=",".join(evaluation["reason_codes"]),
        ) from None
    except OSError as error:
        raise AcquisitionError(
            "QUARANTINE_ATOMIC_PROMOTION_FAILED",
            role=contract.role,
            detail=type(error).__name__,
        ) from None
    verification = verify_registered_package(
        destination,
        (contract,),
        contract_validator=validator,
        contract_version=CONTRACT_VERSION,
        allow_multilink_registration_manifest=True,
    )
    if not verification["accepted_as_unchanged_registered_package"]:
        raise AcquisitionError("POST_PROMOTION_VERIFICATION_FAILED", role=contract.role)
    return {
        "decision": "REGISTERED_EXACT_PETES_LAKE_SINGLETON",
        "role": contract.role,
        "package_id": contract.package_id,
        "run_id": run_id,
        "credentials_exercised": True,
        "download": download,
        "registration": registration,
        "verification": verification,
    }


def _contract_summary(contract: AssetContract) -> dict[str, Any]:
    return {
        "role": contract.role,
        "provider": contract.provider,
        "source_record_id": contract.source_record_id,
        "provider_id": contract.provider_id,
        "native_id": contract.native_id,
        "expected_filename": contract.expected_filename,
        "expected_size_bytes": contract.expected_size_bytes,
        "package_id": contract.package_id,
        "provider_md5": contract.provider_md5,
        "provider_blake3": contract.provider_blake3,
        "expected_zip_root": contract.expected_zip_root,
    }


def _success_state(
    run: PetesLakeOpticalRun,
    trace: PetesLakeTrace,
    contract: AssetContract,
    result: dict[str, Any],
    *,
    quarantine: Path,
    destination: Path,
    metadata_snapshot: dict[str, Any],
) -> dict[str, Any]:
    return {
        "unit_id": UNIT_ID,
        "generated_at_utc": run.generated_at_utc,
        "event_id": EVENT_ID,
        "event_group_id": EVENT_GROUP_ID,
        "pair_id": PAIR_ID,
        "run_id": result["run_id"],
        "role": contract.role,
        "package_id": contract.package_id,
        "contract_version": CONTRACT_VERSION,
        "trace": trace.as_dict(),
        "metadata_snapshot": metadata_snapshot,
        "contract": _contract_summary(contract),
        "quarantine_path": _display_path(run, quarantine),
        "destination_path": _display_path(run, destination),
        "decision": result["decision"],
        "credentials_exercised": result["credentials_exercised"],
        "download": result["download"],
        "registration": result["registration"],
        "verification": result["verification"],
        "disposition": "pass",
        "next_dependency": POST_CONTRACT.role if contract == PRE_CONTRACT else "P2O4-T33-U03",
    }


def _custody_observation(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    if not _path_present(path):
        return {"present": False, "entries": []}
    if not path.is_dir() or path.is_symlink():
        return {"present": True, "plain_directory": False, "entries": []}
    entries = []
    for item in sorted(path.iterdir(), key=lambda value: value.name):
        entries.append(
            {
                "name": item.name,
                "regular_file": item.is_file() and not item.is_symlink(),
                "bytes": item.stat().st_size if item.is_file() and not item.is_symlink() else None,
            }
        )
    return {"present": True, "plain_directory": True, "entries": entries}


def _failure_state(
    run: PetesLakeOpticalRun,
    trace: PetesLakeTrace,
    error: AcquisitionError,
    *,
    stage: str,
    run_id: str,
    credentials_exercised: bool,
    quarantine: Path | None = None,
    destination: Path | None = None,
) -> dict[str, Any]:
    return {
        "unit_id": UNIT_ID,
        "generated_at_utc": run.generated_at_utc,
        "event_id": EVENT_ID,
        "event_group_id": EVENT_GROUP_ID,
        "pair_id": PAIR_ID,
        "run_id": run_id,
        "trace": trace.as_dict(),
        "stage": stage,
        "decision": "PETES_LAKE_OPTICAL_CUSTODY_FAILED",
        "reason_code": error.reason_code,
        "role": error.role,
        "safe_status_detail": error.detail,
        "credentials_exercised": credentials_exercised,
        "quarantine_observation": _custody_observation(quarantine),
        "destination_observation": _custody_observation(destination),
        "disposition": "remediate",
        "u03_authorized": False,
        "next_dependency": UNIT_ID,
    }


def _registration_has_local_hashes(transaction: dict[str, Any]) -> bool:
    registration = transaction.get("registration") or {}
    assets = registration.get("assets")
    if not isinstance(assets, list) or len(assets) != 1 or not isinstance(assets[0], dict):
        return False
    asset = assets[0]
    return all(
        isinstance(asset.get(name), str) and len(asset[name]) == length
        for name, length in (("sha256", 64), ("md5", 32), ("blake3", 64))
    )


def _canonical_json_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )


def _validate_semantic_core(core: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    reasons.extend(f"AGGREGATE_{reason}" for reason in _validate_trace_binding(core.get("trace")))
    if core.get("unit_id") != UNIT_ID:
        reasons.append("U03_UNIT_ID_MISMATCH")
    if core.get("pair_id") != PAIR_ID:
        reasons.append("U03_PAIR_ID_MISMATCH")
    if core.get("decision") != "PASS_PETES_LAKE_OPTICAL_CUSTODY_AUTHORIZE_U03_ONLY":
        reasons.append("U03_AGGREGATE_DECISION_NOT_PASS")
    transactions = core.get("transactions")
    if not isinstance(transactions, list) or len(transactions) != 2:
        return [*reasons, "U03_REQUIRES_TWO_TRANSACTIONS"]
    if [item.get("role") for item in transactions if isinstance(item, dict)] != [
        PRE_CONTRACT.role,
        POST_CONTRACT.role,
    ]:
        reasons.append("U03_TRANSACTION_ORDER_OR_ROLE_MISMATCH")
    observed_times: list[str] = []
    for expected, transaction in zip(PETES_LAKE_CONTRACTS, transactions, strict=True):
        if not isinstance(transaction, dict):
            reasons.append(f"{expected.role}:U03_TRANSACTION_INVALID")
            continue
        if transaction.get("decision") != "REGISTERED_EXACT_PETES_LAKE_SINGLETON":
            reasons.append(f"{expected.role}:U03_TRANSACTION_NOT_PASS")
        if transaction.get("package_id") != expected.package_id:
            reasons.append(f"{expected.role}:U03_PACKAGE_ID_MISMATCH")
        verification = transaction.get("verification") or {}
        if verification.get("accepted_as_unchanged_registered_package") is not True:
            reasons.append(f"{expected.role}:U03_POST_PROMOTION_VERIFICATION_NOT_PASS")
        registration = transaction.get("registration") or {}
        if registration.get("run_id") != transaction.get("run_id"):
            reasons.append(f"{expected.role}:U03_REGISTRATION_RUN_ID_MISMATCH")
        run_pattern = _PRE_RUN_ID_PATTERN if expected == PRE_CONTRACT else _POST_RUN_ID_PATTERN
        if not isinstance(transaction.get("run_id"), str) or run_pattern.fullmatch(
            transaction["run_id"]
        ) is None:
            reasons.append(f"{expected.role}:U03_RUN_ID_NOT_AUTHORIZED")
        if not _registration_has_local_hashes(transaction):
            reasons.append(f"{expected.role}:U03_LOCAL_HASHES_MISSING")
        reasons.extend(
            f"{expected.role}:{reason}"
            for reason in _validate_trace_binding(transaction.get("trace"))
        )
        metadata = transaction.get("metadata_snapshot") or {}
        metadata_reasons = validate_petes_lake_metadata(metadata, (expected,))
        reasons.extend(f"{expected.role}:{reason}" for reason in metadata_reasons)
        observed = metadata.get("observed_at_utc")
        if isinstance(observed, str):
            observed_times.append(observed)
    if len(observed_times) != 2 or observed_times[0] == observed_times[1]:
        reasons.append("U03_DISTINCT_PRE_POST_METADATA_TIMESTAMPS_REQUIRED")
    elif len(observed_times) == 2:
        try:
            parsed_times = [
                datetime.fromisoformat(value.replace("Z", "+00:00")) for value in observed_times
            ]
        except ValueError:
            reasons.append("U03_METADATA_TIMESTAMP_INVALID")
        else:
            if parsed_times[1] <= parsed_times[0]:
                reasons.append("U03_METADATA_REFRESH_ORDER_INVALID")
    if core.get("disposition") != "pass":
        reasons.append("U03_DISPOSITION_NOT_PASS")
    if core.get("next_dependency") != "P2O4-T33-U03":
        reasons.append("U03_NEXT_DEPENDENCY_MISMATCH")
    return list(dict.fromkeys(reasons))


def _semantic_core(
    run: PetesLakeOpticalRun,
    trace: PetesLakeTrace,
    pre: dict[str, Any],
    post: dict[str, Any],
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
        "trace": trace.as_dict(),
        "contracts": [_contract_summary(item) for item in PETES_LAKE_CONTRACTS],
        "transaction_order": [PRE_CONTRACT.role, POST_CONTRACT.role],
        "transactions": [pre, post],
        "gate_results": {
            "exact_ordered_contracts": "pass",
            "separate_live_metadata_refreshes": "pass",
            "pre_singleton_promotion_reopen_and_post_verification": "pass",
            "post_request_after_pre_verification_and_state": "pass",
            "post_singleton_promotion_reopen_and_post_verification": "pass",
            "local_sha256_md5_blake3": "pass",
            "no_overwrite_final_paths_and_run_ids": "pass",
            "archive_pixel_fitness": "not executed; P2O4-T33-U03",
        },
        "disposition": "pass",
        "decision": "PASS_PETES_LAKE_OPTICAL_CUSTODY_AUTHORIZE_U03_ONLY",
        "u03_authorized": True,
        "next_dependency": "P2O4-T33-U03",
        "warning": WARNING,
    }
    reasons = _validate_semantic_core(core)
    if reasons:
        raise AcquisitionError("U03_SEMANTIC_CORE_REJECTED", detail=",".join(reasons))
    return core


def _aggregate_payloads(
    run: PetesLakeOpticalRun,
    trace: PetesLakeTrace,
    pre: dict[str, Any],
    post: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    core = _semantic_core(run, trace, pre, post)
    semantic_sha = sha256(_canonical_json_bytes(core)).hexdigest()
    report = {
        "report_id": REPORT_ID,
        "report_schema_version": REPORT_SCHEMA_VERSION,
        "semantic_sha256": semantic_sha,
        "semantic_record": core,
    }
    report_bytes = (json.dumps(report, indent=2) + "\n").encode("utf-8")
    private = {
        "state_schema_version": "petes-lake-optical-aggregate-state-v0.1.0",
        "unit_id": UNIT_ID,
        "run_id": run.aggregate_run_id,
        "trace": trace.as_dict(),
        "decision": core["decision"],
        "semantic_sha256": semantic_sha,
        "semantic_record": core,
        "tracked_report_binding": {
            "path": _display_path(run, run.tracked_report),
            "bytes": len(report_bytes),
            "sha256": sha256(report_bytes).hexdigest(),
        },
        "disposition": "pass",
        "u03_authorized": True,
        "next_dependency": "P2O4-T33-U03",
    }
    return private, report


def _fresh_verify(contract: AssetContract, destination: Path) -> dict[str, Any]:
    verification = verify_registered_package(
        destination,
        (contract,),
        contract_validator=_singleton_validator(contract),
        contract_version=CONTRACT_VERSION,
        allow_multilink_registration_manifest=True,
    )
    if not verification["accepted_as_unchanged_registered_package"]:
        raise AcquisitionError("REMEDIATION_REGISTERED_PACKAGE_INVALID", role=contract.role)
    return verification


def _transaction_matches_fresh_verification(
    transaction: dict[str, Any], contract: AssetContract, verification: dict[str, Any]
) -> bool:
    return (
        transaction.get("role") == contract.role
        and transaction.get("package_id") == contract.package_id
        and transaction.get("registration") == verification.get("registration")
        and transaction.get("verification", {}).get(
            "accepted_as_unchanged_registered_package"
        )
        is True
        and not _validate_trace_binding(transaction.get("trace"))
    )


def _registered_pre_run_is_authorized(verification: dict[str, Any]) -> bool:
    run_id = (verification.get("registration") or {}).get("run_id")
    return isinstance(run_id, str) and _PRE_RUN_ID_PATTERN.fullmatch(run_id) is not None


def validate_u03_prerequisite(run: PetesLakeOpticalRun) -> list[str]:
    """Require private aggregate, tracked report, and fresh raw-package verification."""

    reasons: list[str] = []
    if not run.aggregate_state.is_file():
        reasons.append("U03_PRIVATE_AGGREGATE_STATE_REQUIRED")
    if not run.tracked_report.is_file():
        reasons.append("U03_TRACKED_REPORT_REQUIRED")
    if reasons:
        return reasons
    try:
        private_bytes = run.aggregate_state.read_bytes()
        report_bytes = run.tracked_report.read_bytes()
        private = json.loads(private_bytes.decode("utf-8"))
        report = json.loads(report_bytes.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return ["U03_AGGREGATE_ARTIFACT_READ_FAILED"]
    if not isinstance(private, dict) or not isinstance(report, dict):
        return ["U03_AGGREGATE_ARTIFACT_NOT_OBJECT"]
    if private.get("trace") != (private.get("semantic_record") or {}).get("trace"):
        reasons.append("U03_PRIVATE_AGGREGATE_TRACE_BINDING_MISMATCH")
    binding = private.get("tracked_report_binding") or {}
    if binding.get("path") != _display_path(run, run.tracked_report):
        reasons.append("U03_TRACKED_REPORT_PATH_BINDING_MISMATCH")
    if binding.get("bytes") != len(report_bytes):
        reasons.append("U03_TRACKED_REPORT_SIZE_BINDING_MISMATCH")
    if binding.get("sha256") != sha256(report_bytes).hexdigest():
        reasons.append("U03_TRACKED_REPORT_HASH_BINDING_MISMATCH")
    private_core = private.get("semantic_record")
    report_core = report.get("semantic_record")
    if not isinstance(private_core, dict) or private_core != report_core:
        reasons.append("U03_AGGREGATE_SEMANTIC_BINDING_MISMATCH")
        return list(dict.fromkeys(reasons))
    semantic_sha = sha256(_canonical_json_bytes(private_core)).hexdigest()
    if private.get("semantic_sha256") != semantic_sha or report.get("semantic_sha256") != semantic_sha:
        reasons.append("U03_AGGREGATE_SEMANTIC_HASH_MISMATCH")
    reasons.extend(_validate_semantic_core(private_core))
    if (run.repository_root / ".git").exists():
        aggregate_source = (private_core.get("trace") or {}).get("git_source_commit")
        trace_items = [private_core.get("trace")]
        trace_items.extend(
            item.get("trace") for item in (private_core.get("transactions") or []) if isinstance(item, dict)
        )
        for index, trace_item in enumerate(trace_items):
            source = trace_item.get("git_source_commit") if isinstance(trace_item, dict) else None
            if not isinstance(source, str) or _git(
                run.repository_root, "cat-file", "-e", f"{source}^{{commit}}"
            ).returncode != 0:
                reasons.append(f"U03_TRACE_COMMIT_{index}_MISSING")
            elif isinstance(aggregate_source, str) and _git(
                run.repository_root, "merge-base", "--is-ancestor", source, aggregate_source
            ).returncode != 0:
                reasons.append(f"U03_TRACE_COMMIT_{index}_NOT_ANCESTOR")
    transactions = private_core.get("transactions") or []
    if len(transactions) == 2:
        for contract, destination, transaction in zip(
            PETES_LAKE_CONTRACTS,
            (run.pre_destination, run.post_destination),
            transactions,
            strict=True,
        ):
            try:
                verification = _fresh_verify(contract, destination)
            except AcquisitionError:
                reasons.append(f"{contract.role}:U03_FRESH_PACKAGE_VERIFICATION_FAILED")
                continue
            if not _transaction_matches_fresh_verification(transaction, contract, verification):
                reasons.append(f"{contract.role}:U03_FRESH_REGISTRATION_BINDING_MISMATCH")
    return list(dict.fromkeys(reasons))


def _now_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _refresh_one(
    contract: AssetContract,
    *,
    metadata_refresh_fn: Callable[..., dict[str, Any]],
    observed_at_utc: str,
) -> dict[str, Any]:
    snapshot = metadata_refresh_fn(contract, observed_at_utc=observed_at_utc)
    reasons = validate_petes_lake_metadata(snapshot, (contract,))
    if reasons:
        raise AcquisitionError(
            "PETES_LAKE_METADATA_CONTRACT_REJECTED",
            role=contract.role,
            detail=",".join(reasons),
        )
    return snapshot


def _try_retain_aggregate_failure(
    run: PetesLakeOpticalRun, failure: dict[str, Any]
) -> None:
    if _path_present(run.aggregate_state):
        return
    try:
        _write_private_run_state(run, run.aggregate_state, failure)
    except AcquisitionError:
        pass


def _write_success_outputs(
    run: PetesLakeOpticalRun,
    trace: PetesLakeTrace,
    pre: dict[str, Any],
    post: dict[str, Any],
) -> dict[str, Any]:
    try:
        for contract, destination, transaction in zip(
            PETES_LAKE_CONTRACTS,
            (run.pre_destination, run.post_destination),
            (pre, post),
            strict=True,
        ):
            verification = _fresh_verify(contract, destination)
            if not _transaction_matches_fresh_verification(
                transaction, contract, verification
            ):
                raise AcquisitionError(
                    "PREPUBLICATION_REGISTRATION_BINDING_MISMATCH",
                    role=contract.role,
                )
    except AcquisitionError as error:
        failure = _failure_state(
            run,
            trace,
            error,
            stage="aggregate-prepublication",
            run_id=run.aggregate_run_id,
            credentials_exercised=False,
        )
        failure["pre_transaction"] = pre
        failure["post_transaction"] = post
        _try_retain_aggregate_failure(run, failure)
        raise
    private, report = _aggregate_payloads(run, trace, pre, post)
    # The private aggregate binds the planned report bytes first.  If tracked
    # report creation fails, aggregate-only remediation can finish without
    # deleting or reacquiring either registered archive.
    _write_private_run_state(run, run.aggregate_state, private)
    _write_tracked_report_no_overwrite(run, run.tracked_report, report)
    return report


def _load_transaction_evidence(
    run: PetesLakeOpticalRun,
    contract: AssetContract,
    verification: dict[str, Any],
) -> dict[str, Any]:
    registration = verification.get("registration") or {}
    expected_run_id = registration.get("run_id")
    if not isinstance(expected_run_id, str) or not expected_run_id:
        raise AcquisitionError("REMEDIATION_REGISTRATION_RUN_ID_MISSING", role=contract.role)
    candidates: list[dict[str, Any]] = []
    direct = run.run_state_parent / f"{expected_run_id}.json"
    paths = [direct]
    if run.run_state_parent.is_dir():
        paths.extend(sorted(run.run_state_parent.glob("*petes-lake-optical-intake-*.json")))
    for path in dict.fromkeys(paths):
        if not path.is_file():
            continue
        payload = _read_json_object(path)
        possible: list[Any] = [payload.get("pre_transaction"), payload.get("post_transaction")]
        semantic = payload.get("semantic_record") or {}
        if isinstance(semantic, dict):
            possible.extend(semantic.get("transactions") or [])
        possible.append(payload)
        for item in possible:
            if isinstance(item, dict) and _transaction_matches_fresh_verification(
                item, contract, verification
            ):
                candidates.append(item)
    unique = {
        sha256(_canonical_json_bytes(candidate)).hexdigest(): candidate for candidate in candidates
    }
    if not unique:
        raise AcquisitionError("REMEDIATION_TRANSACTION_EVIDENCE_MISSING", role=contract.role)
    if len(unique) != 1:
        raise AcquisitionError("REMEDIATION_TRANSACTION_EVIDENCE_AMBIGUOUS", role=contract.role)
    return next(iter(unique.values()))


def _reconstructed_transaction(
    run: PetesLakeOpticalRun,
    trace: PetesLakeTrace,
    contract: AssetContract,
    verification: dict[str, Any],
    metadata_snapshot: dict[str, Any],
) -> dict[str, Any]:
    registration = verification.get("registration") or {}
    run_id = registration.get("run_id")
    if not isinstance(run_id, str) or not run_id:
        raise AcquisitionError("REMEDIATION_REGISTRATION_RUN_ID_MISSING", role=contract.role)
    return {
        "unit_id": UNIT_ID,
        "generated_at_utc": run.generated_at_utc,
        "event_id": EVENT_ID,
        "event_group_id": EVENT_GROUP_ID,
        "pair_id": PAIR_ID,
        "run_id": run_id,
        "role": contract.role,
        "package_id": contract.package_id,
        "contract_version": CONTRACT_VERSION,
        "trace": trace.as_dict(),
        "metadata_snapshot": metadata_snapshot,
        "contract": _contract_summary(contract),
        "quarantine_path": None,
        "destination_path": _display_path(
            run,
            run.pre_destination if contract == PRE_CONTRACT else run.post_destination,
        ),
        "decision": "REGISTERED_EXACT_PETES_LAKE_SINGLETON",
        "credentials_exercised": False,
        "original_credentials_exercised": "not reconstructed",
        "download": {
            "status": "RECONSTRUCTED_FROM_IMMUTABLE_REGISTRATION",
            "provider_archive_request_performed": False,
        },
        "registration": registration,
        "verification": verification,
        "disposition": "pass",
        "next_dependency": "P2O4-T33-U03",
    }


def acquire_petes_lake_optical_pair(
    *,
    credentials: CdseCredentials,
    run: PetesLakeOpticalRun,
    trace: PetesLakeTrace,
    metadata_refresh_fn: Callable[..., dict[str, Any]] = refresh_petes_lake_metadata_for_role,
    observed_at_fn: Callable[[], str] = _now_utc,
    progress: Callable[[str, int, int], None] | None = None,
) -> dict[str, Any]:
    """Execute the exact r001 pre then post acquisition without reuse."""

    if run.mode not in {"full", "full-remediation"}:
        raise AcquisitionError("PETES_LAKE_FULL_OR_FULL_REMEDIATION_MODE_REQUIRED")
    if run.mode == "full" and run.revision != INITIAL_REVISION:
        raise AcquisitionError("PETES_LAKE_FULL_MODE_R001_REQUIRED")
    assert_no_overwrite_targets(run)
    pre_activity = {"credentials_exercised": False}
    try:
        pre_observed = observed_at_fn()
        pre_metadata = _refresh_one(
            PRE_CONTRACT,
            metadata_refresh_fn=metadata_refresh_fn,
            observed_at_utc=pre_observed,
        )
        pre_result = _acquire_singleton(
            contract=PRE_CONTRACT,
            credentials=credentials,
            quarantine=run.pre_quarantine,
            destination=run.pre_destination,
            generated_at_utc=run.generated_at_utc,
            run_id=run.pre_run_id,
            progress=progress,
            activity=pre_activity,
        )
    except AcquisitionError as error:
        failure = _failure_state(
            run,
            trace,
            error,
            stage="pre",
            run_id=run.pre_run_id,
            credentials_exercised=pre_activity["credentials_exercised"],
            quarantine=run.pre_quarantine,
            destination=run.pre_destination,
        )
        _write_private_run_state(run, run.pre_state, failure)
        aggregate_failure = dict(failure, run_id=run.aggregate_run_id)
        _try_retain_aggregate_failure(run, aggregate_failure)
        raise
    pre_state = _success_state(
        run,
        trace,
        PRE_CONTRACT,
        pre_result,
        quarantine=run.pre_quarantine,
        destination=run.pre_destination,
        metadata_snapshot=pre_metadata,
    )
    try:
        _write_private_run_state(run, run.pre_state, pre_state)
    except AcquisitionError as error:
        failure = _failure_state(
            run,
            trace,
            error,
            stage="pre-state",
            run_id=run.aggregate_run_id,
            credentials_exercised=True,
            destination=run.pre_destination,
        )
        failure["pre_transaction"] = pre_state
        _try_retain_aggregate_failure(run, failure)
        raise

    post_activity = {"credentials_exercised": False}
    try:
        post_observed = observed_at_fn()
        if post_observed == pre_observed:
            raise AcquisitionError("PRE_POST_METADATA_TIMESTAMPS_NOT_DISTINCT")
        post_metadata = _refresh_one(
            POST_CONTRACT,
            metadata_refresh_fn=metadata_refresh_fn,
            observed_at_utc=post_observed,
        )
        post_result = _acquire_singleton(
            contract=POST_CONTRACT,
            credentials=credentials,
            quarantine=run.post_quarantine,
            destination=run.post_destination,
            generated_at_utc=run.generated_at_utc,
            run_id=run.post_run_id,
            progress=progress,
            activity=post_activity,
        )
    except AcquisitionError as error:
        failure = _failure_state(
            run,
            trace,
            error,
            stage="post",
            run_id=run.post_run_id,
            credentials_exercised=post_activity["credentials_exercised"],
            quarantine=run.post_quarantine,
            destination=run.post_destination,
        )
        _write_private_run_state(run, run.post_state, failure)
        aggregate_failure = dict(failure, run_id=run.aggregate_run_id)
        aggregate_failure["pre_transaction"] = pre_state
        _try_retain_aggregate_failure(run, aggregate_failure)
        raise
    post_state = _success_state(
        run,
        trace,
        POST_CONTRACT,
        post_result,
        quarantine=run.post_quarantine,
        destination=run.post_destination,
        metadata_snapshot=post_metadata,
    )
    try:
        _write_private_run_state(run, run.post_state, post_state)
    except AcquisitionError as error:
        failure = _failure_state(
            run,
            trace,
            error,
            stage="post-state",
            run_id=run.aggregate_run_id,
            credentials_exercised=True,
            destination=run.post_destination,
        )
        failure["pre_transaction"] = pre_state
        failure["post_transaction"] = post_state
        _try_retain_aggregate_failure(run, failure)
        raise
    return _write_success_outputs(run, trace, pre_state, post_state)


def resume_petes_lake_post_only(
    *,
    credentials: CdseCredentials,
    run: PetesLakeOpticalRun,
    trace: PetesLakeTrace,
    metadata_refresh_fn: Callable[..., dict[str, Any]] = refresh_petes_lake_metadata_for_role,
    observed_at_fn: Callable[[], str] = _now_utc,
    progress: Callable[[str, int, int], None] | None = None,
) -> dict[str, Any]:
    """Acquire only post after freshly verifying immutable accepted pre r001."""

    if run.mode != "post-only":
        raise AcquisitionError("PETES_LAKE_POST_ONLY_MODE_REQUIRED")
    assert_no_overwrite_targets(run)
    pre_verification = _fresh_verify(PRE_CONTRACT, run.pre_destination)
    if not _registered_pre_run_is_authorized(pre_verification):
        raise AcquisitionError("REMEDIATION_AUTHORIZED_PRE_REGISTRATION_REQUIRED")
    pre_state = _load_transaction_evidence(run, PRE_CONTRACT, pre_verification)
    pre_observed = (pre_state.get("metadata_snapshot") or {}).get("observed_at_utc")
    post_activity = {"credentials_exercised": False}
    try:
        post_observed = observed_at_fn()
        if post_observed == pre_observed:
            raise AcquisitionError("PRE_POST_METADATA_TIMESTAMPS_NOT_DISTINCT")
        post_metadata = _refresh_one(
            POST_CONTRACT,
            metadata_refresh_fn=metadata_refresh_fn,
            observed_at_utc=post_observed,
        )
        post_result = _acquire_singleton(
            contract=POST_CONTRACT,
            credentials=credentials,
            quarantine=run.post_quarantine,
            destination=run.post_destination,
            generated_at_utc=run.generated_at_utc,
            run_id=run.post_run_id,
            progress=progress,
            activity=post_activity,
        )
    except AcquisitionError as error:
        failure = _failure_state(
            run,
            trace,
            error,
            stage="post-only",
            run_id=run.post_run_id,
            credentials_exercised=post_activity["credentials_exercised"],
            quarantine=run.post_quarantine,
            destination=run.post_destination,
        )
        _write_private_run_state(run, run.post_state, failure)
        aggregate_failure = dict(failure, run_id=run.aggregate_run_id)
        aggregate_failure["pre_transaction"] = pre_state
        _try_retain_aggregate_failure(run, aggregate_failure)
        raise
    post_state = _success_state(
        run,
        trace,
        POST_CONTRACT,
        post_result,
        quarantine=run.post_quarantine,
        destination=run.post_destination,
        metadata_snapshot=post_metadata,
    )
    try:
        _write_private_run_state(run, run.post_state, post_state)
    except AcquisitionError as error:
        failure = _failure_state(
            run,
            trace,
            error,
            stage="post-only-state",
            run_id=run.aggregate_run_id,
            credentials_exercised=True,
            destination=run.post_destination,
        )
        failure["pre_transaction"] = pre_state
        failure["post_transaction"] = post_state
        _try_retain_aggregate_failure(run, failure)
        raise
    return _write_success_outputs(run, trace, pre_state, post_state)


def finalize_petes_lake_aggregate_only(
    *,
    run: PetesLakeOpticalRun,
    trace: PetesLakeTrace,
    metadata_refresh_fn: Callable[..., dict[str, Any]] = refresh_petes_lake_metadata_for_role,
    observed_at_fn: Callable[[], str] = _now_utc,
) -> dict[str, Any]:
    """Finish dual-artifact binding from two immutable verified packages."""

    if run.mode != "aggregate-only":
        raise AcquisitionError("PETES_LAKE_AGGREGATE_ONLY_MODE_REQUIRED")
    assert_no_overwrite_targets(run)
    pre_verification = _fresh_verify(PRE_CONTRACT, run.pre_destination)
    post_verification = _fresh_verify(POST_CONTRACT, run.post_destination)
    if not _registered_pre_run_is_authorized(pre_verification):
        raise AcquisitionError("REMEDIATION_AUTHORIZED_PRE_REGISTRATION_REQUIRED")
    try:
        pre_state = _load_transaction_evidence(run, PRE_CONTRACT, pre_verification)
        post_state = _load_transaction_evidence(run, POST_CONTRACT, post_verification)
    except AcquisitionError as error:
        if error.reason_code != "REMEDIATION_TRANSACTION_EVIDENCE_MISSING":
            raise
        pre_observed = observed_at_fn()
        post_observed = observed_at_fn()
        if pre_observed == post_observed:
            raise AcquisitionError("PRE_POST_METADATA_TIMESTAMPS_NOT_DISTINCT")
        pre_metadata = _refresh_one(
            PRE_CONTRACT,
            metadata_refresh_fn=metadata_refresh_fn,
            observed_at_utc=pre_observed,
        )
        post_metadata = _refresh_one(
            POST_CONTRACT,
            metadata_refresh_fn=metadata_refresh_fn,
            observed_at_utc=post_observed,
        )
        pre_state = _reconstructed_transaction(
            run, trace, PRE_CONTRACT, pre_verification, pre_metadata
        )
        post_state = _reconstructed_transaction(
            run, trace, POST_CONTRACT, post_verification, post_metadata
        )
    return _write_success_outputs(run, trace, pre_state, post_state)
