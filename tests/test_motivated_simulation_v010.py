from duck.motivated_simulation_v010 import run_motivated_life


def test_longitudinal_v010_motivated_life_passes_all_gates():
    report = run_motivated_life()
    assert report["passed"], report
