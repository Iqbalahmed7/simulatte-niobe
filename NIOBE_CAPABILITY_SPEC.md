# Niobe — Capability Specification
## Population Research Orchestrator — Steady-State North Star

**Version:** 1.0  
**Date:** 2026-04-16  
**Status:** Authoritative. This document defines what Niobe does when fully built.  
**Relationship:** Niobe is to population studies what Morpheus is to deep personas. Same methodology discipline. Different resolution.

---

## 1. The Core Analogy

| Morpheus | Niobe |
|---|---|
| 6–12 calibrated synthetic personas | 500–10,000 synthetic agents |
| Depth: inner world, narrative, contradiction | Breadth: distributions, prevalence, segmentation |
| Produces: hypothesis verdicts, verbatim evidence, archetypes | Produces: distributions, segment maps, driver rankings, surprises |
| Answers: "Why does this segment behave this way?" | Answers: "How many people behave this way, and why?" |
| Currency: quotes and contradictions | Currency: percentages and confidence intervals |
| Handoff: sends Segment Briefs to Niobe | Handoff: sends Hypothesis Lists to Morpheus |

**The rule:** If the question has a "how many" or "what proportion" in it — Niobe. If the question has a "why" or "what drives" in it — Morpheus. Most real research questions have both. That is what the tandem protocol is for.

---

## 2. What Niobe Produces (The Eight Artifacts)

Every Niobe study produces exactly these artifacts, in order:

### 2.1 Population Brief
A structured specification of the research question translated into simulation-ready parameters.

```
study_name, research_question, decision_context, study_objectives (3–5),
target_population definition, market_size_estimate, domain (consumer/policy/political),
geography, n_personas, generation_approach (standard/seeded), budget_cap_usd
```

### 2.2 Population Spec
The demographic distribution that PopScale's calibrator will use to generate the synthetic cohort.

```
state/geography, age_range, urban_pct, stratification (religion × income),
segment_map: [{label, proportion, anchor_overrides}],
estimated_cost, generation_tier
```

### 2.3 Hypothesis Register
6–10 distributional hypotheses, each testable by a PopScale scenario run.

```
id, type (prevalence/distribution/cross_tab/comparative/issue_salience/message_test),
statement, expected_range (numeric bounds), linked_objective, priority (HIGH/MED/LOW)
```

### 2.4 Scenario Designs
PopScale Scenario objects mapped from hypotheses, with run order and cost.

```
scenario_id, linked_hypothesis_id, question, context, options, domain,
run_tier (DEEP/SIGNAL/VOLUME), run_order, expected_if_confirmed, expected_if_disconfirmed,
estimated_cost_usd
```

### 2.5 Population Runs
Records of executed PopScale simulations. One run per scenario design.

```
scenario_id, run_id, status (pending/running/complete/failed),
n_personas, n_delivered, cost_actual_usd,
segmentation_result, distribution_result, driver_result, surprise_result
```

### 2.6 Population Findings
Narrative synthesis of distributional data. One finding per hypothesis.

```
hypothesis_id, headline, verdict (CONFIRMED/PARTIALLY_CONFIRMED/REFUTED/INCONCLUSIVE),
what_the_data_shows, what_drives_it, what_is_surprising, business_implication,
confidence_interval, supporting_runs []
```

### 2.7 Segment Brief (→ Morpheus)
Niobe's handoff to Morpheus when a population finding identifies a segment worth deep investigation.

```
segment_label, population_size_estimate, behavioral_profile {},
population_finding_ref, deep_question,
recommended_morpheus_hypotheses []
```

### 2.8 Client Deliverable
Synthesized findings rendered for a specific sponsor lens.

```
sponsor_lens (PM Decision Tree / CEO Strategic Options / Investor Market Validation /
              Brand Campaign Brief / General Executive),
executive_summary, segment_map, distribution_tables, driver_rankings,
surprise_findings, tandem_recommendations, methodology_note
```

---

## 3. The Five Stages

### Stage 1 — Population Intake
**Trigger:** `niobe stage1`  
**Input:** Business question, geography, domain, population size  
**Process:** Generate Population Brief → Critic review → Generate Population Spec → gate  
**Gate:** `brief_approved AND spec_approved`  
**Output files:** `population_brief.md`, `population_spec.json`

### Stage 2 — Hypothesis & Scenario Design
**Trigger:** `niobe stage2`  
**Input:** Approved brief + spec  
**Process:** Generate hypothesis register → Critic review → Map to scenario designs → cost estimate → gate  
**Gate:** `hypotheses_approved AND scenarios_approved`  
**Output files:** `hypothesis_register.md`, `scenario_designs.md`

