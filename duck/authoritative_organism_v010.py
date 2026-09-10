"""Current organism boundary: evidence, subject appraisal, body, and affordances.

WorldEvent is a compatibility input. Native callers use perceive(SensoryEvidence).
No current control cycle sends fact observations to historical world-truth storage.
"""
from __future__ import annotations

from dataclasses import asdict, replace

from .affordances_v010 import grounded_affordances
from .body_v010 import BodyDynamics, BodyState, LegacyNeedView, RegulatoryState, energy_deficit
from .living import ActionCandidate, BeliefStance, MemoryProvenance, WorldEvent
from .perception_v010 import (
    Appraisal, AppraisalEngine, LegacyWorldEventAdapter, SensoryEvidence,
    appraisal_to_legacy_tags, perceive,
)
from .predictive_organism_v010 import LivingDuck as PredictiveLivingDuck
from .strategy_v010 import CognitiveRegime, cognitive_regime


class LivingDuck(PredictiveLivingDuck):
    def __init__(self, *args, body_state=None, regulatory_state=None, **kwargs):
        super().__init__(*args, **kwargs)
        if self.state.pending_action is not None:
            self.state.pending_action.tags = tuple(self.state.pending_action.tags)
        # One-time legacy migration. The host extracts historical truth first.
        self.state.world_facts.clear()
        legacy = dict(self.state.needs)
        self.body = body_state if body_state is not None else BodyState()
        self.regulatory = regulatory_state if regulatory_state is not None else RegulatoryState()
        self.state.needs = LegacyNeedView(self.body, self.regulatory)
        if regulatory_state is None:
            for key, value in legacy.items():
                if key != "energy":
                    self.state.needs[key] = value
        if body_state is None:
            self.state.needs["energy"] = legacy.get("energy", 0.85)
        self.body_dynamics = BodyDynamics()
        self.perception_adapter = LegacyWorldEventAdapter()
        self.appraisal_engine = AppraisalEngine()
        self.last_percept = None
        self.last_appraisal = Appraisal()
        self._active_affordances = None
        self._chosen_targets = {}
        self._observation_resolutions = ()
        self._selected_regime = CognitiveRegime.BASELINE

    @property
    def regulatory_state(self):
        self.regulatory.energy_deficit = energy_deficit(self.body)
        return self.regulatory

    def set_world_fact(self, key, text, *, perceived=False, source="world"):
        raise RuntimeError("MicroPsiDUCK v0.10 external truth belongs to the host environment")

    def _integrate_fact_observation(self, observation):
        memory = self.state.add_memory(
            f"{observation.key} appeared to be {observation.apparent_value}.",
            tags=("perceived_fact",), provenance=MemoryProvenance.FIRST_PERSON,
            source=observation.source, confidence=observation.reliability,
        )
        # Weak evidence is retained as uncertain, not upgraded to known truth.
        self.revise_belief(
            observation.key, observation.apparent_value,
            BeliefStance.TRUE if observation.reliability >= 0.5 else BeliefStance.UNCERTAIN,
            observation.reliability, evidence_refs=(memory.memory_id,), source="perception",
        )

    def _expectation_aware_event(self, event):
        # Native observations have already resolved the ledger before appraisal.
        resolutions, self._observation_resolutions = self._observation_resolutions, ()
        return event, resolutions

    def step(self, event: WorldEvent, *, allow_inner_speech=True):
        if not event.perceived and event.kind != "endogenous":
            # Direct hidden input has the same epistemic behavior as host delivery.
            return self.heartbeat(allow_inner_speech=allow_inner_speech)
        evidence = self.perception_adapter.evidence(event)
        return self._run_percept(evidence, legacy_event=event, allow_inner_speech=allow_inner_speech)

    def perceive(self, evidence: SensoryEvidence, *, affordances=(), allow_inner_speech=True, infer_social=True):
        if not isinstance(evidence, SensoryEvidence):
            raise TypeError("perceive requires SensoryEvidence")
        return self._run_percept(evidence, affordances=affordances, infer_social=infer_social,
                                 allow_inner_speech=allow_inner_speech)

    def _run_percept(self, evidence, *, legacy_event=None, affordances=(), allow_inner_speech=True, infer_social=True):
        percept = perceive(evidence)
        available = None if legacy_event is not None else grounded_affordances(percept, affordances, infer_social=infer_social)
        self.last_percept = percept
        relation = self.state.relationship(percept.source)
        memories = self.state.retrieve_memories(percept.content, tags=percept.features,
                                               people=(percept.source,), top_k=5)
        # Familiarity is interpreted from the subject's memory, not host novelty.
        if "object_present" in percept.features and not any(m.text == percept.content for m in self.state.memories):
            percept = replace(percept, features=(*percept.features, "unfamiliar_object"))
        self.last_percept = percept
        resolutions = self.expectation_ledger.observe_facts(percept.observed_facts, tick=self.state.tick + 1)
        # Conflicting apparent facts stay uncertain, including in belief revision.
        values = {}
        for observation in percept.observed_facts:
            values.setdefault(observation.key, set()).add(observation.apparent_value.strip().casefold())
        for observation in percept.observed_facts:
            if len(values[observation.key]) > 1:
                observation = replace(observation, reliability=min(observation.reliability, 0.49))
            self._integrate_fact_observation(observation)
        appraisal = self.appraisal_engine.appraise(
            percept, relationship=relation, recalled_memories=memories,
            regulatory=self.regulatory_state,
            expectation_violation=any(r.outcome == "violated" for r in resolutions), strength=evidence.strength,
        )
        tags = list(appraisal_to_legacy_tags(appraisal, percept.features))
        if legacy_event is not None:
            # Explicit compatibility hints retain authored historical scenarios.
            tags.extend(legacy_event.tags)
            appraisal = replace(appraisal, valence=legacy_event.valence, arousal=legacy_event.intensity,
                                threat_relevance=max(appraisal.threat_relevance, float("threat" in legacy_event.tags)),
                                conflict_relevance=max(appraisal.conflict_relevance, float("conflict" in legacy_event.tags)))
        if any(r.outcome == "violated" for r in resolutions):
            tags.extend(("expectation_violation", "prediction_error", "inconsistency"))
        if any(r.outcome == "fulfilled" for r in resolutions):
            tags.extend(("expectation_fulfilled", "prediction_confirmed"))
        self.last_appraisal = appraisal
        event = WorldEvent(
            legacy_event.kind if legacy_event is not None else "percept",
            percept.source, percept.content, tuple(dict.fromkeys(tags)), appraisal.valence,
            appraisal.arousal, (), legacy_event.perceived if legacy_event is not None else True,
        )
        self._observation_resolutions = resolutions
        self._active_affordances = available
        self._chosen_targets = {}
        try:
            result = super().step(event, allow_inner_speech=allow_inner_speech)
            pending = self.state.pending_action
            if pending is not None:
                pending.target = self._chosen_targets.get(pending.name)
                self.cognitive_state.pending_strategy_context = {
                    "action_id": pending.action_id, "regime": self._selected_regime.value}
            trace = dict(result.developer_trace)
            trace["perception"] = {"modality": percept.modality.value, "confidence": percept.confidence,
                                   "legacy_hints": legacy_event is not None,
                                   "observed_fact_count": len(percept.observed_facts)}
            trace["appraisal"] = asdict(appraisal)
            trace["body"] = self.body.to_dict()
            trace["regulatory"] = self.regulatory_state.to_dict()
            trace["affordances"] = {"compatibility_catalog": available is None,
                                     "selected_target": pending.target if pending else None,
                                     "available": [asdict(a) for a in available] if available is not None else []}
            return replace(result, developer_trace=trace)
        finally:
            self._active_affordances = None
            self._observation_resolutions = ()

    def _augment_subjective_moment(self, moment, cycle, recalled):
        moment, recalled_ids = super()._augment_subjective_moment(moment, cycle, recalled)
        sensations = []
        if self.regulatory_state.energy_deficit >= 0.65:
            sensations.append("I'm getting tired and finding it harder to focus.")
        if self.body.sleep_pressure >= 0.7:
            sensations.append("I'm feeling sleepy.")
        if self.body.pain_load >= 0.5:
            sensations.append("Something hurts.")
        if self.body.thermal_stress >= 0.6:
            sensations.append("The temperature is making me uncomfortable.")
        return replace(moment, concerns=tuple(dict.fromkeys((*moment.concerns, *sensations)))), recalled_ids

    def _advance_energy(self):
        self.body_dynamics.advance(self.body)

    def _apply_endogenous_consequence(self, action):
        if action == "rest":
            self.body_dynamics.rest(self.body, tick=self.state.tick)
        else:
            super()._apply_endogenous_consequence(action)

    def _apply_successful_action_regulation(self, action, success):
        if action == "rest":
            if success >= 0.6:
                self.body_dynamics.rest(self.body, tick=self.state.tick, effectiveness=success)
        else:
            super()._apply_successful_action_regulation(action, success)

    def _regime(self):
        relation = self.state.relationship(self.last_percept.source) if self.last_percept else None
        return cognitive_regime(self.regulatory_state, self.last_appraisal, relation)

    def _learned_strategy_value(self, action):
        return self.control.strategy_value(action, self._regime())

    def _outcome_regime(self, action_id):
        pending = self.cognitive_state.pending_strategy_context
        return CognitiveRegime(pending["regime"]) if pending.get("action_id") == action_id else None

    def resolve_outcome(self, action_id, **kwargs):
        super().resolve_outcome(action_id, **kwargs)
        self.cognitive_state.pending_strategy_context = {}

    def _motive_action_weight(self, action, event):
        # An available rest affordance is relevant to an energy motive even when
        # external sensory evidence contains no authored "rest" tag.
        if self._active_affordances is not None and action == "rest":
            event = replace(event, tags=(*event.tags, "rest"))
        return super()._motive_action_weight(action, event)

    def _affordance_cost(self, affordance):
        reg = self.regulatory_state
        modulation = self.current_cycle.modulation if self.current_cycle else self._idle_modulation()
        return (-affordance.effort * (0.15 + 0.85 * reg.energy_deficit)
                -affordance.risk * (0.2 + 0.8 * reg.safety_deficit)
                -affordance.complexity * (1.0 - modulation.resolution) * 0.3
                -affordance.social_exposure * reg.safety_deficit * 0.15
                +affordance.novelty * modulation.exploration * 0.3)

    def _apply_executive_selection(self, event, relation, memories, rows):
        if self._active_affordances is not None:
            base = {row.name: row for row in rows}
            grounded = {}
            for affordance in self._active_affordances:
                row = base.get(affordance.action, ActionCandidate(
                    affordance.action, 0.18 + self._motive_action_weight(affordance.action, event)
                    + 0.2 * self._learned_strategy_value(affordance.action), ("grounded",)))
                adjusted = replace(row, utility=row.utility + self._affordance_cost(affordance))
                previous = grounded.get(affordance.action)
                if previous is None or adjusted.utility > previous.utility:
                    grounded[affordance.action] = adjusted
                    self._chosen_targets[affordance.action] = affordance.target
            rows = list(grounded.values())
        return super()._apply_executive_selection(event, relation, memories, rows)

    def _select_candidate(self, event, relation, memories, candidates):
        self._selected_regime = self._regime()
        return super()._select_candidate(event, relation, memories, candidates)


__all__ = ["LivingDuck"]
