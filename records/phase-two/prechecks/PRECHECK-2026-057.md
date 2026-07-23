# PRECHECK-2026-057 - Official fallback source-gate entry

**Unit / issue / branch:** `P2O4-T34-U01` / #532 / `codex/p2o4-t34-official-fallback-source-gate`

**Run:** `BL-2026-07-23-official-fallback-entry-r001`

**Completed:** 2026-07-23T03:32:13.749Z

**Verified base:** `ad298f244b0261a77ef0d6ff442da5a45738a7d9`

**Decision:** `PASS_FREEZE_MCKENZIE_AND_MILLI_METADATA_ONLY_ROSTER`

## Highest-leverage observed weakness

The latest accepted-label pipeline was executed again from the exact locked Grandview response and receipt under the current BurnLens 0.45.0 environment. It reached the same decision, `ACCEPT_GRANDVIEW_OWNER_APPROVED_PROTOTYPE_LABELS_DEFER_DATASET_SPLIT_BASELINE_MODEL`, with ten owner-approved prototype regions across five complete event groups. The newly rendered 1600 x 1180 PNG was inspected at original resolution: the warning, four summary cards, gate results, blocked six-event minimum, decision, source commit, label/schema versions, and absent dataset/model trace are legible and internally consistent.

Two validation-harness errors failed closed before the successful run. An outside-repository private derivative was rejected with `private input or output is outside the repository`; a pre-created public output directory was rejected with `public output directory already exists`. Neither attempt changed the locked response, receipt, tracked evidence, or custody. The successful run used a unique ignored repository-local private validation path and a new external temporary public-output path; both were removed after exact inspection.

Current 0.45 output intentionally differs from the historical tracked 0.44 artifact only through the displayed `software_version` and its dependent private/public hashes. The current public JSON is SHA-256 `36e56f6fe9e2e7b388dac27f4dcd3debb2e5cccef32d76059be1fff85d0f2580`; its output inventory records a 4,034-byte HTML / SHA-256 `7598940bfb2f37d8ece28d78d2139c75e7c206939a0a1a07953a462aec9b88e7` and an 89,920-byte PNG / SHA-256 `f252f949305876226dc108d01dfb27e282cb899c74e74bd6dacd21d9e7eaee86`. No label state changed. The highest-leverage user-visible and evidence-visible weakness therefore remains the missing sixth complete event, not the accepted-label interface.

## Entry-state verification

| Gate | Actual result |
|---|---|
| Issue and base | Issue #532 is open; canonical branch was created from exact synchronized `origin/main` `ad298f244b0261a77ef0d6ff442da5a45738a7d9` |
| Release state | BurnLens 0.45.0 remains the verified tool; Petes Lake remains `defer / complete / verified` and is not event six |
| Custody aggregate | Read-only inventory remains 168 files / 16,999,841,856 bytes / two zero-byte retained failures |
| Forbidden continuation | Zero `r004`, `U05R3`, or `petes-lake-nwi-context-2026-004` target paths; zero active BurnLens acquisition/provider processes |
| Tracked state | Clean worktree before this record; no ignored custody was initialized or mutated by U01 |
| Checkout stability | Exact LF rules are required in `.gitattributes` for this precheck and its prompt/build log before their first commit |
| Dataset/model state | Dataset, split, baseline, model, metric, GitHub Release, deployment, and deployed analytical application remain absent |

## Immutable control inputs

| Input | Bytes | SHA-256 | Role |
|---|---:|---|---|
| `samples/reference/phase-two/OFFICIAL-SOURCE-SCOUT-2026-001.json` | 150,299 | `1aee7a51a8d46d1c019657df6e777a05ea24ea49d385422cd8272db79683b65e` | verified alternate-candidate reserve |
| `records/phase-two/sources/SOURCE-2026-033.md` | 3,665 | `421d0ec4d94438f3f87bd6fac170699bb5e49701f5aec5d2ec662bd23169959a` | historical McKenzie metadata-only fallback reconnaissance |
| `records/phase-two/manifests/MANIFEST-2026-047.json` | 8,698 | `8391a20b2bd5e9b0bccd3f2f731ff32ea44c64770fd25ba629c9ea19810e573d` | verified v0.45 lifecycle truth and next-gate boundary |
| `docs/governance/CHECKPOINT_POLICY.md` | 9,136 | `bf422056b84aa2f67e79717bb5a5292eed0d36178cecf8c1e1b64246b7e42f77` | milestone/evidence-unit control |
| `docs/phases/phase-02/PHASE_02_OBJECTIVES.md` | 15,018 | `3faac18bbdccf223b585e1a03829d4e115be6c1bc88afc6650eef4f3bc599d62` | Objective Four and six-event outcome |

