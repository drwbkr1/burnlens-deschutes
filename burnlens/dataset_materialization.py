"""Materialize the exact native-grid BurnLens prototype dataset."""

from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
import math
import os
from pathlib import Path
import shutil
from typing import Any

import numpy as np
import rasterio
from rasterio.transform import array_bounds
from rasterio.windows import Window, from_bounds

from . import __version__


DATASET_VERSION = "burnlens-dataset-v0.1.0"
DATASET_ID = "DATASET-2026-001"
DATASET_MANIFEST_VERSION = "burnlens-dataset-manifest-v0.1.0"
TASK_ISSUE = 562
UNIT_ID = "P2O5-T03-U03"
CONTRACT_PATH = Path(
    "records/phase-two/manifests/DATASET-BUILD-CONTRACT-2026-001.json"
)
CONTRACT_SHA256 = (
    "f6106691d42692f39684ed43c35f7c097d51f08b13c3dc3bf1e030ca9687b67f"
)
SPLIT_PATH = Path(
    "records/phase-two/manifests/WHOLE-EVENT-SPLIT-2026-001.json"
)
SPLIT_SHA256 = (
    "a62e66f4f81a95a56a727b29bb382cb87369306f11e2f2a4527d1c7fb68d0b99"
)
CANDIDATE_PATH = Path(
    "records/phase-two/readiness/DATASET-CANDIDATE-2026-002.json"
)
CANDIDATE_SHA256 = (
    "4a9646af493cdce81d0cd57405ebccf0dfecf5ca77c96930d0837c3b7d4e65f2"
)
PATCH_SIZE = 64
FEATURE_BANDS = ("B04", "B8A", "B12")
ELIGIBLE_SCL = (4, 5)
STATE_NODATA = np.uint8(255)


