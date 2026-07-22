from __future__ import annotations

from io import BytesIO
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile

from burnlens.petes_lake_reference_custody import (
    ALLOWED_HOST,
    CANONICAL_ARCHIVE_NAME,
    PetesLakeReferenceCustodyError,
    acquire_delivery,
)
from burnlens.petes_lake_reference_request import CUSTODY_PATHS


URL = f"https://{ALLOWED_HOST}/downloads/orders/private/example.zip"


def archive_bytes() -> bytes:
    buffer = BytesIO()
    root = "mtbs/2023/mtbs_or4396912190120230825_10031414/"
    with ZipFile(buffer, "w") as archive:
        archive.writestr(root + "mtbs_or4396912190120230825_10031414_metadata.xml", b"metadata")
        archive.writestr(root + "mtbs_or4396912190120230825_10031414_dnbr6.tif", b"raster")
    return buffer.getvalue()


class Response:
    def __init__(self, data: bytes, *, fail_after_first: bool = False) -> None:
        self.data = data
        self.offset = 0
        self.status = 200
        self.headers = {"Content-Length": str(len(data))}
        self.fail_after_first = fail_after_first

    def __enter__(self) -> "Response":
        return self

    def __exit__(self, *_: object) -> None:
        return None

    def geturl(self) -> str:
        return URL

    def read(self, maximum: int) -> bytes:
        if self.fail_after_first and self.offset:
            raise OSError("synthetic interrupted transfer")
        block = self.data[self.offset:self.offset + maximum]
        self.offset += len(block)
        return block


class PetesLakeReferenceCustodyTests(unittest.TestCase):
    def repository(self, root: Path) -> tuple[Path, bytes]:
        (root / ".git").mkdir()
        (root / "pyproject.toml").write_text("[project]\nname='burnlens'\n")
        receipt = {
            "run_id": "BL-2026-07-21-petes-lake-reference-request-r001",
            "git_source_commit": "a9e7b3fce9a06b5781fd84e2f5d4cf474523e16e",
            "event_id": "OR4396912190120230825",
            "map_id": 10031414,
            "request": {"state": "ACCEPTED", "mapping_ids": [10031414]},
            "delivery": {"state": "PENDING_EMAIL_DELIVERY"},
        }
        data = (json.dumps(receipt) + "\n").encode()
        path = root / CUSTODY_PATHS["request_directory"] / "request-receipt.json"
        path.parent.mkdir(parents=True)
        path.write_bytes(data)
        return root, data

    def test_exact_delivery_is_preflighted_promoted_and_url_private(self) -> None:
        payload = archive_bytes()
        with TemporaryDirectory() as directory:
            root, receipt = self.repository(Path(directory))
            calls = 0

            def open_once(_: object, **__: object) -> Response:
                nonlocal calls
                calls += 1
                return Response(payload)

            report = acquire_delivery(
                repository_root=root,
                retrieval_url=URL,
                message_received_at_utc="2026-07-21T23:05:35Z",
                captured_at_utc="2026-07-21T23:10:00Z",
                delivery_expiry_text="2026-08-20 18:03:20",
                run_id="BL-TEST-PETES-LAKE-REFERENCE-DELIVERY-R001",
                git_source_commit="f" * 40,
                urlopen_fn=open_once,
                expected_request_receipt_bytes=len(receipt),
                expected_request_receipt_sha256=__import__("hashlib").sha256(receipt).hexdigest(),
            )
            self.assertEqual(calls, 1)
            self.assertEqual(report["archive"]["bytes"], len(payload))
            self.assertFalse(report["archive"]["provider_route_retained"])
            raw = root / CUSTODY_PATHS["raw_package"] / CANONICAL_ARCHIVE_NAME
            self.assertEqual(raw.read_bytes(), payload)
            self.assertFalse((root / CUSTODY_PATHS["delivery_quarantine"]).exists())
            state = root / CUSTODY_PATHS["run_state"]
            combined = state.read_text() + json.dumps(report)
            self.assertNotIn(URL, combined)

    def test_wrong_route_fails_before_custody(self) -> None:
        with TemporaryDirectory() as directory:
            root, receipt = self.repository(Path(directory))
            with self.assertRaisesRegex(PetesLakeReferenceCustodyError, "HTTPS host"):
                acquire_delivery(
                    repository_root=root,
                    retrieval_url="https://example.com/private.zip",
                    message_received_at_utc="2026-07-21T23:05:35Z",
                    captured_at_utc="2026-07-21T23:10:00Z",
                    delivery_expiry_text="2026-08-20 18:03:20",
                    run_id="BL-TEST-PETES-LAKE-REFERENCE-DELIVERY-BAD-ROUTE",
                    git_source_commit="f" * 40,
                    expected_request_receipt_bytes=len(receipt),
                    expected_request_receipt_sha256=__import__("hashlib").sha256(receipt).hexdigest(),
                )
            self.assertFalse((root / CUSTODY_PATHS["delivery_quarantine"]).exists())

    def test_interrupted_transfer_retains_attempt_and_partial_without_retry(self) -> None:
        payload = archive_bytes() + b"x" * (1024 * 1024)
        with TemporaryDirectory() as directory:
            root, receipt = self.repository(Path(directory))
            calls = 0

            def open_once(_: object, **__: object) -> Response:
                nonlocal calls
                calls += 1
                return Response(payload, fail_after_first=True)

            with self.assertRaisesRegex(PetesLakeReferenceCustodyError, "no retry"):
                acquire_delivery(
                    repository_root=root,
                    retrieval_url=URL,
                    message_received_at_utc="2026-07-21T23:05:35Z",
                    captured_at_utc="2026-07-21T23:10:00Z",
                    delivery_expiry_text="2026-08-20 18:03:20",
                    run_id="BL-TEST-PETES-LAKE-REFERENCE-DELIVERY-INTERRUPTED",
                    git_source_commit="f" * 40,
                    urlopen_fn=open_once,
                    expected_request_receipt_bytes=len(receipt),
                    expected_request_receipt_sha256=__import__("hashlib").sha256(receipt).hexdigest(),
                )
            self.assertEqual(calls, 1)
            quarantine = root / CUSTODY_PATHS["delivery_quarantine"]
            partial = quarantine / (CANONICAL_ARCHIVE_NAME + ".partial")
            self.assertTrue(partial.is_file())
            self.assertFalse((root / CUSTODY_PATHS["raw_package"]).exists())
            run_state = root / CUSTODY_PATHS["run_state"]
            failure = run_state.with_suffix("").with_name(run_state.stem + "-failure.json")
            self.assertEqual(
                json.loads(failure.read_text())["state"],
                "DELIVERY_CUSTODY_FAILED_NO_AUTOMATIC_RETRY",
            )


if __name__ == "__main__":
    unittest.main()
