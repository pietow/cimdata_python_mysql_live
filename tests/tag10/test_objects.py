from tag7.models import Course


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
