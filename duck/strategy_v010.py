"""Bounded context for strategy learning, captured at action selection."""
from enum import Enum


class CognitiveRegime(str, Enum):
    BASELINE = "baseline"
    THREATENED = "threatened"
    FATIGUED = "fatigued"
    SOCIALLY_GUARDED = "socially_guarded"
    HIGH_CONFLICT = "high_conflict"


def cognitive_regime(regulatory, appraisal=None, relationship=None):
    if appraisal and appraisal.threat_relevance >= 0.45:
        return CognitiveRegime.THREATENED
    if regulatory.safety_deficit >= 0.6:
        return CognitiveRegime.THREATENED
    if regulatory.energy_deficit >= 0.65:
        return CognitiveRegime.FATIGUED
    if appraisal and appraisal.conflict_relevance >= 0.5:
        return CognitiveRegime.HIGH_CONFLICT
    if relationship and relationship.guardedness >= 0.65:
        return CognitiveRegime.SOCIALLY_GUARDED
    return CognitiveRegime.BASELINE


def contextual_reliability(global_value, contextual_value, contextual_evidence):
    weight = contextual_evidence / (contextual_evidence + 4.0)
    return global_value * (1.0 - weight) + contextual_value * weight
