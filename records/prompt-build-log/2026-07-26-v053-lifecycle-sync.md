# BurnLens 0.53 lifecycle sync

Issue #568 begins from verified merged main
`5a0f8ac027ae20ff9193948506f590afbfb64554`. Annotated tag object
`d66dd7fdc9f2f155d1799cb1e85e77dadd76311a` remotely peels exactly to that
checkpoint.

The sync updates current status, roadmap, changelog, version history, release
audit, living case study, reviewer quickstart, prompt/build log, and devlog.
It supersedes candidate and pending-release wording without changing any
scientific value. The `2026-006` candidate-era reviewer bytes remain
unchanged.

Fresh merged main passes 729 tests with one expected skip, 228 warnings, and
86 subtests in 802.35 seconds. It retains the exact model weights and reviewer
artifacts and reproduces two 1,106,162-byte wheels at SHA-256 `15b8b84f...`.
The isolated CPython 3.12.10 model runtime loads BurnLens 0.53.0, Torch
2.13.0+cpu, and all 107 command-help routes.

Lifecycle source `56ae10ac34fe585b1469b41f3ae3c60957e1881b` builds run
`BL-2026-07-26-v053-lifecycle-portfolio-r001`. The current `2026-007`
reviewer JSON is 9,861 bytes at SHA-256 `a8e38133...`; its HTML is 18,212
bytes at SHA-256 `81d32577...`. An ignored replay matches both outputs
exactly. Deterministic structural, source-binding, link, fragment, image,
claims, and privacy checks pass. The in-app browser security policy blocks
agent navigation to local `file:` pages, so exact owner-operated desktop and
narrow rendering remains the lifecycle pull-request gate; no workaround is
attempted.

One combined lifecycle wrapper later exceeds its 184-second limit while the
environment portability suite is still running. No analytical or public
artifact changes. A bounded rerun of the four directly applicable
dependency/lock/Codex-selector checks passes 4/4; unrelated runtime-profile
smokes are not repeated because the verified v0.53 release already passed
them and this sync changes documentation and presentation truth only.

The synchronized truth is precise: Phase Three is accepted and verified; the
U-Net is a valid trained, evaluated, reproducible, and rejected model artifact;
RBR remains the accepted analytical method; Phase Four may now execute the
baseline-primary/rejected-model-diagnostic route.

The owner directs the current project to complete that route without a Phase
3B remediation milestone and without deferring Phase Four. The U-Net failure
must remain a first-class technical result and must never be described as
outperforming RBR. Its lessons will appear only as recommendations for a
separately governed follow-on experiment; no planning or implementation of
that experiment is authorized in the current project.

No provider, custody, owner response, label, dataset, split, baseline,
software-version, model, training, inference, deployment, GitHub Release,
external submission, access, ownership, or public-sharing change occurs in
this sync.
