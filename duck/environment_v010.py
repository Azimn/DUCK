"""Host-owned external world dynamics for MicroPsiDUCK v0.10.

The simulated subject may generate endogenous pressures, but it must not author
external reality. This module therefore keeps both authoritative world facts and
scheduled environmental changes in a separate host-owned persistence envelope.
Observable changes are delivered to the organism as WorldEvents. Unperceived changes
update world truth without becoming subject belief or autobiographical experience.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from .living import WorldEvent
from .room_v010 import RoomState

ENVIRONMENT_STATE_SCHEMA = "micropsi-duck.environment.v1"
MAX_SCHEDULED_WORLD_EVENTS = 128
MAX_WORLD_FACTS = 1024


def _event_to_dict(event: WorldEvent) -> dict[str, object]:
    return {
        "kind": event.kind,
        "source": event.source,
        "text": event.text,
        "tags": list(event.tags),
        "valence": float(event.valence),
        "intensity": float(event.intensity),
        "world_facts": [list(row) for row in event.world_facts],
        "perceived": bool(event.perceived),
    }


def _event_from_dict(data: Mapping) -> WorldEvent:
    return WorldEvent(
        kind=str(data.get("kind", "environment")),
        source=str(data.get("source", "world")),
        text=str(data.get("text", "")),
        tags=tuple(str(tag) for tag in data.get("tags", ()) if str(tag)),
        valence=float(data.get("valence", 0.0)),
        intensity=float(data.get("intensity", 0.5)),
        world_facts=tuple(
            (str(row[0]), str(row[1]))
            for row in data.get("world_facts", ())
            if isinstance(row, (list, tuple)) and len(row) >= 2
        ),
        perceived=bool(data.get("perceived", True)),
    )


@dataclass(frozen=True)
class ScheduledWorldEvent:
    event_id: str
    created_tick: int
    due_tick: int
    event: WorldEvent

    def to_dict(self) -> dict[str, object]:
        return {
            "event_id": self.event_id,
            "created_tick": int(self.created_tick),
            "due_tick": int(self.due_tick),
            "event": _event_to_dict(self.event),
        }

    @classmethod
    def from_dict(cls, data: Mapping) -> "ScheduledWorldEvent":
        return cls(
            event_id=str(data["event_id"]),
            created_tick=max(0, int(data.get("created_tick", 0))),
            due_tick=max(0, int(data.get("due_tick", 0))),
            event=_event_from_dict(data.get("event", {})),
        )


@dataclass
class EnvironmentDynamicsState:
    """Versioned host authority for current external truth and future events."""

    schema_version: str = ENVIRONMENT_STATE_SCHEMA
    event_counter: int = 0
    world_facts: dict[str, str] = field(default_factory=dict)
    scheduled: list[ScheduledWorldEvent] = field(default_factory=list)
    room: RoomState | None = None

    def normalize(self) -> None:
        if self.schema_version != ENVIRONMENT_STATE_SCHEMA:
            raise ValueError(f"unsupported environment dynamics schema: {self.schema_version}")
        self.event_counter = max(0, int(self.event_counter))
        normalized_facts = {
            str(key): str(value)
            for key, value in self.world_facts.items()
            if str(key).strip()
        }
        if len(normalized_facts) > MAX_WORLD_FACTS:
            # Dict insertion order is meaningful enough for bounded host truth here;
            # retain the most recently inserted tail rather than growing without bound.
            normalized_facts = dict(list(normalized_facts.items())[-MAX_WORLD_FACTS:])
        self.world_facts = normalized_facts

        unique: dict[str, ScheduledWorldEvent] = {}
        for record in self.scheduled:
            if not record.event_id:
                continue
            unique[record.event_id] = record
        self.scheduled = sorted(
            unique.values(),
            key=lambda row: (row.due_tick, row.created_tick, row.event_id),
        )[:MAX_SCHEDULED_WORLD_EVENTS]

    def set_fact(self, key: str, value: str) -> None:
        key = str(key).strip()
        if not key:
            raise ValueError("world fact key is required")
        self.world_facts[key] = str(value)
        self.normalize()

    def apply_event_facts(self, event: WorldEvent) -> None:
        for key, value in event.world_facts:
            self.set_fact(key, value)

    def fact(self, key: str) -> str | None:
        return self.world_facts.get(str(key))

    def schedule(self, current_tick: int, event: WorldEvent, *, due_in: int = 1) -> ScheduledWorldEvent:
        if event.source == "self" or event.kind == "endogenous":
            raise ValueError("external environment scheduler cannot schedule self-authored endogenous events")
        self.event_counter += 1
        record = ScheduledWorldEvent(
            event_id=f"env-{self.event_counter:06d}",
            created_tick=max(0, int(current_tick)),
            due_tick=max(0, int(current_tick)) + max(1, int(due_in)),
            event=event,
        )
        self.scheduled.append(record)
        self.normalize()
        return record

    def next_due(self, next_tick: int) -> ScheduledWorldEvent | None:
        threshold = max(0, int(next_tick))
        for record in self.scheduled:
            if record.due_tick <= threshold:
                return record
        return None

    def complete(self, event_id: str) -> None:
        key = str(event_id)
        self.scheduled = [record for record in self.scheduled if record.event_id != key]

    def cancel(self, event_id: str) -> bool:
        key = str(event_id)
        before = len(self.scheduled)
        self.complete(key)
        return len(self.scheduled) != before

    def to_dict(self) -> dict[str, object]:
        self.normalize()
        return {
            "schema_version": self.schema_version,
            "event_counter": self.event_counter,
            "world_facts": dict(self.world_facts),
            "scheduled": [record.to_dict() for record in self.scheduled],
            "room": self.room.to_dict() if self.room is not None else None,
        }

    @classmethod
    def from_dict(cls, data: Mapping) -> "EnvironmentDynamicsState":
        state = cls(
            schema_version=str(data.get("schema_version", ENVIRONMENT_STATE_SCHEMA)),
            event_counter=int(data.get("event_counter", 0)),
            world_facts={
                str(key): str(value)
                for key, value in data.get("world_facts", {}).items()
            },
            scheduled=[ScheduledWorldEvent.from_dict(row) for row in data.get("scheduled", ())],
            room=RoomState.from_dict(data["room"]) if data.get("room") is not None else None,
        )
        state.normalize()
        return state


__all__ = [
    "ENVIRONMENT_STATE_SCHEMA",
    "MAX_WORLD_FACTS",
    "EnvironmentDynamicsState",
    "ScheduledWorldEvent",
]
