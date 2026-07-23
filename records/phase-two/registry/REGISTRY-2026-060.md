# REGISTRY-2026-060 - BL-EXC-001 corrected 0.45.0 runtime-contract candidate

**Exception unit / issue / branch:** `BL-EXC-001-U03` / #528 / `codex/bl-exc-001-v045-runtime-contract`

**Run:** `BL-2026-07-22-v045-runtime-contract-verification-r001`

**Affected milestone:** P2O4-T33 / issue #521 / PR #527; reviewed head `925b660119c230d292063be5de1064fdd007e83a`; true merge `7d5c07e6b337b6b801b9d41565deedd9d2180b00`

**Exception base / package-sensitive code / tree:** `7d5c07e6b337b6b801b9d41565deedd9d2180b00` / `4bf76eaf1f123d72c9fee11db9035724c3351eac` / `90768cb44b3e3596b38d705b215c9129a42c844a`

**Pushed corrected package checkpoint / tree / PR:** `4bf76eaf1f123d72c9fee11db9035724c3351eac` / `90768cb44b3e3596b38d705b215c9129a42c844a` / #529; this record-only reconciliation remains package-excluded and must be checked at the exact reviewed head before merge

**Disposition / release state:** U01 `remediate`; U02 `pass`; U03 `pass`; U04 `pending`; BurnLens `0.45.0` remains an untagged candidate and `v0.45.0-petes-lake-material-defer` remains withheld

## Scope and predecessor

REGISTRY-2026-059 remains the immutable P2O4-T33 material-defer candidate ledger. It correctly preserves the scientific decision, all U01-U11 milestone evidence, the failed 798,433-byte precursor wheel, and the then-current 800,916-byte pre-exception wheel. This record supersedes only its pending-PR and current-package statements after PR #527 merged and the urgent runtime-contract exception began. It does not rewrite REGISTRY-2026-059 or change any Petes source, terms, custody, raster, render, accepted reference pixel, owner decision, prototype label, accepted event, dataset, split, baseline, or model fact.

## Exception evidence-unit ledger

| Unit | Purpose and exact input | Gates and result | Disposition | Retained failure / next dependency |
|---|---|---|---|---|
| `BL-EXC-001-U01` / `BL-2026-07-22-v045-runtime-dependency-contract-r001` | Independently install and probe the merged P2O4-T33 wheel from merge `7d5c07e6...`; 800,916 bytes / SHA-256 `4e0bd99fec24d693b29be78c7dc943aedeaebaac3c37f1cf48442d507fa2eaa6` | Dependency integrity passes, but only 80 of 81 entry points load and clean `dev` cannot collect the documented suite | `remediate` | Immutable merged-main failure; U02 must preserve the lean optional-geo design while making the package contract true |
| `BL-EXC-001-U02` / `BL-2026-07-22-v045-runtime-contract-remediation-r001` | Exception registration/capsule checkpoint `882d6d3349bb023f699cba04e839959ecf6ea0e2`; route amendment; pushed code `c4387c932ab89ab5857299293ceb469e28f126e4` | All 81 commands load, are callable, and show help; real geo-only execution fails bounded before repository preflight without GeoPandas, Pyogrio, PyProj, and Shapely; 21 focused tests pass with one expected conditional skip; all 33 U05 scientific function ASTs and moved contract values remain exact | `pass` | Proceed through fresh dev, geo-research, custody-enabled, replay, and deterministic-package verification |
| `BL-EXC-001-U03` / `BL-2026-07-22-v045-runtime-contract-verification-r001` | Package-sensitive code `4bf76eaf1f123d72c9fee11db9035724c3351eac`; tree `90768cb44b3e3596b38d705b215c9129a42c844a`; immutable U03/U04 inputs and prior wheels | Fresh dev, geo-research, canonical-custody, bounded absent/unusable-geo failure, exact replay, 81-command, lock-byte, deterministic-wheel, metadata, RECORD, privacy, and forbidden-path gates pass | `pass` | Retains the five failed or superseded U03 attempts below; U04 must review exact PR #529 head, merge, repeat fresh-main gates, and verify the remote annotated tag before release |
| `BL-EXC-001-U04` | Exact reviewed PR #529 head and this record | Exception PR, fresh merged-main runtime/dev/geo/custody/replay/package gates, exact annotated-tag peel, and bounded lifecycle handoff | `pending` | No tag, GitHub Release, deployment, provider, scientific, label, data, or model action is authorized by U03 |

