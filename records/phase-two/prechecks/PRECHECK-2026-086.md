# PRECHECK-2026-086 - Replacement six-event dataset sufficiency

**Date:** 2026-07-25  
**Unit / issue:** `P2O4-T39-U08` / #554  
**Final run:** `BL-2026-07-25-replacement-six-event-dataset-sufficiency-r003`  
**Scientific source commit:** `af37f80dd17febacfbb1cf2801665d74edb16475`  
**Disposition:** `pass-training-false`  
**Next dependency:** separate dataset, whole-event split, QA, and baseline milestone

## Exact candidate

The candidate contains only McKay, Tepee, Green Ridge, Grandview, Windigo, and
Ward Creek. Darlene remains immutable historical prototype evidence but is
excluded from this candidate.

The exact inventory is:

- six complete event groups;
- six burned and six background prototype regions;
- 287 accepted native 20-meter core pixels / 11.48 hectares;
- 531 explicit unknown-ring pixels excluded from learning;
- three MTBS-current events;
- three BAER/MTBS/RAVG-current events; and
- three never-tuned transfer events.

No event contributes more than 20.5575 percent of accepted core pixels. The
balanced review roster does not estimate natural class prevalence.

## Readiness and split-fitness result

All ten required non-count gates pass:

- source and terms;
- provenance and custody;
- schema and quality;
- coverage and balance;
- uncertainty and exclusions;
- leakage and split fitness;
- reproducibility;
- evaluation design;
- human review; and
- claims and privacy.

Fifty-four of 90 prospective whole-event 2/2/2 assignments satisfy the frozen
transfer, source-program, and exact source-regime rules. The independent
dataset-readiness utility reproduces the tracked decision byte for byte and
returns `pass` with `training_authorized=false`.

## Retained attempts

R001 used source `2ffeff8af17c122f6f5f84848aac13be360376b6`.
Its candidate and audit were scientifically consistent, but its generated
decision was a project-specific projection instead of the canonical audit
output. All six exact files remain in ignored no-overwrite custody.

| R001 output | Bytes | SHA-256 |
|---|---:|---|
| candidate | 30,504 | `f157e431ffaa4821ca0456b741defbe9a60807c1a671cc2b9c4d66990de3476f` |
| audit | 6,601 | `81c7e68e5430a9ae4cf5c76124c8870c9d757947df60419716255c2f722bcf04` |
| decision | 2,720 | `e32894e9e217ac2b8874adefe1adc71ffb76115964603bf64671f7a2887ca24b` |
| public JSON | 9,429 | `2abda0c62c6184f16bced62cc3655c26797f82fa4f9c446f1dec68513d7edd04` |
| HTML | 6,295 | `d932ca249106b479fda7ff9f4720411ae696f55b9feb9fd6875b8cf5f2a5d16c` |
| PNG | 101,221 | `b20b3852d23185c2e0aa0f9b6cfd462b22eb98dbdbdaad5b8bb9bdeb43977761` |

Commit `a0584f596bd45c34de0c1c59b7097e01b7292779` makes the repository decision
byte-identical to the independent utility. R002 passes the scientific and
audit gates, but real desktop inspection shows vertically wrapped status text.
Its six exact files remain in separate ignored no-overwrite custody.

| R002 output | Bytes | SHA-256 |
|---|---:|---|
| candidate | 30,504 | `9fd159298bad39881df0c1887ca2d58a14afad275f040e49b2f5cddddbdd848c` |
| audit | 6,601 | `bb1dfa534813523d54521d8d198fb1902f8b5661f59245ecf7efeee9d6c7aa82` |
| decision | 7,088 | `a6e29971f38435549c14daf2981a1d160babe87ff79764c3ae115faea1c797f0` |
| public JSON | 9,429 | `0e0bd26080b96b04ded8a0af6eb4e12ce9e4ac3f161efef504e01d24f1a8f734` |
| HTML | 6,295 | `07df24b6b95ace4c2e9929f1feae5c412bfa91bb3a5a513b5359c5c18884d863` |
| PNG | 101,221 | `b20b3852d23185c2e0aa0f9b6cfd462b22eb98dbdbdaad5b8bb9bdeb43977761` |

Commit `af37f80dd17febacfbb1cf2801665d74edb16475` keeps table headings and
status cells legible. R003 reruns the complete evaluator from that clean,
pushed source.

## Accepted r003 outputs

| Output | Bytes | SHA-256 |
|---|---:|---|
| candidate | 30,504 | `4a9646af493cdce81d0cd57405ebccf0dfecf5ca77c96930d0837c3b7d4e65f2` |
| audit | 6,601 | `50e3b9f3c6c33a9f8cd36cf0952bf5033c039e68ffc864bf952ddec5442e6ed4` |
| decision | 7,088 | `39e7a56199f67bcf397b6d73e6795a2e36528ff0577b7314a8414f21321ce5d8` |
| public JSON | 9,429 | `88cbe6ae01af322d7f80ff8a76b3dce698c08b53394a7e68faec2f5cb198ef0a` |
| HTML | 6,357 | `0fbdfd85a8055b2b560c7aac4d35424693ee60761a5f00f6f1b2f804e894c326` |
| PNG | 101,221 | `b20b3852d23185c2e0aa0f9b6cfd462b22eb98dbdbdaad5b8bb9bdeb43977761` |

The independent audit self-test passes. The focused current and historical
sufficiency suites pass 15 tests. Environment profiles pass five tests across
the 99-command roster. Compilation and diff checks pass.

The actual localhost HTML passes default 1280 by 720 and exact 390 by 844
inspection. Desktop and narrow document widths remain inside their viewports.
Cards collapse to one column at 390 pixels. Tables scroll only inside their
containers. Every status stays on one line. Browser warning and error logs are
empty.

## Boundary

This pass authorizes only a separate dataset, whole-event split, QA, and
strongest justified non-model baseline checkpoint. It creates no dataset,
split, baseline, model, metric, training authorization, inference output,
deployment, or external submission.

The prototype regions are not independent ground truth, field validation,
official wildfire information, endorsement, emergency guidance, or
operational evidence. Official sources govern.
