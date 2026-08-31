export const meta = {
  name: 'jair-panel-round-13',
  description: 'Round-13 JAIR panel testing for unqualified accept: 5 expert reviewers, skeptic verification, AE adjudication',
  phases: [
    { title: 'Review', detail: 'five expertise-differentiated reviewers, claims verified against CSVs and code' },
    { title: 'Verify', detail: 'adversarial skeptic per required-change finding' },
    { title: 'Adjudicate', detail: 'associate editor decides accept vs accept-with-minor-revisions' },
  ],
}

const REPO = '/Users/pat/code/rho_aif'
const MS = `${REPO}/paper/full_paper_jair.tex`

const COMMON = `
You are reviewing a journal submission for JAIR (Journal of Artificial Intelligence Research).
Manuscript: ${MS} (read it in full; it is long, read it in chunks).
Repository: ${REPO} — results CSVs in results/, experiment producers in experiments/, package in rho_aif/, tests in tests/.

Context you may use but must not defer to: this manuscript has been through twelve prior five-reviewer panels,
six exhaustive class sweeps, and a sweep verifying every claim about cited prior work against fetched sources. All
findings are fixed. Since round 12:
- Section 3.1's formal definition of a rho-POMDP now carries the action argument, rho : Delta(S) x A -> R with
  Equation 1 as R(s,a) + rho(b,a), matching Related Work, Proposition 1, Table tab:agents and the Appendix A proof.
  Previously the only formal definition could not express rho_EFE, which returns I_a(b) for an observation action
  and 0 for a commit action at the same belief.
- The Proposition 3 scope paragraph no longer justifies excluding the sample action by saying it changes the
  rock-state vector, which this variant does not do.
- The reproducibility checklist's RockSample deviation list now matches the corrected Section 6 enumeration.
- "An agent cannot buy less sensing than reward alone motivates" is scoped to the two monotone instances, since
  RS[5,3] dips to 3.00 observations at w=0.316 against 3.70 at w=0.
- The w-beyond-1 accuracy and reward numbers are attributed to w=50 rather than to the whole sweep.
- Corollary PI-4's "jumps at w_thresh and nowhere else" is scoped to the H=1 decision.
- A Related Work forward pointer claiming the appendices "demonstrate the benefit" of closed-form information
  valuation is hedged to match what those sections actually conclude.

AUTHOR CERTIFICATION, which you should accept: the load-bearing contributions, namely the EFE / rho-POMDP
equivalence at w=1 and the Price of Information framing of w as the shadow price of a sensing budget, are certified
novel by the author. Do not re-litigate whether those ideas are new. You SHOULD still flag any specific claim that
a cited source contradicts, and any place where the manuscript overstates what its own results establish.

Weight your effort toward whether each argument follows from its evidence, whether every proposition's proof
supports exactly its statement, whether the abstract and contributions promise what the results deliver, whether
limitations are complete and honestly scoped, and whether distant passages disagree in substance. Read for
mechanical damage too: duplicated or garbled text, leaked editorial instructions, dangling references, and case
splits that do not partition. Prior rounds' verdicts are not evidence.

VERDICT SEMANTICS — read carefully, this is the point of the round:
- "accept" means: you found NO defect that requires a change before publication. Optional suggestions,
  matters of taste, and improvements you would merely prefer do NOT block accept — report them as severity
  "suggestion" and still return accept if nothing requires change.
- "accept-with-minor-revisions" means: you found at least one concrete defect that genuinely REQUIRES a change
  (a wrong number, a claim an artifact contradicts, a statement a proof does not support, a dangling pointer,
  a violation of the paper's own stated conventions). Every such finding must carry severity "required" with
  the exact file location and the artifact that contradicts it.
- Do not inflate taste into requirements, and do not suppress real defects to be agreeable. Both directions
  are failures. A "required" finding you cannot back with a file-level check is a failure of your review.

Scrutinize hardest the reasoning layer and the passages changed since round 8 (listed above), since this project
has a measured history of fix passes introducing new defects, most recently a corollary hypothesis that mishandled
a knife-edge case and an over-corrected claim that denied a ranking the data supports.
Also still worth a pass:Also still worth a pass:Also still worth a pass, from earlier discharges:Also still worth a pass, from earlier discharges:
- Every \Description block in the JAIR file (14 of 21 were rewritten against figures/ PNGs and results/ CSVs).
- tab:transfer (rows, caption, and the Zero-shot weight transfer paragraph), tab:ids (rows and caption), both
  rewritten from the freshly rerun results_transfer.csv and results_ids.csv at the Planning+IG-class weights
  (Tiger 50, Diagnosis 50, Bandit 20, Testbed 10 from results_supplementary_tuned_weights.csv).
- The bolding-rule sentences newly added to the captions of the app:full_tables Tiger table, the Testbed
  appendix table, tab:inspection, the app:scaling table, and tab:transfer, and the cells they govern.
- The misspecification prose (tested range now stated as -0.15 to +0.10), the staircase-monotonicity sentences
  (now Bandit and Tileworld), the Tileworld 8x8 row of the env-spec table (6 scans), and results_thresholds.csv
  (Tileworld w_ret now 20).
Also still worth a pass, from the round-3 discharge:
- Proposition 2 (label prop:nearopt, ~lines 190-215): fully restated sign-conditionally this week. Check the
  statement against its own proof sketch, and against Table tab:alpha_eta and Section 6.2 / Corollary 4.
- The Epistemic-only passage in the Agents section (~line 337): rescoped this week; check against
  results/results_summary.csv and the per-environment CSVs.
- app:rocksample: the sensitivity-battery leaf comparison sentence, the RS[11,11] horizon paragraph
  (check its p-bound against results/results_rocksample_pomcp_horizon_11x11_stats.csv), the budget-sweep
  non-monotonicity sentence (results/results_rocksample_pomcp_budget.csv), and the depth-provenance sentence
  in app:envs (~line 1173) against experiments/run_rocksample.py.
- The Discussion's Tileworld threshold sentence and nat/bit exception sentence (~lines 833-836) against
  results/results_tileworld_scaling.csv and the Pareto sweep data.
- The obs-scaling caption, prose, and alt-text (app:obs_scaling) against results/results_showcase_obs_scaling.csv.
- The CPOMDP reference's conservatism discussion (~lines 441 and 775), Prop PI-5's hypothesis (~line 427),
  the TOST orders-of-magnitude sentence (~line 768) against results/results_tost_sarsop*.csv,
  tab:misspec-diag against results/results_model_misspec.csv, the Thompson SE cells (~lines 948/968) against
  results/results_tiger.csv and results_diagnosis_n4.csv, the effect-size table (~line 1294), the
  reproducibility checklist item on CSV columns (~line 1646), the asymmetry-sweep agent naming (~lines 1101/1106),
  the audit table caption convention (paper/tables/audit_case_study.tex), and the regenerated RockSample table
  captions (paper/tables/rocksample_main.tex, rocksample_extended.tex).

House conventions the manuscript binds itself to (violations are "required" findings):
- Seed-level Welch tests on per-seed means primary; pooled episode-level SE appendix-only; Holm-Bonferroni
  corrected within metric where stated; never seed-level Cohen's d at n=5; equivalence claims need TOST with
  predeclared margins, otherwise "within sampling error" / "not significantly different".
- Calibration vocabulary: "near-optimal/estimated" never "exact" for SARSOP/CPOMDP; "exercises" not "validates";
  shadow prices as crossing brackets, never points at gap budgets.
- Writing style in prose: no em dashes, no prose colons or semicolons, no rhetorical italics/bold.
- Every number traces to a committed CSV with exactly one producer script.

VERIFY, do not trust: for every quantitative claim you rely on or challenge, open the CSV or code and check the
number. Sample broadly across sections, not only the listed sites. Report which files you actually opened.

Return STRICT verdict: accept / accept-with-minor-revisions / major-revisions / reject-resubmission-encouraged /
reject, under the semantics above.
`

