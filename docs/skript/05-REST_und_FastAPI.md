# REST, FastAPI und Hogwarts – Teilnehmerskript

Tag 5 des Kurses „Programmierung mit Python für komplexe Datenbanken“.

- Die Abschnitte folgen der Reihenfolge des Unterrichts.
- Ausgangspunkt ist der vollständige Live-Stand aus [Tag 4][tag4].
- Heute werden die bekannten Kurse über eine HTTP-Schnittstelle erreichbar.
- Jeder vollständige Codeblock nennt seine Datei und den passenden Aufruf.
- Pflichtprüfungen erfolgen mit Postman. Zwei GET-Tests sind vorgegeben.
- Die freiwilligen Vertiefungen sind ausdrücklich gekennzeichnet.

## Ziel des Tages

- Eine HTTP-Anfrage und ihre Antwort erklären.
- Ressourcen, Pfade und Methoden unterscheiden.
- JSON lesen und von einem Python-Dictionary unterscheiden.
- Einen Entwicklungsserver mit der ersten FastAPI-App starten.
- Kurse als Sammlung und als einzelne Ressource ausgeben.
- Einen Query-Parameter für die Titelsuche verwenden.
- Einen Kurs mit POST und einem JSON-Body anlegen.
- Eingabe- und Antwortmodelle unterscheiden.
- Statuscodes und Antwortinhalte gemeinsam prüfen.
- Zwei vorgegebene Tests lesen, ausführen und erklären.

Die Hogwarts-Verwaltung besitzt bereits SQL-Auswertungen und Python-Berichte.
Jetzt soll ein Client Kursdaten abrufen können, ohne Python-Code zu kennen.
Du entwickelst dafür eine kleine API mit ausdrücklich benannten Endpunkten.
Der Pflichtteil hält seine Kurse vorübergehend im Arbeitsspeicher.
Eine freiwillige Erweiterung macht die echten Berichte aus Tag 4 erreichbar.

## HTTP und FastAPI auf einen Blick

| Du möchtest … | Werkzeug | Abschnitt |
|---|---|---|
| die Operation einer Anfrage bestimmen | HTTP-Methode | 1 |
| ein Angebot ansprechen | Pfad /courses/{course_id} | 4 |
| eine Sammlung durchsuchen | Query-Parameter q | 5 |
| Daten als Text austauschen | JSON | 1, 6 |
| die App ausführen | Uvicorn | 2 |
| eine Route registrieren | @app.get oder @app.post | 2–6 |
| ungültige Eingaben erkennen | Typangaben und Pydantic | 4, 6 |
| einen fehlenden Kurs melden | HTTPException mit 404 | 4 |
| neue Daten entgegennehmen | Request-Modell CourseCreate | 6 |
| die Ausgabe festlegen | response_model und CourseRead | 6 |
| Schnittstellen nachlesen | Swagger UI und OpenAPI | 7 |
| Antworten automatisch vergleichen | TestClient und assert | 7 |
| echte Berichte über HTTP lesen | tag4.reports, freiwillig | 11 |

> **💡 Merke: HTTP-Vertrag und Speicherung sind verschiedene Fragen**
> Eine Route legt fest, welche Anfrage welche Antwort liefert.
> Der Speicherort wird durch den Anwendungscode bestimmt.
> Ein erfolgreicher POST bedeutet heute noch keinen INSERT in MySQL.



## 1. Ressourcen, HTTP und JSON verstehen

Eine Kollegin möchte Alte Runen lesen, ohne ein Python-Skript auszuführen.
Ihr Client schickt dafür eine Anfrage an den Server.
Der Server verarbeitet sie und schickt eine Antwort zurück.

![HTTP-Anfrage und Antwort][http-svg]

### 1.1 Eine Ressource und ihre Operation unterscheiden

- Eine Ressource ist hier ein Kurs oder eine Sammlung von Kursen.
- /courses bezeichnet die Sammlung. /courses/3 bezeichnet einen Kurs.
- Ein Endpunkt wird durch HTTP-Methode und Pfad bestimmt.
- GET /courses und POST /courses haben andere Aufgaben am gleichen Pfad.
- Browser, Postman und Swagger UI können als Clients arbeiten.
- REST ist ein Architekturstil. HTTP stellt Methoden und Statuscodes bereit.
- Unsere Pfade benennen Ressourcen. Die Methode beschreibt die Operation.
- Jeder Aufruf enthält die Angaben, die für seine Bearbeitung nötig sind.
- Der Server darf den Zustand seiner Ressourcen trotzdem speichern.

