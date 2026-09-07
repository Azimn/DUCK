# DUCK

DUCK is an experimental persistent human-like subject simulator.

It does not claim phenomenal consciousness. The engineering goal is to create a believable continuing individual whose present cognition depends on limited first-person access, lived history, motivation, memory, belief, relationships, commitments, action, consequence, learning, recovery, reinterpretation, and unfinished intentions rather than on a language model pretending to contain all of those things inside one prompt.

The governing rules are:

> The machinery may know numbers. The subject does not.

> What happens to me changes the me who encounters what happens next.

> An intention may persist without continuously occupying attention, and may later influence action without being reissued as an external instruction.

## Motivated prospective agency v0.8 candidate

Version 0.8 keeps the v0.7 thirty-day life-simulation organism and adds a persistent field of unfinished intentions. Prospective concerns can coexist, compete, defer under low energy or threat, wait for relevant context, survive interruption and restart, resume later, link to commitments, and eventually be satisfied or abandoned.

```text
lived experience / self-reflection / commitment
                    |
                    v
          unfinished intentions
                    |
       time + context + motivation
       safety + energy + competition
                    |
                    v
             motivated salience
                    |
          defer / pursue / abandon
                    |
                    v
             selected intention
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
               action / outcome
                    |
                    v
        learning + resolution + next subject
```

The LLM remains optional. It may participate in bounded private cognition and expression, but it does not own the prospective concern field and never receives raw priority values, urgency values, internal concern IDs, trust floats, affect magnitudes, memory retrieval scores, latent vectors, or other developer telemetry.

The v0.8 tests distinguish motivated prospective agency from reminder scheduling. Time can affect salience, but time does not directly execute a task. Current energy, safety, motivation, context, competing concerns, prior attempts, and commitment state can all change whether an unfinished intention becomes actionable.

## Run

```bash
python -m pip install -e '.[test]'
python -m pytest
python -m duck.evaluation
python -m duck.regulation_evaluation
python -m duck.simulation_lab_v06 --out-dir simulation_results/v06
python -m duck.life_simulation --out-dir simulation_results/life-v07
python -m duck.agency_evaluation
python -m duck.agency_simulation --out-dir simulation_results/agency-v08

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

Model swapping and local/offline provider coverage remain possible but are not current research priorities. The present priority is longitudinal organism simulation, motivated endogenous agency, and believable persistent subjectivity.

## Documentation authority

The current architecture candidate is `docs/ARCHITECTURE_v0.8.md`.

The current milestone candidate is `docs/MILESTONE_0_8.md`.

`docs/INDEX.md` defines document authority, `docs/STATUS.md` records implementation evidence, and `docs/DONOR_AUDIT_v0.1.md` records the nonbinding donor survey.

Earlier architecture documents remain preserved as history rather than silently rewritten.
