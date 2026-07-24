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

The corrected complete suite passes 586 tests, one expected skip, 22 retained
NumPy deprecation warnings, and 86 subtests. Compilation passes, all 147
tracked JSON files parse, and all 758 tracked Markdown files have zero broken
local links.

Two separate exact Git ZIP archives of package-sensitive commit
`97ef6e2d11572fa721182cdce161714d50183dfa`, built under
`SOURCE_DATE_EPOCH=1784868552`, produce byte-identical 887,000-byte wheels at
SHA-256
`57b4cc8338926b583ef976d6bee698ecedf1be869944d6dee69ced78cda3da50`.
The wheel has 187 unique entries, zero forbidden paths, and 88 commands. An
ignored isolated Python 3.12.10 environment installs 13 compatible
distributions, resolves BurnLens 0.49.0 from its own `site-packages`, and
passes all 88 command help routes.

The first package-isolation attempt piped Git's binary TAR stream through
PowerShell, which corrupted the stream before build. Windows `tar` rejected
the header checksums. That failed attempt is retained and superseded by
file-based Git ZIP archives. The first ZIP package command exceeded its
two-minute shell window after finishing package C; package D then completed
normally and matches package C exactly.

Exact bundle replay r003 still matches final r002. Text-member inspection finds
no private path, personal email, secret assignment, credential, token, or
retrieval detail. Supporting URLs are public official-source cautions, public
STAC, and public GitHub trace records. `RELEASE-AUDIT-2026-003` is valid and
computes `blocked` only because PR, merge, fresh-main repetition, and remote
tag verification have not run.
