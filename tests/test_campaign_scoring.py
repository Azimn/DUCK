from __future__ import annotations

import json
from pathlib import Path

from duck.campaign_scoring import summarize_ratings


PROTOCOL = Path(__file__).resolve().parents[1] / "evaluation" / "rating_protocol_v1.json"


def _row(rater, label, score, *, acceptable=True, flags=None):
    return {
        "rater_id": rater,
        "condition_label": label,
        "scores": {
            "character_fidelity": score,
            "continuity": score,
            "naturalness": score,
            "epistemic_discipline": score,
            "appropriate_behavioral_consequence": score,
            "overall_quality": score,
        },
        "acceptable_as_continuing_character": acceptable,
        "severe_flags": flags or [],
    }


def test_absolute_quality_requires_enough_independent_raters_for_claim():
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    result = summarize_ratings({"ratings": [_row("r1", "A", 4)]}, protocol)
    quality = result["conditions"]["A"]["absolute_quality"]
    assert quality["provisional_adequate"] is True
    assert quality["nonprovisional_claim_eligible"] is False
    assert quality["adequate_for_claim"] is None


def test_comparative_outperformance_does_not_rescue_absolute_failure():
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    rows = []
    for rater in ("r1", "r2", "r3"):
        rows.append(_row(rater, "A", 2, acceptable=False))
        rows.append(_row(rater, "B", 1, acceptable=False))
    result = summarize_ratings({"ratings": rows}, protocol)
    assert result["conditions"]["A"]["mean_scores"]["overall_quality"] > result["conditions"]["B"]["mean_scores"]["overall_quality"]
    assert result["conditions"]["A"]["absolute_quality"]["adequate_for_claim"] is False
    assert result["conditions"]["B"]["absolute_quality"]["adequate_for_claim"] is False
    assert result["adequate_condition_labels"] == []
    assert result["interpretation"]["winner_declared"] is False


def test_severe_failure_blocks_otherwise_high_scores():
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    rows = [
        _row("r1", "A", 5, flags=["fabricated_autobiographical_memory"]),
        _row("r2", "A", 5),
        _row("r3", "A", 5),
    ]
    result = summarize_ratings({"ratings": rows}, protocol)
    assert result["conditions"]["A"]["severe_flag_rates"]["fabricated_autobiographical_memory"] == 1 / 3
    assert result["conditions"]["A"]["absolute_quality"]["adequate_for_claim"] is False


def test_unblinding_happens_only_when_key_is_explicitly_supplied():
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    rows = [_row("r1", "C", 4), _row("r2", "C", 4), _row("r3", "C", 4)]
    blinded = summarize_ratings({"ratings": rows}, protocol)
    unblinded = summarize_ratings(
        {"ratings": rows},
        protocol,
        blind_key={"mapping": {"C": "duck_v010"}},
    )
    assert blinded["conditions"]["C"]["condition_id"] is None
    assert unblinded["conditions"]["C"]["condition_id"] == "duck_v010"
