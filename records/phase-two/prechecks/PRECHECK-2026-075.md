# PRECHECK-2026-075 — Ward Creek MTBS request

**Date:** 2026-07-24
**Unit / issue:** `P2O4-T39-U03` / #554
**Disposition:** `request-accepted-delivery-pending`
**Source commit:** `21eff8dd85cbf795bef68e0f0113fe5272eb286e`

## Exact request gate

U03 begins only after U02 passes exact committed-custody verification. The
request code is tested and pushed before the queue transaction. Its clean-head
preflight binds the 16,317-byte U02 report at SHA-256
`a8d89779b7508b439fee6cb5bc99dd926a62c56ab58da181b0f1b40b1bcc1f2f`.

Fresh request-time WFS metadata returns exactly one standard MTBS row:

- event `OR4494912090120190812`;
- catalog `34073`;
- map `10016337`;
- incident `WARD CREEK 0769 RN`;
- ignition `2019-08-12`;
- 2,070 mapped acres;
- `nonstandard=false`.

The exact native-UTM payload requests map `10016337` and ten MTBS-applicable
families: metadata, pre/post reflectance, dNBR, RdNBR, burned-area boundary,
non-processing mask, KMZ, PDF, and six-class thematic severity. It explicitly
excludes all eight BAER/RAVG-only soil, basal-area, canopy-cover, and composite
burn-index families.

## Single accepted transaction

Run `BL-2026-07-24-ward-creek-reference-request-r001` begins at
`2026-07-24T20:22:15.169Z`. The recipient comes from local Git configuration,
exists only in one child-process environment variable, and is removed in
`finally`. It is neither printed nor retained.

The official queue returns exactly `{"success":true}`:

- 16 response bytes;
- SHA-256
  `c955e57777ec0d73639dca6748560d00aa5eb8e12f13ebb2ed9656add3908f97`;
- one POST only;
- no retry authorized or performed.

Ignored private request custody contains:

| File | Bytes | SHA-256 |
|---|---:|---|
| `metadata-response.json` | 426 | `b01e4cf75d82433488ae3b61c42be8d9a76295ba4f682d3670d0d9ec91c41c30` |
| `queue-attempt-started.json` | 496 | `981bcb8f0bc580ded9b29b0c24c65840d392ea0dfbfa7ff41ef8078bb6d6f27a` |
| `queue-response.json` | 16 | `c955e57777ec0d73639dca6748560d00aa5eb8e12f13ebb2ed9656add3908f97` |
| `request-prepared.json` | 3,225 | `de76a48ee6b41113e05e2bbe3148f3e82e941a7a73cdbc39c2b404fa2774a98d` |
| `request-receipt.json` | 3,433 | `5f2949fecbd8b8a79de0d573b4fb1c04705ff69e0683901c776251b0cf1c5d98` |

Tracked public report
`WARD-CREEK-REFERENCE-REQUEST-2026-001.json` is 3,413 bytes / SHA-256
`ad8f70ee3cbda8fcff77755486d0cb400a3a5b3c2bc09b99813e8a95abd3d54f`.
Privacy scans find no email address, credential, token, private retrieval route,
or signed URL.

## Pending gate

Queue acceptance is not delivery or source fitness. Provider archive bytes
remain zero. U03 may advance only after the exact completion message is found
read-only, its private HTTPS route is verified without substitution, exact
delivered bytes enter new ignored no-overwrite custody, and every notice,
identity, member, class, mask, CRS/grid, nodata, caution, and local-fitness gate
passes. No reference pixel, candidate, label, dataset, split, baseline, or
model advances.
