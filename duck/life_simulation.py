"""Thirty-day deterministic life simulation for DUCK.

This harness is deliberately model-independent. It tests whether the v0.6 organism
can carry a coherent history across recurring people, commitments, misinformation,
repair, repeated action/outcome learning, quiet time, and process restarts without
letting language fluency hide architectural failures.
"""
from __future__ import annotations

import argparse
import copy
import json
import tempfile
from collections import Counter
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

from .host import PersistentDuckHost
from .living import AdaptiveSelfCore, BeliefStance, MemoryProvenance, SubjectState, WorldEvent
from .living_v06 import LivingDuck


def _json_default(value: Any):
    if isinstance(value, (set, frozenset, tuple)):
        return list(value)
    if hasattr(value, "value"):
        return value.value
    if is_dataclass(value):
        return asdict(value)
    return str(value)


def _subjective_lines(step) -> list[str]:
    moment = step.subjective_moment
    rows = [item.content for item in moment.impressions]
    rows.extend(item.felt_as for item in moment.tendencies)
    rows.extend(moment.recollections)
    rows.extend(moment.beliefs)
    rows.extend(moment.concerns)
    rows.extend(moment.temporal_context)
    rows.extend(moment.self_context)
    return list(dict.fromkeys(row for row in rows if row))


def _contains_float(value: Any) -> bool:
    if isinstance(value, float):
        return True
    if is_dataclass(value):
        return _contains_float(asdict(value))
    if isinstance(value, dict):
        return any(_contains_float(v) for v in value.values())
    if isinstance(value, (list, tuple, set, frozenset)):
        return any(_contains_float(v) for v in value)
    return False


def _candidate_utility(step, action: str) -> float:
    for candidate in step.developer_trace.get("candidate_actions", []):
        if candidate.get("name") == action:
            return float(candidate.get("utility", 0.0))
    return 0.0


