# REGISTRY-2026-022 - Single-Reviewer Reconciliation Evidence

**Checkpoint:** Issue #403 / PR #412; lifecycle sync issue #413; next issue #411; branch `codex/p2o4-t10b-single-reviewer-reconciliation`; base `1c5cadcb6dca9664979ad87a3503f06aeea5fd0f`; source `fda69a60b0a5e350bfe10e7388571d7c1c103735`; public artifacts `57f116aabb7c15e5d0f9d88e8088d2e50c46eb7e`; reviewed candidate head `67216dc9952427a9c511eb871c12a87f94171bea`; merge `4918024dfb83270dbbd83a5880c455cc3c01771c`; verified tag object `5bb840b43ae8594e02a9b026b3932bb16f83bf5b`

| Artifact | Class | Version/state | Committed private/provider bytes |
|---|---|---|---:|
| Private reconciliation builder and CLI | Exact input re-verification, deterministic per-unit rule, atomic ignored preservation | BurnLens `0.20.0`; private report v0.1.0 | 0 |
| Private reconciliation | 56 unit-level source/proposal/reviewer/disposition traces | 72,628 bytes / SHA-256 `a04dd629551a2163e5e7a31f61c3aa95d4fdba136563f3a42940a2e9d1e9249d`; ignored/untracked | 0 |
| `LABEL-REVIEW-SINGLE-REVIEWER-RECONCILIATION-QA-2026-001` JSON/HTML/PNG | Aggregate-only public QA | Run `BL-2026-07-16-single-reviewer-reconciliation-qa-r001` | 0 |
| Installed-Chrome and evidence-card render checks | Real rendered output | Complete and readable; ignored screenshots only | 0 |
| Repository and package checks | Tests, compilation, dependencies, privacy, semantics, exact files, wheel | 181 tests; two clean-checkout identical 340,283-byte wheels; isolated 0.20.0 / 33 entry points | 0 |
| `MANIFEST-2026-022.json` | Exact three-output inventory and bounded release gates | Verified shipped checkpoint evidence | 0 |

One blinded response is reconciled. Six burned units are candidate evidence; fifty units remain ignored; no background candidate survives. No reviewer free text, unit identity, private filename, private path, response byte, receipt byte, authorization byte, private reconciliation byte, or provider byte is committed.

A fresh clean checkout passes 181 tests, compilation, dependency health, 58 tracked-JSON parses, 95 local-link checks, exact manifest reconstruction, and two byte-identical canonical 340,283-byte wheels / SHA-256 `ad506e60ac7480c14382d4d5d0e53468ecb11a39801feae350a0ee397d068b74`. This supersedes the 341,228-byte stale-CRLF candidate build while changing no reconciliation output or decision.
