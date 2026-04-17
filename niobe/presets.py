"""presets — ready-to-use NiobeStudyRequest templates for common studies.

Each preset is a partially-configured NiobeStudyRequest factory. Callers
supply the scenario content; demographics, environment, and stratification
are pre-wired for the relevant context.

India presets:
    west_bengal_election_study()     — WB state election polling
    india_national_policy_study()    — India national policy research
    india_urban_consumer_study()     — India urban D2C / SaaS consumer research

USA presets:
    us_consumer_study()              — US national consumer research
    us_political_study()             — US political polling / policy research
    us_urban_consumer_study()        — US major metro consumer research

UK / Europe presets:
    uk_consumer_study()              — UK consumer / product research
    uk_political_study()             — UK political / public policy research
    europe_consumer_study()          — Pan-European consumer research (UK default profile)

Usage::

    from niobe.presets import us_consumer_study

    request = us_consumer_study(
        scenario_question="Would you pay $19.99/month for an AI productivity tool?",
        scenario_context="A new AI assistant that automates repetitive tasks...",
        scenario_options=["Definitely", "Probably", "Unlikely", "No"],
        n_personas=500,
    )

    import asyncio
    from niobe.runner import run_niobe_study
    result = asyncio.run(run_niobe_study(request))
"""

from __future__ import annotations

from typing import Optional

from .study_request import NiobeStudyRequest


def west_bengal_election_study(
    scenario_question: str,
    scenario_context: str,
    *,
    scenario_options: Optional[list[str]] = None,
    n_personas: int = 500,
    include_social_dynamics: bool = False,
    budget_cap_usd: Optional[float] = 30.0,
    run_id: Optional[str] = None,
) -> NiobeStudyRequest:
    """West Bengal state election study preset.

    Pre-wired with:
    - state=west_bengal, stratify_by_religion=True
    - environment_preset=west_bengal_political_2026
    - domain=political, age 18–70

    Args:
        scenario_question:    The core electoral question to pose.
        scenario_context:     Background on the political situation.
        scenario_options:     Vote choices. Defaults to a 4-party standard set.
        n_personas:           Population size. Default 500.
        include_social_dynamics: Run social loop. Default False.
        budget_cap_usd:       Cost guard. Default $30.
        run_id:               Optional study ID.
    """
    return NiobeStudyRequest(
        study_name="West Bengal Election Sentiment Study",
        state="west_bengal",
        n_personas=n_personas,
        domain="political",
        research_question=scenario_question,
        scenario_question=scenario_question,
        scenario_context=scenario_context,
        scenario_options=scenario_options or [
            "Yes, TMC (incumbent)",
            "BJP",
            "Left-Congress alliance",
            "Undecided / will not vote",
        ],
        environment_preset="west_bengal_political_2026",
        stratify_by_religion=True,
        stratify_by_income=False,
        age_min=18,
        age_max=70,
        include_social_dynamics=include_social_dynamics,
        social_level="moderate",
        budget_cap_usd=budget_cap_usd,
        run_id=run_id,
    )


def india_national_policy_study(
    scenario_question: str,
    scenario_context: str,
    *,
    scenario_options: Optional[list[str]] = None,
    n_personas: int = 1000,
    include_social_dynamics: bool = False,
    budget_cap_usd: Optional[float] = 60.0,
    run_id: Optional[str] = None,
) -> NiobeStudyRequest:
    """India national policy research preset.

    Pre-wired with:
    - state=india (national aggregate), stratify_by_income=True
    - environment_preset=india_national_policy
    - domain=policy, age 18–65

    Args:
        scenario_question:  The policy question.
        scenario_context:   Policy background.
        scenario_options:   Response options. Leave empty for open-ended.
        n_personas:         Population size. Default 1000.
        include_social_dynamics: Run social loop. Default False.
        budget_cap_usd:     Cost guard. Default $60.
        run_id:             Optional study ID.
    """
    return NiobeStudyRequest(
        study_name="India National Policy Study",
        state="india",
        n_personas=n_personas,
        domain="policy",
        research_question=scenario_question,
        scenario_question=scenario_question,
        scenario_context=scenario_context,
        scenario_options=scenario_options or [],
        environment_preset="india_national_policy",
        stratify_by_religion=False,
        stratify_by_income=True,
        age_min=18,
        age_max=65,
        include_social_dynamics=include_social_dynamics,
        social_level="moderate",
        budget_cap_usd=budget_cap_usd,
        run_id=run_id,
    )


