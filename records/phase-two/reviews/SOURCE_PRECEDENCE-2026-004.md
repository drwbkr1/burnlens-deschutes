# SOURCE_PRECEDENCE-2026-004 - Cross-Event Feasibility Source Roles

**Issue:** #357

## Authority and role order

1. Current official incident, emergency, evacuation, transportation, and public-safety sources.
2. Current exact official provider material: Census county geometry, MTBS occurrence/boundary/method metadata, and CDSE Sentinel catalogue/collection metadata.
3. The frozen BurnLens normalized source snapshot, deterministic eligibility assessment, whole-group contract, and rendered feasibility evidence.
4. Future acquired imagery, label evidence, dataset partitions, baselines, models, portfolio interpretation, and application output.

## Finding

The checkpoint keeps these roles separate. Census determines representative-point county membership only. MTBS supplies analyst-interpreted cross-fire event/boundary reference and method context, not burned-pixel truth. CDSE STAC supplies current product identity and availability metadata, not local pixel quality. BurnLens selects exact acquisition candidates and freezes leakage-control groups, but does not create a partition or raise its interpretation above provider evidence.

If a current official source revises an event, boundary, route, terms posture, or safety fact, BurnLens must visibly supersede, correct, withdraw, or mark affected evidence stale. A commit, version, run ID, or reproducible render does not make BurnLens official or operational.

> Experimental BurnLens CV evidence. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