| Methode | Bedeutung im Kursprojekt | Beispiel |
|---|---|---|
| GET | Angebote lesen | GET /courses |
| POST | Ein neues Angebot anlegen | POST /courses |
| PUT | Ein Angebot vollständig ersetzen | PUT /courses/3 |
| PATCH | Einzelne Angaben ändern | PATCH /courses/3 |
| DELETE | Ein Angebot entfernen | DELETE /courses/3 |

Heute implementierst du GET und POST.
PUT und PATCH dienen zunächst der Einordnung. DELETE gehört zum Bonus.

> **💡 Merke: GET liest den fachlichen Bestand**
> Ein Abruf soll keine neue Buchung oder Kursanlage auslösen.
> Wiederholtes POST kann dagegen mehrere Ressourcen anlegen.
> Idempotenz meint die gleiche beabsichtigte Wirkung bei Wiederholung.
> Sie verlangt keine identischen Statuscodes bei jedem Aufruf.

### 1.2 Eine Anfrage lesen

```http
GET /courses/3 HTTP/1.1
Host: 127.0.0.1:8000
Accept: application/json
```

| Bestandteil | Bedeutung |
|---|---|
| GET | Gewünschte Operation |
| /courses/3 | Pfad zur Ressource |
| HTTP/1.1 | Protokollversion dieses Beispiels |
| Host | Serveradresse einschließlich Port |
| Accept | Vom Client gewünschtes Antwortformat |
| Content-Type | Format eines tatsächlich gesendeten Bodys |

- Die vollständige URL lautet http://127.0.0.1:8000/courses/3.
- 127.0.0.1 bezeichnet den eigenen Rechner.
- 8000 ist der Port des heutigen Kursservers.
- Ein POST erhält zusätzlich einen Body mit den neuen Kursdaten.

### 1.3 JSON als Austauschformat

```json
{"id": 3, "title": "Alte Runen"}
```

- JSON ist ein Textformat. Ein Python-Dictionary ist ein Python-Objekt.
- JSON-Objekte verwenden geschweifte Klammern, Arrays eckige Klammern.
- Schlüssel und Zeichenketten stehen in doppelten Anführungszeichen.
- JSON kennt Zahlen, Zeichenketten, Objekte, Arrays, true, false und null.
- Python verwendet dafür unter anderem True, False und None.
- Ein Datum wird später als vereinbarte Zeichenkette übertragen.
- FastAPI wandelt passende Python-Rückgabewerte in eine JSON-Antwort um.

> **⚠️ Pitfall: JSON von Hand zusammenbauen**
> Gib ein Dictionary oder eine Liste zurück, keine selbst gebaute JSON-Zeile.
> Sonst kann der Text als Zeichenkette statt als Objekt ausgegeben werden.
> Ein JSON-Fehlertext allein setzt noch keinen passenden HTTP-Status.

### Kleine Übertragung

1. Plane einen Aufruf zum Lesen aller Schüler.
2. Plane einen Aufruf zum Anlegen eines Schülers.
3. Benenne Methode, Pfad und gegebenenfalls den Body.

<details>
<summary>Erwartung</summary>

GET /students liest die Sammlung.
POST /students übermittelt die neuen Schülerdaten im JSON-Body.
Die API vergibt die ID. Methode und Pfad bestimmen gemeinsam die Operation.

</details>

- [Aufgabe 1][a1] ergänzt daraus einen überprüfbaren API-Vertrag.

## 2. FastAPI starten und die erste Antwort lesen

Die Verwaltung braucht zunächst einen erreichbaren API-Prozess.
Ein kleiner Health-Endpunkt bestätigt, dass die App antwortet.

### 2.1 Die vorhandene Umgebung ergänzen

Datei `requirements-tag5.txt`:

<!-- file: requirements-tag5.txt -->

