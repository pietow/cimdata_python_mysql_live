# Routing und Validierung – Übungen für Tag 6

## Überblick

Die Hogwarts-Verwaltung möchte fehlerhafte Schülerdaten früh erkennen.
Ihr entwickelt dafür eine Schüler-API mit klaren Datenverträgen.
Übertragt die Kursmuster auf Schüler. Kombiniert danach eigene Filter.

- Pflichtaufgaben: 1–8. Bonusaufgaben: 9–11.
- Die Kurs-App aus dem Vormittag läuft auf Port 8000.
- Die Schüler-App läuft auf Port 8001 und hat einen eigenen Bestand.
- Für diese Aufgaben wird keine Datenbank benötigt.
- Neue Daten liegen nur im Speicher des jeweiligen Python-Prozesses.
- Ein Serverneustart oder Reload stellt den Startbestand wieder her.
- Vor festen Ergebniszahlen beginnt ihr mit einem frischen App-Start.
- Ein POST-Klick legt jeweils einen weiteren Schüler an.
- Prüft die API-Regeln mit Postman. In Aufgabe 8 ergänzt ihr anhand eines Gerüsts zwei pytest-Tests.
- Parametrisierung und weitere Testfälle sind freiwillige Vertiefung; eigene Fixtures folgen an Tag 8.

| Aufgabe | Auftrag |
| --- | --- |
| 1 | Eingabeorte und Antwortvertrag planen |
| 2 | Startmaterial übernehmen und die App starten |
| 3 | Schülerdaten mit Pydantic prüfen |
| 4 | Schüler in einem APIRouter lesen |
| 5 | Haus und Schuljahr gemeinsam filtern |
| 6 | Schüler anlegen und Antworten begrenzen |
| 7 | Eine Zusammenfassung nach Häusern liefern |
| 8 | Zwei bekannte GET-Tests übernehmen und zwei POST-Tests ergänzen |
| 9 | Strenge Typprüfung vergleichen |
| 10 | Namen mit PATCH gezielt ändern |
| 11 | Eine verschachtelte Buchungsvorschau ausgeben |

## Vor dem Start

- Verwendet das venv und requirements-tag5.txt aus dem Vormittag.
- In Postman [06-Tag6-Hogwarts.postman_collection.json](06-Tag6-Hogwarts.postman_collection.json) importieren; die Collection heißt „Tag 6 – Hogwarts“.
- Collection-Variable practice_url: http://127.0.0.1:8001.
- Die Pflicht-Requests im Ordner „02 Schüler – Pflicht“ beginnen mit {{practice_url}}; der Schülerbonus verwendet bonus_url.
- Filter im Reiter Params eintragen.
- Für POST und PATCH Body → raw → JSON auswählen.
- Die Bodies sind in den vorbereiteten Requests hinterlegt; Änderungen können im JSON-Feld vorgenommen werden.
- Status und Antwortinhalt bei jedem Aufruf getrennt notieren.

```powershell
Set-Location "$env:USERPROFILE\hogwarts-sql"
.\.venv\Scripts\Activate.ps1
New-Item -ItemType Directory -Force -Path .\tag6\routers
python -m pip check
```


- Bei blockierter Aktivierung das venv-Python direkt verwenden.

```powershell
.\.venv\Scripts\python.exe --version
```


- Danach in den folgenden Befehlen diesen Pfad statt python verwenden.

### Requests zu den Aufgaben

Alle Einträge gehören zur Collection „Tag 6 – Hogwarts“. Pflicht-Requests einzeln senden, sobald der zugehörige Endpunkt umgesetzt ist. Für einen Lauf des ganzen Ordners müssen Aufgaben 1–7 fertig sein und der Server frisch gestartet werden. Aufgabe 8 prüft denselben Vertrag anschließend mit pytest.

