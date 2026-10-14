# SQLAlchemy und Hogwarts – Teilnehmerskript

Tag 3 des Kurses „Programmierung mit Python für komplexe Datenbanken“.

- Die Abschnitte folgen der Reihenfolge des Unterrichts.
- Jeder vollständige Codeblock nennt seine Datei und den passenden Aufruf.
- Ausgangspunkt ist der fertige Live-Bestand aus [Tag 2][tag2].
- Wir verwenden weiterhin pip und die vorhandene virtuelle Umgebung.

## Ziel des Tages

- Eine kurze Core-Abfrage mit gebundenen Parametern entwickeln.
- Vorhandene Tabellen mit ORM-Modellen beschreiben.
- Kurse und Schüler über SQLAlchemy lesen und filtern.
- Ein Kursangebot anlegen, lesen, ändern und wieder entfernen.
- flush, commit und rollback unterscheiden.
- Schüler und Buchung in derselben Transaktion speichern.
- Fremdschlüssel und Objektbeziehungen unterscheiden.

Heute erhält die Hogwarts-Verwaltung Programme mit SQLAlchemy.
Du verwendest dieselbe MySQL-Datenbank wie an Tag 2.
Die bisherigen Programme bleiben als Vergleich erhalten.
Neue Python-Dateien liegen im Ordner tag3.
FastAPI und die HTTP-Schnittstelle folgen an späteren Tagen.

## SQLAlchemy auf einen Blick

| Du möchtest … | Aufruf oder Beschreibung | Abschnitt |
|---|---|---|
| den Datenbankzugriff vorbereiten | create_engine(url) | 1 |
| eine Verbindung ausleihen | engine.connect() | 2–3 |
| SQL-Text ausführen | text und execute | 2 |
| eine vorhandene Tabelle beschreiben | Table und MetaData | 3 |
| eine Abfrage aufbauen | select, where und order_by | 3–5 |
| einen Parameter benennen | bindparam | 3 |
| Tabellen auf Klassen abbilden | DeclarativeBase und mapped_column | 4–5 |
| eine Session erzeugen | SessionLocal() | 4–6 |
| über den Primärschlüssel suchen | session.get(Model, id) | 4–5 |
| Modellobjekte lesen | session.scalars(select(Model)) | 5 |
| ein neues Objekt vormerken | session.add(objekt) | 7–8 |
| Änderungen an MySQL senden | session.flush() | 6–8 |
| offene Änderungen verwerfen | session.rollback() | 6 |
| eine Arbeitseinheit bestätigen | erfolgreiches SessionLocal.begin() | 7–8 |
| eine Zeile zur Löschung vormerken | session.delete(objekt) | 7 |
| verwandte Objekte lesen | relationship und back_populates | 10 |
| Nachladeabfragen bündeln | selectinload | 11 |

## 0. Von Connector-Abfragen zu SQLAlchemy

Die Verwaltung braucht weiterhin Kurslisten und sichere Namenssuchen.
Eine Anmeldung soll Schüler und Buchung gemeinsam speichern.
Neu ist die Art, wie wir den Zugriff in Python beschreiben.

- Tag 2: Python → Connector → MySQL.
- Tag 3: Python → SQLAlchemy → Connector → MySQL.
- MySQL führt weiterhin SQL aus.
- SQLAlchemy ersetzt hier weder den Server noch die Datenbankregeln.
- Core arbeitet mit SQL-Ausdrücken und Ergebniszeilen.
- ORM verbindet Tabellenzeilen mit Python-Objekten.
- Auch eine ORM-Abfrage wird als SQL an MySQL gesendet.

![Client, Server und Volume](../assets/02-docker-aufbau.svg)

| Bestand am Anfang | Erwartete Daten |
|---|---|
| students | Neun Schüler |
| courses | Vier Kurse mit IDs 1–4 |
| bookings | Acht Buchungen |
| Anmeldung aus Tag 2 | Nora Winter mit einer Buchung für Kurs 1 |
| Datenbankregeln | Schuljahrprüfung und beide Fremdschlüssel |
| Speicher-Engine | InnoDB für alle drei Tabellen |

### Projekt und MySQL-Client öffnen

In PowerShell:

```powershell
Set-Location "$env:USERPROFILE\hogwarts-sql"
git status --short
docker compose up -d --wait
docker compose ps
New-Item -ItemType Directory -Force -Path .\tag3
New-Item -ItemType Directory -Force -Path .\sql\tag3
docker compose exec db mysql --user=dumbledore --password hogwarts
```


Das Passwort aus deiner vorhandenen .env eingeben.
Lass dieses Terminal für den MySQL-Client geöffnet.
Öffne eine zweite PowerShell für Python und Git im selben Projektordner.

| Eingabestelle | Erkennbar an | Hier gibst du ein |
|---|---|---|
| PowerShell | PS C:\…> | Python, pip, Docker und Git |
| MySQL-Client | mysql> | SQL und SOURCE |

### Ausgangsbestand kontrollieren

Datei `sql\tag3\01_start_check.sql`:

<!-- file: sql/tag3/01_start_check.sql -->
```sql
USE hogwarts;

SELECT 'students' AS table_name, COUNT(*) AS row_count FROM students
UNION ALL
SELECT 'courses', COUNT(*) FROM courses
UNION ALL
SELECT 'bookings', COUNT(*) FROM bookings;

SHOW CREATE TABLE students;
SHOW CREATE TABLE courses;
SHOW CREATE TABLE bookings;

SELECT s.id, s.first_name, s.last_name, b.course_id, b.booking_date
FROM students AS s
JOIN bookings AS b ON b.student_id = s.id
WHERE s.first_name = 'Nora' AND s.last_name = 'Winter';

SELECT id FROM courses WHERE id = 999;
```

Laden: `SOURCE /work/sql/tag3/01_start_check.sql;`

<details>
<summary>Erwartung</summary>

Neun Schüler, vier Kurse und acht Buchungen.
Nora hat eine Buchung für Kurs 1 am 4. September 1993.
Kurs 999 fehlt. Diese ID dient später als Fehlerfall.
SHOW CREATE TABLE zeigt InnoDB, den CHECK und die Fremdschlüssel.

</details>


> **⚠️ Pitfall: Den Bestand erneut importieren**
> Lade die INSERT-Dateien aus Tag 1 nicht erneut.
> Fehlt Nora, hole die erfolgreiche Anmeldung aus Tag 2 gezielt nach.
> Bei zusätzlichen Zeilen prüfe zuerst deren Herkunft.
> Setze weder Tabellen noch das Daten-Volume pauschal zurück.

## 1. Den Python-Arbeitsplatz erweitern

### 1.1 Lokaler Zugriff und Containerzugriff

| Wo läuft Python? | Host | Port |
|---|---|---|
| Lokal unter Windows | 127.0.0.1 | 3307 |
| Später im Compose-Netz | db | 3306 |

- Behalte deinen tatsächlich veröffentlichten Port aus Tag 1 bei.
- Die Zugangsdaten stammen weiterhin aus der lokalen .env.
- Wir verwenden den Kursbenutzer dumbledore.
- Die Programme aus Tag 2 werden nicht überschrieben.

> **⚠️ Pitfall: db als Host im lokalen Python-Programm**
> db ist der Dienstname innerhalb des Compose-Netzes.
> Unser lokales Python verwendet 127.0.0.1 und den veröffentlichten Port.

### 1.2 Vorhandene Umgebung und Pakete

In der zweiten PowerShell:

```powershell
Set-Location "$env:USERPROFILE\hogwarts-sql"
.\.venv\Scripts\Activate.ps1
python -c "import sys; print(sys.executable)"
python --version
```


- Der Interpreterpfad muss auf .venv\Scripts\python.exe zeigen.
- Du brauchst keine neue Umgebung für diesen Kurstag.
- requirements-tag2.txt bleibt erhalten und wird eingebunden.

Datei `requirements-tag3.txt`:

<!-- file: requirements-tag3.txt -->
```text
-r requirements-tag2.txt
SQLAlchemy==2.0.54
```

```powershell
python -m pip install -r requirements-tag3.txt
python -m pip check
python -m pip show SQLAlchemy mysql-connector-python python-dotenv
```


- Der Unterrichtsstand verwendet SQLAlchemy 2.0.54.
- Connector 9.7.0 und python-dotenv 1.2.1 stammen aus Tag 2.
- Für die gezeigten Zugriffe verwenden wir denselben Connector weiter.

> **💡 Merke: Ein Python-Projekt, eine Umgebung**
> python -m pip installiert die Pakete für den gestarteten Interpreter.
> Das gilt auch für Programme, die wir später mit FastAPI verbinden.

> **⚠️ Pitfall: Aktivierung blockiert**
> Nutze dann .\.venv\Scripts\python.exe direkt statt python.
> Eine Änderung der PowerShell-Ausführungsrichtlinie ist nicht nötig.
> Installiere die Pakete nicht versehentlich in ein anderes Python.

Ohne Aktivierung funktioniert zum Beispiel:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-tag3.txt
```


### 1.3 Die vorhandene Konfiguration verwenden

- MYSQL_HOST: 127.0.0.1. MYSQL_PORT: dein vorhandener lokaler Port.
- MYSQL_USER: dumbledore. MYSQL_DATABASE: hogwarts.
- MYSQL_PASSWORD enthält dein bereits eingerichtetes Passwort.
- Die lokale .env bleibt aus Git ausgeschlossen.
- .env.example enthält weiterhin nur Platzhalter.
- Ersetze die lokale .env nicht durch eine neue Beispieldatei.

### 1.4 Engine und Session-Fabrik bereitstellen

Diese Datei lädt die Konfiguration und bereitet den Datenbankzugriff vor.
Die Session verwenden wir nach dem ersten Modell.

Datei `tag3\db.py`:

<!-- file: tag3/db.py -->
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


- __file__ bezeichnet die Datei db.py.
- parent.parent führt von tag3 zum Projektordner mit der .env.
- URL.create nimmt Benutzer, Passwort, Host und Port einzeln entgegen.
- Sonderzeichen im Passwort müssen nicht von Hand kodiert werden.
- mysql+mysqlconnector nennt Datenbank und verwendeten Treiber.
- create_engine bereitet Zugriff und Verbindungspool vor.
- Erst ein tatsächlicher Datenbankzugriff fordert eine Verbindung an.
- pool_pre_ping prüft eine ausgeliehene Verbindung vor ihrer Nutzung.
- connection_timeout begrenzt das Warten beim Verbindungsaufbau.
- SessionLocal ist eine Fabrik für neue Sessions.

> **💡 Merke: Engine, Connection und Session**
> Die Engine organisiert den Zugang und den Verbindungspool.
> Eine Connection ist eine ausgeliehene Datenbankverbindung.
> Eine Session verwaltet ORM-Objekte und Änderungen für eine Arbeitseinheit.

> **⚠️ Pitfall: Eine Session für alle Vorgänge**
> SessionLocal ist keine globale Session.
> Erzeuge für jeden unabhängigen Vorgang eine neue Session.
> Teile eine Session nicht zwischen unabhängig arbeitenden Programmen.

## 2. Verbindung und Ergebnis unterscheiden

Die Verwaltung möchte Datenbankname und angemeldeten Benutzer sehen.

Datei `tag3\core_connection.py`:

<!-- file: tag3/core_connection.py -->
```python
from sqlalchemy import text