```text
-r requirements-tag3.txt
fastapi==0.143.0
uvicorn==0.54.0
pydantic==2.14.1
starlette==1.7.0
httpx2==2.13.1
pytest==9.1.1
```

```powershell
python -m pip install -r .\requirements-tag5.txt
python -m pip check
python -m pip show fastapi uvicorn pydantic starlette httpx2 pytest
python -m pip freeze > .\requirements-tag5-lock.txt
```

- Die Versionen entsprechen dem Dozentenskript von Tag 5.
- requirements-tag3.txt bringt die vorhandenen Datenbankpakete mit.
- FastAPI beschreibt Routen und verarbeitet passende Anfragen.
- Uvicorn führt die App als Server aus.
- Pydantic beschreibt und prüft Datenmodelle.
- Starlette liefert die HTTP-Grundlage.
- Der hier verwendete TestClient nutzt httpx2.
- pytest führt die vorgegebenen Python-Tests aus.
- Die Lockdatei hält die tatsächlich installierten Pakete fest.

### 2.2 Die erste App anlegen

Datei `tag5\main.py`:

<!-- file: tag5/main.py -->

```python
from fastapi import FastAPI

app = FastAPI(title="Hogwarts-Kursverwaltung")


@app.get("/health")
def read_health():
    return {"status": "ok"}
```

```powershell
python -m uvicorn tag5.main:app --reload --host 127.0.0.1 --port 8000
```

- Starte den Befehl im gemeinsamen Projektordner hogwarts-sql.
- tag5.main bezeichnet das Modul tag5/main.py.
- app nach dem Doppelpunkt ist die FastAPI-Instanz in diesem Modul.
- @app.get registriert die nachfolgende Funktion für GET /health.
- Der Funktionsname read_health ist kein öffentlicher URL-Pfad.
- --reload startet nach Codeänderungen mit neu geladenem Zustand.
- Das Terminal bleibt für den Server belegt. Strg+C beendet ihn.
- Für weitere Befehle öffnest du eine zweite PowerShell im selben Projekt.
- Normale def-Funktionen genügen für diesen Einstieg.

Die [offiziellen ersten Schritte][first] ergänzen die Erklärung der App.
Die Startbefehle dieses Kurses verwenden weiterhin pip und Uvicorn.

### 2.3 Mit Postman anfragen

1. Öffne Postman und erstelle einen Request mit der Methode GET.
2. Trage http://127.0.0.1:8000/health ein und klicke auf Send.
3. Betrachte Status, Antwort-Headers und JSON-Body getrennt.
4. Importiere danach die [Collection für Tag 5][postman].
5. Öffne darin „01 Kurse → Health prüfen“ und sende denselben Aufruf.

<details>
<summary>Erwartung</summary>

Status 200, Content-Type application/json und dieser Body:

```json
{"status": "ok"}
```

Im Browser zeigt dieselbe URL ebenfalls die JSON-Antwort.
Der Health-Endpunkt prüft heute keine Datenbankverbindung.

</details>

Die Collection liegt bei den Kursmaterialien unter docs/postman.
Wähle in Postman Import und die heruntergeladene JSON-Datei.
Die Collection heißt „Tag 5 – Hogwarts“.

| Collection-Variable | Verwendung |
|---|---|
| base_url | http://127.0.0.1:8000 für die Kurs-App |
| practice_url | http://127.0.0.1:8001 für die Schülerübungen |
| reports_url | http://127.0.0.1:8002 für den Datenbank-Bonus |
| created_course_id | Antwort-ID nach erfolgreichem Kurs-POST |
| created_student_id | Antwort-ID nach erfolgreichem Schüler-POST |
| empty_course_id | Tatsächliche ID des leeren Kurses im Datenbank-Bonus |

- {{base_url}} im Request wird durch die Collection-Variable ersetzt.
- Ein zusätzliches Postman-Environment ist nicht erforderlich.
- Sende Requests einzeln, sobald ihre Route implementiert ist.
- Spätere und freiwillige Requests sind bereits enthalten.
- Bei Suchanfragen findest du Query-Werte unter Params.
- Bei POST verwendest du Body → raw → JSON.