| Aufgabe | Ordner → Request | Methode und Endpunkt | Erwartung |
| --- | --- | --- | --- |
| 2 | 02 Schüler – Pflicht → Health prüfen | GET {{practice_url}}/health | 200 |
| 4 | 02 Schüler – Pflicht → Luna lesen | GET {{practice_url}}/students/14 | 200; vollständiges Objekt |
| 4 | 02 Schüler – Pflicht → ID null ablehnen | GET {{practice_url}}/students/0 | 422 |
| 5 | 02 Schüler – Pflicht → Haus und Schuljahr kombinieren | GET {{practice_url}}/students?house=Gryffindor&school_year=2 | 200; nur Ginny |
| 5 | 02 Schüler – Pflicht → Kleingeschriebenes Haus ablehnen | GET {{practice_url}}/students?house=gryffindor | 422 |
| 6 | 02 Schüler – Pflicht → Cho anlegen | POST {{practice_url}}/students | 201; ID wird übernommen |
| 6 | 02 Schüler – Pflicht → Angelegte Schülerin lesen | GET {{practice_url}}/students/{{created_student_id}} | 200; zuerst Cho anlegen |
| 6 | 02 Schüler – Pflicht → Leeren Vornamen ablehnen | POST {{practice_url}}/students | 422; kein neuer Eintrag |
| 7 | 02 Schüler – Pflicht → Zusammenfassung vor Anlage | GET {{practice_url}}/students/summary | 200; frischer Bestand: 6 |
| 7 | 02 Schüler – Pflicht → Zusammenfassung nach Anlage | GET {{practice_url}}/students/summary | 200; nach genau einem POST: 7 |
| 10 | 04 Schülerbonus → Vornamen trimmen | PATCH {{bonus_url}}/students/14 | 200 |
| 11 | 04 Schülerbonus → Buchungsvorschauen lesen | GET {{bonus_url}}/bookings | 200; zwei Vorschauen |

Die übrigen Requests ergänzen die Grenzfälle. Nach einem Neustart müsst ihr Cho erneut anlegen, bevor ihr ihre gespeicherte Antwort-ID verwendet. Ein früher gespeicherter Postman-Wert gehört möglicherweise zum alten Serverbestand.

<a id="aufgabe-1"></a>

## 1. Eingabeorte und Antwortvertrag planen

Die Verwaltung möchte Luna lesen und Cho anlegen.

### Aufgaben

1. Notiert Methode und URL für Luna mit ID 14.
2. Notiert Methode und URL für Schüler aus Gryffindor im zweiten Schuljahr.
3. Notiert Methode und URL für die Anlage von Cho Chang.
4. Ordnet ID, Hausfilter, Schuljahrfilter und Namen ihren Eingabeorten zu.
5. Nennt die Felder des Anlagemodells und des Antwortmodells.
6. Sagt die Statuscodes für ID 0, ID 999 und ID Luna voraus.
7. Erklärt den Unterschied zwischen fehlendem first_name und JSON-null.

### Erfolgskriterien

- Sammlung: /students. Einzelabruf: /students/{student_id}.
- Filter: house und school_year in der Query.
- Anlage: Namen, Haus und Schuljahr im JSON-Body.
- Der Server vergibt die neue ID selbst.
- Die Antwort enthält id, first_name, last_name, house und school_year.
- Ein ungültiger Wert ergibt 422. Eine fehlende Ressource ergibt 404.

<a id="aufgabe-2"></a>

## 2. Startmaterial übernehmen und die App starten

Die Verwaltung braucht eine erreichbare Schüler-App.

### Aufgaben

1. Übernehmt die beiden vollständigen Dateien aus dem Startmaterial.
2. Startet die App mit dem angegebenen Uvicorn-Befehl.
3. Sendet GET {{practice_url}}/health in Postman.
4. Öffnet http://127.0.0.1:8001/docs.
5. Notiert den aktuellen Schülerbestand und die nächste ID.

### Startmaterial: vollständiger Schülerbestand

<!-- file: tag6/practice_data.py -->
- Lokal: `.\tag6\practice_data.py`.

