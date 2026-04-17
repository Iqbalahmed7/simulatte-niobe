"""test_niobe_geo_presets — Niobe US/UK/Europe preset factory tests.

Tests:
    1. us_consumer_study — construction and defaults
    2. us_political_study — construction and defaults
    3. us_urban_consumer_study — construction and urban_only flag
    4. uk_consumer_study — construction and defaults
    5. uk_political_study — construction and defaults
    6. europe_consumer_study — construction and state override
    7. All new presets produce valid StudyConfig without error

Run (no live API calls):
    python3 -m pytest tests/test_niobe_geo_presets.py -v
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
from niobe.runner import _build_study_config
from niobe.presets import (
    us_consumer_study,
    us_political_study,
    us_urban_consumer_study,
    uk_consumer_study,
    uk_political_study,
    europe_consumer_study,
)
from popscale.study.study_runner import StudyConfig


# ── Helpers ───────────────────────────────────────────────────────────────────

_Q  = "Test scenario question with meaningful content?"
_CTX = "Test scenario context providing background for the research question."


# ─────────────────────────────────────────────────────────────────────────────
# 1. us_consumer_study
# ─────────────────────────────────────────────────────────────────────────────

class TestUsConsumerPreset:

    def test_returns_niobe_study_request(self):
        req = us_consumer_study(scenario_question=_Q, scenario_context=_CTX)
        assert isinstance(req, NiobeStudyRequest)

    def test_state_united_states(self):
        req = us_consumer_study(scenario_question=_Q, scenario_context=_CTX)
        assert req.state == "united_states"

    def test_domain_consumer(self):
        req = us_consumer_study(scenario_question=_Q, scenario_context=_CTX)
        assert req.domain == "consumer"

    def test_default_n_personas(self):
        req = us_consumer_study(scenario_question=_Q, scenario_context=_CTX)
        assert req.n_personas == 500

    def test_custom_n_personas(self):
        req = us_consumer_study(scenario_question=_Q, scenario_context=_CTX, n_personas=1000)
        assert req.n_personas == 1000

    def test_stratify_by_income_true(self):
        req = us_consumer_study(scenario_question=_Q, scenario_context=_CTX)
        assert req.stratify_by_income is True

    def test_stratify_by_religion_false(self):
        req = us_consumer_study(scenario_question=_Q, scenario_context=_CTX)
        assert req.stratify_by_religion is False

    def test_environment_preset(self):
        req = us_consumer_study(scenario_question=_Q, scenario_context=_CTX)
        assert req.environment_preset == "us_consumer_2026"

    def test_budget_cap_default(self):
        req = us_consumer_study(scenario_question=_Q, scenario_context=_CTX)
        assert req.budget_cap_usd == 35.0

    def test_age_range(self):
        req = us_consumer_study(scenario_question=_Q, scenario_context=_CTX)
        assert req.age_min == 18
        assert req.age_max == 65

    def test_not_urban_only(self):
        req = us_consumer_study(scenario_question=_Q, scenario_context=_CTX)
        assert req.urban_only is False


# ─────────────────────────────────────────────────────────────────────────────
# 2. us_political_study
# ─────────────────────────────────────────────────────────────────────────────

class TestUsPoliticalPreset:

    def test_returns_niobe_study_request(self):
        req = us_political_study(scenario_question=_Q, scenario_context=_CTX)
        assert isinstance(req, NiobeStudyRequest)

    def test_state_united_states(self):
        req = us_political_study(scenario_question=_Q, scenario_context=_CTX)
        assert req.state == "united_states"

    def test_domain_political(self):
        req = us_political_study(scenario_question=_Q, scenario_context=_CTX)
        assert req.domain == "political"

    def test_default_n_personas_1000(self):
        req = us_political_study(scenario_question=_Q, scenario_context=_CTX)
        assert req.n_personas == 1000

    def test_environment_preset(self):
        req = us_political_study(scenario_question=_Q, scenario_context=_CTX)
        assert req.environment_preset == "us_political_2026"

    def test_age_max_80(self):
        req = us_political_study(scenario_question=_Q, scenario_context=_CTX)
        assert req.age_max == 80

    def test_budget_cap_default(self):
        req = us_political_study(scenario_question=_Q, scenario_context=_CTX)
        assert req.budget_cap_usd == 65.0


# ─────────────────────────────────────────────────────────────────────────────
# 3. us_urban_consumer_study
# ─────────────────────────────────────────────────────────────────────────────

class TestUsUrbanConsumerPreset:

    def test_returns_niobe_study_request(self):
        req = us_urban_consumer_study(scenario_question=_Q, scenario_context=_CTX)
        assert isinstance(req, NiobeStudyRequest)

    def test_urban_only_true(self):
        req = us_urban_consumer_study(scenario_question=_Q, scenario_context=_CTX)
        assert req.urban_only is True

    def test_state_united_states(self):
        req = us_urban_consumer_study(scenario_question=_Q, scenario_context=_CTX)
        assert req.state == "united_states"

    def test_domain_consumer(self):
        req = us_urban_consumer_study(scenario_question=_Q, scenario_context=_CTX)
        assert req.domain == "consumer"

    def test_default_n_personas_300(self):
        req = us_urban_consumer_study(scenario_question=_Q, scenario_context=_CTX)
        assert req.n_personas == 300

    def test_environment_preset(self):
        req = us_urban_consumer_study(scenario_question=_Q, scenario_context=_CTX)
        assert req.environment_preset == "us_urban_consumer"

    def test_age_range_22_55(self):
        req = us_urban_consumer_study(scenario_question=_Q, scenario_context=_CTX)
        assert req.age_min == 22
        assert req.age_max == 55


# ─────────────────────────────────────────────────────────────────────────────
# 4. uk_consumer_study
# ─────────────────────────────────────────────────────────────────────────────

class TestUkConsumerPreset:

    def test_returns_niobe_study_request(self):
        req = uk_consumer_study(scenario_question=_Q, scenario_context=_CTX)
        assert isinstance(req, NiobeStudyRequest)

    def test_state_united_kingdom(self):
        req = uk_consumer_study(scenario_question=_Q, scenario_context=_CTX)
        assert req.state == "united_kingdom"

    def test_domain_consumer(self):
        req = uk_consumer_study(scenario_question=_Q, scenario_context=_CTX)
        assert req.domain == "consumer"

    def test_default_n_personas_500(self):
        req = uk_consumer_study(scenario_question=_Q, scenario_context=_CTX)
        assert req.n_personas == 500

    def test_environment_preset(self):
        req = uk_consumer_study(scenario_question=_Q, scenario_context=_CTX)
        assert req.environment_preset == "uk_consumer_2026"

    def test_stratify_by_income_true(self):
        req = uk_consumer_study(scenario_question=_Q, scenario_context=_CTX)
        assert req.stratify_by_income is True

    def test_stratify_by_religion_false(self):
        req = uk_consumer_study(scenario_question=_Q, scenario_context=_CTX)
        assert req.stratify_by_religion is False

    def test_age_range_18_70(self):
        req = uk_consumer_study(scenario_question=_Q, scenario_context=_CTX)
        assert req.age_min == 18
        assert req.age_max == 70


# ─────────────────────────────────────────────────────────────────────────────
# 5. uk_political_study
# ─────────────────────────────────────────────────────────────────────────────

class TestUkPoliticalPreset:

    def test_returns_niobe_study_request(self):
        req = uk_political_study(scenario_question=_Q, scenario_context=_CTX)
        assert isinstance(req, NiobeStudyRequest)

    def test_state_united_kingdom(self):
        req = uk_political_study(scenario_question=_Q, scenario_context=_CTX)
        assert req.state == "united_kingdom"

    def test_domain_political(self):
        req = uk_political_study(scenario_question=_Q, scenario_context=_CTX)
        assert req.domain == "political"

    def test_default_n_personas_1000(self):
        req = uk_political_study(scenario_question=_Q, scenario_context=_CTX)
        assert req.n_personas == 1000

    def test_environment_preset(self):
        req = uk_political_study(scenario_question=_Q, scenario_context=_CTX)
        assert req.environment_preset == "uk_political_2026"

    def test_age_max_80(self):
        req = uk_political_study(scenario_question=_Q, scenario_context=_CTX)
        assert req.age_max == 80

    def test_budget_cap(self):
        req = uk_political_study(scenario_question=_Q, scenario_context=_CTX)
        assert req.budget_cap_usd == 65.0


# ─────────────────────────────────────────────────────────────────────────────
# 6. europe_consumer_study
# ─────────────────────────────────────────────────────────────────────────────

class TestEuropeConsumerPreset:

    def test_returns_niobe_study_request(self):
        req = europe_consumer_study(scenario_question=_Q, scenario_context=_CTX)
        assert isinstance(req, NiobeStudyRequest)

    def test_default_state_united_kingdom(self):
        req = europe_consumer_study(scenario_question=_Q, scenario_context=_CTX)
        assert req.state == "united_kingdom"

    def test_state_france(self):
        req = europe_consumer_study(scenario_question=_Q, scenario_context=_CTX, state="france")
        assert req.state == "france"

    def test_state_germany(self):
        req = europe_consumer_study(scenario_question=_Q, scenario_context=_CTX, state="germany")
        assert req.state == "germany"

    def test_state_spain(self):
        req = europe_consumer_study(scenario_question=_Q, scenario_context=_CTX, state="spain")
        assert req.state == "spain"

    def test_domain_consumer(self):
        req = europe_consumer_study(scenario_question=_Q, scenario_context=_CTX)
        assert req.domain == "consumer"

    def test_environment_preset(self):
        req = europe_consumer_study(scenario_question=_Q, scenario_context=_CTX)
        assert req.environment_preset == "europe_consumer_2026"

    def test_default_n_personas_500(self):
        req = europe_consumer_study(scenario_question=_Q, scenario_context=_CTX)
        assert req.n_personas == 500

    def test_stratify_by_income_true(self):
        req = europe_consumer_study(scenario_question=_Q, scenario_context=_CTX)
        assert req.stratify_by_income is True


# ─────────────────────────────────────────────────────────────────────────────
# 7. All new presets produce valid StudyConfig
# ─────────────────────────────────────────────────────────────────────────────

class TestAllNewPresetsProduceValidConfig:

    def test_all_presets_produce_study_config(self):
        presets = [
            us_consumer_study(scenario_question=_Q, scenario_context=_CTX),
            us_political_study(scenario_question=_Q, scenario_context=_CTX),
            us_urban_consumer_study(scenario_question=_Q, scenario_context=_CTX),
            uk_consumer_study(scenario_question=_Q, scenario_context=_CTX),
            uk_political_study(scenario_question=_Q, scenario_context=_CTX),
            europe_consumer_study(scenario_question=_Q, scenario_context=_CTX),
            europe_consumer_study(scenario_question=_Q, scenario_context=_CTX, state="france"),
            europe_consumer_study(scenario_question=_Q, scenario_context=_CTX, state="germany"),
            europe_consumer_study(scenario_question=_Q, scenario_context=_CTX, state="spain"),
        ]
        for req in presets:
            config = _build_study_config(req)
            assert isinstance(config, StudyConfig), f"Failed for state={req.state}"
            assert config.spec.n_personas == req.n_personas

    def test_us_consumer_config_location_override(self):
        req = us_consumer_study(scenario_question=_Q, scenario_context=_CTX)
        config = _build_study_config(req)
        # Calibration should produce segments with US location
        from popscale.calibration.calibrator import calibrate
        segments = calibrate(config.spec)
        for seg in segments:
            assert seg.anchor_overrides["location"] == "United States"

    def test_uk_consumer_config_location_override(self):
        req = uk_consumer_study(scenario_question=_Q, scenario_context=_CTX)
        config = _build_study_config(req)
        from popscale.calibration.calibrator import calibrate
        segments = calibrate(config.spec)
        for seg in segments:
            assert seg.anchor_overrides["location"] == "United Kingdom"

    def test_france_config_location_override(self):
        req = europe_consumer_study(scenario_question=_Q, scenario_context=_CTX, state="france")
        config = _build_study_config(req)
        from popscale.calibration.calibrator import calibrate
        segments = calibrate(config.spec)
        for seg in segments:
            assert seg.anchor_overrides["location"] == "France"
