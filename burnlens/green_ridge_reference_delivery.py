"""Safe, identity-first preflight for delivered Green Ridge reference archives."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
import re
from typing import Any, Iterable
from zipfile import BadZipFile, ZipFile


CONTRACT_VERSION = "green-ridge-reference-delivery-preflight-v0.1.0"
EXPECTED_MAP_IDS = {10015623: "BAER", 10021333: "MTBS", 10016049: "RAVG"}
EXPECTED_EVENT_ID = "OR4446712160520200817"
MAX_ARCHIVES = 4
MAX_ARCHIVE_BYTES = 1024 * 1024 * 1024
MAX_TOTAL_ARCHIVE_BYTES = 2 * 1024 * 1024 * 1024
MAX_MEMBERS_PER_ARCHIVE = 5_000
MAX_UNCOMPRESSED_BYTES_PER_ARCHIVE = 12 * 1024 * 1024 * 1024
MAX_EXPANSION_RATIO = 200
NOTICE_TOKENS = ("readme", "notice", "license", "citation", "metadata", "meta", "tip_sheet")


class GreenRidgeReferenceDeliveryError(RuntimeError):
    """Delivered archive preflight failed closed."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while block := source.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def _safe_member(name: str) -> bool:
    path = PurePosixPath(name)
    return bool(name) and not path.is_absolute() and ".." not in path.parts and "\\" not in name


def _is_symlink(external_attr: int) -> bool:
    return ((external_attr >> 16) & 0o170000) == 0o120000


def _map_ids_from_names(names: Iterable[str]) -> set[int]:
    found: set[int] = set()
    for name in names:
        for token in re.findall(r"(?<!\d)(100\d{5})(?!\d)", name):
            value = int(token)
            if value in EXPECTED_MAP_IDS:
                found.add(value)
    return found


def inspect_delivery(archives: list[Path]) -> dict[str, Any]:
    if not 1 <= len(archives) <= MAX_ARCHIVES:
        raise GreenRidgeReferenceDeliveryError("delivery must contain one to four archives")
    resolved = [path.resolve() for path in archives]
    if len(set(resolved)) != len(resolved):
        raise GreenRidgeReferenceDeliveryError("duplicate archive path")
    if any(path.suffix.lower() != ".zip" or not path.is_file() for path in resolved):
        raise GreenRidgeReferenceDeliveryError("every delivery input must be an existing ZIP")
    sizes = [path.stat().st_size for path in resolved]
    if any(size <= 0 or size > MAX_ARCHIVE_BYTES for size in sizes):
        raise GreenRidgeReferenceDeliveryError("archive size outside bounded range")
    if sum(sizes) > MAX_TOTAL_ARCHIVE_BYTES:
        raise GreenRidgeReferenceDeliveryError("total archive size exceeds bounded range")

    summaries: list[dict[str, Any]] = []
    all_names: list[str] = []
    try:
        for path, size in zip(resolved, sizes, strict=True):
            with ZipFile(path) as archive:
                infos = archive.infolist()
                names = [item.filename for item in infos]
                if not infos or len(infos) > MAX_MEMBERS_PER_ARCHIVE:
                    raise GreenRidgeReferenceDeliveryError("archive member count outside bounded range")
                if any(not _safe_member(name) for name in names):
                    raise GreenRidgeReferenceDeliveryError("unsafe archive member path")
                if len({name.casefold() for name in names}) != len(names):
                    raise GreenRidgeReferenceDeliveryError("case-insensitive duplicate member path")
                if any(item.flag_bits & 0x1 for item in infos):
                    raise GreenRidgeReferenceDeliveryError("encrypted archive member")
                if any(_is_symlink(item.external_attr) for item in infos):
                    raise GreenRidgeReferenceDeliveryError("archive symlink member")
                if any(name.lower().endswith(('.zip', '.7z', '.rar')) for name in names):
                    raise GreenRidgeReferenceDeliveryError("nested archive member")
                uncompressed = sum(item.file_size for item in infos)
                if uncompressed > MAX_UNCOMPRESSED_BYTES_PER_ARCHIVE:
                    raise GreenRidgeReferenceDeliveryError("archive expansion exceeds bounded bytes")
                if uncompressed > max(size, 1) * MAX_EXPANSION_RATIO:
                    raise GreenRidgeReferenceDeliveryError("archive expansion ratio exceeds bound")
                bad = archive.testzip()
                if bad is not None:
                    raise GreenRidgeReferenceDeliveryError("archive CRC failure")
                map_ids = sorted(_map_ids_from_names(names))
                notice_candidates = sorted(
                    name
                    for name in names
                    if any(token in PurePosixPath(name).name.casefold() for token in NOTICE_TOKENS)
                )
                summaries.append(
                    {
                        "filename": path.name,
                        "bytes": size,
                        "sha256": _sha256(path),
                        "member_count": len(infos),
                        "uncompressed_bytes": uncompressed,
                        "expansion_ratio": round(uncompressed / size, 4),
                        "map_ids_in_member_names": map_ids,
                        "notice_candidates": notice_candidates,
                        "crc_pass": True,
                        "safe_structure_pass": True,
                    }
                )
                all_names.extend(names)
    except BadZipFile as error:
        raise GreenRidgeReferenceDeliveryError("delivery contains an unreadable ZIP") from error

    observed_map_ids = _map_ids_from_names(all_names)
    missing = sorted(set(EXPECTED_MAP_IDS) - observed_map_ids)
    if missing:
        raise GreenRidgeReferenceDeliveryError(f"missing expected Green Ridge map IDs: {missing}")
    joined = "\n".join(all_names).casefold()
    missing_programs = sorted(
        program for program in set(EXPECTED_MAP_IDS.values()) if program.casefold() not in joined
    )
    if missing_programs:
        raise GreenRidgeReferenceDeliveryError(
            f"missing expected Green Ridge program tokens: {missing_programs}"
        )
    event_id_present = EXPECTED_EVENT_ID.casefold() in joined
    if not event_id_present:
        raise GreenRidgeReferenceDeliveryError("Green Ridge event ID is absent from member names")
    return {
        "contract_version": CONTRACT_VERSION,
        "archive_count": len(summaries),
        "archive_bytes": sum(sizes),
        "expected_event_id": EXPECTED_EVENT_ID,
        "event_id_present": event_id_present,
        "expected_map_ids": sorted(EXPECTED_MAP_IDS),
        "observed_map_ids": sorted(observed_map_ids),
        "programs": [EXPECTED_MAP_IDS[item] for item in sorted(observed_map_ids)],
        "archives": summaries,
        "decision": "PASS_SAFE_EXACT_GREEN_RIDGE_REFERENCE_DELIVERY_PREFLIGHT",
        "next_gate": (
            "Inspect exact archive notices, metadata, CRS, grids, nodata, masks, class domains, "
            "and program-specific semantics before opening or publishing raster evidence."
        ),
        "label_dataset_model_state": "UNCHANGED_NONE_ADVANCED",
    }


def write_receipt(report: dict[str, Any], output_path: Path) -> None:
    if output_path.exists():
        raise GreenRidgeReferenceDeliveryError("preflight receipt exists; no overwrite allowed")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
