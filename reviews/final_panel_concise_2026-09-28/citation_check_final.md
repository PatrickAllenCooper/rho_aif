# Final citation-hallucination check (JAIR and LNCS masters)

Date: 2026-09-29. Read-only check; no manuscript or bibliography file was edited.

## Files checked (sha256)

| File | Role | sha256 |
|---|---|---|
| `paper/full_paper_jair.bib` | JAIR bibliography (`\addbibresource{full_paper_jair.bib}`) | `3b73ee000f5fbde7b69632d026fb9a9508d69f6c44b723dd2d95988d1e0b1235` |
| `paper/full_paper.tex` | LNCS master; embedded `thebibliography` at lines 831 to 1179 | `eda70226ccbc82cb4bfd5eb59d4e806147bf250f4f80ae0915314402f248177f` |
| `paper/full_paper.tex` lines 831 to 1179 | the embedded `thebibliography` block alone | `0cfd7156d332eb24a20888774ad0258d5e327141bb12a67d8a7ae08068bbea08` |
| `paper/full_paper_jair.tex` | JAIR master (citation contexts) | `5896a184006146a7a2d48bc2c3a0f4a5d535573c3e478821b8677edab69dc7f7` |

Working tree at HEAD `9e6ffde`, with both masters showing uncommitted modifications (`git status`), so the hashes above identify the exact text checked.

## Summary

- **Key resolution.** The JAIR master cites 69 distinct keys and all 69 resolve in `full_paper_jair.bib`, which holds exactly 69 entries, none uncited. The LNCS master cites 68 distinct keys and all 68 resolve to its 68 `\bibitem`s, none uncited. The only key not shared is `gundersen2024jair`, which the JAIR reproducibility-checklist appendix cites and the LNCS master does not, as intended.
- **Cross-master agreement.** For all 68 shared entries, a normalized field comparison found that every author surname, title, year, volume, number, pages, journal/booktitle, and arXiv eprint number in the `.bib` entry also appears in the corresponding `\bibitem`. First initials were compared by eye. No disagreements.
- **Primary-record verification.** 69 of 69 entries verified against a primary record. Zero hallucinated references. **Zero bibliographic discrepancies requiring correction.** Zero unverifiable. One entry, `cooper2026iwai`, is the authors' own forthcoming CCIS chapter. It is verified against its arXiv record (2607.16981, which states IWAI 2026 spotlight acceptance and forthcoming CCIS publication), and "To appear" is accurate because the workshop is 14 to 16 October 2026.
- **Prior-pass items still hold.** `devries2025` lists all 16 authors, in arXiv v4 order, with spelling matching the v4 PDF title page (including Raphaël Trésor and Marco Hidalgo Araya). `walraven2024` has G. J. Burghouts (Crossref: Gertjan J. Burghouts).
- **Advisories (not errors).** Three optional improvements:
  1. `towers2024` (Gymnasium) now has a published version, NeurIPS 2025 (Advances in Neural Information Processing Systems 38, pp. 163114 to 163129, DOI 10.52202/085713-4916). The arXiv citation is accurate as it stands.
  2. The sentence at JAIR line 116 cites `friston2010` for the EFE decomposition, which that 2010 review predates.
  3. The sentence at JAIR line 2156 cites `benchetrit2025` for progressive widening and double progressive widening. Benchetrit et al. use that technique but did not introduce it.

  The attribution audit found no citation that is plainly inconsistent with the cited work.
- **Key-year labels (cosmetic, unchanged from prior passes).** Four keys carry a year that differs from the printed year: `champion2024` (printed 2026), `dacosta2020b` (2023), `todorov2007` (2006), and `walraven2024` (2025). The printed years are correct and keys are not visible to readers.

## Method

- Keys: a regex over `\cite`, `\citet`, `\citep`, and variants in both masters, compared with the `.bib` entry list and the `\bibitem` list. Neither master uses `\nocite`.
- Journal articles and DOI-bearing proceedings: the Crossref REST API (`api.crossref.org/works?query.bibliographic=...` and `/works/<doi>`), checking title, full author list and order, container, volume, issue, pages, and print/online/issued dates.
- arXiv preprints: the arXiv export API (`export.arxiv.org/api/query?id_list=...`) for title, authors, first-submission date, comments, and journal_ref. The de Vries and Gymnasium records were also checked against arXiv abs-page metadata and, for de Vries, the v4 PDF title page.
- Conference papers without Crossref records: official proceedings indexes (papers.nips.cc year listings, proceedings.mlr.press paper pages, ijcai.org proceedings tables of contents, iclr.cc virtual site, BAICS 2020 workshop paper list), with OpenAlex as a secondary check for volume and pages.
- Books and theses: the Springer (Crossref) record for Kushner and Clark, and the CRC/Taylor & Francis front matter and ISBN 978-0-8493-0382-1 for Altman. For Duff: the ScholarWorks@UMass record (via Exa), the Mathematics Genealogy Project, and Duff's 2002 thesis announcement.
- Attributions: every citing sentence in `full_paper_jair.tex` (about 100 distinct sentences) was extracted and read against the cited work's abstract (Crossref, arXiv, or publisher page). Where a claim goes beyond the abstract, the full text was checked, namely Russo and Van Roy's Example 1 (arXiv 1403.5556) and Satsangi et al.'s equivalence statement (Springer full text).
- DBLP and OpenReview blocked scripted access (bot challenge) and were not used. ICLR 2019 and BAICS 2020 were confirmed via iclr.cc and the workshop site instead.

