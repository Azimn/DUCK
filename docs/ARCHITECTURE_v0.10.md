# MicroPsiDUCK Architecture v0.10: Motivated Cognitive Organism

MicroPsiDUCK v0.10 is a structural redesign of DUCK around motivated cognition, continuous organism dynamics, associative activation, global cognitive modulation, selective executive recruitment, and a strict experiential firewall.

Version 0.9 remains preserved on `main` as the previous promoted DUCK baseline. The v0.10 development branch may change public classes, file layout, control flow, persistence boundaries, planning interfaces, and renderer contracts when a cleaner structure better serves the new architecture.

The historical system is a donor and regression reference, not an implementation constraint.

The central doctrine is:

> Needs create motives. Motives organize cognition. Internal condition changes the kind of cognition performed. Cognition recruits goals, plans, intentions, and actions.

A second doctrine governs continuity:

> The continuously existing simulated individual lives in persistent system state, not inside a language model invocation.

A third doctrine governs first-person access:

> The machinery may contain numbers, tags, IDs, graphs, and scores. The subject receives only the experiential consequences of that machinery.

A fourth doctrine governs external reasoning services:

> A recruited model may propose. The organism remains the authority that validates, acts, persists, and learns.

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
AUTOMATIC POLICY   EXECUTIVE RECRUITMENT
       |             |
       |             v
       |       EXPERIENTIAL FIREWALL
       |             |
       |             v
       |       EXECUTIVE PROPOSAL
       |             |
       +-------> VALIDATION
                    |
                    v
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
                    +-----> continuous state dynamics
```

Utility calculations may exist at local arbitration points, especially for immediate affordances, but utility is not the executive architecture. The dominant motive determines why cognition is being organized. Modulation determines how cognition operates. Associative activation helps determine what becomes cognitively available. Automatic policy, validated executive proposals, and planning determine what the organism attempts.

## Continuous organism dynamics

MicroPsiDUCK does not attempt to keep an LLM continuously active. The continuously running component is the organism substrate.

Time passes. Energy changes. Affiliation pressure can rise. Commitments approach deadlines. Residues decay. Expectations may fail. Environmental conditions change. Other actors may enter or leave. Goals remain unfinished. Motives can gain or lose urgency. None of these require a language model call.

The continuous substrate therefore acts as an endogenous event generator. Candidate events are produced by changes in body state, world state, social context, commitments, goals, predictions, and learned expectations.

Most candidate events do not recruit executive cognition. Some die below salience threshold. Some are handled by automatic policy or immediate affordance selection. Only situations requiring richer integration, planning, reflection, unusual association, or language should recruit an executive provider.

Continuity belongs to persistent state and causal dynamics, not to inference uptime.

## Need and motive architecture

Needs are regulated internal variables. They are not goals and they do not directly select primitive actions.

Need state and appraisal generate motive candidates. A motive is a persistent pressure to change or preserve a condition. Examples include restoring safety, recovering energy, reducing isolation, understanding something novel, repairing a valued relationship, preserving coherence, completing an important commitment, or maintaining autonomy.

A motive may contain developer-only numeric fields for strength, urgency, inhibition, persistence, competition, and learned history. Those fields are mechanistic and inaccessible to the simulated subject.

Motive selection supports a bounded active set rather than deleting all competitors when one motive wins. The system distinguishes:

```text
primary organizing motive
active supporting or conflicting motives
inhibited motives
latent motives
resolved motives
```

The primary motive organizes current cognition. Other active motives can constrain what counts as an acceptable solution. A restoration motive may dominate while an affiliation motive still prevents a socially damaging strategy.

Motives can persist through quiet time, become inhibited, recover when suppression ends, merge when they represent the same concern, recruit goals, lose dominance after satisfaction, or terminate when their target condition no longer applies.

Canonical motive identity should be stable. Recurrent pressure should normally reactivate an existing `(theme, target)` motive rather than creating unlimited equivalent records.

Coherence is not merely a low stored need. Contradiction, inconsistency, expectation violation, or prediction error may create coherence pressure through appraisal when lived evidence stops fitting the subject's current expectations.

## Global cognitive modulation

MicroPsiDUCK preserves the functional idea that internal condition alters the operating regime of cognition.

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

MicroPsiDUCK has a bounded typed associative graph. The graph is an overlay, not a second database and not a second subject authority.

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

The important behavioral contribution is indirect retrieval. A present cue may activate a person, which activates a concept or place, which activates an old experience, which activates an unfinished motive. The final memory may have little lexical overlap with the current percept.

That bridge case is a required architectural test because it distinguishes associative cognition from another top-k scoring layer.

The associative graph changes availability, not epistemic status. Activating a world fact does not make it a memory. Testimony remains testimony. A belief remains a belief until evidence changes it.

## Cognitive field

The output of motive competition, associative activation, current context, active goals, modulation, and candidate affordances is a bounded transient cognitive field.

`CognitiveField` is mechanistic. It may contain raw candidate utilities, event tags, motive IDs, activated memory IDs, modulation parameters, and other developer-visible machinery. It is not an introspective object and it is not an executive-provider input.

The field determines what is salient enough to influence immediate policy, memory availability, planning, opportunity recognition, or executive recruitment. It should be reconstructed from current canonical state rather than persisted as a second continuing self.

## Automatic policy and executive recruitment

Automatic policy is a first-class path, not a degraded fallback. Routine endogenous cycles, familiar immediate affordances, and urgent protective reactions should be executable without a language model or other expensive executive service.

Executive cognition is optional and selectively recruited. Recruitment can be justified by novelty, unresolved contradiction, obstacles, repair conflict, close competition among plausible affordances, competing motives, or planning demands. Quiet routine state must not continuously call an executive provider.

Severe safety pressure may bypass deliberative executive recruitment when current automatic policy already specifies a protective response. This preserves fast behavior and prevents curiosity or model verbosity from overriding acute safety organization.

The executive interface is:

```text
MECHANISTIC COGNITIVE FIELD
scores, IDs, tags, activations, modulation
        |
        |  influences translation and recruitment
        v
