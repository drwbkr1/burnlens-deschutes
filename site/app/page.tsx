const releaseTag = "v0.56.0-baseline-first-portfolio-release";
const repository = "https://github.com/drwbkr1/burnlens-deschutes";
const release = `${repository}/releases/tag/${releaseTag}`;
const download = `${repository}/releases/download/${releaseTag}/BURNLENS-PHASE-SIX-BASELINE-FIRST-CANDIDATE-2026-002.zip`;

const lineage = [
  ["Repository release", "BurnLens 0.56.0", "tagged baseline-first portfolio release"],
  ["AOI", "aoi-darlene3-model-v0.2.0", "bounded Deschutes County study area"],
  [
    "Prototype labels",
    "owner-approved-prototype-region-labels-v0.5.0",
    "owner-confirmed, not independent ground truth",
  ],
  ["Dataset / split", "burnlens-dataset-v0.1.0", "whole-event split v0.1.0"],
  ["Accepted method", "burnlens-baseline-v0.1.0", "RBR threshold fixed before test"],
  ["Rejected model", "burnlens-unet-binary-v0.1.0", "trained once; rejected after one test opening"],
  [
    "GEOINT run",
    "BL-2026-07-26-p4o1-t01-u07-package-r001",
    "immutable Ward Creek run package",
  ],
];

const stages = [
  "Official sources",
  "Optical pairs",
  "Prototype regions",
  "Whole-event split",
  "Baseline + U-Net",
  "Raster + vectors",
  "Overlay + run package",
];

