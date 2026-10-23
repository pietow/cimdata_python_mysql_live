# Tests und Fehlerbehandlung – Teilnehmerskript

Tag 8 des Kurses „Programmierung mit Python für komplexe Datenbanken“.

Die Hogwarts-Verwaltung möchte Änderungen an der Buchungs-API sicher prüfen.
Du baust auf Tag 7 auf und testest Antworten sowie gespeicherte Daten.

- Neue Wahlfachbuchungen sind erst ab dem dritten Schuljahr erlaubt.
- Harry darf buchen. Luna und Ginny in Jahr 2 werden abgelehnt.
- Eine fehlerhafte Gruppenbuchung darf keine Teilbuchung hinterlassen.
- Bestehende Buchungen bleiben erhalten, auch wenn sie die Regel verletzen.
- Die Beispiele verwenden den fertigen Vormittagsstand von Tag 8.


## Das brauchst du heute

| Frage | Werkzeug |
| --- | --- |
| Stimmt eine einzelne Fachregel? | Unit-Test und pytest.raises |
| Stimmen Statuscode und Antwort? | TestClient und assert |
| Wie bereite ich Tests wiederholbar vor? | Fixtures in conftest.py |
| Welche Datenbank nutzt die API im Test? | Dependency Override |
| Wurde wirklich gespeichert oder zurückgerollt? | Neue Session zum Nachlesen |
| Wurde das richtige Ereignis protokolliert? | Logger und caplog |

> **Merke:** Ein guter Test nennt eine Erwartung, die auch scheitern kann.
> Eine grüne Ausgabe ist nur so aussagekräftig wie ihre Assertions.

## 0. Die Testumgebung starten

Die Pfade gelten im Unterrichtsprojekt `hogwarts-sql`.
- Docker Desktop muss mit Linux-Containern laufen.
- Öffne in VS Code ein PowerShell-Terminal im Projektordner.
- Dieser Aufbau verwendet die Migrationen aus Tag 7 bis Revision 0002.

| Datei | Aufgabe |
| --- | --- |
| compose.test.yaml | Eigener MySQL-Dienst test_db |
| .env.test | Lokale Testpasswörter und Port, normalerweise 3308 |
| tag8/testing_db.py | Verbindung zu hogwarts_test zusammenstellen |
| tag8/init_test_db.py | Testschema mit Alembic aufbauen |
| tests/tag8/conftest.py | Fixtures und Umleitung der Datenbankzugriffe |

### 0.1 Voraussetzungen prüfen

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r .\requirements-tag7.txt
python -m pip check
docker version
docker compose version
New-Item -ItemType Directory -Force -Path .\sql\tag8
```

- docker version soll Angaben zu Client und Server anzeigen.
- Fehlt der Serverteil, zuerst Docker Desktop starten.
- Die folgenden Dateien liegen neben der normalen compose.yaml.
- Die Testumgebung bekommt einen eigenen Dienst, Port und Datenspeicher.

### 0.2 Zugangsdaten anlegen

Datei `.env.test` im Projektordner anlegen:

```dotenv
TEST_MYSQL_ROOT_PASSWORD=replace_test_root_password
TEST_MYSQL_PASSWORD=replace_test_user_password
TEST_MYSQL_PORT=3308
```


- Ersetze beide Passwortplatzhalter durch eigene lokale Testpasswörter.
- TEST_MYSQL_ROOT_PASSWORD gehört zum Administratorkonto root.
- TEST_MYSQL_PASSWORD gehört zum Testbenutzer tester.
- Die Python-Tests verbinden sich als tester, nicht als root.
- Port 3308 ist der Anschluss für Python unter Windows.
- Bei Sonderzeichen das Passwort in einfache Anführungszeichen setzen.

Diese Einträge in der vorhandenen `.gitignore` ergänzen:

```text
.env.test
reports/
.coverage
```

> **⚠️ Pitfall: Die normale .env auf Testwerte umstellen**
> Die normale API verwendet weiterhin ihre bisherigen Zugangsdaten.
> Die Testdatenbank bekommt eine eigene Datei .env.test.
> Nur die Vorlage .env.test.example wird mit Git geteilt.

### 0.3 Die vollständige Compose-Datei anlegen

Datei `compose.test.yaml` im Projektordner:

```yaml
name: hogwarts-tests

