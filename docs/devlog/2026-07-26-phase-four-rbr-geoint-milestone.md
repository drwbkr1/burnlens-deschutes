# Phase Four RBR-primary GEOINT milestone

## What shipped into the release candidate

BurnLens now has one internally consistent Ward Creek run from exact analytical
arrays through a local evidence application. RBR is the accepted analytical
method. The frozen U-Net is preserved as a visibly rejected diagnostic and is
excluded from every accepted measurement.

The milestone writes ten native-grid GeoTIFFs, 202 accepted-RBR polygons,
web-ready vectors, bounded official context, deterministic observations, and a
self-contained interface. The interface separates accepted RBR, rejected
U-Net, MTBS reference, roads, selected public facilities, and generalized BLM
context. It offers layer and opacity controls, patch focus, a textual
equivalent, exact lineage, warnings, and explicit run states.

## The important failure remains visible

WCP-001 contains 141.44 ha of accepted RBR, with 94.19% overlapping the exact
analyst-interpreted MTBS boundary. WCP-002 is an owner-approved background
patch yet contains 66.76 ha of accepted RBR and no MTBS overlap. BurnLens
shows that result as baseline false-positive-risk evidence rather than
discarding it.

The U-Net failure is equally explicit. It predicted every selected Phase Three
test core as burned and scored 0.299 event-class macro Dice against RBR 1.0.
The model is valid, trained, evaluated, and reproducible, but rejected. The
current project does not plan or implement a second experiment.

## Reliability evidence

Accepted package run `BL-2026-07-26-p4o1-t01-u07-package-r001` freezes 66
files / 1,795,388 bytes. The exact 487,893-byte ZIP has SHA-256
`91308a2ffe7095d89843edeb1634d6b1e972eb65bf1f67f38f1da0279102d84e`.
Both tracked forms validate. A clean detached checkout reproduces the ZIP
byte-identically, parses the structured evidence, and renders the packaged
interface at desktop and narrow widths without overflow, runtime errors, or
external requests.

The clean checkout cannot rerun legacy U03-U06 builders without ignored source
and provider custody. Their broad suite therefore retains 11 passes, one
failure, and 18 errors. BurnLens records that limitation instead of calling it
a pass. Portable package validation, repack, contract, compile, structured
parse, and real-render gates pass independently.

## Release and handoff boundary

BurnLens 0.54.0 is a candidate until issue #570 merges and fresh main repeats
the changed-risk gates. Phase Five receives the exact immutable package,
interface, run IDs, source and terms records, warnings, failure evidence, and
rollback posture. No GitHub Release, deployment, external submission, access
change, or public-sharing change is included.

Future recommendations are intentionally separate: more diverse independently
reviewed regions, stronger background coverage, calibration work, or model
architecture/loss changes require a separately governed experiment. They are
not Phase 3B and are not work in the current project.
