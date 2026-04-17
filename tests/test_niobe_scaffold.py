"""Niobe scaffold tests — NiobeStudyRequest, runner translation, presets.

Tests:
    1. NiobeStudyRequest — construction, validation, summary
    2. _build_study_config() — correct translation to StudyConfig
    3. Preset factories — WB election, India policy, India consumer
    4. run_niobe_study imports and signature
    5. Domain, social level, and event category mappings

Run all (no live API calls):
    python3 -m pytest tests/test_niobe_scaffold.py -v
"""

from __future__ import annotations

import sys
from pathlib import Path

_NIOBE_ROOT    = Path(__file__).parents[1]
_POPSCALE_ROOT = _NIOBE_ROOT.parent / "PopScale"
_PG_ROOT       = _NIOBE_ROOT.parent / "Persona Generator"
for p in [str(_NIOBE_ROOT), str(_POPSCALE_ROOT), str(_PG_ROOT)]:
    if p not in sys.path:
        sys.path.insert(0, p)

import pytest

from niobe.study_request import NiobeStudyRequest
from niobe.runner import _build_study_config, run_niobe_study, run_niobe_study_sync
from niobe.presets import (
    india_national_policy_study,
    india_urban_consumer_study,
    west_bengal_election_study,
)
from popscale.scenario.model import SimulationDomain
from popscale.social.social_runner import SocialSimulationLevel
from popscale.study.study_runner import StudyConfig


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_request(**kwargs) -> NiobeStudyRequest:
    defaults = dict(
        study_name="Test Study",
        state="west_bengal",
        n_personas=50,
        domain="policy",
        research_question="Test research question about West Bengal policy.",
        scenario_question="Will you support the proposed fuel subsidy cut?",
        scenario_context=(
            "The government has proposed cutting fuel subsidies to reduce the fiscal deficit. "
            "This will raise LPG prices by 40%. Lower-income households will be most affected."
        ),
        scenario_options=["Support", "Oppose", "Neutral"],
        environment_preset="west_bengal_political_2026",
        stratify_by_religion=True,
    )
    defaults.update(kwargs)
    return NiobeStudyRequest(**defaults)


# ─────────────────────────────────────────────────────────────────────────────
# 1. NiobeStudyRequest — construction and validation
# ─────────────────────────────────────────────────────────────────────────────

class TestNiobeStudyRequest:

    def test_basic_construction(self):
        req = _make_request()
        assert req.state == "west_bengal"
        assert req.n_personas == 50
        assert req.domain == "policy"

    def test_zero_personas_raises(self):
        with pytest.raises(ValueError, match="n_personas"):
            _make_request(n_personas=0)

    def test_empty_scenario_question_raises(self):
        with pytest.raises(ValueError, match="scenario_question"):
            _make_request(scenario_question="   ")

    def test_empty_scenario_context_raises(self):
        with pytest.raises(ValueError, match="scenario_context"):
            _make_request(scenario_context="   ")

    def test_both_urban_rural_raises(self):
        with pytest.raises(ValueError, match="urban_only"):
            _make_request(urban_only=True, rural_only=True)

    def test_invalid_social_level_raises(self):
        with pytest.raises(ValueError, match="social_level"):
            _make_request(social_level="extreme")

    def test_valid_social_levels(self):
        for level in ("isolated", "low", "moderate", "high", "saturated"):
            req = _make_request(social_level=level)
            assert req.social_level == level

    def test_default_social_level_moderate(self):
        req = _make_request()
        assert req.social_level == "moderate"

    def test_default_include_social_false(self):
        req = _make_request()
        assert req.include_social_dynamics is False

    def test_events_list_optional(self):
        req = _make_request()
        assert req.events == []

    def test_events_populated(self):
        req = _make_request(events=[
            {"round": 1, "category": "economic", "description": "Fuel spike.", "magnitude": 0.8}
        ])
        assert len(req.events) == 1

    def test_budget_cap_optional(self):
        req = _make_request(budget_cap_usd=25.0)
        assert req.budget_cap_usd == 25.0

    def test_summary_contains_state(self):
        req = _make_request()
        assert "west_bengal" in req.summary()

    def test_summary_contains_study_name(self):
        req = _make_request(study_name="My Test Study")
        assert "My Test Study" in req.summary()

    def test_summary_mentions_social_when_enabled(self):
        req = _make_request(include_social_dynamics=True, social_level="high")
        assert "social=high" in req.summary()


# ─────────────────────────────────────────────────────────────────────────────
# 2. _build_study_config() — translation correctness
# ─────────────────────────────────────────────────────────────────────────────

