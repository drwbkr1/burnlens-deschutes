# Petes Lake replacement optical custody decision

**Unit / issue:** `P2O4-T33-U03` / #521

**Run:** `BL-2026-07-21-petes-lake-optical-remediation-intake-r001`

**Trace commit:** `9cd81518c8fd859a950eab263e82dc9c9e406c59`

**Decision:** `PASS_PETES_LAKE_REPLACEMENT_OPTICAL_CUSTODY_AUTHORIZE_U03_SOURCE_FITNESS_R002_ONLY`

The owner-authorized DPAPI wrapper completed one exact replacement-post transaction. It repeated the clean remote-equal repository, source, terms, metadata, path, and original-pre gates before loading the credential. It then downloaded only Sentinel-2 L2A UUID `31fa8699-175b-4fd7-91c3-dd727a1576f5` in one attempt from offset zero, cleared credential variables, and completed its credential-free verifier with exit code zero.

The replacement archive is 1,195,226,823 bytes. Its provider MD5 `4cf05a073b4c67f5e92e052ed1eb32bc` and BLAKE3 `1b28f566aee5619ea9a48c8dd042f209194a40989ba4b54cfe4e14904a0ad878` match the exact contract; its independently computed local SHA-256 is `8bf6ffac0d46d17b6f3716250aed9dff49b9f89b62a310c296a5d36f41a0e1d9`. The ZIP contains 95 members and 1,195,191,837 uncompressed bytes under the one expected SAFE root. Manifest and full CRC checks pass.

The archive and registration manifest are single-link regular files in ignored, untracked, no-overwrite repository-local custody. The transaction and aggregate states are also ignored, untracked, and single-link. Quarantine is absent after promotion. The 22,246-byte tracked custody report has SHA-256 `e23d601959d09fb54fc6409f5a073df4f1a3a3a8a0d040e04a9b46c2594537b1`, binds semantic SHA-256 `78c888b4a3b954c4038a3454773b1cd7c922bc5f71957524e803ee6534d71f75`, and is bound back from the private aggregate by exact path, bytes, and hash.

The original 21 July pre archive was not reacquired or modified. It freshly reverified at 1,185,284,273 bytes and local SHA-256 `c5b6ededc5a264fcc617f2712093b847351c5b8ed78f2ea9ce0ebc3a33e1bc34` during preflight and final verification. The original planned post archive and failed U03 r001 evidence also remain unchanged.

Two additional credential-free verifier attempts failed closed without custody mutation: one transient remote-head query failure and one transient official-terms `URLError`. Immediate read-only checks confirmed the branch was unchanged and remote-equal; the next bounded verifier passed. These failures are retained because transport availability is not scientific or custody evidence.

The cleanup audit found five stale broad loopback `http.server` processes on ports 8765/8767, including two rooted in the retired OneDrive checkout and their runtime children. Exact PID, parent, command, executable, and listener identity were checked; all five were stopped. Both ports are closed, and no acquisition process or credential environment remains.

Custody passes only. U03 source-fitness r002 must inspect actual delivered metadata, CRS, grids, bands, nodata, SCL/CLD/SNW, local cloud/smoke/shadow/snow, chronology, registration, paired usable pixels, continuous change evidence, and a real rendered output. The catalogue snow value remains a visible risk. U04 and every downstream reference, candidate, owner-response, label, event-completion, dataset, split, baseline, and model gate remain blocked.

Contains modified Copernicus Sentinel data 2023, accessed through CDSE.

Experimental BurnLens CV evidence. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
