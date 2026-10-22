import pytest
from tag8.rules import SchoolYearTooLow, validate_elective_year


@pytest.mark.parametrize("year", [3, 7])
def test_elective_accepts_allowed_year(year):
    validate_elective_year(year, "Alte Runen")


@pytest.mark.parametrize("year", [1, 2])
def test_elective_rejected_for_low_school_year(year):
    with pytest.raises(SchoolYearTooLow, match="ab Schuljahr 3"):
        validate_elective_year(year, "Alte Runen")

def test_other_offer_has_no_elective():
    validate_elective_year(3, "Flugkunde")