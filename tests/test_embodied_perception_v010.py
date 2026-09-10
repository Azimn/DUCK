from copy import deepcopy
from dataclasses import asdict, replace
import json

import pytest

from duck import LivingDuck, PersistentDuckHost
from duck.affordances_v010 import Affordance, AffordanceSource
from duck.body_v010 import BodyState, BodyDynamics, RegulatoryState, energy_deficit, legacy_need_view
from duck.executive import ExecutiveProposal
from duck.language import ApprovedLanguagePacket, DeterministicExpression, SocialExpressionStance
from duck.living import BeliefStance, WorldEvent
from duck.perception_v010 import FactObservation, Modality, SensoryEvidence
from duck.strategy_v010 import CognitiveRegime


def evidence(*, facts=(), confidence=1.0):
    return SensoryEvidence(Modality.VISION, "world", "I can see the door.",
                           reliability=confidence, observed_facts=facts)


def test_evidence_never_claims_world_truth_and_affects_same_cycle(tmp_path):
    host = PersistentDuckHost.open(tmp_path)
    host.set_world_fact("door", "closed")
    expectation = host.duck.register_expectation("I expect the door to stay closed.",
                                                fact_key="door", expected_value="closed")
    class NeverWrite(dict):
        def __setitem__(self, key, value):
            raise AssertionError("subject received authoritative truth")
        def clear(self):
            raise AssertionError("step still uses temporary clear")
    host.duck.state.world_facts = NeverWrite()
    result = host.duck.perceive(evidence(facts=(FactObservation("door", "open", "vision", .93),)))
    assert host.world_fact("door") == "closed"
    belief = host.duck.state.beliefs["door"]
    assert belief.text == "open" and belief.confidence == .93
    assert host.duck.expectations()[0].expectation_id == expectation.expectation_id
    assert host.duck.expectations()[0].status == "violated"
    assert result.developer_trace["expectations"]["resolved"][0]["outcome"] == "violated"
    assert "expectation_violation" in result.developer_trace["cognitive_field"]["event_tags"]
    assert any("door" in memory.text and "perceived_fact" in memory.tags for memory in host.duck.state.memories)


def test_uncertain_and_conflicting_observations_do_not_resolve_predictions():
    for facts in ((FactObservation("door", "open", "vision", .2),),
                  (FactObservation("door", "open", "vision"), FactObservation("door", "closed", "hearing"))):
        duck = LivingDuck()
        duck.register_expectation("I expect the door to close.", fact_key="door", expected_value="closed")
        duck.perceive(evidence(facts=facts))
        assert duck.expectations()[0].status == "open"
        assert duck.state.beliefs["door"].stance == BeliefStance.UNCERTAIN


def test_hidden_event_never_becomes_percept():
    duck = LivingDuck()
    duck.step(WorldEvent("observation", "world", "Hidden password.", ("threat",), -1, 1,
                         (("secret", "password"),), perceived=False))
    assert "secret" not in duck.state.beliefs
    assert all("password" not in memory.text for memory in duck.state.memories)


def test_appraisal_changes_with_history_for_identical_observable_input():
    trusted, harmed = LivingDuck(), LivingDuck()
    trusted.state.relationship("Morgan").trust = .95
    trusted.state.relationship("Morgan").guardedness = .05
    harmed.state.relationship("Morgan").trust = .1
    harmed.state.relationship("Morgan").guardedness = .95
    harmed.state.add_memory("Morgan hit me before.", people=("Morgan",), source="Morgan", valence=-.9)
    stimulus = SensoryEvidence(Modality.AUDITION, "Morgan", "Morgan raises their voice and comes closer.",
                               strength=.8, features=("loud_voice", "approaching_person"))
    a, b = trusted.perceive(stimulus), harmed.perceive(stimulus)
    assert harmed.last_appraisal.threat_relevance > trusted.last_appraisal.threat_relevance + .2
    assert "threat" not in a.developer_trace["cognitive_field"]["event_tags"]
    assert "threat" in b.developer_trace["cognitive_field"]["event_tags"]
    assert trusted.state.affect["fear"] < harmed.state.affect["fear"]


