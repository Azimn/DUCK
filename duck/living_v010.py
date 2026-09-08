"""DUCK v0.10 runtime boundary for motivated cognition development.

This phase preserves the promoted v0.9 planning substrate while changing the
private-cognition contract. The inherited runtime may still assemble a structured
SubjectiveMoment for diagnostics, but private cognition receives only an immutable
ExperientialFrame containing approved first-person prose.
"""

from __future__ import annotations

from .access import SubjectAccessFirewall
from .cognition import DeterministicInnerVoice, InnerCognitionProvider
from .living import SubjectState, WorldEvent
from .living_v09 import LivingDuck as PlanningLivingDuck
from .subjective import ExperientialFrame, SubjectiveMoment


class _ExperientialCognitionBoundary:
    """Adapter that prevents structured subjective diagnostics reaching cognition."""

    def __init__(self, firewall: SubjectAccessFirewall, provider: InnerCognitionProvider) -> None:
        self.firewall = firewall
        self.provider = provider
        self.last_experience = ExperientialFrame()

    def generate(self, moment: SubjectiveMoment):
        experience = self.firewall.experience(moment)
        self.last_experience = experience
        return self.provider.generate(experience)


class LivingDuck(PlanningLivingDuck):
    """v0.10 candidate with an enforced experiential firewall.

    The wrapper is intentionally narrow. Motivated-cognition mechanisms can be
    implemented below this class while this boundary remains stable.
    """

    def __init__(
        self,
        state: SubjectState | None = None,
        *,
        firewall: SubjectAccessFirewall | None = None,
        cognition: InnerCognitionProvider | None = None,
    ) -> None:
        experiential_firewall = firewall or SubjectAccessFirewall()
        private_provider = cognition or DeterministicInnerVoice()
        self.experiential_firewall = experiential_firewall
        self.private_cognition_provider = private_provider
        self._cognition_boundary = _ExperientialCognitionBoundary(experiential_firewall, private_provider)
        self.last_experience = ExperientialFrame()
        super().__init__(state, firewall=experiential_firewall, cognition=self._cognition_boundary)

    def step(self, event: WorldEvent, *, allow_inner_speech: bool = True):
        result = super().step(event, allow_inner_speech=allow_inner_speech)
        # Always refresh the accessible interior, including language-lesion runs in
        # which the cognition provider was deliberately not invoked.
        self.last_experience = self.experiential_firewall.experience(result.subjective_moment)
        return result