```python
from itertools import count

students = {
    11: {
        "id": 11, "first_name": "Harry", "last_name": "Potter",
        "house": "Gryffindor", "school_year": 3,
    },
    12: {
        "id": 12, "first_name": "Hermione", "last_name": "Granger",
        "house": "Gryffindor", "school_year": 3,
    },
    13: {
        "id": 13, "first_name": "Draco", "last_name": "Malfoy",
        "house": "Slytherin", "school_year": 3,
    },
    14: {
        "id": 14, "first_name": "Luna", "last_name": "Lovegood",
        "house": "Ravenclaw", "school_year": 2,
    },
    15: {
        "id": 15, "first_name": "Ginny", "last_name": "Weasley",
        "house": "Gryffindor", "school_year": 2,
    },
    16: {
        "id": 16, "first_name": "Neville", "last_name": "Longbottom",
        "house": "Gryffindor", "school_year": 3,
    },
}

student_ids = count(17)
```


### Startmaterial: vollständige erste App

<!-- file: tag6/practice.py -->
- Lokal: `.\tag6\practice.py`.

```python
from fastapi import FastAPI

app = FastAPI(title="Hogwarts-Schülerverwaltung – Tag 6")


@app.get("/health", tags=["System"])
def read_health():
    return {"status": "ok", "school": "Hogwarts"}
```

```powershell
python -m uvicorn tag6.practice:app --reload --host 127.0.0.1 --port 8001
```


- Dieses Terminal bleibt offen. Git und pytest brauchen ein zweites Terminal.

### Erfolgskriterien

- Health liefert 200 und {"status":"ok","school":"Hogwarts"}.
- Der Startbestand enthält sechs Schüler mit IDs 11–16.
- Die nächste frisch vergebene ID ist 17.
- Die Speicher-IDs werden nicht als tatsächliche MySQL-IDs behandelt.

<a id="aufgabe-3"></a>

## 3. Schülerdaten mit Pydantic prüfen

Die Verwaltung möchte keine leeren Namen oder unbekannten Hauswerte speichern.

### Aufgaben

1. Erstellt tag6/practice_schemas.py.
2. Definiert House mit Literal und den vier genauen Hausnamen.
3. Erstellt StudentCreate mit vier erforderlichen Eingabefeldern.
4. Erlaubt für Namen 1–50 Zeichen nach dem Entfernen von Rand-Leerzeichen.
5. Erlaubt beim Schuljahr nur ganze Zahlen von 1 bis 7.
6. Verwendet ConfigDict für str_strip_whitespace und extra="forbid".
7. Erstellt StudentRead mit den vier Fachfeldern und einer positiven ID.
8. Prüft die Modelle zunächst mit einem kurzen Python-Aufruf oder in Tests.

### Vereinbarter Vertrag

- House: Gryffindor, Hufflepuff, Ravenclaw oder Slytherin.
- Die Schreibweise ist exakt. gryffindor ist hier kein gültiger Wert.
- Das präzisiert den offenen Hausfilter von Tag 5.
- first_name und last_name sind erforderlich und nicht nullable.
- Ein Name nur aus Leerzeichen ist ungültig.
- Eine mitgesendete ID ist ein unbekanntes Eingabefeld.
- school_year hat zunächst normale Pydantic-Konvertierung.
- Der JSON-String "3" wird daher in die ganze Zahl 3 umgewandelt.
- Die strenge Alternative gehört zu Bonusaufgabe 9.
- StudentRead enthält keine interne Notiz.

### Erfolgskriterien

- " Cho " wird als Cho übernommen.
- Fehlender oder leerer Name ergibt einen Modellfehler.
- school_year=0 und school_year=8 sind ungültig.
- house=Durmstrang und ein zusätzliches id-Feld sind ungültig.
- Die Antwort-ID ist erforderlich und mindestens 1.

<a id="aufgabe-4"></a>

## 4. Schüler in einem APIRouter lesen

Die Verwaltung möchte die Schülerliste und Luna einzeln abrufen.

### Aufgaben

