from getpass import getpass

from pydantic import SecretStr, ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from tag7.db import SessionLocal
from tag9.models import User
from tag9.passwords import hash_password
from tag9.schemas import LoginInput, UserRead


def add_user(db: Session, data: LoginInput, role: str) -> UserRead:
    if role not in {"reader", "staff"}:
        raise ValueError("unbekannte Rolle")
    try:
        user = User(
            username=data.username,
            password_hash = hash_password(data.password.get_secret_value()),
            role=role
        )
        db.add(user)
        db.flush()
        result = UserRead.model_validate(user)
        db.commit()
    except Exception:
        db.rollback()
        raise
    return result


def main():
    username = input("Benutzername: ").strip()
    role = input("Rolle (reader/staff): ").strip() or "reader"
    password = getpass("Lokales Passwort (4 bis 128 Zeichen)")

    try:
        data = LoginInput(username=username, password=SecretStr(password))
    except ValidationError:
        raise SystemExit("Name oder Passwort erfüllt die Regel nicht") 

    try:
        with SessionLocal() as db:
            user = add_user(db, data, role)
    except IntegrityError:
        raise SystemExit("Konto konnte nicht angelegt werden.")
    print(f"Konto {user.username} mit Rolle {user.role} angelegt")


if __name__ == "__main__":
    main()