class TestBuildStudyConfig:

    def test_returns_study_config(self):
        req = _make_request()
        config = _build_study_config(req)
        assert isinstance(config, StudyConfig)

    def test_spec_state_matches_request(self):
        req = _make_request(state="maharashtra")
        config = _build_study_config(req)
        assert config.spec.state == "maharashtra"

    def test_spec_n_personas_matches(self):
        req = _make_request(n_personas=200)
        config = _build_study_config(req)
        assert config.spec.n_personas == 200

    def test_scenario_question_preserved(self):
        req = _make_request()
        config = _build_study_config(req)
        assert config.scenario.question == req.scenario_question

    def test_scenario_context_preserved(self):
        req = _make_request()
        config = _build_study_config(req)
        assert config.scenario.context == req.scenario_context

    def test_scenario_options_preserved(self):
        req = _make_request(scenario_options=["Yes", "No", "Maybe"])
        config = _build_study_config(req)
        assert config.scenario.options == ["Yes", "No", "Maybe"]

    def test_domain_policy_maps_correctly(self):
        req = _make_request(domain="policy")
        config = _build_study_config(req)
        assert config.scenario.domain == SimulationDomain.POLICY

    def test_domain_consumer_maps_correctly(self):
        req = _make_request(domain="consumer")
        config = _build_study_config(req)
        assert config.scenario.domain == SimulationDomain.CONSUMER

    def test_domain_political_maps_correctly(self):
        req = _make_request(domain="political")
        config = _build_study_config(req)
        assert config.scenario.domain == SimulationDomain.POLITICAL

    def test_environment_preset_wired(self):
        req = _make_request(environment_preset="west_bengal_political_2026")
        config = _build_study_config(req)
        assert config.environment is not None
        assert config.environment.name == "west_bengal_political_2026"

    def test_unknown_preset_gives_none(self):
        req = _make_request(environment_preset="nonexistent_preset")
        config = _build_study_config(req)
        assert config.environment is None

    def test_no_preset_gives_none(self):
        req = _make_request(environment_preset=None)
        config = _build_study_config(req)
        assert config.environment is None

    def test_social_dynamics_flag_wired(self):
        req = _make_request(include_social_dynamics=True, social_level="high")
        config = _build_study_config(req)
        assert config.run_social is True
        assert config.social_level == SocialSimulationLevel.HIGH

    def test_social_disabled_by_default(self):
        req = _make_request()
        config = _build_study_config(req)
        assert config.run_social is False

    def test_budget_cap_passed_through(self):
        req = _make_request(budget_cap_usd=15.0)
        config = _build_study_config(req)
        assert config.budget_cap_usd == 15.0

    def test_events_become_timeline(self):
        req = _make_request(events=[
            {"round": 0, "category": "economic",
             "description": "Fuel prices rise 40%.", "magnitude": 0.8},
            {"round": 1, "category": "political",
             "description": "Rally held in Kolkata.", "magnitude": 0.7},
        ])
        config = _build_study_config(req)
        assert config.timeline is not None
        assert config.timeline.n_events == 2

    def test_no_events_gives_no_timeline(self):
        req = _make_request(events=[])
        config = _build_study_config(req)
        assert config.timeline is None

    def test_stratification_flags_passed(self):
        req = _make_request(stratify_by_religion=True, stratify_by_income=False)
        config = _build_study_config(req)
        assert config.spec.stratify_by_religion is True
        assert config.spec.stratify_by_income is False

    def test_age_range_passed(self):
        req = _make_request(age_min=25, age_max=60)
        config = _build_study_config(req)
        assert config.spec.age_min == 25
        assert config.spec.age_max == 60

    def test_persona_prefix_is_niobe(self):
        req = _make_request()
        config = _build_study_config(req)
        assert config.spec.persona_id_prefix == "niobe"

    def test_sarvam_enabled_true(self):
        req = _make_request()
        config = _build_study_config(req)
        assert config.spec.sarvam_enabled is True


# ─────────────────────────────────────────────────────────────────────────────
# 3. Preset factories
# ─────────────────────────────────────────────────────────────────────────────