1. Erstellt tag6/routers/students.py mit einem APIRouter.
2. Verwendet prefix="/students" und tags=["Schüler"].
3. Implementiert die Sammlung als GET mit leerem Routerpfad.
4. Sortiert die Ausgabe nach ID und verwendet list[StudentRead].
5. Implementiert GET /{student_id} mit Annotated, Path und ge=1.
6. Gebt für eine nicht vorhandene ID Status 404 aus.
7. Registriert den Router in tag6/practice.py mit include_router.
8. Entfernt doppelte Endpunktdefinitionen aus der Startdatei.

### Erfolgskriterien

| Aufruf | Erwartetes Ergebnis |
| --- | --- |
| GET /students | 200; IDs 11, 12, 13, 14, 15, 16 |
| GET /students/14 | 200; Luna Lovegood, Ravenclaw, Schuljahr 2 |
| GET /students/0 | 422; loc beginnt mit path |
| GET /students/Luna | 422; ungültiger Integer |
| GET /students/999 | 404; Schüler nicht gefunden. |

- Der Einzelabruf liefert ein Objekt, die Sammlung eine Liste.
- Swagger UI zeigt die Gruppe Schüler.
- Es entsteht kein Pfad /students/students.

<a id="aufgabe-5"></a>

## 5. Haus und Schuljahr gemeinsam filtern

Die Verwaltung benötigt die Gryffindor-Schüler im zweiten Schuljahr.
Hier reicht es nicht, die Titelsuche aus dem Kursrouter umzubenennen.

### Aufgaben

1. Ergänzt den optionalen Query-Parameter house mit dem Typ House.
2. Ergänzt den optionalen Parameter school_year mit Grenzen 1–7.
3. Ohne Parameter soll die vollständige Liste erscheinen.
4. Bei einem Parameter soll nur die zugehörige Bedingung gelten.
5. Bei beiden Parametern müssen beide Bedingungen zutreffen.
6. Erhaltet die ID-Sortierung und den Antworttyp als Liste.
7. Notiert das Verhalten bei ungültigen Filtern und bei null Treffern.

### Erfolgskriterien bei frischem Bestand

| Query an /students | Status | IDs |
| --- | ---: | --- |
| keine | 200 | 11, 12, 13, 14, 15, 16 |
| house=Gryffindor | 200 | 11, 12, 15, 16 |
| school_year=2 | 200 | 14, 15 |
| house=Gryffindor&school_year=2 | 200 | 15 |
| house=Hufflepuff | 200 | leere Liste |
| house=gryffindor | 422 | ungültiger Hauswert |
| school_year=8 | 422 | ungültiges Schuljahr |

- Query-Werte sind URL-Text. "2" wird passend zum Typ gelesen.
- Ein gültiger Filter ohne Treffer ist kein 404.
- Bei 422 nennt loc query und den betroffenen Parameternamen.

<a id="aufgabe-6"></a>

## 6. Schüler anlegen und Antworten begrenzen

Die Verwaltung legt Cho Chang an. Eine interne Erfassungsnotiz bleibt intern.

### Aufgaben

1. Ergänzt POST mit leerem Routerpfad und Status 201.
2. Nehmt StudentCreate als Body und StudentRead als response_model.
3. Vergebt die ID mit student_ids aus practice_data.py.
4. Übernehmt die geprüften Fachfelder mit model_dump.
5. Speichert intern internal_note mit dem Wert Manuell erfasst.
6. Gebt den neuen Speicher-Eintrag zurück.
7. Ruft den angelegten Schüler mit seiner Antwort-ID ab.
8. Sendet danach ungültige Varianten und kontrolliert den Bestand.

### Body für eine gültige Anlage

```json
{
  "first_name": " Cho ",
  "last_name": "Chang",
  "house": "Ravenclaw",
  "school_year": 4
}
```


### Erfolgskriterien

- Die erste gültige Anlage nach frischem Start erhält ID 17.
- Die Antwort enthält Cho ohne Rand-Leerzeichen.
- Die Antwort enthält genau die fünf vereinbarten öffentlichen Felder.
- internal_note steht im Speicher, aber nicht in der HTTP-Antwort.
- Die Sammlung enthält danach sieben Schüler.
- Ein mitgesendetes id-Feld ergibt 422 am Feld body/id.
- first_name nur aus Leerzeichen ergibt 422 am Feld body/first_name.
- Ein ungültiger POST verändert weder Bestand noch nächsten Zählerwert.
- Ein weiterer gültiger POST erzeugt einen weiteren Schüler.

