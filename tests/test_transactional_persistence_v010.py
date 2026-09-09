from __future__ import annotations

import json

import pytest

from duck import PersistentDuckHost
from duck.living import WorldEvent
from duck.persistence_v010 import SNAPSHOT_DIRNAME, SNAPSHOT_MANIFEST
from duck.subjective import PrivateInteriorState


class SimulatedCrash(RuntimeError):
    pass


def _seed_committed_host(tmp_path):
    root = tmp_path / "transactional-host"
    host = PersistentDuckHost.open(root, name="Aster", subject_id="transactional-subject")
    host.private_interior = PrivateInteriorState(experience=("I feel steady.",))
    host.duck.state.self_narrative.append("I remember the first committed generation.")
    host.save()
    assert host.snapshot_generation == 1
    return root, host


def _mutate_next_generation(host) -> None:
    host.duck.state.self_narrative.append("I changed after the first committed generation.")
    host.duck.register_expectation(
        "I expect the west door to open.",
        fact_key="door:west",
        expected_value="open",
        due_in=4,
    )
    host.duck.causal_state.observe_transition(
        "ask",
        "explore",
        outcome="fulfilled",
        tick=host.duck.state.tick + 1,
    )
    host.environment.schedule(
        host.duck.state.tick,
        WorldEvent(
            "observation",
            "world",
            "The west door opens.",
            ("door",),
            0.0,
            0.2,
            world_facts=(("door:west", "open"),),
        ),
        due_in=4,
    )
    host.private_interior = PrivateInteriorState(experience=("I feel changed.",))


def _assert_first_generation_recovered(root) -> None:
    reopened = PersistentDuckHost.open(root)
    assert reopened.snapshot_generation == 1
    assert "I remember the first committed generation." in reopened.duck.state.self_narrative
    assert "I changed after the first committed generation." not in reopened.duck.state.self_narrative
    assert reopened.duck.expectations() == []
    assert reopened.duck.causal_state.transition("ask", "explore") is None
    assert len(reopened.environment.scheduled) == 0
    assert reopened.private_interior is not None
    assert reopened.private_interior.experience == ("I feel steady.",)


@pytest.mark.parametrize(
    "crash_label",
    [
        "component:causal_v010.json",
        "component:cognition_v010.json",
        "component:endogenous_v010.json",
        "component:environment_v010.json",
        "component:expectations_v010.json",
        "component:private_interior.json",
        "component:subject.json",
        "generation_metadata",
        "generation_renamed",
    ],
)
def test_crash_before_manifest_commit_reopens_previous_complete_generation(tmp_path, crash_label):
    root, host = _seed_committed_host(tmp_path)
    _mutate_next_generation(host)

    def crash(label: str) -> None:
        if label == crash_label:
            raise SimulatedCrash(label)

    host.snapshot_store._checkpoint = crash
    with pytest.raises(SimulatedCrash):
        host.save()

    _assert_first_generation_recovered(root)


def test_manifest_swap_is_the_commit_point_even_if_process_dies_immediately_after(tmp_path):
    root, host = _seed_committed_host(tmp_path)
    _mutate_next_generation(host)

    def crash(label: str) -> None:
        if label == "manifest_committed":
            raise SimulatedCrash(label)

    host.snapshot_store._checkpoint = crash
    with pytest.raises(SimulatedCrash):
        host.save()

    reopened = PersistentDuckHost.open(root)
    assert reopened.snapshot_generation == 2
    assert "I changed after the first committed generation." in reopened.duck.state.self_narrative
    assert len(reopened.duck.expectations()) == 1
    assert reopened.duck.causal_state.transition("ask", "explore") is not None
    assert len(reopened.environment.scheduled) == 1
    assert reopened.private_interior is not None
    assert reopened.private_interior.experience == ("I feel changed.",)


def test_root_json_mirrors_are_not_authority_after_manifest_exists(tmp_path):
    root, host = _seed_committed_host(tmp_path)
    original_subject_id = host.duck.state.subject_id

    (root / "subject.json").write_text("{}", encoding="utf-8")
    (root / "expectations_v010.json").write_text(
        json.dumps({"schema_version": "deliberately-invalid"}),
        encoding="utf-8",
    )

    reopened = PersistentDuckHost.open(root)
    assert reopened.snapshot_generation == 1
    assert reopened.duck.state.subject_id == original_subject_id
    assert reopened.duck.expectations() == []


def test_corrupt_current_generation_falls_back_to_previous_complete_generation(tmp_path):
    root, host = _seed_committed_host(tmp_path)
    _mutate_next_generation(host)
    host.save()
    assert host.snapshot_generation == 2

    generation_two_subject = root / SNAPSHOT_DIRNAME / "gen-00000002" / "subject.json"
    generation_two_subject.write_text("{}", encoding="utf-8")

    reopened = PersistentDuckHost.open(root)
    assert reopened.snapshot_generation == 1
    assert "I remember the first committed generation." in reopened.duck.state.self_narrative
    assert "I changed after the first committed generation." not in reopened.duck.state.self_narrative


def test_legacy_root_state_migrates_to_transactional_snapshot_on_next_save(tmp_path):
    root = tmp_path / "legacy-migration"
    host = PersistentDuckHost.open(root, name="Aster", subject_id="legacy-subject")
    # Simulate the pre-transactional root layout without a committed manifest.
    host.duck.state.self_narrative.append("I existed before transactional snapshots.")
    host._write_compatibility_mirrors(host._snapshot_payloads())
    assert not (root / SNAPSHOT_MANIFEST).exists()

    reopened_legacy = PersistentDuckHost.open(root)
    assert reopened_legacy.snapshot_generation == 0
    assert "I existed before transactional snapshots." in reopened_legacy.duck.state.self_narrative

    reopened_legacy.save()
    assert (root / SNAPSHOT_MANIFEST).exists()
    assert reopened_legacy.snapshot_generation == 1

    reopened_transactional = PersistentDuckHost.open(root)
    assert reopened_transactional.snapshot_generation == 1
    assert "I existed before transactional snapshots." in reopened_transactional.duck.state.self_narrative
