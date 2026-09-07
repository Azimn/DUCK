"""Endogenous opportunity pursuit for the DUCK v0.8 agency candidate.

v0.7 can regulate itself during quiet time, but most meaningful goals still arrive
from the current external event. v0.8 adds a narrow prospective-memory mechanism:
an experienced or explicitly registered opportunity can later become the content of
an endogenous cycle and bias action without a new user reminder.

The mechanism remains below the language boundary. Opportunity state is stored as
ordinary autobiographical/self-reflective memory with provenance and tags. No LLM
is required to decide that an opportunity has become salient.
"""
from __future__ import annotations

from typing import Iterable

from .living import ActionCandidate, MemoryProvenance, MemoryRecord, RelationshipState, WorldEvent, _clamp
from .living_v07 import LivingDuck as LifeSimLivingDuck


class LivingDuck(LifeSimLivingDuck):
    """v0.8 candidate with bounded prospective opportunity pursuit."""

    def register_opportunity(
        self,
        text: str,
        *,
        tags: Iterable[str] = (),
        importance: float = 0.7,
        source: str = "self",
    ) -> MemoryRecord:
        """Store a prospective concern that may later drive an endogenous action.

        This does not execute an action and does not manufacture an outcome. It
        records that the subject has something it may want to revisit when quiet
        time and motivation make that concern salient.
        """
        normalized_tags = tuple(dict.fromkeys(("opportunity", "prospective", *(str(tag).lower() for tag in tags))))
        return self.state.add_memory(
            text,
            tags=normalized_tags,
            valence=0.15,
            arousal=0.30,
            importance=_clamp(importance),
            provenance=MemoryProvenance.SELF_REFLECTION,
            source=source,
            confidence=1.0,
        )

    def _pending_opportunity(self) -> MemoryRecord | None:
        candidates = [
            memory
            for memory in self.state.memories
            if "opportunity" in memory.tags and "opportunity_acted" not in memory.tags
        ]
        if not candidates:
            return None
        candidates.sort(key=lambda memory: (memory.importance, memory.tick), reverse=True)
        return candidates[0]

    def heartbeat(self, *, allow_inner_speech: bool = True):
        opportunity = self._pending_opportunity()
        curiosity = self.state.needs.get("curiosity", 0.35)
        energy = self.state.needs.get("energy", 0.85)

        if opportunity is not None and energy >= 0.25 and (curiosity >= 0.40 or opportunity.importance >= 0.78):
            event = WorldEvent(
                kind="endogenous",
                source="self",
                text=opportunity.text,
                tags=tuple(dict.fromkeys(("idle", "time_passed", "opportunity_active", *opportunity.tags))),
                valence=0.08,
                intensity=max(0.15, min(0.60, opportunity.importance * 0.60)),
                perceived=False,
            )
            result = self.step(event, allow_inner_speech=allow_inner_speech)
            if result.selected_action in {"explore", "ask"}:
                opportunity.tags = tuple(dict.fromkeys((*opportunity.tags, "opportunity_acted")))
                self.state.needs["curiosity"] = _clamp(self.state.needs.get("curiosity", 0.35) - 0.08)
            return result

        return super().heartbeat(allow_inner_speech=allow_inner_speech)

    def _candidates(self, event: WorldEvent, relation: RelationshipState, memories: list[MemoryRecord]) -> list[ActionCandidate]:
        rows = super()._candidates(event, relation, memories)
        if event.kind != "endogenous" or "opportunity_active" not in event.tags:
            return rows

        opportunity = self._pending_opportunity()
        importance = opportunity.importance if opportunity is not None else 0.5
        recent = self.state.recent_actions[-5:]
        adjusted: list[ActionCandidate] = []
        for candidate in rows:
            utility = candidate.utility
            if candidate.name == "explore":
                utility += 0.24 + 0.28 * importance
                if "explore" in recent[-2:]:
                    utility -= 0.10
            elif candidate.name == "ask":
                utility += 0.06 + 0.10 * importance
            elif candidate.name == "wait":
                utility -= 0.08 * importance
            adjusted.append(ActionCandidate(candidate.name, utility, candidate.reasons))
        return adjusted
