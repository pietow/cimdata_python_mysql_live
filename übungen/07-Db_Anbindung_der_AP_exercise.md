# Datenbankanbindung der API – Übungen für Tag 7

## Überblick

Die Hogwarts-Verwaltung verwendet jetzt eine dauerhafte MySQL-Datenbank.
Ihr erweitert die API um Schülerlisten und Änderungen an Buchungen.
Anschließend prüft ihr Transaktionen und die erste Schemaänderung.

- Pflicht: Aufgaben 1–8. Bonus: Aufgaben 9–11.
- Arbeitet im Unterrichtsprojekt im vorhandenen venv.

- MySQL läuft im Docker-Dienst db. Alembic steht auf Revision 0002.
- Die Übungs-App läuft auf Port 8001 und verwendet dieselbe Datenbank.
- Ein Serverneustart setzt den Datenbestand nicht zurück.
- Verwendet die echten MySQL-IDs, nicht die Speicher-IDs aus Tag 6.
- Ändert für Schreibtests nur die zusätzlich angelegten Übungseinträge.

- Die Testdatei ist vorgegeben; eigene Tests sind heute kein Auftrag.

| Aufgabe | Auftrag |
| --- | --- |
| 1 | Speichergrenzen und API-Vertrag erklären |
| 2 | Schüler aus MySQL lesen |
| 3 | Haus und Schuljahr gemeinsam filtern |
| 4 | Eine vorhandene Buchung umbuchen |
| 5 | Eine Buchung entfernen |
| 6 | Ganz-oder-gar-nicht nachweisen |
| 7 | Migration und erhaltene Daten prüfen |
| 8 | Kontrollfragen beantworten |
| 9 | Bonus: Buchungszeitraum als Klassen-Dependency |
| 10 | Bonus: Räume per API setzen und entfernen |
| 11 | Bonus: Cursor und Transaktionen mit sqlite3 |

### Postman-Collection verwenden

- Datei: [07-Tag7-Hogwarts.postman_collection.json][postman].
- Collection: „Tag 7 – Hogwarts“; die Datei an die Teilnehmenden verteilen.
- Ordner einzeln passend zum erreichten Unterrichtsstand verwenden.
- Die gesamte Collection nicht am Stück ausführen.
- Vier Werte vorher setzen: harry_id, ron_id und zwei fehlende positive IDs.
- missing_student_id und missing_course_id zuerst per SQL als fehlend prüfen.
- Weitere IDs übernimmt die Collection aus den Antworten.
- Keine gleichnamigen Environment-Variablen verwenden.
- Die JSON-Platzhalter werden durch Collection-Variablen ersetzt.
- Anlage-POSTs nur einmal senden; ein Neustart setzt MySQL nicht zurück.
- probe_course_id ist der löschbare Probekurs aus dem ersten Ordner.
- created_course_id gehört zum zweiten Kurs für die Gruppenübung.
- Zwischen Rollback-Vergleichen keine parallelen Buchungen verändern.
- Die Antwortprüfungen sind vorgegeben; eigene Skripte sind kein Auftrag.

Alle Verweise in dieser Tabelle beginnen mit „Tag 7 – Hogwarts →“.
Die übrigen Fälle stehen jeweils im selben Ordner direkt daneben.

| Zeitpunkt | Ordner → Request | Methode und Endpoint |
| --- | --- | --- |
| Lesen | 00 Kurse lesen und ändern → 02 Kurskatalog und Runen-ID | GET /courses |
| POST | 00 Kurse lesen und ändern → 06 Probekurs anlegen | POST /courses |
| PUT | 00 Kurse lesen und ändern → 08 Probekurs umbenennen | PUT /courses/{{probe_course_id}} |
| DELETE | 00 Kurse lesen und ändern → 10 Probekurs löschen | DELETE /courses/{{probe_course_id}} |
| Gruppenauftrag vorbereiten | 01 Gruppenbuchung und Rollback → 01 Flugkunde für Übungen anlegen | POST /courses |
| Fehlerfall | 01 Gruppenbuchung und Rollback → 04 Gruppenauftrag mit fehlendem Schüler | POST /booking-batches |
| Gegenprobe | 01 Gruppenbuchung und Rollback → 06 Harry und Ron gemeinsam buchen | POST /booking-batches |
| Migration | 02 Nach der Migration → 01 Raumspalte in Kursantwort | GET /courses/{{created_course_id}} |
| Aufgabe 2 | 03 Übungen → 01 Schüler lesen | GET /students |
| Aufgabe 3 | 03 Übungen → 05 Beide Filter verbinden | GET /students?house=Gryffindor&school_year=2 |
| Aufgabe 4 | 03 Übungen → 10 Harry zu Alten Runen umbuchen | PATCH /bookings/{{booking_one_id}} |
| Aufgabe 5 | 03 Übungen → 13 Rons Zusatzbuchung löschen | DELETE /bookings/{{booking_two_id}} |
| Aufgabe 6 | 03 Übungen → 16 Bestand vor Fehlerauftrag; dann 17 und 18 | GET /bookings; POST /booking-batches; GET /bookings |
| Aufgabe 9 | 04 Bonus → 02 Ein Buchungstag | GET /booking-report?start=1993-09-06&end=1993-09-06 |
| Aufgabe 10 | 04 Bonus → 05 Raum setzen | PUT /courses/{{created_course_id}}/room |

