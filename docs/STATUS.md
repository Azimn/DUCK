# MicroPsiDUCK v0.10 Current Status

Current architecture candidate: `docs/ARCHITECTURE_v0.10.md`

Current milestone candidate: `docs/MILESTONE_0_10.md`

Experiential boundary contract: `docs/EXPERIENTIAL_FIREWALL_v0.10.md`

Development branch: `motivated-cognition-v0.10`

Preserved promoted baseline: DUCK v0.9 on `main`

## Scope of the current implementation

MicroPsiDUCK v0.10 is a structural redesign rather than a compatibility-preserving patch to DUCK v0.9. The branch public package points to the v0.10 organism and persistent host. The v0.9 organism remains explicitly importable for comparison and remains preserved as the promoted baseline on `main`.

The current implementation contains the central motivated-cognition control spine. Implemented mechanisms include persistent motives, bounded motive competition, a bounded typed associative graph, transient global cognitive modulation, a transient cognitive field, automatic affordance policy, selective executive recruitment, explicit validated action selection, sparse persistent endogenous scheduling, a persistent subject-owned expectation ledger with learned calibration, host-owned external environment scheduling, outcome learning, restart persistence, and the experiential firewall.

No donor package is a runtime dependency.

## Persistent motivated cognition

Current needs, affect, commitments, relationship conditions, threat, obstacles, novelty, and coherence disruption can generate persistent motives. Implemented motive families include safety, energy, affiliation, curiosity, competence, coherence, autonomy, repair, and commitment.

Motive identity is canonical by `(theme, target)`. Repeated pressure reactivates an existing motive instead of manufacturing an unbounded series of equivalent records. Legacy duplicates can be merged, resolved contextual motives can retire, stale graph references are removed, and the motive store has a hard upper bound. The active set is also bounded so one dominant organizing motive can coexist with a small number of active competitors while other motives remain inhibited, latent, satisfied, or impossible.

Coherence can be recruited by explicit appraisal of contradiction, inconsistency, expectation violation, or prediction error. The longitudinal scenario therefore exercises coherence through a contradictory event rather than by manually lowering a coherence scalar.

## Continuous organism dynamics and endogenous scheduling

The public v0.10 organism is composed in `organism_v010.py` above the motivated-cognition core. The continuously evolving organism does not require a continuously active language model. Canonical subject state, motive state, expectations, prospective concerns and plans, and a small mechanistic endogenous scheduler are sufficient to make internally important conditions recur into cognition over time.

The scheduler state is separately versioned as `micropsi-duck.endogenous.v1`. It persists only anti-chatter machinery: latched signal keys, last-emission ticks, and emission counts. These values are developer-side mechanism and never enter `ExperientialFrame`.

Implemented endogenous sources currently include energy depletion, affiliation/loneliness pressure, unresolved safety pressure, high curiosity when safety permits, recent contradiction or unresolved coherence pressure, approaching or overdue commitments, high-confidence overdue expectations, and persistently blocked active plans. Signals are hysteretic and rate-limited. Recovery or resolution rearms a signal; an unresolved pressure may reassert after a bounded cooldown rather than firing on every heartbeat.

Actionable prospective concerns have priority over generic endogenous signals because they already represent concrete intentions. Body, social, safety, curiosity, coherence, and commitment threshold events are considered next. Overdue expectations and stalled plans can then become salient without creating duplicate goals or predictions.

A high-confidence overdue expectation produces uncertainty pressure such as the qualitative fact that something expected by now is still unconfirmed. This is explicitly not a prediction error. Lack of evidence does not become contradiction. Low-confidence overdue expectations do not automatically force inquiry. Once an overdue expectation is resolved, revised, or retired, its scheduler record is removed.

A blocked active plan becomes endogenously salient only after repeated deferral and only for genuine inability to advance, such as insufficient energy, missing required context, blocked context, or safety override. A concern intentionally scheduled for a future time is not classified as a stalled plan.

Endogenous signals use the automatic policy path. They do not recruit the optional executive merely because an internal threshold crossed. Severe safety, fatigue recovery, social need, curiosity, coherence, commitment, expectation uncertainty, and stalled-plan reactions therefore remain testable under language lesion.

