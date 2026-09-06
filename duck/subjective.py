"""Subject-accessible representations.

These types intentionally contain no numeric confidence, activation, magnitude,
score, probability, embedding, coordinate, or other implementation telemetry.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Intensity(str, Enum):
    FAINT = "faint"
    MILD = "mild"
    MODERATE = "moderate"
    STRONG = "strong"
    OVERWHELMING = "overwhelming"


class Certainty(str, Enum):
    POSSIBLE = "possible"
    PLAUSIBLE = "plausible"
    LIKELY = "likely"
    CLEAR = "clear"


@dataclass(frozen=True)
class FirstPersonImpression:
    channel: str
    content: str
    intensity: Intensity
    certainty: Certainty = Certainty.CLEAR


@dataclass(frozen=True)
class AccessibleTendency:
    action: str
    felt_as: str


@dataclass(frozen=True)
class SubjectiveMoment:
    """What is currently available to the simulated subject.

    A SubjectiveMoment is not canonical mechanistic state and is not a debug
    packet. It is a bounded first-person projection. All fields intentionally use
    qualitative language rather than implementation telemetry.
    """

    impressions: tuple[FirstPersonImpression, ...] = ()
    tendencies: tuple[AccessibleTendency, ...] = ()
    recollections: tuple[str, ...] = ()
    beliefs: tuple[str, ...] = ()
    concerns: tuple[str, ...] = ()
    temporal_context: tuple[str, ...] = ()
    self_context: tuple[str, ...] = ()
