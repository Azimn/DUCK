import json
from datetime import datetime, timezone

from duck.evaluation import run_all
from duck.semantics import ModelEventInterpreter
from duck.temporal import internet_time, stamp


class FakePort:
    def __init__(self, text):
        self.text = text
        self.messages = None

    def complete(self, messages, *, temperature=0.7):
        self.messages = messages
        return self.text


def test_model_semantics_is_bounded_and_cannot_invent_world_facts():
    port = FakePort('{"tags":["threat","not_allowed"],"valence":-4,"intensity":9}')
    interpreter = ModelEventInterpreter(port)
    event = interpreter.interpret("Get away from me!", source="Morgan")
    assert "threat" in event.tags
    assert "not_allowed" not in event.tags
    assert event.valence == -1.0
    assert event.intensity == 1.0
    assert event.world_facts == ()
    assert port.messages is not None
    user_packet = json.loads(port.messages[-1]["content"])
    assert user_packet == {"source": "Morgan", "utterance": "Get away from me!"}
    assert "trust" not in repr(port.messages)
    assert "affect" not in repr(port.messages).lower()


def test_model_semantics_falls_back_when_output_is_invalid():
    interpreter = ModelEventInterpreter(FakePort("not json"))
    event = interpreter.interpret("Thank you for helping me.", source="Jay")
    assert "supportive" in event.tags
    assert event.valence > 0


def test_swatch_beat_time_is_deterministic_for_known_utc_time():
    # 23:00 UTC is midnight BMT and therefore @000.
    moment = datetime(2026, 9, 5, 23, 0, 0, tzinfo=timezone.utc)
    date, beat = internet_time(moment)
    assert date == "2026-09-06"
    assert beat == 0.0
    temporal = stamp(42, moment)
    assert temporal.logical_tick == 42
    assert temporal.beat_label == "@000.00"


def test_integrated_evaluation_harness_passes():
    report = run_all()
    assert report["passed"] is True
    assert {row["name"] for row in report["results"]} == {"paired_history", "language_lesion", "persistence_roundtrip"}
