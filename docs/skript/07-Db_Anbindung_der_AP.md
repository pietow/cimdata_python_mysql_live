# Datenbankanbindung der API – Teilnehmerskript

Tag 7 des Kurses „Programmierung mit Python für komplexe Datenbanken“.

Die Hogwarts-Verwaltung möchte neue Kurse nach einem Neustart wiederfinden.
Du verbindest die API aus [Tag 6][tag6] mit der bekannten MySQL-Datenbank.
Danach buchst du mehrere Schüler gemeinsam und ergänzt einen Kursraum.


- Python läuft lokal im venv; MySQL läuft im Docker-Dienst db.
- Wir verwenden die vorhandenen Tabellen, keine zweite Datenbank.
- Neue Python-Dateien liegen im Unterrichtsprojekt unter tag7.
- Die Speicher-IDs von Tag 6 sind keine MySQL-IDs.
- Ein Serverneustart setzt die Daten ab heute nicht mehr zurück.

## Das brauchst du heute

| Auftrag | Werkzeug | Abschnitt |
| --- | --- | --- |
| Vorhandene Daten und IDs prüfen | MySQL und SOURCE | 0 |
| Datenbankzugriff bereitstellen | Engine, SessionLocal, Depends, yield | 1 |
| ORM-Objekte als JSON ausgeben | from_attributes, response_model | 2 |
| Kurse dauerhaft ändern | db.begin, add, flush | 3–4 |
| Einen Gruppenauftrag absichern | Gemeinsame Transaktion | 5 |
| Die Raumspalte ergänzen | Alembic, Baseline, Migration | 6 |
| Persistenz und Rollback prüfen | TestClient und unabhängiges Nachlesen | 7 |

> **Merke:** Eine erfolgreiche HTTP-Antwort allein speichert keine Daten.
> Erst der erfolgreiche Commit bestätigt die Änderungen in MySQL.

## 0. Den vorhandenen Datenbestand verbinden

### Umgebung vorbereiten

Die folgenden Pfade gelten im Unterrichtsprojekt `hogwarts-sql`.
Docker Desktop muss laufen. Beende den bisherigen Server mit Strg+C.

```powershell
.\.venv\Scripts\Activate.ps1
python -c "import sys; print(sys.executable)"
git status --short
docker compose up -d db
docker compose ps
```

- Docker soll db als healthy anzeigen.
- Falls die Aktivierung blockiert ist, das venv-Python direkt verwenden:

```powershell
.\.venv\Scripts\python.exe --version
```

- In den folgenden Befehlen dann diesen Pfad statt python verwenden.

Datei `requirements-tag7.txt`:

<!-- file: requirements-tag7.txt -->
```text
-r requirements-tag5.txt
alembic==1.20.0
```

```powershell
python -m pip install -r .\requirements-tag7.txt
python -m pip check
python -m pip freeze > .\requirements-tag7-lock.txt
```

- Alembic ist das neue Paket; die vorhandenen Versionen bleiben bestehen.
- Die lokale .env enthält MYSQL_HOST=127.0.0.1 und normalerweise Port 3307.
- Das Passwort bleibt in der lokalen Konfiguration und gehört nicht zu Git.

> **⚠️ Pitfall: den Container-Namen als lokalen Host verwenden**
> Python läuft in Windows und erreicht MySQL über den veröffentlichten Port.
> Der Name db gilt für Zugriffe innerhalb des Compose-Netzes.

### Den tatsächlichen Bestand prüfen

Den MySQL-Client öffnen und das Passwort interaktiv eingeben:

```powershell
docker compose exec db mysql -u dumbledore -p hogwarts
```

Datei `sql/tag7/01_start_check.sql`:

<!-- file: sql/tag7/01_start_check.sql -->
```sql
USE hogwarts;
SELECT DATABASE();
SELECT COUNT(*) AS students FROM students;
SELECT COUNT(*) AS courses FROM courses;
SELECT COUNT(*) AS bookings FROM bookings;
SELECT id, title FROM courses ORDER BY id;
SELECT id, first_name, last_name, house FROM students ORDER BY id;

SHOW CREATE TABLE students;
SHOW CREATE TABLE courses;
SHOW CREATE TABLE bookings;
```

Im MySQL-Client ausführen:

```text
SOURCE /work/sql/tag7/01_start_check.sql;
```

- Dokumentierter Ausgangsstand nach Tag 4: 10 Schüler, 5 Kurse, 9 Buchungen.
- Eigene Übungsdaten können diese Zahlen verändert haben.
- Notiere den tatsächlichen Bestand und die IDs von Harry, Ron und Alte Runen.
- Notiere die beiden berechneten, derzeit fehlenden positiven IDs.
- Vor der ersten Migration fehlen room und alembic_version.
- house darf im vorhandenen Schülerbestand NULL sein.

> **⚠️ Pitfall: den Seed erneut laden, um dieselben Zahlen zu bekommen**
> Vergleiche zuerst den vorhandenen Stand. Zusätzliche Daten sind möglich.
> Eine Speicher-ID aus Tag 6 ist kein Nachweis für eine vorhandene MySQL-Zeile.


### Postman passend zum Projektstand verwenden

- [Collection „Tag 7 – Hogwarts“][postman] importieren.
- harry_id, ron_id, missing_student_id und missing_course_id setzen.
- Fehlende IDs müssen durch die SQL-Abfrage tatsächlich als frei gelten.
- Keine gleichnamigen Environment-Variablen verwenden.
- Weitere IDs übernimmt die Collection aus den Antworten.

| Ordner | Verwendung |
| --- | --- |
| 00 Kurse lesen und ändern | Kurs-CRUD; base_url auf Port 8000. |
| 01 Gruppenbuchung und Rollback | Gruppenauftrag auf Port 8000. |
| 02 Nach der Migration | room in den Kursantworten prüfen. |
| 03 Übungen | Eigene Erweiterung; practice_url auf Port 8001. |
| 04 Bonus | Bonus-App; bonus_url auf Port 8002. |