<a id="aufgabe-7"></a>

## 7. Eine Zusammenfassung nach Häusern liefern

Die Verwaltung braucht eine Schülerzahl für jedes Haus.
Ein Haus ohne Schüler soll mit 0 sichtbar bleiben.

### Aufgaben

1. Definiert StudentSummary in practice_schemas.py.
2. Das Modell enthält total als Integer und by_house als Dictionary.
3. Ergänzt GET /summary im Schülerrouter mit diesem Antwortmodell.
4. Registriert diese feste Route vor /{student_id}.
5. Berechnet die Hauszahlen aus dem aktuellen Schülerbestand.
6. Liefert alle vier Hausnamen, auch wenn ein Haus keinen Schüler hat.
7. Vergleicht die Ausgabe vor und nach einer Anlage von Cho.
8. Erklärt, warum eine int-Annotation die Routenreihenfolge nicht ersetzt.

### Erwartete Antwort bei frischem Bestand

```json
{
  "total": 6,
  "by_house": {
    "Gryffindor": 4,
    "Hufflepuff": 0,
    "Ravenclaw": 1,
    "Slytherin": 1
  }
}
```


### Erfolgskriterien

- GET /students/summary ergibt 200 und nicht 422.
- Die Summe der Hauszahlen entspricht total.
- Nach einer Anlage von Cho: total=7 und Ravenclaw=2.
- Die übrigen Hauszahlen bleiben unverändert.
- Der Endpunkt zählt alle Schüler und hat selbst keine Filterparameter.

<a id="aufgabe-8"></a>

## 8. Bekannte Tests gezielt ergänzen

Die Verwaltung möchte zwei neue Body-Regeln nach Änderungen erneut prüfen. Ihr übernehmt die bekannten GET-Muster und ergänzt zwei POST-Tests. Eine selbst entwickelte Testsammlung wird heute nicht erwartet.

### Vorgegebenes Gerüst

Speichert den folgenden Code als tag6/test_practice.py. Er enthält die beiden bekannten GET-Prüfungen für die Schüler-App sowie die vollständige Hülle der POST-Tests. Eine Bonuslösung aus Tag 5 ist dafür nicht nötig.

Die beiden NotImplementedError-Zeilen markieren offene Arbeit: Beim ersten Lauf bestehen die GET-Tests; die beiden POST-Tests scheitern absichtlich. Ersetzt diese Zeilen durch die verlangten Prüfungen, bevor ihr die Aufgabe abschließt.

<!-- file: tag6/test_practice.py -->
- Lokal: `.\tag6\test_practice.py`.

```python
from fastapi.testclient import TestClient

from tag6.practice import app
from tag6.practice_data import students

client = TestClient(app)
VALID = {
    "first_name": "Cho", "last_name": "Chang",
    "house": "Ravenclaw", "school_year": 4,
}


def test_read_luna():
    response = client.get("/students/14")
    assert response.status_code == 200
    assert response.json() == {
        "id": 14, "first_name": "Luna", "last_name": "Lovegood",
        "house": "Ravenclaw", "school_year": 2,
    }


def test_missing_student():
    response = client.get("/students/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Schüler nicht gefunden."}


def test_invalid_body():
    before = len(students)
    response = client.post("/students", json={**VALID, "first_name": "   "})
    # Ergänzt Status, Fehlerort und unveränderte Anzahl.
    raise NotImplementedError("Hier die drei Prüfungen ergänzen.")


def test_create_trim_and_response():
    before = len(students)
    body = {**VALID, "first_name": " Cho ", "last_name": " Chang ", "school_year": "4"}
    response = client.post("/students", json=body)
    assert response.status_code == 201
    created = response.json()
    try:
        # Ergänzt erwartete Felder, Bestand und den erneuten GET.
        raise NotImplementedError("Hier die Antwort und den GET prüfen.")
    finally:
        # Vorgegeben: Testeintrag auch nach fehlgeschlagener Prüfung entfernen.
        students.pop(created["id"], None)
```

