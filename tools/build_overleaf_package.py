#!/usr/bin/env python3
"""Package the current JAIR source and its referenced assets for Overleaf.

Run from any directory. No experiments or LaTeX compilation are performed.
The archive contains sources only; validate a fresh extracted build before
delivery. Dependency discovery prevents new figures from being omitted.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import zipfile


ROOT = Path(__file__).resolve().parents[1]


def build(output: Path) -> None:
    main = ROOT / "paper/full_paper_jair.tex"
    source = main.read_text()
    members = {
        "full_paper_jair.tex": main,
        "full_paper_jair.bib": ROOT / "paper/full_paper_jair.bib",
        "jair.cls": ROOT / "paper/jair.cls",
    }
    pending = [source]
    while pending:
        text = re.sub(r"(?<!\\)%[^\n]*", "", pending.pop())
        for kind, target in re.findall(
            r"\\(includegraphics|input)(?:\[[^\]]*\])?\{([^}]+)\}", text
        ):
            asset = Path(target)
            if not asset.suffix:
                asset = asset.with_suffix(".pdf" if kind == "includegraphics" else ".tex")
            if asset.is_absolute() or ".." in asset.parts:
                raise ValueError(f"Unexpected archive dependency: {target}")
            key = asset.as_posix()
            if key in members:
                continue
            candidates = [ROOT / "paper" / asset, ROOT / asset]
            path = next((p for p in candidates if p.is_file()), None)
            if path is None:
                raise FileNotFoundError(f"Missing manuscript dependency: {target}")
            members[key] = path
            if kind == "input":
                pending.append(path.read_text())
    figures = sum(k.startswith("figures/") for k in members)
    tables = sum(k.startswith("tables/") for k in members)
    readme = f"""# JAIR manuscript for Overleaf

Upload this ZIP using New Project > Upload Project in Overleaf.
Select `full_paper_jair.tex` as the main document and pdfLaTeX as the compiler.
Use a current TeX Live version. BibLaTeX uses Biber, which Overleaf detects.

This source archive contains the JAIR master, bibliography, official jair.cls,
all {figures} referenced PDF figures, and all {tables} table inputs. Keep figures/
and tables/ beside the main file. Standard TeX Live supplies acmart,
acmauthoryear, acmdatamodel, biblatex, doclicense, fonts, and other packages.

Local build:

```sh
latexmk -pdf -interaction=nonstopmode -halt-on-error full_paper_jair.tex
```

Alternatively run pdfLaTeX, Biber, then pdfLaTeX twice. The compiled manuscript
PDF and auxiliary files are intentionally omitted. No hosted Overleaf test
or journal submission is performed by the packaging script.

Regenerate from the repository with `python tools/build_overleaf_package.py`.
Upload documentation:
https://docs.overleaf.com/managing-projects-and-files/uploading-a-project
"""
    contents = {name: path.read_bytes() for name, path in members.items()}
    contents["README_OVERLEAF.md"] = readme.encode()
    contents["latexmkrc"] = b"$pdf_mode = 1;\n@default_files = ('full_paper_jair.tex');\n"
    output.parent.mkdir(parents=True, exist_ok=True)
    # Stable timestamps/order make repeated packages byte-identical.
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(contents.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, data)
    print(f"{output}: {len(contents)} files, {figures} figures, {tables} tables")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path,
        default=ROOT / "paper/rho_aif_jair_overleaf_2026-10-02.zip",
    )
    build(parser.parse_args().output)
