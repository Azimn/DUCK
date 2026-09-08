"""Subject-accessible representations and private experiential persistence.

Structured subjective diagnostics may remain useful inside the simulator, but the
actual cognitive access boundary is ExperientialFrame. It contains only approved
first-person experiential prose. Numeric telemetry, implementation tags, IDs,
weights, scores, and other mechanistic representations must not cross that
boundary.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re


PRIVATE_INTERIOR_SCHEMA_VERSION = "duck.private-interior.v1"


class Intensity(str, Enum):
    FAINT = "faint"
    MILD = "mild"
    MODERATE = "moderate"
    STRONG = "strong"
    OVERWHELMING = "overwhelming"


class Certainty(str, Enum):
    POSSIBLE = "possible"
    PLAUSIBLE = "plausible"
    LIKELY = "likely"
    CLEAR = "clear"


@dataclass(frozen=True)
class FirstPersonImpression:
    channel: str
    content: str
    intensity: Intensity
    certainty: Certainty = Certainty.CLEAR


@dataclass(frozen=True)
class AccessibleTendency:
    action: str
    felt_as: str


@dataclass(frozen=True)
class SubjectiveMoment:
    """Internal structured projection used to assemble experience.

    This object is diagnostic scaffolding, not the private-cognition contract.
    Private cognition and expression must receive ExperientialFrame instead.
    """

    impressions: tuple[FirstPersonImpression, ...] = ()
    tendencies: tuple[AccessibleTendency, ...] = ()
    recollections: tuple[str, ...] = ()
    beliefs: tuple[str, ...] = ()
    concerns: tuple[str, ...] = ()
    temporal_context: tuple[str, ...] = ()
    self_context: tuple[str, ...] = ()


_TELEMETRY_PATTERNS = (
    re.compile(r"\b\d+\.\d+\b"),
    re.compile(r"\b\d+(?:\.\d+)?%\b"),
    re.compile(r"\b(?:activation|edge weight|node id|route score|retrieval score|motive strength|need magnitude|latent vector|telemetry)\b", re.I),
    re.compile(r"\b(?:concern_id|plan_id|memory_id|action_id)\s*[:=]", re.I),
    re.compile(r"\b(?:pc_|pl_|m\d{6}\b|a-[0-9]+-[0-9a-f]+\b)"),
    re.compile(r"\b[a-z_][a-z0-9_]*\s*=\s*-?\d", re.I),
)


def validate_experiential_prose(lines: tuple[str, ...]) -> tuple[str, ...]:
    """Validate the prose-only data contract crossing the experiential firewall."""

    cleaned: list[str] = []
    for raw in lines:
        if not isinstance(raw, str):
            raise TypeError("experiential state may contain prose strings only")
        text = raw.strip()
        if not text:
            continue
        for pattern in _TELEMETRY_PATTERNS:
            if pattern.search(text):
                raise ValueError(f"mechanistic telemetry cannot cross experiential firewall: {text!r}")
        cleaned.append(text)
    return tuple(dict.fromkeys(cleaned))


@dataclass(frozen=True)
class ExperientialFrame:
    """The complete data contract available to private cognition.

    There are intentionally no channels, scores, tags, IDs, magnitudes, enums, or
    other machine-readable state fields here. The character can experience the
    consequences of substrate state, but cannot inspect the machinery producing
    those consequences.
    """

    prose: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "prose", validate_experiential_prose(tuple(self.prose)))


@dataclass(frozen=True)
class PrivateInteriorState:
    """Versioned durable record of the character's private interior.

    Schema metadata is host-side persistence metadata. It is never included in an
    ExperientialFrame and therefore is not introspectively accessible.
    """

    schema_version: str = PRIVATE_INTERIOR_SCHEMA_VERSION
    experience: tuple[str, ...] = ()
    private_thought: str | None = None

    def __post_init__(self) -> None:
        if self.schema_version != PRIVATE_INTERIOR_SCHEMA_VERSION:
            raise ValueError(f"unsupported private interior schema: {self.schema_version}")
        object.__setattr__(self, "experience", validate_experiential_prose(tuple(self.experience)))
        if self.private_thought is not None:
            thought = self.private_thought.strip()
            validate_experiential_prose((thought,))
            object.__setattr__(self, "private_thought", thought or None)

    @classmethod
    def capture(cls, frame: ExperientialFrame, private_thought: str | None) -> "PrivateInteriorState":
        return cls(experience=frame.prose, private_thought=private_thought)

    def experiential_frame(self) -> ExperientialFrame:
        return ExperientialFrame(self.experience)

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "experience": list(self.experience),
            "private_thought": self.private_thought,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "PrivateInteriorState":
        return cls(
            schema_version=str(data.get("schema_version", "")),
            experience=tuple(str(x) for x in data.get("experience", []) or []),
            private_thought=(str(data["private_thought"]) if data.get("private_thought") else None),
        )