### Aufgaben

1. Führt das Gerüst aus und erklärt bei den GET-Tests App-Import, URL, Status und Antwortinhalt. Vergleicht das bekannte Kursmuster mit dem Schülerobjekt.
2. Ergänzt test_invalid_body: Status 422, loc ["body", "first_name"] und dieselbe Schülerzahl wie vor dem Request.
3. Ergänzt test_create_trim_and_response: Die Antwort enthält genau id, first_name, last_name, house und school_year. Erwartet Cho, Chang, Ravenclaw und die Zahl 4; die ID ist eine positive ganze Zahl. Prüft außerdem, dass genau ein Schüler hinzugekommen ist und der gespeicherte Eintrag die erwarteten Fachwerte sowie eine interne Notiz enthält.
4. Ruft den angelegten Schüler über seine Antwort-ID erneut mit GET ab. Prüft Status 200 und den vollständigen Inhalt. Vergleicht nicht nur zwei möglicherweise gleich falsche Antworten: Prüft zuerst die POST-Antwort gegen eure ausdrücklich erwarteten Werte.
5. Übernehmt die vorgegebene try/finally-Hülle unverändert. Erklärt, warum sie den Testeintrag nach der Prüfung entfernt und warum keine feste neue ID erwartet wird.

In Abschnitt 7 des Skripts ist dasselbe Vorgehen für Kurse vollständig erklärt. Ein assert vergleicht beobachtetes und erwartetes Ergebnis. Der finally-Block räumt auch bei einer fehlgeschlagenen Assertion auf; eigene Fixtures werden erst an Tag 8 entwickelt.


### Erfolgskriterien

- Vier Tests bestehen: zwei übernommene GET-Tests und zwei ergänzte POST-Tests.
- Die Tests laufen ohne Uvicorn; beide NotImplementedError-Platzhalter sind ersetzt.
- Der ungültige POST verändert die Schülerzahl nicht.
- Der erfolgreiche POST liefert alle erwarteten Werte und keine interne Notiz im JSON; der GET bestätigt den gespeicherten Datensatz.
- Die vorgegebene Bereinigung entfernt den Testschüler, auch wenn eine Prüfung scheitert.
- Kombinierte Filter und Summary bleiben Pflicht in Aufgaben 5 und 7 und werden dort mit Postman geprüft.

### Freiwillige Vertiefung

Erst nach dem Grundstand: weitere Filter-, Summary-, ID- und Body-Prüfungen in tag6/test_practice_extra.py ergänzen. Die Referenz bietet 18 Zusatzfälle. Parametrisierung ist hierfür optionales Zusatzmaterial; sie wird an Tag 8 systematisch behandelt.

## Bonusaufgaben

- Pflichtdateien erhalten. Eine eigene Bonus-App verwenden.
- Die Bonus-App läuft auf Port 8002 statt auf Port 8001.
- Postman-Variable bonus_url: http://127.0.0.1:8002.
- Port 8002 wird auch vom Kursbonus des Vormittags verwendet. Vor dem Wechsel den laufenden Bonusserver mit Strg+C stoppen; anschließend tag6.practice_bonus:app starten und ausschließlich den Ordner „04 Schülerbonus“ verwenden.
- Alle drei Bonusaufgaben sind eigene Erweiterungen des heutigen Vertrags.

<a id="aufgabe-9"></a>

## 9. Strenge Typprüfung vergleichen

Die Verwaltung überlegt, Zahlen als JSON-String künftig abzulehnen.

### Aufgaben

1. Erstellt StrictStudentCreate als Ableitung von StudentCreate.
2. Überschreibt nur school_year mit strict=True und Grenzen 1–7.
3. Legt das Modell in tag6/practice_bonus_schemas.py ab.
4. Vergleicht beide Modelle mit school_year=4 und school_year="4".
5. Verwendet model_validate und fangt ValidationError für den Vergleich ab.
6. Erklärt, warum die normale Schüler-App weiterhin "3" akzeptiert.

