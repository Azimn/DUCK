# MicroPsiDUCK v0.10 Current Status

Current architecture candidate: `docs/ARCHITECTURE_v0.10.md`

Current milestone candidate: `docs/MILESTONE_0_10.md`

Experiential boundary contract: `docs/EXPERIENTIAL_FIREWALL_v0.10.md`

Prediction contract: `docs/EXPECTATIONS_v0.10.md`

Causal prediction contract: `docs/CAUSAL_PREDICTION_v0.10.md`

Development branch: `motivated-cognition-v0.10`

Preserved promoted baseline: DUCK v0.9 on `main`

## Current implementation

MicroPsiDUCK v0.10 is a structural redesign rather than a compatibility-preserving patch to DUCK v0.9. The public package on this branch points to the composed v0.10 predictive organism and current persistent host. DUCK v0.9 remains preserved on `main` and remains explicitly importable as a historical comparison point.

The implemented v0.10 control spine now includes persistent motives, bounded motive competition, typed associative activation, global cognitive modulation, a transient cognitive field, automatic affordance policy, selective executive recruitment, validated action selection, bounded planning, sparse endogenous dynamics, subject-owned world expectations, exact-action outcome expectations, learned prediction calibration, sequence-conditioned causal calibration, host-owned external world scheduling, outcome learning, restart persistence, and the experiential firewall.

No donor package is a runtime dependency.

## Persistent motivated cognition

Needs, affect, commitments, relationship conditions, threat, obstacles, novelty, and coherence disruption can generate persistent motives. Implemented motive families include safety, energy, affiliation, curiosity, competence, coherence, autonomy, repair, and commitment.

Motive identity is canonical by theme and target. Repeated pressure reactivates an existing motive instead of manufacturing an unbounded series of equivalent records. The active set is bounded so one organizing motive can coexist with a small number of active competitors while other motives remain inhibited, latent, satisfied, impossible, or retired.

Coherence is recruited by lived contradiction, inconsistency, expectation violation, and prediction error rather than by manually changing a coherence scalar.

## Continuous organism and host-world separation

The organism continues without a continuously active language model. Canonical subject state, motives, expectations, plans, endogenous pressures, and host-owned external scheduling are sufficient to produce ongoing behavior and sparse internally generated salience.

Endogenous scheduler state is separately versioned as `micropsi-duck.endogenous.v1`. Implemented sources include energy depletion, loneliness pressure, unresolved safety pressure, curiosity when safety permits, coherence disruption, approaching commitments, overdue expectations, and persistently blocked plans. Signals are hysteretic and rate-limited so unresolved pressures can recur without firing on every heartbeat.

External reality remains a separate authority. `environment_v010.py` owns host-scheduled world events under schema `micropsi-duck.environment.v1`. Observable events enter the ordinary perception/appraisal path. Hidden world changes may alter host truth without becoming subject memory, belief, expectation evidence, calibration evidence, or experiential prose.

## Prediction and expectation state

The subject-owned expectation ledger in `expectations_v010.py` is versioned as `micropsi-duck.expectations.v1`. It distinguishes predictions from world truth and from beliefs that something has already happened.

World expectations have stable identity, qualitative propositions, expected world-fact values, confidence, optional deadlines, status, evidence, and revision lineage. Deadline passage can make an expectation overdue, but lack of evidence never becomes a fabricated violation. Only perceived evidence for the relevant world fact can fulfill or violate a world expectation.

Perceived counterevidence adds expectation-violation, prediction-error, and inconsistency tags before motivated appraisal, allowing coherence to react in the same cycle. Hidden host/world changes cannot resolve or train the subject predictor.

The ledger also supports exact-action outcome expectations. A prediction about a pending canonical action is linked to that action ID and can only be resolved by the registered outcome for that exact action. Canonical plan steps automatically create bounded action-outcome predictions; routine actions do not automatically manufacture them. Abandoned or overwritten actions retire unresolved predictions without falsely training calibration.

Fulfilled and violated world and action predictions update smoothed domain calibration. New predictions can inherit learned confidence, while explicitly supplied confidence remains intact. General action reliability can influence later route scoring, but the neutral prior has no effect and evidence-weighted adjustment is capped.

## Sequence-conditioned causal prediction

MicroPsiDUCK now has a separate persistent causal-sequence model in `causal_v010.py`, versioned as `micropsi-duck.causal.v1` and persisted as `causal_v010.json`.

This model learns directed reliability between adjacent enacted actions inside one canonical plan route. For example, if a plan executes `ask` and then `explore`, the registered outcome of the later `explore` step can update a defeasible `ask -> explore` transition hypothesis.

Training is deliberately strict. Both actions must belong to the same plan and same route, the later action must be the immediately adjacent step, the previous step must have clearly succeeded, and the later step must receive a clear registered outcome. Success at or above the planner's success threshold records a fulfilled transition. Clear failure records a violated transition. Intermediate outcomes train nothing. Route changes, skipped steps, unrelated actions, hidden world changes, and abandoned actions do not train the transition.

The causal model does not claim that temporal adjacency proves causal necessity. It represents conditional predictive reliability that can bias future route evaluation. Its neutral `0.70` prior contributes no route adjustment; sparse evidence has little effect; repeated evidence can matter more; and the total sequence adjustment is bounded so it cannot override motives, cognitive modulation, safety constraints, affordance validity, or canonical outcome processing by itself.

