# DUCK Integrated Milestone 0.5

This milestone intentionally abandons the one-mechanism-at-a-time research cadence for one integration sprint. The purpose is to assemble a coherent end-to-end simulated individual from mechanisms already explored across the user's prior prototypes, then evaluate and simplify later.

The milestone is complete when the repository contains an executable persistent subject with first-person access, lived memory, world/belief separation, relationships, commitments, homeostatic motivation, endogenous heartbeat, action selection, action/outcome learning, a path-dependent adaptive substrate, optional LLM inner cognition, optional LLM expression, deterministic fallback, persistence, a CLI, and regression tests for the principal authority boundaries.

The implementation must preserve one non-negotiable invariant: private cognition and expression may be affected by mechanistic state, but they may not inspect raw numeric psychological telemetry directly.

The reference interactive surface is:

```bash
python -m pip install -e '.[test]'
duck --root ./duck_state chat
```

A generic model-backed mode is available through `DUCK_LLM_ENDPOINT`, `DUCK_LLM_MODEL`, and optionally `DUCK_LLM_API_KEY`, then:

```bash
duck --root ./duck_state --llm chat
```

This interface is provider-neutral and is not an Ollama milestone.

The deterministic demonstration is:

```bash
duck --root ./demo_state demo
```

The critical tests are paired-history divergence, first-person telemetry isolation, objective-world versus subject-belief separation, commitment consequence, outcome-dependent learning, language-lesion survival, autonomous heartbeat behavior, durable subject identity across restart, and approved LLM packet isolation.

Vision, audio, robotics, XR, and elaborate avatar presentation are not required for this integrated milestone. The architecture is deliberately prepared for them by keeping the subject-access firewall modality-neutral, but the integration sprint focuses on the cognitive organism and conversational host.
