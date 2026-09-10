# Evidence, body, and grounded action in v0.10

This contract records the implementation requested against `c081e6b` on 2026-09-10. Its goal is a continuing subject whose own history and condition influence what evidence means and which available action it chooses. It does not establish human equivalence or a 9/10 behavioral assessment.

## Learning authority

The historical `living.py` runtime now delegates adaptive observation, action bias, and outcome learning through three override seams. Their default implementations preserve AdaptiveSelfCore behavior. `living_v010.py` disables all three. Serialized adaptive state remains loadable and unchanged, but has no action-selection authority in current v0.10. Motivated strategy learning continues to consume actual outcomes. Memory, relationship updates, prediction calibration, and sequence learning retain their different roles.

## Evidence and appraisal

Native input is `SensoryEvidence` in `perception_v010.py`. It carries modality, source, content, strength, reliability, observable features, and `FactObservation` records. The feature vocabulary is deliberately small and validated. Semantic labels such as threat, supportive, conflict, good, and bad cannot be supplied as native sensory features. Percept confidence incorporates sensory reliability and currently reduces visual confidence in dim light. This is a bounded symbolic perception model, not raw image or audio understanding.

`AppraisalEngine` derives relevance from perceptual cues, relationship trust and guardedness, retrieved negative encounters, regulatory pressure, and expectation discrepancies. Coefficients are modeling parameters, not empirical psychological estimates. Identical loud and approaching-person cues therefore produce different threat appraisals for a trusted versus previously harmful person. Appraisal-derived tags temporarily drive the inherited affect and motivated-cognition machinery. This migration does not claim to have replaced every tag-based downstream mechanism.

`WorldEvent` remains an explicit compatibility adapter and the host's existing occurrence format. Its authored semantic tags, valence, and intensity remain compatibility hints so historical scenarios retain their meaning. Developer traces distinguish this path with `legacy_hints` and `compatibility_catalog`. Native evidence receives no such hints. An unperceived external event is not adapted into evidence. Host delivery advances a quiet heartbeat while keeping hidden facts outside the subject.

## Apparent facts and timing

Current perception integrates fact observations before motive preparation and action selection. The expectation ledger consumes those same observations directly. Confidence below 0.5 does not resolve a prediction; contradictory simultaneous observations also leave the prediction unresolved. Belief records retain uncertainty and memories retain observation source and reliability. An expectation resolution means the subject has sufficiently credible perceived evidence under this model. It does not prove external truth.

The compatibility event sent into inherited cognition always has an empty `world_facts` tuple. Current stepping no longer writes and clears authoritative facts in SubjectState. One-time historical migration remains at construction and host loading. `PersistentDuckHost.observe_evidence()` never mutates environment truth. Host `set_world_fact()` and legacy occurrence delivery remain explicit external-world operations.

## Body and regulation

`BodyState` stores reserve, fatigue, sleep pressure, pain, and thermal stress. Basal time progression reduces reserve and increases fatigue and sleep pressure. An executed endogenous rest, or a successfully resolved external rest action, updates physical state. The same rest tick cannot receive a second recovery credit when its outcome is reported. Failed external rest does not restore energy.

`RegulatoryState` uses one direction throughout: zero means no pressure and one means maximum modeled pressure. Energy pressure derives from body reserve and fatigue. The historical `SubjectState.needs` API becomes a write-through `LegacyNeedView`, not an independent dictionary. Compatibility writes to energy explicitly initialize reserve and fatigue together. Current runtime energy dynamics modify the body directly. Historical downstream writes to other need names translate into canonical pressure dimensions.

Sparse endogenous signals already read the resulting energy pressure. The experiential projection also supplies qualitative tiredness, sleepiness, pain, and temperature discomfort when relevant. No body values or regulatory records enter language packets. Pain and thermal stress currently produce sensations; detailed injury and thermodynamic simulation are outside this implementation.

`body_v010.json` and `regulatory_v010.json` join the transactional generation and its component hashes. Old snapshots without these components migrate from legacy needs once. When a committed new snapshot exists, body and regulatory components take precedence over compatibility mirrors. Exact pending strategy context is stored in cognition state and is part of the same transaction.

