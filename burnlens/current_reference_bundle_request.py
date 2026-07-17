"""Preserve an exact current-reference bundle request without claiming delivery."""

from __future__ import annotations

import hashlib
import html
import json
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from PIL import Image, ImageDraw, ImageFont

from .current_reference_inventory import (
    EXPECTED_PRODUCTS,
    CurrentReferenceInventoryError,
    normalize_inventory,
)
from .provider_acquisition import USER_AGENT


SOFTWARE_VERSION = "0.22.0"
REPORT_ID = "CURRENT-REFERENCE-BUNDLE-REQUEST-2026-001"
REPORT_SCHEMA_VERSION = "0.1.0"
REPORT_VERSION = "current-reference-bundle-request-evidence-v0.1.0"
REQUEST_CONTRACT_VERSION = "current-reference-bundle-request-contract-v0.1.0"
SOURCE_RECORD_ID = "SOURCE-2026-015"
TERMS_REVIEW_ID = "TERMS-2026-010"
TASK_ISSUE = 421
PARENT_ISSUE = 416
DECISION = "AWAIT_EXACT_OFFICIAL_BUNDLE_DELIVERY_DEFER_LABELS_DATASET_MODEL"
MAX_METADATA_RESPONSE_BYTES = 2 * 1024 * 1024

WFS_ENDPOINT = "https://edcintl.cr.usgs.gov/geoserver/wfs"
QUEUE_ENDPOINT = "https://burnseverity.cr.usgs.gov/downloads/addQueue.php"
FULL_PROPERTY_NAMES = (
    "id",
    "map_id",
    "map_prog",
    "incid_name",
    "event_id",
    "ig_date",
    "burnbndac",
    "nonstandard",
    "asmt_type",
    "post_id",
    "postfire_date",
    "model",
    "comment",
)

MAPPING_IDS = (10030231, 10030383, 10007931, 10004989, 10011986, 10008484)
MAPPING_BUNDLES = (("baer/2018/OR4383912111420180907.zip", 0),)
MAPPING_PRODUCTS = (
    "Metadata",
    "Pre-fire reflectance",
    "Post-fire reflectance",
    "Continuous severity (i.e dnbr)",
    "Relative continuous severity (i.e rdnbr)",
    "Burned area boundary",
    "Non-processing mask",
    "KMZ",
    "PDF",
    "6 - Class thematic severity",
    "Soil burn severity",
    "Continuous basal area loss",
    "4 - Class basal area loss",
    "7 - Class basal area loss",
    "Continuous canopy cover loss",
    "5 - Class canopy cover loss",
    "Continuous composite burn index",
    "4 - Class composite burn index",
)

EXPECTED_ASSESSMENT_FIELDS = {
    850: {
        "assessment_type": "Extended",
        "post_id": "804503020180710",
        "postfire_date": "2018-07-10",
        "model": "",
        "comment": "",
    },
    3238: {
        "assessment_type": "Initial",
        "post_id": "804503020181014",
        "postfire_date": "2018-10-14",
        "model": "NATL",
        "comment": (
            "The eastern half of this fire was in non-forest cover (e.g., grass or shrub). "
            "RAVG models, which are calibrated for forest cover, are not directly applicable "
            "to these other cover types. "
        ),
    },
    10452: {
        "assessment_type": "Initial",
        "post_id": "804503020170909",
        "postfire_date": "2017-09-09",
        "model": "NATL",
        "comment": (
            "Post-fire scene is best available Landsat imagery as of 20 October but is earlier "
            "after containment than ideal for open canopy cover. Burn severity measures may be "
            "overestimated in those areas."
        ),
    },
    15933: {
        "assessment_type": "Emergency",
        "post_id": "A10TFP20240702_20m",
        "postfire_date": "2024-07-02",
        "model": "",
        "comment": "",
    },
    23539: {
        "assessment_type": "Initial",
        "post_id": "804503020181014",
        "postfire_date": "2018-10-14",
        "model": "",
        "comment": "",
    },
    30012: {
        "assessment_type": "Initial",
        "post_id": "904503020240718",
        "postfire_date": "2024-07-18",
        "model": "NATL",
        "comment": (
            "Portions of this burned area have sparse to no pre-fire tree cover. RAVG models, "
            "which are calibrated for forest cover, are not directly applicable to other cover "
            "types. In areas with very sparse tree cover, the modeled values are less reliable "
            "since the observed reflectance is strongly dominated by the non-tree component."
        ),
    },
    52523: {
        "assessment_type": "Emergency",
        "post_id": "",
        "postfire_date": "",
        "model": "",
        "comment": "Geomac from 9/11, no edits",
    },
}

