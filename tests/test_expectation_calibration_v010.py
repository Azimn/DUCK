from __future__ import annotations

import pytest

from duck import WorldEvent
from duck.expectations_v010 import ExpectationLedgerState


def _event(value: str) -> WorldEvent:
    return WorldEvent(
        "environment",
        "world",
        f"The weather is {value}.",
        ("observation",),
        0.0,
        0.30,
        (("weather", value),),
        True,
    )


def test_default_expectation_confidence_learns_from_domain_outcomes():
    ledger = ExpectationLedgerState()
    first = ledger.register(
        0,
        "I expect the weather to be clear.",
        fact_key="weather",
        expected_value="clear",
        confidence=None,
    )
    assert first.confidence == pytest.approx(0.70)

    ledger.evaluate_event(_event("rain"), 1)
    after_miss = ledger.learned_confidence("weather")
    assert after_miss < 0.70

    second = ledger.register(
        1,
        "I expect the weather to be clear next time.",
        fact_key="weather",
        expected_value="clear",
        confidence=None,
    )
    assert second.confidence == pytest.approx(after_miss)

    ledger.evaluate_event(_event("clear"), 2)
    after_hit = ledger.learned_confidence("weather")
    assert after_hit > after_miss
    assert ledger.calibration["weather"].fulfilled == 1
    assert ledger.calibration["weather"].violated == 1


def test_explicit_confidence_is_preserved_while_calibration_still_learns():
    ledger = ExpectationLedgerState()
    record = ledger.register(
        0,
        "I strongly expect the sensor to be ready.",
        fact_key="sensor",
        expected_value="ready",
        confidence=0.93,
    )
    ledger.evaluate_event(
        WorldEvent(
            "environment",
            "world",
            "The sensor is offline.",
            ("observation",),
            0.0,
            0.30,
            (("sensor", "offline"),),
            True,
        ),
        1,
    )
    assert ledger.get(record.expectation_id).confidence == pytest.approx(0.93)
    assert ledger.calibration["sensor"].violated == 1
    assert ledger.learned_confidence("sensor") < 0.70


def test_calibration_roundtrip_preserves_learned_reliability():
    ledger = ExpectationLedgerState()
    record = ledger.register(
        0,
        "I expect the lamp to be on.",
        fact_key="lamp",
        expected_value="on",
        confidence=None,
    )
    ledger.evaluate_event(
        WorldEvent(
            "environment",
            "world",
            "The lamp is on.",
            ("observation",),
            0.0,
            0.30,
            (("lamp", "on"),),
            True,
        ),
        1,
    )
    restored = ExpectationLedgerState.from_dict(ledger.to_dict())
    assert restored.get(record.expectation_id).status == "fulfilled"
    assert restored.calibration["lamp"].fulfilled == 1
    assert restored.learned_confidence("lamp") == pytest.approx(ledger.learned_confidence("lamp"))


def test_unperceived_evidence_never_updates_calibration():
    ledger = ExpectationLedgerState()
    record = ledger.register(
        0,
        "I expect the door to be open.",
        fact_key="door",
        expected_value="open",
        confidence=None,
    )
    ledger.evaluate_event(
        WorldEvent(
            "environment",
            "world",
            "The door closes elsewhere.",
            ("door",),
            0.0,
            0.30,
            (("door", "closed"),),
            False,
        ),
        1,
    )
    assert ledger.get(record.expectation_id).status == "open"
    assert "door" not in ledger.calibration