services:
  test_db:
    image: mysql:8.4.10
    environment:
      MYSQL_ROOT_PASSWORD: ${TEST_MYSQL_ROOT_PASSWORD:?Set test root password}
      MYSQL_DATABASE: hogwarts_test
      MYSQL_USER: tester
      MYSQL_PASSWORD: ${TEST_MYSQL_PASSWORD:?Set test user password}
    ports:
      # Windows:3308 wird an MySQL:3306 im Container weitergeleitet.
      - "127.0.0.1:${TEST_MYSQL_PORT:-3308}:3306"
    command:
      - --character-set-server=utf8mb4
      - --collation-server=utf8mb4_unicode_ci
    volumes:
      # Daten bleiben beim Stoppen des Containers erhalten.
      - mysql_test_data:/var/lib/mysql
      # SQL-Dateien aus dem Projekt im Container nur lesbar bereitstellen.
      - ./sql:/work/sql:ro
    healthcheck:
      test:
        - CMD-SHELL
        - >-
          MYSQL_PWD="$${MYSQL_PASSWORD}"
          mysql --protocol=TCP --host=127.0.0.1
          --user="$${MYSQL_USER}" "$${MYSQL_DATABASE}"
          --execute="SELECT 1" > /dev/null 2>&1
      interval: 5s
      timeout: 5s
      retries: 30
      start_period: 30s

volumes:
  mysql_test_data:
```

| Einstellung | Bedeutung |
| --- | --- |
| name | Eigenes Compose-Projekt hogwarts-tests |
| test_db | Dienstname für unsere Docker-Befehle |
| image | Dieselbe festgelegte MySQL-Version wie im Dozentenskript |
| environment | Erstinitialisierung von Datenbank und Benutzer |
| 127.0.0.1 | Der veröffentlichte Port ist nur lokal erreichbar. |
| mysql_test_data | Eigenes benanntes Volume für die Testdaten |
| ./sql:/work/sql:ro | Lokale SQL-Dateien im Container unter /work/sql lesen |
| healthcheck | Mit dem Testbenutzer eine echte SQL-Anfrage ausführen |

- `${VAR:?Text}` bricht bei einem fehlenden oder leeren Wert ab.
- `${TEST_MYSQL_PORT:-3308}` verwendet ohne anderen Wert den Port 3308.
- `$$` lässt ein Dollarzeichen für die Shell im Container übrig.
- Damit liest der Healthcheck die MYSQL-Werte erst innerhalb des Containers.
- Er prüft alle fünf Sekunden und wartet pro Prüfung höchstens fünf Sekunden.
- In der Startphase zählen Fehler zunächst nicht zur Grenze von 30 Versuchen.
- Ein erfolgreicher Healthcheck bestätigt die Verbindung, nicht das Testschema.
- Details: [Compose-Variablen][compose-vars] und [Healthcheck][compose-health].

### 0.4 Konfiguration prüfen und MySQL starten

Die gemeinsame Argumentliste verhindert, dass du den normalen Dienst startest.

```powershell
$testCompose = @(
    "--env-file", ".env.test", "-f", "compose.test.yaml"
)

# YAML und Variablen prüfen, ohne aufgelöste Passwörter auszugeben.
docker compose @testCompose config --quiet

