from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from burnlens.phase_five_assurance import (
    PhaseFiveAssuranceError,
    _claim_scan,
    _scan_rules,
    PRIVACY_RULES,
    SECRET_RULES,
    render_html,
)


ROOT = Path(__file__).resolve().parents[1]


class PhaseFiveAssuranceTests(unittest.TestCase):
    def test_release_package_has_no_secret_or_private_material(self) -> None:
        package = (
            ROOT
            / "samples/runs/phase-four/"
            "burnlens-ward-creek-rbr-run-v0.1.0"
        )
        payloads = []
        for path in package.rglob("*"):
            if not path.is_file():
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            payloads.append((path.relative_to(package).as_posix(), text))
        self.assertEqual(_scan_rules(payloads, SECRET_RULES), [])
        self.assertEqual(_scan_rules(payloads, PRIVACY_RULES), [])
        self.assertEqual(_claim_scan(payloads)["status"], "pass")

    def test_affirmative_model_acceptance_fails_claim_scan(self) -> None:
        payloads = [
            (
                "status.json",
                json.dumps({"boundaries": {"model_accepted": True}}),
            )
        ]
        with self.assertRaisesRegex(
            PhaseFiveAssuranceError, "unsupported public claim"
        ):
            _claim_scan(payloads)

    def test_secret_assignment_is_detected_without_returning_value(self) -> None:
        findings = _scan_rules(
            [("bad.json", '{"access_token": "abcdefghijklmnop"}')],
            SECRET_RULES,
        )
        self.assertEqual(
            findings,
            [{"path": "bad.json", "rule_id": "credential-assignment"}],
        )
        self.assertNotIn("abcdefghijklmnop", json.dumps(findings))

    def test_rendered_report_is_offline_and_preserves_boundary(self) -> None:
        report = {
            "run_id": "BL-2026-07-26-p5o1-t01-u04-assurance-r001",
            "git_source_commit": "a" * 40,
            "release_scope": {
                "archive": {"sha256": "b" * 64},
            },
            "checks": {
                "known_vulnerability_classification": {
                    "status": "pass-with-disclosed-medium-finding",
                    "classification": {
                        "ghsa_id": "GHSA-h35f-9h28-mq5c",
                        "cve_id": "CVE-2026-59890",
                        "severity": "medium",
                        "disposition": "bounded mitigation",
                    },
                },
                "performance": {
                    "status": "pass",
                    "budgets": {
                        "archive_bytes": {
                            "actual": 487893,
                            "maximum": 750000,
                        }
                    },
                    "basis": "bounded",
                },
            },
            "limitations": ["No vulnerability-free claim."],
        }
        html = render_html(report).decode("utf-8")
        self.assertIn("default-src 'none'", html)
        self.assertIn("did not outperform RBR", html)
        self.assertNotIn("<script", html)
        self.assertNotIn("https://", html)


if __name__ == "__main__":
    unittest.main()
