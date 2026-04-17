# Niobe — V1 System Definition
## Simulatte Population Research Orchestrator

**Date:** 2026-04-14
**Status:** Converged. Build-ready.
**Inputs:** Morpheus architecture (proven) + PopScale engine (in build) + Aaru competitive analysis → This document (decisive)
**Relationship to Morpheus:** Niobe is a sibling system, not a child. It shares the tandem handoff protocol with Morpheus but has its own primitives, stages, gates, and deliverables. Morpheus asks "why." Niobe asks "how many."

---

## 1. What Niobe Is — One Sentence

Niobe is a population-level research orchestrator implemented as a Claude Code skill that sits on top of PopScale's simulation engine, transforming business questions into structured multi-scenario population studies with distributional findings — and connecting those findings to Morpheus for depth investigation when warranted.

---

## 2. Why Niobe Exists

Morpheus produces depth intelligence: 6–12 calibrated personas, hypothesis registers with binary verdicts, evidence traced to specific verbatim moments. This is the right instrument for "what does the highest-value user need at the moment of conversion." It is the wrong instrument for "what proportion of the market has this need."

PopScale produces raw population simulation output: 2,000+ synthetic agents responding to structured scenarios, with segmentation, probability distributions, key driver analysis, and surprise detection. This is infrastructure. It does not know how to design a study, sequence scenarios, interpret distributions as research findings, or produce a deliverable a client can act on.

Niobe is the research methodology layer between PopScale and the client. It does what neither PopScale nor Morpheus does:

1. **Translates business questions into population research designs** — scenario selection, hypothesis register, population specification
2. **Orchestrates multi-scenario population studies** — running the right scenarios in the right order against the right population
3. **Synthesises statistical output into research narrative** — distributions become findings, segments become strategy options, drivers become recommendations
4. **Connects to Morpheus through formal handoff** — when a population finding warrants depth investigation, Niobe generates a Segment Brief that Morpheus receives as ICP input

---

## 3. Relationship Map

```
CLIENT QUESTION
    │
    ├─── "Why does this user do X?"  ──→  MORPHEUS (depth)
    │                                        │
    │                                        │ Hypothesis List
    │                                        ▼
    ├─── "How many users do X?"  ──────→  NIOBE (breadth)
    │                                        │
    │                                        │ Segment Brief
    │                                        ▼
    │                                     MORPHEUS (depth on segment)
    │
    └─── PopScale ← engine for Niobe
         Persona Generator ← engine for both
```

**Tandem flow — two directions:**

1. **Niobe → Morpheus:** Niobe identifies a segment (e.g., "38% of population has trust anxiety around booking"). Generates a Segment Brief. Morpheus receives it as ICP input and probes: what does that trust anxiety look like, what resolves it, what triggers it.

2. **Morpheus → Niobe:** Morpheus completes a qualitative study and surfaces directional findings (e.g., "credential specificity is the conversion gate"). Generates a Hypothesis List. Niobe receives it and tests: what proportion of the full market has credential specificity as primary concern, secondary, or irrelevant.

Both directions produce higher-value output than either system alone.

---

## 4. Core Capabilities (Max 5)

### Capability 1: Population Research Design

Niobe translates a business question into a structured population study — selecting scenario types, defining the population specification, formulating distributional hypotheses, and sequencing multiple scenarios.

The researcher provides a business question and a target population. Niobe produces:
- A Population Brief (structured specification of who to simulate and what to test)
- A Distributional Hypothesis Register (what distributions and segment splits to expect)
- A Scenario Design (which PopScale scenario types to run, in what order, against which segments)

This is the population-level equivalent of Morpheus's Stages 1–3. But the primitives are different — hypotheses are distributional, not binary. Personas are population segments, not calibrated individuals. Stimuli are structured scenarios, not open-ended probes.

### Capability 2: PopScale Orchestration

Niobe invokes PopScale's engine to execute multi-scenario population studies. For each scenario in the study design:
- Configures the Population Spec for PopScale's demographic sampler
- Selects the appropriate domain framing (Consumer / Policy / Political)
- Runs the scenario against the specified population at the appropriate scale
- Collects `SimulationResult` objects and routes them to the analytics pipeline

The researcher does not interact with PopScale directly. Niobe is the interface.

### Capability 3: Population Synthesis

PopScale produces `PopScaleReport` objects — structured JSON with segments, distributions, drivers, surprises. These are data, not findings.

Niobe converts them into research narrative:
- **Segment narrative:** Who exists in this population, how large, what drives their behavior
- **Distribution narrative:** How responses spread across options, where the concentrations are, where the uncertainty is
- **Driver narrative:** Which population attributes predict which outcomes, what the effect sizes mean for the business question
- **Surprise narrative:** Where the population behaved contrary to the naive prior, what that implies
- **Cross-scenario narrative:** How responses shifted across sequential scenarios, what the deltas reveal

