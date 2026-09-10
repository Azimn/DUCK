# Component selection after prior-work reuse

The first integration was published at `fe8968e7f29f45f73e902e93d3ac883912316507`. [Actions run 34448886046](https://github.com/Azimn/DUCK/actions/runs/34448886046) passed on that exact implementation, including the existing configured evaluation/simulation matrix, 217 tests, and the targeted discriminator. The following comparison phase examines overlapping responsibilities rather than merging every archived subsystem.

## Criterion and evidence limits

A better component must satisfy the current ownership and behavioral contract, have bounded costs and state, preserve restart behavior, and add an observable benefit. This is not an empirical ranking of whole cognitive architectures or proof of globally optimal code. Tests here are authored acceptance scenarios. Older donor algorithms are reconstructed where explicitly stated; their full repositories were not all installed and benchmarked as interchangeable systems.

The executable comparison is `python -m duck.component_comparison --output comparison.json --benchmark`. CI publishes its JSON artifact with the exact DUCK commit, dirty-state flag, and pinned donor revisions. Functional failures link to existing improvement IDs as regressions and return a nonzero process exit. Timings are local diagnostics and do not determine pass/fail.

## Spatial perception: adopt TinyPersona's access structure

DUCK's earlier scalar evidence interface assumed upstream perceptual filtering and therefore did not independently account for field of view, occlusion, range, or proximal touch. The adapted donor adds those checks before evidence reaches cognition. The nine declared cases include front and rear vision, occlusion, range, hearing behind the observer and through an occluder, and near/far touch. The unfiltered baseline meets four of nine access expectations; the adapted filter meets nine. This shows why the room requires spatial access. It is not a claim that the old interface promised geometric filtering and failed its own contract.

The added work costs CPU time. One development run over 300 packets of 48 stimuli measured approximately 0.12 ms per packet for unfiltered scalar conversion and 0.95 ms for spatial filtering plus attention. Those paths perform different amounts of work; the selected path is more correct for this environment, not faster. Hardware, load, and Python version affect these figures, and CI records fresh timings without a brittle latency threshold.

## Attention: retain bounded donor ranking and supply subject relevance

TinyPersona's selector already accepts goal-related salience. DUCK now supplies its own current safety, affiliation, or curiosity relevance to that bounded selector rather than creating another attention architecture. A paired fixture contains a brighter object and a somewhat quieter raised voice. Generic ranking selects the object. With safety pressure, subject relevance selects the voice; returning to neutral pressure restores object focus. This preserves limited attention while allowing current condition to change what reaches appraisal. The salience bonus remains a modeling parameter, not a psychological measurement.

The room uses one focus per tick to preserve separate source and modality provenance. Multimodal simultaneous appraisal is not implied by importing a donor that can rank several items.

## Catch-up and persistence: retain DUCK authority, improve the donor time rule

Jelly's inspected catch-up arithmetic caps processed ticks but subtracts all requested whole ticks when computing the remainder. For 650 elapsed seconds, 60-second ticks, and a three-tick cap, a second zero-elapsed call therefore cannot recover seven unprocessed ticks. DUCK's adaptation retains 470 seconds after the first call, processes the remaining seven ticks on the next call, and preserves a 50-second fractional remainder. Restart between the two calls is part of the comparison.

The selected persistence mechanism remains DUCK's existing complete-generation snapshot. Jelly's separate state/runtime file replacements are not adopted. The room/body/time crash test confirms that a pre-commit crash reopens the previous complete generation. No new storage engine or journaling architecture is necessary for this integration.

The day-cycle function is borrowed, but local-time conversion is replaced with explicit simulation seconds. The environment evolves reproducibly without depending on the machine's timezone. Catch-up delivers due scheduled changes as it advances actual ticks; it does not compress unprocessed history into fabricated memories.

## Social affordances: replace name-based physical access

The prior native helper inferred approach and withdrawal from any sufficiently credible named source. A remote message or disembodied voice therefore implied physical proximity. The replacement keeps conversational possibilities but requires physical presence/approach cues outside the LANGUAGE modality before inferring physical approach. The four declared cases cover remote language, voice without proximity evidence, visible presence, and audible approach cues. The former rule meets two cases; the selected rule meets four. A host can still explicitly supply other physically supported affordances.

This is an availability correction, not a new social-cognition subsystem. The small room adapter deliberately disables inferred social actions because it does not yet execute dialogue or social movement. It cannot manufacture success evidence for an unimplemented action.

## Continuous room host: replace stale availability with refreshed native decisions

Once a room is configured, the standard host heartbeat uses the refreshed room path whenever no scheduled occurrence takes priority. Explicit room ticks and catch-up also honor the existing event queue. Hidden scheduled changes update host reality and are not delivered as direct testimony; refreshed spatial perception may independently expose their observable consequences. Open/closed room object facts delegate to the room object itself, avoiding duplicate truth in the generic fact dictionary.

Tests verify that an object moved behind the observer stays outside beliefs even when a scheduled event changes its state. Turning toward an object or changing access produces new evidence and newly available targets. Generic non-room hosts preserve their prior behavior.

## Components retained or not yet selected

DUCK keeps its current personally conditioned appraisal, uniformly directed regulatory pressure, body dynamics, motivated strategy learning, and prose-only language boundary. Replacing them with older authored valence tags, mixed need scales, raw control packets, or direct room-to-subject writes would break current contracts. This is a contract-based retention decision, not an unperformed claim that each current algorithm wins a performance benchmark.

The full Gelatinblob recurrent learner is not installed beside the motivated learner. It is a materially different learning alternative and would require matched action interfaces, outcomes, and ablations before replacement. No comparative learning-quality result is claimed in this phase.

Pretorius speech-ledger and richer relationship work remain candidate donors for specific autobiographical and social failures. Wayfarer replay and renderer-degradation tests remain evaluation donors. Their existence does not justify importing every dimension or starting another complete rewrite. These were not ranked as interchangeable runtime components in the executable comparison.
