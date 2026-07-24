"""Build and verify the deterministic offline BurnLens submission bundle."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import urlsplit
import zipfile


BUNDLE_ID = "BURNLENS-AUGUST-6-SUBMISSION-2026-001"
BUNDLE_VERSION = "august-6-submission-bundle-v0.1.0"
SOFTWARE_VERSION = "0.49.0"
TASK_ISSUE = 544
SOURCE_RELEASE = "v0.48.0-portfolio-reviewer-experience"
SOURCE_RELEASE_COMMIT = "05140217066277b254e78abb74cd8f61295449d0"
START_PAGE = "START-HERE.html"
INTERNAL_MANIFEST = "BUNDLE-MANIFEST.json"
REVIEWER_README = "SUBMISSION-README.txt"
FIXED_ZIP_TIME = (2026, 7, 24, 0, 0, 0)


class SubmissionBundleError(ValueError):
    """Raised when the public bundle cannot be proven safe and reproducible."""


@dataclass(frozen=True)
class BoundAsset:
    path: str
    bytes: int
    sha256: str
    role: str


BOUND_ASSETS = (
    BoundAsset(
        "portfolio/BURNLENS-PORTFOLIO-REVIEWER-EXPERIENCE-2026-001.html",
        14602,
        "e133a22978d73335c8a67fa39ae5ff48279b67ac6f71c615d95f62c021fda3ae",
        "canonical reviewer experience",
    ),
    BoundAsset(
        "portfolio/BURNLENS-PORTFOLIO-REVIEWER-EXPERIENCE-2026-001.json",
        5675,
        "cfab6176a9e5f1e9c4636e56658cf1ded9092825c3f55c7ebfb9968b2a68a078",
        "canonical reviewer manifest",
    ),
    BoundAsset(
        "portfolio/README.md",
        2300,
        "bacaae92ed18a35777528ed48dc01ddd0b8d59820ced94b199d15e4e75581d3f",
        "reviewer quickstart",
    ),
    BoundAsset(
        "samples/labels/review/windigo/phase-two/intake/"
        "WINDIGO-OWNER-RESPONSE-INTAKE-2026-001.png",
        79681,
        "0a2acfa7e23f8d6b31dcb4468474600f165840fccfa096a86521010ce6253b05",
        "strongest-result preview",
    ),
    BoundAsset(
        "samples/labels/review/windigo/phase-two/intake/"
        "WINDIGO-OWNER-RESPONSE-INTAKE-2026-001.html",
        3582,
        "6f6b9cd17494a42833ce14073bd9c6413c035963df0e445975e000c9fd35cc52",
        "strongest-result detail",
    ),
    BoundAsset(
        "docs/phase-two/objective-four/WINDIGO_OWNER_RESPONSE_INTAKE_DECISION.md",
        1566,
        "0abe41f3966d48eb02fff59ac434414a52620c973d1cbe69b14497419c93b6bb",
        "strongest-result decision",
    ),
    BoundAsset(
        "samples/cross-event/phase-two/petes-lake/"
        "PETES-LAKE-SOURCE-FITNESS-2026-001.png",
        626846,
        "4ed3870e37bf68db24805540f00614c5050c064b621ca3fc5e3c0ef244bf0d42",
        "retained-stop preview",
    ),
    BoundAsset(
        "docs/phase-two/objective-four/PETES_LAKE_MATERIAL_DEFER_DECISION.md",
        6050,
        "6e0cb457261cc0ef48b86b15e8b21a83ec21c4b880990d83b0c79834a26c31e7",
        "retained-stop decision",
    ),
    BoundAsset(
        "records/prompt-build-log/2026-07-21-p2o4-t33.md",
        116961,
        "135515b59a72890bca472fa09798966d7c7648082196693ec09b71164f5b4bdb",
        "retained-stop execution ledger",
    ),
    BoundAsset(
        "docs/case-study/BURNLENS_CASE_STUDY.md",
        84039,
        "49c4810b19fadae38d7dfe8146a17ccaa44954a18170105736c77c409de80e5c",
        "full case study",
    ),
    BoundAsset(
        "records/phase-two/release-audits/RELEASE-AUDIT-2026-002.json",
        8577,
        "f69f8d711c49b55482fcce7b5a27515118213cc050fd506d808607285c810a4f",
        "verified v0.48 release audit",
    ),
)


def _digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def _json_bytes(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=False) + "\n").encode("utf-8")


def _validate_assets(repository_root: Path) -> dict[str, bytes]:
    assets: dict[str, bytes] = {}
    for item in BOUND_ASSETS:
        path = repository_root / item.path
        if not path.is_file():
            raise SubmissionBundleError(f"bound asset missing: {item.path}")
        data = path.read_bytes()
        if len(data) != item.bytes:
            raise SubmissionBundleError(f"bound asset size changed: {item.path}")
        if _digest(data) != item.sha256:
            raise SubmissionBundleError(f"bound asset hash changed: {item.path}")
        assets[item.path] = data
    return assets


def _build_start_page(canonical_html: bytes) -> bytes:
    try:
        text = canonical_html.decode("utf-8")
    except UnicodeDecodeError as error:
        raise SubmissionBundleError("canonical reviewer HTML is not UTF-8") from error
    text = text.replace('href="BURNLENS-PORTFOLIO-', 'href="portfolio/BURNLENS-PORTFOLIO-')
    text = text.replace('href="README.md"', 'href="portfolio/README.md"')
    text = text.replace('href="../', 'href="')
    text = text.replace('src="../', 'src="')
    if "../" in text:
        raise SubmissionBundleError("start page retains an escaping relative path")
    return text.encode("utf-8")


def _reviewer_readme(*, generated_at_utc: str, run_id: str) -> bytes:
    return (
        "BURNLENS AUGUST 6 PORTFOLIO SUBMISSION\n"
        "=====================================\n\n"
        "1. Extract the complete ZIP.\n"
        "2. Open START-HERE.html in a current browser.\n"
        "3. Follow the three-step, two-minute reviewer path.\n"
        "4. Use the linked quickstart, case study, decisions, and audit for depth.\n\n"
        "The bundle is local and offline. Do not open files from inside the ZIP.\n"
        "No Python environment, provider account, credential, or network is required.\n\n"
        "BOUNDARY\n"
        "Owner-approved regions are prototype evidence, not independent ground truth.\n"
        "No accepted dataset, split, baseline, model, accuracy, or inference exists.\n"
        "BurnLens is not official, endorsed, field-validated, operational, or\n"
        "emergency-ready. Official sources govern.\n\n"
        f"Source release: {SOURCE_RELEASE}\n"
        f"Source commit: {SOURCE_RELEASE_COMMIT}\n"
        f"Bundle run: {run_id}\n"
        f"Generated UTC: {generated_at_utc}\n"
    ).encode("utf-8")


class _Links(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.targets: list[str] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        for name, value in attrs:
            if name in {"href", "src"} and value:
                self.targets.append(value)


def _normalized_local_target(value: str) -> str | None:
    if value.startswith("#") or value.startswith("data:"):
        return None
    parsed = urlsplit(value)
    if parsed.scheme or parsed.netloc or parsed.query:
        raise SubmissionBundleError(f"non-local start-page target: {value}")
    path = PurePosixPath(parsed.path)
    if path.is_absolute() or ".." in path.parts or "\\" in parsed.path:
        raise SubmissionBundleError(f"unsafe start-page target: {value}")
    return path.as_posix()


def _validate_start_links(start_page: bytes, members: set[str]) -> None:
    parser = _Links()
    parser.feed(start_page.decode("utf-8"))
    for value in parser.targets:
        target = _normalized_local_target(value)
        if target and target not in members:
            raise SubmissionBundleError(f"start-page target is not bundled: {target}")


def build_bundle_contents(
    *,
    repository_root: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, bytes]:
    """Return the exact safe archive-member map."""
    if len(git_source_commit) != 40:
        raise SubmissionBundleError("git source commit must be a full 40-character ID")
    if not run_id.strip():
        raise SubmissionBundleError("run ID is required")
    assets = _validate_assets(repository_root.resolve())
    contents = dict(assets)
    canonical = assets[
        "portfolio/BURNLENS-PORTFOLIO-REVIEWER-EXPERIENCE-2026-001.html"
    ]
    contents[START_PAGE] = _build_start_page(canonical)
    contents[REVIEWER_README] = _reviewer_readme(
        generated_at_utc=generated_at_utc, run_id=run_id
    )
    _validate_start_links(contents[START_PAGE], set(contents))
    inventory = [
        {
            "path": path,
            "bytes": len(data),
            "sha256": _digest(data),
        }
        for path, data in sorted(contents.items())
    ]
    manifest = {
        "bundle_id": BUNDLE_ID,
        "bundle_version": BUNDLE_VERSION,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": TASK_ISSUE,
        "git_source_commit": git_source_commit,
        "software_version": SOFTWARE_VERSION,
        "source_release": SOURCE_RELEASE,
        "source_release_commit": SOURCE_RELEASE_COMMIT,
        "start_page": START_PAGE,
        "dataset_version": None,
        "split_version": None,
        "baseline_version": None,
        "model_version": None,
        "files": inventory,
        "warning": (
            "Experimental owner-approved prototype evidence. Not ground truth, "
            "official wildfire information, emergency guidance, field validation, "
            "a dataset, or a model. Official sources govern."
        ),
    }
    contents[INTERNAL_MANIFEST] = _json_bytes(manifest)
    return contents


def _zip_info(path: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(path, date_time=FIXED_ZIP_TIME)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 3
    info.external_attr = 0o100644 << 16
    info.flag_bits |= 0x800
    return info


def write_bundle_no_overwrite(
    *,
    contents: dict[str, bytes],
    output_directory: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> tuple[Path, Path]:
    """Write one deterministic ZIP and outer receipt without overwrite."""
    output_directory.mkdir(parents=True, exist_ok=True)
    archive_path = output_directory / f"{BUNDLE_ID}.zip"
    receipt_path = output_directory / f"{BUNDLE_ID}-RECEIPT.json"
    for path in (archive_path, receipt_path):
        if path.exists():
            raise SubmissionBundleError(f"refusing output overwrite: {path}")
    with zipfile.ZipFile(
        archive_path, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as archive:
        for path, data in sorted(contents.items()):
            archive.writestr(_zip_info(path), data, compresslevel=9)
    archive_bytes = archive_path.read_bytes()
    manifest_bytes = contents[INTERNAL_MANIFEST]
    receipt = {
        "receipt_id": f"{BUNDLE_ID}-RECEIPT",
        "bundle_id": BUNDLE_ID,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "git_source_commit": git_source_commit,
        "software_version": SOFTWARE_VERSION,
        "archive": {
            "path": archive_path.name,
            "bytes": len(archive_bytes),
            "sha256": _digest(archive_bytes),
        },
        "internal_manifest": {
            "path": INTERNAL_MANIFEST,
            "bytes": len(manifest_bytes),
            "sha256": _digest(manifest_bytes),
        },
        "member_count": len(contents),
        "safe_structure": True,
        "deployment_or_public_sharing_authorized": False,
    }
    receipt_path.write_bytes(_json_bytes(receipt))
    validate_bundle_archive(archive_path)
    return archive_path, receipt_path


def validate_bundle_archive(archive_path: Path) -> dict[str, Any]:
    """Fail closed on unsafe structure, duplicates, drift, or broken start links."""
    with zipfile.ZipFile(archive_path) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise SubmissionBundleError("archive contains duplicate members")
        for name in names:
            path = PurePosixPath(name)
            if path.is_absolute() or ".." in path.parts or "\\" in name:
                raise SubmissionBundleError(f"unsafe archive member: {name}")
        if INTERNAL_MANIFEST not in names or START_PAGE not in names:
            raise SubmissionBundleError("archive is missing its manifest or start page")
        manifest = json.loads(archive.read(INTERNAL_MANIFEST))
        expected = {item["path"]: item for item in manifest["files"]}
        actual = set(names) - {INTERNAL_MANIFEST}
        if actual != set(expected):
            raise SubmissionBundleError("archive roster differs from manifest")
        for path, item in expected.items():
            data = archive.read(path)
            if len(data) != item["bytes"] or _digest(data) != item["sha256"]:
                raise SubmissionBundleError(f"archive member drift: {path}")
        _validate_start_links(archive.read(START_PAGE), set(names))
        return manifest
