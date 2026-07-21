from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from burnlens.capture_petes_lake_replacement_post import (
    EXPECTED_IDS,
    PetesLakeReplacementError,
    SELECTED_NATIVE_ID,
    rank_candidates,
    write_report,
)


def item(identifier: str, sensing: str, cloud: float, snow: float) -> dict:
    return {
        "id": identifier,
        "datetime": sensing,
        "platform": "sentinel-2a",
        "grid_code": "MGRS-10TEP",
        "relative_orbit": 13,
        "processing_version": "05.10",
        "cloud_cover_percent": cloud,
        "snow_cover_percent": snow,
        "product_bytes": 1_000_000,
        "provider_checksum": "d50110" + "a" * 32,
        "product_filename": f"{identifier}.SAFE.zip",
    }


def roster() -> list[dict]:
    dates = (
        ("2023-08-30T18:59:21.024000Z", 9.96, 0.081708),
        ("2023-09-09T18:59:41.024000Z", 0.35, 0.028301),
        ("2023-09-19T19:00:51.024000Z", 0.24, 0.021692),
        ("2023-09-29T19:02:01.024000Z", 99.97, 0.000348),
        ("2023-10-09T19:03:01.024000Z", 99.32, 0.000036),
        ("2023-10-19T19:04:11.024000Z", 0.1, 0.564076),
    )
    return [item(identifier, *values) for identifier, values in zip(EXPECTED_IDS, dates)]


class PetesLakeReplacementPostTests(unittest.TestCase):
    def test_only_post_status_low_cloud_candidate_is_selected(self) -> None:
        ranked, selected = rank_candidates(roster())
        self.assertEqual(selected["id"], SELECTED_NATIVE_ID)
        self.assertEqual(selected["days_after_ignition"], 55)
        september_19 = ranked[2]
        self.assertIn(
            "INCIDENT_TIMING_PRECEDES_CONSERVATIVE_POST_STATUS_BOUNDARY",
            september_19["reason_codes"],
        )
        self.assertEqual(ranked[3]["reason_codes"], ["CATALOGUE_CLOUD_EXCEEDS_20_PERCENT"])

    def test_candidate_roster_drift_fails_closed(self) -> None:
        changed = roster()
        changed.pop()
        with self.assertRaisesRegex(PetesLakeReplacementError, "roster drifted"):
            rank_candidates(changed)

    def test_report_writer_is_exact_and_no_overwrite(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "report.json"
            output = write_report({"report_id": "fixture"}, path)
            self.assertEqual(output["bytes"], len(path.read_bytes()))
            self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["report_id"], "fixture")
            with self.assertRaisesRegex(RuntimeError, "already exists"):
                write_report({"report_id": "changed"}, path)


if __name__ == "__main__":
    unittest.main()
