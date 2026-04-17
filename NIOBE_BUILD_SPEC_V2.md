# Niobe — Build Specification v2
## Full Engineering Implementation Guide

**Version:** 2.0  
**Date:** 2026-04-16  
**Status:** Build-ready. Supersedes BUILD_SPEC.md.  
**Posture:** You are an engineer. Read this, then build.

---

## 1. Current State (What Is Already Built)

Do not rebuild these. They are production-ready and tested.

### 1.1 Foundation Layer (100% complete)

| Module | File | Status |
|---|---|---|
| NiobeStudyRequest | `niobe/study_request.py` | Production-ready |
| `run_niobe_study()` / `run_niobe_study_sync()` | `niobe/runner.py` | Production-ready |
| Geography presets (9 presets) | `niobe/presets.py` | Production-ready |
| Morpheus→Niobe bridge | `morpheus/bridge/niobe_adapter.py` | Production-ready, deployed |
| Test suite (35+ tests) | `tests/test_niobe_scaffold.py` | All passing |

### 1.2 PopScale Engine (100% complete — dependency)

| Capability | Status |
|---|---|
| DemographicProfile (46 profiles: India 23, USA 16, UK 1, EU 6) | Production-ready |
| PopulationSpec + calibrate() | Production-ready |
| run_calibrated_generation() | Production-ready |
| run_seeded_generation() (VariantGenerator + SeedCalibrator) | Production-ready |
| run_population_scenario() (sharded, circuit-broken, cached) | Production-ready |
| 4-layer analytics: segmentation, distributions, drivers, surprises | Production-ready |
| run_social_scenario() | Experimental (PG-owned, thin wrapper) |
| Cost estimation + budget cap enforcement | Production-ready |

### 1.3 What Is NOT Built (The Build Target)

Everything below this line needs to be built:

1. `~/.claude/skills/simulatte-niobe/SKILL.md` — The skill definition file
2. Stage 1 orchestration logic (brief generation, spec generation, Critic)
3. Stage 2 orchestration logic (hypothesis generation, scenario design, Critic)
4. Stage 3 orchestration logic (pre-simulation check, PopScale invocation, quality review, Critic)
5. Stage 4 orchestration logic (synthesis, findings generation, tandem identification, Critic)
6. Stage 5 orchestration logic (deliverable rendering, Segment Brief generation)
7. Study state management (study_state.json read/write)
8. Research Critic (separate LLM call per stage)
9. Tandem handoff: Niobe → Morpheus (Segment Brief generation)
10. Tandem handoff: Morpheus → Niobe (`--from-morpheus` flag)
11. Morpheus SKILL.md updates (`--from-niobe`, `--to-niobe` flags)
12. End-to-end test: full study, asserts `n_delivered > 0`

---

## 2. Architecture: Exactly Like Morpheus

Niobe is a Claude Code skill. Implementation mirrors Morpheus architecture exactly:

- **Skill file:** `~/.claude/skills/simulatte-niobe/SKILL.md`
- **Invocation:** `niobe [command] [args]`
- **State:** `{study_dir}/study_state.json`
- **Artifacts:** Markdown files + JSON in `{study_dir}/`
- **PopScale calls:** Direct Python import via `run_niobe_study()` in `niobe/runner.py`
- **Critic:** Separate LLM call, constrained context, per stage
- **No web UI.** No API. No queue. File system is the database.

### Study Directory Convention
```
pilots/{client}/niobe/{study_name}/
```
Or for standalone studies:
```
~/simulatte-studies/{study_name}/niobe/
```

---

## 3. SKILL.md Structure

The skill file must implement all 23 commands from the Capability Spec. Structure:

```
# Niobe — Population Research Orchestrator

## Trigger
When user says: "niobe", "/niobe", or any niobe [command]

## Commands
[All 23 commands with exact handling logic]

## Stage Handlers
[One section per stage with: prompt template, Critic prompt, gate logic, file writes]

## State Management
[Read/write study_state.json]

## PopScale Integration
[How to call run_niobe_study() and interpret results]

## Tandem Protocol
[Segment Brief format, Hypothesis List format, handoff logic]

## Critic Architecture
[Per-stage Critic prompts and pass/fail criteria]

## Rules (non-negotiable)
[Equivalent of Morpheus's 45 rules]
```

---

## 4. Stage Implementation — Exact Prompts and Logic

### Stage 1: Population Intake

**Trigger:** `niobe stage1`

**Pre-condition check:**
```python
if study_state["current_stage"] != 1 and not study_state["gates"]["brief_approved"] == False:
    return "Stage 1 already complete. Use 'niobe status' to see current state."
```