- Vormittag: base_url = http://127.0.0.1:8000.
- Übungen: practice_url = http://127.0.0.1:8001.
- Bonus: bonus_url = http://127.0.0.1:8002.
- SQL- und Alembic-Aufträge bleiben im Terminal; Postman prüft HTTP.

## Vor dem Start

- Den Vormittagsserver auf Port 8000 bei Bedarf mit Strg+C stoppen.
- Die zusätzlichen Live-IDs aus dem Vormittag bereithalten.
- created_course_id bezeichnet das neue Angebot „Flugkunde“.
- booking_one_id und booking_two_id bezeichnen seine beiden Buchungen.
- Die erste gehört Harry, die zweite Ron. Beide stammen aus dem Vormittag.
- Falls der Auftrag dort nicht erfolgreich lief, ihn genau einmal ausführen.
- Bei einem bestehenden Angebot die IDs aus GET /bookings übernehmen.
- Ein mehrfacher POST erzeugt zusätzliche Datensätze.
- In Postman die Collection „Tag 7 – Hogwarts“ verwenden.
- practice_url als Collection-Variable auf http://127.0.0.1:8001 setzen.
- Für POST, PUT und PATCH Body → raw → JSON wählen.
- In der Collection werden die JSON-Platzhalter automatisch ersetzt.
- Bei eigenen Requests die tatsächlichen Zahlen verwenden.

```powershell

.\.venv\Scripts\Activate.ps1
docker compose up -d db
python -m pip check
python -m alembic current    # kommt später dran
```

- Erwartet wird Revision 0002. (kommt später)
- Alle folgenden Dateien liegen unter tag7.
- Die Modelle, Schemas und Dependencies des Vormittags bleiben verfügbar.

<a id="aufgabe-1"></a>

## 1. Speichergrenzen und API-Vertrag erklären

Die Verwaltung fragt, welche Daten einen Neustart überstehen.

### Aufgaben

1. Erklärt, wo die Kurse an Tag 6 und heute gespeichert werden.
2. Beschreibt die Aufgaben von Engine, Session und Pydantic-Modell.
3. Nennt die Funktion, die eine Session an den Endpunkt liefert.
4. Ordnet Lesen, Umbuchen und Löschen passenden HTTP-Methoden zu.
5. Erklärt, warum ein anderer Port keine eigene Datenbank erzeugt.

### Erfolgskriterien

- Ihr unterscheidet Prozessspeicher, Datenbank und Antwortdaten.
- Die Session wird pro Request erstellt und danach geschlossen.
- Ihr verwechselt das Schließen einer Session nicht mit einem Commit.
- Für Buchungen verwendet ihr GET, PATCH und DELETE.

<a id="aufgabe-2"></a>

## 2. Schüler aus MySQL lesen

Die Verwaltung möchte Schülerdaten im selben Werkzeug wie Kurse lesen.

### Startmaterial

- Legt zunächst den leeren Übungsrouter an.
- Er wird in den folgenden Aufgaben erweitert.

<!-- file: tag7/routers/practice.py -->
- Lokal: `.\tag7\routers\practice.py`.

```python
from fastapi import APIRouter

router = APIRouter(tags=["Übungen"])
```

<!-- file: tag7/practice.py -->
- Lokal: `.\tag7\practice.py`.

