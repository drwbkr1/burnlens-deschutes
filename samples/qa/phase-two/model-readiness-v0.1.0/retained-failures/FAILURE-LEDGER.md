# P2O5-T03-U06 retained verification failures

## R001 narrow decision-token overflow

Run `BL-2026-07-25-p2o5-t03-u06-readiness-r001` generated five outputs from
source `28c456b5ae7a84f3438f1cc5a1b178d31e6555ab`. Exact replay and the 1280 by
720 desktop render passed.

The 390 by 844 browser check failed because the unbroken
`AUTHORIZE_BOUNDED_UNET` and `REJECTION_FIRST_SINGLE_MODEL_EXPERIMENT` tokens
extended the document to 409 CSS pixels while its client width was 375 CSS
pixels. The first overflowing element was a `strong` token with a right edge
near 408.65 CSS pixels. No analytical, authorization, source, dataset, split,
baseline, or contract value failed. The exact five r001 outputs are retained in
`r001-narrow-token-overflow/`.

Remediation: allow machine-readable text inside cards to wrap anywhere, commit
that renderer change, regenerate a new run, and repeat exact replay plus both
browser viewports.

## V001 wrong Python interpreter

After the r001 byte replay passed, one combined focused verification command
used the system `python` executable instead of the repository's locked
`.venv\Scripts\python.exe`. Twelve tests ran before import of
`tests.test_dataset_qa` failed with `ModuleNotFoundError: No module named
'rasterio'`. This is an invalid-environment verification attempt, not a product
or package failure.

The immediate rerun under the locked CPython 3.12.10 environment passed all 19
model-readiness, baseline, and dataset-QA tests in 23.906 seconds, with only the
existing NumPy 2.5 deprecation warnings.
