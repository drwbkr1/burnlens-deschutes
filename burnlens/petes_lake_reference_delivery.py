"""Identity-first preflight for the exact delivered Petes Lake MTBS archive."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
import re
from typing import Any, Iterable
from zipfile import BadZipFile, ZipFile


CONTRACT_VERSION = "petes-lake-reference-delivery-preflight-v0.1.0"
EXPECTED_MAP_ID = 10031414
EXPECTED_EVENT_ID = "OR4396912190120230825"
EXPECTED_PROGRAM = "MTBS"
MAX_ARCHIVES = 2
MAX_ARCHIVE_BYTES = 1024 * 1024 * 1024
MAX_TOTAL_ARCHIVE_BYTES = 2 * 1024 * 1024 * 1024
MAX_MEMBERS_PER_ARCHIVE = 5_000
MAX_UNCOMPRESSED_BYTES_PER_ARCHIVE = 12 * 1024 * 1024 * 1024
MAX_EXPANSION_RATIO = 200
NOTICE_TOKENS = ("readme", "notice", "license", "citation", "metadata", "meta", "tip_sheet")


class PetesLakeReferenceDeliveryError(RuntimeError):
    """Delivered Petes Lake archive preflight failed closed."""


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
        found.update(int(token) for token in re.findall(r"(?<!\d)(100\d{5})(?!\d)", name))
    return found


def _has_program_token(names: Iterable[str], program: str) -> bool:
    token = program.casefold()
    for name in names:
        parts = [part.casefold() for part in PurePosixPath(name).parts]
        if token in parts or any(part.startswith(token + "_") for part in parts):
            return True
    return False


def inspect_delivery(archives: list[Path]) -> dict[str, Any]:
    if not 1 <= len(archives) <= MAX_ARCHIVES:
        raise PetesLakeReferenceDeliveryError("delivery must contain one or two archives")
    resolved = [path.resolve() for path in archives]
    if len(set(resolved)) != len(resolved):
        raise PetesLakeReferenceDeliveryError("duplicate archive path")
    if any(path.suffix.lower() != ".zip" or not path.is_file() for path in resolved):
        raise PetesLakeReferenceDeliveryError("every delivery input must be an existing ZIP")
    sizes = [path.stat().st_size for path in resolved]
    if any(size <= 0 or size > MAX_ARCHIVE_BYTES for size in sizes):
        raise PetesLakeReferenceDeliveryError("archive size outside bounded range")
    if sum(sizes) > MAX_TOTAL_ARCHIVE_BYTES:
        raise PetesLakeReferenceDeliveryError("total archive size exceeds bounded range")

    summaries: list[dict[str, Any]] = []
    all_names: list[str] = []
    try:
        for index, (path, size) in enumerate(zip(resolved, sizes, strict=True), start=1):
            with ZipFile(path) as archive:
                infos = archive.infolist()
                names = [item.filename for item in infos]
                if not infos or len(infos) > MAX_MEMBERS_PER_ARCHIVE:
                    raise PetesLakeReferenceDeliveryError("archive member count outside bounded range")
                if any(not _safe_member(name) for name in names):
                    raise PetesLakeReferenceDeliveryError("unsafe archive member path")
                if len({name.casefold() for name in names}) != len(names):
                    raise PetesLakeReferenceDeliveryError("case-insensitive duplicate member path")
                if any(item.flag_bits & 0x1 for item in infos):
                    raise PetesLakeReferenceDeliveryError("encrypted archive member")
                if any(_is_symlink(item.external_attr) for item in infos):
                    raise PetesLakeReferenceDeliveryError("archive symlink member")
                if any(name.lower().endswith((".zip", ".7z", ".rar")) for name in names):
                    raise PetesLakeReferenceDeliveryError("nested archive member")
                uncompressed = sum(item.file_size for item in infos)
                if uncompressed > MAX_UNCOMPRESSED_BYTES_PER_ARCHIVE:
                    raise PetesLakeReferenceDeliveryError("archive expansion exceeds bounded bytes")
                if uncompressed > max(size, 1) * MAX_EXPANSION_RATIO:
                    raise PetesLakeReferenceDeliveryError("archive expansion ratio exceeds bound")
                bad = archive.testzip()
                if bad is not None:
                    raise PetesLakeReferenceDeliveryError("archive CRC failure")
                summaries.append(
                    {
                        "filename": f"petes-lake-mtbs-reference-delivery-{index:03d}.zip",
                        "provider_filename_retained": False,
                        "bytes": size,
                        "sha256": _sha256(path),
                        "member_count": len(infos),
                        "uncompressed_bytes": uncompressed,
                        "expansion_ratio": round(uncompressed / size, 4),
                        "map_ids_in_member_names": sorted(_map_ids_from_names(names)),
                        "notice_candidates": sorted(
                            name
                            for name in names
                            if any(token in PurePosixPath(name).name.casefold() for token in NOTICE_TOKENS)
                        ),
                        "crc_pass": True,
                        "safe_structure_pass": True,
                    }
                )
                all_names.extend(names)
    except BadZipFile as error:
        raise PetesLakeReferenceDeliveryError("delivery contains an unreadable ZIP") from error

    observed_map_ids = _map_ids_from_names(all_names)
    if observed_map_ids != {EXPECTED_MAP_ID}:
        raise PetesLakeReferenceDeliveryError(
            f"expected only Petes Lake map ID {EXPECTED_MAP_ID}; observed {sorted(observed_map_ids)}"
        )
    if EXPECTED_EVENT_ID.casefold() not in "\n".join(all_names).casefold():
        raise PetesLakeReferenceDeliveryError("Petes Lake event ID is absent from member names")
    if not _has_program_token(all_names, EXPECTED_PROGRAM):
        raise PetesLakeReferenceDeliveryError("MTBS program token is absent from member names")
    unexpected_programs = [
        program for program in ("BAER", "RAVG") if _has_program_token(all_names, program)
    ]
    if unexpected_programs:
        raise PetesLakeReferenceDeliveryError(
            f"unexpected cross-program product families: {unexpected_programs}"
        )
    notice_candidates = sorted(
        {candidate for summary in summaries for candidate in summary["notice_candidates"]}
    )
    if not notice_candidates:
        raise PetesLakeReferenceDeliveryError("delivery exposes no notice or metadata candidates")
    return {
        "contract_version": CONTRACT_VERSION,
        "archive_count": len(summaries),
        "archive_bytes": sum(sizes),
        "expected_event_id": EXPECTED_EVENT_ID,
        "event_id_present": True,
        "expected_map_id": EXPECTED_MAP_ID,
        "observed_map_ids": sorted(observed_map_ids),
        "programs": [EXPECTED_PROGRAM],
        "unexpected_programs": [],
        "notice_candidates": notice_candidates,
        "archives": summaries,
        "decision": "PASS_SAFE_EXACT_PETES_LAKE_MTBS_DELIVERY_PREFLIGHT",
        "next_gate": (
            "Open and retain exact archive notices first; only after terms resolve may U04 inspect "
            "metadata, CRS, grids, nodata, masks, class domains, and native raster contracts."
        ),
        "reference_pixels_opened": False,
        "label_dataset_model_state": "UNCHANGED_NONE_ADVANCED",
    }


def write_receipt(report: dict[str, Any], output_path: Path) -> None:
    if output_path.exists():
        raise PetesLakeReferenceDeliveryError("preflight receipt exists; no overwrite allowed")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
