"""Selective executive-cognition contracts for MicroPsiDUCK v0.10.

The mechanistic cognitive field is transient and developer-visible. An executive
provider never receives that field. It receives only an ExperientialFrame and may
return a bounded proposal that the canonical runtime is free to accept or reject.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import Protocol

from .motivated_cognition import CognitiveModulation
from .subjective import ExperientialFrame, validate_experiential_prose

_ACTION_RE = re.compile(r"^[a-z][a-z0-9_]*$")


@dataclass(frozen=True)
class CognitiveField:
    """Transient mechanistic workspace assembled before action selection.

    This object may contain raw scores, IDs, tags, and modulation parameters. It is
    therefore forbidden from crossing the experiential firewall or becoming a
    private-cognition/provider input.
    """

    tick: int
    event_kind: str
    event_tags: tuple[str, ...]
    dominant_motive_id: str | None
    active_motive_ids: tuple[str, ...]
    activated_memory_ids: tuple[str, ...]
    candidate_utilities: tuple[tuple[str, float], ...]
    automatic_action: str
    modulation: CognitiveModulation

    def to_developer_dict(self) -> dict[str, object]:
        return {
            "tick": self.tick,
            "event_kind": self.event_kind,
            "event_tags": list(self.event_tags),
            "dominant_motive_id": self.dominant_motive_id,
            "active_motive_ids": list(self.active_motive_ids),
            "activated_memory_ids": list(self.activated_memory_ids),
            "candidate_utilities": [
                {"action": action, "utility": float(utility)}
                for action, utility in self.candidate_utilities
            ],
            "automatic_action": self.automatic_action,
            "modulation": asdict(self.modulation),
        }


@dataclass(frozen=True)
class ExecutiveProposal:
    """A non-authoritative proposal returned by optional executive cognition.

    ``action`` is a requested affordance name and is validated against the current
    canonical candidate set. ``intention`` is optional first-person prose for future
    planning integration. v0.10 does not automatically persist it or grant it state
    authority.
    """

    action: str | None = None
    intention: str | None = None

    def __post_init__(self) -> None:
        if self.action is not None:
            action = self.action.strip().lower()
            if not action or not _ACTION_RE.fullmatch(action):
                raise ValueError("executive action must be a canonical action label")
            object.__setattr__(self, "action", action)
        if self.intention is not None:
            intention = self.intention.strip()
            validate_experiential_prose((intention,))
            object.__setattr__(self, "intention", intention or None)


class ExecutiveCognitionProvider(Protocol):
    """Optional executive service operating only on first-person experience."""

    def propose(self, experience: ExperientialFrame) -> ExecutiveProposal:
        ...