## Host-owned environment dynamics

External reality is not authored by the simulated subject. MicroPsiDUCK has a separate host-owned environment scheduler in `environment_v010.py`, versioned as `micropsi-duck.environment.v1`. Its queue is persisted separately from canonical subject state, motivated-cognition state, expectation state, endogenous scheduler state, and private interior state.

The host can schedule a future external `WorldEvent` for a later organism tick. Observable scheduled events are delivered to the organism through the ordinary external-event path, so they can be appraised, remembered, associated, used as expectation evidence, and acted on without requiring a new user message. The subject does not control their occurrence.

Unperceived environmental change follows a stricter path. Host/world truth may change without delivering the hidden event to appraisal. The host updates the relevant world-fact state and then advances the organism with a normal heartbeat. Hidden event text therefore does not become autobiographical memory, belief, expectation evidence, calibration evidence, or experiential prose merely because the environment scheduler knew it happened.

The scheduler rejects self-authored endogenous events. This enforces the authority boundary: endogenous cognition can alter the subject and its actions, while external-world state changes must originate from host/world authority or another explicit environment source.

The environment queue survives restart and is bounded independently of subject memory. Scheduled event IDs and future event payloads are not stored as subject identity. The public host exposes scheduling and cancellation operations while status reports only scheduler schema and queue count rather than future-event content.

## Prediction and expectation ledger

MicroPsiDUCK now has a subject-owned persistent expectation ledger in `expectations_v010.py`, versioned as `micropsi-duck.expectations.v1`. Expectations are predictions held by the subject. They are neither world truth nor beliefs that the predicted outcome has already occurred.

Each expectation has stable identity, a qualitative proposition, a target world-fact key, an expected value, creation/update time, optional deadline, confidence, status, optional observed evidence, and revision lineage. The ledger is bounded and persists separately from host/world scheduling.

Active expectation states are `open` and `overdue`. Final states include `fulfilled`, `violated`, `superseded`, and `retired`. Deadline passage alone moves an expectation from `open` to `overdue`; it never fabricates a violation. Only perceived evidence for the expectation's fact key can fulfill or violate it. Unrelated observations do not resolve it.

When perceived evidence contradicts an active expectation, the live event is tagged with `expectation_violation`, `prediction_error`, and `inconsistency` before motivated appraisal. The coherence machinery can therefore respond in the same cognitive cycle. The subject also receives a qualitative self-reflective memory of the mismatch. Fulfilled expectations receive a corresponding confirmation record. Numeric confidence and machine IDs remain developer-side.

Revision preserves lineage rather than mutating history. Revising an active expectation marks the previous prediction `superseded` and creates a new expectation that references it. Resolution does not rewrite the prior proposition or its confidence.

The ledger also learns bounded calibration per fact domain. Fulfilled and violated predictions update a smoothed reliability estimate. New expectations with no explicit confidence use that learned calibration as their prior confidence. A miss can lower later default confidence about that domain; a later hit can recover it. Explicitly supplied confidence is preserved while still contributing evidence to domain calibration. Calibration updates only from perceived evidence.

## Associative activation and modulation

MicroPsiDUCK has a typed associative overlay that references canonical memories, people, concepts, motives, actions, beliefs, and other subject entities without becoming a second authority for those entities. Propagation depth, fan-out, active nodes, retained edges, and graph growth are bounded.

The associative bridge test demonstrates indirect retrieval: a present cue can activate a memory through intermediate associations even when direct lexical retrieval does not surface that memory. The retrieved memory retains its canonical provenance and epistemic status.

The global modulation layer changes computation before final action selection. Threat narrows associative propagation and retrieval, reduces exploration and route branching, increases interruption sensitivity, and favors safety-preserving or familiar strategies. Fatigue reduces planning depth and resolution. Curiosity permits broader exploration when safety allows it. Low competence increases familiarity bias. The same external event under different internal regimes therefore produces different pre-action cognitive structure.

## Cognitive field, automatic policy, and selective executive recruitment

Each v0.10 action cycle can assemble a transient mechanistic `CognitiveField` from current context, active motives, associative availability, modulation, and candidate affordances. The field is developer-visible and may contain scores, IDs, tags, activations, and other machinery. It is not introspectively accessible and is not persisted as subject state.

