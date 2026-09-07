# DUCK Current Status

Current architecture candidate: `docs/ARCHITECTURE_v0.9.md`

Current milestone candidate: `docs/MILESTONE_0_9.md`

Branch: `planning-lab-v0.9`

## Integrated implementation

DUCK v0.9 retains the v0.8 motivated prospective-agency organism and adds endogenous goal formation, counterfactual route selection, hierarchical plan steps, and outcome-driven replanning in `duck/living_v09.py`. The candidate wiring makes the persistent host and public package use the v0.9 organism while `duck/living_v08.py`, `duck/living_v07.py`, `duck/living_v06.py`, and `duck/living.py` remain preserved implementation layers and regression baselines.

The organism contains persistent subject identity, affect and homeostatic needs, relationship trajectories, autobiographical memory with provenance, objective world facts separated from subject beliefs, commitments, lived-consequence residue, action selection, action/outcome separation, outcome-dependent learned affordances, a small path-dependent adaptive latent trace, endogenous heartbeat, motivated prospective concerns, optional first-person inner cognition, optional bounded model-assisted semantic appraisal, optional model-backed expression, deterministic fallbacks, atomic JSON state persistence, an append-only JSONL host journal, UTC timestamps, and Swatch Internet Time / Beat Time stamps.

Version 0.9 adds persistent goal roots linked to lived experience, deterministic candidate routes whose ordering depends on current subject state, sequential child concerns for hierarchical subgoals, and route revision after failed action outcome. The subject-access firewall remains mandatory. Raw route scores, plan IDs, route indexes, child indexes, prospective priority/urgency values, internal concern identifiers, cooldowns, private tags, and other mechanistic telemetry remain developer state.

No donor package is a runtime dependency.

## Endogenous planning implementation

The goal-formation gate is deliberately bounded. Novel or unknown perceived situations can create an investigative goal when curiosity is sufficiently engaged. Obstacles can create an overcoming goal when autonomy pressure makes the blockage relevant. Relationship conflict or explicit repair need can create a repair goal when the relationship state makes repair meaningful. Ordinary perception is a negative control and does not automatically create an objective.

A goal root is a provenance-bearing `SELF_REFLECTION` memory in the canonical `SubjectState`. Private `pl_*` tags carry plan kind, status, candidate routes, current route, current step, trigger link, child-concern link, and pending-action link. This keeps planning in the existing subject authority rather than introducing a second canonical planner database.

The current route library is intentionally small and deterministic. It exists so route choice and replanning can be evaluated without an LLM silently generating the executive structure. Investigation can choose direct exploration or cautious inquiry followed by exploration. Obstacles can choose inspection-first or information-first routes. Repair can choose direct repair or clarification-first repair.

Current affect and needs influence route ordering. The focused test demonstrates that low fear with high curiosity prefers direct exploration while a higher fear state can make cautious inquiry preferable for the same investigative objective.

Plan steps reuse v0.8 prospective concerns. This means planning remains subordinate to the organism's motivation, safety, energy, competition, and interruption behavior. A plan does not gain an unconditional task-execution channel.

## Lifecycle defect discovered by planning

The first hierarchical v0.9 test exposed a cross-layer bug after the visible plan behavior already looked correct. The subject asked for information, advanced to the next step, explored, and completed the plan, yet two open plan-step concerns remained.

Diagnostics showed that the real plan-step memories had been satisfied. The open records were `OUTCOME` memories whose descriptions were the successful outcomes. Prospective and planning control tags had propagated from the endogenous action event into the pending action and then into the generic outcome memory. The v0.8 concern scanner consequently misclassified those outcome records as new open intentions.

Version 0.9 now sanitizes action tags before generic outcome learning. Environmental and task-semantic tags are retained, while `pc_*`, `pl_*`, concern identifiers, preferred-action metadata, plan-step markers, opportunity lifecycle tags, and idle-control tags are removed. Outcome memory can influence learning and replanning without becoming a ghost concern.

The planning layer also enforces explicit child lifecycle invariants. An active plan can have at most one live current plan-step concern. Repeated activation of the same current step is idempotent. Completing or abandoning a plan leaves zero live child intentions.

## Focused and long-horizon evaluation

`duck/planning_evaluation.py` tests experience-driven goal formation, risk-sensitive route choice, two-step hierarchical progression, failed-route replanning, state-roundtrip persistence, ordinary-experience false-goal control, and first-person metadata isolation. All probes run with private inner speech disabled.

`duck/planning_simulation.py` runs a longer sequence through the real persistent-host surface. An unfamiliar signal produces an investigative goal. The initially preferred direct route is deliberately failed, causing a switch to cautious inquiry. Successful inquiry advances to informed inspection, which completes the plan. A later blocked gate produces a separate obstacle goal. The host is restarted while that plan is active, the plan continues and completes after restart, an ordinary control event is presented, and quiet time continues afterward to detect runaway goal generation.

Every long-horizon `SubjectiveMoment` is checked for raw floats and private planning metadata. The simulation therefore tests planning while language generation is absent rather than using fluent private narration to conceal executive gaps.

## Verified evidence

The v0.8 merge commit `42e6e7dd86f09f9cec3152d5bd24b9dd98607447` passed post-merge `main` workflow `34168398759` on Python 3.11 and Python 3.12, including all v0.8 and prior regression gates.

The v0.9 planning core at head `759f69a7e60a8a0bbb0dc234f8294e14d98155e4` passed workflow `34169181283` on Python 3.11 and Python 3.12. The focused v0.9 planning evaluation, complete pytest suite, original architecture evaluation, v0.6 regulation evaluation, preserved v0.5/v0.6 simulations, v0.7 thirty-day longitudinal life simulation, v0.8 focused agency evaluation, v0.8 long-horizon agency simulation, and v0.9 long-horizon planning simulation all passed.

The documentation, package-version, public-export, and persistent-host wiring in the current candidate commit require their own branch-head CI before promotion. No promotion claim should be made until that exact head passes both Python versions.

## Relationship to earlier phases

The v0.7 thirty-day longitudinal life simulation and v0.8 motivated prospective agency remain mandatory regression gates. v0.9 does not replace relationship development, epistemic integrity, homeostatic recovery, adaptive action learning, first-person reinterpretation, commitment continuity, or unfinished-intention competition. It adds a larger causal arc: experience can generate an objective, the objective can organize more than one possible route, a route can unfold through intermediate intentions, and consequence can alter the plan.

The central research question remains what is obviously fake when language fluency is not allowed to hide the architecture. For v0.9 the specific question is whether DUCK can behave like a subject that develops and revises purposes, rather than a chatbot that waits for tasks or a task runner that mistakes its script for reality.

Passing the current tests establishes bounded endogenous goal formation and counterfactual hierarchical planning under the tested scenarios. It does not establish phenomenal consciousness, human-equivalent general intelligence, unrestricted autonomy, or general psychological validity.

## Deliberately unfinished surfaces

The present route library is hand-authored and shallow. Learned causal world models, open-ended goal discovery, generated route candidates with architecture-level verification, deeper planning trees, simultaneous interacting plans, theory-of-mind planning, habits, skill composition, richer embodied affordance discovery, real camera/audio sensing, robotics, XR embodiment, avatar animation, voice interruption, long-duration human evaluation, and polished desktop/mobile shells remain future work.

The v0.8, v0.7, v0.6, v0.5, and v0.1 documents remain preserved as historical architecture. The older `DUCK_Unified_Subject_Architecture_Design_Spec_v0.3` remains non-current donor material.