# Reusing prior experiments in DUCK

This increment adapts existing Azimn research rather than merging whole runtimes. The immediate target is a small world with spatially limited sensory access, refreshed affordances, enacted consequences, and continuing life. It does not introduce another learning authority or claim an optimal general cognitive architecture.

## Exact donors

Spatial access, Vec3 operations, observer configuration, bounded attention ranking, and deterministic stimulus tie-breaking are adapted from [TinyPersonaEngine commit 5eb2e84dbb43c828fae7a1459c9fd13535c7b332](https://github.com/Azimn/TinyPersonaEngine/tree/5eb2e84dbb43c828fae7a1459c9fd13535c7b332), specifically `src/living_entity_firstperson/perception.py` and `models.py`. The implementation is in `duck/spatial_v010.py`. DUCK's typed sensory evidence replaces the donor's arbitrary tag and world-fact-reference packet. No host-supplied urgency flag is imported. LANGUAGE in this spatial adapter means audible language; remote text should use the existing nonspatial evidence interface.

Room conditions, the piecewise day cycle, ambient noise relaxation, novelty decay, and bounded catch-up structure are adapted from [Persona-and-Jelly-Sandwich- commit f196ddef26ca755d814b5fb3e4ed41d1fead01a3](https://github.com/Azimn/Persona-and-Jelly-Sandwich-/tree/f196ddef26ca755d814b5fb3e4ed41d1fead01a3), specifically `digital_subject/world.py` and `host.py`. The adapted world is in `duck/room_v010.py`. The host integration uses explicit simulation seconds rather than local wall-clock timezone. Unapplied catch-up time is retained and persisted, not discarded or represented as lived history.

These are user-authorized adaptations from the user's repositories. No root LICENSE file was retrieved from either donor during this inspection, so this document makes no separate license claim for those repositories. Source ownership and exact donor revisions remain recorded here. No new external package dependency is introduced.

## Authority and integration

The optional room is stored inside `EnvironmentDynamicsState`, under its own `micropsi-duck.room.v1` payload, and participates in the existing transactional generation. Attaching a room does not create beliefs. Its objects, positions, occlusion, and open/closed states remain host information until spatial access and attention admit evidence.

A room tick advances ambient time, computes spatial access, selects one focus, and invokes one native cognitive cycle. There is one decision per tick, not one decision per sensory stimulus. The focus is deliberately limited to one for this first integration so sources and appraisals are not merged into an invented omniscient percept. Body temperature stress is a physical consequence of the room, independently projected as qualitative discomfort by the existing firewall.

The room offers inspection and, within reach, opening for the focused visible object. Waiting and resting remain local possibilities. Unmodeled social actions are not offered by the room adapter. Successful inspection records an enacted inspection; successful opening changes the actual object state. Subsequent ticks freshly expose the changed state. With `execute_actions=False`, selection creates a pending intention but no success evidence. Host object IDs stay outside the experiential language packet.

The room supplies the observable `object_present` cue. The subject interprets unfamiliarity using its own memories. Room bookkeeping about previously inspected objects is a history of host-executed operations, not authority over the subject's personal familiarity. The scalar room novelty field is retained from the donor as ambient world bookkeeping and does not directly dictate subjective novelty or utility.

## Use

```python
from duck import PersistentDuckHost, RoomObject, RoomState, Vec3

host = PersistentDuckHost.open("aster-room", name="Aster")
host.configure_room(RoomState(objects={
    "blue_door": RoomObject("blue_door", "The blue door", Vec3(1, 0, 0), openable=True),
    "cabinet": RoomObject("cabinet", "A cabinet", Vec3(-2, 0, 0)),
}))
steps = host.room_heartbeat(30, allow_inner_speech=False)
report = host.catch_up_room(600, max_ticks=5)
# Unprocessed elapsed time is persisted. A later call can drain it with zero new time.
host.catch_up_room(0, max_ticks=5)
```

`room_heartbeat` is the native refreshed-world interface. `catch_up_room` accepts elapsed simulation time explicitly; it does not install a background service or infer wall time. Neither method reconstructs events that were never simulated. After configuration, the standard host heartbeat also uses native room decisions when no scheduled occurrence takes priority. Room ticks and catch-up honor the existing scheduled-event queue. Existing unconfigured hosts retain their behavior.

## Verification scope

`tests/test_room_reuse_v010.py` checks out-of-view, occluded, out-of-range and nonproximal rejection; observer mismatch; auditory access; bounded attention; hidden-object isolation; refreshed targets; actual opening consequences; equivalent continuation after restart; retained catch-up debt; transactional room/body/time crash recovery; and a 120-tick native life run with energy recovery. The existing tests continue covering independent subjective appraisal and the prose-only firewall.

The toy world is intentionally small: at most 48 objects and 128 stimuli per packet. Geometry and occlusion are supplied by a host adapter, not inferred from prose or a physics engine. Navigation, rich conversation execution, arbitrary action plans, and simultaneous multimodal appraisal remain outside this small-world integration. The donor tests and structural checks do not establish human believability.

## Comparison follow-through

`docs/COMPONENT_SELECTION_v0.10.md` records the executed comparison, selected replacements, retained components, timing limits, and alternatives not yet evaluated. `duck.component_comparison` publishes reproducible machine-readable evidence through CI.
