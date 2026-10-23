from sqlalchemy import func, select

from tag7.models import Booking


def test_batch_is_committed(api_client, seed, db_factory):
    student_ids = [seed["harry_id"], seed["hermione_id"]]
    response = api_client.post("/booking-batches", json={
        "course_id": seed["course_id"],
        "student_ids": student_ids,
        "booking_date": "1993-09-06",
    })
    assert response.status_code == 201
    rows = response.json()
    assert [row["student_id"] for row in rows] == student_ids
    assert len({row["id"] for row in rows}) == 2
    assert all(row["booking_date"] == "1993-09-06" for row in rows)
    with db_factory() as db:
        statement = select(Booking).order_by(Booking.id)
        stored = list(db.scalars(statement))
        assert [row.id for row in stored] == [row["id"] for row in rows]
        assert [row.student_id for row in stored] == student_ids
        assert all(row.course_id == seed["course_id"] for row in stored)


def test_batch_rolls_back_on_school_year(api_client, seed, db_factory):
    # Harrys INSERT läuft zuerst. Lunas fachlicher Fehler kommt danach.
    response = api_client.post("/booking-batches", json={
        "course_id": seed["course_id"],
        "student_ids": [seed["harry_id"], seed["luna_id"]],
        "booking_date": "1993-09-06",
    })
    assert response.status_code == 409 # TODOD: WIRD NOCH ANGEPASST
    assert response.json() == {
        "detail": "Wahlfächer sind ab Schuljahr 3 buchbar."
    }
    with db_factory() as db:
        count = db.scalar(select(func.count()).select_from(Booking))
    assert count == 0
