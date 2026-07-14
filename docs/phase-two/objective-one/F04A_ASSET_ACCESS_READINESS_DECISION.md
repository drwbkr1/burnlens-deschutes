# F04-A Asset-Access Readiness Decision

**Decision date:** 2026-07-13

**Issue:** #312

**Branch:** `codex/p2o1-t02-asset-readiness`

**Repository base:** `49943d78016918ab65d2fa0eea9d0e653d905d6f`

**Decision:** `STOP — ROUTES VERIFIED; SOURCE-ASSET INTAKE NOT AUTHORIZED`

## Exact action reviewed

Use public catalog metadata and no-body HTTP checks to select one Sentinel-2 L2A scene and one same-day NOAA-21 VIIRS fire/geolocation pair, then document access, format, CRS/geolocation, quality, checksum, retention, terms, and potential label roles. Do not open, download, preview, process, or derive any provider asset.

## Gate evidence

| Required evidence | Record | Result |
|---|---|---|
| Issue and branch scope | Issue #312; `codex/p2o1-t02-asset-readiness` | Passed for readiness metadata only |
| Exact scene and reference selection | `ASSET_ROUTE_DECISION.md` | Passed |
| Source identities | `SOURCE-2026-004` through `SOURCE-2026-006` | Passed |
| Access behavior | `ACCESS-2026-002.md` | Passed for public metadata and HEAD checks |
| Terms and attribution | `TERMS-2026-002.md` | Resolved for research use; credential action remains gated |
| Format, CRS, geolocation, quality | `PRECHECK-2026-002.md` | Passed as a documented contract; pixel/file inspection remains blocked |
| Label fitness | `LABEL_FITNESS-2026-001.md` | Conditional reference/weak-evidence role only |
| Provenance fixture and manifest | `ASSET-READINESS-2026-001.json`; `MANIFEST-2026-002.json` | Passed; normalized JSON parses, manifest digest matches, provider asset count/bytes are zero |
| Use boundary and registry | `USE_BOUNDARY-2026-002.md`; `REGISTRY-2026-002.md` | Passed |

## Why this gate stops

The selected Sentinel product is public/open data, but both documented native download routes require an account-backed credential: an OData bearer token or S3 access/secret keys. The controlling goal requires owner approval before adding an account, token, or secret. No credential exists in this checkpoint.

The selected NASA files expose stable, no-secret HTTPS routes that currently return transient signed redirects, but their provider metadata supplies no file checksum. Downloading them alone would not provide the optical/reference pair, and the current issue explicitly stops before provider bytes.

## Exact future action that may be proposed

After owner approval for the CDSE credential boundary, a new issue may authorize one acquisition run that:

1. downloads the exact Sentinel SAFE archive through product UUID `58cebcf0-c417-4384-a93a-2d6b15344117`;
2. verifies provider MD5 and BLAKE3 before recording a local SHA-256;
3. downloads the exact `VJ214IMG` and matching `VJ203MODLL` files through their stable LP DAAC routes without retaining signed query strings;
4. computes local SHA-256 values because CMR exposes no provider checksum;
5. records immutable raw paths, byte sizes, tool versions, retry behavior, and a fresh access date;
6. inspects actual raster/HDF metadata and renders a bounded internal review before any label or preprocessing decision.

No action outside that exact contract is authorized by this readiness decision.

> Experimental BurnLens CV output. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
