# SOURCE_PRECEDENCE-2026-001 — Review

## Order of authority

1. Current official incident, emergency, evacuation, transportation, and public-safety information.
2. Official provider metadata and source products from Copernicus, NASA/NOAA, Oregon, and the U.S. Census.
3. Future reviewed BurnLens labels and quality/exclusion masks.
4. Future BurnLens baselines and models.
5. Future BurnLens maps, summaries, reports, and portfolio interpretation.

## Checkpoint finding

The retained fixture preserves provider item, collection, concept, and granule identifiers. It does not overwrite official properties with BurnLens interpretations. The AOI is explicitly marked as a BurnLens discovery envelope, not an official perimeter. The OSFM report is used only to choose a historical time/location context.

## Conflict rule

If official source metadata changes, record the new access date and a new fixture or superseding record. Do not silently rewrite `METADATA-2026-001.json`. If an official incident source conflicts with a BurnLens interpretation, the official source governs and the BurnLens output must be corrected, withdrawn, or clearly marked stale.

## Required public wording

> Experimental BurnLens CV output. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.

## Result

Passed for metadata retention. No analytical or public-output release gate was evaluated.
