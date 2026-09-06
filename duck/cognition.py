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
    """A first-person fallback, not a language model.

    It proves that the organism can continue to deliberate when no model is
    available. It only sees SubjectiveMoment.
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
        if moment.recollections and any("wary" in concern.lower() for concern in moment.concerns):
            return InnerCognition("I've been here before. I don't want to ignore what happened last time.")
        if any("waiting to see whether" in concern.lower() for concern in moment.concerns):
            return InnerCognition("I'm still waiting to see if they actually follow through.")
        if any("connection" in concern.lower() for concern in moment.concerns):
            return InnerCognition("I don't really want to be by myself right now.")
        if uncertain_recognition:
            return InnerCognition("I think I know who that is, but I'm not completely sure.")
        if unexpected:
            return InnerCognition("That wasn't what I expected.")
        if moment.recollections:
            return InnerCognition(moment.recollections[0])
        return InnerCognition(None)
