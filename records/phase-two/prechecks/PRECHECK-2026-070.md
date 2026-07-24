# PRECHECK-2026-070 - exact submission-bundle QA

**Run:** `BL-2026-07-24-august6-submission-bundle-r002`

**Source:** `660f54f4e4786de57257ce12fb24fa31c282cf8d`

Production and ignored replay match exactly:

| Output | Bytes | SHA-256 |
|---|---:|---|
| ZIP | 784,940 | `3d50c6ec627e9b15c63fa84a034e60dddbcccbdd27f182af316a08de3bd13b53` |
| receipt JSON | 774 | `08b507a3adddb66a1b50838cbe23c3e13e6d6b9742d4d3fa274a4c7d282fddbf` |

The archive has 14 unique safe members. Its internal manifest is 3,358 bytes /
SHA-256
`661b9a794facea4b7121955eeca539262fc877fca359df9fb821fcbb98906d10`.
Two independent extractions contain the same 14 files, 970,227 uncompressed
bytes, relative paths, sizes, and hashes.

The extracted `START-HERE.html` passes actual Chrome QA:

- HTTP 200;
- 1440 by 1000 and 390 by 844 without horizontal overflow;
- one H1 plus header, navigation, main, and footer;
- both images load at 1600 and 1800 native pixels;
- all nine local destinations return HTTP 200;
- skip link and reviewer path lead keyboard order;
- narrow navigation collapses;
- zero console errors, request failures, or external requests.

The first browser launch failed because the plugin Playwright browser binary
was not installed. The retained correction uses the installed local Chrome.
One mobile inspection selector then assumed a class the page does not use; the
corrected structural selector changes no page or bundle bytes.

Initial production r001 also remains retained in ignored failure custody. It
exposed that five text members lacked explicit cross-platform LF checkout
contracts. Commit `660f54f...` adds those contracts and binds exact LF bytes.
Final r002 rebuilds, replays, extracts, validates, and renders from that
checkout-stable source.

The browser and loopback server were stopped. The first full candidate suite
then returned 557 passes, one skip, and 29 failures. Every failure was a stale
current-package `0.48.0` assertion after the intentional `0.49.0` bump; no
submission, scientific, custody, or render assertion failed. The bounded
current-version correction passes all 187 affected tests, with 21 existing
NumPy deprecation warnings and four subtests. The first two-minute affected
test invocation timed out without a reported failure; the retained rerun
completed in 182.72 seconds. U01-U05 pass. U06 release verification remains.
