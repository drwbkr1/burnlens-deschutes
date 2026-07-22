# REGISTRY-2026-057 - Petes Lake U05R2 final NWI intake remediation

**Unit / issue / branch:** `P2O4-T33-U05R2` / #521 / `codex/p2o4-t33-petes-lake-milestone`

**Terminal inputs:** `BL-2026-07-21-petes-lake-nwi-context-r001`; `BL-2026-07-22-petes-lake-nwi-context-r002`

**Registered replacement:** `BL-2026-07-22-petes-lake-nwi-context-r003` / `petes-lake-nwi-context-2026-003`

**Code checkpoint:** `1b8c1ad52043536f243b178d279922ceb469103d`

**Decision:** `PASS_OFFLINE_OBSERVABILITY_AND_DISJOINT_R003_CODE_GATE`

**Disposition / next dependency:** U05R2 code `pass`; r003 `not initialized` / commit and push this record sync, prove remote equality and clean preflight again, initialize r003 offline from that exact source commit, validate externally, refresh the five official terms pages once, validate again, then execute asset one only

## Immutable failure chain

R001 remains the five-file qualified-field-validation failure recorded by REGISTRY-2026-055. R002 remains the nineteen-file terminal intake recorded by REGISTRY-2026-056: seven promoted assets, one failed Data Source pre-count attempt at `PROVIDER_OPEN`, four unexecuted assets, and an exact zero-byte failed partial. All 24 files are ignored, untracked, single-link, and exact. R002 still passes the external intake validator with local-file verification. Neither prior run is retried, continued, finalized, copied, relabeled, selected for U05 fitness, or used to seed r003.

The r003 state machine rehashes every one of those 24 paths before initialization and on every later contract load. It separately verifies r002's unit, run, intake, source commit, twelve-asset order, `promoted x7 / failed x1 / authorized x4` state, sole failed attempt, generic failure code and stage, and zero-byte retained identity. It also proves that each of r003's twelve provider URIs, methods, request-body hashes, feature/non-feature CRS roles, logical roles, destination basenames, and staging filenames remains identical to the exact hash-bound r002 contract. Only the run-scoped IDs, attempts, authorization receipt, and custody roots change.

## Disjoint r003 contract

R003 uses unit `P2O4-T33-U05R2`, asset prefix `petes-lake-nwi-r003-`, and these wholly disjoint roots:

- contract, plan, terms, mutex, and dispatch: `downloads/phase-two/runs/P2O4-T33-U05R2/`;
- staging: `downloads/phase-two/quarantine/P2O4-T33-U05R2/petes-lake-nwi-context-r003/`;
- raw package: `downloads/phase-two/raw/petes-lake-nwi-context-v0.1.0-r003/`.

The complete ordered roster remains Wetlands metadata/count/IDs/features/post-count/post-IDs followed by Data Source metadata/count/IDs/features/post-count/post-IDs. Every asset has one `-attempt-001` only. No r001/r002 asset ID, attempt, path, dispatch receipt, terms receipt, destination, or payload is reused. The contract records that r003 is the final automatically authorized same-source attempt; no r004 exists without a later explicit owner amendment.

## Privacy-safe failure evidence

Only a failure caught while the stage is exactly `PROVIDER_OPEN` gains `provider_open_diagnostic`. Its closed schema is `{category, http_status}`. Categories are `http`, `timeout`, `dns`, `tls`, `connection`, and `unknown-open`; `http` requires a non-Boolean integer from 100 through 599, while every other category requires null status. Classification is type-only. It does not stringify the exception, inspect HTTP bodies, or persist provider error text, headers, tokens, private URLs, host-local details, or response content. The raised custody error suppresses the provider exception context from normal traceback display.

Every failed attempt's actual staging path is re-opened safely and rehashed on every contract load. Mutation, deletion, link substitution, or other identity drift fails closed. Failures after response open retain their exact response-header/body/structure stage without a provider-open diagnostic. A failed asset remains terminal and cannot be fetched a second time.

## Exact code checkpoint

| Artifact | Bytes | SHA-256 | Role |
|---|---:|---|---|
| `burnlens/petes_lake_wetland_custody.py` | 136,929 | `6225bfe1a126c40386b6b28c2ecd9045a0a7e8fdfaa48c50692cbfc76dfb2915` | r003 identity, exact r001/r002 bindings, same-source request proof, privacy-safe open diagnostics, failed-byte rehash, final-attempt policy |
| `burnlens/petes_lake_reference_fitness.py` | 61,049 | `238218e08c3b1693674c3e024ed2cc36421865be3e679bf20f810efe1d683c72` | downstream custody-unit/run/path binding while preserving U05 scientific logic and logical-role loading |
| `tests/test_petes_lake_wetland_custody.py` | 52,614 | `001cac6fc3aa41fd8e9253b7faaed119f1378c2533a30b3e08d54679d9b43752` | disjoint identity, exact prior evidence, HTTP/network categories, privacy, schema tamper, one-call/no-retry, retained-byte mutation/deletion |
| `tests/test_petes_lake_reference_fitness.py` | 18,042 | `d72b6c56c1c22c2326eb90df212957c21e92d3d4df036d84303231b180da3ae0` | exact U05R2 custody-unit and forward-time compatibility |

## Verification

- Focused custody/reference suite: 40 passed, one expected pre-finalized-r003-custody skip, and 24 subtests.
- Final exact-checkpoint full suite: 520 passed, one expected skip, 20 existing NumPy deprecation warnings, and 74 subtests.
- A synthetic r003 timeout reaches one mocked provider open, retains only `{category: timeout, http_status: null}`, preserves the exact zero-byte partial, reloads through BurnLens's local rehash gate, and passes the external intake validator with local-file verification. The private sentinel is absent from serialized state.
- HTTP 503, no-follow HTTP 302, timeout, DNS, TLS, connection, and unknown-open cases each call the opener exactly once. A second fetch never calls it. Invalid categories, extra fields, Boolean/string/out-of-range HTTP status, non-HTTP status, and stage/diagnostic mismatch fail closed.
- Exact r001/r002 bindings, tracked SOURCE-2026-032, TERMS-2026-028, PRECHECK-2026-055, and REGISTRY-2026-056, request equivalence, external r002 validation, compilation, LF/index state, 66-package compatibility, diff, and privacy/boundary scans pass.
- Independent review found one retained-failed-byte rehash gap. The implementation and mutate/delete regressions close it; two subsequent independent re-reviews found no material issue.
- The code checkpoint is pushed and remote-equal. A credential-free repository preflight passes from exact commit `1b8c1ad52043536f243b178d279922ceb469103d` without creating run state.
- The r003 run, quarantine, and raw-package roots remain absent. No r003 terms page, provider endpoint, response, or byte has been requested.

This code gate does not pass NWI custody or U05 scientific fitness and accepts zero reference pixels. U06 and every candidate, owner response, label, sixth-event, dataset, split, baseline, model, metric, version, release, tag, deployment, field-validation, official, endorsed, operational, or emergency-ready claim remain blocked.
