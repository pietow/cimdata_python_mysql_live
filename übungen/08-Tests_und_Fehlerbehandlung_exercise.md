# Tests und Fehlerbehandlung – Übungen für Tag 8

## Überblick

Die Hogwarts-Verwaltung will Änderungen an der Buchungs-API sicher prüfen.
Ihr ergänzt Tests für Grenzen, fehlende Daten und fehlgeschlagene Aufträge.
Die Anwendung aus dem Vormittag bleibt die gemeinsame Grundlage.

- Pflicht: Aufgaben 1–7. Bonus: Aufgaben 8–10.
- Verwendet pip, das vorhandene venv und die bisherigen Modelle aus tag7.
- Erstellt neue Testdateien unter tests/tag8.
- Übernehmt die vorhandenen Fixtures aus tests/tag8/conftest.py.
- Datenbanktests verwenden ausschließlich die MySQL-Datenbank hogwarts_test. (siehe /compose.test.yaml)
- Reine Schema- und Regeltests benötigen keine Datenbankverbindung.
- Führt Datenbanktests nacheinander aus, nicht parallel.
- TestClient benötigt keinen gestarteten Entwicklungsserver.
- Die eigentliche Anwendung bleibt unverändert.

| Aufgabe | Auftrag |
| --- | --- |
| 1 | Einen Prüfplan erstellen |
| 2 | Schemas und Titelgrenzen prüfen |
| 3 | Pfad, Query und Antwortvertrag prüfen |
| 4 | Fehlende Verweise und Rollback prüfen |
| 5 | Einen Löschkonflikt selbstständig absichern |
| 6 | Unabhängige Tests nachweisen |
| 7 | Fachliche Ablehnung und Logeinträge prüfen |
| 8 | Bonus: Alle Wahlfächer und Flugkunde prüfen |
| 9 | Bonus: Eine bestehende Ausnahme erhalten |
| 10 | Bonus: Coverage richtig einordnen |

## Vor dem Start

- Alembic hat die Testdatenbank bis Revision 0002 eingerichtet.
- Die echte .env.test enthält eure lokalen Testzugangsdaten.
- Die normale .env bleibt für die vorhandenen Projektimporte verfügbar.
- Die zwölf Testfälle aus dem Vormittag müssen bestehen.


```powershell
$testCompose = @(
    "--env-file", ".env.test", "-f", "compose.test.yaml"
)
docker compose @testCompose up -d --wait
python -m tag8.init_test_db
python -m pytest .\tests\tag8 -q
```

### Verfügbare Fixtures

| Fixture | Verwendung |
| --- | --- |
| client | Health und isolierte Fehlerfälle ohne echte Datenbank |
| api_client | API mit einer neuen Test-Session pro Request |
| db_factory | Session-Fabrik; db_factory() öffnet eine neue Session zum Nachlesen |
| seed | Vier Schüler, drei Kurse und deren tatsächliche IDs |
| caplog | Logeinträge im aktuellen Test untersuchen  # kommt später

- seed legt Harry und Hermione in Schuljahr 3 an.
- Luna und Ginny besuchen im Test Schuljahr 2.
- course_id gehört zu Alte Runen, other_course_id zu Flugkunde.
- empty_course_id gehört zu Astronomie.
- Schüler-IDs heißen harry_id, hermione_id, luna_id und ginny_id.
- Zu Beginn eines Tests mit seed gibt es keine Buchungen.
- db_factory allein legt keine Schüler oder Kurse an.
- seed und api_client teilen im selben Test eine db_factory; pytest bereitet sie nur einmal vor.
- Vor und nach dem Test wird aufgeräumt, nicht zwischen dessen Requests.
- Der Scope session von test_engine meint den Testlauf, keine gemeinsame DB-Session.
- Verwendet api_client für normale Datenbankrouten. client hat keinen DB-Override.
- IDs werden aus seed gelesen. Erwartet keine festen Zahlen.
- Für eine sicher fehlende ID genügt hier die größte Seed-ID plus 1000.
- Das gilt für diesen kontrollierten Testbestand, nicht allgemein für MySQL.

<a id="aufgabe-1"></a>

## 1. Einen Prüfplan erstellen

