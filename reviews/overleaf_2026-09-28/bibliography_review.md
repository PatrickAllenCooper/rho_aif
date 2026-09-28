# Independent bibliography audit, 2026-09-28

Reviewer: final theory panel agent. Verdict: **UNQUALIFIED ACCEPT** for the bounded bibliography correction and its rendered propagation. No remaining correction is required within this review's scope. This supplements the scientific and visual acceptance already recorded in `reviews/final_two_agent_2026-09-28/reviewer_style_round4.md`.

## Scope and independence

I independently checked the primary metadata for the named de Vries, Champion, Walraven, and Sweeney references, then inspected the actual working-tree diff, regenerated Biber output, and affected bibliography pages. I treated the own-author IWAI acceptance/to-appear information as author-supplied. I mechanically checked citation-key closure across all 69 JAIR entries, but did not reverify all 69 references against primary records in this bounded pass. I did not edit manuscript sources or bibliography data. The ZIP's dependency closure and clean-room build are a separate packaging review.

## Primary-source findings

1. **de Vries, arXiv:2504.14898.** The [arXiv abstract record](https://arxiv.org/abs/2504.14898), [official BibTeX export](https://arxiv.org/bibtex/2504.14898), and [version 4 paper](https://arxiv.org/html/2504.14898v4) agree on the ordered list of 16 named authors. The abstract's generic sentence about the number of other authors is inconsistent with its actual named links, so I used the named list and paper author line. The full paper preserves the accents in Raphaël Trésor, which the abstract/export flatten. The [TU/e institutional record for this exact paper](https://research.tue.nl/en/publications/expected-free-energy-based-planning-as-variational-inference/) corroborates the accents and the compound family name Hidalgo Araya. Its structured record places Subramanian in the family-name position, although it shortens this author's given name to Raaja. The applied source retains the complete arXiv name Raaja Ganapathy Subramanian. The year 2025 is correct.

2. **Champion, internal key `champion2024`.** The [publisher DOI record](https://doi.org/10.1162/NECO.a.1491) gives *Neural Computation* 38(3), 439–469, 2026. The [Kent accepted manuscript record](https://kar.kent.ac.uk/113953/1/theophile26reframing.pdf) corroborates this citation. The publisher's online date is February 27, 2026, for the March 2026 issue. The live bibliography already uses 2026. An internal citation key containing 2024 is not a publication-year error and need not be renamed.

3. **Walraven, internal key `walraven2024`.** The [Springer record](https://link.springer.com/article/10.1007/s10458-024-09683-4) identifies volume 39, article 3, 2025, with a November 7, 2024 online publication date. The existing year 2025 is correct for the issue citation. I found one genuine metadata omission: the publisher gives Gertjan J. Burghouts, while the former source had only G. Burghouts. The applied correction to G. J. Burghouts is justified.

4. **Sweeney, `sweeney2026equivalences`.** The [MDPI record](https://www.mdpi.com/1099-4300/28/1/1) identifies *Entropy* 2026, 28(1), article 1, DOI 10.3390/e28010001. Its online publication date is December 19, 2025. The existing year 2026 is correct for the issue citation.

5. **Own IWAI paper, `cooper2026iwai`.** The current 2026 entry explicitly says “To appear.” Retaining the author-supplied conference acceptance and publication-year information is appropriate. This review does not claim independent verification of a completed proceedings publication, and no volume or page numbers were invented.

## Applied correction and name parsing

The complete author field at `paper/full_paper_jair.bib:113` is correct, in this order:

```bibtex
author = {de~Vries, Bert and Nuijten, Wouter and van~de~Laar, Thijs
          and Kouw, Wouter and Adamiat, Sepideh and Nisslbeck, Tim
          and Lukashchuk, Mykola and Nguyen, Hoang Minh Huu
          and Hidalgo~Araya, Marco and Tr{\'e}sor, Rapha{\"e}l
          and Jenneskens, Thijs and Nikoloska, Ivana
          and Subramanian, Raaja Ganapathy and van~Erp, Bart
          and Bagaev, Dmitry and Podusenko, Albert}
```

The comma-form names and existing nonbreaking-space convention make Biber retain de Vries, van de Laar, and van Erp as complete family strings. They preserve the particles in display and sorting without depending on a separate prefix option. Hidalgo Araya remains one compound family name. The generated Biber data decodes both accents correctly and stores Raaja Ganapathy as the given-name string and Subramanian as the family string. That representation follows the official arXiv natural-name export's normal parse and the exact paper's institutional record. Other institutional records for this author use different name segmentation, so I do not claim this establishes a universal personal naming preference.

The regenerated entry at `paper/full_paper_jair.bbl:539` has `\name{author}{16}` and no manual `moreauthor` flag. Its 16 decoded records are in the primary source's order. The old manual `and others` truncation is gone. The bibliography style may still abbreviate the displayed entry. Preserving that journal-style behavior is correct and does not imply incomplete source metadata.

The LNCS hand bibliography at `paper/full_paper.tex:1106` now gives all 16 authors with consistent initials. The surname particles, compound surname, accents, and ordering agree with the JAIR source. G. J. Burghouts is corrected in both sources. The actual diff contains no changes to years, citation keys, titles, scientific prose, experiments, or numerical results. `paper/full_paper_jair.tex` is unchanged.

## Mechanical and rendered verification

- Recursive JAIR source/input scan found 69 unique cited keys. The `.bib` has 69 unique entries and the regenerated `.bbl` has the same 69 entries. No cited key is missing, no bibliography entry is unused, and no Biber entry differs from the source key set.
- The LNCS hand bibliography has 68 entries. The only JAIR-only key is `gundersen2024jair`, used by the JAIR checklist, as expected.
- The regenerated Biber 2.22 log reports 69 citekeys and successful output, with no warnings or errors.
- I visually inspected the rebuilt JAIR PDF page 78 and LNCS PDF page 104. The revised entries fit their text areas and remain readable. JAIR displays the style-generated abbreviated de Vries entry. LNCS displays all 16 authors, including the accented surname and all initials. Extracted text also confirms G. J. Burghouts on JAIR page 79 and LNCS page 108. The PDF page counts remain 115 and 149, respectively.

Reviewed artifact SHA-256 hashes:

```text
paper/full_paper_jair.bib
3b73ee000f5fbde7b69632d026fb9a9508d69f6c44b723dd2d95988d1e0b1235
paper/full_paper_jair.bbl
0938130979b079e0727335e2f497d1f3e4cb5ad01878a560d8728206764f203e
paper/full_paper.tex
927af3644daef7dd1b5ef7112dedd979aa53f12a7eb423edc2b7fdf3fc471fee
paper/full_paper_jair.tex
bc7a055d5993d8c605fd1fc1d4559fc463968f689f2a8bc016386036f5cd4208
paper/full_paper_jair.pdf
67a8003a1c77c1ee4aac66c747bc7fe3e28369db1b66f64fe4a3ac9be77a6d9f
paper/full_paper.pdf
7dfa0850a4f9cf5d761277f6e80bb2788d99af1a6f9a2d7d34434c2cd5349141
```

Confidence is high for the checked metadata, actual propagation, key closure, and affected-page rendering. This verdict imposes no additional conditions on the bounded correction.
