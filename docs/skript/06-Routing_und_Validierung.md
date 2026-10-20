# Routing und Validierung – Teilnehmerskript

Tag 6 des Kurses „Programmierung mit Python für komplexe Datenbanken“.

Die Hogwarts-Verwaltung möchte ungültige Kursanfragen früh erkennen.
Du ergänzt die API aus [Tag 5][tag5] um klare Ein- und Ausgaberegeln.

- Die Kurse liegen heute im Arbeitsspeicher des jeweiligen Prozesses.
- Neustart und Reload setzen den Bestand zurück. MySQL bleibt unverändert.
- Die Datenbankanbindung folgt an Tag 7.

## Das brauchst du heute

| Frage | Werkzeug | Abschnitt |
| --- | --- | --- |
| Woher kommt ein Wert? | Pfad, Query, JSON-Body | 1 |
| Ist die ID gültig? | Annotated und Path | 2 |
| Ist die Suche gültig? | Query und Standardwert | 3 |
| Sind die Eingabedaten erlaubt? | Pydantic und Validator | 4 |
| Welche Felder gehen nach außen? | response_model | 5 |
| Wie ordnen wir Endpunkte? | APIRouter und include_router | 6 |
| Bleibt das Verhalten korrekt? | Postman, TestClient, assert | 7–8 |

> **Merke:** Eingabeprüfung, Datenspeicherung und Antwort sind eigene Schritte.
> Ein gültiger Request erzeugt hier noch keinen Datensatz in MySQL.

## 0. Die Kurs-API von Tag 5 übernehmen

### Umgebung und Startdateien


- Die vorhandenen Paketversionen aus requirements-tag5.txt weiterverwenden.
- Falls die Aktivierung blockiert ist, das venv-Python direkt verwenden:

```powershell
.\.venv\Scripts\python.exe --version
```

- In den folgenden Befehlen dann diesen Pfad statt python verwenden.

Datei `tag6/data.py`:

<!-- file: tag6/data.py -->
```python
from itertools import count

# Eigene Kopie von Tag 5. Daten und Zähler leben nur in diesem Prozess.
# Kein MySQL-Zugriff; der Zähler bleibt beim Router-Umbau hier in data.py.
courses = {
    1: {"id": 1, "title": "Arithmantik"},
    2: {"id": 2, "title": "Wahrsagen"},
    3: {"id": 3, "title": "Alte Runen"},
    4: {"id": 4, "title": "Pflege magischer Geschöpfe"},
    5: {"id": 5, "title": "Zaubertrankpraxis"},
}
course_ids = count(6)
```

Datei `tag6/schemas.py` – zunächst der bekannte Startstand:

<!-- file: tag6/schemas.py -->
```python
from pydantic import BaseModel, Field


class CourseCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)


class CourseRead(BaseModel):
    id: int
    title: str
```

Datei `tag6/main.py` – zunächst ohne Router-Auslagerung:

<!-- file: tag6/main.py -->
```python
from fastapi import FastAPI, HTTPException

from tag6.data import course_ids, courses
from tag6.schemas import CourseCreate, CourseRead

app = FastAPI(title="Hogwarts-Kursverwaltung", version="0.2.0")


@app.get("/health")
def read_health():
    return {"status": "ok"}


@app.get("/courses", response_model=list[CourseRead])
def read_courses(q: str | None = None):
    rows = [courses[key] for key in sorted(courses)]
    if q is not None:
        rows = [r for r in rows if q.casefold() in r["title"].casefold()]
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

### Server und Postman

```powershell
python -m uvicorn tag6.main:app --reload --host 127.0.0.1 --port 8000
```

- Uvicorn bleibt im Terminal geöffnet; Git und pytest laufen im zweiten.
- Swagger UI: `http://127.0.0.1:8000/docs`.
- In Postman die [Collection „Tag 6 – Hogwarts“][postman] importieren.
- Query-Werte: Params. JSON-Body: Body → raw → JSON.

