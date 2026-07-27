# Phase Six release audit

BurnLens now has a verified local pre-publication candidate. That sentence is
deliberately narrower than “published”: no tag, GitHub Release, deployment,
public-sharing change, or external submission exists.

The final audit exercised the repository as a recipient and as an installer.
The 14,963,469-byte Phase Six ZIP validates, extracts to 117 exact files, and
rebuilds byte-for-byte from a fresh short-path checkout. The real package
already passed desktop, narrow, and keyboard-first browser use. Two fixed-epoch
0.56.0 wheels match at SHA-256 `ac9db790...`; a fresh Python 3.12.10
environment loads the installed package from `site-packages`, reports 75
compatible distributions, and runs all 122 command help routes.

The fresh-checkout gate found one material packaging defect before closeout.
Two Phase Six checksum rosters were converted to CRLF because their nested
paths lacked an explicit checkout rule. Validation failed closed. Commit
`cd383a3...` adds the recursive LF contract plus regression coverage. The
corrected clean head passes 801 tests, one expected skip, 422 existing NumPy
deprecation warnings, and 86 subtests.

Closing the milestone then exercised a second edge: the living case study must
advance, but U05's original builder required its old current-checkout bytes.
The builder now reads the exact tracked frozen candidate snapshot after the
package exists. Thirteen focused tests pass and the updated repository still
rebuilds the original ZIP byte-for-byte.

The project narrative remains evidence-led. RBR is the accepted analytical
method for the bounded Ward Creek demonstration. The trained U-Net remains an
exact, reproducible, rejected diagnostic and did not outperform RBR. WCP-002,
the owner-approved-prototype boundary, two medium reliability findings, and
all non-operational limitations remain visible.

U07 disposition is `ready-for-owner-publication-gate`. The next repository
action is one coherent reviewed milestone PR. Public action remains closed
until the owner explicitly handles that separate stop gate.
