# PRECHECK-2026-056 - Petes Lake material-defer milestone exit

**Unit / issue / branch:** `P2O4-T33-U11` / #521 / `codex/p2o4-t33-petes-lake-milestone`

**Terminal evidence checkpoint:** `52310531ad0b8e6d07800fc752f7bf65b5fdea9a`

**Decision:** `AUTHORIZE_MATERIAL_DEFER_CLOSEOUT_ONLY`

## Entry condition

The final automatically authorized same-source run `BL-2026-07-22-petes-lake-nwi-context-r003` is immutable and terminal. Its 85,612-byte contract / SHA-256 `d85dc5ec8991a50605d4501ee91cb717e4089a5243dba40e6531f520bd5d8dc3` records seven promoted assets, one failed asset, and four authorized-unexecuted assets. Asset eight made its only durable request and failed at `PROVIDER_OPEN` with the bounded diagnostic `{category: http, http_status: 500}`. The exact failed partial is zero bytes. REGISTRY-2026-058 preserves and independently revalidates the complete state.

Issue #521 and PRECHECK-2026-055 require this outcome to stop the provider roster and route the milestone to a material decision. No r004, retry, continuation, partial fitness selection, or later roster request is authorized.

## Authorized work

U11 may:

- select and document the `defer` material exit;
- preserve the complete U01-U11 ledger and every failed, superseded, passed, deferred, and unexecuted unit;
- verify the exact ignored custody and tracked Petes evidence without changing it;
- re-run deterministic output reconstruction, package, tests, privacy, link, JSON, LF, and actual-render checks;
- advance BurnLens software to 0.45.0 because the milestone adds material packaged capabilities;
- update active repository truth, open one milestone PR that closes #521, merge it after all gates pass, create the applicable annotated tag, and verify the shipped checkpoint.

U11 may not:

- request or download another NWI response or archive;
- treat any r001-r003 partial as a complete U05 package;
- execute U05 scientific fitness or production U06-U10;
- create a Petes candidate, owner surface, response, label, sixth accepted event, dataset, split, baseline, model, metric, deployment, field-validation, official, endorsed, operational, or emergency-ready claim;
- change historical run outputs merely to display the later milestone software version.

## Material decision

`defer` is the narrowest supported exit. A tested same-source correction does not exist, so `remediate` is unsupported. No equivalent alternate route is registered in #521, so `fallback` cannot execute here. Current evidence does not prove that Petes Lake is permanently unsuitable, so `exclude` is unnecessarily final. One terminal source route does not justify stopping BurnLens.

A separate future issue may register an official fallback under fresh source, terms, custody, integrity, scientific-fitness, privacy, and failure-retention gates. That future route receives new identities and cannot seed itself from r001-r003.

## Retained U11R1 release-candidate failure and remediation

Run `BL-2026-07-22-petes-lake-u04-descendant-trace-remediation-r001` retains the first clean-checkout release failure. Candidate `9f44099922485b9c26b4cadcc029a67423434877` produced two independent, byte-identical 798,433-byte wheels at SHA-256 `8e3f28e1ad49ea0f7d3eb9663e70fd981052c8cbccd01055ff43e4314adfbb79`; isolated installation and both U03 replays passed. U04 stopped before output with exact error `native-contract source bytes differ from the trace commit`.

The defect was in descendant trace enforcement: source `20d6991cbc079f87db6a789717ebd01595c0b05c` compared the whole shared `.gitattributes` and `pyproject.toml` files, so later valid LF rules, version metadata, and console-command additions made an otherwise unchanged U04 computation unreplayable. It was not U04 output, custody, reference-pixel, or scientific drift. Correction checkpoint `fcbaa4c1044672352227f6a3047d998967d1d114` binds the invariant U04 computation while fail-closing on source ancestry, live remote equality, hidden checkout drift, CLI/test/mapping drift, LF overrides, unsafe trace changes, dirty state, and time-of-check/time-of-use changes. Issue comments `5049902001`, `5049932401`, and `5050031734` retain the failure, clarified contract, and merge-topology requirement. No provider, custody, label, dataset, split, baseline, or model state changed.

## Exit gate

U11 closeout completes only when:

1. every unit and retained failure has an exact disposition;
2. r001-r003 revalidate from local files and no r004/provider process exists;
3. actual U03 renders, U03 replay, corrected U04 native-contract replay, safe preparatory U09 software QA, package, and full repository checks pass from the final clean candidate and fresh merged main;
4. non-existent U05 scientific, U06-U10 production, candidate, response, label, dataset, split, baseline, and model outputs are explicitly recorded as unexecuted or absent;
5. active truth says Petes Lake remains deferred and the accepted state remains ten balanced regions across five complete events;
6. public claims retain source precedence and the experimental, non-official, non-operational boundary;
7. the milestone is shipped and verified from `drwbkr1/burnlens-deschutes` only through a true merge commit that preserves `20d6991cbc079f87db6a789717ebd01595c0b05c` as an ancestor and the exact reviewed head as a merge parent; squash and rebase merge are invalid for this milestone.
