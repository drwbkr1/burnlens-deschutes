from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from PIL import Image

import burnlens
from burnlens.label_review_browser_qa import (
    EXPECTED_EXPERIENCE,
    EXPECTED_LABEL_COUNTS,
    EXPECTED_REVIEWER_ID,
    LabelReviewBrowserQaError,
    _validate_observation,
    render_browser_qa_html,
    render_browser_qa_png,
)


ROOT = Path(__file__).resolve().parents[1]
PACKET_DIRECTORY = ROOT / "samples" / "labels" / "review" / "phase-two"
TEMPLATE_PATH = PACKET_DIRECTORY / "LABEL-REVIEW-PACKET-2026-001-RESPONSE-TEMPLATE.json"


def _sha256_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _response() -> dict:
    value = json.loads(TEMPLATE_PATH.read_text(encoding="utf-8"))
    value["reviewer"] = {
        "reviewer_id": EXPECTED_REVIEWER_ID,
        "independent_from_proposal_author": True,
        "burned_area_interpretation_experience": EXPECTED_EXPERIENCE,
        "proposal_seen_before_first_pass": False,
        "attestation": "Software browser fixture only; not a human response.",
    }
    value["review_started_at_utc"] = "2026-07-16T18:30:00Z"
    value["review_completed_at_utc"] = "2026-07-16T18:31:00Z"
    value["completed"] = True
    labels = ["burned", "background", "uncertain", "unusable"]
    sufficiency = ["sufficient", "limited", "insufficient"]
    confidence = ["high", "medium", "low"]
    for index, item in enumerate(value["responses"]):
        item.update(
            {
                "first_pass_label": labels[index % len(labels)],
                "evidence_sufficiency": sufficiency[index % len(sufficiency)],
                "confidence": confidence[index % len(confidence)],
                "reason_codes": ["low-severity-ambiguity"],
                "notes": None,
            }
        )
    return value


def _snapshot(width: int, height: int, *, progress: str = "0 of 56 units complete") -> dict:
    return {
        "title": "BurnLens offline label-review workbench",
        "ready_state": "complete",
        "unit_fieldsets": 56,
        "blind_images": 8,
        "loaded_blind_images": 8,
        "progress": progress,
        "review_summary": "No response review has been run.",
        "error_summary": "",
        "error_summary_visible": False,
        "invalid_cards": 0,
        "active_element_id": None,
        "viewport_width": width,
        "viewport_height": height,
        "document_width": width,
        "horizontal_overflow": False,
        "local_storage_entries": 0,
        "cookie": "",
    }


def _observation(
    *,
    draft_path: Path,
    response_path: Path,
    desktop_path: Path,
    mobile_path: Path,
) -> dict:
    initial = _snapshot(1440, 1000)
    invalid_review = _snapshot(1440, 1000)
    invalid_review.update(
        {
            "review_summary": "Review found 61 issue(s).",
            "error_summary": "Response cannot be finalized. 61 issue(s) remain.",
            "error_summary_visible": True,
            "invalid_cards": 56,
            "active_element_id": "error-summary",
        }
    )
    blocked = deepcopy(invalid_review)
    blocked["review_summary"] = "Export blocked until all issues are corrected."
    restored_snapshot = _snapshot(1440, 1000, progress="7 of 56 units complete")
    completed_review = _snapshot(1440, 1000, progress="56 of 56 units complete")
    completed_review["review_summary"] = (
        "All 56 units and attestations are complete. Label counts: "
        "background: 14 / burned: 14 / uncertain: 14 / unusable: 14. Confirm, then export."
    )
    return {
        "observation_schema_version": "burnlens-label-review-browser-observation-v0.1.0",
        "node_version": "v24.15.0",
        "browser": {
            "product": "Chrome/150.0.7871.124",
            "protocol_version": "1.3",
            "user_agent": "fixture",
            "javascript_version": "15.0",
        },
        "input": {
            "html_filename": "LABEL-REVIEW-HANDOFF-2026-001.html",
            "packet_id": "LABEL-REVIEW-PACKET-2026-001",
            "packet_run_id": "BL-2026-07-16-label-review-packet-r001",
        },
        "initial": initial,
        "invalid_state": {
            "review": invalid_review,
            "blocked_export": blocked,
            "response_file_created": False,
        },
        "draft_roundtrip": {
            "partial_progress": "7 of 56 units complete",
            "draft_filename": draft_path.name,
            "draft_bytes": draft_path.stat().st_size,
            "draft_sha256": _sha256_file(draft_path),
            "draft_completed": False,
            "draft_response_count": 56,
            "cleared": {"progress": "0 of 56 units complete", "reviewer_id": ""},
            "restored": {
                "snapshot": restored_snapshot,
                "reviewer_id": EXPECTED_REVIEWER_ID,
                "reviewer_experience": EXPECTED_EXPERIENCE,
                "first_label": "burned",
            },
        },
        "completed_roundtrip": {
            "progress_before_review": "56 of 56 units complete",
            "review": completed_review,
            "response_filename": response_path.name,
            "response_bytes": response_path.stat().st_size,
            "response_sha256": _sha256_file(response_path),
            "response_completed": True,
            "response_reviewer_id": EXPECTED_REVIEWER_ID,
            "response_count": 56,
            "label_counts": EXPECTED_LABEL_COUNTS,
        },
        "viewports": {
            "desktop": completed_review,
            "mobile": _snapshot(390, 844, progress="56 of 56 units complete"),
            "desktop_screenshot": {
                "filename": desktop_path.name,
                "bytes": desktop_path.stat().st_size,
                "sha256": _sha256_file(desktop_path),
            },
            "mobile_screenshot": {
                "filename": mobile_path.name,
                "bytes": mobile_path.stat().st_size,
                "sha256": _sha256_file(mobile_path),
            },
        },
        "runtime": {
            "console_error_count": 0,
            "runtime_exception_count": 0,
            "log_error_count": 0,
            "request_schemes": {"file": 9, "blob": 2},
            "external_request_schemes": {},
            "startup_message_count": 0,
        },
    }


