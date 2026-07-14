# REGISTRY-2026-004 - Final AOI Artifacts

**Checkpoint:** Issue #321 branch candidate; PR, merge, and tag identity pending

| Artifact | Class | Version/state | Source/analytical bytes |
|---|---|---|---:|
| `NIFC-DARLENE3-PERIMETER-2026-001.geojson` | Immutable official reference snapshot | SHA-256 `3d615d4be88f65806399e3733491ab0d95e16ac91ea86b5a00b3ead81ec17abe` | 47,483 public reference bytes |
| `burnlens/aoi_finalizer.py` | Source validation, projection, AOI derivation, HTML/PNG rendering | BurnLens package `0.2.0`; source commit `bcc1d9aa494c5511ff824692199b40717d320dd4` | No imagery/analytical pixels |
| `burnlens/finalize_aoi.py` | Deterministic AOI CLI | BurnLens package `0.2.0` | No imagery/analytical pixels |
| `tests/test_aoi_finalizer.py` | Unit/integration/contract checks | 8 AOI checks; 16 repository tests passing | No |
| `AOI-FINAL-2026-001.json` | Normalized AOI evidence | SHA-256 `305ddda2eda96fa31e8fb410891d3dc9c0f2b4930af5fc8ee6d2df9bae0b856c` | Derived geometry/metadata only |
| `AOI-FINAL-2026-001.html` | Semantic evidence report | SHA-256 `b45b6659f74249966368e3b2f024363469f88fa6f8f23fc4c1631b39ec009ef2` | Derived geometry/metadata only |
| `AOI-FINAL-2026-001.png` | Rendered evidence map | SHA-256 `73463794d765ca1e19051bb1f5b6dac163c82da5d11a6ea3ca77ce1ea0aeb736` | Derived geometry/metadata only |
| `AOI-2026-002` | Final modeling AOI record | `aoi-darlene3-model-v0.2.0` | Derived geometry only |
| `MANIFEST-2026-004.json` | Checkpoint provenance manifest | Candidate pending shipment identity | No additional source bytes |

The official reference and BurnLens AOI are vector geometry artifacts. They are not imagery, a fire mask, a label, a dataset, a model input, a baseline, a model, a fire detection, a current incident map, or an operational product.