> **⚠️ Pitfall: Die gesamte Collection sofort ausführen**
> Noch nicht entwickelte Routen liefern erwartbar Fehler.
> Jeder POST-Aufruf kann außerdem einen neuen Speichereintrag erzeugen.
> Wähle deshalb nur den Request für deinen aktuellen Unterrichtsschritt.

- [Aufgabe 2][a2] überträgt diesen Start auf eine eigene Schüler-App.

### Den ersten Zwischenstand sichern

```powershell
git status --short
git add -- requirements-tag5.txt requirements-tag5-lock.txt
git add -- tag5/main.py
git diff --cached --check
git diff --cached
git commit -m "Ersten Hogwarts-Endpunkt mit FastAPI bereitstellen"
```

## 3. Die Kursangebote als Sammlung ausgeben

Die Verwaltung möchte alle Angebote sehen.
Ein Listenelement steht für einen Kurs, nicht für eine Buchung.

### Den Speicherbestand anlegen

Datei `tag5\data.py`:

<!-- file: tag5/data.py -->

```python
courses = {
    1: {"id": 1, "title": "Arithmantik"},
    2: {"id": 2, "title": "Wahrsagen"},
    3: {"id": 3, "title": "Alte Runen"},
    4: {"id": 4, "title": "Pflege magischer Geschöpfe"},
    5: {"id": 5, "title": "Zaubertrankpraxis"},
}
```

- Das äußere Dictionary ermöglicht den Zugriff über eine ID.
- Jeder innere Eintrag enthält die Antwortfelder id und title.
- Diese fünf IDs gehören nur zu unserem heutigen Speicherbeispiel.
- Zaubertrankpraxis muss in MySQL nicht die ID 5 haben.

### Die vollständige App ersetzen

Ersetze tag5/main.py durch diesen Stand.
Der Health-Endpunkt bleibt erhalten und die Kursliste kommt hinzu.

Datei `tag5\main.py`:

<!-- file: tag5/main.py -->

```python
from fastapi import FastAPI

from tag5.data import courses

app = FastAPI(title="Hogwarts-Kursverwaltung")


@app.get("/health")
def read_health():
    return {"status": "ok"}


@app.get("/courses")
def read_courses():
    return [courses[key] for key in sorted(courses)]
```

Sende in Postman „01 Kurse → Alle Kurse lesen“.
Das entspricht GET /courses auf dem laufenden Kursserver.

<details>
<summary>Erwartung</summary>

Status 200 und eine Liste mit fünf Kursobjekten.
Ihre IDs sind in dieser Speicher-App 1, 2, 3, 4 und 5.
Jedes Objekt enthält id und title.
Ein erneuter GET verändert weder Anzahl noch Inhalt.

</details>

- sorted(courses) sortiert die Schlüssel des Dictionaries.
- courses[key] liefert das zugehörige Kursobjekt.
- Die List Comprehension bildet daraus die vereinbarte Sammlung.

> **⚠️ Pitfall: Nur die Dictionary-Schlüssel zurückgeben**
> Eine Liste aus courses allein enthält die IDs.
> Der Client braucht hier die vollständigen Kursobjekte mit Titel.

### Kleine Übertragung

1. Sende GET /courses zweimal.
2. Vergleiche Anzahl und Felder der Ergebnisse.
3. Erkläre, weshalb der Body eine Liste statt eines einzelnen Objekts ist.

- [Aufgabe 3][a3] entwickelt später eine Sammlung von Schülern.

## 4. Einen Kurs gezielt lesen und Fehler unterscheiden

Eine Kollegin fragt nach Kurs 3.
Ein fehlender Kurs soll von einer ungültigen Eingabe unterscheidbar sein.

### Die vollständige App erweitern

Ersetze tag5/main.py durch die folgende Fassung.
Sie ergänzt eine einzelne Ressource und die passende Fehlermeldung.

Datei `tag5\main.py`:

<!-- file: tag5/main.py -->

```python
from fastapi import FastAPI, HTTPException

from tag5.data import courses

app = FastAPI(title="Hogwarts-Kursverwaltung")


@app.get("/health")
def read_health():
    return {"status": "ok"}


@app.get("/courses")
def read_courses():
    return [courses[key] for key in sorted(courses)]


@app.get("/courses/{course_id}")
def read_course(course_id: int):
    course = courses.get(course_id)
    if course is None:
        raise HTTPException(status_code=404, detail="Kurs nicht gefunden.")
    return course
```

