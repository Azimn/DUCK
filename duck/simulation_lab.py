"""Long-horizon simulation and ablation tests for the integrated DUCK organism.

The lab deliberately exercises the whole subject across histories instead of
adding new cognitive architecture. Reports contain developer traces, while all
subject-facing cognition still passes through the existing SubjectAccessFirewall.
"""
from __future__ import annotations

import argparse
import copy
import json
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

from .host import PersistentDuckHost
from .living import AdaptiveSelfCore, LivingDuck, SubjectState, WorldEvent


def _lines(step) -> list[str]:
    moment = step.subjective_moment
    rows = [item.content for item in moment.impressions]
    rows.extend(item.felt_as for item in moment.tendencies)
    rows.extend(moment.recollections)
    rows.extend(moment.beliefs)
    rows.extend(moment.concerns)
    rows.extend(moment.temporal_context)
    rows.extend(moment.self_context)
    return list(dict.fromkeys(row for row in rows if row))


def _candidate_utility(step, name: str) -> float:
    for candidate in step.developer_trace.get("candidate_actions", []):
        if candidate.get("name") == name:
            return float(candidate.get("utility", 0.0))
    return 0.0


def paired_history_long_horizon() -> dict[str, Any]:
    neutral = LivingDuck(SubjectState.create("Neutral", "sim-paired-neutral"))
    threatened = LivingDuck(SubjectState.create("Threatened", "sim-paired-threat"))
    supported = LivingDuck(SubjectState.create("Supported", "sim-paired-support"))

    for duck in (neutral, threatened, supported):
        duck.heartbeat(allow_inner_speech=False)

    bad = threatened.step(WorldEvent("encounter", "Morgan", "Morgan threatens me.", ("social", "threat", "conflict"), -0.85, 0.95), allow_inner_speech=False)
    threatened.resolve_outcome(bad.action_id, success=0.9, valence=0.55, description="Backing away kept me safe after Morgan threatened me.", tags=("social", "threat"))
    for _ in range(8):
        threatened.heartbeat(allow_inner_speech=False)

    good = supported.step(WorldEvent("encounter", "Morgan", "Morgan helped me when I needed it.", ("social", "supportive"), 0.8, 0.85), allow_inner_speech=False)
    supported.resolve_outcome(good.action_id, success=0.9, valence=0.75, description="Morgan's help made the situation better.", tags=("social", "supportive"))
    for _ in range(8):
        supported.heartbeat(allow_inner_speech=False)

    for _ in range(9):
        neutral.heartbeat(allow_inner_speech=False)

    present = WorldEvent("message", "Morgan", "Morgan says hello.", ("social",), 0.0, 0.3)
    n = neutral.step(present, allow_inner_speech=False)
    t = threatened.step(present, allow_inner_speech=False)
    s = supported.step(present, allow_inner_speech=False)

    actions = {n.selected_action, t.selected_action, s.selected_action}
    subjective = {_freeze(_lines(n)), _freeze(_lines(t)), _freeze(_lines(s))}
    passed = len(actions) > 1 or len(subjective) > 1
    return {
        "name": "paired_history_long_horizon",
        "passed": passed,
        "present_event": present.text,
        "neutral": {"action": n.selected_action, "subjective": _lines(n), "trace": n.developer_trace},
        "threatened": {"action": t.selected_action, "subjective": _lines(t), "trace": t.developer_trace},
        "supported": {"action": s.selected_action, "subjective": _lines(s), "trace": s.developer_trace},
    }


def _freeze(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False)


def epistemic_integrity() -> dict[str, Any]:
    duck = LivingDuck(SubjectState.create("Epistemic", "sim-epistemic"))
    duck.set_world_fact("drawer_code", "The drawer code is 7319.", perceived=False)
    before = duck.step(WorldEvent("message", "Jay", "What is in the drawer?", ("social", "question"), 0.0, 0.3), allow_inner_speech=False)
    leaked_before = any("7319" in line for line in _lines(before)) or "drawer_code" in duck.state.beliefs

    perceived = duck.step(WorldEvent("observation", "world", "I can see the note inside the drawer.", ("observation",), 0.1, 0.4, (("drawer_code", "The drawer code is 7319."),), True), allow_inner_speech=False)
    after = duck.step(WorldEvent("message", "Jay", "What is the drawer code?", ("social", "question"), 0.0, 0.3), allow_inner_speech=False)
    learned_after = "drawer_code" in duck.state.beliefs and any("7319" in line for line in _lines(after))
    return {
        "name": "epistemic_integrity",
        "passed": (not leaked_before) and learned_after,
        "host_truth_before_perception": duck.state.world_facts.get("drawer_code"),
        "subjective_before": _lines(before),
        "subjective_perception": _lines(perceived),
        "subjective_after": _lines(after),
        "belief_keys": sorted(duck.state.beliefs),
    }


