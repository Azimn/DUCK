# DUCK v0.9 Planning Phase Engineering Notes

Status: nonbinding engineering notes. `ARCHITECTURE_v0.9.md` and `MILESTONE_0_9.md` are authoritative.

Version 0.9 began from a deliberately uncomfortable question: if v0.8 can carry an unfinished intention, who creates the intention and what happens when the first way of pursuing it is wrong?

The first planning candidate therefore did not start by adding a language-model planner. It added a small deterministic route system so the executive mechanics could be exposed directly to tests. Goal formation is gated by lived events and existing motivational state. Route preference is computed from the persistent subject's current state. The current route is decomposed into v0.8 prospective concerns. Outcome, rather than action selection, decides whether the route advances or changes.

This separation produced a useful architecture defect almost immediately. The first hierarchical test appeared superficially correct: the subject chose `ask`, the plan advanced to its second step, the subject chose `explore`, and the plan root became completed. Yet the test still failed because open plan-step concerns remained.

The diagnostic run showed that the original plan-step records were actually closing correctly. The unexpected open concerns were `OUTCOME` memories whose text was the successful outcome description. Those memories had inherited `opportunity`, `prospective`, `plan_step`, and private `pl_*` tags through the action's event tags. The v0.8 concern scanner therefore treated the result of an action as if it were a new intention.

That failure was more important than simply making the test green. It identified a category error at the boundary between executive control and learning. Tags that are useful for selecting and tracing an action are not necessarily semantic properties of the resulting world event.

The v0.9 correction sanitizes pending action tags immediately before generic outcome learning. Environmental and task-semantic tags survive. Idle markers, prospective lifecycle tags, concern IDs, preferred-action metadata, `pc_*` fields, `pl_*` fields, and plan-step control markers do not become learned outcome tags. The generic learner can still update affordances from meaningful context without allowing bookkeeping to reproduce itself as cognition.

The planning layer also now enforces a stronger child-lifecycle invariant. An active plan may have at most one open current plan-step concern. Activating a step first checks whether that exact current child already exists so repeat activation is idempotent. Any stale child from another branch is retired before a new one is created. Completing or abandoning a plan retires any residual live child before changing the root lifecycle state.

Another design choice worth preserving is that a plan step is not given a special execution channel. Once activated, it is a normal prospective concern. Fear, low energy, competing concerns, cooldown, and other organism-level constraints still apply. This prevents the planner from becoming a hidden task bot that overrides the rest of the subject whenever it has something to do.

The initial goal-formation gate is intentionally conservative. It recognizes a small set of architecturally useful cases rather than pretending to solve unrestricted human goal formation. Novelty plus curiosity can create investigation. Obstruction plus autonomy can create an overcoming goal. Relationship conflict can create repair when the relationship gives the repair motive sufficient meaning. Ordinary experience remains a negative control.

Likewise, the current route library is a testing scaffold, not a claim that cognition consists of three hand-written plan types. Its purpose is to establish the required interfaces: one objective can have alternatives, state can change route preference, a route can have ordered children, outcome can advance or invalidate it, and the whole structure can persist without language generation.

The focused v0.9 evaluation is deliberately run before the general pytest step in CI while this phase is under development. This makes architecture failures print their structured diagnostic report instead of being reduced to a single assertion line. Once the phase stabilizes, retaining that early focused gate is useful because it makes planning regressions legible.

The long-horizon simulation uses the real persistent host once v0.9 becomes the current candidate. It forms an investigation goal from an unfamiliar panel, fails direct exploration, switches to cautious inquiry, completes inquiry and informed inspection, forms a separate obstacle goal, restarts the process with that plan active, completes it after restart, presents an ordinary control event, and then continues quiet time. Inner speech remains disabled throughout.

The larger lesson from this phase is consistent with DUCK's development doctrine: do not ask fluent language to cover an architectural discontinuity. When a test says the subject has two ghost intentions after successfully finishing a plan, the correct response is not better prose. The correct response is to find the authority or lifecycle boundary that allowed an outcome to masquerade as a goal.