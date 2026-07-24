# PRECHECK-2026-068 - portfolio output and rendered QA

**Milestone / issue:** `BL-PORT-001 / P2O4-T36` / #540

**Source commit:** `7ffb8ce74350c34f60c36765e194a2aab29dbcd9`

**Run:** `BL-2026-07-24-portfolio-reviewer-experience-r002`

**Disposition:** `PASS_RENDER_AND_REPRODUCIBILITY_ADVANCE_TO_RELEASE_VERIFICATION`

## Exact outputs

| Output | Bytes | SHA-256 |
|---|---:|---|
| `portfolio/BURNLENS-PORTFOLIO-REVIEWER-EXPERIENCE-2026-001.json` | 5,675 | `cfab6176a9e5f1e9c4636e56658cf1ded9092825c3f55c7ebfb9968b2a68a078` |
| `portfolio/BURNLENS-PORTFOLIO-REVIEWER-EXPERIENCE-2026-001.html` | 14,602 | `e133a22978d73335c8a67fa39ae5ff48279b67ac6f71c615d95f62c021fda3ae` |

An independent ignored replay with the same timestamp, run ID, and source
commit matches both production outputs byte for byte.

## Real rendered application

The exact production HTML passes:

- 1440 by 1000 desktop rendering with no horizontal overflow;
- 390 by 844 narrow rendering with no horizontal overflow;
- one H1 plus header, navigation, main, and footer landmarks;
- a working skip link and reviewer-first keyboard order;
- both exact tracked preview images;
- all nine repository-local destinations with HTTP 200;
- zero browser-console errors or warnings; and
- zero external URL loads.

The owner opened the exact page and confirmed: `It renders correctly`.

The loopback server, browser session, and test port were stopped after QA.
No deployment, tracking, analytics, provider, credential, mailbox, upload,
private-custody, or public-sharing capability exists.

## Retained failures

Ignored `render-failed-r001` remains preserved because the first production
page caused one missing-favicon request. It contains a 14,570-byte HTML file at
SHA-256 `84a9072bc24bc84aed1596135bcaa277addf9b46cf12eebba2ceec2043c0d675`
and a 5,675-byte JSON file at SHA-256
`6cebc92c8cf410042a962c13abdc072fd45a2103195e4c17e4226e2a4e44683d`.

The first favicon-focused test then failed because the test validator treated
the inline `data:` favicon as a filesystem target. The corrected validator
accepts only that explicit inline asset and keeps all reviewer links local.

The first complete release-candidate suite then retained 553 passes, one
expected skip, 22 warnings, 86 subtests, and 28 failures. Every failure was the
same current-package contract: a historical test still expected BurnLens
0.47.0 after the intended 0.48.0 bump. No scientific, custody, rendered-output,
or pipeline assertion failed. The bounded correction updates only those
current-version assertions; the Windigo report's historical 0.47.0 identity
remains unchanged. The 28 affected files then pass 183 tests and four subtests.

The corrected complete suite passes 581 tests, one expected skip, 22 retained
NumPy deprecation warnings, and 86 subtests. Compilation passes, all 143
tracked JSON files parse, and all 751 tracked Markdown files have zero broken
local links.

Two exact Git archives of package-sensitive candidate
`f9acd72798bff588edd84aa7d4f03f9a3e90219d`, built under
`SOURCE_DATE_EPOCH=1784862338`, produce byte-identical 881,588-byte wheels at
SHA-256
`4966fd403f6207a4afd63c1fa68658091467e6744dfc332313ca72b2e9811c9b`.
The wheel contains 185 unique entries, zero forbidden paths, and 87 commands.

An ignored isolated Python 3.12.10 environment installs 13 compatible
distributions, resolves BurnLens 0.48.0 from its own `site-packages`, and
passes all 87 command help routes. The initial verification command used
`python -m pip` even though the minimal uv environment intentionally omits pip,
then imported from the repository working directory. The corrected check uses
`uv pip check` and runs outside the source tree; the installed package passes.

`RELEASE-AUDIT-2026-002` is valid and computes `blocked` only because PR,
merge, fresh-main repetition, and remote tag verification have not run.

## Claim boundary

The page presents verified technical-case-study evidence. It does not create or
claim independent ground truth, an accepted dataset, split, baseline, model,
accuracy, field validation, official status, endorsement, operational
readiness, or emergency suitability.

U05 passes. U06 release verification is the next dependency.
