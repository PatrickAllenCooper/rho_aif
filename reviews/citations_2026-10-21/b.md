# Independent citation audit, subset B

Date: 2026-10-21. Baseline: `68a9c137c4529675b3fe097ccda351e464dc3afc`.

All 23 identities are authenticated. No fabricated reference or metadata correction was found. All three attribution precision findings were corrected by root and independently rechecked in both live masters. No further subset-B wording correction is required.

Lindley’s original English text remains inaccessible to this auditor. Root independently read the publisher-hosted Russian translation and reports direct support; this report explicitly distinguishes that cross-auditor evidence from this auditor’s own unsuccessful retrieval. Howard’s original journal scan was read on a third-party host, with provenance retained.

All 34 citation occurrences in the master and its sole table input were counted and checked. Source files were not changed by this auditor.

## Post-fix review

All three source-attribution precision corrections accepted after independent reread in both masters. No further wording change required for subset B.

JAIR lines 146, 156, and 454; LNCS lines 99, 109, and 407. The IDS statement now includes the square, expectation, and action distribution. The Oudeyer statement no longer implies a 2007 review of later algorithms. The rational-inattention statement concerns information prices and constraints, without attributing an online adaptation rule.

Post-fix SHA-256:

- `paper/full_paper_jair.tex`: `5b86fb4963cb04b65926ef86d0da58c14a4c1a37db3b7f14810941b038eafd1f`
- `paper/full_paper_jair.bib`: `e16f1d97e713b71498540c05f30b8f7ad4088ea777c1960162be1111bbfb6592`
- `paper/full_paper.tex`: `326fe1a69322c416bea55658ba39ab30aef0ee6a58d7d61f32ca2a6611ab56ba`

## haarnoja2018

Authenticity: verified.

Title and four authors in correct order match PMLR. ICML 2018; optional omitted pages are 1861–1870 in volume 80.

Official abstract describes off-policy maximum-entropy actor–critic maximizing expected reward plus policy entropy.

Checked primary records:

- https://proceedings.mlr.press/v80/haarnoja18b.html

Manuscript uses:

- L156: SAC is an algorithmic instance of maximum-entropy control. Verdict: supported.

## haarnoja2018sac

Authenticity: verified.

Title, all 11 authors/order and arXiv identifier match. 2018 is v1 date; v2 is January 2019, which does not invalidate cited preprint year.

Introduction and §§5–6 derive automatic temperature tuning; eq.(11) imposes a minimum expected entropy target and eqs.(17)–(18)/Algorithm 1 give dual temperature adjustment.

Checked primary records:

- https://arxiv.org/abs/1812.05905
- https://arxiv.org/html/1812.05905v2

Manuscript uses:

- L159: Automatic temperature tuning drives policy entropy toward a target. Verdict: supported.
- L421: Manuscript adapts the SAC update, substituting sensing usage for entropy. Verdict: supported.
- L454: SAC is a precedent for information pricing and constraints. Verdict: supported.

## houthooft2016

Authenticity: verified.

Actual proceedings PDF title page confirms exactly the six listed authors and order. Landing page incorrectly duplicates Xi Chen, so PDF controls. Title and NIPS 2016 match.

Abstract and paper §2 define information gain about dynamics as a weighted reward augmentation. The model-uncertainty distinction in manuscript is appropriate.

Checked primary records:

- https://proceedings.neurips.cc/paper/2016/hash/abd815286ba1007abfbb8415b83ae2cf-Abstract.html
- https://proceedings.neurips.cc/paper_files/paper/2016/file/abd815286ba1007abfbb8415b83ae2cf-Paper.pdf

Manuscript uses:

- L156: VIME uses a weighted exploration bonus. Verdict: supported.

Access/provenance notes:

- Official NeurIPS landing-page author list duplicates Xi Chen. The underlying official PDF confirms the manuscript list, so no bibliography correction is needed.

## howard1966

Authenticity: verified.

Fresh publisher-deposited Crossref record confirms title, Ronald Howard, IEEE Transactions on Systems Science and Cybernetics, 2(1), 22–26, 1966. Original scan separately shows Ronald A. Howard.

