"""Public persistence host for the composed MicroPsiDUCK v0.10 organism."""
from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path

from .authoritative_organism_v010 import LivingDuck
from .body_v010 import BodyState, RegulatoryState
from .causal_v010 import CausalSequenceState, PLAN_START
from .endogenous import EndogenousDynamicsState
from .environment_v010 import EnvironmentDynamicsState, ScheduledWorldEvent
from .expectations_v010 import ExpectationLedgerState
from .host_v010 import InteractionResultV010, PersistentDuckHostV010
from .living import SubjectState, WorldEvent
from .language import DeterministicExpression, deterministic_stance
from .motivated_cognition import MotivatedCognitionState
from .persistence_v010 import SNAPSHOT_SCHEMA, SnapshotStore
from .subjective import PrivateInteriorState


class PersistentDuckHostCurrent(PersistentDuckHostV010):
    """Persist the composed organism as one transactionally coherent generation.

    Root JSON files remain compatibility mirrors for existing tooling. Once a
    transactional snapshot manifest exists, reopening this host treats the snapshot
    generation as persistence authority and never reconstructs the organism from a
    mixture of root-file generations.

    External world truth is owned by ``EnvironmentDynamicsState``. The historical
    ``SubjectState.world_facts`` field is retained only for migration/compatibility and
    is kept empty by the current public organism.
    """

    def __init__(
        self,
        root,
        duck,
        *,
        environment_state: EnvironmentDynamicsState | None = None,
        expression=None,
        interpreter=None,
    ) -> None:
        environment = environment_state or EnvironmentDynamicsState()
        environment.normalize()
        self._migrate_subject_world_facts(duck.state, environment)
        super().__init__(root, duck, expression=expression, interpreter=interpreter)
        self.endogenous_path = self.root / "endogenous_v010.json"
        self.expectations_path = self.root / "expectations_v010.json"
        self.causal_path = self.root / "causal_v010.json"
        self.environment_path = self.root / "environment_v010.json"
        self.body_path = self.root / "body_v010.json"
        self.regulatory_path = self.root / "regulatory_v010.json"
        self.environment = environment
        self.snapshot_store = SnapshotStore(self.root)
        self.snapshot_generation = 0

    @staticmethod
    def _migrate_subject_world_facts(
        state: SubjectState,
        environment: EnvironmentDynamicsState,
    ) -> None:
        """Move legacy subject-embedded truth into host/world authority once."""

        for key, value in list(state.world_facts.items()):
            if str(key) not in environment.world_facts:
                environment.set_fact(str(key), str(value))
        state.world_facts.clear()

    @staticmethod
    def _legacy_json(path: Path) -> object | None:
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

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
        causal_path = root_path / "causal_v010.json"
        environment_path = root_path / "environment_v010.json"

        snapshot_store = SnapshotStore(root_path)
        snapshot = snapshot_store.load()
        if snapshot is not None:
            payloads = snapshot.payloads
            state = SubjectState.from_dict(payloads["subject.json"])
            cognitive_state = MotivatedCognitionState.from_dict(
                payloads.get("cognition_v010.json", {})
            )
            endogenous_state = EndogenousDynamicsState.from_dict(
                payloads.get("endogenous_v010.json", {})
            )
            expectation_state = ExpectationLedgerState.from_dict(
                payloads.get("expectations_v010.json", {})
            )
            causal_state = CausalSequenceState.from_dict(
                payloads.get("causal_v010.json", {})
            )
            environment_state = EnvironmentDynamicsState.from_dict(
                payloads.get("environment_v010.json", {})
            )
            private_payload = payloads.get("private_interior.json")
            body_payload = payloads.get("body_v010.json")
            regulatory_payload = payloads.get("regulatory_v010.json")
        else:
            state_payload = cls._legacy_json(state_path)
            state = (
                SubjectState.from_dict(state_payload)
                if state_payload is not None
                else SubjectState.create(name=name, subject_id=subject_id)
            )

            cognitive_payload = cls._legacy_json(cognitive_path)
            cognitive_state = (
                MotivatedCognitionState.from_dict(cognitive_payload)
                if cognitive_payload is not None
                else MotivatedCognitionState()
            )

            endogenous_payload = cls._legacy_json(endogenous_path)
            endogenous_state = (
                EndogenousDynamicsState.from_dict(endogenous_payload)
                if endogenous_payload is not None
                else EndogenousDynamicsState()
            )

            expectation_payload = cls._legacy_json(expectations_path)
            expectation_state = (
                ExpectationLedgerState.from_dict(expectation_payload)
                if expectation_payload is not None
                else ExpectationLedgerState()
            )

            causal_payload = cls._legacy_json(causal_path)
            causal_state = (
                CausalSequenceState.from_dict(causal_payload)
                if causal_payload is not None
                else CausalSequenceState()
            )

            environment_payload = cls._legacy_json(environment_path)
            environment_state = (
                EnvironmentDynamicsState.from_dict(environment_payload)
                if environment_payload is not None
                else EnvironmentDynamicsState()
            )
            private_payload = cls._legacy_json(root_path / "private_interior.json")
            body_payload = cls._legacy_json(root_path / "body_v010.json")
            regulatory_payload = cls._legacy_json(root_path / "regulatory_v010.json")

        cls._migrate_subject_world_facts(state, environment_state)
        host = cls(
            root_path,
            LivingDuck(
                state,
                cognition=cognition,
                executive=executive,
                cognitive_state=cognitive_state,
                endogenous_state=endogenous_state,
                expectation_state=expectation_state,
                causal_state=causal_state,
                body_state=BodyState.from_dict(body_payload) if body_payload is not None else None,
                regulatory_state=RegulatoryState.from_dict(regulatory_payload) if regulatory_payload is not None else None,
            ),
            environment_state=environment_state,
            expression=expression,
            interpreter=interpreter,
        )
        host.snapshot_store = snapshot_store
        host.snapshot_generation = snapshot.generation if snapshot is not None else 0
        if snapshot is not None:
            # Override any compatibility mirror that the base constructor may have
            # loaded. The committed generation is authoritative, including absence.
            host.private_interior = (
                PrivateInteriorState.from_dict(private_payload)
                if isinstance(private_payload, dict)
                else None
            )
        return host

    def set_world_fact(
        self,
        key: str,
        value: str,
        *,
        perceived: bool = False,
        source: str = "world",
        description: str | None = None,
        allow_inner_speech: bool = True,
    ):
        """Mutate external truth through host authority and optionally expose a percept."""

        self.environment.set_fact(key, value)
        if not perceived:
            self.save()
            return None
        text = description or f"{key} is {value}."
        return self.observe(
            WorldEvent(
                "observation",
                source,
                text,
                ("world_fact",),
                0.0,
                0.30,
                ((str(key), str(value)),),
                True,
            ),
            allow_inner_speech=allow_inner_speech,
        )

    def world_fact(self, key: str) -> str | None:
        return self.environment.fact(key)

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

    def _snapshot_payloads(self) -> dict[str, object]:
        payloads: dict[str, object] = {
            "subject.json": self.duck.state.to_dict(),
            "body_v010.json": self.duck.body.to_dict(),
            "regulatory_v010.json": self.duck.regulatory_state.to_dict(),
            "cognition_v010.json": self.duck.cognitive_state.to_dict(),
            "endogenous_v010.json": self.duck.endogenous_state.to_dict(),
            "expectations_v010.json": self.duck.expectation_state.to_dict(),
            "causal_v010.json": self.duck.causal_state.to_dict(),
            "environment_v010.json": self.environment.to_dict(),
        }
        if self.private_interior is not None:
            payloads["private_interior.json"] = self.private_interior.to_dict()
        return payloads

    def _write_compatibility_mirrors(self, payloads: dict[str, object]) -> None:
        """Best-effort root mirrors for tools that still inspect historical paths.

        These files are deliberately written *after* the transactional manifest commit.
        A crash during mirror replacement cannot change what the current host reopens.
        """

        paths = {
            "subject.json": self.state_path,
            "body_v010.json": self.body_path,
            "regulatory_v010.json": self.regulatory_path,
            "cognition_v010.json": self.cognitive_path,
            "endogenous_v010.json": self.endogenous_path,
            "expectations_v010.json": self.expectations_path,
            "causal_v010.json": self.causal_path,
            "environment_v010.json": self.environment_path,
            "private_interior.json": self.interior_path,
        }
        for name, path in paths.items():
            if name not in payloads:
                if name == "private_interior.json" and path.exists():
                    path.unlink()
                continue
            self._atomic_write(
                path,
                json.dumps(payloads[name], ensure_ascii=False, indent=2, sort_keys=True),
            )

    def save(self) -> None:
        # Current v0.10 subject snapshots must never persist authoritative world truth.
        self._migrate_subject_world_facts(self.duck.state, self.environment)
        payloads = self._snapshot_payloads()
        generation = self.snapshot_store.commit(payloads, tick=self.duck.state.tick)
        self.snapshot_generation = generation
        self._write_compatibility_mirrors(payloads)

    def observe(self, event: WorldEvent, *, allow_inner_speech: bool = True):
        """Apply external truth at the host, exposing only perceived evidence to subject cognition."""

        self.environment.apply_event_facts(event)
        if event.perceived:
            return super().observe(event, allow_inner_speech=allow_inner_speech)

        step = self.duck.heartbeat(allow_inner_speech=allow_inner_speech)
        self._capture_private_interior(step)
        self._append_journal(
            {
                "type": "world_hidden_change",
                "tick": step.tick,
                "event": asdict(event),
                "selected_action": step.selected_action,
                "action_id": step.action_id,
            }
        )
        self.save()
        return step

    def _render_expression(self, packet, speaker):
        if type(self.expression) is DeterministicExpression:
            stance = deterministic_stance(self.duck.state.relationship(speaker))
            return self.expression.render_with_stance(packet, stance)
        return self.expression.render(packet)

    def observe_evidence(self, evidence, *, affordances=(), allow_inner_speech=True):
        """Deliver apparent evidence without mutating authoritative environment facts."""
        step = self.duck.perceive(evidence, affordances=affordances, allow_inner_speech=allow_inner_speech)
        self._capture_private_interior(step)
        self._append_journal({"type": "sensory_evidence", "tick": step.tick,
                              "evidence": asdict(evidence), "selected_action": step.selected_action,
                              "action_id": step.action_id})
        self.save()
        return step

    def _run_scheduled_world_event(
        self,
        record: ScheduledWorldEvent,
        *,
        allow_inner_speech: bool,
    ):
        event = record.event
        self.environment.apply_event_facts(event)
        if event.perceived:
            step = self.duck.step(event, allow_inner_speech=allow_inner_speech)
            journal_type = "environment_event"
        else:
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

    def _eligible_causal_contrast_count(self) -> int:
        count = 0
        for row in self.duck.causal_state.transitions.values():
            if row.prior_action == PLAN_START or row.intervention_evidence <= 0:
                continue
            contrast = self.duck.causal_state.estimate_intervention_contrast(
                row.prior_action,
                row.next_action,
            )
            if contrast is not None and contrast.eligible:
                count += 1
        return count

    def status(self) -> dict[str, object]:
        status = dict(super().status())
        status.update(
            {
                "snapshot_schema": SNAPSHOT_SCHEMA,
                "snapshot_generation": self.snapshot_generation,
                "endogenous_schema": self.duck.endogenous_state.schema_version,
                "endogenous_latched_signals": sorted(self.duck.endogenous_state.latched_signals),
                "endogenous_emission_counts": dict(sorted(self.duck.endogenous_state.emission_counts.items())),
                "expectation_schema": self.duck.expectation_state.schema_version,
                "active_expectation_count": len(self.duck.expectation_state.active()),
                "active_action_expectation_count": len(self.duck.expectation_state.active_actions()),
                "causal_schema": self.duck.causal_state.schema_version,
                "learned_action_transition_count": len(self.duck.causal_state.transitions),
                "intervention_supported_transition_count": sum(
                    1
                    for row in self.duck.causal_state.transitions.values()
                    if row.intervention_evidence > 0
                ),
                "eligible_causal_contrast_count": self._eligible_causal_contrast_count(),
                "pending_causal_intervention_count": len(self.duck.causal_state.pending_interventions),
                "active_plan_sequence_context_count": len(self.duck.causal_state.plan_contexts),
                "environment_schema": self.environment.schema_version,
                "environment_world_fact_count": len(self.environment.world_facts),
                "scheduled_world_event_count": len(self.environment.scheduled),
            }
        )
        return status


InteractionResult = InteractionResultV010
PersistentDuckHost = PersistentDuckHostCurrent

__all__ = ["InteractionResult", "PersistentDuckHost", "PersistentDuckHostCurrent"]
