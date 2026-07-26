# PRECHECK-2026-002 — P3O1-T01 U03 protocol and preflight

**Recorded:** 2026-07-25

**Issue / branch:** #566 / `codex/p3o1-t01-bounded-unet-milestone`

**Exact source:** `fbb2e923ae7f9ca9ed7dbb317e4235a236ae2411`

**Run:** `BL-2026-07-25-p3o1-t01-u03-preflight-r001`

## Entry

U01 and U02 pass. The locked Windows CPU environment, exact Phase Two
dataset/split/normalization/baseline/training-contract bindings, and the
117,473-parameter reference implementation remain unchanged. U03 may open only
the frozen Green Ridge/Tepee training arrays and Grandview/McKay validation
arrays. Ward Creek and Windigo test arrays must remain unopened.

## Frozen contract

`BOUNDED-UNET-EXPERIMENT-PROTOCOL-2026-001` fixes one CPU model, seed
`20260725`, float32, deterministic fail-closed algorithms, one thread per Torch
pool, batch four, Adam at `0.001`, exact masked BCE, no shuffle or augmentation,
maximum 200 epochs, patience 25, and checkpoint ordering by validation
event-class macro Dice, IoU, masked BCE, then earliest epoch. It authorizes
exactly one substantive U04 run and no architecture, loss, imbalance,
threshold, seed, augmentation, or hyperparameter alternative.

The U05 test-opening mechanism requires an exact authorization record in the
frozen directory, status `AUTHORIZED_NOT_OPENED`, zero prior openings, one
authorized opening, exact config/weights/selection/environment hashes, and the
exact four-patch Ward Creek/Windigo roster. Missing or mismatched evidence
fails before `numpy.load`; a no-overwrite receipt is mandatory after opening.

## Observed preflight

The exact two-epoch train/validation preflight uses four training patches / 109
core pixels and four validation patches / 89 core pixels. Epoch two records
train masked BCE `0.6991592645645142`, validation masked BCE
`0.6716660850503472`, validation event-class macro Dice
`0.392018779342723`, macro IoU `0.3301282051282051`, and worst-event macro
Dice `0.3333333333333333`. No weight or checkpoint is retained, and the smoke
is not the substantive experiment.

The exact HTML renders at desktop and 390-by-844 widths without horizontal
overflow. The 1,800-by-1,120 PNG loads completely; both epoch rows render; no
external resource or browser log appears; and the page visibly states the
no-model, unopened-test, prototype-label, and no-independent-ground-truth
boundaries. The in-app browser timed out while capturing the narrow screenshot,
although its rendered DOM dimensions and content were verified. Direct
`file://` navigation was browser-policy blocked and was not bypassed.

## Exact replay

A fresh detached worktree at the source commit regenerated the 12,308-byte
protocol, 9,343-byte JSON, 3,544-byte HTML, and 77,226-byte PNG with exact
SHA-256 equality. It passed 28 focused model/protocol/readiness/baseline tests,
compilation, `uv lock --check`, and `git diff --check`. The detached worktree
was then removed.

The first U03 test attempt retains one brittle prose-phrase assertion failure;
the corrected test checks the actual explicit unopened-test language without
changing model or render behavior.

## Decision and boundary

U03 passes with a narrow-screenshot tooling limitation. It creates no
substantive training run, candidate checkpoint, promoted weight, test metric,
model-value claim, inference, deployment, or submission-ready claim. Dataset,
split, labels, normalization, and baseline remain frozen.

The next eligible unit is P3O1-T01-U04: exactly one substantive training run,
complete validation history, and validation-only candidate freeze under the
exact U03 protocol. The test role remains sealed.
