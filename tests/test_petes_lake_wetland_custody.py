from __future__ import annotations

from contextlib import ExitStack, contextmanager, nullcontext
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from burnlens.petes_lake_wetland_custody import (
    CONTRACT_PATH,
    CUSTODY_ROOT,
    DISPATCH_ROOT,
    METADATA_IDENTITIES,
    OFFICIAL_TERMS_PAGES,
    PACKAGE_DIRECTORY,
    PLAN_PATH,
    QUERY_BOUNDS_UTM10N,
    STAGING_ROOT,
    TERMS_REFRESH_PATH,
    WETLAND_FIELDS,
    WETLAND_FIELD_TYPES,
    PetesLakeWetlandCustodyError,
    _NoRedirectHandler,
    _dispatch_receipt_payload,
    _dispatch_receipt_relative_path,
    _normalized_html_text,
    _preflight_initialize,
    _transaction_mutex,
    _validate_count,
    _validate_feature_collection,
    _validate_layer_metadata,
    asset_definitions,
    authorize_contract,
    fetch_asset,
    initialize_contract,
    load_contract,
    promote_asset,
    start_asset,
    verify_asset,
)


class _Response:
    def __init__(
        self,
        data: bytes,
        url: str,
        *,
        content_type: str = "application/json; charset=utf-8",
        status: int = 200,
    ) -> None:
        self._data = data
        self._offset = 0
        self._url = url
        self.status = status
        self.headers = {
            "Content-Length": str(len(data)),
            "Content-Type": content_type,
        }

    def __enter__(self) -> "_Response":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def geturl(self) -> str:
        return self._url

    def read(self, size: int = -1) -> bytes:
        if size < 0:
            size = len(self._data) - self._offset
        result = self._data[self._offset : self._offset + size]
        self._offset += len(result)
        return result


def _metadata() -> dict[str, object]:
    return {
        "name": "Wetlands",
        "type": "Feature Layer",
        "geometryType": "esriGeometryPolygon",
        "maxRecordCount": 1000,
        "fields": [
            {
                "name": name,
                "type": WETLAND_FIELD_TYPES[name.split(".")[-1]],
                "domain": None,
            }
            for name in WETLAND_FIELDS
        ],
    }


def _write_private_state(path: Path, state: dict[str, object], **_kwargs: object) -> None:
    if path.exists():
        raise RuntimeError("test private state overwrite")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(state, indent=2) + "\n").encode("utf-8"))


def _clock(start: str = "2026-07-21T23:00:00Z"):
    current = datetime.fromisoformat(start.replace("Z", "+00:00"))

    def now() -> str:
        nonlocal current
        current += timedelta(seconds=1)
        return current.astimezone(timezone.utc).isoformat(timespec="microseconds").replace(
            "+00:00", "Z"
        )

    return now


def _terms_html(page: dict[str, object]) -> bytes:
    fragments = " | ".join(str(item) for item in page["semantic_fragments"])
    return f"<!doctype html><html><body>{fragments}</body></html>".encode("utf-8")


def _terms_provider(request: object, **_kwargs: object) -> _Response:
    url = str(getattr(request, "full_url"))
    page = next(item for item in OFFICIAL_TERMS_PAGES if item["uri"] == url)
    return _Response(_terms_html(page), url, content_type="text/html; charset=UTF-8")


@contextmanager
def _state_machine_patches(identity: dict[str, object]):
    with ExitStack() as stack:
        stack.enter_context(
            patch(
                "burnlens.petes_lake_wetland_custody.METADATA_IDENTITIES",
                {"wetlands": identity, "source": identity},
            )
        )
        stack.enter_context(
            patch(
                "burnlens.petes_lake_wetland_custody._transaction_mutex",
                side_effect=lambda _root: nullcontext(),
            )
        )
        for symbol in (
            "_preflight_initialize",
            "_verify_mutation_context",
            "_verify_tracked_gate_records",
            "_assert_ignored_untracked",
        ):
            stack.enter_context(
                patch(f"burnlens.petes_lake_wetland_custody.{symbol}")
            )
        stack.enter_context(
            patch(
                "burnlens.petes_lake_wetland_custody.write_private_state",
                side_effect=_write_private_state,
            )
        )
        yield


