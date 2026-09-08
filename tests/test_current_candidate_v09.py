from duck import LivingDuck as PublicLivingDuck, PersistentDuckHost
from duck.host_current import PersistentDuckHostCurrent
from duck.living import MemoryProvenance, SubjectState, WorldEvent
from duck.living_v09 import LivingDuck as V09LivingDuck
from duck.living_v010 import LivingDuck as MotivatedCoreV010
from duck.organism_v010 import LivingDuck as OrganismV010


def test_public_package_uses_composed_micropsiduck_v010_candidate(tmp_path):
    assert PublicLivingDuck is OrganismV010
    assert PersistentDuckHost is PersistentDuckHostCurrent
    assert issubclass(OrganismV010, MotivatedCoreV010)
    assert issubclass(OrganismV010, V09LivingDuck)

    host = PersistentDuckHost.open(tmp_path / "current", name="Aster", subject_id="current-v010")
    assert type(host) is PersistentDuckHostCurrent
    assert type(host.duck) is OrganismV010
    assert isinstance(host.duck, MotivatedCoreV010)
    assert isinstance(host.duck, V09LivingDuck)
    status = host.status()
    assert status["subject_id"] == "current-v010"
    assert status["active_plan_count"] == 0
    assert status["endogenous_schema"] == "micropsi-duck.endogenous.v1"


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