This synthesis is Niobe's primary value add. Without it, PopScale output requires manual interpretation by a researcher.

### Capability 4: Tandem Protocol (Morpheus ↔ Niobe)

Formal interchange between the two systems:

**Segment Brief (Niobe → Morpheus):** When Niobe identifies a population segment worth investigating in depth, it generates a structured brief that Morpheus can receive as ICP input — segment label, population size estimate, behavioral profile, the population-level finding that warrants depth, and the specific question that depth research should answer.

**Hypothesis List (Morpheus → Niobe):** When Morpheus completes a qualitative study and wants to test prevalence of its directional findings across a population, it generates a structured list that Niobe can receive as study input — each finding reframed as a distributional hypothesis with a recommended scenario type.

### Capability 5: Population Deliverable Generation

Niobe produces client-facing research output that is structurally different from Morpheus deliverables:

- **Segment Map** — visual and tabular representation of population segments with sizing
- **Distribution Tables** — response distributions with confidence intervals per scenario
- **Driver Ranking** — ranked list of population attributes that predict outcomes, with effect sizes
- **Surprise Findings** — counterintuitive results flagged and explained
- **Tandem Recommendations** — which findings warrant Morpheus depth investigation and why
- **Methodology Note** — population size, demographic calibration source, confidence range, stated limitations

The deliverable language is distributional: "38% of the population, 95% CI [34%, 42%]." Not directional: "the pattern holds across personas."

---

## 5. What Niobe Explicitly Does NOT Do

| Not in v1 | Why |
|---|---|
| Replace Morpheus for qualitative work | Niobe has no probe sessions, no evidence tracing, no verbatim citations. Depth is Morpheus's job. |
| Build or modify PopScale's engine | Niobe is an orchestration layer. It calls PopScale. It does not extend PopScale's analytics, scenario model, or cognitive loop. |
| Generate individual persona narratives | Niobe works with segments and distributions. Individual persona depth is Morpheus territory. |
| Run social simulation studies | PopScale's social loop (`run_social_loop()`) is available but Niobe v1 focuses on single-round scenario response. Multi-round temporal studies are v2. |
| Automated scenario design without researcher review | Niobe proposes scenarios. The researcher approves. No auto-pilot. |
| Cross-study population comparison | Each Niobe study is self-contained. Cross-study meta-analysis is post-v1 — same reasoning as Morpheus v1 excluding multi-project retrieval. |
| Client-facing data visualisation | Niobe produces structured data and narrative. Chart generation (bar charts, distribution curves, segment maps) is a post-v1 frontend capability — or a manual step by the researcher. |
| Electoral outcome prediction as a product claim | Niobe v1 frames electoral output as "behavioral simulation of how voters respond to the current information environment," not "vote-share prediction." The framing is epistemic, not commercial. |

---

## 6. The Primitive Set

### The 8 Primitives

| # | Primitive | Why it exists | Schema core |
|---|---|---|---|
| 1 | **Population Brief** | Structured specification of the research question, target population, and study scope. Immutable after approval. Everything traces back to this. | `business_question`, `target_population`, `market_size_estimate`, `geographic_scope`, `domain`, `population_spec` (age × geography × income × religion × custom dimensions), `study_objectives[]` |
| 2 | **Population Spec** | Demographic and attitudinal specification of the synthetic population to generate. Maps directly to PopScale's `PopulationSpec` calibrator input. | `state_code`, `n_personas`, `domain`, `age_range`, `stratification` (religion × income × urban/rural), `custom_overrides{}`, `sarvam_enabled` |
| 3 | **Distributional Hypothesis** | A testable claim about population-level distributions, segment splits, or prevalence. NOT binary (supported/refuted). Has an expected range. | `id`, `statement`, `type` (prevalence / distribution / cross-tab / comparative), `expected_range` (numeric bounds), `scenario_type` (concept_test / pricing / choice / message_test / issue_salience), `linked_objectives[]`, `population_segments_tested[]` |
| 4 | **Scenario Design** | The specific PopScale scenarios that will test each hypothesis. Maps to PopScale's `Scenario` model. Includes sequencing. | `id`, `scenario` (PopScale `Scenario` object), `target_hypotheses[]`, `population_spec_ref`, `run_order`, `expected_if_confirmed`, `expected_if_disconfirmed`, `tier` (DEEP / SIGNAL / VOLUME) |
| 5 | **Population Run** | Record of a PopScale execution — scenario, cohort, results, cost, diagnostics. Wraps `SimulationResult`. | `id`, `scenario_design_ref`, `simulation_result` (PopScale), `popscale_report` (PopScale), `run_at`, `cost_usd`, `success_rate` |
| 6 | **Population Finding** | A synthesised research finding derived from one or more Population Runs. The narrative interpretation of distributional data. | `id`, `finding_type` (segment / distribution / driver / surprise / cross_scenario), `headline`, `narrative`, `supporting_runs[]`, `confidence_statement`, `tandem_recommendation` (null / segment_brief / none) |
| 7 | **Segment Brief** | Niobe → Morpheus handoff artifact. A structured description of a population segment that warrants depth investigation. | `segment_label`, `population_size_estimate`, `behavioural_profile{}`, `population_finding_ref`, `deep_question` |
| 8 | **Hypothesis List** | Morpheus → Niobe handoff artifact. Directional findings reframed as distributional hypotheses for population testing. | `source_study`, `directional_findings[]` (each: finding, distributional_hypothesis, scenario_type, priority) |

