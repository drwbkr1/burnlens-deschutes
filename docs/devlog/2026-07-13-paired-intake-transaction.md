# Devlog - Three Assets, One Transaction

**Date:** 2026-07-13 local / 2026-07-14 UTC

**Issue:** #325

## Weakness selected

BurnLens had done the careful work of pinning one Sentinel scene and the matching VIIRS fire/geolocation swath. It could also detect the dangerous case where a login page arrived with a successful-looking HTTP status. But it had no executable answer to a simpler reliability question: what prevents only two of the three expected assets from being registered?

That matters because the active-fire granule is not spatially useful without its geolocation companion. Partial raw state would make later provenance look more complete than it was.

## Improvement made

The new contract treats the exact three files as one transaction. It checks identity, exact size, native container, pair token, archive safety, and every provider checksum that exists. It writes local hashes and a registration manifest only after the whole set passes, then promotes the quarantine directory with one same-filesystem rename. It refuses to overwrite an existing destination.

The real package is still absent because credentials remain owner-gated. To test the state machine without weakening that boundary, the CLI creates a tiny temporary synthetic package, proves two failure paths and one successful promotion, and deletes every synthetic byte. The evidence card shows the real blocked state and synthetic mechanics as separate sections.

An audit before shipment found that the first report schema called its pinned metadata facts a refresh performed at the caller-supplied run time. The committed run used the correct time, but later reruns could imply newer research than actually occurred. Report schema `0.2.0` now fixes the observation time, links `ACCESS-2026-005`, and says directly that the deterministic run performs no live provider request.

A second filesystem audit rejected another form of hidden state: symlink, junction, and multiply-linked inputs. Without that rule, a correctly named quarantine entry could hash bytes stored elsewhere and remain mutable after registration through another path. The candidate contract's SHA-256 covers both the three exact asset records and all transaction invariants, so changing a security rule changes the contract identity.

A final recovery audit forced the atomic rename itself to fail. The earlier implementation left its provisional registration manifest in quarantine, making an otherwise valid package fail as unexpected state on retry. Contract `v0.3.0` removes that manifest on rename failure, preserves the original files, and proves that the next ordinary retry succeeds.

## Portfolio meaning

This is invisible plumbing made reviewable. It demonstrates that BurnLens is not merely planning to be reproducible later: it is defining the transaction boundary before source bytes arrive, testing incomplete and tampered inputs, and preserving a truthful distinction between software proof and data proof.

## What it does not solve

No Sentinel or VIIRS provider file has been downloaded or inspected. BurnLens still does not know whether the acquisition contains usable active-fire evidence, whether optical and thermal observations align well enough, or whether the primary target can support a defensible dataset.

## Next boundary

Credential approval remains the only owner decision. If approved for both CDSE and Earthdata, the next checkpoint will place the exact assets in quarantine, run this gate, visually inspect real outputs, and accept or reject the source package without bypassing its unknowns.

> Experimental BurnLens CV output. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