## Retained failed U03 attempts

1. At records checkpoint `d330eb2a7949beb1610d704a3ff75897a7818a02`, two clean builds are byte-identical at 801,833 bytes / SHA-256 `b3db6eecefa8166b9ab732920d3970d13a016500ee458ba5ae1e385297a595e7`. They are retained as superseded U03 package evidence because later required dev, replay, and checkout-stability gates had not yet passed.
2. The first clean `dev` proof at `d330eb2a7949beb1610d704a3ff75897a7818a02` reported 25 failed, 488 passed, 24 skipped, 16 warnings, and 56 subtests. Synthetic wetland-custody tests had not patched the newly added locked-geometry runtime gate, so they traversed the real Shapely boundary; one genuine polygon-validation test also required Shapely. No dependency was added to `dev`; checkpoint `cbc824c1e925bb11a4bf98b7f9422419b254b22f` patches the gate only in synthetic state-machine tests and explicitly skips only the genuine polygon test when the geo profile is absent.
3. The first exception-branch U04 replay stopped before output on the exact unsupported-branch gate. Checkpoint `77d32c5e2408fa1215ca02b53ef30a0cb8c69b21` admits only `codex/bl-exc-001-v045-runtime-contract` in addition to the historical milestone branch and `main`; historical, base, and current non-trace scientific fingerprints remain `3e6a940b62a99c17e1b91099ce5aae66a76494b8575d8f11830b3fc551e4ec59`.
4. The first cross-clone package comparison exposed checkout-dependent `uv.lock` bytes. Checkpoint `5e55ec8afd193d28c6c71191f0cca64c9aa31c29` binds `uv.lock` to `text eol=lf`; fresh proof matches the exact 207,817-byte Git blob, SHA-256 `24071eb7b57ba57cc2728635427dc57643d7d96ac8fa58a4030052abad8dcbba`, with zero carriage returns.
5. Exact-head review at candidate `1288aa26e20d3ba95de7aa9fb4293d99abd45d13` found that `_load_implementation()` wrapped only `ImportError`. An installed-but-unusable optional geo stack could instead raise `OSError`, `AttributeError`, or another initialization `Exception`, leaking host detail or a traceback instead of the promised bounded exit 2. The 801,911-byte / `055e56b1...` wheel is retained as superseded pre-review evidence. Correction `4bf76ea...` wraps the import-time `Exception` boundary and tests sanitized `ImportError`, `OSError`, and `AttributeError` failures before repository preflight.

None of these attempts changes a scientific output or authorizes a wider runtime dependency surface.

Validation-harness findings are also retained. An initial installed-replay harness misread a nested path manifest and produced no mutation or usable evidence; the corrected replay passed. Generic `python -m pip check` was unavailable because the locked environment intentionally omits pip; the prescribed `uv pip check` passed. One package-audit harness imported a constant from the wrong module; the corrected audit passed against unchanged repository and wheel bytes. The first pre-PR Markdown-link command passed an empty parent for root-level Markdown files to PowerShell `Join-Path`; the corrected audit treats the repository root as `.` and passes 707 pre-existing tracked Markdown files plus this registry, 214 local links, and zero missing targets. The first final LF command incorrectly required the legacy canonical working file to have been rewritten already, then used two static .NET hash-format helpers unavailable in Windows PowerShell; the corrected instance-based audit proves that the 209,144-byte / 1,327-CR legacy working file normalizes exactly to the 207,817-byte / `24071eb7...` committed identity, while the separate fresh no-hardlink checkout supplies the required zero-CR proof.

## Exact environment and regression proof

