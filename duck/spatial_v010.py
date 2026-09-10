"""Spatial access adapted from Azimn/TinyPersonaEngine at 5eb2e84.

See docs/DONOR_REUSE_v0.10.md for exact provenance and adaptation boundaries.
Geometry belongs to the host adapter; accessible output is only sensory evidence.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from math import cos, radians, sqrt, isfinite

from .perception_v010 import Modality, SensoryEvidence


@dataclass(frozen=True)
class Vec3:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def __post_init__(self):
        if not all(isfinite(v) for v in (self.x, self.y, self.z)):
            raise ValueError("coordinates must be finite")

    def distance_to(self, other):
        return sqrt((self.x-other.x)**2 + (self.y-other.y)**2 + (self.z-other.z)**2)

    def normalized(self):
        length = sqrt(self.x**2 + self.y**2 + self.z**2)
        if length == 0:
            raise ValueError("direction vector cannot be zero")
        return Vec3(self.x / length, self.y / length, self.z / length)

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def minus(self, other):
        return Vec3(self.x-other.x, self.y-other.y, self.z-other.z)


@dataclass(frozen=True)
class ObserverState:
    character_id: str
    position: Vec3 = Vec3()
    forward: Vec3 = Vec3(1, 0, 0)
    visual_range: float = 25.0
    fov_degrees: float = 100.0
    hearing_range: float = 18.0
    attention_capacity: int = 1

    def __post_init__(self):
        self.forward.normalized()
        if not self.character_id:
            raise ValueError("observer identity is required")
        if not all(isfinite(x) and x > 0 for x in (self.visual_range, self.hearing_range)):
            raise ValueError("sensory ranges must be positive and finite")
        if not 0 < self.fov_degrees <= 360 or not 1 <= self.attention_capacity <= 8:
            raise ValueError("invalid field of view or attention capacity")


@dataclass(frozen=True)
class LocatedStimulus:
    stimulus_id: str
    position: Vec3
    evidence: SensoryEvidence
    occluded: bool = False


@dataclass(frozen=True)
class ObservationPacket:
    observer_id: str
    stimuli: tuple[LocatedStimulus, ...]

    def __post_init__(self):
        object.__setattr__(self, "stimuli", tuple(self.stimuli))
        if len(self.stimuli) > 128:
            raise ValueError("spatial packets are bounded to 128 stimuli")
        ids = [s.stimulus_id for s in self.stimuli]
        if any(not i for i in ids) or len(ids) != len(set(ids)):
            raise ValueError("stimulus IDs must be nonempty and unique")


@dataclass(frozen=True)
class AccessibleStimulus:
    stimulus_id: str
    evidence: SensoryEvidence
    salience: float


class ObserverMismatch(ValueError):
    pass


class PerceptionFilter:
    def access_confidence(self, stimulus: LocatedStimulus, observer: ObserverState) -> float:
        distance = observer.position.distance_to(stimulus.position)
        evidence = stimulus.evidence
        modality = evidence.modality
        if modality in {Modality.TOUCH, Modality.INTEROCEPTION, Modality.PROPRIOCEPTION}:
            return evidence.strength if distance <= 0.75 else 0.0
        if modality == Modality.VISION:
            if stimulus.occluded or distance > observer.visual_range:
                return 0.0
            if distance > 0:
                direction = stimulus.position.minus(observer.position).normalized()
                if observer.forward.normalized().dot(direction) < cos(radians(observer.fov_degrees / 2.0)):
                    return 0.0
            return evidence.strength * max(0.1, 1.0-distance / observer.visual_range)
        if modality in {Modality.AUDITION, Modality.LANGUAGE}:
            if distance > observer.hearing_range:
                return 0.0
            return evidence.strength * (0.45 if stimulus.occluded else 1.0) * max(0.1, 1.0-distance / observer.hearing_range)
        return 0.0

    def filter(self, packet: ObservationPacket, observer: ObserverState) -> tuple[AccessibleStimulus, ...]:
        if packet.observer_id != observer.character_id:
            raise ObserverMismatch("observation belongs to a different private perspective")
        rows = []
        for stimulus in packet.stimuli:
            confidence = min(stimulus.evidence.reliability, self.access_confidence(stimulus, observer))
            if confidence <= 0:
                continue
            evidence = replace(stimulus.evidence, reliability=confidence)
            # Urgency must be appraised by the subject, never supplied as a host flag.
            salience = min(1.0, 0.65 * evidence.strength + 0.25 * confidence)
            rows.append(AccessibleStimulus(stimulus.stimulus_id, evidence, salience))
        return tuple(rows)


class AttentionSelector:
    """Donor bounded ranking, with stable ties and caller-owned motive relevance."""
    def select(self, accessible, *, capacity=1, relevant_features=frozenset()):
        if not 1 <= capacity <= 8:
            raise ValueError("attention capacity must be between one and eight")
        ranked = sorted(accessible, key=lambda row: (
            -(row.salience + 0.2 * bool(set(row.evidence.features) & relevant_features)), row.stimulus_id))
        return tuple(ranked[:capacity])
