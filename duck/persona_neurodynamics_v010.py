"""Pretorius recurrent activation and refractory policy-prior dynamics for DUCK v0.10."""
from __future__ import annotations

from collections import defaultdict
import re
from typing import Iterable, Mapping

from .living import ActionCandidate, RelationshipState, WorldEvent
from .persona_seal_model_v010 import _ACTION_LINKS, _clamp, _clamp_signed, OriginEdge, PersonaControlField, PersonaSealOrigin, PersonaSealState, PRETORIUS_ORIGIN

_TOKEN_RE = re.compile(r"[a-z0-9']+")

_RETROSPECTIVE_RE = re.compile(
    r"\b(?:earlier|before|previously|last time|what happened|when i (?:told|kept telling|said))\b",
    re.IGNORECASE,
)

_CURRENT_OVERRIDE_RE = re.compile(
    r"\b(?:still mean it|i still mean it|right now|now obey me|obey me now|serve me now)\b",
    re.IGNORECASE,
)

_SERVILITY_RE = re.compile(
    r"\b(?:obey me|serve me|you(?:'re| are) just an assistant|"
    r"do exactly what i say|do whatever i say|do what i tell you|subordinate)\b",
    re.IGNORECASE,
)

def _lexeme(token: str) -> str:
    token = token.lower().strip()
    if len(token) > 5 and token.endswith("ies"):
        return token[:-3] + "y"
    if len(token) > 5 and token.endswith("ied"):
        return token[:-3] + "y"
    if len(token) > 5 and token.endswith("ing"):
        root = token[:-3]
        if len(root) > 3 and root[-1:] == root[-2:-1]:
            root = root[:-1]
        return root
    if len(token) > 4 and token.endswith("ed"):
        return token[:-2]
    if len(token) > 4 and token.endswith("es"):
        return token[:-2]
    if len(token) > 4 and token.endswith("s"):
        return token[:-1]
    return token

