"""Build the self-contained Phase Four Ward Creek evidence interface."""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from html import escape
import json
import os
from pathlib import Path
import re
import subprocess
from typing import Any, Callable, Iterable


INTERFACE_VERSION = "burnlens-phase-four-interface-v0.1.0"
INTERFACE_ID = "PHASE-FOUR-EVIDENCE-INTERFACE-2026-001"
SOFTWARE_VERSION = "0.54.0"
RUN_ID_PATTERN = re.compile(
    r"^BL-[0-9]{4}-[0-9]{2}-[0-9]{2}-p4o1-t01-u06-interface-r[0-9]{3}$"
)
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")
OUTPUT_HTML = f"{INTERFACE_ID}.html"
OUTPUT_JSON = f"{INTERFACE_ID}.json"
CONTEXT_BOUNDS_UTM = (657220.0, 4968520.0, 681800.0, 4991800.0)
PATCH_BOUNDS_UTM = {
    "WCP-001": (667220.0, 4978520.0, 668500.0, 4979800.0),
    "WCP-002": (670520.0, 4980520.0, 671800.0, 4981800.0),
}
U03_RUN = Path(
    "runs/phase-four/BL-2026-07-26-p4o1-t01-u03-geospatial-r003"
)
U05_RUN = Path(
    "runs/phase-four/BL-2026-07-26-p4o1-t01-u05-overlay-r001"
)
BOUND_INPUTS = (
    (
        Path(
            "records/phase-four/contracts/"
            "PHASE-FOUR-INTEGRATION-CONTRACT-2026-001.json"
        ),
        19991,
        "a50966b3f9d082bc5700c001e3f3d3f0dbc372ad775d3e95ddcec8261ad631ec",
        "frozen Phase Four integration contract",
    ),
    (
        Path(
            "records/phase-four/geospatial/"
            "PHASE-FOUR-GEOSPATIAL-RECORD-2026-001.json"
        ),
        9119,
        "002860f20df5a2441e71e4b5b27dffdc238c0269a67493900d847e9af9b2e5c9",
        "accepted Phase Four geospatial record",
    ),
    (
        Path(
            "records/phase-four/overlays/"
            "PHASE-FOUR-OVERLAY-RECORD-2026-001.json"
        ),
        8555,
        "48556442dd519fe7300f8793b47778ac628fc8c16fbb61bda85cde57cf0bbd59",
        "accepted Phase Four overlay record",
    ),
    (
        U03_RUN / "vectors/rbr-accepted-polygons.geojson",
        312627,
        "31ce37dd18e608881bc151103217f5e205a6c713175556359e2662a118f5e8af",
        "accepted RBR web vector",
    ),
    (
        U03_RUN / "patches/WCP-001/unet-binary-diagnostic.tif",
        1142,
        "e1d4b4b4e9d46db8d501a161426ddd7ce8c21f2cf57be430d542250df221acb5",
        "WCP-001 rejected U-Net diagnostic raster",
    ),
    (
        U03_RUN / "patches/WCP-002/unet-binary-diagnostic.tif",
        1306,
        "c9302441fde15574ac3745b40033352a11f9b19289681c4c1e2b0bd0b08ab297",
        "WCP-002 rejected U-Net diagnostic raster",
    ),
    (
        U05_RUN / "OVERLAY-MANIFEST.json",
        8088,
        "cf235bee576b4a1c0158a6e68511ce1ef0751061eb2dd8e3e666ef35fd7bbce8",
        "accepted U05 overlay manifest",
    ),
    (
        U05_RUN / "analysis/OVERLAY-SUMMARY.json",
        8081,
        "f60f43d48913e8c8431a76783bb9c8713fbb9b465f26b473a97ec00b3d41135d",
        "accepted U05 deterministic summary",
    ),
    (
        U05_RUN / "context/roads.geojson",
        348717,
        "8f94577b5ce12db980b489954febf7c1ea1f6830e3c63c357deb763a0810c004",
        "bounded TNM road context",
    ),
    (
        U05_RUN / "context/facilities.geojson",
        4529,
        "ae565fafd92afac99c37c48a727d0e86b2c995ec83f29fa895d24c15d478ca1b",
        "bounded TNM facility context",
    ),
    (
        U05_RUN / "context/blm-boundary.geojson",
        36884,
        "6c2b64a0dee303f3258748f5500a31e8797139d140341565a1e7146c287d69c2",
        "bounded TNM BLM context",
    ),
    (
        U05_RUN / "reference/mtbs-ward-creek-boundary.geojson",
        267090,
        "b9c9ebc134811f1ce93194716c2c46a49bac751773bfa19da2d94f04d9fc3f14",
        "exact governed Ward Creek MTBS web boundary",
    ),
)