### Stage 3 — Population Simulation
**Trigger:** `niobe stage3`  
**Input:** Approved scenarios + population spec  
**Process:** Pre-simulation check → Run each scenario via PopScale → quality review → Critic review → gate  
**Gate:** `runs_confirmed (success_rate ≥ 0.8 AND n_delivered ≥ n_requested × 0.8)`  
**Output files:** `population_runs/run_{scenario_id}.json` (one per scenario)

### Stage 4 — Population Synthesis
**Trigger:** `niobe stage4`  
**Input:** Completed runs + hypothesis register + population brief  
**Process:** Generate findings per hypothesis → cross-scenario synthesis → identify tandem candidates → Critic review → gate  
**Gate:** `findings_approved`  
**Output files:** `population_findings.md`, `tandem/tandem_candidates.md`

### Stage 5 — Deliverable & Handoff
**Trigger:** `niobe stage5`  
**Input:** Approved findings + tandem recommendations  
**Process:** Select sponsor lens → generate deliverable sections → generate Segment Briefs → optional DOCX export  
**Gate:** `deliverable_approved`  
**Output files:** `deliverable.md`, `tandem/segment_brief_{N}.json`, optional `deliverable.docx`

---

## 4. Full Command Set (Steady State)

### Pipeline Commands
| Command | What It Does |
|---|---|
| `niobe stage1` | Run Population Intake: generate brief + spec, Critic review, gate |
| `niobe stage2` | Run Hypothesis & Scenario Design, gate |
| `niobe stage3` | Run Population Simulation across all approved scenarios |
| `niobe stage4` | Run Population Synthesis: findings per hypothesis, cross-scenario |
| `niobe stage5` | Generate deliverable + Segment Briefs, optional DOCX |

### Research Operations
| Command | What It Does |
|---|---|
| `niobe probe [segment_label]` | Deep-dive a specific segment: re-run scenario filtered to that segment only, generate focused findings |
| `niobe compare [scenario_a] [scenario_b]` | Side-by-side comparison of two scenario runs: distribution deltas, cross-tab, driver overlap |
| `niobe rerun [scenario_id]` | Re-run a specific scenario (e.g. after updating context or options) |
| `niobe estimate` | Cost estimate for current study config before running Stage 3 |
| `niobe scale [n]` | What would this study cost and show at N personas? |

### Project Health
| Command | What It Does |
|---|---|
| `niobe status` | Show current study state, stage, gates, next action |
| `niobe audit` | Evaluate study health: coverage gaps, hypothesis quality, data sparsity, tandem readiness |
| `niobe correct` | Execute remediation actions from audit findings |
| `niobe onboard` | Retroactively create study state from existing artifacts (e.g. importing a PopScale result) |

### Deliverables & Analysis
| Command | What It Does |
|---|---|
| `niobe deliver` | Generate or re-generate client deliverable (prompts for sponsor lens) |
| `niobe segment [label]` | Generate or update a Segment Brief for the named segment |
| `niobe tandem` | Generate all Segment Briefs that meet tandem criteria; write to `tandem/` |

### Morpheus Integration
| Command | What It Does |
|---|---|
| `niobe --from-morpheus [brief_file]` | Start a Niobe study seeded from a Morpheus Hypothesis List |
| `niobe --to-morpheus` | Generate Segment Briefs in Morpheus-readable format and log handoff |

### Scale & Advanced
| Command | What It Does |
|---|---|
| `niobe counterfactual [dimension]` | What if the population were older / more urban / different income mix? Re-run with modified spec |
| `niobe calibrate` | Run a calibration study against known ground truth (e.g. election results, published survey) |
| `niobe evolve` | Self-assess: what did this study reveal about Niobe's own capability gaps? |
| `niobe discard-brief` | Reject current brief/spec and restart Stage 1 |

### Meta
| Command | What It Does |
|---|---|
| `niobe help` | Display all commands with one-line descriptions |
| `niobe [stage] --dry-run` | Show what a stage would do without making API calls |

**Total: 23 commands** across 6 categories.

---

## 5. Critic Framework

Every stage has a Critic pass before the gate. The Critic is a separate LLM call with constrained context.

### Stage 1 Critic — Brief & Spec Quality
- Is the population spec demographically representative for this geography?
- Is market size sourced or assumed?
- Are study objectives testable at population scale (not requiring depth)?
- Is geographic scope appropriate for the research question?
- Does the brief contain any claims that require Morpheus, not Niobe?

### Stage 2 Critic — Hypothesis & Scenario Quality
- Are any hypotheses untestable with the chosen scenario types?
- Are expected ranges implausibly narrow or wide given prior knowledge?
- Is any scenario question leading (presupposes an answer)?
- Is the scenario sequence biased (priming effect across runs)?
- Are all study objectives covered by at least one hypothesis?

### Stage 3 Critic — Simulation Quality
- Did any scenario return <80% delivery rate? Why?
- Are any distributions suspiciously flat (signal = noise)?
- Are confidence intervals too wide to support findings?
- Are surprise results genuine or artifacts of naive prior?