### Erfolgskriterien

- StudentCreate akzeptiert Zahl 4 und String "4".
- StrictStudentCreate akzeptiert Zahl 4 und lehnt String "4" ab.
- Name, Haus und zusätzliche Felder werden weiterhin wie zuvor geprüft.
- Die Pflicht-App wird durch diesen Modellvergleich nicht verändert.

<a id="aufgabe-10"></a>

## 10. Namen mit PATCH gezielt ändern

Die Verwaltung möchte Rand-Leerzeichen in einem Schülernamen korrigieren.
Haus und Schuljahr sollen dabei erhalten bleiben.

### Aufgaben

1. Erstellt StudentNamePatch in practice_bonus_schemas.py.
2. Erlaubt first_name und last_name jeweils ausgelassen oder als Namen.
3. Verwendet die bisherigen Längenregeln und entfernt Rand-Leerzeichen.
4. Lehnt ausdrücklich gesendete Nullwerte mit einem Validator ab.
5. Lehnt zusätzliche Felder ab.
6. Erstellt tag6/practice_bonus.py und registriert den Schülerrouter.
7. Ergänzt PATCH /students/{student_id} mit positiver Pfad-ID.
8. Übernehmt nur tatsächlich gesendete Werte mit exclude_unset=True.
9. Ein leerer Änderungsbody ergibt nach unserer Regel 400.
10. Prüft erhaltene Werte, fehlende IDs und ungültige Eingaben.

### Prüffälle

| PATCH /students/14 mit Body | Ergebnis |
| --- | --- |
| {"first_name":" Luna "} | 200; Luna, übrige Felder erhalten |
| {"last_name":" Lovegood "} | 200; Lovegood, übrige Felder erhalten |
| {} | 400; Keine Änderung gesendet. |
| {"first_name":null} | 422 |
| {"first_name":"   "} | 422 |
| {"school_year":3} | 422; unbekanntes Änderungsfeld |

- PATCH /students/999 mit gültigem Namen ergibt 404.
- Die Lösung darf fehlende Namen nicht durch None ersetzen.

Wenn ihr PATCH automatisiert prüft: Startet im Test mit einem abweichenden gespeicherten Wert, prüft die tatsächliche Änderung samt erneutem GET und stellt den ursprünglichen Datensatz in finally wieder her. Ein bereits gespeicherter Name mit zusätzlichen Rand-Leerzeichen prüft allein noch keine Änderung am Bestand.

<a id="aufgabe-11"></a>

## 11. Eine verschachtelte Buchungsvorschau ausgeben

Die Verwaltung möchte die beteiligten Schüler und Kurse direkt sehen.
Die Vorschau verwendet eigene Speicherbeispiele und keine MySQL-Abfrage.

### Aufgaben

1. Erstellt BookingPreview mit id, student und course.
2. Verwendet StudentRead und CourseRead als verschachtelte Modelle.
3. Erstellt GET /bookings in practice_bonus.py.
4. Verwendet den vorhandenen Schülerbestand und tag6/data.py für Kurse.
5. Baut Vorschau 101 aus Schüler 11 und Kurs 1.
6. Baut Vorschau 102 aus Schüler 12 und Kurs 3.
7. Gebt eine Liste mit response_model=list[BookingPreview] zurück.
8. Erklärt, warum ein Antwortschema weder Join noch Session erzeugt.
9. Prüft, dass interne Notizen auch in verschachtelten Antworten fehlen.

### Erfolgskriterien

- Erste Vorschau: Harry Potter und Arithmantik.
- Zweite Vorschau: Hermione Granger und Alte Runen.
- Vorschau-IDs 101 und 102 sind unabhängig von MySQL-Buchungs-IDs.
- student und course sind JSON-Objekte, keine JSON-Strings.
- Ein neu angelegter Schüler erzeugt keine zusätzliche Buchungsvorschau.
- Es werden keine realen Buchungen in MySQL angelegt.

### Bonus starten und sichern

```powershell
python -m uvicorn tag6.practice_bonus:app --reload --port 8002
```

