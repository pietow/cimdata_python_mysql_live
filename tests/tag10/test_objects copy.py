from sqlalchemy import func, select

from tag7.models import Booking, Course
from tag10.models import CourseManager


def test_responsible_staff_changes_course(api_client, login_as, seed,
                                          db_factory):
    response = api_client.put(f"/courses/{seed['own_id']}",
        headers=login_as("vector"), json={"title": "Arithmantik am Nachmittag"})
    assert response.status_code == 200
    with db_factory() as db:
        course = db.get(Course, seed["own_id"])
        assert course.title == "Arithmantik am Nachmittag"


def test_other_staff_cannot_change_course(api_client, login_as, seed,
                                         db_factory):
    # Beide Konten sind staff. Nur die Zuständigkeit unterscheidet sie.
    response = api_client.put(
        f"/courses/{seed['own_id']}",
        headers=login_as("hagrid"),
        json={"title": "Fremde Änderung"},
    )

    assert response.status_code == 403
    with db_factory() as db:
        assert db.get(Course, seed["own_id"]).title == "Arithmantik"


def test_creator_is_assigned_by_server(api_client, login_as, accounts,
                                      db_factory):
    response = api_client.post("/courses", headers=login_as("vector"),
                               json={"title": "Muggelkunde"})
    assert response.status_code == 201
    with db_factory() as db:
        assignment = db.get(CourseManager, response.json()["id"])
        assert assignment.user_id == accounts["vector"].id


def test_foreign_batch_is_denied_before_writing(api_client, login_as,
                                               seed, db_factory):
    response = api_client.post("/booking-batches",
        headers=login_as("hagrid"), json={
            "course_id": seed["own_id"], "student_ids": [seed["harry_id"]],
            "booking_date": "1993-09-06",
        })
    assert response.status_code == 403
    with db_factory() as db:
        assert db.scalar(select(func.count()).select_from(Booking)) == 0


def test_own_batch_still_rolls_back(api_client, login_as, seed, db_factory):
    response = api_client.post("/booking-batches",
        headers=login_as("vector"), json={
            "course_id": seed["own_id"],
            "student_ids": [seed["harry_id"], seed["luna_id"]],
            "booking_date": "1993-09-06",
        })
    assert response.status_code == 409
    with db_factory() as db:
        assert db.scalar(select(func.count()).select_from(Booking)) == 0
