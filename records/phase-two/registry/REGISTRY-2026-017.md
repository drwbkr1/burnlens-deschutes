# REGISTRY-2026-017 - Live-Browser Reviewer-Handoff QA Evidence

**Checkpoint:** Issue #383 / PR #385 / merge `861716be16be3a0469d2268baed971be65684d48`; reviewed head `1723f87d252bda7a67680a71108fc0a65b42c587`; source `74275a061fb4054a535cc8b660bebb0021999c54`; browser artifacts `97ddbaf71372e119428868a37d214c3327523514`; verified tag `v0.15.0-live-browser-reviewer-handoff`, object `69b32b076a7fca40ba5eceacb64aeac2a512e7b9`; lifecycle sync issue #386

| Artifact | Class | Version/state | Committed provider bytes |
|---|---|---|---:|
| `burnlens/label_review_browser_controller.mjs` | Dependency-free installed-Chrome controller | Node built-ins; isolated profile; loopback DevTools; file workbench | 0 |
| `burnlens/label_review_browser_qa.py` and CLI | Fail-closed browser-observation verifier and evidence renderer | BurnLens `0.15.0`; `label-review-live-browser-qa-v0.1.0` | 0 |
| Enhanced response-lock path | Evidence-origin and issue-bound receipt | Software fixture cannot count as human or authorize reveal; returned response remains a separate origin | 0 |
| `LABEL-REVIEW-BROWSER-QA-2026-001` JSON/HTML/PNG | Machine-readable, semantic, and rendered browser acceptance evidence | Run `BL-2026-07-16-label-review-browser-qa-r001`; zero human responses used | 0 |
| Desktop and mobile screenshots | Actual browser viewport evidence | 1440 by 1000 and 390 by 844; no horizontal overflow | 0 |
| Repository tests | Browser observation, render, package, lock-origin, chronology, and historical contracts | 154 pass; one known NumPy deprecation warning | 0 |
| `burnlens_deschutes-0.15.0-py3-none-any.whl` | Reproducible release-wheel evidence; not committed | source `74275a061fb4054a535cc8b660bebb0021999c54`; `SOURCE_DATE_EPOCH=1784225027`; 283,856 bytes; SHA-256 `950472207ac8f75208188584e2f8474f88a8a71e0f14fde864aa297b79076352`; isolated import `0.15.0`; 25 entry points; controller packaged | 0 |
| `MANIFEST-2026-017.json` | Exact five-output inventory and release quality gates | Shipped; PR #385, fresh merged-main clone, canonical wheel, exact reconstruction, fresh browser run, and remote-tag gates pass; lifecycle sync issue #386 | 0 |

No provider archive, secret, credential, reviewer response bytes, reviewer notes, adjudication, accepted label, dataset, split, baseline, model, metric, deployment, field claim, official claim, or operational claim is committed.
