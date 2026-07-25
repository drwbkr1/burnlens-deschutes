# PRECHECK-2026-076 — Ward Creek MTBS delivery custody

**Date:** 2026-07-24
**Unit / issue:** `P2O4-T39-U03` / #554
**Disposition:** `custody-pass-source-fitness-pending`
**Source commit:** `62bee5f577e358c6dbd891359923b6aae4cbb188`

## Exact delivery binding

The accepted request is run
`BL-2026-07-24-ward-creek-reference-request-r001`. Read-only Gmail
verification found one matching provider completion message from `usgs.gov`.
It binds event `OR4494912090120190812`, map `10016337`, and expiry text
`2026-08-23 15:23:21`. The recipient, message identity, and retrieval route
remain private and are not retained in repository evidence.

One bounded HTTPS GET captured one archive without redirect, retry,
substitution, or overwrite:

- run `BL-2026-07-24-ward-creek-reference-delivery-r001`;
- 4,385,952 bytes;
- SHA-256
  `d94dfb1609c882fdd26119b2be03cea486af1bbb85e4c9607f108f9455f61d18`;
- ignored path
  `downloads/phase-two/raw/ward-creek-mtbs-reference-v0.1.0/ward-creek-mtbs-reference-delivery-001.zip`.

The ZIP has 16 members, 13 files, 5,462,721 uncompressed bytes, safe unique
paths, no encryption, no links, and a passing full CRC check. Exact event and
map tokens are present.

## Terms-first notice inspection

Before any raster pixel opened, both exact XML notices were parsed:

| Notice | Bytes | SHA-256 |
|---|---:|---|
| FGDC metadata | 37,972 | `39ab440c70785d408e2a2299832064b861fcb7c7a6cbb0bb6f0b5068df85cb99` |
| ISO metadata | 53,161 | `fa6fa6fc897a73d5272b48bf906b3605775b3a89a093d42922cc14ff38a7ffb1` |

The FGDC access constraint is `None`. Use has no restriction beyond
reasonable and proper source acknowledgement. The distribution language
supplies no warranty. The ISO notice repeats acknowledgement and warns that
data may change, represented features may be geographically inaccurate, and
no fitness is supplied.

Those terms permit bounded acknowledged prototype evidence. They do not make
MTBS independent ground truth, field validation, official BurnLens output, or
an operational label.

## Gate

Custody and terms pass. Native source fitness remains pending. U03 may inspect
the exact boundary, rasters, class domain, grids, nodata, optical relationship,
and methods. No candidate, owner response, label, dataset, split, baseline, or
model advances from this precheck.
