# Sicherheitsmechanismen – Teilnehmerskript

Tag 10 des Kurses „Programmierung mit Python für komplexe Datenbanken“.

Vector verwaltet Arithmantik, Hagrid Pflege magischer Geschöpfe. Beide sind
`staff` – trotzdem darf keiner den Kurs des anderen ändern. Außerdem begrenzen
wir, wie viele Treffer eine Antwort enthalten darf.

## Das brauchst du heute

| Schritt | Leitfrage | Nachweis |
| --- | --- | --- |
| Rolle: API5, bekannt aus Tag 9 | Darf reader einen Kurs ändern? | Nein: 403 |
| Objekt: API1, neu | Darf Hagrid Vectors Kurs ändern? | Nein: 403 |
| Menge: API4, neu | Darf Vector 51 Treffer pro Seite anfordern? | Nein: 422 |
| Konfiguration: API8, neu | Verrät die App interne Details? | Nein: bereinigte Fehler |

| Aktion | reader | staff, zuständig | staff, fremder Kurs |
| --- | --- | --- | --- |
| Katalog lesen | ja | ja | ja |
| Kurs anlegen | nein | ja, wird zugeordnet | ja, wird zugeordnet |
| Kurs ändern/löschen | nein | ja | nein |
| Gruppe buchen | nein | ja, Fachregeln gelten | nein |
| Buchungen lesen | nein | eigene Kurse | keine fremden Zeilen |

- Pro Kurs höchstens ein zuständiges Konto. Neue Kurse gehören dem Ersteller.
- Konten und Schüler bleiben getrennt. Es gibt keine neue Rolle.
- Neue Dateien liegen in `tag10`, Tests in `tests/tag10`.

> **⚠️ Pitfall: Ein Limit schützt fremde Daten**
> Erst die Zuständigkeit prüfen, dann die Menge begrenzen.
> Ein Limit verkleinert nur die Antwort – fremde Zeilen bleiben fremd.

## 0. Umgebung vorbereiten

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r .\requirements-tag9.txt
New-Item -ItemType Directory -Force -Path .\tag10\routers
New-Item -ItemType Directory -Force -Path .\tests\tag10
New-Item -ItemType Directory -Force -Path .\sql\tag10
docker compose up -d
python -m alembic current
```

- Ausgangspunkt: Revision `0003`. Keine neuen Python-Pakete nötig.
- Den Server aus Tag 9 mit Strg+C beenden.

## 1. Zuständigkeiten speichern

- Je Kurs höchstens ein Konto; ein Konto darf mehrere Kurse verwalten.
- Keine Zeile in `course_managers` bedeutet: noch nicht zugeordnet.

Datei `tag10/models.py`:

```python
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from tag7.models import Base
from tag9.models import User  # Registriert users an derselben Base.


class CourseManager(Base):
    __tablename__ = "course_managers"

    # Primärschlüssel: Ein Kurs kann nur einmal zugeordnet werden.
    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id"), primary_key=True
    )
    # Nicht unique: Dasselbe Konto darf für mehrere Kurse zuständig sein.
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
```

In `alembic/env.py` bei den Modellimporten ergänzen:

```python
import tag10.models  # Neue Tabelle beim Schemaabgleich berücksichtigen.
```

```powershell
python -m alembic revision --autogenerate --rev-id 0004 -m "course_managers"
python -m alembic upgrade head
python -m alembic check
```

| Befehl | Wirkung |
| --- | --- |
| `revision --autogenerate` | Änderungsvorschlag als neue Datei erzeugen |
| `upgrade head` | Fehlende Migrationen auf die Datenbank anwenden |
| `current` | Eingetragene Revision anzeigen |
| `check` | Würde Autogenerate noch Änderungen vorschlagen? |
| `history` | Revisionskette anzeigen |

- Erzeugte Datei unter `alembic/versions` prüfen: nur `course_managers` mit
  zwei Fremdschlüsseln, keine gelöschten Tabellen.

> **⚠️ Pitfall: Revision 0004 doppelt erzeugen**
> Existiert die Datei bereits, die Erzeugung überspringen und nur `upgrade` ausführen.
> `downgrade` würde die Zuordnungstabelle samt Daten löschen.

Hagrids Konto anlegen (Vector und Babbling existieren schon):

```powershell
python -m tag9.create_user
```

| Benutzername | Rolle | Vorgehen |
| --- | --- | --- |
| `hagrid` | `staff` | Jetzt anlegen, eigenes lokales Übungspasswort |
| `vector` | `staff` | Existiert aus Tag 9 |
| `babbling` | `reader` | Existiert aus Tag 9 |

### Bestehende Kurse zuordnen

Datei `tag10/assign_course.py` – lokales Verwaltungsprogramm, keine API-Route:

```python
from sqlalchemy import select

