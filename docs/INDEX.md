# MicroPsiDUCK Documentation Authority

This file defines which documents govern the current development branch and how the preserved DUCK history relates to it.

## Current MicroPsiDUCK v0.10 candidate

`ARCHITECTURE_v0.10.md` is the binding structural architecture for MicroPsiDUCK v0.10.

`MILESTONE_0_10.md` is the executable acceptance contract for the v0.10 research candidate.

`EXPERIENTIAL_FIREWALL_v0.10.md` is a binding interface contract. It requires a prose-only experiential data contract for private cognition, versioned persistence of private interior state, and a renderer that may read controlled private prose without publishing private state.

`EXPECTATIONS_v0.10.md` is a supporting technical contract for prediction semantics. It defines the separation among world truth, subject belief, and subject expectation; perceived-evidence requirements; overdue versus violated predictions; calibration; revision lineage; and the evidence boundary for action-outcome expectations. It cannot override the architecture or milestone documents.

`CAUSAL_PREDICTION_v0.10.md` is a supporting technical contract for action reliability, sequence-conditioned evidence, explicit intervention evidence, matched direct baselines, and the boundary between defeasible predictive contrast and stronger causal claims. It cannot override the architecture or milestone documents.

`DUCK_DISCRIMINATOR_v0.10.md` is the adversarial evaluation specification. It defines how MicroPsiDUCK should be attacked through randomized holdouts, metamorphic tests, mechanism ablations, parameter perturbation, persistence crash injection, epistemic attacks, firewall/prompt-injection attacks, long-run boundedness, counterfactual provenance tests, causal-confound scenarios, and historical-provenance audits. It does not redefine architecture; it attempts to falsify architectural claims.

`IMPROVEMENT_BACKLOG_v0.10.md` is the living weakness and failure register. Architectural review findings and meaningful DUCK Discriminator failures must create or update an item there with severity, evidence, reproduction information, and explicit criteria for declaring the weakness fixed. Closed items remain in the document as research history.

`MICROPSI_MODERNIZATION_v0.10.md` is supporting design context describing which Psi and MicroPsi principles are being preserved and which historical implementation details are deliberately not copied. It is nonbinding and cannot override the architecture, milestone, experiential-firewall, expectation, or causal-prediction contracts.

`STATUS.md` records what is actually implemented and what CI has verified. A green ordinary CI run does not erase open items in the improvement backlog and does not substitute for the DUCK Discriminator release profile once that profile is executable.

`DONOR_AUDIT_v0.1.md` remains nonbinding research context. Donor mechanisms do not become MicroPsiDUCK requirements merely because they appear there.

## Evaluation doctrine

Normal CI and the DUCK Discriminator answer different questions.

Normal CI verifies that implemented contracts and established regressions still hold.

The DUCK Discriminator attempts to find cases where the architecture's claims are brittle, confounded, leaked, unbounded, provenance-unsafe, or overfit to friendly demonstrations.

A discriminator failure must be dispositioned through `IMPROVEMENT_BACKLOG_v0.10.md`. The preferred response is to correct the mechanism and retain the hostile test. If a discriminator gate is itself invalid, its revision requires a documented rationale rather than silent weakening.

A future v0.10 freeze should require both ordinary release CI and the current discriminator release profile, except for explicitly documented accepted limitations.

## Preserved DUCK v0.9 baseline

The promoted DUCK v0.9 implementation remains preserved on `main`.

`ARCHITECTURE_v0.9.md`, `MILESTONE_0_9.md`, and `PLANNING_PHASE_v0.9_NOTES.md` describe that previous architecture and remain useful comparison material.

The v0.10 branch is not required to keep v0.9 API identity, file layout, class hierarchy, control flow, planner implementation, renderer packet structure, or host contract. Where a v0.9 mechanism remains scientifically or behaviorally valuable, it should be tested as a property rather than preserved solely because of its historical implementation.

## Historical architecture

`ARCHITECTURE_v0.8.md` and `MILESTONE_0_8.md` preserve the first motivated prospective-agency architecture. `AGENCY_PHASE_v0.8_NOTES.md` remains historical engineering context.

`ARCHITECTURE_v0.7.md` and `MILESTONE_0_7.md` preserve the first thirty-day life-simulation architecture.

`ARCHITECTURE_v0.6.md` and `MILESTONE_0_6.md` preserve the first longitudinally regulated whole-organism baseline.

`ARCHITECTURE_v0.5.md` and `MILESTONE_0_5.md` preserve the first whole-organism FrankenDUCK integration.

`ARCHITECTURE_v0.1.md` and `MILESTONE_0_1.md` preserve the original Subjective Moment milestone. Historical documents should not be silently rewritten to describe later architecture.

The older `DUCK_Unified_Subject_Architecture_Design_Spec_v0.3` from `Azimn/persona_engine_PYTHONX` is not the current architecture. It remains donor and history material unless explicitly reintroduced.

## Development doctrine

DUCK v0.5 through v0.9 progressively established a persistent individual with autobiographical continuity, relationship trajectories, regulation, prospective agency, endogenous goals, planning, and outcome-driven change.

MicroPsiDUCK v0.10 changes the organization of cognition itself. Needs generate persistent competing motives. Motives organize associative activation and planning. Global modulation changes the operating regime of cognition. Continuous state dynamics generate endogenous events even when no language model is active.

The v0.10 phase also adds explicit prediction state. World truth, subject belief, and subject expectation remain separate authorities. Expectations mature over time, are resolved only by appropriate evidence, preserve revision history, and learn calibration from outcomes the subject actually perceived. A hidden world change cannot silently train or correct the subject's predictor.

The v0.10 phase also hardens first-person architecture. Mechanistic state may causally shape experience, but private cognition receives only an immutable `ExperientialFrame` containing approved first-person experiential prose. Private interior state is versioned and persistent. Public expression is rendered from a controlled prose-only view rather than canonical subject machinery.

The v0.10 phase modernizes selected Psi and MicroPsi principles without recreating the historical node-net and without turning an LLM into the cognitive architecture.

The new public runtime on this development branch may therefore diverge structurally from v0.9. `main` is the compatibility and historical preservation boundary.

## Future modalities

Vision, audio, touch, proprioception, interoception, avatars, robotics, XR, and richer embodiment remain future surfaces. Machine representations must cross the same experiential firewall before they become available to the simulated subject.
