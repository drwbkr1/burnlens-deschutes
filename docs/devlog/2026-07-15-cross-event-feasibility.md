# Cross-event feasibility: freeze independence before downloading more imagery

The shipped five-state proposal reproduces exactly, but its strongest remaining weakness is structural: one event and one exact scene pair cannot support leakage-resistant evaluation. Tiling Darlene more aggressively would create more files, not more independent evidence.

Issue #357 moves the decision one level upstream. BurnLens 0.10.0 queries current official MTBS, Census, and CDSE metadata, freezes the complete provider response needed for audit, and evaluates every bounded event without downloading a Sentinel product. The capture is deliberately strict about provider schema, transfer limits, county membership, exact routes, terms identity, and full-boundary tile coverage.

That strictness matters. Tepee and McKay each have compatible same-platform/tile/orbit/processing pre/post choices. Milli has abundant intersecting catalogue items but zero single tiles that cover its complete MTBS boundary, so it remains visible and excluded rather than being silently cropped or mosaicked.

The result freezes event, scene, geography, and time groups for Darlene, Tepee, and McKay before any tiling. McKay is only 10.925 km from Darlene, which is disclosed rather than converted into a false independence claim. Whole-group isolation is now the binding contract; a later partition still has to prove zero group overlap and keep its test role untouched.

This checkpoint selects exact acquisition candidates and nothing more. No selected imagery has been downloaded or locally inspected. No cross-event label, dataset, split, baseline, model, application, or accuracy claim exists. The next meaningful question is whether the four frozen Sentinel products survive authenticated acquisition, integrity, local pixel-quality, and registration gates—not how soon BurnLens can train.

> Experimental BurnLens CV evidence. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
