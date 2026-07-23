# PRECHECK-2026-063 - Windigo exact owner-review handoff

**Unit / issue / branch:** `P2O4-T35-U05` / #534 / `codex/p2o4-t35-windigo-deadline-gate`

**Surface run:** `BL-2026-07-23-windigo-owner-review-surface-r002`

**Source code:** `b393886c3ceb0d6d07604c728715febb699070fc`

**Disposition:** `AWAITING_EXACT_OWNER_RESPONSE_KEEP_LOCK_REVEAL_RECONCILIATION_CLOSED`

## Exact contract

U05 preparation opens only the two U04 candidates:

- `WDP-001`, proposed burned, review binding `31cd729bfa466f50145af60de680aa7fc42aadf6cb33d3ce523d6a6fbbd0296d`;
- `WDP-002`, proposed background, review binding `ec56acd1c1812f4ec8b3eda872adf86205e5fe87626c185203f6360872881ec2`.

Both belong to event group `windigo-2022-OR4336312205020220730`. The ordered manifest is `58efe73c109f4f9197952bfb9a11103223e3d34f9cd006b686fc124fa2ce1728`. The two-candidate batch uses the explicit `single-event-pair` exception.

Each card preserves its proposed class, U04 proposal hash, candidate-raster hash, source basis, limitations, core size, unknown-ring size, fixed dNBR interval, deterministic tie, and a separate exact evidence image. No confidence, prior decision, or cross-milestone candidate appears.

## Interaction and custody gates

| Gate | Result |
|---|---|
| roster and bindings | pass: exactly `WDP-001`, then `WDP-002`; one burned and one background; no duplicate or foreign candidate |
| blank state | pass: two null decisions, false attestation, null timestamps, zero owner responses, and zero labels |
| decision domain | pass: one candidate-specific yes/no/uncertain control per card; no bulk action, prefill, or missing-as-uncertain behavior |
| evidence | pass: separate exact optical/reference crop per candidate with descriptive alternative text |
| draft/final contract | pass: hash-named drafts and finals, strict load validation, one batch attestation, candidate-level final summary, and browser lock |
| response custody | pending owner: no owner response has been received, locked, or revealed |
| privacy/security | pass: localhost-only manifest-bound transport serves three exact resources; no recipient, private route, secret, cookie, or raw provider byte is tracked |
| desktop render | pass: actual in-app browser at 1,280 by 720 has 1,265-pixel page width and no page overflow |
| narrow render | pass: actual Chromium at 390 by 844 reports 390-pixel client and scroll widths; navigation and blank-error focus pass |
| reproducibility | pass: production and replay reproduce all six files byte for byte |
| promotion | closed: no owner decision, label, event acceptance, dataset, split, baseline, model, or metric |

The review-control self-test also passes blank preparation, exact-byte lock before reconciliation, aggregate reconciliation, ambiguity refusal, and missing-decision rejection.

## Retained failed attempt

R001 at source `73c5dadef89c95df30d338e2a3a03158b758285b` put both evidence images under an `evidence/` subdirectory. The hardened loopback preflight rejected it with `REVIEW_SURFACE_RESOURCE_NOT_SIBLING:evidence/WDP-001.png`. No server opened and no owner response existed. Its ignored local files remain immutable failure evidence.

R002 flattens only those two image paths and adds the exact preflight as a regression test. No scientific value, candidate, question, source role, or decision contract changes.

## Software fixture boundary

One browser-only software fixture tested two explicit choices, the final summary, hash-named download, completed-response validation, and session lock. It was 1,151 bytes / SHA-256 `b07988f114ec142705a69c14d7137c0d9ee52a396d5001c2ff8ac699bdb30299`.

The fixture was marked `SOFTWARE FIXTURE ONLY - NOT HUMAN EVIDENCE`, validated as one yes and one uncertain choice, and deleted from Downloads immediately. It was never copied, locked, ingested, committed, or treated as owner evidence. The real surface was reloaded to its blank state.

## Exact r002 outputs

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| report JSON | 13,597 | `507a23044b2285462e5c5f7573111fbbb8a5fa52aae11a2956b99c9d8b936e12` |
| HTML | 18,625 | `f46a24dd0b81d225a5b640cc61aa66cc0084308ba8e27dcb74b955f1f186d04b` |
| batch manifest | 5,553 | `5d6ef3909c8a27cc184fe897b08fc592753071f0fb322a6d22834fa29f4723cd` |
| blank response template | 1,017 | `ce881ef9915c60a2a1ffb5cee2a7eacb2e2d8c3546c0aa6254e92f3800712749` |
| `WDP-001` evidence PNG | 25,006 | `dc8df7796e94aca454c98f5b36ff923214cd2d06144102261eaab568d5eba7da` |
| `WDP-002` evidence PNG | 25,418 | `1069390aec07a9fa16157e1667d501a3d08ce491c5bb9e260caed3935a4b0e97` |

## Validation and stop

- owner-review batch, Windigo adapter, and hardened server: 28 tests and 37 subtests passed;
- environment profile: five tests passed with all 85 commands;
- full repository suite: 569 passed, one expected skip, 20 retained warnings, and 86 subtests passed in 470.47 seconds;
- frozen lock, compilation, CLI, exact loopback snapshot, desktop interaction, narrow interaction, replay, and software-fixture cleanup: pass.

U05 now stops for the owner. The owner must review both exact cards, choose yes/no/uncertain for each, attest, review the candidate-level summary, and export the exact final response.

After return, BurnLens must gather every plausible final, lock exact bytes before reveal, reject roster or binding drift, and treat distinct valid finals as ambiguous until the owner designates one. No response or U06 decision may be inferred.
