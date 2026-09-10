"""Evidence, interpretation and appraisal, separate from host world truth.

Feature vocabulary is deliberately small. Legacy semantic tags travel as explicit
adapter hints only, never as features accepted by the evidence API.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from .body_v010 import unit


class Modality(str, Enum):
    VISION = "vision"
    AUDITION = "audition"
    LANGUAGE = "language"
    TOUCH = "touch"
    PROPRIOCEPTION = "proprioception"
    INTEROCEPTION = "interoception"


OBSERVABLE_FEATURES = frozenset({
    "loud_voice", "approaching_person", "raised_hand", "smile", "offered_object",
    "unfamiliar_object", "blocked_path", "spoken_question", "person_present",
    "receding_person", "impact", "dim_light", "tired_sensation", "warm_sensation",
})


@dataclass(frozen=True)
class FactObservation:
    key: str
    apparent_value: str
    source: str
    reliability: float = 1.0

    def __post_init__(self):
        if not all(isinstance(value, str) for value in (self.key, self.apparent_value, self.source)):
            raise TypeError("fact observations require string values")
        if not self.key or not self.source:
            raise ValueError("observations require a key and source")
        object.__setattr__(self, "reliability", unit(self.reliability))


@dataclass(frozen=True)
class SensoryEvidence:
    modality: Modality
    source: str
    content: str
    strength: float = 0.5
    reliability: float = 1.0
    features: tuple[str, ...] = ()
    observed_facts: tuple[FactObservation, ...] = ()

    def __post_init__(self):
        if not isinstance(self.source, str) or not isinstance(self.content, str):
            raise TypeError("sensory source and content must be strings")
        object.__setattr__(self, "modality", Modality(self.modality))
        object.__setattr__(self, "strength", unit(self.strength))
        object.__setattr__(self, "reliability", unit(self.reliability))
        features = tuple(dict.fromkeys(self.features))
        if not set(features) <= OBSERVABLE_FEATURES:
            raise ValueError("evidence features must be observable cues from the supported vocabulary")
        facts = tuple(self.observed_facts)
        if not all(isinstance(fact, FactObservation) for fact in facts):
            raise TypeError("observed facts must be FactObservation objects")
        if len(facts) > 64:
            raise ValueError("too many observations in a percept")
        object.__setattr__(self, "features", features)
        object.__setattr__(self, "observed_facts", facts)


@dataclass(frozen=True)
class Percept:
    source: str
    modality: Modality
    content: str
    confidence: float
    features: tuple[str, ...] = ()
    observed_facts: tuple[FactObservation, ...] = ()


@dataclass(frozen=True)
class Appraisal:
    valence: float = 0.0
    arousal: float = 0.0
    threat_relevance: float = 0.0
    novelty: float = 0.0
    social_relevance: float = 0.0
    conflict_relevance: float = 0.0
    support_relevance: float = 0.0
    goal_relevance: float = 0.0


def perceive(evidence: SensoryEvidence) -> Percept:
    # Dim light reduces visual access, without changing the world.
    confidence = evidence.reliability
    if evidence.modality == Modality.VISION and "dim_light" in evidence.features:
        confidence *= 0.6
    facts = tuple(FactObservation(f.key, f.apparent_value, f.source,
                                 min(f.reliability, confidence)) for f in evidence.observed_facts)
    return Percept(evidence.source, evidence.modality, evidence.content, confidence,
                   evidence.features, facts)


class LegacyWorldEventAdapter:
    def evidence(self, event) -> SensoryEvidence:
        if not event.perceived and event.kind != "endogenous":
            raise ValueError("hidden world events are not sensory evidence")
        modality = Modality.INTEROCEPTION if event.kind == "endogenous" else (
            Modality.LANGUAGE if event.kind in {"message", "conversation"} else Modality.VISION)
        return SensoryEvidence(modality, event.source, event.text, event.intensity,
                              features=tuple(t for t in event.tags if t in OBSERVABLE_FEATURES),
                              observed_facts=tuple(FactObservation(str(k), str(v), event.source)
                                                   for k, v in event.world_facts if event.perceived))


class AppraisalEngine:
    """Bounded modeling rules, not fitted psychological measurements."""
    def appraise(self, percept, *, relationship, recalled_memories, regulatory,
                 expectation_violation=False, strength=0.5):
        cues = set(percept.features)
        social = "person_present" in cues or percept.source not in {"self", "world", "system", ""}
        negative = max((max(0.0, -m.valence) for m in recalled_memories
                        if percept.source in m.people or m.source == percept.source), default=0.0)
        loud = "loud_voice" in cues
        approach = "approaching_person" in cues
        cue_threat = min(1.0, 0.65 * loud + 0.35 * approach + 0.8 * ("impact" in cues))
        threat = unit(percept.confidence * (
            0.40 * cue_threat + 0.20 * relationship.guardedness * bool(cue_threat)
            + 0.15 * negative * bool(cue_threat) + 0.15 * regulatory.safety_deficit * bool(cue_threat)
            + 0.10 * bool(expectation_violation)))
        support = unit(percept.confidence * (0.35 * ("smile" in cues) + 0.40 * ("offered_object" in cues))
                       * (0.5 + 0.5 * relationship.trust))
        novelty = percept.confidence * float("unfamiliar_object" in cues)
        conflict = unit(threat * float(social and loud))
        return Appraisal(support * 0.6 - threat * 0.8,
                         unit(strength * percept.confidence + 0.2 * threat), threat,
                         novelty, float(social) * percept.confidence, conflict, support,
                         unit(max(novelty, threat, float("blocked_path" in cues))))


def appraisal_to_legacy_tags(appraisal: Appraisal, features=()) -> tuple[str, ...]:
    tags = []
    for tag, value, threshold in (("threat", appraisal.threat_relevance, 0.45),
                                  ("conflict", appraisal.conflict_relevance, 0.5),
                                  ("supportive", appraisal.support_relevance, 0.4),
                                  ("novel", appraisal.novelty, 0.5),
                                  ("social", appraisal.social_relevance, 0.5)):
        if value >= threshold:
            tags.append(tag)
    if "blocked_path" in features:
        tags.append("blocked")
    if "spoken_question" in features:
        tags.append("question")
    return tuple(tags)