## Grounded possibilities

Native callers supply bounded typed `Affordance` objects. They carry action, source, target, effort, risk, complexity, novelty, and social exposure, never utility. Waiting and resting are local possibilities; credible social perception can make a small social repertoire available. External actions must be supplied explicitly. The host remains responsible for consequences and for ensuring that supplied possibilities reflect observable access rather than hidden knowledge.

The subject applies motive preferences, strategy learning, modulation, and pressure-dependent costs. The candidate set is restricted before the executive is recruited. An executive proposal cannot make an unavailable action exist. For multiple targets of one action, this first implementation chooses the target with greatest subject-evaluated utility before language selection. The selected target persists with the exact pending action. Target IDs do not enter the prose-only language packet.

Legacy WorldEvent calls retain the existing action catalog as a marked compatibility behavior. Quiet historical scheduling still uses that catalog. Native affordances are scoped to the current decision and must be refreshed by the host for subsequent observations; they are not an omniscient persistent world model. Arbitrary multistep plans over new target actions are not yet generated by the inherited planner.

## Contextual strategy learning

The strategy engine uses five enum regimes: baseline, threatened, fatigued, socially guarded, and high conflict. Selection records the regime against the exact pending action ID. A delayed outcome, including one delivered after restart or after body state changes, trains the selection-time context. Replacing an unresolved action replaces its pending context without training it.

Global signed strategy value remains available. Contextual value is blended with global value using evidence divided by evidence plus four, rather than adding two full scores. Context has neutral initialization and becomes influential with evidence. Context evidence saturates at 10,000; global action values are capped at 64 and contextual rows at 320. These are bounded strategy reward estimates, not proofs of causal effects. The separate causal transition learner remains global in this increment; applying regime conditioning to it is explicitly future work.

## Deterministic expression and language access

The local deterministic renderer accepts a qualitative `SocialExpressionStance` derived from relationship state. It no longer infers warmth or caution from exact private sentences. The current host supplies stance only to its built-in deterministic renderer. Custom and model renderers continue receiving only `ApprovedLanguagePacket`; neither stance records nor numeric relationship state are added to that packet. Rewording private trust prose therefore does not alter the deterministic social stance.

## Verification and limits

`tests/test_learning_authority_v010.py` checks that adversarial historical adaptive state cannot bias or learn in the current runtime and that historical learning still operates. `tests/test_embodied_perception_v010.py` exercises same-cycle evidence, absence of temporary world-truth writes, hidden-event isolation, uncertain and contradictory facts, history-dependent appraisal, native feature validation, physical rest, write-through regulation, migration and restart authority, crash recovery for both new components, selection-time contextual learning, unavailable executive actions, target persistence, pressure-sensitive effort, bounded contextual storage, and wording-independent expression.

The existing targeted discriminator retains its original social-history acceptance condition but now calls the deterministic stance interface. It continues to report that human believability is unmeasured. Ordinary CI and these targeted causal checks do not close the independent believability backlog item. Broader perception vocabularies, environment integrations, context-conditioned causal transitions, native grounded heartbeat scheduling, and independent interaction assessment remain separate work.


## Native host example

The caller can deliver apparent evidence independently of external reality. This example supplies an available exploration target and a sensory observation. It does not claim that the door really is open or automatically execute the selected action.

```python
from duck import (
    Affordance, AffordanceSource, FactObservation, Modality,
    PersistentDuckHost, SensoryEvidence,
)

host = PersistentDuckHost.open("aster-state", name="Aster")
stimulus = SensoryEvidence(
    modality=Modality.VISION,
    source="world",
    content="An unfamiliar door appears to be open.",
    features=("unfamiliar_object",),
    observed_facts=(FactObservation("door.state", "open", "vision", 0.93),),
)
step = host.observe_evidence(
    stimulus,
    affordances=(Affordance("explore", AffordanceSource.ENVIRONMENT,
                           target="door_12", effort=0.15, novelty=0.8),),
    allow_inner_speech=False,
)
pending = host.duck.state.pending_action
# The host can now execute pending.name against pending.target, then report the
# actual outcome using step.action_id. A selected intention is not a success.
```
