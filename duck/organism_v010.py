"""Current MicroPsiDUCK v0.10 organism composition.

The motivated-cognition core remains in ``living_v010``. This layer owns continuous
heartbeat scheduling, sparse endogenous signal generation, and subject-owned
expectation evaluation. Keeping those responsibilities explicit prevents body,
social, planning, and prediction dynamics from collapsing into hard-coded executive
rules inside the motive engine.
"""
from __future__ import annotations

from dataclasses import replace

from .access import SubjectAccessFirewall
from .cognition import InnerCognitionProvider
from .endogenous import EndogenousDynamicsState, EndogenousEventGenerator, EndogenousSignal
from .executive import ExecutiveCognitionProvider
from .expectations_v010 import ExpectationLedgerState, ExpectationRecord, ExpectationResolution
from .living import (
    ActionCandidate,
    MemoryProvenance,
    MemoryRecord,
    RelationshipState,
    SubjectState,
    WorldEvent,
)
from .living_v010 import LivingDuck as MotivatedLivingDuck
from .motivated_cognition import MotivatedCognitionState


_STALLED_PLAN_REASONS = frozenset({"low_energy", "context_missing", "context_blocked", "safety_override"})
_PLAN_PRESSURE_REPEAT_AFTER = 10


class LivingDuck(MotivatedLivingDuck):
    """v0.10 organism with motivated cognition, expectations, and endogenous scheduling."""

    def __init__(
        self,
        state: SubjectState | None = None,
        *,
        firewall: SubjectAccessFirewall | None = None,
        cognition: InnerCognitionProvider | None = None,
        executive: ExecutiveCognitionProvider | None = None,
        cognitive_state: MotivatedCognitionState | None = None,
        endogenous_state: EndogenousDynamicsState | None = None,
        expectation_state: ExpectationLedgerState | None = None,
    ) -> None:
        super().__init__(
            state,
            firewall=firewall,
            cognition=cognition,
            executive=executive,
            cognitive_state=cognitive_state,
        )
        self.endogenous = EndogenousEventGenerator(endogenous_state)
        self.expectation_ledger = expectation_state or ExpectationLedgerState()
        self.expectation_ledger.normalize()

    @property
    def endogenous_state(self) -> EndogenousDynamicsState:
        return self.endogenous.state

    @property
    def expectation_state(self) -> ExpectationLedgerState:
        return self.expectation_ledger

    def register_expectation(
        self,
        proposition: str,
        *,
        fact_key: str,
        expected_value: str,
        due_in: int | None = None,
        confidence: float = 0.70,
    ) -> ExpectationRecord:
        """Create a persistent prediction held by the subject."""

        return self.expectation_ledger.register(
            self.state.tick,
            proposition,
            fact_key=fact_key,
            expected_value=expected_value,
            due_in=due_in,
            confidence=confidence,
        )

    def expectations(self, *, status: str | None = None) -> list[ExpectationRecord]:
        rows = list(self.expectation_ledger.records)
        if status is not None:
            rows = [record for record in rows if record.status == str(status)]
        return rows

    def revise_expectation(
        self,
        expectation_id: str,
        *,
        proposition: str | None = None,
        expected_value: str | None = None,
        due_in: int | None = None,
        confidence: float | None = None,
    ) -> ExpectationRecord:
        """Supersede an active prediction while preserving revision lineage."""

        return self.expectation_ledger.revise(
            expectation_id,
            self.state.tick,
            proposition=proposition,
            expected_value=expected_value,
            due_in=due_in,
            confidence=confidence,
        )

    def retire_expectation(self, expectation_id: str) -> ExpectationRecord:
        return self.expectation_ledger.retire(expectation_id, self.state.tick)

    def _expectation_aware_event(
        self,
        event: WorldEvent,
    ) -> tuple[WorldEvent, tuple[ExpectationResolution, ...]]:
        """Attach appraisal consequences only when perceived evidence resolves a prediction."""

        resolutions = self.expectation_ledger.evaluate_event(event, self.state.tick + 1)
        if not resolutions:
            return event, ()
        tags = list(event.tags)
        if any(row.outcome == "violated" for row in resolutions):
            tags.extend(("expectation_violation", "prediction_error", "inconsistency"))
        if any(row.outcome == "fulfilled" for row in resolutions):
            tags.extend(("expectation_fulfilled", "prediction_confirmed"))
        return replace(event, tags=tuple(dict.fromkeys(tags))), resolutions

    def _record_expectation_resolutions(
        self,
        resolutions: tuple[ExpectationResolution, ...],
    ) -> tuple[str, ...]:
        memory_ids: list[str] = []
        for row in resolutions:
            if row.outcome == "violated":
                text = f"What happened did not match what I expected: {row.proposition}"
                tags = ("expectation", "expectation_violation", "prediction_error", "inconsistency")
                valence = -0.22
                arousal = 0.56
            else:
                text = f"What happened matched what I expected: {row.proposition}"
                tags = ("expectation", "expectation_fulfilled", "prediction_confirmed")
                valence = 0.12
                arousal = 0.28
            memory = self.state.add_memory(
                text,
                tags=tags,
                valence=valence,
                arousal=arousal,
                importance=max(0.48, min(0.88, 0.46 + 0.34 * row.confidence)),
                provenance=MemoryProvenance.SELF_REFLECTION,
                source="self",
                confidence=row.confidence,
            )
            memory_ids.append(memory.memory_id)
        return tuple(memory_ids)

    def step(self, event: WorldEvent, *, allow_inner_speech: bool = True):
        """Evaluate predictions before appraisal, then persist qualitative resolution memory."""

        prepared, resolutions = self._expectation_aware_event(event)
        result = super().step(prepared, allow_inner_speech=allow_inner_speech)
        memory_ids = self._record_expectation_resolutions(resolutions)
        trace = dict(result.developer_trace)
        trace["expectations"] = {
            "resolved": [
                {
                    "expectation_id": row.expectation_id,
                    "outcome": row.outcome,
                    "expected_value": row.expected_value,
                    "observed_value": row.observed_value,
                    "confidence": row.confidence,
                }
                for row in resolutions
            ],
            "resolution_memory_ids": list(memory_ids),
            "active_count": len(self.expectation_ledger.active()),
        }
        return replace(result, developer_trace=trace)

    def _candidates(
        self,
        event: WorldEvent,
        relation: RelationshipState,
        memories: list[MemoryRecord],
    ) -> list[ActionCandidate]:
        """Add local affordance support for explicit endogenous threshold signals."""

        rows = super()._candidates(event, relation, memories)
        tags = {str(tag).lower() for tag in event.tags}
        bonuses: dict[str, float] = {}
        reason = ""
        if "fatigue_signal" in tags:
            energy = max(0.0, min(1.0, float(self.state.needs.get("energy", 0.85))))
            deficit = max(0.0, 0.28 - energy)
            bonuses = {"rest": 0.62 + 0.90 * deficit, "wait": -0.04}
            reason = "endogenous_energy"
        elif "affiliation_signal" in tags:
            bonuses = {"seek_connection": 0.40, "wait": -0.04}
            reason = "endogenous_affiliation"
        elif "safety_signal" in tags:
            bonuses = {"step_back": 0.28, "wait": 0.12, "explore": -0.12}
            reason = "endogenous_safety"
        elif "commitment_signal" in tags:
            bonuses = {"ask": 0.34, "respond": 0.12, "wait": -0.03}
            reason = "endogenous_commitment"
        elif "coherence_signal" in tags:
            bonuses = {"ask": 0.38, "wait": 0.05, "explore": 0.08}
            reason = "endogenous_coherence"
        elif "curiosity_signal" in tags:
            bonuses = {"explore": 0.38, "ask": 0.16, "wait": -0.05}
            reason = "endogenous_curiosity"
        elif "plan_pressure" in tags:
            if "stall_low_energy" in tags:
                bonuses = {"rest": 0.42, "wait": 0.05}
            elif "stall_context_missing" in tags:
                bonuses = {"ask": 0.22, "wait": 0.12}
            elif "stall_context_blocked" in tags:
                bonuses = {"wait": 0.20, "ask": 0.10}
            elif "stall_safety_override" in tags:
                bonuses = {"step_back": 0.18, "wait": 0.18, "explore": -0.10}
            else:
                bonuses = {"wait": 0.12}
            reason = "endogenous_plan_pressure"
        if not bonuses:
            return rows

        adjusted: list[ActionCandidate] = []
        for candidate in rows:
            bonus = bonuses.get(candidate.name, 0.0)
            reasons = candidate.reasons
            if bonus != 0.0 and reason:
                reasons = tuple(dict.fromkeys((*reasons, reason)))
            adjusted.append(ActionCandidate(candidate.name, candidate.utility + bonus, reasons))
        return adjusted

    def _has_actionable_concern(self) -> bool:
        """Check whether the inherited prospective-agency path should run first."""

        context_tags = self._recent_context_tags()
        for concern in self.concerns(status="open"):
            available, _ = self._concern_viability(concern, context_tags)
            if available and self._concern_score(concern) >= 0.42:
                return True
        return False

    def _refresh_plan_pressure_state(self) -> None:
        """Retire scheduler keys when a plan resolves or becomes actionable again."""

        active = {plan.plan_id: plan for plan in self.plans(status="active")}
        known_keys = set(self.endogenous_state.latched_signals)
        known_keys.update(self.endogenous_state.last_emitted_tick)
        known_keys.update(self.endogenous_state.emission_counts)
        for key in list(known_keys):
            if key.startswith("plan:") and key.split(":", 1)[1] not in active:
                self.endogenous_state.forget(key)

        context_tags = self._recent_context_tags()
        for plan in active.values():
            key = f"plan:{plan.plan_id}"
            if not plan.pending_concern_id:
                self.endogenous_state.forget(key)
                continue
            try:
                concern = self._concern_from_memory(self._concern_memory(plan.pending_concern_id))
            except KeyError:
                self.endogenous_state.forget(key)
                continue
            available, reason = self._concern_viability(concern, context_tags)
            if available or reason not in _STALLED_PLAN_REASONS:
                self.endogenous_state.forget(key)

    @staticmethod
    def _stalled_plan_text(reason: str) -> str:
        if reason == "low_energy":
            return "I keep coming back to something I want to do, but I don't have the energy for it yet."
        if reason == "context_missing":
            return "I keep coming back to something I want to do, but something I need is still missing."
        if reason == "context_blocked":
            return "I keep coming back to something I want to do, but the situation still blocks it."
        if reason == "safety_override":
            return "I keep coming back to something I want to do, but it still doesn't feel safe enough."
        return "I keep coming back to something I still haven't been able to move forward."

    def _stalled_plan_signal(self) -> EndogenousSignal | None:
        """Surface a persistently blocked canonical plan without creating a new goal."""

        context_tags = self._recent_context_tags()
        rows: list[tuple[float, str, object, str]] = []
        for plan in self.plans(status="active"):
            if not plan.pending_concern_id:
                continue
            try:
                concern = self._concern_from_memory(self._concern_memory(plan.pending_concern_id))
            except KeyError:
                continue
            available, reason = self._concern_viability(concern, context_tags)
            if available or reason not in _STALLED_PLAN_REASONS or concern.deferrals < 2:
                continue
            salience = 0.44 + 0.18 * concern.priority + 0.12 * concern.urgency
            salience += min(0.12, concern.deferrals * 0.025)
            if reason == "safety_override":
                salience += 0.12
            elif reason == "low_energy":
                salience += 0.08
            rows.append((min(0.86, salience), plan.plan_id, concern, reason))

        if not rows:
            return None
        rows.sort(key=lambda row: (row[0], row[1]), reverse=True)
        salience, plan_id, concern, reason = rows[0]
        return self.endogenous.claim_signal(
            self.state,
            key=f"plan:{plan_id}",
            kind="plan",
            text=self._stalled_plan_text(reason),
            tags=("plan_pressure", "blocked_intention", f"stall_{reason}", "planning"),
            salience=salience,
            repeat_after=_PLAN_PRESSURE_REPEAT_AFTER,
        )

    @staticmethod
    def _annotate_heartbeat(result, payload: dict[str, object]):
        trace = dict(result.developer_trace)
        trace["endogenous_dynamics"] = payload
        return replace(result, developer_trace=trace)

    def heartbeat(self, *, allow_inner_speech: bool = True):
        """Advance the organism and recruit the strongest appropriate endogenous event."""

        overdue = self.expectation_ledger.advance(self.state.tick + 1)
        self.endogenous.refresh(self.state)
        self._refresh_plan_pressure_state()
        if self._has_actionable_concern():
            result = super().heartbeat(allow_inner_speech=allow_inner_speech)
            trace = {
                "emitted": False,
                "reason": "prospective_concern_priority",
                "latched_signals": sorted(self.endogenous_state.latched_signals),
            }
        else:
            signal = self.endogenous.next_signal(self.state)
            if signal is None:
                signal = self._stalled_plan_signal()
            if signal is not None:
                result = self.step(signal.event, allow_inner_speech=allow_inner_speech)
                trace = {
                    "emitted": True,
                    "signal": signal.to_developer_dict(),
                    "latched_signals": sorted(self.endogenous_state.latched_signals),
                    "emission_count": self.endogenous_state.emission_counts.get(signal.key, 0),
                }
            else:
                result = super().heartbeat(allow_inner_speech=allow_inner_speech)
                trace = {
                    "emitted": False,
                    "reason": "no_threshold_crossing",
                    "latched_signals": sorted(self.endogenous_state.latched_signals),
                }
        result = self._annotate_heartbeat(result, trace)
        if overdue:
            developer_trace = dict(result.developer_trace)
            expectation_trace = dict(developer_trace.get("expectations", {}))
            expectation_trace["became_overdue"] = [record.expectation_id for record in overdue]
            developer_trace["expectations"] = expectation_trace
            result = replace(result, developer_trace=developer_trace)
        return result
