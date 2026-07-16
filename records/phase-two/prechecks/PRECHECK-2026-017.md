# PRECHECK-2026-017 - Atomic Reviewer-Response Intake Entry Gate

**Issue / branch / base:** #402 / `codex/p2o4-t09b-atomic-response-intake` / `5b9e099913311c0ae8ec3040a700e3dc041435db`

## Cycle-start evidence

The current workbench, exact handoff archive, Chrome response roundtrip, first-response lock, and mixed-version dual-lock verifier all pass. The project still has one returned independent response. No second human response exists and the reveal remains operator-declared unopened. The owner subsequently waived reviewer two; issue #393 is superseded and issue #403 controls the replacement single-reviewer route.

The highest-leverage weakness is the operator seam between receiving a file and locking it. BurnLens `0.17.0` validates a response and writes a receipt, but it does not itself preserve the inbound bytes. A manual copy can select the wrong source, expose a partial copy, overwrite custody evidence, or let source bytes drift between validation and preservation.

## Frozen inputs

- Packet: `LABEL-REVIEW-PACKET-2026-001`; 56 review units; SHA-256 `77067063a769645af13886b6c87cc236a10e06199d091743908d63556e07637c`.
- Application: `label-review-handoff-workbench-v0.1.0`; local/offline, not deployed.
- First returned response: 16,443 bytes; SHA-256 `485e80f2563f8b723c16daa8b5e5a1172dd88e8f2a28a7dd8608c933fa64eed9`; exact bytes and receipt remain ignored/private.
- First returned-response count: one.
- Software fixture: 14,749 bytes; SHA-256 `aeb408873811dc3ce326078adc617d207a9cba6b3ce94539c8a012802ae5acec`; explicitly non-human.
- Operator-declared reveal state: `withheld-unopened-after-lock`.

## Primary technical research

Accessed 2026-07-16:

- Python 3.12 `tempfile`: secure temporary files can be created in a chosen directory, supporting same-directory custody staging.
- Python 3.12 `os.link`: hard-link creation fails when the destination already exists, supporting no-overwrite promotion on the current Windows/NTFS workspace.
- Python 3.12 `os.fsync`: flushed file data can be requested for durable write-through before promotion.
- Python 3.12 `shutil`: high-level copy helpers may copy content without preserving all platform metadata, so the custody contract should bind exact content bytes and hashes rather than imply complete filesystem-metadata preservation.

Official references:

- https://docs.python.org/3.12/library/tempfile.html
- https://docs.python.org/3.12/library/os.html#os.link
- https://docs.python.org/3.12/library/os.html#os.fsync
- https://docs.python.org/3.12/library/shutil.html

These APIs do not prove storage-device persistence, reviewer identity, reviewer qualification, source-history integrity before intake, or reveal history.

## Allowed action

Add one atomic, non-overwriting, ignored-storage intake command; preserve exact source bytes through same-directory temporary staging, flush/fsync, re-hash, current-contract validation, duplicate rejection, and receipt binding; retain historical receipt compatibility; and publish fixture-only content-withheld QA.

## Prohibited action

Do not alter or reopen the first response, create or impersonate a second reviewer, classify the software fixture as human evidence, open or release the reveal, compare responses, adjudicate, accept labels, create a dataset or split, train a baseline or model, deploy, or make accuracy, field, official, endorsed, emergency, or operational claims. Do not use `burnlens-site`.

## Entry decision

`PASS_ATOMIC_RESPONSE_INTAKE_ENTRY_GATE_FIXTURE_ONLY_NO_REVEAL`.

This checkpoint makes response custody safer. It does not create reviewer-two evidence or reduce the single-reviewer validation risk.
