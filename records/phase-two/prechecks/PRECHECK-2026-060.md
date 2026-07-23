# PRECHECK-2026-060 - Windigo optical custody pass

**Unit / issue / branch:** `P2O4-T35-U02` / #534 / `codex/p2o4-t35-windigo-deadline-gate`

**Decision:** `PASS_WINDIGO_OPTICAL_CUSTODY_AUTHORIZE_REFERENCE_REQUEST_PREFLIGHT`

**Cutoff:** July 27, 2026 at 6:00 PM America/Indianapolis

## Scope and boundaries

U02 acquired only the U01-frozen Sentinel-2 L2A pair. It used runtime-only CDSE credentials, sequential singleton transactions, ignored quarantine and raw custody, no-overwrite promotion, exact current OData identity, provider and local hashes, safe ZIP/root/member/CRC checks, registration manifests, and post-promotion rehash.

This pass authorizes only the already contracted single combined BAER/RAVG/MTBS Portal request. It does not authorize delivered reference pixels, candidates, labels, a dataset, a split, a baseline, a model, or a Phase Two completion claim. Exact delivered notices, identities, archive safety, CRS, grids, nodata, class domains, masks, terms, and program limitations must still pass.

## Exact custody

| Role | Provider UUID | SAFE archive | Bytes | Local SHA-256 | Provider MD5 | Provider BLAKE3 |
|---|---|---|---:|---|---|---|
| pre | `f1111cd2-acb1-4324-9b48-854e2e71a384` | `S2A_MSIL2A_20220726T185931_N0510_R013_T10TEP_20240712T042551.SAFE.zip` | 1,185,125,439 | `6a62dd98ce619f53a2dc4e8348de5503edac6cfe3cf58449cdb0de98750d8034` | `6103928264ef49f78cbc6200e613b158` | `13541bf3ea1c56269b3b4667e0051f7d95bbe7b64b69a9228ce1f2f9899fa17f` |
| post | `10bb27c6-5df5-44f1-9a72-517c696cb5e1` | `S2A_MSIL2A_20220815T185931_N0510_R013_T10TEP_20240703T124031.SAFE.zip` | 1,187,986,637 | `18a40c3c7a8c14443892461876ed1deafab1b22d54446802cc394bd465910987` | `9aa84788fd136aad2da9a30dacc17330` | `1923a7089f58278add5f2f2692139cbf4bf2a900ec8ca4afb8a4b8391ce89cff` |

Combined provider bytes are exactly 2,373,112,076. Registration manifests are 937 bytes / SHA-256 `3ac05e85e5207ffb3d0ff9ea2f5e9e6332e49c298f77eff4826ee5c6aa5ad3e9` and 940 bytes / SHA-256 `7b4de9bcbe7fac9037b41dd58b0ec589283ff5bdd9a9a3f200bf5d27e7527c34`.

The corrected tracked report is `samples/cross-event/phase-two/windigo/WINDIGO-OPTICAL-CUSTODY-2026-002.json`: 6,579 bytes, SHA-256 `b05d3e71052331e094957717da798117776965b728e717bfe525b8b5196dc755`, schema `0.1.1`, run `BL-2026-07-23-windigo-optical-intake-r001`, source commit `3167287da34bcabf99284da51e813eb0b03aa59c`.

## Retained attempts and reconciliation

The first pre attempt is immutable at 2,798 state bytes / SHA-256 `e02fce0508a763b7603f72e50bdf3c25c721fa2f15c8e3a26a6598d3a11b7af6`. Its interrupted partial was 134,217,728 bytes / SHA-256 `5fac4900d65591f3c44c6ee3dec3939a27b0759e22656e0a7c2d5bac38c54c75`; CDSE did not honor the later Range request, so the successful pre transfer restarted safely without overwriting promoted custody.

The first post attempt is immutable at 4,243 state bytes / SHA-256 `55cb89d8b03d8d254f9446c07dde01e33f1307e6c1e104ae2b8cd44ad34aadde`. It retains a 102,760,448-byte partial / SHA-256 `3c057925cfc5323887a56d0e87487b7f95de1c1d7fb28029920b9f58e936ad77` after two stream timeouts and later transport failures. The distinct r002 transaction used a 600-second timeout and two-attempt maximum; it succeeded on its first attempt.

Successful private states are:

- pre r002: 7,825 bytes / SHA-256 `b852693651fc64ae77f66e2532eeeedccf1ce281025b4c53839aed9f30fbda67`;
- post r002: 7,418 bytes / SHA-256 `46499f1a0760408344dd30b4cba740839a2aa7de53ec6333ab62b178852a6e8e`;
- aggregate r001: 4,320 bytes / SHA-256 `f48442c1be7a0484fc5068f5d357a5c5fc6a7415113d70f870918a6f24764136`.

The first generated public report omitted the retained pre interruption. Its exact 5,338 bytes / SHA-256 `8ed642b2bc100f774f11d6e592e63f60f2fb261d23475132c3ed2b471facbe01` are preserved as superseded evidence. Report `2026-002` was rebuilt without provider access from the already verified states and packages; it explicitly retains both failures.

## Validation

- credential-free live OData preflight: pass, two exact products;
- focused final custody/transport tests: 44 passed;
- broader transport plus historical source-gate regressions: 50 passed and two subtests passed;
- full suite at the transport-remediation checkpoint: 551 passed, one skipped, 20 existing warnings, 83 subtests passed;
- final credential-free completed-custody verification: pass;
- wrapper stderr: zero bytes;
- `BURNLENS_CDSE_USERNAME` and `BURNLENS_CDSE_PASSWORD` absent after the transaction;
- no provider, wrapper, or review process remains running.

## Disposition and next dependency

U02 optical custody passes. The only eligible next action is one combined official Portal request for BAER `10022395`, RAVG `10022960`, and MTBS `10029547`, followed by exact delivered-byte and notice inspection. U03 remains blocked until that delivery passes its source, terms, custody, identity, integrity, and native-pixel fitness gates.
