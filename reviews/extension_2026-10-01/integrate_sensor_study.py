"""One-time, guarded integration of the frozen public-data results."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
main = r"""\subsection{Sensor Records with Learned Likelihoods}
\label{sec:real_sensor}

We next test calibration on recorded observations with a learned model. The UCI Gas Sensor Array Drift dataset contains $13{,}910$ exposures to six gases, measured by sixteen sensors \citep{vergara2012data,vergara2012}. Acquiring a sensor reveals its eight stored descriptors once. This is retrospective access to recordings, not selective operation of the original instruments. Before evaluating policies or inspecting usage curves, we fixed targets $B\in\{2,4,8\}$ accesses per case. They are researcher-defined requirements, not operator-supplied needs or measured energy budgets.

Batches 1--6 provide $3{,}550$ training, $1{,}175$ calibration and $1{,}208$ test cases, stratified by batch and class. Training alone determines eight categories per sensor, class priors and smoothed categorical likelihoods. Policies assume conditional independence of sensors given gas identity, use one-observation lookahead, and cannot reacquire a sensor. Each action reveals the case's actual category. Correct classification earns $1$, with a benchmark cost of $0.02$ per access. All methods share this fitted model. We compare the crossing mixture with calibration-selected equality mixtures from a direct usage-penalty family, a best equality mixture within the weight grid, and greedy conditional-information acquisition that takes exactly $B$ sensors. Greedy information acquisition is an established approach \citep{covert2023}, and this comparison does not reproduce a learned neural acquisition method. Appendix~\ref{app:real_sensor} gives the frozen grids, splits and uncertainty procedure.

The weight family cannot reach $B=2$, whose target is below its smallest calibration usage, $3.424$. The two straddled targets transfer closely to unseen cases, with mean usage $4.006$ and $8.019$. Their Bonferroni-adjusted $98.333\%$ conditional bootstrap intervals for usage error are $[-0.210,0.255]$ and $[-0.362,0.411]$, inside the predeclared $\pm0.5$ tolerance. Each of the $2{,}000$ replicates reselects the calibration crossing. None fails at $B=4$ or $8$, whereas all fail at $B=2$. Thus two targets meet the usage criterion, and the all-three-target requirement fails.

Accurate usage does not make the selected policy competitive on classification. At $B=4,8$, the crossing mixtures achieve $80.23\%$ and $76.28\%$ accuracy, against $82.11\%$ and $80.18\%$ for direct equality mixtures and $81.71\%$ and $79.47\%$ for exact-count greedy information acquisition. The direct mixtures use $3.965$ and $7.977$ sensors on test cases, so their realized usage is close but not identical to the crossing mixtures'. Each nominal paired accuracy-gap interval lies below zero (Figure~\ref{fig:real_sensor}). The best equality mixtures within the weight grid also do better, at $82.12\%$ and $78.41\%$. The direct and exact-count policies can serve $B=2$, with $80.08\%$ and $81.04\%$ accuracy. These results favor the simpler controls in this configuration, not calibration as a general acquisition algorithm.

Frozen calibration does not transfer to the $7{,}977$ later cases in batches 7--10. Across those batches, the $B=4$ mixture uses $5.15$--$6.51$ sensors and the $B=8$ mixture uses $9.49$--$12.73$. Accuracy also falls, reaching $14.56\%$ and $11.56\%$ in batch 8. The model is deliberately approximate. Even within the test period, the full-record classifier has log loss $2.237$, worse than the prior's $1.674$, despite higher accuracy. The study therefore demonstrates within-period usage calibration and its limits under learned likelihoods and collection shift. It provides neither deployment validation nor a general robustness advantage.

