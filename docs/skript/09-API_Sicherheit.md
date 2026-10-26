# API-Sicherheit – Teilnehmerskript

Tag 9 des Kurses „Programmierung mit Python für komplexe Datenbanken“.

Babbling darf Kurse lesen. Vector darf Kurse ändern und Gruppen buchen.
Die API prüft dafür bei jeder geschützten Anfrage Identität und Rechte.
Schüler, Kurse und Buchungen bleiben in der vorhandenen MySQL-Datenbank.

## Das brauchst du heute

| Frage | Werkzeug |
| --- | --- |
| Wer stellt die Anfrage? | Authentifizierung mit Bearer-Token |
| Darf das Konto diese Aktion ausführen? | Autorisierung mit Rollen |
| Wie speichern wir Passwörter? | Argon2id-Hash und Salt |
| Wie bleibt die Anmeldung gespeichert? | Tabelle access_tokens |
| Wie schützen wir Routen? | Depends und Router-Dependencies |
| Wie widerrufen wir eine Anmeldung? | Tokenzeile löschen und committen |

- `reader`: Babbling liest den Kurskatalog.
- `staff`: Vector bearbeitet Kurse und verwaltet Buchungen.
- Benutzerkonten sind von Schülerdatensätzen getrennt.
- Heute prüfen wir Rollen. Einzelne Kurszuständigkeiten folgen später.
- Die Codeausschnitte erklären den gemeinsam aufgebauten Stand in `tag9`.
- Als Ausschnitt bezeichnete Blöcke ergänzen eine bestehende Datei.

> **⚠️ Pitfall: Angemeldet bedeutet uneingeschränkt berechtigt**
> Ein gültiges Token bestätigt eine Identität.
> Die Rolle entscheidet zusätzlich, ob die Aktion erlaubt ist.
> Auch erlaubte Aktionen müssen Eingaben und Fachregeln prüfen.

## 0. Umgebung und Rechte festlegen

Datei `requirements-tag9.txt`:

```text
-r requirements-tag7.txt
pwdlib[argon2]==0.3.1
```

Im Unterrichtsprojekt `hogwarts-sql`, bei laufendem Docker Desktop:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r .\requirements-tag9.txt
python -m pip check
docker compose up -d
python -m alembic current
```

- Ausgangspunkt ist Revision `0002`.
- Python erreicht MySQL über `127.0.0.1:3307` gemäß lokaler `.env`.
- Neue Dateien liegen in `tag9`; Tests liegen in `tests/tag9`.
- Für die vollständige API den bisherigen Server mit Strg+C beenden.

| Anfrage | Ohne Token | reader | staff |
| --- | --- | --- | --- |
| GET /health | 200 | 200 | 200 |
| POST /auth/login | Zugangsdaten prüfen | ebenso | ebenso |
| GET /auth/me | 401 | 200 | 200 |
| POST /auth/logout | 401 | 204 | 204 |
| GET /courses | 401 | erlaubt | erlaubt |
| GET /courses/count | 401 | erlaubt | erlaubt |
| GET /courses/{id} | 401 | erlaubt | erlaubt |
| POST /courses | 401 | 403 | erlaubt |
| PUT, DELETE /courses/{id} | 401 | 403 | erlaubt |
| GET /bookings | 401 | 403 | erlaubt |
| POST /booking-batches | 401 | 403 | erlaubt |

- `401`: Ein gültiger Zugangsnachweis fehlt.
- `403`: Die Identität ist bekannt. Ihre Rechte reichen nicht.
- `422`: Eingaben verletzen die festgelegten Formatregeln.
- `404` und `409` behalten ihre fachliche Bedeutung.
- `/docs` und `/openapi.json` bleiben in diesem Stand öffentlich.

## 1. Passwörter hashen und prüfen

- Ein Hash ist keine reversible Verschlüsselung.
- Argon2id erschwert das Ausprobieren vieler Passwortkandidaten.
- Ein zufälliger Salt sorgt für unterschiedliche gespeicherte Hashes.
- Salt und Parameter stehen im gespeicherten Hashtext.
- `verify` prüft das Passwort gegen diesen vollständigen Text.

Datei `tag9/passwords.py`:

```python
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()
# Einmal vorbereiten: Auch unbekannte Konten lösen eine Hashprüfung aus.
DUMMY_HASH = password_hash.hash("unused-dummy-password")


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, stored_hash: str) -> bool:
    return password_hash.verify(password, stored_hash)
