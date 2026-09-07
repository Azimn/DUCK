"""Focused evaluation probes for DUCK v0.9 endogenous planning."""
from __future__ import annotations

from .living import SubjectState, WorldEvent
from .living_v09 import LivingDuck


def _mystery_event(text: str = "A faint patterned signal is coming from the old panel.") -> WorldEvent:
    return WorldEvent("observation", "world", text, ("mystery", "novel", "panel"), 0.05, 0.45)


def _subjective_lines(step) -> list[str]:
    moment = step.subjective_moment
    rows = [item.content for item in moment.impressions]
    rows.extend(item.felt_as for item in moment.tendencies)
    rows.extend(moment.recollections)
    rows.extend(moment.beliefs)
    rows.extend(moment.concerns)
    rows.extend(moment.temporal_context)
    rows.extend(moment.self_context)
    return [row for row in dict.fromkeys(rows) if row]


def _plan_step_rows(duck: LivingDuck) -> list[dict]:
    rows: list[dict] = []
    for concern in duck.concerns(status=None):
        memory = duck._concern_memory(concern.concern_id)
        if "plan_step" not in memory.tags:
            continue
        rows.append(
            {
                "concern_id": concern.concern_id,
                "status": concern.status,
                "text": concern.text,
                "preferred_action": concern.preferred_action,
                "plan_tags": [tag for tag in memory.tags if tag.startswith("pl_")],
            }
        )
    return rows


def experience_forms_goal_without_instruction() -> dict:
    duck = LivingDuck(SubjectState.create(name="Aster", subject_id="planning-formation"))
    duck.state.needs["curiosity"] = 0.78
    step = duck.step(_mystery_event(), allow_inner_speech=False)
    plans = duck.plans(status="active")
    open_plan_steps = [row for row in duck.concerns(status="open") if "plan_step" in duck._concern_memory(row.concern_id).tags]
    return {
        "name": "experience_forms_goal_without_instruction",
        "passed": len(plans) == 1 and len(open_plan_steps) == 1 and "goal_formation" in step.developer_trace,
        "plan_kind": plans[0].kind if plans else None,
        "route": plans[0].current_route if plans else None,
        "open_plan_steps": len(open_plan_steps),
    }


def counterfactual_route_changes_with_risk() -> dict:
    low = LivingDuck(SubjectState.create(name="Aster", subject_id="planning-low-risk"))
    low.state.needs["curiosity"] = 0.80
    low.state.affect["fear"] = 0.06
    low.step(_mystery_event("An unfamiliar blue mechanism is humming quietly."), allow_inner_speech=False)
    low_plan = low.plans(status="active")[0]

    high = LivingDuck(SubjectState.create(name="Aster", subject_id="planning-higher-risk"))
    high.state.needs["curiosity"] = 0.80
    high.state.affect["fear"] = 0.46
    high.step(_mystery_event("An unfamiliar blue mechanism is humming quietly."), allow_inner_speech=False)
    high_plan = high.plans(status="active")[0]
    return {
        "name": "counterfactual_route_changes_with_risk",
        "passed": low_plan.current_route == "direct_exploration" and high_plan.current_route == "cautious_inquiry",
        "low_risk_route": low_plan.current_route,
        "higher_risk_route": high_plan.current_route,
    }


def hierarchical_plan_advances_through_subgoals() -> dict:
    duck = LivingDuck(SubjectState.create(name="Aster", subject_id="planning-hierarchy"))
    duck.state.needs["curiosity"] = 0.82
    duck.state.affect["fear"] = 0.46
    duck.step(_mystery_event("A strange sealed instrument is blinking in a pattern."), allow_inner_speech=False)
    initial = duck.plans(status="active")[0]
    first = duck.heartbeat(allow_inner_speech=False)
    duck.resolve_outcome(first.action_id, success=0.88, valence=0.20, description="The question produced useful information.")
    middle = duck.plans(status="active")[0]
    second = duck.heartbeat(allow_inner_speech=False)
    duck.resolve_outcome(second.action_id, success=0.91, valence=0.28, description="The instrument was inspected successfully.")
    completed = duck.plans(status="completed")
    lifecycle = _plan_step_rows(duck)
    open_plan_steps = [row for row in lifecycle if row["status"] == "open"]
    return {
        "name": "hierarchical_plan_advances_through_subgoals",
        "passed": (
            initial.current_route == "cautious_inquiry"
            and first.selected_action == "ask"
            and middle.step_index == 1
            and second.selected_action == "explore"
            and len(completed) == 1
            and not open_plan_steps
        ),
        "first_action": first.selected_action,
        "middle_step": middle.step_index,
        "second_action": second.selected_action,
        "completed": len(completed),
        "plan_step_lifecycle": lifecycle,
        "open_plan_steps": open_plan_steps,
    }


