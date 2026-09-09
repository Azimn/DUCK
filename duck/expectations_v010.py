"""Persistent subject-owned expectations for MicroPsiDUCK v0.10.

Expectations are predictions held by the continuing subject, not facts owned by the
world. They may contain mechanistic confidence, deadlines, identifiers, and status,
but those values remain developer-side state. Only perceived evidence may fulfill
or violate an expectation. Hidden host/world changes cannot resolve subject belief.

The ledger also maintains bounded domain calibration. Repeated fulfilled or violated
predictions change the default confidence of later expectations about the same fact
key without rewriting the truth status of any prior record.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
from typing import Mapping

from .living import WorldEvent, _clamp

EXPECTATION_STATE_SCHEMA = "micropsi-duck.expectations.v1"
MAX_EXPECTATIONS = 128
MAX_CALIBRATION_KEYS = 128
_ACTIVE_STATUSES = frozenset({"open", "overdue"})
_FINAL_STATUSES = frozenset({"fulfilled", "violated", "superseded", "retired"})


def _norm(value: str) -> str:
    return " ".join(str(value).strip().lower().split())


@dataclass(frozen=True)
class ExpectationRecord:
    expectation_id: str
    proposition: str
    fact_key: str
    expected_value: str
    created_tick: int
    updated_tick: int
    due_tick: int | None = None
    confidence: float = 0.70
    status: str = "open"
    evidence_tick: int | None = None
    observed_value: str = ""
    evidence_source: str = ""
    revision_of: str | None = None

    def normalize(self) -> "ExpectationRecord":
        status = str(self.status).lower()
        if status not in _ACTIVE_STATUSES | _FINAL_STATUSES:
            status = "open"
        return replace(
            self,
            proposition=str(self.proposition).strip(),
            fact_key=str(self.fact_key).strip(),
            expected_value=str(self.expected_value).strip(),
            created_tick=max(0, int(self.created_tick)),
            updated_tick=max(0, int(self.updated_tick)),
            due_tick=(max(0, int(self.due_tick)) if self.due_tick is not None else None),
            confidence=_clamp(self.confidence),
            status=status,
            evidence_tick=(max(0, int(self.evidence_tick)) if self.evidence_tick is not None else None),
            observed_value=str(self.observed_value),
            evidence_source=str(self.evidence_source),
            revision_of=(str(self.revision_of) if self.revision_of else None),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self.normalize())

    @classmethod
    def from_dict(cls, data: Mapping) -> "ExpectationRecord":
        return cls(
            expectation_id=str(data["expectation_id"]),
            proposition=str(data.get("proposition", "")),
            fact_key=str(data.get("fact_key", "")),
            expected_value=str(data.get("expected_value", "")),
            created_tick=int(data.get("created_tick", 0)),
            updated_tick=int(data.get("updated_tick", data.get("created_tick", 0))),
            due_tick=(int(data["due_tick"]) if data.get("due_tick") is not None else None),
            confidence=float(data.get("confidence", 0.70)),
            status=str(data.get("status", "open")),
            evidence_tick=(int(data["evidence_tick"]) if data.get("evidence_tick") is not None else None),
            observed_value=str(data.get("observed_value", "")),
            evidence_source=str(data.get("evidence_source", "")),
            revision_of=(str(data["revision_of"]) if data.get("revision_of") else None),
        ).normalize()


@dataclass(frozen=True)
class ExpectationResolution:
    expectation_id: str
    outcome: str
    proposition: str
    expected_value: str
    observed_value: str
    confidence: float


@dataclass
class ExpectationCalibration:
    fact_key: str
    fulfilled: int = 0
    violated: int = 0
    updated_tick: int = 0

    def normalize(self) -> None:
        self.fact_key = str(self.fact_key).strip()
        self.fulfilled = max(0, int(self.fulfilled))
        self.violated = max(0, int(self.violated))
        self.updated_tick = max(0, int(self.updated_tick))

    @property
    def reliability(self) -> float:
        """Smoothed predictive reliability with a moderate 0.70 prior."""

        return _clamp((4.2 + self.fulfilled) / (6.0 + self.fulfilled + self.violated))

    def record(self, outcome: str, tick: int) -> None:
        if outcome == "fulfilled":
            self.fulfilled += 1
        elif outcome == "violated":
            self.violated += 1
        self.updated_tick = max(self.updated_tick, int(tick))
        self.normalize()

    def to_dict(self) -> dict[str, object]:
        self.normalize()
        return {
            "fact_key": self.fact_key,
            "fulfilled": self.fulfilled,
            "violated": self.violated,
            "updated_tick": self.updated_tick,
        }

    @classmethod
    def from_dict(cls, data: Mapping) -> "ExpectationCalibration":
        row = cls(
            fact_key=str(data.get("fact_key", "")),
            fulfilled=int(data.get("fulfilled", 0)),
            violated=int(data.get("violated", 0)),
            updated_tick=int(data.get("updated_tick", 0)),
        )
        row.normalize()
        return row


@dataclass
class ExpectationLedgerState:
    """Versioned canonical store for predictions held by the subject."""

    schema_version: str = EXPECTATION_STATE_SCHEMA
    expectation_counter: int = 0
    records: list[ExpectationRecord] = field(default_factory=list)
    calibration: dict[str, ExpectationCalibration] = field(default_factory=dict)

    def normalize(self) -> None:
        if self.schema_version != EXPECTATION_STATE_SCHEMA:
            raise ValueError(f"unsupported expectation schema: {self.schema_version}")
        self.expectation_counter = max(0, int(self.expectation_counter))
        unique: dict[str, ExpectationRecord] = {}
        for raw in self.records:
            record = raw.normalize()
            if record.expectation_id and record.fact_key:
                unique[record.expectation_id] = record
        rows = list(unique.values())
        if len(rows) > MAX_EXPECTATIONS:
            rows.sort(
                key=lambda row: (
                    row.status in _ACTIVE_STATUSES,
                    row.updated_tick,
                    row.created_tick,
                    row.expectation_id,
                ),
                reverse=True,
            )
            rows = rows[:MAX_EXPECTATIONS]
        self.records = sorted(rows, key=lambda row: (row.created_tick, row.expectation_id))

        normalized_calibration: dict[str, ExpectationCalibration] = {}
        for key, raw in self.calibration.items():
            row = raw if isinstance(raw, ExpectationCalibration) else ExpectationCalibration.from_dict(raw)
            row.normalize()
            canonical_key = row.fact_key or str(key).strip()
            if canonical_key:
                row.fact_key = canonical_key
                normalized_calibration[canonical_key] = row
        if len(normalized_calibration) > MAX_CALIBRATION_KEYS:
            ordered = sorted(
                normalized_calibration.items(),
                key=lambda item: (item[1].updated_tick, item[1].fulfilled + item[1].violated, item[0]),
                reverse=True,
            )[:MAX_CALIBRATION_KEYS]
            normalized_calibration = dict(ordered)
        self.calibration = normalized_calibration

    def learned_confidence(self, fact_key: str) -> float:
        row = self.calibration.get(str(fact_key).strip())
        return row.reliability if row is not None else 0.70

    def register(
        self,
        current_tick: int,
        proposition: str,
        *,
        fact_key: str,
        expected_value: str,
        due_in: int | None = None,
        confidence: float | None = None,
        revision_of: str | None = None,
    ) -> ExpectationRecord:
        proposition = str(proposition).strip()
        fact_key = str(fact_key).strip()
        expected_value = str(expected_value).strip()
        if not proposition or not fact_key or not expected_value:
            raise ValueError("expectation proposition, fact_key, and expected_value are required")
        self.expectation_counter += 1
        tick = max(0, int(current_tick))
        resolved_confidence = self.learned_confidence(fact_key) if confidence is None else _clamp(confidence)
        record = ExpectationRecord(
            expectation_id=f"exp-{self.expectation_counter:06d}",
            proposition=proposition,
            fact_key=fact_key,
            expected_value=expected_value,
            created_tick=tick,
            updated_tick=tick,
            due_tick=(tick + max(1, int(due_in))) if due_in is not None else None,
            confidence=resolved_confidence,
            revision_of=revision_of,
        ).normalize()
        self.records.append(record)
        self.normalize()
        return record

    def get(self, expectation_id: str) -> ExpectationRecord:
        key = str(expectation_id)
        for record in self.records:
            if record.expectation_id == key:
                return record
        raise KeyError(key)

    def active(self) -> tuple[ExpectationRecord, ...]:
        return tuple(record for record in self.records if record.status in _ACTIVE_STATUSES)

    def advance(self, current_tick: int) -> tuple[ExpectationRecord, ...]:
        tick = max(0, int(current_tick))
        changed: list[ExpectationRecord] = []
        updated: list[ExpectationRecord] = []
        for record in self.records:
            if record.status == "open" and record.due_tick is not None and tick > record.due_tick:
                record = replace(record, status="overdue", updated_tick=tick)
                changed.append(record)
            updated.append(record)
        self.records = updated
        return tuple(changed)

    def _learn_resolution(self, record: ExpectationRecord, outcome: str, tick: int) -> None:
        key = record.fact_key
        calibration = self.calibration.get(key)
        if calibration is None:
            calibration = ExpectationCalibration(fact_key=key)
            self.calibration[key] = calibration
        calibration.record(outcome, tick)
        self.normalize()

    def evaluate_event(self, event: WorldEvent, current_tick: int) -> tuple[ExpectationResolution, ...]:
        if not event.perceived or not event.world_facts:
            return ()
        observed = {str(key): str(value) for key, value in event.world_facts}
        tick = max(0, int(current_tick))
        resolutions: list[ExpectationResolution] = []
        updated: list[ExpectationRecord] = []
        learned: list[tuple[ExpectationRecord, str]] = []
        for record in self.records:
            actual = observed.get(record.fact_key)
            if record.status not in _ACTIVE_STATUSES or actual is None:
                updated.append(record)
                continue
            outcome = "fulfilled" if _norm(actual) == _norm(record.expected_value) else "violated"
            resolved = replace(
                record,
                status=outcome,
                updated_tick=tick,
                evidence_tick=tick,
                observed_value=actual,
                evidence_source=event.source,
            )
            updated.append(resolved)
            learned.append((record, outcome))
            resolutions.append(
                ExpectationResolution(
                    expectation_id=record.expectation_id,
                    outcome=outcome,
                    proposition=record.proposition,
                    expected_value=record.expected_value,
                    observed_value=actual,
                    confidence=record.confidence,
                )
            )
        self.records = updated
        for record, outcome in learned:
            self._learn_resolution(record, outcome, tick)
        return tuple(resolutions)

    def revise(
        self,
        expectation_id: str,
        current_tick: int,
        *,
        proposition: str | None = None,
        expected_value: str | None = None,
        due_in: int | None = None,
        confidence: float | None = None,
    ) -> ExpectationRecord:
        old = self.get(expectation_id)
        if old.status not in _ACTIVE_STATUSES:
            raise ValueError("only active expectations can be revised")
        tick = max(0, int(current_tick))
        self.records = [
            replace(record, status="superseded", updated_tick=tick)
            if record.expectation_id == old.expectation_id else record
            for record in self.records
        ]
        return self.register(
            tick,
            proposition if proposition is not None else old.proposition,
            fact_key=old.fact_key,
            expected_value=expected_value if expected_value is not None else old.expected_value,
            due_in=due_in,
            confidence=old.confidence if confidence is None else confidence,
            revision_of=old.expectation_id,
        )

    def retire(self, expectation_id: str, current_tick: int) -> ExpectationRecord:
        old = self.get(expectation_id)
        if old.status not in _ACTIVE_STATUSES:
            return old
        tick = max(0, int(current_tick))
        retired = replace(old, status="retired", updated_tick=tick)
        self.records = [retired if row.expectation_id == old.expectation_id else row for row in self.records]
        return retired

    def to_dict(self) -> dict[str, object]:
        self.normalize()
        return {
            "schema_version": self.schema_version,
            "expectation_counter": self.expectation_counter,
            "records": [record.to_dict() for record in self.records],
            "calibration": {
                key: row.to_dict()
                for key, row in sorted(self.calibration.items())
            },
        }

    @classmethod
    def from_dict(cls, data: Mapping) -> "ExpectationLedgerState":
        state = cls(
            schema_version=str(data.get("schema_version", EXPECTATION_STATE_SCHEMA)),
            expectation_counter=int(data.get("expectation_counter", 0)),
            records=[ExpectationRecord.from_dict(row) for row in data.get("records", ())],
            calibration={
                str(key): ExpectationCalibration.from_dict(value)
                for key, value in data.get("calibration", {}).items()
            },
        )
        state.normalize()
        return state


__all__ = [
    "EXPECTATION_STATE_SCHEMA",
    "ExpectationCalibration",
    "ExpectationLedgerState",
    "ExpectationRecord",
    "ExpectationResolution",
]
