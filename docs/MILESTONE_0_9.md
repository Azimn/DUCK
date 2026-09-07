# DUCK Milestone 0.9: Endogenous Goal Formation and Counterfactual Planning

This milestone expands v0.8 prospective agency from carrying explicit unfinished intentions into forming selected goals from lived experience and pursuing those goals through revisable multi-step plans.

The milestone is complete when DUCK can encounter a goal-relevant event without receiving an explicit task command, form a persistent qualitative goal because that event matters to the current subject, compare more than one candidate route, activate one current subgoal through the existing motivated-agency layer, use action outcome to advance or invalidate the route, and preserve the plan across process restart.

The implementation must remain subject-authoritative and language-optional. The subject-access firewall remains mandatory. Private cognition may receive qualitative goal and concern content, but it may not receive raw route scores, route indexes, subgoal indexes, internal plan IDs, concern IDs, private persistence tags, need values, affect values, retrieval scores, or developer telemetry.

The phase must demonstrate endogenous goal formation. A mystery or unknown situation can produce an investigative objective when curiosity makes it relevant. A meaningful obstacle can produce an overcoming objective when autonomy makes the blockage relevant. Ordinary experience must remain a negative control and must not manufacture a goal merely because a perception occurred.

The phase must demonstrate counterfactual route choice. At least one objective must have more than one candidate route, and changing the subject's current risk state must be able to alter the preferred route without changing the objective itself.

The phase must demonstrate hierarchical subgoals. At least one selected route must require two ordered child intentions. Successful completion of the first child must close that child, advance the plan, and activate the second. Completing the final child must complete the plan and leave zero live plan-step concerns.

The phase must demonstrate outcome-driven replanning. A failed route must not be cosmetically narrated as success and must not be retried indefinitely. Failure must close the attempted child concern, preserve the failed outcome as history, move to a different available route, and activate that route's first subgoal. If no route remains, the plan can be abandoned.

The phase must demonstrate that outcome memory does not become executive state. Plan-control and prospective-control tags must be stripped before learned action tags are persisted to an `OUTCOME` memory. An outcome record must not be misclassified as a fresh prospective concern or ghost goal.

The phase must demonstrate persistence. An active plan must survive full `SubjectState` serialization and reconstruction. The long-horizon simulation must also perform a process restart of the persistent host while an active plan exists and then continue the same plan under the same subject identity.

The phase must demonstrate boundedness. Once test plans are completed or abandoned, an ordinary control event and extended quiet time must not cause indefinite goal manufacture or residual plan execution.

The phase must demonstrate language lesion. Goal formation, route selection, subgoal progression, failure-triggered replanning, restart continuity, and closure must all work with private inner speech disabled. Planning metadata must remain absent from the first-person `SubjectiveMoment`.

The focused evaluation command is:

```bash
python -m duck.planning_evaluation
```

The long-horizon planning simulation command is:

```bash
python -m duck.planning_simulation --out-dir simulation_results/planning-v09
```

Before promotion, Python 3.11 and Python 3.12 CI must pass the documentation contract, complete pytest suite, original architectural evaluation, v0.6 regulation evaluation, preserved v0.5/v0.6 simulation gates, v0.7 thirty-day longitudinal life simulation, v0.8 focused agency evaluation, v0.8 long-horizon agency simulation, focused v0.9 planning evaluation, and long-horizon v0.9 planning simulation.

Passing this milestone establishes bounded endogenous goal formation, state-sensitive counterfactual route selection, hierarchical subgoal progression, and outcome-driven replanning under the tested scenarios. It does not establish phenomenal consciousness, human-equivalent general planning, unrestricted autonomy, or general psychological validity.