from db import engine


statement = text(
    "SELECT DATABASE() AS db_name, CURRENT_USER() AS db_user"
)
with engine.connect() as connection:
    row = connection.execute(statement).mappings().one()
    print(row["db_name"], row["db_user"])
```

```powershell
python .\tag3\core_connection.py
```

<details>
<summary>Erwartung</summary>

Die Datenbank ist hogwarts.
Der Benutzer beginnt mit dumbledore; der Hostteil kann abweichen.
Ein Cursor wird hier nicht von Hand geöffnet.

</details>


| Bestandteil | Aufgabe |
|---|---|
| text | SQL-Text als ausführbare SQLAlchemy-Anweisung kennzeichnen |
| engine.connect | Eine Connection ausleihen |
| execute | Die Anweisung ausführen |
| mappings | Ergebniszeilen über Spaltennamen zugänglich machen |
| one | Genau eine Zeile verlangen |

- row["db_name"] liest den Wert unter dem vereinbarten Spaltennamen.
- one meldet einen Fehler, wenn keine oder mehrere Zeilen vorhanden sind.
- Das Ergebnis wird innerhalb des offenen Connection-Blocks gelesen.
- Das Blockende gibt die Connection an die Engine zurück.

> **💡 Merke: Auch Lesen hat eine Transaktionsgrenze**
> Die erste Abfrage beginnt hier eine Lesetransaktion.
> Beim Schließen wird diese offene Transaktion zurückgerollt.
> Ein ROLLBACK im SQL-Log nach einer reinen Abfrage ist kein Fehler.

> **⚠️ Pitfall: Ein SQL-String allein reicht nicht**
> Verwende text für SQL-Text, den du an execute übergibst.
> Eine vorbereitete statement-Variable wird erst durch execute ausgeführt.

### Einen Zwischenstand sichern

```powershell
git add -- requirements-tag3.txt tag3/db.py tag3/core_connection.py
git add -- sql/tag3/01_start_check.sql
git diff --cached --check
git diff --cached
git commit -m "SQLAlchemy mit vorhandener MySQL-Datenbank verbinden"
```


## 3. Einen Kurs mit Core auswählen

Die Verwaltung fragt nach Alte Runen.
Du beschreibst die bestehende Tabelle und baust eine passende SELECT-Abfrage.

Datei `tag3\core_catalog.py`:

<!-- file: tag3/core_catalog.py -->
```python
from sqlalchemy import Column, Integer, MetaData, String, Table
from sqlalchemy import bindparam, select

from db import engine


# Sammelstelle für Tabellendefinitionen: Jede Table mit diesen
# metadata wird hier registriert (z. B. metadata.tables["courses"]).
# Gemeinsames MetaData löst auch ForeignKey("courses.id") auf,
# daher müssen verknüpfte Tabellen in denselben metadata stehen.
metadata = MetaData()
courses = Table(
    "courses",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String(100), nullable=False),
)
statement = (
    select(courses.c.id, courses.c.title)
    .where(courses.c.title == bindparam("wanted_title"))
    .order_by(courses.c.id)
)
with engine.connect() as connection:
    rows = connection.execute(
        statement, {"wanted_title": "Alte Runen"}
    ).all()
    for course_id, title in rows:
        print(course_id, title)
