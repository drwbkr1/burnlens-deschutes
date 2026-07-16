# Devlog: Owner-Waiver Reveal Readiness

The highest-leverage weakness after atomic response intake was no longer custody; it was the absence of a separate, inspectable authorization boundary between the owner's reviewer-two waiver and proposal reveal. Issue #407 splits that gate from reconciliation so BurnLens can prove exact pre-reveal state before opening content.

BurnLens `0.19.0` adds a fail-closed authorization command and independent public-QA command. The real run reverified the 16,443-byte preserved response, 2,508-byte receipt, 61,599-byte packet, and 9,433-byte reveal by exact SHA-256. The authorization is 3,643 ignored bytes with SHA-256 `db917fdf287ffb156b574beb6ec3a891c1d55d9653b6dfc2e1f8e434f6bed952`. It records one response, no reviewer two, explicit reduced-validation acknowledgement, zero reveal actions, and authorization only for a later private issue-#403 reconciliation.

The public JSON/HTML/PNG withhold response labels, distributions, confidence, reasons, notes, timestamps, reviewer experience, attestation text, private filenames and paths, and proposal-reveal content. The 1800x1280 evidence card is readable at original resolution and states the absent inter-rater, consensus, adjudication, label, dataset, split, baseline, and model evidence.

All 176 tests, compileall, dependency health, semantic, privacy, original-resolution visual, and exact-file gates pass. Two fixed-epoch fresh-source wheels are byte-identical at 326,372 bytes / SHA-256 `2987698bf86e1d80f8d944e9643ce2bb6171ad658f78d709d83a6fa973d3eb8e`; isolated BurnLens `0.19.0` exposes 31 console entry points and zero private/download/build entries.

The reveal remains operator-declared unopened. The next run may open it only inside deterministic ignored reconciliation under issue #403.

PR #408 was reviewed at `bb89a7bd36b60379f4c7680ae28837dd51111911` and squash-merged as `0ab2b948a4d74c770f6d23042a1d9725642eac42`. Annotated tag `v0.19.0-owner-waiver-reveal-readiness` has tag object `dca77c6194edfa5aadb5a4a41c5acc9ddf93e6ec` and peels remotely to that merge. A fresh merged-main checkout passed all 176 tests, compileall, dependency health, Node syntax, 56 tracked-JSON checks, 125 internal-link checks, exact output verification, and canonical-wheel reproduction. Issue #409 synchronizes this terminal release evidence without changing custody or scientific state.