# Erst nach erfolgreicher Konfigurationsprüfung starten.
docker compose @testCompose up -d --wait test_db
docker compose @testCompose ps
```

- --env-file liest die Werte aus .env.test für die Compose-Konfiguration.
- -f wählt ausdrücklich compose.test.yaml aus.
- @testCompose übergibt die Listeneinträge als einzelne Argumente.
- -d startet im Hintergrund. --wait wartet auf einen gesunden Dienst.
- Beim ersten Start kann Docker das Image herunterladen.
- Erwartet: test_db ist healthy und Port 3308 ist an 3306 gebunden.
- In jedem neuen PowerShell-Terminal die Variable testCompose erneut setzen.
- Bereits gesetzte TEST_MYSQL-Umgebungsvariablen können Dateiwerte übersteuern.

> **⚠️ Pitfall: Container-Port und Windows-Port verwechseln**
> Python unter Windows verwendet 127.0.0.1:3308.
> Innerhalb des Containers läuft MySQL weiterhin auf Port 3306.
> test_db ist der Compose-Dienstname, kein Hostname für lokales Python.

### 0.5 Anmeldung und Testschema prüfen

Öffne zuerst den MySQL-Client im Testcontainer:

```powershell
docker compose @testCompose exec test_db mysql -u tester -p hogwarts_test
```

- Gib bei der Passwortabfrage den Wert von TEST_MYSQL_PASSWORD ein.
- Es ist normal, dass beim Tippen keine Zeichen angezeigt werden.
- Verlasse den Client anschließend mit `exit;`.

Die Datenbank existiert jetzt. Die Tabellen entstehen erst durch Alembic.
Übernimm dafür die beiden Python-Dateien aus dem [Startmaterial][test-setup]:

- `tag8/testing_db.py` liest .env.test und wählt fest hogwarts_test.
- `tag8/init_test_db.py` führt die vorhandenen Migrationen aus.
- Der Aufruf gilt für den Tag-8-Stand mit Migrationen bis 0002.
- Das Skript setzt die Testverbindung in seinem eigenen Python-Prozess.
- Die normale .env und das aufrufende PowerShell-Terminal bleiben unverändert.

```powershell
python -m tag8.init_test_db
```

Den MySQL-Client für die Kontrolle erneut öffnen:

```powershell
docker compose @testCompose exec test_db mysql -u tester -p hogwarts_test
```

Datei `sql/tag8/02_test_schema_check.sql`:

```sql
USE hogwarts_test;
SELECT DATABASE();
SELECT version_num FROM alembic_version;
SELECT COUNT(*) AS student_count FROM students;
SELECT COUNT(*) AS course_count FROM courses;
SELECT COUNT(*) AS booking_count FROM bookings;
```

Im MySQL-Client ausführen:

```text
SOURCE /work/sql/tag8/02_test_schema_check.sql;
```

- Erwartet: hogwarts_test, Revision 0002 und zunächst drei leere Tabellen.
- SOURCE liest den Containerpfad /work/sql, nicht den Windows-Pfad.
- Der Mount aus compose.test.yaml macht dieselbe Datei dort erreichbar.
- Vor dem nächsten PowerShell-Befehl den MySQL-Client mit `exit;` verlassen.

### 0.6 Die Tests ausführen

Übernimm die [vollständigen Fixtures][fixtures] aus dem Vormittag.
Sie prüfen den Datenbanknamen und lenken die API auf die Testdatenbank um.

```powershell
python -m pytest .\tests\tag8 -q
```

- TestClient benötigt keinen laufenden Uvicorn-Server.
- Regel- und Health-Tests benötigen auch keine laufende Datenbank.
- Die Integrationstests benötigen den Dienst test_db.
- Nach einem vollständigen DB-Test räumen die Fixtures die Testzeilen auf.
- Tabellen und Migrationsstand bleiben erhalten.

### 0.7 Stoppen, wiederaufnehmen und Fehler eingrenzen

```powershell
# Bei einem Startfehler zuerst Status und letzte Meldungen ansehen.
docker compose @testCompose ps
docker compose @testCompose logs --tail 50 test_db

# Für die Pause oder das Unterrichtsende stoppen.
docker compose @testCompose stop test_db

# Später wieder starten. Das vorhandene Volume wird weiterverwendet.
docker compose @testCompose up -d --wait test_db
```

| Beobachtung | Nächster Schritt |
| --- | --- |
| Docker-Server nicht erreichbar | Docker Desktop starten und erneut prüfen. |
| Passwortvariable fehlt | Dateiname, Werte und --env-file prüfen. |
| Port 3308 ist belegt | Freien TEST_MYSQL_PORT in .env.test wählen. |
| test_db bleibt unhealthy | Logs und Zugangsdaten prüfen. |
| Tabelle fehlt | init_test_db am richtigen Unterrichtsstand ausführen. |
| Falsche Revision | Projektstand mit Tag 8 abgleichen; nicht herabstufen. |

> **⚠️ Pitfall: Passwortänderung nur in .env.test speichern**
> MySQL legt Benutzer und Passwörter beim ersten leeren Datenverzeichnis an.
> Bei vorhandenem Volume ändert eine neue Umgebungsvariable kein DB-Passwort.
> Verwende die bisherigen Werte oder ändere das Passwort gezielt in MySQL.
> Das Verhalten beschreibt das [offizielle MySQL-Image][mysql-image].

- Ein Volume erhält Daten, ersetzt aber kein Backup.
- Zum normalen Stoppen ist kein Löschen des Volumes erforderlich.

> **⚠️ Pitfall: Tests auf dem Unterrichtsbestand ausführen**
> Die DB-Fixtures löschen Testzeilen vor und nach jedem Test.
> Nutze die vollständige Konfiguration mit Prüfung auf hogwarts_test.
> Starte gezielt tests/tag8. Die alte Datei tag7/test_api.py gehört nicht dazu.

## 1. Eine Fachregel mit Grenzfällen prüfen

Ein Unit-Test prüft die Regel ohne HTTP und Datenbank.
Wir verwenden zunächst Tests, dann eine passende Implementierung.

1. **Rot:** Ein Test findet das noch fehlende Verhalten.
2. **Grün:** Die kleinste passende Implementierung erfüllt die Erwartung.
3. **Verbessern:** Code vereinfachen und erneut testen.

Datei: `tag8/rules.py`, fertige Regel aus dem Unterricht.

```python
class SchoolYearTooLow(ValueError):
    pass


