# Giving the Reviewer a Clean Room Instead of a JSON Chore

BurnLens `0.13.0` made independent review possible, but not comfortable or well-isolated. The reviewer still had to edit a long JSON response beside repository files that included the proposal reveal. That was a usability problem and a study-integrity problem hiding in plain sight.

Issue #379 keeps the scientific packet fixed and changes the handoff boundary. BurnLens now builds one deterministic offline ZIP containing only the blank response contract, eight blind pages, a safe README, and a self-contained workbench. The workbench presents all 56 units as labelled native form controls, explains the decision vocabulary, shows progress and errors, lets the reviewer save or reload a local draft, and exports the exact existing response schema. It has no network dependency and no proposal reveal.

The archive is intentionally boring: stored members, fixed order, fixed timestamps, fixed modes, one root, and an explicit allowlist. A separately implemented verifier checks those properties and the workbench's embedded response contract. The return path then validates the completed JSON and writes a deterministic SHA-256 receipt before reveal. It refuses overwrite and rejects proposal-bearing additions.

The distinction remains the point. BurnLens has improved the conditions for independent review, but no independent response has occurred. The complete-response fixture in the test suite is software evidence only. The browser interaction runtime was unavailable, so this checkpoint records served semantic checks and original-resolution renders without claiming an interactive browser pass.

Candidate source is `75102d79e6e184a1ecac941900fd74938cdaa972`; candidate artifacts are `0400b894bcbf3938eb9b4666162512dd4263e45f`; exact inventory is `MANIFEST-2026-016`. PR, merge, fresh-main, and tag gates remain pending.

> Experimental BurnLens CV evidence. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