CAUTION_DETAILS = {
    30012: {
        "code": "DARLENE_RAVG_SPARSE_TREE_COVER",
        "summary": (
            "Sparse or absent pre-fire tree cover makes the forest-calibrated RAVG model less "
            "reliable where non-tree reflectance dominates."
        ),
        "effect": "RAVG cannot independently promote Darlene labels.",
    },
    3238: {
        "code": "TEPEE_RAVG_NON_FOREST_COVER",
        "summary": (
            "About the eastern half is non-forest cover, where the forest-calibrated RAVG model "
            "is not directly applicable."
        ),
        "effect": "RAVG cannot independently promote Tepee labels in affected cover.",
    },
    10452: {
        "code": "MCKAY_RAVG_EARLY_POST_SCENE",
        "summary": (
            "The available post-fire scene is earlier than ideal for open canopy, so severity "
            "may be overestimated there."
        ),
        "effect": "RAVG severity requires optical and cross-program corroboration.",
    },
    52523: {
        "code": "TEPEE_BAER_NONSTANDARD_LEGACY",
        "summary": "The BAER record is nonstandard, has no map ID, and carries a minimal legacy note.",
        "effect": "Use only the explicit viewer-resolved bundle path; inspect contents before use.",
    },
}


class CurrentReferenceBundleRequestError(RuntimeError):
    """A deterministic, secret-free bundle-request evidence failure."""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def request_payload() -> dict[str, Any]:
    return {
        "download_type": "mapping_products",
        "mapping_bundles": [list(item) for item in MAPPING_BUNDLES],
        "mapping_ids": list(MAPPING_IDS),
        "mapping_products": list(MAPPING_PRODUCTS),
        "projection": "UTM",
        "mosaics": [],
    }


def full_inventory_request_url() -> str:
    event_ids = sorted({str(item["event_id"]) for item in EXPECTED_PRODUCTS})
    cql_filter = "event_id IN (" + ",".join(f"'{item}'" for item in event_ids) + ")"
    query = urlencode(
        (
            ("service", "WFS"),
            ("version", "2.0.0"),
            ("request", "GetFeature"),
            ("typeNames", "mtbs:fire_polygons"),
            ("outputFormat", "application/json"),
            ("propertyName", ",".join(FULL_PROPERTY_NAMES)),
            ("cql_filter", cql_filter),
        )
    )
    return f"{WFS_ENDPOINT}?{query}"


def fetch_full_inventory_response(*, timeout_seconds: int = 90) -> bytes:
    request = Request(
        full_inventory_request_url(),
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    )
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            status = int(getattr(response, "status", 200))
            content_type = response.headers.get_content_type()
            data = response.read(MAX_METADATA_RESPONSE_BYTES + 1)
    except OSError as error:
        raise CurrentReferenceBundleRequestError(
            "official full-metadata endpoint is unavailable"
        ) from error
    if status != 200 or content_type not in {"application/json", "application/geo+json"}:
        raise CurrentReferenceBundleRequestError(
            "official full-metadata response is not JSON"
        )
    if len(data) > MAX_METADATA_RESPONSE_BYTES:
        raise CurrentReferenceBundleRequestError(
            "official full-metadata response exceeds bounded size"
        )
    return data


def _date(value: Any) -> str:
    if value in (None, ""):
        return ""
    text = str(value)
    return text[:10]


