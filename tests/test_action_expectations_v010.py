from __future__ import annotations

import json

import pytest

from duck import LivingDuck, PersistentDuckHost
from duck.expectations_v010 import ExpectationLedgerState
from duck.living import SubjectState, WorldEvent
from duck.predictive_organism_v010 import LivingDuck as PredictiveLivingDuck


def _state(subject_id: str) -> SubjectState:
    state = SubjectState.create("Aster", subject_id)
    state.needs["energy"] = 0.92
    state.needs["safety"] = 0.90
    state.needs["curiosity"] = 0.82
    state.needs["competence"] = 0.72
    state.needs["coherence"] = 0.80
    state.needs["autonomy"] = 0.70
    state.affect["fear"] = 0.06
    state.affect["unease"] = 0.04
    return state


def _mystery(text: str = "A patterned signal is coming from the old panel.") -> WorldEvent:
    return WorldEvent(
        "observation",
        "world",
        text,
        ("mystery", "novel", "panel"),
        0.05,
        0.45,
    )


def test_public_living_duck_is_action_predictive_composition():
    assert LivingDuck is PredictiveLivingDuck


def test_canonical_plan_step_automatically_predicts_its_own_outcome():
    duck = LivingDuck(_state("action-expectation-plan"))
    duck.state.affect["fear"] = 0.46
    duck.step(_mystery("A sealed instrument is blinking in a pattern."), allow_inner_speech=False)
    assert duck.plans(status="active")

    attempted = duck.heartbeat(allow_inner_speech=False)
    rows = duck.action_expectations(status="open")
    assert len(rows) == 1
    prediction = rows[0]
    assert prediction.action_id == attempted.action_id
    assert prediction.action_name == attempted.selected_action
    assert prediction.min_success == pytest.approx(0.55)
    assert attempted.developer_trace["expectations"]["automatic_action_expectation_id"] == prediction.expectation_id
    assert attempted.inner_cognition.thought is None

    duck.resolve_outcome(
        attempted.action_id,
        success=0.88,
        valence=0.20,
        description="The step produced useful information.",
    )
    resolved = duck.expectation_state.get_action(prediction.expectation_id)
    assert resolved.status == "fulfilled"
    assert resolved.observed_success == pytest.approx(0.88)
    domain = f"action:{attempted.selected_action}"
    assert duck.expectation_state.calibration[domain].fulfilled == 1
    assert any("action_expectation_fulfilled" in memory.tags for memory in duck.state.memories)


def test_failed_plan_action_violates_causal_prediction_and_leaves_prediction_error_memory():
    duck = LivingDuck(_state("action-expectation-failure"))
    duck.step(_mystery("A hidden latch seems to control the unfamiliar panel."), allow_inner_speech=False)
    attempted = duck.heartbeat(allow_inner_speech=False)
    prediction = duck.action_expectations(status="open")[0]

    duck.resolve_outcome(
        attempted.action_id,
        success=0.10,
        valence=-0.35,
        description="Direct inspection did not reveal how the latch works.",
    )

    resolved = duck.expectation_state.get_action(prediction.expectation_id)
    assert resolved.status == "violated"
    assert any(
        "action_expectation_violation" in memory.tags
        and "prediction_error" in memory.tags
        and "inconsistency" in memory.tags
        for memory in duck.state.memories
    )
    domain = f"action:{attempted.selected_action}"
    assert duck.expectation_state.calibration[domain].violated == 1


def test_routine_nonplan_action_does_not_manufacture_action_expectation():
    duck = LivingDuck(_state("action-expectation-control"))
    duck.step(
        WorldEvent(
            "observation",
            "world",
            "The room remains quiet.",
            ("ordinary", "room"),
            0.0,
            0.15,
        ),
        allow_inner_speech=False,
    )
    assert duck.action_expectations() == []


def test_manual_action_prediction_requires_one_pending_canonical_action():
    duck = LivingDuck(_state("action-expectation-manual"))
    with pytest.raises(ValueError):
        duck.register_action_outcome_expectation("I expect this to work.")

    step = duck.step(
        WorldEvent(
            "observation",
            "Morgan",
            "Morgan asks a straightforward question.",
            ("social",),
            0.05,
            0.25,
        ),
        allow_inner_speech=False,
    )
    prediction = duck.register_action_outcome_expectation(
        "I expect my response to go reasonably well.",
        min_success=0.60,
        min_valence=-0.10,
    )
    assert prediction.action_id == step.action_id

    duck.resolve_outcome(
        step.action_id,
        success=0.72,
        valence=0.10,
        description="The exchange went smoothly.",
    )
    assert duck.expectation_state.get_action(prediction.expectation_id).status == "fulfilled"


def test_world_evidence_and_wrong_action_id_cannot_resolve_action_prediction():
    ledger = ExpectationLedgerState()
    prediction = ledger.register_action(
        0,
        "I expect opening the door to work.",
        action_id="act-1",
        action_name="explore",
        min_success=0.60,
        confidence=0.80,
    )
    ledger.evaluate_event(
        WorldEvent(
            "environment",
            "world",
            "The door is open.",
            ("observation",),
            0.0,
            0.20,
            (("door", "open"),),
            True,
        ),
        1,
    )
    assert ledger.get_action(prediction.expectation_id).status == "open"

    assert ledger.evaluate_action_outcome(
        "act-other",
        success=1.0,
        valence=1.0,
        current_tick=1,
    ) == ()
    assert ledger.get_action(prediction.expectation_id).status == "open"

    resolution = ledger.evaluate_action_outcome(
        "act-1",
        success=0.75,
        valence=0.10,
        current_tick=1,
    )
    assert resolution[0].outcome == "fulfilled"


