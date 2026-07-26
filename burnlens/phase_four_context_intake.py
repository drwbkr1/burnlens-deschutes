"""Acquire the exact bounded USGS context package under no-overwrite custody."""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import subprocess
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener


INTAKE_VERSION = "burnlens-phase-four-context-intake-v0.1.0"
PLAN_PATH = Path(
    "records/phase-four/intake/P4O1-T01-U04-context-intake.json"
)
PLAN_SHA256 = (
    "c7bd8ffee3f0088bdbc86df70ef9a0bddbb417b4e0eb0c15693fe15b65918001"
)
FINAL_CONTRACT_SHA256 = (
    "3cc26f5be2fcb811dfe46a95dbdd9daf828457b7b10d6918a307b30450abfdcd"
)
SOURCE_GATE_PATH = Path(
    "records/phase-four/sources/"
    "PHASE-FOUR-CONTEXT-SOURCE-GATE-2026-001.json"
)
SOURCE_GATE_SHA256 = (
    "12c273f24565d4899517d64408654128c62a0b8ba9e8f58d3dd898dacaef7a28"
)
RUN_ROOT = Path("runs/phase-four")
RUN_ID_PATTERN = re.compile(
    r"^BL-[0-9]{4}-[0-9]{2}-[0-9]{2}-p4o1-t01-u04-context-r[0-9]{3}$"
)
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")
MAX_RESPONSE_BYTES = 10 * 1024 * 1024

ASSET_RULES: dict[str, dict[str, Any]] = {
    "ntd-secondary-highways": {
        "count": 28,
        "geometry_types": {"LineString", "MultiLineString"},
        "fields": {
            "objectid",
            "permanent_identifier",
            "source_datasetid",
            "source_datadesc",
            "source_originator",
            "loaddate",
            "tnmfrc",
            "mtfcc_code",
            "name",
            "globalid",
        },
    },
    "ntd-local-connecting-roads": {
        "count": 30,
        "geometry_types": {"LineString", "MultiLineString"},
        "fields": {
            "objectid",
            "permanent_identifier",
            "source_datasetid",
            "source_datadesc",
            "source_originator",
            "loaddate",
            "tnmfrc",
            "mtfcc_code",
            "name",
            "globalid",
        },
    },
    "ntd-local-roads": {
        "count": 111,
        "geometry_types": {"LineString", "MultiLineString"},
        "fields": {
            "objectid",
            "permanent_identifier",
            "source_datasetid",
            "source_datadesc",
            "source_originator",
            "loaddate",
            "tnmfrc",
            "mtfcc_code",
            "name",
            "globalid",
        },
    },
    "nsd-cemeteries": {
        "count": 3,
        "geometry_types": {"Point", "MultiPoint"},
        "fields": {
            "objectid",
            "permanent_identifier",
            "source_datasetid",
            "source_datadesc",
            "source_originator",
            "loaddate",
            "ftype",
            "fcode",
            "name",
            "pointlocationtype",
            "admintype",
            "gnis_id",
            "globalid",
        },
    },
    "nsd-post-offices": {
        "count": 2,
        "geometry_types": {"Point", "MultiPoint"},
        "fields": {
            "objectid",
            "permanent_identifier",
            "source_datasetid",
            "source_datadesc",
            "source_originator",
            "loaddate",
            "ftype",
            "fcode",
            "name",
            "pointlocationtype",
            "admintype",
            "gnis_id",
            "globalid",
        },
    },
    "nsd-fire-ems": {
        "count": 1,
        "geometry_types": {"Point", "MultiPoint"},
        "fields": {
            "objectid",
            "permanent_identifier",
            "source_datasetid",
            "source_datadesc",
            "source_originator",
            "loaddate",
            "ftype",
            "fcode",
            "name",
            "pointlocationtype",
            "admintype",
            "gnis_id",
            "globalid",
        },
    },
    "nsd-trailheads": {
        "count": 2,
        "geometry_types": {"Point", "MultiPoint"},
        "fields": {
            "objectid",
            "permanent_identifier",
            "source_datasetid",
            "source_datadesc",
            "source_originator",
            "loaddate",
            "ftype",
            "fcode",
            "name",
            "pointlocationtype",
            "admintype",
            "gnis_id",
            "globalid",
        },
    },
    "nbd-blm-boundary": {
        "count": 1,
        "geometry_types": {"Polygon", "MultiPolygon"},
        "fields": {
            "objectid",
            "permanent_identifier",
            "source_datasetid",
            "source_datadesc",
            "source_originator",
            "loaddate",
            "name",
            "ftype",
            "fcode",
            "admintype",
            "ownerormanagingagency",
            "globalid",
        },
    },
}


