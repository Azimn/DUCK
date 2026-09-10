"""Reproducible, scoped comparison of overlapping prior-work mechanisms.

Baselines reconstruct the inspected donor rules where noted. This is an acceptance
comparison on declared cases, not independent human evaluation or global optimality.
"""
from __future__ import annotations

import argparse
from dataclasses import replace
import json
from pathlib import Path
import subprocess
import tempfile
from time import perf_counter

from .authoritative_organism_v010 import LivingDuck
from .affordances_v010 import grounded_affordances
from .host_current import PersistentDuckHostCurrent
from .perception_v010 import Modality, SensoryEvidence, perceive
from .room_v010 import RoomState
from .spatial_v010 import AttentionSelector, LocatedStimulus, ObservationPacket, ObserverState, PerceptionFilter, Vec3


DONORS = {"TinyPersonaEngine": "5eb2e84dbb43c828fae7a1459c9fd13535c7b332",
          "Persona-and-Jelly-Sandwich-": "f196ddef26ca755d814b5fb3e4ed41d1fead01a3"}


def spatial_comparison():
    observer = ObserverState("aster")
    cases = [
        ("visible", Modality.VISION, Vec3(2, 0, 0), False, True),
        ("behind", Modality.VISION, Vec3(-2, 0, 0), False, False),
        ("occluded", Modality.VISION, Vec3(2, 0, 0), True, False),
        ("distant", Modality.VISION, Vec3(40, 0, 0), False, False),
        ("hear_behind", Modality.AUDITION, Vec3(-2, 0, 0), False, True),
        ("hear_occluded", Modality.AUDITION, Vec3(2, 0, 0), True, True),
        ("inaudible", Modality.AUDITION, Vec3(40, 0, 0), False, False),
        ("touch_near", Modality.TOUCH, Vec3(.2, 0, 0), False, True),
        ("touch_far", Modality.TOUCH, Vec3(2, 0, 0), False, False),
    ]
    results = []
    for name, modality, position, blocked, expected in cases:
        evidence = SensoryEvidence(modality, "world", "A signal.", strength=1)
        item = LocatedStimulus(name, position, evidence, blocked)
        selected = PerceptionFilter().filter(ObservationPacket("aster", (item,)), observer)
        # The previous scalar adapter presupposed a filtered upstream input.
        unfiltered = perceive(evidence).confidence > 0
        results.append({"case": name, "expected_access": expected,
                        "unfiltered_correct": unfiltered == expected, "adapted_correct": bool(selected) == expected})
    return {"decision": "adopt_spatial_prefilter", "cases": results,
            "baseline_passes": sum(r["unfiltered_correct"] for r in results),
            "selected_passes": sum(r["adapted_correct"] for r in results), "case_count": len(results),
            "passed": all(r["adapted_correct"] for r in results)}


def attention_comparison():
    observer = ObserverState("aster")
    objects = (
        LocatedStimulus("object", Vec3(1, 0, 0), SensoryEvidence(Modality.VISION, "world", "A bright object.", strength=.8, features=("object_present",))),
        LocatedStimulus("voice", Vec3(1, 0, 0), SensoryEvidence(Modality.AUDITION, "Morgan", "Morgan raises their voice.", strength=.68, features=("loud_voice",))),
    )
    rows = PerceptionFilter().filter(ObservationPacket("aster", objects), observer)
    selector = AttentionSelector()
    fixed = selector.select(rows)[0].stimulus_id
    subject = LivingDuck()
    subject.regulatory.safety_deficit = .85
    conditional = selector.select(rows, relevant_features=subject.perceptual_priorities())[0].stimulus_id
    subject.regulatory.safety_deficit = .15
    neutral = selector.select(rows, relevant_features=subject.perceptual_priorities())[0].stimulus_id
    return {"decision": "retain_donor_ranking_supply_subject_relevance", "fixed_focus": fixed,
            "threatened_focus": conditional, "neutral_focus": neutral,
            "passed": fixed == "object" and conditional == "voice" and neutral == "object"}