**Step 1.1 — Brief Generation Prompt:**
```
You are writing a Population Brief for a Simulatte population study.

INPUTS:
- Research question: {user_research_question}
- Geography: {state}
- Domain: {domain}
- Population size: {n_personas}
- Budget cap: {budget_cap_usd}

Generate a Population Brief with these exact sections:

## Decision Context
[2–3 sentences: what decision will this research inform?]

## Study Objectives
[3–5 numbered objectives, each starting with an action verb, each testable at population scale]

## Target Population Definition
[Who exactly is in scope: age range, geography, urban/rural, any filters]

## Market Size Estimate
[Estimated real-world population this synthetic cohort represents. Source or flag as assumed.]

## Research Scope Boundary
[1–2 sentences: what this study will NOT attempt to answer — reserve for Morpheus]

RULES:
- Objectives must be testable via scenario simulation (distribution questions, not depth questions)
- Any objective requiring "why do they feel this way" belongs in Research Scope Boundary
- Market size must cite a source or be flagged as [ASSUMED]
```

**Step 1.2 — Spec Generation:**
Call `calibrate(PopulationSpec(state=state, n_personas=n_personas, ...))` to get segment map.

Then render:
```
## Population Spec

Geography: {state} ({pg_location})
N Personas: {n_personas}
Generation approach: {standard|seeded} (seeded if n_personas > 300)
Seed count: {200 if seeded else N/A}
Estimated generation cost: ${estimate}
Estimated simulation cost: ${estimate} (per scenario at SIGNAL tier)

### Demographic Segments
| Segment | Proportion | Count | Anchor Overrides |
|---|---|---|---|
{for each segment from calibrate() result}

### Stratification
Religion × income: {yes/no, with explanation}
Urban/rural split: {urban_pct}% urban
Age range: {min_age}–{max_age}
```

**Step 1.3 — Stage 1 Critic:**
```
You are the Stage 1 Critic for a Niobe population study. Review this Population Brief and Spec.
Be terse. Fail fast. Do not hedge.

BRIEF:
{population_brief_content}

SPEC:
{population_spec_content}

Check each criterion. Answer YES or NO, then one sentence of explanation.

1. REPRESENTATIVENESS: Is the demographic spec representative of the stated geography?
2. SOURCED MARKET SIZE: Is market size sourced, or flagged as assumed?
3. TESTABILITY: Are all 3–5 objectives testable via scenario simulation (not requiring depth)?
4. SCOPE BOUNDARY: Is there a clear scope boundary reserving depth questions for Morpheus?
5. SEGMENT COVERAGE: Do the demographic segments cover the target population adequately?

VERDICT: PASS or FAIL (fail if any criterion is NO)
REQUIRED CHANGES: [bullet list if FAIL, empty if PASS]
```

**Gate logic:**
- Critic returns PASS → set `brief_approved = true`, `spec_approved = true`, advance stage
- Critic returns FAIL → display REQUIRED CHANGES, stay in Stage 1, prompt user to revise

**File writes:**
- `population_brief.md`
- `population_spec.json`
- Update `study_state.json`

---

### Stage 2: Hypothesis & Scenario Design

**Trigger:** `niobe stage2`

**Pre-condition:** `brief_approved AND spec_approved`

**Step 2.1 — Hypothesis Generation Prompt:**
```
You are generating distributional hypotheses for a Niobe population study.

POPULATION BRIEF:
{population_brief_content}

STUDY OBJECTIVES:
{objectives_list}

Generate 6–10 distributional hypotheses. Each hypothesis must:
- Be testable by a single PopScale scenario run
- Have a numeric expected range
- Map to at least one study objective
- Use one of these types: prevalence | distribution | cross_tab | comparative | issue_salience | message_test

For each hypothesis, output:
---
ID: H{N}
TYPE: {type}
STATEMENT: [A falsifiable distributional claim]
EXPECTED RANGE: [{low}%–{high}%] or [{option}: {low}–{high}%] for distributions
LINKED OBJECTIVE: O{N}
PRIORITY: HIGH | MED | LOW
RATIONALE: [1 sentence: why this range? What prior knowledge informs it?]
---

HYPOTHESIS TYPES DEFINED:
- prevalence: "X% of population will [action/believe Y]"
- distribution: "Responses will distribute as [option A: X%, option B: Y%, ...]"
- cross_tab: "Segment A will show [X%] vs Segment B [Y%] on the same measure"
- comparative: "Option A will score [X points] higher than Option B on [measure]"
- issue_salience: "[Issue X] will rank in top-3 concerns for [Y%] of population"
- message_test: "Message A will achieve [X%] positive reception vs Message B [Y%]"
```

