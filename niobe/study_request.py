"""study_request — NiobeStudyRequest, the high-level entry model for Niobe.

NiobeStudyRequest is the consumer-facing input to Niobe. It is intentionally
simpler than PopScale's StudyConfig — no knowledge of sharding, tiers, or
cache internals required. Niobe translates it into a StudyConfig internally.

Design principle: NiobeStudyRequest should be fillable by a product manager
or research analyst. StudyConfig is for engineers. Niobe bridges the two.

Usage::

    from niobe.study_request import NiobeStudyRequest

    request = NiobeStudyRequest(
        study_name="West Bengal Election Sentiment 2026",
        state="west_bengal",
        n_personas=500,
        domain="policy",
        research_question="How will Bengali voters respond to fuel price rises?",
        scenario_question="Will you vote for the incumbent TMC party?",
        scenario_context="...",
        scenario_options=["Yes, TMC", "BJP", "Left-Congress", "Undecided"],
        environment_preset="west_bengal_political_2026",
        stratify_by_religion=True,
        include_social_dynamics=True,
        events=[
            {"round": 0, "category": "economic",
             "description": "Fuel prices rise 40%.", "magnitude": 0.8},
        ],
        budget_cap_usd=30.0,
    )
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

_POPSCALE_ROOT = Path(__file__).parents[2] / "PopScale"
if str(_POPSCALE_ROOT) not in sys.path:
    sys.path.insert(0, str(_POPSCALE_ROOT))


@dataclass
class NiobeStudyRequest:
    """High-level research study request for Niobe.

    Attributes:
        study_name:            Human-readable name for the study (used in reports).
        state:                 Geography code for the study population.
                               India: "west_bengal", "maharashtra", "india" (national).
                               USA:   "california", "texas", "new_york", "florida",
                                      "illinois", "georgia", "washington", "united_states".
                               Also accepts "us"/"usa" for US national aggregate.
                               See popscale.calibration.profiles.list_states() for all options.
        n_personas:            Number of personas to simulate. Recommended: 100–2000.
        domain:                Research domain — "policy", "consumer", "political".
        research_question:     The overarching research question (for report headers).
        scenario_question:     The specific question posed to each persona.
        scenario_context:      Background context for the scenario (50–300 words recommended).
        scenario_options:      Discrete choice options (2–6). Leave empty for open-ended.
        environment_preset:    Name of a SimulationEnvironment preset, or None.
                               e.g. "west_bengal_political_2026", "india_urban_consumer".
        stratify_by_religion:  If True, split cohort by religious composition.
        stratify_by_income:    If True, split cohort by income bands.
        age_min:               Minimum persona age. Default 18.
        age_max:               Maximum persona age. Default 65.
        urban_only:            Restrict to urban archetypes.
        rural_only:            Restrict to rural archetypes.
        include_social_dynamics: If True, run social simulation after main sim.
        social_level:          Social simulation intensity.
                               "isolated" | "low" | "moderate" | "high" | "saturated"
        events:                List of event dicts for temporal injection.
                               Each: {round, category, description, magnitude, tags?}
        budget_cap_usd:        Refuse if estimated cost exceeds this. None = no cap.
        output_dir:            If set, save reports and cohort to this directory.
        run_id:                Optional study identifier. Auto-generated if None.
        use_seeded_generation: When True, generates seed_count deep personas first,
                               then expands to n_personas using the VariantGenerator
                               (1 Haiku call per variant). Recommended for n>=1,000.
                               Default False (every persona uses the full pipeline).
        seed_count:            Number of deep seed personas to generate before
                               expansion. Only used when use_seeded_generation=True.
                               Default 200. Must be <= n_personas.
        seed_tier:             PG tier for seed generation: "deep" (default) or
                               "signal". "deep" gives richer seeds; "signal" is
                               faster and cheaper for exploratory work.
    """
    study_name: str
    state: str
    n_personas: int
    domain: str
    research_question: str
    scenario_question: str
    scenario_context: str

    scenario_options: list[str] = field(default_factory=list)
    environment_preset: Optional[str] = None

    stratify_by_religion: bool = False
    stratify_by_income: bool = False
    age_min: int = 18
    age_max: int = 65
    urban_only: bool = False
    rural_only: bool = False

    include_social_dynamics: bool = False
    social_level: str = "moderate"

    events: list[dict] = field(default_factory=list)

    budget_cap_usd: Optional[float] = None
    output_dir: Optional[Path] = None
    run_id: Optional[str] = None

    # Seeded generation
    use_seeded_generation: bool = False
    seed_count: int = 200
    seed_tier: str = "deep"

    def __post_init__(self) -> None:
        if self.n_personas < 1:
            raise ValueError(f"n_personas must be ≥ 1, got {self.n_personas}")
        if not self.scenario_question.strip():
            raise ValueError("scenario_question must not be empty")
        if not self.scenario_context.strip():
            raise ValueError("scenario_context must not be empty")
        if self.urban_only and self.rural_only:
            raise ValueError("urban_only and rural_only cannot both be True")
        valid_levels = {"isolated", "low", "moderate", "high", "saturated"}
        if self.social_level not in valid_levels:
            raise ValueError(f"social_level must be one of {valid_levels}")
        if self.use_seeded_generation:
            if self.seed_count < 1:
                raise ValueError(f"seed_count must be ≥ 1, got {self.seed_count}")
            if self.seed_count > self.n_personas:
                raise ValueError(
                    f"seed_count ({self.seed_count}) must be ≤ n_personas ({self.n_personas})"
                )
            valid_tiers = {"deep", "signal", "volume"}
            if self.seed_tier not in valid_tiers:
                raise ValueError(f"seed_tier must be one of {valid_tiers}")

    def generation_cost_estimate(self) -> dict:
        """Estimate generation cost in USD based on mode and counts.

        Returns dict with keys: mode, seed_cost, variant_cost, total_cost,
        standard_cost, savings_pct.
        """
        standard_cost = self.n_personas * 0.30
        if not self.use_seeded_generation:
            return {
                "mode": "standard",
                "seed_cost": standard_cost,
                "variant_cost": 0.0,
                "total_cost": standard_cost,
                "standard_cost": standard_cost,
                "savings_pct": 0.0,
            }
        seed_cost = self.seed_count * 0.30
        variant_count = self.n_personas - self.seed_count
        variant_cost = variant_count * 0.004
        total = seed_cost + variant_cost
        savings_pct = (1.0 - total / standard_cost) * 100 if standard_cost > 0 else 0.0
        return {
            "mode": "seeded",
            "seed_cost": round(seed_cost, 2),
            "variant_cost": round(variant_cost, 2),
            "total_cost": round(total, 2),
            "standard_cost": round(standard_cost, 2),
            "savings_pct": round(savings_pct, 1),
        }

    def summary(self) -> str:
        parts = [
            f"'{self.study_name}'",
            f"state={self.state}",
            f"n={self.n_personas}",
            f"domain={self.domain}",
        ]
        if self.environment_preset:
            parts.append(f"env={self.environment_preset}")
        if self.include_social_dynamics:
            parts.append(f"social={self.social_level}")
        if self.events:
            parts.append(f"events={len(self.events)}")
        if self.use_seeded_generation:
            parts.append(f"seeded=true seeds={self.seed_count}")
        return f"NiobeStudyRequest({', '.join(parts)})"
