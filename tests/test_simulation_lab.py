from duck.simulation_lab import run_all


def test_simulation_lab_passes():
    report = run_all()
    failures = [row for row in report["results"] if not row.get("passed")]
    assert report["passed"], failures
