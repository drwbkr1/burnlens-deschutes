# REGISTRY-2026-001 — P3O1-T01 milestone

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
| `P3O1-T01-U03-TEST-R001` | first frozen-protocol suite | 15 pass / one brittle equivalent-prose assertion failure | `retained-failure` | correct test oracle |
| `P3O1-T01-U03-CODE-R001` | `fbb2e923ae7f9ca9ed7dbb317e4235a236ae2411`; remote-equal branch | exact protocol, preflight, render, and authorization-bound one-opening mechanism | `pass` | production preflight |
| `P3O1-T01-U03-PREFLIGHT-R001` | `BL-2026-07-25-p3o1-t01-u03-preflight-r001` | two train/validation epochs; 109/89 cores; finite; no weights/checkpoint; test unopened | `pass-preflight-not-model` | render |
| `P3O1-T01-U03-RENDER-R001` | exact 3,544-byte HTML and 77,226-byte PNG | desktop/narrow layout; complete image; two rows; no external resources/logs; visible boundaries | `pass-with-tool-limit` | detached replay |
| `P3O1-T01-U03-DETACHED-R001` | fresh detached worktree at `fbb2e92...` | exact four-artifact replay; 28 focused tests; compile; lock; diff | `pass` | U04 |
| `P3O1-T01-U04-TEST-R001` | first focused training suite | 24 pass / two stale synthetic-fixture failures / three stale editable-install failures | `retained-failure` | correct fixtures and resync exact lock |
| `P3O1-T01-U04-CODE-R001` | `5179a745f091c29d095461d511633f055967ef91`; remote-equal branch | frozen-protocol training harness, append-only epochs, atomic candidate, rendered diagnostics | `pass` | detached proof |
| `P3O1-T01-U04-DETACHED-R001` | fresh model profile at `5179a745...` | 28 distributions; 107/107 commands; deterministic CPU smoke; 35 focused tests; compile/lock/diff/real-entry | `pass` | substantive run |
| `P3O1-T01-U04-TRAINING-R001` | `BL-2026-07-25-p3o1-t01-u04-training-r001`; 43 ignored files / 3,592,037 bytes; inventory `e260d8b9...` | one 35-epoch run; epoch 10 selected from validation; append-only custody; test unopened | `pass-candidate-frozen` | independent verification |
| `P3O1-T01-U04-CANDIDATE-VERIFY-R001` | nine candidate artifacts; weights `703d9257...`; selection `6dcae9af...` | exact receipts; history/selection/stopping recomputation; checkpoints reload; no test request | `pass` | render |
| `P3O1-T01-U04-RENDER-R001` | exact 8,176-byte HTML and 80,920-byte PNG | desktop/narrow layout; complete chart; 35 rows; contained table overflow; no external resources/logs; visible boundaries | `pass-with-tool-limit` | commit and push U04 evidence |
| `P3O1-T01-U05-TEST-R001` | first evaluator suite | collection failure from wrong environment-path import; zero tests and zero array access | `retained-failure` | correct import |
| `P3O1-T01-U05-PREFLIGHT-R001-R003` | validation-only renderer rehearsals | retained narrow overflow, PNG annotation overlap, and false test-opening wording; test open-count zero | `retained-render-failures` | correct before freeze |
| `P3O1-T01-U05-CODE-R001` | `aa6b7f385224943a4550657318117dbec1b038c2`; remote-equal branch | exact roster enforcement; candidate/clean-HEAD/unused-opening gates; complete metrics, arrays, render, and no-retry paths | `pass` | exact preflight |
| `P3O1-T01-U05-PREFLIGHT-R005` | `BL-2026-07-25-p3o1-t01-u05-preflight-r005`; validation only | 39 focused tests; compile/lock/diff; desktop/narrow render; three-artifact exact replay; test open-count zero | `pass-preopen` | authorization |
| `P3O1-T01-U05-AUTH-R001` | `4f71ec7c61ac0ca1b1dcfcd995d1444c9ec00c9e`; authorization `8e0e6442...` | exact config/weights/selection/environment/event/ordered-patch bindings; `AUTHORIZED_NOT_OPENED`; remote-equal clean HEAD | `pass-authorization` | one opening |
| `P3O1-T01-U05-TEST-R001` | `BL-2026-07-25-p3o1-t01-u05-test-r001`; opening consumed 0→1 | 89 cores; finite; all predicted burned; macro Dice `0.29874213836477986`; RBR `1.0`; no tuning/retry | `pass-evaluation-reject-analytical-winner` | independent verification |
| `P3O1-T01-U05-VERIFY-R001` | first inventory verifier | unavailable `System.Convert.ToHexString`; no output change | `retained-tool-failure` | compatible verifier |
| `P3O1-T01-U05-VERIFY-R002` | 12 outputs / 340,542 bytes / inventory `f850ed08...` | receipts/promotion/array schema/threshold predictions/denominators/baseline comparison | `pass` | render |
| `P3O1-T01-U05-RENDER-R001` | exact 7,022-byte HTML and 217,578-byte PNG | desktop/narrow layout; complete four-patch geospatial evidence; contained tables; no external resources; visible boundaries | `pass` | U06 |

U01 opens no dataset array. U02 and U03 use only train/validation arrays for
bounded smoke evidence. U04 performs the one authorized substantive
train/validation experiment and freezes a validation-only candidate. U05 then
consumes the single Ward Creek/Windigo opening. The candidate predicts all 89
selected test cores as burned and is rejected as the analytical winner against
perfect RBR. It remains a valid evaluated but unaccepted branch candidate. No
second test opening, inference, deployment, or final model decision exists.
The exact next eligible unit is `P3O1-T01-U06`.
