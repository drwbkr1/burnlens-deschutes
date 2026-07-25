# PRECHECK-2026-082 - Ward Creek U05 two-class proposal

**Date:** 2026-07-24
**Unit / issue:** `P2O4-T39-U05` / #554
**Run:** `BL-2026-07-24-ward-creek-region-proposal-r001`
**Scientific source commit:** `5cc266da918862106ed225d52a0f2d809c132954`
**Disposition:** `pass`
**Next dependency:** U06 exact two-candidate owner review

## Inputs and unchanged gates

The run reopens the exact accepted U04 route and the exact P2O5-T02
sufficiency report. It recomputes the Ward Creek optical pair, MTBS evidence,
quality masks, nine registration windows, both proposal routes, and the
proposal-time leakage check from immutable custody.

The accepted background JSON is 27,905 bytes at SHA-256
`acf5b02c314b7dfdee94d8709323117f24e1966042818c37ef7431085813933c`.
The accepted six-event sufficiency JSON is 10,087 bytes at SHA-256
`a3fa779669143333fbc2b9b27fb35d210d0847283ef754c9e7f1f39a0c30908b`.
All inherited source, terms, custody, raster, CRS, nodata, class-domain,
quality, registration, uncertainty, privacy, and reproducibility gates pass.

## Deterministic proposal

The selector uses one intact eight-connected native 20 m component in a fixed
0.05 dNBR bin. It targets 25 pixels, then breaks equal-distance ties with a
SHA-256 binding over class, bin, and ordered native-grid coordinates. It never
clips, pads, merges, or expands a component to force the target.

The exact routes contain 686 burned pixels and 21,266 affirmative-background
pixels. They yield exactly:

| Candidate | Proposed class | Core | Unknown ring | Raster SHA-256 |
|---|---|---:|---:|---|
| `WCP-001` | burned | 14 pixels / 0.56 ha | 26 pixels | `a9b525cca8461fb9550988b045878cae41e17b9fa0c4d5db55de87ebeabdeccc` |
| `WCP-002` | background | 25 pixels / 1.00 ha | 40 pixels | `787bf4455104bbc5ac34b56f409db27b60417b96d5b551687e375bc302c6dfe3` |

`WCP-001` is 11 pixels below the target because it is the nearest eligible
intact burned component. Preserving that intact component is a required
scientific limitation, not a failed count gate. The two cores and rings do not
overlap. Ward Creek collides with no existing prototype event group or year.
No split assignment is created.

## Exact outputs and replay

Candidate, replay, and tracked runs use distinct output locations and reproduce
all five files byte-for-byte:

| Output | Bytes | SHA-256 |
|---|---:|---|
| HTML | 5,059 | `fc2ef47ee56acb0fea10fcf480f11568639ea2a3429d3544a589333f5293e6c6` |
| JSON | 8,433 | `06100de3df058b397f3a797069a2705eea3d7f79c71dfa333a11698331b13638` |
| PNG | 85,888 | `78ccc856def6e8b0551a553daa80e0ae2bf9f1736c90e4d938ab907dab292498` |
| WCP-001 TIFF | 3,253 | `a9b525cca8461fb9550988b045878cae41e17b9fa0c4d5db55de87ebeabdeccc` |
| WCP-002 TIFF | 3,267 | `787bf4455104bbc5ac34b56f409db27b60417b96d5b551687e375bc302c6dfe3` |

Both rasters are EPSG:32610 on the exact 20 m Ward Creek context grid with
nodata 255. Their domains contain only background 0, core 1, ring 2, and
nodata. The exact counts are `{0: 250637, 1: 14, 2: 26}` and
`{0: 250612, 1: 25, 2: 40}`.

The original-resolution PNG passes visual inspection. The exact tracked HTML
passes desktop 1280x720 and narrow 390x844 browser checks: both candidates,
both TIFF links, the warning, and the 1800x1040 image load; no page overflow,
external request, console warning, or console error occurs. The narrow table
uses its intended local overflow container.

## Tests and package evidence

Focused U04/U05 verification passes 12 tests. The locked runtime and
geo-research profiles pass with all 96 command help paths. The full suite
passes 635 tests, one expected custody skip, 58 existing NumPy deprecation
warnings, and 86 subtests.

Two ordinary 965,739-byte wheel attempts are retained as a package
reproducibility failure. Their SHA-256 values are
`713eacd1a4947506566b6e8587b5ecea12c03af20dad6ce06ecf8c5557a267ce`
and
`9d94a8685b50c25f3ecabbd9c2e22a14b4fb501fa37d8ef31ad669ae7c2f4908`.
Member content is identical; timestamps differ in six distribution-metadata
members.

The corrected fixed-epoch builds are each 965,739 bytes at SHA-256
`c9426e77393be91a32991e5997cc94153c3411bab430208d96485276b439d70d`.
The wheel has 203 unique members, one entry-point file, and no forbidden
repository, custody, credential, secret, or private path. A fresh isolated
CPython 3.12.10 installation passes dependency compatibility, pinned runtime
checks, and all 96 installed command help paths.

## Disposition and boundary

U05 passes. U06 may build one blank owner yes/no/uncertain batch bound to these
exact proposal and raster hashes.

The run creates two unreviewed proposals and 66 excluded ring pixels. It
creates zero owner responses and zero labels. No dataset, split, baseline,
model, metric, inference output, deployment, external submission, ground-truth
claim, independent-validation claim, field-validation claim, official claim,
or operational claim advances.
