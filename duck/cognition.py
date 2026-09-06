"""Private cognition interfaces operating only on subject-accessible state."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .subjective import Intensity, SubjectiveMoment


@dataclass(frozen=True)
class InnerCognition:
    thought: str | None


class InnerCognitionProvider(Protocol):
    def generate(self, moment: SubjectiveMoment) -> InnerCognition:
        ...


class DeterministicInnerVoice:
    """A tiny first-person baseline, not a language model.

    Its purpose is to make the access boundary testable before any LLM is allowed
    into private cognition.
    """

    def generate(self, moment: SubjectiveMoment) -> InnerCognition:
        strong_fear = any(
            impression.channel == "affect"
            and impression.intensity in {Intensity.STRONG, Intensity.OVERWHELMING}
            and "scared" in impression.content.lower()
            for impression in moment.impressions
        )
        step_back = any(t.action == "step_back" for t in moment.tendencies)
        unexpected = any(i.channel == "expectation" for i in moment.impressions)
        uncertain_recognition = any(i.channel == "recognition" and i.certainty.value != "clear" for i in moment.impressions)
        unexplained_unease = any("not sure why" in i.content.lower() for i in moment.impressions)

        if strong_fear and step_back:
            return InnerCognition("I don't like this. I should give myself some space.")
        if unexplained_unease:
            return InnerCognition("Something feels wrong, and I can't quite place why.")
        if uncertain_recognition:
            return InnerCognition("I think I know who that is, but I'm not completely sure.")
        if unexpected:
            return InnerCognition("That wasn't what I expected.")
        return InnerCognition(None)
