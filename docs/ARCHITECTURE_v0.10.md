# MicroPsiDUCK Architecture v0.10: Motivated Cognitive Organism

MicroPsiDUCK v0.10 is a structural redesign of DUCK around motivated cognition, continuous organism dynamics, associative activation, global cognitive modulation, and a strict experiential firewall.

Version 0.9 remains preserved on `main` as the previous promoted DUCK baseline. The v0.10 development branch is allowed to change public classes, file layout, control flow, persistence boundaries, planning interfaces, and renderer contracts when a cleaner structure better serves the new architecture.

The historical system is therefore a donor and regression reference, not an implementation constraint.

The central doctrine is:

> Needs create motives. Motives organize cognition. Internal condition changes the kind of cognition performed. Cognition recruits goals, plans, intentions, and actions.

A second doctrine governs continuity:

> The continuously existing simulated individual lives in persistent system state, not inside a language model invocation.

A third doctrine governs first-person access:

> The machinery may contain numbers, tags, IDs, graphs, and scores. The subject receives only the experiential consequences of that machinery.

## Control spine

The v0.10 control hierarchy is:

```text
WORLD / BODY / SOCIAL CONTEXT
            |
            v
CONTINUOUS STATE DYNAMICS
            |
            v
APPRAISAL + NEED CHANGE
            |
            v
         MOTIVES
            |
            v
    MOTIVE COMPETITION
            |
            v
SELECTED ORGANIZING MOTIVE
        /           \
       v             v
ASSOCIATIVE       GLOBAL
ACTIVATION       MODULATION
       \             /
        v           v
       COGNITIVE FIELD
             |
             v
 ATTENTION / OPPORTUNITY
        /           \
       v             v
AUTOMATIC POLICY   EXECUTIVE COGNITION
       |             |
       v             v
 AFFORDANCE       GOAL / PLAN
       \             /
        v           v
         INTENTION
             |
             v
           ACTION
             |
             v
          OUTCOME
             |
             v
 LEARNING + CHANGED SUBJECT
             |
             +------> continuous state dynamics
```

Utility calculations may still exist at local arbitration points, especially for immediate affordances, but utility is not the executive architecture. The dominant motive determines why cognition is being organized. Modulation determines how cognition operates. Associative activation helps determine what becomes cognitively available. Planning and affordance arbitration determine what the organism attempts.

## Continuous organism dynamics

MicroPsiDUCK does not attempt to keep an LLM continuously active. The continuously running component is the organism substrate.

Time passes. Energy changes. Affiliation pressure can rise. Commitments approach deadlines. Residues decay. Expectations may fail. Environmental conditions change. Other actors may enter or leave. Goals remain unfinished. Motives can gain or lose urgency. None of these require a language model call.

The continuous substrate therefore acts as an endogenous event generator. Candidate events are produced by changes in body state, world state, social context, commitments, goals, predictions, and learned expectations.

Most candidate events do not recruit executive cognition. Some die below salience threshold. Some are handled by automatic policy or immediate affordance selection. Only situations requiring richer integration, planning, reflection, unusual association, or language should recruit an executive cognition provider.

Continuity belongs to persistent state and causal dynamics, not to inference uptime.

## Need and motive architecture

Needs are regulated internal variables. They are not goals and they do not directly select primitive actions.

Need state generates motive candidates. A motive is a persistent pressure to change or preserve a condition. Examples include restoring safety, recovering energy, reducing isolation, understanding something novel, repairing a valued relationship, preserving coherence, completing an important commitment, or maintaining autonomy.

A motive may contain developer-only numeric fields for strength, urgency, expected relief, inhibition, persistence, and competition. Those fields are mechanistic and inaccessible to the simulated subject.

Motive selection should support a bounded active motive set rather than deleting all competitors when one motive wins. The system distinguishes:

```text
primary organizing motive
active supporting or conflicting motives
inhibited motives
latent motives
resolved motives
```

The primary motive organizes current cognition. Other active motives can constrain what counts as an acceptable solution. A restoration motive may dominate while an affiliation motive still prevents a socially damaging strategy.