class TestPresets:

    def test_wb_election_preset_returns_request(self):
        req = west_bengal_election_study(
            scenario_question="Will you vote for TMC?",
            scenario_context="Elections are next month. Fuel prices have risen 40%.",
        )
        assert isinstance(req, NiobeStudyRequest)

    def test_wb_election_preset_state(self):
        req = west_bengal_election_study(
            scenario_question="Q?",
            scenario_context="Context for Bengal election study with enough detail.",
        )
        assert req.state == "west_bengal"

    def test_wb_election_preset_stratifies_religion(self):
        req = west_bengal_election_study(
            scenario_question="Q?",
            scenario_context="Context for Bengal election study with enough detail.",
        )
        assert req.stratify_by_religion is True

    def test_wb_election_preset_environment(self):
        req = west_bengal_election_study(
            scenario_question="Q?",
            scenario_context="Context for Bengal election study with enough detail.",
        )
        assert req.environment_preset == "west_bengal_political_2026"

    def test_wb_election_preset_custom_n(self):
        req = west_bengal_election_study(
            scenario_question="Q?",
            scenario_context="Context for Bengal election study with enough detail.",
            n_personas=1000,
        )
        assert req.n_personas == 1000

    def test_wb_election_default_options_4(self):
        req = west_bengal_election_study(
            scenario_question="Q?",
            scenario_context="Context for Bengal election study with enough detail.",
        )
        assert len(req.scenario_options) == 4

    def test_india_policy_preset_returns_request(self):
        req = india_national_policy_study(
            scenario_question="Do you support the fuel subsidy cut?",
            scenario_context="Government has proposed cutting fuel subsidies to reduce deficit.",
        )
        assert isinstance(req, NiobeStudyRequest)

    def test_india_policy_preset_state_india(self):
        req = india_national_policy_study(
            scenario_question="Q?",
            scenario_context="Government national policy study context with sufficient detail here.",
        )
        assert req.state == "india"

    def test_india_policy_preset_income_stratification(self):
        req = india_national_policy_study(
            scenario_question="Q?",
            scenario_context="Government national policy study context with sufficient detail here.",
        )
        assert req.stratify_by_income is True

    def test_urban_consumer_preset_returns_request(self):
        req = india_urban_consumer_study(
            scenario_question="Would you pay Rs 1,999/month for this SaaS?",
            scenario_context="A new AI-powered productivity tool launching in urban India.",
        )
        assert isinstance(req, NiobeStudyRequest)

    def test_urban_consumer_preset_urban_only(self):
        req = india_urban_consumer_study(
            scenario_question="Q?",
            scenario_context="A new AI-powered productivity tool launching in urban India.",
        )
        assert req.urban_only is True

    def test_urban_consumer_preset_domain_consumer(self):
        req = india_urban_consumer_study(
            scenario_question="Q?",
            scenario_context="A new AI-powered productivity tool launching in urban India.",
        )
        assert req.domain == "consumer"

    def test_all_presets_produce_valid_study_config(self):
        """All preset outputs should translate to valid StudyConfig without error."""
        presets = [
            west_bengal_election_study(
                scenario_question="Will you vote for TMC?",
                scenario_context="West Bengal election context study with enough detail provided here.",
            ),
            india_national_policy_study(
                scenario_question="Do you support the fuel subsidy cut?",
                scenario_context="Government has proposed cutting fuel subsidies to reduce deficit.",
            ),
            india_urban_consumer_study(
                scenario_question="Would you pay Rs 1,999/month?",
                scenario_context="A new AI-powered productivity tool launching in urban India.",
            ),
        ]
        for req in presets:
            config = _build_study_config(req)
            assert isinstance(config, StudyConfig)
            assert config.spec.n_personas == req.n_personas


# ─────────────────────────────────────────────────────────────────────────────
# 4. Runner module interface
# ─────────────────────────────────────────────────────────────────────────────

class TestRunnerInterface:

    def test_run_niobe_study_is_coroutine(self):
        import asyncio
        assert asyncio.iscoroutinefunction(run_niobe_study)

    def test_run_niobe_study_sync_callable(self):
        assert callable(run_niobe_study_sync)

    def test_run_niobe_study_signature(self):
        import inspect
        sig = inspect.signature(run_niobe_study)
        assert "request" in sig.parameters

    def test_build_study_config_importable(self):
        from niobe.runner import _build_study_config
        assert callable(_build_study_config)


# ─────────────────────────────────────────────────────────────────────────────
# 5. Event category and social level mappings
# ─────────────────────────────────────────────────────────────────────────────

class TestMappings:

    def test_economic_category_maps(self):
        req = _make_request(events=[
            {"round": 0, "category": "economic",
             "description": "Fuel prices rise.", "magnitude": 0.7}
        ])
        config = _build_study_config(req)
        from popscale.scenario.events import EventCategory
        assert config.timeline.events[0].category == EventCategory.ECONOMIC

    def test_political_category_maps(self):
        req = _make_request(events=[
            {"round": 1, "category": "political",
             "description": "Election rally held.", "magnitude": 0.6}
        ])
        config = _build_study_config(req)
        from popscale.scenario.events import EventCategory
        assert config.timeline.events[0].category == EventCategory.POLITICAL

    def test_social_level_high_maps(self):
        req = _make_request(include_social_dynamics=True, social_level="high")
        config = _build_study_config(req)
        assert config.social_level == SocialSimulationLevel.HIGH

    def test_social_level_saturated_maps(self):
        req = _make_request(include_social_dynamics=True, social_level="saturated")
        config = _build_study_config(req)
        assert config.social_level == SocialSimulationLevel.SATURATED

    def test_unknown_event_category_defaults_to_economic(self):
        req = _make_request(events=[
            {"round": 0, "category": "unknown_type",
             "description": "Something happened.", "magnitude": 0.5}
        ])
        config = _build_study_config(req)
        from popscale.scenario.events import EventCategory
        assert config.timeline.events[0].category == EventCategory.ECONOMIC
