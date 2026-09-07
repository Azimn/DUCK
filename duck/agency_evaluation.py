"""Focused prospective-agency probes for the DUCK v0.8 candidate."""
from __future__ import annotations

from .living import SubjectState, WorldEvent
from .living_v08 import LivingDuck


def opportunity_without_prompt() -> dict:
    duck = LivingDuck(SubjectState.create(name="Aster", subject_id="agency-opportunity"))
    opportunity = duck.register_opportunity(
        "I want to inspect the blue flower when I have a quiet moment.",
        tags=("garden", "flower"),
        importance=0.86,
    )
    steps = [duck.heartbeat(allow_inner_speech=False) for _ in range(3)]
    acted = [step for step in steps if step.selected_action == "explore"]
    return {
        "name": "opportunity_without_prompt",
        "passed": bool(acted) and "opportunity_acted" in opportunity.tags,
        "actions": [step.selected_action for step in steps],
        "acted_tick": acted[0].tick if acted else None,
    }


def opportunity_survives_restart() -> dict:
    state = SubjectState.create(name="Aster", subject_id="agency-restart")
    duck = LivingDuck(state)
    concern = duck.register_concern(
        "I want to look at the old map when I get a chance.",
        tags=("map", "investigate"),
        priority=0.84,
        preferred_action="explore",
    )
    restored = SubjectState.from_dict(state.to_dict())
    reopened = LivingDuck(restored)
    step = reopened.heartbeat(allow_inner_speech=False)
    persisted = reopened._concern_memory(concern.memory_id)
    return {
        "name": "opportunity_survives_restart",
        "passed": step.selected_action == "explore" and "opportunity_acted" in persisted.tags,
        "same_subject": reopened.state.subject_id == state.subject_id,
        "action": step.selected_action,
    }


def competing_concerns_choose_most_motivated() -> dict:
    duck = LivingDuck(SubjectState.create(name="Aster", subject_id="agency-competition"))
    low = duck.register_concern(
        "I would like to inspect a decorative stone sometime.",
        priority=0.44,
        urgency=0.20,
        preferred_action="explore",
    )
    high = duck.register_concern(
        "I need to check whether Morgan is still waiting for my answer.",
        tags=("social",),
        priority=0.92,
        urgency=0.86,
        preferred_action="ask",
        due_in=0,
        min_energy=0.15,
    )
    step = duck.heartbeat(allow_inner_speech=False)
    agency = step.developer_trace.get("agency", {})
    return {
        "name": "competing_concerns_choose_most_motivated",
        "passed": agency.get("selected_concern_id") == high.memory_id and step.selected_action == "ask",
        "selected": agency.get("selected_concern_id"),
        "high": high.memory_id,
        "low": low.memory_id,
        "action": step.selected_action,
    }


def low_energy_defers_then_resumes() -> dict:
    duck = LivingDuck(SubjectState.create(name="Aster", subject_id="agency-energy"))
    concern = duck.register_concern(
        "I want to explore the garden path.",
        priority=0.90,
        urgency=0.65,
        preferred_action="explore",
        min_energy=0.55,
    )
    duck.state.needs["energy"] = 0.20
    first = duck.heartbeat(allow_inner_speech=False)
    before = duck._concern_from_memory(duck._concern_memory(concern.memory_id))
    duck.state.needs["energy"] = 0.82
    second = duck.heartbeat(allow_inner_speech=False)
    return {
        "name": "low_energy_defers_then_resumes",
        "passed": first.selected_action != "explore" and before.deferrals >= 1 and second.selected_action == "explore",
        "first": first.selected_action,
        "second": second.selected_action,
        "deferrals": before.deferrals,
    }


def safety_overrides_curiosity_then_releases() -> dict:
    duck = LivingDuck(SubjectState.create(name="Aster", subject_id="agency-safety"))
    concern = duck.register_concern(
        "I want to inspect the strange machine.",
        priority=0.92,
        urgency=0.72,
        preferred_action="explore",
        min_energy=0.20,
    )
    duck.state.affect["fear"] = 0.80
    first = duck.heartbeat(allow_inner_speech=False)
    blocked = duck._concern_from_memory(duck._concern_memory(concern.memory_id))
    duck.state.affect["fear"] = 0.08
    second = duck.heartbeat(allow_inner_speech=False)
    return {
        "name": "safety_overrides_curiosity_then_releases",
        "passed": first.selected_action != "explore" and blocked.deferrals >= 1 and second.selected_action == "explore",
        "first": first.selected_action,
        "second": second.selected_action,
    }


def context_gates_action() -> dict:
    duck = LivingDuck(SubjectState.create(name="Aster", subject_id="agency-context"))
    concern = duck.register_concern(
        "I want to inspect the blue flower when I am in the garden.",
        priority=0.88,
        urgency=0.62,
        preferred_action="explore",
        required_tags=("garden",),
    )
    before = duck.heartbeat(allow_inner_speech=False)
    duck.step(
        WorldEvent("observation", "world", "I am standing in the garden beside the blue flower.", ("garden", "flower"), 0.1, 0.3),
        allow_inner_speech=False,
    )
    after = duck.heartbeat(allow_inner_speech=False)
    return {
        "name": "context_gates_action",
        "passed": before.selected_action != "explore" and after.selected_action == "explore",
        "before": before.selected_action,
        "after": after.selected_action,
        "concern": concern.memory_id,
    }


