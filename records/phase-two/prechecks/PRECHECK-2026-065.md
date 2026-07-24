# PRECHECK-2026-065 - Windigo release-candidate pass

**Unit / issue / branch:** `P2O4-T35-U06` / #534 / `codex/p2o4-t35-windigo-deadline-gate`

**Package-sensitive / closeout-record commits:** `714273adfcf8f90ab16abe798eb086201577b0e9` / `e8739a90b8ed7337851afcffb313f3d4114224bf`

**Closeout run:** `BL-2026-07-24-windigo-milestone-closeout-r001`

**Decision:** `ACCEPT_WINDIGO_AS_SIXTH_OWNER_APPROVED_PROTOTYPE_EVENT_KEEP_DATASET_SPLIT_BASELINE_MODEL_CLOSED`

## Render closure

The final tracked HTML is 3,582 bytes / SHA-256 `6f6b9cd17494a42833ce14073bd9c6413c035963df0e445975e000c9fd35cc52`. It uses only its sibling PNG, contains bounded responsive metrics below 700 pixels, descriptive alternative text, no form controls, and a horizontal-overflow guard.

The owner opened the exact final report after the automated local-file navigation policy blocked a fresh tool-driven check. The requested desktop and narrow review was answered with the exact response `It renders correctly` and recorded at `2026-07-24T01:10:16.8257050Z`. The 1,600 by 1,100 PNG had already passed original-resolution inspection.

The render gate passes. No browser-policy bypass or alternate hidden surface was used.

## Runtime and package proof

Release verification found and corrected two packaging-only drifts before this checkpoint: the editable lock version and the frozen command count. The refreshed environment proves:

- CPython 3.12.10;
- 66 compatible locked distributions;
- BurnLens 0.47.0 from the active environment;
- 86 of 86 command help probes;
- five environment-profile tests;
- six exact Windigo response-intake tests; and
- 575 full-suite tests, one expected skip, 22 retained NumPy deprecation warnings, and 86 subtests.

Two separate exact Git archives at candidate commit `714273a...` were built under `SOURCE_DATE_EPOCH=1784854998` and `PYTHONHASHSEED=0`. Both produce the same `burnlens_deschutes-0.47.0-py3-none-any.whl`:

| Property | Result |
|---|---|
| bytes | 872,766 |
| SHA-256 | `1fabf5408113dcd238871070a3fbe0105526a845c66eb8f0f48edcb99595aea7` |
| archive entries | 183 unique |
| forbidden entries | zero |
| installed distributions | 13 compatible runtime packages |
| installed version | 0.47.0 |
| installed source | ignored isolated `site-packages`, not the repository root |
| installed commands | 86 of 86 help probes pass |

The first isolated metadata probe ran from the repository root and was rejected as provenance-contaminated even though installation succeeded. The accepted probe runs inside the ignored isolated environment and resolves `burnlens` from its own `site-packages`.

## Public and claim audit

- All 139 tracked/candidate JSON documents parse.
- All 740 Markdown files have zero broken local links.
- Changed public surfaces contain no response notes, unit decisions, private path, recipient, retrieval URL, credential, token, cookie, signed URL, or raw provider byte.
- README, roadmap, phase status, Phase Two objectives, changelog, version history, decision, case study, prompt/build log, registry, and devlog agree on the candidate state.
- `owner-approved-prototype-region-labels-v0.4.0` contains 12 balanced regions, 286 core pixels / 11.44 ha, 533 excluded unknown-ring pixels, and six complete event groups.
- The six-event count minimum passes. The separate sufficiency evaluator, accepted dataset, split, baseline, and model remain closed.
- No ground-truth, independent-review, inter-rater, field-validation, accuracy, official, endorsed, emergency-ready, operational, GitHub Release, or deployment claim exists.

## Live repository truth

Closeout-record commit `e8739a90b8ed7337851afcffb313f3d4114224bf` is pushed and remote-equal. Its diff from package-sensitive checkpoint `714273adfcf8f90ab16abe798eb086201577b0e9` changes zero package-sensitive paths. Issue #534 is open and retains the exact six-unit contract. Its U05 evidence comment was corrected in place after a PowerShell escape defect made the first live body malformed; the verified live body now contains the complete response, result, package, and remaining-gate facts.

`RELEASE-AUDIT-2026-001` is valid and computes `blocked` only because the PR, merge, fresh-main repetition, and remote annotated-tag peel have not run.

## Disposition and next dependency

The U06 release candidate passes. Open one coherent milestone PR. After its exact checks and diff pass, merge it, verify the actual outputs and package from fresh `origin/main`, create annotated tag `v0.47.0-windigo-sixth-prototype-event`, and verify the remote object peels to the merged checkpoint.

Do not create a dataset, split, baseline, model, GitHub Release, deployment, or public-sharing change during shipment.
