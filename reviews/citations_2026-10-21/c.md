# Citation audit C — 2026-10-21

Baseline `68a9c137c4529675b3fe097ccda351e464dc3afc`. Fresh primary checks of 23 entries and all 38 manuscript citation occurrences. The sole input, `paper/tables/rocksample_main.tex`, has no citations. No manuscript or bibliography edits were made.

All 23 works are real. No required metadata or attribution correction was identified. One minor primary-source disagreement remains: the Schmidhuber chapter ends at 228 in publisher-deposited metadata and 227 in the author HTML. The current entry follows the publisher. This is not a hallucinated reference.

The UCI primary page also contains both legacy research-only text and a current CC BY 4.0 panel. Current manuscript wording safely refers research users to the primary terms. Do not turn this into a claim that the repository MIT license covers the external measurements.

The JSON report records every bibliographic field and occurrence. All dates use issue/conference years where applicable. Metadata verification from a publisher deposit is distinguished from reading full text, and blocked full-text routes are listed.

## sajid2021

Authenticity: verified real work. Metadata: all fields present in the entry checked and consistent.

Primary sources checked:
- https://api.crossref.org/works/10.1162/neco_a_01357

- Line 156: Publisher-deposited abstract explicitly describes epistemic exploration and reward-free environments. Supports the limited claim that EFE can produce intrinsic-motivation behavior; manuscript does not import all claims of this source.

Access/scope: Metadata and relevant claim checked against publisher-deposited Crossref abstract; full article not needed for the narrow attribution.

## satsangi2018

Authenticity: verified real work. Metadata: all fields present in the entry checked and consistent.

Primary sources checked:
- https://api.crossref.org/works/10.1007/s10514-017-9666-5
- https://link.springer.com/article/10.1007/s10514-017-9666-5

- Line 139: Publisher abstract explicitly establishes reductions between rho-POMDP and POMDP-IR and equality of corresponding policy values. Supports the stated relationship.
- Line 293: Publisher abstract/full text concerns explicit information rewards and the rho-POMDP/POMDP-IR construction. Supports historical lineage of information-reward planning; manuscript proves its own particular weight equivalence separately.

Note: Printed issue February 2018, online August 29, 2017. Current 2018 year is correct.

## schmidhuber1991

Authenticity: verified real work. Metadata: publisher-supported, with the page-range disagreement below.

Primary sources checked:
- https://api.crossref.org/works/10.7551/mitpress/3115.003.0030
- https://people.idsia.ch/~juergen/curiositysab/curiositysab.html
- https://people.idsia.ch/~juergen/curiositysab/node2.html

- Line 156: Author full text, Section 2, adds curiosity reinforcement from prediction mismatch and discusses relative strengths of goal-directed and curiosity reinforcement. Supports the weighted exploration-bonus lineage.

Note: Publisher-deposited Crossref page range is 222–228, matching the bibliography. The author-hosted HTML lists 222–227. Both are real primary records for the same work. Retain publisher metadata unless the printed chapter itself resolves this one-page discrepancy. No claim or authenticity issue.

Access/scope: Publisher PDF returned HTTP 403. Thus the physical last page is unresolved between publisher metadata 228 and author HTML 227.

## schuirmann1987

Authenticity: verified real work. Metadata: all fields present in the entry checked and consistent.

Primary sources checked:
- https://api.crossref.org/works/10.1007/bf01068419
- https://link.springer.com/article/10.1007/BF01068419

- Line 552: Publisher abstract describes the two one-sided test procedure and its relation to a 1−2α interval for the mean difference. Supports naming/using TOST, while margins, Welch formulation and multiplicity are this study’s methods.
- Line 1290: Same methodological attribution to TOST is supported. The paper’s own numeric outcomes are not attributed to Schuirmann.

## shani2013

Authenticity: verified real work. Metadata: all fields present in the entry checked and consistent.

Primary sources checked:
- https://api.crossref.org/works/10.1007/s10458-012-9200-2
- https://link.springer.com/article/10.1007/s10458-012-9200-2

- Line 135: Publisher abstract describes restricting value computations to a finite belief subset, local updates, and surveying point-based methods. Supports the grouped point-based-solver context.

Note: Printed issue July 2013, online June 8, 2012. Current 2013 year is correct.

