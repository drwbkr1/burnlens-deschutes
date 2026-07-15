# SOURCE_FITNESS-2026-002 - Exact optical-pair fitness

**Issue:** #343

**Decision:** `ACCEPT_EXACT_OPTICAL_PAIR_FOR_PROTOCOL_EVIDENCE`

The exact Sentinel-2A pre/post pair passes legal-use, identity, availability, provider checksum, local multihash, SAFE/ZIP/root/manifest/CRC, AOI coverage, CRS, native-grid, product-scaling, required-band, readability, pairwise quality, and original-resolution visual-review gates.

Pairwise AOI quality is 98.9137% eligible comparison, 0.7641% review-needed, and 0.3222% excluded. Both scenes have no AOI no-data, cloud, cirrus, or snow pixels under their recorded SCL arrays. This is strong source fitness for a protocol checkpoint.

The decision does not prove every pre pixel is unburned, every post change is fire-caused, subpixel content registration, a burn boundary, a label, severity, dataset readiness, or model readiness. The approximately ten-day interval permits vegetation, moisture, atmosphere, soil, and other change. SCL and continuous dNBR are evidence, not truth.

Raw provider bytes remain local and ignored. Public modified evidence requires `Contains modified Copernicus Sentinel data 2024` and the BurnLens warning/source-precedence language.