ELECTIVE_COURSES = frozenset({
    "Arithmantik", "Wahrsagen", "Alte Runen", "Pflege magischer Geschöpfe",
})


def validate_elective_year(school_year: int, course_title: str) -> None:
    if course_title in ELECTIVE_COURSES and school_year < 3:
        raise SchoolYearTooLow("Wahlfächer sind ab Schuljahr 3 buchbar.")
```

Datei: `tests/tag8/test_rules.py`.

```python
import pytest

from tag8.rules import SchoolYearTooLow, validate_elective_year


@pytest.mark.parametrize("year", [3, 7])
def test_elective_accepts_allowed_year(year):
    # Hier ist keine Ausnahme das erwartete Verhalten.
    validate_elective_year(year, "Alte Runen")


@pytest.mark.parametrize("year", [1, 2])
def test_elective_rejects_lower_year(year):
    # Fehlt die Ausnahme, scheitert der Test mit DID NOT RAISE.
    with pytest.raises(SchoolYearTooLow, match="ab Schuljahr 3"):
        validate_elective_year(year, "Alte Runen")


def test_other_offer_has_no_elective_limit():
    validate_elective_year(2, "Flugkunde")
```

```powershell
python -m pytest .\tests\tag8\test_rules.py -q
```

- parametrize erzeugt für jeden angegebenen Wert einen eigenen Testfall.
- Hier entstehen fünf Fälle aus drei Testfunktionen.
- Die Grenze liegt zwischen Jahr 2 und Jahr 3.
- Die Schemas prüfen weiterhin gültige Schuljahre von 1 bis 7.
- Die neue Fachregel betrifft nur die vier aufgeführten Wahlfächer.

> **⚠️ Pitfall: Nur erlaubte Eingaben testen**
> Eine leere Funktion würde die erlaubten Fälle ebenfalls bestehen.
> Prüfe auch die Ablehnung und die erlaubte Grenze selbst.
> Bei versehentlichem <= 3 muss der Test für Jahr 3 scheitern.

## 2. API-Antworten mit TestClient prüfen

Ein Test folgt häufig drei Schritten: vorbereiten, ausführen, prüfen.
Die englischen Bezeichnungen sind Arrange, Act und Assert.

Die Fixture `client` steht bereits in `tests/tag8/conftest.py`.
Dieser Ausschnitt erklärt das Muster; die vollständigen DB-Fixtures bleiben.

```python
import pytest
from fastapi.testclient import TestClient

from tag8.main import app


@pytest.fixture
def client():
    return TestClient(app)
```

Datei: `tests/tag8/test_health.py`.

```python
def test_health(client):
    # Arrange: pytest stellt client über die gleichnamige Fixture bereit.
    response = client.get("/health")  # Act: Anfrage an die App ausführen.
    assert response.status_code == 200  # Assert: Status prüfen.
    assert response.json() == {"status": "ok"}  # Antwortvertrag prüfen.
```

- TestClient ruft die App im Testprozess auf, ohne echten HTTP-Server.
- Der Parameter client fordert die Fixture an; du rufst sie nicht selbst auf.
- assert vergleicht tatsächliches und erwartetes Verhalten.
- Ein Health-Test bestätigt hier keine funktionierende MySQL-Verbindung.

> **⚠️ Pitfall: Nur assert response schreiben**
> Damit prüfst du weder den erwarteten Status noch die Antwortfelder genau.
> Verwende konkrete Assertions für den Vertrag der Route.

## 3. Fixtures und Testdaten auseinanderhalten

Fixtures übernehmen wiederverwendbare Vorbereitung und Aufräumen.
Der vollständige [Fixture-Stand][fixtures] ist die Grundlage aller DB-Tests.

| Fixture | Aufgabe |
| --- | --- |
| client | App für Health und isolierte Fehlerantworten ansprechen |
| test_engine | Testdatenbank und Revision prüfen; Engine bereitstellen |
| db_factory | Testtabellen leeren und eine Session-Fabrik liefern |
| seed | Vier Schüler und drei Kurse speichern; ihre IDs zurückgeben |
| api_client | API-Dependency auf die Testdatenbank umstellen |

- Standard-Scope function: eine Fixture-Instanz pro Testfall.
- test_engine hat Scope session: eine Engine für den gesamten Testlauf.
- seed und api_client verwenden im selben Test dieselbe db_factory.
- Verschiedene Testfälle erhalten über db_factory einen leeren Ausgangsstand.
- yield übergibt einen Wert; der Aufräumteil läuft beim Fixture-Abbau.
- finally sorgt dafür, dass Aufräumen auch nach einem Testfehler versucht wird.
- pytest findet conftest.py für Tests in diesem Ordner und seinen Unterordnern.
- Der Parametername fordert die Fixture an. Wir rufen sie nicht selbst auf.
- Nur angeforderte Fixtures und ihre Abhängigkeiten werden aufgebaut.

Die folgenden Ausschnitte erklären die vorhandene `tests/tag8/conftest.py`.
Sie werden nicht zusätzlich als zweite Fixtures angelegt.
Diese Imports gehören zum gemeinsamen Modul:

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete, text
from sqlalchemy.orm import sessionmaker

from tag7.dependencies import get_session
from tag7.models import Booking, Course, Student
from tag8.main import app
from tag8.testing_db import make_test_url
```

