# Exact replay

From a BurnLens checkout with the locked geospatial profile:

```powershell
uv run --locked --extra model --extra geo-research burnlens-validate-phase-four-package --package-path samples/runs/phase-four/burnlens-ward-creek-rbr-run-v0.1.0
uv run --locked --extra model --extra geo-research burnlens-validate-phase-four-package --package-path portfolio/phase-four/BURNLENS-WARD-CREEK-RBR-RUN-2026-001.zip
```

Both commands must report `PACKAGE_VALIDATION_PASS`. The validator checks the manifest, checksum roster, safe archive structure, actual GeoTIFF/GeoPackage/GeoJSON products, interface boundaries, and accepted-versus-rejected analytical status.
