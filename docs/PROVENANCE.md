# Project provenance

DUCK is a clean implementation line created after extensive experimentation in `Azimn/persona_engine_PYTHONX`.

The older repository contains Wayfarer, the DUCK future-build experiments, model portability work, memory systems, embodiment scaffolding, cartridge systems, persistence mechanisms, evaluators, and many abandoned or superseded design paths.

This repository does not import that codebase as a dependency and does not treat it as the current architecture.

It is retained as a donor archive. A mechanism may be transplanted, rewritten, or adapted when a concrete behavioral failure in this repository establishes the need for it. When that occurs, the new implementation should document the donor concept and the reason it was introduced.

The first concrete defect motivating this clean line was that private cognition in the older engine could receive raw relationship and pressure values. DUCK v0.1 introduces a subject-access firewall so implementation telemetry cannot automatically become first-person knowledge.
