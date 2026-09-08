"""Focused executable evaluation for the MicroPsiDUCK v0.10 control spine."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

from .host import PersistentDuckHost
from .living import SubjectState, WorldEvent
from .living_v010 import LivingDuck


def _state(subject_id: str) -> SubjectState:
    state = SubjectState.create("Aster", subject_id)
    state.affect["fear"] = 0.02
    state.needs["energy"] = 0.95
    state.needs["safety"] = 0.95
    state.needs["curiosity"] = 0.88
    state.needs["competence"] = 0.72
    state.needs["coherence"] = 0.82
    state.needs["autonomy"] = 0.72
    state.needs["affiliation"] = 0.18
    return state


def motive_competition() -> dict:
    duck = LivingDuck(_state("eval-motives"))
    duck.step(
        WorldEvent("observation", "world", "A strange mechanism pulses.", ("novel", "mystery"), 0.0, 0.55),
        allow_inner_speech=False,
    )
    first = duck.control.dominant_motive()
    duck.step(
        WorldEvent("encounter", "Morgan", "Morgan threatens me.", ("social", "threat", "conflict"), -0.8, 0.95),
        allow_inner_speech=False,
    )
    second = duck.control.dominant_motive()
    curiosity_survives = any(m.theme == "curiosity" for m in duck.cognitive_state.motives.values())
    return {
        "name": "motive_competition",
        "passed": bool(first and second and first.theme == "curiosity" and second.theme == "safety" and curiosity_survives),
        "first": first.theme if first else None,
        "second": second.theme if second else None,
        "motive_count": len(duck.cognitive_state.motives),
    }


def associative_bridge() -> dict:
    state = _state("eval-bridge")
    state.add_memory("I had dinner with Sarah.", tags=("garden",), people=("Sarah",), importance=0.62)
    flower = state.add_memory("I noticed a blue flower by the old wall.", tags=("garden", "flower"), importance=0.62)
    direct_ids = {
        row.memory_id
        for row in state.retrieve_memories("Sarah arrived.", people=("Sarah",), top_k=5)
    }
    duck = LivingDuck(state)
    step = duck.step(
        WorldEvent("encounter", "Sarah", "Sarah arrived.", ("social",), 0.0, 0.30),
        allow_inner_speech=False,
    )
    activated = set(step.developer_trace["motivated_cognition"]["activated_memory_ids"])
    return {
        "name": "associative_bridge",
        "passed": flower.memory_id not in direct_ids and flower.memory_id in activated and flower.memory_id in step.recalled_memory_ids,
        "direct_ids": sorted(direct_ids),
        "activated_ids": sorted(activated),
    }


def modulation_regimes() -> dict:
    event = WorldEvent("observation", "world", "An unfamiliar device hums.", ("novel", "mystery"), 0.0, 0.45)
    calm_state = _state("eval-calm")
    threat_state = _state("eval-threat")
    threat_state.affect["fear"] = 0.88
    threat_state.needs["safety"] = 0.28
    calm = LivingDuck(calm_state).step(event, allow_inner_speech=False)
    threat = LivingDuck(threat_state).step(event, allow_inner_speech=False)
    a = calm.developer_trace["motivated_cognition"]["modulation"]
    b = threat.developer_trace["motivated_cognition"]["modulation"]
    return {
        "name": "modulation_regimes",
        "passed": (
            b["propagation_depth"] < a["propagation_depth"]
            and b["retrieval_budget"] < a["retrieval_budget"]
            and b["exploration"] < a["exploration"]
        ),
        "calm": a,
        "threat": b,
    }


def persistence_roundtrip() -> dict:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory) / "state"
        host = PersistentDuckHost.open(root, name="Aster", subject_id="eval-v010-persist")
        host.observe(
            WorldEvent("observation", "world", "A strange signal appears.", ("novel", "mystery"), 0.0, 0.50),
            allow_inner_speech=False,
        )
        before = host.duck.cognitive_state.to_dict()
        host.save()
        reopened = PersistentDuckHost.open(root)
        after = reopened.duck.cognitive_state.to_dict()
        return {
            "name": "cognitive_persistence",
            "passed": (
                before["schema_version"] == after["schema_version"]
                and set(before["motives"]) == set(after["motives"])
                and len(before["graph"]["edges"]) == len(after["graph"]["edges"])
            ),
            "motive_count": len(after["motives"]),
            "edge_count": len(after["graph"]["edges"]),
        }


def language_lesion() -> dict:
    duck = LivingDuck(_state("eval-lesion-v010"))
    step = duck.step(
        WorldEvent("encounter", "world", "Something dangerous approaches.", ("threat",), -0.8, 0.9),
        allow_inner_speech=False,
    )
    return {
        "name": "language_lesion_v010",
        "passed": (
            step.inner_cognition.thought is None
            and bool(step.selected_action)
            and duck.current_cycle is not None
            and bool(duck.current_cycle.dominant_motive_id)
            and bool(duck.last_experience.prose)
        ),
        "action": step.selected_action,
        "dominant_motive": duck.control.dominant_motive().theme if duck.control.dominant_motive() else None,
    }


def run_all() -> dict:
    results = [
        motive_competition(),
        associative_bridge(),
        modulation_regimes(),
        persistence_roundtrip(),
        language_lesion(),
    ]
    return {"suite": "MicroPsiDUCK motivated cognition v0.10", "passed": all(row["passed"] for row in results), "results": results}


def main() -> int:
    report = run_all()
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
