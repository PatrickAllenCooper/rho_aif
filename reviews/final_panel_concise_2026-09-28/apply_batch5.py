"""Batch 5 of the concise-manuscript panel (ledger 9.17.57).

Fable required change 1: the observe-then-commit POMCP charged +cost per
simulated observation and started every rollout from the root belief. Both
are fixed in rho_aif/agents/pomcp.py (v2.1.0) and every POMCP producer was
rerun. This batch rewrites every POMCP-dependent sentence and the inline
Table tab:pomcp against the new CSVs, adds a dated correction note, and
folds in the two optional attribution fixes of the final citation check.
Main-body edits are net-neutral or near it.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MASTERS = [ROOT / "paper/full_paper_jair.tex", ROOT / "paper/full_paper.tex"]

TT = r"\texttt{tests/\allowbreak test\_\allowbreak pomcp\_\allowbreak "

EDITS = [
    # ---------------- main body ----------------
    ("M1 main body sec 750",
     r"A separate sweep selects constants on tuning seeds under a recorded rule, but the canonical five-seed sweep had already been inspected before that rule was written. The Tiger tuning result is therefore retrospective.",
     r"A separate sweep selects constants on tuning seeds under a recorded rule, written after an earlier sweep had been inspected but before the corrected POMCP runs reported here.", 1),
    ("M2 main body 843",
     r"Tuning POMCP's exploration constant recovers most of the initial Tiger gap. The narrower comparison after selecting both solvers' constants uses disjoint tuning seeds, but its evaluation runs had already been inspected, so the Tiger result is retrospective evidence.",
     r"Tuning POMCP's exploration constant narrows the Tiger gap without closing it. With both solvers' constants selected on disjoint tuning seeds, MCTS-EFE remains significantly ahead on Tiger success and reward.", 1),
    # ---------------- citation-check advisories ----------------
    ("C1 EFE decomposition attribution",
     r"\citep{friston2010,parr2019}",
     r"\citep{friston2015,parr2019}", 1),
    # ---------------- appendix POMCP: fidelity paragraph ----------------
    ("A1 fidelity gaps",
     r"Our implementation adapts the algorithm to the observe-then-commit action structure, and three fidelity gaps against Silver and Veness must be stated before the numbers. Rollouts initialize from the agent's root belief regardless of tree depth, ignoring the observations accumulated along the tree path. The depth-cap leaf returns the best commit reward for the sampled state, a clairvoyant quantity. And rollouts credit the belief-expected commit reward rather than the sampled-state reward. The clairvoyant leaf and the belief-expected commit credit are favorable or neutral to POMCP on these small instances. The root-belief rollout cuts the other way, since it denies observation branches credit for the in-tree observations that produced them, so the net direction of these simplifications is mixed rather than uniformly favorable. None is present in the RockSample POMCP",
     r"Our implementation adapts the algorithm to the observe-then-commit action structure, and two fidelity gaps against Silver and Veness must be stated before the numbers. The depth-cap leaf returns the best commit reward for the sampled state, a clairvoyant quantity. And rollouts credit the belief-expected commit reward rather than the sampled-state reward. Both are favorable or neutral to POMCP on these small instances. Each rollout starts from the belief updated along the simulated action-observation history that reached its leaf. Correction, 2026-09-29: an earlier version of this planner added the observation cost to its simulated return instead of subtracting it, a subsidy of twice the cost per simulated observation, and started every rollout from the root belief, so an observation earned no credit in the rollout after it. Both are fixed (" + TT + r"cost\_\allowbreak sign.py}, " + TT + r"rollout\_\allowbreak belief.py}) and every POMCP result in this article was rerun, with EFE, Planning, and MCTS-EFE reproducing bit-identically. The corrected planner observes less. The earlier Bandit success lead and the earlier failure to distinguish tuned POMCP from MCTS-EFE on Tiger were artifacts of the subsidy and are withdrawn. Neither gap is present in the RockSample POMCP", 1),
    ("A2 where the gap is largest",
     r"On Diagnosis and Tileworld, where the agent must choose among several tests, the gap is largest, and the exploration sweep below shows that neither the exploration constant nor the rollout policy closes it. Bandit, where the agent also chooses among several inspections, shows no success gap, so a choice among tests is not by itself what produces one. EFE chooses",
     r"The gap is smallest on Tiger, which has a single observation action, and larger on Diagnosis, Bandit, and Tileworld, where the agent must choose among several tests, and the exploration sweep below shows that neither the exploration constant nor the rollout policy closes it on the two swept multi-test environments. EFE chooses", 1),
    # ---------------- Table tab:pomcp ----------------
    ("T1 caption",
     r"($73.6\%$ against $71.9\%$, $-21.41$ against $-21.62$), and on Bandit POMCP(1000) leads on success ($87.7\%$ against $86.9\%$), both within seed-level sampling error.}",
     r"($73.6\%$ against $71.9\%$, $-21.41$ against $-21.62$), within seed-level sampling error.}", 1),
    ("T2 Tiger row", r"& POMCP (1000) & $1.80$ & 89.4\% & $-3.48 \pm 0.28$ \\",
     r"& POMCP (1000) & $1.64$ & 89.2\% & $-3.57 \pm 0.18$ \\", 1),
    ("T3 Diagnosis row", r"& POMCP (1000) & $3.96$ & 74.1\% & $-9.49 \pm 0.22$ \\",
     r"& POMCP (1000) & $3.19$ & 70.5\% & $-10.91 \pm 0.63$ \\", 1),
    ("T4 Bandit row", r"& POMCP (1000) & $7.20$ & 87.7\% & $+5.29 \pm 0.04$ \\",
     r"& POMCP (1000) & $1.34$ & 47.2\% & $+4.58 \pm 0.09$ \\", 1),
    ("T5 Tileworld row", r"& POMCP (1000) & $1.35$ & 5.6\% & $-47.99 \pm 0.72$ \\",
     r"& POMCP (1000) & $0.05$ & 2.6\% & $-48.49 \pm 0.28$ \\", 1),
    # ---------------- POMCP comparison paragraph ----------------
    ("P1 comparison",
     r"Table~\ref{tab:pomcp} shows POMCP underperforming both EFE and Planning on reward on every environment, and on success rate everywhere except Bandit. On Tiger, POMCP at this table's untuned exploration constant commits prematurely (1.80 observations vs.\ 4.20 for EFE), yielding 89.4\% success against EFE's 99.4\%",
     r"Table~\ref{tab:pomcp} shows POMCP underperforming both EFE and Planning on reward and success rate on every environment. On Tiger, POMCP at this table's untuned exploration constant commits prematurely (1.64 observations vs.\ 4.20 for EFE), yielding 89.2\% success against EFE's 99.4\%", 1),
    ("P2 comparison Diagnosis",
     r"On Diagnosis, POMCP achieves 74.1\% success ($-9.49$ reward) while EFE reaches 97.2\% ($-1.37$ reward).",
     r"On Diagnosis, POMCP achieves 70.5\% success ($-10.91$ reward) while EFE reaches 97.2\% ($-1.37$ reward).", 1),
    ("P3 comparison Bandit and Tileworld",
     r"On Bandit, POMCP's Monte Carlo exploration achieves a slightly higher success rate than EFE ($87.7 \pm 0.5\%$ vs.\ $86.9 \pm 0.3\%$ seed-level SE, $+0.8$ pp) but with lower reward ($+5.29 \pm 0.04$ vs.\ EFE's $+6.27 \pm 0.04$), buying that success with 7.20 inspections against EFE's 5.11. On success the two are close. EFE is ahead on reward. On Tileworld ($6{\times}6$, $|S|{=}36$), POMCP collapses to 5.6\% success, as the 36 commit actions and 6 scan actions create a branching factor that overwhelms 1{,}000 simulations.",
     r"On Bandit, POMCP inspects $1.34$ times per episode against EFE's $5.11$ and reaches $47.2 \pm 1.0\%$ success against EFE's $86.9 \pm 0.3\%$ (seed-level SE), at $+4.58 \pm 0.09$ reward against $+6.27 \pm 0.04$. On Tileworld ($6{\times}6$, $|S|{=}36$), POMCP collapses to 2.6\% success with almost no scans ($0.05$ per episode), as the 36 commit actions and 6 scan actions create a branching factor that 1{,}000 simulations do not resolve.", 1),
    # ---------------- simulation-budget scaling ----------------
    ("S1 scaling",
     r"On Diagnosis, POMCP(5000) reaches $75.5 \pm 0.6\%$ success (seed-level SE), still far short of EFE's $97.2 \pm 0.3\%$, while taking substantially more wall-clock time per episode (311.9 ms/ep vs.\ EFE's closed-form computation). On Tiger, POMCP(5000) reaches $90.3 \pm 0.3\%$ but at roughly 5$\times$ the compute of the 1{,}000-simulation budget. On Bandit the sweep is not monotone in the middle. POMCP(2000) reaches $90.8 \pm 0.3\%$ success at $+5.90 \pm 0.05$ reward, ahead of POMCP(1000) on both metrics and nominally above Planning's $+5.75$. POMCP(5000) then reaches $97.2 \pm 0.2\%$ success (clearly ahead of EFE), but its reward falls to $+5.18 \pm 0.04$. Its wall-clock cost rises to roughly 0.93 s/episode, a $\sim$6.9$\times$ slowdown versus the 1{,}000-simulation budget. The 2{,}000-to-5{,}000 step is the clearest case in our results of buying success-rate with both compute and return. These results indicate that EFE's advantage is not merely a compute-budget artifact but reflects the benefit of closed-form information gain valuation over Monte Carlo exploration as configured here, with this rollout policy and a single untuned exploration constant, particularly on multi-observation-action environments where the agent must choose which information to gather. A stronger POMCP configuration does narrow the gap, sharply so on Tiger (Table~\ref{tab:pomcp-sweep}), so we do not claim the comparison bounds what a best-practice POMCP can achieve.",
     r"On Diagnosis, POMCP(5000) reaches $71.6 \pm 0.9\%$ success (seed-level SE), still far short of EFE's $97.2 \pm 0.3\%$, while taking more wall-clock time per episode (329.9 ms against EFE's 96.2 ms). On Tiger, POMCP(5000) reaches $89.5 \pm 0.3\%$, no better than at 1{,}000 simulations. On Bandit the sweep is not monotone. POMCP(1000) reaches $47.2 \pm 1.0\%$ success, below POMCP(500)'s $50.9 \pm 1.1\%$ and POMCP(2000)'s $51.6 \pm 1.1\%$, and POMCP(5000) rises to $62.1 \pm 1.2\%$ at $+5.56 \pm 0.10$ reward, still below EFE on both metrics, at roughly 5.8 times the wall-clock cost of the 1{,}000-simulation budget. On Tileworld no budget exceeds $3.8\%$ success. Timings in this appendix, except the compute-matched check below, are wall clock with other batteries running concurrently, so ratios between them are indicative only. As configured here, with this rollout policy and a single untuned exploration constant, the gap is therefore not a simulation-budget artifact. A tuned constant narrows it on Tiger (Table~\ref{tab:pomcp-sweep}), so we do not claim the comparison bounds what a best-practice POMCP can achieve.", 1),
    # ---------------- MCTS-EFE paragraph ----------------
    ("E1 MCTS timings",
     r"MCTS-EFE with 500 simulations achieves 97.7\% success ($23$--$28$ ms per episode across the three horizons tested, \texttt{results\_\allowbreak mcts\_\allowbreak efe.csv}), compared to POMCP's 88.8\% at the same simulation count ($15$--$19$ ms per episode across horizons, simulation-matched, not compute-matched) and exact EFE's 99.9\% at $H{=}6$ ($103$ ms per episode,",
     r"MCTS-EFE with 500 simulations achieves 97.7\% success ($16$--$18$ ms per episode across the three horizons tested, \texttt{results\_\allowbreak mcts\_\allowbreak efe.csv}), compared to POMCP's 88.1\% at the same simulation count ($12$--$14$ ms per episode across horizons, simulation-matched, not compute-matched) and exact EFE's 99.9\% at $H{=}6$ ($79$ ms per episode,", 1),
    ("E2 compute-matched",
     r"gives 24.97s ($97.7\% \pm 0.5$pp success, seed-level SE). Calibrating POMCP's wall-clock cost at 200/500/1{,}000 simulations on the same protocol and machine and solving for the simulation budget matching 24.97s gives 699 simulations, roughly 40\% more than the simulation-matched comparison. POMCP(699) reaches $89.0\% \pm 0.8$pp success ($-3.82 \pm 0.81$ reward, $24.99$s), and a seed-level Welch test against the simulation-matched POMCP(500) ($88.8\% \pm 0.2$pp success, $-4.03 \pm 0.21$ reward, $19.08$s) confirms the two are not significantly different (success $p{=}0.81$, reward $p{=}0.81$). Giving POMCP the same wall-clock budget as MCTS-EFE rather than the same simulation count does not close the gap at this exploration constant, and this is a direct test result rather than a bare assertion. Both POMCP configurations remain significantly behind MCTS-EFE on both metrics (seed-level Welch $p<0.0002$ in every comparison).",
     r"gives 13.87s ($97.7\% \pm 0.5$pp success, seed-level SE), with no other battery running. Calibrating POMCP's wall-clock cost at 200/500/1{,}000 simulations on the same protocol and machine and solving for the simulation budget matching 13.87s gives 661 simulations, roughly 32\% more than the simulation-matched comparison. POMCP(661) reaches $88.0\% \pm 0.6$pp success ($-4.80 \pm 0.69$ reward, $13.88$s), and a seed-level Welch test against the simulation-matched POMCP(500) ($88.1\% \pm 0.2$pp success, $-4.67 \pm 0.19$ reward, $10.42$s) finds no significant difference (success $p{=}0.89$, reward $p{=}0.85$). Giving POMCP the same wall-clock budget as MCTS-EFE rather than the same simulation count does not close the gap at this exploration constant. Both POMCP configurations remain significantly behind MCTS-EFE on both metrics (seed-level Welch $p<0.0001$ in every comparison).", 1),
    # ---------------- exploration sweep paragraph ----------------
    ("X1 finding one",
     r"First, the constant matters a great deal on Tiger. POMCP at $c{=}50$ reaches $96.3\% \pm 0.6$ success at $+3.21 \pm 0.62$ reward, and against MCTS-EFE at its default constant we fail to reject on either metric ($p{=}0.09$ and $p{=}0.54$, a failure to reject rather than a TOST-backed equivalence claim). The $88.8\%$ figure above therefore measures an untuned constant and not the solver.",
     r"First, the constant matters on Tiger, and tuning it does not close the gap. POMCP at $c{=}50$ reaches $93.2\% \pm 0.5$ success at $+0.39 \pm 0.52$ reward, against $87.3$ to $89.0\%$ at constants up to $10$, and it remains behind MCTS-EFE at its default constant on both metrics after Holm correction (seed-level Welch $p{=}0.0002$ and $p{=}0.002$).", 1),
    ("X2 selected Tiger",
     r"MCTS-EFE remains ahead on Tiger success ($98.2\% \pm 0.3$ at $c{=}5$ against POMCP's $96.3\% \pm 0.6$ at $c{=}50$, seed-level Welch $p{=}0.024$, surviving Holm correction within the stated six-test family of success and reward on the three environments) with reward not distinguishable ($p{=}0.16$).",
     r"MCTS-EFE remains ahead on Tiger success ($98.2\% \pm 0.3$ at $c{=}5$ against POMCP's $93.2\% \pm 0.5$ at $c{=}50$, seed-level Welch $p{=}0.0001$) and reward ($+4.33 \pm 0.28$ against $+0.39 \pm 0.52$, $p{=}0.0005$), both surviving Holm correction within the stated six-test family of success and reward on the three environments.", 1),
    ("X3 selections",
     r"and for POMCP $c{=}50$ with uniform rollouts on Tiger, $c{=}5$ with information-gain rollouts on Diagnosis, and $c{=}2$ with uniform rollouts on Tileworld. On Tiger and Diagnosis these are the configurations the evaluation seeds would also have selected, and on Tileworld the evaluation seeds would have selected $c{=}1$ for POMCP. The canonical runs had been inspected before the rule was written, so what the protocol removes is selection on the reported seeds, not our prior sight of them, and the narrow Tiger result counts as retrospective evidence (Section~\ref{sec:discussion}). Tuning the constant narrows the Tiger gap sharply and does not remove it.",
     r"and for POMCP $c{=}50$ with uniform rollouts on Tiger, $c{=}5$ with uniform rollouts on Diagnosis, and $c{=}5$ with information-gain rollouts on Tileworld. On Tiger and Tileworld these are the configurations the evaluation seeds would also have selected, and on Diagnosis the evaluation seeds would have selected $c{=}2$ for POMCP. The rule was written after an earlier, uncorrected sweep had been inspected, but before the corrected runs reported here, which it selected from unchanged. Tuning the constant narrows the Tiger gap and does not remove it.", 1),
    ("X4 finding three",
     r"Its tuning-seed selection, $c{=}5$ with information-gain rollouts on Diagnosis and $c{=}2$ with uniform rollouts on Tileworld-$6{\times}6$, reaches $71.4\% \pm 1.5$ and $19.7\% \pm 1.7$ against MCTS-EFE's $94.7\% \pm 0.4$ at $c{=}5$ and $95.4\% \pm 0.6$ at its default, every comparison significant after Holm correction. The evaluation seeds' own best POMCP configuration on Tileworld, $c{=}1$ at $22.3\% \pm 1.7$, is not the selected one and is reported here only as a descriptive row of the sweep. On Tileworld-$6{\times}6$ success falls as $c$ rises over most of the range, from $22.3\%$ at $c{=}1$ to $2.8\%$ at $c{=}50$, recovering slightly to $3.5\%$ at $c{=}R$. That environment's best therefore sits at the grid's lower edge. A constant below $1$ was not tested, so whether one would do better is not settled here. Information-gain rollouts leave both gaps open, putting Diagnosis at $71.4\%$ against $68.2$ and Tileworld at $19.1\%$ against $11.3$ at $c{=}5$, neither difference surviving Holm correction (seed-level Welch $p{=}0.25$ and $p{=}0.023$).",
     r"Its tuning-seed selection reaches $65.6\% \pm 1.4$ on Diagnosis and $8.2\% \pm 0.6$ on Tileworld-$6{\times}6$ against MCTS-EFE's $94.7\% \pm 0.4$ at $c{=}5$ and $95.4\% \pm 0.6$ at its default, every comparison significant after Holm correction. The evaluation seeds' own best POMCP configuration on Diagnosis, $c{=}2$ at $69.1\% \pm 1.7$, is not the selected one and is reported here only as a descriptive row of the sweep. On Tileworld-$6{\times}6$ POMCP with uniform rollouts barely scans at $c \geq 5$, at most $0.09$ scans per episode, and succeeds on $1.8$ to $3.1\%$ of episodes, while $c{=}1$ reaches $7.1\%$ with about one scan. That environment's best uniform-rollout constant therefore sits at the grid's lower edge, and a constant below $1$ was not tested. Information-gain rollouts leave both gaps open. At $c{=}5$ they put Diagnosis at $66.8\%$ against $65.6$, not a significant difference ($p{=}0.57$), and Tileworld at $8.2\%$ against $2.6$, which survives Holm correction on success ($p{=}0.0002$) but not on reward ($p{=}0.012$).", 1),
    # ---------------- Appendix Y (interpretation) ----------------
    ("Y1 MCTS numbers",
     r"($23$--$28$ ms per episode across the three horizons tested, \texttt{results\_\allowbreak mcts\_\allowbreak efe.csv}), compared to $88.8\% \pm 0.2$pp for POMCP at the same simulation count ($15$--$19$ ms per episode across horizons, seed-level SE, seed-level Welch $p{=}5.2{\times}10^{-6}$).",
     r"($16$--$18$ ms per episode across the three horizons tested, \texttt{results\_\allowbreak mcts\_\allowbreak efe.csv}), compared to $88.1\% \pm 0.2$pp for POMCP at the same simulation count ($12$--$14$ ms per episode across horizons, seed-level SE, seed-level Welch $p{=}4.4{\times}10^{-6}$).", 1),
    ("Y2 objection one",
     r"The sweep changes the Tiger reading substantially. At its best swept constant POMCP reaches $96.3\% \pm 0.6$pp success, and we cannot distinguish that configuration from MCTS-EFE at its default constant on either metric, that is, we fail to reject the null hypothesis of no difference (seed-level Welch $p{=}0.09$ and $p{=}0.54$). The $88.8\%$ figure above therefore measures an untuned constant rather than the solver. The sweep also shows MCTS-EFE's default is not its own best, so the appendix compares the two solvers with each at a constant selected on tuning seeds disjoint from every evaluation seed, under a rule recorded before the selection was run. At those constants, MCTS-EFE stays ahead on Tiger success ($98.2\% \pm 0.3$pp against $96.3\% \pm 0.6$pp, $p{=}0.024$, surviving Holm correction within the appendix's six-test family) with reward not distinguishable ($p{=}0.16$), so tuning narrows the Tiger gap sharply without removing it. Because the canonical runs had been inspected before the rule was written, that narrow Tiger result is retrospective evidence rather than a prospective confirmation, and a confirmatory claim would need fresh evaluation seeds that no one has looked at. The Diagnosis and Tileworld differences are large enough that the same caveat does not change their reading. Where the agent must choose among tests, tuning the constant leaves most of the gap in place. POMCP's selected configuration reaches $71.4\% \pm 1.5$pp on Diagnosis and $19.7\% \pm 1.7$pp on Tileworld-$6{\times}6$",
     r"On Tiger the constant matters. At its best swept constant POMCP reaches $93.2\% \pm 0.5$pp success against $87.3$ to $89.0\%$ at constants up to $10$, but it remains behind MCTS-EFE at its default constant on both metrics after Holm correction. The sweep also shows MCTS-EFE's default is not its own best, so the appendix compares the two solvers with each at a constant selected on tuning seeds disjoint from every evaluation seed, under a rule recorded before the corrected runs reported here. At those constants, MCTS-EFE stays ahead on Tiger success ($98.2\% \pm 0.3$pp against $93.2\% \pm 0.5$pp, $p{=}0.0001$) and reward ($p{=}0.0005$), both surviving Holm correction within the appendix's six-test family, so tuning narrows the Tiger gap without removing it. Where the agent must choose among tests, tuning the constant leaves most of the gap in place. POMCP's selected configuration reaches $65.6\% \pm 1.4$pp on Diagnosis and $8.2\% \pm 0.6$pp on Tileworld-$6{\times}6$", 1),
    ("Y3 objection two",
     r"At $c{=}5$ they put Diagnosis at $71.4\%$ against the uniform-rollout POMCP's $68.2$ at the same constant and Tileworld-$6{\times}6$ at $19.1\%$ against $11.3$, neither difference surviving Holm correction (seed-level Welch $p{=}0.25$ and $p{=}0.023$).",
     r"At $c{=}5$ they put Diagnosis at $66.8\%$ against the uniform-rollout POMCP's $65.6$ at the same constant, not a significant difference, and Tileworld-$6{\times}6$ at $8.2\%$ against $2.6$, a difference that survives Holm correction on success but leaves POMCP more than eighty points behind.", 1),
    ("Y4 taken together",
     r"as on Tiger, tuning the constant recovers most of the difference. Where the agent must choose which of several tests to run, neither control removes more than a small part of the gap, which stays above twenty points on Diagnosis and above seventy points on Tileworld-$6{\times}6$ at every swept configuration.",
     r"as on Tiger, tuning the constant narrows the difference without removing it. Where the agent must choose which of several tests to run, neither control removes more than a small part of the gap, which stays above twenty-five points on Diagnosis and above eighty points on Tileworld-$6{\times}6$ at every swept configuration.", 1),
]


def main() -> int:
    texts = {p: p.read_text() for p in MASTERS}
    ok = True
    for p in MASTERS:
        t = texts[p]
        for eid, old, new, n in EDITS:
            c = t.count(old)
            if c != n:
                print(f"FAIL {p.name} {eid}: found {c}, expected {n}")
                ok = False
                continue
            t = t.replace(old, new)
        texts[p] = t
    if not ok:
        print("Nothing written.")
        return 1
    for p, t in texts.items():
        p.write_text(t)
    print(f"Applied {len(EDITS)} edits to both masters.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