Die Verwaltung möchte wissen, welche Risiken eure Tests abdecken.

### Aufgaben

1. Erstellt eine Tabelle mit Fall, Vorbereitung und erwarteter Wirkung.
2. Plant eine erlaubte Buchung für Harry und eine abgelehnte für Luna.
3. Plant einen Gruppenauftrag mit Harry und einer fehlenden Schüler-ID.
4. Plant das Löschen eines bereits gebuchten Kurses.
5. Plant eine nicht erreichbare Datenbank.
6. Ordnet jedem Fall Unit-Test, API-Test oder Integrationstest zu.
7. Nennt jeweils eine HTTP-, Daten- oder Log-Assertion, die nötig ist.

### Erfolgskriterien

- Der Plan unterscheidet den Vertrag der API vom gespeicherten Zustand.
- Bei Gruppenfehlern darf keine Teilbuchung zurückbleiben.
- Für den Ausfall wird eine sichere 503-Antwort erwartet.
- Ihr könnt erklären, warum eine richtige 409 allein nicht ausreicht.

<a id="aufgabe-2"></a>

## 2. Schemas und Titelgrenzen prüfen

Kurse brauchen verständliche Titel. Zusätzliche Eingabefelder sind verboten.

- Datei: tests/tag8/test_practice_schemas.py.
- Verwendet CourseCreate aus tag7.schemas und ValidationError aus pydantic.
- Für diese Aufgabe wird keine DB-Fixture benötigt.

### Aufgaben

1. Prüft mit parametrize die gültigen Werte in der Tabelle.
2. Prüft die ungültigen Werte mit pytest.raises.
3. Prüft, dass eine mitgesendete id im Eingabe-Dictionary abgelehnt wird.
4. Verwendet für den dritten Test CourseCreate.model_validate.
5. Erklärt den Unterschied zwischen Eingabemodell und Datenbankmodell.

| Eingabe | Erwartung |
| --- | --- |
| Astronomie | Titel bleibt Astronomie |
| Flugkunde mit äußeren Leerzeichen | Titel wird Flugkunde |
| 100-mal A | Titel wird angenommen |
| Leerer String | ValidationError |
| Nur drei Leerzeichen | ValidationError |
| 101-mal A | ValidationError |
| Titel Flugkunde und zusätzlich id 17 | ValidationError |

### Erfolgskriterien

- Sieben Testfälle bestehen.
- Die gültigen Fälle vergleichen den tatsächlichen normalisierten Titel.
- Die ungültigen Fälle erwarten gezielt ValidationError.
- Es werden keine neuen Kurse gespeichert.

<a id="aufgabe-3"></a>

## 3. Pfad, Query und Antwortvertrag prüfen

Ein Aufrufer muss ungültige Eingaben von fehlenden Kursen unterscheiden.

- Datei: tests/tag8/test_practice_contract.py.
- Verwendet api_client; bei vorhandenen Kursen zusätzlich seed.

### Aufgaben

1. Ruft GET /courses/{course_id} mit 0, -1 und Luna als Pfadwert auf.
2. Erwartet 422 und den Fehlerort path, course_id im JSON-Feld loc.
3. Ruft einen fehlenden positiven Kurs auf und erwartet 404.
4. Prüft dabei die Meldung „Kurs nicht gefunden.“.
5. Prüft q mit einem Zeichen und mit 101 Zeichen an GET /courses.
6. Erwartet 422 und den Fehlerort query, q.
7. Prüft GET /courses/count mit seed: 200 und exakt count gleich 3.
8. Sucht mit q=Run. Erwartet ausschließlich Alte Runen mit room null.
9. Erklärt, warum /courses/count nicht als Kurs-ID interpretiert werden darf.

### Erfolgskriterien

- Prüft die Zählroute und die Suche in zwei getrennten Testfunktionen.
- In der Referenzlösung entstehen dadurch acht Fälle. Entscheidend sind die
  abgedeckten Erwartungen, nicht eine identische Aufteilung eurer Funktionen.
- Der Test unterscheidet 422 von 404.
- Die Suchantwort enthält die tatsächliche Kurs-ID aus seed.
- Prüft ausgewählte Fehlerfelder statt der gesamten Versionsmeldung.