- Alle drei Basis-URLs beginnen mit `http://127.0.0.1`.
- Ordner einzeln passend zum erreichten Stand verwenden.
- probe_course_id bezeichnet den später löschbaren Probekurs.
- created_course_id bezeichnet den neuen Kurs für die Gruppenbuchung.

> **⚠️ Pitfall: einen POST nach Neustart erneut senden**
> MySQL behält die Daten. Wiederholtes POST legt einen weiteren Kurs an.
> Die gesamte Collection daher nicht in einem Lauf ausführen.

## 1. Eine Session pro Request bereitstellen

### Engine, Fabrik und Session auseinanderhalten

| Baustein | Aufgabe | Lebensdauer |
| --- | --- | --- |
| Engine | Verbindungen und Pool verwalten. | Gemeinsam im Prozess. |
| SessionLocal | Neue Sessions erzeugen. | Gemeinsam im Prozess. |
| Session | ORM-Objekte und Transaktion verwalten. | Eine pro Request. |
| db.begin() | Einen Schreibauftrag abgrenzen. | Innerhalb der Route. |

Eine Dependency ist eine Hilfsfunktion, die FastAPI für die Route aufruft.
Hier öffnet und schließt sie die Session. Die Route bearbeitet den Auftrag.

Datei `tag7/db.py` – die bekannte Verbindung aus Tag 3:

<!-- file: tag7/db.py -->
```python
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine
from sqlalchemy.orm import sessionmaker


PROJECT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_DIR / ".env")

password = os.environ.get("MYSQL_PASSWORD")
if not password:
    raise ValueError("MYSQL_PASSWORD fehlt in der lokalen .env.")

url = URL.create(
    "mysql+mysqlconnector",
    username=os.environ.get("MYSQL_USER", "dumbledore"),
    password=password,
    host=os.environ.get("MYSQL_HOST", "127.0.0.1"),
    port=int(os.environ.get("MYSQL_PORT", "3307")),
    database=os.environ.get("MYSQL_DATABASE", "hogwarts"),
    query={"charset": "utf8mb4"},
)

engine = create_engine(
    url,
    pool_pre_ping=True,
    connect_args={"connection_timeout": 5},
)
SessionLocal = sessionmaker(bind=engine)
```

Datei `tag7/models.py` – vorhandene Tabellen, zunächst ohne Raumspalte:

<!-- file: tag7/models.py -->
```python
from datetime import date

from sqlalchemy import CheckConstraint, Date, ForeignKey, String
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.orm import relationship


class Base(DeclarativeBase):
    pass


class Student(Base):
    __tablename__ = "students"
    __table_args__ = (
        CheckConstraint(
            "school_year BETWEEN 1 AND 7",
            name="ck_students_school_year",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    house: Mapped[str | None] = mapped_column(String(20))
    school_year: Mapped[int] = mapped_column(TINYINT)
    bookings: Mapped[list["Booking"]] = relationship(
        back_populates="student"
    )


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    bookings: Mapped[list["Booking"]] = relationship(
        back_populates="course"
    )


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"))
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"))
    booking_date: Mapped[date] = mapped_column(Date)
    student: Mapped[Student] = relationship(back_populates="bookings")
    course: Mapped[Course] = relationship(back_populates="bookings")
```

- Das Modell beschreibt die Tabellen. Sein Import erzeugt sie nicht.
- create_all wird hier nicht beim API-Start aufgerufen.
- Eine Session ist weder ein Cursor noch eine neue Datenbank.

### Exkurs: Iterator und Generator

Diese Mini-Beispiele kannst du in einer Python-Konsole nachvollziehen.
Ein Iterator liefert mit next schrittweise Werte:

```python
iterator = iter([1, 2])
print(next(iterator))        # 1
print(next(iterator))        # 2
print(next(iterator, None))  # None: kein weiterer Wert
```

Eine Generatorfunktion enthält yield. Ihr Aufruf erzeugt einen Generator:

```python
def beispiel():
    print("Vor der Pause")
    yield 42
    print("Nach der Pause")


generator = beispiel()      # Noch keine Ausgabe: Generator nur erzeugt.
wert = next(generator)     # Ausgabe: Vor der Pause; liefert 42, pausiert.
print(wert)                # 42; die Funktion pausiert weiterhin.
next(generator, None)      # Ausgabe: Nach der Pause; Generator endet.
```

- Der Funktionskörper startet erst beim ersten next.
- yield liefert einen Wert und pausiert mit erhaltenem Zustand.
- Das nächste next setzt direkt nach yield fort.
- Jeder Generator ist ein Iterator; nicht jeder Iterator ist ein Generator.

### Die Session als Dependency übergeben

Datei `tag7/dependencies.py`:

<!-- file: tag7/dependencies.py -->
```python
from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from tag7.db import SessionLocal


def get_session() -> Iterator[Session]:
    # Eine neue Session pro Request, keine globale gemeinsame Session.
    with SessionLocal() as session:
        yield session
    # Der Kontext schließt auch bei einem Fehler. Er committet nicht.


DbSession = Annotated[Session, Depends(get_session)]
```

- SessionLocal() erstellt vor yield eine Session.
- yield übergibt sie an FastAPI und hält den with-Block offen.
- Die Route erhält die Session als db; sie erhält keinen Generator.
- Beim Aufräumen setzt FastAPI die Dependency fort und schließt die Session.
- DbSession verbindet den Typ Session mit seiner Beschaffung durch Depends.

Die folgende Skizze zeigt den normalen Ablauf ohne HTTP oder SQL-Abfrage.
Im Projektstamm nach dem Anlegen der Dependency ausprobieren:

```python
from tag7.dependencies import get_session

generator = get_session()   # Neuer Generator; noch keine Session erstellt.
db = next(generator)       # Session erstellen; bei yield pausieren.
try:
    print(type(db).__name__)  # Session; hier arbeitet sonst der Endpunkt.
finally:
    next(generator, None)  # Fortsetzen; with verlassen; Session schließen.
```

