# REGISTRY-2026-064 - BL-EXC-002 Windigo checkout-byte remediation

**Issue / branch / candidate:** #536 / `codex/bl-exc-002-windigo-byte-stability` / `e5743c723bfebfb13108458f8ace2e8e429517e1`

**Parent milestone / PR / failed merge:** P2O4-T35 / #535 / `00d01402657e92357f5f4c795ba9a4f4fd99038a`

**Decision:** `REMEDIATE_CHECKOUT_BYTES_WITHOUT_CHANGING_EVIDENCE`

## Failure retained

Fresh merged main rebuilt the correct 0.47 environment and passed 569 tests plus 86 subtests before the Windigo intake setup failed closed on `SOURCE-2026-036` byte drift. The full attempt ended with six exact-byte errors. The tag remained uncreated.

The cause is path coverage, not scientific or custody drift: Git stored the correct LF blobs, but the Windows checkout had no explicit LF rule for eight of the nine bound records or the nested final intake JSON/HTML.

## Candidate state

| Gate | Result |
|---|---|
| scope | pass: `.gitattributes`, one regression test, and release-truth records only |
| exact bound records | pass: nine of nine original sizes and SHA-256 values |
| exact final public output | pass: original JSON/HTML/PNG sizes and hashes |
| attribute regression | pass: all bound text paths resolve to `text=set`, `eol=lf`; PNG resolves to `text=unset` |
| focused replay | pass: eight tests |
| complete repository | pass: 577 tests, one expected skip, 22 warnings, 86 subtests |
| package | pass: two exact-candidate 872,766-byte wheels reproduce SHA-256 `1fabf5408113dcd238871070a3fbe0105526a845c66eb8f0f48edcb99595aea7` |
| exception PR / corrected main / tag | pass: PR #537 merges at `6a80ba14d060702d97c5d39f40cf3d6f8122ccc8`; corrected main passes 8 focused and 577 full tests with one expected skip and 86 subtests; tag object `31cf93a13b8d7d7f2f4a4730cffe5960d7469cb5` peels exactly to the merge |

The first candidate focused run exposed the missing nested output rule. The second exposed path-separator quoting in the new test. Both remain part of the failure chain.

The corrected-main packaging chain also retains two non-product attempts. The first used invalid PowerShell `git archive` argument syntax and produced no archive or wheel. The second correctly archived the source but the lean runtime refused a no-isolation build because it intentionally excludes setuptools. Accepted `r003` uses the declared isolated build system and produces two byte-identical canonical wheels. Its fresh isolated installation resolves only from `site-packages`, reports version 0.47.0, and passes 86 command help routes.

## Scientific and public boundary

`owner-approved-prototype-region-labels-v0.4.0`, its 12 balanced regions, 286 core pixels / 11.44 ha, 533 excluded ring pixels, and six event groups do not change. Dataset, split, baseline, and model remain null.

No ground truth, independent review, accuracy, field validation, official status, endorsement, emergency suitability, operational readiness, GitHub Release, deployment, or public-sharing change is created.
