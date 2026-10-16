# REST und FastAPI – Übungen für Tag 5

## Überblick

Die Hogwarts-Verwaltung möchte Schüler über eine HTTP-Schnittstelle verwalten.
Ihr übertragt die Kurs-Endpunkte des Vormittags auf diese Ressource.
Plant zunächst den API-Vertrag. Entwickelt danach kleine überprüfbare Schritte.

- Pflichtaufgaben: 1–7; die API wird mit Postman geprüft.
- Bonusaufgaben: 8–11; eigene pytest-Tests sind freiwillig.
- Pflicht und Speicher-Bonus verwenden keine Datenbank.
- Die Tabellen und Berichte aus Tag 4 bleiben erhalten.
- Die Übungs-App verwendet eigene Daten und läuft auf Port 8001.
- Alle Codepfade gelten im Unterrichtsprojekt hogwarts-sql.
- Prüft bei jedem Aufruf Methode, URL, Status und Antwortinhalt.
- Beschreibt, was ein Objekt oder ein Listenelement fachlich bedeutet.
- POST-Anlagen bestehen nur im Speicher des jeweiligen Python-Prozesses.
- Neustart und Reload stellen den Startbestand wieder her.
- Vor festen Ergebniszahlen die betreffende App neu starten.

| Aufgabe | Verwaltungsauftrag |
| --- | --- |
| 1 | Den API-Vertrag für Schüler planen |
| 2 | Die eigene Übungs-App starten |
| 3 | Schüler als Sammlung und einzeln lesen |
| 4 | Schüler nach Haus auswählen |
| 5 | Eingabe und Antwort unterscheiden |
| 6 | Einen Schüler über POST anlegen |
| 7 | Erfolg und Fehler systematisch vergleichen |
| 8 | Bonus: zwei bekannte GET-Tests übertragen |
| 9 | Schülerzahlen nach Haus als Bericht liefern |
| 10 | Einen Speicher-Eintrag mit DELETE entfernen |
| 11 | Die echte Teilnehmerliste aus Tag 4 über HTTP lesen |

## HTTP-Aufrufe mit Postman

- Importiert [05-Tag5-Hogwarts.postman_collection.json][postman] in Postman.
- Die Collection heißt „Tag 5 – Hogwarts“. Für die Pflichtübungen den Ordner „02 Schüler – Pflicht“ öffnen.
- Die Variable `practice_url` enthält `http://127.0.0.1:8001`. Die Requests enthalten Methode, Endpoint und gegebenenfalls einen JSON-Body.
- Führt die Requests einzeln aus, sobald der jeweilige Endpunkt implementiert ist. Lest vorher den erwarteten Status in der Request-Beschreibung.
- Bei POST Body → raw → JSON prüfen. Die Datei new_student.json dient als eigene Vorlage; Postman liest sie nicht automatisch.
- Ein erfolgreiches „Cho anlegen“ speichert die Antwort-ID für „Angelegten Schüler lesen“ in `created_student_id`.
- Nach Serverneustart oder Reload den POST erneut senden. Vor festen Ergebniszahlen mit einem frischen App-Bestand beginnen.
- Jeder weitere POST-Klick erzeugt einen weiteren Schüler. Die Bonusordner erst mit der jeweils passenden App-Variante verwenden.

## Vor dem Start

- Verwendet das venv und die Pakete des Vormittags.
- requirements-tag5.txt steht vollständig im Skript.
- Die vollständigen Übungsdaten und Schemas stehen hier in Aufgabe 2 und 5.
- Ihr benötigt keine Übungslösung aus Tag 4.
- Der optionale Datenbank-Bonus benötigt den Live-Code aus Tag 4.

<a id="aufgabe-1"></a>

## 1. Den API-Vertrag für Schüler planen

Die Verwaltung braucht die Schülerliste, einzelne Schüler und eine Anlage.

### Aufgaben

1. Notiert Methode und Pfad für die Schülerliste.
2. Notiert Methode und Pfad für einen Schüler mit ID 12.
3. Notiert Methode und Pfad für die Anlage eines Schülers.
4. Legt für jeden erfolgreichen Aufruf den Statuscode fest. Recherchiert den passenden Statuscode.
5. Entscheidet, ob der Antwort-Body eine Liste oder ein Objekt enthält.
6. Erklärt, wo die neuen Schülerdaten bei der Anlage gesendet werden.
7. Erklärt den Unterschied zwischen einem Query-Parameter und einer ID im Pfad.


