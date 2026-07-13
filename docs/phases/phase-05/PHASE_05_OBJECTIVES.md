# BurnLens Deschutes — Phase Five Objectives

## Document role

This document expands the Phase Five objective summarized in `docs/roadmap/BURNLENS_BUILD_ROADMAP.md`.

It defines the release-candidate quality gate. Phase Five is hardening, not feature expansion.

## Phase name

**Reliability Engineering, Quality Assurance, Reproducibility, Security, and Release Control**

## Canonical objective summary

Harden the integrated workflow into a tested, reproducible, secure, accessible, performant, and reversible release candidate without expanding analytical scope.

## Current status

**Proposed — blocked.**

Phase Five depends on an accepted Phase Four run package, interface candidate, exact version chain, and explicit QA activation.

## Phase purpose

Phase Five tests the complete system:

```text
source records
→ preprocessing
→ model or baseline inference
→ raster and vector generation
→ spatial overlays
→ summary calculations
→ run package
→ interactive interface
→ public-facing documentation candidate
```

It must answer:

> Can BurnLens consistently reproduce its evidence, survive expected failures, protect its lineage, and present a dependable interface without exceeding its documented use boundaries?

New features are deferred unless necessary to fix a release-blocking reliability, accessibility, security, traceability, performance, or clarity defect.

## Position in the six-phase build

| Phase Four provides | Phase Five creates | Phase Six receives |
|---|---|---|
| Integrated workflow, accepted run candidate, artifacts, interface, run states, warnings | Automated tests, clean-room reproduction, integrity checks, accessibility/security/performance evidence, release/rollback controls | Frozen release candidate, verified demonstration run, approved public claims and caveats, known issues, rollback target |

## Required outcomes

Phase Five must produce:

1. an approved QA and release-control plan;
2. unit, integration, geospatial invariant, regression, component, and end-to-end tests;
3. small immutable fixtures for every run state and key defect;
4. required CI and protected merge-path evidence where configuration is authorized;
5. dependency and environment locks;
6. clean-room reconstruction evidence;
7. run-package and checksum integrity validation;
8. dependency, code, secret, and public-artifact security checks;
9. accessibility evidence across keyboard, color, text alternatives, zoom, and representative browsers;
10. analytical and web performance budgets;
11. deliberate failure-injection and safe recovery evidence;
12. release candidate, preview deployment, version audit, known-issues register, and rollback rehearsal;
13. an explicit Phase Six recommendation.

## Objective set

### Objective One — Define the QA and release standard

**Purpose:** Lock the accepted run, test environments, quality categories, defect severity, release states, required evidence, and Phase Six gate.

**Acceptance gate:** Every hardening activity has an issue, expected result, evidence-retention rule, and release-blocking condition, with remediation separated from new feature work.

### Objective Two — Build automated tests and regression evidence

**Purpose:** Verify analytical functions, geospatial invariants, run packages, interface behavior, and critical user journeys through layered tests.

**Required result:** Python unit/integration tests; representative fixtures; golden or tolerance-based regression evidence; web unit/component tests; end-to-end journeys; visible flaky-test policy.

**Acceptance gate:** Critical contracts and every run state have automated evidence; skipped and flaky checks remain visible and linked to issues.

### Objective Three — Establish CI and reproducibility controls

**Purpose:** Require proposed changes to prove they preserve the accepted workflow before reaching the default branch.

**Required result:** Fast and full PR checks; scheduled/manual reconstruction; branch rules when authorized; exact, tolerance-based, and semantic reproducibility definitions; locked Python/Node/geospatial environments; optional container SBOM and provenance.

**Acceptance gate:** The candidate can be reconstructed from documented inputs and the required checks produce retained evidence.

### Objective Four — Harden security and artifact integrity

**Purpose:** Reduce dependency, secret, deployment, parsing, asset, and information-exposure risks appropriate to the static-artifact architecture.

**Required result:** Dependency and code scanning; secret review; license review; bounded web security controls; checksum/path/schema validation; safe handling of corrupt or missing assets; unsupported-claims scan.

**Acceptance gate:** No exposed secret or unresolved release-blocking security/integrity issue remains, and public artifacts fail visibly rather than silently mislead.

### Objective Five — Validate accessibility, performance, resilience, and clarity

**Purpose:** Ensure a first-time viewer can understand and operate the demonstration across representative browsers, devices, networks, and interaction methods.

**Required result:** Keyboard and focus review; non-color communication; textual summary; browser/device matrix; analytical/web performance budgets; visual review; documented internal clarity walkthrough that is not represented as external validation.

**Acceptance gate:** Critical interface paths work within declared support and budgets, and degraded/failure states remain understandable.

### Objective Six — Freeze the release candidate and verify rollback

