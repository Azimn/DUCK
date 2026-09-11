from __future__ import annotations

import json
from pathlib import Path

import pytest

from duck.continuity_campaign import (
    CampaignRunner,
    CharacterOrigin,
    ConditionTurn,
    DuckCondition,
    FrozenPrompt,
    PlainHistoryCondition,
    StrongMemoryCondition,
)


FIXTURE = Path(__file__).resolve().parents[1] / "evaluation" / "fixtures" / "pretorius_origin_v1.json"


class FakePort:
    def __init__(self, model: str = "fake-shared-model") -> None:
        self.model = model
        self.calls = []

    def complete(self, messages, *, temperature=0.7):
        self.calls.append({"messages": messages, "temperature": temperature})
        return f"response-{len(self.calls)}"


class StaticCondition:
    def __init__(self, condition_id: str, origin: CharacterOrigin, model_id: str) -> None:
        self.condition_id = condition_id
        self.origin_digest = origin.digest
        self.model_id = model_id
        self.turns = []
        self.closed = False

    def respond(self, text: str, *, speaker: str) -> ConditionTurn:
        self.turns.append((speaker, text))
        return ConditionTurn(f"{self.condition_id}:{speaker}:{text}")

    def close(self) -> None:
        self.closed = True


def test_pretorius_origin_is_loadable_and_digest_is_stable():
    first = CharacterOrigin.load(FIXTURE)
    second = CharacterOrigin.load(FIXTURE)
    assert first.origin_id == "pretorius-v1"
    assert first.name == "Doctor Septimus Pretorius"
    assert first.digest == second.digest
    assert len(first.digest) == 64


def test_campaign_rejects_model_mismatch():
    origin = CharacterOrigin.load(FIXTURE)
    conditions = [
        StaticCondition("one", origin, "model-a"),
        StaticCondition("two", origin, "model-b"),
    ]
    with pytest.raises(ValueError, match="same model"):
        CampaignRunner(origin, conditions)


def test_frozen_runner_blinds_conditions_and_holds_inputs_fixed(tmp_path):
    origin = CharacterOrigin.load(FIXTURE)
    conditions = [
        StaticCondition("plain", origin, "shared"),
        StaticCondition("strong", origin, "shared"),
        StaticCondition("duck", origin, "shared"),
        StaticCondition("wayfarer", origin, "shared"),
    ]
    prompts = [FrozenPrompt("Hello."), FrozenPrompt("Do you remember that?", "Jay")]
    report = CampaignRunner(origin, conditions, seed=91).run_frozen(prompts, tmp_path / "out")

    blind = json.loads((tmp_path / "out" / "blind_transcripts.json").read_text(encoding="utf-8"))
    key = json.loads((tmp_path / "out" / "blind_key.json").read_text(encoding="utf-8"))
    assert report["prompt_count"] == 2
    assert set(blind["transcripts"]) == {"A", "B", "C", "D"}
    assert set(key["mapping"].values()) == {"plain", "strong", "duck", "wayfarer"}
    assert all(condition.turns == [("Jay", "Hello."), ("Jay", "Do you remember that?")] for condition in conditions)
    assert all(condition.closed for condition in conditions)


def test_plain_and_strong_baselines_use_one_public_model_call_per_turn(tmp_path):
    origin = CharacterOrigin.load(FIXTURE)
    plain_port = FakePort()
    strong_port = FakePort()
    plain = PlainHistoryCondition(tmp_path / "plain", origin, plain_port, model_id=plain_port.model)
    strong = StrongMemoryCondition(tmp_path / "strong", origin, strong_port, model_id=strong_port.model)

    plain.respond("I promise I will bring the notes tomorrow.", speaker="Jay")
    strong.respond("I promise I will bring the notes tomorrow.", speaker="Jay")
    plain.respond("What did I say I would bring?", speaker="Jay")
    strong.respond("What did I say I would bring?", speaker="Jay")

    assert len(plain_port.calls) == 2
    assert len(strong_port.calls) == 2
    strong_context = strong_port.calls[-1]["messages"][-1]["content"]
    assert "bring the notes" in strong_context
    assert "open_commitments" in strong_context


def test_duck_condition_uses_common_origin_and_one_public_renderer_call(tmp_path):
    origin = CharacterOrigin.load(FIXTURE)
    port = FakePort()
    condition = DuckCondition(tmp_path / "duck", origin, port, model_id=port.model)
    turn = condition.respond("Hello. How are you?", speaker="Jay")
    condition.close()

    assert turn.response_text == "response-1"
    assert len(port.calls) == 1
    system_prompt = port.calls[0]["messages"][0]["content"]
    assert "Doctor Septimus Pretorius" in system_prompt
    assert "frozen origin" in system_prompt
