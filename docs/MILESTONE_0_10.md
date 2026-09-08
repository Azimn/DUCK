# DUCK Milestone 0.10: Motivated Cognition, Associative Activation, and Global Modulation

This milestone converts DUCK's current motivated planning system into a richer motivated cognitive architecture. It must preserve every promoted v0.9 invariant while adding persistent motive dynamics, a typed associative activation substrate, and global cognitive modulation.

The milestone is complete when current needs can generate persistent competing motives, those motives can survive across quiet time and restart, the currently dominant motive can recruit retrieval and planning rather than mapping directly to a primitive action, and satisfaction or changed conditions can alter motive dominance without deleting unrelated latent motives.

The motive system must distinguish need, motive, goal, plan, intention, action, and outcome. A need is regulated internal state. A motive is a persistent pressure to change or preserve a condition. A goal is a concrete objective recruited in service of a motive. A plan is a route to a goal. An intention is the currently active step. An action is an outward attempt. An outcome updates the continuing subject.

The associative substrate must link canonical entities rather than replacing them. At minimum, graph nodes must be able to refer to autobiographical memories, concepts, people, goals, plans, actions, outcomes, and motives. Activation must propagate for bounded depth with decay, and current perceptual context plus selected motive must be able to alter which canonical entities become cognitively available.

The associative layer must demonstrate a nontrivial bridge case. A current cue must be able to activate a prior memory through an intermediate association that ordinary direct lexical retrieval would not have ranked highly enough on its own. The returned memory must preserve its original provenance and epistemic status.

Associative activation must be learnable but bounded. Repeated co-activation or action/outcome experience may strengthen an edge, but graph growth, fan-out, propagation depth, total activation mass, and retained edge count must remain limited under long quiet simulations.

The cognitive modulation layer must change computation rather than merely final action utility. The milestone must demonstrate at least four operating-regime effects. Threat must narrow associative breadth and planning branching. Curiosity must broaden associative exploration when safety permits. Fatigue must reduce planning depth or working-set size. Low competence must increase reliance on familiar or previously successful strategies.

The same external situation must be evaluated under at least two different internal regimes and produce measurably different retrieval breadth or planning structure before final action selection.

Motive state and modulation must interact with the v0.9 planner. A selected motive must be able to recruit or prioritize a goal, and modulation must be able to constrain route search depth or branching. Planning may remain deterministic for the milestone, but route generation and evaluation must consume motive and modulation context rather than only shallow utility terms.

The subject-access firewall remains mandatory. No first-person `SubjectiveMoment`, private-cognition provider, or language-expression provider may receive raw need magnitudes, motive strengths, graph activations, edge weights, modulation coefficients, route scores, plan indexes, concern IDs, trust floats, affect magnitudes, retrieval scores, or latent vectors.

The qualitative projection may include first-person content such as `I'm exhausted`, `I keep coming back to what Morgan promised`, `I don't feel safe enough to poke around`, `I want to understand this`, or `I should stick with something I know how to do` when those statements are warranted by accessible state.

The milestone must pass language-lesion testing. Motive generation, motive persistence, motive competition, associative propagation, modulation, retrieval changes, planning recruitment, action selection, outcome learning, and restart continuity must operate with inner speech disabled and with no LLM provider.

The milestone must pass persistence testing. Motives, learned graph associations, and any persistent modulation-relevant learned state must survive `SubjectState` serialization and process restart without creating a second subject authority.

The milestone must pass longitudinal testing. A multi-day synthetic-life scenario must include competing safety, curiosity, energy, affiliation, competence, and coherence pressures; recurring people; commitments; a threat episode; a novel problem; fatigue; successful and failed plans; quiet recovery; and at least one restart. The test must show that motives rise, fall, persist, become inhibited, recruit goals, and stop dominating when their target condition changes.

The milestone must include negative controls. Ordinary quiet state must not continuously generate new motives or graph activation. A satisfied motive must not remain permanently dominant. Threat narrowing must relax after safety recovery. Curiosity broadening must not override severe threat. Fatigue must not permanently cripple planning after energy recovery.

All v0.9 and earlier regression suites remain mandatory. v0.10 is additive and may not weaken autobiographical provenance, world/belief separation, relationship trajectories, commitments, outcome learning, prospective agency, hierarchical planning, restart continuity, language-lesion survival, bounded quiet-time behavior, or the subject-access firewall.

Passing this milestone establishes a tested modern motivated-cognition layer under the defined simulations. It does not establish phenomenal consciousness, human-equivalent cognition, general psychological validity, or unrestricted autonomous agency.
