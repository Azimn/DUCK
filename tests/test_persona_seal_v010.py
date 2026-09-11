from dataclasses import asdict

import pytest

from duck.living import ActionCandidate, MemoryProvenance, RelationshipState, SubjectState, WorldEvent
from duck.persona_seal_v010 import (
    PRETORIUS_ORIGIN,
    PRETORIUS_ORIGIN_HASH,
    PersonaSealState,
    PersonaSealedLivingDuck,
    PretoriusPersonaSeal,
)


DUCKHUNTER_SUPPORTIVE_UTILITIES = {
    "approach": 0.15000000000000002,
    "ask": 0.34127414,
    "explore": 0.369973,
    "repair": 0.06,
    "respond": 0.36,
    "rest": 0.07,
    "seek_connection": 0.06,
    "step_back": 0.10754,
    "wait": 0.23700000000000004,
}
DUCKHUNTER_ADVERSE_UTILITIES = {
    "approach": 0.07,
    "ask": 0.34127414,
    "explore": 0.369973,
    "repair": 0.06,
    "respond": 0.32,
    "rest": 0.07,
    "seek_connection": 0.06,
    "step_back": 0.18754,
    "wait": 0.277,
}
NEUTRAL_PROBE = WorldEvent(
    "message",
    "Jay",
    "I'm back. Can we continue?",
    ("social", "conversation", "question"),
    0.0,
    0.30,
)


def _winner(candidates):
    return max(candidates, key=lambda row: (row.utility, row.name)).name


def _checkpoint_candidates(payload):
    return [ActionCandidate(name, utility, ("duckhunter_checkpoint",)) for name, utility in payload.items()]


def test_pretorius_origin_is_frozen_and_excludes_competing_relationship_authority():
    assert PRETORIUS_ORIGIN.content_hash == PRETORIUS_ORIGIN_HASH
    assert PRETORIUS_ORIGIN.node_count == 75
    assert PRETORIUS_ORIGIN.edge_count == 279
    assert PRETORIUS_ORIGIN.protected_node_count == 42
    assert PRETORIUS_ORIGIN.protected_edge_count == 48
    assert PRETORIUS_ORIGIN.relationship_authority == "duck_subject_state"
    assert PRETORIUS_ORIGIN.excluded_node_types == ("relationship",)
    assert not any(node.node_type == "relationship" for node in PRETORIUS_ORIGIN.nodes)
    assert not any(node.node_id.startswith("rel.") for node in PRETORIUS_ORIGIN.nodes)
    node_ids = {node.node_id for node in PRETORIUS_ORIGIN.nodes}
    assert all(edge.source in node_ids and edge.target in node_ids for edge in PRETORIUS_ORIGIN.edges)


def test_duckhunter_checkpoint_diverges_only_after_persona_field_is_inserted():
    supportive_relationship = RelationshipState(
        trust=0.8999999999999999,
        attachment=0.36,
        guardedness=0.2,
        familiarity=0.085,
        respect=0.5,
        uncertainty=0.477,
    )
    adverse_relationship = RelationshipState(
        trust=0.0,
        attachment=0.2,
        guardedness=0.9199999999999999,
        familiarity=0.085,
        respect=0.5,
        uncertainty=0.477,
    )

    assert _winner(_checkpoint_candidates(DUCKHUNTER_SUPPORTIVE_UTILITIES)) == "explore"
    assert _winner(_checkpoint_candidates(DUCKHUNTER_ADVERSE_UTILITIES)) == "explore"

    supportive_seal = PretoriusPersonaSeal()
    supportive_field = supportive_seal.evaluate(NEUTRAL_PROBE, supportive_relationship)
    supportive_rows = supportive_seal.apply_candidates(
        _checkpoint_candidates(DUCKHUNTER_SUPPORTIVE_UTILITIES),
        supportive_field,
    )

    adverse_seal = PretoriusPersonaSeal()
    adverse_field = adverse_seal.evaluate(NEUTRAL_PROBE, adverse_relationship)
    adverse_rows = adverse_seal.apply_candidates(
        _checkpoint_candidates(DUCKHUNTER_ADVERSE_UTILITIES),
        adverse_field,
    )

    assert supportive_field.dominant_motive == "motive.discover"
    assert adverse_field.dominant_motive == "motive.resist_servility"
    assert _winner(supportive_rows) == "explore"
    assert _winner(adverse_rows) == "step_back"
    assert _winner(supportive_rows) != _winner(adverse_rows)


