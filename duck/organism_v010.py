"""Current MicroPsiDUCK v0.10 organism composition.

The motivated-cognition core remains in ``living_v010``. This layer owns continuous
heartbeat scheduling and sparse endogenous signal generation. Keeping scheduling
separate prevents body/social/commitment dynamics from becoming another set of
hard-coded executive rules inside the motive engine.
"""
from __future__ import annotations

from dataclasses import replace

from .access import SubjectAccessFirewall
from .cognition import InnerCognitionProvider
from .endogenous import EndogenousDynamicsState, EndogenousEventGenerator
from .executive import ExecutiveCognitionProvider
from .living import ActionCandidate, MemoryRecord, RelationshipState, SubjectState, WorldEvent
from .living_v010 import LivingDuck as MotivatedLivingDuck
from .motivated_cognition import MotivatedCognitionState


class LivingDuck(MotivatedLivingDuck):
    """v0.10 organism with persistent motivated cognition and endogenous scheduling."""

    def __init__(
        self,
        state: SubjectState | None = None,
        *,
        firewall: SubjectAccessFirewall | None = None,
        cognition: InnerCognitionProvider | None = None,
        executive: ExecutiveCognitionProvider | None = None,
        cognitive_state: MotivatedCognitionState | None = None,
        endogenous_state: EndogenousDynamicsState | None = None,
    ) -> None:
        super().__init__(
            state,
            firewall=firewall,
            cognition=cognition,
            executive=executive,
            cognitive_state=cognitive_state,
        )
        self.endogenous = EndogenousEventGenerator(endogenous_state)

    @property
    def endogenous_state(self) -> EndogenousDynamicsState:
        return self.endogenous.state

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
            # A threshold-crossing depletion alarm should tip the already-active
            # energy motive from passive waiting toward explicit recovery. This is
            # a local affordance bias, not a replacement for motive competition.
            bonuses = {"rest": 0.54}
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
        if not bonuses:
            return rows

        adjusted: list[ActionCandidate] = []
        for candidate in rows:
            bonus = bonuses.get(candidate.name, 0.0)
            reasons = candidate.reasons
            if bonus != 0.0 and reason:
                reasons = tuple(dict.fromkeys((*reasons, reason)))
            adjusted.append(
                ActionCandidate(candidate.name, candidate.utility + bonus, reasons)
            )
        return adjusted

    def _has_actionable_concern(self) -> bool:
        """Check whether the inherited prospective-agency path should run first."""

        context_tags = self._recent_context_tags()
        for concern in self.concerns(status="open"):
            available, _ = self._concern_viability(concern, context_tags)
            if available and self._concern_score(concern) >= 0.42:
                return True
        return False

    @staticmethod
    def _annotate_heartbeat(result, payload: dict[str, object]):
        trace = dict(result.developer_trace)
        trace["endogenous_dynamics"] = payload
        return replace(result, developer_trace=trace)

    def heartbeat(self, *, allow_inner_speech: bool = True):
        """Advance the organism and recruit the strongest appropriate endogenous event.

        Existing actionable prospective concerns have priority because they already
        represent concrete intentions. When no such concern is actionable, newly
        crossed body/social/safety/commitment pressures can create a sparse internal
        event. Otherwise the inherited quiet heartbeat runs unchanged.
        """

        self.endogenous.refresh(self.state)
        if self._has_actionable_concern():
            result = super().heartbeat(allow_inner_speech=allow_inner_speech)
            return self._annotate_heartbeat(
                result,
                {
                    "emitted": False,
                    "reason": "prospective_concern_priority",
                    "latched_signals": sorted(self.endogenous_state.latched_signals),
                },
            )

        signal = self.endogenous.next_signal(self.state)
        if signal is not None:
            result = self.step(signal.event, allow_inner_speech=allow_inner_speech)
            return self._annotate_heartbeat(
                result,
                {
                    "emitted": True,
                    "signal": signal.to_developer_dict(),
                    "latched_signals": sorted(self.endogenous_state.latched_signals),
                    "emission_count": self.endogenous_state.emission_counts.get(signal.key, 0),
                },
            )

        result = super().heartbeat(allow_inner_speech=allow_inner_speech)
        return self._annotate_heartbeat(
            result,
            {
                "emitted": False,
                "reason": "no_threshold_crossing",
                "latched_signals": sorted(self.endogenous_state.latched_signals),
            },
        )
