# DUCK Milestone 0.8: Motivated Prospective Agency

This milestone expands endogenous behavior from quiet-time regulation into a persistent field of unfinished intentions.

The milestone is complete when DUCK can retain multiple prospective concerns across time, allow them to compete according to current motivation and circumstance, defer them for meaningful reasons, resume them after interruption or state change, satisfy or abandon them, and preserve their lifecycle across process restart without requiring a new user prompt to reactivate the concern.

The implementation must remain subject-authoritative and language-optional. The subject-access firewall remains mandatory. Private cognition may receive first-person-accessible concern content, but it may not receive raw priority values, urgency values, internal concern IDs, cooldown counters, private persistence tags, retrieval scores, or other mechanistic telemetry.

The phase must demonstrate that a concern can become actionable during a silent heartbeat with inner speech disabled, and that a subject with no prospective concern does not invent one merely because time passes. Multiple concerns must not behave as a FIFO reminder queue. A more important or urgent concern can beat a weak curiosity while the weaker concern remains unresolved.

The phase must demonstrate motivational deferral. Low energy can postpone an energy-demanding concern without deleting it. Elevated fear or threatening context can override curiosity-driven exploration. Recovery can later permit the same concern to become actionable.

The phase must demonstrate contextual prospective memory. A concern requiring a particular situation can remain dormant while the context is absent, then become active after the subject encounters the relevant context. An interruption can displace current attention without erasing the unfinished intention.

The phase must demonstrate lifecycle closure. A satisfied concern stops competing. An impossible concern can be abandoned. A linked commitment-followup concern can become salient at the appropriate time and then retire when the underlying commitment is resolved. Resolution must preserve history rather than erasing the fact that the concern previously existed.

The phase must demonstrate persistence. At least one unresolved concern must survive full `SubjectState` serialization and reconstruction, and the long-horizon simulation must include persistent-host restart while prospective state is active.

The phase must demonstrate boundedness. Cooldowns and ordinary action regulation must prevent a single concern from monopolizing every heartbeat. After all test concerns are resolved or abandoned, extended quiet time must return to bounded baseline activity instead of continuing to manufacture goal-directed behavior.

The focused evaluation command is:

```bash
python -m duck.agency_evaluation
```

The long-horizon agency simulation command is:

```bash
python -m duck.agency_simulation --out-dir simulation_results/agency-v08
```

Before promotion, Python 3.11 and Python 3.12 CI must pass the documentation contract, complete pytest suite, original architectural evaluation, v0.6 regulation evaluation, preserved v0.5/v0.6 simulation gates, v0.7 thirty-day life simulation, focused v0.8 agency evaluation, and long-horizon v0.8 agency simulation.

Passing this milestone establishes motivated prospective agency under the tested scenarios. It does not establish phenomenal consciousness, human-equivalent planning, unrestricted autonomy, or general psychological validity.