- Beim zweiten next wird aufgeräumt, keine neue Session erstellt.
- FastAPI verwaltet diesen Ablauf einschließlich Fehlerbehandlung selbst.
- Dieselbe Dependency wird innerhalb eines Requests standardmäßig gecacht.

![Request, Session und Transaktion][session-svg]

> **⚠️ Pitfall: Funktion und Funktionsaufruf vertauschen**
> Depends(get_session) übergibt die Funktion zur späteren Ausführung.
> get_session() würde sofort einen Generator erzeugen.
> Iterator[Session] ist eine Typangabe; sie erstellt keine Session.

> **⚠️ Pitfall: close mit Commit verwechseln**
> Schließen bestätigt keine Änderungen. Eine offene Transaktion wird beendet
> und zurückgerollt. Der Schreibauftrag muss vorher erfolgreich committen.
> Eine globale, parallel geteilte Session ersetzt die Dependency nicht.

## 2. Den Kurskatalog aus MySQL lesen

### ORM-Modell und Antwortmodell

- Course beschreibt die Tabelle und ihre ORM-Objekte.
- CourseRead legt fest, welche Attribute öffentlich als Antwort erscheinen.
- from_attributes erlaubt das Lesen von course.id und course.title.
- Es sucht selbst keine Datensätze und führt keine Migration durch.
- scalars liefert hier ORM-Objekte; get sucht über den Primärschlüssel.

Datei `tag7/schemas.py` – die Buchungsschemas werden schon mit angelegt:

<!-- file: tag7/schemas.py -->
```python
from datetime import date
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class CourseCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    title: str = Field(min_length=1, max_length=100)


class CourseRead(BaseModel):
    # ORM-Attribute lesen. Das Modell erzeugt keine Datenbanktabelle.
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str


class CourseCount(BaseModel):
    count: int


class BookingBatchCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    course_id: int = Field(ge=1)
    student_ids: list[Annotated[int, Field(ge=1)]] = Field(
        min_length=1, max_length=20
    )
    booking_date: date


class BookingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    student_id: int
    course_id: int
    booking_date: date
```

### Die Antwortumwandlung sichtbar machen

Datei `tag7/show_response.py` – liest den ersten vorhandenen Kurs:

<!-- file: tag7/show_response.py -->
```python
from sqlalchemy import select

from tag7.db import SessionLocal
from tag7.models import Course
from tag7.schemas import CourseRead

with SessionLocal() as db:
    course = db.scalar(select(Course).order_by(Course.id).limit(1))
    if course is None:
        raise RuntimeError("Für das Lesebeispiel fehlt ein Kurs.")
    answer = CourseRead.model_validate(course)
    print(type(course).__name__)  # Course: ORM-Objekt
    print(type(answer).__name__)  # CourseRead: Pydantic-Objekt

print(answer.model_dump())       # Python-Dictionary
print(answer.model_dump_json())  # JSON-Text
```

```powershell
python -m tag7.show_response
```

- CourseRead.model_validate erzeugt das geprüfte Antwortobjekt.
- model_dump liefert ein Dictionary; model_dump_json liefert JSON-Text.
- Die gelesenen Antwortfelder sind danach von der Session unabhängig.
- Nach der Migration kommt room in der Ausgabe hinzu.

### Den Kursrouter aufbauen

Datei `tag7/routers/courses.py` – vollständiger Zielstand für Abschnitte 2–4.
Zuerst Imports, Aliase und GET-Routen übernehmen.
POST und PUT folgen in Abschnitt 3; DELETE folgt in Abschnitt 4.

<!-- file: tag7/routers/courses.py -->
```python
from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query, Response
from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError

from tag7.dependencies import DbSession
from tag7.models import Course
from tag7.schemas import CourseCount, CourseCreate, CourseRead

router = APIRouter(prefix="/courses", tags=["Kurse"])
CourseId = Annotated[int, Path(ge=1)]
Search = Annotated[str | None, Query(min_length=2, max_length=100)]


@router.get("", response_model=list[CourseRead])
def read_courses(db: DbSession, q: Search = None):
    statement = select(Course).order_by(Course.id)
    if q is not None:
        # Werte werden gebunden. % und _ bleiben hier normale Suchzeichen.
        statement = statement.where(Course.title.contains(q, autoescape=True))
    return db.scalars(statement).all()


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
def create_course(data: CourseCreate, db: DbSession):
    with db.begin():
        course = Course(title=data.title)
        db.add(course)
        db.flush()  # INSERT ausführen und die vergebene ID einlesen.
        result = CourseRead.model_validate(course)
    # Erst nach erfolgreichem Commit den Erfolg zurückgeben.
    return result


@router.put("/{course_id}", response_model=CourseRead)
def replace_course(course_id: CourseId, data: CourseCreate, db: DbSession):
    # Auch der SELECT gehört in den Transaktionsblock.
    with db.begin():
        course = db.get(Course, course_id)
        if course is None:
            raise HTTPException(404, "Kurs nicht gefunden.")
        course.title = data.title
        db.flush()
        result = CourseRead.model_validate(course)
    return result


@router.delete("/{course_id}", status_code=204)
def delete_course(course_id: CourseId, db: DbSession):
    try:
        with db.begin():
            if db.get(Course, course_id) is None:
                raise HTTPException(404, "Kurs nicht gefunden.")
            # Direktes DELETE lässt MySQL die Fremdschlüssel prüfen.
            db.execute(delete(Course).where(Course.id == course_id))
    except IntegrityError as exc:
        # begin() hat bereits zurückgerollt, bevor dieser Block läuft.
        raise HTTPException(409, "Kurs wird noch verwendet.") from exc
    return Response(status_code=204)
```

Datei `tag7/main.py` – zunächst nur den Kursrouter registrieren:

<!-- file: tag7/main.py -->
```python
from fastapi import FastAPI

from tag7.routers import courses

app = FastAPI(title="Hogwarts-Kursverwaltung", version="0.3.0")
app.include_router(courses.router)


@app.get("/health")
def read_health():
    # Prozessprüfung; eine funktionierende Datenbank folgt daraus nicht.
    return {"status": "ok"}
```