@pytest.mark.parametrize("feature", ["threat", "good", "bad", "conflict", "supportive"])
def test_native_evidence_rejects_authored_appraisal(feature):
    with pytest.raises(ValueError):
        SensoryEvidence(Modality.VISION, "world", "Something happens.", features=(feature,))


def test_rest_changes_body_and_reduces_pressure_without_double_credit():
    body = BodyState(energy_reserve=.2, fatigue_load=.8)
    duck = LivingDuck(body_state=body)
    duck.cognitive_state.strategy_success["rest"] = 1
    before = energy_deficit(body)
    step = duck.heartbeat(allow_inner_speech=False)
    assert step.selected_action == "rest"
    after = energy_deficit(body)
    assert after < before
    duck.resolve_outcome(step.action_id, success=1, valence=.5, description="I rested.")
    assert energy_deficit(body) == after
    assert duck.state.needs["energy"] == pytest.approx(1 - after)
    assert "energy_reserve" not in " ".join(duck.last_experience.prose)


def test_regulatory_view_is_bidirectional_without_independent_store():
    duck = LivingDuck()
    duck.state.needs["affiliation"] = .9
    duck.state.needs["safety"] = .2
    assert duck.regulatory_state.affiliation_need == .9
    assert duck.regulatory_state.safety_deficit == .8
    duck.regulatory.affiliation_need = .3
    assert duck.state.needs["affiliation"] == .3
    assert legacy_need_view(duck.regulatory_state) == dict(duck.state.needs)
    json.dumps(duck.state.to_dict())


def test_body_regulation_and_action_context_survive_restart(tmp_path):
    host = PersistentDuckHost.open(tmp_path)
    host.duck.body.energy_reserve = .15
    host.duck.body.fatigue_load = .9
    host.duck.body.pain_load = .4
    host.duck.regulatory.affiliation_need = .7
    step = host.observe_evidence(evidence())
    assert step.selected_action == "rest"
    before = deepcopy(host.duck.body.to_dict())
    pending = dict(host.duck.cognitive_state.pending_strategy_context)
    reopened = PersistentDuckHost.open(tmp_path)
    assert reopened.duck.body.to_dict() == before
    assert reopened.duck.cognitive_state.pending_strategy_context == pending
    reopened.duck.body.energy_reserve = 1
    reopened.duck.body.fatigue_load = 0
    reopened.resolve_outcome(step.action_id, success=1, valence=.8, description="It worked.")
    assert f"{step.selected_action}|fatigued" in reopened.duck.cognitive_state.strategy_contexts
    assert f"{step.selected_action}|baseline" not in reopened.duck.cognitive_state.strategy_contexts
    assert PersistentDuckHost.open(tmp_path).duck.cognitive_state.pending_strategy_context == {}


def test_legacy_snapshot_migrates_once_and_new_body_has_authority(tmp_path):
    from duck.living import SubjectState
    state = SubjectState.create("Aster")
    state.needs["energy"] = .23
    (tmp_path / "subject.json").write_text(json.dumps(state.to_dict()))
    host = PersistentDuckHost.open(tmp_path)
    assert host.duck.state.needs["energy"] == pytest.approx(.23)
    host.duck.body.energy_reserve = .8
    host.duck.body.fatigue_load = .5
    host.save()
    mirror = state.to_dict()
    mirror["needs"]["energy"] = .01
    (tmp_path / "subject.json").write_text(json.dumps(mirror))
    reopened = PersistentDuckHost.open(tmp_path)
    assert reopened.duck.body.energy_reserve == .8
    assert reopened.duck.body.fatigue_load == .5