- {course_id} übernimmt einen variablen Teil aus dem URL-Pfad.
- course_id: int verlangt einen als Ganzzahl lesbaren Wert.
- courses.get liefert das Kursobjekt oder None, falls die ID fehlt.
- raise HTTPException beendet diesen Ablauf mit dem angegebenen HTTP-Status.
- detail erscheint als Feld in der JSON-Fehlerantwort.

| Request in „01 Kurse“ | Aufruf | Status |
|---|---|---:|
| Alte Runen lesen | GET /courses/3 | 200 |
| Fehlende Kurs-ID | GET /courses/999 | 404 |
| Text als Kurs-ID | GET /courses/AlteRunen | 422 |
| DELETE ohne Implementierung | DELETE /courses/3 | 405 |
| Unbekannter Pfad | GET /unknown | 404 |

<details>
<summary>Erwartung</summary>

Kurs 3 liefert {"id": 3, "title": "Alte Runen"}.
Die fehlende ID liefert {"detail": "Kurs nicht gefunden."} mit 404.
Der Textwert kann nicht als int gelesen werden und ergibt 422.
DELETE ist für diesen Pfad nicht implementiert und ergibt 405.
Die Fehleraufrufe verändern die Kurssammlung nicht.

</details>

> **💡 Merke: 404 und 422 beantworten unterschiedliche Fragen**
> 404 bedeutet hier: Die angefragte Ressource fehlt.
> 422 bedeutet hier: Die Eingabe passt nicht zum erwarteten Format.
> Eine gültige Ganzzahl beweist noch nicht, dass ein Kurs existiert.

> **⚠️ Pitfall: Den Status nur in den Body schreiben**
> Ein Dictionary mit status_code 404 setzt noch keinen HTTP-Status.
> Verwende raise HTTPException und prüfe den Status in Postman.
> Gib die Exception nicht mit return zurück.

### Kleine Übertragung

1. Lies Kurs 2 und prüfe den Titel.
2. Frage eine fehlende numerische ID und danach einen Textwert ab.
3. Begründe die drei unterschiedlichen Antworten.

<details>
<summary>Erwartung</summary>

GET /courses/2 liefert Wahrsagen mit 200.
Die fehlende ID ergibt 404. Der Textwert ergibt 422.
Eine vorhandene GET-Route stellt DELETE nicht automatisch bereit.

</details>

- [Aufgabe 3][a3] überträgt den Einzelabruf auf Schüler.
- [Aufgabe 7][a7] sammelt die verschiedenen Fehlerfälle im Prüfprotokoll.

### Sammlung und Einzelabruf sichern

```powershell
git add -- tag5/data.py tag5/main.py
git diff --cached --check
git commit -m "Kursliste und einzelne Kurse per HTTP lesen"
```

## 5. Eine Titelsuche mit Query-Parameter anbieten

Die Verwaltung kennt einen Teil des Kurstitels, aber noch keine ID.
Du ergänzt eine Auswahl innerhalb der Kurssammlung.

### Die vollständige App ersetzen

Datei `tag5\main.py`:

<!-- file: tag5/main.py -->

```python
from fastapi import FastAPI, HTTPException

from tag5.data import courses

app = FastAPI(title="Hogwarts-Kursverwaltung")


@app.get("/health")
def read_health():
    return {"status": "ok"}


@app.get("/courses")
def read_courses(q: str | None = None):
    rows = [courses[key] for key in sorted(courses)]
    if q is not None:
        rows = [row for row in rows if q.casefold() in row["title"].casefold()]
    return rows


@app.get("/courses/{course_id}")
def read_course(course_id: int):
    course = courses.get(course_id)
    if course is None:
        raise HTTPException(status_code=404, detail="Kurs nicht gefunden.")
    return course
```

- q steht nicht im Pfadmuster und wird hier zum Query-Parameter.
- q: str | None = None erlaubt einen fehlenden Suchwert.
- Ohne q liefert die Route alle Kurse.
- casefold gleicht die Groß- und Kleinschreibung für den Vergleich an.
- in prüft hier einen Teilstring innerhalb eines Python-Strings.
- Das ist eine Suche im Speicher, keine SQL-Abfrage.

