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

## Claim boundary

The page presents verified technical-case-study evidence. It does not create or
claim independent ground truth, an accepted dataset, split, baseline, model,
accuracy, field validation, official status, endorsement, operational
readiness, or emergency suitability.

U05 passes. U06 release verification is the next dependency.
