import logging

from sqlalchemy.exc import OperationalError

from tag7.dependencies import get_session
from tag8.main import app


def test_database_failure_has_safe_response(client, monkeypatch, caplog):
    def unavailable_session():
        raise OperationalError("SELECT 1", {}, RuntimeError("secret-value"))

    # Nur diesen Fehler simulieren; echte DB-Tests bleiben an anderer Stelle.
    monkeypatch.setitem(app.dependency_overrides, get_session,
                        unavailable_session)
    caplog.set_level(logging.ERROR, logger="hogwarts.api")
    response = client.get("/courses")
    assert response.status_code == 503
    assert response.json() == {
        "detail": "Datenbank derzeit nicht erreichbar."
    }
    assert "secret-value" not in response.text
    assert "secret-value" not in caplog.text
    assert "database_unavailable method=GET path=/courses" in caplog.text
