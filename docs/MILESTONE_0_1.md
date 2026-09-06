# Milestone 0.1: The Subjective Moment

## Purpose

Establish the smallest executable DUCK that proves a simulated subject can be causally affected by numeric internal state without being given direct access to that numeric state.

This milestone deliberately avoids memory systems, persistence, cameras, microphones, model APIs, elaborate embodiment, cartridges, and portability layers. Those mechanisms enter only when a concrete test requires them.

## Acceptance conditions

Private cognition must never receive raw float-valued psychological telemetry.

Changing mechanistic magnitude must be able to change the qualitative first-person projection.

Recognition confidence must appear to the subject as ordinary uncertainty such as "I think that's Sarah," not as a percentage or score.

A hidden computational cause may remain introspectively unavailable even while it influences the subject.

Inner speech must be optional. A SubjectiveMoment must still be capable of influencing action when no sentence is generated.

Developer diagnostics may retain raw mechanistic values, but those diagnostics must be a separate object from the SubjectiveMoment.

## Current implementation

`duck/mechanics.py` defines developer-visible mechanistic input.

`duck/access.py` implements `SubjectAccessFirewall`.

`duck/subjective.py` defines the subject-accessible representation.

`duck/cognition.py` defines a private cognition protocol and deterministic first-person baseline.

`duck/runtime.py` proves the developer and subject views can coexist without sharing authority.

`tests/test_subjective_access.py` attacks the boundary directly.

## What comes next

Do not add another subsystem because it sounds cognitively plausible.

Run behavioral experiments against this minimal kernel. The next mechanism should be selected by the first important failure that cannot be expressed cleanly with the current architecture.

Likely future candidates include lived memory provenance, prospective commitments, objective-world versus subjective-belief separation, temporal continuity, and learned consequence. None is automatically part of Milestone 0.2.
