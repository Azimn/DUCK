from __future__ import annotations

import json

from duck import LivingDuck, PersistentDuckHost
from duck.causal_v010 import PLAN_START
from duck.counterfactual_v010 import COUNTERFACTUAL_PROVENANCE
from duck.living import SubjectState


def _state(subject_id: str) -> SubjectState:
    state = SubjectState.create("Aster", subject_id)
    state.needs["energy"] = 0.92
    state.needs["safety"] = 0.88
    state.needs["curiosity"] = 0.84
    state.needs["competence"] = 0.74
    state.needs["coherence"] = 0.82
    state.needs["autonomy"] = 0.72
    state.affect["fear"] = 0.08
    state.affect["unease"] = 0.04
    return state


def test_route_selection_captures_one_selected_route_and_unenacted_counterfactuals():
    duck = LivingDuck(_state("counterfactual-selection"))
    assert duck.last_route_comparison is None
    assert duck.counterfactual_routes() == ()

    root = duck.form_goal("investigate", "I want to understand the unfamiliar panel.")
    plan = duck._plan_from_memory(root)
    snapshot = duck.last_route_comparison
    assert snapshot is not None
    assert snapshot.kind == "investigate"
    assert snapshot.selected_route == plan.current_route
    assert len(snapshot.estimates) == len(duck._ROUTES["investigate"])
    assert sum(1 for row in snapshot.estimates if row.selected) == 1
    assert len(snapshot.counterfactuals) == len(snapshot.estimates) - 1
    assert all(row.provenance == COUNTERFACTUAL_PROVENANCE for row in snapshot.estimates)
    assert all("motivated_structure" in row.evidence_basis for row in snapshot.estimates)


def test_reading_counterfactuals_does_not_create_memory_prediction_or_learning_state():
    duck = LivingDuck(_state("counterfactual-purity"))
    duck.form_goal("investigate", "I want to understand the unfamiliar panel.")
    before_memories = len(duck.state.memories)
    before_expectations = duck.expectation_state.to_dict()
    before_causal = duck.causal_state.to_dict()
    before_cognition = duck.cognitive_state.to_dict()

    rows = duck.counterfactual_routes()
    assert rows
    assert all(not row.selected for row in rows)

    assert len(duck.state.memories) == before_memories
    assert duck.expectation_state.to_dict() == before_expectations
    assert duck.causal_state.to_dict() == before_causal
    assert duck.cognitive_state.to_dict() == before_cognition
    assert not any(
        COUNTERFACTUAL_PROVENANCE in memory.tags or COUNTERFACTUAL_PROVENANCE in memory.text
        for memory in duck.state.memories
    )


def test_counterfactual_evidence_basis_can_report_matched_contrast_without_exposing_values():
    duck = LivingDuck(_state("counterfactual-evidence-basis"))
    for tick in range(1, 5):
        duck.causal_state.observe_transition(
            "ask",
            "explore",
            outcome="fulfilled",
            tick=tick,
            intervention=True,
        )
    for tick in range(5, 9):
        duck.causal_state.observe_transition(
            PLAN_START,
            "explore",
            outcome="violated",
            tick=tick,
        )

    duck.form_goal("investigate", "I want to understand another unfamiliar panel.")
    snapshot = duck.last_route_comparison
    assert snapshot is not None
    cautious = next(row for row in snapshot.estimates if row.route == "cautious_inquiry")
    assert "sequence_calibration" in cautious.evidence_basis
    assert "intervention_sequence" in cautious.evidence_basis
    assert "matched_intervention_contrast" in cautious.evidence_basis
    assert all("0." not in basis for basis in cautious.evidence_basis)


def test_counterfactual_snapshot_is_not_persisted_as_subject_history(tmp_path):
    root = tmp_path / "counterfactual-host"
    host = PersistentDuckHost.open(root, name="Aster", subject_id="counterfactual-host")
    host.duck.state.needs.update(_state("template").needs)
    host.duck.state.affect.update(_state("template").affect)
    host.duck.form_goal("investigate", "I want to understand the unfamiliar panel.")
    assert host.duck.last_route_comparison is not None
    host.save()

    payload_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in root.glob("*.json")
    )
    assert COUNTERFACTUAL_PROVENANCE not in payload_text
    assert "preference_score" not in payload_text
    assert "last_route_comparison" not in payload_text

    reopened = PersistentDuckHost.open(root)
    assert reopened.duck.last_route_comparison is None
    assert reopened.duck.counterfactual_routes() == ()


def test_counterfactual_snapshot_does_not_enter_private_interior_or_public_status(tmp_path):
    root = tmp_path / "counterfactual-firewall"
    host = PersistentDuckHost.open(root, name="Aster", subject_id="counterfactual-firewall")
    host.duck.form_goal("investigate", "I want to understand the unfamiliar panel.")
    host.save()

    status = json.dumps(host.status(), sort_keys=True)
    assert "counterfactual" not in status.lower()
    private_text = (root / "private_interior.json").read_text(encoding="utf-8")
    assert COUNTERFACTUAL_PROVENANCE not in private_text
    assert "preference_score" not in private_text
