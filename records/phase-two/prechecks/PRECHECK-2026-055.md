# PRECHECK-2026-055 - Petes Lake NWI provider-open observability remediation

**Unit / issue / branch:** `P2O4-T33-U05R2` / #521 / `codex/p2o4-t33-petes-lake-milestone`

**Terminal input run:** `BL-2026-07-22-petes-lake-nwi-context-r002`

**Registered replacement run:** `BL-2026-07-22-petes-lake-nwi-context-r003`

**Decision:** `AUTHORIZE_OFFLINE_OBSERVABILITY_REMEDIATION_AND_ONE_FINAL_DISJOINT_R003_INTAKE`

## Exact blocking evidence

R002 initialized from pushed record checkpoint `87a852c750fe7527bd018c32f630c8447e61fc47`, passed external contract validation, and passed a fresh one-shot five-page official terms refresh. The first seven ordered assets each completed one attempt and promoted into ignored, single-link custody. The eighth asset, `petes-lake-nwi-r002-source-pre-count`, started at `2026-07-22T03:03:48.717885Z`, durably dispatched its only POST at `2026-07-22T03:03:51.052853Z`, and failed at `2026-07-22T03:03:53.965614Z` before a response object opened.

| Evidence | Bytes | SHA-256 | State |
|---|---:|---|---|
| terminal r002 contract | 79,265 | `37cd244ecba3e19db978505fb1dbecfc08ac68752a2e41352fbdad5f9ad6479a` | failed; external validator with local-file verification passes |
| immutable r002 plan | 20,684 | `ea1a23462f7395a2d8c5bf64e672d557c3aa6120106bdd78c038a84683c98a62` | exact |
| r002 live-terms receipt | 5,354 | `1cdbad419ccc9804cbbbeb1aa45466cb1fb882ae855ed3759cc91ced7ed48fbc` | passed for r002 only; never reused |
| failed source-pre-count dispatch receipt | 905 | `5a841bdb72f597d2a470eb88f6eb5425f8d580767a1e76ec936df9aefe9d2058` | one exact dispatched POST |
| retained source-pre-count partial | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | exact; single-link; no response byte |

The terminal state is seven `promoted`, one `failed`, and four `authorized` assets. Assets 9-12 are unexecuted. R002 is disposition `remediate` and is never retried, continued, finalized, copied, moved, relabeled, partially selected, or used for U05 scientific fitness.

## Honest diagnosis

The exact request body and public route were durably bound before access. A POST using the same body hash succeeded earlier against the Wetlands query route, and the Data Source layer-metadata GET succeeded about 40 seconds before the failed POST. This does not establish the failed request's cause.

The current implementation sets stage `PROVIDER_OPEN` before opening the response, catches every exception, stores only the generic stage and zero-byte retained identity, and raises only a generic no-retry error. The exact cause is therefore irretrievably absent. HTTP status or redirect, timeout, DNS, TLS, socket, provider availability, request construction, and local interruption cannot be distinguished. No provider-side, malformed-request, or transient-network root-cause claim is authorized.

## Registered remediation

Issue #521 was amended before implementation at `2026-07-22T03:11:05Z`. Its 27,324-character body has SHA-256 `0748bacc311eb9436938ed3338bd4555f4373c60dbdc552a95272118ff253a1d` and registers:

- unit `P2O4-T33-U05R2`;
- run `BL-2026-07-22-petes-lake-nwi-context-r003`;
- intake `petes-lake-nwi-context-2026-003`;
- twelve ordered `petes-lake-nwi-r003-*` assets with one `-attempt-001` each;
- contract, plan, terms, and dispatch paths under `downloads/phase-two/runs/P2O4-T33-U05R2/`;
- staging under `downloads/phase-two/quarantine/P2O4-T33-U05R2/petes-lake-nwi-context-r003/`;
- raw package `downloads/phase-two/raw/petes-lake-nwi-context-v0.1.0-r003/`;
- fresh run-bound terms authorization and complete source/custody gate replay;
- r001 and r002 exact-evidence rehash on initialization and every later contract load;
- a final automatically authorized same-source attempt, with no r004 absent a later explicit owner amendment.

R003 must reacquire the complete twelve-asset roster. No r001 or r002 ID, attempt, receipt, path, destination, terms authorization, or payload may seed or satisfy r003.

## Allowed implementation and gates

Allowed tracked work is the smallest Petes-specific custody and reference-fitness update, focused tests, exact LF wiring, and required milestone/precheck/registry/prompt/devlog/status records within issue #521's existing path families. No software version, release, tag, deployment, candidate, label, dataset, split, baseline, or model action is authorized.

Before r003 initialization:

1. preserve and enumerate all terminal r001/r002 evidence;
2. persist only privacy-safe controlled provider-open diagnostics: a bounded category and integer HTTP status when available, never raw exception text, headers, bodies, secrets, tokens, host-local details, or unregistered URLs;
3. prove HTTP, timeout, DNS/TLS/connection, unknown-open, privacy, one-call, no-retry, and retained-byte behavior offline;
4. bind all prior evidence on every future contract load;
5. commit, push, independently review, and verify the remediation checkpoint remote-equal;
6. confirm every r003 target is absent.

R003 must then initialize offline, pass external contract validation, perform its fresh five-page terms authorization once, pass validation again, and execute exactly one ordered asset transaction at a time. Any r003 source, terms, provider, structure, identity, custody, privacy, or integrity failure stops the roster and routes the milestone to a material remediation, fallback, exclusion, deferral, or stop exit. U06 and all later work remain blocked.
