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