### What was deliberately excluded

| Excluded | Reason |
|---|---|
| **Assumptions Ledger** | In population research, assumptions surface in scenario design, not in hypothesis extraction. Scenario design review (the Critic pass) catches faulty assumptions. A separate Assumptions primitive adds overhead without proportional value at population scale — the per-hypothesis assumption extraction that makes sense for 8 hypotheses doesn't make sense for 15 distributional hypotheses each running 2,000 agents. |
| **Probe Session** | Niobe has no probing. Scenarios are structured and standardised, not open-ended conversations. If depth probing is needed, that's a Segment Brief → Morpheus handoff. |
| **Evidence Tags** | Evidence in population research is distributional — confidence intervals, effect sizes, segment proportions. These are embedded in the Population Finding narrative, not tagged on individual moments. |
| **Stimulus** | Replaced by Scenario Design. At population scale, "stimuli" are structured scenarios with defined options and domain framing, not open-ended probe prompts. The PopScale `Scenario` model is the stimulus equivalent. |

### How relationships are enforced

1. **Distributional Hypothesis → Population Brief.** Every hypothesis must link to at least one study objective in the approved Population Brief.
2. **Scenario Design → Distributional Hypothesis.** Every scenario must target at least one hypothesis. Every hypothesis must have at least one scenario.
3. **Population Run → Scenario Design.** Every run references an approved scenario design.
4. **Population Finding → Population Run.** Every finding must cite at least one run's data.
5. **Segment Brief → Population Finding.** A Segment Brief can only be generated from a finding that identifies a distinct population segment.
6. **State gate.** The study state file prevents downstream execution if upstream artifacts are not approved. Same enforcement model as Morpheus: if-statements, not a dependency engine.

---

## 7. Workflow Design

### The 5 Stages

```
┌──────────────────────────────────────────────────────────────────┐
│  STAGE 1: POPULATION INTAKE                                      │
│  Business Question → Population Brief + Population Spec          │
│  Gate: Researcher approves brief and population spec             │
├──────────────────────────────────────────────────────────────────┤
│  STAGE 2: HYPOTHESIS & SCENARIO DESIGN                           │
│  Brief → Distributional Hypotheses + Scenario Designs            │
│  Gate: Researcher approves hypothesis register + scenario set    │
├──────────────────────────────────────────────────────────────────┤
│  STAGE 3: POPULATION SIMULATION                                  │
│  Scenarios → PopScale Runs → SimulationResults + PopScaleReports │
│  Gate: Researcher reviews run diagnostics + confirms quality     │
├──────────────────────────────────────────────────────────────────┤
│  STAGE 4: POPULATION SYNTHESIS                                   │
│  PopScaleReports → Population Findings + Tandem Recommendations  │
│  Gate: Researcher approves findings                              │
├──────────────────────────────────────────────────────────────────┤
│  STAGE 5: DELIVERABLE & HANDOFF                                  │
│  Findings → Client Deliverable + Segment Briefs (if warranted)   │
│  Gate: Researcher approves deliverable                           │
└──────────────────────────────────────────────────────────────────┘
```

### Stage 1: Population Intake

**Goal:** Transform a business question into a structured Population Brief and demographic Population Spec.

**Inputs:** Business question (text), target population description, geographic scope, domain

**Process:**
1. Researcher provides business question and context
2. Niobe generates Population Brief: decision context, study objectives, target population definition, market size estimate
3. Niobe generates Population Spec: demographic distribution from PopScale's calibration profiles (census-grounded for India states), stratification recommendations
4. Research Critic reviews: "Is the population spec representative? Are the study objectives testable at population scale? Are there scope gaps?"
5. Researcher reviews, edits, approves

**Outputs:** Approved Population Brief, approved Population Spec

**Gate:** Researcher approves both. After approval, the Population Brief becomes the grounding constraint for Stage 2 — every hypothesis must trace to a study objective.

**What makes this different from Morpheus Stage 1:**
Morpheus Stage 1 produces a fact table classifying claims. Niobe Stage 1 produces a population specification classifying demographics. The fact table is about epistemic certainty ("is this a fact or a belief?"). The Population Spec is about statistical representation ("does this synthetic population mirror the real one?").

---

