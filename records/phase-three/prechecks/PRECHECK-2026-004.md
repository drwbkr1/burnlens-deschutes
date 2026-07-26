# PRECHECK-2026-004 — P3O1-T01 U05 evaluator freeze

**Recorded:** 2026-07-25

**Issue / branch:** #566 / `codex/p3o1-t01-bounded-unet-milestone`

**Exact source:** `aa6b7f385224943a4550657318117dbec1b038c2`

**Exact preflight:** `BL-2026-07-25-p3o1-t01-u05-preflight-r005`

## Entry and boundary

U04 evidence commit `0f4cf0a96ac8507859e29653b0845c73bb92423b`
is remote-equal. Candidate config, selected weights, checkpoint selection,
environment, dataset, split, normalization, baseline, label schema, and exact
four-patch test roster remain frozen. This precheck reads only validation
arrays. Ward Creek and Windigo remain sealed at analytical open-count zero.

## Pre-open hardening

The authorization validator now compares the ordered patch IDs with the exact
manifest roster rather than accepting any list of four. A mismatch fails before
`numpy.load`. The evaluator also requires an exact clean Git HEAD, the frozen
output/run locations, all candidate hashes, and an unused opening ID. Any prior
ignored or tracked consumed-opening receipt blocks a retry.

The frozen implementation provides aggregate, event, and class support,
TP/FP/FN, Dice/IoU denominators, Dice, IoU, precision, recall, masked BCE,
selected-core area difference, worst-event evidence, fixed 0.25/0.50/0.75
threshold diagnostics, and descriptive ten-bin probability status. It saves
per-patch probability and binary-prediction arrays and renders pre/post
SWIR/NIR/red, probability, prototype-core, and error views with exact CRS,
transform, window, and 20-metre context.

## Retained pre-open attempts

- `P3O1-T01-U05-TEST-R001` fails during collection because the new module
  initially imported the environment path from the wrong module. No test ran
  and no dataset array opened. The import was corrected.
- `P3O1-T01-U05-PREFLIGHT-R001` completes validation-only computation, but the
  narrow document is 405 pixels wide in a 375-pixel client because an
  underscore-delimited status cannot wrap.
- `P3O1-T01-U05-PREFLIGHT-R002` fixes narrow overflow, but visual inspection
  finds patch annotations overlapping the image tiles.
- `P3O1-T01-U05-PREFLIGHT-R003` fixes the PNG layout, but its generic production
  wording falsely implies a test opening on the validation-only rehearsal.
- `P3O1-T01-U05-PREFLIGHT-R004` corrects those truth surfaces before the source
  freeze.
- `P3O1-T01-U05-PREFLIGHT-R005` runs from exact remote-equal source and passes.

These are code/render preflight attempts, not analytical test openings.

## Exact source and preflight evidence

| Path | Bytes | SHA-256 |
|---|---:|---|
| `burnlens/bounded_unet_evaluation.py` | 52,732 | `4184ba16c38a729cfa61c9055f931cadbc06423df7cf96365bad4caf0c941630` |
| `burnlens/run_bounded_unet_evaluation.py` | 3,746 | `2d787cb7aeef2e2e132736bc1d47b824c6487e7f2a07fabcdce3b16e2bcc0350` |
| `burnlens/unet_experiment.py` | 29,166 | `79ad51e6d2b8d77b93659e431d0f7a6abc83bdb816ecfb32ccddb60da8396011` |
| `tests/test_bounded_unet_evaluation.py` | 6,812 | `fe34a300aa35736e0edaf53be36c77779a8b0ee9d90f1f8a000b80246bab8135` |
| `tests/test_unet_experiment.py` | 8,971 | `06bdf99190477799bcad823190497eef4c86cceae0a0fa9e32aac2645983f376` |
| exact preflight JSON | 13,642 | `a9fbed1407357bba4839e6391feb99f7a3e347b56bf670dda48d42e23f61b3a9` |
| exact preflight HTML | 7,042 | `6bda457e7e4f09339face86033ef915f6281b54afcc8cc0bb7f5c07868f97959` |
| exact preflight PNG | 222,602 | `5b66f1e3ec17f9d86e07a8f49ca2f13b6c1c101154e903ab9b734068be51f1e4` |

The exact source passes 39 focused model/protocol/evaluator/readiness/baseline
tests, compilation, lock freshness, and diff checks. An independent second
validation-only execution with the same source, time, and run ID reproduces all
three preflight artifacts byte-for-byte.

The exact loopback HTML passes 1,265-pixel desktop and 390-by-844 narrow
inspection: no document overflow, complete 2,100-by-1,540 image, four internally
scrollable tables, no external resources, and visible validation-only,
zero-opening, no-ground-truth, and no-model-value boundaries. The PNG preserves
all four validation rows without annotation overlap.

## Decision

The U05 evaluator and no-retry opening mechanism pass pre-open gates. No test
array or metric exists. The next eligible action is to generate, inspect,
commit, and push one exact `AUTHORIZED_NOT_OPENED` record bound to config
`1f939540...`, weights `703d9257...`, selection `6dcae9af...`, environment
`009effea...`, events Ward Creek/Windigo, and the exact ordered four-patch
roster. Only then may the analytical opening occur once.