```powershell
python -m uvicorn tag7.main:app --reload --host 127.0.0.1 --port 8000
```

- Swagger UI: `http://127.0.0.1:8000/docs`.
- GET /courses liefert den tatsächlichen MySQL-Katalog.
- GET /courses?q=Run sucht Alte Runen; /courses/count zählt die Kurse.
- /courses/0 liefert 422; eine gültige, fehlende Kurs-ID liefert 404.
- Suchwerte werden gebunden; autoescape behandelt % und _ als Suchzeichen.
- Groß-/Kleinschreibung folgt nun der MySQL-Kollation statt Python-casefold.

> **⚠️ Pitfall: ein grünes /health als Datenbanknachweis verwenden**
> /health prüft nur den API-Prozess. Erst eine Datenbankroute nutzt MySQL.
> Starte tag7.main, damit nicht versehentlich die Speicher-App aus Tag 6 läuft.

## 3. Einen Kurs dauerhaft anlegen und korrigieren

### Die Transaktionsgrenze vor die erste Abfrage setzen

- Ergänze jetzt POST und PUT aus dem vollständigen Kursrouter.
- with db.begin() bestätigt den ganzen Block bei erfolgreichem Verlassen.
- Verlässt eine Ausnahme den Block, wird zurückgerollt.
- Auch ein SELECT kann automatisch eine Transaktion beginnen: autobegin.
- Deshalb gehören Prüfen und Ändern gemeinsam in den Schreibblock.

Datei `tag7/show_transaction_state.py` – verändert keine Datensätze:

<!-- file: tag7/show_transaction_state.py -->
```python
from sqlalchemy import func, select

from tag7.db import SessionLocal
from tag7.models import Course

with SessionLocal() as db:
    print(db.in_transaction())
    db.scalar(select(func.count()).select_from(Course))
    print(db.in_transaction())
    # Ein db.begin() an dieser Stelle wäre für unseren Ablauf zu spät.
    db.rollback()
    print(db.in_transaction())
```

```powershell
python -m tag7.show_transaction_state
```

Erwartete Ausgabe: False, True, False.
rollback beendet hier die durch den SELECT eröffnete Lesetransaktion.

| Schritt beim Anlegen | Wirkung |
| --- | --- |
| db.add(course) | Neues Objekt in der Session vormerken. |
| db.flush() | INSERT ausführen und die MySQL-ID übernehmen. |
| CourseRead.model_validate(course) | Die Antwort noch vor Commit prüfen. |
| begin-Block erfolgreich verlassen | Änderungen committen. |
| return result | Erst nach erfolgreichem Commit antworten. |

> **⚠️ Pitfall: SELECT vor db.begin() ausführen**
> Dadurch kann die Session bereits eine aktive Transaktion besitzen.
> Ein weiteres äußeres begin meldet dann „Transaction already begun“.
> Schließe die Existenzprüfung in denselben Schreibblock ein.

### Den vollständigen CRUD-Weg prüfen

POST /courses mit folgendem Body senden:

```json
{"title": " Flugkunde "}
```

- Erwartet: 201 und Flugkunde ohne Rand-Leerzeichen.
- Die Antwort-ID als probe_course_id übernehmen.
- GET /courses/{{probe_course_id}} liefert den neuen Kurs.
- Server mit Strg+C beenden und mit demselben Befehl neu starten.
- Der erneute GET liefert weiterhin 200.

PUT /courses/{{probe_course_id}} mit folgendem Body senden:

```json
{"title": "Flugtraining"}
```

- Erwartet: 200; der nächste GET zeigt Flugtraining.
- Ein leerer Titel liefert 422; ein PUT auf eine fehlende ID liefert 404.
- Titel sind nicht unique; ein weiterer POST erzeugt einen weiteren Kurs.

> **⚠️ Pitfall: flush als dauerhafte Speicherung verstehen**
> Nach flush sind SQL und ID vorhanden, aber noch kein Commit bestätigt.
> Ein Fehler im Block kann das INSERT weiterhin zurückrollen.
> Ein Commit erst nach der HTTP-Erfolgsmeldung käme zu spät.

### Warum POST ein Antwortobjekt zurückgibt

- Ein Commit lässt ORM-Attribute standardmäßig ablaufen.
- Späteres Lesen dieser Attribute kann einen weiteren SELECT auslösen.
- POST und PUT erzeugen CourseRead deshalb nach flush und vor Commit.
- GET gibt das geladene ORM-Objekt an FastAPIs Antwortprüfung weiter.

## 4. Löschen und Fremdschlüssel respektieren

Ergänze DELETE aus dem vollständigen Kursrouter in Abschnitt 2.
Das direkte delete(Course) überlässt MySQL die Fremdschlüsselprüfung.

| Auftrag | Ergebnis |
| --- | --- |
| Probekurs ohne Buchungen löschen | 204, kein Body. |
| Gelöschten Kurs erneut lesen | 404. |
| Fehlende positive Kurs-ID löschen | 404. |
| Tatsächlich gebuchten Kurs löschen | 409; Kurs und Buchungen bleiben. |

- IntegrityError wird außerhalb von begin abgefangen.
- Zu diesem Zeitpunkt hat der Kontext bereits zurückgerollt.
- SQL-Fehlertexte und Zugangsdaten gehören nicht in die öffentliche Antwort.

> **⚠️ Pitfall: abhängige Buchungen ungefragt mitlöschen**
> Der Kurs ist vorhanden, wird aber noch verwendet: Das ist ein Konflikt.
> 409 beschreibt diesen Fall; 404 würde die falsche Ursache nennen.
> Bei 204 keinen zusätzlichen JSON-Body zurückgeben.

Commitpunkt im Unterrichtsprojekt:

```powershell
git add tag7 requirements-tag7.txt requirements-tag7-lock.txt
git add sql/tag7/01_start_check.sql
git commit -m "Kurs-API mit MySQL und Session-Dependency verbinden"
```

## 5. Mehrere Schüler gemeinsam buchen

