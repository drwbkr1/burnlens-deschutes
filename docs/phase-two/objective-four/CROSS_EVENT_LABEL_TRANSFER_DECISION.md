# Cross-Event Five-State Label-Transfer Decision

## Question

Can BurnLens transfer its established five-state burn-scar proposal from Darlene 3 to the exact source-fit Tepee and McKay event pairs while preserving uncertainty, frozen groups, Tepee exclusions, source precedence, and complete traceability?

## Exact experiment

Issue #367 uses the four registered Sentinel-2 L2A archives accepted by `CROSS-EVENT-SOURCE-FITNESS-2026-001` and two exact public MTBS annual thematic clips registered under `SOURCE-2026-013`. The MTBS clips are analyst-interpreted remotely sensed reference evidence. They are not field truth, an operational perimeter, automatic labels, or endorsement.

The proposal keeps `burn-scar-label-protocol-v0.1.0` as a transfer hypothesis and `burn-scar-five-state-schema-v0.1.0` as the implemented state contract. Burned candidates require coherent Sentinel spectral change inside the eroded event boundary plus MTBS support class 2-4. MTBS never independently creates a burned candidate. SCL, source-fitness registration, ambiguous MTBS values, boundary transitions, cross-source conflicts, and unsupported usable pixels remain review-needed, excluded, or unknown.

The fixed Darlene near-zero stability rule produced no primary stable pixels for McKay. Under the owner's authorized burn-scar binary-mask fallback, BurnLens admits only the lowest 15% normalized non-burn change tail outside the expanded boundary with MTBS code 0, caps the normalized score at 6.0, and requires seven-of-nine spatial support. Tepee's event-relative threshold is `1.287317` with 445 coherent fallback pixels; McKay's is `5.842086` with 55. These are proposal diagnostics, not universal calibration or optimized accuracy thresholds.

## Real output

Final proposal run `BL-2026-07-16-cross-event-label-transfer-r003`, generated from source `6d9bb2a34a32f775e4bf83249151e41c25998ee5`, produces:

| Event | Background | Burned | Unknown | Excluded | Review-needed | Candidate / ignored |
|---|---:|---:|---:|---:|---:|---:|
| Tepee 1144 NE | 494 | 92 | 10,942 | 16,025 | 16,322 | 586 / 43,289 |
| McKay 1035 NE | 55 | 9,119 | 7,483 | 0 | 3,398 | 9,174 / 10,881 |
| Aggregate | 549 | 9,211 | 18,425 | 16,025 | 19,720 | 9,760 / 54,170 |

Tepee preserves W-01 exclusion, W-02 review, W-03 pass, and pixel-level SCL restrictions. McKay has no source-fitness exclusion, so the absent excluded state is recorded as zero rather than fabricated to satisfy a visual checklist.

![BurnLens cross-event five-state transfer](../../../samples/labels/cross-event/phase-two/CROSS-EVENT-LABEL-TRANSFER-2026-001.png)

## Separate QA

Final QA run `BL-2026-07-16-cross-event-label-transfer-qa-r003` invokes a separate module that does not import the transfer classifier. It reopens and verifies all four Sentinel archives and both MTBS clips, independently recomputes SCL, registration, spectral evidence, reference resampling, fallback, states, targets, raster tags, hashes, and grids, and compares every output pixel.

Across 63,930 pixels, state mismatches are 0 and target mismatches are 0. Forty-five deterministic per-state audit samples agree; the zero-count McKay excluded state is explicitly verified absent.

![BurnLens separate cross-event QA](../../../samples/labels/cross-event/phase-two/CROSS-EVENT-LABEL-TRANSFER-QA-2026-001.png)

## Decision

`ACCEPT_CROSS_EVENT_LABEL_TRANSFER_PROPOSAL_DEFER_DATASET`.

Accept this exact multi-event proposal as reproducible, reviewable evidence that the five-state uncertainty contract transfers across the two frozen source-fit events. The result materially improves portfolio evidence: the tool now shows exact imagery, reference evidence, proposal states, candidate targets, event differences, fallback behavior, and independent all-pixel software agreement in one traceable interface.

Do not call the proposal accepted ground truth, an independently human-reviewed label set, a dataset, a split, a baseline, a model, an accuracy result, field validation, or operational evidence. Software agreement proves reproducibility of the declared rules, not their ecological or field correctness. The event-relative fallback and the large ignored domain remain primary label/model risks.

## Next gate

Before a dataset or split can exist, quantify label fitness with review evidence independent of the proposal software, preserve whole event/geography/scene/time groups, define acceptance and adjudication rules, and decide whether the candidate pixels are strong enough for a leakage-resistant dataset or require a baseline-only/stop path. Do not optimize thresholds against desired class counts.
