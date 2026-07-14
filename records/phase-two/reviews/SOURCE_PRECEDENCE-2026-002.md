# SOURCE_PRECEDENCE-2026-002 - Final AOI Evidence Review

## Authority order applied

1. Current official incident, emergency, evacuation, transportation, and public-safety information.
2. NIFC WFIGS source geometry and official Copernicus/NASA/Census provider metadata.
3. BurnLens's derived modeling AOI.
4. Future reviewed labels, baselines, models, maps, summaries, and portfolio interpretations.

## Finding

The rendered evidence uses orange for the cited NIFC final-perimeter reference and a separate green rectangle for the BurnLens modeling AOI. It states that no basemap, imagery, label, detection, or model output is present. The AOI does not overwrite or restyle the official geometry as a BurnLens result.

If the dynamic NIFC service later changes, `SOURCE-2026-007` and its checksum remain the exact evidence used here. A later run must record a new source snapshot or explicit comparison; it must not silently rewrite the committed source.

## Conflict rule

Current official sources always govern. If an official source conflicts with the frozen BurnLens AOI or later interpretation, BurnLens must correct, supersede, withdraw, or visibly mark the affected output stale. Versioning never raises BurnLens above official information.

> Experimental BurnLens CV output. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
