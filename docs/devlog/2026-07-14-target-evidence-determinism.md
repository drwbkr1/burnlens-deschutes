# Devlog - A Release Gate Must Survive Checkout

**Date:** 2026-07-14

**Issue / PR:** #339 / #340

## Failure caught before release

PR #338 merged the owner-approved burn-scar target decision at `68971e9709b886adf8575a58d32694aad42f038e`. The post-merge unit suite, compilation, and dependency checks passed. The real fixed-input reconstruction did not: JSON changed because the new MTBS source record had LF bytes during branch generation and CRLF bytes after checkout on `main`.

The failure did not change the MTBS query result, the owner decision, the HTML, or the PNG. It did prove that the report's raw text-file hash contract was too dependent on checkout behavior. BurnLens withheld the release tag.

## Bounded correction

Run `r001` remains committed as historical evidence. The remediation:

- normalizes structured JSON input hashes through universal-newline decoding and UTF-8/LF serialization;
- writes target JSON and HTML with explicit UTF-8/LF serialization;
- pins target JSON and HTML line endings through `.gitattributes`;
- tests that LF and CRLF forms of the same source record produce the same report;
- publishes corrected immutable run `TARGET-DECISION-2026-002` / `BL-2026-07-14-target-decision-r002`.

The corrected JSON, HTML, and PNG reproduce byte for byte. The 1600 by 1050 evidence card is visually clean. No scientific finding, target rule, label, dataset, baseline, model, application, or public analytical claim changed.

## Release rule

The release rule required `v0.6.0-burn-scar-target-baseline` to remain uncreated until the corrected run reconstructed after the remediation PR merged to `main`. That check passed on 2026-07-15: all three artifacts matched, and annotated tag object `0b4e0ff226be0d78b3b510b7786be0ca1c817887` now remotely peels to remediation merge `bcb71ebd01d3184f8de24318428309e61d33e54f`. The tag records the evidence; it did not substitute for the check.

> Experimental BurnLens CV evidence. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
