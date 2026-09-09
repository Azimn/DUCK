from __future__ import annotations

import json

import pytest

from duck import LivingDuck, PersistentDuckHost
from duck.causal_v010 import CausalSequenceState, PLAN_START
from duck.living import SubjectState, WorldEvent


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


def test_transition_state_distinguishes_observation_from_intervention_evidence():
    state = CausalSequenceState()
    state.observe_transition("ask", "explore", outcome="fulfilled", tick=1)
    observed = state.transition("ask", "explore")
    assert observed is not None
    assert observed.fulfilled == 1
    assert observed.intervention_fulfilled == 0
    assert observed.observational_evidence == 1

    state.observe_transition(
        "ask",
        "explore",
        outcome="fulfilled",
        tick=2,
        intervention=True,
    )
    mixed = state.transition("ask", "explore")
    assert mixed is not None
    assert mixed.fulfilled == 2
    assert mixed.intervention_fulfilled == 1
    assert mixed.intervention_evidence == 1
    assert mixed.observational_evidence == 1
    assert mixed.observational_reliability > 0.70
    assert mixed.intervention_reliability > 0.70


def test_intervention_contrast_requires_treatment_and_direct_baseline_evidence():
    state = CausalSequenceState()
    state.observe_transition(
        "ask",
        "explore",
        outcome="fulfilled",
        tick=1,
        intervention=True,
    )
    assert state.estimate_intervention_contrast("ask", "explore") is None

    state.observe_transition(PLAN_START, "explore", outcome="violated", tick=2)
    sparse = state.estimate_intervention_contrast("ask", "explore")
    assert sparse is not None
    assert sparse.eligible is False
    assert sparse.intervention_evidence == 1
    assert sparse.baseline_evidence == 1

    state.observe_transition(
        "ask",
        "explore",
        outcome="fulfilled",
        tick=3,
        intervention=True,
    )
    state.observe_transition(PLAN_START, "explore", outcome="violated", tick=4)
    supported = state.estimate_intervention_contrast("ask", "explore")
    assert supported is not None
    assert supported.eligible is True
    assert supported.intervention_evidence == 2
    assert supported.baseline_evidence == 2
    assert supported.delta > 0.0


def test_intervention_label_grants_no_special_route_weight_without_matched_baseline():
    duck = LivingDuck(_state("intervention-no-magic-weight"))
    assert duck._intervention_contrast_route_adjustment("investigate", "cautious_inquiry") == pytest.approx(0.0)

    for tick in range(1, 5):
        duck.causal_state.observe_transition(
            "ask",
            "explore",
            outcome="fulfilled",
            tick=tick,
            intervention=True,
        )
    assert duck._intervention_contrast_route_adjustment("investigate", "cautious_inquiry") == pytest.approx(0.0)

    for tick in range(5, 9):
        duck.causal_state.observe_transition(
            PLAN_START,
            "explore",
            outcome="violated",
            tick=tick,
        )
    assert duck._intervention_contrast_route_adjustment("investigate", "cautious_inquiry") > 0.0


def test_negative_matched_contrast_can_reduce_multi_step_route_score():
    duck = LivingDuck(_state("intervention-negative-contrast"))
    for tick in range(1, 5):
        duck.causal_state.observe_transition(
            "ask",
            "explore",
            outcome="violated",
            tick=tick,
            intervention=True,
        )
    for tick in range(5, 9):
        duck.causal_state.observe_transition(
            PLAN_START,
            "explore",
            outcome="fulfilled",
            tick=tick,
        )
    adjustment = duck._intervention_contrast_route_adjustment("investigate", "cautious_inquiry")
    assert adjustment < 0.0
    assert adjustment >= -0.10


def test_intervention_requires_exact_pending_canonical_plan_action():
    duck = LivingDuck(_state("intervention-contract"))
    with pytest.raises(ValueError):
        duck.mark_pending_action_as_intervention("I want to test whether asking first helps.")

    duck.step(
        WorldEvent(
            "observation",
            "Morgan",
            "Morgan asks a routine question.",
            ("social",),
            0.05,
            0.20,
        ),
        allow_inner_speech=False,
    )
    with pytest.raises(ValueError):
        duck.mark_pending_action_as_intervention("I want to test whether replying changes the plan.")


