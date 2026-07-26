# PRECHECK-2026-003 — P3O1-T01 U04 substantive training

**Recorded:** 2026-07-25

**Issue / branch:** #566 / `codex/p3o1-t01-bounded-unet-milestone`

**Exact source:** `5179a745f091c29d095461d511633f055967ef91`

**Run:** `BL-2026-07-25-p3o1-t01-u04-training-r001`

## Entry

U01-U03 pass and are remote-equal. The exact dataset, whole-event split,
train-only normalization, baseline, model environment, 117,473-parameter
implementation, frozen protocol, and one-test-opening mechanism remain
unchanged. The substantive run started from a clean remote-equal source commit.
It could open only four Green Ridge/Tepee train patches and four
Grandview/McKay validation patches. Ward Creek and Windigo remained sealed.

## Retained pre-training failures

The first focused suite retained five failures: two synthetic fixtures used an
outdated `ModelExample` shape, while three environment-profile checks observed a
stale editable install that did not expose the new command. The fixtures were
corrected and the canonical environment was resynchronized from the exact lock.
The corrected suite passed 29 tests with one expected geo-profile skip.

A fresh detached worktree at the source commit rebuilt the 28-distribution
model profile, exposed all 107 installed commands, passed deterministic CPU
smoke and 35 focused tests, and passed compilation, lock freshness, diff, and
real train/validation entry checks. No substantive run had occurred before
these gates passed.

## The one substantive run

The only authorized run trained for 35 append-only epochs and stopped early
under the frozen patience rule in 18.76287959999172 seconds. Epoch 10 was
selected by the preregistered validation order. It records train masked BCE
`0.6315077543258667`, validation masked BCE `0.6219634259684702`, validation
event-class macro Dice `0.7253521126760564`, macro IoU
`0.7051282051282051`, and worst-event macro Dice
`0.4507042253521127`.

Grandview's 25 background and 25 burned validation cores are all classified
correctly. McKay exposes the material weakness: the selected checkpoint predicts
all 39 validation cores as burned, including seven background cores, for event
macro Dice `0.4507042253521127` and macro IoU
`0.41025641025641024`. These are validation diagnostics, not generalization or
test results.

## Custody and independent checks

The ignored run directory retains 43 files / 3,592,037 bytes, including 35
append-only epoch records. Its canonical sorted inventory is 4,030 bytes with
SHA-256
`e260d8b98b20b523f7b636bb95a179a13addfb7441f853bdeebaa1b7d2f54b19`.
The nine promoted candidate artifacts have exact size/hash receipts.

Independent verification matches all nine receipts, all 35 epoch records, the
epoch-10 selection, and the epoch-35 stopping point. Selected and final
checkpoints reload, selected model-only weights equal the selected checkpoint's
model state, and the selected and final states differ as expected.

The exact HTML passes direct desktop and 390-by-844 rendered inspection. It has
no document overflow, complete chart and 35-row history, no external resource
or browser log, and visible candidate, sealed-test, prototype-label, and
no-model-value boundaries. Narrow table overflow is contained. The browser tool
did not complete a horizontal-scroll gesture, and unreliable full-page tiling
was not treated as rendered evidence.

## Decision and boundary

U04 passes as a validation-only frozen candidate. It is not an accepted or
released model and makes no model-value, ground-truth, field-validation,
operational, or portfolio-readiness claim. No test array, test metric,
inference, deployment, second model, or hyperparameter search exists. Dataset,
split, labels, normalization, and baseline remain frozen.

P3O1-T01-U05 becomes eligible only after these exact candidate and evidence
bytes are committed and pushed. U05 may then create the exact
`AUTHORIZED_NOT_OPENED` authorization bound to config, weights, selection,
environment, and four-patch Ward Creek/Windigo roster before the single
permitted test opening.
