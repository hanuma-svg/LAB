import pytest

from daycare_fees import enrolment_allowed, extra_hours_fee, pickup_status


def test_extra_hours_fee_rejects_unknown_age_group():
    with pytest.raises(ValueError, match="unknown age group"):
        extra_hours_fee("school_age", 10, False)


def test_extra_hours_fee_rejects_negative_hours():
    with pytest.raises(ValueError, match="invalid hours"):
        extra_hours_fee("infant", -1, False)


def test_extra_hours_fee_returns_zero_at_included_limit():
    assert extra_hours_fee("toddler", 25, False) == 0


def test_extra_hours_fee_applies_sibling_hours_for_non_infant():
    assert extra_hours_fee("toddler", 30, True) == 0


def test_extra_hours_fee_uses_infant_rate_for_small_overage():
    assert extra_hours_fee("infant", 21, False) == 14


def test_extra_hours_fee_uses_standard_rate_for_non_infant_overage():
    assert extra_hours_fee("preschool", 31, False) == 9


def test_extra_hours_fee_applies_high_rate_to_non_infant_large_overage():
    assert extra_hours_fee("toddler", 46, False) == 294


def test_extra_hours_fee_applies_infant_large_overage_surcharge():
    assert extra_hours_fee("infant", 41, False) == 462


def test_enrolment_allowed_when_pending_immunisation_and_old_enough():
    assert enrolment_allowed(12, 0, True) is True


def test_enrolment_rejected_when_pending_immunisation_and_too_young():
    assert enrolment_allowed(11, 10, True) is False


def test_enrolment_rejected_for_under_six_months_without_pending_immunisation():
    assert enrolment_allowed(5, 2, False) is False


def test_enrolment_allowed_with_vacancy():
    assert enrolment_allowed(6, 1, False) is True


def test_enrolment_rejected_without_vacancy():
    assert enrolment_allowed(6, 0, False) is False


@pytest.mark.parametrize(
    ("minutes_left", "is_aftercare", "is_friday", "expected"),
    [
        (10, False, False, "on_time"),
        (0, False, False, "late"),
        (-6, False, False, "overdue"),
        (20, True, False, "on_time"),
        (15, True, True, "late"),
        (14, True, True, "overdue"),
        (30, True, True, "on_time"),
    ],
)
def test_pickup_status_covers_cutoffs_and_statuses(
    minutes_left, is_aftercare, is_friday, expected
):
    assert pickup_status(minutes_left, is_aftercare, is_friday) == expected
