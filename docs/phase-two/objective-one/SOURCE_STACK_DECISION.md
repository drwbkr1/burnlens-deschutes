# Phase Two First Source-Stack Decision

**Decision ID:** `P2O1-SOURCE-STACK-2026-001`

**Decision date:** 2026-07-13

**Status:** Accepted for metadata discovery; asset intake remains blocked

## Decision

Use the following smallest defensible first stack for the Darlene 3 feasibility slice:

| Role | Selected source | Decision | Why |
|---|---|---|---|
| Primary optical imagery candidate | Copernicus Sentinel-2 Level-2A, Collection 1, discovered through the official CDSE STAC catalog | Accept for discovery; asset access deferred | Open Sentinel terms, 10–20 m visible/NIR/SWIR bands, five event-window acquisitions found, and no secret needed for metadata |
| Active-fire reference candidate | NASA VIIRS 375 m Collection 2 Level-2 active-fire products `VNP14IMG`, `VJ114IMG`, and `VJ214IMG`, discovered through NASA CMR | Accept as reference metadata; asset access deferred | Open NASA data posture, 124 matching granule records across three platforms, and event-start coverage after the reported ignition time |
| Incident context | Oregon State Fire Marshal Darlene 3 release | Accept for event identity, approximate start time, and approximate location only | Official state source reports the fire started around 1 p.m. June 25, 2024, one mile south of La Pine on the east side of Darlene Way |
| AOI anchor | U.S. Census representative point for La Pine plus a deliberately buffered research envelope | Accept for discovery only | Reproducible public anchor without claiming an official fire perimeter |
| FIRMS archive/API delivery | NASA FIRMS authenticated archive and map-key API | Defer | Historical archive requires Earthdata or emailed authentication; API requires a map key. No secret is authorized in this checkpoint. |
| Burn-scar fallback imagery | Sentinel-2 L2A from the same collection at later dates | Defer | The fallback remains controlled but is not activated by metadata availability alone. |
| Additional imagery systems | Landsat, HLS, commercial imagery, and parallel source stacks | Defer | They do not improve the first metadata decision enough to justify more surface area now. |

## Discovery result

For `AOI-2026-001` and `2024-06-24T00:00:00Z/2024-07-06T23:59:59Z`:

- CDSE returned five Sentinel-2 L2A items in tile `T10TFP` with collection cloud-cover values of 0.78%, 0.53%, 56.13%, 0.02%, and 0.01%.
- NASA CMR returned 41 `VNP14IMG`, 41 `VJ114IMG`, and 42 `VJ214IMG` granule records.
- Four VIIRS granule records begin after the reported ignition time on June 25: one S-NPP, one NOAA-20, and two NOAA-21 records.
- A matching VIIRS swath record means the AOI intersects the granule footprint. It does **not** prove that the granule contains a fire detection at the incident.

## Evidence roles

Sentinel-2 L2A is the optical input candidate. VIIRS is a coarse thermal-anomaly reference, cue, sampling aid, or baseline candidate. The OSFM release is incident context. These evidence classes must remain separate.

No source in this decision is pixel-perfect ground truth. VIIRS 375 m pixels must not be resampled and described as genuine Sentinel-resolution labels. Cloud, smoke, saturation, parallax, geolocation, temporal mismatch, mixed pixels, and missed or false detections must be represented through quality masks, unknown/exclude regions, and review.

## Next checkpoint

Open a bounded asset-access readiness issue that compares the actual Sentinel asset and NASA VIIRS access paths, verifies one scene/granule pair without adding a secret unless the owner approves it, and decides whether active-fire label construction is defensible. Do not download assets under this decision alone.

> Experimental BurnLens CV output. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
