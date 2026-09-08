"""Minimal DUCK runtime with an enforced experiential access boundary.

Developer telemetry and structured subjective diagnostics remain separate from the
prose-only ExperientialFrame supplied to private cognition.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .access import SubjectAccessFirewall
from .cognition import DeterministicInnerVoice, InnerCognition, InnerCognitionProvider
from .mechanics import MechanisticSnapshot
from .subjective import ExperientialFrame, SubjectiveMoment


@dataclass(frozen=True)
class StepResult:
    subjective_moment: SubjectiveMoment
    experiential_frame: ExperientialFrame
    inner_cognition: InnerCognition
    selected_action: str | None
    developer_trace: dict[str, Any]


class DuckRuntime:
    def __init__(self, *, firewall: SubjectAccessFirewall | None = None, cognition: InnerCognitionProvider | None = None) -> None:
        self.firewall = firewall or SubjectAccessFirewall()
        self.cognition = cognition or DeterministicInnerVoice()

    def step(self, snapshot: MechanisticSnapshot, *, allow_inner_speech: bool = True) -> StepResult:
        moment = self.firewall.project(snapshot)
        experience = self.firewall.experience(moment)
        thought = self.cognition.generate(experience) if allow_inner_speech else InnerCognition(None)
        selected_action = moment.tendencies[0].action if moment.tendencies else None
        developer_trace = {
            "mechanistic_snapshot": asdict(snapshot),
            "structured_subjective_projection": asdict(moment),
            "experiential_projection": list(experience.prose),
            "inner_speech_enabled": bool(allow_inner_speech),
        }
        return StepResult(moment, experience, thought, selected_action, developer_trace)