class LabelReviewBrowserQaTests(unittest.TestCase):
    def test_current_package_version_and_packaged_controller(self) -> None:
        self.assertEqual(burnlens.__version__, "0.47.0")
        controller = ROOT / "burnlens" / "label_review_browser_controller.mjs"
        self.assertTrue(controller.is_file())
        text = controller.read_text(encoding="utf-8")
        self.assertNotIn("puppeteer", text.lower())
        self.assertNotIn("playwright", text.lower())
        self.assertIn('from "node:child_process"', text)

    def test_observation_validator_accepts_exact_browser_roundtrip(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            draft = _response()
            draft["completed"] = False
            draft["review_completed_at_utc"] = None
            draft_path = root / "draft.json"
            response_path = root / "response.json"
            draft_path.write_text(json.dumps(draft) + "\n", encoding="utf-8", newline="\n")
            response_path.write_text(
                json.dumps(_response()) + "\n",
                encoding="utf-8",
                newline="\n",
            )
            desktop_path = root / "desktop.png"
            mobile_path = root / "mobile.png"
            Image.new("RGB", (1440, 1000), "white").save(desktop_path)
            Image.new("RGB", (390, 844), "white").save(mobile_path)
            observation = _observation(
                draft_path=draft_path,
                response_path=response_path,
                desktop_path=desktop_path,
                mobile_path=mobile_path,
            )
            checks = _validate_observation(
                observation,
                draft_path=draft_path,
                response_path=response_path,
                desktop_path=desktop_path,
                mobile_path=mobile_path,
            )
            self.assertEqual(checks["completed_progress"], "56 of 56 units complete")
            self.assertEqual(checks["external_request_schemes"], {})

            tampered = deepcopy(observation)
            tampered["runtime"]["external_request_schemes"] = {"https": 1}
            with self.assertRaisesRegex(LabelReviewBrowserQaError, "external network"):
                _validate_observation(
                    tampered,
                    draft_path=draft_path,
                    response_path=response_path,
                    desktop_path=desktop_path,
                    mobile_path=mobile_path,
                )

    def test_rendered_browser_qa_is_semantic_and_visually_bounded(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            desktop = root / "desktop.png"
            mobile = root / "mobile.png"
            Image.new("RGB", (1440, 1000), "#fffdf8").save(desktop)
            Image.new("RGB", (390, 844), "#fffdf8").save(mobile)
            report = {
                "run_id": "BL-TEST-BROWSER-QA",
                "git_source_commit": "1" * 40,
                "software_version": "0.15.0",
                "application_version": "label-review-handoff-workbench-v0.1.0",
                "browser_runtime": {
                    "product": "Chrome/150.0.7871.124",
                    "browser_binary_sha256": "2" * 64,
                },
                "archive_binding": {"sha256": "3" * 64},
                "checks": {
                    "fixture_lock": {
                        "decision": "PASS_SOFTWARE_FIXTURE_CONTRACT_AND_HASH_LOCK_NO_REVEAL"
                    }
                },
                "screenshots": {
                    "desktop": {"path": "desktop.png", "viewport": "1440x1000"},
                    "mobile": {"path": "mobile.png", "viewport": "390x844"},
                },
                "decision": "PASS_LIVE_BROWSER_RESPONSE_ROUNDTRIP_NO_HUMAN_EVIDENCE_DEFER_DATASET",
                "decision_detail": "Software-only browser acceptance; human review remains absent.",
                "claims": {"not_proven": ["Independent human review is absent."]},
                "warning": "Experimental BurnLens CV evidence. Not official wildfire information.",
            }
            png = root / "qa.png"
            html = root / "qa.html"
            render_browser_qa_png(
                report,
                desktop_path=desktop,
                mobile_path=mobile,
                output_path=png,
            )
            render_browser_qa_html(report, output_path=html)
            with Image.open(png) as image:
                self.assertEqual(image.size, (1800, 1540))
            text = html.read_text(encoding="utf-8")
            self.assertIn("<main>", text)
            self.assertIn("Not human label evidence", text)
            self.assertIn(
                "Independent human responses / adjudications used in this QA:</strong> 0 / 0",
                text,
            )


if __name__ == "__main__":
    unittest.main()