Motives can persist through quiet time, become inhibited, recover when suppression ends, merge when they represent the same concern, recruit goals, lose dominance after satisfaction, or terminate when their target condition no longer applies.

## Global cognitive modulation

MicroPsiDUCK inherits the functional idea that internal condition alters the operating regime of cognition.

The modernized global control state includes at minimum:

```text
cognitive mobilization
cognitive resolution
switching threshold / cognitive commitment
competitor inhibition
associative exploration
```

These controls affect computation upstream of final action selection.

High threat can increase mobilization, narrow associative breadth, reduce planning depth, increase interruption sensitivity, favor familiar strategies, strengthen commitment to the dominant safety motive, and suppress weak exploratory motives.

Calm curiosity can permit higher resolution, broader associative spread, deeper route search, weaker competitor suppression, and exploration of lower-strength associations.

Fatigue can reduce working-set size, planning depth, representational detail, and tolerance for expensive multi-step strategies.

Low competence can bias cognition toward previously successful or well-understood strategies without merely adding a constant to one action score.

The same person in the same external situation should therefore exhibit different cognitive structure under different internal conditions without requiring multiple personality definitions.

## Associative activation substrate

MicroPsiDUCK adds a bounded typed associative graph. The graph is an overlay, not a second database and not a second subject authority.

Canonical entities remain in their authoritative stores. The graph holds typed references to those entities and learned association edges between them.

Nodes may reference autobiographical memories, concepts, people, relationships, perceptual entities, beliefs, goals, plans, concerns, actions, outcomes, motives, places, objects, commitments, and self-relevant themes.

Edges may represent temporal adjacency, semantic relationship, co-occurrence, social relationship, causal association, goal relevance, action-outcome association, affective linkage, repeated co-activation, and learned contextual association.

A simplified mechanistic update can resemble:

```text
next_activation
    = current_activation * decay
    + contextual_input
    + sum(edge_weight * source_activation)
```

Propagation depth, fan-out, retained edges, total activation mass, and graph growth must remain bounded.

The important behavioral contribution is indirect retrieval. A present cue may activate a person, which activates a place, which activates an old experience, which activates an unfinished motive. The final memory may have little lexical overlap with the current percept.

That bridge case is a required architectural test because it distinguishes associative cognition from another top-k scoring layer.

## Cognitive field and executive recruitment

The output of motive competition, associative activation, current context, active goals, and modulation is a bounded cognitive field.

The field determines what is salient enough to influence immediate policy, memory availability, planning, opportunity recognition, or executive recruitment.

An executive cognition provider is optional and replaceable. It may be a deterministic rule system, a small local model, a frontier language model, or another reasoning engine.

The provider is not the subject.

The intended interface is:

```text
MicroPsiDUCK organism
        |
        v
ExperientialFrame / approved cognitive situation
        |
        v
ExecutiveCognitionProvider
        |
        v
proposal or private thought
        |
        v
MicroPsiDUCK validation and subject authority
```

The provider cannot become canonical authority for identity, memories, beliefs, relationships, motives, goals, plans, commitments, or outcomes.

## Planning

Version 0.9 planning may be reused where useful, but it is no longer architecturally privileged.

A motive can recruit an existing goal, create a bounded goal when conditions justify one, resume a suspended concern, or support a direct affordance when no multi-step plan is required.

The architecture preserves the distinctions:

```text
NEED
internal regulated condition

MOTIVE
pressure to alter or preserve a condition

GOAL
concrete objective recruited in service of a motive

PLAN
route toward the goal

INTENTION
currently active step

ACTION
outward attempt

OUTCOME
consequence that changes the continuing subject
```

Planning depth and branching are controlled by modulation. Associative activation supplies contextually energized memories, concepts, people, and prior outcomes. Motive state supplies organizing purpose. Local utilities may still arbitrate among immediate affordances or candidate routes.

## Canonical subject authority

MicroPsiDUCK must continue to have one authoritative continuing subject.

Autobiographical memory, beliefs, relationships, commitments, motives, goals, plans, learned associations, adaptive state, and private interior persistence must have explicit ownership. Overlay systems may reference these stores but may not create competing canonical copies.

