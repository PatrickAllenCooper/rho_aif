"""Build the delivered Overleaf archive independently and record verification."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
ARCHIVE = ROOT / "paper/rho_aif_jair_overleaf_2026-09-28.zip"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pdf_text(path):
    return subprocess.check_output(["pdftotext", "-layout", str(path), "-"], text=True)


def pdf_pages(path):
    info = subprocess.check_output(["pdfinfo", str(path)], text=True)
    return int(re.search(r"^Pages:\s+(\d+)", info, re.M).group(1))


def log_check(path):
    log = path.read_text(errors="replace")
    failures = [
        line for line in log.splitlines()
        if any(pattern in line for pattern in (
            "Overfull", "Missing character", "undefined references",
            "undefined citations", "LaTeX Error", "Class acmart Error",
            "Fatal error",
        )) or ("Warning:" in line and "undefined" in line)
    ]
    if failures:
        raise RuntimeError("\n".join(failures))
    return {"overfull": 0, "missing_characters": 0, "undefined_references_or_citations": 0}


subprocess.run(
    ["python3", "tools/build_overleaf_package.py", "--output", str(ARCHIVE)],
    cwd=ROOT, check=True,
)
with tempfile.TemporaryDirectory(prefix="rho_aif_overleaf_oct01_") as temp:
    directory = Path(temp)
    with zipfile.ZipFile(ARCHIVE) as archive:
        names = archive.namelist()
        assert len(names) == len(set(names))
        assert all(not Path(n).is_absolute() and ".." not in Path(n).parts for n in names)
        assert archive.testzip() is None
        archive.extractall(directory)
    assert (directory / "full_paper_jair.tex").read_bytes() == (ROOT / "paper/full_paper_jair.tex").read_bytes()
    env = dict(os.environ)
    env["PATH"] = "/Users/pat/Library/TinyTeX/bin/universal-darwin:" + env["PATH"]
    build = subprocess.run(
        ["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", "full_paper_jair.tex"],
        cwd=directory, env=env, text=True, capture_output=True,
    )
    if build.returncode:
        (HERE / "package_build_failure.log").write_text(build.stdout + build.stderr)
        raise RuntimeError("Fresh archive compilation failed; see package_build_failure.log")
    log_check(directory / "full_paper_jair.log")
    canonical = ROOT / "paper/full_paper_jair.pdf"
    extracted = directory / "full_paper_jair.pdf"
    assert pdf_text(canonical) == pdf_text(extracted), "Extracted PDF text differs from canonical PDF"
    package_pages = pdf_pages(extracted)
    assert package_pages == pdf_pages(canonical)
    rendered_text = pdf_text(canonical)
    reference_pages = [
        i for i, page in enumerate(rendered_text.split("\f"), 1)
        if re.search(r"^\s*(?:\d+\s+)?References\s*$", page, re.M)
    ]
    assert reference_pages == [38], reference_pages
    for stem in ("full_paper_jair", "full_paper"):
        log_check(ROOT / "paper" / f"{stem}.log")
    report = {
        "date": "2026-10-01",
        "archive": str(ARCHIVE.relative_to(ROOT)),
        "archive_sha256": sha(ARCHIVE),
        "archive_members": len(names),
        "figures": sum(n.startswith("figures/") for n in names),
        "tables": sum(n.startswith("tables/") for n in names),
        "fresh_extracted_compile_exit": build.returncode,
        "fresh_extracted_pdf_text_matches_canonical": True,
        "jair_pages": package_pages,
        "jair_references_start_page": reference_pages[0],
        "lncs_pages": pdf_pages(ROOT / "paper/full_paper.pdf"),
        "log_checks_each_master_and_package": log_check(directory / "full_paper_jair.log"),
        "artifacts": {
            str(p.relative_to(ROOT)): sha(p) for p in [
                ROOT / "paper/full_paper_jair.tex", ROOT / "paper/full_paper.tex",
                ROOT / "paper/full_paper_jair.pdf", ROOT / "paper/full_paper.pdf",
                ROOT / "paper/tables/horizon_map.tex", ROOT / "paper/tables/w_atlas.tex",
            ]
        },
        "validation_scope": "Local fresh extracted build, not a hosted Overleaf compilation or journal submission.",
    }
    (HERE / "delivery_validation.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
