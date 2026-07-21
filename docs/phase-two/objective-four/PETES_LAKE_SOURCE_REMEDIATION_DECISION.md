# Petes Lake Source Remediation Decision

## Decision

`SELECT_REPLACEMENT_POST_AUTHORIZE_CONTRACT_REVISION_ONLY`.

U03 r001 rejects the planned October 29 post because 78.0782% of the Petes Lake boundary is SCL snow/ice and zero of eight registration windows passes. Metadata-only run `BL-2026-07-21-petes-lake-replacement-post-selection-r001` therefore searches only the same event, Sentinel-2 L2A source regime, Sentinel-2A platform, MGRS-10TEP tile, relative orbit 13, processing baseline 05.10, and predeclared post-ignition window.

Six full-boundary candidates match. August 30, September 9, and September 19 are excluded before acquisition under a conservative September 23 incident-status boundary supported by official regional updates. September 29 and October 9 are excluded because catalogue cloud exceeds 99%, above the unchanged 20% gate. October 19 is the only remaining candidate.

Current OData identifies exact product UUID `31fa8699-175b-4fd7-91c3-dd727a1576f5`, SAFE `S2A_MSIL2A_20231019T190411_N0510_R013_T10TEP_20241107T024526.SAFE`, 1,195,226,823 bytes, MD5 `4cf05a073b4c67f5e92e052ed1eb32bc`, and BLAKE3 `1b28f566aee5619ea9a48c8dd042f209194a40989ba4b54cfe4e14904a0ad878`. STAC reports 0.10% cloud and 0.564076% snow tile-wide; the snow value remains an explicit unresolved local-fitness risk.

The run used public metadata only, no credential, and zero provider product/archive bytes. The selected product may enter an exact replacement contract and clean preflight only after this evidence is committed, pushed, and recorded on issue #521. Contract revision must retain exact-source, checksum, no-overwrite custody, terms, local SCL/CLD/SNW, registration, paired-quality, render, warning, and no-label gates. The existing planned post and r001 failure remain immutable.

U04 remains blocked. No local replacement pixel, source pass, reference, candidate, owner response, prototype label, sixth accepted event, dataset, split, baseline, model, official status, field validation, endorsement, operational readiness, or emergency-ready claim is created.

Primary evidence: [`PETES-LAKE-SOURCE-REMEDIATION-2026-001.json`](../../../samples/cross-event/phase-two/petes-lake/PETES-LAKE-SOURCE-REMEDIATION-2026-001.json).
