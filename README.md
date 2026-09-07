# DUCK

DUCK is an experimental persistent human-like subject simulator.

It does not claim phenomenal consciousness. The engineering goal is to create a believable continuing individual whose present cognition depends on limited first-person access, lived history, motivation, memory, belief, relationships, commitments, action, consequence, learning, recovery, and reinterpretation rather than on a language model pretending to contain all of those things inside one prompt.

The two governing rules are:

> The machinery may know numbers. The subject does not.

> What happens to me changes the me who encounters what happens next.

## Life-simulation v0.7 candidate

Version 0.7 keeps the regulated v0.6 whole-organism architecture and adds refinements discovered by running one persistent subject through a deterministic thirty-day simulated life.

```text
world / user / time
        |
        v
persistent mechanistic subject
        |
        v
memory + appraisal + motivation + continuity + adaptive state
        |
        v
contextual action ecology
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
learning + relationship change + recovery
        |
        v
reinterpretation + changed next subject
```

The LLM is optional. When enabled, it can participate in private first-person cognition and expression, but it only receives approved subject-accessible state. It never receives raw trust floats, affect magnitudes, memory retrieval scores, latent vectors, or other developer telemetry.

The v0.7 life simulation specifically tests recurring relationships, promises and disappointment, later repair, hidden world truth versus subjective belief, false testimony followed by direct contradictory evidence, repeated action/outcome learning, long quiet periods, multiple process restarts, bounded homeostasis, and first-person reinterpretation of mixed relationship history.

## Run

```bash
python -m pip install -e '.[test]'
python -m pytest
python -m duck.evaluation
python -m duck.regulation_evaluation
python -m duck.simulation_lab_v06 --out-dir simulation_results/v06
python -m duck.life_simulation --out-dir simulation_results/life-v07

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

Model swapping and local/offline provider coverage remain possible but are not current research priorities. The present priority is longitudinal organism simulation and believable persistent subjectivity.

## Documentation authority

The current architecture candidate is `docs/ARCHITECTURE_v0.7.md`.

The current milestone candidate is `docs/MILESTONE_0_7.md`.

`docs/INDEX.md` defines document authority, `docs/STATUS.md` records implementation evidence, and `docs/DONOR_AUDIT_v0.1.md` records the nonbinding donor survey.

Earlier architecture documents remain preserved as history rather than silently rewritten.
