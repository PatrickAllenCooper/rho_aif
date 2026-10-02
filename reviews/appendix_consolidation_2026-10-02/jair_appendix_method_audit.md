# JAIR Volume 84 appendix-length methodology audit

Audited 2026-10-02. No manuscript files changed.

## Scope and denominator

The [official Volume 84 (2025) contents](https://www.jair.org/index.php/jair/issue/view/1173) contains 30 article entries, plus a separate masthead. The 30 PDF census is a defensible estimate for this complete volume. It is not a random journal-wide sample, all of 2025, or the distribution of every accepted submission. Use “published papers in JAIR Volume 84 (2025)” when giving precise scope. Do not present the number as an official JAIR statistic, an acceptance criterion, or a page limit.

Report both mean across all 30 papers (zeros for papers without substantive in-PDF appendices) and mean/median among papers that have such appendices. The latter is the clearer comparison for a manuscript that already has substantial appendices. Compute one total per article, not a mean across individual lettered appendices. Include a median because long appendices can move the mean.

## Measurement

Count the union of physical PDF pages occupied by substantive appendix content. Mixed reference/appendix pages count once; reference-only, checklist-only, cover/contents-only, and receipt-date-only pages are excluded. Inclusive occupied-page spans are not fractional typeset page equivalents. This rounding can overstate actual content, especially for short appendices. The estimate also depends on formatting, type size, and page layout.

Independent visual boundary spotchecks confirmed:

- Listed paper 8, *Thousands of AI Authors on the Future of AI*: substantive appendices occupy pages 21-47 (27 pages). Page 21 is mixed references/Appendix A; page 47 contains Appendix E results; page 48 is only the reproducibility checklist and receipt dates. Including the checklist adds one page.
- Listed paper 16, *On the Equivalence between Logic Programs and Bipolar Argumentation Frameworks*: page 42 contains appendix proof content; page 43 contains only receipt/acceptance dates and must be excluded.
- Listed paper 22, *Mechanisms of Symbol Processing for In-Context Learning in Transformer Networks*: Appendix A starts on mixed reference/appendix page 55. Counting this page is consistent with the occupied-page convention.

The listing order differs from each PDF's printed Article number; identifiers and URLs should be retained to prevent confusion.

## Article-type sensitivity

The official section label “Articles” does not distinguish literature surveys from research articles. Exclude the following four only in a clearly labeled research-paper sensitivity analysis:

- Listed 19: [Trustworthy Transfer Learning: A Survey](https://www.jair.org/index.php/jair/article/view/17602).
- Listed 27: [Combining Constraint Programming and Machine Learning: From Current Progress to Future Opportunities](https://www.jair.org/index.php/jair/article/view/19533). Its abstract explicitly identifies it as a survey.
- Listed 28: [Agentic Large Language Models, a Survey](https://www.jair.org/index.php/jair/article/view/18675).
- Listed 29: [Viewpoint: The Future of Human-Centric Explainable Artificial Intelligence (XAI) is not Post-Hoc Explanations](https://www.jair.org/index.php/jair/article/view/17970).

Retain listed 8: [Thousands of AI Authors on the Future of AI](https://www.jair.org/index.php/jair/article/view/19087) is original empirical survey research, not a literature-survey article.

## Separate supplements and policy

Listed paper 22 has an official [Online Appendices PDF](https://www.jair.org/index.php/jair/article/download/17469/27247/50940). It is 25 physical pages: cover on page 1, contents on page 2, substantive content on pages 3-24 (22 pages), and references only on page 25. Pages 3, 24, and 25 were rendered and visually inspected. These 22 pages are additional to its in-article appendix pages, with no overlapping physical pages. They may be added in a separately labeled sensitivity analysis, not silently folded into the in-PDF estimate. The separate supplement uses a different, larger-type layout, so summing its pages with the main PDF is only a rough physical-page comparison.

Other articles link external code, data, or study material. A zero in-PDF appendix count does not establish an absence of supplementary material. Official Code galleys and external repositories have no consistent page measure and remain excluded. Do not describe the result as a census of total supplementary material.

The current [JAIR submissions guidelines](https://www.jair.org/index.php/jair/about/submissions) distinguish online appendices from the reviewed article and say online appendices are not part of peer review. They also require the reproducibility checklist as a submission appendix but allow its omission from the accepted final version. Published appendix lengths therefore do not measure all pages reviewed during submission. The guidelines encourage concise articles, but the observed mean is not a prescribed target.

## Recommended wording

“I measured the published PDFs for all 30 articles in JAIR Volume 84 (2025). Substantive appendices occupied an average of 6.4 pages across all articles, or 11.3 pages among the 17 articles with appendices (median 13). These are pages containing appendix material, excluding references and reproducibility checklists. This is a recent-volume benchmark, not an official journal-wide average or an acceptance limit. One paper also has a separate 22-page substantive online appendix.”

For a manuscript comparison, state the observed difference without implying that appendix length alone predicts rejection. Compare against the conditional mean, median, observed range, and similar research papers; clearly state whether the manuscript’s own count uses the same exclusion rules and format.

## Independent arithmetic verification

Independently combined both measurement JSON files and verified 30 unique listed positions/URLs, every union of physical-page intervals, every per-appendix union, every page bound, and all 30 saved PDF SHA-256 hashes. No discrepancies found.

- Primary in-PDF measure: 192 substantive occupied appendix pages in 30 papers; 17 papers have appendices. Across all 30, mean 6.4 and median 2.5 pages. Conditional on having appendices, mean 11.2941, median 13, range 2-27 pages.
- Excluding three literature surveys and one viewpoint: all four have zero in-PDF appendix pages. Across the remaining 26 papers, mean 7.3846 and median 4.5. Conditional mean/median/range are unchanged.
- Adding the separately hosted 22 substantive appendix pages to listed paper 22 changes that paper from 15 to 37 pages and the volume total from 192 to 214. Across 30, mean 7.1333; among 17 with appendices, mean 12.5882, median 13, range 2-37. This is a sensitivity, not a total-supplement census.
- Excluding the four review/viewpoint papers while adding the official online appendix yields 214/26 = 8.2308 across papers; conditional statistics remain as above.
- Counting the one reproducibility checklist page instead would produce 193/30 = 6.4333 overall and 193/17 = 11.3529 among papers with appendices. It does not materially change the comparison.
- A 42-page substantive appendix is about 3.7 times the primary conditional mean and 3.2 times the conditional median. It exceeds the largest in-PDF appendix in this volume by 15 pages, or the largest main-plus-official-online appendix total by 5 pages. This is an observed comparison only, subject to formatting and content differences.

Full independently computed numeric output: `jair_appendix_method_arithmetic.json`.
