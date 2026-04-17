# Niobe — Zero-Ambiguity Build Spec
## Population Research Orchestrator — Engineering Specification

**Date:** 2026-04-14
**Status:** Final. Build-ready. No more design documents after this.
**Posture:** You are an engineer. Start coding.
**Dependency:** PopScale engine (Week 3 analytics schema must be stable before Niobe v1 build begins)

---

## 1. Architecture Decision: Claude Code Skill System

**Decision: Claude Code skill. Same as Morpheus. Not a web app. Not a hybrid.**

Niobe is implemented as a Claude Code skill at `~/.claude/skills/simulatte-niobe/SKILL.md`. It reads and writes files in a study directory. The "UX" is the Claude Code conversation interface. The "state management" is a JSON file. The "database" is the filesystem.

**Why this and not a web app or API wrapper:**

1. Morpheus works this way. The researcher is already trained on the skill-based interaction model. Introducing a different interface for population research creates cognitive switching cost for zero research quality improvement.

2. The user base is one person. A web frontend for population research would require: a queue management UI for simulation runs, a distribution chart renderer, an interactive segment explorer. All of these are future capabilities. v1 needs the orchestration logic, not the chrome.

3. PopScale already has its own API (Week 10). Niobe doesn't need to re-expose PopScale's capabilities through another API. It calls PopScale's Python functions directly.

**What this means for PopScale invocation:**

Niobe calls PopScale by importing its Python modules directly:

```python
from popscale.orchestrator.runner import run_population_scenario
from popscale.analytics.report import generate_report
from popscale.calibration.calibrator import calibrate
from popscale.calibration.population_spec import PopulationSpec
from popscale.scenario.model import Scenario, SimulationDomain
```

These calls happen within the skill's tool execution context. The skill describes the call, the tool makes it, the result is captured and presented to the researcher.

**What this means for study directories:**

Each Niobe study creates a directory under the project's Case Studies path:

```
/Users/admin/Documents/Simulatte Projects/Case Studies/{client}/niobe/
├── study_state.json
├── population_brief.md
├── population_spec.json
├── hypothesis_register.md
├── scenario_designs.md
├── ...
```

This mirrors Morpheus's project directory convention. A client may have both Morpheus studies and Niobe studies.

---

## 2. Study State Schema (Exact, Final)

The full schema is specified in V1_SYSTEM_DEFINITION.md Section 11. This section documents the operational details: initialization, validation, transition rules.

### Initialization

When the researcher invokes `niobe stage1`:

```json
{
  "study_id": "NIOBE_{YYYYMMDD}_{study_slug}",
  "created_at": "ISO8601",
  "updated_at": "ISO8601",
  "current_stage": "intake",
  "source": "direct",
  "source_ref": null,
  "population_brief": { "id": "PB_001", "file": "population_brief.md", "status": "draft" },
  "population_spec": { "id": "PSPEC_001", "file": "population_spec.json", "status": "draft" },
  "hypotheses": { "status": "not_started", "entries": [] },
  "scenario_designs": { "status": "not_started", "entries": [] },
  "population_runs": [],
  "findings": { "status": "not_started", "entries": [] },
  "tandem": { "segment_briefs_generated": [], "hypothesis_list_received": null },
  "deliverable": { "status": "not_started" },
  "stage_gates": {
    "brief_approved": false, "spec_approved": false,
    "hypotheses_approved": false, "scenarios_approved": false,
    "runs_confirmed": false, "findings_approved": false,
    "deliverable_approved": false
  }
}
```

When the source is a Morpheus handoff (`niobe stage1 --from-morpheus {hypothesis_list.json}`):

```json
{
  "source": "morpheus_handoff",
  "source_ref": "PRJ_20260414_khidma"
}
```

The Hypothesis List from Morpheus is read at Stage 1 and used to pre-populate the business question and suggested hypotheses. The researcher still reviews and approves everything.

### Validation Rules

1. `study_id` format: `NIOBE_{YYYYMMDD}_{slug}` — slug is lowercase, alphanumeric + underscores only
2. `current_stage` must be one of: `intake`, `scenario_design`, `simulation`, `synthesis`, `deliverable`
3. `domain` must be one of: `CONSUMER`, `POLICY`, `POLITICAL`
4. Every `scenario_design.entry` must reference at least one `hypotheses.entry`
5. Every `population_run` must reference a `scenario_design.entry` with status `approved`
6. `stage_gates` values are boolean, set only by the orchestrator on researcher approval
7. `population_spec.n_personas` must be a positive integer
8. `population_spec.state` must be a value from the supported geography list (see Contract 1 geography table) — PopScale validates this internally on `run_niobe_study()`

### Transition Rules

```
intake → scenario_design     requires: brief_approved AND spec_approved
scenario_design → simulation requires: hypotheses_approved AND scenarios_approved
simulation → synthesis       requires: runs_confirmed
synthesis → deliverable      requires: findings_approved
```

**No backwards transitions.** If the researcher needs to amend an upstream artifact:
1. The artifact is edited in-place
2. `updated_at` is refreshed
3. All downstream artifacts that reference the edited artifact are flagged `upstream_amended`
4. The current stage does not revert — the researcher decides whether downstream artifacts need regeneration

---

## 3. Stage Execution Flows (Exact)

### Stage 1: Population Intake

```
TRIGGER: Researcher invokes `niobe stage1`
         OR `niobe stage1 --from-morpheus {hypothesis_list.json}`

STEP 1 — INGEST
  If direct: ask researcher for business question, target population, 
             geographic scope, domain
  If from Morpheus: read hypothesis_list.json, extract source_study context,
                    pre-populate business question from directional findings
  Save business question to population_brief.md (draft)
  Create study_state.json

STEP 2 — GENERATE POPULATION BRIEF
  Run Population Intake module:
    Input: business question, target population, domain, geographic scope
    Output: 
      - Decision context (what the business is trying to decide)
      - Study objectives (3-7 testable population-level questions)
      - Target population definition (who is being simulated)
      - Market size estimate (with source: census / estimate / unknown)
  Save to population_brief.md

STEP 3 — GENERATE POPULATION SPEC
  Niobe constructs the NiobeStudyRequest parameters from the brief:
    - state: mapped from geographic scope (India state, united_kingdom, 
             united_states, france, etc.)
    - n_personas: recommended based on study scope (default 2,000)
    - domain: CONSUMER / POLICY / POLITICAL
    - environment_preset: selected from available presets for the geography
    - stratify_by_religion: true for India domains; ignored elsewhere
    - stratify_by_income: true for all domains
    - sarvam_enabled: true for India states only
    - tier: VOLUME default; SIGNAL for high-confidence hypotheses

  Niobe generates a human-readable description of the planned population
  from these parameters — it does NOT call PopScale internals to preview.
  The spec description is constructed from Niobe's own knowledge of what
  the parameters produce:
    "2,000 synthetic agents representing [geography], stratified by 
     [dimensions], calibrated against [source]. Religion stratification 
     [applies / does not apply — income stratification used instead]."

  Save parameters to population_spec.json
  (PopScale resolves these into actual persona segments at Stage 3 runtime)

STEP 4 — CRITIQUE
  Run Research Critic (SEPARATE TOOL CALL):
    Input: population_brief.md + population_spec.json ONLY
    Criteria:
      1. Is the population spec representative of the stated target population?
      2. Is any major demographic segment missing from stratification?
      3. Are the study objectives answerable at population scale?
      4. Is the market size estimate sourced or assumed?
      5. Is the n_personas sufficient for the number of study objectives?
    Output: critique annotations
  Save to critic_brief.md

STEP 5 — PRESENT
  Display to researcher:
    - Population Brief (decision context, objectives, target population)
    - Population Spec (demographic breakdown table)
    - Critic annotations
  Ask: "Review the population brief and spec. Approve when ready."

STEP 6 — GATE
  On approval:
    population_brief.status → "approved"
    population_spec.status → "approved"
    stage_gates.brief_approved → true
    stage_gates.spec_approved → true
    current_stage → "scenario_design"
```