def normalize_assessment_metadata(raw_response: bytes) -> list[dict[str, Any]]:
    try:
        payload = json.loads(raw_response)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise CurrentReferenceBundleRequestError(
            "full-metadata response is invalid JSON"
        ) from error
    features = payload.get("features")
    if not isinstance(features, list):
        raise CurrentReferenceBundleRequestError("full-metadata features are invalid")
    by_catalog_id: dict[int, dict[str, Any]] = {}
    for feature in features:
        if not isinstance(feature, dict) or feature.get("geometry") is not None:
            raise CurrentReferenceBundleRequestError(
                "full-metadata response must remain property-only"
            )
        properties = feature.get("properties")
        if not isinstance(properties, dict) or not isinstance(properties.get("id"), int):
            raise CurrentReferenceBundleRequestError(
                "full-metadata properties are invalid"
            )
        catalog_id = int(properties["id"])
        if catalog_id in by_catalog_id:
            raise CurrentReferenceBundleRequestError(
                f"duplicate full-metadata catalog ID {catalog_id}"
            )
        by_catalog_id[catalog_id] = properties
    if set(by_catalog_id) != set(EXPECTED_ASSESSMENT_FIELDS):
        raise CurrentReferenceBundleRequestError(
            "full-metadata product identities differ from the request contract"
        )
    try:
        base_products = normalize_inventory(raw_response)
    except CurrentReferenceInventoryError as error:
        raise CurrentReferenceBundleRequestError(str(error)) from error
    normalized: list[dict[str, Any]] = []
    base_by_id = {int(item["catalog_id"]): item for item in base_products}
    for catalog_id in sorted(by_catalog_id):
        properties = by_catalog_id[catalog_id]
        observed = {
            "assessment_type": str(properties.get("asmt_type") or ""),
            "post_id": str(properties.get("post_id") or ""),
            "postfire_date": _date(properties.get("postfire_date")),
            "model": str(properties.get("model") or ""),
            "comment": str(properties.get("comment") or ""),
        }
        if observed != EXPECTED_ASSESSMENT_FIELDS[catalog_id]:
            raise CurrentReferenceBundleRequestError(
                f"assessment metadata drifted for catalog {catalog_id}"
            )
        base = base_by_id[catalog_id]
        caution = CAUTION_DETAILS.get(catalog_id)
        normalized.append(
            {
                "catalog_id": catalog_id,
                "map_id": int(base["map_id"]),
                "program": str(base["program"]),
                "event_id": str(base["event_id"]),
                "event_group_id": str(base["event_group_id"]),
                "display_name": str(base["display_name"]),
                "assessment_type": observed["assessment_type"],
                "post_id": observed["post_id"],
                "postfire_date": observed["postfire_date"] or None,
                "model": observed["model"] or None,
                "provider_comment_present": bool(observed["comment"]),
                "provider_comment_sha256": (
                    _sha256(observed["comment"].encode("utf-8"))
                    if observed["comment"]
                    else None
                ),
                "caution": caution,
            }
        )
    return normalized


