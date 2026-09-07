# DUCK Endogenous Planning Architecture v0.9

Status: binding architecture candidate for the `planning-lab-v0.9` branch.

DUCK remains an experimental functional simulation of a persistent human-like subject. It does not claim phenomenal consciousness. Version 0.9 preserves the v0.8 life-simulation and motivated prospective-agency organism, then adds a bounded planning layer: selected goals can arise from lived experience, alternative routes can be compared against the subject's current condition, a chosen route can unfold through ordered subgoals, and failed action can revise the route rather than merely producing another fluent explanation.

The governing invariants remain:

> The machinery may know numbers. The subject does not.

> What happens to the subject must be able to change the subject who encounters the next moment.

> An intention may persist without continuously occupying attention, and may later influence action without being reissued as an external instruction.

Version 0.9 adds two operational rules:

> A goal may arise from lived experience rather than from an external instruction.

> Plans are hypotheses, not scripts. Outcome can invalidate a route and change what the subject tries next.

## Why v0.9 exists

Version 0.8 removed one major chatbot artifact by allowing unfinished intentions to survive the user turn. It could remember that something still mattered, wait for the right circumstances, compete with other concerns, defer under threat or low energy, resume after interruption, and close the concern when it was satisfied or abandoned.

That still left an important artificiality. The meaningful concern usually had to be registered explicitly. Once registered, it normally pointed at one preferred action rather than representing a larger objective with more than one possible route. A convincing continuing individual should sometimes acquire a goal because of what it encounters, consider more than one way to respond, pursue intermediate steps, discover that an approach did not work, and alter the plan while retaining the original reason for caring.

Version 0.9 attacks that gap without making an LLM the executive system.

## Architecture

```text
PERCEIVED LIVED EVENT
        |
        v
ordinary appraisal / memory / belief / relationship update
        |
        v
GOAL-FORMATION GATE
experience + needs + relationship + context
        |
        +---- no meaningful trigger ----> no new goal
        |
        v
PERSISTENT GOAL ROOT
why this matters to this continuing subject
        |
        v
COUNTERFACTUAL ROUTE SELECTION
more than one candidate way forward
        |
        v
CURRENT ROUTE
        |
        v
HIERARCHICAL SUBGOAL
        |
        v
v0.8 motivated prospective agency
        |
        v
subject-access firewall
        |
        v
SubjectiveMoment
        |
        v
optional inner cognition
        |
        v
ACTION
        |
        v
OUTCOME
   |           |
 success     failure
   |           |
   v           v
next step   route invalidated
   |           |
   |      counterfactual replanning
   |           |
   +-----------+
        |
        v
changed continuing subject
```

Planning is layered on top of the same persistent subject authority. It is not a second agent and it is not a text planner whose prose is treated as cognition.

## Endogenous goal formation

A v0.9 goal can be created after a perceived event when the event has a goal-relevant relation to the subject's current state. The first implementation intentionally keeps this gate narrow. Novel or unknown situations can produce an investigative goal when curiosity is sufficiently engaged. A perceived obstacle can produce an overcoming goal when autonomy pressure makes the obstruction relevant. Relationship conflict or explicit repair need can produce a repair goal when the existing relationship makes repair meaningful.

This mechanism is not intended to turn every event into a task. Ordinary experience is a control condition. A calm, unchanged room should not manufacture a new objective merely because the subject is alive and time is passing.

The original triggering experience remains autobiographical evidence. The goal root is a later `SELF_REFLECTION` memory linked to that history rather than a rewrite of the event itself.

## Persistent goal roots

The goal root records a qualitative objective such as wanting to understand an unfamiliar mechanism or work out a way past an obstacle. Mechanistic planning metadata is encoded privately on that same provenance-bearing memory record. This preserves the single persistent `SubjectState` authority instead of introducing a separate planner-owned identity store.

The current encoding includes plan kind, lifecycle status, ordered candidate routes, current route index, current subgoal index, triggering memory link, current child concern link, and current attempted action link. Those fields are implementation machinery. They are not introspective facts available to the subject.

A plan root can be active, completed, or abandoned. Completion and abandonment preserve history instead of deleting the plan from autobiography.

## Counterfactual route selection

Counterfactual route selection means the architecture can represent more than one plausible way to pursue the same objective before action is committed. The present prototype uses a small deterministic route library so the architecture can be tested without hiding route generation inside an LLM.

For investigation, direct exploration can compete with cautious inquiry followed by exploration. For an obstacle, inspection followed by action can compete with seeking information before acting. For relationship repair, a direct repair attempt can compete with clarification before repair.

Route ordering is influenced by the subject's current mechanistic condition. Curiosity, autonomy, affiliation, safety, competence, energy, and fear can alter which route is preferred. A low-risk curious subject can prefer direct exploration while the same objective under higher fear can favor information gathering first.

The route scores themselves remain developer state. First-person cognition may later contain a qualitative tendency such as wanting to ask first, but it does not receive the arithmetic used to rank routes.

## Hierarchical subgoals

A selected route is decomposed into one current subgoal at a time. Each current subgoal becomes an ordinary v0.8 prospective concern and therefore inherits the already-tested agency machinery for salience, competition, safety, energy, interruption, cooldown, and persistence.

