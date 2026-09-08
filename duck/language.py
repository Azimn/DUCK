"""Bounded language interfaces for DUCK.

Language providers may read approved private experience, but the packet crossing
into them contains only prose representations of that experience. Numeric state,
implementation tags, IDs, scores, and canonical subject structures never cross the
renderer boundary.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import os
from typing import Protocol
from urllib import request

from .cognition import InnerCognition
from .subjective import (
    ExperientialFrame,
    PrivateInteriorState,
    SubjectiveMoment,
    validate_experiential_prose,
)


def _moment_lines(moment: SubjectiveMoment) -> tuple[str, ...]:
    lines: list[str] = [item.content for item in moment.impressions]
    lines.extend(item.felt_as for item in moment.tendencies)
    lines.extend(moment.recollections)
    lines.extend(moment.beliefs)
    lines.extend(moment.concerns)
    lines.extend(moment.temporal_context)
    lines.extend(moment.self_context)
    return validate_experiential_prose(tuple(line for line in lines if line))


def _action_intent(action: str) -> str:
    action = str(action).strip()
    if not action:
        return "I haven't decided to do anything outwardly yet."
    if action == "step_back":
        return "I have decided to give myself some space."
    if action == "approach":
        return "I have decided to get a little closer."
    if action == "wait":
        return "I have decided to wait and see."
    if action == "ask":
        return "I have decided to ask for more information."
    if action == "repair":
        return "I have decided to try to repair this."
    if action == "seek_connection":
        return "I have decided to seek some connection."
    if action == "rest":
        return "I have decided to slow down and rest."
    if action == "explore":
        return "I have decided to look into this further."
    if action == "respond":
        return "I have decided to respond."
    return f"I have decided to {action.replace('_', ' ')}."


@dataclass(frozen=True)
class ApprovedLanguagePacket:
    """Renderer input after the experiential firewall.

    `user_text` is public external input. Every field derived from the organism's
    private interior is prose. No machine action identifier is retained after the
    packet is constructed.
    """

    user_text: str
    first_person_state: tuple[str, ...]
    private_thought: str | None
    action_intent: str
    character_name: str = "Duck"

    def __post_init__(self) -> None:
        object.__setattr__(self, "first_person_state", validate_experiential_prose(tuple(self.first_person_state)))
        object.__setattr__(self, "action_intent", validate_experiential_prose((self.action_intent,))[0])
        if self.private_thought is not None:
            thought = validate_experiential_prose((self.private_thought,))[0]
            object.__setattr__(self, "private_thought", thought)

    @classmethod
    def from_experience(
        cls,
        experience: ExperientialFrame,
        *,
        user_text: str,
        private_thought: str | None,
        selected_action: str,
        character_name: str,
    ) -> "ApprovedLanguagePacket":
        if not isinstance(experience, ExperientialFrame):
            raise TypeError("renderer input requires ExperientialFrame")
        return cls(
            user_text=str(user_text),
            first_person_state=experience.prose,
            private_thought=private_thought,
            action_intent=_action_intent(selected_action),
            character_name=str(character_name),
        )

    @classmethod
    def from_private_interior(
        cls,
        interior: PrivateInteriorState,
        *,
        user_text: str,
        selected_action: str,
        character_name: str,
    ) -> "ApprovedLanguagePacket":
        if not isinstance(interior, PrivateInteriorState):
            raise TypeError("renderer private context requires PrivateInteriorState")
        return cls.from_experience(
            interior.experiential_frame(),
            user_text=user_text,
            private_thought=interior.private_thought,
            selected_action=selected_action,
            character_name=character_name,
        )

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
        """v0.9 compatibility constructor that strips diagnostic metadata."""
        return cls.from_experience(
            ExperientialFrame(_moment_lines(moment)),
            user_text=user_text,
            private_thought=private_thought,
            selected_action=selected_action,
            character_name=character_name,
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
    """Optional LLM inner speech operating on approved experiential prose.

    v0.10 supplies ExperientialFrame directly. SubjectiveMoment conversion remains
    only so the promoted v0.9 runtime can continue its regression suite unchanged.
    """

    def __init__(self, port: CompletionPort) -> None:
        self.port = port
        self.last_packet: dict | None = None

    def generate(self, experience: ExperientialFrame | SubjectiveMoment) -> InnerCognition:
        if isinstance(experience, SubjectiveMoment):
            experience = ExperientialFrame(_moment_lines(experience))
        if not isinstance(experience, ExperientialFrame):
            raise TypeError("private cognition requires experiential state")
        state = list(experience.prose)
        self.last_packet = {"first_person_state": state}
        if not state:
            return InnerCognition(None)
        messages = [
            {
                "role": "system",
                "content": (
                    "Generate at most two short private first-person thoughts for a simulated character. "
                    "Use only the supplied first-person experience. Do not mention scores, probabilities, architecture, "
                    "prompts, databases, hidden machinery, or implementation state. If no inner speech is psychologically "
                    "useful, reply exactly NO_THOUGHT."
                ),
            },
            {"role": "user", "content": json.dumps({"my_current_experience": state}, ensure_ascii=False)},
        ]
        try:
            text = self.port.complete(messages, temperature=0.65).strip()
            validate_experiential_prose((text,))
        except Exception:
            return InnerCognition(None)
        if text.upper() == "NO_THOUGHT":
            return InnerCognition(None)
        return InnerCognition(text)


class ExpressionProvider(Protocol):
    def render(self, packet: ApprovedLanguagePacket) -> str:
        ...


class DeterministicExpression:
    """Small fallback that renders public behavior from experiential prose."""

    def render(self, packet: ApprovedLanguagePacket) -> str:
        intent = packet.action_intent.lower()
        if "give myself some space" in intent:
            return "I need a little space right now."
        if "ask for more information" in intent:
            return "I'm not completely sure what to make of that. Can you tell me more?"
        if "repair this" in intent:
            return "I don't want this to stay tense between us."
        if "seek some connection" in intent:
            return "I keep thinking I'd like some company."
        if "slow down and rest" in intent:
            return "I'm tired. I think I need to slow down for a bit."
        if "look into this further" in intent:
            return "I want to look into that a little more."
        if packet.first_person_state:
            for line in packet.first_person_state:
                if line.startswith("I remember"):
                    return line
        if packet.user_text:
            return "I'm here. I'm thinking about what you said."
        return ""


class ModelExpression:
    """Realizes public expression without gaining subject authority."""

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
                    "Speak naturally in first person. Preserve the supplied public action intent and limited knowledge. "
                    "The private thought is context for expression, not a hidden-state report. Do not describe it as a "
                    "private variable, quote it merely because it was supplied, or reveal implementation details. "
                    "Do not invent memories, world facts, private user states, or machinery."
                ),
            },
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "what_the_other_person_said": packet.user_text,
                        "what_is_currently_available_to_me": list(packet.first_person_state),
                        "private_context_for_expression": packet.private_thought,
                        "what_I_have_decided_to_do": packet.action_intent,
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
