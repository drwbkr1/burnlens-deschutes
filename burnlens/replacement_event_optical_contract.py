"""Controlled sequential custody for the exact Ward Creek Sentinel-2 pair."""

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
import zipfile

import rasterio

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


SOFTWARE_VERSION = "0.50.0"
UNIT_ID = "P2O4-T39-U02"
TASK_ISSUE = 554
EVENT_ID = "OR4494912090120190812"
EVENT_GROUP_ID = "event-ward-creek-2019"
SOURCE_RECORD_ID = "SOURCE-2026-038"
TERMS_REVIEW_ID = "TERMS-2026-033"
PAIR_ID = "ward-creek-s2-optical-pair-v0.1.0"
PRE_PACKAGE_ID = "ward-creek-s2-optical-pre-v0.1.0"
POST_PACKAGE_ID = "ward-creek-s2-optical-post-v0.1.0"
CONTRACT_VERSION = "ward-creek-optical-intake-contract-v0.1.0"
INTAKE_ID = "p2o4-t39-u02-ward-creek-optical-r001"
REPORT_ID = "WARD-CREEK-OPTICAL-CUSTODY-2026-001"
REPORT_SCHEMA_VERSION = "0.1.0"
REPOSITORY = "drwbkr1/burnlens-deschutes"
BRANCH = "codex/p2o4-t39-replacement-event"
GIT_BASE_COMMIT = "657ba657ab9d23964dcaf76d377aec3a10e814da"
U01_ENTRY_COMMIT = "11c5ad377cb6a65242720ae819c769b29b82cee2"
PRODUCTION_RUN_DATE = "2026-07-24"
MAX_TRANSFER_ATTEMPTS = 2
TRANSFER_TIMEOUT_SECONDS = 600