This reuse is deliberate. Planning should not bypass the organism. A plan does not receive a privileged execution channel just because the planner wants it completed.

The architecture enforces a lifecycle invariant: an active plan may have at most one live current plan-step concern, while a completed or abandoned plan must have zero live child intentions. Step transitions retire the prior child before activating the next one.

## Outcome-driven replanning

An attempted plan step is not equivalent to success. The ordinary DUCK action/outcome boundary remains authoritative. The host or world reports an outcome after the action. That outcome is learned and remembered before the planner decides how the plan changes.

Sufficient success satisfies the current child concern and advances the route. If another subgoal remains, it becomes the new current prospective concern. If the final subgoal succeeds, the plan root becomes completed.

A sufficiently failed action marks the attempted child concern unsuccessful. If another route remains, the previous route is treated as invalidated under the current evidence and the plan restarts at the first subgoal of the next route. DUCK adds a qualitative self-reflection that the previous approach did not work and another way is being tried. If no route remains, the plan is abandoned instead of looping forever.

This is the phase's central distinction from scripted task execution. The selected plan can be wrong.

## Outcome memory is not executive state

During development, the v0.9 tests exposed a cross-layer error. The v0.8 endogenous action event carried prospective-control tags into the pending action. The generic outcome learner then copied those tags onto the resulting `OUTCOME` memory. Because v0.8 identifies prospective concerns partly through tags, the outcome could be misclassified as a new open concern. Successful evidence therefore created a ghost intention.

Version 0.9 separates semantic action tags from executive bookkeeping before outcome learning. Environmental and task-semantic tags remain available to learning, while private concern IDs, route metadata, planning tags, opportunity lifecycle tags, and idle-control tags are stripped from the outcome's learned tag set.

This produces a stronger invariant: an outcome can change learning and planning, but an outcome record cannot become a new executive intention merely by inheriting control metadata.

## First-person access

The subject-access firewall remains mandatory. The subject can access qualitative material such as remembering an unresolved objective, feeling drawn toward investigation, recalling that an approach failed, or recognizing that another way should be tried. It does not receive plan IDs, route indexes, subgoal indexes, candidate-route scores, internal concern IDs, private persistence tags, or raw numeric need and affect values.

Inner speech is optional. Endogenous goal formation, route selection, hierarchical subgoal advancement, outcome-driven replanning, persistence, and plan closure must operate with private language generation disabled.

The Language-Lesion principle therefore continues to apply: removing eloquent internal narration must not remove the executive structure being evaluated.

## Persistence and restart

Goal roots and plan-step concerns use the same canonical persistent subject memory ledger as the rest of DUCK. An active plan must survive `SubjectState` serialization and reconstruction. The long-horizon v0.9 simulation also restarts the persistent host while a plan is active and then continues that same plan in the same subject.

Swatch Internet Time / Beat Time and UTC remain host-provided temporal representations. Persistence mechanics and raw temporal arithmetic remain outside first-person introspection.

## Boundedness

Endogenous planning must not turn DUCK into an obsessive task engine. Goal formation is gated. Plans can fail. Routes can be exhausted. Completed and abandoned plans stop producing child concerns. Ordinary experience does not automatically generate new goals. After test plans close, extended quiet time must return to the regulated baseline rather than continuing to invent purposeful activity.

Silence remains a valid behavior. `wait` is not failure merely because a plan system exists.

## Evaluation doctrine

The focused v0.9 evaluation tests goal formation from experience without explicit registration, state-sensitive route choice, multi-step hierarchical progression, failure-triggered route revision, state-roundtrip persistence, ordinary-experience controls, and planning-metadata isolation.

The long-horizon simulation creates an investigative goal from an unfamiliar signal, deliberately fails the initially preferred direct route, requires replanning through inquiry, completes the revised route, later forms an obstacle goal from experience, restarts the persistent host while that plan remains active, completes the plan after restart, presents an ordinary control event, then runs extended quiet time to detect runaway goal manufacture.

All v0.9 planning evaluations run with inner speech disabled. Every long-horizon `SubjectiveMoment` is checked for raw floats and private planning metadata.

Passing these gates demonstrates bounded endogenous goal formation and counterfactual hierarchical planning under the tested scenarios. It does not establish general planning intelligence, human-equivalent executive function, phenomenal consciousness, unrestricted autonomy, or psychological validity outside the evaluated regimes.

## Language model boundary

No v0.9 planning mechanism requires an LLM. A model may later help propose richer candidate routes, interpret ambiguous situations, simulate accessible possibilities, or express a plan, but its suggestions must be converted into bounded structures owned and evaluated by the persistent organism. It does not become the canonical goal store, the route authority, or the outcome judge.

The LLM remains an organ, not the organism.

## Future work

The current route library is deliberately small and deterministic. Future phases can investigate learned route construction, causal world models, richer counterfactual simulation, hierarchical goals deeper than two steps, plan interaction across multiple long-lived objectives, theory-of-mind planning, habits, skill composition, richer embodied affordances, and opportunity discovery from continuous sensory streams.

Those extensions should preserve the distinctions established here: lived event is not goal, goal is not plan, plan is not action, action is not outcome, and outcome can revise the subject who plans what comes next.