# BurnLens Version History

## Version policy

BurnLens uses the identifier classes in `VERSIONING.md`. A tag records repository state; it does not imply an application, dataset, model, run, public release, operational readiness, or official status.

## Repository baselines

| Identifier | State | Commit | Meaning |
|---|---|---|---|
| `v0.3.0-intake-transaction-baseline` | Candidate; tag not created | Source implementation `2491766022b549402b64e3136a79fd9c046beff5`; issue #325; checkpoint commit pending | Exact three-asset contract, fail-closed validation, local multihash registration, atomic all-or-none promotion, and deterministic real-state/synthetic-rehearsal evidence. Zero credentials, provider assets/bytes, promoted real packages, or retained synthetic bytes. |
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
| Source record set | `SOURCE-2026-001` through `SOURCE-2026-007`; newest is one public NIFC reference vector |
| Metadata fixture | `METADATA-2026-001`; SHA-256 `803db2b82c7d6ef23d12c34f370dd9a7504bf181f772db22d1ed55c83c6b791a` |
| Asset-readiness record set | `SOURCE-2026-004` through `SOURCE-2026-006`; shipped at `v0.1.1-asset-readiness-baseline`; no provider asset retained |
| Asset-readiness fixture | `ASSET-READINESS-2026-001`; SHA-256 `c5bcfbf57cf23a7bf3ed9bd1302461b2ba1ee101ab05b7d935419223763e5ce7` |
| Access-integrity tool | BurnLens package `0.1.2`; Pillow `12.2.0`; shipped at `v0.1.2-access-integrity-baseline` |
| Access-precheck fixture | `VIIRS-ACCESS-PRECHECK-2026-001`; JSON SHA-256 `107c08e00539257d7b86265d316060f35c019c821acc59f89dfc4b8875205f7f` |
| AOI finalizer | BurnLens package `0.2.0`; generator source commit `bcc1d9aa494c5511ff824692199b40717d320dd4`; 16 repository tests passing |
| AOI evidence | `AOI-FINAL-2026-001`; JSON `305ddda2eda96fa31e8fb410891d3dc9c0f2b4930af5fc8ee6d2df9bae0b856c`; HTML `b45b6659f74249966368e3b2f024363469f88fa6f8f23fc4c1631b39ec009ef2`; PNG `73463794d765ca1e19051bb1f5b6dac163c82da5d11a6ea3ca77ce1ea0aeb736` |
| Paired-intake transaction | BurnLens package `0.3.0`; `paired-intake-contract-v0.1.0`; contract SHA-256 `85b6934ed3fe47dabfdddd47375dc07fc78bd0db8d15c24cb3a50c53e65b8362`; source implementation `2491766022b549402b64e3136a79fd9c046beff5`; 31 repository tests passing |
| Paired-intake rehearsal | `PAIR-INTAKE-REHEARSAL-2026-001`; JSON `1eae030c41174fa2806f218bc28db143e83ca08b1eb69230385691e29a6bddbc`; HTML `f24f2e2006505ba0b9b1f03b3910cfdd83d6ab09744ecce5baaae67f2cfcc62e`; PNG `35b1b018b208d819a8d3a785ec40c5bbdfba1cb3899f8527dfa17a72b13beba9`; real decision `BLOCKED_OWNER_CREDENTIAL` |
| Dataset | Not created |
| Label schema implementation | Not created |
| Baseline method | Not created |
| Model | Not created |
| Run | Latest `BL-2026-07-14-paired-intake-rehearsal-r001` — real empty-provider state plus temporary synthetic transaction; earlier AOI geometry run remains versioned; no imagery/provider pixels or model output |
| Report/interface | `paired-intake-rehearsal-v0.1.0`; semantic HTML and PNG hashes listed above; AOI and access report versions remain unchanged |

The source-metadata, asset-readiness, access-integrity, AOI, and intake-transaction baselines record availability, route, governance, delivery/transaction validation, and geometry evidence only. The one retained NIFC source asset is reference vector geometry, not provider imagery or a label. The intake rehearsal uses temporary synthetic bytes and retains none. None of these baselines implies that a selected scene contains a Darlene 3 detection or that the active-fire target is label-ready.

Every shipped checkpoint must update this file with its version, exact commit, evidence meaning, and explicit non-implications.