| Collection-Ordner | App und Zeitpunkt |
| --- | --- |
| 00 Startstand aus Tag 5 | Vor den neuen Regeln; base_url, Port 8000. |
| 01 Kurse – Pflicht | Nach dem jeweiligen Ausbau; base_url, Port 8000. |
| 02 Schüler – Pflicht | Nachmittagsübungen; practice_url, Port 8001. |
| 03 Kursbonus | tag6.bonus:app; bonus_url, Port 8002. |
| 04 Schülerbonus | tag6.practice_bonus:app; bonus_url, Port 8002. |

- Collection-Variablen enthalten jeweils `http://127.0.0.1:<Port>`.
- Zuerst GET /health, GET /courses und GET /courses/3 prüfen.
- Erwartet: 200, fünf Kurse und Alte Runen. /courses/999 liefert 404.

> **⚠️ Pitfall: falscher Server oder alter Speicherbestand**
> Prüfe App-Modul und Port. Ein gespeicherter Postman-ID-Wert erzeugt
> keine Daten.
> Nach einem Neustart einen Kurs erneut anlegen, bevor du seine neue ID liest.
> Sende Requests passend zum Ausbaustand; nicht die ganze Collection auf einmal.

### Das Ausgangsproblem

POST /courses akzeptiert im Startstand noch diesen Body mit Status 201:

```json
{"title": "   ", "id": 42}
```

- Der Leerzeichen-Titel besteht die bisherige Mindestlänge.
- Das unbekannte Feld id wird ignoriert; der Server vergibt selbst eine ID.
- Nach dem Versuch neu starten, damit wieder fünf Kurse vorhanden sind.
- Dieses Verhalten verschärfen wir in Abschnitt 4.

## 1. Pfad, Query, Body und Antwort unterscheiden

| Angabe | Eingabeort | Beispiel |
| --- | --- | --- |
| course_id | Pfad: eine Ressource auswählen | GET /courses/3 |
| q | Query: Sammlung einschränken | GET /courses?q=Run |
| title | JSON-Body: neue Ressource beschreiben | POST /courses |

- Path und Query ergänzen Regeln für URL-Werte.
- Ein Pydantic-Modell beschreibt den JSON-Body.
- Request ist die Anfrage; Response ist die Antwort mit Status und Daten.
- Die Suche liefert eine Liste, der Einzelabruf ein Objekt.


> **⚠️ Pitfall: Suchtext im falschen Eingabeort**
> q gehört in die Query, nicht in die Kurs-ID und nicht in einen GET-Body.
> Die Antwort ist nicht automatisch derselbe Inhalt wie die Eingabe.

**Selbst prüfen:** Woher kommt die 2 bei GET /courses/2?
Woher kommt der Titel bei POST /courses?

## 2. Positive Pfad-IDs prüfen

In `tag6/main.py` den bisherigen Einzelabruf ersetzen.
Die neuen Imports oben ergänzen; App, Daten und Schemas bleiben bestehen.

```python
from typing import Annotated

from fastapi import Path


# Annotated verbindet Typ und Metadaten: int + Pfadwert ab 1.
# FastAPI liest "3" als 3; "Harry" scheitert am Typ, "0" an ge=1.
# ge bedeutet: größer oder gleich. Fehler liefern vor dem Aufruf 422.
@app.get("/courses/{course_id}", response_model=CourseRead)
def read_course(course_id: Annotated[int, Path(ge=1)]):
    # Die Typprüfung kennt den Bestand nicht. Erst hier prüfen wir die Existenz.
    course = courses.get(course_id)
    if course is None:
        raise HTTPException(status_code=404, detail="Kurs nicht gefunden.")
    return course
```

| Aufruf | Status | Grund |
| --- | --- | --- |
| GET /courses/3 | 200 | Gültige ID, Kurs vorhanden. |
| GET /courses/0 | 422 | Kleiner als 1. |
| GET /courses/-1 | 422 | Kleiner als 1. |
| GET /courses/Harry | 422 | Keine ganze Zahl. |
| GET /courses/999 | 404 | Gültige ID, Kurs fehlt. |

