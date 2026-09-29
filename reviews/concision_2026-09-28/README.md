# Main-text concision and notation audit, 2026-09-28

The JAIR manuscript now reaches its references on page 38 rather than page 82.
Its full PDF has 117 pages because supporting proofs and studies remain in
bound appendices. The LNCS companion has 155 pages. Main figures decrease from
16 to 12, and the complete paper retains all 25. Fonts and margins are unchanged.

The untouched alternative is `paper/legacy/2026-09-28_pre_concision/`, captured
from commit `2d3bac4` before editing. Its six artifact hashes have been verified.

## Review records

- `final_critic_review.md`, `final_theory_review.md`, and
  `evidence_final_review.md` accept the scientific content of the structural
  revision. They document evidence retention and the corrections found during it.
- `notation_theory_review.md`, `appendix_math_review.md`, and
  `empirical_math_layout_review.md` accept the delivered sources after the
  user's additional mathematics request. They record exact source/PDF hashes,
  notation corrections, implementation checks, and focused rendered-page review.
- `final_hashes.json` identifies the delivered masters, PDFs, and source ZIP.
  `build_counts.json`, `preservation_audit.json`, and `package_build.json` record
  mechanical checks. Reviewer acceptance is internal, not a journal decision.

All 117 final JAIR pages were inspected as rendered contact sheets. Reviewers
also inspected mathematical pages at readable resolution in both formats.
The final-pass build logs have no overfull boxes, unresolved references, missing
characters, or oversized floats. The fresh extracted Overleaf package builds
successfully and produces exactly the same extracted PDF text as the canonical
JAIR build. It contains 39 files, including 25 figures and 9 table inputs.
The complete suite passes with 486 tests and 20 existing deprecation warnings.
The claim checker has no hard failures and 160 heuristic advisories. Its output
is not a substitute for the reviewers' source and CSV checks.

## Reconstruction

`assemble.py` reconstructs this dated pass from the frozen legacy sources and
the reviewed fragments. The active theory fragments end in `_restored.tex`.
It applies the guarded `appendix_notation_fixes.py` and
`theory_notation_fixes.py` transformations, then discretionary layout breaks.
The other fragment files retain the review history, not alternative live masters.

Do not rerun this historical assembler after later manuscript edits unless
those edits have been incorporated into its inputs. The normal publication
sources remain `paper/full_paper_jair.tex` and `paper/full_paper.tex`.

`verify_preservation.py` compares the live sources with the frozen masters and
their archived table inputs. It checks labels, citations, references, and table
data, allowing the explicitly reviewed taxonomy-header correction. The
`audit_theory_chunks.py --restored` check applies to the pre-notation fragments,
whose formal statements match the baseline apart from proof-location pointers.
The later depth and tie-breaking amendments are reviewed in the mathematics
addenda rather than represented as byte-identical to the baseline.

No experiment or empirical CSV changed in this pass. The only experiment-script
edit is the scoring-table caption, mirrored in the generated table.
