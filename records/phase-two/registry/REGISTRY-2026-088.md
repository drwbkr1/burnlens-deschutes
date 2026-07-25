# REGISTRY-2026-088 - P2O5-T03 U05 non-model baseline

**Recorded:** 2026-07-25

**Issue:** #562

| Unit | Run / source | Inputs / outputs | Gates | Disposition | Next dependency |
|---|---|---|---|---|---|
| `P2O5-T03-U05-PROTOCOL-R001` | `BL-2026-07-25-p2o5-t03-u05-preregistration-r001`; `b4720ca...` | protocol 6,301 bytes / `31eb08ae...` | primary sources; formulas; rosters; fit/select/metric/test contract; exact replay; zero arrays opened | `pass-test-sealed` | train/validation selection |
| `P2O5-T03-U05-SELECTION-R001` | `BL-2026-07-25-p2o5-t03-u05-selection-r001`; `f48ef98...` | selection 37,091 bytes / `061596f7...` | train-only thresholds; validation-only family choice; RBR threshold 0.041043221950531006; exact replay; test unopened | `pass-selection-frozen` | commit before test open |
| `P2O5-T03-U05-EVALUATION-R001` | `BL-2026-07-25-p2o5-t03-u05-evaluation-r001`; `220ce86...` | three retained outputs | frozen metrics complete; excluded nonfinite display cast warns | `remediate-retained` | neutral display fill |
| `P2O5-T03-U05-EVALUATION-R002` | `BL-2026-07-25-p2o5-t03-u05-evaluation-r002`; `f1406b3...` | three retained outputs | exact metrics/replay/render pass; selection-bias limitation omitted | `remediate-retained` | explicit limitation |
| `P2O5-T03-U05-EVALUATION-R003` | `BL-2026-07-25-p2o5-t03-u05-evaluation-r003`; `bfd5c6c9a137b0888d9678b176cf2412a1e18805` | JSON `a8ba82f9...`; HTML `109075ca...`; PNG `49bf3686...` | unchanged analytical result; exact replay; desktop/narrow render; 33 focused tests; complete limitations | `pass-reproducible-non-model-baseline-evaluation` | `P2O5-T03-U06` |

The single analytical test opening fixes 89 cores across Ward Creek and
Windigo. RBR, dNBR, and dNDVI each score 1.0000 event-class macro Dice and IoU.
The selected RBR retains validation precedence; test results do not reselect a
family.

Perfect selected-core classification is not a generalization, natural
prevalence, complete-scar, independent-ground-truth, or field-validation
result. Model creation and training authorization remain false.