**Step 2.2 — Scenario Design Prompt:**
```
You are designing PopScale scenarios from a hypothesis register.

HYPOTHESIS REGISTER:
{hypothesis_register_content}

POPULATION SPEC:
{population_spec_content}

For each hypothesis, generate a PopScale scenario:

---
SCENARIO ID: S{N}
LINKED HYPOTHESIS: H{N}
QUESTION: [The exact question the synthetic population will answer]
CONTEXT: [2–4 sentences of context that frames the question without leading the answer]
OPTIONS: [List of 3–6 options; last option should always be "None of the above / Unsure"]
DOMAIN: consumer | policy | political
RUN TIER: DEEP | SIGNAL | VOLUME
RUN ORDER: {N} (lower = run first; run screening scenarios before depth)
EXPECTED IF CONFIRMED: [What the distribution would look like if hypothesis is true]
EXPECTED IF DISCONFIRMED: [What it would look like if false]
---

SCENARIO DESIGN RULES:
- Question must be answerable by a single person making a single choice
- Context must not reveal expected answer
- Options must be mutually exclusive and exhaustive
- VOLUME tier for prevalence screening; SIGNAL for direction; DEEP for final validation
- Run order: lower-cost screening scenarios first
```

**Step 2.3 — Stage 2 Critic:**
```
You are the Stage 2 Critic. Review this hypothesis register and scenario design.

HYPOTHESIS REGISTER:
{hypothesis_register_content}

SCENARIO DESIGNS:
{scenario_designs_content}

Check each criterion:
1. COVERAGE: Is every study objective covered by at least one hypothesis?
2. TESTABILITY: Are all hypotheses testable via the scenario types assigned?
3. RANGE VALIDITY: Are expected ranges plausible (not 0–100%, not single-point)?
4. QUESTION NEUTRALITY: Is any scenario question leading?
5. SEQUENCE BIAS: Could running scenario S{N} before S{M} prime responses?
6. COST SANITY: Is the total estimated cost within budget cap?

VERDICT: PASS or FAIL
REQUIRED CHANGES: [bullet list if FAIL]
```

**File writes:**
- `hypothesis_register.md`
- `scenario_designs.md`
- Update `study_state.json`

---

### Stage 3: Population Simulation

**Trigger:** `niobe stage3`

**Pre-condition:** `hypotheses_approved AND scenarios_approved`

**Step 3.1 — Pre-Simulation Check Display:**
```
## Pre-Simulation Check

Study: {study_name}
Population: {n_personas} personas ({state})
Generation: {standard|seeded} (seeds: {seed_count if seeded})
Scenarios: {n_scenarios} to run

Estimated costs:
  Generation:  ${generation_estimate}
  Simulation:  ${simulation_estimate} (total across {n_scenarios} scenarios)
  Total:        ${total_estimate}
  Budget cap:   ${budget_cap_usd}

Proceed? (yes / no)
```

If user confirms: begin simulation.

**Step 3.2 — Generation (if cohort not yet generated):**
```python
if not cohort_already_generated:
    request = NiobeStudyRequest(
        study_name=study_name,
        state=state,
        n_personas=n_personas,
        domain=domain,
        research_question=research_question,
        # scenario fields will be filled per scenario run
        stratify_by_religion=stratify_by_religion,
        stratify_by_income=stratify_by_income,
        budget_cap_usd=budget_cap_usd,
        use_seeded_generation=(n_personas > 300),
        seed_count=200,
    )
    cohort_result = await run_niobe_study(request)
    # cache cohort personas for reuse across scenario runs
```

**Step 3.3 — Scenario Execution Loop:**
```
For each scenario in scenario_designs (by run_order):
  Display: "Running scenario {S_ID}: {scenario_question[:50]}..."
  Call: run_niobe_study() with pre-built cohort + this scenario's question/context/options
  Write: population_runs/run_{S_ID}.json
  Display: "  ✓ {n_delivered}/{n_personas} delivered | cost: ${cost_actual} | {top_option}: {pct}%"
  Update: study_state.json
```

**Step 3.4 — Stage 3 Critic:**
```
You are the Stage 3 Critic. Review these simulation results.

SCENARIO DESIGNS:
{scenario_designs_content}

SIMULATION RESULTS SUMMARY:
{for each run: scenario_id, n_delivered, success_rate, top_option, distribution_summary}

Check:
1. DELIVERY RATE: Did any scenario deliver <80% of requested personas?
2. DISTRIBUTION VALIDITY: Are any distributions suspiciously flat (all options within 5pp)?
3. CI WIDTH: Are confidence intervals too wide (>30pp) to support findings?
4. CIRCUIT BREAKER: Did any run trip the circuit breaker? Why?
5. SURPRISE SIGNALS: Are any surprise results flagged by PopScale's analytics?

VERDICT: PASS or FAIL
REQUIRED CHANGES: [e.g. rerun S03 with larger N; check circuit breaker cause]
```

