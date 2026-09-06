# DUCK Integrated Architecture v0.5

Status: binding architecture for the `franken-duck` integration candidate.

DUCK is a functional simulation of a persistent human-like subject. It does not claim phenomenal consciousness. The engineering target is a believable continuing individual whose present cognition depends on its own limited first-person access, lived history, current needs, beliefs, relationships, commitments, predictions, actions, and consequences.

The central rule remains:

> The machinery may know numbers. The subject does not.

The broader rule is now:

> What happens to the subject must be able to change the subject who encounters the next moment.

## Architecture

```text
WORLD / USER / TIME
        |
        v
semantic event
        |
        v
mechanistic subject state
  affect / needs / relationships
  beliefs / world facts / commitments
  autobiographical memory
  path-dependent adaptive state
        |
        v
memory retrieval + appraisal + prediction error
        |
        v
candidate action ecology
        |
        v
selected intention
        |
        +------------------------------+
        |                              |
        v                              v
SUBJECT ACCESS FIREWALL          developer diagnostics
        |                              |
        v                              | raw numeric state
SUBJECTIVE MOMENT                     |
  what I perceive/feel                 |
  what I remember                      |
  what I believe                       |
  what concerns me                     |
  what I want to do                    |
        |                              |
        v                              |
optional private cognition             |
        |                              |
        v                              |
approved language packet <-------------+
        |
        v
expression / action
        |
        v
WORLD OUTCOME
        |
        v
memory + learning + residue
        |
        v
NEXT SUBJECT
```

The arrow from developer diagnostics to the approved language packet above is conceptual separation only: raw diagnostics are explicitly excluded from that packet. The packet is constructed exclusively from the Subjective Moment, selected action, user-visible input, and optional private thought.

## Subject authority

Canonical subject state lives outside the language model. It includes persistent subject identity, affective and homeostatic variables, relationship trajectories, autobiographical records, beliefs, commitments, learned action associations, path-dependent latent state, and pending action/outcome state.

The LLM may contribute semantic interpretation, private first-person cognition, simulation, reflection, and expression through bounded interfaces. It is an organ of cognition and language, not the canonical subject and not the sole decision authority.

## First-person access

Canonical numeric and implementation-specific state is not introspectively readable. `SubjectAccessFirewall` converts mechanistic state into qualitative first-person impressions. Confidence becomes ordinary uncertainty, affect magnitude becomes felt intensity, and relationship state becomes experience such as guardedness or trust.

The same boundary applies to autobiographical retrieval, beliefs, concerns, and temporal carryover. Private cognition receives only `SubjectiveMoment`. A language provider must not receive raw floats, embeddings, scores, memory ranks, database identifiers, latent vectors, or hidden causal annotations.

Inner speech is optional. Behavior and learning must continue when language cognition is disabled.

## Memory and epistemic separation

DUCK separates objective world facts, subject beliefs, testimony, first-person experience, self-reflection, and observed outcomes. A world fact does not automatically become a subject belief merely because the host knows it. A fact becomes subject-accessible only through perception, testimony, inference, or another explicit evidence path.

Autobiographical memory stores provenance and developer-visible scoring metadata. Retrieval ranking remains mechanistic. The subject receives recollection, familiarity, or uncertainty, not retrieval scores.

## Continuity and lived consequence

Recent events can leave decaying mechanistic residue. Commitments can alter later trust, guardedness, affect, and concerns. Retrieved negative history can change appraisal of an otherwise identical present event. Different lived histories therefore may produce different present subjective moments and actions.

Continuity may bias the established action ecology, but no memory or continuity subsystem selects an action directly.

## Motivation and agency

Homeostatic state changes with time. Current implementation tracks energy, affiliation, curiosity, safety, competence, coherence, and autonomy. These variables affect candidate actions. Heartbeat steps allow endogenous pressures to produce action opportunities without a new user message.

A user message is input, not a command to speak. DUCK may respond, ask, wait, step back, explore, rest, repair, approach, or seek connection depending on its current state and available action set.

## Action and outcome

Action selection happens before language realization. Each selected action receives an action ID and becomes a pending prediction. A later outcome can confirm or violate that prediction. Outcome success and valence alter competence, affect, autobiographical memory, and learned action associations.

The language model cannot retroactively change the selected action by wording the response differently.

## Adaptive self-core

The integrated candidate includes a small deterministic path-dependent latent substrate inspired by Gelatinblob. Event history alters an eight-dimensional recurrent trace, and observed outcomes update bounded tag/action associations. This is intentionally inspectable and replayable rather than an opaque neural claim.

The latent substrate is not available to the subject. Its value must be demonstrated through ablation and paired-history tests rather than assumed.

## Time and proactivity

A heartbeat advances homeostasis even without conversation. Endogenous needs can therefore generate action such as rest, exploration, or seeking connection. The current host uses logical ticks rather than wall-clock scheduling. Wall-clock persistence and richer temporal models may be added later without changing subject authority.

## Persistence

The reference host persists canonical subject state to atomic JSON and appends interaction/outcome records to JSONL. Persistence is host authority. The character does not inspect its state file as introspection.

## Language model boundary

`OpenAICompatiblePort` is a generic optional transport. Model-backed private cognition receives only the Subjective Moment. Model-backed expression receives only the approved first-person packet plus the selected action and current user text.

Failure of the language provider must degrade to deterministic cognition or expression without erasing canonical state, action choice, memory, or learning.

## Donor synthesis

The build clean-room synthesizes design lessons rather than importing donor packages as dependencies. Digital Subject contributes causal continuity and paired-history testing. TinyPersonaEngine contributes first-person authority separation. Gelatinblob contributes path dependence, action/outcome separation, and adaptive learning. Wayfarer/Ensemble contributes canonical subject authority, epistemic provenance, commitments, and the principle that the LLM is an organ rather than the organism. Alice, Moemate, and rho inform future presence, interruption, voice, and autonomous-heartbeat surfaces.

## Acceptance standard

The integrated candidate is successful only if automated tests establish all of the following simultaneously: raw numeric state does not reach private cognition; different histories can yield different present experience; world truth does not silently become subject belief; commitments have later causal effects; outcomes alter future adaptive bias; behavior survives a language lesion; endogenous heartbeat can cause unprompted action; persistence preserves the same subject; and model-facing packets contain only approved subject-accessible state.

Human lifelikeness is a later evaluation layer. Passing these tests demonstrates architectural properties, not consciousness or human equivalence.
