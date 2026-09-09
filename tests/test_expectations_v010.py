from __future__ import annotations

import json

import pytest

from duck import LivingDuck, PersistentDuckHost, SubjectState, WorldEvent
from duck.expectations_v010 import EXPECTATION_STATE_SCHEMA, ExpectationLedgerState


def _quiet_state(subject_id: str) -> SubjectState:
    state = SubjectState.create("Aster", subject_id)
    state.affect["fear"] = 0.02
    state.affect["unease"] = 0.03
    state.affect["loneliness"] = 0.12
    state.needs["energy"] = 0.92
    state.needs["safety"] = 0.94
    state.needs["curiosity"] = 0.38
    state.needs["competence"] = 0.72
    state.needs["coherence"] = 0.82
    state.needs["autonomy"] = 0.70
    state.needs["affiliation"] = 0.20
    return state


def test_perceived_matching_fact_fulfills_expectation():
    duck = LivingDuck(_quiet_state("expectation-fulfilled"))
    record = duck.register_expectation(
        "I expect the garden door to be open.",
        fact_key="garden_door",
        expected_value="open",
        confidence=0.84,
    )
    step = duck.step(
        WorldEvent(
            "environment", "world", "The garden door is open.", ("observation",),
            0.05, 0.35, (("garden_door", "open"),), True,
        ),
        allow_inner_speech=False,
    )
    resolved = duck.expectation_state.get(record.expectation_id)
    assert resolved.status == "fulfilled"
    assert resolved.observed_value == "open"
    assert step.developer_trace["expectations"]["resolved"][0]["outcome"] == "fulfilled"
    assert any("expectation_fulfilled" in memory.tags for memory in duck.state.memories)
    assert duck.state.world_facts == {}
    assert step.inner_cognition.thought is None


def test_perceived_counterevidence_violates_expectation_and_recruits_coherence_same_cycle():
    duck = LivingDuck(_quiet_state("expectation-violated"))
    record = duck.register_expectation(
        "I expect the garden door to be open.",
        fact_key="garden_door",
        expected_value="open",
        confidence=0.91,
    )
    step = duck.step(
        WorldEvent(
            "environment", "world", "The garden door is locked.", ("observation",),
            -0.05, 0.45, (("garden_door", "locked"),), True,
        ),
        allow_inner_speech=False,
    )
    resolved = duck.expectation_state.get(record.expectation_id)
    assert resolved.status == "violated"
    assert resolved.observed_value == "locked"
    event_tags = set(step.developer_trace["cognitive_field"]["event_tags"])
    assert {"expectation_violation", "prediction_error", "inconsistency"}.issubset(event_tags)
    assert any(motive.theme == "coherence" for motive in duck.cognitive_state.motives.values())
    assert any("expectation_violation" in memory.tags for memory in duck.state.memories)
    assert any("What happened did not match what I expected" in memory.text for memory in duck.state.memories)
    assert duck.state.world_facts == {}
    assert step.inner_cognition.thought is None


def test_unrelated_perceived_fact_does_not_resolve_expectation():
    duck = LivingDuck(_quiet_state("expectation-unrelated"))
    record = duck.register_expectation(
        "I expect the garden door to be open.",
        fact_key="garden_door",
        expected_value="open",
    )
    duck.step(
        WorldEvent(
            "environment", "world", "The hall light came on.", ("observation",),
            0.0, 0.30, (("hall_light", "on"),), True,
        ),
        allow_inner_speech=False,
    )
    assert duck.expectation_state.get(record.expectation_id).status == "open"
    assert duck.state.world_facts == {}


def test_deadline_passage_marks_overdue_not_violated_and_becomes_sparse_uncertainty_pressure():
    duck = LivingDuck(_quiet_state("expectation-overdue"))
    record = duck.register_expectation(
        "I expect the delivery to be here soon.",
        fact_key="delivery_status",
        expected_value="arrived",
        due_in=1,
        confidence=0.80,
    )

    first = duck.heartbeat(allow_inner_speech=False)
    assert duck.expectation_state.get(record.expectation_id).status == "open"
    assert first.inner_cognition.thought is None

    second = duck.heartbeat(allow_inner_speech=False)
    overdue = duck.expectation_state.get(record.expectation_id)
    assert overdue.status == "overdue"
    assert record.expectation_id in second.developer_trace["expectations"]["became_overdue"]
    signal = second.developer_trace["endogenous_dynamics"]["signal"]
    assert signal["kind"] == "expectation"
    assert signal["key"] == f"expectation:{record.expectation_id}"
    assert "expectation_pressure" in signal["tags"]
    assert "expectation_violation" not in signal["tags"]
    assert second.developer_trace["executive_recruitment"]["invoked"] is False
    assert not any("expectation_violation" in memory.tags for memory in duck.state.memories)

    third = duck.heartbeat(allow_inner_speech=False)
    assert third.developer_trace["endogenous_dynamics"]["emitted"] is False
    assert duck.endogenous_state.emission_counts[f"expectation:{record.expectation_id}"] == 1


