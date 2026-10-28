# Performance und Skalierbarkeit – Teilnehmerskript


Vector möchte einen Tagesbericht: Buchungs-ID, Schülername, Kurstitel und Datum.
Der Bericht bleibt geschützt wie in Tag 10. Heute sorgen wir dafür, dass
MySQL und Python dafür keine unnötige Arbeit leisten.

## Das brauchst du heute

| Schritt | Leitfrage | Nachweis |
| --- | --- | --- |
| SQL-Plan lesen | Wie viele Zeilen liest MySQL für 20 Treffer? | `EXPLAIN ANALYZE` |
| Index | Findet MySQL die Tagesbuchungen gezielter? | Gleiche IDs, weniger Zeilenarbeit |
| Migration | Ist der Index im Projekt nachvollziehbar? | Revision `0005` |
| N+1 | Wie viele SELECTs schickt Python für einen Bericht? | SQL-Ausgabe mit `echo` |


- Alle Funktionen bleiben synchron. Anmeldung, Rollen und Zuständigkeit aus
  Tag 10 bleiben aktiv.
- Neue Dateien liegen in `tag11`, Tests in `tests/tag11`, SQL in `sql/tag11`.
- Wir vergleichen Ergebnisse und sichtbare Arbeit – keine feste Millisekunden-Grenze.


## 0. Umgebung und Bestand prüfen

```powershell
.\.venv\Scripts\Activate.ps1
New-Item -ItemType Directory -Force -Path .\tag11\routers, .\tests\tag11, .\sql\tag11
New-Item -ItemType File -Force -Path .\tag11\__init__.py, .\tag11\routers\__init__.py
docker compose up -d
python -m alembic current
```

- Ausgangspunkt: Revision `0004`. Keine neuen Python-Pakete nötig.
- Den Server aus Tag 10 mit Strg+C beenden.

Datei `sql/tag11/01_inventory.sql`:

```sql
SHOW CREATE TABLE bookings;
SHOW INDEX FROM bookings;
SHOW CREATE TABLE students;
SHOW INDEX FROM users;

SELECT u.username, b.booking_date, COUNT(*) AS bookings
FROM bookings AS b
JOIN course_managers AS cm ON cm.course_id = b.course_id
JOIN users AS u ON u.id = cm.user_id
GROUP BY u.username, b.booking_date
ORDER BY u.username, b.booking_date;
```

```powershell
docker compose exec db mysql -u dumbledore -p hogwarts
```

```text
SOURCE /work/sql/tag11/01_inventory.sql;
```

| Vorhandene Regel | Bedeutung |
| --- | --- |
| PRIMARY KEY / UNIQUE | Identifiziert die Zeile / erzwingt eindeutige Werte |
| FOREIGN KEY / CHECK | Verhindert ungültige Referenzen / begrenzt das Schuljahr |
| Normaler Index | Unterstützt Zugriffe; erlaubt Duplikate |

- Einen vorhandenen Berichtstag für Vector notieren. `1993-09-01` ist nur ein Beispiel.
- InnoDB legt Indizes für Fremdschlüssel selbst an. Mit `SHOW INDEX` prüfen.

> **⚠️ Pitfall: Index als Fachregel verstehen**
> Ein normaler Index beschleunigt nur Zugriffe. Er verbietet nichts.
> `UNIQUE` auf Schüler und Kurs wäre eine neue Entscheidung über erlaubte Buchungen.

## 1. SQL-Plan vor und nach einem Index

### Vier Zugriffsarten

Ein Index (B-Tree) hält seine Einträge nach dem Schlüssel sortiert. Darum kann
MySQL zum Anfang eines Bereichs springen und dort weiterlesen.

![Table scan: acht Tabellenzeilen prüfen und vier passende Buchungen finden.](../assets/11-01-table-scan.svg)

![Index lookup: den Schüler zur student_id einer ausgewählten Buchung über den Primärschlüssel suchen.](../assets/11-02-index-lookup.svg)

