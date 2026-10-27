import logging


def test_successful_batch_is_logged(api_client, seed, caplog):
    caplog.set_level(logging.INFO, logger="hogwarts.bookings")
    response = api_client.post("/booking-batches", json={
        "course_id": seed["course_id"],
        "student_ids": [seed["harry_id"]],
        "booking_date": "1993-09-06",
    })
    assert response.status_code == 201
    expected = f"booking_batch_saved course_id={seed['course_id']} count=1"
    records = [r for r in caplog.records if r.name == "hogwarts.bookings"]
    assert [r.getMessage() for r in records] == [expected]
    assert records[0].levelno == logging.INFO