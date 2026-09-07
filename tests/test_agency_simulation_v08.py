from duck.agency_simulation import run_agency_simulation


def test_long_horizon_v08_agency_simulation_passes_all_gates():
    report = run_agency_simulation()
    assert report["passed"], report
    assert all(report["gates"].values()), report["gates"]
    assert report["final"]["subject_id"] == "agency-14d"
    assert not report["final"]["open_concerns"]
