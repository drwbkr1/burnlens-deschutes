# REGISTRY-2026-087 - P2O5-T03 U04 independent dataset QA

**Recorded:** 2026-07-25

**Issue:** #562

| Unit | Run / source | Outputs | Gates | Disposition | Next dependency |
|---|---|---|---|---|---|
| `P2O5-T03-U04-R001` | `BL-2026-07-25-p2o5-t03-u04-dataset-qa-r001`; `d63c8a5...` | four retained, invalid-bound outputs | supplied commit did not equal actual HEAD; zero promotion | `fail-retained` | exact-HEAD enforcement |
| `P2O5-T03-U04-R002` | `BL-2026-07-25-p2o5-t03-u04-dataset-qa-r002`; `dcb2afc...` | four retained outputs | all data gates and desktop render pass; narrow document 764 px wide | `fail-retained` | responsive table containment |
| `P2O5-T03-U04-R003` | `BL-2026-07-25-p2o5-t03-u04-dataset-qa-r003`; `4df233f...` | four retained outputs | tables fit; unbroken decision token keeps narrow document at 764 px | `fail-retained` | decision-text wrapping |
| `P2O5-T03-U04-R004` | `BL-2026-07-25-p2o5-t03-u04-dataset-qa-r004`; `86d5e4555a51f791426c3d0f20e901cbdbf18f3c` | QA JSON `90aafef4...`; HTML `6092266f...`; PNG `c1f8fe50...`; normalization `63448616...` | 12 archives; 48 files; 12 reconstructions; zero duplicate/cross-role overlap; exact replay; desktop and narrow render; 40 focused tests | `pass-independent-qa-authorize-baseline-preregistration-only` | `P2O5-T03-U05` |
| `P2O5-T03-U04-SUITE-R001` | committed checkpoint `289ed09b7760a0f2e00efbdbf8f4939dd8aa5b04` | 683 pass / 1 expected skip / 228 warnings / 86 subtests | full clean repository regression passes in 713.56 seconds | `pass` | U04 record sync |

Accepted r004 independently reconstructs all 287 core pixels and 531 unknown
ring pixels. Only locked training pixels create normalization statistics.
Validation and test pixels remain excluded from those statistics.

Test integrity reconstruction emits no test image, distribution, statistic, or
metric. Analytical test-open count remains zero. No baseline, model, metric,
training authorization, inference, deployment, or external submission
advances.