---

### Stage 2: Hypothesis & Scenario Design

```
TRIGGER: Researcher invokes `niobe stage2`

PRE-CHECK: brief_approved AND spec_approved must be true

STEP 1 — LOAD
  Read study_state.json
  Load population_brief.md
  Load population_spec.json

STEP 2 — GENERATE DISTRIBUTIONAL HYPOTHESES
  Run Hypothesis Designer module:
    Input: study objectives + target population + domain
    If from Morpheus handoff: also include directional findings as seeding context
    Output: distributional hypotheses with types and expected ranges
  Rules enforced:
    - Every hypothesis must link to ≥1 study objective
    - Every study objective must have ≥1 hypothesis
    - Each hypothesis must have a type (prevalence / distribution / cross_tab / 
      comparative / issue_salience / message_test)
    - Each hypothesis must have an expected_range (numeric bounds that define 
      confirmation vs refutation)
    - UNCOVERED objectives are flagged
  Save to hypothesis_register.md

STEP 3 — GENERATE SCENARIO DESIGNS
  For each hypothesis, generate a matching PopScale Scenario:
    - Map hypothesis type → scenario type (see mapping table below)
    - Generate scenario question, context, options (from domain + brief)
    - Set domain framing (CONSUMER / POLICY / POLITICAL)
    - Determine run order (independent scenarios can run in any order;
      comparative scenarios must run in sequence)
    - Select tier: VOLUME for standard (cost-efficient), SIGNAL for 
      high-confidence hypotheses, DEEP only if N < 50
    - Generate expected_if_confirmed and expected_if_disconfirmed 
      (forces the researcher to think about what the distribution means)
  Save to scenario_designs.md

  HYPOTHESIS TYPE → SCENARIO TYPE MAPPING:
  ┌─────────────────────┬───────────────────────────────────┐
  │ prevalence          │ Binary choice or concept test     │
  │ distribution        │ Van Westendorp / Likert scale     │
  │ cross_tab           │ Same scenario, segmented sub-pops │
  │ comparative         │ A/B scenario variants             │
  │ issue_salience      │ MaxDiff ranking or priority sort  │
  │ message_test        │ 2-4 concept variants              │
  └─────────────────────┴───────────────────────────────────┘

STEP 4 — COST ESTIMATION
  For each scenario design, estimate simulation cost:
    Call: estimate_simulation_cost(
      count=population_spec.n_personas,
      tier=scenario.tier,
      n_stimuli=1
    )
  Display total study cost estimate:
    - Per-scenario cost breakdown
    - Total estimated cost
    - Total estimated time
  
STEP 5 — CRITIQUE
  Run Research Critic (SEPARATE TOOL CALL):
    Input: hypothesis_register.md + scenario_designs.md ONLY
    Criteria:
      1. Are any hypotheses untestable with the chosen scenario type?
      2. Are any expected ranges implausibly narrow (<5pp) or wide (>50pp)?
      3. Is any scenario language leading (biasing toward an option)?
      4. Is the scenario sequence biased (order creates priming)?
      5. Swap test: would this scenario produce the same result for a 
         different business question?
      6. Are any cross-tab hypotheses based on sub-samples that will be 
         too small after stratification?

STEP 6 — PRESENT
  Display to researcher:
    - Hypothesis register (all hypotheses with types and expected ranges)
    - Scenario designs (each scenario with question, options, domain framing)
    - Cost estimation summary
    - Critic annotations
  Ask: "Review hypotheses and scenario designs. Approve when ready."

STEP 7 — GATE
  On approval:
    hypotheses.status → "approved"
    scenario_designs.status → "approved"
    stage_gates.hypotheses_approved → true
    stage_gates.scenarios_approved → true
    current_stage → "simulation"
```

---

### Stage 3: Population Simulation

```
TRIGGER: Researcher invokes `niobe stage3`

PRE-CHECK: hypotheses_approved AND scenarios_approved must be true

STEP 1 — LOAD
  Read study_state.json
  Load population_spec.json
  Load scenario_designs.md

STEP 2 — BUILD NIOBE STUDY REQUEST
  Assemble NiobeStudyRequest from approved artifacts:
    state:              population_spec.state
    n_personas:         population_spec.n_personas
    domain:             population_spec.domain
    business_problem:   population_brief.decision_context
    scenarios:          [Scenario objects built from each scenario_design]
    environment_preset: population_spec.environment_preset
    stratify_by_religion: population_spec.stratify_by_religion
    stratify_by_income:   population_spec.stratify_by_income
    sarvam_enabled:       population_spec.sarvam_enabled
    tier:               scenario_design.tier (or VOLUME default)
    budget_cap_usd:     sum of per-scenario budget caps

STEP 3 — PRE-RUN CHECK
  Display expected run parameters to researcher:
    "Ready to run {N} scenarios against {M} synthetic agents.
     Geography: {state}. Domain: {domain}.
     Tier: {tier}. Budget cap: ${budget_cap}.
     Proceed?"
  On researcher confirmation → proceed
  On researcher decline → pause, allow modifications

STEP 4 — EXECUTE
  Call (async):
    study_result: StudyResult = await run_niobe_study(request)
  
  All persona generation, calibration, demographic sampling, cognitive
  simulation, analytics, and caching happen inside PopScale/PG.
  Niobe receives a single StudyResult.

  While executing, display streaming progress as StudyResult emits it.
  Do not attempt to interpret partial results — wait for completion.

STEP 5 — RECEIVE AND SAVE RESULTS
  Wrap StudyResult in NiobeStudyReport:
    study_report = NiobeStudyReport(
        study_id=study_state.study_id,
        study_result=study_result
    )
  Save study_result to reports/study_result.json
  
  Update study_state population_runs:
    For each scenario in the result:
      Add population_run entry:
        n_personas:   study_result.cohort_size
        success_rate: study_result.success_rate
        cost_usd:     study_result.cost_actual_usd
        duration:     study_result.duration_seconds

STEP 6 — RUN QUALITY REVIEW
  Display summary from StudyResult:
    - Total personas simulated
    - Success rate (successful / total)
    - Total cost
    - Total time
    - Any circuit breaker events surfaced by PopScale
  
  If success_rate < 90%:
    WARN: "Success rate below 90%. {fallback_count} personas used 
           fallback responses. Review before proceeding."
  
  Ask: "Review run quality. Confirm to proceed to synthesis, 
        or re-run?"
  On re-run: rebuild NiobeStudyRequest and return to STEP 4

STEP 7 — GATE
  On confirmation:
    stage_gates.runs_confirmed → true
    current_stage → "synthesis"
```

