from __future__ import annotations

from contextlib import contextmanager, redirect_stdout
from hashlib import sha256
import http.client
import io
import json
import os
from pathlib import Path
import threading
from tempfile import TemporaryDirectory
import time
import unittest
from unittest.mock import patch
from urllib.request import Request, urlopen
from urllib.parse import urlsplit

from burnlens import serve_review_surface as review_server
from burnlens.owner_review_batch import build_surface, write_surface
from burnlens.serve_review_surface import (
    ReviewSurfaceError,
    create_review_server,
    prepare_review_surface,
)


ROOT = Path(__file__).resolve().parents[1]


def u09a_manifest(evidence_root: Path) -> dict[str, object]:
    evidence: list[dict[str, object]] = []
    for index in range(2):
        path = evidence_root / f"evidence-{index + 1:03d}.png"
        path.write_bytes(b"\x89PNG\r\n\x1a\n" + bytes([index]) * 24)
        payload = path.read_bytes()
        evidence.append(
            {
                "path": path.name,
                "bytes": len(payload),
                "sha256": sha256(payload).hexdigest(),
                "alt": f"Synthetic evidence {index + 1}; software fixture only.",
            }
        )
    candidates = []
    for index, proposed_class in enumerate(("burned", "background")):
        candidates.append(
            {
                "candidate_id": f"U09B-CAND-{index + 1:03d}",
                "event_group_id": "event-u09b-integration",
                "proposed_class": proposed_class,
                "question": f"Is this exact region a usable prototype {proposed_class} label candidate?",
                "proposition_basis": "Synthetic U09A to U09B integration fixture only.",
                "limitations": ["Software fixture; not owner evidence or a label."],
                "facts": [
                    {"label": "Core", "value": "synthetic"},
                    {"label": "Unknown ring", "value": "excluded"},
                ],
                "proposal_binding": {
                    "record_id": f"U09B-PROPOSAL-{index + 1:03d}",
                    "bytes": 100 + index,
                    "sha256": sha256(f"proposal-{index}".encode()).hexdigest(),
                },
                "candidate_raster_binding": {
                    "path": f"candidate-{index + 1:03d}.tif",
                    "bytes": 200 + index,
                    "sha256": sha256(f"raster-{index}".encode()).hexdigest(),
                },
                "evidence_images": [evidence[index]],
            }
        )
    return {
        "manifest_schema_version": "burnlens-owner-review-batch-manifest-v0.1.0",
        "surface_id": "OWNER-REVIEW-BATCH-U09B-INTEGRATION",
        "surface_revision": 1,
        "surface_run_id": "BL-TEST-U09B-INTEGRATION-R001",
        "milestone_id": "P2O4-T33",
        "task_issue": 521,
        "generated_at_utc": "2026-07-21T18:00:00Z",
        "git_source_commit": "a" * 40,
        "title": "Synthetic U09A to U09B integration",
        "review_groups": [
            {
                "event_group_id": "event-u09b-integration",
                "event_label": "Synthetic integration event",
                "context": "Software fixture only; no owner or label evidence.",
                "candidate_ids": [candidate["candidate_id"] for candidate in candidates],
            }
        ],
        "candidates": candidates,
        "batch_size_exception": "single-event-pair",
        "supersedes_surface_id": None,
    }


def output_binding(path: Path, root: Path) -> dict[str, object]:
    payload = path.read_bytes()
    return {
        "path": path.relative_to(root).as_posix(),
        "bytes": len(payload),
        "sha256": sha256(payload).hexdigest(),
    }


@contextmanager
def running_session(snapshot, *, port: int = 0):
    session = create_review_server(
        snapshot,
        port=port,
        capability_token="fixed-test-capability-token",
    )
    thread = threading.Thread(
        target=session.server.serve_forever,
        kwargs={"poll_interval": 0.01},
        daemon=True,
    )
    thread.start()
    try:
        yield session
    finally:
        session.server.shutdown()
        session.server.server_close()
        thread.join(timeout=5)
        if thread.is_alive():
            raise AssertionError("review server thread did not stop")


def raw_request(
    session,
    method: str,
    path: str | None = None,
    *,
    host: str | None = None,
    body: bytes | None = None,
):
    parsed = urlsplit(session.url)
    connection = http.client.HTTPConnection(parsed.hostname, parsed.port, timeout=5)
    request_path = path if path is not None else parsed.path
    connection.putrequest(method, request_path, skip_host=True)
    connection.putheader(
        "Host",
        host if host is not None else f"127.0.0.1:{parsed.port}",
    )
    if body is not None:
        connection.putheader("Content-Length", str(len(body)))
    connection.endheaders(body)
    response = connection.getresponse()
    payload = response.read()
    headers = {name.lower(): value for name, value in response.getheaders()}
    result = response.status, headers, payload
    connection.close()
    return result


