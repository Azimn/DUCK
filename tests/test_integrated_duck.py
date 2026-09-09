from dataclasses import fields, is_dataclass
from enum import Enum

from duck import (
    ApprovedLanguagePacket,
    BeliefStance,
    LivingDuck,
    ModelExpression,
    ModelInnerVoice,
    PersistentDuckHost,
    SubjectState,
    WorldEvent,
)


def _contains_float(value) -> bool:
    if isinstance(value, float):
        return True
    if isinstance(value, Enum):
        return False
    if is_dataclass(value):
        return any(_contains_float(getattr(value, item.name)) for item in fields(value))
    if isinstance(value, dict):
        return any(_contains_float(k) or _contains_float(v) for k, v in value.items())
    if isinstance(value, (tuple, list, set, frozenset)):
        return any(_contains_float(item) for item in value)
    return False


class FakePort:
    def __init__(self, text="I should think about this."):
        self.text = text
        self.messages = None

    def complete(self, messages, *, temperature=0.7):
        self.messages = messages
        return self.text


def test_same_present_event_differs_after_different_lived_history():
    neutral = LivingDuck(SubjectState.create("A", "neutral"))
    hurt = LivingDuck(SubjectState.create("B", "hurt"))

    neutral.heartbeat(allow_inner_speech=False)
    danger = hurt.step(WorldEvent("encounter", "Morgan", "Morgan threatens me.", ("social", "threat", "conflict"), -0.8, 0.9))
    hurt.resolve_outcome(
        danger.action_id,
        success=0.8,
        valence=-0.7,
        description="Backing away kept me safe, but Morgan frightened me.",
        tags=("threat", "safety"),
    )

    present = WorldEvent("message", "Morgan", "Morgan says hello.", ("social", "conversation"), 0.0, 0.3)
    neutral_now = neutral.step(present)
    hurt_now = hurt.step(present)

    assert neutral_now.subjective_moment != hurt_now.subjective_moment
    assert hurt_now.recalled_memory_ids
    assert any("Morgan" in line or "fright" in line for line in hurt_now.subjective_moment.recollections)
    assert hurt_now.developer_trace["mechanistic_snapshot"]["affect"]["fear"] > neutral_now.developer_trace["mechanistic_snapshot"]["affect"]["fear"]


def test_subjective_moment_still_contains_no_raw_floats_in_integrated_runtime():
    duck = LivingDuck(SubjectState.create("Duck", "no-floats"))
    step = duck.step(WorldEvent("encounter", "Morgan", "Morgan threatens me.", ("social", "threat"), -0.7, 0.9))
    assert not _contains_float(step.subjective_moment)
    assert _contains_float(step.developer_trace["mechanistic_snapshot"])


def test_world_truth_is_not_automatically_subject_belief(tmp_path):
    host = PersistentDuckHost.open(tmp_path / "epistemic", name="Duck", subject_id="epistemic")
    host.set_world_fact("door", "the blue door is unlocked", perceived=False)
    assert host.world_fact("door") == "the blue door is unlocked"
    assert host.duck.state.world_facts == {}
    assert "door" not in host.duck.state.beliefs

    host.set_world_fact(
        "door",
        "the blue door is unlocked",
        perceived=True,
        description="The blue door is unlocked.",
        allow_inner_speech=False,
    )
    assert host.world_fact("door") == "the blue door is unlocked"
    assert host.duck.state.world_facts == {}
    assert host.duck.state.beliefs["door"].stance is BeliefStance.TRUE
    assert any(memory.provenance.value == "world_fact" for memory in host.duck.state.memories)


def test_broken_commitment_changes_later_first_person_state():
    duck = LivingDuck(SubjectState.create("Duck", "commitment"))
    item = duck.create_commitment("Jay", "Jay will come back.", importance=1.0)
    duck.resolve_commitment(item.commitment_id, kept=False, outcome="Jay did not come back.")
    result = duck.step(WorldEvent("message", "Jay", "Jay says hello.", ("social",), 0.0, 0.3))
    assert any("wary" in concern.lower() for concern in result.subjective_moment.concerns)
    assert any("Jay" in memory.text for memory in duck.state.memories)
    assert duck.state.relationship("Jay").trust < 0.5


def test_positive_outcome_changes_learned_action_association():
    duck = LivingDuck(SubjectState.create("Duck", "learning"))
    step = duck.step(WorldEvent("object", "world", "A strange glorp appears.", ("novel", "glorp"), 0.0, 0.5), allow_inner_speech=False)
    duck.resolve_outcome(step.action_id, success=1.0, valence=0.8, description="That choice worked well.", tags=("glorp",))
    learned = duck.state.adaptive.action_associations
    assert "glorp" in learned
    assert learned["glorp"][step.selected_action] > 0.0


def test_language_lesion_preserves_behavior_and_learning():
    duck = LivingDuck(SubjectState.create("Duck", "lesion"))
    step = duck.step(WorldEvent("encounter", "world", "Something dangerous approaches.", ("threat",), -0.8, 0.9), allow_inner_speech=False)
    assert step.inner_cognition.thought is None
    assert step.selected_action
    duck.resolve_outcome(step.action_id, success=0.9, valence=0.6, description="The action kept me safe.", tags=("threat",))
    assert duck.state.adaptive.action_associations["threat"][step.selected_action] > 0


def test_endogenous_heartbeat_can_generate_unprompted_action():
    state = SubjectState.create("Duck", "heartbeat")
    state.needs["affiliation"] = 0.95
    duck = LivingDuck(state)
    step = duck.heartbeat()
    assert step.selected_action == "seek_connection"
    assert any("connection" in concern.lower() for concern in step.subjective_moment.concerns)


def test_persistence_roundtrip_preserves_same_subject_and_history(tmp_path):
    host = PersistentDuckHost.open(tmp_path / "duck", name="Aster", subject_id="aster-1")
    first = host.interact("Hello, Aster.")
    assert first.action_id
    before = host.status()

    reopened = PersistentDuckHost.open(tmp_path / "duck")
    after = reopened.status()
    assert after["subject_id"] == "aster-1"
    assert after["tick"] == before["tick"]
    assert after["memory_count"] == before["memory_count"]
    assert (tmp_path / "duck" / "events.jsonl").exists()


def test_llm_inner_voice_and_expression_only_receive_approved_string_state():
    inner_port = FakePort("I wonder what they mean.")
    inner = ModelInnerVoice(inner_port)
    duck = LivingDuck(SubjectState.create("Aster", "llm-boundary"), cognition=inner)
    step = duck.step(WorldEvent("message", "Sarah", "Sarah says hello.", ("social",), 0.0, 0.3))
    assert inner.last_packet is not None
    assert not _contains_float(inner.last_packet)

    expression_port = FakePort("Hello.")
    expression = ModelExpression(expression_port)
    packet = ApprovedLanguagePacket.from_moment(
        step.subjective_moment,
        user_text="hello",
        private_thought=step.inner_cognition.thought,
        selected_action=step.selected_action,
        character_name="Aster",
    )
    response = expression.render(packet)
    assert response == "Hello."
    assert expression.last_packet is not None
    assert not _contains_float(expression.last_packet)
