from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from tag7.db import SessionLocal

def get_session()-> Iterator[Session]:
    with SessionLocal() as session:
        yield session 


DbSession = Annotated[Session, Depends(get_session)]