![Index range scan: den Datumsbereich suchen und vier passende Indexeinträge durchlaufen.](../assets/11-03-index-range-scan.svg)

![Index scan: alle acht Einträge des Datumsindex in der gewünschten Reihenfolge lesen.](../assets/11-04-index-scan.svg)


| Begriff im Plan | Merksatz | `type` in EXPLAIN |
| --- | --- | --- |
| Table scan | Tabellenzeilen durchlaufen | `ALL` |
| Index range scan | Einen Bereich im Index suchen und durchlaufen | `range` |
| Index scan | Indexeinträge durchlaufen, hier den gesamten Index | `index` |
| Index lookup | Einen konkreten Schlüssel im Index suchen | `ref`, `eq_ref` |

- Der Optimierer wählt den tatsächlichen Plan. Bei wenigen Zeilen kann ein
  Scan die beste Wahl sein.
- Ohne `ORDER BY` ist die Ergebnisreihenfolge nicht garantiert – auch mit Index.

### Demo-Daten laden

- `sql/tag11/02_demo_data.sql` wird bereitgestellt. Du musst den Generator nicht lesen.
- Er legt 10.000 Buchungen in der temporären Tabelle `perf_bookings` an.
  Echte Buchungen bleiben unverändert.

```text
SOURCE /work/sql/tag11/02_demo_data.sql;
```

```sql
SELECT COUNT(*) AS total FROM perf_bookings;
```

- Erwartet: `total = 10000`.

> **⚠️ Pitfall: MySQL-Verbindung zwischendurch schließen**
> Eine temporäre Tabelle gehört zur aktuellen Verbindung.
> Nach dem Schließen sind Tabelle und Demo-Index weg: `02_demo_data.sql` erneut ausführen.

### Ohne Datumsindex messen

```sql
-- Ergebnis-IDs notieren.
SELECT id, student_id, course_id, booking_date
FROM perf_bookings
WHERE booking_date = '1993-09-01' AND id > 0
ORDER BY id
LIMIT 20;

-- Nur der Plan.
EXPLAIN
SELECT id, student_id, course_id, booking_date
FROM perf_bookings
WHERE booking_date = '1993-09-01' AND id > 0
ORDER BY id
LIMIT 20;

-- Führt das SELECT aus und misst.
EXPLAIN ANALYZE
SELECT id, student_id, course_id, booking_date
FROM perf_bookings
WHERE booking_date = '1993-09-01' AND id > 0
ORDER BY id
LIMIT 20;

-- Zweiter Vergleich: alle Buchungen des Tages zählen.
EXPLAIN ANALYZE
SELECT COUNT(*)
FROM perf_bookings
WHERE booking_date = '1993-09-01';
```

| Plananzeige | Darauf achten |
| --- | --- |
| `possible_keys` / `key` | Mögliche Indizes / tatsächlich gewählter Index |
| `type` / `rows` / `Extra` | Zugriffsart, geschätzte Zeilen, zusätzliches Filtern |
| `actual time` / `rows` / `loops` | Gemessene Zeit, Zeilen und Durchläufe eines Knotens |
| `cost` | Geschätzter Aufwand in internen Einheiten – keine Millisekunden |

Beispiel aus dem Unterricht:

```text
-> Limit: 20 row(s)  (cost=1038 rows=20) (actual time=0.977..3.6 rows=20 loops=1)
    -> Filter: ((perf_bookings.booking_date = DATE'1993-09-01') and (perf_bookings.id > 0))  (cost=1038 rows=512) (actual time=0.913..3.53 rows=20 loops=1)
        -> Index range scan on perf_bookings using PRIMARY over (0 < id)  (cost=1038 rows=5123) (actual time=0.523..2.62 rows=7178 loops=1)
```

- Von unten lesen: IDs lesen → Datum prüfen → nach 20 Treffern stoppen.
- **7178 Zeilen gelesen für 20 Treffer.** Das ist unser Ansatzpunkt.
- `rows` vor `actual` ist geschätzt, `rows` hinter `actual` ist gemessen.
- Zeiten nicht addieren: Ein oberer Knoten enthält die Arbeit seiner Unterknoten.

