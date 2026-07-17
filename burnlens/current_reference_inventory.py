"""Capture and render the current official cross-program burn reference inventory.

This module inventories exact BAER, RAVG, and MTBS catalog records for the
three frozen BurnLens events. It does not download product bundles, interpret
pixels, promote labels, create a dataset, or validate BurnLens scientifically.
"""

from __future__ import annotations

from collections import Counter
from hashlib import sha256
from html import escape
import json
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from PIL import Image, ImageDraw, ImageFont

from .provider_acquisition import USER_AGENT


SOFTWARE_VERSION = "0.21.0"
REPORT_ID = "CROSS-EVENT-REFERENCE-INVENTORY-2026-001"
REPORT_SCHEMA_VERSION = "0.1.0"
REPORT_VERSION = "cross-event-current-reference-inventory-v0.1.0"
INVENTORY_CONTRACT_VERSION = "cross-event-current-reference-inventory-contract-v0.1.0"
SOURCE_RECORD_ID = "SOURCE-2026-014"
TERMS_REVIEW_ID = "TERMS-2026-009"
TASK_ISSUE = 411
WFS_ENDPOINT = "https://edcintl.cr.usgs.gov/geoserver/wfs"
VIEWER_URL = "https://burnseverity.cr.usgs.gov/viewer/"
PRODUCT_URL = "https://burnseverity.cr.usgs.gov/products/mtbs"
RELEASE_URL = "https://burnseverity.cr.usgs.gov/node/53"
DIRECT_DOWNLOAD_URL = "https://burnseverity.cr.usgs.gov/direct-download"
USGS_PUBLIC_DOMAIN_URL = "https://www.usgs.gov/faqs/are-usgs-reportspublications-copyrighted"
WARNING = (
    "Experimental BurnLens CV evidence. Not official wildfire information. "
    "Not emergency guidance. Not evacuation, routing, tactical, or "
    "incident-command support. Official sources govern."
)
DECISION = "ACQUIRE_CURRENT_CROSS_PROGRAM_REFERENCE_BUNDLES_DEFER_LABELS_DATASET_MODEL"
MAX_RESPONSE_BYTES = 2 * 1024 * 1024

EVENTS = {
    "OR4364712147820240625": {
        "event_group_id": "event-darlene3-or-2024",
        "display_name": "Darlene 3",
    },
    "OR4375212142520170829": {
        "event_group_id": "event-mckay-1035-ne-2017",
        "display_name": "McKay 1035 NE",
    },
    "OR4383912111420180907": {
        "event_group_id": "event-tepee-1144-ne-2018",
        "display_name": "Tepee 1144 NE",
    },
}

# Exact catalog identities are a drift alarm, not an assertion about product
# pixel fitness. A changed identity requires deliberate inspection.
EXPECTED_PRODUCTS = (
    {
        "catalog_id": 15933,
        "map_id": 10030231,
        "program": "BAER",
        "incident_name": "0289 NE DARLENE 3",
        "event_id": "OR4364712147820240625",
        "ignition_date": "2024-06-25",
        "boundary_acres": 3911,
        "nonstandard": False,
    },
    {
        "catalog_id": 30012,
        "map_id": 10030383,
        "program": "RAVG",
        "incident_name": "0289 NE DARLENE 3",
        "event_id": "OR4364712147820240625",
        "ignition_date": "2024-06-25",
        "boundary_acres": 3905,
        "nonstandard": False,
    },
    {
        "catalog_id": 850,
        "map_id": 10007931,
        "program": "MTBS",
        "incident_name": "MCKAY 1035 NE",
        "event_id": "OR4375212142520170829",
        "ignition_date": "2017-08-29",
        "boundary_acres": 1221,
        "nonstandard": False,
    },
    {
        "catalog_id": 10452,
        "map_id": 10004989,
        "program": "RAVG",
        "incident_name": "MCKAY 1035 NE",
        "event_id": "OR4375212142520170829",
        "ignition_date": "2017-08-29",
        "boundary_acres": 1221,
        "nonstandard": False,
    },
    {
        "catalog_id": 52523,
        "map_id": 0,
        "program": "BAER",
        "incident_name": "TEPEE 1144 NE",
        "event_id": "OR4383912111420180907",
        "ignition_date": "2018-07-09",
        "boundary_acres": 3897,
        "nonstandard": True,
    },
    {
        "catalog_id": 23539,
        "map_id": 10011986,
        "program": "MTBS",
        "incident_name": "TEPEE 1144 NE",
        "event_id": "OR4383912111420180907",
        "ignition_date": "2018-09-07",
        "boundary_acres": 2135,
        "nonstandard": False,
    },
    {
        "catalog_id": 3238,
        "map_id": 10008484,
        "program": "RAVG",
        "incident_name": "TEPEE 1144 NE",
        "event_id": "OR4383912111420180907",
        "ignition_date": "2018-09-07",
        "boundary_acres": 2029,
        "nonstandard": False,
    },
)


