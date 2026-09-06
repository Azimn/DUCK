# DUCK Documentation Authority

This file defines which documents govern the current `Azimn/DUCK` repository.

## Current binding design

The current architecture contract is [`ARCHITECTURE_v0.1.md`](ARCHITECTURE_v0.1.md).

The current executable milestone and its acceptance conditions are [`MILESTONE_0_1.md`](MILESTONE_0_1.md).

These two documents are binding for the current milestone. If the architecture changes, create a new versioned architecture document rather than silently rewriting `ARCHITECTURE_v0.1.md`.

## Current status

[`STATUS.md`](STATUS.md) records what is actually implemented, what has been verified, and what experiment is next. Unlike versioned architecture snapshots, `STATUS.md` is intentionally updated in place as evidence changes.

## Context and provenance

[`PROVENANCE.md`](PROVENANCE.md) records the relationship between this repository and earlier research.

The earlier `Azimn/persona_engine_PYTHONX` repository is a donor archive and historical laboratory. Documents in that repository, including earlier broad DUCK architecture specifications, Wayfarer architecture locks, portability plans, sensory/embodiment plans, and subjective-access drafts, are historical or donor material only. They are not binding on this repository unless a specific mechanism is deliberately reintroduced here and tested against a current DUCK failure.

In particular, the older `DUCK_Unified_Subject_Architecture_Design_Spec_v0.3` is not the current architecture of `Azimn/DUCK`.

## Scope discipline

Nothing enters current DUCK merely because an older branch or framework contained it.

A mechanism should enter the active architecture only when a concrete behavioral experiment exposes a failure that the current system cannot express cleanly, and the new mechanism has a falsifiable acceptance test.

Future modality notes are hypotheses, not commitments. Vision, audio, touch, proprioception, vestibular sensing, interoception, avatars, robotics, XR, and multimodal binding remain nonbinding until an actual experiment or product surface requires them.

## Repository hygiene rule

`tools/check_docs.py` enforces the current documentation contract. The normal test suite and GitHub CI run that guard so stale document authority or accidental scope expansion is caught as a test failure rather than discovered later in review.
