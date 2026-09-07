# DUCK

DUCK is an experimental persistent human-like subject simulator.

It does not claim phenomenal consciousness. The engineering goal is to create a believable continuing individual whose present cognition depends on limited first-person access, lived history, motivation, memory, belief, relationships, commitments, action, consequence, learning, and recovery rather than on a language model pretending to contain all of those things inside one prompt.

The two governing rules are:

> The machinery may know numbers. The subject does not.

> What happens to me changes the me who encounters what happens next.

## Integrated v0.6 candidate

Version 0.6 keeps the whole-organism FrankenDUCK integration and adds long-horizon regulation discovered through simulation testing.

```text
world / user / time
        |
        v
mechanistic subject
        |
        v
memory + appraisal + motivation + continuity + adaptive state
        |
        v
regulated action ecology
        |
        v
subject-access firewall
        |
        v
first-person SubjectiveMoment
        |
        v
optional inner cognition
        |
        v
expression / action
        |
        v
outcome
        |
        v
learning + residue + recovery
        |
        v
changed next subject
```

The LLM is optional. When enabled, it can participate in private first-person cognition and expression, but it only receives approved subject-accessible state. It never receives raw trust floats, affect magnitudes, memory retrieval scores, latent vectors, or other developer telemetry.

The current simulation work specifically tests whether history remains causal without causing permanent emotional saturation, whether quiet-time drives remain bounded, whether memory affects the present without explicit recall requests, whether relationships can be damaged and partially repaired, whether the same subject survives restart, and whether cognition/action continue with inner language disabled.

## Run

```bash
python -m pip install -e '.[test]'
python -m pytest
python -m duck.evaluation
python -m duck.regulation_evaluation
python -m duck.simulation_lab_v06 --out-dir simulation_results/v06

duck --root ./duck_state status
duck --root ./duck_state chat
duck --root ./demo_state demo
```

For any OpenAI-compatible chat-completions provider:

```bash
export DUCK_LLM_ENDPOINT="https://provider.example/v1"
export DUCK_LLM_MODEL="model-name"
export DUCK_LLM_API_KEY="optional-key"
duck --root ./duck_state --llm chat
```

Model swapping and local/offline provider coverage remain possible but are not current research priorities. The present priority is longitudinal organism simulation.

## Documentation authority

The current integrated architecture candidate is `docs/ARCHITECTURE_v0.6.md`.

The current integrated milestone is `docs/MILESTONE_0_6.md`.

`docs/INDEX.md` defines document authority, `docs/STATUS.md` records implementation evidence, and `docs/DONOR_AUDIT_v0.1.md` records the nonbinding donor survey.

Earlier architecture documents remain preserved as history rather than silently rewritten.