### 3.1 client: Die App ohne Datenbankumleitung ansprechen

- Liefert den TestClient aus Abschnitt 2.
- Hat keine Abhängigkeit von einer anderen Fixture.
- Wird pro Testfall neu erstellt, sobald ein Test client anfordert.
- return übergibt den Client; die Fixture hat keinen eigenen Aufräumteil.
- Wir verwenden ihn für /health und den gezielt simulierten Datenbankfehler.
- Er startet weder einen Uvicorn-Server noch selbst eine MySQL-Verbindung.
- Eine aufgerufene DB-Route könnte aber die normale Session anfordern.

> **⚠️ Pitfall: TestClient bedeutet automatisch Testdatenbank**
> Der Client allein ändert die Datenbankverbindung nicht.
> Erst api_client ersetzt die Session-Dependency der App.

### 3.2 test_engine: Den Datenbankzugang einmal prüfen

- Liefert eine SQLAlchemy-Engine für hogwarts_test.
- make_test_url liest den Zugang aus .env.test.
- Scope session meint den gesamten pytest-Lauf, nicht eine ORM-Session.
- Sie wird aufgebaut, sobald ein Test sie direkt oder indirekt braucht.

```python
@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine(make_test_url(), pool_pre_ping=True)
    try:
        with engine.connect() as connection:
            name = connection.scalar(text("SELECT DATABASE()"))
            if name != "hogwarts_test":
                raise RuntimeError("Dies ist nicht die Testdatenbank.")
            revision = connection.scalar(text(
                "SELECT version_num FROM alembic_version"
            ))
            if revision != "0002":
                raise RuntimeError("Zuerst init_test_db ausführen.")
        yield engine  # Dieselbe Engine dient den heutigen DB-Tests.
    finally:
        engine.dispose()  # Pool beim Abbau der Fixture freigeben.
```

- Der Verbindungsblock prüft Datenbankname und erwartete Migration.
- Bei einer falschen Datenbank wird vor der Tabellenbereinigung abgebrochen.
- Die Engine stellt Verbindungen bereit. Sie enthält nicht den Testbestand.
- Sie führt weder Migrationen aus noch legt sie Schüler oder Kurse an.
- Beim normalen Ende des Testlaufs wird die Engine freigegeben.

> **⚠️ Pitfall: Scope session für alle Fixtures übernehmen**
> Die Engine darf geteilt werden. Veränderliche Testdaten brauchen Isolation.
> Eine gemeinsame Datenvorbereitung für alle Tests würde Zustände weiterreichen.

### 3.3 db_factory: Mit leeren Tabellen beginnen und aufräumen

- Braucht test_engine und liefert eine Session-Fabrik aus sessionmaker.
- Die Fabrik erzeugt bei jedem Aufruf eine neue ORM-Session.
- Vor dem Test werden alte Testzeilen entfernt, danach die neuen Testzeilen.
- clear_test_rows ist eine normale Hilfsfunktion, keine pytest-Fixture.

```python
def clear_test_rows(factory):
    # Nur über die geprüfte Test-Engine verwenden.
    with factory.begin() as db:
        db.execute(delete(Booking))  # Kindzeilen zuerst entfernen.
        db.execute(delete(Student))
        db.execute(delete(Course))
    # Der erfolgreiche Block bestätigt die Löschungen mit einem Commit.


@pytest.fixture
def db_factory(test_engine):
    factory = sessionmaker(bind=test_engine)
    clear_test_rows(factory)  # Definierter Anfang, auch nach einem Abbruch.
    try:
        yield factory
    finally:
        clear_test_rows(factory)  # Aufräumen auch nach fehlgeschlagenem assert.
```

- Buchungen verweisen auf Schüler und Kurse. Deshalb werden sie zuerst gelöscht.
- Die Bereinigung entfernt Zeilen, keine Tabellen und kein Volume.
- alembic_version bleibt bestehen.
- `with db_factory() as db` öffnet eine Session und schließt sie danach.
- Dieser normale Session-Kontext führt keinen automatischen Commit aus.
- `with db_factory.begin() as db` umfasst zusätzlich eine Transaktion.
- Bei Erfolg folgt ein Commit. Bei einer Ausnahme folgt ein Rollback.