from tag7.db import SessionLocal
from tag7.models import Course
from tag9.models import User
from tag10.models import CourseManager


def main():
    course_id = int(input("Kurs-ID: "))
    username = input("Zuständiges staff-Konto: ").strip()
    # Lokales Verwaltungsprogramm: eigene Session und eigene Transaktion.
    # Normaler Blockabschluss: Commit. Fehler: Rollback.
    with SessionLocal.begin() as db:
        course = db.get(Course, course_id)
        user = db.scalar(select(User).where(User.username == username))
        if course is None:
            raise SystemExit("Kurs nicht gefunden.")
        if user is None or not user.is_active or user.role != "staff":
            raise SystemExit("Aktives staff-Konto erforderlich.")
        assignment = db.get(CourseManager, course_id)
        if assignment is None:
            db.add(CourseManager(course_id=course_id, user_id=user.id))
        else:
            assignment.user_id = user.id
    print("Zuständigkeit gespeichert.")


if __name__ == "__main__":
    main()
```

Kurs-IDs und Zuordnungen nachsehen – Datei `sql/tag10/01_assignments.sql`:

```sql
USE hogwarts;
SELECT id, title FROM courses ORDER BY id;
SELECT id, username, role FROM users ORDER BY id;
SELECT c.id, c.title, u.username
FROM courses AS c
LEFT JOIN course_managers AS cm ON cm.course_id = c.id
LEFT JOIN users AS u ON u.id = cm.user_id
ORDER BY c.id;
```

```powershell
docker compose exec db mysql -u dumbledore -p hogwarts
```

```sql
SOURCE /work/sql/tag10/01_assignments.sql;
```

| Kurs | Benutzername eingeben | Befehl |
| --- | --- | --- |
| Arithmantik | `vector` | `python -m tag10.assign_course` |
| Pflege magischer Geschöpfe | `hagrid` | `python -m tag10.assign_course` |

- Erwartet: Nicht zugeordnete Kurse zeigen `username = NULL`.

> **⚠️ Pitfall: Alle Kurse pauschal Vector zuordnen**
> Dann sieht man keinen Unterschied zwischen eigenem und fremdem Kurs.
> Eine Zuordnung allein gibt außerdem keine Schreibrechte: Die Rolle zählt weiter.

## 2. Änderungen am konkreten Kurs erlauben

- Erst Rolle und Kurszuständigkeit prüfen, dann Daten ändern.
- Fehlender Kurs: `404`. Fremder oder nicht zugeordneter Kurs: `403`.

Datei `tag10/permissions.py`:

```python
from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from tag7.models import Course
from tag9.dependencies import require_staff
from tag9.schemas import UserRead
from tag10.models import CourseManager

# API5, bekannt: FastAPI prüft die Rolle und übergibt das bestätigte Konto.
StaffUser = Annotated[UserRead, Depends(require_staff)]