export default function Home() {
  return (
    <>
      <a className="skip-link" href="#evidence">
        Skip to evidence
      </a>

      <header className="site-header">
        <a className="wordmark" href="#top" aria-label="BurnLens home">
          <span aria-hidden="true" className="mark-dot" />
          BurnLens
        </a>
        <nav aria-label="Primary navigation">
          <a href="#decision">Decision</a>
          <a href="#workflow">Workflow</a>
          <a href="#evidence">Evidence</a>
          <a href="#limits">Limits</a>
        </nav>
        <a className="header-link" href={repository}>
          Source ↗
        </a>
      </header>

      <main id="top">
        <section className="hero" aria-labelledby="hero-title">
          <div className="hero-copy">
            <p className="eyebrow">Experimental CV-to-GEOINT · baseline first</p>
            <h1 id="hero-title">
              The model failed.
              <span>The evidence held.</span>
            </h1>
            <p className="lede">
              BurnLens turns one bounded wildfire segmentation experiment into
              a reproducible geospatial evidence workflow. A U-Net was trained,
              evaluated once, and rejected. The stronger RBR baseline carries
              the accepted result forward—with its failure modes left visible.
            </p>
            <div className="hero-actions">
              <a className="button primary" href="/evidence/ward-creek/">
                Explore the GEOINT result
              </a>
              <a className="button secondary" href={download}>
                Download the verified release
              </a>
            </div>
            <p className="release-line">
              <span className="status-pulse" aria-hidden="true" />
              Published as BurnLens 0.56.0 · exact release archive and lineage
            </p>
          </div>

          <div className="hero-visual" aria-label="BurnLens analytical summary">
            <div className="contour contour-one" />
            <div className="contour contour-two" />
            <div className="contour contour-three" />
            <div className="map-grid" aria-hidden="true" />
            <div className="metric-float metric-a">
              <span>Accepted</span>
              <strong>RBR</strong>
              <small>Dice 1.000</small>
            </div>
            <div className="metric-float metric-b">
              <span>Rejected</span>
              <strong>U-Net</strong>
              <small>Dice 0.299</small>
            </div>
            <div className="metric-float metric-c">
              <span>Visible risk</span>
              <strong>WCP-002</strong>
              <small>0% MTBS overlap</small>
            </div>
          </div>
        </section>

        <aside className="boundary" aria-label="Use boundary">
          <strong>Use boundary</strong>
          <p>
            Experimental BurnLens CV output. Not official wildfire
            information. Not emergency guidance. Not for evacuation, routing,
            tactical, suppression, incident-command, property, insurance,
            legal, or regulatory decisions. Official sources govern.
          </p>
        </aside>

        <section id="decision" className="section decision">
          <div className="section-heading">
            <p className="eyebrow">The technical decision</p>
            <h2>Reproducible does not mean accepted.</h2>
            <p>
              The bounded U-Net reproduced exactly—but predicted every selected
              test core as burned. BurnLens preserves that failure and keeps the
              stronger preregistered RBR baseline.
            </p>
          </div>

          <div className="comparison">
            <article className="result-card accepted-card">
              <div className="card-kicker">Accepted analytical method</div>
              <div className="result-row">
                <h3>RBR baseline</h3>
                <span className="pill accepted-pill">Accepted</span>
              </div>
              <strong className="big-number">1.000</strong>
              <p>Event-class macro Dice on 89 selected sealed-test cores.</p>
              <div className="score-track" aria-label="RBR Dice 1.000">
                <span className="score-rbr" />
              </div>
              <a href="/evidence/baseline/">Inspect exact evaluation →</a>
            </article>

            <article className="result-card rejected-card">
              <div className="card-kicker">First-class diagnostic result</div>
              <div className="result-row">
                <h3>Bounded U-Net</h3>
                <span className="pill rejected-pill">Rejected</span>
              </div>
              <strong className="big-number">0.299</strong>
              <p>
                Event-class macro Dice; all 89 selected cores predicted burned.
              </p>
              <div className="score-track" aria-label="U-Net Dice 0.299">
                <span className="score-unet" />
              </div>
              <a href="/evidence/model/">Read the rejection decision →</a>
            </article>
          </div>
        </section>

        <section id="workflow" className="section workflow">
          <div className="section-heading compact">
            <p className="eyebrow">The evidence chain</p>
            <h2>A gated workflow, not a black box.</h2>
          </div>
          <ol className="stage-list">
            {stages.map((stage, index) => (
              <li key={stage}>
                <span>{String(index + 1).padStart(2, "0")}</span>
                <strong>{stage}</strong>
              </li>
            ))}
          </ol>
          <p className="workflow-note">
            Every stage retains exact sources, terms, hashes, uncertainty,
            leakage controls, failures, and the next dependency. Owner “yes” is
            necessary for prototype labels, never sufficient.
          </p>
        </section>

        <section id="evidence" className="section evidence" tabIndex={-1}>
          <div className="section-heading">
            <p className="eyebrow">Inspect the actual outputs</p>
            <h2>One accepted result. One failure kept in frame.</h2>
            <p>
              These are exact repository artifacts carried into the public
              release—not marketing reconstructions.
            </p>
          </div>

          <div className="evidence-grid">
            <a className="evidence-card feature" href="/evidence/ward-creek/">
              <img
                src="/evidence/ward-creek/overlay-quicklook.png"
                alt="Ward Creek RBR overlay quicklook with accepted polygons, MTBS comparison boundary, and bounded context"
              />
              <div>
                <span className="card-kicker">Interactive GEOINT evidence</span>
                <h3>Ward Creek, inspected end to end</h3>
                <p>
                  Toggle the rejected model diagnostic, examine two analysis
                  patches, and inspect raster, vector, context, and overlap
                  evidence.
                </p>
                <strong>Open the live evidence interface →</strong>
              </div>
            </a>

            <a className="evidence-card" href="/evidence/baseline/">
              <img
                src="/evidence/baseline/evaluation.png"
                alt="BurnLens baseline evaluation showing RBR performance on Ward Creek and Windigo"
              />
              <div>
                <span className="card-kicker">Accepted baseline</span>
                <h3>RBR wins the bounded test</h3>
                <p>
                  The threshold was selected before the sealed test opening and
                  evaluated by whole event.
                </p>
              </div>
            </a>

            <a className="evidence-card" href="/evidence/model/">
              <img
                src="/evidence/model/evaluation.png"
                alt="Bounded U-Net evaluation showing the rejected model result"
              />
              <div>
                <span className="card-kicker">Rejected model</span>
                <h3>The failure remains inspectable</h3>
                <p>
                  Exact weights and training history reproduce; analytical
                  acceptance does not follow.
                </p>
              </div>
            </a>
          </div>

          <div className="fact-grid">
            <article>
              <span>WCP-001</span>
              <strong>141.44 ha</strong>
              <p>Accepted RBR area; 94.19% overlaps the MTBS boundary.</p>
            </article>
            <article className="warning-fact">
              <span>WCP-002</span>
              <strong>66.76 ha</strong>
              <p>
                Accepted RBR area; 0% MTBS overlap. Preserved as
                false-positive-risk evidence.
              </p>
            </article>
            <article>
              <span>Output package</span>
              <strong>202 vectors</strong>
              <p>Accepted polygons plus native-grid rasters and manifests.</p>
            </article>
          </div>
        </section>

        <section id="limits" className="section limits">
          <div className="section-heading compact">
            <p className="eyebrow">Interpretation boundary</p>
            <h2>What BurnLens does not prove.</h2>
          </div>
          <div className="limits-grid">
            <article>
              <span>01</span>
              <h3>No independent ground truth</h3>
              <p>
                Owner-approved prototype regions are disclosed human evidence,
                not field validation, consensus, or agency truth.
              </p>
            </article>
            <article>
              <span>02</span>
              <h3>No generalization claim</h3>
              <p>
                Twelve balanced patches do not estimate landscape prevalence or
                complete-scar performance.
              </p>
            </article>
            <article>
              <span>03</span>
              <h3>No model superiority</h3>
              <p>
                The U-Net did not outperform RBR and is excluded from accepted
                measurements.
              </p>
            </article>
            <article>
              <span>04</span>
              <h3>No operational status</h3>
              <p>
                BurnLens is experimental, non-emergency, non-operational, and
                not agency-endorsed.
              </p>
            </article>
          </div>
        </section>

        <section className="section trace">
          <div className="section-heading">
            <p className="eyebrow">Exact traceability</p>
            <h2>Every public claim has an identity.</h2>
          </div>
          <div className="trace-table" role="table" aria-label="Release lineage">
            {lineage.map(([layer, identity, note]) => (
              <div className="trace-row" role="row" key={layer}>
                <strong role="cell">{layer}</strong>
                <code role="cell">{identity}</code>
                <span role="cell">{note}</span>
              </div>
            ))}
          </div>
          <div className="trace-actions">
            <a className="button primary" href={release}>
              Open GitHub Release
            </a>
            <a
              className="button secondary"
              href={`${repository}/blob/${releaseTag}/docs/case-study/BURNLENS_CASE_STUDY.md`}
            >
              Read the full case study
            </a>
            <a
              className="button secondary"
              href={`${repository}/blob/${releaseTag}/docs/phase-six/REVIEWER_JOURNEY.md`}
            >
              Follow the reviewer journey
            </a>
          </div>
        </section>

        <section className="section sources">
          <div className="section-heading compact">
            <p className="eyebrow">Source precedence</p>
            <h2>Official sources govern.</h2>
          </div>
          <div className="source-grid">
            <p>Contains modified Copernicus Sentinel data 2019.</p>
            <p>
              Map services and data available from U.S. Geological Survey,
              National Geospatial Program.
            </p>
            <p>
              Monitoring Trends in Burn Severity (MTBS), U.S. Geological Survey
              and USDA Forest Service.
            </p>
          </div>
          <p className="source-note">
            No raw provider archive, private owner response, credential,
            retrieval detail, ignored custody path, or machine-local path is
            published here.
          </p>
        </section>
      </main>

      <footer>
        <div>
          <a className="wordmark footer-mark" href="#top">
            <span aria-hidden="true" className="mark-dot" />
            BurnLens
          </a>
          <p>Evidence before confidence.</p>
        </div>
        <div>
          <strong>Release</strong>
          <a href={release}>BurnLens 0.56.0</a>
          <a href={repository}>Source repository</a>
        </div>
        <div>
          <strong>Boundaries</strong>
          <span>Experimental</span>
          <span>Non-operational</span>
          <span>Official sources govern</span>
        </div>
      </footer>
    </>
  );
}
