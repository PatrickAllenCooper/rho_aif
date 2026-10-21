# Root source checks and access reconciliation

Date: 2026-10-21. These checks supplement, rather than replace, the three independent 23-entry audits.

## Independently confirmed corrections

- **Russo and Van Roy.** The [author arXiv record](https://arxiv.org/abs/1403.5556) explicitly defines information-directed sampling using squared expected single-period regret and information about the optimal action. The corrected sentence also identifies the optimization over an action distribution. The original wording omitted the square and the information target. The official NIPS record was independently checked by reviewers B and C.
- **Oudeyer and Kaplan.** The [publisher full text](https://www.frontiersin.org/journals/neurorobotics/articles/10.3389/neuro.12.006.2007/full) describes a computational typology of intrinsic motivation. Calling it an earlier typology avoids implying that it surveyed the 2016–2019 methods listed immediately before it.
- **Rational inattention.** The [American Economic Association record](https://www.aeaweb.org/articles?id=10.1257/aer.20130047) describes costly information acquisition. The revised positioning sentence refers to information prices and resource constraints, rather than implying that all of the grouped sources provide online price adaptation. The neighboring related-work paragraph already distinguishes the specific precedents.

The three sentence replacements are identical across the two live masters. A later JAIR-only correction removes the unverified checklist-removal statement described below. No citation keys or bibliography entries changed. Reviewers B and C independently approved the three mirrored replacements in the actual edited sources.

## Lindley: primary translation closes the content-access gap

Reviewer B verified the original 1956 metadata but could not retrieve the English text or the translation. The root reviewer successfully read the publisher-hosted Russian translation through the web tool on 2026-10-21:

- [Mathnet record](https://www.mathnet.ru/eng/mat101), hosted by the Steklov Mathematical Institute. It identifies the 1959 Russian translation and explicitly cites the original *Annals of Mathematical Statistics* 27 (1956), 986–1005. The bibliography continues to cite the English original and its year.
- [Full translation](https://www.mathnet.ru/php/getFT.phtml?jrnid=mat&option_lang=eng&paperid=101&what=fullt). Printed page 88 (PDF page 2), Section 2, states the rule of choosing the experiment with the greatest expected increase in information. Printed page 90 (PDF page 4), Definitions 1–2 and equations (6)–(7), define the posterior-minus-prior information difference and its expectation. These passages support the manuscript's limited historical attribution to information-gain experimental design.

The successful web extraction contained 18 pages and 672 lines. Direct shell download timed out; the English Project Euclid page was blocked. The root did not obtain or inspect a local English original. This is a direct reading of the primary published translation, not a secondary summary, and is credited to the root rather than to reviewer B. No quotation from the translation is inserted into the manuscript.

## Additional authenticity and metadata checks

- [Cooper and Velasquez, arXiv:2607.16981](https://arxiv.org/abs/2607.16981) is live with the stated title and authors. Its comments report IWAI spotlight acceptance and forthcoming Springer CCIS publication. The record supports the existing forthcoming status; it does not establish a published proceedings volume or page range.
- [Schmidhuber's author page](https://people.idsia.ch/~juergen/curiositysab/curiositysab.html) gives 222–227, while the fresh publisher-deposited record checked by reviewer C gives 222–228. The existing publisher range is retained. This one-page discrepancy is unresolved and is not evidence of an invented work.
- **Ghavamzadeh et al.** Reviewer A found a second pagination disagreement: the [author arXiv record](https://arxiv.org/abs/1609.04436) gives 359–492, while the publisher deposit for [DOI 10.1561/2200000049](https://doi.org/10.1561/2200000049) gives 359–483. The bibliography correctly follows the publisher.
- **Blum (1954).** The root's direct Project Euclid request also encountered a bot/access block. The work's identity, exact title and bibliographic fields are verified through the publisher deposit by reviewer A. Full theorem text is not claimed to have been freshly reread. The current manuscript uses this reference for a generic historical almost-sure-convergence attribution and supplies its own controller proof.
- **Altman (1999).** The author-hosted book record and contents establish its constrained-control, duality and randomization coverage. Reviewer A did not freshly reread every hypothesis in the full book. The manuscript's line 561 is a caution against automatically extending finite-state results to the continuous belief MDP, not a claim that an unchecked book theorem certifies the numerical reference.

## JAIR checklist wording

Reviewer A directly verified that the cited Gundersen editorial requires the checklist for submission. The additional sentence claiming that the checklist is not part of the accepted version was not located in the retrieved article portions. The root's request to the live [JAIR submission instructions](https://www.jair.org/index.php/jair/about/submissions) returned HTTP 503, and attempts to reread the author-hosted PDF timed out. The root removed only that extra sentence; the verified description of the checklist's review purpose and all questions and answers remain unchanged. This removes an unsupported future-policy assertion without making a new policy claim. The LNCS master has no corresponding checklist sentence.

## Build and visual checks

The root inspected the regenerated JAIR pages 4, 5, 14 and 49 and LNCS pages 5, 6 and 18. The new sentences and their citations are readable, with no clipped text or layout regressions. Both builds have no overfull boxes, unresolved references/citations, missing characters or LaTeX errors. The package is validated from a fresh extraction and has matching PDF text. See `build_checks.json` and `delivery_validation.json` for recorded results.