def india_urban_consumer_study(
    scenario_question: str,
    scenario_context: str,
    *,
    scenario_options: Optional[list[str]] = None,
    n_personas: int = 300,
    include_social_dynamics: bool = False,
    budget_cap_usd: Optional[float] = 20.0,
    run_id: Optional[str] = None,
) -> NiobeStudyRequest:
    """India urban consumer research preset.

    Pre-wired with:
    - state=india, urban_only=True, stratify_by_income=True
    - environment_preset=india_urban_consumer
    - domain=consumer, age 20–50

    Args:
        scenario_question:  The consumer question.
        scenario_context:   Product/market background.
        scenario_options:   Purchase/attitude options.
        n_personas:         Population size. Default 300.
        include_social_dynamics: Run social loop. Default False.
        budget_cap_usd:     Cost guard. Default $20.
        run_id:             Optional study ID.
    """
    return NiobeStudyRequest(
        study_name="India Urban Consumer Study",
        state="india",
        n_personas=n_personas,
        domain="consumer",
        research_question=scenario_question,
        scenario_question=scenario_question,
        scenario_context=scenario_context,
        scenario_options=scenario_options or [],
        environment_preset="india_urban_consumer",
        stratify_by_religion=False,
        stratify_by_income=True,
        age_min=20,
        age_max=50,
        urban_only=True,
        include_social_dynamics=include_social_dynamics,
        social_level="low",
        budget_cap_usd=budget_cap_usd,
        run_id=run_id,
    )


# ── USA presets ───────────────────────────────────────────────────────────────

def us_consumer_study(
    scenario_question: str,
    scenario_context: str,
    *,
    scenario_options: Optional[list[str]] = None,
    n_personas: int = 500,
    include_social_dynamics: bool = False,
    budget_cap_usd: Optional[float] = 35.0,
    run_id: Optional[str] = None,
) -> NiobeStudyRequest:
    """United States national consumer research preset.

    Pre-wired with:
    - state=united_states, stratify_by_income=True
    - environment_preset=us_consumer_2026
    - domain=consumer, age 18–65

    Args:
        scenario_question:  The consumer question.
        scenario_context:   Product/market background.
        scenario_options:   Response options. Leave empty for open-ended.
        n_personas:         Population size. Default 500.
        include_social_dynamics: Run social loop. Default False.
        budget_cap_usd:     Cost guard. Default $35.
        run_id:             Optional study ID.
    """
    return NiobeStudyRequest(
        study_name="US Consumer Study",
        state="united_states",
        n_personas=n_personas,
        domain="consumer",
        research_question=scenario_question,
        scenario_question=scenario_question,
        scenario_context=scenario_context,
        scenario_options=scenario_options or [],
        environment_preset="us_consumer_2026",
        stratify_by_religion=False,
        stratify_by_income=True,
        age_min=18,
        age_max=65,
        include_social_dynamics=include_social_dynamics,
        social_level="moderate",
        budget_cap_usd=budget_cap_usd,
        run_id=run_id,
    )


def us_political_study(
    scenario_question: str,
    scenario_context: str,
    *,
    scenario_options: Optional[list[str]] = None,
    n_personas: int = 1000,
    include_social_dynamics: bool = False,
    budget_cap_usd: Optional[float] = 65.0,
    run_id: Optional[str] = None,
) -> NiobeStudyRequest:
    """United States political polling / policy research preset.

    Pre-wired with:
    - state=united_states, stratify_by_income=True
    - environment_preset=us_political_2026
    - domain=political, age 18–80

    Args:
        scenario_question:  The political/policy question.
        scenario_context:   Political or policy context.
        scenario_options:   Response options. Leave empty for open-ended.
        n_personas:         Population size. Default 1000.
        include_social_dynamics: Run social loop. Default False.
        budget_cap_usd:     Cost guard. Default $65.
        run_id:             Optional study ID.
    """
    return NiobeStudyRequest(
        study_name="US Political Study",
        state="united_states",
        n_personas=n_personas,
        domain="political",
        research_question=scenario_question,
        scenario_question=scenario_question,
        scenario_context=scenario_context,
        scenario_options=scenario_options or [],
        environment_preset="us_political_2026",
        stratify_by_religion=False,
        stratify_by_income=True,
        age_min=18,
        age_max=80,
        include_social_dynamics=include_social_dynamics,
        social_level="moderate",
        budget_cap_usd=budget_cap_usd,
        run_id=run_id,
    )


def us_urban_consumer_study(
    scenario_question: str,
    scenario_context: str,
    *,
    scenario_options: Optional[list[str]] = None,
    n_personas: int = 300,
    include_social_dynamics: bool = False,
    budget_cap_usd: Optional[float] = 22.0,
    run_id: Optional[str] = None,
) -> NiobeStudyRequest:
    """United States urban consumer research preset (major metros).

    Pre-wired with:
    - state=united_states, urban_only=True, stratify_by_income=True
    - environment_preset=us_urban_consumer
    - domain=consumer, age 22–55

    Args:
        scenario_question:  The consumer question.
        scenario_context:   Product/market background.
        scenario_options:   Response options. Leave empty for open-ended.
        n_personas:         Population size. Default 300.
        include_social_dynamics: Run social loop. Default False.
        budget_cap_usd:     Cost guard. Default $22.
        run_id:             Optional study ID.
    """
    return NiobeStudyRequest(
        study_name="US Urban Consumer Study",
        state="united_states",
        n_personas=n_personas,
        domain="consumer",
        research_question=scenario_question,
        scenario_question=scenario_question,
        scenario_context=scenario_context,
        scenario_options=scenario_options or [],
        environment_preset="us_urban_consumer",
        stratify_by_religion=False,
        stratify_by_income=True,
        age_min=22,
        age_max=55,
        urban_only=True,
        include_social_dynamics=include_social_dynamics,
        social_level="low",
        budget_cap_usd=budget_cap_usd,
        run_id=run_id,
    )