@pytest.mark.parametrize("label", ["component:body_v010.json", "component:regulatory_v010.json"])
def test_body_and_regulatory_snapshot_crashes_recover_previous_generation(tmp_path, label):
    host = PersistentDuckHost.open(tmp_path)
    host.save()
    before = host.duck.body.to_dict()
    host.duck.body.energy_reserve = .01
    host.duck.regulatory.affiliation_need = .98
    def crash(current):
        if current == label:
            raise RuntimeError("crash")
    host.snapshot_store._checkpoint = crash
    with pytest.raises(RuntimeError, match="crash"):
        host.save()
    reopened = PersistentDuckHost.open(tmp_path)
    assert reopened.duck.body.to_dict() == before
    assert reopened.duck.regulatory.affiliation_need != .98


def test_executive_cannot_select_absent_affordance():
    class Executive:
        def propose(self, frame):
            return ExecutiveProposal(action="explore")
    duck = LivingDuck(executive=Executive())
    result = duck.perceive(SensoryEvidence(Modality.VISION, "world", "An unfamiliar object.",
                                          features=("unfamiliar_object",)))
    assert {r["name"] for r in result.developer_trace["candidate_actions"]} == {"wait", "rest"}
    assert result.selected_action in {"wait", "rest"}
    assert result.developer_trace["executive_recruitment"]["proposal_rejected"] == "unavailable_action"


def test_available_targets_are_selected_by_subject_cost_and_persist(tmp_path):
    class Executive:
        def propose(self, frame):
            return ExecutiveProposal(action="open")
    host = PersistentDuckHost.open(tmp_path, executive=Executive())
    options = (Affordance("open", AffordanceSource.ENVIRONMENT, "heavy_door", effort=.9),
               Affordance("open", AffordanceSource.ENVIRONMENT, "light_door", effort=.1))
    result = host.observe_evidence(SensoryEvidence(Modality.VISION, "world", "Two unfamiliar doors.",
                                                  features=("unfamiliar_object",)), affordances=options)
    assert result.selected_action == "open"
    assert host.duck.state.pending_action.target == "light_door"
    assert PersistentDuckHost.open(tmp_path).duck.state.pending_action.target == "light_door"
    host.duck.body.energy_reserve, host.duck.body.fatigue_load = .1, .9
    tired_penalty = host.duck._affordance_cost(options[0]) - host.duck._affordance_cost(options[1])
    host.duck.body.energy_reserve, host.duck.body.fatigue_load = .9, .1
    rested_penalty = host.duck._affordance_cost(options[0]) - host.duck._affordance_cost(options[1])
    assert tired_penalty < rested_penalty


def test_contextual_learning_backs_off_and_remains_bounded():
    duck = LivingDuck()
    engine = duck.control
    for _ in range(20):
        engine.record_outcome("explore", 1, .8, (), 0, regime=CognitiveRegime.BASELINE)
        engine.record_outcome("explore", 0, -.8, (), 0, regime=CognitiveRegime.FATIGUED)
    assert engine.strategy_value("explore", CognitiveRegime.BASELINE) > .5
    assert engine.strategy_value("explore", CognitiveRegime.FATIGUED) < -.5
    assert engine.strategy_value("explore", CognitiveRegime.SOCIALLY_GUARDED) == engine.state.strategy_success["explore"]
    for index in range(400):
        engine.record_outcome(f"action{index}", 1, 1, (), 0, regime=CognitiveRegime.BASELINE)
    assert len(engine.state.strategy_contexts) <= 320
    assert len(engine.state.strategy_success) <= 64


def test_expression_stance_is_independent_of_private_wording():
    packet = ApprovedLanguagePacket(private_thought=None, user_text="Hello", action_intent="I have decided to respond.",
                                    first_person_state=("I feel safe with this person.",))
    renderer = DeterministicExpression()
    a = renderer.render_with_stance(packet, SocialExpressionStance.WARM)
    b = renderer.render_with_stance(replace(packet, first_person_state=("I trust them.",)), SocialExpressionStance.WARM)
    assert a == b
    assert a != renderer.render_with_stance(packet, SocialExpressionStance.CAUTIOUS)
    assert "stance" not in asdict(packet)
