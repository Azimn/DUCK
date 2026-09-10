"""Small world adapted from Persona-and-Jelly-Sandwich- at f196dde.

Jelly's day cycle and ambient room model are retained. DUCK owns canonical elapsed
simulation time, evidence transfer, grounded consequences and atomic persistence.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
import math

from .affordances_v010 import Affordance, AffordanceSource
from .body_v010 import unit
from .perception_v010 import FactObservation, Modality, SensoryEvidence
from .spatial_v010 import LocatedStimulus, ObservationPacket, ObserverState, Vec3


@dataclass
class RoomObject:
    object_id: str
    name: str
    position: Vec3
    occluded: bool = False
    openable: bool = False
    opened: bool = False
    effort: float = 0.1
    sound: str = ""
    sound_strength: float = 0.5
    is_person: bool = False

    def __post_init__(self):
        if not self.object_id or not self.name or len(self.object_id) > 100 or len(self.name) > 200:
            raise ValueError("room objects require bounded identity and names")
        self.effort = unit(self.effort)
        self.sound_strength = unit(self.sound_strength)

    @classmethod
    def from_dict(cls, data):
        return cls(**{**data, "position": Vec3(**data["position"])})


@dataclass
class RoomState:
    room_id: str = "room-001"
    name: str = "The Room"
    light: float = 0.5
    noise: float = 0.15
    temperature: float = 0.55
    clutter: float = 0.15
    novelty: float = 0.1
    auto_day_cycle: bool = True
    simulation_seconds: float = 43200.0
    tick_seconds: float = 60.0
    catchup_remainder: float = 0.0
    position: Vec3 = Vec3()
    forward: Vec3 = Vec3(1, 0, 0)
    objects: dict[str, RoomObject] = field(default_factory=dict)
    visited: set[str] = field(default_factory=set)

    def __post_init__(self):
        self.forward.normalized()
        for key in ("light", "noise", "temperature", "clutter", "novelty"):
            setattr(self, key, unit(getattr(self, key)))
        if not math.isfinite(self.tick_seconds) or self.tick_seconds <= 0:
            raise ValueError("room tick duration must be positive and finite")
        if not all(math.isfinite(x) and x >= 0 for x in (self.simulation_seconds, self.catchup_remainder)):
            raise ValueError("room time must be finite and nonnegative")
        if len(self.objects) > 48 or any(key != obj.object_id for key, obj in self.objects.items()):
            raise ValueError("room must contain at most 48 consistently keyed objects")
        self.visited.intersection_update(self.objects)

    def to_dict(self):
        data = asdict(self)
        data["visited"] = sorted(self.visited)
        return {"schema_version": "micropsi-duck.room.v1", **data}

    @classmethod
    def from_dict(cls, data):
        if data.get("schema_version") != "micropsi-duck.room.v1":
            raise ValueError("unsupported room schema")
        values = {k: v for k, v in data.items() if k != "schema_version"}
        values["position"] = Vec3(**values["position"])
        values["forward"] = Vec3(**values["forward"])
        values["objects"] = {k: RoomObject.from_dict(v) for k, v in values["objects"].items()}
        values["visited"] = set(values.get("visited", ()))
        return cls(**values)


class RoomWorld:
    def __init__(self, state: RoomState):
        self.state = state

    @staticmethod
    def daylight(hour):
        if hour < 5:
            return .08
        if hour < 8:
            return .08 + (hour-5) / 3 * .57
        if hour < 18:
            return .65
        if hour < 21:
            return .65 - (hour-18) / 3 * .47
        return .08

    def advance(self):
        room = self.state
        room.simulation_seconds += room.tick_seconds
        if room.auto_day_cycle:
            hour = (room.simulation_seconds / 3600) % 24
            room.light = self.daylight(hour)
            target_noise = .08 if hour < 6 or hour >= 22 else .16
            room.noise = unit(room.noise * .85 + target_noise * .15)
        room.novelty = unit(room.novelty * .97)

    def observer(self, subject_id):
        return ObserverState(subject_id, self.state.position, self.state.forward)

    def packet(self, subject_id):
        room = self.state
        rows = []
        for key, obj in sorted(room.objects.items()):
            features = ["person_present"] if obj.is_person else ["object_present"]
            if room.light < .2:
                features.append("dim_light")
            apparent = "open" if obj.opened else "closed"
            facts = (FactObservation(f"object:{key}:state", apparent, "vision"),) if obj.openable else ()
            content = f"{obj.name} is here."
            if obj.openable:
                content = f"{obj.name} appears {apparent}."
            rows.append(LocatedStimulus("vision:"+key, obj.position,
                SensoryEvidence(Modality.VISION, key if obj.is_person else "world", content,
                                strength=min(1.0, room.light * 1.5), features=tuple(features), observed_facts=facts),
                obj.occluded))
            if obj.sound:
                rows.append(LocatedStimulus("sound:"+key, obj.position,
                    SensoryEvidence(Modality.AUDITION, key if obj.is_person else "world", obj.sound,
                                    strength=obj.sound_strength,
                                    features=("loud_voice",) if obj.is_person and obj.sound_strength > .7 else ()),
                    obj.occluded))
        # Ambient evidence contains no object inventory or hidden object facts.
        if room.noise > .2:
            rows.append(LocatedStimulus("ambient:noise", room.position,
                SensoryEvidence(Modality.AUDITION, "world", "There is noise around me.", strength=room.noise)))
        if abs(room.temperature-.5) > .25:
            rows.append(LocatedStimulus("ambient:temperature", room.position,
                SensoryEvidence(Modality.TOUCH, "world", "The air feels warm." if room.temperature > .5 else "The air feels cold.",
                                strength=abs(room.temperature-.5),
                                features=("warm_sensation",) if room.temperature > .5 else ())))
        return ObservationPacket(subject_id, tuple(rows))

    def affordances(self, stimulus_id):
        if not stimulus_id.startswith("vision:"):
            return ()
        key = stimulus_id.split(":", 1)[1]
        obj = self.state.objects[key]
        rows = [Affordance("explore", AffordanceSource.ENVIRONMENT, key,
                           effort=obj.effort)]
        if obj.openable and not obj.opened and self.state.position.distance_to(obj.position) <= 1.5:
            rows.append(Affordance("open", AffordanceSource.ENVIRONMENT, key, effort=obj.effort))
        return tuple(rows)

    def execute(self, action, target):
        """Execute a deliberately small action set; unmodeled actions cannot succeed."""
        if action in {"wait", "rest"}:
            return 1.0, .1, "I waited for a while." if action == "wait" else "I rested for a while."
        obj = self.state.objects.get(target)
        if obj is None or obj.occluded:
            return 0.0, -.1, "That action could not reach its target."
        if action == "explore":
            self.state.visited.add(target)
            return 1.0, .15, f"I spent time looking at {obj.name}."
        if action == "open" and obj.openable and not obj.opened and self.state.position.distance_to(obj.position) <= 1.5:
            obj.opened = True
            return 1.0, .2, f"I opened {obj.name}."
        return 0.0, -.1, "The room could not carry out that action."
