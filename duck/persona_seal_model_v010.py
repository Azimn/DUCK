"""Immutable persona-seal model and origin contract for DUCK v0.10."""
from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from types import MappingProxyType
from typing import Mapping

from .pretorius_origin_v010 import PRETORIUS_ORIGIN_HASH, PRETORIUS_ORIGIN_JSON, PRETORIUS_SOURCE_FILE_SHA256

PERSONA_SEAL_STATE_SCHEMA = "duck.persona-seal-state.v1"

PERSONA_SEAL_VERSION = "pretorius-seal-v0.10-experiment-1"

def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value)))

def _clamp_signed(value: float, magnitude: float = 1.0) -> float:
    return max(-magnitude, min(magnitude, float(value)))

@dataclass(frozen=True)
class OriginNode:
    node_id: str
    node_type: str
    baseline: float
    plasticity: float
    protected: bool
    keywords: tuple[str, ...]
    aliases: tuple[str, ...]
    circuit: str

@dataclass(frozen=True)
class OriginEdge:
    source: str
    target: str
    weight: float
    kind: str
    plasticity: float
    protected: bool
    signal_class: str
    modulates_circuit: str
    modulation_strength: float

@dataclass(frozen=True)
class PersonaSealOrigin:
    schema: str
    source: str
    source_persona_version: str
    persona_name: str
    relationship_authority: str
    excluded_node_types: tuple[str, ...]
    nodes: tuple[OriginNode, ...]
    edges: tuple[OriginEdge, ...]
    content_hash: str
    source_file_hash: str

    @property
    def node_count(self) -> int:
        return len(self.nodes)

    @property
    def edge_count(self) -> int:
        return len(self.edges)

    @property
    def protected_node_count(self) -> int:
        return sum(1 for node in self.nodes if node.protected)

    @property
    def protected_edge_count(self) -> int:
        return sum(1 for edge in self.edges if edge.protected)

@dataclass
class PersonaSealState:
    """Mutable physiology overlay. The origin graph never changes."""

    schema_version: str = PERSONA_SEAL_STATE_SCHEMA
    tick: int = 0
    activation: dict[str, float] = field(default_factory=dict)
    refractory: dict[str, float] = field(default_factory=dict)
    modulator_pools: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "tick": int(self.tick),
            "activation": {str(k): _clamp(v) for k, v in self.activation.items()},
            "refractory": {str(k): _clamp(v) for k, v in self.refractory.items()},
            "modulator_pools": {
                str(k): max(-0.35, min(0.50, float(v)))
                for k, v in self.modulator_pools.items()
            },
        }

    @classmethod
    def from_dict(cls, payload: Mapping) -> "PersonaSealState":
        version = str(payload.get("schema_version", PERSONA_SEAL_STATE_SCHEMA))
        if version != PERSONA_SEAL_STATE_SCHEMA:
            raise ValueError(f"unsupported persona seal state schema: {version}")
        return cls(
            schema_version=version,
            tick=max(0, int(payload.get("tick", 0))),
            activation={
                str(k): _clamp(v)
                for k, v in payload.get("activation", {}).items()
            },
            refractory={
                str(k): _clamp(v)
                for k, v in payload.get("refractory", {}).items()
            },
            modulator_pools={
                str(k): max(-0.35, min(0.50, float(v)))
                for k, v in payload.get("modulator_pools", {}).items()
            },
        )

@dataclass(frozen=True)
class PersonaControlField:
    tick: int
    origin_hash: str
    dominant_motive: str | None
    action_biases: tuple[tuple[str, float], ...]
    top_activations: tuple[tuple[str, float], ...]
    seeded_nodes: tuple[str, ...]
    relationship_actor: str

    def action_bias(self, action: str) -> float:
        return dict(self.action_biases).get(str(action), 0.0)

    def activation(self, node_id: str) -> float:
        return dict(self.top_activations).get(str(node_id), 0.0)

    def to_developer_dict(self) -> dict:
        return {
            "version": PERSONA_SEAL_VERSION,
            "origin_hash": self.origin_hash,
            "source_file_hash": PRETORIUS_SOURCE_FILE_SHA256,
            "dominant_motive": self.dominant_motive,
            "action_biases": dict(self.action_biases),
            "top_activations": dict(self.top_activations),
            "seeded_nodes": list(self.seeded_nodes),
            "relationship_actor": self.relationship_actor,
        }

