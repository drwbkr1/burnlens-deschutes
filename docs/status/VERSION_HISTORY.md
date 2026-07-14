# BurnLens Version History

## Version policy

BurnLens uses the identifier classes in `VERSIONING.md`. A tag records repository state; it does not imply an application, dataset, model, run, public release, operational readiness, or official status.

## Repository baselines

| Identifier | State | Commit | Meaning |
|---|---|---|---|
| `v0.2.0-aoi-baseline` | Candidate on issue #321 branch; not yet a tag | Generator source `bcc1d9aa494c5511ff824692199b40717d320dd4`; checkpoint commit pending | Deterministic final modeling AOI, exact public NIFC reference snapshot, county/source coverage checks, and rendered non-operational evidence. No imagery, label, dataset, baseline, model, or detection. |
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
| AOI | `aoi-darlene3-model-v0.2.0` — accepted final modeling AOI candidate; supersedes the discovery version for modeling |
| Source record set | `SOURCE-2026-001` through `SOURCE-2026-007`; newest is one public NIFC reference vector |
| Metadata fixture | `METADATA-2026-001`; SHA-256 `803db2b82c7d6ef23d12c34f370dd9a7504bf181f772db22d1ed55c83c6b791a` |
| Asset-readiness record set | `SOURCE-2026-004` through `SOURCE-2026-006`; shipped at `v0.1.1-asset-readiness-baseline`; no provider asset retained |
| Asset-readiness fixture | `ASSET-READINESS-2026-001`; SHA-256 `c5bcfbf57cf23a7bf3ed9bd1302461b2ba1ee101ab05b7d935419223763e5ce7` |
| Access-integrity tool | BurnLens package `0.1.2`; Pillow `12.2.0`; shipped at `v0.1.2-access-integrity-baseline` |
| Access-precheck fixture | `VIIRS-ACCESS-PRECHECK-2026-001`; JSON SHA-256 `107c08e00539257d7b86265d316060f35c019c821acc59f89dfc4b8875205f7f` |
| AOI finalizer | BurnLens package `0.2.0`; generator source commit `bcc1d9aa494c5511ff824692199b40717d320dd4`; 16 repository tests passing |
| AOI evidence | `AOI-FINAL-2026-001`; JSON `305ddda2eda96fa31e8fb410891d3dc9c0f2b4930af5fc8ee6d2df9bae0b856c`; HTML `b45b6659f74249966368e3b2f024363469f88fa6f8f23fc4c1631b39ec009ef2`; PNG `73463794d765ca1e19051bb1f5b6dac163c82da5d11a6ea3ca77ce1ea0aeb736` |
| Dataset | Not created |
| Label schema implementation | Not created |
| Baseline method | Not created |
| Model | Not created |
| Run | `BL-2026-07-14-aoi-final-r001` — geometry-only evidence run; no imagery/provider pixels or model output |
| Report/interface | `aoi-evidence-v0.1.0`; semantic HTML and PNG hashes listed above; access report remains `viirs-access-precheck-v0.1.0` |

The source-metadata, asset-readiness, access-integrity, and AOI baselines record availability, route, governance, delivery validation, and geometry evidence only. The one retained NIFC source asset is reference vector geometry, not provider imagery or a label. None of these baselines implies that a selected scene contains a Darlene 3 detection or that the active-fire target is label-ready.

Every shipped checkpoint must update this file with its version, exact commit, evidence meaning, and explicit non-implications.