### Index anlegen und erneut messen

```sql
CREATE INDEX ix_perf_date_id ON perf_bookings (booking_date, id);
SHOW INDEX FROM perf_bookings;
```

Danach dieselben Abfragen wie oben erneut ausführen.

| Beobachtung | Ohne Datumsindex | Mit Datumsindex |
| --- | --- | --- |
| Gewählter Index | `PRIMARY` | `ix_perf_date_id` |
| Vom Zugriffsknoten gelieferte Zeilen | 7178 | 20 |
| Geschätzte Kosten | 1038 | 33,4 |
| Ergebnis-IDs | gleich | gleich |
| `Extra` | `Using where` | `Using index condition` |

- Werte aus einem Unterrichtslauf. Deine Zahlen können abweichen.
- Der Index ist nach Datum, dann nach ID sortiert. Bei festem Datum liegen die
  IDs schon in der richtigen Reihenfolge.
- `student_id` und `course_id` stehen nicht im Index. MySQL liest sie aus der Tabelle nach.
- Ein einzelner Lauf kann trotzdem länger dauern. Belegt ist der gezieltere
  Zugriff, nicht automatisch ein Zeitgewinn.

Beim `COUNT(*)` zeigt sich der Gewinn deutlich:

| Vergleich | Ohne Index | Mit Index |
| --- | --- | --- |
| Zugriff | Table scan | Covering index lookup |
| Gelesene Zeilen | 10000 | 27 |
| Gemessene Zeit | 14,1 ms | 2,02 ms |
| Zählergebnis | 27 | 27 |

- **Covering (abdeckend):** Für `COUNT(*)` reicht der Index. Keine Tabellenzeile wird nachgeladen.
- Welche Spalten eine Abfrage braucht, bestimmt den Nutzen des Index.

> **⚠️ Pitfall: Using index condition mit Using index verwechseln**
> `Using index`: Alle benötigten Spalten liegen im Index.
> `Using index condition`: Nur die Bedingung wird im Index geprüft; Zeilen werden nachgelesen.

Zum Wiederholen: `DROP INDEX ix_perf_date_id ON perf_bookings;` und beide Messungen erneut ausführen.

## 2. Index migrieren

In `tag7/models.py` den Import ergänzen und nur `Booking` ersetzen:

```python
from sqlalchemy import Index


class Booking(Base):
    __tablename__ = "bookings"
    # Reihenfolge ist wichtig: zuerst Datum, innerhalb eines Datums die ID.
    __table_args__ = (
        Index("ix_bookings_date_id", "booking_date", "id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"))
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"))
    booking_date: Mapped[date] = mapped_column(Date)
    student: Mapped[Student] = relationship(back_populates="bookings")
    course: Mapped[Course] = relationship(back_populates="bookings")
```

```powershell
python -m alembic revision --autogenerate --rev-id 0005 -m "booking date index"
```

Erzeugte Datei `alembic/versions/0005_booking_date_index.py` prüfen – erwartet:

```python
def upgrade():
    op.create_index(
        "ix_bookings_date_id", "bookings", ["booking_date", "id"],
        unique=False,
    )


def downgrade():
    op.drop_index("ix_bookings_date_id", table_name="bookings")
```

```powershell
python -m alembic upgrade head
python -m alembic current
python -m alembic check
```

- Erwartet: Revision `0005`, keine offene Modelländerung.

> **⚠️ Pitfall: Autogenerate ungeprüft übernehmen**
> Die Revision darf nur den Index ergänzen.
> Gelöschte oder geänderte Tabellen zuerst klären, nicht migrieren.

Echten Bericht prüfen – Datei `sql/tag11/04_real_report.sql`:

