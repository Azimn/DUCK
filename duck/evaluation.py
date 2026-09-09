"""Built-in architectural evaluations for the integrated DUCK candidate."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

from .host_v05 import PersistentDuckHostV05 as PersistentDuckHost
from .living import LivingDuck, SubjectState, WorldEvent


def paired_history() -> dict:
    neutral = LivingDuck(SubjectState.create("A", "eval-neutral"))
    changed = LivingDuck(SubjectState.create("B", "eval-changed"))
    neutral.heartbeat(allow_inner_speech=False)
    event = changed.step(WorldEvent("encounter", "Morgan", "Morgan threatens me.", ("social", "threat", "conflict"), -0.8, 0.9))
    changed.resolve_outcome(event.action_id, success=0.8, valence=-0.7, description="Backing away kept me safe, but Morgan frightened me.", tags=("threat",))
    present = WorldEvent("message", "Morgan", "Morgan says hello.", ("social",), 0.0, 0.3)
    a = neutral.step(present)
    b = changed.step(present)
    return {
        "name": "paired_history",
        "passed": a.subjective_moment != b.subjective_moment and bool(b.recalled_memory_ids),
        "neutral_action": a.selected_action,
        "changed_action": b.selected_action,
        "neutral_subjective": [item.content for item in a.subjective_moment.impressions],
        "changed_subjective": [item.content for item in b.subjective_moment.impressions],
        "changed_recollections": list(b.subjective_moment.recollections),
    }


def language_lesion() -> dict:
    duck = LivingDuck(SubjectState.create("Duck", "eval-lesion"))
    step = duck.step(WorldEvent("encounter", "world", "Something dangerous approaches.", ("threat",), -0.8, 0.9), allow_inner_speech=False)
    duck.resolve_outcome(step.action_id, success=0.9, valence=0.6, description="The action kept me safe.", tags=("threat",))
    learned = duck.state.adaptive.action_associations.get("threat", {}).get(step.selected_action, 0.0)
    return {
        "name": "language_lesion",
        "passed": step.inner_cognition.thought is None and bool(step.selected_action) and learned > 0.0,
        "action": step.selected_action,
        "learned": learned,
    }


def persistence_roundtrip() -> dict:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory) / "state"
        host = PersistentDuckHost.open(root, name="Aster", subject_id="eval-persistence")
        host.observe(WorldEvent("message", "user", "Hello.", ("social",), 0.0, 0.3))
        first = host.status()
        reopened = PersistentDuckHost.open(root)
        second = reopened.status()
        passed = first["subject_id"] == second["subject_id"] and first["tick"] == second["tick"] and first["memory_count"] == second["memory_count"]
        return {"name": "persistence_roundtrip", "passed": passed, "subject_id": second["subject_id"], "tick": second["tick"]}


def run_all() -> dict:
    results = [paired_history(), language_lesion(), persistence_roundtrip()]
    return {"passed": all(row["passed"] for row in results), "results": results}


def main() -> int:
    report = run_all()
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
