# MicroPsiDUCK

MicroPsiDUCK v0.10 is an experimental persistent motivated-cognition architecture built from the useful continuity mechanisms developed in DUCK and selected functional ideas from Psi and MicroPsi.

It does not claim phenomenal consciousness. The engineering target is a believable continuing simulated individual whose cognition is organized by internal needs and motives, whose operating regime changes with condition, whose memories and goals can become available through associative activation, and whose first-person access remains narrower than the machinery implementing it.

The central rules are:

> The machinery may know numbers. The subject does not.

> Needs create motives. Motives organize cognition.

> Internal state changes how cognition operates, not merely which action gets the largest score.

> The continuously existing organism lives in persistent system state, not inside an LLM invocation.

> What happens to the subject must be able to change the subject who encounters the next moment.

## v0.10 architecture

The development control spine is:

```text
world / body / social context
          |
          v
continuous state dynamics
          |
          v
appraisal + needs
          |
          v
motives -> motive competition
          |
          v
selected organizing motive
       /        \
      v          v
associative    global
activation     modulation
      \          /
       v        v
     cognitive field
          |
          v
attention / opportunity
      /           \
     v             v
automatic       executive
policy          cognition
     \             /
      v           v
       intention
          |
          v
        action
          |
          v
        outcome
          |
          v
learning + changed subject
```

Version 0.9 remains preserved on `main` as the previous DUCK baseline. The v0.10 branch is a structural redesign and is not required to preserve v0.9 API identity, class hierarchy, planner implementation, host contract, or renderer packet layout.

## Experiential firewall

Mechanistic state may contain numeric need values, motive strengths, graph activations, edge weights, route scores, confidence values, tags, identifiers, and latent state.

Private cognition does not receive those representations.

The v0.10 introspective contract is `ExperientialFrame`, an immutable object containing only approved first-person experiential prose. A structured diagnostic representation may exist internally, but it does not cross the private-cognition boundary.

Private interior state is versioned and persistent across restart. Public expression is produced through a renderer that reads controlled prose-only private context. Public interaction results and ordinary event journals do not expose private thought or private experiential state.

## LLM role

An LLM is optional. It may be recruited for bounded executive cognition, interpretation, or expression, but it is not the continuing subject and does not own canonical motives, memories, beliefs, relationships, goals, plans, or outcomes.

The architecture must continue to function with inner language disabled.

## Run

```bash
python -m pip install -e '.[test]'
python -m pytest
python -m duck.evaluation
python -m duck.regulation_evaluation
python -m duck.planning_evaluation
python -m duck.planning_simulation --out-dir simulation_results/planning-v09

micropsiduck --root ./duck_state status
micropsiduck --root ./duck_state chat
micropsiduck --root ./demo_state demo
```

The historical `duck` command remains an alias for the same v0.10 CLI on this branch.

For an OpenAI-compatible chat-completions provider:

```bash
export DUCK_LLM_ENDPOINT="https://provider.example/v1"
export DUCK_LLM_MODEL="model-name"
export DUCK_LLM_API_KEY="optional-key"
micropsiduck --root ./duck_state --llm chat
```

## Documentation authority

The current structural architecture is `docs/ARCHITECTURE_v0.10.md`.

The current acceptance contract is `docs/MILESTONE_0_10.md`.

The experiential data boundary is defined by `docs/EXPERIENTIAL_FIREWALL_v0.10.md`.

`docs/INDEX.md` defines document authority, `docs/STATUS.md` records implementation evidence, and `docs/MICROPSI_MODERNIZATION_v0.10.md` records nonbinding donor interpretation.

`docs/ARCHITECTURE_v0.9.md` and `docs/MILESTONE_0_9.md` remain preserved history for the previous DUCK baseline on `main`.
