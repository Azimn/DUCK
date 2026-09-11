"""Opt-in Pretorius persona-seal organism for the DUCK v0.10 causal experiment."""
from __future__ import annotations

from .authoritative_organism_v010 import LivingDuck as CurrentLivingDuck
from .living import ActionCandidate, RelationshipState, WorldEvent
from .persona_neurodynamics_v010 import PretoriusPersonaSeal
from .persona_seal_model_v010 import (
    PERSONA_SEAL_STATE_SCHEMA,
    PERSONA_SEAL_VERSION,
    PRETORIUS_ORIGIN,
    PRETORIUS_ORIGIN_HASH,
    OriginNode,
    OriginEdge,
    PersonaSealOrigin,
    PersonaSealState,
    PersonaControlField,
)

class PersonaSealedLivingDuck(CurrentLivingDuck):
    """Opt-in DUCK organism with a Pretorius policy prior before final competition."""

    def __init__(
        self,
        *args,
        persona_seal: PretoriusPersonaSeal | None = None,
        persona_seal_state: PersonaSealState | None = None,
        **kwargs,
    ) -> None:
        if persona_seal is not None and persona_seal_state is not None:
            raise ValueError("provide persona_seal or persona_seal_state, not both")
        super().__init__(*args, **kwargs)
        self.persona_seal = persona_seal or PretoriusPersonaSeal(persona_seal_state)
        self.last_persona_field: PersonaControlField | None = None

    @property
    def persona_seal_state(self) -> PersonaSealState:
        return self.persona_seal.state

    def _apply_executive_selection(
        self,
        event: WorldEvent,
        relation: RelationshipState,
        memories,
        rows: list[ActionCandidate],
    ) -> list[ActionCandidate]:
        memory_tags = tuple(
            tag
            for memory in memories[:5]
            for tag in memory.tags
        )
        field = self.persona_seal.evaluate(
            event,
            relation,
            affect=self.state.affect,
            memory_tags=memory_tags,
        )
        self.last_persona_field = field
        adjusted = self.persona_seal.apply_candidates(rows, field)
        selected_rows = super()._apply_executive_selection(
            event,
            relation,
            memories,
            adjusted,
        )
        self._pending_executive_trace["persona_seal"] = field.to_developer_dict()
        return selected_rows

__all__ = [
    "PERSONA_SEAL_STATE_SCHEMA",
    "PERSONA_SEAL_VERSION",
    "PRETORIUS_ORIGIN",
    "PRETORIUS_ORIGIN_HASH",
    "OriginNode",
    "OriginEdge",
    "PersonaSealOrigin",
    "PersonaSealState",
    "PersonaControlField",
    "PretoriusPersonaSeal",
    "PersonaSealedLivingDuck",
]
