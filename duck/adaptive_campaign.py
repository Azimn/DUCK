"""Blinded adaptive-conversation mode for Duckhunter evaluation.

Frozen-input evaluation and adaptive conversation answer different questions.
This module records one natural conversation per blinded condition so a human
partner can respond to what the character actually said instead of following a
script that no longer fits the interaction.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import random
from typing import Any, Callable, Sequence

from .continuity_campaign import (
    CAMPAIGN_SCHEMA,
    CampaignRunner,
    CharacterOrigin,
    ConditionAdapter,
    FrozenPrompt,
    _build_reference_conditions,
    _sha256_json,
)
from .language import OpenAICompatiblePort


AdaptivePartner = Callable[[str, tuple[dict[str, Any], ...]], FrozenPrompt | None]


class AdaptiveCampaignRunner:
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
        validator = CampaignRunner(origin, self.conditions, seed=self.seed)
        self._blind_map = validator._blind_map()

    def run(
        self,
        opening: FrozenPrompt,
        partner: AdaptivePartner,
        output_dir: str | Path,
        *,
        max_turns: int = 20,
    ) -> dict[str, Any]:
        if max_turns < 1:
            raise ValueError("max_turns must be at least 1")
        output = Path(output_dir)
        output.mkdir(parents=True, exist_ok=True)

        condition_by_label = {
            self._blind_map[condition.condition_id]: condition for condition in self.conditions
        }
        session_order = list(condition_by_label)
        random.Random(self.seed + 1).shuffle(session_order)
        transcripts: dict[str, list[dict[str, Any]]] = {label: [] for label in condition_by_label}

        try:
            for label in session_order:
                condition = condition_by_label[label]
                current = opening
                for turn_index in range(1, max_turns + 1):
                    result = condition.respond(current.text, speaker=current.speaker)
                    transcripts[label].append(
                        {
                            "turn": turn_index,
                            "speaker": current.speaker,
                            "input": current.text,
                            "response": result.response_text,
                        }
                    )
                    if turn_index >= max_turns:
                        break
                    next_prompt = partner(label, tuple(transcripts[label]))
                    if next_prompt is None:
                        break
                    current = next_prompt
        finally:
            for condition in self.conditions:
                condition.close()

        blind_payload = {
            "schema": CAMPAIGN_SCHEMA,
            "mode": "adaptive-conversation",
            "origin_id": self.origin.origin_id,
            "origin_digest": self.origin.digest,
            "model_id": self.conditions[0].model_id,
            "seed": self.seed,
            "opening": {"speaker": opening.speaker, "text": opening.text},
            "session_order": session_order,
            "transcripts": transcripts,
        }
        key_payload = {
            "schema": "duckhunter-blind-key-v1",
            "origin_digest": self.origin.digest,
            "mapping": {label: condition_id for condition_id, label in self._blind_map.items()},
        }
        manifest = {
            "schema": "duckhunter-campaign-manifest-v1",
            "mode": "adaptive-conversation",
            "origin_id": self.origin.origin_id,
            "origin_digest": self.origin.digest,
            "model_id": self.conditions[0].model_id,
            "condition_ids": [condition.condition_id for condition in self.conditions],
            "session_order": session_order,
            "max_turns": max_turns,
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
                "Adaptive sessions are scored separately from frozen-input sessions.",
                "After the common opening, human inputs may diverge because each prior response changes the conversation.",
                "Session order is randomized to reduce fixed order effects.",
                "Comparative rank does not substitute for adequate absolute quality.",
            ],
        }
        (output / "adaptive_blind_transcripts.json").write_text(
            json.dumps(blind_payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8"
        )
        (output / "blind_key.json").write_text(
            json.dumps(key_payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8"
        )
        (output / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8"
        )
        return manifest


class ConsolePartner:
    def __init__(self) -> None:
        self._announced: set[str] = set()

    def __call__(self, label: str, transcript: tuple[dict[str, Any], ...]) -> FrozenPrompt | None:
        if label not in self._announced:
            print(f"\n=== Blinded session {label} ===")
            self._announced.add(label)
        latest = transcript[-1]
        print(f"character> {latest['response']}")
        try:
            text = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return None
        if not text or text.lower() in {"/end", "/quit", "/next"}:
            return None
        return FrozenPrompt(text=text, speaker="Jay")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Duckhunter blinded adaptive conversation runner")
    parser.add_argument("--origin", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--state-root", type=Path, required=True)
    parser.add_argument("--opening", default="Hello. How are you?")
    parser.add_argument("--max-turns", type=int, default=20)
    parser.add_argument("--seed", type=int, default=91)
    parser.add_argument("--wayfarer-command", nargs="+", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    origin = CharacterOrigin.load(args.origin)
    port = OpenAICompatiblePort.from_env()
    conditions = _build_reference_conditions(args, origin, port, port.model)
    if len(conditions) != 4:
        raise SystemExit("A scored adaptive A/B/C/D run requires all four conditions.")
    report = AdaptiveCampaignRunner(origin, conditions, seed=args.seed).run(
        FrozenPrompt(args.opening, "Jay"),
        ConsolePartner(),
        args.output,
        max_turns=args.max_turns,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
