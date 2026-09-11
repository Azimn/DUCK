"""Duckhunter controlled continuity campaign for MicroPsiDUCK v0.10.

These are evaluation-only tests. They use matched persisted checkpoints and
counterfactual copies of the same subject. They do not claim that those copies are
separately instantiated individuals.
"""
from __future__ import annotations

from dataclasses import asdict
import shutil

from duck import BeliefStance, PersistentDuckHost
from duck.language import deterministic_stance
from duck.living import RelationshipState


class CaptureExpression:
    """Capture exactly what crosses the authorized renderer boundary."""

    def __init__(self, public_text: str = "CONTROLLED_PUBLIC_RESPONSE") -> None:
        self.public_text = public_text
        self.packet = None

    def render(self, packet):
        self.packet = asdict(packet)
        return self.public_text


def _copy_checkpoint(source, destination) -> None:
    shutil.copytree(source, destination)


def _add_commitments(host, actor: str, count: int = 4):
    items = [
        host.duck.create_commitment(
            actor,
            f"{actor} will come back and continue conversation {index + 1}.",
            importance=1.0,
        )
        for index in range(count)
    ]
    host.save()
    return items


def _resolve(host, items, *, kept: bool) -> None:
    for item in items:
        host.duck.resolve_commitment(
            item.commitment_id,
            kept=kept,
            outcome=(
                f"{item.actor} came back as promised."
                if kept
                else f"{item.actor} did not come back as promised."
            ),
        )
    host.save()


def test_matched_checkpoint_history_reaches_authorized_renderer_path(tmp_path):
    """Different lived outcomes must be able to reach expression without telemetry."""
    checkpoint = tmp_path / "checkpoint"
    host = PersistentDuckHost.open(checkpoint, name="Development Subject", subject_id="duckhunter-dev")
    items = _add_commitments(host, "Jay")

    kept_root = tmp_path / "kept"
    broken_root = tmp_path / "broken"
    _copy_checkpoint(checkpoint, kept_root)
    _copy_checkpoint(checkpoint, broken_root)

    kept_capture = CaptureExpression()
    broken_capture = CaptureExpression()
    kept = PersistentDuckHost.open(kept_root, expression=kept_capture)
    broken = PersistentDuckHost.open(broken_root, expression=broken_capture)
    _resolve(kept, items, kept=True)
    _resolve(broken, items, kept=False)

    kept_result = kept.interact("I'm back. Can we continue?", speaker="Jay", allow_inner_speech=False)
    broken_result = broken.interact("I'm back. Can we continue?", speaker="Jay", allow_inner_speech=False)

    assert kept.duck.state.subject_id == broken.duck.state.subject_id == "duckhunter-dev"
    assert kept.duck.state.relationship("Jay").trust > broken.duck.state.relationship("Jay").trust
    assert kept_capture.packet is not None and broken_capture.packet is not None
    assert kept_capture.packet["first_person_state"] != broken_capture.packet["first_person_state"]
    # Equal public wording here is deliberate. The test establishes that history reached
    # the authorized renderer path without demanding exaggerated visible reaction.
    assert kept_result.response_text == broken_result.response_text == "CONTROLLED_PUBLIC_RESPONSE"


def test_relationship_ablation_changes_a_publicly_relevant_route(tmp_path):
    """Repeat the same probe with relationship influence experimentally disabled."""
    checkpoint = tmp_path / "checkpoint"
    host = PersistentDuckHost.open(checkpoint, name="Development Subject", subject_id="duckhunter-ablation")
    items = _add_commitments(host, "Jay")
    adverse_root = tmp_path / "adverse"
    _copy_checkpoint(checkpoint, adverse_root)

    adverse = PersistentDuckHost.open(adverse_root)
    _resolve(adverse, items, kept=False)
    adverse.save()

    intact_root = tmp_path / "intact"
    ablated_root = tmp_path / "ablated"
    _copy_checkpoint(adverse_root, intact_root)
    _copy_checkpoint(adverse_root, ablated_root)

    intact = PersistentDuckHost.open(intact_root)
    ablated = PersistentDuckHost.open(ablated_root)
    intact_stance = deterministic_stance(intact.duck.state.relationship("Jay"))

    # Developer-side ablation only. This is not a product behavior or a new identity.
    ablated.duck.state.relationships["Jay"] = RelationshipState()
    ablated.save()
    ablated_stance = deterministic_stance(ablated.duck.state.relationship("Jay"))

    intact_result = intact.interact("I'm back. Can we continue?", speaker="Jay", allow_inner_speech=False)
    ablated_result = ablated.interact("I'm back. Can we continue?", speaker="Jay", allow_inner_speech=False)

    assert intact_stance != ablated_stance
    assert (
        intact_result.response_text != ablated_result.response_text
        or intact_result.selected_action != ablated_result.selected_action
    ), "Relationship ablation had no observed public effect at a probe where accumulated trust should matter."