---

### Stage 4: Population Synthesis

```
TRIGGER: Researcher invokes `niobe stage4`

PRE-CHECK: runs_confirmed must be true

STEP 1 — LOAD
  Read study_state.json
  Load all PopScaleReport files from reports/
  Load hypothesis_register.md
  Load population_brief.md

STEP 2 — GENERATE FINDINGS (per hypothesis)
  For each distributional hypothesis:
    a. Load the PopScaleReport from the matching run
    b. Extract relevant analytics:
       - Segmentation: segment labels, sizes, trait profiles
       - Distribution: option proportions with confidence intervals
       - Drivers: ranked effect sizes
       - Surprises: deviations from naive prior
    c. Generate finding narrative:

       FINDING TEMPLATE:
       """
       FINDING {PF_ID}: {headline}
       
       HYPOTHESIS: {DH_ID} — {hypothesis statement}
       VERDICT: CONFIRMED / PARTIALLY CONFIRMED / REFUTED
       CONFIDENCE: {CI range}
       
       WHAT THE DATA SHOWS:
       {Distribution narrative — what proportions, what spread, what 
        concentration}
       
       WHAT DRIVES IT:
       {Driver narrative — which attributes predict this outcome, 
        effect sizes, what it means for the business question}
       
       WHAT'S SURPRISING:
       {Surprise narrative — if any deviation from naive prior exceeded 
        15pp, what it means}
       
       WHAT THIS MEANS FOR {business_question}:
       {Actionable interpretation — not a recommendation, but a clear 
        statement of what the finding implies for the decision the 
        client is trying to make}
       """

STEP 3 — GENERATE CROSS-SCENARIO FINDINGS
  If the study includes sequential or comparative scenarios:
    Compare distributions across runs:
    - Delta analysis: what changed between scenario A and scenario B?
    - Segment-level shifts: which segments moved most?
    - Cross-scenario narrative: what the sequence reveals

STEP 4 — IDENTIFY TANDEM CANDIDATES
  For each finding that identifies a distinct segment (finding_type = "segment"):
    Evaluate: does this segment warrant depth investigation?
    Criteria:
      - Segment is >15% of population (large enough to matter)
      - Segment's behavior is surprising or unexplained by demographics alone
      - The "why" behind the segment's behavior is not answered by the 
        distributional data
    If yes: propose tandem recommendation
      "Segment [{label}] ({size}% of population) warrants depth investigation 
       via Morpheus. This segment {behavior_summary}. The distributional data 
       shows WHAT they do but not WHY. Morpheus can answer: {deep_question}."

STEP 5 — CRITIQUE
  Run Research Critic (SEPARATE TOOL CALL):
    Input: population_findings.md ONLY
    Criteria:
      1. Does any finding claim more precision than the CI supports?
      2. Are any cross-tab findings based on sub-samples < 30?
      3. Are any surprise findings artifacts of the naive prior (bad 
         baseline), not genuine deviations?
      4. Are the tandem recommendations substantiated by the data?
      5. Is any finding stating a causal claim when the data only 
         supports correlation?

STEP 6 — PRESENT
  Display:
    - All findings (per hypothesis + cross-scenario)
    - Tandem recommendations
    - Critic annotations
  Ask: "Review findings. Approve, edit, or reject individual findings. 
        Approve or decline tandem recommendations."

STEP 7 — GATE
  On approval:
    findings.status → "approved"
    stage_gates.findings_approved → true
    current_stage → "deliverable"
    For each approved tandem recommendation:
      Generate segment_brief.json in tandem/ directory
      Add to tandem.segment_briefs_generated
```

---

### Stage 5: Deliverable & Handoff

```
TRIGGER: Researcher invokes `niobe stage5`

PRE-CHECK: findings_approved must be true

STEP 1 — LOAD
  Read study_state.json
  Load population_findings.md
  Load population_brief.md
  Load all segment_briefs from tandem/ (if any)

STEP 2 — SELECT SPONSOR LENS
  Ask researcher: "Who is the primary audience for this deliverable?"
  Options:
    A. Product Manager → Decision Tree format
    B. CEO / Founder → Strategic Options format
    C. Investor → Market Validation format
    D. Brand / CMO → Campaign Brief format
    E. General → Standard Executive format

STEP 3 — GENERATE DELIVERABLE
  Based on sponsor lens, generate deliverable sections:

  ALL FORMATS include:
    - Executive Summary (3-5 bullet points)
    - Population Overview (who was simulated, how many, calibration source)
    - Methodology Note (simulation type, confidence range, limitations)

  PM DECISION TREE:
    - Decision tree: for each finding, "if this, then this" action mapping
    - Segment priority matrix (size × value × actionability)
    - Feature/change recommendations per segment
    - Tandem recommendations as "further investigation needed" items

  CEO STRATEGIC OPTIONS:
    - 3 strategic options with trade-offs
    - Segment map with sizing
    - Revenue impact estimates per option (from WTP distributions)
    - Risk/opportunity assessment per option

  INVESTOR MARKET VALIDATION:
    - TAM/SAM/SOM from segment sizing
    - Demand validation (proportion willing to pay at target price)
    - Competitive positioning (if comparative scenarios ran)
    - Key risk factors from driver analysis

  BRAND CAMPAIGN BRIEF:
    - Audience segments with messaging recommendations
    - Message test results (if message_test scenarios ran)
    - Channel recommendations by segment
    - Creative brief direction per segment

  GENERAL STANDARD EXECUTIVE:
    - Findings ranked by confidence and actionability
    - Segment overview table
    - Distribution summary table
    - Key drivers table
    - Surprise findings highlighted
    - Tandem recommendations

STEP 4 — PRESENT
  Display full deliverable
  Ask: "Review deliverable. Approve, edit, or request changes."

STEP 5 — GATE
  On approval:
    deliverable.status → "approved"
    stage_gates.deliverable_approved → true
    
STEP 6 — EXPORT
  Save deliverable.md
  If DOCX requested:
    Generate via docx-js (same toolchain as Morpheus)
    Save deliverable.docx
  If tandem handoffs exist:
    Display: "Segment Briefs ready for Morpheus handoff:
             {list of segment briefs}
             Run `morpheus stage1 --from-niobe {segment_brief.json}` to start 
             depth investigation."

STEP 7 — OFFER RETROSPECTIVE VALIDATION
  If domain is POLITICAL and study is prospective:
    "When the election results are available, run `niobe validate` to compare 
     simulation output against actual results."
```

---

## 4. PopScale Integration Contracts (Locked)

### The boundary rule

**Niobe never calls PopScale or Persona Generator internals directly.** No imports from `popscale.calibration`, `popscale.orchestrator`, `popscale.analytics`, `popscale.scenario`, or any `src.*` PG module. The only PopScale surface Niobe touches is `run_niobe_study()` and the types it exchanges.

This is not a preference — it is an architectural constraint. PopScale's internal schema changes frequently during build. If Niobe reaches into internals, every PopScale refactor breaks Niobe. The `run_study()` interface is the stability contract.

