from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import Mock, patch

from shapely.geometry import Polygon, mapping

from burnlens.replacement_event_source_gate import (
    ASSESSMENT_ID,
    REPORT_ID,
    REQUIRED_CRITERIA,
    SELECTED_PRODUCTS,
    SOURCE_ID,
    UNIT_ID,
    ReplacementEventSourceGateError,
    _normalize_stac,
    _source_gate,
    _validate_odata,
    build_report,
    render_html,
    validate_source,
    validate_repository_trace,
    write_outputs,
)


ASSESSED = "2026-07-24T18:30:00Z"
COMMIT = "a" * 40


def _stac(role: str) -> dict:
    expected = SELECTED_PRODUCTS[role]
    return {
        "stac_id": expected["stac_id"],
        "provider_id": expected["provider_id"],
        "native_id": expected["native_id"],
        "datetime": expected["acquisition_utc"],
        "platform": "sentinel-2a",
        "grid_code": "MGRS-10TFQ",
        "relative_orbit_number": 13,
        "processor_version": "05.00",
        "product_type": "S2MSI2A",
        "cloud_cover_percent": expected["stac_cloud_cover_percent"],
        "geometry_type": "Polygon",
        "full_boundary_coverage": True,
    }


def _odata(role: str) -> dict:
    expected = SELECTED_PRODUCTS[role]
    return {
        "role": role,
        "provider_id": expected["provider_id"],
        "native_id": expected["native_id"],
        "size_bytes": expected["size_bytes"],
        "online": True,
        "acquisition_utc": expected["acquisition_utc"],
        "publication_utc": "2024-01-01T00:00:00Z",
        "s3_path": "/eodata/frozen",
        "md5": expected["md5"],
        "blake3": expected["blake3"],
        "platform": "A",
        "tile_id": "10TFQ",
        "relative_orbit_number": 13,
        "processor_version": "05.00",
        "product_type": "S2MSI2A",
        "cloud_cover_percent": expected["odata_cloud_cover_percent"],
    }


def _gate_source(source_id: str) -> dict:
    evidence = {criterion: [f"{criterion} evidence"] for criterion in REQUIRED_CRITERIA}
    notes = {criterion: f"{criterion} note" for criterion in REQUIRED_CRITERIA}
    return _source_gate(
        source_id=source_id,
        name=source_id,
        locator="https://example.invalid/official",
        evidence=evidence,
        notes=notes,
        observed_at=ASSESSED,
    )


def _valid_source() -> dict:
    products = [
        {
            "role": role,
            "provider_id": expected["provider_id"],
            "native_id": expected["native_id"],
            "size_bytes": expected["size_bytes"],
            "md5": expected["md5"],
            "blake3": expected["blake3"],
        }
        for role, expected in SELECTED_PRODUCTS.items()
    ]
    return {
        "source_id": SOURCE_ID,
        "schema_version": "0.1.0",
        "unit_id": UNIT_ID,
        "run_id": "BL-2026-07-24-p2o4-t39-u01-test",
        "accessed_at_utc": ASSESSED,
        "git_source_commit": COMMIT,
        "software_version": "0.50.0",
        "event": {
            "event_id": "OR4494912090120190812",
            "event_name": "WARD CREEK 0769 RN",
            "ignition_date": "2019-08-12",
            "catalog_id": 34073,
            "map_id": 10016337,
            "acres": 2070,
        },
        "boundary": {
            "geometry_type": "Polygon",
            "valid": True,
            "empty": False,
            "exterior_vertex_count": 3340,
            "bounds_wgs84": [-120.902079, 44.915764, -120.856115, 44.955295],
            "area_square_degrees": 0.0009553536724757831,
            "coverage_predicate": "shapely.geometry.shape(item.geometry).covers(boundary)",
        },
        "catalog_search": {
            "returned_item_count": 49,
            "selected_item_count": 2,
            "selected": {role: _stac(role) for role in SELECTED_PRODUCTS},
        },
        "odata": {role: _odata(role) for role in SELECTED_PRODUCTS},
        "receipts": {},
        "source_gate": {
            "contract_version": "source-gate/v1",
            "assessment_id": ASSESSMENT_ID,
            "assessed_at": ASSESSED,
            "intended_use": {
                "summary": "Exact Ward Creek optical acquisition.",
                "planned_actions": ["metadata review", "acquire exact pair"],
            },
            "sources": [_gate_source("mtbs"), _gate_source("sentinel")],
            "decision": {
                "status": "ready",
                "blocking_reasons": [],
                "live_verification_pending": [],
                "approved_actions": ["metadata review", "acquire exact pair"],
            },
            "write_boundary": {
                "permitted_without_further_authorization": ["metadata review"],
                "requires_explicit_authorization": ["different product"],
            },
            "provider_bytes_authorized": True,
            "authorized_provider_byte_scope": {"products": products},
        },
        "limitations": ["No source pixel is accepted."],
        "warning": "Experimental.",
    }


