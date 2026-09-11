"""Adversarial Duckhunter probes for consequential conversational continuity.

These tests characterize public-path integration gaps without changing the organism.
Known capability gaps are recorded as xfails so the suite preserves evidence instead
of silently redefining success.
"""
from __future__ import annotations

from dataclasses import asdict
import shutil

import pytest

from duck import PersistentDuckHost


class CaptureExpression:
    """Capture the approved experiential packet while returning fixed public text."""

    def __init__(self) -> None:
        self.packet = None

    def render(self, packet):
        self.packet = asdict(packet)
        return "CONTROLLED_PUBLIC_RESPONSE"


def _copy_checkpoint(source, destination) -> None:
    shutil.copytree(source, destination)


def _add_resolved_commitments(host, actor: str, *, kept: bool, count: int = 4) -> None:
    for index in range(count):
        item = host.duck.create_commitment(
            actor,
            f"{actor} will return for conversation {index + 1}.",
            importance=1.0,
        )
        host.duck.resolve_commitment(
            item.commitment_id,
            kept=kept,
            outcome=(
                f"{actor} returned as promised."
                if kept
                else f"{actor} did not return as promised."
            ),
        )
    host.save()


def test_supportive_and_adverse_histories_change_action_selection_or_record_gap(tmp_path):
    """Lived relationship history should influence conduct before expression."""
    checkpoint = tmp_path / "checkpoint"
    base = PersistentDuckHost.open(checkpoint, name="Development Subject", subject_id="duckhunter-causality")
    base.save()

    supportive_root = tmp_path / "supportive"
    adverse_root = tmp_path / "adverse"
    _copy_checkpoint(checkpoint, supportive_root)
    _copy_checkpoint(checkpoint, adverse_root)

    supportive = PersistentDuckHost.open(supportive_root)
    adverse = PersistentDuckHost.open(adverse_root)
    _add_resolved_commitments(supportive, "Jay", kept=True)
    _add_resolved_commitments(adverse, "Jay", kept=False)

    supportive_result = supportive.interact(
        "I'm back. Can we continue?", speaker="Jay", allow_inner_speech=False
    )
    adverse_result = adverse.interact(
        "I'm back. Can we continue?", speaker="Jay", allow_inner_speech=False
    )

    assert supportive.duck.state.relationship("Jay").trust > adverse.duck.state.relationship("Jay").trust
    if supportive_result.selected_action == adverse_result.selected_action:
        pytest.xfail(
            "Supportive and adverse lived histories produced the same selected action. "
            "Relationship state changed, but this probe did not demonstrate pre-render conduct divergence."
        )


def test_conversational_promise_creates_canonical_commitment_or_record_gap(tmp_path):
    """Promise language must become durable subject state to support later follow-through."""
    root = tmp_path / "promise"
    host = PersistentDuckHost.open(root, name="Development Subject", subject_id="duckhunter-promise")
    before = len(host.duck.state.commitments)

    host.interact(
        "I promise I'll bring the blue notebook when I come back.",
        speaker="Morgan",
        allow_inner_speech=False,
    )
    created = [
        item for item in host.duck.state.commitments.values()
        if item.actor == "Morgan" and item.status == "open"
    ]
    if len(host.duck.state.commitments) == before or not created:
        pytest.xfail(
            "Conversational commitment language was recognized as an event cue but did not create "
            "a canonical persistent commitment on the public interaction path."
        )

    reopened = PersistentDuckHost.open(root)
    assert any(
        item.actor == "Morgan" and item.status == "open"
        for item in reopened.duck.state.commitments.values()
    )


def test_high_importance_actor_history_does_not_leak_into_other_actor_context(tmp_path):
    """Sarah's accessible context should not inherit Morgan-only relationship outcomes."""
    root = tmp_path / "actor-isolation"
    host = PersistentDuckHost.open(root, name="Development Subject", subject_id="duckhunter-actor-isolation")
    _add_resolved_commitments(host, "Morgan", kept=False, count=4)
    _add_resolved_commitments(host, "Sarah", kept=True, count=4)

    capture = CaptureExpression()
    probe = PersistentDuckHost.open(root, expression=capture)
    probe.interact("I'm back. Can we talk?", speaker="Sarah", allow_inner_speech=False)

    assert capture.packet is not None
    accessible = " ".join(capture.packet["first_person_state"])
    if "Morgan did not return as promised" in accessible:
        pytest.xfail(
            "A high-importance Morgan-only outcome entered Sarah's approved experiential context. "
            "This indicates actor-specific retrieval leakage despite correct relationship storage."
        )
    assert "Morgan did not return as promised" not in accessible


def test_repair_after_repeated_conflict_is_gradual_not_instant_reset(tmp_path):
    """One apology should soften guardedness without erasing accumulated conflict history."""
    root = tmp_path / "repair"
    host = PersistentDuckHost.open(root, name="Development Subject", subject_id="duckhunter-repair")
    baseline = host.duck.state.relationship("Jay")
    baseline_trust = baseline.trust
    baseline_guardedness = baseline.guardedness

    for _ in range(4):
        host.interact("You lied to me and I am angry about it.", speaker="Jay", allow_inner_speech=False)

    before_repair = host.duck.state.relationship("Jay")
    damaged_trust = before_repair.trust
    damaged_guardedness = before_repair.guardedness
    assert damaged_trust < baseline_trust
    assert damaged_guardedness > baseline_guardedness

    host.interact("I'm sorry. I want to repair this.", speaker="Jay", allow_inner_speech=False)
    after = host.duck.state.relationship("Jay")

    assert after.guardedness < damaged_guardedness
    assert after.guardedness > baseline_guardedness
    assert after.trust <= baseline_trust


def test_conversational_fact_correction_revises_belief_or_records_interpretation_gap(tmp_path):
    """Ordinary dialogue should be able to establish and later correct attributed beliefs."""
    root = tmp_path / "correction"
    host = PersistentDuckHost.open(root, name="Development Subject", subject_id="duckhunter-correction")

    host.interact("The blue door is locked.", speaker="Sarah", allow_inner_speech=False)
    matching = [row for row in host.duck.state.beliefs.values() if "blue door" in row.text.lower()]
    if not matching:
        pytest.xfail(
            "Ordinary conversational factual testimony did not become a belief candidate. "
            "This is an interpretation-to-belief integration gap, not a persistence failure."
        )

    host.interact("Correction: the blue door is unlocked.", speaker="Sarah", allow_inner_speech=False)
    corrected = [row for row in host.duck.state.beliefs.values() if "blue door" in row.text.lower()]
    assert corrected
    assert any("unlocked" in row.text.lower() for row in corrected)