| Aufruf | Erwartung bei fünf Startkursen |
|---|---|
| GET /courses | Fünf Objekte |
| GET /courses?q=RUNEN | Eine Liste mit Alte Runen |
| GET /courses?q=Quidditch | Leere Liste |
| GET /courses?q= | Fünf Objekte |

Sende die passenden Suchrequests im Postman-Ordner „01 Kurse“.
Alle vier Aufrufe liefern Status 200.

<details>
<summary>Erwartung</summary>

Für RUNEN kommt [{"id": 3, "title": "Alte Runen"}].
Für Quidditch kommt []. Die Sammlung existiert weiterhin.
Der leere String ist in jedem Titel enthalten und findet deshalb alle Kurse.
Auch genau ein Suchtreffer bleibt ein Element einer Liste.

</details>

> **⚠️ Pitfall: Eine leere Auswahl als fehlende Ressource behandeln**
> GET /courses?q=Quidditch ist eine gültige Suche ohne Treffer.
> GET /courses/999 fragt dagegen nach einem bestimmten, fehlenden Kurs.
> Deshalb liefert die Suche 200 mit [] und der Einzelabruf 404.

### Kleine Übertragung

1. Suche mit q=WAHR nach Wahrsagen.
2. Wähle einen eigenen Suchtext ohne Treffer.
3. Vergleiche die Form der beiden Antwort-Bodys.

- [Aufgabe 4][a4] überträgt das Muster auf einen exakten Hausfilter.
- Dort ist der vollständige Hausname gefragt, kein Teilstring.

## 6. Einen Kurs mit POST und JSON anlegen

Die Verwaltung möchte Astronomie als zusätzliches Angebot aufnehmen.
Der Client übermittelt den Titel. Die API vergibt die neue ID.

### 6.1 Eingabe und Antwort unterscheiden

| Modell | Felder | Aufgabe |
|---|---|---|
| CourseCreate | title | Eingabe für die Anlage prüfen |
| CourseRead | id, title | Antwort auf Kursanfragen beschreiben |

- BaseModel ist die Grundlage für ein Pydantic-Modell.
- Field begrenzt hier die Titellänge auf 1 bis 100 Zeichen.
- CourseCreate verlangt einen Titel, aber keine vom Client vergebene ID.
- CourseRead enthält zusätzlich die serverseitige ID.
- Ein Pydantic-Schema legt keine MySQL-Tabelle an.
- Die SQLAlchemy-Modelle aus Tag 3 bleiben davon getrennt.
- Ein Body-Modell wird aus dem JSON der Anfrage erzeugt und geprüft.
- Bei ungültiger Eingabe wird unsere Anlagefunktion nicht ausgeführt.

Datei `tag5\schemas.py`:

<!-- file: tag5/schemas.py -->

```python
from pydantic import BaseModel, Field


class CourseCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)


class CourseRead(BaseModel):
    id: int
    title: str
```

Das [FastAPI-Kapitel zum Request-Body][body] erklärt diesen Ablauf ergänzend.
Im heutigen Beispiel beschränken wir uns auf den Kurstitel.

> **⚠️ Pitfall: Mehr Validierung erwarten, als programmiert wurde**
> min_length=1 lehnt einen leeren String ab.
> Ein String nur aus Leerzeichen ist damit noch nicht ausgeschlossen.
> Zusätzliche Normalisierung und strengere Feldregeln folgen an Tag 6.

### 6.2 Die vollständige Kurs-App zusammenführen

Ersetze tag5/main.py vollständig durch diesen Stand.
Er enthält alle Routen des Vormittags und benötigt keine Übungslösung.
Die Dateien data.py und schemas.py aus den vorigen Abschnitten bleiben bestehen.

Datei `tag5\main.py`:

<!-- file: tag5/main.py -->

