"""Minimal persistence support for historical DUCK regression runtimes.

Historical simulations must not resolve the package-level public host because the
public host changes as new architecture candidates are developed. Subclasses pin a
specific historical LivingDuck implementation while sharing the same narrow
SubjectState persistence contract.
"""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
from typing import Any, ClassVar

from .living import LivingStep, SubjectState, WorldEvent
from .temporal import stamp


class HistoricalPersistentDuckHost:
    """Durable host whose organism class is explicitly supplied by a subclass."""

    duck_class: ClassVar[type]

    def __init__(self, root: str | Path, duck) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.state_path = self.root / "subject.json"
        self.duck = duck

    @classmethod
    def open(
        cls,
        root: str | Path,
        *,
        name: str = "Duck",
        subject_id: str | None = None,
    ):
        root_path = Path(root)
        state_path = root_path / "subject.json"
        if state_path.exists():
            state = SubjectState.from_dict(json.loads(state_path.read_text(encoding="utf-8")))
        else:
            state = SubjectState.create(name=name, subject_id=subject_id)
        return cls(root_path, cls.duck_class(state))

    @staticmethod
    def _atomic_write(path: Path, payload: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            delete=False,
            dir=path.parent,
            prefix=path.stem + ".",
            suffix=".tmp",
        ) as handle:
            handle.write(payload)
            temp_name = handle.name
        Path(temp_name).replace(path)

    def save(self) -> None:
        self._atomic_write(
            self.state_path,
            json.dumps(self.duck.state.to_dict(), ensure_ascii=False, indent=2, sort_keys=True),
        )

    def observe(self, event: WorldEvent, *, allow_inner_speech: bool = True) -> LivingStep:
        step = self.duck.step(event, allow_inner_speech=allow_inner_speech)
        self.save()
        return step

    def heartbeat(self, count: int = 1, *, allow_inner_speech: bool = True) -> list[LivingStep]:
        steps: list[LivingStep] = []
        for _ in range(max(0, int(count))):
            steps.append(self.duck.heartbeat(allow_inner_speech=allow_inner_speech))
        self.save()
        return steps

    def resolve_outcome(
        self,
        action_id: str,
        *,
        success: float,
        valence: float,
        description: str,
        tags: tuple[str, ...] = (),
    ) -> None:
        self.duck.resolve_outcome(
            action_id,
            success=success,
            valence=valence,
            description=description,
            tags=tags,
        )
        self.save()

    def status(self) -> dict[str, Any]:
        state = self.duck.state
        temporal = stamp(state.tick)
        return {
            "subject_id": state.subject_id,
            "name": state.name,
            "tick": state.tick,
            "beat_time": temporal.beat_label,
            "bmt_date": temporal.bmt_date,
            "memory_count": len(state.memories),
            "belief_count": len(state.beliefs),
            "commitment_count": len(state.commitments),
            "open_commitments": sum(1 for item in state.commitments.values() if item.status == "open"),
            "pending_action": state.pending_action.name if state.pending_action else None,
            "recent_actions": list(state.recent_actions[-8:]),
        }
