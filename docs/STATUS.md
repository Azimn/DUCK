# DUCK Current Status

Current architecture candidate: `docs/ARCHITECTURE_v0.6.md`

Current milestone candidate: `docs/MILESTONE_0_6.md`

Branch: `simulation-lab-v0.6`

## Integrated implementation

DUCK retains the v0.5 whole-organism implementation and adds a regulated v0.6 candidate in `duck/living_v06.py`. The public package and persistent host use the regulated candidate on this branch while `duck/living.py` remains preserved as the v0.5 baseline implementation for direct comparison.

The organism contains persistent subject identity, affect and homeostatic needs, relationship trajectories, autobiographical memory with provenance, objective world facts separated from subject beliefs, commitments, lived-consequence residue, action selection, action/outcome separation, outcome-dependent learned affordances, a small path-dependent adaptive latent trace, endogenous heartbeat, optional first-person inner cognition, optional bounded model-assisted semantic appraisal, optional model-backed expression, deterministic fallbacks, atomic JSON state persistence, an append-only JSONL host journal, UTC timestamps, and Swatch Internet Time / Beat Time stamps.

The subject-access firewall remains mandatory. Model-backed private cognition and expression are constructed exclusively from qualitative first-person state. Raw mechanistic numbers remain developer diagnostics.

No donor package is a runtime dependency.

## Simulation infrastructure

`duck/simulation_lab.py` preserves the original v0.5 long-horizon scenarios and report format. `duck/simulation_lab_v06.py` runs those same scenarios against the regulated v0.6 organism. `duck/regulation_evaluation.py` contains focused checks for affective recovery, quiet-time regulation, and relationship repair after broken commitments.

The simulation set exercises paired-history divergence, hidden world truth versus subject belief, commitment consequences, memory influence without explicit recall prompting, adaptive-core ablation, long language-lesion runs, 500-cycle quiet-time behavior, and a multi-day relationship scenario with process restart.

## Failures found by simulation

The first v0.5 long-horizon run passed its original broad assertions but exposed three important behavioral pathologies. A single residual negative event could be re-added as fresh affect every heartbeat, important negative memories could repeatedly increase unease and guardedness during idle recall, and homeostatic variables saturated because heartbeat actions did not regulate the needs that selected them.

The 500-cycle v0.5 baseline ended with energy at 0.0, affiliation at 1.0, curiosity at 1.0, and `seek_connection` selected 459 times. A 60-cycle language-lesion run selected `step_back` 59 times. These were treated as simulation failures even though the earlier loose assertions technically passed.

## v0.6 corrections

Version 0.6 treats lived-consequence residue as decaying activation rather than fresh injury on every cycle. Idle retrieval of a negative autobiographical memory no longer creates a new permanent guardedness increment or a fresh unease increment. Endogenous actions can partially regulate the drives that selected them, and recent-action inhibition discourages active-intention perseveration. Waiting is treated as healthy silence and does not restore energy.

Repair is directional rather than amnesic: an apology can raise trust and lower guardedness while the subject still remembers the prior broken commitment.

## Verified evidence

Branch head `7ea54b1fc967b3cd308a62c7de8e7bbdf1d3930f` passed GitHub Actions workflow `34118784081` on Python 3.11 and Python 3.12. The documentation guard passed, the full pytest suite reported `26 passed`, the original architectural evaluation passed, the preserved baseline simulation passed its historical gates, and the regulated v0.6 simulation suite completed successfully.

The focused recovery test began after an adverse event with fear 0.380 and unease 0.437. After 40 quiet cycles, fear recovered to 0.042 and unease to 0.042 while the autobiographical event remained available. The final 20 actions were 18 `wait`, one `rest`, and one `seek_connection`, rather than continued defensive perseveration.

In 500 quiet v0.6 heartbeat cycles, `wait` occurred 436 times, `rest` 25 times, `seek_connection` 26 times, `explore` 11 times, and `ask` twice. The connection-seeking ratio was 5.2 percent rather than the v0.5 baseline's 91.8 percent. Energy finished at 0.85, affiliation at 0.59, and curiosity at 0.43 instead of saturating at their bounds.

The regulated 60-cycle language-lesion run produced 32 `step_back`, 22 `wait`, two `ask`, two `rest`, and two `seek_connection` actions while preserving learned threat-action association and using no inner language.

The long paired-history test still differentiates subjects after identical present input. A neutral history responds to Morgan, a previously threatened history steps back and recalls the threat, and a supportive history responds with lower suspicion. The threat-conditioned subject's unease in the same-present probe is approximately 0.305 rather than the v0.5 baseline's saturated 1.0.

The multi-day persistent scenario preserves subject identity across restart, recalls Morgan's broken promise on a later return, steps back on the unresolved return, and later shifts to `ask` when Morgan attempts repair. Focused repair evaluation moved trust from 0.356 to 0.389 and guardedness from 0.362 to 0.296 without erasing the broken-promise memory.

## Current interpretation

DUCK v0.6 is a stronger whole-organism simulation candidate because longitudinal testing now constrains how its mechanisms compose over time. The result is not merely more features: the same memory, affect, relationship, motivation, and heartbeat mechanisms now demonstrate recovery, boundedness, persistence, causal history sensitivity, and nonverbal operation over longer runs.

Passing these tests establishes behavior under the tested scenarios. It does not establish phenomenal consciousness, human-equivalent cognition, or psychological validity outside those regimes.

## Deliberately unfinished surfaces

Model swapping is not a current priority. Real camera/audio sensing, robotics, XR embodiment, avatar animation, voice interruption, richer wall-clock scheduling, long-duration human evaluation, and a polished desktop/mobile shell remain future product surfaces.

The v0.5 and v0.1 documents remain preserved as history. The older `DUCK_Unified_Subject_Architecture_Design_Spec_v0.3` remains non-current donor material.
