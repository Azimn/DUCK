# DUCK Current Status

Current architecture candidate: `docs/ARCHITECTURE_v0.8.md`

Current milestone candidate: `docs/MILESTONE_0_8.md`

Branch: `agency-lab-v0.8`

## Integrated implementation

DUCK v0.8 retains the v0.7 life-simulation organism and adds motivated prospective agency in `duck/living_v08.py`. The persistent host uses the v0.8 candidate on this branch while `duck/living_v07.py`, `duck/living_v06.py`, and `duck/living.py` remain preserved historical implementation layers.

The organism contains persistent subject identity, affect and homeostatic needs, relationship trajectories, autobiographical memory with provenance, objective world facts separated from subject beliefs, commitments, lived-consequence residue, action selection, action/outcome separation, outcome-dependent learned affordances, a small path-dependent adaptive latent trace, endogenous heartbeat, optional first-person inner cognition, optional bounded model-assisted semantic appraisal, optional model-backed expression, deterministic fallbacks, atomic JSON state persistence, an append-only JSONL host journal, UTC timestamps, and Swatch Internet Time / Beat Time stamps.

Version 0.8 adds a persistent field of prospective concerns. Multiple unfinished intentions can coexist, compete, wait until a later time, require relevant context, defer under low energy or threat, survive interruption and state restart, resume later, link to existing commitments, and stop competing when satisfied or abandoned.

The subject-access firewall remains mandatory. Model-backed private cognition and expression are constructed exclusively from qualitative first-person state. Raw mechanistic numbers, prospective priority/urgency metadata, internal concern identifiers, cooldowns, and private persistence tags remain developer diagnostics.

No donor package is a runtime dependency.

## Prospective concern implementation

The current prototype deliberately encodes prospective metadata on provenance-bearing `SELF_REFLECTION` memory records instead of introducing a second canonical goal store. This preserves one subject authority and lets the existing serialization path carry prospective state across restart. The encoding is provisional and should not be mistaken for a psychological claim or permanent storage format.

A concern can carry a preferred action, priority, urgency, due point, not-before point, minimum energy, required context, blocking context, attempt/deferral history, short cooldown, lifecycle state, and optional commitment link. Those fields influence mechanistic salience but are not introspectively exposed.

Selection is motivational rather than FIFO. Due time can increase salience but does not itself execute the task. Current curiosity, affiliation, energy, fear, context, competing concerns, prior deferrals, and prior attempts can alter whether the concern becomes actionable.

## Focused agency evaluation

`duck/agency_evaluation.py` exercises spontaneous pursuit without a new prompt, state-roundtrip persistence, competition between weak and strong concerns, low-energy deferral and later resumption, safety override, context gating, interruption, satisfaction, abandonment, commitment follow-up, false-goal controls, and multi-concern boundedness. All focused probes run with private inner language disabled.

The multi-concern test deliberately treats silence as healthy. Long runs of `wait` are not classified as pathological perseveration. The boundedness test instead looks for repetitive active behavior while requiring that more than one active intention type can emerge when several concerns compete.

## Long-horizon agency simulation

`duck/agency_simulation.py` runs one persistent Aster through an extended motivated-agency scenario. The subject begins with several unrelated unfinished intentions plus a social commitment. A garden goal is blocked by threat and later resumes when the environment is safe. A delayed map intention survives an interruption and remains dormant until its not-before boundary passes. A commitment-linked follow-up becomes endogenous around the due period and retires when Morgan follows through. An impossible tunnel goal is abandoned. A greenhouse goal is deferred under low energy, survives process restart, and resumes after recovery. Later, a high-priority social concern competes against a low-priority curiosity. After all concerns are resolved, the simulation continues for 60 quiet cycles to check for runaway residual agency.

The entire scenario runs with inner speech disabled. It checks every generated `SubjectiveMoment` for numeric telemetry and private concern metadata. The simulated subject can therefore maintain and act on unfinished intentions without an LLM narrating or owning the executive process.

## Verified evidence

Implementation head `f821d1838103678a9727d5d061e4d21c52363559` passed GitHub Actions workflow `34156217216` on Python 3.11 and Python 3.12. The full pytest suite, documentation contract as it existed at that head, v0.6 regulation evaluation, original architectural evaluation, preserved v0.5/v0.6 simulations, v0.7 thirty-day longitudinal life simulation, focused v0.8 agency evaluation, and long-horizon v0.8 agency simulation all passed.

The green v0.8 implementation demonstrates that a prospective concern can become actionable without a new user prompt, can survive serialization/reconstruction, can lose to a more motivated concern, can be deferred by insufficient energy or safety pressure, can wait for context, can survive an interruption, can be satisfied or abandoned, and can be retired automatically when its linked commitment resolves.

During development, the expanded tests exposed useful failures. A weak delayed map intention originally failed to resume because its motivation no longer cleared the salience threshold after many quiet cycles. Rather than lowering the global threshold simply to make the scenario pass, the simulation was corrected so the map represented a meaningfully motivated delayed intention. Earlier versions also allowed a linked commitment follow-up to remain open while cooling down after the underlying commitment had already resolved; lifecycle resolution was moved ahead of cooldown gating.

## Relationship to v0.7

The v0.7 thirty-day longitudinal life simulation remains a mandatory regression gate. v0.8 does not replace relationship development, epistemic integrity, homeostatic recovery, adaptive action learning, or first-person reinterpretation. It adds a new temporal dimension: the same continuing subject can now be organized partly by things it has not finished yet.

The central research question remains what is obviously fake when language fluency is not allowed to hide the architecture. For v0.8 the specific question is whether DUCK behaves like a subject carrying unfinished intentions, rather than a chatbot waiting for the next message or a reminder scheduler executing a queue.

Passing the current tests establishes bounded motivated prospective agency under the tested scenarios. It does not establish phenomenal consciousness, human-equivalent executive function, unrestricted autonomy, or general psychological validity.

## Deliberately unfinished surfaces

Automatic high-level goal formation from unconstrained natural experience, hierarchical planning, counterfactual imagination, theory-of-mind planning, habits, skill composition, richer real-time opportunity detection, model swapping, real camera/audio sensing, robotics, XR embodiment, avatar animation, voice interruption, long-duration human evaluation, and a polished desktop/mobile shell remain future work.

The v0.7, v0.6, v0.5, and v0.1 documents remain preserved as historical architecture. The older `DUCK_Unified_Subject_Architecture_Design_Spec_v0.3` remains non-current donor material.
