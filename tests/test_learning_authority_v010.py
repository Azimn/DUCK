from copy import deepcopy

from duck import LivingDuck
from duck.living import LivingDuck as HistoricalDuck, SubjectState, WorldEvent


def test_legacy_adaptive_state_cannot_bias_or_learn_in_current_runtime():
    original = SubjectState.create(name="Aster")
    changed = deepcopy(original)
    for _ in range(30):
        changed.adaptive.observe("door", ("novel",))
        changed.adaptive.learn("explore", ("novel",), -1.0)
    frozen = deepcopy(changed.adaptive.to_dict())
    first, second = LivingDuck(original), LivingDuck(changed)
    event = WorldEvent("observation", "world", "A door.", ("novel",))
    a, b = first.step(event), second.step(event)
    assert a.selected_action == b.selected_action
    assert a.developer_trace["candidate_actions"] == b.developer_trace["candidate_actions"]
    second.resolve_outcome(b.action_id, success=0.0, valence=-0.8, description="It failed.")
    assert second.state.adaptive.to_dict() == frozen
    assert second.cognitive_state.strategy_success[b.selected_action] < 0.0


def test_historical_runtime_retains_adaptive_learning():
    duck = HistoricalDuck()
    before = deepcopy(duck.state.adaptive.to_dict())
    result = duck.step(WorldEvent("observation", "world", "A door.", ("novel",)))
    duck.resolve_outcome(result.action_id, success=0.0, valence=-0.8, description="It failed.")
    assert duck.state.adaptive.to_dict() != before