### Stage 2: Hypothesis & Scenario Design

**Goal:** Generate distributional hypotheses and map them to PopScale scenarios.

**Inputs:** Approved Population Brief + Population Spec

**Process:**
1. Niobe generates Distributional Hypotheses: prevalence estimates, distribution shapes, cross-tab predictions, comparative claims
2. For each hypothesis, Niobe recommends a scenario type:
   - **Prevalence** → single-question concept test
   - **Distribution** → Van Westendorp pricing / 5-point scale
   - **Cross-tab** → segmented scenario (same question, different sub-populations)
   - **Comparative** → A/B scenario (two variants, same population)
   - **Issue salience** → MaxDiff-style ranking
   - **Message test** → concept comparison (2–4 message variants)
3. Niobe generates Scenario Designs: PopScale `Scenario` objects with domain framing, sequencing, expected outcomes
4. Research Critic reviews: "Are any hypotheses untestable at population scale? Are any scenarios leading? Is the scenario sequence biased?"
5. Researcher reviews, edits, approves

**Outputs:** Approved Distributional Hypothesis Register, approved Scenario Designs

**Gate:** Researcher approves both. After approval, scenarios are locked for execution.

**What makes this different from Morpheus Stage 2:**
Morpheus generates binary hypotheses grounded in a fact table. Niobe generates distributional hypotheses grounded in study objectives. Morpheus hypotheses are tested through probe sessions. Niobe hypotheses are tested through structured scenarios.

---

### Stage 3: Population Simulation

**Goal:** Execute approved scenarios against the synthetic population via PopScale.

**Inputs:** Approved Scenario Designs, approved Population Spec

**Process:**
1. Niobe invokes PopScale's `calibrate()` to generate the persona segment breakdown from the Population Spec
2. Niobe invokes PopScale's `run_population_scenario()` for each scenario in sequence order
3. For each completed run, Niobe displays: cost, latency, success rate, circuit breaker events
4. Niobe runs PopScale's `generate_report()` on each `SimulationResult` to produce the `PopScaleReport` (segmentation, distributions, drivers, surprises)
5. Researcher reviews run quality: any circuit breaker trips? Any anomalous fallback rates? Any scenarios where success rate < 90%?
6. If quality acceptable, researcher confirms

**Outputs:** Population Runs (with embedded `SimulationResult` and `PopScaleReport`)

**Gate:** Researcher confirms run quality. This is a quality gate, not a content gate — the researcher is verifying the simulation executed correctly, not interpreting results yet.

**What makes this different from Morpheus Stage 4 (probing):**
In Morpheus, the researcher IS the human in the loop during probing — they direct the conversation. In Niobe, the simulation runs headlessly. The researcher's role at this stage is quality assurance, not content generation. The simulation either ran or it didn't. Interpretation happens in Stage 4.

---

### Stage 4: Population Synthesis

**Goal:** Convert PopScaleReport data into research findings and identify tandem handoff candidates.

**Inputs:** Completed Population Runs with PopScaleReports

**Process:**
1. Niobe reads all PopScaleReports across the study
2. For each hypothesis, Niobe generates a finding:
   - What the distribution shows
   - Whether the hypothesis is confirmed, partially confirmed, or refuted (with confidence intervals)
   - What the driver analysis reveals about why
   - Whether any surprise detection flags fired
3. Niobe generates cross-scenario findings: what changed between scenarios, what deltas reveal
4. For each finding that identifies a distinct segment, Niobe proposes: "This segment warrants depth investigation via Morpheus. Generate Segment Brief?"
5. Research Critic reviews findings: "Are any claims stronger than the confidence interval supports? Are any surprises artifacts of small sub-sample sizes? Are the tandem recommendations justified?"
6. Researcher reviews, edits, approves findings

**Outputs:** Approved Population Findings, Tandem Recommendations

**Gate:** Researcher approves findings.

**What makes this different from Morpheus evidence synthesis:**
Morpheus synthesis is qualitative — the researcher reads probe transcripts and identifies patterns manually, with system-surfaced evidence tags as support. Niobe synthesis is quantitative — the system produces distributional narratives from statistical output, and the researcher validates the interpretation. The human role shifts from "pattern recognition" to "interpretation validation."

---

### Stage 5: Deliverable & Handoff

**Goal:** Produce client-facing deliverable and generate Segment Briefs for tandem handoff.

**Inputs:** Approved Population Findings, Tandem Recommendations

**Process:**
1. Niobe selects deliverable template based on sponsor lens (same 5 templates as Morpheus: PM Decision Tree, CEO Strategic Options, Investor Market Validation, Brand Campaign Brief, General Standard Executive)
2. Niobe generates deliverable sections: Segment Map, Distribution Tables, Driver Rankings, Surprise Findings, Methodology Note
3. For each approved tandem recommendation, Niobe generates a Segment Brief for Morpheus
4. Researcher reviews and approves deliverable
5. If DOCX export requested, Niobe generates via docx-js (same toolchain as Morpheus)