Access/scope: Publisher full text is subscription content; metadata and relevant general claim were verified on the accessible publisher abstract.

## silver2010

Authenticity: verified real work. Metadata: all fields present in the entry checked and consistent.

Primary sources checked:
- https://papers.nips.cc/paper_files/paper/2010/hash/edfbe1afcf9246bb0d40eb4d8027d90f-Abstract.html
- https://papers.nips.cc/paper_files/paper/2010/file/edfbe1afcf9246bb0d40eb4d8027d90f-Paper.pdf

- Line 135: Full paper Section 3.1 (PDF page 3 onward) explicitly uses UCB1 for tree selection and rollout simulation. Supports the algorithm description.
- Line 958: Citation marks the original POMCP algorithm. Manuscript explicitly labels its observe-then-commit implementation an adaptation and discloses its different leaf/rollout choices, rather than attributing those choices to Silver and Veness.
- Line 1234: Full paper PDF page 6 sets c=R_hi−R_lo from preliminary POMCP and rollout returns. Confirms the manuscript’s distinction from its fixed commit-reward-range constant.

## sims2003

Authenticity: verified real work. Metadata: all fields present in the entry checked and consistent.

Primary sources checked:
- https://api.crossref.org/works/10.1016/s0304-3932(03)00029-1
- https://collaborate.princeton.edu/en/publications/implications-of-rational-inattention/

- Line 159: Author’s university record reproduces the abstract’s finite Shannon-capacity constraint. Supports the information-capacity background; pricing is jointly cited with Matejka and McKay.
- Line 454: Same primary abstract supports rational-inattention resource-constraint precedent in the grouped resource-control sentence. No claim that Sims supplies the manuscript’s projected controller theorem.

## smallwood1973

Authenticity: verified real work. Metadata: all fields present in the entry checked and consistent.

Primary sources checked:
- https://api.crossref.org/works/10.1287/opre.21.5.1071

- Line 135: Publisher-deposited abstract formulates finite-state Markov control with probabilistic observations of hidden state and finite-horizon policy computation. Supports the POMDP foundations statement.

## smith2004

Authenticity: verified real work. Metadata: all fields present in the entry checked and consistent.

Primary sources checked:
- https://arxiv.org/abs/1207.4166
- https://arxiv.org/pdf/1207.4166

- Line 135: Author paper describes HSVI as a point-based value-iteration approach with heuristic belief search. Supports its inclusion among point-based offline solvers.
- Line 244: Full paper Section 5, printed page 525, says sampled good rocks become bad. Confirms the disclosed fixed-quality variant difference.
- Line 469: Full paper Section 5 defines visible position, binary hidden qualities, noisy checks, sampling rewards and east-side exit. Manuscript explicitly distinguishes its altered benchmark.
- Line 1137: Full paper Section 5, printed pages 524–525, supports free non-sampling moves/checks, east-edge exit, good-to-bad sampling, and exponential distance-dependent sensing tending toward chance. Exact 0.5 cost, modified sensor and cap are openly stated as this project’s changes.

## spaan2015

Authenticity: verified real work. Metadata: all fields present in the entry checked and consistent.

Primary sources checked:
- https://api.crossref.org/works/10.1007/s10458-014-9279-8
- https://link.springer.com/article/10.1007/s10458-014-9279-8

- Line 139: Publisher abstract introduces POMDP-IR for active cooperative perception and real robot-assisted surveillance. Directly supports attribution.
- Line 293: Publisher abstract describes explicit information rewards in the standard POMDP framework. Supports lineage; not asserted to prove the present EFE coefficient theorem.

Note: Printed issue November 2015, online December 23, 2014. Current 2015 year is correct.

Access/scope: Publisher full text is subscription content; metadata and the two limited lineage claims were verified on the accessible publisher abstract.

## stocco2024recursive

Authenticity: verified real work. Metadata: all fields present in the entry checked and consistent.

Primary sources checked:
- https://api.crossref.org/works/10.1609/icaps.v34i1.31518
- https://ojs.aaai.org/index.php/ICAPS/article/view/31518

- Line 454: Publisher abstract explicitly introduces history-dependent dual variables optimized by recursive dual ascent inside Lagrangian-guided CPOMDP Monte Carlo planning. Supports the per-node versus across-episode distinction.

