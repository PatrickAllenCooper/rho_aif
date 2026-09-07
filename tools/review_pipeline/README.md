# Review pipeline tooling

Working tools and records from the multi-round referee-simulation loop and
the manuscript's citation/claim verification passes. Kept in the repository
deliberately, as part of this project's provenance discipline: every claim
in the paper traces to a script and a CSV, and every fix to the paper
traces to a check that found it.

- **`verify_claims.py`** — mechanical pre-check run before staging any
  manuscript prose that adds numbers, references, or CSV citations. See
  its module docstring and `CLAUDE.md`'s "Mechanical claim verification"
  section for what it checks and why it's scoped the way it is.
  Validated in `tests/test_verify_claims.py`, including a retroactive
  replay against the exact commit that introduced the defect it exists to
  catch.
- **`safe_apply.py`** — guarded string-replacement helper for applying
  reviewer-suggested prose fixes across both manuscript masters at once.
  Refuses non-idempotent replacements, instruction-shaped replacement
  text, and post-checks for duplicate sentences, comma stutters, and
  whitespace lost at a splice point.
- **`panel_template.js`** — a `Workflow`-tool script template for running
  an expertise-differentiated reviewer panel (POMDP planning, active
  inference, decision theory, statistics, generalist) with adversarial
  skeptic verification and AE adjudication, under unqualified-accept
  semantics. Later review rounds in the ledger (`Guidance_Documents/`)
  are variants of this template.
- **`figure_audit_2026-08-30.json`**, **`round13_raw_findings_UNVERIFIED.json`**
  — raw output from two review rounds, kept for provenance. The
  `UNVERIFIED` suffix is load-bearing: these are a reviewer's raw claims
  before adversarial verification, not a record of confirmed defects.
  The verified, disposed record for every round is in
  `Guidance_Documents/full_paper_plan.md`.