```

```powershell
python .\tag3\core_catalog.py
```

<details>
<summary>Erwartung</summary>

```text
3 Alte Runen
```

Mit wanted_title=Wahrsagen erscheint Kurs 2.
Ein unbekannter Titel liefert keine Zeile.

</details>


- MetaData sammelt Tabellenbeschreibungen in Python.
- Table beschreibt hier die vorhandene Tabelle courses.
- courses.c.id und courses.c.title beschreiben ihre Spalten.
- select wählt Spalten aus. where ergänzt die Bedingung.
- order_by legt die Ergebnisreihenfolge fest.
- bindparam benennt den Eingabeparameter wanted_title.
- execute erhält den Parameterwert in einem separaten Dictionary.
- all liest die Ergebniszeilen als Liste.
- Die Schleife verteilt jede Zeile auf course_id und title.

> **💡 Merke: Eine Tabellenbeschreibung verändert keine Tabelle**
> Table und MetaData beschreiben das Schema zunächst nur in Python.
> Wir rufen kein create_all auf. Die MySQL-Tabellen sind schon vorhanden.

> **⚠️ Pitfall: Parameternamen passen nicht zusammen**
> wanted_title muss in bindparam und im Parameter-Dictionary gleich heißen.
> Setze den Suchwert nicht mit einem f-String in SQL ein.

### Kleine Übertragung

1. Ändere den Filter in einer Probe auf die Kurs-ID.
2. Verwende den benannten Parameter wanted_id.
3. Prüfe ID 3 und danach ID 999.
4. Erkläre vor der Ausführung, welche SQL-Bedingung entsteht.
5. Stelle den Live-Code anschließend wieder auf den Titelfilter zurück.

- ID 3 liefert Alte Runen. ID 999 liefert keine Zeile.
- [Aufgabe 2][a2] festigt dieses Muster mit dem Übungsbestand.

## 4. Einen Kurs als ORM-Objekt laden

Die Verwaltung möchte einen Kurs als Python-Objekt verwenden.
Zuerst brauchen wir nur die Klasse Course und eine gemeinsame Modellbasis.

### 4.1 Das kleinste Modell

Datei `tag3\models.py`:

<!-- file: tag3/models.py -->
```python
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# Eigene Basisklasse = gemeinsamer Katalog aller Modelle:
# Base.metadata sammelt alle Tabellen (wie MetaData() im Core),
# damit ForeignKeys aufgelöst werden und create_all alles anlegt.
# Modelle nie direkt von DeclarativeBase erben lassen (Fehler).
class Base(DeclarativeBase):
    pass


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
```


- Base ist die gemeinsame Basis der ORM-Modellklassen.
- __tablename__ nennt die bereits vorhandene Tabelle.
- Mapped[int] und Mapped[str] beschreiben Python-Attributtypen.
- mapped_column beschreibt die zugehörige Datenbankspalte.
- String(100) passt zum vorhandenen VARCHAR(100).
- Course ist die Klasse. Ein course ist ein konkretes Objekt dieser Klasse.
- Die Modelldefinition erzeugt hier keine neue Datenbanktabelle.

### 4.2 Das Objekt mit einer Session lesen

Datei `tag3\orm_first_course.py`:

<!-- file: tag3/orm_first_course.py -->
```python
from db import SessionLocal, engine
from models import Course


engine.echo = True
try:
    with SessionLocal() as session:
        course = session.get(Course, 3)
        if course is None:
            print("Nicht gefunden")
        else:
            print(course.id, course.title)
finally:
    engine.echo = False
```

```powershell
python .\tag3\orm_first_course.py
```

<details>
<summary>Erwartung</summary>

Die fachliche Ausgabe lautet 3 Alte Runen.
Im Log erscheint ein SELECT auf courses mit einer Primärschlüsselbedingung.
Daneben können Initialisierungsabfragen des MySQL-Dialekts erscheinen.
ROLLBACK beim Schließen beendet die offene Lesetransaktion.

</details>


- SessionLocal() erzeugt eine neue Session.
- session.get(Course, 3) sucht nach dem Primärschlüssel.
- Bei einem Treffer erhältst du ein Course-Objekt.
- Bei einer fehlenden ID erhältst du None.
- course.id und course.title lesen die Attribute des Objekts.
- engine.echo zeigt ausgeführtes SQL und Parameterwerte.
- finally setzt die Log-Einstellung auch bei einem Fehler zurück.
- Der with-Block schließt die Session; Lesen benötigt keinen COMMIT.

> **⚠️ Pitfall: Attribute eines fehlenden Objekts lesen**
> None hat kein title-Attribut.
> Prüfe den Rückgabewert von get vor dem Attributzugriff.

### Kleine Übertragung

1. Lies nacheinander die IDs 2 und 999.
2. Gib jeweils den Titel oder Nicht gefunden aus.
3. Zeige die Prüfung, die einen Zugriff auf None.title verhindert.
4. Stelle den Live-Code anschließend wieder auf ID 3 zurück.

- ID 2 liefert Wahrsagen. ID 999 liefert Nicht gefunden.

### Den ersten ORM-Stand sichern

```powershell
git add -- tag3/core_catalog.py tag3/models.py tag3/orm_first_course.py
git diff --cached --check
git diff --cached
git commit -m "Einen Kurs mit kleinem ORM-Modell laden"
```


## 5. Mit einer Session lesen und sicher suchen

Jetzt braucht die Verwaltung auch Schüler und Buchungen.
Wir ergänzen ihre Tabellenabbildungen zunächst ohne Objektbeziehungen.

### 5.1 Die weiteren Modelle ergänzen

Ersetze models.py durch diesen vollständigen Zwischenstand.
Base und Course bleiben darin enthalten.

Datei `tag3\models.py`:

<!-- file: tag3/models.py -->
```python
from datetime import date

from sqlalchemy import CheckConstraint, Date, ForeignKey, String
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


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


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"))
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"))
    booking_date: Mapped[date] = mapped_column(Date)
