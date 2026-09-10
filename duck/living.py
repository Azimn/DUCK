"""Integrated persistent-subject runtime for the FrankenDUCK build.

This module intentionally combines lessons from the older Digital Subject,
Gelatinblob, Wayfarer/Ensemble, and the new Subjective Moment kernel without
making any donor repository a runtime dependency.

The mechanistic state is canonical and developer-visible. Private cognition only
receives SubjectiveMoment, never raw numeric telemetry.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
from enum import Enum
import hashlib
import math
import re
import uuid
from typing import Iterable

from .access import SubjectAccessFirewall
from .cognition import DeterministicInnerVoice, InnerCognition, InnerCognitionProvider
from .mechanics import MechanisticSnapshot, RecognitionSignal
from .subjective import SubjectiveMoment


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value)))


def _clamp_signed(value: float) -> float:
    return max(-1.0, min(1.0, float(value)))


_TOKEN_RE = re.compile(r"[a-z0-9']+")


def _tokens(text: str) -> set[str]:
    return set(_TOKEN_RE.findall(text.lower()))


class MemoryProvenance(str, Enum):
    FIRST_PERSON = "first_person"
    TESTIMONY = "testimony"
    WORLD_FACT = "world_fact"
    SELF_REFLECTION = "self_reflection"
    OUTCOME = "outcome"


class BeliefStance(str, Enum):
    TRUE = "true"
    FALSE = "false"
    UNCERTAIN = "uncertain"


@dataclass
class RelationshipState:
    trust: float = 0.50
    attachment: float = 0.20
    guardedness: float = 0.20
    familiarity: float = 0.05
    respect: float = 0.50
    uncertainty: float = 0.50

    def normalize(self) -> None:
        for key in ("trust", "attachment", "guardedness", "familiarity", "respect", "uncertainty"):
            setattr(self, key, _clamp(getattr(self, key)))


@dataclass
class MemoryRecord:
    memory_id: str
    tick: int
    text: str
    tags: tuple[str, ...] = ()
    people: tuple[str, ...] = ()
    valence: float = 0.0
    arousal: float = 0.0
    importance: float = 0.5
    provenance: MemoryProvenance = MemoryProvenance.FIRST_PERSON
    source: str = ""
    confidence: float = 1.0

    def to_dict(self) -> dict:
        data = asdict(self)
        data["provenance"] = self.provenance.value
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "MemoryRecord":
        payload = dict(data)
        payload["tags"] = tuple(payload.get("tags", ()))
        payload["people"] = tuple(payload.get("people", ()))
        payload["provenance"] = MemoryProvenance(payload.get("provenance", "first_person"))
        return cls(**payload)


@dataclass
class BeliefRecord:
    key: str
    text: str
    stance: BeliefStance = BeliefStance.UNCERTAIN
    confidence: float = 0.5
    evidence_refs: tuple[str, ...] = ()
    source: str = "experience"
    updated_tick: int = 0

    def to_dict(self) -> dict:
        data = asdict(self)
        data["stance"] = self.stance.value
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "BeliefRecord":
        payload = dict(data)
        payload["stance"] = BeliefStance(payload.get("stance", "uncertain"))
        payload["evidence_refs"] = tuple(payload.get("evidence_refs", ()))
        return cls(**payload)


@dataclass
class CommitmentRecord:
    commitment_id: str
    actor: str
    text: str
    created_tick: int
    due_tick: int | None = None
    importance: float = 0.5
    status: str = "open"
    resolved_tick: int | None = None
    outcome: str = ""


@dataclass
class Residue:
    channel: str
    magnitude: float
    decay: float
    source: str
    created_tick: int


@dataclass
class PendingAction:
    action_id: str
    name: str
    tags: tuple[str, ...]
    tick: int
    predicted_valence: float = 0.0
    target: str | None = None


@dataclass
class AdaptiveSelfCore:
    """Small path-dependent substrate inspired by the Gelatinblob experiments.

    It is deliberately not exposed to the subject. A recurrent latent trace gives
    different histories persistent internal trajectories, while learned
    tag/action associations let observed outcomes alter later action selection.
    """

    latent: list[float] = field(default_factory=lambda: [0.0] * 8)
    action_associations: dict[str, dict[str, float]] = field(default_factory=dict)

    @staticmethod
    def _feature_vector(text: str, tags: Iterable[str]) -> list[float]:
        payload = (text.lower() + "|" + "|".join(sorted(str(t).lower() for t in tags))).encode("utf-8")
        digest = hashlib.sha256(payload).digest()
        return [((digest[i] / 255.0) * 2.0) - 1.0 for i in range(8)]

    def observe(self, text: str, tags: Iterable[str]) -> None:
        features = self._feature_vector(text, tags)
        previous = list(self.latent)
        for i, value in enumerate(features):
            neighbor = previous[(i - 1) % len(previous)]
            self.latent[i] = math.tanh(0.84 * previous[i] + 0.13 * value + 0.05 * neighbor)

    def bias(self, action: str, tags: Iterable[str]) -> float:
        learned = 0.0
        for tag in tags:
            learned += self.action_associations.get(str(tag).lower(), {}).get(action, 0.0)
        digest = hashlib.sha256(action.encode("utf-8")).digest()
        latent_index = digest[0] % len(self.latent)
        return learned + 0.08 * self.latent[latent_index]

    def learn(self, action: str, tags: Iterable[str], reward: float) -> None:
        reward = _clamp_signed(reward)
        for tag in tags:
            key = str(tag).lower()
            bucket = self.action_associations.setdefault(key, {})
            old = float(bucket.get(action, 0.0))
            bucket[action] = max(-0.45, min(0.45, old + 0.08 * reward))

    def to_dict(self) -> dict:
        return {"latent": list(self.latent), "action_associations": self.action_associations}

    @classmethod
    def from_dict(cls, data: dict) -> "AdaptiveSelfCore":
        latent = [float(x) for x in data.get("latent", [0.0] * 8)]
        if len(latent) != 8:
            latent = (latent + [0.0] * 8)[:8]
        associations = {
            str(tag): {str(action): float(value) for action, value in actions.items()}
            for tag, actions in data.get("action_associations", {}).items()
        }
        return cls(latent=latent, action_associations=associations)


@dataclass
class SubjectState:
    subject_id: str
    name: str = "Duck"
    tick: int = 0
    affect: dict[str, float] = field(default_factory=lambda: {
        "fear": 0.05,
        "unease": 0.05,
        "anger": 0.02,
        "joy": 0.15,
        "loneliness": 0.20,
    })
    needs: dict[str, float] = field(default_factory=lambda: {
        "energy": 0.85,
        "affiliation": 0.25,
        "curiosity": 0.35,
        "safety": 0.85,
        "competence": 0.55,
        "coherence": 0.70,
        "autonomy": 0.65,
    })
    relationships: dict[str, RelationshipState] = field(default_factory=dict)
    memories: list[MemoryRecord] = field(default_factory=list)
    beliefs: dict[str, BeliefRecord] = field(default_factory=dict)
    world_facts: dict[str, str] = field(default_factory=dict)
    commitments: dict[str, CommitmentRecord] = field(default_factory=dict)
    residues: list[Residue] = field(default_factory=list)
    adaptive: AdaptiveSelfCore = field(default_factory=AdaptiveSelfCore)
    pending_action: PendingAction | None = None
    recent_actions: list[str] = field(default_factory=list)
    self_narrative: list[str] = field(default_factory=list)
    memory_counter: int = 0
    commitment_counter: int = 0

    @classmethod
    def create(cls, name: str = "Duck", subject_id: str | None = None) -> "SubjectState":
        return cls(subject_id=subject_id or str(uuid.uuid4()), name=name)

    def relationship(self, actor: str) -> RelationshipState:
        key = str(actor or "unknown")
        if key not in self.relationships:
            self.relationships[key] = RelationshipState()
        return self.relationships[key]

    def add_memory(
        self,
        text: str,
        *,
        tags: Iterable[str] = (),
        people: Iterable[str] = (),
        valence: float = 0.0,
        arousal: float = 0.0,
        importance: float = 0.5,
        provenance: MemoryProvenance = MemoryProvenance.FIRST_PERSON,
        source: str = "",
        confidence: float = 1.0,
    ) -> MemoryRecord:
        self.memory_counter += 1
        record = MemoryRecord(
            memory_id=f"m{self.memory_counter:06d}",
            tick=self.tick,
            text=str(text).strip(),
            tags=tuple(dict.fromkeys(str(x).lower() for x in tags if str(x).strip())),
            people=tuple(dict.fromkeys(str(x) for x in people if str(x).strip())),
            valence=_clamp_signed(valence),
            arousal=_clamp(arousal),
            importance=_clamp(importance),
            provenance=provenance,
            source=str(source),
            confidence=_clamp(confidence),
        )
        self.memories.append(record)
        if len(self.memories) > 2000:
            self.memories = self.memories[-2000:]
        return record

    def retrieve_memories(
        self,
        query: str,
        *,
        tags: Iterable[str] = (),
        people: Iterable[str] = (),
        top_k: int = 5,
    ) -> list[MemoryRecord]:
        query_tokens = _tokens(query)
        query_tags = {str(t).lower() for t in tags}
        query_people = {str(p).lower() for p in people}
        ranked: list[tuple[float, int, MemoryRecord]] = []
        current_valence = self.affect.get("joy", 0.0) - self.affect.get("fear", 0.0) - self.affect.get("anger", 0.0)
        for record in self.memories:
            words = _tokens(record.text)
            lexical = len(query_tokens & words) / max(1, len(query_tokens | words))
            tag_overlap = len(query_tags & set(record.tags)) / max(1, len(query_tags)) if query_tags else 0.0
            people_overlap = (
                len(query_people & {p.lower() for p in record.people}) / max(1, len(query_people))
                if query_people else 0.0
            )
            age = max(0, self.tick - record.tick)
            recency = 1.0 / (1.0 + age / 40.0)
            affect_match = 1.0 - min(1.0, abs(current_valence - record.valence) / 2.0)
            score = lexical * 0.32 + tag_overlap * 0.20 + people_overlap * 0.18 + recency * 0.10 + record.importance * 0.14 + affect_match * 0.06
            if lexical > 0 or tag_overlap > 0 or people_overlap > 0 or record.importance >= 0.85:
                ranked.append((score, record.tick, record))
        ranked.sort(key=lambda row: (row[0], row[1]), reverse=True)
        return [row[2] for row in ranked[:top_k]]

    def to_dict(self) -> dict:
        return {
            "subject_id": self.subject_id,
            "name": self.name,
            "tick": self.tick,
            "affect": self.affect,
            "needs": dict(self.needs),
            "relationships": {key: asdict(value) for key, value in self.relationships.items()},
            "memories": [memory.to_dict() for memory in self.memories],
            "beliefs": {key: value.to_dict() for key, value in self.beliefs.items()},
            "world_facts": self.world_facts,
            "commitments": {key: asdict(value) for key, value in self.commitments.items()},
            "residues": [asdict(value) for value in self.residues],
            "adaptive": self.adaptive.to_dict(),
            "pending_action": asdict(self.pending_action) if self.pending_action else None,
            "recent_actions": list(self.recent_actions),
            "self_narrative": list(self.self_narrative),
            "memory_counter": self.memory_counter,
            "commitment_counter": self.commitment_counter,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SubjectState":
        state = cls(subject_id=str(data["subject_id"]), name=str(data.get("name", "Duck")), tick=int(data.get("tick", 0)))
        state.affect = {str(k): float(v) for k, v in data.get("affect", state.affect).items()}
        state.needs = {str(k): float(v) for k, v in data.get("needs", state.needs).items()}
        state.relationships = {str(k): RelationshipState(**v) for k, v in data.get("relationships", {}).items()}
        state.memories = [MemoryRecord.from_dict(v) for v in data.get("memories", [])]
        state.beliefs = {str(k): BeliefRecord.from_dict(v) for k, v in data.get("beliefs", {}).items()}
        state.world_facts = {str(k): str(v) for k, v in data.get("world_facts", {}).items()}
        state.commitments = {str(k): CommitmentRecord(**v) for k, v in data.get("commitments", {}).items()}
        state.residues = [Residue(**v) for v in data.get("residues", [])]
        state.adaptive = AdaptiveSelfCore.from_dict(data.get("adaptive", {}))
        pending = data.get("pending_action")
        state.pending_action = PendingAction(**pending) if pending else None
        state.recent_actions = [str(x) for x in data.get("recent_actions", [])][-32:]
        state.self_narrative = [str(x) for x in data.get("self_narrative", [])][-32:]
        state.memory_counter = int(data.get("memory_counter", len(state.memories)))
        state.commitment_counter = int(data.get("commitment_counter", len(state.commitments)))
        return state


@dataclass(frozen=True)
class WorldEvent:
    kind: str
    source: str
    text: str
    tags: tuple[str, ...] = ()
    valence: float = 0.0
    intensity: float = 0.5
    world_facts: tuple[tuple[str, str], ...] = ()
    perceived: bool = True


@dataclass(frozen=True)
class ActionCandidate:
    name: str
    utility: float
    reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class LivingStep:
    tick: int
    subjective_moment: SubjectiveMoment
    inner_cognition: InnerCognition
    selected_action: str
    action_id: str
    recalled_memory_ids: tuple[str, ...]
    developer_trace: dict


class RuleEventInterpreter:
    """Fallback semantic interpreter for conversational text.

    A language-model interpreter can replace this later, but the organism remains
    runnable and testable without one.
    """

    POSITIVE = {"thanks", "thank", "love", "great", "good", "kind", "help", "happy", "glad", "proud"}
    NEGATIVE = {"hate", "angry", "hurt", "bad", "awful", "betray", "lied", "lie", "threat", "danger", "scared"}

    def interpret(self, text: str, *, source: str = "user") -> WorldEvent:
        words = _tokens(text)
        tags: list[str] = ["social", "conversation"]
        positive = len(words & self.POSITIVE)
        negative = len(words & self.NEGATIVE)
        valence = _clamp_signed((positive - negative) * 0.28)
        intensity = _clamp(0.30 + 0.12 * (positive + negative))
        lowered = text.lower()
        if words & {"hurt", "threat", "danger", "scared", "attack"}:
            tags.append("threat")
        if words & {"angry", "hate", "betray", "lied", "lie"}:
            tags.append("conflict")
        if words & {"thanks", "thank", "kind", "help", "love", "proud"}:
            tags.append("supportive")
        if any(word in words for word in {"promise", "promised"}) or "i will" in lowered or "i'll" in lowered:
            tags.append("commitment_language")
        if "sorry" in words or "apolog" in lowered:
            tags.append("repair")
        if "?" in text:
            tags.append("question")
        return WorldEvent("message", source, text.strip(), tuple(dict.fromkeys(tags)), valence, intensity)


class LivingDuck:
    """A persistent simulated individual rather than a prompt wrapper."""

    def __init__(
        self,
        state: SubjectState | None = None,
        *,
        firewall: SubjectAccessFirewall | None = None,
        cognition: InnerCognitionProvider | None = None,
    ) -> None:
        self.state = state or SubjectState.create()
        self.firewall = firewall or SubjectAccessFirewall()
        self.cognition = cognition or DeterministicInnerVoice()

    def set_world_fact(self, key: str, text: str, *, perceived: bool = False, source: str = "world") -> None:
        self.state.world_facts[str(key)] = str(text)
        if perceived:
            memory = self.state.add_memory(
                str(text),
                tags=("world_fact",),
                provenance=MemoryProvenance.WORLD_FACT,
                source=source,
                importance=0.55,
            )
            self.revise_belief(str(key), str(text), BeliefStance.TRUE, 0.90, evidence_refs=(memory.memory_id,), source="perception")

    def revise_belief(
        self,
        key: str,
        text: str,
        stance: BeliefStance | str,
        confidence: float,
        *,
        evidence_refs: Iterable[str] = (),
        source: str = "experience",
    ) -> BeliefRecord:
        record = BeliefRecord(
            key=str(key),
            text=str(text),
            stance=BeliefStance(stance),
            confidence=_clamp(confidence),
            evidence_refs=tuple(evidence_refs),
            source=str(source),
            updated_tick=self.state.tick,
        )
        self.state.beliefs[record.key] = record
        return record

    def create_commitment(self, actor: str, text: str, *, due_in: int | None = None, importance: float = 0.5) -> CommitmentRecord:
        self.state.commitment_counter += 1
        commitment = CommitmentRecord(
            commitment_id=f"c{self.state.commitment_counter:05d}",
            actor=str(actor),
            text=str(text),
            created_tick=self.state.tick,
            due_tick=(self.state.tick + int(due_in)) if due_in is not None else None,
            importance=_clamp(importance),
        )
        self.state.commitments[commitment.commitment_id] = commitment
        return commitment

    def resolve_commitment(self, commitment_id: str, *, kept: bool, outcome: str = "") -> CommitmentRecord:
        commitment = self.state.commitments[commitment_id]
        commitment.status = "kept" if kept else "broken"
        commitment.resolved_tick = self.state.tick
        commitment.outcome = str(outcome)
        relation = self.state.relationship(commitment.actor)
        if kept:
            relation.trust = _clamp(relation.trust + 0.10 * commitment.importance)
            relation.attachment = _clamp(relation.attachment + 0.04 * commitment.importance)
            self._add_residue("relief", 0.20 + 0.20 * commitment.importance, 0.84, "kept commitment")
        else:
            relation.trust = _clamp(relation.trust - 0.16 * commitment.importance)
            relation.guardedness = _clamp(relation.guardedness + 0.18 * commitment.importance)
            self._add_residue("fear", 0.24 + 0.28 * commitment.importance, 0.91, "broken commitment")
            self._add_residue("unease", 0.18 + 0.22 * commitment.importance, 0.90, "broken commitment")
        self.state.add_memory(
            outcome or (f"{commitment.actor} kept the commitment: {commitment.text}" if kept else f"{commitment.actor} broke the commitment: {commitment.text}"),
            tags=("commitment", "kept" if kept else "broken"),
            people=(commitment.actor,),
            valence=0.55 if kept else -0.75,
            arousal=0.45 if kept else 0.75,
            importance=max(0.65, commitment.importance),
            provenance=MemoryProvenance.OUTCOME,
            source=commitment.actor,
        )
        return commitment

    def resolve_outcome(
        self,
        action_id: str,
        *,
        success: float,
        valence: float,
        description: str,
        tags: Iterable[str] = (),
    ) -> None:
        pending = self.state.pending_action
        if pending is None or pending.action_id != action_id:
            raise ValueError("outcome does not match the current pending action")
        success = _clamp(success)
        valence = _clamp_signed(valence)
        reward = _clamp_signed((success - 0.5) * 1.4 + valence * 0.55)
        learning_tags = tuple(dict.fromkeys((*pending.tags, *(str(t).lower() for t in tags))))
        self._adaptive_learn(pending.name, learning_tags, reward)
        self.state.needs["competence"] = _clamp(self.state.needs.get("competence", 0.5) + 0.08 * reward)
        prediction_error = abs(valence - pending.predicted_valence)
        if prediction_error > 0.45:
            self._add_residue("unease", min(0.50, prediction_error), 0.86, "unexpected outcome")
        if valence < -0.20:
            self._add_residue("fear", abs(valence) * 0.35, 0.88, "bad outcome")
        elif valence > 0.25:
            self.state.affect["joy"] = _clamp(self.state.affect.get("joy", 0.0) + valence * 0.25)
        self.state.add_memory(
            description,
            tags=("outcome", pending.name, *learning_tags),
            valence=valence,
            arousal=min(1.0, abs(valence) + prediction_error * 0.5),
            importance=min(1.0, 0.45 + abs(valence) * 0.45 + prediction_error * 0.30),
            provenance=MemoryProvenance.OUTCOME,
            source="world",
        )
        self.state.pending_action = None

    def _adaptive_observe(self, text: str, tags: Iterable[str]) -> None:
        self.state.adaptive.observe(text, tags)

    def _adaptive_bias(self, action: str, tags: Iterable[str]) -> float:
        return self.state.adaptive.bias(action, tags)

    def _adaptive_learn(self, action: str, tags: Iterable[str], reward: float) -> None:
        self.state.adaptive.learn(action, tags, reward)

    def _select_candidate(
        self,
        event: WorldEvent,
        relation: RelationshipState,
        memories: list[MemoryRecord],
        candidates: list[ActionCandidate],
    ) -> ActionCandidate:
        """Select one current affordance without changing candidate scores.

        Historical runtimes inherit the original max-utility policy unchanged.
        Newer architectures may override this seam to validate a higher-level
        proposal while keeping the underlying affordance utilities intact.
        """
        return max(candidates, key=lambda candidate: (candidate.utility, candidate.name))

    def step(self, event: WorldEvent, *, allow_inner_speech: bool = True) -> LivingStep:
        self.state.tick += 1
        self._advance_homeostasis()
        self._apply_residues()
        relation = self.state.relationship(event.source)
        memories = self.state.retrieve_memories(event.text, tags=event.tags, people=(event.source,), top_k=5)
        prediction_error = self._appraise(event, relation, memories)
        self._adaptive_observe(event.text, event.tags)
        candidates = self._candidates(event, relation, memories)
        selected = self._select_candidate(event, relation, memories, candidates)

        for key, text in event.world_facts:
            self.state.world_facts[str(key)] = str(text)
            if event.perceived:
                belief_memory = self.state.add_memory(
                    str(text), tags=("world_fact", *event.tags), people=(event.source,),
                    provenance=MemoryProvenance.WORLD_FACT, source=event.source, importance=0.55,
                )
                self.revise_belief(str(key), str(text), BeliefStance.TRUE, 0.88, evidence_refs=(belief_memory.memory_id,), source="perception")

        suspicion = _clamp((1.0 - relation.trust) * 0.55 + relation.guardedness * 0.45)
        recognition = None
        if event.source not in {"self", "world", "system", ""}:
            confidence = _clamp(0.35 + relation.familiarity * 0.65)
            recognition = RecognitionSignal(event.source, confidence)

        hidden_causes: dict[str, str] = {}
        accessible_causes: set[str] = set()
        if self.state.affect.get("unease", 0.0) >= 0.25:
            if memories and memories[0].valence < -0.20:
                hidden_causes["unease"] = f"what happened before with {event.source}"
            elif "threat" in event.tags or "conflict" in event.tags:
                hidden_causes["unease"] = "what is happening right now"
                accessible_causes.add("unease")

        snapshot = MechanisticSnapshot(
            affect={
                "fear": self.state.affect.get("fear", 0.0),
                "loneliness": self.state.affect.get("loneliness", 0.0),
                "unease": self.state.affect.get("unease", 0.0),
            },
            relationship={
                "trust": relation.trust,
                "guardedness": relation.guardedness,
                "suspicion": suspicion,
            },
            prediction_error=prediction_error,
            recognition=recognition,
            action_tendency=selected.name,
            hidden_causes=hidden_causes,
            introspectively_accessible_causes=frozenset(accessible_causes),
        )
        base_moment = self.firewall.project(snapshot)
        moment = replace(
            base_moment,
            recollections=tuple(self._recollection_text(memory) for memory in memories[:3]),
            beliefs=tuple(self._belief_text(belief) for belief in self._relevant_beliefs(event.text)[:3]),
            concerns=self._subjective_concerns(event.source),
            temporal_context=self._temporal_context(),
            self_context=tuple(self.state.self_narrative[-3:]),
        )
        thought = self.cognition.generate(moment) if allow_inner_speech else InnerCognition(None)
        action_id = f"a-{self.state.tick}-{uuid.uuid4().hex[:8]}"
        self.state.pending_action = PendingAction(action_id, selected.name, tuple(event.tags), self.state.tick, event.valence)
        self.state.recent_actions.append(selected.name)
        self.state.recent_actions = self.state.recent_actions[-32:]

        if event.perceived and event.text.strip():
            importance = _clamp(0.35 + abs(event.valence) * 0.35 + event.intensity * 0.25 + prediction_error * 0.25)
            self.state.add_memory(
                event.text,
                tags=event.tags,
                people=(event.source,) if event.source else (),
                valence=event.valence,
                arousal=event.intensity,
                importance=importance,
                provenance=MemoryProvenance.FIRST_PERSON,
                source=event.source,
            )

        developer_trace = {
            "subject_id": self.state.subject_id,
            "tick": self.state.tick,
            "mechanistic_snapshot": asdict(snapshot),
            "retrieved_memory_ids": [memory.memory_id for memory in memories],
            "candidate_actions": [asdict(candidate) for candidate in candidates],
            "adaptive_latent": list(self.state.adaptive.latent),
            "subjective_projection": asdict(moment),
        }
        return LivingStep(
            tick=self.state.tick,
            subjective_moment=moment,
            inner_cognition=thought,
            selected_action=selected.name,
            action_id=action_id,
            recalled_memory_ids=tuple(memory.memory_id for memory in memories),
            developer_trace=developer_trace,
        )

    def heartbeat(self, *, allow_inner_speech: bool = True) -> LivingStep:
        event = WorldEvent(
            kind="endogenous",
            source="self",
            text="",
            tags=("idle", "time_passed"),
            valence=0.0,
            intensity=0.10,
            perceived=False,
        )
        return self.step(event, allow_inner_speech=allow_inner_speech)

    def _advance_homeostasis(self) -> None:
        for channel in list(self.state.affect):
            baseline = 0.04 if channel in {"fear", "unease", "anger"} else 0.10 if channel == "joy" else 0.18
            self.state.affect[channel] = _clamp(baseline + (self.state.affect[channel] - baseline) * 0.88)
        self._advance_energy()
        self.state.needs["affiliation"] = _clamp(self.state.needs.get("affiliation", 0.25) + 0.009)
        self.state.needs["curiosity"] = _clamp(self.state.needs.get("curiosity", 0.35) + 0.004)
        for relation in self.state.relationships.values():
            relation.uncertainty = _clamp(relation.uncertainty + 0.002)

    def _advance_energy(self) -> None:
        self.state.needs["energy"] = _clamp(self.state.needs.get("energy", 0.85) - 0.008)

    def _apply_residues(self) -> None:
        retained: list[Residue] = []
        for residue in self.state.residues:
            if residue.channel in self.state.affect:
                self.state.affect[residue.channel] = _clamp(self.state.affect[residue.channel] + residue.magnitude)
            residue.magnitude *= residue.decay
            if abs(residue.magnitude) >= 0.025:
                retained.append(residue)
        self.state.residues = retained

    def _add_residue(self, channel: str, magnitude: float, decay: float, source: str) -> None:
        self.state.residues.append(Residue(channel, _clamp(magnitude), _clamp(decay), source, self.state.tick))
        self.state.residues = self.state.residues[-64:]

    def _appraise(self, event: WorldEvent, relation: RelationshipState, memories: list[MemoryRecord]) -> float:
        intensity = _clamp(event.intensity)
        valence = _clamp_signed(event.valence)
        tags = set(event.tags)
        relation.familiarity = _clamp(relation.familiarity + (0.035 if event.source not in {"self", "world", "system"} else 0.0))
        relation.uncertainty = _clamp(relation.uncertainty - 0.025)
        if "social" in tags and event.source not in {"self", "world", "system"}:
            self.state.affect["loneliness"] = _clamp(self.state.affect.get("loneliness", 0.2) - 0.12)
            self.state.needs["affiliation"] = _clamp(self.state.needs.get("affiliation", 0.25) - 0.08)
        if valence > 0:
            self.state.affect["joy"] = _clamp(self.state.affect.get("joy", 0.1) + valence * 0.28 * intensity)
        if valence < 0:
            self.state.affect["unease"] = _clamp(self.state.affect.get("unease", 0.05) + abs(valence) * 0.24 * intensity)
        if "threat" in tags:
            self.state.affect["fear"] = _clamp(self.state.affect.get("fear", 0.05) + 0.42 * intensity)
            self.state.affect["unease"] = _clamp(self.state.affect.get("unease", 0.05) + 0.30 * intensity)
            self.state.needs["safety"] = _clamp(self.state.needs.get("safety", 0.85) - 0.18 * intensity)
        if "conflict" in tags:
            self.state.affect["anger"] = _clamp(self.state.affect.get("anger", 0.02) + 0.32 * intensity)
            relation.trust = _clamp(relation.trust - 0.12 * intensity)
            relation.guardedness = _clamp(relation.guardedness + 0.16 * intensity)
        if "supportive" in tags:
            relation.trust = _clamp(relation.trust + 0.08 * intensity)
            relation.attachment = _clamp(relation.attachment + 0.05 * intensity)
            relation.guardedness = _clamp(relation.guardedness - 0.05 * intensity)
            self.state.needs["safety"] = _clamp(self.state.needs.get("safety", 0.85) + 0.06 * intensity)
        if "repair" in tags:
            relation.guardedness = _clamp(relation.guardedness - 0.04 * intensity)
        if memories:
            negative = max(0.0, -min(memory.valence for memory in memories[:3]))
            if negative > 0.30:
                relation.guardedness = _clamp(relation.guardedness + 0.08 * negative)
                self.state.affect["unease"] = _clamp(self.state.affect.get("unease", 0.0) + 0.10 * negative)
        prediction_error = 0.0
        prior = self.state.memories[-1] if self.state.memories else None
        if prior is not None:
            prediction_error = _clamp(abs(prior.valence - valence) * 0.75)
        return prediction_error

    def _candidates(self, event: WorldEvent, relation: RelationshipState, memories: list[MemoryRecord]) -> list[ActionCandidate]:
        fear = self.state.affect.get("fear", 0.0)
        unease = self.state.affect.get("unease", 0.0)
        energy = self.state.needs.get("energy", 0.5)
        affiliation = self.state.needs.get("affiliation", 0.3)
        curiosity = self.state.needs.get("curiosity", 0.3)
        tags = event.tags
        candidates = [
            ActionCandidate("wait", 0.16 + self._adaptive_bias("wait", tags), ("baseline",)),
            ActionCandidate("respond", 0.28 + relation.familiarity * 0.12 + affiliation * 0.16 - fear * 0.08 + self._adaptive_bias("respond", tags), ("social",)),
            ActionCandidate("step_back", 0.08 + fear * 0.78 + unease * 0.24 + relation.guardedness * 0.18 + self._adaptive_bias("step_back", tags), ("safety",)),
            ActionCandidate("approach", 0.06 + relation.trust * 0.34 + affiliation * 0.26 - fear * 0.45 + self._adaptive_bias("approach", tags), ("affiliation",)),
            ActionCandidate("ask", 0.10 + curiosity * 0.38 + relation.uncertainty * 0.22 + self._adaptive_bias("ask", tags), ("uncertainty",)),
            ActionCandidate("explore", 0.08 + curiosity * 0.45 - fear * 0.28 + self._adaptive_bias("explore", tags), ("curiosity",)),
            ActionCandidate("rest", 0.06 + (1.0 - energy) * 0.68 + self._adaptive_bias("rest", tags), ("energy",)),
        ]
        if "repair" in event.tags or self.state.affect.get("anger", 0.0) > 0.45:
            candidates.append(ActionCandidate("repair", 0.18 + relation.attachment * 0.30 + relation.trust * 0.18 + self._adaptive_bias("repair", tags), ("relationship",)))
        if event.kind == "endogenous":
            candidates = [candidate for candidate in candidates if candidate.name not in {"respond", "approach"}]
            if affiliation > 0.62:
                candidates.append(ActionCandidate("seek_connection", 0.22 + affiliation * 0.58 + self._adaptive_bias("seek_connection", tags), ("affiliation_pressure",)))
        return candidates

    @staticmethod
    def _recollection_text(memory: MemoryRecord) -> str:
        if memory.provenance is MemoryProvenance.TESTIMONY:
            return f"I remember {memory.source or 'someone'} telling me that {memory.text}"
        if memory.provenance is MemoryProvenance.WORLD_FACT:
            return f"I know that {memory.text}"
        if memory.provenance is MemoryProvenance.SELF_REFLECTION:
            return f"I've thought before that {memory.text}"
        if memory.provenance is MemoryProvenance.OUTCOME:
            return f"I remember that {memory.text}"
        return f"I remember {memory.text}"

    @staticmethod
    def _belief_text(belief: BeliefRecord) -> str:
        if belief.stance is BeliefStance.TRUE and belief.confidence >= 0.78:
            return f"I believe {belief.text}"
        if belief.stance is BeliefStance.FALSE and belief.confidence >= 0.78:
            return f"I believe it isn't true that {belief.text}"
        return f"I'm not completely sure whether {belief.text}"

    def _relevant_beliefs(self, query: str) -> list[BeliefRecord]:
        query_tokens = _tokens(query)
        rows: list[tuple[int, int, BeliefRecord]] = []
        for belief in self.state.beliefs.values():
            overlap = len(query_tokens & _tokens(belief.text))
            if overlap or belief.confidence >= 0.85:
                rows.append((overlap, belief.updated_tick, belief))
        rows.sort(key=lambda row: (row[0], row[1]), reverse=True)
        return [row[2] for row in rows]

    def _subjective_concerns(self, actor: str) -> tuple[str, ...]:
        concerns: list[str] = []
        open_for_actor = [c for c in self.state.commitments.values() if c.actor == actor and c.status == "open"]
        broken_for_actor = [c for c in self.state.commitments.values() if c.actor == actor and c.status == "broken"]
        if broken_for_actor:
            concerns.append("I'm still wary because they let me down before.")
        if open_for_actor:
            concerns.append("I'm still waiting to see whether they follow through.")
        if self.state.needs.get("energy", 1.0) < 0.35:
            concerns.append("I'm tired.")
        if self.state.needs.get("affiliation", 0.0) > 0.65:
            concerns.append("I want some connection.")
        if self.state.needs.get("curiosity", 0.0) > 0.72:
            concerns.append("I keep wanting to find out more.")
        return tuple(concerns)

    def _temporal_context(self) -> tuple[str, ...]:
        context: list[str] = []
        if self.state.residues:
            context.append("What happened recently is still affecting me.")
        overdue = [c for c in self.state.commitments.values() if c.status == "open" and c.due_tick is not None and c.due_tick <= self.state.tick]
        if overdue:
            context.append("Something I was waiting for is overdue.")
        return tuple(context)
