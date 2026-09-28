# Citation integrity, slice C (entries 47-69 of `paper/full_paper_jair.bib`)

Checked 2026-09-28. Entries 47-69 in file order run from `robbins1951` to `kushner1978` (23 entries).
Every verdict below rests on a primary record fetched in this session: Crossref API work records,
arXiv API or abs pages, papers.nips.cc proceedings pages, the Springer book page, or the BAICS 2020
workshop programme page. Citation contexts were read in `paper/full_paper_jair.tex`.

## Summary

- VERIFIED: 22
- DISCREPANCY: 1 (`schmidhuber1991`, a one-page difference in the page range)
- Not found (possible hallucination): 0
- Clear misattributions in the manuscript: 0

## Per-entry results

| # | Key | Verdict | Primary record checked |
|---|-----|---------|------------------------|
| 47 | robbins1951 | VERIFIED | https://api.crossref.org/works/10.1214/aoms/1177729586 |
| 48 | russo2014 | VERIFIED | https://papers.nips.cc/paper_files/paper/2014/hash/90720a2fcc41f9332e6a1558da327089-Abstract.html |
| 49 | russo2018ids | VERIFIED | https://api.crossref.org/works/10.1287/opre.2017.1663 |
| 50 | sajid2021 | VERIFIED | https://api.crossref.org/works/10.1162/neco_a_01357 |
| 51 | satsangi2018 | VERIFIED | https://api.crossref.org/works/10.1007/s10514-017-9666-5 |
| 52 | schmidhuber1991 | DISCREPANCY (pages) | https://api.crossref.org/works/10.7551/mitpress/3115.003.0030 |
| 53 | schuirmann1987 | VERIFIED | https://api.crossref.org/works/10.1007/bf01068419 |
| 54 | shani2013 | VERIFIED | https://api.crossref.org/works/10.1007/s10458-012-9200-2 |
| 55 | silver2010 | VERIFIED | https://papers.nips.cc/paper_files/paper/2010/hash/edfbe1afcf9246bb0d40eb4d8027d90f-Abstract.html |
| 56 | sims2003 | VERIFIED | https://api.crossref.org/works/10.1016/s0304-3932(03)00029-1 |
| 57 | smallwood1973 | VERIFIED | https://api.crossref.org/works/10.1287/opre.21.5.1071 |
| 58 | smith2004 | VERIFIED | https://arxiv.org/abs/1207.4166 ("Appears in Proceedings of the Twentieth Conference on Uncertainty in Artificial Intelligence (UAI2004)", UAI-P-2004-PG-520-527) |
| 59 | spaan2015 | VERIFIED | https://api.crossref.org/works/10.1007/s10458-014-9279-8 |
| 60 | stocco2024recursive | VERIFIED | https://api.crossref.org/works/10.1609/icaps.v34i1.31518 |
| 61 | sunberg2018 | VERIFIED | https://api.crossref.org/works/10.1609/icaps.v28i1.13882 |
| 62 | sweeney2026equivalences | VERIFIED | https://api.crossref.org/works/10.3390/e28010001 |
| 63 | todorov2007 | VERIFIED | https://papers.nips.cc/paper_files/paper/2006/hash/d806ca13ca3449af72a1ea5aedbed26a-Abstract.html and Crossref 10.7551/mitpress/7503.003.0176 |
| 64 | towers2024 | VERIFIED | https://arxiv.org/abs/2407.17032 (arXiv API) |
| 65 | tschantz2020 | VERIFIED | https://arxiv.org/abs/2002.12636 (arXiv API) and https://baicsworkshop.github.io/papers.html |
| 66 | walraven2024 | VERIFIED | https://api.crossref.org/works/10.1007/s10458-024-09683-4 |
| 67 | wei2024voi | VERIFIED | https://arxiv.org/abs/2408.06542 (arXiv API) |
| 68 | ye2017 | VERIFIED | https://api.crossref.org/works/10.1613/jair.5328 |
| 69 | kushner1978 | VERIFIED | https://api.crossref.org/works/10.1007/978-1-4684-9352-8 and https://link.springer.com/book/10.1007/978-1-4684-9352-8 ("AMS, volume 26") |

## Discrepancies

### schmidhuber1991

- Field: `pages`
- Current value: `222--227`
- Correct value per the primary record: `222--228`. Crossref lists the chapter in MIT Press's *From
  Animals to Animats* (DOI 10.7551/mitpress/3115.003.0030) as pages 222-228.
- Severity: trivial. Many secondary sources cite 222-227, so the gap may just be a trailing blank or
  reference page. Every other field matches: sole author Schmidhuber, J., the exact title, the
  Simulation of Adaptive Behavior proceedings (published as *From Animals to Animats*), and 1991.

## Checks that passed, with notes

These are not discrepancies. Each field matched the primary record, and these notes save a later
reader from re-checking them.

- robbins1951: Robbins, Monro, Ann. Math. Stat. 22(3):400-407, 1951.
- russo2014 and russo2018ids share a title and are two distinct, real works: the NeurIPS 2014
  conference paper and the Operations Research 66(1):230-252 (2018) journal paper, whose DOI
  10.1287/opre.2017.1663 resolves to the journal paper.
