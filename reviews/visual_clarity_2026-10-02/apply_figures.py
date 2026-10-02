"""Guarded mirrored manuscript edits for the reader-requested figure pass."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
LABELS = ('fig:engineering_workflow', 'fig:collapse', 'fig:real_sensor', 'fig:tw_scaling')

def figure_span(source, label):
    marker = r'\label{' + label + '}'
    assert source.count(marker) == 1, label
    pos = source.index(marker)
    start = source.rfind(r'\begin{figure}', 0, pos)
    end = source.index(r'\end{figure}', pos) + len(r'\end{figure}')
    assert start >= 0 and r'\end{figure}' not in source[start:pos]
    return start, end

def replace_once(source, old, new):
    assert source.count(old) == 1, (old[:70], source.count(old))
    return source.replace(old, new, 1)

FIGURES = {
'fig:collapse': r'''\begin{figure}[tbp]
\centering
\includegraphics[width=\textwidth]{figures/price_scale_invariance.pdf}
\caption{Reward-scale transfer on Diagnosis at the expected-use target $B=8$. (a) The open-to-closed segments show the grid brackets in raw weight $w$ when rewards and sensing costs are multiplied by $\alpha\in\{0.1,1,10\}$. They shift tenfold with the scale. (b) After dividing weight by $\alpha$, all 14 matched grid-point usage means and seed-level SEs coincide exactly, so the common curve is drawn only once. The dashed line is $B=8$, and the open-to-closed segment is the shared bracket $(0.141,0.323]$. The segment marks grid resolution, not a confidence interval or a policy attaining $B$; the curve between grid points is unresolved. Five seeds and 100 episodes per seed share per-episode random streams.}
\label{fig:collapse}
\Description{Two panels show why reward scaling requires a matching change of information weight. On the left, three horizontal open-to-closed intervals for the same target occur at progressively larger raw weights as the scale multiplier rises from 0.1 to 1 to 10. On the right, one plotted Diagnosis usage curve against normalized weight w divided by alpha rises from about 5.9 to 9.8 observations between two sampled weights. All three scale conditions have the same 14 measured point estimates and seed errors at these normalized weights, so the redundant curves are omitted. A dashed line marks eight observations and a short open-to-closed segment marks the common grid bracket from 0.141 to 0.323.}
\end{figure}''',
'fig:real_sensor': r'''\begin{figure}[tbp]
\centering
\includegraphics[width=\linewidth]{figures/real_sensor_transfer.pdf}
\caption{Usage transfer and accuracy costs on recorded sensor cases for the two available crossings, $B=4$ and $B=8$. (a) Each point is mean usage minus its target on within-period test cases or one later batch. The gray band is the predeclared $\pm0.5$ access tolerance. Test intervals have $98.333\%$ conditional bootstrap coverage with calibration reselection; later intervals are nominal $95\%$ with selections fixed. Collection groups are categorical, so points are not connected. (b) Paired test accuracy gaps against direct equality mixtures and exact-count greedy conditional-information acquisition (CMI), with nominal $95\%$ intervals including calibration reselection. Positive gaps favor the crossing mixture. Direct mixtures need not exactly meet $B$ on test cases. All intervals condition on one fitted model and within-stratum case exchangeability. The fixed $B=2$ request has no calibration crossing and fails the all-target criterion; it is stated here rather than plotted as a measurement.}
\label{fig:real_sensor}
\Description{Two panels plot the available four- and eight-access crossing mixtures. The left panel shows separate estimates of usage minus target on held-out cases and four later batches, with intervals and a gray half-sensor tolerance band around zero. Both targets are met on test cases and overshot in every later batch. The right panel shows two negative paired accuracy gaps per target against a direct equality mixture and exact-count conditional-information acquisition; all four intervals lie below zero. The unavailable two-access crossing is stated in the caption, with no point placed on either axis.}
\end{figure}''',
'fig:tw_scaling': r'''\begin{figure}[tbp]
\centering
\includegraphics[width=\linewidth]{figures/fig_tileworld_scaling.pdf}
\caption{Why fixed-depth Planning fails on the largest Tileworld grid ($H=2$, 200 episodes per seed over five seeds). (a) Planning and EFE have similar success at $4{\times}4$ and $6{\times}6$, but at $8{\times}8$ Planning falls to $1.4\%$ while EFE reaches $69.4\%$. (b) Planning takes no scans at $8{\times}8$, compared with EFE's $17.50$ per episode. The fixed $w=100$ Planning+IG comparator reaches $97.8\%$ success using $39.52$ scans, but earns $-30.84$ mean reward against EFE's $-25.86$ (reward not plotted). Panel (a) error bars are seed-level SE; panel (b) shows mean scan counts without uncertainty bars. The other two agents, rewards, and timing measurements remain in \texttt{results\_tileworld\_scaling.csv}.}
\label{fig:tw_scaling}
\Description{Two panels show three policy series across Tileworld grids of size four by four, six by six, and eight by eight. The left panel shows success: Planning and EFE are both near 75 percent at the smaller grids, but Planning drops to roughly 1 percent at eight by eight while EFE remains near 69 percent. The fixed-weight Planning plus information-gain comparator stays near 98 percent. The right panel shows the associated mean scan counts. Planning drops from about 16 scans to zero on the largest grid, EFE increases to about 17.5, and the fixed high-weight comparator rises to about 39.5.}
\end{figure}''',
}

def apply(path):
    source = path.read_text()
    before_hash = hashlib.sha256(source.encode()).hexdigest()
    start, end = figure_span(source, 'fig:engineering_workflow')
    source = source[:start] + source[end:]
    source = replace_once(source,
        r"Figures~\ref{fig:hero} and~\ref{fig:engineering_workflow} connect this construction to the engineer's workflow.",
        r'Figure~\ref{fig:hero} illustrates the crossing and endpoint mixture. The same construction guides an inspection engineer from a usage requirement to a running policy.')
    for label, replacement in FIGURES.items():
        start, end = figure_span(source, label)
        source = source[:start] + replacement + source[end:]
    assert 'fig:engineering_workflow' not in source
    assert all(source.count(r'\label{' + label + '}') == 1 for label in FIGURES)
    path.write_text(source)
    return {'before': before_hash, 'after': hashlib.sha256(source.encode()).hexdigest()}

if __name__ == '__main__':
    report = {name: apply(ROOT / 'paper' / name) for name in
              ('full_paper_jair.tex', 'full_paper.tex')}
    (Path(__file__).with_name('figure_application.json')).write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