class DatasetMaterializationError(RuntimeError):
    """A deterministic dataset materialization failure."""


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(
        "utf-8"
    )


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(8 * 1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _binding(root: Path, relative: Path) -> dict[str, Any]:
    path = root / relative
    if not path.is_file():
        raise DatasetMaterializationError(
            f"required input is absent: {relative.as_posix()}"
        )
    return {
        "path": relative.as_posix(),
        "bytes": path.stat().st_size,
        "sha256": _sha256_file(path),
    }


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise DatasetMaterializationError(
            f"JSON root is not an object: {path}"
        )
    return value


def _validate_inputs(
    root: Path,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    bindings = {
        "contract": _binding(root, CONTRACT_PATH),
        "split": _binding(root, SPLIT_PATH),
        "candidate": _binding(root, CANDIDATE_PATH),
    }
    expected = {
        "contract": CONTRACT_SHA256,
        "split": SPLIT_SHA256,
        "candidate": CANDIDATE_SHA256,
    }
    for name, digest in expected.items():
        if bindings[name]["sha256"] != digest:
            raise DatasetMaterializationError(f"{name} hash drift")
    contract = _read_json(root / CONTRACT_PATH)
    split = _read_json(root / SPLIT_PATH)
    candidate = _read_json(root / CANDIDATE_PATH)
    if split.get("split_version") != "burnlens-whole-event-split-v0.1.0":
        raise DatasetMaterializationError("split version drift")
    if split.get("sealed_test", {}).get("open_count") != 0:
        raise DatasetMaterializationError("test was already opened")
    if contract["patch_contract"]["patch_size_pixels"] != [64, 64]:
        raise DatasetMaterializationError("patch-size contract drift")
    if contract["input_contract"]["channel_order"] != [
        "pre_B04",
        "pre_B8A",
        "pre_B12",
        "post_B04",
        "post_B8A",
        "post_B12",
    ]:
        raise DatasetMaterializationError("channel-order contract drift")
    return contract, split, candidate


def _registration_index(
    root: Path,
) -> dict[str, tuple[Path, dict[str, Any], dict[str, Any]]]:
    raw_root = root / "downloads/phase-two/raw"
    output: dict[str, tuple[Path, dict[str, Any], dict[str, Any]]] = {}
    for registration_path in raw_root.rglob(".burnlens-registration.json"):
        registration = _read_json(registration_path)
        if registration.get("synthetic_fixture") is not False:
            continue
        for asset in registration.get("assets", []):
            filename = asset.get("filename")
            if not isinstance(filename, str):
                continue
            archive_path = registration_path.parent / filename
            if filename in output:
                raise DatasetMaterializationError(
                    f"duplicate registered archive filename: {filename}"
                )
            output[filename] = (archive_path, registration, asset)
    return output


def verify_archives(
    root: Path, contract: dict[str, Any]
) -> dict[str, dict[str, Any]]:
    index = _registration_index(root)
    verified: dict[str, dict[str, Any]] = {}
    for event in contract["source_pairs"]:
        for product in event["products"]:
            filename = product.get("filename")
            if filename not in index:
                raise DatasetMaterializationError(
                    f"registered archive is absent: {filename}"
                )
            path, registration, asset = index[filename]
            if not path.is_file():
                raise DatasetMaterializationError(
                    f"archive bytes are absent: {filename}"
                )
            if asset.get("native_id") != product.get("native_id"):
                raise DatasetMaterializationError(
                    f"registered native ID drift: {filename}"
                )
            observed_bytes = path.stat().st_size
            if observed_bytes != asset.get("bytes"):
                raise DatasetMaterializationError(
                    f"registered archive size drift: {filename}"
                )
            if path.stat().st_nlink != 1:
                raise DatasetMaterializationError(
                    f"registered archive link-count drift: {filename}"
                )
            observed_sha256 = _sha256_file(path)
            if observed_sha256 != asset.get("sha256"):
                raise DatasetMaterializationError(
                    f"registered archive hash drift: {filename}"
                )
            verified[product["role"]] = {
                "role": product["role"],
                "package_id": registration["package_id"],
                "registration_run_id": registration["run_id"],
                "registration_manifest_sha256": _sha256_file(
                    path.parent / ".burnlens-registration.json"
                ),
                "native_id": asset["native_id"],
                "filename": filename,
                "bytes": observed_bytes,
                "sha256": observed_sha256,
                "md5": asset.get("md5"),
                "blake3": asset.get("blake3"),
                "filesystem_link_count": path.stat().st_nlink,
                "_path": path,
            }
    if len(verified) != 12:
        raise DatasetMaterializationError(
            f"exactly 12 archives are required, observed {len(verified)}"
        )
    return verified


def _aligned_source_window(
    source: rasterio.DatasetReader,
    target_transform: rasterio.Affine,
    target_shape: tuple[int, int],
) -> Window:
    bounds = array_bounds(*target_shape, target_transform)
    candidate = from_bounds(*bounds, transform=source.transform)
    rounded = Window(
        round(float(candidate.col_off)),
        round(float(candidate.row_off)),
        round(float(candidate.width)),
        round(float(candidate.height)),
    )
    deltas = (
        abs(float(candidate.col_off) - rounded.col_off),
        abs(float(candidate.row_off) - rounded.row_off),
        abs(float(candidate.width) - rounded.width),
        abs(float(candidate.height) - rounded.height),
    )
    if max(deltas) > 1e-7:
        raise DatasetMaterializationError(
            "candidate grid is not integer-aligned to the source"
        )
    if (
        rounded.col_off < 0
        or rounded.row_off < 0
        or rounded.col_off + rounded.width > source.width
        or rounded.row_off + rounded.height > source.height
    ):
        raise DatasetMaterializationError(
            "candidate grid exceeds the source raster"
        )
    if source.window_transform(rounded) != target_transform:
        raise DatasetMaterializationError(
            "source window transform differs from candidate grid"
        )
    return rounded


def _read_member(
    archive_path: Path,
    member: str,
    target_transform: rasterio.Affine,
    target_shape: tuple[int, int],
    dtype: str,
) -> np.ndarray:
    uri = archive_path.resolve().as_posix()
    with rasterio.open(f"zip://{uri}!{member}") as source:
        if source.driver != "JP2OpenJPEG":
            raise DatasetMaterializationError("unexpected Sentinel driver")
        if source.crs is None or source.crs.to_epsg() != 32610:
            raise DatasetMaterializationError("Sentinel CRS drift")
        if source.count != 1 or source.dtypes != (dtype,):
            raise DatasetMaterializationError(
                f"Sentinel raster dtype/count drift: {member}"
            )
        if abs(source.transform.a - 20.0) > 1e-9 or abs(
            source.transform.e + 20.0
        ) > 1e-9:
            raise DatasetMaterializationError(
                f"Sentinel source is not native 20 m: {member}"
            )
        window = _aligned_source_window(
            source, target_transform, target_shape
        )
        values = source.read(1, window=window)
    if values.shape != target_shape:
        raise DatasetMaterializationError(
            f"source window shape drift: {member}"
        )
    return values


def _registration(
    report: dict[str, Any], event_id: str
) -> dict[str, Any]:
    if isinstance(report.get("events"), list):
        matching = [
            event
            for event in report["events"]
            if event.get("event_group_id") == event_id
        ]
        if len(matching) != 1:
            raise DatasetMaterializationError(
                f"source report event is not unique: {event_id}"
            )
        registration = matching[0].get("registration")
    elif isinstance(report.get("registration"), dict):
        registration = report["registration"]
    else:
        registration = report.get("optical_reverification", {}).get(
            "registration"
        )
    if not isinstance(registration, dict) or not isinstance(
        registration.get("windows"), list
    ):
        raise DatasetMaterializationError(
            f"registration evidence is absent: {event_id}"
        )
    return registration


def _registration_pass_mask(
    registration: dict[str, Any], shape: tuple[int, int]
) -> tuple[np.ndarray, dict[str, int]]:
    state = np.full(shape, 3, dtype=np.uint8)
    rank = {"pass": 0, "review-needed": 1, "excluded": 2}
    covered = np.zeros(shape, dtype=bool)
    for item in registration["windows"]:
        value = rank.get(item.get("state"))
        if value is None:
            raise DatasetMaterializationError(
                "unsupported registration state"
            )
        window = item.get("pixel_window", {})
        row = int(window.get("row_offset", -1))
        column = int(window.get("column_offset", -1))
        height = int(window.get("height", 0))
        width = int(window.get("width", 0))
        if (
            row < 0
            or column < 0
            or height <= 0
            or width <= 0
            or row + height > shape[0]
            or column + width > shape[1]
        ):
            raise DatasetMaterializationError(
                "registration window exceeds candidate grid"
            )
        view = state[row : row + height, column : column + width]
        coverage = covered[row : row + height, column : column + width]
        view[~coverage] = value
        view[coverage] = np.maximum(view[coverage], value)
        coverage[:] = True
    counts = {
        "pass": int(np.count_nonzero(state == 0)),
        "review_needed": int(np.count_nonzero(state == 1)),
        "excluded": int(np.count_nonzero(state == 2)),
        "uncovered": int(np.count_nonzero(state == 3)),
    }
    return state == 0, counts


def _event_state(
    root: Path, event: dict[str, Any]
) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    arrays: dict[str, np.ndarray] = {}
    first_profile: tuple[
        tuple[int, int], rasterio.Affine, str
    ] | None = None
    for candidate in event["candidates"]:
        path = root / candidate["raster"]["path"]
        with rasterio.open(path) as source:
            values = source.read(1)
            profile = (values.shape, source.transform, str(source.crs))
        if first_profile is None:
            first_profile = profile
        elif profile != first_profile:
            raise DatasetMaterializationError(
                f"candidate grid mismatch: {event['event_group_id']}"
            )
        if set(int(value) for value in np.unique(values)) - {0, 1, 2, 255}:
            raise DatasetMaterializationError(
                f"candidate value-domain drift: {candidate['candidate_id']}"
            )
        if int(np.count_nonzero(values == 1)) != candidate["core_pixels"]:
            raise DatasetMaterializationError(
                f"candidate core-count drift: {candidate['candidate_id']}"
            )
        if int(np.count_nonzero(values == 2)) != candidate[
            "unknown_ring_pixels"
        ]:
            raise DatasetMaterializationError(
                f"candidate unknown-count drift: {candidate['candidate_id']}"
            )
        arrays[candidate["candidate_id"]] = values
    if first_profile is None:
        raise DatasetMaterializationError("event has no candidates")
    shape = first_profile[0]
    state = np.full(shape, STATE_NODATA, dtype=np.uint8)
    unknown_union = np.logical_or.reduce(
        [values == 2 for values in arrays.values()]
    )
    state[unknown_union] = 2
    occupied = np.zeros(shape, dtype=bool)
    for candidate in event["candidates"]:
        core = arrays[candidate["candidate_id"]] == 1
        other_unknown = np.logical_or.reduce(
            [
                values == 2
                for candidate_id, values in arrays.items()
                if candidate_id != candidate["candidate_id"]
            ]
        )
        if np.any(core & occupied) or np.any(core & other_unknown):
            raise DatasetMaterializationError(
                f"candidate core collision: {candidate['candidate_id']}"
            )
        state[core] = 0 if candidate["class"] == "background" else 1
        occupied |= core
    return state, arrays


def _patch_window(core: np.ndarray) -> tuple[int, int, int, int]:
    rows, columns = np.where(core)
    if not len(rows):
        raise DatasetMaterializationError("candidate core is empty")
    center_row = math.floor(float(rows.mean()))
    center_column = math.floor(float(columns.mean()))
    row = min(max(center_row - PATCH_SIZE // 2, 0), core.shape[0] - PATCH_SIZE)
    column = min(
        max(center_column - PATCH_SIZE // 2, 0),
        core.shape[1] - PATCH_SIZE,
    )
    if row < 0 or column < 0:
        raise DatasetMaterializationError(
            "event grid is smaller than the fixed patch"
        )
    window = (row, column, PATCH_SIZE, PATCH_SIZE)
    patch_core = core[row : row + PATCH_SIZE, column : column + PATCH_SIZE]
    if int(patch_core.sum()) != int(core.sum()):
        raise DatasetMaterializationError("fixed patch clips a candidate core")
    return window


def _npy_bytes(array: np.ndarray) -> bytes:
    import io

    output = io.BytesIO()
    np.save(output, array, allow_pickle=False)
    return output.getvalue()


def _file_record(path: Path, relative_to: Path) -> dict[str, Any]:
    return {
        "path": path.relative_to(relative_to).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": _sha256_file(path),
    }


def _role_by_event(split: dict[str, Any]) -> dict[str, str]:
    output: dict[str, str] = {}
    for role, summary in split["selection"]["roles"].items():
        for event_id in summary["event_group_ids"]:
            if event_id in output:
                raise DatasetMaterializationError(
                    f"event crosses roles: {event_id}"
                )
            output[event_id] = role
    if len(output) != 6:
        raise DatasetMaterializationError("split event roster drift")
    return output


def materialize(
    root: Path,
    output_directory: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, Any]:
    contract, split, candidate = _validate_inputs(root)
    verified = verify_archives(root, contract)
    role_by_event = _role_by_event(split)
    pair_by_event = {
        pair["event_group_id"]: pair for pair in contract["source_pairs"]
    }
    event_by_id = {
        event["event_group_id"]: event for event in candidate["events"]
    }
    output_directory.mkdir(parents=True, exist_ok=False)
    patch_records: list[dict[str, Any]] = []
    archive_records = []
    try:
        for record in verified.values():
            archive_records.append(
                {key: value for key, value in record.items() if key != "_path"}
            )
        for event_id in sorted(event_by_id):
            event = event_by_id[event_id]
            pair = pair_by_event[event_id]
            state, candidate_arrays = _event_state(root, event)
            shape = state.shape
            transform = rasterio.Affine(
                *event["candidates"][0]["raster_contract"]["transform"]
            )
            report = _read_json(root / pair["source_report"]["path"])
            registration_pass, registration_counts = _registration_pass_mask(
                _registration(report, event_id), shape
            )
            features: list[np.ndarray] = []
            numeric_valid = np.ones(shape, dtype=bool)
            scl_values: list[np.ndarray] = []
            source_members: list[dict[str, Any]] = []
            for product in pair["products"]:
                archive = verified[product["role"]]["_path"]
                for band in FEATURE_BANDS:
                    dn = _read_member(
                        archive,
                        product["members"][band],
                        transform,
                        shape,
                        "uint16",
                    )
                    valid = (dn != product["nodata_dn"]) & (
                        dn != product["saturated_dn"]
                    )
                    numeric_valid &= valid
                    reflectance = (
                        dn.astype(np.float32)
                        + np.float32(product["boa_offsets"][band])
                    ) / np.float32(product["boa_quantification_value"])
                    features.append(reflectance.astype(np.float32))
                    source_members.append(
                        {
                            "role": product["role"],
                            "band": band,
                            "member": product["members"][band],
                        }
                    )
                scl_values.append(
                    _read_member(
                        archive,
                        product["members"]["SCL"],
                        transform,
                        shape,
                        "uint8",
                    )
                )
            feature_stack = np.stack(features).astype(np.float32)
            scl_valid = np.logical_and.reduce(
                [np.isin(scl, ELIGIBLE_SCL) for scl in scl_values]
            )
            input_valid = numeric_valid & scl_valid & registration_pass
            accepted_core = np.isin(state, (0, 1))
            invalid_core = accepted_core & ~input_valid
            if np.any(invalid_core):
                raise DatasetMaterializationError(
                    f"accepted core fails source validity: {event_id} "
                    f"({int(invalid_core.sum())} pixels)"
                )
            feature_stack[:, ~input_valid] = np.nan
            for candidate_region in event["candidates"]:
                candidate_id = candidate_region["candidate_id"]
                core = candidate_arrays[candidate_id] == 1
                row, column, height, width = _patch_window(core)
                own_unknown = candidate_arrays[candidate_id] == 2
                if int(
                    own_unknown[
                        row : row + height, column : column + width
                    ].sum()
                ) != int(own_unknown.sum()):
                    raise DatasetMaterializationError(
                        f"fixed patch clips an unknown ring: {candidate_id}"
                    )
                for other_id, values in candidate_arrays.items():
                    if other_id != candidate_id and np.any(
                        (values == 1)[
                            row : row + height, column : column + width
                        ]
                    ):
                        raise DatasetMaterializationError(
                            f"patch includes another candidate core: {candidate_id}"
                        )
                patch_state = state[
                    row : row + height, column : column + width
                ].copy()
                patch_valid = input_valid[
                    row : row + height, column : column + width
                ].copy()
                patch_loss = np.isin(patch_state, (0, 1)) & patch_valid
                if int(patch_loss.sum()) != candidate_region["core_pixels"]:
                    raise DatasetMaterializationError(
                        f"patch loss count drift: {candidate_id}"
                    )
                patch_features = feature_stack[
                    :, row : row + height, column : column + width
                ].copy()
                role = role_by_event[event_id]
                patch_id = (
                    f"{role}--{event_id}--{candidate_id}--"
                    f"r{row}c{column}h{height}w{width}"
                )
                patch_directory = output_directory / "patches" / patch_id
                patch_directory.mkdir(parents=True, exist_ok=False)
                arrays_to_write = {
                    "features.npy": patch_features,
                    "state.npy": patch_state,
                    "input_valid.npy": patch_valid.astype(np.uint8),
                    "loss_mask.npy": patch_loss.astype(np.uint8),
                }
                files = []
                for name, array in arrays_to_write.items():
                    path = patch_directory / name
                    path.write_bytes(_npy_bytes(array))
                    files.append(_file_record(path, output_directory))
                patch_transform = transform * rasterio.Affine.translation(
                    column, row
                )
                patch_records.append(
                    {
                        "patch_id": patch_id,
                        "split_role": role,
                        "event_group_id": event_id,
                        "candidate_id": candidate_id,
                        "class": candidate_region["class"],
                        "window": {
                            "row_offset": row,
                            "column_offset": column,
                            "height": height,
                            "width": width,
                        },
                        "crs": "EPSG:32610",
                        "transform": list(patch_transform)[:6],
                        "channel_order": contract["input_contract"][
                            "channel_order"
                        ],
                        "core_pixels": candidate_region["core_pixels"],
                        "unknown_ring_pixels_in_patch": int(
                            np.count_nonzero(patch_state == 2)
                        ),
                        "input_valid_pixels": int(patch_valid.sum()),
                        "loss_pixels": int(patch_loss.sum()),
                        "registration_state_counts_on_event_grid": (
                            registration_counts
                        ),
                        "source_members": source_members,
                        "files": sorted(files, key=lambda item: item["path"]),
                    }
                )
        patch_records.sort(key=lambda item: item["patch_id"])
        if len(patch_records) != 12:
            raise DatasetMaterializationError("dataset patch count drift")
        total_loss = sum(item["loss_pixels"] for item in patch_records)
        if total_loss != 287:
            raise DatasetMaterializationError(
                f"dataset core count drift: {total_loss}"
            )
        class_counts = Counter()
        for item in patch_records:
            class_counts[item["class"]] += item["loss_pixels"]
        if class_counts != {"background": 140, "burned": 147}:
            raise DatasetMaterializationError(
                f"dataset class-pixel count drift: {dict(class_counts)}"
            )
        manifest = {
            "dataset_manifest_version": DATASET_MANIFEST_VERSION,
            "dataset_id": DATASET_ID,
            "dataset_version": DATASET_VERSION,
            "generated_at_utc": generated_at_utc,
            "run_id": run_id,
            "repository": "drwbkr1/burnlens-deschutes",
            "task_issue": TASK_ISSUE,
            "unit_id": UNIT_ID,
            "git_source_commit": git_source_commit,
            "software_version": __version__,
            "inputs": {
                "dataset_contract": _binding(root, CONTRACT_PATH),
                "whole_event_split": _binding(root, SPLIT_PATH),
                "dataset_candidate": _binding(root, CANDIDATE_PATH),
            },
            "source_archive_verification": {
                "archive_count": len(archive_records),
                "total_bytes": sum(
                    record["bytes"] for record in archive_records
                ),
                "all_sha256_match": True,
                "all_single_link": True,
                "archives": sorted(
                    archive_records, key=lambda item: item["role"]
                ),
            },
            "dataset_contract": {
                "format": "one directory per candidate patch; NumPy .npy arrays without pickles",
                "patch_shape": [64, 64],
                "feature_shape": [6, 64, 64],
                "feature_dtype": "float32",
                "state_dtype": "uint8",
                "mask_dtype": "uint8",
                "channel_order": contract["input_contract"]["channel_order"],
                "invalid_feature_value": "NaN",
                "state_values": contract["label_contract"][
                    "combined_state_values"
                ],
                "loss_mask": contract["label_contract"]["loss_mask"],
                "metric_mask": contract["label_contract"]["metric_mask"],
                "normalization_statistics_created": False,
                "resampling": "none",
                "reprojection": "none",
                "mosaicking": "none",
            },
            "inventory": {
                "event_groups": 6,
                "patches": 12,
                "patches_by_role": dict(
                    sorted(
                        Counter(
                            item["split_role"] for item in patch_records
                        ).items()
                    )
                ),
                "accepted_core_pixels": total_loss,
                "class_core_pixels": dict(sorted(class_counts.items())),
                "source_unknown_ring_pixels": 531,
                "test_open_count": 0,
            },
            "patches": patch_records,
            "attribution": (
                "Contains modified Copernicus Sentinel data 2017-2022, "
                "accessed through the Copernicus Data Space Ecosystem; "
                "prototype region labels derive from disclosed official "
                "BAER/MTBS/RAVG evidence roles and owner review."
            ),
            "limitations": [
                "This is a sparse owner-approved prototype dataset, not independent ground truth.",
                "Only 287 labeled core pixels exist across twelve patches and six events.",
                "The balanced review roster does not estimate natural prevalence.",
                "Unknown rings, unreviewed context, invalid source pixels, and unassessed registration context never contribute to loss or metrics.",
                "The test roster is locked and its open count remains zero.",
            ],
            "boundaries": {
                "dataset_created": True,
                "split_locked": True,
                "dataset_qa_passed": False,
                "normalization_statistics_created": False,
                "baseline_created": False,
                "model_created": False,
                "metric_result_created": False,
                "test_pixels_opened": False,
                "training_authorized": False,
                "independent_ground_truth_claimed": False,
                "generalization_claimed": False,
            },
            "next_dependency": "P2O5-T03-U04",
        }
        manifest_path = output_directory / "DATASET-MANIFEST.json"
        manifest_path.write_bytes(_json_bytes(manifest))
        if _read_json(manifest_path) != manifest:
            raise DatasetMaterializationError(
                "dataset manifest exact readback failed"
            )
        return manifest
    except Exception:
        if output_directory.exists():
            shutil.rmtree(output_directory)
        raise


def write_dataset(
    root: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> Path:
    destination = (
        root / "samples/datasets" / DATASET_VERSION
    )
    if destination.exists():
        raise DatasetMaterializationError(
            f"dataset destination already exists: {destination}"
        )
    staging = (
        root
        / "downloads/phase-two/staging"
        / f"{run_id}--{DATASET_VERSION}"
    )
    if staging.exists():
        raise DatasetMaterializationError(
            f"dataset staging already exists: {staging}"
        )
    materialize(
        root, staging, generated_at_utc, run_id, git_source_commit
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    os.replace(staging, destination)
    if not (destination / "DATASET-MANIFEST.json").is_file():
        raise DatasetMaterializationError("dataset promotion readback failed")
    return destination
