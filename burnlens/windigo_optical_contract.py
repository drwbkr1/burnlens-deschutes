"""Fail-closed sequential custody for the exact Windigo Sentinel-2 pair."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import subprocess
from typing import Any, Callable, Iterable
from urllib.request import Request, urlopen

from .cross_event_optical_contract import CdseCredentials
from .paired_intake import AssetContract, validate_asset_contracts, verify_registered_package
from .provider_acquisition import (
    AcquisitionError,
    USER_AGENT,
    _open_json,
    classify_transfer_failure,
    promote_quarantine_no_overwrite,
    stream_cdse_asset_with_retries,
    write_private_state,
)


SOFTWARE_VERSION = "0.46.0"
UNIT_ID = "P2O4-T35-U02"
TASK_ISSUE = 534
EVENT_ID = "OR4336312205020220730"
EVENT_GROUP_ID = "event-windigo-2022"
SOURCE_RECORD_ID = "SOURCE-2026-036"
TERMS_REVIEW_ID = "TERMS-2026-031"
PAIR_ID = "windigo-s2-optical-pair-v0.1.0"
PRE_PACKAGE_ID = "windigo-s2-optical-pre-v0.1.0"
POST_PACKAGE_ID = "windigo-s2-optical-post-v0.1.0"
CONTRACT_VERSION = "windigo-optical-intake-contract-v0.1.0"
REPORT_ID = "WINDIGO-OPTICAL-CUSTODY-2026-001"
REPORT_SCHEMA_VERSION = "0.1.0"
REPOSITORY = "drwbkr1/burnlens-deschutes"
BRANCH = "codex/p2o4-t35-windigo-deadline-gate"
GIT_BASE_COMMIT = "0e58459ea45f509eca537223d872fd6992efb291"
U01_ENTRY_COMMIT = "9fba1c7a2b860fedf0cac70e355cffaa6a7dc5d8"
PRODUCTION_RUN_DATE = "2026-07-23"
REVISION = "r001"
MAX_TRANSFER_ATTEMPTS = 5
PRE_FAILURE_R001_BYTES = 2_798
PRE_FAILURE_R001_SHA256 = (
    "e02fce0508a763b7603f72e50bdf3c25c721fa2f15c8e3a26a6598d3a11b7af6"
)
PRE_PARTIAL_R001_BYTES = 134_217_728
PRE_PARTIAL_R001_SHA256 = (
    "5fac4900d65591f3c44c6ee3dec3939a27b0759e22656e0a7c2d5bac38c54c75"
)

U01_BINDINGS = {
    "records/phase-two/prechecks/PRECHECK-2026-059.md": (
        7_031,
        "b3e2f66d0fdc15a022556387a604208591cc90bf494508dd8134c5ea8089f506",
    ),
    "records/phase-two/sources/SOURCE-2026-036.md": (
        8_940,
        "d8ea91debe6f02f4ca672084ad35a02e80cda1c10469cc391d8174bb8b724128",
    ),
    "records/phase-two/terms/TERMS-2026-031.md": (
        5_902,
        "4ba57312c3be30c1c0b0c288b9d488cb3303159db275b2a477ecd5eb299d0f15",
    ),
    "records/phase-two/intake/P2O4-T35-U01-windigo-metadata.json": (
        36_954,
        "15129b379ceec032840a897c2feb5f541ff5f6f6e83ffbafd19f0df914d6774e",
    ),
}

WARNING = (
    "Experimental BurnLens CV evidence. Not official wildfire information. "
    "Not emergency guidance. Not field validation or operational support. "
    "Official sources govern."
)


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
    role="windigo-2022-pre",
    package_id=PRE_PACKAGE_ID,
    provider_id="f1111cd2-acb1-4324-9b48-854e2e71a384",
    safe_name="S2A_MSIL2A_20220726T185931_N0510_R013_T10TEP_20240712T042551.SAFE",
    size_bytes=1_185_125_439,
    md5="6103928264ef49f78cbc6200e613b158",
    blake3="13541bf3ea1c56269b3b4667e0051f7d95bbe7b64b69a9228ce1f2f9899fa17f",
)
POST_CONTRACT = _contract(
    role="windigo-2022-post",
    package_id=POST_PACKAGE_ID,
    provider_id="10bb27c6-5df5-44f1-9a72-517c696cb5e1",
    safe_name="S2A_MSIL2A_20220815T185931_N0510_R013_T10TEP_20240703T124031.SAFE",
    size_bytes=1_187_986_637,
    md5="9aa84788fd136aad2da9a30dacc17330",
    blake3="1923a7089f58278add5f2f2692139cbf4bf2a900ec8ca4afb8a4b8391ce89cff",
)
WINDIGO_CONTRACTS = (PRE_CONTRACT, POST_CONTRACT)

EXPECTED_METADATA = {
    PRE_CONTRACT.role: {
        "acquisition_utc": "2022-07-26T18:59:31.024000Z",
        "publication_utc": "2024-12-24T07:06:56.947635Z",
    },
    POST_CONTRACT.role: {
        "acquisition_utc": "2022-08-15T18:59:31.024000Z",
        "publication_utc": "2025-03-18T00:52:08.078142Z",
    },
}

_PRODUCT_PATTERN = re.compile(
    r"^(?P<platform>S2[ABCD])_MSIL2A_\d{8}T\d{6}_"
    r"N(?P<baseline>\d{4})_R(?P<orbit>\d{3})_T(?P<tile>[0-9A-Z]{5})_"
    r"\d{8}T\d{6}\.SAFE$"
)


def _singleton_validator(expected: AssetContract) -> Callable[[Iterable[AssetContract]], list[str]]:
    def validate(contracts: Iterable[AssetContract]) -> list[str]:
        items = list(contracts)
        reasons = validate_asset_contracts(items)
        if items != [expected]:
            reasons.append(f"{expected.role}:SINGLETON_CONTRACT_MISMATCH")
        return reasons

    return validate


def validate_windigo_contracts(
    contracts: Iterable[AssetContract] = WINDIGO_CONTRACTS,
) -> list[str]:
    items = list(contracts)
    reasons: list[str] = []
    if items != list(WINDIGO_CONTRACTS):
        reasons.append("WINDIGO_ORDERED_PAIR_CONTRACT_MISMATCH")
    if len(items) != 2:
        reasons.append("CONTRACT_REQUIRES_EXACT_PRE_POST_PAIR")
        return reasons
    for expected, observed in zip(WINDIGO_CONTRACTS, items, strict=True):
        reasons.extend(_singleton_validator(expected)((observed,)))
    parsed = [_PRODUCT_PATTERN.fullmatch(item.native_id) for item in items]
    if any(item is None for item in parsed):
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
            reasons.append("WINDIGO_PAIR_IDENTITY_MISMATCH")
    return list(dict.fromkeys(reasons))


def _metadata_url(contract: AssetContract) -> str:
    return (
        "https://catalogue.dataspace.copernicus.eu/odata/v1/"
        f"Products({contract.provider_id})"
        "?$select=Id,Name,ContentLength,Online,PublicationDate,Checksum,ContentDate,S3Path"
    )


def _normalize_metadata(payload: dict[str, Any], *, role: str) -> dict[str, Any]:
    checksums = {
        str(item.get("Algorithm", "")).upper(): str(item.get("Value", "")).lower()
        for item in payload.get("Checksum") or []
        if isinstance(item, dict)
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
    }


def validate_windigo_metadata(
    snapshot: dict[str, Any],
    contracts: Iterable[AssetContract] = WINDIGO_CONTRACTS,
) -> list[str]:
    items = list(contracts)
    reasons = validate_windigo_contracts(items)
    if snapshot.get("source_record_id") != SOURCE_RECORD_ID:
        reasons.append("METADATA_SOURCE_RECORD_MISMATCH")
    if snapshot.get("terms_review_id") != TERMS_REVIEW_ID:
        reasons.append("METADATA_TERMS_RECORD_MISMATCH")
    if snapshot.get("live_refresh_performed") is not True:
        reasons.append("LIVE_METADATA_REFRESH_REQUIRED")
    records = snapshot.get("records")
    if not isinstance(records, list) or len(records) != len(items):
        return [*reasons, "METADATA_RECORD_SET_MISMATCH"]
    if [item.get("role") for item in records if isinstance(item, dict)] != [
        item.role for item in items
    ]:
        reasons.append("METADATA_ORDERED_ROLE_SET_MISMATCH")
    for contract, record in zip(items, records, strict=True):
        if not isinstance(record, dict):
            reasons.append(f"{contract.role}:RECORD_INVALID")
            continue
        expected = EXPECTED_METADATA[contract.role]
        comparisons = {
            "EVENT_ID": EVENT_ID,
            "EVENT_GROUP": EVENT_GROUP_ID,
            "PROVIDER_ID": contract.provider_id,
            "NATIVE_ID": contract.native_id,
            "SIZE": contract.expected_size_bytes,
            "ACQUISITION": expected["acquisition_utc"],
            "PUBLICATION": expected["publication_utc"],
        }
        fields = {
            "EVENT_ID": record.get("event_id"),
            "EVENT_GROUP": record.get("event_group_id"),
            "PROVIDER_ID": record.get("provider_id"),
            "NATIVE_ID": record.get("native_id"),
            "SIZE": record.get("size_bytes"),
            "ACQUISITION": record.get("acquisition_utc"),
            "PUBLICATION": record.get("publication_utc"),
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


def refresh_windigo_metadata(
    *,
    observed_at_utc: str,
    urlopen_fn: Callable[..., Any] = urlopen,
) -> dict[str, Any]:
    records = []
    headers = {"Accept": "application/json", "User-Agent": USER_AGENT}
    for contract in WINDIGO_CONTRACTS:
        payload = _open_json(
            Request(_metadata_url(contract), headers=headers),
            urlopen_fn=urlopen_fn,
        )
        records.append(_normalize_metadata(payload, role=contract.role))
    snapshot = {
        "observed_at_utc": observed_at_utc,
        "source_record_id": SOURCE_RECORD_ID,
        "terms_review_id": TERMS_REVIEW_ID,
        "live_refresh_performed": True,
        "records": records,
    }
    reasons = validate_windigo_metadata(snapshot)
    if reasons:
        raise AcquisitionError("WINDIGO_PUBLIC_METADATA_DRIFT", detail=",".join(reasons))
    return snapshot


@dataclass(frozen=True)
class WindigoOpticalRun:
    repository_root: Path
    generated_at_utc: str

    @classmethod
    def create(cls, *, repository_root: Path, generated_at_utc: str) -> "WindigoOpticalRun":
        if not generated_at_utc.endswith("Z"):
            raise ValueError("generated_at_utc must be explicit UTC")
        return cls(repository_root=repository_root.resolve(), generated_at_utc=generated_at_utc)

    @property
    def pre_quarantine(self) -> Path:
        return self.repository_root / "downloads/phase-two/quarantine/P2O4-T35-U02/windigo-optical-pre-r001"

    @property
    def post_quarantine(self) -> Path:
        return self.repository_root / "downloads/phase-two/quarantine/P2O4-T35-U02/windigo-optical-post-r001"

    @property
    def pre_destination(self) -> Path:
        return self.repository_root / "downloads/phase-two/raw" / PRE_PACKAGE_ID

    @property
    def post_destination(self) -> Path:
        return self.repository_root / "downloads/phase-two/raw" / POST_PACKAGE_ID

    @property
    def state_parent(self) -> Path:
        return self.repository_root / "downloads/phase-two/runs/P2O4-T35-U02"

    @property
    def pre_state(self) -> Path:
        return self.state_parent / f"BL-{PRODUCTION_RUN_DATE}-windigo-optical-pre-r002.json"

    @property
    def pre_failure_state(self) -> Path:
        return self.state_parent / f"BL-{PRODUCTION_RUN_DATE}-windigo-optical-pre-r001.json"

    @property
    def post_state(self) -> Path:
        return self.state_parent / f"BL-{PRODUCTION_RUN_DATE}-windigo-optical-post-r001.json"

    @property
    def aggregate_state(self) -> Path:
        return self.state_parent / f"BL-{PRODUCTION_RUN_DATE}-windigo-optical-intake-r001.json"

    @property
    def tracked_report(self) -> Path:
        return self.repository_root / "samples/cross-event/phase-two/windigo" / f"{REPORT_ID}.json"


@dataclass(frozen=True)
class WindigoTrace:
    git_source_commit: str
    resumable_pre_bytes: int = 0

    def as_dict(self) -> dict[str, Any]:
        return {
            "repository": REPOSITORY,
            "branch": BRANCH,
            "task_issue": TASK_ISSUE,
            "git_base_commit": GIT_BASE_COMMIT,
            "u01_entry_commit": U01_ENTRY_COMMIT,
            "git_source_commit": self.git_source_commit,
            "resumable_pre_bytes": self.resumable_pre_bytes,
            "prior_local_interruption": (
                "LOCAL_PROGRESS_PIPE_CLOSED_RETAINED_EXACT_PARTIAL"
                if self.resumable_pre_bytes
                else None
            ),
            "retained_pre_failure": (
                {
                    "run_id": f"BL-{PRODUCTION_RUN_DATE}-windigo-optical-pre-r001",
                    "bytes": PRE_FAILURE_R001_BYTES,
                    "sha256": PRE_FAILURE_R001_SHA256,
                    "partial_bytes": PRE_PARTIAL_R001_BYTES,
                    "partial_sha256": PRE_PARTIAL_R001_SHA256,
                    "disposition": "failed-immutable-superseded-by-r002-resume",
                }
                if self.resumable_pre_bytes
                else None
            ),
            "u01_bindings": {
                path: {"bytes": size, "sha256": digest}
                for path, (size, digest) in U01_BINDINGS.items()
            },
        }


def _git(root: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *arguments],
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


def _resumable_pre_bytes(run: WindigoOpticalRun) -> int:
    """Accept only the exact interrupted pre partial and no other entry."""

    quarantine = run.pre_quarantine
    if not _path_present(quarantine):
        return 0
    is_junction = getattr(quarantine, "is_junction", None)
    if (
        quarantine.is_symlink()
        or bool(is_junction and is_junction())
        or not quarantine.is_dir()
    ):
        raise AcquisitionError("WINDIGO_PRE_RESUME_QUARANTINE_INVALID")
    part = quarantine / f"{PRE_CONTRACT.expected_filename}.part"
    entries = list(quarantine.iterdir())
    if entries != [part] or not part.is_file() or part.is_symlink():
        raise AcquisitionError("WINDIGO_PRE_RESUME_ROSTER_MISMATCH")
    observed = part.lstat()
    if observed.st_nlink != 1:
        raise AcquisitionError("WINDIGO_PRE_RESUME_MULTILINK")
    if observed.st_size != PRE_PARTIAL_R001_BYTES:
        raise AcquisitionError("WINDIGO_PRE_RESUME_SIZE_INVALID")
    if _sha256_file(part) != PRE_PARTIAL_R001_SHA256:
        raise AcquisitionError("WINDIGO_PRE_RESUME_HASH_MISMATCH")
    failure = run.pre_failure_state
    if (
        not failure.is_file()
        or failure.stat().st_size != PRE_FAILURE_R001_BYTES
        or _sha256_file(failure) != PRE_FAILURE_R001_SHA256
    ):
        raise AcquisitionError("WINDIGO_PRE_FAILURE_BINDING_MISMATCH")
    return observed.st_size


def verify_windigo_repository_preflight(
    run: WindigoOpticalRun,
    *,
    existing_success_outputs: bool = False,
) -> WindigoTrace:
    root = run.repository_root
    top = _git(root, "rev-parse", "--show-toplevel")
    if top.returncode != 0 or Path(top.stdout.strip()).resolve() != root:
        raise AcquisitionError("WINDIGO_REPOSITORY_ROOT_MISMATCH")
    branch = _git(root, "branch", "--show-current")
    if branch.returncode != 0 or branch.stdout.strip() != BRANCH:
        raise AcquisitionError("WINDIGO_BRANCH_MISMATCH")
    origin = _git(root, "config", "--get", "remote.origin.url")
    normalized_origin = origin.stdout.strip().lower().replace("\\", "/")
    if origin.returncode != 0 or REPOSITORY not in normalized_origin:
        raise AcquisitionError("WINDIGO_ORIGIN_MISMATCH")
    head = _git(root, "rev-parse", "HEAD")
    if head.returncode != 0 or re.fullmatch(r"[0-9a-f]{40}", head.stdout.strip()) is None:
        raise AcquisitionError("WINDIGO_COMMITTED_HEAD_REQUIRED")
    remote = _git(root, "rev-parse", f"origin/{BRANCH}")
    if remote.returncode != 0 or remote.stdout.strip() != head.stdout.strip():
        raise AcquisitionError("WINDIGO_REMOTE_HEAD_MISMATCH")
    status = _git(root, "status", "--porcelain=v1", "--untracked-files=all")
    allowed = f"?? {run.tracked_report.relative_to(root).as_posix()}" if existing_success_outputs else ""
    if status.returncode != 0 or status.stdout.strip().replace("\\", "/") != allowed:
        raise AcquisitionError("WINDIGO_WORKTREE_NOT_CLEAN")
    for ancestor, reason in (
        (GIT_BASE_COMMIT, "WINDIGO_BASE_NOT_ANCESTOR"),
        (U01_ENTRY_COMMIT, "WINDIGO_U01_NOT_ANCESTOR"),
    ):
        if _git(root, "merge-base", "--is-ancestor", ancestor, head.stdout.strip()).returncode != 0:
            raise AcquisitionError(reason)
    for relative, (size, digest) in U01_BINDINGS.items():
        path = root / relative
        if not path.is_file() or path.stat().st_size != size or _sha256_file(path) != digest:
            raise AcquisitionError("WINDIGO_U01_BINDING_MISMATCH", detail=relative)
    resumable_pre_bytes = _resumable_pre_bytes(run)
    private_paths = (
        run.pre_quarantine,
        run.post_quarantine,
        run.pre_destination,
        run.post_destination,
        run.pre_failure_state,
        run.pre_state,
        run.post_state,
        run.aggregate_state,
    )
    for path in private_paths:
        relative = path.relative_to(root).as_posix()
        if _git(root, "check-ignore", "--quiet", "--no-index", "--", relative).returncode != 0:
            raise AcquisitionError("WINDIGO_PRIVATE_PATH_NOT_IGNORED", detail=relative)
        if _git(root, "ls-files", "--error-unmatch", "--", relative).returncode != 1:
            raise AcquisitionError("WINDIGO_PRIVATE_PATH_TRACKED", detail=relative)
    report_relative = run.tracked_report.relative_to(root).as_posix()
    if _git(root, "check-ignore", "--quiet", "--no-index", "--", report_relative).returncode != 1:
        raise AcquisitionError("WINDIGO_TRACKED_REPORT_IGNORED")
    if _git(root, "ls-files", "--error-unmatch", "--", report_relative).returncode != 1:
        raise AcquisitionError("WINDIGO_TRACKED_REPORT_ALREADY_TRACKED")
    targets = (*private_paths, run.tracked_report)
    if existing_success_outputs:
        if not all(path.is_file() for path in (run.pre_state, run.post_state, run.aggregate_state, run.tracked_report)):
            raise AcquisitionError("WINDIGO_SUCCESS_OUTPUTS_MISSING")
    else:
        resumable_pre_bytes = _resumable_pre_bytes(run)
        present = [
            path.relative_to(root).as_posix()
            for path in targets
            if _path_present(path)
            and not (
                resumable_pre_bytes
                and path in {run.pre_quarantine, run.pre_failure_state}
            )
        ]
        if present:
            raise AcquisitionError("WINDIGO_NO_OVERWRITE_TARGET_EXISTS", detail=",".join(present))
    return WindigoTrace(
        git_source_commit=head.stdout.strip(),
        resumable_pre_bytes=resumable_pre_bytes,
    )


def _write_tracked_report(run: WindigoOpticalRun, payload: dict[str, Any]) -> None:
    path = run.tracked_report
    path.parent.mkdir(parents=True, exist_ok=True)
    if _path_present(path):
        raise AcquisitionError("WINDIGO_TRACKED_REPORT_OVERWRITE_REFUSED")
    relative = path.relative_to(run.repository_root).as_posix()
    if _git(run.repository_root, "check-ignore", "--quiet", "--no-index", "--", relative).returncode != 1:
        raise AcquisitionError("WINDIGO_TRACKED_REPORT_IGNORED")
    data = (json.dumps(payload, indent=2) + "\n").encode("utf-8")
    try:
        with path.open("xb") as handle:
            if handle.write(data) != len(data):
                raise AcquisitionError("WINDIGO_TRACKED_REPORT_SHORT_WRITE")
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError:
        raise AcquisitionError("WINDIGO_TRACKED_REPORT_OVERWRITE_REFUSED") from None


def _acquire_singleton(
    *,
    run: WindigoOpticalRun,
    trace: WindigoTrace,
    credentials: CdseCredentials,
    contract: AssetContract,
    metadata_record: dict[str, Any],
    quarantine: Path,
    destination: Path,
    state_path: Path,
    run_id: str,
    progress: Callable[[str, int, int], None] | None,
) -> dict[str, Any]:
    validator = _singleton_validator(contract)
    attempts: list[dict[str, Any]] = []
    if contract == PRE_CONTRACT and trace.resumable_pre_bytes:
        attempts.append(
            {
                "attempt_id": f"{run_id}-a000",
                "outcome": "interrupted",
                "reason_code": "LOCAL_PROGRESS_PIPE_CLOSED",
                "classification": "RETRYABLE_LOCAL_ORCHESTRATION",
                "retained_partial_bytes": trace.resumable_pre_bytes,
            }
        )
    try:
        for attempt in range(1, MAX_TRANSFER_ATTEMPTS + 1):
            try:
                download = stream_cdse_asset_with_retries(
                    contract,
                    quarantine,
                    username=credentials.username,
                    password=credentials.password,
                    max_attempts=1,
                    timeout_seconds=180,
                    progress=progress,
                )
            except AcquisitionError as error:
                classification = classify_transfer_failure(error)
                attempts.append(
                    {
                        "attempt_id": f"{run_id}-a{attempt:03d}",
                        "outcome": "failed",
                        "reason_code": error.reason_code,
                        "detail": error.detail,
                        "classification": classification,
                    }
                )
                if classification.startswith("RETRYABLE_") and attempt < MAX_TRANSFER_ATTEMPTS:
                    continue
                raise
            attempts.append(
                {
                    "attempt_id": f"{run_id}-a{attempt:03d}",
                    "outcome": "succeeded",
                    "classification": "completed",
                }
            )
            download = dict(download)
            download["attempt_count"] = attempt
            break
        else:
            raise AcquisitionError("WINDIGO_TRANSFER_ATTEMPTS_EXHAUSTED", role=contract.role)
        registration = promote_quarantine_no_overwrite(
            quarantine,
            destination,
            (contract,),
            generated_at_utc=run.generated_at_utc,
            run_id=run_id,
            synthetic_fixture=False,
            contract_validator=validator,
            contract_version=CONTRACT_VERSION,
        )
        verification = verify_registered_package(
            destination,
            (contract,),
            contract_validator=validator,
            contract_version=CONTRACT_VERSION,
        )
        if not verification["accepted_as_unchanged_registered_package"]:
            raise AcquisitionError(
                "WINDIGO_POST_PROMOTION_VERIFICATION_FAILED",
                role=contract.role,
            )
    except (AcquisitionError, OSError, ValueError) as error:
        if not _path_present(state_path):
            failure = {
                "state_schema_version": "0.1.0",
                "unit_id": UNIT_ID,
                "run_id": run_id,
                "generated_at_utc": run.generated_at_utc,
                "event_id": EVENT_ID,
                "event_group_id": EVENT_GROUP_ID,
                "pair_id": PAIR_ID,
                "contract_version": CONTRACT_VERSION,
                "trace": trace.as_dict(),
                "metadata_record": metadata_record,
                "attempts": attempts,
                "failure": {
                    "reason_code": (
                        error.reason_code
                        if isinstance(error, AcquisitionError)
                        else "LOCAL_TRANSACTION_FAILURE"
                    ),
                    "detail": (
                        error.detail
                        if isinstance(error, AcquisitionError)
                        else type(error).__name__
                    ),
                },
                "credentials_exercised": True,
                "decision": "FAILED_WINDIGO_OPTICAL_SINGLETON_RETAIN_EVIDENCE",
                "warning": WARNING,
            }
            write_private_state(state_path, failure, repo_root=run.repository_root)
        raise
    state = {
        "state_schema_version": "0.1.0",
        "unit_id": UNIT_ID,
        "run_id": run_id,
        "generated_at_utc": run.generated_at_utc,
        "event_id": EVENT_ID,
        "event_group_id": EVENT_GROUP_ID,
        "pair_id": PAIR_ID,
        "contract_version": CONTRACT_VERSION,
        "trace": trace.as_dict(),
        "metadata_record": metadata_record,
        "attempts": attempts,
        "download": download,
        "registration": registration,
        "verification": verification,
        "credentials_exercised": True,
        "decision": "REGISTERED_EXACT_WINDIGO_OPTICAL_SINGLETON",
        "warning": WARNING,
    }
    write_private_state(state_path, state, repo_root=run.repository_root)
    return state


def _public_package(state: dict[str, Any]) -> dict[str, Any]:
    verification = state["verification"]
    observation = verification["observations"][0]
    registration = verification["registration"]
    return {
        "role": observation["role"],
        "provider_id": observation["provider_id"],
        "native_id": observation["native_id"],
        "bytes": observation["observed_bytes"],
        "local_hashes": observation["local_hashes"],
        "registration_manifest_sha256": verification["registration_manifest_sha256"],
        "registration_run_id": registration["run_id"],
        "archive_container": observation["container_details"],
        "decision": state["decision"],
    }


def acquire_windigo_optical_pair(
    *,
    run: WindigoOpticalRun,
    trace: WindigoTrace,
    credentials: CdseCredentials,
    metadata_snapshot: dict[str, Any],
    progress: Callable[[str, int, int], None] | None = None,
) -> dict[str, Any]:
    reasons = validate_windigo_metadata(metadata_snapshot)
    if reasons:
        raise AcquisitionError("WINDIGO_METADATA_REJECTED", detail=",".join(reasons))
    pre = _acquire_singleton(
        run=run,
        trace=trace,
        credentials=credentials,
        contract=PRE_CONTRACT,
        metadata_record=metadata_snapshot["records"][0],
        quarantine=run.pre_quarantine,
        destination=run.pre_destination,
        state_path=run.pre_state,
        run_id=(
            f"BL-{PRODUCTION_RUN_DATE}-windigo-optical-pre-r002"
            if trace.resumable_pre_bytes
            else f"BL-{PRODUCTION_RUN_DATE}-windigo-optical-pre-r001"
        ),
        progress=progress,
    )
    # The post request is unreachable unless the promoted pre package has just
    # passed a complete rehash and registration verification.
    pre_verify = verify_registered_package(
        run.pre_destination,
        (PRE_CONTRACT,),
        contract_validator=_singleton_validator(PRE_CONTRACT),
        contract_version=CONTRACT_VERSION,
    )
    if not pre_verify["accepted_as_unchanged_registered_package"]:
        raise AcquisitionError("WINDIGO_PRE_DEPENDENCY_FAILED")
    post = _acquire_singleton(
        run=run,
        trace=trace,
        credentials=credentials,
        contract=POST_CONTRACT,
        metadata_record=metadata_snapshot["records"][1],
        quarantine=run.post_quarantine,
        destination=run.post_destination,
        state_path=run.post_state,
        run_id=f"BL-{PRODUCTION_RUN_DATE}-windigo-optical-post-r001",
        progress=progress,
    )
    aggregate = {
        "state_schema_version": "0.1.0",
        "unit_id": UNIT_ID,
        "run_id": f"BL-{PRODUCTION_RUN_DATE}-windigo-optical-intake-r001",
        "generated_at_utc": run.generated_at_utc,
        "event_id": EVENT_ID,
        "event_group_id": EVENT_GROUP_ID,
        "pair_id": PAIR_ID,
        "contract_version": CONTRACT_VERSION,
        "trace": trace.as_dict(),
        "transaction_order": [PRE_CONTRACT.role, POST_CONTRACT.role],
        "metadata_snapshot": metadata_snapshot,
        "private_states": [run.pre_state.name, run.post_state.name],
        "credentials_exercised": True,
        "decision": "REGISTERED_EXACT_WINDIGO_OPTICAL_PAIR",
        "warning": WARNING,
    }
    write_private_state(run.aggregate_state, aggregate, repo_root=run.repository_root)
    report = {
        "report_id": REPORT_ID,
        "report_schema_version": REPORT_SCHEMA_VERSION,
        "software_version": SOFTWARE_VERSION,
        "unit_id": UNIT_ID,
        "run_id": aggregate["run_id"],
        "generated_at_utc": run.generated_at_utc,
        "event_id": EVENT_ID,
        "event_group_id": EVENT_GROUP_ID,
        "pair_id": PAIR_ID,
        "contract_version": CONTRACT_VERSION,
        "trace": trace.as_dict(),
        "transaction_order": aggregate["transaction_order"],
        "packages": [_public_package(pre), _public_package(post)],
        "expected_combined_bytes": sum(item.expected_size_bytes for item in WINDIGO_CONTRACTS),
        "gate_results": {
            "exact_current_odata_identity": "pass",
            "sequential_singleton_custody": "pass",
            "provider_md5_blake3": "pass",
            "local_sha256_md5_blake3": "pass",
            "safe_zip_root_manifest_crc": "pass",
            "post_promotion_rehash": "pass",
            "u03_local_pixel_fitness": "not executed",
            "reference_delivery": "not requested",
            "candidate_label_dataset_split_baseline_model": "not created",
        },
        "retained_failures": (
            [trace.as_dict()["retained_pre_failure"]]
            if trace.resumable_pre_bytes
            else []
        ),
        "decision": "PASS_WINDIGO_OPTICAL_CUSTODY_AUTHORIZE_REFERENCE_REQUEST_PREFLIGHT",
        "warning": WARNING,
    }
    _write_tracked_report(run, report)
    return report


def verify_windigo_completed(run: WindigoOpticalRun) -> list[str]:
    reasons: list[str] = []
    for contract, destination in (
        (PRE_CONTRACT, run.pre_destination),
        (POST_CONTRACT, run.post_destination),
    ):
        verification = verify_registered_package(
            destination,
            (contract,),
            contract_validator=_singleton_validator(contract),
            contract_version=CONTRACT_VERSION,
        )
        if not verification["accepted_as_unchanged_registered_package"]:
            reasons.append(f"{contract.role}:REGISTERED_PACKAGE")
    for path in (run.pre_state, run.post_state, run.aggregate_state, run.tracked_report):
        if not path.is_file():
            reasons.append(f"{path.name}:MISSING")
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            reasons.append(f"{path.name}:INVALID_JSON")
            continue
        if not isinstance(payload, dict):
            reasons.append(f"{path.name}:NOT_OBJECT")
    if run.tracked_report.is_file():
        report = json.loads(run.tracked_report.read_text(encoding="utf-8"))
        if report.get("decision") != "PASS_WINDIGO_OPTICAL_CUSTODY_AUTHORIZE_REFERENCE_REQUEST_PREFLIGHT":
            reasons.append("TRACKED_REPORT_DECISION")
        if report.get("expected_combined_bytes") != 2_373_112_076:
            reasons.append("TRACKED_REPORT_BYTES")
    if run.pre_failure_state.is_file():
        if (
            run.pre_failure_state.stat().st_size != PRE_FAILURE_R001_BYTES
            or _sha256_file(run.pre_failure_state) != PRE_FAILURE_R001_SHA256
        ):
            reasons.append("PRE_FAILURE_R001_BINDING")
    return reasons