**Outputs:** Client deliverable (markdown + optional DOCX), Segment Briefs (if generated)

**Gate:** Researcher approves deliverable.

---

## 8. The Research Critic in Niobe

The Critic follows the same architecture as Morpheus — a separate LLM call with constrained context that receives only the artifact and review criteria.

### Critic review criteria per stage

**Stage 1 (Population Brief + Spec):**
1. Is the population spec demographically representative? Are any major segments missing?
2. Is the market size estimate sourced or assumed?
3. Are the study objectives answerable at population scale with available scenario types?
4. Is the geographic scope appropriate for the question?

**Stage 2 (Hypotheses + Scenarios):**
1. Are any distributional hypotheses untestable with the chosen scenario type?
2. Are any expected ranges implausibly narrow or wide?
3. Is any scenario language leading (biasing responses toward a specific option)?
4. Is the scenario sequence biased (does order create a priming effect)?
5. Swap test: would this scenario produce the same result for any business question?

**Stage 4 (Findings):**
1. Does any finding claim stronger precision than the confidence interval supports?
2. Are any cross-tab findings based on sub-samples too small for statistical validity (n < 30)?
3. Are any surprise findings artifacts of the naive prior estimation, not genuine deviations?
4. Are tandem recommendations justified by the data or speculative?

---

## 9. Distributional Hypothesis Types — Full Specification

### Type 1: Prevalence
**What it tests:** What proportion of the population has attribute X or would do action Y.
**Expected format:** "We expect >40% of the [segment] to [behavior]"
**Confirmed when:** Actual proportion falls within expected range
**Scenario type:** Single-question concept test or binary choice
**Example:** "We expect >40% of less-practicing Muslim women in the UK to consider a digital Islamic mental health service."

### Type 2: Distribution
**What it tests:** How a continuous variable (e.g., WTP) spreads across the population.
**Expected format:** "WTP concentrates between £X–£Y for [segment]"
**Confirmed when:** Median and IQR fall within expected range
**Scenario type:** Van Westendorp pricing (4 questions: too cheap / cheap / expensive / too expensive) or 5-point Likert scale
**Example:** "WTP for a scholar session concentrates between £45–£65 for devout users, but distributes broadly (£20–£75) for moderate users."

### Type 3: Cross-tab
**What it tests:** Whether a segment-level attribute predicts a different outcome distribution.
**Expected format:** "[Attribute X] predicts [outcome Y] with effect size > 0.2"
**Confirmed when:** Cramér's V or point-biserial r exceeds threshold
**Scenario type:** Same scenario run on segmented sub-populations, results compared
**Example:** "Trust orientation (high vs. low) predicts Scholar vs. Counsellor track selection with effect size > 0.3."

### Type 4: Comparative
**What it tests:** Whether variant A produces a different response distribution than variant B.
**Expected format:** "Variant A outperforms variant B by >10pp in [segment]"
**Confirmed when:** A/B delta exceeds expected threshold, measured per segment
**Scenario type:** A/B scenario — same population receives two scenario variants (between-subjects or within-subjects)
**Example:** "WhatsApp-native booking outperforms website booking by >10pp in conversion intent for Counsellor-track users."

### Type 5: Issue Salience
**What it tests:** Which issues, features, or attributes the population ranks highest.
**Expected format:** "[Issue X] ranks in the top 3 for [segment]"
**Confirmed when:** Ranking position matches expected range
**Scenario type:** MaxDiff-style forced ranking or priority ranking
**Example:** "Credential verification ranks in the top 2 concerns for devout users seeking a Scholar."

### Type 6: Message Test
**What it tests:** Which message framing resonates most with the target population.
**Expected format:** "Message A resonates more strongly than Message B with [segment]"
**Confirmed when:** Message A's acceptance rate exceeds Message B's by > threshold
**Scenario type:** Concept comparison — 2–4 message variants presented, response distribution measured
**Example:** "'Makkah-trained scholar specialising in waswasa' outperforms 'certified Islamic counsellor' in booking intent for devout users."

---

## 10. Tandem Protocol — Full Specification

### Segment Brief (Niobe → Morpheus)

Generated when a Population Finding identifies a segment that warrants depth investigation.

```json
{
  "source": "niobe",
  "source_study_id": "NIOBE_20260501_khidma_population",
  "segment_label": "Credential-driven devout user",
  "population_size_estimate": "~68,000 UK (38% of 180K)",
  "behavioural_profile": {
    "trust_orientation": "HIGH",
    "credential_salience": "PRIMARY",
    "price_sensitivity": "LOW",
    "decision_style": "DELIBERATE",
    "track_preference": "SCHOLAR"
  },
  "population_finding": "38% of market. WTP ceiling £75+. Converts only on credential specificity. Highest-value segment by revenue-per-user.",
  "deep_question": "What does the credential verification moment look like for this user? What specific information resolves credential anxiety — institution name, scholar biography, case experience count, or something else? At what point in the journey does this anxiety peak?",
  "recommended_morpheus_hypotheses": [
    "Credential anxiety peaks during WhatsApp pre-booking conversation, not on the landing page",
    "Institution name alone is insufficient — condition-specific experience is the resolver",
    "Credential trust is binary (sufficient or insufficient), not a gradient"
  ]
}
```