```python
from fastapi import FastAPI

from tag7.routers import bookings, courses, practice

app = FastAPI(title="Hogwarts – Datenbankübungen")
app.include_router(courses.router)
app.include_router(bookings.router)
app.include_router(practice.router)


@app.get("/health")
def read_health():
    return {"status": "ok"}
```

```powershell
python -m uvicorn tag7.practice:app --reload --host 127.0.0.1 --port 8001
```

### Orientierung für die Übertragung

- Course ist das Vorbild für den Datenbankzugriff auf Student.
- CourseRead zeigt, wie ein Antwortmodell ORM-Attribute liest.
- Die fünf Schülerfelder und NULL bei house bestimmt ihr selbst.
- DbSession stellt die Session bereit; die Route führt die Abfrage aus.

### Aufgaben

1. Legt tag7/practice_schemas.py mit einem Modell StudentRead an.
2. Gebt id, first_name, last_name, house und school_year zurück.
3. Berücksichtigt, dass house in bestehenden Daten NULL sein darf.
4. Erstellt GET /students im Übungsrouter mit DbSession.
5. Sortiert aufsteigend nach der Schüler-ID.
6. Ergänzt GET /students/{student_id} mit positiver Pfad-ID.
7. Liefert 404, wenn eine gültige ID nicht existiert.
8. Prüft beide Routen in Postman. Lest auch einen Schüler mit house: null.

### Erfolgskriterien

- GET {{practice_url}}/students liefert 200 und echte MySQL-Datensätze.
- Die Liste entspricht dem SQL-Bestand, nicht den sechs Speicher-Schülern.
- Ein unbekanntes Haus darf als null in der Antwort erscheinen.
- Die Einzelantwort enthält die fünf vereinbarten Felder.
- ID 0 liefert 422. Eine nachweislich fehlende positive ID liefert 404.
- Das response_model ist für Liste und Einzelabruf angegeben.

<a id="aufgabe-3"></a>

## 3. Haus und Schuljahr gemeinsam filtern

Die Verwaltung sucht Schüler eines Hauses in einem bestimmten Schuljahr.

### Aufgaben

1. Ergänzt an GET /students die optionalen Query-Parameter house und
   school_year.
2. Erlaubt beim Haus nur die vier bekannten, exakt geschriebenen Hausnamen.
3. Erlaubt beim Schuljahr nur Werte von 1 bis 7.
4. Verbindet beide Filter mit UND, wenn beide gesetzt sind.
5. Führt die Filter in SQLAlchemy aus, nicht nachträglich auf Python-Listen.
6. Prüft beide Filter einzeln und gemeinsam.
7. Erklärt, warum ein Schüler mit house: null beim Hausfilter nicht erscheint.

### Prüffälle

| Query | Erwartung |
| --- | --- |
| Keine | Alle vorhandenen Schüler |
| house=Gryffindor | Nur Schüler dieses Hauses |
| school_year=2 | Nur Schüler im zweiten Schuljahr |
| house=Gryffindor&school_year=2 | Unter den Startdaten Ginny |
| house=gryffindor | 422 |
| school_year=8 | 422 |

### Erfolgskriterien

- Die Reihenfolge bleibt nach ID sortiert.
- Ohne Filter werden auch Datensätze mit unbekanntem Haus zurückgegeben.
- Zusätzliche eigene Datensätze werden fachlich korrekt mitgefiltert.
- Es werden gebundene Werte verwendet, keine zusammengesetzten SQL-Texte.

<a id="aufgabe-4"></a>

## 4. Eine vorhandene Buchung umbuchen

Harry möchte vom neuen Übungsangebot zu Alte Runen wechseln.
Die Buchung soll ihre ID und ihr ursprüngliches Buchungsdatum behalten.

- Übertragt die Transaktionsgrenze aus PUT /courses auf die Buchung.
- Überlegt, welche zwei Datensätze vor der Änderung existieren müssen.
- Das erste get gehört bereits in den gemeinsamen begin-Block.
- Eine positive Ziel-ID allein weist noch keinen vorhandenen Kurs nach.

### Aufgaben

