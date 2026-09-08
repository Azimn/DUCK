"""Private cognition interfaces operating only on prose-only experiential state."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .subjective import ExperientialFrame


@dataclass(frozen=True)
class InnerCognition:
    thought: str | None


class InnerCognitionProvider(Protocol):
    def generate(self, experience: ExperientialFrame) -> InnerCognition:
        ...


class DeterministicInnerVoice:
    """A first-person fallback, not a language model.

    It proves that the organism can continue to deliberate when no model is
    available. It receives only ExperientialFrame and therefore cannot inspect
    channels, scores, tags, IDs, certainty telemetry, or other substrate state.
    """

    def generate(self, experience: ExperientialFrame) -> InnerCognition:
        if not isinstance(experience, ExperientialFrame):
            raise TypeError("private cognition requires ExperientialFrame")

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
