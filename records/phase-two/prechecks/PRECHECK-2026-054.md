# PRECHECK-2026-054 - Petes Lake NWI retained-byte validator remediation

**Unit / issue / branch:** `P2O4-T33-U05R1` / #521 / `codex/p2o4-t33-petes-lake-milestone`

**Remediation run:** `BL-2026-07-22-petes-lake-nwi-context-r002`

**Checked:** 2026-07-22T02:13:04.267350Z

## Decision

`PASS_LOCAL_VALIDATOR_REMEDIATION_FOR_NEW_EXACT_R002_INTAKE_ONLY`.

**Current status:** `PLANNED_UNDER_CODE_REMEDIATION_NOT_YET_EFFECTIVE`. This decision becomes operative only after the exact remediation code, focused regressions, failure record, and this precheck are committed, pushed, recorded on issue #521, and verified clean and remote-equal. It authorizes no retry of r001 and no provider request from an uncommitted or stale checkout.

Issue #521 was revised before implementation and verified current at 2026-07-22T02:12:34Z. It registers `P2O4-T33-U05R1`, the disjoint r002 run/intake/path identities, the exact twelve-asset roster, required gates, failure retention, and downstream blocks. The source, target user, CV task, phase outcome, source precedence, use boundary, and U05 scientific contract do not change.

## Exact retained r001 failure

The first and only r001 provider-data request began at `2026-07-22T02:05:00.749610Z`, was durably marked dispatched at `2026-07-22T02:05:02.165139Z`, and failed closed at `2026-07-22T02:05:04.250588Z` in `RESPONSE_STRUCTURE`. The loop stopped before request two. The contract records `NWI_TRANSFER_OR_STRUCTURE_FAILURE_NO_RETRY`; its disposition is `remediate`, not pass, retry, exclusion, or source drift.

The ignored, untracked, repository-local r001 evidence remains immutable:

| Evidence | Bytes | SHA-256 |
|---|---:|---|
| mutable terminal contract `petes-lake-nwi-context-r001-intake.json` | 24,434 | `a809241052aa8a8ce7705bf2cf9553b3113c10981791dd3dd4a0c0a9c1df2b7b` |
| immutable plan `petes-lake-nwi-context-r001-plan.json` | 18,137 | `e11428002a64052c8e66e7de0967eca00c61b5f12229b9aac42fefec7dd44685` |
| passed live-terms receipt `petes-lake-nwi-context-r001-terms-refresh.json` | 5,352 | `dc8bcd0a39556395e90be28dab48c7d25edec182a50c3a7e4be0ed3d307eabcb` |
| dispatch receipt `wetlands-layer-metadata-attempt-001.json` | 820 | `8a13dabf62e119500782e5333047c710cc0fed2eded0c8fb025e85b0484288b2` |
| retained response `wetlands-layer-metadata.json.partial` | 21,276 | `975c06d4c44ecedf23d1d5930ac1316913234ed0fd5b3a76fc365d07db466459` |

The retained response exactly matches the pre-registered official metadata identity. It has `name=Wetlands`, `type=Feature Layer`, `geometryType=esriGeometryPolygon`, `maxRecordCount=1000`, and all seven exact required `Wetlands.*` publisher fields with their expected types. The local validator collapsed 43 qualified field names to suffixes; joined `NWI_Wetland_Codes.OBJECTID` then overwrote `Wetlands.OBJECTID` and falsely changed the observed type from OID to integer. This is a local validator defect, not source, transport, byte, terms, or custody drift.

## Remediation and offline proof

The allowed fix is exact and narrow:

- validate required Wetlands fields by their full publisher-qualified names;
- validate Data Source fields by their exact publisher names;
- reject duplicate exact field names and wrong required field types;
- retain unrelated joined metadata fields without letting them satisfy or overwrite required fields;
- add a synthetic joined-field regression plus an offline exact retained-byte regression;
- bind and rehash every r001 failure artifact before r002 initialization;
- preserve all existing name, layer type, polygon geometry, maximum-record-count, source renderer, coded-domain, duplicate-key, topology, count, ID, media, identity, and no-retry gates.

The fix may not weaken a source rule, accept suffix-only substitutes, copy or promote r001 bytes, or mutate r001 evidence. A dirty worktree, absent or changed r001 byte, failed focused/full regression, failed external contract validation, or remote mismatch blocks r002 initialization.

## Exact r002 identity and roster

The new run uses intake ID `petes-lake-nwi-context-2026-002`, ignored contract/plan/terms/dispatch paths under `downloads/phase-two/runs/P2O4-T33-U05R1/`, ignored staging under `downloads/phase-two/quarantine/P2O4-T33-U05R1/petes-lake-nwi-context-r002/`, and raw package `downloads/phase-two/raw/petes-lake-nwi-context-v0.1.0-r002/`. No r001 path, asset ID, attempt ID, or destination is reused.

The exact ordered assets are:

1. `petes-lake-nwi-r002-wetlands-layer-metadata`
2. `petes-lake-nwi-r002-wetlands-pre-count`
3. `petes-lake-nwi-r002-wetlands-pre-ids`
4. `petes-lake-nwi-r002-wetlands-features`
5. `petes-lake-nwi-r002-wetlands-post-count`
6. `petes-lake-nwi-r002-wetlands-post-ids`
7. `petes-lake-nwi-r002-source-layer-metadata`
8. `petes-lake-nwi-r002-source-pre-count`
9. `petes-lake-nwi-r002-source-pre-ids`
10. `petes-lake-nwi-r002-source-features`
11. `petes-lake-nwi-r002-source-post-count`
12. `petes-lake-nwi-r002-source-post-ids`

Each permits exactly one `-attempt-001`. Before provider-data asset one, r002 must bind a clean pushed remediation commit, pass the external intake-contract validator, perform a fresh one-shot/no-redirect/no-retry five-page terms refresh into its own run-bound receipt, and pass external validation again. Each asset must then start, fetch, verify, promote, and pass external validation before the next asset. Any failure stops the roster and is retained under a newly registered future identity rather than retried.

Passing r002 custody authorizes only the still-separate U05 reference-fitness inspection. U06 and every candidate, owner response, label, sixth-event, dataset, split, baseline, model, version, release, tag, deployment, field-validation, official, endorsed, operational, and emergency-ready result remain blocked.