1. Erstellt BookingMove in tag7/practice_schemas.py.
2. Es enthält ausschließlich eine erforderliche, positive course_id.
3. Erstellt PATCH /bookings/{booking_id} im Übungsrouter.
4. Prüft Buchung und Zielkurs innerhalb derselben Transaktion.
5. Liefert 404, falls einer der beiden Datensätze fehlt.
6. Ändert nur course_id. Nutzt BookingRead als Antwortmodell.
7. Übernehmt Alte Runens tatsächliche ID aus GET /courses.
8. Sendet den PATCH für booking_one_id mit dieser Ziel-ID.
9. Wiederholt den PATCH mit einer nachweislich fehlenden Zielkurs-ID.
10. Prüft anschließend mit GET /bookings den gespeicherten Zustand.

### Beispielbody

- 3 ist nur dann korrekt, wenn Alte Runen bei euch diese ID hat.

```json
{"course_id": 3}
```

### Erfolgskriterien

- Der gültige PATCH liefert 200 und die neue course_id.
- id, student_id und booking_date sind unverändert.
- Der fehlerhafte PATCH liefert 404 und verändert keine Buchung.
- Ein ungültiger Body liefert 422.
- Die Transaktion beginnt vor dem ersten Datenbankzugriff.
- Ein Fremdschlüsselkonflikt führt nach Rollback zu 409.

<a id="aufgabe-5"></a>

## 5. Eine Buchung entfernen

Ron benötigt seine zusätzliche Übungsbuchung nicht mehr.

### Aufgaben

1. Ergänzt DELETE /bookings/{booking_id} im Übungsrouter.
2. Prüft die positive ID und das Vorhandensein der Buchung.
3. Löscht booking_two_id in einer Transaktion.
4. Liefert bei Erfolg 204 ohne Body.
5. Sendet denselben DELETE erneut und erklärt die Antwort.
6. Prüft, dass Ron, der Kurs und Harrys Buchung weiterhin existieren.

### Erfolgskriterien

- Der erste DELETE liefert 204. Der zweite liefert 404.
- Es wird genau die gewählte Buchung entfernt.
- Schüler und Kurs werden nicht mitgelöscht.
- Harrys verschobene Buchung bleibt bestehen.

<a id="aufgabe-6"></a>

## 6. Ganz-oder-gar-nicht nachweisen

Die Verwaltung will prüfen, ob ein fehlerhafter Sammelauftrag Daten hinterlässt.

### Aufgaben

1. Notiert die IDs aller vorhandenen Buchungen mit GET /bookings.
2. Wählt das zusätzliche Übungsangebot und Harrys tatsächliche Schüler-ID.
3. Bestimmt eine positive Schüler-ID, die nicht vorhanden ist.
4. Sendet POST /booking-batches mit Harry zuerst und der fehlenden ID danach.
5. Vergleicht die Buchungsliste vor und nach dem Auftrag.
6. Erklärt, welche Wirkung flush beim ersten Schüler bereits hatte.
7. Erklärt, warum trotzdem keine neue Buchung vorhanden sein darf.
8. Nennt die Codeänderung, die diesen Schutz versehentlich aufheben würde.
9. Erklärt, warum 404 allein noch kein Nachweis für Rollback ist.

### Erfolgskriterien

- Die Antwort hat Status 404 und nennt den fehlenden Schüler.
- Die Buchungsliste enthält genau dieselben Datensätze wie vorher.
- Ihr könnt Transaktionsgrenze und Rollback im Code zeigen.
- Ihr verwendet die Datensätze als Beleg, nicht den nächsten ID-Zähler.
- Zeigt im Routencode den ersten flush vor der fehlerhaften Prüfung.
- Die bekannte erfolgreiche Gruppenanlage dient als Gegenprobe.
- Ein Commit pro Schleifendurchlauf wird als Fehler erkannt.

### Abgleich mit der vorgegebenen Testdatei

- Ihr schreibt keine eigenen Tests und keine Hilfsfunktionen.
- Der manuelle Vorher-Nachher-Vergleich bleibt der Pflichtnachweis.
- test_batch_saves_all_bookings prüft die erfolgreiche Gruppenanlage.
- test_batch_rolls_back_on_missing_student prüft den Fehlerfall getrennt.
- Beide Tests erzeugen unabhängig voneinander einen eigenen Testkurs.
- Ordnet eure Beobachtungen den beiden Tests zu, falls ihr sie nachlest.
- Erklärt: Warum reicht ein bestandener Fehlertest allein nicht aus?
- Vorbereitung und Aufräumen sind vorgegeben; Fixtures folgen an Tag 8.

