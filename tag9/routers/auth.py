import secrets
import time

from fastapi import APIRouter, Response
from sqlalchemy import delete, select

from tag9.dependencies import CurrentUser, DbSession, Token
from tag9.dependencies import token_digest, unauthorized
from tag9.models import AccessToken, User
from tag9.passwords import DUMMY_HASH, verify_password
from tag9.schemas import LoginInput, TokenRead, UserRead

router = APIRouter(prefix="/auth", tags=["Anmeldung"])
TOKEN_SECONDS = 30 * 60


@router.post("/login", response_model=TokenRead)
def login(data: LoginInput, db: DbSession, response: Response):
    user = db.scalar(select(User).where(User.username == data.username))
    stored_hash = user.password_hash if user else DUMMY_HASH # dummy hash führt leer passworthashing aus, sodass benutzernamen nicht erraten werden können
    valid = verify_password(data.password.get_secret_value(), stored_hash)
    if not valid or user is None or not user.is_active:
        raise unauthorized()
    raw_token = secrets.token_urlsafe(32) # zufälliger Token wird erstellt

    db.add(AccessToken(
        token_hash=token_digest(raw_token), user_id=user.id,
        expires_at=int(time.time()) + TOKEN_SECONDS,
    ))
    db.commit()
    response.headers["Cache-Control"] = "no-store"
    return {"access_token": raw_token, "expires_in": TOKEN_SECONDS}


@router.get("/me", response_model=UserRead)
def read_me(user: CurrentUser):
    return user

@router.post("/logout", status_code=204)
def logout(user: CurrentUser, token: Token, db: DbSession):
    db.execute(delete(AccessToken).where(
        AccessToken.token_hash == token_digest(token),
        AccessToken.user_id == user.id))
    db.commit()
    return Response(status_code=204)