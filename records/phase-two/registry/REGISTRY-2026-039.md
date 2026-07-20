# REGISTRY-2026-039 - Grandview Native Source Fitness Candidate

**Issue / branch:** #495 / `codex/p2o4-t27-grandview-source-fitness`

**Contract source:** `a4596661fd2794d67ba3dbd16f6dcf0457bb07b4`

**Generator source:** `527caeb0c83fb70bdd0af37d11a1215914ca0be9`

**Runs:** `BL-2026-07-20-grandview-optical-intake-r001` / `BL-2026-07-20-grandview-source-fitness-r001`

| Artifact | State | Exact result |
|---|---|---|
| Grandview optical package | Ignored exact custody | 2 Sentinel-2B L2A archives; 1,923,481,794 provider bytes; both 109-member SAFE/CRC gates pass |
| Native event evidence | Release candidate | 62,588 full-boundary 20 m pixels; 97.5794% pair eligible; 1.0337% review-needed; 1.3868% excluded |
| Content registration | Passed | 9/9 deterministic windows; p95 0.1158 px; maximum 0.153 px / 3.06 m |
| Continuous dNBR | Evidence only | 61,073 valid pixels; median 0.183221; no threshold, class, or label |
| Official reference pixels | Deferred | BAER `10019092`, MTBS `10023989`, and RAVG `10019464` identities known; no reference pixel opened in this run |
| Candidate/owner/label state | Deferred | Zero Grandview candidate regions, owner decisions, or labels |
| Dataset/split/baseline/model | Blocked | Existing eight prototype regions across four events remain unchanged |
| Provider inputs | Existing ignored custody | 0 provider bytes committed |