\begin{figure}[tbp]
\centering
\includegraphics[width=\linewidth]{figures/real_sensor_transfer.pdf}
\caption{Usage transfer and accuracy costs on recorded sensor cases. (a) Frozen crossing-mixture usage minus its target on within-period test cases and later batches. The gray band is the predeclared $\pm0.5$ access tolerance. Test intervals are $98.333\%$ conditional bootstrap intervals with calibration reselection. Later intervals are nominal $95\%$ intervals with selections fixed. Positions denote collection groups, not equal elapsed times. (b) Paired test accuracy gaps against direct equality mixtures and exact-count greedy conditional-information acquisition (CMI), with nominal $95\%$ intervals including calibration reselection. Positive gaps favor the crossing mixture. Direct mixtures need not exactly meet the target on test cases. All intervals condition on one trained model and within-stratum case exchangeability. The unbracketed $B=2$ request is retained as unavailable.}
\label{fig:real_sensor}
DESCRIPTION_PLACEHOLDER
\end{figure}

"""
description = r"\Description{Two panels retain all three fixed sensor-access targets. The left plots crossing-mixture usage minus target for within-period held-out cases and four later batches. Error bars surround the estimates, and a gray half-sensor tolerance band surrounds zero. Both available targets are near zero on test cases and above tolerance on every later batch. The right plots negative paired test accuracy gaps against direct equality and exact-count information acquisition, with interval bars entirely below zero. The two-sensor target is labeled unavailable rather than given a numerical outcome.}"

appendix = r"""\FloatBarrier
\subsection{Retrospective Sensor-Acquisition Protocol}
\label{app:real_sensor}

The protocol for Section~\ref{sec:real_sensor} was committed before calibration or held-out evaluation. Targets, model, grids, split rules and inferential margins were fixed together. The sensor archive's ten chronological batches and consecutive eight-descriptor sensor blocks follow its primary documentation \citep{vergara2012data}. All sixteen sensors originally operated together. This study masks access to their stored records and does not measure physical sensing costs.

Within each batch/class stratum of batches 1--6, a permutation with seed $20261001$ assigns floor proportions $60\%$ to training and $20\%$ to calibration, with the remainder to testing. Exact duplicate feature vectors would be grouped before splitting, and any overlap with later batches excluded from the primary transfer summary. Neither duplicates nor cross-period overlaps occur in this archive. Batch/class stratification preserves represented collection periods, not independence of laboratory exposures. Batches 7--10 contain $3{,}613$, $294$, $470$ and $3{,}600$ cases, respectively. Each is evaluated separately, with an equal-batch mean also archived. No later label adjusts a prior, model, weight or mixture.

For each sensor, training-only standardization precedes eight-center $k$-means with ten initializations, at most $300$ iterations and seed $20261001+j$ for zero-based sensor index $j$. Add-one smoothing estimates the six-class prior and each class-conditional categorical distribution. Real sensors need not satisfy the model's conditional-independence assumption. Acquisition reveals the held-out row's encoded value, never a simulated draw from the learned likelihood. The observed-sensor mask augments the planning state. At belief $b$, the one-observation acquisition value for an unobserved sensor $j$ is
\[
Q_w(j,b)=-0.02+wI_b(Y;Z_j)+\sum_z P(z\mid b,j)\max_y b(y\mid z,j),
\]
with information in bits and stopping value $\max_y b(y)$. This is the $H=1$ observe-then-commit convention of Section~\ref{sec:agents}, replanned after each access. Numerical ties favor stopping, then the lowest sensor index, using a relative tolerance of $10^{-12}$ times the largest absolute eligible score or stopping value. Classification ties use the lowest class ID. No case acquires a sensor twice.

The information grid is the sorted union $\{0,\ln2,1\}\cup\{2^k:k=-8,\ldots,8\}$. Direct policies omit information gain and replace the acquisition cost by $0.02+\lambda$, with $\lambda\in\{0,-0.02\}\cup\{\pm2^k:k=-10,\ldots,1\}$. Negative effective penalties are explicit benchmark subsidies that allow equality references to spend more. Every return is nevertheless scored at the common base cost $0.02$. The direct and information-grid equality references maximize estimated calibration return over per-case mixtures with expected calibration usage equal to $B$. Separate cap references replace equality by an upper bound. These are sampled-family linear programs, not global constrained optima. Direct equality selections at $B=4$ and $8$ mix the $\lambda=-2$ and $\lambda=2^{-6}$ policies. The crossing rule uses weights $(0.0625,0.125)$ at $B=4$ and $(8,16)$ at $B=8$, with upper probabilities $0.41328$ and $0.22276$. Its calibration curve has one descending grid step, so monotonicity is not assumed. Any unbracketed request fails the declared crossing criterion, even if a separate policy can attain it.

