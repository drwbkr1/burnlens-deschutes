# REGISTRY-2026-001 — P3O1-T01 U01

**Recorded:** 2026-07-25

**Issue:** #566

| Unit / attempt | Exact identity | Gates | Disposition | Next dependency |
|---|---|---|---|---|
| `P3O1-T01-U01-SOURCE-R001` | `MODEL-ENVIRONMENT-SOURCE-GATE-2026-001`; PyPI torch/setuptools; PyTorch/uv docs; GHSA | identity, availability, terms, platform, deterministic limits, security applicability | `pass` | lock |
| `P3O1-T01-U01-VERIFY-R001` | canonical combined wrapper | exceeded 184-second wrapper before aggregate result | `retained-timeout` | bounded reruns |
| `P3O1-T01-U01-VERIFY-R002` | canonical source tree | 3 structural tests; compile; lock; diff | `pass` | model smoke |
| `P3O1-T01-U01-VERIFY-R003` | canonical `.venv`; torch `2.13.0+cpu` | 105/105 commands; CPU/no CUDA; deterministic finite exact synthetic replay | `pass` | implementation commit |
| `P3O1-T01-U01-CODE-R001` | `ddf32dbfee5a29e0fe362859c456e7a362fee20c`; remote-equal branch | pinned model profile; 259,657-byte lock / `87afed69...`; docs/tests | `pass` | detached reconstruction |
| `P3O1-T01-U01-DETACHED-R001` | fresh detached worktree at `ddf32db...`; 28 installed distributions | locked sync; pip check; 105/105 commands; deterministic CPU smoke; clean exact HEAD | `pass` | audit |
| `P3O1-T01-U01-AUDIT-R001` | 28 dependency records | zero torch findings; one disclosed non-applicable-path setuptools finding; one expected editable-project skip | `pass-with-disclosure` | U02 |
| `P3O1-T01-U02-TEST-R001` | first focused reference suite | 10 pass / one brittle module-container assertion failure | `retained-failure` | correct test oracle |
| `P3O1-T01-U02-CODE-R001` | implementation `30503a0...`; cumulative fix `552f47d...` | exact architecture/loader/loss/finite/optimizer/early-stop/checkpoint/test-lock paths; EOF warning corrected | `pass` | detached proof |
| `P3O1-T01-U02-DETACHED-R001` | fresh model profile at `552f47d...` | 28 distributions; 105/105 commands; 24 focused compatibility tests | `pass` | bounded smoke |
| `P3O1-T01-U02-SYNTHETIC-R001` | generated two-example one-step replay | loss `0.6861169338226318`; state `c2402840...` twice exactly | `pass` | real train/validation smoke |
| `P3O1-T01-U02-REAL-R002` | four train / four validation patches; sealed test rejected before `numpy.load` | 109/89 core pixels; finite one-step train and forward-only validation; warnings-as-errors | `pass` | U03 |

U01 opens no dataset array. U02 opens only the permitted train and validation
arrays for a bounded ephemeral smoke; sealed test arrays remain unopened. No
substantive training or promoted model/checkpoint exists. The exact next
eligible unit is `P3O1-T01-U03`.
