# REGISTRY-2026-084 - P2O5-T03 U01 dataset contract

**Recorded:** 2026-07-25

**Issue:** #562

**Branch:** `codex/p2o5-t03-dataset-split-baselines`

| Unit | Run / source | Inputs | Outputs | Gates | Disposition | Next dependency |
|---|---|---|---|---|---|---|
| `P2O5-T03-U01-R001` | local precommit contract exercise | exact v0.51 candidate and prior readiness | temporary untracked contract/audit/decision | focused contract and readiness utility pass; source identity not yet committed | `superseded-before-record` | commit implementation |
| `P2O5-T03-U01-R002` | `BL-2026-07-25-p2o5-t03-u01-dataset-contract-r002`; source `0a1d533...` | candidate `4a9646af...`; prior audit `50e3b9f3...`; every bound proposal/intake/source/terms/raster; six optical report lineages | contract 29,653 / `f6106691...`; audit 7,750 / `f5af1b8b...`; decision 8,109 / `5295f932...` | all ten non-count gates; six exact counts; exact three-output replay; 14 focused tests; five environment tests; compile/diff | `pass-training-false` | `P2O5-T03-U02` |

U01 freezes the six-channel native-grid input, label/mask, 64 by 64 patch,
train-only normalization, whole-event grouping, and sealed-test evaluation
contracts. It does not select a split or create dataset bytes.

No provider transaction, owner review, label promotion, dataset, split,
baseline, model, metric result, training authorization, inference, deployment,
or external submission advances.