<a id="aufgabe-2"></a>

## 2. Die eigene Übungs-App starten

Die Verwaltung möchte prüfen, ob die neue Schüler-API erreichbar ist.

### Aufgaben

1. Übernehmt die beiden vollständigen Dateien aus dem Startmaterial.
2. Startet die App auf Port 8001.
3. Sendet „02 Schüler – Pflicht → Health prüfen“ in Postman und ruft /health auch im Browser auf.
4. Öffnet die Dokumentation unter /docs.
5. Notiert Status, Content-Type und JSON-Body der Health-Antwort.
6. Erklärt, was der Health-Aufruf tatsächlich prüft.

### Startmaterial: vollständiger Schülerbestand

<!-- file: tag5/practice_data.py -->
- Lokal: `.\tag5\practice_data.py`.

```python
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
```

### Startmaterial: vollständige erste App

<!-- file: tag5/practice.py -->
- Lokal: `.\tag5\practice.py`.

```python
from fastapi import FastAPI

app = FastAPI(title="Hogwarts-Schülerverwaltung – Übungen")


@app.get("/health")
def read_health():
    return {"status": "ok", "school": "Hogwarts"}
```

```powershell
python -m uvicorn tag5.practice:app --reload --host 127.0.0.1 --port 8001
```

- Dieses Terminal für den Server offen lassen.
- Die HTTP-Aufrufe in Postman senden. Eine zweite PowerShell wird nur beim freiwilligen pytest-Bonus benötigt.

In [Collection „Tag 5 – Hogwarts“][postman] diese Requests einzeln senden:

| Ordner → Request | Methode und Endpoint | Erwarteter Status |
| --- | --- | ---: |
| 02 Schüler – Pflicht → Health prüfen | `GET /health` | 200 |

### Erfolgskriterien

- Status 200 und Content-Type application/json.
- Antwort: status hat den Wert ok. school hat den Wert Hogwarts.
- http://127.0.0.1:8001/docs zeigt den Health-Endpunkt.
- Die App funktioniert ohne laufende MySQL-Datenbank.
- Der Health-Endpunkt behauptet keine geprüfte Datenbankverbindung.

<a id="aufgabe-3"></a>

## 3. Schüler als Sammlung und einzeln lesen

Die Verwaltung möchte alle Schüler sehen und Luna gezielt abrufen.

### Aufgaben

1. Ergänzt tag5/practice.py um GET /students.
2. Gebt alle Schüler als Liste aus und sortiert nach ID.
3. Ergänzt GET /students/{student_id} mit einem int-Parameter.
4. Sucht tatsächlich nach dieser ID im gegebenen Speicherbestand.
5. Gebt für einen fehlenden Schüler Status 404 und eine passende Meldung aus.
6. Ruft Luna mit ID 14, die fehlende ID 999 und den Text Luna als ID ab.
7. Notiert die Unterschiede der drei Antworten.

### Erfolgskriterien

- Die Sammlung enthält nach frischem Start sechs Schüler.
- Die IDs erscheinen in der Reihenfolge 11, 12, 13, 14, 15 und 16.
- GET /students/14 liefert Luna Lovegood aus Ravenclaw im zweiten Schuljahr.
- Das Einzelobjekt enthält id, first_name, last_name, house und school_year.
- ID 999 ergibt Status 404 und die Meldung Schüler nicht gefunden.
- Text statt Integer ergibt Status 422.
- Kein GET-Aufruf verändert den Bestand.

In [Collection „Tag 5 – Hogwarts“][postman] diese Requests einzeln senden:

| Ordner → Request | Methode und Endpoint | Erwarteter Status |
| --- | --- | ---: |
| 04 Bonus – DELETE → Restliche Schüler lesen | `GET /students` | 200 |
| 02 Schüler – Pflicht → Luna lesen | `GET /students/14` | 200 |
| 02 Schüler – Pflicht → Fehlende Schüler-ID | `GET /students/999` | 404 |
| 02 Schüler – Pflicht → Text als Schüler-ID | `GET /students/Luna` | 422 |

<a id="aufgabe-4"></a>

## 4. Schüler nach Haus auswählen

Die Verwaltung benötigt eine Liste für ein bestimmtes Haus.
Anders als bei der Titelsuche wird das ganze Haus verglichen.

### Aufgaben

