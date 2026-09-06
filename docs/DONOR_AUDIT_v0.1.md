# DUCK Donor Audit v0.1

Status: research note, nonbinding.

This document surveys earlier experiments and adjacent repositories that may contain useful mechanisms for the clean `Azimn/DUCK` line. It does not authorize importing any subsystem. The binding architecture remains `ARCHITECTURE_v0.1.md`, and mechanisms still enter DUCK only after a concrete behavioral failure demonstrates their need.

## Donor rule

The default reuse unit is a tested idea or narrow mechanism, not a repository.

For each candidate donor:

1. identify the DUCK failure it could address;
2. extract the smallest relevant mechanism or test pattern;
3. preserve DUCK's subject-access and authority boundaries;
4. add a falsifiable DUCK acceptance test;
5. prefer a clean reimplementation when the donor is a third-party fork or licensing/provenance is unclear.

A donor is evidence, not architecture authority.

## Immediate donor: Persona-and-Jelly-Sandwich / digital_subject

Repository: `Azimn/Persona-and-Jelly-Sandwich-`

This is the strongest donor for DUCK's next experiment because it already states almost the same continuity criterion:

> Every new moment belongs to the same subject who lived through the previous moment, and the previous moment alters the subject who encounters the next one.

The most relevant implementation is `digital_subject/continuity_influence.py`, supported by `tests/test_continuity_causality.py` and `docs/CAUSAL_CONTINUITY.md`.

The useful pattern is not its complete continuity system. The useful pattern is the paired-history causal test:

```text
same present state
same present event
different lived history
        ->
different current behavior for an inspectable reason
```

Its `ContinuityInfluence` also preserves a good authority boundary: history may bias existing pressures and concerns, but it does not directly choose the action. DUCK should retain this principle if a consequence-carryover mechanism is added.

### Recommendation

Use the paired-history test methodology immediately. Do not transplant the complete commitment/expectation/epistemic subsystem into DUCK 0.2. First determine whether the smaller problem is simply persistence of consequence from one moment into the next.

## Immediate cross-check donor: TinyPersonaEngine

Repository: `Azimn/TinyPersonaEngine`

This experiment is unexpectedly close to current DUCK. Its `Living Entity: First-Person Bridge` separates authoritative observations, character-relative perceptual access, attention, subjective experience, memory cues, and validated action proposals. The architecture explicitly distinguishes world fact, perception, belief, experience, and subjective completion.

Relevant paths include:

- `src/living_entity_firstperson/pipeline.py`
- `src/living_entity_firstperson/perception.py`
- `src/living_entity_firstperson/transducer.py`
- `src/living_entity_firstperson/authority.py`
- `docs/ARCHITECTURE.md`
- `docs/REUSE_MAP.md`

### Recommendation

Do not merge its sensory pipeline into Milestone 0.1 or 0.2. Use it as a design cross-check for the subject-access firewall and, later, as a donor when real perception or world-fact/perception separation becomes an observed requirement.

Its strongest current lesson is that subjective state should be causally useful without becoming world authority.

## High-value later donor: Gelatinblob Sidecar

Location: `Azimn/Persona-and-Jelly-Sandwich-/gelatinblob_sidecar/`

Gelatinblob is the strongest experimental donor for path-dependent change that cannot be represented adequately by simple explicit state variables. It maintains a persistent recurrent latent state, predicts consequences, receives later outcomes, and uses bounded plasticity. Its later versions add regression-gated readout learning, neuromodulated provisional synaptic tags, outcome-dependent capture, ablations, and criticality diagnostics.

Potentially useful future mechanisms include:

- path-dependent latent state;
- prediction -> action -> outcome separation;
- prediction-error-driven learning;
- temporary versus consolidated change;
- plastic versus frozen ablation tests;
- rollback when adaptive updates regress behavior.

### Recommendation

Do not import the recurrent reservoir into DUCK 0.2. A neural/plastic substrate would be unjustified until a simpler explicit carryover model fails a meaningful longitudinal test. Keep Gelatinblob as the candidate donor for a later question such as: "Can the subject develop history-sensitive tendencies that are not reducible to hand-authored scalar decay rules?"

## Mature donor archive: persona_engine_PYTHONX / Wayfarer / DUCK / Ensemble

Repository: `Azimn/persona_engine_PYTHONX`

This repository remains the broadest engineering laboratory and has many useful proven mechanisms, but it also contains the most historical baggage. Current useful donor families include:

