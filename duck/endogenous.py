"""Sparse endogenous event generation for the continuously running organism.

The motivated substrate already evolves on every heartbeat. This module adds a
small scheduler that turns meaningful internal threshold crossings into endogenous
WorldEvents. Signals are hysteretic and persistent: a pressure fires once, remains
latched while the condition stays active, and can fire again only after recovery or
resolution re-arms it.

The scheduler is mechanistic state. Its thresholds, keys, counts, and salience are
never part of the subject's ExperientialFrame.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from .living import SubjectState, WorldEvent, _clamp

ENDOGENOUS_STATE_SCHEMA = "micropsi-duck.endogenous.v1"
MAX_SIGNAL_RECORDS = 64


@dataclass
class EndogenousDynamicsState:
    """Persistent anti-chatter state for endogenous threshold events."""

    schema_version: str = ENDOGENOUS_STATE_SCHEMA
    latched_signals: set[str] = field(default_factory=set)
    last_emitted_tick: dict[str, int] = field(default_factory=dict)
    emission_counts: dict[str, int] = field(default_factory=dict)

    def normalize(self) -> None:
        if self.schema_version != ENDOGENOUS_STATE_SCHEMA:
            raise ValueError(f"unsupported endogenous dynamics schema: {self.schema_version}")
        self.latched_signals = {str(x) for x in self.latched_signals if str(x)}
        self.last_emitted_tick = {
            str(key): max(0, int(value))
            for key, value in self.last_emitted_tick.items()
            if str(key)
        }
        self.emission_counts = {
            str(key): max(0, int(value))
            for key, value in self.emission_counts.items()
            if str(key)
        }
        self._bound_records()

    def _bound_records(self) -> None:
        keys = set(self.last_emitted_tick) | set(self.emission_counts) | set(self.latched_signals)
        if len(keys) <= MAX_SIGNAL_RECORDS:
            return
        ordered = sorted(
            keys,
            key=lambda key: (
                key in self.latched_signals,
                self.last_emitted_tick.get(key, -1),
                self.emission_counts.get(key, 0),
                key,
            ),
            reverse=True,
        )
        keep = set(ordered[:MAX_SIGNAL_RECORDS])
        self.latched_signals.intersection_update(keep)
        self.last_emitted_tick = {key: value for key, value in self.last_emitted_tick.items() if key in keep}
        self.emission_counts = {key: value for key, value in self.emission_counts.items() if key in keep}

    def record(self, key: str, tick: int) -> None:
        normalized = str(key)
        self.latched_signals.add(normalized)
        self.last_emitted_tick[normalized] = max(0, int(tick))
        self.emission_counts[normalized] = self.emission_counts.get(normalized, 0) + 1
        self._bound_records()

    def rearm(self, key: str) -> None:
        self.latched_signals.discard(str(key))

    def forget(self, key: str) -> None:
        normalized = str(key)
        self.latched_signals.discard(normalized)
        self.last_emitted_tick.pop(normalized, None)
        self.emission_counts.pop(normalized, None)

    def to_dict(self) -> dict[str, object]:
        self.normalize()
        return {
            "schema_version": self.schema_version,
            "latched_signals": sorted(self.latched_signals),
            "last_emitted_tick": dict(sorted(self.last_emitted_tick.items())),
            "emission_counts": dict(sorted(self.emission_counts.items())),
        }

    @classmethod
    def from_dict(cls, data: Mapping) -> "EndogenousDynamicsState":
        state = cls(
            schema_version=str(data.get("schema_version", ENDOGENOUS_STATE_SCHEMA)),
            latched_signals={str(x) for x in data.get("latched_signals", ())},
            last_emitted_tick={
                str(key): int(value)
                for key, value in data.get("last_emitted_tick", {}).items()
            },
            emission_counts={
                str(key): int(value)
                for key, value in data.get("emission_counts", {}).items()
            },
        )
        state.normalize()
        return state


@dataclass(frozen=True)
class EndogenousSignal:
    """One transient internal event selected for the current heartbeat."""

    key: str
    kind: str
    salience: float
    event: WorldEvent

    def to_developer_dict(self) -> dict[str, object]:
        return {
            "key": self.key,
            "kind": self.kind,
            "salience": float(self.salience),
            "tags": list(self.event.tags),
        }


class EndogenousEventGenerator:
    """Generate sparse internal events from persistent subject conditions."""

    def __init__(self, state: EndogenousDynamicsState | None = None) -> None:
        self.state = state or EndogenousDynamicsState()
        self.state.normalize()

    @staticmethod
    def _signal_event(kind: str, text: str, tags: tuple[str, ...], salience: float) -> WorldEvent:
        return WorldEvent(
            kind="endogenous",
            source="self",
            text=text,
            tags=tuple(dict.fromkeys(("idle", "time_passed", "endogenous_signal", *tags))),
            valence=0.0,
            intensity=max(0.20, min(0.85, float(salience))),
            perceived=False,
        )

    def refresh(self, subject: SubjectState) -> None:
        """Re-arm recovered pressures and retire resolved commitment alarms."""

        energy = _clamp(subject.needs.get("energy", 0.85))
        if energy >= 0.55:
            self.state.rearm("energy")

        affiliation = _clamp(subject.needs.get("affiliation", 0.25))
        loneliness = _clamp(subject.affect.get("loneliness", 0.20))
        if affiliation <= 0.48 and loneliness <= 0.42:
            self.state.rearm("affiliation")

        fear = _clamp(subject.affect.get("fear", 0.05))
        safety = _clamp(subject.needs.get("safety", 0.85))
        if fear <= 0.32 and safety >= 0.62:
            self.state.rearm("safety")

        known_commitments = {f"commitment:{item.commitment_id}" for item in subject.commitments.values()}
        for key in list(self.state.latched_signals):
            if not key.startswith("commitment:"):
                continue
            commitment_id = key.split(":", 1)[1]
            record = subject.commitments.get(commitment_id)
            if record is None or record.status != "open":
                self.state.forget(key)
        for key in list(self.state.last_emitted_tick):
            if key.startswith("commitment:") and key not in known_commitments:
                self.state.forget(key)

        self.state.normalize()

    def _candidates(self, subject: SubjectState) -> list[EndogenousSignal]:
        rows: list[EndogenousSignal] = []
        next_tick = subject.tick + 1

        energy = _clamp(subject.needs.get("energy", 0.85))
        if energy <= 0.28 and "energy" not in self.state.latched_signals:
            salience = _clamp(0.58 + (0.28 - energy) * 1.35)
            rows.append(
                EndogenousSignal(
                    "energy",
                    "energy",
                    salience,
                    self._signal_event(
                        "energy",
                        "I keep noticing how depleted I feel.",
                        ("fatigue_signal", "rest_needed", "energy_pressure"),
                        salience,
                    ),
                )
            )

        affiliation = _clamp(subject.needs.get("affiliation", 0.25))
        loneliness = _clamp(subject.affect.get("loneliness", 0.20))
        affiliation_pressure = max(affiliation, loneliness * 0.90)
        if affiliation_pressure >= 0.76 and "affiliation" not in self.state.latched_signals:
            salience = _clamp(0.52 + (affiliation_pressure - 0.76) * 1.45)
            rows.append(
                EndogenousSignal(
                    "affiliation",
                    "affiliation",
                    salience,
                    self._signal_event(
                        "affiliation",
                        "I keep wanting some connection.",
                        ("affiliation_signal", "social_need", "affiliation_pressure"),
                        salience,
                    ),
                )
            )

        fear = _clamp(subject.affect.get("fear", 0.05))
        safety = _clamp(subject.needs.get("safety", 0.85))
        safety_pressure = max(fear, 1.0 - safety)
        if safety_pressure >= 0.72 and "safety" not in self.state.latched_signals:
            salience = _clamp(0.64 + (safety_pressure - 0.72) * 1.20)
            rows.append(
                EndogenousSignal(
                    "safety",
                    "safety",
                    salience,
                    self._signal_event(
                        "safety",
                        "I still feel that I need to protect myself.",
                        ("safety_signal", "safety_pressure"),
                        salience,
                    ),
                )
            )

        for commitment in subject.commitments.values():
            if commitment.status != "open" or commitment.due_tick is None:
                continue
            distance = commitment.due_tick - next_tick
            if distance > 2:
                continue
            key = f"commitment:{commitment.commitment_id}"
            if key in self.state.latched_signals:
                continue
            urgency = 0.68 if distance > 0 else 0.78 if distance == 0 else 0.84
            salience = _clamp(urgency * max(0.55, commitment.importance))
            rows.append(
                EndogenousSignal(
                    key,
                    "commitment",
                    salience,
                    self._signal_event(
                        "commitment",
                        f"I keep coming back to what still needs following through with {commitment.actor}.",
                        ("commitment_signal", "commitment_pressure", "commitment"),
                        salience,
                    ),
                )
            )

        return rows

    def next_signal(self, subject: SubjectState) -> EndogenousSignal | None:
        """Return and latch the strongest newly-crossed endogenous pressure."""

        self.refresh(subject)
        rows = self._candidates(subject)
        if not rows:
            return None
        rows.sort(key=lambda row: (row.salience, row.kind, row.key), reverse=True)
        selected = rows[0]
        self.state.record(selected.key, subject.tick + 1)
        return selected
