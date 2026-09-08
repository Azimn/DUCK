"""Private cognition interfaces operating on experiential state.

The v0.10 candidate runtime guarantees that providers receive ExperientialFrame.
A narrow SubjectiveMoment compatibility path remains here so promoted v0.9
regression harnesses continue to execute unchanged until v0.10 is promoted.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .subjective import ExperientialFrame, SubjectiveMoment


@dataclass(frozen=True)
class InnerCognition:
    thought: str | None


class InnerCognitionProvider(Protocol):
    def generate(self, experience: ExperientialFrame) -> InnerCognition:
        ...


def _legacy_experience(moment: SubjectiveMoment) -> ExperientialFrame:
    lines: list[str] = [item.content for item in moment.impressions]
    lines.extend(item.felt_as for item in moment.tendencies)
    lines.extend(moment.recollections)
    lines.extend(moment.beliefs)
    lines.extend(moment.concerns)
    lines.extend(moment.temporal_context)
    lines.extend(moment.self_context)
    return ExperientialFrame(tuple(line for line in lines if line))


def _coerce_experience(value: ExperientialFrame | SubjectiveMoment) -> ExperientialFrame:
    if isinstance(value, ExperientialFrame):
        return value
    if isinstance(value, SubjectiveMoment):
        return _legacy_experience(value)
    raise TypeError("private cognition requires experiential state")


class DeterministicInnerVoice:
    """A first-person fallback, not a language model.

    v0.10 callers pass ExperientialFrame directly. The legacy conversion exists
    solely so v0.9 regression paths remain executable during candidate development.
    """

    def generate(self, experience: ExperientialFrame | SubjectiveMoment) -> InnerCognition:
        experience = _coerce_experience(experience)
        lines = tuple(line.lower() for line in experience.prose)
        strong_fear = any("i'm scared" in line or "i am scared" in line for line in lines)
        step_back = any("i want to step back" in line for line in lines)
        unexpected = any("isn't what i expected" in line or "wasn't what i expected" in line for line in lines)
        uncertain_recognition = any(
            "i think that's" in line or "that might be" in line or "looks familiar" in line
            for line in lines
        )
        unexplained_unease = any("not sure why" in line for line in lines)

        if strong_fear and step_back:
            return InnerCognition("I don't like this. I should give myself some space.")
        if unexplained_unease:
            return InnerCognition("Something feels wrong, and I can't quite place why.")
        if any("i remember" in line for line in lines) and any("wary" in line for line in lines):
            return InnerCognition("I've been here before. I don't want to ignore what happened last time.")
        if any("waiting to see whether" in line for line in lines):
            return InnerCognition("I'm still waiting to see if they actually follow through.")
        if any("connection" in line for line in lines):
            return InnerCognition("I don't really want to be by myself right now.")
        if uncertain_recognition:
            return InnerCognition("I think I know who that is, but I'm not completely sure.")
        if unexpected:
            return InnerCognition("That wasn't what I expected.")
        if experience.prose:
            recollection = next((line for line in experience.prose if line.startswith("I remember")), None)
            if recollection:
                return InnerCognition(recollection)
        return InnerCognition(None)
