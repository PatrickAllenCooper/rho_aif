# Independent evidence review — monochrome grid spotlight, 2026-10-09

## Verdict

**ACCEPT, with no required scientific revisions remaining.**

I reviewed all four v5 slide renders, actual PPTX slide text and speaker notes, native chart values, dot geometry in the PPTX, the builder, and all 331 words of the current script. Sources are the accepted IWAI paper, the current corrected JAIR manuscript, Tileworld environment and scaling producer, the scaling CSV, and the existing budget-frontier and recorded-sensor archives. No empirical episodes were rerun. The earlier Bandit-deck review is preserved as a private draft at `presentations/iwai2026_spotlight/.build/review_alternatives/final_evidence_v4.md` and is not the review of the current design.

The final v6 artifact visibly adds “specified reward-based recursion,” names the three budget-study tasks, and describes the initial grid as “All cells equally likely.” I verified these three changes directly in its PPTX text. All other slide text, notes and native chart data match the approved v5 contents.

## Evidence and scope

1. **Accepted identity and core claim.** The title, Greek rho, two author names and affiliation match the accepted paper. The reward-based EFE formulation is visibly an augmented per-step utility inside recursive planning. The script and notes retain exact Bayesian updates, horizon and unit matching, state-preserving sensing, terminal/tie-rule consistency, the reward convention and the normalizer qualification. The talk does not claim a universal weight or reward-optimality theorem. Slide 3 states the empirical bit-unit convention.

2. **Grid illustration.** Tileworld has one fixed hidden target, noisy scans and terminal collection at a chosen cell. The illustration invents no navigation position, path or obstacles. At 4×4 with a uniform prior, the available high-row-bit scan is 80% accurate. Its “top half” response gives probability 0.1 to each top cell and 0.025 to each bottom cell. I verified this directly using the environment's observation matrices. The grids are labelled illustrative. Builder diameter is proportional to the square root of probability, and actual PPTX ellipse dimensions confirm a top-to-bottom posterior area ratio of approximately 4:1, subject only to integer drawing-unit rounding. Every cell retains nonzero probability. Thus the dots accurately show belief, not sixteen targets or a revealed target.

3. **Measured grid result.** The native chart stores exactly 0.014, 0.694 and 0.978 from the 8×8 Planning/EFE/Planning+IG rows of `results_tileworld_scaling.csv`. Visible success percentages, scan means (0,17.5,39.5), and rewards (−49.16,−25.86,−30.84) round correctly. Every source record is copied exactly into `content.json`. The identities `reward = 60 × success − 50 − scans` independently reproduce all three rewards. Information bonus is not included in the reported task reward.

4. **Fair comparison.** All three policies use H=2, with five seeds ×200 episodes, not the previous Bandit deck's 5,000 episodes. The high comparator is fixed w=100 and is not called tuned. The slide visibly says the reward-only policy takes no scans at this horizon. The script expressly limits the result to shallow planning and mentions similar smaller-grid performance. Notes retain seed-level uncertainty and the absence of a formal scaling comparison test. The chart presents descriptive means, not a statistical superiority test, general scaling law or matched-compute comparison. All net rewards are negative and are drawn/labeled accordingly.

5. **Subsequent work.** Slide 4 separates later research from the accepted contribution. Its two-policy interpolation is explicitly schematic and represents a randomized mixture with expected usage between its endpoints. It does not label the horizontal direction as an information weight or assert monotonicity of U(w). The empirical summary is independently supported by 12 attainable mixture rows with maximum absolute held-out mean usage error 0.123. These are 11 distinct environment-budget pairs because a Tiger target duplicates. The three tasks are Tiger, Diagnosis and Bandit, not Tileworld. Notes disclose the duplicate, excluded below-range failures and calibration-derived target rule. Visible caveats and script distinguish expected usage from a hard cap and a reward optimum.

6. **Transfer caveat and presentation format.** The spoken recorded-sensor later-batch overspend statement agrees with the current data and is appropriately limited to recorded-data replay. The script has 54+94+92+91=331 spoken words. Timing marks are a rehearsal target, not an observed speaking-time claim. The PPTX contains native geometric shapes, editable text and a native chart, with no media entries or generated imagery. All four reviewed renders are legible and free of misleading empirical annotations.

## Artifact reviewed

v5 PPTX SHA-256: `be87505217b7fcd56d17d6b42982a62e812b0f0994703c25ca21120e51c88624`.

PDF conversion/portability and final delivery checks are performed separately by the presentation owner. This verdict concerns factual accuracy, diagram mathematics, presentation of numerical evidence and the spoken script.

## Final v6 artifact closure

**ACCEPT, with no required scientific revisions remaining.** Verified the actual v6 PPTX and all four rendered PDF pages. The three wording clarifications are accurate, notes and chart data are unchanged, and the PDF preserves the intended mathematical and empirical content without clipping. No media entries were introduced.

- PPTX SHA-256: `7bf8a599c5990db8e38e67f078cd06e6b4c89942d8bd74dd32e36988e1938553`
- PDF SHA-256: `7ee9b984440a24c640b7c37a4d77f48281bc11fb6aeb0f8ac15b18144131bf6d`

These hashes identify `iwai2026_spotlight_2026-10-09_v6.pptx` and its PDF. A canonical delivery copy with identical bytes carries the same evidence verdict.

## Canonical v7 delivery closure

**ACCEPT, with no required scientific revisions remaining.** Compared the final v7 package against v6. The chart XML has exactly one substantive change: vertical-axis maximum 1.0 becomes 1.2 to give the 97.8% label headroom. All chart data and text are unchanged. All four slide XML files have identical content and geometry after removing regenerated creation/relationship IDs, and all four note XML files are byte-identical. Rebuilding also regenerates package metadata/IDs. Thus this is a chart-layout change, not a scientific revision. The owner separately verified the result in native PowerPoint.

The canonical files are byte-identical to v7:

- `presentations/iwai2026_spotlight/output/iwai2026_spotlight_2026-10-09.pptx` — SHA-256 `54e5cd8b03fb16254fdef8d98ec84abe65bf2ca383328100c96aa348b0071992`.
- `presentations/iwai2026_spotlight/output/iwai2026_spotlight_2026-10-09.pdf` — SHA-256 `60803e9731dfe44a76038d06fa3fd051710b0a22c31635f00123d221bc68e5ae`.
