# Label-Review Readiness Decision

## Decision

`ACCEPT_PROPOSAL_BLINDED_REVIEW_READINESS_DEFER_DATASET`.

Issue #375 creates a deterministic review instrument for the exact Darlene 3, Tepee, and McKay proposal evidence. It does not claim that an independent reviewer has completed the instrument.

`LABEL-REVIEW-PACKET-2026-001` reopens the six registered Sentinel archives and two registered MTBS clips, rebuilds the three committed proposals, and requires exact state/target agreement before sampling. It selects four units from every proposal state present in each event. The result is 56 units across 14 present event/state strata. McKay has no excluded proposal pixels; that structural absence is recorded instead of manufacturing an excluded example.

The first-pass pages show pre-event imagery, post-event imagery, fixed-display continuous dNBR, and NIFC or MTBS source context. They do not show the sample-specific BurnLens proposal state or binary target. A separate reveal page and blank response/adjudication templates enforce the intended order without claiming cryptographic blindness.

## Evidence boundary

The packet is a bounded coverage probe and review-readiness artifact. It is not:

- a probability sample or accuracy assessment;
- accepted ground truth;
- completed independent human review;
- inter-rater agreement or adjudication;
- field validation;
- a dataset, split, baseline, model, application, or operational result.

Codex authored the proposal and review tooling and therefore cannot count as a qualifying independent reviewer. Before adjudication, two independent reviewers must complete all units, attest that the reveal was not seen first, and preserve immutable response hashes. Any disagreement, uncertainty, unusable evidence, or insufficient evidence remains ignored unless a qualifying independent adjudicator resolves it.

## Research basis

The protocol was refreshed against current primary sources before implementation:

- [MTBS mapping methods](https://www.mtbs.gov/mapping-methods) documents multitemporal interpretation, scene-quality limitations, analyst subjectivity, and uncertainty.
- Padilla et al. (2017), [DOI 10.1016/j.rse.2017.06.041](https://doi.org/10.1016/j.rse.2017.06.041), supports predeclared stratification for burned-area reference sampling.
- Vanderhoof et al. (2017), [DOI 10.1016/j.rse.2017.06.025](https://doi.org/10.1016/j.rse.2017.06.025), independently developed three analyst references and found that two-of-three agreement reduced reference error in their study.
- Franquesa et al. (2022), [DOI 10.3390/rs14174354](https://doi.org/10.3390/rs14174354), shows that interpreter experience and low-severity ambiguity can materially affect burned-area reference data.

These sources inform the workflow. They do not make BurnLens's bounded packet a statistically representative validation study.

## Traceability

- Issue: #375
- Branch: `codex/p2o4-t05-label-review-readiness`
- Software: BurnLens `0.13.0`
- Generator/verifier source: `a11ae5123728d3823ba67d22d49250d4affb18f6`
- Candidate artifacts: `f15cc0608e2093daf0ca339c17145d50933cc743`
- Packet run: `BL-2026-07-16-label-review-packet-r001`
- QA run: `BL-2026-07-16-label-review-packet-qa-r001`
- Review protocol: `proposal-blinded-label-review-readiness-v0.1.0`
- Response schema: `burnlens-label-review-response-v0.1.0`
- Adjudication protocol: `burnlens-label-adjudication-v0.1.0`
- Label schema: `burn-scar-five-state-schema-v0.1.0`
- Dataset / split / baseline / model / application: none
- Exact inventory: `MANIFEST-2026-015`

## Next gate

Obtain qualifying independent responses without exposing the reveal first. Then evaluate response quality, disagreement, evidence sufficiency, and proposal concordance by event and class. Adjudicate unresolved units or keep them ignored. Do not create a dataset split or baseline until that evidence supports an explicit dataset-candidacy decision.

> Experimental BurnLens CV evidence. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