class PhaseFourContextIntakeError(RuntimeError):
    """The exact bounded context intake failed closed."""


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(
        self,
        req: Any,
        fp: Any,
        code: int,
        msg: str,
        headers: Any,
        newurl: str,
    ) -> None:
        return None


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(
        "utf-8"
    )


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(8 * 1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PhaseFourContextIntakeError(f"invalid JSON: {path}") from exc
    if not isinstance(value, dict):
        raise PhaseFourContextIntakeError(f"JSON object required: {path}")
    return value


def _write_new(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    created = False
    try:
        with path.open("xb") as stream:
            created = True
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        if path.read_bytes() != payload:
            raise PhaseFourContextIntakeError(
                f"exact output readback failed: {path}"
            )
    except Exception:
        if created and path.exists():
            path.unlink()
        raise


def _require_clean_head(root: Path, git_source_commit: str) -> None:
    if not COMMIT_PATTERN.fullmatch(git_source_commit):
        raise PhaseFourContextIntakeError("git source commit is invalid")
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if head != git_source_commit:
        raise PhaseFourContextIntakeError("git source commit differs from HEAD")
    status = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    if status:
        raise PhaseFourContextIntakeError(
            "working tree must be clean before context intake"
        )


def _load_exact_plan(root: Path) -> dict[str, Any]:
    plan_path = root / PLAN_PATH
    gate_path = root / SOURCE_GATE_PATH
    if _sha256_file(plan_path) != PLAN_SHA256:
        raise PhaseFourContextIntakeError("tracked intake plan hash drift")
    if _sha256_file(gate_path) != SOURCE_GATE_SHA256:
        raise PhaseFourContextIntakeError("source gate hash drift")
    plan = _read_json(plan_path)
    if (
        plan.get("collision_policy") != "fail"
        or plan.get("promotion_mode") != "atomic-no-replace"
        or plan.get("secret_policy") != "references-only"
    ):
        raise PhaseFourContextIntakeError("intake safety policy drift")
    assets = plan.get("assets")
    if not isinstance(assets, list):
        raise PhaseFourContextIntakeError("intake asset roster is invalid")
    if [asset.get("asset_id") for asset in assets] != list(ASSET_RULES):
        raise PhaseFourContextIntakeError("intake asset roster drift")
    for asset in assets:
        if (
            asset.get("state") != "authorized"
            or asset.get("attempts") != []
            or any(value is not None for value in asset["observed"].values())
        ):
            raise PhaseFourContextIntakeError(
                f"intake asset is not pristine authorized: {asset.get('asset_id')}"
            )
    expected = plan["extensions"].get("metadata_only_expected_counts")
    if expected != {
        asset_id: rule["count"] for asset_id, rule in ASSET_RULES.items()
    }:
        raise PhaseFourContextIntakeError("metadata count contract drift")
    return plan


def validate_finalized_context_intake(
    repository_root: Path,
) -> dict[str, Any]:
    """Revalidate the exact promoted U04 custody without contacting USGS."""

    root = repository_root.resolve()
    contract_path = root / PLAN_PATH
    gate_path = root / SOURCE_GATE_PATH
    if _sha256_file(contract_path) != FINAL_CONTRACT_SHA256:
        raise PhaseFourContextIntakeError("final intake contract hash drift")
    if _sha256_file(gate_path) != SOURCE_GATE_SHA256:
        raise PhaseFourContextIntakeError("source gate hash drift")
    contract = _read_json(contract_path)
    if (
        contract.get("extensions", {}).get("state")
        != "PASS_EXACT_PUBLIC_TNM_CONTEXT_CUSTODY_FOR_U05"
        or contract["extensions"].get("asset_count") != len(ASSET_RULES)
        or contract["extensions"].get("all_promoted") is not True
        or contract["extensions"].get("all_single_link") is not True
    ):
        raise PhaseFourContextIntakeError("final intake state drift")
    summaries: list[dict[str, Any]] = []
    for asset in contract.get("assets", []):
        asset_id = asset.get("asset_id")
        if asset_id not in ASSET_RULES or asset.get("state") != "promoted":
            raise PhaseFourContextIntakeError("final asset state drift")
        destination = _asset_path(root, contract, asset, "destination")
        observed = asset.get("observed", {})
        digest = observed.get("promoted_sha256")
        size = observed.get("promoted_size_bytes")
        if (
            not destination.is_file()
            or destination.is_symlink()
            or destination.stat().st_nlink != 1
            or destination.stat().st_size != size
            or _sha256_file(destination) != digest
            or observed.get("staged_sha256") != digest
            or observed.get("staged_size_bytes") != size
        ):
            raise PhaseFourContextIntakeError(
                f"final custody identity drift: {asset_id}"
            )
        validation = validate_feature_collection(
            destination.read_bytes(),
            asset_id=asset_id,
        )
        summaries.append(
            {
                "asset_id": asset_id,
                "bytes": size,
                "sha256": digest,
                "validation": validation,
            }
        )
    if [item["asset_id"] for item in summaries] != list(ASSET_RULES):
        raise PhaseFourContextIntakeError("final asset roster drift")
    return {
        "state": "PASS_EXACT_PUBLIC_TNM_CONTEXT_CUSTODY_FOR_U05",
        "contract_sha256": FINAL_CONTRACT_SHA256,
        "source_gate_sha256": SOURCE_GATE_SHA256,
        "asset_count": len(summaries),
        "bytes": sum(item["bytes"] for item in summaries),
        "assets": summaries,
    }


def validate_feature_collection(
    payload: bytes,
    *,
    asset_id: str,
) -> dict[str, Any]:
    """Validate one exact ArcGIS GeoJSON response without trusting its name."""

    if asset_id not in ASSET_RULES:
        raise PhaseFourContextIntakeError("unknown context asset")
    if not payload or len(payload) > MAX_RESPONSE_BYTES:
        raise PhaseFourContextIntakeError("context response size is invalid")
    try:
        value = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PhaseFourContextIntakeError(
            f"context response is not UTF-8 JSON: {asset_id}"
        ) from exc
    if not isinstance(value, dict) or value.get("type") != "FeatureCollection":
        if isinstance(value, dict) and "error" in value:
            raise PhaseFourContextIntakeError(
                f"ArcGIS error response: {asset_id}"
            )
        raise PhaseFourContextIntakeError(
            f"FeatureCollection required: {asset_id}"
        )
    features = value.get("features")
    rule = ASSET_RULES[asset_id]
    if not isinstance(features, list) or len(features) != rule["count"]:
        raise PhaseFourContextIntakeError(
            f"feature count drift: {asset_id}"
        )
    try:
        from shapely.geometry import shape
    except ImportError as exc:
        raise PhaseFourContextIntakeError(
            "locked geo-research profile is required"
        ) from exc
    object_ids: list[int] = []
    geometry_types: dict[str, int] = {}
    total_vertices = 0
    for index, feature in enumerate(features):
        if not isinstance(feature, dict) or feature.get("type") != "Feature":
            raise PhaseFourContextIntakeError(
                f"invalid GeoJSON feature: {asset_id}[{index}]"
            )
        properties = feature.get("properties")
        if not isinstance(properties, dict):
            raise PhaseFourContextIntakeError(
                f"feature properties absent: {asset_id}[{index}]"
            )
        fields = {str(key).casefold() for key in properties}
        if fields != rule["fields"]:
            raise PhaseFourContextIntakeError(
                f"feature field roster drift: {asset_id}"
            )
        object_id = next(
            (
                value
                for key, value in properties.items()
                if str(key).casefold() == "objectid"
            ),
            None,
        )
        if (
            not isinstance(object_id, int)
            or isinstance(object_id, bool)
            or object_id in object_ids
        ):
            raise PhaseFourContextIntakeError(
                f"invalid or duplicate object ID: {asset_id}"
            )
        object_ids.append(object_id)
        geometry = shape(feature.get("geometry"))
        if (
            geometry.is_empty
            or not geometry.is_valid
            or geometry.geom_type not in rule["geometry_types"]
        ):
            raise PhaseFourContextIntakeError(
                f"geometry type or validity drift: {asset_id}"
            )
        bounds = geometry.bounds
        if not all(
            (
                float("-inf") < coordinate < float("inf")
                and (
                    -180.0 <= coordinate <= 180.0
                    if position % 2 == 0
                    else -90.0 <= coordinate <= 90.0
                )
            )
            for position, coordinate in enumerate(bounds)
        ):
            raise PhaseFourContextIntakeError(
                f"geometry coordinate domain drift: {asset_id}"
            )
        geometry_types[geometry.geom_type] = (
            geometry_types.get(geometry.geom_type, 0) + 1
        )
        if geometry.geom_type == "Point":
            total_vertices += 1
        elif geometry.geom_type == "MultiPoint":
            total_vertices += len(geometry.geoms)
        elif geometry.geom_type == "LineString":
            total_vertices += len(geometry.coords)
        elif geometry.geom_type == "MultiLineString":
            total_vertices += sum(len(part.coords) for part in geometry.geoms)
        elif geometry.geom_type == "Polygon":
            total_vertices += len(geometry.exterior.coords) + sum(
                len(ring.coords) for ring in geometry.interiors
            )
        elif geometry.geom_type == "MultiPolygon":
            total_vertices += sum(
                len(part.exterior.coords)
                + sum(len(ring.coords) for ring in part.interiors)
                for part in geometry.geoms
            )
    if object_ids != sorted(object_ids):
        raise PhaseFourContextIntakeError(
            f"provider response order drift: {asset_id}"
        )
    return {
        "feature_count": len(features),
        "object_id_min": min(object_ids),
        "object_id_max": max(object_ids),
        "object_ids_strictly_increasing": True,
        "geometry_types": dict(sorted(geometry_types.items())),
        "total_vertices": total_vertices,
        "allowed_fields_exact": True,
        "all_geometries_valid": True,
        "coordinate_domain": "EPSG:4326",
    }


def _acquire(uri: str) -> tuple[bytes, str]:
    opener = build_opener(_NoRedirect())
    request = Request(
        uri,
        headers={
            "Accept": "application/geo+json, application/json",
            "User-Agent": "BurnLens/0.54.0 phase-four-context-intake",
        },
        method="GET",
    )
    try:
        with opener.open(request, timeout=60) as response:
            if response.status != 200 or response.geturl() != uri:
                raise PhaseFourContextIntakeError(
                    "context response status or final URL drift"
                )
            content_type = response.headers.get_content_type().casefold()
            if content_type not in {
                "application/json",
                "application/geo+json",
                "text/json",
                "text/plain",
            }:
                raise PhaseFourContextIntakeError(
                    f"unexpected context content type: {content_type}"
                )
            declared = response.headers.get("Content-Length")
            if declared is not None and int(declared) > MAX_RESPONSE_BYTES:
                raise PhaseFourContextIntakeError(
                    "declared context response exceeds limit"
                )
            payload = response.read(MAX_RESPONSE_BYTES + 1)
            if len(payload) > MAX_RESPONSE_BYTES:
                raise PhaseFourContextIntakeError(
                    "context response exceeds limit"
                )
            return payload, content_type
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        raise PhaseFourContextIntakeError(
            f"context transfer failed: {type(exc).__name__}"
        ) from exc


def _asset_path(root: Path, plan: dict[str, Any], asset: dict[str, Any], kind: str) -> Path:
    base = plan["staging_root"] if kind == "staging" else plan["custody_root"]
    relative = (
        asset["staging_relative_path"]
        if kind == "staging"
        else asset["destination_relative_path"]
    )
    path = (root / base / relative).resolve(strict=False)
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise PhaseFourContextIntakeError("context path escapes repository") from exc
    if path.is_symlink():
        raise PhaseFourContextIntakeError("context path is a symlink")
    return path


def _promote(staging: Path, destination: Path, digest: str, size: int) -> None:
    if (
        not staging.is_file()
        or staging.is_symlink()
        or staging.stat().st_nlink != 1
        or staging.stat().st_size != size
        or _sha256_file(staging) != digest
    ):
        raise PhaseFourContextIntakeError("verified staging identity drift")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() or destination.is_symlink():
        raise PhaseFourContextIntakeError("context destination collision")
    try:
        os.link(staging, destination, follow_symlinks=False)
    except FileExistsError as exc:
        raise PhaseFourContextIntakeError(
            "context destination collision"
        ) from exc
    if (
        destination.is_symlink()
        or not destination.is_file()
        or destination.stat().st_nlink != 2
        or destination.stat().st_size != size
        or _sha256_file(destination) != digest
    ):
        raise PhaseFourContextIntakeError(
            "atomic context promotion readback failed"
        )
    staging.unlink()
    if destination.stat().st_nlink != 1:
        raise PhaseFourContextIntakeError(
            "promoted context file is not single-link"
        )


def run_context_intake(
    *,
    repository_root: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, Any]:
    """Execute the exact eight-asset bounded context transaction."""

    root = repository_root.resolve()
    if not RUN_ID_PATTERN.fullmatch(run_id):
        raise PhaseFourContextIntakeError("run ID does not match U04 contract")
    _require_clean_head(root, git_source_commit)
    plan = _load_exact_plan(root)
    candidate = deepcopy(plan)
    run_directory = root / RUN_ROOT / run_id
    if run_directory.exists() or run_directory.is_symlink():
        raise PhaseFourContextIntakeError(f"run already exists: {run_id}")
    run_directory.mkdir(parents=True)
    started = {
        "attempt_version": INTAKE_VERSION,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "git_source_commit": git_source_commit,
        "status": "STARTED",
    }
    _write_new(run_directory / "RUN-STARTED.json", _json_bytes(started))
    summaries: list[dict[str, Any]] = []
    try:
        for asset in candidate["assets"]:
            asset_id = asset["asset_id"]
            staging = _asset_path(root, candidate, asset, "staging")
            destination = _asset_path(root, candidate, asset, "destination")
            if (
                staging.exists()
                or staging.is_symlink()
                or destination.exists()
                or destination.is_symlink()
            ):
                raise PhaseFourContextIntakeError(
                    f"preflight path collision: {asset_id}"
                )
            attempt = {
                "attempt_id": f"{asset_id}-r001",
                "started_at": generated_at_utc,
                "completed_at": None,
                "outcome": "started",
            }
            asset["state"] = "staging"
            asset["attempts"].append(attempt)
            payload, content_type = _acquire(asset["source"]["uri"])
            validation = validate_feature_collection(
                payload,
                asset_id=asset_id,
            )
            _write_new(staging, payload)
            digest = _sha256_file(staging)
            size = staging.stat().st_size
            asset["observed"]["staged_sha256"] = digest
            asset["observed"]["staged_size_bytes"] = size
            asset["state"] = "verified"
            attempt["completed_at"] = generated_at_utc
            attempt["outcome"] = "succeeded"
            _promote(staging, destination, digest, size)
            asset["observed"]["promoted_sha256"] = digest
            asset["observed"]["promoted_size_bytes"] = size
            asset["state"] = "promoted"
            summaries.append(
                {
                    "asset_id": asset_id,
                    "destination_relative_path": (
                        Path(candidate["custody_root"])
                        / asset["destination_relative_path"]
                    ).as_posix(),
                    "bytes": size,
                    "sha256": digest,
                    "content_type": content_type,
                    "validation": validation,
                }
            )
        candidate["extensions"].update(
            {
                "state": "PASS_EXACT_PUBLIC_TNM_CONTEXT_CUSTODY_FOR_U05",
                "run_id": run_id,
                "git_source_commit": git_source_commit,
                "completed_at_utc": generated_at_utc,
                "asset_count": len(summaries),
                "all_promoted": True,
                "all_single_link": True,
            }
        )
        candidate_bytes = _json_bytes(candidate)
        _write_new(
            run_directory / "INTAKE-CONTRACT-FINAL.json",
            candidate_bytes,
        )
        result = {
            "result_version": INTAKE_VERSION,
            "generated_at_utc": generated_at_utc,
            "run_id": run_id,
            "git_source_commit": git_source_commit,
            "state": "PASS_EXACT_PUBLIC_TNM_CONTEXT_CUSTODY_FOR_U05",
            "source_gate": {
                "path": SOURCE_GATE_PATH.as_posix(),
                "sha256": SOURCE_GATE_SHA256,
            },
            "intake_plan": {
                "path": PLAN_PATH.as_posix(),
                "sha256": PLAN_SHA256,
            },
            "final_contract": {
                "path": "INTAKE-CONTRACT-FINAL.json",
                "bytes": len(candidate_bytes),
                "sha256": sha256(candidate_bytes).hexdigest(),
            },
            "assets": summaries,
            "total_assets": len(summaries),
            "total_bytes": sum(item["bytes"] for item in summaries),
            "privacy_scan": {
                "minimal_declared_fields_only": True,
                "personal_contact_fields_retained": False,
                "secret_fields_retained": False,
                "private_provider_routes_retained": False,
            },
            "boundaries": {
                "context_is_label_truth": False,
                "context_is_operational_authority": False,
                "routing_or_closure_use": False,
                "native_bulk_package_acquired": False,
                "authentication_used": False,
                "paid_service_used": False,
            },
            "next_dependency": "P4O1-T01-U04 exact MTBS local-boundary reuse validation and closure",
        }
        result_bytes = _json_bytes(result)
        _write_new(run_directory / "CONTEXT-INTAKE-RESULT.json", result_bytes)
        complete = {
            **started,
            "status": "COMPLETE",
            "state": result["state"],
            "asset_count": len(summaries),
            "total_bytes": result["total_bytes"],
            "result_sha256": sha256(result_bytes).hexdigest(),
            "final_contract_sha256": sha256(candidate_bytes).hexdigest(),
        }
        _write_new(run_directory / "RUN-COMPLETE.json", _json_bytes(complete))
        return result
    except Exception as exc:
        failure_contract = _json_bytes(candidate)
        try:
            _write_new(
                run_directory / "INTAKE-CONTRACT-FAILED.json",
                failure_contract,
            )
            _write_new(
                run_directory / "FAILURE.json",
                _json_bytes(
                    {
                        **started,
                        "status": "FAILED",
                        "error_type": type(exc).__name__,
                        "error": str(exc),
                        "promoted_assets": [
                            asset["asset_id"]
                            for asset in candidate["assets"]
                            if asset.get("state") == "promoted"
                        ],
                    }
                ),
            )
        except Exception:
            pass
        raise