Harry und Ron sollen gemeinsam ein zusätzliches Angebot buchen.
Der ganze Auftrag soll gelingen oder vollständig zurückgerollt werden.

- Eine positive Schüler-ID ist nicht automatisch in MySQL vorhanden.
- Die API erlaubt hier 1–20 Schüler-IDs je Auftrag.
- Kapazität und doppelte Buchungen werden heute noch nicht geregelt.
- Eine gemeinsame Transaktion umfasst alle Prüfungen und INSERTs.

Datei `tag7/routers/bookings.py`:

<!-- file: tag7/routers/bookings.py -->
```python
from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from tag7.dependencies import DbSession
from tag7.models import Booking, Course, Student
from tag7.schemas import BookingBatchCreate, BookingRead

router = APIRouter(tags=["Buchungen"])


@router.get("/bookings", response_model=list[BookingRead])
def read_bookings(db: DbSession):
    return db.scalars(select(Booking).order_by(Booking.id)).all()


@router.post("/booking-batches", response_model=list[BookingRead],
             status_code=201)
def create_booking_batch(data: BookingBatchCreate, db: DbSession):
    try:
        with db.begin():
            if db.get(Course, data.course_id) is None:
                raise HTTPException(404, "Kurs nicht gefunden.")
            result = []
            for student_id in data.student_ids:
                if db.get(Student, student_id) is None:
                    raise HTTPException(404, "Schüler nicht gefunden.")
                booking = Booking(
                    student_id=student_id,
                    course_id=data.course_id,
                    booking_date=data.booking_date,
                )
                db.add(booking)
                # Bewusst je Eintrag flushen: Fehler nach INSERT vorführen.
                db.flush()
                result.append(BookingRead.model_validate(booking))
        return result
    except IntegrityError as exc:
        raise HTTPException(409, "Buchungskonflikt.") from exc
```

Datei `tag7/main.py` vollständig ersetzen, um beide Router zu registrieren:

<!-- file: tag7/main.py -->
```python
from fastapi import FastAPI

from tag7.routers import bookings, courses

app = FastAPI(title="Hogwarts-Kursverwaltung", version="0.3.0")
app.include_router(courses.router)
app.include_router(bookings.router)


@app.get("/health")
def read_health():
    # Prozessprüfung; eine funktionierende Datenbank folgt daraus nicht.
    return {"status": "ok"}
```

### Zuerst einen Fehler nach dem ersten INSERT prüfen

1. Ein zusätzliches Angebot Flugkunde mit POST /courses anlegen.
2. Seine ID als created_course_id notieren.
3. Harrys und Rons MySQL-IDs sowie die geprüfte fehlende ID übernehmen.
4. GET /bookings abrufen und den bisherigen Bestand festhalten.
5. Einen Gruppenauftrag mit Harry und dem fehlenden Schüler senden.

Die folgenden IDs sind Platzhalter und müssen ersetzt werden.
course_id muss auf den tatsächlich angelegten Kurs zeigen:

```json
{
  "course_id": 999,
  "student_ids": [1, 999999],
  "booking_date": "1993-09-06"
}
```

| Ablauf im Fehlerfall | Wirkung |
| --- | --- |
| Harry prüfen, Buchung adden und flushen | INSERT ausgeführt, kein Commit. |
| Zweiten Schüler suchen | Nicht vorhanden; HTTPException mit 404. |
| begin-Block mit Ausnahme verlassen | Auch Harrys INSERT wird zurückgerollt. |
| GET /bookings erneut aufrufen | Keine neue Buchung aus dem Auftrag. |

Danach die fehlende ID durch Rons ID ersetzen und genau einmal senden.

- Erwartet: 201 und zwei Buchungen, die einen Neustart überstehen.
- booking_one_id und booking_two_id aus der Antwort notieren.
- Den Kurs und beide Buchungen für die Nachmittagsaufgaben behalten.
- Gegenüber dem Startbestand: ein Kurs und zwei Buchungen zusätzlich.

> **⚠️ Pitfall: pro Schüler committen**
> Dann könnte Harrys Buchung trotz Fehler beim zweiten Schüler bestehen bleiben.
> Die Transaktion gehört um den gesamten Auftrag, nicht in jeden Durchlauf.
> Eine Ausnahme nicht im Block schlucken und dann normal weiterlaufen.

> **⚠️ Pitfall: ID-Lücken als fehlgeschlagenes Rollback deuten**
> MySQL kann vergebene Auto-IDs nach einem Rollback überspringen.
> Vergleiche Datensätze. Eine vergebene ID beweist keinen Commit.
> Atomarität löst außerdem nicht automatisch doppelte oder parallele Buchungen.

Commitpunkt:

```powershell
git add tag7
git commit -m "Gruppenbuchungen atomar ueber die API speichern"
```

## 6. Die erste Migration am vorhandenen Bestand

Die Verwaltung benötigt einen optionalen Raum für jeden Kurs.
Die vorhandenen Datensätze müssen bei dieser Schemaänderung erhalten bleiben.

| Begriff | Bedeutung |
| --- | --- |
| ORM-Modell | Beschreibt die gewünschte Tabellenstruktur. |
| Migration | Beschreibt die Änderung vom alten zum neuen Schema. |
| alembic_version | Speichert die als angewendet markierte Revision. |
| Baseline 0001 | Beschreibt den übernommenen Stand ohne room. |

### Alembic einmalig einrichten

- Uvicorn stoppen, damit Reload keinen unvollständigen Schemawechsel lädt.
- Falls alembic.ini oder der Ordner schon existieren: zuerst den Stand prüfen.
- init nicht bei jeder Wiederaufnahme erneut ausführen.

```powershell
python -m alembic init alembic
Get-Content .\alembic.ini
```

- Die erzeugte alembic.ini mit script_location und prepend_sys_path behalten.
- Keine Zugangsdaten eintragen; env.py nutzt die vorhandene Engine.

Datei `alembic/env.py` vollständig ersetzen:

