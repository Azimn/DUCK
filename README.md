# DUCK

DUCK is a clean experimental implementation of a persistent human-like subject simulation.

The project does not attempt to prove or claim phenomenal consciousness. Its current engineering goal is narrower and testable: construct a believable continuing individual whose cognition is constrained by a first-person point of access rather than by omniscient access to implementation state.

## Milestone 0.1: The Subjective Moment

The first invariant is simple:

> The machinery may know numbers. The subject does not.

Raw mechanistic state is projected through a `SubjectAccessFirewall` into a bounded `SubjectiveMoment`. Private cognition receives the SubjectiveMoment, never raw psychological telemetry.

```text
mechanistic state
      |
      v
subject-access firewall
      |
      v
first-person subjective moment
      |
      v
optional inner cognition
      |
      v
choice / action
```

Example:

```text
developer state:
    recognition confidence = 0.64

subject access:
    "I think that's Sarah."
```

The current code is intentionally small. The older `Azimn/persona_engine_PYTHONX` repository remains a donor and research archive rather than a dependency.

## Run tests

```bash
python -m pip install -e '.[test]'
python -m pytest
```

## Documentation authority

The current binding architecture is `docs/ARCHITECTURE_v0.1.md`.

The current executable milestone is `docs/MILESTONE_0_1.md`.

`docs/INDEX.md` defines documentation authority and explicitly separates current DUCK from historical donor documents. `docs/STATUS.md` records what is actually implemented and verified.

Run the documentation/scope guard directly with:

```bash
python tools/check_docs.py
```
