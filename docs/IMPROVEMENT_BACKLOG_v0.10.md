# MicroPsiDUCK v0.10 Improvement Backlog

## Purpose

This is the living engineering and research backlog for weaknesses that can materially improve MicroPsiDUCK v0.10.

It is intentionally separate from `STATUS.md`.

`STATUS.md` answers: **What exists and what has been verified?**

This document answers: **What is weak, risky, incomplete, misleading, or known to fail, and what would count as fixing it?**

The DUCK Discriminator defined in `DUCK_DISCRIMINATOR_v0.10.md` must add or update entries here whenever it finds a meaningful failure.

`IMPROVEMENT_LOOP_v0.10.md` defines the remediation-first working order. Known high-priority weaknesses are fixed with targeted hostile verification before expensive broad discriminator discovery.

A green ordinary CI run does not automatically close an item in this backlog.

## Status values

- **OPEN**: confirmed weakness or planned hardening work
- **INVESTIGATING**: mechanism is being isolated
- **IN PROGRESS**: implementation work has begun
- **VERIFYING**: candidate fix exists and adversarial verification is running
- **BLOCKED**: cannot proceed until another item or dependency changes
- **ACCEPTED LIMITATION**: deliberately not fixed for this milestone, with rationale
- **FIXED**: acceptance criteria passed and verification evidence recorded

## Priority values

- **P0 Critical**: canonical-state corruption, irreversible false history, mandatory authority-boundary violation, or unrecoverable persistence
- **P1 High**: central architecture claim invalidated, major leakage/unboundedness, or systematic epistemic/causal failure
- **P2 Moderate**: brittleness, strong confounding, parameter cliffs, demonstrated architecture debt, or misleading evidence
- **P3 Low**: documentation, provenance, diagnostics, or maintainability defect without current major behavioral consequence

## Working rule

Every item must contain enough information that a future contributor can answer four questions without reconstructing the entire conversation that discovered it:

1. What is wrong or risky?
2. Why does it matter architecturally?
3. What evidence exposed it?
4. What exact evidence would let us call it fixed?

---

## IMP-001 Cross-file persistence is not transactionally coherent

**Status:** FIXED  
**Priority:** P1  
**Affected subsystem:** persistence / host / continuity  
**Discriminator gates:** DISC-005  
**Source:** adversarial architecture review, 2026-09-09

### Problem

The previous host atomically replaced individual JSON files, but the organism was persisted across multiple files including canonical subject state, motivated cognition, endogenous scheduler state, expectations, causal state, environment state, and private interior state. A crash between file replacements could therefore reopen a mixture of generations.

### Resolution

The current public host now commits one generation through `SnapshotStore` in `persistence_v010.py`.

A save stages every current component in a generation directory, records SHA-256 hashes in generation metadata, atomically renames the complete staged directory, and only then atomically replaces `snapshot_manifest_v010.json`. The manifest replacement is the persistence commit point.

Root JSON files remain compatibility mirrors for existing tools and tests, but are written only after the transactional commit and are no longer authoritative once a snapshot manifest exists.

On reopen, the host validates the committed generation and component hashes. If the newest committed generation is corrupt, it falls back to the most recent earlier valid committed generation rather than mixing root mirrors or partial files.

Legacy pre-snapshot root state remains readable and migrates to transactional persistence on the next save.

### Targeted hostile verification

`tests/test_transactional_persistence_v010.py` injects simulated process failure after each staged canonical component, after generation metadata, after generation rename, and immediately after manifest commit.

The suite also verifies:

- every pre-manifest crash reopens the previous complete generation
- a crash immediately after manifest replacement reopens the new complete generation
- tampered root compatibility mirrors cannot override committed snapshot authority
- a corrupted newest generation falls back to the prior valid generation
- legacy root persistence migrates cleanly
- subject, expectation, causal, environment, and private-interior state remain generation-consistent in the crash scenarios

### Verification evidence

Implementation commits:

- `0545709c007f12e095949523bb00423634a81b9d` added the transactional snapshot substrate
- `b5326ae881f3e28549777579ef97913962f20c86` integrated snapshot authority into the current public host
- `6a9adaf64b69224f4b4095b80e67ff4ed5ad2f64` added targeted crash-consistency tests

CI run #272 passed the targeted crash suite, full pytest suite, v0.10 longitudinal simulation, and all configured regression/evaluation suites on Python 3.11 and Python 3.12.

### Residual note

The append-only developer/event journal is not canonical subject state and is not part of the transactional snapshot. If the journal later becomes replay authority rather than diagnostic history, it will need an explicit generation/commit relationship rather than being assumed transactionally equivalent to the canonical organism snapshot.

---

## IMP-002 Authoritative world truth still physically inhabits SubjectState

**Status:** OPEN  
**Priority:** P1  
**Affected subsystem:** environment / epistemic authority  
**Discriminator gates:** DISC-006  
**Source:** adversarial architecture review, 2026-09-09

### Problem

Hidden world changes are correctly prevented from becoming subject perception or expectation evidence, but authoritative `world_facts` are still mutated through the subject state object.

### Why it matters

The architecture conceptually separates WORLD from SUBJECT. Keeping authoritative external truth inside `SubjectState` weakens that boundary and increases the chance that later code accidentally treats omniscient host facts as subject-accessible facts.

### Improvement direction

Move authoritative world facts into environment/world state. Subject state should contain beliefs, remembered percepts, and other subject-owned representations only.

### Fixed when

- external truth has a separate canonical store
- hidden world mutation never writes subject-owned state
- perception explicitly transfers only allowed evidence into subject processing
- DISC-006 cannot force hidden truth into memory, belief, expectations, calibration, or experience

---

## IMP-003 v0.10 composition is becoming an inheritance tower

**Status:** OPEN  
**Priority:** P2  
**Affected subsystem:** runtime composition / maintainability / version provenance  
**Discriminator gates:** DISC-003, DISC-011  
**Source:** adversarial architecture review, 2026-09-09

### Problem

The current public organism is assembled through multiple subclass layers over historical planning/runtime classes. Similar layering exists in the host stack.

Development has already exposed dynamic-dispatch and version-binding regressions.

### Why it matters

Inheritance makes it increasingly difficult to identify which layer owns a behavior and can cause historical tests to execute current behavior unintentionally.

### Improvement direction

Move toward explicit composition/orchestration of motivated control, planning, expectation, causal learning, endogenous dynamics, and executive recruitment. Preserve historical runtimes as explicit adapters rather than superclass implementation dependencies where practical.

### Fixed when

- major v0.10 subsystems have explicit ownership interfaces
- current runtime behavior can be traced without relying on deep method override chains
- historical harnesses are explicitly version-bound
- mechanism ablation can disable a subsystem cleanly without monkey-patching superclass behavior

---

## IMP-004 Experiential firewall is structurally strong but semantically under-specified

**Status:** OPEN  
**Priority:** P1  
**Affected subsystem:** experiential firewall / executive boundary / security  
**Discriminator gates:** DISC-007, DISC-014  
**Source:** adversarial architecture review, 2026-09-09

### Problem

`ExperientialFrame` enforces a prose-only boundary and rejects obvious telemetry patterns, but syntactically valid prose can still be non-experiential, authoritative, manipulative, or prompt-injection-like. Perceived external language can also enter the experiential material delivered to an executive provider.

### Why it matters

The intended guarantee is stronger than "contains strings instead of floats." The subject should experience percepts without confusing quoted external instructions with self-generated cognition or substrate authority.

### Improvement direction

Add provenance-aware experiential atoms before final prose rendering, distinguish perceived quotation from self-generated experience, and adversarially test semantic prompt injection. Keep the executive proposal non-authoritative.

### Fixed when

- hostile perceptual text cannot acquire canonical authority
- externally quoted instructions are distinguishable from self-generated intention
- semantic telemetry/instruction attacks are rejected or safely represented even when they contain no regex-detectable numeric telemetry
- automatic policy remains valid with a compromised/failing executive provider
- DISC-007 and DISC-014 pass