**Purpose:** Create one traceable pre-release candidate and prove it can be deployed, identified, audited, withdrawn, and restored.

**Required result:** Candidate version; exact commits and run; preview deployment; full version audit; release evidence package; known limitations; rollback target and rehearsal; Phase Six recommendation.

**Acceptance gate:** Candidate is accepted, accepted with caveats, accepted baseline-first, remediated, rolled back, or stopped through a reviewed decision.

## Defect severity

| Severity | Default effect |
|---|---|
| Critical | Blocks Phase Six. Includes wrong run identity, materially displaced CRS, hidden failed/degraded state, exposed secret, operational guidance, or no rollback. |
| High | Normally blocks Phase Six unless removed from release scope. Includes unreproducible summaries, broken lineage, inaccessible core controls, major browser failure, or no-detection implying safety. |
| Medium | May be accepted only in the known-issues register with a clear user impact and workaround. |
| Low | Cosmetic or nonessential improvement; may be deferred. |

## Completion evidence

Phase Five is complete only when:

- the release candidate is traceable to exact commits, run, model/baseline, dataset, label, AOI, source dates, configs, and checksums;
- mandatory checks pass or documented caveats are accepted by the human owner;
- a clean environment reconstructs the candidate within declared exact, tolerance, or semantic rules;
- failure injection proves missing/corrupt/mismatched assets remain visible;
- accessibility and browser evidence covers the declared support matrix;
- performance remains within approved budgets or limitations are visible;
- no unsupported operational, institutional, or field-validation claim remains;
- rollback succeeds and is documented;
- the Phase Six recommendation is reviewed and merged.

## Dependencies

- accepted Phase Four run package and interface candidate;
- immutable fixture assets and reproducibility inputs;
- authorized CI, repository setting, preview deployment, and scanning permissions where applicable;
- current security, licensing, claims, accessibility, and release controls;
- a known rollback target.

## Non-goals

Phase Five does not:

- retrain or retune the model;
- change dataset, labels, target, AOI, threshold, calibration, or summary logic;
- add new map layers, live feeds, uploads, or a second CV task;
- create the final portfolio case study;
- publish the production release, tag, or GitHub Release without Phase Six authorization;
- represent internal walkthroughs as practitioner or agency validation.

## Fixed boundaries

- Reliability evidence must cover the complete version chain.
- Failed and degraded states remain visible.
- Written workflow policy is not claimed as platform enforcement unless verified.
- Retries do not convert flaky tests into ordinary passes.
- Static artifacts and minimal services remain preferred to reduce attack surface.
- Accessibility needs map-independent information.
- Release readiness does not mean operational wildfire readiness.

## Known risks and assumptions

- Exact numerical reproducibility may vary across hardware and geospatial libraries.
- Map rendering and visual regression may vary by browser or basemap labels.
- CI fixtures can be too small to represent full analytical behavior.
- Dependency scanning may identify vulnerabilities with limited practical exposure but still require classification.
- Performance budgets may force artifact-format changes that affect lineage and require review.
- Preview and production deployments can drift if exact commits and assets are not recorded.
- Configured branch protection may not be available through current tooling; policy and enforcement must remain distinct.

## Authority delegated to Codex

After activation and within approved hardening scope, Codex may:

- add tests, fixtures, validation, error handling, documentation, and non-analytical performance fixes;
- classify defects using the approved severity model;
- propose removal of nonessential release scope to resolve blockers;
- run clean-room, browser, accessibility, integrity, and security checks;
- prepare and deploy an authorized preview candidate;
- recommend accept, caveated, baseline-first, remediate, rollback, or stop outcomes.

Codex must not change frozen analytical evidence, conceal failing tests, silently regenerate the canonical run, or promote production without approval.

## Changes requiring explicit approval

- modifying analytical results or frozen versions;
- changing required checks, severity definitions, support matrix, or performance budgets after results are known;
- configuring branch protection, secrets, scanners, deployment access, ownership, or permissions;
- adding paid infrastructure or services;
- accepting critical or high defects;
- promoting a release candidate or changing the rollback target;
- creating tags or GitHub Releases.

## Expected handoff to Phase Six

The handoff must provide:

- accepted release-candidate version and exact commits;
- canonical run and analytical lineage;
- preview deployment and rollback target;
- QA matrix and retained evidence;
- clean-room reconstruction result;
- security, accessibility, browser, and performance results;
- known issues and accepted defects;
- approved public claims, mandatory caveats, and prohibited language;
- licensing questions still blocking specific artifacts;
- explicit accepted, caveated, baseline-first, remediate, rollback, or stop outcome.

## Source basis

This document consolidates the supplied Phase Five objective plan and current BurnLens reproducibility, claims, release, repository, and use-boundary controls. Detailed hardening tasks remain issue-generated and evidence-responsive.
