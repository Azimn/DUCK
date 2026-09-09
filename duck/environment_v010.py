"""Host-owned external world dynamics for MicroPsiDUCK v0.10.

The simulated subject may generate endogenous pressures, but it must not author
external reality. This module therefore keeps scheduled environmental changes in a
separate host-owned persistence envelope. Observable changes are delivered to the
organism as WorldEvents. Unperceived changes update world truth without becoming
subject belief or autobiographical experience.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from .living import WorldEvent

ENVIRONMENT_STATE_SCHEMA = "micropsi-duck.environment.v1"
MAX_SCHEDULED_WORLD_EVENTS = 128


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
    """Versioned host authority for future external events."""

    schema_version: str = ENVIRONMENT_STATE_SCHEMA
    event_counter: int = 0
    scheduled: list[ScheduledWorldEvent] = field(default_factory=list)

    def normalize(self) -> None:
        if self.schema_version != ENVIRONMENT_STATE_SCHEMA:
            raise ValueError(f"unsupported environment dynamics schema: {self.schema_version}")
        self.event_counter = max(0, int(self.event_counter))
        unique: dict[str, ScheduledWorldEvent] = {}
        for record in self.scheduled:
            if not record.event_id:
                continue
            unique[record.event_id] = record
        self.scheduled = sorted(
            unique.values(),
            key=lambda row: (row.due_tick, row.created_tick, row.event_id),
        )[:MAX_SCHEDULED_WORLD_EVENTS]

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
            "scheduled": [record.to_dict() for record in self.scheduled],
        }

    @classmethod
    def from_dict(cls, data: Mapping) -> "EnvironmentDynamicsState":
        state = cls(
            schema_version=str(data.get("schema_version", ENVIRONMENT_STATE_SCHEMA)),
            event_counter=int(data.get("event_counter", 0)),
            scheduled=[ScheduledWorldEvent.from_dict(row) for row in data.get("scheduled", ())],
        )
        state.normalize()
        return state


__all__ = [
    "ENVIRONMENT_STATE_SCHEMA",
    "EnvironmentDynamicsState",
    "ScheduledWorldEvent",
]
