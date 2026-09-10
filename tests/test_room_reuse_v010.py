from dataclasses import replace
from copy import deepcopy
import json

import pytest

from duck import LivingDuck, PersistentDuckHost, RoomObject, RoomState, Vec3
from duck.perception_v010 import FactObservation, Modality, SensoryEvidence
from duck.room_v010 import RoomWorld
from duck.spatial_v010 import AttentionSelector, LocatedStimulus, ObservationPacket, ObserverMismatch, ObserverState, PerceptionFilter


def stimulus(name="visible", *, position=Vec3(2, 0, 0), modality=Modality.VISION, occluded=False):
    return LocatedStimulus(name, position, SensoryEvidence(modality, "world", "A door is here.", strength=1,
                             observed_facts=(FactObservation("door", "open", "vision"),)), occluded)


@pytest.mark.parametrize("item", [stimulus(position=Vec3(-2, 0, 0)), stimulus(position=Vec3(40, 0, 0)),
                                  stimulus(occluded=True), stimulus(position=Vec3(2, 0, 0), modality=Modality.TOUCH)])
def test_inaccessible_world_information_never_becomes_evidence(item):
    observer = ObserverState("aster")
    assert PerceptionFilter().filter(ObservationPacket("aster", (item,)), observer) == ()


def test_private_observer_identity_and_modality_access():
    observer = ObserverState("aster")
    with pytest.raises(ObserverMismatch):
        PerceptionFilter().filter(ObservationPacket("morgan", (stimulus(),)), observer)
    hearing = stimulus(position=Vec3(-2, 0, 0), modality=Modality.AUDITION)
    rows = PerceptionFilter().filter(ObservationPacket("aster", (hearing,)), observer)
    assert rows and rows[0].evidence.reliability < 1
    blocked = PerceptionFilter().filter(ObservationPacket("aster", (replace(hearing, occluded=True),)), observer)
    assert 0 < blocked[0].evidence.reliability < rows[0].evidence.reliability


def test_attention_is_bounded_and_order_independent():
    observer = ObserverState("aster")
    items = tuple(stimulus(str(i), position=Vec3(i + 1, 0, 0)) for i in range(12))
    left = PerceptionFilter().filter(ObservationPacket("aster", items), observer)
    right = PerceptionFilter().filter(ObservationPacket("aster", tuple(reversed(items))), observer)
    assert AttentionSelector().select(left, capacity=2) == AttentionSelector().select(right, capacity=2)
    assert len(AttentionSelector().select(left, capacity=2)) == 2


def room_with_door():
    return RoomState(auto_day_cycle=False, light=.8,
                     objects={"door": RoomObject("door", "The blue door", Vec3(1, 0, 0), openable=True)})


def test_native_room_refreshes_evidence_and_only_enacted_actions_learn(tmp_path):
    host = PersistentDuckHost.open(tmp_path)
    room = room_with_door()
    room.objects["hidden"] = RoomObject("hidden", "Secret cabinet", Vec3(-1, 0, 0), openable=True)
    host.configure_room(room)
    assert not host.duck.state.beliefs
    step = host.room_heartbeat(allow_inner_speech=False)[0]
    assert step.developer_trace["perception"]["legacy_hints"] is False
    assert step.developer_trace["affordances"]["compatibility_catalog"] is False
    assert "object:door:state" in host.duck.state.beliefs
    assert "object:hidden:state" not in host.duck.state.beliefs
    assert all("Secret cabinet" not in m.text for m in host.duck.state.memories)
    assert host.duck.state.pending_action is None
    assert step.selected_action in host.duck.cognitive_state.strategy_success
    host.environment.room.forward = Vec3(-1, 0, 0)
    host.room_heartbeat(allow_inner_speech=False)
    assert "object:hidden:state" in host.duck.state.beliefs


def test_scene_refresh_removes_unavailable_targets(tmp_path):
    host = PersistentDuckHost.open(tmp_path)
    host.configure_room(room_with_door())
    first = host.room_heartbeat(execute_actions=False)[0]
    assert any(a["target"] == "door" for a in first.developer_trace["affordances"]["available"])
    host.environment.room.objects["door"].occluded = True
    second = host.room_heartbeat(execute_actions=False)[0]
    assert {a["action"] for a in second.developer_trace["affordances"]["available"]} == {"wait", "rest"}
    assert host.duck.cognitive_state.strategy_success == {}


def test_room_object_execution_is_real_and_failures_do_not_open_door():
    room = room_with_door()
    world = RoomWorld(room)
    assert world.execute("open", "missing")[0] == 0
    assert not room.objects["door"].opened
    assert world.execute("open", "door")[0] == 1
    assert room.objects["door"].opened
    assert world.execute("open", "door")[0] == 0
    assert not any(a.action == "open" for a in world.affordances("vision:door"))