def _initialize(root: Path, identity: dict[str, object]) -> None:
    initialize_contract(
        root,
        created_at_utc="2026-07-21T23:00:00Z",
        git_source_commit="a" * 40,
    )
    authorize_contract(root, terms_open_fn=_terms_provider, now_fn=_clock())


class PetesLakeWetlandCustodyTests(unittest.TestCase):
    def test_terms_semantics_must_be_visible_not_script_only(self) -> None:
        text = _normalized_html_text(
            b"<html><body>visible boundary<script>hidden permission phrase</script>"
            b"<style>.x{content:'hidden style phrase'}</style></body></html>"
        )
        self.assertIn("visible boundary", text)
        self.assertNotIn("hidden permission phrase", text)
        self.assertNotIn("hidden style phrase", text)

    def test_authorization_refreshes_exact_live_terms_semantics_without_snapshot_hashes(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".git").mkdir()
            (root / "pyproject.toml").write_text("[project]\n", encoding="utf-8")
            data = json.dumps(_metadata()).encode("utf-8")
            identity = {"bytes": len(data), "sha256": sha256(data).hexdigest()}
            with _state_machine_patches(identity):
                _initialize(root, identity)
                _path, contract = load_contract(root)
                refresh = contract["extensions"]["terms_refresh"]
                self.assertEqual(refresh["state"], "passed")
                self.assertFalse(refresh["automatic_retry"])
                self.assertEqual(
                    [item["page_id"] for item in refresh["observations"]],
                    [item["page_id"] for item in OFFICIAL_TERMS_PAGES],
                )
                for page, observation in zip(
                    OFFICIAL_TERMS_PAGES, refresh["observations"], strict=True
                ):
                    current = _terms_html(page)
                    self.assertEqual(observation["bytes"], len(current))
                    self.assertEqual(observation["sha256"], sha256(current).hexdigest())
                    self.assertEqual(observation["requested_url"], page["uri"])
                    self.assertEqual(observation["final_url"], page["uri"])
                receipt_path = root / TERMS_REFRESH_PATH
                receipt_bytes = receipt_path.read_bytes()
                self.assertEqual(refresh["receipt"]["path"], TERMS_REFRESH_PATH.as_posix())
                self.assertEqual(refresh["receipt"]["bytes"], len(receipt_bytes))
                self.assertEqual(
                    refresh["receipt"]["sha256"], sha256(receipt_bytes).hexdigest()
                )
                receipt = json.loads(receipt_bytes)
                self.assertEqual(
                    receipt["decision"],
                    "PASS_CURRENT_OFFICIAL_NWI_TERMS_SEMANTICS_FOR_BOUNDED_PROVIDER_INTAKE",
                )
                self.assertFalse(receipt["provider_data_requests_created"])

    def test_redirect_is_refused_and_terms_attempt_is_one_shot(self) -> None:
        handler = _NoRedirectHandler()
        self.assertIsNone(
            handler.redirect_request(None, None, 302, "Found", {}, "https://example.invalid/")
        )
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".git").mkdir()
            (root / "pyproject.toml").write_text("[project]\n", encoding="utf-8")
            data = json.dumps(_metadata()).encode("utf-8")
            identity = {"bytes": len(data), "sha256": sha256(data).hexdigest()}
            with _state_machine_patches(identity):
                initialize_contract(
                    root,
                    created_at_utc="2026-07-21T23:00:00Z",
                    git_source_commit="a" * 40,
                )
                calls = {"redirect": 0, "retry": 0}

                def redirect(request: object, **_kwargs: object) -> _Response:
                    calls["redirect"] += 1
                    url = str(getattr(request, "full_url"))
                    return _Response(
                        b"<html>redirect</html>",
                        url,
                        content_type="text/html",
                        status=302,
                    )

                with self.assertRaisesRegex(PetesLakeWetlandCustodyError, "without retry"):
                    authorize_contract(root, terms_open_fn=redirect, now_fn=_clock())
                self.assertEqual(calls["redirect"], 1)
                _path, failed = load_contract(root)
                self.assertEqual(failed["extensions"]["terms_refresh"]["state"], "failed")
                self.assertTrue(all(item["state"] == "planned" for item in failed["assets"]))

                def forbidden(*_args: object, **_kwargs: object) -> _Response:
                    calls["retry"] += 1
                    raise AssertionError("one-shot refresh unexpectedly retried")

                with self.assertRaisesRegex(PetesLakeWetlandCustodyError, "one-shot"):
                    authorize_contract(root, terms_open_fn=forbidden, now_fn=_clock())
                self.assertEqual(calls["retry"], 0)

    def test_initialize_rejects_wrong_origin_before_remote_probe(self) -> None:
        root = Path("C:/synthetic/burnlens-deschutes")
        context = {"branch": "codex/p2o4-t33-petes-lake-milestone", "head": "a" * 40}
        calls: list[tuple[str, ...]] = []

        def git(_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
            calls.append(args)
            if args == ("config", "--get", "remote.origin.url"):
                return subprocess.CompletedProcess(
                    ["git", *args], 0, "https://github.com/drwbkr1/burnlens-site.git\n", ""
                )
            raise AssertionError("remote probe must not run after wrong origin")

        with patch(
            "burnlens.petes_lake_wetland_custody._git_context", return_value=context
        ), patch("burnlens.petes_lake_wetland_custody._run_git", side_effect=git):
            with self.assertRaisesRegex(PetesLakeWetlandCustodyError, "exact drwbkr1"):
                _preflight_initialize(root, "a" * 40)
        self.assertEqual(calls, [("config", "--get", "remote.origin.url")])

    def test_query_is_exact_public_https_and_includes_context_halo(self) -> None:
        definitions = {item["asset_id"]: item for item in asset_definitions()}
        url = definitions["wetlands-features"]["uri"]
        self.assertTrue(url.startswith("https://fwspublicservices.wim.usgs.gov/"))
        body = definitions["wetlands-features"]["body"].decode("ascii")
        for value in QUERY_BOUNDS_UTM10N:
            self.assertIn(str(value), body)
        self.assertIn("outSR=3857", body)
        self.assertIn("returnGeometry=true", body)
        self.assertIn("returnTrueCurves=true", body)
        self.assertNotIn("token", (url + body).casefold())

    def test_layer_metadata_requires_exact_polygon_field_types(self) -> None:
        payload = _metadata()
        result = _validate_layer_metadata(payload, layer="wetlands")
        self.assertEqual(result["max_record_count"], 1000)
        changed = dict(payload, geometryType="esriGeometryPoint")
        with self.assertRaisesRegex(PetesLakeWetlandCustodyError, "geometry"):
            _validate_layer_metadata(changed, layer="wetlands")
        wrong_type = json.loads(json.dumps(payload))
        wrong_type["fields"][0]["type"] = "esriFieldTypeString"
        with self.assertRaisesRegex(PetesLakeWetlandCustodyError, "field type"):
            _validate_layer_metadata(wrong_type, layer="wetlands")

    def test_feature_geometry_is_finite_closed_exact_2d_and_clockwise(self) -> None:
        self.assertEqual(_validate_count({"count": 2}), 2)
        with self.assertRaises(PetesLakeWetlandCustodyError):
            _validate_count({"count": -1})
        feature = {
            "geometry": {
                "rings": [[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]]
            },
            "attributes": {
                "OBJECTID": 1,
                "GLOBALID": "{EXAMPLE}",
                "ATTRIBUTE": "PSS1C",
                "WETLAND_TYPE": "Freshwater Forested/Shrub Wetland",
                "ACRES": 2.5,
                "Shape_Length": 5.0,
                "Shape_Area": 1.0,
            },
        }
        payload = {
            "geometryType": "esriGeometryPolygon",
            "spatialReference": {"wkid": 102100, "latestWkid": 3857},
            "features": [feature],
        }
        result = _validate_feature_collection(payload, layer="wetlands")
        self.assertEqual(result["feature_count"], 1)
        malformed = json.loads(json.dumps(payload))
        malformed["features"][0]["geometry"]["rings"][0][0] = [0, 0, 9]
        with self.assertRaisesRegex(PetesLakeWetlandCustodyError, "exact 2D"):
            _validate_feature_collection(malformed, layer="wetlands")
        duplicate = dict(payload, features=[feature, feature])
        with self.assertRaisesRegex(PetesLakeWetlandCustodyError, "duplicated"):
            _validate_feature_collection(duplicate, layer="wetlands")

    def test_state_machine_reserves_before_provider_and_promotes_exact_bytes(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".git").mkdir()
            (root / "pyproject.toml").write_text("[project]\n", encoding="utf-8")
            data = json.dumps(_metadata()).encode("utf-8")
            identity = {"bytes": len(data), "sha256": sha256(data).hexdigest()}
            with _state_machine_patches(identity):
                _initialize(root, identity)
                asset_id = "wetlands-layer-metadata"
                start_asset(
                    root,
                    asset_id=asset_id,
                    started_at_utc="2026-07-21T23:01:00Z",
                )
                uri = next(
                    item["uri"]
                    for item in asset_definitions()
                    if item["asset_id"] == asset_id
                )
                provider_observed = {"called": 0}

                def provider(*_args: object, **_kwargs: object) -> _Response:
                    provider_observed["called"] += 1
                    reservation = (
                        root
                        / STAGING_ROOT
                        / "wetlands-layer-metadata.json.partial"
                    )
                    self.assertTrue(reservation.is_file())
                    self.assertEqual(reservation.stat().st_size, 0)
                    _path, active = load_contract(root)
                    attempt = active["assets"][0]["attempts"][0]
                    self.assertIsNotNone(attempt["dispatch_receipt_sha256"])
                    return _Response(data, uri, content_type="text/plain; charset=UTF-8")

                fetch_asset(
                    root,
                    asset_id=asset_id,
                    request_dispatched_at_utc="2026-07-21T23:02:00Z",
                    urlopen_fn=provider,
                    now_fn=lambda: "2026-07-21T23:03:00Z",
                )
                self.assertEqual(provider_observed["called"], 1)
                verify_asset(root, asset_id=asset_id)
                promoted = promote_asset(root, asset_id=asset_id)
                destination = root / "downloads/phase-two/raw" / promoted[
                    "destination_relative_path"
                ]
                self.assertEqual(destination.read_bytes(), data)
                self.assertEqual(destination.stat().st_nlink, 1)

    def test_destination_inserted_after_start_blocks_before_provider(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".git").mkdir()
            (root / "pyproject.toml").write_text("[project]\n", encoding="utf-8")
            data = json.dumps(_metadata()).encode("utf-8")
            identity = {"bytes": len(data), "sha256": sha256(data).hexdigest()}
            with _state_machine_patches(identity):
                _initialize(root, identity)
                asset_id = "wetlands-layer-metadata"
                start_asset(
                    root,
                    asset_id=asset_id,
                    started_at_utc="2026-07-21T23:01:00Z",
                )
                destination = (
                    root
                    / CUSTODY_ROOT
                    / PACKAGE_DIRECTORY
                    / "wetlands-layer-metadata.json"
                )
                destination.parent.mkdir(parents=True)
                destination.write_bytes(b"collision")
                calls = {"count": 0}

                def forbidden(*_args: object, **_kwargs: object) -> _Response:
                    calls["count"] += 1
                    raise AssertionError("provider called after destination collision")

                with self.assertRaisesRegex(PetesLakeWetlandCustodyError, "without retry"):
                    fetch_asset(
                        root,
                        asset_id=asset_id,
                        request_dispatched_at_utc="2026-07-21T23:02:00Z",
                        urlopen_fn=forbidden,
                    )
                self.assertEqual(calls["count"], 0)
                _path, failed = load_contract(root)
                self.assertEqual(
                    failed["assets"][0]["failure"]["stage"],
                    "PRE_DISPATCH_FILESYSTEM",
                )

    def test_prior_promoted_identity_drift_blocks_next_provider_dispatch(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".git").mkdir()
            (root / "pyproject.toml").write_text("[project]\n", encoding="utf-8")
            data = json.dumps(_metadata()).encode("utf-8")
            identity = {"bytes": len(data), "sha256": sha256(data).hexdigest()}
            with _state_machine_patches(identity):
                _initialize(root, identity)
                first = "wetlands-layer-metadata"
                start_asset(root, asset_id=first, started_at_utc="2026-07-21T23:01:00Z")
                uri = asset_definitions()[0]["uri"]
                fetch_asset(
                    root,
                    asset_id=first,
                    request_dispatched_at_utc="2026-07-21T23:02:00Z",
                    urlopen_fn=lambda *_args, **_kwargs: _Response(data, uri),
                    now_fn=lambda: "2026-07-21T23:03:00Z",
                )
                verify_asset(root, asset_id=first)
                promoted = promote_asset(root, asset_id=first)
                second = "wetlands-pre-count"
                start_asset(root, asset_id=second, started_at_utc="2026-07-21T23:04:00Z")
                destination = root / CUSTODY_ROOT / promoted["destination_relative_path"]
                destination.write_bytes(b"tampered prior response")
                calls = {"count": 0}

                def forbidden(*_args: object, **_kwargs: object) -> _Response:
                    calls["count"] += 1
                    raise AssertionError("provider called after prior-response drift")

                with self.assertRaisesRegex(PetesLakeWetlandCustodyError, "without retry"):
                    fetch_asset(
                        root,
                        asset_id=second,
                        request_dispatched_at_utc="2026-07-21T23:05:00Z",
                        urlopen_fn=forbidden,
                    )
                self.assertEqual(calls["count"], 0)
                _path, failed = load_contract(root)
                self.assertEqual(
                    failed["assets"][1]["failure"]["stage"],
                    "PRE_DISPATCH_FILESYSTEM",
                )

    def test_multilink_reservation_and_extra_raw_roster_fail_before_provider(self) -> None:
        for mode in ("multilink", "extra-raw"):
            with self.subTest(mode=mode), TemporaryDirectory() as directory:
                root = Path(directory)
                (root / ".git").mkdir()
                (root / "pyproject.toml").write_text("[project]\n", encoding="utf-8")
                data = json.dumps(_metadata()).encode("utf-8")
                identity = {"bytes": len(data), "sha256": sha256(data).hexdigest()}
                with _state_machine_patches(identity):
                    _initialize(root, identity)
                    asset_id = "wetlands-layer-metadata"
                    if mode == "extra-raw":
                        package = root / CUSTODY_ROOT / PACKAGE_DIRECTORY
                        package.mkdir(parents=True)
                        (package / "extra.json").write_bytes(b"extra")
                        with self.assertRaisesRegex(PetesLakeWetlandCustodyError, "raw package"):
                            start_asset(
                                root,
                                asset_id=asset_id,
                                started_at_utc="2026-07-21T23:01:00Z",
                            )
                        continue
                    start_asset(
                        root,
                        asset_id=asset_id,
                        started_at_utc="2026-07-21T23:01:00Z",
                    )
                    reservation = (
                        root / STAGING_ROOT / "wetlands-layer-metadata.json.partial"
                    )
                    reservation.parent.mkdir(parents=True)
                    reservation.write_bytes(b"")
                    os.link(reservation, root / "reservation-second-link")
                    calls = {"count": 0}

                    def forbidden(*_args: object, **_kwargs: object) -> _Response:
                        calls["count"] += 1
                        raise AssertionError("provider called after multilink reservation")

                    with self.assertRaisesRegex(PetesLakeWetlandCustodyError, "without retry"):
                        fetch_asset(
                            root,
                            asset_id=asset_id,
                            request_dispatched_at_utc="2026-07-21T23:02:00Z",
                            urlopen_fn=forbidden,
                        )
                    self.assertEqual(calls["count"], 0)

    def test_out_of_order_and_retrograde_start_fail_before_provider(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".git").mkdir()
            (root / "pyproject.toml").write_text("[project]\n", encoding="utf-8")
            data = json.dumps(_metadata()).encode("utf-8")
            identity = {"bytes": len(data), "sha256": sha256(data).hexdigest()}
            with _state_machine_patches(identity):
                _initialize(root, identity)
                with self.assertRaisesRegex(PetesLakeWetlandCustodyError, "prerequisites"):
                    start_asset(
                        root,
                        asset_id="wetlands-pre-count",
                        started_at_utc="2026-07-21T23:01:00Z",
                    )
                with self.assertRaisesRegex(PetesLakeWetlandCustodyError, "timestamp"):
                    start_asset(
                        root,
                        asset_id="wetlands-layer-metadata",
                        started_at_utc="2026-07-21T23:00:00Z",
                    )

    def test_tampered_static_field_and_duplicate_roster_fail_on_load(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".git").mkdir()
            (root / "pyproject.toml").write_text("[project]\n", encoding="utf-8")
            data = json.dumps(_metadata()).encode("utf-8")
            identity = {"bytes": len(data), "sha256": sha256(data).hexdigest()}
            with _state_machine_patches(identity):
                initialize_contract(
                    root,
                    created_at_utc="2026-07-21T23:00:00Z",
                    git_source_commit="a" * 40,
                )
                contract_path = root / CONTRACT_PATH
                original = json.loads(contract_path.read_bytes())
                tampered = json.loads(json.dumps(original))
                tampered["assets"][0]["expected"]["sha256"] = "b" * 64
                contract_path.write_bytes(
                    (json.dumps(tampered, indent=2) + "\n").encode("utf-8")
                )
                with self.assertRaisesRegex(PetesLakeWetlandCustodyError, "immutable"):
                    load_contract(root)
                duplicate = json.loads(json.dumps(original))
                duplicate["assets"].append(duplicate["assets"][0])
                contract_path.write_bytes(
                    (json.dumps(duplicate, indent=2) + "\n").encode("utf-8")
                )
                with self.assertRaisesRegex(PetesLakeWetlandCustodyError, "roster"):
                    load_contract(root)

    def test_missing_or_tampered_plan_and_receipt_without_marker_fail_closed(self) -> None:
        for mode in ("missing-plan", "tampered-plan", "receipt-without-marker"):
            with self.subTest(mode=mode), TemporaryDirectory() as directory:
                root = Path(directory)
                (root / ".git").mkdir()
                (root / "pyproject.toml").write_text("[project]\n", encoding="utf-8")
                data = json.dumps(_metadata()).encode("utf-8")
                identity = {"bytes": len(data), "sha256": sha256(data).hexdigest()}
                with _state_machine_patches(identity):
                    _initialize(root, identity)
                    plan = root / PLAN_PATH
                    if mode == "missing-plan":
                        plan.unlink()
                        with self.assertRaisesRegex(PetesLakeWetlandCustodyError, "plan receipt"):
                            load_contract(root)
                        continue
                    if mode == "tampered-plan":
                        plan.write_bytes(plan.read_bytes() + b" ")
                        with self.assertRaisesRegex(PetesLakeWetlandCustodyError, "identity"):
                            load_contract(root)
                        continue
                    asset_id = "wetlands-layer-metadata"
                    start_asset(
                        root,
                        asset_id=asset_id,
                        started_at_utc="2026-07-21T23:01:00Z",
                    )
                    _path, contract = load_contract(root)
                    asset = contract["assets"][0]
                    definition = asset_definitions()[0]
                    receipt = _dispatch_receipt_payload(
                        contract,
                        asset,
                        definition,
                        "2026-07-21T23:02:00Z",
                    )
                    receipt_path = root / _dispatch_receipt_relative_path(asset_id)
                    _write_private_state(receipt_path, receipt)
                    self.assertTrue(receipt_path.is_relative_to(root / DISPATCH_ROOT))
                    with self.assertRaisesRegex(
                        PetesLakeWetlandCustodyError, "without a durable contract dispatch marker"
                    ):
                        load_contract(root)

    def test_wrong_media_type_is_terminal_and_never_retried(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".git").mkdir()
            (root / "pyproject.toml").write_text("[project]\n", encoding="utf-8")
            data = json.dumps(_metadata()).encode("utf-8")
            identity = {"bytes": len(data), "sha256": sha256(data).hexdigest()}
            with _state_machine_patches(identity):
                _initialize(root, identity)
                asset_id = "wetlands-layer-metadata"
                start_asset(
                    root,
                    asset_id=asset_id,
                    started_at_utc="2026-07-21T23:01:00Z",
                )
                uri = asset_definitions()[0]["uri"]
                with self.assertRaisesRegex(PetesLakeWetlandCustodyError, "without retry"):
                    fetch_asset(
                        root,
                        asset_id=asset_id,
                        request_dispatched_at_utc="2026-07-21T23:02:00Z",
                        urlopen_fn=lambda *_args, **_kwargs: _Response(
                            data, uri, content_type="text/html"
                        ),
                        now_fn=lambda: "2026-07-21T23:03:00Z",
                    )
                calls = {"count": 0}

                def forbidden(*_args: object, **_kwargs: object) -> _Response:
                    calls["count"] += 1
                    return _Response(data, uri)

                with self.assertRaises(PetesLakeWetlandCustodyError):
                    fetch_asset(
                        root,
                        asset_id=asset_id,
                        request_dispatched_at_utc="2026-07-21T23:04:00Z",
                        urlopen_fn=forbidden,
                    )
                self.assertEqual(calls["count"], 0)

    def test_partial_transfer_records_exact_retained_hash_and_failure_stage(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".git").mkdir()
            (root / "pyproject.toml").write_text("[project]\n", encoding="utf-8")
            complete = json.dumps(_metadata()).encode("utf-8")
            identity = {"bytes": len(complete), "sha256": sha256(complete).hexdigest()}
            partial = b'{"name":"Wetlands"'

            class PartialResponse(_Response):
                def __init__(self, url: str) -> None:
                    super().__init__(complete, url)
                    self._reads = 0

                def read(self, size: int = -1) -> bytes:
                    self._reads += 1
                    if self._reads == 1:
                        return partial
                    raise OSError("synthetic interrupted response")

            with _state_machine_patches(identity):
                _initialize(root, identity)
                asset_id = "wetlands-layer-metadata"
                start_asset(
                    root,
                    asset_id=asset_id,
                    started_at_utc="2026-07-21T23:01:00Z",
                )
                uri = asset_definitions()[0]["uri"]
                with self.assertRaisesRegex(PetesLakeWetlandCustodyError, "without retry"):
                    fetch_asset(
                        root,
                        asset_id=asset_id,
                        request_dispatched_at_utc="2026-07-21T23:02:00Z",
                        urlopen_fn=lambda *_args, **_kwargs: PartialResponse(uri),
                        now_fn=lambda: "2026-07-21T23:03:00Z",
                    )
                _path, contract = load_contract(root)
                failed = contract["assets"][0]
                self.assertEqual(failed["state"], "failed")
                self.assertEqual(failed["failure"]["stage"], "RESPONSE_BODY")
                retained = failed["failure"]["retained_staging"]
                self.assertEqual(retained["status"], "exact")
                self.assertEqual(retained["size_bytes"], len(partial))
                self.assertEqual(retained["sha256"], sha256(partial).hexdigest())
                self.assertTrue(all(value is None for value in failed["observed"].values()))

    def test_provider_redirect_response_is_terminal_with_no_follow_or_retry(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".git").mkdir()
            (root / "pyproject.toml").write_text("[project]\n", encoding="utf-8")
            data = json.dumps(_metadata()).encode("utf-8")
            identity = {"bytes": len(data), "sha256": sha256(data).hexdigest()}
            with _state_machine_patches(identity):
                _initialize(root, identity)
                asset_id = "wetlands-layer-metadata"
                start_asset(
                    root,
                    asset_id=asset_id,
                    started_at_utc="2026-07-21T23:01:00Z",
                )
                uri = asset_definitions()[0]["uri"]
                calls = {"initial": 0, "follow": 0}

                def redirect(*_args: object, **_kwargs: object) -> _Response:
                    calls["initial"] += 1
                    return _Response(data, uri, status=302)

                with self.assertRaisesRegex(PetesLakeWetlandCustodyError, "without retry"):
                    fetch_asset(
                        root,
                        asset_id=asset_id,
                        request_dispatched_at_utc="2026-07-21T23:02:00Z",
                        urlopen_fn=redirect,
                        now_fn=lambda: "2026-07-21T23:03:00Z",
                    )
                self.assertEqual(calls, {"initial": 1, "follow": 0})

                def forbidden(*_args: object, **_kwargs: object) -> _Response:
                    calls["follow"] += 1
                    raise AssertionError("terminal redirect unexpectedly retried")

                with self.assertRaises(PetesLakeWetlandCustodyError):
                    fetch_asset(
                        root,
                        asset_id=asset_id,
                        request_dispatched_at_utc="2026-07-21T23:04:00Z",
                        urlopen_fn=forbidden,
                    )
                self.assertEqual(calls, {"initial": 1, "follow": 0})

    def test_real_mutex_rejects_concurrent_holder(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            (root / "pyproject.toml").write_text("[project]\n", encoding="utf-8")
            (root / ".gitignore").write_text("downloads/\n", encoding="utf-8")
            with _transaction_mutex(root):
                with self.assertRaisesRegex(
                    PetesLakeWetlandCustodyError, "another NWI custody mutation"
                ):
                    with _transaction_mutex(root):
                        self.fail("second mutex unexpectedly acquired")


if __name__ == "__main__":
    unittest.main()
