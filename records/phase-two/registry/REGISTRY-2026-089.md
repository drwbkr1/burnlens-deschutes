# REGISTRY-2026-089 - P2O5-T03 U06 model readiness

**Recorded:** 2026-07-25

**Issue:** #562

| Unit | Run / source | Inputs / outputs | Gates | Disposition | Next dependency |
|---|---|---|---|---|---|
| `P2O5-T03-U06-SOURCE-R001` | research at `2026-07-25T20:40:03Z` | tooling source 5,462 bytes / `5e55f5fb...`; zero retained third-party bytes | official PyTorch 2.13 docs; Windows/Python/CPU; deterministic/numerical/loss limits; compatible dry-run; no install | `pass-tooling-feasibility` | code-only audit |
| `P2O5-T03-U06-READINESS-R001` | `BL-2026-07-25-p2o5-t03-u06-readiness-r001`; `28c456b...` | five exact retained outputs | all analytical gates/replay and desktop pass; narrow document 409 / 375 CSS pixels | `remediate-retained` | wrap machine tokens |
| `P2O5-T03-U06-VERIFY-V001` | system-Python focused command | no product output | invalid environment lacks `rasterio`; locked-environment rerun passes 19 tests | `invalid-environment-retained` | use `.venv` only |
| `P2O5-T03-U06-READINESS-R002` | `BL-2026-07-25-p2o5-t03-u06-readiness-r002`; `4caf37e52591933c2c03ae050926d5123e47ed2f` | audit `eebd08f...`; decision `74fd1c21...`; contract `670dbb07...`; HTML `6e80c26c...`; PNG `6fc5d5b2...` | ten exact inputs; nine substantive gates; exact replay; 19 focused tests; desktop/narrow render; empty browser log | `authorize-bounded-unet-rejection-first` | `P2O5-T03-U07` |

Authorization is narrow and delayed until U07 is merged, tagged, and verified.
It permits one CPU-only U-Net experiment under the exact contract. No model,
weights, training run, model metric, inference, deployment, generalization, or
final-submission-ready claim exists.

RBR remains the accepted analytical method and already reaches 1.0 on the
frozen selected-core primary metrics. The model cannot numerically exceed that
baseline under the predeclared winner rule. Matching is not added value; a
weaker or invalid result rejects the model honestly.
