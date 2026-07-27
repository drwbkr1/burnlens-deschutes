# BurnLens portfolio site

This directory is the repository-owned Codex Sites source for the BurnLens
0.56.0 baseline-first portfolio release. It belongs to
`drwbkr1/burnlens-deschutes`; the separate `burnlens-site` repository is never
used.

## Public narrative

The site presents the accepted RBR baseline and the bounded U-Net as a
reproducible but rejected diagnostic. It makes no model-superiority,
independent-ground-truth, field-validation, official, operational, emergency,
or agency-endorsement claim. Official sources govern.

## Evidence custody

`public/evidence/manifest.json` binds every published evidence copy to its
canonical tracked source by repository-relative path, byte count, and SHA-256.
These are exact copies, not re-created marketing images. Raw provider archives,
private owner responses, credentials, retrieval details, ignored custody paths,
and machine-local paths are excluded.

## Local verification

Requires Node.js 22.13 or newer.

```bash
npm ci
npm test
npm audit
```

`npm test` builds the Vinext application, renders the worker output, verifies
the public claims and privacy boundary, and compares every evidence copy with
its canonical source.

## Publication

The Sites project identity is stored in `.openai/hosting.json` after project
creation. Deployment must follow the controlling BurnLens goal and issue
#584: merge the exact source, push the exact Sites source state, package that
state, save a version, deploy the saved version, and validate the production
URL. Do not persist a Sites credential in the repository.
