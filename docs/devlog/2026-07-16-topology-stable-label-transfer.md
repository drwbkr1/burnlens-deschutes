# When Correct Pixels Still Produce an Unstable Run

BurnLens began this cycle by rerunning the shipped cross-event workflow. The maps looked identical because they were identical: all four GeoTIFFs, both rendered PNGs, and both semantic HTML pages matched byte for byte. The proposal JSON did not.

The difference was not scientific. OneDrive had changed two small registered MTBS files from the exact-two-link topology observed at release to the single-link topology that the safety verifier also accepts. The public JSON serialized that current link count, so an approved storage transition changed the run hash even though every source byte, raster grid, raster value, proposed pixel, and QA result stayed fixed.

That is a reliability defect worth fixing before moving on. A reproducible run identity should change when evidence changes, not when a sync client changes an incidental filesystem alias.

BurnLens `0.12.1` keeps the strict runtime rule: the manifest and both clips may have one or exactly two links, and all other counts fail closed. Exact bytes, hashes, grids, transforms, and values are still reopened and checked. The public run now records the policy and stable content result without promoting the transient observed count into scientific provenance. The acquisition-time count remains preserved in the immutable registration record.

The strongest test used two real ignored copies of the same MTBS package. One had one link per file; the other had one external hard-link alias for the manifest and each clip. The full multi-gigabyte Sentinel/MTBS workflow produced ten byte-identical outputs under both topologies. A third link fails before publication.

The corrected evidence gets new `2026-002` and `r004` identities. The `2026-001` package is not rewritten. Its link-count trace remains useful history: it exposed the design mistake.

Nothing about the analytical result improved. The same 9,760 candidate pixels and 54,170 ignored pixels remain, and separate QA still reports zero mismatch across 63,930 pixels. Independent human review is still absent. The next substantive question remains whether the three-event proposal is fit for adjudication and eventual dataset candidacy.
