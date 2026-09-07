# DUCK

DUCK is an experimental persistent human-like subject simulator.

It does not claim phenomenal consciousness. The engineering goal is to create a believable continuing individual whose present cognition depends on limited first-person access, lived history, motivation, memory, belief, relationships, commitments, action, consequence, learning, recovery, reinterpretation, unfinished intentions, self-generated goals, and revisable plans rather than on a language model pretending to contain all of those things inside one prompt.

The governing rules are:

> The machinery may know numbers. The subject does not.

> What happens to me changes the me who encounters what happens next.

> An intention may persist without continuously occupying attention, and may later influence action without being reissued as an external instruction.

> A goal may arise from lived experience, and a failed plan may change what I try next.

## Endogenous planning v0.9 candidate

Version 0.9 keeps the v0.8 motivated prospective-agency organism and adds bounded endogenous goal formation, state-sensitive counterfactual route choice, hierarchical subgoals, and outcome-driven replanning.

```text
lived experience
      |
      v
motivation-sensitive goal formation
      |
      v
persistent goal root
      |
      v
alternative routes
      |
      v
current subgoal
      |
      v
v0.8 motivated prospective agency
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
action -> outcome
          |
          +-> advance plan
          +-> replan
          +-> complete / abandon
```

The LLM remains optional. It may participate in bounded private cognition, interpretation, route proposal, and expression, but it does not own goal formation, canonical plan state, action outcome, or the continuing subject. Raw route scores, plan IDs, subgoal indexes, priority values, trust floats, affect magnitudes, private persistence tags, retrieval scores, and latent values remain outside first-person access.

The v0.9 tests deliberately run planning with inner speech disabled. They test whether meaningful experience can create a goal without an explicit task command, whether different risk states can prefer different routes to the same objective, whether a multi-step route advances through child intentions, whether failed action changes the route, whether active planning survives restart, whether ordinary experience avoids false goal creation, and whether completed plans stop producing behavior.

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
python -m duck.planning_evaluation
python -m duck.planning_simulation --out-dir simulation_results/planning-v09

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

Model swapping and local/offline provider coverage remain possible but are not current research priorities. The present priority is longitudinal organism simulation, grounded endogenous agency, and believable persistent subjectivity.

## Documentation authority

The current architecture candidate is `docs/ARCHITECTURE_v0.9.md`.

The current milestone candidate is `docs/MILESTONE_0_9.md`.

`docs/INDEX.md` defines document authority, `docs/STATUS.md` records implementation evidence, `docs/PLANNING_PHASE_v0.9_NOTES.md` records nonbinding engineering observations, and `docs/DONOR_AUDIT_v0.1.md` records the nonbinding donor survey.

Earlier architecture documents remain preserved as history rather than silently rewritten.