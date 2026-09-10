"""Bounded current-scene continuity for MicroPsiDUCK v0.10.

The workspace is not autobiographical memory and is not world truth. It records what
this subject most recently perceived about identifiable entities so continuous sensing
can distinguish a stable re-observation from a new or changed percept.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from .body_v010 import unit
from .perception_v010 import Modality, Percept

PERCEPTUAL_WORKSPACE_SCHEMA = "micropsi-duck.perceptual-workspace.v1"
MAX_PERCEIVED_ENTITIES = 128
MAX_APPARENT_FACTS_PER_ENTITY = 32


@dataclass
class PerceivedEntity:
    entity_id: str
    last_seen_tick: int
    modality: Modality
    content: str
    features: tuple[str, ...] = ()
    apparent_facts: dict[str, str] = field(default_factory=dict)
    confidence: float = 0.5

    def __post_init__(self):
        self.entity_id = str(self.entity_id)
        if not self.entity_id:
            raise ValueError("perceived entity identity is required")
        self.last_seen_tick = max(0, int(self.last_seen_tick))
        self.modality = Modality(self.modality)
        self.content = str(self.content)
        self.features = tuple(dict.fromkeys(str(x) for x in self.features if str(x)))
        self.apparent_facts = dict(list({str(k): str(v) for k, v in self.apparent_facts.items()}.items())[-MAX_APPARENT_FACTS_PER_ENTITY:])
        self.confidence = unit(self.confidence)

    def to_dict(self):
        return {
            "entity_id": self.entity_id,
            "last_seen_tick": self.last_seen_tick,
            "modality": self.modality.value,
            "content": self.content,
            "features": list(self.features),
            "apparent_facts": dict(self.apparent_facts),
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, data: Mapping):
        return cls(
            entity_id=str(data["entity_id"]),
            last_seen_tick=int(data.get("last_seen_tick", 0)),
            modality=Modality(data.get("modality", "vision")),
            content=str(data.get("content", "")),
            features=tuple(data.get("features", ())),
            apparent_facts=dict(data.get("apparent_facts", {})),
            confidence=float(data.get("confidence", 0.5)),
        )


@dataclass(frozen=True)
class PerceptualUpdate:
    entity_id: str | None
    status: str
    changed_fact_keys: tuple[str, ...] = ()

    @property
    def autobiographically_novel(self) -> bool:
        return self.status in {"new", "changed"}


@dataclass
class PerceptualWorkspaceState:
    schema_version: str = PERCEPTUAL_WORKSPACE_SCHEMA
    entities: dict[str, PerceivedEntity] = field(default_factory=dict)

    def normalize(self):
        if self.schema_version != PERCEPTUAL_WORKSPACE_SCHEMA:
            raise ValueError(f"unsupported perceptual workspace schema: {self.schema_version}")
        rows = sorted(self.entities.values(), key=lambda row: (row.last_seen_tick, row.entity_id), reverse=True)
        self.entities = {row.entity_id: row for row in rows[:MAX_PERCEIVED_ENTITIES]}

    def observe(self, percept: Percept, *, tick: int) -> PerceptualUpdate:
        entity_id = percept.entity_id
        if not entity_id:
            return PerceptualUpdate(None, "untracked", ())
        key = str(entity_id)
        facts = {row.key: row.apparent_value for row in percept.observed_facts}
        previous = self.entities.get(key)
        if previous is None:
            status = "new"
            changed = tuple(sorted(facts))
        else:
            changed_keys = {
                fact_key for fact_key in set(previous.apparent_facts) | set(facts)
                if previous.apparent_facts.get(fact_key) != facts.get(fact_key)
            }
            content_changed = previous.content != percept.content
            feature_changed = previous.features != percept.features
            status = "changed" if changed_keys or content_changed or feature_changed else "stable"
            changed = tuple(sorted(changed_keys))
        self.entities[key] = PerceivedEntity(
            entity_id=key,
            last_seen_tick=tick,
            modality=percept.modality,
            content=percept.content,
            features=percept.features,
            apparent_facts=facts,
            confidence=percept.confidence,
        )
        self.normalize()
        return PerceptualUpdate(key, status, changed)

    def currently_known(self, entity_id: str) -> PerceivedEntity | None:
        return self.entities.get(str(entity_id))

    def to_dict(self):
        self.normalize()
        return {
            "schema_version": self.schema_version,
            "entities": {key: row.to_dict() for key, row in self.entities.items()},
        }

    @classmethod
    def from_dict(cls, data: Mapping):
        if not data:
            return cls()
        state = cls(
            schema_version=str(data.get("schema_version", PERCEPTUAL_WORKSPACE_SCHEMA)),
            entities={str(k): PerceivedEntity.from_dict(v) for k, v in data.get("entities", {}).items()},
        )
        state.normalize()
        return state


__all__ = [
    "MAX_PERCEIVED_ENTITIES",
    "PERCEPTUAL_WORKSPACE_SCHEMA",
    "PerceivedEntity",
    "PerceptualUpdate",
    "PerceptualWorkspaceState",
]
