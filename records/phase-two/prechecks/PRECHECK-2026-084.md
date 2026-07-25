# PRECHECK-2026-084 - Ward Creek U06 exact response lock

**Date:** 2026-07-25
**Unit / issue:** `P2O4-T39-U06` / #554
**Run:** `BL-2026-07-25-ward-creek-owner-response-lock-r001`
**Source commit:** `d88e50df95467022d4a10f65f06aac6cd04bc014`
**Disposition:** `pass-decisions-unrevealed`
**Next dependency:** authorized aggregate reconciliation

## Content-withheld discovery

BurnLens enumerated every plausible Ward Creek response export in Downloads
without opening decision or note values. Exactly one candidate matched the
surface identity and review window.

The repository's pre-reveal validator proves:

- one completed response;
- one distinct exact payload;
- exact surface, run, revision, milestone, ordered-manifest, candidate roster,
  event-group, and candidate-binding matches;
- two response records in exact order;
- completed chronology and one owner attestation;
- a filename matching the exact response hash; and
- no ambiguity, decision access, or note access.

The exact response is 1,041 bytes at SHA-256
`aadd221da037ab7fc89bd04fb4532651b917190ac55e97ee7f4d5ce4eb951dbc`.
It is distinct from the removed 1,040-byte software fixture at SHA-256
`4eb36c4c38c149e1cfb23ead74cbf9a3e389194ef5a9372ad8b1b10749cf3cc2`.

## No-overwrite custody

The response was copied byte-for-byte into ignored, untracked,
repository-local custody with exclusive creation, flush, fsync, and exact
readback. The source rehash remained unchanged.

The private receipt is 2,692 bytes at SHA-256
`dba7d81aa21dde09b21d549dba7440363906ab3cebfb4d14e958588fb2efc4bf`.
It binds the exact surface and response, declares owner-returned origin, and
states `decisions_revealed=false`, `decision_values_read=false`, and
`note_values_read=false`.

The human-review control self-test passes blank preparation, exact-byte
lock-before-reveal, aggregate reconciliation, ambiguity detection, and
missing-decision rejection.

## Boundary

U06 exact-byte custody passes. The existing milestone authority permits
aggregate reconciliation only after this commit. Owner yes remains necessary
but insufficient; every non-owner gate must be recomputed.

No decision, note, label, dataset, split, baseline, model, metric, inference
output, deployment, or external submission is disclosed or advanced here.
