# Situated sensorimotor continuity in MicroPsiDUCK v0.10

## Purpose

This increment closes several causal gaps exposed after the TinyPersonaEngine spatial-access and Jelly room integrations. It does not add another cognitive architecture. It strengthens the existing world -> sensation -> appraisal -> motive -> affordance -> action -> outcome loop so spatial perception, bodily state, and continuing world dynamics can affect one another.

The implementation remains bounded and symbolic. It is not a physics engine, biological physiology model, general navigation system, or proof of human believability.

## Perceptual continuity

`duck/perceptual_workspace_v010.py` adds a bounded subject-side current-scene workspace under schema `micropsi-duck.perceptual-workspace.v1`. It records only what the subject most recently perceived about identifiable entities. It is neither world truth nor autobiographical memory.

Native `SensoryEvidence` and `Percept` can carry an `entity_id`. The workspace classifies a tracked percept as `new`, `changed`, or `stable`. Stable re-observation remains available to appraisal and action selection but does not automatically create another identical autobiographical event. New or changed observations can still be encoded normally. The workspace is included in DUCK's transactional snapshot so restart does not make every currently visible object artificially novel again.

The workspace is deliberately smaller than a full evidence/claim ledger. Contradictory multi-source evidence, delayed observations, source calibration, and event-time versus receipt-time reasoning remain separate future work.

## Bidirectional body coupling

`BodyState` now also carries bounded `autonomic_arousal` and `exertion_load`. `BodyDynamics` decays acute mobilization over time, lets threat/appraisal mobilize the body, and applies realized action effort to energy reserve and fatigue. Failed physical attempts can still cost energy.

This preserves the distinction between appraisal and physiology: appraisal can change body state, but an appraisal score is not itself body truth.

`duck/sensation_v010.py` converts body condition into qualitative interoceptive `SensoryEvidence`. In configured room life those signals enter the same bounded attention selector as external stimuli. Mechanistic body values do not cross the experiential language boundary.

## Locomotion and proprioception

The bounded room now supports `turn_toward`, `approach`, and `step_back` in addition to its prior actions. These actions modify the host-owned observer pose rather than merely returning an abstract success value. Movement can therefore change what is visible or reachable on the next cognitive cycle.

Executed self-motion leaves a bounded proprioceptive sensory consequence. Proprioception is represented as sensory evidence and can compete for attention rather than directly editing subject belief.

The current room still uses simple Euclidean motion with no pathfinding, collision mesh, doors-as-navigation-topology, terrain, or multi-room graph. Those remain future navigation work.

## Realized execution consequences

`ExecutionOutcome` separates action success/valence/description from realized physical effort and optional displacement. It retains tuple-like access for the historical room tests while allowing current host code to consume structured consequences.

Affordance `effort` remains a prediction/availability property used during action evaluation. Realized effort is applied only after the world executes the selected action. This preserves the distinction between predicted action cost and what physically happened.

## Autonomous room processes

`RoomProcess` adds a small host-owned external-dynamics mechanism. Bounded processes can move an object/person, toggle an openable object, or change a sound on a periodic schedule. The process advances as part of world time whether or not the subject attends to its result.

Person motion can generate observable approaching/receding cues when spatially accessible. This is external-world behavior, not a theory-of-mind model and not a second DUCK agent. Rich social policies remain future work.

## Authority boundaries

The increment preserves the current authority doctrine:

- `EnvironmentDynamicsState` / `RoomState` own external truth and pose.
- `BodyState` owns simulated physical condition.
- `SensoryEvidence` is apparent evidence, not truth.
- `PerceptualWorkspaceState` is the subject's bounded current-scene continuity, not world truth.
- autobiographical memory records selected lived events, not every unchanged sensor refresh.
- appraisal remains subject-dependent interpretation.
- affordances describe available possibilities and costs, never externally supplied utility.
- the organism selects and validates actions.
- the world executes supported physical consequences.
- mechanistic telemetry remains outside the experiential firewall.

## Current loop

```text
WORLD / ROOM DYNAMICS
        |
        v
SPATIAL ACCESS + BODY SENSORS
        |
        v
BOUNDED ATTENTION
        |
        v
PERCEPT
        |
        +----> PERCEPTUAL WORKSPACE
        |          new / changed / stable
        v
SUBJECT-DEPENDENT APPRAISAL <----> BODY MOBILIZATION
        |
        v
MOTIVES / MODULATION
        |
        v
GROUNDED AFFORDANCES
        |
        v
ACTION SELECTION
        |
        v
WORLD EXECUTION
        |
        +----> pose/world change
        +----> realized effort -> BODY
        +----> proprioceptive consequence
        |
        v
OUTCOME LEARNING
        |
        v
NEXT WORLD/PERCEPTUAL CYCLE
```

## Deliberately remaining work

The next useful extensions should be driven by observed behavioral need rather than subsystem count. The clearest remaining capabilities are:

1. an immutable evidence/claim ledger for cumulative, contradictory, delayed, and duplicate observations;
2. richer navigation/topology beyond one-step Euclidean approach;
3. host-owned person policies for meaningful autonomous social interaction;
4. a bounded multimodal situational workspace with focal versus peripheral context;
5. procedural memory so repeated successful deliberation can become learned skill/habit;
6. explicit impasse states that recruit planning/memory/optional executive cognition only when automatic procedure is insufficient;
7. context-conditioned causal transition learning and the other already-recorded backlog items;
8. independent continuing-character believability assessment.

These are not automatically approved implementation requirements. The improvement loop should first establish the behavioral failure they address and check donor literature/code before adding them.
