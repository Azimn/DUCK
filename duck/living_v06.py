"""Long-horizon regulation refinements for the DUCK v0.6 simulation candidate.

This module subclasses the integrated v0.5 LivingDuck rather than rewriting it in
place. The goal is to correct pathologies exposed by longitudinal simulation while
preserving the v0.5 implementation as a historical reference during evaluation.

The refinements are intentionally mechanistic and remain below the subject-access
firewall. They change how residual affect, endogenous drives, repeated action
selection, and repair influence later state. They do not expose numeric telemetry
to private cognition.
"""
from __future__ import annotations

from .living import (
    ActionCandidate,
    LivingDuck as BaseLivingDuck,
    LivingStep,
    MemoryRecord,
    RelationshipState,
    WorldEvent,
    _clamp,
)


class LivingDuck(BaseLivingDuck):
    """v0.6 regulated DUCK used by the longitudinal simulation candidate."""

    def _apply_residues(self) -> None:
        """Apply residual state as decaying activation, not repeated accumulation.

        v0.5 added the full residue magnitude into affect on every tick. A single
        negative outcome could therefore drive fear/unease to 1.0 and keep action
        selection trapped there. In v0.6 residue is a temporary floor above the
        normal affect baseline. Multiple residues can combine, but they decay
        without being re-added as fresh injury each cycle.
        """
        retained = []
        activation: dict[str, float] = {}
        relief = 0.0
        for residue in self.state.residues:
            if residue.channel == "relief":
                relief += residue.magnitude
            elif residue.channel in self.state.affect:
                activation[residue.channel] = activation.get(residue.channel, 0.0) + residue.magnitude
            residue.magnitude *= residue.decay
            if abs(residue.magnitude) >= 0.025:
                retained.append(residue)
        self.state.residues = retained

        baselines = {
            "fear": 0.04,
            "unease": 0.04,
            "anger": 0.04,
            "joy": 0.10,
            "loneliness": 0.18,
        }
        for channel, total in activation.items():
            baseline = baselines.get(channel, 0.0)
            target = _clamp(baseline + min(0.72, total))
            self.state.affect[channel] = max(self.state.affect.get(channel, baseline), target)

        if relief > 0.0:
            self.state.affect["fear"] = _clamp(self.state.affect.get("fear", 0.04) - 0.30 * relief)
            self.state.affect["unease"] = _clamp(self.state.affect.get("unease", 0.04) - 0.34 * relief)

    def _appraise(self, event: WorldEvent, relation: RelationshipState, memories: list[MemoryRecord]) -> float:
        """Keep memory causally active without treating recall as a fresh injury.

        v0.5 permanently increased guardedness whenever a negative memory was
        retrieved. It also increased unease on every retrieval. Because important
        memories can be retrieved during an idle heartbeat, a remembered adverse
        event could re-injure the subject indefinitely even after its residual
        activation had decayed.

        v0.6 keeps the memory available to cognition and action selection, but
        removes the permanent guardedness increment caused by retrieval alone. On
        endogenous idle cycles it also removes the fresh unease increment. A new
        external encounter may still reactivate unease, which is a different causal
        event from merely remembering something while time passes.
        """
        negative = 0.0
        if memories:
            negative = max(0.0, -min(memory.valence for memory in memories[:3]))
        prediction_error = super()._appraise(event, relation, memories)
        if negative > 0.30:
            relation.guardedness = _clamp(relation.guardedness - 0.08 * negative)
            if event.kind == "endogenous":
                self.state.affect["unease"] = _clamp(
                    self.state.affect.get("unease", 0.0) - 0.10 * negative
                )

        if "repair" in event.tags:
            intensity = _clamp(event.intensity)
            relation.trust = _clamp(relation.trust + 0.06 * intensity)
            relation.guardedness = _clamp(relation.guardedness - 0.08 * intensity)
        return prediction_error

    def _candidates(self, event: WorldEvent, relation: RelationshipState, memories: list[MemoryRecord]) -> list[ActionCandidate]:
        rows = super()._candidates(event, relation, memories)
        if event.kind != "endogenous":
            return rows

        recent = self.state.recent_actions[-8:]
        adjusted: list[ActionCandidate] = []
        for candidate in rows:
            utility = candidate.utility
            repeats4 = sum(1 for action in recent[-4:] if action == candidate.name)
            if candidate.name == "seek_connection" and candidate.name in recent[-6:]:
                utility -= 0.42
            elif candidate.name in {"rest", "explore", "ask", "step_back"}:
                utility -= 0.10 * repeats4
            elif candidate.name == "wait":
                utility += 0.05
            adjusted.append(ActionCandidate(candidate.name, utility, candidate.reasons))
        return adjusted

    def step(self, event: WorldEvent, *, allow_inner_speech: bool = True) -> LivingStep:
        result = super().step(event, allow_inner_speech=allow_inner_speech)
        if event.kind == "endogenous":
            self._apply_endogenous_consequence(result.selected_action)
        return result

    def _apply_endogenous_consequence(self, action: str) -> None:
        """Let self-directed actions partly regulate the drives that selected them.

        Seeking connection does not imply that anyone replied, and exploration does
        not imply external success. The intention itself can nevertheless produce a
        limited refractory effect. Rest is the only endogenous action that restores
        energy; simply waiting no longer creates energy.
        """
        if action == "rest":
            self.state.needs["energy"] = _clamp(self.state.needs.get("energy", 0.5) + 0.16)
        elif action == "explore":
            self.state.needs["curiosity"] = _clamp(self.state.needs.get("curiosity", 0.3) - 0.16)
        elif action == "ask":
            self.state.needs["curiosity"] = _clamp(self.state.needs.get("curiosity", 0.3) - 0.08)
        elif action == "seek_connection":
            self.state.needs["affiliation"] = _clamp(self.state.needs.get("affiliation", 0.3) - 0.16)
            self.state.affect["loneliness"] = _clamp(self.state.affect.get("loneliness", 0.18) - 0.04)