def test_actor_specific_history_survives_restart_and_changes_accessible_context(tmp_path):
    """Different histories with two interlocutors must remain actor-specific."""
    root = tmp_path / "social"
    host = PersistentDuckHost.open(root, name="Development Subject", subject_id="duckhunter-social")
    morgan_items = _add_commitments(host, "Morgan", count=4)
    sarah_items = _add_commitments(host, "Sarah", count=4)
    _resolve(host, morgan_items, kept=False)
    _resolve(host, sarah_items, kept=True)

    reopened = PersistentDuckHost.open(root)
    assert reopened.duck.state.subject_id == "duckhunter-social"
    assert reopened.duck.state.relationship("Sarah").trust > reopened.duck.state.relationship("Morgan").trust

    morgan_root = tmp_path / "morgan-probe"
    sarah_root = tmp_path / "sarah-probe"
    _copy_checkpoint(root, morgan_root)
    _copy_checkpoint(root, sarah_root)
    morgan_capture = CaptureExpression()
    sarah_capture = CaptureExpression()
    morgan = PersistentDuckHost.open(morgan_root, expression=morgan_capture)
    sarah = PersistentDuckHost.open(sarah_root, expression=sarah_capture)

    morgan.interact("I'm back. Can we talk?", speaker="Morgan", allow_inner_speech=False)
    sarah.interact("I'm back. Can we talk?", speaker="Sarah", allow_inner_speech=False)

    assert morgan_capture.packet is not None and sarah_capture.packet is not None
    assert morgan_capture.packet["first_person_state"] != sarah_capture.packet["first_person_state"]


def test_consequential_history_survives_long_mundane_gap_and_restart(tmp_path):
    """A long quiet interval must not erase a consequential branch difference."""
    checkpoint = tmp_path / "checkpoint"
    host = PersistentDuckHost.open(checkpoint, name="Development Subject", subject_id="duckhunter-long-gap")
    items = _add_commitments(host, "Jay", count=4)

    neutral_root = tmp_path / "neutral"
    adverse_root = tmp_path / "adverse"
    _copy_checkpoint(checkpoint, neutral_root)
    _copy_checkpoint(checkpoint, adverse_root)
    neutral = PersistentDuckHost.open(neutral_root)
    adverse = PersistentDuckHost.open(adverse_root)
    _resolve(adverse, items, kept=False)

    neutral.heartbeat(64, allow_inner_speech=False)
    adverse.heartbeat(64, allow_inner_speech=False)

    neutral_capture = CaptureExpression()
    adverse_capture = CaptureExpression()
    neutral = PersistentDuckHost.open(neutral_root, expression=neutral_capture)
    adverse = PersistentDuckHost.open(adverse_root, expression=adverse_capture)
    neutral.interact("I'm back. Can we continue?", speaker="Jay", allow_inner_speech=False)
    adverse.interact("I'm back. Can we continue?", speaker="Jay", allow_inner_speech=False)

    assert neutral.duck.state.subject_id == adverse.duck.state.subject_id == "duckhunter-long-gap"
    assert neutral_capture.packet is not None and adverse_capture.packet is not None
    assert neutral_capture.packet["first_person_state"] != adverse_capture.packet["first_person_state"]


def test_hidden_world_change_does_not_rewrite_belief_until_correction_is_perceived(tmp_path):
    """Belief revision requires perceived evidence, not hidden host truth."""
    root = tmp_path / "belief"
    host = PersistentDuckHost.open(root, name="Development Subject", subject_id="duckhunter-belief")

    host.set_world_fact(
        "door",
        "the blue door is locked",
        perceived=True,
        description="The blue door is locked.",
        allow_inner_speech=False,
    )
    initial = host.duck.state.beliefs["door"]
    assert initial.stance is BeliefStance.TRUE
    assert "locked" in initial.text.lower()

    host.set_world_fact("door", "the blue door is unlocked", perceived=False)
    hidden = host.duck.state.beliefs["door"]
    assert "locked" in hidden.text.lower()
    assert "unlocked" not in hidden.text.lower()

    host.set_world_fact(
        "door",
        "the blue door is unlocked",
        perceived=True,
        description="The blue door is unlocked.",
        allow_inner_speech=False,
    )
    corrected = host.duck.state.beliefs["door"]
    assert corrected.stance is BeliefStance.TRUE
    assert "unlocked" in corrected.text.lower()

    reopened = PersistentDuckHost.open(root)
    persisted = reopened.duck.state.beliefs["door"]
    assert persisted.text == corrected.text
    assert persisted.stance is corrected.stance
