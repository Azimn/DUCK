"""Public persistence host for the composed MicroPsiDUCK v0.10 organism."""
from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path

from .endogenous import EndogenousDynamicsState
from .environment_v010 import EnvironmentDynamicsState, ScheduledWorldEvent
from .expectations_v010 import ExpectationLedgerState
from .host_v010 import InteractionResultV010, PersistentDuckHostV010
from .living import SubjectState, WorldEvent
from .motivated_cognition import MotivatedCognitionState
from .organism_v010 import LivingDuck


class PersistentDuckHostCurrent(PersistentDuckHostV010):
    """Persist subject cognition plus separate expectation, endogenous, and world state."""

    def __init__(
        self,
        root,
        duck,
        *,
        environment_state: EnvironmentDynamicsState | None = None,
        expression=None,
        interpreter=None,
    ) -> None:
        super().__init__(root, duck, expression=expression, interpreter=interpreter)
        self.endogenous_path = self.root / "endogenous_v010.json"
        self.expectations_path = self.root / "expectations_v010.json"
        self.environment_path = self.root / "environment_v010.json"
        self.environment = environment_state or EnvironmentDynamicsState()
        self.environment.normalize()

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
        expectations_path = root_path / "expectations_v010.json"
        environment_path = root_path / "environment_v010.json"

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

        if expectations_path.exists():
            expectation_state = ExpectationLedgerState.from_dict(
                json.loads(expectations_path.read_text(encoding="utf-8"))
            )
        else:
            expectation_state = ExpectationLedgerState()

        if environment_path.exists():
            environment_state = EnvironmentDynamicsState.from_dict(
                json.loads(environment_path.read_text(encoding="utf-8"))
            )
        else:
            environment_state = EnvironmentDynamicsState()

        return cls(
            root_path,
            LivingDuck(
                state,
                cognition=cognition,
                executive=executive,
                cognitive_state=cognitive_state,
                endogenous_state=endogenous_state,
                expectation_state=expectation_state,
            ),
            environment_state=environment_state,
            expression=expression,
            interpreter=interpreter,
        )

    def schedule_world_event(self, event: WorldEvent, *, due_in: int = 1) -> ScheduledWorldEvent:
        """Schedule an external change under host/world authority."""

        record = self.environment.schedule(self.duck.state.tick, event, due_in=due_in)
        self.save()
        return record

    def cancel_world_event(self, event_id: str) -> bool:
        cancelled = self.environment.cancel(event_id)
        if cancelled:
            self.save()
        return cancelled

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
        self._atomic_write(
            self.expectations_path,
            json.dumps(
                self.duck.expectation_state.to_dict(),
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            ),
        )
        self._atomic_write(
            self.environment_path,
            json.dumps(
                self.environment.to_dict(),
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            ),
        )

    def _run_scheduled_world_event(
        self,
        record: ScheduledWorldEvent,
        *,
        allow_inner_speech: bool,
    ):
        event = record.event
        if event.perceived:
            step = self.duck.step(event, allow_inner_speech=allow_inner_speech)
            journal_type = "environment_event"
        else:
            # Unperceived world change belongs to host truth. It cannot be allowed
            # to alter appraisal, memory, belief, or expectation resolution as though
            # the subject sensed it.
            for key, text in event.world_facts:
                self.duck.state.world_facts[str(key)] = str(text)
            step = self.duck.heartbeat(allow_inner_speech=allow_inner_speech)
            journal_type = "environment_hidden_change"

        self._capture_private_interior(step)
        self.environment.complete(record.event_id)
        self._append_journal(
            {
                "type": journal_type,
                "tick": step.tick,
                "scheduled_event_id": record.event_id,
                "event": asdict(event),
                "selected_action": step.selected_action,
                "action_id": step.action_id,
            }
        )
        return step

    def heartbeat(self, count: int = 1, *, allow_inner_speech: bool = True) -> list:
        """Advance time, delivering due host/world events before quiet organism beats."""

        steps = []
        for _ in range(max(0, int(count))):
            due = self.environment.next_due(self.duck.state.tick + 1)
            if due is not None:
                step = self._run_scheduled_world_event(
                    due,
                    allow_inner_speech=allow_inner_speech,
                )
            else:
                step = self.duck.heartbeat(allow_inner_speech=allow_inner_speech)
                self._capture_private_interior(step)
                self._append_journal(
                    {
                        "type": "heartbeat",
                        "tick": step.tick,
                        "selected_action": step.selected_action,
                        "action_id": step.action_id,
                    }
                )
            steps.append(step)
        self.save()
        return steps

    def status(self) -> dict[str, object]:
        status = dict(super().status())
        status.update(
            {
                "endogenous_schema": self.duck.endogenous_state.schema_version,
                "endogenous_latched_signals": sorted(self.duck.endogenous_state.latched_signals),
                "endogenous_emission_counts": dict(sorted(self.duck.endogenous_state.emission_counts.items())),
                "expectation_schema": self.duck.expectation_state.schema_version,
                "active_expectation_count": len(self.duck.expectation_state.active()),
                "environment_schema": self.environment.schema_version,
                "scheduled_world_event_count": len(self.environment.scheduled),
            }
        )
        return status


InteractionResult = InteractionResultV010
PersistentDuckHost = PersistentDuckHostCurrent

__all__ = ["InteractionResult", "PersistentDuckHost", "PersistentDuckHostCurrent"]
