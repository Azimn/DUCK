"""Sparse endogenous event generation for the continuously running organism.

The motivated substrate already evolves on every heartbeat. This module adds a
small scheduler that turns meaningful internal threshold crossings into endogenous
WorldEvents. Signals are hysteretic and rate-limited: a pressure fires when it
crosses a meaningful threshold, remains latched while active, and may reassert only
after a bounded cooldown if it is still unresolved. Recovery or resolution clears
the latch and allows a later genuine threshold crossing to fire immediately.

The scheduler is mechanistic state. Its thresholds, keys, counts, cooldown timing,
and salience are never part of the subject's ExperientialFrame.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from .living import SubjectState, WorldEvent, _clamp

ENDOGENOUS_STATE_SCHEMA = "micropsi-duck.endogenous.v1"
MAX_SIGNAL_RECORDS = 64
_REPEAT_AFTER = {
    "energy": 8,
    "affiliation": 12,
    "safety": 4,
    "curiosity": 16,
    "coherence": 10,
    "commitment": 6,
}
_COHERENCE_TAGS = frozenset({
    "contradiction",
    "inconsistency",
    "expectation_violation",
    "prediction_error",
})


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

    @staticmethod
    def _recent_coherence_disruption(subject: SubjectState, *, max_age: int = 8) -> bool:
        for memory in reversed(subject.memories):
            age = subject.tick - memory.tick
            if age > max_age:
                break
            if set(memory.tags) & _COHERENCE_TAGS:
                return True
        return False

    def _ready(self, key: str, next_tick: int, repeat_after: int) -> bool:
        """Allow a new crossing immediately or a persistent pressure after cooldown."""

        if key not in self.state.latched_signals:
            return True
        last = self.state.last_emitted_tick.get(key)
        if last is None:
            return True
        return next_tick - last >= max(1, int(repeat_after))

    def claim_signal(
        self,
        subject: SubjectState,
        *,
        key: str,
        kind: str,
        text: str,
        tags: tuple[str, ...],
        salience: float,
        repeat_after: int,
    ) -> EndogenousSignal | None:
        """Rate-limit and record a composed endogenous source using this scheduler.

        Higher organism layers can identify domain-specific pressures such as a
        persistently blocked canonical plan without creating another clock, latch
        store, or persistence authority. The returned event remains transient.
        """

        next_tick = subject.tick + 1
        if not self._ready(key, next_tick, repeat_after):
            return None
        signal = EndogenousSignal(
            str(key),
            str(kind),
            _clamp(salience),
            self._signal_event(str(kind), str(text), tuple(tags), salience),
        )
        self.state.record(signal.key, next_tick)
        return signal

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

        curiosity = _clamp(subject.needs.get("curiosity", 0.35))
        if curiosity <= 0.56:
            self.state.rearm("curiosity")

        coherence = _clamp(subject.needs.get("coherence", 0.70))
        unease = _clamp(subject.affect.get("unease", 0.05))
        if (
            coherence >= 0.68
            and unease <= 0.30
            and not self._recent_coherence_disruption(subject)
        ):
            self.state.rearm("coherence")

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
        if energy <= 0.28 and self._ready("energy", next_tick, _REPEAT_AFTER["energy"]):
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
        if (
            affiliation_pressure >= 0.76
            and self._ready("affiliation", next_tick, _REPEAT_AFTER["affiliation"])
        ):
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
        if (
            safety_pressure >= 0.72
            and self._ready("safety", next_tick, _REPEAT_AFTER["safety"])
        ):
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

        curiosity = _clamp(subject.needs.get("curiosity", 0.35))
        if (
            curiosity >= 0.82
            and fear <= 0.35
            and safety >= 0.62
            and self._ready("curiosity", next_tick, _REPEAT_AFTER["curiosity"])
        ):
            salience = _clamp(0.50 + (curiosity - 0.82) * 1.35)
            rows.append(
                EndogenousSignal(
                    "curiosity",
                    "curiosity",
                    salience,
                    self._signal_event(
                        "curiosity",
                        "I keep wanting to find something out.",
                        ("curiosity_signal", "curiosity_pressure", "unknown"),
                        salience,
                    ),
                )
            )

        coherence = _clamp(subject.needs.get("coherence", 0.70))
        unease = _clamp(subject.affect.get("unease", 0.05))
        disrupted = self._recent_coherence_disruption(subject)
        coherence_pressure = max(1.0 - coherence, 0.70 if disrupted else 0.0, unease * 0.65)
        if (
            coherence_pressure >= 0.62
            and self._ready("coherence", next_tick, _REPEAT_AFTER["coherence"])
        ):
            salience = _clamp(0.56 + (coherence_pressure - 0.62) * 1.20)
            rows.append(
                EndogenousSignal(
                    "coherence",
                    "coherence",
                    salience,
                    self._signal_event(
                        "coherence",
                        "I keep turning over something that does not fit together yet.",
                        ("coherence_signal", "coherence_pressure", "inconsistency", "question"),
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
            if not self._ready(key, next_tick, _REPEAT_AFTER["commitment"]):
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
        """Return and rate-limit the strongest currently eligible internal pressure."""

        self.refresh(subject)
        rows = self._candidates(subject)
        if not rows:
            return None
        rows.sort(key=lambda row: (row.salience, row.kind, row.key), reverse=True)
        selected = rows[0]
        self.state.record(selected.key, subject.tick + 1)
        return selected
