# PRECHECK-2026-071 - final submission-recipient walkthrough

**Issue / run:** #548 /
`BL-2026-07-24-final-submission-readiness-r001`

**Base:** `origin/main@ca5a2cee130da0e918b061206998b096a302a6f7`

The exact tracked 784,940-byte v0.49 ZIP at SHA-256
`3d50c6ec627e9b15c63fa84a034e60dddbcccbdd27f182af316a08de3bd13b53`
is the immutable input. The exact 774-byte receipt remains
`08b507a3adddb66a1b50838cbe23c3e13e6d6b9742d4d3fa274a4c7d282fddbf`.

No-overwrite extraction produces 14 files / 968,739 uncompressed bytes.
`validate_bundle_archive` passes every safe-name, duplicate, roster, byte, and
SHA-256 check. `START-HERE.html`, `SUBMISSION-README.txt`, and the internal
manifest match their bound identities.

Actual in-app browser QA from the clean extraction passes:

- one H1 plus header, primary navigation, main, and footer;
- desktop and 390 by 844 layouts without horizontal overflow;
- both exact images at 1600 by 1100 and 1800 by 1240;
- the strongest-result link reaches the Windigo aggregate report;
- all nine non-fragment destinations return HTTP 200;
- null dataset, split, baseline, and model stages remain visible;
- the use warning and official-source precedence remain visible; and
- zero console warnings or errors.

The linked Windigo page states the Copernicus attribution and bounded
BAER/MTBS/RAVG roles. Automated text inspection finds no private user path,
email, secret assignment, credential, token, retrieval detail, JavaScript, or
start-page external URL.

Retained limitations:

- the loopback server observes one browser-generated `/favicon.ico` 404 after
  navigating to the linked Windigo page. Intended extracted-file use, content,
  navigation, and console behavior are unaffected;
- the in-app browser's synthetic Tab control leaves focus on BODY. The exact
  v0.49 installed-Chrome keyboard-order gate remains passed evidence; and
- Markdown depth links render as text in a plain browser.

These are non-material to the instructed extract-and-open handoff. Repacking
the verified ZIP would create more release risk than value. The candidate
decision is
`READY_FOR_OWNER_SUBMISSION_AS_OFFLINE_TECHNICAL_CASE_STUDY`, pending
records-only PR and exact-main verification.
