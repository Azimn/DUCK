"""Bounded sequence-conditioned causal learning for MicroPsiDUCK v0.10.

This module does not claim causal certainty from temporal adjacency. It stores a
small subject-owned predictive model of how reliably one enacted plan action has
been followed by success or failure of the next action in the same canonical route.
Ordinary sequence observations and explicitly marked intervention evidence are kept
distinct. The model can bias later route evaluation while remaining subordinate to
motive, modulation, affordance validity, and actual outcome learning.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Mapping

from .living import _clamp

CAUSAL_STATE_SCHEMA = "micropsi-duck.causal.v1"
MAX_TRANSITIONS = 96
MAX_PLAN_CONTEXTS = 32
MAX_PENDING_INTERVENTIONS = 32


def _norm_action(value: str) -> str:
    return " ".join(str(value).strip().lower().split())


def transition_key(prior_action: str, next_action: str) -> str:
    return f"{_norm_action(prior_action)}->{_norm_action(next_action)}"


@dataclass
class ActionTransitionCalibration:
    """Evidence that a next plan action succeeds after a prior plan action."""

    prior_action: str
    next_action: str
    fulfilled: int = 0
    violated: int = 0
    intervention_fulfilled: int = 0
    intervention_violated: int = 0
    updated_tick: int = 0

    def normalize(self) -> None:
        self.prior_action = _norm_action(self.prior_action)
        self.next_action = _norm_action(self.next_action)
        self.fulfilled = max(0, int(self.fulfilled))
        self.violated = max(0, int(self.violated))
        self.intervention_fulfilled = min(self.fulfilled, max(0, int(self.intervention_fulfilled)))
        self.intervention_violated = min(self.violated, max(0, int(self.intervention_violated)))
        self.updated_tick = max(0, int(self.updated_tick))

    @property
    def evidence(self) -> int:
        return self.fulfilled + self.violated

    @property
    def intervention_evidence(self) -> int:
        return self.intervention_fulfilled + self.intervention_violated

    @property
    def observational_evidence(self) -> int:
        return self.evidence - self.intervention_evidence

    @property
    def reliability(self) -> float:
        """Smoothed conditional reliability with the same neutral 0.70 prior."""

        return _clamp((4.2 + self.fulfilled) / (6.0 + self.evidence))

    @property
    def intervention_reliability(self) -> float:
        """Smoothed reliability using only explicitly marked intervention evidence."""

        return _clamp(
            (4.2 + self.intervention_fulfilled)
            / (6.0 + self.intervention_evidence)
        )

    def record(self, outcome: str, tick: int, *, intervention: bool = False) -> None:
        if outcome == "fulfilled":
            self.fulfilled += 1
            if intervention:
                self.intervention_fulfilled += 1
        elif outcome == "violated":
            self.violated += 1
            if intervention:
                self.intervention_violated += 1
        else:
            raise ValueError("transition outcome must be fulfilled or violated")
        self.updated_tick = max(self.updated_tick, int(tick))
        self.normalize()

    def to_dict(self) -> dict[str, object]:
        self.normalize()
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Mapping) -> "ActionTransitionCalibration":
        row = cls(
            prior_action=str(data.get("prior_action", "")),
            next_action=str(data.get("next_action", "")),
            fulfilled=int(data.get("fulfilled", 0)),
            violated=int(data.get("violated", 0)),
            intervention_fulfilled=int(data.get("intervention_fulfilled", 0)),
            intervention_violated=int(data.get("intervention_violated", 0)),
            updated_tick=int(data.get("updated_tick", 0)),
        )
        row.normalize()
        return row


@dataclass
class PendingIntervention:
    """An exact pending plan action deliberately marked as a causal test."""

    action_id: str
    hypothesis: str
    created_tick: int

    def normalize(self) -> None:
        self.action_id = str(self.action_id).strip()
        self.hypothesis = str(self.hypothesis).strip()
        self.created_tick = max(0, int(self.created_tick))

    def to_dict(self) -> dict[str, object]:
        self.normalize()
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Mapping) -> "PendingIntervention":
        row = cls(
            action_id=str(data.get("action_id", "")),
            hypothesis=str(data.get("hypothesis", "")),
            created_tick=int(data.get("created_tick", 0)),
        )
        row.normalize()
        return row


@dataclass
class PlanSequenceContext:
    """The last clearly successful step available to condition the next step."""

    plan_id: str
    route: str
    previous_action: str
    previous_step_index: int
    updated_tick: int
    previous_was_intervention: bool = False
    intervention_hypothesis: str = ""

    def normalize(self) -> None:
        self.plan_id = str(self.plan_id).strip()
        self.route = str(self.route).strip()
        self.previous_action = _norm_action(self.previous_action)
        self.previous_step_index = max(0, int(self.previous_step_index))
        self.updated_tick = max(0, int(self.updated_tick))
        self.previous_was_intervention = bool(self.previous_was_intervention)
        self.intervention_hypothesis = str(self.intervention_hypothesis).strip()
        if not self.previous_was_intervention:
            self.intervention_hypothesis = ""

    def to_dict(self) -> dict[str, object]:
        self.normalize()
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Mapping) -> "PlanSequenceContext":
        row = cls(
            plan_id=str(data.get("plan_id", "")),
            route=str(data.get("route", "")),
            previous_action=str(data.get("previous_action", "")),
            previous_step_index=int(data.get("previous_step_index", 0)),
            updated_tick=int(data.get("updated_tick", 0)),
            previous_was_intervention=bool(data.get("previous_was_intervention", False)),
            intervention_hypothesis=str(data.get("intervention_hypothesis", "")),
        )
        row.normalize()
        return row


@dataclass
class CausalSequenceState:
    """Versioned, bounded predictive state for within-plan action transitions."""

    schema_version: str = CAUSAL_STATE_SCHEMA
    transitions: dict[str, ActionTransitionCalibration] = field(default_factory=dict)
    plan_contexts: dict[str, PlanSequenceContext] = field(default_factory=dict)
    pending_interventions: dict[str, PendingIntervention] = field(default_factory=dict)

    def normalize(self) -> None:
        if self.schema_version != CAUSAL_STATE_SCHEMA:
            raise ValueError(f"unsupported causal schema: {self.schema_version}")

        normalized_transitions: dict[str, ActionTransitionCalibration] = {}
        for key, raw in self.transitions.items():
            row = raw if isinstance(raw, ActionTransitionCalibration) else ActionTransitionCalibration.from_dict(raw)
            row.normalize()
            if not row.prior_action or not row.next_action:
                continue
            normalized_transitions[transition_key(row.prior_action, row.next_action)] = row
        if len(normalized_transitions) > MAX_TRANSITIONS:
            ordered = sorted(
                normalized_transitions.items(),
                key=lambda item: (item[1].updated_tick, item[1].evidence, item[0]),
                reverse=True,
            )[:MAX_TRANSITIONS]
            normalized_transitions = dict(ordered)
        self.transitions = normalized_transitions

        normalized_contexts: dict[str, PlanSequenceContext] = {}
        for key, raw in self.plan_contexts.items():
            row = raw if isinstance(raw, PlanSequenceContext) else PlanSequenceContext.from_dict(raw)
            row.normalize()
            canonical = row.plan_id or str(key).strip()
            if canonical and row.route and row.previous_action:
                row.plan_id = canonical
                normalized_contexts[canonical] = row
        if len(normalized_contexts) > MAX_PLAN_CONTEXTS:
            ordered = sorted(
                normalized_contexts.items(),
                key=lambda item: (item[1].updated_tick, item[0]),
                reverse=True,
            )[:MAX_PLAN_CONTEXTS]
            normalized_contexts = dict(ordered)
        self.plan_contexts = normalized_contexts

        normalized_interventions: dict[str, PendingIntervention] = {}
        for key, raw in self.pending_interventions.items():
            row = raw if isinstance(raw, PendingIntervention) else PendingIntervention.from_dict(raw)
            row.normalize()
            canonical = row.action_id or str(key).strip()
            if canonical and row.hypothesis:
                row.action_id = canonical
                normalized_interventions[canonical] = row
        if len(normalized_interventions) > MAX_PENDING_INTERVENTIONS:
            ordered = sorted(
                normalized_interventions.items(),
                key=lambda item: (item[1].created_tick, item[0]),
                reverse=True,
            )[:MAX_PENDING_INTERVENTIONS]
            normalized_interventions = dict(ordered)
        self.pending_interventions = normalized_interventions

    def transition(self, prior_action: str, next_action: str) -> ActionTransitionCalibration | None:
        return self.transitions.get(transition_key(prior_action, next_action))

    def observe_transition(
        self,
        prior_action: str,
        next_action: str,
        *,
        outcome: str,
        tick: int,
        intervention: bool = False,
    ) -> ActionTransitionCalibration:
        prior = _norm_action(prior_action)
        following = _norm_action(next_action)
        if not prior or not following:
            raise ValueError("both transition actions are required")
        key = transition_key(prior, following)
        row = self.transitions.get(key)
        if row is None:
            row = ActionTransitionCalibration(prior, following)
            self.transitions[key] = row
        row.record(outcome, tick, intervention=intervention)
        self.normalize()
        return self.transitions[key]

    def register_intervention(self, action_id: str, hypothesis: str, *, tick: int) -> PendingIntervention:
        action_id = str(action_id).strip()
        hypothesis = str(hypothesis).strip()
        if not action_id or not hypothesis:
            raise ValueError("intervention requires an action ID and qualitative hypothesis")
        row = PendingIntervention(action_id, hypothesis, tick)
        row.normalize()
        self.pending_interventions[action_id] = row
        self.normalize()
        return self.pending_interventions[action_id]

    def intervention_for(self, action_id: str) -> PendingIntervention | None:
        return self.pending_interventions.get(str(action_id).strip())

    def consume_intervention(self, action_id: str) -> PendingIntervention | None:
        return self.pending_interventions.pop(str(action_id).strip(), None)

    def context_for(self, plan_id: str) -> PlanSequenceContext | None:
        return self.plan_contexts.get(str(plan_id).strip())

    def set_context(
        self,
        plan_id: str,
        *,
        route: str,
        previous_action: str,
        previous_step_index: int,
        tick: int,
        previous_was_intervention: bool = False,
        intervention_hypothesis: str = "",
    ) -> PlanSequenceContext:
        row = PlanSequenceContext(
            plan_id=str(plan_id).strip(),
            route=str(route).strip(),
            previous_action=previous_action,
            previous_step_index=previous_step_index,
            updated_tick=tick,
            previous_was_intervention=previous_was_intervention,
            intervention_hypothesis=intervention_hypothesis,
        )
        row.normalize()
        if not row.plan_id or not row.route or not row.previous_action:
            raise ValueError("plan context requires plan, route, and action")
        self.plan_contexts[row.plan_id] = row
        self.normalize()
        return self.plan_contexts[row.plan_id]

    def clear_context(self, plan_id: str) -> None:
        self.plan_contexts.pop(str(plan_id).strip(), None)

    def to_dict(self) -> dict[str, object]:
        self.normalize()
        return {
            "schema_version": self.schema_version,
            "transitions": {
                key: row.to_dict()
                for key, row in sorted(self.transitions.items())
            },
            "plan_contexts": {
                key: row.to_dict()
                for key, row in sorted(self.plan_contexts.items())
            },
            "pending_interventions": {
                key: row.to_dict()
                for key, row in sorted(self.pending_interventions.items())
            },
        }

    @classmethod
    def from_dict(cls, data: Mapping) -> "CausalSequenceState":
        state = cls(
            schema_version=str(data.get("schema_version", CAUSAL_STATE_SCHEMA)),
            transitions={
                str(key): ActionTransitionCalibration.from_dict(value)
                for key, value in data.get("transitions", {}).items()
            },
            plan_contexts={
                str(key): PlanSequenceContext.from_dict(value)
                for key, value in data.get("plan_contexts", {}).items()
            },
            pending_interventions={
                str(key): PendingIntervention.from_dict(value)
                for key, value in data.get("pending_interventions", {}).items()
            },
        )
        state.normalize()
        return state


__all__ = [
    "CAUSAL_STATE_SCHEMA",
    "ActionTransitionCalibration",
    "CausalSequenceState",
    "PendingIntervention",
    "PlanSequenceContext",
    "transition_key",
]