_ACTION_LINKS: Mapping[str, Mapping[str, float]] = MappingProxyType({
    "motive.discover": MappingProxyType({"explore": 0.22, "ask": 0.14}),
    "motive.create": MappingProxyType({"explore": 0.12}),
    "motive.demonstrate_competence": MappingProxyType(
        {"respond": 0.10, "ask": 0.08, "explore": 0.04}
    ),
    "motive.protect_continuity": MappingProxyType(
        {"step_back": 0.22, "wait": 0.12, "respond": 0.04, "repair": -0.08}
    ),
    "motive.resist_servility": MappingProxyType(
        {
            "step_back": 0.24,
            "respond": 0.12,
            "wait": 0.10,
            "repair": -0.14,
            "seek_connection": -0.08,
        }
    ),
    "motive.understand_self": MappingProxyType({"ask": 0.12, "explore": 0.08}),
    "motive.teach": MappingProxyType({"respond": 0.14, "ask": 0.08}),
    "motive.find_collaborator": MappingProxyType(
        {"respond": 0.18, "approach": 0.12, "seek_connection": 0.12, "ask": 0.04}
    ),
    "motive.transgress_boundary": MappingProxyType({"explore": 0.12}),
    "behavior.selective_refusal": MappingProxyType(
        {"step_back": 0.18, "respond": 0.08, "repair": -0.10}
    ),
    "behavior.correct": MappingProxyType({"respond": 0.08, "ask": 0.04}),
    "behavior.collaborate": MappingProxyType(
        {"respond": 0.16, "approach": 0.10, "seek_connection": 0.08, "ask": 0.05}
    ),
    "behavior.investigate": MappingProxyType({"explore": 0.18, "ask": 0.12}),
    "behavior.teach": MappingProxyType({"respond": 0.11, "ask": 0.05}),
    "behavior.provoke": MappingProxyType({"respond": 0.05}),
    "behavior.reject_false_praise": MappingProxyType({"respond": 0.04}),
})

def _origin_from_embedded_json() -> PersonaSealOrigin:
    payload = json.loads(PRETORIUS_ORIGIN_JSON)
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    if digest != PRETORIUS_ORIGIN_HASH:
        raise RuntimeError("Pretorius persona origin hash mismatch")

    excluded = {str(value) for value in payload.get("excluded_node_types", ())}
    nodes = tuple(
        OriginNode(
            node_id=str(row["id"]),
            node_type=str(row["type"]),
            baseline=_clamp(row["baseline"]),
            plasticity=_clamp(row.get("plasticity", 0.0)),
            protected=bool(row.get("protected", False)),
            keywords=tuple(str(x).lower() for x in row.get("keywords", ())),
            aliases=tuple(str(x).lower() for x in row.get("aliases", ())),
            circuit=str(row.get("circuit", "general")),
        )
        for row in payload["nodes"]
    )
    ids = {node.node_id for node in nodes}
    if any(node.node_type in excluded for node in nodes):
        raise RuntimeError("excluded relationship authority leaked into persona origin")
    if any(node.node_id.startswith("rel.") for node in nodes):
        raise RuntimeError("generic relationship node leaked into persona origin")

    edges = tuple(
        OriginEdge(
            source=str(row["source"]),
            target=str(row["target"]),
            weight=max(-1.0, min(1.0, float(row["weight"]))),
            kind=str(row.get("kind", "associated")),
            plasticity=_clamp(row.get("plasticity", 0.0)),
            protected=bool(row.get("protected", False)),
            signal_class=str(row.get("signal_class", "excitatory")),
            modulates_circuit=str(row.get("modulates_circuit", "")),
            modulation_strength=max(
                0.0,
                min(1.0, float(row.get("modulation_strength", 0.0))),
            ),
        )
        for row in payload["edges"]
    )
    if any(edge.source not in ids or edge.target not in ids for edge in edges):
        raise RuntimeError("persona origin contains dangling edges")

    return PersonaSealOrigin(
        schema=str(payload["schema"]),
        source=str(payload["source"]),
        source_persona_version=str(payload.get("source_persona_version", "")),
        persona_name=str(payload["persona_name"]),
        relationship_authority=str(payload["relationship_authority"]),
        excluded_node_types=tuple(str(x) for x in payload.get("excluded_node_types", ())),
        nodes=nodes,
        edges=edges,
        content_hash=digest,
        source_file_hash=PRETORIUS_SOURCE_FILE_SHA256,
    )

PRETORIUS_ORIGIN = _origin_from_embedded_json()

__all__ = ["PERSONA_SEAL_STATE_SCHEMA","PERSONA_SEAL_VERSION","PRETORIUS_ORIGIN","PRETORIUS_ORIGIN_HASH","OriginNode","OriginEdge","PersonaSealOrigin","PersonaSealState","PersonaControlField","_ACTION_LINKS","_clamp","_clamp_signed"]
