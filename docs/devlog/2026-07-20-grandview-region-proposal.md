# Devlog - Grandview Region Proposal

The cycle began by rerunning verified v0.41.0 from lifecycle-synchronized main. All three route outputs reproduced byte for byte and the highest-leverage weakness remained user-visible: 67,782 evidence pixels existed, but no bounded unit could be reviewed.

The implementation reuses the established intact-component selector rather than creating a parallel proposal system. It exposes the exact MTBS raster on the v0.41 context grid, keeps the existing background route unchanged, and applies fixed 0.05 dNBR bins, the 25-pixel target, deterministic coordinate hashing, and one-pixel unknown rings.

The actual rendered run proposes two 25-pixel cores. `GVP-001` is MTBS-backed burned evidence with 46 ring pixels and low but positive observed pre/post dNBR. `GVP-002` is affirmative background-route evidence with 52 ring pixels. RAVG modeled classes are not used. Both rasters retain the full 749 by 592 EPSG:32610 grid, domains 0/1/2, nodata 255, exact trace tags, and `label_created=false`.

The original-resolution PNG and semantic HTML show actual optical, dNBR, MTBS/background-route, core, ring, and limitation evidence. Full release verification is pending. Issue #511 owns a separate blank review surface; this checkpoint creates zero owner responses or labels.
