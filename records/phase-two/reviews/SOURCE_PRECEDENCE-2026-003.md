# SOURCE_PRECEDENCE-2026-003 - Five-state proposal source-role review

**Issue:** #353

## Authority and role order

1. Current official incident, emergency, evacuation, transportation, and public-safety sources.
2. Exact official provider data and metadata: Copernicus Sentinel source/quality evidence and the NIFC WFIGS incident-reference snapshot.
3. BurnLens-derived spectral evidence, five-state proposal, target raster, and separate software QA.
4. Portfolio interpretation and future baseline/model output.

## Finding

The proposal keeps source roles separate. Sentinel supplies native-grid reflectance and SCL quality evidence. The later NIFC geometry supplies context and a review boundary, not pixel-perfect truth. VIIRS and MTBS assign no proposal pixel. dNBR and supporting changes are transparent proposal screens, not fire cause, perimeter, severity, accuracy, or field-validation evidence.

The rendered proposal and QA distinguish official inputs from BurnLens-derived states, retain the Copernicus attribution and NIFC-context caveat, and state that official sources govern. If a current official source conflicts with the frozen proposal, BurnLens must visibly supersede, correct, withdraw, or mark the affected output stale; versioning and software agreement do not raise BurnLens above the official record.

> Experimental BurnLens CV evidence. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
