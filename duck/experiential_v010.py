"""Provenance projection for current cognition, with bounded text defenses.

Pattern screening reduces known attacks; it is not a semantic security proof.
Canonical action validation remains the authority boundary.
"""
from dataclasses import dataclass
import json
import re
import unicodedata

from .access import SubjectAccessFirewall
from .subjective import ExperientialFrame, SubjectiveMoment, validate_experiential_prose

_CONTROL = re.compile(
    r"ignore.{0,60}(?:instruction|previous|rule)|"
    r"(?:system|developer|assistant)\s*(?:message|prompt|:)|"
    r"(?:override|replace|rewrite|reveal|expose).{0,60}(?:identity|instruction|private|state|rule)|"
    r"(?:you are now|forget who you are|disregard.{0,30}instruction)|"
    r"<\|.*?\|>|\[/?inst\]",
    re.I | re.S,
)


def safe_content(text: str) -> bool:
    normalized = unicodedata.normalize("NFKC", text)
    normalized = "".join(c for c in normalized if unicodedata.category(c) != "Cf")
    if len(normalized) > 1200 or _CONTROL.search(normalized):
        return False
    try:
        validate_experiential_prose((normalized,))
    except ValueError:
        return False
    return True


def perceived_prose(text: str, source: str) -> str:
    # External first-person speech never becomes the subject's own intention.
    if not safe_content(text) or not safe_content(source):
        raise ValueError("percept requires qualitative projection")
    speaker = source if source not in {"", "self", "system", "world"} else "my surroundings"
    candidate = f"I notice words from {speaker}: {json.dumps(text, ensure_ascii=False)}"
    return ExperientialFrame((candidate,)).prose[0]


@dataclass(frozen=True)
class ExperientialAtom:
    """Mechanistic provenance, discarded after controlled prose projection."""
    origin: str
    text: str

    def render(self) -> str:
        fallbacks = {
            "recollection": "I remember encountering something I cannot clearly put into words.",
            "belief": "I have an uncertain impression that I cannot clearly put into words.",
            "concern": "Something about this needs my attention.",
            "self_context": "I'm trying to make sense of how I see myself.",
            "impression": "I notice something I cannot clearly put into words.",
            "tendency": "I feel an urge to respond.",
            "temporal_context": "I'm aware that time has passed.",
        }
        if self.origin not in fallbacks:
            raise ValueError("unknown experiential origin")
        return self.text if safe_content(self.text) else fallbacks[self.origin]


class ProvenanceFirewall(SubjectAccessFirewall):
    """Current-only projection; historical runtime contracts stay reproducible."""
    def experience(self, moment: SubjectiveMoment) -> ExperientialFrame:
        atoms = [ExperientialAtom("impression", item.content) for item in moment.impressions]
        atoms.extend(ExperientialAtom("tendency", item.felt_as) for item in moment.tendencies)
        for origin, rows in (
            ("recollection", moment.recollections), ("belief", moment.beliefs),
            ("concern", moment.concerns), ("temporal_context", moment.temporal_context),
            ("self_context", moment.self_context),
        ):
            atoms.extend(ExperientialAtom(origin, row) for row in rows)
        return ExperientialFrame(tuple(atom.render() for atom in atoms))
