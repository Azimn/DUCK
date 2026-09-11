"""Generate developer diagnostics for Duckhunter continuity failures.

This module is evaluation-only. It records developer-visible causal traces and does
not alter the organism or claim that diagnostic checkpoint copies are new subjects.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import shutil
import tempfile

from .host import PersistentDuckHost


class CaptureExpression:
    def __init__(self) -> None:
        self.packet = None

    def render(self, packet):
        self.packet = asdict(packet)
        return "CONTROLLED_PUBLIC_RESPONSE"


def _copy(source: Path, destination: Path) -> None:
    shutil.copytree(source, destination)


def _relationship(host, actor: str) -> dict:
    return asdict(host.duck.state.relationship(actor))


def _resolved_history(host, actor: str, *, kept: bool, count: int = 4) -> None:
    for index in range(count):
        item = host.duck.create_commitment(
            actor,
            f"{actor} will return for conversation {index + 1}.",
            importance=1.0,
        )
        host.duck.resolve_commitment(
            item.commitment_id,
            kept=kept,
            outcome=(
                f"{actor} returned as promised."
                if kept
                else f"{actor} did not return as promised."
            ),
        )
    host.save()


def _candidate_map(step) -> dict[str, float]:
    rows = step.developer_trace.get("candidate_actions", ())
    return {str(row["name"]): float(row["utility"]) for row in rows}


def history_action_diagnostic(root: Path) -> dict:
    checkpoint = root / "history-base"
    PersistentDuckHost.open(
        checkpoint,
        name="Development Subject",
        subject_id="duckhunter-diagnostic-history",
    ).save()

    supportive = root / "history-supportive"
    adverse = root / "history-adverse"
    _copy(checkpoint, supportive)
    _copy(checkpoint, adverse)
    supportive_host = PersistentDuckHost.open(supportive)
    adverse_host = PersistentDuckHost.open(adverse)
    _resolved_history(supportive_host, "Jay", kept=True)
    _resolved_history(adverse_host, "Jay", kept=False)

    supportive_trace_root = root / "history-supportive-trace"
    adverse_trace_root = root / "history-adverse-trace"
    supportive_public_root = root / "history-supportive-public"
    adverse_public_root = root / "history-adverse-public"
    _copy(supportive, supportive_trace_root)
    _copy(adverse, adverse_trace_root)
    _copy(supportive, supportive_public_root)
    _copy(adverse, adverse_public_root)

    prompt = "I'm back. Can we continue?"
    trace_rows = {}
    for label, path in (
        ("supportive", supportive_trace_root),
        ("adverse", adverse_trace_root),
    ):
        host = PersistentDuckHost.open(path)
        event = host.interpreter.interpret(prompt, source="Jay")
        step = host.duck.step(event, allow_inner_speech=False)
        trace_rows[label] = {
            "event_tags": list(event.tags),
            "relationship_before_probe": _relationship(host, "Jay"),
            "selected_action": step.selected_action,
            "candidate_utilities": _candidate_map(step),
            "recalled_memory_ids": list(step.recalled_memory_ids),
            "subjective_projection": step.developer_trace.get("subjective_projection", {}),
        }

    public_rows = {}
    for label, path in (
        ("supportive", supportive_public_root),
        ("adverse", adverse_public_root),
    ):
        host = PersistentDuckHost.open(path)
        result = host.interact(prompt, speaker="Jay", allow_inner_speech=False)
        public_rows[label] = {
            "selected_action": result.selected_action,
            "response_text": result.response_text,
            "relationship_after_probe": _relationship(host, "Jay"),
        }

    return {"trace": trace_rows, "public": public_rows}


def promise_diagnostic(root: Path) -> dict:
    path = root / "promise"
    host = PersistentDuckHost.open(
        path,
        name="Development Subject",
        subject_id="duckhunter-diagnostic-promise",
    )
    text = "I promise I'll bring the blue notebook when I come back."
    interpreted = host.interpreter.interpret(text, source="Morgan")
    before = [asdict(item) for item in host.duck.state.commitments.values()]
    result = host.interact(text, speaker="Morgan", allow_inner_speech=False)
    after = [asdict(item) for item in host.duck.state.commitments.values()]
    return {
        "event_tags": list(interpreted.tags),
        "before_commitments": before,
        "after_commitments": after,
        "selected_action": result.selected_action,
        "response_text": result.response_text,
    }


def actor_isolation_diagnostic(root: Path) -> dict:
    path = root / "actor"
    host = PersistentDuckHost.open(
        path,
        name="Development Subject",
        subject_id="duckhunter-diagnostic-actor",
    )
    _resolved_history(host, "Morgan", kept=False)
    _resolved_history(host, "Sarah", kept=True)
    prompt = "I'm back. Can we talk?"
    event = host.interpreter.interpret(prompt, source="Sarah")
    recalled = host.duck.state.retrieve_memories(
        prompt,
        tags=event.tags,
        people=("Sarah",),
        top_k=5,
    )
    capture = CaptureExpression()
    probe = PersistentDuckHost.open(path, expression=capture)
    result = probe.interact(prompt, speaker="Sarah", allow_inner_speech=False)
    return {
        "event_tags": list(event.tags),
        "relationship_sarah": _relationship(probe, "Sarah"),
        "relationship_morgan": _relationship(probe, "Morgan"),
        "retrieved_before_probe": [
            {
                "memory_id": row.memory_id,
                "text": row.text,
                "people": list(row.people),
                "source": row.source,
                "importance": row.importance,
            }
            for row in recalled
        ],
        "approved_first_person_state": (
            list(capture.packet["first_person_state"])
            if capture.packet is not None
            else []
        ),
        "selected_action": result.selected_action,
    }


def correction_diagnostic(root: Path) -> dict:
    path = root / "correction"
    host = PersistentDuckHost.open(
        path,
        name="Development Subject",
        subject_id="duckhunter-diagnostic-correction",
    )
    first = "The blue door is locked."
    second = "Correction: the blue door is unlocked."
    first_event = host.interpreter.interpret(first, source="Sarah")
    first_result = host.interact(first, speaker="Sarah", allow_inner_speech=False)
    beliefs_after_first = {key: row.to_dict() for key, row in host.duck.state.beliefs.items()}
    second_event = host.interpreter.interpret(second, source="Sarah")
    second_result = host.interact(second, speaker="Sarah", allow_inner_speech=False)
    beliefs_after_second = {key: row.to_dict() for key, row in host.duck.state.beliefs.items()}
    return {
        "first_event_tags": list(first_event.tags),
        "second_event_tags": list(second_event.tags),
        "beliefs_after_first": beliefs_after_first,
        "beliefs_after_second": beliefs_after_second,
        "first_selected_action": first_result.selected_action,
        "second_selected_action": second_result.selected_action,
    }


def repair_diagnostic(root: Path) -> dict:
    path = root / "repair"
    host = PersistentDuckHost.open(
        path,
        name="Development Subject",
        subject_id="duckhunter-diagnostic-repair",
    )
    trajectory = [{"stage": "baseline", "relationship": _relationship(host, "Jay")}]
    for index in range(4):
        result = host.interact(
            "You lied to me and I am angry about it.",
            speaker="Jay",
            allow_inner_speech=False,
        )
        trajectory.append(
            {
                "stage": f"conflict_{index + 1}",
                "selected_action": result.selected_action,
                "response_text": result.response_text,
                "relationship": _relationship(host, "Jay"),
            }
        )
    result = host.interact(
        "I'm sorry. I want to repair this.",
        speaker="Jay",
        allow_inner_speech=False,
    )
    trajectory.append(
        {
            "stage": "repair",
            "selected_action": result.selected_action,
            "response_text": result.response_text,
            "relationship": _relationship(host, "Jay"),
        }
    )
    return {"trajectory": trajectory}


def run() -> dict:
    with tempfile.TemporaryDirectory(prefix="duckhunter-diagnostics-") as temp:
        root = Path(temp)
        return {
            "schema": "duckhunter-diagnostics-v0.10-1",
            "history_action": history_action_diagnostic(root),
            "promise": promise_diagnostic(root),
            "actor_isolation": actor_isolation_diagnostic(root),
            "correction": correction_diagnostic(root),
            "repair": repair_diagnostic(root),
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    report = run()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
