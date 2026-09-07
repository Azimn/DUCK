# DUCK Long-Horizon Regulation Architecture v0.6

Status: binding architecture candidate for the `simulation-lab-v0.6` branch.

DUCK remains a functional simulation of a persistent human-like subject. It does not claim phenomenal consciousness. Version 0.6 keeps the integrated v0.5 cognitive organism and adds regulation rules derived from longitudinal simulation failures rather than from a new cognitive theory.

The two governing invariants remain:

> The machinery may know numbers. The subject does not.

> What happens to the subject must be able to change the subject who encounters the next moment.

## Why v0.6 exists

The first long-horizon simulations exposed three pathologies in v0.5. Residual affect was repeatedly accumulated as though an old injury happened again every heartbeat. Important negative memories could be retrieved during idle cycles and repeatedly increase unease and guardedness. Homeostatic drives increased or decreased indefinitely while endogenous actions did not regulate the pressures that selected them, producing saturation and repeated `seek_connection` behavior.

Those are organism-level failures. A continuing subject should retain consequences without being permanently re-injured by its own memory, should recover from temporary activation while preserving autobiographical knowledge, and should be capable of partial self-regulation during quiet time.

## Architecture

```text
WORLD / USER / TIME
        |
        v
mechanistic subject state
  affect / needs / relationships
  beliefs / world facts / commitments
  autobiographical memory
  adaptive latent state
        |
        v
appraisal + retrieval + motivation
        |
        v
regulated action ecology
        |
        v
selected intention
        |
        +----------------------------+
        |                            |
        v                            v
SUBJECT ACCESS FIREWALL       developer diagnostics
        |
        v
SUBJECTIVE MOMENT
  what I notice
  what I feel
  what I remember
  what I believe
  what concerns me
  what I want to do
        |
        v
optional private cognition
        |
        v
expression / action
        |
        v
WORLD OUTCOME
        |
        v
learning + residue + memory
        |
        v
REGULATION / RECOVERY
        |
        v
NEXT SUBJECT
```

## Subject authority and first-person access

Canonical subject state remains outside the language model. The subject-access firewall remains mandatory. Raw affect values, need magnitudes, relationship scores, memory retrieval scores, embeddings, latent vectors, database identifiers, and hidden causal annotations are developer state, not first-person experience.

Private cognition receives only the qualitative `SubjectiveMoment`. Inner speech is optional. Disabling language must not remove action selection, memory influence, learning, homeostasis, relationship consequences, or persistence.

The LLM may contribute bounded interpretation, reflection, private cognition, and expression. It is neither canonical subject state nor sole decision authority.

## Memory, world facts, and subject beliefs

DUCK continues to distinguish world facts, subject beliefs, testimony, first-person experience, self-reflection, and observed outcomes. Objective world facts do not become subject beliefs merely because the host knows them. The subject gains access through perception, testimony, inference, or another explicit evidence path.

Autobiographical memory remains causally active. A remembered betrayal can make a later encounter feel uncertain or suspicious and can alter action utility. Retrieval itself, however, is not a new betrayal. On an endogenous idle cycle, simply retrieving an important negative memory must not permanently increase relationship guardedness or repeatedly add fresh affective injury.

## Residual affect and recovery

A consequence may leave a decaying residue that influences later moments. In v0.6 residue acts as temporary activation above an affective baseline rather than as a quantity re-added as fresh affect on every cycle. This lets a subject remain shaken after an event while also allowing recovery when no new adverse event occurs.

The memory of the event can remain indefinitely even after acute fear or unease has subsided. This deliberately separates autobiographical persistence from physiological-style activation.

A repair event may move trust and guardedness in a positive direction without erasing the history that made the relationship guarded. Recovery is therefore not equivalent to forgetting.

## Endogenous regulation

Heartbeat cycles continue even without user input. Most heartbeat cycles are allowed to produce `wait`, which represents no outward initiative. Silence is not a failure of cognition.

Endogenous actions can partly regulate the drives that selected them. `rest` restores energy. `explore` and `ask` reduce accumulated curiosity pressure. `seek_connection` creates a limited refractory reduction in affiliation pressure but does not imply that another person responded or that a social need was fully satisfied.

Simply waiting does not create energy.

Recent-action inhibition discourages rapid repetition of the same active intention, particularly repeated connection-seeking. It is a bounded anti-perseveration mechanism, not a randomizer and not a second decision engine.

## Action and outcome

Action selection still occurs before language realization. World outcomes remain separate from intentions. Learned action associations are updated only from observed outcomes. Endogenous self-regulation does not manufacture successful external outcomes.

The adaptive latent substrate remains mechanistic and inaccessible to the subject. Its contribution must continue to be measured with ablation rather than assumed.

## Persistence and time

Persistent subject identity, memories, beliefs, relationships, commitments, adaptive state, and current mechanistic state survive host restart. Swatch Internet Time / Beat Time and UTC remain host-provided temporal representations. State files and clocks are not introspection surfaces.

## Simulation as an architecture gate

Version 0.6 adds longitudinal simulation to the normal acceptance process. Unit tests alone are insufficient for stateful organism dynamics because individually reasonable update rules can compose into saturation, perseveration, or permanent emotional escalation over hundreds of cycles.

The regulated candidate is tested against a preserved v0.5 baseline as well as focused v0.6 regulation probes. The simulation harness must exercise paired histories, epistemic integrity, commitment consequences, memory influence without explicit recall prompts, adaptive-core ablation, language lesion, quiet-time boundedness, persistence/restart, and multi-day relationship change.

A passing simulation demonstrates bounded causal behavior under those scenarios. It does not demonstrate phenomenal consciousness, human equivalence, or psychological validity outside the tested regimes.

## Language model boundary

Model-facing private cognition and expression remain downstream of subject-access projection. No regulation change in v0.6 relaxes this boundary. The architecture must remain functional when model services are absent.

## Future modalities

Vision, audio, robotics, XR, touch, proprioception, interoception, avatars, and richer embodiment remain future product surfaces. Their machine representations must cross the same subject-access firewall before becoming available to the simulated subject.
