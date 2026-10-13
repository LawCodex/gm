# The Gambia (GM) — legislation as Markdown

Part of [LawCodex](https://github.com/LawCodex): the legislation of every country as plain Markdown in git.

**Minimal repository.** The Constitution of the Republic of The Gambia (1997, 2002 reprint) and the Acts published
as PDFs by the **Ministry of Justice** (moj.gov.gm), in English.

Retrieved 2026-10-13.

<!-- COUNTS -->
| Directory | Files |
|---|---|
| `acts/` | 6 |
| `constitution/` | 1 |
| **Total** | **7** |
<!-- /COUNTS -->

## Structure

```
constitution/constitution-1997.md   Constitution of the Second Republic (in force 16 January 1997), 2002 revised reprint
acts/<year>/<title>.md              Acts (Criminal Offences Act 2025, Criminal Procedure Act 2025, Anti-Corruption Act 2023, ...)
```

The Constitution PDF prints section numbers and marginal notes (section titles) in a left margin; the conversion
rebuilds `Section N — <marginal note>` headings from the layout. About 15 sections whose marginal note could not be
aligned keep their text without a separate heading; sections 51–57 were deleted by Act No. 6 of 2001. Amendment
references printed in the margin ("6 of 2001") are dropped. Acts: file names and titles derived from the PDF file
names; `status: unknown`.

## Source

| Source | URL |
|---|---|
| Ministry of Justice — documents (list from the site's WordPress media API) | https://moj.gov.gm/ |

## Not covered / known gaps

* **No general collection of Gambian statutes.** The National Assembly (assembly.gov.gm), the Judiciary and the
  Government portal did not answer. The GambiaLII site is not used (its terms prohibit scraping and bulk download).
* Skipped (scanned PDFs without text layer, not OCRed): Constitutional Review Commission Act 2017, Truth,
  Reconciliation and Reparations Commission Act 2017. The 2020 draft constitution (rejected by the National Assembly)
  is not included.
* Amendments to the Constitution after the 2002 reprint are not included.

## Copyright

Official texts of the Republic of The Gambia published by the Ministry of Justice; official legislative texts are
generally not subject to copyright. The Markdown conversion is provided as is; the authoritative text is the one
published in the *Gambia Gazette*.

## Regenerating

```sh
python3 scripts/gm_fetch.py    # downloads to ../_raw/gm/ (3 s between requests) and writes the Markdown
python3 scripts/gm_readme.py   # updates the counts table
```
