# Cross-event source fitness: real bytes, visible exclusions

The 0.10 metadata checkpoint showed where independent events might come from, but not whether their pixels were usable. Issue #361 therefore stayed narrow: acquire only the four frozen Tepee/McKay products and make the real source limitations visible before any new label or dataset work.

That boundary paid off immediately. Four authenticated attempts failed closed on early EOF, transient metadata access, a route that ignored `Range`, and OneDrive hard-link races. BurnLens preserved bounded private failure states, changed no scene identity, and never weakened size, checksum, ZIP, SAFE, CRC, path, or atomic-registration gates. Run `BL-2026-07-16-cross-event-optical-intake-r005` finally registered all 4,551,170,756 bytes.

The source-fitness tool then opens exact native TCI/B04/B8A/B12/SCL members, transforms the complete frozen MTBS geometry to the native grid, and counts quality only where pixel centers fall inside that geometry. Registration uses independent spectral gradients with no shared mask. Context outside an irregular boundary may support correlation, but it never becomes quality or label evidence.

McKay is the clean result: 100% pair-eligible boundary pixels and three passing windows. Tepee is more useful precisely because it is not clean: 8.3441% review-needed, 5.1341% excluded, one excluded registration window, one review-needed window, and one pass. The rendered report keeps those states visible and binding.

A final local check found another real reliability edge. OneDrive aliases the small registration metadata manifest even while the four provider archives remain single-linked. BurnLens now rejects multiply linked manifests by default and permits only this cross-event metadata exception after one-read SHA-256 plus complete registration and asset comparison. The exception appears in JSON, HTML, and PNG instead of disappearing into local setup notes.

Fresh merged-main semantic readback then found a pre-tag trace mismatch: the manifest named implemented schema `burn-scar-five-state-schema-v0.1.0`, while the report's `label_schema_version` repeated the older design protocol. BurnLens withheld the tag, opened issue #363, added a frozen-input schema gate, and made protocol and schema separate public fields. Remediated source `cf1d9101e2760bf7d779b6fae68e605bb8809c1c` generated run `BL-2026-07-16-cross-event-source-fitness-r006`. All event pixels, metrics, windows, decisions, lineage fields, and input hashes remain identical to `r005`; the original-resolution PNG and live HTML now expose both identifiers.

Decision `ACCEPT_CROSS_EVENT_SOURCE_FITNESS_WITH_EXCLUSIONS` clears only the next cross-event five-state proposal/QA experiment. It creates no dataset, split, baseline, model, application, accuracy, generalization, independent human validation, or field claim.

> Experimental BurnLens CV evidence. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
