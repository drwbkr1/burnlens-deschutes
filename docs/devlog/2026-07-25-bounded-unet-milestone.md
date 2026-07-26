# Bounded U-Net milestone

## 2026-07-25 — the environment comes before the model

BurnLens now has a real, opt-in Windows CPU environment for its one authorized
U-Net experiment. PyTorch is not a loose workstation install: the lock names
the exact CPython 3.12 Windows wheel, the repository setup refuses lock drift,
and the offline verifier proves that the installed build is CPU-only before
any model code exists.

The small smoke is intentionally stricter than an import. It enables
deterministic algorithms in fail-closed mode, pins both PyTorch thread pools to
one, runs the same generated convolution twice, and requires the exact finite
bytes to match. A fresh detached checkout reproduces that result while loading
all 105 shipped BurnLens commands from the installed package.

The dependency audit also found something worth keeping visible. The exact
setuptools version frozen by Phase Two has a source-distribution advisory.
BurnLens does not exercise that path: this is Windows, there is no
`MANIFEST.in`, all tracked paths are ASCII/NFC, and this milestone does not
build an sdist. Rather than erase the finding, U01 turns those facts into a
documented boundary and a future stop condition.

No dataset array has been opened. No model, checkpoint, training curve, or
metric exists yet. U02 can now implement the frozen reference path without
guessing which framework build or execution posture it means.

## 2026-07-25 — one reference path, still no experiment

The reference model is deliberately unsurprising: two encoder levels, one
bottleneck, two skip-connected decoder levels, and one binary logit. More
important than novelty is what surrounds it. Every array is checked against
the frozen manifest before opening; normalization comes only from the locked
training record; unknown, invalid, nodata, and excluded pixels cannot enter
loss or metrics; and a request for the test role fails before NumPy is called.

The tests now exercise a complete forward/backward step, mask exclusion,
finite gradients and weights, deterministic replay, early-stop ordering, and
checkpoint recovery. They also run one ephemeral step on the real permitted
training patches and a forward-only validation pass. That proves the pieces
connect without turning the smoke into the substantive experiment.

Two small failures stay visible. The first test guessed the total number of
PyTorch module containers instead of checking the actual architecture. The
test was corrected to count convolutions, transposed convolutions, pools, and
parameters. The first pushed file also had one extra blank line at EOF; a
separate cumulative fix closes that formatting gate.

No weight or checkpoint from these smokes is retained as a model. Ward Creek
and Windigo remain sealed. U03 must now freeze the complete experiment and the
only mechanism that can eventually open them.

## 2026-07-25 — the experiment is frozen before it is run

U03 makes the substantive experiment deliberately boring before it becomes
expensive: one seed, one CPU, one model, one optimizer, one threshold, one
stopping rule, and one checkpoint order. It also turns the future test opening
into a concrete authorization object bound to exact config, weights, selection,
environment, and roster hashes. A missing or drifting object fails before any
test array is opened.

The two-epoch preflight is connectivity evidence, not a model. It opens only
the frozen train and validation roles, records every event/class denominator,
renders the trajectory, and then discards the ephemeral state. Its validation
Dice stays flat while BCE improves enough to select epoch two under the frozen
tie-break. That observation is useful for proving the rule executes, not for
claiming model quality.

The exact protocol and three preflight surfaces reproduce byte-for-byte in a
fresh detached worktree. Desktop and narrow rendering have no horizontal
overflow or external resource, and the page keeps the model, sealed-test, and
ground-truth limitations visible. Narrow screenshot capture timed out in the
browser tool, so that width is retained as direct rendered-DOM evidence rather
than overstated as a captured-image pass.

Ward Creek and Windigo remain unopened. No substantive training, weight,
checkpoint, model evaluation, inference, or portfolio-readiness claim exists.
U04 can now run the one authorized experiment without revisiting its design.

## 2026-07-25 — the first candidate is useful because its weakness is visible

The one substantive run is complete. It trains for 35 epochs, stops under the
frozen patience rule, and selects epoch 10 without opening the test role. The
candidate looks strong on Grandview's balanced validation evidence, then
collapses to all-burned predictions on McKay. That contrast is more valuable
than the aggregate alone: it makes the model's event sensitivity inspectable
before anyone can mistake a single validation score for generalization.

The run also closes a reproducibility loop around the actual training process.
Every epoch has an append-only record, the ignored run has a canonical
inventory hash, and the promoted configuration, complete history, selected and
final checkpoints, model-only weights, JSON, HTML, and PNG each have exact
receipts. Independent checks recompute selection and early stopping and reload
the retained states.

The rendered page keeps the warning next to the result: these are
owner-approved prototype labels, not independent ground truth, and the sealed
test still has not been opened. Desktop and narrow layouts preserve the full
history with contained table overflow. The browser tool could not complete a
horizontal-scroll gesture, so the measured overflow is retained as a tool
limitation rather than overstated as an interaction pass.

This is a candidate, not an accepted or released model. U05 is now the single
high-risk gate: one exact, authorization-bound test opening against Ward Creek
and Windigo, with no retry or tuning path.

## 2026-07-25 — rehearse the dangerous path without touching the test

The U05 evaluator now exists, but it first runs against validation only. That
rehearsal caught three reviewer-visible problems before the irreversible
opening: a long status escaped the narrow viewport, patch annotations covered
their imagery, and generic production wording falsely implied the sealed test
had already opened. Each failure remains named; the final renderer says exactly
what it is—a validation-only preflight with open-count zero.

The scientific path is equally explicit. The evaluator cannot accept any four
patch IDs merely because the count matches. It requires the ordered manifest
roster, exact candidate hashes, a clean source commit, one fixed threshold, and
an opening ID that has never acquired a consumed receipt. Its outputs preserve
probabilities and decisions per patch, class denominators, threshold
diagnostics, descriptive probability status, and the comparison the portfolio
needs: a trained result may be valid while still losing to the perfect frozen
RBR baseline.

The exact source and rendered preflight now replay byte-for-byte. Ward Creek
and Windigo are still sealed. The next commit will be intentionally small: the
single authorization object that makes the one-way test opening possible.

## 2026-07-25 — the model fails honestly, and that is the result

The opening is consumed. On Ward Creek and Windigo, the selected U-Net predicts
every one of the 89 reviewed cores as burned. It catches all 39 burned cores
and misclassifies all 50 background cores. The resulting event-class macro Dice
is 0.299, far below the transparent RBR baseline's 1.0.

That is not the portfolio story we might have preferred, but it is a stronger
engineering story than a tuned or hidden failure. The configuration, weights,
threshold, roster, and code were frozen first. The page makes the failure
visual: the two burned patches are green in the error view, while both
background patches are red. Fixed-threshold diagnostics also show that the
probabilities have not learned a useful separation—0.25 and 0.50 predict all
burned, while 0.75 predicts none.

Every probability and binary array is retained with an exact receipt, the
single opening has an immutable consumed record, and independent checks
recompute the class denominators and baseline decision without reopening the
source test arrays. The candidate is trained and evaluated, but it is not
accepted or released and it is not the analytical winner.

The final Phase Three unit now has a crisp job: reproduce the training bytes,
package this valid rejected-model evidence, write the model card and inference
contract, and choose a Phase Four path that demonstrates the model honestly
without pretending it outperforms the baseline.