class CurrentReferenceInventoryError(RuntimeError):
    """A deterministic, secret-free inventory failure."""


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _canonical_sha256(value: Any) -> str:
    return sha256(_canonical_bytes(value)).hexdigest()


def _write_utf8_lf(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8"))


def inventory_request_url() -> str:
    event_filter = ",".join(f"'{event_id}'" for event_id in EVENTS)
    params = (
        ("service", "WFS"),
        ("version", "2.0.0"),
        ("request", "GetFeature"),
        ("typeNames", "mtbs:fire_polygons"),
        ("outputFormat", "application/json"),
        (
            "propertyName",
            "id,map_id,map_prog,incid_name,event_id,ig_date,burnbndac,nonstandard",
        ),
        ("cql_filter", f"event_id IN ({event_filter})"),
    )
    return f"{WFS_ENDPOINT}?{urlencode(params)}"


def fetch_inventory_response(*, timeout_seconds: int = 60) -> bytes:
    request = Request(
        inventory_request_url(),
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    )
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            payload = response.read(MAX_RESPONSE_BYTES + 1)
    except OSError as error:
        raise CurrentReferenceInventoryError(
            "official burn-severity inventory endpoint is unavailable"
        ) from error
    if len(payload) > MAX_RESPONSE_BYTES:
        raise CurrentReferenceInventoryError("inventory response exceeds bounded size")
    return payload


def normalize_inventory(raw_response: bytes) -> list[dict[str, Any]]:
    try:
        payload = json.loads(raw_response.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise CurrentReferenceInventoryError("inventory response is not valid UTF-8 JSON") from error
    if not isinstance(payload, dict) or payload.get("type") != "FeatureCollection":
        raise CurrentReferenceInventoryError("inventory response is not a GeoJSON FeatureCollection")
    features = payload.get("features")
    if not isinstance(features, list):
        raise CurrentReferenceInventoryError("inventory response has no feature list")

    products: list[dict[str, Any]] = []
    for feature in features:
        if not isinstance(feature, dict) or feature.get("geometry") is not None:
            raise CurrentReferenceInventoryError("inventory response violated property-only contract")
        properties = feature.get("properties")
        if not isinstance(properties, dict):
            raise CurrentReferenceInventoryError("inventory feature properties are missing")
        date = properties.get("ig_date")
        if not isinstance(date, str) or len(date) < 10:
            raise CurrentReferenceInventoryError("inventory ignition date is invalid")
        product = {
            "catalog_id": properties.get("id"),
            "map_id": properties.get("map_id"),
            "program": properties.get("map_prog"),
            "incident_name": properties.get("incid_name"),
            "event_id": properties.get("event_id"),
            "ignition_date": date[:10],
            "boundary_acres": properties.get("burnbndac"),
            "nonstandard": properties.get("nonstandard"),
        }
        if product["event_id"] not in EVENTS:
            raise CurrentReferenceInventoryError("inventory returned an unexpected event")
        if product["program"] not in {"BAER", "MTBS", "RAVG"}:
            raise CurrentReferenceInventoryError("inventory returned an unexpected program")
        if (
            not isinstance(product["catalog_id"], int)
            or not isinstance(product["map_id"], int)
            or not isinstance(product["boundary_acres"], int)
            or not isinstance(product["nonstandard"], bool)
            or not isinstance(product["incident_name"], str)
        ):
            raise CurrentReferenceInventoryError("inventory field type contract failed")
        product.update(EVENTS[product["event_id"]])
        products.append(product)

    products.sort(key=lambda item: (item["event_id"], item["program"], item["catalog_id"]))
    expected = [dict(item) for item in EXPECTED_PRODUCTS]
    expected.sort(key=lambda item: (item["event_id"], item["program"], item["catalog_id"]))
    observed_contract = [
        {key: item[key] for key in EXPECTED_PRODUCTS[0]}
        for item in products
    ]
    if observed_contract != expected:
        raise CurrentReferenceInventoryError(
            "current catalog identities differ from the reviewed seven-product contract"
        )
    if len({item["catalog_id"] for item in products}) != len(products):
        raise CurrentReferenceInventoryError("inventory contains duplicate catalog identities")
    return products


def build_current_reference_inventory(
    raw_response: bytes,
    *,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, Any]:
    products = normalize_inventory(raw_response)
    by_event = []
    for event_id, event in EVENTS.items():
        event_products = [item for item in products if item["event_id"] == event_id]
        by_event.append(
            {
                **event,
                "event_id": event_id,
                "programs": sorted(item["program"] for item in event_products),
                "product_count": len(event_products),
                "has_cross_program_reference": len({item["program"] for item in event_products}) >= 2,
            }
        )
    program_counts = Counter(item["program"] for item in products)
    return {
        "report_id": REPORT_ID,
        "report_schema_version": REPORT_SCHEMA_VERSION,
        "report_version": REPORT_VERSION,
        "inventory_contract_version": INVENTORY_CONTRACT_VERSION,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": TASK_ISSUE,
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
            "organization": (
                "Burned Area Emergency Response, Rapid Assessment of Vegetation "
                "Condition after Wildfire, and Monitoring Trends in Burn Severity; "
                "U.S. Geological Survey and USDA Forest Service"
            ),
            "endpoint": WFS_ENDPOINT,
            "request_url": inventory_request_url(),
            "raw_response_bytes": len(raw_response),
            "raw_response_sha256": sha256(raw_response).hexdigest(),
            "normalized_products_sha256": _canonical_sha256(products),
            "access_route": "current official Burn Severity Portal WFS; public; no credential",
        },
        "official_currentness_evidence": {
            "release_announcement": RELEASE_URL,
            "product_page": PRODUCT_URL,
            "viewer": VIEWER_URL,
            "direct_download": DIRECT_DOWNLOAD_URL,
            "accessed_utc_date": generated_at_utc[:10],
            "finding": (
                "The official 2026 portal release says the archive was reprocessed "
                "in late 2025 with contemporary calibration and distribution changes. "
                "Current product identities must therefore govern new evidence acquisition."
            ),
        },
        "inventory": {
            "event_count": len(by_event),
            "product_count": len(products),
            "program_counts": dict(sorted(program_counts.items())),
            "all_events_have_cross_program_reference": all(
                item["has_cross_program_reference"] for item in by_event
            ),
            "events": by_event,
            "products": products,
        },
        "legacy_reference_boundary": {
            "source_record_id": "SOURCE-2026-013",
            "package_id": "burnlens-mtbs-cross-event-reference-v0.1.0",
            "state": "FROZEN_REPRODUCIBLE_HISTORICAL_EVIDENCE_NOT_CURRENT_FOR_NEW_LABEL_PROMOTION",
            "scope": (
                "The two 2025-era annual ImageServer clips remain valid provenance "
                "for the already-published proposal. They are not silently replaced "
                "and do not establish current product fitness."
            ),
        },
        "promotion_gates": [
            "receive and preserve exact current product-bundle bytes",
            "resolve bundle-specific attribution, redistribution, and non-USGS content terms",
            "inspect product identity, metadata, CRS, grid, nodata, class domain, and masks",
            "compare current cross-program pixels with optical evidence and reviewer dispositions",
            "publish a rendered scientific-fitness decision before promoting any label",
        ],
        "claim_boundaries": {
            "inventory_only": True,
            "product_bundles_downloaded_by_this_run": False,
            "pixels_inspected_by_this_run": False,
            "labels_promoted_by_this_run": False,
            "dataset_created": False,
            "model_trained": False,
            "scientific_validation_claimed": False,
            "field_validation_claimed": False,
            "official_or_endorsed_status_claimed": False,
        },
        "decision": DECISION,
        "warning": WARNING,
    }


def _html(report: dict[str, Any]) -> str:
    rows = []
    for item in report["inventory"]["products"]:
        rows.append(
            "<tr>"
            f"<td>{escape(item['display_name'])}</td>"
            f"<td>{escape(item['program'])}</td>"
            f"<td>{item['catalog_id']}</td>"
            f"<td>{item['map_id']}</td>"
            f"<td>{escape(item['ignition_date'])}</td>"
            f"<td>{item['boundary_acres']:,}</td>"
            f"<td>{'yes' if item['nonstandard'] else 'no'}</td>"
            "</tr>"
        )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{REPORT_ID}</title>
<style>
body{{margin:0;background:#0b1220;color:#e9eef7;font:16px/1.5 system-ui,sans-serif}}
main{{max-width:1180px;margin:auto;padding:48px 28px 70px}} .eyebrow{{color:#79d3a9;font-weight:700}}
h1{{font-size:42px;line-height:1.08;margin:.25em 0}} h2{{margin-top:38px}}
.decision{{border-left:6px solid #f0b35a;background:#172237;padding:18px 22px;margin:26px 0}}
.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}} .card{{background:#131e31;padding:18px;border-radius:8px}}
.value{{font-size:34px;font-weight:750;color:#79d3a9}} table{{width:100%;border-collapse:collapse;background:#131e31}}
th,td{{text-align:left;padding:11px;border-bottom:1px solid #30405a}} th{{color:#a9b8ce}}
code{{overflow-wrap:anywhere}} .warning{{color:#f5cc8e}} @media(max-width:760px){{.grid{{grid-template-columns:1fr}}table{{font-size:13px}}}}
</style></head><body><main>
<div class="eyebrow">BurnLens · current official reference inventory · issue #{report['task_issue']}</div>
<h1>Cross-program reference exists. Promotion remains closed.</h1>
<p>Run <code>{escape(report['run_id'])}</code> · BurnLens {report['software_version']} · {escape(report['generated_at_utc'])}</p>
<div class="decision"><strong>{escape(report['decision'])}</strong><br>
The current official catalog passes the exact seven-product identity gate. Product bytes and pixels have not yet passed fitness review.</div>
<div class="grid"><div class="card"><div class="value">3/3</div>events have ≥2 programs</div>
<div class="card"><div class="value">7</div>exact current products</div>
<div class="card"><div class="value">0</div>labels promoted</div></div>
<h2>Exact current catalog identities</h2>
<table><thead><tr><th>Event</th><th>Program</th><th>Catalog</th><th>Map</th><th>Date</th><th>Acres</th><th>Nonstandard</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table>
<h2>Why the old reference cannot govern new promotion</h2>
<p>{escape(report['official_currentness_evidence']['finding'])}</p>
<p><code>SOURCE-2026-013</code> remains frozen, reproducible historical evidence for the published proposal. It is not current product-fitness evidence.</p>
<h2>Required next gates</h2><ol>{''.join(f"<li>{escape(item)}</li>" for item in report['promotion_gates'])}</ol>
<p class="warning">{escape(report['warning'])}</p>
</main></body></html>
"""


def _png(report: dict[str, Any]) -> Image.Image:
    image = Image.new("RGB", (1800, 1340), "#0b1220")
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("arial.ttf", 31)
    small = ImageFont.truetype("arial.ttf", 24)
    title = ImageFont.truetype("arialbd.ttf", 57)
    big = ImageFont.truetype("arialbd.ttf", 52)
    draw.text((86, 72), "BURNLENS · CURRENT OFFICIAL REFERENCE INVENTORY", fill="#79d3a9", font=small)
    draw.text((86, 125), "Cross-program reference exists.", fill="#f5f7fb", font=title)
    draw.text((86, 195), "Label promotion remains closed.", fill="#f5f7fb", font=title)
    draw.rounded_rectangle((86, 295, 1714, 435), 18, fill="#172237")
    draw.text((120, 326), "DECISION", fill="#f0b35a", font=small)
    draw.text((120, 371), "Acquire current bundles · defer labels, dataset, and model", fill="#f5f7fb", font=font)
    cards = ((86, "3/3", "events with cross-program reference"), (640, "7", "exact current catalog products"), (1194, "0", "labels promoted"))
    for x, value, label in cards:
        draw.rounded_rectangle((x, 485, x + 520, 650), 16, fill="#131e31")
        draw.text((x + 28, 505), value, fill="#79d3a9", font=big)
        draw.text((x + 28, 578), label, fill="#c8d2e1", font=small)
    draw.text((86, 715), "CURRENT PRODUCT IDENTITIES", fill="#a9b8ce", font=small)
    y = 770
    for event in report["inventory"]["events"]:
        programs = "  ·  ".join(event["programs"])
        draw.text((100, y), event["display_name"], fill="#f5f7fb", font=font)
        draw.text((650, y), programs, fill="#79d3a9", font=font)
        y += 62
    draw.line((86, 985, 1714, 985), fill="#30405a", width=2)
    draw.text((86, 1025), "FRESHNESS BOUNDARY", fill="#f0b35a", font=small)
    lines = (
        "The official archive was reprocessed and redistributed in late 2025.",
        "SOURCE-2026-013 remains historical provenance, not current fitness evidence.",
        "Next: preserve exact bundles, inspect pixels, and publish a fitness decision.",
    )
    y = 1070
    for line in lines:
        draw.text((100, y), line, fill="#dbe3ef", font=small)
        y += 46
    warning_lines = (
        "Experimental BurnLens CV evidence. Not official wildfire information or emergency guidance.",
        "Not evacuation, routing, tactical, or incident-command support. Official sources govern.",
    )
    draw.text((86, 1232), warning_lines[0], fill="#f5cc8e", font=small)
    draw.text((86, 1273), warning_lines[1], fill="#f5cc8e", font=small)
    return image


def write_current_reference_inventory(
    report: dict[str, Any],
    *,
    json_path: Path,
    html_path: Path,
    png_path: Path,
) -> None:
    expected = {json_path.with_suffix(".json"), html_path.with_suffix(".html"), png_path.with_suffix(".png")}
    if len(expected) != 3:
        raise CurrentReferenceInventoryError("output paths must be distinct JSON, HTML, and PNG files")
    _write_utf8_lf(json_path, json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    _write_utf8_lf(html_path, _html(report))
    png_path.parent.mkdir(parents=True, exist_ok=True)
    _png(report).save(png_path, format="PNG", optimize=True)
