# Devlog - Additional Whole-Event Groups

The cycle began by reconstructing the verified official-source scout. All four outputs matched exactly, but the result made the current weakness obvious: the leading candidates were mostly older Landsat-era events, while BurnLens needed comparable Sentinel-era whole-event groups before touching dataset or model work.

The new metadata-only path queried current official MTBS, Burn Severity Portal, and CDSE STAC services for five bounded Central Oregon candidates. It required one Sentinel item to cover every MTBS boundary vertex, then required pre/post scenes to match platform, MGRS tile, relative orbit, and processing baseline with catalogue cloud at or below 20%.

Green Ridge (2020), Grandview (2021), and Petes Lake (2023) win the deterministic ranking because they add three event years absent from the existing pool, retain repeated official reference regimes, and then maximize spatial separation. Whychus and Whitewater remain visible reserves. The three selected boundaries do not overlap.

The rendered report freezes six total event identities and six exact Sentinel products totaling 6.277 GiB catalogued. Zero product bytes were downloaded. The original-resolution PNG was visually inspected and clean. Both classes, unknown boundaries, local pixel quality, registration, label fitness, owner review, split integrity, baseline value, and model value remain gated.

After PR #469 merged, the separate remote-main clone reproduced the report exactly and passed its tests. It also caught a release-metadata defect: the earlier wheel came from a long-lived Windows checkout with stale CRLF package bytes, whereas the existing repository attributes correctly produce LF bytes in a fresh clone. The tag stayed withheld. Issue #470 binds the release to the independently repeated 476,330-byte fresh-clone wheel without changing any event, source, output, or scientific claim.
