# SOURCE_FITNESS-2026-001 - Real Sentinel/VIIRS Package

**Decision:** `ACCEPT FOR SOURCE AND REFERENCE INSPECTION; DEFER LABELS AND DATASET`

## Evidence that passes

- The exact registered package independently re-verifies against the immutable contract and current file hashes.
- The Sentinel true-color and SCL assets open on the expected CRS, resolution, dimensions, and exact AOI grid.
- The VIIRS fire mask, QA array, and 65 sparse vectors are structurally consistent.
- Eight provider fire records fall inside the frozen AOI; six are nominal and two high confidence.
- The companion real geolocation arrays cover the AOI and contain no invalid coordinate pair under the implemented checks.
- The rendered HTML and PNG keep the reference perimeter, provider points, exclusions, warning, source precedence, and traceability visible.

## Evidence that prevents label promotion

- Three of eight AOI records carry the residual-bowtie flag and are excluded from the five-record non-bowtie count.
- The AOI records have 69.02-69.07 degree view zenith, and companion AOI pixels sit only seven columns from the eastern swath edge.
- The optical scene precedes the VIIRS swath by 46 minutes 40.976 seconds.
- The 375 m thermal-anomaly product cannot supply 10-20 m semantic-segmentation boundaries.
- The later NIFC final perimeter is incident-reference geometry, not contemporaneous pixel truth.
- SCL reports 9.0281% medium/high cloud but is a scene-classification aid rather than an infallible usability mask.

## Phase decision

Phase Two has crossed the access and raw-integrity uncertainty but has not crossed label or dataset readiness. The next checkpoint should test whether an alternate temporally relevant VIIRS observation offers materially better scan geometry and whether an explicit weak/reference-label protocol can preserve unknowns. It must not force the current pair into training truth.

> Experimental BurnLens CV evidence. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
