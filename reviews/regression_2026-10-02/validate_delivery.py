"""Verify the current source ZIP compiles without repository inputs."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import zipfile


ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / "paper/rho_aif_jair_overleaf_2026-10-02.zip"
CANONICAL = ROOT / "paper/full_paper_jair.pdf"
REPORT = Path(__file__).with_name("delivery_validation.json")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


with zipfile.ZipFile(ARCHIVE) as archive:
    assert archive.testzip() is None
    names = archive.namelist()
    assert len(names) == 16
    assert sum(name.startswith("figures/") for name in names) == 10
    assert "figures/fig_engineering_workflow.pdf" not in names
    with tempfile.TemporaryDirectory(prefix="rho_overleaf_check_") as temporary:
        archive.extractall(temporary)
        env = os.environ.copy()
        env["PATH"] = "/Users/pat/Library/TinyTeX/bin/universal-darwin:" + env["PATH"]
        build = subprocess.run(
            ["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error",
             "-quiet", "full_paper_jair.tex"],
            cwd=temporary, env=env, capture_output=True, text=True,
        )
        if build.returncode:
            raise RuntimeError(build.stdout[-1500:] + build.stderr[-1500:])
        extracted = Path(temporary) / "full_paper_jair.pdf"
        extracted_text = subprocess.check_output(["pdftotext", "-layout", str(extracted), "-"])
        canonical_text = subprocess.check_output(["pdftotext", "-layout", str(CANONICAL), "-"])
        assert extracted_text == canonical_text

report = {
    "archive": str(ARCHIVE),
    "archive_sha256": sha(ARCHIVE),
    "members": len(names),
    "figures": 10,
    "tables": 1,
    "extract_compile": "passed",
    "pdf_text_match": True,
    "jair_source_sha256": sha(ROOT / "paper/full_paper_jair.tex"),
    "jair_pdf_sha256": sha(CANONICAL),
    "lncs_source_sha256": sha(ROOT / "paper/full_paper.tex"),
    "lncs_pdf_sha256": sha(ROOT / "paper/full_paper.pdf"),
}
REPORT.write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
