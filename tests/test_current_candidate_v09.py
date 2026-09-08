from duck import LivingDuck as PublicLivingDuck, PersistentDuckHost
from duck.living import MemoryProvenance, SubjectState, WorldEvent
from duck.living_v09 import LivingDuck as V09LivingDuck
from duck.living_v010 import LivingDuck as V010LivingDuck
from duck.host_v010 import PersistentDuckHostV010


def test_public_package_uses_micropsiduck_v010_candidate(tmp_path):
    assert PublicLivingDuck is V010LivingDuck
    assert PersistentDuckHost is PersistentDuckHostV010
    host = PersistentDuckHost.open(tmp_path / "current", name="Aster", subject_id="current-v010")
    assert isinstance(host.duck, V010LivingDuck)
    assert isinstance(host.duck, V09LivingDuck)
    status = host.status()
    assert status["subject_id"] == "current-v010"
    assert status["active_plan_count"] == 0


def test_v09_remains_available_as_explicit_preserved_baseline():
    legacy = V09LivingDuck(SubjectState.create(name="Aster", subject_id="preserved-v09"))
    assert type(legacy) is V09LivingDuck
    assert legacy.state.subject_id == "preserved-v09"


def test_plan_outcome_memory_cannot_become_a_ghost_concern():
    duck = V09LivingDuck(SubjectState.create(name="Aster", subject_id="outcome-boundary"))
    duck.state.needs["curiosity"] = 0.84
    duck.state.affect["fear"] = 0.05
    duck.step(
        WorldEvent(
            "observation",
            "world",
            "An unfamiliar mechanism is blinking in a repeating pattern.",
            ("mystery", "novel", "mechanism"),
            0.05,
            0.40,
        ),
        allow_inner_speech=False,
    )
    attempted = duck.heartbeat(allow_inner_speech=False)
    duck.resolve_outcome(
        attempted.action_id,
        success=0.90,
        valence=0.25,
        description="The mechanism was successfully inspected.",
        tags=("mechanism", "success"),
    )

    outcomes = [memory for memory in duck.state.memories if memory.provenance is MemoryProvenance.OUTCOME]
    assert outcomes
    for memory in outcomes:
        assert "opportunity" not in memory.tags
        assert "prospective" not in memory.tags
        assert "plan_step" not in memory.tags
        assert not any(tag.startswith(("pc_", "pl_", "concern_id:", "preferred_action:")) for tag in memory.tags)

    for concern in duck.concerns(status=None):
        assert duck._concern_memory(concern.concern_id).provenance is MemoryProvenance.SELF_REFLECTION
