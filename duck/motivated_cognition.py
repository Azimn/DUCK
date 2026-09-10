"""Persistent motivated-cognition substrate for MicroPsiDUCK v0.10.

Persistent: motive identities, learned associative links, strategy familiarity.
Transient: activation fields and global cognitive modulation.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Iterable, Mapping

from .living import MemoryProvenance, MemoryRecord, SubjectState, WorldEvent, _clamp

from .strategy_v010 import CognitiveRegime, contextual_reliability

COGNITIVE_STATE_SCHEMA = "micropsi-duck.cognition.v1"
MAX_MOTIVES = 24
MAX_EDGES = 2048
MAX_ACTIVE_MOTIVES = 3

_CONTROL_PREFIXES = ("pc_", "pl_", "concern_id:", "preferred_action:", "opportunity_")
_CONTROL_TAGS = {
    "idle", "time_passed", "opportunity", "prospective", "opportunity_active",
    "opportunity_acted", "plan_step", "planning",
}
COHERENCE_DISRUPTION_TAGS = frozenset({
    "contradiction", "inconsistency", "expectation_violation", "prediction_error",
})
_STATUS_PRIORITY = {
    "dominant": 5, "active": 4, "latent": 3, "inhibited": 2,
    "satisfied": 1, "impossible": 0,
}

MOTIVE_ACTION_PREFERENCES: dict[str, tuple[str, ...]] = {
    "safety": ("step_back", "wait", "ask"),
    "energy": ("rest", "wait"),
    "affiliation": ("seek_connection", "respond", "approach", "repair"),
    "curiosity": ("explore", "ask"),
    "competence": ("ask", "explore", "wait"),
    "coherence": ("ask", "wait", "repair"),
    "autonomy": ("explore", "ask"),
    "repair": ("repair", "ask", "respond"),
    "commitment": ("ask", "respond", "wait"),
}
MOTIVE_PROSE: dict[str, str] = {
    "safety": "I want to get somewhere that feels safer.",
    "energy": "I need to slow down and recover.",
    "affiliation": "I don't want to stay disconnected.",
    "curiosity": "I want to understand this.",
    "competence": "I want to find something I know how to handle.",
    "coherence": "I want this to make sense.",
    "autonomy": "I want some control over what happens next.",
    "repair": "I want to make this right.",
    "commitment": "I don't want to lose track of what still needs following through.",
}


def _semantic_tag(tag: str) -> bool:
    value = str(tag).lower()
    if value in _CONTROL_TAGS:
        return False
    return not any(value.startswith(prefix) for prefix in _CONTROL_PREFIXES)


def _ref(kind: str, value: str) -> str:
    return f"{kind}:{str(value).strip().lower()}"


@dataclass
class MotiveRecord:
    motive_id: str
    theme: str
    source: str
    target: str
    strength: float
    urgency: float
    persistence: float
    inhibition: float
    status: str
    created_tick: int
    updated_tick: int
    last_dominant_tick: int | None = None
    links: tuple[str, ...] = ()

    def normalize(self) -> None:
        self.strength = _clamp(self.strength)
        self.urgency = _clamp(self.urgency)
        self.persistence = _clamp(self.persistence)
        self.inhibition = _clamp(self.inhibition)
        self.links = tuple(dict.fromkeys(str(x) for x in self.links if str(x)))

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Mapping) -> "MotiveRecord":
        row = cls(
            motive_id=str(data["motive_id"]),
            theme=str(data["theme"]),
            source=str(data.get("source", data.get("theme", "internal"))),
            target=str(data.get("target", "")),
            strength=float(data.get("strength", 0.0)),
            urgency=float(data.get("urgency", 0.0)),
            persistence=float(data.get("persistence", 0.0)),
            inhibition=float(data.get("inhibition", 0.0)),
            status=str(data.get("status", "latent")),
            created_tick=int(data.get("created_tick", 0)),
            updated_tick=int(data.get("updated_tick", 0)),
            last_dominant_tick=(
                int(data["last_dominant_tick"]) if data.get("last_dominant_tick") is not None else None
            ),
            links=tuple(str(x) for x in data.get("links", ())),
        )
        row.normalize()
        return row


@dataclass
class AssociativeEdge:
    source: str
    target: str
    relation: str
    weight: float
    count: int
    updated_tick: int

    def normalize(self) -> None:
        self.weight = max(0.02, min(1.0, float(self.weight)))
        self.count = max(1, int(self.count))

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Mapping) -> "AssociativeEdge":
        row = cls(
            source=str(data["source"]),
            target=str(data["target"]),
            relation=str(data.get("relation", "associated")),
            weight=float(data.get("weight", 0.2)),
            count=int(data.get("count", 1)),
            updated_tick=int(data.get("updated_tick", 0)),
        )
        row.normalize()
        return row


@dataclass(frozen=True)
class ActivationField:
    scores: dict[str, float]
    propagation_depth: int
    expanded_nodes: int

    def top(self, prefix: str | None = None, limit: int = 8) -> tuple[str, ...]:
        rows = [
            (score, node)
            for node, score in self.scores.items()
            if prefix is None or node.startswith(prefix)
        ]
        rows.sort(key=lambda row: (row[0], row[1]), reverse=True)
        return tuple(node for _, node in rows[:max(0, int(limit))])


@dataclass
class AssociativeGraph:
    edges: dict[str, AssociativeEdge] = field(default_factory=dict)

    @staticmethod
    def _key(source: str, target: str, relation: str) -> str:
        return f"{source}|{relation}|{target}"

    def connect(
        self, source: str, target: str, relation: str, weight: float, tick: int, *,
        learn: bool = True,
    ) -> None:
        if not source or not target or source == target:
            return
        key = self._key(source, target, relation)
        edge = self.edges.get(key)
        if edge is None:
            self.edges[key] = AssociativeEdge(
                source=source, target=target, relation=str(relation),
                weight=max(0.02, min(1.0, float(weight))), count=1, updated_tick=int(tick),
            )
        elif learn:
            edge.count += 1
            edge.weight = min(1.0, edge.weight + 0.035 * (1.0 - edge.weight))
            edge.updated_tick = int(tick)
        self._bound()

    def connect_both(
        self, left: str, right: str, relation: str, weight: float, tick: int, *,
        learn: bool = True,
    ) -> None:
        self.connect(left, right, relation, weight, tick, learn=learn)
        self.connect(right, left, relation, weight, tick, learn=learn)

    def _bound(self) -> None:
        if len(self.edges) <= MAX_EDGES:
            return
        ordered = sorted(
            self.edges.items(),
            key=lambda row: (row[1].weight, row[1].count, row[1].updated_tick),
            reverse=True,
        )
        self.edges = dict(ordered[:MAX_EDGES])

    def remove_nodes(self, nodes: set[str]) -> None:
        if not nodes:
            return
        self.edges = {
            key: edge for key, edge in self.edges.items()
            if edge.source not in nodes and edge.target not in nodes
        }

    def spread(
        self, seeds: Mapping[str, float], *, depth: int, fanout: int,
        decay: float = 0.68, max_active: int = 64,
    ) -> ActivationField:
        # Sum distinct cue contributions, while retaining only the strongest path
        # from each cue. A loop or duplicate relation is not another experience.
        depth = max(0, min(5, int(depth)))
        fanout = max(1, min(10, int(fanout)))
        max_active = max(0, min(64, int(max_active)))
        decay = max(0.0, min(1.0, float(decay)))
        def bounded(rows):
            return dict(sorted(rows.items(), key=lambda row: (-row[1], row[0]))[:max_active])

        seeds = bounded({
            str(node): max(0.0, min(1.0, float(value)))
            for node, value in seeds.items() if float(value) > 0
        })
        adjacency: dict[str, dict[str, float]] = {}
        for edge in self.edges.values():
            targets = adjacency.setdefault(edge.source, {})
            targets[edge.target] = max(targets.get(edge.target, 0.0), edge.weight)
        neighbors = {
            source: sorted(targets.items(), key=lambda row: (-row[1], row[0]))[:fanout]
            for source, targets in adjacency.items()
        }
        scores: dict[str, float] = {}
        expanded = 0
        for seed, activation in seeds.items():
            strongest = {seed: activation}
            frontier = dict(strongest)
            for _ in range(depth):
                next_frontier: dict[str, float] = {}
                for source, value in sorted(frontier.items()):
                    expanded += 1
                    for target, weight in neighbors.get(source, ()):
                        propagated = value * weight * decay
                        if propagated < 0.035 or propagated <= strongest.get(target, 0.0):
                            continue
                        next_frontier[target] = max(next_frontier.get(target, 0.0), propagated)
                if not next_frontier:
                    break
                strongest = bounded({**strongest, **next_frontier})
                frontier = {node: value for node, value in next_frontier.items() if node in strongest}
            for node, value in strongest.items():
                scores[node] = min(1.0, scores.get(node, 0.0) + value)
        return ActivationField(scores=bounded(scores), propagation_depth=depth, expanded_nodes=expanded)

    def to_dict(self) -> dict:
        return {"edges": [edge.to_dict() for edge in self.edges.values()]}

    @classmethod
    def from_dict(cls, data: Mapping) -> "AssociativeGraph":
        graph = cls()
        for payload in data.get("edges", ()):
            edge = AssociativeEdge.from_dict(payload)
            graph.edges[graph._key(edge.source, edge.target, edge.relation)] = edge
        graph._bound()
        return graph


@dataclass
class MotivatedCognitionState:
    schema_version: str = COGNITIVE_STATE_SCHEMA
    motive_counter: int = 0
    motives: dict[str, MotiveRecord] = field(default_factory=dict)
    graph: AssociativeGraph = field(default_factory=AssociativeGraph)
    indexed_memory_ids: set[str] = field(default_factory=set)
    last_dominant_motive_id: str | None = None
    strategy_success: dict[str, float] = field(default_factory=dict)
    strategy_contexts: dict[str, dict] = field(default_factory=dict)
    pending_strategy_context: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "motive_counter": self.motive_counter,
            "motives": {key: value.to_dict() for key, value in self.motives.items()},
            "graph": self.graph.to_dict(),
            "indexed_memory_ids": sorted(self.indexed_memory_ids),
            "last_dominant_motive_id": self.last_dominant_motive_id,
            "strategy_success": {str(k): float(v) for k, v in self.strategy_success.items()},
            "strategy_contexts": {k: dict(v) for k, v in self.strategy_contexts.items()},
            "pending_strategy_context": dict(self.pending_strategy_context),
        }

    @classmethod
    def from_dict(cls, data: Mapping) -> "MotivatedCognitionState":
        version = str(data.get("schema_version", COGNITIVE_STATE_SCHEMA))
        if version != COGNITIVE_STATE_SCHEMA:
            raise ValueError(f"unsupported motivated cognition schema: {version}")
        state = cls(
            schema_version=version,
            motive_counter=int(data.get("motive_counter", 0)),
            motives={
                str(key): MotiveRecord.from_dict(value)
                for key, value in data.get("motives", {}).items()
            },
            graph=AssociativeGraph.from_dict(data.get("graph", {})),
            indexed_memory_ids={str(x) for x in data.get("indexed_memory_ids", ())},
            last_dominant_motive_id=(
                str(data["last_dominant_motive_id"])
                if data.get("last_dominant_motive_id") is not None else None
            ),
            strategy_success={
                str(key): max(-1.0, min(1.0, float(value)))
                for key, value in list(data.get("strategy_success", {}).items())[-64:]
            },
        )
        for key, value in list(data.get("strategy_contexts", {}).items())[-320:]:
            action, regime = key.rsplit("|", 1)
            CognitiveRegime(regime)
            state.strategy_contexts[key] = {
                "value": max(-1.0, min(1.0, float(value["value"]))),
                "evidence": max(0, min(10000, int(value["evidence"]))),
            }
        pending = data.get("pending_strategy_context", {})
        if pending:
            state.pending_strategy_context = {
                "action_id": str(pending["action_id"]),
                "regime": CognitiveRegime(pending["regime"]).value,
            }
        _compact_motive_state(
            state,
            tick=max((m.updated_tick for m in state.motives.values()), default=0),
            retire_stale=False,
        )
        return state


def _survivor_key(motive: MotiveRecord) -> tuple:
    return (
        _STATUS_PRIORITY.get(motive.status, 0),
        motive.persistence,
        motive.strength,
        motive.urgency,
        motive.updated_tick,
        -motive.created_tick,
    )


def _merge_motive(survivor: MotiveRecord, other: MotiveRecord) -> None:
    survivor.strength = max(survivor.strength, other.strength)
    survivor.urgency = max(survivor.urgency, other.urgency)
    survivor.persistence = max(survivor.persistence, other.persistence)
    survivor.inhibition = min(survivor.inhibition, other.inhibition)
    survivor.created_tick = min(survivor.created_tick, other.created_tick)
    survivor.updated_tick = max(survivor.updated_tick, other.updated_tick)
    if other.last_dominant_tick is not None:
        survivor.last_dominant_tick = max(
            survivor.last_dominant_tick or other.last_dominant_tick,
            other.last_dominant_tick,
        )
    if _STATUS_PRIORITY.get(other.status, 0) > _STATUS_PRIORITY.get(survivor.status, 0):
        survivor.status = other.status
    if other.source.startswith("appraisal:") and not survivor.source.startswith("appraisal:"):
        survivor.source = other.source
    survivor.links = tuple(dict.fromkeys((*survivor.links, *other.links)))
    survivor.normalize()


def _compact_motive_state(
    state: MotivatedCognitionState,
    *,
    tick: int,
    retire_stale: bool = True,
) -> None:
    """Canonicalize motive identity and retire stale records.

    Motive identity is `(theme, target)`. Repeated pressure reactivates the same
    persistent object. Compaction is intentionally conservative for untargeted
    homeostatic motives and more aggressive for resolved contextual motives.
    """
    grouped: dict[tuple[str, str], list[MotiveRecord]] = {}
    for motive in state.motives.values():
        grouped.setdefault((motive.theme, motive.target), []).append(motive)

    retire_ids: set[str] = set()
    dominant_remap: dict[str, str] = {}
    for rows in grouped.values():
        if len(rows) <= 1:
            continue
        rows.sort(key=_survivor_key, reverse=True)
        survivor = rows[0]
        for duplicate in rows[1:]:
            _merge_motive(survivor, duplicate)
            dominant_remap[duplicate.motive_id] = survivor.motive_id
            retire_ids.add(duplicate.motive_id)

    if state.last_dominant_motive_id in dominant_remap:
        state.last_dominant_motive_id = dominant_remap[state.last_dominant_motive_id]

    if retire_stale:
        protected = {
            motive_id for motive_id, motive in state.motives.items()
            if motive.status in {"dominant", "active"}
        }
        for motive_id, motive in state.motives.items():
            if motive_id in protected or motive_id in retire_ids:
                continue
            age = max(0, int(tick) - motive.updated_tick)
            targeted_resolved = (
                bool(motive.target)
                and motive.status in {"satisfied", "impossible"}
                and age >= 24
            )
            targeted_weak = (
                bool(motive.target)
                and motive.status in {"latent", "inhibited"}
                and motive.strength < 0.22
                and motive.persistence < 0.20
                and age >= 48
            )
            if targeted_resolved or targeted_weak:
                retire_ids.add(motive_id)

    survivors = [
        motive for motive_id, motive in state.motives.items()
        if motive_id not in retire_ids
    ]
    if len(survivors) > MAX_MOTIVES:
        survivors.sort(
            key=lambda m: (
                m.status == "dominant",
                m.status == "active",
                not bool(m.target),
                _STATUS_PRIORITY.get(m.status, 0),
                m.persistence,
                m.strength,
                m.urgency,
                m.updated_tick,
            ),
            reverse=True,
        )
        keep_ids = {m.motive_id for m in survivors[:MAX_MOTIVES]}
        retire_ids.update(m.motive_id for m in survivors[MAX_MOTIVES:] if m.motive_id not in keep_ids)

    if retire_ids:
        state.graph.remove_nodes({_ref("motive", motive_id) for motive_id in retire_ids})
        for motive_id in retire_ids:
            state.motives.pop(motive_id, None)
        if state.last_dominant_motive_id in retire_ids:
            state.last_dominant_motive_id = None


@dataclass(frozen=True)
class CognitiveModulation:
    mobilization: float
    resolution: float
    switching_threshold: float
    competitor_inhibition: float
    exploration: float
    retrieval_budget: int
    propagation_depth: int
    propagation_fanout: int
    planning_depth: int
    route_branching: int
    familiar_strategy_bias: float
    interruption_sensitivity: float

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class CognitiveCycle:
    tick: int
    dominant_motive_id: str | None
    active_motive_ids: tuple[str, ...]
    modulation: CognitiveModulation
    activation: ActivationField
    activated_memory_ids: tuple[str, ...]

    def to_developer_dict(self) -> dict:
        return {
            "tick": self.tick,
            "dominant_motive_id": self.dominant_motive_id,
            "active_motive_ids": list(self.active_motive_ids),
            "modulation": self.modulation.to_dict(),
            "activation": {
                "propagation_depth": self.activation.propagation_depth,
                "expanded_nodes": self.activation.expanded_nodes,
                "active_node_count": len(self.activation.scores),
            },
            "activated_memory_ids": list(self.activated_memory_ids),
        }


class MotivatedCognitionEngine:
    """Persistent motive/association controller with transient modulation."""

    def __init__(self, state: MotivatedCognitionState | None = None) -> None:
        self.state = state or MotivatedCognitionState()
        _compact_motive_state(
            self.state,
            tick=max((m.updated_tick for m in self.state.motives.values()), default=0),
            retire_stale=False,
        )

    def _pressure_map(
        self, subject: SubjectState, event: WorldEvent
    ) -> dict[tuple[str, str], tuple[str, float]]:
        tags = {str(tag).lower() for tag in event.tags}
        fear = _clamp(subject.affect.get("fear", 0.0))
        loneliness = _clamp(subject.affect.get("loneliness", 0.0))
        unease = _clamp(subject.affect.get("unease", 0.0))
        energy = _clamp(subject.needs.get("energy", 0.85))
        affiliation = _clamp(subject.needs.get("affiliation", 0.25))
        curiosity = _clamp(subject.needs.get("curiosity", 0.35))
        safety = _clamp(subject.needs.get("safety", 0.85))
        competence = _clamp(subject.needs.get("competence", 0.55))
        coherence = _clamp(subject.needs.get("coherence", 0.70))
        autonomy = _clamp(subject.needs.get("autonomy", 0.65))
        threat_event = _clamp(event.intensity if "threat" in tags else 0.0)
        obstacle = _clamp(event.intensity if tags & {"obstacle", "blocked"} else 0.0)
        novel = _clamp(event.intensity if tags & {"novel", "mystery", "unknown"} else 0.0)
        coherence_disruption = _clamp(
            event.intensity if tags & COHERENCE_DISRUPTION_TAGS else 0.0
        )
        baseline_coherence_pressure = max(1.0 - coherence, unease * 0.45)
        coherence_pressure = max(baseline_coherence_pressure, coherence_disruption * 0.88)
        coherence_source = (
            "appraisal:inconsistency"
            if coherence_disruption * 0.88 > baseline_coherence_pressure
            else "need:coherence"
        )
        rows: dict[tuple[str, str], tuple[str, float]] = {
            ("safety", ""): ("need:safety", max(1.0 - safety, fear * 0.9, threat_event)),
            ("energy", ""): ("need:energy", 1.0 - energy),
            ("affiliation", ""): ("need:affiliation", max(affiliation, loneliness * 0.8)),
            ("curiosity", ""): ("need:curiosity", max(curiosity, novel * 0.75)),
            ("competence", ""): ("need:competence", 1.0 - competence),
            ("coherence", ""): (coherence_source, coherence_pressure),
            ("autonomy", ""): ("need:autonomy", max(1.0 - autonomy, obstacle * 0.75)),
        }
        if "conflict" in tags or "repair_needed" in tags:
            target = event.source if event.source not in {"", "self", "world", "system"} else ""
            relation = subject.relationship(target) if target else None
            relationship_value = 0.50
            if relation is not None:
                relationship_value = max(relation.attachment, relation.trust * 0.8)
            rows[("repair", target)] = (
                "relationship", _clamp(0.42 + 0.45 * relationship_value)
            )
        due_pressure = 0.0
        due_actor = ""
        for item in subject.commitments.values():
            if item.status != "open":
                continue
            if item.due_tick is None:
                pressure = 0.22 * item.importance
            else:
                distance = item.due_tick - (subject.tick + 1)
                pressure = item.importance * (
                    0.35 if distance > 8 else 0.55 if distance > 2 else 0.82
                )
            if pressure > due_pressure:
                due_pressure = pressure
                due_actor = item.actor
        if due_pressure >= 0.25:
            rows[("commitment", due_actor)] = ("commitment", _clamp(due_pressure))
        return rows

    def _existing_motive(self, theme: str, target: str) -> MotiveRecord | None:
        matches = [
            motive for motive in self.state.motives.values()
            if motive.theme == theme and motive.target == target
        ]
        if not matches:
            return None
        return max(matches, key=_survivor_key)

    def _ensure_motive(
        self, theme: str, source: str, target: str, pressure: float, tick: int
    ) -> MotiveRecord | None:
        motive = self._existing_motive(theme, target)
        if motive is None and pressure < 0.34:
            return None
        if motive is None:
            self.state.motive_counter += 1
            motive = MotiveRecord(
                motive_id=f"mot{self.state.motive_counter:05d}",
                theme=theme,
                source=source,
                target=target,
                strength=_clamp(pressure),
                urgency=_clamp(pressure * 0.85),
                persistence=0.18,
                inhibition=0.0,
                status="latent",
                created_tick=tick,
                updated_tick=tick,
                links=tuple(
                    x for x in (
                        _ref("concept", theme),
                        _ref("person", target) if target else "",
                    ) if x
                ),
            )
            self.state.motives[motive.motive_id] = motive
        else:
            if motive.status == "impossible":
                if pressure < 0.34:
                    return motive
                motive.status = "latent"
                motive.inhibition *= 0.35
            motive.inhibition *= 0.72
            motive.strength = _clamp(motive.strength * 0.70 + pressure * 0.30)
            motive.urgency = _clamp(motive.urgency * 0.72 + pressure * 0.28)
            if pressure >= 0.24:
                motive.persistence = _clamp(motive.persistence + 0.045)
            else:
                motive.persistence = _clamp(motive.persistence - 0.035)
            if source.startswith("appraisal:") or motive.source.startswith("need:"):
                motive.source = source
            motive.updated_tick = tick
        if pressure <= 0.16 and motive.strength <= 0.28:
            motive.status = "satisfied"
        elif motive.status == "satisfied" and pressure >= 0.34:
            motive.status = "latent"
        motive.normalize()
        return motive

    def _motive_score(self, motive: MotiveRecord, event: WorldEvent) -> float:
        score = (
            0.50 * motive.strength
            + 0.24 * motive.urgency
            + 0.20 * motive.persistence
            - 0.42 * motive.inhibition
        )
        tags = {str(tag).lower() for tag in event.tags}
        if motive.theme == "safety" and "threat" in tags:
            score += 0.34
        if motive.theme == "curiosity" and tags & {"novel", "mystery", "unknown"}:
            score += 0.12
        if motive.theme == "autonomy" and tags & {"obstacle", "blocked"}:
            score += 0.14
        if motive.theme == "repair" and tags & {"conflict", "repair_needed"}:
            score += 0.18
        if motive.theme == "coherence" and tags & COHERENCE_DISRUPTION_TAGS:
            score += 0.20
        return score

    def _select_motives(
        self, subject: SubjectState, event: WorldEvent, tick: int
    ) -> tuple[str | None, tuple[str, ...]]:
        candidates = [
            motive for motive in self.state.motives.values()
            if motive.status not in {"satisfied", "impossible"}
            and (motive.strength >= 0.22 or motive.persistence >= 0.24)
        ]
        if not candidates:
            self.state.last_dominant_motive_id = None
            return None, ()
        ranked = sorted(
            ((self._motive_score(motive, event), motive) for motive in candidates),
            key=lambda row: (row[0], row[1].urgency, row[1].created_tick),
            reverse=True,
        )
        top_score, top = ranked[0]
        previous = self.state.motives.get(self.state.last_dominant_motive_id or "")
        preliminary = self.derive_modulation(subject, event, previous)
        switching_margin = 0.035 + 0.20 * preliminary.switching_threshold
        if previous is not None and previous.status not in {"satisfied", "impossible"}:
            previous_score = self._motive_score(previous, event)
            if previous_score + switching_margin >= top_score:
                top = previous

        active = tuple(m.motive_id for _, m in ranked[:MAX_ACTIVE_MOTIVES])
        if top.motive_id not in active:
            active = (top.motive_id, *active[:MAX_ACTIVE_MOTIVES - 1])
        for _, motive in ranked:
            if motive.motive_id == top.motive_id:
                motive.status = "dominant"
                motive.last_dominant_tick = tick
                motive.inhibition *= 0.55
            elif motive.motive_id in active:
                motive.status = "active"
                motive.inhibition = _clamp(
                    motive.inhibition + 0.03 + 0.10 * preliminary.competitor_inhibition
                )
            else:
                motive.status = "inhibited"
                motive.inhibition = _clamp(
                    motive.inhibition + 0.02 + 0.08 * preliminary.competitor_inhibition
                )
        self.state.last_dominant_motive_id = top.motive_id
        return top.motive_id, active

    def derive_modulation(
        self, subject: SubjectState, event: WorldEvent, dominant_motive: MotiveRecord | None
    ) -> CognitiveModulation:
        tags = {str(tag).lower() for tag in event.tags}
        threat_signal = max(
            _clamp(subject.affect.get("fear", 0.0)),
            1.0 - _clamp(subject.needs.get("safety", 0.85)),
            _clamp(event.intensity if "threat" in tags else 0.0),
        )
        fatigue = 1.0 - _clamp(subject.needs.get("energy", 0.85))
        curiosity = _clamp(subject.needs.get("curiosity", 0.35))
        competence_pressure = 1.0 - _clamp(subject.needs.get("competence", 0.55))
        motive_urgency = dominant_motive.urgency if dominant_motive is not None else 0.0

        mobilization = _clamp(
            0.24 + 0.58 * threat_signal + 0.22 * event.intensity
            + 0.14 * motive_urgency - 0.18 * fatigue
        )
        resolution = _clamp(
            0.70 + 0.22 * curiosity - 0.52 * threat_signal - 0.46 * fatigue
        )
        switching_threshold = _clamp(0.16 + 0.46 * threat_signal + 0.18 * fatigue)
        competitor_inhibition = _clamp(0.10 + 0.62 * threat_signal)
        exploration = _clamp(
            0.24 + 0.66 * curiosity - 0.72 * threat_signal - 0.34 * fatigue
        )
        familiar_strategy_bias = _clamp(
            0.18 + 0.56 * competence_pressure + 0.34 * threat_signal
        )
        interruption = _clamp(0.18 + 0.72 * threat_signal + 0.12 * fatigue)
        retrieval_budget = max(2, min(7, 2 + round(resolution * 5)))
        propagation_depth = max(1, min(4, 1 + round(resolution * 3)))
        fanout = max(2, min(8, 2 + round((resolution + exploration) * 3)))
        planning_depth = max(1, min(4, 1 + round(resolution * 3)))
        route_branching = 1 + int(exploration >= 0.34) + int(resolution >= 0.66)
        return CognitiveModulation(
            mobilization=mobilization,
            resolution=resolution,
            switching_threshold=switching_threshold,
            competitor_inhibition=competitor_inhibition,
            exploration=exploration,
            retrieval_budget=retrieval_budget,
            propagation_depth=propagation_depth,
            propagation_fanout=fanout,
            planning_depth=planning_depth,
            route_branching=max(1, min(3, route_branching)),
            familiar_strategy_bias=familiar_strategy_bias,
            interruption_sensitivity=interruption,
        )

    def _index_memory(self, subject: SubjectState, memory: MemoryRecord) -> None:
        if memory.memory_id in self.state.indexed_memory_ids:
            return
        tick = subject.tick
        graph = self.state.graph
        memory_ref = _ref("memory", memory.memory_id)
        semantic_tags = [str(tag).lower() for tag in memory.tags if _semantic_tag(tag)][:12]
        for tag in semantic_tags:
            graph.connect_both(memory_ref, _ref("concept", tag), "tag", 0.58, tick, learn=False)
        for person in memory.people[:6]:
            graph.connect_both(memory_ref, _ref("person", person), "person", 0.72, tick, learn=False)
        if memory.source and memory.source not in {"self", "world", "system"}:
            graph.connect_both(
                memory_ref, _ref("person", memory.source), "source", 0.64, tick, learn=False
            )
        if memory.provenance is MemoryProvenance.OUTCOME:
            for actions in MOTIVE_ACTION_PREFERENCES.values():
                for name in actions:
                    if name in semantic_tags:
                        graph.connect_both(
                            memory_ref, _ref("action", name), "outcome_action",
                            0.62, tick, learn=False,
                        )
        previous = None
        if len(subject.memories) >= 2:
            try:
                index = next(
                    i for i, row in enumerate(subject.memories)
                    if row.memory_id == memory.memory_id
                )
                if index > 0:
                    previous = subject.memories[index - 1]
            except StopIteration:
                pass
        if previous is not None:
            graph.connect_both(
                memory_ref, _ref("memory", previous.memory_id), "temporal",
                0.34, tick, learn=False,
            )
        self.state.indexed_memory_ids.add(memory.memory_id)

    def index_canonical_state(self, subject: SubjectState) -> None:
        for memory in subject.memories:
            self._index_memory(subject, memory)
        for key in subject.beliefs:
            self.state.graph.connect_both(
                _ref("belief", key), _ref("concept", key), "belief_topic",
                0.46, subject.tick, learn=False,
            )
        for person in subject.relationships:
            self.state.graph.connect(
                _ref("person", person), _ref("concept", "social"), "social",
                0.28, subject.tick, learn=False,
            )
        for motive in self.state.motives.values():
            motive_ref = _ref("motive", motive.motive_id)
            self.state.graph.connect_both(
                motive_ref, _ref("concept", motive.theme), "motive_theme",
                0.74, subject.tick, learn=False,
            )
            if motive.target:
                self.state.graph.connect_both(
                    motive_ref, _ref("person", motive.target), "motive_target",
                    0.66, subject.tick, learn=False,
                )

    def prepare_cycle(self, subject: SubjectState, event: WorldEvent) -> CognitiveCycle:
        tick = subject.tick + 1
        _compact_motive_state(self.state, tick=tick)
        for (theme, target), (source, pressure) in self._pressure_map(subject, event).items():
            self._ensure_motive(theme, source, target, pressure, tick)
        _compact_motive_state(self.state, tick=tick)

        dominant_id, active_ids = self._select_motives(subject, event, tick)
        dominant = self.state.motives.get(dominant_id or "")
        modulation = self.derive_modulation(subject, event, dominant)
        self.index_canonical_state(subject)

        seeds: dict[str, float] = {}
        if event.source and event.source not in {"self", "world", "system"}:
            seeds[_ref("person", event.source)] = 0.92
        for tag in event.tags:
            if _semantic_tag(tag):
                ref = _ref("concept", tag)
                seeds[ref] = max(seeds.get(ref, 0.0), 0.78)
        for rank, motive_id in enumerate(active_ids):
            seeds[_ref("motive", motive_id)] = max(0.42, 0.88 - rank * 0.16)
            motive = self.state.motives.get(motive_id)
            if motive is not None:
                ref = _ref("concept", motive.theme)
                seeds[ref] = max(seeds.get(ref, 0.0), 0.68 - rank * 0.10)

        activation = self.state.graph.spread(
            seeds,
            depth=modulation.propagation_depth,
            fanout=modulation.propagation_fanout,
            decay=0.68 + modulation.exploration * 0.08,
            max_active=64,
        )
        memory_refs = activation.top("memory:", modulation.retrieval_budget)
        return CognitiveCycle(
            tick=tick,
            dominant_motive_id=dominant_id,
            active_motive_ids=active_ids,
            modulation=modulation,
            activation=activation,
            activated_memory_ids=tuple(ref.split(":", 1)[1] for ref in memory_refs),
        )

    def learn_after_step(
        self, subject: SubjectState, event: WorldEvent, cycle: CognitiveCycle, *,
        recalled_memory_ids: Iterable[str], selected_action: str,
    ) -> None:
        self.index_canonical_state(subject)
        graph = self.state.graph
        tick = subject.tick
        context_refs: list[str] = []
        if event.source and event.source not in {"self", "world", "system"}:
            context_refs.append(_ref("person", event.source))
        context_refs.extend(
            _ref("concept", tag) for tag in event.tags if _semantic_tag(tag)
        )
        memory_refs = [_ref("memory", memory_id) for memory_id in recalled_memory_ids]
        for motive_id in cycle.active_motive_ids:
            if motive_id not in self.state.motives:
                continue
            motive_ref = _ref("motive", motive_id)
            for target in (*context_refs[:6], *memory_refs[:4]):
                graph.connect_both(motive_ref, target, "coactive", 0.24, tick, learn=True)
            graph.connect_both(
                motive_ref, _ref("action", selected_action), "action_context",
                0.28, tick, learn=True,
            )
        for left in context_refs[:5]:
            for right in context_refs[:5]:
                if left < right:
                    graph.connect_both(left, right, "cooccurs", 0.18, tick, learn=True)

    def record_outcome(
        self, action: str, success: float, valence: float,
        tags: Iterable[str], tick: int, *, regime: CognitiveRegime | None = None,
    ) -> None:
        success = _clamp(success)
        reward = max(-1.0, min(1.0, (success - 0.5) * 1.4 + float(valence) * 0.45))
        old = self.state.strategy_success.get(action, 0.0)
        self.state.strategy_success[action] = max(
            -1.0, min(1.0, old * 0.82 + reward * 0.18)
        )
        if regime is not None:
            key = f"{action}|{CognitiveRegime(regime).value}"
            row = self.state.strategy_contexts.setdefault(key, {"value": 0.0, "evidence": 0})
            row["value"] = max(-1.0, min(1.0, row["value"] * 0.82 + reward * 0.18))
            row["evidence"] = min(10000, row["evidence"] + 1)
            while len(self.state.strategy_contexts) > 320:
                del self.state.strategy_contexts[next(iter(self.state.strategy_contexts))]
        while len(self.state.strategy_success) > 64:
            del self.state.strategy_success[next(iter(self.state.strategy_success))]
        action_ref = _ref("action", action)
        for tag in tags:
            if _semantic_tag(tag):
                self.state.graph.connect_both(
                    action_ref, _ref("concept", tag), "outcome_context",
                    0.34 + 0.20 * max(0.0, reward), tick, learn=True,
                )

    def strategy_value(self, action: str, regime: CognitiveRegime) -> float:
        global_value = self.state.strategy_success.get(action, 0.0)
        row = self.state.strategy_contexts.get(f"{action}|{regime.value}")
        if row is None:
            return global_value
        return contextual_reliability(global_value, row["value"], row["evidence"])

    def compact(self, tick: int, *, retire_stale: bool = True) -> None:
        _compact_motive_state(self.state, tick=tick, retire_stale=retire_stale)

    def dominant_motive(self) -> MotiveRecord | None:
        return self.state.motives.get(self.state.last_dominant_motive_id or "")

    def motive_for(self, motive_id: str | None) -> MotiveRecord | None:
        if not motive_id:
            return None
        return self.state.motives.get(motive_id)
