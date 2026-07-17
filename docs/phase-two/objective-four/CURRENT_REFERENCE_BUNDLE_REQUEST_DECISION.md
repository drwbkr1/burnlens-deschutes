# P2O4-T12A Current Reference Bundle Request Decision

**Issue / PR / parent:** #421 / #422 / #416

**Run:** `BL-2026-07-17-current-reference-bundle-request-r001`

## Decision

`AWAIT_EXACT_OFFICIAL_BUNDLE_DELIVERY_DEFER_LABELS_DATASET_MODEL`.

The current official viewer route accepted one bounded request covering all seven frozen BAER/RAVG/MTBS catalog products and 18 applicable product families. BurnLens preserved the exact 16-byte response and full property-only WFS capture in ignored local storage, published their hashes, withheld recipient and retrieval details, and rendered a clear pending-delivery state.

This resolves the request-reproducibility weakness but not the scientific weakness. Zero archives were received. No bundle notice, structure, grid, mask, class domain, or pixel has been inspected.

## Why this sub-checkpoint exists

The official queue is asynchronous. Waiting for an external retrieval message should not erase the exact request or tempt a later reconstruction from memory. Issue #421 therefore preserves a verifiable accepted-request checkpoint while parent #416 remains open for delivery and source fitness.

## Provider cautions

Four current metadata cautions are now binding:

- Darlene RAVG has sparse/no-tree-cover reliability limits.
- Tepee RAVG is not directly applicable across substantial non-forest cover.
- McKay RAVG can overestimate open-canopy severity because the post-fire scene is early.
- Tepee BAER is a nonstandard legacy-path record requiring exact content inspection.

These limitations are evidence, not footnotes. They govern which pixels can later contribute to a label decision.

## State change

- Request accepted: yes
- Archives received: 0
- Labels promoted: 0
- Candidate counts: 6 burned, 0 background, 50 ignored
- Dataset/split/baseline/model: absent
- Reviewer two: waived and absent
- Inter-rater/consensus/adjudication claims: absent

The next action under #416 is to preserve exact delivered bytes, inspect terms and structure, and render cross-program pixel fitness. No guessed delivery URL or substitute product is acceptable.

## Verified release

Issue #421 / PR #422 merged at `1bbd3c6385f9a1c543a851a1a278e0ac976a2d57`. Annotated tag object `0407f90c855e0e4b62b37c14ae69c5a85cadcaf7` remotely peels to that merge as `v0.22.0-current-bundle-request-evidence`. Fresh merged-main release gates pass. Lifecycle sync issue #423 changes no analytical, delivery, label, or model state.