The fixed-count CMI policy greedily selects the unobserved sensor with largest model conditional information gain and stops after exactly $B$ accesses. A fixed-order control instead ranks sensors once by training-prior information. Zero-access, full-access and weights $0$, $1$, and $\ln2$ are also archived. On within-period test cases, the fixed-order accuracies at $B=2,4,8$ are $68.87\%$, $68.96\%$ and $76.82\%$. The weight-one and nat-canonical policies use $6.280$ and $5.985$ sensors with accuracies $75.99\%$ and $75.91\%$. These controls isolate aspects of this fitted model and acquisition family. They are not a comparison with state-of-the-art active feature acquisition.

Each deterministic candidate is evaluated on every relevant recorded case, with ordered acquisitions, observed categories, posterior, prediction, usage and base return archived. Mixture expectations average the candidate contributions analytically, representing a random endpoint chosen once per case. A separately seeded realization checks that implementation. Candidate evaluations do not create additional independent cases.

Within-period uncertainty uses $2{,}000$ paired bootstrap replicates, with calibration and test rows resampled independently within their original batch/class strata. Each calibration resample reselects all crossing brackets and fitted LP supports. All policies share the resampled test cases. The three usage-error intervals use Bonferroni-adjusted $98.333\%$ coverage, giving a nominal simultaneous $95\%$ family under the bootstrap assumptions. The margin is $\pm0.5$ accesses, and all targets must pass for the study-wide criterion. Accuracy comparisons have nominal paired $95\%$ intervals, with no family-wide superiority claim. Failed fits are retained in the denominator. No interval is reported for the $2$-sensor crossing, which fails in all replicates. Both higher-target crossings and their references remain feasible throughout. Later-batch intervals resample within each batch/class while holding the original calibration selections fixed. Every interval conditions on one fitted model and assumed exchangeability within strata. It excludes retraining, unobserved dependence among exposures and variation across devices or sites.

The archive reports accuracy, balanced accuracy, class-specific usage, base return, log loss and Brier score. More access need not improve this approximate model's predictions. Full-record test accuracy is $76.32\%$, below reward-only planning's $82.04\%$ at $3.385$ accesses, and full-record log loss is worse than the prior's. Later shifts include changing class proportions as well as sensor responses. Their effects are not separated causally. The results support neither a deployment claim nor the premise that every usage target expresses an external need.

The source checksum, training transforms, row partitions, policies and analysis are reproducible from \texttt{experiments/\allowbreak run\_real\_sensor\_study.py} and \texttt{experiments/\allowbreak analyze\_real\_sensor\_study.py}, with instructions in \texttt{results/\allowbreak real\_sensor\_2026-10-01/\allowbreak README.md}. Computation is CPU only. Model fitting takes $0.44$ seconds, calibration replay $1.71$ seconds, held-out replay $13.68$ seconds and the complete analysis $6.12$ seconds on the recorded host. Peak replay process memory is approximately $186$ MB. Timings describe vectorized batches, not per-case response latency. All selected policies, including failures, are retained in \texttt{results\_real\_sensor\_summary.csv}.

