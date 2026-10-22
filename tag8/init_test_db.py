import os

from alembic import command
from alembic.config import Config

from tag8.testing_db import PROJECT_DIR, make_test_url


if __name__ == "__main__":
    url = make_test_url()
    # env.py baut die Engine beim Import aus diesen MYSQL-Variablen. Sie müssen deshalb
    # gesetzt sein, bevor Alembic läuft. Alembic läuft im selben Prozess, damit kein
    # Kindprozess ohne Windows-Systemvariablen startet.
    values = {
        "MYSQL_HOST": url.host or "",
        "MYSQL_PORT": str(url.port),
        "MYSQL_USER": url.username or "",
        "MYSQL_PASSWORD": url.password or "",
        "MYSQL_DATABASE": url.database or "",
    }
    os.environ.update(values)

    cfg = Config(str(PROJECT_DIR / "alembic.ini"))
    # Entspricht: python -m alembic upgrade head
    command.upgrade(cfg, "head")
    # command.downgrade(cfg, "base")
    print("Testdatenbank ist auf dem aktuellen Migrationsstand.")