```

- Im festgelegten Paketstand verwendet `recommended()` Argon2id.
- Bei bekanntem Namen prüfen wir den gespeicherten Passwort-Hash.
- Bei unbekanntem Namen prüfen wir gegen `DUMMY_HASH`.
- Das vermindert grobe Zeitunterschiede bei falschen Anmeldungen.
- Es garantiert keine identischen Antwortzeiten.

> **⚠️ Pitfall: Zwei frisch erzeugte Hashes vergleichen**
> Derselbe Passworttext kann verschiedene Hashtexte ergeben.
> Verwende `verify_password`, um das Passwort zu prüfen.
> Der Dummy-Hash gehört zu keinem Konto und erlaubt keine Anmeldung.

Datei `tests/tag9/test_passwords.py`:

```python
from tag9.passwords import hash_password, verify_password


def test_password_hash_has_salt_and_checks_password():
    password = "Nur-fuer-den-lokalen-Test-123!"
    first = hash_password(password)
    second = hash_password(password)
    assert first != second  # Zufälliger Salt, gleicher Passworttext.
    assert first != password
    assert verify_password(password, first)
    assert not verify_password("falsch", first)
```

```powershell
python -m pytest .\tests\tag9\test_passwords.py -v
```

## 2. Konten und Token speichern

Die Modelle in `tag9/models.py` verwenden dieselbe `Base` wie bisher.

| Tabelle | Wichtige Felder | Zweck |
| --- | --- | --- |
| users | id, username, password_hash, role, is_active | Konto und Rechte |
| access_tokens | token_hash, user_id, expires_at | Gespeicherte Anmeldung |

- Der Benutzername ist eindeutig. Rollen sind `reader` oder `staff`.
- Ein Konto kann mehrere Token besitzen, etwa für mehrere Geräte.
- `expires_at` enthält UTC-Unixzeit in ganzen Sekunden.
- Der Client erhält das rohe Zufallstoken einmal beim Login.
- MySQL speichert nur dessen SHA-256-Fingerabdruck.
- SHA-256 verwenden wir hier für Zufallstoken, nicht für Passwörter.

In `alembic/env.py` wird das neue Modellmodul registriert:

```python
import tag9.models  # Registriert users und access_tokens an derselben Base.
```

Nur wenn Revision `0003` noch nicht vorhanden ist, neu erzeugen:

```powershell
python -m alembic history
python -m alembic revision --autogenerate --rev-id 0003 -m "auth"
```

- `alembic/versions/0003_auth.py` prüfen, bevor die Migration läuft.
- Sie soll genau `users` und `access_tokens` mit ihren Schlüsseln anlegen.
- Vorhandene Schüler-, Kurs- und Buchungstabellen bleiben bestehen.
- Der Rollen-Check muss `reader` und `staff` zulassen.
- Python-Defaults sind keine automatischen Datenbank-Defaults.

```powershell
python -m alembic upgrade head
python -m alembic check
python -m alembic current
```

- Erwartet: Revision `0003` und keine weitere erkannte Modelländerung.

> **⚠️ Pitfall: stamp statt Migration verwenden**
> `stamp` setzt nur den vermerkten Stand. Es erzeugt keine Tabellen.
> `upgrade` führt die Migration wirklich aus.
> Eine vorhandene Revision nicht ein zweites Mal erzeugen.

### Ein- und Ausgabe trennen

Datei `tag9/schemas.py`:

```python
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, SecretStr

