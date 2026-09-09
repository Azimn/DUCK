"""Run the established Simulation Lab scenarios against the v0.6 organism.

The original ``duck.simulation_lab`` remains a v0.5 baseline snapshot. This module
reuses its scenario definitions while substituting the regulated v0.6 LivingDuck,
so the same tests can compare the candidate against the historical behavior.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import simulation_lab as baseline
from .living_v06 import LivingDuck
from .host_v06 import PersistentDuckHostV06


def run_all() -> dict:
    original = baseline.LivingDuck
    original_host = baseline.PersistentDuckHost
    baseline.LivingDuck = LivingDuck
    baseline.PersistentDuckHost = PersistentDuckHostV06
    try:
        report = baseline.run_all()
    finally:
        baseline.LivingDuck = original
        baseline.PersistentDuckHost = original_host
    return {
        "suite": "DUCK Simulation Lab v0.6 regulated candidate",
        "passed": report["passed"],
        "results": report["results"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run DUCK v0.6 regulated longitudinal simulations")
    parser.add_argument("--out-dir", type=Path, default=None)
    args = parser.parse_args(argv)
    report = run_all()
    rendered = json.dumps(report, indent=2, ensure_ascii=False, default=baseline._json_default)
    print(rendered)
    if args.out_dir is not None:
        args.out_dir.mkdir(parents=True, exist_ok=True)
        (args.out_dir / "simulation_report_v06.json").write_text(rendered + "\n", encoding="utf-8")
        (args.out_dir / "simulation_report_v06.md").write_text(baseline._markdown(report), encoding="utf-8")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