<!-- file: alembic/env.py -->
```python
from alembic import context

from tag7.db import engine
from tag7.models import Base

# Alle drei ORM-Klassen wurden durch den Modulimport registriert.
target_metadata = Base.metadata


def run_migrations_offline():
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
```

### Den vorhandenen Stand als Baseline übernehmen

Zuerst das Gerüst der Baseline mit Alembic erzeugen:

```powershell
python -m alembic revision -m "baseline" --rev-id 0001
```

- Alembic legt `alembic/versions/0001_baseline.py` mit leerem upgrade und downgrade an.
- `--rev-id 0001` ergibt die feste Revision 0001 statt einer zufälligen ID.
- Den Kopf der erzeugten Datei behalten. Nur drei Stellen ergänzen:
  den mysql-Import sowie die Rümpfe von upgrade und downgrade.
- Die vollständige Datei steht unten. Nur Create Date weicht bei euch ab.

| Kopfzeile | Bedeutung |
| --- | --- |
| `revision: str = '0001'` | Eigene Kennung dieser Migration. |
| `down_revision = None` | Kein Vorgänger: Das ist die erste Migration der Kette. |
| `branch_labels`, `depends_on` | Für verzweigte Migrationsketten; hier immer None. |
| `Revises`, `Create Date` im Docstring | Nur Dokumentation; Alembic liest die Variablen. |

- Typangaben wie `Union[str, Sequence[str], None]` und `-> None` sind Type Hints.
- Für die Ausführung zählen nur die Werte.

> **⚠️ Pitfall: Baseline mit --autogenerate erzeugen**
> Autogenerate vergleicht die Modelle mit der aktuellen Datenbank.
> Die Tabellen existieren schon, upgrade bliebe deshalb leer.
> Eine Baseline muss aber eine leere Datenbank aufbauen können.

<!-- file: alembic/versions/0001_baseline.py -->
```python
"""baseline

Revision ID: 0001
Revises: 
Create Date: 2026-10-20 17:20:51.726941

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
# Ergänzt: für den MySQL-Typ TINYINT.
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision: str = '0001'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Ergänzt: Nur eine leere Datenbank braucht diese CREATE-Anweisungen.
    op.create_table(
        "students",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("first_name", sa.String(50), nullable=False),
        sa.Column("last_name", sa.String(50), nullable=False),
        sa.Column("house", sa.String(20), nullable=True),
        sa.Column("school_year", mysql.TINYINT(), nullable=False),
        sa.CheckConstraint(
            "school_year BETWEEN 1 AND 7",
            name="ck_students_school_year",
        ),
    )
    op.create_table(
        "courses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(100), nullable=False),
    )
    op.create_table(
        "bookings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("booking_date", sa.Date(), nullable=False),
        sa.ForeignKeyConstraint(
            ["student_id"], ["students.id"], name="fk_bookings_student"
        ),
        sa.ForeignKeyConstraint(
            ["course_id"], ["courses.id"], name="fk_bookings_course"
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Ergänzt: Schutz des bestehenden Unterrichtsbestands vor versehentlichem DROP.
    raise RuntimeError("Die Baseline wird in diesem Kurs nicht entfernt.")
```

- Vor stamp die SHOW-CREATE-Ausgaben mit der Baseline vergleichen.
- Prüfe Namen, Typen, Längen, Nullbarkeit, Schlüssel und AUTO_INCREMENT.
- Prüfe auch Schuljahr-CHECK, Fremdschlüssel und InnoDB.
- Bei Abweichungen stoppen; keine Tabellen für einen Neustart löschen.
- Der folgende Ablauf gilt für den bereits vorhandenen Kursbestand:

```powershell
python -m alembic history
python -m alembic stamp 0001
python -m alembic current
python -m alembic check
```

| Befehl | Aussage |
| --- | --- |
| history | Welche Migrationsdateien sind vorhanden und wie verbunden? |
| stamp 0001 | Nur den geprüften Stand markieren; kein CREATE ausführen. |
| current | Welche Revision steht in der verbundenen Datenbank? |
| check | Würde Autogenerate neue Migrationsoperationen vorschlagen? |

- Erwartet: current zeigt 0001; check findet keine neue Upgrade-Operation.
- check ergänzt den manuellen Vergleich, erkennt aber nicht jede Abweichung.
- Die Baseline enthält Tabellen, aber keine Schüler- oder Kursbeispieldaten.

> **⚠️ Pitfall: stamp als Schemareparatur verwenden**
> stamp prüft das Schema nicht und führt keine Tabellenänderung aus.
> Die Markierung ist nur nach dem Abgleich des vorhandenen Stands passend.
> upgrade 0001 wäre für eine leere Datenbank gedacht, nicht für den Altbestand.

### room im Modell ergänzen

In `tag7/models.py` nur Course ersetzen. Imports und andere Klassen behalten:

```python
class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    room: Mapped[str | None] = mapped_column(String(30))
    bookings: Mapped[list["Booking"]] = relationship(
        back_populates="course"
    )
```

Eine neue Revision erzeugen und ihren Inhalt lesen:

```powershell
python -m alembic revision --autogenerate --rev-id 0002 -m "course_room"
Get-Content .\alembic\versions\0002_course_room.py
```

Datei `alembic/versions/0002_course_room.py` – erwarteter vollständiger Inhalt:

<!-- file: alembic/versions/0002_course_room.py -->
```python
"""course_room

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-20 17:45:12.104233

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0002'
down_revision: Union[str, Sequence[str], None] = '0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Bestehende Kurse erhalten NULL. Ihre IDs und Titel bleiben erhalten.
    op.add_column("courses", sa.Column("room", sa.String(30), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Dabei gehen eingetragene Raumwerte verloren.
    op.drop_column("courses", "room")
```

- `down_revision = '0001'` verbindet diese Datei mit der Baseline zur Kette.
- Die erzeugten Kommentare „### commands auto generated …“ dürfen entfernt werden.

- Der Entwurf darf nur die optionale Raumspalte hinzufügen.
- Unerwartete DROP- oder weitere Änderungsanweisungen zuerst klären.
- Alte Kurse erhalten NULL; ihre IDs und Titel bleiben erhalten.