Username = Annotated[str, Field(
    min_length=3, max_length=50, pattern=r"^[a-z][a-z0-9._-]*$"
)]
Password = Annotated[SecretStr, Field(min_length=4, max_length=128)]


class LoginInput(BaseModel):
    model_config = ConfigDict(extra="forbid")  # Kein role-Feld vom Client.
    username: Username
    password: Password


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    role: Literal["reader", "staff"]  # Kein Passwort-Hash in der Antwort.


class TokenRead(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int
```

- Vier Zeichen sind hier nur die Mindestlänge des Unterrichtsbeispiels.
- Das Passwort bleibt unverändert. Auch Leerzeichen am Rand zählen.
- Ungültiges Format ergibt `422`; falsche gültige Zugangsdaten ergeben `401`.

> **⚠️ Pitfall: SecretStr als Verschlüsselung verstehen**
> `SecretStr` verdeckt den Wert bei normaler Darstellung des Modells.
> `get_secret_value()` gibt ihn für die Passwortprüfung frei.
> Transport und Speicherung werden dadurch nicht verschlüsselt.

### Die beiden Konten anlegen

Das vorhandene Verwaltungsprogramm interaktiv zweimal starten:

```powershell
python -m tag9.create_user
```

| Benutzername | Rolle | Passwort |
| --- | --- | --- |
| babbling | reader | Eigenes lokales Übungspasswort |
| vector | staff | Eigenes lokales Übungspasswort |

- `input` liest Benutzername und Rolle; Enter übernimmt `reader`.
- `getpass` verdeckt die Eingabe. Es hasht selbst kein Passwort.
- `add_user` hasht, speichert und committet; bei Fehlern rollt es zurück.
- Ein vorhandener Name wird abgelehnt. Er wird nicht überschrieben.

## 3. Identität und Rechte als Dependencies prüfen

Der fachliche Weg für eine geschützte Schreibanfrage:

```text
Authorization: Bearer <Token>
    → HTTPBearer: Header lesen
    → get_token: Token-Zeichenfolge entnehmen
    → get_current_user: Token, Ablauf und Konto prüfen
    → require_staff: Rolle prüfen
    → Fachroute: Auftrag prüfen und ausführen
```

Datei `tag9/dependencies.py`:

```python
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

bearer = HTTPBearer(auto_error=False)  # Liest nur den Header.


def get_session() -> Iterator[Session]:
    with SessionLocal() as db:
        try:
            yield db  # Dieselbe Session für Authentifizierung und Fachroute.
        except Exception:
            db.rollback()  # Auch geflushte INSERTs zurücknehmen.
            raise
    # Schließt die Session; nach reinem Lesen ist kein Commit nötig.


DbSession = Annotated[Session, Depends(get_session)]
Credentials = Annotated[
    HTTPAuthorizationCredentials | None, Depends(bearer)
]


def token_digest(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def unauthorized() -> HTTPException:
    return HTTPException(
        401, "Anmeldung erforderlich oder ungültig.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_token(credentials: Credentials) -> str:
    if credentials is None:
        raise unauthorized()
    return credentials.credentials  # Reiner Tokenwert ohne Bearer-Präfix.


Token = Annotated[str, Depends(get_token)]


def get_current_user(token: Token, db: DbSession) -> UserRead:
    stored = db.get(AccessToken, token_digest(token))
    if stored is None or stored.expires_at <= int(time.time()):
        raise unauthorized()  # Genau an expires_at ist das Token ungültig.
    user = db.get(User, stored.user_id)
    if user is None or not user.is_active:
        raise unauthorized()
    return UserRead.model_validate(user)  # Aktuelle Rolle aus der Datenbank.


CurrentUser = Annotated[UserRead, Depends(get_current_user)]


def require_staff(user: CurrentUser) -> UserRead:
    if user.role != "staff":
        raise HTTPException(403, "Verwaltungsrecht erforderlich.")
    return user
```

- `Depends` beschreibt, wie FastAPI einen Parameterwert beschafft.
- `CurrentUser` ist ein Alias, kein bereits angemeldetes Konto.
- `user: CurrentUser` erhält das geprüfte Ergebnis von `get_current_user`.
- FastAPI verwendet Dependency-Ergebnisse im selben Request wieder.
- Der nächste Request prüft Token und Konto erneut.
- Normale Python-Funktionsaufrufe führen Dependencies nicht selbst aus.

> **⚠️ Pitfall: HTTPBearer prüft das Token automatisch**
> Die Klasse liest nur den Zugangsnachweis aus dem Header.
> Unsere Funktionen prüfen Existenz, Ablauf, Kontostatus und Rolle.
> Ein frei erfundener Tokenwert ist keine gültige Anmeldung.

### Anmeldung und Datenbanksession unterscheiden

| Begriff | Lebensdauer |
| --- | --- |
| Anmeldung in access_tokens | Bis Ablauf oder Widerruf; über viele Requests |
| SQLAlchemy-Session | Ein Request; danach schließen |
| Verbindung im Engine-Pool | Kann für spätere Requests wiederverwendet werden |

> **⚠️ Pitfall: Session schließen bedeutet abmelden**
> Das Schließen gibt die Datenbankverbindung frei.
> Die Anmeldung bleibt als Tokenzeile gespeichert.
> Logout muss diese Zeile löschen und die Löschung committen.

## 4. Login, Identität und Logout

Datei `tag9/routers/auth.py`:

```python
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
    stored_hash = user.password_hash if user else DUMMY_HASH
    valid = verify_password(data.password.get_secret_value(), stored_hash)
    if not valid or user is None or not user.is_active:
        raise unauthorized()  # Auch passender Dummy-Hash lässt niemanden ein.
    raw_token = secrets.token_urlsafe(32)
    db.add(AccessToken(
        token_hash=token_digest(raw_token), user_id=user.id,
        expires_at=int(time.time()) + TOKEN_SECONDS,
    ))
    db.commit()  # Erst speichern, dann den Zugangsnachweis ausgeben.
    response.headers["Cache-Control"] = "no-store"
    return {"access_token": raw_token, "expires_in": TOKEN_SECONDS}


@router.get("/me", response_model=UserRead)
def read_me(user: CurrentUser):
    return user  # Keine Rolle erforderlich; beide Rollen sehen sich selbst.


@router.post("/logout", status_code=204)
def logout(user: CurrentUser, token: Token, db: DbSession):
    db.execute(delete(AccessToken).where(
        AccessToken.token_hash == token_digest(token),
        AccessToken.user_id == user.id,
    ))
    db.commit()  # Widerruft genau die vorgelegte Anmeldung.
    return Response(status_code=204)
```

- Login erhält JSON mit `username` und `password`.
- Er liefert `access_token`, `token_type="bearer"` und `expires_in=1800`.
- Das Token ist ein zufälliger, undurchsichtiger Wert ohne Rolleninhalt.
- Folgende Requests senden es im `Authorization`-Header.
- Eine neue Anmeldung erzeugt ein weiteres Token; alte bleiben gültig.
- Logout löscht genau eine Tokenzeile. Die Antwort `204` hat keinen Body.

> **⚠️ Pitfall: Nur das Token auf dem Client löschen**
> Eine Kopie wäre bis zum Ablauf weiterhin nutzbar.
> Unser Logout löscht deshalb die Tokenzeile in der Datenbank.
> Danach ergibt derselbe Nachweis auch auf einem anderen Client `401`.

> **⚠️ Pitfall: Kontosperre mit dauerhaftem Widerruf verwechseln**
> `is_active=False` sperrt den Zugriff, löscht aber keine Tokenzeilen.
> Nicht abgelaufene Token können nach erneuter Aktivierung wieder gelten.
> Für einen dauerhaften Widerruf müssen die Tokenzeilen gelöscht werden.

## 5. Fachrouten schützen und Transaktionen beibehalten

Ausschnitt aus `tag9/routers/courses.py`:

```python
from fastapi import APIRouter, Depends
from tag9.dependencies import get_current_user, require_staff

router = APIRouter(
    prefix="/courses", tags=["Kurse"],
    dependencies=[Depends(get_current_user)],  # Alle Kursrouten: Anmeldung.
)
```

- Zusätzliche Schreibrechte werden am jeweiligen Endpunkt geprüft.
- Eine Decorator-Dependency genügt, wenn die Route keinen Benutzerwert braucht.

Ausschnitt aus derselben Datei; die vorhandenen Imports bleiben bestehen:

```python
@router.post("", response_model=CourseRead, status_code=201,
             dependencies=[Depends(require_staff)])
def create_course(data: CourseCreate, db: DbSession):
    course = Course(title=data.title)
    db.add(course)
    db.flush()  # Neue ID erhalten; noch kein dauerhafter Erfolg.
    result = CourseRead.model_validate(course)
    db.commit()
    return result
```

Ausschnitt aus `tag9/main.py`; App und Fehlerhandler bleiben bestehen:

```python
from fastapi import Depends
from tag9.dependencies import require_staff
from tag9.routers import auth, bookings, courses

app.include_router(auth.router)  # Login muss ohne Token erreichbar sein.
app.include_router(courses.router)
app.include_router(bookings.router, dependencies=[Depends(require_staff)])
```

- Die gesamte Buchungsverwaltung verlangt damit `staff`.
- Lesen benötigt keinen Commit. Schreiben committet erst nach allen Prüfungen.
- Gruppenbuchungen haben genau einen Commit hinter der Schleife.
- Bei einem Fehler rollt `get_session` den gesamten Auftrag zurück.
- Die Wahlfachregel bleibt gültig: Harry darf buchen, Luna noch nicht.

> **⚠️ Pitfall: Nach der Anmeldung erneut db.begin() starten**
> Der erste Auth-SELECT hat die gemeinsame Transaktion bereits begonnen.
> Die Fachroute setzt sie fort und committet am Ende.
> Ein zusätzliches `with db.begin()` kann deshalb einen Fehler auslösen.

## 6. Den HTTP-Ablauf prüfen

```powershell
python -m uvicorn tag9.main:app --reload --host 127.0.0.1 --port 8000
```

In Postman dieselben lokalen Zugangsdaten wie bei der Kontoanlage verwenden.

1. `GET /health` ohne Token: `200`.
2. `GET /courses` ohne Token: `401`, Header `WWW-Authenticate: Bearer`.
3. `POST /auth/login` als Babbling mit falschem Passwort: `401`.
4. Mit gültigen Daten anmelden und das zurückgegebene Token übernehmen.
5. `GET /auth/me` und `GET /courses` mit diesem Token: jeweils `200`.
6. `POST /courses` als Babbling: `403`, kein Kurs wird angelegt.
7. Als Vector anmelden; Probekurs anlegen, ändern und löschen.
8. Erwartet: `201`, `200`, `204`. Bestehende Kursdaten nicht verwenden.
9. `POST /auth/logout` mit dem Token: `204`.
10. Dasselbe Token erneut für `/auth/me` verwenden: `401`.

JSON-Body für den Login; `LOKALES_PASSWORT` durch die eigene Eingabe ersetzen:

```json
{
  "username": "babbling",
  "password": "LOKALES_PASSWORT"
}
```

Der Header eines folgenden Requests:

```text
Authorization: Bearer <zurückgegebenes access_token>
```

> **⚠️ Pitfall: Benutzername oder Passwort als Bearer-Token senden**
> Verwende den Wert aus `access_token` der erfolgreichen Login-Antwort.
> Token gehören in den Header, nicht in URL oder Query-Parameter.
> Bei Passwörtern mit Sonderzeichen auf gültiges JSON achten.

- Passwörter, Hashes und Token nicht in Git oder Logausgaben ablegen.
- HTTP auf `127.0.0.1` ist die lokale Unterrichtsumgebung.
- Für den produktiven Transport ist HTTPS erforderlich.

## 7. Sicherheit und bestehendes Verhalten testen

| Fixture | Aufgabe im Test |
| --- | --- |
| test_engine | Testdatenbank hogwarts_test und Revision 0003 prüfen |
| db_factory | Testzeilen bereinigen und neue Sessions erzeugen |
| api_client | get_session auf die Testdatenbank umleiten |
| accounts | Babbling als reader und Vector als staff speichern |
| login_as | Hilfsfunktion für echten Login und Authorization-Header liefern |
| seed | Harry, Luna und Alte Runen als feste Testdaten anlegen |

- `login_as("reader")` meldet Babbling an; `login_as("staff")` meldet Vector an.
- Die Fixture liefert eine Funktion. Erst deren Aufruf führt den Login aus.
- Für DB-Overrides zählt `get_session` aus `tag9.dependencies`.
- Anmeldung und Fachrouten laufen weiter mit echter Logik gegen MySQL.

Ausschnitt aus `tests/tag9/test_security.py`:

```python
from tag9.dependencies import token_digest
from tag9.models import AccessToken


def test_logout_deletes_presented_token(api_client, login_as, db_factory):
    headers = login_as("reader")
    token = headers["Authorization"].removeprefix("Bearer ")
    assert api_client.post("/auth/logout", headers=headers).status_code == 204
    assert api_client.get("/auth/me", headers=headers).status_code == 401
    with db_factory() as db:  # Unabhängig nachlesen, nicht nur HTTP prüfen.
        assert db.get(AccessToken, token_digest(token)) is None
```

- Rechteprüfungen müssen auch nachweisen, dass keine Daten geändert wurden.
- Bei Harry und Luna in einer Wahlfachgruppe wird die ganze Gruppe abgelehnt.
- Erwartet: `409` und keine teilweise gespeicherte Buchung.
- Suche, Eingabeprüfung und bereinigte Fehlerantworten müssen weiter gelten.

```powershell
$testCompose = @("--env-file", ".env.test", "-f", "compose.test.yaml")
docker compose @testCompose up -d --wait test_db
python -m tag8.init_test_db
python -m pytest .\tests\tag9 -q
```

> **⚠️ Pitfall: TestClient bedeutet automatisch Testdatenbank**
> Erst der Override der richtigen Session-Dependency leitet DB-Zugriffe um.
> Die Schutzprüfung auf `hogwarts_test` muss vor dem Bereinigen laufen.
> Normale Unterrichtsdaten dürfen durch Tests nicht gelöscht werden.

## Das solltest du erklären können

1. Warum beweisen zwei unterschiedliche Hashtexte kein falsches Passwort?
2. Warum führt ein passendes Dummy-Passwort nicht zu einer Anmeldung?
3. Wann antwortet die API mit `401`, wann mit `403`?
4. Warum beendet das Schließen einer DB-Session keine Anmeldung?
5. Warum steht der Commit einer Gruppenbuchung hinter der Schleife?

| Merksatz | Bedeutung |
| --- | --- |
| Hash prüfen statt Hashtexte vergleichen | Salt berücksichtigen |
| Token lesen ist noch keine Identitätsprüfung | DB und Ablauf prüfen |
| Identität und Rolle getrennt prüfen | Anmeldung ist kein Schreibrecht |
| Ein Request, eine gemeinsame DB-Session | Auth und Fachroute verbinden |
| Logout muss gespeichert werden | Tokenzeile löschen und committen |

