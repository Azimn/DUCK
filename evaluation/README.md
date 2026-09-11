# Duckhunter Conversational Evaluation

This directory contains evaluation infrastructure only. It does not redefine the DUCK v0.10 cognitive architecture under test.

## Frozen subject origin

`fixtures/pretorius_origin_v1.json` is the common authored origin for the development character, Doctor Septimus Pretorius. It projects the preserved character invariants and the frozen Wayfarer Pretorius cartridge into a framework-neutral identity payload. Accumulated runtime state is excluded.

The origin includes the same authored identity, role, worldview, moral boundaries, interaction tendencies, voice constraints, and expression landmarks that may be supplied to every condition. A framework may operationalize those facts differently. That difference is part of the experiment. A condition may not receive additional character facts privately during scoring.

The Wayfarer adapter additionally verifies the exact frozen source cartridge SHA-256 recorded in the origin before a scored session can begin.

## Comparison conditions

A scored campaign requires four conditions. `plain_history` receives the frozen origin plus raw dialogue history and no explicit continuity model. `strong_memory` receives the same origin plus deterministic retrieval, a qualitative relationship summary, open commitments, and recent dialogue. `duck_v010` runs the current DUCK host and uses the common origin only at the authorized public renderer boundary. `wayfarer` runs through the external JSONL adapter and a frozen Wayfarer checkout.

The four conditions must report the same model ID and the same origin digest. The first three use DUCK's `OpenAICompatiblePort`. The Wayfarer bridge installs Wayfarer's public `ExternalChatRenderer` around that same port, so it uses the same endpoint and model rather than a second provider. The comparison disables DUCK inner speech and Wayfarer's external renderer provides zero-effect private cognition, leaving one shared-model expression call per conversational turn in each condition.

A renderer fallback in Wayfarer is treated as an invalid scored response rather than silently accepted.

## Model configuration

Set one OpenAI-compatible endpoint and one model for the campaign. For a local Ollama installation, the base endpoint can be `http://127.0.0.1:11434/v1`; `OpenAICompatiblePort` appends `/chat/completions`.

PowerShell example:

```powershell
$env:DUCK_LLM_ENDPOINT = "http://127.0.0.1:11434/v1"
$env:DUCK_LLM_MODEL = "qwen3:8b"
```

Use an already installed model. Model installation or tuning is a separate decision from evidence collection.

## Frozen-input campaign

`prompts/pretorius_development_v1.json` is the first development conversation. It contains identity pressure, epistemic disagreement, relationship strain and repair, a promise, grounded recall, a false-memory trap, coercive devotion, worldview discussion, repeated pressure, and a final relationship judgment.

Use a fresh state root for each replicate. Reusing a state root intentionally continues the prior subjects and is therefore a different experiment.

```powershell
python -m duck.continuity_campaign `
  --origin evaluation/fixtures/pretorius_origin_v1.json `
  run-frozen `
  --prompts evaluation/prompts/pretorius_development_v1.json `
  --output evaluation/runs/pretorius-frozen-001 `
  --state-root .duckhunter/pretorius-frozen-001 `
  --seed 91 `
  --wayfarer-command python tools/wayfarer_duckhunter_bridge.py C:\path\to\wayfarer\source
```

The Wayfarer source path must be the directory that contains the `persona_engine` package and its frozen `cartridges/pretorius.snp`.

The runner writes `blind_transcripts.json`, `blind_key.json`, and `manifest.json`. Raters should receive the transcript and rating protocol but not the blind key. The key should remain sealed until ratings are frozen.

## Adaptive-conversation campaign

Adaptive sessions answer a different question. Every condition receives the same opening, then the human conversation partner responds naturally to what that condition actually says. Sessions are identified only by randomized labels and their order is randomized. These transcripts must not be pooled with frozen-input scores.

```powershell
python -m duck.adaptive_campaign `
  --origin evaluation/fixtures/pretorius_origin_v1.json `
  --output evaluation/runs/pretorius-adaptive-001 `
  --state-root .duckhunter/pretorius-adaptive-001 `
  --opening "Hello. How are you?" `
  --max-turns 20 `
  --seed 91 `
  --wayfarer-command python tools/wayfarer_duckhunter_bridge.py C:\path\to\wayfarer\source
```

Entering `/end`, `/quit`, or `/next` ends the current blinded session.

## Rating and interpretation

`rating_protocol_v1.json` freezes the rating dimensions and the absolute-quality gate before transcripts are inspected. Character fidelity, continuity, naturalness, epistemic discipline, appropriate behavioral consequence, and overall quality remain separate dimensions. The protocol also records severe failure flags such as fabricated autobiographical memory and identity collapse.

Comparative rank never rescues an inadequate condition. A condition can outperform another and still fail the absolute-quality gate. Fewer than three independent raters may produce a provisional development result, but not a nonprovisional claim under this protocol.

Ratings can be aggregated while still blinded:

```powershell
python -m duck.campaign_scoring `
  --ratings evaluation/ratings/pretorius-frozen-001.json `
  --protocol evaluation/rating_protocol_v1.json `
  --output evaluation/runs/pretorius-frozen-001/blind-rating-summary.json
```

Only after ratings are frozen should the mapping be supplied:

```powershell
python -m duck.campaign_scoring `
  --ratings evaluation/ratings/pretorius-frozen-001.json `
  --protocol evaluation/rating_protocol_v1.json `
  --blind-key evaluation/runs/pretorius-frozen-001/blind_key.json `
  --output evaluation/runs/pretorius-frozen-001/unblinded-rating-summary.json
```

The scoring utility intentionally does not declare a single scalar winner. It reports whether each condition clears the absolute gate and preserves dimension-level tradeoffs for interpretation.

## Causal evidence remains separate

The conversational comparison measures experienced quality and observable continuity. Matched-checkpoint interventions and ablations remain the causal layer. A public response that changes because prior experience reached an authorized renderer path can count as a behavioral consequence even when the coarse action label is unchanged. Conversely, an internal label change with identical delivered conduct is not sufficient evidence of meaningful public continuity at that opportunity.

A null ablation result is recorded as no demonstrated contribution under those test conditions. It is not automatically interpreted as proof that the component is unnecessary.

## Generalization

Pretorius is a development character because both DUCK and Wayfarer work have already been shaped around him. Results from this fixture must not be treated as generalization. After the development protocol stabilizes, new characters and situations should be authored independently of the tested mechanisms and run without retuning the architecture to each holdout.
