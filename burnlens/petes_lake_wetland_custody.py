"""Controlled public-source custody for Petes Lake NWI context.

The exact U.S. Fish and Wildlife Service REST responses are retained in ignored
repository-local custody.  This module intentionally separates state changes so
the external intake-contract validator can run between transitions.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from functools import wraps
from hashlib import sha256
from html.parser import HTMLParser
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import socket
import ssl
import stat
import subprocess
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from .provider_acquisition import AcquisitionError, USER_AGENT, write_private_state


CONTROLLING_UNIT_ID = "P2O4-T33-U05"
R001_UNIT_ID = CONTROLLING_UNIT_ID
R001_RUN_ID = "BL-2026-07-21-petes-lake-nwi-context-r001"
R002_UNIT_ID = "P2O4-T33-U05R1"
R002_RUN_ID = "BL-2026-07-22-petes-lake-nwi-context-r002"
R002_SOURCE_COMMIT = "87a852c750fe7527bd018c32f630c8447e61fc47"
UNIT_ID = "P2O4-T33-U05R2"
INTAKE_ID = "petes-lake-nwi-context-2026-003"
RUN_ID = "BL-2026-07-22-petes-lake-nwi-context-r003"
ASSET_ID_PREFIX = "petes-lake-nwi-r003"
BRANCH = "codex/p2o4-t33-petes-lake-milestone"
CONTRACT_VERSION = "1.0"
SERVICE_HOST = "fwspublicservices.wim.usgs.gov"
SERVICE_ROOT = f"https://{SERVICE_HOST}/wetlandsmapservice/rest/services"
WETLAND_LAYER = f"{SERVICE_ROOT}/Wetlands/MapServer/0"
SOURCE_LAYER = f"{SERVICE_ROOT}/Data_Source/MapServer/0"
TERMS_REFERENCE = "https://www.fws.gov/page/wetlands-geodatabase-disclaimer"
LIMITATIONS_REFERENCE = (
    "https://www.fws.gov/page/wetlands-data-limitations-exclusions-and-precautions"
)
USER_CAUTION_REFERENCE = "https://www.fws.gov/page/wetlands-geodatabase-user-caution"
WEB_SERVICE_REFERENCE = (
    "https://www.fws.gov/program/national-wetlands-inventory/web-mapping-services"
)
DATA_DOWNLOAD_REFERENCE = (
    "https://www.fws.gov/program/national-wetlands-inventory/data-download"
)
AUTHORIZATION_REFERENCE = "PRECHECK-2026-055"
SOURCE_RECORD_REFERENCE = "SOURCE-2026-032"
TERMS_RECORD_REFERENCE = "TERMS-2026-028"
TERMINAL_RECORD_REFERENCE = "REGISTRY-2026-056"
TRACKED_GATE_RECORDS = (
    {
        "record_id": SOURCE_RECORD_REFERENCE,
        "path": Path("records/phase-two/sources/SOURCE-2026-032.md"),
        "bytes": 7_569,
        "sha256": "2f063e80ba1e0d049cd6230de26aa46cb86014bfc1e33aafac81823949fc21fb",
        "required_decision": "PASS_EXACT_USFWS_NWI_SOURCE_FOR_BOUNDED_PETES_LAKE_CONTEXT_QUERY_ONLY",
    },
    {
        "record_id": TERMS_RECORD_REFERENCE,
        "path": Path("records/phase-two/terms/TERMS-2026-028.md"),
        "bytes": 5_608,
        "sha256": "6a40f423720e1eb276cc3c192fededea16a4cf8992af025ad34dc3094dbaa104",
        "required_decision": "RESOLVED_FOR_EXACT_PETES_LAKE_NWI_BOUNDED_QUERY_IGNORED_LOCAL_CUSTODY_AND_ATTRIBUTED_DERIVED_EXCLUSION_CONTEXT_ONLY; RAW_PAYLOAD_REPUBLICATION_BLOCKED",
    },
    {
        "record_id": AUTHORIZATION_REFERENCE,
        "path": Path("records/phase-two/prechecks/PRECHECK-2026-055.md"),
        "bytes": 5_463,
        "sha256": "d37b113344242fdffd8b26061110ec6295d5c73d8790839c18c8748ebf592b5b",
        "required_decision": "AUTHORIZE_OFFLINE_OBSERVABILITY_REMEDIATION_AND_ONE_FINAL_DISJOINT_R003_INTAKE",
    },
    {
        "record_id": TERMINAL_RECORD_REFERENCE,
        "path": Path("records/phase-two/registry/REGISTRY-2026-056.md"),
        "bytes": 5_999,
        "sha256": "251aca22791ffeec2582d7698d151348a2d92ad23ecb10e103f66c6b4cc3afbf",
        "required_decision": "R002 is immutable and terminal",
    },
)
GRID_BOUNDS_UTM10N = (584_560, 4_866_340, 591_540, 4_871_520)
GRID_CRS = "EPSG:32610"
MAX_ACCEPTED_SOURCE_SCALE = 100_000
QUERY_CONTEXT_BUFFER_METERS = MAX_ACCEPTED_SOURCE_SCALE // 1_000
QUERY_BOUNDS_UTM10N = (
    GRID_BOUNDS_UTM10N[0] - QUERY_CONTEXT_BUFFER_METERS,
    GRID_BOUNDS_UTM10N[1] - QUERY_CONTEXT_BUFFER_METERS,
    GRID_BOUNDS_UTM10N[2] + QUERY_CONTEXT_BUFFER_METERS,
    GRID_BOUNDS_UTM10N[3] + QUERY_CONTEXT_BUFFER_METERS,
)
MAX_RESPONSE_BYTES = 32 * 1024 * 1024
MAX_TERMS_PAGE_BYTES = 2 * 1024 * 1024
MIN_FREE_BYTES = 128 * 1024 * 1024
ALLOWED_JSON_MEDIA_TYPES = {"application/json", "text/plain"}
ALLOWED_HTML_MEDIA_TYPES = {"text/html"}
_REPARSE_ATTRIBUTE = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
CONTRACT_PATH = Path(
    "downloads/phase-two/runs/P2O4-T33-U05R2/"
    "petes-lake-nwi-context-r003-intake.json"
)
STAGING_ROOT = Path(
    "downloads/phase-two/quarantine/P2O4-T33-U05R2/"
    "petes-lake-nwi-context-r003"
)
CUSTODY_ROOT = Path("downloads/phase-two/raw")
PACKAGE_DIRECTORY = Path("petes-lake-nwi-context-v0.1.0-r003")
MUTEX_PATH = Path(
    "downloads/phase-two/runs/P2O4-T33-U05R2/"
    ".petes-lake-nwi-context-r003.lock"
)
PLAN_PATH = Path(
    "downloads/phase-two/runs/P2O4-T33-U05R2/"
    "petes-lake-nwi-context-r003-plan.json"
)
DISPATCH_ROOT = Path("downloads/phase-two/runs/P2O4-T33-U05R2/dispatch")
TERMS_REFRESH_PATH = Path(
    "downloads/phase-two/runs/P2O4-T33-U05R2/"
    "petes-lake-nwi-context-r003-terms-refresh.json"
)
R001_EVIDENCE = (
    {
        "role": "terminal_contract",
        "path": Path(
            "downloads/phase-two/runs/P2O4-T33-U05/"
            "petes-lake-nwi-context-r001-intake.json"
        ),
        "bytes": 24_434,
        "sha256": "a809241052aa8a8ce7705bf2cf9553b3113c10981791dd3dd4a0c0a9c1df2b7b",
    },
    {
        "role": "immutable_plan",
        "path": Path(
            "downloads/phase-two/runs/P2O4-T33-U05/"
            "petes-lake-nwi-context-r001-plan.json"
        ),
        "bytes": 18_137,
        "sha256": "e11428002a64052c8e66e7de0967eca00c61b5f12229b9aac42fefec7dd44685",
    },
    {
        "role": "live_terms_receipt",
        "path": Path(
            "downloads/phase-two/runs/P2O4-T33-U05/"
            "petes-lake-nwi-context-r001-terms-refresh.json"
        ),
        "bytes": 5_352,
        "sha256": "dc8bcd0a39556395e90be28dab48c7d25edec182a50c3a7e4be0ed3d307eabcb",
    },
    {
        "role": "dispatch_receipt",
        "path": Path(
            "downloads/phase-two/runs/P2O4-T33-U05/dispatch/"
            "wetlands-layer-metadata-attempt-001.json"
        ),
        "bytes": 820,
        "sha256": "8a13dabf62e119500782e5333047c710cc0fed2eded0c8fb025e85b0484288b2",
    },
    {
        "role": "retained_response",
        "path": Path(
            "downloads/phase-two/quarantine/P2O4-T33-U05/"
            "petes-lake-nwi-context-r001/wetlands-layer-metadata.json.partial"
        ),
        "bytes": 21_276,
        "sha256": "975c06d4c44ecedf23d1d5930ac1316913234ed0fd5b3a76fc365d07db466459",
    },
)
R002_EVIDENCE = (
    {
        "role": "terminal_contract",
        "path": Path(
            "downloads/phase-two/runs/P2O4-T33-U05R1/"
            "petes-lake-nwi-context-r002-intake.json"
        ),
        "bytes": 79_265,
        "sha256": "37cd244ecba3e19db978505fb1dbecfc08ac68752a2e41352fbdad5f9ad6479a",
    },
    {
        "role": "immutable_plan",
        "path": Path(
            "downloads/phase-two/runs/P2O4-T33-U05R1/"
            "petes-lake-nwi-context-r002-plan.json"
        ),
        "bytes": 20_684,
        "sha256": "ea1a23462f7395a2d8c5bf64e672d557c3aa6120106bdd78c038a84683c98a62",
    },
    {
        "role": "live_terms_receipt",
        "path": Path(
            "downloads/phase-two/runs/P2O4-T33-U05R1/"
            "petes-lake-nwi-context-r002-terms-refresh.json"
        ),
        "bytes": 5_354,
        "sha256": "1cdbad419ccc9804cbbbeb1aa45466cb1fb882ae855ed3759cc91ced7ed48fbc",
    },
    {
        "role": "wetlands_layer_metadata_dispatch",
        "path": Path(
            "downloads/phase-two/runs/P2O4-T33-U05R1/dispatch/"
            "petes-lake-nwi-r002-wetlands-layer-metadata-attempt-001.json"
        ),
        "bytes": 862,
        "sha256": "c55e1c9f3d0fca9d04783558c4ca1afcc4a693b0f569da2576793d1814b2dffa",
    },
    {
        "role": "wetlands_pre_count_dispatch",
        "path": Path(
            "downloads/phase-two/runs/P2O4-T33-U05R1/dispatch/"
            "petes-lake-nwi-r002-wetlands-pre-count-attempt-001.json"
        ),
        "bytes": 908,
        "sha256": "9c7ffd000c9b9c3d9ab3fadeaaa2df56646031c04139155f8059b59f8d1edcb3",
    },
    {
        "role": "wetlands_pre_ids_dispatch",
        "path": Path(
            "downloads/phase-two/runs/P2O4-T33-U05R1/dispatch/"
            "petes-lake-nwi-r002-wetlands-pre-ids-attempt-001.json"
        ),
        "bytes": 902,
        "sha256": "a23d95354a53df4eb7cb174071f0596516cb6694f8d9406ae5ddc183de32d79e",
    },
    {
        "role": "wetlands_features_dispatch",
        "path": Path(
            "downloads/phase-two/runs/P2O4-T33-U05R1/dispatch/"
            "petes-lake-nwi-r002-wetlands-features-attempt-001.json"
        ),
        "bytes": 905,
        "sha256": "d286a7459a0e23f208b53df4e6ba21124d6f449d130bbd03b63a3eff75a072ad",
    },
    {
        "role": "wetlands_post_count_dispatch",
        "path": Path(
            "downloads/phase-two/runs/P2O4-T33-U05R1/dispatch/"
            "petes-lake-nwi-r002-wetlands-post-count-attempt-001.json"
        ),
        "bytes": 911,
        "sha256": "a7f7a0af621b9429053d32d5a7713fd8be99f31864b0c7a45206e447e6f73f57",
    },
    {
        "role": "wetlands_post_ids_dispatch",
        "path": Path(
            "downloads/phase-two/runs/P2O4-T33-U05R1/dispatch/"
            "petes-lake-nwi-r002-wetlands-post-ids-attempt-001.json"
        ),
        "bytes": 905,
        "sha256": "d8d2702e5d04f2a35004a43c754e2af9bc4b4908e54126e8ccbdc59de1336f17",
    },
    {
        "role": "source_layer_metadata_dispatch",
        "path": Path(
            "downloads/phase-two/runs/P2O4-T33-U05R1/dispatch/"
            "petes-lake-nwi-r002-source-layer-metadata-attempt-001.json"
        ),
        "bytes": 859,
        "sha256": "e3823948901a61a0e0448a5225136d66b077ef14a289db42e3c2e2d756b1e51f",
    },
    {
        "role": "source_pre_count_dispatch",
        "path": Path(
            "downloads/phase-two/runs/P2O4-T33-U05R1/dispatch/"
            "petes-lake-nwi-r002-source-pre-count-attempt-001.json"
        ),
        "bytes": 905,
        "sha256": "5a841bdb72f597d2a470eb88f6eb5425f8d580767a1e76ec936df9aefe9d2058",
    },
    {
        "role": "wetlands_layer_metadata_payload",
        "path": Path(
            "downloads/phase-two/raw/petes-lake-nwi-context-v0.1.0-r002/"
            "wetlands-layer-metadata.json"
        ),
        "bytes": 21_276,
        "sha256": "975c06d4c44ecedf23d1d5930ac1316913234ed0fd5b3a76fc365d07db466459",
    },
    {
        "role": "wetlands_pre_count_payload",
        "path": Path(
            "downloads/phase-two/raw/petes-lake-nwi-context-v0.1.0-r002/"
            "wetlands-pre-count.json"
        ),
        "bytes": 13,
        "sha256": "0aa3cb3ca1de6d4591eed691291545c02dfba8db948d9ec844d73e380d6c5b26",
    },
    {
        "role": "wetlands_pre_ids_payload",
        "path": Path(
            "downloads/phase-two/raw/petes-lake-nwi-context-v0.1.0-r002/"
            "wetlands-pre-ids.json"
        ),
        "bytes": 5_662,
        "sha256": "68741e7dafb1177ee471c5f21be33074aab98a7c157fea349f86fcfe343c20f3",
    },
    {
        "role": "wetlands_features_payload",
        "path": Path(
            "downloads/phase-two/raw/petes-lake-nwi-context-v0.1.0-r002/"
            "wetlands-features.json"
        ),
        "bytes": 4_689_626,
        "sha256": "10d7a283c666d0cd6916b1058cf380a049f2651fe47f84ef5b7c035e35316ef1",
    },
    {
        "role": "wetlands_post_count_payload",
        "path": Path(
            "downloads/phase-two/raw/petes-lake-nwi-context-v0.1.0-r002/"
            "wetlands-post-count.json"
        ),
        "bytes": 13,
        "sha256": "0aa3cb3ca1de6d4591eed691291545c02dfba8db948d9ec844d73e380d6c5b26",
    },
    {
        "role": "wetlands_post_ids_payload",
        "path": Path(
            "downloads/phase-two/raw/petes-lake-nwi-context-v0.1.0-r002/"
            "wetlands-post-ids.json"
        ),
        "bytes": 5_662,
        "sha256": "68741e7dafb1177ee471c5f21be33074aab98a7c157fea349f86fcfe343c20f3",
    },
    {
        "role": "source_layer_metadata_payload",
        "path": Path(
            "downloads/phase-two/raw/petes-lake-nwi-context-v0.1.0-r002/"
            "source-layer-metadata.json"
        ),
        "bytes": 11_229,
        "sha256": "de5dcacb9531a380ef4c29167031f928e48add79e0410020928e316d5f98cf12",
    },
    {
        "role": "source_pre_count_retained_partial",
        "path": Path(
            "downloads/phase-two/quarantine/P2O4-T33-U05R1/"
            "petes-lake-nwi-context-r002/source-pre-count.json.partial"
        ),
        "bytes": 0,
        "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    },
)

WETLAND_FIELDS = (
    "Wetlands.OBJECTID",
    "Wetlands.GLOBALID",
    "Wetlands.ATTRIBUTE",
    "Wetlands.WETLAND_TYPE",
    "Wetlands.ACRES",
    "Wetlands.Shape_Length",
    "Wetlands.Shape_Area",
)
SOURCE_FIELDS = (
    "OBJECTID",
    "PROJECT_NAME",
    "STATUS",
    "SUPPMAPINFO",
    "FGDC_METADATA",
    "DATA_SOURCE",
    "IMAGE_YR",
    "IMAGE_DATE",
    "IMAGE_SCALE",
    "ALL_SCALES",
    "EMULSION",
    "COMMENTS",
    "SOURCE_TYPE",
    "SHAPE_Length",
    "SHAPE_Area",
)
WETLAND_FIELD_TYPES = {
    "OBJECTID": "esriFieldTypeOID",
    "GLOBALID": "esriFieldTypeGlobalID",
    "ATTRIBUTE": "esriFieldTypeString",
    "WETLAND_TYPE": "esriFieldTypeString",
    "ACRES": "esriFieldTypeDouble",
    "Shape_Length": "esriFieldTypeDouble",
    "Shape_Area": "esriFieldTypeDouble",
}
SOURCE_FIELD_TYPES = {
    "OBJECTID": "esriFieldTypeOID",
    "PROJECT_NAME": "esriFieldTypeString",
    "STATUS": "esriFieldTypeString",
    "SUPPMAPINFO": "esriFieldTypeString",
    "FGDC_METADATA": "esriFieldTypeString",
    "DATA_SOURCE": "esriFieldTypeString",
    "IMAGE_YR": "esriFieldTypeSmallInteger",
    "IMAGE_DATE": "esriFieldTypeString",
    "IMAGE_SCALE": "esriFieldTypeInteger",
    "ALL_SCALES": "esriFieldTypeString",
    "EMULSION": "esriFieldTypeString",
    "COMMENTS": "esriFieldTypeString",
    "SOURCE_TYPE": "esriFieldTypeString",
    "SHAPE_Length": "esriFieldTypeDouble",
    "SHAPE_Area": "esriFieldTypeDouble",
}
SOURCE_TYPE_RENDERER_VALUES = {" ", "<Null>", "UNKNOWN", "BW", "CIR", "Scalable", "TC"}
METADATA_IDENTITIES = {
    "wetlands": {
        "bytes": 21_276,
        "sha256": "975c06d4c44ecedf23d1d5930ac1316913234ed0fd5b3a76fc365d07db466459",
    },
    "source": {
        "bytes": 11_229,
        "sha256": "de5dcacb9531a380ef4c29167031f928e48add79e0410020928e316d5f98cf12",
    },
}
OFFICIAL_TERMS_PAGES = (
    {
        "page_id": "wetlands-geodatabase-disclaimer",
        "uri": TERMS_REFERENCE,
        "semantic_fragments": (
            "wetlands geodatabase disclaimer",
            "may not be consistent with wetland boundaries established according to the federal regulatory definition of wetlands",
            "should not be interpreted as representing the presence, absence, or extent of wetlands",
            "federal, state, tribal, or local laws",
        ),
    },
    {
        "page_id": "wetlands-data-limitations",
        "uri": LIMITATIONS_REFERENCE,
        "semantic_fragments": (
            "data limitations",
            "the accuracy of image interpretation depends on the quality of the imagery",
            "wetlands or other mapped features may have changed since the date of the imagery and/or field work",
            "should not be interpreted as representing the presence, absence, or extent of wetlands",
            "federal, state, tribal, or local laws",
        ),
    },
    {
        "page_id": "wetlands-geodatabase-user-caution",
        "uri": USER_CAUTION_REFERENCE,
        "semantic_fragments": (
            "wetlands geodatabase user caution",
            "represents the extent, approximate location and type of wetlands and deepwater habitats",
            "1:24,000 or 1:25,000 scale",
            "neither designed nor intended to represent legal or regulatory products",
            "only effective as of the date of extraction or delivery",
            "to ensure you have the most up to date information",
            "federal, state, tribal, or local laws",
        ),
    },
    {
        "page_id": "wetland-web-mapping-services",
        "uri": WEB_SERVICE_REFERENCE,
        "semantic_fragments": (
            "web mapping services",
            "can be accessed by web-based applications and mapping software",
            "software developers can incorporate our rest services within their map applications",
        ),
    },
    {
        "page_id": "wetlands-data-download",
        "uri": DATA_DOWNLOAD_REFERENCE,
        "semantic_fragments": (
            "data download",
            "to display and query wetlands data in your software application please use our web map services",
        ),
    },
)
OFFICIAL_TERMS_SEMANTIC_PROPOSITIONS = (
    "NWI mapping is approximate and may be incomplete or stale",
    "NWI mapping is non-regulatory and is not a legal wetland delineation",
    "accuracy scale currency interpretation and jurisdiction limitations remain",
    "the anonymous official web service remains an application display and query route",
    "NWI does not imply field validation burn severity background truth endorsement or operational fitness",
)


class PetesLakeWetlandCustodyError(RuntimeError):
    """The exact NWI context transaction failed closed."""


class _NoRedirectHandler(HTTPRedirectHandler):
    """Refuse every HTTP redirect before urllib can follow it."""

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


class _VisibleTextCollector(HTMLParser):
    """Collect page text for stable semantic checks without retaining HTML."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._suppressed_depth = 0

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        del attrs
        if tag.casefold() in {"script", "style", "noscript", "svg"}:
            self._suppressed_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if (
            tag.casefold() in {"script", "style", "noscript", "svg"}
            and self._suppressed_depth
        ):
            self._suppressed_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self._suppressed_depth and data.strip():
            self.parts.append(data)