> **⚠️ Pitfall: Die Fabrik mit einer Session verwechseln**
> db_factory wird im Test geteilt. Jeder Aufruf erzeugt eine neue Session.
> Er startet die Fixture nicht erneut und leert keine Tabellen.

### 3.4 seed: Einen bekannten Anfangsbestand speichern

- Braucht db_factory und damit indirekt die geprüfte test_engine.
- Legt vier Schüler und drei Kurse an. Buchungen werden nicht angelegt.
- Liefert ein Dictionary mit den tatsächlich erzeugten IDs.
- Die vorbereiteten Daten sind für die folgenden API-Requests sichtbar.

```python
@pytest.fixture
def seed(db_factory):
    with db_factory.begin() as db:
        harry = Student(first_name="Harry", last_name="Potter",
                        house="Gryffindor", school_year=3)
        hermione = Student(first_name="Hermione", last_name="Granger",
                           house="Gryffindor", school_year=3)
        luna = Student(first_name="Luna", last_name="Lovegood",
                       house="Ravenclaw", school_year=2)
        ginny = Student(first_name="Ginny", last_name="Weasley",
                        house="Gryffindor", school_year=2)
        elective = Course(title="Alte Runen")
        other = Course(title="Flugkunde")
        empty = Course(title="Astronomie")
        db.add_all([harry, hermione, luna, ginny, elective, other, empty])
        db.flush()  # INSERTs ausführen: Die erzeugten IDs stehen jetzt fest.
        result = {
            "harry_id": harry.id, "hermione_id": hermione.id,
            "luna_id": luna.id, "ginny_id": ginny.id,
            "course_id": elective.id, "other_course_id": other.id,
            "empty_course_id": empty.id,
        }
    # Erst den erfolgreichen Commit abwarten, dann die IDs weitergeben.
    return result
```

- flush liefert die IDs, ist aber noch kein Commit.
- Der Commit erfolgt beim erfolgreichen Verlassen von db_factory.begin().
- Zurückgegeben werden einfache Werte statt sessiongebundener ORM-Objekte.
- seed braucht keinen eigenen Löschteil: db_factory räumt später auf.

| Schlüssel aus seed | Bedeutung |
| --- | --- |
| harry_id, hermione_id | Schüler im dritten Schuljahr |
| luna_id, ginny_id | Schülerinnen im zweiten Schuljahr |
| course_id | Alte Runen |
| other_course_id | Flugkunde |
| empty_course_id | Astronomie |

> **⚠️ Pitfall: Feste IDs wie 1 und 2 erwarten**
> Das Leeren einer Tabelle setzt ihren Auto-Increment-Zähler nicht zurück.
> Verwende die IDs aus seed oder aus der API-Antwort.

### 3.5 api_client: API-Requests auf die Testdatenbank umleiten

- Braucht dieselbe db_factory wie seed und liefert einen TestClient.
- Ersetzt die Herkunft der Session, nicht die Fachlogik der Route.
- Vor dem Test wird die Umleitung gesetzt; danach wird sie zurückgenommen.

```python
@pytest.fixture
def api_client(db_factory):
    def override_session():
        with db_factory() as db:  # Eigene Session für jeden Request.
            yield db

    previous = app.dependency_overrides.copy()
    app.dependency_overrides[get_session] = override_session
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous)
```

- pytest, app und TestClient sind bereits im selben Modul importiert.
- Der Schlüssel ist die originale Funktion get_session, ohne Klammern.
- FastAPI ruft für diesen Test stattdessen override_session auf.
- override_session ist eine FastAPI-Ersatzdependency, keine pytest-Fixture.
- Ihr inneres yield stellt eine Session für einen einzelnen Request bereit.
- Das äußere yield der Fixture stellt den Client für den ganzen Test bereit.
- Die Routen führen ihre eigenen Transaktionen weiterhin wirklich aus.
- Nach dem Test wird der vorherige Override-Zustand wiederhergestellt.

> **⚠️ Pitfall: client und api_client verwechseln**
> client leitet Datenbankzugriffe nicht automatisch um.
> Für echte DB-Aufträge ist api_client mit den vollständigen Fixtures nötig.
> Keine parallelen Testläufe auf dieser gemeinsam geleerten Testdatenbank.

### 3.6 Wie arbeiten die Fixtures in einem Test zusammen?

Der Buchungstest aus Abschnitt 5 fordert drei Werte an:

```python
def test_batch_rolls_back_on_school_year(api_client, seed, db_factory):
    # Hier folgt der Testkörper aus Abschnitt 5.
    ...
```