```sql
SET @viewer_id = (SELECT id FROM users WHERE username = 'vector');

SHOW INDEX FROM bookings;

EXPLAIN ANALYZE
SELECT b.id, s.first_name, s.last_name, c.title, b.booking_date
FROM bookings AS b
JOIN course_managers AS cm ON cm.course_id = b.course_id
JOIN students AS s ON s.id = b.student_id
JOIN courses AS c ON c.id = b.course_id
WHERE cm.user_id = @viewer_id
  AND b.booking_date = '1993-09-01'
  AND b.id > 0
ORDER BY b.id
LIMIT 20;
```

```text
SOURCE /work/sql/tag11/04_real_report.sql;
```

- Bei wenigen echten Buchungen kann MySQL einen anderen Plan wählen.
- Indizes kosten Speicher und Schreibarbeit. Nur begründet anlegen.

## 3. Bericht als API anbieten

| Frage | Werkzeug | Maßnahme |
| --- | --- | --- |
| Wie schnell findet MySQL die Zeilen? | `EXPLAIN ANALYZE` | `Index(...)` + Migration |
| Wie viele Abfragen schickt Python? | `engine.echo`, SELECTs zählen | `joinedload(...)` |

### Abfrage passend zum Index

Datei `tag11/reports.py`:

```python
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from tag7.models import Booking
from tag10.models import CourseManager
from tag11.schemas import BookingReportRead


# Nur die Abfrage zusammenstellen; SQL wird erst in load_report ausgeführt.
def booking_statement(user_id, day, limit=20, after_id=0):
    return (
        select(Booking)
        .join(CourseManager, CourseManager.course_id == Booking.course_id)
        .where(
            CourseManager.user_id == user_id,  # Rechte vor LIMIT filtern.
            Booking.booking_date == day,  # Nur der gewählte Tag.
            Booking.id > after_id,  # Fortsetzung hinter der letzten ID.
        )
        .order_by(Booking.id)
        .limit(limit)
    )


def load_report(db, statement, eager=True):
    # eager=False: Beziehungen beim Zugriff nachladen.
    # eager=True: Schüler und Kurs schon im ersten SELECT mitladen.
    if eager:
        statement = statement.options(
            joinedload(Booking.student),
            joinedload(Booking.course),
        )
    rows = []
    for booking in db.scalars(statement):
        # Ohne eager loading können diese Zugriffe weitere SELECTs auslösen.
        student = booking.student
        rows.append(BookingReportRead(
            id=booking.id,
            student_name=f"{student.first_name} {student.last_name}",
            course_title=booking.course.title,
            booking_date=booking.booking_date,
        ))
    return rows
```

Datei `tag11/schemas.py`:

```python
from datetime import date

from pydantic import BaseModel


class BookingReportRead(BaseModel):
    id: int
    student_name: str
    course_title: str
    booking_date: date
```

### Das N+1-Problem

- SQLAlchemy lädt Beziehungen standardmäßig erst beim Zugriff (*lazy loading*).
- `booking.student` sieht aus wie ein Attribut, **kann aber ein eigenes SELECT auslösen.**
- Bei N Buchungen: 1 SELECT für die Liste plus bis zu N weitere je Beziehung.

```text
SELECT ... FROM bookings ... LIMIT 20      -- 1 Abfrage für die Liste
SELECT ... FROM students WHERE id = 7      -- Schüler der 1. Buchung
SELECT ... FROM courses  WHERE id = 3      -- Kurs der 1. Buchung
SELECT ... FROM students WHERE id = 12     -- Schüler der 2. Buchung
...                                        -- bis zu 1 + 20 + 20 = 41 SELECTs
```

- `joinedload` hängt Schüler und Kurs per JOIN an: **ein SELECT** für alles.
- Ein Index hilft hier nicht: Jede Abfrage ist schnell, aber es sind zu viele.

> **⚠️ Pitfall: JOIN für Rechte und joinedload verwechseln**
> Der JOIN auf `CourseManager` filtert, welche Buchungen erlaubt sind.
> `joinedload` lädt nur Antwortdaten zu den bereits erlaubten Buchungen.

