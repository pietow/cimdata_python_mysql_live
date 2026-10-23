from pathlib import Path

from dotenv import dotenv_values
from sqlalchemy import URL

PROJECT_DIR = Path(__file__).resolve().parent.parent


def make_test_url() -> URL:
    # .env.test lesen, ohne die Umgebung der normalen API zu überschreiben.
    settings = dotenv_values(PROJECT_DIR / ".env.test")
    password = settings.get("TEST_MYSQL_PASSWORD")
    if not password:
        raise RuntimeError("TEST_MYSQL_PASSWORD fehlt in .env.test.")
    port = settings.get("TEST_MYSQL_PORT") or "3308"
    return URL.create(
        "mysql+mysqlconnector",
        username="tester",
        password=password,
        host="127.0.0.1",
        port=int(port),
        database="hogwarts_test",
        query={"charset": "utf8mb4"},
    )
