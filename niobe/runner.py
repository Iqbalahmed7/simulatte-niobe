"""runner — Niobe's primary orchestration entry point.

run_niobe_study() translates a NiobeStudyRequest into a PopScale StudyConfig
and runs the full pipeline. It is the single function Niobe's API, CLI, and
UI should call.

Translation layer:
    NiobeStudyRequest
        → PopulationSpec      (from state, n_personas, stratification flags)
        → Scenario            (from scenario_question, context, options, domain)
        → SimulationEnvironment (from environment_preset, if set)
        → EventTimeline       (from events list, if set)
        → StudyConfig         (assembled)
        → run_study()         (PopScale)
        → StudyResult         (returned)

Usage::

    import asyncio
    from niobe.runner import run_niobe_study
    from niobe.study_request import NiobeStudyRequest

    request = NiobeStudyRequest(
        study_name="West Bengal Election Sentiment 2026",
        state="west_bengal",
        n_personas=500,
        domain="policy",
        research_question="How will voters respond to fuel price rises?",
        scenario_question="Will you vote for the incumbent TMC party?",
        scenario_context="...",
        scenario_options=["Yes, TMC", "BJP", "Left-Congress", "Undecided"],
        environment_preset="west_bengal_political_2026",
        stratify_by_religion=True,
        include_social_dynamics=True,
        budget_cap_usd=30.0,
    )

    result = asyncio.run(run_niobe_study(request))
    print(result.report.to_markdown())
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

# ── Path setup ────────────────────────────────────────────────────────────────
_POPSCALE_ROOT = Path(__file__).parents[2] / "PopScale"
_PG_ROOT       = Path(__file__).parents[2] / "Persona Generator"
for p in [str(_POPSCALE_ROOT), str(_PG_ROOT)]:
    if p not in sys.path:
        sys.path.insert(0, p)

# ── PopScale imports ──────────────────────────────────────────────────────────
from popscale.calibration.population_spec import PopulationSpec       # noqa: E402
from popscale.environment import get_preset                            # noqa: E402
from popscale.scenario.events import (                                 # noqa: E402
    EventCategory,
    EventTimeline,
    SimulationEvent,
)
from popscale.scenario.model import Scenario, SimulationDomain        # noqa: E402
from popscale.social.social_runner import SocialSimulationLevel       # noqa: E402
from popscale.study.study_runner import StudyConfig, StudyResult, run_study  # noqa: E402

# ── Niobe imports ─────────────────────────────────────────────────────────────
from .study_request import NiobeStudyRequest                          # noqa: E402


# ── Domain mapping ────────────────────────────────────────────────────────────

_DOMAIN_MAP: dict[str, SimulationDomain] = {
    "consumer":  SimulationDomain.CONSUMER,
    "policy":    SimulationDomain.POLICY,
    "political": SimulationDomain.POLITICAL,
}

_SOCIAL_LEVEL_MAP: dict[str, SocialSimulationLevel] = {
    "isolated":  SocialSimulationLevel.ISOLATED,
    "low":       SocialSimulationLevel.LOW,
    "moderate":  SocialSimulationLevel.MODERATE,
    "high":      SocialSimulationLevel.HIGH,
    "saturated": SocialSimulationLevel.SATURATED,
}

_CATEGORY_MAP: dict[str, EventCategory] = {
    "economic":    EventCategory.ECONOMIC,
    "policy":      EventCategory.POLICY,
    "social":      EventCategory.SOCIAL,
    "information": EventCategory.INFORMATION,
    "natural":     EventCategory.NATURAL,
    "political":   EventCategory.POLITICAL,
    "technology":  EventCategory.TECHNOLOGY,
}


# ── Public API ────────────────────────────────────────────────────────────────

async def run_niobe_study(
    request: NiobeStudyRequest,
    *,
    llm_client: Any = None,
) -> StudyResult:
    """Translate a NiobeStudyRequest into a PopScale study and run it.

    Args:
        request:     The NiobeStudyRequest describing the study.
        llm_client:  Optional Anthropic client. Created automatically if None.

    Returns:
        StudyResult with full cohort, simulation, and analytics.
    """
    logger.info("run_niobe_study | %s", request.summary())

    config = _build_study_config(request, llm_client=llm_client)
    return await run_study(config)


def run_niobe_study_sync(
    request: NiobeStudyRequest,
    **kwargs: Any,
) -> StudyResult:
    """Synchronous wrapper. Do not call from an active event loop."""
    return asyncio.run(run_niobe_study(request, **kwargs))


# ── Translation helpers ───────────────────────────────────────────────────────

def _build_study_config(
    request: NiobeStudyRequest,
    *,
    llm_client: Any = None,
) -> StudyConfig:
    """Translate NiobeStudyRequest → StudyConfig."""

    # Sarvam is India-specific cultural enrichment. Disable for non-India markets
    # even if the key is set — it adds overhead with no benefit outside India.
    _NON_INDIA_STATES = {
        "united_states", "us", "usa", "california", "texas", "new_york",
        "florida", "illinois", "pennsylvania", "ohio", "georgia", "north_carolina",
        "washington", "colorado", "arizona", "michigan", "new_jersey",
        "massachusetts", "virginia", "us_northeast", "us_south", "us_midwest", "us_west",
        "united_kingdom", "france", "germany", "spain", "italy",
        "netherlands", "poland", "sweden",
    }

    # PopulationSpec
    spec = PopulationSpec(
        state=request.state,
        n_personas=request.n_personas,
        domain=request.domain,
        business_problem=request.research_question,
        age_min=request.age_min,
        age_max=request.age_max,
        urban_only=request.urban_only,
        rural_only=request.rural_only,
        stratify_by_religion=request.stratify_by_religion,
        stratify_by_income=request.stratify_by_income,
        client="Niobe",
        persona_id_prefix="niobe",
        sarvam_enabled=bool(os.environ.get("SARVAM_API_KEY")) and request.state not in _NON_INDIA_STATES,
    )

    # Scenario
    domain = _DOMAIN_MAP.get(request.domain.lower(), SimulationDomain.POLICY)
    scenario = Scenario(
        question=request.scenario_question,
        context=request.scenario_context,
        options=request.scenario_options,
        domain=domain,
        metadata={"study_name": request.study_name},
    )

    # Environment preset
    environment = None
    if request.environment_preset:
        try:
            environment = get_preset(request.environment_preset)
        except KeyError:
            logger.warning(
                "Unknown environment preset '%s' — proceeding without it.",
                request.environment_preset,
            )

    # EventTimeline
    timeline: Optional[EventTimeline] = None
    if request.events:
        events: list[SimulationEvent] = []
        for ev in request.events:
            category = _CATEGORY_MAP.get(
                str(ev.get("category", "economic")).lower(),
                EventCategory.ECONOMIC,
            )
            events.append(SimulationEvent(
                round=int(ev.get("round", 0)),
                category=category,
                description=str(ev["description"]),
                magnitude=float(ev.get("magnitude", 0.5)),
                tags=list(ev.get("tags", [])),
                source=ev.get("source"),
            ))
        timeline = EventTimeline(events=events, name=request.study_name)

    # Social level
    social_level = _SOCIAL_LEVEL_MAP.get(
        request.social_level.lower(), SocialSimulationLevel.MODERATE
    )

    return StudyConfig(
        spec=spec,
        scenario=scenario,
        environment=environment,
        timeline=timeline,
        run_social=request.include_social_dynamics,
        social_level=social_level,
        generation_tier="volume",
        use_seeded_generation=request.use_seeded_generation,
        seed_count=request.seed_count,
        seed_tier=request.seed_tier,
        budget_cap_usd=request.budget_cap_usd,
        use_cache=True,
        output_dir=request.output_dir,
        run_id=request.run_id,
        llm_client=llm_client,
    )
