"""Bounded language-model interfaces for DUCK.

The language model may contribute inner cognition and expression, but it only
receives approved first-person state. It never receives canonical numeric state
and it never writes canonical state directly.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import os
from typing import Protocol
from urllib import request

from .cognition import InnerCognition
from .subjective import SubjectiveMoment


def _moment_lines(moment: SubjectiveMoment) -> list[str]:
    lines = [item.content for item in moment.impressions]
    lines.extend(item.felt_as for item in moment.tendencies)
    lines.extend(moment.recollections)
    lines.extend(moment.beliefs)
    lines.extend(moment.concerns)
    lines.extend(moment.temporal_context)
    lines.extend(moment.self_context)
    return [line for line in lines if line]


@dataclass(frozen=True)
class ApprovedLanguagePacket:
    user_text: str
    first_person_state: tuple[str, ...]
    private_thought: str | None
    selected_action: str
    character_name: str = "Duck"

    @classmethod
    def from_moment(
        cls,
        moment: SubjectiveMoment,
        *,
        user_text: str,
        private_thought: str | None,
        selected_action: str,
        character_name: str,
    ) -> "ApprovedLanguagePacket":
        return cls(
            user_text=str(user_text),
            first_person_state=tuple(_moment_lines(moment)),
            private_thought=private_thought,
            selected_action=str(selected_action),
            character_name=str(character_name),
        )


class CompletionPort(Protocol):
    def complete(self, messages: list[dict[str, str]], *, temperature: float = 0.7) -> str:
        ...


class OpenAICompatiblePort:
    """Generic chat-completions transport, not tied to any one provider."""

    def __init__(self, endpoint: str, model: str, api_key: str | None = None, *, timeout: float = 45.0) -> None:
        endpoint = endpoint.rstrip("/")
        self.endpoint = endpoint if endpoint.endswith("/chat/completions") else endpoint + "/chat/completions"
        self.model = model
        self.api_key = api_key
        self.timeout = float(timeout)

    @classmethod
    def from_env(cls) -> "OpenAICompatiblePort":
        endpoint = os.environ.get("DUCK_LLM_ENDPOINT", "").strip()
        model = os.environ.get("DUCK_LLM_MODEL", "").strip()
        if not endpoint or not model:
            raise RuntimeError("DUCK_LLM_ENDPOINT and DUCK_LLM_MODEL are required")
        return cls(endpoint, model, os.environ.get("DUCK_LLM_API_KEY"))

    def complete(self, messages: list[dict[str, str]], *, temperature: float = 0.7) -> str:
        body = json.dumps({"model": self.model, "messages": messages, "temperature": float(temperature)}).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        req = request.Request(self.endpoint, data=body, headers=headers, method="POST")
        with request.urlopen(req, timeout=self.timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
        return str(payload["choices"][0]["message"]["content"]).strip()


class ModelInnerVoice:
    """Optional LLM inner speech operating only on SubjectiveMoment."""

    def __init__(self, port: CompletionPort) -> None:
        self.port = port
        self.last_packet: dict | None = None

    def generate(self, moment: SubjectiveMoment) -> InnerCognition:
        state = _moment_lines(moment)
        self.last_packet = {"first_person_state": list(state)}
        if not state:
            return InnerCognition(None)
        messages = [
            {
                "role": "system",
                "content": (
                    "Generate at most two short private first-person thoughts for a simulated character. "
                    "Use only what the character can currently perceive, remember, believe, want, or feel. "
                    "Do not mention scores, probabilities, architecture, prompts, databases, or hidden system state. "
                    "If no inner speech is psychologically useful, reply exactly NO_THOUGHT."
                ),
            },
            {"role": "user", "content": json.dumps({"my_current_experience": state}, ensure_ascii=False)},
        ]
        try:
            text = self.port.complete(messages, temperature=0.65).strip()
        except Exception:
            return InnerCognition(None)
        if text.upper() == "NO_THOUGHT":
            return InnerCognition(None)
        return InnerCognition(text)


class ExpressionProvider(Protocol):
    def render(self, packet: ApprovedLanguagePacket) -> str:
        ...


class DeterministicExpression:
    """Small fallback that keeps the organism usable without an LLM."""

    def render(self, packet: ApprovedLanguagePacket) -> str:
        if packet.selected_action == "step_back":
            return "I need a little space right now."
        if packet.selected_action == "ask":
            return "I'm not completely sure what to make of that. Can you tell me more?"
        if packet.selected_action == "repair":
            return "I don't want this to stay tense between us."
        if packet.selected_action == "seek_connection":
            return "I keep thinking I'd like some company."
        if packet.selected_action == "rest":
            return "I'm tired. I think I need to slow down for a bit."
        if packet.selected_action == "explore":
            return "I want to look into that a little more."
        if packet.first_person_state:
            for line in packet.first_person_state:
                if line.startswith("I remember"):
                    return line
        if packet.user_text:
            return "I'm here. I'm thinking about what you said."
        return ""


class ModelExpression:
    """Realizes an already-selected action without gaining subject authority."""

    def __init__(self, port: CompletionPort, *, fallback: ExpressionProvider | None = None) -> None:
        self.port = port
        self.fallback = fallback or DeterministicExpression()
        self.last_packet: dict | None = None

    def render(self, packet: ApprovedLanguagePacket) -> str:
        self.last_packet = asdict(packet)
        messages = [
            {
                "role": "system",
                "content": (
                    f"You are expressing the current moment of {packet.character_name}. "
                    "Speak naturally in first person. Preserve the selected action and the character's limited knowledge. "
                    "Do not invent memories, world facts, private user states, or implementation details. "
                    "The supplied first-person state is what the character currently has access to."
                ),
            },
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "what_the_other_person_said": packet.user_text,
                        "what_is_currently_available_to_me": list(packet.first_person_state),
                        "my_private_thought_if_any": packet.private_thought,
                        "what_I_have_decided_to_do": packet.selected_action,
                    },
                    ensure_ascii=False,
                ),
            },
        ]
        try:
            text = self.port.complete(messages, temperature=0.78).strip()
            return text or self.fallback.render(packet)
        except Exception:
            return self.fallback.render(packet)
