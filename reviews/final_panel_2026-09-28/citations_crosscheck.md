# Citation cross-check (slice X), 2026-09-28

Scope: `paper/full_paper_jair.bib` (69 `@` entries, used by `paper/full_paper_jair.tex` via
`\addbibresource`) against the inline `thebibliography` of `paper/full_paper.tex` (68 `\bibitem`
entries, lines 1035 to 1380). This slice compares the two bibliographies against each other and
against their own masters. It does not check either bibliography against external records, which is
slices A, B, and C's job.

Method: both bibliographies were parsed mechanically with a brace-depth-aware BibTeX field parser and
a `\bibitem[label]{key}` splitter (throwaway scripts in `/tmp`, no repository file touched). Every
JAIR field (author surnames, author order, title, journal, booktitle, year, volume, number, pages,
eprint, doi, publisher, school, series, address, note) was normalized (accents, braces, `~`, `--`
removed, lowercased) and tested for presence in the corresponding LNCS bibitem. The reverse direction
was also run: every LNCS word and number absent from the JAIR entry was listed. Every flag was then
read by hand. Cite extraction covers every `\...cite...{}` command form including multi-key cites, with
`%` comments stripped and, for LNCS, only the bibliography block excised (the LNCS appendices follow
the bibliography, starting around line 1820).

## Summary

| Check | Result |
|---|---|
| JAIR keys mapped to an LNCS bibitem | 68 of 69 |
| Keys present in only one master | 1 (`gundersen2024jair`, JAIR only) |
| Substantive content mismatches between mapped pairs | 1 (DOI present only in JAIR, `russo2018ids`) plus 1 annotation difference (`haarnoja2018sac`) |
| Cited keys with no bibliography entry | none in either master |
| Bibliography entries never cited | none in either master |
| LNCS natbib label defects | 1 (`haarnoja2018` / `haarnoja2018sac` year suffix) |

## 1. Key mapping and the 69 vs 68 difference

