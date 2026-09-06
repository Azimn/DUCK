"""Fail fast when DUCK's current documentation authority drifts.

This guard is intentionally small. It does not try to decide architecture.
It makes the current binding files explicit and catches the specific failure mode
where historical donor documents or future-scope plans quietly become current.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CURRENT_ARCHITECTURE = "docs/ARCHITECTURE_v0.1.md"
CURRENT_MILESTONE = "docs/MILESTONE_0_1.md"
CURRENT_INDEX = "docs/INDEX.md"
CURRENT_STATUS = "docs/STATUS.md"
REQUIRED = (
    "README.md",
    CURRENT_ARCHITECTURE,
    CURRENT_MILESTONE,
    CURRENT_INDEX,
    CURRENT_STATUS,
    "docs/PROVENANCE.md",
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

    if "DUCK_Unified_Subject_Architecture_Design_Spec_v0.3" not in index:
        errors.append("docs/INDEX.md must explicitly classify the older broad v0.3 document")
    if "not the current architecture" not in index:
        errors.append("docs/INDEX.md must state that donor-era architecture is non-current")

    if "Future scope, explicitly nonbinding" not in architecture:
        errors.append("current architecture must preserve an explicit nonbinding future-scope section")
    if "No modality-specific schema should be added until" not in architecture:
        errors.append("current architecture must preserve evidence-before-modality scope discipline")

    if "cameras, microphones" not in milestone:
        errors.append("current milestone must explicitly exclude camera/microphone integration")
    if "synthetic vision subsystem" not in status or "synthetic audio subsystem" not in status:
        errors.append("STATUS.md must explicitly state that synthetic vision/audio are not current milestone subsystems")

    legacy_roots = (
        ROOT / "docs" / "DUCK_Unified_Subject_Architecture_Design_Spec_v0.3.md",
        ROOT / "docs" / "DUCK_Subjective_Access_Phase_One_Implementation_Spec_v0.1.md",
    )
    for legacy in legacy_roots:
        if legacy.exists():
            errors.append(
                f"legacy broad/draft document is in the active docs root: {legacy.relative_to(ROOT)}; "
                "move historical material under an explicitly nonbinding history area instead"
            )

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
