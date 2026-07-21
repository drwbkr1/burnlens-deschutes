# Owner Review Batching Contract

## Decision

BurnLens batches the owner's interaction and exact response custody, never the candidate decision or promotion gate.

The prospective contract is:

```text
review-ready candidates
  -> frozen ordered manifest
  -> one offline owner-review session
  -> one explicit decision per candidate
  -> one final attestation and exact response export
  -> exact-byte lock before reveal
  -> candidate-level reconciliation
  -> event-level completion decision
```

This contract is implemented prospectively by `burnlens/owner_review_batch.py` and `burnlens/owner_review_batch_lock.py`. Previously shipped 56-unit, six-region, Green Ridge, and Grandview surfaces remain immutable and continue to use their versioned generators.

## Current Petes Lake application

P2O4-T33-U09 must use one two-card surface containing only the exact U08 Petes Lake burned proposal and affirmative-background proposal for `event-petes-lake-2023`. Petes Lake must not wait for unrelated fires merely to reach the normal batch size.

The two owner decisions and all non-owner gates remain independent evidence records. The issue #521 exit is event-atomic: both exact classes and every applicable source, terms, custody, quality, uncertainty, leakage, response, and reproducibility binding pass together, or neither candidate is promoted as the sixth complete event.

U09A does not create that production surface. It supplies the reusable contract and synthetic QA while U01-U08 establish the real evidence.

## Batch-size policy

| Candidate count | Contract |
|---:|---|
| 4-6 | Normal future batch; no size exception. Usually two or three event groups. |
| 2 | Petes-style `single-event-pair` exception when one event has exactly one burned and one background proposal. |
| 1 or 3 | Allowed only with a recorded reason; never used to avoid a ready paired candidate. |
| 7-8 | Allowed only with an explicit recorded size exception. |
| 9 or more | Rejected. Create another milestone-authorized surface. |

An actual future multi-fire surface may be created only inside a milestone that authorizes every included fire. A batch never silently expands the active issue.

## Frozen manifest

Each surface begins from one ordered `burnlens-owner-review-batch-manifest-v0.1.0` manifest. It binds:

- surface ID, revision, run ID, milestone ID, issue, commit, and generation time;
- the ordered event groups and their contiguous candidate rosters;
- one neutral stable ID and proposed class per candidate;
- the disclosed question, proposition basis, facts, and limitations;
- exact proposal record, candidate raster, and evidence-image byte counts and SHA-256 values;
- canonical, portable relative paths with no traversal, URL metacharacters, platform-reserved names, or case-folded evidence collisions;
- a derived SHA-256 binding for each complete candidate record;
- one SHA-256 over the complete canonical ordered manifest;
- any non-default batch-size exception and any superseded surface identity.

Candidate order is explicit and immutable. Keeping each event group contiguous preserves necessary context; changing order, roster, proposal, raster, displayed evidence, question, limitations, or decision contract requires a new surface revision and new review.

The manifest accepts no confidence, preferred-outcome, prior-decision, or prefilled-decision field.

Before writing any surface output, the complete semantic surface must reconstruct from its embedded manifest and ordered hash. Evidence bytes are verified before output begins. A write failure removes only files created by that transaction, so stale or partial artifacts cannot be mistaken for a complete review surface.

## Owner interaction

The offline surface presents one candidate at a time, with Previous, Next, and Resume at first unanswered controls. It discloses the proposed class and relevant evidence because this is owner confirmation of a proposal, not independent annotation.

Every candidate has exactly three unselected choices:

- `yes`: the owner supports the disclosed proposed class; every non-owner gate remains mandatory;
- `no`: the owner rejects the proposal; BurnLens does not infer the opposite class;
- `uncertain`: evidence is insufficient or conflicting; the candidate remains excluded with uncertainty preserved.

Blank is not `uncertain`. An incomplete session is a draft and cannot be finalized.

The surface must not provide approve-all, bulk-fill, preselected answers, confidence-ranked ordering, prior decisions, preferred outcomes, or running yes/no/uncertain totals. It may show only completion progress.

## Localhost transport

P2O4-T33-U09B adds `burnlens-serve-review-surface` as the review transport for
generated surfaces. It does not change the manifest, candidate ordering,
response schema, decision semantics, exact export, or pre-reveal custody
contract.

The command requires one exact HTML file and its sibling output report. Before
opening a listener, it verifies the HTML and every referenced local resource
against exact byte-count and SHA-256 bindings, including an explicitly
hash-bound predecessor report when a current surface reuses earlier evidence.
It then preloads only the selected page and referenced resources as one
immutable session snapshot. Other report outputs, reveal pages, templates,
responses, receipts, repository metadata, raw custody, and directory listings
are not routes.

The selected HTML is the sole document route. Referenced resources must be
sibling static assets with safe, unambiguous names; secondary HTML, JSON/text
data, nested paths, duplicate HTML attributes, navigation/meta-refresh paths,
and sensitive reveal, response, receipt, intake, template, raw, private,
adjudication, or quarantine names fail before bind even when a report lists and
hashes them. A U09 production adapter must therefore emit sibling evidence
asset names when using the more general U09A manifest writer.