1. Ergänzt GET /students um den optionalen Query-Parameter house.
2. Ohne house soll die vollständige Schülerliste erscheinen.
3. Bei house vergleicht den ganzen Hausnamen ohne Großschreibung.
4. Erhaltet die Sortierung nach Schüler-ID.
5. Gebt auch einen einzelnen Treffer als Liste aus.
6. Prüft einen vorhandenen Hausnamen und einen Wert ohne Treffer.
7. Erklärt, warum der Fall ohne Treffer kein fehlender Schüler ist.

### Erfolgskriterien

- house=gryffindor liefert Harry, Hermione, Ginny und Neville.
- Die zugehörigen IDs sind 11, 12, 15 und 16.
- house=Ravenclaw liefert Luna als einziges Listenelement.
- house=Gryff liefert keine Teiltreffer.
- house=Durmstrang liefert [] mit Status 200.
- Ohne Parameter erscheinen alle sechs Startschüler.
- Ein house-Wert von None in einem Datensatz verursacht keinen Fehler.

In [Collection „Tag 5 – Hogwarts“][postman] diese Requests einzeln senden:

| Ordner → Request | Methode und Endpoint | Erwarteter Status |
| --- | --- | ---: |
| 02 Schüler – Pflicht → Gryffindor filtern | `GET /students?house=gryffindor` | 200 |
| 02 Schüler – Pflicht → Ravenclaw filtern | `GET /students?house=Ravenclaw` | 200 |
| 02 Schüler – Pflicht → Hausname als Teilwort | `GET /students?house=Gryff` | 200 |
| 02 Schüler – Pflicht → Haus ohne Treffer | `GET /students?house=Durmstrang` | 200 |

<a id="aufgabe-5"></a>

## 5. Eingabe und Antwort unterscheiden

Die Verwaltung möchte einen Schüler anlegen. Seine ID soll die API vergeben.

### Aufgaben

1. Übernehmt die beiden vollständigen Schemas unten.
2. Erklärt, warum StudentCreate keine ID enthält.
3. Erklärt, warum StudentRead eine ID enthält.
4. Ordnet die Schemafelder den Schlüsseln in tag5/practice_data.py zu.
5. Verwendet StudentRead als response_model der beiden vorhandenen GET-Endpunkte. Die Sammlung liefert eine Liste von Schülern.
6. Schreibt einen gültigen JSON-Body für Cho Chang aus Ravenclaw, Schuljahr 4.
7. Legt ihn in tag5/new_student.json ab.
8. Nennt die Regeln, die StudentCreate bei einer Eingabe prüft.
9. Nennt mindestens eine fachliche Regel, die das Schema noch nicht prüft.

### Vollständiges Schema-Startmaterial

<!-- file: tag5/practice_schemas.py -->
- Lokal: `.\tag5\practice_schemas.py`.

```python
from pydantic import BaseModel, Field


class StudentCreate(BaseModel):
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    house: str | None = None
    school_year: int = Field(ge=1, le=7)


class StudentRead(BaseModel):
    id: int
    first_name: str
    last_name: str
    house: str | None
    school_year: int
```


<a id="aufgabe-6"></a>

## 6. Einen Schüler über POST anlegen

Die Verwaltung meldet Cho Chang über die API an.

### Aufgaben

1. Ergänzt tag5/practice.py um POST /students.
2. Nehmt StudentCreate als JSON-Body an.
3. Verwendet einen ID-Zähler ab 17, etwa itertools.count wie im Vormittag.
4. Speichert ID und Eingabefelder im gegebenen Schüler-Dictionary.
5. Gebt das neue Objekt mit StudentRead und Status 201 zurück.
6. Übertragt den JSON-Inhalt aus Aufgabe 5 in Body → raw → JSON des Requests „02 Schüler – Pflicht → Cho anlegen“. Sendet ihn und lest die Antwort-ID ab.
7. Sendet danach „02 Schüler – Pflicht → Angelegten Schüler lesen“. Die Antwort-ID wird automatisch als Collection-Variable übernommen.
8. Prüft, wie sich die Größe der Sammlung verändert hat.
9. Startet die App neu und erklärt den Unterschied im Datenbestand.

### Erfolgskriterien

- Das erste gültige POST nach frischem Start erzeugt ID 17.
- Die Antwort enthält Cho Chang, Ravenclaw und Schuljahr 4.
- Ein nachfolgender GET auf die Antwort-ID liefert dasselbe Objekt mit 200.
- Nach genau einem POST enthält die Sammlung sieben Schüler.
- Der Ravenclaw-Filter enthält danach Luna und Cho.
- Neustart und Reload stellen die sechs Startschüler wieder her.
- MySQL wurde durch die Übung nicht verändert.