- Annotated verbindet den Typ int mit Path-Metadaten.
- ge=1 bedeutet „größer oder gleich 1“.
- FastAPI prüft Typ und Grenze vor dem Funktionsaufruf.
- Die Funktion prüft anschließend, ob der Kurs existiert.
- Bei 422 enthält detail eine Liste; loc nennt Ort und Feld.
- Beispiel: `["path", "course_id"]`. msg erklärt, type benennt die Fehlerart.

> **⚠️ Pitfall: 422 und 404 gleichsetzen**
> Auch 0 ist ein int. Erst Path(ge=1) verbietet diesen Wert.
> Eine gültige, unbekannte ID liefert dagegen 404 aus deiner Funktion.
> Pfadname und Funktionsparameter müssen beide course_id heißen.

## Exkurs: Instanzmethoden und Klassenmethoden

- Eine Instanzmethode erhält das konkrete Objekt als self.
- Eine Klassenmethode erhält durch @classmethod die Klasse als cls.
- Die Namen self und cls sind Konventionen.

Datei `tag6/method_demo.py` – getrennt von den API-Dateien:

<!-- file: tag6/method_demo.py -->
```python
class Course:
    def __init__(self, title):
        self.title = title

    def describe(self):
        # Beim Aufruf course.describe() setzt Python course als self ein.
        # Nur die konkrete Instanz hat hier ihren eigenen Titel.
        return f"Kursangebot: {self.title}"

    @classmethod
    def from_title(cls, title):
        # Python setzt Course als cls ein. Vorher ist keine Instanz nötig.
        # cls(...) ist hier ein zusätzlicher Weg zur Instanzerzeugung.
        return cls(title.strip())


if __name__ == "__main__":
    course = Course.from_title("  Alte Runen  ")
    print(course.title)
    print(course.describe())
```

```powershell
python -m tag6.method_demo
```

Erwartete Ausgabe:

```text
Alte Runen
Kursangebot: Alte Runen
```

- from_title erzeugt hier eine Instanz mit bereinigtem Titel.
- Eine Klassenmethode muss nicht grundsätzlich eine Instanz zurückgeben.
- Pydantic: model_validate arbeitet an der Klasse, model_dump an der Instanz.
- cls begegnet dir gleich beim Titel-Validator wieder.

> **⚠️ Pitfall: die konkrete Instanz vergessen**
> Course.describe() fehlt self. Verwende course.describe().
> Die Klasse kennt nicht automatisch den Titel einer bestimmten Instanz.
> Ohne @classmethod wird cls nicht automatisch mit der Klasse belegt.

## 3. Query-Parameter begrenzen

In `tag6/main.py` Query importieren und read_courses ersetzen.
Ein gesendeter Suchtext muss jetzt 2–100 Zeichen lang sein.

```python
from fastapi import Query


@app.get("/courses", response_model=list[CourseRead])
def read_courses(
    q: Annotated[
        # Erlaubter Python-Wert: Text oder None; noch keine Regel zum Weglassen.
        str | None,
        # Grenzen und Beschreibung gelten nur für einen gesendeten Suchtext.
        Query(min_length=2, max_length=100, description="Teil des Titels"),
    # Der Standardwert macht q auslassbar. q= ist dagegen ein leerer String.
    ] = None,
):
    rows = [courses[key] for key in sorted(courses)]
    # Ohne q alle Kurse; mit q filtern. Kein Treffer bleibt 200 mit [].
    if q is not None:
        # casefold ignoriert Groß-/Kleinschreibung; getrimmt wird hier nicht.
        rows = [
            row for row in rows
            if q.casefold() in row["title"].casefold()
        ]
    return rows
```

| Aufruf | Ergebnis |
| --- | --- |
| GET /courses | 200; fünf Kurse nach frischem Start. |
| GET /courses?q=RUN | 200; Alte Runen. |
| GET /courses?q=xyz | 200; leere Liste. |
| GET /courses?q=A | 422; zu kurz. |
| GET /courses?q= | 422; leer. |

