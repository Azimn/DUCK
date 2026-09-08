"""Persistent v0.10 host with private experiential-state isolation."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
import tempfile
from typing import Any

from .language import ApprovedLanguagePacket, DeterministicExpression, ExpressionProvider
from .living import LivingStep, RuleEventInterpreter, SubjectState, WorldEvent
from .living_v010 import LivingDuck
from .subjective import PrivateInteriorState
from .temporal import stamp


@dataclass(frozen=True)
class InteractionResultV010:
    """Public v0.10 interaction result with no private interior fields."""

    response_text: str
    selected_action: str
    action_id: str
    tick: int


class PersistentDuckHostV010:
    """v0.10 host separating durable private interior from public expression."""

    def __init__(
        self,
        root: str | Path,
        duck: LivingDuck,
        *,
        expression: ExpressionProvider | None = None,
        interpreter=None,
    ) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.state_path = self.root / "subject.json"
        self.interior_path = self.root / "private_interior.json"
        self.journal_path = self.root / "events.jsonl"
        self.duck = duck
        self.expression = expression or DeterministicExpression()
        self.interpreter = interpreter or RuleEventInterpreter()
        self.private_interior = self._load_private_interior()

    @classmethod
    def open(
        cls,
        root: str | Path,
        *,
        name: str = "Duck",
        subject_id: str | None = None,
        cognition=None,
        expression: ExpressionProvider | None = None,
        interpreter=None,
    ) -> "PersistentDuckHostV010":
        root_path = Path(root)
        state_path = root_path / "subject.json"
        if state_path.exists():
            state = SubjectState.from_dict(json.loads(state_path.read_text(encoding="utf-8")))
        else:
            state = SubjectState.create(name=name, subject_id=subject_id)
        return cls(
            root_path,
            LivingDuck(state, cognition=cognition),
            expression=expression,
            interpreter=interpreter,
        )

    def _load_private_interior(self) -> PrivateInteriorState | None:
        if not self.interior_path.exists():
            return None
        payload = json.loads(self.interior_path.read_text(encoding="utf-8"))
        return PrivateInteriorState.from_dict(payload)

    def _capture_private_interior(self, step: LivingStep) -> None:
        self.private_interior = PrivateInteriorState.capture(
            self.duck.last_experience,
            step.inner_cognition.thought,
        )

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
        state_payload = json.dumps(self.duck.state.to_dict(), ensure_ascii=False, indent=2, sort_keys=True)
        self._atomic_write(self.state_path, state_payload)
        if self.private_interior is not None:
            interior_payload = json.dumps(
                self.private_interior.to_dict(),
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
            self._atomic_write(self.interior_path, interior_payload)

    def _append_journal(self, event: dict[str, Any]) -> None:
        record = dict(event)
        record["time"] = asdict(stamp(int(record.get("tick", self.duck.state.tick))))
        with self.journal_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    def interact(self, text: str, *, speaker: str = "user", allow_inner_speech: bool = True) -> InteractionResultV010:
        event = self.interpreter.interpret(text, source=speaker)
        step = self.duck.step(event, allow_inner_speech=allow_inner_speech)
        self._capture_private_interior(step)
        if self.private_interior is None:
            raise RuntimeError("private interior capture failed")
        packet = ApprovedLanguagePacket.from_private_interior(
            self.private_interior,
            user_text=text,
            selected_action=step.selected_action,
            character_name=self.duck.state.name,
        )
        response = self.expression.render(packet)
        self._append_journal(
            {
                "type": "interaction",
                "tick": step.tick,
                "speaker": speaker,
                "input": text,
                "selected_action": step.selected_action,
                "action_id": step.action_id,
                "response": response,
                "recalled_memory_ids": list(step.recalled_memory_ids),
            }
        )
        self.save()
        return InteractionResultV010(response, step.selected_action, step.action_id, step.tick)

    def observe(self, event: WorldEvent, *, allow_inner_speech: bool = True) -> LivingStep:
        step = self.duck.step(event, allow_inner_speech=allow_inner_speech)
        self._capture_private_interior(step)
        self._append_journal(
            {
                "type": "world_event",
                "tick": step.tick,
                "event": asdict(event),
                "selected_action": step.selected_action,
                "action_id": step.action_id,
            }
        )
        self.save()
        return step

    def heartbeat(self, count: int = 1, *, allow_inner_speech: bool = True) -> list[LivingStep]:
        steps: list[LivingStep] = []
        for _ in range(max(0, int(count))):
            step = self.duck.heartbeat(allow_inner_speech=allow_inner_speech)
            steps.append(step)
            self._capture_private_interior(step)
            self._append_journal(
                {
                    "type": "heartbeat",
                    "tick": step.tick,
                    "selected_action": step.selected_action,
                    "action_id": step.action_id,
                }
            )
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
        self.duck.resolve_outcome(action_id, success=success, valence=valence, description=description, tags=tags)
        self._append_journal(
            {
                "type": "outcome",
                "tick": self.duck.state.tick,
                "action_id": action_id,
                "success": float(success),
                "valence": float(valence),
                "description": description,
                "tags": list(tags),
            }
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
            "active_plan_count": len(self.duck.plans(status="active")),
            "completed_plan_count": len(self.duck.plans(status="completed")),
            "pending_action": state.pending_action.name if state.pending_action else None,
            "recent_actions": list(state.recent_actions[-8:]),
            "private_interior_schema": self.private_interior.schema_version if self.private_interior else None,
        }
