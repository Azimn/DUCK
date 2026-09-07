"""Fail fast when DUCK's documentation authority drifts."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURRENT_ARCHITECTURE = "docs/ARCHITECTURE_v0.9.md"
CURRENT_MILESTONE = "docs/MILESTONE_0_9.md"
CURRENT_INDEX = "docs/INDEX.md"
CURRENT_STATUS = "docs/STATUS.md"
REQUIRED = (
    "README.md",
    CURRENT_ARCHITECTURE,
    CURRENT_MILESTONE,
    CURRENT_INDEX,
    CURRENT_STATUS,
    "docs/PLANNING_PHASE_v0.9_NOTES.md",
    "docs/PROVENANCE.md",
    "docs/DONOR_AUDIT_v0.1.md",
)


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def check() -> list[str]:
    errors: list[str] = []
    for relative in REQUIRED:
        if not (ROOT / relative).is_file():
            errors.append(f"missing required documentation file: {relative}")
    if errors:
        return errors

    readme = _read("README.md")
    index = _read(CURRENT_INDEX)
    status = _read(CURRENT_STATUS)
    architecture = _read(CURRENT_ARCHITECTURE)
    milestone = _read(CURRENT_MILESTONE)

    for path in (CURRENT_ARCHITECTURE, CURRENT_MILESTONE, CURRENT_INDEX, CURRENT_STATUS):
        if path not in readme:
            errors.append(f"README.md must point to current authority file: {path}")

    for historical in ("ARCHITECTURE_v0.8.md", "ARCHITECTURE_v0.7.md", "ARCHITECTURE_v0.6.md", "ARCHITECTURE_v0.5.md", "ARCHITECTURE_v0.1.md"):
        if historical not in index:
            errors.append(f"docs/INDEX.md must preserve {historical} as historical architecture")
    if "historical" not in index.lower():
        errors.append("docs/INDEX.md must explicitly classify older architecture as historical")
    if "DUCK_Unified_Subject_Architecture_Design_Spec_v0.3" not in index:
        errors.append("docs/INDEX.md must explicitly classify the older broad v0.3 document")
    if "not the current architecture" not in index:
        errors.append("docs/INDEX.md must state that donor-era v0.3 is non-current")

    required_architecture_phrases = (
        "The machinery may know numbers. The subject does not.",
        "What happens to the subject must be able to change the subject who encounters the next moment.",
        "An intention may persist without continuously occupying attention",
        "A goal may arise from lived experience rather than from an external instruction.",
        "Plans are hypotheses, not scripts.",
        "Counterfactual route selection",
        "Hierarchical subgoals",
        "Outcome-driven replanning",
        "subject-access firewall remains mandatory",
        "Inner speech is optional.",
        "The LLM remains an organ, not the organism.",
    )
    architecture_lower = architecture.lower()
    for phrase in required_architecture_phrases:
        if phrase.lower() not in architecture_lower:
            errors.append(f"current architecture is missing invariant text: {phrase}")

    required_milestone_phrases = (
        "endogenous goal formation",
        "counterfactual route",
        "hierarchical subgoals",
        "failed route",
        "outcome memory",
        "process restart",
        "ordinary experience",
        "subject-access firewall",
        "python -m duck.planning_evaluation",
        "python -m duck.planning_simulation",
    )
    milestone_lower = milestone.lower()
    for phrase in required_milestone_phrases:
        if phrase.lower() not in milestone_lower:
            errors.append(f"current milestone is missing acceptance/scope text: {phrase}")

    status_lower = status.lower()
    if "subject-access firewall remains mandatory" not in status_lower:
        errors.append("STATUS.md must preserve the subject-access firewall as mandatory")
    if "No donor package is a runtime dependency." not in status:
        errors.append("STATUS.md must state that donor packages are not runtime dependencies")
    if "endogenous goal formation" not in status_lower or "counterfactual" not in status_lower:
        errors.append("STATUS.md must record the v0.9 endogenous-planning phase")
    if "motivated prospective agency" not in status_lower:
        errors.append("STATUS.md must preserve v0.8 motivated prospective-agency evidence")
    if "thirty-day" not in status_lower or "longitudinal" not in status_lower:
        errors.append("STATUS.md must preserve prior longitudinal simulation evidence")

    legacy_roots = (
        ROOT / "docs" / "DUCK_Unified_Subject_Architecture_Design_Spec_v0.3.md",
        ROOT / "docs" / "DUCK_Subjective_Access_Phase_One_Implementation_Spec_v0.1.md",
    )
    for legacy in legacy_roots:
        if legacy.exists():
            errors.append(f"legacy donor/draft document is in active docs root: {legacy.relative_to(ROOT)}")
    return errors


def main() -> int:
    errors = check()
    if errors:
        print("DUCK documentation contract failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("DUCK documentation contract OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())