def test_intervention_hypothesis_must_pass_experiential_prose_validation():
    duck = LivingDuck(_state("intervention-firewall"))
    _force_two_step_investigation(duck)
    first = duck.heartbeat(allow_inner_speech=False)
    assert first.selected_action == "ask"
    with pytest.raises(ValueError):
        duck.mark_pending_action_as_intervention("I am 64% certain this will increase success.")


def test_marked_first_step_trains_intervention_transition_not_plain_observation():
    duck = LivingDuck(_state("intervention-sequence"))
    plan = _force_two_step_investigation(duck)
    first = duck.heartbeat(allow_inner_speech=False)
    assert first.selected_action == "ask"
    marked = duck.mark_pending_action_as_intervention(
        "I want to test whether asking first makes the later inspection work better."
    )
    assert marked.action_id == first.action_id

    duck.resolve_outcome(
        first.action_id,
        success=0.91,
        valence=0.18,
        description="The question produced useful context.",
    )
    context = duck.causal_state.context_for(plan.plan_id)
    assert context is not None
    assert context.previous_was_intervention is True
    assert "asking first" in context.intervention_hypothesis
    first_step = duck.causal_state.transition(PLAN_START, "ask")
    assert first_step is not None
    assert first_step.intervention_fulfilled == 1

    second = duck.heartbeat(allow_inner_speech=False)
    assert second.selected_action == "explore"
    duck.resolve_outcome(
        second.action_id,
        success=0.89,
        valence=0.22,
        description="The later inspection succeeded.",
    )

    learned = duck.causal_state.transition("ask", "explore")
    assert learned is not None
    assert learned.fulfilled == 1
    assert learned.intervention_fulfilled == 1
    assert learned.intervention_evidence == 1
    assert learned.observational_evidence == 0


def test_intervention_marker_survives_restart_before_first_outcome(tmp_path):
    root = tmp_path / "intervention-restart"
    host = PersistentDuckHost.open(root, name="Aster", subject_id="intervention-restart")
    host.duck.state.needs.update(_state("template").needs)
    host.duck.state.affect.update(_state("template").affect)
    plan = _force_two_step_investigation(host.duck)
    first = host.duck.heartbeat(allow_inner_speech=False)
    host.duck.mark_pending_action_as_intervention(
        "I want to test whether asking first changes how well the inspection works."
    )
    host.save()

    payload = json.loads((root / "causal_v010.json").read_text(encoding="utf-8"))
    assert first.action_id in payload["pending_interventions"]

    reopened = PersistentDuckHost.open(root)
    restored = reopened.duck.causal_state.intervention_for(first.action_id)
    assert restored is not None
    reopened.duck.resolve_outcome(
        first.action_id,
        success=0.90,
        valence=0.16,
        description="The deliberate inquiry produced context after restart.",
    )
    context = reopened.duck.causal_state.context_for(plan.plan_id)
    assert context is not None
    assert context.previous_was_intervention is True
    assert reopened.duck.causal_state.intervention_for(first.action_id) is None

    second = reopened.duck.heartbeat(allow_inner_speech=False)
    reopened.duck.resolve_outcome(
        second.action_id,
        success=0.88,
        valence=0.20,
        description="The informed inspection succeeded.",
    )
    learned = reopened.duck.causal_state.transition("ask", "explore")
    assert learned is not None
    assert learned.intervention_fulfilled == 1


def test_abandoned_marked_action_drops_intervention_without_training():
    duck = LivingDuck(_state("intervention-abandon"))
    _force_two_step_investigation(duck)
    first = duck.heartbeat(allow_inner_speech=False)
    duck.mark_pending_action_as_intervention(
        "I want to test whether asking first changes what happens next."
    )
    assert duck.causal_state.intervention_for(first.action_id) is not None

    duck.step(
        WorldEvent(
            "observation",
            "world",
            "A separate interruption occurs before the planned action is resolved.",
            ("ordinary",),
            0.0,
            0.20,
        ),
        allow_inner_speech=False,
    )
    assert duck.causal_state.intervention_for(first.action_id) is None
    assert duck.causal_state.transitions == {}
