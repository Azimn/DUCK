"""Small world adapted from Persona-and-Jelly-Sandwich- at f196dde.

Jelly's day cycle and ambient room model are retained. DUCK owns canonical elapsed
simulation time, evidence transfer, grounded consequences and atomic persistence.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
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
    last_motion_tick: int = -1
    last_motion_feature: str = ""

    def __post_init__(self):
        if not self.object_id or not self.name or len(self.object_id) > 100 or len(self.name) > 200:
            raise ValueError("room objects require bounded identity and names")
        self.effort = unit(self.effort)
        self.sound_strength = unit(self.sound_strength)
        self.last_motion_tick = int(self.last_motion_tick)
        if self.last_motion_feature not in {"", "approaching_person", "receding_person"}:
            raise ValueError("unsupported room motion feature")

    @classmethod
    def from_dict(cls, data):
        return cls(**{**data, "position": Vec3(**data["position"])})


@dataclass
class RoomProcess:
    process_id: str
    kind: str
    target_id: str
    interval_ticks: int = 1
    next_tick: int = 1
    delta: Vec3 = Vec3()
    text: str = ""
    enabled: bool = True

    def __post_init__(self):
        if not self.process_id or not self.target_id:
            raise ValueError("room processes require identity and a target")
        if self.kind not in {"move", "toggle_open", "set_sound"}:
            raise ValueError("unsupported room process kind")
        self.interval_ticks = max(1, int(self.interval_ticks))
        self.next_tick = max(0, int(self.next_tick))
        self.text = str(self.text)[:500]

    @classmethod
    def from_dict(cls, data):
        return cls(**{**data, "delta": Vec3(**data.get("delta", {}))})


@dataclass(frozen=True)
class ExecutionOutcome:
    success: float
    valence: float
    description: str
    effort_realized: float = 0.0
    displacement: Vec3 | None = None

    def __post_init__(self):
        object.__setattr__(self, "success", unit(self.success))
        object.__setattr__(self, "valence", max(-1.0, min(1.0, float(self.valence))))
        object.__setattr__(self, "effort_realized", unit(self.effort_realized))

    def _legacy(self):
        return (self.success, self.valence, self.description)

    def __getitem__(self, index):
        return self._legacy()[index]

    def __iter__(self):
        return iter(self._legacy())


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
    processes: dict[str, RoomProcess] = field(default_factory=dict)
    pending_proprioception: str = ""

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
        if len(self.processes) > 64 or any(key != row.process_id for key, row in self.processes.items()):
            raise ValueError("room must contain at most 64 consistently keyed processes")
        self.pending_proprioception = str(self.pending_proprioception)[:500]
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
        values["processes"] = {k: RoomProcess.from_dict(v) for k, v in values.get("processes", {}).items()}
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

    @property
    def current_tick(self):
        return int(self.state.simulation_seconds // self.state.tick_seconds)

    def _advance_processes(self):
        room = self.state
        tick = self.current_tick
        for process in sorted(room.processes.values(), key=lambda row: row.process_id):
            if not process.enabled or process.next_tick > tick:
                continue
            obj = room.objects.get(process.target_id)
            if obj is None:
                process.next_tick = tick + process.interval_ticks
                continue
            if process.kind == "move":
                before = room.position.distance_to(obj.position)
                obj.position = Vec3(obj.position.x + process.delta.x,
                                    obj.position.y + process.delta.y,
                                    obj.position.z + process.delta.z)
                after = room.position.distance_to(obj.position)
                obj.last_motion_tick = tick
                if obj.is_person and after < before:
                    obj.last_motion_feature = "approaching_person"
                elif obj.is_person and after > before:
                    obj.last_motion_feature = "receding_person"
                else:
                    obj.last_motion_feature = ""
            elif process.kind == "toggle_open" and obj.openable:
                obj.opened = not obj.opened
            elif process.kind == "set_sound":
                obj.sound = process.text
            process.next_tick = tick + process.interval_ticks

    def advance(self):
        room = self.state
        room.simulation_seconds += room.tick_seconds
        if room.auto_day_cycle:
            hour = (room.simulation_seconds / 3600) % 24
            room.light = self.daylight(hour)
            target_noise = .08 if hour < 6 or hour >= 22 else .16
            room.noise = unit(room.noise * .85 + target_noise * .15)
        room.novelty = unit(room.novelty * .97)
        self._advance_processes()

    def observer(self, subject_id):
        return ObserverState(subject_id, self.state.position, self.state.forward)

    def packet(self, subject_id):
        room = self.state
        rows = []
        current_tick = self.current_tick
        for key, obj in sorted(room.objects.items()):
            features = ["person_present"] if obj.is_person else ["object_present"]
            if obj.last_motion_tick == current_tick and obj.last_motion_feature:
                features.append(obj.last_motion_feature)
            if room.light < .2:
                features.append("dim_light")
            apparent = "open" if obj.opened else "closed"
            facts = (FactObservation(f"object:{key}:state", apparent, "vision"),) if obj.openable else ()
            content = f"{obj.name} is here."
            if obj.openable:
                content = f"{obj.name} appears {apparent}."
            rows.append(LocatedStimulus("vision:"+key, obj.position,
                SensoryEvidence(Modality.VISION, key if obj.is_person else "world", content,
                                strength=min(1.0, room.light * 1.5), features=tuple(features),
                                observed_facts=facts, entity_id=key), obj.occluded))
            if obj.sound:
                sound_features = []
                if obj.is_person and obj.sound_strength > .7:
                    sound_features.append("loud_voice")
                if obj.last_motion_tick == current_tick and obj.last_motion_feature:
                    sound_features.append(obj.last_motion_feature)
                rows.append(LocatedStimulus("sound:"+key, obj.position,
                    SensoryEvidence(Modality.AUDITION, key if obj.is_person else "world", obj.sound,
                                    strength=obj.sound_strength, features=tuple(sound_features), entity_id=key),
                    obj.occluded))
        if room.pending_proprioception:
            rows.append(LocatedStimulus("proprioception:self", room.position,
                SensoryEvidence(Modality.PROPRIOCEPTION, "self", room.pending_proprioception,
                                strength=.75, reliability=.98, features=("self_motion",), entity_id="self")))
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
        if not (stimulus_id.startswith("vision:") or stimulus_id.startswith("sound:")):
            return ()
        modality, key = stimulus_id.split(":", 1)
        obj = self.state.objects[key]
        distance = self.state.position.distance_to(obj.position)
        rows = [Affordance("turn_toward", AffordanceSource.ENVIRONMENT, key, effort=.02)]
        if distance > 1.25:
            rows.append(Affordance("approach", AffordanceSource.ENVIRONMENT, key,
                                   effort=min(1.0, .08 + distance / 30.0)))
        elif distance > 0:
            rows.append(Affordance("step_back", AffordanceSource.ENVIRONMENT, key, effort=.08))
        if modality == "vision":
            rows.append(Affordance("explore", AffordanceSource.ENVIRONMENT, key, effort=obj.effort))
            if obj.openable and not obj.opened and distance <= 1.5:
                rows.append(Affordance("open", AffordanceSource.ENVIRONMENT, key, effort=obj.effort))
        return tuple(rows)

    @staticmethod
    def _direction(source: Vec3, target: Vec3):
        delta = target.minus(source)
        try:
            return delta.normalized()
        except ValueError:
            return None

    def execute(self, action, target):
        """Execute a bounded sensorimotor action set; unmodeled actions cannot succeed."""
        if action in {"wait", "rest"}:
            return ExecutionOutcome(1.0, .1,
                "I waited for a while." if action == "wait" else "I rested for a while.", 0.0)
        obj = self.state.objects.get(target)
        if obj is None or obj.occluded:
            return ExecutionOutcome(0.0, -.1, "That action could not reach its target.", .04)
        direction = self._direction(self.state.position, obj.position)
        if action == "turn_toward":
            if direction is None:
                return ExecutionOutcome(1.0, .02, "I was already right beside it.", .01)
            self.state.forward = direction
            self.state.pending_proprioception = "I turned my body toward it."
            return ExecutionOutcome(1.0, .04, "I turned toward it.", .02)
        if action == "approach":
            distance = self.state.position.distance_to(obj.position)
            if direction is None or distance <= 1.0:
                return ExecutionOutcome(1.0, .03, "I was already close enough.", .02)
            step = min(1.0, max(0.0, distance - 1.0))
            displacement = Vec3(direction.x * step, direction.y * step, direction.z * step)
            self.state.position = Vec3(self.state.position.x + displacement.x,
                                       self.state.position.y + displacement.y,
                                       self.state.position.z + displacement.z)
            self.state.forward = direction
            self.state.pending_proprioception = "I moved forward and came closer to it."
            return ExecutionOutcome(1.0, .06, "I moved closer.", min(1.0, .08 + step * .12), displacement)
        if action == "step_back":
            if direction is None:
                return ExecutionOutcome(0.0, -.02, "I could not tell which way to step back.", .03)
            step = .75
            displacement = Vec3(-direction.x * step, -direction.y * step, -direction.z * step)
            self.state.position = Vec3(self.state.position.x + displacement.x,
                                       self.state.position.y + displacement.y,
                                       self.state.position.z + displacement.z)
            self.state.pending_proprioception = "I stepped backward and made more space."
            return ExecutionOutcome(1.0, .03, "I stepped back.", .10, displacement)
        if action == "explore":
            self.state.visited.add(target)
            return ExecutionOutcome(1.0, .15, f"I spent time looking at {obj.name}.", obj.effort)
        if action == "open" and obj.openable and not obj.opened and self.state.position.distance_to(obj.position) <= 1.5:
            obj.opened = True
            return ExecutionOutcome(1.0, .2, f"I opened {obj.name}.", obj.effort)
        return ExecutionOutcome(0.0, -.1, "The room could not carry out that action.", obj.effort * .5)


__all__ = ["ExecutionOutcome", "RoomObject", "RoomProcess", "RoomState", "RoomWorld"]
