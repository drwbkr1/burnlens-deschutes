# LABEL_FITNESS-2026-002 - Real-File Decision

**Decision:** `DEFER - REAL SOURCE IS REFERENCE-READY, NOT LABEL-READY`

The provisional rules in `LABEL_FITNESS-2026-001` were exercised on the real files. Valid AOI fire records exist and the Sentinel crop is readable, so the primary active-fire target is not rejected. Direct label creation remains indefensible because the observations are at the far swath edge, three records are residual-bowtie, the source resolutions differ by more than an order of magnitude, the observations are offset in time, and no independently reviewed fine-resolution boundary exists.

No provider hotspot, buffered point, NIFC perimeter, SCL class, or absence of detection may be coerced into positive, negative, or background segmentation truth. Unknown and excluded areas remain unresolved until a versioned label schema and human-review protocol pass their own checkpoint.
