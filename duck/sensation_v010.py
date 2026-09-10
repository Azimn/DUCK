"""Body-to-perception transduction for the current MicroPsiDUCK runtime.

Body truth remains mechanistic. This sensor emits qualitative sensory evidence that can
compete for attention alongside external stimuli; it does not expose body telemetry to
the experiential or language boundary.
"""
from __future__ import annotations

from .body_v010 import BodyState, energy_deficit
from .perception_v010 import Modality, SensoryEvidence


def body_sensory_evidence(body: BodyState) -> tuple[SensoryEvidence, ...]:
    rows: list[SensoryEvidence] = []
    fatigue = energy_deficit(body)
    if fatigue >= 0.35:
        rows.append(SensoryEvidence(
            Modality.INTEROCEPTION,
            "self",
            "I can feel fatigue building in my body.",
            strength=min(1.0, fatigue),
            reliability=0.95,
            features=("tired_sensation",),
            entity_id="self",
        ))
    if body.sleep_pressure >= 0.45:
        rows.append(SensoryEvidence(
            Modality.INTEROCEPTION,
            "self",
            "I feel sleepy.",
            strength=body.sleep_pressure,
            reliability=0.95,
            features=("sleepy_sensation",),
            entity_id="self",
        ))
    if body.pain_load >= 0.20:
        rows.append(SensoryEvidence(
            Modality.INTEROCEPTION,
            "self",
            "Something in my body hurts.",
            strength=body.pain_load,
            reliability=0.98,
            features=("pain_sensation",),
            entity_id="self",
        ))
    if body.thermal_stress >= 0.25:
        rows.append(SensoryEvidence(
            Modality.INTEROCEPTION,
            "self",
            "The temperature feels uncomfortable to me.",
            strength=body.thermal_stress,
            reliability=0.90,
            features=("warm_sensation",),
            entity_id="self",
        ))
    if body.exertion_load >= 0.20:
        rows.append(SensoryEvidence(
            Modality.INTEROCEPTION,
            "self",
            "I can feel the effort of what I've been doing.",
            strength=body.exertion_load,
            reliability=0.95,
            features=("exertion_sensation",),
            entity_id="self",
        ))
    return tuple(rows)


__all__ = ["body_sensory_evidence"]
