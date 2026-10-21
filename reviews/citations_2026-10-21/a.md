# Citation audit A — 2026-10-21

23 real works; 39 manuscript uses. No fabricated reference or erroneous bibliography field was found. Thirty-five uses are directly supported at the depth of the claim. Four uses retain the explicit source-access/policy limitations below. No source edits were made by this reviewer.

Baseline commit: `68a9c137c4529675b3fe097ccda351e464dc3afc`. Baseline and final SHA-256 values are in `a.json`. Final source was rechecked after the parent changed line 454 to information prices and resource constraints. The only included TeX table has no citations.

## Remaining verification limits

- **Blum 1954, lines 447 and 1263:** publisher-deposited metadata is verified. Primary full text/abstract remained inaccessible. The generic almost-sure-convergence attribution is credible and consistent with the title, but it is not labeled fully verified from the original text. The manuscript proves its own scalar result.
- **Altman 1999, line 561:** author-hosted book contents establish the relevant finite/infinite MDP, Lagrangian and randomization chapters. Exact strong-duality hypotheses were not reread in the full book.
- **Gundersen et al. 2024, line 1244:** checklist submission requirement is verified. Removal from an accepted manuscript should be confirmed from current JAIR submission instructions; that detail was not located in the retrieved article portions.
- **Cooper and Velasquez 2026:** independently verified on arXiv and in the official IWAI program. The workshop site supports planned Springer CCIS proceedings. Existing **To appear** is appropriate; no published volume, DOI or pages were established. User-supplied acceptance is separate supporting evidence.

## Entry-by-entry record

### altman1999

**Real work; printed metadata matches.** Manuscript locations: 159, 350, 454, 561.
Author-hosted book page and complete contents identify the 1999 Chapman & Hall/CRC book. Chapters 3.3–3.5 and 4.3–4.4 explicitly cover constrained control, Lagrangian/dual LP formulations and randomization. The contents separate finite and infinite MDPs.

The parent changed line 454 from resource-price adaptation to information prices and resource constraints during the audit; final wording was rechecked.

