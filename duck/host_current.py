"""Public persistence host for the composed MicroPsiDUCK v0.10 organism."""
from __future__ import annotations

import json
from pathlib import Path

from .endogenous import EndogenousDynamicsState
from .host_v010 import InteractionResultV010, PersistentDuckHostV010
from .living import SubjectState
from .motivated_cognition import MotivatedCognitionState
from .organism_v010 import LivingDuck


class PersistentDuckHostCurrent(PersistentDuckHostV010):
    """Persist subject, motivated cognition, private interior, and scheduler state."""

    def __init__(self, root, duck, *, expression=None, interpreter=None) -> None:
        super().__init__(root, duck, expression=expression, interpreter=interpreter)
        self.endogenous_path = self.root / "endogenous_v010.json"

    @classmethod
    def open(
        cls,
        root: str | Path,
        *,
        name: str = "Duck",
        subject_id: str | None = None,
        cognition=None,
        executive=None,
        expression=None,
        interpreter=None,
    ) -> "PersistentDuckHostCurrent":
        root_path = Path(root)
        state_path = root_path / "subject.json"
        cognitive_path = root_path / "cognition_v010.json"
        endogenous_path = root_path / "endogenous_v010.json"

        if state_path.exists():
            state = SubjectState.from_dict(json.loads(state_path.read_text(encoding="utf-8")))
        else:
            state = SubjectState.create(name=name, subject_id=subject_id)

        if cognitive_path.exists():
            cognitive_state = MotivatedCognitionState.from_dict(
                json.loads(cognitive_path.read_text(encoding="utf-8"))
            )
        else:
            cognitive_state = MotivatedCognitionState()

        if endogenous_path.exists():
            endogenous_state = EndogenousDynamicsState.from_dict(
                json.loads(endogenous_path.read_text(encoding="utf-8"))
            )
        else:
            endogenous_state = EndogenousDynamicsState()

        return cls(
            root_path,
            LivingDuck(
                state,
                cognition=cognition,
                executive=executive,
                cognitive_state=cognitive_state,
                endogenous_state=endogenous_state,
            ),
            expression=expression,
            interpreter=interpreter,
        )

    def save(self) -> None:
        super().save()
        self._atomic_write(
            self.endogenous_path,
            json.dumps(
                self.duck.endogenous_state.to_dict(),
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            ),
        )

    def status(self) -> dict[str, object]:
        status = dict(super().status())
        status.update(
            {
                "endogenous_schema": self.duck.endogenous_state.schema_version,
                "endogenous_latched_signals": sorted(self.duck.endogenous_state.latched_signals),
                "endogenous_emission_counts": dict(sorted(self.duck.endogenous_state.emission_counts.items())),
            }
        )
        return status


InteractionResult = InteractionResultV010
PersistentDuckHost = PersistentDuckHostCurrent

__all__ = ["InteractionResult", "PersistentDuckHost", "PersistentDuckHostCurrent"]
