from __future__ import annotations

import json

from duck import LivingDuck, PersistentDuckHost, SubjectState, WorldEvent
from duck.motivated_cognition import (
    COGNITIVE_STATE_SCHEMA,
    MAX_ACTIVE_MOTIVES,
    MAX_EDGES,
    MotivatedCognitionState,
)


def _state(subject_id: str) -> SubjectState:
    state = SubjectState.create("Aster", subject_id)
    state.affect["fear"] = 0.02
    state.affect["unease"] = 0.03
    state.needs["energy"] = 0.95
    state.needs["safety"] = 0.95
    state.needs["curiosity"] = 0.88
    state.needs["competence"] = 0.72
    state.needs["coherence"] = 0.82
    state.needs["autonomy"] = 0.72
    state.needs["affiliation"] = 0.18
    return state


def _motive_theme(duck: LivingDuck) -> str | None:
    motive = duck.control.dominant_motive()
    return motive.theme if motive is not None else None


def test_motive_competition_displaces_without_deleting_loser():
    duck = LivingDuck(_state("motive-competition"))
    duck.step(
        WorldEvent(
            "observation",
            "world",
            "A strange mechanism pulses in an unfamiliar pattern.",
            ("novel", "mystery"),
            0.0,
            0.55,
        ),
        allow_inner_speech=False,
    )
    assert _motive_theme(duck) == "curiosity"
    curiosity_ids = {
        motive.motive_id
        for motive in duck.cognitive_state.motives.values()
        if motive.theme == "curiosity"
    }
    assert curiosity_ids

    duck.step(
        WorldEvent(
            "encounter",
            "Morgan",
            "Morgan suddenly threatens me.",
            ("social", "threat", "conflict"),
            -0.8,
            0.95,
        ),
        allow_inner_speech=False,
    )
    assert _motive_theme(duck) == "safety"
    assert curiosity_ids.issubset(duck.cognitive_state.motives)
    assert any(
        duck.cognitive_state.motives[motive_id].status in {"active", "inhibited", "latent"}
        for motive_id in curiosity_ids
    )
    assert len(
        [
            motive
            for motive in duck.cognitive_state.motives.values()
            if motive.status in {"dominant", "active"}
        ]
    ) <= MAX_ACTIVE_MOTIVES


def test_energy_motive_can_be_satisfied_after_recovery():
    state = _state("motive-satisfaction")
    state.needs["energy"] = 0.08
    state.needs["curiosity"] = 0.10
    duck = LivingDuck(state)
    duck.heartbeat(allow_inner_speech=False)
    energy = next(m for m in duck.cognitive_state.motives.values() if m.theme == "energy")
    assert energy.status in {"dominant", "active"}

    duck.state.needs["energy"] = 0.99
    for _ in range(9):
        duck.heartbeat(allow_inner_speech=False)
    energy = duck.cognitive_state.motives[energy.motive_id]
    assert energy.status == "satisfied"
    assert duck.cognitive_state.last_dominant_motive_id != energy.motive_id


def test_associative_bridge_surfaces_nonlexical_memory_before_private_cognition():
    state = _state("bridge")
    dinner = state.add_memory(
        "I had dinner with Sarah after work.",
        tags=("garden", "dinner"),
        people=("Sarah",),
        importance=0.62,
    )
    flower = state.add_memory(
        "I noticed a blue flower beside the old wall.",
        tags=("garden", "flower"),
        importance=0.62,
    )
    direct = state.retrieve_memories(
        "Sarah just arrived.",
        people=("Sarah",),
        top_k=5,
    )
    assert dinner in direct
    assert flower not in direct

    duck = LivingDuck(state)
    step = duck.step(
        WorldEvent(
            "encounter",
            "Sarah",
            "Sarah just arrived.",
            ("social",),
            0.0,
            0.30,
        ),
        allow_inner_speech=False,
    )
    trace = step.developer_trace["motivated_cognition"]
    assert flower.memory_id in trace["activated_memory_ids"]
    assert flower.memory_id in step.recalled_memory_ids
    assert any("blue flower" in line.lower() for line in step.subjective_moment.recollections)


def test_same_external_event_has_narrower_cognition_under_threat():
    event = WorldEvent(
        "observation",
        "world",
        "An unfamiliar device is humming.",
        ("novel", "mystery"),
        0.0,
        0.45,
    )
    calm_state = _state("regime-calm")
    threatened_state = _state("regime-threat")
    threatened_state.affect["fear"] = 0.88
    threatened_state.needs["safety"] = 0.28

    calm = LivingDuck(calm_state).step(event, allow_inner_speech=False)
    threatened = LivingDuck(threatened_state).step(event, allow_inner_speech=False)
    calm_mod = calm.developer_trace["motivated_cognition"]["modulation"]
    threat_mod = threatened.developer_trace["motivated_cognition"]["modulation"]

    assert threat_mod["propagation_depth"] < calm_mod["propagation_depth"]
    assert threat_mod["retrieval_budget"] < calm_mod["retrieval_budget"]
    assert threat_mod["route_branching"] <= calm_mod["route_branching"]
    assert threat_mod["exploration"] < calm_mod["exploration"]


