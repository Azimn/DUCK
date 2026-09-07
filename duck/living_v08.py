"""Motivated prospective agency for the DUCK v0.8 candidate.

v0.7 can regulate itself during quiet time, but most meaningful goals still arrive
from the current external event. v0.8 adds a larger prospective-agency field built
on persistent, provenance-bearing self-reflective memory. Multiple unfinished
concerns can coexist, compete, defer, survive interruption/restart, become actionable
when context changes, and later be satisfied or abandoned.

This remains a prototype layer. Concern metadata is encoded in private persistence
tags on SELF_REFLECTION memory records so the v0.7 SubjectState schema does not need
a second canonical subject store. The simulated subject never sees those tags or
numeric scores; it receives only the projected first-person moment.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .living import (
    ActionCandidate,
    CommitmentRecord,
    MemoryProvenance,
    MemoryRecord,
    RelationshipState,
    WorldEvent,
    _clamp,
)
from .living_v07 import LivingDuck as LifeSimLivingDuck


_META_PREFIX = "pc_"


def _replace_tag(tags: tuple[str, ...], prefix: str, value: str) -> tuple[str, ...]:
    kept = [tag for tag in tags if not tag.startswith(prefix)]
    kept.append(f"{prefix}{value}")
    return tuple(dict.fromkeys(kept))


def _tag_value(tags: Iterable[str], prefix: str, default: str = "") -> str:
    for tag in tags:
        if tag.startswith(prefix):
            return tag[len(prefix) :]
    return default


def _tag_int(tags: Iterable[str], prefix: str, default: int = 0) -> int:
    try:
        return int(_tag_value(tags, prefix, str(default)))
    except ValueError:
        return default


def _decode_percent(tags: Iterable[str], prefix: str, default: float) -> float:
    return _clamp(_tag_int(tags, prefix, round(default * 100)) / 100.0)


@dataclass(frozen=True)
class ProspectiveConcern:
    concern_id: str
    text: str
    priority: float
    urgency: float
    preferred_action: str
    due_tick: int | None
    not_before_tick: int | None
    min_energy: float
    required_tags: tuple[str, ...]
    blocked_tags: tuple[str, ...]
    status: str
    attempts: int
    deferrals: int
    cooldown_until: int
    commitment_id: str | None


class LivingDuck(LifeSimLivingDuck):
    """v0.8 candidate with bounded, motivated prospective agency."""

    def register_concern(
        self,
        text: str,
        *,
        tags: Iterable[str] = (),
        priority: float = 0.70,
        urgency: float = 0.45,
        preferred_action: str = "explore",
        due_in: int | None = None,
        not_before_in: int | None = None,
        min_energy: float = 0.25,
        required_tags: Iterable[str] = (),
        blocked_tags: Iterable[str] = ("threat",),
        source: str = "self",
        commitment_id: str | None = None,
    ) -> MemoryRecord:
        """Register an unfinished prospective concern without executing it.

        The concern is persistent subject state, not a scheduled command. Numeric
        priority/urgency values remain implementation metadata and are never passed
        through the subject-access firewall.
        """
        due_tick = self.state.tick + int(due_in) if due_in is not None else None
        not_before_tick = self.state.tick + int(not_before_in) if not_before_in is not None else None
        normalized_tags = [
            "opportunity",
            "prospective",
            f"{_META_PREFIX}status:open",
            f"{_META_PREFIX}priority:{round(_clamp(priority) * 100)}",
            f"{_META_PREFIX}urgency:{round(_clamp(urgency) * 100)}",
            f"{_META_PREFIX}action:{str(preferred_action).lower()}",
            f"{_META_PREFIX}min_energy:{round(_clamp(min_energy) * 100)}",
            f"{_META_PREFIX}attempts:0",
            f"{_META_PREFIX}deferrals:0",
            f"{_META_PREFIX}cooldown:0",
        ]
        if due_tick is not None:
            normalized_tags.append(f"{_META_PREFIX}due:{due_tick}")
        if not_before_tick is not None:
            normalized_tags.append(f"{_META_PREFIX}not_before:{not_before_tick}")
        if commitment_id:
            normalized_tags.append(f"{_META_PREFIX}commitment:{commitment_id}")
        normalized_tags.extend(f"{_META_PREFIX}required:{str(tag).lower()}" for tag in required_tags)
        normalized_tags.extend(f"{_META_PREFIX}blocked:{str(tag).lower()}" for tag in blocked_tags)
        normalized_tags.extend(str(tag).lower() for tag in tags)
        return self.state.add_memory(
            text,
            tags=tuple(dict.fromkeys(normalized_tags)),
            valence=0.15,
            arousal=_clamp(urgency),
            importance=_clamp(priority),
            provenance=MemoryProvenance.SELF_REFLECTION,
            source=source,
            confidence=1.0,
        )

    def register_opportunity(
        self,
        text: str,
        *,
        tags: Iterable[str] = (),
        importance: float = 0.7,
        source: str = "self",
    ) -> MemoryRecord:
        """Backward-compatible convenience wrapper for a curiosity concern."""
        return self.register_concern(
            text,
            tags=tags,
            priority=importance,
            urgency=0.45,
            preferred_action="explore",
            source=source,
        )

    def register_commitment_followup(
        self,
        commitment: CommitmentRecord | str,
        *,
        text: str | None = None,
        preferred_action: str = "ask",
        priority: float | None = None,
    ) -> MemoryRecord:
        record = self.state.commitments[commitment] if isinstance(commitment, str) else commitment
        due_in = max(0, (record.due_tick or self.state.tick) - self.state.tick)
        return self.register_concern(
            text or f"I need to follow up on whether {record.actor} follows through: {record.text}",
            tags=("social", "commitment_followup", record.actor.lower()),
            priority=priority if priority is not None else max(0.65, record.importance),
            urgency=max(0.45, record.importance * 0.70),
            preferred_action=preferred_action,
            due_in=due_in,
            not_before_in=due_in,
            min_energy=0.18,
            blocked_tags=("threat",),
            source="self",
            commitment_id=record.commitment_id,
        )

    def _concern_from_memory(self, memory: MemoryRecord) -> ProspectiveConcern:
        tags = memory.tags
        due_raw = _tag_value(tags, f"{_META_PREFIX}due:")
        not_before_raw = _tag_value(tags, f"{_META_PREFIX}not_before:")
        required = tuple(tag.split(":", 1)[1] for tag in tags if tag.startswith(f"{_META_PREFIX}required:"))
        blocked = tuple(tag.split(":", 1)[1] for tag in tags if tag.startswith(f"{_META_PREFIX}blocked:"))
        commitment = _tag_value(tags, f"{_META_PREFIX}commitment:") or None
        return ProspectiveConcern(
            concern_id=memory.memory_id,
            text=memory.text,
            priority=_decode_percent(tags, f"{_META_PREFIX}priority:", memory.importance),
            urgency=_decode_percent(tags, f"{_META_PREFIX}urgency:", memory.arousal),
            preferred_action=_tag_value(tags, f"{_META_PREFIX}action:", "explore"),
            due_tick=int(due_raw) if due_raw else None,
            not_before_tick=int(not_before_raw) if not_before_raw else None,
            min_energy=_decode_percent(tags, f"{_META_PREFIX}min_energy:", 0.25),
            required_tags=required,
            blocked_tags=blocked,
            status=_tag_value(tags, f"{_META_PREFIX}status:", "open"),
            attempts=_tag_int(tags, f"{_META_PREFIX}attempts:", 0),
            deferrals=_tag_int(tags, f"{_META_PREFIX}deferrals:", 0),
            cooldown_until=_tag_int(tags, f"{_META_PREFIX}cooldown:", 0),
            commitment_id=commitment,
        )

    def concerns(self, *, status: str | None = "open") -> list[ProspectiveConcern]:
        rows = []
        for memory in self.state.memories:
            if "opportunity" not in memory.tags or "prospective" not in memory.tags:
                continue
            concern = self._concern_from_memory(memory)
            if status is None or concern.status == status:
                rows.append(concern)
        return rows

    def _concern_memory(self, concern_id: str) -> MemoryRecord:
        for memory in self.state.memories:
            if memory.memory_id == concern_id and "opportunity" in memory.tags:
                return memory
        raise KeyError(concern_id)

    def _update_counter(self, memory: MemoryRecord, field: str, value: int) -> None:
        memory.tags = _replace_tag(memory.tags, f"{_META_PREFIX}{field}:", str(max(0, int(value))))

    def _set_status(self, memory: MemoryRecord, status: str) -> None:
        memory.tags = _replace_tag(memory.tags, f"{_META_PREFIX}status:", status)

    def resolve_concern(self, concern_id: str, *, satisfied: bool, reason: str = "") -> ProspectiveConcern:
        memory = self._concern_memory(concern_id)
        status = "satisfied" if satisfied else "abandoned"
        self._set_status(memory, status)
        memory.tags = tuple(dict.fromkeys((*memory.tags, f"opportunity_{status}")))
        self.state.add_memory(
            reason or (f"I finished what I meant to do: {memory.text}" if satisfied else f"I decided not to keep pursuing this: {memory.text}"),
            tags=("prospective_resolution", status),
            valence=0.35 if satisfied else -0.05,
            arousal=0.25,
            importance=max(0.45, memory.importance * 0.70),
            provenance=MemoryProvenance.SELF_REFLECTION,
            source="self",
        )
        return self._concern_from_memory(memory)

    def mark_concern_impossible(self, concern_id: str, *, reason: str = "") -> ProspectiveConcern:
        return self.resolve_concern(concern_id, satisfied=False, reason=reason or "That goal is no longer possible, so I am letting it go.")

    def _recent_context_tags(self, max_age: int = 8) -> set[str]:
        for memory in reversed(self.state.memories):
            if memory.provenance is not MemoryProvenance.FIRST_PERSON:
                continue
            if self.state.tick - memory.tick > max_age:
                return set()
            return {tag for tag in memory.tags if not tag.startswith(_META_PREFIX)}
        return set()

    def _commitment_is_open(self, concern: ProspectiveConcern) -> bool:
        if concern.commitment_id is None:
            return True
        commitment = self.state.commitments.get(concern.commitment_id)
        return commitment is not None and commitment.status == "open"

    def _concern_viability(self, concern: ProspectiveConcern, context_tags: set[str]) -> tuple[bool, str]:
        if concern.status != "open":
            return False, "resolved"
        if concern.not_before_tick is not None and self.state.tick < concern.not_before_tick:
            return False, "too_early"
        if self.state.tick < concern.cooldown_until:
            return False, "cooldown"
        if not self._commitment_is_open(concern):
            memory = self._concern_memory(concern.concern_id)
            self._set_status(memory, "satisfied")
            return False, "linked_commitment_resolved"
        if self.state.needs.get("energy", 0.0) < concern.min_energy:
            return False, "low_energy"
        if concern.required_tags and not set(concern.required_tags).issubset(context_tags):
            return False, "context_missing"
        if set(concern.blocked_tags) & context_tags:
            return False, "context_blocked"
        if self.state.affect.get("fear", 0.0) >= 0.55 and concern.preferred_action in {"explore", "ask", "approach", "repair"}:
            return False, "safety_override"
        return True, "available"

    def _concern_score(self, concern: ProspectiveConcern) -> float:
        score = 0.40 * concern.priority + 0.18 * concern.urgency
        curiosity = self.state.needs.get("curiosity", 0.35)
        affiliation = self.state.needs.get("affiliation", 0.25)
        if concern.preferred_action in {"explore", "ask"}:
            score += 0.14 * curiosity
        if concern.preferred_action in {"ask", "repair", "approach", "seek_connection"}:
            score += 0.12 * affiliation
        if concern.due_tick is not None:
            distance = concern.due_tick - self.state.tick
            if distance <= 0:
                score += 0.30
            elif distance <= 3:
                score += 0.20
            elif distance <= 8:
                score += 0.10
        score += min(0.10, concern.deferrals * 0.02)
        score -= min(0.12, concern.attempts * 0.03)
        return score

    def _best_actionable_concern(self) -> tuple[ProspectiveConcern | None, dict[str, str]]:
        context_tags = self._recent_context_tags()
        reasons: dict[str, str] = {}
        viable: list[tuple[float, ProspectiveConcern]] = []
        for concern in self.concerns(status="open"):
            available, reason = self._concern_viability(concern, context_tags)
            reasons[concern.concern_id] = reason
            if available:
                viable.append((self._concern_score(concern), concern))
            elif reason in {"low_energy", "context_missing", "context_blocked", "safety_override", "too_early"}:
                memory = self._concern_memory(concern.concern_id)
                self._update_counter(memory, "deferrals", concern.deferrals + 1)
        if not viable:
            return None, reasons
        viable.sort(key=lambda row: (row[0], row[1].priority, -row[1].attempts), reverse=True)
        score, concern = viable[0]
        if score < 0.48:
            return None, reasons
        return concern, reasons

    def _pending_opportunity(self) -> MemoryRecord | None:
        concern, _ = self._best_actionable_concern()
        return self._concern_memory(concern.concern_id) if concern is not None else None

    def heartbeat(self, *, allow_inner_speech: bool = True):
        concern, reasons = self._best_actionable_concern()
        if concern is None:
            return super().heartbeat(allow_inner_speech=allow_inner_speech)

        memory = self._concern_memory(concern.concern_id)
        event = WorldEvent(
            kind="endogenous",
            source="self",
            text=concern.text,
            tags=tuple(dict.fromkeys((
                "idle",
                "time_passed",
                "opportunity_active",
                f"concern_id:{concern.concern_id}",
                f"preferred_action:{concern.preferred_action}",
                *(tag for tag in memory.tags if not tag.startswith(_META_PREFIX)),
            ))),
            valence=0.08,
            intensity=max(0.15, min(0.70, concern.priority * 0.45 + concern.urgency * 0.25)),
            perceived=False,
        )
        result = self.step(event, allow_inner_speech=allow_inner_speech)
        successful_attempt = result.selected_action == concern.preferred_action
        if successful_attempt:
            self._update_counter(memory, "attempts", concern.attempts + 1)
            self._update_counter(memory, "cooldown", self.state.tick + 3)
            memory.tags = tuple(dict.fromkeys((*memory.tags, "opportunity_acted")))
        else:
            self._update_counter(memory, "deferrals", concern.deferrals + 1)
            self._update_counter(memory, "cooldown", self.state.tick + 1)
        result.developer_trace["agency"] = {
            "selected_concern_id": concern.concern_id,
            "preferred_action": concern.preferred_action,
            "available_reasons": reasons,
            "attempted": successful_attempt,
        }
        return result

    def _candidates(self, event: WorldEvent, relation: RelationshipState, memories: list[MemoryRecord]) -> list[ActionCandidate]:
        rows = super()._candidates(event, relation, memories)
        if event.kind != "endogenous" or "opportunity_active" not in event.tags:
            return rows

        concern_id = next((tag.split(":", 1)[1] for tag in event.tags if tag.startswith("concern_id:")), "")
        try:
            concern = self._concern_from_memory(self._concern_memory(concern_id))
        except KeyError:
            return rows

        recent = self.state.recent_actions[-6:]
        adjusted: list[ActionCandidate] = []
        for candidate in rows:
            utility = candidate.utility
            if candidate.name == concern.preferred_action:
                # A selected prospective concern should normally shape intention,
                # while rest and safety remain free to win when the organism needs
                # them. This is stronger than a cosmetic dialogue preference.
                utility += 0.50 + 0.36 * concern.priority + 0.16 * concern.urgency
                repeats = sum(1 for action in recent[-3:] if action == candidate.name)
                utility -= min(0.18, repeats * 0.06)
            elif candidate.name == "wait":
                utility -= 0.10 * concern.priority
            adjusted.append(ActionCandidate(candidate.name, utility, candidate.reasons))
        return adjusted