def interruption_preserves_unfinished_intention() -> dict:
    duck = LivingDuck(SubjectState.create(name="Aster", subject_id="agency-interruption"))
    concern = duck.register_concern(
        "I want to review the map later.",
        priority=0.82,
        urgency=0.55,
        preferred_action="explore",
        not_before_in=2,
    )
    duck.step(WorldEvent("message", "Jay", "Can you help me with something first?", ("social", "question"), 0.0, 0.4), allow_inner_speech=False)
    still_open = any(row.concern_id == concern.memory_id for row in duck.concerns(status="open"))
    first_quiet = duck.heartbeat(allow_inner_speech=False)
    second_quiet = duck.heartbeat(allow_inner_speech=False)
    return {
        "name": "interruption_preserves_unfinished_intention",
        "passed": still_open and (first_quiet.selected_action == "explore" or second_quiet.selected_action == "explore"),
        "actions": [first_quiet.selected_action, second_quiet.selected_action],
    }


def satisfied_and_abandoned_concerns_stop_competing() -> dict:
    duck = LivingDuck(SubjectState.create(name="Aster", subject_id="agency-resolution"))
    satisfied = duck.register_concern("I want to inspect the map.", priority=0.9, preferred_action="explore")
    abandoned = duck.register_concern("I want to search the closed tunnel.", priority=0.88, preferred_action="explore")
    duck.resolve_concern(satisfied.memory_id, satisfied=True, reason="I finished reviewing the map.")
    duck.mark_concern_impossible(abandoned.memory_id, reason="The tunnel collapsed and cannot be entered.")
    steps = [duck.heartbeat(allow_inner_speech=False) for _ in range(6)]
    return {
        "name": "satisfied_and_abandoned_concerns_stop_competing",
        "passed": not duck.concerns(status="open") and all("agency" not in step.developer_trace for step in steps),
        "actions": [step.selected_action for step in steps],
    }


def commitment_followup_becomes_endogenous() -> dict:
    duck = LivingDuck(SubjectState.create(name="Aster", subject_id="agency-commitment"))
    commitment = duck.create_commitment("Morgan", "Morgan will bring the map.", due_in=1, importance=0.9)
    concern = duck.register_commitment_followup(commitment)
    duck.heartbeat(allow_inner_speech=False)
    due_step = duck.heartbeat(allow_inner_speech=False)
    selected = due_step.developer_trace.get("agency", {}).get("selected_concern_id")
    duck.resolve_commitment(commitment.commitment_id, kept=True, outcome="Morgan brought the map.")
    duck.heartbeat(allow_inner_speech=False)
    status = duck._concern_from_memory(duck._concern_memory(concern.memory_id)).status
    return {
        "name": "commitment_followup_becomes_endogenous",
        "passed": selected == concern.memory_id and due_step.selected_action == "ask" and status == "satisfied",
        "action": due_step.selected_action,
        "status_after_resolution": status,
    }


def no_opportunity_no_false_goal() -> dict:
    duck = LivingDuck(SubjectState.create(name="Aster", subject_id="agency-control"))
    steps = [duck.heartbeat(allow_inner_speech=False) for _ in range(8)]
    opportunity_memories = [memory.memory_id for memory in duck.state.memories if "opportunity" in memory.tags]
    return {
        "name": "no_opportunity_no_false_goal",
        "passed": not opportunity_memories and not duck.concerns(status="open") and all("agency" not in step.developer_trace for step in steps),
        "actions": [step.selected_action for step in steps],
    }


def bounded_multi_concern_field() -> dict:
    duck = LivingDuck(SubjectState.create(name="Aster", subject_id="agency-bounded"))
    for index in range(6):
        duck.register_concern(
            f"I want to investigate item {index} when I can.",
            priority=0.58 + index * 0.05,
            urgency=0.30 + index * 0.04,
            preferred_action="explore" if index % 2 == 0 else "ask",
        )
    steps = [duck.heartbeat(allow_inner_speech=False) for _ in range(24)]
    actions = [step.selected_action for step in steps]
    active = [action for action in actions if action not in {"wait", "rest", "step_back"}]
    max_run = 0
    current = 0
    previous = None
    for action in actions:
        current = current + 1 if action == previous else 1
        previous = action
        max_run = max(max_run, current)
    attempted = sum(row.attempts for row in duck.concerns(status="open"))
    return {
        "name": "bounded_multi_concern_field",
        "passed": len(active) >= 2 and max_run <= 6 and attempted <= 24,
        "actions": actions,
        "active_count": len(active),
        "max_run": max_run,
        "attempts": attempted,
    }


def run() -> dict:
    results = [
        opportunity_without_prompt(),
        opportunity_survives_restart(),
        competing_concerns_choose_most_motivated(),
        low_energy_defers_then_resumes(),
        safety_overrides_curiosity_then_releases(),
        context_gates_action(),
        interruption_preserves_unfinished_intention(),
        satisfied_and_abandoned_concerns_stop_competing(),
        commitment_followup_becomes_endogenous(),
        no_opportunity_no_false_goal(),
        bounded_multi_concern_field(),
    ]
    return {"suite": "DUCK motivated prospective agency evaluation v0.8", "passed": all(row["passed"] for row in results), "results": results}


if __name__ == "__main__":
    import json

    report = run()
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report["passed"] else 1)