In [Collection „Tag 5 – Hogwarts“][postman] diese Requests einzeln senden:

| Ordner → Request | Methode und Endpoint | Erwarteter Status |
| --- | --- | ---: |
| 02 Schüler – Pflicht → Cho anlegen | `POST /students` | 201 |

<a id="aufgabe-7"></a>

## 7. Erfolg und Fehler systematisch vergleichen

In [Collection „Tag 5 – Hogwarts“][postman] diese Requests einzeln senden:

| Ordner → Request | Methode und Endpoint | Erwarteter Status |
| --- | --- | ---: |
| 02 Schüler – Pflicht → Harry lesen | `GET /students/11` | 200 |
| 02 Schüler – Pflicht → Fehlende Schüler-ID | `GET /students/999` | 404 |
| 02 Schüler – Pflicht → Text als Schüler-ID | `GET /students/Luna` | 422 |
| 02 Schüler – Pflicht → Haus ohne Treffer | `GET /students?house=Durmstrang` | 200 |
| 02 Schüler – Pflicht → Schüler ohne Pflichtfelder | `POST /students` | 422 |
| 02 Schüler – Pflicht → Ungültiges Schuljahr | `POST /students` | 422 |
| 02 Schüler – Pflicht → DELETE ohne Implementierung | `DELETE /students/11` | 405 |
| 02 Schüler – Pflicht → Unbekannter Pfad | `GET /unknown` | 404 |
| 04 Bonus – DELETE → Restliche Schüler lesen | `GET /students` | 200 |

Die Verwaltung benötigt ein nachvollziehbares Prüfprotokoll.
Nicht jeder Fehler hat dieselbe Ursache.

### Aufgaben

1. Erstellt docs/tag5_http_checks.md im Unterrichtsprojekt.
2. Dokumentiert Methode, URL, Body, Status und beobachtetes Ergebnis.
3. Prüft einen erfolgreichen Abruf von Harry mit ID 11.
4. Prüft eine fehlende numerische ID und eine Text-ID.
5. Prüft einen Hausfilter ohne Treffer.
6. Sendet POST /students mit dem Body {}.
7. Sendet POST mit school_year: 8 und ansonsten gültigen Feldern.
8. Ruft DELETE /students/11 im Pflichtstand auf.
9. Ruft einen unbekannten Pfad auf.
10. Kontrolliert, dass ungültige POST-Aufrufe keine Schüler angelegt haben.
11. Erklärt zu jedem Fehler, welche Angabe korrigiert werden müsste.

### Erfolgskriterien

| Fall | Erwarteter Status |
| --- | ---: |
| Vorhandener Schüler | 200 |
| Fehlende numerische ID | 404 |
| Text-ID | 422 |
| Hausfilter ohne Treffer | 200 |
| Fehlende POST-Pflichtfelder | 422 |
| Schuljahr 8 | 422 |
| DELETE im Pflichtstand | 405 |
| Unbekannter Pfad | 404 |

- Der Hausfilter liefert []. Er ist eine erfolgreiche Auswahl.
- Das ungültige POST erhöht die Schülerzahl nicht.
- Im Bonus mit implementiertem DELETE ändert sich dessen Erwartung.
- Ein Body mit detail und Status 200 erfüllt den Fehlervertrag nicht.
- Fehlertexte der Standardvalidierung müssen nicht wortgleich sein.
- Erstellt docs bei Bedarf mit New-Item als Verzeichnis.

## Bonusaufgaben

Bearbeitet zuerst Aufgaben 1–7 einschließlich der Postman-Prüfungen. Die folgenden Aufgaben 8–11 sind freiwillig. Tag 6 setzt keine eigene pytest-Lösung aus Tag 5 voraus.

<a id="aufgabe-8"></a>

## 8. Bonus: zwei bekannte GET-Tests übertragen

Übertragt die beiden fertigen GET-Tests aus dem Vormittag auf die Schüler-App. Ihr sollt das bekannte Muster nachvollziehen, noch keine vollständige Testsammlung entwerfen.

### Aufgaben

