from duck.life_simulation import run_thirty_day_life


def test_thirty_day_life_simulation_passes_all_gates():
    report = run_thirty_day_life()
    assert report["passed"], report
    assert all(report["gates"].values()), report["gates"]


def test_v07_social_actions_are_not_question_dominated():
    report = run_thirty_day_life()
    timeline_actions = [row["action"] for row in report["timeline"]]
    assert timeline_actions.count("respond") > timeline_actions.count("ask")
    assert any(row["action"] == "repair" for row in report["timeline"])


def test_v07_safety_recovers_and_competence_does_not_saturate():
    report = run_thirty_day_life()
    needs = report["final_state"]["needs"]
    assert 0.60 < needs["safety"] < 0.90
    assert 0.60 < needs["competence"] < 0.99


def test_v07_reinterprets_repaired_relationship_without_erasing_failure():
    report = run_thirty_day_life()
    final_morgan = next(row for row in report["timeline"] if row["label"] == "final_morgan")
    subjective = " ".join(final_morgan["subjective"])
    assert "They let me down before, but they've followed through since." in subjective
    assert any("missed meeting" in row.lower() or "never" in row.lower() for row in final_morgan["subjective"] + [m for m in final_morgan.get("subjective", [])]) or report["gates"]["broken_promise_remembered_on_return"]
