# Paired-Intake Transaction Decision

## Decision

Accept `paired-intake-contract-v0.4.0` as the fail-closed registration boundary for the exact Sentinel-2 plus NOAA-21 VIIRS fire/geolocation package. The rehearsal correctly remained at `BLOCKED_OWNER_CREDENTIAL` when it ran. `ACCESS-2026-006` records the owner's later approval for both credential boundaries; no authenticated request or provider byte has yet been exercised.

## Weakness addressed

BurnLens already knew the three exact asset identities and could reject a single malformed delivery, but it did not prove that the pair would enter raw storage as one indivisible package. A fire granule without its geolocation companion, or any partial registration after a later failure, would corrupt provenance before preprocessing began.

## Adopted design

- One versioned contract pins all filenames, provider IDs, native IDs, exact sizes, container types, pair token, and available provider checksums.
- All three files must coexist in a clean quarantine directory.
- Quarantine paths, destination parents, and asset files must not use symlink/junction indirection; asset files must have one filesystem link.
- Validation fails closed before registration.
- Sentinel must pass both provider MD5 and provider BLAKE3 plus ZIP/SAFE integrity checks.
- VIIRS must pass exact-size and native HDF5 signature checks; local SHA-256, MD5, and BLAKE3 values compensate for the absence of published provider checksums without misrepresenting them as provider attestations.
- Registration writes the manifest in quarantine and atomically renames the complete directory on the same filesystem.
- Existing destinations are never overwritten.
- The contract digest covers the exact asset records and every transaction invariant, not asset identities alone.
- A failed atomic rename removes its provisional manifest and leaves the validated quarantine available for a clean retry.
- A promoted package can be re-verified against registration schema `0.2.0`, the full contract digest, exact entry set, container checks, and current local hashes; later mutation fails visibly.

## Evidence

Run `BL-2026-07-14-paired-intake-rehearsal-r001` reports the actual empty-provider state and a separate temporary synthetic rehearsal. The synthetic path rejects a partial set and checksum tamper, promotes a complete set atomically, and retains no fixture bytes. Report schema `0.2.0` fixes the primary-source metadata observation at 2026-07-14 and declares that the deterministic run performs no live provider request. The JSON, semantic HTML, and 1600x1200 evidence card reproduce byte for byte from fixed inputs.

## Primary-source basis

- CDSE OData documentation defines authenticated `$value` product delivery and exposes product size/checksum metadata.
- CDSE token guidance says not to hardcode usernames or passwords.
- NASA Earthdata Login documents protected data access and application authorization.
- Current public CDSE OData and NASA CMR records still match the three pinned identities and sizes; NASA CMR publishes no checksums for the two selected VIIRS granules.
- The pinned `blake3==1.0.9` package is the current verified PyPI release used to evaluate CDSE's published BLAKE3 value.

## Phase and portfolio meaning

This advances Phase Two Objectives Two and Three at their boundary: the source stack now has an executable, reviewable transaction contract before real bytes arrive. It does not satisfy source-fitness, immutable real-raw registration, preprocessing, label, dataset, baseline, or model-readiness outcomes.

For a portfolio reviewer, the value is reliability discipline made visible: BurnLens can show what it will accept, why incomplete state is forbidden, what was tested, and what remains unknown without pretending synthetic evidence is remote-sensing evidence.

## Next gate

The transaction baseline shipped through issue #325 / PR #326 at `ee1a1d678ad888b595dc3c7b215f787ea5156582` and annotated tag `v0.3.0-intake-transaction-baseline`. After lifecycle sync issue #327 ships, open a new issue-backed branch, use the authorized credentials to acquire only the exact three assets into excluded quarantine, apply this contract, visually inspect the real source package and AOI-relevant contents, and either register the complete package or delete the rejected quarantine. A passing transaction must still be followed by a separate pixel-, quality-, geolocation-, and target-fitness decision.