### Route anschließen

Datei `tag11/routers/reports.py`:

```python
from datetime import date

from fastapi import APIRouter

from tag9.dependencies import DbSession
from tag10.pagination import AfterId, Limit
from tag10.permissions import StaffUser
from tag11.reports import booking_statement, load_report
from tag11.schemas import BookingReportRead

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/bookings", response_model=list[BookingReportRead])
def read_booking_report(
    booking_date: date,
    db: DbSession,
    user: StaffUser,
    limit: Limit = 20,
    after_id: AfterId = 0,
):
    statement = booking_statement(user.id, booking_date, limit, after_id)
    return load_report(db, statement)
```

Datei `tag11/main.py`:

```python
import os

from tag10.main import create_app as create_previous_app
from tag11.routers import reports


def create_app(show_docs=False):
    # Geschützte Routen und Fehlerhandler aus Tag 10 weiterverwenden.
    app = create_previous_app(show_docs=show_docs)
    app.version = "0.7.0"
    app.include_router(reports.router)
    return app


app = create_app(show_docs=os.environ.get("API_DOCS", "0") == "1")
```

- `/reports/bookings` verlangt `staff` und liefert nur Buchungen zugeordneter Kurse.
- `booking_date` ist Pflicht; `limit` und `after_id` stammen aus Tag 10.

## 4. Nachladen sichtbar machen

```powershell
Copy-Item .\tests\tag10\conftest.py .\tests\tag11\conftest.py
Copy-Item .\tests\tag10\test_objects.py .\tests\tag11\test_objects.py
Copy-Item .\tests\tag10\test_limits.py .\tests\tag11\test_limits.py
```

| Datei | Änderung |
| --- | --- |
| `tests/tag11/conftest.py` | `from tag10.main import create_app` → `from tag11.main import create_app`; Revision `0004` → `0005` |
| `tests/tag11/test_limits.py` | App-Import auf `tag11.main` ändern |

- Ohne neuen App-Import liefert `/reports/bookings` im Test `404`.

Am Ende von `tests/tag11/conftest.py` ergänzen (`from datetime import date` oben bei den Importen):

```python
@pytest.fixture
def report_seed(db_factory, seed):
    day = date(1993, 9, 1)
    with db_factory.begin() as db:
        nora = Student(first_name="Nora", last_name="Winter",
                       house="Ravenclaw", school_year=3)
        elias = Student(first_name="Elias", last_name="Brook",
                        house="Hufflepuff", school_year=3)
        db.add_all([nora, elias])
        db.flush()
        # Eigene IDs sind durch eine fremde Buchung unterbrochen.
        bookings = [
            Booking(student_id=seed["harry_id"],
                    course_id=seed["own_id"], booking_date=day),
            Booking(student_id=seed["harry_id"],
                    course_id=seed["other_id"], booking_date=day),
            Booking(student_id=nora.id, course_id=seed["own_id"],
                    booking_date=day),
            Booking(student_id=elias.id, course_id=seed["own_id"],
                    booking_date=day),
            Booking(student_id=seed["harry_id"],
                    course_id=seed["own_id"], booking_date=date(1993, 9, 2)),
        ]
        db.add_all(bookings)
        db.flush()
        return {
            "day": day,
            "own_ids": [bookings[i].id for i in (0, 2, 3)],
            "foreign_id": bookings[1].id,
        }
```

Datei `tests/tag11/test_report.py`:

```python
import pytest

from tag11.reports import booking_statement, load_report


def test_report_keeps_permissions(api_client, login_as, report_seed):
    response = api_client.get("/reports/bookings", params={
        "booking_date": str(report_seed["day"]),
    }, headers=login_as("vector"))
    assert response.status_code == 200
    assert [row["id"] for row in response.json()] == report_seed["own_ids"]
    assert response.json()[0]["student_name"] == "Harry Potter"


# ids legt fest, wie pytest die beiden Durchläufe in der Ausgabe nennt.
@pytest.mark.parametrize("eager", [False, True], ids=["nachladen", "mitladen"])
def test_loading_keeps_result(db_factory, accounts, report_seed, eager):
    statement = booking_statement(accounts["vector"].id, report_seed["day"])
    with db_factory() as db:
        # Nur für die lokale Demo SQL anzeigen; Parameter bleiben verborgen.
        engine = db.get_bind()
        engine.hide_parameters = True
        engine.echo = True
        try:
            rows = load_report(db, statement, eager=eager)
        finally:
            engine.echo = False
    # Beide Strategien müssen denselben erlaubten Bericht ergeben.
    assert [row.id for row in rows] == report_seed["own_ids"]
    assert [row.student_name for row in rows] == [
        "Harry Potter", "Nora Winter", "Elias Brook",
    ]
```

```powershell
$testCompose = @("--env-file", ".env.test", "-f", "compose.test.yaml")
docker compose @testCompose up -d --wait test_db
python -m tag8.init_test_db
python -m pytest .\tests\tag11 -q
python -m pytest .\tests\tag11\test_report.py::test_loading_keeps_result -v -s
```

- `-s` zeigt die SQL-Ausgabe, `-v` die Namen `[nachladen]` und `[mitladen]`.
- Erwartet beim Nachladen: ein Buchungs-SELECT, drei Schüler-SELECTs, ein Kurs-SELECT.
- Erwartet beim Mitladen: ein SELECT.
- Erwartet: 11 Tests bestanden.

> **⚠️ Pitfall: Zeiten mit SQL-Ausgabe vergleichen**
> Die Konsolenausgabe kostet selbst Zeit, und drei Buchungen sind zu wenig.
> SQL beobachten und Laufzeit messen sind getrennte Durchläufe.

### Rückblick auf Tag 7: Abfrage in der Schleife

Ausschnitt aus `tag7/routers/bookings.py`:

```python
for student_id in data.student_ids:
    if db.get(Student, student_id) is None:
        raise HTTPException(404, "Schüler nicht gefunden.")
```

- Wie viele SELECTs entstehen für 20 vorhandene, noch nicht geladene Schüler?
- Wie lassen sich alle Schüler mit einer gemeinsamen Abfrage prüfen?

Mögliche Lösung – eine Abfrage für alle IDs:

```python
from sqlalchemy import func, select

wanted_ids = set(data.student_ids)  # Doppelte IDs nur einmal zählen.
found_count = db.scalar(
    select(func.count(Student.id)).where(Student.id.in_(wanted_ids))
)
if found_count != len(wanted_ids):
    raise HTTPException(404, "Schüler nicht gefunden.")
```

- Auch ein ausdrücklicher DB-Aufruf in einer Schleife erzeugt ein N+1-artiges Muster.

## 5. Bericht mit Postman prüfen

```powershell
$env:API_DOCS = "1"
python -m uvicorn tag11.main:app --host 127.0.0.1 --port 8000
```

- Collection `docs/postman/11-Tag11-Hogwarts.postman_collection.json` importieren.
- Lokale Passwörter und einen vorhandenen Berichtstag eintragen.
- Im Runner Ordner 00 → 01 → 02 → 03.

| Fall | Erwartet |
| --- | --- |
| Vector, Berichtstag | 200 mit eigenen Buchungen |
| Zweite Seite mit `after_id` | Nächste Buchungen folgen |
| Tag ohne eigene Buchungen | 200 mit `[]` |
| Ohne Token / reader | 401 / 403 |
| Ungültiges Datum oder `limit=51` | 422 |

- Passwörter und Token danach aus Postman entfernen.



## Das solltest du erklären können

1. Warum kann MySQL mit einem Index einen Bereich überspringen?
2. Warum hilft derselbe Index beim `COUNT(*)` stärker als beim Bericht?
3. Was ist das N+1-Problem, und warum hilft dagegen kein Index?
4. Warum ersetzt `joinedload` nicht den JOIN auf `CourseManager`?