The listener binds directly and only to `127.0.0.1`. Port `0` uses one atomic
operating-system allocation; an occupied explicit port fails instead of
scanning or incrementing. A random per-session capability prefix is part of the
printed machine-readable URL. The server accepts only `GET` and `HEAD`, exposes
no CORS or upload endpoint, stores no response, suppresses request-path logs,
and serves fixed content types with no-cache, no-sniff, same-origin, and
no-external-connection browser policy headers. Ctrl+C ends the session and
releases the listener.

Localhost is transport within the existing offline owner-review model, not
public hosting or deployment. The browser still creates the exact hash-named
response as a local download; U10 remains the only route for locking and
interpreting returned bytes. A transport failure blocks the browser handoff
but cannot alter a source, proposal, owner decision, label, or scientific gate.

## Draft, finalization, and response schema

Hash-named drafts may contain unanswered candidates and may be reloaded only when every surface, manifest, roster, event, and candidate binding matches. Loading never converts a blank answer to `uncertain`.

A completed `burnlens-owner-review-batch-response-v0.1.0` response requires:

- the exact response schema, surface, run, revision, milestone, and ordered-manifest bindings;
- the exact ordered candidate IDs, event IDs, and candidate SHA-256 bindings;
- one allowed decision for every candidate;
- bounded notes strings;
- a timezone-aware start and completion time in valid order;
- one explicit owner attestation;
- a visible final candidate-by-candidate summary before export.

The final export is deterministic UTF-8 JSON with LF and a filename containing the first 16 characters of its whole-file SHA-256. Successful export locks response controls for that browser session.

## Pre-reveal custody

`owner-review-batch-exact-byte-lock-v0.1.0` validates only completion and immutable envelope bindings before interpreting decision or note values. Duplicate JSON keys, oversized inputs, altered surface contracts, tracked custody paths, and non-ignored custody paths fail closed. It then:

1. verifies the hash-derived source filename and bounded byte size;
2. verifies receipt time is not earlier than review completion;
3. requires repository-local ignored custody destinations;
4. writes the exact response without overwrite, flushes, fsyncs, and rereads it;
5. writes and verifies a separate receipt without overwrite;
6. rolls back newly created transaction files on a partial failure;
7. records `decisions_revealed: false`, `decision_values_read: false`, and `note_values_read: false`.

Only after this succeeds may a task-specific U10 adapter fully validate decisions and recompute non-owner gates.

Byte-identical duplicate final exports are idempotent. Two or more distinct envelope-valid completed exports for one surface are ambiguous and block intake until the owner explicitly designates the authoritative SHA-256. Timestamp order never silently selects an authoritative final.

## Registry and revision rules

The prospective registry contract records surface ID, revision, milestone, ordered-manifest SHA-256, candidate IDs and count, batch-size exception, state, and supersession. Admission reconstructs the complete surface first. Later revisions must point to the registered immediately preceding revision in the same milestone; an active or completed successor requires that predecessor to be marked superseded. The registry rejects:

- the same surface revision twice;
- one candidate in two active surfaces;
- a changed candidate or manifest hidden behind an existing revision;
- an invalid or unrecorded non-default batch size.
- a missing, cross-milestone, reused, or still-active predecessor for a promoted successor revision.

Completed and superseded entries remain auditable. Failed, rejected, or superseded evidence is not deleted to make the batch appear clean.

## Custody versus scientific disposition

The batch response and receipt form one atomic custody transaction. Scientific results remain candidate-specific: each decision and each non-owner gate is recorded independently. A later event adapter then applies the milestone's event-completion rule.

For Petes Lake, a candidate that individually receives `yes` but cannot complete the event must remain visible in private reconciliation as owner-supported but not promoted. It cannot enter the cumulative label set alone.

## Privacy and public boundary

Completed response bytes, receipts, notes, private paths, and candidate-level reconciliation remain ignored and private. A later public report may expose only aggregate-safe evidence required by the milestone.

Every applicable public surface uses this warning or a tighter equivalent:

> Experimental BurnLens CV output. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.

This route does not create independent ground truth, inter-rater agreement, consensus, field validation, official status, endorsement, a dataset, a split, a baseline, a model, an accuracy claim, or operational capability.

## Version and release effect

The prospective review protocol is `owner-confirmed-prototype-label-review-v0.2.0` because presentation ordering and response behavior materially change. The manifest, surface, response, registry, and lock contracts begin at their own `v0.1.0` identifiers.

U09A does not independently change BurnLens 0.44.0, create a tag, publish a GitHub Release, deploy, or create a lifecycle synchronization. The coherent P2O4-T33 milestone decides software and prototype-label artifact versions only at U11 after its actual success or material-decision exit is verified.

## U09 and U10 handoff

Once U08 has two exact review-ready proposals:

1. add a thin Petes Lake adapter that verifies the real proposal, rasters, evidence, warnings, and prior gates;
2. construct the one-event/two-candidate manifest with `single-event-pair`;
3. render and inspect the actual desktop and narrow-viewport surface;
4. reconstruct all tracked blank artifacts exactly from a clean checkout;
5. wait for explicit owner yes/no/uncertain decisions without inference or prefill;
6. use the generic pre-reveal lock, then a Petes-specific intake that recomputes all gates and enforces no partial event promotion.