**File writes:**
- `population_runs/run_{S_ID}.json` (one per scenario)
- Update `study_state.json`

---

### Stage 4: Population Synthesis

**Trigger:** `niobe stage4`

**Pre-condition:** `runs_confirmed`

**Step 4.1 — Findings Generation Prompt (per hypothesis):**
```
You are synthesizing population simulation results into a research finding.

HYPOTHESIS:
{hypothesis_content}

SIMULATION RESULT FOR THIS HYPOTHESIS:
Scenario: {scenario_question}
Distribution: {option: pct% (CI: ±X%) for each option}
Top drivers: {driver_1 (effect: X), driver_2 (effect: Y), ...}
Surprises: {surprise_list or "none flagged"}
Segment breakdown: {key cross-tabs if available}

POPULATION BRIEF (for context):
{population_brief_content}

Generate a Population Finding with these exact sections:

## HEADLINE
[One sentence: the most important thing the data shows]

## VERDICT
CONFIRMED | PARTIALLY_CONFIRMED | REFUTED | INCONCLUSIVE
[One sentence explaining why]

## WHAT THE DATA SHOWS
[2–3 sentences describing the distribution. Lead with the number. "X% of the simulated population chose Y..."]

## WHAT DRIVES IT
[2–3 sentences on the top 1–2 drivers and their effect sizes]

## WHAT IS SURPRISING
[1–2 sentences. If nothing is surprising, say so explicitly — do not invent surprises]

## BUSINESS IMPLICATION
[1–2 sentences: what should the decision-maker do or consider differently because of this finding?]

RULES:
- Lead every section with a number or a direct claim. No hedging preamble.
- CI must be stated in WHAT THE DATA SHOWS if relevant.
- Business implication must name a specific action, not a general observation.
- If verdict is INCONCLUSIVE, explain what additional data would resolve it.
```

**Step 4.2 — Cross-Scenario Synthesis Prompt:**
```
You are synthesizing cross-scenario findings for a Niobe population study.

INDIVIDUAL FINDINGS:
{all_findings_content}

HYPOTHESIS REGISTER:
{hypothesis_register_content}

STUDY OBJECTIVES:
{objectives_list}

Generate:

## CROSS-SCENARIO THEMES
[2–3 themes that appear across multiple findings. Each theme: headline + 2 sentences of synthesis]

## OBJECTIVE COVERAGE
For each study objective: ANSWERED | PARTIALLY_ANSWERED | UNANSWERED
[If unanswered: why, and what would answer it]

## TANDEM CANDIDATES
[List 0–3 segments where Niobe found a clear "what" but not the "why".
For each: segment label, what Niobe found, what Morpheus should investigate]

## CONFIDENCE SUMMARY
[One sentence per finding: HIGH / MEDIUM / LOW confidence, and why]
```

**Step 4.3 — Stage 4 Critic:**
```
You are the Stage 4 Synthesis Critic. This is the most important Critic in the pipeline.

POPULATION FINDINGS:
{all_findings_content}

CROSS-SCENARIO SYNTHESIS:
{cross_scenario_content}

Check:
1. PRECISION CLAIMS: Does any finding claim stronger precision than the CI supports?
2. SMALL SAMPLES: Are any cross-tab findings based on sub-samples smaller than 50 personas?
3. ACTIONABILITY: Does every finding's Business Implication name a specific action?
4. SURPRISE VALIDITY: Are flagged surprises genuine or artifacts of an implausible prior?
5. TANDEM JUSTIFICATION: Is each tandem candidate justified by a real gap (what/why split)?
6. INTERNAL CONSISTENCY: Do any findings contradict each other without explanation?

For each finding, rate: ACTIONABLE: YES | NO

VERDICT: PASS or FAIL
PASS requires: ≥70% of findings are ACTIONABLE: YES
REQUIRED CHANGES: [per finding if needed]
```

**File writes:**
- `population_findings.md`
- `tandem/tandem_candidates.md`
- Update `study_state.json`

---

### Stage 5: Deliverable & Handoff

**Trigger:** `niobe stage5`

**Pre-condition:** `findings_approved`

**Step 5.1 — Sponsor Lens Selection:**
```
Which deliverable format?

1. PM Decision Tree — "What should we build / not build?"
2. CEO Strategic Options — "Where do we play, and how do we win?"
3. Investor Market Validation — "How big is this, and do people want it?"
4. Brand Campaign Brief — "What messages land, and with whom?"
5. General Executive — "What does our target population think and do?"

Enter 1–5:
```

