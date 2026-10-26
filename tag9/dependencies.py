import hashlib
import time
from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from tag7.db import SessionLocal
from tag9.models import AccessToken, User
from tag9.schemas import UserRead

bearer = HTTPBearer(auto_error=False)


def get_session() -> Iterator[Session]:
    with SessionLocal() as db:
        try: 
            yield db
        except Exception:
            db.rollback()
            raise
    

# Alias für Typ und Herkunft. Diese Zuweisung öffnet noch keine Session.
DbSession = Annotated[Session, Depends(get_session)]
Credentials = Annotated[
    HTTPAuthorizationCredentials | None, Depends(bearer)
]


def token_digest(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

def unauthorized() -> HTTPException:
    return HTTPException(
        401, "Anmeldung erforderlich oder ungültig",
        headers={"WWW-Authenticate": "Bearer"}
    )
    


def get_token(credentials: Credentials) -> str:
    if credentials is None:
        raise unauthorized()
    return credentials.credentials


Token = Annotated[str, Depends(get_token)]


def get_current_user(token: Token, db: DbSession) -> UserRead:
    stored = db.get(AccessToken, token_digest(token))
    if stored is None or stored.expires_at <= int(time.time()):
        raise unauthorized()
    user = db.get(User, stored.user_id)
    if user is None or not user.is_active:
        raise unauthorized()
    return UserRead.model_validate(user)



CurrentUser = Annotated[UserRead, Depends(get_current_user)]


def require_staff(user: CurrentUser) -> UserRead:
    if user.role != 'staff':
        raise HTTPException(403, "Keine Berechtigung")
    return user