```powershell
python -m alembic upgrade head
python -m alembic current
python -m alembic check
```

> **⚠️ Pitfall: nur das Python-Modell ändern**
> Das Modell erzeugt keine fehlende Spalte in einer vorhandenen Tabelle.
> Erst upgrade führt die geprüfte Migration aus. stamp head ersetzt sie nicht.
> Ein gewöhnliches Rollback macht MySQL-DDL nicht zuverlässig rückgängig.
> downgrade entfernt hier room und damit eventuell gespeicherte Raumwerte.

### room als Antwortfeld zulassen

In `tag7/schemas.py` nur CourseRead ersetzen:

```python
class CourseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    room: str | None = None
```

- POST und PUT bearbeiten weiterhin nur den Titel.
- room ist im Pflichtteil ein Antwortfeld; seine Pflege folgt im Bonus.

Datei `sql/tag7/02_migration_check.sql`:

<!-- file: sql/tag7/02_migration_check.sql -->
```sql
USE hogwarts;
SELECT version_num FROM alembic_version;
SHOW COLUMNS FROM courses;
SELECT id, title, room FROM courses ORDER BY id;
SELECT COUNT(*) AS students FROM students;
SELECT COUNT(*) AS courses FROM courses;
SELECT COUNT(*) AS bookings FROM bookings;
```

Im MySQL-Client ausführen:

```text
SOURCE /work/sql/tag7/02_migration_check.sql;
```

- Erwartet: Revision 0002 und nullable VARCHAR(30) für room.
- Die Zeilenzahlen müssen dem Stand unmittelbar vor der Migration entsprechen.
- Server wieder mit dem bekannten Uvicorn-Befehl starten.
- Kursantworten enthalten jetzt zusätzlich `"room": null`.

Commitpunkt:

```powershell
git add tag7 alembic alembic.ini sql/tag7
git commit -m "Bestehendes Schema versionieren und Kursraum ergaenzen"
```

## 7. Persistenz und Rollback gezielt testen

Die vorgegebenen Tests rufen die API mit TestClient ohne Uvicorn auf.
MySQL muss trotzdem laufen: Das sind Integrationstests.

| Test | Was wird geprüft? |
| --- | --- |
| Kurs-CRUD | Anlegen, lesen, ändern, löschen und Statuscodes. |
| Erfolgreicher Gruppenauftrag | Zwei Buchungen sind in MySQL gespeichert. |
| Fehlender zweiter Schüler | 404 und unveränderter Buchungsbestand. |

- Jeder Gruppentest legt einen eigenen Kurs an und ist unabhängig vom anderen.
- Eine neue Session liest den gespeicherten Zustand nach.
- finally entfernt nur den eigenen Testkurs samt eigenen Testbuchungen.
- Mindestens zwei Schüler müssen bereits vorhanden sein.
- Die Hilfsfunktionen werden übernommen; eigene Fixtures folgen an Tag 8.
- Währenddessen keine parallelen Buchungen in diese Testkurse vornehmen.

<details>
<summary>Vollständige vorgegebene Testdatei aufklappen</summary>

Datei `tag7/test_api.py`:

<!-- file: tag7/test_api.py -->
```python
from fastapi.testclient import TestClient
from sqlalchemy import delete, func, select

from tag7.db import SessionLocal
from tag7.main import app
from tag7.models import Booking, Course, Student


# Vorgegebene Hilfsfunktionen: vorbereiten, nachlesen, aufräumen.
def prepare_batch_case():
    with SessionLocal.begin() as db:
        students = list(db.scalars(select(Student.id)
                                   .order_by(Student.id).limit(2)))
        assert len(students) == 2, "Zwei vorhandene Schüler benötigt."
        missing_id = db.scalar(select(func.max(Student.id))) + 1000
        course = Course(title="Flugkunde")
        db.add(course)
        db.flush()
        course_id = course.id
    return course_id, students, missing_id


def booking_snapshot(course_id):
    # Neue Session: den gespeicherten Stand dieses Testkurses prüfen.
    with SessionLocal() as db:
        statement = select(
            Booking.id, Booking.student_id, Booking.course_id,
            Booking.booking_date,
        ).where(Booking.course_id == course_id).order_by(Booking.id)
        return db.execute(statement).all()


def cleanup_course(course_id):
    # Nur die Datensätze des in diesem Test erzeugten Kurses entfernen.
    with SessionLocal.begin() as db:
        db.execute(delete(Booking).where(Booking.course_id == course_id))
        db.execute(delete(Course).where(Course.id == course_id))


def test_course_roundtrip():
    with TestClient(app) as client:
        response = client.post("/courses", json={"title": " Flugkunde "})
        assert response.status_code == 201
        course_id = response.json()["id"]
        try:
            assert response.json()["title"] == "Flugkunde"
            url = f"/courses/{course_id}"
            stored = client.get(url)
            assert stored.status_code == 200
            assert stored.json()["title"] == "Flugkunde"
            changed = client.put(url, json={"title": "Flugtraining"})
            assert changed.status_code == 200
            assert changed.json()["title"] == "Flugtraining"
            invalid = client.post("/courses", json={"title": " "})
            assert invalid.status_code == 422
            removed = client.delete(url)
            assert removed.status_code == 204
            assert removed.content == b""
            assert client.get(url).status_code == 404
        finally:
            cleanup_course(course_id)


def test_batch_saves_all_bookings():
    course_id, students, _ = prepare_batch_case()
    try:
        with TestClient(app) as client:
            response = client.post("/booking-batches", json={
                "course_id": course_id,
                "student_ids": students,
                "booking_date": "1993-09-06",
            })
        assert response.status_code == 201
        assert [row["student_id"] for row in response.json()] == students
        stored = booking_snapshot(course_id)
        assert [row.student_id for row in stored] == students
    finally:
        cleanup_course(course_id)


def test_batch_rolls_back_on_missing_student():
    course_id, students, missing_id = prepare_batch_case()
    try:
        before = booking_snapshot(course_id)
        with TestClient(app) as client:
            response = client.post("/booking-batches", json={
                "course_id": course_id,
                "student_ids": [students[0], missing_id],
                "booking_date": "1993-09-06",
            })
        assert response.status_code == 404
        assert response.json() == {"detail": "Schüler nicht gefunden."}
        assert booking_snapshot(course_id) == before
    finally:
        cleanup_course(course_id)
```