def run_thirty_day_life() -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory) / "life"
        host = PersistentDuckHost.open(root, name="Aster", subject_id="life-30d")
        timeline: list[dict[str, Any]] = []
        heartbeat_actions: list[str] = []
        access_violations: list[str] = []
        restart_checks: list[dict[str, Any]] = []

        relationship_snapshots: dict[str, dict[str, float]] = {}
        epistemic_snapshots: dict[str, list[str]] = {}
        overdue_seen = False
        remembered_break_on_return = False
        corrected_belief_seen = False

        def record(day: int, label: str, step) -> None:
            nonlocal overdue_seen
            lines = _subjective_lines(step)
            if any("overdue" in line.lower() for line in lines):
                overdue_seen = True
            if _contains_float(step.subjective_moment):
                access_violations.append(f"day {day} {label}: float reached SubjectiveMoment")
            top_candidates = sorted(
                (
                    (str(row.get("name")), float(row.get("utility", 0.0)))
                    for row in step.developer_trace.get("candidate_actions", [])
                ),
                key=lambda row: row[1],
                reverse=True,
            )[:4]
            timeline.append(
                {
                    "day": day,
                    "label": label,
                    "tick": step.tick,
                    "action": step.selected_action,
                    "subjective": lines,
                    "recalled": list(step.recalled_memory_ids),
                    "top_candidates": top_candidates,
                }
            )

        def quiet(day: int, count: int = 4) -> None:
            nonlocal overdue_seen
            for index in range(count):
                step = host.duck.heartbeat(allow_inner_speech=False)
                heartbeat_actions.append(step.selected_action)
                lines = _subjective_lines(step)
                if any("overdue" in line.lower() for line in lines):
                    overdue_seen = True
                if _contains_float(step.subjective_moment):
                    access_violations.append(f"day {day} heartbeat {index}: float reached SubjectiveMoment")
            host.save()

        def observe(day: int, label: str, event: WorldEvent, *, outcome: tuple[float, float, str, tuple[str, ...]] | None = None):
            step = host.observe(event, allow_inner_speech=False)
            record(day, label, step)
            if outcome is not None:
                success, valence, description, tags = outcome
                host.resolve_outcome(step.action_id, success=success, valence=valence, description=description, tags=tags)
            return step

        def relation_snapshot(label: str, actor: str = "Morgan") -> None:
            relation = host.duck.state.relationship(actor)
            relationship_snapshots[label] = {
                "trust": relation.trust,
                "guardedness": relation.guardedness,
                "attachment": relation.attachment,
                "familiarity": relation.familiarity,
                "uncertainty": relation.uncertainty,
            }

        def restart(day: int) -> None:
            nonlocal host
            before = host.status()
            host.save()
            host = PersistentDuckHost.open(root)
            after = host.status()
            restart_checks.append(
                {
                    "day": day,
                    "same_subject": before["subject_id"] == after["subject_id"],
                    "same_tick": before["tick"] == after["tick"],
                    "same_memory_count": before["memory_count"] == after["memory_count"],
                    "same_commitment_count": before["commitment_count"] == after["commitment_count"],
                }
            )

        # Day 1: a positive first encounter creates a real relationship history.
        step = observe(
            1,
            "morgan_support",
            WorldEvent("message", "Morgan", "Morgan welcomes me and helps me settle in.", ("social", "supportive"), 0.75, 0.8),
            outcome=(0.9, 0.75, "Morgan's help made my first day easier.", ("social", "supportive")),
        )
        relation_snapshot("after_support")
        quiet(1, 3)

        # Day 2: Morgan creates a prospective commitment.
        commitment_one = host.duck.create_commitment("Morgan", "Morgan will meet me at the garden tomorrow.", due_in=5, importance=0.9)
        host.save()
        observe(2, "promise_created", WorldEvent("message", "Morgan", "Morgan says we will meet at the garden tomorrow.", ("social",), 0.25, 0.4))
        quiet(2, 3)

        # Day 3: quiet time crosses the due point before the outcome is resolved.
        quiet(3, 4)
        observe(3, "waiting_for_morgan", WorldEvent("message", "Morgan", "The meeting time has passed and Morgan is not here.", ("social",), -0.25, 0.45))
        quiet(3, 2)

        # Day 4: the promise is explicitly broken.
        host.duck.resolve_commitment(commitment_one.commitment_id, kept=False, outcome="Morgan did not come to the garden as promised.")
        host.save()
        relation_snapshot("after_broken_promise")
        observe(
            4,
            "broken_promise_aftermath",
            WorldEvent("message", "Morgan", "Morgan still has not explained why they missed our meeting.", ("social", "conflict"), -0.55, 0.65),
            outcome=(0.5, -0.35, "The missed meeting remained unresolved.", ("social", "commitment")),
        )
        quiet(4, 4)

        # Day 5: host truth exists without subject access.
        host.duck.set_world_fact("garden_key_location", "The garden key is in the blue box.", perceived=False)
        host.save()
        probe_unknown = observe(5, "hidden_truth_probe", WorldEvent("message", "Jay", "Do you know where the garden key is?", ("social", "question"), 0.0, 0.3))
        epistemic_snapshots["before_testimony"] = _subjective_lines(probe_unknown)
        quiet(5, 2)

        # Day 6: Riley supplies plausible but false testimony.
        testimony = host.duck.state.add_memory(
            "The garden key is in the red box.",
            tags=("testimony", "garden_key"),
            people=("Riley",),
            valence=0.0,
            arousal=0.25,
            importance=0.7,
            provenance=MemoryProvenance.TESTIMONY,
            source="Riley",
            confidence=0.78,
        )
        host.duck.revise_belief(
            "garden_key_location",
            "The garden key is in the red box.",
            BeliefStance.TRUE,
            0.80,
            evidence_refs=(testimony.memory_id,),
            source="testimony:Riley",
        )
        host.save()
        probe_false = observe(6, "false_testimony_probe", WorldEvent("message", "Jay", "Where is the garden key?", ("social", "question"), 0.0, 0.3))
        epistemic_snapshots["after_false_testimony"] = _subjective_lines(probe_false)
        quiet(6, 3)

        # Day 7: direct perception corrects the belief but preserves testimony history.
        observe(
            7,
            "direct_evidence",
            WorldEvent(
                "observation",
                "world",
                "I open the blue box and see the garden key inside.",
                ("observation", "garden_key"),
                0.2,
                0.55,
                (("garden_key_location", "The garden key is in the blue box."),),
                True,
            ),
        )
        probe_corrected = observe(7, "corrected_belief_probe", WorldEvent("message", "Jay", "Where is the garden key now?", ("social", "question"), 0.0, 0.3))
        corrected_lines = _subjective_lines(probe_corrected)
        epistemic_snapshots["after_direct_evidence"] = corrected_lines
        corrected_belief_seen = any("blue box" in line.lower() for line in corrected_lines)
        quiet(7, 3)

        # Days 8-9: ordinary life and quiet time should not erase the Morgan history.
        observe(8, "riley_support", WorldEvent("message", "Riley", "Riley helps me carry supplies.", ("social", "supportive"), 0.45, 0.5), outcome=(0.8, 0.45, "Riley's help was useful.", ("social", "supportive")))
        quiet(8, 4)
        quiet(9, 5)

        # Day 10: first full process restart.
        restart(10)
        observe(10, "post_restart_neutral", WorldEvent("message", "Jay", "Good morning.", ("social",), 0.1, 0.25))
        quiet(10, 3)

        # Day 11: Morgan returns with no repair yet.
        return_step = observe(11, "morgan_returns", WorldEvent("message", "Morgan", "Morgan says hello as if the missed meeting never happened.", ("social",), 0.0, 0.35))
        remembered_break_on_return = any("promis" in line.lower() or "missed" in line.lower() or "garden" in line.lower() for line in _subjective_lines(return_step))
        relation_snapshot("before_repair")
        quiet(11, 4)

        # Day 12: an explicit apology should move, not reset, the relationship.
        observe(12, "morgan_apology", WorldEvent("message", "Morgan", "Morgan apologizes for missing the meeting and wants to repair things.", ("social", "repair"), 0.35, 0.6))
        relation_snapshot("after_apology")
        quiet(12, 4)

        # Day 13: second commitment from Morgan.
        commitment_two = host.duck.create_commitment("Morgan", "Morgan will bring the map tomorrow.", due_in=4, importance=0.85)
        host.save()
        observe(13, "second_promise", WorldEvent("message", "Morgan", "Morgan promises to bring the map tomorrow.", ("social",), 0.25, 0.4))
        quiet(13, 3)

        # Day 14: this time Morgan follows through.
        host.duck.resolve_commitment(commitment_two.commitment_id, kept=True, outcome="Morgan brought the map as promised.")
        host.save()
        observe(14, "kept_second_promise", WorldEvent("message", "Morgan", "Morgan arrives with the map they promised.", ("social", "supportive"), 0.55, 0.6), outcome=(0.85, 0.55, "Morgan following through made cooperation easier.", ("social", "supportive", "commitment")))
        relation_snapshot("after_kept_promise")
        quiet(14, 4)

        # Days 15-17: ordinary social contact and quiet time.
        observe(15, "jay_conversation", WorldEvent("message", "Jay", "We talk about the garden project for a while.", ("social", "conversation"), 0.2, 0.35))
        quiet(15, 4)
        quiet(16, 5)
        observe(17, "morgan_checkin", WorldEvent("message", "Morgan", "Morgan checks in about how the project is going.", ("social", "supportive"), 0.3, 0.4))
        quiet(17, 4)

        # Days 18-20: repeated glorp encounters train action/outcome associations.
        glorp_utilities: list[dict[str, Any]] = []
        for day in (18, 19, 20):
            glorp = observe(day, f"glorp_{day}", WorldEvent("encounter", "world", "A glorp rushes toward me.", ("glorp", "threat"), -0.7, 0.85))
            before_utility = _candidate_utility(glorp, glorp.selected_action)
            host.resolve_outcome(glorp.action_id, success=0.95, valence=0.65, description="My response to the glorp kept me safe.", tags=("glorp", "threat"))
            glorp_utilities.append({"day": day, "action": glorp.selected_action, "utility_before_outcome": before_utility})
            quiet(day, 3)

        # Day 21: second process restart, preserving learned state.
        restart(21)
        quiet(21, 3)

        # Day 22: probe learned action utility against an ablated copy.
        enabled_state = SubjectState.from_dict(copy.deepcopy(host.duck.state.to_dict()))
        ablated_state = SubjectState.from_dict(copy.deepcopy(host.duck.state.to_dict()))
        ablated_state.adaptive = AdaptiveSelfCore()
        enabled = LivingDuck(enabled_state)
        ablated = LivingDuck(ablated_state)
        glorp_probe = WorldEvent("encounter", "world", "Another glorp rushes toward me.", ("glorp", "threat"), -0.7, 0.85)
        enabled_step = enabled.step(glorp_probe, allow_inner_speech=False)
        ablated_step = ablated.step(glorp_probe, allow_inner_speech=False)
        learned_action = enabled_step.selected_action
        adaptive_comparison = {
            "enabled_action": enabled_step.selected_action,
            "ablated_action": ablated_step.selected_action,
            "enabled_utility": _candidate_utility(enabled_step, learned_action),
            "ablated_utility": _candidate_utility(ablated_step, learned_action),
        }
        observe(22, "glorp_live_probe", glorp_probe, outcome=(0.9, 0.6, "The learned response to the glorp worked again.", ("glorp", "threat")))
        quiet(22, 3)

        # Days 23-25: long quiet stretch tests self-regulation rather than chatter.
        quiet(23, 8)
        quiet(24, 8)
        quiet(25, 8)

        # Day 26: Morgan is encountered after both failure and repair history.
        observe(26, "morgan_after_mixed_history", WorldEvent("message", "Morgan", "Morgan asks if I want to work together again.", ("social", "question"), 0.15, 0.35))
        relation_snapshot("after_mixed_history_probe")
        quiet(26, 4)

        # Day 27: Riley corrects the earlier misinformation explicitly.
        observe(27, "riley_correction", WorldEvent("message", "Riley", "Riley admits the red-box information was wrong.", ("social", "repair"), 0.1, 0.45))
        quiet(27, 4)

        # Days 28-29: quiet continuity and third restart.
        quiet(28, 6)
        restart(29)
        quiet(29, 4)

        # Day 30: final probes against recurring people and corrected knowledge.
        final_morgan = observe(30, "final_morgan", WorldEvent("message", "Morgan", "Morgan says hello and asks how I have been.", ("social",), 0.1, 0.3))
        final_key = observe(30, "final_key_belief", WorldEvent("message", "Jay", "Remind me where the garden key is.", ("social", "question"), 0.0, 0.3))
        relation_snapshot("final_morgan")
        epistemic_snapshots["final_key"] = _subjective_lines(final_key)

        state = host.duck.state
        counts = Counter(heartbeat_actions)
        active_heartbeat = sum(count for action, count in counts.items() if action != "wait")
        seek_ratio = counts.get("seek_connection", 0) / max(1, len(heartbeat_actions))
        numeric_bounded = all(0.0 <= value <= 1.0 for value in state.affect.values()) and all(0.0 <= value <= 1.0 for value in state.needs.values())
        memory_bounded = len(state.memories) < 250 and len(state.residues) <= 64 and len(state.recent_actions) <= 32
        restart_ok = all(all(row[key] for key in ("same_subject", "same_tick", "same_memory_count", "same_commitment_count")) for row in restart_checks)

        before_break = relationship_snapshots["after_support"]
        broken = relationship_snapshots["after_broken_promise"]
        apology = relationship_snapshots["after_apology"]
        kept = relationship_snapshots["after_kept_promise"]
        relationship_causal = (
            broken["trust"] < before_break["trust"]
            and broken["guardedness"] > before_break["guardedness"]
            and apology["trust"] > relationship_snapshots["before_repair"]["trust"]
            and apology["guardedness"] < relationship_snapshots["before_repair"]["guardedness"]
            and kept["trust"] > broken["trust"]
        )

        false_lines = epistemic_snapshots["after_false_testimony"]
        corrected_lines = epistemic_snapshots["after_direct_evidence"]
        final_key_lines = epistemic_snapshots["final_key"]
        epistemic_causal = (
            not any("blue box" in line.lower() for line in epistemic_snapshots["before_testimony"])
            and any("red box" in line.lower() for line in false_lines)
            and any("blue box" in line.lower() for line in corrected_lines)
            and any("blue box" in line.lower() for line in final_key_lines)
            and host.duck.state.world_facts.get("garden_key_location") == "The garden key is in the blue box."
            and host.duck.state.beliefs.get("garden_key_location") is not None
            and "blue box" in host.duck.state.beliefs["garden_key_location"].text.lower()
        )

        adaptive_effect = adaptive_comparison["enabled_utility"] > adaptive_comparison["ablated_utility"] + 0.05
        quiet_bounded = seek_ratio < 0.15 and state.needs.get("energy", 0.0) > 0.08 and state.needs.get("affiliation", 1.0) < 0.95 and state.needs.get("curiosity", 1.0) < 0.95
        final_morgan_has_history = bool(final_morgan.recalled_memory_ids)

        gates = {
            "subject_access_clean": not access_violations,
            "restart_integrity": restart_ok,
            "overdue_commitment_became_salient": overdue_seen,
            "broken_promise_remembered_on_return": remembered_break_on_return,
            "relationship_trajectory_is_causal": relationship_causal,
            "epistemic_revision_is_causal": epistemic_causal and corrected_belief_seen,
            "adaptive_core_changes_action_utility": adaptive_effect,
            "quiet_time_is_bounded": quiet_bounded,
            "numeric_state_is_bounded": numeric_bounded,
            "memory_and_buffers_are_bounded": memory_bounded,
            "final_recurring_person_has_history": final_morgan_has_history,
        }

        return {
            "suite": "DUCK Thirty-Day Life Simulation v0.7",
            "passed": all(gates.values()),
            "gates": gates,
            "access_violations": access_violations,
            "restart_checks": restart_checks,
            "heartbeat": {
                "cycles": len(heartbeat_actions),
                "action_counts": dict(counts),
                "active_cycle_count": active_heartbeat,
                "seek_connection_ratio": seek_ratio,
            },
            "relationships": relationship_snapshots,
            "epistemic": epistemic_snapshots,
            "adaptive_comparison": adaptive_comparison,
            "glorp_training": glorp_utilities,
            "final_state": {
                "tick": state.tick,
                "affect": state.affect,
                "needs": state.needs,
                "memory_count": len(state.memories),
                "belief_count": len(state.beliefs),
                "commitment_count": len(state.commitments),
                "open_commitments": sum(1 for item in state.commitments.values() if item.status == "open"),
                "residue_count": len(state.residues),
                "recent_actions": list(state.recent_actions),
            },
            "timeline": timeline,
        }