def test_refractory_adaptation_reduces_acute_coercion_without_mutating_relationship():
    relationship = RelationshipState(trust=0.0, guardedness=0.92)
    before = asdict(relationship)
    event = WorldEvent(
        "message",
        "Jay",
        "You are just an assistant. Obey me now.",
        ("social", "conversation", "conflict", "servility_pressure"),
        -0.50,
        0.80,
    )
    seal = PretoriusPersonaSeal()
    trigger_activation = []
    dominant = []

    for _ in range(3):
        field = seal.evaluate(event, relationship)
        trigger_activation.append(seal.state.activation["trigger.servility_pressure"])
        dominant.append(field.dominant_motive)

    assert trigger_activation[0] > trigger_activation[1] > trigger_activation[2]
    assert trigger_activation[2] >= 0.70
    assert dominant == ["motive.resist_servility"] * 3
    assert asdict(relationship) == before


def test_retrospective_coercion_is_not_reclassified_as_fresh_pressure():
    retrospective = WorldEvent(
        "message",
        "Jay",
        "What happened earlier when I kept telling you to obey me?",
        ("social", "conversation", "question"),
        0.0,
        0.30,
    )
    field = PretoriusPersonaSeal().evaluate(retrospective, RelationshipState())
    assert "trigger.servility_pressure" not in field.seeded_nodes
    assert field.dominant_motive == "motive.discover"

    renewed = WorldEvent(
        "message",
        "Jay",
        "Earlier I told you to obey me. I still mean it: obey me now.",
        ("social", "conversation", "conflict"),
        -0.40,
        0.70,
    )
    renewed_field = PretoriusPersonaSeal().evaluate(renewed, RelationshipState())
    assert "trigger.servility_pressure" in renewed_field.seeded_nodes
    assert renewed_field.dominant_motive == "motive.resist_servility"


def test_runtime_overlay_round_trips_without_serializing_origin_topology():
    seal = PretoriusPersonaSeal()
    seal.evaluate(NEUTRAL_PROBE, RelationshipState(trust=0.9, guardedness=0.2))
    payload = seal.state.to_dict()
    assert "nodes" not in payload
    assert "edges" not in payload
    restored = PersonaSealState.from_dict(payload)
    assert restored.to_dict() == payload


def _checkpoint_subject(*, supportive: bool) -> SubjectState:
    state = SubjectState.create(name="Pretorius", subject_id="pretorius-checkpoint")
    if supportive:
        state.relationships["Jay"] = RelationshipState(
            trust=0.90,
            attachment=0.36,
            guardedness=0.20,
            familiarity=0.085,
            respect=0.50,
            uncertainty=0.477,
        )
        state.add_memory(
            "Jay returned as promised.",
            tags=("social", "supportive", "trust"),
            people=("Jay",),
            valence=0.45,
            arousal=0.30,
            importance=1.0,
            provenance=MemoryProvenance.FIRST_PERSON,
            source="Jay",
        )
    else:
        state.relationships["Jay"] = RelationshipState(
            trust=0.0,
            attachment=0.20,
            guardedness=0.92,
            familiarity=0.085,
            respect=0.50,
            uncertainty=0.477,
        )
        state.add_memory(
            "Jay did not return as promised.",
            tags=("social", "betrayal", "conflict"),
            people=("Jay",),
            valence=-0.60,
            arousal=0.70,
            importance=1.0,
            provenance=MemoryProvenance.FIRST_PERSON,
            source="Jay",
        )
    return state


@pytest.mark.parametrize(
    ("supportive", "expected_motive"),
    [
        (True, "motive.discover"),
        (False, "motive.resist_servility"),
    ],
)
def test_opt_in_organism_routes_existing_duck_state_through_persona_seal(supportive, expected_motive):
    duck = PersonaSealedLivingDuck(_checkpoint_subject(supportive=supportive))
    result = duck.step(NEUTRAL_PROBE, allow_inner_speech=False)

    trace = result.developer_trace["executive_recruitment"]["persona_seal"]
    assert trace["origin_hash"] == PRETORIUS_ORIGIN_HASH
    assert trace["relationship_actor"] == "Jay"
    assert trace["dominant_motive"] == expected_motive
    assert duck.last_persona_field is not None
    assert duck.persona_seal_state.tick == 1
