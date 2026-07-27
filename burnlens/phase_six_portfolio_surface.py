"""Build and validate the Phase Six baseline-first portfolio surface."""

from __future__ import annotations

import argparse
from hashlib import sha256
import html
import json
from pathlib import Path
import re
from typing import Any


SURFACE_VERSION = "burnlens-baseline-first-portfolio-surface-v0.1.0"
SURFACE_ID = "BURNLENS-PHASE-SIX-PORTFOLIO-SURFACE-2026-001"
ROUTE = "baseline-primary-with-rejected-model-diagnostic"
ACCEPTED_METHOD = "burnlens-baseline-v0.1.0"
REJECTED_MODEL = "burnlens-unet-binary-v0.1.0"
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")
RUN_ID_PATTERN = re.compile(
    r"^BL-[0-9]{4}-[0-9]{2}-[0-9]{2}-p6o1-t01-u03-"
    r"portfolio-surface-r[0-9]{3}$"
)
HREF_PATTERN = re.compile(r'href="([^"]+)"')

SOURCE_FILES = (
    {
        "path": "docs/phase-six/REVIEWER_JOURNEY.md",
        "bytes": 10842,
        "sha256": "74b072903c56603e390803a1eea0e1f72a2a9f019c8d2ee5a946941e645bee3f",
        "role": "passed U02 narrative contract",
    },
    {
        "path": (
            "samples/runs/phase-four/"
            "burnlens-geoint-evidence-interface-v0.1.0/"
            "PHASE-FOUR-EVIDENCE-INTERFACE-2026-001.html"
        ),
        "bytes": 177666,
        "sha256": "7a657ad772b34ff42cf4f4024a585b70fb8e7f41bab363cd056fcf8059825fb7",
        "role": "exact accepted RBR-primary evidence interface",
    },
    {
        "path": (
            "samples/model-packages/burnlens-unet-binary-v0.1.0/"
            "PHASE-THREE-MODEL-DECISION.html"
        ),
        "bytes": 3981,
        "sha256": "36986bcfa4ab22ded2ed7b736730a769f2223fdaf70318e1b5bf60e537aafc1e",
        "role": "exact rejected-model decision",
    },
    {
        "path": (
            "samples/baselines/burnlens-baseline-v0.1.0/"
            "BASELINE-EVALUATION-2026-001.html"
        ),
        "bytes": 3921,
        "sha256": "109075ca31cb1c01137bdccff5786c862105eb15dc1cbe15c8603dcf3d15fd99",
        "role": "exact accepted baseline evaluation",
    },
    {
        "path": (
            "samples/runs/phase-five/"
            "burnlens-phase-five-baseline-first-candidate-v0.1.1/index.html"
        ),
        "bytes": 4007,
        "sha256": "f05dcc11e5912e356bb9da4a1826e731cb4d8a5dff0795b4e68225421ab5bdd2",
        "role": "exact Phase Five candidate index",
    },
    {
        "path": (
            "samples/runs/phase-five/"
            "burnlens-phase-five-baseline-first-candidate-v0.1.1/"
            "KNOWN-ISSUES.md"
        ),
        "bytes": 1969,
        "sha256": "5abff617fa6bcb341d17e3ce0566de15cfed4b2b0d5cc79f0e05b64ce4007b17",
        "role": "exact Phase Five known-issues register",
    },
    {
        "path": (
            "portfolio/phase-four/"
            "BURNLENS-WARD-CREEK-RBR-RUN-2026-001.zip"
        ),
        "bytes": 487893,
        "sha256": "91308a2ffe7095d89843edeb1634d6b1e972eb65bf1f67f38f1da0279102d84e",
        "role": "exact immutable Phase Four run package",
    },
    {
        "path": (
            "portfolio/phase-five/"
            "BURNLENS-PHASE-FIVE-BASELINE-FIRST-CANDIDATE-2026-002.zip"
        ),
        "bytes": 646513,
        "sha256": "691c4bddb6754d74ca858a0b801fb21e62103032184425d2ba1b1648df1b0c26",
        "role": "exact immutable Phase Five candidate package",
    },
)

