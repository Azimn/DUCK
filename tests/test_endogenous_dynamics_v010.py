from __future__ import annotations

import json

import pytest

from duck import LivingDuck, PersistentDuckHost, SubjectState
from duck.endogenous import EndogenousDynamicsState


def _state(subject_id: str) -> SubjectState:
    state = SubjectState.create("Aster", subject_id)
    state.affect["fear"] = 0.02
    state.affect["unease"] = 0.03
    state.affect["loneliness"] = 0.15
    state.needs["energy"] = 0.94
    state.needs["safety"] = 0.95
    state.needs["curiosity"] = 0.55
    state.needs["competence"] = 0.72
    state.needs["coherence"] = 0.82
    state.needs["autonomy"] = 0.72
    state.needs["affiliation"] = 0.18
    return state


def _dynamics(step) -> dict:
    return step.developer_trace["endogenous_dynamics"]


def test_low_energy_crossing_emits_once_and_recruits_rest_affordance():
    state = _state("endogenous-energy")
    state.needs["energy"] = 0.18
    duck = LivingDuck(state)

    first = duck.heartbeat(allow_inner_speech=False)
    first_trace = _dynamics(first)
    assert first_trace["emitted"] is True
    assert first_trace["signal"]["kind"] == "energy"
    assert first.selected_action == "rest"
    assert first.inner_cognition.thought is None
    assert duck.endogenous_state.emission_counts["energy"] == 1

    second = duck.heartbeat(allow_inner_speech=False)
    second_trace = _dynamics(second)
    assert second_trace["emitted"] is False
    assert duck.endogenous_state.emission_counts["energy"] == 1


def test_recovery_rearms_energy_signal_for_a_later_real_crossing():
    state = _state("endogenous-energy-rearm")
    state.needs["energy"] = 0.18
    duck = LivingDuck(state)
    duck.heartbeat(allow_inner_speech=False)
    assert "energy" in duck.endogenous_state.latched_signals

    duck.state.needs["energy"] = 0.72
    recovered = duck.heartbeat(allow_inner_speech=False)
    assert _dynamics(recovered)["emitted"] is False
    assert "energy" not in duck.endogenous_state.latched_signals

    duck.state.needs["energy"] = 0.18
    repeated = duck.heartbeat(allow_inner_speech=False)
    assert _dynamics(repeated)["signal"]["kind"] == "energy"
    assert duck.endogenous_state.emission_counts["energy"] == 2


def test_affiliation_pressure_can_initiate_connection_without_external_prompt():
    state = _state("endogenous-affiliation")
    state.needs["affiliation"] = 0.90
    state.affect["loneliness"] = 0.78
    duck = LivingDuck(state)

    step = duck.heartbeat(allow_inner_speech=False)
    trace = _dynamics(step)
    assert trace["emitted"] is True
    assert trace["signal"]["kind"] == "affiliation"
    assert step.selected_action == "seek_connection"
    assert duck.control.dominant_motive() is not None
    assert duck.control.dominant_motive().theme == "affiliation"


def test_due_commitment_can_generate_one_targeted_followup_signal():
    state = _state("endogenous-commitment")
    duck = LivingDuck(state)
    commitment = duck.create_commitment(
        "Morgan",
        "Morgan will bring the map.",
        due_in=1,
        importance=0.90,
    )

    first = duck.heartbeat(allow_inner_speech=False)
    trace = _dynamics(first)
    key = f"commitment:{commitment.commitment_id}"
    assert trace["emitted"] is True
    assert trace["signal"]["kind"] == "commitment"
    assert trace["signal"]["key"] == key
    assert first.selected_action == "ask"
    assert duck.endogenous_state.emission_counts[key] == 1

    second = duck.heartbeat(allow_inner_speech=False)
    assert _dynamics(second)["emitted"] is False
    assert duck.endogenous_state.emission_counts[key] == 1


def test_actionable_prospective_concern_has_priority_over_generic_social_signal():
    state = _state("endogenous-concern-priority")
    state.needs["curiosity"] = 0.88
    state.needs["affiliation"] = 0.90
    state.affect["loneliness"] = 0.78
    duck = LivingDuck(state)
    concern = duck.register_concern(
        "I want to inspect the workbench when I have a chance.",
        tags=("workbench",),
        priority=0.92,
        urgency=0.80,
        preferred_action="explore",
        min_energy=0.20,
        blocked_tags=(),
    )

    step = duck.heartbeat(allow_inner_speech=False)
    trace = _dynamics(step)
    assert trace["emitted"] is False
    assert trace["reason"] == "prospective_concern_priority"
    assert step.developer_trace["agency"]["selected_concern_id"] == concern.memory_id
    assert step.selected_action == "explore"
    assert duck.endogenous_state.emission_counts.get("affiliation", 0) == 0


