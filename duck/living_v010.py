"""MicroPsiDUCK v0.10 motivated-cognition runtime.

v0.10 keeps canonical identity, memory, belief, relationship, commitment, and
outcome state in SubjectState, while replacing direct need-to-action control with
persistent motives, associative activation, and global cognitive modulation.
"""
from __future__ import annotations

from dataclasses import asdict, replace
from typing import Iterable

from .access import SubjectAccessFirewall
from .cognition import DeterministicInnerVoice, InnerCognition, InnerCognitionProvider
from .living import (
    ActionCandidate,
    MemoryProvenance,
    MemoryRecord,
    RelationshipState,
    SubjectState,
    WorldEvent,
    _clamp,
)
from .living_v08 import ProspectiveConcern
from .living_v09 import LivingDuck as PlanningLivingDuck
from .motivated_cognition import (
    CognitiveCycle,
    CognitiveModulation,
    MOTIVE_ACTION_PREFERENCES,
    MOTIVE_PROSE,
    MotivatedCognitionEngine,
    MotivatedCognitionState,
)
from .subjective import ExperientialFrame, SubjectiveMoment


class LivingDuck(PlanningLivingDuck):
    """v0.10 organism with a persistent motivated-cognition control spine."""

    _ROUTE_FEATURES: dict[str, dict[str, float | str]] = {
        "direct_exploration": {
            "safety": 0.18, "novelty": 1.00, "complexity": 0.45, "social": 0.05, "action": "explore",
        },
        "cautious_inquiry": {
            "safety": 0.86, "novelty": 0.42, "complexity": 0.68, "social": 0.72, "action": "ask",
        },
        "inspect_then_act": {
            "safety": 0.42, "novelty": 0.72, "complexity": 0.72, "social": 0.08, "action": "explore",
        },
        "seek_information_then_act": {
            "safety": 0.76, "novelty": 0.38, "complexity": 0.74, "social": 0.76, "action": "ask",
        },
        "direct_repair": {
            "safety": 0.40, "novelty": 0.20, "complexity": 0.36, "social": 1.00, "action": "repair",
        },
        "clarify_then_repair": {
            "safety": 0.70, "novelty": 0.28, "complexity": 0.66, "social": 0.92, "action": "ask",
        },
    }

    def __init__(
        self,
        state: SubjectState | None = None,
        *,
        firewall: SubjectAccessFirewall | None = None,
        cognition: InnerCognitionProvider | None = None,
        cognitive_state: MotivatedCognitionState | None = None,
    ) -> None:
        experiential_firewall = firewall or SubjectAccessFirewall()
        self.experiential_firewall = experiential_firewall
        self.private_cognition_provider = cognition or DeterministicInnerVoice()
        self.control = MotivatedCognitionEngine(cognitive_state)
        self.current_cycle: CognitiveCycle | None = None
        self.last_experience = ExperientialFrame()
        # Parent cognition is never invoked directly by v0.10 step. The parent loop
        # runs with language lesioned, then v0.10 projects the final cognitive field
        # through the experiential firewall and optionally recruits private language.
        super().__init__(
            state,
            firewall=experiential_firewall,
            cognition=DeterministicInnerVoice(),
        )

    @property
    def cognitive_state(self) -> MotivatedCognitionState:
        return self.control.state

    def _dominant_theme(self) -> str | None:
        motive = self.control.motive_for(
            self.current_cycle.dominant_motive_id if self.current_cycle is not None else self.cognitive_state.last_dominant_motive_id
        )
        return motive.theme if motive is not None else None

    def _motive_action_weight(self, action: str) -> float:
        if self.current_cycle is None:
            return 0.0
        total = 0.0
        for rank, motive_id in enumerate(self.current_cycle.active_motive_ids):
            motive = self.control.motive_for(motive_id)
            if motive is None:
                continue
            preferences = MOTIVE_ACTION_PREFERENCES.get(motive.theme, ())
            if action not in preferences:
                continue
            preference_rank = preferences.index(action)
            dominance = 1.0 if motive_id == self.current_cycle.dominant_motive_id else 0.46
            preference = max(0.25, 1.0 - preference_rank * 0.22)
            total += dominance * preference * (0.30 + 0.38 * motive.strength + 0.18 * motive.urgency)
        return total

    def _candidates(
        self,
        event: WorldEvent,
        relation: RelationshipState,
        memories: list[MemoryRecord],
    ) -> list[ActionCandidate]:
        """Local affordance arbitration downstream of motive and modulation.

        Numeric utility remains intentionally local. Needs and affect no longer enter
        this stage as direct global action terms.
        """
        modulation = self.current_cycle.modulation if self.current_cycle is not None else self._idle_modulation()
        tags = {str(tag).lower() for tag in event.tags}
        base = {
            "wait": 0.20,
            "respond": 0.23,
            "step_back": 0.08,
            "approach": 0.07,
            "ask": 0.11,
            "explore": 0.09,
            "rest": 0.07,
            "repair": 0.06,
            "seek_connection": 0.06,
        }
        if event.kind == "endogenous" and not event.text:
            base["respond"] -= 0.10
            base["approach"] -= 0.04
        if "social" in tags:
            base["respond"] += 0.09
        if "supportive" in tags:
            base["approach"] += 0.10
            base["respond"] += 0.05
        if "threat" in tags:
            base["step_back"] += 0.24
            base["wait"] += 0.08
        if "conflict" in tags:
            base["repair"] += 0.07
            base["ask"] += 0.04
        if tags & {"novel", "mystery", "unknown"}:
            base["explore"] += 0.08
            base["ask"] += 0.05
        if tags & {"obstacle", "blocked"}:
            base["explore"] += 0.05
            base["ask"] += 0.04

        # Relationship values are local affordance evidence, not global drives.
        if relation.trust >= 0.68:
            base["approach"] += 0.08
            base["respond"] += 0.04
        if relation.guardedness >= 0.58:
            base["step_back"] += 0.08
            base["wait"] += 0.04

        base["explore"] += 0.18 * modulation.exploration
        base["ask"] += 0.09 * modulation.resolution
        base["wait"] += 0.10 * (1.0 - modulation.resolution)
        base["step_back"] += 0.09 * modulation.interruption_sensitivity

        activated_tags: set[str] = set()
        if self.current_cycle is not None:
            activated = set(self.current_cycle.activated_memory_ids)
            for memory in self.state.memories:
                if memory.memory_id in activated:
                    activated_tags.update(tag for tag in memory.tags if not tag.startswith(("pc_", "pl_")))
        if "threat" in activated_tags:
            base["step_back"] += 0.07
        if activated_tags & {"novel", "mystery", "unknown"}:
            base["ask"] += 0.04
            base["explore"] += 0.04
        if activated_tags & {"repair", "conflict"}:
            base["repair"] += 0.04

        rows: list[ActionCandidate] = []
        for action, utility in base.items():
            motive_term = self._motive_action_weight(action)
            learned = self.cognitive_state.strategy_success.get(action, 0.0)
            learned_term = max(0.0, learned) * 0.20 * modulation.familiar_strategy_bias
            adaptive = self.state.adaptive.bias(action, event.tags) * 0.18
            rows.append(
                ActionCandidate(
                    action,
                    utility + motive_term + learned_term + adaptive,
                    ("affordance", "motive", "modulation"),
                )
            )
        return rows

    def _idle_modulation(self) -> CognitiveModulation:
        event = WorldEvent(
            "endogenous",
            "self",
            "",
            ("idle", "time_passed"),
            0.0,
            0.10,
            perceived=False,
        )
        return self.control.derive_modulation(self.state, event, self.control.dominant_motive())

    def _concern_viability(self, concern: ProspectiveConcern, context_tags: set[str]) -> tuple[bool, str]:
        if concern.status != "open":
            return False, "resolved"
        if not self._commitment_is_open(concern):
            memory = self._concern_memory(concern.concern_id)
            self._set_status(memory, "satisfied")
            return False, "linked_commitment_resolved"
        if concern.not_before_tick is not None and self.state.tick < concern.not_before_tick:
            return False, "too_early"
        if self.state.tick < concern.cooldown_until:
            return False, "cooldown"
        if concern.required_tags and not set(concern.required_tags).issubset(context_tags):
            return False, "context_missing"
        if set(concern.blocked_tags) & context_tags:
            return False, "context_blocked"

        modulation = self.current_cycle.modulation if self.current_cycle is not None else self._idle_modulation()
        complex_actions = {"explore", "ask", "repair", "approach"}
        if modulation.planning_depth <= 1 and concern.preferred_action in complex_actions:
            return False, "low_resolution"
        if modulation.interruption_sensitivity >= 0.72 and concern.preferred_action in complex_actions:
            return False, "safety_override"
        return True, "available"

    def _concern_score(self, concern: ProspectiveConcern) -> float:
        score = 0.40 * concern.priority + 0.22 * concern.urgency
        dominant = self.control.dominant_motive()
        if dominant is not None:
            preferences = MOTIVE_ACTION_PREFERENCES.get(dominant.theme, ())
            if concern.preferred_action in preferences:
                score += 0.24 * max(0.35, dominant.strength)
        if concern.due_tick is not None:
            distance = concern.due_tick - self.state.tick
            if distance <= 0:
                score += 0.30
            elif distance <= 3:
                score += 0.20
            elif distance <= 8:
                score += 0.10
        score += min(0.10, concern.deferrals * 0.02)
        score -= min(0.12, concern.attempts * 0.03)
        return score

    def _route_score(self, kind: str, route: str) -> float:
        features = self._ROUTE_FEATURES.get(route, {})
        if not features:
            return 0.0
        modulation = self.current_cycle.modulation if self.current_cycle is not None else self._idle_modulation()
        theme = self._dominant_theme()
        safety = float(features.get("safety", 0.5))
        novelty = float(features.get("novelty", 0.5))
        complexity = float(features.get("complexity", 0.5))
        social = float(features.get("social", 0.0))
        action = str(features.get("action", "wait"))

        score = 0.18
        if theme == "safety":
            score += 0.64 * safety
        elif theme == "curiosity":
            score += 0.60 * novelty
        elif theme == "autonomy":
            score += 0.40 * novelty + 0.18 * (1.0 - social)
        elif theme == "competence":
            score += 0.30 * safety + 0.18 * (1.0 - complexity)
        elif theme in {"affiliation", "repair", "commitment"}:
            score += 0.46 * social + 0.18 * safety
        elif theme == "coherence":
            score += 0.30 * social + 0.24 * novelty
        elif theme == "energy":
            score += 0.42 * (1.0 - complexity)

        score += modulation.exploration * 0.26 * novelty
        score += modulation.resolution * 0.12 * complexity
        score -= (1.0 - modulation.resolution) * 0.34 * complexity
        score += modulation.interruption_sensitivity * 0.30 * safety
        score -= modulation.interruption_sensitivity * 0.18 * novelty
        learned = max(0.0, self.cognitive_state.strategy_success.get(action, 0.0))
        score += learned * 0.24 * modulation.familiar_strategy_bias
        return score

    def _ordered_routes(self, kind: str) -> tuple[str, ...]:
        options = self._ROUTES.get(kind)
        if not options:
            raise ValueError(f"unknown plan kind: {kind}")
        ordered = tuple(
            sorted(options, key=lambda route: (self._route_score(kind, route), route), reverse=True)
        )
        modulation = self.current_cycle.modulation if self.current_cycle is not None else self._idle_modulation()
        return ordered[: max(1, min(len(ordered), modulation.route_branching))]

    def _infer_goal(self, event: WorldEvent) -> tuple[str, str] | None:
        if self.current_cycle is None:
            return None
        motive = self.control.motive_for(self.current_cycle.dominant_motive_id)
        if motive is None:
            return None
        tags = {str(tag).lower() for tag in event.tags}
        if tags & {"mystery", "unknown", "novel"} and motive.theme in {"curiosity", "coherence"}:
            return "investigate", f"I want to understand what I encountered: {event.text.strip()}"
        if tags & {"obstacle", "blocked"} and motive.theme in {"autonomy", "competence", "coherence"}:
            return "overcome", f"I want to work out a way past this obstacle: {event.text.strip()}"
        if tags & {"repair_needed", "conflict"} and motive.theme in {"repair", "affiliation", "coherence", "commitment"}:
            return "repair", f"I want to repair what went wrong with {event.source}."
        return None

    def form_goal(
        self,
        kind: str,
        text: str,
        *,
        trigger_memory_id: str | None = None,
        importance: float = 0.82,
    ) -> MemoryRecord:
        root = super().form_goal(
            kind,
            text,
            trigger_memory_id=trigger_memory_id,
            importance=importance,
        )
        if self.current_cycle is not None and self.current_cycle.dominant_motive_id:
            self.cognitive_state.graph.connect_both(
                f"motive:{self.current_cycle.dominant_motive_id.lower()}",
                f"memory:{root.memory_id.lower()}",
                "recruits_goal",
                0.76,
                self.state.tick,
                learn=True,
            )
        return root

    def _memory_by_id(self, memory_id: str) -> MemoryRecord | None:
        for memory in self.state.memories:
            if memory.memory_id == memory_id:
                return memory
        return None

    def _augment_subjective_moment(
        self,
        moment: SubjectiveMoment,
        cycle: CognitiveCycle,
        recalled: tuple[str, ...],
    ) -> tuple[SubjectiveMoment, tuple[str, ...]]:
        recollections = list(moment.recollections)
        recalled_ids = list(recalled)
        for memory_id in cycle.activated_memory_ids:
            if memory_id in recalled_ids:
                continue
            memory = self._memory_by_id(memory_id)
            if memory is None:
                continue
            text = self._recollection_text(memory)
            if text and text not in recollections:
                recollections.append(text)
                recalled_ids.append(memory_id)
            if len(recollections) >= cycle.modulation.retrieval_budget:
                break

        concerns = list(moment.concerns)
        dominant = self.control.motive_for(cycle.dominant_motive_id)
        if dominant is not None:
            prose = MOTIVE_PROSE.get(dominant.theme)
            if prose and prose not in concerns:
                concerns.append(prose)
        if cycle.modulation.planning_depth <= 1:
            concerns.append("I don't have much room for a complicated plan right now.")
        if cycle.modulation.exploration <= 0.14 and dominant is not None and dominant.theme == "safety":
            concerns.append("I don't feel safe enough to poke around.")
        if cycle.modulation.familiar_strategy_bias >= 0.72 and dominant is not None and dominant.theme == "competence":
            concerns.append("I should stick with something I know how to do.")

        augmented = replace(
            moment,
            recollections=tuple(dict.fromkeys(recollections)),
            concerns=tuple(dict.fromkeys(concerns)),
        )
        return augmented, tuple(dict.fromkeys(recalled_ids))

    def step(self, event: WorldEvent, *, allow_inner_speech: bool = True):
        cycle = self.control.prepare_cycle(self.state, event)
        self.current_cycle = cycle

        # Parent mechanics, appraisal, memory, plans, and outcomes remain active, but
        # parent language is always lesioned. v0.10 recruits language only after the
        # motivated cognitive field has been projected into first-person experience.
        result = super().step(event, allow_inner_speech=False)
        moment, recalled_ids = self._augment_subjective_moment(
            result.subjective_moment,
            cycle,
            result.recalled_memory_ids,
        )
        self.last_experience = self.experiential_firewall.experience(moment)
        thought = (
            self.private_cognition_provider.generate(self.last_experience)
            if allow_inner_speech
            else InnerCognition(None)
        )

        self.control.learn_after_step(
            self.state,
            event,
            cycle,
            recalled_memory_ids=recalled_ids,
            selected_action=result.selected_action,
        )
        trace = dict(result.developer_trace)
        trace["motivated_cognition"] = cycle.to_developer_dict()
        trace["motivated_cognition"]["motive_state"] = [
            motive.to_dict()
            for motive in sorted(
                self.cognitive_state.motives.values(),
                key=lambda row: (row.status == "dominant", row.strength, row.urgency),
                reverse=True,
            )[:8]
        ]
        trace["motivated_cognition"]["graph_edge_count"] = len(self.cognitive_state.graph.edges)
        trace["subjective_projection"] = asdict(moment)
        return replace(
            result,
            subjective_moment=moment,
            inner_cognition=thought,
            recalled_memory_ids=recalled_ids,
            developer_trace=trace,
        )

    def _apply_successful_action_regulation(self, action: str, success: float) -> None:
        if success < 0.60:
            return
        scale = min(1.0, success)
        if action == "rest":
            self.state.needs["energy"] = _clamp(self.state.needs.get("energy", 0.8) + 0.24 * scale)
        elif action in {"explore", "ask"}:
            self.state.needs["curiosity"] = _clamp(self.state.needs.get("curiosity", 0.35) - 0.14 * scale)
            self.state.needs["coherence"] = _clamp(self.state.needs.get("coherence", 0.70) + 0.07 * scale)
        elif action in {"seek_connection", "respond", "approach", "repair"}:
            self.state.needs["affiliation"] = _clamp(self.state.needs.get("affiliation", 0.25) - 0.14 * scale)
            self.state.affect["loneliness"] = _clamp(self.state.affect.get("loneliness", 0.2) - 0.10 * scale)
            if action == "repair":
                self.state.needs["coherence"] = _clamp(self.state.needs.get("coherence", 0.70) + 0.06 * scale)
        elif action == "step_back":
            self.state.needs["safety"] = _clamp(self.state.needs.get("safety", 0.85) + 0.12 * scale)

    def resolve_outcome(
        self,
        action_id: str,
        *,
        success: float,
        valence: float,
        description: str,
        tags: Iterable[str] = (),
    ) -> None:
        pending = self.state.pending_action
        action = pending.name if pending is not None and pending.action_id == action_id else ""
        semantic_tags = tuple(tags)
        super().resolve_outcome(
            action_id,
            success=success,
            valence=valence,
            description=description,
            tags=semantic_tags,
        )
        if action:
            self._apply_successful_action_regulation(action, _clamp(success))
            self.control.record_outcome(
                action,
                success,
                valence,
                semantic_tags,
                self.state.tick,
            )