**Rules:**
- A Segment Brief can only be generated from an approved Population Finding
- The researcher must approve the Segment Brief before it is handed off
- Morpheus receives it as equivalent to a problem statement — it enters Morpheus at Stage 1
- The `recommended_morpheus_hypotheses` are suggestions, not mandates — Morpheus's own Stage 2 may generate different hypotheses

### Hypothesis List (Morpheus → Niobe)

Generated when Morpheus completes a qualitative study and wants population-level prevalence testing.

```json
{
  "source": "morpheus",
  "source_study_id": "PRJ_20260414_khidma",
  "directional_findings": [
    {
      "finding": "Credential specificity is the conversion gate for Scholar-track users",
      "distributional_hypothesis": "Credential specificity is the primary conversion driver for >35% of the total addressable market",
      "recommended_scenario_type": "prevalence",
      "priority": "HIGH",
      "context": "Supported by H01, H03, H07 across 12 probe sessions. Consistent across S01, S02, S07 personas."
    },
    {
      "finding": "WhatsApp-native booking converts Counsellor segment but undermines Scholar trust",
      "distributional_hypothesis": "WhatsApp-native booking produces a >15pp conversion delta between Counsellor-track and Scholar-track populations",
      "recommended_scenario_type": "comparative",
      "priority": "HIGH",
      "context": "Counterfactual finding CF-PR01. 38% divergence. Consistent across all Scholar-track personas."
    }
  ]
}
```

**Rules:**
- A Hypothesis List can only be generated from approved Morpheus evidence synthesis
- The researcher must approve the Hypothesis List before it is handed off
- Niobe receives it as equivalent to a business question — it enters Niobe at Stage 1
- Niobe may reframe the hypotheses or add additional ones during its own Stage 2

---

## 11. Population Study State File

One JSON file per study: `{study_dir}/study_state.json`

```json
{
  "study_id": "NIOBE_{YYYYMMDD}_{study_slug}",
  "created_at": "ISO8601",
  "updated_at": "ISO8601",
  "current_stage": "intake | scenario_design | simulation | synthesis | deliverable",
  "source": "direct | morpheus_handoff",
  "source_ref": "null | PRJ_{id}",

  "population_brief": {
    "id": "PB_001",
    "file": "population_brief.md",
    "status": "draft | approved",
    "approved_at": "ISO8601 | null",
    "business_question": "string",
    "domain": "CONSUMER | POLICY | POLITICAL",
    "geographic_scope": "string",
    "market_size_estimate": "string"
  },

  "population_spec": {
    "id": "PSPEC_001",
    "file": "population_spec.json",
    "status": "draft | approved",
    "approved_at": "ISO8601 | null",
    "state_code": "string",
    "n_personas": 0,
    "stratification": "religion | income | religion_x_income | custom",
    "calibration_source": "census_2011 | nfhs_5 | manual"
  },

  "hypotheses": {
    "status": "not_started | draft | approved",
    "approved_at": "ISO8601 | null",
    "file": "hypothesis_register.md",
    "critic_file": "critic_hypotheses.md",
    "entries": [
      {
        "id": "DH01",
        "type": "prevalence | distribution | cross_tab | comparative | issue_salience | message_test",
        "status": "approved | rejected",
        "expected_range": "string",
        "scenario_ref": "SD01"
      }
    ]
  },

  "scenario_designs": {
    "status": "not_started | draft | approved",
    "approved_at": "ISO8601 | null",
    "file": "scenario_designs.md",
    "entries": [
      {
        "id": "SD01",
        "scenario_type": "concept_test | pricing | choice | message_test | issue_salience | comparative",
        "target_hypotheses": ["DH01", "DH03"],
        "run_order": 1,
        "tier": "DEEP | SIGNAL | VOLUME",
        "population_spec_ref": "PSPEC_001",
        "status": "pending | running | complete | failed"
      }
    ]
  },

  "population_runs": [
    {
      "id": "RUN_001",
      "scenario_design_ref": "SD01",
      "status": "pending | running | complete | failed",
      "started_at": "ISO8601 | null",
      "completed_at": "ISO8601 | null",
      "n_personas": 0,
      "success_rate": 0.0,
      "cost_usd": 0.0,
      "report_file": "reports/run_001_report.json",
      "diagnostics_file": "reports/run_001_diagnostics.json"
    }
  ],

  "findings": {
    "status": "not_started | draft | approved",
    "approved_at": "ISO8601 | null",
    "file": "population_findings.md",
    "entries": [
      {
        "id": "PF01",
        "finding_type": "segment | distribution | driver | surprise | cross_scenario",
        "headline": "string",
        "supporting_runs": ["RUN_001", "RUN_003"],
        "tandem_recommendation": "segment_brief | none"
      }
    ]
  },

  "tandem": {
    "segment_briefs_generated": [],
    "hypothesis_list_received": null
  },

  "deliverable": {
    "status": "not_started | draft | approved",
    "file": "deliverable.md",
    "docx_file": "null | deliverable.docx",
    "sponsor_lens": "pm | ceo | investor | brand | general",
    "approved_at": "ISO8601 | null"
  },

  "stage_gates": {
    "brief_approved": false,
    "spec_approved": false,
    "hypotheses_approved": false,
    "scenarios_approved": false,
    "runs_confirmed": false,
    "findings_approved": false,
    "deliverable_approved": false
  }
}
```