1. Kopiert die vollständige Testdatei tag5/test_main.py nach tag5/test_practice.py. Behaltet den TestClient-Import und seine Initialisierung bei; importiert app nun aus tag5.practice.
2. Ändert den vorhandenen Kursabruf zu GET /students/14. Erwartet Status 200 und das vollständige öffentliche Objekt für Luna aus dem Startbestand.
3. Ändert den fehlenden Kursabruf zu GET /students/999. Erwartet Status 404 und {"detail": "Schüler nicht gefunden."}.
4. Benennt die Funktionen passend zu ihren Schüler-Prüfungen.
5. Führt die Tests aus. Ändert eine erwartete Angabe absichtlich, erklärt die fehlgeschlagene Prüfung und korrigiert sie anschließend wieder.

```powershell
python -m pytest -q tag5/test_practice.py
```

### Erfolgskriterien

- Zwei GET-Tests bestehen ohne gestarteten Uvicorn-Server.
- Ihr könnt erklären, was TestClient tut, was pytest tut und welche Erwartung jedes assert prüft.
- Die Tests ändern keine Daten; eine Bereinigung ist daher hier nicht nötig.
- Die Pflichtprüfungen von POST, Filtern und Fehlerfällen stehen weiterhin in Aufgaben 3–7 und werden mit Postman ausgeführt.
- Systematischer Testentwurf, Parametrisierung und Fixtures folgen an Tag 8.

<a id="aufgabe-9"></a>

## 9. Schülerzahlen nach Haus als Bericht liefern

In [Collection „Tag 5 – Hogwarts“][postman] diese Requests einzeln senden:

| Ordner → Request | Methode und Endpoint | Erwarteter Status |
| --- | --- | ---: |
| 03 Bonus – Hausbericht → Schülerzahlen nach Haus | `GET /reports/students-by-house` | 200 |
| 03 Bonus – Hausbericht → Cho anlegen | `POST /students` | 201 |
| 03 Bonus – Hausbericht → Schüler ohne Haus anlegen | `POST /students` | 201 |

Die Verwaltung benötigt die Anzahl ihrer Schüler pro Haus.
Plant die Ergebnisform selbst. Übertragt das Gruppierungsdenken aus Tag 4.

### Aufgaben

1. Erstellt tag5/practice_counts.py als Erweiterung der vorhandenen Übungs-App.
2. Importiert app aus tag5.practice und students aus tag5.practice_data.
3. Ergänzt GET /reports/students-by-house.
4. Liefert pro Haus ein Objekt mit house und student_count.
5. Zählt jeden vorhandenen Schüler genau einmal.
6. Sortiert nach Haus. Eine Gruppe ohne Haus soll zuerst erscheinen.
7. Prüft den Bericht nach Start und nach einer gültigen Schüleranlage.
8. Prüft außerdem eine gültige Anlage ohne house.

### Erfolgskriterien

- Nach Start: Gryffindor 4, Ravenclaw 1 und Slytherin 1.
- Die Summe der Kennzahlen entspricht immer der Zahl der Schüler.
- Nach Cho Changs Anlage hat Ravenclaw den Wert 2.
- Eine Anlage ohne Haus erscheint in einer eigenen Gruppe mit house: null.
- Der Bericht verändert keine Daten.

```powershell
python -m uvicorn tag5.practice_counts:app --host 127.0.0.1 --port 8001
```

<a id="aufgabe-10"></a>

## 10. Einen Speicher-Eintrag mit DELETE entfernen

In [Collection „Tag 5 – Hogwarts“][postman] diese Requests einzeln senden:

| Ordner → Request | Methode und Endpoint | Erwarteter Status |
| --- | --- | ---: |
| 04 Bonus – DELETE → Draco löschen – erster Aufruf | `DELETE /students/13` | 204 |
| 04 Bonus – DELETE → Draco nach Löschung lesen | `GET /students/13` | 404 |
| 04 Bonus – DELETE → Draco löschen – zweiter Aufruf | `DELETE /students/13` | 404 |
| 04 Bonus – DELETE → Restliche Schüler lesen | `GET /students` | 200 |

Die Verwaltung möchte Draco aus dem heutigen Übungsbestand entfernen.
Die Antwort soll bei erfolgreicher Löschung keinen Body enthalten.

### Aufgaben

1. Erstellt tag5/practice_delete.py als weitere Erweiterungsvariante.
2. Importiert die Übungs-App und ihren Speicherbestand.
3. Ergänzt DELETE /students/{student_id} mit einem int-Parameter.
4. Entfernt bei vorhandener ID genau diesen Speichereintrag.
5. Gebt Status 204 und keinen Antwort-Body zurück.
6. Gebt bei fehlender ID Status 404 zurück.
7. Prüft DELETE für ID 13, den anschließenden GET und ein zweites DELETE.
8. Erklärt, warum unterschiedliche Antworten die Löschwirkung nicht ändern.