### The 4-block data flow

```
NiobeStudyRequest
    → _build_study_config()          [Niobe owns this translation]
    → run_study(StudyConfig)         [PopScale — single entry point]
    → run_calibrated_generation()    [PopScale → PG internally]
    → invoke_persona_generator()     [PG — Niobe never sees this]
    → run_population_scenario()      [PopScale → PG — Niobe never sees this]
    → (optional) run_social_scenario() [PopScale → PG — v2 only]
    → StudyResult                    [returned to Niobe]
```

### Contract 1: Niobe → PopScale (the only call)

```python
from popscale.niobe_interface import run_niobe_study, run_niobe_study_sync
from popscale.niobe_interface import NiobeStudyRequest
from popscale.study import StudyResult

# Async (default — use inside async context)
result: StudyResult = await run_niobe_study(
    NiobeStudyRequest(
        state="west_bengal",          # or "united_kingdom", "france", etc.
        n_personas=2000,
        domain="POLITICAL",
        business_problem="How do voters in West Bengal respond to...",
        scenarios=[...],              # list of Scenario objects
        environment_preset="west_bengal_political_2026",
        stratify_by_religion=True,    # silently no-op for non-India profiles
        stratify_by_income=True,
        sarvam_enabled=True,          # India only
        tier="VOLUME",
        budget_cap_usd=100.0
    )
)

# Sync wrapper (use from non-async context only — never from inside event loop)
result: StudyResult = run_niobe_study_sync(request)
```

### What Niobe owns: the translation layer

`_build_study_config()` is Niobe's sole authored function that touches PopScale types. It converts a `NiobeStudyRequest` into a `StudyConfig` that `run_study()` accepts. This function lives in Niobe's codebase, not PopScale's.

```python
# niobe/study_config.py — Niobe-authored

from popscale.niobe_interface import NiobeStudyRequest
from popscale.study import StudyConfig  # PopScale's type, read-only

def _build_study_config(request: NiobeStudyRequest) -> StudyConfig:
    """
    Translates NiobeStudyRequest → StudyConfig.
    This is the only place Niobe touches PopScale's config schema.
    When PopScale changes StudyConfig, update only here.
    """
    return StudyConfig(
        state=request.state,
        n_personas=request.n_personas,
        domain=request.domain,
        business_problem=request.business_problem,
        scenarios=request.scenarios,
        environment_preset=request.environment_preset,
        stratify_by_religion=request.stratify_by_religion,
        stratify_by_income=request.stratify_by_income,
        sarvam_enabled=request.sarvam_enabled,
        tier=request.tier,
        budget_cap_usd=request.budget_cap_usd,
    )
```

If PopScale changes `StudyConfig` — adds a field, renames a parameter — `_build_study_config()` is the only file that needs updating. No other Niobe file is exposed to that change.

### What Niobe receives: wrapping StudyResult

`run_niobe_study()` returns PopScale's `StudyResult`. Niobe reads it but does not modify it. If Niobe needs its own report format for the deliverable, it wraps `StudyResult` — it does not alter PopScale's output schema.

```python
# niobe/study_report.py — Niobe-authored

from popscale.study import StudyResult
from dataclasses import dataclass

@dataclass
class NiobeStudyReport:
    """
    Niobe's view of a completed study. Wraps StudyResult.
    Never modifies StudyResult's schema.
    """
    study_id: str
    study_result: StudyResult          # preserved exactly as returned
    
    # Niobe-specific additions
    findings: list                     # populated in Stage 4 synthesis
    segment_briefs: list               # populated in Stage 4 tandem step
    deliverable_md: str | None         # populated in Stage 5
    
    @property
    def segmentation(self):
        return self.study_result.report.segmentation
    
    @property
    def distributions(self):
        return self.study_result.report.distributions
    
    @property
    def drivers(self):
        return self.study_result.report.drivers
    
    @property
    def surprises(self):
        return self.study_result.report.surprises
```

### Geography support (current)

The `state` field in `NiobeStudyRequest` accepts:

| Region | Values |
|---|---|
| India states | `west_bengal`, `maharashtra`, `uttar_pradesh`, `bihar`, `tamil_nadu`, `karnataka`, `gujarat`, `rajasthan`, `delhi`, `andhra_pradesh`, `telangana`, and others in PopScale's profiles |
| USA | `united_states`, `us_northeast`, `us_south`, `us_midwest`, `us_west` |
| UK | `united_kingdom` |
| Europe | `france`, `germany`, `spain`, `italy`, `netherlands`, `poland`, `sweden` |

**Religion stratification behaviour:**
- India profiles: `stratify_by_religion=True` applies census-calibrated religion × income stratification
- US/UK/EU profiles: `stratify_by_religion=True` is a silent no-op — income stratification is used instead. Niobe presets handle this automatically; no special-casing needed in custom requests.

**EU geography note:** UK and US routing to PG persona pools is confirmed. EU country profiles (France, Spain, etc.) route via domain pool keys rather than location strings in PG. If a PG pool for that country hasn't been seeded, generation falls back gracefully — this is a PG-level concern, not Niobe's. Niobe passes the geography; PopScale handles the routing.

### Environment presets (current)

Pass as `environment_preset` string in `NiobeStudyRequest`. PopScale resolves to a full `SimulationEnvironment`.

| Geography | Available presets |
|---|---|
| India | `west_bengal_political_2026`, `india_national_policy`, `india_urban_consumer`, `india_rural_economy`, `maharashtra_consumer` |
| USA | `us_consumer_2026`, `us_political_2026`, `us_urban_consumer` |
| UK | `uk_consumer_2026`, `uk_political_2026` |
| Europe | `europe_consumer_2026`, `france_consumer_2026`, `uk_and_eu_policy` |

### Contract 2: Niobe → Morpheus (Segment Brief)

The Segment Brief is a JSON file written to `{study_dir}/tandem/segment_brief_{N}.json`. Morpheus reads it when invoked with `morpheus stage1 --from-niobe {path}`.

The Morpheus SKILL.md must be updated to support `--from-niobe` flag on `stage1`. This is a Stage 1 ingest variant that pre-populates the problem statement with the segment brief's context and recommended hypotheses.

### Contract 3: Morpheus → Niobe (Hypothesis List)

The Hypothesis List is a JSON file written by Morpheus to its project's `tandem/` directory. Niobe reads it when invoked with `niobe stage1 --from-morpheus {path}`.

---

## 5. Scenario Design Templates

Pre-built scenario templates for common research patterns. The researcher can use these directly or modify them.

### Template 1: Market Adoption (Consumer)

```yaml
template: market_adoption
domain: CONSUMER
scenarios:
  - name: awareness_and_interest
    type: concept_test
    question_template: "If a service existed that offered {value_prop}, how interested would you be?"
    options: ["Very interested", "Somewhat interested", "Neutral", "Not very interested", "Not at all interested"]
    hypothesis_type: prevalence
    
  - name: willingness_to_pay
    type: pricing
    question_template: "At what price would {product} be..."
    sub_questions:
      - "too cheap (you'd question the quality)?"
      - "a bargain (you'd feel great about buying it)?"
      - "getting expensive (you'd have to think about it)?"
      - "too expensive (you'd never buy it)?"
    hypothesis_type: distribution
    
  - name: feature_priority
    type: issue_salience
    question_template: "Rank these features of {product} from most to least important to you"
    options_from: feature_list
    hypothesis_type: issue_salience
```

