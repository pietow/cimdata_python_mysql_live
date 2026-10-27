from fastapi.testclient import TestClient

from tag10.main import create_app


def test_wrong_host_is_rejected():
    with TestClient(create_app(), base_url="http://localhost") as client:
        response = client.get("/health", headers={"Host": "fremd.example"})
    assert response.status_code == 400