U01_BINDINGS = {
    "samples/reference/phase-two/REPLACEMENT-EVENT-SOURCE-2026-001.json": (
        23_919,
        "2038ffb62bd065779a59593fd4e4f1756ba418da857091a1226850ca92717895",
    ),
    "samples/reference/phase-two/REPLACEMENT-EVENT-SOURCE-GATE-2026-001.json": (
        15_015,
        "77b30f5aec41473bc631684c48ba21b2d28d1c3f51d49d6e788393643af91559",
    ),
    "samples/reference/phase-two/REPLACEMENT-EVENT-SOURCE-GATE-REPORT-2026-001.json": (
        2_619,
        "40edad405ac13bfd080b71d19de04ce7fc576577816cdb2fc9495ce6c3832c4f",
    ),
    "samples/reference/phase-two/REPLACEMENT-EVENT-SOURCE-GATE-REPORT-2026-001.html": (
        3_998,
        "a645602eea5df31508353175abeeaff73fb8d39f0e432597a1d4374d75f1ec4",
    ),
    "records/phase-two/sources/SOURCE-2026-038.md": (
        5_103,
        "239192c10e16f69ed6218c8e8766ba2a79826618095c30b6ab5561cbaed740c3",
    ),
    "records/phase-two/terms/TERMS-2026-033.md": (
        4_058,
        "e8f55e33c67edad1462676812ec20663e96e239e45fa908ef13c33571fede268",
    ),
    "records/phase-two/prechecks/PRECHECK-2026-073.md": (
        5_322,
        "9bac466cdeeb9c11067ac3e4cd3ddf7a549bd16d07242715af6a7e40912496cb",
    ),
    "records/phase-two/registry/REGISTRY-2026-069.md": (
        3_665,
        "bd0606eeefcefddb5eeb373cbc3b0ce644975e9efdd961e364bc55704c53a59",
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
    role="ward-creek-2019-pre",
    package_id=PRE_PACKAGE_ID,
    provider_id="f6b6697d-5b7d-4049-8caf-8b0c7fdad4b7",
    safe_name="S2A_MSIL2A_20190801T185921_N0500_R013_T10TFQ_20230707T221135.SAFE",
    size_bytes=1_198_399_787,
    md5="7de4c0076a9ed4a3024ef46474b2aaac",
    blake3="737a71d70c36ae8d65d26df28e87730d08ed0bade1d2a327cce8a6b812a32c2a",
)
POST_CONTRACT = _contract(
    role="ward-creek-2019-post",
    package_id=POST_PACKAGE_ID,
    provider_id="51ddb0b7-8456-40a2-8301-e1651c951116",
    safe_name="S2A_MSIL2A_20190831T185921_N0500_R013_T10TFQ_20230528T200015.SAFE",
    size_bytes=1_198_420_414,
    md5="28f18e0328dd4cb8ab45446a1a238fb0",
    blake3="eaf090416dd240478d85389ba018f1d193e09c270ff40a6f346ee9c4f8110eaf",
)
WARD_CREEK_CONTRACTS = (PRE_CONTRACT, POST_CONTRACT)

EXPECTED_METADATA = {
    PRE_CONTRACT.role: {
        "acquisition_utc": "2019-08-01T18:59:21.024000Z",
        "publication_utc": "2024-04-13T14:52:27.028094Z",
    },
    POST_CONTRACT.role: {
        "acquisition_utc": "2019-08-31T18:59:21.024000Z",
        "publication_utc": "2023-11-30T19:34:35.294111Z",
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


def validate_ward_creek_contracts(
    contracts: Iterable[AssetContract] = WARD_CREEK_CONTRACTS,
) -> list[str]:
    items = list(contracts)
    reasons: list[str] = []
    if items != list(WARD_CREEK_CONTRACTS):
        reasons.append("WARD_CREEK_ORDERED_PAIR_CONTRACT_MISMATCH")
    if len(items) != 2:
        return [*reasons, "CONTRACT_REQUIRES_EXACT_PRE_POST_PAIR"]
    for expected, observed in zip(WARD_CREEK_CONTRACTS, items, strict=True):
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
        if identities != {("S2A", "0500", "013", "10TFQ")}:
            reasons.append("WARD_CREEK_PAIR_IDENTITY_MISMATCH")
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


def validate_ward_creek_metadata(snapshot: dict[str, Any]) -> list[str]:
    reasons = validate_ward_creek_contracts()
    if snapshot.get("source_record_id") != SOURCE_RECORD_ID:
        reasons.append("METADATA_SOURCE_RECORD_MISMATCH")
    if snapshot.get("terms_review_id") != TERMS_REVIEW_ID:
        reasons.append("METADATA_TERMS_RECORD_MISMATCH")
    if snapshot.get("live_refresh_performed") is not True:
        reasons.append("LIVE_METADATA_REFRESH_REQUIRED")
    records = snapshot.get("records")
    if not isinstance(records, list) or len(records) != 2:
        return [*reasons, "METADATA_RECORD_SET_MISMATCH"]
    for contract, record in zip(WARD_CREEK_CONTRACTS, records, strict=True):
        if not isinstance(record, dict):
            reasons.append(f"{contract.role}:RECORD_INVALID")
            continue
        expected = EXPECTED_METADATA[contract.role]
        comparisons = {
            "ROLE": contract.role,
            "EVENT_ID": EVENT_ID,
            "EVENT_GROUP": EVENT_GROUP_ID,
            "PROVIDER_ID": contract.provider_id,
            "NATIVE_ID": contract.native_id,
            "SIZE": contract.expected_size_bytes,
            "ACQUISITION": expected["acquisition_utc"],
            "PUBLICATION": expected["publication_utc"],
        }
        fields = {
            "ROLE": record.get("role"),
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


def refresh_ward_creek_metadata(
    *,
    observed_at_utc: str,
    urlopen_fn: Callable[..., Any] = urlopen,
) -> dict[str, Any]:
    records = []
    headers = {"Accept": "application/json", "User-Agent": USER_AGENT}
    for contract in WARD_CREEK_CONTRACTS:
        payload = _open_json(Request(_metadata_url(contract), headers=headers), urlopen_fn=urlopen_fn)
        records.append(_normalize_metadata(payload, role=contract.role))
    snapshot = {
        "observed_at_utc": observed_at_utc,
        "source_record_id": SOURCE_RECORD_ID,
        "terms_review_id": TERMS_REVIEW_ID,
        "live_refresh_performed": True,
        "records": records,
    }
    reasons = validate_ward_creek_metadata(snapshot)
    if reasons:
        raise AcquisitionError("WARD_CREEK_PUBLIC_METADATA_DRIFT", detail=",".join(reasons))
    return snapshot


@dataclass(frozen=True)
class WardCreekOpticalRun:
    repository_root: Path
    generated_at_utc: str

    @classmethod
    def create(cls, *, repository_root: Path, generated_at_utc: str) -> "WardCreekOpticalRun":
        if not generated_at_utc.endswith("Z"):
            raise ValueError("generated_at_utc must be explicit UTC")
        return cls(repository_root=repository_root.resolve(), generated_at_utc=generated_at_utc)

    def quarantine(self, role: str) -> Path:
        return self.repository_root / "downloads/phase-two/quarantine/P2O4-T39-U02" / f"{role}-r001"

    def destination(self, contract: AssetContract) -> Path:
        return self.repository_root / "downloads/phase-two/raw" / contract.package_id

    def state(self, role: str) -> Path:
        return self.repository_root / "downloads/phase-two/runs/P2O4-T39-U02" / f"BL-{PRODUCTION_RUN_DATE}-{role}-r001.json"

    @property
    def aggregate_state(self) -> Path:
        return self.repository_root / "downloads/phase-two/runs/P2O4-T39-U02" / f"BL-{PRODUCTION_RUN_DATE}-ward-creek-optical-intake-r001.json"

    @property
    def intake_contract(self) -> Path:
        return self.repository_root / "downloads/phase-two/contracts/P2O4-T39-U02/ward-creek-optical-intake-r001.json"

    @property
    def tracked_report(self) -> Path:
        return self.repository_root / "samples/reference/phase-two" / f"{REPORT_ID}.json"


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


def verify_ward_creek_repository_preflight(
    run: WardCreekOpticalRun,
    *,
    existing_success_outputs: bool = False,
) -> str:
    root = run.repository_root
    top = _git(root, "rev-parse", "--show-toplevel")
    if top.returncode != 0 or Path(top.stdout.strip()).resolve() != root:
        raise AcquisitionError("WARD_CREEK_REPOSITORY_ROOT_MISMATCH")
    branch = _git(root, "branch", "--show-current")
    if branch.returncode != 0 or branch.stdout.strip() != BRANCH:
        raise AcquisitionError("WARD_CREEK_BRANCH_MISMATCH")
    origin = _git(root, "config", "--get", "remote.origin.url")
    if origin.returncode != 0 or REPOSITORY not in origin.stdout.strip().lower().replace("\\", "/"):
        raise AcquisitionError("WARD_CREEK_ORIGIN_MISMATCH")
    head = _git(root, "rev-parse", "HEAD")
    commit = head.stdout.strip()
    if head.returncode != 0 or re.fullmatch(r"[0-9a-f]{40}", commit) is None:
        raise AcquisitionError("WARD_CREEK_COMMITTED_HEAD_REQUIRED")
    remote = _git(root, "rev-parse", f"origin/{BRANCH}")
    if remote.returncode != 0 or remote.stdout.strip() != commit:
        raise AcquisitionError("WARD_CREEK_REMOTE_HEAD_MISMATCH")
    allowed = f"?? {run.tracked_report.relative_to(root).as_posix()}" if existing_success_outputs else ""
    status = _git(root, "status", "--porcelain=v1", "--untracked-files=all")
    if status.returncode != 0 or status.stdout.strip().replace("\\", "/") != allowed:
        raise AcquisitionError("WARD_CREEK_WORKTREE_NOT_CLEAN")
    for ancestor, reason in (
        (GIT_BASE_COMMIT, "WARD_CREEK_BASE_NOT_ANCESTOR"),
        (U01_ENTRY_COMMIT, "WARD_CREEK_U01_NOT_ANCESTOR"),
    ):
        if _git(root, "merge-base", "--is-ancestor", ancestor, commit).returncode != 0:
            raise AcquisitionError(reason)
    for relative, (size, digest) in U01_BINDINGS.items():
        path = root / relative
        if not path.is_file() or path.stat().st_size != size or _sha256_file(path) != digest:
            raise AcquisitionError("WARD_CREEK_U01_BINDING_MISMATCH", detail=relative)
    private_paths = [
        run.intake_contract,
        run.aggregate_state,
        *(run.quarantine(item.role) for item in WARD_CREEK_CONTRACTS),
        *(run.destination(item) for item in WARD_CREEK_CONTRACTS),
        *(run.state(item.role) for item in WARD_CREEK_CONTRACTS),
    ]
    for path in private_paths:
        relative = path.relative_to(root).as_posix()
        if _git(root, "check-ignore", "--quiet", "--no-index", "--", relative).returncode != 0:
            raise AcquisitionError("WARD_CREEK_PRIVATE_PATH_NOT_IGNORED", detail=relative)
        if _git(root, "ls-files", "--error-unmatch", "--", relative).returncode != 1:
            raise AcquisitionError("WARD_CREEK_PRIVATE_PATH_TRACKED", detail=relative)
    report_relative = run.tracked_report.relative_to(root).as_posix()
    if _git(root, "check-ignore", "--quiet", "--no-index", "--", report_relative).returncode != 1:
        raise AcquisitionError("WARD_CREEK_TRACKED_REPORT_IGNORED")
    if existing_success_outputs:
        required = [
            run.intake_contract,
            run.aggregate_state,
            run.tracked_report,
            *(run.destination(item) for item in WARD_CREEK_CONTRACTS),
            *(run.state(item.role) for item in WARD_CREEK_CONTRACTS),
        ]
        if not all(_path_present(path) for path in required):
            raise AcquisitionError("WARD_CREEK_SUCCESS_OUTPUTS_MISSING")
    else:
        targets = [run.aggregate_state, run.tracked_report, *(run.destination(item) for item in WARD_CREEK_CONTRACTS), *(run.state(item.role) for item in WARD_CREEK_CONTRACTS)]
        present = [path.relative_to(root).as_posix() for path in targets if _path_present(path)]
        if present:
            raise AcquisitionError("WARD_CREEK_NO_OVERWRITE_TARGET_EXISTS", detail=",".join(present))
    return commit


def build_intake_contract(run: WardCreekOpticalRun) -> dict[str, Any]:
    assets = []
    for contract in WARD_CREEK_CONTRACTS:
        assets.append(
            {
                "asset_id": contract.role,
                "source": {
                    "kind": "https",
                    "uri": contract.stable_route,
                    "authorization_ref": "local-dpapi-cdse-account-reference-only",
                    "terms_ref": TERMS_REVIEW_ID,
                    "transport_exception_ref": None,
                },
                "destination_relative_path": f"{contract.package_id}/{contract.expected_filename}",
                "staging_relative_path": f"{contract.role}-r001/{contract.expected_filename}.part",
                "expected": {
                    "sha256": None,
                    "size_bytes": contract.expected_size_bytes,
                    "unavailable_reason": "CDSE publishes exact MD5 and BLAKE3 for this product, but no upstream SHA-256.",
                },
                "observed": {
                    "staged_sha256": None,
                    "staged_size_bytes": None,
                    "promoted_sha256": None,
                    "promoted_size_bytes": None,
                },
                "state": "authorized",
                "attempts": [],
                "failure": None,
                "superseded_by": None,
            }
        )
    return {
        "contract_version": "1.0",
        "intake_id": INTAKE_ID,
        "created_at": run.generated_at_utc,
        "collision_policy": "fail",
        "promotion_mode": "atomic-no-replace",
        "secret_policy": "references-only",
        "custody_root": "downloads/phase-two/raw",
        "staging_root": "downloads/phase-two/quarantine/P2O4-T39-U02",
        "assets": assets,
        "extensions": {
            "unit_id": UNIT_ID,
            "issue": TASK_ISSUE,
            "event_id": EVENT_ID,
            "source_record_id": SOURCE_RECORD_ID,
            "terms_review_id": TERMS_REVIEW_ID,
            "provider_checksums": {
                item.role: {"md5": item.provider_md5, "blake3": item.provider_blake3}
                for item in WARD_CREEK_CONTRACTS
            },
        },
    }


def write_intake_contract(run: WardCreekOpticalRun) -> dict[str, Any]:
    payload = build_intake_contract(run)
    run.intake_contract.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(payload, indent=2) + "\n").encode("utf-8")
    try:
        with run.intake_contract.open("xb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError:
        raise AcquisitionError("WARD_CREEK_INTAKE_CONTRACT_OVERWRITE_REFUSED") from None
    return payload


def _update_intake_contract_asset(
    *,
    run: WardCreekOpticalRun,
    contract: AssetContract,
    attempts: list[dict[str, Any]],
    state: str,
    local_sha256: str | None = None,
    failure: dict[str, Any] | None = None,
) -> None:
    payload = json.loads(run.intake_contract.read_text(encoding="utf-8"))
    if payload.get("intake_id") != INTAKE_ID:
        raise AcquisitionError("WARD_CREEK_INTAKE_CONTRACT_IDENTITY_MISMATCH")
    assets = payload.get("assets")
    if not isinstance(assets, list):
        raise AcquisitionError("WARD_CREEK_INTAKE_CONTRACT_ASSETS_INVALID")
    matches = [item for item in assets if item.get("asset_id") == contract.role]
    if len(matches) != 1:
        raise AcquisitionError("WARD_CREEK_INTAKE_CONTRACT_ROSTER_MISMATCH")
    asset = matches[0]
    normalized_attempts = []
    for index, attempt in enumerate(attempts, start=1):
        outcome = attempt["outcome"]
        normalized_attempts.append(
            {
                "attempt_id": f"{contract.role}-a{index:03d}",
                "started_at": run.generated_at_utc,
                "completed_at": run.generated_at_utc,
                "outcome": "succeeded" if outcome == "succeeded" else "failed",
            }
        )
    asset["attempts"] = normalized_attempts
    asset["state"] = state
    asset["failure"] = failure
    if state == "promoted":
        if local_sha256 is None:
            raise AcquisitionError("WARD_CREEK_INTAKE_CONTRACT_SHA256_REQUIRED")
        asset["observed"] = {
            "staged_sha256": local_sha256,
            "staged_size_bytes": contract.expected_size_bytes,
            "promoted_sha256": local_sha256,
            "promoted_size_bytes": contract.expected_size_bytes,
        }
    data = (json.dumps(payload, indent=2) + "\n").encode("utf-8")
    temporary = run.intake_contract.with_suffix(".json.next")
    try:
        with temporary.open("xb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, run.intake_contract)
    except FileExistsError:
        raise AcquisitionError("WARD_CREEK_INTAKE_CONTRACT_TEMP_COLLISION") from None
    finally:
        temporary.unlink(missing_ok=True)


def _profile_archive(path: Path, contract: AssetContract) -> dict[str, Any]:
    required = {
        "B04_10m": ("_B04_10m.jp2", 10, "uint16"),
        "B08_10m": ("_B08_10m.jp2", 10, "uint16"),
        "B11_20m": ("_B11_20m.jp2", 20, "uint16"),
        "B12_20m": ("_B12_20m.jp2", 20, "uint16"),
        "SCL_20m": ("_SCL_20m.jp2", 20, "uint8"),
    }
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
    profiles: dict[str, Any] = {}
    for key, (suffix, resolution, dtype) in required.items():
        matches = [name for name in names if name.endswith(suffix)]
        if len(matches) != 1:
            raise AcquisitionError("WARD_CREEK_REQUIRED_RASTER_ROSTER", role=contract.role, detail=key)
        member = matches[0]
        with rasterio.open(f"zip://{path.resolve()}!{member}") as source:
            observed_resolution = (abs(float(source.transform.a)), abs(float(source.transform.e)))
            if (
                source.crs is None
                or source.crs.to_epsg() != 32610
                or observed_resolution != (float(resolution), float(resolution))
                or source.count != 1
                or source.dtypes != (dtype,)
                or source.nodata is not None
            ):
                raise AcquisitionError("WARD_CREEK_RASTER_PROFILE_MISMATCH", role=contract.role, detail=key)
            profiles[key] = {
                "member": member,
                "crs": source.crs.to_string(),
                "epsg": source.crs.to_epsg(),
                "width": source.width,
                "height": source.height,
                "transform": list(source.transform)[:6],
                "resolution_m": list(observed_resolution),
                "count": source.count,
                "dtype": source.dtypes[0],
                "nodata": source.nodata,
            }
    if profiles["B04_10m"]["transform"][2:] != profiles["B08_10m"]["transform"][2:]:
        raise AcquisitionError("WARD_CREEK_10M_GRID_MISMATCH", role=contract.role)
    if profiles["B11_20m"]["transform"][2:] != profiles["B12_20m"]["transform"][2:]:
        raise AcquisitionError("WARD_CREEK_20M_GRID_MISMATCH", role=contract.role)
    if profiles["B11_20m"]["transform"][2:] != profiles["SCL_20m"]["transform"][2:]:
        raise AcquisitionError("WARD_CREEK_SCL_GRID_MISMATCH", role=contract.role)
    quality_members = [
        name
        for name in names
        if "/QI_DATA/" in name and (
            "MSK_" in Path(name).name or Path(name).name.endswith(".xml")
        )
    ]
    if not quality_members:
        raise AcquisitionError("WARD_CREEK_QUALITY_MASKS_MISSING", role=contract.role)
    return {
        "safe_root": contract.expected_zip_root,
        "member_count": len(names),
        "quality_mask_member_count": len(quality_members),
        "quality_mask_examples": quality_members[:12],
        "rasters": profiles,
    }


def _write_private_failure(
    *,
    run: WardCreekOpticalRun,
    contract: AssetContract,
    commit: str,
    attempts: list[dict[str, Any]],
    error: BaseException,
) -> None:
    state_path = run.state(contract.role)
    if _path_present(state_path):
        return
    payload = {
        "state_schema_version": "0.1.0",
        "unit_id": UNIT_ID,
        "run_id": f"BL-{PRODUCTION_RUN_DATE}-{contract.role}-r001",
        "generated_at_utc": run.generated_at_utc,
        "event_id": EVENT_ID,
        "git_source_commit": commit,
        "attempts": attempts,
        "failure": {
            "reason_code": error.reason_code if isinstance(error, AcquisitionError) else "LOCAL_TRANSACTION_FAILURE",
            "detail": error.detail if isinstance(error, AcquisitionError) else type(error).__name__,
        },
        "decision": "FAILED_WARD_CREEK_OPTICAL_SINGLETON_RETAIN_EVIDENCE",
        "warning": WARNING,
    }
    write_private_state(state_path, payload, repo_root=run.repository_root)


def _acquire_singleton(
    *,
    run: WardCreekOpticalRun,
    commit: str,
    credentials: CdseCredentials,
    contract: AssetContract,
    metadata_record: dict[str, Any],
    progress: Callable[[str, int, int], None] | None,
) -> dict[str, Any]:
    quarantine = run.quarantine(contract.role)
    destination = run.destination(contract)
    state_path = run.state(contract.role)
    run_id = f"BL-{PRODUCTION_RUN_DATE}-{contract.role}-r001"
    attempts: list[dict[str, Any]] = []
    try:
        for attempt in range(1, MAX_TRANSFER_ATTEMPTS + 1):
            try:
                download = stream_cdse_asset_with_retries(
                    contract,
                    quarantine,
                    username=credentials.username,
                    password=credentials.password,
                    max_attempts=1,
                    timeout_seconds=TRANSFER_TIMEOUT_SECONDS,
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
            break
        else:
            raise AcquisitionError("WARD_CREEK_TRANSFER_ATTEMPTS_EXHAUSTED", role=contract.role)
        registration = promote_quarantine_no_overwrite(
            quarantine,
            destination,
            (contract,),
            generated_at_utc=run.generated_at_utc,
            run_id=run_id,
            synthetic_fixture=False,
            contract_validator=_singleton_validator(contract),
            contract_version=CONTRACT_VERSION,
        )
        verification = verify_registered_package(
            destination,
            (contract,),
            contract_validator=_singleton_validator(contract),
            contract_version=CONTRACT_VERSION,
        )
        if not verification["accepted_as_unchanged_registered_package"]:
            raise AcquisitionError("WARD_CREEK_POST_PROMOTION_VERIFICATION_FAILED", role=contract.role)
        archive_profile = _profile_archive(destination / contract.expected_filename, contract)
    except (AcquisitionError, OSError, ValueError, zipfile.BadZipFile) as error:
        _update_intake_contract_asset(
            run=run,
            contract=contract,
            attempts=attempts,
            state="failed",
            failure={
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
        )
        _write_private_failure(
            run=run,
            contract=contract,
            commit=commit,
            attempts=attempts,
            error=error,
        )
        raise
    local_sha256 = verification["observations"][0]["local_hashes"]["sha256"]
    _update_intake_contract_asset(
        run=run,
        contract=contract,
        attempts=attempts,
        state="promoted",
        local_sha256=local_sha256,
    )
    state = {
        "state_schema_version": "0.1.0",
        "unit_id": UNIT_ID,
        "run_id": run_id,
        "generated_at_utc": run.generated_at_utc,
        "event_id": EVENT_ID,
        "event_group_id": EVENT_GROUP_ID,
        "git_source_commit": commit,
        "pair_id": PAIR_ID,
        "contract_version": CONTRACT_VERSION,
        "metadata_record": metadata_record,
        "attempts": attempts,
        "download": download,
        "registration": registration,
        "verification": verification,
        "archive_profile": archive_profile,
        "credentials_exercised": True,
        "decision": "REGISTERED_EXACT_WARD_CREEK_OPTICAL_SINGLETON",
        "warning": WARNING,
    }
    write_private_state(state_path, state, repo_root=run.repository_root)
    return state


def _public_package(state: dict[str, Any]) -> dict[str, Any]:
    observation = state["verification"]["observations"][0]
    return {
        "role": observation["role"],
        "provider_id": observation["provider_id"],
        "native_id": observation["native_id"],
        "bytes": observation["observed_bytes"],
        "local_hashes": observation["local_hashes"],
        "registration_manifest_sha256": state["verification"]["registration_manifest_sha256"],
        "archive_container": observation["container_details"],
        "archive_profile": state["archive_profile"],
        "decision": state["decision"],
    }


def _write_tracked_report(run: WardCreekOpticalRun, payload: dict[str, Any]) -> None:
    run.tracked_report.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(payload, indent=2) + "\n").encode("utf-8")
    try:
        with run.tracked_report.open("xb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError:
        raise AcquisitionError("WARD_CREEK_TRACKED_REPORT_OVERWRITE_REFUSED") from None


def acquire_ward_creek_optical_pair(
    *,
    run: WardCreekOpticalRun,
    commit: str,
    credentials: CdseCredentials,
    metadata_snapshot: dict[str, Any],
    progress: Callable[[str, int, int], None] | None = None,
) -> dict[str, Any]:
    reasons = validate_ward_creek_metadata(metadata_snapshot)
    if reasons:
        raise AcquisitionError("WARD_CREEK_METADATA_REJECTED", detail=",".join(reasons))
    pre = _acquire_singleton(
        run=run,
        commit=commit,
        credentials=credentials,
        contract=PRE_CONTRACT,
        metadata_record=metadata_snapshot["records"][0],
        progress=progress,
    )
    pre_verify = verify_registered_package(
        run.destination(PRE_CONTRACT),
        (PRE_CONTRACT,),
        contract_validator=_singleton_validator(PRE_CONTRACT),
        contract_version=CONTRACT_VERSION,
    )
    if not pre_verify["accepted_as_unchanged_registered_package"]:
        raise AcquisitionError("WARD_CREEK_PRE_DEPENDENCY_FAILED")
    post = _acquire_singleton(
        run=run,
        commit=commit,
        credentials=credentials,
        contract=POST_CONTRACT,
        metadata_record=metadata_snapshot["records"][1],
        progress=progress,
    )
    temporal = {
        "pre_acquisition_utc": EXPECTED_METADATA[PRE_CONTRACT.role]["acquisition_utc"],
        "ignition_utc": "2019-08-12T00:00:00Z",
        "post_acquisition_utc": EXPECTED_METADATA[POST_CONTRACT.role]["acquisition_utc"],
        "ordered_pre_before_ignition_before_post": True,
    }
    aggregate = {
        "state_schema_version": "0.1.0",
        "unit_id": UNIT_ID,
        "run_id": f"BL-{PRODUCTION_RUN_DATE}-ward-creek-optical-intake-r001",
        "generated_at_utc": run.generated_at_utc,
        "event_id": EVENT_ID,
        "event_group_id": EVENT_GROUP_ID,
        "git_source_commit": commit,
        "transaction_order": [PRE_CONTRACT.role, POST_CONTRACT.role],
        "metadata_snapshot": metadata_snapshot,
        "temporal_relation": temporal,
        "decision": "REGISTERED_EXACT_WARD_CREEK_OPTICAL_PAIR",
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
        "intake_id": INTAKE_ID,
        "trace": {
            "repository": REPOSITORY,
            "branch": BRANCH,
            "task_issue": TASK_ISSUE,
            "git_base_commit": GIT_BASE_COMMIT,
            "u01_entry_commit": U01_ENTRY_COMMIT,
            "git_source_commit": commit,
            "u01_bindings": {
                path: {"bytes": size, "sha256": digest}
                for path, (size, digest) in U01_BINDINGS.items()
            },
        },
        "transaction_order": aggregate["transaction_order"],
        "temporal_relation": temporal,
        "packages": [_public_package(pre), _public_package(post)],
        "expected_combined_bytes": sum(item.expected_size_bytes for item in WARD_CREEK_CONTRACTS),
        "gate_results": {
            "exact_current_odata_identity": "pass",
            "sequential_singleton_custody": "pass",
            "provider_md5_blake3": "pass",
            "local_sha256_md5_blake3": "pass",
            "safe_zip_root_manifest_crc": "pass",
            "post_promotion_rehash": "pass",
            "exact_crs_grid_nodata_band_and_scl_profiles": "pass",
            "quality_mask_roster": "pass",
            "temporal_relation": "pass",
            "u03_mtbs_reference": "not executed",
            "candidate_label_dataset_split_baseline_model": "not created",
        },
        "decision": "PASS_WARD_CREEK_OPTICAL_CUSTODY_AUTHORIZE_U03_REFERENCE_INTAKE",
        "warning": WARNING,
    }
    _write_tracked_report(run, report)
    return report


def verify_ward_creek_completed(run: WardCreekOpticalRun) -> list[str]:
    reasons: list[str] = []
    for contract in WARD_CREEK_CONTRACTS:
        verification = verify_registered_package(
            run.destination(contract),
            (contract,),
            contract_validator=_singleton_validator(contract),
            contract_version=CONTRACT_VERSION,
        )
        if not verification["accepted_as_unchanged_registered_package"]:
            reasons.append(f"{contract.role}:REGISTERED_PACKAGE")
        state_path = run.state(contract.role)
        if not state_path.is_file():
            reasons.append(f"{contract.role}:STATE_MISSING")
            continue
        state = json.loads(state_path.read_text(encoding="utf-8"))
        if state.get("decision") != "REGISTERED_EXACT_WARD_CREEK_OPTICAL_SINGLETON":
            reasons.append(f"{contract.role}:STATE_DECISION")
        try:
            _profile_archive(run.destination(contract) / contract.expected_filename, contract)
        except (AcquisitionError, OSError, ValueError, zipfile.BadZipFile):
            reasons.append(f"{contract.role}:ARCHIVE_PROFILE")
    if not run.aggregate_state.is_file():
        reasons.append("AGGREGATE_STATE_MISSING")
    if not run.tracked_report.is_file():
        reasons.append("TRACKED_REPORT_MISSING")
    else:
        report = json.loads(run.tracked_report.read_text(encoding="utf-8"))
        if report.get("decision") != "PASS_WARD_CREEK_OPTICAL_CUSTODY_AUTHORIZE_U03_REFERENCE_INTAKE":
            reasons.append("TRACKED_REPORT_DECISION")
        if report.get("expected_combined_bytes") != 2_396_820_201:
            reasons.append("TRACKED_REPORT_BYTES")
    return reasons
