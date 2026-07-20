from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile

from burnlens.green_ridge_reference_delivery import (
    GreenRidgeReferenceDeliveryError,
    inspect_delivery,
    write_receipt,
)


class GreenRidgeReferenceDeliveryTests(unittest.TestCase):
    def make_zip(self, root: Path, members: dict[str, bytes]) -> Path:
        path = root / "delivery.zip"
        with ZipFile(path, "w") as archive:
            for name, data in members.items():
                archive.writestr(name, data)
        return path

    def valid_members(self) -> dict[str, bytes]:
        event = "OR4446712160520200817"
        return {
            f"baer/2020/baer_{event}_10015623/metadata.txt": b"baer",
            f"mtbs/2020/mtbs_{event}_10021333/metadata.txt": b"mtbs",
            f"ravg/2020/ravg_{event}_10016049/metadata.txt": b"ravg",
        }

    def test_safe_exact_delivery_passes_without_extraction(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            path = self.make_zip(root, self.valid_members())
            report = inspect_delivery([path])
            self.assertEqual(report["observed_map_ids"], [10015623, 10016049, 10021333])
            self.assertEqual(
                report["decision"], "PASS_SAFE_EXACT_GREEN_RIDGE_REFERENCE_DELIVERY_PREFLIGHT"
            )
            output = root / "receipt.json"
            write_receipt(report, output)
            self.assertTrue(output.is_file())
            with self.assertRaisesRegex(GreenRidgeReferenceDeliveryError, "no overwrite"):
                write_receipt(report, output)

    def test_traversal_and_nested_archive_fail_closed(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            members = self.valid_members()
            members["../escape.txt"] = b"bad"
            with self.assertRaisesRegex(GreenRidgeReferenceDeliveryError, "unsafe"):
                inspect_delivery([self.make_zip(root, members)])
        with TemporaryDirectory() as directory:
            root = Path(directory)
            members = self.valid_members()
            members["nested.zip"] = b"bad"
            with self.assertRaisesRegex(GreenRidgeReferenceDeliveryError, "nested"):
                inspect_delivery([self.make_zip(root, members)])

    def test_missing_identity_fails_closed(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            members = self.valid_members()
            members.pop(next(iter(members)))
            with self.assertRaisesRegex(GreenRidgeReferenceDeliveryError, "missing expected"):
                inspect_delivery([self.make_zip(root, members)])


if __name__ == "__main__":
    unittest.main()
