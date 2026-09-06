# DUCK Current Status

Current architecture: `docs/ARCHITECTURE_v0.1.md`

Current milestone: `docs/MILESTONE_0_1.md`

## Implemented

Milestone 0.1 implements the smallest executable Subjective Moment kernel. Developer-visible mechanistic state is projected through `SubjectAccessFirewall` into a bounded subject-accessible representation. Private cognition consumes that representation rather than raw psychological telemetry. Inner speech is optional, and developer diagnostics remain separate from subject-accessible state.

The active implementation is intentionally limited to `duck/mechanics.py`, `duck/access.py`, `duck/subjective.py`, `duck/cognition.py`, and `duck/runtime.py`, plus focused tests.

No memory database, persistence architecture, model-provider integration, camera, microphone, synthetic vision subsystem, synthetic audio subsystem, robotics layer, XR embodiment, cartridge system, or portability framework is part of Milestone 0.1.

## Verified evidence

The milestone commit `592dc7e090511962503a19b3ec222bc1ea669b71` passed the complete repository test suite in GitHub Actions on Python 3.11 and Python 3.12 in workflow run `34008547707`.

The acceptance tests verify that raw float-valued psychological telemetry does not reach private cognition, qualitative experience changes when underlying mechanistic magnitude changes, uncertainty remains ordinary first-person uncertainty rather than a numeric confidence report, hidden causes can remain introspectively unavailable, developer diagnostics remain separate, and behavior can be influenced without generated inner prose.

## Next experiment

The next research question is continuity of consequence:

> Does something that happens to the subject alter the subject who encounters the next moment?

The experiment should first demonstrate the failure with the current minimal kernel. Only then should a Milestone 0.2 mechanism be selected. Lived consequence, memory provenance, temporal continuity, prospective commitments, and objective-world versus subjective-belief separation are candidate mechanisms, not pre-approved architecture.

## Scope status

The older `Azimn/persona_engine_PYTHONX` repository remains a donor archive. Its broad DUCK v0.3 specification and other Wayfarer-era documents are not current architecture for this repository.

Vision, audio, touch, proprioception, vestibular sensing, interoception, avatars, robotics, XR, body transfer, and multimodal binding remain nonbinding future scope. The only retained cross-modal rule is that future machine representations must cross the subject-access boundary before they become available to the simulated subject.
