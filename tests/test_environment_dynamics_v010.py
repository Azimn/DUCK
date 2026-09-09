from __future__ import annotations

import json

import pytest

from duck import LivingDuck, PersistentDuckHost, SubjectState, WorldEvent
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


def test_unperceived_environment_change_updates_host_truth_without_subject_knowledge(tmp_path):
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
    assert host.environment.world_facts["east_door_state"] == "locked"
    assert host.world_fact("east_door_state") == "locked"
    assert host.duck.state.world_facts == {}
    assert "east_door_state" not in host.duck.state.beliefs
    assert all(hidden_text not in memory.text for memory in host.duck.state.memories)
    assert all("maintenance system" not in line.lower() for line in host.duck.last_experience.prose)

    journal = (root / "events.jsonl").read_text(encoding="utf-8")
    assert '"type": "environment_hidden_change"' in journal


def test_perceived_world_fact_updates_environment_truth_and_subject_belief_separately(tmp_path):
    root = tmp_path / "environment-perceived-fact"
    host = PersistentDuckHost.open(root, name="Aster", subject_id="environment-perceived-fact")
    step = host.observe(
        WorldEvent(
            "observation",
            "world",
            "The north lamp is glowing.",
            ("environment", "lamp"),
            0.05,
            0.30,
            (("north_lamp", "on"),),
            True,
        ),
        allow_inner_speech=False,
    )

    assert step.tick == 1
    assert host.environment.fact("north_lamp") == "on"
    assert host.duck.state.world_facts == {}
    assert host.duck.state.beliefs["north_lamp"].text == "on"
    assert any(
        memory.text == "on" and "world_fact" in memory.tags
        for memory in host.duck.state.memories
    )


def test_direct_public_organism_never_retains_authoritative_world_facts():
    state = SubjectState.create("Aster", "direct-authority")
    state.world_facts["legacy_fact"] = "legacy_value"
    duck = LivingDuck(state)
    assert duck.state.world_facts == {}

    duck.step(
        WorldEvent(
            "observation",
            "world",
            "The hatch is open.",
            ("environment",),
            0.0,
            0.30,
            (("hatch", "open"),),
            True,
        ),
        allow_inner_speech=False,
    )
    assert duck.state.world_facts == {}
    assert duck.state.beliefs["hatch"].text == "open"

    with pytest.raises(RuntimeError):
        duck.set_world_fact("hatch", "closed")


def test_host_set_world_fact_is_the_public_world_mutation_path(tmp_path):
    root = tmp_path / "host-world-mutation"
    host = PersistentDuckHost.open(root, name="Aster", subject_id="host-world-mutation")

    host.set_world_fact("weather", "rain", perceived=False)
    assert host.environment.fact("weather") == "rain"
    assert host.duck.state.world_facts == {}
    assert "weather" not in host.duck.state.beliefs

    host.set_world_fact(
        "weather",
        "clear",
        perceived=True,
        description="The rain stops and the sky clears.",
        allow_inner_speech=False,
    )
    assert host.environment.fact("weather") == "clear"
    assert host.duck.state.world_facts == {}
    assert host.duck.state.beliefs["weather"].text == "clear"
    assert any("sky clears" in memory.text.lower() for memory in host.duck.state.memories)


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


def test_legacy_subject_world_facts_migrate_to_environment_authority(tmp_path):
    root = tmp_path / "world-fact-migration"
    host = PersistentDuckHost.open(root, name="Aster", subject_id="world-fact-migration")
    # Write one legacy-style compatibility payload without committing a snapshot.
    host.duck.state.world_facts["legacy_door"] = "locked"
    host._write_compatibility_mirrors(host._snapshot_payloads())

    reopened = PersistentDuckHost.open(root)
    assert reopened.environment.fact("legacy_door") == "locked"
    assert reopened.duck.state.world_facts == {}
    reopened.save()

    again = PersistentDuckHost.open(root)
    assert again.environment.fact("legacy_door") == "locked"
    assert again.duck.state.world_facts == {}


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
