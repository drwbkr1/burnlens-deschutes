# SOURCE_PRECEDENCE-2026-005 - STAC Identity vs OData Archive Bytes

## Decision

Use the frozen STAC item ID, CDSE UUID, and SAFE name together as scene-identity provenance. Use current CDSE OData `ContentLength`, MD5, BLAKE3, online state, attributes, and the documented `download.dataspace.copernicus.eu` `$value` route as the binding archive-byte contract for P2O4-T03.

## Reason

The official STAC `Product` assets use a `zipper.dataspace.copernicus.eu` route. The official OData product-download documentation uses a `download.dataspace.copernicus.eu` route. Current records preserve the same scene UUIDs and SAFE identities but expose route-specific byte sizes and checksums. BurnLens treats this as disclosed packaging-route divergence, not as evidence that one checksum can validate the other route.

The acquisition must stop if UUID, SAFE name, platform, tile, orbit, baseline, acquisition time, product type, online state, OData size, OData MD5, or OData BLAKE3 drifts. A STAC/OData archive-byte mismatch alone does not authorize changing the scene or weakening the OData contract.

## Non-implications

This precedence decision proves no delivery, archive fitness, local pixel quality, label truth, dataset readiness, or model value. It authorizes no route other than the four exact current OData product downloads.
