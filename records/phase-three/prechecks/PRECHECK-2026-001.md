# PRECHECK-2026-001 — bounded U-Net environment

**Date:** 2026-07-25

**Issue:** #566

**Unit / run:** `P3O1-T01-U01` /
`BL-2026-07-25-p3o1-t01-u01-environment-r001`

**Exact source commit:** `ddf32dbfee5a29e0fe362859c456e7a362fee20c`

**Exact base:** `c290e90c76e29c2bd33423f5c51878c950412b1d`

**Disposition:** `pass`

## Entry and source gates

Verified BurnLens 0.52.0, the frozen dataset/split/normalization/baseline/training
contract hashes, issue #566, and the exact branch base all match. U01 hashes
those Phase Two artifacts without opening any train, validation, or test NumPy
array.

Fresh primary-source checks bind PyTorch 2.13.0, its exact 122,057,313-byte
CPython 3.12 Windows wheel at SHA-256 `024c6cc0...`, its composite license
expression, deterministic-operation limits, Windows execution guidance, and
uv locked-sync behavior. The exact setuptools 82.0.0 wheel is 1,003,468 bytes
at SHA-256 `70b18734...` under MIT.

The live audit reports one disclosed setuptools finding,
GHSA-h35f-9h28-mq5c / CVE-2026-59890. Its vulnerable path requires an sdist,
`MANIFEST.in` exclusions, and normalization-preserving macOS filenames. This
checkpoint is Windows/NTFS, has no `MANIFEST.in`, has 1,656 ASCII/NFC tracked
paths, and forbids sdist creation. That resolves current applicability without
calling the environment vulnerability-free. An sdist, macOS evidence run, or
manifest exclusion is an explicit future stop trigger.

## Locked execution proof

The opt-in `model-research` profile resolves 94 universal lock records and
installs 28 Windows distributions. The exact `uv.lock` is 259,657 bytes at
SHA-256 `87afed69d2b6823abe4eb7b8aea012b21893887d6e09472e9afbfcf38e181eba`.

The installed runtime is PyTorch `2.13.0+cpu`, build commit
`cf30153c4c131c8164ee7798e5022d810682e2cb`, with MKL, MKLDNN, OpenMP, and
AVX2. CUDA build identity and availability are both absent. The verifier sets
seed `20260725`, deterministic algorithms on with `warn_only=False`, and both
thread pools to one. Two synthetic CPU convolutions reproduce SHA-256
`0640f0d2...` exactly and remain finite.

A retained first combined validation attempt timed out without a conclusive
aggregate result. Bounded reruns then pass structural gates, compilation, lock
freshness, diff hygiene, and the exact model smoke. A fresh detached worktree
at the pushed source commit creates a new `.venv` from the lock, passes
dependency integrity, verifies all 105 installed command launchers, repeats the
CPU primitive, and stays clean at the exact source commit.

## Boundary and next dependency

U01 creates no model code, weights, training run, dataset change, split change,
label change, baseline change, test opening, inference, deployment, provider
transaction, or claim of model value. U02 may implement exactly the frozen
single U-Net, loader, masked loss, and metrics with synthetic and permitted
train/validation evidence only.

## U02 addendum — reference path

Exact cumulative source `552f47d629f275fc732a36d9d7362b3e3ffc40a8`
implements the frozen 117,473-parameter U-Net, manifest-bound loader, exact
normalization and mask, masked BCE, finite checks, Adam, early stopping,
checkpoint recovery, and unconditional pre-U05 test lock. The implementation
is 23,729 bytes / SHA-256 `36bedaf8...`; its test module is 11,764 bytes /
SHA-256 `d92fbad4...`.

The initial focused suite retained one bad test assertion about total module
containers; exact layer-type and parameter-count assertions replace it. A
formatting-only EOF warning is retained and corrected in the cumulative source
commit. The fresh detached model profile passes 24 bounded-model,
model-readiness, and baseline tests after its complete 105-command environment
verification.

Synthetic one-step replay produces identical loss and state bytes twice. A
separate warnings-as-errors smoke performs one ephemeral optimizer step on the
four permitted train patches and one forward-only validation evaluation. It
uses 109 train and 89 validation core pixels and produces finite loss and
metrics. This is implementation evidence, not the substantive U04 training
run, and no checkpoint or weight is promoted.