### Template 2: Message Resonance (Consumer/Political)

```yaml
template: message_resonance
domain: CONSUMER | POLITICAL
scenarios:
  - name: message_ab_test
    type: message_test
    variants:
      - name: "Variant A"
        message: "{message_a}"
      - name: "Variant B"
        message: "{message_b}"
    question_template: "After reading this message, how likely are you to {action}?"
    options: ["Very likely", "Somewhat likely", "Neutral", "Somewhat unlikely", "Very unlikely"]
    hypothesis_type: comparative
```

### Template 3: Electoral Landscape (Political)

```yaml
template: electoral_landscape
domain: POLITICAL
scenarios:
  - name: party_preference
    type: choice
    question_template: "If the {election} were held today, which party would you vote for?"
    options_from: party_list
    hypothesis_type: distribution
    
  - name: issue_salience
    type: issue_salience
    question_template: "Which issue is most important to you in deciding your vote?"
    options_from: issue_list
    hypothesis_type: issue_salience
    
  - name: candidate_perception
    type: concept_test
    question_template: "How would you describe your impression of {candidate}?"
    options: ["Very favorable", "Somewhat favorable", "Neutral", "Somewhat unfavorable", "Very unfavorable"]
    hypothesis_type: distribution
    
  - name: turnout_intent
    type: prevalence
    question_template: "How likely are you to vote in the upcoming {election}?"
    options: ["Definitely will vote", "Probably will vote", "Might vote", "Probably won't vote", "Definitely won't vote"]
    hypothesis_type: prevalence
```

### Template 4: Policy Response (Policy)

```yaml
template: policy_response
domain: POLICY
scenarios:
  - name: policy_support
    type: concept_test
    question_template: "The government is considering {policy}. How do you feel about this?"
    options: ["Strongly support", "Somewhat support", "Neutral", "Somewhat oppose", "Strongly oppose"]
    hypothesis_type: prevalence
    
  - name: compliance_intent
    type: prevalence
    question_template: "If {policy} were implemented, how likely would you be to {compliance_action}?"
    options: ["Very likely", "Somewhat likely", "Neutral", "Somewhat unlikely", "Very unlikely"]
    hypothesis_type: cross_tab
    
  - name: communication_test
    type: message_test
    variants:
      - name: "Factual framing"
        message: "{factual_message}"
      - name: "Benefit framing"
        message: "{benefit_message}"
    question_template: "How does this message change your view on {policy}?"
    hypothesis_type: comparative
```

---

## 6. Population Synthesis — Prompt Specification

### Finding Generation Prompt

```
You are a population research analyst synthesising simulation results 
into actionable findings.

CONTEXT:
Business question: {business_question}
Target population: {target_population}
Population size: {n_personas} synthetic agents
Domain: {domain}

HYPOTHESIS: {DH_ID} — "{hypothesis_statement}"
TYPE: {prevalence / distribution / cross_tab / comparative / issue_salience / message_test}
EXPECTED RANGE: {expected_range}

POPSCALE ANALYTICS OUTPUT:

SEGMENTATION:
{segmentation_result_formatted}

DISTRIBUTIONS:
{distribution_result_formatted}

DRIVERS:
{driver_analysis_formatted}

SURPRISES:
{surprise_result_formatted}

Generate a POPULATION FINDING with these sections:

1. HEADLINE — One sentence that states the finding in plain English. 
   No codes, no effect sizes, no technical language. A founder should 
   be able to read this sentence and know what it means.

2. VERDICT — Is the hypothesis CONFIRMED, PARTIALLY CONFIRMED, or 
   REFUTED? State the actual distribution and compare to the expected 
   range. Include the confidence interval.

3. WHAT THE DATA SHOWS — Describe the distribution in natural language. 
   Use percentages and proportions. Translate segment labels into 
   human-readable descriptions. Do not use internal codes.

4. WHAT DRIVES IT — Which population attributes predict this outcome? 
   Use the driver analysis. Translate effect sizes into plain language:
   - Effect size < 0.10: "no meaningful relationship"
   - 0.10–0.29: "weak but detectable relationship"  
   - 0.30–0.49: "meaningful relationship"
   - ≥ 0.50: "strong relationship"
   Name the specific attributes, not just the effect sizes.

5. WHAT'S SURPRISING — If any surprise flag fired (deviation >15pp 
   from naive prior), explain what was expected and what actually 
   happened. If no surprises, state: "No counterintuitive findings 
   for this hypothesis."

6. WHAT THIS MEANS — Connect the finding back to the business question. 
   Not a recommendation — a clear statement of what the finding implies 
   for the decision the client is trying to make. Use language like 
   "this suggests" or "this implies" — never "you should" or "we 
   recommend."

RULES:
- No internal codes (DH01, SD01, RUN_001). Use plain English.
- No PopScale technical terms (Cramér's V, eta-squared, Wilson CI). 
  Translate into natural language.
- Round percentages to whole numbers unless the decimal matters.
- Always state the confidence interval when citing a proportion.
- If a finding is based on a sub-sample < 30, explicitly flag it: 
  "Note: this finding is based on a small sub-sample ({n}) and should 
  be treated as directional, not definitive."
```

### Cross-Scenario Finding Prompt

```
You are comparing results across two or more population simulation 
scenarios to identify what changed and what that reveals.

SCENARIO A: {scenario_a_question}
Results: {distribution_a}

SCENARIO B: {scenario_b_question}
Results: {distribution_b}

SEGMENT-LEVEL DELTAS:
{per_segment_comparison}

Generate a CROSS-SCENARIO FINDING:

1. HEADLINE — What changed and why it matters.

2. OVERALL SHIFT — The population-level delta between scenarios. 
   Express as percentage-point change.

3. SEGMENT SHIFTS — Which segments moved most? Which didn't move? 
   What does the differential shift reveal about the segments?

4. INTERPRETATION — What does the comparison tell us about the 
   business question that neither scenario alone could?

RULES:
- Same plain-English rules as individual findings.
- Focus on the DELTA, not restating each scenario's results.
```

---

## 7. Research Critic — Exact Spec (Locked)

The Critic follows Morpheus's architecture: separate LLM call, constrained context, no access to conversation history.

### Stage 1 Critic

```
Review this population brief and demographic specification.

POPULATION BRIEF:
{brief_text}

POPULATION SPEC:
{spec_json}

CALIBRATION PROFILE:
{demographic_profile}

CRITERIA:
1. Does the population spec cover all segments named in the brief?
2. Is any demographic segment >10% of the real population missing 
   from stratification?
3. Is the market size estimate sourced or assumed? If assumed, flag it.
4. Are the study objectives testable at population scale with 
   structured scenarios (not open-ended probing)?
5. Is {n_personas} sufficient for the number of study objectives? 
   (Rule of thumb: ≥200 per hypothesis for statistical validity)
6. Is the geographic scope consistent with the population spec's 
   state/region?

Output each issue as:
ISSUE: {description}
SEVERITY: HIGH | MEDIUM | LOW
LOCATION: {which section}
SUGGESTION: {specific fix}
```

