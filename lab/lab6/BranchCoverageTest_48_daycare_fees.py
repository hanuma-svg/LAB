import pytest

from daycare_fees import enrolment_allowed, extra_hours_fee, pickup_status


@pytest.mark.parametrize(
    ("age_group", "hours", "has_sibling", "expected"),
    [
        ("infant", 20, False, 0),
        ("infant", 21, False, 14),
        ("toddler", 25, True, 0),
        ("toddler", 31, True, 9),
        ("toddler", 45, False, 180),
        ("toddler", 46, False, 294),
        ("infant", 40, False, 280),
        ("infant", 41, False, 462),
    ],
)
def test_extra_hours_fee_boundary_paths(age_group, hours, has_sibling, expected):
    assert extra_hours_fee(age_group, hours, has_sibling) == expected


@pytest.mark.parametrize(
    ("age_group", "hours", "message"),
    [
        ("unknown", 0, "unknown age group"),
        ("preschool", -1, "invalid hours"),
    ],
)
def test_extra_hours_fee_validation_paths(age_group, hours, message):
    with pytest.raises(ValueError, match=message):
        extra_hours_fee(age_group, hours, False)


@pytest.mark.parametrize(
    ("age_months", "vacancies", "pending", "expected"),
    [
        (11, 5, True, False),
        (12, 0, True, True),
        (5, 5, False, False),
        (6, 0, False, False),
        (6, 1, False, True),
    ],
)
def test_enrolment_decision_boundaries(
    age_months, vacancies, pending, expected
):
    assert enrolment_allowed(age_months, vacancies, pending) is expected


@pytest.mark.parametrize(
    ("minutes_left", "aftercare", "friday", "expected"),
    [
        (10, False, False, "on_time"),
        (9, False, False, "late"),
        (-6, False, False, "overdue"),
        (30, True, True, "on_time"),
        (29, True, True, "late"),
        (14, True, True, "overdue"),
    ],
)
def test_pickup_status_threshold_boundaries(
    minutes_left, aftercare, friday, expected
):
    assert pickup_status(minutes_left, aftercare, friday) == expected
