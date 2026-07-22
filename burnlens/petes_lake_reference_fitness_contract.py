"""Lightweight immutable contract for Petes Lake U05 reference fitness."""

from pathlib import Path


SOFTWARE_VERSION = "0.44.0"
REPORT_ID = "PETES-LAKE-REFERENCE-FITNESS-2026-001"
REPORT_VERSION = "petes-lake-reference-fitness-v0.1.0"
PROTOCOL_VERSION = "petes-lake-reference-fitness-protocol-v0.1.0"
UNIT_ID = "P2O4-T33-U05"
RUN_ID = "BL-2026-07-21-petes-lake-reference-fitness-r001"
PREVIEW_RUN_ID = "BL-2026-07-21-petes-lake-reference-fitness-preview-r001"
BRANCH = "codex/p2o4-t33-petes-lake-milestone"
TASK_ISSUE = 521
FINAL_DIRECTORY = Path("samples/cross-event/phase-two/petes-lake")
PREVIEW_DIRECTORY = Path(
    "downloads/phase-two/runs/P2O4-T33-U05/petes-lake-reference-fitness-preview-r001"
)
VISUAL_PENDING = "PENDING_ACTUAL_PETES_LAKE_REFERENCE_RENDER_REVIEW"
VISUAL_PASS = "PASS_ACTUAL_PETES_LAKE_REFERENCE_RENDER_REVIEW"
VISUAL_FAIL = "FAIL_ACTUAL_PETES_LAKE_REFERENCE_RENDER_REVIEW"
VISUAL_PASS_NOTE = (
    "PASS_ORIGINAL_RESOLUTION_U05_RENDER_LEGIBLE_CONSISTENT_UNCLIPPED_"
    "AND_WITHOUT_MISLEADING_DISPLAY_ARTIFACT"
)
VISUAL_FAIL_NOTE = (
    "FAIL_ORIGINAL_RESOLUTION_U05_RENDER_REVIEW_WITH_EXACT_FAILURE_"
    "RETAINED_IN_THE_ASSOCIATED_REVIEW_RECORD"
)


class PetesLakeReferenceFitnessError(RuntimeError):
    """Exact U05 reference fitness failed closed."""
