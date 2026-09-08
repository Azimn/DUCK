from dataclasses import asdict, fields, is_dataclass
from enum import Enum

from duck import DuckRuntime, ExperientialFrame, MechanisticSnapshot, RecognitionSignal, SubjectAccessFirewall
from duck.cognition import InnerCognition


def _contains_float(value) -> bool:
    if isinstance(value, float):
        return True
    if isinstance(value, Enum):
        return False
    if is_dataclass(value):
        return any(_contains_float(getattr(value, f.name)) for f in fields(value))
    if isinstance(value, dict):
        return any(_contains_float(k) or _contains_float(v) for k, v in value.items())
    if isinstance(value, (list, tuple, set, frozenset)):
        return any(_contains_float(item) for item in value)
    return False


class SpyCognition:
    def __init__(self):
        self.seen = None

    def generate(self, experience):
        self.seen = experience
        return InnerCognition("I need a moment to think.")


def test_private_cognition_receives_only_experiential_frame():
    spy = SpyCognition()
    runtime = DuckRuntime(cognition=spy)
    snapshot = MechanisticSnapshot(
        affect={"fear": 0.71, "loneliness": 0.43},
        relationship={"trust": 0.31, "guardedness": 0.68, "suspicion": 0.73},
        prediction_error=0.62,
        recognition=RecognitionSignal("Sarah", 0.64),
        action_tendency="step_back",
    )
    result = runtime.step(snapshot)
    assert spy.seen is result.experiential_frame
    assert isinstance(spy.seen, ExperientialFrame)
    assert fields(spy.seen)[0].name == "prose"
    assert len(fields(spy.seen)) == 1
    assert all(isinstance(line, str) for line in spy.seen.prose)
    assert not _contains_float(spy.seen)
    assert _contains_float(result.developer_trace["mechanistic_snapshot"])


def test_raw_magnitude_changes_experience_without_leaking_value():
    firewall = SubjectAccessFirewall()
    low = firewall.project(MechanisticSnapshot(relationship={"suspicion": 0.20}))
    high = firewall.project(MechanisticSnapshot(relationship={"suspicion": 0.80}))
    assert not any("suspicious" in i.content.lower() for i in low.impressions)
    assert any("suspicious" in i.content.lower() for i in high.impressions)
    experience = firewall.experience(high)
    rendered = repr(experience)
    assert "0.8" not in rendered
    assert "80%" not in rendered


def test_recognition_uncertainty_is_human_like_not_numeric():
    moment = SubjectAccessFirewall().project(MechanisticSnapshot(recognition=RecognitionSignal("Sarah", 0.64)))
    recognition = next(i for i in moment.impressions if i.channel == "recognition")
    assert recognition.content == "I think that's Sarah."
    experience = SubjectAccessFirewall().experience(moment)
    assert recognition.content in experience.prose
    assert "0.64" not in repr(experience)
    assert "64%" not in repr(experience)


def test_introspective_cause_can_remain_hidden_from_subject():
    snapshot = MechanisticSnapshot(affect={"unease": 0.80}, hidden_causes={"unease": "the unresolved argument from yesterday"})
    result = DuckRuntime().step(snapshot)
    impression = next(i for i in result.subjective_moment.impressions if "uneasy" in i.content.lower())
    assert impression.content == "I feel uneasy, but I'm not sure why."
    assert "unresolved argument" not in repr(result.experiential_frame)
    assert result.developer_trace["mechanistic_snapshot"]["hidden_causes"]["unease"] == "the unresolved argument from yesterday"


def test_cause_may_become_accessible_when_the_subject_has_access_to_it():
    snapshot = MechanisticSnapshot(
        affect={"unease": 0.80},
        hidden_causes={"unease": "what happened yesterday"},
        introspectively_accessible_causes=frozenset({"unease"}),
    )
    firewall = SubjectAccessFirewall()
    experience = firewall.project_experience(snapshot)
    assert "I feel uneasy about what happened yesterday." in experience.prose


def test_inner_speech_is_optional_but_action_can_still_happen():
    runtime = DuckRuntime()
    snapshot = MechanisticSnapshot(affect={"fear": 0.90}, action_tendency="step_back")
    result = runtime.step(snapshot, allow_inner_speech=False)
    assert result.inner_cognition.thought is None
    assert result.selected_action == "step_back"
    assert "I want to step back." in result.experiential_frame.prose


def test_deterministic_inner_voice_uses_first_person_experiential_state():
    runtime = DuckRuntime()
    result = runtime.step(MechanisticSnapshot(affect={"fear": 0.90}, action_tendency="step_back"))
    assert result.inner_cognition.thought == "I don't like this. I should give myself some space."
    assert "0.9" not in result.inner_cognition.thought


def test_experiential_types_have_no_float_fields():
    firewall = SubjectAccessFirewall()
    experience = firewall.project_experience(
        MechanisticSnapshot(affect={"fear": 0.55}, relationship={"trust": 0.20}, recognition=RecognitionSignal("Sarah", 0.55))
    )
    assert not _contains_float(experience)
    assert not _contains_float(asdict(experience))
