from duck.agency_evaluation import (
    bounded_multi_concern_field,
    commitment_followup_becomes_endogenous,
    competing_concerns_choose_most_motivated,
    context_gates_action,
    interruption_preserves_unfinished_intention,
    low_energy_defers_then_resumes,
    no_opportunity_no_false_goal,
    opportunity_survives_restart,
    opportunity_without_prompt,
    run,
    safety_overrides_curiosity_then_releases,
    satisfied_and_abandoned_concerns_stop_competing,
)


def test_registered_opportunity_can_drive_later_endogenous_action():
    report = opportunity_without_prompt()
    assert report["passed"], report


def test_prospective_opportunity_survives_state_roundtrip():
    report = opportunity_survives_restart()
    assert report["passed"], report
    assert report["same_subject"]


def test_competing_concerns_choose_the_more_motivated_goal():
    report = competing_concerns_choose_most_motivated()
    assert report["passed"], report


def test_low_energy_can_defer_and_then_resume_a_goal():
    report = low_energy_defers_then_resumes()
    assert report["passed"], report


def test_safety_can_override_curiosity_without_erasing_it():
    report = safety_overrides_curiosity_then_releases()
    assert report["passed"], report


def test_context_can_make_a_goal_actionable_later():
    report = context_gates_action()
    assert report["passed"], report


def test_interruption_does_not_delete_unfinished_intention():
    report = interruption_preserves_unfinished_intention()
    assert report["passed"], report


def test_satisfied_and_impossible_goals_stop_competing():
    report = satisfied_and_abandoned_concerns_stop_competing()
    assert report["passed"], report


def test_commitment_followup_can_become_endogenous():
    report = commitment_followup_becomes_endogenous()
    assert report["passed"], report


def test_quiet_time_does_not_invent_opportunities():
    report = no_opportunity_no_false_goal()
    assert report["passed"], report


def test_multi_concern_field_remains_bounded():
    report = bounded_multi_concern_field()
    assert report["passed"], report


def test_full_v08_agency_suite_passes():
    report = run()
    assert report["passed"], report