</details>

```powershell
python -m pytest .\tag7\test_api.py -q
```

- Erwartet: 3 passed. Die Live-Buchungen für den Nachmittag bleiben bestehen.
- Die Auto-ID-Zähler können durch diese Tests weiterlaufen.

> **⚠️ Pitfall: 404 allein als Rollback-Nachweis akzeptieren**
> Ein Endpunkt könnte immer 404 liefern, ohne einen Auftrag zu verarbeiten.
> Deshalb den gespeicherten Zustand vergleichen und auch den Erfolgsfall testen.
> Der Routencode zeigt zusätzlich den ersten flush vor der späteren Ausnahme.
> Ein fehlendes MySQL ist kein erfolgreicher Integrationstest.

## 8. Den Stand für den Nachmittag sichern

| Datei | Aufgabe |
| --- | --- |
| tag7/db.py | Engine und Session-Fabrik. |
| tag7/models.py | Student, Course mit room und Booking. |
| tag7/dependencies.py | Session pro Request. |
| tag7/schemas.py | Eingabe- und Antwortverträge. |
| tag7/routers/courses.py | Kurs-CRUD. |
| tag7/routers/bookings.py | Lesen und gemeinsame Buchungsanlage. |
| tag7/main.py | Router registrieren und Health bereitstellen. |
| alembic/ | Baseline 0001 und Raum-Migration 0002. |

- Das neue Angebot besitzt zwei neue Live-Buchungen.
- Die drei tatsächlichen Antwort-IDs sind für die Übungen notiert.

```powershell
git add tag7
git commit -m "Kursablauf und Buchungsrollback mit TestClient pruefen"
```

<details>
<summary>Endgültige Modelle und Schemas nach Revision 0002 aufklappen</summary>

Die Router und die Dependency oben bleiben gültig.
Diese vollständigen Dateien ersetzen die Zwischenstände vor der Migration.

Datei `tag7/models.py`:

<!-- file: tag7/models.py -->
```python
from datetime import date

from sqlalchemy import CheckConstraint, Date, ForeignKey, String
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.orm import relationship


class Base(DeclarativeBase):
    pass


class Student(Base):
    __tablename__ = "students"
    __table_args__ = (
        CheckConstraint(
            "school_year BETWEEN 1 AND 7",
            name="ck_students_school_year",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    house: Mapped[str | None] = mapped_column(String(20))
    school_year: Mapped[int] = mapped_column(TINYINT)
    bookings: Mapped[list["Booking"]] = relationship(
        back_populates="student"
    )


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    room: Mapped[str | None] = mapped_column(String(30))
    bookings: Mapped[list["Booking"]] = relationship(
        back_populates="course"
    )


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"))
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"))
    booking_date: Mapped[date] = mapped_column(Date)
    student: Mapped[Student] = relationship(back_populates="bookings")
    course: Mapped[Course] = relationship(back_populates="bookings")
```

Datei `tag7/schemas.py`:

<!-- file: tag7/schemas.py -->
```python
from datetime import date
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class CourseCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    title: str = Field(min_length=1, max_length=100)


class CourseRead(BaseModel):
    # ORM-Attribute lesen. Das Modell erzeugt keine Datenbanktabelle.
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    room: str | None = None


class CourseCount(BaseModel):
    count: int


class BookingBatchCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    course_id: int = Field(ge=1)
    student_ids: list[Annotated[int, Field(ge=1)]] = Field(
        min_length=1, max_length=20
    )
    booking_date: date


class BookingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    student_id: int
    course_id: int
    booking_date: date
```

</details>

### Eigenständige Übertragung

Verwende die [Aufgaben für Tag 7][aufgaben].
Die Übungs-App auf Port 8001 greift auf dieselbe MySQL-Datenbank zu.

| Aufgaben | Auftrag |
| --- | --- |
| 1–3 | Persistenz erklären, Schüler lesen und Filter mit UND kombinieren. |
| 4–6 | Buchung umbuchen, löschen und einen Gruppenfehler prüfen. |
| 7–8 | Migration kontrollieren und eigene PCPP1-Fragen beantworten. |
| 9–11 | Freiwillig: Datumsfilter, Raumpflege und Cursorvergleich. |

> **⚠️ Pitfall: getrennte Ports mit getrennten Datenbanken verwechseln**
> Kurs-App und Übungs-App verwenden heute denselben MySQL-Bestand.
> Änderungen daher nur an den dafür zusätzlich angelegten Einträgen vornehmen.

## 9. Kontrollfragen kompakt


| Frage | Kurzantwort |
| --- | --- |
| Welche Schicht nimmt den Auftrag entgegen? | HTTP-API. |
| Wer verwaltet ORM-Objekte? | Die SQLAlchemy-Session. |
| Wer prüft den Fremdschlüssel? | Die Datenbank. |
| Ist flush ein Commit? | Nein; SQL kann schon ausgeführt, aber offen sein. |
| Ist eine Session ein Cursor? | Nein; der Cursor arbeitet mit SQL und Zeilen. |
| Wie wird ein Datum zu JSON? | Als vereinbarte Zeichenkette. |
| Warum Suchwerte binden? | Datenwerte von der SQL-Struktur getrennt halten. |
| Macht Rollback eine Migration rückgängig? | Nicht zuverlässig bei MySQL-DDL. |


| API-Fall | Status |
| --- | --- |
| Ungültige Eingabe wie eine ID 0 | 422 |
| Gültige, nicht vorhandene Kurs-ID | 404 |
| Neue Ressource angelegt | 201 |
| Ungebuchten Kurs gelöscht | 204 ohne Body |
| Kurs mit bestehenden Buchungen löschen | 409 |
