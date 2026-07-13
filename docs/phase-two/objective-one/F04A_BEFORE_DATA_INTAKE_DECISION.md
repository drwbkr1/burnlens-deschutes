# F04-A Before-Data Intake Decision

**Decision date:** 2026-07-13

**Issue:** #293

**Branch:** `codex/p2o1-t01-source-readiness`

**Repository base:** `a72e88234f4e4e8ebb3dcb5c1a4aab14e06a9103`

**Decision:** `PASS — METADATA DISCOVERY ONLY`

## Exact action reviewed

Run read-only, no-secret metadata discovery for a bounded Darlene 3 / La Pine research envelope and retain one normalized JSON fixture containing only provider identifiers, acquisition times, bounding boxes, cloud-cover metadata, product versions, query counts, and selected VIIRS granule identifiers.

This decision does **not** authorize imagery, raster, vector, NetCDF, HDF, SAFE, JP2, preview, fire-detection, perimeter, label, mask, model-input, or other source-asset download. It does not authorize preprocessing, labeling, baseline execution, model work, mapping, deployment, or publication of analytical output.

## Gate evidence

| Required evidence | Instantiated record | Result |
|---|---|---|
| Exact issue authorization | GitHub issue #293 | Passed for metadata-only discovery |
| Branch and PR scope | `codex/p2o1-t01-source-readiness`; PR pending | Passed for branch scope; PR evidence pending |
| AOI record and identifier | `records/phase-two/aoi/AOI-2026-001.md` | Passed for a discovery envelope; not a fire perimeter or final modeling AOI |
| Source records | `SOURCE-2026-001` through `SOURCE-2026-003` | Passed |
| Access method record | `records/phase-two/access/ACCESS-2026-001.md` | Passed; no credential used or recorded |
| Terms and licensing review | `records/phase-two/terms/TERMS-2026-001.md` | Passed for retained metadata; protected asset access remains deferred |
| Format and CRS precheck | `records/phase-two/prechecks/PRECHECK-2026-001.md` | Passed for JSON metadata and WGS 84 query geometry only |
| Provenance manifest | `records/phase-two/manifests/MANIFEST-2026-001.json` | Passed for the retained fixture |
| Artifact registry classification | `records/phase-two/registry/REGISTRY-2026-001.md` | Passed |
| Source-precedence review | `records/phase-two/reviews/SOURCE_PRECEDENCE-2026-001.md` | Passed |
| Use-boundary review | `records/phase-two/reviews/USE_BOUNDARY-2026-001.md` | Passed |
| Prompt/build log | `records/prompt-build-log/2026-07-13-p2o1-t01.md` | Required before PR review |
| Repository-truth update | Roadmap, phase status, version history, changelog, and devlog | Required before PR review |

## Why the gate passes narrowly

- The official Copernicus Data Space STAC catalog and Sentinel-2 L2A collection metadata were readable without authentication.
- The Sentinel collection links directly to the Sentinel Data Legal Notice, which permits access, reproduction, distribution, communication, adaptation, and modification subject to required attribution.
- NASA Common Metadata Repository collection and granule metadata were readable without authentication.
- NASA Earthdata states that NASA-led mission data are CC0 unless marked otherwise and asks users to acknowledge and cite the data.
- The retained fixture contains metadata only. It contains no provider asset bytes, signed URLs, tokens, cookies, credentials, or derived analytical result.

## Remaining blockers

F04-A remains **incomplete for every later asset or processing action**. A future issue must re-open the gate for one exact action and verify, at minimum:

1. the chosen Sentinel asset endpoint and its current authentication, quota, format, band, CRS, nodata, and checksum behavior;
2. the chosen NASA VIIRS asset path, Earthdata access requirement, companion geolocation product, format, and retention method;
3. whether FIRMS delivery adds value beyond the standard VIIRS product and, if so, an owner-approved secret path;
4. the final modeling AOI or a justified revision of the discovery envelope;
5. storage, checksums, immutable raw registration, and redistribution rules;
6. a separate issue-backed acquisition contract.

## Stop conditions carried forward

Stop before any later asset access if terms or source identity are unresolved; before any secret, paid service, or account is added; before treating active-fire detections as exact perimeters or pixel-perfect truth; and before shipping any output that cannot be verified.

> Experimental BurnLens CV output. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