---

## IMP-005 Hand-tuned constants may encode too much designer intelligence

**Status:** OPEN  
**Priority:** P2  
**Affected subsystem:** motive arbitration / endogenous dynamics / route scoring / causal weighting  
**Discriminator gates:** DISC-004  
**Source:** adversarial architecture review, 2026-09-09

### Problem

Motive thresholds, route features, salience cutoffs, utility bonuses, reliability priors, causal weights, and cooldown values are extensively hand-authored.

### Why it matters

This is acceptable in a prototype, but convincing behavior may partly reflect careful tuning rather than robust architecture. A mechanism that collapses under a small parameter perturbation is not yet strong evidence for the mechanism itself.

### Improvement direction

Create systematic parameter-sensitivity sweeps and identify cliff effects. Separate constants that encode domain semantics from constants that merely compensate for another subsystem.

### Fixed when

- core claimed behaviors survive reasonable parameter neighborhoods
- sensitive parameters have documented causal roles
- no unrelated behavioral invariant depends on a narrow magic-number basin
- DISC-004 reports acceptable robustness ranges

---

## IMP-006 Associative graph uses strongest-path style propagation rather than convergent activation

**Status:** OPEN  
**Priority:** P2  
**Affected subsystem:** associative activation  
**Discriminator gates:** DISC-003, DISC-004  
**Source:** adversarial architecture review, 2026-09-09

### Problem

Current spreading activation keeps a stronger propagated value when multiple paths reach the same target rather than accumulating converging support from several weak but jointly relevant sources.

### Why it matters

This can underrepresent classic associative convergence and makes the graph closer to bounded strongest-path retrieval than a full spreading-activation field.

### Improvement direction

Evaluate additive or normalized convergent activation, inhibitory links, decay behavior, diversity-preserving pruning, and saturation controls.

### Fixed when

- a controlled bridge test demonstrates meaningful convergent multi-source activation
- activation remains bounded under dense graphs
- convergence improves retrieval without causing hub domination or runaway activation
- ablation shows the graph contributes behavior that lexical/direct retrieval cannot replace

---

## IMP-007 Causal sequence learning is insufficiently context-conditioned

**Status:** OPEN  
**Priority:** P1  
**Affected subsystem:** causal prediction / planning  
**Discriminator gates:** DISC-010  
**Source:** adversarial architecture review, 2026-09-09

### Problem

A learned transition such as `ask -> explore` is still relatively global. Its observed reliability can differ substantially across threat, fatigue, social support, competence, environment, and motive regime.

### Why it matters

A context-insensitive transition can convert correlation from one regime into misleading route bias elsewhere.

### Improvement direction

Add bounded context-conditioned transition models with deliberately coarse context features and backoff to global priors. Avoid arbitrary context strings or combinatorial state explosion.

### Fixed when

- the same action sequence can learn different reliability under meaningfully different contexts
- sparse contexts back off rather than overfit
- context model remains bounded
- DISC-010 confound scenarios no longer produce inappropriate universal route bias

---

## IMP-008 Current validation is still too friendly

**Status:** IN PROGRESS  
**Priority:** P1  
**Affected subsystem:** evaluation methodology  
**Discriminator gates:** DISC-001 through DISC-014  
**Source:** adversarial architecture review, 2026-09-09

### Problem

The existing longitudinal and focused suites are strong implementation acceptance tests, but most scenarios were designed alongside the architecture and intentionally exercise expected mechanisms.

### Why it matters

A system can become highly optimized to its own demonstrations. Friendly tests establish implementation correctness better than falsification strength.

### Improvement direction

Implement the DUCK Discriminator specified in `DUCK_DISCRIMINATOR_v0.10.md`, including randomized holdouts, metamorphic tests, ablations, parameter sweeps, crash injection, adversarial percepts, long-run boundedness, and causal confounds.

### Fixed when

This item is not closed by creating the discriminator file. It is fixed for the v0.10 milestone only when a defined discriminator release profile exists, runs automatically, and its release gates are green or explicitly recorded as accepted limitations.