def managed_course(course_id: int, db: Session, user: UserRead) -> Course:
    if user.role != "staff":
        raise HTTPException(403, "Verwaltungsrecht erforderlich.")
    # Kurs-ID sucht einen Kurs. user.id bezeichnet ein Benutzerkonto.
    course = db.get(Course, course_id)
    if course is None:
        raise HTTPException(404, "Kurs nicht gefunden.")
    assignment = db.get(CourseManager, course_id)
    # API1, neu: Auch ein staff-Konto braucht die passende Kurszuordnung.
    # Zwei Konto-IDs vergleichen, nicht die Kurs-ID mit der Konto-ID.
    if assignment is None or assignment.user_id != user.id:
        raise HTTPException(403, "Keine Zuständigkeit für diesen Kurs.")
    return course
```

Datei `tag10/routers/courses.py`:

```python
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError

from tag7.models import Course
from tag7.schemas import CourseCount, CourseCreate, CourseRead
from tag9.dependencies import DbSession, get_current_user
from tag9.routers.courses import CourseId, Search
from tag10.models import CourseManager
from tag10.permissions import StaffUser, managed_course

router = APIRouter(prefix="/courses", tags=["Kurse"],
                   dependencies=[Depends(get_current_user)])


@router.get("", response_model=list[CourseRead])
def read_courses(db: DbSession, q: Search = None):
    # Der Katalog ist für alle angemeldeten Konten sichtbar.
    statement = select(Course)
    if q is not None:
        statement = statement.where(Course.title.contains(q, autoescape=True))
    return db.scalars(statement.order_by(Course.id)).all()


@router.get("/count", response_model=CourseCount)
def count_courses(db: DbSession):
    return {"count": db.scalar(select(func.count()).select_from(Course))}


@router.get("/{course_id}", response_model=CourseRead)
def read_course(course_id: CourseId, db: DbSession):
    course = db.get(Course, course_id)
    if course is None:
        raise HTTPException(404, "Kurs nicht gefunden.")
    return course


@router.post("", response_model=CourseRead, status_code=201)
def create_course(data: CourseCreate, db: DbSession, user: StaffUser):
    course = Course(title=data.title)
    db.add(course)
    # INSERT ausführen, damit MySQL die ID vergibt. Noch kein Commit.
    db.flush()
    db.add(CourseManager(course_id=course.id, user_id=user.id))
    result = CourseRead.model_validate(course)
    # Kurs und Zuordnung werden gemeinsam gespeichert.
    db.commit()
    return result


@router.put("/{course_id}", response_model=CourseRead)
def replace_course(course_id: CourseId, data: CourseCreate,
                   db: DbSession, user: StaffUser):
    # Rechte prüfen, bevor das Objekt verändert wird.
    course = managed_course(course_id, db, user)
    course.title = data.title
    db.flush()
    result = CourseRead.model_validate(course)
    db.commit()
    return result


@router.delete("/{course_id}", status_code=204)
def delete_course(course_id: CourseId, db: DbSession, user: StaffUser):
    managed_course(course_id, db, user)
    try:
        db.execute(delete(CourseManager).where(
            CourseManager.course_id == course_id
        ))
        db.execute(delete(Course).where(Course.id == course_id))
        db.commit()
    except IntegrityError as exc:
        # get_session rollt auch das vorangehende Löschen der Zuordnung zurück.
        raise HTTPException(409, "Kurs wird noch verwendet.") from exc
    return Response(status_code=204)
```

- Ergebnis: Vector darf Arithmantik ändern, Hagrid erhält dafür `403`.
- Bei Ablehnung bleiben Titel und Zuordnung unverändert.

> **⚠️ Pitfall: Kurs-ID mit Konto-ID vergleichen**
> `course_id == user.id` ist zufällig manchmal wahr – und dann falsch erlaubt.
> Verglichen wird `assignment.user_id` mit `user.id`: zwei Konto-IDs.

## 3. Nur eigene Buchungen liefern

- Der JOIN verbindet jede Buchung mit der Zuständigkeit ihres Kurses.
- Keine eigenen Treffer ergibt `[]`, nicht `403`.

Datei `tag10/routers/bookings.py`:

```python
from fastapi import APIRouter
from sqlalchemy import select

