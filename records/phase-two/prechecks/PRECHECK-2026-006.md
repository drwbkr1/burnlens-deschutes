# PRECHECK-2026-006 - Authenticated Source Inspection

**Issue:** #329

**Tool version:** BurnLens package `0.4.0`

**Source package:** `darlene3-s2-viirs-pair-v0.1.0`

**Inspection run:** `BL-2026-07-14-source-inspection-r001`

## Gates exercised

1. Re-verify the promoted four-entry package against registration schema `0.2.0` and `paired-intake-contract-v0.4.0`.
2. Open the exact Sentinel SAFE ZIP; require valid archive paths, CRC, SAFE root, manifest, EPSG:32610, 10 m true-color, and 20 m SCL grids.
3. Require the frozen AOI to align exactly to both source grids and read the real `1,200 x 900` RGB and `600 x 450` SCL crops.
4. Open the exact VJ214IMG HDF5/NetCDF-4 asset; require expected full-mask shape, sparse-vector lengths, in-range indices, and sparse confidence equal to the indexed mask class.
5. Decode geolocation and residual-bowtie QA flags without hiding excluded records.
6. Open the exact companion VJ203MODLL HDF5 asset; require the real array shapes, valid coordinate ranges, and AOI coverage.
7. Compare AOI fire records to the retained NIFC final-perimeter reference only as incident context.
8. Render JSON, semantic HTML, and a source-evidence card with explicit use boundaries, attribution, versions, run ID, source commit, and label deferral.

## Result

The package passes source readability and reference-evidence gates. Direct label promotion fails by design. The AOI is at the far VIIRS scan edge, three of eight AOI fire records are residual-bowtie observations, and 375 m thermal-anomaly evidence cannot become 10-20 m segmentation truth.

Decision: `ACCEPT_SOURCE_REFERENCE_DEFER_LABELS`.