def test_low_confidence_overdue_expectation_does_not_force_endogenous_inquiry():
    duck = LivingDuck(_quiet_state("expectation-low-confidence"))
    record = duck.register_expectation(
        "I tentatively expect the package to arrive.",
        fact_key="package_status",
        expected_value="arrived",
        due_in=1,
        confidence=0.40,
    )
    duck.heartbeat(allow_inner_speech=False)
    second = duck.heartbeat(allow_inner_speech=False)
    assert duck.expectation_state.get(record.expectation_id).status == "overdue"
    assert second.developer_trace["endogenous_dynamics"]["emitted"] is False
    assert f"expectation:{record.expectation_id}" not in duck.endogenous_state.emission_counts


def test_resolving_overdue_expectation_retires_its_scheduler_pressure():
    duck = LivingDuck(_quiet_state("expectation-pressure-resolution"))
    record = duck.register_expectation(
        "I expect the signal light to turn green.",
        fact_key="signal_light",
        expected_value="green",
        due_in=1,
        confidence=0.90,
    )
    duck.heartbeat(allow_inner_speech=False)
    duck.heartbeat(allow_inner_speech=False)
    key = f"expectation:{record.expectation_id}"
    assert key in duck.endogenous_state.latched_signals

    duck.step(
        WorldEvent(
            "environment", "world", "The signal light turns green.", ("observation",),
            0.05, 0.30, (("signal_light", "green"),), True,
        ),
        allow_inner_speech=False,
    )
    assert duck.expectation_state.get(record.expectation_id).status == "fulfilled"
    assert key not in duck.endogenous_state.latched_signals
    assert key not in duck.endogenous_state.last_emitted_tick
    assert key not in duck.endogenous_state.emission_counts


def test_revision_preserves_prediction_lineage():
    duck = LivingDuck(_quiet_state("expectation-revision"))
    original = duck.register_expectation(
        "I expect the door to stay open.",
        fact_key="door",
        expected_value="open",
        due_in=4,
        confidence=0.72,
    )
    revised = duck.revise_expectation(
        original.expectation_id,
        proposition="I now expect the door to be closed.",
        expected_value="closed",
        due_in=3,
        confidence=0.81,
    )
    assert duck.expectation_state.get(original.expectation_id).status == "superseded"
    assert revised.revision_of == original.expectation_id
    assert revised.expected_value == "closed"
    assert revised.status == "open"


def test_hidden_world_change_cannot_resolve_subject_expectation(tmp_path):
    root = tmp_path / "hidden-expectation"
    host = PersistentDuckHost.open(root, name="Aster", subject_id="hidden-expectation")
    host.duck.state.needs.update(_quiet_state("template").needs)
    record = host.duck.register_expectation(
        "I expect the archive door to remain open.",
        fact_key="archive_door",
        expected_value="open",
        due_in=6,
        confidence=0.88,
    )
    host.schedule_world_event(
        WorldEvent(
            "environment", "world", "The archive door locks while Aster is elsewhere.",
            ("door", "lock"), 0.0, 0.40, (("archive_door", "locked"),), False,
        ),
        due_in=1,
    )
    host.heartbeat(1, allow_inner_speech=False)
    assert host.environment.world_facts["archive_door"] == "locked"
    assert host.duck.state.world_facts == {}
    unresolved = host.duck.expectation_state.get(record.expectation_id)
    assert unresolved.status == "open"
    assert unresolved.observed_value == ""
    assert not any("expectation_violation" in memory.tags for memory in host.duck.state.memories)


def test_perceived_scheduled_world_event_can_resolve_expectation(tmp_path):
    root = tmp_path / "perceived-expectation"
    host = PersistentDuckHost.open(root, name="Aster", subject_id="perceived-expectation")
    record = host.duck.register_expectation(
        "I expect the workshop light to turn on.",
        fact_key="workshop_light",
        expected_value="on",
        due_in=3,
    )
    host.schedule_world_event(
        WorldEvent(
            "environment", "world", "The workshop light turns on.", ("observation",),
            0.0, 0.35, (("workshop_light", "on"),), True,
        ),
        due_in=1,
    )
    step = host.heartbeat(1, allow_inner_speech=False)[0]
    assert host.environment.fact("workshop_light") == "on"
    assert host.duck.state.world_facts == {}
    assert host.duck.expectation_state.get(record.expectation_id).status == "fulfilled"
    assert step.developer_trace["expectations"]["resolved"][0]["expectation_id"] == record.expectation_id


def test_expectation_ledger_survives_restart_separately_from_environment(tmp_path):
    root = tmp_path / "expectation-restart"
    host = PersistentDuckHost.open(root, name="Aster", subject_id="expectation-restart")
    record = host.duck.register_expectation(
        "I expect Morgan to leave the map on the table.",
        fact_key="map_location",
        expected_value="table",
        due_in=5,
        confidence=0.86,
    )
    host.save()
    path = root / "expectations_v010.json"
    assert path.exists()
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == EXPECTATION_STATE_SCHEMA
    assert payload["records"][0]["expectation_id"] == record.expectation_id

    reopened = PersistentDuckHost.open(root)
    restored = reopened.duck.expectation_state.get(record.expectation_id)
    assert restored.proposition == record.proposition
    assert restored.expected_value == "table"
    assert restored.confidence == pytest.approx(0.86)
    assert reopened.duck.state.world_facts == {}
    assert reopened.status()["active_expectation_count"] == 1


def test_expectation_schema_rejects_unknown_versions():
    with pytest.raises(ValueError):
        ExpectationLedgerState.from_dict(
            {
                "schema_version": "micropsi-duck.expectations.v999",
                "expectation_counter": 0,
                "records": [],
            }
        )