### Stage 4 Critic — Findings Quality
- Does any finding claim stronger precision than the CI supports?
- Are any cross-tab findings based on sub-samples too small (<50)?
- Are tandem recommendations justified by the data?
- Does any finding contradict another finding without explanation?
- Is every finding's business implication explicit and actionable?

### Stage 5 Critic — Deliverable Quality
- Does the deliverable match the sponsor lens selected?
- Are all distribution tables correctly formatted with CIs?
- Is the methodology note accurate (generation approach, n, tier)?
- Are Segment Briefs specific enough for Morpheus to act on?

---

## 6. The Tandem Protocol

Niobe and Morpheus interoperate via two handoff types:

### Niobe → Morpheus (Segment Brief)
**When:** Stage 4 synthesis identifies a segment where population data is clear but depth explanation is missing.  
**Trigger:** `niobe tandem` or auto-generated during Stage 5.  
**Format:** `tandem/segment_brief_{N}.json`

A Segment Brief contains:
- Which segment (label + size estimate + behavioral profile)
- What Niobe found (population finding reference + key statistics)
- What Niobe cannot answer (the deep question requiring personas)
- What Morpheus should hypothesize (3–5 recommended hypotheses in Morpheus format)

**Morpheus receives this via:** `morpheus stage1 --from-niobe segment_brief.json`

### Morpheus → Niobe (Hypothesis List)
**When:** Morpheus completes a study and wants to test prevalence of its directional findings.  
**Format:** `from_morpheus/hypothesis_list_{study_id}.json`

A Hypothesis List contains:
- Source study ID and summary
- Directional findings reframed as distributional hypotheses
- Recommended scenario types and priority

**Niobe receives this via:** `niobe stage1 --from-morpheus hypothesis_list.json`

### Reconciliation Rule
When Niobe and Morpheus contradict each other on the same question (e.g. Morpheus: "credential specificity is the gate"; Niobe: "only 22% prioritize it"), neither is wrong. Morpheus found it in depth for a specific segment. Niobe measured its population prevalence. The deliverable must contain a **Reconciliation Note** explaining both findings in context.

---

## 7. Geography & Domain Coverage

### Supported Geographies (46 profiles)
**India (24):** West Bengal, Maharashtra, Uttar Pradesh, Bihar, Tamil Nadu, Karnataka, Rajasthan, Delhi, Gujarat, Kerala, Punjab, Telangana, Andhra Pradesh, Madhya Pradesh, Odisha, Assam, Jharkhand, Chhattisgarh, Uttarakhand, Himachal Pradesh, Haryana, Goa, Jammu & Kashmir, India (national)

**USA (16):** National, Northeast, South, Midwest, West, California, Texas, New York, Florida, Illinois, Pennsylvania, Ohio, Georgia, North Carolina, Washington, Colorado, Arizona, Michigan, New Jersey, Massachusetts, Virginia

**UK (1):** United Kingdom

**Europe (6):** France, Germany, Spain, Italy, Netherlands, Poland, Sweden

### Supported Domains
| Domain | Population Framing |
|---|---|
| `consumer` | Purchase decisions, brand preference, price sensitivity, adoption |
| `policy` | Regulatory attitudes, compliance, public opinion, service usage |
| `political` | Voting intention, party identification, issue salience |
| `india_general` | General India population (auto-routes to appropriate sub-domain) |

### Religion Stratification
- India profiles: `stratify_by_religion=True` applies census-calibrated religion × income cross-stratification
- US/UK/EU profiles: `stratify_by_religion=True` is a silent no-op (income stratification used instead)

---

## 8. Scale & Cost Model

### Generation Approaches

**Standard (full pipeline)**
- Every persona: full Persona Generator pipeline
- Cost: ~$0.30 per persona
- 500 personas = ~$150 | 1,000 = ~$300 | 10,000 = ~$3,000

**Seeded (recommended for studies >500 personas)**
- Pass 1: N_seeds deep personas via full PG pipeline (default: 200)
- Pass 2: Expand to target N via VariantGenerator (single Haiku call per variant)
- Cost: (seed_count × $0.30) + ((n_total - seed_count) × $0.004)
- 500 personas ≈ $62 | 1,000 ≈ $63 | 10,000 ≈ $93
- **Savings vs standard: 58% at 500 / 79% at 1k / 97% at 10k**

### Simulation Tiers
| Tier | Cost/persona | Use When |
|---|---|---|
| DEEP | ~$0.08 | Final/publish-grade runs, complex decision scenarios |
| SIGNAL | ~$0.04 | Hypothesis validation, direction checking |
| VOLUME | ~$0.01 | Fast prevalence checks, large-N screening |