def test_endogenous_latch_state_survives_restart_without_duplicate_alarm(tmp_path):
    root = tmp_path / "continuous-host"
    host = PersistentDuckHost.open(root, name="Aster", subject_id="endogenous-restart")
    host.duck.state.needs["energy"] = 0.18
    first = host.heartbeat(1, allow_inner_speech=False)[0]
    assert _dynamics(first)["signal"]["kind"] == "energy"
    host.save()

    dynamics_path = root / "endogenous_v010.json"
    assert dynamics_path.exists()
    payload = json.loads(dynamics_path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "micropsi-duck.endogenous.v1"
    assert "energy" in payload["latched_signals"]
    assert payload["emission_counts"]["energy"] == 1

    reopened = PersistentDuckHost.open(root)
    assert reopened.duck.state.subject_id == "endogenous-restart"
    assert reopened.duck.endogenous_state.emission_counts["energy"] == 1
    second = reopened.heartbeat(1, allow_inner_speech=False)[0]
    assert _dynamics(second)["emitted"] is False
    assert reopened.duck.endogenous_state.emission_counts["energy"] == 1


def test_endogenous_state_schema_rejects_unknown_versions():
    with pytest.raises(ValueError):
        EndogenousDynamicsState.from_dict(
            {
                "schema_version": "micropsi-duck.endogenous.v999",
                "latched_signals": [],
                "last_emitted_tick": {},
                "emission_counts": {},
            }
        )


def test_endogenous_signal_path_operates_under_language_lesion():
    state = _state("endogenous-lesion")
    state.needs["energy"] = 0.18
    duck = LivingDuck(state)
    step = duck.heartbeat(allow_inner_speech=False)

    assert _dynamics(step)["signal"]["kind"] == "energy"
    assert step.selected_action == "rest"
    assert step.inner_cognition.thought is None
    assert step.developer_trace["executive_recruitment"]["invoked"] is False
    assert duck.current_cycle is not None


def test_curiosity_pressure_can_initiate_exploration_once_when_safe():
    state = _state("endogenous-curiosity")
    state.needs["curiosity"] = 0.93
    duck = LivingDuck(state)

    first = duck.heartbeat(allow_inner_speech=False)
    trace = _dynamics(first)
    assert trace["emitted"] is True
    assert trace["signal"]["kind"] == "curiosity"
    assert first.selected_action == "explore"
    assert first.developer_trace["executive_recruitment"]["invoked"] is False
    assert duck.endogenous_state.emission_counts["curiosity"] == 1

    second = duck.heartbeat(allow_inner_speech=False)
    assert _dynamics(second)["emitted"] is False
    assert duck.endogenous_state.emission_counts["curiosity"] == 1


def test_safety_pressure_blocks_curiosity_signal_until_conditions_recover():
    state = _state("endogenous-curiosity-safety")
    state.needs["curiosity"] = 0.95
    state.needs["safety"] = 0.20
    state.affect["fear"] = 0.88
    duck = LivingDuck(state)

    threatened = duck.heartbeat(allow_inner_speech=False)
    assert _dynamics(threatened)["signal"]["kind"] == "safety"
    assert duck.endogenous_state.emission_counts.get("curiosity", 0) == 0

    duck.state.needs["safety"] = 0.92
    duck.state.affect["fear"] = 0.08
    recovered = duck.heartbeat(allow_inner_speech=False)
    assert _dynamics(recovered)["signal"]["kind"] == "curiosity"
    assert recovered.selected_action == "explore"


def test_recent_contradiction_can_become_endogenous_coherence_pressure():
    state = _state("endogenous-coherence")
    state.add_memory(
        "The new observation contradicts what I expected.",
        tags=("observation", "contradiction"),
        valence=-0.20,
        arousal=0.55,
        importance=0.75,
        source="world",
    )
    duck = LivingDuck(state)

    step = duck.heartbeat(allow_inner_speech=False)
    trace = _dynamics(step)
    assert trace["emitted"] is True
    assert trace["signal"]["kind"] == "coherence"
    assert step.selected_action == "ask"
    assert step.developer_trace["executive_recruitment"]["invoked"] is False
    assert duck.control.dominant_motive() is not None
    assert duck.control.dominant_motive().theme == "coherence"


def test_coherence_signal_rearms_only_after_resolution_and_a_new_disruption():
    state = _state("endogenous-coherence-rearm")
    state.add_memory(
        "Something does not fit the explanation I had.",
        tags=("inconsistency",),
        valence=-0.10,
        arousal=0.45,
        importance=0.70,
        source="world",
    )
    duck = LivingDuck(state)
    duck.heartbeat(allow_inner_speech=False)
    assert duck.endogenous_state.emission_counts["coherence"] == 1

    duck.state.needs["coherence"] = 0.86
    duck.state.affect["unease"] = 0.05
    duck.state.tick += 9
    quiet = duck.heartbeat(allow_inner_speech=False)
    assert _dynamics(quiet)["emitted"] is False
    assert "coherence" not in duck.endogenous_state.latched_signals

    duck.state.add_memory(
        "A later observation conflicts with the repaired explanation.",
        tags=("expectation_violation",),
        valence=-0.10,
        arousal=0.45,
        importance=0.70,
        source="world",
    )
    repeated = duck.heartbeat(allow_inner_speech=False)
    assert _dynamics(repeated)["signal"]["kind"] == "coherence"
    assert duck.endogenous_state.emission_counts["coherence"] == 2
