# BurnLens Version History

## Version policy

BurnLens uses the identifier classes in `VERSIONING.md`. A tag records repository state; it does not imply an application, dataset, model, run, public release, operational readiness, or official status.

## Repository baselines

| Identifier | State | Commit | Meaning |
|---|---|---|---|
| `v0.6.0-burn-scar-target-baseline` | Issue #337 / PR #338 merged; tag withheld pending #339 | Analytical merge `68971e9709b886adf8575a58d32694aad42f038e`; remediation merge pending | Owner-approved activation of `target-burn-scar-v0.2.0`, direct active-fire label rejection, current official MTBS no-Darlene/AOI finding, and a pre/post optical source-and-protocol gate. Post-merge validation caught checkout-dependent `r001` input hashing; #339 publishes immutable LF-stable `r002` from source `cfbf357634cdcf9e68c3af78bfcb3e195bebc17a` before tagging. Zero label, dataset, baseline, model, or raw provider bytes. |
| `v0.5.0-observation-geometry-baseline` | Verified annotated tag; object `cb9e675789d8ca4c4f8a5f4828331d41d023038e` | `1c85496d9d488c0d2d5a58207d8b4786a683ba52` | Complete 23-granule NOAA-21 observation comparison, exact selected companion, uncertainty-preserving weak/reference-label protocol, and explicit label/dataset deferral, shipped through issue #333 / PR #334. Generator source `89d50c24a696cc7e3ec023eec00b021a4a0cdda6`; 24 raw assets / 83,723,055 bytes remain local and ignored; zero raw provider bytes or secret material are committed. |
| `v0.4.0-authenticated-source-baseline` | Verified annotated tag; object `98228058b232bc0838eb976f982ef4775b711776` | `7678cf41b64e128106c199b913fe74590a52cf80` | Secret-safe authenticated exact-package acquisition, real Sentinel/VIIRS array inspection, deterministic source evidence, and explicit label/dataset deferral, shipped through PR #330. Generator source `9a7e614fbfbbcd4c5a6795417121cafb82ae5dcc`. Three raw assets / 1,169,997,942 bytes remain local and ignored; zero raw provider bytes or secret material are committed. |
| `v0.3.0-intake-transaction-baseline` | Verified annotated tag | `ee1a1d678ad888b595dc3c7b215f787ea5156582` | Exact three-asset and transaction-invariant contract, link-alias rejection, fail-closed validation, local multihash registration, retry-safe atomic promotion, registered-package re-verification, and deterministic real-state/synthetic-rehearsal evidence, shipped through PR #326. Generator source `ac8ee43151991c38ccf5d446a53c09b617afeb54`. Zero credentials exercised, provider assets/bytes, promoted real packages, or retained synthetic bytes. |
| `v0.2.0-aoi-baseline` | Verified annotated tag | `fffd3dda123d7c43fe678dca9adfd8feb73de158` | Deterministic final modeling AOI, exact public NIFC reference snapshot, county/source coverage checks, and rendered non-operational evidence, shipped through PR #322. Generator source commit `bcc1d9aa494c5511ff824692199b40717d320dd4`. No imagery, label, dataset, baseline, model, or detection. |
| `v0.1.2-access-integrity-baseline` | Verified annotated tag | `d4ce26c87341e4d3798a0d84e257a964ebd2cde0` | Runnable fail-closed provider-payload validator plus normalized and rendered credential-block evidence, shipped through PR #318. Zero provider assets or analytical pixels. |
| `v0.1.1-asset-readiness-baseline` | Verified annotated tag | `cf4aba2f40aa426f28f09b1b1b1bad895394198b` | Exact Sentinel-2 product and same-day NOAA-21 VIIRS fire/geolocation route contract plus metadata-only readiness fixture, shipped through PR #314. No credential, provider asset, detection, label, dataset, or analytical capability. |
| `v0.1.0-source-metadata-baseline` | Verified annotated tag | `6abe87bba486e3fe49b6c06178b454335663cb73` | First Phase Two source-readiness package: versioned discovery AOI, three reviewed source records, terms/access/precheck/provenance controls, and a normalized public-metadata fixture. No source assets or analytical capability. |
| `v0.0.8-execution-goal-baseline` | Verified annotated tag | `22a8d88435cb8d5b900a398b7482c3b7277d2ee6` | Controlling execution goal, six-phase roadmap, repository-only product boundary, and active status/log baseline. No analytical capability. |
| `v0.0.7-objective-seven-phase-one-baseline` | Historical candidate only; never created as a tag | Eligible historical target `10caebb3d61ff622dc6dfe8809a63886089eba4e` | Phase One documentation/control candidate approved for Phase Two planning only. |

