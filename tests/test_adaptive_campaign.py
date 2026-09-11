from __future__ import annotations

import json
from pathlib import Path

from duck.adaptive_campaign import AdaptiveCampaignRunner
from duck.continuity_campaign import CharacterOrigin, ConditionTurn, FrozenPrompt


FIXTURE = Path(__file__).resolve().parents[1] / "evaluation" / "fixtures" / "pretorius_origin_v1.json"


class StaticCondition:
    def __init__(self, condition_id: str, origin: CharacterOrigin, model_id: str = "shared-model") -> None:
        self.condition_id = condition_id
        self.origin_digest = origin.digest
        self.model_id = model_id
        self.received = []
        self.closed = False

    def respond(self, text: str, *, speaker: str) -> ConditionTurn:
        self.received.append((speaker, text))
        return ConditionTurn(f"{self.condition_id} reply {len(self.received)}")

    def close(self) -> None:
        self.closed = True


def test_adaptive_sessions_share_opening_then_may_diverge(tmp_path):
    origin = CharacterOrigin.load(FIXTURE)
    conditions = [
        StaticCondition("plain", origin),
        StaticCondition("strong", origin),
        StaticCondition("duck", origin),
        StaticCondition("wayfarer", origin),
    ]

    def partner(label, transcript):
        if len(transcript) >= 3:
            return None
        return FrozenPrompt(f"adaptive follow-up for {label} after {transcript[-1]['response']}")

    report = AdaptiveCampaignRunner(origin, conditions, seed=91).run(
        FrozenPrompt("Common opening."), partner, tmp_path / "out", max_turns=5
    )

    payload = json.loads((tmp_path / "out" / "adaptive_blind_transcripts.json").read_text(encoding="utf-8"))
    key = json.loads((tmp_path / "out" / "blind_key.json").read_text(encoding="utf-8"))

    assert report["mode"] == "adaptive-conversation"
    assert set(payload["transcripts"]) == {"A", "B", "C", "D"}
    assert set(key["mapping"].values()) == {"plain", "strong", "duck", "wayfarer"}
    assert all(condition.received[0] == ("Jay", "Common opening.") for condition in conditions)
    assert all(len(condition.received) == 3 for condition in conditions)
    assert len({condition.received[1][1] for condition in conditions}) == 4
    assert all(condition.closed for condition in conditions)
