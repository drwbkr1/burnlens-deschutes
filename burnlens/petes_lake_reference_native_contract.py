"""Terms-first native contract for the exact delivered Petes Lake MTBS bundle."""

from __future__ import annotations

import ast
from hashlib import sha256
from io import BytesIO
import json
import os
from pathlib import Path, PurePosixPath
import re
import struct
import subprocess
import tomllib
from typing import Any
import xml.etree.ElementTree as ET
from uuid import uuid4
from zipfile import BadZipFile, ZipFile

import numpy as np
import rasterio
from rasterio.crs import CRS
from rasterio.io import MemoryFile

from .petes_lake_reference_delivery import inspect_delivery
from .petes_lake_reference_request import CUSTODY_PATHS, EVENT_ID, MAP_ID


SOFTWARE_VERSION = "0.44.0"
REPORT_ID = "PETES-LAKE-REFERENCE-NATIVE-CONTRACT-2026-001"
REPORT_VERSION = "petes-lake-reference-native-contract-v0.1.0"
PROTOCOL_VERSION = "petes-lake-reference-native-contract-protocol-v0.1.0"
ARCHIVE_BYTES = 5_963_437
ARCHIVE_SHA256 = "f17db688309c72eb84460f67476c116525ae3727bddfd406a8616f1fe0fad6da"
ARCHIVE_MEMBERS = 20
CUSTODY_RUN_ID = "BL-2026-07-21-petes-lake-reference-delivery-r001"
CUSTODY_STATE_BYTES = 3_841
CUSTODY_STATE_SHA256 = "5a65cada71c845395001a109e8a93129abd4baa8691697176f6e6be3e93007b5"
REQUEST_RUN_ID = "BL-2026-07-21-petes-lake-reference-request-r001"
NATIVE_CONTRACT_RUN_ID = "BL-2026-07-21-petes-lake-reference-native-contract-r001"
MILESTONE_BRANCH = "codex/p2o4-t33-petes-lake-milestone"
REQUEST_RECEIPT_BYTES = 4_775
REQUEST_RECEIPT_SHA256 = "8f29336c5c9f79a0ceb90b65f97f9434b71bbad8087b6dda36abf188a92aa595"
ROOT = "mtbs/2023/mtbs_or4396912190120230825_10031414/"
STEM = "mtbs_or4396912190120230825_10031414"
PAIR = f"{STEM}_20230801_20240811"
DIRECTORIES = ("mtbs/", "mtbs/2023/", ROOT)
OUTPUT_PATH = (
    "samples/cross-event/phase-two/petes-lake/"
    "PETES-LAKE-REFERENCE-NATIVE-CONTRACT-2026-001.json"
)
EXPECTED_RASTER_TRANSFORM = [30.0, 0.0, 581_520.0, 0.0, -30.0, 4_874_520.0]
EXPECTED_RASTER_BOUNDS = [581_520.0, 4_863_300.0, 594_540.0, 4_874_520.0]
EXPECTED_KMZ_MEMBERS = 188
EXPECTED_KMZ_UNCOMPRESSED_BYTES = 1_181_609
NATIVE_MODULE_PATH = "burnlens/petes_lake_reference_native_contract.py"
NATIVE_CLI_PATH = "burnlens/inspect_petes_lake_reference_native_contract.py"
NATIVE_TEST_PATH = "tests/test_petes_lake_reference_native_contract.py"
IMMUTABLE_TRACE_PATHS = (
    NATIVE_CLI_PATH,
    NATIVE_TEST_PATH,
)
TRACE_ATTRIBUTE_PATHS = (
    NATIVE_MODULE_PATH,
    NATIVE_CLI_PATH,
    NATIVE_TEST_PATH,
)
TRACE_SCRIPT_NAME = "burnlens-inspect-petes-lake-reference-native-contract"
TRACE_SCRIPT_TARGET = "burnlens.inspect_petes_lake_reference_native_contract:main"
SUPPORTED_REPLAY_BRANCHES = (MILESTONE_BRANCH, "main")

EXPECTED_MEMBERS = {
    "burn_area_shp": ROOT + f"{PAIR}_burn_area.shp",
    "pre_reflectance": ROOT + f"{STEM}_20230801_l9_refl.tif",
    "burn_area_shx": ROOT + f"{PAIR}_burn_area.shx",
    "post_reflectance": ROOT + f"{STEM}_20240811_l8_refl.tif",
    "burn_area_dbf": ROOT + f"{PAIR}_burn_area.dbf",
    "dnbr": ROOT + f"{PAIR}_dnbr.tif",
    "burn_area_prj": ROOT + f"{PAIR}_burn_area.prj",
    "rdnbr": ROOT + f"{PAIR}_rdnbr.tif",
    "mask_area_shp": ROOT + f"{PAIR}_mask_area.shp",
    "dnbr6": ROOT + f"{PAIR}_dnbr6.tif",
    "mask_area_shx": ROOT + f"{PAIR}_mask_area.shx",
    "mask_area_dbf": ROOT + f"{PAIR}_mask_area.dbf",
    "mask_area_prj": ROOT + f"{PAIR}_mask_area.prj",
    "fgdc_metadata": ROOT + f"{PAIR}_metadata.xml",
    "iso_metadata": ROOT + f"{PAIR}_iso_metadata.xml",
    "kmz": ROOT + f"{PAIR}.kmz",
    "pdf": ROOT + f"{PAIR}.pdf",
}

MTBS_CLASS_SEMANTICS = {
    "0": "outside_or_nodata_not_background_truth",
    "1": "unburned_to_low_or_rapid_recovery_ambiguous_not_background_truth",
    "2": "low_severity_reference_evidence",
    "3": "moderate_severity_reference_evidence",
    "4": "high_severity_reference_evidence",
    "5": "increased_greenness_reference_evidence",
    "6": "nonprocessing_mask_excluded",
}