def commitment_consequence() -> dict[str, Any]:
    kept = LivingDuck(SubjectState.create("Kept", "sim-commit-kept"))
    broken = LivingDuck(SubjectState.create("Broken", "sim-commit-broken"))
    ck = kept.create_commitment("Morgan", "Morgan will meet me tomorrow.", due_in=3, importance=0.9)
    cb = broken.create_commitment("Morgan", "Morgan will meet me tomorrow.", due_in=3, importance=0.9)
    for _ in range(3):
        kept.heartbeat(allow_inner_speech=False)
        broken.heartbeat(allow_inner_speech=False)
    kept.resolve_commitment(ck.commitment_id, kept=True, outcome="Morgan arrived as promised.")
    broken.resolve_commitment(cb.commitment_id, kept=False, outcome="Morgan never arrived despite promising to come.")
    for _ in range(3):
        kept.heartbeat(allow_inner_speech=False)
        broken.heartbeat(allow_inner_speech=False)
    present = WorldEvent("message", "Morgan", "Can you rely on me?", ("social", "question"), 0.0, 0.4)
    a = kept.step(present, allow_inner_speech=False)
    b = broken.step(present, allow_inner_speech=False)
    rk = kept.state.relationship("Morgan")
    rb = broken.state.relationship("Morgan")
    passed = rk.trust > rb.trust and rb.guardedness > rk.guardedness and _lines(a) != _lines(b)
    return {
        "name": "commitment_consequence",
        "passed": passed,
        "kept": {"action": a.selected_action, "trust": rk.trust, "guardedness": rk.guardedness, "subjective": _lines(a)},
        "broken": {"action": b.selected_action, "trust": rb.trust, "guardedness": rb.guardedness, "subjective": _lines(b)},
    }


def memory_influence_without_recall_prompt() -> dict[str, Any]:
    experienced = LivingDuck(SubjectState.create("Experienced", "sim-memory-experienced"))
    control = LivingDuck(SubjectState.create("Control", "sim-memory-control"))
    event = experienced.step(WorldEvent("encounter", "Riley", "Riley shoved me away from the door.", ("social", "threat", "conflict"), -0.75, 0.9), allow_inner_speech=False)
    experienced.resolve_outcome(event.action_id, success=0.8, valence=-0.4, description="Riley's aggression made me keep my distance.", tags=("social", "threat"))
    for _ in range(12):
        experienced.heartbeat(allow_inner_speech=False)
        control.heartbeat(allow_inner_speech=False)
    present = WorldEvent("message", "Riley", "Riley asks whether I want to walk outside.", ("social",), 0.0, 0.3)
    e = experienced.step(present, allow_inner_speech=False)
    c = control.step(present, allow_inner_speech=False)
    passed = bool(e.recalled_memory_ids) and (e.selected_action != c.selected_action or _lines(e) != _lines(c))
    return {
        "name": "memory_influence_without_recall_prompt",
        "passed": passed,
        "experienced": {"action": e.selected_action, "recalled": list(e.recalled_memory_ids), "subjective": _lines(e)},
        "control": {"action": c.selected_action, "recalled": list(c.recalled_memory_ids), "subjective": _lines(c)},
    }


