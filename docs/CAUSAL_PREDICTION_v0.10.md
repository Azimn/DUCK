# MicroPsiDUCK v0.10 Causal Prediction Contract

MicroPsiDUCK distinguishes prediction from causal certainty. The subject may learn that one action has tended to make a later action more or less reliable within enacted plans, but temporal order alone does not authorize the system to declare a necessary causal law.

## Authority boundaries

World truth remains host/world authority. Beliefs remain subject-owned epistemic state. Expectations remain subject-owned predictions about future world facts or the outcome of one exact canonical action. Sequence-conditioned causal calibration is a separate subject-owned mechanistic predictive model.

The causal model does not write external facts, resolve world expectations, alter beliefs directly, or bypass canonical planning and outcome registration. It can only provide bounded evidence to route evaluation.

## What may be learned

The current implementation learns adjacent action transitions inside one canonical plan route. For example, if a plan executes `ask` and then `explore`, later success or failure of the `explore` step can update a predictive transition for `ask -> explore`.

A transition observation is valid only when all of the following hold:

- both actions belong to the same canonical plan;
- both belong to the same route;
- the later action is exactly the next plan step;
- the previous step had a clearly successful registered outcome;
- the later step receives a clearly resolved registered outcome.

Unrelated actions, actions from another plan, route changes, skipped steps, and hidden world events cannot train the transition.

## Outcome thresholds

The transition learner follows the planner's clear outcome bands. A later plan step with success at or above `0.60` records a fulfilled transition. Success at or below `0.38` records a violated transition. Intermediate outcomes are ambiguous and train nothing.

These numeric thresholds are mechanistic. They remain behind the experiential firewall.

## Calibration

Each directed action transition has bounded fulfilled and violated evidence counts and a smoothed reliability estimate with the same moderate `0.70` neutral prior used by action prediction calibration.

No evidence means no route adjustment. Sparse evidence has only a small effect. Repeated evidence can change route preference more strongly, but the adjustment is capped and cannot by itself override motive competition, cognitive modulation, safety constraints, affordance validity, or canonical outcome handling.

The current route evaluator can therefore distinguish three levels of learned prediction:

1. general route properties supplied by motive and modulation;
2. action-level reliability, such as whether `explore` has tended to meet its predicted outcome;
3. sequence-conditioned reliability, such as whether `explore` has tended to succeed specifically after `ask` in enacted plans.

The third level does not imply that `ask` has been proven to cause success. It is a defeasible conditional hypothesis used for prospective control.

## Persistence and restart

Causal sequence state is persisted separately as `causal_v010.json` under schema `micropsi-duck.causal.v1`.

The persistent state contains bounded transition calibration plus the minimal previous-success context needed to interpret the next adjacent step of an active plan. This context survives restart. Once a plan completes, abandons the route, or receives a clear failed step, obsolete sequence context is removed.

The causal state is not canonical autobiographical memory and is not exposed as private thought. It is mechanistic predictive state owned by the continuing subject.

## Experiential firewall

Transition keys, evidence counts, reliability values, plan IDs, step indices, and route adjustments must never cross into `ExperientialFrame`.

The subject may experience ordinary qualitative consequences such as confidence, hesitation, familiarity, surprise, or the remembered fact that a prior approach worked. It may not introspect raw transition statistics or hidden planning machinery.

## Current scope

The current learner handles adjacent within-plan action transitions. It does not yet infer arbitrary causal graphs, latent causes, interventions, counterfactual causal effects, or source-specific structural models.

Future extensions should preserve the same discipline: causal hypotheses must be grounded in registered experience, remain defeasible, distinguish observation from intervention where possible, stay bounded, and influence behavior through validated organism-owned mechanisms rather than becoming an unconstrained language-model belief generator.
