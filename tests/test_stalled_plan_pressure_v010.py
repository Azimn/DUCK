from __future__ import annotations

from duck import LivingDuck, PersistentDuckHost, SubjectState
from duck.living import MemoryProvenance


def _state(subject_id: str) -> SubjectState:
    state = SubjectState.create("Aster", subject_id)
    state.affect["fear"] = 0.02
    state.affect["unease"] = 0.03
    state.affect["loneliness"] = 0.15
    state.needs["energy"] = 0.90
    state.needs["safety"] = 0.95
    state.needs["curiosity"] = 0.55
    state.needs["competence"] = 0.72
    state.needs["coherence"] = 0.82
    state.needs["autonomy"] = 0.72
    state.needs["affiliation"] = 0.18
    return state


def _dynamics(step) -> dict:
    return step.developer_trace["endogenous_dynamics"]


def _require_context_for_current_plan(duck: LivingDuck, tag: str = "lab_open"):
    plan = duck.plans(status="active")[0]
    assert plan.pending_concern_id is not None
    memory = duck._concern_memory(plan.pending_concern_id)
    memory.tags = tuple(
        dict.fromkeys(
            (
                *memory.tags,
                f"pc_required:{tag}",
            )
        )
    )
    return plan, duck._concern_from_memory(memory)


def test_repeatedly_blocked_active_plan_becomes_sparse_endogenous_pressure():
    duck = LivingDuck(_state("stalled-plan-context"))
    duck.form_goal("investigate", "I want to understand the sealed instrument panel.")
    plan, concern = _require_context_for_current_plan(duck)

    first = duck.heartbeat(allow_inner_speech=False)
    second = duck.heartbeat(allow_inner_speech=False)
    assert _dynamics(first)["emitted"] is False
    assert _dynamics(second)["emitted"] is False

    third = duck.heartbeat(allow_inner_speech=False)
    trace = _dynamics(third)
    key = f"plan:{plan.plan_id}"
    assert trace["emitted"] is True
    assert trace["signal"]["kind"] == "plan"
    assert trace["signal"]["key"] == key
    assert "plan_pressure" in trace["signal"]["tags"]
    assert "stall_context_missing" in trace["signal"]["tags"]
    assert duck.endogenous_state.emission_counts[key] == 1
    assert third.developer_trace["executive_recruitment"]["invoked"] is False
    assert concern.preferred_action in {"ask", "explore"}

    immediate = duck.heartbeat(allow_inner_speech=False)
    assert not (
        _dynamics(immediate).get("emitted") is True
        and _dynamics(immediate).get("signal", {}).get("key") == key
    )
    assert duck.endogenous_state.emission_counts[key] == 1


def test_new_context_retires_plan_pressure_and_normal_plan_execution_resumes():
    duck = LivingDuck(_state("stalled-plan-resume"))
    duck.form_goal("investigate", "I want to inspect the sealed instrument panel.")
    plan, concern = _require_context_for_current_plan(duck)

    duck.heartbeat(allow_inner_speech=False)
    duck.heartbeat(allow_inner_speech=False)
    pressure = duck.heartbeat(allow_inner_speech=False)
    key = f"plan:{plan.plan_id}"
    assert _dynamics(pressure)["signal"]["key"] == key
    assert key in duck.endogenous_state.latched_signals

    duck.state.add_memory(
        "The lab is open now.",
        tags=("lab_open",),
        valence=0.05,
        arousal=0.20,
        importance=0.55,
        provenance=MemoryProvenance.FIRST_PERSON,
        source="world",
    )
    resumed = duck.heartbeat(allow_inner_speech=False)
    trace = _dynamics(resumed)
    assert trace["emitted"] is False
    assert trace["reason"] == "prospective_concern_priority"
    assert resumed.developer_trace["agency"]["selected_concern_id"] == concern.concern_id
    assert resumed.selected_action == concern.preferred_action
    assert key not in duck.endogenous_state.latched_signals
    assert key not in duck.endogenous_state.last_emitted_tick


def test_intentionally_future_scheduled_concern_does_not_count_as_stalled_plan():
    duck = LivingDuck(_state("scheduled-plan-not-stalled"))
    duck.form_goal("investigate", "I want to inspect the panel later.")
    plan = duck.plans(status="active")[0]
    assert plan.pending_concern_id is not None
    memory = duck._concern_memory(plan.pending_concern_id)
    memory.tags = tuple(
        dict.fromkeys(
            (
                *(tag for tag in memory.tags if not tag.startswith("pc_not_before:")),
                f"pc_not_before:{duck.state.tick + 6}",
            )
        )
    )

    for _ in range(4):
        step = duck.heartbeat(allow_inner_speech=False)
        trace = _dynamics(step)
        assert not (
            trace.get("emitted") is True
            and trace.get("signal", {}).get("kind") == "plan"
        )
    assert duck.endogenous_state.emission_counts.get(f"plan:{plan.plan_id}", 0) == 0


def test_stalled_plan_cooldown_survives_host_restart(tmp_path):
    root = tmp_path / "stalled-plan-host"
    host = PersistentDuckHost.open(root, name="Aster", subject_id="stalled-plan-restart")
    host.duck.state.needs.update(_state("unused").needs)
    host.duck.state.affect.update(_state("unused").affect)
    host.duck.form_goal("investigate", "I want to inspect the sealed panel.")
    plan, _ = _require_context_for_current_plan(host.duck)

    host.heartbeat(2, allow_inner_speech=False)
    emitted = host.heartbeat(1, allow_inner_speech=False)[0]
    key = f"plan:{plan.plan_id}"
    assert _dynamics(emitted)["signal"]["key"] == key
    assert host.duck.endogenous_state.emission_counts[key] == 1
    host.save()

    reopened = PersistentDuckHost.open(root)
    assert reopened.duck.state.subject_id == "stalled-plan-restart"
    assert reopened.duck.endogenous_state.emission_counts[key] == 1
    next_step = reopened.heartbeat(1, allow_inner_speech=False)[0]
    assert not (
        _dynamics(next_step).get("emitted") is True
        and _dynamics(next_step).get("signal", {}).get("key") == key
    )
    assert reopened.duck.endogenous_state.emission_counts[key] == 1
