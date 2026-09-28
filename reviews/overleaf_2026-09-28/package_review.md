# Independent Overleaf package review

Reviewer: final evidence panel reviewer 2. Date: 2026-09-28.

**Decision: UNQUALIFIED ACCEPT.** No required changes remain for the bibliography correction and the self-contained JAIR source ZIP. This is a bounded packaging and bibliography review, supplementing the prior independent scientific and figure acceptance.

## Exact artifact reviewed

- Archive: `paper/rho_aif_jair_overleaf_2026-09-28.zip`
- SHA-256: `83c779e2fd63da62bea6f7efb1d7a4c6c4c7a7ad11f0b579e508a80d34c01c20`
- Size: 495,994 bytes; 34 files.
- Independently extracted to `/Users/pat/Documents/Codex/2026-09-17/plea/work/overleaf-review-2026-09-28/project/`.
- Independent compiled PDF: 115 pages; SHA-256 `675041231d054c048b7bc8cdab066f019bce3513c012f04b1391913954a61863`.

All 34 archive entries match the manifest's byte counts and SHA-256 hashes. All 32 entries copied from the repository match their current canonical files byte for byte. The two additional files are the package instructions and a two-line `latexmkrc`.

## Dependency closure and package contents

I independently parsed the JAIR master and inspected its class and table inputs. The archive contains exactly the required 20 PDF figures, nine table inputs, main `.tex`, bibliography, and `jair.cls`, plus `README_OVERLEAF.md` and `latexmkrc`. No table has another external input. There are no missing graphics, nested TeX dependencies, verbatim source inclusions, external-document references, or attached-PDF dependencies.

All 69 distinct cited keys resolve to the 69 bibliography entries. Biber successfully emitted all 69 entries. The standard `acmart`, ACM BibLaTeX styles/data model, `doclicense`, fonts, and other packages are TeX Live dependencies, correctly disclosed in the README. Partial vendoring of those installed packages is unnecessary.

Archive names are unique and relative, with no traversal components, symlinks, hidden files, or macOS metadata. There are no review records, raw results, experiment code, credentials, personal scratch files, repository metadata, LNCS manuscript, redundant PNG figures, compiled main PDF, or auxiliary build outputs. Author information intentionally present in the manuscript is preserved. The source retains its canonical `graphicspath`; the build audit below demonstrates that the parent-directory fallback was not used to retrieve repository assets.

## Independent extraction and build

From the newly extracted project, I ran:

```sh
env -u TEXINPUTS -u BIBINPUTS -u BSTINPUTS -u TEXMFHOME -u TEXMFCNF \
  PATH=/Users/pat/Library/TinyTeX/bin/universal-darwin:/usr/bin:/bin:/opt/homebrew/bin \
  latexmk -norc -r latexmkrc -pdf -recorder \
  -interaction=nonstopmode -halt-on-error full_paper_jair.tex
```

Exit status was zero. Latexmk invoked Biber and converged on the 115-page PDF with all targets up to date. The final recorder contains 299 unique input paths; every one resolves within the extraction or the installed TinyTeX distribution. None resolves within `/Users/pat/code/rho_aif` or another working directory. Biber's log likewise identifies the extracted bibliography as its data source. This establishes the archive's project-file dependency closure independently of the repository build.

The final log has no undefined references or citations, missing files, or fatal errors. Existing class/header/PDF-string warnings and the previously reviewed 2.94536-point proof box warning remain; this is not a claim of a warning-free build.

I compared extracted text on every page against the newly built canonical JAIR PDF: all 115 pages match. An independent full-document glyph-boundary scan found zero off-page glyphs. I rendered and visually inspected bibliography pages 78 and 79; the corrected entries are legible and have no clipping or layout regression. The rest of the manuscript and all figure/table assets are byte-identical to those covered by the prior full visual/scientific review; a new experiment or full figure redesign audit was unnecessary.

Evidence logs and renders are in the extraction's parent directory: `independent-build.log`, `recorder_audit.json`, `pdf_compare.json`, `independent-pdf.txt`, and `references-078.png` / `references-079.png`.

## Bibliography corrections

I independently checked the complete 16-author sequence in `devries2025` against the current [arXiv v4 PDF, first page](https://arxiv.org/pdf/2504.14898), as well as the [arXiv record](https://arxiv.org/abs/2504.14898). Names, order, and the PDF's accents in Raphaël Trésor are correctly encoded. Biber parses the entry as `\name{author}{16}`. The long master's inline reference mirrors the complete author sequence using initials. The JAIR bibliography style intentionally abbreviates the displayed long author list, while preserving all authors in the source metadata; the README explains this accurately.

The additional `walraven2024` correction from `G.` to `G. J.` Burghouts is supported independently by the [TU Delft primary publication record](https://research.tudelft.nl/en/publications/information-gathering-in-pomdps-using-active-inference/) and its linked publisher PDF. Both masters agree. I reviewed the actual diff: the manuscript edits are confined to these bibliography corrections and the bibliography provenance comment. No scientific claim, number, result file, table, or figure is altered in this packaging task.

## Instructions and limits of verification

`README_OVERLEAF.md` correctly names `full_paper_jair.tex` as the main document, pdfLaTeX as compiler, and BibLaTeX/Biber as the bibliography workflow. It supplies an executable local Latexmk command, explains the required directory layout and installed packages, and accurately says that local validation used TeX Live 2026. `latexmkrc` selects PDF output and the intended default document without custom scripts or external fetches.

The archive has not been uploaded to or compiled on Overleaf's hosted service. This limit is explicitly disclosed rather than presenting a local build as a hosted test. It does not leave a packaging condition: the independent fresh extraction builds successfully using the documented standard toolchain, all manuscript dependencies are present, and the project settings are explicit.

Confidence is high for dependency closure, citation correction, isolation, and local reproducibility. There are no outstanding required or optional corrections from this bounded audit.