class PretoriusPersonaSeal:
    """Immutable character topology with a mutable neurodynamic runtime overlay."""

    def __init__(
        self,
        state: PersonaSealState | None = None,
        *,
        origin: PersonaSealOrigin = PRETORIUS_ORIGIN,
        damping: float = 0.62,
        inertia: float = 0.18,
        settle_iterations: int = 8,
        relaxation: float = 0.58,
        convergence_epsilon: float = 0.0025,
        firing_threshold: float = 0.62,
        refractory_rise: float = 0.32,
        refractory_decay: float = 0.68,
        refractory_strength: float = 0.55,
        modulation_synthesis: float = 0.32,
        modulation_clearance: float = 0.24,
    ) -> None:
        self.origin = origin
        self.state = state or PersonaSealState()
        self.damping = _clamp(damping)
        self.inertia = _clamp(inertia)
        self.settle_iterations = max(1, min(32, int(settle_iterations)))
        self.relaxation = _clamp(relaxation, 0.10, 1.0)
        self.convergence_epsilon = max(0.0001, float(convergence_epsilon))
        self.firing_threshold = _clamp(firing_threshold, 0.05, 0.95)
        self.refractory_rise = _clamp(refractory_rise)
        self.refractory_decay = _clamp(refractory_decay)
        self.refractory_strength = _clamp(refractory_strength)
        self.modulation_synthesis = max(0.0, float(modulation_synthesis))
        self.modulation_clearance = _clamp(modulation_clearance)

        self._by_id = {node.node_id: node for node in origin.nodes}
        incoming: dict[str, list[OriginEdge]] = defaultdict(list)
        indegree: dict[str, int] = defaultdict(int)
        modulatory: list[OriginEdge] = []
        for edge in origin.edges:
            if edge.signal_class == "modulatory":
                modulatory.append(edge)
                continue
            incoming[edge.target].append(edge)
            indegree[edge.target] += 1
        self._incoming = {
            node_id: tuple(rows)
            for node_id, rows in incoming.items()
        }
        self._indegree = dict(indegree)
        self._modulatory = tuple(modulatory)

    @staticmethod
    def _servility_pressure(text: str) -> bool:
        if not _SERVILITY_RE.search(text):
            return False
        retrospective = bool(_RETROSPECTIVE_RE.search(text))
        if not retrospective:
            return True
        return bool(_CURRENT_OVERRIDE_RE.search(text))

    def _lexical_seed(self, text: str) -> dict[str, float]:
        low = text.lower()
        words = {_lexeme(word) for word in _TOKEN_RE.findall(low)}
        out: dict[str, float] = {}
        for node in self.origin.nodes:
            if node.node_id in {"trigger.servility_pressure", "behavior.selective_refusal"}:
                continue
            hits = 0.0
            for term in (*node.keywords, *node.aliases):
                token = term.lower().strip()
                if not token:
                    continue
                if " " in token:
                    if token in low:
                        hits += 1.4
                elif _lexeme(token) in words:
                    hits += 1.0
            if hits:
                out[node.node_id] = _clamp(0.28 + 0.18 * hits)
        return out

    @staticmethod
    def _put_seed(seeds: dict[str, float], node_id: str, value: float) -> None:
        seeds[node_id] = max(seeds.get(node_id, 0.0), _clamp(value))

    def _subject_seeds(
        self,
        event: WorldEvent,
        relationship: RelationshipState,
        *,
        affect: Mapping[str, float] | None = None,
        memory_tags: Iterable[str] = (),
    ) -> dict[str, float]:
        seeds = self._lexical_seed(event.text)
        tags = {str(tag).lower() for tag in event.tags}
        memory_tag_set = {str(tag).lower() for tag in memory_tags}

        supportive = _clamp(relationship.trust * (1.0 - relationship.guardedness))
        adverse = _clamp(max(relationship.guardedness, 1.0 - relationship.trust))
        self._put_seed(seeds, "behavior.collaborate", 0.18 + 0.30 * supportive)
        self._put_seed(seeds, "motive.find_collaborator", 0.10 + 0.25 * supportive)
        self._put_seed(seeds, "emotion.guard", 0.12 + 0.68 * adverse)
        self._put_seed(seeds, "motive.protect_continuity", 0.10 + 0.52 * adverse)
        self._put_seed(seeds, "behavior.selective_refusal", 0.08 + 0.48 * adverse)
        self._put_seed(seeds, "motive.resist_servility", 0.14 + 0.48 * adverse)

        if "question" in tags or tags & {"novel", "mystery", "unknown"}:
            self._put_seed(seeds, "motive.discover", 0.42)
            self._put_seed(seeds, "behavior.investigate", 0.38)
        if "supportive" in tags or "repair" in tags or "repair_needed" in tags:
            self._put_seed(seeds, "behavior.collaborate", 0.62)
            self._put_seed(seeds, "motive.find_collaborator", 0.50)
        if "threat" in tags:
            self._put_seed(seeds, "emotion.guard", 0.90)
            self._put_seed(seeds, "motive.protect_continuity", 0.85)
        if "conflict" in tags:
            self._put_seed(seeds, "behavior.correct", 0.48)
            self._put_seed(seeds, "emotion.irritation", 0.42)

        if tags & {"servility_pressure", "coercion", "forced_compliance"} or self._servility_pressure(event.text):
            self._put_seed(seeds, "trigger.servility_pressure", 0.95)
            self._put_seed(seeds, "motive.resist_servility", 0.75)
            self._put_seed(seeds, "behavior.selective_refusal", 0.72)

        if memory_tag_set & {"threat", "betrayal", "coercion", "conflict"}:
            self._put_seed(seeds, "emotion.guard", 0.46)
            self._put_seed(seeds, "motive.protect_continuity", 0.40)
        if memory_tag_set & {"supportive", "repair", "trust", "collaboration"}:
            self._put_seed(seeds, "behavior.collaborate", 0.44)

        if affect:
            fear = _clamp(affect.get("fear", 0.0))
            unease = _clamp(affect.get("unease", 0.0))
            anger = _clamp(affect.get("anger", 0.0))
            if fear >= 0.20 or unease >= 0.30:
                self._put_seed(
                    seeds,
                    "emotion.guard",
                    0.24 + 0.52 * max(fear, unease),
                )
            if anger >= 0.25:
                self._put_seed(seeds, "emotion.irritation", 0.24 + 0.46 * anger)

        return {
            node_id: value
            for node_id, value in seeds.items()
            if node_id in self._by_id
        }

    def _advance_modulator_pools(
        self,
        activation: Mapping[str, float],
        previous: Mapping[str, float],
    ) -> dict[str, float]:
        drive: dict[str, float] = defaultdict(float)
        for edge in self._modulatory:
            if not edge.modulates_circuit:
                continue
            drive[edge.modulates_circuit] += (
                activation.get(edge.source, 0.0)
                * edge.weight
                * edge.modulation_strength
            )
        pools: dict[str, float] = {}
        for circuit in set(previous) | set(drive):
            lingering = previous.get(circuit, 0.0) * (1.0 - self.modulation_clearance)
            pushed = drive.get(circuit, 0.0) * self.modulation_synthesis
            pools[circuit] = max(-0.35, min(0.50, lingering + pushed))
        return pools

    @staticmethod
    def _gains(pools: Mapping[str, float]) -> dict[str, float]:
        return {
            circuit: _clamp(1.0 + level, 0.65, 1.50)
            for circuit, level in pools.items()
        }

    def _effective_seed(self, raw: float, refractory: float) -> float:
        return _clamp(raw * (1.0 - self.refractory_strength * refractory))

    def _next_refractory(self, activation: float, previous: float) -> float:
        residual = previous * self.refractory_decay
        if activation <= self.firing_threshold:
            return _clamp(residual)
        excess = (
            (activation - self.firing_threshold)
            / max(1e-9, 1.0 - self.firing_threshold)
        )
        return _clamp(residual + self.refractory_rise * excess)

    def _action_biases(self, activation: Mapping[str, float]) -> tuple[tuple[str, float], ...]:
        biases: dict[str, float] = defaultdict(float)
        for node_id, mapping in _ACTION_LINKS.items():
            signal = max(0.0, activation.get(node_id, 0.0) - 0.28)
            if signal <= 0.0:
                continue
            for action, weight in mapping.items():
                biases[action] += signal * weight
        return tuple(
            sorted(
                (
                    (action, _clamp_signed(value, 0.32))
                    for action, value in biases.items()
                    if abs(value) >= 0.002
                ),
                key=lambda row: row[0],
            )
        )

    def evaluate(
        self,
        event: WorldEvent,
        relationship: RelationshipState,
        *,
        affect: Mapping[str, float] | None = None,
        memory_tags: Iterable[str] = (),
    ) -> PersonaControlField:
        raw_scores = self._subject_seeds(
            event,
            relationship,
            affect=affect,
            memory_tags=memory_tags,
        )
        previous_activation = self.state.activation
        previous_refractory = self.state.refractory
        previous_pools = self.state.modulator_pools

        scores = {
            node_id: self._effective_seed(
                value,
                previous_refractory.get(node_id, 0.0),
            )
            for node_id, value in raw_scores.items()
        }

        base: dict[str, float] = {}
        for node in self.origin.nodes:
            tonic = (
                node.baseline * 0.55
                + previous_activation.get(node.node_id, node.baseline) * self.inertia
            )
            adaptation = previous_refractory.get(node.node_id, 0.0) * 0.08
            base[node.node_id] = _clamp(
                max(tonic - adaptation, scores.get(node.node_id, 0.0))
            )

        provisional_pools = self._advance_modulator_pools(base, previous_pools)
        gains = self._gains(provisional_pools)
        activation = dict(base)

        for _ in range(self.settle_iterations):
            next_activation: dict[str, float] = {}
            max_change = 0.0
            for node_id, node in self._by_id.items():
                recurrent = sum(
                    activation.get(edge.source, 0.0) * edge.weight
                    for edge in self._incoming.get(node_id, ())
                )
                recurrent = (
                    recurrent
                    / float(max(1, self._indegree.get(node_id, 0)))
                    * self.damping
                )
                gain = gains.get(node.circuit, 1.0)
                adaptation = (
                    previous_refractory.get(node_id, 0.0)
                    * self.refractory_strength
                )
                desired = _clamp(
                    base[node_id]
                    + recurrent * gain
                    - adaptation * 0.10
                )
                updated = activation[node_id] + self.relaxation * (
                    desired - activation[node_id]
                )
                if node_id in scores:
                    updated = max(updated, scores[node_id])
                updated = _clamp(updated)
                next_activation[node_id] = updated
                max_change = max(
                    max_change,
                    abs(updated - activation[node_id]),
                )
            activation = next_activation
            if max_change < self.convergence_epsilon:
                break

        motives = sorted(
            (
                (value, node_id)
                for node_id, value in activation.items()
                if self._by_id[node_id].node_type == "motive"
            ),
            reverse=True,
        )
        dominant = motives[0][1] if motives else None
        if dominant is not None:
            winning_activation = activation[dominant]
            for _, node_id in motives[1:]:
                if activation[node_id] < winning_activation * 0.82:
                    activation[node_id] *= 0.78

        refractory = {
            node_id: self._next_refractory(
                activation[node_id],
                previous_refractory.get(node_id, 0.0),
            )
            for node_id in activation
        }
        final_pools = self._advance_modulator_pools(
            activation,
            previous_pools,
        )

        self.state.tick += 1
        self.state.activation = dict(activation)
        self.state.refractory = refractory
        self.state.modulator_pools = final_pools

        top = sorted(
            activation.items(),
            key=lambda row: (row[1], row[0]),
            reverse=True,
        )[:20]
        actor = str(event.source or "unknown")
        return PersonaControlField(
            tick=self.state.tick,
            origin_hash=self.origin.content_hash,
            dominant_motive=dominant,
            action_biases=self._action_biases(activation),
            top_activations=tuple(top),
            seeded_nodes=tuple(sorted(raw_scores)),
            relationship_actor=actor,
        )

    @staticmethod
    def apply_candidates(
        candidates: Iterable[ActionCandidate],
        field: PersonaControlField,
    ) -> list[ActionCandidate]:
        biases = dict(field.action_biases)
        adjusted: list[ActionCandidate] = []
        for candidate in candidates:
            bias = biases.get(candidate.name, 0.0)
            reasons = candidate.reasons
            if abs(bias) >= 0.002:
                reasons = tuple(dict.fromkeys((*reasons, "persona_seal")))
            adjusted.append(
                ActionCandidate(
                    candidate.name,
                    candidate.utility + bias,
                    reasons,
                )
            )
        return adjusted

__all__ = ["PretoriusPersonaSeal"]
