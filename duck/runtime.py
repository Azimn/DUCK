"""Minimal DUCK 0.1 runtime.

The runtime deliberately keeps developer telemetry and subject-accessible state in
separate objects. Private cognition receives only SubjectiveMoment.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .access import SubjectAccessFirewall
from .cognition import DeterministicInnerVoice, InnerCognition, InnerCognitionProvider
from .mechanics import MechanisticSnapshot
from .subjective import SubjectiveMoment


@dataclass(frozen=True)
class StepResult:
    subjective_moment: SubjectiveMoment
    inner_cognition: InnerCognition
    selected_action: str | None
    developer_trace: dict[str, Any]


class DuckRuntime:
    def __init__(self, *, firewall: SubjectAccessFirewall | None = None, cognition: InnerCognitionProvider | None = None) -> None:
        self.firewall = firewall or SubjectAccessFirewall()
        self.cognition = cognition or DeterministicInnerVoice()

    def step(self, snapshot: MechanisticSnapshot, *, allow_inner_speech: bool = True) -> StepResult:
        moment = self.firewall.project(snapshot)
        thought = self.cognition.generate(moment) if allow_inner_speech else InnerCognition(None)
        selected_action = moment.tendencies[0].action if moment.tendencies else None
        developer_trace = {
            "mechanistic_snapshot": asdict(snapshot),
            "subjective_projection": asdict(moment),
            "inner_speech_enabled": bool(allow_inner_speech),
        }
        return StepResult(moment, thought, selected_action, developer_trace)
