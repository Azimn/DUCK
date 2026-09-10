# MicroPsiDUCK v0.10 Current Status

Current architecture candidate: `docs/ARCHITECTURE_v0.10.md`

Current milestone candidate: `docs/MILESTONE_0_10.md`

Experiential boundary contract: `docs/EXPERIENTIAL_FIREWALL_v0.10.md`

Prediction contract: `docs/EXPECTATIONS_v0.10.md`

Causal prediction contract: `docs/CAUSAL_PREDICTION_v0.10.md`

Adversarial evaluation specification: `docs/DUCK_DISCRIMINATOR_v0.10.md`

Living improvement backlog: `docs/IMPROVEMENT_BACKLOG_v0.10.md`

Development branch: `motivated-cognition-v0.10`

Preserved promoted baseline: DUCK v0.9 on `main`

## Current implementation

MicroPsiDUCK v0.10 is a structural redesign rather than a compatibility-preserving patch to DUCK v0.9. The public package on this branch points to the composed v0.10 predictive organism and current persistent host. DUCK v0.9 remains preserved on `main` and remains explicitly importable as a historical comparison point.

The implemented v0.10 control spine includes persistent motives, bounded motive competition, typed associative activation, global cognitive modulation, a transient cognitive field, automatic affordance policy, selective executive recruitment, validated action selection, bounded planning, sparse endogenous dynamics, subject-owned world expectations, exact-action outcome expectations, learned prediction calibration, sequence-conditioned predictive calibration, explicit intervention evidence, matched causal contrasts, transient counterfactual route comparison, host-owned external world scheduling, outcome learning, restart persistence, and the experiential firewall.

No donor package is a runtime dependency.

## Persistent motivated cognition

Needs, affect, commitments, relationship conditions, threat, obstacles, novelty, and coherence disruption can generate persistent motives. Implemented motive families include safety, energy, affiliation, curiosity, competence, coherence, autonomy, repair, and commitment.

Motive identity is canonical by theme and target. Repeated pressure reactivates an existing motive instead of manufacturing an unbounded series of equivalent records. The active set is bounded so one organizing motive can coexist with a small number of active competitors while other motives remain inhibited, latent, satisfied, impossible, or retired.

Coherence is recruited by lived contradiction, inconsistency, expectation violation, and prediction error rather than by manually changing a coherence scalar.

## Continuous organism and host-world separation

The organism continues without a continuously active language model. Canonical subject state, motives, expectations, plans, endogenous pressures, and host-owned external scheduling are sufficient to produce ongoing behavior and sparse internally generated salience.

Endogenous scheduler state is separately versioned as `micropsi-duck.endogenous.v1`. Implemented sources include energy depletion, loneliness pressure, unresolved safety pressure, curiosity when safety permits, coherence disruption, approaching commitments, overdue expectations, and persistently blocked plans. Signals are hysteretic and rate-limited so unresolved pressures can recur without firing on every heartbeat.

External reality remains separate authority. `environment_v010.py` owns host-scheduled world events under schema `micropsi-duck.environment.v1`. Observable events enter the ordinary perception/appraisal path. Hidden world changes may alter host truth without becoming subject memory, belief, expectation evidence, calibration evidence, or experiential prose.

## Prediction and expectation state

The subject-owned expectation ledger in `expectations_v010.py` is versioned as `micropsi-duck.expectations.v1`. It distinguishes predictions from world truth and from beliefs that something has already happened.

World expectations have stable identity, qualitative propositions, expected world-fact values, confidence, optional deadlines, status, evidence, and revision lineage. Deadline passage can make an expectation overdue, but lack of evidence never becomes a fabricated violation. Only perceived evidence for the relevant world fact can fulfill or violate a world expectation.

Perceived counterevidence adds expectation-violation, prediction-error, and inconsistency tags before motivated appraisal, allowing coherence to react in the same cycle. Hidden host/world changes cannot resolve or train the subject predictor.

The ledger also supports exact-action outcome expectations. A prediction about a pending canonical action is linked to that action ID and can only be resolved by the registered outcome for that exact action. Canonical plan steps automatically create bounded action-outcome predictions; routine actions do not automatically manufacture them. Abandoned or overwritten actions retire unresolved predictions without falsely training calibration.

