from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_sites_evidence_manifest_binds_exact_tracked_sources() -> None:
    manifest = json.loads(
        (SITE / "public/evidence/manifest.json").read_text(encoding="utf-8")
    )

    assert manifest["manifest_version"] == "burnlens-sites-evidence-manifest-v0.1.0"
    assert manifest["release_version"] == "0.56.0"
    assert len(manifest["entries"]) == 13

    for entry in manifest["entries"]:
        public_path = SITE / entry["public_path"]
        source_path = ROOT / entry["source_path"]
        assert public_path.stat().st_size == entry["bytes"]
        assert source_path.stat().st_size == entry["bytes"]
        assert _sha256(public_path) == entry["sha256"]
        assert _sha256(source_path) == entry["sha256"]


def test_sites_source_preserves_public_claim_and_privacy_boundaries() -> None:
    source = "\n".join(
        [
            (SITE / "app/page.tsx").read_text(encoding="utf-8"),
            (SITE / "app/layout.tsx").read_text(encoding="utf-8"),
            (SITE / "README.md").read_text(encoding="utf-8"),
        ]
    )

    required = [
        "RBR baseline",
        "Bounded U-Net",
        "Rejected",
        "No model superiority",
        "Not official wildfire",
        "Not emergency guidance",
        "Official sources govern",
        "not independent ground truth",
        "v0.56.0-baseline-first-portfolio-release",
        'id="evidence" className="section evidence" tabIndex={-1}',
    ]
    for phrase in required:
        assert phrase in source

    prohibited = [
        "C:\\Users\\",
        "file:///",
        "recipient/retrieval",
        "DPAPI",
    ]
    page_and_layout = "\n".join(
        [
            (SITE / "app/page.tsx").read_text(encoding="utf-8"),
            (SITE / "app/layout.tsx").read_text(encoding="utf-8"),
        ]
    )
    for phrase in prohibited:
        assert phrase not in page_and_layout


def test_sites_project_stays_repository_owned_and_reproducible() -> None:
    package = json.loads((SITE / "package.json").read_text(encoding="utf-8"))
    hosting = json.loads(
        (SITE / ".openai/hosting.json").read_text(encoding="utf-8")
    )

    assert package["name"] == "burnlens-portfolio-site"
    assert package["version"] == "0.56.0"
    assert package["scripts"]["test"].startswith("npm run build")
    assert hosting == {
        "project_id": "appgprj_6a67a02d7c488191b66ced0f2ac3550e",
        "d1": None,
        "r2": None,
    }
    assert not (SITE / "public/favicon.svg").exists()
