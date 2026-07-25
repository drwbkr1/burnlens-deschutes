# REGISTRY-2026-090 - P2O5-T03 U07 release candidate

**Recorded:** 2026-07-25

**Issue:** #562

| Unit | Run / source | Inputs / outputs | Gates | Disposition | Next dependency |
|---|---|---|---|---|---|
| `P2O5-T03-U07-PORTFOLIO-R001` | `BL-2026-07-25-p2o5-t03-u07-portfolio-r001`; source `d0456f5...` | report `2026-002`; JSON `66dbd4aa...`; HTML `681c1433...` | exact replay passes; real render exposes shifted Petes image/decision bindings | `remediate-retained` | role-based binding |
| `P2O5-T03-U07-PORTFOLIO-R002` | `BL-2026-07-25-p2o5-t03-u07-portfolio-r002`; source `e013a76...` | report `2026-003`; JSON `0c4f6ba6...`; HTML `927af4a2...` | exact roles/replay pass; selection-bias cause is not explicit on page | `remediate-retained` | expose evidence risk |
| `P2O5-T03-U07-PORTFOLIO-R003` | `BL-2026-07-25-p2o5-t03-u07-portfolio-r003`; source `403a2f3...` | report `2026-004`; JSON `1fc9f1e6...`; HTML `cc64bbce...` | exact replay; desktop/narrow; both images; links; keyboard; privacy; explicit limits; empty browser log; zero external requests | `pass` | release QA |
| `P2O5-T03-U07-SUITE-R001` | lean `dev` profile | no product output | five GeoPandas-dependent collection errors because the wrong profile was selected | `invalid-environment-retained` | restore locked geo profile |
| `P2O5-T03-U07-SUITE-R002` | locked `dev + geo-research` | 693 pass / 2 fail / 1 skip / 228 warnings / 86 subtests | detects stale 99-command expectation and missing devlog LF rule | `remediate-retained` | release-contract correction |
| `P2O5-T03-U07-SUITE-R003` | candidate `4655db6...` | 695 pass / 1 expected skip / 228 warnings / 86 subtests | complete canonical suite passes in 649.22 seconds | `pass` | package |
| `P2O5-T03-U07-PACKAGE-R001` | candidate `4655db6...`; epoch `1785016562` | two 1,050,456-byte wheels / `eff2396b...`; 221 entries | byte-identical; safe unique paths; metadata/license/privacy pass | `pass` | isolated runtime |
| `P2O5-T03-U07-RUNTIME-V001` | first isolated metadata query | BurnLens 0.52.0 / 13 compatible distributions; zero commands tested | PowerShell newline corrupts roster query | `invalid-verification-retained` | delimiter-safe query |
| `P2O5-T03-U07-RUNTIME-R001` | isolated CPython 3.12.10 | BurnLens 0.52.0 from `site-packages`; 105 commands | dependency health and every help route pass | `pass` | PR/live verification |

The candidate is not released. Merge, fresh-main verification, and remote
annotated-tag peel remain required. Phase Three may not execute the U06
contract before those gates pass.
