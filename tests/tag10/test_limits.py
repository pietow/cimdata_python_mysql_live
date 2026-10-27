def test_next_course_page_has_later_ids(api_client, login_as, seed):
    headers = login_as("babbling")
    first = api_client.get("/courses?limit=1", headers=headers)
    assert first.status_code == 200
    assert len(first.json()) == 1
    after = first.json()[0]["id"]
    second = api_client.get(
        f"/courses?limit=1&after_id={after}", headers=headers,
    )
    assert second.status_code == 200
    assert len(second.json()) == 1
    assert second.json()[0]["id"] > after


def test_limit_above_fifty_is_rejected(api_client, login_as):
    response = api_client.get("/courses?limit=51", headers=login_as("babbling"))
    assert response.status_code == 422
    print(response.json())
    assert response.json()["detail"][0]["loc"][1] == "limit"
