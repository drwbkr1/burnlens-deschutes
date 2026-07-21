# REGISTRY-2026-044 - Grandview Owner Response Intake Candidate

**Issue / branch:** #517 / `codex/p2o4-t32-grandview-owner-response-intake`

**Lock source:** `6a75065fb1e339d7c26208329ee080129de58803`

**Intake source:** `33e5b02bebf335c5026688a3d2a33ae2d48b8991`

**Candidate artifacts:** `822f13a3d1a845d63e4d2f13dee62627d9a2b240`

**Run:** `BL-2026-07-21-grandview-owner-response-intake-r002`

| Artifact | State | Exact result |
|---|---|---|
| Owner export | Ignored no-overwrite custody | 887 bytes; SHA-256 `41fe9b3fa731a57d65def5d6952ef029a982ed26bcf62b9bf9cfa5d267018585`; 2 yes / 0 no / 0 uncertain |
| Pre-reveal receipt | Ignored no-overwrite custody | 1,835 bytes; SHA-256 `0b2fa3360c5c54f39a5b2623ee0cf8acd0ab13ca76b2ef2ecd704c2a699dfa6a`; decision and note values unread during lock |
| Private r002 reconciliation | Ignored no-overwrite custody | 8,893 bytes; SHA-256 `0a7c1322ff8e9c5983a4baeb6d2cf7d03bd45f77b4926f5d93909c4fb4c74d05` |
| Rejected private r001 reconciliation | Ignored audit custody; never accepted | Source `e4dfc1f9d57fb1e0426382eacd67545ea7967852`; 8,759 bytes; SHA-256 `0dd76a3aa30edd1492fdb92ab28c10a03b3855aa453b62633ae1f4913bf6805d`; no public or label state |
| Public JSON | Release candidate | 9,112 bytes; SHA-256 `2897656ad13164295ad2fda78887d8a41b920dfe73e39c12396e55a034b081b5` |
| Public HTML | Release candidate; manual local render pending | 4,034 bytes; SHA-256 `744c1489021e1967a91756c6042c233694294e4eec6acde398cc8ac826658545` |
| Public PNG | Inspected at original 1600 x 1180 resolution | 89,738 bytes; SHA-256 `ad39379668cc8a8baed49ccc24e25828c4bed1d7dcb915c101112d53b64145e2` |
| Fresh remote-head reconstruction | Passed from response + receipt only | Head `4449f476b31d321d29db64632bc211be813a01e3`; exact private r002 and 3/3 public outputs; required LF files preserved; ignored rebuild leaves a clean checkout |
| Canonical wheel | Two fresh-clone builds pass | Epoch `1784604671`; 630,232 bytes; SHA-256 `3a890e24f44d703f389fdb3840990cd7a728bc45b8c245794979a83c59a313f1`; 145 clean entries; 70 commands |
| Isolated install | Passed | Dependency-complete BurnLens 0.44.0 import from `site-packages`; dependency health and both new CLI help routes pass |
| New prototype labels | Passed candidate gates | 1 burned + 1 background; 50 core pixels / 2.00 ha; 98 one-pixel unknown-ring pixels excluded |
| Cumulative label set | `owner-approved-prototype-region-labels-v0.3.0` | 5 burned + 5 background; 236 core pixels / 9.44 ha; 431 ring pixels excluded; 5 complete event groups |
| Dataset/split/baseline/model | Blocked | Five complete events remain below the required six, and the later sufficiency evaluator still governs all additional class, regime, transfer, and dominance gates |
| Provider/private inputs | Existing ignored custody | Zero provider or owner-response bytes committed; unit decisions and notes remain private |

The automated in-app browser cannot navigate local `file://` URLs under its security policy. The HTML is therefore not release-verified until the owner opens the exact canonical page and confirms the rendered result. No bypass or alternate browser workaround is used.

The rejected r001 run is retained because it exposed substantive gate defects before publication: non-owner gate families were represented as unconditional booleans, accepted-label and rejected-candidate ring semantics were conflated, and event completion could increment when only one class was admitted. The hardened r002 route derives every non-owner gate from exact inputs, counts only accepted-label rings, and requires both burned and background labels before an event is complete.