Sources checked: [primary 1](https://www-sop.inria.fr/members/Eitan.Altman/mdp1.html); [primary 2](https://www-sop.inria.fr/members/Eitan.Altman/PAPERS/cont.txt).

Access/scope: Full book theorems and their exact hypotheses were not accessible in this pass. General attribution is supported by author-hosted contents; the strong-duality qualification at line 561 is appropriately cautious but not a freshly checked book theorem.

### araya2010

**Real work; printed metadata matches.** Manuscript locations: 104, 137, 204, 293.
Official PDF byline resolves abbreviated author names in the HTML record. Section 3.1 defines the full belief/action reward; theorem 3.1 and section 4 cover convex values and PWLC approximation. This supports the manuscript distinction between the original full reward and its own information-only rho.

Sources checked: [primary 1](https://proceedings.neurips.cc/paper/2010/hash/68053af2923e00204c3ca7c6a3150cf7-Abstract.html); [primary 2](https://proceedings.neurips.cc/paper_files/paper/2010/file/68053af2923e00204c3ca7c6a3150cf7-Paper.pdf).

### bellemare2016

**Real work; printed metadata matches.** Manuscript locations: 156.
Official NeurIPS record lists the six authors in manuscript order and describes density-model pseudo-counts used for exploration bonuses.

Sources checked: [primary 1](https://proceedings.neurips.cc/paper_files/paper/2016/hash/afda332245e2af431fb7b672a68b659d-Abstract.html).

Access/scope: Official full abstract was sufficient for this broad attribution; algorithm derivations were not re-audited.

### bernardo1979

**Real work; printed metadata matches.** Manuscript locations: 122, 142, 227, 1263.
All five pages of the author-hosted scan were rendered and visually inspected. Sections 2–4 define information gain and logarithmic proper utility; the final derivation identifies expected utility increase with a positive constant times EIG. Unit log score gives the manuscript identity.

Z=1 follows directly from the manuscript unit-log-score algebra, rather than being represented as a verbatim theorem of Bernardo. For A log p+B, the utility improvement is A times EIG; the manuscript specifies the unit log score.

Sources checked: [primary 1](https://api.crossref.org/works/10.1214/aos/1176344689); [primary 2](https://www.uv.es/~bernardo/publications.html); [primary 3](https://www.uv.es/~bernardo/1979AS.pdf).

### benchetrit2025

**Real work; printed metadata matches.** Manuscript locations: 137.
The author-deposited arXiv record verifies all four authors, title and 2025 submission. Its abstract describes an anytime incremental rho-POMDP planner in continuous spaces.

Sources checked: [primary 1](https://arxiv.org/abs/2502.02549).

Access/scope: Verified as an arXiv work, not as an accepted/published IJCAI paper. Bibliography claims only arXiv.

### blum1954

**Real work; printed metadata matches.** Manuscript locations: 447, 1263.
Publisher-deposited Crossref metadata exactly verifies Julius R. Blum, title, Annals of Mathematical Statistics 25(2), 382–386, 1954. The title supports almost-sure convergence as its subject. The original text and abstract were not successfully retrieved.

Sources checked: [primary 1](https://api.crossref.org/works/10.1214/aoms/1177728794).

Access/scope: Project Euclid DOI, article and legacy PDF routes, and JSTOR were inaccessible. Indexed secondary abstract corroborates the historical connection but was not substituted for primary-text verification. Both uses remain primary-text access-limited; the manuscript separately proves its bounded scalar result.

### boutilier2002

**Real work; printed metadata matches.** Manuscript locations: 139.
Author-hosted full paper section 3.1 uses utility functions as hidden states, query costs, and state-dependent terminal decision rewards. Section 3 distinguishes sequential elicitation from myopic expected value of information.

Sources checked: [primary 1](https://research.google/pubs/a-pomdp-formulation-of-preference-elicitation-problems/); [primary 2](https://www.cs.toronto.edu/~cebly/Papers/pefa-abs.html); [primary 3](https://www.cs.toronto.edu/~cebly/Papers/_download_/pefa.pdf).

### burda2019

**Real work; printed metadata matches.** Manuscript locations: 156.
Coauthor institutional publication record verifies all four authors, ICLR 2019 and exact title. The complete abstract describes a neural-network prediction-error exploration bonus and combining intrinsic and extrinsic rewards.

Sources checked: [primary 1](https://www.research.ed.ac.uk/en/publications/exploration-by-random-network-distillation/).

Access/scope: OpenReview direct access was blocked; institutional author record and full abstract independently support this narrow attribution. 2019 is conference year, not 2018 preprint year.

### champion2024

**Real work; printed metadata matches.** Manuscript locations: 151, 220.
Publisher metadata and author institutional record verify 2026, Neural Computation 38(3), 439–469 and all four authors. The abstract/full author manuscript discuss distinct EFE root definitions and associated restrictions on preference distributions.

Citation-key suffix 2024 is historical and not a false publication year. Printed year 2026 is correct.

Sources checked: [primary 1](https://api.crossref.org/works/10.1162/NECO.a.1491); [primary 2](https://kar.kent.ac.uk/113953/); [primary 3](https://kar.kent.ac.uk/113953/1/theophile26reframing.pdf).

### cooper2026iwai

**Real work; printed metadata matches.** Manuscript locations: 128.
ArXiv verifies title, Cooper/Velasquez and the July 2026 manuscript. Its sections contain EFE equivalence and benchmarks, including the older state-space-size claim. Official IWAI program lists the title and Patrick Cooper; workshop site identifies CCIS proceedings. User-supplied acceptance is separate corroboration.

Do not replace To appear with invented proceedings volume/pages. Official event has already occurred as of audit date; existence does not depend solely on future-event claims.

Sources checked: [primary 1](https://arxiv.org/abs/2607.16981); [primary 2](https://arxiv.org/html/2607.16981v1); [primary 3](https://iwaiworkshop.github.io/); [primary 4](https://iwaiworkshop.github.io/docs/IWAI_2026_program_detailed.pdf).

Access/scope: No published Springer volume, DOI or pagination was independently located. Acceptance and planned CCIS publication are verified; actual proceedings publication is not. Existing To appear note is appropriate. Exact abridged conference version length is based on user-provided acceptance context, not inferred from the 41-page arXiv preprint.

### dacosta2020

**Real work; printed metadata matches.** Manuscript locations: 149.
Publisher metadata verifies 2020, volume 99, article 102447 and six authors. Full author PDF section 7 decomposes EFE into extrinsic expected log evidence and intrinsic information gain.

ArXiv journal-reference text labels the journal 2021; publisher-deposited journal metadata gives December 2020 and agrees with bibliography. No correction warranted.

Sources checked: [primary 1](https://api.crossref.org/works/10.1016/j.jmp.2020.102447); [primary 2](https://arxiv.org/abs/2001.07203); [primary 3](https://arxiv.org/pdf/2001.07203).

### dacosta2020b

**Real work; printed metadata matches.** Manuscript locations: 149, 183, 220, 1263.
Full text section 4.3 theorem 16 gives finite-horizon recursive Bellman optimality in the zero-temperature preference limit. Section 5.2 explicitly extends to known-model POMDPs with exact inference. The manuscript retains these qualifications and rejects finite-weight reward optimality.

2023 is the journal year, despite historical key 2020b; title maximization follows the published US spelling.

Sources checked: [primary 1](https://api.crossref.org/works/10.1162/neco_a_01574); [primary 2](https://discovery.ucl.ac.uk/id/eprint/10168059/1/neco_a_01574.pdf); [primary 3](https://arxiv.org/abs/2009.08111); [primary 4](https://arxiv.org/html/2009.08111v4).

### devries2025

**Real work; printed metadata matches.** Manuscript locations: 151.
ArXiv v4 verifies all 16 authors in bibliography order, title and 2025 date. Full abstract/model discussion derives planning from an augmented generative model with preference and epistemic priors.

The earlier and others omission is no longer present. Wouter Kouw is fourth, and all 13 authors after the first three are now included.

Sources checked: [primary 1](https://arxiv.org/abs/2504.14898); [primary 2](https://arxiv.org/html/2504.14898v4).

### duff2002

**Real work; printed metadata matches.** Manuscript locations: 156.
University thesis record verifies Michael O’Gordon Duff, exact title, 2002 PhD and institution. Its full abstract describes exploration/exploitation through Bayesian treatment of unknown model parameters and hyperstates.

Sources checked: [primary 1](https://scholarworks.umass.edu/dissertations/AAI3039353/).

Access/scope: Full dissertation was not retrieved; the complete institutional abstract is sufficient for the broad claim made.

### fehr2018

**Real work; printed metadata matches.** Manuscript locations: 137.
Official proceedings metadata and full text verify four authors, title/year and a Lipschitz reward assumption. The paper treats rewards beyond convex functions and finite-horizon approximation; the manuscript explicitly states the Lipschitz hypothesis and does not rely on this guarantee.

Sources checked: [primary 1](https://proceedings.neurips.cc/paper_files/paper/2018/hash/de7f47e09c8e05e6021ababdf6bc58e7-Abstract.html); [primary 2](https://proceedings.neurips.cc/paper_files/paper/2018/file/de7f47e09c8e05e6021ababdf6bc58e7-Paper.pdf).

### foster2021dad

**Real work; printed metadata matches.** Manuscript locations: 142.
Official PMLR metadata verifies all four authors and pages 3384–3395. Section 2 defines expected information gain as mutual information; section 2.1 describes sequential adaptation.

Sources checked: [primary 1](https://proceedings.mlr.press/v139/foster21a.html); [primary 2](https://proceedings.mlr.press/v139/foster21a/foster21a.pdf).

### fountas2020

**Real work; printed metadata matches.** Manuscript locations: 153.
Official NeurIPS record verifies title/year and four authors. Full abstract describes deep active inference using neural networks and Monte Carlo tree search, supporting its place in the collective scaling-work citation.

Sources checked: [primary 1](https://proceedings.neurips.cc/paper/2020/hash/865dfbde8a344b44095495f3591f7407-Abstract.html).

Access/scope: This collective citation is not read as claiming every referenced paper implements every listed scaling method.

### friston2010

**Real work; printed metadata matches.** Manuscript locations: 149.
Publisher-deposited metadata and the full PubMed record verify single author, title, 2010, 11(2), 127–138. Abstract describes the free-energy account linking action and perception.

Sources checked: [primary 1](https://api.crossref.org/works/10.1038/nrn2787); [primary 2](https://pubmed.ncbi.nlm.nih.gov/20068583/).

Access/scope: Nature full text was inaccessible; publisher metadata plus complete indexed primary abstract support the broad background claim.

### friston2015

**Real work; printed metadata matches.** Manuscript locations: 122, 149.
Publisher metadata and freshly retrieved Europe PMC full abstract verify all six authors and 2015, 6(4), 187–214. Abstract explicitly decomposes negative EFE into extrinsic expected utility and epistemic information gain.

Sources checked: [primary 1](https://api.crossref.org/works/10.1080/17588928.2015.1020053); [primary 2](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A25689102&format=json&resultType=core).

Access/scope: Publisher full text was inaccessible; retrieved deposited abstract is directly sufficient for these general claims.

### friston2021

**Real work; printed metadata matches.** Manuscript locations: 149, 183.
Publisher metadata verifies all five authors and 33(3), 713–763, 2021. Institutional complete abstract describes recursive inference about future beliefs. Da Costa full text additionally spells out the cited sophisticated recursive scheme.

Sources checked: [primary 1](https://api.crossref.org/works/10.1162/neco_a_01351); [primary 2](https://discovery.ucl.ac.uk/id/eprint/10124606/).

### ghavamzadeh2015

**Real work; printed metadata matches.** Manuscript locations: 156.
Publisher metadata verifies four authors, journal 8(5–6), 359–483, 2015. Abstract surveys Bayesian treatment of uncertainty, including model-based and model-free methods. Manuscript primarily is a broad characterization, not a claim that all Bayesian RL is model-based.

ArXiv journal-reference text gives final page 492, but publisher-deposited final pagination is 483. Bibliography follows publisher and should stay unchanged.

Sources checked: [primary 1](https://api.crossref.org/works/10.1561/2200000049); [primary 2](https://arxiv.org/abs/1609.04436).

### guez2013

**Real work; printed metadata matches.** Manuscript locations: 156.
Publisher record and complete abstract verify all three authors, title, JAIR 48, 841–883, 2013. Abstract explicitly describes planning with model uncertainty via Bayes-adaptive Monte Carlo search.

Sources checked: [primary 1](https://api.crossref.org/works/10.1613/jair.4117); [primary 2](https://www.jair.org/index.php/jair/article/view/10853).

### gundersen2024jair

**Real work; printed metadata matches.** Manuscript locations: 1244.
JAIR metadata and author-hosted published PDF verify all three authors, title, volume 81, 1019–1041, 2024. Abstract and section 3 state that submitting authors complete a reproducibility checklist.

Sources checked: [primary 1](https://api.crossref.org/works/10.1613/jair.1.16905); [primary 2](https://www.jair.org/index.php/jair/article/view/16905); [primary 3](https://ai.dmi.unibas.ch/papers/gundersen-et-al-jair2024.pdf).

Access/scope: The checklist requirement is directly verified. The adjacent statement about removal from an accepted version was not independently located in the retrieved portions of this article; confirm against current JAIR author instructions rather than attributing that detail to the abstract.

Detailed field-by-field comparisons and each manuscript-use verdict appear in `a.json`. Full third-party article downloads were moved to temporary storage; `sources_a/provenance.json` records their original URLs, sizes and SHA-256 digests.