def test_overwritten_pending_action_retires_unresolved_prediction_without_training():
    duck = LivingDuck(_state("action-expectation-retire"))
    first = duck.step(
        WorldEvent("observation", "world", "A switch is visible.", ("ordinary",), 0.0, 0.20),
        allow_inner_speech=False,
    )
    prediction = duck.register_action_outcome_expectation(
        "I expect this first action to work.",
        confidence=0.82,
    )
    duck.step(
        WorldEvent("observation", "world", "A second event interrupts me.", ("ordinary",), 0.0, 0.20),
        allow_inner_speech=False,
    )
    retired = duck.expectation_state.get_action(prediction.expectation_id)
    assert retired.status == "retired"
    assert f"action:{first.selected_action}" not in duck.expectation_state.calibration


def test_action_calibration_changes_later_default_action_confidence():
    ledger = ExpectationLedgerState()
    first = ledger.register_action(
        0,
        "I expect exploring to work.",
        action_id="act-1",
        action_name="explore",
        min_success=0.60,
        confidence=None,
    )
    assert first.confidence == pytest.approx(0.70)
    ledger.evaluate_action_outcome(
        "act-1",
        success=0.10,
        valence=-0.20,
        current_tick=1,
    )
    learned = ledger.learned_confidence("action:explore")
    assert learned < 0.70

    second = ledger.register_action(
        2,
        "I expect exploring to work this time.",
        action_id="act-2",
        action_name="explore",
        min_success=0.60,
        confidence=None,
    )
    assert second.confidence == pytest.approx(learned)


def test_resolved_causal_reliability_changes_future_route_scores_without_neutral_prior_bias():
    duck = LivingDuck(_state("action-route-calibration"))
    base_direct = duck._route_score("investigate", "direct_exploration")
    base_cautious = duck._route_score("investigate", "cautious_inquiry")
    assert duck._action_prediction_route_adjustment("explore") == pytest.approx(0.0)
    assert duck._action_prediction_route_adjustment("ask") == pytest.approx(0.0)

    for index in range(4):
        action_id = f"explore-fail-{index}"
        duck.expectation_state.register_action(
            index,
            "I expect exploring to work.",
            action_id=action_id,
            action_name="explore",
            min_success=0.55,
            confidence=None,
        )
        duck.expectation_state.evaluate_action_outcome(
            action_id,
            success=0.10,
            valence=-0.20,
            current_tick=index + 1,
        )

        action_id = f"ask-hit-{index}"
        duck.expectation_state.register_action(
            index,
            "I expect asking to work.",
            action_id=action_id,
            action_name="ask",
            min_success=0.55,
            confidence=None,
        )
        duck.expectation_state.evaluate_action_outcome(
            action_id,
            success=0.90,
            valence=0.20,
            current_tick=index + 1,
        )

    explore_adjustment = duck._action_prediction_route_adjustment("explore")
    ask_adjustment = duck._action_prediction_route_adjustment("ask")
    assert explore_adjustment < 0.0
    assert ask_adjustment > 0.0

    learned_direct = duck._route_score("investigate", "direct_exploration")
    learned_cautious = duck._route_score("investigate", "cautious_inquiry")
    assert learned_direct < base_direct
    assert learned_cautious > base_cautious
    assert (learned_cautious - learned_direct) > (base_cautious - base_direct) + 0.25


def test_pending_action_expectation_survives_public_host_restart_and_resolves(tmp_path):
    root = tmp_path / "predictive-host-restart"
    host = PersistentDuckHost.open(root, name="Aster", subject_id="predictive-host-restart")
    host.duck.state.needs.update(_state("template").needs)
    host.duck.state.affect["fear"] = 0.46
    host.duck.step(_mystery("A strange instrument is blinking in a pattern."), allow_inner_speech=False)
    attempted = host.duck.heartbeat(allow_inner_speech=False)
    prediction = host.duck.action_expectations(status="open")[0]
    assert prediction.action_id == attempted.action_id
    host.save()

    payload = json.loads((root / "expectations_v010.json").read_text(encoding="utf-8"))
    assert payload["action_records"][0]["expectation_id"] == prediction.expectation_id

    reopened = PersistentDuckHost.open(root)
    assert isinstance(reopened.duck, PredictiveLivingDuck)
    assert reopened.duck.state.pending_action is not None
    assert reopened.duck.state.pending_action.action_id == attempted.action_id
    restored = reopened.duck.expectation_state.get_action(prediction.expectation_id)
    assert restored.status == "open"
    assert reopened.status()["active_action_expectation_count"] == 1

    reopened.duck.resolve_outcome(
        attempted.action_id,
        success=0.86,
        valence=0.18,
        description="The planned step worked after restart.",
    )
    assert reopened.duck.expectation_state.get_action(prediction.expectation_id).status == "fulfilled"
