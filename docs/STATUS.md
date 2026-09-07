# DUCK Current Status

Current architecture candidate: `docs/ARCHITECTURE_v0.7.md`

Current milestone candidate: `docs/MILESTONE_0_7.md`

Branch: `life-sim-v0.7`

## Integrated implementation

DUCK v0.7 retains the v0.6 regulated whole-organism architecture and adds a life-simulation refinement layer in `duck/living_v07.py`. The public package and persistent host use the v0.7 candidate on this branch. `duck/living_v06.py` remains the regulated v0.6 baseline and `duck/living.py` remains the earlier integrated baseline.

The organism contains persistent subject identity, affect and homeostatic needs, relationship trajectories, autobiographical memory with provenance, objective world facts separated from subject beliefs, commitments, lived-consequence residue, action selection, action/outcome separation, outcome-dependent learned affordances, a small path-dependent adaptive latent trace, endogenous heartbeat, optional first-person inner cognition, optional bounded model-assisted semantic appraisal, optional model-backed expression, deterministic fallbacks, atomic JSON state persistence, an append-only JSONL host journal, UTC timestamps, and Swatch Internet Time / Beat Time stamps.

The subject-access firewall remains mandatory. Model-backed private cognition and expression are constructed exclusively from qualitative first-person state. Raw mechanistic numbers remain developer diagnostics.

No donor package is a runtime dependency.

## Thirty-day longitudinal simulation

`duck/life_simulation.py` runs one persistent Aster through a deterministic thirty-day simulated life. The scenario includes recurring people, a helpful first encounter, a prospective commitment, an overdue commitment, a broken promise, hidden host truth, false testimony, direct contradictory evidence, ordinary social contact, apology, a second kept promise, repeated novel threat encounters with outcome learning, long quiet periods, and process restarts on simulated Days 10, 21, and 29.

The life-simulation gate checks subject-access isolation, restart integrity, spontaneous salience of an overdue commitment, later recall of a broken promise, causal relationship trajectories, causal epistemic revision, adaptive-core contribution under ablation, bounded quiet-time behavior, bounded numeric state, bounded memory/buffers, and persistent history for a recurring person.

## v0.7 corrections discovered by simulated life

The first thirty-day run against v0.6 remained bounded but exposed subtler artificiality. Benign social encounters were too often resolved as `ask`, safety could remain chronically depleted after danger had passed, competence could saturate at 1.0, and a relationship containing a broken commitment could retain a permanent undifferentiated wariness even after later apology and reliable follow-through.

Version 0.7 adds slow safety recovery toward a conservative baseline and slow competence normalization. Social action selection now uses event context: questions and supportive contact favor ordinary response, explicit repair can create a repair affordance, and recent repeated questioning receives bounded inhibition. These rules modify intention selection below the language layer rather than asking an LLM to cosmetically vary dialogue.

Relationship reinterpretation is also evidence-sensitive. A broken commitment remains autobiographical history, but later kept commitments can change its current first-person meaning. Under sufficient later evidence the subject can represent the mixed history as `They let me down before, but they've followed through since.` rather than remaining indefinitely in the same warning state.

## Verified evidence

Implementation head `50c7c49f0028e6a7f6436996ca1943f392111f84` passed GitHub Actions workflow `34119932720` on Python 3.11 and Python 3.12. The documentation guard, full repository tests, original architecture evaluation, v0.6 regulation evaluation, preserved baseline simulations, and the v0.7 thirty-day life simulation all completed successfully. Subsequent commits formalize the v0.7 milestone, documentation authority, focused regression tests, and consistent use of the v0.7 candidate inside the ablation probe; those commits require their own branch-head CI before promotion.

In the verified thirty-day run, all eleven life-simulation gates passed. The three process restarts preserved subject identity, tick, memory count, and commitment count. No float reached `SubjectiveMoment`.

Across 121 quiet heartbeat cycles, Aster selected `wait` 84 times, `step_back` 25 times, `rest` seven times, `ask` four times, and `explore` once, with no `seek_connection` behavior. The final affect state was near baseline rather than chronically escalated.

Safety recovered to approximately 0.716 after the later threat sequence rather than remaining near the earlier depleted value, while competence finished near 0.929 rather than saturating at 1.0. Energy finished near 0.81, affiliation near 0.31, and curiosity near 0.45. The final state contained 36 memories, one belief, two resolved commitments, and no active residue.

The epistemic sequence remained causal. Host truth placed the garden key in the blue box without giving the subject access. Riley's false testimony produced a remembered red-box statement and a red-box belief. Direct observation later revised the belief to blue box while preserving the fact that Riley had said red box. The corrected blue-box belief survived to Day 30.

The relationship sequence also remained causal. Morgan's initial support produced trust near 0.564 and guardedness near 0.160. The broken promise moved trust to 0.420 and guardedness to 0.322. Before explicit repair, trust fell further to 0.342 and guardedness rose to 0.426. An apology moved those values in the repair direction, and a later kept promise raised trust to 0.511. By the final Morgan encounter trust was near 0.543 while the earlier failure remained part of autobiographical history.

The first-person interpretation changed with that evidence. Before repair Aster could represent the relationship as `I'm still wary because they let me down before.` After the later kept promise the simulation produced `They let me down before, but they've followed through since.` The adverse event was not deleted.

Repeated successful glorp encounters increased the selected defensive action utility from approximately 0.532 to 0.964 to 1.261. In the later adaptive-core comparison, the learned candidate utility was approximately 1.358 with the adaptive state present versus 0.862 after ablation.

## Current interpretation

DUCK v0.7 is a life-simulation candidate rather than merely a conversation architecture. Its present value is that memory, belief, affect, relationships, motivation, learning, recovery, and restart continuity are tested as one interacting system over an extended synthetic history.

The central evaluation question is what remains obviously fake when linguistic fluency is not allowed to conceal the architecture. Passing the current tests establishes bounded causal behavior under the tested scenarios. It does not establish phenomenal consciousness, human-equivalent cognition, or general psychological validity.

## Deliberately unfinished surfaces

Model swapping is not a current priority. Real camera/audio sensing, robotics, XR embodiment, avatar animation, voice interruption, richer wall-clock scheduling, long-duration human evaluation, and a polished desktop/mobile shell remain future product surfaces.

The v0.6, v0.5, and v0.1 documents remain preserved as historical architecture. The older `DUCK_Unified_Subject_Architecture_Design_Spec_v0.3` remains non-current donor material.
