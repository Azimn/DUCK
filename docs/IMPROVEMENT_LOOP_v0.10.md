# MicroPsiDUCK v0.10 Improvement Loop

## Purpose

This document defines the working loop for improving MicroPsiDUCK without wasting time rediscovering defects that are already known.

The Improvement Backlog is the source of truth for known weaknesses. The DUCK Discriminator is the adversarial evaluator. They serve different roles and should not be run in the least efficient order.

The default development order is:

```text
KNOWN WEAKNESS
    ↓
IMPROVEMENT BACKLOG ITEM
    ↓
IMPLEMENT / REFACTOR
    ↓
TARGETED HOSTILE VERIFICATION
    ↓
ORDINARY CI + NEIGHBORING REGRESSIONS
    ↓
BACKLOG ITEM VERIFIED/FIXED
    ↓
NEXT KNOWN WEAKNESS

After high-priority known weaknesses are substantially cleared:

BROAD DUCK DISCRIMINATOR RUN
    ↓
classify findings as NEW / KNOWN / REGRESSION
    ↓
NEW findings create backlog items
KNOWN findings update existing items without duplication
REGRESSIONS reopen or escalate previously fixed items
    ↓
repeat the loop
```

The purpose is to spend adversarial evaluation effort on discovering unknown failure modes, not repeatedly reporting defects already documented in `IMPROVEMENT_BACKLOG_v0.10.md`.

## Two evaluation modes

### Mode A: targeted remediation verification

Used while fixing known backlog items.

Only the discriminator gates relevant to the current improvement are exercised, together with neighboring invariants likely to regress.

Examples:

- IMP-001 transactional persistence → DISC-005 crash consistency plus restart/identity regressions
- IMP-002 world authority separation → DISC-006 epistemic boundary attacks plus expectation/world tests
- IMP-004 semantic experiential firewall → DISC-007 and DISC-014 plus executive fallback tests
- IMP-007 context-conditioned causal learning → DISC-010 plus ordinary sequence/intervention regressions
- IMP-009 historical provenance → DISC-011 plus explicit historical harness identity checks

A targeted run is allowed to know the weakness being fixed. Its purpose is engineering verification, not scientific holdout discovery.

### Mode B: broad discriminator discovery

Used after the known high-priority remediation queue has been substantially cleared.

The broad run should emphasize holdout adversaries, fuzz seeds, metamorphic perturbations, long-run boundedness, ablations, parameter sweeps, and combinations not used directly while implementing fixes.

Its purpose is to find **unknown** weaknesses.

Broad discovery should not spend substantial analysis tokens explaining a known open defect again unless the observed behavior differs materially from the existing backlog description.

## Failure classification

Every discriminator finding must be classified before analysis expands.

### NEW

The failure does not match an existing open, in-progress, verifying, accepted-limitation, or fixed backlog item.

Action:

1. create a new `IMP-xxx` item
2. record reproduction/seed/evidence
3. assign severity
4. enter the remediation queue

### KNOWN

The failure is already represented by an open/in-progress/verifying backlog item and is behaviorally consistent with that item.

Action:

- link the finding to the existing IMP ID
- update reproduction evidence if useful
- do not create a duplicate item
- do not repeat a full architectural diagnosis unless new evidence changes the suspected mechanism

### REGRESSION

The failure matches an item previously marked `FIXED`, or a current change makes an existing weakness materially worse.

Action:

- reopen the existing item
- record first regressing commit if known
- increase severity if justified
- prioritize before new feature work when the regression affects a protected invariant

### EXPECTED / ACCEPTED LIMITATION

The failure matches an explicitly documented accepted limitation whose behavior has not worsened.

Action:

- report it compactly
- retain the limitation
- do not consume a new backlog ID

An accepted limitation may still block a release profile if the release doctrine says the gate is mandatory.

## Report structure

A discriminator report should separate discovery from known debt:

```text
run
  commit_sha
  suite_version
  profile
  seeds

summary
  new_failures
  known_failures
  regressions
  accepted_limitations
  passes

findings[]
  gate_id
  classification      NEW | KNOWN | REGRESSION | ACCEPTED
  backlog_item_id
  scenario_id
  seed
  severity
  evidence
  changed_from_previous_evidence
```

This lets a broad run say, for example, `DISC-005: KNOWN → IMP-001` without producing another long persistence diagnosis.

## Current remediation queue

The following order is the current default unless a new P0/P1 regression changes priorities.

### Phase 1: authority and continuity hardening

1. **IMP-001** transactional persistence across subject/cognition/expectation/causal/environment/private state
2. **IMP-002** move authoritative world truth out of `SubjectState`
3. **IMP-004** strengthen the experiential firewall semantically and provenance-wise
4. **IMP-007** context-condition causal sequence learning and add bounded backoff

These are P1 because they affect continuity, authority, privacy/access, or epistemic/causal correctness.

### Phase 2: provenance and structural cleanup

5. **IMP-009** pin and audit historical regression provenance
6. **IMP-003** reduce the v0.10 inheritance tower through explicit composition/orchestration
7. **IMP-006** evaluate and improve convergent associative activation

### Phase 3: robustness characterization

8. **IMP-005** parameter-sensitivity analysis and magic-number/cliff detection

Parameter sensitivity is intentionally later because measuring robustness before major known structural changes would characterize a configuration we already intend to replace.

### Phase 4: broad adversarial discovery

9. **IMP-011** complete the executable DUCK Discriminator release harness
10. **IMP-008** run and maintain the broad adversarial validation program

Pieces of the executable discriminator may be implemented earlier when needed for targeted verification. What is deferred is the expensive broad discovery profile, not the ability to test a current fix adversarially.

## Stop conditions for broad discovery

The first serious broad discriminator campaign should not begin merely because ordinary CI is green.

Preferred preconditions:

- no open P0 items
- IMP-001, IMP-002, IMP-004, and IMP-007 are FIXED or explicitly accepted with rationale
- historical provenance is trustworthy enough to interpret regression results
- architecture composition is stable enough that broad failures will not mostly reflect a refactor already planned
- ordinary CI is green on the exact candidate commit

P2 items may remain open if they are themselves useful targets for broad evaluation, but they should be classified as known debt so the report does not pretend to discover them again.

## Improvement-item micro-loop

For each backlog item:

1. Read the item and the affected architecture contract.
2. Capture a minimal failing or weakness-demonstrating case before changing the mechanism when practical.
3. Implement the smallest architectural correction that addresses the mechanism rather than the symptom.
4. Run the targeted discriminator gate.
5. Run neighboring regression tests and the ordinary CI matrix.
6. If the fix passes only the original scenario, perturb the scenario or seed before closing.
7. Record verification commit/run in the backlog.
8. Mark the item `FIXED`, or record why it remains open.
9. Continue to the next queue item.

## Token and evaluation discipline

To avoid wasting evaluation effort:

- do not run the entire broad discriminator after every small code change
- do not create duplicate backlog entries for the same mechanism
- do not repeatedly write long explanations of known failures unless evidence changes
- preserve failing seeds and reproductions so later checks can be mechanical
- use focused adversarial tests during remediation and broad holdouts only at meaningful checkpoints
- when a known issue is fixed, keep its historical entry so later regressions can be recognized immediately

## Research rationale

This workflow intentionally separates two scientific activities:

**engineering hardening** asks whether we fixed weaknesses we already understand.

**adversarial discovery** asks what weaknesses remain that we did not already know to look for.

Conflating them makes the discriminator less informative because a large fraction of its output simply restates the development team's own backlog. The remediation-first loop preserves the discriminator's value as a source of genuinely new evidence.
