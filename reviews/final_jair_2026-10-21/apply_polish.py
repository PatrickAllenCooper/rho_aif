"""Guarded, one-time application of the final panel's clarity refinements."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
CHANGES = [
    ("qualification pointer", "the qualification following the proof", "the qualification following the proposition"),
    ("positive initial step", r"The schedule in~\eqref{eq:dual_update} satisfies these conditions when $\delta>0$.", r"The schedule in~\eqref{eq:dual_update} satisfies these conditions when $\eta_0>0$ and $\delta>0$."),
    ("named proof sketch", r"\begin{proof}[Proof sketch]", r"\begin{proof}[Proof sketch for Proposition~\ref{prop:factored}]"),
    ("Kronecker argument", r"Since $1/a_t = (1 + \delta t)/\eta_0$ increases to infinity, Kronecker's lemma gives $a_n \sum_{t<n} (B - U_t) \to 0$, and because $n\,a_n \to \eta_0/\delta > 0$ under that schedule, the one property of it the running-average claim uses, this is $\frac{1}{n}\sum_{t<n} (B - U_t) \to 0$ almost surely.", r"Since $1/a_t = (1 + \delta t)/\eta_0$ increases to infinity, Kronecker's lemma gives $a_n \sum_{t<n} (B - U_t) \to 0$ almost surely. Under the harmonic schedule, $n\,a_n \to \eta_0/\delta > 0$. Dividing by $n\,a_n$ therefore gives $\frac{1}{n}\sum_{t<n} (B - U_t) \to 0$ almost surely."),
    ("symmetric upper threshold", r"""The upper (over-observation) threshold is
\begin{equation*}
    w^*_{\mathrm{over}} = \begin{cases}
    (c - \mathrm{VoI}_2(b)) / I(b) & \text{if } \mathrm{VoI}_2(b) < c, \\
    +\infty & \text{otherwise.}
    \end{cases}
\end{equation*}
In this symmetric model $\mathrm{VoI}_2(b)=0$, because a disconfirming second observation returns the posterior to the tie point. Thus the finite branch applies.""", r"""In this symmetric model $\mathrm{VoI}_2(b)=0$, because a disconfirming second observation returns the posterior to the tie point. The upper (over-observation) threshold therefore simplifies to
\begin{equation*}
    w^*_{\mathrm{over}} = \frac{c-\mathrm{VoI}_2(b)}{I(b)} = \frac{c}{I(b)}.
\end{equation*}"""),
]

prepared = []
manifest = []
for name in ["full_paper_jair.tex", "full_paper.tex"]:
    p = ROOT / "paper" / name
    old = p.read_text()
    new = old
    for label, before, after in CHANGES:
        assert new.count(before) == 1, (name, label, new.count(before))
        new = new.replace(before, after)
    if name == "full_paper_jair.tex":
        before = r"""\setcopyright{cc}
\acmDOI{10.1613/jair.1.xxxxx}

\JAIRAE{}
\JAIRTrack{}
\acmVolume{1}
\acmArticle{1}
\acmMonth{8}
\acmYear{2026}"""
        after = r"""\setcopyright{cc}
% Publication metadata will be supplied by JAIR after acceptance.
\acmDOI{}
\settopmatter{printacmref=false}
\JAIRAE{}
\JAIRTrack{}
\acmVolume{}
\acmArticle{}
\acmYear{2026}
\AtBeginDocument{%
  \fancyfoot[RO,LE]{\footnotesize Manuscript prepared for JAIR review.}%
  \fancypagestyle{firstpagestyle}{%
    \fancyhf{}%
    \fancyfoot[RO,LE]{\footnotesize Manuscript prepared for JAIR review.}%
  }%
}"""
        assert new.count(before) == 1
        new = new.replace(before, after)
    prepared.append((p, new))
    manifest.append({"file": str(p.relative_to(ROOT)), "before_sha256": hashlib.sha256(old.encode()).hexdigest(), "after_sha256": hashlib.sha256(new.encode()).hexdigest(), "edits": [c[0] for c in CHANGES] + (["submission metadata"] if "jair" in name else [])})

for p, content in prepared:
    p.write_text(content)
Path(__file__).with_name("application_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(json.dumps(manifest, indent=2))
