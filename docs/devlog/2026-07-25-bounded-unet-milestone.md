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