LINKS = (
    {
        "id": "phase-four-interface",
        "href": (
            "../../phase-four/burnlens-geoint-evidence-interface-v0.1.0/"
            "PHASE-FOUR-EVIDENCE-INTERFACE-2026-001.html"
        ),
        "repository_path": SOURCE_FILES[1]["path"],
    },
    {
        "id": "model-decision",
        "href": (
            "../../../model-packages/burnlens-unet-binary-v0.1.0/"
            "PHASE-THREE-MODEL-DECISION.html"
        ),
        "repository_path": SOURCE_FILES[2]["path"],
    },
    {
        "id": "baseline-evaluation",
        "href": (
            "../../../baselines/burnlens-baseline-v0.1.0/"
            "BASELINE-EVALUATION-2026-001.html"
        ),
        "repository_path": SOURCE_FILES[3]["path"],
    },
    {
        "id": "phase-five-index",
        "href": (
            "../../phase-five/"
            "burnlens-phase-five-baseline-first-candidate-v0.1.1/index.html"
        ),
        "repository_path": SOURCE_FILES[4]["path"],
    },
    {
        "id": "known-issues",
        "href": (
            "../../phase-five/"
            "burnlens-phase-five-baseline-first-candidate-v0.1.1/"
            "KNOWN-ISSUES.md"
        ),
        "repository_path": SOURCE_FILES[5]["path"],
    },
    {
        "id": "phase-four-zip",
        "href": (
            "../../../../portfolio/phase-four/"
            "BURNLENS-WARD-CREEK-RBR-RUN-2026-001.zip"
        ),
        "repository_path": SOURCE_FILES[6]["path"],
    },
    {
        "id": "phase-five-zip",
        "href": (
            "../../../../portfolio/phase-five/"
            "BURNLENS-PHASE-FIVE-BASELINE-FIRST-CANDIDATE-2026-002.zip"
        ),
        "repository_path": SOURCE_FILES[7]["path"],
    },
    {
        "id": "reviewer-journey",
        "href": "../../../../docs/phase-six/REVIEWER_JOURNEY.md",
        "repository_path": SOURCE_FILES[0]["path"],
    },
    {
        "id": "case-study",
        "href": "../../../../docs/case-study/BURNLENS_CASE_STUDY.md",
        "repository_path": "docs/case-study/BURNLENS_CASE_STUDY.md",
    },
)


class PhaseSixPortfolioSurfaceError(RuntimeError):
    """The Phase Six portfolio surface failed a controlled gate."""


def _sha256_bytes(payload: bytes) -> str:
    return sha256(payload).hexdigest()


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


def _verify_sources(repository_root: Path) -> list[dict[str, Any]]:
    verified: list[dict[str, Any]] = []
    for source in SOURCE_FILES:
        path = repository_root / str(source["path"])
        if not path.is_file() or path.is_symlink():
            raise PhaseSixPortfolioSurfaceError(
                f"missing or unsafe source: {source['path']}"
            )
        actual_bytes = path.stat().st_size
        actual_sha256 = _sha256_file(path)
        if actual_bytes != source["bytes"]:
            raise PhaseSixPortfolioSurfaceError(
                f"source byte mismatch: {source['path']}"
            )
        if actual_sha256 != source["sha256"]:
            raise PhaseSixPortfolioSurfaceError(
                f"source hash mismatch: {source['path']}"
            )
        verified.append(dict(source))
    for link in LINKS:
        target = repository_root / str(link["repository_path"])
        if not target.is_file() or target.is_symlink():
            raise PhaseSixPortfolioSurfaceError(
                f"missing or unsafe link target: {link['repository_path']}"
            )
    return verified


