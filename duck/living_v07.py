"""Thirty-day regulation refinements for the DUCK v0.7 candidate.

The 30-day life simulation showed that v0.6 remained bounded and causally coherent,
but also exposed subtler artificiality: safety could stay chronically depleted after
danger had passed, competence could saturate at its upper bound, and `ask` became a
default social action across many unrelated interactions. This layer corrects those
long-horizon tendencies without changing the first-person access boundary.
"""
from __future__ import annotations

from .living import ActionCandidate, CommitmentRecord, MemoryRecord, RelationshipState, WorldEvent, _clamp
from .living_v06 import LivingDuck as RegulatedLivingDuck


class LivingDuck(RegulatedLivingDuck):
    """v0.7 candidate with slower trait recovery and contextual social action."""

    def _advance_homeostasis(self) -> None:
        super()._advance_homeostasis()

        # Safety is a regulated expectation, not a one-way damage meter. In quiet
        # time it slowly recovers toward a conservative baseline. New threats can
        # still lower it immediately through ordinary appraisal.
        safety = self.state.needs.get("safety", 0.85)
        self.state.needs["safety"] = _clamp(safety + (0.85 - safety) * 0.025)

        # Competence is longer lived than acute affect, but should not become a
        # permanent 1.0 after a short run of successful outcomes.
        competence = self.state.needs.get("competence", 0.55)
        self.state.needs["competence"] = _clamp(competence + (0.60 - competence) * 0.004)

    def _candidates(self, event: WorldEvent, relation: RelationshipState, memories: list[MemoryRecord]) -> list[ActionCandidate]:
        rows = super()._candidates(event, relation, memories)
        if event.kind == "endogenous":
            return rows

        tags = set(event.tags)
        recent = self.state.recent_actions[-8:]
        adjusted: list[ActionCandidate] = []
        ask_repeats = sum(1 for action in recent[-6:] if action == "ask")
        respond_repeats = sum(1 for action in recent[-5:] if action == "respond")

        for candidate in rows:
            utility = candidate.utility

            # A question directed at the subject is normally an occasion to
            # respond, not recursively ask another question.
            if "question" in tags:
                if candidate.name == "respond":
                    utility += 0.16
                elif candidate.name == "ask":
                    utility -= 0.09

            # Supportive social contact makes ordinary engagement more natural.
            if "supportive" in tags:
                if candidate.name == "respond":
                    utility += 0.10
                elif candidate.name == "approach":
                    utility += 0.05

            # A repair attempt creates a genuine repair affordance when the
            # relationship has something to repair.
            if "repair" in tags and relation.guardedness > 0.24:
                if candidate.name == "repair":
                    utility += 0.14
                elif candidate.name == "ask":
                    utility -= 0.04

            # Repetition pressure is small and contextual. It prevents `ask`
            # from becoming a universal social default without forcing random
            # variety when repeated questioning is actually warranted.
            if candidate.name == "ask":
                utility -= min(0.18, 0.045 * ask_repeats)
            elif candidate.name == "respond" and respond_repeats >= 4:
                utility -= 0.03

            # Familiar trusted people modestly favor ordinary engagement.
            if candidate.name == "respond":
                utility += 0.035 * relation.familiarity + 0.025 * relation.trust

            adjusted.append(ActionCandidate(candidate.name, utility, candidate.reasons))
        return adjusted

    def _subjective_concerns(self, actor: str) -> tuple[str, ...]:
        """Integrate later repair into the first-person interpretation of history.

        Broken commitments remain autobiographical facts. A later kept commitment
        can, however, change what that history means now. This avoids a permanent
        binary 'they once failed me, therefore I am forever wary' rule.
        """
        concerns: list[str] = []
        open_for_actor = [c for c in self.state.commitments.values() if c.actor == actor and c.status == "open"]
        broken_for_actor: list[CommitmentRecord] = [c for c in self.state.commitments.values() if c.actor == actor and c.status == "broken"]
        kept_for_actor: list[CommitmentRecord] = [c for c in self.state.commitments.values() if c.actor == actor and c.status == "kept"]

        if broken_for_actor:
            last_broken = max((c.resolved_tick or c.created_tick) for c in broken_for_actor)
            later_kept = any((c.resolved_tick or c.created_tick) > last_broken for c in kept_for_actor)
            relation = self.state.relationship(actor)
            if later_kept and relation.trust >= 0.48 and relation.guardedness <= 0.36:
                concerns.append("They let me down before, but they've followed through since.")
            else:
                concerns.append("I'm still wary because they let me down before.")

        if open_for_actor:
            concerns.append("I'm still waiting to see whether they follow through.")
        if self.state.needs.get("energy", 1.0) < 0.35:
            concerns.append("I'm tired.")
        if self.state.needs.get("affiliation", 0.0) > 0.65:
            concerns.append("I want some connection.")
        if self.state.needs.get("curiosity", 0.0) > 0.72:
            concerns.append("I keep wanting to find out more.")
        return tuple(concerns)