### Typical Study Costs (seeded generation + SIGNAL simulation)
| n_personas | Scenarios | Generation | Simulation | Total |
|---|---|---|---|---|
| 500 | 3 | $62 | $60 | ~$122 |
| 1,000 | 5 | $63 | $200 | ~$263 |
| 2,000 | 6 | $66 | $480 | ~$546 |
| 10,000 | 8 | $93 | $3,200 | ~$3,293 |

### 10,000-Persona Study (Minimal Cost Path)
- Seeded generation: 200 deep seeds + 9,800 variants = **~$93 generation cost**
- Simulation: VOLUME tier for screening, SIGNAL for priority scenarios = **~$400–800**
- **Total: ~$500–900 for a 10K-persona study**
- Infrastructure requirement: sharded execution (50/shard × 20 concurrent), circuit breaker, response cache
- Recommended approach: run generation once, cache personas, run multiple scenario waves

---

## 9. Study State Machine

```
CREATED → STAGE1_IN_PROGRESS → STAGE1_COMPLETE
       → STAGE2_IN_PROGRESS → STAGE2_COMPLETE
       → STAGE3_IN_PROGRESS → STAGE3_COMPLETE
       → STAGE4_IN_PROGRESS → STAGE4_COMPLETE
       → STAGE5_IN_PROGRESS → STUDY_COMPLETE

Any stage can transition to: STAGE{N}_BLOCKED (Critic rejects)
                              STAGE{N}_IN_PROGRESS (re-attempt after correction)
```

**State persisted in:** `{study_dir}/study_state.json`

```json
{
  "study_id": "NBS_20260416_khidma_v1",
  "study_name": "...",
  "current_stage": 3,
  "status": "STAGE3_IN_PROGRESS",
  "gates": {
    "brief_approved": true,
    "spec_approved": true,
    "hypotheses_approved": true,
    "scenarios_approved": true,
    "runs_confirmed": false,
    "findings_approved": false,
    "deliverable_approved": false
  },
  "artifacts": {
    "population_brief": "population_brief.md",
    "population_spec": "population_spec.json",
    "hypothesis_register": "hypothesis_register.md",
    "scenario_designs": "scenario_designs.md",
    "population_runs": [...],
    "population_findings": "population_findings.md",
    "tandem_candidates": "tandem/tandem_candidates.md",
    "deliverable": null
  },
  "cost_actual_usd": 87.40,
  "created_at": "2026-04-16T09:00:00Z",
  "updated_at": "2026-04-16T11:23:00Z"
}
```

---

## 10. Steady-State Benchmarks

A fully-built Niobe meets these benchmarks:

| Benchmark | Target |
|---|---|
| Stage 1 brief quality | Critic PASS rate ≥ 85% on first attempt |
| Stage 2 hypothesis coverage | All study objectives covered by ≥1 hypothesis |
| Stage 3 delivery rate | n_delivered / n_requested ≥ 0.80 across scenarios |
| Stage 4 finding actionability | ≥70% of findings rated ACTIONABLE by Synthesis Critic |
| Stage 5 deliverable quality | ≥80% of deliverables require no revision before client use |
| Tandem trigger rate | ≥60% of completed studies produce at least one Segment Brief |
| Population prediction MAE | < 9.8pp vs pre-election poll baseline (Delhi 2025 benchmark) |
| Cost efficiency | 10K-persona study at ≤$900 total (seeded + VOLUME/SIGNAL) |

---

## 11. What Niobe Does NOT Do

- Niobe does not produce depth narratives, inner monologues, or character arcs — that is Morpheus.
- Niobe does not conduct structured interviews or probing sessions — that is Morpheus.
- Niobe does not adjudicate individual persona contradictions — it reports population distributions.
- Niobe does not replace census data or published surveys — it is a simulation tool, not a polling firm.
- Niobe does not guarantee causal inference — distributions show correlation structure, not causation.
- Niobe does not store or transmit real personal data — all agents are synthetic.

---

## 12. File Structure (Per Study)

```
{study_dir}/                          (e.g. pilots/khidma/niobe/)
├── study_state.json                  (state machine — source of truth)
├── population_brief.md               (Stage 1 output)
├── population_spec.json              (Stage 1 output)
├── hypothesis_register.md            (Stage 2 output)
├── scenario_designs.md               (Stage 2 output)
├── population_runs/
│   ├── run_H01_prevalence.json       (Stage 3 — one per scenario)
│   ├── run_H02_distribution.json
│   └── ...
├── population_findings.md            (Stage 4 output)
├── tandem/
│   ├── tandem_candidates.md          (Stage 4 output)
│   ├── segment_brief_1.json          (Stage 5 output — one per tandem segment)
│   └── segment_brief_2.json
├── deliverable.md                    (Stage 5 output)
└── deliverable.docx                  (Stage 5 optional export)
```

---

*Niobe Capability Specification v1.0 — 2026-04-16*  
*Simulatte Research Platform*