from tag7.models import Booking
from tag7.schemas import BookingBatchCreate, BookingRead
from tag9.dependencies import DbSession
from tag9.routers.bookings import create_booking_batch as save_batch
from tag10.models import CourseManager
from tag10.permissions import StaffUser, managed_course

router = APIRouter(tags=["Buchungen"])


@router.get("/bookings", response_model=list[BookingRead])
def read_bookings(db: DbSession, user: StaffUser):
    statement = (
        select(Booking)
        # Zuständigkeit zum Kurs der Buchung hinzunehmen.
        .join(CourseManager, CourseManager.course_id == Booking.course_id)
        # API1: Nur Kurse des bestätigten Kontos auswählen.
        .where(CourseManager.user_id == user.id)
        .order_by(Booking.id)
    )
    return db.scalars(statement).all()


@router.post("/booking-batches", response_model=list[BookingRead],
             status_code=201)
def create_booking_batch(data: BookingBatchCreate,
                         db: DbSession, user: StaffUser):
    # API1: Auch die Kurs-ID aus einem gültigen JSON braucht eine Rechteprüfung.
    managed_course(data.course_id, db, user)
    # Normaler Python-Aufruf: Wir reichen die bereits offene Session weiter.
    # FastAPI führt bei diesem direkten Aufruf keine Dependencies erneut aus.
    # Tag 9 prüft die Fachregeln und committet die ganze Gruppe.
    return save_batch(data=data, db=db)
```

> **⚠️ Pitfall: Nur staff prüfen**
> Vector und Hagrid haben beide die Rolle `staff`.
> Ohne Zuständigkeitsfilter sieht jeder alle Buchungen.
> Auch eine `course_id` im JSON-Body muss geprüft werden.

## 4. Erlaubte Listen begrenzen: API4

- `limit`: Seitengröße, höchstens 50.
- `after_id`: letzte erhaltene ID – keine Seitennummer.

Datei `tag10/pagination.py`:

```python
from typing import Annotated

from fastapi import Query

# API4: Höchstens 50 Treffer anfordern. 51 ergibt bereits hier 422.
# 50 ist unser Unterrichtswert, keine Vorgabe von OWASP.
Limit = Annotated[int, Query(ge=1, le=50)]

# Navigation: Nach der letzten erhaltenen ID weiterlesen.
# Beispiel: IDs 4 und 9 erhalten -> nächste Anfrage mit after_id=9.
AfterId = Annotated[int, Query(ge=0)]
```

In beiden Routern den Import ergänzen und nur die Listenfunktion ersetzen:

```python
from tag10.pagination import AfterId, Limit
```

Ausschnitt `tag10/routers/courses.py`:

```python
@router.get("", response_model=list[CourseRead])
def read_courses(db: DbSession, q: Search = None,
                 limit: Limit = 20, after_id: AfterId = 0):
    # Der Katalog ist für alle angemeldeten Konten sichtbar.
    statement = select(Course).where(Course.id > after_id)
    if q is not None:
        # q auch auf der nächsten Seite mitsenden.
        statement = statement.where(Course.title.contains(q, autoescape=True))
    return db.scalars(
        statement.order_by(Course.id).limit(limit)
    ).all()  # Erst die begrenzte Ergebnismenge laden.
```

Ausschnitt `tag10/routers/bookings.py`:

```python
@router.get("/bookings", response_model=list[BookingRead])
def read_bookings(db: DbSession, user: StaffUser,
                  limit: Limit = 20, after_id: AfterId = 0):
    statement = (
        select(Booking)
        .join(CourseManager, CourseManager.course_id == Booking.course_id)
        .where(CourseManager.user_id == user.id)  # API1: Welche Zeilen?
        .where(Booking.id > after_id)            # Navigation: Wo weiter?
        .order_by(Booking.id)
        .limit(limit)                           # API4: Wie viele Treffer?
    )
    return db.scalars(statement).all()
