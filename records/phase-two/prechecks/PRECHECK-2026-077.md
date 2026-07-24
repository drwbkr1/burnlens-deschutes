# PRECHECK-2026-077 — Ward Creek MTBS native source fitness

**Date:** 2026-07-24
**Unit / issue:** `P2O4-T39-U03` / #554
**Disposition:** `machine-pass-render-pending`
**Source commit:** `b5272bc28275b100fa142fee46fec5a2c97576f9`
**Run:** `BL-2026-07-24-ward-creek-reference-fitness-r002`

## Native source gates

The r002 command first requires the supplied source commit to equal the active
repository `HEAD`. It then rehashes the exact 4,385,952-byte MTBS archive,
rechecks its exact roster and safety, and reopens the two embedded notices.

The delivered boundary has one valid EPSG:32610 polygon. Its exact event, map,
incident, fire type, assessment type, acreage, ignition date, pre-image ID,
post-image ID, and analyst thresholds match the frozen Ward Creek source.

All five native rasters share one 324 by 347, 30-meter EPSG:32610 grid. Every
band is read. Native nodata, dtypes, transforms, bounds, continuous ranges,
and exact class counts are retained. The dNBR6 domain is:

| Class | Native pixels | Role |
|---:|---:|---|
| 0 | 103,122 | outside or nodata; never background truth |
| 1 | 460 | unburned-to-low or recovery ambiguity |
| 2 | 8,287 | low-severity reference evidence |
| 3 | 558 | moderate-severity reference evidence |
| 5 | 1 | increased-greenness reference evidence |

No high-severity class or non-processing-mask pixel is present. Absence is
recorded, not repaired or inferred.

## Optical relationship

The exact registered Sentinel pair rehashes successfully. The delivered MTBS
boundary creates 20,943 optical-grid pixel centers. All are pair-eligible.
All nine deterministic local registration windows pass, with a maximum
residual of 0.0721 pixels / 1.442 meters.

Nearest-neighbor comparison from native 30 meters to the verified 20-meter
optical grid claims no resolution gain:

- class 0: 389;
- class 1: 853;
- class 2: 18,440;
- class 3: 1,260;
- class 5: 1;
- classes 2-4 affirmative: 19,700;
- optical-valid affirmative: 19,700.

MTBS classes 2-4 may support a later burned-candidate proposal. No delivered
class is affirmative background truth.

## Exact outputs

| Output | Bytes | SHA-256 |
|---|---:|---|
| JSON | 62,022 | `835ae480d097c8e4de6a44f53d16bbd696caf9ff2a53e956af1152c9144282e0` |
| PNG | 385,352 | `7797c3846e0036f65f6adf4ff98bee8537708c01e6ac046e19ea2655c52ca44a` |
| HTML | 3,227 | `0ede181bf2b8d868ab45a87dd5e734047869f1254430ec8a707f9b1dca5dcfa3` |

The exact PNG passes visual inspection. Automated in-app navigation to the
local HTML is blocked by the browser URL policy. That block is retained and
not bypassed. U03 remains `machine-pass-render-pending` until the exact HTML
receives a real local desktop and narrow-viewport render confirmation.

## Decision boundary

No U04 work starts from machine evidence alone. No candidate, owner response,
label, dataset, split, baseline, model, metric, official status, endorsement,
operational readiness, or emergency suitability is created.