World truth and subject belief remain distinct. Memory provenance remains distinct. An activated world fact does not become a memory merely because it is salient. A testimony memory remains testimony. A false belief remains a belief until evidence changes it.

The associative graph changes availability, not epistemic status.

## Experiential firewall

The experiential firewall is the technical boundary between mechanistic state and first-person access.

The substrate may contain numeric need levels, motive strengths, inhibition values, activation values, graph weights, propagation depth, modulation coefficients, retrieval scores, route scores, plan indexes, confidence values, trust values, affect magnitudes, latent vectors, tags, and identifiers.

None of those representations may cross into private cognition.

The boundary path is:

```text
MECHANISTIC STATE
numbers, tags, IDs, scores, graph state
        |
        v
STRUCTURED INTERNAL PROJECTION
internal diagnostic representation
        |
        v
EXPERIENTIAL FIREWALL
translation + validation
        |
        v
EXPERIENTIAL FRAME
immutable first-person experiential prose only
        |
        +-------------------+
        |                   |
        v                   v
PRIVATE COGNITION    PRIVATE INTERIOR RECORD
        |                   |
        +---------+---------+
                  |
                  v
             RENDERER VIEW
                  |
                  v
             PUBLIC OUTPUT
```

`ExperientialFrame` is the introspective API. Structured diagnostics such as `SubjectiveMoment` may exist internally during development, but they are not private cognition input.

The subject may experience:

```text
I'm exhausted.
I really need somewhere quiet.
That flower just came back to mind.
I feel uneasy, but I'm not sure why.
I don't feel safe enough to think about this right now.
```

The subject may not receive:

```text
energy = 0.19
motive_strength = 0.83
flower.activation = 0.47
planning_depth = 2
trust = 0.61
```

The translator must reject disguised telemetry rather than merely removing float-typed fields.

## Private interior persistence

Private interior state is versioned and persistent.

A durable private-interior record contains approved experiential prose and optional private inner speech. Host-side schema metadata may be stored for migration and validation, but schema metadata does not enter the character's experiential frame.

Unsupported private-interior schema versions must fail explicitly.

Persistence of private interior does not make the persisted file introspectively accessible. The subject experiences the restored interior, not the serialization mechanism.

## Renderer boundary

Public expression is produced through a renderer that receives only controlled prose derived from accessible private state plus public conversational context.

Machine action identifiers are translated into first-person action intent before entering the renderer packet.

The renderer may use private thought as context for expression, but public interaction results and ordinary event journals do not publish private thought or private experiential state.

The renderer cannot directly modify canonical subject state.

## Language lesion

The motive system, associative graph, modulation, cognitive field, retrieval, planning, automatic policy, action selection, learning, persistence, and experiential projection must function with inner language disabled and without an LLM service.

The language model is a recruited cognitive or expressive organ. It is not where the simulated individual resides.

## Longitudinal requirement

The architecture must be evaluated as an interacting organism across time.

A long-horizon simulation must force safety, curiosity, energy, affiliation, competence, coherence, and autonomy pressures to compete across changing histories. Motives should rise, remain latent, become inhibited, return, recruit plans, resolve through simple affordances, fail, become impossible, or disappear after satisfaction.

The same external situation should produce different measurable cognitive regimes under different internal histories and conditions while developer diagnostics remain causally interpretable.

## Compatibility and naming doctrine

The v0.10 branch is MicroPsiDUCK, not a compatibility-preserving patch to the v0.9 public runtime.

Version 0.9 remains available on `main` and in explicit historical modules for comparison. v0.10 may refactor or replace earlier implementation details when doing so improves the architecture.

Historical Psi and MicroPsi systems are functional donors, not authorities. MicroPsiDUCK preserves useful principles such as motivated autonomous behavior, spreading activation, and global modulation without recreating the historical implementation.

The research target is therefore not `MicroPsi rewritten in Python`, and it is not `DUCK v0.9 with three extra modules`. It is a new motivated cognitive organism that preserves the strongest DUCK subject-continuity ideas while reorganizing the control structure around motivation, associative cognition, modulation, continuous state evolution, and bounded first-person access.
