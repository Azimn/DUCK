"""Persistent host and conversational shell for the integrated DUCK build."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
import tempfile
from typing import Any

from .language import ApprovedLanguagePacket, DeterministicExpression, ExpressionProvider
from .living import LivingDuck, LivingStep, RuleEventInterpreter, SubjectState, WorldEvent


@dataclass(frozen=True)
class InteractionResult:
    response_text: str
    selected_action: str
    action_id: str
    private_thought: str | None
    subjective_state: tuple[str, ...]
    tick: int


class PersistentDuckHost:
    """Owns durable state, event journaling, and user-facing interaction.

    Persistence is intentionally boring JSON plus append-only JSONL. The character
    never reads these files directly; they are host authority.
    """

    def __init__(
        self,
        root: str | Path,
        duck: LivingDuck,
        *,
        expression: ExpressionProvider | None = None,
        interpreter: RuleEventInterpreter | None = None,
    ) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.state_path = self.root / "subject.json"
        self.journal_path = self.root / "events.jsonl"
        self.duck = duck
        self.expression = expression or DeterministicExpression()
        self.interpreter = interpreter or RuleEventInterpreter()

    @classmethod
    def open(
        cls,
        root: str | Path,
        *,
        name: str = "Duck",
        subject_id: str | None = None,
        cognition=None,
        expression: ExpressionProvider | None = None,
    ) -> "PersistentDuckHost":
        root_path = Path(root)
        state_path = root_path / "subject.json"
        if state_path.exists():
            state = SubjectState.from_dict(json.loads(state_path.read_text(encoding="utf-8")))
        else:
            state = SubjectState.create(name=name, subject_id=subject_id)
        return cls(root_path, LivingDuck(state, cognition=cognition), expression=expression)

    def save(self) -> None:
        payload = json.dumps(self.duck.state.to_dict(), ensure_ascii=False, indent=2, sort_keys=True)
        self.root.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=self.root, prefix="subject.", suffix=".tmp") as handle:
            handle.write(payload)
            temp_name = handle.name
        Path(temp_name).replace(self.state_path)

    def _append_journal(self, event: dict[str, Any]) -> None:
        with self.journal_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")

    @staticmethod
    def _subjective_lines(step: LivingStep) -> tuple[str, ...]:
        moment = step.subjective_moment
        lines: list[str] = [item.content for item in moment.impressions]
        lines.extend(item.felt_as for item in moment.tendencies)
        lines.extend(moment.recollections)
        lines.extend(moment.beliefs)
        lines.extend(moment.concerns)
        lines.extend(moment.temporal_context)
        lines.extend(moment.self_context)
        return tuple(dict.fromkeys(line for line in lines if line))

    def interact(self, text: str, *, speaker: str = "user", allow_inner_speech: bool = True) -> InteractionResult:
        event = self.interpreter.interpret(text, source=speaker)
        step = self.duck.step(event, allow_inner_speech=allow_inner_speech)
        packet = ApprovedLanguagePacket.from_moment(
            step.subjective_moment,
            user_text=text,
            private_thought=step.inner_cognition.thought,
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
        return InteractionResult(
            response,
            step.selected_action,
            step.action_id,
            step.inner_cognition.thought,
            self._subjective_lines(step),
            step.tick,
        )

    def observe(self, event: WorldEvent, *, allow_inner_speech: bool = True) -> LivingStep:
        step = self.duck.step(event, allow_inner_speech=allow_inner_speech)
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
            self._append_journal(
                {
                    "type": "heartbeat",
                    "tick": step.tick,
                    "selected_action": step.selected_action,
                    "action_id": step.action_id,
                    "private_thought": step.inner_cognition.thought,
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
        return {
            "subject_id": state.subject_id,
            "name": state.name,
            "tick": state.tick,
            "memory_count": len(state.memories),
            "belief_count": len(state.beliefs),
            "commitment_count": len(state.commitments),
            "open_commitments": sum(1 for item in state.commitments.values() if item.status == "open"),
            "pending_action": state.pending_action.name if state.pending_action else None,
            "recent_actions": list(state.recent_actions[-8:]),
        }
