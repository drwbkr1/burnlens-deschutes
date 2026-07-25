from __future__ import annotations

from io import BytesIO
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from zipfile import ZipFile

from burnlens.replacement_event_reference_custody import (
    ALLOWED_HOST,
    CANONICAL_ARCHIVE_NAME,
    WardCreekReferenceCustodyError,
    acquire_delivery,
    inspect_archive,
)
from burnlens.replacement_event_reference_request import CUSTODY_PATHS


URL = f"https://{ALLOWED_HOST}/downloads/orders/private/example.zip"


def archive_bytes() -> bytes:
    buffer = BytesIO()
    root = "mtbs/2019/mtbs_or4494912090120190812_10016337/"
    with ZipFile(buffer, "w") as archive:
        archive.writestr(
            root + "mtbs_or4494912090120190812_10016337_metadata.xml",
            b"metadata",
        )
        archive.writestr(
            root + "mtbs_or4494912090120190812_10016337_dnbr6.tif",
            b"raster",
        )
    return buffer.getvalue()


class Response:
    def __init__(self, data: bytes, *, fail_after_first: bool = False):
        self.data = data
        self.offset = 0
        self.status = 200
        self.headers = {"Content-Length": str(len(data))}
        self.fail_after_first = fail_after_first

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def getcode(self):
        return 200

    def geturl(self):
        return URL

    def read(self, maximum: int) -> bytes:
        if self.fail_after_first and self.offset:
            raise OSError("synthetic interrupted transfer")
        block = self.data[self.offset : self.offset + maximum]
        self.offset += len(block)
        return block


class ReplacementEventReferenceCustodyTests(unittest.TestCase):
    def test_safe_archive_inspection_binds_event_and_map(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "delivery.zip"
            path.write_bytes(archive_bytes())
            report = inspect_archive(path)
            self.assertEqual(report["member_count"], 2)
            self.assertTrue(report["crc_test_passed"])
            self.assertTrue(report["event_identity_present"])
            self.assertTrue(report["map_identity_present"])

    def test_wrong_route_fails_before_preflight_or_custody(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaisesRegex(
                WardCreekReferenceCustodyError, "HTTPS host"
            ):
                acquire_delivery(
                    repository_root=root,
                    retrieval_url="https://example.com/private.zip",
                    message_received_at_utc="2026-07-24T20:23:22Z",
                    captured_at_utc="2026-07-24T20:30:00Z",
                    delivery_expiry_text="2026-08-23 15:23:21",
                    run_id="BL-2026-07-24-ward-creek-reference-delivery-r001",
                    git_source_commit="a" * 40,
                )
            self.assertFalse(
                (root / CUSTODY_PATHS["delivery_quarantine"]).exists()
            )

    def test_exact_delivery_is_promoted_and_url_is_not_retained(self):
        payload = archive_bytes()
        with TemporaryDirectory() as directory:
            root = Path(directory)
            with patch(
                "burnlens.replacement_event_reference_custody.verify_repository_preflight"
            ):
                report = acquire_delivery(
                    repository_root=root,
                    retrieval_url=URL,
                    message_received_at_utc="2026-07-24T20:23:22Z",
                    captured_at_utc="2026-07-24T20:30:00Z",
                    delivery_expiry_text="2026-08-23 15:23:21",
                    run_id="BL-2026-07-24-ward-creek-reference-delivery-r001",
                    git_source_commit="a" * 40,
                    urlopen_fn=lambda *_args, **_kwargs: Response(payload),
                )
            self.assertEqual(report["archive"]["bytes"], len(payload))
            raw = root / CUSTODY_PATHS["raw_package"] / CANONICAL_ARCHIVE_NAME
            self.assertEqual(raw.read_bytes(), payload)
            combined = json.dumps(report) + (
                root / CUSTODY_PATHS["run_state"]
            ).read_text()
            self.assertNotIn(URL, combined)

    def test_interrupted_transfer_retains_partial_and_forbids_retry(self):
        payload = archive_bytes() + b"x" * (2 * 1024 * 1024)
        with TemporaryDirectory() as directory:
            root = Path(directory)
            with patch(
                "burnlens.replacement_event_reference_custody.verify_repository_preflight"
            ):
                with self.assertRaises(OSError):
                    acquire_delivery(
                        repository_root=root,
                        retrieval_url=URL,
                        message_received_at_utc="2026-07-24T20:23:22Z",
                        captured_at_utc="2026-07-24T20:30:00Z",
                        delivery_expiry_text="2026-08-23 15:23:21",
                        run_id="BL-2026-07-24-ward-creek-reference-delivery-r001",
                        git_source_commit="a" * 40,
                        urlopen_fn=lambda *_args, **_kwargs: Response(
                            payload, fail_after_first=True
                        ),
                    )
            quarantine = root / CUSTODY_PATHS["delivery_quarantine"]
            self.assertTrue(
                (quarantine / f"{CANONICAL_ARCHIVE_NAME}.partial").is_file()
            )
            self.assertFalse((root / CUSTODY_PATHS["raw_package"]).exists())
            failure = (
                root
                / CUSTODY_PATHS["run_state"]
            ).with_name("BL-2026-07-24-ward-creek-reference-r001-failure.json")
            self.assertEqual(
                json.loads(failure.read_text())["state"],
                "DELIVERY_CUSTODY_FAILED_NO_AUTOMATIC_RETRY",
            )


if __name__ == "__main__":
    unittest.main()