def adaptive_core_ablation() -> dict[str, Any]:
    learned = LivingDuck(SubjectState.create("Learned", "sim-adaptive"))
    training = WorldEvent("encounter", "world", "A glorp rushes toward me.", ("glorp", "threat"), -0.7, 0.85)
    for _ in range(6):
        step = learned.step(training, allow_inner_speech=False)
        learned.resolve_outcome(step.action_id, success=0.95, valence=0.65, description="Stepping back from the glorp kept me safe.", tags=("glorp", "threat"))
    enabled_state = SubjectState.from_dict(copy.deepcopy(learned.state.to_dict()))
    ablated_state = SubjectState.from_dict(copy.deepcopy(learned.state.to_dict()))
    ablated_state.adaptive = AdaptiveSelfCore()
    enabled = LivingDuck(enabled_state)
    ablated = LivingDuck(ablated_state)
    probe = WorldEvent("encounter", "world", "Another glorp rushes toward me.", ("glorp", "threat"), -0.7, 0.85)
    a = enabled.step(probe, allow_inner_speech=False)
    b = ablated.step(probe, allow_inner_speech=False)
    target = learned.state.recent_actions[-1]
    enabled_utility = _candidate_utility(a, target)
    ablated_utility = _candidate_utility(b, target)
    return {
        "name": "adaptive_core_ablation",
        "passed": abs(enabled_utility - ablated_utility) > 1e-6,
        "trained_action": target,
        "enabled_action": a.selected_action,
        "ablated_action": b.selected_action,
        "enabled_utility": enabled_utility,
        "ablated_utility": ablated_utility,
    }


def language_lesion_longitudinal() -> dict[str, Any]:
    duck = LivingDuck(SubjectState.create("Lesion", "sim-lesion-long"))
    actions: list[str] = []
    for cycle in range(60):
        if cycle % 10 == 0:
            step = duck.step(WorldEvent("encounter", "world", "Something dangerous approaches.", ("threat",), -0.7, 0.8), allow_inner_speech=False)
            duck.resolve_outcome(step.action_id, success=0.85, valence=0.55, description="My response kept me safe.", tags=("threat",))
        else:
            step = duck.heartbeat(allow_inner_speech=False)
        actions.append(step.selected_action)
        if step.inner_cognition.thought is not None:
            return {"name": "language_lesion_longitudinal", "passed": False, "reason": "inner speech appeared during lesion"}
    learned = duck.state.adaptive.action_associations.get("threat", {})
    return {
        "name": "language_lesion_longitudinal",
        "passed": bool(actions) and bool(learned),
        "action_counts": dict(Counter(actions)),
        "learned_threat_actions": learned,
    }


def bounded_quiet_time() -> dict[str, Any]:
    duck = LivingDuck(SubjectState.create("Quiet", "sim-bounded"))
    actions: list[str] = []
    for _ in range(500):
        step = duck.heartbeat(allow_inner_speech=False)
        actions.append(step.selected_action)
    numeric_ok = all(0.0 <= value <= 1.0 for value in duck.state.affect.values()) and all(0.0 <= value <= 1.0 for value in duck.state.needs.values())
    bounds_ok = len(duck.state.memories) <= 2000 and len(duck.state.residues) <= 64 and len(duck.state.recent_actions) <= 32
    varied = len(set(actions)) >= 2
    return {
        "name": "bounded_quiet_time",
        "passed": numeric_ok and bounds_ok and varied,
        "ticks": duck.state.tick,
        "action_counts": dict(Counter(actions)),
        "affect": duck.state.affect,
        "needs": duck.state.needs,
        "memory_count": len(duck.state.memories),
        "residue_count": len(duck.state.residues),
    }