def test_fatigue_reduces_planning_depth_and_low_competence_favors_familiarity():
    event = WorldEvent("observation", "world", "A closed gate blocks the path.", ("obstacle",), 0.0, 0.40)
    rested_state = _state("rested")
    tired_state = _state("tired")
    tired_state.needs["energy"] = 0.08

    rested = LivingDuck(rested_state).step(event, allow_inner_speech=False)
    tired = LivingDuck(tired_state).step(event, allow_inner_speech=False)
    assert (
        tired.developer_trace["motivated_cognition"]["modulation"]["planning_depth"]
        < rested.developer_trace["motivated_cognition"]["modulation"]["planning_depth"]
    )

    competent_state = _state("competent")
    competent_state.needs["competence"] = 0.92
    uncertain_state = _state("uncertain")
    uncertain_state.needs["competence"] = 0.12
    competent = LivingDuck(competent_state).step(event, allow_inner_speech=False)
    uncertain = LivingDuck(uncertain_state).step(event, allow_inner_speech=False)
    assert (
        uncertain.developer_trace["motivated_cognition"]["modulation"]["familiar_strategy_bias"]
        > competent.developer_trace["motivated_cognition"]["modulation"]["familiar_strategy_bias"]
    )


def test_route_ordering_is_downstream_of_current_cognitive_regime():
    event = WorldEvent(
        "observation",
        "world",
        "An unfamiliar mechanism is blinking.",
        ("novel", "mystery"),
        0.0,
        0.45,
    )
    curious = LivingDuck(_state("route-curious"))
    curious.current_cycle = curious.control.prepare_cycle(curious.state, event)
    curious_plan = curious.form_goal("investigate", "I want to understand the mechanism.")
    assert curious._plan_from_memory(curious_plan).current_route == "direct_exploration"

    threat_state = _state("route-threat")
    threat_state.affect["fear"] = 0.90
    threat_state.needs["safety"] = 0.25
    threatened = LivingDuck(threat_state)
    threatened.current_cycle = threatened.control.prepare_cycle(threatened.state, event)
    threat_plan = threatened.form_goal("investigate", "I want to understand the mechanism.")
    assert threatened._plan_from_memory(threat_plan).current_route == "cautious_inquiry"


def test_language_lesion_preserves_full_control_spine():
    duck = LivingDuck(_state("lesion-control"))
    step = duck.step(
        WorldEvent(
            "encounter",
            "world",
            "Something dangerous moves closer.",
            ("threat",),
            -0.7,
            0.90,
        ),
        allow_inner_speech=False,
    )
    assert step.inner_cognition.thought is None
    assert step.selected_action
    assert duck.current_cycle is not None
    assert duck.current_cycle.dominant_motive_id
    assert step.developer_trace["motivated_cognition"]["modulation"]["propagation_depth"] >= 1
    assert duck.last_experience.prose


def test_cognitive_state_is_versioned_and_persists_across_host_restart(tmp_path):
    root = tmp_path / "micropsi"
    host = PersistentDuckHost.open(root, name="Aster", subject_id="persist-v010")
    host.observe(
        WorldEvent(
            "observation",
            "world",
            "A strange signal appears.",
            ("novel", "mystery"),
            0.0,
            0.50,
        ),
        allow_inner_speech=False,
    )
    host.save()
    assert (root / "cognition_v010.json").exists()
    payload = json.loads((root / "cognition_v010.json").read_text(encoding="utf-8"))
    assert payload["schema_version"] == COGNITIVE_STATE_SCHEMA
    assert payload["motives"]
    before_ids = set(payload["motives"])
    before_edges = len(payload["graph"]["edges"])

    reopened = PersistentDuckHost.open(root)
    assert set(reopened.duck.cognitive_state.motives) == before_ids
    assert len(reopened.duck.cognitive_state.graph.edges) == before_edges
    assert reopened.duck.cognitive_state.schema_version == COGNITIVE_STATE_SCHEMA


def test_cognitive_state_roundtrip_and_unknown_schema_rejected():
    state = MotivatedCognitionState()
    restored = MotivatedCognitionState.from_dict(state.to_dict())
    assert restored.schema_version == COGNITIVE_STATE_SCHEMA

    bad = state.to_dict()
    bad["schema_version"] = "future.schema"
    try:
        MotivatedCognitionState.from_dict(bad)
    except ValueError:
        pass
    else:
        raise AssertionError("unknown cognitive schema must fail explicitly")


def test_quiet_time_stays_bounded():
    state = _state("quiet-bounds")
    state.needs["curiosity"] = 0.18
    duck = LivingDuck(state)
    for _ in range(160):
        duck.heartbeat(allow_inner_speech=False)
    assert len(duck.cognitive_state.motives) <= 12
    assert len(duck.cognitive_state.graph.edges) <= MAX_EDGES