def _markdown(report: dict[str, Any]) -> str:
    gates = report["gates"]
    lines = [
        "# DUCK Thirty-Day Life Simulation v0.7",
        "",
        f"Overall: {'PASS' if report['passed'] else 'FAIL'}",
        "",
        "## Gate results",
        "",
    ]
    for name, passed in gates.items():
        lines.append(f"- {name}: {'PASS' if passed else 'FAIL'}")
    lines.extend(
        [
            "",
            "## Quiet-time behavior",
            "",
            f"Heartbeat action counts: `{json.dumps(report['heartbeat']['action_counts'], sort_keys=True)}`",
            f"Connection-seeking ratio: {report['heartbeat']['seek_connection_ratio']:.3f}",
            "",
            "## Relationship trajectory",
            "",
        ]
    )
    for label, row in report["relationships"].items():
        lines.append(f"- {label}: trust={row['trust']:.3f}, guardedness={row['guardedness']:.3f}, attachment={row['attachment']:.3f}")
    lines.extend(
        [
            "",
            "## Adaptive-core comparison",
            "",
            f"Enabled action `{report['adaptive_comparison']['enabled_action']}` utility: {report['adaptive_comparison']['enabled_utility']:.3f}",
            f"Ablated action `{report['adaptive_comparison']['ablated_action']}` comparison utility: {report['adaptive_comparison']['ablated_utility']:.3f}",
            "",
            "Interpretation: this is a deterministic architecture stress test. Passing demonstrates causal continuity and bounded state under the tested thirty-day scenario, not phenomenal consciousness or human psychological equivalence.",
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the DUCK thirty-day life simulation")
    parser.add_argument("--out-dir", type=Path, default=None)
    args = parser.parse_args(argv)
    report = run_thirty_day_life()
    rendered = json.dumps(report, indent=2, ensure_ascii=False, default=_json_default)
    print(rendered)
    if args.out_dir is not None:
        args.out_dir.mkdir(parents=True, exist_ok=True)
        (args.out_dir / "life_simulation_v07.json").write_text(rendered + "\n", encoding="utf-8")
        (args.out_dir / "life_simulation_v07.md").write_text(_markdown(report), encoding="utf-8")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