**Step 5.2 — Deliverable Generation Prompt:**
```
You are generating a client deliverable for a Niobe population study.

SPONSOR LENS: {selected_lens}
POPULATION FINDINGS: {all_findings_content}
CROSS-SCENARIO SYNTHESIS: {cross_scenario_content}
STUDY METADATA: {study_name, geography, n_personas, date}

Generate a deliverable with these sections:

## Executive Summary
[3–5 bullet points. Lead with the most important finding. Each bullet: one number + one implication.]

## Segment Map
[Visual-text description of 3–5 key segments: label, size (%), key behavioral trait]

## Key Findings
[One section per finding, formatted for {sponsor_lens}:
 - PM lens: frame as "build/don't build" recommendations
 - CEO lens: frame as strategic options with evidence
 - Investor lens: frame as market validation evidence
 - Brand lens: frame as message effectiveness + target segments
 - General lens: frame as descriptive population intelligence]

## Distribution Tables
[For each scenario: question, option distribution with CIs, sample size]

## What's Surprising
[Top 3 surprise findings from PopScale analytics. Each: headline + 1 sentence explanation]

## Tandem Recommendations
[If tandem candidates exist: "For deeper investigation, we recommend a Morpheus study on X segment to understand Y"]

## Methodology Note
Study: {study_name}
Date: {date}
Population: {n_personas} synthetic agents ({geography})
Generation: {standard|seeded generation approach}
Simulation tier: {tier}
Important: This study uses synthetic agents calibrated to real demographic distributions.
Findings represent simulated behavioral patterns, not direct survey responses.
```

**Step 5.3 — Segment Brief Generation (for each tandem candidate):**
```json
{
  "segment_label": "{label from tandem_candidates}",
  "population_size_estimate": "{pct}% of {market_size_estimate} = ~{N}",
  "behavioral_profile": {
    "decision_driver": "{top driver from PopScale analytics}",
    "key_constraint": "{what stops them}",
    "response_to_message": "{how they responded to scenarios}"
  },
  "population_finding": "{headline from related finding}",
  "population_statistics": {
    "segment_size_pct": "{N}%",
    "ci_95": "±{X}pp",
    "key_distribution": "{option}: {pct}%"
  },
  "deep_question": "{what Niobe cannot answer — requires Morpheus depth}",
  "recommended_morpheus_hypotheses": [
    "{hypothesis 1 in Morpheus format}",
    "{hypothesis 2}",
    "{hypothesis 3}"
  ],
  "niobe_study_ref": "{study_id}",
  "generated_at": "{ISO timestamp}"
}
```

**Step 5.4 — Stage 5 Critic:**
```
You are the Stage 5 Deliverable Critic.

DELIVERABLE:
{deliverable_content}

SEGMENT BRIEFS:
{segment_briefs_content}

Check:
1. LENS MATCH: Does the framing match the selected sponsor lens?
2. CI PRESENCE: Are all distribution tables showing CIs?
3. METHODOLOGY ACCURACY: Is the methodology note accurate?
4. SEGMENT BRIEF SPECIFICITY: Is each Segment Brief specific enough for Morpheus to act on?
5. EXECUTIVE SUMMARY NUMBERS: Does every bullet point in the executive summary contain a number?

VERDICT: PASS or FAIL
REQUIRED CHANGES: [bullet list if FAIL]
```

**File writes:**
- `deliverable.md`
- `tandem/segment_brief_{N}.json` (one per tandem candidate)
- Update `study_state.json` → `STUDY_COMPLETE`

---

## 5. Study State Management

### study_state.json Schema
```json
{
  "study_id": "NBS_YYYYMMDD_{client}_{version}",
  "study_name": "string",
  "domain": "consumer | policy | political | india_general",
  "state": "string (geography)",
  "n_personas": "int",
  "current_stage": "int (1–5)",
  "status": "CREATED | STAGE{N}_IN_PROGRESS | STAGE{N}_COMPLETE | STAGE{N}_BLOCKED | STUDY_COMPLETE",
  "gates": {
    "brief_approved": false,
    "spec_approved": false,
    "hypotheses_approved": false,
    "scenarios_approved": false,
    "runs_confirmed": false,
    "findings_approved": false,
    "deliverable_approved": false
  },
  "artifacts": {
    "population_brief": "population_brief.md | null",
    "population_spec": "population_spec.json | null",
    "hypothesis_register": "hypothesis_register.md | null",
    "scenario_designs": "scenario_designs.md | null",
    "population_runs": [],
    "population_findings": "population_findings.md | null",
    "tandem_candidates": "tandem/tandem_candidates.md | null",
    "segment_briefs": [],
    "deliverable": "deliverable.md | null"
  },
  "cohort_cache": {
    "generated": false,
    "persona_ids": [],
    "generation_cost_usd": 0.0,
    "generation_approach": "standard | seeded",
    "seed_count": null
  },
  "cost_actual_usd": 0.0,
  "budget_cap_usd": 100.0,
  "created_at": "ISO8601",
  "updated_at": "ISO8601"
}
```

