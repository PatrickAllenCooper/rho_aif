# Complete JAIR citation audit — 2026-10-21

**No fabricated references found.** All 69 bibliography entries were authenticated against fresh publisher, proceedings, author/institutional, arXiv or publisher-deposited DOI records. The audit examined every one of the manuscript's 111 individual citation uses, grouped into 84 citation commands. No bibliography entry needed correction. Three attribution sentences were corrected in both live masters, and one unverified policy sentence was removed from the JAIR-only checklist introduction.

This is a fresh audit from commit `68a9c137c4529675b3fe097ccda351e464dc3afc`, not a reuse of earlier citation verdicts. Authenticity, bibliographic accuracy and support for an attributed claim are separate checks. A verified identity is not described as a newly verified full-text theorem when access was unavailable.

## Coverage and independent reviews

- [Reviewer A](a.md): 23 entries and 39 uses; [field-by-field evidence](a.json). Its final [post-edit check](post_edit_a.md) closes the checklist wording flag while retaining the Blum and Altman reading limits.
- [Reviewer B](b.md): 23 entries and 34 uses; [field-by-field evidence and post-edit verdict](b.json). All three proposed attribution refinements were independently rechecked against the edited sources.
- [Reviewer C](c.md): 23 entries and 38 uses; [field-by-field evidence](c.json). Its independent [post-edit check](post_edit_c.md) approves the three mirrored corrections.
- [Root checks](root_source_checks.md) independently confirm the corrected attributions, close Lindley's content-access gap using the primary published translation, and explain the remaining limits and source disagreements.

[The coverage manifest](coverage.json) maps all 69 keys to reviewers and checked primary URLs and records the final artifact hashes. [The verifier](verify_audit.py) checks exact coverage of all 111 key/file/line occurrences, confirms an unchanged bibliography and proves that the live sources differ from the baseline only by the four recorded edit groups. The baseline [inventory](inventory.json) and [cross-master comparison](cross_master.json) are preserved. Every bibliography entry is cited, with no missing key. The LNCS master has the same 68 shared references; only the JAIR checklist citation is additional.

Saved publisher-deposited snapshots retain the bibliographic fields used in verification and the original response fingerprints. Full article text, abstracts and unrelated reference lists are omitted from those repository snapshots. [The retention manifest](source_snapshot_policy.json) distinguishes original-response hashes from the retained metadata-file hashes; reviewer reports preserve claim-support paraphrases and source URLs.

## Corrections applied

1. IDS now minimizes a ratio with **squared expected one-period regret**, identifies information about the optimal action and specifies an action distribution. The previous wording reduced this to an unspecified regret/information ratio.
2. Oudeyer and Kaplan (2007) are described as an **earlier typology** of computational intrinsic motivation. The old wording could imply coverage of the 2016–2019 methods in the preceding sentence.
3. The positioning paragraph refers to **information prices and resource constraints**, avoiding an attribution of online price adaptation to every rational-inattention source in the group.
4. The JAIR checklist no longer states that it is excluded from an accepted version. The accessible cited material verifies its review purpose, but that extra policy statement was not established. All questions and answers remain unchanged.

[The guarded edit script](apply_attribution_edits.py) preserves the exact before/after text. No mathematical result, empirical number, experiment implementation, result archive, figure, table or bibliography record changed.

## Source disagreements and bounded verification

The audit does not claim that all web records agree. Schmidhuber's publisher deposit gives pages 222–228 while his author HTML gives 222–227. Ghavamzadeh's publisher deposit gives 359–483 while the arXiv journal reference gives 359–492. The bibliography retains the publisher ranges. VIME's proceedings landing page duplicates an author; the actual proceedings PDF confirms the existing six-author entry. None is an invented work.

The easily confused publication years were checked as issue or conference years, including Champion, Sweeney, Walraven, Satsangi, Shani, Spaan, Todorov and Burda. Citation-key years do not dictate the printed year. The full de Vries author list is present. Cooper and Velasquez's arXiv record and official IWAI material corroborate acceptance; no published Springer volume/pages were established, so the existing forthcoming status is retained.

Three citation uses have a bounded remaining primary-text limitation: Blum at two locations, where the original text was inaccessible, and the Altman finite-state-duality caution, for which the complete book hypotheses were not freshly reread. Their identities and bibliographic fields are verified. The manuscript supplies its own controller proof and expressly avoids treating finite-state duality as certification of the continuous-belief reference. No unsupported technical conclusion was discovered, but a fresh theorem-by-theorem reading of those sources is not claimed.

Howard's original journal scan was read on a third-party host and authenticated separately through publisher metadata. Lindley's relevant material was read by the root in its primary Russian translation; the English original remained blocked. These provenance limits are recorded rather than hidden. Access problems with the live JAIR instructions also mean this is not a fresh certification of all current submission policies.

## Delivery validation

JAIR remains 51 pages and LNCS 66. Both builds have zero LaTeX errors, unresolved references/citations, overfull boxes or missing characters. Changed pages were visually inspected. [Build checks](build_checks.json) and [claim-checker output](verify_claims.txt) pass.

The refreshed `paper/rho_aif_jair_overleaf_2026-10-21.zip` contains 16 files, ten figures and one table input. [Fresh-extraction validation](delivery_validation.json) confirms that it compiles independently and matches the canonical JAIR PDF text. The final PDF and ZIP hashes are recorded there and in the coverage manifest. The prior same-day version remains recoverable at baseline commit `68a9c13`; historical frozen alternatives were not edited.

No experimental episodes, GPU jobs or test-suite reruns were needed for this citation-only pass. The 541-test result belongs to the immediately preceding final-panel pass, not to a new run here. No submission or external message was sent.

**Verdict: PASS for citation authenticity, complete inventory coverage and the verified corrections, with the stated reading/provenance limits.** This citation audit is not a new prediction of JAIR's eventual decision. The preceding full-panel recommendations and their scope remain in `reviews/final_jair_2026-10-21/`.
