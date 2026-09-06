# DUCK Current Status

Current architecture candidate: `docs/ARCHITECTURE_v0.5.md`

Current milestone candidate: `docs/MILESTONE_0_5.md`

Branch: `franken-duck`

## Integrated implementation

The branch contains the original Subjective Moment kernel plus a clean-room integrated organism in `duck/living.py`, bounded model interfaces in `duck/language.py`, optional bounded semantic interpretation in `duck/semantics.py`, explicit temporal representation in `duck/temporal.py`, a persistent host in `duck/host.py`, an integrated evaluation harness in `duck/evaluation.py`, and an interactive CLI in `duck/cli.py`.

The integrated organism now contains persistent subject identity, affect and homeostatic needs, relationship trajectories, autobiographical memory with provenance, objective world facts separated from subject beliefs, commitments, decaying lived-consequence residue, action selection, action/outcome separation, outcome-dependent learned affordances, a small path-dependent adaptive latent trace, endogenous heartbeat, optional first-person inner cognition, optional bounded model-assisted semantic appraisal, optional model-backed expression, deterministic fallbacks, atomic JSON state persistence, an append-only JSONL host journal, UTC timestamps, and Swatch Internet Time / Beat Time stamps.

The subject-access firewall remains mandatory. Model-backed private cognition and expression are constructed exclusively from qualitative first-person state. The semantic model sees only the current utterance and source and can propose only schema-bounded tags, valence, and intensity. Raw mechanistic numbers remain developer diagnostics.

## Donor synthesis

`docs/DONOR_AUDIT_v0.1.md` remains the donor map. The integrated build uses design lessons from Digital Subject causal continuity, TinyPersonaEngine first-person authority boundaries, Gelatinblob path-dependent learning and action/outcome separation, and Wayfarer/Ensemble subject authority, provenance, commitments, and model firewalls. Alice, Moemate, rho, Omnicore, and AIML remain useful for later presentation, proactivity, and evaluation work.

No donor package is a runtime dependency.

## Verified evidence

Integrated commit `51bab647c5d781a862e83649b56a32d1d67e3d7d` passed GitHub Actions workflow `34012675711` on Python 3.11 and Python 3.12. The documentation authority guard passed, the full repository suite reported `22 passed`, and `python -m duck.evaluation` passed all three current architecture probes.

The paired-history evaluation produced the same present event after two different histories. The neutral subject selected `ask`; the previously threatened subject selected `step_back`, reported first-person fear/unease/suspicion, and retrieved its prior encounter and outcome. The language-lesion evaluation demonstrated action selection and outcome learning with inner language disabled. The persistence evaluation reopened the same subject identity with its state intact.

The regression suite additionally verifies raw-float exclusion from `SubjectiveMoment`, world-fact versus belief separation, broken-commitment causal effect, positive outcome learning, endogenous heartbeat initiative, model-facing packet isolation, bounded semantic-model proposals, deterministic semantic fallback, and deterministic Beat Time conversion.

## Current interpretation

This is now a coherent integrated cognitive-organism prototype rather than a one-mechanism research kernel. It is appropriate for end-to-end simulation, ablation, transcript studies, model-assisted conversation experiments, and further product hardening. The passing tests establish authority boundaries and causal behavior, not phenomenal consciousness or human-equivalent cognition.

## Deliberately unfinished surfaces

Real camera/audio sensing, robotics, XR embodiment, avatar animation, voice interruption, wall-clock catch-up scheduling, long-duration human evaluation, and a polished desktop/mobile shell remain future product surfaces. The integrated cognitive core does not depend on those surfaces.

The earlier v0.1 documentation remains preserved as history. The older `DUCK_Unified_Subject_Architecture_Design_Spec_v0.3` remains non-current donor material.