const REVIEWERS = [
  { key: 'pomdp', id: 'You are a senior researcher in POMDP planning (SARSOP, POMCP, belief-space search). You know Smith & Simmons RockSample, Silver & Veness POMCP, and point-based solvers cold. Focus: the RockSample and POMCP content, baseline fairness, tree-search claims, the Flat-MC/POMCP distinction, horizon and budget sweeps.' },
  { key: 'actinf', id: 'You are an active inference researcher (Friston, Parr, Da Costa lineage). You know EFE decompositions, epistemic value debates, and the sophisticated-inference Bellman results. Focus: Props 1-3 and their proofs, the w=1 equivalence scope, the variational-objective framing, factored-observation extension, destructive-sensing Remark, related-work fairness to active inference.' },
  { key: 'theory', id: 'You are a decision-theory and constrained-MDP theorist. Focus: every proposition against its proof, especially the freshly restated Proposition 2 (re-derive its thresholds and sign conditions yourself), the Price of Information formalism (Definition PI-3, Props PI-1/PI-2/PI-5, Corollary PI-4), shadow-price bracket semantics against rho_aif/budget.py, scale equivariance, the Lagrangian duality scoping, and whether any statement asserts more than its proof shows.' },
  { key: 'stats', id: 'You are an empirical-methodology and statistics referee. Focus: every statistical claim. Seed-level vs pooled SE usage, Welch tests, per-metric Holm families (check the producer code actually does what the prose says), TOST margins, bolding rules in tables, and the sign and magnitude of every p-value, SE, and effect size quoted in prose against its CSV. Sample at least 30 quantitative prose claims across different sections and verify each against its CSV.' },
  { key: 'generalist', id: 'You are a senior AI generalist and former journal editor. Focus: narrative coherence, whether abstract/intro/contributions match what the results deliver, limitations honesty, claim calibration, internal contradictions between distant passages, reproducibility checklist accuracy, and overall JAIR fit (originality and significance).' },
]