class PetesLakeReferenceNativeContractError(RuntimeError):
    """The exact delivered MTBS native contract failed closed."""


def validate_trace_inputs(*, generated_at_utc: str, run_id: str, git_source_commit: str) -> None:
    if not re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3,6})?Z",
        generated_at_utc,
    ):
        raise PetesLakeReferenceNativeContractError(
            "generated timestamp must be an explicit UTC Z timestamp"
        )
    if run_id != NATIVE_CONTRACT_RUN_ID:
        raise PetesLakeReferenceNativeContractError("native-contract run ID drifted")
    if not re.fullmatch(r"[0-9a-f]{40}", git_source_commit):
        raise PetesLakeReferenceNativeContractError(
            "git source commit must be an exact lowercase SHA-1"
        )


def _git(repository_root: Path, *arguments: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["GIT_ATTR_NOSYSTEM"] = "1"
    environment["GIT_TERMINAL_PROMPT"] = "0"
    return subprocess.run(
        ["git", "-C", str(repository_root), *arguments],
        check=check,
        capture_output=True,
        text=True,
        env=environment,
        timeout=30,
    )


def _git_bytes(
    repository_root: Path,
    *arguments: str,
    check: bool = True,
) -> subprocess.CompletedProcess[bytes]:
    environment = os.environ.copy()
    environment["GIT_ATTR_NOSYSTEM"] = "1"
    environment["GIT_TERMINAL_PROMPT"] = "0"
    return subprocess.run(
        ["git", "-C", str(repository_root), *arguments],
        check=check,
        capture_output=True,
        text=False,
        env=environment,
        timeout=30,
    )


def _scientific_source_fingerprint(source: str, label: str) -> str:
    """Hash every native-contract AST node except the bounded trace machinery."""

    try:
        tree = ast.parse(source)
    except SyntaxError as error:
        raise PetesLakeReferenceNativeContractError(
            f"{label} native-contract source could not be parsed"
        ) from error
    exact_trace_imports = {
        ast.dump(ast.parse(statement).body[0], include_attributes=False)
        for statement in ("import ast", "import tomllib")
    }
    exact_trace_assignments = {
        node.targets[0].id: ast.dump(node, include_attributes=False)
        for statement in (
            '''TRACE_PATHS = (
    ".gitattributes",
    "pyproject.toml",
    "burnlens/inspect_petes_lake_reference_native_contract.py",
    "burnlens/petes_lake_reference_native_contract.py",
    "tests/test_petes_lake_reference_native_contract.py",
)''',
            'NATIVE_MODULE_PATH = "burnlens/petes_lake_reference_native_contract.py"',
            'NATIVE_CLI_PATH = "burnlens/inspect_petes_lake_reference_native_contract.py"',
            'NATIVE_TEST_PATH = "tests/test_petes_lake_reference_native_contract.py"',
            '''IMMUTABLE_TRACE_PATHS = (
    NATIVE_CLI_PATH,
    NATIVE_TEST_PATH,
)''',
            '''TRACE_ATTRIBUTE_PATHS = (
    NATIVE_MODULE_PATH,
    NATIVE_CLI_PATH,
    NATIVE_TEST_PATH,
)''',
            'TRACE_SCRIPT_NAME = "burnlens-inspect-petes-lake-reference-native-contract"',
            'TRACE_SCRIPT_TARGET = "burnlens.inspect_petes_lake_reference_native_contract:main"',
            'SUPPORTED_REPLAY_BRANCHES = (MILESTONE_BRANCH, "main")',
        )
        for node in [ast.parse(statement).body[0]]
        if isinstance(node, ast.Assign)
        and len(node.targets) == 1
        and isinstance(node.targets[0], ast.Name)
    }
    trace_functions = {
        "_git",
        "_git_bytes",
        "_scientific_source_fingerprint",
        "_project_script_target",
        "_attribute_map",
        "_validate_checkout_attributes",
        "validate_repository_trace",
    }
    trace_function_counts: dict[str, int] = {}
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.name not in trace_functions:
            continue
        trace_function_counts[node.name] = trace_function_counts.get(node.name, 0) + 1
        defaults = list(node.args.defaults) + [
            default for default in node.args.kw_defaults if default is not None
        ]
        if node.decorator_list or any(
            not isinstance(default, ast.Constant) for default in defaults
        ):
            raise PetesLakeReferenceNativeContractError(
                f"{label} trace-function definition is unsafe"
            )
    historical_trace_functions = {"_git": 1, "validate_repository_trace": 1}
    current_trace_functions = {name: 1 for name in trace_functions}
    if trace_function_counts not in (
        historical_trace_functions,
        current_trace_functions,
    ):
        raise PetesLakeReferenceNativeContractError(
            f"{label} trace-function roster drifted"
        )
    retained: list[ast.stmt] = []
    for node in tree.body:
        node_dump = ast.dump(node, include_attributes=False)
        if isinstance(node, ast.Import) and node_dump in exact_trace_imports:
            continue
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in trace_functions:
            continue
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and exact_trace_assignments.get(node.targets[0].id) == node_dump
        ):
            continue
        retained.append(node)
    normalized = ast.dump(
        ast.Module(body=retained, type_ignores=[]),
        annotate_fields=True,
        include_attributes=False,
    ).encode("utf-8")
    return sha256(normalized).hexdigest()


def _project_script_target(source: str, label: str) -> str:
    try:
        document = tomllib.loads(source)
        target = document["project"]["scripts"][TRACE_SCRIPT_NAME]
    except (KeyError, TypeError, tomllib.TOMLDecodeError) as error:
        raise PetesLakeReferenceNativeContractError(
            f"{label} U04 console mapping is missing or invalid"
        ) from error
    if target != TRACE_SCRIPT_TARGET:
        raise PetesLakeReferenceNativeContractError(
            f"{label} U04 console mapping drifted"
        )
    return target


