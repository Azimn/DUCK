# Behavior-first development and review

The target is a believable continuing individual. A simple utility rule, authored routine, or compact association is acceptable if it produces the intended behavior reliably. Computational complexity and resemblance to a biological implementation do not earn points by themselves.

The previous decimal ratings were informal architecture judgments. They are not measured human believability or a validated scale. This project must not declare completion by raising its own scores. A 9/10 claim requires a declared task domain, rubric, representative unseen scenarios, comparison conditions, and independent assessment. Passing automated gates is necessary evidence for specific mechanisms, but does not substitute for that assessment.

## Goal alignment

Before changing code, identify the observable failure and the goal it harms. Check existing mechanisms and donor work. Choose the smallest correction that addresses the failure, run the relevant check and neighboring regressions, then retain or revert it. Additional causal mechanisms and a whole-life simulator remain deferred until a behavioral experiment demonstrates their need.

Continuity means that identity and learned dispositions survive save, restart, and provider replacement, with equivalent continuation under equivalent conditions. Storing the same identifier alone is insufficient. Actual cross-model voice and character fidelity remain unmeasured in this pass.

Development means that different enacted histories affect later choices or expression, that contrary evidence can revise expectations, and that one event does not arbitrarily replace the character. A learned route score is evidence for a local mechanism, not proof of lifelong personality development. Authored formative memories and enacted formative experience must be compared rather than assumed equivalent.

Motivation and cognitive condition should alter action, retrieval, and persistence in ways traceable to the character's current situation. Endogenous continuity should survive the absence or failure of language services. Limited first-person access should preserve the distinction between perceived words and intention, and between private recollection and public expression.

Adaptive believability requires observing interactions in a declared world over time. A lightweight authored world is sufficient for a first experiment. Rich perception, full embodiment, sophisticated causal inference, and biological realism are not prerequisites for demonstrating a narrower successful character experience.

## Current changes and limits

Associative retrieval now adds contributions from distinct cues while retaining the strongest path from each cue. Cycles and duplicate relation labels do not supply extra evidence. Search depth, fanout, seed count, and active nodes remain bounded. A two-cue retrieval test defeats a stronger single distractor and survives a small parameter neighborhood. Broad hub-bias and retrieval-quality evaluation remains open.

The donor is the contextual summation principle described in Niels Taatgen's 1999 thesis, Learning without Limits, printed pages 41-42: https://act-r.psy.cmu.edu/wordpress/wp-content/uploads/2012/12/345nat_1999_b.pdf . DUCK uses capped graph contributions; it does not implement ACT-R's complete activation, latency, noise, or source-budget equations. No donor code or package was copied.

The current experiential projection uses internal provenance atoms. External speech beginning with I stays attributed to its source. Known instruction patterns and telemetry in recollection, belief, and concern text receive qualitative replacements. Pattern screening and quotation do not guarantee protection from every semantic prompt injection. A compromised executive can still propose an available action. IMP-004 remains open for that reason.

Negative strategy evidence now reduces candidate and route scores instead of being clamped away. Positive subsequent evidence can recover the preference using the existing learner. This fixes a disconnected consequence of learning without adding another memory system.

Private cognition failure or an invalid return contract now uses the deterministic fallback. Public world authority is cleared even if a cognitive step raises. Pending-action tags normalize to their declared tuple on current-runtime construction after JSON restoration.

The deterministic renderer expresses trust or guardedness from approved experience and handles waiting explicitly. It no longer copies the first private recollection into public output automatically. These are modest authored behaviors, not a claim of natural conversation parity with a person.

## Executable evaluation

Run `python -m duck.discriminator --seed 17 --ticks 1000 --output report.json` for the targeted profile. Run with `--ticks 10000` for the longer boundedness check. The runner has no model dependency and does not call a paid API.

The JSON report records the commit, dirty-worktree status, seed, duration in ticks, per-scenario evidence, and backlog classification. Failed checks also appear in `backlog_updates`. A contributor applies those records to the referenced backlog item, retaining reproduction and verification history. The runner does not silently edit repository documents during CI.

This is a targeted remediation profile, not the complete fourteen-family discriminator release profile. Its restart scenario checks exact reconstructed state and next-step equivalence; the separate transactional pytest suite exercises crash boundaries. Its learning scenario isolates the strategy mechanism. Its paired social-history scenario checks history-dependent public expression after a quiet interval and persistence of relationship differences after one contrary event. Its toy-world scenario checks boundedness, not realism. Names randomized within convergence do not make the entire evaluator an independent holdout study.

Human believability is explicitly reported as not measured. The next product-level evidence should be blinded evaluation of continuing interactions, comparing an unchanging character description, an authored initialized character, and a character shaped by enacted experience, using matched worlds and previously unseen encounters. Assess recognizability, appropriateness of change, consistency of knowledge, relationship specificity, and natural expression before assigning an overall score.