- objective world authority versus subjective belief;
- autobiographical provenance and cold-history retrieval;
- commitments and prospective state;
- explicit subject-owned time;
- deterministic persistence, replay, checkpointing, and recovery;
- renderer/model authority firewalls;
- body/effectors as capability constraints;
- action -> consequence -> prediction-error loops;
- epistemic evidence and revision;
- paired model-swap and lifecycle acceptance tests;
- CI and documentation hygiene.

The `ensemble` branch adds useful later-stage ideas such as noncanonical candidate ecology, character-owned conversational initiative, subject-relative appraisal, and evidence-gated expression. Those should remain later donors because DUCK currently does not yet need a sophisticated language realization ecology.

### Recommendation

Continue treating this repository as a quarry, not a base class. Port tests and authority principles before porting implementations.

## Early conceptual donor: Omnicore

Repository: `Azimn/Omnicore`

Omnicore contains early versions of several ideas that later became more rigorous elsewhere: emotionally weighted memory, a Cognitive State Monitor, valence/arousal/dominance-style affect, optional internal thought, and separation of stable persona from mutable memory/state.

### Recommendation

Use primarily as design-history evidence. Prefer newer implementations when the same idea exists in Wayfarer, Digital Subject, TinyPersonaEngine, or Gelatinblob. The six-dimensional emotion proposal may be worth revisiting only if a later affect experiment demonstrates that DUCK's simpler qualitative projection cannot represent required distinctions.

## Presence and product donors: AliceMod and Moemate

Repositories:

- `Azimn/AliceMod`
- `Azimn/moemate-core`

Alice demonstrates a mature desktop-companion surface with voice interaction, short/long-term memory, summarization, mood estimation, vision, tools, wake word, and an animated presence. Moemate separates companion skills such as mood, emote, expression, speech, and stop/wait behaviors from interchangeable model providers.

### Recommendation

These are not cognitive-core donors for the current milestone. They become relevant when DUCK has an internal subject worth embodying. At that point they can inform voice interruption, presence, expression, avatar state, tool capability boundaries, and the distinction between internal state and performance.

Because these repositories derive from third-party projects, reuse must respect upstream licensing and provenance. Prefer interface lessons or clean-room adaptation unless direct reuse is clearly permitted.

## Proactivity donor: rho

Repository: `Azimn/rho`

Rho provides a persistent heartbeat, scheduled check-ins, memory files, task triggers, and platform capabilities. Its key lesson for DUCK is operational rather than cognitive: an agent can continue to receive opportunities for action when no user message arrives.

### Recommendation

Do not import heartbeat machinery yet. Use it later when DUCK reaches a demonstrated failure of endogenous/prospective action, for example when a commitment becomes due but nothing happens unless the user sends another message.

## Historical conversational donor: chatbotAIML

Repository: `Azimn/chatbotAIML`

This older AIML-based system is useful as a reminder that authored dialogue landmarks and deterministic pattern matching can sometimes preserve recognizable voice or behavior more reliably than free generation.

### Recommendation

Do not use it as cognition. Consider it later as an evaluation/control baseline or as a source of sparse authored expression landmarks if a generative renderer becomes repetitive or character-inconsistent.

## Infrastructure donors

Some mechanisms should be copied forward sooner because they are research-neutral engineering hygiene rather than cognitive theory:

- Python 3.11/3.12 CI patterns;
- deterministic test harnesses;
- status/documentation authority checks;
- reproducible fixtures and seeds;
- regression and ablation methodology;
- recovery/rollback patterns when adaptive state is eventually introduced.

These do not need to wait for a cognitive failure because they reduce the chance of invalidating experiments.

## Current donor decision for the next experiment

The next DUCK question remains:

> Does something that happens to the subject alter the subject who encounters the next moment?

The donor audit changes how this should be tested, not the scope of the milestone.

The first experiment should borrow the paired-history method from `digital_subject`:

```text
History A: no disturbing event
History B: disturbing event occurs

then force both runs to receive the same neutral present input

expected if continuity exists:
    the two SubjectiveMoments or selected tendencies remain measurably different
    for a traceable reason
```

The current DUCK 0.1 runtime is expected to fail because every `MechanisticSnapshot` is supplied independently. That failure should be recorded before choosing the smallest Milestone 0.2 mechanism.

A simple explicit consequence residue is the first candidate. Gelatinblob-style latent plasticity, full autobiographical memory, commitments, world authority, and heartbeat/proactivity remain unapproved until simpler mechanisms fail their own tests.