<a id="aufgabe-7"></a>

## 7. Migration und erhaltene Daten prüfen

Die Verwaltung möchte belegen, dass die neue Raumspalte keine Daten löscht.

- Ihr untersucht die geführte Migration aus dem Vormittag.
- Ihr müsst keine weitere Migration oder neue Baseline entwerfen.

### Aufgaben

1. Führt alembic current, history und check aus.
2. Öffnet 0001_baseline.py und 0002_course_room.py.
3. Beschreibt die Aufgabe jeder Revision in einem Satz.
4. Lest in beiden Dateien revision und down_revision. Zeichnet daraus die Kette.
5. Vergleicht die Kette mit der Ausgabe von alembic history.
6. Nennt den Unterschied zwischen stamp und upgrade.
7. Prüft in MySQL die Raumspalte und den aktuellen Datenbestand.
8. Prüft mit GET /courses, wie ein fehlender Raum als JSON erscheint.
9. Erklärt den Datenverlust, den downgrade von 0002 verursachen könnte.
10. Führt für diese Aufgabe kein Downgrade aus.

### Befehle

```powershell
python -m alembic current
python -m alembic history
python -m alembic check
docker compose exec db mysql -u dumbledore -p hogwarts
```

<!-- file: sql/tag7/03_exercise_check.sql -->
- Lokal: `.\sql\tag7\03_exercise_check.sql`.

```sql
USE hogwarts;
SELECT version_num FROM alembic_version;
SHOW COLUMNS FROM courses;
SELECT id, title, room FROM courses ORDER BY id;
SELECT id, student_id, course_id, booking_date FROM bookings ORDER BY id;
```

```text
SOURCE /work/sql/tag7/03_exercise_check.sql;
```

### Erfolgskriterien

- Die Datenbank steht auf 0002. check meldet keine neue Upgrade-Operation.
- Eure gezeichnete Kette stimmt mit alembic history überein.
- room ist VARCHAR(30) und nullable.
- Die Änderungen aus Aufgabe 4 und 5 sind weiterhin vorhanden.
- Der Fehlerauftrag aus Aufgabe 6 hat keine neue Buchung erzeugt.
- Ihr unterscheidet Schemaänderung, Datenänderung und Versionsmarkierung.

<a id="aufgabe-8"></a>

## 8. Kontrollfragen beantworten

Beantwortet die Fragen in eigenen Worten. Ein Satz allein reicht nicht,
wenn nach einer Begründung gefragt wird.

1. Was unterscheidet POST, Session.add, flush und commit?
2. Warum ist eine Session kein DB-API-Cursor?
3. Was liefern fetchone und fetchall nach demselben SELECT nacheinander?
4. Wozu dient executemany? Wo liegt die Transaktionsgrenze?
5. Welche Antworten erwartet ihr bei ungültiger ID, fehlender Ressource,
   erfolgreicher Anlage und erfolgreichem Löschen?
6. Wie werden date, None und eine Liste in einer JSON-Antwort dargestellt?
7. Warum müssen Suchwerte als Parameter gebunden werden?
8. Was bleibt gespeichert, wenn der zweite INSERT eines begin-Blocks
   scheitert? Was könnte sich trotzdem am ID-Zähler ändern?
9. Warum ist stamp kein Ersatz für upgrade?
10. Welche dieser Grundlagen sind unabhängig von FastAPI und SQLAlchemy?

### Erfolgskriterien

- Ihr trennt HTTP, ORM, DB-API und Datenbank.
- Eure Antworten erklären das beobachtete Verhalten aus den Aufgaben.
- Ihr könnt Cursor und Transaktionen auch ohne ORM beschreiben.

<a id="aufgabe-9"></a>

## 9. Bonus: Buchungszeitraum als Klassen-Dependency

Die Verwaltung möchte Buchungen nach ihrem Erfassungsdatum auswählen.

### Aufgaben

1. Legt tag7/bonus.py an und übernehmt dort die App aus tag7.practice.
2. Erstellt eine Klasse BookingPeriod mit optionalem start und end.
3. Beide Werte kommen als Datum aus der Query.
4. Liefert 400, wenn start nach end liegt.
5. Bindet die Klasse mit Depends in GET /booking-report ein.
6. Filtert booking_date in SQLAlchemy. Beide Grenzen sind inklusive.
7. Liefert eine nach ID sortierte Liste von BookingRead zurück.
8. Prüft eine einzelne Grenze, beide Grenzen und fehlende Grenzen.

