"""Serve one exact BurnLens review surface over an allowlisted loopback origin.

The selected HTML and every static resource it references must be bound by the
surface's sibling JSON report.  All served bytes are verified and preloaded
before the listener opens, so one review session is immutable and never exposes
the containing directory, repository, reveal pages, or response custody.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from functools import partial
from hashlib import sha256
from html.parser import HTMLParser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path, PurePosixPath
import re
import secrets
import stat
import sys
from types import MappingProxyType
from typing import Any, Mapping, Sequence
from urllib.parse import quote, unquote_to_bytes, urlsplit
import webbrowser


LOOPBACK_HOST = "127.0.0.1"
DEFAULT_PORT = 0
CAPABILITY_TOKEN_BYTES = 24
MAX_REJECTED_REQUEST_BODY_BYTES = 64 * 1024

_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
_CSS_URL_PATTERN = re.compile(
    r"url\(\s*(?:'([^']*)'|\"([^\"]*)\"|([^\s\)]+))\s*\)",
    re.IGNORECASE,
)
_REPARSE_ATTRIBUTE = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x0400)

_CONTENT_TYPES = {
    ".css": "text/css; charset=utf-8",
    ".gif": "image/gif",
    ".html": "text/html; charset=utf-8",
    ".ico": "image/x-icon",
    ".jpeg": "image/jpeg",
    ".jpg": "image/jpeg",
    ".js": "text/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".mjs": "text/javascript; charset=utf-8",
    ".png": "image/png",
    ".svg": "image/svg+xml",
    ".txt": "text/plain; charset=utf-8",
    ".webp": "image/webp",
}

_REFERENCED_RESOURCE_SUFFIXES = {
    ".css",
    ".gif",
    ".ico",
    ".jpeg",
    ".jpg",
    ".js",
    ".mjs",
    ".png",
    ".svg",
    ".webp",
}
_SENSITIVE_RESOURCE_TOKEN = re.compile(
    r"(?:^|[-_.])(?:adjudication|intake|private|quarantine|raw|receipt|response|reveal|template)(?:[-_.]|$)",
    re.IGNORECASE,
)

_RESOURCE_ATTRIBUTES = {
    "audio": ("src",),
    "img": ("src", "srcset"),
    "input": ("src",),
    "link": ("href",),
    "script": ("src",),
    "source": ("src", "srcset"),
    "track": ("src",),
    "video": ("src", "poster"),
}
_FORBIDDEN_ELEMENTS = {"base", "embed", "form", "iframe", "object"}

_CONTENT_SECURITY_POLICY = "; ".join(
    (
        "default-src 'none'",
        "img-src 'self' data: blob:",
        "style-src 'self' 'unsafe-inline'",
        "script-src 'self' 'unsafe-inline'",
        "font-src 'self' data:",
        "media-src 'self'",
        "connect-src 'none'",
        "worker-src 'none'",
        "frame-src 'none'",
        "object-src 'none'",
        "base-uri 'none'",
        "form-action 'none'",
        "frame-ancestors 'none'",
    )
)


class ReviewSurfaceError(ValueError):
    """Raised when a review surface cannot be served without weakening a gate."""


@dataclass(frozen=True)
class BoundResource:
    """One immutable response body admitted to a review session."""

    relative_path: str
    payload: bytes
    sha256: str
    content_type: str


@dataclass(frozen=True)
class ReviewSurfaceSnapshot:
    """Verified startup snapshot for one selected HTML page."""

    page_path: Path
    report_path: Path
    page_relative_path: str
    resources: Mapping[str, BoundResource]

    @property
    def page(self) -> BoundResource:
        return self.resources[self.page_relative_path]

    @property
    def total_bytes(self) -> int:
        return sum(len(item.payload) for item in self.resources.values())


@dataclass(frozen=True)
class ReviewServerSession:
    """Bound HTTP server and the capability URL for its selected page."""

    server: ThreadingHTTPServer
    url: str
    capability_token: str
    snapshot: ReviewSurfaceSnapshot


def _error(code: str, detail: str | None = None) -> ReviewSurfaceError:
    return ReviewSurfaceError(code if detail is None else f"{code}:{detail}")


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise _error("REVIEW_SURFACE_REPORT_DUPLICATE_JSON_KEY", key)
        value[key] = item
    return value


def _is_reparse(path: Path) -> bool:
    metadata = os.lstat(path)
    return stat.S_ISLNK(metadata.st_mode) or bool(
        getattr(metadata, "st_file_attributes", 0) & _REPARSE_ATTRIBUTE
    )


def _assert_existing_path_has_no_reparse(path: Path) -> None:
    """Reject symbolic links and Windows junction/reparse ancestors."""

    absolute = path.absolute()
    chain = [absolute, *absolute.parents]
    for current in reversed(chain):
        if current.exists() and _is_reparse(current):
            raise _error("REVIEW_SURFACE_REPARSE_PATH_NOT_ALLOWED", str(current))


def _safe_relative_path(value: Any, *, code: str) -> str:
    if not isinstance(value, str) or not value:
        raise _error(code, "path is not a non-empty string")
    if "\x00" in value or "\\" in value or ":" in value:
        raise _error(code, value)
    if value.startswith(("/", "//")):
        raise _error(code, value)
    pieces = value.split("/")
    if any(piece in {"", ".", ".."} for piece in pieces):
        raise _error(code, value)
    path = PurePosixPath(value)
    normalized = path.as_posix()
    if normalized != value:
        raise _error(code, value)
    return normalized


def _decode_url_path(value: str, *, code: str) -> str:
    try:
        decoded = unquote_to_bytes(value).decode("utf-8", errors="strict")
    except (UnicodeDecodeError, ValueError) as error:
        raise _error(code, "invalid UTF-8 URL path") from error
    return _safe_relative_path(decoded, code=code)


def _normalize_reference(value: str, *, base_directory: PurePosixPath) -> str | None:
    reference = value.strip()
    if not reference or reference.startswith("#"):
        return None
    parsed = urlsplit(reference)
    if parsed.scheme or parsed.netloc or reference.startswith(("//", "/", "\\")):
        raise _error("REVIEW_SURFACE_EXTERNAL_OR_ABSOLUTE_RESOURCE", reference)
    relative = _decode_url_path(
        parsed.path,
        code="REVIEW_SURFACE_UNSAFE_RESOURCE_PATH",
    )
    joined = base_directory.joinpath(PurePosixPath(relative))
    return _safe_relative_path(
        joined.as_posix(),
        code="REVIEW_SURFACE_UNSAFE_RESOURCE_PATH",
    )


def _srcset_references(value: str) -> list[str]:
    if value.lstrip().lower().startswith("data:"):
        raise _error("REVIEW_SURFACE_EXTERNAL_OR_ABSOLUTE_RESOURCE", "data: srcset")
    references: list[str] = []
    for item in value.split(","):
        candidate = item.strip().split(maxsplit=1)[0] if item.strip() else ""
        if candidate:
            references.append(candidate)
    return references


class _ReviewReferenceParser(HTMLParser):
    def __init__(self, page_relative_path: str) -> None:
        super().__init__(convert_charrefs=True)
        self._base = PurePosixPath(page_relative_path).parent
        self._style_depth = 0
        self.references: set[str] = set()

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        self._handle_element(tag.lower(), attrs)

    def handle_startendtag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        self._handle_element(tag.lower(), attrs)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "style" and self._style_depth:
            self._style_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._style_depth:
            self._collect_css(data)

    def _handle_element(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        if tag in _FORBIDDEN_ELEMENTS:
            raise _error("REVIEW_SURFACE_FORBIDDEN_ELEMENT", tag)
        if tag == "style":
            self._style_depth += 1
        attribute_names = [name.lower() for name, _ in attrs]
        if len(attribute_names) != len(set(attribute_names)):
            raise _error("REVIEW_SURFACE_DUPLICATE_HTML_ATTRIBUTE", tag)
        attributes = {name.lower(): value for name, value in attrs}
        if tag == "meta" and str(attributes.get("http-equiv", "")).lower() == "refresh":
            raise _error("REVIEW_SURFACE_META_REFRESH_NOT_ALLOWED")
        if tag == "a" and attributes.get("href") not in {None, ""}:
            href = str(attributes["href"]).strip()
            if not href.startswith("#"):
                raise _error("REVIEW_SURFACE_NAVIGATION_LINK_NOT_ALLOWED", href)
        if attributes.get("style"):
            self._collect_css(str(attributes["style"]))
        for name in _RESOURCE_ATTRIBUTES.get(tag, ()):
            value = attributes.get(name)
            if not value:
                continue
            candidates = _srcset_references(str(value)) if name == "srcset" else [str(value)]
            for candidate in candidates:
                normalized = _normalize_reference(candidate, base_directory=self._base)
                if normalized is not None:
                    self.references.add(normalized)

    def _collect_css(self, value: str) -> None:
        for match in _CSS_URL_PATTERN.finditer(value):
            candidate = next(item for item in match.groups() if item is not None)
            normalized = _normalize_reference(candidate, base_directory=self._base)
            if normalized is not None:
                self.references.add(normalized)


def _content_type(relative_path: str) -> str:
    suffix = PurePosixPath(relative_path).suffix.lower()
    try:
        return _CONTENT_TYPES[suffix]
    except KeyError as error:
        raise _error("REVIEW_SURFACE_UNSUPPORTED_RESOURCE_TYPE", suffix or "none") from error


def _assert_owner_review_report(
    report: Mapping[str, Any],
    *,
    page_relative_path: str,
) -> None:
    """Reject non-review reports even when their output bytes are valid."""

    if _SENSITIVE_RESOURCE_TOKEN.search(PurePosixPath(page_relative_path).name):
        raise _error("REVIEW_SURFACE_SENSITIVE_PAGE_NOT_ALLOWED", page_relative_path)
    report_id = report.get("report_id")
    if report_id != PurePosixPath(page_relative_path).stem:
        raise _error("REVIEW_SURFACE_REPORT_ID_MISMATCH", str(report_id))
    response_schema_version = report.get("response_schema_version")
    if not isinstance(response_schema_version, str) or not response_schema_version.strip():
        raise _error("REVIEW_SURFACE_NOT_OWNER_REVIEW_REPORT", str(report_id))


def _assert_admissible_referenced_resource(
    relative_path: str,
    *,
    page_relative_path: str,
) -> None:
    """Apply an independent deny gate beyond manifest membership and hashes."""

    path = PurePosixPath(relative_path)
    if path.parent != PurePosixPath(page_relative_path).parent:
        raise _error("REVIEW_SURFACE_RESOURCE_NOT_SIBLING", relative_path)
    suffix = path.suffix.lower()
    if suffix == ".html":
        raise _error("REVIEW_SURFACE_SECONDARY_HTML_NOT_ALLOWED", relative_path)
    if suffix == ".json":
        raise _error("REVIEW_SURFACE_DATA_RESOURCE_NOT_ALLOWED", relative_path)
    if suffix not in _REFERENCED_RESOURCE_SUFFIXES:
        raise _error("REVIEW_SURFACE_UNSUPPORTED_RESOURCE_TYPE", suffix or "none")
    if _SENSITIVE_RESOURCE_TOKEN.search(path.name):
        raise _error("REVIEW_SURFACE_SENSITIVE_RESOURCE_NOT_ALLOWED", relative_path)


def _parse_report_payload(payload: bytes, *, report_path: Path) -> dict[str, Any]:
    try:
        text = payload.decode("utf-8", errors="strict")
        value = json.loads(text, object_pairs_hook=_reject_duplicate_keys)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise _error("REVIEW_SURFACE_REPORT_INVALID", str(report_path)) from error
    if not isinstance(value, dict):
        raise _error("REVIEW_SURFACE_REPORT_INVALID", str(report_path))
    outputs = value.get("outputs")
    if not isinstance(outputs, (list, dict)):
        raise _error("REVIEW_SURFACE_REPORT_OUTPUTS_INVALID")
    return value


def _load_report(report_path: Path) -> tuple[dict[str, Any], bytes]:
    _assert_existing_path_has_no_reparse(report_path)
    if not report_path.is_file():
        raise _error("REVIEW_SURFACE_REPORT_NOT_FOUND", str(report_path))
    try:
        payload = report_path.read_bytes()
    except OSError as error:
        raise _error("REVIEW_SURFACE_REPORT_INVALID", str(report_path)) from error
    return _parse_report_payload(payload, report_path=report_path), payload


def _output_entries(report: dict[str, Any]) -> list[Any]:
    outputs = report.get("outputs")
    if isinstance(outputs, list):
        return outputs
    if isinstance(outputs, dict) and isinstance(outputs.get("files"), list):
        return outputs["files"]
    raise _error("REVIEW_SURFACE_REPORT_OUTPUTS_INVALID")


def _linked_report_descriptors(report: dict[str, Any]) -> list[tuple[str, str]]:
    source_bindings = report.get("source_bindings")
    if not isinstance(source_bindings, dict):
        return []
    descriptors: list[tuple[str, str]] = []
    for value in source_bindings.values():
        if not isinstance(value, dict):
            continue
        report_id = value.get("report_id")
        digest = value.get("sha256")
        if (
            isinstance(report_id, str)
            and report_id
            and isinstance(digest, str)
            and _SHA256_PATTERN.fullmatch(digest)
        ):
            descriptors.append((report_id, digest))
    return descriptors


def _merge_binding_maps(
    target: dict[str, dict[str, Any]],
    source: Mapping[str, dict[str, Any]],
) -> None:
    for relative, binding in source.items():
        existing = target.get(relative)
        if existing is not None and (
            existing["bytes"] != binding["bytes"]
            or existing["sha256"] != binding["sha256"]
        ):
            raise _error("REVIEW_SURFACE_OUTPUT_BINDING_CONFLICT", relative)
        target.setdefault(relative, binding)


def _all_bound_outputs(
    report: dict[str, Any],
    *,
    root: Path,
) -> dict[str, dict[str, Any]]:
    bindings = _output_bindings(report)
    for report_id, expected_sha256 in _linked_report_descriptors(report):
        relative_report = _safe_relative_path(
            f"{report_id}.json",
            code="REVIEW_SURFACE_LINKED_REPORT_ID_INVALID",
        )
        linked_path = root.joinpath(*PurePosixPath(relative_report).parts)
        if not linked_path.is_file():
            continue
        linked, payload = _load_report(linked_path)
        if sha256(payload).hexdigest() != expected_sha256:
            raise _error("REVIEW_SURFACE_LINKED_REPORT_SHA256_MISMATCH", report_id)
        if linked.get("report_id") != report_id:
            raise _error("REVIEW_SURFACE_LINKED_REPORT_ID_MISMATCH", report_id)
        _merge_binding_maps(bindings, _output_bindings(linked))
    return bindings


def _output_bindings(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    entries = _output_entries(report)
    if not entries:
        raise _error("REVIEW_SURFACE_REPORT_OUTPUTS_INVALID")
    bindings: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(entries):
        if not isinstance(item, dict):
            raise _error("REVIEW_SURFACE_OUTPUT_BINDING_INVALID", str(index))
        relative = _safe_relative_path(
            item.get("path"),
            code="REVIEW_SURFACE_OUTPUT_PATH_INVALID",
        )
        byte_count = item.get("bytes")
        digest = item.get("sha256")
        if (
            isinstance(byte_count, bool)
            or not isinstance(byte_count, int)
            or byte_count < 0
            or not isinstance(digest, str)
            or not _SHA256_PATTERN.fullmatch(digest)
        ):
            raise _error("REVIEW_SURFACE_OUTPUT_BINDING_INVALID", relative)
        if relative in bindings:
            raise _error("REVIEW_SURFACE_OUTPUT_PATH_DUPLICATED", relative)
        bindings[relative] = item
    return bindings


def _read_bound_resource(
    root: Path,
    relative_path: str,
    binding: Mapping[str, Any],
) -> BoundResource:
    path = root.joinpath(*PurePosixPath(relative_path).parts)
    _assert_existing_path_has_no_reparse(path)
    try:
        resolved = path.resolve(strict=True)
        resolved.relative_to(root)
    except (FileNotFoundError, ValueError) as error:
        raise _error("REVIEW_SURFACE_RESOURCE_ESCAPES_ROOT", relative_path) from error
    if not resolved.is_file():
        raise _error("REVIEW_SURFACE_RESOURCE_NOT_REGULAR_FILE", relative_path)
    try:
        payload = resolved.read_bytes()
    except OSError as error:
        raise _error("REVIEW_SURFACE_RESOURCE_READ_FAILED", relative_path) from error
    digest = sha256(payload).hexdigest()
    if len(payload) != binding["bytes"]:
        raise _error("REVIEW_SURFACE_RESOURCE_BYTE_COUNT_MISMATCH", relative_path)
    if digest != binding["sha256"]:
        raise _error("REVIEW_SURFACE_RESOURCE_SHA256_MISMATCH", relative_path)
    return BoundResource(
        relative_path=relative_path,
        payload=payload,
        sha256=digest,
        content_type=_content_type(relative_path),
    )


def prepare_review_surface(page: Path | str) -> ReviewSurfaceSnapshot:
    """Validate and preload one exact page plus only its referenced resources."""

    supplied_page = Path(page).absolute()
    _assert_existing_path_has_no_reparse(supplied_page)
    if supplied_page.suffix.lower() != ".html" or not supplied_page.is_file():
        raise _error("REVIEW_SURFACE_PAGE_MUST_BE_HTML_FILE", str(supplied_page))
    report_path = supplied_page.with_suffix(".json")
    report, _ = _load_report(report_path)
    root = supplied_page.parent.resolve(strict=True)
    page_path = supplied_page.resolve(strict=True)
    try:
        page_relative = page_path.relative_to(root).as_posix()
    except ValueError as error:
        raise _error("REVIEW_SURFACE_PAGE_ESCAPES_ROOT") from error
    page_relative = _safe_relative_path(
        page_relative,
        code="REVIEW_SURFACE_PAGE_PATH_INVALID",
    )
    _assert_owner_review_report(report, page_relative_path=page_relative)
    bindings = _all_bound_outputs(report, root=root)
    if page_relative not in bindings:
        raise _error("REVIEW_SURFACE_PAGE_NOT_BOUND_BY_REPORT", page_relative)
    page_resource = _read_bound_resource(root, page_relative, bindings[page_relative])
    try:
        html = page_resource.payload.decode("utf-8", errors="strict")
    except UnicodeDecodeError as error:
        raise _error("REVIEW_SURFACE_PAGE_NOT_UTF8", page_relative) from error
    parser = _ReviewReferenceParser(page_relative)
    try:
        parser.feed(html)
        parser.close()
    except ReviewSurfaceError:
        raise
    except Exception as error:
        raise _error("REVIEW_SURFACE_HTML_PARSE_FAILED", page_relative) from error
    resources: dict[str, BoundResource] = {page_relative: page_resource}
    for relative in sorted(parser.references):
        _assert_admissible_referenced_resource(
            relative,
            page_relative_path=page_relative,
        )
        if relative not in bindings:
            raise _error("REVIEW_SURFACE_REFERENCED_RESOURCE_NOT_BOUND", relative)
        resources[relative] = _read_bound_resource(root, relative, bindings[relative])
    return ReviewSurfaceSnapshot(
        page_path=page_path,
        report_path=report_path.resolve(strict=True),
        page_relative_path=page_relative,
        resources=MappingProxyType(resources),
    )


class _LoopbackReviewServer(ThreadingHTTPServer):
    allow_reuse_address = False
    daemon_threads = True
    block_on_close = True


class _ReviewRequestHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def __init__(
        self,
        *args: Any,
        snapshot: ReviewSurfaceSnapshot,
        capability_token: str,
        **kwargs: Any,
    ) -> None:
        self._snapshot = snapshot
        self._capability_token = capability_token
        super().__init__(*args, **kwargs)

    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler contract
        self._serve(include_body=True)

    def do_HEAD(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler contract
        self._serve(include_body=False)

    def do_POST(self) -> None:  # noqa: N802
        self._method_not_allowed()

    def do_PUT(self) -> None:  # noqa: N802
        self._method_not_allowed()

    def do_PATCH(self) -> None:  # noqa: N802
        self._method_not_allowed()

    def do_DELETE(self) -> None:  # noqa: N802
        self._method_not_allowed()

    def do_OPTIONS(self) -> None:  # noqa: N802
        self._method_not_allowed()

    def do_TRACE(self) -> None:  # noqa: N802
        self._method_not_allowed()

    def do_CONNECT(self) -> None:  # noqa: N802
        self._method_not_allowed()

    def send_error(  # type: ignore[override]
        self,
        code: int,
        message: str | None = None,
        explain: str | None = None,
    ) -> None:
        """Replace BaseHTTPRequestHandler's fingerprinting HTML errors."""

        del message, explain
        if code == HTTPStatus.NOT_IMPLEMENTED:
            self._method_not_allowed()
            return
        try:
            status = HTTPStatus(code)
        except ValueError:
            status = HTTPStatus.BAD_REQUEST
        self._status(status, include_body=self.command != "HEAD")

    def log_message(self, format: str, *args: Any) -> None:
        del format, args

    def _expected_host(self) -> str:
        return f"{LOOPBACK_HOST}:{self.server.server_address[1]}"

    def _host_is_valid(self) -> bool:
        values = self.headers.get_all("Host", failobj=[])
        return len(values) == 1 and values[0].strip() == self._expected_host()

    def _resource_for_request(self) -> BoundResource | None:
        parsed = urlsplit(self.path)
        if parsed.scheme or parsed.netloc or parsed.query:
            return None
        prefix = f"/{self._capability_token}/"
        if not parsed.path.startswith(prefix):
            return None
        encoded = parsed.path[len(prefix) :]
        try:
            relative = _decode_url_path(
                encoded,
                code="REVIEW_SURFACE_REQUEST_PATH_INVALID",
            )
        except ReviewSurfaceError:
            return None
        return self._snapshot.resources.get(relative)

    def _serve(self, *, include_body: bool) -> None:
        if not self._host_is_valid():
            self._status(HTTPStatus.BAD_REQUEST, include_body=include_body)
            return
        resource = self._resource_for_request()
        if resource is None:
            self._status(HTTPStatus.NOT_FOUND, include_body=include_body)
            return
        self.send_response_only(HTTPStatus.OK)
        self.send_header("Content-Type", resource.content_type)
        self.send_header("Content-Length", str(len(resource.payload)))
        self.send_header("ETag", f'"sha256-{resource.sha256}"')
        self._security_headers()
        self.end_headers()
        if include_body:
            self.wfile.write(resource.payload)

    def _method_not_allowed(self) -> None:
        content_length = self.headers.get("Content-Length")
        if content_length is not None and content_length.isdecimal():
            byte_count = int(content_length, 10)
            if 0 < byte_count <= MAX_REJECTED_REQUEST_BODY_BYTES:
                self.rfile.read(byte_count)
        self.close_connection = True
        self.send_response_only(HTTPStatus.METHOD_NOT_ALLOWED)
        self.send_header("Allow", "GET, HEAD")
        self.send_header("Connection", "close")
        self.send_header("Content-Length", "0")
        self._security_headers()
        self.end_headers()

    def _status(self, status: HTTPStatus, *, include_body: bool) -> None:
        payload = f"{status.value} {status.phrase}\n".encode("ascii")
        self.send_response_only(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self._security_headers()
        self.end_headers()
        if include_body:
            self.wfile.write(payload)

    def _security_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Security-Policy", _CONTENT_SECURITY_POLICY)
        self.send_header("Cross-Origin-Resource-Policy", "same-origin")
        self.send_header("Permissions-Policy", "camera=(), geolocation=(), microphone=()")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")


def create_review_server(
    snapshot: ReviewSurfaceSnapshot,
    *,
    port: int = DEFAULT_PORT,
    capability_token: str | None = None,
) -> ReviewServerSession:
    """Atomically bind one loopback server without port scanning or fallback."""

    if isinstance(port, bool) or not isinstance(port, int) or not 0 <= port <= 65535:
        raise _error("REVIEW_SURFACE_PORT_INVALID", str(port))
    token = capability_token or secrets.token_urlsafe(CAPABILITY_TOKEN_BYTES)
    if not re.fullmatch(r"[A-Za-z0-9_-]{16,}", token):
        raise _error("REVIEW_SURFACE_CAPABILITY_TOKEN_INVALID")
    handler = partial(
        _ReviewRequestHandler,
        snapshot=snapshot,
        capability_token=token,
    )
    server = _LoopbackReviewServer((LOOPBACK_HOST, port), handler)
    selected_port = server.server_address[1]
    page_url = quote(snapshot.page_relative_path, safe="/")
    url = f"http://{LOOPBACK_HOST}:{selected_port}/{token}/{page_url}"
    return ReviewServerSession(
        server=server,
        url=url,
        capability_token=token,
        snapshot=snapshot,
    )


def _port_argument(value: str) -> int:
    try:
        port = int(value, 10)
    except ValueError as error:
        raise argparse.ArgumentTypeError("port must be an integer from 0 to 65535") from error
    if not 0 <= port <= 65535:
        raise argparse.ArgumentTypeError("port must be an integer from 0 to 65535")
    return port


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Serve one manifest-bound BurnLens review surface only on 127.0.0.1."
        )
    )
    parser.add_argument(
        "--page",
        type=Path,
        required=True,
        help="Exact generated review-surface HTML; its sibling JSON report is required",
    )
    parser.add_argument(
        "--port",
        type=_port_argument,
        default=DEFAULT_PORT,
        help="Loopback TCP port; 0 asks the operating system to select one (default: 0)",
    )
    parser.add_argument(
        "--open-browser",
        action="store_true",
        help="Open the verified localhost URL in the default browser after binding",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        snapshot = prepare_review_surface(args.page)
        session = create_review_server(snapshot, port=args.port)
    except ReviewSurfaceError as error:
        parser.error(str(error))
    except OSError as error:
        print(f"REVIEW_SURFACE_BIND_FAILED={error}", file=sys.stderr)
        return 2

    try:
        print(f"REVIEW_SURFACE_URL={session.url}", flush=True)
        print(f"REVIEW_SURFACE_SHA256={snapshot.page.sha256}", flush=True)
        print(f"REVIEW_SURFACE_RESOURCE_COUNT={len(snapshot.resources)}", flush=True)
        print(f"REVIEW_SURFACE_TOTAL_BYTES={snapshot.total_bytes}", flush=True)
        print("REVIEW_SURFACE_STOP=Ctrl+C", flush=True)
        if args.open_browser:
            try:
                browser_opened = webbrowser.open(session.url, new=2)
            except Exception as error:
                print(
                    f"REVIEW_SURFACE_BROWSER_OPEN_FAILED={error}",
                    file=sys.stderr,
                    flush=True,
                )
                return 2
            if not browser_opened:
                print("REVIEW_SURFACE_BROWSER_OPENED=false", flush=True)
        session.server.serve_forever(poll_interval=0.1)
    except KeyboardInterrupt:
        pass
    finally:
        session.server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