Fulfilled and violated world and action predictions update smoothed domain calibration. New predictions can inherit learned confidence, while explicitly supplied confidence remains intact. General action reliability can influence later route scoring, but the neutral prior has no effect and evidence-weighted adjustment is capped.

## Sequence-conditioned and intervention-aware causal prediction

MicroPsiDUCK has separate persistent causal state in `causal_v010.py`, versioned as `micropsi-duck.causal.v1` and persisted as `causal_v010.json`.

Ordinary sequence learning records bounded directed reliability between adjacent actions inside one enacted canonical plan route. The later action must be the immediately adjacent step in the same plan and route, the previous step must have clearly succeeded, and the later step must receive a clear registered outcome. Clear success trains a fulfilled transition, clear failure trains a violated transition, and ambiguous outcomes train nothing.

Clearly resolved first plan steps are also recorded against a hidden mechanistic `__plan_start__` baseline. This provides direct-action comparison data without becoming autobiographical memory or introspectively visible state.

A pending canonical plan action can be marked before its outcome as a deliberate intervention carrying a qualitative first-person hypothesis. The hypothesis must pass `ExperientialFrame` validation. No pending action, routine nonplan actions, telemetry-bearing hypotheses, and retroactive marking are rejected. Intervention markers survive restart but are discarded without training when their action is abandoned or overwritten.

When a marked prior step succeeds and its immediately following plan step later resolves, the directed transition records intervention evidence separately from ordinary observational evidence. Merely labeling an action as an intervention grants no extra route weight.

Intervention-specific route influence requires a matched direct baseline for the same target action. For example, intervention evidence for `ask -> explore` is compared with ordinary `__plan_start__ -> explore` evidence. Both sides require at least two resolved observations before the contrast becomes eligible. The resulting difference can support or oppose the multi-step route, is evidence-weighted, and is capped at a small magnitude.

This is a defeasible within-model contrast, not a randomized causal effect. Context selection and other confounds remain possible. The architecture therefore preserves a strict distinction among temporal association, intervention evidence, matched contrast, and stronger causal claims.

The minimum previous-step context, pending intervention markers, transition evidence, and matched-baseline evidence survive process restart through the causal state file. Plan completion, clear route failure, or abandoned pending actions clear obsolete transient causal context.

## Counterfactual route prediction

Route selection now records a transient developer-side comparison of the routes considered at the decision point. Every route estimate is explicitly provenance-labeled `model_prediction`; exactly one route is selected and the remaining alternatives remain unenacted counterfactuals.

Counterfactual snapshots are intentionally non-persistent. Reading them is side-effect free and does not create autobiographical memory, belief, expectation evidence, causal training data, world truth, relationship evidence, or private experiential history. Reopening the host begins with no counterfactual snapshot.

Counterfactual evidence descriptions may identify which evidence classes informed a route estimate, such as motivated structure, action calibration, sequence calibration, intervention-supported sequence evidence, or an eligible matched intervention contrast. Raw preference scores and causal telemetry remain developer-side.

The counterfactual boundary and non-persistence tests are verified on the current branch. CI run #262 completed successfully on Python 3.11 and Python 3.12 at commit `2959ce945fa59c7d9691b2e4206e5743afdf4cc8`.

## Associative activation, modulation, and selective executive cognition

The typed associative overlay references canonical memories, people, concepts, motives, actions, beliefs, and other subject entities without becoming a second authority. Propagation depth, fan-out, active nodes, retained edges, and graph growth are bounded. The bridge test verifies indirect retrieval through intermediate associations when direct lexical retrieval does not surface the target memory.

Global cognitive modulation changes computation before final action selection. Threat narrows associative breadth and route branching, raises interruption sensitivity, and favors safer or more familiar strategies. Fatigue reduces planning depth and resolution. Curiosity broadens exploration when safety allows it. Low competence increases familiarity bias. Equivalent external events can therefore produce different pre-action cognitive structures under different internal regimes.

The optional executive provider is selectively recruited only when additional cognition is justified. It receives an `ExperientialFrame`, not the mechanistic `CognitiveField`, and may only propose bounded action or intention content. The organism validates the proposal against canonical affordances and falls back to automatic policy when the provider is absent, disabled, fails, or proposes an unavailable action.

