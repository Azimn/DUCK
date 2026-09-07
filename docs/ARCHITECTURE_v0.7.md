# DUCK Life-Simulation Architecture v0.7

Status: binding architecture candidate for the `life-sim-v0.7` branch.

DUCK remains a functional simulation of a persistent human-like subject. It does not claim phenomenal consciousness. Version 0.7 preserves the v0.6 regulated organism and treats extended lived simulation as the primary way to expose failures that short unit tests and fluent language can hide.

The governing invariants remain:

> The machinery may know numbers. The subject does not.

> What happens to the subject must be able to change the subject who encounters the next moment.

## Why v0.7 exists

The first thirty-day simulation showed that v0.6 was bounded and causally coherent, but still behaved artificially in subtler ways. Social action selection drifted toward excessive questioning, safety could remain depleted long after danger had passed, competence could saturate at its upper bound after repeated success, and a broken relationship could remain represented by a permanent binary warning even after later apology and reliable follow-through.

Version 0.7 corrects those long-horizon artifacts without adding a second subject authority or moving cognition into the language model.

## Architecture

```text
WORLD / USER / TIME
        |
        v
persistent mechanistic subject
  affect / needs / relationships
  beliefs / world facts / commitments
  autobiographical memory
  adaptive latent state
        |
        v
appraisal + retrieval + motivation
        |
        v
contextual action ecology
        |
        v
selected intention
        |
        +--------------------------+
        |                          |
        v                          v
SUBJECT ACCESS FIREWALL     developer diagnostics
        |
        v
SUBJECTIVE MOMENT
        |
        v
optional private cognition
        |
        v
expression / action
        |
        v
WORLD OUTCOME
        |
        v
learning + relationship update
        |
        v
slow regulation + reinterpretation
        |
        v
NEXT SUBJECT
```

## Subject authority and language boundary

Canonical subject state remains outside the language model. The subject-access firewall is mandatory. Raw affect values, need magnitudes, relationship scores, memory retrieval scores, embeddings, adaptive vectors, database identifiers, and hidden causal annotations remain developer-only state.

Inner speech is optional. Disabling language must not remove memory influence, belief revision, motivation, action selection, outcome learning, relationship change, homeostasis, or persistence.

The LLM may assist bounded interpretation, private cognition, and expression. It is not the organism and is not a substitute for the causal architecture.

## Long-horizon homeostasis

Needs are regulated quantities rather than permanent damage or reward meters. Safety may fall rapidly after threat, then recover slowly toward a conservative baseline when no new threat occurs. Recovery must not erase threat memories or learned caution.

Competence may increase through successful outcomes, but it also normalizes slowly rather than remaining pinned at 1.0 after a short run of success. Other v0.6 regulation rules remain intact: energy, affiliation, and curiosity are bounded and endogenous actions can partially regulate the drives that selected them.

## Contextual social action

Question asking is not a universal social default. A question directed at the subject normally favors responding. Supportive contact favors ordinary engagement. A genuine repair event can create a repair affordance when the relationship contains unresolved damage. Familiar and trusted people modestly favor ordinary response and approach.

Recent-action inhibition remains bounded and contextual. Its purpose is to prevent perseveration, not to force random behavioral variety.

## Relationship reinterpretation

Autobiographical facts are not rewritten when a relationship changes. If someone broke a commitment, that event remains in memory. Later apology, kept commitments, and reliable behavior can nevertheless change the present interpretation of that history.

The architecture therefore distinguishes historical fact from current relational meaning. A subject may move from "I'm still wary because they let me down before" toward "They let me down before, but they've followed through since" when later evidence warrants that change.

This is not forgetting. It is evidence-sensitive reinterpretation of persistent history.

## Epistemic continuity

World facts, subject beliefs, testimony, and first-person evidence remain distinct. Host truth does not automatically become subject knowledge. Testimony can create a belief that is later revised by stronger direct evidence while the original testimony remains remembered as something another person said.

The thirty-day simulation must preserve this distinction across quiet time and restart boundaries.

## Learning and action consequence

Action selection remains prior to expression. Outcomes remain separate from intentions. Learned action utility changes only through experienced outcome evidence. Repeated successful responses to a novel event class should measurably alter later action utility, and ablation of the adaptive component should measurably reduce that learned contribution.

## Persistence and simulated life

Persistent identity, memory, beliefs, commitments, relationships, adaptive state, and current mechanistic state survive process restart. Swatch Internet Time / Beat Time and UTC remain host-provided temporal representations rather than introspection surfaces.

Version 0.7 requires a deterministic thirty-day simulated-life gate with recurring people, promises, disappointment, repair, misinformation, direct evidence, repeated novel encounters, quiet periods, and multiple process restarts.

A passing life simulation demonstrates causal coherence and bounded state under those scenarios. It does not establish phenomenal consciousness, human equivalence, or general psychological validity.

## Evaluation doctrine

The central diagnostic question is: what remains obviously fake when linguistic fluency is not allowed to conceal the architecture?

Unit tests remain necessary, but extended simulations are now first-class architecture tests. Failures discovered only after days or hundreds of cycles are treated as architecture defects when they produce implausible perseveration, saturation, irreversible affect, social monotony, epistemic leakage, or loss of autobiographical continuity.

## Future modalities

Vision, audio, robotics, XR, touch, proprioception, interoception, avatars, and richer embodiment remain future surfaces. Any machine representation entering those systems must cross the same subject-access firewall before it becomes available to the simulated subject.
