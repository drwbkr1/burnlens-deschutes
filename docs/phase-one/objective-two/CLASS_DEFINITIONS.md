# P1O2-T03 — Class Definitions

## Status

Phase 1 / Objective Two task artifact.

This document defines the class logic for the first BurnLens Deschutes segmentation task. It does not create labels, download imagery, define a train/validation/test split, train a model, or run inference.

## Applies to

Primary target selected in P1O2-T02:

**active-fire / hotspot-informed binary fire mask**

The future label schema should use a binary target for model training, while preserving a separate ambiguity pathway for pixels, regions, or source conflicts that should not be forced into either training class.

## Class structure

| Internal value | Class name | Training role | Meaning |
|---:|---|---|---|
| 1 | Positive / fire-relevant | Positive class | Region is reasonably associated with active-fire or hotspot-informed fire evidence under the documented label rule. |
| 0 | Negative / background | Negative class | Region is not associated with the selected fire-relevant class under the documented label rule. |
| 255 or null | Unknown / exclude / review needed | Excluded from training metrics unless explicitly handled later | Region is ambiguous, source-conflicted, obscured, stale, or otherwise not safe to force into positive or negative. |

The exact numeric encoding can be revised during Phase Two, but the logical separation must remain.

## Positive class definition

A future pixel or region may be labeled positive only when it is tied to documented fire-relevant evidence under the selected label rule.

Potential positive evidence may include:

- active-fire or thermal-anomaly reference evidence from public fire products
- hotspot-informed regions created by a documented buffer or rasterization process
- manually reviewed active-fire-relevant imagery regions
- other source-documented active-fire references approved in the Phase Two labeling guide

Positive labels must record source, source date, processing date, and method used to convert reference evidence into mask-like geometry.

## Negative/background class definition

A future pixel or region may be labeled negative/background when it is not associated with the selected positive class under the same label rule and does not require exclusion.

Likely negative/background examples include:

- vegetation not associated with the selected positive class
- bare ground or soil
- roads
- buildings and rooftops
- water
- non-fire bright surfaces
- non-fire warm or reflective surfaces
- clear background pixels outside a documented fire-relevant reference area

Negative labels must be selected carefully so the dataset does not become dominated by easy background pixels that hide poor performance near confusing areas.

## Unknown / exclude / review-needed definition

Ambiguous regions should be excluded or flagged for review instead of forced into positive or negative labels.

Examples include:

- cloud-covered areas
- smoke-obscured areas
- shadows that change interpretation
- geolocation mismatch between imagery and reference evidence
- stale imagery compared with reference data
- low-resolution or mixed pixels
- hotspot/reference evidence that does not align cleanly with imagery
- bright roofs, roads, bare ground, water glare, or industrial heat-like features that may confuse interpretation
- any conflict between BurnLens-derived interpretation and official/public source information

## Why ambiguity must be preserved

Forcing ambiguous regions into a binary class can make the future model look cleaner than the evidence supports. It can also hide label noise, inflate metrics, and create misleading portfolio claims.

BurnLens should prefer honest exclusions and documented uncertainty over artificial label certainty.

## Source-precedence rule

Official sources govern.

BurnLens-derived class labels, masks, polygons, maps, summaries, and reports are experimental portfolio artifacts. They must never override county, state, federal, fire-service, emergency-management, transportation, evacuation, hazard, or incident information.

## Boundary language for future labels

Future labels should be described as:

> Experimental BurnLens labels derived from public/open reference information and documented review rules for portfolio segmentation research.

Future labels should not be described as:

> Ground truth wildfire perimeters.

> Official active-fire boundaries.

> Emergency-ready detection labels.

> Field-validated fire observations.

## Phase Two implications

Phase Two must create a labeling guide that converts these definitions into concrete rules for:

- source selection
- reference-to-mask conversion
- buffer or rasterization assumptions
- ambiguity/exclusion encoding
- label quality notes
- train/validation/test split handling
- class imbalance handling
- manifest fields

## Acceptance checklist

- [x] Positive class is defined.
- [x] Negative/background class is defined.
- [x] Unknown/exclude/review-needed handling is defined.
- [x] Ambiguity is preserved instead of forced into binary labels.
- [x] Source-precedence and use-boundary language are included.
- [x] Phase boundary preserved: no labels, imagery download, dataset split, training, inference, or demo integration.