class ReplacementEventSourceGateTests(unittest.TestCase):
    def test_source_gate_evidence_is_machine_valid_shape(self) -> None:
        source = _gate_source("source")
        criteria = source["criteria"]
        self.assertEqual(tuple(item["id"] for item in criteria), REQUIRED_CRITERIA)
        for criterion in criteria:
            evidence = criterion["evidence"][0]
            self.assertIn(evidence["type"], {"static", "live"})
            self.assertTrue(evidence["locator"].startswith("https://"))
            self.assertTrue(evidence["note"])
            if criterion["requires_live"]:
                self.assertEqual(evidence["observed_at"], ASSESSED)

    def test_shapely_coverage_rejects_interior_hole(self) -> None:
        boundary = Polygon([(2, 2), (8, 2), (8, 8), (2, 8), (2, 2)])
        item = {
            "id": SELECTED_PRODUCTS["pre"]["stac_id"],
            "geometry": mapping(
                Polygon(
                    [(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)],
                    holes=[[(4, 4), (6, 4), (6, 6), (4, 6), (4, 4)]],
                )
            ),
            "properties": {},
        }
        with self.assertRaisesRegex(
            ReplacementEventSourceGateError, "STAC_FULL_BOUNDARY_COVERAGE_FAILED"
        ):
            _normalize_stac(item, boundary)

    def test_odata_identity_fails_closed(self) -> None:
        _validate_odata(_odata("pre"), role="pre")
        drift = _odata("pre")
        drift["size_bytes"] += 1
        with self.assertRaisesRegex(
            ReplacementEventSourceGateError, "ODATA_IDENTITY_DRIFT:pre:size_bytes"
        ):
            _validate_odata(drift, role="pre")

    def test_report_preserves_exact_scope_and_limits(self) -> None:
        source = _valid_source()
        validate_source(source)
        report = build_report(source)
        self.assertEqual(report["report_id"], REPORT_ID)
        self.assertEqual(report["provider_bytes_acquired"], 0)
        self.assertEqual(len(report["authorized_products"]), 2)
        html = render_html(report)
        self.assertIn('name="viewport"', html)
        self.assertIn("full Shapely polygon", html)
        self.assertIn("No source pixel", html)
        self.assertNotIn("<script", html.lower())

    def test_tampered_roster_and_overwrite_fail_closed(self) -> None:
        source = _valid_source()
        tampered = deepcopy(source)
        tampered["catalog_search"]["returned_item_count"] = 48
        with self.assertRaisesRegex(
            ReplacementEventSourceGateError, "STAC_SEARCH_COUNT_DRIFT"
        ):
            validate_source(tampered)
        with TemporaryDirectory() as directory:
            output = Path(directory)
            write_outputs(source=source, output_directory=output)
            with self.assertRaisesRegex(
                ReplacementEventSourceGateError, "OUTPUT_ALREADY_EXISTS"
            ):
                write_outputs(source=source, output_directory=output)

    def test_repository_trace_rejects_commit_or_relevant_drift(self) -> None:
        with patch(
            "burnlens.replacement_event_source_gate.subprocess.run",
            side_effect=[
                Mock(stdout=str(Path.cwd()) + "\n"),
                Mock(stdout="b" * 40 + "\n"),
                Mock(stdout=""),
            ],
        ):
            with self.assertRaisesRegex(
                ReplacementEventSourceGateError, "GIT_SOURCE_COMMIT_MISMATCH"
            ):
                validate_repository_trace(Path.cwd(), "a" * 40)
        with patch(
            "burnlens.replacement_event_source_gate.subprocess.run",
            side_effect=[
                Mock(stdout=str(Path.cwd()) + "\n"),
                Mock(stdout="a" * 40 + "\n"),
                Mock(stdout=" M burnlens/replacement_event_source_gate.py\n"),
            ],
        ):
            with self.assertRaisesRegex(
                ReplacementEventSourceGateError, "GIT_RELEVANT_WORKTREE_DIRTY"
            ):
                validate_repository_trace(Path.cwd(), "a" * 40)


if __name__ == "__main__":
    unittest.main()
