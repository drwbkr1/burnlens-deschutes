"""Fail-closed validation for provider delivery payloads.

The stable LP DAAC routes used by BurnLens can ultimately return an HTML login
page with a successful HTTP status. A filename suffix or status code is therefore
never sufficient evidence that provider data were acquired.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from html import escape
from pathlib import Path
import json
import re
import textwrap
from typing import Any, Iterable

from PIL import Image, ImageDraw, ImageFont


HDF5_MAGIC = b"\x89HDF\r\n\x1a\n"
HTML_PREFIXES = (b"<!doctype html", b"<html")
TITLE_PATTERN = re.compile(rb"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)


@dataclass(frozen=True)
class AssetSpec:
    role: str
    source_record_id: str
    collection: str
    native_id: str
    expected_filename: str
    stable_route: str
    minimum_size_bytes: int
    expected_signature: str = "HDF5/NetCDF-4"


def _read_prefix(path: Path, size: int = 4096) -> bytes:
    with path.open("rb") as handle:
        return handle.read(size)


def _html_title(prefix: bytes) -> str | None:
    match = TITLE_PATTERN.search(prefix)
    if not match:
        return None
    title = re.sub(rb"\s+", b" ", match.group(1)).strip()
    return title.decode("utf-8", errors="replace")[:160]


def _looks_like_html(prefix: bytes) -> bool:
    stripped = prefix.lstrip().lower()
    return stripped.startswith(HTML_PREFIXES) or b"<html" in stripped[:1024]


def inspect_payload(path: Path, spec: AssetSpec, http_status: int | None) -> dict[str, Any]:
    """Inspect a local response body without trusting its name or HTTP status."""

    if not path.exists() or not path.is_file():
        return {
            "role": spec.role,
            "source_record_id": spec.source_record_id,
            "collection": spec.collection,
            "native_id": spec.native_id,
            "expected_filename": spec.expected_filename,
            "stable_route": spec.stable_route,
            "http_status": http_status,
            "observed_bytes": 0,
            "observed_magic_hex": None,
            "observed_media_hint": "missing",
            "response_title": None,
            "expected_signature": spec.expected_signature,
            "minimum_size_bytes": spec.minimum_size_bytes,
            "accepted_as_source_asset": False,
            "sha256": None,
            "reason_codes": ["PAYLOAD_MISSING"],
        }

    observed_bytes = path.stat().st_size
    prefix = _read_prefix(path)
    observed_magic = prefix[:8]
    is_hdf5 = observed_magic == HDF5_MAGIC
    is_html = _looks_like_html(prefix)
    title = _html_title(prefix) if is_html else None

    reason_codes: list[str] = []
    if is_html:
        reason_codes.append("HTML_LOGIN_OR_ERROR_RESPONSE")
    if not is_hdf5:
        reason_codes.append("EXPECTED_SIGNATURE_MISSING")
    if observed_bytes < spec.minimum_size_bytes:
        reason_codes.append("PAYLOAD_BELOW_EXPECTED_MINIMUM")

    accepted = not reason_codes
    return {
        "role": spec.role,
        "source_record_id": spec.source_record_id,
        "collection": spec.collection,
        "native_id": spec.native_id,
        "expected_filename": spec.expected_filename,
        "stable_route": spec.stable_route,
        "http_status": http_status,
        "observed_bytes": observed_bytes,
        "observed_magic_hex": observed_magic.hex() if observed_magic else None,
        "observed_media_hint": "hdf5" if is_hdf5 else ("html" if is_html else "unknown"),
        "response_title": title,
        "expected_signature": spec.expected_signature,
        "minimum_size_bytes": spec.minimum_size_bytes,
        "accepted_as_source_asset": accepted,
        "sha256": _sha256(path) if accepted else None,
        "reason_codes": reason_codes or ["SOURCE_ASSET_ACCEPTED"],
    }


def _sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_report(
    observations: Iterable[dict[str, Any]],
    *,
    generated_at_utc: str,
    run_id: str,
) -> dict[str, Any]:
    items = list(observations)
    accepted = [item for item in items if item["accepted_as_source_asset"]]
    rejected = [item for item in items if not item["accepted_as_source_asset"]]
    all_rejections_are_login = bool(rejected) and all(
        "HTML_LOGIN_OR_ERROR_RESPONSE" in item.get("reason_codes", [])
        and item.get("response_title") == "Earthdata Login"
        for item in rejected
    )
    if not rejected:
        decision = "READY_FOR_FORMAT_INSPECTION"
        decision_detail = "All expected provider payloads passed signature and minimum-size gates."
        permitted_claims = [
            "The exact local payloads passed the BurnLens delivery-integrity precheck.",
            "Accepted payload checksums and byte counts are available for structural format inspection.",
        ]
    elif all_rejections_are_login:
        decision = "BLOCKED_OWNER_CREDENTIAL"
        decision_detail = "Both exact LP DAAC routes require an owner-supplied Earthdata Login credential before provider bytes can be inspected."
        permitted_claims = [
            "BurnLens fails closed when a provider route returns HTML instead of the expected data format.",
            "The exact LP DAAC delivery routes are credential-gated in the tested environment.",
        ]
    else:
        decision = "BLOCKED_PAYLOAD_INTEGRITY"
        decision_detail = "At least one required payload failed identity or integrity prechecks; diagnose the recorded reason codes before source registration."
        permitted_claims = [
            "BurnLens rejected one or more payloads that did not satisfy its delivery-integrity contract.",
        ]
    return {
        "report_id": "VIIRS-ACCESS-PRECHECK-2026-001",
        "schema_version": "0.1.0",
        "report_version": "viirs-access-precheck-v0.1.0",
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "task_issue": 317,
        "branch": "codex/p2o1-t03-viirs-inspection",
        "git_base_commit": "1858f3d5ad3c193f997bef4f9142c996e174af27",
        "application_version": None,
        "aoi_version": "aoi-darlene3-discovery-v0.1.0",
        "dataset_version": None,
        "label_schema_version": None,
        "baseline_version": None,
        "model_version": None,
        "observations": items,
        "retention": {
            "provider_source_asset_count": len(accepted),
            "provider_source_asset_bytes": sum(item["observed_bytes"] for item in accepted),
            "rejected_delivery_response_count": len(rejected),
            "rejected_delivery_response_bytes_retained": 0,
            "credentials_used": False,
            "signed_urls_retained": False,
        },
        "decision": decision,
        "decision_detail": decision_detail,
        "claims": {
            "permitted": permitted_claims,
            "prohibited": [
                "Provider pixels were inspected.",
                "A wildfire detection, label, paired source package, dataset, model, metric, or map exists.",
            ],
        },
        "limitations": [
            "HTTP status and filename suffix do not establish payload identity.",
            "This precheck does not inspect fire-mask, QA, or geolocation arrays.",
            "AOI-2026-001 remains a metadata-discovery envelope, not incident geometry or a final modeling AOI.",
        ],
        "source_precedence": "Official sources govern over every BurnLens-derived artifact.",
        "warning": "Experimental BurnLens CV output. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.",
    }


def write_report(report: dict[str, Any], json_path: Path, html_path: Path, png_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    html_path.write_text(render_html(report), encoding="utf-8")
    render_png(report, png_path)


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    return ImageFont.load_default(size=size)


def _wrapped(text: str, width: int) -> str:
    return "\n".join(textwrap.wrap(text, width=width, break_long_words=False))


def render_png(report: dict[str, Any], path: Path) -> None:
    """Render a deterministic visual evidence card from normalized report data."""

    canvas = Image.new("RGB", (1600, 1200), "#f4f1ea")
    draw = ImageDraw.Draw(canvas)
    ink = "#17211b"
    muted = "#556158"
    border = "#8c968e"
    card = "#ffffff"
    danger = "#f4b8a7"
    warning = "#fff0ac"
    blocked = report["decision"] != "READY_FOR_FORMAT_INSPECTION"
    hero = "Provider bytes\ndid not pass." if blocked else "Provider bytes\npassed precheck."
    status_heading = (
        "BLOCKED - OWNER CREDENTIAL REQUIRED"
        if report["decision"] == "BLOCKED_OWNER_CREDENTIAL"
        else ("BLOCKED - PAYLOAD INTEGRITY" if blocked else "READY - FORMAT INSPECTION")
    )
    status_fill = danger if blocked else "#c8ebd2"

    draw.text((90, 62), "PHASE TWO  /  ACCESS INTEGRITY", fill=muted, font=_font(24))
    draw.multiline_text((90, 112), hero, fill=ink, font=_font(72), spacing=4)

    draw.rounded_rectangle((90, 300, 1510, 410), radius=12, fill=warning, outline=ink, width=3)
    draw.text((120, 325), "EXPERIMENTAL - NOT OFFICIAL WILDFIRE INFORMATION", fill=ink, font=_font(26))
    draw.text(
        (120, 365),
        "Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.",
        fill=ink,
        font=_font(20),
    )

    draw.rounded_rectangle((90, 440, 1510, 575), radius=12, fill=status_fill, outline=ink, width=3)
    draw.text((120, 466), status_heading, fill=ink, font=_font(32))
    draw.multiline_text(
        (120, 515),
        _wrapped(report["decision_detail"], 92),
        fill=ink,
        font=_font(21),
        spacing=5,
    )

    metrics = [
        (str(report["retention"]["provider_source_asset_count"]), "accepted provider assets"),
        (str(report["retention"]["rejected_delivery_response_count"]), "rejected delivery responses"),
        ("0", "credentials used"),
    ]
    for index, (value, label) in enumerate(metrics):
        left = 90 + index * 480
        right = left + 450
        draw.rounded_rectangle((left, 610, right, 750), radius=10, fill=card, outline=border, width=2)
        draw.text((left + 28, 632), value, fill=ink, font=_font(52))
        draw.text((left + 28, 706), label, fill=muted, font=_font(20))

    draw.text((90, 805), "EXACT ROUTE RESULTS", fill=muted, font=_font(22))
    draw.line((90, 842, 1510, 842), fill=border, width=2)
    row_y = 865
    for item in report["observations"]:
        role = item["role"].replace("-", " ").title()
        result = "ACCEPTED: HDF5" if item["accepted_as_source_asset"] else f"REJECTED: {item['observed_media_hint'].upper()}"
        result_color = "#005b46" if item["accepted_as_source_asset"] else "#8b1e0e"
        draw.text((90, row_y), role, fill=ink, font=_font(23))
        draw.text((455, row_y), item["collection"], fill=ink, font=_font(23))
        draw.text((680, row_y), f"HTTP {item['http_status']}  ·  {item['observed_bytes']:,} bytes", fill=ink, font=_font(22))
        draw.text((1150, row_y), result, fill=result_color, font=_font(23))
        row_y += 62
        draw.line((90, row_y - 20, 1510, row_y - 20), fill="#d0d5d1", width=1)

    draw.rounded_rectangle((90, 1000, 1510, 1100), radius=10, fill=card, outline=border, width=2)
    draw.text((120, 1020), "WHAT THIS PROVES", fill=muted, font=_font(20))
    draw.text((120, 1056), "BurnLens fails closed on deceptive delivery responses. It does not prove a fire observation.", fill=ink, font=_font(22))

    draw.text((90, 1142), f"{report['run_id']}  ·  {report['report_version']}  ·  discovery AOI only", fill=muted, font=_font(18))
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path, format="PNG", optimize=False)


def render_html(report: dict[str, Any]) -> str:
    blocked = report["decision"] != "READY_FOR_FORMAT_INSPECTION"
    status_label = (
        "Blocked — credential required"
        if report["decision"] == "BLOCKED_OWNER_CREDENTIAL"
        else ("Blocked — payload integrity" if blocked else "Payloads accepted")
    )
    hero = "Provider bytes did not pass." if blocked else "Provider bytes passed precheck."
    rows = []
    for item in report["observations"]:
        result = "Rejected" if not item["accepted_as_source_asset"] else "Accepted"
        reasons = ", ".join(item["reason_codes"])
        rows.append(
            "<tr>"
            f"<th scope=\"row\">{escape(item['role'])}</th>"
            f"<td><code>{escape(item['collection'])}</code></td>"
            f"<td>{escape(str(item['http_status']))}</td>"
            f"<td>{escape(item['observed_media_hint'])}</td>"
            f"<td>{item['observed_bytes']:,}</td>"
            f"<td><strong>{result}</strong><br><small>{escape(reasons)}</small></td>"
            "</tr>"
        )
    sources = "".join(
        f"<li><a href=\"{escape(item['stable_route'])}\">{escape(item['collection'])} stable route</a> — <code>{escape(item['native_id'])}</code></li>"
        for item in report["observations"]
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>BurnLens VIIRS access precheck</title>
  <style>
    :root {{ color-scheme: light; font-family: Inter, ui-sans-serif, system-ui, sans-serif; background: #f4f1ea; color: #17211b; }}
    body {{ margin: 0; }}
    main {{ max-width: 72rem; margin: auto; padding: 2rem 1.25rem 4rem; }}
    .eyebrow {{ letter-spacing: .12em; text-transform: uppercase; font-size: .78rem; font-weight: 800; color: #5a645d; }}
    h1 {{ font-size: clamp(2rem, 5vw, 4.5rem); line-height: .96; max-width: 12ch; margin: .4rem 0 1rem; }}
    .warning, .status {{ border: 2px solid #17211b; padding: 1rem; margin: 1rem 0; box-shadow: .35rem .35rem 0 #17211b; }}
    .warning {{ background: #fff4c2; }}
    .status {{ background: {'#f8c6b8' if blocked else '#c8ebd2'}; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(13rem, 1fr)); gap: 1rem; margin: 1.5rem 0; }}
    .card {{ background: white; border: 1px solid #aab0ab; padding: 1rem; }}
    .metric {{ display: block; font-size: 2.2rem; font-weight: 850; }}
    table {{ border-collapse: collapse; width: 100%; background: white; margin: 1rem 0 2rem; }}
    caption {{ text-align: left; font-weight: 800; padding: .75rem 0; }}
    th, td {{ border: 1px solid #9aa19b; padding: .75rem; text-align: left; vertical-align: top; }}
    thead th {{ background: #dde5df; }}
    code {{ overflow-wrap: anywhere; }}
    a {{ color: #005b46; }}
    footer {{ border-top: 1px solid #9aa19b; margin-top: 2rem; padding-top: 1rem; color: #4d5750; }}
    @media (max-width: 48rem) {{ table, thead, tbody, tr, th, td {{ display: block; }} thead {{ position: absolute; left: -9999px; }} tr {{ border: 1px solid #9aa19b; margin-bottom: 1rem; }} th, td {{ border: 0; }} }}
  </style>
</head>
<body>
<main>
  <p class="eyebrow">Phase Two · access integrity · {escape(report['report_version'])}</p>
  <h1>{hero}</h1>
  <p class="warning"><strong>Use boundary:</strong> {escape(report['warning'])}</p>
  <section class="status" aria-labelledby="status-heading">
    <h2 id="status-heading">{status_label}</h2>
    <p>{escape(report['decision_detail'])}</p>
  </section>
  <section class="grid" aria-label="Precheck summary">
    <div class="card"><span class="metric">{report['retention']['provider_source_asset_count']}</span>accepted provider assets</div>
    <div class="card"><span class="metric">{report['retention']['rejected_delivery_response_count']}</span>rejected delivery responses</div>
    <div class="card"><span class="metric">0</span>credentials used</div>
  </section>
  <section aria-labelledby="observations-heading">
    <h2 id="observations-heading">Observed delivery responses</h2>
    <p>A successful HTTP status and expected filename are insufficient. BurnLens requires the native HDF5/NetCDF-4 signature and plausible size before registering provider bytes.</p>
    <table>
      <caption>Exact route results; response bodies are not retained</caption>
      <thead><tr><th>Role</th><th>Collection</th><th>HTTP</th><th>Observed</th><th>Bytes</th><th>Decision</th></tr></thead>
      <tbody>{''.join(rows)}</tbody>
    </table>
  </section>
  <section aria-labelledby="meaning-heading">
    <h2 id="meaning-heading">What this means</h2>
    <p>BurnLens has verified an access boundary, not a fire observation. No mask, QA field, geolocation array, Sentinel pixel, label, dataset, model, metric, or map was created.</p>
    <h3>Carried limitations</h3>
    <ul>{''.join(f'<li>{escape(item)}</li>' for item in report['limitations'])}</ul>
  </section>
  <section aria-labelledby="trace-heading">
    <h2 id="trace-heading">Traceability</h2>
    <dl>
      <dt>Run ID</dt><dd><code>{escape(report['run_id'])}</code></dd>
      <dt>Base commit</dt><dd><code>{escape(report['git_base_commit'])}</code></dd>
      <dt>AOI version</dt><dd><code>{escape(report['aoi_version'])}</code> — discovery only</dd>
      <dt>Dataset / label schema / model</dt><dd>Not created</dd>
    </dl>
    <h3>Stable source routes</h3><ul>{sources}</ul>
  </section>
  <footer>{escape(report['source_precedence'])} Generated {escape(report['generated_at_utc'])}.</footer>
</main>
</body>
</html>
"""
