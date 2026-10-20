from alembic import context

from tag7.db import engine
from tag7.models import Base

# Alle drei ORM-Klassen wurden durch den Modulimport registriert.
target_metadata = Base.metadata


def run_migrations_offline(): # keine Verbindung
    context.configure(
        url=engine.url,
        target_metadata=target_metadata,
        literal_binds=True, 
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    # Zugangsdaten kommen aus derselben .env wie beim API-Zugriff.
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