# ── UK presets ────────────────────────────────────────────────────────────────

def uk_consumer_study(
    scenario_question: str,
    scenario_context: str,
    *,
    scenario_options: Optional[list[str]] = None,
    n_personas: int = 500,
    include_social_dynamics: bool = False,
    budget_cap_usd: Optional[float] = 35.0,
    run_id: Optional[str] = None,
) -> NiobeStudyRequest:
    """United Kingdom consumer research preset.

    Pre-wired with:
    - state=united_kingdom, stratify_by_income=True
    - environment_preset=uk_consumer_2026
    - domain=consumer, age 18–70

    Args:
        scenario_question:  The consumer question.
        scenario_context:   Product/market background.
        scenario_options:   Response options. Leave empty for open-ended.
        n_personas:         Population size. Default 500.
        include_social_dynamics: Run social loop. Default False.
        budget_cap_usd:     Cost guard. Default $35.
        run_id:             Optional study ID.
    """
    return NiobeStudyRequest(
        study_name="UK Consumer Study",
        state="united_kingdom",
        n_personas=n_personas,
        domain="consumer",
        research_question=scenario_question,
        scenario_question=scenario_question,
        scenario_context=scenario_context,
        scenario_options=scenario_options or [],
        environment_preset="uk_consumer_2026",
        stratify_by_religion=False,
        stratify_by_income=True,
        age_min=18,
        age_max=70,
        include_social_dynamics=include_social_dynamics,
        social_level="moderate",
        budget_cap_usd=budget_cap_usd,
        run_id=run_id,
    )


def uk_political_study(
    scenario_question: str,
    scenario_context: str,
    *,
    scenario_options: Optional[list[str]] = None,
    n_personas: int = 1000,
    include_social_dynamics: bool = False,
    budget_cap_usd: Optional[float] = 65.0,
    run_id: Optional[str] = None,
) -> NiobeStudyRequest:
    """United Kingdom political / public policy research preset.

    Pre-wired with:
    - state=united_kingdom, stratify_by_income=True
    - environment_preset=uk_political_2026
    - domain=political, age 18–80

    Args:
        scenario_question:  The political/policy question.
        scenario_context:   Political or policy context.
        scenario_options:   Response options. Leave empty for open-ended.
        n_personas:         Population size. Default 1000.
        include_social_dynamics: Run social loop. Default False.
        budget_cap_usd:     Cost guard. Default $65.
        run_id:             Optional study ID.
    """
    return NiobeStudyRequest(
        study_name="UK Political Study",
        state="united_kingdom",
        n_personas=n_personas,
        domain="political",
        research_question=scenario_question,
        scenario_question=scenario_question,
        scenario_context=scenario_context,
        scenario_options=scenario_options or [],
        environment_preset="uk_political_2026",
        stratify_by_religion=False,
        stratify_by_income=True,
        age_min=18,
        age_max=80,
        include_social_dynamics=include_social_dynamics,
        social_level="moderate",
        budget_cap_usd=budget_cap_usd,
        run_id=run_id,
    )


# ── Europe presets ────────────────────────────────────────────────────────────

def europe_consumer_study(
    scenario_question: str,
    scenario_context: str,
    *,
    state: str = "united_kingdom",
    scenario_options: Optional[list[str]] = None,
    n_personas: int = 500,
    include_social_dynamics: bool = False,
    budget_cap_usd: Optional[float] = 35.0,
    run_id: Optional[str] = None,
) -> NiobeStudyRequest:
    """Pan-European or single-country consumer research preset.

    Pre-wired with:
    - state=<country code> (default: united_kingdom)
    - environment_preset=europe_consumer_2026
    - domain=consumer, age 18–65

    For country-specific research, pass state="france", state="germany", etc.
    Available EU profiles: france, germany, spain, italy, netherlands, poland, sweden.

    Args:
        scenario_question:  The consumer question.
        scenario_context:   Product/market background.
        state:              Country code (default: "united_kingdom").
                            Use "france", "germany", "spain", "italy",
                            "netherlands", "poland", "sweden" for specific markets.
        scenario_options:   Response options. Leave empty for open-ended.
        n_personas:         Population size. Default 500.
        include_social_dynamics: Run social loop. Default False.
        budget_cap_usd:     Cost guard. Default $35.
        run_id:             Optional study ID.
    """
    return NiobeStudyRequest(
        study_name="Europe Consumer Study",
        state=state,
        n_personas=n_personas,
        domain="consumer",
        research_question=scenario_question,
        scenario_question=scenario_question,
        scenario_context=scenario_context,
        scenario_options=scenario_options or [],
        environment_preset="europe_consumer_2026",
        stratify_by_religion=False,
        stratify_by_income=True,
        age_min=18,
        age_max=65,
        include_social_dynamics=include_social_dynamics,
        social_level="moderate",
        budget_cap_usd=budget_cap_usd,
        run_id=run_id,
    )