```

1. `GET /courses?limit=1`: genau ein Treffer.
2. Dessen ID als `after_id` senden: der nächste Treffer folgt.
3. `GET /courses?limit=51`: `422`.

> **⚠️ Pitfall: Ohne order_by blättern**
> `after_id` funktioniert nur bei aufsteigend sortierten IDs.
> Ohne Sortierung können Treffer doppelt erscheinen oder fehlen.

| Grenze | Wo umgesetzt? | Beispiel | Ergebnis |
| --- | --- | --- | --- |
| Erlaubte Felder | `CourseCreate` mit `extra="forbid"` | `user_id` zusätzlich senden | 422 |
| Titel | `CourseCreate` | leer oder über 100 Zeichen | 422 |
| Gruppengröße | `BookingBatchCreate` | mehr als 20 Schüler-IDs | 422 |
| Seitengröße | `Limit` und SQL-`LIMIT` | `limit=51` | 422 |
| ID-Grenze | `AfterId` | `after_id=-1` | 422 |

## 5. Die App sicher konfigurieren: API8

API8 bedeutet „Security Misconfiguration“. Wir setzen sie zentral in
`tag10/main.py` um.

| API8-Maßnahme | Stelle in `tag10/main.py` |
| --- | --- |
| Debug-Fehlerseiten abschalten | `FastAPI(debug=False)` |
| Dokumentation bewusst freigeben | `docs_url` und `openapi_url` |
| Interne Details aus Fehlern entfernen | Fehlerhandler registrieren |
| Erlaubte Zielnamen festlegen | `TrustedHostMiddleware` |

Datei `tag10/main.py`:

```python
import logging
import os

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError

from tag8.logging_setup import configure_logging
from tag8.rules import SchoolYearTooLow
from tag10.routers import bookings, courses
from tag9.routers import auth

configure_logging()
logger = logging.getLogger("hogwarts.api")



def school_year_error(request: Request, exc: SchoolYearTooLow):
    return JSONResponse(status_code=409, content={"detail": str(exc)})


def database_error(request: Request, exc: OperationalError):
    logger.error("database_unavailable")
    return JSONResponse(status_code=503, content={
        "detail": "Datenbank derzeit nicht erreichbar.",
    })


def unexpected_error(request: Request, exc: Exception):
    # Der rohe Fehlertext könnte SQL-Parameter oder Zugangsdaten enthalten.
    logger.error("unhandled_request_error")
    return JSONResponse(status_code=500, content={
        "detail": "Interner Fehler.",
    })


def create_app(show_docs=False):
    # API8: Zentrale Sicherheitskonfiguration in tag10/main.py.
    # Jede Ausführung erzeugt eine neue, gleich konfigurierte FastAPI-Instanz.
    app = FastAPI(
        title="Hogwarts-Kursverwaltung", version="0.6.0",
        debug=False,  # API8: Keine Debug-Fehlerseiten mit internen Details.
        # API8: Dokumentation bewusst je Betriebsmodus freigeben.
        # Das Abschalten ersetzt keine Rechteprüfung.
        docs_url="/docs" if show_docs else None,
        redoc_url=None,
        openapi_url="/openapi.json" if show_docs else None,
    )
    app.include_router(auth.router)
    app.include_router(courses.router)
    app.include_router(bookings.router)

    # Fehlerklasse und Funktion ohne Klammern registrieren.
    # FastAPI ruft den passenden Handler erst beim Auftreten des Fehlers auf.
    # API8: Unsere Handler vermeiden interne SQL-Details in Fehlerantworten.
    app.add_exception_handler(SchoolYearTooLow, school_year_error)
    app.add_exception_handler(OperationalError, database_error)
    app.add_exception_handler(Exception, unexpected_error)

    @app.get("/health")
    def read_health():
        return {"status": "ok"}

    # API8 in main.py: Host-Prüfung für die gesamte App registrieren.
    # Die Middleware prüft vor der Route: unbekannter Zielname -> 400.
    # Beim Deployment den tatsächlichen API-Domainnamen ergänzen.
    app.add_middleware(
        TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1"]
    )
    return app


