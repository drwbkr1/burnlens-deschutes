# BurnLens Phase Five known issues

This register belongs to the baseline-first candidate. It is not a claim of vulnerability-free, accessibility-certified, operational, official, field-validated, endorsed, or emergency-ready status.

## P5-U04-KI-001 — medium dependency advisory

The locked runtime contains setuptools 82.0.0. The U04 snapshot records GHSA-h35f-9h28-mq5c / CVE-2026-59890 as medium. The public candidate is ZIP-only, has no `MANIFEST.in`, uses ASCII/NFC paths, and distributes no sdist. Impact is bounded to the advisory's affected package-discovery path. Workaround: keep the public route ZIP-only and do not add an sdist or `MANIFEST.in`; re-audit before any future packaging change. No vulnerability-free claim is made.

## P5-U05-KI-001 — medium historical builder identity omission

The Phase Four release audit recorded its fixed epoch and wheel hash but omitted the setuptools 82.0.1 builder identity embedded in the historical wheel. The locked v0.54 runtime alone produces a semantically equivalent but byte-different wheel. Workaround: use CPython 3.12.10, setuptools 82.0.1, `SOURCE_DATE_EPOCH=1785094504`, and `PYTHONHASHSEED=0` when exact historical wheel reconstruction is required. U05 verified two exact 1,166,315-byte wheels at SHA-256 `ad3ae7c8...`.

## Retained limitations

- The naive clean clone lacks ignored custody required by five historical builder test files and two exact-custody assertions. The explicit portable roster passes 711 tests; the naive failure remains visible.
- The exact U03 owner review is an internal rendered interaction check, not independent accessibility certification or formal WCAG conformance.
- RBR remains the accepted method. WCP-002 remains visible false-positive-risk evidence. The trained U-Net remains rejected and did not outperform RBR.
- This candidate is local and offline. It creates no deployment, GitHub Release, access, ownership, public-sharing, or external submission change.
