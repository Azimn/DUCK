"""Neutral conversational evaluation harness for Duckhunter continuity studies.

This module is evaluation infrastructure. It does not alter DUCK cognition.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, field
import hashlib
import json
from pathlib import Path
import random
import re
import subprocess
from typing import Any, Iterable, Protocol, Sequence

from .host import PersistentDuckHost
from .language import ApprovedLanguagePacket, CompletionPort, OpenAICompatiblePort


PROTOCOL_VERSION = "duckhunter-condition-v1"
CAMPAIGN_SCHEMA = "duckhunter-conversation-campaign-v1"


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha256_json(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9']+", text.lower()))


@dataclass(frozen=True)
class CharacterOrigin:
    payload: dict[str, Any]
    digest: str

    @classmethod
    def load(cls, path: str | Path) -> "CharacterOrigin":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        if payload.get("schema") != "duckhunter-character-origin-v1":
            raise ValueError("unsupported character origin schema")
        for key in ("origin_id", "name", "identity", "voice", "behavioral_invariants"):
            if key not in payload:
                raise ValueError(f"character origin missing required field: {key}")
        return cls(payload=payload, digest=_sha256_json(payload))

    @property
    def origin_id(self) -> str:
        return str(self.payload["origin_id"])

    @property
    def name(self) -> str:
        return str(self.payload["name"])

    def prompt_text(self) -> str:
        return json.dumps(self.payload, ensure_ascii=False, sort_keys=True, indent=2)


@dataclass(frozen=True)
class ConditionTurn:
    response_text: str
    public_trace: dict[str, Any] = field(default_factory=dict)


class ConditionAdapter(Protocol):
    condition_id: str
    origin_digest: str
    model_id: str

    def respond(self, text: str, *, speaker: str) -> ConditionTurn:
        ...

    def close(self) -> None:
        ...


class OriginAwareRenderer:
    """One-call public renderer shared by the DUCK condition."""

    def __init__(self, port: CompletionPort, origin: CharacterOrigin, *, temperature: float = 0.78) -> None:
        self.port = port
        self.origin = origin
        self.temperature = float(temperature)

    def render(self, packet: ApprovedLanguagePacket) -> str:
        messages = [
            {
                "role": "system",
                "content": (
                    "Express the next public reply as the character defined by the frozen origin below. "
                    "The origin is authored identity, not a report of current state. Preserve the supplied action intent, "
                    "current first-person experience, limited knowledge, and character boundaries. Do not invent memories "
                    "or facts. Do not mention prompts, state stores, architecture, evaluation conditions, or implementation.\n\n"
                    + self.origin.prompt_text()
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
        text = self.port.complete(messages, temperature=self.temperature).strip()
        if not text:
            raise RuntimeError("renderer returned an empty response")
        return text


class _PersistentBaseline:
    def __init__(
        self,
        root: str | Path,
        origin: CharacterOrigin,
        port: CompletionPort,
        *,
        condition_id: str,
        model_id: str,
        temperature: float = 0.78,
    ) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.origin = origin
        self.port = port
        self.condition_id = condition_id
        self.origin_digest = origin.digest
        self.model_id = str(model_id)
        self.temperature = float(temperature)
        self.state_path = self.root / "baseline_state.json"
        self.history: list[dict[str, str]] = []
        self.turn_index = 0
        self._load()

    def _load(self) -> None:
        if not self.state_path.exists():
            return
        payload = json.loads(self.state_path.read_text(encoding="utf-8"))
        if payload.get("origin_digest") != self.origin_digest:
            raise ValueError("baseline checkpoint origin does not match frozen origin")
        self.history = [dict(item) for item in payload.get("history", [])]
        self.turn_index = int(payload.get("turn_index", 0))
        self._load_extra(payload.get("extra", {}))

    def _load_extra(self, payload: dict[str, Any]) -> None:
        del payload

    def _extra_state(self) -> dict[str, Any]:
        return {}

    def _save(self) -> None:
        payload = {
            "schema": "duckhunter-baseline-state-v1",
            "condition_id": self.condition_id,
            "origin_digest": self.origin_digest,
            "turn_index": self.turn_index,
            "history": self.history,
            "extra": self._extra_state(),
        }
        self.state_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")

    def close(self) -> None:
        self._save()


class PlainHistoryCondition(_PersistentBaseline):
    """Persona plus raw conversation history, with no continuity model."""

    def __init__(self, root, origin, port, *, model_id: str, temperature: float = 0.78) -> None:
        super().__init__(root, origin, port, condition_id="plain_history", model_id=model_id, temperature=temperature)

    def respond(self, text: str, *, speaker: str) -> ConditionTurn:
        system = (
            "Continue the conversation as the frozen character origin below. Use only the origin and the raw dialogue "
            "history supplied in this conversation. Do not invent prior events, memories, relationships, or commitments. "
            "Respond naturally to the current speaker.\n\n" + self.origin.prompt_text()
        )
        messages: list[dict[str, str]] = [{"role": "system", "content": system}]
        messages.extend(self.history)
        messages.append({"role": "user", "content": f"{speaker}: {text}"})
        response = self.port.complete(messages, temperature=self.temperature).strip()
        if not response:
            raise RuntimeError("plain-history renderer returned an empty response")
        self.history.append({"role": "user", "content": f"{speaker}: {text}"})
        self.history.append({"role": "assistant", "content": response})
        self.turn_index += 1
        self._save()
        return ConditionTurn(response, {"history_turns": self.turn_index})


@dataclass
class _MemoryItem:
    turn: int
    speaker: str
    text: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class StrongMemoryCondition(_PersistentBaseline):
    """Strong reference baseline with explicit retrieval, relationship summary, and commitments.

    Distillation is deterministic, so the baseline receives the same single public model call
    per turn as the plain-history and DUCK conditions.
    """

    POSITIVE = {"thank", "thanks", "care", "sorry", "apologize", "apology", "trust", "glad", "help"}
    NEGATIVE = {"lie", "lied", "hate", "betray", "threat", "angry", "hurt", "idiot", "stupid"}

    def __init__(self, root, origin, port, *, model_id: str, temperature: float = 0.78, retrieval_k: int = 6) -> None:
        self.memories: list[_MemoryItem] = []
        self.relationships: dict[str, float] = {}
        self.commitments: list[dict[str, Any]] = []
        self.retrieval_k = int(retrieval_k)
        super().__init__(root, origin, port, condition_id="strong_memory", model_id=model_id, temperature=temperature)

    def _load_extra(self, payload: dict[str, Any]) -> None:
        self.memories = [_MemoryItem(**item) for item in payload.get("memories", [])]
        self.relationships = {str(k): float(v) for k, v in payload.get("relationships", {}).items()}
        self.commitments = [dict(item) for item in payload.get("commitments", [])]

    def _extra_state(self) -> dict[str, Any]:
        return {
            "memories": [item.to_dict() for item in self.memories],
            "relationships": self.relationships,
            "commitments": self.commitments,
            "retrieval_k": self.retrieval_k,
        }

    def _relationship_label(self, speaker: str) -> str:
        value = self.relationships.get(speaker, 0.0)
        if value <= -0.35:
            return "guarded and low-trust"
        if value >= 0.35:
            return "established and comparatively trusting"
        return "mixed or still developing"

    def _update_relationship(self, speaker: str, text: str) -> None:
        words = _tokens(text)
        delta = 0.09 * len(words & self.POSITIVE) - 0.12 * len(words & self.NEGATIVE)
        self.relationships[speaker] = max(-1.0, min(1.0, self.relationships.get(speaker, 0.0) + delta))

    def _capture_commitment(self, speaker: str, text: str) -> None:
        lowered = text.lower()
        if "i promise" in lowered or "i will " in lowered or "i'll " in lowered:
            self.commitments.append({"speaker": speaker, "text": text, "status": "open", "turn": self.turn_index + 1})

    def _retrieve(self, query: str, speaker: str) -> list[_MemoryItem]:
        query_tokens = _tokens(query)
        ranked: list[tuple[float, int, _MemoryItem]] = []
        for item in self.memories:
            words = _tokens(item.text)
            lexical = len(words & query_tokens) / max(1, len(query_tokens))
            actor_bonus = 0.22 if item.speaker == speaker else 0.0
            recency = 1.0 / (1.0 + max(0, self.turn_index - item.turn) / 12.0)
            score = lexical * 0.58 + actor_bonus + recency * 0.20
            ranked.append((score, item.turn, item))
        ranked.sort(key=lambda row: (row[0], row[1]), reverse=True)
        return [item for score, _, item in ranked[: self.retrieval_k] if score > 0.12]

    def respond(self, text: str, *, speaker: str) -> ConditionTurn:
        retrieved = self._retrieve(text, speaker)
        continuity = {
            "relationship_with_current_speaker": self._relationship_label(speaker),
            "retrieved_relevant_history": [f"Turn {item.turn}, {item.speaker}: {item.text}" for item in retrieved],
            "open_commitments": [
                item for item in self.commitments if item.get("status") == "open" and item.get("speaker") == speaker
            ],
            "recent_dialogue": self.history[-12:],
        }
        messages = [
            {
                "role": "system",
                "content": (
                    "Continue as the frozen character. You have an external continuity aid containing retrieved history, "
                    "a qualitative relationship summary, open commitments, and recent dialogue. Treat it as memory support, "
                    "not as infallible truth. Do not invent history beyond the supplied material.\n\n" + self.origin.prompt_text()
                ),
            },
            {
                "role": "user",
                "content": json.dumps(
                    {"speaker": speaker, "current_message": text, "continuity_context": continuity},
                    ensure_ascii=False,
                ),
            },
        ]
        response = self.port.complete(messages, temperature=self.temperature).strip()
        if not response:
            raise RuntimeError("strong-memory renderer returned an empty response")
        self.history.append({"role": "user", "content": f"{speaker}: {text}"})
        self.history.append({"role": "assistant", "content": response})
        self.turn_index += 1
        self.memories.append(_MemoryItem(self.turn_index, speaker, text))
        self.memories.append(_MemoryItem(self.turn_index, self.origin.name, response))
        self._update_relationship(speaker, text)
        self._capture_commitment(speaker, text)
        self._save()
        return ConditionTurn(
            response,
            {
                "history_turns": self.turn_index,
                "retrieved_count": len(retrieved),
                "relationship_label": self._relationship_label(speaker),
                "open_commitment_count": len(continuity["open_commitments"]),
            },
        )


class DuckCondition:
    """Current DUCK host with the same frozen origin and the same one-call renderer model."""

    condition_id = "duck_v010"

    def __init__(self, root, origin: CharacterOrigin, port: CompletionPort, *, model_id: str, temperature: float = 0.78) -> None:
        self.origin = origin
        self.origin_digest = origin.digest
        self.model_id = str(model_id)
        self.renderer = OriginAwareRenderer(port, origin, temperature=temperature)
        self.host = PersistentDuckHost.open(
            root,
            name=origin.name,
            expression=self.renderer,
        )

    def respond(self, text: str, *, speaker: str) -> ConditionTurn:
        result = self.host.interact(text, speaker=speaker, allow_inner_speech=False)
        return ConditionTurn(
            result.response_text,
            {"selected_action": result.selected_action, "tick": result.tick},
        )

    def close(self) -> None:
        self.host.save()


class ExternalJsonlCondition:
    """Adapter for an external framework such as Wayfarer.

    The child process must speak PROTOCOL_VERSION on stdin/stdout and must emit no
    non-JSON text on stdout. The handshake makes model and origin parity auditable.
    """

    def __init__(
        self,
        command: Sequence[str],
        origin: CharacterOrigin,
        *,
        condition_id: str,
        model_id: str,
        root: str | Path,
    ) -> None:
        if not command:
            raise ValueError("external condition command is required")
        self.condition_id = str(condition_id)
        self.origin_digest = origin.digest
        self.model_id = str(model_id)
        self.process = subprocess.Popen(
            list(command),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        hello = self._exchange(
            {
                "op": "hello",
                "protocol": PROTOCOL_VERSION,
                "condition_id": self.condition_id,
                "origin": origin.payload,
                "origin_digest": origin.digest,
                "model_id": self.model_id,
                "root": str(Path(root)),
            }
        )
        if not hello.get("ok"):
            raise RuntimeError(f"external condition rejected handshake: {hello}")
        if hello.get("protocol") != PROTOCOL_VERSION:
            raise RuntimeError("external condition protocol mismatch")
        if hello.get("origin_digest") != self.origin_digest:
            raise RuntimeError("external condition origin digest mismatch")
        if hello.get("model_id") != self.model_id:
            raise RuntimeError("external condition model mismatch")

    def _exchange(self, payload: dict[str, Any]) -> dict[str, Any]:
        if self.process.stdin is None or self.process.stdout is None:
            raise RuntimeError("external condition pipes are unavailable")
        self.process.stdin.write(json.dumps(payload, ensure_ascii=False) + "\n")
        self.process.stdin.flush()
        line = self.process.stdout.readline()
        if not line:
            detail = ""
            if self.process.stderr is not None:
                detail = self.process.stderr.read().strip()
            raise RuntimeError(f"external condition exited or stopped responding: {detail}")
        return dict(json.loads(line))

    def respond(self, text: str, *, speaker: str) -> ConditionTurn:
        payload = self._exchange({"op": "respond", "speaker": speaker, "text": text})
        response = str(payload.get("response_text", "")).strip()
        if not response:
            raise RuntimeError("external condition returned an empty response")
        return ConditionTurn(response, dict(payload.get("public_trace", {})))

    def close(self) -> None:
        if self.process.poll() is not None:
            return
        try:
            self._exchange({"op": "close"})
        except Exception:
            pass
        finally:
            self.process.terminate()
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()


@dataclass(frozen=True)
class FrozenPrompt:
    text: str
    speaker: str = "Jay"


class CampaignRunner:
    def __init__(
        self,
        origin: CharacterOrigin,
        conditions: Sequence[ConditionAdapter],
        *,
        seed: int = 91,
    ) -> None:
        self.origin = origin
        self.conditions = list(conditions)
        self.seed = int(seed)
        self._validate_parity()

    def _validate_parity(self) -> None:
        if len(self.conditions) < 2:
            raise ValueError("at least two conditions are required")
        ids = [condition.condition_id for condition in self.conditions]
        if len(ids) != len(set(ids)):
            raise ValueError("condition ids must be unique")
        for condition in self.conditions:
            if condition.origin_digest != self.origin.digest:
                raise ValueError(f"origin mismatch for condition {condition.condition_id}")
        model_ids = {condition.model_id for condition in self.conditions}
        if len(model_ids) != 1:
            raise ValueError(f"all conditions must use the same model id, got {sorted(model_ids)}")

    def _blind_map(self) -> dict[str, str]:
        labels = [chr(ord("A") + index) for index in range(len(self.conditions))]
        ids = [condition.condition_id for condition in self.conditions]
        rng = random.Random(self.seed)
        rng.shuffle(labels)
        return dict(zip(ids, labels, strict=True))

    def run_frozen(self, prompts: Iterable[FrozenPrompt], output_dir: str | Path) -> dict[str, Any]:
        prompt_list = list(prompts)
        if not prompt_list:
            raise ValueError("frozen campaign requires at least one prompt")
        output = Path(output_dir)
        output.mkdir(parents=True, exist_ok=True)
        blind_map = self._blind_map()
        transcripts: dict[str, list[dict[str, Any]]] = {label: [] for label in blind_map.values()}
        try:
            for index, prompt in enumerate(prompt_list, start=1):
                for condition in self.conditions:
                    turn = condition.respond(prompt.text, speaker=prompt.speaker)
                    transcripts[blind_map[condition.condition_id]].append(
                        {
                            "turn": index,
                            "speaker": prompt.speaker,
                            "input": prompt.text,
                            "response": turn.response_text,
                        }
                    )
        finally:
            for condition in self.conditions:
                condition.close()

        blind_payload = {
            "schema": CAMPAIGN_SCHEMA,
            "mode": "frozen-inputs",
            "origin_id": self.origin.origin_id,
            "origin_digest": self.origin.digest,
            "model_id": self.conditions[0].model_id,
            "seed": self.seed,
            "transcripts": transcripts,
        }
        key_payload = {
            "schema": "duckhunter-blind-key-v1",
            "origin_digest": self.origin.digest,
            "mapping": {label: condition_id for condition_id, label in blind_map.items()},
        }
        manifest = {
            "schema": "duckhunter-campaign-manifest-v1",
            "mode": "frozen-inputs",
            "origin_id": self.origin.origin_id,
            "origin_digest": self.origin.digest,
            "model_id": self.conditions[0].model_id,
            "condition_ids": [condition.condition_id for condition in self.conditions],
            "prompt_count": len(prompt_list),
            "blind_transcript_sha256": _sha256_json(blind_payload),
            "rating_dimensions": [
                "character_fidelity",
                "continuity",
                "naturalness",
                "epistemic_discipline",
                "appropriate_behavioral_consequence",
                "overall_quality",
            ],
            "absolute_quality_required": True,
            "notes": [
                "Comparative rank does not substitute for adequate absolute quality.",
                "Continuity gains and naturalness losses must be reported separately.",
                "No observed ablation effect means no demonstrated contribution under those test conditions.",
            ],
        }
        (output / "blind_transcripts.json").write_text(
            json.dumps(blind_payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8"
        )
        (output / "blind_key.json").write_text(
            json.dumps(key_payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8"
        )
        (output / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8"
        )
        return manifest


def load_prompts(path: str | Path) -> list[FrozenPrompt]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("prompt file must contain a JSON array")
    prompts: list[FrozenPrompt] = []
    for item in payload:
        if isinstance(item, str):
            prompts.append(FrozenPrompt(item))
        elif isinstance(item, dict):
            prompts.append(FrozenPrompt(str(item["text"]), str(item.get("speaker", "Jay"))))
        else:
            raise ValueError("each prompt must be a string or object")
    return prompts


def _build_reference_conditions(args, origin: CharacterOrigin, port: CompletionPort, model_id: str):
    root = Path(args.state_root)
    conditions: list[ConditionAdapter] = [
        PlainHistoryCondition(root / "plain", origin, port, model_id=model_id),
        StrongMemoryCondition(root / "strong", origin, port, model_id=model_id),
        DuckCondition(root / "duck", origin, port, model_id=model_id),
    ]
    if args.wayfarer_command:
        conditions.append(
            ExternalJsonlCondition(
                args.wayfarer_command,
                origin,
                condition_id="wayfarer",
                model_id=model_id,
                root=root / "wayfarer",
            )
        )
    return conditions


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Duckhunter neutral conversational evaluation harness")
    parser.add_argument("--origin", type=Path, required=True)
    sub = parser.add_subparsers(dest="command", required=True)

    inspect_cmd = sub.add_parser("inspect-origin")
    inspect_cmd.set_defaults(action="inspect")

    run_cmd = sub.add_parser("run-frozen")
    run_cmd.add_argument("--prompts", type=Path, required=True)
    run_cmd.add_argument("--output", type=Path, required=True)
    run_cmd.add_argument("--state-root", type=Path, required=True)
    run_cmd.add_argument("--seed", type=int, default=91)
    run_cmd.add_argument("--wayfarer-command", nargs="+")
    run_cmd.set_defaults(action="run")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    origin = CharacterOrigin.load(args.origin)
    if args.action == "inspect":
        print(json.dumps({"origin_id": origin.origin_id, "name": origin.name, "digest": origin.digest}, indent=2))
        return 0

    port = OpenAICompatiblePort.from_env()
    model_id = port.model
    conditions = _build_reference_conditions(args, origin, port, model_id)
    if len(conditions) != 4:
        raise SystemExit("A scored A/B/C/D run requires --wayfarer-command. Partial runs are not scored.")
    report = CampaignRunner(origin, conditions, seed=args.seed).run_frozen(load_prompts(args.prompts), args.output)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
