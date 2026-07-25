# PRECHECK-2026-079 — Ward Creek U03 closure

**Date:** 2026-07-24
**Unit / issue:** `P2O4-T39-U03` / #554
**Disposition:** `pass`
**Next dependency:** `P2O4-T39-U04`

## Exact accepted attempt

Run `BL-2026-07-24-ward-creek-reference-fitness-r003` binds report
`WARD-CREEK-REFERENCE-FITNESS-2026-002`, protocol
`ward-creek-reference-fitness-protocol-v0.1.1`, and scientific source commit
`b1614fe0260c46570366e6bbe22f74fd24cb7523`.

The public no-overwrite outputs are:

| File | Bytes | SHA-256 |
|---|---:|---|
| `WARD-CREEK-REFERENCE-FITNESS-2026-002.json` | 61,346 | `f31bc51c64dae60b5a419146f4183b960b8504044f79e7505018a630c47c466d` |
| `WARD-CREEK-REFERENCE-FITNESS-2026-002.png` | 385,352 | `7797c3846e0036f65f6adf4ff98bee8537708c01e6ac046e19ea2655c52ca44a` |
| `WARD-CREEK-REFERENCE-FITNESS-2026-002.html` | 3,227 | `a34b408e3f021303491997a0f1b620fb23bbfe474d712de976a13831c5e05703` |

An exact detached replay from the scientific source commit uses a deliberately
different extraction location. All three files reproduce byte-for-byte.
R003 contains no checkout-dependent extraction path.

## Scientific gates

- exact archive: 4,385,952 bytes / SHA-256
  `d94dfb1609c882fdd26119b2be03cea486af1bbb85e4c9607f108f9455f61d18`;
- embedded FGDC and ISO notices permit bounded acknowledged use while retaining
  update, location, no-warranty, and fitness cautions;
- event `OR4494912090120190812` and MTBS map `10016337` match the request,
  delivery, boundary, metadata, and optical pair;
- one valid native boundary and all five expected 30-meter EPSG:32610 rasters
  pass identity, grid, CRS, nodata, and class-domain checks;
- all 20,943 optical boundary pixels are eligible in both images;
- all nine local registration windows pass, with maximum residual
  0.0721 pixel / 1.442 meters;
- 19,700 native MTBS class-2/3 pixel centers are recorded on the optical grid
  using nearest-neighbor comparison without claiming resolution gain;
- no MTBS class is treated as affirmative background truth;
- dataset, split, baseline, model, and application versions remain null.

## Render and packaging gates

The owner confirmed that the exact r002 HTML renders correctly. R003 uses the
same layout and a byte-identical 385,352-byte PNG; only the report image name,
run ID, and source-commit text change in its HTML. This supplies an
evidence-backed render-equivalence gate for the accepted r003 output.

The first 946,174-byte wheel at scientific commit `b1614fe...` is retained as a
failed package attempt because a runtime-only install could not load the new
command's `--help` without `geopandas`. Wrapper-only remediation commit
`0006643894eb2a588172017614048f49326cd1ff` delays the optional import and
adds two regression tests. It changes no scientific output.

The remediated wheel is 946,331 bytes / SHA-256
`ca0cdf52da48ac0e04ded4b0561bb503ac41efd2d1c461b1b1df432c104e6103`.
A fresh CPython 3.12.10 runtime-only environment installs it, passes dependency
compatibility, verifies all six pinned runtime distributions, exercises all 94
installed command help paths, and confirms the new command exits 2 with exact
`geo-research` setup guidance when optional geospatial dependencies are absent.
Final repository verification at `0006643...` passes 623 tests, one expected
custody skip, 58 existing NumPy deprecation warnings, and 86 subtests.

## Retained failures and boundary

R001 remains the failed non-HEAD trace attempt. R002 remains the
checkout-dependent JSON reproducibility failure. The first r003 package remains
the lean-install help failure. None changed provider custody or scientific
facts.

U03 advances only exact Ward Creek reference fitness. U04 may establish
independent affirmative-background evidence. No candidate, owner response,
label, dataset, split, baseline, model, metric, inference output, deployment,
or external submission advances here.