```


| Beschreibung | Bedeutung |
|---|---|
| Mapped[str] | Python-Attribut für Text; hier kein NULL |
| Mapped[str \| None] | Python-Attribut für Text oder None |
| String(50) | SQL-Zeichenkette mit höchstens 50 Zeichen |
| TINYINT | Vorhandener MySQL-Zahlentyp für school_year |
| Date | SQL-Datum; Python verwendet datetime.date |
| ForeignKey("students.id") | Verweis auf die vorhandene Schülertabelle |
| CheckConstraint | Beschreibung der vorhandenen Schuljahrregel |

- Ohne ausdrückliches nullable leitet SQLAlchemy es hier aus Mapped ab.
- house darf None enthalten. Die anderen Fachfelder sind erforderlich.
- Der Primärschlüssel erlaubt trotzdem kein NULL in der Datenbank.
- Die Länge und die Fremdschlüssel passen zum vorhandenen Schema.
- Das Eintragen von CheckConstraint ändert keine bestehende Tabelle.
- Die Datenbankregel ist schon seit Tag 1 vorhanden.

> **⚠️ Pitfall: Modelldeklaration als Eingabeprüfung verstehen**
> Mapped allein prüft beliebige Benutzereingaben nicht zur Laufzeit.
> String(100) kürzt einen Python-String nicht automatisch.
> MySQL setzt seine tatsächlichen Constraints beim Schreiben durch.
> Eine Änderung des vorhandenen Schemas braucht später eine Migration.

### 5.2 Den Kurskatalog ausgeben

Datei `tag3\orm_catalog.py`:

<!-- file: tag3/orm_catalog.py -->
```python
from sqlalchemy import select

from db import SessionLocal
from models import Course


with SessionLocal() as session:
    statement = select(Course).order_by(Course.id)
    for course in session.scalars(statement):
        # scalar: wert statt row[0] (liste)
        print(course.id, course.title)

    course = session.get(Course, 3)
    print("Einzelabruf:", course.title if course else "Nicht gefunden")
    print("Fehlender Kurs:", session.get(Course, 999))
```

```powershell
python .\tag3\orm_catalog.py
```

<details>
<summary>Erwartung</summary>

```text
1 Arithmantik
2 Wahrsagen
3 Alte Runen
4 Pflege magischer Geschöpfe
Einzelabruf: Alte Runen
Fehlender Kurs: None
```


</details>


- select(Course) wählt hier ganze ORM-Objekte aus.
- session.scalars liefert die Course-Objekte direkt.
- session.execute würde Zeilen liefern, die das Objekt enthalten.
- Die Attribute werden gelesen, während die Session offen ist.
- Die Identity Map verwaltet geladene Objekte nach ihrem Primärschlüssel.
- Ein erneutes get kann dasselbe schon geladene Objekt liefern.
- Das ist kein allgemeiner Cache für beliebige Abfragen.

### 5.3 Eine sichere Namenssuche schreiben

Datei `tag3\student_search.py`:

<!-- file: tag3/student_search.py -->
```python
from sqlalchemy import select

from db import SessionLocal
from models import Student


def find_students(last_name: str) -> list[tuple[int, str, str]]:
    statement = (
        select(Student.id, Student.first_name, Student.last_name)
        .where(Student.last_name == last_name)
        .order_by(Student.id)
    )
    with SessionLocal() as session:
        return [tuple(row) for row in session.execute(statement)]


if __name__ == "__main__":
    for last_name in ("Weasley", "O'Neil", "' OR 1=1 --"):
        print(last_name, find_students(last_name))
```

```powershell
python .\tag3\student_search.py
```

<details>
<summary>Erwartung</summary>

Weasley liefert Ron mit ID 3 und Ginny mit ID 7.
O'Neil liefert eine leere Liste. Das Apostroph erzeugt keinen SQL-Fehler.
Auch der SQL-artige Text liefert eine leere Liste.
Die WHERE-Bedingung wird dadurch nicht aufgehoben.

</details>


- Der Vergleich Student.last_name == last_name bindet den Eingabewert.
- Du baust keine Quotes und keinen SQL-String aus diesem Wert zusammen.
- Hier wählt select drei Spalten und keine vollständigen Objekte aus.
- execute liefert deshalb passende Ergebniszeilen.
- tuple(row) wandelt die Zeile in einfache Rückgabedaten um.
- Die Funktion gibt die fertig gelesene Liste nach dem Session-Block zurück.

> **💡 Merke: scalars hängt von deiner Auswahl ab**
> Bei select(Course) enthält die erste Ergebnisspalte ein Course-Objekt.
> Bei select(Student.id, Student.first_name) wäre es nur die ID.
> Verwende execute, wenn du alle ausgewählten Spalten brauchst.

> **⚠️ Pitfall: Nach dem Schließen neue Daten nachladen**
> Bereits geladene Attribute können danach noch lesbar sein.
> Nicht geladene oder abgelaufene Attribute benötigen eine aktive Session.
> Unsere Operationsfunktionen geben deshalb IDs und einfache Daten zurück.

- [Aufgabe 3][a3] überträgt die Suche auf Haus und fehlendes Haus.
- [Aufgabe 4][a4] behandelt ausdrücklich eine fehlende Kurs-ID.

### Den Abfragestand sichern

```powershell
git add -- tag3/models.py tag3/orm_catalog.py tag3/student_search.py
git diff --cached --check
git diff --cached
git commit -m "Hogwarts-Tabellen mit ORM lesen und sicher filtern"
```


## 6. Eine Änderung zur Probe ausführen

Die Verwaltung möchte einen Kurstitel ausprobieren und anschließend verwerfen.

Datei `tag3\rollback_probe.py`:

<!-- file: tag3/rollback_probe.py -->
```python
from db import SessionLocal, engine
from models import Course


