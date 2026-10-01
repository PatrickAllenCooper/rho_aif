"""Hostile-AE R1: episode-matched SARSOP equivalence (results_tost_sarsop_episode_paired.csv)."""
from pathlib import Path

EDITS = [
    ("The nominal seed lists are shared, but differing policies consume random draws differently. A paired five-seed sensitivity analysis confirms that covariance is positive here and the unpaired analysis is conservative. Tiger's paired differences are identically zero. Diagnosis and Bandit give paired $p_{\\mathrm{TOST}}$ of $0.016$ and $3.6{\\times}10^{-5}$.",
     "The nominal seed lists are shared, but differing policies consume random draws differently, so seed-paired differences are not episode-matched. A predeclared twenty-seed check reseeds every episode so both policies face the same episodes. It retains equivalence, with paired differences of $+0.11\\pm0.09$ on Diagnosis and $+0.04\\pm0.03$ on Bandit and paired $p_{\\mathrm{TOST}}$ of $3.2{\\times}10^{-9}$ and $4.6{\\times}10^{-12}$, while Tiger's two policies act identically."),
    ("Its estimated gap from EFE is zero on Tiger,",
     "Its estimated gap from EFE on the canonical stream is zero on Tiger,"),
    ("The shared-seed covariance is therefore positive on both environments, so the unpaired analysis reported above (\\texttt{results\\_\\allowbreak tost\\_\\allowbreak sarsop.csv}) is the conservative one and the equivalence conclusion does not depend on the choice.\\par}",
     "The shared-seed covariance is therefore positive on both environments, so the unpaired analysis reported above (\\texttt{results\\_\\allowbreak tost\\_\\allowbreak sarsop.csv}) is the conservative one and the equivalence conclusion does not depend on the choice.\\par}\n\nSeed-paired differences are still not episode-matched, because the two policies consume each seed's random stream differently. A predeclared episode-matched check removes that limitation (\\texttt{run\\_\\allowbreak tost\\_\\allowbreak sarsop.py --episode-seeding}, \\texttt{results\\_\\allowbreak tost\\_\\allowbreak sarsop\\_\\allowbreak episode\\_\\allowbreak paired.csv} and its per-seed file). It resets episode $e$ of seed $s$ at $10^4 s + e$, the budget-frontier convention, so both policies face the same hidden states and the same observation draws for as long as their actions agree, and it uses the same twenty seeds, $500$ episodes per seed, and margins as the $n{=}20$ study. Equivalence holds on all three environments. Tiger's policies act identically. Diagnosis gives a paired difference of $+0.11$ with SE $0.09$ and paired $p_{\\mathrm{TOST}}=3.2{\\times}10^{-9}$, and Bandit gives $+0.04$ with SE $0.03$ and $p_{\\mathrm{TOST}}=4.6{\\times}10^{-12}$. The unpaired versions on the same runs give $3.8{\\times}10^{-5}$ and $1.8{\\times}10^{-8}$."),
    ("Its held-out shortfall therefore sat uneasily with the $n{=}20$ equivalence of $w{=}1$ and that policy in Section~\\ref{sec:sarsop}.",
     "Its held-out shortfall therefore sat uneasily with the $n{=}20$ equivalence of $w{=}1$ and that policy in Section~\\ref{sec:sarsop}. On those five held-out seeds the plateau policy trails the unpenalized policy by $1.01\\pm0.18$ on matched episodes, whereas the twenty-seed episode-matched check of Appendix~\\ref{app:sarsop_details} gives $+0.11\\pm0.09$."),
]
for name in ("full_paper_jair.tex", "full_paper.tex"):
    p = Path("paper") / name
    t = p.read_text()
    for old, new in EDITS:
        n = t.count(old)
        assert n == 1, (name, old[:70], n)
        t = t.replace(old, new)
    p.write_text(t)
    print(name, "ok")
