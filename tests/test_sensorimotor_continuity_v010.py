from duck import (
    Affordance, AffordanceSource, BodyState, LivingDuck, PersistentDuckHost,
    RoomObject, RoomProcess, RoomState, Vec3,
)
from duck.body_v010 import BodyDynamics, energy_deficit
from duck.perception_v010 import Modality, SensoryEvidence
from duck.room_v010 import RoomWorld
from duck.sensation_v010 import body_sensory_evidence
from duck.spatial_v010 import AttentionSelector, LocatedStimulus, ObservationPacket, ObserverState, PerceptionFilter


def test_stable_entity_reobservation_is_not_reencoded_as_new_event():
    duck = LivingDuck()
    evidence = SensoryEvidence(Modality.VISION, "world", "The cabinet is here.", strength=.8,
                               features=("object_present",), entity_id="cabinet")
    first = duck.perceive(evidence, allow_inner_speech=False)
    duck.resolve_outcome(first.action_id, success=1, valence=0, description="I waited.")
    second = duck.perceive(evidence, allow_inner_speech=False)
    assert first.developer_trace["perception"]["continuity"] == "new"
    assert first.developer_trace["perception"]["autobiographical_encoding"] is True
    assert second.developer_trace["perception"]["continuity"] == "stable"
    assert second.developer_trace["perception"]["autobiographical_encoding"] is False


def test_perceptual_workspace_survives_transactional_restart(tmp_path):
    host = PersistentDuckHost.open(tmp_path)
    host.configure_room(RoomState(auto_day_cycle=False, light=.8, objects={
        "cabinet": RoomObject("cabinet", "The cabinet", Vec3(2, 0, 0)),
    }))
    host.room_heartbeat(1, execute_actions=False, allow_inner_speech=False)
    assert host.duck.perceptual_workspace.currently_known("cabinet") is not None
    reopened = PersistentDuckHost.open(tmp_path)
    known = reopened.duck.perceptual_workspace.currently_known("cabinet")
    assert known is not None
    assert known.last_seen_tick == host.duck.state.tick


def test_locomotion_changes_pose_and_emits_proprioception():
    room = RoomState(auto_day_cycle=False, light=.8, objects={
        "door": RoomObject("door", "The door", Vec3(4, 0, 0), openable=True),
    })
    world = RoomWorld(room)
    assert any(row.action == "approach" for row in world.affordances("vision:door"))
    outcome = world.execute("approach", "door")
    assert outcome.success == 1
    assert outcome.displacement is not None
    assert room.position.x > 0
    assert room.pending_proprioception
    packet = world.packet("aster")
    proprio = [row for row in packet.stimuli if row.stimulus_id == "proprioception:self"]
    assert proprio and proprio[0].evidence.modality is Modality.PROPRIOCEPTION


def test_turning_changes_which_side_of_room_is_visible():
    room = RoomState(auto_day_cycle=False, light=.8, objects={
        "front": RoomObject("front", "Front object", Vec3(2, 0, 0)),
        "rear": RoomObject("rear", "Rear object", Vec3(-2, 0, 0)),
    })
    world = RoomWorld(room)
    observer = world.observer("aster")
    before = PerceptionFilter().filter(world.packet("aster"), observer)
    assert any(row.stimulus_id == "vision:front" for row in before)
    assert not any(row.stimulus_id == "vision:rear" for row in before)
    assert world.execute("turn_toward", "rear").success == 1
    after = PerceptionFilter().filter(world.packet("aster"), world.observer("aster"))
    assert any(row.stimulus_id == "vision:rear" for row in after)


def test_realized_effort_changes_body_even_when_attempt_is_not_fully_successful():
    body = BodyState(energy_reserve=.8, fatigue_load=.2)
    dynamics = BodyDynamics()
    before = energy_deficit(body)
    dynamics.exert(body, effort=.9, success=.2)
    assert body.energy_reserve < .8
    assert body.fatigue_load > .2
    assert body.exertion_load > 0
    assert energy_deficit(body) > before


def test_body_sensation_competes_in_same_attention_selector():
    body = BodyState(energy_reserve=.15, fatigue_load=.8)
    internal = body_sensory_evidence(body)
    assert internal
    observer = ObserverState("aster")
    external = LocatedStimulus(
        "vision:object", Vec3(2, 0, 0),
        SensoryEvidence(Modality.VISION, "world", "An object is here.", strength=.55,
                        features=("object_present",), entity_id="object"),
    )
    body_rows = tuple(LocatedStimulus(f"interoception:{i}", Vec3(), row) for i, row in enumerate(internal))
    accessible = PerceptionFilter().filter(ObservationPacket("aster", (external, *body_rows)), observer)
    focused = AttentionSelector().select(accessible, capacity=1,
                                         relevant_features=frozenset({"tired_sensation", "exertion_sensation"}))
    assert focused[0].evidence.modality is Modality.INTEROCEPTION


def test_autonomous_person_motion_changes_world_before_subject_perception():
    person = RoomObject("morgan", "Morgan", Vec3(5, 0, 0), is_person=True)
    process = RoomProcess("morgan-walk", "move", "morgan", interval_ticks=1,
                          next_tick=0, delta=Vec3(-1, 0, 0))
    room = RoomState(auto_day_cycle=False, light=.8, objects={"morgan": person},
                     processes={process.process_id: process})
    world = RoomWorld(room)
    before = room.objects["morgan"].position.x
    world.advance()
    assert room.objects["morgan"].position.x < before
    packet = world.packet("aster")
    visual = next(row for row in packet.stimuli if row.stimulus_id == "vision:morgan")
    assert "approaching_person" in visual.evidence.features


def test_threat_appraisal_can_mobilize_body_without_becoming_body_truth_input():
    duck = LivingDuck()
    before = duck.body.autonomic_arousal
    evidence = SensoryEvidence(
        Modality.AUDITION, "morgan", "Morgan is shouting while coming closer.",
        strength=.9, reliability=.9,
        features=("loud_voice", "approaching_person", "person_present"), entity_id="morgan",
    )
    step = duck.perceive(evidence, affordances=(Affordance("wait", AffordanceSource.INTERNAL),),
                         allow_inner_speech=False)
    assert step.developer_trace["appraisal"]["threat_relevance"] > 0
    assert duck.body.autonomic_arousal > before