- `str | None` erlaubt Text oder None als Wert.
- Erst `= None` macht den Parameter auslassbar.
- casefold ermöglicht den Vergleich ohne Groß-/Kleinschreibung.
- q wird hier nicht getrimmt; bei 422 lautet loc `["query", "q"]`.

> **⚠️ Pitfall: weggelassen und leer verwechseln**
> Ohne q wird nicht gefiltert. q= sendet einen leeren String und scheitert.
> Eine gültige Suche ohne Treffer liefert 200 mit [], keinen 404-Fehler.

Commitpunkt im Unterrichtsprojekt:

```powershell
git add .\tag6\data.py .\tag6\schemas.py .\tag6\main.py
git commit -m "Pruefe Kurs-IDs und Suchparameter"
```

## 4. Den JSON-Body mit Pydantic prüfen

`tag6/schemas.py` vollständig ersetzen.
Der Ablauf lautet: eigener Before-Validator → Typ und Länge → Route.

<!-- file: tag6/schemas.py -->
```python
from pydantic import BaseModel, ConfigDict, Field, field_validator


class CourseCreate(BaseModel):
    # Eingabeschema
    # BaseModel verarbeitet strukturierte Eingaben und ihre Regeln.
    # Nur dieses Modell: lehnt felder ab, die das model nicht kennt.
    model_config = ConfigDict(extra="forbid") #erzeugt 422
    # Field ergänzt die Mindest- und Höchstlänge.
    title: str = Field(min_length=1, max_length=100)

    # Eigene Feldprüfung vor Pydantics normaler Typ- und Längenprüfung.
    @field_validator("title", mode="before")
    # Was wäre,wenn mode="after"--> "   ".len > 1, strip: leer string erfolgreich
    # Python übergibt die Modellklasse als cls, keine Eingabeinstanz als self.
    @classmethod # CouseCreate.trim_title("  Flugkunde  "), instanze ist noch nicht aufgebaut
    def trim_title(cls, value):
        # strip nur auf Strings anwenden. Andere Typen prüft danach Pydantic.
        if isinstance(value, str):
            # "   " wird leer und scheitert danach an min_length=1.
            return value.strip()
        # Jeden Pfad mit Rückgabewert abschließen; sonst entstünde None.
        return value # wird zum neuen Feldwert


class CourseRead(BaseModel):
    # Antwortschema
    # Separater Antwortvertrag: positive ID, Titel mit 1–100 Zeichen.
    id: int = Field(ge=1)
    title: str = Field(min_length=1, max_length=100)


class CourseCount(BaseModel):
    # Für die feste Auswertungsroute im Router-Abschnitt.
    count: int = Field(ge=0)
```

- BaseModel verarbeitet die strukturierten Daten.
- Field setzt Grenzen; ConfigDict(extra="forbid") verbietet Zusatzfelder.
- Der Validator trimmt Strings vor der Längenprüfung und gibt den Wert zurück.
- Die anderen Typen lässt er zur normalen Pydantic-Prüfung weiterlaufen.
- Ungültige Eingaben erzeugen 422, keine neue ID und keinen Speicherwert.

### Drei POST-Bodies vergleichen

POST /courses mit diesem Body: 201 und der Titel Flugkunde.

```json
{"title": "  Flugkunde  "}
```

Dieser Body liefert 422 mit loc `["body", "title"]`:

```json
{"title": "   "}
```

Dieser Body liefert 422 mit loc `["body", "id"]`:

```json
{"title": "Flugkunde", "id": 42}
```

| Body-Fall | Bedeutung | Status |
| --- | --- | --- |
| {} | title fehlt. | 422 |
| title ist "" oder "   " | Leer oder nach dem Trimmen leer. | 422 |
| title ist null | None ist für dieses Feld nicht erlaubt. | 422 |
| title ist 123 | Zahl statt String. | 422 |