Language-lesion operation disables optional language-dependent executive recruitment and inner speech while preserving motive generation, competition, associative propagation, modulation, expectation maturation and resolution, causal sequence and intervention learning, endogenous scheduling, host-world event delivery, planning, action selection, outcome learning, persistence, and experiential projection.

## Experiential firewall

The private cognition boundary remains mandatory. `ExperientialFrame` is immutable and contains first-person experiential prose only. Mechanistic numbers, machine identifiers, motive strengths, activations, route scores, retrieval scores, expectation confidence, action calibration, transition evidence counts, transition reliability, intervention markers, baseline symbols, plan IDs, step indices, contrast deltas, causal route adjustments, and counterfactual preference scores do not cross the experiential firewall.

Private interior state is persisted separately under `duck.private-interior.v1`. The public host separately persists canonical subject state, motivated cognition, endogenous scheduler state, expectation state, causal sequence state, environment state, and private interior state. Public interaction results and ordinary journals do not expose private thought or mechanistic interior state.

The renderer is an expression surface, not subject authority. It receives controlled prose and a humanized action-intent representation rather than raw machine actions or private telemetry.

## Validation status

The configured CI matrix runs documentation validation, focused regulation/planning/motivated evaluations, the v0.9 planning simulation, the v0.10 motivated longitudinal simulation, the full pytest suite, and designated historical simulation/evaluation suites on Python 3.11 and Python 3.12.

Focused tests cover the experiential firewall, motive persistence and competition, associative bridge retrieval, modulation regimes, selective executive recruitment, sparse endogenous scheduling, host-owned world events, hidden-world nonleakage, expectation fulfillment and violation, overdue uncertainty, revision lineage, learned expectation calibration, exact-action predictions, action reliability effects on route scoring, sequence-conditioned causal learning, restart persistence, intervention marking, intervention restart, abandoned-intervention nonlearning, matched-baseline eligibility, positive and negative causal-contrast effects, transient counterfactual route comparison, counterfactual side-effect purity, counterfactual non-persistence, and counterfactual firewall/status nonleakage.

The current full configured matrix passed on both Python versions at commit `2959ce945fa59c7d9691b2e4206e5743afdf4cc8` in CI run #262.

The explicit intervention suite passed on both Python versions at commit `853cf1801e918c17ea667044d7f946c48654100c` in CI run #249. The sequence-conditioned causal suite passed on both Python versions at commit `5a8e1e1fb8ae7285b687fca23422173e048001a2` in CI run #244. The action-reliability route-scoring suite passed on both Python versions at commit `380a0c5a75dd1a6713cb9bde64fc652e731f304c` in CI run #240.

Normal CI is not the same as adversarial validation. `DUCK_DISCRIMINATOR_v0.10.md` now defines a separate falsification-oriented evaluation program, and `IMPROVEMENT_BACKLOG_v0.10.md` records the weaknesses and discriminator failures that remain to be addressed.

## Remaining architectural work

The central v0.10 motive, association, modulation, cognitive-field, firewall, selective-executive, explicit action-selection, expectation, action-prediction, sequence-causal, intervention-aware, counterfactual-route, endogenous-dynamics, and host-world scheduling mechanisms exist, but the development line is not frozen.

The next predictive extensions should move beyond exact equality and simple adjacent transitions. Candidate work includes source-specific expectations, probabilistic alternatives, temporal windows, context-conditioned transition models, multi-step causal hypotheses, stronger comparison designs, and richer counterfactual models. Counterfactual model output must continue to remain distinct from observed history.

The highest-priority hardening work is tracked in `IMPROVEMENT_BACKLOG_v0.10.md`. Current items include transactional persistence, stronger world/subject state separation, runtime composition cleanup, semantic experiential-firewall hardening, parameter sensitivity, convergent associative activation, context-conditioned causal learning, adversarial validation, and historical harness provenance.

A later environment extension can generate external events from richer simulated-world policies rather than only explicit host scheduling. Those policies must remain independently replaceable world authority rather than becoming subject-authored reality.

