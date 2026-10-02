# Final PDF and source-package check, 2026-10-01

**Result: PASS.** The JAIR manuscript and the LNCS companion compile, and the
refreshed source archive builds independently. Scientific acceptance is recorded
separately by the two independent referees.

## Build correction

The first clean JAIR build with `-halt-on-error` failed at document end because
the inherited appendix wrapper redefined the protected `section` command.
The official JAIR class extends acmart, which rejects that redefinition. Both
masters now put explicit `FloatBarrier` commands before appendix sections,
retaining their placement and the class's command. No class file was patched and
no error was suppressed. Subsequent final builds exit successfully.

JAIR uses TinyTeX pdfLaTeX/Biber through latexmk. The companion uses Tectonic.
The final JAIR PDF is 111 pages, with references beginning on page 38; the LNCS
PDF is 141 pages. The last-pass logs have no overfull boxes, missing characters,
or unresolved references/citations. Existing nonfatal class notices and
underfull-box warnings remain.

## Visual inspection actually performed

The root reviewer inspected all 111 JAIR pages in seven contact sheets for
layout, float placement, large gaps, overlap, and clipping. The final citation
and causal-scope edits changed extracted text only on pages 78, 79, and 103;
those pages were rendered again and inspected individually.

Detailed 115-dpi page renders were opened for pages 1, 10, 13, 14, 28, 29, 58,
73, 74, 78, 79, 81, 83, 103, and 104. These cover the abstract, destructive
sensing equations, crossing definition, scale identities, target-reference
table and discussion, horizon-map criterion, atlas brackets, controller
schematic/proof, citation restriction, and RockSample/Inspection details.
Mathematical symbols, subscripts, superscripts, tables, and captions are legible
and remain within their margins. No overlap, clipped text, or missing glyph was
observed in these renders. Figures and empirical table bodies were unchanged.

The independent appendix reviewer inspected the companion's changed captions
and final changed text at 140 dpi, with the exact pages and PDF hash recorded in
`lncs_visual_check.md`. No layout defect was found.

## Overleaf package

`validate_delivery.py` created and extracted the 39-file archive, verified its
member integrity, and compiled it in a new temporary directory without any
repository inputs. The archive includes the main source, bibliography, official
class, build configuration/instructions, 25 figure PDFs, and nine table inputs.
The extracted main source is byte-identical to the reviewed source. The compiled
PDF's complete `pdftotext -layout` output matches the canonical JAIR PDF exactly,
including page breaks and line numbers. Both contain 111 pages.

Exact source, PDF, and ZIP SHA-256 hashes are in `delivery_validation.json`.
The stable September 28 archive filename now contains the October 1 revision.
No hosted Overleaf compilation or JAIR submission was performed.
