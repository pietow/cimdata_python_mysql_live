from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from tag7.db import SessionLocal


def get_session() -> Iterator[Session]:
    # Eine neue Session pro Request, keine globale gemeinsame Session.
    with SessionLocal() as session:
        print('Session offen: ', session)
        yield session
    print('Session geschlossen: ', session)
    # Der Kontext schließt auch bei einem Fehler. Er committet nicht.


DbSession = Annotated[Session, Depends(get_session)]
