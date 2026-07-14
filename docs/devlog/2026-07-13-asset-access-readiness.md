# Devlog — Exact Asset-Access Readiness

**Date:** 2026-07-13

**Issue:** #312

**Branch:** `codex/p2o1-t02-asset-readiness`

## Weakness selected

BurnLens could enumerate candidate scenes and swaths, but it could not identify one reproducible source-asset route or explain what would have to be read, checked, aligned, excluded, and retained before any imagery or active-fire reference could enter the pipeline.

## Improvement made

This checkpoint resolves that ambiguity without downloading source data:

- the first post-report, low-cloud Sentinel-2 L2A scene is selected;
- its exact CDSE product UUID, SAFE identity, size, provider checksums, candidate band/quality assets, and credential boundary are recorded;
- the closest same-day NOAA-21 VIIRS swath is selected 46 minutes 40.976 seconds after the Sentinel acquisition;
- its exact active-fire and terrain-corrected geolocation granules, formats, stable access routes, revision dates, and missing provider-checksum behavior are recorded;
- the label-fitness review states what could become positive, unknown, exclusion, or review evidence after asset inspection.

## Reliability result

The NASA HTTPS routes currently answer no-secret HEAD requests with `303` redirects to transient signed CloudFront URLs. The signed targets were neither followed nor retained. The Sentinel product is discoverable without a credential, but CDSE documents that product download requires an authorization token and S3 access requires account-generated credentials.

The strongest reproducible Sentinel route is therefore the full 1,127,031,562-byte SAFE product through OData, followed by provider MD5/BLAKE3 verification and local SHA-256 registration. That route cannot proceed until the owner approves use of a CDSE account/token. NASA files can be tested later without adding a secret, but downloading them alone would not resolve the paired evidence weakness.

## Portfolio meaning

BurnLens now has an honest, inspectable acquisition contract instead of a vague data-source claim. It still has no source image, fire mask, label, dataset, baseline, model, run, map, or analytical output. The next checkpoint must acquire and visually inspect the exact pair or stop; it must not imply that metadata intersection proves a Darlene 3 detection.

## Shipment evidence

Issue #312 closed through PR #314. The pull request was squash-merged at `cf4aba2f40aa426f28f09b1b1b1bad895394198b`, and the annotated `v0.1.1-asset-readiness-baseline` tag was independently verified to dereference to that exact commit. The rendered merged F04-A and normalized fixture passed browser verification; the fixture still shows zero provider assets, zero retained provider bytes, no credentials, and no verified fire detection.

> Experimental BurnLens CV output. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