app = create_app(show_docs=os.environ.get("API_DOCS", "0") == "1")
```

| Beispiel | Öffentliche Antwort |
| --- | --- |
| `limit=51` | Feld `limit` ist ungültig |
| Passwort fehlt | Feld `password` ist ungültig oder fehlt |
| Beliebiges Zusatzfeld | Nur `request`; freier Feldname wird nicht gespiegelt |
| Unerwarteter Programmfehler | `Interner Fehler.` (500) |

- Middleware umschließt jede Anfrage und prüft vor der Route.
- Der Host-Header benennt das Ziel. Er bestätigt keine Client-Identität.

> **⚠️ Pitfall: Handler mit Klammern registrieren**
> `add_exception_handler(..., invalid_request)` übergibt die Funktion.
> `invalid_request()` würde sie sofort aufrufen – und scheitern.

Entwicklungsserver mit Dokumentation starten:

```powershell
$env:API_DOCS = "1"
python -m uvicorn tag10.main:app --reload --host 127.0.0.1 --port 8000
```

## 6. Schutzwirkung mit Postman prüfen

- Collection `docs/postman/10-Tag10-Hogwarts.postman_collection.json` importieren.
- Lokale Passwörter für vector, hagrid und babbling eintragen.
- `base_url`: `http://127.0.0.1:8000`. Im Runner Ordner 00 → 01 → 02 → 03 → 04.

| Ordner | Request | Beobachtung |
| --- | --- | --- |
| 00 – Anmeldung | POST /auth/login, GET /auth/me | Drei Konten anmelden |
| 01 – Probekurse | POST /courses | Vector und Hagrid erhalten je einen eigenen Kurs |
| 02 – Rechte | PUT, DELETE /courses/{id} | Eigene Änderung erlaubt; fremde 403 |
| 03 – Grenzen | GET /courses?limit=1, after_id | Nächste Seite folgt |
| 03 – Grenzen | GET /courses?limit=51 | 422 mit bereinigter Feldinformation |
| 03 – Grenzen | POST /courses mit user_id | 422 |
| 03 – Grenzen | POST /booking-batches mit 21 IDs | 422, keine Buchung |
| 04 – Aufräumen | DELETE /courses/{id}, POST /auth/logout | Probekurse weg, Token widerrufen |
| 05 – nach Aufgabe 3 | GET /courses/{id}/bookings | Eigener Kurs 200; fremder 403 |

- Bei `401` neu anmelden; bei `403` Rolle und Zuordnung prüfen.
- Passwörter und Token danach aus Postman entfernen.

## 7. Mit Tests nachweisen

```powershell
$testCompose = @("--env-file", ".env.test", "-f", "compose.test.yaml")
docker compose @testCompose up -d --wait test_db
python -m tag8.init_test_db
```

| Befehl | Zweck |
| --- | --- |
| `docker compose @testCompose up -d --wait test_db` | Testdienst starten und warten |
| `docker compose @testCompose ps` | Status ansehen |
| `docker compose @testCompose logs --tail 50 test_db` | Startprobleme untersuchen |
| `docker compose @testCompose stop test_db` | Anhalten, Daten behalten |

- `init_test_db` migriert die Testdatenbank; erwartet wird Revision `0004`.
- Nur `tests/tag10` ausführen; ältere Tests erwarten andere Revisionen.

