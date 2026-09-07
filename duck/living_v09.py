"""Endogenous goal formation and counterfactual planning for DUCK v0.9.

v0.8 can carry unfinished intentions once they exist. v0.9 adds a bounded planning
layer that can form selected goals from lived experience, compare more than one
route, decompose a chosen route into sequential subgoals, and revise the route when
an action outcome contradicts the plan.

Planning metadata remains mechanistic. Canonical persistence still lives in the
existing SubjectState memory ledger. The simulated subject can access qualitative
self-reflections and current concerns, but never raw route scores, indexes, internal
plan IDs, or private planning tags.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .living import MemoryProvenance, MemoryRecord, WorldEvent, _clamp
from .living_v08 import LivingDuck as AgencyLivingDuck, ProspectiveConcern


_PLAN_PREFIX = "pl_"


def _tag_value(tags: Iterable[str], prefix: str, default: str = "") -> str:
    for tag in tags:
        if tag.startswith(prefix):
            return tag[len(prefix) :]
    return default


def _replace_tag(tags: tuple[str, ...], prefix: str, value: str) -> tuple[str, ...]:
    kept = [tag for tag in tags if not tag.startswith(prefix)]
    if value:
        kept.append(f"{prefix}{value}")
    return tuple(dict.fromkeys(kept))


@dataclass(frozen=True)
class PlanStepSpec:
    text: str
    preferred_action: str
    min_energy: float = 0.20
    tags: tuple[str, ...] = ()


@dataclass(frozen=True)
class GoalPlan:
    plan_id: str
    text: str
    kind: str
    status: str
    routes: tuple[str, ...]
    route_index: int
    step_index: int
    trigger_memory_id: str | None
    pending_concern_id: str | None
    pending_action_id: str | None

    @property
    def current_route(self) -> str | None:
        if 0 <= self.route_index < len(self.routes):
            return self.routes[self.route_index]
        return None


class LivingDuck(AgencyLivingDuck):
    """v0.9 candidate with bounded endogenous goals and hierarchical replanning."""

    _ROUTES: dict[str, dict[str, tuple[PlanStepSpec, ...]]] = {
        "investigate": {
            "direct_exploration": (
                PlanStepSpec("I should inspect it directly.", "explore", 0.28, ("investigate",)),
            ),
            "cautious_inquiry": (
                PlanStepSpec("I should ask for more information first.", "ask", 0.18, ("investigate", "inquiry")),
                PlanStepSpec("I should inspect it after gathering more information.", "explore", 0.28, ("investigate",)),
            ),
        },
        "overcome": {
            "inspect_then_act": (
                PlanStepSpec("I should examine what is blocking me.", "explore", 0.28, ("obstacle", "planning")),
                PlanStepSpec("I should try the path that now looks workable.", "explore", 0.34, ("obstacle", "planning")),
            ),
            "seek_information_then_act": (
                PlanStepSpec("I should ask for information about the obstacle.", "ask", 0.18, ("obstacle", "inquiry")),
                PlanStepSpec("I should use what I learned to try another way through.", "explore", 0.30, ("obstacle", "planning")),
            ),
        },
        "repair": {
            "direct_repair": (
                PlanStepSpec("I should try to repair the relationship directly.", "repair", 0.18, ("repair", "social")),
            ),
            "clarify_then_repair": (
                PlanStepSpec("I should ask what went wrong before trying to repair it.", "ask", 0.16, ("repair", "social", "inquiry")),
                PlanStepSpec("I should make a repair attempt with that context in mind.", "repair", 0.18, ("repair", "social")),
            ),
        },
    }

    def _plan_from_memory(self, memory: MemoryRecord) -> GoalPlan:
        routes = tuple(filter(None, _tag_value(memory.tags, f"{_PLAN_PREFIX}routes:").split("|")))
        try:
            route_index = int(_tag_value(memory.tags, f"{_PLAN_PREFIX}route_index:", "0"))
        except ValueError:
            route_index = 0
        try:
            step_index = int(_tag_value(memory.tags, f"{_PLAN_PREFIX}step_index:", "0"))
        except ValueError:
            step_index = 0
        return GoalPlan(
            plan_id=memory.memory_id,
            text=memory.text,
            kind=_tag_value(memory.tags, f"{_PLAN_PREFIX}kind:", "investigate"),
            status=_tag_value(memory.tags, f"{_PLAN_PREFIX}status:", "active"),
            routes=routes,
            route_index=max(0, route_index),
            step_index=max(0, step_index),
            trigger_memory_id=_tag_value(memory.tags, f"{_PLAN_PREFIX}trigger:") or None,
            pending_concern_id=_tag_value(memory.tags, f"{_PLAN_PREFIX}pending_concern:") or None,
            pending_action_id=_tag_value(memory.tags, f"{_PLAN_PREFIX}pending_action:") or None,
        )

    def plans(self, *, status: str | None = None) -> list[GoalPlan]:
        rows: list[GoalPlan] = []
        for memory in self.state.memories:
            if "plan_root" not in memory.tags:
                continue
            plan = self._plan_from_memory(memory)
            if status is None or plan.status == status:
                rows.append(plan)
        return rows

    def _plan_memory(self, plan_id: str) -> MemoryRecord:
        for memory in self.state.memories:
            if memory.memory_id == plan_id and "plan_root" in memory.tags:
                return memory
        raise KeyError(plan_id)

    @staticmethod
    def _set_plan_field(memory: MemoryRecord, field: str, value: str | int | None) -> None:
        memory.tags = _replace_tag(memory.tags, f"{_PLAN_PREFIX}{field}:", "" if value is None else str(value))

    def _route_score(self, kind: str, route: str) -> float:
        fear = self.state.affect.get("fear", 0.0)
        curiosity = self.state.needs.get("curiosity", 0.35)
        autonomy = self.state.needs.get("autonomy", 0.60)
        affiliation = self.state.needs.get("affiliation", 0.25)
        safety = self.state.needs.get("safety", 0.80)
        competence = self.state.needs.get("competence", 0.55)
        energy = self.state.needs.get("energy", 0.80)

        if kind == "investigate":
            if route == "direct_exploration":
                return 0.55 * curiosity + 0.24 * autonomy + 0.15 * energy - 0.62 * fear
            return 0.32 * curiosity + 0.22 * safety + 0.16 * affiliation + 0.12 * competence - 0.08 * fear + 0.08
        if kind == "overcome":
            if route == "inspect_then_act":
                return 0.34 * competence + 0.30 * autonomy + 0.16 * energy - 0.48 * fear
            return 0.22 * competence + 0.18 * affiliation + 0.24 * safety - 0.10 * fear + 0.12
        if kind == "repair":
            if route == "direct_repair":
                return 0.32 * affiliation + 0.24 * autonomy + 0.18 * competence - 0.20 * fear + 0.08
            return 0.28 * affiliation + 0.22 * safety + 0.15 * competence - 0.06 * fear + 0.10
        return 0.0

    def _ordered_routes(self, kind: str) -> tuple[str, ...]:
        options = self._ROUTES.get(kind)
        if not options:
            raise ValueError(f"unknown plan kind: {kind}")
        return tuple(sorted(options, key=lambda route: (self._route_score(kind, route), route), reverse=True))

    def form_goal(
        self,
        kind: str,
        text: str,
        *,
        trigger_memory_id: str | None = None,
        importance: float = 0.82,
    ) -> MemoryRecord:
        normalized = str(text).strip()
        if not normalized:
            raise ValueError("goal text must not be empty")
        for existing in self.plans(status="active"):
            if existing.kind == kind and existing.text == normalized:
                return self._plan_memory(existing.plan_id)

        routes = self._ordered_routes(kind)
        tags = [
            "plan_root",
            "prospective_plan",
            f"{_PLAN_PREFIX}status:active",
            f"{_PLAN_PREFIX}kind:{kind}",
            f"{_PLAN_PREFIX}routes:{'|'.join(routes)}",
            f"{_PLAN_PREFIX}route_index:0",
            f"{_PLAN_PREFIX}step_index:0",
        ]
        if trigger_memory_id:
            tags.append(f"{_PLAN_PREFIX}trigger:{trigger_memory_id}")
        root = self.state.add_memory(
            normalized,
            tags=tags,
            valence=0.12,
            arousal=0.42,
            importance=_clamp(importance),
            provenance=MemoryProvenance.SELF_REFLECTION,
            source="self",
        )
        self._activate_current_step(root)
        return root

    def _route_steps(self, plan: GoalPlan) -> tuple[PlanStepSpec, ...]:
        route = plan.current_route
        if route is None:
            return ()
        return self._ROUTES.get(plan.kind, {}).get(route, ())

    def _activate_current_step(self, root: MemoryRecord) -> MemoryRecord | None:
        plan = self._plan_from_memory(root)
        if plan.status != "active":
            return None
        steps = self._route_steps(plan)
        if plan.step_index >= len(steps):
            self._complete_plan(root)
            return None

        current = steps[plan.step_index]
        concern = self.register_concern(
            current.text,
            tags=(
                "plan_step",
                "planning",
                plan.kind,
                *current.tags,
                f"{_PLAN_PREFIX}plan:{plan.plan_id}",
                f"{_PLAN_PREFIX}step:{plan.step_index}",
                f"{_PLAN_PREFIX}route:{plan.current_route or ''}",
            ),
            priority=max(0.72, root.importance),
            urgency=0.56,
            preferred_action=current.preferred_action,
            min_energy=current.min_energy,
            blocked_tags=("threat",),
            source="self",
        )
        self._set_plan_field(root, "pending_concern", concern.memory_id)
        self._set_plan_field(root, "pending_action", None)
        return concern

    def _complete_plan(self, root: MemoryRecord) -> GoalPlan:
        self._set_plan_field(root, "status", "completed")
        self._set_plan_field(root, "pending_concern", None)
        self._set_plan_field(root, "pending_action", None)
        root.tags = tuple(dict.fromkeys((*root.tags, "plan_completed")))
        self.state.add_memory(
            f"I completed the plan I formed: {root.text}",
            tags=("plan_resolution", "completed"),
            valence=0.32,
            arousal=0.22,
            importance=max(0.55, root.importance * 0.75),
            provenance=MemoryProvenance.SELF_REFLECTION,
            source="self",
        )
        return self._plan_from_memory(root)

    def _abandon_plan(self, root: MemoryRecord, reason: str) -> GoalPlan:
        self._set_plan_field(root, "status", "abandoned")
        self._set_plan_field(root, "pending_concern", None)
        self._set_plan_field(root, "pending_action", None)
        root.tags = tuple(dict.fromkeys((*root.tags, "plan_abandoned")))
        self.state.add_memory(
            reason,
            tags=("plan_resolution", "abandoned"),
            valence=-0.08,
            arousal=0.30,
            importance=max(0.50, root.importance * 0.70),
            provenance=MemoryProvenance.SELF_REFLECTION,
            source="self",
        )
        return self._plan_from_memory(root)

    def _plan_for_concern(self, concern_id: str) -> tuple[MemoryRecord, GoalPlan] | None:
        try:
            concern_memory = self._concern_memory(concern_id)
        except KeyError:
            return None
        plan_id = _tag_value(concern_memory.tags, f"{_PLAN_PREFIX}plan:")
        if not plan_id:
            return None
        try:
            root = self._plan_memory(plan_id)
        except KeyError:
            return None
        return root, self._plan_from_memory(root)

    def _plan_for_pending_action(self, action_id: str) -> tuple[MemoryRecord, GoalPlan] | None:
        for plan in self.plans(status="active"):
            if plan.pending_action_id == action_id:
                return self._plan_memory(plan.plan_id), plan
        return None

    def heartbeat(self, *, allow_inner_speech: bool = True):
        result = super().heartbeat(allow_inner_speech=allow_inner_speech)
        agency = result.developer_trace.get("agency")
        if not agency:
            return result
        concern_id = str(agency.get("selected_concern_id") or "")
        linked = self._plan_for_concern(concern_id)
        if linked is None:
            return result
        root, plan = linked
        attempted = bool(agency.get("attempted"))
        if attempted:
            self._set_plan_field(root, "pending_concern", concern_id)
            self._set_plan_field(root, "pending_action", result.action_id)
        result.developer_trace["planning"] = {
            "plan_id": plan.plan_id,
            "kind": plan.kind,
            "route": plan.current_route,
            "route_index": plan.route_index,
            "step_index": plan.step_index,
            "attempted": attempted,
        }
        return result

    def resolve_outcome(
        self,
        action_id: str,
        *,
        success: float,
        valence: float,
        description: str,
        tags: Iterable[str] = (),
    ) -> None:
        linked = self._plan_for_pending_action(action_id)
        success_value = _clamp(success)
        super().resolve_outcome(action_id, success=success, valence=valence, description=description, tags=tags)
        if linked is None:
            return

        root, old_plan = linked
        concern_id = old_plan.pending_concern_id
        if success_value >= 0.60:
            if concern_id:
                try:
                    self.resolve_concern(concern_id, satisfied=True, reason=f"That step worked: {description}")
                except KeyError:
                    pass
            self._set_plan_field(root, "pending_action", None)
            self._set_plan_field(root, "pending_concern", None)
            self._set_plan_field(root, "step_index", old_plan.step_index + 1)
            refreshed = self._plan_from_memory(root)
            if refreshed.step_index >= len(self._route_steps(refreshed)):
                self._complete_plan(root)
            else:
                self._activate_current_step(root)
            return

        if success_value <= 0.38:
            if concern_id:
                try:
                    self.resolve_concern(concern_id, satisfied=False, reason=f"That approach did not work: {description}")
                except KeyError:
                    pass
            next_route = old_plan.route_index + 1
            self._set_plan_field(root, "pending_action", None)
            self._set_plan_field(root, "pending_concern", None)
            if next_route < len(old_plan.routes):
                self._set_plan_field(root, "route_index", next_route)
                self._set_plan_field(root, "step_index", 0)
                self.state.add_memory(
                    "That approach did not work, so I am trying another way.",
                    tags=("plan_revision", "counterfactual_revision"),
                    valence=-0.05,
                    arousal=0.34,
                    importance=max(0.58, root.importance * 0.78),
                    provenance=MemoryProvenance.SELF_REFLECTION,
                    source="self",
                )
                self._activate_current_step(root)
            else:
                self._abandon_plan(root, f"I ran out of workable approaches for this goal: {root.text}")
            return

        self._set_plan_field(root, "pending_action", None)

    def _find_trigger_memory(self, event: WorldEvent) -> str | None:
        for memory in reversed(self.state.memories):
            if memory.tick != self.state.tick:
                break
            if memory.provenance is MemoryProvenance.FIRST_PERSON and memory.text == event.text:
                return memory.memory_id
        return None

    def _infer_goal(self, event: WorldEvent) -> tuple[str, str] | None:
        tags = {str(tag).lower() for tag in event.tags}
        if tags & {"mystery", "unknown", "novel"} and self.state.needs.get("curiosity", 0.0) >= 0.48:
            return "investigate", f"I want to understand what I encountered: {event.text.strip()}"
        if tags & {"obstacle", "blocked"} and self.state.needs.get("autonomy", 0.0) >= 0.48:
            return "overcome", f"I want to work out a way past this obstacle: {event.text.strip()}"
        if "repair_needed" in tags:
            return "repair", f"I want to repair what went wrong with {event.source}."
        if "conflict" in tags and event.source not in {"self", "world", "system", ""}:
            relation = self.state.relationship(event.source)
            if relation.attachment >= 0.20 or relation.trust >= 0.42:
                return "repair", f"I want to repair what went wrong with {event.source}."
        return None

    def _maybe_form_goal_from_experience(self, event: WorldEvent) -> MemoryRecord | None:
        if not event.perceived or event.kind == "endogenous" or event.source == "self":
            return None
        inferred = self._infer_goal(event)
        if inferred is None:
            return None
        kind, text = inferred
        return self.form_goal(kind, text, trigger_memory_id=self._find_trigger_memory(event))

    def step(self, event: WorldEvent, *, allow_inner_speech: bool = True):
        result = super().step(event, allow_inner_speech=allow_inner_speech)
        before = {plan.plan_id for plan in self.plans(status="active")}
        root = self._maybe_form_goal_from_experience(event)
        if root is not None and root.memory_id not in before:
            plan = self._plan_from_memory(root)
            result.developer_trace["goal_formation"] = {
                "plan_id": plan.plan_id,
                "kind": plan.kind,
                "route": plan.current_route,
                "trigger_memory_id": plan.trigger_memory_id,
            }
        return result
