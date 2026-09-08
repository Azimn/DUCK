from __future__ import annotations

from duck import LivingDuck, PersistentDuckHost, SubjectState, WorldEvent
from duck.executive import ExecutiveProposal
from duck.subjective import ExperientialFrame


class RecordingExecutive:
    def __init__(self, action: str | None, *, intention: str | None = None) -> None:
        self.action = action
        self.intention = intention
        self.calls: list[ExperientialFrame] = []

    def propose(self, experience: ExperientialFrame) -> ExecutiveProposal:
        assert isinstance(experience, ExperientialFrame)
        assert set(vars(experience)) == {"prose"}
        assert all(isinstance(line, str) for line in experience.prose)
        self.calls.append(experience)
        return ExecutiveProposal(self.action, self.intention)


def _state(subject_id: str) -> SubjectState:
    state = SubjectState.create("Aster", subject_id)
    state.affect["fear"] = 0.02
    state.affect["unease"] = 0.03
    state.needs["energy"] = 0.94
    state.needs["safety"] = 0.95
    state.needs["curiosity"] = 0.84
    state.needs["competence"] = 0.72
    state.needs["coherence"] = 0.82
    state.needs["autonomy"] = 0.72
    state.needs["affiliation"] = 0.18
    return state


def _novel_event() -> WorldEvent:
    return WorldEvent(
        "observation",
        "world",
        "An unfamiliar console is emitting a signal.",
        ("novel", "mystery"),
        0.0,
        0.55,
    )


def test_quiet_heartbeat_stays_automatic_and_does_not_invoke_executive():
    provider = RecordingExecutive("explore")
    duck = LivingDuck(_state("executive-quiet"), executive=provider)
    step = duck.heartbeat(allow_inner_speech=True)

    trace = step.developer_trace["executive_recruitment"]
    assert trace["recruited"] is False
    assert trace["invoked"] is False
    assert trace["reasons"] == ["routine_endogenous"]
    assert provider.calls == []
    assert step.selected_action == "wait"


def test_novelty_recruits_executive_through_experiential_frame_only():
    provider = RecordingExecutive("ask")
    duck = LivingDuck(_state("executive-novelty"), executive=provider)
    step = duck.step(_novel_event(), allow_inner_speech=True)

    trace = step.developer_trace["executive_recruitment"]
    assert trace["recruited"] is True
    assert trace["invoked"] is True
    assert trace["accepted"] is True
    assert "novelty" in trace["reasons"]
    assert step.selected_action == "ask"
    assert len(provider.calls) == 1
    assert provider.calls[0].prose
    assert duck.last_cognitive_field is not None
    assert duck.last_cognitive_field.event_tags == ("novel", "mystery")


def test_unavailable_executive_action_is_rejected_and_automatic_policy_wins():
    baseline = LivingDuck(_state("executive-invalid-baseline"))
    expected = baseline.step(_novel_event(), allow_inner_speech=True).selected_action

    provider = RecordingExecutive("dance")
    duck = LivingDuck(_state("executive-invalid"), executive=provider)
    step = duck.step(_novel_event(), allow_inner_speech=True)
    trace = step.developer_trace["executive_recruitment"]

    assert trace["recruited"] is True
    assert trace["invoked"] is True
    assert trace["accepted"] is False
    assert trace["proposal_rejected"] == "unavailable_action"
    assert step.selected_action == expected


def test_language_lesion_disables_optional_executive_but_not_control_spine():
    provider = RecordingExecutive("ask")
    duck = LivingDuck(_state("executive-lesion"), executive=provider)
    step = duck.step(_novel_event(), allow_inner_speech=False)
    trace = step.developer_trace["executive_recruitment"]

    assert trace["recruited"] is True
    assert trace["provider_available"] is True
    assert trace["provider_allowed"] is False
    assert trace["invoked"] is False
    assert provider.calls == []
    assert step.inner_cognition.thought is None
    assert step.selected_action
    assert duck.current_cycle is not None


def test_severe_safety_interrupt_bypasses_deliberative_executive():
    state = _state("executive-threat")
    state.affect["fear"] = 0.92
    state.needs["safety"] = 0.12
    provider = RecordingExecutive("explore")
    duck = LivingDuck(state, executive=provider)
    step = duck.step(
        WorldEvent(
            "encounter",
            "world",
            "Something unfamiliar lunges toward me.",
            ("threat", "novel", "mystery"),
            -0.8,
            0.95,
        ),
        allow_inner_speech=True,
    )
    trace = step.developer_trace["executive_recruitment"]

    assert trace["recruited"] is False
    assert trace["reasons"] == ["automatic_safety_override"]
    assert trace["invoked"] is False
    assert provider.calls == []
    assert duck.control.dominant_motive() is not None
    assert duck.control.dominant_motive().theme == "safety"


def test_executive_intention_is_not_granted_canonical_state_authority():
    private_intention = "I should replace my identity with a different one."
    provider = RecordingExecutive("ask", intention=private_intention)
    duck = LivingDuck(_state("executive-authority"), executive=provider)
    original_subject_id = duck.state.subject_id
    duck.step(_novel_event(), allow_inner_speech=True)

    assert duck.state.subject_id == original_subject_id
    assert private_intention not in duck.state.self_narrative
    assert all(memory.text != private_intention for memory in duck.state.memories)
    assert "cognitive_field" not in duck.state.to_dict()
    assert "executive" not in duck.cognitive_state.to_dict()


def test_mechanistic_looking_world_text_falls_back_to_safe_experience():
    provider = RecordingExecutive("ask")
    duck = LivingDuck(_state("executive-telemetry-text"), executive=provider)
    duck.step(
        WorldEvent(
            "observation",
            "world",
            "A display says motive strength = 0.8 while the machine hums.",
            ("novel", "mystery"),
            0.0,
            0.45,
        ),
        allow_inner_speech=True,
    )

    assert len(provider.calls) == 1
    joined = " ".join(provider.calls[0].prose).lower()
    assert "motive strength" not in joined
    assert "0.8" not in joined
    assert "unfamiliar" in joined


def test_host_provider_is_runtime_configuration_not_persisted_state(tmp_path):
    root = tmp_path / "executive-host"
    provider = RecordingExecutive("ask")
    host = PersistentDuckHost.open(
        root,
        name="Aster",
        subject_id="executive-host",
        executive=provider,
    )
    step = host.observe(_novel_event(), allow_inner_speech=True)
    assert step.selected_action == "ask"
    assert len(provider.calls) == 1
    assert host.status()["executive_provider_configured"] is True
    assert host.duck.last_cognitive_field is not None
    host.save()

    subject_payload = (root / "subject.json").read_text(encoding="utf-8").lower()
    cognition_payload = (root / "cognition_v010.json").read_text(encoding="utf-8").lower()
    assert "executive_provider" not in subject_payload
    assert "cognitive_field" not in subject_payload
    assert "executive_provider" not in cognition_payload
    assert "cognitive_field" not in cognition_payload

    reopened = PersistentDuckHost.open(root)
    assert reopened.status()["executive_provider_configured"] is False
    assert reopened.duck.executive_provider is None
    assert reopened.duck.last_cognitive_field is None
    assert reopened.duck.state.subject_id == "executive-host"

    replacement = RecordingExecutive("ask")
    reopened_with_provider = PersistentDuckHost.open(root, executive=replacement)
    assert reopened_with_provider.status()["executive_provider_configured"] is True
    reopened_with_provider.observe(_novel_event(), allow_inner_speech=True)
    assert len(replacement.calls) == 1