<a id="aufgabe-4"></a>

## 4. Fehlende Verweise und Rollback prüfen

Ein Gruppenauftrag darf bei fehlenden Schülern keine Teilbuchung erzeugen.

- Datei: tests/tag8/test_practice_missing.py.
- Verwendet api_client, seed und db_factory.
- Verwendet für neue Buchungen das Datum 1993-09-06.

### Aufgaben

1. Bucht Alte Runen zuerst für Harry und danach für eine fehlende Schüler-ID.
2. Sendet beide IDs in einem POST an /booking-batches.
3. Erwartet 404 und „Schüler nicht gefunden.“.
4. Zählt Booking-Zeilen mit einer neuen Session aus db_factory.
5. Erwartet null Zeilen, obwohl Harry zuerst verarbeitet wurde.
6. Schreibt einen zweiten Test für einen fehlenden Zielkurs mit Harry.
7. Erwartet 404, „Kurs nicht gefunden.“ und erneut keine Buchung.

### Erfolgskriterien

- Zwei unabhängige Testfälle bestehen.
- Die Datenbankprüfung erfolgt nach dem Request in einer neuen Session.
- Ein Vergleich nur mit der HTTP-Antwort genügt nicht.
- Ihr erklärt, warum die Reihenfolge der Schüler im ersten Test wichtig ist.

<a id="aufgabe-5"></a>

## 5. Einen Löschkonflikt selbstständig absichern

Die Verwaltung meldet: „Ein bereits gebuchter Kurs darf beim Löschen weder
verschwinden noch seine Buchungen verlieren. Der Aufrufer braucht eine
verständliche Konfliktmeldung.“

- Datei: tests/tag8/test_practice_delete.py.
- Nutzt die bekannte API und die vorhandenen Fixtures.
- In dieser Aufgabe wählt ihr Vorbereitung, Request und Assertions selbst.

### Aufgaben

1. Formuliert vor dem Code einen Prüfplan mit Arrange, Act und Assert.
2. Entscheidet, welche Ausgangsdaten den gemeldeten Konflikt tatsächlich erzeugen.
3. Schreibt einen unabhängigen Test für diesen fachlichen Auftrag.
4. Begründet, welche Beobachtungen an HTTP-Antwort und Datenbestand nötig sind.
5. Erklärt, welchen fehlerhaften Endpunkt ein reiner Statuscode-Test übersehen würde.

### Erfolgskriterien

- Die Vorbereitung erzeugt nachweislich eine echte Buchung auf den betroffenen Kurs.
- Der Löschversuch meldet den im API-Vertrag vorgesehenen Konflikt.
- Der betroffene Kurs und seine Buchungen bleiben inhaltlich unverändert.
- Mindestens eine unabhängige DB-Abfrage nach dem Request sichert den gespeicherten Zustand ab.
- Der Test funktioniert allein, ohne feste IDs und ohne vorherige Testläufe.
- Ihr könnt jede Assertion einer fachlichen Anforderung zuordnen.

### Gestufte Hilfen – erst nach einem eigenen Versuch

1. Lest den Lösch-Endpunkt im Kursrouter aus Tag 7 und dessen Fehlervertrag.
2. Fragt euch, welche Fremdschlüsselreferenz das Löschen verhindert.
3. Vergleicht einen vorher erfassten Buchungsbestand mit dem Zustand danach.

<a id="aufgabe-6"></a>

## 6. Unabhängige Tests nachweisen

Ein Test darf keinen bestimmten Vorgänger benötigen.

- Datei: tests/tag8/test_practice_isolation.py.

### Aufgaben

1. Schreibt test_one_test_can_create_a_booking mit api_client und seed.
2. Legt eine Buchung an und erwartet anschließend genau eine Buchung.
3. Schreibt test_another_test_starts_without_bookings mit denselben Fixtures.
4. Erwartet dort 200 und eine leere Buchungsliste, ohne selbst zu löschen.
5. Führt beide Tests zusammen und anschließend in umgekehrter Reihenfolge aus.
6. Beobachtet mit --setup-show die Fixture-Vorbereitung und das Aufräumen.
7. Erklärt, warum gleiche IDs zwischen Tests keine Voraussetzung sind.

