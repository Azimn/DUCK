# MicroPsiDUCK v0.10 Counterfactual Prediction Contract

MicroPsiDUCK may compare routes that were available but not enacted. Those comparisons are model predictions, not experiences. This distinction is mandatory because a persistent organism that silently remembers imagined alternatives as observed history will corrupt autobiography, calibration, causal learning, and eventually identity.

## Provenance

Every unchosen route estimate has fixed provenance `model_prediction`.

A counterfactual estimate is not:

- an autobiographical memory;
- a perceived world event;
- a belief that the route actually occurred;
- an expectation that the route will necessarily occur;
- an action outcome;
- causal training evidence;
- a private thought;
- public renderer content.

The current counterfactual dataclasses reject alternate provenance labels.

## Decision-time snapshot

When the motivated planner orders routes, the predictive layer creates a transient `RouteComparisonSnapshot` for that exact organism tick. The snapshot contains one selected route and developer-side estimates for the other available routes.

Each route estimate contains its route kind, route name, action sequence, current preference score, qualitative evidence-class labels, selected/not-selected status, and fixed model-prediction provenance.

The preference score is not a probability of success and must not be rendered as one.

The evidence-class labels may indicate that the estimate used motivated structure, action calibration, ordinary sequence calibration, intervention sequence evidence, or an eligible matched intervention contrast. They identify classes of machinery, not numeric confidence.

## Relationship to cognitive modulation

The snapshot may contain developer estimates for routes that the current modulation regime would not keep inside the bounded active planning branch set. This does not mean the subject consciously considered every available route. The snapshot is an engineering counterfactual surface over the planner's available route definitions, separate from the subject's bounded cognitive search.

The actual plan still obeys route ordering, route-branching limits, motive competition, safety, fatigue, and other modulation effects.

## No persistence

The counterfactual module intentionally defines no persistence format. `last_route_comparison` is transient runtime state.

Saving the host does not serialize it. Reopening the same subject begins with no counterfactual snapshot. Subject state, expectation state, causal state, private interior state, motivated-cognition state, and environment state do not acquire counterfactual route estimates merely because a comparison occurred.

If a future version needs longitudinal counterfactual research data, that data must live in a developer/evaluation log with explicit model-prediction provenance. It must not be inserted into canonical subject memory.

## No learning from unchosen outcomes

An unchosen route has no registered outcome. It therefore cannot train:

- action success calibration;
- sequence calibration;
- intervention evidence;
- matched causal contrast;
- belief confidence;
- expectation fulfillment or violation.

Learning occurs only from enacted canonical actions and permitted perceived evidence.

A later real execution of a formerly counterfactual route is a new enacted event. Its actual registered outcome may then train the ordinary learning machinery.

## Experiential firewall

Counterfactual route names, preference scores, evidence labels, selected flags, and snapshot objects do not cross into `ExperientialFrame` or `PrivateInteriorState`.

The subject may have ordinary first-person experiences that resemble human counterfactual thought, such as wondering whether another approach might have worked, but such prose must be generated through an explicitly approved experiential mechanism. It must not expose or copy the developer-side route table.

The current counterfactual route snapshot is not that mechanism.

## Public surface

The current persistent host does not report counterfactual scores, route alternatives, or snapshot contents in ordinary public status. Public interaction results and renderer packets remain unchanged.

## Current scope

The current implementation provides decision-time alternative-route estimates and strict non-persistence. It does not yet simulate complete alternate world trajectories, fabricate hypothetical memories, perform Monte Carlo rollouts, or train on imagined outcomes.

Future counterfactual work should preserve three separate provenance classes:

1. observed history, which may train from actual experience;
2. explicit future expectation, which may later be tested against permitted evidence;
3. counterfactual model prediction, which remains hypothetical unless the corresponding action is actually enacted.
