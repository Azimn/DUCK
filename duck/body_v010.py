"""Small physical state and one-direction regulatory pressure with a legacy view."""
from __future__ import annotations

from collections.abc import MutableMapping
from dataclasses import asdict, dataclass
import math


def unit(value: float) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError("state values must be finite")
    return max(0.0, min(1.0, value))


@dataclass
class BodyState:
    energy_reserve: float = 0.85
    fatigue_load: float = 0.10
    sleep_pressure: float = 0.10
    pain_load: float = 0.0
    thermal_stress: float = 0.0
    autonomic_arousal: float = 0.05
    exertion_load: float = 0.0
    last_rest_tick: int = -1

    def __post_init__(self):
        for name in (
            "energy_reserve", "fatigue_load", "sleep_pressure", "pain_load",
            "thermal_stress", "autonomic_arousal", "exertion_load",
        ):
            setattr(self, name, unit(getattr(self, name)))

    def to_dict(self):
        return {"schema_version": "micropsi-duck.body.v1", **asdict(self)}

    @classmethod
    def from_dict(cls, data):
        if data.get("schema_version") != "micropsi-duck.body.v1":
            raise ValueError("unsupported body schema")
        return cls(**{k: v for k, v in data.items() if k != "schema_version"})


def energy_deficit(body: BodyState) -> float:
    return unit(0.65 * (1.0 - body.energy_reserve) + 0.35 * body.fatigue_load)


class BodyDynamics:
    def advance(self, body: BodyState, *, elapsed: float = 1.0) -> None:
        if not math.isfinite(elapsed) or elapsed < 0:
            raise ValueError("elapsed time must be finite and nonnegative")
        body.energy_reserve = unit(body.energy_reserve - 0.006 * elapsed)
        body.fatigue_load = unit(body.fatigue_load + 0.004 * elapsed)
        body.sleep_pressure = unit(body.sleep_pressure + 0.003 * elapsed)
        # Acute mobilization and exertion decay toward baseline instead of becoming
        # permanent motivational variables.
        body.autonomic_arousal = unit(0.05 + (body.autonomic_arousal - 0.05) * (0.90 ** elapsed))
        body.exertion_load = unit(body.exertion_load * (0.82 ** elapsed))

    def rest(self, body: BodyState, *, tick: int, effectiveness: float = 1.0) -> None:
        if body.last_rest_tick == tick:
            return
        scale = unit(effectiveness)
        body.energy_reserve = unit(body.energy_reserve + 0.035 * scale)
        body.fatigue_load = unit(body.fatigue_load - 0.045 * scale)
        body.sleep_pressure = unit(body.sleep_pressure - 0.035 * scale)
        body.autonomic_arousal = unit(body.autonomic_arousal - 0.08 * scale)
        body.exertion_load = unit(body.exertion_load - 0.12 * scale)
        body.last_rest_tick = tick

    def exert(self, body: BodyState, *, effort: float, success: float = 1.0) -> None:
        """Apply realized physical work; failed attempts can still be costly."""
        effort = unit(effort)
        success = unit(success)
        attempted = effort * (0.75 + 0.25 * success)
        body.energy_reserve = unit(body.energy_reserve - 0.030 * attempted)
        body.fatigue_load = unit(body.fatigue_load + 0.024 * attempted)
        body.exertion_load = unit(body.exertion_load + 0.20 * attempted)

    def mobilize(self, body: BodyState, *, threat_relevance: float, arousal: float) -> None:
        """Let appraisal alter physiology without making affect and body identical."""
        pressure = unit(0.7 * unit(threat_relevance) + 0.3 * unit(arousal))
        body.autonomic_arousal = unit(body.autonomic_arousal + 0.10 * pressure)


@dataclass
class RegulatoryState:
    energy_deficit: float = 0.15
    safety_deficit: float = 0.15
    affiliation_need: float = 0.25
    curiosity_drive: float = 0.35
    competence_deficit: float = 0.45
    coherence_deficit: float = 0.30
    autonomy_deficit: float = 0.35

    def to_dict(self):
        return {"schema_version": "micropsi-duck.regulatory.v1", **asdict(self)}

    @classmethod
    def from_dict(cls, data):
        if data.get("schema_version") != "micropsi-duck.regulatory.v1":
            raise ValueError("unsupported regulatory schema")
        return cls(**{k: unit(v) for k, v in data.items() if k != "schema_version"})


_FIELDS = {"energy": "energy_deficit", "safety": "safety_deficit",
           "affiliation": "affiliation_need", "curiosity": "curiosity_drive",
           "competence": "competence_deficit", "coherence": "coherence_deficit",
           "autonomy": "autonomy_deficit"}
_INVERTED = {"energy", "safety", "competence", "coherence", "autonomy"}


def legacy_need_view(reg: RegulatoryState) -> dict[str, float]:
    return {key: 1.0 - getattr(reg, name) if key in _INVERTED else getattr(reg, name)
            for key, name in _FIELDS.items()}


class LegacyNeedView(MutableMapping):
    """Write-through adapter, never a second independent store of needs.

    Legacy callers can still set energy for fixtures and migration. This explicitly
    sets reserve and fatigue together. Current runtime energy dynamics use BodyState.
    """
    def __init__(self, body: BodyState, regulatory: RegulatoryState):
        self.body, self.regulatory = body, regulatory

    def __getitem__(self, key):
        if key == "energy":
            self.regulatory.energy_deficit = energy_deficit(self.body)
        value = getattr(self.regulatory, _FIELDS[key])
        return 1.0 - value if key in _INVERTED else value

    def __setitem__(self, key, value):
        value = unit(value)
        name = _FIELDS[key]
        if key == "energy":
            self.body.energy_reserve = value
            self.body.fatigue_load = 1.0 - value
        setattr(self.regulatory, name, 1.0 - value if key in _INVERTED else value)

    def __delitem__(self, key):
        raise TypeError("regulatory dimensions cannot be deleted")

    def __iter__(self):
        return iter(_FIELDS)

    def __len__(self):
        return len(_FIELDS)

    def copy(self):
        return dict(self)