### State Read/Write Pattern
```python
import json
from pathlib import Path

def load_state(study_dir: str) -> dict:
    path = Path(study_dir) / "study_state.json"
    if not path.exists():
        raise FileNotFoundError(f"No study state at {study_dir}")
    return json.loads(path.read_text())

def save_state(study_dir: str, state: dict) -> None:
    path = Path(study_dir) / "study_state.json"
    state["updated_at"] = datetime.utcnow().isoformat() + "Z"
    path.write_text(json.dumps(state, indent=2))
```

---

## 6. Niobe Rules (Non-Negotiable)

These are enforced in the SKILL.md. Never override them.

1. **Gate enforcement:** No stage proceeds without the previous stage's gate passing. Gates are in `study_state.json`. They cannot be bypassed by user request.
2. **Critic is never skipped:** Every stage runs the Critic before advancing. If user says "skip critic", refuse.
3. **No number without CI:** Any finding that states a percentage must state its confidence interval.
4. **Tandem is auto-triggered, opt-out:** If tandem candidates are identified in Stage 4, Segment Briefs are generated in Stage 5 automatically. User can discard them, but they are not opt-in.
5. **Scope boundary is enforced:** If a user's research question is a depth question ("why does segment X feel this way"), Niobe must say so and suggest Morpheus.
6. **Cohort is cached:** Once personas are generated for a study, they are reused for all scenario runs. Never regenerate the same cohort.
7. **Methodology note is mandatory:** Every deliverable contains the methodology note. It cannot be removed.
8. **No external knowledge injection:** Findings must be grounded in simulation results. Niobe cannot invent statistics not present in PopScale output.
9. **Budget cap is hard:** If estimated cost exceeds budget_cap_usd, Stage 3 does not run without explicit user confirmation.
10. **State is the source of truth:** If `study_state.json` says Stage 2 is complete, it is. Never re-derive state from file presence.

---

## 7. Morpheus Integration (SKILL.md Updates Required)

### Morpheus → Niobe flag (`--from-morpheus`)
Add to Morpheus SKILL.md's `deliver` and `evidence` commands:

```
morpheus deliver --to-niobe
```
Generates `from_morpheus/hypothesis_list_{study_id}.json` in the current study directory.

Add to Niobe SKILL.md's `stage1` command:
```
niobe stage1 --from-morpheus [path/to/hypothesis_list.json]
```
Pre-populates Stage 1 with directional hypotheses reframed as distributional hypotheses.

### Niobe → Morpheus flag (`--from-niobe`)
Add to Morpheus SKILL.md's `stage1` command:
```
morpheus stage1 --from-niobe [path/to/segment_brief.json]
```
Pre-populates Stage 1 with segment description, behavioral profile, and recommended hypotheses from Niobe's Segment Brief.

---

## 8. Build Sequence

### Phase 1 (Week 1): SKILL.md Scaffold + Status + State Management
**Deliverable:** `niobe help`, `niobe status`, `niobe discard-brief` work end-to-end.

Tasks:
- [ ] Create `~/.claude/skills/simulatte-niobe/SKILL.md`
- [ ] Implement `niobe help` (prints all 23 commands)
- [ ] Implement `niobe status` (reads study_state.json, displays current state)
- [ ] Implement `niobe discard-brief` (resets Stage 1 state)
- [ ] Implement `load_state()` / `save_state()` helpers
- [ ] Write test: create study_state.json, call status, verify output

**Acceptance:** `niobe status` on a fresh study dir shows "No study found. Run 'niobe stage1' to begin."

### Phase 2 (Week 2): Stage 1 — Population Intake
**Deliverable:** `niobe stage1` generates brief + spec, runs Critic, gates.

Tasks:
- [ ] Implement Stage 1 brief generation prompt
- [ ] Implement PopulationSpec display (call `calibrate()`, render segment table)
- [ ] Implement Stage 1 Critic (5 criteria, PASS/FAIL verdict)
- [ ] Implement gate logic (set `brief_approved`, `spec_approved`)
- [ ] Write `population_brief.md` and `population_spec.json`
- [ ] Write test: stage1 with valid input → both files exist, gates are true