def failed_route_causes_counterfactual_replanning() -> dict:
    duck = LivingDuck(SubjectState.create(name="Aster", subject_id="planning-replan"))
    duck.state.needs["curiosity"] = 0.84
    duck.state.affect["fear"] = 0.05
    duck.step(_mystery_event("A hidden latch seems to control the unfamiliar panel."), allow_inner_speech=False)
    before = duck.plans(status="active")[0]
    attempted = duck.heartbeat(allow_inner_speech=False)
    duck.resolve_outcome(attempted.action_id, success=0.10, valence=-0.35, description="Direct inspection did not reveal how the latch works.")
    after = duck.plans(status="active")[0]
    current = duck._concern_from_memory(duck._concern_memory(after.pending_concern_id)) if after.pending_concern_id else None
    revisions = [memory for memory in duck.state.memories if "counterfactual_revision" in memory.tags]
    return {
        "name": "failed_route_causes_counterfactual_replanning",
        "passed": (
            before.current_route == "direct_exploration"
            and attempted.selected_action == "explore"
            and after.current_route == "cautious_inquiry"
            and after.route_index == 1
            and current is not None
            and current.preferred_action == "ask"
            and bool(revisions)
        ),
        "before_route": before.current_route,
        "attempted": attempted.selected_action,
        "after_route": after.current_route,
        "next_action": current.preferred_action if current else None,
    }


def plan_survives_state_roundtrip() -> dict:
    state = SubjectState.create(name="Aster", subject_id="planning-restart")
    duck = LivingDuck(state)
    duck.state.needs["curiosity"] = 0.80
    duck.step(_mystery_event("A set of unknown symbols appeared on the display."), allow_inner_speech=False)
    before = duck.plans(status="active")[0]
    restored = SubjectState.from_dict(state.to_dict())
    reopened = LivingDuck(restored)
    after = reopened.plans(status="active")[0]
    concern = reopened._concern_from_memory(reopened._concern_memory(after.pending_concern_id)) if after.pending_concern_id else None
    return {
        "name": "plan_survives_state_roundtrip",
        "passed": (
            before.plan_id == after.plan_id
            and before.current_route == after.current_route
            and before.step_index == after.step_index
            and concern is not None
            and reopened.state.subject_id == state.subject_id
        ),
        "same_plan": before.plan_id == after.plan_id,
        "same_subject": reopened.state.subject_id == state.subject_id,
        "route": after.current_route,
    }


def ordinary_experience_does_not_invent_goal() -> dict:
    duck = LivingDuck(SubjectState.create(name="Aster", subject_id="planning-control"))
    duck.state.needs["curiosity"] = 0.90
    step = duck.step(
        WorldEvent("observation", "world", "The room is quiet and unchanged.", ("ordinary", "room"), 0.0, 0.15),
        allow_inner_speech=False,
    )
    return {
        "name": "ordinary_experience_does_not_invent_goal",
        "passed": not duck.plans() and "goal_formation" not in step.developer_trace,
        "plan_count": len(duck.plans()),
    }


def planning_metadata_stays_out_of_subjective_access() -> dict:
    duck = LivingDuck(SubjectState.create(name="Aster", subject_id="planning-firewall"))
    duck.state.needs["curiosity"] = 0.82
    duck.step(_mystery_event("A cryptic indicator has started pulsing."), allow_inner_speech=False)
    step = duck.heartbeat(allow_inner_speech=False)
    lines = _subjective_lines(step)
    joined = " ".join(lines).lower()
    forbidden = ("pl_", "route_index", "step_index", "plan_id", "pending_concern", "pending_action")
    return {
        "name": "planning_metadata_stays_out_of_subjective_access",
        "passed": step.inner_cognition.thought is None and not any(token in joined for token in forbidden),
        "subjective": lines,
    }


def run() -> dict:
    results = [
        experience_forms_goal_without_instruction(),
        counterfactual_route_changes_with_risk(),
        hierarchical_plan_advances_through_subgoals(),
        failed_route_causes_counterfactual_replanning(),
        plan_survives_state_roundtrip(),
        ordinary_experience_does_not_invent_goal(),
        planning_metadata_stays_out_of_subjective_access(),
    ]
    return {"suite": "DUCK endogenous planning evaluation v0.9", "passed": all(row["passed"] for row in results), "results": results}


if __name__ == "__main__":
    import json

    report = run()
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report["passed"] else 1)
