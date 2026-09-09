"""Action-causal prediction layer for MicroPsiDUCK v0.10.

This composition layer extends the continuous organism with predictions about the
outcomes of the subject's own canonical actions. World-fact expectations remain
resolved by perceived world evidence. Action expectations are resolved only by
``resolve_outcome`` for the exact action ID they reference.

Resolved action predictions influence later route evaluation. A separate persistent
causal-sequence model also learns whether the next action in an enacted canonical
plan tends to succeed after the previous action. Temporal adjacency is treated as a
bounded predictive hypothesis, not proof of causal necessity. Motive and modulation
remain the organizing control system.
"""
from __future__ import annotations

from dataclasses import replace
from typing import Iterable

from .causal_v010 import CausalSequenceState
from .expectations_v010 import (
    ActionExpectationResolution,
    ActionOutcomeExpectation,
)
from .living import MemoryProvenance, WorldEvent
from .organism_v010 import LivingDuck as ContinuousLivingDuck


class LivingDuck(ContinuousLivingDuck):
    """v0.10 organism with explicit action and sequence-conditioned prediction."""

    def __init__(self, *args, causal_state: CausalSequenceState | None = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.causal_state = causal_state or CausalSequenceState()
        self.causal_state.normalize()

    def action_expectations(self, *, status: str | None = None) -> list[ActionOutcomeExpectation]:
        rows = list(self.expectation_ledger.action_records)
        if status is not None:
            rows = [record for record in rows if record.status == str(status)]
        return rows

    def _action_prediction_route_adjustment(self, action: str) -> float:
        """Return a bounded evidence-weighted route prior from action calibration.

        The ledger's 0.70 smoothed prior is neutral. Sparse evidence has a small
        effect; repeated evidence can matter more, but cannot dominate motive and
        modulation by itself.
        """

        key = f"action:{str(action).strip().lower()}"
        row = self.expectation_ledger.calibration.get(key)
        if row is None:
            return 0.0
        evidence = row.fulfilled + row.violated
        if evidence <= 0:
            return 0.0
        evidence_weight = min(1.0, evidence / 4.0)
        centered_reliability = row.reliability - 0.70
        return max(-0.24, min(0.24, centered_reliability * 0.90 * evidence_weight))

    def _sequence_prediction_route_adjustment(self, kind: str, route: str) -> float:
        """Bias a route from learned reliability of its adjacent action sequence."""

        steps = self._ROUTES.get(kind, {}).get(route, ())
        if len(steps) < 2:
            return 0.0
        adjustment = 0.0
        for prior, following in zip(steps, steps[1:]):
            row = self.causal_state.transition(prior.preferred_action, following.preferred_action)
            if row is None or row.evidence <= 0:
                continue
            evidence_weight = min(1.0, row.evidence / 4.0)
            centered_reliability = row.reliability - 0.70
            adjustment += centered_reliability * 0.80 * evidence_weight
        return max(-0.20, min(0.20, adjustment))

    def _route_score(self, kind: str, route: str) -> float:
        """Blend action and sequence reliability into motivated route evaluation."""

        score = super()._route_score(kind, route)
        features = self._ROUTE_FEATURES.get(route, {})
        action = str(features.get("action", "wait"))
        return (
            score
            + self._action_prediction_route_adjustment(action)
            + self._sequence_prediction_route_adjustment(kind, route)
        )

    def register_action_outcome_expectation(
        self,
        proposition: str,
        *,
        min_success: float | None = 0.55,
        min_valence: float | None = None,
        max_valence: float | None = None,
        confidence: float | None = None,
    ) -> ActionOutcomeExpectation:
        """Predict the outcome of the one action currently pending resolution."""

        pending = self.state.pending_action
        if pending is None:
            raise ValueError("an action must be pending before its outcome can be predicted")
        return self.expectation_ledger.register_action(
            self.state.tick,
            proposition,
            action_id=pending.action_id,
            action_name=pending.name,
            min_success=min_success,
            min_valence=min_valence,
            max_valence=max_valence,
            confidence=confidence,
        )

    def _canonical_plan_step(self, event: WorldEvent) -> tuple[bool, str]:
        """Verify that an endogenous event refers to the current canonical plan step."""

        tags = {str(tag).lower() for tag in event.tags}
        if "opportunity_active" not in tags or "plan_step" not in tags:
            return False, ""
        concern_id = next(
            (
                str(tag).split(":", 1)[1]
                for tag in event.tags
                if str(tag).lower().startswith("concern_id:")
            ),
            "",
        )
        if not concern_id:
            return False, ""
        try:
            concern_memory = self._concern_memory(concern_id)
        except KeyError:
            return False, ""
        if "plan_step" not in concern_memory.tags:
            return False, ""
        active_plan = next(
            (
                plan
                for plan in self.plans(status="active")
                if plan.pending_concern_id == concern_id
            ),
            None,
        )
        if active_plan is None:
            return False, ""
        concern = self._concern_from_memory(concern_memory)
        return True, concern.text

    def _automatic_plan_action_expectation(
        self,
        event: WorldEvent,
        *,
        action_id: str,
        selected_action: str,
        concern_text: str,
    ) -> ActionOutcomeExpectation | None:
        if selected_action in {"", "wait"}:
            return None
        if any(
            record.status == "open" and record.action_id == action_id
            for record in self.expectation_ledger.action_records
        ):
            return None
        action_phrase = selected_action.replace("_", " ")
        proposition = (
            f"I expect {action_phrase} to move this step forward: {concern_text}"
            if concern_text
            else f"I expect {action_phrase} to move this plan forward."
        )
        return self.expectation_ledger.register_action(
            self.state.tick,
            proposition,
            action_id=action_id,
            action_name=selected_action,
            min_success=0.55,
            confidence=None,
        )

    def step(self, event: WorldEvent, *, allow_inner_speech: bool = True):
        """Retire abandoned action predictions and predict canonical plan-step outcomes."""

        previous_pending = self.state.pending_action
        if previous_pending is not None:
            self.expectation_ledger.retire_action_for(
                previous_pending.action_id,
                self.state.tick + 1,
            )

        is_plan_step, concern_text = self._canonical_plan_step(event)
        result = super().step(event, allow_inner_speech=allow_inner_speech)

        auto_record = None
        if is_plan_step:
            auto_record = self._automatic_plan_action_expectation(
                event,
                action_id=result.action_id,
                selected_action=result.selected_action,
                concern_text=concern_text,
            )

        trace = dict(result.developer_trace)
        expectation_trace = dict(trace.get("expectations", {}))
        expectation_trace["active_action_count"] = len(self.expectation_ledger.active_actions())
        if auto_record is not None:
            expectation_trace["automatic_action_expectation_id"] = auto_record.expectation_id
        trace["expectations"] = expectation_trace
        return replace(result, developer_trace=trace)

    def _record_action_expectation_resolutions(
        self,
        resolutions: tuple[ActionExpectationResolution, ...],
    ) -> tuple[str, ...]:
        memory_ids: list[str] = []
        for row in resolutions:
            if row.outcome == "violated":
                text = f"My action did not turn out the way I expected: {row.proposition}"
                tags = (
                    "expectation",
                    "action_expectation",
                    "action_expectation_violation",
                    "expectation_violation",
                    "prediction_error",
                    "inconsistency",
                )
                valence = -0.24
                arousal = 0.58
            else:
                text = f"My action turned out the way I expected: {row.proposition}"
                tags = (
                    "expectation",
                    "action_expectation",
                    "action_expectation_fulfilled",
                    "expectation_fulfilled",
                    "prediction_confirmed",
                )
                valence = 0.14
                arousal = 0.30
            memory = self.state.add_memory(
                text,
                tags=tags,
                valence=valence,
                arousal=arousal,
                importance=max(0.48, min(0.90, 0.48 + 0.34 * row.confidence)),
                provenance=MemoryProvenance.SELF_REFLECTION,
                source="self",
                confidence=row.confidence,
            )
            memory_ids.append(memory.memory_id)
        return tuple(memory_ids)

    def _learn_plan_transition(
        self,
        linked,
        *,
        action_name: str,
        success: float,
    ) -> None:
        """Update only clearly resolved adjacent steps in one canonical plan route."""

        if linked is None or not action_name:
            return
        root, old_plan = linked
        plan_id = old_plan.plan_id
        route = old_plan.current_route or ""
        context = self.causal_state.context_for(plan_id)

        if context is not None:
            adjacent = (
                context.route == route
                and context.previous_step_index + 1 == old_plan.step_index
            )
            if adjacent and success >= 0.60:
                self.causal_state.observe_transition(
                    context.previous_action,
                    action_name,
                    outcome="fulfilled",
                    tick=self.state.tick,
                )
            elif adjacent and success <= 0.38:
                self.causal_state.observe_transition(
                    context.previous_action,
                    action_name,
                    outcome="violated",
                    tick=self.state.tick,
                )

        if success >= 0.60:
            try:
                refreshed = self._plan_from_memory(root)
            except Exception:
                self.causal_state.clear_context(plan_id)
                return
            if refreshed.status == "active" and refreshed.current_route == route:
                self.causal_state.set_context(
                    plan_id,
                    route=route,
                    previous_action=action_name,
                    previous_step_index=old_plan.step_index,
                    tick=self.state.tick,
                )
            else:
                self.causal_state.clear_context(plan_id)
        elif success <= 0.38:
            self.causal_state.clear_context(plan_id)

    def resolve_outcome(
        self,
        action_id: str,
        *,
        success: float,
        valence: float,
        description: str,
        tags: Iterable[str] = (),
    ) -> None:
        """Resolve action predictions and learn bounded within-plan transitions."""

        linked = self._plan_for_pending_action(action_id)
        pending = self.state.pending_action
        action_name = (
            pending.name
            if pending is not None and pending.action_id == action_id
            else ""
        )
        success_value = max(0.0, min(1.0, float(success)))
        resolutions = self.expectation_ledger.evaluate_action_outcome(
            action_id,
            success=success,
            valence=valence,
            current_tick=self.state.tick,
        )
        super().resolve_outcome(
            action_id,
            success=success,
            valence=valence,
            description=description,
            tags=tags,
        )
        self._learn_plan_transition(
            linked,
            action_name=action_name,
            success=success_value,
        )
        self._record_action_expectation_resolutions(resolutions)


__all__ = ["LivingDuck"]
