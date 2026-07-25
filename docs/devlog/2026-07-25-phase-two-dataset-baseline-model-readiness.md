# Phase Two dataset, baseline, and model-readiness package

BurnLens now has an accepted prototype dataset package instead of only a
passing sufficiency candidate.

P2O5-T03 freezes the input and evaluation contract, ranks all valid
whole-event assignments before patching, and locks Green Ridge plus Tepee for
train, Grandview plus McKay for validation, and Ward Creek plus Windigo for
test. Darlene remains preserved and excluded.

`burnlens-dataset-v0.1.0` contains twelve native-grid 64-by-64 patches, 287
selected core pixels, and 531 unknown-ring pixels. The rings retain value 2
and remain outside loss and metric masks. The materializer never resamples the
source grid.

Independent QA rehashes twelve registered Sentinel archives totaling
13,633,040,965 bytes and reconstructs all patches without importing the
materializer. It verifies schema, domains, grids, masks, class counts,
duplicates, cross-role overlaps, source-product separation, and train-only
normalization. The accepted QA run replays JSON, HTML, PNG, and normalization
bytes exactly and passes desktop and narrow rendering.

The baseline protocol is committed before arrays open. RBR, dNBR, and dNDVI
fit on train and select on validation. RBR threshold
`0.041043221950531006` is frozen before the single test opening. It classifies
all 89 selected test cores correctly and remains selected by validation
precedence.

That perfect selected-core result has a deliberate warning. Candidate
construction used optical and official-reference evidence and may favor the
measured spectral separability. It does not measure unknown rings, unreviewed
pixels, complete burn scars, natural class prevalence, independent truth,
field validation, or generalization.

U06 therefore authorizes one rejection-first experiment. After the coherent
U07 release is verified, Phase Three may train exactly one small CPU-only
U-Net with frozen channels, masks, normalization, architecture, optimizer,
seed, validation selection, and model-test rules. There is no search,
augmentation, test tuning, or second model. Matching RBR is a valid trained
result but not added value. A weaker or invalid model is rejected.

No model, weights, training run, model evaluation, inference, deployment, or
final-submission-ready claim exists at this checkpoint.

Release QA retains two reviewer-page failures before accepting report
`2026-004`: one positional binding error and one missing explanation of
candidate-selection bias. The accepted page replays exactly and passes real
desktop/narrow rendering, both images, evidence links, keyboard order,
privacy, and zero-external-request gates.

Canonical release QA also retains one wrong lean-profile invocation and one
full-suite run with two stale release-contract assertions. After the explicit
105-command and LF-checkout corrections, the complete suite passes 695 tests,
one expected skip, 228 warnings, and 86 subtests.

Two fixed-epoch Git-archive builds produce identical 1,050,456-byte BurnLens
0.52.0 wheels at SHA-256 `eff2396b...`. An isolated CPython 3.12.10 runtime
loads 13 compatible distributions and all 105 command help routes. Merge,
fresh-main repetition, and remote annotated-tag verification remain required
before this becomes a verified release or Phase Three training begins.