```python
from itertools import count

from fastapi import FastAPI, HTTPException

from tag5.data import courses
from tag5.schemas import CourseCreate, CourseRead

app = FastAPI(
    title="Hogwarts-Kursverwaltung",
    description="Lern-API mit vorübergehendem Speicherbestand.",
    version="0.1.0",
)
course_ids = count(6)


@app.get("/health")
def read_health():
    return {"status": "ok"}


@app.get("/courses", response_model=list[CourseRead])
def read_courses(q: str | None = None):
    rows = [courses[key] for key in sorted(courses)]
    if q is not None:
        rows = [row for row in rows if q.casefold() in row["title"].casefold()]
    return rows


@app.get("/courses/{course_id}", response_model=CourseRead)
def read_course(course_id: int):
    course = courses.get(course_id)
    if course is None:
        raise HTTPException(status_code=404, detail="Kurs nicht gefunden.")
    return course


@app.post("/courses", response_model=CourseRead, status_code=201)
def create_course(course: CourseCreate):
    course_id = next(course_ids)
    created = {"id": course_id, "title": course.title}
    courses[course_id] = created
    return created
```

- count(6) erzeugt im neuen Prozess die IDs 6, 7, 8 und so weiter.
- next(course_ids) liefert die nächste ID für genau diese App.
- course.title enthält den von Pydantic geprüften Titel.
- created ist das neue Kursobjekt mit ID und Titel.
- Die Zuweisung in courses speichert es im Python-Prozess.
- status_code=201 kennzeichnet die erfolgreiche Anlage.
- response_model prüft und beschreibt die Struktur der Antwort.
- list[CourseRead] liefert eine Sammlung, CourseRead ein einzelnes Objekt.
- title, description und version beschreiben die API in ihrer Dokumentation.

### 6.3 Den Anfrage-Body senden

Datei `tag5\new_course.json`:

<!-- file: tag5/new_course.json -->

```json
{
  "title": "Astronomie"
}
```

1. Öffne in Postman „01 Kurse → Astronomie anlegen“.
2. Prüfe die Methode POST und die URL {{base_url}}/courses.
3. Wähle Body → raw → JSON und vergleiche den Body mit der Datei.
4. Sende den Request einmal und notiere Status und Antwort-ID.
5. Sende danach „Angelegten Kurs lesen“ und „Alle Kurse lesen“.

- Die JSON-Datei dient als Vorlage. Postman liest sie nicht automatisch.
- JSON als Body-Format setzt den passenden Content-Type application/json.
- Das vorbereitete Post-response-Skript merkt sich die Antwort-ID.
- Der Folge-GET verwendet dafür {{created_course_id}}.

<details>
<summary>Erwartung</summary>

Nach einem frischen Serverstart liefert der erste POST Status 201.

```json
{"id": 6, "title": "Astronomie"}
```

GET /courses/6 liefert dasselbe Objekt mit Status 200.
Die Kurssammlung enthält jetzt sechs Angebote.
Ein weiterer POST erzeugt einen weiteren Kurs mit einer neuen ID.

</details>

> **💡 Merke: Die Antwort-ID gehört zum aktuellen Speicherstand**
> Verwende nach weiteren Anlagen die tatsächlich zurückgegebene ID.
> Neustart und Reload setzen das Dictionary und den Zähler zurück.
> Ein Kurs aus einem früheren Prozess existiert danach nicht automatisch.

### 6.4 Ungültige Eingaben prüfen

Sende „Kurs ohne Pflichtfeld“ und „Kurs mit leerem Titel“ in Postman.
Die jeweiligen Bodys sind {} und {"title": ""}.

<details>
<summary>Erwartung</summary>

Beide Aufrufe liefern 422.
Die Antwort nennt unter detail den Eingabefehler.
Die Kurszahl bleibt gleich, weil kein neuer Kurs gespeichert wird.
Die genaue Standardfehlermeldung kann sich zwischen Versionen unterscheiden.

</details>

- Ein GET im Browser sendet keinen POST-Body für eine Kursanlage.
- Der Titel gehört in den JSON-Body, nicht in einen Query-Parameter.
- Die Ressource wird heute nur im Speicher angelegt.
- MySQL bleibt bei zehn Schülern, fünf Kursen und neun Buchungen.
- [Aufgaben 5–6][a5] übertragen Eingabeschema und Anlage auf Schüler.

### Lesen, Suchen und Anlegen sichern

