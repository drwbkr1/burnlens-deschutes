from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile

from burnlens.petes_lake_reference_delivery import (
    PetesLakeReferenceDeliveryError,
    inspect_delivery,
    write_receipt,
)


class PetesLakeReferenceDeliveryTests(unittest.TestCase):
    def make_zip(self, root: Path, members: dict[str, bytes]) -> Path:
        path = root / "delivery.zip"
        with ZipFile(path, "w") as archive:
            for name, data in members.items():
                archive.writestr(name, data)
        return path

    def valid_members(self) -> dict[str, bytes]:
        token = "mtbs/2023/mtbs_OR4396912190120230825_10031414"
        return {
            f"{token}/mtbs_OR4396912190120230825_10031414_metadata.xml": b"metadata",
            f"{token}/mtbs_OR4396912190120230825_10031414_dnbr6.tif": b"raster",
        }

    def test_safe_exact_delivery_passes_without_raster_open(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            path = self.make_zip(root, self.valid_members())
            report = inspect_delivery([path])
            self.assertEqual(report["observed_map_ids"], [10031414])
            self.assertFalse(report["reference_pixels_opened"])
            self.assertEqual(
                report["archives"][0]["filename"],
                "petes-lake-mtbs-reference-delivery-001.zip",
            )
            self.assertFalse(report["archives"][0]["provider_filename_retained"])
            self.assertEqual(
                report["decision"], "PASS_SAFE_EXACT_PETES_LAKE_MTBS_DELIVERY_PREFLIGHT"
            )
            output = root / "receipt.json"
            write_receipt(report, output)
            self.assertTrue(output.is_file())
            with self.assertRaisesRegex(PetesLakeReferenceDeliveryError, "no overwrite"):
                write_receipt(report, output)

    def test_unsafe_nested_and_cross_program_members_fail_closed(self) -> None:
        for name, message in (
            ("../escape.txt", "unsafe"),
            ("nested.zip", "nested"),
            (
                "ravg/2023/ravg_OR4396912190120230825_10031414_metadata.xml",
                "cross-program",
            ),
        ):
            with TemporaryDirectory() as directory:
                root = Path(directory)
                members = self.valid_members()
                members[name] = b"bad"
                with self.assertRaisesRegex(PetesLakeReferenceDeliveryError, message):
                    inspect_delivery([self.make_zip(root, members)])

    def test_missing_or_extra_map_identity_fails_closed(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            members = {
                name.replace("10031414", "10099999"): data
                for name, data in self.valid_members().items()
            }
            with self.assertRaisesRegex(PetesLakeReferenceDeliveryError, "expected only"):
                inspect_delivery([self.make_zip(root, members)])
        with TemporaryDirectory() as directory:
            root = Path(directory)
            members = self.valid_members()
            members["mtbs/extra/mtbs_OTHER_10099999_metadata.xml"] = b"extra"
            with self.assertRaisesRegex(PetesLakeReferenceDeliveryError, "expected only"):
                inspect_delivery([self.make_zip(root, members)])


if __name__ == "__main__":
    unittest.main()
