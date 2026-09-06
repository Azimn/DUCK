"""Developer-visible mechanistic state.

Nothing in this module is automatically subject-accessible. Values here may be
numeric, statistical, implementation-specific, or otherwise unsuitable for the
simulated subject's first-person perspective.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping


@dataclass(frozen=True)
class RecognitionSignal:
    candidate: str
    confidence: float


@dataclass(frozen=True)
class MechanisticSnapshot:
    affect: Mapping[str, float] = field(default_factory=dict)
    relationship: Mapping[str, float] = field(default_factory=dict)
    prediction_error: float = 0.0
    recognition: RecognitionSignal | None = None
    action_tendency: str | None = None
    hidden_causes: Mapping[str, str] = field(default_factory=dict)
    introspectively_accessible_causes: frozenset[str] = frozenset()
