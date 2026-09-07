from duck.regulation_evaluation import (
    quiet_time_regulation,
    repair_moves_without_erasing_history,
    residue_recovery,
)


def test_residue_recovers_without_perseveration():
    report = residue_recovery()
    assert report["passed"], report


def test_quiet_time_does_not_saturate_or_spam_one_action():
    report = quiet_time_regulation()
    assert report["passed"], report


def test_repair_moves_relationship_without_erasing_history():
    report = repair_moves_without_erasing_history()
    assert report["passed"], report
