# DUCK Architecture v0.10: Motivated Cognitive Architecture

DUCK v0.10 evolves the persistent subject simulator into a modern motivated cognitive architecture that explicitly incorporates the strongest surviving functional ideas from Psi and MicroPsi without recreating their historical node-net implementation.

The architecture remains governed by DUCK's existing subject-authority and first-person access rules. The mechanistic system may use numeric need levels, motive strengths, activation values, graph weights, modulation coefficients, retrieval scores, route utilities, uncertainty values, and latent state internally. The simulated subject never receives those values as introspective content. It receives qualitative first-person consequences such as `I'm exhausted`, `I keep thinking about Morgan`, `Something about this feels dangerous`, `I want to understand what happened`, or `I don't think I can handle something complicated right now`.

> The machinery may know numbers. The subject does not.

> Needs create motives. Motives organize cognition. Cognition recruits plans and actions.

> Internal state changes how cognition operates, not merely which action receives the largest score.

## Architectural goal

The v0.9 organism can form goals from lived experience, maintain unfinished intentions, compare bounded routes, and replan after failure. Its remaining weakness is that motivational state still participates too directly in action and route scoring. Cognition is also dominated by explicit memory retrieval rather than by a broader field of associative activation, and affect mostly changes values rather than changing the operating regime of cognition itself.

v0.10 introduces three interacting mechanisms: a persistent motive system, a general associative activation substrate, and global cognitive modulation.

These mechanisms do not replace persistent identity, autobiographical memory, belief/world separation, relationship trajectories, commitments, prospective concerns, planning, action/outcome learning, the adaptive self-core, the autonomous heartbeat, or the subject-access firewall. They reorganize how those existing mechanisms are recruited.

## Motive system

Needs are no longer treated primarily as direct action-bias terms. Need state generates motive candidates. A motive is a persistent, bounded motivational object representing what the organism is currently pulled toward changing or preserving.

A motive has a source need or composite source, qualitative theme, target condition, persistence, urgency, expected relief, inhibition state, and links to relevant goals, memories, people, concepts, and plans. Numeric motive state is developer-only.

Examples include restoring safety, reducing loneliness, understanding something novel, repairing a valued relationship, preserving coherence, recovering energy, maintaining autonomy, or completing a socially important commitment.

Motive generation is continuous but bounded. A motive can remain latent while another motive dominates. Selection does not delete nonselected motives. Motives decay, recover, become inhibited, gain urgency, conflict, merge when they represent the same concern, and terminate when the relevant need or target condition changes sufficiently.

The selected motive becomes an organizing context for cognition. It does not directly choose `ask`, `explore`, `repair`, or another primitive action. Instead it changes associative activation, retrieval, planning priority, planning depth, opportunity recognition, and action affordance evaluation. The resulting plan or immediate affordance can then produce action.

The causal sequence is therefore:

```text
need state + lived context
        |
        v
motive generation / persistence
        |
        v
motive competition
        |
        v
selected organizing motive
        |
        +-------------------------+
        |                         |
        v                         v
associative activation      cognitive modulation
        |                         |
        +------------+------------+
                     |
                     v
              retrieval / planning
                     |
                     v
               intention / action
                     |
                     v
                   outcome
                     |
                     v
             changed need + motive
```

A motive can recruit an existing v0.9 goal, create a new bounded goal when experience and context justify one, resume a suspended prospective concern, or support a direct affordance when no multi-step plan is necessary.

## Associative activation substrate

DUCK v0.10 adds a general graph-based activation layer inspired by Psi/MicroPsi spreading activation but implemented as a modern typed associative graph rather than a literal historical node-net.

The graph is not a second memory authority. Canonical memory, beliefs, people, commitments, goals, plans, actions, concepts, and motives continue to live in their existing domain stores. The activation graph contains typed references to those canonical entities plus learned association edges between them.

Graph nodes may refer to autobiographical memories, semantic concepts, people, relationships, perceptual entities, beliefs, goals, plans, prospective concerns, actions, outcomes, motives, places, objects, and self-relevant themes. Edges may represent temporal adjacency, semantic similarity, co-occurrence, causal association, social association, goal relevance, action-outcome association, affective association, and learned contextual linkage.

Activation enters the graph from the current perceptual context, selected motive, current affective state, active goals, recent memories, relevant people, current body/interoceptive state, and current situational tags. It propagates for a bounded number of steps with decay. Edge weights may be updated by repeated co-activation and by outcome learning.

The graph returns an activation field, not a sentence. High-activation canonical entities become candidates for retrieval, attention, planning, recognition, and qualitative first-person projection. Numeric activation values remain mechanistic.

This permits cognitive behavior that explicit top-k retrieval alone does not provide. A present person can activate a prior event, which activates a place, which activates a commitment, which activates an unresolved concern. A threat-associated percept can activate earlier danger memories and defensive affordances. Curiosity can spread activation more broadly through weak semantic links. A socially important motive can preferentially energize memories and goals associated with a particular person.

Associative activation must remain bounded. Propagation depth, fan-out, total active mass, edge growth, and persistent graph size require explicit limits. Quiet time must not cause perpetual uncontrolled activation.

## Global cognitive modulation

