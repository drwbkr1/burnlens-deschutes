# Devlog - A Clear Pair Is Still Not a Label

**Date:** 2026-07-15

**Issue:** #343

## Weakness selected

BurnLens had an accepted burn-scar target but no real pre/post optical proof. The highest-leverage next question was whether one exact pair could support an honest label protocol without turning continuous change or a later perimeter into manufactured truth.

## What changed

BurnLens froze a same-Sentinel-2A, same-tile, same-orbit, same-baseline pair around Darlene 3; refreshed current official metadata and terms; acquired both complete native SAFE archives through the protected CDSE boundary; and opened the real AOI TCI, B04, B8A, B12, and SCL pixels.

The real files exposed a metadata implementation bug before acceptance: the raster filename `B04` maps to physical band `B4` in product offset metadata. The corrected join has a regression test. The real render then showed a coherent change pattern near the later incident-reference outline, but the implementation keeps dNBR continuous and threshold-free.

## Reliability lesson

The provider and the filesystem each exercised a different retry path. One CDSE response ended early and left a valid range-resumable `.part`; the next server response ignored the Range header, so the client safely restarted instead of appending incompatible bytes. Separately, OneDrive twice created temporary upload-staging hard links. The multi-link guard rejected both registration attempts without weakening the contract.

The second rejection also exposed a CLI error-boundary gap: a generic promotion `ValueError` escaped without a normalized private state record. BurnLens added tested conversion to secret-free reason codes before retrying the unchanged complete pair.

## Evidence and meaning

The final pairwise AOI quality is 98.9137% eligible, 0.7641% review-needed, and 0.3222% excluded. Protocol `burn-scar-label-protocol-v0.1.0` keeps burned, background-candidate, unknown, excluded, and review-needed states separate and requires registration measurement, leakage-resistant grouping, boundary review, and independent QA.

This is meaningful Phase Two progress because a technical reviewer can inspect the exact real pixels and the proposed truth boundary. It is deliberately not a label checkpoint. No label array, dataset, split, baseline, model, metric, app, deployment, or operational result exists.

## Verification and shipment

The registered pair independently reverified after merge. All 86 repository tests, compilation, dependency health, byte-identical JSON/HTML/PNG reconstruction, original-resolution image review, real semantic-page browser review, wheel build and isolated import, secret/raw-byte exclusion, issue closure, and PR merge checks pass. PR #344 merged as `136d4d0919eba7144881c22163a149c89fee5a76`; annotated tag object `28d12fb5ef5c70054b8af5fd3c4847ba268000a1` remotely peels to that exact commit as `v0.7.0-optical-pair-protocol-baseline`.

Lifecycle issue #345 synchronizes the exact shipment identity. It changes no pixels, code, decision, or analytical status.

> Experimental BurnLens CV evidence. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