## sunberg2018

Authenticity: verified real work. Metadata: all fields present in the entry checked and consistent.

Primary sources checked:
- https://api.crossref.org/works/10.1609/icaps.v28i1.13882
- https://arxiv.org/abs/1709.06196
- https://arxiv.org/pdf/1709.06196

- Line 135: Author full text introduction and Sections 3–4 explicitly define POMCPOW with double progressive widening and weighted particle filtering. Supports continuous-space planner summary.

Access/scope: AAAI landing-page fetch returned HTTP 503. Publisher-deposited metadata and author-hosted arXiv full text were successfully checked.

## sweeney2026equivalences

Authenticity: verified real work. Metadata: all fields present in the entry checked and consistent.

Primary sources checked:
- https://api.crossref.org/works/10.3390/e28010001
- https://pubmed.ncbi.nlm.nih.gov/41593908/
- https://pmc.ncbi.nlm.nih.gov/articles/PMC12840411/

- Line 151: Publisher-deposited abstract and full article Section 1.2 describe a structured review of formal correspondences between EFE and six decision-theoretic frameworks. Supports the survey description without asserting all forms have the manuscript’s coefficient.

Note: Crossref journal-issue.published-online is January 2026 and PMC gives collection date January 2026. Article online publication is December 19, 2025. Current journal-issue year 2026 is correct. Page 1 is the article number.

Access/scope: MDPI direct page/PDF returned HTTP 429/403. Publisher Crossref deposit and publisher-deposited PMC full text were successfully checked, including January 2026 collection date.

## todorov2007

Authenticity: verified real work. Metadata: all fields present in the entry checked and consistent.

Primary sources checked:
- https://papers.nips.cc/paper_files/paper/2006/hash/d806ca13ca3449af72a1ea5aedbed26a-Abstract.html
- https://papers.nips.cc/paper_files/paper/2006/file/d806ca13ca3449af72a1ea5aedbed26a-Paper.pdf

- Line 156: Official paper introduces KL-regularized controlled versus passive transition probabilities and an exponential transform of the value function. It is appropriate foundational background in the grouped control-as-inference citation with Levine, rather than a claimed source of the present theorem.

Note: The key suffix is 2007, but the entry correctly uses the 2006 conference year, explicitly identified by official NeurIPS proceedings.

## towers2024

Authenticity: verified real work. Metadata: all fields present in the entry checked and consistent.

Primary sources checked:
- https://arxiv.org/abs/2407.17032

- Line 1135: Author arXiv abstract identifies Gymnasium as a standard environment API for reinforcement learning. Supports naming the interface. This is not evidence that the project itself uses it; that implementation fact belongs to the repository audit.

Note: All sixteen authors and their order match arXiv. The record now notes acceptance at NeurIPS Datasets and Benchmarks 2025. Citing the genuine 2024 arXiv preprint remains accurate.

## tschantz2020

Authenticity: verified real work. Metadata: all fields present in the entry checked and consistent.

Primary sources checked:
- https://arxiv.org/abs/2002.12636
- https://baicsworkshop.github.io/papers.html

- Line 153: Author arXiv abstract explicitly combines active-inference ideas with reinforcement learning and demonstrates the resulting objective on RL benchmarks. Supports its role in the grouped scaling-work sentence; MCTS is supplied by the other grouped citations, not falsely assigned solely to this paper.

Note: Workshop programme and arXiv both verify the work. The workshop webpage misspells Tschantz as Tschanz; author-uploaded arXiv uses Tschantz, as does the manuscript.

## walraven2024

Authenticity: verified real work. Metadata: all fields present in the entry checked and consistent.

Primary sources checked:
- https://api.crossref.org/works/10.1007/s10458-024-09683-4
- https://link.springer.com/article/10.1007/s10458-024-09683-4

- Line 146: Publisher abstract explicitly bridges active inference and POMDP information gathering and introduces a tailored information-gathering approach. Direct support.

Note: The key suffix is 2024 but the entry correctly prints the 2025 issue year. Publisher identifies volume 39, article 3 (2025), online November 7, 2024. Crossref confirms issue 1.