def _attribute_map(output: str, label: str) -> dict[tuple[str, str], str]:
    values: dict[tuple[str, str], str] = {}
    for line in output.splitlines():
        fields = line.split(": ", 2)
        if len(fields) != 3:
            raise PetesLakeReferenceNativeContractError(
                f"{label} U04 checkout attributes could not be parsed"
            )
        path, attribute, value = fields
        key = (path, attribute)
        if key in values:
            raise PetesLakeReferenceNativeContractError(
                f"{label} U04 checkout attributes contain duplicates"
            )
        values[key] = value
    expected = {
        (path, attribute)
        for path in TRACE_ATTRIBUTE_PATHS
        for attribute in ("text", "eol")
    }
    if set(values) != expected:
        raise PetesLakeReferenceNativeContractError(
            f"{label} U04 checkout attributes are incomplete"
        )
    return values


def _validate_checkout_attributes(
    repository_root: Path,
    git_source_commit: str,
    current_head: str,
) -> None:
    try:
        historical = _git(
            repository_root,
            "-c",
            f"core.attributesFile={os.devnull}",
            "check-attr",
            f"--source={git_source_commit}",
            "text",
            "eol",
            "--",
            *TRACE_ATTRIBUTE_PATHS,
        )
        current = _git(
            repository_root,
            "-c",
            f"core.attributesFile={os.devnull}",
            "check-attr",
            f"--source={current_head}",
            "text",
            "eol",
            "--",
            *TRACE_ATTRIBUTE_PATHS,
        )
    except (OSError, UnicodeError, subprocess.SubprocessError) as error:
        raise PetesLakeReferenceNativeContractError(
            "U04 checkout attributes could not be verified"
        ) from error
    for label, result in (("historical", historical), ("current", current)):
        values = _attribute_map(result.stdout, label)
        for path in TRACE_ATTRIBUTE_PATHS:
            if values.get((path, "text")) != "set" or values.get((path, "eol")) != "lf":
                raise PetesLakeReferenceNativeContractError(
                    f"{label} U04 checkout attributes drifted"
                )


def validate_repository_trace(repository_root: Path, git_source_commit: str) -> None:
    try:
        top = _git(repository_root, "rev-parse", "--show-toplevel").stdout.strip()
        branch = _git(repository_root, "branch", "--show-current").stdout.strip()
        head = _git(repository_root, "rev-parse", "HEAD").stdout.strip()
        status = _git(
            repository_root,
            "status",
            "--porcelain=v1",
            "--untracked-files=all",
        ).stdout.strip()
        if branch not in SUPPORTED_REPLAY_BRANCHES:
            raise PetesLakeReferenceNativeContractError(
                "native-contract replay branch identity drifted"
            )
        remote = _git(
            repository_root,
            "-c",
            "credential.interactive=never",
            "ls-remote",
            "--heads",
            "origin",
            branch,
        ).stdout.split()
        info_attributes_value = _git(
            repository_root,
            "rev-parse",
            "--git-path",
            "info/attributes",
        ).stdout.strip()
        info_attributes = Path(info_attributes_value)
        if not info_attributes.is_absolute():
            info_attributes = repository_root / info_attributes
        if info_attributes.is_file() and any(
            line.strip() and not line.lstrip().startswith("#")
            for line in info_attributes.read_text(encoding="utf-8").splitlines()
        ):
            raise PetesLakeReferenceNativeContractError(
                "repository-local attribute overrides are not permitted"
            )
        _git(repository_root, "cat-file", "-e", f"{git_source_commit}^{{commit}}")
        ancestor = _git(
            repository_root,
            "merge-base",
            "--is-ancestor",
            git_source_commit,
            head,
            check=False,
        )
        source_diff = _git(
            repository_root,
            "diff",
            "--quiet",
            git_source_commit,
            "--",
            *IMMUTABLE_TRACE_PATHS,
            check=False,
        )
        historical_module = _git(
            repository_root,
            "show",
            f"{git_source_commit}:{NATIVE_MODULE_PATH}",
        ).stdout
        historical_cli = _git_bytes(
            repository_root,
            "show",
            f"{git_source_commit}:{NATIVE_CLI_PATH}",
        ).stdout
        historical_test = _git_bytes(
            repository_root,
            "show",
            f"{git_source_commit}:{NATIVE_TEST_PATH}",
        ).stdout
        historical_pyproject = _git(
            repository_root,
            "show",
            f"{git_source_commit}:pyproject.toml",
        ).stdout
        head_module = _git_bytes(
            repository_root,
            "show",
            f"{head}:{NATIVE_MODULE_PATH}",
        ).stdout
        head_pyproject = _git_bytes(
            repository_root,
            "show",
            f"{head}:pyproject.toml",
        ).stdout
        current_module_path = repository_root / NATIVE_MODULE_PATH
        current_cli_path = repository_root / NATIVE_CLI_PATH
        current_test_path = repository_root / NATIVE_TEST_PATH
        current_module_bytes = current_module_path.read_bytes()
        current_cli = current_cli_path.read_bytes()
        current_test = current_test_path.read_bytes()
        current_pyproject_bytes = (repository_root / "pyproject.toml").read_bytes()
        current_module = head_module.decode("utf-8")
        current_pyproject = head_pyproject.decode("utf-8")
    except (OSError, UnicodeError, subprocess.SubprocessError) as error:
        raise PetesLakeReferenceNativeContractError(
            "repository trace could not be verified"
        ) from error
    if Path(top).resolve() != repository_root.resolve():
        raise PetesLakeReferenceNativeContractError("repository root identity drifted")
    if status:
        raise PetesLakeReferenceNativeContractError("repository worktree is not clean")
    if remote != [head, f"refs/heads/{branch}"]:
        raise PetesLakeReferenceNativeContractError("replay branch is not remote-equal")
    if ancestor.returncode != 0:
        raise PetesLakeReferenceNativeContractError("git source commit is not an ancestor of HEAD")
    if source_diff.returncode != 0:
        raise PetesLakeReferenceNativeContractError(
            "native-contract source bytes differ from the trace commit"
        )
    if current_cli != historical_cli:
        raise PetesLakeReferenceNativeContractError(
            "native-contract CLI checkout bytes differ from the trace commit"
        )
    if current_test != historical_test:
        raise PetesLakeReferenceNativeContractError(
            "native-contract test checkout bytes differ from the trace commit"
        )
    if current_module_bytes != head_module:
        raise PetesLakeReferenceNativeContractError(
            "native-contract module checkout bytes differ from HEAD"
        )
    if current_pyproject_bytes != head_pyproject:
        raise PetesLakeReferenceNativeContractError(
            "pyproject checkout bytes differ from HEAD"
        )
    try:
        executing_module = Path(__file__).read_bytes()
        executing_cli = Path(__file__).with_name(Path(NATIVE_CLI_PATH).name).read_bytes()
    except OSError as error:
        raise PetesLakeReferenceNativeContractError(
            "executing native-contract package could not be verified"
        ) from error
    if executing_module != current_module_bytes:
        raise PetesLakeReferenceNativeContractError(
            "executing native-contract module differs from repository source"
        )
    if executing_cli != historical_cli:
        raise PetesLakeReferenceNativeContractError(
            "executing native-contract CLI differs from the trace commit"
        )
    if _scientific_source_fingerprint(
        historical_module, "historical"
    ) != _scientific_source_fingerprint(current_module, "current"):
        raise PetesLakeReferenceNativeContractError(
            "native-contract scientific source drifted"
        )
    _project_script_target(historical_pyproject, "historical")
    _project_script_target(current_pyproject, "current")
    _validate_checkout_attributes(repository_root, git_source_commit, head)
    try:
        final_head = _git(repository_root, "rev-parse", "HEAD").stdout.strip()
        final_branch = _git(repository_root, "branch", "--show-current").stdout.strip()
        final_status = _git(
            repository_root,
            "status",
            "--porcelain=v1",
            "--untracked-files=all",
        ).stdout.strip()
        final_remote = _git(
            repository_root,
            "-c",
            "credential.interactive=never",
            "ls-remote",
            "--heads",
            "origin",
            branch,
        ).stdout.split()
    except (OSError, subprocess.SubprocessError) as error:
        raise PetesLakeReferenceNativeContractError(
            "repository trace could not be reverified"
        ) from error
    if (
        final_head != head
        or final_branch != branch
        or final_status
        or final_remote != [head, f"refs/heads/{branch}"]
    ):
        raise PetesLakeReferenceNativeContractError(
            "repository trace state changed during verification"
        )


