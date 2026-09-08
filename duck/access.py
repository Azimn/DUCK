"""The subject-access firewall.

Raw mechanistic state may influence the subject, but it must be projected into
bounded first-person experience before private cognition can access it. Structured
SubjectiveMoment data remains internal diagnostic scaffolding. ExperientialFrame is
the actual access contract and contains prose only.
"""

from __future__ import annotations

from .mechanics import MechanisticSnapshot
from .subjective import (
    AccessibleTendency,
    Certainty,
    ExperientialFrame,
    FirstPersonImpression,
    Intensity,
    SubjectiveMoment,
)


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _intensity(value: float) -> Intensity:
    value = _clamp01(value)
    if value < 0.20:
        return Intensity.FAINT
    if value < 0.40:
        return Intensity.MILD
    if value < 0.60:
        return Intensity.MODERATE
    if value < 0.82:
        return Intensity.STRONG
    return Intensity.OVERWHELMING


def _certainty(value: float) -> Certainty:
    value = _clamp01(value)
    if value < 0.40:
        return Certainty.POSSIBLE
    if value < 0.60:
        return Certainty.PLAUSIBLE
    if value < 0.82:
        return Certainty.LIKELY
    return Certainty.CLEAR


class SubjectAccessFirewall:
    """Translate implementation state into bounded first-person experience."""

    def project(self, snapshot: MechanisticSnapshot) -> SubjectiveMoment:
        """Build internal structured subjective diagnostics from mechanistic state."""
        impressions: list[FirstPersonImpression] = []
        tendencies: list[AccessibleTendency] = []

        fear = _clamp01(snapshot.affect.get("fear", 0.0))
        if fear >= 0.20:
            level = _intensity(fear)
            if level in {Intensity.FAINT, Intensity.MILD}:
                content = "I feel a little uneasy."
            elif level is Intensity.MODERATE:
                content = "I'm nervous."
            else:
                content = "I'm scared."
            impressions.append(FirstPersonImpression("affect", content, level))

        loneliness = _clamp01(snapshot.affect.get("loneliness", 0.0))
        if loneliness >= 0.25:
            level = _intensity(loneliness)
            content = "I've been feeling lonely." if level in {Intensity.MILD, Intensity.MODERATE} else "I really don't want to be alone right now."
            impressions.append(FirstPersonImpression("affect", content, level))

        unease = _clamp01(snapshot.affect.get("unease", 0.0))
        if unease >= 0.25:
            level = _intensity(unease)
            cause = snapshot.hidden_causes.get("unease")
            if cause and "unease" in snapshot.introspectively_accessible_causes:
                content = f"I feel uneasy about {cause}."
            elif cause:
                content = "I feel uneasy, but I'm not sure why."
            else:
                content = "Something feels off."
            impressions.append(FirstPersonImpression("affect", content, level))

        guardedness = _clamp01(snapshot.relationship.get("guardedness", 0.0))
        if guardedness >= 0.50:
            impressions.append(FirstPersonImpression("relationship", "I feel guarded around them.", _intensity(guardedness)))

        trust = _clamp01(snapshot.relationship.get("trust", 0.5))
        if trust <= 0.35:
            impressions.append(FirstPersonImpression("relationship", "I don't completely trust them.", _intensity(1.0 - trust)))
        elif trust >= 0.78:
            impressions.append(FirstPersonImpression("relationship", "I trust them.", _intensity(trust)))

        suspicion = _clamp01(snapshot.relationship.get("suspicion", 0.0))
        if suspicion >= 0.45:
            impressions.append(FirstPersonImpression("relationship", "Something about this feels suspicious.", _intensity(suspicion)))

        prediction_error = _clamp01(snapshot.prediction_error)
        if prediction_error >= 0.45:
            impressions.append(FirstPersonImpression("expectation", "That isn't what I expected.", _intensity(prediction_error)))

        if snapshot.recognition is not None:
            certainty = _certainty(snapshot.recognition.confidence)
            name = snapshot.recognition.candidate
            if certainty is Certainty.CLEAR:
                content = f"That's {name}."
            elif certainty is Certainty.LIKELY:
                content = f"I think that's {name}."
            elif certainty is Certainty.PLAUSIBLE:
                content = f"That might be {name}."
            else:
                content = "That person looks familiar."
            impressions.append(FirstPersonImpression("recognition", content, Intensity.MODERATE, certainty))

        if snapshot.action_tendency:
            action = snapshot.action_tendency.strip()
            tendencies.append(AccessibleTendency(action=action, felt_as=self._felt_tendency(action)))

        return SubjectiveMoment(tuple(impressions), tuple(tendencies))

    def experience(self, moment: SubjectiveMoment) -> ExperientialFrame:
        """Cross the experiential firewall.

        Only prose consequences of the structured projection survive this method.
        Channels, intensities, certainty enums, action tags, IDs, and all numeric
        implementation values remain on the mechanistic side of the boundary.
        """
        lines: list[str] = [item.content for item in moment.impressions]
        lines.extend(item.felt_as for item in moment.tendencies)
        lines.extend(moment.recollections)
        lines.extend(moment.beliefs)
        lines.extend(moment.concerns)
        lines.extend(moment.temporal_context)
        lines.extend(moment.self_context)
        return ExperientialFrame(tuple(line for line in lines if line))

    def project_experience(self, snapshot: MechanisticSnapshot) -> ExperientialFrame:
        return self.experience(self.project(snapshot))

    @staticmethod
    def _felt_tendency(action: str) -> str:
        humanized = action.replace("_", " ")
        if action == "step_back":
            return "I want to step back."
        if action == "approach":
            return "I want to get closer."
        if action == "wait":
            return "I want to wait and see."
        return f"I feel like I should {humanized}."
