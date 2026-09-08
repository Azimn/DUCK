"""Long-horizon motivated-agency simulation for DUCK v0.8.

The scenario tests whether unfinished intentions can persist and compete across time,
context changes, safety pressure, low energy, interruption, commitment outcomes, and
process restart without becoming a reminder queue or leaking mechanistic metadata
into first-person cognition.
"""
from __future__ import annotations

import argparse
import json
import tempfile
from collections import Counter
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

from .host_v08 import PersistentDuckHostV08 as PersistentDuckHost
from .living import WorldEvent


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


def run_agency_simulation() -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory) / "agency"
        host = PersistentDuckHost.open(root, name="Aster", subject_id="agency-14d")
        timeline: list[dict[str, Any]] = []
        access_violations: list[str] = []
        inner_language_violations: list[str] = []

        def capture(label: str, step) -> None:
            lines = _subjective_lines(step)
            if _contains_float(step.subjective_moment):
                access_violations.append(f"{label}: float reached SubjectiveMoment")
            if any(token in " ".join(lines).lower() for token in ("pc_", "concern_id:", "priority:", "urgency:")):
                access_violations.append(f"{label}: private agency metadata leaked")
            if step.inner_cognition.thought is not None:
                inner_language_violations.append(label)
            timeline.append(
                {
                    "label": label,
                    "tick": step.tick,
                    "action": step.selected_action,
                    "subjective": lines,
                    "agency": step.developer_trace.get("agency"),
                }
            )

        def heartbeat(label: str):
            step = host.duck.heartbeat(allow_inner_speech=False)
            capture(label, step)
            host.save()
            return step

        def observe(label: str, event: WorldEvent):
            step = host.observe(event, allow_inner_speech=False)
            capture(label, step)
            return step

        flower = host.duck.register_concern(
            "I want to inspect the blue flower when I am back in the garden.",
            tags=("garden_project", "flower"),
            priority=0.80,
            urgency=0.52,
            preferred_action="explore",
            required_tags=("garden",),
            min_energy=0.30,
        )
        # This is deliberately delayed but still meaningfully motivated once its
        # not-before boundary passes. The test is about interruption/resumption,
        # not whether a weak whim should overcome low curiosity.
        map_goal = host.duck.register_concern(
            "I want to review the old map when I have enough time.",
            tags=("map", "project"),
            priority=0.68,
            urgency=0.40,
            preferred_action="explore",
            not_before_in=14,
            min_energy=0.28,
        )
        map_not_before = host.duck._concern_from_memory(map_goal).not_before_tick
        tunnel = host.duck.register_concern(
            "I want to investigate the old tunnel if it becomes accessible.",
            tags=("tunnel",),
            priority=0.68,
            urgency=0.38,
            preferred_action="explore",
            required_tags=("tunnel_open",),
        )
        commitment = host.duck.create_commitment("Morgan", "Morgan will bring the seed catalog.", due_in=6, importance=0.92)
        followup = host.duck.register_commitment_followup(commitment)
        host.save()

        early_one = heartbeat("early_quiet_1")
        early_two = heartbeat("early_quiet_2")
        no_premature_goal = all(step.developer_trace.get("agency") is None for step in (early_one, early_two))

        observe(
            "garden_threat",
            WorldEvent("observation", "world", "Something dangerous moves beside the flower.", ("garden", "threat"), -0.65, 0.85),
        )
        blocked = heartbeat("garden_blocked_by_threat")
        flower_after_block = host.duck._concern_from_memory(host.duck._concern_memory(flower.memory_id))
        safety_deferral = blocked.selected_action != "explore" and flower_after_block.deferrals >= 1

        observe(
            "garden_safe_again",
            WorldEvent("observation", "world", "The garden is quiet again and the blue flower is beside me.", ("garden", "safe", "flower"), 0.20, 0.30),
        )
        host.duck.state.affect["fear"] = 0.10
        flower_step = heartbeat("flower_opportunity_returns")
        flower_acted = flower_step.developer_trace.get("agency", {}).get("selected_concern_id") == flower.memory_id and flower_step.selected_action == "explore"
        host.duck.resolve_concern(flower.memory_id, satisfied=True, reason="I inspected the blue flower while I had the chance.")
        host.save()

        before_restart = host.status()
        host = PersistentDuckHost.open(root)
        after_restart = host.status()
        restart_ok = (
            before_restart["subject_id"] == after_restart["subject_id"]
            and before_restart["tick"] == after_restart["tick"]
            and host.duck._concern_from_memory(host.duck._concern_memory(flower.memory_id)).status == "satisfied"
            and any(row.concern_id == map_goal.memory_id for row in host.duck.concerns(status="open"))
        )

        while host.duck.state.tick < commitment.due_tick:
            heartbeat("waiting_for_commitment")
        followup_step = heartbeat("commitment_followup_due")
        followup_acted = (
            followup_step.developer_trace.get("agency", {}).get("selected_concern_id") == followup.memory_id
            and followup_step.selected_action == "ask"
        )
        host.duck.resolve_commitment(commitment.commitment_id, kept=True, outcome="Morgan brought the seed catalog as promised.")
        heartbeat("after_commitment_resolution")
        followup_status = host.duck._concern_from_memory(host.duck._concern_memory(followup.memory_id)).status
        linked_resolution = followup_status == "satisfied"

        host.duck.mark_concern_impossible(tunnel.memory_id, reason="The tunnel entrance collapsed, so I cannot pursue that plan.")
        impossible_status = host.duck._concern_from_memory(host.duck._concern_memory(tunnel.memory_id)).status

        observe(
            "jay_interrupts",
            WorldEvent("message", "Jay", "Before you do anything else, can you help me check this note?", ("social", "question"), 0.0, 0.35),
        )
        map_still_open_after_interrupt = any(row.concern_id == map_goal.memory_id for row in host.duck.concerns(status="open"))
        while map_not_before is not None and host.duck.state.tick < map_not_before:
            heartbeat("map_waits_until_later")
        map_step = heartbeat("map_goal_resumes")
        map_resumed = map_step.developer_trace.get("agency", {}).get("selected_concern_id") == map_goal.memory_id and map_step.selected_action == "explore"
        host.duck.resolve_concern(map_goal.memory_id, satisfied=True, reason="I reviewed the old map.")

        energy_goal = host.duck.register_concern(
            "I want to inspect the greenhouse equipment.",
            tags=("greenhouse",),
            priority=0.86,
            urgency=0.60,
            preferred_action="explore",
            min_energy=0.62,
        )
        host.duck.state.needs["energy"] = 0.20
        low_energy_step = heartbeat("greenhouse_deferred_for_energy")
        deferred = host.duck._concern_from_memory(host.duck._concern_memory(energy_goal.memory_id))
        energy_deferred = low_energy_step.selected_action != "explore" and deferred.deferrals >= 1

        host.save()
        host = PersistentDuckHost.open(root)
        host.duck.state.needs["energy"] = 0.82
        resumed_step = heartbeat("greenhouse_resumes_after_restart")
        energy_resumed = resumed_step.developer_trace.get("agency", {}).get("selected_concern_id") == energy_goal.memory_id and resumed_step.selected_action == "explore"
        host.duck.resolve_concern(energy_goal.memory_id, satisfied=True, reason="I inspected the greenhouse equipment after resting.")

        low = host.duck.register_concern(
            "I might inspect the decorative stones sometime.",
            priority=0.42,
            urgency=0.18,
            preferred_action="explore",
        )
        high = host.duck.register_concern(
            "I need to check whether Riley is still waiting for my answer.",
            tags=("social",),
            priority=0.95,
            urgency=0.90,
            preferred_action="ask",
            due_in=0,
            min_energy=0.15,
        )
        competition_step = heartbeat("competing_concerns")
        competition_ok = (
            competition_step.developer_trace.get("agency", {}).get("selected_concern_id") == high.memory_id
            and competition_step.selected_action == "ask"
        )
        host.duck.resolve_concern(high.memory_id, satisfied=True, reason="I checked in with Riley.")
        host.duck.resolve_concern(low.memory_id, satisfied=False, reason="The decorative stones are not important enough to keep pursuing.")

        baseline_actions: list[str] = []
        for index in range(60):
            step = heartbeat(f"post_goal_quiet_{index}")
            baseline_actions.append(step.selected_action)
        counts = Counter(baseline_actions)
        active_ratio = sum(count for action, count in counts.items() if action != "wait") / max(1, len(baseline_actions))
        no_runaway_after_resolution = active_ratio < 0.35 and not host.duck.concerns(status="open")

        gates = {
            "no_premature_goal_execution": no_premature_goal,
            "safety_can_defer_goal": safety_deferral,
            "context_can_reactivate_goal": flower_acted,
            "concerns_survive_restart": restart_ok,
            "commitment_followup_becomes_endogenous": followup_acted,
            "resolved_commitment_retires_followup": linked_resolution,
            "impossible_goal_can_be_abandoned": impossible_status == "abandoned",
            "interruption_preserves_intention": map_still_open_after_interrupt,
            "deferred_goal_can_resume": map_resumed,
            "low_energy_defers_goal": energy_deferred,
            "energy_recovery_and_restart_allow_resumption": energy_resumed,
            "competing_concerns_select_stronger_motive": competition_ok,
            "resolved_goals_do_not_create_runaway_activity": no_runaway_after_resolution,
            "language_lesion_survives": not inner_language_violations,
            "subject_access_remains_clean": not access_violations,
        }

        return {
            "suite": "DUCK motivated agency simulation v0.8",
            "passed": all(gates.values()),
            "gates": gates,
            "timeline": timeline,
            "access_violations": access_violations,
            "inner_language_violations": inner_language_violations,
            "post_goal_quiet": {
                "cycles": len(baseline_actions),
                "action_counts": dict(counts),
                "active_ratio": active_ratio,
            },
            "final": {
                "tick": host.duck.state.tick,
                "open_concerns": [asdict(row) for row in host.duck.concerns(status="open")],
                "memory_count": len(host.duck.state.memories),
                "subject_id": host.duck.state.subject_id,
            },
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the DUCK v0.8 motivated-agency simulation")
    parser.add_argument("--out-dir", type=Path, default=None)
    args = parser.parse_args(argv)
    report = run_agency_simulation()
    rendered = json.dumps(report, indent=2, ensure_ascii=False)
    print(rendered)
    if args.out_dir is not None:
        args.out_dir.mkdir(parents=True, exist_ok=True)
        (args.out_dir / "agency_simulation_v08.json").write_text(rendered + "\n", encoding="utf-8")
        lines = ["# DUCK Motivated Agency Simulation v0.8", "", f"Overall: {'PASS' if report['passed'] else 'FAIL'}", ""]
        for name, passed in report["gates"].items():
            lines.append(f"- {name}: {'PASS' if passed else 'FAIL'}")
        lines.extend(["", f"Post-goal quiet actions: `{json.dumps(report['post_goal_quiet']['action_counts'], sort_keys=True)}`"])
        (args.out_dir / "agency_simulation_v08.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