## Per-entry table

"Yes" means the work exists and the title, all listed authors (order and spelling, with initials as printed), the published year, and the venue/volume/issue/pages stated in the entry match the primary record.

| Key | Verified | Source used | Discrepancy / note |
|---|---|---|---|
| altman1999 | yes | CRC/T&F front matter (c) 1999, ISBN 978-0-8493-0382-1; Google Books (CRC Press, 30 Mar 1999) | None. Crossref's only DOI is the 2021 Routledge re-issue, and 1999 Chapman & Hall/CRC is the original. |
| araya2010 | yes | papers.nips.cc 2010 listing (NeurIPS 23); OpenAlex (vol 23, pp. 64 to 72) | None. The NeurIPS listing prints "Mauricio Araya", and Araya-López is his full surname. |
| bellemare2016 | yes | papers.nips.cc 2016 listing; OpenAlex (NeurIPS 29, pp. 1479 to 1487) | None |
| bernardo1979 | yes | Crossref 10.1214/aos/1176344689; Project Euclid ("Ann. Statist. 7(3): 686-690, May 1979") | None |
| benchetrit2025 | yes | arXiv 2502.02549v1 (4 Feb 2025), 4 authors | None. No published version found on Crossref. |
| blum1954 | yes | Crossref 10.1214/aoms/1177728794, 25(2):382 to 386 | None |
| boutilier2002 | yes | ACM DL / OpenAlex 10.5555/777092.777132, AAAI-02 pp. 239 to 246 | None |
| burda2019 | yes | iclr.cc/virtual/2019/poster/1093; Edinburgh Research Explorer record (ICLR 2019); arXiv 1810.12894 | None |
| champion2024 | yes | Crossref 10.1162/neco.a.1491, Neural Computation 38(3):439 to 469, 2026 | None. The key says 2024 but the printed year 2026 is correct (cosmetic). |
| cooper2026iwai | yes | arXiv 2607.16981 (title, authors, IWAI 2026 spotlight and CCIS statement) | None. Forthcoming, so "To appear" is correct. |
| dacosta2020 | yes | Crossref 10.1016/j.jmp.2020.102447, 99:102447 | None |
| dacosta2020b | yes | Crossref 10.1162/neco_a_01574, 35(5):807 to 852, 2023 | None. The key says 2020 but the printed year 2023 is correct (cosmetic). |
| devries2025 | yes | arXiv 2504.14898v4 API, abs metadata, and v4 PDF title page (16 authors) | None. All 16 authors are present and in order, matching the 2026-09-28 fix. |
| duff2002 | yes | ScholarWorks@UMass record; Math Genealogy Project; 2002 thesis announcement | None |
| fehr2018 | yes | papers.nips.cc 2018 listing; OpenAlex (NeurIPS 31, pp. 6933 to 6943) | None |
| foster2021dad | yes | proceedings.mlr.press/v139/foster21a (PMLR 139:3384 to 3395) | None |
| fountas2020 | yes | papers.nips.cc 2020 listing; arXiv 2006.04176 | None |
| friston2010 | yes | Crossref 10.1038/nrn2787, 11(2):127 to 138 | None |
| friston2015 | yes | Crossref 10.1080/17588928.2015.1020053, 6(4):187 to 214 | None |
| friston2021 | yes | Crossref 10.1162/neco_a_01351, 33(3):713 to 763 | None |
| ghavamzadeh2015 | yes | Crossref 10.1561/2200000049, 8(5 to 6):359 to 483 | None |
| gneiting2007 | yes | OpenAlex/DOI 10.1198/016214506000001437, JASA 102(477):359 to 378 | None |
| guez2013 | yes | Crossref 10.1613/jair.4117, 48:841 to 883 | None |
| gundersen2024jair | yes | Crossref 10.1613/jair.1.16905, JAIR 81:1019 to 1041 | None (JAIR only) |
| haarnoja2018 | yes | proceedings.mlr.press/v80/haarnoja18b (ICML 2018, 4 authors) | None |
| haarnoja2018sac | yes | arXiv 1812.05905 (11 authors, Dec 2018) | None |
| heins2022 | yes | Crossref 10.21105/joss.04098, JOSS 7(73):4098 | None |
| houthooft2016 | yes | papers.nips.cc 2016 listing; arXiv 1605.09674 (NeurIPS 29, pp. 1109 to 1117) | None. The NeurIPS site lists "Xi Chen" twice, a proceedings-site artifact. The arXiv record has 6 authors, as the bibliography does. |
| howard1966 | yes | Crossref 10.1109/tssc.1966.300074, 2(1):22 to 26 | None |
| kaelbling1998 | yes | Crossref 10.1016/s0004-3702(98)00023-x, 101(1 to 2):99 to 134 | None |
| kim2011cpomdp | yes | ijcai.org IJCAI 2011 TOC: starts p. 1968, next paper p. 1975 (DOI 10.5591/978-1-57735-516-8/IJCAI11-329) | None |
| kouw2026bethe | yes | arXiv 2608.17167v1 (17 Aug 2026), W. M. Kouw | None |
| kurniawati2008 | yes | Crossref 10.15607/rss.2008.iv.009 (RSS IV) | None |
| laouar2026voi | yes | Crossref 10.1609/icaps.v36i1.42824, ICAPS 36(1):152 to 160 | None |
| levine2018 | yes | arXiv 1805.00909 | None |
| lindley1956 | yes | Crossref 10.1214/aoms/1177728069, 27(4):986 to 1005 | None |
| maisto2025 | yes | Crossref 10.1016/j.neucom.2024.129319, 623:129319 | None |
| matejka2015 | yes | Crossref 10.1257/aer.20130047, 105(1):272 to 298 | None |
| millidge2020 | yes | Crossref 10.1007/978-3-030-64919-7_1 (IWAI 2020, CCIS, pp. 3 to 11) | None |
| millidge2021 | yes | Crossref 10.1162/neco_a_01354, 33(2):447 to 482 | None |
| oudeyer2007 | yes | Frontiers article page metadata (Oudeyer and Kaplan, vol 1, article 6, 2007) | None. Crossref's record omits Kaplan, but the publisher page lists both authors. |
| parr2019 | yes | Crossref 10.1007/s00422-019-00805-w, 113(5 to 6):495 to 513 | None |
| parr2022 | yes | Crossref 10.7551/mitpress/12441.001.0001 (MIT Press 2022) | None |
| pathak2017 | yes | proceedings.mlr.press/v70/pathak17a (ICML 2017) | None |
| pineau2003 | yes | ijcai.org IJCAI 2003 TOC (p. 1025) | None |
| rawlik2012 | yes | Crossref 10.15607/rss.2012.viii.045 (RSS VIII) | None |
| robbins1951 | yes | Crossref 10.1214/aoms/1177729586, 22(3):400 to 407 | None |
| russo2014 | yes | papers.nips.cc 2014 listing (NeurIPS 27) | None |
| russo2018ids | yes | Crossref 10.1287/opre.2017.1663, 66(1):230 to 252 | None |
| sajid2021 | yes | Crossref 10.1162/neco_a_01357, 33(3):674 to 712 | None |
| satsangi2018 | yes | Crossref 10.1007/s10514-017-9666-5, 42(2):209 to 233 (print 2018) | None |
| schmidhuber1991 | yes | Crossref 10.7551/mitpress/3115.003.0030 (From Animals to Animats, SAB 1991, pp. 222 to 228) | None |
| schuirmann1987 | yes | Crossref 10.1007/bf01068419, 15(6):657 to 680 | None |
| shani2013 | yes | Crossref 10.1007/s10458-012-9200-2, 27(1):1 to 51 (print 2013) | None |
| silver2010 | yes | papers.nips.cc 2010 listing; OpenAlex (NeurIPS 23, pp. 2164 to 2172) | None |
| sims2003 | yes | Crossref 10.1016/s0304-3932(03)00029-1, 50(3):665 to 690 | None |
| smallwood1973 | yes | Crossref 10.1287/opre.21.5.1071, 21(5):1071 to 1088 | None |
| smith2004 | yes | ACM DL / OpenAlex 10.5555/1036843.1036906 (UAI 2004, pp. 520 to 527) | None |
| spaan2015 | yes | Crossref 10.1007/s10458-014-9279-8, 29(6):1157 to 1185 (print 2015) | None |
| stocco2024recursive | yes | Crossref 10.1609/icaps.v34i1.31518, ICAPS 34:565 to 569 | None |
| sunberg2018 | yes | Crossref 10.1609/icaps.v28i1.13882 (ICAPS 28, pp. 259 to 263) | None |
| sweeney2026equivalences | yes | Crossref 10.3390/e28010001, Entropy 28(1):1 | None. Online 19 Dec 2025, but the issue is January 2026, so 2026 is the volume year. |
| todorov2007 | yes | papers.nips.cc 2006 listing (NeurIPS 19); Crossref MIT Press chapter pp. 1369 to 1376 | None. The key says 2007 but the printed year 2006 is correct (cosmetic). |
| towers2024 | yes | arXiv 2407.17032v4, 16 authors in the bibliography's order | None as cited. **Advisory:** a published version exists, NeurIPS 2025 (Crossref 10.52202/085713-4916). |
| tschantz2020 | yes | BAICS 2020 (ICLR workshop) accepted-papers page; arXiv 2002.12636 | None |
| walraven2024 | yes | Crossref 10.1007/s10458-024-09683-4, 39(1), article 3 (print 2025) | None. Burghouts is correct. The key says 2024 but the printed year 2025 is correct (cosmetic). |
| wei2024voi | yes | arXiv 2408.06542 (Ran Wei) | None |
| ye2017 | yes | Crossref 10.1613/jair.5328, 58:231 to 266 | None |
| kushner1978 | yes | Crossref 10.1007/978-1-4684-9352-8 (Applied Mathematical Sciences, Springer 1978) | None. The series volume is not in Crossref, but 26 is the standard record. |

