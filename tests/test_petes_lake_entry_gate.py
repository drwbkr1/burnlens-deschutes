import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = (
    ROOT
    / "samples"
    / "cross-event"
    / "phase-two"
    / "petes-lake"
    / "PETES-LAKE-ENTRY-GATE-2026-001.json"
)


def load_report() -> dict:
    return json.loads(REPORT_PATH.read_text(encoding="utf-8"))


def test_entry_gate_binds_exact_event_and_optical_pair() -> None:
    report = load_report()

    assert report["report_id"] == "PETES-LAKE-ENTRY-GATE-2026-001"
    assert report["report_schema_version"] == "0.1.0"
    assert report["unit_id"] == "P2O4-T33-U01"
    assert report["run_id"] == "BL-2026-07-21-petes-lake-entry-gate-r003"
    assert report["git_base_commit"] == "0d41942dc6c3c307a9a146a2d38fb816e038bb42"
    assert report["git_source_commit"] == "43635eb20183f49864397f8b74db4f49eb7a3b7e"
    assert report["application_version"] is None

    event = report["event"]
    assert event["event_id"] == "OR4396912190120230825"
    assert event["map_id"] == 10031414
    assert event["portal_catalog_id_frozen"] == 50884
    assert event["portal_catalog_id_current"] == 50890
    assert event["portal_nonstandard"] is False
    assert event["official_comment"] == "Fire severity could be misrepresented in wetland areas."

    products = report["optical_products"]
    assert [item["role"] for item in products] == [
        "petes-lake-2023-pre",
        "petes-lake-2023-post",
    ]
    assert [item["provider_uuid"] for item in products] == [
        "bf275eb0-7e50-4d4d-a01b-fbaaa18e5142",
        "80363c3a-8c04-4ed3-8e2a-d1f35e7a62c6",
    ]
    assert [item["size_bytes"] for item in products] == [1185284273, 1243068088]
    assert sum(item["size_bytes"] for item in products) == 2428352361
    assert all(item["online"] for item in products)
    assert all(item["platform"] == "sentinel-2a" for item in products)
    assert all(item["tile"] == "MGRS-10TEP" for item in products)
    assert all(item["relative_orbit"] == 13 for item in products)
    assert all(item["processing_baseline"] == "05.10" for item in products)


def test_entry_gate_retains_failures_and_limits_the_next_dependency() -> None:
    report = load_report()

    assert [(item["run_id"], item["disposition"]) for item in report["retained_prior_runs"]] == [
        ("BL-2026-07-21-petes-lake-entry-gate-r001", "remediate"),
        ("BL-2026-07-21-petes-lake-live-source-gate-r002", "remediate"),
    ]
    assert report["access"]["token_only_authentication"] == "pass"
    assert report["access"]["credential_or_token_retained"] is False
    assert report["access"]["provider_product_archive_bytes_requested"] == 0
    assert report["official_reference_delivery"]["request_submitted"] is False
    assert (
        report["decision"]
        == "PASS_PETES_LAKE_ENTRY_GATE_AUTHORIZE_SEQUENTIAL_U02_OPTICAL_CUSTODY_ONLY"
    )
    assert report["next_dependency"] == "P2O4-T33-U02"
    assert report["gate_results"]["provider_archive_or_pixel_fitness"] == "not executed; U02-U05"
    assert report["gate_results"]["owner_review"] == "not executed; U09A, U09, and U10"
    assert report["petes_lake_label_set_version"] is None
    assert report["dataset_version"] is None
    assert report["split_version"] is None
    assert report["baseline_version"] is None
    assert report["model_version"] is None


def test_entry_gate_binds_records_custody_and_owner_batch_contract() -> None:
    report = load_report()

    assert report["record_bindings"]["source_records"] == ["SOURCE-2026-028", "SOURCE-2026-029"]
    assert report["record_bindings"]["terms_records"] == ["TERMS-2026-024", "TERMS-2026-025"]
    assert report["record_bindings"]["access_record"] == "ACCESS-2026-018"
    assert report["record_bindings"]["precheck_record"] == "PRECHECK-2026-043"

    custody = report["u02_custody_destinations"]
    assert custody["pre_raw_package"].endswith("petes-lake-s2-optical-pre-v0.1.0")
    assert custody["post_raw_package"].endswith("petes-lake-s2-optical-post-v0.1.0")
    assert "Pre must pass full promotion" in custody["no_overwrite_rule"]

    contract = report["owner_review_batch_contract"]
    assert contract["production_event_group"] == "event-petes-lake-2023"
    assert contract["production_candidate_classes"] == ["burned", "affirmative-background"]
    assert contract["batched_scope"] == "session and response envelope only"
    assert "approve-all" in contract["prohibited"]
    assert "prefilled answers" in contract["prohibited"]
    assert "missing-as-uncertain inference" in contract["prohibited"]
    assert "cross-milestone candidates" in contract["prohibited"]
    assert "distinct valid finals are ambiguous" in contract["custody_and_intake"]
    assert "cannot interrupt U01-U08" in contract["sequencing"]

    for relative_path in (
        "records/phase-two/sources/SOURCE-2026-028.md",
        "records/phase-two/sources/SOURCE-2026-029.md",
        "records/phase-two/terms/TERMS-2026-024.md",
        "records/phase-two/terms/TERMS-2026-025.md",
        "records/phase-two/access/ACCESS-2026-018.md",
        "records/phase-two/prechecks/PRECHECK-2026-043.md",
        "records/phase-two/reviews/SOURCE_PRECEDENCE-2026-018.md",
        "records/phase-two/reviews/USE_BOUNDARY-2026-039.md",
    ):
        assert (ROOT / relative_path).is_file()