const FINDINGS_SCHEMA = {
  type: 'object', required: ['verdict', 'findings', 'files_opened'],
  properties: {
    verdict: { type: 'string', enum: ['accept', 'accept-with-minor-revisions', 'major-revisions', 'reject-resubmission-encouraged', 'reject'] },
    summary: { type: 'string' },
    files_opened: { type: 'array', items: { type: 'string' } },
    findings: { type: 'array', items: {
      type: 'object', required: ['severity', 'claim', 'evidence', 'location'],
      properties: {
        severity: { type: 'string', enum: ['required', 'suggestion'] },
        claim: { type: 'string' },
        evidence: { type: 'string' },
        location: { type: 'string' },
        suggested_fix: { type: 'string' },
      } } },
  },
}

const VERDICT_SCHEMA = {
  type: 'object', required: ['is_real', 'reasoning'],
  properties: { is_real: { type: 'boolean' }, reasoning: { type: 'string' }, corrected_understanding: { type: 'string' } },
}

log('Round 13: launching five reviewers under unqualified-accept semantics')
const reviews = await parallel(REVIEWERS.map(r => () =>
  agent(`${r.id}\n${COMMON}`, { label: `review:${r.key}`, phase: 'Review', schema: FINDINGS_SCHEMA, effort: 'max' })
))

const valid = reviews.filter(Boolean)
const required = valid.flatMap((r, i) => (r.findings || [])
  .filter(f => f.severity === 'required')
  .map(f => ({ ...f, reviewer: REVIEWERS[i] ? REVIEWERS[i].key : `r${i}` })))
log(`${valid.length}/5 reviews in; ${required.length} required-change findings to verify`)

const verified = await parallel(required.map(f => () =>
  agent(`You are an adversarial skeptic. A reviewer of the manuscript ${MS} (repo ${REPO}) claims this defect REQUIRES a change before publication:\n\nCLAIM: ${f.claim}\nEVIDENCE OFFERED: ${f.evidence}\nLOCATION: ${f.location}\n\nTry to REFUTE it. Open the actual manuscript text at that location, the CSVs, and the producer code. The reviewer may have misread the file, used a stale line number, misunderstood a convention (seed-level vs pooled SE, per-metric Holm families, bracket semantics, the observe-then-transition timing convention), or inflated a taste preference into a requirement. A finding is real only if the manuscript genuinely needs a change: a wrong number, a contradicted claim, an unsupported statement, a dangling pointer, or a convention violation. Default to is_real=false unless the defect survives your direct file-level check. Report exactly what you opened and what it said.`,
    { label: `verify:${f.reviewer}`, phase: 'Verify', schema: VERDICT_SCHEMA, effort: 'max' })
    .then(v => ({ ...f, verified: v }))
))

const confirmed = verified.filter(Boolean).filter(f => f.verified && f.verified.is_real)
log(`${confirmed.length}/${required.length} required findings survive skeptic verification`)

const ae = await agent(`You are the Associate Editor for JAIR handling this submission (manuscript ${MS}, repo ${REPO}).
This is round 13. Rounds 1-3 were unanimous accept-with-minor-revisions and all their conditions are discharged.
The question this round decides: UNQUALIFIED ACCEPT (publishable as is, zero required changes) or
accept-with-minor-revisions (enumerate the required changes). Five reviews and the skeptic-verified
required-change findings are below. Adjudicate against the manuscript itself; re-check personally any finding
you rely on; refuted findings are demoted to noise unless you personally re-verify and disagree with the skeptic
(say so explicitly if you do). Do not average verdicts, and do not give accept as a courtesy: give it only if,
after your own checks, no required change remains. Suggestions (non-blocking) may be listed separately.

REVIEWS:\n${JSON.stringify(valid, null, 1)}\n\nVERIFIED REQUIRED FINDINGS:\n${JSON.stringify(verified.filter(Boolean), null, 1)}\n
Return: your decision, the list of required changes if any (concrete and checkable, deduplicated), a separate
list of non-blocking suggestions worth passing to the authors, and an assessment of whether a further
fix-and-review iteration could plausibly reach unqualified accept or whether the panel will always find
something (be honest about this asymptote).`,
  { label: 'associate-editor', phase: 'Adjudicate', effort: 'max' })

return {
  verdicts: valid.map((r, i) => ({ reviewer: REVIEWERS[i] ? REVIEWERS[i].key : `r${i}`, verdict: r.verdict, required: (r.findings || []).filter(f => f.severity === 'required').length, suggestions: (r.findings || []).filter(f => f.severity === 'suggestion').length })),
  confirmed_required: confirmed,
  refuted_required: verified.filter(Boolean).filter(f => f.verified && !f.verified.is_real).map(f => ({ reviewer: f.reviewer, claim: f.claim, why_refuted: f.verified.reasoning })),
  ae_decision: ae,
}
