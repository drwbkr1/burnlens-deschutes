# PRECHECK-2026-026 - Prototype Sufficiency Checkout Stability

**Issue / PR:** #446 / #447

**Trigger:** Fresh validation of analytical merge `dbc24c57442d0c2564ce7ae4e4da17a2c966b910` failed because a Windows checkout expanded the committed 3,770-byte readiness HTML to 3,780 bytes.

## Scope decision

- Add explicit LF checkout rules for Phase Two label-readiness JSON and HTML.
- Add regression coverage for those rules.
- Repeat detached/fresh checkout tests and exact three-output reconstruction before tagging.
- Change no analytical output content, owner evidence, label state, dataset/split/baseline/model version, source role, or public claim.

**Entry decision:** `REMEDIATE_CHECKOUT_BYTES_BEFORE_RELEASE`.
