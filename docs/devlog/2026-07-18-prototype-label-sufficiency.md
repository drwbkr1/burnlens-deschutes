# Devlog - Prototype Label Sufficiency

This cycle began by rerunning the exact owner-response gate. Its 24 accepted prototype points exposed the next evidence-visible weakness: BurnLens had not proved that sparse decisions could support a segmentation dataset or independent split.

BurnLens `0.27.0` measures the reviewed points against all 189,541 candidate-domain pixels, their event/class geometry, natural proposal prevalence, source regimes, and every nonempty three-way event assignment. The points are spatially distinct, but four points per class/event are not masks. Three events permit only one event per train/validation/test role, and each event carries a different reference regime. The balanced, proposal-stratified review sample cannot estimate natural prevalence or provide independent evaluation.

The rendered report therefore blocks dataset, split, baseline, and model work. This is a portfolio-positive reliability result: the tool makes insufficient evidence visible and specifies the minimum remediation instead of manufacturing sample count by tiling.

All 227 tracked tests pass. Two clean-checkout fixed-epoch wheels are byte-identical at 422,069 bytes / SHA-256 `741eb378433c8240809fb9de144b4db6884a2612a335e2d26be71e376bfe41da`. An isolated install reports BurnLens `0.27.0`, 41 console entry points, 90 wheel entries, zero forbidden files, and healthy pinned dependencies.

PR #445 merged the analysis at `dbc24c57442d0c2564ce7ae4e4da17a2c966b910`, but the first fresh Windows checkout correctly failed release verification: HTML line-ending conversion expanded the tracked evidence from 3,770 to 3,780 bytes and invalidated its manifest hash. Issue #446 adds the missing LF checkout contract plus a regression test. A detached checkout of remediation source `faca91a` preserves the exact 3,770 bytes, passes 228 tests, and reconstructs all three outputs byte for byte. The analytical decision and private/public evidence content do not change.