def build_bundle_request_evidence(
    raw_metadata_response: bytes,
    raw_queue_response: bytes,
    *,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, Any]:
    products = normalize_assessment_metadata(raw_metadata_response)
    try:
        queue_payload = json.loads(raw_queue_response)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise CurrentReferenceBundleRequestError(
            "queue response is invalid JSON"
        ) from error
    if queue_payload != {"success": True}:
        raise CurrentReferenceBundleRequestError("official bundle request was not accepted")
    payload = request_payload()
    return {
        "report_id": REPORT_ID,
        "report_schema_version": REPORT_SCHEMA_VERSION,
        "report_version": REPORT_VERSION,
        "request_contract_version": REQUEST_CONTRACT_VERSION,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": TASK_ISSUE,
        "parent_issue": PARENT_ISSUE,
        "git_source_commit": git_source_commit,
        "software_version": SOFTWARE_VERSION,
        "provenance": {
            "aoi_version": "aoi-darlene3-model-v0.2.0",
            "target_version": "target-burn-scar-v0.2.0",
            "label_schema_version": "burn-scar-five-state-schema-v0.1.0",
            "dataset_version": None,
            "split_version": None,
            "baseline_version": None,
            "model_version": None,
        },
        "source": {
            "source_record_id": SOURCE_RECORD_ID,
            "terms_review_id": TERMS_REVIEW_ID,
            "metadata_endpoint": WFS_ENDPOINT,
            "metadata_request_url": full_inventory_request_url(),
            "metadata_response_bytes": len(raw_metadata_response),
            "metadata_response_sha256": _sha256(raw_metadata_response),
            "queue_endpoint": QUEUE_ENDPOINT,
            "queue_response_bytes": len(raw_queue_response),
            "queue_response_sha256": _sha256(raw_queue_response),
            "recipient": "WITHHELD_PRIVATE",
            "retrieval_channel": "WITHHELD_PRIVATE_PENDING_DELIVERY",
        },
        "request": {
            "accepted": True,
            "projection": "UTM",
            "standard_mapping_ids": list(MAPPING_IDS),
            "nonstandard_mapping_bundles": [list(item) for item in MAPPING_BUNDLES],
            "product_families": list(MAPPING_PRODUCTS),
            "product_family_count": len(MAPPING_PRODUCTS),
            "canonical_payload_sha256": _sha256(_canonical_bytes(payload)),
            "requested_catalog_product_count": 7,
        },
        "assessment_metadata": {
            "product_count": len(products),
            "caution_count": sum(item["caution"] is not None for item in products),
            "products": products,
        },
        "delivery_state": {
            "queue_accepted": True,
            "delivery_pending": True,
            "retrieval_message_received_by_this_run": False,
            "bundle_archives_received": 0,
            "bundle_bytes_received": 0,
            "bundle_terms_inspected": False,
            "bundle_structure_inspected": False,
            "bundle_pixels_inspected": False,
        },
        "label_state": {
            "burned_candidates": 6,
            "background_candidates": 0,
            "ignored_units": 50,
            "tepee_candidates": 0,
            "labels_promoted_by_this_run": 0,
        },
        "claim_boundaries": {
            "request_acceptance_is_delivery": False,
            "bundle_received_claimed": False,
            "bundle_fitness_claimed": False,
            "scientific_validation_claimed": False,
            "field_validation_claimed": False,
            "official_or_endorsed_status_claimed": False,
            "dataset_created": False,
            "model_trained": False,
        },
        "decision": DECISION,
        "warning": (
            "Experimental BurnLens CV evidence. Request acceptance is not bundle delivery or "
            "scientific fitness. Not official wildfire information or emergency guidance. "
            "Official sources govern."
        ),
    }


