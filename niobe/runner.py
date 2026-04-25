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
import functools
import json
import logging
import os
import signal
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)
_MAX_CONCURRENT_LLM = int(os.getenv("SIMULATTE_MAX_CONCURRENT_LLM", "20"))
_llm_semaphore: asyncio.Semaphore | None = None


def _get_llm_semaphore() -> asyncio.Semaphore:
    global _llm_semaphore
    if _llm_semaphore is None:
        _llm_semaphore = asyncio.Semaphore(_MAX_CONCURRENT_LLM)
    return _llm_semaphore


def with_llm_semaphore(func):
    """Wrap an async LLM-calling function with the shared semaphore."""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        async with _get_llm_semaphore():
            return await func(*args, **kwargs)
    return wrapper

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
try:
    from src.observability.cost_tracer import CostTracer             # noqa: E402
except ImportError:
    CostTracer = None  # type: ignore[assignment,misc]


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
    enable_partial_writes: bool = True,
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
    guarded_run_study = with_llm_semaphore(run_study)

    if not enable_partial_writes:
        result = await guarded_run_study(config)
        for persona in result.cohort.personas:
            if CostTracer is not None:
                summary = CostTracer.finish_persona(persona.persona_id)
                logger.info("persona_cost_summary: %s", summary)
        return result

    config.run_id = config.run_id or request.run_id or f"niobe-{uuid.uuid4().hex[:8]}"
    output_dir = _resolve_output_dir(request)
    partial_path = output_dir / f"{config.run_id}.partial.json"
    _write_partial_json(partial_path, None, status="in_progress")
    result: StudyResult | None = None

    previous_handlers: dict[int, Any] = {}

    def _flush_partial() -> None:
        _write_partial_json(partial_path, result, status="in_progress")

    for sig in (signal.SIGTERM, signal.SIGINT):
        try:
            previous_handlers[sig] = signal.getsignal(sig)
            signal.signal(sig, lambda *_: _flush_partial())
        except (ValueError, RuntimeError):
            continue

    try:
        result = await guarded_run_study(config)
        _write_partial_json(partial_path, result, status="completed")
    except Exception:
        _write_partial_json(partial_path, result, status="failed")
        raise
    finally:
        for sig, handler in previous_handlers.items():
            try:
                signal.signal(sig, handler)
            except (ValueError, RuntimeError):
                continue

    for persona in result.cohort.personas:
        if CostTracer is not None:
            summary = CostTracer.finish_persona(persona.persona_id)
            logger.info("persona_cost_summary: %s", summary)
    return result


def run_niobe_study_sync(
    request: NiobeStudyRequest,
    **kwargs: Any,
) -> StudyResult:
    """Synchronous wrapper. Do not call from an active event loop."""
    return asyncio.run(run_niobe_study(request, **kwargs))


async def run_niobe_study_streaming(
    request: NiobeStudyRequest,
    *,
    llm_client: Any = None,
) -> StudyResult:
    """Compatibility streaming entrypoint with partial checkpoint writes enabled."""
    return await run_niobe_study(
        request,
        llm_client=llm_client,
        enable_partial_writes=True,
    )


def _resolve_output_dir(request: NiobeStudyRequest) -> Path:
    output_dir = Path(request.output_dir) if request.output_dir else Path(
        os.getenv("SIMULATTE_PARTIAL_DIR", "/tmp/wb_reruns")
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def _json_default(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def _write_partial_json(path: Path, result: StudyResult | None, *, status: str) -> None:
    payload: dict[str, Any] = {
        "status": status,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    if result is not None:
        payload.update({
            "run_id": result.run_id,
            "n_personas": result.n_personas,
            "cohort_size": result.cohort.total_delivered,
            "seat_report_available": result.report is not None,
            "cost_usd": round(result.total_cost_usd, 4),
            "cohort": result.cohort,
            "simulation": result.simulation,
        })
    path.write_text(
        json.dumps(payload, default=_json_default, indent=2),
        encoding="utf-8",
    )


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
        "united_arab_emirates", "uae", "dubai", "abu_dhabi",
        "saudi_arabia", "ksa",
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