class SyntheticReviewSurface:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True)
        self.page = self.root / "SYNTHETIC-OWNER-REVIEW.html"
        self.image = self.root / "evidence.png"
        self.reveal = self.root / "SYNTHETIC-OWNER-REVIEW-REVEAL.html"
        self.private = self.root / "SYNTHETIC-OWNER-RESPONSE.json"
        self.image.write_bytes(b"\x89PNG\r\n\x1a\nexact-synthetic-image")
        self.reveal.write_text("<h1>unlisted reveal</h1>\n", encoding="utf-8")
        self.private.write_text('{"decision":"private"}\n', encoding="utf-8")
        self.write_page(
            """<!doctype html><html><head><meta charset="utf-8">
<style>body{background:#fff}.evidence{background-image:url('evidence.png')}</style>
</head><body><main><img src="evidence.png" alt="synthetic evidence">
<button id="export" type="button">Export exact response</button>
<script>document.getElementById('export').addEventListener('click',()=>{});</script>
</main></body></html>"""
        )
        self.write_report(extra_outputs=(self.reveal, self.private))

    @property
    def report(self) -> Path:
        return self.page.with_suffix(".json")

    def write_page(self, html: str) -> None:
        self.page.write_bytes(html.encode("utf-8"))

    def write_report(self, *, extra_outputs: tuple[Path, ...] = ()) -> None:
        outputs = [output_binding(self.page, self.root), output_binding(self.image, self.root)]
        outputs.extend(output_binding(path, self.root) for path in extra_outputs)
        self.report.write_text(
            json.dumps(
                {
                    "report_id": self.page.stem,
                    "response_schema_version": "synthetic-owner-response-v1",
                    "outputs": outputs,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )


class ReviewSurfacePreparationTests(unittest.TestCase):
    def test_u09a_output_prepares_and_serves_as_u09b_snapshot(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            evidence_root = root / "evidence"
            evidence_root.mkdir()
            surface = build_surface(u09a_manifest(evidence_root))
            output = root / "surface"
            write_surface(surface, evidence_root, output)
            page = output / f"{surface['report_id']}.html"

            snapshot = prepare_review_surface(page)
            self.assertEqual(len(snapshot.resources), 3)
            self.assertEqual(
                set(snapshot.resources),
                {page.name, "evidence-001.png", "evidence-002.png"},
            )
            with running_session(snapshot) as session:
                with urlopen(session.url, timeout=5) as response:
                    self.assertEqual(response.read(), page.read_bytes())

    def test_current_owner_review_formats_prepare_from_exact_output_bindings(self) -> None:
        cases = {
            "samples/labels/review/phase-two/OWNER-REVIEW-SURFACE-2026-001.html": 17,
            "samples/labels/review/regions/phase-two/REGION-OWNER-REVIEW-SURFACE-2026-001.html": 7,
            "samples/labels/review/green-ridge/phase-two/GREEN-RIDGE-OWNER-REVIEW-SURFACE-2026-001.html": 3,
            "samples/labels/review/grandview/phase-two/GRANDVIEW-OWNER-REVIEW-SURFACE-2026-001.html": 3,
        }
        for relative, resource_count in cases.items():
            with self.subTest(relative=relative):
                snapshot = prepare_review_surface(ROOT / relative)
                self.assertEqual(len(snapshot.resources), resource_count)
                self.assertEqual(
                    snapshot.page.sha256,
                    sha256(snapshot.page_path.read_bytes()).hexdigest(),
                )
                self.assertFalse(
                    any("REVEAL" in path.upper() for path in snapshot.resources)
                )

    def test_external_missing_unbound_and_navigation_resources_fail_closed(self) -> None:
        cases = (
            (
                '<!doctype html><img src="https://example.com/evidence.png">',
                "REVIEW_SURFACE_EXTERNAL_OR_ABSOLUTE_RESOURCE",
            ),
            (
                '<!doctype html><img src="missing.png">',
                "REVIEW_SURFACE_REFERENCED_RESOURCE_NOT_BOUND",
            ),
            (
                '<!doctype html><a href="SYNTHETIC-OWNER-REVIEW-REVEAL.html">Reveal</a>',
                "REVIEW_SURFACE_NAVIGATION_LINK_NOT_ALLOWED",
            ),
            (
                '<!doctype html><iframe src="evidence.png"></iframe>',
                "REVIEW_SURFACE_FORBIDDEN_ELEMENT",
            ),
            (
                '<!doctype html><meta http-equiv="refresh" content="0;url=https://example.com">',
                "REVIEW_SURFACE_META_REFRESH_NOT_ALLOWED",
            ),
            (
                '<!doctype html><img src="evidence.png" SRC="SYNTHETIC-OWNER-RESPONSE.json">',
                "REVIEW_SURFACE_DUPLICATE_HTML_ATTRIBUTE",
            ),
        )
        for html, reason in cases:
            with self.subTest(reason=reason), TemporaryDirectory() as directory:
                fixture = SyntheticReviewSurface(Path(directory) / "surface")
                fixture.write_page(html)
                fixture.write_report(extra_outputs=(fixture.reveal, fixture.private))
                with self.assertRaisesRegex(ReviewSurfaceError, reason):
                    prepare_review_surface(fixture.page)

    def test_manifest_bound_reveal_and_response_references_fail_closed(self) -> None:
        cases = (
            (
                '<!doctype html><script src="SYNTHETIC-OWNER-REVIEW-REVEAL.html"></script>',
                "REVIEW_SURFACE_SECONDARY_HTML_NOT_ALLOWED",
            ),
            (
                '<!doctype html><script src="SYNTHETIC-OWNER-RESPONSE.json"></script>',
                "REVIEW_SURFACE_DATA_RESOURCE_NOT_ALLOWED",
            ),
        )
        for html, reason in cases:
            with self.subTest(reason=reason), TemporaryDirectory() as directory:
                fixture = SyntheticReviewSurface(Path(directory) / "surface")
                fixture.write_page(html)
                fixture.write_report(extra_outputs=(fixture.reveal, fixture.private))
                with self.assertRaisesRegex(ReviewSurfaceError, reason):
                    prepare_review_surface(fixture.page)

    def test_non_owner_report_and_report_id_mismatch_fail_closed(self) -> None:
        with TemporaryDirectory() as directory:
            fixture = SyntheticReviewSurface(Path(directory) / "surface")
            report = json.loads(fixture.report.read_text(encoding="utf-8"))
            del report["response_schema_version"]
            fixture.report.write_text(json.dumps(report), encoding="utf-8")
            with self.assertRaisesRegex(
                ReviewSurfaceError, "REVIEW_SURFACE_NOT_OWNER_REVIEW_REPORT"
            ):
                prepare_review_surface(fixture.page)

        with TemporaryDirectory() as directory:
            fixture = SyntheticReviewSurface(Path(directory) / "surface")
            report = json.loads(fixture.report.read_text(encoding="utf-8"))
            report["report_id"] = "DIFFERENT-OWNER-REVIEW"
            fixture.report.write_text(json.dumps(report), encoding="utf-8")
            with self.assertRaisesRegex(
                ReviewSurfaceError, "REVIEW_SURFACE_REPORT_ID_MISMATCH"
            ):
                prepare_review_surface(fixture.page)

    def test_sensitive_primary_page_fails_closed_even_when_bound(self) -> None:
        with TemporaryDirectory() as directory:
            fixture = SyntheticReviewSurface(Path(directory) / "surface")
            fixture.page = fixture.root / "SYNTHETIC-OWNER-REVIEW-REVEAL.html"
            fixture.write_page("<!doctype html><p>bound synthetic reveal</p>")
            fixture.write_report()
            with self.assertRaisesRegex(
                ReviewSurfaceError, "REVIEW_SURFACE_SENSITIVE_PAGE_NOT_ALLOWED"
            ):
                prepare_review_surface(fixture.page)

    def test_manifest_and_resource_drift_fail_closed(self) -> None:
        with TemporaryDirectory() as directory:
            fixture = SyntheticReviewSurface(Path(directory) / "surface")
            report = json.loads(fixture.report.read_text(encoding="utf-8"))
            report["outputs"][0]["path"] = "../SYNTHETIC-OWNER-REVIEW.html"
            fixture.report.write_text(json.dumps(report), encoding="utf-8")
            with self.assertRaisesRegex(
                ReviewSurfaceError, "REVIEW_SURFACE_OUTPUT_PATH_INVALID"
            ):
                prepare_review_surface(fixture.page)

        with TemporaryDirectory() as directory:
            fixture = SyntheticReviewSurface(Path(directory) / "surface")
            fixture.image.write_bytes(fixture.image.read_bytes() + b"drift")
            with self.assertRaisesRegex(
                ReviewSurfaceError, "REVIEW_SURFACE_RESOURCE_BYTE_COUNT_MISMATCH"
            ):
                prepare_review_surface(fixture.page)

    def test_symlink_or_reparse_resource_fails_closed(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory) / "surface"
            fixture = SyntheticReviewSurface(root)
            target = Path(directory) / "outside.png"
            target.write_bytes(fixture.image.read_bytes())
            fixture.image.unlink()
            try:
                os.symlink(target, fixture.image)
            except (OSError, NotImplementedError) as error:
                self.skipTest(f"symlink creation unavailable: {error}")
            fixture.write_report(extra_outputs=(fixture.reveal, fixture.private))
            with self.assertRaisesRegex(
                ReviewSurfaceError, "REVIEW_SURFACE_REPARSE_PATH_NOT_ALLOWED"
            ):
                prepare_review_surface(fixture.page)


class ReviewSurfaceHTTPTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.fixture = SyntheticReviewSurface(Path(self.temporary.name) / "surface")
        self.snapshot = prepare_review_surface(self.fixture.page)

    def test_get_and_head_return_exact_bytes_and_security_headers(self) -> None:
        page_before = self.fixture.page.stat()
        image_before = self.fixture.image.stat()
        page_hash_before = sha256(self.fixture.page.read_bytes()).hexdigest()
        image_hash_before = sha256(self.fixture.image.read_bytes()).hexdigest()
        with running_session(self.snapshot) as session:
            with urlopen(session.url, timeout=5) as response:
                payload = response.read()
                headers = {name.lower(): value for name, value in response.headers.items()}
            self.assertEqual(payload, self.fixture.page.read_bytes())
            self.assertEqual(sha256(payload).hexdigest(), self.snapshot.page.sha256)
            self.assertEqual(int(headers["content-length"]), len(payload))
            self.assertEqual(headers["content-type"], "text/html; charset=utf-8")
            self.assertEqual(headers["cache-control"], "no-store")
            self.assertIn("connect-src 'none'", headers["content-security-policy"])
            self.assertEqual(headers["cross-origin-resource-policy"], "same-origin")
            self.assertEqual(headers["x-content-type-options"], "nosniff")
            self.assertNotIn("server", headers)
            self.assertNotIn("access-control-allow-origin", headers)
            self.assertNotIn("set-cookie", headers)

            head_status, head_headers, head_payload = raw_request(session, "HEAD")
            self.assertEqual(head_status, 200)
            self.assertEqual(head_payload, b"")
            self.assertEqual(int(head_headers["content-length"]), len(payload))

            image_url = session.url.rsplit("/", 1)[0] + "/evidence.png"
            with urlopen(image_url, timeout=5) as response:
                self.assertEqual(response.read(), self.fixture.image.read_bytes())
                self.assertEqual(response.headers["Content-Type"], "image/png")

        page_after = self.fixture.page.stat()
        image_after = self.fixture.image.stat()
        self.assertEqual(
            (page_after.st_size, page_after.st_mtime_ns),
            (page_before.st_size, page_before.st_mtime_ns),
        )
        self.assertEqual(
            (image_after.st_size, image_after.st_mtime_ns),
            (image_before.st_size, image_before.st_mtime_ns),
        )
        self.assertEqual(
            sha256(self.fixture.page.read_bytes()).hexdigest(), page_hash_before
        )
        self.assertEqual(
            sha256(self.fixture.image.read_bytes()).hexdigest(), image_hash_before
        )

    def test_unlisted_sensitive_paths_and_traversal_are_not_served(self) -> None:
        with running_session(self.snapshot) as session:
            parsed = urlsplit(session.url)
            prefix = f"/{session.capability_token}/"
            paths = (
                "/",
                prefix,
                prefix + "SYNTHETIC-OWNER-REVIEW-REVEAL.html",
                prefix + "SYNTHETIC-OWNER-RESPONSE.json",
                prefix + ".git/config",
                prefix + "downloads/phase-two/raw/",
                prefix + "../SYNTHETIC-OWNER-REVIEW-REVEAL.html",
                prefix + "%2e%2e/SYNTHETIC-OWNER-REVIEW-REVEAL.html",
                prefix + "C%3A/Windows/win.ini",
                prefix + "%5c%5cserver%5cshare",
                f"/wrong-capability/{self.fixture.page.name}",
            )
            for path in paths:
                with self.subTest(path=path):
                    status, _, _ = raw_request(
                        session,
                        "GET",
                        path,
                        host=f"127.0.0.1:{parsed.port}",
                    )
                    self.assertEqual(status, 404)

    def test_host_and_write_method_boundaries_fail_closed(self) -> None:
        hashes_before = {
            path: sha256(path.read_bytes()).hexdigest()
            for path in (
                self.fixture.page,
                self.fixture.image,
                self.fixture.reveal,
                self.fixture.private,
                self.fixture.report,
            )
        }
        with running_session(self.snapshot) as session:
            status, _, _ = raw_request(session, "GET", host="attacker.example")
            self.assertEqual(status, 400)
            for method in ("POST", "PUT", "PATCH", "DELETE", "OPTIONS"):
                with self.subTest(method=method):
                    status, headers, payload = raw_request(
                        session,
                        method,
                        body=b'{"attempt":"write"}',
                    )
                    self.assertEqual(status, 405)
                    self.assertEqual(headers["allow"], "GET, HEAD")
                    self.assertEqual(payload, b"")
            for method in ("PROPFIND", "BREW"):
                with self.subTest(method=method):
                    status, headers, payload = raw_request(session, method)
                    self.assertEqual(status, 405)
                    self.assertEqual(headers["allow"], "GET, HEAD")
                    self.assertEqual(headers["cache-control"], "no-store")
                    self.assertNotIn("server", headers)
                    self.assertEqual(payload, b"")
        hashes_after = {
            path: sha256(path.read_bytes()).hexdigest() for path in hashes_before
        }
        self.assertEqual(hashes_after, hashes_before)

    def test_running_session_serves_immutable_startup_snapshot(self) -> None:
        expected_page = self.fixture.page.read_bytes()
        expected_image = self.fixture.image.read_bytes()
        with running_session(self.snapshot) as session:
            self.fixture.page.write_text("changed after bind", encoding="utf-8")
            self.fixture.image.write_bytes(b"changed after bind")
            with urlopen(session.url, timeout=5) as response:
                self.assertEqual(response.read(), expected_page)
            image_url = session.url.rsplit("/", 1)[0] + "/evidence.png"
            with urlopen(image_url, timeout=5) as response:
                self.assertEqual(response.read(), expected_image)

    def test_port_zero_collision_and_clean_reuse(self) -> None:
        first = create_review_server(
            self.snapshot,
            port=0,
            capability_token="first-test-capability-token",
        )
        selected_port = first.server.server_address[1]
        self.assertEqual(first.server.server_address[0], "127.0.0.1")
        with self.assertRaises(OSError):
            create_review_server(
                self.snapshot,
                port=selected_port,
                capability_token="second-test-capability-token",
            )
        first.server.server_close()
        for _ in range(50):
            try:
                replacement = create_review_server(
                    self.snapshot,
                    port=selected_port,
                    capability_token="replacement-capability-token",
                )
                break
            except OSError:
                time.sleep(0.01)
        else:
            self.fail("closed review port was not reusable")
        replacement.server.server_close()

    def test_cli_emits_parseable_ready_contract_and_closes(self) -> None:
        output = io.StringIO()
        with patch.object(
            review_server._LoopbackReviewServer,
            "serve_forever",
            side_effect=KeyboardInterrupt,
        ), redirect_stdout(output):
            self.assertEqual(
                review_server.main(
                    ["--page", str(self.fixture.page), "--port", "0"]
                ),
                0,
            )
        lines = dict(
            line.split("=", 1)
            for line in output.getvalue().splitlines()
            if "=" in line
        )
        self.assertTrue(lines["REVIEW_SURFACE_URL"].startswith("http://127.0.0.1:"))
        self.assertEqual(lines["REVIEW_SURFACE_SHA256"], self.snapshot.page.sha256)
        self.assertEqual(lines["REVIEW_SURFACE_RESOURCE_COUNT"], "2")
        self.assertEqual(lines["REVIEW_SURFACE_STOP"], "Ctrl+C")

    def test_browser_open_exception_still_closes_bound_server(self) -> None:
        session = create_review_server(
            self.snapshot,
            port=0,
            capability_token="browser-failure-capability-token",
        )
        selected_port = session.server.server_address[1]
        with patch.object(
            review_server,
            "create_review_server",
            return_value=session,
        ), patch.object(
            review_server.webbrowser,
            "open",
            side_effect=RuntimeError("synthetic browser failure"),
        ), redirect_stdout(io.StringIO()):
            self.assertEqual(
                review_server.main(
                    ["--page", str(self.fixture.page), "--open-browser"]
                ),
                2,
            )
        replacement = create_review_server(
            self.snapshot,
            port=selected_port,
            capability_token="browser-failure-reuse-token",
        )
        replacement.server.server_close()


if __name__ == "__main__":
    unittest.main()
