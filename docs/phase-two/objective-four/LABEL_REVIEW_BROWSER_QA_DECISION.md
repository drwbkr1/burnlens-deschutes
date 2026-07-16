# Live-Browser Reviewer-Handoff QA Decision

## Decision

`ACCEPT_LIVE_BROWSER_REVIEWER_HANDOFF_QA_DEFER_DATASET`.

Issue #383 closes the principal verification gap left by BurnLens `0.14.0`: the exact isolated workbench had deterministic archive, semantic, JavaScript, and static-render evidence, but its invalid-state handling, draft roundtrip, completed response export, viewport behavior, and console state had not been exercised in a live browser.

BurnLens `0.15.0` launches an installed current Chrome runtime with a temporary isolated profile and a loopback-only DevTools control plane. It opens the exact extracted `file://` workbench from the byte-reconstructed 8,652,301-byte handoff archive and records the real page behavior. The authoritative run loads all eight blind images and 56 fieldsets, blocks incomplete review, downloads and reloads a seven-unit draft through the native file input, completes and exports all 56 responses, and validates and locks the export only as a software fixture.

The desktop 1440 by 1000 and mobile 390 by 844 viewports have no horizontal overflow. The inspected page target records no external resource request, console error, runtime exception, cookie, or local-storage entry. The loopback DevTools transport is disclosed separately and is not represented as application traffic.

## Evidence boundary

This checkpoint proves one dependency-free acceptance run of the exact workbench in Chrome `150.0.7871.124` under the recorded Windows and Node runtime. It does not prove:

- cross-browser certification or formal accessibility conformance;
- reviewer identity, expertise, independence, or scientific fitness;
- that the software fixture was produced by a human;
- label agreement, adjudication, accepted ground truth, accuracy, or field validation;
- a dataset, split, baseline, model, deployment, official status, endorsement, or operational readiness.

The fixture receipt is classified `software-browser-fixture`, records `qualifying_independent_human_response: false`, and prohibits reveal. It cannot count toward the independent-response gate.

## Fresh technical basis

The implementation was checked against current primary sources on 2026-07-16:

- [Chrome Headless mode](https://developer.chrome.com/docs/chromium/headless) for the installed browser execution path;
- [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/tot/) for page, runtime, network, file-input, download, and viewport instrumentation;
- [Node.js WebSocket](https://nodejs.org/api/globals.html#class-websocket) for the dependency-free controller transport.

These sources support the recorded mechanism. They do not expand the scientific or public-use claims.

## Traceability

- Issue: #383
- Branch: `codex/p2o4-t07-browser-acceptance`
- Base: `d8864e2c5b05061a49f87edc64adb95848400ac0`
- Software: BurnLens `0.15.0`
- Generator source: `74275a061fb4054a535cc8b660bebb0021999c54`
- Candidate browser artifacts: `97ddbaf71372e119428868a37d214c3327523514`
- Browser-QA run: `BL-2026-07-16-label-review-browser-qa-r001`
- Browser-QA report: `LABEL-REVIEW-BROWSER-QA-2026-001`
- Application: `label-review-handoff-workbench-v0.1.0`; local/offline, not deployed
- Archive: `LABEL-REVIEW-HANDOFF-2026-001.zip`; 8,652,301 bytes; SHA-256 `12f4cbe3d7903b2c404d5dfafbc141c35afa74e51c5d0b9a1816c65f82b8d8cc`
- Packet: `LABEL-REVIEW-PACKET-2026-001`; SHA-256 `77067063a769645af13886b6c87cc236a10e06199d091743908d63556e07637c`
- Label schema: `burn-scar-five-state-schema-v0.1.0`
- AOI: `aoi-darlene3-model-v0.2.0`
- Dataset / split / baseline / model: none
- Exact inventory: `MANIFEST-2026-017`

## Current project state and next gate

This browser-QA run used zero independent human responses and zero adjudications. Separately, one returned response has since been preserved and operator-locked under issue #384; it is not evidence for this run and its bounded public receipt must ship as its own checkpoint. Keep the proposal reveal unopened, obtain the required second qualifying response, and do not create a dataset partition before review and adjudication gates pass.

> Experimental BurnLens CV evidence. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
