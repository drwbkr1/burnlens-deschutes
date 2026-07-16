# Devlog: Single-Reviewer Reconciliation

The highest-leverage weakness after reveal authorization was label-evidence credibility. Issue #403 therefore compared the one exact blinded response with the exact proposal under the owner's reviewer-two waiver, while keeping weak or conflicting evidence ignored.

BurnLens `0.20.0` adds atomic ignored reconciliation, deterministic per-unit traceability, aggregate-only public QA, and two new console commands. The private 72,628-byte report has SHA-256 `a04dd629551a2163e5e7a31f61c3aa95d4fdba136563f3a42940a2e9d1e9249d`. It binds all 56 units to event, source pixel, proposal, response hash, rule, software, commit, and run without changing the response or proposal.

The rule retains only sufficient-evidence binary matches without weak, conflicting, or semantically inconsistent reasons. Six burned units survive; no background unit survives. Darlene contributes 3, McKay 3, and Tepee 0. The other 50 units remain ignored. That imbalance makes remediation the honest result.

Public JSON/HTML/PNG expose only aggregates and exact bindings. They withhold reviewer free text, unit IDs, coordinates, private filenames, and private paths. The 1800-by-1280 card and a full installed-Chrome render were inspected at original resolution. All 181 tests pass. The initial stale-working-tree wheels were identical but retained CRLF package-source bytes despite the LF checkout contract. Lifecycle verification supersedes them with two byte-identical clean-checkout wheels at 340,283 bytes / SHA-256 `ad506e60ac7480c14382d4d5d0e53468ecb11a39801feae350a0ee397d068b74`; an isolated install reports BurnLens `0.20.0`, 33 console entry points, and zero private evidence entries.

The preflight sequence exception is explicit: reveal HTML appeared in a repository-search result before the explicit verifier command. Exact authorization passed immediately afterward and before private-response access or comparison. Reviewer blindness and every locked byte remained intact, but the pre-access gate is recorded as fail-disclosed.

Current official MTBS and CEOS LPV material supports the conservative posture: cloud/shadow and uninterpretable areas must remain masked, scene registration and multitemporal interpretation matter, and limited samples do not justify representative validation claims. Issue #411 now owns the smallest useful reference-evidence remediation. Dataset, split, baseline, and model work remain deferred.

PR #412 merged the bounded checkpoint at `4918024dfb83270dbbd83a5880c455cc3c01771c`. Annotated tag `v0.20.0-single-reviewer-reconciliation` has object `5bb840b43ae8594e02a9b026b3932bb16f83bf5b` and remotely peels to that merge. A fresh clean checkout passes all 181 tests, compilation, dependency health, JSON/link/manifest gates, and the authoritative 340,283-byte wheel. Issue #413 synchronizes release lifecycle facts only; issue #411 remains the scientific next step.
