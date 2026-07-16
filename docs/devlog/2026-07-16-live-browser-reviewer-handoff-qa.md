# Proving the Offline Workbench in the Browser That Actually Runs It

BurnLens `0.14.0` shipped a careful offline reviewer handoff, but one awkward sentence remained in the evidence: interactive browser validation was unavailable. That meant the most human-facing behaviors—blocked incomplete export, draft download and reload, native file input, all-unit review, completed JSON export, responsive layout, and browser console state—were supported by code and semantic checks rather than a recorded real-browser run.

Issue #383 resolves that gap without introducing a browser automation dependency or pretending a software fixture is a reviewer. BurnLens `0.15.0` uses Node built-ins and the installed Chrome DevTools endpoint to launch a short-lived isolated browser profile, open the exact extracted `file://` workbench, drive its real controls, collect actual downloads, inspect page-target requests and errors, and capture desktop and mobile screenshots.

The authoritative run reconstructs the exact 8,652,301-byte archive, loads all eight blind images and 56 fieldsets, finds 61 visible incomplete-review errors, restores a seven-unit downloaded draft after clearing the form, and exports a complete 56-unit response. The exported labels are deliberately balanced software data—14 each burned, background, uncertain, and unusable—and the response lock identifies them as `software-browser-fixture`. That receipt prohibits reveal and cannot count as human evidence.

The 1440 by 1000 desktop view and 390 by 844 mobile view have no horizontal overflow. The inspected page target records no external resource scheme, console error, runtime exception, cookie, or local-storage entry. The loopback DevTools control plane is disclosed rather than hidden. The result is strong evidence that the reviewer surface works as shipped, not evidence that a reviewer is qualified or that BurnLens labels are scientifically correct.

One real returned response arrived after the browser run and has been preserved and operator-locked under issue #384. Its exact bytes remain ignored and private, its notes are not exposed here, and the reveal remains unopened. That evidence will ship separately so the browser fixture and returned-human evidence cannot be confused.

Candidate source is `74275a061fb4054a535cc8b660bebb0021999c54`; browser evidence is committed at `97ddbaf71372e119428868a37d214c3327523514`; exact inventory is `MANIFEST-2026-017`.

> Experimental BurnLens CV evidence. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
