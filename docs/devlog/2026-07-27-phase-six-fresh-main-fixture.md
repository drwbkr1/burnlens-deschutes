# Phase Six fresh-main fixture remediation

The Phase Six milestone merged cleanly, but its first fresh-main verification
exposed a local-state assumption in the tests. The default lean environment
did not include pytest; after the locked developer profile was installed,
five tests still failed because they expected the ignored `downloads/`
directory to pre-exist.

BL-EXC-004 makes that temporary parent explicit in both Phase Six test classes.
A clean remote clone at `0ea5543...` now passes all 15 focused tests, both
candidate validators, the structured release audit, and dependency health.
The 14,963,469-byte candidate ZIP remains byte-identical at `5a314b69...`.

This is a test-fixture portability repair. It changes no analytical or
portfolio artifact and authorizes no public action.