DUCK v0.10 introduces a global modulation state that changes how cognitive mechanisms operate as a function of the organism's current motivational, affective, energetic, and competence state.

This is not an additional emotion label. It is an operating-regime controller.

The modulation layer derives bounded control parameters for associative breadth, retrieval breadth, novelty preference, planning depth, plan branching, action conservatism, persistence, interruption sensitivity, evidence threshold, and familiar-strategy bias.

High threat should narrow associative spread, reduce exploratory branching, increase interruption sensitivity, favor high-confidence familiar strategies, and raise the evidence threshold for risky novelty. High curiosity should broaden activation, increase weak-association exploration, allow more route alternatives, and increase novelty preference when safety permits. Low competence should increase reliance on previously successful or familiar strategies and reduce speculative branching. Fatigue should reduce planning depth and working-set size, increase the probability of rest or deferral, and make complex multi-step routes less attractive. Strong affiliation pressure should preferentially activate people, social memories, commitments, and repair opportunities. High coherence pressure should favor interpretations and actions that resolve contradiction or uncertainty.

Modulation changes computation before final action choice. A threat state should therefore cause fewer memories to be actively considered, shallower route search, and narrower associative spread, not merely add `+0.4` to `step_back`. Curiosity should expose more potentially relevant associations and plans, not merely add utility to `explore`.

The modulation state is recomputed as the organism changes. It can vary within a plan. A plan formed while calm can become shallower or be deferred if fatigue rises. A previously narrow threat regime can broaden again after safety recovers.

## Interaction with v0.9 planning

The v0.9 planner remains the executive planning substrate for this phase, but its route selection becomes downstream of motive and modulation state.

A selected motive can recruit a goal root. Associative activation supplies contextually energized memories, concepts, people, actions, and prior outcomes. Cognitive modulation determines how broadly and deeply the planner searches. The planner then evaluates candidate routes using these inputs plus its existing explicit world/belief state.

This architecture preserves the distinction between motive and goal. A motive such as `restore safety` may recruit many different goals depending on context. A goal such as `find another way through the gate` is a concrete objective formed in service of the motive. A plan is a route toward that goal. An intention is the currently activated step. An action is the outward attempt. An outcome changes the subject and therefore changes future motive dynamics.

## Interaction with memory and belief

Explicit autobiographical memory remains canonical. Associative activation does not fabricate memories and cannot satisfy autobiographical recall with world facts or beliefs.

The existing provenance rules remain binding. A highly activated world fact is still not a first-person memory. A highly activated testimony memory remains testimony. A highly activated false belief remains a belief until evidence changes it.

Associative activation changes which canonical entities become cognitively available or salient, not what their epistemic status is.

## Interaction with relationships

People and relationship trajectories become first-class activation anchors. A person can activate prior experiences, commitments, unresolved concerns, social motives, and learned expectations associated with that person.

Relationship state can influence motive formation. Low trust may generate caution, attachment plus conflict may generate repair pressure, and loneliness may increase affiliation motives. These remain mechanistic causes. First-person cognition receives only qualitative projections.

## Interaction with the subject-access firewall

The first-person access firewall remains a hard architectural boundary.

The following are developer-only and must never be handed directly to private cognition or expression: need magnitudes, motive strengths, inhibition values, activation weights, graph node IDs, graph edge weights, propagation depth, modulation coefficients, retrieval scores, route scores, plan IDs, concern IDs, trust floats, affect magnitudes, latent vectors, and raw confidence telemetry.

First-person projection may expose qualitative consequences such as motive content, felt urgency, accessible uncertainty, attentional narrowing, fatigue, remembered associations, or a sense that something keeps coming back to mind.

A subject may think `I can't stop thinking about what Morgan promised` but may not think `Morgan node activation is 0.82`.

## Language lesion requirement

The motive system, associative activation substrate, cognitive modulation, retrieval changes, planning-depth changes, goal recruitment, action selection, learning, persistence, and restart continuity must operate with inner language disabled and without any LLM service.

The LLM may later render approved qualitative state into first-person inner speech or outward language. It is not the source of motive persistence, graph activation, modulation, goal authority, or plan state.

## Longitudinal requirement

The architecture must be tested as an interacting organism rather than as isolated unit features.

A long-horizon simulation should force motives to compete, become satisfied, reappear, lose salience, recruit different goals, and interact with fatigue, threat, curiosity, competence, relationships, commitments, misinformation, planning failure, and quiet time.

The same external event should produce measurably different internal computational regimes under different subject states while remaining causally interpretable through developer diagnostics.

## Compatibility doctrine

v0.10 preserves v0.9 and earlier architecture as regression history. It does not remove the autonomous heartbeat, persistent subject identity, autobiographical continuity, world/belief separation, commitments, relationship development, first-person reinterpretation, prospective agency, goal formation, counterfactual planning, outcome learning, or simulation harnesses.

Historical Psi/MicroPsi mechanisms are donors, not authorities. DUCK adopts functional principles when they survive modern architectural scrutiny and fit the subject model. It does not adopt historical implementation details merely for fidelity to the donor architecture.

The v0.10 research target is therefore not `MicroPsi rewritten in Python`. It is DUCK as a modern motivated cognitive architecture with persistent motives, associative activation, and state-dependent cognitive operating regimes integrated into the existing persistent artificial individual.
