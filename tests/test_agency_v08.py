from duck.agency_evaluation import (
    no_opportunity_no_false_goal,
    opportunity_survives_restart,
    opportunity_without_prompt,
)


def test_registered_opportunity_can_drive_later_endogenous_action():
    report = opportunity_without_prompt()
    assert report["passed"], report


def test_prospective_opportunity_survives_state_roundtrip():
    report = opportunity_survives_restart()
    assert report["passed"], report
    assert report["same_subject"]


def test_quiet_time_does_not_invent_opportunities():
    report = no_opportunity_no_false_goal()
    assert report["passed"], report