**Acceptance:** Critic PASS rate ≥ 85% on 5 test inputs.

### Phase 3 (Week 3): Stage 2 — Hypothesis & Scenario Design
**Deliverable:** `niobe stage2` generates hypotheses, scenario designs, Critic, gates.

Tasks:
- [ ] Implement hypothesis generation prompt (6 types, numeric ranges)
- [ ] Implement scenario design prompt (question, context, options, tier, run_order)
- [ ] Implement Stage 2 Critic (6 criteria)
- [ ] Implement gate logic
- [ ] Write `hypothesis_register.md` and `scenario_designs.md`
- [ ] Write test: stage2 with approved brief → 6–10 hypotheses, all cover objectives

**Acceptance:** All objectives covered, no leading questions, cost within budget.

### Phase 4 (Week 4): Stage 3 — Population Simulation
**Deliverable:** `niobe stage3` runs all scenarios via PopScale, displays progress, gates.

Tasks:
- [ ] Implement pre-simulation cost display + confirmation prompt
- [ ] Implement cohort generation (seeded if n > 300, cache cohort)
- [ ] Implement scenario execution loop (run in run_order, write per-run JSON)
- [ ] Implement Stage 3 Critic (delivery rate, distribution validity, CI width)
- [ ] Implement gate logic
- [ ] Write test (mocked PopScale): stage3 with 2 scenarios → 2 run files, gates true

**Acceptance:** End-to-end test with real PopScale call: `n_delivered > 0`.

### Phase 5 (Week 5): Stage 4 — Population Synthesis
**Deliverable:** `niobe stage4` synthesizes findings, cross-scenario themes, tandem candidates, Critic, gates.

Tasks:
- [ ] Implement per-hypothesis finding generation prompt
- [ ] Implement cross-scenario synthesis prompt
- [ ] Implement tandem candidate identification logic
- [ ] Implement Stage 4 Critic (actionability rating per finding, ≥70% ACTIONABLE: YES)
- [ ] Write `population_findings.md` and `tandem/tandem_candidates.md`
- [ ] Write test: stage4 with 3 mock run results → findings file exists, ≥1 finding is CONFIRMED or REFUTED

**Pre-ship gate:** Run Stage 4 on 3 real PopScale outputs. ≥70% findings must be ACTIONABLE: YES before shipping.

### Phase 6 (Week 6): Stage 5 — Deliverable & Handoff
**Deliverable:** `niobe stage5` generates deliverable, Segment Briefs, Critic, STUDY_COMPLETE.

Tasks:
- [ ] Implement sponsor lens selection prompt
- [ ] Implement deliverable generation prompt (5 lens templates)
- [ ] Implement Segment Brief generation (for each tandem candidate)
- [ ] Implement Stage 5 Critic
- [ ] Write `deliverable.md` and `tandem/segment_brief_{N}.json`
- [ ] Set status to `STUDY_COMPLETE`
- [ ] Write test: stage5 → deliverable.md exists, methodology note present, all CIs shown

**Acceptance:** ≥80% of deliverables require no revision before client use (test on 3 real studies).

### Phase 7 (Week 7): Tandem Protocol + Morpheus Updates
**Deliverable:** `niobe tandem`, `niobe --from-morpheus`, `morpheus --from-niobe`, `morpheus deliver --to-niobe`.

Tasks:
- [ ] Implement `niobe tandem` command (generate all Segment Briefs that meet criteria)
- [ ] Implement `niobe stage1 --from-morpheus [file]` (pre-populate from Hypothesis List)
- [ ] Update Morpheus SKILL.md: add `morpheus stage1 --from-niobe [file]`
- [ ] Update Morpheus SKILL.md: add `morpheus deliver --to-niobe`
- [ ] Write tandem integration test: Morpheus hypothesis list → Niobe stage1 pre-populate

### Phase 8 (Week 8): Remaining Commands + Hardening
**Deliverable:** All 23 commands functional, end-to-end tests passing.

Tasks:
- [ ] Implement `niobe probe [segment]`
- [ ] Implement `niobe compare [s_a] [s_b]`
- [ ] Implement `niobe rerun [scenario_id]`
- [ ] Implement `niobe estimate`
- [ ] Implement `niobe scale [n]`
- [ ] Implement `niobe audit` + `niobe correct`
- [ ] Implement `niobe onboard`
- [ ] Implement `niobe counterfactual [dimension]`
- [ ] Implement `niobe calibrate` (hooks into Delhi 2025 benchmark)
- [ ] Implement `niobe evolve`
- [ ] End-to-end test: full pipeline, real PopScale, asserts `n_delivered > 0` and `STUDY_COMPLETE`

