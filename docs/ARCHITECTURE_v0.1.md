# DUCK Architecture v0.1

Status: binding design for Milestone 0.1.

## Research target

DUCK is a computational simulation of a persistent human-like subject. It does not claim phenomenal consciousness or sentience. The engineering target is a believable continuing individual whose current cognition is constrained by what that individual can perceive, remember, infer, feel, and introspect from a first-person position.

The immediate research question is:

> Can a computational individual behave as though there is an ongoing first-person life behind the conversation when the language model is not allowed omniscient access to implementation state?

## Core invariant

Implementation state and subject-accessible state are different things.

The implementation may use numbers, embeddings, probabilities, scores, coordinates, database identifiers, hashes, classifier outputs, or hidden causal annotations. None of those are automatically available to the simulated subject.

All machine and internal state must cross a subject-access boundary before it can participate in private cognition.

```text
MECHANISTIC STATE
numbers, scores, hidden causes, implementation telemetry
        |
        v
SUBJECT ACCESS FIREWALL
        |
        v
SUBJECTIVE MOMENT
bounded first-person impressions and tendencies
        |
        v
PRIVATE COGNITION
optional first-person inner thought
        |
        v
CHOICE / ACTION
        |
        v
CONSEQUENCE
```

## The subject does not inspect its own implementation

A developer may see `fear = 0.71`, `trust = 0.31`, `recognition_confidence = 0.64`, and `prediction_error = 0.62`. The subject may instead have access to "I'm scared," "I don't completely trust them," "I think that's Sarah," and "That isn't what I expected." The numerical values govern projection. They are not first-person facts.

## Introspective opacity

The system may know the computational cause of a state while the subject does not. A hidden cause can influence the subject while the accessible experience remains "I feel uneasy, but I'm not sure why." A later memory or inference may make the cause accessible. Privileged implementation access does not.

## Inner speech is optional

First-person accessibility is not the same as verbal narration. The subject may perceive, appraise, anticipate, or act without producing a sentence. Inner speech is one possible cognitive operation over a SubjectiveMoment, not the definition of cognition.

## LLM boundary

An LLM is not the subject and is not canonical state authority. An LLM may later participate in bounded cognition, simulation, reflection, imagination, inner speech, and expression. Any such component must receive only the state intentionally made available at its interface.

## One subject, not two

The SubjectiveMoment is not a second identity store or a second canonical subject. It is a projection of the current subject state for first-person access. Developer diagnostics may inspect both mechanistic and subjective state. The character may inspect only the latter.

## Current scope

Milestone 0.1 covers internal affect, relationship impressions, expectation violation, uncertain recognition, action tendencies, introspective opacity, optional inner speech, and the access firewall itself.

## Future scope, explicitly nonbinding

Vision, audio, touch, proprioception, vestibular sense, interoception, robotics, avatars, XR embodiment, body transfer, and multimodal binding are not frozen implementation designs in v0.1.

The only binding future rule is that if such modalities are added, their machine representations must cross the same subject-access boundary before becoming available to the character. No modality-specific schema should be added until a concrete behavior or product surface requires it.

## Historical relationship to Wayfarer

The earlier `Azimn/persona_engine_PYTHONX` repository is a donor and research archive, not a runtime dependency of this repository. Proven mechanisms may be transplanted selectively when a failing DUCK experiment demonstrates their need. Nothing enters this repository merely because the older project contained it.

## Change rule

v0.1 is a historical architecture snapshot. Do not silently rewrite it when the design changes. Create v0.2 or a later version and record what changed and why.