Keys only in the JAIR bibliography: `gundersen2024jair` (Gundersen, Helmert, Hoos, "Improving
reproducibility in AI research: Four mechanisms adopted by JAIR", JAIR 81:1019--1041, 2024).

Keys only in the LNCS bibliography: none.

Explanation: the extra JAIR entry is cited exactly once in `full_paper_jair.tex`, at line 1823, the
opening sentence of `\section{Reproducibility Checklist for JAIR}` ("This appendix answers the JAIR
reproducibility checklist \citep{gundersen2024jair} ..."). The LNCS master has no JAIR checklist
section (no match for "reproducibility checklist" in `full_paper.tex`), so it has no need for the
entry. The difference is legitimate.

Side note, not a citation defect: the header comment of `full_paper_jair.bib` still says "Converted
1:1 from the hand-rolled thebibliography block (68 entries)". It is stale by one entry since
`gundersen2024jair` was added.

Full mapping (year is the JAIR `year` field; cite counts are occurrences of the key across all cite
commands in each master):

| JAIR key | JAIR year | LNCS natbib label | JAIR cites | LNCS cites |
|---|---|---|---|---|
| `altman1999` | 1999 | Altman(1999) | 4 | 4 |
| `araya2010` | 2010 | Araya-López et al.(2010) | 7 | 7 |
| `bellemare2016` | 2016 | Bellemare et al.(2016) | 1 | 1 |
| `bernardo1979` | 1979 | Bernardo(1979) | 5 | 5 |
| `benchetrit2025` | 2025 | Benchetrit et al.(2025) | 2 | 2 |
| `blum1954` | 1954 | Blum(1954) | 2 | 1 |
| `boutilier2002` | 2002 | Boutilier(2002) | 1 | 1 |
| `burda2019` | 2019 | Burda et al.(2019) | 1 | 1 |
| `champion2024` | 2026 | Champion et al.(2026) | 2 | 2 |
| `cooper2026iwai` | 2026 | Cooper and Velasquez(2026) | 1 | 1 |
| `dacosta2020` | 2020 | Da Costa et al.(2020) | 1 | 1 |
| `dacosta2020b` | 2023 | Da Costa et al.(2023) | 4 | 3 |
| `devries2025` | 2025 | de Vries et al.(2025) | 2 | 2 |
| `duff2002` | 2002 | Duff(2002) | 1 | 1 |
| `fehr2018` | 2018 | Fehr et al.(2018) | 3 | 3 |
| `foster2021dad` | 2021 | Foster et al.(2021) | 2 | 2 |
| `fountas2020` | 2020 | Fountas et al.(2020) | 1 | 1 |
| `friston2010` | 2010 | Friston(2010) | 2 | 2 |
| `friston2015` | 2015 | Friston et al.(2015) | 1 | 1 |
| `friston2021` | 2021 | Friston et al.(2021) | 3 | 3 |
| `ghavamzadeh2015` | 2015 | Ghavamzadeh et al.(2015) | 1 | 1 |
| `gneiting2007` | 2007 | Gneiting and Raftery(2007) | 1 | 1 |
| `guez2013` | 2013 | Guez et al.(2013) | 1 | 1 |
| `gundersen2024jair` | 2024 | (none) | 1 | 0 |
| `haarnoja2018` | 2018 | Haarnoja et al.(2018) | 1 | 1 |
| `haarnoja2018sac` | 2018 | Haarnoja et al.(2018b) | 4 | 4 |
| `heins2022` | 2022 | Heins et al.(2022) | 2 | 2 |
| `houthooft2016` | 2016 | Houthooft et al.(2016) | 1 | 1 |
| `howard1966` | 1966 | Howard(1966) | 1 | 1 |
| `kaelbling1998` | 1998 | Kaelbling et al.(1998) | 2 | 2 |
| `kim2011cpomdp` | 2011 | Kim et al.(2011) | 4 | 4 |
| `kouw2026bethe` | 2026 | Kouw(2026) | 2 | 2 |
| `kurniawati2008` | 2008 | Kurniawati et al.(2008) | 3 | 3 |
| `laouar2026voi` | 2026 | Laouar et al.(2026) | 1 | 1 |
| `levine2018` | 2018 | Levine(2018) | 1 | 1 |
| `lindley1956` | 1956 | Lindley(1956) | 3 | 3 |
| `maisto2025` | 2025 | Maisto et al.(2025) | 1 | 1 |
| `matejka2015` | 2015 | Matějka and McKay(2015) | 4 | 4 |
| `millidge2020` | 2020 | Millidge et al.(2020) | 1 | 1 |
| `millidge2021` | 2021 | Millidge et al.(2021) | 2 | 2 |
| `oudeyer2007` | 2007 | Oudeyer and Kaplan(2007) | 1 | 1 |
| `parr2019` | 2019 | Parr and Friston(2019) | 3 | 3 |
| `parr2022` | 2022 | Parr et al.(2022) | 1 | 1 |
| `pathak2017` | 2017 | Pathak et al.(2017) | 1 | 1 |
| `pineau2003` | 2003 | Pineau et al.(2003) | 1 | 1 |
| `rawlik2012` | 2012 | Rawlik et al.(2012) | 1 | 1 |
| `robbins1951` | 1951 | Robbins and Monro(1951) | 4 | 3 |
| `russo2014` | 2014 | Russo and Van Roy(2014) | 4 | 4 |
| `russo2018ids` | 2018 | Russo and Van Roy(2018) | 1 | 1 |
| `sajid2021` | 2021 | Sajid et al.(2021) | 1 | 1 |
| `satsangi2018` | 2018 | Satsangi et al.(2018) | 2 | 2 |
| `schmidhuber1991` | 1991 | Schmidhuber(1991) | 1 | 1 |
| `schuirmann1987` | 1987 | Schuirmann(1987) | 2 | 1 |
| `shani2013` | 2013 | Shani et al.(2013) | 1 | 1 |
| `silver2010` | 2010 | Silver and Veness(2010) | 4 | 4 |
| `sims2003` | 2003 | Sims(2003) | 4 | 4 |
| `smallwood1973` | 1973 | Smallwood and Sondik(1973) | 1 | 1 |
| `smith2004` | 2004 | Smith and Simmons(2004) | 8 | 7 |
| `spaan2015` | 2015 | Spaan et al.(2015) | 2 | 2 |
| `stocco2024recursive` | 2024 | Stocco et al.(2024) | 1 | 1 |
| `sunberg2018` | 2018 | Sunberg and Kochenderfer(2018) | 3 | 3 |
| `sweeney2026equivalences` | 2026 | Sweeney et al.(2026) | 1 | 1 |
| `todorov2007` | 2006 | Todorov(2006) | 1 | 1 |
| `towers2024` | 2024 | Towers et al.(2024) | 2 | 2 |
| `tschantz2020` | 2020 | Tschantz et al.(2020) | 1 | 1 |
| `walraven2024` | 2025 | Walraven et al.(2025) | 1 | 1 |
| `wei2024voi` | 2024 | Wei(2024) | 1 | 1 |
| `ye2017` | 2017 | Ye et al.(2017) | 1 | 1 |
| `kushner1978` | 1978 | Kushner and Clark(1978) | 3 | 2 |

Cite counts differ for six keys (`blum1954`, `dacosta2020b`, `robbins1951`, `schuirmann1987`,
`smith2004`, `kushner1978`), each by one extra JAIR cite. That reflects prose differences between the
masters, not bibliography differences, and is recorded here only for completeness.

## 2. Content mismatches between mapped pairs

Across all 68 mapped pairs, authors (full list, order, and count), title, venue, year, volume, issue,
pages, and arXiv id agree in substance in both directions. The mismatches found:

1. `russo2018ids`, field `doi`. JAIR has `doi = {10.1287/opre.2017.1663}`. The LNCS bibitem has no
   DOI. Everything else (authors, title, Operations Research, 66(1):230--252, 2018) agrees. This is
   an omission in LNCS, not a conflict. Whether the DOI resolves to this work is for the slice
   verifier covering this entry to confirm.
2. `haarnoja2018sac`, annotation. The LNCS bibitem ends with a note absent from the JAIR entry: "The
   applications paper introducing automatic entropy-temperature tuning. The earlier ICML 2018 paper
   uses a fixed temperature." The JAIR entry has no `note` field. The bibliographic data (eleven
   authors in the same order, title, arXiv:1812.05905, 2018) agree. This contradicts the JAIR bib's
   own header claim that notes were "preserved verbatim", but it is an annotation, not a data
   conflict.

Checked and dismissed as false positives: the author-order flags on `haarnoja2018sac` (short
surnames "Ha" and "Tan" match inside other names) and `kim2011cpomdp` (two authors named Kim). By-eye
reading confirms identical order in both.

Known key/year labeling mismatches, harmless because the printed year is what matters and it agrees
across masters: `champion2024` (year 2026), `dacosta2020b` (2023), `todorov2007` (2006),
`walraven2024` (2025).

## 3. Cited keys without entries, and entries never cited

JAIR (`full_paper_jair.tex` against `full_paper_jair.bib`): 69 distinct cited keys, 69 entries.
- Cited keys with no bibliography entry: none.
- Bibliography entries never cited: none.
- `\nocite`: none.

LNCS (`full_paper.tex` against its inline `thebibliography`): 68 distinct cited keys, 68 bibitems.
- Cited keys with no bibliography entry: none.
- Bibliography entries never cited: none.
- `\nocite`: none.

Note for anyone rerunning this: `gneiting2007` and `russo2018ids` are cited only in the LNCS
appendices (lines 1975 and 1933), which come after `\end{thebibliography}`. A scan that stops at the
bibliography will wrongly report them as uncited.

## 4. LNCS natbib labels against authors and year

Each label was checked against the bibitem's author list (one author gives "Surname", two give "A and
B", three or more or an explicit "et al." give "First et al.") and against the year printed in the
bibitem body and in the JAIR entry. 67 of 68 labels are correct, including the four keys whose names
carry a different year from the publication year (their labels use the correct publication year).

Defect:
- `haarnoja2018` has label `Haarnoja et~al.(2018)`, and `haarnoja2018sac` has label
  `Haarnoja et~al.(2018b)`. Both render as "Haarnoja et al." with year 2018, and they are the only
  duplicate label pair in the LNCS bibliography. A "b" suffix is used with no matching "a". The
  consistent natbib form is `Haarnoja et~al.(2018a)` for `haarnoja2018` (ICML 2018) and
  `Haarnoja et~al.(2018b)` for `haarnoja2018sac` (arXiv:1812.05905). As it stands, a reader sees
  "Haarnoja et al. (2018)" and "Haarnoja et al. (2018b)" and cannot tell which is the unsuffixed one.
  The two works are distinguished in the surrounding prose ("Soft actor-critic" versus "Soft
  Actor-Critic's automatic entropy-temperature tuning" / "applications paper"), so the risk is
  cosmetic.
  For comparison, the JAIR build (biblatex `acmauthoryear`, `uniquename=init`) assigns no
  `extradate` to either entry in `full_paper_jair.bbl`, because the author lists differ (4 versus 11
  authors). So JAIR prints both as "Haarnoja et al., 2018". That is standard biblatex behavior, not
  an entry error, but readers of the JAIR version get the same ambiguity.

JAIR labels are generated by biber from the `.bib` fields, so they need no separate check beyond
section 2.