```powershell
git add -- tag5/main.py tag5/schemas.py tag5/new_course.json
git diff --cached --check
git diff --cached
git commit -m "Kurse per JSON anlegen und Antworten beschreiben"
```

## 7. Dokumentation und zwei vorgegebene Tests verwenden

Die Verwaltung braucht eine nachvollziehbare Beschreibung der Schnittstelle.
Du vergleichst sie mit den Antworten deiner App.

### 7.1 Swagger UI und OpenAPI öffnen

| URL | Inhalt |
|---|---|
| http://127.0.0.1:8000/docs | Interaktive Swagger UI |
| http://127.0.0.1:8000/redoc | Alternative Dokumentationsansicht |
| http://127.0.0.1:8000/openapi.json | Maschinenlesbare API-Beschreibung |

- OpenAPI beschreibt unter anderem Pfade, Methoden und Datenschemas.
- Swagger UI stellt diese Beschreibung als bedienbare Oberfläche dar.
- Öffne GET /courses und lies Parameter sowie mögliche Antworten.
- Öffne POST /courses und vergleiche CourseCreate mit CourseRead.
- Die Eingabe verlangt title. Die Antwort enthält außerdem id.
- „Try it out“ führt echte Requests gegen die laufende App aus.
- Auch ein POST aus Swagger UI legt deshalb einen weiteren Speicherkurs an.

> **⚠️ Pitfall: Dokumentation für eine Simulation halten**
> Ein Aufruf über Swagger UI nutzt dieselben Routen wie Postman.
> Zusätzliche implementierete POSTs Routen verändern daher die erwartete Anzahl der Kurse.

### 7.2 Zwei GET-Tests gemeinsam nachvollziehen

Heute erhältst du zwei vollständige Tests als Muster.
Lies sie, führe sie aus und erkläre die Vergleiche.
Eigene Tests im Nachmittagsblatt sind eine freiwillige Übertragung.

Datei `tag5\test_main.py`:

<!-- file: tag5/test_main.py -->

```python
from fastapi.testclient import TestClient

from tag5.main import app

client = TestClient(app)


def test_read_course():
    response = client.get("/courses/1")
    assert response.status_code == 200
    assert response.json() == {"id": 1, "title": "Arithmantik"}


def test_missing_course():
    response = client.get("/courses/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Kurs nicht gefunden."}
```

```powershell
python -m pytest -q tag5/test_main.py
```

- pytest findet Funktionen, deren Namen mit test_ beginnen.
- TestClient verwendet die importierte FastAPI-App direkt.
- client.get erzeugt den Request für den angegebenen Pfad.
- response.status_code liefert den HTTP-Status.
- response.json() liest den JSON-Body als Python-Datenstruktur.
- assert vergleicht das beobachtete Ergebnis mit der Erwartung.
- Beide Tests lesen nur und verändern den Speicherbestand nicht.
- Der geöffnete Uvicorn-Server wird durch diese Tests nicht angesprochen.
- Der pytest-Prozess importiert seinen eigenen frischen App-Bestand.

<details>
<summary>Erwartung</summary>

Zwei Tests bestehen.
Der erste prüft Status und vollständiges Kursobjekt für Arithmantik.
Der zweite prüft 404 und die vereinbarte Meldung für einen fehlenden Kurs.

</details>

Das [FastAPI-Testing-Tutorial][testing] beschreibt TestClient ergänzend.
Fixtures, Testisolation und eigener Testentwurf folgen später im Kurs.

### Kleine Übertragung

1. Ändere im ersten Test vorübergehend den erwarteten Titel auf Wahrsagen.
2. Führe den Test erneut aus und lies den Vergleich in der Fehlermeldung.
3. Stelle Arithmantik wieder her und führe beide Tests erneut aus.

<details>
<summary>Erwartung</summary>

Mit der falschen Erwartung scheitert der erste Test.
Die tatsächliche Antwort enthält weiterhin Arithmantik.
Nach der Korrektur bestehen wieder beide Tests.

</details>

- [Aufgabe 8][a8] überträgt genau dieses GET-Muster freiwillig auf Schüler.
- Die verpflichtende Prüfung am Nachmittag erfolgt mit Postman.

