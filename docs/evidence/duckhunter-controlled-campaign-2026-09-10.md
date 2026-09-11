# Duckhunter Controlled Continuity Campaign

Date: 2026-09-10

## Frozen implementation

The implementation under evaluation is `motivated-cognition-v0.10` at commit `30a11ea8308ebd0fc89a06bb994ab0e23bd02886`. The evaluation work is isolated on `duckhunter-eval-20260910`. No cognitive architecture changes were made on the evaluation branch.

The first controlled campaign was added in commit `ff10377f75649c8daf2f21d2167c865e7ec568f3` as `tests/test_duckhunter_controlled_campaign_v010.py`.

## Method

The campaign uses persisted matched checkpoints. Experimental branches are copies of the same subject checkpoint and preserve the same `subject_id`. They are counterfactual copies for causal comparison, not claims of separately instantiated individuals.

The tests exercise history reaching the authorized renderer boundary, relationship ablation at a configured relationship-sensitive opportunity, actor-specific history after restart, survival of consequential history across a long quiet interval and restart, and belief revision only after perceived corrective evidence.

The relationship intervention deliberately creates a large state difference. Four broken commitments from the same actor are sufficient under the current update rules to drive the intact adverse branch into a cautious relationship stance. The ablated branch resets only that actor's relationship state to the neutral default. Both branches then receive the same probe.

## First run

GitHub Actions run `34544982018` executed the evaluation commit. The existing targeted discriminator succeeded and the existing component comparison succeeded. The full pytest job failed on the new campaign. Python 3.11 reported `1 failed, 233 passed`. The Python 3.12 matrix reached the same pytest failure before the workflow was cancelled by fail-fast behavior.

Four of the five new controlled tests passed. Matched kept versus broken history produced different authorized first-person renderer context while allowing the public wording to remain deliberately identical. Actor-specific relationship histories survived restart and produced different accessible context for the corresponding interlocutors. An adverse history remained distinguishable from its matched comparison after 64 quiet heartbeats and restart. A hidden world change did not rewrite the subject's belief until corrective evidence was perceived, and the corrected belief survived restart.

The failed test was `test_relationship_ablation_changes_a_publicly_relevant_route`.

The intact adverse branch and the relationship-ablated branch had different relationship stances, satisfying the state-level intervention check. Nevertheless, both selected the same action, `explore`, and both delivered exactly `I want to look into that a little more.`

## Failure localization

The relevant relationship information was not lost from persistent state. The relationship intervention changed the derived stance as intended. The observed loss occurs later in the public realization path.

`PersistentDuckHost._render_expression` computes a relationship-sensitive deterministic stance, but when the selected action is present in `DeterministicExpression._ACTION_LINES`, the action-specific fixed line replaces the response. For `explore`, that replacement masks the stance difference. Under this controlled opportunity, removing the relationship influence therefore produced no observed difference in selected action or delivered deterministic wording.

The appropriate conclusion is narrow: the current deterministic expression path demonstrates no public contribution from the relationship state at this probe despite a large relationship intervention. This does not establish that relationship state is generally unnecessary. It could affect other actions, other probes, or a capable language renderer. It does establish a concrete integration point where preserved subject state can fail to influence delivered behavior.

## Campaign readiness limits

The branch does not currently contain Pretorius or Wayfarer character fixtures. The public host constructor accepts subject identity and runtime dependencies but does not expose a first-class character-origin or persona fixture interface sufficient to instantiate Pretorius from a frozen origin definition for this study. The current branch also does not expose genuine same-origin new-instantiation semantics for creating distinct developed individuals from one origin.

The command-line chat path can use the deterministic expression layer or an OpenAI-compatible provider, but this evaluation environment does not provide a frozen shared provider configuration, frozen Pretorius origin, Wayfarer conversational fixture, strong persistent-memory baseline implementation, plain persona-and-history baseline, or blinded human-rating panel. Therefore the requested A/B/C/D conversational quality comparison cannot be validly completed from this branch by inventing transcripts or privately patching identities.

This is itself a campaign-readiness result. The controlled causal tests can run now, but the central absolute-quality and incremental-value claim remains unevaluated until all comparison systems can be instantiated from frozen definitions and exercised through comparable conversational runners.

## Current evidentiary conclusion

The present result supports several implementation claims about persistence, authorized experiential access, actor-conditioned relationship state, restart continuity, and evidence-gated belief revision. It also exposes a specific public realization path where a large relationship intervention is behaviorally masked.

No claim of superior conversational individuality is supported by this campaign. No claim of adequate absolute conversational quality is supported either. Existing internal mechanism gates remaining green does not resolve those questions.

Architectural expansion is not justified by this result. The next work needed for the research question is evaluation and integration infrastructure sufficient to run the frozen plain-history baseline, strong-memory baseline, full DUCK host, and Wayfarer path with the same underlying model and matched histories, followed by separate controlled and adaptive conversation scoring.