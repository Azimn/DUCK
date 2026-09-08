# MicroPsiDUCK v0.10 Current Status

Current architecture candidate: `docs/ARCHITECTURE_v0.10.md`

Current milestone candidate: `docs/MILESTONE_0_10.md`

Experiential boundary contract: `docs/EXPERIENTIAL_FIREWALL_v0.10.md`

Development branch: `motivated-cognition-v0.10`

Preserved promoted baseline: DUCK v0.9 on `main`

## Scope of the current implementation

MicroPsiDUCK v0.10 is now treated as a structural redesign rather than a compatibility-preserving patch to DUCK v0.9. The branch public package points to the v0.10 runtime and persistent host. The v0.9 organism remains explicitly importable for comparison and remains preserved unchanged as the promoted baseline on `main`.

The current implementation hardens the first-person boundary before the full motive, associative-graph, and global-modulation control spine is implemented.

The new private-cognition contract is `ExperientialFrame`. It is immutable and contains only approved first-person experiential prose. Structured `SubjectiveMoment` data may still exist inside inherited implementation layers as diagnostic scaffolding, but the v0.10 runtime converts it through the experiential firewall before a private cognition provider receives it.

The experiential validator rejects raw decimal telemetry, percentages used as magnitude or confidence reports, machine identifiers, key-value telemetry, activation reports, route scores, retrieval scores, motive strengths, need magnitudes, and related implementation leakage.

Private interior state is persisted separately in a versioned `PrivateInteriorState` envelope. The current schema is `duck.private-interior.v1`. The persistence envelope stores approved experiential prose and optional private thought, while mechanistic affect, need state, action scores, graph state, and other developer telemetry remain outside it. Unsupported private-interior schema versions fail explicitly.

The v0.10 persistent host writes canonical subject state and private interior state separately. Public interaction results no longer include private-thought or subjective-state fields. Ordinary interaction and heartbeat journals do not publish private interior content.

The renderer contract now receives prose-only experiential state, optional private thought as controlled rendering context, and a first-person action-intent sentence. Machine action identifiers are translated before entering the renderer packet. The renderer remains an expression surface and cannot become canonical subject authority.

The branch CLI has been aligned with that boundary. Ordinary tick and demo output no longer print private thought. The package metadata identifies the candidate as `micropsi-duck` version `0.10.0`, with both `micropsiduck` and historical `duck` command aliases targeting the v0.10 CLI.

No donor package is a runtime dependency.

## Architecture still to implement

The binding v0.10 architecture now defines the next control spine: continuous state dynamics, need-driven persistent motives, motive competition, a bounded active motive set, typed associative activation, global cognitive modulation, a cognitive field, automatic policy, executive recruitment, planning, action, outcome, and recursive learning.

The motive system, typed associative graph, modernized global modulators, and dedicated long-horizon MicroPsiDUCK simulation are not yet complete merely because the experiential firewall is implemented. The v0.10 milestone remains open until those mechanisms and their required experiments pass.

The v0.9 planner is not architecturally privileged in v0.10. It may be reused, refactored, or replaced if a different bounded planning design better fits the motive and modulation control spine.

## Experiential firewall verification targets

The v0.10 tests require the full candidate runtime to deliver an `ExperientialFrame` to private cognition rather than structured diagnostic state. They verify that the frame has only a prose field, that no raw float telemetry appears, that disguised telemetry is rejected, and that language-lesion operation still refreshes experiential state.

The persistence tests require private interior state to survive restart with the same supported schema and prose content. They verify that the private-interior file does not contain canonical affect, needs, or machine action selection state.

Renderer tests require first-person action intent rather than machine action tags and verify that renderer packets do not contain private schema metadata or selected-action identifiers.

Public-boundary tests verify that interaction results omit private thought and subjective state and that ordinary event journals do not publish private interior fields.

## Preserved scientific and behavioral invariants

The v0.10 branch may change implementation structure, but it continues to protect substantive invariants that remain useful from DUCK: persistent subject identity, autobiographical provenance, world and belief separation, relationship continuity, commitments, outcome learning, restart continuity, bounded quiet-time behavior, language-lesion operation, and the experiential firewall.

Earlier long-horizon regulation, life simulation, agency, and planning harnesses remain valuable regression evidence while the new control spine is built. They are historical behavioral tests, not authorities over v0.10 internal design.

## Relationship to DUCK v0.9

DUCK v0.9 remains the stable comparison point on `main`. It established endogenous goal formation, counterfactual route selection, hierarchical subgoals, outcome-driven replanning, and a persistent planning lifecycle.

MicroPsiDUCK v0.10 changes the research question. The target is no longer only whether lived experience can create and revise goals. The target is whether needs create persistent motives, motives organize cognition, associative activation makes relevant material available without explicit search, internal condition changes the computational regime, and the subject experiences the consequences of those mechanisms without gaining introspective access to the machinery.

The subject-access firewall remains mandatory, now strengthened as the experiential firewall.

Passing current firewall and regression tests establishes only the implemented boundary behavior. It does not establish completion of the full MicroPsiDUCK motive, association, and modulation architecture, phenomenal consciousness, human-equivalent cognition, unrestricted autonomy, or general psychological validity.
