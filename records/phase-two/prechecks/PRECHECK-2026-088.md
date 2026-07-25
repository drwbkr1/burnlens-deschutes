# PRECHECK-2026-088 - BL-EXC-003 v0.51 checkout-byte correction

**Date:** 2026-07-25

**Issue / PR:** #558 / #559

**Exact base:** `7f7b332ed0cecccb7956d93bf7589f2d2497db03`

**Implementation commit:** `cb1f383c8f908882c4f83e8e75aa19c119e316a2`

**Disposition:** `candidate-pass-tag-withheld`

## Trigger and containment

PR #557 merged P2O4-T39 at the exact base above. Its first fresh-main Windows
checkout failed five tests and six test setups because 40 newly merged text
paths had working-tree CRLF bytes that did not match their exact bindings.
The accepted Git blobs and scientific outputs did not change.

BL-EXC-003 adds explicit checkout contracts. Immutable
`records/phase-two/prechecks/PRECHECK-2026-081.md` intentionally retains its
2,294-byte CRLF checkout identity at SHA-256
`057355ae3939cbe08403b9002faf3797220a250d4339ea122fc2c40b2872e865`.
Every other affected P2O4-T39 text path is explicitly LF.

The exception changes no source, terms, provider custody, candidate, owner
response, prototype label, readiness decision, dataset, split, baseline,
model, metric, inference, deployment, access, ownership, or public-sharing
state.

## Exact verification

- A new independent Windows clone at implementation commit `cb1f383...` is
  clean and passes four checkout-contract tests.
- The focused exact-binding gate passes 25 tests with two retained NumPy
  deprecation warnings.
- The full custody-backed suite passes 658 tests, one expected skip, 96
  retained NumPy deprecation warnings, and 86 subtests in 827.76 seconds.
- An isolated replay from scientific source
  `af37f80dd17febacfbb1cf2801665d74edb16475` reproduces all six accepted
  outputs byte for byte.
- Two fixed-epoch wheels remain byte-identical at 993,480 bytes and SHA-256
  `414fa8c118ac538239906c4b6e9437eaaeb07fd27be40b44c617415791674477`.
- A fresh CPython 3.12.10 lean runtime installs 13 compatible distributions,
  reports BurnLens 0.51.0, and passes all 99 command load/help probes.
- Draft PR #559 targets exact base `7f7b332...`; GitHub reports it clean and
  mergeable at initial remote head `cb1f383...`, with no configured checks.

## Scientific identities preserved

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `DATASET-CANDIDATE-2026-002.json` | 30,504 | `4a9646af493cdce81d0cd57405ebccf0dfecf5ca77c96930d0837c3b7d4e65f2` |
| `DATASET-READINESS-AUDIT-2026-002.json` | 6,601 | `50e3b9f3c6c33a9f8cd36cf0952bf5033c039e68ffc864bf952ddec5442e6ed4` |
| `DATASET-READINESS-DECISION-2026-002.json` | 7,088 | `39e7a56199f67bcf397b6d73e6795a2e36528ff0577b7314a8414f21321ce5d8` |
| Public JSON | 9,429 | `88cbe6ae01af322d7f80ff8a76b3dce698c08b53394a7e68faec2f5cb198ef0a` |
| Public HTML | 6,357 | `0fbdfd85a8055b2b560c7aac4d35424693ee60761a5f00f6f1b2f804e894c326` |
| Public PNG | 101,221 | `b20b3852d23185c2e0aa0f9b6cfd462b22eb98dbdbdaad5b8bb9bdeb43977761` |

The result remains six events, 12 balanced owner-approved prototype regions,
287 accepted core pixels, 531 excluded unknown-ring pixels, and 54 valid
whole-event assignments. `training_authorized` remains false.

## Remaining release gate

The annotated `v0.51.0-replacement-six-event-sufficiency` tag remains
withheld. PR #559 must merge, and corrected fresh main must repeat the
risk-matched checkout, focused, full-suite, replay, package, runtime, claims,
privacy, and remote-tag gates before the release becomes verified.
