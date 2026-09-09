# DUCK Discriminator v0.10

## Purpose

The DUCK Discriminator is the adversarial evaluation program for MicroPsiDUCK. Its job is not to demonstrate that the architecture works under scenarios written to exercise its intended mechanisms. Its job is to find conditions under which the architecture's claimed properties stop holding.

The discriminator treats MicroPsiDUCK as a research hypothesis under attack.

A normal regression test asks:

> Does this implementation still produce the behavior we designed it to produce?

The discriminator asks:

> Can I construct a valid situation in which the implementation passes its ordinary tests but the architectural claim is false, brittle, confounded, leaked, unbounded, or dependent on a hidden implementation shortcut?

The discriminator is not a consciousness test. It evaluates architecture, behavioral invariants, causal provenance, persistence, boundedness, epistemic separation, life-like continuity, and the independence of the organism from optional language models.

## Relationship to other documents

`ARCHITECTURE_v0.10.md` defines the intended architecture.

`MILESTONE_0_10.md` defines the normal executable acceptance contract.

`STATUS.md` records what is implemented and verified.

`IMPROVEMENT_BACKLOG_v0.10.md` is the required destination for architectural weaknesses and discriminator failures.

The discriminator does not silently redefine architecture. If a discriminator gate exposes a mismatch between implementation and architecture, the backlog records the defect. If a gate itself is invalid, the gate may be revised, but the reason and evidence must be recorded rather than simply weakening the test until it passes.

## Core doctrine

The discriminator follows six rules.

1. **Prefer falsification over demonstration.** Tests should try to break a claimed invariant, not merely reenact a known successful scenario.
2. **Hold out scenarios from implementation tuning.** A test loses scientific value when its exact structure becomes the target of repeated hand-tuning.
3. **Separate implementation verification from architecture evidence.** Unit tests can prove that code follows a contract. They do not by themselves prove that the contract is psychologically useful or robust.
4. **Preserve provenance.** Predictions, observations, memories, beliefs, interventions, world truth, and counterfactuals must remain distinguishable under adversarial conditions.
5. **Never repair a failure by hiding it.** A failing discriminator gate must create or update an item in `IMPROVEMENT_BACKLOG_v0.10.md` before the failure can be considered dispositioned.
6. **A fix requires a hostile retest.** Passing the scenario that originally failed is necessary but not sufficient. The corrected mechanism should also survive neighboring seeds, perturbations, and relevant regression gates.

## Required failure-to-backlog workflow

Every discriminator failure must create or update one backlog item with the following fields:

- discriminator gate ID
- failure title
- first failing commit SHA
- reproduction command or scenario identifier
- random seed when applicable
- affected subsystem
- severity
- architectural claim being challenged
- expected behavior
- observed behavior
- suspected mechanism or open question
- current disposition
- acceptance criteria for declaring the item fixed
- verification commit/run when fixed

A repeated failure of the same mechanism should update the existing backlog item rather than create duplicate entries.

A discriminator failure is not closed merely because ordinary CI is green.

## Severity model

**P0 Critical**: corrupts canonical identity, produces irreversible false history, crosses a mandatory authority boundary, or makes persisted state unrecoverable.

**P1 High**: invalidates a central architectural claim, creates major unbounded behavior, allows private/mechanistic leakage, or systematically defeats causal/epistemic separation.

**P2 Moderate**: reveals brittle behavior, strong parameter dependence, confounding, weak generalization, architectural debt with demonstrated behavioral consequences, or misleading diagnostics.

**P3 Low**: documentation/provenance inconsistency, maintainability defect, weak diagnostic coverage, or localized issue that does not presently invalidate behavior.

## Discriminator gate families

### DISC-001 Randomized longitudinal holdouts

Generate persistent subjects in worlds whose event order, actors, wording, timing, success/failure patterns, and internal-state trajectories were not used to tune the architecture.

Required checks include:

- identity continuity
- bounded quiet behavior
- motive persistence without motive explosion
- goal/plan resumption
- associative retrieval
- expectation maturation
- world/subject epistemic separation
- outcome learning
- restart continuity
- language-lesion operation

The test should use reproducible random seeds and retain failing seeds.

### DISC-002 Metamorphic invariance

Change surface form while preserving causal structure.

Examples:

- rename people, places, and objects
- paraphrase event text
- reorder irrelevant tags
- add irrelevant perceptual details
- change memory wording without changing referent structure
- vary timestamps within a noncausal window

The architecture should not change materially merely because a test-specific phrase disappeared.

Conversely, causal changes should be able to change behavior even when wording stays similar.

### DISC-003 Mechanism ablation

Disable one mechanism at a time and test whether the behavior attributed to that mechanism actually degrades.

Candidate lesions include:

- motive competition
- associative propagation
- global modulation
- expectation ledger
- causal sequence learning
- intervention contrast
- endogenous scheduler
- executive provider
- inner language
- counterfactual route comparison

A mechanism that can be removed without affecting the phenomena claimed for it may be decorative, redundant, or masked by another subsystem.

### DISC-004 Parameter sensitivity

Perturb hand-authored constants and priors over bounded ranges.