---

## IMP-009 Historical regression provenance is incomplete

**Status:** OPEN  
**Priority:** P2  
**Affected subsystem:** historical evaluation / versioning  
**Discriminator gates:** DISC-011  
**Source:** adversarial architecture review and prior v0.7 host-binding defect

### Problem

Some historical simulation modules have imported branch-public components while carrying historical version labels. One v0.7 contamination path was already found and fixed, demonstrating that this is a real rather than hypothetical risk.

### Why it matters

A passing test labeled "v0.8" is not valid historical evidence if it silently executes portions of v0.10.

### Improvement direction

Audit every historical simulation and pin or parameterize runtime/host dependencies explicitly.

### Fixed when

- every historical harness declares the exact runtime and host implementation it exercises
- DISC-011 verifies no branch-public alias leakage
- CI output identifies historical provenance clearly

---

## IMP-010 Counterfactual implementation/status documentation drift

**Status:** FIXED  
**Priority:** P3  
**Affected subsystem:** documentation  
**Discriminator gates:** none; documentation hygiene  
**Source:** adversarial architecture review, 2026-09-09

### Problem

`STATUS.md` described explicitly labeled counterfactual predictions as candidate future work even though transient counterfactual route comparison had been implemented and verified.

### Resolution

`STATUS.md` now records transient counterfactual route comparison as implemented, documents `model_prediction` provenance and non-persistence, records the verified CI run, and limits future work to genuine extensions such as richer counterfactual models.

### Verification evidence

Documentation correction commit: `4327cda65a2acc493568aaff862bf0d7a248377e`.

This was a documentation-only defect; the underlying counterfactual behavior was already verified in CI run #262 at commit `2959ce945fa59c7d9691b2e4206e5743afdf4cc8` on Python 3.11 and Python 3.12.

---

## IMP-011 Build the executable DUCK Discriminator harness

**Status:** OPEN  
**Priority:** P1  
**Affected subsystem:** evaluation infrastructure  
**Discriminator gates:** all  
**Source:** discriminator specification

### Problem

`DUCK_DISCRIMINATOR_v0.10.md` defines the adversarial program, but a documented evaluator is not yet an executable evaluator.

### Improvement direction

Implement a dedicated discriminator runner and machine-readable result format without conflating it with ordinary pytest acceptance tests.

Pieces of the executable discriminator may be implemented early as targeted remediation gates. The expensive broad discovery profile is intentionally deferred until the high-priority known weakness queue is substantially cleared, as specified in `IMPROVEMENT_LOOP_v0.10.md`.

Suggested broad executable tranche:

1. DISC-001 randomized longitudinal holdouts
2. DISC-002 metamorphic invariance
3. DISC-003 mechanism ablation
4. DISC-005 crash consistency
5. DISC-007 firewall/prompt injection
6. DISC-008 10k-heartbeat boundedness
7. DISC-010 causal confounds

### Fixed when

- `python -m duck.discriminator...` or an equivalent stable command runs the release profile
- failures produce machine-readable evidence
- failures create/update this backlog by ID through a documented workflow
- CI can gate a release candidate on the discriminator independently from normal regression tests

---

# Discriminator failure intake template

Copy this section for each new unique failure or update the existing matching item.

## IMP-XXX Short failure title

**Status:** OPEN  
**Priority:** P0/P1/P2/P3  
**Affected subsystem:** ...  
**Discriminator gate:** DISC-...  
**First failing commit:** ...  
**Scenario/seed:** ...

### Challenged architectural claim

...

### Expected behavior

...

### Observed behavior

...

### Reproduction

...

### Suspected mechanism / open question

...

### Improvement direction

...

### Fixed when

...

### Verification evidence

Commit/run: pending

---

## Backlog discipline

When an item is fixed, retain it in this document. Change its status to `FIXED` and record the verification commit/run. The backlog is also a research history of which architectural assumptions failed and how they were corrected.

Do not delete embarrassing failures. They are evidence.