### Erfolgskriterien

- Beide Reihenfolgen bestehen.
- Kein Test ruft einen anderen Test auf.
- Das Aufräumen erfolgt durch die gemeinsame Fixture.
- Ein Test für sich allein besteht ebenfalls.

<a id="aufgabe-7"></a>

## 7. Fachliche Ablehnung und Logeinträge prüfen

Ein fehlgeschlagener Gruppenauftrag darf nicht als Erfolg protokolliert werden.

- Datei: tests/tag8/test_practice_logs.py.
- Verwendet caplog, api_client, seed und db_factory.

### Aufgaben

1. Parametrisiert den zweiten Schüler mit luna_id und ginny_id.
2. Bucht zuerst Harry und danach den jüngeren Schüler für Alte Runen.
3. Aktiviert caplog ab INFO für den Logger hogwarts.
4. Erwartet 409 und „Wahlfächer sind ab Schuljahr 3 buchbar.“.
5. Prüft, dass keine Booking-Zeile gespeichert wurde.
6. Erwartet genau eine Warnung des Loggers hogwarts.api.
7. Erwartet den Text booking_batch_rejected reason=school_year.
8. Prüft, dass keine Nachricht booking_batch_saved enthält.

### Erfolgskriterien

- Zwei Testfälle bestehen.
- HTTP-Antwort, DB-Zustand, Loggername und Level werden geprüft.
- Fremde Logeinträge werden bei der Warnungszählung herausgefiltert.
- Die fehlende Erfolgsmeldung wird ausdrücklich nachgewiesen.

<a id="aufgabe-8"></a>

## 8. Bonus: Alle Wahlfächer und Flugkunde prüfen

Die Regel soll für alle vier bekannten Wahlfächer gelten.

- Datei: tests/tag8/test_bonus_rules.py.

### Aufgaben

1. Prüft Arithmantik, Wahrsagen, Alte Runen und Tierwesenpflege.
2. Verwendet für Tierwesenpflege den Titel Pflege magischer Geschöpfe.
3. Prüft jeden Titel mit Schuljahr 2 und 3 über die reine Funktion.
4. Schreibt die erwarteten Titel im Test ausdrücklich auf.
5. Übernehmt die Testwerte nicht aus ELECTIVE_COURSES der Implementierung.
6. Prüft zusätzlich über die API, dass Luna Flugkunde buchen darf.
7. Prüft 201 sowie Schüler- und Kurs-ID in der Antwort.

### Erfolgskriterien

- Acht Regelkombinationen und ein API-Fall bestehen.
- Jahr 2 löst nur für ein Wahlfach SchoolYearTooLow aus.
- Jahr 3 ist zugelassen. Flugkunde ist auch für Luna zulässig.
- Eine versehentlich aus der Implementierung entfernte Auswahl wird entdeckt.

<a id="aufgabe-9"></a>

## 9. Bonus: Eine bestehende Ausnahme erhalten

Lunas alte Buchung für Alte Runen muss weiterhin lesbar bleiben.

- Datei: tests/tag8/test_bonus_legacy.py.
- Bildet die Ausnahme ausschließlich in hogwarts_test nach.

### Aufgaben

1. Speichert über db_factory.begin eine Buchung für Luna in Alte Runen.
2. Verwendet dafür das Datum 1993-09-01 und merkt euch die erzeugte ID.
3. Erklärt, warum hier die DB statt der neuen Buchungs-API verwendet wird.
4. Prüft mit GET /bookings alle Felder dieser bestehenden Buchung.
5. Sendet danach einen neuen Buchungsauftrag für Luna am 1993-09-06.
6. Erwartet 409. Prüft anschließend den unveränderten Altbestand.

### Erfolgskriterien

- Genau die bestehende Ausnahme bleibt erhalten und lesbar.
- Eine neue Buchung mit derselben fachlichen Voraussetzung wird abgelehnt.
- Die Testvorbereitung verändert keine echten Unterrichtsdaten.
- Mit beiden Bonusdateien umfasst die Referenzlösung 44 Testfälle.

