"""Optional semantic interpretation as a bounded model proposal."""
from __future__ import annotations

import json
import re

from .language import CompletionPort
from .living import RuleEventInterpreter, WorldEvent

_ALLOWED_TAGS = {
    "social", "conversation", "threat", "conflict", "supportive", "commitment_language",
    "repair", "question", "praise", "rejection", "loss", "novel", "humor", "affection",
    "criticism", "request", "farewell", "greeting", "uncertainty", "surprise",
}


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, float(value)))


def _json_object(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end < start:
        raise ValueError("model did not return a JSON object")
    data = json.loads(text[start : end + 1])
    if not isinstance(data, dict):
        raise ValueError("semantic proposal must be an object")
    return data


class ModelEventInterpreter:
    """Let an LLM propose appraisal-relevant semantics without subject authority.

    The model sees only the current utterance and source. It cannot see canonical
    state, memories, relationship scores, world truth, or hidden diagnostics. Its
    proposal is schema-checked, clamped, and merged with the deterministic parser.
    It cannot create world facts.
    """

    def __init__(self, port: CompletionPort, *, fallback: RuleEventInterpreter | None = None) -> None:
        self.port = port
        self.fallback = fallback or RuleEventInterpreter()
        self.last_proposal: dict | None = None

    def interpret(self, text: str, *, source: str = "user") -> WorldEvent:
        baseline = self.fallback.interpret(text, source=source)
        messages = [
            {
                "role": "system",
                "content": (
                    "Classify one utterance for a character-simulation appraisal layer. Return JSON only with "
                    "keys tags, valence, intensity. tags must be chosen only from: "
                    + ", ".join(sorted(_ALLOWED_TAGS))
                    + ". valence is -1 to 1. intensity is 0 to 1. Do not infer hidden world facts, memories, identity, or user mental state."
                ),
            },
            {"role": "user", "content": json.dumps({"source": source, "utterance": text}, ensure_ascii=False)},
        ]
        try:
            proposal = _json_object(self.port.complete(messages, temperature=0.15))
            tags = [str(tag).lower() for tag in proposal.get("tags", []) if str(tag).lower() in _ALLOWED_TAGS]
            merged_tags = tuple(dict.fromkeys((*baseline.tags, *tags)))
            valence = _clamp(proposal.get("valence", baseline.valence), -1.0, 1.0)
            intensity = _clamp(proposal.get("intensity", baseline.intensity), 0.0, 1.0)
            self.last_proposal = {"tags": list(merged_tags), "valence": valence, "intensity": intensity}
            return WorldEvent(
                kind=baseline.kind,
                source=source,
                text=text.strip(),
                tags=merged_tags,
                valence=valence,
                intensity=intensity,
                world_facts=(),
                perceived=True,
            )
        except Exception:
            self.last_proposal = None
            return baseline
