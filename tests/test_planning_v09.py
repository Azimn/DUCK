from duck.planning_evaluation import (
    counterfactual_route_changes_with_risk,
    experience_forms_goal_without_instruction,
    failed_route_causes_counterfactual_replanning,
    hierarchical_plan_advances_through_subgoals,
    ordinary_experience_does_not_invent_goal,
    plan_survives_state_roundtrip,
    planning_metadata_stays_out_of_subjective_access,
    run,
)


def test_experience_can_form_a_goal_without_explicit_registration():
    report = experience_forms_goal_without_instruction()
    assert report["passed"], report


def test_counterfactual_route_choice_changes_with_risk_state():
    report = counterfactual_route_changes_with_risk()
    assert report["passed"], report


def test_hierarchical_plan_advances_across_successful_subgoals():
    report = hierarchical_plan_advances_through_subgoals()
    assert report["passed"], report


def test_failed_route_causes_counterfactual_replanning():
    report = failed_route_causes_counterfactual_replanning()
    assert report["passed"], report


def test_plan_survives_subject_state_roundtrip():
    report = plan_survives_state_roundtrip()
    assert report["passed"], report
    assert report["same_subject"]


def test_ordinary_experience_does_not_manufacture_goal():
    report = ordinary_experience_does_not_invent_goal()
    assert report["passed"], report


def test_private_planning_metadata_stays_out_of_subjective_access():
    report = planning_metadata_stays_out_of_subjective_access()
    assert report["passed"], report


def test_full_v09_planning_suite_passes():
    report = run()
    assert report["passed"], report