def _render_html(
    *,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> bytes:
    generated = html.escape(generated_at_utc)
    run = html.escape(run_id)
    commit = html.escape(git_source_commit)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; img-src data:; base-uri 'none'; form-action 'none'">
  <title>BurnLens — baseline first, evidence visible</title>
  <style>
    :root {{
      color-scheme: dark;
      --ink: #f5f1e8;
      --muted: #b9c1c9;
      --deep: #07151b;
      --panel: #0d222a;
      --line: #28434c;
      --amber: #f6b64a;
      --mint: #67d5b5;
      --coral: #ff806b;
      --blue: #79b8ff;
      --max: 1180px;
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin: 0;
      background:
        radial-gradient(circle at 80% 0%, #173843 0, transparent 32rem),
        linear-gradient(160deg, #07151b 0%, #091a21 48%, #07151b 100%);
      color: var(--ink);
      font: 16px/1.58 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    a {{ color: var(--mint); text-underline-offset: .18em; }}
    a:hover {{ color: #9be7d2; }}
    a:focus-visible, summary:focus-visible {{
      outline: 3px solid var(--amber);
      outline-offset: 4px;
      border-radius: 3px;
    }}
    .skip {{
      position: absolute; left: 1rem; top: -5rem; z-index: 10;
      background: var(--amber); color: #101820; padding: .65rem .9rem;
    }}
    .skip:focus {{ top: 1rem; }}
    header, main, footer {{ width: min(calc(100% - 2rem), var(--max)); margin-inline: auto; }}
    header {{ padding: 1.1rem 0 2.8rem; }}
    nav {{ display: flex; gap: .65rem 1.25rem; flex-wrap: wrap; align-items: center; }}
    nav .mark {{ color: var(--ink); font-weight: 800; letter-spacing: .08em; text-decoration: none; margin-right: auto; }}
    nav a:not(.mark) {{ font-size: .9rem; }}
    .hero {{ padding: 5.5rem 0 2rem; max-width: 900px; }}
    .eyebrow {{ color: var(--amber); font-weight: 800; letter-spacing: .11em; text-transform: uppercase; font-size: .78rem; }}
    h1 {{ margin: .4rem 0 1rem; max-width: 15ch; font-size: clamp(2.7rem, 7vw, 6.4rem); line-height: .96; letter-spacing: -.055em; }}
    h2 {{ margin: 0 0 .7rem; font-size: clamp(1.7rem, 4vw, 2.7rem); line-height: 1.08; letter-spacing: -.025em; }}
    h3 {{ margin: 0 0 .45rem; font-size: 1.08rem; }}
    p {{ max-width: 72ch; }}
    .lede {{ color: #d6dde0; font-size: clamp(1.12rem, 2.5vw, 1.4rem); max-width: 64ch; }}
    .warning {{ margin-top: 2rem; border-left: 4px solid var(--coral); padding: .75rem 1rem; background: #271b1a; max-width: 78ch; }}
    .actions {{ display: flex; flex-wrap: wrap; gap: .75rem; margin-top: 1.8rem; }}
    .button {{ display: inline-block; padding: .75rem 1rem; border: 1px solid var(--mint); border-radius: 999px; text-decoration: none; font-weight: 750; }}
    .button.primary {{ background: var(--mint); color: #07151b; }}
    section {{ padding: 4rem 0; border-top: 1px solid var(--line); }}
    .grid {{ display: grid; grid-template-columns: repeat(12, 1fr); gap: 1rem; }}
    .card {{ grid-column: span 4; background: linear-gradient(145deg, #102a33, #0c2027); border: 1px solid var(--line); border-radius: 14px; padding: 1.2rem; }}
    .card.wide {{ grid-column: span 6; }}
    .card strong.metric {{ display: block; font-size: clamp(2rem, 5vw, 3.8rem); line-height: 1; margin: .5rem 0; }}
    .accepted {{ color: var(--mint); }}
    .rejected {{ color: var(--coral); }}
    .risk {{ color: var(--amber); }}
    .muted {{ color: var(--muted); }}
    .compare {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1.1rem; margin-top: 1.2rem; }}
    .bar {{ height: .8rem; border-radius: 99px; background: #19313a; overflow: hidden; margin: .7rem 0; }}
    .bar > span {{ display: block; height: 100%; border-radius: inherit; }}
    .bar.rbr > span {{ width: 100%; background: var(--mint); }}
    .bar.unet > span {{ width: 29.8742%; background: var(--coral); }}
    .flow {{ display: grid; gap: .55rem; counter-reset: flow; }}
    .flow li {{ list-style: none; background: #0d222a; border-left: 3px solid var(--blue); padding: .65rem .85rem; }}
    .flow li::before {{ counter-increment: flow; content: counter(flow) ". "; color: var(--blue); font-weight: 800; }}
    table {{ width: 100%; border-collapse: collapse; font-size: .92rem; }}
    th, td {{ padding: .65rem; text-align: left; vertical-align: top; border-bottom: 1px solid var(--line); }}
    th {{ color: var(--amber); }}
    code {{ overflow-wrap: anywhere; color: #d4ebff; }}
    details {{ border: 1px solid var(--line); border-radius: 10px; padding: .85rem 1rem; background: #0b1e25; }}
    summary {{ cursor: pointer; color: var(--amber); font-weight: 800; }}
    footer {{ padding: 2.5rem 0 4rem; color: var(--muted); font-size: .86rem; border-top: 1px solid var(--line); }}
    @media (max-width: 760px) {{
      .hero {{ padding-top: 3.5rem; }}
      .card, .card.wide {{ grid-column: 1 / -1; }}
      .compare {{ grid-template-columns: 1fr; }}
      table {{ display: block; overflow-x: auto; }}
    }}
    @media (prefers-reduced-motion: reduce) {{ html {{ scroll-behavior: auto; }} }}
  </style>
</head>
<body>
  <a class="skip" href="#main">Skip to evidence</a>
  <header>
    <nav aria-label="Primary">
      <a class="mark" href="#top">BURNLENS</a>
      <a href="#result">Result</a>
      <a href="#workflow">Workflow</a>
      <a href="#limits">Limits</a>
      <a href="#trace">Trace</a>
    </nav>
    <div class="hero" id="top">
      <div class="eyebrow">Experimental CV-to-GEOINT · baseline first</div>
      <h1>Evidence wins. The model doesn’t.</h1>
      <p class="lede">BurnLens trains a bounded U-Net, evaluates it once, preserves its failure, and rejects it against a stronger RBR baseline. The accepted baseline then becomes one georeferenced Ward Creek evidence workflow—with uncertainty and false-positive risk left visible.</p>
      <div class="actions">
        <a class="button primary" href="{LINKS[0]['href']}">Open the Ward Creek interface</a>
        <a class="button" href="{LINKS[1]['href']}">Inspect the rejected model</a>
      </div>
      <p class="warning"><strong>Use boundary:</strong> Experimental BurnLens CV output. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.</p>
    </div>
  </header>

  <main id="main">
    <section id="result" aria-labelledby="result-title">
      <div class="eyebrow">The decision</div>
      <h2 id="result-title">Reproducible model. Rejected model.</h2>
      <p>The U-Net predicts all 89 selected Ward Creek and Windigo test cores as burned. RBR remains the accepted analytical method for this bounded demonstration.</p>
      <div class="compare" aria-label="Event-class macro Dice comparison">
        <div class="card wide">
          <h3 class="accepted">Accepted RBR</h3>
          <strong class="metric accepted">1.000</strong>
          <span class="muted">event-class macro Dice on selected test cores</span>
          <div class="bar rbr" aria-hidden="true"><span></span></div>
          <a href="{LINKS[2]['href']}">Open exact baseline evaluation</a>
        </div>
        <div class="card wide">
          <h3 class="rejected">Rejected U-Net</h3>
          <strong class="metric rejected">0.299</strong>
          <span class="muted">event-class macro Dice on selected test cores</span>
          <div class="bar unet" aria-hidden="true"><span></span></div>
          <a href="{LINKS[1]['href']}">Open exact model decision</a>
        </div>
      </div>
    </section>

    <section aria-labelledby="map-title">
      <div class="eyebrow">The GEOINT result</div>
      <h2 id="map-title">One bounded result. One visible warning.</h2>
      <div class="grid">
        <article class="card">
          <h3>WCP-001</h3>
          <strong class="metric accepted">141.44 ha</strong>
          <p>Accepted RBR area; 94.19% overlaps the exact analyst-interpreted MTBS boundary.</p>
        </article>
        <article class="card">
          <h3>WCP-002</h3>
          <strong class="metric risk">66.76 ha</strong>
          <p>Accepted RBR area; 0% MTBS overlap. BurnLens presents this as first-class false-positive-risk evidence.</p>
        </article>
        <article class="card">
          <h3>Context stays context</h3>
          <strong class="metric">0</strong>
          <p>Selected TNM roads, facilities, and BLM boundaries intersecting either accepted footprint. They are not labels, routing, safety, or legal authority.</p>
        </article>
      </div>
      <div class="actions">
        <a class="button primary" href="{LINKS[0]['href']}">Explore exact map and layers</a>
        <a class="button" href="{LINKS[5]['href']}">Download exact Phase Four ZIP</a>
      </div>
    </section>

    <section id="workflow" aria-labelledby="workflow-title">
      <div class="eyebrow">How the evidence moves</div>
      <h2 id="workflow-title">A gated chain, not a black box.</h2>
      <ol class="flow">
        <li>Official and optical evidence enter source, terms, custody, quality, and uncertainty gates.</li>
        <li>Owner-confirmed prototype regions retain explicit unknown rings; owner yes is necessary, never sufficient.</li>
        <li>Twelve native-grid patches are divided by a pre-locked 2/2/2 whole-event split and independently reconstructed.</li>
        <li>Preregistered RBR and one bounded 117,473-parameter CPU U-Net are evaluated under separate sealed openings.</li>
        <li>The U-Net loses and remains diagnostic; RBR becomes the accepted bounded route.</li>
        <li>Ward Creek output becomes rasters, vectors, context, observations, an offline interface, and an immutable run package.</li>
        <li>Phase Five tests recovery, assurance, reconstruction, packaging, rollback, and known issues without changing the analysis.</li>
      </ol>
    </section>

    <section id="limits" aria-labelledby="limits-title">
      <div class="eyebrow">Interpretation boundary</div>
      <h2 id="limits-title">What BurnLens does not prove.</h2>
      <div class="grid">
        <article class="card wide"><h3>No independent truth</h3><p>Owner-approved prototype regions are not independent ground truth or field validation.</p></article>
        <article class="card wide"><h3>No generalization</h3><p>Twelve balanced patches, 287 selected cores, and 89 selected test cores do not estimate natural prevalence or complete-scar performance.</p></article>
        <article class="card wide"><h3>No model superiority</h3><p>The U-Net is not an accepted perimeter, area estimator, or calibrated confidence product. It did not outperform RBR.</p></article>
        <article class="card wide"><h3>No operational claim</h3><p>The interface is local and offline. BurnLens is not official, deployed, endorsed, field-validated, operational, or emergency-ready.</p></article>
      </div>
      <details>
        <summary>Two visible medium reliability findings</summary>
        <p>The Phase Five candidate retains a bounded setuptools advisory under the ZIP-only route and an omitted historical builder identity needed only for exact v0.54 wheel reconstruction. Both include impact and workaround.</p>
        <a href="{LINKS[4]['href']}">Read the exact known-issues register</a>
      </details>
    </section>

    <section id="trace" aria-labelledby="trace-title">
      <div class="eyebrow">Exact lineage</div>
      <h2 id="trace-title">Every claim has an identity.</h2>
      <table>
        <thead><tr><th>Layer</th><th>Identity</th></tr></thead>
        <tbody>
          <tr><td>Software baseline</td><td><code>0.55.0</code> · merge <code>7066dcd9cef555a6df0716dc7568205e7d6d395e</code></td></tr>
          <tr><td>AOI</td><td><code>aoi-darlene3-model-v0.2.0</code></td></tr>
          <tr><td>Labels</td><td><code>burn-scar-binary-region-label-schema-v0.3.0</code> · <code>owner-approved-prototype-region-labels-v0.5.0</code></td></tr>
          <tr><td>Dataset / split</td><td><code>burnlens-dataset-v0.1.0</code> · <code>burnlens-whole-event-split-v0.1.0</code></td></tr>
          <tr><td>Baseline / model</td><td><code>burnlens-baseline-v0.1.0</code> · <code>burnlens-unet-binary-v0.1.0</code> rejected</td></tr>
          <tr><td>Accepted run</td><td><code>BL-2026-07-26-p4o1-t01-u07-package-r001</code></td></tr>
          <tr><td>Phase Four ZIP</td><td>487,893 bytes · <code>91308a2ffe7095d89843edeb1634d6b1e972eb65bf1f67f38f1da0279102d84e</code></td></tr>
          <tr><td>Phase Five ZIP</td><td>646,513 bytes · <code>691c4bddb6754d74ca858a0b801fb21e62103032184425d2ba1b1648df1b0c26</code></td></tr>
          <tr><td>This surface</td><td><code>{run}</code> · source <code>{commit}</code></td></tr>
        </tbody>
      </table>
      <div class="actions">
        <a class="button" href="{LINKS[3]['href']}">Open Phase Five evidence</a>
        <a class="button" href="{LINKS[6]['href']}">Download Phase Five ZIP</a>
        <a class="button" href="{LINKS[7]['href']}">Read the full reviewer journey</a>
        <a class="button" href="{LINKS[8]['href']}">Read the case study</a>
      </div>
    </section>

    <section aria-labelledby="source-title">
      <div class="eyebrow">Source precedence and attribution</div>
      <h2 id="source-title">Official sources govern.</h2>
      <p>Contains modified Copernicus Sentinel data 2019.</p>
      <p>Map services and data available from U.S. Geological Survey, National Geospatial Program.</p>
      <p>Monitoring Trends in Burn Severity (MTBS), U.S. Geological Survey and USDA Forest Service.</p>
      <p class="muted">No raw provider archive, private owner response, credential, retrieval detail, ignored custody path, or machine-local path is included in this surface.</p>
    </section>
  </main>

  <footer>
    <p>Surface <code>{SURFACE_VERSION}</code> · generated {generated} · local pre-publication evidence only.</p>
    <p>No GitHub Release, deployment, public-sharing change, publication, or external submission is implied.</p>
  </footer>
</body>
</html>
""".encode("utf-8")


def _render_readme(
    *,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> bytes:
    return f"""# BurnLens Phase Six baseline-first portfolio surface

Surface: `{SURFACE_VERSION}`  
Run: `{run_id}`  
Source commit: `{git_source_commit}`  
Generated: `{generated_at_utc}`

Open `index.html`. The page is static, offline, keyboard-readable, and contains
no script or external asset. It links to exact immutable evidence already
tracked in this repository.

RBR is the accepted analytical method for one bounded Ward Creek
demonstration. The trained U-Net is a rejected diagnostic and did not
outperform RBR. WCP-002 remains visible false-positive-risk evidence.

This is a local pre-publication surface. It is not official wildfire
information, emergency guidance, field validation, an operational system, a
deployment, a GitHub Release, or an external submission.
""".encode("utf-8")


def build_surface(
    *,
    repository_root: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, Any]:
    if not generated_at_utc.endswith("Z"):
        raise PhaseSixPortfolioSurfaceError("generated_at_utc must end with Z")
    if not RUN_ID_PATTERN.fullmatch(run_id):
        raise PhaseSixPortfolioSurfaceError("invalid U03 run ID")
    if not COMMIT_PATTERN.fullmatch(git_source_commit):
        raise PhaseSixPortfolioSurfaceError("invalid git source commit")
    sources = _verify_sources(repository_root)
    page = _render_html(
        generated_at_utc=generated_at_utc,
        run_id=run_id,
        git_source_commit=git_source_commit,
    )
    readme = _render_readme(
        generated_at_utc=generated_at_utc,
        run_id=run_id,
        git_source_commit=git_source_commit,
    )
    manifest = {
        "manifest_version": "burnlens-phase-six-portfolio-surface-manifest-v0.1.0",
        "surface_id": SURFACE_ID,
        "surface_version": SURFACE_VERSION,
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "git_source_commit": git_source_commit,
        "software_version_at_build": "0.55.0",
        "state": "local-pre-publication-surface",
        "route": ROUTE,
        "accepted_method": ACCEPTED_METHOD,
        "rejected_model": REJECTED_MODEL,
        "model_accepted": False,
        "model_outperformed_rbr": False,
        "public_action_authorized": False,
        "sources": sources,
        "links": [dict(item) for item in LINKS],
        "outputs": [
            {
                "path": "README.md",
                "bytes": len(readme),
                "sha256": _sha256_bytes(readme),
                "media_type": "text/markdown",
            },
            {
                "path": "index.html",
                "bytes": len(page),
                "sha256": _sha256_bytes(page),
                "media_type": "text/html",
            },
        ],
        "features": {
            "static": True,
            "offline": True,
            "scripts": 0,
            "external_assets": 0,
            "external_links": 0,
            "keyboard_skip_link": True,
            "responsive_breakpoint_px": 760,
            "reduced_motion_respected": True,
            "visible_wcp_002_failure": True,
            "accepted_and_rejected_methods_separated": True,
            "text_equivalent": True,
        },
        "required_notices": [
            "Contains modified Copernicus Sentinel data 2019.",
            (
                "Map services and data available from U.S. Geological Survey, "
                "National Geospatial Program."
            ),
            (
                "Monitoring Trends in Burn Severity (MTBS), U.S. Geological "
                "Survey and USDA Forest Service."
            ),
            (
                "Experimental BurnLens CV output. Not official wildfire "
                "information. Not emergency guidance."
            ),
        ],
        "next_dependency": "P6O1-T01-U03 real rendered and interaction QA",
    }
    return {
        "files": {
            "MANIFEST.json": _json_bytes(manifest),
            "README.md": readme,
            "index.html": page,
        },
        "manifest": manifest,
    }


def write_surface(
    *,
    repository_root: Path,
    output_root: Path,
    generated_at_utc: str,
    run_id: str,
    git_source_commit: str,
) -> dict[str, Any]:
    result = build_surface(
        repository_root=repository_root,
        generated_at_utc=generated_at_utc,
        run_id=run_id,
        git_source_commit=git_source_commit,
    )
    surface_root = output_root / SURFACE_VERSION
    if surface_root.exists():
        raise PhaseSixPortfolioSurfaceError(
            f"refusing to overwrite existing surface: {surface_root}"
        )
    surface_root.mkdir(parents=True)
    for relative, payload in result["files"].items():
        target = surface_root / relative
        target.write_bytes(payload)
    validation = validate_surface(
        surface_root,
        repository_root=repository_root,
    )
    return {
        "surface_root": surface_root.as_posix(),
        "manifest_path": (surface_root / "MANIFEST.json").as_posix(),
        "index_path": (surface_root / "index.html").as_posix(),
        "validation": validation,
        "result": "PHASE_SIX_PORTFOLIO_SURFACE_WRITE_PASS",
    }


def validate_surface(
    surface_root: Path,
    *,
    repository_root: Path,
) -> dict[str, Any]:
    if not surface_root.is_dir() or surface_root.is_symlink():
        raise PhaseSixPortfolioSurfaceError("surface must be a safe directory")
    expected_names = {"MANIFEST.json", "README.md", "index.html"}
    actual_names = {item.name for item in surface_root.iterdir()}
    if actual_names != expected_names:
        raise PhaseSixPortfolioSurfaceError("surface file roster mismatch")
    if any(item.is_symlink() or not item.is_file() for item in surface_root.iterdir()):
        raise PhaseSixPortfolioSurfaceError("unsafe surface member")
    try:
        manifest = json.loads((surface_root / "MANIFEST.json").read_text("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PhaseSixPortfolioSurfaceError("invalid surface manifest") from exc
    if manifest.get("surface_id") != SURFACE_ID:
        raise PhaseSixPortfolioSurfaceError("surface ID mismatch")
    if manifest.get("surface_version") != SURFACE_VERSION:
        raise PhaseSixPortfolioSurfaceError("surface version mismatch")
    if manifest.get("route") != ROUTE:
        raise PhaseSixPortfolioSurfaceError("surface route mismatch")
    if manifest.get("accepted_method") != ACCEPTED_METHOD:
        raise PhaseSixPortfolioSurfaceError("accepted method mismatch")
    if manifest.get("rejected_model") != REJECTED_MODEL:
        raise PhaseSixPortfolioSurfaceError("rejected model mismatch")
    if manifest.get("model_accepted") is not False:
        raise PhaseSixPortfolioSurfaceError("model must remain rejected")
    if manifest.get("model_outperformed_rbr") is not False:
        raise PhaseSixPortfolioSurfaceError("model superiority mismatch")
    if manifest.get("public_action_authorized") is not False:
        raise PhaseSixPortfolioSurfaceError("public action boundary mismatch")
    _verify_sources(repository_root)
    for item in manifest.get("outputs", []):
        path = surface_root / item["path"]
        if path.stat().st_size != item["bytes"]:
            raise PhaseSixPortfolioSurfaceError(
                f"surface output byte mismatch: {item['path']}"
            )
        if _sha256_file(path) != item["sha256"]:
            raise PhaseSixPortfolioSurfaceError(
                f"surface output hash mismatch: {item['path']}"
            )
    page = (surface_root / "index.html").read_text("utf-8")
    required = (
        "<title>BurnLens — baseline first, evidence visible</title>",
        "Evidence wins. The model doesn’t.",
        "Rejected U-Net",
        "Accepted RBR",
        "WCP-002",
        "66.76 ha",
        "did not outperform RBR",
        "Official sources govern.",
        "Skip to evidence",
        "Contains modified Copernicus Sentinel data 2019.",
    )
    if any(token not in page for token in required):
        raise PhaseSixPortfolioSurfaceError("surface semantic contract mismatch")
    if "<script" in page.lower():
        raise PhaseSixPortfolioSurfaceError("surface must contain no script")
    if re.search(r"https?://|file://|[A-Za-z]:\\\\", page, flags=re.IGNORECASE):
        raise PhaseSixPortfolioSurfaceError("surface contains external or local locator")
    actual_hrefs = HREF_PATTERN.findall(page)
    expected_hrefs = {
        "#top",
        "#result",
        "#workflow",
        "#limits",
        "#trace",
        "#main",
        *(str(item["href"]) for item in LINKS),
    }
    if set(actual_hrefs) != expected_hrefs:
        raise PhaseSixPortfolioSurfaceError("surface link roster mismatch")
    for link in manifest.get("links", []):
        target = repository_root / str(link["repository_path"])
        if not target.is_file() or target.is_symlink():
            raise PhaseSixPortfolioSurfaceError(
                f"surface link target mismatch: {link['id']}"
            )
    return {
        "surface_id": SURFACE_ID,
        "surface_version": SURFACE_VERSION,
        "run_id": manifest["run_id"],
        "git_source_commit": manifest["git_source_commit"],
        "files": 3,
        "links": len(LINKS),
        "external_links": 0,
        "scripts": 0,
        "result": "PHASE_SIX_PORTFOLIO_SURFACE_VALIDATION_PASS",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build or validate the BurnLens Phase Six portfolio surface."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    build = subparsers.add_parser("build")
    build.add_argument("--repository-root", type=Path, required=True)
    build.add_argument("--output-root", type=Path, required=True)
    build.add_argument("--generated-at-utc", required=True)
    build.add_argument("--run-id", required=True)
    build.add_argument("--git-source-commit", required=True)
    validate = subparsers.add_parser("validate")
    validate.add_argument("--repository-root", type=Path, required=True)
    validate.add_argument("surface_root", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "build":
            result = write_surface(
                repository_root=args.repository_root.resolve(),
                output_root=args.output_root.resolve(),
                generated_at_utc=args.generated_at_utc,
                run_id=args.run_id,
                git_source_commit=args.git_source_commit,
            )
        else:
            result = validate_surface(
                args.surface_root.resolve(),
                repository_root=args.repository_root.resolve(),
            )
    except PhaseSixPortfolioSurfaceError as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
