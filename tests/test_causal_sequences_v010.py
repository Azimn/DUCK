from __future__ import annotations

import json

import pytest

from duck import LivingDuck, PersistentDuckHost
from duck.causal_v010 import CausalSequenceState, PLAN_START
from duck.living import SubjectState


def _state(subject_id: str) -> SubjectState:
    state = SubjectState.create("Aster", subject_id)
    state.needs["energy"] = 0.92
    state.needs["safety"] = 0.88
    state.needs["curiosity"] = 0.84
    state.needs["competence"] = 0.74
    state.needs["coherence"] = 0.82
    state.needs["autonomy"] = 0.72
    state.affect["fear"] = 0.08
    state.affect["unease"] = 0.04
    return state


def _force_two_step_investigation(duck: LivingDuck):
    root = duck.form_goal("investigate", "I want to understand the unfamiliar panel.")
    initial = duck._plan_from_memory(root)
    target_index = initial.routes.index("cautious_inquiry")
    duck._retire_open_plan_steps(initial.plan_id)
    duck._set_plan_field(root, "route_index", target_index)
    duck._set_plan_field(root, "step_index", 0)
    duck._set_plan_field(root, "pending_concern", None)
    duck._set_plan_field(root, "pending_action", None)
    duck._activate_current_step(root)
    return duck._plan_from_memory(root)


def test_causal_sequence_state_has_neutral_prior_and_directional_learning():
    state = CausalSequenceState()
    assert state.transition("ask", "explore") is None

    for tick in range(1, 5):
        state.observe_transition("ask", "explore", outcome="fulfilled", tick=tick)
    learned = state.transition("ask", "explore")
    assert learned is not None
    assert learned.evidence == 4
    assert learned.reliability > 0.70

    failed = CausalSequenceState()
    for tick in range(1, 5):
        failed.observe_transition("ask", "explore", outcome="violated", tick=tick)
    learned_failure = failed.transition("ask", "explore")
    assert learned_failure is not None
    assert learned_failure.reliability < 0.70


def test_sequence_reliability_changes_only_multi_step_route_score():
    duck = LivingDuck(_state("causal-route-score"))
    direct_before = duck._route_score("investigate", "direct_exploration")
    cautious_before = duck._route_score("investigate", "cautious_inquiry")
    assert duck._sequence_prediction_route_adjustment("investigate", "direct_exploration") == pytest.approx(0.0)
    assert duck._sequence_prediction_route_adjustment("investigate", "cautious_inquiry") == pytest.approx(0.0)

    for tick in range(1, 5):
        duck.causal_state.observe_transition("ask", "explore", outcome="fulfilled", tick=tick)

    direct_after = duck._route_score("investigate", "direct_exploration")
    cautious_after = duck._route_score("investigate", "cautious_inquiry")
    assert direct_after == pytest.approx(direct_before)
    assert cautious_after > cautious_before


def test_enacted_adjacent_plan_steps_train_transition_and_clear_context_on_completion():
    duck = LivingDuck(_state("causal-enacted-sequence"))
    plan = _force_two_step_investigation(duck)
    assert plan.current_route == "cautious_inquiry"

    first = duck.heartbeat(allow_inner_speech=False)
    assert first.selected_action == "ask"
    duck.resolve_outcome(
        first.action_id,
        success=0.90,
        valence=0.20,
        description="The inquiry produced useful context.",
    )
    context = duck.causal_state.context_for(plan.plan_id)
    assert context is not None
    assert context.previous_action == "ask"
    assert context.previous_step_index == 0
    baseline = duck.causal_state.transition(PLAN_START, "ask")
    assert baseline is not None
    assert baseline.fulfilled == 1
    assert duck.causal_state.transition("ask", "explore") is None

    second = duck.heartbeat(allow_inner_speech=False)
    assert second.selected_action == "explore"
    duck.resolve_outcome(
        second.action_id,
        success=0.88,
        valence=0.24,
        description="The informed inspection worked.",
    )

    learned = duck.causal_state.transition("ask", "explore")
    assert learned is not None
    assert learned.fulfilled == 1
    assert learned.violated == 0
    assert duck.causal_state.context_for(plan.plan_id) is None
    assert duck.plans(status="completed")


def test_ambiguous_next_step_does_not_train_transition():
    duck = LivingDuck(_state("causal-ambiguous"))
    plan = _force_two_step_investigation(duck)
    first = duck.heartbeat(allow_inner_speech=False)
    duck.resolve_outcome(
        first.action_id,
        success=0.92,
        valence=0.16,
        description="The inquiry helped.",
    )
    second = duck.heartbeat(allow_inner_speech=False)
    duck.resolve_outcome(
        second.action_id,
        success=0.50,
        valence=0.0,
        description="The result was inconclusive.",
    )
    assert duck.causal_state.transition("ask", "explore") is None
    assert duck.causal_state.context_for(plan.plan_id) is not None


def test_failed_next_step_records_negative_transition_and_clears_old_route_context():
    duck = LivingDuck(_state("causal-failed-sequence"))
    plan = _force_two_step_investigation(duck)
    first = duck.heartbeat(allow_inner_speech=False)
    duck.resolve_outcome(
        first.action_id,
        success=0.90,
        valence=0.18,
        description="The inquiry produced context.",
    )
    second = duck.heartbeat(allow_inner_speech=False)
    duck.resolve_outcome(
        second.action_id,
        success=0.12,
        valence=-0.32,
        description="Inspection still failed despite the inquiry.",
    )
    learned = duck.causal_state.transition("ask", "explore")
    assert learned is not None
    assert learned.fulfilled == 0
    assert learned.violated == 1
    assert duck.causal_state.context_for(plan.plan_id) is None


def test_plan_sequence_context_survives_public_host_restart_and_trains_once(tmp_path):
    root = tmp_path / "causal-restart"
    host = PersistentDuckHost.open(root, name="Aster", subject_id="causal-restart")
    host.duck.state.needs.update(_state("template").needs)
    host.duck.state.affect.update(_state("template").affect)
    plan = _force_two_step_investigation(host.duck)

    first = host.duck.heartbeat(allow_inner_speech=False)
    assert first.selected_action == "ask"
    host.duck.resolve_outcome(
        first.action_id,
        success=0.91,
        valence=0.18,
        description="The question yielded useful context.",
    )
    host.save()

    payload = json.loads((root / "causal_v010.json").read_text(encoding="utf-8"))
    assert payload["schema_version"] == "micropsi-duck.causal.v1"
    assert plan.plan_id in payload["plan_contexts"]
    assert f"{PLAN_START}->ask" in payload["transitions"]
    assert "ask->explore" not in payload["transitions"]

    reopened = PersistentDuckHost.open(root)
    context = reopened.duck.causal_state.context_for(plan.plan_id)
    assert context is not None
    assert context.previous_action == "ask"
    assert reopened.status()["active_plan_sequence_context_count"] == 1

    second = reopened.duck.heartbeat(allow_inner_speech=False)
    assert second.selected_action == "explore"
    reopened.duck.resolve_outcome(
        second.action_id,
        success=0.89,
        valence=0.22,
        description="The informed inspection succeeded after restart.",
    )
    reopened.save()

    learned = reopened.duck.causal_state.transition("ask", "explore")
    assert learned is not None
    assert learned.fulfilled == 1
    assert learned.violated == 0
    assert reopened.duck.causal_state.context_for(plan.plan_id) is None
    assert reopened.status()["learned_action_transition_count"] == 2