def _font(size: int, *, bold: bool = False) -> ImageFont.ImageFont:
    candidates = (
        ("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
        ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"),
    )
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


def render_png(report: dict[str, Any]) -> Image.Image:
    canvas = Image.new("RGB", (1800, 1400), "#091321")
    draw = ImageDraw.Draw(canvas)
    mint, amber, white, muted, panel = "#74e0b8", "#ffbd59", "#f5f7ff", "#b8c7da", "#152238"
    draw.text((86, 70), "BURNLENS · EXACT BUNDLE REQUEST", fill=mint, font=_font(24))
    draw.text((86, 128), "Official request accepted.", fill=white, font=_font(58, bold=True))
    draw.text((86, 204), "Delivery and pixel fitness remain pending.", fill=white, font=_font(58, bold=True))
    draw.rounded_rectangle((86, 310, 1714, 462), radius=22, fill=panel)
    draw.text((120, 340), "DECISION", fill=amber, font=_font(24))
    draw.text((120, 390), "Await exact delivery · defer labels, dataset, and model", fill=white, font=_font(32))
    cards = (
        ("7", "catalog products requested"),
        ("18", "applicable product families"),
        ("0", "bundle archives received"),
    )
    for index, (value, label) in enumerate(cards):
        left = 86 + index * 554
        draw.rounded_rectangle((left, 510, left + 520, 676), radius=18, fill=panel)
        draw.text((left + 30, 535), value, fill=mint, font=_font(48, bold=True))
        draw.text((left + 30, 606), label, fill=muted, font=_font(23))
    draw.text((86, 736), "BINDING PROVIDER CAUTIONS", fill=muted, font=_font(24))
    cautions = (
        ("DARLENE · RAVG", "Sparse/no tree cover lowers forest-model reliability."),
        ("TEPEE · RAVG", "Non-forest eastern cover is outside direct model applicability."),
        ("MCKAY · RAVG", "Early post-fire timing may overestimate open-canopy severity."),
        ("TEPEE · BAER", "Nonstandard legacy path requires content inspection."),
    )
    y = 792
    for title, detail in cautions:
        draw.text((100, y), title, fill=mint, font=_font(25, bold=True))
        draw.text((520, y), detail, fill=white, font=_font(24))
        y += 70
    draw.line((86, 1105, 1714, 1105), fill="#38516f", width=2)
    draw.text((86, 1150), "NEXT", fill=amber, font=_font(24))
    draw.text(
        (86, 1200),
        "Receive exact archives, inspect notices and structure, then compare pixels.",
        fill=white,
        font=_font(27),
    )
    draw.text(
        (86, 1300),
        "Experimental evidence · request acceptance is not delivery, validation, or official status.",
        fill=amber,
        font=_font(22),
    )
    return canvas


def render_html(report: dict[str, Any], *, image_name: str) -> str:
    caution_items = "".join(
        "<li><strong>{}</strong> — {} <em>{}</em></li>".format(
            html.escape(item["caution"]["code"]),
            html.escape(item["caution"]["summary"]),
            html.escape(item["caution"]["effect"]),
        )
        for item in report["assessment_metadata"]["products"]
        if item["caution"] is not None
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{REPORT_ID}</title><style>
body{{margin:0;background:#091321;color:#f5f7ff;font:18px/1.55 Arial,sans-serif}}main{{max-width:1080px;margin:auto;padding:48px 28px 80px}}
h1{{font-size:48px;line-height:1.08}}h2{{color:#74e0b8;margin-top:42px}}.warning{{border-left:5px solid #ffbd59;padding:16px 20px;background:#152238}}
.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}}.card{{background:#152238;padding:24px;border-radius:14px}}.metric{{display:block;color:#74e0b8;font-size:42px;font-weight:bold}}
img{{width:100%;height:auto;border:1px solid #38516f}}code{{overflow-wrap:anywhere}}@media(max-width:760px){{.grid{{grid-template-columns:1fr}}h1{{font-size:36px}}}}
</style></head><body><main>
<p style="color:#74e0b8">BurnLens · Phase Two · Objective Four</p>
<h1>Official bundle request accepted. Delivery remains pending.</h1>
<p class="warning">{report['warning']}</p>
<img src="{image_name}" width="1800" height="1400" alt="Bundle request evidence card with accepted request, pending delivery, and four provider cautions">
<div class="grid"><div class="card"><span class="metric">7</span>catalog products requested</div><div class="card"><span class="metric">18</span>product families</div><div class="card"><span class="metric">0</span>bundle archives received</div></div>
<h2>Exact request</h2><p>Six standard map IDs plus one explicit nonstandard BAER path were submitted through the current official viewer route in local UTM. Recipient and retrieval channel remain private.</p>
<p>Canonical payload SHA-256: <code>{report['request']['canonical_payload_sha256']}</code></p>
<h2>Provider cautions bind later fitness</h2><ul>{caution_items}</ul>
<h2>Next gate</h2><p>Receive and hash exact archives, inspect notices and marked non-USGS content, verify identity/structure/CRS/grid/nodata/class domains, and only then compare pixels with optical evidence and reviewer dispositions.</p>
<h2>Trace</h2><p>Run <code>{report['run_id']}</code>; source commit <code>{report['git_source_commit']}</code>; software {SOFTWARE_VERSION}; dataset/model remain null.</p>
</main></body></html>
"""


def write_bundle_request_evidence(
    report: dict[str, Any],
    *,
    json_path: Path,
    html_path: Path,
    png_path: Path,
) -> None:
    resolved = {path.resolve() for path in (json_path, html_path, png_path)}
    if len(resolved) != 3:
        raise CurrentReferenceBundleRequestError(
            "output paths must be distinct JSON, HTML, and PNG files"
        )
    for path in (json_path, html_path, png_path):
        path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    html_path.write_text(
        render_html(report, image_name=png_path.name),
        encoding="utf-8",
        newline="\n",
    )
    render_png(report).save(png_path, format="PNG", optimize=False)