---

## 9. End-to-End Acceptance Test

This test must pass before Niobe v1 ships:

```python
# tests/test_e2e_niobe.py

async def test_full_niobe_study():
    """End-to-end test: full study pipeline with real PopScale."""
    study_dir = "/tmp/niobe_e2e_test"
    
    # Stage 1
    result = await run_niobe_cli("stage1", study_dir, 
        research_question="Do Delhi consumers prefer convenience over price for food delivery?",
        state="delhi", n_personas=100, domain="consumer", budget_cap_usd=30.0)
    assert state["gates"]["brief_approved"]
    assert state["gates"]["spec_approved"]
    
    # Stage 2
    result = await run_niobe_cli("stage2", study_dir)
    assert state["gates"]["hypotheses_approved"]
    assert state["gates"]["scenarios_approved"]
    assert len(hypotheses) >= 3
    
    # Stage 3
    result = await run_niobe_cli("stage3", study_dir)
    assert state["gates"]["runs_confirmed"]
    # THE CRITICAL ASSERTION
    total_delivered = sum(r["n_delivered"] for r in state["artifacts"]["population_runs"])
    assert total_delivered > 0, f"No personas delivered — PopScale pipeline broken"
    
    # Stage 4
    result = await run_niobe_cli("stage4", study_dir)
    assert state["gates"]["findings_approved"]
    findings = load_findings(study_dir)
    assert len(findings) >= 3
    
    # Stage 5
    result = await run_niobe_cli("stage5", study_dir, sponsor_lens="General Executive")
    assert state["status"] == "STUDY_COMPLETE"
    assert Path(study_dir, "deliverable.md").exists()
    
    print(f"✓ End-to-end test passed. Total delivered: {total_delivered}. Cost: ${state['cost_actual_usd']:.2f}")
```

---

## 10. PopScale Dependency: One Remaining Gap

**Gap:** If `invoke_persona_generator` raises an unhandled exception at the orchestrator level (auth failure, PG crash), the entire study halts with no recovery.

**Fix location:** `popscale/generation/calibrated_generator.py` and `seeded_calibrated_generator.py` at the **cohort level** (wrapping the full generation call).

**Fix:** Add a study-level exception boundary in `popscale/orchestrator/study_runner.py`:
```python
try:
    cohort_result = await run_calibrated_generation(spec, ...)
except Exception as exc:
    logger.error("Cohort generation failed: %s: %s", type(exc).__name__, exc)
    return StudyResult(
        run_id=run_id,
        config=config,
        status="GENERATION_FAILED",
        error=str(exc),
        cost_actual_usd=0.0,
    )
```

This ensures PopScale returns a structured failure rather than an unhandled exception when PG's orchestrator is down.

---

## 11. 10,000-Persona Study Plan

### Prerequisites (all already built)
- Seeded generation: VariantGenerator + SeedCalibrator (production-ready)
- Sharded execution: 50/shard × 20 concurrent (production-ready)
- Response cache: SHA256 per persona×scenario (production-ready)
- Circuit breaker: pause + backoff on fallback rate >10% (production-ready)

### Recommended Configuration
```python
NiobeStudyRequest(
    n_personas=10_000,
    use_seeded_generation=True,
    seed_count=200,          # 200 deep, 9800 variants via Haiku
    simulation_tier="VOLUME", # for screening; upgrade to SIGNAL for key scenarios
    budget_cap_usd=900.0,
)
```

### Cost Breakdown
| Phase | Cost |
|---|---|
| 200 deep seed personas | $60 |
| 9,800 variants (Haiku) | $39 |
| 8 scenarios × 10k personas at VOLUME | ~$800 |
| **Total** | **~$899** |

### Infrastructure Requirement
- Shard size: 50 personas/shard
- Concurrent shards: 20
- Total shards per scenario: 200
- Sequential scenario runs (to avoid rate limiting)
- Response cache enabled (deduplicate across scenario runs on same cohort)
- Estimated wall-clock time per scenario: ~45 min at VOLUME tier

### Recommended Approach for First 10K Study
1. Start with `niobe estimate --n 10000` to confirm cost
2. Run generation first separately: `niobe stage3 --generation-only` (generate + cache cohort)
3. Run scenarios in two waves: screening (VOLUME, all 8 scenarios), then depth (SIGNAL, top 3)
4. Use `niobe scale 10000` to compare against a prior 500-persona study before committing

---

*Niobe Build Specification v2.0 — 2026-04-16*  
*Simulatte Research Platform*