| Fixture | Bedeutung im Test |
| --- | --- |
| `api_client` | Anfrage an die App mit der Testdatenbank |
| `login_as("hagrid")` | Anmeldung als konkretes Konto |
| `seed["own_id"]` | Vectors Kurs; Hagrid ist nicht zuständig |
| `db_factory()` | Gespeicherte Werte unabhängig nachlesen |

Gemeinsam geschrieben – Datei `tests/tag10/test_objects.py`:

```python
def test_other_staff_cannot_change_course(api_client, login_as, seed,
                                         db_factory):
    # Beide Konten sind staff. Nur die Zuständigkeit unterscheidet sie.
    response = api_client.put(
        f"/courses/{seed['own_id']}",
        headers=login_as("hagrid"),
        json={"title": "Fremde Änderung"},
    )

    assert response.status_code == 403
    with db_factory() as db:
        assert db.get(Course, seed["own_id"]).title == "Arithmantik"
```

```powershell
python -m pytest tests/tag10/test_objects.py -k other_staff -q
python -m pytest tests/tag10/test_limits.py -q
python -m pytest .\tests\tag10 -q
```

| Datei | Aussage |
| --- | --- |
| `test_objects.py` | Zuständigkeit, automatische Zuordnung, Rollback |
| `test_limits.py` | Seitengrenze und nächste Seite |
| `test_operation.py` | Falscher Host ergibt 400 (API8) |

- Erwartet: 8 Tests bestanden.

> **⚠️ Pitfall: API1 mit reader testen**
> Dann greift schon die Rollenprüfung (API5) – der Test beweist nichts Neues.
> Für API1 braucht es zwei staff-Konten mit unterschiedlicher Zuständigkeit.

## 8. Betriebsgrenzen benennen

Die App schützt heute: Rolle, Zuständigkeit, Seitengröße, Feld- und
Gruppengrenzen, bereinigte Fehler, Host-Prüfung. Beim Deployment fehlt noch:

| Maßnahme | Motivation | Heute |
| --- | --- | --- |
| HTTPS | Passwörter und Token auf dem Transportweg schützen | Nur lokales HTTP |
| Body-Limit | Zu große Requests früh abweisen (413) | Nicht eingerichtet |
| Rate-Limit | Zu viele Requests pro Zeit begrenzen (429) | Nicht eingerichtet |
| Zeit- und Verbindungsgrenzen | Langsame oder viele gleichzeitige Anfragen begrenzen | Deployment |
| Netzwerkzugang | Interne App- und DB-Ports nicht öffentlich | Deployment |

| Mechanismus | Zweck und Grenze |
| --- | --- |
| HTTPS | Verschlüsselt die Übertragung und prüft den Server |
| TrustedHost | Prüft den Zielnamen, nicht den Client |
| Firewall | Begrenzt erreichbare Ports; MySQL braucht keinen öffentlichen Port |
| CORS | Regelt Browser-Ursprünge; sperrt Postman nicht aus |

> **⚠️ Pitfall: Ein Mechanismus ersetzt die Rechteprüfung**
> HTTPS, Host-Prüfung, Firewall und CORS ergänzen API1 und API5.
> Auch abgeschaltete `/docs` sind keine Berechtigungsprüfung.

Betriebsmodus lokal prüfen:

```powershell
$env:API_DOCS = "0"
python -m uvicorn tag10.main:app --host 127.0.0.1 --port 8000
```

- `/health` bleibt erreichbar; `/docs` und `/openapi.json` liefern `404`.

```powershell
git ls-files -- .env .env.test
```

- Keine Ausgabe: Secrets sind aktuell nicht getrackt. Historie und Logs sind
  damit nicht geprüft.

## Das solltest du erklären können

1. Warum reicht die Rolle `staff` nicht für Änderungen an einem Kurs?
2. Warum ergibt eine leere eigene Buchungsliste `[]` und nicht `403`?
3. Warum schützt `limit` keine fremden Daten?
5. Welche Grenzen gehören in den Betrieb statt in die App?
