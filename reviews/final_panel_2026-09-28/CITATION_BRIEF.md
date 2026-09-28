# Final citation-integrity check (2026-09-28)

Repository: /Users/pat/code/rho_aif. Do NOT edit any file except your own report file.

## Slice verifiers (slices A, B, C)

File: `paper/full_paper_jair.bib` (69 BibTeX entries, counted as lines beginning with `@`, in file order).
Slice A = entries 1-23, slice B = entries 24-46, slice C = entries 47-69.

For EACH entry in your slice, verify against a primary record you actually fetch (Crossref API
`https://api.crossref.org/works?query.bibliographic=...`, arXiv abs pages, DBLP, publisher pages,
PMLR / NeurIPS / AAAI / IJCAI proceedings pages):

1. the work exists,
2. authors (full list and order),
3. title,
4. venue, journal, or booktitle,
5. year,
6. volume, issue, pages if present,
7. DOI or arXiv id if present resolves to this work.

Also, for each key, find where it is cited in `paper/full_paper_jair.tex` (cite, citet, citep,
textcite, parencite commands, including multi-key cites) and read the surrounding sentence. Flag
only clear misattributions (the source plainly does not say or do what the sentence attributes to it).

Write your report to `reviews/final_panel_2026-09-28/citations_slice_<A|B|C>.md`: for each key,
VERIFIED or DISCREPANCY, the source URL checked, and for discrepancies the field, current value, and
correct value. Separately list any entry you could not locate at all (possible hallucination) with
what you searched. Never mark VERIFIED without having seen a primary record.

## Cross-check (slice X)

`paper/full_paper_jair.tex` uses `paper/full_paper_jair.bib` (69 entries). `paper/full_paper.tex`
(LNCS) has an inline `thebibliography` with 68 natbib-style `\bibitem[Author(Year)]{key}` entries.

1. Map every JAIR key to its LNCS bibitem. List keys present in only one, and explain 69 vs 68
   (is the extra entry cited in the JAIR tex?).
2. For each mapped pair compare authors, title, venue, year, volume, issue, pages, DOI/arXiv id and
   list every substantive content mismatch (ignore formatting and abbreviations).
3. In each master, list cited keys with no bibliography entry, and bibliography entries never cited.
4. Check each LNCS natbib label matches the entry's actual authors and year.

Write to `reviews/final_panel_2026-09-28/citations_crosscheck.md`. Say "none" for empty categories.

Finish by replying with a short summary: counts of VERIFIED, DISCREPANCY, not-found, and the path of your report.
