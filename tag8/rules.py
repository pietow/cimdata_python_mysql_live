class SchoolYearTooLow(ValueError):
    pass

ELECTIVE_COURSES = ["Arithmantik", "Wahrsagen", "Alte Runen", "Pflege magischer Geschöpfe",]

def validate_elective_year(school_year: int, course_title: str) -> None:
    if course_title in ELECTIVE_COURSES and school_year < 3:
        raise SchoolYearTooLow("Wahlfächer sind ab Schuljahr 3 buchbar.")


if __name__ == "__main__":
    validate_elective_year(2, "Wahrsagen")