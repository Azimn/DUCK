"""Fail fast when MicroPsiDUCK documentation authority drifts."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURRENT_ARCHITECTURE = "docs/ARCHITECTURE_v0.10.md"
CURRENT_MILESTONE = "docs/MILESTONE_0_10.md"
CURRENT_FIREWALL = "docs/EXPERIENTIAL_FIREWALL_v0.10.md"
CURRENT_INDEX = "docs/INDEX.md"
CURRENT_STATUS = "docs/STATUS.md"
REQUIRED = (
    "README.md",
    CURRENT_ARCHITECTURE,
    CURRENT_MILESTONE,
    CURRENT_FIREWALL,
    CURRENT_INDEX,
    CURRENT_STATUS,
    "docs/MICROPSI_MODERNIZATION_v0.10.md",
    "docs/ARCHITECTURE_v0.9.md",
    "docs/MILESTONE_0_9.md",
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
    firewall = _read(CURRENT_FIREWALL)

    for path in (CURRENT_ARCHITECTURE, CURRENT_MILESTONE, CURRENT_FIREWALL, CURRENT_INDEX, CURRENT_STATUS):
        if path not in readme:
            errors.append(f"README.md must point to current authority file: {path}")

    if "MicroPsiDUCK" not in readme or "MicroPsiDUCK" not in architecture:
        errors.append("README and current architecture must identify the v0.10 line as MicroPsiDUCK")

    for historical in (
        "ARCHITECTURE_v0.9.md",
        "ARCHITECTURE_v0.8.md",
        "ARCHITECTURE_v0.7.md",
        "ARCHITECTURE_v0.6.md",
        "ARCHITECTURE_v0.5.md",
        "ARCHITECTURE_v0.1.md",
    ):
        if historical not in index:
            errors.append(f"docs/INDEX.md must preserve {historical} as historical architecture")
    if "historical" not in index.lower() and "preserved" not in index.lower():
        errors.append("docs/INDEX.md must explicitly classify older architecture as historical or preserved")
    if "DUCK_Unified_Subject_Architecture_Design_Spec_v0.3" not in index:
        errors.append("docs/INDEX.md must explicitly classify the older broad v0.3 document")
    if "not the current architecture" not in index:
        errors.append("docs/INDEX.md must state that donor-era v0.3 is not the current architecture")

    required_architecture_phrases = (
        "Needs create motives. Motives organize cognition.",
        "continuous state dynamics",
        "Associative activation substrate",
        "Global cognitive modulation",
        "Experiential firewall",
        "ExperientialFrame",
        "Private interior persistence",
        "Renderer boundary",
        "Language lesion",
        "Version 0.9 remains available on `main`",
    )
    architecture_lower = architecture.lower()
    for phrase in required_architecture_phrases:
        if phrase.lower() not in architecture_lower:
            errors.append(f"current architecture is missing invariant text: {phrase}")

    required_milestone_phrases = (
        "persistent competing motives",
        "nontrivial bridge case",
        "operating-regime effects",
        "ExperientialFrame",
        "versioned and persistent",
        "public renderer",
        "language-lesion testing",
        "process restart",
        "longitudinal testing",
        "v0.9 API identity",
    )
    milestone_lower = milestone.lower()
    for phrase in required_milestone_phrases:
        if phrase.lower() not in milestone_lower:
            errors.append(f"current milestone is missing acceptance/scope text: {phrase}")

    required_firewall_phrases = (
        "partial access",
        "ExperientialFrame",
        "first-person experiential prose only",
        "versioned `PrivateInteriorState`",
        "Public interaction results",
        "renderer is an expression surface, not subject authority",
    )
    firewall_lower = firewall.lower()
    for phrase in required_firewall_phrases:
        if phrase.lower() not in firewall_lower:
            errors.append(f"experiential firewall contract is missing required text: {phrase}")

    status_lower = status.lower()
    if "subject-access firewall remains mandatory" not in status_lower and "experiential firewall" not in status_lower:
        errors.append("STATUS.md must preserve the first-person firewall as mandatory")
    if "No donor package is a runtime dependency." not in status:
        errors.append("STATUS.md must state that donor packages are not runtime dependencies")
    if "v0.9" not in status_lower or "main" not in status_lower:
        errors.append("STATUS.md must identify v0.9 on main as the preserved baseline")

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
        print("MicroPsiDUCK documentation contract failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("MicroPsiDUCK documentation contract OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
