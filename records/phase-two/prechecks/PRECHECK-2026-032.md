# PRECHECK-2026-032 - v0.32 Fresh-Clone Package Binding

**Issue:** #470

## Finding

PR #469 merged the event-group plan at `7eb007afe5ba96f97cdba278038c09f3123b0e5c`. A separate clone of remote `main` reconstructed the canonical JSON, HTML, and PNG byte for byte and passed 253 tests with four expected local-custody skips. The release tag remained withheld because the fresh-clone wheel did not match the wheel recorded before merge.

The long-lived Windows worktree retained CRLF bytes for some package files checked out before the repository's existing LF attributes were introduced. The Git index and fresh clone correctly contain LF bytes. Two fixed-epoch wheels built from fresh remote `main` match each other at 476,330 bytes and SHA-256 `ce16b3134a12a20fab21ebd7b71cb8f0c108719d4351e93ac2266b27f2c5f46c`. The stale-worktree 477,273-byte wheel is rejected.

## Allowed work

Correct only the manifest, prompt/build log, status, roadmap, changelog, version history, and human-readable devlog so they bind the release candidate to fresh-clone bytes. Re-run package inspection and the merged-main gates before tagging.

## Prohibited work

Do not change the event plan, source snapshot, selected events, rendered outputs, source decisions, labels, dataset, split, baseline, model, or public claims. Do not tag until a post-remediation fresh clone passes.

**Entry decision:** `REMEDIATE_RELEASE_METADATA_ONLY; WITHHOLD_TAG`.