engine.echo = True
try:
    with SessionLocal() as session: # kein autocommit
        course = session.get(Course, 2)
        if course is None:
            raise ValueError("Kurs 2 fehlt im Ausgangsbestand.")
        course.title = "Wahrsagen - Probe"
        session.flush()
        print("In der Transaktion:", course.title)
        session.rollback()

    with SessionLocal() as session:
        course = session.get(Course, 2)
        if course is None:
            raise ValueError("Kurs 2 fehlt nach der Probe.")
        print("Nach Rollback:", course.title)
finally:
    engine.echo = False
```

```powershell
python .\tag3\rollback_probe.py
```

<details>
<summary>Erwartung</summary>

```text
In der Transaktion: Wahrsagen - Probe
Nach Rollback: Wahrsagen
```


</details>


- Die Zuweisung an course.title merkt eine Änderung in der Session vor.
- flush sendet das UPDATE in die laufende MySQL-Transaktion.
- Der geänderte Wert ist dadurch noch nicht dauerhaft bestätigt.
- rollback nimmt die offene Änderung zurück.
- Die neue Session liest wieder den ursprünglichen Kurstitel.
- Im SQL-Log kannst du UPDATE, ROLLBACK und die neue Abfrage erkennen.

| Schritt | Wirkung |
|---|---|
| Attribut ändern | Änderung am verwalteten Objekt vormerken |
| flush | Änderungen an MySQL senden |
| commit | Transaktion bestätigen; führt vorher bei Bedarf flush aus |
| rollback | Offene Transaktion zurücknehmen |
| Session schließen | Ressourcen freigeben; kein automatischer COMMIT |

> **💡 Merke: flush ist kein commit**
> Ein erfolgreicher flush sagt nicht, dass die Änderung dauerhaft bleibt.
> Die gesamte Transaktion kann anschließend noch zurückgerollt werden.

> **⚠️ Pitfall: ROLLBACK nach COMMIT**
> ROLLBACK kann eine bereits bestätigte Änderung nicht zurücknehmen.
> Eine spätere Korrektur ist ein neuer Schreibvorgang.

- [Aufgabe 6][a6] überträgt die Probe auf das Haus eines Schülers.
- Autoflush vor ORM-Abfragen steht im Bonusabschnitt.

## 7. Ein Kursangebot vollständig verwalten

Die Verwaltung möchte ein Probeangebot anlegen, lesen, ändern und entfernen.
Diese vier Schritte heißen CRUD: Create, Read, Update und Delete.

### 7.1 Operationsfunktionen entwickeln

Die Funktionen wachsen nacheinander in derselben Datei.
Der Block zeigt ihren vollständig zusammengeführten Stand.

Datei `tag3\course_operations.py`:

<!-- file: tag3/course_operations.py -->
```python
from db import SessionLocal
from models import Course


def create_course(title: str) -> int:
    with SessionLocal.begin() as session:
        course = Course(title=title)
        session.add(course)
        session.flush()
        course_id = course.id
    return course_id


def get_course(course_id: int) -> tuple[int, str] | None:
    with SessionLocal() as session:
        course = session.get(Course, course_id)
        if course is None:
            return None
        return course.id, course.title


def rename_course(course_id: int, title: str) -> bool:
    with SessionLocal.begin() as session:
        course = session.get(Course, course_id)
        if course is None:
            return False
        course.title = title
    return True


def delete_course(course_id: int) -> bool:
    with SessionLocal.begin() as session:
        course = session.get(Course, course_id)
        if course is None:
            return False
        session.delete(course)
    return True
```


### 7.2 Anlegen und neu lesen

- create_course erzeugt ein neues Course-Objekt.
- add merkt das Objekt vor. flush sendet den INSERT.
- Danach enthält course.id die von MySQL erzeugte ID.
- Wir kopieren diese ID noch innerhalb des Transaktionsblocks.
- Das erfolgreiche Blockende bestätigt die Transaktion.
- get_course liest über eine neue Session ein Tupel oder None.

> **💡 Merke: SessionLocal.begin()**
> Dieser Kontext öffnet eine Session mit einer Transaktion.
> Bei Erfolg bestätigt er sie. Bei einer Exception rollt er sie zurück.
> Danach schließt er die Session.
> Das ist etwas anderes als with SessionLocal() ohne begin.

### 7.3 Genau das eigene Angebot ändern und entfernen

- rename_course ändert den Titel eines tatsächlich vorhandenen Objekts.
- delete_course merkt ein vorhandenes Objekt zur Löschung vor.
- Beide Funktionen liefern False, wenn die ID nicht vorhanden ist.
- Ein Fehler wird weitergegeben; der Transaktionsblock rollt zurück.
- Wir löschen in dieser Demo nur unser eigenes ungebuchtes Probeangebot.
- Beim Löschen gebuchter Kurse gelten weiterhin die Fremdschlüssel.

### 7.4 Den vollständigen Ablauf prüfen

Datei `tag3\course_demo.py`:

<!-- file: tag3/course_demo.py -->
```python
from course_operations import create_course, delete_course
from course_operations import get_course, rename_course