| Angefordert | Braucht vorher |
| --- | --- |
| api_client | db_factory → test_engine |
| seed | db_factory → test_engine |
| db_factory | test_engine |

1. pytest stellt zunächst die benötigte test_engine bereit.
2. db_factory leert die Testtabellen und liefert die Fabrik.
3. seed speichert Startdaten; api_client richtet den Override ein.
4. Erst wenn beide bereit sind, beginnt der eigentliche Testkörper.
5. Der Request verwendet eine Session aus der gemeinsamen Test-Fabrik.
6. Der Test liest anschließend mit einer neuen Session aus derselben DB.
7. Beim Abbau wird der Override zurückgesetzt und db_factory leert die Tabellen.
8. Am Ende des Testlaufs wird test_engine abgebaut.

- seed und api_client haben untereinander keine festgelegte Aufbaureihenfolge.
- Sie hängen beide von db_factory ab und müssen vor dem Testkörper fertig sein.
- pytest führt db_factory innerhalb desselben Testfalls nur einmal aus.
- Mehrere Abhängigkeiten erhalten ihren bereits bereitgestellten Wert.
- Deshalb löscht api_client nicht erneut die gerade angelegten Seed-Daten.
- Nach einem assert-Fehler läuft der normale Fixture-Abbau ebenfalls.
- Ein hart beendeter Prozess kann Aufräumen verhindern; der nächste Lauf leert.

| Zeitpunkt | Schüler | Kurse | Buchungen |
| --- | ---: | ---: | ---: |
| Nach db_factory, vor seed | 0 | 0 | 0 |
| Nach seed | 4 | 3 | 0 |
| Nach abgelehnter Gruppe mit erfolgreichem Rollback | 4 | 3 | 0 |
| Nach vollständigem Fixture-Abbau | 0 | 0 | 0 |

Den tatsächlichen Aufbau und Abbau anzeigen:

```powershell
python -m pytest .\tests\tag8\test_bookings.py -v --setup-show
```

> **⚠️ Pitfall: Testreihenfolge als Datenvorbereitung verwenden**
> Ein Test darf nicht darauf warten, dass ein anderer vorher einen Kurs anlegt.
> Fordere seed an oder lege die benötigten Daten im eigenen Test an.

## 4. Eine Speicherung unabhängig nachlesen

Die API könnte 201 melden, obwohl nichts dauerhaft gespeichert wurde.
Deshalb prüfen wir die Antwort und lesen danach mit einer neuen Session.

Ausschnitt aus dem Kurs-CRUD-Test in `tests/tag8/test_courses.py`:

```python
from tag7.models import Course


def test_course_roundtrip(api_client, db_factory):
    response = api_client.post("/courses", json={"title": " Flugkunde "})
    assert response.status_code == 201
    created = response.json()
    course_id = created["id"]
    assert created == {
        "id": course_id, "title": "Flugkunde", "room": None,
    }
    with db_factory() as db:  # Unabhängig vom Session-Zustand der Route.
        stored = db.get(Course, course_id)
        assert stored is not None
        assert stored.title == "Flugkunde"
```

- Der vollständige Unterrichtstest prüft zusätzlich Lesen, Ändern und Löschen.
- Nach DELETE erwarten wir 204, einen leeren Body und anschließend 404.
- Auch das Löschen wird mit einer neuen Session nachgelesen.

> **⚠️ Pitfall: Ein ORM-Objekt als Commit-Nachweis verwenden**
> Ein Objekt in einer Session muss noch nicht dauerhaft gespeichert sein.
> Lies den Zustand unabhängig nach. flush ist noch kein Commit.

## 5. Rollback als fachliche Eigenschaft testen

Harry wird zuerst verarbeitet. Danach scheitert Luna an der Wahlfachregel.
Die Route aus `tag8/routers/bookings.py` bündelt den Auftrag in db.begin().
Sie führt nach jedem hinzugefügten Booking ein flush aus.

Datei: `tests/tag8/test_bookings.py`, der Rollback-Test aus dem Unterricht.

```python
from sqlalchemy import func, select

from tag7.models import Booking


def test_batch_rolls_back_on_school_year(api_client, seed, db_factory):
    response = api_client.post("/booking-batches", json={
        "course_id": seed["course_id"],
        "student_ids": [seed["harry_id"], seed["luna_id"]],
        "booking_date": "1993-09-06",
    })
    assert response.status_code == 409
    assert response.json() == {
        "detail": "Wahlfächer sind ab Schuljahr 3 buchbar.",
    }
    with db_factory() as db:
        count = db.scalar(select(func.count()).select_from(Booking))
    assert count == 0  # Auch Harrys zuerst eingefügte Buchung fehlt.
```

