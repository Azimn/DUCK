# DUCK Milestone 0.6: Long-Horizon Regulation

This milestone promotes simulation testing to a first-class architecture gate. The integrated v0.5 organism remains the foundation, but it is not sufficient for individual mechanisms to look plausible in isolation. The subject must remain bounded, recoverable, history-sensitive, and non-perseverative when those mechanisms interact over long sequences.

Milestone 0.6 is complete when the regulated candidate passes the existing architecture probes, the full unit/regression suite, focused regulation tests, the preserved v0.5 simulation baseline, and the full v0.6 longitudinal simulation suite on Python 3.11 and 3.12.

The subject-access firewall remains mandatory. Simulation code may inspect raw developer telemetry for diagnosis, but private cognition must never receive raw numeric psychological state.

The required simulation behaviors include paired-history divergence after the same present event, epistemic integrity when host world facts are unknown to the subject, later consequences from kept and broken commitments, memory influence without an explicit recall prompt, measurable adaptive-core contribution under ablation, language-lesion survival, endogenous heartbeat behavior, persistence across restart, affective recovery after adverse events, bounded homeostatic state during long quiet periods, and relationship repair that moves state without erasing adverse history.

The quiet-time acceptance rule explicitly permits most cycles to produce `wait`. A persistent subject does not need to speak or initiate an outward action on every heartbeat. The failure condition is runaway initiative, state saturation, starvation, or pathological repetition of active behavior, not silence.

The v0.6 regulation candidate must demonstrate that a single adverse event can leave a temporary residue and later recover toward baseline in the absence of new adverse evidence. Remembering the event may continue to influence appraisal and action, but idle recall must not count as a fresh injury on every cycle.

Endogenous drive regulation must remain causally modest. Rest may restore energy, curiosity-directed activity may reduce curiosity pressure, and connection-seeking may create a limited refractory reduction in affiliation pressure. These internal effects may not fabricate successful world outcomes.

The principal commands are:

```bash
python -m pip install -e '.[test]'
python tools/check_docs.py
python -m duck.regulation_evaluation
python -m pytest
python -m duck.evaluation
python -m duck.simulation_lab --out-dir simulation_results/baseline
python -m duck.simulation_lab_v06 --out-dir simulation_results/v06
```

The milestone is not an LLM quality test and does not prioritize model swapping. Model-independent simulation is intentional because the purpose is to test the organism beneath linguistic fluency.

Vision, audio, robotics, XR, and elaborate avatar presentation are not required for this milestone. They remain future surfaces governed by the same first-person access rule.
