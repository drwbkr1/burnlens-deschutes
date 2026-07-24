# PRECHECK-2026-062 - Windigo exact two-class proposal pass

**Unit / issue / branch:** `P2O4-T35-U04` / #534 / `codex/p2o4-t35-windigo-deadline-gate`

**Run:** `BL-2026-07-23-windigo-region-proposal-r001`

**Source code:** `fc8c81ad7e0fff081299e6f72a68c957081f7867`

**Decision:** `PROPOSE_EXACT_WINDIGO_TWO_CLASS_REGIONS_KEEP_OWNER_REVIEW_AND_PROMOTION_CLOSED`

## Entry and exact inputs

U04 begins only after U03 passes. It reopens the exact registered Sentinel pair, delivered Windigo reference archive, valid provider-generated MTBS boundary, and corrected source-fitness report without changing custody.

The controlling source report is `WINDIGO-SOURCE-FITNESS-2026-006.json`: 105,348 bytes / SHA-256 `7e0ede49bcee692c130c6f04fe90898f6c393fb57f64191da1f16c1567b724b2`. U04 recomputes its source-fitness archive, evidence, source-precedence, and fitness sections before candidate selection. Any drift fails closed.

## Deterministic two-class method

The exact pre/post pair is evaluated on one 20 m, EPSG:32610 grid covering the valid Windigo boundary plus three kilometres.

- The burned route requires usable optical pixels, the previously frozen multi-signal burn screen, BAER SBS classes 2-4, and MTBS dNBR6 classes 2-4.
- The background route requires usable optical pixels, the previously frozen multi-signal stability screen, and position outside a 60 m buffer around every conservative BAER, MTBS, or RAVG raster-domain footprint.
- RAVG remains context and conservative exclusion only. No RAVG class is affirmative evidence.
- Each route uses the established fixed 0.05 dNBR bin, intact eight-connected component, deterministic tie hash, 25-pixel core, and 51-pixel unknown ring.

The context has 205,548 quality-eligible pixels, 159 review-needed pixels, and 1,767 excluded pixels. The burned route contains 8,606 eligible pixels. The background route contains 182 eligible pixels; its largest intact component contains 30 pixels. Those exact counts are fail-closed drift gates.

## Exact proposals

| Candidate | Proposed class | Core | Unknown ring | Proposal binding |
|---|---|---:|---:|---|
| `WDP-001` | burned | 25 pixels | 51 pixels | `5c42d462910feecca3c060b189cffcdd61633a2285934a64250f7b8b0aa4fcb5` |
| `WDP-002` | background | 25 pixels | 51 pixels | `06b8a28d40abfb967a35fda06202e720b5449814e56ed55523c7fedbd3561aad` |

The cores and rings do not overlap. Each candidate raster records value `1` for the proposed core, value `2` for the unknown ring, and value `0` elsewhere. Both raster metadata sets record `owner_decision=none` and `label_created=false`.

## Gate ledger

| Gate | Result |
|---|---|
| source identity and precedence | pass: exact U03 report and recomputed sections match; BAER is primary positive evidence, MTBS corroborates, and RAVG remains context/exclusion |
| terms | pass for bounded attributed prototype evidence under `TERMS-2026-031` and `TERMS-2026-032`; no new source or right is inferred |
| custody and integrity | pass: exact ignored inputs remain unchanged; production and replay use no-overwrite directories |
| optical quality | pass: exact context quality counts match the frozen contract |
| registration | pass: the full context preserves all nine U03 registration-window passes |
| burned route | pass: 8,606 pixels satisfy every conjunctive optical, BAER, and MTBS condition |
| affirmative background route | pass for owner proposal only: 182 pixels satisfy optical stability outside the conservative source buffer |
| uncertainty | pass: both 51-pixel rings stay unknown; low/zero reference classes, nodata, review-needed pixels, and exclusions are never promoted |
| leakage | pass for this unit: Windigo remains one event group; no split, tuning, cross-event evaluation, or dataset promotion occurs |
| privacy and security | pass: no recipient, private retrieval URL, credential, token, cookie, or raw provider byte enters tracked evidence |
| render | pass for U04: the actual 1,800 by 1,040 production PNG was inspected at original resolution; HTML links only the exact local artifacts and contains responsive table overflow rules |
| reproducibility | pass: independent ignored replay reproduces all five output files byte for byte |
| promotion | closed: zero owner responses, labels, accepted event decisions, datasets, splits, baselines, models, or metrics |

Fresh local-file navigation remained unavailable under the in-app browser security policy and was not bypassed. U05 must still validate the exact interactive two-card owner-review surface at desktop and narrow widths before handoff.

## Exact outputs

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| JSON | 29,995 | `612143b0d54f6203026f00cc7848ea4d073b219967c75014b5d119ed85ec7365` |
| HTML | 4,885 | `0e3103393936d9937a2cabb9bb96d7dec80b71c54a5c0d5a8b9829539e58198a` |
| PNG | 87,000 | `47cb29f066f0e6e81aaabd222b7e1fdc4a5a95be419524648aa51474019b796b` |
| `WDP-001` raster | 2,852 | `0106fe4bf81ee9614a090a38541bb78be9cf033ae6b94c9fe9f3594a62fc0e2a` |
| `WDP-002` raster | 2,864 | `ada6b1e772a9039b5e73ed15ac184229a3df7bed7b55c402ac78e972aec6950e` |

## Validation and next dependency

- focused Windigo proposal and source-fitness tests: seven passed;
- environment/profile and proposal tests: eight passed after the console-command count advanced from 83 to 84;
- full repository suite: 566 passed, one expected skip, 20 retained NumPy deprecation warnings, and 86 subtests passed in 494.30 seconds;
- frozen 66-distribution lock, compilation, CLI help, and diff hygiene: pass;
- staged Git blobs match every recorded output hash; nested JSON/HTML use LF and PNG/TIFF use explicit binary attributes;
- original-resolution production PNG and exact replay: pass.

U04 disposition is `pass`. Only `P2O4-T35-U05_EXACT_TWO_CARD_OWNER_REVIEW` is eligible next. U05 must present only `WDP-001` and `WDP-002`, collect one yes/no/uncertain decision per candidate, preserve hash-bound drafts and finals, and lock the exact returned export before reveal. No answer may be prefilled or inferred. A yes is necessary but never sufficient for promotion.