## Frozen candidate roster

### Candidate one - Petes Lake McKenzie HUC8 NWI

- candidate ID: `candidate-petes-lake-mckenzie-hu8-17090004`
- publisher: U.S. Fish and Wildlife Service National Wetlands Inventory
- exact prospective asset: `HU8_17090004_Watershed.zip`
- intended role: approximate wetlands/deepwater context and conservative uncertainty/exclusion evidence only
- prohibited roles: burned truth, affirmative background truth, wetland-absence proof, burn severity, field truth, regulatory delineation, official validation, or automatic label truth
- inherited state: metadata-only route observed in `SOURCE-2026-033`; no archive byte or member has been requested or retained

### Candidate two - Milli 0843 CS

- candidate ID: `candidate-milli-0843-cs-2017`
- exact event: `OR4425712174320170811`; ignition 2017-08-11; occurrence MTBS map `10008215`; 24,065 acres
- exact standard Portal records retained by the verified scout: BAER catalog `2033` / map `10004702` / 24,216 acres; MTBS catalog `11202` / map `10008215` / 24,065 acres; RAVG catalog `1295` / map `10005445` / 24,299 acres; all `nonstandard=false`
- verified reserve facts: scout rank 2 / score 34; 61.035 km minimum separation from the then-current event set; 68 Landsat burned-area metadata matches
- intended prospective roles: Sentinel-2 optical evidence, program-limited BAER/MTBS/RAVG reference evidence, affirmative unchanged background evidence, explicit unknown/exclusion evidence, and later owner yes/no/uncertain review if every intervening gate passes
- decisive metadata question: no single Sentinel-2 tile was previously shown to cover the complete MTBS boundary, so U03 must prove or reject a bounded minimum complete multi-tile pre/post roster, grids, seams, orbits, temporal relation, expected transactions/bytes, and zero silent clipping before any future acquisition can be selected

Milli is frozen instead of verified-scout rank-one GW Fire because P2O4-T34 ranks prospective evidence completeness and current access feasibility before diversity. Milli has three standard program identities and can reuse the already established Sentinel/CDSE source regime without a new secret. GW has a nonstandard BAER record with map ID zero, predates Sentinel-2, and its observed Landsat data route requires unestablished EROS authentication. Milli's multi-tile risk is material and must remain visible, but it can be decided with metadata only. No third candidate may enter this milestone and a failed candidate cannot be replaced.

## Frozen issue-scoped request contract

Only the following request classes may run after this precheck:

1. official explanatory, terms, limitation, citation, or notice pages by HTTPS `GET`, one request per frozen locator, no authentication, 30-second connection/read timeout, at most 2 MiB retained per response;
2. official catalog or feature metadata by bounded HTTPS `GET`, exact candidate filter, property-only or extent-only response where supported, no geometry unless the U03 complete-coverage comparison requires the provider's bounded metadata footprint, no authentication, no automatic retry, at most 5 MiB retained per response;
3. exact archive or raster asset locators by HTTPS `HEAD` only, redirects disabled, no `GET`, no `Range`, no response body, no authentication, no automatic retry, 30-second timeout;
4. current Sentinel catalog metadata for the frozen Milli boundary and pre/post windows, with an explicit result limit no greater than 100 per request and no asset body.

Unexpected redirect, host drift, authentication demand, response over the declared limit, unsafe media, source-asset body, unbounded pagination, new secret, payment, click-through, or access change stops the affected candidate. Failed, timed-out, malformed, and superseded metadata attempts remain in the U02/U03 ledger. Provider/source bytes, ignored custody, email bundle requests, r004, candidates, responses, labels, datasets, splits, baselines, models, metrics, deployments, and public-sharing changes are forbidden.

## Intended-use and rights questions

Each candidate must independently distinguish:

- metadata inspection;
- future ignored local acquisition and retention;
- future local processing and scientific inspection;
- attributed derived-publication use;
- raw payload, archive, member, attribute, or logo redistribution.

Silence never passes a right. A later selected route must have affirmative support for the exact local acquisition/retention/processing and derived-publication posture; raw redistribution must be expressly allowed or conservatively prohibited. Selection authorizes only a later issue contract, not data access.

## U01 disposition and next dependency

U01 passes. U02 may refresh and gate only `candidate-petes-lake-mckenzie-hu8-17090004` under the frozen request contract. U03 may independently gate only `candidate-milli-0843-cs-2017`. Neither unit may acquire source-asset bytes or initialize custody. Every live observation receives an absolute UTC timestamp, exact locator, bounded request identity, response size/hash where a metadata body is retained, criterion status, limitation, disposition, and next dependency.
