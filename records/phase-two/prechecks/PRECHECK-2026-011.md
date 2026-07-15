# PRECHECK-2026-011 - Cross-Event Feasibility Before Source Acquisition

**Checked:** 2026-07-15 UTC

**Issue:** #357

**Decision:** `PROCEED_METADATA_FEASIBILITY_ONLY`

## Cycle-start evidence

The exact shipped BurnLens 0.9 proposal and separate verifier were rerun first from synchronized `main` at `67044a51701f0abb3e730d4540ea7cb488801ed8`. All eight proposal/QA artifacts reproduced byte for byte. The verifier's binding limitations remained visible: one event and one exact scene pair cannot support leakage-resistant split evidence; both implementations share one conceptual contract; the same Codex director authored them; and no independent human or field validation exists.

The highest-leverage weakness was therefore cross-event feasibility, not more one-event threshold work or premature tiling.

## Frozen metadata screen

- repository: `drwbkr1/burnlens-deschutes` only; the separate `burnlens-site` repository is prohibited;
- official MTBS occurrence/boundary layers 62/63, service version `11.5`;
- official Census TIGERweb Deschutes County geometry, GEOID `41017`, service version `11.5`;
- minimum year 2017, wildfire only, 1,000 through 30,000 acres;
- exact MTBS representative point inside the Census county polygon;
- non-overlap with the frozen Darlene AOI and between selected candidate boundaries;
- one Sentinel-2 L2A item must cover the full MTBS boundary;
- selected pre/post scenes must share platform, MGRS tile, relative orbit, and processing baseline;
- catalogue cloud metadata must be at most 20%; local pixel fitness remains unproved;
- prefer the initial post-fire window, then stable low-cloud/short-span ordering;
- select two candidate events and freeze event/scene/geography/time groups before any tiling.

## Allowed and prohibited work

Allowed: public metadata queries, normalized source capture, deterministic assessment, exact acquisition-candidate identities, whole-group contracts, source/terms/provenance records, and rendered feasibility evidence.

Prohibited: provider imagery download, raw package retention, label creation, a versioned dataset, train/validation/test assignment, patching, baseline construction, model work, application/deployment work, performance or generalization claims, and official/operational/emergency/field-validated/endorsed status.

## Decision routing

- two compatible non-overlapping candidates: `SELECT_CROSS_EVENT_ACQUISITION_CANDIDATES`;
- one: `REMEDIATE_CROSS_EVENT_FEASIBILITY`;
- none: `STOP_DATASET_PATH`.

The before-data and terms gates are resolved for the bounded metadata action. Any later exact source acquisition is a new data-touch checkpoint and must revalidate authenticated delivery and local source fitness without changing these frozen group identities silently.