def catchup_comparison():
    # Exact arithmetic of Jelly's inspected cap/remainder rule, not its full host.
    total, tick_seconds, limit = 650, 60, 3
    requested = total // tick_seconds
    baseline_first = min(requested, limit)
    baseline_remainder = total - requested * tick_seconds
    baseline_second = min(baseline_remainder // tick_seconds, 7)
    with tempfile.TemporaryDirectory() as directory:
        host = PersistentDuckHostCurrent.open(directory, subject_id="comparison")
        host.configure_room(RoomState())
        first = host.catch_up_room(total, max_ticks=limit)
        reopened = PersistentDuckHostCurrent.open(directory)
        second = reopened.catch_up_room(0, max_ticks=7)
        actual = reopened.duck.state.tick
    return {"decision": "replace_discarded_time_with_persistent_debt",
            "baseline_lived_ticks": baseline_first + baseline_second,
            "selected_lived_ticks": actual, "expected_ticks": requested,
            "selected_remainder": second["remaining_seconds"],
            "passed": actual == requested and first["remaining_seconds"] == 470 and second["remaining_seconds"] == 50}


def social_comparison():
    cases = [(Modality.LANGUAGE, (), False), (Modality.AUDITION, (), False),
             (Modality.VISION, ("person_present",), True),
             (Modality.AUDITION, ("approaching_person",), True)]
    rows = []
    for modality, features, expected in cases:
        percept = perceive(SensoryEvidence(modality, "Morgan", "Morgan is communicating.", features=features))
        actions = {a.action for a in grounded_affordances(percept)}
        rows.append({"modality": modality.value, "features": features,
                     "baseline_correct": expected,  # Old named-source rule always offered approach.
                     "selected_correct": ("approach" in actions) == expected})
    return {"decision": "require_physical_evidence_for_approach", "cases": rows,
            "baseline_passes": sum(r["baseline_correct"] for r in rows),
            "selected_passes": sum(r["selected_correct"] for r in rows),
            "passed": all(r["selected_correct"] for r in rows)}


def benchmark():
    observer = ObserverState("aster")
    packet = ObservationPacket("aster", tuple(LocatedStimulus(str(i), Vec3(1 + i % 20, 0, 0),
        SensoryEvidence(Modality.VISION, "world", "An object.", strength=.8)) for i in range(48)))
    rounds = 300
    started = perf_counter()
    for _ in range(rounds):
        for stimulus in packet.stimuli:
            perceive(stimulus.evidence)
    scalar = (perf_counter()-started) * 1000 / rounds
    started = perf_counter()
    for _ in range(rounds):
        AttentionSelector().select(PerceptionFilter().filter(packet, observer))
    spatial = (perf_counter()-started) * 1000 / rounds
    return {"stimuli_per_packet": 48, "rounds": rounds,
            "unfiltered_scalar_ms_per_packet": scalar, "spatial_attention_ms_per_packet": spatial,
            "interpretation": "local diagnostic; extra access checks are accepted for correctness, not claimed faster"}


def compare(*, timing=False):
    results = {"spatial_access": spatial_comparison(), "attention": attention_comparison(),
               "catchup": catchup_comparison(), "social_affordances": social_comparison()}
    root = Path(__file__).resolve().parents[1]
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=root, text=True).strip())
    backlog = {"spatial_access": "IMP-019", "attention": "IMP-021",
               "catchup": "IMP-022", "social_affordances": "IMP-023"}
    updates = [{"backlog_id": backlog[name], "classification": "REGRESSION", "scenario": name,
                "evidence": result} for name, result in results.items() if not result["passed"]]
    report = {"schema": "duck.component-comparison.v1", "commit": commit, "dirty": dirty,
              "donor_revisions": DONORS, "results": results, "backlog_updates": updates,
              "passed": all(r["passed"] for r in results.values()),
              "scope": "declared synthetic component contracts; not independent believability or global optimality"}
    if timing:
        report["timing"] = benchmark()
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--benchmark", action="store_true")
    args = parser.parse_args()
    report = compare(timing=args.benchmark)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps({"passed": report["passed"], "results": report["results"]}, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