The minimum prior-step context required to interpret the next adjacent action survives process restart. Completion, route failure, or abandonment clears obsolete context. Focused tests verify successful transition learning, negative transition learning, ambiguous-outcome nonlearning, neutral-prior behavior, route-score influence, restart persistence between steps, exactly-once training after restart, and context retirement when the plan resolves.

## Associative activation, modulation, and selective executive cognition

The typed associative overlay references canonical memories, people, concepts, motives, actions, beliefs, and other subject entities without becoming a second authority. Propagation depth, fan-out, active nodes, retained edges, and graph growth are bounded. The bridge test verifies indirect retrieval through intermediate associations when direct lexical retrieval does not surface the target memory.

Global cognitive modulation changes computation before final action selection. Threat narrows associative breadth and route branching, raises interruption sensitivity, and favors safer or more familiar strategies. Fatigue reduces planning depth and resolution. Curiosity broadens exploration when safety allows it. Low competence increases familiarity bias. Equivalent external events can therefore produce different pre-action cognitive structures under different internal regimes.

The optional executive provider is selectively recruited only when additional cognition is justified. It receives an `ExperientialFrame`, not the mechanistic `CognitiveField`, and may only propose bounded action or intention content. The organism validates the proposal against canonical affordances and falls back to automatic policy when the provider is absent, disabled, fails, or proposes an unavailable action.

Language-lesion operation disables optional language-dependent executive recruitment and inner speech while preserving motive generation, competition, associative propagation, modulation, expectation maturation and resolution, causal sequence learning, endogenous scheduling, host-world event delivery, planning, action selection, outcome learning, persistence, and experiential projection.

## Experiential firewall

The private cognition boundary remains mandatory. `ExperientialFrame` is immutable and contains first-person experiential prose only. Mechanistic numbers, machine identifiers, motive strengths, activations, route scores, retrieval scores, expectation confidence, action calibration, transition evidence counts, transition reliability, plan IDs, step indices, and causal route adjustments do not cross the experiential firewall.

Private interior state is persisted separately under `duck.private-interior.v1`. The public host separately persists canonical subject state, motivated cognition, endogenous scheduler state, expectation state, causal sequence state, environment state, and private interior state. Public interaction results and ordinary journals do not expose private thought or mechanistic interior state.

The renderer is an expression surface, not subject authority. It receives controlled prose and a humanized action-intent representation rather than raw machine actions or private telemetry.

## Validation status

The configured CI matrix runs documentation validation, focused regulation/planning/motivated evaluations, the v0.9 planning simulation, the v0.10 motivated longitudinal simulation, the full pytest suite, and designated historical simulation/evaluation suites on Python 3.11 and Python 3.12.

Focused tests cover the experiential firewall, motive persistence and competition, associative bridge retrieval, modulation regimes, selective executive recruitment, sparse endogenous scheduling, host-owned world events, hidden-world nonleakage, expectation fulfillment and violation, overdue uncertainty, revision lineage, learned expectation calibration, exact-action predictions, action reliability effects on route scoring, sequence-conditioned causal learning, and restart persistence.

The sequence-conditioned causal suite passed on both Python versions at commit `5a8e1e1fb8ae7285b687fca23422173e048001a2` in CI run #244. The earlier action-reliability route-scoring suite passed on both Python versions at commit `380a0c5a75dd1a6713cb9bde64fc652e731f304c` in CI run #240.

## Remaining architectural work

The central v0.10 motive, association, modulation, cognitive-field, firewall, selective-executive, explicit action-selection, expectation, action-prediction, sequence-causal, endogenous-dynamics, and host-world scheduling mechanisms now exist, but the development line is not frozen.

The next predictive extensions should move beyond exact equality and simple adjacent action transitions. Candidate work includes source-specific expectations, probabilistic alternatives, temporal windows, context-conditioned transition models, multi-step causal hypotheses, explicit intervention records, and counterfactual comparison of routes that were considered but not enacted. Any such extension must preserve the distinction between observed correlation, intervention evidence, and stronger causal claims.

A later environment extension can generate external events from richer simulated-world policies rather than only explicit host scheduling. Those policies must remain independently replaceable world authority rather than becoming subject-authored reality.

Executive proposals may eventually support validated goal or plan proposals in addition to immediate action proposals. A provider may suggest; the organism must validate, adopt, reject, revise, persist, and learn through canonical state machinery.

The planner still inherits substantial v0.9 representation and lifecycle machinery. A later cleanup may move goal, plan, and intention ownership into a purpose-built motivated-cognition planning layer if that produces clearer authority boundaries without sacrificing tested behavior.

Historical regression harnesses remain useful, but some older simulation modules still import branch-public components and should eventually be pinned or parameterized before their version labels are treated as exact implementation provenance.

## Preserved scientific and behavioral invariants

The v0.10 branch may change implementation structure, but it continues to protect persistent subject identity, autobiographical provenance, world and belief separation, prediction and world separation, defeasible causal learning rather than fabricated causal certainty, relationship continuity, commitments, outcome learning, restart continuity, bounded quiet-time behavior, language-lesion operation, sparse endogenous dynamics, external-world authority separation, and the experiential firewall.

Passing the current architecture and regression tests establishes the implemented behavior under the defined simulations. It does not establish phenomenal consciousness, human-equivalent cognition, unrestricted autonomy, causal correctness outside the tested domains, or general psychological validity.