| Pydantic-2-Feld | None erlaubt? | Weglassen erlaubt? |
| --- | --- | --- |
| value: str | nein | nein |
| value: str \| None | ja | nein |
| value: str \| None = None | ja | ja |

> **⚠️ Pitfall: im Validator keinen Wert zurückgeben**
> Ohne return entsteht None. Prüfe vor strip außerdem den Eingangstyp.
> mode="before" ist hier nötig: Erst trimmen, dann die Länge prüfen.
> extra="forbid" in diesem Modell verbietet keine unbekannten Query-Parameter.

## 5. Request und Response getrennt halten

| Datenstruktur | Inhalt und Zweck |
| --- | --- |
| CourseCreate | Erlaubte Eingabe: title. |
| Speicher-Dictionary | id, title und die interne Notiz. |
| CourseRead | Öffentliche Antwort: id und title. |

In `tag6/main.py` create_course ersetzen:

```python
# response_model prüft die Rückgabe und serialisiert nur öffentliche Felder.
@app.post("/courses", response_model=CourseRead, status_code=201)
def create_course(course: CourseCreate):
    # FastAPI hat JSON eingelesen und geprüft: course ist eine Pydantic-Modellinstanz.
    # Erst die Route vergibt die ID; der Client darf sie nicht mitsenden.
    course_id = next(course_ids)
    created = {
        "id": course_id,
        "title": course.title,
        # Intern speichern, aber über CourseRead nicht öffentlich ausgeben.
        "internal_note": "Manuell erfasst.",
    }
    courses[course_id] = created
    # Vollständig speichern; die HTTP-Antwort enthält nur id und title.
    return created
```

- Beim frischen Start erhält der erste neue Kurs die ID 6.
- POST liefert 201; GET mit der zurückgegebenen ID liefert 200.
- Beide Antworten enthalten nur id und title.
- Die interne Notiz bleibt im Speicher und wird aus der Antwort gefiltert.
- Eingang: JSON → CourseCreate-Instanz. Ausgang: geprüfte Daten → JSON.
- model_dump liefert ein Dictionary; model_dump_json liefert JSON-Text.

> **⚠️ Pitfall: Antwortfilterung als Zugriffsschutz verstehen**
> response_model begrenzt öffentliche Felder, ersetzt aber keine Berechtigung.
> Eine ungültige Serverantwort ist ein Programmfehler, gewöhnlich Status 500.
> Das ist ein anderer Fall als eine ungültige Request-Eingabe mit 422.

## 6. Kursrouten mit APIRouter auslagern

- schemas.py enthält Verträge, data.py den Bestand und Zähler.
- APIRouter bündelt Kursendpunkte. main.py registriert sie an der App.
- Der Router selbst öffnet keine Datenbankverbindung.

Datei `tag6/routers/courses.py` vollständig anlegen:

<!-- file: tag6/routers/courses.py -->
```python
from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query

from tag6.data import course_ids, courses
from tag6.schemas import CourseCount, CourseCreate, CourseRead

# Kein Import von app aus main.py: So vermeiden wir gegenseitige Imports.
# prefix ergänzt jeden Pfad; tags gruppiert die Endpunkte in Swagger UI.
router = APIRouter(prefix="/courses", tags=["Kurse"])


# Leerer Pfad + Präfix ergibt /courses ohne zusätzlichen Slash.
@router.get("", response_model=list[CourseRead])
def read_courses(
    q: Annotated[
        str | None,
        Query(min_length=2, max_length=100, description="Teil des Titels"),
    ] = None,
):
    rows = [courses[key] for key in sorted(courses)]
    if q is not None:
        rows = [
            row for row in rows
            if q.casefold() in row["title"].casefold()
        ]
    return rows


# Registrierung wird der Reihe nach geprüft: /count vor /{course_id}.
# Sonst erfasst der Platzhalter "count" und die int-Prüfung liefert 422.
# Die int-Annotation allein verhindert diese falsche Zuordnung nicht.
@router.get("/count", response_model=CourseCount)
def read_course_count():
    # CourseCount liefert count: Anzahl der Kurse, keine Buchungen/DB-Zeilen.
    return {"count": len(courses)}


# Mit Präfix ergibt das /courses/{course_id}.
@router.get("/{course_id}", response_model=CourseRead)
def read_course(course_id: Annotated[int, Path(ge=1)]):
    course = courses.get(course_id)
    if course is None:
        raise HTTPException(status_code=404, detail="Kurs nicht gefunden.")
    return course


@router.post("", response_model=CourseRead, status_code=201)
def create_course(course: CourseCreate):
    course_id = next(course_ids)
    created = {
        "id": course_id,
        "title": course.title,
        # Nur im Lernspeicher. CourseRead gibt dieses Feld nicht aus.
        "internal_note": "Manuell erfasst.",
    }
    courses[course_id] = created
    return created
```