Routine endogenous cycles remain on the automatic path. Severe safety interruption can also remain automatic rather than recruiting deliberative cognition. Novelty, coherence disruption, obstacles, repair conflicts, close affordance competition, and motive conflict can recruit an optional executive provider when conditions justify the additional computation.

`ExecutiveCognitionProvider` is an optional runtime service. It never receives `CognitiveField`. Its input is only an `ExperientialFrame` containing validated first-person experiential prose. It may return an `ExecutiveProposal`, but the proposal is not subject authority. The runtime validates a proposed action against currently available canonical affordances, rejects invalid or unavailable proposals, and falls back to automatic policy when the provider is absent, disabled, fails, or returns an invalid result.

Accepted executive choices pass through an explicit `_select_candidate(...)` seam. Historical runtimes inherit the original max-utility selection unchanged. MicroPsiDUCK can choose a validated executive proposal at the selection layer without modifying the underlying affordance utilities. Regression tests require the complete candidate-utility map and the transient cognitive field to remain identical between equivalent provider and no-provider runs even when the accepted executive action differs from the automatic winner.

Executive intention prose is not automatically written to autobiographical memory, self-narrative, goals, plans, motives, beliefs, expectations, or identity. Provider configuration is host/runtime configuration rather than persistent cognitive identity. Reopening a saved organism without supplying a provider restores the same subject and cognitive state without restoring the provider itself or a previous transient cognitive field.

Private inner voice and executive proposal are separate roles. The deterministic or model-backed inner-cognition provider may generate private first-person thought after experiential projection. The executive provider is recruited selectively before final action selection and may only propose bounded action/intention content.

Current language-lesion operation disables optional language-dependent executive recruitment as well as inner speech while preserving motive generation, competition, associative propagation, modulation, expectation maturation/resolution, endogenous scheduling, environment-event delivery, planning, action selection, learning, persistence, and experiential projection.

## Experiential firewall

The private-cognition contract is `ExperientialFrame`. It is immutable and contains only approved first-person experiential prose. Structured `SubjectiveMoment` data may still exist inside inherited implementation layers as diagnostic scaffolding, but v0.10 converts it through the experiential firewall before private cognition or an executive provider receives it.

The experiential validator rejects raw decimal telemetry, percentages used as magnitude or confidence reports, machine identifiers, key-value telemetry, activation reports, route scores, retrieval scores, motive strengths, need magnitudes, expectation confidence, learned calibration scores, and related implementation leakage. Current-world text that resembles machinery is not blindly copied across the boundary; executive experiential projection falls back to qualitative first-person content when necessary.

Private interior state is persisted separately in a versioned `PrivateInteriorState` envelope. The current schema is `duck.private-interior.v1`. The persistence envelope stores approved experiential prose and optional private thought, while mechanistic affect, needs, action scores, cognitive fields, graph state, expectation machinery, executive provider configuration, endogenous scheduler state, environment scheduler state, and other developer telemetry remain outside it.

The v0.10 persistent host writes canonical subject state, motivated-cognition state, expectation state, endogenous scheduler state, environment scheduler state, and private interior state separately. Public interaction results do not include private-thought or subjective-state fields. Ordinary interaction and heartbeat journals do not publish private interior content.

The renderer receives prose-only experiential state, optional private thought as controlled rendering context, and a first-person action-intent sentence. Machine action identifiers are translated before entering the renderer packet. The renderer remains an expression surface and cannot become canonical subject authority.

## Planning and longitudinal validation

The current v0.10 runtime still reuses portions of the v0.9 bounded planner, but route ordering and planning breadth consume motive and modulation context. The v0.9 planner is not architecturally privileged and may be refactored or replaced if a cleaner planner better fits the control spine.

The dedicated MicroPsiDUCK longitudinal simulation exercises seventeen architecture gates, including associative bridge retrieval, contradiction-driven coherence, endogenous curiosity planning, failed-plan replanning, motive-driven obstacle goals, restart persistence, safety dominance, post-threat regime recovery, fatigue and recovery, repair, commitment pressure, major motive-family coverage, bounded quiet time, language lesion, and subject-access cleanliness.

