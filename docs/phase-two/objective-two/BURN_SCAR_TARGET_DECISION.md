# P2O2-T05 Burn-Scar Target-Path Decision

## Decision

The owner approved `ACTIVATE_BURN_SCAR_BINARY_MASK_FALLBACK` on 2026-07-14. BurnLens target decision `target-burn-scar-v0.2.0` is active.

This is the established Phase One fallback, activated after real Phase Two evidence rejected direct active-fire labels. It does not change the project promise, technical and technical-adjacent reviewer, experimental binary semantic-segmentation task, six phase outcomes, GEOINT workflow, source precedence, transparency requirements, or use boundaries. It does not authorize severity, recovery, or multiclass work.

## Why the active-fire label path was rejected

P2O2-T04 inspected every one of the 23 bounded official NOAA-21 `VJ214IMG.002` candidates and selected the strongest defensible complementary reference. The selected day observation has 11 qualified AOI records, zero residual-bowtie exclusions, and a 31.01-degree qualified median view zenith. It is still 2.478049 hours after the Sentinel observation and has 375 m spatial support.

Those facts support native-scale thermal-anomaly reference use. They do not define genuine 10-20 m positive pixels, background pixels, or burn boundaries. BurnLens therefore retains active-fire observations as `COMPLEMENTARY_REFERENCE_ONLY` and will not buffer, resize, or otherwise promote them into burn-scar segmentation truth.

## MTBS availability decision

MTBS is scientifically relevant to the fallback. Its official documentation describes analyst-interpreted fire-level pre/post reflectance imagery, burn indices, burned-area boundaries, thematic severity, and non-processing masks. It also documents missing-fire reasons, quarterly releases, product revision, 30 m raster resolution, and 1:24,000-1:50,000 vector delineation.

The current official MTBS service does not expose an exact Darlene 3 record:

| Check | Result |
|---|---|
| 2024 occurrence inventory | 941 features returned without transfer-limit truncation |
| Darlene name / known AOI match in the 2024 inventory | 0 |
| 2024 occurrence features intersecting the BurnLens discovery envelope | 0 |
| All-years occurrence features intersecting the same envelope | 0 |

The result means `NO_CURRENT_DARLENE3_RECORD_CONSIDER_METHODS_AND_CROSS_FIRE_REFERENCE`. It does not mean no burn scar exists. MTBS may be considered for methodology, future re-query, or explicitly separated cross-fire reference evidence. It cannot provide the exact Darlene 3 label today, must not be represented as field truth, and its six severity classes must not expand the active binary target.

MTBS metadata evaluation is allowed with citation. USGS states that USGS-authored or produced data and information are generally U.S. public domain while identifying exceptions for third-party materials. Any future exact MTBS product download or derivative build must re-query availability and revalidate the product metadata and current terms before data touch.

## Binary target contract before labels

| State | Current rule |
|---|---|
| Burned | Future positive pixels require an accepted, temporally appropriate, quality-screened optical-change and review protocol. No positive label exists yet. |
| Background candidate | Clear and observable pixels require affirmative support as unburned. Outside a perimeter or absence of a hotspot is not automatically background. |
| Unknown | Cloud, smoke, haze, shadow, snow, temporal ambiguity, source disagreement, and unobserved areas remain unknown. |
| Excluded | Invalid pixels, non-processing areas, failed georegistration, and quality states disallowed by the future protocol are excluded. |
| Review needed | Borderline optical change, uncertain timing, source disagreement, and protocol exceptions remain visible for review. |

Unknown and excluded pixels are never silently converted to background.

## Next gate

Proceed to one bounded source-and-protocol checkpoint. Before creating any label array, BurnLens must:

1. identify one exact, legally usable, temporally defensible pre/post optical source pair over `aoi-darlene3-model-v0.2.0`;
2. visually inspect the real native/analysis-grid pixels and optical quality states;
3. record exact provenance, terms, dates, CRS, grid, AOI coverage, and checksums;
4. define burned, background-candidate, unknown, excluded, and review-needed rules;
5. define georegistration tolerance, non-processing masks, temporal-leakage controls, and independent QA;
6. decide whether a reproducible non-model spectral baseline is defensible before any model work.

This checkpoint does not authorize a label array, dataset, split, baseline mask, model, inference, metric, deployment, or public wildfire result.

## Reliability remediation

PR #338 merged the first evidence run at `68971e9709b886adf8575a58d32694aad42f038e`. The required post-merge reconstruction then caught a checkout-dependent byte hash: the MTBS JSON source record used LF when `r001` was generated and CRLF after the squash merge. The scientific content, HTML, and PNG did not change, but the regenerated JSON correctly failed its byte-identity gate.

BurnLens did not tag or silently rewrite `r001`. Issue #339 preserves that run and defines a cross-platform contract: structured JSON input hashes are computed after universal-newline decoding and LF serialization; target JSON and HTML are written as explicit UTF-8/LF; repository attributes pin target evidence to LF; and a regression test proves equivalent LF and CRLF source records yield the same report. The immutable corrected evidence is `TARGET-DECISION-2026-002` / `BL-2026-07-14-target-decision-r002`.

## Evidence and traceability

- Decision issue / PR / analytical merge: #337 / #338 / `68971e9709b886adf8575a58d32694aad42f038e`
- Remediation issue / branch: #339 / `codex/p2o2-t05-eol-determinism`
- Software: BurnLens `0.6.0`
- Target: `target-burn-scar-v0.2.0`
- AOI: `aoi-darlene3-model-v0.2.0`
- Run: `BL-2026-07-14-target-decision-r002`
- Generator source: `cfbf357634cdcf9e68c3af78bfcb3e195bebc17a`
- MTBS record: `MTBS-DARLENE3-AVAILABILITY-2026-001`
- Input active-fire evidence: `OBSERVATION-GEOMETRY-2026-001` / `BL-2026-07-14-observation-geometry-r002`
- JSON SHA-256: `ac67f6c34a934d639c215ee98b181f1114b5624acafb85f65b1e2f3e804ce4d4`
- HTML SHA-256: `0c1279e5e1047ff251dcd65f068d3d45bf2c6982e6a308972205e9d0a76879d4`
- PNG SHA-256: `36f221aa6393ad07f14d4d7bb54b1f171ef0636ebb5640a11ab02ab9c5a9b5b0`
- Application / dataset / label schema / baseline / model: not created / not created / not created / not created / not created

The corrected JSON, HTML, and PNG reconstruct byte for byte from committed inputs and fixed `r002` parameters. The original 1600 by 1050 PNG was visually inspected. Semantic HTML content, relative image reference, intrinsic image dimensions, warning, source precedence, null lineage, and LF/CRLF input equivalence are covered by focused tests. The in-app browser rejected the local `file://` URL under its security policy; BurnLens does not claim a passing browser check for this checkpoint. `TARGET-DECISION-2026-001` remains the immutable pre-remediation run and is superseded for current evidence use.

## Primary sources

- MTBS FAQ: https://www.mtbs.gov/index.php/faqs
- MTBS product page: https://burnseverity.cr.usgs.gov/products/mtbs
- Official MTBS ArcGIS service: https://apps.fs.usda.gov/arcx/rest/services/EDW/EDW_MTBS_01/MapServer/
- USGS copyrights and credits: https://www.usgs.gov/information-policies-and-instructions/copyrights-and-credits

> Experimental BurnLens CV evidence. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