`tag6/main.py` vollständig ersetzen; die alten Kursrouten dort entfernen:

<!-- file: tag6/main.py -->
```python
from fastapi import FastAPI

from tag6.routers.courses import router as course_router

app = FastAPI(
    title="Hogwarts-Kursverwaltung",
    description="Validierte Lern-API mit vorübergehendem Speicher.",
    version="0.2.0",
)
# Ein Import allein genügt nicht: include_router registriert die Kurs-Endpunkte.
app.include_router(course_router)


@app.get("/health", tags=["System"])
def read_health():
    return {"status": "ok"}
```

- prefix und Dekoratorpfad ergeben zusammen die URL.
- `prefix="/courses"` plus `"/count"` ergibt /courses/count.
- tags gruppiert die Endpunkte in Swagger UI.
- Alle bisherigen Kursaufrufe bleiben erreichbar.
- GET /courses/count liefert nach frischem Start `{"count": 5}`.

> **⚠️ Pitfall: die feste Route hinter dem Platzhalter registrieren**
> /count muss vor /{course_id} stehen, sonst wird count als ID geprüft: 422.
> int allein verhindert diese falsche Routenzuordnung nicht.
> Ein Import ohne include_router registriert keine Kursendpunkte.
> Das Präfix im Dekorator nicht erneut als /courses schreiben.

Commitpunkt:

```powershell
git add .\tag6\schemas.py .\tag6\routers\courses.py .\tag6\main.py
git diff --cached
git commit -m "Validiere Kurse und gliedere Routen mit APIRouter"
```

## 7. Den API-Vertrag mit vier Tests sichern

Postman und TestClient prüfen dieselben Erwartungen.
TestClient ruft die importierte App auf; dafür muss Uvicorn nicht laufen.

Datei `tag6/test_api.py`:

<!-- file: tag6/test_api.py -->
```python
from fastapi.testclient import TestClient

from tag6.data import courses
# Die zwei bekannten GET-Tests erhalten nur den neuen App-Import.
from tag6.main import app

# pytest führt Tests aus; TestClient sendet Requests ohne Serverstart.
client = TestClient(app)


def test_read_course():
    response = client.get("/courses/1")
    assert response.status_code == 200
    assert response.json() == {"id": 1, "title": "Arithmantik"}


def test_missing_course():
    response = client.get("/courses/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Kurs nicht gefunden."}


def test_invalid_body():
    # Nicht nur die Fehlermeldung prüfen: Der Bestand muss gleich bleiben.
    before = len(courses)
    # json= sendet den Body; response.json() liest später den Antwort-Body.
    response = client.post("/courses", json={"title": "   "})
    assert response.status_code == 422
    # loc nennt Ort und Feld; kein Vergleich versionsabhängiger Meldungstexte.
    assert response.json()["detail"][0]["loc"] == ["body", "title"]
    assert len(courses) == before


def test_create_and_filter_response():
    before = len(courses)
    response = client.post("/courses", json={"title": "  Flugkunde  "})
    assert response.status_code == 201
    created = response.json()
    # try enthält die Prüfungen; finally räumt auch nach einer Assertion auf.
    try:
        # Mit fachlichen Erwartungswerten vergleichen: getrimmt und öffentlich.
        assert created["title"] == "Flugkunde"
        assert set(created) == {"id", "title"}
        assert len(courses) == before + 1
        stored = courses[created["id"]]
        # Antwortfilterung entfernt die Notiz nicht aus dem Speicher.
        assert stored["internal_note"] == "Manuell erfasst."
        # Auch die Abrufbarkeit der gerade erzeugten Daten prüfen.
        detail = client.get(f"/courses/{created['id']}")
        assert detail.status_code == 200
        assert detail.json() == created
    finally:
        # Nur diesen Testkurs löschen. None toleriert einen fehlenden Eintrag.
        courses.pop(created["id"], None)
```

