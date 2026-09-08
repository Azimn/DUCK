# Psi / MicroPsi Modernization Notes for DUCK v0.10

This document records how DUCK intends to inherit functional ideas from Psi and MicroPsi without treating the historical implementation as an architectural authority. It is supporting design context. `ARCHITECTURE_v0.10.md` and `MILESTONE_0_10.md` are binding for the candidate phase.

## Preserve the functional principle, not the old representation

Psi and MicroPsi are valuable to DUCK primarily because they treat cognition as motivated, situated, affect-modulated, and dynamically associative rather than as a sequence of isolated symbolic queries. Those principles remain useful. The historical node-net representation, old implementation constraints, and exact parameterization do not need to survive.

DUCK already provides several mechanisms that Psi/MicroPsi did not provide in the same modern form: provenance-aware autobiographical memory, explicit world-fact versus subject-belief separation, durable relationship trajectories, commitments, persistent first-person subject authority, action/outcome separation, restart continuity, a strict subject-access firewall, optional LLM rendering, and long-horizon simulation regression. These remain DUCK-native and are not displaced.

## Motivation

The strongest Psi/MicroPsi idea to preserve is that behavior is organized by motivational pressure rather than by a flat action selector.

DUCK currently has needs, prospective concerns, and endogenous goals, but need values still influence action and route utilities fairly directly. v0.10 introduces an intermediate motive layer so a need can produce a persistent motive that competes with other motives and organizes cognition over time.

A motive is not synonymous with a goal. Safety pressure may create a motive to restore safety, but the concrete goal can vary with the situation. Curiosity may sustain a motive to understand something without immediately requiring an action. Affiliation pressure may organize attention toward a particular person, memory, or unresolved commitment before a repair or contact goal is formed.

This separation should produce more realistic persistence, interruption, substitution, conflict, and recovery than mapping need state directly to primitive action utilities.

## Associative activation

MicroPsi's spreading activation is preserved as a general architectural principle: currently relevant material should energize related material, and cognition should emerge partly from the evolving activation field rather than exclusively from explicit top-k retrieval calls.

DUCK should implement this with a typed graph whose nodes reference canonical entities already owned elsewhere. The graph is an index and dynamic activation substrate, not a replacement memory system.

The important modern addition is heterogeneous typing. Memory, people, concepts, beliefs, motives, goals, plans, percepts, actions, outcomes, places, and objects can all participate in one activation field while retaining their own canonical semantics and provenance.

A current cue can therefore activate a person, which activates a prior event, which activates an unresolved commitment, which activates a social motive, which changes retrieval and planning. This is closer to associative cognition than running a single semantic-search query over stored text.

## Emotional and motivational modulation

Psi/MicroPsi treated emotion and motivation as changes to cognitive processing, not only as labels attached to state. DUCK v0.10 should preserve that principle explicitly.

Threat should narrow cognition before action choice. Curiosity should broaden it. Fatigue should reduce planning depth and working capacity. Low competence should increase reliance on familiar successful strategies. Affiliation should increase access to socially linked material. Coherence pressure should increase attention to contradictions and unresolved uncertainty.

This should be implemented as bounded modulation parameters affecting retrieval breadth, graph propagation, planning branching, search depth, novelty tolerance, interruption thresholds, evidence thresholds, and persistence. The exact parameterization is a DUCK implementation choice and should be learned or tuned through simulation rather than copied from historical Psi values.

## Do not recreate the MicroPsi node-net literally

The historical node-net is not required for DUCK's research goal. Recreating it literally would risk duplicating representation already provided by explicit memory records, relationship objects, belief records, commitments, plans, and adaptive state.

A modern graph layer can provide spreading activation and learned association while avoiding a second competing identity or memory ontology.

The graph should store references and associations, not duplicate full canonical subject records.

## Do not let motive activation become introspection

Psi-style numeric activation values are useful mechanistically but violate DUCK's first-person design if they reach private cognition directly.

The subject should experience qualitative consequences of motive and activation dynamics. It can notice that a memory keeps returning, that attention feels narrowed, that a person is on its mind, that it feels pulled toward understanding something, or that fatigue makes a complicated plan feel unmanageable. It cannot inspect a drive value, motive strength, graph activation score, or modulation coefficient.

## Preserve DUCK's epistemic architecture

Spreading activation must never blur memory provenance or belief status.

Association can make a testimony memory salient, but does not turn testimony into observation. Association can make a world fact available to the planner, but does not turn it into autobiographical memory. Association can reactivate a false belief, but does not make the belief true. The existing provenance and belief/world separation remain authoritative.

## Preserve language independence

MicroPsi's useful contribution here aligns with DUCK's existing language-lesion doctrine. Motivation, activation, modulation, retrieval, planning, and action must remain computationally meaningful without verbal thought.

Inner speech can be generated from the resulting first-person state, but it is an expression of cognition rather than the substrate on which cognition depends.

## Development implication

The v0.10 phase should be implemented as one substantial organism-level experiment rather than three unrelated feature modules. The motive system should energize the activation graph. The activation graph should influence retrieval and planning. Global modulation should change how widely activation spreads and how deeply planning searches. Outcomes should then alter needs, learned associations, competence, beliefs, relationships, and future motive dynamics.

The meaningful test is not whether each component works independently. It is whether the same continuing subject behaves differently for intelligible internal reasons across threat, curiosity, fatigue, social pressure, uncertainty, competence changes, failure, recovery, and quiet time while the language layer is disabled.
