# REGISTRY-2026-014 - Topology-Stable Label-Transfer Evidence

**Checkpoint:** Issue #371 / PR #372 / merge `e00028509145b439d95eb302591e7cb19bd073fd`; reviewed head `345dd72363377aad3215d23a8120c42edbe85278`; generator/QA source `0c2b489f34915e352cefe72ca76dea488bc8a4db`; candidate artifacts `567b9cd986a44c3a9b320f558ab7cd156d451fb4`; verified tag `v0.12.1-topology-stable-label-transfer`, object `8606c61f0e1668f2b057abca177144937eae1036`; lifecycle sync issue #373 / PR #374

| Artifact | Class | Version/state | Committed provider bytes |
|---|---|---|---:|
| `burnlens/mtbs_cross_event_reference.py` | Fail-closed registered-package verifier plus content-stable public verification summary | BurnLens `0.12.1`; `mtbs-registered-package-link-policy-v0.1.0`; one or exact-two links accepted only after content verification; all other counts rejected | 0 |
| `burnlens/cross_event_label_transfer.py` and proposal CLI | Scientific transfer method unchanged; public MTBS lineage no longer treats transient current link count as run identity | `cross-event-five-state-transfer-v0.1.0`; report `v0.1.1`; run `BL-2026-07-16-cross-event-label-transfer-r004` | 0 |
| `burnlens/cross_event_label_transfer_qa.py` and QA CLI | QA method unchanged; versioned corrected report binds the new proposal identity | `separate-cross-event-five-state-qa-v0.1.0`; report `v0.1.1`; run `BL-2026-07-16-cross-event-label-transfer-qa-r004` | 0 |
| Preserved `2026-001` proposal/QA package | Original v0.12.0 evidence and its observed two-link trace | Immutable historical evidence in `MANIFEST-2026-013` | 0 |
| Corrected `2026-002` proposal/QA package | New JSON/HTML/PNG plus four traceable GeoTIFFs | 9,760 candidate / 54,170 ignored; 63,930 QA pixels; zero mismatch; hashes in `MANIFEST-2026-014` | 0 |
| Real topology replay | Ignored one-link and exact-two-link copies of the registered MTBS package | All ten outputs byte-identical; third-link test fails closed | 0 |
| Repository tests | Dynamic link safety, public-identity stability, transfer, QA independence, and predecessor contracts | 137 pass | 0 |
| `burnlens_deschutes-0.12.1-py3-none-any.whl` | Reproducible release-wheel evidence; not committed | source `0c2b489f34915e352cefe72ca76dea488bc8a4db`; fresh LF checkout; `SOURCE_DATE_EPOCH=1784179803`; two byte-identical builds; 215,461 bytes; SHA-256 `e6e45cfc69aebb17b9a6396d593508b297b8461deb69463edd1ba04cc4ad99d3`; isolated import `0.12.1` | 0 |
| `MANIFEST-2026-014.json` | Exact corrected ten-output inventory and release gates | Shipped; PR #372, fresh merged-main, canonical-wheel, real-reconstruction, and remote-tag gates pass; sync #373 / PR #374 | 0 |

No classifier, threshold, source, target, label protocol, label schema, event group, output pixel, dataset, split, baseline, model, application, accuracy claim, field claim, operational claim, official status, credential material, or provider byte changes in this remediation.