class PhaseFourInterfaceError(RuntimeError):
    """The U06 interface build or custody gate failed."""


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(8 * 1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(
        "utf-8"
    )


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PhaseFourInterfaceError(f"invalid JSON: {path}") from exc
    if not isinstance(value, dict):
        raise PhaseFourInterfaceError(f"JSON object required: {path}")
    return value


def _validate_inputs(root: Path) -> dict[str, dict[str, Any]]:
    receipts = []
    by_role: dict[str, Path] = {}
    for relative, expected_bytes, expected_hash, role in BOUND_INPUTS:
        path = root / relative
        if not path.is_file():
            raise PhaseFourInterfaceError(f"bound input missing: {relative}")
        if path.stat().st_size != expected_bytes:
            raise PhaseFourInterfaceError(f"bound input size drift: {relative}")
        if _sha256_file(path) != expected_hash:
            raise PhaseFourInterfaceError(f"bound input hash drift: {relative}")
        by_role[role] = path
        receipts.append(
            {
                "path": relative.as_posix(),
                "bytes": expected_bytes,
                "sha256": expected_hash,
                "role": role,
                "tracked": not relative.as_posix().startswith("runs/"),
            }
        )
    contract = _load_json(by_role["frozen Phase Four integration contract"])
    geospatial = _load_json(by_role["accepted Phase Four geospatial record"])
    overlay_record = _load_json(by_role["accepted Phase Four overlay record"])
    overlay = _load_json(by_role["accepted U05 overlay manifest"])
    summary = _load_json(by_role["accepted U05 deterministic summary"])
    if (
        contract.get("route")
        != "baseline-primary-with-rejected-model-diagnostic"
        or contract.get("analytical_methods", {})
        .get("rejected_diagnostic", {})
        .get("outperformed_rbr")
        is not False
        or contract.get("boundaries", {}).get("phase_3b_created") is not False
    ):
        raise PhaseFourInterfaceError("Phase Four contract drift")
    if (
        geospatial.get("disposition") != "pass"
        or overlay_record.get("disposition") != "pass"
        or overlay.get("disposition")
        != "pass-overlay-summary-pending-interface"
        or overlay.get("boundaries", {}).get("unet_used_for_measurement")
        is not False
        or summary.get("state") != "accepted-baseline"
    ):
        raise PhaseFourInterfaceError("accepted U03/U05 state drift")
    return {
        "receipts": {"items": receipts},
        "paths": {role: path for role, path in by_role.items()},
        "contract": contract,
        "geospatial": geospatial,
        "overlay_record": overlay_record,
        "overlay": overlay,
        "summary": summary,
    }


def _features(path: Path) -> list[dict[str, Any]]:
    value = _load_json(path)
    if value.get("type") != "FeatureCollection":
        raise PhaseFourInterfaceError(f"FeatureCollection required: {path}")
    features = value.get("features")
    if not isinstance(features, list) or not features:
        raise PhaseFourInterfaceError(f"nonempty features required: {path}")
    return features


def _diagnostic_features(root: Path) -> list[dict[str, Any]]:
    import rasterio
    from rasterio.features import shapes
    from rasterio.warp import transform_geom

    result = []
    for candidate_id in PATCH_BOUNDS_UTM:
        relative = (
            U03_RUN
            / f"patches/{candidate_id}/unet-binary-diagnostic.tif"
        )
        with rasterio.open(root / relative) as dataset:
            if (
                dataset.crs is None
                or dataset.crs.to_string() != "EPSG:32610"
                or dataset.shape != (64, 64)
                or dataset.tags().get("ANALYTICAL_STATUS")
                != "rejected-model-diagnostic"
            ):
                raise PhaseFourInterfaceError(
                    f"rejected diagnostic raster drift: {candidate_id}"
                )
            array = dataset.read(1)
            if set(array.reshape(-1).tolist()) - {0, 1}:
                raise PhaseFourInterfaceError(
                    f"rejected diagnostic domain drift: {candidate_id}"
                )
            geometries = [
                transform_geom(
                    dataset.crs,
                    "EPSG:4326",
                    geometry,
                    precision=8,
                )
                for geometry, value in shapes(
                    array,
                    mask=array == 1,
                    transform=dataset.transform,
                    connectivity=4,
                )
                if int(value) == 1
            ]
        result.extend(
            {
                "type": "Feature",
                "id": f"{candidate_id}-UNET-{index:03d}",
                "geometry": geometry,
                "properties": {
                    "candidate_id": candidate_id,
                    "analytical_status": "rejected-model-diagnostic",
                },
            }
            for index, geometry in enumerate(geometries, 1)
        )
    if not result:
        raise PhaseFourInterfaceError("rejected diagnostic vector is empty")
    return result


def _all_coordinates(geometry: dict[str, Any]) -> Iterable[tuple[float, float]]:
    coordinates = geometry.get("coordinates")
    if geometry.get("type") == "Point":
        yield float(coordinates[0]), float(coordinates[1])
        return

    def walk(value: Any) -> Iterable[tuple[float, float]]:
        if (
            isinstance(value, list)
            and len(value) >= 2
            and all(isinstance(item, (int, float)) for item in value[:2])
        ):
            yield float(value[0]), float(value[1])
            return
        if isinstance(value, list):
            for item in value:
                yield from walk(item)

    yield from walk(coordinates)


def _projector(
    bounds: tuple[float, float, float, float],
) -> Callable[[float, float], tuple[float, float]]:
    minx, miny, maxx, maxy = bounds

    def project(x: float, y: float) -> tuple[float, float]:
        return (
            24.0 + (x - minx) / (maxx - minx) * 952.0,
            636.0 - (y - miny) / (maxy - miny) * 612.0,
        )

    return project


def _path_data(
    geometry: dict[str, Any],
    project: Callable[[float, float], tuple[float, float]],
) -> str:
    kind = geometry.get("type")
    coordinates = geometry.get("coordinates")

    def line(points: list[Any], *, close: bool) -> str:
        if not points:
            return ""
        projected = [project(float(x), float(y)) for x, y, *_ in points]
        command = "M" + " ".join(
            f"{x:.2f},{y:.2f}" if index == 0 else f"L{x:.2f},{y:.2f}"
            for index, (x, y) in enumerate(projected)
        )
        return command + ("Z" if close else "")

    if kind == "LineString":
        return line(coordinates, close=False)
    if kind == "MultiLineString":
        return "".join(line(item, close=False) for item in coordinates)
    if kind == "Polygon":
        return "".join(line(ring, close=True) for ring in coordinates)
    if kind == "MultiPolygon":
        return "".join(
            line(ring, close=True)
            for polygon in coordinates
            for ring in polygon
        )
    raise PhaseFourInterfaceError(f"unsupported SVG geometry: {kind}")


def _svg_layer(
    features: list[dict[str, Any]],
    project: Callable[[float, float], tuple[float, float]],
    *,
    layer_id: str,
    css_class: str,
) -> str:
    markup = []
    for feature in features:
        geometry = feature.get("geometry")
        if not isinstance(geometry, dict):
            raise PhaseFourInterfaceError(f"invalid geometry in {layer_id}")
        if geometry.get("type") == "Point":
            x, y = project(*next(iter(_all_coordinates(geometry))))
            markup.append(
                f'<circle class="{css_class}" cx="{x:.2f}" cy="{y:.2f}" '
                'r="5"><title>Selected official-context facility point</title></circle>'
            )
        else:
            path = _path_data(geometry, project)
            if not path:
                raise PhaseFourInterfaceError(f"empty path in {layer_id}")
            markup.append(f'<path class="{css_class}" d="{path}"/>')
    return f'<g id="{layer_id}" data-layer="{layer_id}">' + "".join(markup) + "</g>"


def _patch_markup(
    project: Callable[[float, float], tuple[float, float]]
) -> tuple[str, dict[str, str]]:
    from pyproj import Transformer

    transformer = Transformer.from_crs(
        "EPSG:32610", "EPSG:4326", always_xy=True
    )
    items = []
    views = {"all": "0 0 1000 660"}
    for candidate_id, (left, bottom, right, top) in PATCH_BOUNDS_UTM.items():
        lon1, lat1 = transformer.transform(left, bottom)
        lon2, lat2 = transformer.transform(right, top)
        x1, y1 = project(lon1, lat2)
        x2, y2 = project(lon2, lat1)
        x = min(x1, x2)
        y = min(y1, y2)
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        pad = 32
        views[candidate_id] = (
            f"{x - pad:.2f} {y - pad:.2f} "
            f"{width + 2 * pad:.2f} {height + 2 * pad:.2f}"
        )
        items.append(
            f'<rect class="patch" x="{x:.2f}" y="{y:.2f}" '
            f'width="{width:.2f}" height="{height:.2f}"/>'
            f'<text class="patch-label" x="{x + 7:.2f}" '
            f'y="{y + 20:.2f}">{candidate_id}</text>'
        )
    return '<g id="patches">' + "".join(items) + "</g>", views


def _map_markup(
    root: Path, input_state: dict[str, Any]
) -> tuple[str, dict[str, Any]]:
    from pyproj import Transformer

    paths = input_state["paths"]
    accepted = _features(paths["accepted RBR web vector"])
    diagnostic = _diagnostic_features(root)
    mtbs = _features(paths["exact governed Ward Creek MTBS web boundary"])
    roads = _features(paths["bounded TNM road context"])
    facilities = _features(paths["bounded TNM facility context"])
    blm = _features(paths["bounded TNM BLM context"])
    transformer = Transformer.from_crs(
        "EPSG:32610", "EPSG:4326", always_xy=True
    )
    left, bottom, right, top = CONTEXT_BOUNDS_UTM
    lon1, lat1 = transformer.transform(left, bottom)
    lon2, lat2 = transformer.transform(right, top)
    bounds = (
        min(lon1, lon2),
        min(lat1, lat2),
        max(lon1, lon2),
        max(lat1, lat2),
    )
    project = _projector(bounds)
    patch_markup, views = _patch_markup(project)
    layers = [
        _svg_layer(
            accepted,
            project,
            layer_id="accepted-rbr",
            css_class="accepted-rbr",
        ),
        _svg_layer(
            diagnostic,
            project,
            layer_id="rejected-unet",
            css_class="rejected-unet",
        ),
        _svg_layer(
            blm,
            project,
            layer_id="blm",
            css_class="blm",
        ),
        _svg_layer(
            roads,
            project,
            layer_id="roads",
            css_class="roads",
        ),
        _svg_layer(
            mtbs,
            project,
            layer_id="mtbs",
            css_class="mtbs",
        ),
        _svg_layer(
            facilities,
            project,
            layer_id="facilities",
            css_class="facilities",
        ),
        patch_markup,
    ]
    counts = {
        "accepted_rbr_features": len(accepted),
        "rejected_unet_diagnostic_features": len(diagnostic),
        "mtbs_features": len(mtbs),
        "road_features": len(roads),
        "facility_features": len(facilities),
        "blm_features": len(blm),
    }
    return "".join(layers), {"views": views, "counts": counts, "bounds": bounds}


def _control(
    layer_id: str,
    title: str,
    role: str,
    *,
    checked: bool,
    opacity: int,
) -> str:
    checked_attr = " checked" if checked else ""
    return (
        f'<div class="layer-control"><div><label><input type="checkbox" '
        f'data-toggle="{layer_id}"{checked_attr}> <strong>{escape(title)}</strong>'
        f'</label><small>{escape(role)}</small></div><label class="opacity">'
        f'<span>{escape(title)} opacity</span><input type="range" min="0" max="100" '
        f'value="{opacity}" data-opacity="{layer_id}" aria-label="{escape(title)} opacity">'
        "</label></div>"
    )


def _render_html(
    report: dict[str, Any],
    map_markup: str,
    map_state: dict[str, Any],
) -> bytes:
    metrics = report["measurements"]
    views = map_state["views"]
    controls = "".join(
        [
            _control(
                "accepted-rbr",
                "Accepted RBR",
                "Primary analytical output",
                checked=True,
                opacity=78,
            ),
            _control(
                "rejected-unet",
                "Rejected U-Net",
                "Diagnostic only; off by default",
                checked=False,
                opacity=60,
            ),
            _control(
                "mtbs",
                "MTBS boundary",
                "Official-program reference context",
                checked=True,
                opacity=100,
            ),
            _control(
                "roads",
                "Selected roads",
                "Official context; not routing",
                checked=True,
                opacity=72,
            ),
            _control(
                "facilities",
                "Selected facilities",
                "Official context; not availability",
                checked=True,
                opacity=100,
            ),
            _control(
                "blm",
                "BLM boundary",
                "Generalized planning context",
                checked=True,
                opacity=75,
            ),
        ]
    )
    trace_rows = "".join(
        f"<tr><th scope=\"row\">{escape(key)}</th><td><code>{escape(value)}</code></td></tr>"
        for key, value in report["lineage"].items()
    )
    input_rows = "".join(
        "<li><code>"
        + escape(item["path"])
        + "</code> - "
        + f"{item['bytes']:,} bytes - <code>{item['sha256']}</code> - "
        + escape(item["role"])
        + "</li>"
        for item in report["bound_inputs"]
    )
    states = "".join(
        f'<li class="state {item["status"]}"><strong>{escape(item["name"])}</strong>'
        f'<span>{escape(item["meaning"])}</span><em>{escape(item["current"])}</em></li>'
        for item in report["run_state_taxonomy"]
    )
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="BurnLens local Phase Four RBR-primary CV-to-GEOINT evidence interface.">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; connect-src 'none'; font-src 'none'; object-src 'none'; frame-src 'none'; base-uri 'none'; form-action 'none'">
<link rel="icon" href="data:,">
<title>BurnLens - Ward Creek evidence interface</title>
<style>
:root{{--ink:#eaf1ec;--muted:#aebdb6;--night:#0c1614;--panel:#14221f;--line:#30463f;--forest:#143d35;--teal:#42d9cc;--ember:#ff9d42;--magenta:#ff66c4;--yellow:#ffd166;--blue:#65b7dd;--focus:#fff27a}}
*{{box-sizing:border-box}}html{{scroll-behavior:smooth}}body{{margin:0;background:var(--night);color:var(--ink);font:16px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif}}button,input{{font:inherit}}a{{color:var(--teal)}}button:focus-visible,input:focus-visible,a:focus-visible,summary:focus-visible{{outline:4px solid var(--focus);outline-offset:3px}}.skip{{position:absolute;left:-999px;top:1rem;background:white;color:#111;padding:.7rem;z-index:10}}.skip:focus{{left:1rem}}header{{border-bottom:1px solid var(--line);background:linear-gradient(120deg,#0d2822,#111a18)}}.hero{{max-width:1440px;margin:auto;padding:3.3rem 1.4rem 2.8rem;display:grid;grid-template-columns:1.25fr .75fr;gap:2rem}}.eyebrow{{color:#91d8cc;font-weight:800;letter-spacing:.1em;text-transform:uppercase;font-size:.82rem}}h1{{font-size:clamp(2.6rem,6vw,5.4rem);letter-spacing:-.055em;line-height:.95;margin:.5rem 0 1.2rem;max-width:850px}}.lede{{color:#d2dfda;font-size:1.18rem;max-width:770px}}.posture{{align-self:end;background:#ffffff0c;border:1px solid #ffffff25;border-radius:18px;padding:1.2rem}}.posture strong{{display:block;color:var(--ember);font-size:1.35rem}}main{{max-width:1440px;margin:auto;padding:1.4rem 1.4rem 5rem}}.warning{{background:#33271b;border:1px solid #8f612d;border-left:8px solid var(--ember);border-radius:14px;padding:1rem 1.2rem;margin:0 0 1.4rem}}.warning strong{{display:block;color:var(--yellow)}}.workspace{{display:grid;grid-template-columns:minmax(0,1fr) 370px;gap:1rem;align-items:start}}.map-card,.controls,.panel{{background:var(--panel);border:1px solid var(--line);border-radius:18px}}.map-card{{overflow:hidden}}.map-head{{padding:1rem 1rem .8rem;display:flex;justify-content:space-between;gap:1rem;align-items:center;border-bottom:1px solid var(--line)}}.map-head h2{{margin:0;font-size:1.25rem}}.focus-controls{{display:flex;flex-wrap:wrap;gap:.45rem}}.focus-controls button{{border:1px solid #5b746b;background:#1c302b;color:var(--ink);border-radius:99px;padding:.4rem .7rem;cursor:pointer}}.focus-controls button[aria-pressed="true"]{{background:var(--teal);color:#07211d;border-color:var(--teal);font-weight:800}}.map-wrap{{position:relative;background:#101d20;aspect-ratio:1000/660}}svg{{display:block;width:100%;height:100%}}svg.focused .patch-label{{display:none}}.accepted-rbr{{fill:var(--ember);stroke:#ffe0b8;stroke-width:.7;vector-effect:non-scaling-stroke}}.rejected-unet{{fill:url(#diag);stroke:var(--magenta);stroke-width:1.2;vector-effect:non-scaling-stroke}}.mtbs{{fill:none;stroke:var(--teal);stroke-width:3;vector-effect:non-scaling-stroke}}.roads{{fill:none;stroke:#c9c2a0;stroke-width:1.1;vector-effect:non-scaling-stroke}}.blm{{fill:none;stroke:var(--blue);stroke-width:1.4;stroke-dasharray:5 4;vector-effect:non-scaling-stroke}}.facilities{{fill:var(--yellow);stroke:#362c14;stroke-width:1;vector-effect:non-scaling-stroke}}.patch{{fill:none;stroke:white;stroke-width:2;stroke-dasharray:7 4;vector-effect:non-scaling-stroke}}.patch-label{{fill:white;font:bold 15px system-ui;paint-order:stroke;stroke:#0c1614;stroke-width:4px;stroke-linejoin:round}}.map-caption{{padding:.75rem 1rem;color:var(--muted);border-top:1px solid var(--line)}}.controls{{padding:1rem;position:sticky;top:1rem}}.controls h2{{font-size:1.25rem;margin:.1rem 0 .7rem}}.layer-control{{padding:.8rem 0;border-top:1px solid var(--line)}}.layer-control>div{{display:flex;flex-direction:column}}.layer-control small{{color:var(--muted);margin-left:1.45rem}}.opacity{{display:grid;grid-template-columns:1fr 120px;gap:.7rem;align-items:center;margin-top:.55rem;color:var(--muted);font-size:.83rem}}input[type=range]{{width:100%;accent-color:var(--teal)}}section{{margin-top:3.5rem;scroll-margin-top:1rem}}.section-head{{max-width:850px;margin-bottom:1.2rem}}.section-head h2{{font-size:clamp(2rem,4vw,3.4rem);line-height:1.03;letter-spacing:-.035em;margin:.3rem 0}}.section-head p{{color:var(--muted)}}.compare{{display:grid;grid-template-columns:1fr 1fr;gap:1rem}}.panel{{padding:1.2rem}}.panel h3{{margin:.1rem 0 .5rem}}.metric-row{{display:grid;grid-template-columns:repeat(3,1fr);gap:.65rem;margin:1rem 0}}.metric{{background:#0e1c19;border:1px solid var(--line);border-radius:12px;padding:.8rem}}.metric strong{{display:block;color:var(--ember);font-size:1.55rem;line-height:1.1}}.failure{{border-color:#8a456e}}.failure h3,.failure .metric strong{{color:var(--magenta)}}.source-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem}}.source-grid strong{{display:block;margin-bottom:.35rem}}.source-grid p{{color:var(--muted);margin:.3rem 0}}.states{{list-style:none;padding:0;display:grid;grid-template-columns:repeat(3,1fr);gap:.75rem}}.state{{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:1rem}}.state strong,.state span,.state em{{display:block}}.state span{{color:var(--muted);min-height:3.1rem}}.state em{{font-style:normal;font-weight:800;margin-top:.5rem}}.state.active{{border-color:var(--teal)}}.state.active em{{color:var(--teal)}}.state.retained{{border-color:var(--magenta)}}.state.retained em{{color:var(--magenta)}}table{{width:100%;border-collapse:collapse;background:var(--panel);border:1px solid var(--line)}}th,td{{padding:.8rem;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}}th{{width:32%;color:var(--muted)}}code{{font:0.86rem/1.4 ui-monospace,SFMono-Regular,Consolas,monospace;overflow-wrap:anywhere}}details{{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:1rem;margin-top:1rem}}summary{{cursor:pointer;font-weight:800}}details li+li{{margin-top:.55rem}}footer{{border-top:1px solid var(--line);padding:2rem 1.4rem;color:var(--muted)}}footer div{{max-width:1440px;margin:auto}}@media(max-width:1000px){{.workspace{{grid-template-columns:1fr}}.controls{{position:static;display:grid;grid-template-columns:1fr 1fr;gap:0 1rem}}.controls h2,.controls>p{{grid-column:1/-1}}.source-grid{{grid-template-columns:1fr 1fr}}}}@media(max-width:620px){{.hero{{grid-template-columns:1fr;padding-top:2.4rem}}main{{padding-left:.75rem;padding-right:.75rem}}.map-head{{align-items:flex-start;flex-direction:column}}.controls,.compare,.source-grid,.states{{grid-template-columns:1fr}}.metric-row{{grid-template-columns:1fr 1fr}}.opacity{{grid-template-columns:1fr 100px}}th,td{{display:block;width:100%}}th{{padding-bottom:.15rem;border-bottom:0}}td{{padding-top:.15rem}}}}@media(prefers-reduced-motion:reduce){{html{{scroll-behavior:auto}}}}@media print{{.controls,.focus-controls{{display:none}}body{{background:white;color:#111}}.panel,.map-card,table,details{{break-inside:avoid;border-color:#999}}}}
</style>
</head>
<body>
<a class="skip" href="#map">Skip to map</a>
<header><div class="hero"><div><p class="eyebrow">Phase Four - local/offline evidence interface</p><h1>Burn scar evidence, with failure visible.</h1><p class="lede">Ward Creek shows the accepted RBR baseline as the analytical output, the trained U-Net as a rejected diagnostic, and official-source context in distinct, inspectable roles.</p></div><aside class="posture" aria-label="Analytical posture"><strong>Baseline primary</strong>RBR is accepted for this bounded demonstration. The U-Net remains trained, reproducible, evaluated, and rejected. It is never used for U05 measurements.</aside></div></header>
<main>
<div class="warning" role="note"><strong>Experimental and non-operational.</strong>Owner-approved prototype regions are not independent ground truth. This interface is not official, field-validated, endorsed, operational, or suitable for routing, closure, tactical, property, legal, safety, or emergency decisions. Official sources govern their own facts.</div>
<div class="workspace">
<article class="map-card" id="map"><div class="map-head"><h2>Ward Creek bounded evidence map</h2><div class="focus-controls" aria-label="Map focus"><button type="button" data-view="{views['all']}" data-focus="all" aria-pressed="true">All context</button><button type="button" data-view="{views['WCP-001']}" data-focus="WCP-001" aria-pressed="false">WCP-001 burned</button><button type="button" data-view="{views['WCP-002']}" data-focus="WCP-002" aria-pressed="false">WCP-002 background</button></div></div><div class="map-wrap"><svg id="evidence-map" viewBox="0 0 1000 660" role="img" aria-labelledby="map-title map-desc" preserveAspectRatio="xMidYMid meet"><title id="map-title">Ward Creek accepted RBR and bounded official context</title><desc id="map-desc">Interactive layer map. Orange accepted RBR appears in two prototype patches. The cyan MTBS boundary overlaps most accepted RBR in WCP-001 and none in WCP-002. Rejected U-Net diagnostic is hidden by default and may be enabled as magenta hatching.</desc><defs><pattern id="diag" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="8" stroke="#ff66c4" stroke-width="3"/></pattern></defs><rect width="1000" height="660" fill="#101d20"/>{map_markup}</svg></div><div class="map-caption" aria-live="polite" id="map-status">Showing all bounded context. Rejected U-Net diagnostic is off by default.</div></article>
<aside class="controls" aria-label="Map layer controls"><h2>Layers and opacity</h2><p>Each layer keeps its own evidence role. Turning on the rejected U-Net does not promote it.</p>{controls}</aside>
</div>
<section id="text-equivalent" aria-labelledby="text-heading"><div class="section-head"><p class="eyebrow">Textual equivalent</p><h2 id="text-heading">The same result without relying on the map.</h2><p>These are deterministic, bounded observations with declared units and exclusions—not accuracy, prevalence, complete-scar, or generalization claims.</p></div><div class="compare"><article class="panel"><span class="eyebrow">Owner-approved burned prototype</span><h3>WCP-001</h3><div class="metric-row"><div class="metric"><strong>{metrics['WCP-001']['accepted_rbr_area_ha']:.2f} ha</strong>accepted RBR</div><div class="metric"><strong>{metrics['WCP-001']['accepted_rbr_inside_mtbs_pct']:.2f}%</strong>inside MTBS</div><div class="metric"><strong>{metrics['WCP-001']['roads']['secondary-highway']['nearest_distance_to_accepted_rbr_m']/1000:.2f} km</strong>nearest selected secondary highway</div></div><p>Accepted RBR covers 141.44 ha. Of that footprint, 133.22 ha overlaps the exact analyst-interpreted MTBS boundary. This is bounded spatial agreement, not field validation or complete-scar accuracy.</p></article><article class="panel failure"><span class="eyebrow">Owner-approved background prototype</span><h3>WCP-002 - visible baseline failure evidence</h3><div class="metric-row"><div class="metric"><strong>{metrics['WCP-002']['accepted_rbr_area_ha']:.2f} ha</strong>accepted RBR</div><div class="metric"><strong>{metrics['WCP-002']['accepted_rbr_inside_mtbs_pct']:.2f}%</strong>inside MTBS</div><div class="metric"><strong>{metrics['WCP-002']['accepted_rbr_patch_fraction_pct']:.2f}%</strong>of full patch</div></div><p>RBR marks 66.76 ha in the background patch and has zero MTBS overlap. BurnLens preserves this as first-class false-positive-risk evidence; it is not hidden by the stronger WCP-001 result.</p></article></div></section>
<section id="model" aria-labelledby="model-heading"><div class="section-head"><p class="eyebrow">Accepted baseline versus rejected model</p><h2 id="model-heading">A trained model can still be the wrong analytical choice.</h2><p>The frozen U-Net predicts all 89 selected test cores as burned and scores macro Dice 0.298742 against RBR 1.0. In the displayed patches it marks 4,095 of 4,096 pixels in WCP-001 and 3,206 of 4,096 in WCP-002. Those diagnostic footprints are inspectable but never used as the accepted perimeter or as an input to U05 measurements.</p></div><div class="compare"><div class="panel"><h3>Accepted RBR</h3><ul><li>Analytical status: accepted baseline.</li><li>Frozen threshold: <code>0.041043221950531006</code>.</li><li>Georeferenced raster and vector products pass exact round-trip validation.</li><li>WCP-002 remains visible false-positive-risk evidence.</li></ul></div><div class="panel failure"><h3>Rejected U-Net diagnostic</h3><ul><li>Analytical status: valid trained, evaluated, reproducible, and rejected.</li><li>Frozen diagnostic threshold: <code>0.5</code>.</li><li>No claim that it outperformed or added value beyond RBR.</li><li>No Phase 3B or follow-on experiment exists in this project.</li></ul></div></div></section>
<section id="sources" aria-labelledby="sources-heading"><div class="section-head"><p class="eyebrow">Source precedence</p><h2 id="sources-heading">Context stays context.</h2></div><div class="source-grid"><article class="panel"><strong>BurnLens RBR</strong><p>Accepted analytical output only for this bounded demonstration.</p></article><article class="panel"><strong>Rejected U-Net</strong><p>Diagnostic evidence only. Never the accepted perimeter or measurement source.</p></article><article class="panel"><strong>MTBS</strong><p>Analyst-interpreted official-program reference context; not ground truth or an operational incident perimeter.</p></article><article class="panel"><strong>The National Map</strong><p>Selected roads, facilities, and generalized BLM planning context; not routing, availability, access, ownership, or safety authority.</p></article></div></section>
<section id="states" aria-labelledby="states-heading"><div class="section-head"><p class="eyebrow">Run-state transparency</p><h2 id="states-heading">Every state remains visible, even when it is not active.</h2><p>The current run is accepted-baseline. The taxonomy prevents degraded, no-detection, fallback, failed, or withheld results from silently appearing accepted.</p></div><ul class="states">{states}</ul></section>
<section id="trace" aria-labelledby="trace-heading"><div class="section-head"><p class="eyebrow">Exact lineage</p><h2 id="trace-heading">Every displayed claim binds to a version and run.</h2></div><table><tbody>{trace_rows}</tbody></table><details><summary>Exact bound inputs</summary><ul>{input_rows}</ul></details></section>
</main>
<footer><div><strong>BurnLens {SOFTWARE_VERSION}</strong><p>Interface <code>{INTERFACE_VERSION}</code> - run <code>{escape(report['run_id'])}</code> - commit <code>{escape(report['git_source_commit'])}</code> - issue #570. Self-contained local/offline evidence; no external request, deployment, upload, or public-sharing change.</p></div></footer>
<script>
"use strict";
const map=document.getElementById("evidence-map");
const status=document.getElementById("map-status");
document.querySelectorAll("[data-toggle]").forEach(control=>{{
  const layer=document.getElementById(control.dataset.toggle);
  const apply=()=>{{layer.hidden=!control.checked;status.textContent=`${{control.checked?"Showing":"Hiding"}} ${{control.parentElement.innerText.trim()}}. Analytical roles are unchanged.`;}};
  apply();control.addEventListener("change",apply);
}});
document.querySelectorAll("[data-opacity]").forEach(control=>{{
  const layer=document.getElementById(control.dataset.opacity);
  const apply=()=>{{layer.style.opacity=String(Number(control.value)/100);}};
  apply();control.addEventListener("input",apply);
}});
document.querySelectorAll("[data-view]").forEach(button=>button.addEventListener("click",()=>{{
  document.querySelectorAll("[data-view]").forEach(item=>item.setAttribute("aria-pressed","false"));
  button.setAttribute("aria-pressed","true");map.setAttribute("viewBox",button.dataset.view);
  map.classList.toggle("focused",button.dataset.focus!=="all");
  status.textContent=`Focused on ${{button.textContent}}. Layer roles and measurements are unchanged.`;
}}));
</script>
</body>
</html>
"""
    return html.encode("utf-8")


def build_interface(
    *,
    repository_root: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, Any]:
    root = repository_root.resolve()
    if not RUN_ID_PATTERN.fullmatch(run_id):
        raise PhaseFourInterfaceError("run ID does not match U06 contract")
    if not COMMIT_PATTERN.fullmatch(git_source_commit):
        raise PhaseFourInterfaceError("git source commit is invalid")
    input_state = _validate_inputs(root)
    map_markup, map_state = _map_markup(root, input_state)
    overlay = input_state["overlay"]
    contract = input_state["contract"]
    report = {
        "interface_version": INTERFACE_VERSION,
        "interface_id": INTERFACE_ID,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "repository": "drwbkr1/burnlens-deschutes",
        "issue": 570,
        "unit_id": "P4O1-T01-U06",
        "git_source_commit": git_source_commit,
        "software_version_at_execution": SOFTWARE_VERSION,
        "state": "accepted-baseline",
        "route": "baseline-primary-with-rejected-model-diagnostic",
        "bound_inputs": input_state["receipts"]["items"],
        "map": {
            "self_contained": True,
            "offline": True,
            "external_requests": 0,
            "viewbox": "0 0 1000 660",
            "bounds_epsg_4326": map_state["bounds"],
            **map_state["counts"],
            "layer_controls": [
                "accepted-rbr",
                "rejected-unet",
                "mtbs",
                "roads",
                "facilities",
                "blm",
            ],
            "opacity_controls": True,
            "patch_focus_controls": ["all", "WCP-001", "WCP-002"],
            "textual_equivalent": True,
            "non_color_cues": True,
        },
        "measurements": overlay["measurement_contract"]["patches"],
        "lineage": {
            "Application version": SOFTWARE_VERSION,
            "Interface version": INTERFACE_VERSION,
            "Interface run": run_id,
            "Interface source commit": git_source_commit,
            "Accepted analytical method": contract["versions"]["baseline_version"],
            "Rejected diagnostic model": contract["versions"]["model_version"],
            "Rejected model package": contract["versions"][
                "rejected_model_package_version"
            ],
            "Dataset version": contract["versions"]["dataset_version"],
            "Whole-event split": contract["versions"]["split_version"],
            "Source state schema": contract["versions"][
                "source_label_state_schema_version"
            ],
            "Dataset label schema": contract["versions"][
                "dataset_label_schema_version"
            ],
            "Prototype label set": contract["versions"][
                "prototype_label_set_version"
            ],
            "Analytical run": "BL-2026-07-26-p4o1-t01-u02-analysis-r001",
            "Geospatial run": "BL-2026-07-26-p4o1-t01-u03-geospatial-r003",
            "Context run": "BL-2026-07-26-p4o1-t01-u04-context-r001",
            "Overlay run": "BL-2026-07-26-p4o1-t01-u05-overlay-r001",
        },
        "run_state_taxonomy": [
            {
                "name": "Accepted",
                "meaning": "All required gates pass for the declared bounded role.",
                "current": "Active: accepted RBR baseline",
                "status": "active",
            },
            {
                "name": "Degraded",
                "meaning": "Output exists with a material quality limitation.",
                "current": "Not active in accepted run",
                "status": "inactive",
            },
            {
                "name": "No detection",
                "meaning": "A valid run reports no accepted detection.",
                "current": "Not active in accepted run",
                "status": "inactive",
            },
            {
                "name": "Fallback",
                "meaning": "A declared fallback route ran instead of the primary route.",
                "current": "Not active; RBR is primary",
                "status": "inactive",
            },
            {
                "name": "Failed",
                "meaning": "The attempt cannot satisfy its declared output gates.",
                "current": "Retained: U03 render QA r001/r002",
                "status": "retained",
            },
            {
                "name": "Withheld",
                "meaning": "Output is intentionally not released from custody.",
                "current": "Not active in accepted run",
                "status": "inactive",
            },
        ],
        "accessibility": {
            "semantic_landmarks": True,
            "skip_link": True,
            "keyboard_native_controls": True,
            "visible_focus": True,
            "reduced_motion": True,
            "responsive_narrow_layout": True,
            "svg_title_and_description": True,
            "map_textual_equivalent": True,
            "role_not_conveyed_by_color_alone": True,
        },
        "warning": (
            "Experimental owner-approved prototype evidence. Not independent "
            "ground truth, official, field-validated, endorsed, operational, "
            "or suitable for routing, closure, tactical, property, legal, "
            "safety, or emergency decisions."
        ),
        "boundaries": {
            "model_accepted": False,
            "model_outperformed_rbr": False,
            "unet_used_for_measurement": False,
            "context_is_label_truth": False,
            "context_is_model_input": False,
            "phase_3b_created": False,
            "second_experiment_planned": False,
            "second_experiment_implemented": False,
            "external_requests": False,
            "user_upload": False,
            "deployment": False,
            "public_sharing_change": False,
            "official_operational_field_validated_endorsed_or_emergency_claim": False,
        },
        "disposition": "pass-interface-candidate-pending-render-qa",
        "next_dependency": "P4O1-T01-U06 real desktop and narrow interaction QA",
    }
    html_bytes = _render_html(report, map_markup, map_state)
    final_report = deepcopy(report)
    final_report["outputs"] = [
        {
            "path": OUTPUT_HTML,
            "bytes": len(html_bytes),
            "sha256": sha256(html_bytes).hexdigest(),
        }
    ]
    json_bytes = _json_bytes(final_report)
    return {
        "report": final_report,
        "outputs": {
            OUTPUT_HTML: html_bytes,
            OUTPUT_JSON: json_bytes,
        },
    }


def _require_clean_head(root: Path, git_source_commit: str) -> None:
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if head != git_source_commit:
        raise PhaseFourInterfaceError("git source commit differs from HEAD")
    status = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    if status:
        raise PhaseFourInterfaceError("working tree must be clean before U06")


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
            raise PhaseFourInterfaceError(f"output readback differs: {path}")
    except Exception:
        if created and path.exists():
            path.unlink()
        raise


def run_interface(
    *,
    repository_root: Path,
    output_directory: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, Any]:
    root = repository_root.resolve()
    output = output_directory.resolve()
    if output.exists() and any(output.iterdir()):
        raise PhaseFourInterfaceError(
            f"refusing to overwrite nonempty output directory: {output}"
        )
    _require_clean_head(root, git_source_commit)
    build = build_interface(
        repository_root=root,
        generated_at_utc=generated_at_utc,
        run_id=run_id,
        git_source_commit=git_source_commit,
    )
    for name, payload in build["outputs"].items():
        _write_new(output / name, payload)
    return build
