# MicroPsiDUCK v0.10 Causal Prediction Contract

MicroPsiDUCK distinguishes prediction, temporal dependency, intervention evidence, and causal certainty. The subject may learn that one action has tended to make a later action more or less reliable within enacted plans, but temporal order alone does not authorize the system to declare a necessary causal law. Deliberately testing an action produces a stronger evidence category than ordinary succession, but it still does not establish a causal effect without a comparison condition.

## Authority boundaries

World truth remains host/world authority. Beliefs remain subject-owned epistemic state. Expectations remain subject-owned predictions about future world facts or the outcome of one exact canonical action. Sequence-conditioned causal calibration is a separate subject-owned mechanistic predictive model.

The causal model does not write external facts, resolve world expectations, alter beliefs directly, or bypass canonical planning and outcome registration. It can only provide bounded evidence to route evaluation.

## Observational sequence learning

The implementation learns adjacent action transitions inside one canonical plan route. For example, if a plan executes `ask` and then `explore`, later success or failure of the `explore` step can update a predictive transition for `ask -> explore`.

A transition observation is valid only when both actions belong to the same canonical plan and route, the later action is exactly the next plan step, the previous step clearly succeeded, and the later step receives a clear registered outcome. Unrelated actions, actions from another plan, route changes, skipped steps, and hidden world events cannot train the transition.

The learner also records clearly resolved first-step plan outcomes under a mechanistic `__plan_start__ -> action` transition. This is not an autobiographical event or a subject-visible symbol. It provides a direct-action comparison baseline for later intervention analysis.

## Intervention evidence

One exact pending canonical plan action may be marked before its outcome as a deliberate intervention. The marker carries a qualitative first-person hypothesis that must pass the experiential-prose validator. Raw confidence, percentages, telemetry, route scores, or machine state cannot be used as the hypothesis.

An intervention cannot be attached when there is no pending action or when the pending action is not a canonical active-plan action. It cannot be applied retroactively after seeing the outcome. If the marked action is abandoned or overwritten before outcome registration, the intervention marker is retired without training. A valid pending marker survives process restart and is consumed when that exact action resolves.

When a marked prior step clearly succeeds and the immediately following step later resolves, the resulting directed transition keeps intervention evidence separate from ordinary observational evidence. Total fulfilled/violated counts, intervention fulfilled/violated counts, and their corresponding smoothed reliability estimates remain mechanistic state.

The intervention label itself grants no additional behavioral weight.

## Matched baseline contrast

A stronger causal-use term is available only when intervention-supported sequencing can be compared with an ordinary direct baseline for the same target action.

For a hypothesis such as whether `ask` improves later `explore`, the treated condition is intervention evidence for `ask -> explore`. The current comparison condition is ordinary non-intervention evidence for `__plan_start__ -> explore`, representing direct exploration without the preceding ask step.

The contrast is ineligible unless both conditions contain at least two resolved observations. Once eligible, the model compares smoothed intervention reliability with smoothed direct-baseline reliability. The difference may be positive or negative. Its contribution to route evaluation is evidence-weighted and capped at a small magnitude.

This is still not a randomized causal effect. Context selection, route selection, hidden common causes, and other confounds may remain. The implementation therefore treats the result as a defeasible within-model causal contrast, not proof that the prior action caused the later outcome.

## Outcome thresholds

The transition learner follows the planner's clear outcome bands. A plan step with success at or above `0.60` is a fulfilled transition outcome. Success at or below `0.38` is a violated transition outcome. Intermediate outcomes are ambiguous and train neither observational nor intervention transition calibration.

These numeric thresholds are mechanistic. They remain behind the experiential firewall.

## Calibration and control

Each directed action transition has bounded evidence counts and a smoothed reliability estimate with a moderate `0.70` neutral prior. Observational and intervention subsets retain their own smoothed estimates.

No evidence means no route adjustment. Sparse sequence evidence has only a small effect. Repeated evidence can change route preference more strongly, but all sequence effects are capped. Intervention-specific influence is zero until a matched baseline becomes eligible. An eligible matched contrast adds only a smaller capped adjustment on top of ordinary motivated and predictive route scoring.

The route evaluator therefore distinguishes four evidence levels:

1. route properties supplied by motives and global cognitive modulation;
2. action-level predictive reliability;
3. ordinary sequence-conditioned reliability;
4. intervention-supported sequence evidence with a matched direct baseline.

None of these levels can independently override safety constraints, canonical affordance validity, motive competition, modulation, or registered outcome handling.

## Persistence and restart

Causal sequence state is persisted separately as `causal_v010.json` under schema `micropsi-duck.causal.v1`.

The persistent state contains bounded transition calibration, the minimal previous-success context needed to interpret the next adjacent plan step, and exact pending intervention markers. This state survives restart. Once a plan completes, changes route after clear failure, abandons an unresolved action, or otherwise invalidates its causal context, obsolete context and pending markers are removed.

The public host exposes only bounded aggregate status counts such as learned transition count, intervention-supported transition count, eligible causal-contrast count, and pending intervention count. It does not expose intervention hypotheses, transition reliabilities, action IDs, evidence tables, or causal route adjustments through the public expression surface.

The causal state is not canonical autobiographical memory and is not private thought. It is mechanistic predictive state owned by the continuing subject.

## Experiential firewall

Transition keys, evidence counts, reliability values, intervention markers, plan IDs, step indices, baseline symbols, contrast deltas, and route adjustments must never cross into `ExperientialFrame`.

The subject may experience ordinary qualitative consequences such as confidence, hesitation, familiarity, surprise, remembered success or failure, or a first-person intention to test an approach. It may not introspect raw causal statistics or hidden planning machinery.

## Current scope

The current learner handles adjacent within-plan action transitions, exact pre-outcome intervention markers, direct plan-start baselines, and bounded intervention-versus-baseline contrasts. It does not yet infer arbitrary causal graphs, latent causes, randomized treatment effects, multi-variable structural models, or unrestricted counterfactual worlds.

Future extensions should preserve the same discipline: causal hypotheses must be grounded in registered experience, remain defeasible, distinguish observation from intervention, require comparison evidence before stronger causal use, stay bounded, and influence behavior through validated organism-owned mechanisms rather than becoming an unconstrained language-model belief generator.
