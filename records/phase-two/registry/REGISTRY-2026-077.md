# REGISTRY-2026-077 - Ward Creek U05 final disposition

**Recorded:** 2026-07-24
**Issue:** #554
**Branch:** `codex/p2o4-t39-replacement-event`

| Unit | Run / commit | State | Evidence | Next dependency |
|---|---|---|---|---|
| `P2O4-T39-U04` | `BL-2026-07-24-ward-creek-background-evidence-r001` / `390231c...` | `pass` | PRECHECK-2026-080/081; 21,266 exact route pixels; exact replay and owner-confirmed render | U05 |
| `P2O4-T39-U05-PROPOSAL` | `BL-2026-07-24-ward-creek-region-proposal-r001` / `5cc266d...` | `pass` | PRECHECK-2026-082; one 14-pixel burned core and one 25-pixel background core; 66 excluded ring pixels; five files replay exactly | U06 |
| `P2O4-T39-U05-RENDER` | exact 5,059-byte HTML / `fc2ef47e...` | `pass` | desktop and narrow real-browser DOM, image, link, overflow, warning, request, and console checks | U06 |
| `P2O4-T39-U05-PACKAGE-A/B` | two ordinary 965,739-byte wheels | `fail-retained` | different wheel hashes; zero content differences; six distribution-metadata timestamp differences | fixed epoch |
| `P2O4-T39-U05-PACKAGE-C/D` | 965,739 bytes / `c9426e77...` | `pass` | byte-identical fixed-epoch wheels; 203 safe unique members; isolated 96-command runtime | U06 |
| `P2O4-T39-U06` | not started | `eligible` | every U05 source, scientific, uncertainty, leakage, replay, render, test, and package gate passes | exact blank owner batch |

The 14-pixel burned core is the nearest eligible intact component under the
frozen selector. It is disclosed rather than clipped, padded, merged, or
expanded. Owner review remains mandatory and yes would be necessary but not
sufficient for promotion.

No owner response, label, dataset, split, baseline, model, metric, inference
output, deployment, or external submission exists from U05.