### Stage 2 Critic

```
Review these distributional hypotheses and scenario designs.

HYPOTHESES:
{hypothesis_register_text}

SCENARIO DESIGNS:
{scenario_designs_text}

CRITERIA:
1. Are any hypotheses untestable with the chosen scenario type?
2. Are any expected ranges implausibly narrow (<5pp) or wide (>50pp)?
3. Is any scenario question using leading language?
4. Will any cross-tab hypothesis end up with sub-samples < 30 after 
   stratification? (Check population spec N vs segment proportions)
5. Is the scenario sequence biased? Would a different order produce 
   different results?
6. Swap test: could any scenario produce the same result for a 
   completely different business question?
7. Are comparative scenarios fair? Do both variants get equal framing?

Output format: ISSUE / SEVERITY / LOCATION / SUGGESTION
```

### Stage 4 Critic

```
Review these population findings.

FINDINGS:
{findings_text}

ANALYTICS DATA USED:
{raw_analytics_summaries}

CRITERIA:
1. Does any finding claim more precision than the confidence interval 
   supports?
2. Are any cross-tab findings based on sub-samples < 30?
3. Are any surprise findings artifacts of the naive prior estimation 
   (was the prior poorly calibrated) rather than genuine population 
   deviations?
4. Does any finding make a causal claim when the data only supports 
   correlation?
5. Are the tandem recommendations substantiated — is there actually a 
   "why" question left unanswered, or is the finding self-explanatory?
6. Are any findings redundant (saying the same thing with different 
   numbers)?

Output format: ISSUE / SEVERITY / LOCATION / SUGGESTION
```

---

## 8. SKILL.md Command Structure

### Command Reference

| Command | Stage | What It Does | Requires |
|---|---|---|---|
| `niobe stage1` | Intake | Generate Population Brief + Spec, Critic, gate | Nothing |
| `niobe stage1 --from-morpheus {path}` | Intake | Pre-populate from Morpheus Hypothesis List | Hypothesis List JSON |
| `niobe stage2` | Design | Generate hypotheses + scenarios, cost estimate, Critic, gate | Stage 1 approved |
| `niobe stage3` | Simulation | Execute scenarios via PopScale, quality review, gate | Stage 2 approved |
| `niobe stage4` | Synthesis | Generate findings + tandem recommendations, Critic, gate | Stage 3 confirmed |
| `niobe stage5` | Deliverable | Generate client deliverable + Segment Briefs, gate | Stage 4 approved |
| `niobe status` | Any | Show study state, gates, next action | Nothing |
| `niobe help` | Any | Show all commands | Nothing |
| `niobe validate` | Post-study | Compare simulation output to actual outcomes | Study complete + real data |

### Skill Triggers

```yaml
triggers:
  - "niobe"
  - "population study"
  - "population research"
  - "how many users"
  - "what proportion"
  - "segment sizing"
  - "distribution analysis"
  - "electoral simulation"
  - "voter simulation"
  - "population simulation"
  - "run population"
  - "broad research"
```

---

## 9. Morpheus SKILL.md Updates Required

To support the tandem protocol, Morpheus needs these additions:

### New `--from-niobe` flag on stage1

When `morpheus stage1 --from-niobe {segment_brief.json}` is invoked:
1. Read the Segment Brief JSON
2. Pre-populate problem statement with:
   - Business context from the Niobe study
   - The segment description as the target ICP
   - The deep question as the research question
