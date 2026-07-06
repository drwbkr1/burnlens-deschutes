# Access Log Template

## Template status

This is a blank Phase Two intake template. It does not access, download, store, transform, or publish data.

Do not replace placeholders until Phase Two access is authorized.

## Purpose

Use this record to document each source access event before and after data retrieval. The access log must show what was accessed, why, under what terms, with what parameters, and what happened, while keeping credentials and sensitive access details out of the repository.

## Boundary warning

Experimental BurnLens data-access record. Not official wildfire information. Not emergency guidance. Official sources govern.

## Access identifiers

| Field | Value |
|---|---|
| Access log ID | `ACCESS-YYYY-NNN` |
| Related source record | `SRC-YYYY-NNN` |
| Related AOI record | `AOI-YYYY-NNN` |
| Related provenance manifest | `MANIFEST-YYYY-NNN` |
| Task issue / PR | `#`, `#` |
| Branch | `[branch]` |
| Access status | planned / completed / failed / cancelled / no-go |
| Created date | `YYYY-MM-DD` |
| Access date/time UTC | `YYYY-MM-DDTHH:MM:SSZ` |

## Access request

| Field | Value |
|---|---|
| Source URL or endpoint | `[placeholder]` |
| Landing page used | `[placeholder]` |
| Access method | browser / API / CLI / bulk download / manual request / other |
| Request purpose | `[why access is needed]` |
| Request parameters | `[bbox/date/query/bands/etc.; do not include secrets]` |
| AOI used? | no / yes: `AOI-ID` |
| Authentication required? | yes / no / unknown |
| Credentials recorded in repo? | no |
| Terms reviewed before access? | yes / no / not applicable |
| Rate limit or quota concern? | yes / no / unknown |

## Access result

| Field | Value |
|---|---|
| Result | success / failed / partial / cancelled / no-go |
| HTTP/status or tool status | `[placeholder]` |
| Files received? | no / yes |
| File names | `[future filenames only after authorized access]` |
| Storage path | `[future path only after authorized access]` |
| File sizes | `[placeholder]` |
| Checksums | `[placeholder]` |
| Metadata received? | yes / no / unknown |
| License or citation file received? | yes / no / unknown |
| Error message summary | `[if failed, summarize without secrets]` |

## Security and privacy exclusions

- [ ] No credentials, tokens, cookies, API keys, or private URLs are recorded.
- [ ] No sensitive personal information is recorded.
- [ ] No restricted data is stored in the repository.
- [ ] No unreviewed emergency guidance is created.
- [ ] No access method bypasses provider terms.

## Pre-use gate

Before accessed data may be used:

- [ ] Source record is approved.
- [ ] Access log is complete.
- [ ] File checksums are recorded when files exist.
- [ ] Format/CRS precheck is complete.
- [ ] Provenance manifest is updated.
- [ ] Claims register entry is created if the source supports any claim.

## No-go access conditions

Do not access or use data if:

- provider terms are unclear or incompatible;
- access requires storing secrets in the repo;
- data is restricted, sensitive, or not appropriate for a public portfolio project;
- source identity or metadata is too ambiguous;
- access would imply official emergency-use authority;
- requested data would exceed the authorized Phase Two scope.

## Verification notes

| Check | Result | Notes |
|---|---|---|
| Source record exists. | pending / yes / no | `[SRC-ID]` |
| Access scope matches source terms. | pending / yes / no | `[note]` |
| No credentials recorded. | pending / yes / no | `[note]` |
| Checksums recorded if files exist. | pending / yes / no / not applicable | `[note]` |
| Downstream precheck required. | yes | Format/CRS precheck before use. |

## Handoff

If access succeeds, complete or update the format/CRS precheck and provenance manifest before any preprocessing, labels, masks, model inputs, outputs, metrics, maps, or public-demo work.