**State transitions:**

```
intake → scenario_design     (requires: brief_approved AND spec_approved)
scenario_design → simulation (requires: hypotheses_approved AND scenarios_approved)
simulation → synthesis       (requires: runs_confirmed)
synthesis → deliverable      (requires: findings_approved)
```

**File layout per study:**

```
{study_dir}/
├── study_state.json
├── population_brief.md
├── population_spec.json
├── hypothesis_register.md
├── scenario_designs.md
├── critic_hypotheses.md
├── critic_findings.md
├── population_findings.md
├── deliverable.md
├── deliverable.docx              (optional)
├── reports/
│   ├── run_001_report.json       (PopScaleReport)
│   ├── run_001_diagnostics.json  (SimulationResult diagnostics)
│   ├── run_002_report.json
│   └── ...
├── tandem/
│   ├── segment_brief_001.json    (Niobe → Morpheus)
│   └── ...
├── trace/
│   ├── stage1_trace.md
│   ├── stage2_trace.md
│   └── ...
└── export/
    └── study_summary.json        (machine-readable study output)
```

---

## 12. Domain-Specific Configurations

Niobe inherits PopScale's three-domain model. Each domain changes scenario language, population defaults, and output framing.

### Consumer (PopScale equivalent: Lumen)

**Population defaults:** Census-calibrated consumer demographics, income stratification, urban/rural split
**Scenario language:** Market context, purchase decisions, brand perception, price sensitivity
**Output framing:** Segment sizing for TAM/SAM, WTP distributions, conversion probability, competitive positioning
**Typical hypothesis types:** Distribution (pricing), Prevalence (adoption), Comparative (A/B messaging), Message test

### Policy (PopScale equivalent: Seraph)

**Population defaults:** Citizen demographics with institutional trust scores, political lean, media consumption
**Scenario language:** Policy context, institutional trust, compliance intent, public communication
**Output framing:** Public approval probability, resistance mapping, communication effectiveness by demographic
**Typical hypothesis types:** Prevalence (support/oppose), Cross-tab (trust × compliance), Issue salience

### Political (PopScale equivalent: Dynamo)

**Population defaults:** Voter profiles with party affiliation, issue priorities, turnout history, caste-community alignment (India-specific)
**Scenario language:** Electoral context, candidate perception, issue salience, mobilisation
**Output framing:** Vote-share simulation (framed as behavioral, not predictive), turnout likelihood, swing segment identification, message resonance by voter type
**Typical hypothesis types:** Distribution (vote share), Cross-tab (caste × party), Issue salience, Message test (campaign messaging)
**India-specific:** Sarvam cultural integration, state-level demographic profiles from PopScale calibrator, caste-religion stratification

---

## 13. Biggest Remaining Risks

### Risk 1: PopScale analytics output is not rich enough for Niobe's synthesis needs

Niobe's synthesis layer converts PopScaleReport data into research narrative. If the PopScaleReport is too sparse (e.g., segmentation with only 3 segments, driver analysis with only categorical attributes), Niobe's synthesis will be thin. The quality ceiling is set by PopScale's analytics output, not Niobe's synthesis capability.

**Mitigation:** Review PopScaleReport output from Week 3 test runs before finalising Niobe's synthesis prompts. If the analytics are sparse, identify what's missing and feed back to PopScale development.

### Risk 2: Distributional hypotheses generate false precision

Population research tempts precise numerical claims: "42.3% ± 3.1%." With synthetic respondents — not random samples of real people — these numbers are internally consistent but not externally validated. If Niobe presents distributions with narrow confidence intervals, clients may treat them as census-grade truth.

**Mitigation:** Every Niobe deliverable must include a Methodology Note that states: "These distributions represent the behavioral response of synthetic agents calibrated against [data source]. They indicate directional patterns and relative magnitudes, not census-validated prevalence. Confidence intervals reflect internal simulation consistency, not sampling error."

