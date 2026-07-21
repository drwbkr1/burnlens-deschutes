from __future__ import annotations

from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile

from burnlens.petes_lake_reference_native_contract import (
    ARCHIVE_SHA256,
    DIRECTORIES,
    EXPECTED_MEMBERS,
    EXPECTED_RASTER_BOUNDS,
    EXPECTED_RASTER_TRANSFORM,
    MTBS_CLASS_SEMANTICS,
    PetesLakeReferenceNativeContractError,
    _assert_exact_roster,
    _inspect_notices,
    _validate_raster_profile,
    inspect_native_archive,
    validate_trace_inputs,
    write_report,
)


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = (
    ROOT
    / "downloads/phase-two/raw/petes-lake-mtbs-reference-v0.1.0/"
    "petes-lake-mtbs-reference-delivery-001.zip"
)


def notice_archive(*, warning: bool = True) -> ZipFile:
    warning_text = "Fire severity could be misrepresented in wetland areas." if warning else ""
    fgdc = f"""<metadata><accconst>None</accconst><useconst>There are no restrictions on use, except for reasonable and proper acknowledgement of information sources.</useconst><datacred>Monitoring Trends in Burn Severity Project (U.S. Geological Survey and USDA Forest Service)</datacred><distliab>no warranty expressed or implied</distliab><comment>{warning_text}</comment></metadata>""".encode()
    iso = f"""<MD_Metadata><text>reasonable and proper acknowledgement make no expressed or implied warranty reserve the right to correct, update, modify, or replace OR4396912190120230825 {warning_text}</text></MD_Metadata>""".encode()
    buffer = BytesIO()
    with ZipFile(buffer, "w") as archive:
        archive.writestr(EXPECTED_MEMBERS["fgdc_metadata"], fgdc)
        archive.writestr(EXPECTED_MEMBERS["iso_metadata"], iso)
    buffer.seek(0)
    return ZipFile(buffer)


class PetesLakeReferenceNativeContractTests(unittest.TestCase):
    def test_exact_roster_rejects_missing_extra_and_duplicates(self) -> None:
        exact = list(DIRECTORIES) + list(EXPECTED_MEMBERS.values())
        _assert_exact_roster(exact)
        with self.assertRaisesRegex(PetesLakeReferenceNativeContractError, "roster drifted"):
            _assert_exact_roster(exact + ["mtbs/extra.txt"])
        with self.assertRaisesRegex(PetesLakeReferenceNativeContractError, "duplicate"):
            _assert_exact_roster(exact + [exact[-1]])

    def test_notice_gate_requires_exact_wetland_warning(self) -> None:
        with notice_archive() as archive:
            report = _inspect_notices(archive)
        self.assertTrue(report["intended_local_analysis_and_bounded_derived_evidence_permitted"])
        with notice_archive(warning=False) as archive, self.assertRaisesRegex(
            PetesLakeReferenceNativeContractError, "wetland warning"
        ):
            _inspect_notices(archive)

    def test_class_semantics_do_not_silently_create_background(self) -> None:
        self.assertIn("not_background_truth", MTBS_CLASS_SEMANTICS["0"])
        self.assertIn("ambiguous_not_background_truth", MTBS_CLASS_SEMANTICS["1"])
        self.assertEqual(MTBS_CLASS_SEMANTICS["6"], "nonprocessing_mask_excluded")

    def test_trace_inputs_fail_closed(self) -> None:
        validate_trace_inputs(
            generated_at_utc="2026-07-21T23:30:00.000Z",
            run_id="BL-2026-07-21-petes-lake-reference-native-contract-r001",
            git_source_commit="a" * 40,
        )
        with self.assertRaisesRegex(PetesLakeReferenceNativeContractError, "run ID drifted"):
            validate_trace_inputs(
                generated_at_utc="2026-07-21T23:30:00.000Z",
                run_id="wrong",
                git_source_commit="a" * 40,
            )
        with self.assertRaisesRegex(PetesLakeReferenceNativeContractError, "UTC Z"):
            validate_trace_inputs(
                generated_at_utc="2026-07-21T23:30:00",
                run_id="BL-2026-07-21-petes-lake-reference-native-contract-r001",
                git_source_commit="a" * 40,
            )
        with self.assertRaisesRegex(PetesLakeReferenceNativeContractError, "lowercase SHA-1"):
            validate_trace_inputs(
                generated_at_utc="2026-07-21T23:30:00.000Z",
                run_id="BL-2026-07-21-petes-lake-reference-native-contract-r001",
                git_source_commit="A" * 40,
            )

    def test_exact_raster_grid_fails_closed_on_consistent_shift(self) -> None:
        profile = {
            "driver": "GTiff",
            "width": 434,
            "height": 374,
            "crs": "EPSG:32610",
            "resolution_m": [30.0, 30.0],
            "transform": EXPECTED_RASTER_TRANSFORM.copy(),
            "bounds": EXPECTED_RASTER_BOUNDS.copy(),
            "mask_flags": [["nodata"]],
            "band_count": 1,
            "dtypes": ["int16"],
            "nodata_values": [-32768.0],
            "band_summaries": [{"native_value_domain": None}],
        }
        _validate_raster_profile("dnbr", profile)
        profile["transform"][2] += 30.0
        profile["bounds"][0] += 30.0
        profile["bounds"][2] += 30.0
        with self.assertRaisesRegex(PetesLakeReferenceNativeContractError, "grid drifted"):
            _validate_raster_profile("dnbr", profile)

    def test_report_write_preserves_stale_temp_and_never_overwrites(self) -> None:
        with TemporaryDirectory() as directory:
            output = Path(directory) / "report.json"
            stale = Path(directory) / ".report.json.tmp-stale"
            stale.write_bytes(b"retained failure")
            write_report({"decision": "test"}, output)
            self.assertEqual(stale.read_bytes(), b"retained failure")
            first = output.read_bytes()
            with self.assertRaisesRegex(PetesLakeReferenceNativeContractError, "no overwrite"):
                write_report({"decision": "different"}, output)
            self.assertEqual(output.read_bytes(), first)

    @unittest.skipUnless(ARCHIVE.is_file(), "requires ignored exact Petes Lake MTBS custody")
    def test_exact_local_archive_passes_terms_first_native_contract(self) -> None:
        report = inspect_native_archive(ARCHIVE)
        self.assertEqual(report["archive"]["sha256"], ARCHIVE_SHA256)
        self.assertTrue(report["notice_gate_completed_before_raster_open"])
        self.assertEqual(len(report["native_rasters"]), 5)
        self.assertEqual(len(report["member_manifest"]), 20)
        self.assertEqual(
            sum(item["is_directory"] for item in report["member_manifest"]),
            3,
        )
        self.assertEqual(report["native_grid_groups"], 1)
        self.assertEqual(
            report["native_rasters"][-1]["band_summaries"][0]["native_value_domain"],
            {"0": 147156, "1": 1524, "2": 3191, "3": 4371, "4": 5873, "6": 201},
        )
        self.assertEqual(report["semantic_boundaries"]["accepted_reference_pixels"], 0)


if __name__ == "__main__":
    unittest.main()