def _utc(value: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3,6})?Z", value
    ):
        raise PetesLakeWetlandCustodyError("timestamp must be an explicit UTC Z value")
    datetime.fromisoformat(value[:-1] + "+00:00")
    return value


def _utc_datetime(value: str) -> datetime:
    return datetime.fromisoformat(_utc(value)[:-1] + "+00:00")


def _now_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace(
        "+00:00", "Z"
    )


def _monotonic_timestamp(now_fn: Callable[[], str], after: datetime) -> tuple[str, datetime]:
    observed = _utc_datetime(_utc(now_fn()))
    if observed <= after:
        observed = after + timedelta(microseconds=1)
    value = observed.isoformat(timespec="microseconds").replace("+00:00", "Z")
    return value, observed


def _open_no_redirect(request: Request, *, timeout: int) -> Any:
    return build_opener(_NoRedirectHandler()).open(request, timeout=timeout)


def _provider_open_diagnostic(error: BaseException) -> dict[str, Any]:
    """Return a bounded diagnostic without serializing provider exception material."""

    if isinstance(error, HTTPError):
        status = error.code
        if isinstance(status, int) and not isinstance(status, bool) and 100 <= status <= 599:
            return {"category": "http", "http_status": status}
        return {"category": "unknown-open", "http_status": None}
    candidate: object = error.reason if isinstance(error, URLError) else error
    if isinstance(candidate, TimeoutError):
        category = "timeout"
    elif isinstance(candidate, socket.gaierror):
        category = "dns"
    elif isinstance(candidate, ssl.SSLError):
        category = "tls"
    elif isinstance(candidate, ConnectionError):
        category = "connection"
    else:
        category = "unknown-open"
    return {"category": category, "http_status": None}


def _normalized_html_text(data: bytes) -> str:
    try:
        source = data.decode("utf-8")
    except UnicodeDecodeError as error:
        raise PetesLakeWetlandCustodyError(
            "official terms page is not UTF-8 HTML"
        ) from error
    if "<html" not in source.casefold():
        raise PetesLakeWetlandCustodyError("official terms page lacks an HTML root")
    collector = _VisibleTextCollector()
    try:
        collector.feed(source)
        collector.close()
    except Exception as error:
        raise PetesLakeWetlandCustodyError(
            "official terms page HTML could not be parsed"
        ) from error
    return re.sub(r"\s+", " ", " ".join(collector.parts)).strip().casefold()


def _capture_official_terms_page(
    page: dict[str, Any],
    *,
    open_fn: Callable[..., Any],
) -> dict[str, Any]:
    request = Request(
        page["uri"],
        headers={"User-Agent": USER_AGENT, "Accept": "text/html"},
        method="GET",
    )
    with open_fn(request, timeout=60) as response:
        status = getattr(response, "status", None)
        if not isinstance(status, int) or isinstance(status, bool) or status != 200:
            raise PetesLakeWetlandCustodyError(
                "official terms page status is not exact HTTP 200"
            )
        geturl = getattr(response, "geturl", None)
        final_url = str(geturl()) if callable(geturl) else ""
        if final_url != page["uri"]:
            raise PetesLakeWetlandCustodyError(
                "official terms page redirected from its exact URL"
            )
        content_type = str(response.headers.get("Content-Type") or "")
        media_type = content_type.split(";", 1)[0].strip().casefold()
        if media_type not in ALLOWED_HTML_MEDIA_TYPES:
            raise PetesLakeWetlandCustodyError(
                "official terms page is not text/html"
            )
        length_raw = response.headers.get("Content-Length")
        try:
            content_length = int(length_raw) if length_raw else None
        except (TypeError, ValueError):
            raise PetesLakeWetlandCustodyError(
                "official terms page content length is invalid"
            ) from None
        if content_length is not None and not 0 < content_length <= MAX_TERMS_PAGE_BYTES:
            raise PetesLakeWetlandCustodyError(
                "official terms page content length is outside its bound"
            )
        chunks: list[bytes] = []
        total = 0
        while block := response.read(256 * 1024):
            if not isinstance(block, bytes):
                raise PetesLakeWetlandCustodyError(
                    "official terms response yielded non-byte content"
                )
            total += len(block)
            if total > MAX_TERMS_PAGE_BYTES:
                raise PetesLakeWetlandCustodyError(
                    "official terms page exceeds its bounded size"
                )
            chunks.append(block)
    data = b"".join(chunks)
    if not data or (content_length is not None and content_length != len(data)):
        raise PetesLakeWetlandCustodyError(
            "official terms page byte count is incomplete"
        )
    semantic_text = _normalized_html_text(data)
    missing = [
        fragment
        for fragment in page["semantic_fragments"]
        if fragment.casefold() not in semantic_text
    ]
    if missing:
        raise PetesLakeWetlandCustodyError(
            "official terms page failed stable semantic checks"
        )
    return {
        "page_id": page["page_id"],
        "requested_url": page["uri"],
        "final_url": final_url,
        "status": 200,
        "content_type": content_type,
        "content_length": content_length,
        "bytes": len(data),
        "sha256": _digest(data),
        "semantic_fragments": list(page["semantic_fragments"]),
    }


def _canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise PetesLakeWetlandCustodyError(
                f"JSON contains a duplicate object key: {key}"
            )
        value[key] = item
    return value


def _absolute_lexical_path(path: Path) -> Path:
    return Path(os.path.abspath(os.fspath(path)))


def _is_link_like(path: Path) -> bool:
    observed = path.lstat()
    return stat.S_ISLNK(observed.st_mode) or bool(
        getattr(observed, "st_file_attributes", 0) & _REPARSE_ATTRIBUTE
    )


def _assert_no_link_like_path_components(path: Path) -> None:
    lexical = _absolute_lexical_path(path)
    for component in (*reversed(lexical.parents), lexical):
        if os.path.lexists(component) and _is_link_like(component):
            raise PetesLakeWetlandCustodyError(
                "intake path contains a symbolic link or Windows reparse point"
            )


def _project_path(root: Path, relative: Path | PurePosixPath) -> Path:
    text = relative.as_posix()
    pieces = text.split("/")
    if (
        not text
        or text.startswith(("/", "//"))
        or ":" in text
        or "\\" in text
        or any(piece in {"", ".", ".."} for piece in pieces)
    ):
        raise PetesLakeWetlandCustodyError("intake path is not a safe relative path")
    lexical_root = _absolute_lexical_path(root)
    candidate = _absolute_lexical_path(lexical_root / Path(*pieces))
    try:
        candidate.relative_to(lexical_root)
    except ValueError:
        raise PetesLakeWetlandCustodyError(
            "intake path escapes the repository"
        ) from None
    _assert_no_link_like_path_components(candidate)
    return candidate


def _run_git(root: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *arguments],
        capture_output=True,
        text=True,
        check=False,
    )


def _is_exact_origin_url(value: str) -> bool:
    normalized = value.strip().casefold()
    return bool(
        re.fullmatch(
            r"(?:https://github\.com/drwbkr1/burnlens-deschutes(?:\.git)?/?|"
            r"git@github\.com:drwbkr1/burnlens-deschutes(?:\.git)?|"
            r"ssh://git@github\.com/drwbkr1/burnlens-deschutes(?:\.git)?/?)",
            normalized,
        )
    )


def _assert_ignored_untracked(root: Path, path: Path) -> None:
    try:
        relative = _absolute_lexical_path(path).relative_to(root).as_posix()
    except ValueError:
        raise PetesLakeWetlandCustodyError("private intake path escapes the repository") from None
    ignored = _run_git(root, "check-ignore", "--quiet", "--no-index", "--", relative)
    tracked = _run_git(root, "ls-files", "--error-unmatch", "--", relative)
    if ignored.returncode != 0 or tracked.returncode != 1:
        raise PetesLakeWetlandCustodyError(
            "private intake path is not both ignored and untracked"
        )


def _verify_tracked_gate_records(root: Path) -> None:
    for record in TRACKED_GATE_RECORDS:
        path = _project_path(root, record["path"])
        relative = path.relative_to(root).as_posix()
        tracked = _run_git(root, "ls-files", "--error-unmatch", "--", relative)
        if tracked.returncode != 0:
            raise PetesLakeWetlandCustodyError(
                f"tracked source gate record is not committed: {record['record_id']}"
            )
        if (
            not path.is_file()
            or path.is_symlink()
            or path.stat().st_nlink != 1
            or path.stat().st_size != record["bytes"]
            or _file_digest(path) != record["sha256"]
        ):
            raise PetesLakeWetlandCustodyError(
                f"tracked source gate record identity changed: {record['record_id']}"
            )
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as error:
            raise PetesLakeWetlandCustodyError(
                f"tracked source gate record is not UTF-8: {record['record_id']}"
            ) from error
        if record["required_decision"] not in content:
            raise PetesLakeWetlandCustodyError(
                f"tracked source gate decision is absent: {record['record_id']}"
            )


def _verify_locked_geometry_runtime() -> None:
    try:
        import shapely
    except ImportError as error:
        raise PetesLakeWetlandCustodyError(
            "geo-research environment is required before NWI authorization"
        ) from error
    if shapely.__version__ != "2.1.2":
        raise PetesLakeWetlandCustodyError(
            "NWI topology validation requires locked Shapely 2.1.2"
        )


def _git_context(root: Path) -> dict[str, str]:
    commands = {
        "top": ("rev-parse", "--show-toplevel"),
        "branch": ("branch", "--show-current"),
        "head": ("rev-parse", "HEAD"),
        "status": ("status", "--porcelain=v1", "--untracked-files=all"),
    }
    results = {name: _run_git(root, *arguments) for name, arguments in commands.items()}
    if any(result.returncode != 0 for result in results.values()):
        raise PetesLakeWetlandCustodyError("Git context verification failed")
    if _absolute_lexical_path(Path(results["top"].stdout.strip())) != root:
        raise PetesLakeWetlandCustodyError("Git top-level is not the supplied repository root")
    if results["status"].stdout.strip():
        raise PetesLakeWetlandCustodyError("tracked or untracked repository state is not clean")
    head = results["head"].stdout.strip()
    if not re.fullmatch(r"[0-9a-f]{40}", head):
        raise PetesLakeWetlandCustodyError("Git HEAD is not an exact lowercase SHA-1")
    return {
        "branch": results["branch"].stdout.strip(),
        "head": head,
    }