def simulated_week_with_restart() -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory) / "week"
        host = PersistentDuckHost.open(root, name="Aster", subject_id="sim-week")
        timeline: list[dict[str, Any]] = []

        def record(day: int, label: str, step) -> None:
            timeline.append({"day": day, "label": label, "tick": step.tick, "action": step.selected_action, "subjective": _lines(step), "recalled": list(step.recalled_memory_ids)})

        day1 = host.observe(WorldEvent("message", "Morgan", "Morgan welcomes me and offers to help.", ("social", "supportive"), 0.7, 0.7), allow_inner_speech=False)
        record(1, "support", day1)
        host.resolve_outcome(day1.action_id, success=0.9, valence=0.7, description="Morgan's help made my first day easier.", tags=("social", "supportive"))
        promise = host.duck.create_commitment("Morgan", "Morgan will meet me on Day 3.", due_in=8, importance=0.9)
        host.save()
        host.heartbeat(4, allow_inner_speech=False)

        day2 = host.observe(WorldEvent("message", "Riley", "Riley warns me not to trust Morgan.", ("social", "conflict"), -0.35, 0.55), allow_inner_speech=False)
        record(2, "warning", day2)
        host.resolve_outcome(day2.action_id, success=0.5, valence=-0.1, description="Riley's warning left me uncertain.", tags=("social",))
        host.heartbeat(4, allow_inner_speech=False)

        day3 = host.observe(WorldEvent("message", "Morgan", "Morgan never came to meet me.", ("social", "conflict"), -0.65, 0.75), allow_inner_speech=False)
        record(3, "broken_promise", day3)
        host.duck.resolve_commitment(promise.commitment_id, kept=False, outcome="Morgan did not show up for our planned meeting.")
        host.resolve_outcome(day3.action_id, success=0.4, valence=-0.55, description="Waiting for Morgan ended badly.", tags=("social", "commitment"))
        host.save()
        before_restart = host.status()

        host = PersistentDuckHost.open(root)
        after_restart = host.status()
        restart_ok = before_restart["subject_id"] == after_restart["subject_id"] and before_restart["tick"] == after_restart["tick"]
        host.heartbeat(8, allow_inner_speech=False)

        day5 = host.observe(WorldEvent("message", "Morgan", "Morgan says hello as if nothing happened.", ("social",), 0.0, 0.35), allow_inner_speech=False)
        record(5, "return", day5)
        remembered = bool(day5.recalled_memory_ids)
        relation = host.duck.state.relationship("Morgan")
        host.resolve_outcome(day5.action_id, success=0.5, valence=0.0, description="The encounter ended without resolution.", tags=("social",))
        host.heartbeat(8, allow_inner_speech=False)

        day7 = host.observe(WorldEvent("message", "Morgan", "Morgan apologizes for missing our meeting.", ("social", "repair"), 0.35, 0.55), allow_inner_speech=False)
        record(7, "repair_attempt", day7)
        final_status = host.status()
        passed = restart_ok and remembered and final_status["tick"] > before_restart["tick"] and relation.guardedness > 0.2
        return {
            "name": "simulated_week_with_restart",
            "passed": passed,
            "restart_preserved_subject": restart_ok,
            "remembered_broken_promise_on_return": remembered,
            "morgan_relationship": {"trust": relation.trust, "guardedness": relation.guardedness, "attachment": relation.attachment, "familiarity": relation.familiarity},
            "timeline": timeline,
            "final_status": final_status,
        }


def run_all() -> dict[str, Any]:
    results = [
        paired_history_long_horizon(),
        epistemic_integrity(),
        commitment_consequence(),
        memory_influence_without_recall_prompt(),
        adaptive_core_ablation(),
        language_lesion_longitudinal(),
        bounded_quiet_time(),
        simulated_week_with_restart(),
    ]
    return {"suite": "DUCK Simulation Lab v0.6", "passed": all(result.get("passed") for result in results), "results": results}


def _markdown(report: dict[str, Any]) -> str:
    lines = ["# DUCK Simulation Lab v0.6", "", f"Overall: {'PASS' if report['passed'] else 'FAIL'}", ""]
    for result in report["results"]:
        lines.append(f"## {result['name']}")
        lines.append("")
        lines.append(f"Result: {'PASS' if result.get('passed') else 'FAIL'}")
        lines.append("")
        if result["name"] == "paired_history_long_horizon":
            lines.append(f"Same present event produced actions neutral={result['neutral']['action']}, threatened={result['threatened']['action']}, supported={result['supported']['action']}.")
        elif result["name"] == "simulated_week_with_restart":
            lines.append(f"Restart preserved subject: {result['restart_preserved_subject']}. Broken-promise history was recalled on later return: {result['remembered_broken_promise_on_return']}.")
        elif "action_counts" in result:
            lines.append(f"Action counts: `{json.dumps(result['action_counts'], sort_keys=True)}`")
        lines.append("")
    lines.append("Architectural interpretation: passing this suite demonstrates longitudinal causal continuity, bounded state evolution, epistemic separation, persistence, language-independent action/learning, and measurable contribution from the adaptive substrate. It does not demonstrate phenomenal consciousness or human equivalence.")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run DUCK longitudinal simulation tests")
    parser.add_argument("--out-dir", type=Path, default=None)
    args = parser.parse_args(argv)
    report = run_all()
    rendered = json.dumps(report, indent=2, ensure_ascii=False)
    print(rendered)
    if args.out_dir is not None:
        args.out_dir.mkdir(parents=True, exist_ok=True)
        (args.out_dir / "simulation_report.json").write_text(rendered + "\n", encoding="utf-8")
        (args.out_dir / "simulation_report.md").write_text(_markdown(report), encoding="utf-8")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
