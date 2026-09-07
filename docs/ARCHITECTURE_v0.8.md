# DUCK Motivated Prospective Agency Architecture v0.8

Status: binding architecture candidate for the `agency-lab-v0.8` branch.

DUCK remains an experimental functional simulation of a persistent human-like subject. It does not claim phenomenal consciousness. Version 0.8 preserves the v0.7 life-simulation organism and adds motivated prospective agency: unfinished intentions can remain part of the same subject across time, compete for control, defer when conditions are poor, become salient when circumstances change, survive interruption and process restart, and eventually be satisfied or relinquished without requiring a new user prompt.

The governing invariants remain:

> The machinery may know numbers. The subject does not.

> What happens to the subject must be able to change the subject who encounters the next moment.

A third operational rule is added for prospective agency:

> An intention may persist without continuously occupying attention, and may later influence action without being reissued as an external instruction.

## Why v0.8 exists

The v0.7 organism demonstrated persistent history, relationship development, epistemic revision, learning, homeostatic recovery, and quiet-time cognition. It still retained a major chatbot-like limitation: most meaningful action trajectories began because the current external event supplied the immediate reason to act.

A continuing individual is also organized by unfinished business. People carry intentions, postponed questions, commitments, plans, curiosities, and unresolved concerns across periods in which those concerns are not currently attended. Later context, time, motivation, safety, energy, or social circumstances can make one of those concerns salient again.

Version 0.8 therefore introduces a prospective concern field rather than a timer-driven reminder queue.

## Architecture

```text
LIVED EVENT / SELF-REFLECTION / COMMITMENT
                  |
                  v
        PERSISTENT PROSPECTIVE FIELD
       unfinished concerns / intentions
                  |
          quiet time continues
                  |
        +---------+----------+
        |         |          |
        v         v          v
     context    needs      safety
        |         |          |
        +---------+----------+
                  |
                  v
       MOTIVATED SALIENCE / COMPETITION
                  |
        defer / pursue / abandon
                  |
                  v
          SELECTED INTENTION
                  |
                  v
        SUBJECT ACCESS FIREWALL
                  |
                  v
          SUBJECTIVE MOMENT
                  |
                  v
     optional first-person cognition
                  |
                  v
                ACTION
                  |
                  v
               OUTCOME
                  |
                  v
       learning / resolution / next subject
```

Prospective agency remains downstream of the same persistent subject authority used by memory, beliefs, relationships, needs, and commitments. It is not a second executive agent.

## Prospective concerns

A prospective concern represents something the subject may want or need to revisit later. It is not itself a command. It can include a preferred class of action, motivational importance, urgency, a not-before boundary, a due point, minimum energy, relevant context, blocking context, a link to an existing commitment, and a lifecycle state.

The current v0.8 implementation deliberately stores this metadata on provenance-bearing `SELF_REFLECTION` memory records rather than creating a second canonical identity or goal database. This encoding is a prototype implementation detail, not a claim that human prospective memory is literally tag-based and not a permanent storage-format commitment.

Raw concern metadata is developer state. Numeric priority, urgency, internal identifiers, counters, cooldowns, and private tags never become first-person introspection.

## Motivated salience instead of reminder scheduling

A due time can increase the salience of a concern, but time alone does not execute an action. Current motivation, energy, safety, context, competing concerns, prior attempts, and deferral history also influence whether the concern becomes actionable.

A low-priority curiosity may remain dormant. A significant social obligation may beat it. A high fear state may suppress exploration. Insufficient energy may postpone a task without deleting it. A location- or situation-specific concern may remain inactive until relevant context is perceived.

This distinction is essential. DUCK v0.8 is intended to simulate motivated prospective memory, not to conceal a scheduler behind first-person prose.

## Competition and interruption

Multiple concerns may remain open simultaneously. They are evaluated as candidates for salience rather than executed FIFO. Stronger current motivation can win while weaker concerns remain unresolved.

Interruption does not erase an unfinished intention. An external event can temporarily occupy the current cognitive cycle while the prospective concern remains persistent and can return later when its conditions are met.

Recent attempts and short cooldowns prevent one concern from monopolizing every heartbeat. Silence and `wait` remain valid outcomes. A subject is not required to externalize or act on every internal concern.

## Deferral, resumption, satisfaction, and abandonment

Deferral is a first-class outcome. A concern can remain open because it is too early, the subject is exhausted, relevant context is missing, a blocking circumstance is present, or safety takes precedence.

When the relevant condition changes, the same unresolved concern can become salient again. Resumption must not require the user to restate the goal.

A completed concern is marked satisfied and stops competing. An impossible or no-longer-valued concern can be abandoned. Resolution is recorded as later self-reflective history rather than deleting the original intention from autobiography.

## Commitments and prospective agency

Existing commitments can be linked to prospective concerns. A commitment follow-up can remain dormant until its due point, later become salient without a new prompt, and retire when the underlying commitment is resolved.

Commitments remain their own canonical records. The prospective layer does not duplicate or overrule their truth. It provides a path by which a persistent commitment can influence later endogenous cognition and action.

## First-person access

The subject-access firewall remains mandatory. The subject may have access to psychologically plausible content such as remembering that it meant to inspect something, feeling that an unfinished task matters, or wanting to follow up with someone. It does not receive `priority=0.84`, internal concern IDs, cooldown counters, due-tick arithmetic, or the private persistence tags used to implement the mechanism.

Inner speech is optional. Prospective concerns must survive, compete, defer, resume, and affect action when private language generation is completely disabled.

## Safety and homeostasis remain higher-order constraints

Prospective agency does not bypass the organism. Safety and physiological-style regulation remain legitimate competitors. A curiosity-driven goal can be postponed under threat. A high-energy task can remain unresolved when the subject is depleted. Later recovery can make the same concern actionable.

This is intentionally different from a planner that forces task completion regardless of the current organism state.

## Persistence

Prospective concerns are part of persistent subject history and therefore survive ordinary state serialization and process restart. The same subject must retain open, satisfied, and abandoned concern history across restart boundaries.

Swatch Internet Time / Beat Time and UTC remain host-provided temporal representations. Internal tick arithmetic and persistence metadata are not subject introspection surfaces.

## Evaluation doctrine

Version 0.8 is evaluated in both focused probes and a longer motivated-agency simulation. The tests deliberately remove inner language, create several competing concerns, manipulate energy and safety, change context, interrupt active trajectories, resolve and abandon goals, link one concern to a commitment, restart the process, and continue quiet-time cognition afterward.

The important failure conditions are not only forgetting. The phase also rejects premature execution, FIFO-like behavior, inability to defer, inability to resume, inability to relinquish impossible goals, repeated pursuit after satisfaction, false spontaneous goal invention, runaway activity after goals are resolved, and leakage of implementation metadata into first-person cognition.

A passing v0.8 demonstrates bounded prospective agency under the tested scenarios. It does not establish human-equivalent executive function, psychological validity outside the tested regimes, phenomenal consciousness, or metaphysical agency.

## Language model boundary

No v0.8 mechanism requires an LLM. A model may later help interpret events, privately reason about an accessible concern, imagine possibilities, or express an intention, but it does not own the prospective concern field and may not inspect raw mechanistic metadata.

The LLM remains an organ, not the organism.

## Future work

The current concern field is intentionally compact. Richer hierarchical planning, automatic concern formation from complex perception, counterfactual imagination, social theory-of-mind planning, habit formation, skill composition, richer wall-clock opportunity recognition, and embodied affordance discovery remain possible future extensions. They should build on the tested distinction between persistent concern, current salience, selected intention, action, and outcome rather than collapsing those stages into one language-model prompt.
