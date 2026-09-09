from __future__ import annotations

import json

import pytest

from duck import PersistentDuckHost, WorldEvent
from duck.environment_v010 import EnvironmentDynamicsState


def test_observable_scheduled_world_event_arrives_without_user_prompt(tmp_path):
    root = tmp_path / "environment-observable"
    host = PersistentDuckHost.open(root, name="Aster", subject_id="environment-observable")
    record = host.schedule_world_event(
        WorldEvent(
            "observation",
            "world",
            "The greenhouse lights switch on by themselves.",
            ("environment", "novel"),
            0.10,
            0.45,
        ),
        due_in=2,
    )

    first = host.heartbeat(1, allow_inner_speech=False)[0]
    assert first.tick == 1
    assert host.status()["scheduled_world_event_count"] == 1
    assert all("greenhouse lights" not in memory.text.lower() for memory in host.duck.state.memories)

    second = host.heartbeat(1, allow_inner_speech=False)[0]
    assert second.tick == 2
    assert host.status()["scheduled_world_event_count"] == 0
    assert any("greenhouse lights" in memory.text.lower() for memory in host.duck.state.memories)
    assert second.inner_cognition.thought is None
    assert record.event_id not in {item.event_id for item in host.environment.scheduled}

    journal = (root / "events.jsonl").read_text(encoding="utf-8")
    assert '"type": "environment_event"' in journal
    assert record.event_id in journal


def test_unperceived_environment_change_updates_world_truth_without_subject_knowledge(tmp_path):
    root = tmp_path / "environment-hidden"
    host = PersistentDuckHost.open(root, name="Aster", subject_id="environment-hidden")
    hidden_text = "A maintenance system silently locks the east door."
    host.schedule_world_event(
        WorldEvent(
            "world_change",
            "world",
            hidden_text,
            ("environment", "door"),
            0.0,
            0.20,
            (("east_door_state", "locked"),),
            False,
        ),
        due_in=1,
    )

    step = host.heartbeat(1, allow_inner_speech=False)[0]
    assert step.tick == 1
    assert host.duck.state.world_facts["east_door_state"] == "locked"
    assert "east_door_state" not in host.duck.state.beliefs
    assert all(hidden_text not in memory.text for memory in host.duck.state.memories)
    assert all("maintenance system" not in line.lower() for line in host.duck.last_experience.prose)

    journal = (root / "events.jsonl").read_text(encoding="utf-8")
    assert '"type": "environment_hidden_change"' in journal


def test_environment_queue_is_separate_persistent_host_state(tmp_path):
    root = tmp_path / "environment-restart"
    host = PersistentDuckHost.open(root, name="Aster", subject_id="environment-restart")
    text = "Rain begins against the windows."
    record = host.schedule_world_event(
        WorldEvent("observation", "world", text, ("environment", "weather"), -0.05, 0.30),
        due_in=3,
    )

    environment_path = root / "environment_v010.json"
    assert environment_path.exists()
    payload = json.loads(environment_path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "micropsi-duck.environment.v1"
    assert payload["scheduled"][0]["event_id"] == record.event_id
    assert payload["scheduled"][0]["event"]["text"] == text

    subject_payload = (root / "subject.json").read_text(encoding="utf-8")
    assert record.event_id not in subject_payload
    assert text not in subject_payload

    reopened = PersistentDuckHost.open(root)
    assert reopened.duck.state.subject_id == "environment-restart"
    assert reopened.status()["scheduled_world_event_count"] == 1
    reopened.heartbeat(2, allow_inner_speech=False)
    assert reopened.status()["scheduled_world_event_count"] == 1
    delivered = reopened.heartbeat(1, allow_inner_speech=False)[0]
    assert delivered.tick == 3
    assert reopened.status()["scheduled_world_event_count"] == 0
    assert any(text == memory.text for memory in reopened.duck.state.memories)


def test_environment_scheduler_cannot_author_endogenous_self_events():
    state = EnvironmentDynamicsState()
    with pytest.raises(ValueError):
        state.schedule(
            0,
            WorldEvent(
                "endogenous",
                "self",
                "I decide the world changed because I wanted it to.",
                ("invalid",),
                0.0,
                0.1,
                perceived=False,
            ),
            due_in=1,
        )


def test_environment_schema_rejects_unknown_versions():
    with pytest.raises(ValueError):
        EnvironmentDynamicsState.from_dict(
            {
                "schema_version": "micropsi-duck.environment.v999",
                "event_counter": 0,
                "scheduled": [],
            }
        )


def test_scheduled_observable_event_operates_under_language_lesion(tmp_path):
    root = tmp_path / "environment-lesion"
    host = PersistentDuckHost.open(root, name="Aster", subject_id="environment-lesion")
    host.schedule_world_event(
        WorldEvent(
            "observation",
            "world",
            "A previously quiet machine begins making an unfamiliar sound.",
            ("environment", "novel", "mystery"),
            0.0,
            0.50,
        ),
        due_in=1,
    )

    step = host.heartbeat(1, allow_inner_speech=False)[0]
    assert step.inner_cognition.thought is None
    assert step.selected_action
    assert step.developer_trace["executive_recruitment"]["invoked"] is False
    assert any("unfamiliar sound" in memory.text.lower() for memory in host.duck.state.memories)