def _digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def _file_digest(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as source:
        while block := source.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def _metadata_text(root: ET.Element, tag: str) -> str:
    matches: list[str] = []
    for item in root.iter():
        if item.tag.split("}")[-1].casefold() == tag.casefold():
            value = " ".join("".join(item.itertext()).split())
            if value:
                matches.append(value)
    if len(matches) != 1:
        raise PetesLakeReferenceNativeContractError(
            f"expected one {tag} metadata value; found {len(matches)}"
        )
    return matches[0]


def _assert_exact_roster(names: list[str]) -> None:
    expected = set(DIRECTORIES) | set(EXPECTED_MEMBERS.values())
    observed = set(names)
    if len(names) != len(observed):
        raise PetesLakeReferenceNativeContractError("archive contains duplicate exact member names")
    if observed != expected:
        missing = sorted(expected - observed)
        extra = sorted(observed - expected)
        raise PetesLakeReferenceNativeContractError(
            f"exact MTBS member roster drifted; missing={missing}; extra={extra}"
        )


def _inspect_notices(archive: ZipFile) -> dict[str, Any]:
    try:
        fgdc_data = archive.read(EXPECTED_MEMBERS["fgdc_metadata"])
        iso_data = archive.read(EXPECTED_MEMBERS["iso_metadata"])
        fgdc = ET.fromstring(fgdc_data)
        iso = ET.fromstring(iso_data)
    except (KeyError, ET.ParseError) as error:
        raise PetesLakeReferenceNativeContractError("delivered metadata notices are unreadable") from error
    fgdc_text = " ".join(" ".join(fgdc.itertext()).split())
    iso_text = " ".join(" ".join(iso.itertext()).split())
    access = _metadata_text(fgdc, "accconst")
    use = _metadata_text(fgdc, "useconst")
    credit = _metadata_text(fgdc, "datacred")
    liability = _metadata_text(fgdc, "distliab")
    warning = "Fire severity could be misrepresented in wetland areas."
    if access != "None":
        raise PetesLakeReferenceNativeContractError("delivered MTBS access constraints drifted")
    if use != (
        "There are no restrictions on use, except for reasonable and proper "
        "acknowledgement of information sources."
    ):
        raise PetesLakeReferenceNativeContractError("delivered MTBS use constraints drifted")
    if credit != "Monitoring Trends in Burn Severity Project (U.S. Geological Survey and USDA Forest Service)":
        raise PetesLakeReferenceNativeContractError("delivered MTBS credit drifted")
    if "no warranty expressed or implied" not in liability:
        raise PetesLakeReferenceNativeContractError("delivered MTBS liability language drifted")
    if warning not in fgdc_text or warning not in iso_text:
        raise PetesLakeReferenceNativeContractError("delivered wetland warning is absent")
    required_iso = (
        "reasonable and proper acknowledgement",
        "make no expressed or implied warranty",
        "reserve the right to correct, update, modify, or replace",
        EVENT_ID,
    )
    if any(value not in iso_text for value in required_iso):
        raise PetesLakeReferenceNativeContractError("delivered ISO terms or identity drifted")
    return {
        "gate": "PASS_EXACT_DELIVERED_NOTICES_BEFORE_NATIVE_PIXEL_OPEN",
        "notice_candidates": [
            {
                "role": "fgdc_metadata",
                "member": EXPECTED_MEMBERS["fgdc_metadata"],
                "bytes": len(fgdc_data),
                "sha256": _digest(fgdc_data),
                "xml_root": fgdc.tag.split("}")[-1],
            },
            {
                "role": "iso_metadata",
                "member": EXPECTED_MEMBERS["iso_metadata"],
                "bytes": len(iso_data),
                "sha256": _digest(iso_data),
                "xml_root": iso.tag.split("}")[-1],
            },
        ],
        "access_constraints": access,
        "use_constraints": use,
        "credit": credit,
        "distribution_liability": liability,
        "wetland_warning": warning,
        "revision_without_notice_warning_present": True,
        "archive_specific_conflict_found": False,
        "unresolved_third_party_term_found": False,
        "intended_local_analysis_and_bounded_derived_evidence_permitted": True,
    }


def _dbf_records(data: bytes) -> list[dict[str, str]]:
    if len(data) < 33:
        raise PetesLakeReferenceNativeContractError("truncated DBF header")
    record_count = struct.unpack("<I", data[4:8])[0]
    header_bytes = struct.unpack("<H", data[8:10])[0]
    record_bytes = struct.unpack("<H", data[10:12])[0]
    fields: list[tuple[str, int]] = []
    position = 32
    while position < header_bytes and data[position] != 13:
        descriptor = data[position:position + 32]
        if len(descriptor) != 32:
            raise PetesLakeReferenceNativeContractError("truncated DBF field descriptor")
        name = descriptor[:11].split(b"\0", 1)[0].decode("ascii", "strict")
        fields.append((name, descriptor[16]))
        position += 32
    rows: list[dict[str, str]] = []
    for index in range(record_count):
        start = header_bytes + index * record_bytes
        record = data[start:start + record_bytes]
        if len(record) != record_bytes:
            raise PetesLakeReferenceNativeContractError("truncated DBF record")
        if record[:1] == b"*":
            continue
        offset = 1
        row: dict[str, str] = {}
        for name, width in fields:
            row[name] = record[offset:offset + width].decode("cp1252", "replace").strip()
            offset += width
        rows.append(row)
    return rows


def _shapefile_contract(data: bytes) -> dict[str, Any]:
    if len(data) < 100 or struct.unpack(">i", data[:4])[0] != 9994:
        raise PetesLakeReferenceNativeContractError("invalid shapefile header")
    if struct.unpack("<i", data[32:36])[0] != 5:
        raise PetesLakeReferenceNativeContractError("reference vector is not polygon geometry")
    position = 100
    count = 0
    shape_types: set[int] = set()
    while position < len(data):
        if position + 8 > len(data):
            raise PetesLakeReferenceNativeContractError("truncated shapefile record header")
        length = struct.unpack(">i", data[position + 4:position + 8])[0] * 2
        record = data[position + 8:position + 8 + length]
        if len(record) < 4:
            raise PetesLakeReferenceNativeContractError("truncated shapefile record")
        shape_types.add(struct.unpack("<i", record[:4])[0])
        position += 8 + length
        count += 1
    if position != len(data) or shape_types - {0, 5} or count != 1:
        raise PetesLakeReferenceNativeContractError("reference vector record contract drifted")
    return {
        "shape_type": 5,
        "record_count": count,
        "bbox": [round(value, 9) for value in struct.unpack("<4d", data[36:68])],
    }


def _inspect_vectors(archive: ZipFile) -> dict[str, Any]:
    result: dict[str, Any] = {}
    records: dict[str, dict[str, str]] = {}
    for role in ("burn_area", "mask_area"):
        parts: dict[str, Any] = {}
        for extension in ("shp", "shx", "dbf", "prj"):
            key = f"{role}_{extension}"
            data = archive.read(EXPECTED_MEMBERS[key])
            part: dict[str, Any] = {
                "member": EXPECTED_MEMBERS[key],
                "bytes": len(data),
                "sha256": _digest(data),
            }
            if extension == "shp":
                part.update(_shapefile_contract(data))
            elif extension == "shx":
                if len(data) != 108 or struct.unpack(">i", data[:4])[0] != 9994:
                    raise PetesLakeReferenceNativeContractError("shapefile index contract drifted")
            elif extension == "dbf":
                rows = _dbf_records(data)
                if len(rows) != 1:
                    raise PetesLakeReferenceNativeContractError("expected one DBF record")
                records[role] = rows[0]
                part["record_count"] = 1
            elif extension == "prj":
                try:
                    crs = CRS.from_wkt(data.decode("ascii", "strict"))
                except (UnicodeDecodeError, rasterio.errors.CRSError) as error:
                    raise PetesLakeReferenceNativeContractError("reference vector CRS is unreadable") from error
                if crs.to_epsg() != 32610:
                    raise PetesLakeReferenceNativeContractError("reference vector CRS drifted")
                part["crs"] = "EPSG:32610"
            parts[extension] = part
        result[role] = {"parts": parts, "attributes": records[role]}

    burn_expected = {
        "EVENT_ID": EVENT_ID,
        "INCID_NAME": "PETES LAKE",
        "INCID_TYPE": "Wildfire",
        "MAP_ID": str(MAP_ID),
        "MAP_PROG": "MTBS",
        "ASMNT_TYPE": "Extended",
        "BURNBNDAC": "3372",
        "IG_DATE": "20230825",
        "PRE_ID": "904502920230801",
        "POST_ID": "804502920240811",
        "DNBR_OFFST": "14",
        "DNBR_STDDV": "16",
        "NODATA_T": "-970",
        "INCGREEN_T": "-150",
        "LOW_T": "70",
        "MOD_T": "330",
        "HIGH_T": "570",
        "COMMENT": "Fire severity could be misrepresented in wetland areas.",
    }
    if any(records["burn_area"].get(key) != value for key, value in burn_expected.items()):
        raise PetesLakeReferenceNativeContractError("burn-area DBF identity or caution drifted")
    mask_expected = {
        "EVENT_ID": EVENT_ID,
        "INCID_NAME": "PETES LAKE",
        "MAP_ID": str(MAP_ID),
    }
    if any(records["mask_area"].get(key) != value for key, value in mask_expected.items()):
        raise PetesLakeReferenceNativeContractError("non-processing mask DBF identity drifted")
    burn_bbox = result["burn_area"]["parts"]["shp"]["bbox"]
    mask_bbox = result["mask_area"]["parts"]["shp"]["bbox"]
    if not (
        burn_bbox[0] <= mask_bbox[0] <= mask_bbox[2] <= burn_bbox[2]
        and burn_bbox[1] <= mask_bbox[1] <= mask_bbox[3] <= burn_bbox[3]
    ):
        raise PetesLakeReferenceNativeContractError("non-processing mask bbox exceeds burn-area bbox")
    result["threshold_reconciliation"] = {
        "wfs_raw_fields": {"mod_t": 570, "high_t": 330},
        "delivered_dbf_semantic_fields": {"MOD_T": 330, "HIGH_T": 570},
        "silent_normalization": False,
        "disposition": "PRESERVE_DISTINCT_RAW_SOURCE_FIELDS_AND_USE_DELIVERED_DBF_NAMES_ONLY",
    }
    return result


def _inspect_raster(archive: ZipFile, role: str) -> dict[str, Any]:
    member = EXPECTED_MEMBERS[role]
    data = archive.read(member)
    try:
        with MemoryFile(data) as memory, memory.open() as source:
            stack = source.read()
            band_summaries = []
            for index, band in enumerate(stack):
                nodata = source.nodatavals[index]
                valid = np.isfinite(band)
                if nodata is not None:
                    valid &= band != nodata
                values = band[valid]
                encoded, counts = np.unique(band[np.isfinite(band)], return_counts=True)
                band_summaries.append(
                    {
                        "band": index + 1,
                        "valid_pixels": int(values.size),
                        "nodata_pixels": int(band.size - values.size),
                        "valid_min": float(values.min()) if values.size else None,
                        "valid_max": float(values.max()) if values.size else None,
                        "encoded_unique_count": int(encoded.size),
                        "native_value_domain": (
                            {
                                str(int(value)): int(count)
                                for value, count in zip(encoded, counts, strict=True)
                            }
                            if encoded.size <= 32
                            else None
                        ),
                        "valid_quantiles": (
                            {
                                name: round(float(value), 4)
                                for name, value in zip(
                                    ("min", "p01", "p10", "p50", "p90", "p99", "max"),
                                    np.percentile(values, (0, 1, 10, 50, 90, 99, 100)),
                                    strict=True,
                                )
                            }
                            if values.size and encoded.size > 32
                            else None
                        ),
                    }
                )
            profile = {
                "role": role,
                "member": member,
                "bytes": len(data),
                "sha256": _digest(data),
                "driver": source.driver,
                "width": source.width,
                "height": source.height,
                "band_count": source.count,
                "dtypes": list(source.dtypes),
                "crs": source.crs.to_string() if source.crs else None,
                "resolution_m": [abs(source.transform.a), abs(source.transform.e)],
                "transform": list(source.transform)[:6],
                "bounds": list(source.bounds),
                "nodata_values": list(source.nodatavals),
                "mask_flags": [
                    [flag.name for flag in flags] for flags in source.mask_flag_enums
                ],
                "all_bands_read": True,
                "band_summaries": band_summaries,
            }
    except rasterio.errors.RasterioError as error:
        raise PetesLakeReferenceNativeContractError(f"unreadable native reference raster: {role}") from error
    _validate_raster_profile(role, profile)
    return profile


def _validate_raster_profile(role: str, profile: dict[str, Any]) -> None:
    if (
        profile["driver"] != "GTiff"
        or profile["width"] != 434
        or profile["height"] != 374
        or profile["crs"] != "EPSG:32610"
        or profile["resolution_m"] != [30.0, 30.0]
        or profile["transform"] != EXPECTED_RASTER_TRANSFORM
        or profile["bounds"] != EXPECTED_RASTER_BOUNDS
        or any(flags != ["nodata"] for flags in profile["mask_flags"])
    ):
        raise PetesLakeReferenceNativeContractError(f"native reference grid drifted: {role}")
    if role in ("pre_reflectance", "post_reflectance"):
        if (
            profile["band_count"] != 6
            or profile["dtypes"] != ["uint16"] * 6
            or profile["nodata_values"] != [0.0] * 6
        ):
            raise PetesLakeReferenceNativeContractError(f"reflectance band contract drifted: {role}")
    elif role in ("dnbr", "rdnbr"):
        if (
            profile["band_count"] != 1
            or profile["dtypes"] != ["int16"]
            or profile["nodata_values"] != [-32768.0]
        ):
            raise PetesLakeReferenceNativeContractError(f"continuous severity contract drifted: {role}")
    elif role == "dnbr6":
        domain = set(profile["band_summaries"][0]["native_value_domain"] or {})
        if (
            profile["band_count"] != 1
            or profile["dtypes"] != ["uint8"]
            or profile["nodata_values"] != [0.0]
            or domain != {"0", "1", "2", "3", "4", "6"}
        ):
            raise PetesLakeReferenceNativeContractError("six-class severity domain drifted")


def _inspect_media(archive: ZipFile) -> dict[str, Any]:
    pdf = archive.read(EXPECTED_MEMBERS["pdf"])
    if not pdf.startswith(b"%PDF-"):
        raise PetesLakeReferenceNativeContractError("delivered PDF magic mismatch")
    kmz = archive.read(EXPECTED_MEMBERS["kmz"])
    try:
        with ZipFile(BytesIO(kmz)) as package:
            infos = package.infolist()
            names = [item.filename for item in infos]
            if (
                not infos
                or len(infos) > 5_000
                or any(PurePosixPath(name).is_absolute() or ".." in PurePosixPath(name).parts or "\\" in name for name in names)
                or len({name.casefold() for name in names}) != len(names)
                or any(item.flag_bits & 0x1 for item in infos)
                or any(((item.external_attr >> 16) & 0o170000) == 0o120000 for item in infos)
                or any(PurePosixPath(name).suffix.casefold() not in {".kml", ".png"} for name in names)
                or sum(item.file_size for item in infos) > 64 * 1024 * 1024
                or sum(item.file_size for item in infos) > max(len(kmz), 1) * 100
                or package.testzip() is not None
            ):
                raise PetesLakeReferenceNativeContractError("delivered KMZ structure is unsafe")
            uncompressed_bytes = sum(item.file_size for item in infos)
            if (
                len(infos) != EXPECTED_KMZ_MEMBERS
                or uncompressed_bytes != EXPECTED_KMZ_UNCOMPRESSED_BYTES
            ):
                raise PetesLakeReferenceNativeContractError("delivered KMZ identity drifted")
            event_kml = [name for name in names if name.casefold() == f"{EVENT_ID.casefold()}.kml"]
            if len(event_kml) != 1:
                raise PetesLakeReferenceNativeContractError("delivered KMZ event identity drifted")
            kmz_contract = {
                "member_count": len(infos),
                "uncompressed_bytes": uncompressed_bytes,
                "event_kml": event_kml[0],
                "suffixes": sorted({PurePosixPath(name).suffix.casefold() for name in names}),
                "safe_structure": True,
                "crc_pass": True,
            }
    except BadZipFile as error:
        raise PetesLakeReferenceNativeContractError("delivered KMZ is unreadable") from error
    return {
        "pdf": {
            "member": EXPECTED_MEMBERS["pdf"],
            "bytes": len(pdf),
            "sha256": _digest(pdf),
            "magic": "%PDF-",
        },
        "kmz": {
            "member": EXPECTED_MEMBERS["kmz"],
            "bytes": len(kmz),
            "sha256": _digest(kmz),
            **kmz_contract,
        },
    }


def inspect_native_archive(
    archive_path: Path,
    *,
    expected_archive_bytes: int = ARCHIVE_BYTES,
    expected_archive_sha256: str = ARCHIVE_SHA256,
) -> dict[str, Any]:
    if (
        not archive_path.is_file()
        or archive_path.stat().st_size != expected_archive_bytes
        or _file_digest(archive_path) != expected_archive_sha256
        or archive_path.stat().st_nlink != 1
    ):
        raise PetesLakeReferenceNativeContractError("exact reference archive custody mismatch")
    preflight = inspect_delivery([archive_path])
    if preflight["archives"][0]["member_count"] != ARCHIVE_MEMBERS:
        raise PetesLakeReferenceNativeContractError("exact reference archive member count mismatch")
    with ZipFile(archive_path) as archive:
        _assert_exact_roster(archive.namelist())
        notices = _inspect_notices(archive)
        # The notices gate above must pass before any vector, media, or raster is decoded.
        vectors = _inspect_vectors(archive)
        media = _inspect_media(archive)
        rasters = [
            _inspect_raster(archive, role)
            for role in ("pre_reflectance", "post_reflectance", "dnbr", "rdnbr", "dnbr6")
        ]
        signatures = {
            (
                item["width"],
                item["height"],
                tuple(item["transform"]),
                tuple(item["bounds"]),
                item["crs"],
                tuple(item["resolution_m"]),
            )
            for item in rasters
        }
        if len(signatures) != 1:
            raise PetesLakeReferenceNativeContractError("native MTBS raster grids differ")
        roles_by_member = {member: role for role, member in EXPECTED_MEMBERS.items()}
        manifest = []
        for member in sorted(archive.namelist()):
            data = archive.read(member)
            info = archive.getinfo(member)
            manifest.append(
                {
                    "role": roles_by_member.get(member, "directory"),
                    "member": member,
                    "is_directory": info.is_dir(),
                    "bytes": len(data),
                    "compressed_bytes": info.compress_size,
                    "crc32": f"{info.CRC:08x}",
                    "sha256": _digest(data),
                }
            )
    manifest_sha256 = _digest(
        json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )
    return {
        "archive": {
            **preflight["archives"][0],
            "exact_contract_pass": True,
            "single_link": True,
            "private_delivery_route_retained": False,
        },
        "root": ROOT,
        "directory_members": list(DIRECTORIES),
        "member_manifest": manifest,
        "member_manifest_sha256": manifest_sha256,
        "notice_and_terms_gate": notices,
        "notice_gate_completed_before_raster_open": True,
        "boundary_and_mask_vectors": vectors,
        "media": media,
        "native_rasters": rasters,
        "native_grid_groups": 1,
        "raster_resampling": "none",
        "raster_reprojection": "none",
        "class_semantics": MTBS_CLASS_SEMANTICS,
        "semantic_boundaries": {
            "continuous_dnbr_is_change_context_not_a_label_threshold": True,
            "continuous_rdnbr_is_change_context_not_a_label_threshold": True,
            "class_zero_is_not_affirmative_background": True,
            "class_one_is_ambiguous_not_affirmative_background": True,
            "classes_two_through_four_are_bounded_reference_evidence_not_label_truth": True,
            "class_six_and_mask_vector_are_excluded_nonprocessing_evidence": True,
            "accepted_reference_pixels": 0,
        },
    }


def build_report(
    *,
    repository_root: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, Any]:
    root = repository_root.resolve()
    if not (root / ".git").exists() or not (root / "pyproject.toml").is_file():
        raise PetesLakeReferenceNativeContractError(
            "repository root is not the canonical BurnLens checkout"
        )
    validate_trace_inputs(
        generated_at_utc=generated_at_utc,
        run_id=run_id,
        git_source_commit=git_source_commit,
    )
    validate_repository_trace(root, git_source_commit)
    archive = root / CUSTODY_PATHS["raw_package"] / "petes-lake-mtbs-reference-delivery-001.zip"
    custody_state = root / CUSTODY_PATHS["run_state"]
    request_receipt = root / CUSTODY_PATHS["request_directory"] / "request-receipt.json"
    for path, size, digest in (
        (custody_state, CUSTODY_STATE_BYTES, CUSTODY_STATE_SHA256),
        (request_receipt, REQUEST_RECEIPT_BYTES, REQUEST_RECEIPT_SHA256),
    ):
        if not path.is_file() or path.stat().st_size != size or _file_digest(path) != digest:
            raise PetesLakeReferenceNativeContractError("upstream request or custody state mismatch")
    custody = json.loads(custody_state.read_bytes())
    if (
        custody.get("run_id") != CUSTODY_RUN_ID
        or custody.get("state") != "PASS_EXACT_PETES_LAKE_MTBS_DELIVERY_CUSTODY"
        or custody.get("archive", {}).get("sha256") != ARCHIVE_SHA256
        or custody.get("terms_and_native_pixels") != "NOT_OPENED_PENDING_TERMS_FIRST_NATIVE_CONTRACT"
    ):
        raise PetesLakeReferenceNativeContractError("upstream custody semantics mismatch")
    native = inspect_native_archive(archive)
    return {
        "report_id": REPORT_ID,
        "report_version": REPORT_VERSION,
        "protocol_version": PROTOCOL_VERSION,
        "unit_id": "P2O4-T33-U04",
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": 521,
        "git_source_commit": git_source_commit,
        "software_version": SOFTWARE_VERSION,
        "application_version": None,
        "event": {
            "event_id": EVENT_ID,
            "event_name": "PETES LAKE",
            "event_group_id": "event-petes-lake-2023",
            "geography_group_id": "geo-mtbs-or4396912190120230825",
            "map_id": MAP_ID,
            "map_program": "MTBS",
        },
        "trace": {
            "request_run_id": REQUEST_RUN_ID,
            "request_receipt_bytes": REQUEST_RECEIPT_BYTES,
            "request_receipt_sha256": REQUEST_RECEIPT_SHA256,
            "custody_run_id": CUSTODY_RUN_ID,
            "custody_state_bytes": CUSTODY_STATE_BYTES,
            "custody_state_sha256": CUSTODY_STATE_SHA256,
            "source_record_id": "SOURCE-2026-029",
            "terms_review_id": "TERMS-2026-025",
            "upstream_optical_run_id": "BL-2026-07-21-petes-lake-replacement-source-fitness-r002",
            "upstream_optical_report_sha256": "1aa88c0021c610e492d2645e3f2c49a4afe96d9d907e2ee4481948a4c58f2ebd",
            "aoi_version": "multi-event-native-grids-v0.3.0",
            "target_version": "target-burn-scar-v0.2.0",
            "label_schema_version": "burn-scar-five-state-schema-v0.1.0",
            "prior_label_set_version": "owner-approved-prototype-region-labels-v0.3.0",
            "petes_lake_label_set_version": None,
            "dataset_version": None,
            "split_version": None,
            "baseline_version": None,
            "model_version": None,
        },
        "native_contract": native,
        "decision": {
            "code": "PASS_EXACT_PETES_LAKE_MTBS_NATIVE_REFERENCE_CONTRACT_FOR_U05",
            "disposition": "pass",
            "reference_role": "bounded_analyst_interpreted_revisable_official_reference_evidence",
            "wetland_warning_status": "UNRESOLVED_MEASUREMENT_REQUIRED_IN_U05",
            "accepted_reference_pixels": 0,
            "next_dependency": "P2O4-T33-U05_OFFICIAL_REFERENCE_FITNESS_AND_SOURCE_PRECEDENCE",
        },
        "claim_boundaries": {
            "official_or_operational_status": False,
            "field_validation_or_endorsement": False,
            "pixel_perfect_ground_truth": False,
            "candidate_or_owner_response_created": False,
            "prototype_label_created": False,
            "dataset_split_baseline_model_created": False,
        },
        "warning": (
            "Experimental BurnLens CV evidence. Not official wildfire information. "
            "Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. "
            "Official sources govern."
        ),
    }


def write_report(report: dict[str, Any], output_path: Path) -> None:
    if output_path.exists():
        raise PetesLakeReferenceNativeContractError("native-contract report exists; no overwrite allowed")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(report, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    temporary = output_path.with_name(f".{output_path.name}.tmp-{uuid4().hex}")
    try:
        with temporary.open("xb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        temporary.rename(output_path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