EXPERIENTIAL FIREWALL
        |
        v
EXPERIENTIAL FRAME
first-person prose only
        |
        v
ExecutiveCognitionProvider
        |
        v
ExecutiveProposal
bounded suggestion only
        |
        v
ORGANISM VALIDATION
        |
        +---- reject / fall back to automatic policy
        |
        +---- accept as current action or later validated goal/plan proposal
```

The provider never receives the raw cognitive field. It cannot inspect motive strengths, candidate utilities, graph activations, route scores, modulation coefficients, IDs, or persistence metadata.

A proposed action must correspond to an affordance currently available to the organism. Invalid, unavailable, malformed, failed, or absent proposals are rejected without corrupting state, and the automatic policy remains available.

Provider output is not canonical authority. Executive intention prose does not automatically become autobiographical memory, self-narrative, belief, motive, goal, plan, commitment, or identity. If future versions permit richer goal or plan proposals, the organism must validate and explicitly adopt them through canonical state transitions.

Provider configuration is runtime/host configuration rather than persistent cognitive identity. Restarting the organism without supplying a provider restores the subject and its cognitive state without silently restoring the provider or the previous transient cognitive field.

## Private inner cognition is a separate contract

Private inner cognition and executive proposal are different functions even when both happen to be implemented by language models.

`InnerCognitionProvider` receives experiential state and may generate private first-person thought. Its output can become controlled private interior context, subject to the experiential validator and private-interior persistence rules.

`ExecutiveCognitionProvider` is recruited selectively before final action selection and returns a bounded proposal. It is not the same interface as inner voice, and an executive proposal does not become private thought merely because both are language-like.

This separation allows experiments in which inner language is absent while motivated cognition, automatic policy, associative retrieval, modulation, planning, and action continue to function.

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

MicroPsiDUCK has one authoritative continuing subject.

Autobiographical memory, beliefs, relationships, commitments, motives, goals, plans, learned associations, adaptive state, and private interior persistence must have explicit ownership. Overlay systems and recruited providers may reference or influence these stores but may not create competing canonical copies.

World truth and subject belief remain distinct. Memory provenance remains distinct. The associative graph changes availability, not truth status. A renderer or executive provider cannot directly rewrite identity or autobiographical history.

## Experiential firewall

The experiential firewall is the technical boundary between mechanistic state and first-person access.

The substrate may contain numeric need levels, motive strengths, inhibition values, activation values, graph weights, propagation depth, modulation coefficients, retrieval scores, action utilities, route scores, plan indexes, confidence values, trust values, affect magnitudes, latent vectors, tags, and identifiers.

None of those representations may cross into private cognition or executive-provider input.

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
        +------------------------+
        |                        |
        v                        v
PRIVATE INNER COGNITION    OPTIONAL EXECUTIVE
        |                        |
        v                        v
PRIVATE INTERIOR RECORD    VALIDATED PROPOSAL
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
I keep coming back to what Morgan promised.
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

The translator must reject disguised telemetry rather than merely removing float-typed fields. If current-world text itself resembles implementation telemetry, the experiential projection must avoid blindly copying that machinery into the private interface and should fall back to an appropriate qualitative first-person description when possible.

## Private interior persistence

Private interior state is versioned and persistent.

A durable private-interior record contains approved experiential prose and optional private inner speech. Host-side schema metadata may be stored for migration and validation, but schema metadata does not enter the character's experiential frame.

Unsupported private-interior schema versions must fail explicitly.

Persistence of private interior does not make the persisted file introspectively accessible. The subject experiences the restored interior, not the serialization mechanism.

Transient cognitive fields and executive-provider objects are not private interior and are not persisted as subject identity.

## Renderer boundary

Public expression is produced through a renderer that receives only controlled prose derived from accessible private state plus public conversational context.

Machine action identifiers are translated into first-person action intent before entering the renderer packet.

The renderer may use private thought as context for expression, but public interaction results and ordinary event journals do not publish private thought or private experiential state.

The renderer cannot directly modify canonical subject state.

## Language lesion

Motive generation, motive competition, associative graph propagation, modulation, cognitive-field construction, retrieval, planning, automatic policy, action selection, learning, persistence, and experiential projection must function with inner language disabled and without an LLM service.

A language-dependent executive provider must be removable without disabling the organism. The current lesion condition may disable both optional executive calls and inner voice while leaving the full substrate control spine operational.

The language model is a recruited cognitive or expressive organ. It is not where the simulated individual resides.

## Longitudinal requirement

The architecture must be evaluated as an interacting organism across time.

A long-horizon simulation must force safety, curiosity, energy, affiliation, competence, coherence, autonomy, repair, and commitment pressures to compete across changing histories. Motives should rise, remain latent, become inhibited, return, recruit plans, resolve through simple affordances, fail, become impossible, or disappear after satisfaction.

The same external situation should produce different measurable cognitive regimes under different internal histories and conditions while developer diagnostics remain causally interpretable.

Quiet time must remain bounded. Persistent motives must not become unbounded motive records, learned associations must not grow without limits, and optional executive cognition must not be continuously recruited simply because a provider is available.

## Compatibility and naming doctrine

The v0.10 branch is MicroPsiDUCK, not a compatibility-preserving patch to the v0.9 public runtime.

Version 0.9 remains available on `main` and in explicit historical modules for comparison. v0.10 may refactor or replace earlier implementation details when doing so improves the architecture.

Historical Psi and MicroPsi systems are functional donors, not authorities. MicroPsiDUCK preserves useful principles such as motivated autonomous behavior, spreading activation, and global modulation without recreating the historical implementation.

The research target is therefore not `MicroPsi rewritten in Python`, and it is not `DUCK v0.9 with extra modules`. It is a motivated cognitive organism that preserves the strongest DUCK subject-continuity ideas while reorganizing the control structure around motivation, associative cognition, modulation, continuous state evolution, selective executive recruitment, and bounded first-person access.