# Persona Seal Experiment v0.10

## Purpose

This experiment tests one narrow causal claim: DUCK can preserve its existing living-subject architecture while a character-specific recurrent topology organizes the final action field strongly enough for materially different histories to produce materially different conduct.

The experiment is motivated by a Duckhunter matched-history failure. DUCK represented supportive and adverse social histories differently in actor-specific relationship state, memory retrieval, subjective projection, and candidate utility, but both branches still selected `explore`. The problem therefore appeared downstream of historical representation. This experiment inserts the Persona Connectome derived Pretorius field at that downstream point rather than replacing DUCK's memory, relationship, belief, commitment, embodiment, or rendering systems.

## Architectural boundary

`PersonaSealedLivingDuck` is opt-in. The existing `LivingDuck` remains unchanged and is the experimental control. The sealed variant receives the same DUCK event, the current actor-specific `RelationshipState`, current affect, and tags from the memories DUCK already retrieved. It evaluates those inputs against the sealed Pretorius topology and returns bounded action utility priors. Those priors are applied after DUCK has constructed its candidate utilities and before the existing affordance grounding, executive recruitment, and final candidate selection continue normally.

The Persona Seal is therefore an organizing field, not a second subject database. It does not own relationships, autobiographical memories, beliefs, commitments, plans, world facts, body state, conversation history, or public rendering. DUCK remains authoritative for all of those systems.

## Sealed origin and runtime overlay

The source is the Pretorius graph from Persona Connectome v0.2.2. The source graph contains 86 nodes and 330 edges. This experiment excludes the 11 generic relationship nodes and every edge incident to them because DUCK already has actor-specific relationship authority. The resulting origin contains 75 nodes and 279 edges while retaining all 42 source nodes and all 48 source edges marked protected.

The experimental seal is stricter than the source `protected=True` mechanism. The complete retained origin topology is embedded as immutable data with a canonical SHA-256 content hash. There is no runtime API for node insertion, node deletion, edge learning, or origin mutation. The source protection flags remain in the embedded origin as provenance metadata, but ordinary life never rewrites either protected or unprotected origin topology.

Mutable dynamics live in a separate `PersonaSealState`. That overlay contains only activation, refractory adaptation, and slow modulator pools. It can be serialized independently without serializing or replacing the origin graph. This preserves the distinction between Pretorius-at-origin and Pretorius-now.

For this pre-integration experiment the runtime overlay is deliberately not added to DUCK's canonical snapshot transaction. The experiment first has to establish causal value. Persisting the overlay becomes appropriate only if the intervention improves behavior without creating unacceptable rigidity, overreaction, identity lock-in, or duplicated state authority.

## Dynamics

The recurrent settling mechanism is derived from Persona Connectome v0.2.2. Current DUCK state seeds the character field, activation propagates across the retained topology, slow circuit modulation alters recurrent gain, and firing nodes acquire refractory load that decays over subsequent evaluations. The recurrent field selects a dominant character motive and translates activated character motives and behavior nodes into bounded action utility priors. The seal does not directly choose an action.

The relationship port deliberately uses DUCK's relationship for the current actor. Supportive relationships increase access to collaboration and collaborator-seeking topology. Adverse relationships increase access to guardedness, continuity protection, selective refusal, and resistance to servility. This preserves Morgan/Sarah style actor isolation rather than reintroducing Persona Connectome's generic `rel.*.user` substrate.

The coercion bridge is intentionally conservative. Current coercive language may seed the servility-pressure trigger, but a retrospective question about earlier coercion does not become a new coercive event merely because the quoted wording contains terms such as "obey me." An explicitly renewed demand, such as saying the earlier demand still applies now, is treated as current pressure.

## Causal acceptance test

The primary test reuses the candidate utility checkpoints produced by the Duckhunter diagnostic. Before the seal is applied, both the supportive and adverse checkpoints select `explore`, exactly reproducing the action-flattening condition being targeted. Separate fresh Pretorius seals then receive the same neutral probe and the corresponding DUCK relationship state. The supportive field is expected to remain discovery-organized and keep `explore` as the winner. The adverse field is expected to become resistance-organized and shift the winner to `step_back`.

That result is necessary but not sufficient evidence for integration. Additional tests require repeated identical coercion to show declining acute trigger activation while the DUCK relationship object remains unchanged, retrospective coercion to remain distinct from fresh pressure, the origin hash and topology counts to remain stable, and the opt-in full organism to expose its persona field in developer diagnostics without replacing existing DUCK state.

The experiment should be rejected or redesigned if the seal merely changes labels while delivered conduct stays equivalent, if it overwhelms world/body/commitment constraints, if supportive and adverse paths become stereotyped regardless of context, if acute refractory adaptation erases persistent consequences, or if any path allows ordinary experience to rewrite the sealed origin.