Focused endogenous tests verify threshold crossing, cooldown reassertion, recovery rearming, safety-gated curiosity, contradiction-driven coherence pressure, prospective-concern priority, stalled-plan salience, future-scheduled-plan exclusion, plan resumption when context returns, expectation uncertainty pressure, language-lesion operation, and scheduler persistence across restart.

Focused environment tests verify autonomous observable external events, hidden world-fact change without belief, memory, expectation, or calibration leakage, separate queue persistence, restart delivery, language-lesion operation, and rejection of subject-authored external events.

Focused expectation tests verify fulfillment, perceived violation, same-cycle coherence recruitment, unrelated-evidence nonresolution, overdue-without-false-violation semantics, sparse overdue uncertainty, revision lineage, pressure retirement after resolution, restart persistence, schema rejection, learned calibration, calibration persistence, explicit-confidence preservation, and the rule that unperceived evidence cannot train the predictor.

The configured CI matrix runs documentation validation, focused regulation/planning/motivated evaluations, v0.9 planning simulation, the v0.10 motivated longitudinal simulation, the full pytest suite, and designated historical simulation/evaluation suites on Python 3.11 and 3.12.

## Remaining architectural work

The central v0.10 motive, association, modulation, cognitive-field, firewall, selective-executive, explicit action-selection, expectation, sparse endogenous-dynamics, and host-world scheduling mechanisms exist, but the development line is not frozen.

The next expectation target is richer predictive structure beyond exact world-fact equality. Useful extensions include source-specific expectations, probabilistic alternatives, temporal windows, expected action outcomes linked to plans, and explicit causal hypotheses. These should build on the existing ledger rather than returning to loose event tags as prediction state.

A later environment extension can add policies that generate scheduled events from richer simulated-world state rather than only explicit host scheduling. Those policies must remain external-world authority and should be independently replaceable from the subject model.

Executive proposals may eventually support validated goal or plan proposals in addition to immediate action proposals, but any such extension must preserve canonical subject authority. A provider may suggest; the organism must validate, adopt, reject, revise, persist, and learn through its own state machinery.

The current v0.10 planner still inherits substantial v0.9 representation and lifecycle machinery. A later cleanup may move goal, plan, and intention ownership into a purpose-built motivated-cognition planning layer if that produces clearer authority boundaries without sacrificing the current tested behaviors.

Historical regression harnesses remain useful, but their version binding needs continued cleanup. The v0.7 thirty-day harness is explicitly pinned to a v0.7 persistence host. Some older v0.5/v0.6/v0.8/v0.9 simulation modules still import the branch-public host and should be pinned or parameterized before their version labels are treated as exact implementation provenance rather than broad behavioral regression evidence.

## Preserved scientific and behavioral invariants

The v0.10 branch may change implementation structure, but it continues to protect persistent subject identity, autobiographical provenance, world and belief separation, prediction and world separation, relationship continuity, commitments, outcome learning, restart continuity, bounded quiet-time behavior, language-lesion operation, sparse endogenous dynamics, external-world authority separation, and the experiential firewall.

Earlier long-horizon regulation, life simulation, agency, and planning harnesses remain useful regression evidence while the new architecture is refined. They are historical behavioral tests, not authorities over v0.10 internal design.

## Relationship to DUCK v0.9

DUCK v0.9 remains the stable comparison point on `main`. It established endogenous goal formation, counterfactual route selection, hierarchical subgoals, outcome-driven replanning, and a persistent planning lifecycle.

MicroPsiDUCK v0.10 changes the research question. The target is whether needs create persistent motives, motives organize cognition, associative activation makes relevant material available without explicit search, internal condition changes the computational regime, predictions persist and learn from perceived outcomes, automatic behavior handles routine conditions, continuing internal pressures become salient without external prompting, external reality can continue changing without being authored by the subject, richer cognition is selectively recruited when necessary, and the subject experiences the consequences of those mechanisms without gaining introspective access to the machinery.

Passing the current architecture and regression tests establishes the implemented behavior under the defined simulations. It does not establish phenomenal consciousness, human-equivalent cognition, unrestricted autonomy, or general psychological validity.
