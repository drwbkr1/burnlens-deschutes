# Devlog - Change the Target Only After the Evidence

**Date:** 2026-07-14

**Decision issue / PR; remediation:** #337 / #338; #339

## Weakness selected

BurnLens had exhausted the most obvious active-fire improvement: it inspected every bounded NOAA-21 candidate and found a substantially better swath. The better swath still could not define 10-20 m labels. The highest-leverage weakness was no longer geometry; it was an unresolved target path that prevented honest progress.

## Owner decision and bounded improvement

The owner activated the established burn-scar binary-mask fallback. The checkpoint turns that choice into repository truth and a deterministic evidence surface. It does not jump ahead to label generation.

The new report keeps the original evidence visible: active-fire observations remain useful complementary thermal-anomaly references, but not label pixels. It also distinguishes burned, background-candidate, unknown, and excluded semantics before any implementation can erase ambiguity.

## What MTBS changed

MTBS initially looked like the strongest candidate exact reference because its mapped-fire packages can include pre/post imagery, burn indices, boundaries, severity, and non-processing masks. A current official-service check changed that expectation. The 2024 inventory returned 941 records but no Darlene match, and neither the 2024 nor all-years occurrence layer returned a feature inside the frozen AOI.

That negative result is useful. BurnLens can borrow method discipline and revisit MTBS later, but it cannot pretend an exact Darlene 3 product exists. The report also prevents a tempting scope expansion: six MTBS severity classes do not become a new multiclass target.

## Verification lesson

The first 1600 by 1050 render exposed an unsupported font glyph in a heading. The renderer was corrected, committed, and the public artifacts were regenerated against the corrected source commit. The final PNG is visually clean and all three outputs rebuild byte for byte.

The in-app browser refused the local file URL under its security policy. That is recorded as a limitation, not converted into a passing browser claim. Tests verify semantic HTML structure and the linked image contract; original-resolution visual QA covers the generated decision graphic.

Post-merge reconstruction found a subtler reliability defect before tagging. The newly committed MTBS JSON used LF during branch generation and CRLF after checkout on `main`, so its raw byte hash changed and `r001` no longer reproduced. BurnLens preserved `r001`, withheld the tag, and opened #339. Corrected run `r002` normalizes structured-input hashes to LF, explicitly writes target JSON/HTML as UTF-8/LF, and tests LF/CRLF equivalence. Its three artifacts rebuild byte for byte, and the corrected 1600 by 1050 card is visually clean.

## What remains

BurnLens still has no label, dataset, baseline, model, inference result, application, or deployment. The next evidence gate is concrete: choose one legally usable pre/post optical pair, inspect the real pixels, and define the burn-scar protocol—including unknown/excluded handling and leakage controls—before building labels.

> Experimental BurnLens CV evidence. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