course_id = create_course("Runenwerkstatt - Probe")
try:
    print("Neu:", get_course(course_id))
    print("Geaendert:", rename_course(course_id, "Runenwerkstatt"))
    print("Gelesen:", get_course(course_id))
finally:
    print("Entfernt:", delete_course(course_id))
print("Danach:", get_course(course_id))
```

```powershell
python .\tag3\course_demo.py
```

<details>
<summary>Erwartung</summary>

Neu: die erzeugte ID und Runenwerkstatt - Probe.
Geaendert: True. Gelesen zeigt dieselbe ID mit Runenwerkstatt.
Entfernt: True. Danach liefert get_course den Wert None.
Es bleiben vier Kurse im Live-Bestand.
Die neue ID kann bei jeder Ausführung anders sein.

</details>


- finally entfernt das eigene Probeangebot auch bei einem Prüfungsfehler.
- Es wird nur die von create_course zurückgegebene ID gelöscht.
- commit lässt standardmäßig ORM-Attribute ablaufen.
- Eine kopierte ID oder ein Tupel braucht später keine Session zum Nachladen.

> **⚠️ Pitfall: Frühere Schreibvorgänge zurückrollen wollen**
> Jede Operationsfunktion hat eine eigene Transaktion.
> Ein Fehler beim Umbenennen nimmt das frühere Anlegen nicht zurück.
> Bei einem Prozessabbruch prüfe, ob dein Probeangebot noch vorhanden ist.
> Entferne gegebenenfalls genau seine nachgewiesene ID.

### Kleine Übertragung

1. Lies mit get_course die fehlende ID 999.
2. Versuche, diesen Kurs mit rename_course umzubenennen.
3. Prüfe, dass weiterhin vier Kurse vorhanden sind.
4. Begründe, warum die fehlende ID keinen neuen Kurs erzeugt.

- get_course liefert None. rename_course liefert False.
- [Aufgabe 5][a5] überträgt den Lebenszyklus auf einen eigenen Übungskurs.

### Den CRUD-Stand sichern

```powershell
git add -- tag3/rollback_probe.py tag3/course_operations.py
git add -- tag3/course_demo.py
git diff --cached --check
git diff --cached
git commit -m "Kursangebote mit ORM anlegen aendern und entfernen"
```


## 8. Schüler und Buchung gemeinsam anlegen

Die Verwaltung meldet Elias Brook für Arithmantik an.
Wie an Tag 2 sollen beide Datensätze gemeinsam gespeichert werden.
Ein Fehler darf keinen Schüler ohne die gewünschte Buchung hinterlassen.

### 8.1 Die gemeinsame Operation

Datei `tag3\register_student.py`:

<!-- file: tag3/register_student.py -->
```python
from datetime import date

from db import SessionLocal
from models import Booking, Student


def register_student(
    first_name: str,
    last_name: str,
    course_id: int,
    booking_date: date,
) -> tuple[int, int]:
    with SessionLocal.begin() as session:
        student = Student(
            first_name=first_name,
            last_name=last_name,
            house=None,
            school_year=1,
        )
        session.add(student)
        session.flush()
        booking = Booking(
            student_id=student.id,
            course_id=course_id,
            booking_date=booking_date,
        )
        session.add(booking)
        session.flush()
        result = student.id, booking.id
    return result
```


- Der begin-Block umfasst die gesamte Anmeldung.
- Der erste flush erzeugt die Schülerzeile und übernimmt ihre ID.
- student_id verknüpft die neue Buchung mit dieser Schüler-ID.
- Der zweite flush erzeugt die Buchung und liefert ihre ID.
- Beide Zeilen sind bis zum erfolgreichen Blockende unbestätigt.
- Ein unbekannter Kurs scheitert weiterhin am Fremdschlüssel.
- Der Fehler rollt auch die schon gesendete Schülerzeile zurück.
- Die Funktion gibt die kopierten IDs erst nach dem COMMIT zurück.

> **⚠️ Pitfall: Die Exception im Transaktionsblock verschlucken**
> Behandle den Anmeldefehler außerhalb der Operationsfunktion.
> So hat der Kontext beim Eintritt in except bereits zurückgerollt.
> Gib nach einem Datenbankfehler keine erfolgreiche ID zurück.

### 8.2 Fehlerfall und Erfolgsfall prüfen

Datei `tag3\registration_demo.py`:

<!-- file: tag3/registration_demo.py -->
```python
from datetime import date

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from db import SessionLocal
from models import Student
from register_student import register_student


try:
    register_student("Test", "Rollback", 999, date(1993, 9, 5))
except IntegrityError:
    print("Ungueltiger Kurs: Anmeldung vollstaendig zurueckgesetzt.")

with SessionLocal() as session:
    existing_id = session.scalar(
        select(Student.id).where(
            Student.first_name == "Elias",
            Student.last_name == "Brook",
        )
    )
if existing_id is None:
    ids = register_student("Elias", "Brook", 1, date(1993, 9, 5))
    print("Gespeichert: Schueler-ID, Buchungs-ID", ids)
else:
    print("Elias bereits vorhanden. Buchung in der Kontrolle pruefen.")
