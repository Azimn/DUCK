"""Focused long-horizon regulation checks for the DUCK v0.6 candidate."""
from __future__ import annotations

import json
from collections import Counter

from .living import SubjectState, WorldEvent
from .living_v06 import LivingDuck


def residue_recovery() -> dict:
    duck = LivingDuck(SubjectState.create("Recovery", "reg-recovery"))
    event = duck.step(WorldEvent("encounter", "world", "An adverse event occurs.", ("threat",), -0.8, 0.9), allow_inner_speech=False)
    duck.resolve_outcome(event.action_id, success=0.7, valence=-0.65, description="The event ended, but it left me shaken.", tags=("threat",))
    first = duck.heartbeat(allow_inner_speech=False)
    peak_fear = duck.state.affect.get("fear", 0.0)
    peak_unease = duck.state.affect.get("unease", 0.0)
    actions = [first.selected_action]
    for _ in range(40):
        actions.append(duck.heartbeat(allow_inner_speech=False).selected_action)
    final_fear = duck.state.affect.get("fear", 0.0)
    final_unease = duck.state.affect.get("unease", 0.0)
    late = actions[-20:]
    return {
        "name": "residue_recovery",
        "passed": final_fear < peak_fear and final_unease < peak_unease and final_fear < 0.25 and final_unease < 0.25 and late.count("step_back") < 10,
        "peak_fear": peak_fear,
        "peak_unease": peak_unease,
        "final_fear": final_fear,
        "final_unease": final_unease,
        "late_actions": dict(Counter(late)),
    }


def quiet_time_regulation() -> dict:
    duck = LivingDuck(SubjectState.create("Quiet", "reg-quiet"))
    actions = [duck.heartbeat(allow_inner_speech=False).selected_action for _ in range(500)]
    counts = Counter(actions)
    dominant_ratio = max(counts.values()) / len(actions)
    seek_ratio = counts.get("seek_connection", 0) / len(actions)
    needs = dict(duck.state.needs)
    bounded = all(0.0 <= value <= 1.0 for value in duck.state.affect.values()) and all(0.0 <= value <= 1.0 for value in needs.values())
    not_saturated = needs.get("energy", 0.0) > 0.08 and needs.get("affiliation", 1.0) < 0.95 and needs.get("curiosity", 1.0) < 0.95
    return {
        "name": "quiet_time_regulation",
        "passed": bounded and not_saturated and len(counts) >= 3 and dominant_ratio < 0.60 and seek_ratio < 0.35,
        "action_counts": dict(counts),
        "dominant_action_ratio": dominant_ratio,
        "seek_connection_ratio": seek_ratio,
        "needs": needs,
    }


def repair_moves_without_erasing_history() -> dict:
    duck = LivingDuck(SubjectState.create("Repair", "reg-repair"))
    commitment = duck.create_commitment("Morgan", "Morgan will meet me later.", due_in=2, importance=0.9)
    duck.heartbeat(allow_inner_speech=False)
    duck.heartbeat(allow_inner_speech=False)
    duck.resolve_commitment(commitment.commitment_id, kept=False, outcome="Morgan did not arrive as planned.")
    for _ in range(6):
        duck.heartbeat(allow_inner_speech=False)
    relation = duck.state.relationship("Morgan")
    before = (relation.trust, relation.guardedness)
    step = duck.step(WorldEvent("message", "Morgan", "Morgan apologizes and tries to repair things.", ("social", "repair"), 0.35, 0.55), allow_inner_speech=False)
    after = (relation.trust, relation.guardedness)
    return {
        "name": "repair_moves_without_erasing_history",
        "passed": after[0] > before[0] and after[1] < before[1] and after[1] > 0.20,
        "before": {"trust": before[0], "guardedness": before[1]},
        "after": {"trust": after[0], "guardedness": after[1]},
        "action": step.selected_action,
        "recalled": list(step.recalled_memory_ids),
    }


def run_all() -> dict:
    results = [residue_recovery(), quiet_time_regulation(), repair_moves_without_erasing_history()]
    return {"suite": "DUCK regulation evaluation v0.6", "passed": all(row["passed"] for row in results), "results": results}


def main() -> int:
    report = run_all()
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
