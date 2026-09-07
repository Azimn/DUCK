from duck.planning_simulation import run_planning_simulation


def test_long_horizon_v09_planning_simulation_passes_all_gates():
    report = run_planning_simulation()
    assert report["passed"], report
    assert all(report["gates"].values()), report["gates"]
    assert report["final"]["subject_id"] == "planning-21d"
    assert not report["final"]["active_plans"]