```

```powershell
python .\tag3\registration_demo.py
```

<details>
<summary>Erwartung</summary>

Der ungültige Kurs liefert die Rollback-Meldung.
Der Schüler Test Rollback ist danach nicht gespeichert.
Elias erhält eine Buchung für Kurs 1 am 5. September 1993.
Es bleiben zehn Schüler, vier Kurse und neun Buchungen.
Bei einem erneuten Start wird Elias nicht noch einmal angelegt.

</details>


- Kurs 999 fehlt laut Ausgangskontrolle und löst den Fehlerfall aus.
- IntegrityError behandelt hier die Fremdschlüsselverletzung.
- Der Existenzcheck dient der Wiederaufnahme dieses Unterrichtsbeispiels.
- Prüfe bei bereits vorhandenem Elias seine Buchung mit der SQL-Kontrolle.
- Dieser Check verhindert keine konkurrierenden doppelten Anmeldungen.
- Nora aus Tag 2 bleibt erhalten.
- Nora und Elias sind die vorhandenen Beispieldaten des Live-Projekts.

> **💡 Merke: Eine Anmeldung ist eine Arbeitseinheit**
> Schüler und Buchung werden mit derselben Session gespeichert.
> Zwischen ihren INSERTs steht kein COMMIT.
> Entweder werden beide Zeilen bestätigt oder beide zurückgenommen.

- [Aufgabe 7][a7] übt denselben Zusammenhang im unabhängigen Bestand.
- Objektbeziehungen sind für diese Anmeldung noch nicht erforderlich.
- Sie folgen am Anfang des Nachmittags in Abschnitt 10.

## 9. Stand am Ende des Vormittags

### Den bestätigten Datenbestand kontrollieren

Datei `sql\tag3\02_end_check.sql`:

<!-- file: sql/tag3/02_end_check.sql -->
```sql
USE hogwarts;

SELECT 'students' AS table_name, COUNT(*) AS row_count FROM students
UNION ALL
SELECT 'courses', COUNT(*) FROM courses
UNION ALL
SELECT 'bookings', COUNT(*) FROM bookings;

SELECT s.id, s.first_name, s.last_name, c.title, b.booking_date
FROM students AS s
JOIN bookings AS b ON b.student_id = s.id
JOIN courses AS c ON c.id = b.course_id
WHERE s.first_name = 'Elias' AND s.last_name = 'Brook';

SELECT id FROM students
WHERE first_name = 'Test' AND last_name = 'Rollback';

SELECT id, title FROM courses ORDER BY id;
```

Laden: `SOURCE /work/sql/tag3/02_end_check.sql;`

<details>
<summary>Erwartung</summary>

Zehn Schüler, vier Kurse und neun Buchungen.
Genau eine Zeile für Elias und Arithmantik am 5. September 1993.
Keine Zeile für Test Rollback.
Die vier ursprünglichen Kurse bleiben vorhanden.
Nora und ihre Buchung aus Tag 2 bleiben erhalten.

</details>


- [ ] core_connection zeigt hogwarts und dumbledore.
- [ ] core_catalog findet Alte Runen über einen gebundenen Parameter.
- [ ] orm_first_course liest ein Course-Objekt.
- [ ] orm_catalog zeigt vier Kurse und None für Kurs 999.
- [ ] student_search findet Ron und Ginny bei Weasley.
- [ ] Kurs 2 heißt nach der Probe weiterhin Wahrsagen.
- [ ] Das Probeangebot ist anhand seiner ID entfernt worden.
- [ ] Die fehlgeschlagene Anmeldung hinterlässt keinen Schüler.
- [ ] Elias und seine Buchung wurden genau einmal gespeichert.
- [ ] Der Endstand lautet 10 / 4 / 9.

Dieser Live-Bestand bleibt die Grundlage für Tag 4.
Der Nachmittag hat eigene Tabellen für deine Versuche.

### Die Anmeldung sichern

```powershell
git add -- tag3/register_student.py tag3/registration_demo.py
git add -- sql/tag3/02_end_check.sql
git diff --cached --check
git diff --cached
git commit -m "Anmeldung mit ORM atomar speichern"
```


### Fragen zum Selbstprüfen

1. Welche Aufgaben haben Engine, Connection und Session?
2. Was unterscheidet eine Modellklasse von einem Modellobjekt?
3. Warum verwenden wir hier kein create_all?
4. Was unterscheidet flush von commit?
5. Was liefert get bei einer fehlenden ID?
6. Was passiert, wenn der Buchungs-INSERT der Anmeldung scheitert?
7. Warum geben die Operationsfunktionen einfache Daten zurück?

<details>
<summary>Antworten zum Vergleichen</summary>

1. Die Engine organisiert Zugang und Pool. Connection ist eine Verbindung.
   Die Session verwaltet ORM-Objekte und ihre Änderungen.
2. Die Klasse beschreibt die Abbildung. Das Objekt ist ein konkreter Datensatz.
3. Das Schema ist vorhanden. create_all ändert keine bestehenden Spalten.
4. flush sendet Änderungen. commit bestätigt die ganze Transaktion.
5. get liefert None.
6. Auch der zuvor eingefügte Schüler wird zurückgerollt.
7. Der Aufrufer braucht dann keine Session zum Nachladen von Attributen.

</details>
