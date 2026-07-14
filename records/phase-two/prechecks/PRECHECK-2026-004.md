# PRECHECK-2026-004 - Final AOI Geometry, CRS, and Coverage Contract

**Issue:** #321

**Tool version:** BurnLens package `0.2.0`

**Report contract:** `aoi-evidence-v0.1.0`

## Source acceptance order

The tool must fail before derivation unless the input:

1. is a regular local file with exact SHA-256 `3d615d4be88f65806399e3733491ab0d95e16ac91ea86b5a00b3ead81ec17abe`;
2. parses as one GeoJSON FeatureCollection feature;
3. matches the exact Darlene 3 object, IRWIN, unique-fire, state/county, source, category, method, valid, and quarantine fields;
4. is a non-empty MultiPolygon whose rings are closed;
5. has a plausible coordinate count;
6. projects locally to the independent NIFC EPSG:32610 extent within 0.10 m.

## AOI derivation contract

- Source CRS: EPSG:4326.
- Analysis CRS: EPSG:32610, meters.
- Display/catalog CRS: EPSG:4326.
- Buffer: 2,000 m on each side of the projected source extent.
- Snap: outward to 1,000 m grid lines.
- Required extent: `[620000, 4831000, 632000, 4840000]`.
- Required complete source containment: true.
- Required Census Deschutes County containment: true.
- Required selected Sentinel/VIIRS metadata-footprint containment: true.

The tool implements the WGS 84 / UTM zone 10N Transverse Mercator parameters for EPSG:32610: longitude of origin -123 degrees, scale 0.9996, false easting 500,000 m, false northing 0 m, and WGS84 ellipsoid. The authoritative CRS identifier is https://www.opengis.net/def/crs/EPSG/0/32610.

## Actual result

All gates pass. Local projection differs from the NIFC projected reference extent by at most 0.000220 m. The final AOI fully contains the reference, is within Census `GEOID 41017`, and is covered by the selected source metadata footprints.

The earlier discovery envelope cannot contain the official reference. The final AOI truthfully supersedes it, reducing projected bounding area by 48.096% while extending 2,883.302 m farther east.

## Non-implications

Geometry, county, and catalog-footprint checks do not establish usable pixels, cloud/smoke conditions, fire presence, label alignment, ground truth, dataset readiness, model readiness, or operational fitness.