def test_room_restart_preserves_world_and_next_behavior(tmp_path):
    host = PersistentDuckHost.open(tmp_path)
    host.configure_room(room_with_door())
    host.room_heartbeat(4, allow_inner_speech=False)
    reopened = PersistentDuckHost.open(tmp_path)
    assert reopened.environment.to_dict() == host.environment.to_dict()
    left = host.room_heartbeat(allow_inner_speech=False)[0]
    right = reopened.room_heartbeat(allow_inner_speech=False)[0]
    assert left.selected_action == right.selected_action
    assert left.developer_trace["candidate_actions"] == right.developer_trace["candidate_actions"]
    assert host.duck.body.to_dict() == reopened.duck.body.to_dict()


def test_catchup_retains_time_debt_without_fabricating_unlived_history(tmp_path):
    host = PersistentDuckHost.open(tmp_path)
    host.configure_room(room_with_door())
    first = host.catch_up_room(650, max_ticks=3)
    assert first == {"requested_ticks": 10, "applied_ticks": 3, "remaining_seconds": 470}
    assert host.duck.state.tick == 3
    reopened = PersistentDuckHost.open(tmp_path)
    reopened.catch_up_room(0, max_ticks=7)
    assert reopened.duck.state.tick == 10
    assert reopened.environment.room.catchup_remainder == 50
    assert reopened.environment.room.simulation_seconds == 43200 + 600


def test_room_body_and_time_recover_as_one_generation(tmp_path):
    host = PersistentDuckHost.open(tmp_path)
    host.configure_room(room_with_door())
    before = deepcopy(host._snapshot_payloads())
    def crash(label):
        if label == "component:environment_v010.json":
            raise RuntimeError("simulated crash")
    host.snapshot_store._checkpoint = crash
    with pytest.raises(RuntimeError, match="simulated crash"):
        host.catch_up_room(600)
    assert PersistentDuckHost.open(tmp_path)._snapshot_payloads() == before


def test_daylight_is_a_function_of_simulation_time_only():
    room = room_with_door()
    room.auto_day_cycle = True
    room.simulation_seconds = 4 * 3600
    world = RoomWorld(room)
    world.advance()
    assert room.light == .08
    room.simulation_seconds = 12 * 3600
    world.advance()
    assert room.light == .65


def test_room_longer_life_stays_bounded_and_recovers_energy(tmp_path):
    host = PersistentDuckHost.open(tmp_path)
    host.configure_room(room_with_door())
    host.duck.state.needs["energy"] = .1
    steps = host.room_heartbeat(120, allow_inner_speech=False)
    assert any(step.selected_action == "rest" for step in steps)
    assert host.duck.state.needs["energy"] > .1
    assert all(0 <= v <= 1 for v in host.duck.state.needs.values())
    assert not host.duck.state.world_facts
    assert len(host.environment.room.objects) == 1
    json.dumps(host._snapshot_payloads())


def test_default_heartbeat_uses_configured_room_and_keeps_scheduled_changes(tmp_path):
    from duck import WorldEvent
    host = PersistentDuckHost.open(tmp_path)
    room = room_with_door()
    room.objects["door"].position = Vec3(-1, 0, 0)
    host.configure_room(room)
    host.schedule_world_event(WorldEvent("change", "world", "Secret opening.",
        world_facts=(("object:door:state", "open"),), perceived=False), due_in=2)
    before_time = host.environment.room.simulation_seconds
    steps = host.heartbeat(3, allow_inner_speech=False)
    assert all(not s.developer_trace["affordances"]["compatibility_catalog"] for s in steps)
    assert host.world_fact("object:door:state") == "open"
    assert host.environment.room.objects["door"].opened
    assert "object:door:state" not in host.environment.world_facts
    assert "object:door:state" not in host.duck.state.beliefs
    assert host.environment.room.simulation_seconds == before_time + 180
    assert not host.environment.scheduled


def test_catchup_delivers_scheduled_room_changes(tmp_path):
    from duck import WorldEvent
    host = PersistentDuckHost.open(tmp_path)
    host.configure_room(room_with_door())
    host.schedule_world_event(WorldEvent("change", "world", "The door opens.",
        world_facts=(("object:door:state", "open"),), perceived=False), due_in=2)
    host.catch_up_room(180)
    assert host.world_fact("object:door:state") == "open"
    assert host.duck.state.beliefs["object:door:state"].text == "open"
    assert host.duck.state.tick == 3


def test_comparison_contracts_require_selected_components_to_pass():
    from duck.component_comparison import compare
    report = compare()
    assert report["passed"]
    spatial = report["results"]["spatial_access"]
    assert spatial["selected_passes"] == spatial["case_count"]
    assert spatial["baseline_passes"] < spatial["selected_passes"]
    assert report["results"]["social_affordances"]["selected_passes"] == 4
