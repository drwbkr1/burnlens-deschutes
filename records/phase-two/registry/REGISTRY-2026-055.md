# REGISTRY-2026-055 - Petes Lake U05 retained-byte NWI validator remediation

**Unit / issue / branch:** `P2O4-T33-U05R1` / #521 / `codex/p2o4-t33-petes-lake-milestone`

**Failed run retained:** `BL-2026-07-21-petes-lake-nwi-context-r001`

**Registered replacement run:** `BL-2026-07-22-petes-lake-nwi-context-r002`

**Code checkpoint:** `8b0267e096654e919427947ca8a566352deb73c2`

**Decision:** `PASS_LOCAL_VALIDATOR_REMEDIATION_FOR_NEW_EXACT_R002_INTAKE_ONLY`

**Disposition / next dependency:** r001 `remediate`; U05R1 code gate `pass`; r002 intake `not executed` / clean record-sync commit, offline r002 initialization, external validation, fresh one-shot terms authorization, validation again, then r002 asset one only

## Retained r001 attempt

The first and only r001 provider-data request stopped at `RESPONSE_STRUCTURE`; the ordered loop made no second provider-data request. The retained provider response exactly matches the pre-registered official metadata bytes, so source and transport drift are excluded. The local validator stripped table qualifiers and allowed joined `NWI_Wetland_Codes.OBJECTID` to overwrite publisher field `Wetlands.OBJECTID`, producing a false OID-versus-integer mismatch.

| Evidence | Bytes | SHA-256 | State |
|---|---:|---|---|
| terminal r001 intake contract | 24,434 | `a809241052aa8a8ce7705bf2cf9553b3113c10981791dd3dd4a0c0a9c1df2b7b` | failed; ignored; untracked; single-link; external validator passes |
| immutable r001 plan | 18,137 | `e11428002a64052c8e66e7de0967eca00c61b5f12229b9aac42fefec7dd44685` | exact; ignored; untracked; single-link |
| r001 live-terms receipt | 5,352 | `dc8bcd0a39556395e90be28dab48c7d25edec182a50c3a7e4be0ed3d307eabcb` | passed for r001 only; ignored; untracked; single-link; never reused by r002 |
| r001 dispatch receipt | 820 | `8a13dabf62e119500782e5333047c710cc0fed2eded0c8fb025e85b0484288b2` | exact first and only dispatched provider-data request |
| retained r001 metadata response | 21,276 | `975c06d4c44ecedf23d1d5930ac1316913234ed0fd5b3a76fc365d07db466459` | exact official identity; ignored; untracked; single-link; never copied or promoted |

The r001 contract, plan, terms receipt, dispatch receipt, and response remain unchanged. r001 is not retried, reclassified, overwritten, deleted, copied, or continued at asset two.

## Registered r002 custody identity

Issue #521 was revised before implementation and verified current at 2026-07-22T02:12:34Z. The revision registers a separate remediation evidence unit, intake ID `petes-lake-nwi-context-2026-002`, twelve exact `petes-lake-nwi-r002-*` asset IDs, separate attempt IDs, separate contract/plan/terms/dispatch/staging paths under `P2O4-T33-U05R1`, and raw package `petes-lake-nwi-context-v0.1.0-r002`.

No r001 path or identity is reused. Every r002 contract load rehashes all five r001 artifacts and fails closed if any changes after initialization. Each r002 asset remains single-attempt and ordered. A fresh run-bound five-page terms receipt is mandatory; the passed r001 receipt cannot authorize r002.

At this registry checkpoint, the r002 contract, immutable plan, live-terms receipt, dispatch root, staging root, and raw package do not exist. Zero r002 provider-data request or byte exists.

## Code and test checkpoint

| Artifact | Bytes | SHA-256 | Role |
|---|---:|---|---|
| `burnlens/petes_lake_wetland_custody.py` | 122,054 | `197b167297ef87b2b8527abc7777e4f0745bbedba77809a50bd495d7d2b03629` | qualified publisher-field validation, exact r001 binding on every load, disjoint r002 state machine, run-scoped assets and custody |
| `burnlens/petes_lake_reference_fitness.py` | 60,838 | `609ed448b865173ad175e8d04adf6acf14f8a8df05198dd43a8f4ab7a5a9911b` | downstream loading by exact logical role while retaining run-scoped custody identities |
| `tests/test_petes_lake_wetland_custody.py` | 38,171 | `00227630580eba920fd9af9d8776b36db7579940c81a3393ec3020febca8f4e3` | joined-field regression, exact retained-byte local gate, post-init r001 mutation stop, r002 state-machine regressions |
| `tests/test_petes_lake_reference_fitness.py` | 17,701 | `d43e9895eb6d0359a7a7067e2e042f2abbd8d204f881568e5da5b08b10ba197f` | r002 package-path binding and downstream compatibility |
| `records/phase-two/prechecks/PRECHECK-2026-054.md` | 5,798 | `d17bf88b9915a8508f6e18b11955042f3bbe74608c17060f453ab92fa37d2ebe` | issue registration, exact failure, remediation, roster, custody, no-retry, and stop authorization |

## Verification

- Exact retained production response passes the corrected qualified-field validator offline. All seven required `Wetlands.*` publisher fields are exact; the joined integer `NWI_Wetland_Codes.OBJECTID` remains separate and cannot satisfy or overwrite the required OID field.
- Wrong required publisher field type, duplicate exact field name, wrong layer identity/type/geometry, and invalid maximum record count remain fail-closed.
- Twelve r002 asset IDs, logical roles, destinations, attempts, and ignored custody namespaces are unique and ordered.
- Every common r002 contract load rehashes the five r001 identities; a synthetic post-initialization mutation blocks the next load.
- Focused Petes suite: 107 passed, one expected pre-finalized-custody skip, and 5 subtests.
- Exact pushed checkpoint full suite: 514 passed, one expected pre-finalized-custody skip, 20 existing NumPy deprecation warnings, and 55 subtests.
- Lock freshness, 66-package compatibility, compilation, staged diff, LF/index byte, privacy, r001 external-contract validation, Git origin, push, and remote equality pass.
- Independent read-only staged audit found the initial post-initialization provenance gap; the common-load fix and regression closed it. Re-review found no remaining material blocker.

U05 accepts zero reference pixel at this checkpoint. U06 and every candidate, owner response, prototype label, sixth event, dataset, split, baseline, model, metric, version, release, tag, deployment, field-validation, official, endorsed, operational, and emergency-ready claim remain blocked.
