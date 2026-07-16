# Dual-Lock Custody Readiness

BurnLens had one safely locked response but no tested way to combine its historical receipt with the receipt a future second response should receive. Issue #394 fixes only that custody seam.

The historical first receipt remains frozen at its original v0.2.0 / BurnLens 0.15.0 identity. The live receipt builder now defaults to v0.3.0 / BurnLens 0.17.0, and historical browser reconstruction passes its legacy identity explicitly. A new independent verifier opens two private pairs, recomputes both 56-unit contracts, verifies packet and receipt bindings, checks chronology and distinctness, then publishes only content-withheld custody evidence.

The real readiness run combines the actual first private pair with the already-classified browser software fixture. That is deliberate: it proves compatibility without fabricating a second reviewer. The result remains one returned-response origin plus one software fixture, and the fixture cannot authorize reveal.

![BurnLens dual-lock custody readiness](../../samples/labels/review/phase-two/LABEL-REVIEW-DUAL-LOCK-READINESS-QA-2026-001.png)

All 163 tests pass. Two detached-source fixed-epoch wheels from reviewed candidate head `125fcc677cba114277b8a066709d753c54ba619c` are byte-identical at 302,018 bytes / SHA-256 `cac65ceaf6ce75ef67d16d55379df9234a591563c94800791d972965281f80d2`. An isolated install reports BurnLens `0.17.0`, all 27 console entry points, and no private/download entries. PR #395 merged at `eb84aad222a07b89f03a892c2cc0df9540b20d25`; a fresh remote-main clone repeats the gates; annotated tag object `8fca2a51548690b710ad3903a19312e77c748420` peels to that merge.

The next scientific action has not changed. A second qualifying reviewer must return a completed response. BurnLens must lock those exact bytes before a separate reveal, comparison, and adjudication checkpoint.
