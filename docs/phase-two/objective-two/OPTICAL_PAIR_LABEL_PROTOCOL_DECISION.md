# Exact Optical Pair and Burn-Scar Label-Protocol Decision

## Decision

Accept the exact same-orbit Sentinel-2A pair as readable, legally usable source evidence for the BurnLens burn-scar label protocol. Defer every label pixel, dataset, split, baseline, and model.

Decision code: `ACCEPT_OPTICAL_PAIR_FOR_PROTOCOL_DEFER_LABELS`.

This accepts source and protocol evidence only. It does not accept a burn-scar label set, severity interpretation, model input, analytical product, or operational wildfire result.

## Weakness addressed

BurnLens had activated `target-burn-scar-v0.2.0` but had not proved that one exact pre/post optical pair was usable over the frozen AOI or defined how burned, background, uncertainty, quality exclusions, and review exceptions would remain distinct. That gap blocked every later Phase Two label, baseline, and dataset decision.

## Exact pair

The pair contains two complete Sentinel-2A L2A Collection 1 SAFE products on tile `10TFP`, relative orbit `13`, and processing baseline `05.10`:

- pre: `S2A_MSIL2A_20240625T185941_N0510_R013_T10TFP_20240626T012349.SAFE`, acquired about one hour before the approximate reported start;
- post: `S2A_MSIL2A_20240705T185921_N0510_R013_T10TFP_20240706T015448.SAFE`, acquired about ten days after that start.

The registered pair contains 2,254,805,631 ignored local provider bytes. Both archives have one SAFE root, 95 members, the expected manifest, clean CRC results, exact provider MD5/BLAKE3 values, and recorded local SHA-256 values. Zero provider bytes are committed.

## Real AOI evidence

Run `BL-2026-07-15-optical-pair-evidence-r001` opens the real product/tile metadata and exact `aoi-darlene3-model-v0.2.0` windows:

- pre and post true color: `1,200 x 900` at native 10 m;
- pre and post B04, B8A, B12, and SCL: `600 x 450` at native 20 m;
- CRS: EPSG:32610;
- pre/post 20 m transforms and AOI bounds: exactly equal;
- spectral comparison: no reprojection, no resampling, and BOA quantification/offsets read from each product;
- pairwise quality: 267,067 pixels / 98.9137% eligible, 2,063 / 0.7641% review-needed, and 870 / 0.3222% excluded.

The original-resolution render shows readable pre/post pixels and a spatially coherent continuous dNBR response around the later NIFC incident-reference outline. That visible agreement supports pair fitness, not pixel truth. dNBR remains continuous evidence with a disclosed fixed color stretch and no classification or severity threshold.

## Five-state protocol

Protocol `burn-scar-label-protocol-v0.1.0` is a versioned design gate and is not implemented in a label array.

| State | Future target value | Rule |
|---|---:|---|
| Burned | 1 | Requires accepted optical change, visible boundary review, valid quality, temporal plausibility, and independent approval. No single index, SCL class, VIIRS point, or perimeter is sufficient. |
| Background-candidate | 0 | Requires clear observable land and affirmative unchanged/unburned support. Outside a perimeter, absent hotspot evidence, or low change alone is insufficient. |
| Unknown | ignored | Evidence is insufficient, mixed, ambiguous, or conflicting. Unknown never becomes background. |
| Excluded | ignored | No data, saturation/defect, shadow, cloud/cirrus, snow/ice, water, failed registration, or disallowed processing remains outside loss and metrics. |
| Review-needed | ignored until resolved | SCL 7, borderline change, boundary/mixed pixels, atmosphere concerns, local registration doubt, disagreement, and exceptions require explicit review. |

The future binary target therefore requires a companion state layer. A binary array without the state/audit evidence is non-conforming.

## Registration, leakage, and independent QA

- Exact source-grid identity is necessary but does not prove subpixel content registration. Before label construction, measure local content residual and require no more than 0.5 native 20 m pixel / 10 m, or remediate/exclude the affected area.
- Keep at least a one-native-pixel review band around candidate transitions and uncertain boundaries.
- Group by incident/event, scene pair, geography, and time before patches are created. This one event cannot independently populate train, validation, and test groups.
- Imagery and later references used to construct labels cannot also serve as independent evaluation evidence for the same held-out group.
- A later label checkpoint requires a second review pass independent of the proposal, recorded disagreements, boundary review, and an audit sample from all five states.

## Source and use basis

`SOURCE-2026-009`, `SOURCE-2026-010`, `TERMS-2026-004`, `ACCESS-2026-009`, and `PRECHECK-2026-008` preserve exact identity, current terms, attribution, owner-authorized access, and the bounded data-touch gate. Modified evidence says `Contains modified Copernicus Sentinel data 2024`.

The NIFC outline is later mixed-method incident-reference context, not pixel-perfect truth. Active-fire observations remain complementary native-scale thermal-anomaly references. Current MTBS evidence contains no exact Darlene 3 record in the frozen AOI and remains methodology or future/cross-fire reference only.

## What remains

No content-registration measurement, label array, independent annotation QA, dataset, leakage-resistant split, spectral baseline, model, metric, application, deployment, or operational validation exists. The next bounded checkpoint may implement registration measurement and a reviewable five-state label proposal; it may not silently collapse uncertainty or create a dataset before label QA passes.

Successor note: P2O3-T01 / issue #347 later measures pair-local translation under `local-content-registration-v0.1.0` and accepts all twelve fixed AOI windows. This satisfies the bounded registration prerequisite only. Label implementation, independent QA, dataset, split, baseline, model, application, and operational validation remain absent.

> Experimental BurnLens CV evidence. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
