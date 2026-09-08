import json
from dataclasses import fields

import pytest

from duck import (
    ApprovedLanguagePacket,
    ExperientialFrame,
    LivingDuckV010,
    PersistentDuckHostV010,
    PrivateInteriorState,
    SubjectState,
    WorldEvent,
)
from duck.cognition import InnerCognition
from duck.language import ModelExpression
from duck.subjective import PRIVATE_INTERIOR_SCHEMA_VERSION


class SpyCognition:
    def __init__(self):
        self.seen = None

    def generate(self, experience):
        self.seen = experience
        return InnerCognition("I want to be careful with this.")


class FakePort:
    def __init__(self, text="I'll answer carefully."):
        self.text = text
        self.messages = None

    def complete(self, messages, *, temperature=0.7):
        self.messages = messages
        return self.text


def test_full_v010_runtime_private_cognition_gets_prose_only():
    spy = SpyCognition()
    duck = LivingDuckV010(SubjectState.create("Aster", "firewall-subject"), cognition=spy)
    step = duck.step(
        WorldEvent("encounter", "Morgan", "Morgan threatens me.", ("social", "threat", "conflict"), -0.8, 0.9)
    )
    assert isinstance(spy.seen, ExperientialFrame)
    assert len(fields(spy.seen)) == 1
    assert fields(spy.seen)[0].name == "prose"
    assert spy.seen == duck.last_experience
    assert all(isinstance(line, str) for line in spy.seen.prose)
    assert "0.9" not in repr(spy.seen)
    assert "threat" not in spy.seen.prose
    assert step.developer_trace["mechanistic_snapshot"]["affect"]["fear"] > 0.0


def test_experiential_frame_rejects_disguised_telemetry():
    with pytest.raises(ValueError):
        ExperientialFrame(("My motive strength = 0.83.",))
    with pytest.raises(ValueError):
        ExperientialFrame(("Activation is 0.61.",))
    with pytest.raises(ValueError):
        ExperientialFrame(("I am 64% certain.",))


def test_private_interior_is_versioned_and_roundtrips():
    interior = PrivateInteriorState.capture(
        ExperientialFrame(("I'm tired.", "I want somewhere quiet.")),
        "I should probably slow down.",
    )
    payload = interior.to_dict()
    assert payload["schema_version"] == PRIVATE_INTERIOR_SCHEMA_VERSION
    restored = PrivateInteriorState.from_dict(payload)
    assert restored == interior
    assert restored.experiential_frame() == ExperientialFrame(("I'm tired.", "I want somewhere quiet."))


def test_host_persists_private_interior_but_does_not_return_it_publicly(tmp_path):
    root = tmp_path / "aster"
    host = PersistentDuckHostV010.open(root, name="Aster", subject_id="aster-firewall")
    result = host.interact("Hello, Aster.")

    assert result.response_text
    assert not hasattr(result, "private_thought")
    assert not hasattr(result, "subjective_state")
    assert host.private_interior is not None
    assert (root / "private_interior.json").exists()

    payload = json.loads((root / "private_interior.json").read_text(encoding="utf-8"))
    assert payload["schema_version"] == PRIVATE_INTERIOR_SCHEMA_VERSION
    assert "affect" not in payload
    assert "needs" not in payload
    assert "selected_action" not in payload

    reopened = PersistentDuckHostV010.open(root)
    assert reopened.private_interior == host.private_interior


def test_event_journal_does_not_publish_private_interior(tmp_path):
    root = tmp_path / "aster"
    host = PersistentDuckHostV010.open(root, name="Aster")
    host.interact("Can we talk?")
    host.heartbeat(1)
    journal = (root / "events.jsonl").read_text(encoding="utf-8")
    assert "private_thought" not in journal
    assert "subjective_state" not in journal
    assert "first_person_state" not in journal


def test_renderer_packet_contains_prose_intent_not_machine_action_tag():
    interior = PrivateInteriorState.capture(
        ExperientialFrame(("I'm nervous.", "I want to step back.")),
        "I don't like this.",
    )
    packet = ApprovedLanguagePacket.from_private_interior(
        interior,
        user_text="Come closer.",
        selected_action="step_back",
        character_name="Aster",
    )
    assert not hasattr(packet, "selected_action")
    assert packet.action_intent == "I have decided to give myself some space."
    assert "step_back" not in repr(packet)

    port = FakePort("I need a little room right now.")
    renderer = ModelExpression(port)
    output = renderer.render(packet)
    assert output == "I need a little room right now."
    assert renderer.last_packet is not None
    assert "selected_action" not in renderer.last_packet
    assert "schema_version" not in renderer.last_packet


def test_language_lesion_still_refreshes_experiential_state():
    duck = LivingDuckV010(SubjectState.create("Aster", "lesioned-firewall"))
    step = duck.step(
        WorldEvent("encounter", "world", "Something dangerous approaches.", ("threat",), -0.8, 0.9),
        allow_inner_speech=False,
    )
    assert step.inner_cognition.thought is None
    assert isinstance(duck.last_experience, ExperientialFrame)
    assert duck.last_experience.prose
