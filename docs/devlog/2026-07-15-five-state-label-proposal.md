# Five-state proposal: make uncertainty visible before a dataset exists

The registration checkpoint cleared the pair-local alignment prerequisite, but BurnLens still had no reviewable target pixels. That was the highest-leverage evidence gap: the protocol described five states, while the portfolio could show only imagery and continuous change.

Issue #353 implements the smallest defensible next step. The new BurnLens 0.9.0 proposal path reopens the exact registered Sentinel pair, works on its native 600 by 450 20 m grid, computes four change signals, and uses the later NIFC geometry only as context. Burned and background are affirmative candidate classes; unknown, excluded, and review-needed remain visible and stay outside target use.

The first real render exposed too much isolated spectral speckle. Rather than hide it with presentation smoothing, the method added explicit local-evidence requirements: at least five of nine neighboring pixels for a burn candidate and seven of nine for stable background. The final proposal still leaves 33.4144% of the AOI ignored, which is a feature of the evidence posture rather than a coverage failure.

A separate verifier then reopens the sources and independently recomputes every state. It imports no proposal-classification helper, checks both GeoTIFF contracts and trace tags, compares all 270,000 state and target pixels, and audits 120 deterministic samples. Agreement is exact. The render makes the limitation equally prominent: this is software reproducibility under a shared contract, not independent human annotation or field validation.

The checkpoint accepts `darlene3-burn-scar-label-proposal-v0.1.0` as reviewable one-event evidence and deliberately defers a dataset. The next hard question is cross-event truth and leakage-resistant grouping, not how quickly to tile this one fire or train a model.

> Experimental BurnLens CV evidence. Not official wildfire information. Not emergency guidance. Not evacuation, routing, tactical, or incident-command support. Official sources govern.