Executive proposals may eventually support validated goal or plan proposals in addition to immediate action proposals. A provider may suggest; the organism must validate, adopt, reject, revise, persist, and learn through canonical state machinery.

The planner still inherits substantial v0.9 representation and lifecycle machinery. A later cleanup may move goal, plan, and intention ownership into a purpose-built motivated-cognition planning layer if that produces clearer authority boundaries without sacrificing tested behavior.

Historical regression harnesses remain useful, but some older simulation modules still import branch-public components and should eventually be pinned or parameterized before their version labels are treated as exact implementation provenance.

## Preserved scientific and behavioral invariants

The v0.10 branch may change implementation structure, but it continues to protect persistent subject identity, autobiographical provenance, world and belief separation, prediction and world separation, observational and intervention evidence separation, defeasible causal learning rather than fabricated causal certainty, counterfactual and observed-history separation, relationship continuity, commitments, outcome learning, restart continuity, bounded quiet-time behavior, language-lesion operation, sparse endogenous dynamics, external-world authority separation, and the experiential firewall.

Passing the current architecture and regression tests establishes implemented behavior under the defined simulations. It does not establish phenomenal consciousness, human-equivalent cognition, unrestricted autonomy, randomized causal identification, causal correctness outside tested domains, or general psychological validity.

## Behavior-first hardening, 2026-09-09

Current work adds distinct-cue associative convergence, provenance-aware experiential projection, negative strategy penalties, private-provider fallback, exact pending-action tag restoration, and a contextual deterministic renderer that does not automatically publish recollections. The targeted executable discriminator is available as `python -m duck.discriminator`. See `BEHAVIOR_FIRST_v0.10.md` for scope and validation limits. Human believability and all-metrics 9/10 are not established.

Local validation passed 182 tests on Python 3.12, the documentation contract, and all configured evaluation/simulation commands. A development 10,000-tick seed-17 run passed boundedness with peaks of 2,000 memories, 2,048 graph edges, and seven motives; `evidence/behavior-first-10000-development.json` explicitly records its development provenance. The clean `5fb6492` commit separately passed the seven-scenario targeted profile at seed 91 over 200 ticks. GitHub publication was blocked by automatic approval review, so no remote CI success is claimed.

## Evidence and embodiment increment, 2026-09-10

The current public organism now supports native `SensoryEvidence`, personally conditioned appraisal, direct fact-observation belief and expectation integration before action selection, body-derived regulatory pressure, transactional body and regulatory components, explicit grounded affordances with persistent selected targets, and bounded strategy learning conditioned on the selection-time regime. AdaptiveSelfCore is historical compatibility only in v0.10. Current stepping no longer uses temporary subject-world-truth writes. The deterministic fallback uses local qualitative stance independently of private prose wording.

`docs/EMBODIED_PERCEPTION_v0.10.md` defines these contracts and their limits. Legacy WorldEvent semantic hints and action catalogs remain explicit compatibility adapters. Contextual causal transition tables, fully grounded native heartbeat scheduling, and independent human believability assessment are not claimed complete.

Implementation verification: commit `43421e53c682ac9571f0e2fa9a6580a06eb77391` passed [Actions run 34445348762](https://github.com/Azimn/DUCK/actions/runs/34445348762). Both Python versions passed the configured evaluations, simulations, and 203-test suite; the 200-tick targeted discriminator also passed. A development 10,000-tick attempt produced no completed report and is not counted as evidence.

## Prior-work reuse integration

`docs/DONOR_REUSE_v0.10.md` records pinned TinyPersonaEngine sensory-access and Jelly room/host donors. The public host supports native room ticks and bounded elapsed-time catch-up with preserved time debt, spatial access, actual object consequences, and transactional room state. This is a bounded simulated room, not a full embodiment or human-believability result.

## Component comparison

`docs/COMPONENT_SELECTION_v0.10.md` and `duck.component_comparison` record scoped comparisons of spatial access, attention relevance, catch-up arithmetic, and social action availability. The selected implementation refreshes configured-room decisions through the standard heartbeat, integrates scheduled world changes, and retains DUCK transactional persistence. The comparison reports correctness and diagnostic timing, not overall human-likeness or global optimality.