Original journal scan/OCR, p.24, eq.(13), defines expected value of clairvoyance as the improvement in expected profit; pp.25–26 discuss imperfect information and experimental programs. This supports the manuscript’s broad decision-value characterization.

Checked primary records:

- https://api.crossref.org/works/10.1109/TSSC.1966.300074

Manuscript uses:

- L142: Classical VOI measures improvement an observation can bring to a decision. Verdict: supported.

Access/provenance notes:

- IEEE article and abstract endpoints were blocked (JavaScript/bot challenge/418). Content checked in publicly readable original journal scan/OCR hosted by Scribd, not its AI-enhanced title/summary. That is primary textual material on an unofficial host; exact publisher-byte equivalence was not established.

Other attempted or original-scan URLs:

- https://www.scribd.com/document/320139530/Howard-1966-Information-Value-Theory
- https://ieeexplore.ieee.org/document/4082064/
- https://ieeexplore.ieee.org/abstract/document/4082064

## kaelbling1998

Authenticity: verified.

Crossref and MIT author-hosted journal PDF confirm exact title, all three authors/order, 1998, Artificial Intelligence 101(1–2), 99–134.

Intro/§3 establish decision making under partial observability. §5.1 explicitly gives Tiger two states, accuracy .85, listen cost 1, good door +10, bad door −100. Original problem resets after opening; manuscript clearly uses its own terminal-commit variant.

Checked primary records:

- https://api.crossref.org/works/10.1016/S0004-3702(98)00023-X
- https://people.csail.mit.edu/lpk/papers/aij98-pomdp.pdf

Manuscript uses:

- L135: POMDPs formalize decision making under state uncertainty. Verdict: supported.
- L467: Tiger benchmark and numeric observation/reward parameters. Verdict: supported.

## kim2011cpomdp

Authenticity: verified.

Institutional record and official PDF confirm title, Dongho Kim/Jaesong Lee/Kee-Eung Kim/Pascal Poupart order, IJCAI 2011, pages 1968–1974.

Abstract and §§2–3 present cost-constrained belief-space dynamic programming and randomized policies. §2.2 example and §5.1 show deterministic policies can be suboptimal; general policies select actions by belief and remaining cost.

Checked primary records:

- https://pure.kaist.ac.kr/en/publications/point-based-value-iteration-for-constrained-pomdps/
- https://www.ijcai.org/Proceedings/11/Papers/329.pdf

Manuscript uses:

- L159: CPOMDP methods track admissible cost alongside belief. Verdict: supported.
- L350: Randomization can be needed in constrained POMDPs. Verdict: supported.
- L456: A CPOMDP solver may randomize belief-dependently and outperform an episode-fixed weight mixture. Verdict: supported_as_structural_inference. Evidence: The cited paper supplies the broader randomized class; it does not experimentally compare against this manuscript’s specific mixture. Manuscript says may, which is appropriate.

Access/provenance notes:

- Initial IJCAI PDF request timed out, but retry succeeded and full text was checked.

## kouw2026bethe

Authenticity: verified.

Exact title, sole author Wouter M. Kouw, arXiv ID and August 17 2026 initial date match.

Abstract explicitly imposes an information constraint on the Bethe functional, introduces a corresponding KKT multiplier, and identifies EFE at a specific multiplier. This is not an observation-count constraint.

Checked primary records:

- https://arxiv.org/abs/2608.17167

Manuscript uses:

- L159: A dual formulation of EFE itself is distinct from the manuscript’s sensing calibration. Verdict: supported.
- L454: Information constraint internal to EFE differs from episode-level sensing control. Verdict: supported.

## kurniawati2008

Authenticity: verified.

Official RSS IV proceedings record verifies exact SARSOP title, Hanna Kurniawati/David Hsu/Wee Sun Lee, 2008 and venue.

Abstract describes point-based planning exploiting optimally reachable belief spaces. Manuscript explicitly calls its SARSOP result near-optimal rather than certified exact; local solver build/precision are manuscript facts, not attributed to source.

Checked primary records:

- https://www.roboticsproceedings.org/rss04/p9.html

Manuscript uses:

- L135: SARSOP is a point-based offline solver on reachable beliefs. Verdict: supported.
- L550: SARSOP reference solver identification. Verdict: supported.

## laouar2026voi

Authenticity: verified.

Fresh Crossref publisher record confirms title, Zakariya Laouar/Qi Heng Ho/Zachary Sunberg order, ICAPS 2026, 152–160; volume36 issue1 are optional absent fields. Manuscript Z. initial matches primary deposited name.

Publisher-deposited abstract describes VOIMCP avoiding observation branching when decision VOI is low. The distinction from adding information gain to the planning reward is accurate.

Checked primary records:

- https://api.crossref.org/works/10.1609/icaps.v36i1.42824
- https://arxiv.org/abs/2604.01434

Manuscript uses:

- L135: VOIMCP selectively skips observation branches with low expected decision value. Verdict: supported.

Access/provenance notes:

- AAAI article endpoint returned 503. Fresh Crossref DOI record includes full publisher-deposited abstract and publication metadata; arXiv independently authenticates the work.

## levine2018

Authenticity: verified.

Exact title, sole author Sergey Levine, arXiv ID and May2018 initial year match.

Abstract explicitly relates maximum-entropy reinforcement learning to exact inference under deterministic dynamics and variational inference under stochastic dynamics. Manuscript makes a broad relation, not unconditional exact-equivalence claim.

Checked primary records:

- https://arxiv.org/abs/1805.00909

Manuscript uses:

- L156: Control-as-inference relates maximum-entropy control to probabilistic inference. Verdict: supported.

## lindley1956

Authenticity: verified.

Fresh publisher-deposited Crossref record confirms exact title, D.V. Lindley, Annals of Mathematical Statistics 27(4), 986–1005, December1956.

Primary full text and abstract could not be retrieved by this auditor. Secondary transcriptions of the abstract are consistent with the claimed experimental-design use, but are not treated as fresh primary verification.

Checked primary records:

- https://api.crossref.org/works/10.1214/aoms/1177728069

Manuscript uses:

- L142: Bayesian experimental design commonly selects observations by expected information gain. Verdict: primary_text_verification_incomplete.

Access/provenance notes:

- English original on Project Euclid/JSTOR remains blocked. Repeated independent Mathnet publisher PDF and record opens timed out, including root-provided successful web reference ID. This subset auditor does not claim to have read the translation. Root separately reports direct publisher-hosted Russian translation evidence supporting the manuscript; see cross-auditor follow-up below.

Other attempted or original-scan URLs:

- https://projecteuclid.org/journals/annals-of-mathematical-statistics/volume-27/issue-4/On-a-Measure-of-the-Information-Provided-by-an-Experiment/10.1214/aoms/1177728069.full
- https://projecteuclid.org/download/pdf_1/euclid.aoms/1177728069
- https://www.jstor.org/stable/2237191
- https://www.mathnet.ru/eng/mat101
- https://www.mathnet.ru/php/getFT.phtml?jrnid=mat&option_lang=eng&paperid=101&what=fullt

Cross-auditor follow-up:

