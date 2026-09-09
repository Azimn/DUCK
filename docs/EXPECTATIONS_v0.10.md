# MicroPsiDUCK v0.10 Prediction and Expectation Contract

This document defines the prediction boundary for the current MicroPsiDUCK v0.10 candidate. It supplements `ARCHITECTURE_v0.10.md` and is subordinate only to the architecture and milestone documents if a conflict appears.

## Authority separation

MicroPsiDUCK distinguishes at least three epistemic authorities:

```text
WORLD TRUTH
what is actually the case in the host/environment

SUBJECT BELIEF
what the subject currently takes to be the case

SUBJECT EXPECTATION
what the subject predicts may become or prove to be the case
```

These stores may influence one another, but they are not interchangeable.

A hidden world change may alter world truth without altering belief or expectation status. A perceived observation may update belief and may fulfill or violate an expectation. An expectation does not become a world fact merely because the subject strongly predicts it.

## Expectation ownership

Expectations belong to the continuing subject. The current versioned persistence envelope is `micropsi-duck.expectations.v1`.

Mechanistic expectation records may contain IDs, fact keys, deadlines, confidence, learned calibration, status, evidence references, and revision lineage. These are developer-side representations. They do not cross the experiential firewall.

The subject may experience qualitative consequences such as:

```text
I expected that by now, but I still don't know whether it happened.
What happened did not match what I expected.
That happened the way I thought it would.
```

The subject may not introspect:

```text
expectation_id = exp-000014
confidence = 0.83
calibration.weather = 0.71
status = overdue
```

## World-fact expectations

A world-fact expectation predicts a value for an external fact key.

It may be:

```text
open
    |
    +---- perceived confirming evidence ----> fulfilled
    |
    +---- perceived counterevidence --------> violated
    |
    +---- deadline passes ------------------> overdue
    |
    +---- explicit revision ----------------> superseded
    |
    +---- explicit abandonment -------------> retired
```

`overdue` does not mean `violated`. A missed deadline without evidence represents uncertainty, not contradiction.

Only perceived evidence for the relevant fact key may fulfill or violate the expectation. Unrelated observations do not resolve it. Hidden host/world changes cannot resolve it or train expectation calibration.

## Prediction error

Prediction error requires evidence.

When perceived evidence contradicts an active expectation, the event may acquire `expectation_violation`, `prediction_error`, and `inconsistency` control semantics before motivated appraisal. This allows coherence pressure, associative retrieval, planning, or executive recruitment to respond in the same cognitive cycle.

Mere lateness is not prediction error. High-confidence overdue expectations may generate sparse uncertainty pressure through the endogenous scheduler, but that event must not be labeled as a contradiction.

## Revision

Revision preserves history.

An active expectation that is revised becomes `superseded`. The replacement receives a new stable identity and points back to the prior expectation. Prior predictions and their confidence are not silently rewritten to make the subject appear retrospectively correct.

## Calibration

MicroPsiDUCK maintains bounded learned calibration by prediction domain. Confirmed and violated predictions alter the default confidence used for later expectations in the same domain.

Calibration is smoothed so one observation does not produce extreme certainty or distrust. Explicitly supplied confidence is preserved for that prediction while its eventual outcome may still contribute evidence to domain calibration.

Calibration updates only from evidence available to the subject. Omniscient host knowledge cannot train the subject's predictor.

## Action-outcome expectations

A world-fact expectation and an action-outcome expectation require different evidence.

A world-fact expectation asks:

```text
What do I expect the world to be like?
```

An action-outcome expectation asks:

```text
What do I expect this action to cause?
```

Action-outcome expectations must link to one canonical pending action. They may predict minimum success, expected valence or another bounded outcome property. They are resolved only when `resolve_outcome(...)` resolves that exact action. A later unrelated world observation cannot fulfill or violate an action-outcome expectation.

Likewise, resolving an action outcome must not implicitly claim that unrelated world-fact expectations were tested.

This distinction is required before plan-level causal learning can be treated as prediction rather than simple action-reward association.

## Boundedness

Expectation records, calibration domains, endogenous expectation-pressure scheduler records, and any future causal-hypothesis structures must remain bounded.

Repeated pressure should update, revise, or resolve existing prediction state rather than generating unlimited semantically equivalent records.

## Language lesion

Expectation maturation, overdue transition, perceived-evidence resolution, calibration learning, prediction-error tagging, endogenous uncertainty pressure, persistence, and action-outcome comparison must operate without inner language or an LLM.

Language may render or reflect the experiential consequences of prediction. It is not the mechanism that owns or evaluates the prediction.