| Environment | Installed distributions / optional modules | Regression result | Command and environment result |
|---|---|---|---|
| Fresh locked `dev`, no custody | 18 distributions; all eight geo-research modules absent | 499 passed, 25 explicitly disclosed skips, 16 warnings, 81 subtests | Exact profile and bounded absent/unusable-geo verification pass; 81/81 installed commands load and show help |
| Fresh locked `geo-research`, no custody | 66 distributions | 515 passed, 23 expected custody skips, 16 warnings, 81 subtests | Runtime and complete offline geospatial smoke pass; 81/81 installed commands load and show help |
| Canonical geo-research with ignored custody | 66 locked distributions | 537 passed, 1 expected unfinalized-NWI skip, 20 retained NumPy warnings, 81 subtests | Dependency, compile, diff, exact-custody, and actual-pipeline checks pass |

Profile-dependent skips are explicit. A profile capability or software pass is not source, scientific, label, dataset, or model fitness.

The pre-PR record audit parses all 121 tracked JSON documents, finds zero missing targets across the 214 local Markdown links, verifies zero CR bytes plus exact LF attributes for this registry and `uv.lock`, passes `git diff --check`, and finds zero added-line private-path, signed-query, bearer-token, private-key, or forbidden-repository findings.

## Corrected package and exact replay

Two separate fresh no-hardlink clones at pushed package-code checkpoint `4bf76eaf1f123d72c9fee11db9035724c3351eac` independently produce the exact `burnlens_deschutes-0.45.0-py3-none-any.whl`: 801,906 bytes / SHA-256 `8e17c18a53b7770b6de00b9668d02efa9b07945329672ed29883798442d906ea`. The files are byte-identical and contain 170 unique entries: 164 package files and six dist-info files. All 81 console commands retain their exact mappings, RECORD has exactly 170 rows, package metadata identifies BurnLens 0.45.0, and no forbidden path is present. Both clones have the exact 207,817-byte zero-CR lock and remain clean. Earlier builds through `1288aa2...`, including the 801,911-byte / `055e56b1...` wheel, remain exact superseded evidence rather than current-candidate proof.

The corrected wheel and final source reproduce the same tracked pipeline outputs:

| Output | Bytes | SHA-256 | Result |
|---|---:|---|---|
| Planned U03 JSON | 56,285 | `ac9befd021d71ff779ec56ddefc894f4e39b92e64e65c2c4afb815663d1ad443` | Exact; retained snow-dominated planned-post rejection |
| Planned U03 PNG | 626,846 | `4ed3870e37bf68db24805540f00614c5050c064b621ca3fc5e3c0ef244bf0d42` | Exact; warning and no-label boundary remain legible |
| Replacement U03 JSON | 60,069 | `1aa88c0021c610e492d2645e3f2c49a4afe96d9d907e2ee4481948a4c58f2ebd` | Exact; pass with all spatial exclusions retained |
| Replacement U03 PNG | 588,891 | `fd5b9ae54e1b9c3e0d495e337387d874ae911bd0f586e835b4184312d486d931` | Exact; exclusions and no-label boundary remain legible |
| U04 native-contract JSON | 32,991 | `b489bd30b467ab38f7320c9b313f904e0bbe9a33e2bed8b346230b9f48a6053c` | Exact; zero accepted reference pixels |

The replay proves unchanged computation and packaging, not a Petes U05 scientific pass. Production U06-U10 remain unexecuted/deferred, Petes Lake is not event six, and `owner-approved-prototype-region-labels-v0.3.0` remains unchanged.

From the clean, remote-equal corrected package checkpoint, the actual U04 command independently reconstructs the exact 32,991-byte / `b489bd30...` JSON in ignored no-overwrite storage and again reports zero accepted reference pixels. No provider call or custody mutation occurs.

## Release boundary

PR #527 and true merge `7d5c07e6b337b6b801b9d41565deedd9d2180b00` are completed historical milestone facts. Exception PR #529 exists and is unmerged; its exact reviewed head, merge, fresh-main verification, and remote tag peel do not yet exist. The latest verified release remains v0.44. No local or remote `v0.45.0-petes-lake-material-defer` tag, GitHub Release object, or deployment exists. README and changelog candidate truth identify the current exception hold; lifecycle, status, roadmap, case-study, version-history, VERSIONING, and manifest updates must wait for exact U04 identities.