```powershell
python -m pytest .\tag6\test_api.py -q
```

- Erwartet: vier bestandene Tests, auch beim nächsten Aufruf.
- Die GET-Tests prüfen einen vorhandenen und einen fehlenden Kurs.
- Die POST-Tests prüfen ungültige Eingaben, Trimmen und Antwortfilterung.
- Status, Feldort und Wirkung auf den Bestand gehören zusammen.

> **⚠️ Pitfall: eine feste neue ID im Test erwarten**
> Nutze die tatsächliche ID aus der Antwort; der Zähler läuft weiter.
> finally entfernt den eigenen Testkurs auch bei fehlgeschlagenen Assertions.
> TestClient und Uvicorn laufen hier in getrennten Prozessen mit eigenen Daten.
> TestClient reicht unerwartete Serverfehler standardmäßig als Exception weiter.

## 8. Eine unbekannte Eingabe selbst prüfen

1. Sende POST /courses mit title=Flugkunde und capacity=20.
2. Prüfe den Status und den Feldort in der Antwort.
3. Prüfe danach, ob ein neuer Kurs angelegt wurde.

Erwartet: 422, loc `["body", "capacity"]` und unveränderter Bestand.
Die vorhandene Modellregel greift vor dem Aufruf von create_course.

> **⚠️ Pitfall: für jedes Zusatzfeld neuen Routencode schreiben**
> capacity ist nicht vereinbart. extra="forbid" weist es bereits ab.
> Eine Kapazitätsregel wird dadurch noch nicht Teil des Datenmodells.

## 9. Den vollständigen Projektstand nachschlagen

```text
hogwarts-sql/
├── requirements-tag5.txt
└── tag6/
    ├── data.py
    ├── schemas.py
    ├── main.py
    ├── test_api.py
    └── routers/
        └── courses.py
```

- tag6 wird im Projektstamm als Namespace-Paket geladen.
- Bei diesem Aufbau ist keine __init__.py erforderlich.
- Dateien nicht fastapi.py oder pydantic.py nennen: Das verdeckt die Pakete.

<details>
<summary>Vollständige endgültige Dateien aufklappen</summary>

Diese Dateien bilden gemeinsam den Pflichtstand nach Abschnitt 6 und 7.
Sie ersetzen die jeweiligen Startdateien und Zwischenstände oben.

Datei `tag6/data.py`:

<!-- file: tag6/data.py -->
```python
from itertools import count

# Eigene Kopie des Live-Bestands von Tag 5, ohne Datenbankzugriff.
courses = {
    1: {"id": 1, "title": "Arithmantik"},
    2: {"id": 2, "title": "Wahrsagen"},
    3: {"id": 3, "title": "Alte Runen"},
    4: {"id": 4, "title": "Pflege magischer Geschöpfe"},
    5: {"id": 5, "title": "Zaubertrankpraxis"},
}
course_ids = count(6)
```

Datei `tag6/schemas.py`:

<!-- file: tag6/schemas.py -->
```python
from pydantic import BaseModel, ConfigDict, Field, field_validator


class CourseCreate(BaseModel):
    # Unbekannte Body-Felder werden gemeldet, statt still ignoriert.
    model_config = ConfigDict(extra="forbid")
    title: str = Field(min_length=1, max_length=100)

    @field_validator("title", mode="before")
    @classmethod
    def trim_title(cls, value):
        # Vor der Längenprüfung kürzen. Falsche Typen prüft Pydantic.
        if isinstance(value, str):
            return value.strip()
        return value


class CourseRead(BaseModel):
    id: int = Field(ge=1)
    title: str = Field(min_length=1, max_length=100)


class CourseCount(BaseModel):
    count: int = Field(ge=0)
```

Datei `tag6/routers/courses.py`:

<!-- file: tag6/routers/courses.py -->
```python
from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query

from tag6.data import course_ids, courses
from tag6.schemas import CourseCount, CourseCreate, CourseRead

router = APIRouter(prefix="/courses", tags=["Kurse"])


@router.get("", response_model=list[CourseRead])
def read_courses(
    q: Annotated[
        str | None,
        Query(min_length=2, max_length=100, description="Teil des Titels"),
    ] = None,
):
    rows = [courses[key] for key in sorted(courses)]
    if q is not None:
        rows = [
            row for row in rows
            if q.casefold() in row["title"].casefold()
        ]
    return rows


# Feste Pfade vor dem Platzhalter: count darf keine Kurs-ID werden.
@router.get("/count", response_model=CourseCount)
def read_course_count():
    return {"count": len(courses)}


@router.get("/{course_id}", response_model=CourseRead)
def read_course(course_id: Annotated[int, Path(ge=1)]):
    course = courses.get(course_id)
    if course is None:
        raise HTTPException(status_code=404, detail="Kurs nicht gefunden.")
    return course


@router.post("", response_model=CourseRead, status_code=201)
def create_course(course: CourseCreate):
    course_id = next(course_ids)
    created = {
        "id": course_id,
        "title": course.title,
        # Nur im Lernspeicher. CourseRead gibt dieses Feld nicht aus.
        "internal_note": "Manuell erfasst.",
    }
    courses[course_id] = created
    return created
```

Datei `tag6/main.py`:

<!-- file: tag6/main.py -->
```python
from fastapi import FastAPI

from tag6.routers.courses import router as course_router

app = FastAPI(
    title="Hogwarts-Kursverwaltung",
    description="Validierte Lern-API mit vorübergehendem Speicher.",
    version="0.2.0",
)
# Ein Import allein registriert keine Endpunkte in der Anwendung.
app.include_router(course_router)


@app.get("/health", tags=["System"])
def read_health():
    return {"status": "ok"}
```

Datei `tag6/test_api.py`:

<!-- file: tag6/test_api.py -->
```python
from fastapi.testclient import TestClient

from tag6.data import courses
from tag6.main import app

client = TestClient(app)


def test_read_course():
    response = client.get("/courses/1")
    assert response.status_code == 200
    assert response.json() == {"id": 1, "title": "Arithmantik"}


def test_missing_course():
    response = client.get("/courses/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Kurs nicht gefunden."}


def test_invalid_body():
    before = len(courses)
    response = client.post("/courses", json={"title": "   "})
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "title"]
    assert len(courses) == before


def test_create_and_filter_response():
    before = len(courses)
    response = client.post("/courses", json={"title": "  Flugkunde  "})
    assert response.status_code == 201
    created = response.json()
    try:
        assert created["title"] == "Flugkunde"
        assert set(created) == {"id", "title"}
        assert len(courses) == before + 1
        stored = courses[created["id"]]
        assert stored["internal_note"] == "Manuell erfasst."
        detail = client.get(f"/courses/{created['id']}")
        assert detail.status_code == 200
        assert detail.json() == created
    finally:
        # Vorgegebene Bereinigung: auch bei fehlgeschlagener Prüfung entfernen.
        courses.pop(created["id"], None)
```

</details>

Abschlussbefehle im Unterrichtsprojekt:

```powershell
python -m pytest .\tag6\test_api.py -q
git add .\tag6\test_api.py
git commit -m "Teste Eingabegrenzen und Kursantworten"
```