# BurnLens maintenance, issue intake, archive, and supersession

## Current posture

BurnLens is a repository-owned, local, offline portfolio project. There is no
GitHub Release, deployment, production service, domain, public-sharing change,
support SLA, operational monitoring, or external submission.

The Phase Six candidate must remain reproducible and reviewable without
implying ongoing emergency or operational support.

## What is maintained

- repository code and locked dependency profiles;
- exact tracked evidence packages, manifests, checksums, and validators;
- the accepted RBR / rejected U-Net decision boundary;
- current reviewer guidance, claim matrix, source notices, and known issues;
- issue-backed correction paths for reproducibility, security, rights, privacy,
  accessibility, traceability, or material claim defects.

## What is not maintained

- live incident feeds, alerts, routing, closures, evacuation information, or
  incident-command support;
- hosted inference, uploads, user accounts, remote storage, or provider proxy
  access;
- public raw provider custody or private owner-review bytes;
- accuracy monitoring, field validation, adoption reporting, or operational
  availability;
- the separately governed follow-on model experiment.

## Issue intake

Use a repository issue only when the report can be public. A useful report
includes:

1. affected commit, version, run ID, or package hash;
2. exact local artifact and route;
3. expected and observed behavior;
4. reproduction steps and environment;
5. whether the concern affects rights, privacy, security, custody, claims,
   geospatial validity, accessibility, or reproducibility.

Do not paste credentials, private URLs, owner responses, ignored custody paths,
provider archives, personal data, or embargoed details into an issue. Handle a
potential secret or private-data exposure outside public issue content and stop
publication until it is resolved.

## Severity and response

| Class | Examples | Candidate action |
|---|---|---|
| Critical | Secret/private-data exposure, unsafe archive, rights violation, materially false public claim | Stop publication; preserve evidence; remediate before any release action. |
| High | Broken canonical route, invalid package identity, corrupted geospatial output, rollback failure | Block milestone exit; create bounded issue-backed remediation. |
| Medium | Bounded dependency advisory, historical builder identity, nonblocking accessibility defect with workaround | Keep visible with impact/workaround; fix when it materially improves the candidate. |
| Low | Editorial clarity, nonmaterial formatting, optional reviewer convenience | Batch only when it does not displace evidence or release QA. |

## Archive decision

For the pre-publication candidate:

- retain immutable Phase Four and Phase Five tracked packages unchanged;
- retain the Phase Six package created by U05 with its manifest and checksums;
- retain milestone records, known issues, release audit, tag/merge verification,
  and supersession notice;
- exclude raw provider archives, private owner responses, credentials,
  retrieval details, ignored custody, transient screenshots, browser profiles,
  temporary servers, and machine-local logs;
- do not create a GitHub Release or deployment during U04.

## Supersession

A later candidate may supersede presentation or packaging only through a new
issue-backed version with:

- explicit predecessor identity;
- reason for supersession;
- unchanged or explicitly revalidated analytical evidence;
- fresh rights, privacy, claim, render, package, and rollback gates;
- a durable notice that the earlier artifact remains historical evidence.

Never overwrite a versioned artifact or reuse its run ID. A corrected artifact
receives a new version or run ID and retains the failed/superseded attempt.

## End-of-project closeout

U07 may recommend `ready-for-owner-publication-gate`, `remediate`,
`narrower-baseline-first-outcome`, or `stop`. Only a later explicitly
authorized public action may create a GitHub Release, deployment, access or
sharing change, or external submission.
