"""Capture a metadata-only replacement-post selection for Petes Lake U03."""

from __future__ import annotations

import argparse
from datetime import date, datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

from .cross_event_source import _expanded_bbox, _geometry_bbox, _request_json, _stac_window
from .optical_pair_evidence import WARNING, _sha256_lf_text
from .petes_lake_optical_contract import normalize_cloud_cover_for_comparison
from .petes_lake_source_fitness import _load_candidate, _write_bytes_no_overwrite


REPORT_ID = "PETES-LAKE-SOURCE-REMEDIATION-2026-001"
REPORT_VERSION = "petes-lake-source-remediation-v0.1.0"
UNIT_ID = "P2O4-T33-U03"
TASK_ISSUE = 521
BRANCH = "codex/p2o4-t33-petes-lake-milestone"
SOURCE_RECORD_ID = "SOURCE-2026-030"
TERMS_REVIEW_ID = "TERMS-2026-024"
EVENT_GROUP_ID = "event-petes-lake-2023"
EVENT_ID = "OR4396912190120230825"
IGNITION_DATE = date(2023, 8, 25)
EARLIEST_POST_STATUS_DATE = date(2023, 9, 23)
MAX_CATALOGUE_CLOUD_PERCENT = 20.0
PLAN_PATH = Path("samples/cross-event/phase-two/ADDITIONAL-EVENT-GROUP-PLAN-2026-001.json")
FAILED_U03_PATH = Path(
    "samples/cross-event/phase-two/petes-lake/PETES-LAKE-SOURCE-FITNESS-2026-001.json"
)
FAILED_U03_SHA256 = "ac9befd021d71ff779ec56ddefc894f4e39b92e64e65c2c4afb815663d1ad443"
OUTPUT_PATH = Path(
    "samples/cross-event/phase-two/petes-lake/PETES-LAKE-SOURCE-REMEDIATION-2026-001.json"
)
RUN_ID = "BL-2026-07-21-petes-lake-replacement-post-selection-r001"
SELECTED_NATIVE_ID = "S2A_MSIL2A_20231019T190411_N0510_R013_T10TEP_20241107T024526"
EXPECTED_IDS = (
    "S2A_MSIL2A_20230830T185921_N0510_R013_T10TEP_20241023T063829",
    "S2A_MSIL2A_20230909T185941_N0510_R013_T10TEP_20241104T170811",
    "S2A_MSIL2A_20230919T190051_N0510_R013_T10TEP_20241105T130020",
    "S2A_MSIL2A_20230929T190201_N0510_R013_T10TEP_20241031T230941",
    "S2A_MSIL2A_20231009T190301_N0510_R013_T10TEP_20241020T100944",
    SELECTED_NATIVE_ID,
)
INCIDENT_SOURCES = (
    {
        "title": "Petes Lake Fire Update, September 18",
        "publisher": "Central Oregon Fire Information",
        "url": "https://centraloregonfire.org/2023/09/18/13036/",
        "supported_fact": (
            "The official regional update says the fire grew to 3,009 acres on "
            "September 17 and could continue growing on September 18."
        ),
    },
    {
        "title": "Lookout, Bedrock, Petes Lake, Horse Creek, and Pothole Fires",
        "publisher": "Central Oregon Fire Information",
        "url": (
            "https://centraloregonfire.org/2023/09/22/"
            "lookout-bedrock-petes-lake-horse-creek-and-pothole-fires-2/"
        ),
        "supported_fact": (
            "The September 22 update reports Petes Lake at 50 percent completed "
            "with low fire activity and continued monitoring."
        ),
    },
)


class PetesLakeReplacementError(RuntimeError):
    """A fail-closed metadata-only replacement-selection error."""


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, text=True, check=False
    )


def _preflight(root: Path) -> str:
    top = _git(root, "rev-parse", "--show-toplevel")
    if top.returncode != 0 or Path(top.stdout.strip()).resolve() != root:
        raise PetesLakeReplacementError("repository root mismatch")
    branch = _git(root, "branch", "--show-current")
    if branch.returncode != 0 or branch.stdout.strip() != BRANCH:
        raise PetesLakeReplacementError("branch mismatch")
    status = _git(root, "status", "--porcelain=v1", "--untracked-files=all")
    if status.returncode != 0 or status.stdout.strip():
        raise PetesLakeReplacementError("worktree is not clean")
    head = _git(root, "rev-parse", "HEAD")
    commit = head.stdout.strip()
    if head.returncode != 0 or not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise PetesLakeReplacementError("committed source HEAD required")
    remote = _git(
        root,
        "-c",
        "credential.interactive=never",
        "ls-remote",
        "--heads",
        "origin",
        BRANCH,
    )
    if remote.returncode != 0 or remote.stdout.split("\t", 1)[0].strip() != commit:
        raise PetesLakeReplacementError("remote branch is not equal to source HEAD")
    return commit


