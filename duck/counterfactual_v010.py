"""Transient counterfactual route estimates for MicroPsiDUCK v0.10.

Counterfactuals are model predictions about routes considered at a decision point.
They are not observations, autobiographical memories, expectations that an event
will occur, or outcome evidence. This module deliberately contains no persistence
API so a route comparison cannot silently become subject history.
"""
from __future__ import annotations

from dataclasses import dataclass

COUNTERFACTUAL_PROVENANCE = "model_prediction"


@dataclass(frozen=True)
class CounterfactualRouteEstimate:
    """Developer-side estimate for one route at one decision point."""

    kind: str
    route: str
    action_sequence: tuple[str, ...]
    preference_score: float
    evidence_basis: tuple[str, ...]
    selected: bool = False
    provenance: str = COUNTERFACTUAL_PROVENANCE

    def __post_init__(self) -> None:
        if self.provenance != COUNTERFACTUAL_PROVENANCE:
            raise ValueError("counterfactual route provenance must remain model_prediction")
        if not str(self.kind).strip() or not str(self.route).strip():
            raise ValueError("counterfactual route estimate requires kind and route")
        if not self.action_sequence:
            raise ValueError("counterfactual route estimate requires an action sequence")


@dataclass(frozen=True)
class RouteComparisonSnapshot:
    """Complete transient route comparison made at a single organism tick."""

    tick: int
    kind: str
    selected_route: str
    estimates: tuple[CounterfactualRouteEstimate, ...]

    def __post_init__(self) -> None:
        if self.tick < 0:
            raise ValueError("route comparison tick cannot be negative")
        if not self.estimates:
            raise ValueError("route comparison requires at least one estimate")
        selected = [row for row in self.estimates if row.selected]
        if len(selected) != 1 or selected[0].route != self.selected_route:
            raise ValueError("route comparison must contain exactly one selected route")

    @property
    def counterfactuals(self) -> tuple[CounterfactualRouteEstimate, ...]:
        return tuple(row for row in self.estimates if not row.selected)


__all__ = [
    "COUNTERFACTUAL_PROVENANCE",
    "CounterfactualRouteEstimate",
    "RouteComparisonSnapshot",
]
