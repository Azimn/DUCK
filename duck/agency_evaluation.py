"""Focused endogenous-agency probes for the DUCK v0.8 candidate."""
from __future__ import annotations

from .living import SubjectState
from .living_v08 import LivingDuck


def opportunity_without_prompt() -> dict:
    duck = LivingDuck(SubjectState.create(name="Aster", subject_id="agency-opportunity"))
    opportunity = duck.register_opportunity(
        "I want to inspect the blue flower when I have a quiet moment.",
        tags=("garden", "flower"),
        importance=0.86,
    )
    steps = [duck.heartbeat(allow_inner_speech=False) for _ in range(3)]
    acted = [step for step in steps if step.selected_action in {"explore", "ask"}]
    tagged_done = "opportunity_acted" in opportunity.tags
    return {
        "name": "opportunity_without_prompt",
        "passed": bool(acted) and tagged_done,
        "actions": [step.selected_action for step in steps],
        "acted_tick": acted[0].tick if acted else None,
        "opportunity_tags": list(opportunity.tags),
    }


def opportunity_survives_restart() -> dict:
    state = SubjectState.create(name="Aster", subject_id="agency-restart")
    duck = LivingDuck(state)
    duck.register_opportunity(
        "I want to look at the old map when I get a chance.",
        tags=("map", "investigate"),
        importance=0.84,
    )
    restored = SubjectState.from_dict(state.to_dict())
    reopened = LivingDuck(restored)
    step = reopened.heartbeat(allow_inner_speech=False)
    acted_memory = next(memory for memory in reopened.state.memories if "opportunity" in memory.tags)
    return {
        "name": "opportunity_survives_restart",
        "passed": step.selected_action in {"explore", "ask"} and "opportunity_acted" in acted_memory.tags,
        "same_subject": reopened.state.subject_id == state.subject_id,
        "action": step.selected_action,
        "tags": list(acted_memory.tags),
    }


def no_opportunity_no_false_goal() -> dict:
    duck = LivingDuck(SubjectState.create(name="Aster", subject_id="agency-control"))
    steps = [duck.heartbeat(allow_inner_speech=False) for _ in range(8)]
    fabricated = any("opportunity_active" in row for step in steps for row in [tuple(step.developer_trace.get("mechanistic_snapshot", {}).keys())])
    opportunity_memories = [memory for memory in duck.state.memories if "opportunity" in memory.tags]
    return {
        "name": "no_opportunity_no_false_goal",
        "passed": not fabricated and not opportunity_memories,
        "actions": [step.selected_action for step in steps],
    }


def run() -> dict:
    results = [opportunity_without_prompt(), opportunity_survives_restart(), no_opportunity_no_false_goal()]
    return {"suite": "DUCK agency evaluation v0.8", "passed": all(row["passed"] for row in results), "results": results}


if __name__ == "__main__":
    import json

    report = run()
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report["passed"] else 1)