def _timestamp(value: str) -> str:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise argparse.ArgumentTypeError("access timestamp must be ISO-8601") from None
    if not value.endswith("Z") or parsed.tzinfo is None:
        raise argparse.ArgumentTypeError("access timestamp must be UTC")
    return value


def rank_candidates(items: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Apply only predeclared identity, timing, and catalogue-cloud gates."""

    ids = tuple(item.get("id") for item in items)
    if ids != EXPECTED_IDS:
        raise PetesLakeReplacementError("current STAC candidate roster drifted")
    ranked: list[dict[str, Any]] = []
    for item in items:
        if (
            item.get("platform") != "sentinel-2a"
            or item.get("grid_code") != "MGRS-10TEP"
            or item.get("relative_orbit") != 13
            or item.get("processing_version") != "05.10"
        ):
            raise PetesLakeReplacementError("same-regime identity gate failed")
        try:
            sensing = datetime.fromisoformat(item["datetime"].replace("Z", "+00:00")).date()
            cloud = float(item["cloud_cover_percent"])
            snow = float(item["snow_cover_percent"])
            size = int(item["product_bytes"])
        except (KeyError, TypeError, ValueError) as error:
            raise PetesLakeReplacementError("STAC candidate metadata is invalid") from error
        if size <= 0 or not 0 <= cloud <= 100 or not 0 <= snow <= 100:
            raise PetesLakeReplacementError("STAC candidate range gate failed")
        reasons: list[str] = []
        if sensing < EARLIEST_POST_STATUS_DATE:
            reasons.append("INCIDENT_TIMING_PRECEDES_CONSERVATIVE_POST_STATUS_BOUNDARY")
        if cloud > MAX_CATALOGUE_CLOUD_PERCENT:
            reasons.append("CATALOGUE_CLOUD_EXCEEDS_20_PERCENT")
        disposition = "eligible-for-ranking" if not reasons else "reject-before-acquisition"
        ranked.append(
            {
                "id": item["id"],
                "datetime": item["datetime"],
                "days_after_ignition": (sensing - IGNITION_DATE).days,
                "platform": item["platform"],
                "grid_code": item["grid_code"],
                "relative_orbit": item["relative_orbit"],
                "processing_version": item["processing_version"],
                "catalogue_cloud_percent": cloud,
                "catalogue_snow_percent": snow,
                "product_bytes": size,
                "stac_checksum": item.get("provider_checksum"),
                "product_filename": item.get("product_filename"),
                "disposition": disposition,
                "reason_codes": reasons,
            }
        )
    eligible = [item for item in ranked if item["disposition"] == "eligible-for-ranking"]
    if len(eligible) != 1 or eligible[0]["id"] != SELECTED_NATIVE_ID:
        raise PetesLakeReplacementError("replacement-post selection is ambiguous")
    eligible[0]["disposition"] = "selected-for-contract-revision-only"
    eligible[0]["reason_codes"] = [
        "ONLY_SAME_REGIME_CANDIDATE_AFTER_STATUS_BOUNDARY_BELOW_CLOUD_GATE"
    ]
    return ranked, eligible[0]


def _selected_odata(selected: dict[str, Any]) -> dict[str, Any]:
    payload, _ = _request_json(
        "https://catalogue.dataspace.copernicus.eu/odata/v1/Products",
        {
            "$filter": f"startswith(Name,'{selected['id']}')",
            "$select": (
                "Id,Name,ContentLength,Online,Checksum,ContentDate,"
                "PublicationDate,S3Path,Attributes"
            ),
            "$expand": "Attributes",
        },
    )
    values = payload.get("value")
    if not isinstance(values, list) or len(values) != 1 or not isinstance(values[0], dict):
        raise PetesLakeReplacementError("selected OData record count mismatch")
    item = values[0]
    attributes = {
        str(entry.get("Name")): entry.get("Value")
        for entry in item.get("Attributes") or []
        if isinstance(entry, dict) and entry.get("Name") is not None
    }
    checksums = {
        str(entry.get("Algorithm", "")).upper(): str(entry.get("Value", "")).lower()
        for entry in item.get("Checksum") or []
        if isinstance(entry, dict)
    }
    native_id = selected["id"]
    comparisons = {
        "name": (item.get("Name"), f"{native_id}.SAFE"),
        "size": (item.get("ContentLength"), selected["product_bytes"]),
        "online": (item.get("Online"), True),
        "platform": (attributes.get("platformSerialIdentifier"), "A"),
        "tile": (attributes.get("tileId"), "10TEP"),
        "orbit": (attributes.get("relativeOrbitNumber"), 13),
        "baseline": (attributes.get("processorVersion"), "05.10"),
        "product_type": (attributes.get("productType"), "S2MSI2A"),
        "cloud_2dp": (
            normalize_cloud_cover_for_comparison(attributes.get("cloudCover")),
            normalize_cloud_cover_for_comparison(selected["catalogue_cloud_percent"]),
        ),
    }
    failures = [name for name, (observed, expected) in comparisons.items() if observed != expected]
    if failures:
        raise PetesLakeReplacementError("selected OData identity mismatch: " + ",".join(failures))
    provider_id = str(item.get("Id", ""))
    if not re.fullmatch(r"[0-9a-f-]{36}", provider_id):
        raise PetesLakeReplacementError("selected provider UUID is invalid")
    md5 = checksums.get("MD5", "")
    blake3 = checksums.get("BLAKE3", "")
    if not re.fullmatch(r"[0-9a-f]{32}", md5) or not re.fullmatch(r"[0-9a-f]{64}", blake3):
        raise PetesLakeReplacementError("selected provider checksum is invalid")
    if selected.get("stac_checksum") != f"d50110{md5}":
        raise PetesLakeReplacementError("selected STAC/OData checksum mismatch")
    s3_path = str(item.get("S3Path", ""))
    if not s3_path.endswith(f"/{native_id}.SAFE"):
        raise PetesLakeReplacementError("selected S3 identity mismatch")
    return {
        "provider_id": provider_id,
        "native_id": native_id,
        "expected_filename": f"{native_id}.SAFE.zip",
        "package_id": "petes-lake-s2-optical-post-remediation-v0.2.0",
        "role": "optical-post-remediation",
        "size_bytes": item["ContentLength"],
        "online": item["Online"],
        "acquisition_utc": (item.get("ContentDate") or {}).get("Start"),
        "publication_utc": item.get("PublicationDate"),
        "provider_md5": md5,
        "provider_blake3": blake3,
        "platform_serial_identifier": attributes["platformSerialIdentifier"],
        "tile_id": attributes["tileId"],
        "relative_orbit_number": attributes["relativeOrbitNumber"],
        "processor_version": attributes["processorVersion"],
        "product_type": attributes["productType"],
        "odata_cloud_cover_percent": attributes["cloudCover"],
        "stac_cloud_cover_percent": selected["catalogue_cloud_percent"],
        "stac_snow_cover_percent": selected["catalogue_snow_percent"],
        "s3_identity_verified_without_retaining_path": True,
    }


def build_report(*, repository_root: Path, accessed_at_utc: str, git_source_commit: str) -> dict[str, Any]:
    failed_path = repository_root / FAILED_U03_PATH
    if sha256(failed_path.read_bytes()).hexdigest() != FAILED_U03_SHA256:
        raise PetesLakeReplacementError("failed U03 prerequisite hash mismatch")
    _, candidate = _load_candidate(repository_root / PLAN_PATH)
    if candidate.get("event_group_id") != EVENT_GROUP_ID or candidate.get("fire_id") != EVENT_ID:
        raise PetesLakeReplacementError("Petes Lake event binding mismatch")
    boundary = candidate.get("boundary_geometry")
    if not isinstance(boundary, dict):
        raise PetesLakeReplacementError("Petes Lake boundary is missing")
    window = _stac_window(
        bbox=_expanded_bbox(_geometry_bbox(boundary)),
        start=datetime(2023, 8, 26, tzinfo=timezone.utc),
        end=datetime(2023, 10, 28, tzinfo=timezone.utc),
        window="post_remediation_scout",
        boundary=boundary,
    )
    matching = [
        item
        for item in window["items"]
        if item.get("platform") == "sentinel-2a"
        and item.get("grid_code") == "MGRS-10TEP"
        and item.get("relative_orbit") == 13
        and item.get("processing_version") == "05.10"
    ]
    ranked, selected = rank_candidates(matching)
    contract = _selected_odata(selected)
    return {
        "report_id": REPORT_ID,
        "report_version": REPORT_VERSION,
        "generated_at_utc": accessed_at_utc,
        "run_id": RUN_ID,
        "unit_id": UNIT_ID,
        "task_issue": TASK_ISSUE,
        "repository": "drwbkr1/burnlens-deschutes",
        "git_source_commit": git_source_commit,
        "event_group_id": EVENT_GROUP_ID,
        "event_id": EVENT_ID,
        "source_record_id": SOURCE_RECORD_ID,
        "terms_review_id": TERMS_REVIEW_ID,
        "input_hashes": {
            "failed_u03_report_sha256": FAILED_U03_SHA256,
            "additional_event_plan_sha256": _sha256_lf_text(repository_root / PLAN_PATH),
        },
        "search_contract": {
            "collection": "sentinel-2-l2a",
            "date_range_utc": ["2023-08-26T00:00:00Z", "2023-10-28T23:59:59Z"],
            "full_boundary_coverage_required": True,
            "platform": "sentinel-2a",
            "grid_code": "MGRS-10TEP",
            "relative_orbit": 13,
            "processing_version": "05.10",
            "earliest_post_status_date": EARLIEST_POST_STATUS_DATE.isoformat(),
            "catalogue_cloud_max_percent": MAX_CATALOGUE_CLOUD_PERCENT,
            "catalogue_snow_threshold": None,
            "local_quality_requirement": (
                "Delivered native SCL/CLD/SNW and actual render must independently pass; "
                "catalogue metadata never establishes local fitness."
            ),
        },
        "source_observation": {
            "stac_collection": "https://stac.dataspace.copernicus.eu/v1/collections/sentinel-2-l2a",
            "stac_page_count": window["page_count"],
            "stac_returned_item_count": window["returned_item_count"],
            "full_boundary_coverage_item_count": window["full_boundary_coverage_item_count"],
            "same_regime_candidate_count": len(matching),
            "odata_collection": "https://catalogue.dataspace.copernicus.eu/odata/v1/Products",
            "credentials_used": False,
            "provider_product_or_archive_bytes": 0,
        },
        "incident_timing_evidence": {
            "sources": list(INCIDENT_SOURCES),
            "decision_boundary": (
                "Reject scenes before 2023-09-23 because official September 18 and 22 "
                "updates show material activity and incomplete incident work. This is a "
                "conservative scene-selection boundary, not a containment or fire-end claim."
            ),
        },
        "candidates": ranked,
        "selected_contract": contract,
        "decision": "SELECT_REPLACEMENT_POST_AUTHORIZE_CONTRACT_REVISION_ONLY",
        "disposition": "pass-for-contract-revision-only",
        "next_dependency": "P2O4-T33-U03_REPLACEMENT_CONTRACT_AND_PREFLIGHT",
        "limitations": [
            "The selected product is not acquired or locally inspected in this run.",
            "Tile-wide cloud and snow metadata do not prove boundary-local quality.",
            "The October 19 product still carries nonzero catalogue snow and may fail native SCL/SNW or render gates.",
            "Incident evidence supports excluding earlier scenes but does not establish an official fire-end date for October 19.",
            "Selection authorizes no provider transaction until the exact contract is committed, pushed, and recorded on issue #521.",
        ],
        "claims": {
            "proven": [
                "Six same-platform, same-tile, same-orbit, PB05.10 post candidates cover the full frozen boundary in current STAC metadata.",
                "Only the October 19 product is after the conservative incident-status boundary and below the established 20 percent catalogue-cloud gate.",
                "Current OData identifies the selected product as online with exact UUID, size, MD5, BLAKE3, acquisition time, tile, orbit, baseline, and product type.",
            ],
            "not_proven": [
                "No replacement provider archive, local pixel, source-fitness pass, reference, candidate, owner response, label, dataset, split, baseline, or model exists.",
                "No official containment, fire-end, field-validation, endorsement, emergency-ready, or operational status is claimed.",
            ],
        },
        "attribution": "Contains modified Copernicus Sentinel data 2023, accessed through CDSE.",
        "warning": WARNING,
    }


def write_report(report: dict[str, Any], path: Path) -> dict[str, Any]:
    payload = (json.dumps(report, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    _write_bytes_no_overwrite(path, payload)
    return {"path": path.as_posix(), "bytes": len(payload), "sha256": sha256(payload).hexdigest()}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--accessed-at-utc", type=_timestamp, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        root = args.repository_root.resolve()
        commit = _preflight(root)
        report = build_report(
            repository_root=root,
            accessed_at_utc=args.accessed_at_utc,
            git_source_commit=commit,
        )
        output = write_report(report, root / OUTPUT_PATH)
        print(json.dumps({"report_id": REPORT_ID, "run_id": RUN_ID, "decision": report["decision"], "output": output}, sort_keys=True))
        return 0
    except (OSError, ValueError, PetesLakeReplacementError) as error:
        print(f"PETES_LAKE_U03_REPLACEMENT_FAILURE; reason={error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