1. Die Fachregel löst SchoolYearTooLow aus.
2. Die Ausnahme verlässt den Transaktionsblock; db.begin führt Rollback aus.
3. Der registrierte Fehlerhandler übersetzt die Ausnahme in HTTP 409.
4. Der Test prüft danach, dass keine Buchung übrig ist.

| Situation | Erwarteter Status |
| --- | --- |
| Gültige Gruppe gespeichert | 201 |
| Kurs oder Schüler existiert nicht | 404 |
| Schuljahrregel oder Buchungskonflikt | 409 |
| Ungültiger Request nach Schema oder Parametern | 422 |
| Behandelter OperationalError | 503 |

> **⚠️ Pitfall: 409 mit erfolgreichem Rollback gleichsetzen**
> Der Status allein entdeckt keine gespeicherte Teilbuchung.
> Prüfe nach dem fehlgeschlagenen Auftrag zusätzlich den Datenbankzustand.

## 6. Ereignisse mit caplog prüfen

Logs ergänzen die Aussagen aus HTTP-Antwort und Datenbank.
Die App verwendet die Konfiguration in `tag8/logging_setup.py`.

| Ereignis | Logger | Level |
| --- | --- | --- |
| booking_batch_saved | hogwarts.bookings | INFO |
| booking_batch_rejected | hogwarts.api | WARNING |
| database_unavailable | hogwarts.api | ERROR |

- Die Erfolgsmeldung steht im Router nach dem Transaktionsblock.
- Die Einträge enthalten Ereignisnamen und IDs, keine Request-Bodies.
- caplog ist eine von pytest bereitgestellte Fixture.

Datei: `tests/tag8/test_logging.py`.

```python
import logging


def test_successful_batch_is_logged(api_client, seed, caplog):
    caplog.set_level(logging.INFO, logger="hogwarts.bookings")
    response = api_client.post("/booking-batches", json={
        "course_id": seed["course_id"],
        "student_ids": [seed["harry_id"]],
        "booking_date": "1993-09-06",
    })
    assert response.status_code == 201
    expected = f"booking_batch_saved course_id={seed['course_id']} count=1"
    records = [r for r in caplog.records if r.name == "hogwarts.bookings"]
    assert [r.getMessage() for r in records] == [expected]
    assert records[0].levelno == logging.INFO
```

> **⚠️ Pitfall: Ein Logeintrag beweist die Speicherung**
> Dieser Test prüft Meldung und Level, nicht den Datenbankinhalt.
> Er beweist auch nicht die zeitliche Reihenfolge von Commit und Logeintrag.
> Dafür bleiben Codeprüfung und die Datenbanktests nötig.

### Optional: Eine Störung kontrolliert auslösen

- Der Unterrichtstest ersetzt get_session vorübergehend durch eine Funktion.
- Diese wirft gezielt OperationalError; eine echte Verbindung entsteht nicht.
- monkeypatch setzt den Override nach dem Test wieder zurück.
- Geprüft werden 503, ein neutraler Antworttext und ein ERROR-Logeintrag.
- Technische Fehlerdetails dürfen weder in Antwort noch Log erscheinen.
- Die Zuordnung jedes OperationalError zu 503 ist eine Kursvereinfachung.
- Der Test prüft den Fehlerhandler, nicht die Ausfallsicherheit von MySQL.

## 7. Tests im Alltag ausführen

```powershell
# Gesamten Tag prüfen.
python -m pytest .\tests\tag8 -q

# Nur eine Datei prüfen und Testnamen anzeigen.
python -m pytest .\tests\tag8\test_bookings.py -v

# Passende Namen auswählen und Fixture-Aufbau ansehen.
python -m pytest .\tests\tag8 -k "school_year" -v
python -m pytest .\tests\tag8 --setup-show -q

# Tests sammeln oder zuletzt fehlgeschlagene Tests wiederholen.
python -m pytest .\tests\tag8 --collect-only -q
python -m pytest .\tests\tag8 -x --lf
```

- Der vollständige Vormittag enthält zwölf Fälle, optional dreizehn.
- Zusätzliche Übungstests erhöhen diese Anzahl.
- collect-only führt Testkörper und Fixtures nicht aus; Imports laufen trotzdem.
- -x stoppt beim ersten Fehler. --lf wählt zuletzt fehlgeschlagene Fälle.
- Ohne gespeicherte Fehlschläge kann --lf wieder alle Tests ausführen.
- Nach einer neuen Migration init_test_db erneut ausführen.
- Nach dem Testen den Dienst bei Bedarf stoppen; das Volume bleibt bestehen.

```powershell
docker compose @testCompose stop test_db
git add .\tag8 .\tests\tag8 .\pytest.ini
git commit -m "Buchungsregeln und Rollback mit Tests absichern"
```