Access/scope: Publisher full text is subscription content; all bibliographic fields and the general attribution are available in primary metadata/abstract.

## wei2024voi

Authenticity: verified real work. Metadata: all fields present in the entry checked and consistent.

Primary sources checked:
- https://arxiv.org/abs/2408.06542

- Line 151: Author arXiv abstract explicitly asks about EFE’s optimality gap against a reward-driven RL agent using belief-MDP analysis. Directly supports the limited optimality-gap-analysis description.

## ye2017

Authenticity: verified real work. Metadata: all fields present in the entry checked and consistent.

Primary sources checked:
- https://api.crossref.org/works/10.1613/jair.5328

- Line 135: Publisher-deposited abstract explicitly defines DESPOT as a sparse belief-tree approximation and describes optimizing a regularized objective. Direct support.

## kushner1978

Authenticity: verified real work. Metadata: all fields present in the entry checked and consistent.

Primary sources checked:
- https://api.crossref.org/works/10.1007/978-1-4684-9352-8
- https://link.springer.com/book/10.1007/978-1-4684-9352-8
- https://link.springer.com/content/pdf/bfm:978-1-4684-9352-8/1

- Line 447: Publisher front-matter preface states constrained extensions and projection forms of stochastic-approximation algorithms; contents list projection algorithms at pages 189 and 223. Supports historical/background citation. Manuscript supplies its own proof rather than importing unverified theorem hypotheses.
- Line 1263: Same front matter and contents support constrained stochastic-approximation background. No blanket equivalence to an external convergence theorem is claimed.

Note: Publisher front matter verifies Springer-Verlag New York, first edition 1978, Applied Mathematical Sciences volume 26. Ebook date 2012 is not the book year.

## vergara2012data

Authenticity: verified real work. Metadata: all fields present in the entry checked and consistent.

Primary sources checked:
- https://archive.ics.uci.edu/dataset/224/gas+sensor+array+drift+dataset

- Line 628: UCI primary page directly gives 13,910 measurements, 16 sensors, six gases and the eight-feature-per-sensor ordering. Supports dataset facts.
- Line 1146: UCI primary documentation gives all ten chronological batch ranges and the consecutive eight-descriptor sensor grouping. Supports these protocol premises.
- Line 1275: UCI primary page licenses research use in legacy text and CC BY 4.0 in its current panel. The manuscript defers external-data terms to UCI and does not apply the repository MIT license to measurements.
- Line 1294: UCI page verifies the named public dataset and original documentation. Split, checksum, duplicate checks and retrospective-access limitations are the authors’ protocol, not claims attributed to the dataset paper.

Note: The UCI page simultaneously contains a legacy research-only/noncommercial sentence and a current CC BY 4.0 license panel. Manuscript accurately limits its wording to research reproducibility and source attribution terms. This is a source-level license inconsistency, not a fabricated citation or a required manuscript correction.

## vergara2012

Authenticity: verified real work. Metadata: all fields present in the entry checked and consistent.

Primary sources checked:
- https://api.crossref.org/works/10.1016/j.snb.2012.01.074
- https://archive.ics.uci.edu/dataset/224/gas+sensor+array+drift+dataset

- Line 628: Crossref verifies the associated article’s identity and full author list. Co-cited UCI primary dataset record independently supplies all quantitative facts in this sentence. Publisher full-text fetch was blocked, so article-only verification of those numbers is not claimed.
- Line 1294: Article authenticity and role as the dataset’s originating study are consistent with the co-cited primary UCI documentation. This citation is not used to assert an uninspected theorem or result.

Access/scope: ScienceDirect article and abstract pages returned HTTP 403. Bibliographic metadata were checked from the publisher Crossref deposit; quantitative dataset facts from the co-cited UCI primary documentation.

## covert2023

Authenticity: verified real work. Metadata: all fields present in the entry checked and consistent.

Primary sources checked:
- https://proceedings.mlr.press/v202/covert23a.html

- Line 144: PMLR abstract explicitly proposes greedy conditional-mutual-information dynamic feature selection and amortized learned approximation. Direct support.
- Line 630: Same primary abstract supports the greedy-information comparator lineage. Manuscript explicitly states that it does not reproduce the neural acquisition method, avoiding over-attribution.