### Erfolgskriterien

- Erstes DELETE: 204 und leerer Body.
- Danach GET /students/13: 404.
- Zweites DELETE auf dieselbe ID: 404.
- Nach der Löschung sind fünf Startschüler im Speicher übrig.
- Ein Neustart stellt den Schüler wieder her.
- Die MySQL-Tabellen bleiben unverändert.

```powershell
python -m uvicorn tag5.practice_delete:app --host 127.0.0.1 --port 8001
```

<a id="aufgabe-11"></a>

## 11. Die echte Teilnehmerliste aus Tag 4 über HTTP lesen

In [Collection „Tag 5 – Hogwarts“][postman] diese Requests einzeln senden:

| Ordner → Request | Methode und Endpoint | Erwarteter Status |
| --- | --- | ---: |
| 05 Bonus – Tag-4-Berichte → Kursbuchungen lesen | `GET /reports/course-bookings` | 200 |
| 05 Bonus – Tag-4-Berichte → Teilnehmer Wahrsagen | `GET /courses/2/participants` | 200 |
| 05 Bonus – Tag-4-Berichte → Teilnehmer leerer Kurs | `GET /courses/{{empty_course_id}}/participants` | 200 |
| 05 Bonus – Tag-4-Berichte → Teilnehmer fehlender Kurs | `GET /courses/999/participants` | 404 |
| 05 Bonus – Tag-4-Berichte → Text als Kurs-ID | `GET /courses/AlteRunen/participants` | 422 |

Die Verwaltung möchte Buchungsdaten aus MySQL in einem HTTP-Client verwenden.
Hier werden die vorhandenen Berichte aus dem Live-Unterricht eingesetzt.

### Aufgaben

1. Erstellt tag5/report_api.py als separate App auf Port 8002.
2. Nutzt course_summary und course_register aus tag4.reports.
3. Ergänzt GET /reports/course-bookings um die vorhandenen Berichtsfelder.
4. Ergänzt GET /courses/{course_id}/participants mit einem int-Parameter.
5. Prüft, ob der Kurs existiert, bevor ihr die Teilnehmerliste zurückgebt.
6. Unterscheidet einen leeren vorhandenen Kurs von einer unbekannten ID.
7. Lest die tatsächliche ID von Zaubertrankpraxis aus dem Kursbericht ab und tragt sie in der Collection-Variable empty_course_id ein.
8. Ruft Wahrsagen und das leere Angebot ab.
9. Beschreibt, wie die Python-Datumswerte in JSON erscheinen.
10. Behandelt SQLAlchemyError mit Status 503 und einer kurzen Meldung.

### Erfolgskriterien

- Der Bericht enthält fünf Kursobjekte, auch das leere Angebot mit Zahl 0.
- Es werden die tatsächlichen MySQL-IDs verwendet, nicht die Speicher-IDs.
- Wahrsagen mit ID 2 liefert Harry und Ron mit ihren Buchungsdaten.
- Der vorhandene leere Kurs liefert 200 mit [].
- Ein unbekannter Kurs liefert 404. Eine Text-ID liefert 422.
- Datumswerte erscheinen als ISO-Zeichenketten, etwa 1993-09-01.
- Datenbankzugriffe werden durch die vorhandenen Berichte durchgeführt.
- Kein Kurs und keine Buchung wird in MySQL angelegt oder verändert.
- Die optionale NOT-EXISTS-Vertiefung aus Tag 4 wird nicht benötigt.
- Die vorübergehenden POST-Anlagen aus dem Pflichtteil erscheinen hier nicht.

```powershell
docker compose up -d --wait
python -m uvicorn tag5.report_api:app --host 127.0.0.1 --port 8002
```

- Die vorhandene .env verwenden.
- Den Report-Ordner in Postman öffnen.

## Abschlusskontrolle

- Pflicht-App nach Neustart: sechs Startschüler.
- Alle Pflichtfälle aus Aufgaben 1–7 wurden mit Postman geprüft und protokolliert.
- Nur bei bearbeitetem Bonus 8: Beide GET-Tests bestehen.
- Die Übungsdateien verwenden ausschließlich den eigenen Speicherbestand.
- Der Datenbank-Bonus liest nur die Live-Daten aus Tag 4.
- MySQL bleibt bei zehn Schülern, fünf Kursen und neun Buchungen.

[postman]: ../assets/05-Tag5-Hogwarts.postman_collection.json
