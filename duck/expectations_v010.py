"""Persistent subject-owned expectations for MicroPsiDUCK v0.10.

Expectations are predictions held by the continuing subject, not facts owned by the
world. World-fact expectations are resolved only by perceived world evidence.
Action-outcome expectations are resolved only by the registered outcome of the exact
canonical action they predict. Hidden host/world changes cannot resolve subject
prediction state or train calibration.

The ledger also maintains bounded domain calibration. Repeated fulfilled or violated
predictions change the default confidence of later expectations in the same domain
without rewriting any historical prediction.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
from typing import Mapping

from .living import WorldEvent, _clamp, _clamp_signed

EXPECTATION_STATE_SCHEMA = "micropsi-duck.expectations.v1"
MAX_EXPECTATIONS = 128
MAX_ACTION_EXPECTATIONS = 128
MAX_CALIBRATION_KEYS = 128
_ACTIVE_STATUSES = frozenset({"open", "overdue"})
_FINAL_STATUSES = frozenset({"fulfilled", "violated", "superseded", "retired"})
_ACTION_ACTIVE_STATUSES = frozenset({"open"})


def _norm(value: str) -> str:
    return " ".join(str(value).strip().lower().split())


def _action_domain(action_name: str) -> str:
    return f"action:{_norm(action_name)}"


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


@dataclass(frozen=True)
class ActionOutcomeExpectation:
    """Prediction about the outcome of one canonical action attempt."""

    expectation_id: str
    action_id: str
    action_name: str
    proposition: str
    created_tick: int
    updated_tick: int
    confidence: float = 0.70
    min_success: float | None = 0.55
    min_valence: float | None = None
    max_valence: float | None = None
    status: str = "open"
    evidence_tick: int | None = None
    observed_success: float | None = None
    observed_valence: float | None = None

    def normalize(self) -> "ActionOutcomeExpectation":
        status = str(self.status).lower()
        if status not in _ACTION_ACTIVE_STATUSES | _FINAL_STATUSES:
            status = "open"
        minimum = _clamp(self.min_success) if self.min_success is not None else None
        min_valence = _clamp_signed(self.min_valence) if self.min_valence is not None else None
        max_valence = _clamp_signed(self.max_valence) if self.max_valence is not None else None
        if min_valence is not None and max_valence is not None and min_valence > max_valence:
            min_valence, max_valence = max_valence, min_valence
        return replace(
            self,
            action_id=str(self.action_id).strip(),
            action_name=str(self.action_name).strip().lower(),
            proposition=str(self.proposition).strip(),
            created_tick=max(0, int(self.created_tick)),
            updated_tick=max(0, int(self.updated_tick)),
            confidence=_clamp(self.confidence),
            min_success=minimum,
            min_valence=min_valence,
            max_valence=max_valence,
            status=status,
            evidence_tick=(max(0, int(self.evidence_tick)) if self.evidence_tick is not None else None),
            observed_success=(_clamp(self.observed_success) if self.observed_success is not None else None),
            observed_valence=(_clamp_signed(self.observed_valence) if self.observed_valence is not None else None),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self.normalize())

    @classmethod
    def from_dict(cls, data: Mapping) -> "ActionOutcomeExpectation":
        return cls(
            expectation_id=str(data["expectation_id"]),
            action_id=str(data.get("action_id", "")),
            action_name=str(data.get("action_name", "")),
            proposition=str(data.get("proposition", "")),
            created_tick=int(data.get("created_tick", 0)),
            updated_tick=int(data.get("updated_tick", data.get("created_tick", 0))),
            confidence=float(data.get("confidence", 0.70)),
            min_success=(float(data["min_success"]) if data.get("min_success") is not None else None),
            min_valence=(float(data["min_valence"]) if data.get("min_valence") is not None else None),
            max_valence=(float(data["max_valence"]) if data.get("max_valence") is not None else None),
            status=str(data.get("status", "open")),
            evidence_tick=(int(data["evidence_tick"]) if data.get("evidence_tick") is not None else None),
            observed_success=(float(data["observed_success"]) if data.get("observed_success") is not None else None),
            observed_valence=(float(data["observed_valence"]) if data.get("observed_valence") is not None else None),
        ).normalize()


@dataclass(frozen=True)
class ActionExpectationResolution:
    expectation_id: str
    action_id: str
    action_name: str
    outcome: str
    proposition: str
    confidence: float
    observed_success: float
    observed_valence: float


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
    action_records: list[ActionOutcomeExpectation] = field(default_factory=list)
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

        action_unique: dict[str, ActionOutcomeExpectation] = {}
        for raw in self.action_records:
            record = raw.normalize()
            if record.expectation_id and record.action_id and record.action_name:
                action_unique[record.expectation_id] = record
        action_rows = list(action_unique.values())
        if len(action_rows) > MAX_ACTION_EXPECTATIONS:
            action_rows.sort(
                key=lambda row: (
                    row.status in _ACTION_ACTIVE_STATUSES,
                    row.updated_tick,
                    row.created_tick,
                    row.expectation_id,
                ),
                reverse=True,
            )
            action_rows = action_rows[:MAX_ACTION_EXPECTATIONS]
        self.action_records = sorted(
            action_rows,
            key=lambda row: (row.created_tick, row.expectation_id),
        )

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
                key=lambda item: (
                    item[1].updated_tick,
                    item[1].fulfilled + item[1].violated,
                    item[0],
                ),
                reverse=True,
            )[:MAX_CALIBRATION_KEYS]
            normalized_calibration = dict(ordered)
        self.calibration = normalized_calibration

    def learned_confidence(self, domain_key: str) -> float:
        row = self.calibration.get(str(domain_key).strip())
        return row.reliability if row is not None else 0.70

    def _next_id(self) -> str:
        self.expectation_counter += 1
        return f"exp-{self.expectation_counter:06d}"

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
        tick = max(0, int(current_tick))
        resolved_confidence = self.learned_confidence(fact_key) if confidence is None else _clamp(confidence)
        record = ExpectationRecord(
            expectation_id=self._next_id(),
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

    def register_action(
        self,
        current_tick: int,
        proposition: str,
        *,
        action_id: str,
        action_name: str,
        min_success: float | None = 0.55,
        min_valence: float | None = None,
        max_valence: float | None = None,
        confidence: float | None = None,
    ) -> ActionOutcomeExpectation:
        proposition = str(proposition).strip()
        action_id = str(action_id).strip()
        action_name = str(action_name).strip().lower()
        if not proposition or not action_id or not action_name:
            raise ValueError("action expectation proposition, action_id, and action_name are required")
        if min_success is None and min_valence is None and max_valence is None:
            raise ValueError("action expectation requires at least one outcome criterion")
        if any(
            row.action_id == action_id and row.status == "open"
            for row in self.action_records
        ):
            raise ValueError("an open action expectation already exists for this action")
        tick = max(0, int(current_tick))
        domain = _action_domain(action_name)
        resolved_confidence = self.learned_confidence(domain) if confidence is None else _clamp(confidence)
        record = ActionOutcomeExpectation(
            expectation_id=self._next_id(),
            action_id=action_id,
            action_name=action_name,
            proposition=proposition,
            created_tick=tick,
            updated_tick=tick,
            confidence=resolved_confidence,
            min_success=min_success,
            min_valence=min_valence,
            max_valence=max_valence,
        ).normalize()
        self.action_records.append(record)
        self.normalize()
        return record

    def get(self, expectation_id: str) -> ExpectationRecord:
        key = str(expectation_id)
        for record in self.records:
            if record.expectation_id == key:
                return record
        raise KeyError(key)

    def get_action(self, expectation_id: str) -> ActionOutcomeExpectation:
        key = str(expectation_id)
        for record in self.action_records:
            if record.expectation_id == key:
                return record
        raise KeyError(key)

    def active(self) -> tuple[ExpectationRecord, ...]:
        return tuple(record for record in self.records if record.status in _ACTIVE_STATUSES)

    def active_actions(self) -> tuple[ActionOutcomeExpectation, ...]:
        return tuple(record for record in self.action_records if record.status == "open")

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

    def _learn_domain(self, domain_key: str, outcome: str, tick: int) -> None:
        key = str(domain_key).strip()
        calibration = self.calibration.get(key)
        if calibration is None:
            calibration = ExpectationCalibration(fact_key=key)
            self.calibration[key] = calibration
        calibration.record(outcome, tick)
        self.normalize()

    def evaluate_event(self, event: WorldEvent, current_tick: int) -> tuple[ExpectationResolution, ...]:
        """Resolve world-fact expectations only from perceived world evidence."""

        if not event.perceived or not event.world_facts:
            return ()
        return self._evaluate_observed(
            {str(key): (str(value), event.source) for key, value in event.world_facts}, current_tick)

    def observe_facts(self, observations, *, tick: int) -> tuple[ExpectationResolution, ...]:
        """Only sufficiently reliable, unambiguous apparent facts resolve a prediction.

        Reliability below 0.5 remains uncertain evidence. Conflicting simultaneous
        observations do not get arbitrary last-writer authority.
        """
        grouped = {}
        for observation in observations:
            if observation.reliability >= 0.5:
                grouped.setdefault(observation.key, []).append(observation)
        observed = {}
        for key, rows in grouped.items():
            if len({_norm(row.apparent_value) for row in rows}) == 1:
                row = max(rows, key=lambda row: (row.reliability, row.source))
                observed[key] = (row.apparent_value, row.source)
        return self._evaluate_observed(observed, tick)

    def _evaluate_observed(self, observed, current_tick):
        tick = max(0, int(current_tick))
        resolutions: list[ExpectationResolution] = []
        updated: list[ExpectationRecord] = []
        learned: list[tuple[str, str]] = []
        for record in self.records:
            evidence = observed.get(record.fact_key)
            actual = evidence[0] if evidence is not None else None
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
                evidence_source=evidence[1],
            )
            updated.append(resolved)
            learned.append((record.fact_key, outcome))
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
        for domain, outcome in learned:
            self._learn_domain(domain, outcome, tick)
        return tuple(resolutions)

    def evaluate_action_outcome(
        self,
        action_id: str,
        *,
        success: float,
        valence: float,
        current_tick: int,
    ) -> tuple[ActionExpectationResolution, ...]:
        """Resolve only predictions linked to the exact action whose outcome arrived."""

        action_id = str(action_id).strip()
        success = _clamp(success)
        valence = _clamp_signed(valence)
        tick = max(0, int(current_tick))
        resolutions: list[ActionExpectationResolution] = []
        updated: list[ActionOutcomeExpectation] = []
        learned: list[tuple[str, str]] = []
        for record in self.action_records:
            if record.status != "open" or record.action_id != action_id:
                updated.append(record)
                continue
            checks = []
            if record.min_success is not None:
                checks.append(success >= record.min_success)
            if record.min_valence is not None:
                checks.append(valence >= record.min_valence)
            if record.max_valence is not None:
                checks.append(valence <= record.max_valence)
            outcome = "fulfilled" if checks and all(checks) else "violated"
            resolved = replace(
                record,
                status=outcome,
                updated_tick=tick,
                evidence_tick=tick,
                observed_success=success,
                observed_valence=valence,
            )
            updated.append(resolved)
            learned.append((_action_domain(record.action_name), outcome))
            resolutions.append(
                ActionExpectationResolution(
                    expectation_id=record.expectation_id,
                    action_id=record.action_id,
                    action_name=record.action_name,
                    outcome=outcome,
                    proposition=record.proposition,
                    confidence=record.confidence,
                    observed_success=success,
                    observed_valence=valence,
                )
            )
        self.action_records = updated
        for domain, outcome in learned:
            self._learn_domain(domain, outcome, tick)
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

    def retire_action_for(self, action_id: str, current_tick: int) -> tuple[ActionOutcomeExpectation, ...]:
        """Retire unresolved predictions when their pending action is abandoned/overwritten."""

        action_id = str(action_id).strip()
        tick = max(0, int(current_tick))
        retired: list[ActionOutcomeExpectation] = []
        updated: list[ActionOutcomeExpectation] = []
        for record in self.action_records:
            if record.status == "open" and record.action_id == action_id:
                record = replace(record, status="retired", updated_tick=tick)
                retired.append(record)
            updated.append(record)
        self.action_records = updated
        return tuple(retired)

    def to_dict(self) -> dict[str, object]:
        self.normalize()
        return {
            "schema_version": self.schema_version,
            "expectation_counter": self.expectation_counter,
            "records": [record.to_dict() for record in self.records],
            "action_records": [record.to_dict() for record in self.action_records],
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
            action_records=[
                ActionOutcomeExpectation.from_dict(row)
                for row in data.get("action_records", ())
            ],
            calibration={
                str(key): ExpectationCalibration.from_dict(value)
                for key, value in data.get("calibration", {}).items()
            },
        )
        state.normalize()
        return state


__all__ = [
    "EXPECTATION_STATE_SCHEMA",
    "ActionExpectationResolution",
    "ActionOutcomeExpectation",
    "ExpectationCalibration",
    "ExpectationLedgerState",
    "ExpectationRecord",
    "ExpectationResolution",
]