Root reports successful access to the [publisher-hosted Russian translation](https://www.mathnet.ru/php/getFT.phtml?jrnid=mat&option_lang=eng&paperid=101&what=fullt). Printed p.88 §2 states the experimental rule to choose the experiment with greatest expected increase in information; printed p.90 Definitions 1–2 and equations (6)–(7) define observed and expected information gain. Verified by root, not independently retrieved by subset-B auditor; root consolidation owns final source check.

## maisto2025

Authenticity: verified.

Crossref and institutional journal PDF confirm title, all four authors/order, Neurocomputing623, article129319, 2025. DOI includes2024 and preprint begins2021; printed journal year2025 is correct.

Journal abstract and AcT Algorithm1 combine active inference planning with sampled tree search; this supports grouped scaling-work characterization. Manuscript does not attribute all deep/RL/MCTS elements individually to this source.

Checked primary records:

- https://api.crossref.org/works/10.1016/j.neucom.2024.129319
- https://arxiv.org/abs/2103.13860
- https://iris.cnr.it/retrieve/1d947b32-cbcf-4136-8299-07721aa765d8/1-s2.0-S0925231224020903-main.pdf

Manuscript uses:

- L153: Scaling active inference includes tree-search methods. Verdict: supported.

Access/provenance notes:

- ScienceDirect article page gave403, resolved via author institution’s journal PDF and Crossref.

## matejka2015

Authenticity: verified.

Official AEA record confirms full title, Filip Matějka/Alisdair McKay order, American Economic Review105(1),272–298, January2015.

Abstract models costly information acquisition through rational inattention. Supports information pricing/capacity, but abstract does not support online adaptation of a price parameter.

Checked primary records:

- https://www.aeaweb.org/articles?id=10.1257/aer.20130047

Manuscript uses:

- L159: Rational inattention constrains or prices information capacity. Verdict: supported.
- L454: Information prices and resource constraints are classical in rational inattention. Verdict: supported_after_revision. Evidence: This source supports costly information acquisition, not an online update rule.

Findings:

- Replace the broad adaptation claim with Information prices and resource constraints are classical in constrained MDPs and rational inattention; reserve adaptation specifically for SAC or another source that actually derives an update. Status: resolved_and_independently_rechecked_2026-10-21.

## millidge2020

Authenticity: verified.

Official Springer chapter verifies title, all four authors/order, IWAI2020, Springer, pp3–11 and December18,2020.

Abstract explicitly locates primary AIF/CAI difference in how rewards/goals are encoded in generative models and consequent objective/exploration differences.

Checked primary records:

- https://link.springer.com/chapter/10.1007/978-3-030-64919-7_1

Manuscript uses:

- L156: Control-as-inference treats value differently from active inference. Verdict: supported.

Access/provenance notes:

- Full chapter is subscription-only; official abstract directly supports the single broad attributed claim.

## millidge2021

Authenticity: verified.

Fresh publisher-deposited Crossref verifies title, three authors/order, Neural Computation33(2),447–482, February2021. arXiv2020 is preprint date only.

Publisher-deposited full abstract explicitly distinguishes EFE from future VFE, says naive extension discourages exploration, and introduces FEEF.

Checked primary records:

- https://api.crossref.org/works/10.1162/neco_a_01354
- https://arxiv.org/abs/2004.08128

Manuscript uses:

- L151: Distinguishes EFE from naive future VFE and proposes FEEF. Verdict: supported.

Access/provenance notes:

- MIT direct article open gave403. Crossref includes full publisher-deposited abstract and complete metadata; arXiv independently authenticates content.

## oudeyer2007

Authenticity: verified.

Official full text confirms title, Pierre-Yves Oudeyer/Frederic Kaplan, Frontiers in Neurorobotics1:6, November2,2007.

Abstract and formal typology classify intrinsic-motivation mechanisms. It predates VIME(2016), Pathak(2017), and RND(2019), so cannot literally survey those named methods.

Checked primary records:

- https://www.frontiersin.org/journals/neurorobotics/articles/10.3389/neuro.12.006.2007/full

Manuscript uses:

- L156: Oudeyer and Kaplan provide an earlier typology of computational intrinsic motivation. Verdict: supported_after_revision.

Findings:

- Use: Oudeyer and Kaplan (2007) provide an earlier typology of computational intrinsic motivation. This preserves the legitimate citation without implying coverage of later algorithms. Status: resolved_and_independently_rechecked_2026-10-21.

## parr2019

Authenticity: verified.

Publisher full text/Crossref verify title, Thomas Parr/Karl J.Friston, Biological Cybernetics113(5–6),495–513,2019.

Equation(10) decomposes EFE into epistemic/extrinsic terms; introduction and discussion distinguish generalized free energy with explicit future-outcome beliefs from expected free energy. The manuscript’s limited equivalence claim is correctly separated.

Checked primary records:

- https://link.springer.com/article/10.1007/s00422-019-00805-w
- https://link.springer.com/content/pdf/10.1007/s00422-019-00805-w.pdf
- https://api.crossref.org/works/10.1007/s00422-019-00805-w

Manuscript uses:

- L122: EFE combines pragmatic value and expected information gain. Verdict: supported.
- L149: EFE combines pragmatic and epistemic terms. Verdict: supported.
- L151: Generalized free energy is a distinct functional. Verdict: supported.

## parr2022

Authenticity: verified.

Official publisher verifies exact title/subtitle, Thomas Parr/Giovanni Pezzulo/Karl J.Friston order, MITPress, March29,2022. New paperback2025 does not alter first edition year.

Publisher description characterizes perception, planning and action as probabilistic inference under free-energy minimization; sufficient for broad introductory use.

Checked primary records:

- https://mitpress.mit.edu/9780262045353/active-inference/

Manuscript uses:

- L149: Active inference casts perception and action as variational inference. Verdict: supported.

## pathak2017

Authenticity: verified.

Official PMLR record confirms title, Deepak Pathak/Pulkit Agrawal/Alexei A.Efros/Trevor Darrell order, ICML2017. Optional omitted pages2778–2787.

Abstract describes curiosity as intrinsic reward from learned prediction error. Supports placement among exploration-bonus methods.

Checked primary records:

- https://proceedings.mlr.press/v70/pathak17a.html

Manuscript uses:

- L156: Curiosity-based exploration uses intrinsic reward bonuses. Verdict: supported.

## pineau2003

Authenticity: verified.

CMU institutional record verifies exact title, Joelle Pineau/Geoffrey Gordon/Sebastian Thrun, IJCAI2003.

Abstract describes approximating value iteration on representative belief points chosen with stochastic trajectories.

Checked primary records:

- https://publications.ri.cmu.edu/point-based-value-iteration-an-anytime-algorithm-for-pomdps

Manuscript uses:

- L135: PBVI approximates value functions on reachable beliefs. Verdict: supported.

## rawlik2012

Authenticity: verified.

Official RSS record verifies title, Konrad Rawlik/Marc Toussaint/Sethu Vijayakumar, RSS2012. Edinburgh confirms2012 conference version; later2013 IJCAI version exists but does not make this entry false.

Institutional abstract directly formulates stochastic optimal control as KL-divergence minimization and describes approximate inference and model-free algorithms.

Checked primary records:

- https://www.roboticsproceedings.org/rss08/p45.html
- https://www.research.ed.ac.uk/en/publications/on-stochastic-optimal-control-and-reinforcement-learning-by-appro/

Manuscript uses:

- L156: KL-minimizing control is an algorithmic control-as-inference instance. Verdict: supported.

## robbins1951

Authenticity: verified.

Crossref and university-hosted original journal scan confirm exact title, Herbert Robbins/Sutton Monro, Annals of Mathematical Statistics22(3),400–407, September1951.

Original §3 eq.(7) is the stochastic root-finding recursion with target minus response. It establishes convergence in probability/quadratic mean under its assumptions. Manuscript separately attributes later almost-sure/constrained extensions and supplies its own proof, so it does not overclaim original result.

Checked primary records:

- https://api.crossref.org/works/10.1214/aoms/1177729586
- https://www.columbia.edu/~ww2040/8100F16/RM51.pdf

Manuscript uses:

- L447: Controller is a projected Robbins–Monro recursion. Verdict: supported.
- L1263: Checklist cites Robbins–Monro as a nontrivial theoretical tool. Verdict: supported.

Access/provenance notes:

- Euclid/JSTOR direct text blocked; original journal scan on Columbia site successfully read.

## russo2014

Authenticity: verified.

Official NIPS2014 record verifies exact title and Daniel Russo/Benjamin VanRoy author order.

Abstract defines the ratio of squared expected single-period regret to mutual information about the optimal action, not plain regret/information ratio. Follow-up: fresh arXiv abstract independently confirms the edited squared-expected-regret/information formulation; selecting an action distribution is the correct IDS minimization domain.

Checked primary records:

- https://proceedings.neurips.cc/paper_files/paper/2014/hash/90720a2fcc41f9332e6a1558da327089-Abstract.html
- https://arxiv.org/abs/1403.5556

Manuscript uses:

- L146: IDS selects an action distribution minimizing squared expected one-period regret divided by expected information gain about the optimal action. Verdict: supported_after_revision.

Findings:

- State that IDS minimizes the ratio of squared expected single-period regret to expected information gain. Status: resolved_and_independently_rechecked_2026-10-21.
