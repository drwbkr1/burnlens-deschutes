# Make the portfolio portable without flattening its evidence

The Phase Six package keeps the exact reviewer surface and its
repository-relative evidence paths intact. Rather than rewrite the prior
artifacts into one new summary, it copies 112 permitted tracked files,
including the complete Phase Five candidate and the local-link closure needed
by the reviewer journey and case study.

The first result is one 117-file extract-and-open directory and a deterministic
14,963,460-byte ZIP. Every file is manifest/checksum bound. The build refuses
untracked sources, overwrites, path traversal, links, encrypted members,
custody/private-response material, and model weights. Two independent rebuilds
match the tracked ZIP byte for byte.

The full suite then exposed a source-binding problem: r001 declares a commit
whose project files say 0.56.0 while its lockfile still says 0.55.0. Locked
environment setup refuses that mismatch. R001 remains exact failed
pre-freeze evidence; a no-overwrite v0.1.1 / r002 correction is required before
recipient QA.

This is still local pre-publication work. U06 cannot begin until the corrected
package passes the full clean-source gate. RBR remains accepted, the U-Net
remains rejected, WCP-002 stays visible, and no public action has occurred.

The corrected source then passes 800 tests, one expected skip, 86 subtests,
locked-environment verification, and dependency integrity. R002 keeps the
same 117-file evidence roster and creates a new no-overwrite v0.1.1 archive at
SHA-256 `5a314b69...`. Installed-CLI directory/archive validation and two exact
rebuilds pass. R001 remains visible; U06 may now test r002 as a recipient.
