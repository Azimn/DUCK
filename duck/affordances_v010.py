"""Available possibilities carry costs and targets, never external utility."""
from dataclasses import dataclass
from enum import Enum
from .body_v010 import unit


class AffordanceSource(str, Enum):
    ENVIRONMENT = "environment"
    SOCIAL = "social"
    BODY = "body"
    INTERNAL = "internal"


@dataclass(frozen=True)
class Affordance:
    action: str
    source: AffordanceSource
    target: str | None = None
    effort: float = 0.0
    risk: float = 0.0
    complexity: float = 0.0
    novelty: float = 0.0
    social_exposure: float = 0.0

    def __post_init__(self):
        if not self.action or not self.action.replace("_", "").isalpha() or len(self.action) > 48:
            raise ValueError("action must be a short alphabetic action name")
        object.__setattr__(self, "source", AffordanceSource(self.source))
        if self.target is not None and (not isinstance(self.target, str) or len(self.target) > 160):
            raise ValueError("target must be a bounded string")
        for name in ("effort", "risk", "complexity", "novelty", "social_exposure"):
            object.__setattr__(self, name, unit(getattr(self, name)))


def grounded_affordances(percept, supplied=(), *, infer_social=True):
    rows = [Affordance("wait", AffordanceSource.INTERNAL), Affordance("rest", AffordanceSource.BODY)]
    if infer_social and percept.confidence >= 0.5 and ("person_present" in percept.features or
                                     percept.source not in {"self", "world", "system", ""}):
        rows.extend(Affordance(action, AffordanceSource.SOCIAL, target=percept.source,
                               social_exposure=0.4) for action in ("respond", "ask", "approach", "step_back"))
    rows.extend(supplied)
    if len(rows) > 64 or not all(isinstance(row, Affordance) for row in rows):
        raise ValueError("affordances must be at most 64 typed possibilities")
    return tuple(rows)