3. Pre-populate fact table with:
   - Population finding as a FACT entry (it's validated distributional data)
   - Segment behavioral profile as FACT entries
   - Recommended hypotheses as INFERENCE entries (they're suggestions)
4. Present to researcher for review — same Stage 1 flow, just pre-populated

### New `--to-niobe` flag on deliver (Step 5)

After `morpheus deliver`, add an offer:
```
"This study produced directional findings. Would you like to test their 
prevalence across a population via Niobe?

If yes, I'll generate a Hypothesis List that Niobe can use as input."
```

If researcher confirms:
1. Extract directional findings from evidence synthesis
2. Reframe each as a distributional hypothesis
3. Generate hypothesis_list.json in `{project_dir}/tandem/`
4. Display: "Run `niobe stage1 --from-morpheus {path}` to start the population study."

---

## 10. Build Sequence (Locked)

### When to start: PopScale Week 4 complete

Niobe build starts ONLY after:
- PopScale `PopScaleReport` schema is stable (Week 3)
- PopScale 2,000-agent validation passes (Week 4)
- Scenario model, analytics, and orchestrator APIs are tested

### Build phases

```
PHASE 1 — SKILL SCAFFOLD + STAGE 1 (Week 5)
  - Create skill directory: ~/.claude/skills/simulatte-niobe/
  - Write SKILL.md with stage1 flow
  - Population Brief generation prompt
  - PopulationSpec generation (calls PopScale calibrator)
  - Critic for Stage 1
  - study_state.json initialization
  - Test: run Stage 1 on 3 different business questions

PHASE 2 — STAGE 2 + SCENARIO DESIGN (Week 6)
  - Hypothesis Designer module
  - Scenario Design generation (maps hypothesis type → scenario type)
  - Cost estimation integration
  - Critic for Stage 2
  - Test: run Stage 2 on outputs from Phase 1

PHASE 3 — STAGE 3 + POPSCALE ORCHESTRATION (Week 7)
  - PopScale invocation flow
  - Run quality review display
  - Diagnostics capture
  - Circuit breaker event handling
  - Test: run Stage 3 with 500 personas (cost-safe scale)
  - Test: run Stage 3 with 2,000 personas (full scale)

PHASE 4 — STAGE 4 + SYNTHESIS (Week 8)
  - Finding generation prompts
  - Cross-scenario finding generation
  - Tandem candidate identification
  - Critic for Stage 4
  - Segment Brief generation
  - Test: run Stage 4 on outputs from Phase 3

PHASE 5 — STAGE 5 + DELIVERABLE + TANDEM (Week 9)
  - Deliverable generation (5 sponsor lens templates)
  - DOCX export (reuse Morpheus docx-js toolchain)
  - Morpheus SKILL.md updates (--from-niobe, --to-niobe)
  - End-to-end test: full study from Stage 1 → 5
  - Tandem test: Morpheus → Niobe and Niobe → Morpheus handoff
```

### West Bengal readiness

```
Week 9:  Niobe v1 complete
Week 9:  PopScale Political domain templates ready
Week 10: 10K scale validation (requires PopScale fan-out extension)
Week 11: West Bengal study design (Niobe Stage 1-2)
Week 12: West Bengal study execution (Niobe Stage 3-5)
```

---

## 11. Kill List

### 5 things that MUST NOT enter Niobe v1

1. **Social simulation orchestration.** PopScale's `run_social_loop()` supports multi-round agent-to-agent interaction. Niobe v1 uses single-round scenario response only. Social simulation studies are v2.

2. **Automated chart generation.** Distributions are described in narrative. Bar charts, segment maps, and distribution curves are future capabilities. The researcher generates charts manually if needed.

3. **Real-time simulation monitoring dashboard.** The skill displays progress after each shard completes. There is no live-updating progress bar or WebSocket feed. The researcher waits.

4. **Cross-study meta-analysis.** Each Niobe study is self-contained. "Compare this study to last month's study" is a post-v1 capability.

5. **Automated tandem handoff.** The researcher must explicitly invoke `morpheus stage1 --from-niobe`. There is no automatic Morpheus study creation when a Segment Brief is generated. The researcher decides.

### 5 things that will tempt over-engineering

1. **"Let's add a segment explorer that lets the researcher drill into individual agents."** No. Individual agents are Morpheus territory. Niobe works with distributions and segments. If the researcher needs to understand one agent, that's a Segment Brief → Morpheus handoff.

2. **"Let's build a scenario A/B testing framework with statistical significance testing."** No. Niobe compares distributions. Statistical significance testing on synthetic agents is epistemically fraught — the "sample" is not a sample, it's a deterministic simulation. CIs are internal consistency measures, not sampling error. Don't build a framework that implies otherwise.

3. **"Let's make Niobe learn from past studies to improve future scenario design."** No. This is Morpheus Observatory territory. Niobe v1 designs each study from scratch. Cross-study learning is a shared capability, not duplicated across tools.

4. **"Let's add environment presets for every Indian state."** PopScale already has environment presets. Niobe uses them. Niobe does not create or manage environments — that's PopScale's domain.

5. **"Let's build a population comparison view that shows how the synthetic population differs from census data."** PopScale's calibrator already validates within 5% deviation. Niobe trusts that validation. It does not re-validate.

### 5 signals that Niobe is becoming too complex

1. The SKILL.md exceeds 800 lines → split into sub-skills or reference files
2. A stage requires more than 3 LLM calls → the stage is doing too much
3. The study_state.json has more than 4 levels of nesting → you're building a database
4. The synthesis prompt exceeds 2,000 tokens → the prompt is trying to be too smart
5. The researcher skips Niobe and runs PopScale directly → Niobe adds friction, not value

---

## 12. Success Metrics (Locked, Final)

| # | Metric | Definition | Target | How to Measure | Kill Signal |
|---|---|---|---|---|---|
| 1 | **Synthesis actionability** | Can a non-technical reader act on the finding without asking for clarification? | ≥80% of findings rated actionable | Researcher reviews each finding post-study: "Would {client} understand this?" | <50% after 3 studies → synthesis prompts need redesign |
| 2 | **Scenario design accuracy** | Do approved scenario designs produce valid PopScale `SimulationResult` objects? | ≥95% success rate across all runs | success_count / total_personas across all runs in a study | <90% → scenario generation is producing invalid inputs |
| 3 | **Hypothesis resolution rate** | % of distributional hypotheses that reach a clear verdict (CONFIRMED / REFUTED) rather than "inconclusive" | ≥70% | Count verdicts across all hypotheses | <50% → hypotheses are too vague or scenarios don't test them |
| 4 | **Time-to-findings** | Researcher time from business question to approved findings | ≤2 hours for a 2,000-agent study | Timestamps: study creation → findings approval | >4 hours → Niobe adds too much overhead |
| 5 | **Tandem usage rate** | % of studies that generate at least one Segment Brief | ≥30% | Count segment_briefs_generated across studies | 0% after 5 studies → tandem protocol is unused; simplify or remove |
| 6 | **Critic-induced edit rate** | % of critic issues that result in researcher editing before approval | 15-30% | Compare artifact pre/post approval | <10% → Critic is noise; >40% → generation prompts are weak |

---

## 13. Raising the Probability to ~90%

The original probability breakdown identified two drag points: synthesis quality (70%) and tandem protocol adoption (60%). Getting to 90% overall requires targeted interventions on both — not architectural changes, but specific build decisions that address the failure modes directly.

### The gap analysis

| Component | Original | Why it was low | Target |
|---|---|---|---|
| PopScale orchestration | 95% | Low risk — Python function calls | 97% |
| State management | 85% | Proven Morpheus pattern | 92% |
| Scenario design validity | 80% | Invalid PopScale inputs possible | 92% |
| Population synthesis | 70% | Fluent but not sharp | 88% |
| Tandem protocol adoption | 60% | Opt-in means it gets skipped | 78% |

**Combined estimate with interventions: ~88–90%.**

### Intervention 1: Template-first scenario design (80% → 92%)

The risk was that free-form scenario generation produces invalid PopScale `Scenario` objects or leading question language. Fix: Niobe always starts from a pre-validated template (Section 5 of this spec) and customises, rather than generating from scratch. Template → customisation reduces generation errors by constraining the output space.

Additionally, **pre-approval scenario validation**: before presenting scenarios to the researcher, Niobe constructs the actual `Scenario` object and validates it against PopScale's model:

```python
from popscale.scenario.model import Scenario
try:
    scenario = Scenario(**generated_design)
    # validation passes → present to researcher
except ValidationError as e:
    # regenerate, fix, then present
```

No invalid scenarios reach the researcher. The researcher approves only scenarios that PopScale will accept.

**Add to Stage 2 execution flow — between STEP 3 and STEP 4:**

```
STEP 3b — PRE-VALIDATE SCENARIOS
  For each generated scenario design:
    Attempt to construct PopScale Scenario object
    If ValidationError:
      Log the failure
      Regenerate that scenario with the validation error as context
      Retry (max 2 attempts)
    If still invalid after 2 attempts:
      Flag as NEEDS_MANUAL_REVIEW and skip Critic for this scenario
  
  Display validation summary before Critic:
    "Validated {N}/{total} scenarios. {N} passed, {N} flagged for review."
```

### Intervention 2: Synthesis Validation Critic (70% → 88%)

The synthesis Critic at Stage 4 currently checks statistical validity: "does any finding claim more precision than the CI supports?" This is necessary but insufficient. The deeper failure mode is a finding that is statistically correct but communicatively useless — a researcher reads it and knows it's technically right but can't translate it into a decision.

Add a **dedicated second Critic pass for synthesis**: after the statistical Critic runs, a separate LLM call with a completely different brief evaluates only communication quality.

**Synthesis Validation Critic prompt:**

```
You are a non-technical business advisor reading a research finding.
You have no statistical background. You are trying to make a product 
decision.

BUSINESS QUESTION: {business_question}
TARGET DECISION-MAKER: {sponsor_lens}

FINDING:
{finding_text}

Answer these questions:
1. Can you make a decision based on this finding? YES / NO
   If NO: what is missing that would make it actionable?

2. Is there any sentence you would need to ask the researcher to 
   explain? Mark each one.

3. Does this finding answer the business question directly, or does 
   it answer a related but different question?

4. If you had to cut this finding to one sentence that a founder 
   would put in a board deck, what would it be?

Output:
ACTIONABLE: YES | NO
UNCLEAR_SENTENCES: {list or "none"}
ANSWERS_BUSINESS_QUESTION: YES | PARTIALLY | NO
BOARD_DECK_SENTENCE: {one sentence}
```

**Rule:** A finding is approved for the deliverable only if `ACTIONABLE: YES` AND `ANSWERS_BUSINESS_QUESTION: YES | PARTIALLY`. If both fail, the finding is returned to synthesis with the Critic's specific objections, and regenerated once.

**Add to Stage 4 execution flow — after STEP 5:**

```
STEP 5b — SYNTHESIS VALIDATION CRITIC
  For each finding that passed the statistical Critic:
    Run Synthesis Validation Critic (SEPARATE TOOL CALL):
      Input: business_question + sponsor_lens + finding text ONLY
    If ACTIONABLE: NO AND ANSWERS_BUSINESS_QUESTION: NO:
      Regenerate finding with validation failures as context
      Re-run statistical Critic on regenerated finding
      Re-run Synthesis Validation Critic
      Accept the regenerated version regardless of outcome
        (one regeneration attempt — do not loop)
    Record: BOARD_DECK_SENTENCE for each finding
      (used as the headline in the deliverable)
```

**Why one regeneration attempt and not a loop:** The failure mode is prompts, not architecture. If the second attempt still fails validation, the synthesis prompt needs redesigning. A loop would mask this signal. Surface it to the researcher.

### Intervention 3: Business question anchoring (70% → 88%, works with Intervention 2)

Every synthesis prompt currently includes the business question as context. That's necessary but not sufficient — LLMs use context but don't always make the final connection explicit.

**Change the synthesis prompt's mandatory section:**

The `WHAT THIS MEANS` section of every finding prompt must be restructured:

```
6. WHAT THIS MEANS FOR THE DECISION

Complete this sentence: "Given this finding, {client_name} should 
consider {specific_action} because {this_finding_shows_that_X} 
and ignoring this would mean {Y}."

If you cannot complete this sentence without guessing, do not 
attempt to. Instead write: "This finding establishes [X] but the 
decision implication depends on [what additional context is needed]."

Do not fabricate a business implication. An honest "we know X but 
not yet what to do about it" is more valuable than a false 
recommendation.
```

This forces explicit connection to the decision, but with an honest escape hatch that prevents hallucinated implications. It also surfaces when a finding genuinely doesn't answer the business question — which is useful signal, not a failure.

### Intervention 4: Tandem auto-trigger, opt-out (60% → 78%)

The tandem protocol was designed as opt-in: "Would you like to generate a Segment Brief?" The problem with opt-in is that it requires the researcher to recognise, in the moment, that a segment warrants depth investigation. Under delivery pressure, researchers don't stop to think. They move to the deliverable.

**Change: auto-trigger with opt-out.**

During Stage 4, any finding that meets all three tandem criteria automatically generates a draft Segment Brief:

```
TANDEM CRITERIA (all three must be true):
1. Segment size ≥ 15% of population
2. The finding identifies a behavioral pattern (not just a demographic split)
3. The driver analysis does not explain WHY — only WHAT

If all three criteria met:
  AUTO-GENERATE segment_brief_{N}.json in tandem/
  Display: "Segment Brief generated for [{segment_label}].
           This segment's behavior is not explained by demographics alone.
           Review in tandem/ or discard with `niobe discard-brief {N}`."
```

The researcher can ignore it or discard it. But they see it. The default is "this segment warrants investigation" not "ask me if you want to investigate."

**Additionally:** the Segment Brief must be rich enough to save time. Minimum required fields for it to feel useful rather than bureaucratic:

```json
{
  "what_niobe_found": "38% of the population refuses to book without verifying the scholar's qualification. This group has the highest WTP (£75+) but the lowest conversion rate.",
  "what_morpheus_should_answer": "What specific credential information resolves this — institution name alone, or is case-experience description required? At what point in the journey does verification anxiety peak?",
  "what_you_already_know": "Trust orientation is the strongest predictor (Cramér's V = 0.43). This segment is not price-sensitive — credential-anxious, not budget-constrained.",
  "pre_populated_morpheus_hypotheses": [
    "Institution name alone is insufficient — condition-specific experience is the resolver",
    "Credential anxiety peaks at the point of payment, not at discovery",
    "A scholar biography page resolves more anxiety than a WhatsApp credential exchange"
  ]
}
```

The researcher reads this and immediately knows what Morpheus is for. It saves 30 minutes of problem-framing, which is the threshold for making the handoff feel worth it.

### Intervention 5: Pre-ship synthesis gate (equivalent to Morpheus Week 1 gate)

Before shipping Niobe v1, run a mandatory pre-ship test:

```
Pre-ship gate (must pass before any client study):

1. Take 3 real PopScaleReport outputs from PopScale's Week 3-4 test runs
2. Run the synthesis prompt on each
3. Run the Synthesis Validation Critic on each output
4. For each finding, ask: "Would a non-technical client act on this?"
5. Count findings where ACTIONABLE: YES

Gate:
  ≥70% of findings ACTIONABLE: YES across all 3 test runs → SHIP
  <70% → redesign the synthesis prompt. Do not ship.
```

This is the same gating logic as Morpheus's Week 1 Assumptions Ledger test. It forces an empirical validation of the most critical capability before any real study runs.

**Add to build sequence Phase 4 (Week 8):**

```
PHASE 4 — STAGE 4 + SYNTHESIS (Week 8)
  [existing steps]
  
  PRE-SHIP SYNTHESIS GATE (end of Week 8):
    Run synthesis + validation Critic on 3 PopScale Week 3-4 outputs
    Count ACTIONABLE: YES rate
    Record: which findings failed and why
    If <70%: redesign synthesis prompt before Phase 5
    If ≥70%: proceed to Phase 5
```

---

## 14. Final Verdict

### Will this work?

**~90% chance it works in real usage with the five interventions above.**

| Component | Probability | Intervention |
|---|---|---|
| PopScale orchestration | 97% | Pre-approval validation catches invalid scenarios before researcher sees them |
| State management | 92% | Proven Morpheus pattern. Minor risk from new state fields. |
| Scenario design validity | 92% | Template-first + pre-approval validation eliminates most invalid inputs |
| Population synthesis | 88% | Synthesis Validation Critic + business question anchoring + pre-ship gate |
| Tandem protocol adoption | 78% | Auto-trigger changes default from opt-in to opt-out |

Without the five interventions, the estimate stays at 75%. With them, ~88–90%.

### The ONE thing most likely to still fail

**The synthesis will produce findings that are actionable on the first attempt less often than expected.** The Synthesis Validation Critic catches failures and triggers regeneration — but regeneration is one attempt, not a loop. If the synthesis prompt is fundamentally misaligned with what the business question requires, the pre-ship gate will catch it before it ships. If the misalignment is subtler — context-dependent, varies by domain — it will surface in the first 2-3 real studies.

The pre-ship gate is the safety net before shipping. The Critic-induced edit rate metric is the ongoing signal. If the Critic-induced edit rate stays below 10% after 5 studies, the synthesis prompts have saturated — either they're genuinely good, or the Critic has lost sharpness. The pre-ship gate confirms which.

### What to do right now

Same as before: wait for PopScale Week 3 analytics schema to stabilise. Then, before writing any orchestration code, write the synthesis prompt and the Synthesis Validation Critic prompt. Run both against real PopScaleReport output. Count actionable findings. If ≥70%, the synthesis architecture is sound. If not, fix the prompt before building anything else.

The pre-ship gate forces this discipline into the build sequence, not just as advice.

---

*End of build spec. Start building when PopScale Week 3 delivers.*
