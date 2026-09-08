"""Longitudinal motivated-cognition simulation for MicroPsiDUCK v0.10.

This is an architecture stress test, not a consciousness test. One persistent
subject is carried through recurring people, associative recall, curiosity,
planning failure and recovery, obstacle pressure, restart, threat, fatigue,
repair, commitments, and quiet time with inner language disabled throughout.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict, is_dataclass
import json
from pathlib import Path
import tempfile
from typing import Any

from .host import PersistentDuckHost
from .living import WorldEvent


def _contains_float(value: Any) -> bool:
    if isinstance(value, float):
        return True
    if is_dataclass(value):
        return _contains_float(asdict(value))
    if isinstance(value, dict):
        return any(_contains_float(item) for item in value.values())
    if isinstance(value, (list, tuple, set, frozenset)):
        return any(_contains_float(item) for item in value)
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


def run_motivated_life() -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory) / "motivated-v010"
        host = PersistentDuckHost.open(root, name="Aster", subject_id="motivated-v010-life")
        host.duck.state.affect["fear"] = 0.03
        host.duck.state.affect["loneliness"] = 0.10
        host.duck.state.needs.update(
            {
                "energy": 0.94,
                "affiliation": 0.18,
                "curiosity": 0.86,
                "safety": 0.94,
                "competence": 0.68,
                "coherence": 0.80,
                "autonomy": 0.72,
            }
        )

        timeline: list[dict[str, Any]] = []
        access_violations: list[str] = []
        language_violations: list[str] = []
        CONTROL_TOKENS = (
            "mot000",
            "active_motive_ids",
            "propagation_depth",
            "retrieval_budget",
            "route_index",
            "step_index",
            "strategy_success",
            "pc_",
            "pl_",
        )

        def active_themes() -> list[str]:
            cycle = host.duck.current_cycle
            if cycle is None:
                return []
            rows: list[str] = []
            for motive_id in cycle.active_motive_ids:
                motive = host.duck.control.motive_for(motive_id)
                if motive is not None:
                    rows.append(motive.theme)
            return list(dict.fromkeys(rows))

        def capture(day: int, label: str, step) -> dict[str, Any]:
            lines = _subjective_lines(step)
            joined = " ".join(lines).lower()
            if _contains_float(step.subjective_moment):
                access_violations.append(f"day {day} {label}: numeric telemetry reached SubjectiveMoment")
            if any(token in joined for token in CONTROL_TOKENS):
                access_violations.append(f"day {day} {label}: control metadata leaked into first-person access")
            if step.inner_cognition.thought is not None:
                language_violations.append(f"day {day} {label}")
            motivated = step.developer_trace.get("motivated_cognition", {})
            dominant_id = motivated.get("dominant_motive_id")
            dominant = host.duck.control.motive_for(dominant_id)
            row = {
                "day": day,
                "label": label,
                "tick": step.tick,
                "action": step.selected_action,
                "dominant_motive": dominant.theme if dominant is not None else None,
                "active_motives": active_themes(),
                "modulation": motivated.get("modulation", {}),
                "activated_memory_ids": motivated.get("activated_memory_ids", []),
                "recalled_memory_ids": list(step.recalled_memory_ids),
                "goal_formation": step.developer_trace.get("goal_formation"),
                "planning": step.developer_trace.get("planning"),
                "subjective": lines,
            }
            timeline.append(row)
            return row

        def observe(day: int, label: str, event: WorldEvent):
            step = host.observe(event, allow_inner_speech=False)
            return step, capture(day, label, step)

        def heartbeat(day: int, label: str):
            step = host.heartbeat(1, allow_inner_speech=False)[0]
            return step, capture(day, label, step)

        def memory_id(text: str) -> str | None:
            for memory in reversed(host.duck.state.memories):
                if memory.text == text:
                    return memory.memory_id
            return None

        def resolve(step, success: float, valence: float, description: str, tags: tuple[str, ...] = ()) -> None:
            pending = host.duck.state.pending_action
            if pending is not None and pending.action_id == step.action_id:
                host.resolve_outcome(
                    step.action_id,
                    success=success,
                    valence=valence,
                    description=description,
                    tags=tags,
                )

        # Days 1-3: recurring-person associative bridge.
        dinner_text = "Sarah and I shared dinner beside the garden fountain."
        step, _ = observe(
            1,
            "sarah_dinner",
            WorldEvent("encounter", "Sarah", dinner_text, ("social", "garden"), 0.35, 0.45),
        )
        resolve(step, 0.85, 0.35, "Dinner with Sarah felt easy and familiar.", ("social", "garden"))

        flower_text = "A cobalt flower opened beside the old stone wall."
        step, _ = observe(
            2,
            "garden_flower",
            WorldEvent("observation", "world", flower_text, ("garden", "flower"), 0.20, 0.32),
        )
        resolve(step, 0.80, 0.20, "I had time to notice the unusual flower.", ("garden", "flower"))
        flower_id = memory_id(flower_text)

        sarah_return, sarah_return_row = observe(
            3,
            "sarah_returns",
            WorldEvent("encounter", "Sarah", "Sarah arrives at the door.", ("social",), 0.10, 0.25),
        )
        associative_bridge = bool(
            flower_id
            and flower_id in sarah_return_row["activated_memory_ids"]
            and flower_id in sarah_return.recalled_memory_ids
        )

        # Days 4-6: curiosity recruits a plan, failure changes route, success completes it.
        host.duck.state.needs["curiosity"] = 0.92
        host.duck.state.needs["energy"] = 0.90
        host.duck.state.needs["safety"] = 0.95
        host.duck.state.affect["fear"] = 0.02
        mystery, mystery_row = observe(
            4,
            "novel_console",
            WorldEvent(
                "observation",
                "world",
                "An unfamiliar console is repeating a violet signal.",
                ("novel", "mystery", "console"),
                0.0,
                0.55,
            ),
        )
        plans = host.duck.plans(status="active")
        curiosity_plan_formed = bool(plans and plans[0].kind == "investigate")
        first_route = plans[0].current_route if plans else None

        failed_attempt, _ = heartbeat(4, "curiosity_plan_attempt")
        failed_planning = failed_attempt.developer_trace.get("planning")
        if failed_planning and failed_planning.get("attempted"):
            resolve(
                failed_attempt,
                0.08,
                -0.35,
                "The first approach did not explain the violet signal.",
                ("console", "failed_attempt"),
            )
        revised_plans = host.duck.plans(status="active")
        second_route = revised_plans[0].current_route if revised_plans else None
        counterfactual_replan = bool(first_route and second_route and first_route != second_route)

        plan_guard = 0
        while host.duck.plans(status="active") and plan_guard < 6:
            plan_guard += 1
            step, row = heartbeat(5, f"curiosity_recovery_{plan_guard}")
            planning = step.developer_trace.get("planning")
            if planning and planning.get("attempted"):
                resolve(
                    step,
                    0.90,
                    0.24,
                    f"Curiosity plan step {plan_guard} worked.",
                    ("console", "information", "success"),
                )
        curiosity_plan_completed = not host.duck.plans(status="active") and bool(host.duck.plans(status="completed"))

        # Day 6: a newly afforded obstacle can recruit from the active motive set even if
        # a prior curiosity motive still has motivational inertia.
        host.duck.state.needs["autonomy"] = 0.88
        host.duck.state.needs["competence"] = 0.62
        obstacle, obstacle_row = observe(
            6,
            "blocked_garden_gate",
            WorldEvent(
                "observation",
                "world",
                "A jammed gate blocks the route into the garden.",
                ("obstacle", "blocked", "garden", "gate"),
                -0.05,
                0.48,
            ),
        )
        obstacle_plans = host.duck.plans(status="active")
        obstacle_plan = next((plan for plan in obstacle_plans if plan.kind == "overcome"), None)
        obstacle_goal_recruited = obstacle_plan is not None
        obstacle_plan_id = obstacle_plan.plan_id if obstacle_plan is not None else None

        # Restart while the obstacle plan and motivated-cognition state are live.
        before_restart = {
            "subject_id": host.duck.state.subject_id,
            "motive_ids": set(host.duck.cognitive_state.motives),
            "edge_count": len(host.duck.cognitive_state.graph.edges),
            "plan_id": obstacle_plan_id,
        }
        host.save()
        host = PersistentDuckHost.open(root)
        after_restart = {
            "subject_id": host.duck.state.subject_id,
            "motive_ids": set(host.duck.cognitive_state.motives),
            "edge_count": len(host.duck.cognitive_state.graph.edges),
            "plan_ids": {plan.plan_id for plan in host.duck.plans(status="active")},
        }
        restart_persistence = bool(
            before_restart["subject_id"] == after_restart["subject_id"]
            and before_restart["motive_ids"] == after_restart["motive_ids"]
            and before_restart["edge_count"] == after_restart["edge_count"]
            and obstacle_plan_id in after_restart["plan_ids"]
        )

        obstacle_guard = 0
        while host.duck.plans(status="active") and obstacle_guard < 6:
            obstacle_guard += 1
            step, _ = heartbeat(7, f"obstacle_step_{obstacle_guard}")
            planning = step.developer_trace.get("planning")
            if planning and planning.get("attempted"):
                resolve(
                    step,
                    0.88,
                    0.20,
                    f"Obstacle plan step {obstacle_guard} worked.",
                    ("gate", "progress", "success"),
                )
        obstacle_plan_completed = bool(
            obstacle_plan_id
            and any(plan.plan_id == obstacle_plan_id for plan in host.duck.plans(status="completed"))
        )

        # Days 8-9: explicit threat, then the same non-perceived cognitive probe under
        # threatened and recovered internal regimes.
        host.duck.state.affect["fear"] = 0.12
        threat, threat_row = observe(
            8,
            "garden_threat",
            WorldEvent(
                "encounter",
                "world",
                "Something dangerous lunges from behind the garden wall.",
                ("threat", "garden"),
                -0.80,
                0.95,
            ),
        )
        threat_response = threat_row["dominant_motive"] == "safety" and threat.selected_action in {"step_back", "wait"}
        resolve(threat, 0.90, 0.20, "Backing away kept me out of immediate danger.", ("threat", "safe"))

        probe = WorldEvent(
            "probe",
            "world",
            "A sealed mechanism hums beside me.",
            ("novel", "mystery"),
            0.0,
            0.45,
            perceived=False,
        )
        host.duck.state.affect["fear"] = 0.88
        host.duck.state.needs["safety"] = 0.24
        threatened_probe, threatened_row = observe(8, "same_situation_threatened", probe)

        host.duck.state.affect["fear"] = 0.04
        host.duck.state.needs["safety"] = 0.94
        host.duck.state.needs["energy"] = 0.88
        host.duck.state.needs["curiosity"] = 0.82
        recovered_probe, recovered_row = observe(9, "same_situation_recovered", probe)
        threat_mod = threatened_row["modulation"]
        recovered_mod = recovered_row["modulation"]
        regime_recovery = bool(
            threat_mod
            and recovered_mod
            and threat_mod["propagation_depth"] < recovered_mod["propagation_depth"]
            and threat_mod["planning_depth"] < recovered_mod["planning_depth"]
            and threat_mod["exploration"] < recovered_mod["exploration"]
        )

        # Day 10: fatigue reduces cognitive resolution, recovery restores it.
        host.duck.state.affect["fear"] = 0.03
        host.duck.state.needs["safety"] = 0.94
        host.duck.state.needs["energy"] = 0.12
        _, fatigued_row = observe(10, "fatigued_probe", probe)
        host.duck.state.needs["energy"] = 0.92
        _, rested_row = observe(10, "rested_probe", probe)
        fatigue_mod = fatigued_row["modulation"]
        rested_mod = rested_row["modulation"]
        fatigue_effect = bool(
            fatigue_mod
            and rested_mod
            and fatigue_mod["planning_depth"] < rested_mod["planning_depth"]
            and fatigue_mod["retrieval_budget"] <= rested_mod["retrieval_budget"]
        )

        # Days 11-12: relationship conflict and explicit repair cue.
        host.duck.state.affect["fear"] = 0.04
        host.duck.state.needs["safety"] = 0.92
        conflict, conflict_row = observe(
            11,
            "morgan_conflict",
            WorldEvent(
                "message",
                "Morgan",
                "Morgan admits they ignored something important I asked them to do.",
                ("social", "conflict"),
                -0.50,
                0.62,
            ),
        )
        apology, apology_row = observe(
            12,
            "morgan_apology",
            WorldEvent(
                "message",
                "Morgan",
                "Morgan apologizes and asks to repair what happened.",
                ("social", "repair"),
                0.20,
                0.55,
            ),
        )
        repair_themes = set(apology_row["active_motives"])
        repair_goal = apology_row.get("goal_formation") or {}
        repair_recruited = bool(
            "repair" in repair_themes
            or apology.selected_action == "repair"
            or repair_goal.get("kind") == "repair"
        )

        # Day 13: prospective commitment becomes an endogenous pressure and action.
        commitment = host.duck.create_commitment(
            "Morgan",
            "Morgan will bring the garden map.",
            due_in=2,
            importance=0.92,
        )
        followup = host.duck.register_commitment_followup(commitment)
        host.save()
        followup_acted = False
        commitment_motive_seen = False
        for index in range(5):
            step, row = heartbeat(13, f"commitment_wait_{index}")
            if "commitment" in row["active_motives"] or row["dominant_motive"] == "commitment":
                commitment_motive_seen = True
            agency = step.developer_trace.get("agency") or {}
            if agency.get("selected_concern_id") == followup.memory_id and agency.get("attempted"):
                followup_acted = True
                break
        host.duck.resolve_commitment(
            commitment.commitment_id,
            kept=True,
            outcome="Morgan brought the garden map as promised.",
        )
        heartbeat(13, "commitment_resolved")
        followup_status = host.duck._concern_from_memory(host.duck._concern_memory(followup.memory_id)).status
        commitment_cycle = commitment_motive_seen and followup_acted and followup_status == "satisfied"

        # Resolve any remaining plan roots so quiet-time behavior is measured after
        # motivated work has actually ended, rather than by abandoning state.
        drain_guard = 0
        while host.duck.plans(status="active") and drain_guard < 10:
            drain_guard += 1
            step, _ = heartbeat(14, f"drain_plan_{drain_guard}")
            planning = step.developer_trace.get("planning")
            if planning and planning.get("attempted"):
                resolve(
                    step,
                    0.90,
                    0.20,
                    f"Late plan step {drain_guard} completed.",
                    ("resolution", "success"),
                )

        # Day 14+: quiet negative control.
        host.duck.state.affect["fear"] = 0.03
        host.duck.state.affect["loneliness"] = 0.10
        host.duck.state.needs.update(
            {
                "energy": 0.90,
                "affiliation": 0.20,
                "curiosity": 0.22,
                "safety": 0.94,
                "competence": 0.72,
                "coherence": 0.82,
                "autonomy": 0.72,
            }
        )
        quiet_actions: list[str] = []
        for index in range(30):
            step, _ = heartbeat(15, f"quiet_{index}")
            quiet_actions.append(step.selected_action)
        quiet_counts = Counter(quiet_actions)
        quiet_active_ratio = sum(count for action, count in quiet_counts.items() if action != "wait") / len(quiet_actions)
        quiet_bounded = quiet_active_ratio < 0.45 and not host.duck.plans(status="active")

        motive_themes = {motive.theme for motive in host.duck.cognitive_state.motives.values()}
        broad_motive_coverage = {"safety", "curiosity", "energy", "affiliation", "competence", "coherence", "autonomy", "repair", "commitment"}.issubset(motive_themes)

        gates = {
            "associative_bridge_reaches_nonlexical_memory": associative_bridge,
            "curiosity_forms_endogenous_plan": curiosity_plan_formed,
            "failed_plan_causes_counterfactual_replan": counterfactual_replan,
            "curiosity_plan_completes": curiosity_plan_completed,
            "active_motive_set_can_recruit_obstacle_goal": obstacle_goal_recruited,
            "motivated_state_and_plan_survive_restart": restart_persistence,
            "obstacle_plan_completes_after_restart": obstacle_plan_completed,
            "threat_makes_safety_organizing": threat_response,
            "same_situation_changes_cognitive_regime_after_recovery": regime_recovery,
            "fatigue_reduces_and_recovery_restores_resolution": fatigue_effect,
            "explicit_repair_cue_recruits_repair": repair_recruited,
            "commitment_becomes_endogenous_and_resolves": commitment_cycle,
            "major_motive_families_are_exercised": broad_motive_coverage,
            "quiet_time_is_bounded": quiet_bounded,
            "language_lesion_survives_full_simulation": not language_violations,
            "subject_access_remains_clean": not access_violations,
        }

        return {
            "suite": "MicroPsiDUCK longitudinal motivated cognition v0.10",
            "passed": all(gates.values()),
            "gates": gates,
            "timeline": timeline,
            "quiet": {
                "cycles": len(quiet_actions),
                "action_counts": dict(quiet_counts),
                "active_ratio": quiet_active_ratio,
            },
            "restart": {
                "subject_id_preserved": before_restart["subject_id"] == after_restart["subject_id"],
                "motive_count": len(after_restart["motive_ids"]),
                "edge_count": after_restart["edge_count"],
                "plan_id": obstacle_plan_id,
            },
            "access_violations": access_violations,
            "language_violations": language_violations,
            "final": {
                "subject_id": host.duck.state.subject_id,
                "tick": host.duck.state.tick,
                "motive_themes": sorted(motive_themes),
                "motive_count": len(host.duck.cognitive_state.motives),
                "graph_edge_count": len(host.duck.cognitive_state.graph.edges),
                "active_plans": [asdict(plan) for plan in host.duck.plans(status="active")],
                "completed_plan_count": len(host.duck.plans(status="completed")),
                "memory_count": len(host.duck.state.memories),
            },
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the MicroPsiDUCK v0.10 longitudinal motivated-cognition simulation")
    parser.add_argument("--out-dir", type=Path, default=None)
    args = parser.parse_args(argv)
    report = run_motivated_life()
    rendered = json.dumps(report, indent=2, ensure_ascii=False)
    print(rendered)
    if args.out_dir is not None:
        args.out_dir.mkdir(parents=True, exist_ok=True)
        (args.out_dir / "motivated_simulation_v010.json").write_text(rendered + "\n", encoding="utf-8")
        lines = [
            "# MicroPsiDUCK Longitudinal Motivated Cognition v0.10",
            "",
            f"Overall: {'PASS' if report['passed'] else 'FAIL'}",
            "",
        ]
        for name, passed in report["gates"].items():
            lines.append(f"- {name}: {'PASS' if passed else 'FAIL'}")
        lines.extend(
            [
                "",
                f"Quiet action counts: `{json.dumps(report['quiet']['action_counts'], sort_keys=True)}`",
                f"Quiet active ratio: {report['quiet']['active_ratio']:.3f}",
            ]
        )
        (args.out_dir / "motivated_simulation_v010.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