### Risk 3: The tandem protocol is used once and abandoned

The Segment Brief and Hypothesis List are architecturally elegant but operationally expensive — each handoff starts a new study in the receiving system. If the researcher decides it's faster to just "read the Niobe findings and start Morpheus fresh," the tandem protocol becomes unused infrastructure.

**Mitigation:** The tandem handoff must save meaningful time. A Segment Brief should pre-populate Morpheus Stage 1 with enough context that the researcher skips 30+ minutes of problem framing. If it doesn't, the handoff format needs to carry more context — not less.

### Risk 4: Niobe and Morpheus diverge on the same question

If Morpheus says "credential specificity is the conversion gate" and Niobe says "only 22% of the population prioritises credentials," neither is wrong — they're measuring different things. But a client receiving both outputs will see a contradiction.

**Mitigation:** Every tandem study must include a Reconciliation Note that explicitly explains why the findings differ: "Morpheus tested the highest-intent segment (calibrated personas with the specific problem). Niobe tested the full population (census-representative distribution). The 22% prevalence validates that this is a minority segment — but it is the highest-value minority segment, which is why Morpheus found it dominant."

---

## 14. What Makes This the Best Population Researcher Available

### Versus Aaru (scale-first)

Aaru runs 100,000+ agents trained on census + financial + social data. Scale is their advantage. Niobe's advantage is the 200-deep-then-scale architecture: every population study is anchored by psychologically calibrated personas, not just statistically differentiated demographic shells. The depth of the 200 anchors produces behavioral realism that pure scale cannot — a Niobe agent doesn't just have an age, income, and location. It has a cognitive loop (perceive → reflect → decide), a trust orientation, a decision style, and a cultural worldview calibrated by Sarvam.

### Versus Ditto (population-grounded personas)

Ditto grounds synthetic personas in population data. Niobe does this AND orchestrates multi-scenario studies with distributional hypothesis testing, formal synthesis, and tandem depth investigation. Ditto is a persona tool. Niobe is a research instrument.

### Versus Manual Survey Research

A traditional survey study of 2,000 respondents takes 4–8 weeks and costs $30K–$100K. Niobe runs 2,000–10,000 synthetic agents in under 15 minutes. The synthetic output is not a replacement for real survey data — it is a rapid pre-test that identifies the right questions to ask, the right segments to sample, and the right hypotheses to validate.

### The Unique Combination

No competitor has all of these simultaneously:
1. **Depth-anchored population simulation** — Psychologically calibrated DEEP-tier personas serve as behavioral anchors for the scaled synthetic population, not just demographic shells
2. **Multi-scenario study orchestration** — not just one scenario, but a sequenced study with distributional hypothesis testing across 6 scenario types
3. **Formal tandem with a depth instrument** — Niobe findings flow into Morpheus for qualitative investigation of the most interesting segments, and Morpheus findings flow into Niobe for prevalence testing
4. **India cultural realism** — Sarvam integration, state-level census calibration, 85.3% validated accuracy on Indian cultural axes
5. **Census-grounded demographics** — PopScale's calibrator uses Census 2011, NFHS-5, and World Bank data for statistically representative population generation

---

## 15. Final Convergence

### A. This is what we are building

A population-level research orchestrator implemented as a Claude Code skill that:
1. Translates business questions into structured multi-scenario population studies
2. Runs those studies through PopScale's simulation engine
3. Synthesises distributional output into research findings
4. Connects to Morpheus through formal handoff when depth is warranted
5. Produces client deliverables with stated confidence ranges and methodology notes

It has 8 primitives, 5 stages, 7 gates, a Research Critic, and a formal tandem protocol with Morpheus.

### B. This is what we are NOT building

- A replacement for Morpheus (depth is Morpheus's job)
- A PopScale feature (Niobe orchestrates PopScale, it does not extend it)
- A self-serve population research platform (v1 is a researcher tool)
- A data visualisation tool (v1 produces structured data and narrative, not charts)
- A real-time election prediction product (v1 frames electoral output as behavioral simulation)
- A social simulation orchestrator (multi-round temporal is v2)

### C. If we get only one thing right, it should be this

**The population synthesis must convert statistical output into findings that a non-technical client can act on.**

Everything else — the hypothesis register, the tandem protocol, the scenario design — is supporting infrastructure. The synthesis is why Niobe exists. If a client reads "38% of the population, 95% CI [34%, 42%], has credential-driven trust anxiety — this is the highest-revenue segment and they convert only when they can verify the scholar's institution and specialisation on the landing page" and immediately knows what to build, the product works. If they read "Segment 1: 38%, Cramér's V = 0.43, risk_appetite = HIGH" and don't know what it means, it doesn't.

Build the synthesis first. Test it on real PopScale output. Make it sharp.

---

*End of system definition.*
