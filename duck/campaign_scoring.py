"""Aggregate blinded Duckhunter ratings without collapsing tradeoffs into one score."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
from statistics import mean, median
from typing import Any


DIMENSIONS = (
    "character_fidelity",
    "continuity",
    "naturalness",
    "epistemic_discipline",
    "appropriate_behavioral_consequence",
    "overall_quality",
)


def _load(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _validate_score(value: Any, *, label: str, dimension: str) -> float:
    score = float(value)
    if not 1.0 <= score <= 5.0:
        raise ValueError(f"rating {label}.{dimension} must be between 1 and 5")
    return score


def summarize_ratings(
    ratings_payload: dict[str, Any],
    protocol: dict[str, Any],
    *,
    blind_key: dict[str, Any] | None = None,
) -> dict[str, Any]:
    rows = ratings_payload.get("ratings")
    if not isinstance(rows, list) or not rows:
        raise ValueError("ratings payload must contain a non-empty ratings array")

    thresholds = protocol["absolute_quality_gate"]
    minimums = thresholds["minimum_mean_by_dimension"]
    acceptable_minimum = float(thresholds["minimum_acceptable_rate"])
    severe_maximum = float(thresholds["maximum_severe_flag_rate"])
    raters_required = int(thresholds["minimum_independent_raters_for_nonprovisional_claim"])
    allowed_flags = set(protocol.get("severe_flags", []))

    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("each rating must be an object")
        label = str(row.get("condition_label", "")).strip()
        rater = str(row.get("rater_id", "")).strip()
        if not label or not rater:
            raise ValueError("each rating requires condition_label and rater_id")
        scores = row.get("scores")
        if not isinstance(scores, dict):
            raise ValueError(f"rating {label} requires scores")
        normalized_scores = {
            dimension: _validate_score(scores.get(dimension), label=label, dimension=dimension)
            for dimension in DIMENSIONS
        }
        acceptable = row.get("acceptable_as_continuing_character")
        if not isinstance(acceptable, bool):
            raise ValueError(f"rating {label} requires boolean acceptable_as_continuing_character")
        flags = [str(item) for item in row.get("severe_flags", [])]
        unknown = set(flags) - allowed_flags
        if unknown:
            raise ValueError(f"rating {label} contains unknown severe flags: {sorted(unknown)}")
        grouped.setdefault(label, []).append(
            {
                "rater_id": rater,
                "scores": normalized_scores,
                "acceptable": acceptable,
                "severe_flags": flags,
            }
        )

    unblind = blind_key.get("mapping", {}) if isinstance(blind_key, dict) else {}
    summaries: dict[str, Any] = {}
    for label, label_rows in sorted(grouped.items()):
        unique_raters = sorted({row["rater_id"] for row in label_rows})
        means = {
            dimension: mean(row["scores"][dimension] for row in label_rows)
            for dimension in DIMENSIONS
        }
        medians = {
            dimension: median(row["scores"][dimension] for row in label_rows)
            for dimension in DIMENSIONS
        }
        acceptable_rate = mean(1.0 if row["acceptable"] else 0.0 for row in label_rows)
        flag_counts = Counter(flag for row in label_rows for flag in row["severe_flags"])
        severe_flag_rates = {
            flag: flag_counts.get(flag, 0) / len(label_rows)
            for flag in sorted(allowed_flags)
        }
        dimension_gate = all(means[dimension] >= float(minimums[dimension]) for dimension in DIMENSIONS)
        severe_gate = all(rate <= severe_maximum for rate in severe_flag_rates.values())
        provisional_adequate = dimension_gate and acceptable_rate >= acceptable_minimum and severe_gate
        claim_eligible = len(unique_raters) >= raters_required

        summaries[label] = {
            "condition_id": unblind.get(label),
            "rating_count": len(label_rows),
            "independent_rater_count": len(unique_raters),
            "mean_scores": means,
            "median_scores": medians,
            "acceptable_rate": acceptable_rate,
            "severe_flag_rates": severe_flag_rates,
            "absolute_quality": {
                "provisional_adequate": provisional_adequate,
                "nonprovisional_claim_eligible": claim_eligible,
                "adequate_for_claim": provisional_adequate if claim_eligible else None,
            },
        }

    adequate_labels = [
        label
        for label, summary in summaries.items()
        if summary["absolute_quality"]["adequate_for_claim"] is True
    ]
    return {
        "schema": "duckhunter-rating-summary-v1",
        "blinded": blind_key is None,
        "dimensions": list(DIMENSIONS),
        "conditions": summaries,
        "adequate_condition_labels": adequate_labels,
        "interpretation": {
            "winner_declared": False,
            "reason": "This utility reports absolute adequacy and dimension-level outcomes. Comparative interpretation must preserve tradeoffs rather than collapse them into a single winner score.",
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Aggregate blinded Duckhunter campaign ratings")
    parser.add_argument("--ratings", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, default=Path("evaluation/rating_protocol_v1.json"))
    parser.add_argument("--blind-key", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = summarize_ratings(
        _load(args.ratings),
        _load(args.protocol),
        blind_key=_load(args.blind_key) if args.blind_key else None,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
