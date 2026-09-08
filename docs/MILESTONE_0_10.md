# MicroPsiDUCK Milestone 0.10: Motivated Cognition, Associative Activation, Global Modulation, and Experiential Access

This milestone defines a new MicroPsiDUCK development line built from the useful parts of DUCK and selected functional ideas from Psi and MicroPsi. Version 0.9 remains preserved on `main` and in historical modules. Version 0.10 is not required to preserve v0.9 API identity, file layout, class hierarchy, or internal control structure when a cleaner architecture better satisfies the research target.

What must survive are the substantive properties that remain useful: persistent subject identity, autobiographical provenance, world and belief separation, relationship continuity, commitments, outcome learning, restart continuity, language-lesion operation, bounded quiet-time behavior, and first-person access discipline. Regression tests should detect loss of those properties, not force obsolete implementation structure to remain authoritative.

The milestone is complete when current needs can generate persistent competing motives, those motives can survive quiet time and restart, the currently dominant motive can organize retrieval and planning rather than mapping directly to a primitive action, and satisfaction or changed conditions can alter motive dominance without deleting unrelated latent motives.

The motive system must distinguish need, motive, goal, plan, intention, action, and outcome. A need is regulated internal state. A motive is a persistent pressure to change or preserve a condition. A goal is a concrete objective recruited in service of a motive. A plan is a route to a goal. An intention is the currently active step. An action is an outward attempt. An outcome updates the continuing subject.

The associative substrate must link canonical entities rather than replacing them. At minimum, graph nodes must be able to refer to autobiographical memories, concepts, people, goals, plans, actions, outcomes, and motives. Activation must propagate for bounded depth with decay, and current perceptual context plus selected motive must be able to alter which canonical entities become cognitively available.

The associative layer must demonstrate a nontrivial bridge case. A current cue must be able to activate a prior memory through an intermediate association that ordinary direct lexical retrieval would not have ranked highly enough on its own. The returned memory must preserve its original provenance and epistemic status.

Associative activation must be learnable but bounded. Repeated co-activation or action and outcome experience may strengthen an edge, but graph growth, fan-out, propagation depth, total activation mass, and retained edge count must remain limited under long quiet simulations.

The cognitive modulation layer must change computation rather than merely final action utility. The milestone must demonstrate at least four operating-regime effects. Threat must narrow associative breadth and planning branching. Curiosity must broaden associative exploration when safety permits. Fatigue must reduce planning depth or working-set size. Low competence must increase reliance on familiar or previously successful strategies.

The same external situation must be evaluated under at least two different internal regimes and produce measurably different retrieval breadth or planning structure before final action selection.

A selected motive must be able to recruit or prioritize a goal, and modulation must be able to constrain route search depth or branching. Planning may remain deterministic for the milestone, but route generation and evaluation must consume motive and modulation context rather than only shallow utility terms. The v0.9 planner may be reused, refactored, or replaced if another bounded planner better fits the new control spine.

## Experiential firewall acceptance contract

The experiential firewall is a technical requirement of the architecture, not a rendering preference.

The mechanistic substrate may store numeric need values, motive strengths, graph activations, edge weights, modulation coefficients, action scores, route scores, confidence values, tags, identifiers, and latent state. None of those representations may cross into the v0.10 private-cognition interface.

Private cognition must receive only an immutable `ExperientialFrame` containing approved first-person experiential prose. A structured diagnostic object such as `SubjectiveMoment` may exist internally, but it is not the introspective API.

The translator must reject raw decimals, percentages used as magnitude or confidence reports, machine identifiers, key-value telemetry, activation reports, route scores, retrieval scores, motive strengths, need magnitudes, and equivalent disguised machinery when they attempt to cross the boundary.

The qualitative projection may include first-person content such as `I'm exhausted`, `I keep coming back to what Morgan promised`, `I don't feel safe enough to poke around`, `I want to understand this`, or `I should stick with something I know how to do` when those statements are warranted by accessible state.

Private interior state must be versioned and persistent across process restart. The persistence envelope may contain host-side schema metadata, but the subject cannot introspect that metadata. Unsupported schema versions must fail explicitly rather than being silently reinterpreted.

The public renderer may read a controlled prose-only view of private interior state. Machine action identifiers must be translated into first-person intent prose before entering the renderer packet. Public interaction results and ordinary event journals must not publish private thought or private experiential state.

The renderer is not subject authority. It cannot directly write canonical memories, beliefs, relationships, motives, plans, goals, or mechanistic state.

## Lesion, persistence, and longitudinal requirements

The milestone must pass language-lesion testing. Motive generation, motive persistence, motive competition, associative propagation, modulation, retrieval changes, planning recruitment, action selection, outcome learning, experiential projection, and restart continuity must operate with inner speech disabled and with no LLM provider.

The milestone must pass persistence testing. Motives, learned graph associations, persistent modulation-relevant learned state, and versioned private interior state must survive process restart without creating a second subject authority.

The milestone must pass longitudinal testing. A multi-day synthetic-life scenario must include competing safety, curiosity, energy, affiliation, competence, and coherence pressures; recurring people; commitments; a threat episode; a novel problem; fatigue; successful and failed plans; quiet recovery; and at least one restart. The test must show that motives rise, fall, persist, become inhibited, recruit goals, and stop dominating when their target condition changes.

The milestone must include negative controls. Ordinary quiet state must not continuously generate new motives or graph activation. A satisfied motive must not remain permanently dominant. Threat narrowing must relax after safety recovery. Curiosity broadening must not override severe threat. Fatigue must not permanently cripple planning after energy recovery. Raw mechanistic telemetry must not appear in private cognition or public language packets.

## Promotion rule

The branch public API may point directly at the v0.10 MicroPsiDUCK runtime and host. Version 0.9 remains the preserved comparison baseline on `main`; v0.10 does not need to masquerade as v0.9 while under development.

Before promotion, the full v0.10 test matrix must pass on supported Python versions, including documentation validation, architectural unit tests, language-lesion tests, persistence and restart tests, experiential-firewall tests, long-horizon simulation, and any historical behavioral regressions still designated as scientifically relevant.

Passing this milestone establishes a tested modern motivated-cognition architecture under the defined simulations. It does not establish phenomenal consciousness, human-equivalent cognition, general psychological validity, or unrestricted autonomous agency.