- sajid2021: all four authors in order, Neural Computation 33(3):674-712, 2021.
- satsangi2018: all four authors in order, Autonomous Robots 42(2):209-233, 2018.
- schuirmann1987: J. Pharmacokinet. Biopharm. 15(6):657-680, 1987.
- shani2013: Shani, Pineau, Kaplow, AAMAS 27(1):1-51, 2013.
- silver2010: Silver, Veness, NeurIPS 2010. The entry has no pages field, which is optional.
- sims2003: J. Monetary Economics 50(3):665-690, 2003.
- smallwood1973: Operations Research 21(5):1071-1088, 1973.
- smith2004: Smith, Simmons, UAI 2004 (pages 520-527 per the arXiv comment, no pages field in the entry).
- spaan2015: Spaan, Veiga, Lima, AAMAS 29(6):1157-1185, 2015.
- stocco2024recursive: Stocco, Chundi, Jamgochian, Kochenderfer, ICAPS 34, pp. 565-569, 2024.
- sunberg2018: Sunberg, Kochenderfer, ICAPS 28, 2018 (pages 259-263 per Crossref, no pages field in the entry).
- sweeney2026equivalences: Sweeney, Ruiz-Serra, Harre, Entropy 28(1), article 1. Crossref gives the
  online date as 2025-12-19. It belongs to the 2026 volume, so `year = 2026` is defensible.
- todorov2007: the key says 2007 but the printed year is 2006, which is correct (NeurIPS 19, the 2006
  conference; the MIT Press volume carries a 2007 date). This key-versus-year mismatch was already
  known from ledger 9.12.
- towers2024: all 16 authors match the arXiv record in order. The arXiv comment says "Accepted at
  NeurIPS Datasets and Benchmarks 2025". Citing the published version is optional, and the arXiv
  citation is not wrong.
- tschantz2020: Tschantz, Millidge, Seth, Buckley. arXiv 2002.12636 exists, and the BAICS
  workshop (ICLR 2020) programme lists "Reinforcement Learning through Active Inference" as a spotlight.
- walraven2024: the key says 2024 but the printed year is 2025, which is correct. Walraven, Sijs,
  Burghouts, AAMAS 39(1), article 3, issue dated 2025 (the article was online in 2024). Also known from
  ledger 9.12.
- wei2024voi: sole author Ran Wei, arXiv 2408.06542, 2024.
- ye2017: Ye, Somani, Hsu, Lee, JAIR 58:231-266, 2017.
- kushner1978: Kushner, Clark, Springer Applied Mathematical Sciences vol. 26, 1978.

## Citation-context check (paper/full_paper_jair.tex)

I read every sentence that cites a key in this slice. None misattributes its source. The claims most
worth checking, and what the source shows:

- sweeney2026equivalences (line 143) is said to "survey formal correspondences between EFE
  minimization and six decision-theoretic frameworks". The Crossref abstract names Bayesian decision
  theory, resource rationality, optimal control, reinforcement learning, rate-distortion theory, and
  maximum entropy, and calls the paper a review. The claim matches.
- stocco2024recursive (line 519) is said to apply "Lagrangian-guided Monte Carlo tree search with
  recursive, history-dependent dual ascent" inside CPOMDP planning. The abstract says
  "history-dependent dual variables ... optimized with recursive dual ascent" within Lagrangian-guided
  MCTS for CPOMDPs. The claim matches.
- wei2024voi (line 143) is said to analyze EFE's optimality gap against a reward-driven
  Bayes-optimal policy in a belief-MDP casting, via information value. The abstract says exactly this.
- satsangi2018 (lines 129 and 388) is said to show that POMDP-IR and rho-POMDPs are equivalent. This
  matches the paper's known equivalence result.
- silver2010 (lines 120, 1042 and 1748): POMCP is described as UCB1 MCTS with rollouts, and the
  constant is attributed to an R_hi - R_lo rule. Both are standard content of the NeurIPS 2010 paper.
- smith2004 (lines 544 and 1867) lists how the original RockSample differs from this paper's variant:
  free moves and checks, +10 exit at the east edge, perfect check accuracy at zero distance, and
  sampled rocks turning bad. These match the original benchmark.
- robbins1951 and kushner1978 (lines 491, 497, 500 and 1842) are used for the Robbins-Monro recursion,
  its sign and separation conditions (continuity of M is not required), and the constrained or
  projected recursion. All are appropriate. blum1954 is outside this slice.
- russo2014 and russo2018ids (lines 134, 392, 783 and 1646): the information ratio (squared regret over
  information gain), randomized policies over D(A), and the journal version's example showing that
  deterministic policies can incur linear regret. All are consistent with the sources.
- tschantz2020 (line 149) is cited for the FEEF objective, which that paper introduces.
- schuirmann1987 (TOST), sims2003 (Shannon-capacity constraint), smallwood1973, shani2013, ye2017,
  sunberg2018 (POMCPOW, progressive widening), spaan2015, sajid2021, schmidhuber1991 (curiosity),
  todorov2007 (control as inference), towers2024 (Gymnasium API) and walraven2024 are all cited
  appropriately.

## Entries not located

None. All 23 entries were found in a primary record.


## Correction after the independent two-agent pass, 2026-09-28

The blanket attribution verdict above for PI-5's sign/separation hypotheses was too strong. Inspection of Robbins and Monro (1951), pp. 404–405, shows that its first convergence theorem uses uniform separation and a specified step-size class, while its second uses monotonicity, equality at the root, and a positive derivative. Neither states the more general annulus-separation hypothesis used in PI-5. A cubic crossing satisfies PI-5 but not those original theorem hypotheses. The conclusion in PI-5 is valid; the revised manuscript supplies a direct projected squared-distance supermartingale proof for its bounded scalar setting, retaining Robbins–Monro, Blum, and Kushner as historical/background citations rather than an exact theorem mapping. See `reviews/final_two_agent_2026-09-28/reviewer_theory_round1.md`, R1, for the primary-source link and counterexample. Bibliographic metadata are unchanged.