### Erfolgskriterien

- Ohne Grenzen werden alle Buchungen geliefert.
- Gleicher Start und gleiches Ende wählen genau diesen Tag aus.
- start=1993-09-07&end=1993-09-06 liefert 400.
- start=kein-datum liefert 422.
- Die Datumsprüfung steckt in der Dependency, nicht mehrfach in Routen.

<a id="aufgabe-10"></a>

## 10. Bonus: Räume per API setzen und entfernen

Die Verwaltung weist dem zusätzlichen Kurs den Raum „Nordturm“ zu.

### Aufgaben

1. Ergänzt tag7/bonus.py um CourseRoomUpdate.
2. Das Feld room ist erforderlich, darf aber null sein.
3. Entfernt Rand-Leerzeichen. Ein Text braucht danach 1 bis 30 Zeichen.
4. Verbietet zusätzliche Eingabefelder.
5. Erstellt PUT /courses/{course_id}/room mit positiver Pfad-ID.
6. Ändert nur room und liefert CourseRead zurück.
7. Prüft einen gültigen Text, null, fehlendes room und Leerzeichen.
8. Startet den Server neu und prüft die Persistenz eines gesetzten Raums.

### Erfolgskriterien

- Ein gültiger Text ergibt 200. Ein nachfolgender GET zeigt den Raum.
- room: null entfernt die Raumangabe und ergibt 200.
- Ein fehlendes room sowie ein leerer Text ergeben 422.
- Bei unbekanntem Kurs wird 404 geliefert.
- Der Titel und vorhandene Buchungen ändern sich nicht.

### Bonusserver für Aufgabe 9 und 10

```powershell
python -m uvicorn tag7.bonus:app --reload --host 127.0.0.1 --port 8002
```

- In Postman bonus_url auf http://127.0.0.1:8002 setzen.
- Die Bonus-App nutzt denselben MySQL-Bestand wie die anderen Apps.

<a id="aufgabe-11"></a>

## 11. Bonus: Cursor und Transaktionen mit sqlite3

Ihr vergleicht die ORM-Begriffe mit direkten DB-API-Aufrufen.
Dieses kurze Programm verwendet eine eigene SQLite-Datenbank im Speicher.
Es verändert keine Hogwarts-Daten in MySQL.

### Aufgaben

1. Sagt die beiden Ausgabezeilen voraus, bevor ihr das Programm startet.
2. Markiert das erste Commit und das spätere Rollback.
3. Erklärt den Unterschied zwischen execute und executemany.
4. Erklärt, warum fetchall den ersten Datensatz nicht erneut liefert.
5. Prüft eure Vorhersage durch Ausführen des Programms.
6. Ersetzt anschließend nur rollback durch commit. Sagt die neue Ausgabe.
7. Erklärt, warum close nicht das erste Commit ersetzen darf.

<!-- file: tag7/pcpp_cursor.py -->
- Lokal: `.\tag7\pcpp_cursor.py`.

```python
import sqlite3

# Die Hogwarts-API bleibt bei MySQL.
connection = sqlite3.connect(":memory:", autocommit=False)
try:
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE courses (id INTEGER, title TEXT)")
    cursor.executemany(
        "INSERT INTO courses VALUES (?, ?)",
        [(1, "Arithmantik"), (2, "Alte Runen")],
    )
    connection.commit()
    cursor.execute("UPDATE courses SET title = ? WHERE id = ?",
                   ("Flugkunde", 1))
    connection.rollback()
    cursor.execute("SELECT id, title FROM courses ORDER BY id")
    print(cursor.fetchone())
    print(cursor.fetchall())  # Nur die noch nicht gelesenen Zeilen.
finally:
    connection.close()
```

```powershell
python .\tag7\pcpp_cursor.py
```

### Erfolgskriterien

- Im ersten Lauf erscheint weiterhin Arithmantik, nicht Flugkunde.
- fetchall liefert nur die noch nicht gelesene zweite Zeile.
- Nach der Änderung zu commit erscheint Flugkunde.
- Ihr könnt beschreiben, welche Änderungen bestätigt wurden.