"""

edits = [
    ("We study uncertainty about state under a known model, and retain dependence on a shared reward convention when describing $w=1$ as untuned.",
     "Our planners treat the observation model as fixed, either supplied by a simulator or fitted once from training records. They do not plan to learn that model. Describing $w=1$ as untuned still depends on a shared reward convention."),
    ("Within a fixed reward convention, the information-unit weight $w{=}1$ is a robust untuned default.",
     "Within a fixed reward convention, the information-unit weight $w{=}1$ is a reproducible default whose usefulness must be evaluated empirically."),
    ("The held-out targets are calibration-derived rather than application-specified. Deployment requires a supplied model and a calibration check under the intended operating conditions.",
     "The simulated targets are calibration-derived. The sensor-record targets were fixed independently of usage curves, but are researcher-defined rather than application requirements. Their later-batch failures require a fresh transfer check before using a frozen calibration."),
    ("The benchmarks use known models, and Structural Inspection uses a synthetic task and a hand-coded leaf rule. Learned models, more efficient search, transition-aware budget control and validation against an operational sensing requirement remain open.",
     "The simulators use known models, and Structural Inspection uses a synthetic task and a hand-coded leaf rule. The sensor-record study learns a model, but its shallow planner and conditional-independence approximation establish no general acquisition advantage. More efficient search, transition-aware budget control and validation against an operational sensing requirement remain open."),
    ("The held-out study shows accurate usage calibration but also its reward cost. Meeting an equality target can earn less than spending below it, and the selected mixture need not be optimal within the family or against the constrained reference. Calibration is appropriate when expected usage itself is the requirement.",
     "The simulated held-out study shows accurate usage calibration but also its reward cost. Real sensor records extend the test to learned likelihoods and targets fixed independently of usage curves. Two targets transfer within the represented collection period, one is unattainable, and later batches defeat frozen calibration. Direct cost tuning and fixed-count information acquisition also give better test accuracy in that configuration. Calibration is therefore a way to adapt an already-selected information-weighted family to a feasible expected-use target, subject to a transfer check. It is not a reason to prefer that family when directly counting or penalizing accesses meets the design need."),
    ("The untuned $w=1$ lies in the reward-maximizing run of sampled weights on three of five swept environments and is beaten on the other two.\n\\textbf{Conclusions:}",
     "On real sensor records with learned likelihoods, two independently fixed targets transfer within the represented collection period, one is unattainable, and later batches defeat frozen calibration. Direct-penalty and fixed-count policies achieve better classification accuracy.\n\\textbf{Conclusions:}"),
    ("Third, it evaluates the calibration procedure and the information-unit default against reward-only planning, tuned information gain, POMCP, and near-optimal offline references.",
     "Third, it evaluates calibration and the information-unit default against planning baselines and offline references, then tests learned likelihoods on real sensor records with independently fixed targets and a chronological transfer set."),
]

for filename in ('full_paper_jair.tex','full_paper.tex'):
    p=ROOT/'paper'/filename;s=p.read_text()
    for old,new in edits:
        # LNCS uses an unstructured abstract; its summary receives a separate edit below.
        if old.endswith('\\textbf{Conclusions:}') and filename=='full_paper.tex':continue
        assert s.count(old)==1,(filename,old[:100],s.count(old))
        s=s.replace(old,new,1)
    s=s.replace(r'\subsection{Reward-Irrelevant Sensing}',main.replace('DESCRIPTION_PLACEHOLDER',description if filename=='full_paper_jair.tex' else '')+r'\subsection{Reward-Irrelevant Sensing}',1)
    marker='\\FloatBarrier\n\\section{Extended Budget Evidence}'
    assert s.count(marker)==1
    s=s.replace(marker,appendix+marker,1)
    related="Information-directed sampling (IDS) trades instantaneous regret"
    assert s.count(related)==1
    s=s.replace(related,"Dynamic feature acquisition can greedily select features by conditional mutual information, with learned approximations to the required distributions \\citep{covert2023}. Our sensor-record study uses this established greedy rule as a fixed-count comparator. Its purpose is to test usage calibration within an information-weighted family, not introduce a new feature-selection principle.\n\n"+related,1)
    p.write_text(s)

(Path(__file__).with_name('sensor_integration_hashes.json')).write_text(json.dumps({n:hashlib.sha256((ROOT/'paper'/n).read_bytes()).hexdigest() for n in ('full_paper_jair.tex','full_paper.tex')},indent=2)+'\n')