## Attribution spot-check (JAIR master)

All of the roughly 100 distinct citing sentences were read against the cited works. None is plainly inconsistent with its cited work. The items below were checked most closely because the claim is specific.

- `russo2018ids`, "every stationary deterministic policy incurs linear regret for some prior ... randomization playing a fundamental role": matches Example 1 of Russo and Van Roy nearly word for word.
- `satsangi2018`, "show that these two formulations are equivalent" (POMDP-IR and rho-POMDP): matches the paper, which reduces each to the other with the value function preserved.
- `kim2011cpomdp`, optimal constrained POMDP policies may require randomization and use point-based DP over (belief, admissible cost): consistent with the paper.
- `dacosta2020b`, Bellman optimality of recursive (sophisticated) inference on finite horizons: consistent with the abstract, which says the standard scheme is optimal for horizon 1 only and the recursive scheme for any finite horizon.
- `laouar2026voi`, VOIMCP "selectively disregarding observation information when the VOI is low": matches the abstract.
- `stocco2024recursive`, Lagrangian-guided MCTS with history-dependent duals and recursive dual ascent: matches the abstract.
- `silver2010`, the R_hi minus R_lo rule for the UCB constant from preliminary runs: consistent with the POMCP paper's experimental setup.
- `devries2025`, "augmented with preference and epistemic priors": matches the abstract. `wei2024voi`, "EFE optimality-gap analysis": matches the abstract. `sweeney2026equivalences`, "survey of formal equivalences": the paper is a review of formal correspondences.
- `bernardo1979`, expected improvement in log score equals expected information gain: matches the abstract.
- `boutilier2002`, preference elicitation as a POMDP over the utility (state-dependent rewards), trading elicitation effort against decision quality: consistent.

Two advisory attribution notes (low severity, optional):

1. JAIR line 116 (and the LNCS mirror, line 82): "Its Expected Free Energy (EFE) objective combines pragmatic value with expected information gain \citep{friston2010,parr2019}." Friston (2010) is the free-energy-principle review, which predates the pragmatic-plus-epistemic EFE decomposition, first set out in Friston et al. (2015). Optional: `\citep{friston2010,parr2019}` to `\citep{friston2015,parr2019}` in both masters. Line 141 already uses `friston2015` for the same point.
2. JAIR line 2156: "such as progressive widening or double progressive widening \citep{benchetrit2025}". Benchetrit et al. build their rho-POMCPOW planner on progressive widening but did not introduce it. Optional: `\citep{sunberg2018,benchetrit2025}`, since `sunberg2018` is already in the bibliography and is cited for POMCPOW's progressive widening at line 129. Apply the same change in the LNCS mirror at `full_paper.tex` line 2460.

## Counts

- Verified: 69 of 69
- Bibliographic discrepancies requiring correction: 0
- Unverifiable: 0
- Advisories (optional, non-error): 3 (towers2024 published version, friston2010 attribution, benchetrit2025 attribution)