def _preflight_initialize(root: Path, git_source_commit: str) -> None:
    context = _git_context(root)
    if context != {"branch": BRANCH, "head": git_source_commit}:
        raise PetesLakeWetlandCustodyError(
            "initial Git branch or HEAD does not match the exact custody contract"
        )
    origin = _run_git(root, "config", "--get", "remote.origin.url")
    if origin.returncode != 0 or not _is_exact_origin_url(origin.stdout):
        raise PetesLakeWetlandCustodyError(
            "origin is not the exact drwbkr1/burnlens-deschutes repository"
        )
    remote = _run_git(
        root,
        "-c",
        "credential.interactive=never",
        "ls-remote",
        "--heads",
        "origin",
        BRANCH,
    )
    expected = f"{git_source_commit}\trefs/heads/{BRANCH}"
    if remote.returncode != 0 or remote.stdout.strip() != expected:
        raise PetesLakeWetlandCustodyError(
            "origin milestone branch is not exactly equal to the committed custody source"
        )


def _verify_retained_r001_evidence(root: Path) -> None:
    observed: dict[str, Path] = {}
    for evidence in R001_EVIDENCE:
        path = _project_path(root, evidence["path"])
        _assert_ignored_untracked(root, path)
        if (
            not path.is_file()
            or path.is_symlink()
            or path.stat().st_nlink != 1
            or path.stat().st_size != evidence["bytes"]
            or _file_digest(path) != evidence["sha256"]
        ):
            raise PetesLakeWetlandCustodyError(
                f"retained r001 remediation evidence changed: {evidence['role']}"
            )
        observed[evidence["role"]] = path
    try:
        prior = json.loads(
            observed["terminal_contract"].read_bytes(),
            object_pairs_hook=_reject_duplicate_keys,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise PetesLakeWetlandCustodyError(
            "retained r001 terminal contract is not valid JSON"
        ) from error
    extensions = prior.get("extensions", {})
    assets = prior.get("assets", [])
    if (
        extensions.get("unit_id") != R001_UNIT_ID
        or extensions.get("run_id") != R001_RUN_ID
        or not isinstance(assets, list)
        or len(assets) != 12
        or assets[0].get("asset_id") != "wetlands-layer-metadata"
        or assets[0].get("state") != "failed"
        or assets[0].get("failure", {}).get("code")
        != "NWI_TRANSFER_OR_STRUCTURE_FAILURE_NO_RETRY"
        or assets[0].get("failure", {}).get("stage") != "RESPONSE_STRUCTURE"
        or any(item.get("state") != "authorized" for item in assets[1:])
        or any(item.get("attempts") for item in assets[1:])
    ):
        raise PetesLakeWetlandCustodyError(
            "retained r001 terminal failure semantics changed"
        )


def _verify_retained_r002_evidence(root: Path) -> None:
    observed: dict[str, Path] = {}
    for evidence in R002_EVIDENCE:
        path = _project_path(root, evidence["path"])
        _assert_ignored_untracked(root, path)
        if (
            not path.is_file()
            or path.is_symlink()
            or path.stat().st_nlink != 1
            or path.stat().st_size != evidence["bytes"]
            or _file_digest(path) != evidence["sha256"]
        ):
            raise PetesLakeWetlandCustodyError(
                f"retained r002 remediation evidence changed: {evidence['role']}"
            )
        observed[evidence["role"]] = path
    try:
        prior = json.loads(
            observed["terminal_contract"].read_bytes(),
            object_pairs_hook=_reject_duplicate_keys,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise PetesLakeWetlandCustodyError(
            "retained r002 terminal contract is not valid JSON"
        ) from error
    extensions = prior.get("extensions", {})
    assets = prior.get("assets", [])
    expected_ids = [
        f"petes-lake-nwi-r002-{role}"
        for role in (
            "wetlands-layer-metadata",
            "wetlands-pre-count",
            "wetlands-pre-ids",
            "wetlands-features",
            "wetlands-post-count",
            "wetlands-post-ids",
            "source-layer-metadata",
            "source-pre-count",
            "source-pre-ids",
            "source-features",
            "source-post-count",
            "source-post-ids",
        )
    ]
    if (
        prior.get("intake_id") != "petes-lake-nwi-context-2026-002"
        or extensions.get("unit_id") != R002_UNIT_ID
        or extensions.get("run_id") != R002_RUN_ID
        or extensions.get("git_source_commit") != R002_SOURCE_COMMIT
        or extensions.get("state") is not None
        or extensions.get("terms_refresh", {}).get("state") != "passed"
        or not isinstance(assets, list)
        or len(assets) != 12
        or [item.get("asset_id") for item in assets] != expected_ids
        or any(item.get("state") != "promoted" for item in assets[:7])
        or any(
            len(item.get("attempts", [])) != 1
            or item["attempts"][0].get("outcome") != "succeeded"
            for item in assets[:7]
        )
        or assets[7].get("state") != "failed"
        or len(assets[7].get("attempts", [])) != 1
        or assets[7]["attempts"][0].get("outcome") != "failed"
        or assets[7].get("failure", {}).get("code")
        != "NWI_TRANSFER_OR_STRUCTURE_FAILURE_NO_RETRY"
        or assets[7].get("failure", {}).get("stage") != "PROVIDER_OPEN"
        or assets[7].get("failure", {}).get("retained_staging")
        != {
            "status": "exact",
            "size_bytes": 0,
            "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        }
        or any(item.get("state") != "authorized" for item in assets[8:])
        or any(item.get("attempts") for item in assets[8:])
    ):
        raise PetesLakeWetlandCustodyError(
            "retained r002 terminal failure semantics changed"
        )
    definitions = asset_definitions()
    for asset, definition in zip(assets, definitions, strict=True):
        prior_static = asset.get("extensions", {})
        source = asset.get("source", {})
        if (
            source.get("uri") != definition["uri"]
            or prior_static.get("logical_role") != definition["logical_role"]
            or prior_static.get("http_method") != definition["method"]
            or prior_static.get("request_body_sha256") != definition["body_sha256"]
            or prior_static.get("provider_geometry_crs")
            != ("EPSG:3857" if definition["format"] == "features" else None)
            or PurePosixPath(asset.get("destination_relative_path", "")).name
            != definition["filename"]
            or asset.get("staging_relative_path") != definition["filename"] + ".partial"
        ):
            raise PetesLakeWetlandCustodyError(
                f"r003 provider request drifted from retained r002: {definition['logical_role']}"
            )


def _verify_mutation_context(root: Path, contract: dict[str, Any]) -> None:
    context = _git_context(root)
    extensions = contract.get("extensions", {})
    if context != {
        "branch": extensions.get("branch"),
        "head": extensions.get("git_source_commit"),
    }:
        raise PetesLakeWetlandCustodyError(
            "current Git branch or HEAD changed after custody authorization"
        )


@contextmanager
def _transaction_mutex(root: Path) -> Any:
    lock_path = _project_path(root, MUTEX_PATH)
    _assert_ignored_untracked(root, lock_path)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    _assert_no_link_like_path_components(lock_path.parent)
    flags = os.O_RDWR | os.O_CREAT | getattr(os, "O_BINARY", 0)
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(lock_path, flags, 0o600)
    handle = os.fdopen(descriptor, "r+b", buffering=0)
    locked = False
    try:
        opened = os.fstat(handle.fileno())
        observed = lock_path.lstat()
        if (
            not stat.S_ISREG(opened.st_mode)
            or opened.st_nlink != 1
            or _is_link_like(lock_path)
            or not os.path.samestat(opened, observed)
        ):
            raise PetesLakeWetlandCustodyError("custody mutex path is unsafe")
        if opened.st_size == 0:
            handle.write(b"\0")
            handle.flush()
            os.fsync(handle.fileno())
        handle.seek(0)
        try:
            import msvcrt

            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            unlock = lambda: msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        except ImportError:
            import fcntl

            try:
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError as error:
                raise PetesLakeWetlandCustodyError(
                    "another NWI custody mutation is active"
                ) from error
            unlock = lambda: fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        except OSError as error:
            raise PetesLakeWetlandCustodyError(
                "another NWI custody mutation is active"
            ) from error
        locked = True
        _assert_no_link_like_path_components(lock_path)
        _assert_ignored_untracked(root, lock_path)
        yield
    finally:
        if locked:
            handle.seek(0)
            try:
                unlock()
            except OSError:
                pass
        handle.close()


def _serialized_mutation(function: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(function)
    def wrapper(repository_root: Path, *args: Any, **kwargs: Any) -> Any:
        root = _validate_root(repository_root)
        with _transaction_mutex(root):
            return function(root, *args, **kwargs)

    return wrapper


def _digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def _file_digest(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _write_contract(path: Path, contract: dict[str, Any], *, create: bool = False) -> None:
    data = _canonical_bytes(contract)
    _assert_no_link_like_path_components(path.parent)
    path.parent.mkdir(parents=True, exist_ok=True)
    _assert_no_link_like_path_components(path.parent)
    if create:
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0)
        try:
            descriptor = os.open(path, flags, 0o600)
        except FileExistsError:
            raise PetesLakeWetlandCustodyError("intake contract exists; no overwrite allowed") from None
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        return
    if not path.is_file() or path.is_symlink() or path.stat().st_nlink != 1:
        raise PetesLakeWetlandCustodyError("intake contract is not a single-link regular file")
    temporary = path.with_name(f".{path.name}.next-{os.getpid()}")
    try:
        with temporary.open("xb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        if temporary.stat().st_nlink != 1:
            raise PetesLakeWetlandCustodyError("temporary contract link count changed")
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _query_parameters(
    *,
    operation: str,
    fields: tuple[str, ...] = (),
    order_field: str = "",
) -> tuple[tuple[str, str], ...]:
    west, south, east, north = QUERY_BOUNDS_UTM10N
    query: list[tuple[str, str]] = [
        ("where", "1=1"),
        (
            "geometry",
            json.dumps(
                {
                    "xmin": west,
                    "ymin": south,
                    "xmax": east,
                    "ymax": north,
                    "spatialReference": {"wkid": 32610},
                },
                separators=(",", ":"),
            ),
        ),
        ("geometryType", "esriGeometryEnvelope"),
        ("inSR", "32610"),
        ("spatialRel", "esriSpatialRelIntersects"),
    ]
    if operation == "count":
        query.extend((("returnCountOnly", "true"), ("f", "json")))
    elif operation == "ids":
        query.extend((("returnIdsOnly", "true"), ("f", "json")))
    elif operation == "features":
        query.extend(
            (
                ("outFields", ",".join(fields)),
                ("returnGeometry", "true"),
                ("returnTrueCurves", "true"),
                ("outSR", "3857"),
                ("returnZ", "false"),
                ("returnM", "false"),
                ("orderByFields", f"{order_field} ASC"),
                ("cacheHint", "false"),
                ("f", "json"),
            )
        )
    else:
        raise PetesLakeWetlandCustodyError("unsupported NWI query operation")
    return tuple(query)


def _post_definition(
    *,
    asset_id: str,
    filename: str,
    layer: str,
    layer_url: str,
    operation: str,
    fields: tuple[str, ...] = (),
    order_field: str = "",
) -> dict[str, Any]:
    parameters = _query_parameters(
        operation=operation, fields=fields, order_field=order_field
    )
    body = urlencode(parameters).encode("ascii")
    return {
        "asset_id": _run_asset_id(asset_id),
        "logical_role": asset_id,
        "filename": filename,
        "uri": f"{layer_url}/query",
        "method": "POST",
        "body": body,
        "body_sha256": _digest(body),
        "format": operation,
        "layer": layer,
    }


def _run_asset_id(logical_role: str) -> str:
    return f"{ASSET_ID_PREFIX}-{logical_role}"


def asset_definitions() -> tuple[dict[str, Any], ...]:
    return (
        {
            "asset_id": _run_asset_id("wetlands-layer-metadata"),
            "logical_role": "wetlands-layer-metadata",
            "filename": "wetlands-layer-metadata.json",
            "uri": f"{WETLAND_LAYER}?f=pjson",
            "method": "GET",
            "body": None,
            "body_sha256": None,
            "format": "layer-metadata",
            "layer": "wetlands",
        },
        _post_definition(asset_id="wetlands-pre-count", filename="wetlands-pre-count.json", layer="wetlands", layer_url=WETLAND_LAYER, operation="count"),
        _post_definition(asset_id="wetlands-pre-ids", filename="wetlands-pre-ids.json", layer="wetlands", layer_url=WETLAND_LAYER, operation="ids"),
        _post_definition(asset_id="wetlands-features", filename="wetlands-features.json", layer="wetlands", layer_url=WETLAND_LAYER, operation="features", fields=WETLAND_FIELDS, order_field="Wetlands.OBJECTID"),
        _post_definition(asset_id="wetlands-post-count", filename="wetlands-post-count.json", layer="wetlands", layer_url=WETLAND_LAYER, operation="count"),
        _post_definition(asset_id="wetlands-post-ids", filename="wetlands-post-ids.json", layer="wetlands", layer_url=WETLAND_LAYER, operation="ids"),
        {
            "asset_id": _run_asset_id("source-layer-metadata"),
            "logical_role": "source-layer-metadata",
            "filename": "source-layer-metadata.json",
            "uri": f"{SOURCE_LAYER}?f=pjson",
            "method": "GET",
            "body": None,
            "body_sha256": None,
            "format": "layer-metadata",
            "layer": "source",
        },
        _post_definition(asset_id="source-pre-count", filename="source-pre-count.json", layer="source", layer_url=SOURCE_LAYER, operation="count"),
        _post_definition(asset_id="source-pre-ids", filename="source-pre-ids.json", layer="source", layer_url=SOURCE_LAYER, operation="ids"),
        _post_definition(asset_id="source-features", filename="source-features.json", layer="source", layer_url=SOURCE_LAYER, operation="features", fields=SOURCE_FIELDS, order_field="OBJECTID"),
        _post_definition(asset_id="source-post-count", filename="source-post-count.json", layer="source", layer_url=SOURCE_LAYER, operation="count"),
        _post_definition(asset_id="source-post-ids", filename="source-post-ids.json", layer="source", layer_url=SOURCE_LAYER, operation="ids"),
    )


def _contract_asset(definition: dict[str, Any]) -> dict[str, Any]:
    identity = METADATA_IDENTITIES.get(definition["layer"]) if definition["format"] == "layer-metadata" else None
    return {
        "asset_id": definition["asset_id"],
        "source": {
            "kind": "https",
            "uri": definition["uri"],
            "authorization_ref": AUTHORIZATION_REFERENCE,
            "terms_ref": TERMS_RECORD_REFERENCE,
            "source_record_ref": SOURCE_RECORD_REFERENCE,
            "transport_exception_ref": None,
        },
        "destination_relative_path": (PACKAGE_DIRECTORY / definition["filename"]).as_posix(),
        "staging_relative_path": definition["filename"] + ".partial",
        "expected": {
            "sha256": identity["sha256"] if identity else None,
            "size_bytes": identity["bytes"] if identity else None,
            "unavailable_reason": (
                None
                if identity
                else "The live public REST query publishes no immutable object digest or byte size; "
                "exact observed bytes are retained and hashed without retry."
            ),
        },
        "observed": {
            "staged_sha256": None,
            "staged_size_bytes": None,
            "promoted_sha256": None,
            "promoted_size_bytes": None,
        },
        "state": "planned",
        "attempts": [],
        "failure": None,
        "superseded_by": None,
        "extensions": {
            "logical_role": definition["logical_role"],
            "http_method": definition["method"],
            "request_body_sha256": definition["body_sha256"],
            "request_body_media_type": (
                "application/x-www-form-urlencoded" if definition["body"] is not None else None
            ),
            "provider_geometry_crs": "EPSG:3857" if definition["format"] == "features" else None,
        },
    }


def _contract_extensions(git_source_commit: str) -> dict[str, Any]:
    return {
        "unit_id": UNIT_ID,
        "run_id": RUN_ID,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": 521,
        "branch": BRANCH,
        "git_source_commit": git_source_commit,
        "grid": {
            "crs": GRID_CRS,
            "analysis_bounds": list(GRID_BOUNDS_UTM10N),
            "query_bounds": list(QUERY_BOUNDS_UTM10N),
            "query_context_buffer_meters": QUERY_CONTEXT_BUFFER_METERS,
            "role": "exact U03 optical grid plus a bounded 100 m context halo for conservative source-scale wetland exclusion; query features remain context only",
        },
        "source_references": {
            "web_service": WEB_SERVICE_REFERENCE,
            "terms": TERMS_REFERENCE,
            "limitations": LIMITATIONS_REFERENCE,
            "user_caution": USER_CAUTION_REFERENCE,
        },
        "tracked_source_gate": [
            {
                "record_id": item["record_id"],
                "path": item["path"].as_posix(),
                "bytes": item["bytes"],
                "sha256": item["sha256"],
            }
            for item in TRACKED_GATE_RECORDS
        ],
        "no_automatic_retry": True,
        "same_source_attempt_policy": "r003 is final; no r004 without explicit owner amendment",
        "analysis_or_label_semantics": "none; custody only",
        "remediation_of": {
            "unit_id": R002_UNIT_ID,
            "run_id": R002_RUN_ID,
            "disposition": "remediate",
            "failure_code": "NWI_TRANSFER_OR_STRUCTURE_FAILURE_NO_RETRY",
            "failure_stage": "PROVIDER_OPEN",
            "evidence": [
                {
                    "role": item["role"],
                    "path": item["path"].as_posix(),
                    "bytes": item["bytes"],
                    "sha256": item["sha256"],
                }
                for item in R002_EVIDENCE
            ],
        },
        "earlier_remediation_evidence": {
            "unit_id": R001_UNIT_ID,
            "run_id": R001_RUN_ID,
            "disposition": "remediate",
            "failure_code": "NWI_TRANSFER_OR_STRUCTURE_FAILURE_NO_RETRY",
            "failure_stage": "RESPONSE_STRUCTURE",
            "evidence": [
                {
                    "role": item["role"],
                    "path": item["path"].as_posix(),
                    "bytes": item["bytes"],
                    "sha256": item["sha256"],
                }
                for item in R001_EVIDENCE
            ],
        },
    }


def _planned_contract_projection(contract: dict[str, Any]) -> dict[str, Any]:
    commit = contract["extensions"]["git_source_commit"]
    return {
        "contract_version": CONTRACT_VERSION,
        "intake_id": INTAKE_ID,
        "created_at": contract["created_at"],
        "collision_policy": "fail",
        "promotion_mode": "atomic-no-replace",
        "secret_policy": "references-only",
        "custody_root": CUSTODY_ROOT.as_posix(),
        "staging_root": STAGING_ROOT.as_posix(),
        "assets": [_contract_asset(item) for item in asset_definitions()],
        "extensions": _contract_extensions(commit),
    }


def _validate_plan_receipt(root: Path, contract: dict[str, Any]) -> None:
    receipt = contract["extensions"].get("plan_receipt")
    if not isinstance(receipt, dict) or set(receipt) != {
        "path",
        "bytes",
        "sha256",
    }:
        raise PetesLakeWetlandCustodyError("immutable plan receipt binding is absent")
    if receipt["path"] != PLAN_PATH.as_posix():
        raise PetesLakeWetlandCustodyError("immutable plan receipt path drifted")
    path = _project_path(root, PLAN_PATH)
    _assert_ignored_untracked(root, path)
    if not path.is_file() or path.is_symlink() or path.stat().st_nlink != 1:
        raise PetesLakeWetlandCustodyError("immutable plan receipt is absent or unsafe")
    data = path.read_bytes()
    if len(data) != receipt["bytes"] or _digest(data) != receipt["sha256"]:
        raise PetesLakeWetlandCustodyError("immutable plan receipt identity changed")
    try:
        plan = json.loads(data, object_pairs_hook=_reject_duplicate_keys)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise PetesLakeWetlandCustodyError("immutable plan receipt is not JSON") from error
    if plan != _planned_contract_projection(contract):
        raise PetesLakeWetlandCustodyError(
            "mutable intake contract no longer matches its immutable plan"
        )


def _terms_refresh_receipt_payload(
    contract: dict[str, Any], refresh: dict[str, Any]
) -> dict[str, Any]:
    return {
        "receipt_version": "1.0",
        "unit_id": UNIT_ID,
        "run_id": RUN_ID,
        "intake_id": INTAKE_ID,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": 521,
        "git_source_commit": contract["extensions"]["git_source_commit"],
        "started_at_utc": refresh["started_at_utc"],
        "completed_at_utc": refresh["completed_at_utc"],
        "automatic_retry": False,
        "observations": deepcopy(refresh["observations"]),
        "tested_semantic_propositions": list(
            OFFICIAL_TERMS_SEMANTIC_PROPOSITIONS
        ),
        "decision": (
            "PASS_CURRENT_OFFICIAL_NWI_TERMS_SEMANTICS_FOR_BOUNDED_PROVIDER_INTAKE"
            if refresh["state"] == "passed"
            else "FAIL_CURRENT_OFFICIAL_NWI_TERMS_REFRESH_NO_RETRY"
        ),
        "failure": deepcopy(refresh["failure"]),
        "provider_data_requests_created": False,
        "scope": "terms-only refresh; this receipt alone authorizes no provider-data request",
    }


def _validate_terms_refresh_receipt(root: Path, contract: dict[str, Any]) -> None:
    refresh = contract["extensions"].get("terms_refresh")
    path = _project_path(root, TERMS_REFRESH_PATH)
    _assert_ignored_untracked(root, path)
    if refresh is None or refresh["state"] == "started":
        if path.exists() or path.is_symlink():
            raise PetesLakeWetlandCustodyError(
                "terminal terms receipt exists without a durable terminal contract marker"
            )
        return
    binding = refresh["receipt"]
    if (
        not path.is_file()
        or path.is_symlink()
        or path.stat().st_nlink != 1
    ):
        raise PetesLakeWetlandCustodyError(
            "official terms refresh receipt is absent or unsafe"
        )
    data = path.read_bytes()
    if len(data) != binding["bytes"] or _digest(data) != binding["sha256"]:
        raise PetesLakeWetlandCustodyError(
            "official terms refresh receipt identity changed"
        )
    try:
        receipt = json.loads(data, object_pairs_hook=_reject_duplicate_keys)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise PetesLakeWetlandCustodyError(
            "official terms refresh receipt is not JSON"
        ) from error
    if receipt != _terms_refresh_receipt_payload(contract, refresh):
        raise PetesLakeWetlandCustodyError(
            "official terms refresh receipt semantics changed"
        )


def _dispatch_receipt_relative_path(asset_id: str) -> Path:
    return DISPATCH_ROOT / f"{asset_id}-attempt-001.json"


def _dispatch_receipt_payload(
    contract: dict[str, Any],
    asset: dict[str, Any],
    definition: dict[str, Any],
    dispatched_at_utc: str,
) -> dict[str, Any]:
    return {
        "receipt_version": "1.0",
        "intake_id": INTAKE_ID,
        "run_id": RUN_ID,
        "asset_id": asset["asset_id"],
        "attempt_id": asset["attempts"][0]["attempt_id"],
        "dispatched_at_utc": dispatched_at_utc,
        "git_source_commit": contract["extensions"]["git_source_commit"],
        "source": {
            "uri": definition["uri"],
            "method": definition["method"],
            "request_body_sha256": definition["body_sha256"],
        },
        "reservation": {
            "path": (STAGING_ROOT / PurePosixPath(asset["staging_relative_path"])).as_posix(),
            "size_bytes": 0,
            "sha256": _digest(b""),
        },
        "automatic_retry": False,
    }


def _validate_dispatch_receipts(root: Path, contract: dict[str, Any]) -> None:
    expected_names: set[str] = set()
    definitions = {item["asset_id"]: item for item in asset_definitions()}
    for asset in contract["assets"]:
        attempt = asset["attempts"][0] if asset["attempts"] else None
        relative = _dispatch_receipt_relative_path(asset["asset_id"])
        receipt_path = _project_path(root, relative)
        _assert_ignored_untracked(root, receipt_path)
        if attempt is None or attempt["request_dispatched_at"] is None:
            if receipt_path.exists() or receipt_path.is_symlink():
                raise PetesLakeWetlandCustodyError(
                    "dispatch receipt exists without a durable contract dispatch marker"
                )
            continue
        expected_names.add(receipt_path.name)
        if attempt["dispatch_receipt_path"] != relative.as_posix():
            raise PetesLakeWetlandCustodyError("dispatch receipt path binding drifted")
        if (
            not receipt_path.is_file()
            or receipt_path.is_symlink()
            or receipt_path.stat().st_nlink != 1
        ):
            raise PetesLakeWetlandCustodyError("dispatch receipt is absent or unsafe")
        data = receipt_path.read_bytes()
        if (
            len(data) != attempt["dispatch_receipt_size_bytes"]
            or _digest(data) != attempt["dispatch_receipt_sha256"]
        ):
            raise PetesLakeWetlandCustodyError("dispatch receipt identity changed")
        try:
            receipt = json.loads(data, object_pairs_hook=_reject_duplicate_keys)
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise PetesLakeWetlandCustodyError("dispatch receipt is not JSON") from error
        expected = _dispatch_receipt_payload(
            contract,
            asset,
            definitions[asset["asset_id"]],
            attempt["request_dispatched_at"],
        )
        if receipt != expected:
            raise PetesLakeWetlandCustodyError("dispatch receipt semantics changed")
    dispatch_root = _project_path(root, DISPATCH_ROOT)
    if dispatch_root.exists():
        if not dispatch_root.is_dir() or dispatch_root.is_symlink():
            raise PetesLakeWetlandCustodyError("dispatch receipt root is unsafe")
        observed_names = {item.name for item in dispatch_root.iterdir()}
        if observed_names != expected_names:
            raise PetesLakeWetlandCustodyError("dispatch receipt roster contains extra or missing files")


def _validate_provider_open_diagnostic(value: Any) -> None:
    if not isinstance(value, dict) or set(value) != {"category", "http_status"}:
        raise PetesLakeWetlandCustodyError(
            "provider-open diagnostic schema is not privacy-safe"
        )
    category = value.get("category")
    status = value.get("http_status")
    if category not in {
        "http",
        "timeout",
        "dns",
        "tls",
        "connection",
        "unknown-open",
    }:
        raise PetesLakeWetlandCustodyError(
            "provider-open diagnostic category is not controlled"
        )
    if category == "http":
        if (
            not isinstance(status, int)
            or isinstance(status, bool)
            or not 100 <= status <= 599
        ):
            raise PetesLakeWetlandCustodyError(
                "provider-open HTTP status is not a bounded integer"
            )
    elif status is not None:
        raise PetesLakeWetlandCustodyError(
            "non-HTTP provider-open diagnostic carries an HTTP status"
        )


def _validate_asset_contract(
    asset: Any,
    definition: dict[str, Any],
    *,
    created_at: datetime,
    prior_completed_at: datetime | None,
) -> datetime | None:
    if not isinstance(asset, dict) or set(asset) != {
        "asset_id",
        "source",
        "destination_relative_path",
        "staging_relative_path",
        "expected",
        "observed",
        "state",
        "attempts",
        "failure",
        "superseded_by",
        "extensions",
    }:
        raise PetesLakeWetlandCustodyError("intake asset schema drifted")
    expected = _contract_asset(definition)
    for key in (
        "asset_id",
        "source",
        "destination_relative_path",
        "staging_relative_path",
        "expected",
        "superseded_by",
    ):
        if asset.get(key) != expected[key]:
            raise PetesLakeWetlandCustodyError(
                f"immutable intake asset field drifted: {definition['asset_id']}:{key}"
            )
    observed = asset.get("observed")
    if not isinstance(observed, dict) or set(observed) != set(expected["observed"]):
        raise PetesLakeWetlandCustodyError("intake observed-identity schema drifted")
    for key, value in observed.items():
        if value is not None and (
            (key.endswith("sha256") and not re.fullmatch(r"[0-9a-f]{64}", str(value)))
            or (key.endswith("size_bytes") and (not isinstance(value, int) or value <= 0))
        ):
            raise PetesLakeWetlandCustodyError("intake observed identity is invalid")
    extensions = asset.get("extensions")
    if not isinstance(extensions, dict):
        raise PetesLakeWetlandCustodyError("intake asset extensions are invalid")
    initial_extensions = expected["extensions"]
    for key, value in initial_extensions.items():
        if extensions.get(key) != value:
            raise PetesLakeWetlandCustodyError(
                f"immutable intake extension drifted: {definition['asset_id']}:{key}"
            )
    allowed_extensions = set(initial_extensions) | {
        "http_status",
        "content_type",
        "content_length",
        "structure",
        "automatic_retry",
    }
    if not set(extensions).issubset(allowed_extensions):
        raise PetesLakeWetlandCustodyError("intake asset extensions contain unknown fields")
    state = asset.get("state")
    if state not in {
        "planned",
        "authorized",
        "staging",
        "staged",
        "verified",
        "promoted",
        "failed",
    }:
        raise PetesLakeWetlandCustodyError("intake asset state is invalid")
    attempts = asset.get("attempts")
    if not isinstance(attempts, list) or len(attempts) > 1:
        raise PetesLakeWetlandCustodyError("intake asset attempt roster is invalid")
    if state in {"planned", "authorized"}:
        if attempts or any(value is not None for value in observed.values()):
            raise PetesLakeWetlandCustodyError("inactive intake asset carries attempt evidence")
        if asset.get("failure") is not None:
            raise PetesLakeWetlandCustodyError("inactive intake asset carries failure evidence")
        return prior_completed_at
    if len(attempts) != 1:
        raise PetesLakeWetlandCustodyError("active intake asset lacks its sole attempt")
    attempt = attempts[0]
    if not isinstance(attempt, dict) or set(attempt) != {
        "attempt_id",
        "started_at",
        "request_dispatched_at",
        "dispatch_receipt_path",
        "dispatch_receipt_size_bytes",
        "dispatch_receipt_sha256",
        "completed_at",
        "outcome",
    }:
        raise PetesLakeWetlandCustodyError("intake attempt schema drifted")
    if attempt.get("attempt_id") != f"{definition['asset_id']}-attempt-001":
        raise PetesLakeWetlandCustodyError("intake attempt identity drifted")
    started_at = _utc_datetime(attempt.get("started_at"))
    if started_at <= created_at or (
        prior_completed_at is not None and started_at <= prior_completed_at
    ):
        raise PetesLakeWetlandCustodyError("intake attempt timestamp is not monotonic")
    dispatched_raw = attempt.get("request_dispatched_at")
    dispatched_at = _utc_datetime(dispatched_raw) if dispatched_raw is not None else None
    if dispatched_at is not None and dispatched_at < started_at:
        raise PetesLakeWetlandCustodyError("request dispatch predates the attempt start")
    receipt_values = (
        attempt.get("dispatch_receipt_path"),
        attempt.get("dispatch_receipt_size_bytes"),
        attempt.get("dispatch_receipt_sha256"),
    )
    if dispatched_at is None:
        if any(value is not None for value in receipt_values):
            raise PetesLakeWetlandCustodyError("undispatched attempt carries a dispatch receipt")
    elif (
        not isinstance(receipt_values[0], str)
        or not isinstance(receipt_values[1], int)
        or receipt_values[1] <= 0
        or not isinstance(receipt_values[2], str)
        or not re.fullmatch(r"[0-9a-f]{64}", receipt_values[2])
    ):
        raise PetesLakeWetlandCustodyError("dispatched attempt lacks an exact receipt identity")
    completed_raw = attempt.get("completed_at")
    completed_at = _utc_datetime(completed_raw) if completed_raw is not None else None
    if completed_at is not None and completed_at <= (dispatched_at or started_at):
        raise PetesLakeWetlandCustodyError("attempt completion predates request dispatch")
    outcome = attempt.get("outcome")
    if state == "staging":
        if outcome != "started" or completed_at is not None:
            raise PetesLakeWetlandCustodyError("staging attempt state is inconsistent")
        if any(value is not None for value in observed.values()):
            raise PetesLakeWetlandCustodyError("staging attempt carries completed identities")
    elif state == "failed":
        failure = asset.get("failure")
        failure_stage = failure.get("stage") if isinstance(failure, dict) else None
        expected_failure_keys = {"code", "stage", "retained_staging", "next_action"}
        if failure_stage == "PROVIDER_OPEN":
            expected_failure_keys.add("provider_open_diagnostic")
        if (
            outcome != "failed"
            or completed_at is None
            or not isinstance(failure, dict)
            or set(failure) != expected_failure_keys
            or failure.get("code") != "NWI_TRANSFER_OR_STRUCTURE_FAILURE_NO_RETRY"
            or any(value is not None for value in observed.values())
        ):
            raise PetesLakeWetlandCustodyError("failed attempt state is inconsistent")
        if failure_stage == "PROVIDER_OPEN":
            _validate_provider_open_diagnostic(failure.get("provider_open_diagnostic"))
        retained = failure.get("retained_staging")
        if (
            failure.get("stage")
            not in {
                "PRE_DISPATCH_FILESYSTEM",
                "STAGING_RESERVATION",
                "DISPATCH_RECEIPT_WRITE",
                "DISPATCH_MARKER_COMMIT",
                "PROVIDER_OPEN",
                "RESPONSE_HEADERS",
                "RESPONSE_BODY",
                "RESPONSE_STRUCTURE",
                "EXPECTED_IDENTITY",
                "STATE_COMMIT",
            }
            or not isinstance(retained, dict)
            or set(retained) != {"status", "size_bytes", "sha256"}
            or retained.get("status")
            not in {"exact", "absent", "unsafe-or-unavailable"}
            or (
                retained.get("status") == "exact"
                and (
                    not isinstance(retained.get("size_bytes"), int)
                    or isinstance(retained.get("size_bytes"), bool)
                    or retained["size_bytes"] < 0
                    or not isinstance(retained.get("sha256"), str)
                    or re.fullmatch(r"[0-9a-f]{64}", retained["sha256"])
                    is None
                )
            )
            or (
                retained.get("status") != "exact"
                and (
                    retained.get("size_bytes") is not None
                    or retained.get("sha256") is not None
                )
            )
            or not isinstance(failure.get("next_action"), str)
            or not failure["next_action"].strip()
        ):
            raise PetesLakeWetlandCustodyError(
                "failed attempt retained-byte evidence is invalid"
            )
    else:
        if outcome != "succeeded" or completed_at is None or asset.get("failure") is not None:
            raise PetesLakeWetlandCustodyError("successful attempt state is inconsistent")
        if observed["staged_sha256"] is None or observed["staged_size_bytes"] is None:
            raise PetesLakeWetlandCustodyError("successful attempt lacks staged identity")
        if state == "promoted" and (
            observed["promoted_sha256"] != observed["staged_sha256"]
            or observed["promoted_size_bytes"] != observed["staged_size_bytes"]
        ):
            raise PetesLakeWetlandCustodyError("promoted identity differs from staged identity")
        if state in {"staged", "verified"} and any(
            observed[key] is not None
            for key in ("promoted_sha256", "promoted_size_bytes")
        ):
            raise PetesLakeWetlandCustodyError("unpromoted attempt carries promoted identity")
        media_type = str(extensions.get("content_type") or "").split(";", 1)[0].strip().casefold()
        if (
            set(extensions) != allowed_extensions
            or extensions.get("http_status") != 200
            or media_type not in ALLOWED_JSON_MEDIA_TYPES
            or extensions.get("automatic_retry") is not False
            or not isinstance(extensions.get("structure"), dict)
            or (
                extensions.get("content_length") is not None
                and (
                    not isinstance(extensions["content_length"], int)
                    or extensions["content_length"] <= 0
                )
            )
        ):
            raise PetesLakeWetlandCustodyError("successful response metadata is incomplete")
    return completed_at or prior_completed_at


def _validate_terms_refresh(value: Any, *, created_at: datetime) -> None:
    if value is None:
        return
    if not isinstance(value, dict) or set(value) != {
        "refresh_version",
        "state",
        "started_at_utc",
        "completed_at_utc",
        "automatic_retry",
        "observations",
        "failure",
        "receipt",
    }:
        raise PetesLakeWetlandCustodyError("official terms refresh schema drifted")
    if value.get("refresh_version") != "1.0" or value.get("automatic_retry") is not False:
        raise PetesLakeWetlandCustodyError("official terms refresh policy drifted")
    state = value.get("state")
    if state not in {"started", "passed", "failed"}:
        raise PetesLakeWetlandCustodyError("official terms refresh state is invalid")
    started_at = _utc_datetime(value.get("started_at_utc"))
    if started_at <= created_at:
        raise PetesLakeWetlandCustodyError(
            "official terms refresh does not follow contract creation"
        )
    observations = value.get("observations")
    if not isinstance(observations, list) or len(observations) > len(OFFICIAL_TERMS_PAGES):
        raise PetesLakeWetlandCustodyError(
            "official terms observation roster is invalid"
        )
    prior = started_at
    for index, observation in enumerate(observations):
        page = OFFICIAL_TERMS_PAGES[index]
        if not isinstance(observation, dict) or set(observation) != {
            "page_id",
            "requested_url",
            "final_url",
            "status",
            "content_type",
            "content_length",
            "bytes",
            "sha256",
            "semantic_fragments",
            "observed_at_utc",
        }:
            raise PetesLakeWetlandCustodyError(
                "official terms observation schema drifted"
            )
        media_type = str(observation.get("content_type") or "").split(
            ";", 1
        )[0].strip().casefold()
        content_length = observation.get("content_length")
        observed_bytes = observation.get("bytes")
        if (
            observation.get("page_id") != page["page_id"]
            or observation.get("requested_url") != page["uri"]
            or observation.get("final_url") != page["uri"]
            or observation.get("status") != 200
            or media_type not in ALLOWED_HTML_MEDIA_TYPES
            or not isinstance(observed_bytes, int)
            or isinstance(observed_bytes, bool)
            or not 0 < observed_bytes <= MAX_TERMS_PAGE_BYTES
            or (
                content_length is not None
                and (
                    not isinstance(content_length, int)
                    or isinstance(content_length, bool)
                    or content_length != observed_bytes
                )
            )
            or not isinstance(observation.get("sha256"), str)
            or re.fullmatch(r"[0-9a-f]{64}", observation["sha256"]) is None
            or observation.get("semantic_fragments")
            != list(page["semantic_fragments"])
        ):
            raise PetesLakeWetlandCustodyError(
                "official terms observation identity or semantics drifted"
            )
        observed_at = _utc_datetime(observation.get("observed_at_utc"))
        if observed_at <= prior:
            raise PetesLakeWetlandCustodyError(
                "official terms observation timestamps are not monotonic"
            )
        prior = observed_at
    completed_raw = value.get("completed_at_utc")
    completed_at = _utc_datetime(completed_raw) if completed_raw is not None else None
    failure = value.get("failure")
    receipt = value.get("receipt")
    if state == "started":
        if completed_at is not None or failure is not None or receipt is not None:
            raise PetesLakeWetlandCustodyError(
                "active official terms refresh carries terminal evidence"
            )
    elif state == "passed":
        if (
            len(observations) != len(OFFICIAL_TERMS_PAGES)
            or completed_at is None
            or completed_at <= prior
            or failure is not None
            or not isinstance(receipt, dict)
        ):
            raise PetesLakeWetlandCustodyError(
                "passed official terms refresh is incomplete"
            )
    else:
        if (
            completed_at is None
            or completed_at <= prior
            or not isinstance(failure, dict)
            or set(failure)
            != {"code", "page_id", "stage", "next_action"}
            or failure.get("code") != "OFFICIAL_TERMS_REFRESH_FAILED_NO_RETRY"
            or failure.get("page_id")
            not in {page["page_id"] for page in OFFICIAL_TERMS_PAGES}
            or failure.get("stage")
            not in {
                "LIVE_PAGE_REQUEST_OR_VALIDATION",
                "PAGE_OBSERVATION_COMMIT",
                "POST_REFRESH_CUSTODY_RECHECK",
                "TERMINAL_RECEIPT_WRITE",
                "AUTHORIZATION_COMMIT",
            }
            or not isinstance(failure.get("next_action"), str)
            or not failure["next_action"].strip()
            or not isinstance(receipt, dict)
        ):
            raise PetesLakeWetlandCustodyError(
                "failed official terms refresh evidence is incomplete"
            )
    if state in {"passed", "failed"} and (
        not isinstance(receipt, dict)
        or set(receipt) != {"path", "bytes", "sha256"}
        or receipt.get("path") != TERMS_REFRESH_PATH.as_posix()
        or not isinstance(receipt.get("bytes"), int)
        or isinstance(receipt.get("bytes"), bool)
        or receipt["bytes"] <= 0
        or not isinstance(receipt.get("sha256"), str)
        or re.fullmatch(r"[0-9a-f]{64}", receipt["sha256"]) is None
    ):
        raise PetesLakeWetlandCustodyError(
            "official terms refresh receipt binding is invalid"
        )


def _validate_contract_structure(contract: Any) -> None:
    if not isinstance(contract, dict) or set(contract) != {
        "contract_version",
        "intake_id",
        "created_at",
        "collision_policy",
        "promotion_mode",
        "secret_policy",
        "custody_root",
        "staging_root",
        "assets",
        "extensions",
    }:
        raise PetesLakeWetlandCustodyError("intake contract schema drifted")
    if (
        contract.get("contract_version") != CONTRACT_VERSION
        or contract.get("intake_id") != INTAKE_ID
        or contract.get("collision_policy") != "fail"
        or contract.get("promotion_mode") != "atomic-no-replace"
        or contract.get("secret_policy") != "references-only"
        or contract.get("custody_root") != CUSTODY_ROOT.as_posix()
        or contract.get("staging_root") != STAGING_ROOT.as_posix()
    ):
        raise PetesLakeWetlandCustodyError("intake contract identity or safety policy drifted")
    created_at = _utc_datetime(contract.get("created_at"))
    extensions = contract.get("extensions")
    if not isinstance(extensions, dict):
        raise PetesLakeWetlandCustodyError("intake contract extensions are invalid")
    commit = extensions.get("git_source_commit")
    if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise PetesLakeWetlandCustodyError("intake contract source commit is invalid")
    immutable_extensions = _contract_extensions(commit)
    for key, value in immutable_extensions.items():
        if extensions.get(key) != value:
            raise PetesLakeWetlandCustodyError(
                f"immutable intake contract extension drifted: {key}"
            )
    final_extension_keys = {
        "completed_at_utc",
        "state",
        "terms_and_limitations",
        "wetland_truth_claim",
        "candidate_or_label_created",
        "next_dependency",
        "bounded_transaction_consistency",
    }
    if not set(extensions).issubset(
        set(immutable_extensions)
        | final_extension_keys
        | {"plan_receipt", "terms_refresh"}
    ):
        raise PetesLakeWetlandCustodyError("intake contract extensions contain unknown fields")
    _validate_terms_refresh(extensions.get("terms_refresh"), created_at=created_at)
    definitions = asset_definitions()
    assets = contract.get("assets")
    if not isinstance(assets, list) or len(assets) != len(definitions):
        raise PetesLakeWetlandCustodyError("intake asset roster length drifted")
    expected_order = [item["asset_id"] for item in definitions]
    observed_order = [item.get("asset_id") if isinstance(item, dict) else None for item in assets]
    if observed_order != expected_order or len(set(observed_order)) != len(observed_order):
        raise PetesLakeWetlandCustodyError("intake asset roster order or uniqueness drifted")
    prior_completed_at: datetime | None = None
    states: list[str] = []
    for asset, definition in zip(assets, definitions, strict=True):
        prior_completed_at = _validate_asset_contract(
            asset,
            definition,
            created_at=created_at,
            prior_completed_at=prior_completed_at,
        )
        states.append(asset["state"])
    if all(state == "planned" for state in states):
        pass
    elif "planned" in states:
        raise PetesLakeWetlandCustodyError("planned and authorized intake states are mixed")
    else:
        first_nonpromoted = next(
            (index for index, state in enumerate(states) if state != "promoted"),
            len(states),
        )
        if any(state != "promoted" for state in states[:first_nonpromoted]):
            raise PetesLakeWetlandCustodyError("intake promoted prefix is invalid")
        if first_nonpromoted < len(states):
            if any(state != "authorized" for state in states[first_nonpromoted + 1 :]):
                raise PetesLakeWetlandCustodyError("intake dependency order drifted")
    terms_state = (
        extensions.get("terms_refresh", {}).get("state")
        if isinstance(extensions.get("terms_refresh"), dict)
        else None
    )
    if all(state == "planned" for state in states):
        if terms_state == "passed":
            raise PetesLakeWetlandCustodyError(
                "passed official terms refresh lacks authorized assets"
            )
    elif terms_state != "passed":
        raise PetesLakeWetlandCustodyError(
            "active intake assets lack a passed live official terms refresh"
        )
    final_state = extensions.get("state")
    if final_state is None:
        if any(key in extensions for key in final_extension_keys):
            raise PetesLakeWetlandCustodyError("partial finalization metadata is present")
    else:
        if final_state != "PASS_EXACT_PUBLIC_NWI_CONTEXT_CUSTODY_FOR_U05" or any(
            state != "promoted" for state in states
        ):
            raise PetesLakeWetlandCustodyError("final intake state is inconsistent")
        if (
            extensions.get("terms_and_limitations")
            != "TERMS-2026-028 resolved for bounded query, ignored local custody, and attributed derived exclusion context only; raw payload republication blocked"
            or extensions.get("wetland_truth_claim") is not False
            or extensions.get("candidate_or_label_created") is not False
            or extensions.get("next_dependency")
            != "P2O4-T33-U05_REFERENCE_FITNESS"
            or not isinstance(extensions.get("bounded_transaction_consistency"), dict)
        ):
            raise PetesLakeWetlandCustodyError("final intake disposition metadata drifted")
        completed_at = _utc_datetime(extensions.get("completed_at_utc"))
        if prior_completed_at is None or completed_at <= prior_completed_at:
            raise PetesLakeWetlandCustodyError("final intake timestamp is not monotonic")


def _validate_root(root: Path) -> Path:
    lexical = _absolute_lexical_path(root)
    _assert_no_link_like_path_components(lexical)
    if not (lexical / ".git").exists() or not (lexical / "pyproject.toml").is_file():
        raise PetesLakeWetlandCustodyError("repository root is not the canonical BurnLens checkout")
    return lexical


@_serialized_mutation
def initialize_contract(
    repository_root: Path,
    *,
    created_at_utc: str,
    git_source_commit: str,
) -> dict[str, Any]:
    root = _validate_root(repository_root)
    _utc(created_at_utc)
    if not re.fullmatch(r"[0-9a-f]{40}", git_source_commit):
        raise PetesLakeWetlandCustodyError("git source commit must be an exact lowercase SHA-1")
    _verify_retained_r001_evidence(root)
    _verify_retained_r002_evidence(root)
    _preflight_initialize(root, git_source_commit)
    _verify_tracked_gate_records(root)
    contract_path = _project_path(root, CONTRACT_PATH)
    plan_path = _project_path(root, PLAN_PATH)
    terms_refresh_path = _project_path(root, TERMS_REFRESH_PATH)
    staging = _project_path(root, STAGING_ROOT)
    package = _project_path(root, CUSTODY_ROOT / PACKAGE_DIRECTORY)
    for private_path in (
        contract_path,
        plan_path,
        terms_refresh_path,
        staging,
        package,
    ):
        _assert_ignored_untracked(root, private_path)
    if (
        contract_path.exists()
        or plan_path.exists()
        or terms_refresh_path.exists()
        or terms_refresh_path.is_symlink()
        or staging.exists()
        or package.exists()
    ):
        raise PetesLakeWetlandCustodyError("intake target exists; no overwrite allowed")
    if shutil.disk_usage(root).free < MIN_FREE_BYTES:
        raise PetesLakeWetlandCustodyError("insufficient free space for bounded intake")
    contract = {
        "contract_version": CONTRACT_VERSION,
        "intake_id": INTAKE_ID,
        "created_at": created_at_utc,
        "collision_policy": "fail",
        "promotion_mode": "atomic-no-replace",
        "secret_policy": "references-only",
        "custody_root": CUSTODY_ROOT.as_posix(),
        "staging_root": STAGING_ROOT.as_posix(),
        "assets": [_contract_asset(item) for item in asset_definitions()],
        "extensions": _contract_extensions(git_source_commit),
    }
    plan = deepcopy(contract)
    try:
        write_private_state(plan_path, plan, repo_root=root)
    except AcquisitionError as error:
        raise PetesLakeWetlandCustodyError(
            "immutable intake plan receipt could not be written"
        ) from error
    plan_data = plan_path.read_bytes()
    contract["extensions"]["plan_receipt"] = {
        "path": PLAN_PATH.as_posix(),
        "bytes": len(plan_data),
        "sha256": _digest(plan_data),
    }
    try:
        _write_contract(contract_path, contract, create=True)
    except Exception:
        if (
            plan_path.is_file()
            and not plan_path.is_symlink()
            and plan_path.stat().st_nlink == 1
            and plan_path.read_bytes() == plan_data
        ):
            plan_path.unlink()
        raise
    return contract


def load_contract(repository_root: Path) -> tuple[Path, dict[str, Any]]:
    root = _validate_root(repository_root)
    _verify_retained_r001_evidence(root)
    _verify_retained_r002_evidence(root)
    path = _project_path(root, CONTRACT_PATH)
    if not path.is_file() or path.is_symlink() or path.stat().st_nlink != 1:
        raise PetesLakeWetlandCustodyError("intake contract is absent or unsafe")
    try:
        contract = json.loads(
            path.read_bytes(), object_pairs_hook=_reject_duplicate_keys
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise PetesLakeWetlandCustodyError("intake contract is not valid JSON") from error
    _validate_contract_structure(contract)
    _validate_plan_receipt(root, contract)
    _validate_terms_refresh_receipt(root, contract)
    _validate_dispatch_receipts(root, contract)
    _verify_failed_staging_evidence(root, contract)
    return path, contract


def _write_terms_refresh_receipt(
    root: Path, contract: dict[str, Any], refresh: dict[str, Any]
) -> dict[str, Any]:
    receipt_path = _project_path(root, TERMS_REFRESH_PATH)
    _assert_ignored_untracked(root, receipt_path)
    if receipt_path.exists() or receipt_path.is_symlink():
        raise PetesLakeWetlandCustodyError(
            "official terms refresh receipt exists; no overwrite allowed"
        )
    payload = _terms_refresh_receipt_payload(contract, refresh)
    try:
        write_private_state(receipt_path, payload, repo_root=root)
    except AcquisitionError as error:
        raise PetesLakeWetlandCustodyError(
            "official terms refresh receipt could not be durably written"
        ) from error
    data = receipt_path.read_bytes()
    return {
        "path": TERMS_REFRESH_PATH.as_posix(),
        "bytes": len(data),
        "sha256": _digest(data),
    }


@_serialized_mutation
def authorize_contract(
    repository_root: Path,
    *,
    terms_open_fn: Callable[..., Any] | None = None,
    now_fn: Callable[[], str] = _now_utc,
) -> dict[str, Any]:
    root = _validate_root(repository_root)
    path, contract = load_contract(root)
    _verify_mutation_context(root, contract)
    _verify_tracked_gate_records(root)
    _verify_locked_geometry_runtime()
    if contract["extensions"].get("state") is not None:
        raise PetesLakeWetlandCustodyError("finalized intake is immutable")
    if any(item.get("state") != "planned" for item in contract["assets"]):
        raise PetesLakeWetlandCustodyError("only a fully planned contract may be authorized")
    if contract["extensions"].get("terms_refresh") is not None:
        raise PetesLakeWetlandCustodyError(
            "official terms refresh is one-shot; existing attempt requires disposition"
        )
    for item in contract["assets"]:
        source = urlsplit(item["source"]["uri"])
        if (
            source.scheme != "https"
            or source.hostname != SERVICE_HOST
            or source.port not in (None, 443)
            or source.username is not None
            or source.password is not None
            or source.fragment
        ):
            raise PetesLakeWetlandCustodyError("source failed exact public HTTPS contract")
        destination = _project_path(
            root, CUSTODY_ROOT / PurePosixPath(item["destination_relative_path"])
        )
        staging = _project_path(
            root, STAGING_ROOT / PurePosixPath(item["staging_relative_path"])
        )
        _assert_ignored_untracked(root, destination)
        _assert_ignored_untracked(root, staging)
        if destination.exists() or destination.is_symlink() or staging.exists() or staging.is_symlink():
            raise PetesLakeWetlandCustodyError("intake path collision blocks authorization")
    started_at_utc, started_at = _monotonic_timestamp(
        now_fn, _utc_datetime(contract["created_at"])
    )
    refresh = {
        "refresh_version": "1.0",
        "state": "started",
        "started_at_utc": started_at_utc,
        "completed_at_utc": None,
        "automatic_retry": False,
        "observations": [],
        "failure": None,
        "receipt": None,
    }
    contract["extensions"]["terms_refresh"] = refresh
    _write_contract(path, contract)
    opener = terms_open_fn or _open_no_redirect
    active_page_id = OFFICIAL_TERMS_PAGES[0]["page_id"]
    failure_stage = "LIVE_PAGE_REQUEST_OR_VALIDATION"
    prior_timestamp = started_at
    try:
        for page_definition in OFFICIAL_TERMS_PAGES:
            active_page_id = page_definition["page_id"]
            failure_stage = "LIVE_PAGE_REQUEST_OR_VALIDATION"
            observation = _capture_official_terms_page(
                page_definition,
                open_fn=opener,
            )
            observed_at_utc, prior_timestamp = _monotonic_timestamp(
                now_fn, prior_timestamp
            )
            observation["observed_at_utc"] = observed_at_utc
            refresh["observations"].append(observation)
            failure_stage = "PAGE_OBSERVATION_COMMIT"
            _write_contract(path, contract)

        failure_stage = "POST_REFRESH_CUSTODY_RECHECK"
        for item in contract["assets"]:
            destination = _destination_path(root, item)
            staging = _staging_path(root, item)
            _assert_ignored_untracked(root, destination)
            _assert_ignored_untracked(root, staging)
            if (
                destination.exists()
                or destination.is_symlink()
                or staging.exists()
                or staging.is_symlink()
            ):
                raise PetesLakeWetlandCustodyError(
                    "intake path collision appeared during terms refresh"
                )
        completed_at_utc, prior_timestamp = _monotonic_timestamp(
            now_fn, prior_timestamp
        )
        refresh.update(
            {
                "state": "passed",
                "completed_at_utc": completed_at_utc,
                "failure": None,
            }
        )
        failure_stage = "TERMINAL_RECEIPT_WRITE"
        refresh["receipt"] = _write_terms_refresh_receipt(root, contract, refresh)
        for item in contract["assets"]:
            item["state"] = "authorized"
        failure_stage = "AUTHORIZATION_COMMIT"
        _write_contract(path, contract)
        return contract
    except Exception as error:
        for item in contract["assets"]:
            item["state"] = "planned"
        failed_at_utc, _failed_at = _monotonic_timestamp(now_fn, prior_timestamp)
        refresh.update(
            {
                "state": "failed",
                "completed_at_utc": failed_at_utc,
                "receipt": None,
                "failure": {
                    "code": "OFFICIAL_TERMS_REFRESH_FAILED_NO_RETRY",
                    "page_id": active_page_id,
                    "stage": failure_stage,
                    "next_action": "retain this exact refresh attempt and resolve it before creating a new intake identity",
                },
            }
        )
        try:
            refresh["receipt"] = _write_terms_refresh_receipt(
                root, contract, refresh
            )
            _write_contract(path, contract)
        except Exception:
            pass
        raise PetesLakeWetlandCustodyError(
            "live official terms refresh failed without retry"
        ) from error


def _asset(contract: dict[str, Any], asset_id: str) -> dict[str, Any]:
    matches = [item for item in contract["assets"] if item["asset_id"] == asset_id]
    if len(matches) != 1:
        raise PetesLakeWetlandCustodyError("unknown or duplicate intake asset")
    return matches[0]


def _staging_path(root: Path, asset: dict[str, Any]) -> Path:
    return _project_path(
        root, STAGING_ROOT / PurePosixPath(asset["staging_relative_path"])
    )


def _destination_path(root: Path, asset: dict[str, Any]) -> Path:
    return _project_path(
        root, CUSTODY_ROOT / PurePosixPath(asset["destination_relative_path"])
    )


def _available_asset_path(root: Path, asset: dict[str, Any]) -> Path:
    return (
        _destination_path(root, asset)
        if asset["state"] == "promoted"
        else _staging_path(root, asset)
    )


def _verify_promoted_file_identity(root: Path, asset: dict[str, Any]) -> None:
    destination = _destination_path(root, asset)
    expected = asset["observed"]
    if (
        not destination.is_file()
        or destination.is_symlink()
        or destination.stat().st_nlink != 1
        or destination.stat().st_size != expected["promoted_size_bytes"]
        or _file_digest(destination) != expected["promoted_sha256"]
    ):
        raise PetesLakeWetlandCustodyError(
            "prior promoted response identity changed before provider dispatch"
        )


def _verify_pre_provider_filesystem(
    root: Path,
    contract: dict[str, Any],
    *,
    asset_id: str,
    allow_current_empty_reservation: bool,
) -> None:
    current = _asset(contract, asset_id)
    promoted = [item for item in contract["assets"] if item["state"] == "promoted"]
    package = _project_path(root, CUSTODY_ROOT / PACKAGE_DIRECTORY)
    _assert_ignored_untracked(root, package)
    expected_names = {
        PurePosixPath(item["destination_relative_path"]).name for item in promoted
    }
    if expected_names:
        if not package.is_dir() or package.is_symlink():
            raise PetesLakeWetlandCustodyError(
                "promoted package directory is absent or unsafe before provider dispatch"
            )
        observed = list(package.iterdir())
        if (
            {item.name for item in observed} != expected_names
            or len(observed) != len(expected_names)
        ):
            raise PetesLakeWetlandCustodyError(
                "promoted package roster contains an extra or missing path"
            )
        for item in promoted:
            _verify_promoted_file_identity(root, item)
    elif package.exists() or package.is_symlink():
        raise PetesLakeWetlandCustodyError(
            "raw package exists before the first promoted response"
        )

    current_destination = _destination_path(root, current)
    _assert_ignored_untracked(root, current_destination)
    if current_destination.exists() or current_destination.is_symlink():
        raise PetesLakeWetlandCustodyError(
            "destination collision blocks provider dispatch"
        )

    staging_root = _project_path(root, STAGING_ROOT)
    _assert_ignored_untracked(root, staging_root)
    if not staging_root.exists():
        return
    if not staging_root.is_dir() or staging_root.is_symlink():
        raise PetesLakeWetlandCustodyError(
            "staging root is unsafe before provider dispatch"
        )
    observed_staging = list(staging_root.iterdir())
    current_staging = _staging_path(root, current)
    allowed_names = (
        {current_staging.name}
        if allow_current_empty_reservation and current_staging.exists()
        else set()
    )
    if (
        {item.name for item in observed_staging} != allowed_names
        or len(observed_staging) != len(allowed_names)
    ):
        raise PetesLakeWetlandCustodyError(
            "staging roster contains an extra or stale path"
        )
    if allowed_names:
        observed = current_staging.lstat()
        if (
            not stat.S_ISREG(observed.st_mode)
            or current_staging.is_symlink()
            or observed.st_nlink != 1
            or observed.st_size != 0
        ):
            raise PetesLakeWetlandCustodyError(
                "existing staging reservation is unsafe or nonempty"
            )


@_serialized_mutation
def start_asset(
    repository_root: Path,
    *,
    asset_id: str,
    started_at_utc: str,
) -> dict[str, Any]:
    root = _validate_root(repository_root)
    path, contract = load_contract(root)
    _verify_mutation_context(root, contract)
    _verify_tracked_gate_records(root)
    if contract["extensions"].get("state") is not None:
        raise PetesLakeWetlandCustodyError("finalized intake is immutable")
    asset = _asset(contract, asset_id)
    if asset.get("state") != "authorized" or asset.get("attempts"):
        raise PetesLakeWetlandCustodyError("asset is not eligible for its sole transfer attempt")
    order = [item["asset_id"] for item in asset_definitions()]
    index = order.index(asset_id)
    if any(item["state"] != "promoted" for item in contract["assets"][:index]):
        raise PetesLakeWetlandCustodyError("asset prerequisites are not promoted in exact order")
    if any(item["state"] != "authorized" for item in contract["assets"][index + 1 :]):
        raise PetesLakeWetlandCustodyError("later asset state violates exact intake order")
    _verify_pre_provider_filesystem(
        root,
        contract,
        asset_id=asset_id,
        allow_current_empty_reservation=False,
    )
    definition = asset_definitions()[index]
    if definition["format"] == "features":
        metadata_asset = _asset(
            contract, _run_asset_id(f"{definition['layer']}-layer-metadata")
        )
        count_asset = _asset(
            contract, _run_asset_id(f"{definition['layer']}-pre-count")
        )
        ids_asset = _asset(contract, _run_asset_id(f"{definition['layer']}-pre-ids"))
        metadata = _validate_layer_metadata(
            _read_json(_destination_path(root, metadata_asset)),
            layer=definition["layer"],
        )
        count = _validate_count(_read_json(_destination_path(root, count_asset)))
        ids = _validate_ids(
            _read_json(_destination_path(root, ids_asset)), layer=definition["layer"]
        )["object_ids"]
        if len(ids) != count:
            raise PetesLakeWetlandCustodyError(
                "pre-query count and object-ID roster differ; feature request blocked"
            )
        if count > metadata["max_record_count"]:
            raise PetesLakeWetlandCustodyError(
                "feature response would require unsupported pagination; provider request blocked"
            )
    started_at = _utc_datetime(started_at_utc)
    created_at = _utc_datetime(contract["created_at"])
    previous_completed = None
    if index:
        previous_completed = _utc_datetime(
            contract["assets"][index - 1]["attempts"][0]["completed_at"]
        )
    if started_at <= created_at or (
        previous_completed is not None and started_at <= previous_completed
    ):
        raise PetesLakeWetlandCustodyError("asset start timestamp is not monotonic")
    staging = _project_path(
        root, STAGING_ROOT / PurePosixPath(asset["staging_relative_path"])
    )
    destination = _project_path(
        root, CUSTODY_ROOT / PurePosixPath(asset["destination_relative_path"])
    )
    if staging.exists() or staging.is_symlink() or destination.exists() or destination.is_symlink():
        raise PetesLakeWetlandCustodyError("asset path collision blocks transfer start")
    asset["attempts"].append(
        {
            "attempt_id": f"{asset_id}-attempt-001",
            "started_at": _utc(started_at_utc),
            "request_dispatched_at": None,
            "dispatch_receipt_path": None,
            "dispatch_receipt_size_bytes": None,
            "dispatch_receipt_sha256": None,
            "completed_at": None,
            "outcome": "started",
        }
    )
    asset["state"] = "staging"
    _write_contract(path, contract)
    return asset


def _read_json(path: Path) -> Any:
    try:
        return json.loads(
            path.read_bytes(), object_pairs_hook=_reject_duplicate_keys
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise PetesLakeWetlandCustodyError(f"response is not JSON: {path.name}") from error


def _validate_layer_metadata(payload: Any, *, layer: str) -> dict[str, Any]:
    expected_name = "Wetlands" if layer == "wetlands" else "Source Type"
    expected_types = (
        {
            field_name: WETLAND_FIELD_TYPES[field_name.split(".", 1)[1]]
            for field_name in WETLAND_FIELDS
        }
        if layer == "wetlands"
        else dict(SOURCE_FIELD_TYPES)
    )
    if not isinstance(payload, dict) or payload.get("name") != expected_name:
        raise PetesLakeWetlandCustodyError("NWI layer metadata identity mismatch")
    if payload.get("type") != "Feature Layer" or payload.get("geometryType") != "esriGeometryPolygon":
        raise PetesLakeWetlandCustodyError("NWI layer type or geometry changed")
    raw_fields = payload.get("fields")
    if not isinstance(raw_fields, list):
        raise PetesLakeWetlandCustodyError("NWI layer field contract changed")
    fields: dict[str, dict[str, Any]] = {}
    for item in raw_fields:
        if not isinstance(item, dict) or not isinstance(item.get("name"), str):
            raise PetesLakeWetlandCustodyError("NWI layer field contract changed")
        field_name = item["name"]
        if not field_name or field_name in fields:
            raise PetesLakeWetlandCustodyError(
                "NWI layer exact field name is empty or duplicated"
            )
        fields[field_name] = item
    if not set(expected_types).issubset(fields):
        raise PetesLakeWetlandCustodyError("NWI layer field contract changed")
    for field_name, field_type in expected_types.items():
        if fields[field_name].get("type") != field_type:
            raise PetesLakeWetlandCustodyError("NWI layer field type contract changed")
    maximum = payload.get("maxRecordCount")
    if not isinstance(maximum, int) or maximum < 1:
        raise PetesLakeWetlandCustodyError("NWI maximum record count is unavailable")
    result: dict[str, Any] = {
        "name": expected_name,
        "max_record_count": maximum,
        "field_names": sorted(fields),
        "required_field_types": dict(sorted(expected_types.items())),
    }
    if layer == "source":
        renderer = payload.get("drawingInfo", {}).get("renderer", {})
        values = {
            str(item.get("value"))
            for item in renderer.get("uniqueValueInfos", [])
            if isinstance(item, dict)
        }
        if renderer.get("field1") != "SOURCE_TYPE" or values != SOURCE_TYPE_RENDERER_VALUES:
            raise PetesLakeWetlandCustodyError(
                "NWI source-type publisher renderer contract changed"
            )
        if any(fields[name].get("domain") is not None for name in expected_types):
            raise PetesLakeWetlandCustodyError(
                "NWI source metadata unexpectedly added coded domains"
            )
        result["source_type_renderer_values"] = sorted(values)
        result["coded_value_domains"] = None
    return result


def _validate_count(payload: Any) -> int:
    if not isinstance(payload, dict) or set(payload) != {"count"}:
        raise PetesLakeWetlandCustodyError("NWI count response schema changed")
    count = payload["count"]
    if not isinstance(count, int) or isinstance(count, bool) or count < 0:
        raise PetesLakeWetlandCustodyError("NWI count is invalid")
    return count


def _normalize_attributes(attributes: Any) -> dict[str, Any]:
    if not isinstance(attributes, dict):
        raise PetesLakeWetlandCustodyError("NWI feature attributes are missing")
    normalized: dict[str, Any] = {}
    for key, value in attributes.items():
        short = str(key).split(".")[-1]
        if short in normalized:
            raise PetesLakeWetlandCustodyError("NWI feature attributes collide after qualification")
        normalized[short] = value
    return normalized


def _validate_ids(payload: Any, *, layer: str) -> dict[str, Any]:
    if not isinstance(payload, dict) or not isinstance(payload.get("objectIds"), list):
        raise PetesLakeWetlandCustodyError("NWI object ID response schema changed")
    field = str(payload.get("objectIdFieldName", ""))
    expected = "OBJECTID"
    if field.split(".")[-1] != expected:
        raise PetesLakeWetlandCustodyError("NWI object ID field changed")
    ids = payload["objectIds"]
    if any(not isinstance(item, int) or isinstance(item, bool) for item in ids):
        raise PetesLakeWetlandCustodyError("NWI object ID roster is invalid")
    if len(ids) != len(set(ids)):
        raise PetesLakeWetlandCustodyError("NWI object ID roster contains duplicates")
    return {"object_id_field": field, "object_ids": sorted(ids)}


def _validate_esri_polygon_rings(rings: Any) -> dict[str, int]:
    try:
        from shapely.geometry import LinearRing, MultiPolygon, Polygon
    except ImportError as error:
        raise PetesLakeWetlandCustodyError(
            "locked geo-research environment is required for polygon topology validation"
        ) from error
    if not isinstance(rings, list) or not rings:
        raise PetesLakeWetlandCustodyError("NWI polygon ring roster is absent")
    outers: list[tuple[Any, list[tuple[float, float]]]] = []
    holes: list[tuple[Any, list[tuple[float, float]]]] = []
    coordinate_count = 0
    for coordinates in rings:
        if not isinstance(coordinates, list) or len(coordinates) < 4:
            raise PetesLakeWetlandCustodyError("NWI polygon ring is malformed")
        points: list[tuple[float, float]] = []
        for point in coordinates:
            if (
                not isinstance(point, list)
                or len(point) != 2
                or any(
                    not isinstance(value, (int, float))
                    or isinstance(value, bool)
                    or not math.isfinite(float(value))
                    for value in point
                )
            ):
                raise PetesLakeWetlandCustodyError(
                    "NWI polygon coordinate is not finite exact 2D"
                )
            points.append((float(point[0]), float(point[1])))
        if points[0] != points[-1]:
            raise PetesLakeWetlandCustodyError("NWI polygon ring is not closed")
        ring = LinearRing(points)
        polygon = Polygon(points)
        if not ring.is_simple or not ring.is_valid or not polygon.is_valid or polygon.area <= 0:
            raise PetesLakeWetlandCustodyError("NWI polygon ring topology is invalid")
        (holes if ring.is_ccw else outers).append((polygon, points))
        coordinate_count += len(points)
    if not outers:
        raise PetesLakeWetlandCustodyError("NWI polygon has no clockwise Esri outer ring")
    assigned_holes: list[list[list[tuple[float, float]]]] = [[] for _ in outers]
    for hole, points in holes:
        containers = [
            (index, outer.area)
            for index, (outer, _outer_points) in enumerate(outers)
            if outer.contains(hole.representative_point())
        ]
        if not containers:
            raise PetesLakeWetlandCustodyError("NWI polygon hole is not contained")
        assigned_holes[min(containers, key=lambda item: item[1])[0]].append(points)
    polygons = [
        Polygon(points, holes=assigned_holes[index])
        for index, (_outer, points) in enumerate(outers)
    ]
    assembled = polygons[0] if len(polygons) == 1 else MultiPolygon(polygons)
    if assembled.is_empty or not assembled.is_valid:
        raise PetesLakeWetlandCustodyError("NWI assembled polygon topology is invalid")
    return {
        "ring_count": len(rings),
        "outer_ring_count": len(outers),
        "hole_ring_count": len(holes),
        "coordinate_count": coordinate_count,
    }


def _validate_feature_collection(payload: Any, *, layer: str) -> dict[str, Any]:
    if not isinstance(payload, dict) or payload.get("geometryType") != "esriGeometryPolygon":
        raise PetesLakeWetlandCustodyError("NWI feature response is not polygon Esri JSON")
    spatial_reference = payload.get("spatialReference")
    if not isinstance(spatial_reference, dict) or not {
        spatial_reference.get("wkid"), spatial_reference.get("latestWkid")
    }.intersection({3857, 102100}):
        raise PetesLakeWetlandCustodyError("NWI feature response CRS changed")
    if payload.get("exceededTransferLimit") is True:
        raise PetesLakeWetlandCustodyError("NWI feature response exceeded its transfer limit")
    features = payload.get("features")
    if not isinstance(features, list):
        raise PetesLakeWetlandCustodyError("NWI feature roster is missing")
    required = {
        item.split(".")[-1] for item in (WETLAND_FIELDS if layer == "wetlands" else SOURCE_FIELDS)
    }
    object_ids: set[int] = set()
    geometry_totals = Counter()
    for feature in features:
        if not isinstance(feature, dict):
            raise PetesLakeWetlandCustodyError("NWI feature schema changed")
        geometry = feature.get("geometry")
        if not isinstance(geometry, dict) or set(geometry) != {"rings"}:
            raise PetesLakeWetlandCustodyError("NWI feature geometry is not simple polygon rings")
        geometry_totals.update(_validate_esri_polygon_rings(geometry["rings"]))
        properties = _normalize_attributes(feature.get("attributes"))
        if not required.issubset(properties):
            raise PetesLakeWetlandCustodyError("NWI feature property contract changed")
        object_id = properties.get("OBJECTID")
        if not isinstance(object_id, int) or object_id in object_ids:
            raise PetesLakeWetlandCustodyError("NWI feature OBJECTID is invalid or duplicated")
        object_ids.add(object_id)
    return {
        "feature_count": len(features),
        "object_ids": sorted(object_ids),
        "object_ids_unique": True,
        "spatial_reference": spatial_reference,
        "exceeded_transfer_limit": bool(payload.get("exceededTransferLimit", False)),
        "geometry_totals": dict(sorted(geometry_totals.items())),
    }


def _open_reservation(staging: Path) -> tuple[Any, os.stat_result]:
    _assert_no_link_like_path_components(staging.parent)
    staging.parent.mkdir(parents=True, exist_ok=True)
    _assert_no_link_like_path_components(staging.parent)
    flags = os.O_RDWR | getattr(os, "O_BINARY", 0)
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(staging, flags | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        descriptor = os.open(staging, flags)
    handle = os.fdopen(descriptor, "r+b", buffering=0)
    try:
        opened = os.fstat(handle.fileno())
        observed = staging.lstat()
        if (
            not stat.S_ISREG(opened.st_mode)
            or opened.st_nlink != 1
            or _is_link_like(staging)
            or not os.path.samestat(opened, observed)
            or opened.st_size != 0
        ):
            raise PetesLakeWetlandCustodyError(
                "staging reservation is unsafe or contains prior bytes"
            )
        return handle, opened
    except Exception:
        handle.close()
        raise


def _retained_staging_identity(staging: Path) -> dict[str, Any]:
    if not os.path.lexists(staging):
        return {"status": "absent", "size_bytes": None, "sha256": None}
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0)
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(staging, flags)
        with os.fdopen(descriptor, "rb", buffering=0) as handle:
            opened = os.fstat(handle.fileno())
            observed = staging.lstat()
            if (
                not stat.S_ISREG(opened.st_mode)
                or opened.st_nlink != 1
                or _is_link_like(staging)
                or not os.path.samestat(opened, observed)
            ):
                return {
                    "status": "unsafe-or-unavailable",
                    "size_bytes": None,
                    "sha256": None,
                }
            digest = sha256()
            total = 0
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                total += len(block)
                digest.update(block)
            final_descriptor = os.fstat(handle.fileno())
            final_path = staging.lstat()
            if (
                total != final_descriptor.st_size
                or not os.path.samestat(opened, final_descriptor)
                or not os.path.samestat(opened, final_path)
                or final_path.st_nlink != 1
            ):
                return {
                    "status": "unsafe-or-unavailable",
                    "size_bytes": None,
                    "sha256": None,
                }
            return {
                "status": "exact",
                "size_bytes": total,
                "sha256": digest.hexdigest(),
            }
    except OSError:
        return {
            "status": "unsafe-or-unavailable",
            "size_bytes": None,
            "sha256": None,
        }


def _verify_failed_staging_evidence(root: Path, contract: dict[str, Any]) -> None:
    for asset in contract["assets"]:
        if asset.get("state") != "failed":
            continue
        staging = _project_path(
            root, STAGING_ROOT / PurePosixPath(asset["staging_relative_path"])
        )
        _assert_ignored_untracked(root, staging)
        expected = asset["failure"]["retained_staging"]
        if _retained_staging_identity(staging) != expected:
            raise PetesLakeWetlandCustodyError(
                f"failed retained staging identity changed: {asset['asset_id']}"
            )


@_serialized_mutation
def fetch_asset(
    repository_root: Path,
    *,
    asset_id: str,
    request_dispatched_at_utc: str,
    urlopen_fn: Callable[..., Any] | None = None,
    now_fn: Callable[[], str] = _now_utc,
) -> dict[str, Any]:
    root = _validate_root(repository_root)
    path, contract = load_contract(root)
    _verify_mutation_context(root, contract)
    _verify_tracked_gate_records(root)
    if contract["extensions"].get("state") is not None:
        raise PetesLakeWetlandCustodyError("finalized intake is immutable")
    asset = _asset(contract, asset_id)
    definition = next(item for item in asset_definitions() if item["asset_id"] == asset_id)
    attempts = asset.get("attempts", [])
    if (
        asset.get("state") != "staging"
        or len(attempts) != 1
        or attempts[0].get("outcome") != "started"
        or attempts[0].get("request_dispatched_at") is not None
    ):
        raise PetesLakeWetlandCustodyError(
            "asset is not an undispatched, durably started sole attempt"
        )
    dispatched_at = _utc_datetime(request_dispatched_at_utc)
    started_at = _utc_datetime(attempts[0]["started_at"])
    if dispatched_at <= started_at:
        raise PetesLakeWetlandCustodyError("request dispatch must follow the attempt start")
    staging = _project_path(
        root, STAGING_ROOT / PurePosixPath(asset["staging_relative_path"])
    )
    handle: Any | None = None
    opened_identity: os.stat_result | None = None
    failure_stage = "PRE_DISPATCH_FILESYSTEM"
    try:
        _verify_pre_provider_filesystem(
            root,
            contract,
            asset_id=asset_id,
            allow_current_empty_reservation=True,
        )
        _assert_ignored_untracked(root, staging)
        failure_stage = "STAGING_RESERVATION"
        handle, opened_identity = _open_reservation(staging)
        receipt_relative = _dispatch_receipt_relative_path(asset_id)
        receipt_path = _project_path(root, receipt_relative)
        _assert_ignored_untracked(root, receipt_path)
        receipt = _dispatch_receipt_payload(
            contract, asset, definition, request_dispatched_at_utc
        )
        failure_stage = "DISPATCH_RECEIPT_WRITE"
        try:
            write_private_state(receipt_path, receipt, repo_root=root)
        except AcquisitionError as error:
            raise PetesLakeWetlandCustodyError(
                "dispatch receipt could not be durably written before provider access"
            ) from error
        receipt_data = receipt_path.read_bytes()
        attempts[0].update(
            {
                "request_dispatched_at": request_dispatched_at_utc,
                "dispatch_receipt_path": receipt_relative.as_posix(),
                "dispatch_receipt_size_bytes": len(receipt_data),
                "dispatch_receipt_sha256": _digest(receipt_data),
            }
        )
        failure_stage = "DISPATCH_MARKER_COMMIT"
        _write_contract(path, contract)
        request_headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
        if definition["body"] is not None:
            request_headers["Content-Type"] = "application/x-www-form-urlencoded"
        request = Request(
            asset["source"]["uri"],
            data=definition["body"],
            headers=request_headers,
            method=definition["method"],
        )
        failure_stage = "PROVIDER_OPEN"
        opener = urlopen_fn or _open_no_redirect
        with opener(request, timeout=90) as response:
            failure_stage = "RESPONSE_HEADERS"
            status = getattr(response, "status", None)
            if not isinstance(status, int) or isinstance(status, bool) or status != 200:
                raise PetesLakeWetlandCustodyError("NWI response status is not 200")
            geturl = getattr(response, "geturl", None)
            final_url = str(geturl()) if callable(geturl) else ""
            if final_url != asset["source"]["uri"]:
                raise PetesLakeWetlandCustodyError("NWI response redirected from the exact source")
            content_type = str(response.headers.get("Content-Type") or "")
            if (
                content_type.split(";", 1)[0].strip().casefold()
                not in ALLOWED_JSON_MEDIA_TYPES
            ):
                raise PetesLakeWetlandCustodyError(
                    "NWI response media type is not an allowed JSON-compatible type"
                )
            length_raw = response.headers.get("Content-Length")
            try:
                length = int(length_raw) if length_raw else None
            except (TypeError, ValueError):
                raise PetesLakeWetlandCustodyError(
                    "NWI content length header is invalid"
                ) from None
            if length is not None and not 0 < length <= MAX_RESPONSE_BYTES:
                raise PetesLakeWetlandCustodyError("NWI content length is outside the bounded contract")
            digest = sha256()
            total = 0
            failure_stage = "RESPONSE_BODY"
            while block := response.read(1024 * 1024):
                if not isinstance(block, bytes):
                    raise PetesLakeWetlandCustodyError(
                        "NWI response yielded non-byte content"
                    )
                total += len(block)
                if total > MAX_RESPONSE_BYTES:
                    raise PetesLakeWetlandCustodyError("NWI response exceeds the bounded size")
                handle.write(block)
                digest.update(block)
            handle.flush()
            os.fsync(handle.fileno())
        completed_at_utc = _utc(now_fn())
        if _utc_datetime(completed_at_utc) <= dispatched_at:
            raise PetesLakeWetlandCustodyError(
                "captured transfer completion must follow request dispatch"
            )
        if total <= 0 or (length is not None and total != length):
            raise PetesLakeWetlandCustodyError("NWI response byte count mismatch")
        observed = staging.lstat()
        if (
            not stat.S_ISREG(observed.st_mode)
            or staging.is_symlink()
            or observed.st_nlink != 1
            or opened_identity is None
            or not os.path.samestat(opened_identity, observed)
        ):
            raise PetesLakeWetlandCustodyError(
                "staged response path identity changed during transfer"
            )
        failure_stage = "RESPONSE_STRUCTURE"
        payload = _read_json(staging)
        if definition["format"] == "layer-metadata":
            structure = _validate_layer_metadata(payload, layer=definition["layer"])
        elif definition["format"] == "count":
            structure = {"count": _validate_count(payload)}
        elif definition["format"] == "ids":
            structure = _validate_ids(payload, layer=definition["layer"])
        else:
            structure = _validate_feature_collection(payload, layer=definition["layer"])
        failure_stage = "EXPECTED_IDENTITY"
        expected = asset["expected"]
        if expected["sha256"] is not None and expected["sha256"] != digest.hexdigest():
            raise PetesLakeWetlandCustodyError("NWI published metadata byte identity changed")
        if expected["size_bytes"] is not None and expected["size_bytes"] != total:
            raise PetesLakeWetlandCustodyError("NWI published metadata byte size changed")
        attempts[0].update(
            {"completed_at": _utc(completed_at_utc), "outcome": "succeeded"}
        )
        asset["observed"].update(
            {"staged_sha256": digest.hexdigest(), "staged_size_bytes": total}
        )
        asset["state"] = "staged"
        asset.setdefault("extensions", {}).update(
            {
                "http_status": 200,
                "content_type": content_type,
                "content_length": length,
                "structure": structure,
                "automatic_retry": False,
            }
        )
        failure_stage = "STATE_COMMIT"
        _write_contract(path, contract)
        return asset
    except Exception as error:
        failed_at = _utc_datetime(_utc(now_fn()))
        if failed_at <= dispatched_at:
            failed_at = dispatched_at + timedelta(microseconds=1)
        failed_at_utc = failed_at.isoformat(timespec="microseconds").replace(
            "+00:00", "Z"
        )
        for key in asset["observed"]:
            asset["observed"][key] = None
        for key in (
            "http_status",
            "content_type",
            "content_length",
            "structure",
            "automatic_retry",
        ):
            asset["extensions"].pop(key, None)
        if handle is not None:
            try:
                handle.flush()
                os.fsync(handle.fileno())
            except OSError:
                pass
        attempts[0].update(
            {
                "completed_at": failed_at_utc,
                "outcome": "failed",
            }
        )
        asset["state"] = "failed"
        asset["failure"] = {
            "code": "NWI_TRANSFER_OR_STRUCTURE_FAILURE_NO_RETRY",
            "stage": failure_stage,
            "retained_staging": _retained_staging_identity(staging),
            "next_action": "retain and disposition this exact failed attempt before any new asset identity",
        }
        if failure_stage == "PROVIDER_OPEN":
            asset["failure"]["provider_open_diagnostic"] = _provider_open_diagnostic(error)
        try:
            _write_contract(path, contract)
        except Exception:
            pass
        raise PetesLakeWetlandCustodyError(
            f"NWI transfer failed without retry: {asset_id}"
        ) from None
    finally:
        if handle is not None:
            handle.close()


@_serialized_mutation
def verify_asset(repository_root: Path, *, asset_id: str) -> dict[str, Any]:
    root = _validate_root(repository_root)
    path, contract = load_contract(root)
    _verify_mutation_context(root, contract)
    _verify_tracked_gate_records(root)
    if contract["extensions"].get("state") is not None:
        raise PetesLakeWetlandCustodyError("finalized intake is immutable")
    asset = _asset(contract, asset_id)
    if asset.get("state") != "staged":
        raise PetesLakeWetlandCustodyError("only staged bytes may be verified")
    staging = _staging_path(root, asset)
    expected = asset["observed"]
    if (
        not staging.is_file()
        or staging.is_symlink()
        or staging.stat().st_nlink != 1
        or staging.stat().st_size != expected["staged_size_bytes"]
        or _file_digest(staging) != expected["staged_sha256"]
    ):
        raise PetesLakeWetlandCustodyError("staged response identity changed")
    definition = next(item for item in asset_definitions() if item["asset_id"] == asset_id)
    payload = _read_json(staging)
    if definition["format"] == "layer-metadata":
        _validate_layer_metadata(payload, layer=definition["layer"])
    elif definition["format"] == "count":
        _validate_count(payload)
    elif definition["format"] == "ids":
        _validate_ids(payload, layer=definition["layer"])
    else:
        feature_summary = _validate_feature_collection(payload, layer=definition["layer"])
        count_asset = _asset(
            contract, _run_asset_id(f"{definition['layer']}-pre-count")
        )
        ids_asset = _asset(
            contract, _run_asset_id(f"{definition['layer']}-pre-ids")
        )
        if count_asset.get("state") not in {"verified", "promoted"}:
            raise PetesLakeWetlandCustodyError("pre-count asset must be verified before features")
        if ids_asset.get("state") not in {"verified", "promoted"}:
            raise PetesLakeWetlandCustodyError("pre-ID asset must be verified before features")
        count_path = _available_asset_path(root, count_asset)
        expected_count = _validate_count(_read_json(count_path))
        ids_path = _available_asset_path(root, ids_asset)
        expected_ids = _validate_ids(
            _read_json(ids_path), layer=definition["layer"]
        )["object_ids"]
        metadata_asset = _asset(
            contract, _run_asset_id(f"{definition['layer']}-layer-metadata")
        )
        if metadata_asset.get("state") not in {"verified", "promoted"}:
            raise PetesLakeWetlandCustodyError("layer metadata must be verified before features")
        metadata_path = _available_asset_path(root, metadata_asset)
        metadata = _validate_layer_metadata(_read_json(metadata_path), layer=definition["layer"])
        if feature_summary["feature_count"] != expected_count:
            raise PetesLakeWetlandCustodyError("NWI count and feature response differ")
        if feature_summary["object_ids"] != expected_ids:
            raise PetesLakeWetlandCustodyError("NWI ID and feature response differ")
        if expected_count > metadata["max_record_count"]:
            raise PetesLakeWetlandCustodyError("NWI query requires unsupported pagination")
    asset["state"] = "verified"
    _write_contract(path, contract)
    return asset


@_serialized_mutation
def promote_asset(repository_root: Path, *, asset_id: str) -> dict[str, Any]:
    root = _validate_root(repository_root)
    path, contract = load_contract(root)
    _verify_mutation_context(root, contract)
    _verify_tracked_gate_records(root)
    if contract["extensions"].get("state") is not None:
        raise PetesLakeWetlandCustodyError("finalized intake is immutable")
    asset = _asset(contract, asset_id)
    if asset.get("state") != "verified":
        raise PetesLakeWetlandCustodyError("only verified bytes may be promoted")
    staging = _staging_path(root, asset)
    destination = _destination_path(root, asset)
    _assert_ignored_untracked(root, staging)
    _assert_ignored_untracked(root, destination)
    if destination.exists() or destination.is_symlink():
        raise PetesLakeWetlandCustodyError("destination collision blocks promotion")
    expected = asset["observed"]
    if (
        not staging.is_file()
        or staging.is_symlink()
        or staging.stat().st_nlink != 1
        or staging.stat().st_size != expected["staged_size_bytes"]
        or _file_digest(staging) != expected["staged_sha256"]
    ):
        raise PetesLakeWetlandCustodyError(
            "verified staging identity changed before promotion"
        )
    destination.parent.mkdir(parents=True, exist_ok=True)
    _assert_no_link_like_path_components(destination.parent)
    _assert_ignored_untracked(root, destination)
    if destination.exists() or destination.is_symlink():
        raise PetesLakeWetlandCustodyError(
            "destination collision appeared immediately before promotion"
        )
    try:
        os.link(staging, destination, follow_symlinks=False)
    except FileExistsError:
        raise PetesLakeWetlandCustodyError("destination collision blocks atomic promotion") from None
    if (
        not destination.is_file()
        or destination.is_symlink()
        or destination.stat().st_nlink != 2
        or destination.stat().st_size != expected["staged_size_bytes"]
        or _file_digest(destination) != expected["staged_sha256"]
    ):
        raise PetesLakeWetlandCustodyError("promoted response failed exact readback")
    staging.unlink()
    if destination.stat().st_nlink != 1:
        raise PetesLakeWetlandCustodyError("promoted response is not a single-link file")
    asset["observed"].update(
        {
            "promoted_sha256": expected["staged_sha256"],
            "promoted_size_bytes": expected["staged_size_bytes"],
        }
    )
    asset["state"] = "promoted"
    _write_contract(path, contract)
    return asset


def _validate_exact_custody_roster(
    root: Path,
    contract: dict[str, Any],
    *,
    staging_may_be_absent: bool,
) -> None:
    package = _project_path(root, CUSTODY_ROOT / PACKAGE_DIRECTORY)
    expected_names = {item["filename"] for item in asset_definitions()}
    if not package.is_dir() or package.is_symlink():
        raise PetesLakeWetlandCustodyError("final NWI package directory is absent or unsafe")
    observed = list(package.iterdir())
    if {item.name for item in observed} != expected_names or len(observed) != len(expected_names):
        raise PetesLakeWetlandCustodyError("final NWI package roster contains extra or missing paths")
    for asset in contract["assets"]:
        destination = _destination_path(root, asset)
        if (
            not destination.is_file()
            or destination.is_symlink()
            or destination.stat().st_nlink != 1
            or destination.stat().st_size != asset["observed"]["promoted_size_bytes"]
            or _file_digest(destination) != asset["observed"]["promoted_sha256"]
        ):
            raise PetesLakeWetlandCustodyError("final custody readback failed")
    staging = _project_path(root, STAGING_ROOT)
    if not staging.exists():
        if staging_may_be_absent:
            return
        raise PetesLakeWetlandCustodyError("final staging directory unexpectedly disappeared")
    if not staging.is_dir() or staging.is_symlink() or any(staging.iterdir()):
        raise PetesLakeWetlandCustodyError("final staging roster is not exactly empty")


def _compute_bounded_consistency(
    root: Path, contract: dict[str, Any]
) -> dict[str, Any]:
    consistency: dict[str, Any] = {}
    for layer in ("wetlands", "source"):
        def payload(asset_id: str) -> Any:
            return _read_json(_destination_path(root, _asset(contract, asset_id)))

        metadata = _validate_layer_metadata(
            payload(_run_asset_id(f"{layer}-layer-metadata")), layer=layer
        )
        pre_count = _validate_count(payload(_run_asset_id(f"{layer}-pre-count")))
        post_count = _validate_count(payload(_run_asset_id(f"{layer}-post-count")))
        pre_ids = _validate_ids(
            payload(_run_asset_id(f"{layer}-pre-ids")), layer=layer
        )["object_ids"]
        post_ids = _validate_ids(
            payload(_run_asset_id(f"{layer}-post-ids")), layer=layer
        )["object_ids"]
        features = _validate_feature_collection(
            payload(_run_asset_id(f"{layer}-features")), layer=layer
        )
        if not (
            pre_count
            == post_count
            == len(pre_ids)
            == len(post_ids)
            == features["feature_count"]
            and pre_ids == post_ids == features["object_ids"]
        ):
            raise PetesLakeWetlandCustodyError(
                f"{layer} pre/payload/post identity changed during bounded intake"
            )
        if pre_count > metadata["max_record_count"]:
            raise PetesLakeWetlandCustodyError(f"{layer} response requires pagination")
        consistency[layer] = {
            "feature_count": pre_count,
            "pre_post_count_equal": True,
            "pre_post_object_ids_equal": True,
            "payload_object_ids_equal": True,
            "max_record_count": metadata["max_record_count"],
            "transfer_limit_exceeded": False,
            "provider_geometry_crs": "EPSG:3857",
            "geometry_totals": features["geometry_totals"],
        }
    return consistency


def validate_finalized_contract(repository_root: Path) -> dict[str, Any]:
    root = _validate_root(repository_root)
    _verify_tracked_gate_records(root)
    _path, contract = load_contract(root)
    if contract["extensions"].get("state") != "PASS_EXACT_PUBLIC_NWI_CONTEXT_CUSTODY_FOR_U05":
        raise PetesLakeWetlandCustodyError("NWI custody is not finalized")
    _validate_exact_custody_roster(root, contract, staging_may_be_absent=True)
    consistency = _compute_bounded_consistency(root, contract)
    if consistency != contract["extensions"].get("bounded_transaction_consistency"):
        raise PetesLakeWetlandCustodyError(
            "stored NWI transaction consistency does not match fresh recomputation"
        )
    return deepcopy(contract)


@_serialized_mutation
def finalize_contract(repository_root: Path, *, completed_at_utc: str) -> dict[str, Any]:
    root = _validate_root(repository_root)
    path, contract = load_contract(root)
    _verify_mutation_context(root, contract)
    _verify_tracked_gate_records(root)
    if contract["extensions"].get("state") is not None:
        raise PetesLakeWetlandCustodyError("finalized intake is immutable")
    if any(item.get("state") != "promoted" for item in contract["assets"]):
        raise PetesLakeWetlandCustodyError("all assets must be promoted before finalization")
    finalized_at = _utc_datetime(completed_at_utc)
    last_completed = _utc_datetime(contract["assets"][-1]["attempts"][0]["completed_at"])
    if finalized_at <= last_completed:
        raise PetesLakeWetlandCustodyError(
            "finalization timestamp must follow the last transfer completion"
        )
    _validate_exact_custody_roster(root, contract, staging_may_be_absent=False)
    consistency = _compute_bounded_consistency(root, contract)
    contract["extensions"].update(
        {
            "completed_at_utc": _utc(completed_at_utc),
            "state": "PASS_EXACT_PUBLIC_NWI_CONTEXT_CUSTODY_FOR_U05",
            "terms_and_limitations": "TERMS-2026-028 resolved for bounded query, ignored local custody, and attributed derived exclusion context only; raw payload republication blocked",
            "wetland_truth_claim": False,
            "candidate_or_label_created": False,
            "next_dependency": "P2O4-T33-U05_REFERENCE_FITNESS",
            "bounded_transaction_consistency": consistency,
        }
    )
    _write_contract(path, contract)
    try:
        _project_path(root, STAGING_ROOT).rmdir()
    except OSError:
        pass
    return validate_finalized_contract(root)