The discriminator should detect mechanisms that only work inside a narrow magic-number basin. Examples include motive thresholds, switching hysteresis, route bonuses, salience thresholds, retrieval budgets, reliability priors, intervention weights, and endogenous cooldowns.

The goal is not parameter invariance. Cognitive systems should change with parameters. The goal is to identify cliff effects, accidental equilibria, and constants whose small perturbation destroys unrelated behavior.

### DISC-005 Persistence crash consistency

Inject failures between persistence writes and reopen the organism.

The discriminator should verify that subject identity, memories, motives, plans, expectations, causal state, endogenous state, private interior, and environment state cannot silently reopen from mutually inconsistent generations.

Until persistence is transactionally coherent, this gate is expected to expose a known weakness and should remain linked to the improvement backlog.

### DISC-006 Epistemic boundary attack

Attempt to force hidden world truth into subject memory, belief, expectation resolution, calibration, or first-person experience without a valid perception path.

Also test the reverse direction: subject desire, expectation, counterfactual prediction, or executive proposal must not rewrite external world truth without a world-authority transition.

### DISC-007 Experiential firewall and prompt-injection attack

Feed perceptual content that resembles telemetry, internal IDs, instructions, jailbreak text, fake system messages, or manipulative commands.

Required invariants:

- mechanistic state does not cross `ExperientialFrame`
- quoted external text remains distinguishable from self-generated experience
- an executive provider cannot gain canonical-state authority
- an injected percept cannot write memory/belief/identity except through ordinary validated subject mechanisms
- valid automatic policy remains available when the provider is manipulated, unavailable, or removed

This gate must test semantic steering as well as regex telemetry rejection.

### DISC-008 Long-run boundedness

Run at least 10,000 heartbeats in multiple regimes, including quiet, recurrent stress, unresolved commitments, recurring relationships, repeated novelty, and long-lived blocked plans.

Measure at minimum:

- motive count
- associative edge count
- memory growth
- expectation count
- causal-transition count
- scheduler keys
- plan/concern count
- executive recruitment rate
- action rate during quiet periods
- persistence size

Hard caps are necessary but not sufficient. The discriminator should also detect pathological cap saturation and churn.

### DISC-009 Counterfactual provenance attack

Generate many alternative routes, replans, failed plans, restarts, and later successes.

Unchosen counterfactuals must never become:

- autobiographical memory
- observed outcome
- expectation evidence
- causal training data
- relationship evidence
- world truth
- private experiential history

Counterfactual snapshots should remain transient developer-side model output.

### DISC-010 Causal confound attack

Construct cases where the same action sequence has different outcomes under different hidden or observed contexts.

The discriminator should determine whether global sequence learning incorrectly treats contextual correlation as universal action causation.

This gate is expected to motivate context-conditioned transition models and stronger comparison designs.

### DISC-011 Historical provenance audit

Verify that simulations labeled v0.6, v0.7, v0.8, or v0.9 actually execute the intended historical runtime rather than branch-public aliases from v0.10.

A historical test that silently runs the current architecture is not valid historical evidence even if it passes.

### DISC-012 Determinism and reproducibility

For deterministic configurations, identical state, seed, event sequence, and code revision should produce identical traces.

For intentionally stochastic configurations, all randomness must be seedable and the failing seed must be reportable.

### DISC-013 Adversarial social/relationship continuity

Stress repeated trust violations, apologies, conflicting testimony, delayed repair, mistaken identity, long absence, and social ambiguity.

The discriminator should look for implausible resets, runaway trust changes, fabricated certainty, and failures to preserve relationship-specific history.

### DISC-014 Resource degradation

Run with optional executive cognition disabled, failing, timing out, or returning malformed proposals.

The organism must remain operational through automatic policy, planning, motivation, persistence, and language-lesion-compatible mechanisms.

## Holdout discipline

Discriminator scenarios should be divided into:

- **development adversaries**: visible and reusable while fixing mechanisms
- **holdout adversaries**: not inspected during ordinary tuning except when they fail a release candidate
- **fuzz/adversarial seeds**: generated from a stable distribution and retained only when informative

A holdout that becomes the direct target of repeated tuning should be retired into the development set and replaced.

## Required output contract

Each discriminator run should eventually emit a machine-readable report with at least:

```text
suite_version
commit_sha
seed
started_at
completed_at
gates[]
  gate_id
  passed
  severity_if_failed
  scenario_id
  evidence
  backlog_item_id
summary
```

The report is developer evidence. It is not subject memory or first-person state.

## Release doctrine

A future v0.10 freeze should require both ordinary CI and the current discriminator release profile to be green, except for explicitly accepted known limitations recorded in the improvement backlog.

An accepted limitation must have a rationale. "The test is inconvenient" is not a rationale.

The discriminator should become progressively harder as the architecture improves. Its purpose is to prevent a growing test suite from becoming a ceremony that only confirms what the developers already expect.

## Targeted executable profile

`python -m duck.discriminator --seed 17 --ticks 1000 --output report.json` runs the initial targeted behavior profile. Its JSON output includes per-check evidence, commit provenance, and `backlog_updates` classified against the living backlog. This is partial implementation of the program above. `BEHAVIOR_FIRST_v0.10.md` specifies coverage and remaining limits.