An authenticated tag inventory at goal activation on 2026-07-13 returned no tag refs. After PR #291 merged, the annotated `v0.0.8-execution-goal-baseline` tag was created, pushed, and independently dereferenced to the exact merge commit. Historical text that treated the tag inventory as inaccessible is superseded for current status, but remains part of the audit trail.

## Artifact versions

| Class | Current version |
|---|---|
| Application | Not created |
| AOI | `aoi-darlene3-model-v0.2.0` — accepted and shipped final modeling AOI; supersedes the discovery version for modeling |
| Source record set | `SOURCE-2026-001` through `SOURCE-2026-008`; newest is the exact NOAA-21 observation inventory and selected companion |
| Metadata fixture | `METADATA-2026-001`; SHA-256 `803db2b82c7d6ef23d12c34f370dd9a7504bf181f772db22d1ed55c83c6b791a` |
| Asset/source record set | `SOURCE-2026-004` through `SOURCE-2026-008`; exact source and observation-screen packages registered in ignored local raw storage; zero raw provider bytes committed |
| Asset-readiness fixture | `ASSET-READINESS-2026-001`; SHA-256 `c5bcfbf57cf23a7bf3ed9bd1302461b2ba1ee101ab05b7d935419223763e5ce7` |
| Access-integrity tool | BurnLens package `0.1.2`; Pillow `12.2.0`; shipped at `v0.1.2-access-integrity-baseline` |
| Access-precheck fixture | `VIIRS-ACCESS-PRECHECK-2026-001`; JSON SHA-256 `107c08e00539257d7b86265d316060f35c019c821acc59f89dfc4b8875205f7f` |
| AOI finalizer | BurnLens package `0.2.0`; generator source commit `bcc1d9aa494c5511ff824692199b40717d320dd4`; 16 repository tests passing |
| AOI evidence | `AOI-FINAL-2026-001`; JSON `305ddda2eda96fa31e8fb410891d3dc9c0f2b4930af5fc8ee6d2df9bae0b856c`; HTML `b45b6659f74249966368e3b2f024363469f88fa6f8f23fc4c1631b39ec009ef2`; PNG `73463794d765ca1e19051bb1f5b6dac163c82da5d11a6ea3ca77ce1ea0aeb736` |
| Paired-intake transaction | BurnLens package `0.3.0`; `paired-intake-contract-v0.4.0`; full contract SHA-256 `5135b6b0b554e533df98ede568b1eafbd45c692b73a1e1abd3e50ba098f0958d`; report-generator source `ac8ee43151991c38ccf5d446a53c09b617afeb54`; 37 repository tests passing |
| Paired-intake rehearsal | `PAIR-INTAKE-REHEARSAL-2026-001`; JSON `94e311fd608f9c10e024138d9eff6abf0f70187a69c031264e91cb8d9d1af234`; HTML `b76cbf50f60dd112430616b4a472ac440444cbf48194a0672df91876e78ea20c`; PNG `c38bf7fc825dd780affe3f8d1080cffb3bdb90ef2164cb27b1295b4e54bbfcd0`; historical pre-authorization decision `BLOCKED_OWNER_CREDENTIAL` |
| Credential authorization | `ACCESS-2026-006`; owner-authorized CDSE and Earthdata use on 2026-07-14; owner-attested setup `PASS`; no credential loaded, request made, or provider byte retained by BurnLens in that record |
| Authenticated acquisition | `ACCESS-2026-007`; run `BL-2026-07-14-authenticated-intake-r001`; exact three-asset package / 1,169,997,942 bytes accepted locally; credentials used at runtime with zero secret material retained |
| Source-inspection tool | BurnLens package `0.4.0`; h5py `3.16.0`; NumPy `2.5.1`; Pillow `12.2.0`; Rasterio `1.5.0`; generator source `9a7e614fbfbbcd4c5a6795417121cafb82ae5dcc`; 56 repository tests passing |
| Source-inspection evidence | `SOURCE-INSPECTION-2026-001`; JSON `cbd4dfba840680256a100aeca1a2e0b28483796f7e7b79b90de8b933d58b0a53`; HTML `76d13d3e105f053410d0063b17eb740f732c786dc395fe13335701496cbb41a0`; PNG `da93de6e432296f72c8f420d0181cfc81d99be7cf70ad96fe5b7bba619739966`; decision `ACCEPT_SOURCE_REFERENCE_DEFER_LABELS` |
| Observation-geometry tool | BurnLens package `0.5.0`; generator source `89d50c24a696cc7e3ec023eec00b021a4a0cdda6`; `observation-screen-contract-v0.2.0`; `weak-reference-label-feasibility-v0.1.0`; 65 post-merge tests passing |
| Observation-geometry evidence | `OBSERVATION-GEOMETRY-2026-001`; JSON `c1da1c47483ab573a8a123a26f7c5b2f111b57b4eaedb05ffb2d3aafa46e881d`; HTML `a63ee62c660c7b573d829847ac008786a6ecff91c61f5433365e640f64742ad2`; PNG `4dd21c3df693856fda47d23cd763054016a105d8c760181c4052411fa4ff6687`; decision `ACCEPT_COMPLEMENTARY_REFERENCE_GEOMETRY_DEFER_LABELS` |
| Active target decision | `target-burn-scar-v0.2.0`; owner-approved 2026-07-14; active-fire source retained as complementary reference only; no severity/multiclass expansion |
| MTBS availability record | `MTBS-DARLENE3-AVAILABILITY-2026-001`; current 2024 inventory 941 records; zero Darlene name matches; zero 2024/all-years AOI features; metadata use resolved with citation; any future exact product requires fresh metadata/terms validation |
| Target-decision tool | BurnLens package `0.6.0`; remediation source `cfbf357634cdcf9e68c3af78bfcb3e195bebc17a`; fails closed on contradictory source evidence; LF-normalizes structured-input hashes and writes target JSON/HTML with explicit LF serialization; 69 repository tests passing before PR |
| Target-decision evidence | Corrected `TARGET-DECISION-2026-002`; JSON `ac67f6c34a934d639c215ee98b181f1114b5624acafb85f65b1e2f3e804ce4d4`; HTML `0c1279e5e1047ff251dcd65f068d3d45bf2c6982e6a308972205e9d0a76879d4`; PNG `36f221aa6393ad07f14d4d7bb54b1f171ef0636ebb5640a11ab02ab9c5a9b5b0`; decision `ACTIVATE_BURN_SCAR_BINARY_MASK_FALLBACK`; `001` preserved as pre-remediation evidence |
| Dataset | Not created |
| Label schema implementation | Not created |
| Baseline method | Not created |
| Model | Not created |
| Run | Latest corrected `BL-2026-07-14-target-decision-r002` - owner-approved target-path evidence; `r001` preserved as pre-remediation evidence; no label, dataset, baseline, model, or analytical inference output |
| Report/interface | `target-path-decision-v0.1.0`; semantic HTML and PNG expose the target decision, active-fire disposition, current MTBS result, next gate, warning, run ID, source commit, and null app/dataset/label/baseline/model versions |

The source-metadata, asset-readiness, access-integrity, AOI, and intake-transaction baselines record availability, route, governance, delivery/transaction validation, and geometry evidence. The `0.4.0` baseline adds real provider source/reference inspection. The shipped `0.5.0` baseline adds complete observation comparison and an explicit no-label protocol. The `0.6.0` candidate activates the controlled burn-scar target and records its next evidence gate without creating analytical output. None is a BurnLens detection or label set; no provider hotspot, perimeter, MTBS severity class, or absence record is pixel-perfect segmentation truth.

Every shipped checkpoint must update this file with its version, exact commit, evidence meaning, and explicit non-implications.
