# Phase Five primary-source research

Checked: 2026-07-26

This record supports only the bounded Phase Five QA standard. It does not
create a formal accessibility certification, a broad penetration test, a
vulnerability-free claim, or an operational-readiness claim.

## W3C WCAG 2.2

Source: [Web Content Accessibility Guidelines 2.2](https://www.w3.org/TR/WCAG22/)

Relevant current requirements include keyboard operation, no keyboard trap,
meaningful focus order, visible and unobscured focus, non-color
communication, reflow, and programmatic name, role, and value. BurnLens adopts
these as a bounded AA-oriented review standard for the exact repository-owned
interface. Automated and internal review is not represented as complete WCAG
conformance or third-party certification.

## OWASP archive path handling

Source: [OWASP Web Security Testing Guide — malicious file upload and archive
directory traversal](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/10-Business_Logic_Testing/09-Test_Upload_of_Malicious_Files)

OWASP describes archive directory traversal when extraction does not validate
member paths. BurnLens therefore requires an adversarial archive member that
would escape the destination and must be rejected before extraction. The test
is scoped to BurnLens's own offline package format; it is not a claim about a
general-purpose upload service.

## CISA SBOM resources

Source: [CISA SBOM Resources Library](https://www.cisa.gov/topics/cyber-threats-and-advisories/sbom/sbomresourceslibrary)

CISA describes an SBOM as a record of software component details and
supply-chain relationships. BurnLens will generate a release-scoped
dependency inventory and classify the current vulnerability result. The
inventory improves transparency but does not prove that the software is
vulnerability-free.

## PyPA pip-audit

Source: [PyPA pip-audit](https://github.com/pypa/pip-audit)

The current primary documentation identifies `pip-audit` as a scanner for
known Python dependency vulnerabilities, documents installed-environment
auditing with `--path`, JSON output, and exit code `1` when findings exist,
and explicitly warns that the tool is not a static code analyzer or a defense
against malicious packages. BurnLens therefore retains the exact nonzero
result, classifies every unique advisory, and makes no vulnerability-free
claim.

## GitHub Advisory Database

Source:
[GHSA-h35f-9h28-mq5c](https://github.com/advisories/GHSA-h35f-9h28-mq5c)

The 2026-07-26 API snapshot classifies the setuptools finding as medium
severity with CVSS 3.1 score 6.1 and a fixed version of 83.0.0. The affected
path is `MANIFEST.in` exclusion matching for macOS source-distribution builds.
BurnLens retains setuptools 82.0.0 because the frozen model environment
requires that pin, discloses the finding, and verifies the bounded mitigation:
Windows/NTFS, no `MANIFEST.in`, normalized ASCII tracked paths, no source
distribution, and a ZIP-only release package.

## SPDX

Source: [SPDX overview](https://spdx.dev/about/overview/)

SPDX is an open standard for communicating software bill-of-materials,
provenance, licensing, and security information. U04 records a
release-scoped component and rights inventory but does not label the
project-specific JSON as SPDX or claim formal SPDX conformance.

## Decisions

- Phase Five accessibility target: bounded WCAG 2.2 AA-oriented review.
- Required hostile package case: archive path traversal rejected before
  extraction.
- Required supply-chain evidence: exact release dependency inventory plus
  vulnerability classification.
- A known medium advisory may pass only with its exact identity, severity,
  affected path, bounded mitigation, retained raw result, and explicit
  no-vulnerability-free-claim limitation.
- Project-specific offline performance budgets are explicitly local design
  constraints, not externally asserted universal standards.
- Browser security policy remains controlling. The blocked local `file://`
  automation route will not be bypassed.
