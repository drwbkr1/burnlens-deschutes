# Devlog - Green Ridge Owner Response Intake

The response arrived as one exact hash-named 893-byte file. BurnLens did not inspect its decision values first. A new v0.38 transaction validated the response contract and copied the exact bytes into ignored repository-local custody without overwrite, fsynced the copy, re-read the source, verified byte identity, and wrote a separately bound receipt. Synthetic tests prove tamper, reordering, wrong filename, incomplete attestation, overwrite, and privacy failures close the path.

Only after custody passed did reconciliation reveal two yes decisions. Both candidate rasters then re-passed exact bytes, EPSG:32610 native grids, nodata and class domains, intact eight-connected 25-pixel cores, exact one-pixel unknown rings, source and terms, quality and registration, and event identity. The two regions become one burned and one background owner-approved prototype label; the 87 ring pixels remain unknown and excluded.

The cumulative label set now has eight regions, balanced four/four across four events, with 186 core pixels / 7.44 ha and 333 excluded ring pixels. That is stronger evidence, not a training dataset. Six accepted event groups remain the gate, so the next bounded checkpoint is Grandview source fitness under issue #495.

The first clean branch clone catches one release-only defect: the new nested intake JSON checks out with CRLF and no longer matches its authoritative LF bytes. Rebuilt outputs themselves remain exact. BurnLens adds explicit LF rules for the nested JSON/HTML path and repeats clean-clone reconstruction rather than weakening the hash gate. The corrected clone reproduces JSON, HTML, and PNG exactly.

The package gate uses two independent corrected clean checkouts, not the long-lived worktree. Their fixed-epoch wheels are byte-identical at 552,457 bytes / SHA-256 `ea80b167b29064fb6f53dd5971acf4289cf1e7e2616c9a6abe8d62616b70e29e`. A dependency-complete isolated install exposes all 59 commands, passes both new CLI help paths and `pip check`, and the 123 wheel entries contain no private response, download, build, or private-reconciliation path.
