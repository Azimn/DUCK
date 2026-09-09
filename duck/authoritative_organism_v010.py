"""Public v0.10 organism boundary enforcing WORLD != SUBJECT authority.

Historical DUCK runtimes stored authoritative ``world_facts`` inside ``SubjectState``.
MicroPsiDUCK v0.10 preserves that field only for historical serialization
compatibility. The current public organism does not treat it as an authority store.
External truth belongs to the host-owned ``EnvironmentDynamicsState``.
"""
from __future__ import annotations

from .living import WorldEvent
from .predictive_organism_v010 import LivingDuck as PredictiveLivingDuck


class LivingDuck(PredictiveLivingDuck):
    """Current public organism with no authoritative external truth in SubjectState."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if self.state.pending_action is not None:
            self.state.pending_action.tags = tuple(self.state.pending_action.tags)
        # A host opening historical state migrates these facts to environment state
        # before construction. Direct current-organism construction has no external
        # world authority, so legacy truth cannot remain canonical in the subject.
        self.state.world_facts.clear()

    def set_world_fact(self, key: str, text: str, *, perceived: bool = False, source: str = "world") -> None:
        del key, text, perceived, source
        raise RuntimeError(
            "MicroPsiDUCK v0.10 external truth belongs to the host environment; "
            "use PersistentDuckHost.set_world_fact or deliver a WorldEvent perception"
        )

    def step(self, event: WorldEvent, *, allow_inner_speech: bool = True):
        """Allow perceived evidence to update subject belief without retaining world truth.

        Historical substrate code may temporarily copy ``event.world_facts`` into the
        inherited SubjectState during the step. The current authority layer clears
        that compatibility field before and after the inherited cycle. Perceived
        facts still produce ordinary memories/beliefs through the historical evidence
        path, and expectation evaluation still sees the event facts before they are
        discarded from subject authority.
        """

        self.state.world_facts.clear()
        try:
            return super().step(event, allow_inner_speech=allow_inner_speech)
        finally:
            self.state.world_facts.clear()


__all__ = ["LivingDuck"]
