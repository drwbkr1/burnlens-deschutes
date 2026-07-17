# Devlog - Official Source and Candidate-Fire Scout

**Date:** 2026-07-17

**Issue / branch / parent:** #425 / `codex/p2o4-t13-official-source-scout` / #416

The cycle started from the real 0.22.0 accepted-request output and the existing 56-unit review handoff. The visible bottlenecks were an asynchronous provider queue, no affirmative background candidates, limited event diversity, and a newly approved owner-confirmed review route that needs stronger disclosed evidence.

The new BurnLens 0.23.0 scout makes twelve bounded live requests to official metadata/document routes, rejects oversized or malformed responses, normalizes their hashes and roles, and ranks current Deschutes candidate fires by a predeclared rule. It does not request the pending seven bundles or acquire large products.

The result identifies 21 additional candidates. GW Fire leads because of cross-program coverage, time/geography diversity, and live Landsat burned-area metadata. Milli remains attractive but carries the previously proven Sentinel single-tile exclusion, so it is not the first choice. NASA 500 m burned-area products are retained only for coarse context; NIFC perimeters and NLCD remain context, not label truth.

The official Landsat STAC catalog worked, but its advertised top-item asset redirected to EROS login. The tool recorded `AUTHENTICATION_REQUIRED`, sent no credentials, retained no asset content, and kept acquisition closed. This prevents a metadata success from being misreported as a usable data route.

The real HTML was checked at 1440 px and 390 px. The initial mobile review exposed a 974 px document overflow caused by the long decision identifier; a source fix now wraps the identifier while preserving intentionally scrollable tables. The final report has no document overflow, no external runtime resources, two tables with 8 and 7 rows, and a readable original 1800-by-1540 PNG.

Run `BL-2026-07-17-official-source-scout-r004` binds all four artifacts to source commit `216c4a9e1a6f1ea5ab8065edb9b8884dfab2d4af`. It creates zero labels, datasets, splits, baselines, or models. The original 56 units and historical 6/0/50 result remain unchanged; a later checkpoint will reopen them for owner yes/no/uncertain review.
