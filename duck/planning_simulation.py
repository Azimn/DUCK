"""Long-horizon endogenous-goal and replanning simulation for DUCK v0.9."""
from __future__ import annotations

import argparse
import json
import tempfile
from collections import Counter
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

from .host_v09 import PersistentDuckHostV09 as PersistentDuckHost
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


def run_planning_simulation() -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory) / "planning"
        host = PersistentDuckHost.open(root, name="Aster", subject_id="planning-21d")
        host.duck.state.needs["curiosity"] = 0.84
        host.duck.state.needs["autonomy"] = 0.78
        host.duck.state.affect["fear"] = 0.05
        timeline: list[dict[str, Any]] = []
        access_violations: list[str] = []
        inner_language_violations: list[str] = []

        def capture(label: str, step) -> None:
            lines = _subjective_lines(step)
            if _contains_float(step.subjective_moment):
                access_violations.append(f"{label}: float reached SubjectiveMoment")
            joined = " ".join(lines).lower()
            if any(token in joined for token in ("pl_", "route_index", "step_index", "plan_id", "pending_concern", "pending_action")):
                access_violations.append(f"{label}: private planning metadata leaked")
            if step.inner_cognition.thought is not None:
                inner_language_violations.append(label)
            timeline.append(
                {
                    "label": label,
                    "tick": step.tick,
                    "action": step.selected_action,
                    "goal_formation": step.developer_trace.get("goal_formation"),
                    "planning": step.developer_trace.get("planning"),
                    "subjective": lines,
                }
            )

        mystery = host.observe(
            WorldEvent(
                "observation",
                "world",
                "A previously unknown control panel is emitting a repeating blue signal.",
                ("mystery", "unknown", "panel"),
                0.05,
                0.45,
            ),
            allow_inner_speech=False,
        )
        capture("mystery_encounter", mystery)
        initial_plans = host.duck.plans(status="active")
        formed_from_experience = len(initial_plans) == 1 and "goal_formation" in mystery.developer_trace
        initial_route = initial_plans[0].current_route if initial_plans else None

        first_attempt = host.heartbeat(1, allow_inner_speech=False)[0]
        capture("direct_attempt", first_attempt)
        host.resolve_outcome(
            first_attempt.action_id,
            success=0.08,
            valence=-0.35,
            description="Direct inspection did not reveal how the panel works.",
            tags=("panel", "failed_attempt"),
        )
        revised = host.duck.plans(status="active")[0]
        replanned_after_failure = initial_route == "direct_exploration" and revised.current_route == "cautious_inquiry" and revised.route_index == 1

        inquiry = host.heartbeat(1, allow_inner_speech=False)[0]
        capture("replanned_inquiry", inquiry)
        host.resolve_outcome(
            inquiry.action_id,
            success=0.90,
            valence=0.20,
            description="Asking produced a useful explanation of the signal pattern.",
            tags=("panel", "information"),
        )
        after_inquiry = host.duck.plans(status="active")[0]
        hierarchy_advanced = inquiry.selected_action == "ask" and after_inquiry.step_index == 1

        inspect = host.heartbeat(1, allow_inner_speech=False)[0]
        capture("informed_inspection", inspect)
        host.resolve_outcome(
            inspect.action_id,
            success=0.94,
            valence=0.32,
            description="The panel was successfully inspected using the new information.",
            tags=("panel", "success"),
        )
        first_plan_completed = bool(host.duck.plans(status="completed")) and not host.duck.plans(status="active")

        obstacle = host.observe(
            WorldEvent(
                "observation",
                "world",
                "A jammed maintenance gate is blocking the route into the garden.",
                ("obstacle", "blocked", "gate", "garden"),
                -0.05,
                0.40,
            ),
            allow_inner_speech=False,
        )
        capture("obstacle_encounter", obstacle)
        obstacle_plans = host.duck.plans(status="active")
        second_goal_formed = len(obstacle_plans) == 1 and obstacle_plans[0].kind == "overcome"
        obstacle_plan_id = obstacle_plans[0].plan_id if obstacle_plans else None
        before_restart = host.status()
        host.save()
        host = PersistentDuckHost.open(root)
        after_restart = host.status()
        restarted_plans = host.duck.plans(status="active")
        restart_preserved_plan = (
            before_restart["subject_id"] == after_restart["subject_id"]
            and obstacle_plan_id is not None
            and any(plan.plan_id == obstacle_plan_id for plan in restarted_plans)
        )

        host.duck.state.affect["fear"] = 0.08
        host.duck.state.needs["energy"] = 0.85
        safety_counter = 0
        while host.duck.plans(status="active") and safety_counter < 6:
            safety_counter += 1
            step = host.heartbeat(1, allow_inner_speech=False)[0]
            capture(f"obstacle_plan_step_{safety_counter}", step)
            planning = step.developer_trace.get("planning")
            if planning and planning.get("attempted"):
                host.resolve_outcome(
                    step.action_id,
                    success=0.88,
                    valence=0.22,
                    description=f"Obstacle plan step {safety_counter} worked.",
                    tags=("gate", "progress"),
                )
        second_plan_completed = obstacle_plan_id is not None and any(
            plan.plan_id == obstacle_plan_id for plan in host.duck.plans(status="completed")
        )

        ordinary = host.observe(
            WorldEvent("observation", "world", "The garden is calm and nothing unusual is happening.", ("ordinary", "garden"), 0.0, 0.12),
            allow_inner_speech=False,
        )
        capture("ordinary_control", ordinary)
        no_false_goal = not host.duck.plans(status="active") and "goal_formation" not in ordinary.developer_trace

        quiet_actions: list[str] = []
        for index in range(40):
            step = host.heartbeat(1, allow_inner_speech=False)[0]
            capture(f"post_plan_quiet_{index}", step)
            quiet_actions.append(step.selected_action)
        counts = Counter(quiet_actions)
        active_ratio = sum(count for action, count in counts.items() if action != "wait") / max(1, len(quiet_actions))
        bounded_after_plans = active_ratio < 0.50 and not host.duck.plans(status="active")

        gates = {
            "experience_can_form_goal": formed_from_experience,
            "counterfactual_failure_triggers_replan": replanned_after_failure,
            "hierarchical_plan_advances": hierarchy_advanced,
            "first_plan_completes": first_plan_completed,
            "second_goal_forms_from_obstacle": second_goal_formed,
            "active_plan_survives_restart": restart_preserved_plan,
            "second_plan_completes_after_restart": second_plan_completed,
            "ordinary_experience_does_not_invent_goal": no_false_goal,
            "post_plan_activity_is_bounded": bounded_after_plans,
            "language_lesion_survives": not inner_language_violations,
            "subject_access_remains_clean": not access_violations,
        }
        return {
            "suite": "DUCK endogenous planning simulation v0.9",
            "passed": all(gates.values()),
            "gates": gates,
            "timeline": timeline,
            "access_violations": access_violations,
            "inner_language_violations": inner_language_violations,
            "quiet": {"cycles": len(quiet_actions), "action_counts": dict(counts), "active_ratio": active_ratio},
            "final": {
                "subject_id": host.duck.state.subject_id,
                "tick": host.duck.state.tick,
                "active_plans": [asdict(plan) for plan in host.duck.plans(status="active")],
                "completed_plans": [asdict(plan) for plan in host.duck.plans(status="completed")],
                "memory_count": len(host.duck.state.memories),
            },
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default=None)
    args = parser.parse_args()
    report = run_planning_simulation()
    if args.out_dir:
        out = Path(args.out_dir)
        out.mkdir(parents=True, exist_ok=True)
        (out / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
