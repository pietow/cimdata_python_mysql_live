# Komplexere Abfragen und Hogwarts – Teilnehmerskript

Tag 4 des Kurses „Programmierung mit Python für komplexe Datenbanken“.

- Die Abschnitte folgen der Reihenfolge des Unterrichts.
- Ausgangspunkt ist der vollständige Live-Stand aus [Tag 3][tag3].
- SQL kommt zuerst. Danach verwenden wir drei Berichte in Python.
- Jeder vollständige Codeblock nennt seine Datei und den passenden Aufruf.
- Die freiwilligen Vertiefungen sind ausdrücklich gekennzeichnet.

## Ziel des Tages

- Daten aus Schülern, Kursen und Buchungen gemeinsam auswerten.
- INNER JOIN und LEFT JOIN passend zur Datenfrage wählen.
- Buchungszeilen und verschiedene Personen unterschiedlich zählen.
- Gesamtwerte berechnen und Gruppen mit GROUP BY bilden.
- Einzelzeilen mit WHERE und Gruppen mit HAVING filtern.
- Eine Auswahl mit einer IN-Unterabfrage beschreiben.
- Zwei Auswertungen mit SQLAlchemy in Python verwenden.
- Objektzugriff und ausdrücklich aufgebaute Abfragen unterscheiden.

Die Hogwarts-Verwaltung kann Schüler, Kurse und Buchungen speichern.
Heute braucht sie verständliche Teilnehmerlisten und Kursübersichten.
Auch ein Angebot ohne Buchung soll in der Übersicht erscheinen.
Du entwickelst die Abfragen zuerst in SQL und nutzt ausgewählte in Python.
Die Tabellenstruktur und die vorhandenen Modelle bleiben erhalten.

## Auswertungen auf einen Blick

| Du möchtest … | Werkzeug | Abschnitt |
|---|---|---|
| nur passende Zeilen kombinieren | INNER JOIN und ON | 2 |
| auch Zeilen ohne Partner behalten | LEFT JOIN | 3 |
| nur bestimmte Partner ergänzen | zusätzliche Bedingung im ON | 3.2 |
| Ergebniszeilen zählen | COUNT(*) | 4 |
| vorhandene Werte zählen | COUNT(Spalte) | 4 |
| verschiedene Werte zählen | COUNT(DISTINCT Spalte) | 4–5, 7 |
| Grenzen und Mittelwerte bestimmen | MIN, MAX und AVG | 4 |
| eine Zeile je Kurs bilden | GROUP BY | 5.1 |
| einzelne Zeilen auswählen | WHERE | 5.3 |
| berechnete Gruppen auswählen | HAVING | 5.2–5.3 |
| Zugehörigkeit zu einer Auswahl prüfen | IN mit Unterabfrage | 6.1 |
| fehlende Treffer prüfen | NOT EXISTS, freiwillig | 6.2 |
| einen Beziehungspfad in SQL nutzen | join(Booking.student) | 8 |
| eine berechnete Spalte benennen | label | 8 |
| Ergebniszeilen über Namen lesen | mappings und dict | 8 |

> **💡 Merke: Erst die Frage, dann die Abfrage**
> Lege fest, was eine Ergebniszeile bedeuten soll.
> Entscheide dann, welche Tabellen und welche Verknüpfungen du brauchst.
> Die richtige Zeilenzahl allein genügt nicht. Prüfe auch die Inhalte.

## 0. Vom Speichern zum Auswerten

Eine Teilnehmerliste braucht Namen statt bloßer Schüler-IDs.
Eine Kursübersicht braucht Zahlen, ohne leere Angebote zu übersehen.
Das sind neue Abfragen auf demselben Datenbestand.

| Bestand zu Beginn | Erwartung nach dem vollständigen Tag 3 |
|---|---|
| students | Zehn Schüler |
| courses | Vier ursprüngliche Angebote |
| bookings | Neun Buchungen |
| Nora aus Tag 2 | Buchung für Kurs 1 am 4. September 1993 |
| Elias aus Tag 3 | Buchung für Kurs 1 am 5. September 1993 |
| ORM | Student, Course, Booking mit ihren Beziehungen |

- Nora, Elias und Alex sind vorhandene Beispieldaten der bisherigen Tage.
- Heute wird nur ein zusätzliches Kursangebot angelegt.
- Alle folgenden Live-Auswertungen lesen Daten.
- Die Übungsaufgaben am Nachmittag verwenden eigene practice4-Tabellen.

### Projekt und MySQL-Client öffnen

In PowerShell:

```powershell
Set-Location "$env:USERPROFILE\hogwarts-sql"
.\.venv\Scripts\Activate.ps1
python -c "import sys; print(sys.executable)"
git status --short
docker compose up -d --wait
docker compose ps
New-Item -ItemType Directory -Force -Path .\tag4
New-Item -ItemType Directory -Force -Path .\sql\tag4
docker compose exec db mysql --user=dumbledore --password hogwarts
```

Gib das bereits eingerichtete Datenbankpasswort ein.
Lass diesen Client geöffnet. Öffne eine zweite PowerShell für Python und Git.

| Eingabestelle | Hier eingeben |
|---|---|
| PowerShell im Projekt hogwarts-sql | Python, pip, Docker und Git |
| MySQL-Client mit mysql> | SQL und SOURCE |

- MySQL läuft weiterhin im Docker-Container.
- Python läuft lokal im vorhandenen venv.
- pip und die Pakete aus Tag 3 werden weiterverwendet.
- Du brauchst heute keine neue Umgebung und keine weitere Bibliothek.
- Die SQL-Dateien unter sql liegen im Container unter /work/sql.

> **⚠️ Pitfall: Die Aktivierung der Umgebung ist blockiert**
> Verwende dann ..venvScriptspython.exe direkt statt python.
> Prüfe den Interpreter, bevor du Pakete in ein anderes Python installierst.

### Den Ausgangsbestand prüfen

Datei `sql\tag4\00_start_check.sql`:

<!-- file: sql/tag4/00_start_check.sql -->

```sql
USE hogwarts;

SELECT 'students' AS table_name, COUNT(*) AS row_count FROM students
UNION ALL
SELECT 'courses', COUNT(*) FROM courses
UNION ALL
SELECT 'bookings', COUNT(*) FROM bookings;

SELECT id, title FROM courses ORDER BY id;
SELECT s.first_name, s.last_name, b.course_id, b.booking_date
FROM students AS s
INNER JOIN bookings AS b ON b.student_id = s.id
WHERE (s.first_name = 'Nora' AND s.last_name = 'Winter')
   OR (s.first_name = 'Elias' AND s.last_name = 'Brook')
ORDER BY s.first_name;
```

Laden: `SOURCE /work/sql/tag4/00_start_check.sql;`

<details>
<summary>Erwartung</summary>

Zehn Schüler, vier Kurse und neun Buchungen.
Nora hat Kurs 1 am 4. September 1993 gebucht.
Elias hat Kurs 1 am 5. September 1993 gebucht.
Die Kursliste enthält Arithmantik, Wahrsagen und Alte Runen.
Dazu kommt Pflege magischer Geschöpfe.

</details>

- Bei fehlendem Elias hole die erfolgreiche Anmeldung aus Tag 3 nach.
- Übernimm keine Übungstabellen aus Tag 3 als Ersatz für den Live-Bestand.
- Prüfe vorhandene zusätzliche Angebote, bevor du Daten erneut anlegst.
- Die IDs neuer Datensätze müssen nicht lückenlos sein.

> **⚠️ Pitfall: Erneut alle Startdaten importieren**
> Lade die INSERT-Dateien früherer Tage nicht pauschal erneut.
> Prüfe bei einem abweichenden Bestand zuerst die konkreten Datensätze.
> Setze dafür weder Tabellen noch das Daten-Volume zurück.

## 1. Beziehungen und Auswertungsfragen unterscheiden

Eine Buchung verbindet einen Schüler mit einem Kurs.
Das Buchungsdatum gehört zu dieser Verbindung.

- students enthält Schülerdaten.
- courses enthält Angebote.
- bookings enthält student_id, course_id und booking_date.
- Jede Buchung verweist auf einen Schüler und einen Kurs.
- Ein Schüler kann mehrere Buchungen besitzen.
- Ein Kurs kann mehrere Buchungen besitzen oder noch keine.
- Schüler und Kurse sind über die Buchungen n:m verbunden.

Die gespeicherte Beziehung legt noch keine fertige Teilnehmerliste fest.
Du entscheidest mit einer Abfrage, welche Zeilen und Spalten benötigt werden.

### Ein ungebuchtes Angebot ergänzen

Die Verwaltung plant „Zaubertrankpraxis“.
Das neue Angebot bleibt zunächst ohne Buchung.
So kannst du prüfen, ob deine Auswertung auch leere Angebote zeigt.

Datei `sql\tag4\01_empty_course.sql`:

<!-- file: sql/tag4/01_empty_course.sql -->

```sql
USE hogwarts;

INSERT INTO courses (title) VALUES ('Zaubertrankpraxis');
SET @new_course_id = LAST_INSERT_ID();
SELECT id, title FROM courses WHERE id = @new_course_id;
```

Laden: `SOURCE /work/sql/tag4/01_empty_course.sql;`

<details>
<summary>Erwartung</summary>

Ein neuer Kurs mit einer von MySQL vergebenen ID.
Insgesamt fünf Kurse, weiterhin zehn Schüler und neun Buchungen.
Notiere die neue ID. Sie muss nicht 5 sein.
Das Angebot bleibt als Grundlage für die nächsten Tage erhalten.

</details>

- LAST_INSERT_ID liefert hier die gerade erzeugte Auto-ID dieser Verbindung.
- @new_course_id ist eine Variable in der aktuellen MySQL-Verbindung.
- Die Datei ändert Daten, aber keine Spalten oder Tabellenregeln.

> **⚠️ Pitfall: Einrichtung bei jedem Start wiederholen**
> Führe diese INSERT-Datei genau einmal aus.
> Falls Zaubertrankpraxis schon vorhanden ist, prüfe den vorhandenen Eintrag.
> Die späteren SELECT-Dateien kannst du dagegen erneut ausführen.

## 2. Teilnehmerdaten mit INNER JOIN verbinden

### 2.1 Zwei Tabellen verbinden

Die Verwaltung möchte zu jeder Buchung den Schülernamen sehen.
Dafür verbindet die Abfrage bookings mit students.

- INNER JOIN liefert passende Kombinationen aus beiden Tabellen.
- ON beschreibt, welche Werte miteinander übereinstimmen müssen.
- b und s sind kurze Tabellenaliase innerhalb dieser Abfrage.
- b.student_id verweist auf s.id.
- Die Buchungs-ID b.id bezeichnet dagegen die Buchung selbst.

Datei `sql\tag4\02_inner_join.sql`:

<!-- file: sql/tag4/02_inner_join.sql -->

```sql
USE hogwarts;

SELECT b.id AS booking_id, s.first_name, s.last_name, b.course_id
FROM bookings AS b
INNER JOIN students AS s ON s.id = b.student_id
ORDER BY b.id;
```

Laden: `SOURCE /work/sql/tag4/02_inner_join.sql;`

<details>
<summary>Erwartung</summary>

Neun Zeilen, eine je Buchung.
Hermione erscheint zweimal, weil sie zwei verschiedene Kurse gebucht hat.
Ginny und Alex fehlen, weil sie im Live-Bestand keine Buchung haben.
Die Schülernamen werden zusammen mit der passenden Buchung ausgegeben.

</details>

Der Join speichert keine neue Beziehung und verändert keine Tabelle.
Er bildet für diese Abfrage zusammengehörige Ergebniszeilen.

> **💡 Merke: Eine Zeile bedeutet hier eine Buchung**
> Derselbe Schüler kann in einer Teilnehmerauswertung mehrfach erscheinen.
> Prüfe deshalb vor DISTINCT, ob diese Wiederholung fachlich richtig ist.

### 2.2 Einen Kursnamen über die dritte Tabelle ergänzen

Für Arithmantik braucht die Verwaltung Namen und Buchungsdaten.
Der Join-Pfad führt von students über bookings zu courses.

- Die erste ON-Bedingung verbindet die Buchung mit dem Schüler.
- Die zweite ON-Bedingung verbindet dieselbe Buchung mit dem Kurs.
- WHERE wählt anschließend Kurs 1 aus.
- ORDER BY legt die Ausgabereihenfolge ausdrücklich fest.

Datei `sql\tag4\03_three_tables.sql`:

<!-- file: sql/tag4/03_three_tables.sql -->

```sql
USE hogwarts;

SELECT b.id AS booking_id, s.first_name, s.last_name,
       c.title, b.booking_date
FROM bookings AS b
INNER JOIN students AS s ON s.id = b.student_id
INNER JOIN courses AS c ON c.id = b.course_id
WHERE c.id = 1
ORDER BY s.id, b.id;
```

Laden: `SOURCE /work/sql/tag4/03_three_tables.sql;`

<details>
<summary>Erwartung</summary>

| Schüler | Kurs | Buchungsdatum |
|---|---|---|
| Hermione Granger | Arithmantik | 1993-09-01 |
| Nora Winter | Arithmantik | 1993-09-04 |
| Elias Brook | Arithmantik | 1993-09-05 |

Die Ausgabe ist nach Schüler-ID und anschließend Buchungs-ID sortiert.
Die IDs von Nora und Elias wurden bei ihrer Anmeldung erzeugt.

</details>

> **⚠️ Pitfall: Gleich aussehende IDs verwechseln**
> Verknüpfe s.id mit b.student_id und c.id mit b.course_id.
> Gleiche Zahlen in b.id und s.id beweisen keinen Zusammenhang.
> Ohne passende Join-Bedingung können ungewollte Kombinationen entstehen.

### Kleine Übertragung

1. Ändere den Kursfilter vorübergehend auf Kurs 2.
2. Sage vor dem Ausführen voraus, welche Namen erscheinen.
3. Prüfe die Ausgabe und setze den gespeicherten Stand wieder auf Kurs 1.

<details>
<summary>Erwartung</summary>

Harry Potter und Ron Weasley.
Ihre Buchungen gehören zu Wahrsagen.
Die Datumswerte bleiben die Werte ihrer jeweiligen Buchung.

</details>

- [Aufgaben 2–3][a2] übertragen den Join-Pfad auf die Übungsdaten.

## 3. Fehlende Treffer mit LEFT JOIN erhalten

### 3.1 Auch Angebote ohne Buchung zeigen

Die Verwaltung möchte alle Angebote sehen, auch Zaubertrankpraxis.
Ein INNER JOIN würde den neuen Kurs aus dieser Liste entfernen.

- courses steht links und liefert die Angebote, die erhalten bleiben sollen.
- LEFT JOIN ergänzt jede passende Buchungszeile.
- Ohne passenden Treffer stehen auf der rechten Seite NULL-Werte.
- Mehrere Buchungen eines Kurses ergeben weiterhin mehrere Zeilen.
- LEFT JOIN bedeutet also nicht automatisch eine Zeile je Kurs.

Datei `sql\tag4\04_left_join.sql`:

<!-- file: sql/tag4/04_left_join.sql -->

```sql
USE hogwarts;

SELECT c.id AS course_id, c.title, b.id AS booking_id
FROM courses AS c
LEFT JOIN bookings AS b ON b.course_id = c.id
ORDER BY c.id, b.id;
```

Laden: `SOURCE /work/sql/tag4/04_left_join.sql;`

<details>
<summary>Erwartung</summary>

Zehn Ergebniszeilen: neun Buchungen und eine ergänzte Zeile.
Bei Zaubertrankpraxis ist booking_id NULL.
Die anderen Kurse erscheinen entsprechend ihrer Buchungszahl mehrfach.
Im Live-Bestand hat Alte Runen zwei passende Buchungszeilen.

</details>

![Joins und Buchungszahlen](../assets/05-joins-und-gruppen.svg)

Die Grafik zeigt einen kleinen Ausschnitt des Bestands.
Sie ist keine vollständige Liste aller Kurse und Buchungen.

| Fall | Ergebnis nach LEFT JOIN |
|---|---|
| Kurs mit zwei Buchungen | Zwei Zeilen mit vorhandener booking_id |
| Kurs ohne Buchung | Eine ergänzte Zeile mit booking_id NULL |

> **💡 Merke: Ein Join-NULL ist keine neue gespeicherte Buchung**
> Die rechte NULL-Zeile entsteht im Abfrageergebnis.
> In bookings wird dafür nichts eingefügt.
> Genau das ist später beim Zählen wichtig.

### 3.2 Nur Buchungen im Zeitraum ergänzen

Die Verwaltung möchte alle Angebote mit Buchungen ab dem 3. September sehen.
Ein Angebot soll auch erscheinen, wenn es nur frühere Buchungen hat.

- Der Datumsfilter gehört deshalb in die ON-Bedingung.
- Er begrenzt die Buchungen, die als passende Partner gelten.
- Gibt es keinen Partner im Zeitraum, bleibt der Kurs mit NULL rechts.

Datei `sql\tag4\05_left_filter.sql`:

<!-- file: sql/tag4/05_left_filter.sql -->

```sql
USE hogwarts;

SELECT c.id AS course_id, c.title, b.id AS booking_id
FROM courses AS c
LEFT JOIN bookings AS b
    ON b.course_id = c.id AND b.booking_date >= '1993-09-03'
ORDER BY c.id, b.id;
```

Laden: `SOURCE /work/sql/tag4/05_left_filter.sql;`

<details>
<summary>Erwartung</summary>

Sechs Ergebniszeilen mit allen fünf Angeboten.
Arithmantik erscheint mit den Buchungen von Nora und Elias.
Pflege magischer Geschöpfe erscheint mit Cedrics Buchung vom 3. September.
Wahrsagen, Alte Runen und Zaubertrankpraxis erscheinen mit booking_id NULL.

</details>

> **⚠️ Pitfall: Den Datumsfilter in WHERE verschieben**
> WHERE b.booking_date >= Datum verwirft auch die ergänzten NULL-Zeilen.
> Kurse ohne passenden Treffer verschwinden dann aus dieser Auswertung.
> Lege zuerst fest, ob die linke Seite vollständig erhalten bleiben soll.

- LEFT OUTER JOIN und LEFT JOIN bezeichnen hier dieselbe Join-Art.
- WHERE b.id IS NULL wäre eine gezielte Suche nach fehlenden Treffern.
- Ein Vergleich wie NULL >= Datum ist dagegen nicht wahr.
- [Aufgabe 4][a4] übt den Zeitraum mit dem unabhängigen Übungsbestand.

### Einen Zwischenstand sichern

```powershell
git status --short
git add -- sql/tag4/00_start_check.sql
git add -- sql/tag4/01_empty_course.sql
git add -- sql/tag4/02_inner_join.sql
git add -- sql/tag4/03_three_tables.sql
git add -- sql/tag4/04_left_join.sql
git add -- sql/tag4/05_left_filter.sql
git commit -m "Teilnehmerlisten und leere Kurse mit SQL auswerten"
```

## 4. Gesamtwerte mit Aggregaten berechnen

Die Verwaltung fragt nach Buchungszahlen und dem Buchungszeitraum.
Ein Aggregat fasst Werte mehrerer Zeilen zusammen.
Ohne GROUP BY betrachten die folgenden Abfragen jeweils den Gesamtbestand.

| Ausdruck | Bedeutung |
|---|---|
| COUNT(*) | Alle Ergebniszeilen zählen |
| COUNT(house) | Nur vorhandene Hausangaben zählen |
| COUNT(DISTINCT student_id) | Verschiedene gebuchte Schüler zählen |
| MIN(booking_date) | Frühestes vorhandenes Datum |
| MAX(booking_date) | Spätestes vorhandenes Datum |
| AVG(school_year) | Mittelwert der vorhandenen Zahlenwerte |
| SUM(Zahlenspalte) | Vorhandene Zahlenwerte summieren |

- MIN, MAX, AVG und SUM überspringen NULL-Werte.
- Für Gebühren fehlt im Projekt ein Feld. Dafür ergänzt du keines.
- Ein Durchschnitt über eine leere Auswahl ist NULL, nicht 0.
- COUNT liefert dagegen 0, wenn nichts zu zählen ist.

Datei `sql\tag4\06_totals.sql`:

<!-- file: sql/tag4/06_totals.sql -->

```sql
USE hogwarts;

SELECT COUNT(*) AS booking_count,
       COUNT(DISTINCT student_id) AS student_count,
       MIN(booking_date) AS first_booking,
       MAX(booking_date) AS last_booking
FROM bookings;

SELECT COUNT(*) AS student_count, COUNT(house) AS known_house_count,
       MIN(school_year) AS first_year, MAX(school_year) AS last_year,
       AVG(school_year) AS average_year
FROM students;
```

Laden: `SOURCE /work/sql/tag4/06_totals.sql;`

<details>
<summary>Erwartung</summary>

| Kennzahl | Wert |
|---|---|
| Buchungen | 9 |
| Verschiedene gebuchte Schüler | 8 |
| Erstes Buchungsdatum | 1993-09-01 |
| Letztes Buchungsdatum | 1993-09-05 |
| Schüler insgesamt | 10 |
| Schüler mit bekanntem Haus | 7 |
| Kleinster und größter Jahrgang | 1 und 5 |
| Mittlerer Jahrgang | 2,4 |

MySQL zeigt den Mittelwert mit Dezimalpunkt und Nachkommastellen.
Hermione hat zwei Buchungen, ist aber nur eine Person.
Die NULL-Hausangaben gehören zu Alex, Nora und Elias.

</details>

> **⚠️ Pitfall: COUNT(*) und COUNT(Spalte) gleichsetzen**
> COUNT(house) ist nicht die Gesamtzahl der Schüler.
> Es lässt Schüler ohne bekannte Hausangabe aus der Zählung weg.
> COUNT(DISTINCT house) würde wiederum verschiedene Hauswerte zählen.

### Kleine Übertragung

1. Formuliere eine Abfrage für die Anzahl aller Buchungen.
2. Ergänze die Anzahl verschiedener gebuchter Kurse.
3. Erkläre, warum die Anzahl angebotener Kurse davon abweicht.

<details>
<summary>Erwartung</summary>

Neun Buchungen verteilen sich auf vier gebuchte Kurse.
Das fünfte Angebot hat keinen Eintrag in bookings.
Die Zahl der Angebote erhältst du aus courses, nicht aus bookings.

</details>

- [Aufgabe 5][a5] unterscheidet Buchungszahl und Personenzahl.

## 5. Gruppen bilden und filtern

### 5.1 Eine Zeile pro Kurs bilden

Die Verwaltung braucht die Buchungszahl für jedes einzelne Angebot.
Auch für Zaubertrankpraxis soll eine Zahl erscheinen.

- LEFT JOIN bildet zuerst die bekannten Einzelzeilen.
- GROUP BY fasst sie nach Kurs-ID und Titel zusammen.
- COUNT(b.id) zählt die nicht-NULL Buchungs-IDs innerhalb jeder Gruppe.
- ORDER BY sortiert die fertigen Kursgruppen.

Datei `sql\tag4\07_course_counts.sql`:

<!-- file: sql/tag4/07_course_counts.sql -->

```sql
USE hogwarts;

SELECT c.id AS course_id, c.title, COUNT(b.id) AS booking_count
FROM courses AS c
LEFT JOIN bookings AS b ON b.course_id = c.id
GROUP BY c.id, c.title
ORDER BY c.id;
```

Laden: `SOURCE /work/sql/tag4/07_course_counts.sql;`

<details>
<summary>Erwartung</summary>

| Kurs | Buchungen |
|---|---:|
| Arithmantik | 3 |
| Wahrsagen | 2 |
| Alte Runen | 2 |
| Pflege magischer Geschöpfe | 2 |
| Zaubertrankpraxis | 0 |

Fünf Zeilen, eine je Angebot.
Die Buchungszahlen ergeben zusammen neun.

</details>

> **💡 Merke: Was zählt die leere Kursgruppe?**
> COUNT(*) zählt bei Zaubertrankpraxis die ergänzte Ergebniszeile: 1.
> COUNT(b.id) ignoriert deren NULL-Wert und zählt Buchungen: 0.
> Wähle den Ausdruck danach, was deine Zahl fachlich bedeuten soll.

- Gruppiere nach ID und Titel, nicht nur nach dem Titel.
- Zwei unterschiedliche Kurse können denselben Titel haben.
- Nichtaggregierte Ausgabespalten stehen hier ausdrücklich in GROUP BY.
- ONLY_FULL_GROUP_BY bleibt eingeschaltet.
- Korrigiere eine unklare Gruppierung, statt den SQL-Modus abzuschalten.

### 5.2 Gruppen mit HAVING auswählen

Die Verwaltung möchte Angebote mit mindestens drei Buchungen sehen.
Die Grenze bezieht sich auf die berechnete Zahl pro Gruppe.

Datei `sql\tag4\08_having.sql`:

<!-- file: sql/tag4/08_having.sql -->

```sql
USE hogwarts;

SELECT c.id AS course_id, c.title, COUNT(b.id) AS booking_count
FROM courses AS c
LEFT JOIN bookings AS b ON b.course_id = c.id
GROUP BY c.id, c.title
HAVING COUNT(b.id) >= 3
ORDER BY c.id;
```

Laden: `SOURCE /work/sql/tag4/08_having.sql;`

<details>
<summary>Erwartung</summary>

Eine Zeile: Arithmantik mit drei Buchungen.
Die übrigen Angebote erfüllen die Grenze drei nicht.

</details>

- HAVING prüft hier das Ergebnis von COUNT je Kursgruppe.
- WHERE COUNT(...) ist kein gültiger Ersatz.
- ORDER BY legt erst die Reihenfolge des verbleibenden Ergebnisses fest.

### 5.3 Erst Einzelzeilen, dann Gruppen filtern

Jetzt interessieren Kurse mit mindestens zwei frühen Buchungen.
Als früh gelten hier Buchungen vor dem 3. September 1993.

Datei `sql\tag4\09_where_having.sql`:

<!-- file: sql/tag4/09_where_having.sql -->

```sql
USE hogwarts;

SELECT course_id, COUNT(*) AS booking_count
FROM bookings
WHERE booking_date < '1993-09-03'
GROUP BY course_id
HAVING COUNT(*) >= 2
ORDER BY course_id;
```

Laden: `SOURCE /work/sql/tag4/09_where_having.sql;`

<details>
<summary>Erwartung</summary>

Kurs 2 und Kurs 3 haben im ausgewählten Zeitraum je zwei Buchungen.
Kurs 1 hat davor nur eine Buchung und erfüllt die Gruppengrenze nicht.
Die Buchung vom 3. September selbst ist nicht mehr im Zeitraum.

</details>

| Schritt | Aufgabe in dieser Abfrage |
|---|---|
| FROM bookings | Buchungszeilen als Grundlage nehmen |
| WHERE | Buchungen vor dem 3. September auswählen |
| GROUP BY | Die ausgewählten Buchungen je Kurs zusammenfassen |
| HAVING | Kursgruppen mit mindestens zwei Buchungen behalten |
| ORDER BY | Das Ergebnis nach Kurs-ID sortieren |

Das beschreibt die logische Bedeutung der Abfrage.
Es legt keinen konkreten internen Ausführungsplan von MySQL fest.
Hier genügt bookings, weil die Verwaltung nur gebuchte Kurse sehen möchte.

> **⚠️ Pitfall: WHERE und HAVING vertauschen**
> WHERE begrenzt die Einzelzeilen vor der Gruppenberechnung.
> HAVING prüft anschließend Bedingungen für die Gruppen.
> Ein später Datumsfilter ist nicht dasselbe wie ein Filter der Gruppenanzahl.

### Kleine Übertragung

1. Ändere in 08_having.sql die Grenze vorübergehend auf mindestens zwei.
2. Begründe, welche Angebote danach erscheinen.
3. Setze den gespeicherten Stand anschließend wieder auf drei.

<details>
<summary>Erwartung</summary>

Alle vier ursprünglichen Angebote erscheinen.
Zaubertrankpraxis fehlt mit null Buchungen weiterhin.
Ein Kurs wird einmal gezeigt, unabhängig von seiner Buchungszahl.

</details>

- [Aufgaben 5–7][a5] übertragen die Zählfragen auf andere Aufträge.
- Aufgabe 6 verlangt Schülerzahlen und Buchungszahlen pro Haus.
- Aufgabe 7 zählt verschiedene Kurse je Schüler.

### Die Gruppierungen sichern

```powershell
git status --short
git add -- sql/tag4/06_totals.sql
git add -- sql/tag4/07_course_counts.sql
git add -- sql/tag4/08_having.sql
git add -- sql/tag4/09_where_having.sql
git commit -m "Gesamtwerte und Kursgruppen mit SQL berechnen"
```

## 6. Einfache Unterabfragen verwenden

### 6.1 Eine Auswahl mit IN beschreiben

Die Verwaltung sucht Schüler, die Alte Runen gebucht haben.
Die innere Abfrage liefert dafür Schüler-IDs aus bookings.
Die äußere Abfrage liefert die Namen aus students.

Datei `sql\tag4\10_in_subquery.sql`:

<!-- file: sql/tag4/10_in_subquery.sql -->

```sql
USE hogwarts;

SELECT student_id FROM bookings WHERE course_id = 3 ORDER BY student_id;

SELECT id, first_name, last_name
FROM students
WHERE id IN (
    SELECT student_id
    FROM bookings
    WHERE course_id = 3
)
ORDER BY id;
```

Laden: `SOURCE /work/sql/tag4/10_in_subquery.sql;`

<details>
<summary>Erwartung</summary>

Die erste Ausgabe zeigt die Schüler-IDs 2 und 5.
Die zweite zeigt Hermione Granger und Luna Lovegood.
Jede Person erscheint im äußeren Ergebnis einmal.

</details>

- Eine Unterabfrage ist eine SELECT-Abfrage innerhalb einer anderen Abfrage.
- IN prüft, ob die äußere Schüler-ID in der inneren Auswahl vorkommt.
- Die innere Abfrage liefert eine Spalte, kann aber mehrere Zeilen liefern.
- Sie ist unabhängig von der jeweils betrachteten äußeren Schülerzeile.
- Wiederholte IDs im inneren Ergebnis vervielfachen äußere Zeilen nicht.
- Zum Verstehen kannst du die innere Abfrage zuerst einzeln betrachten.
- Das schreibt MySQL keine feste Reihenfolge der internen Ausführung vor.

> **⚠️ Pitfall: Eine mehrzeilige Auswahl mit = vergleichen**
> Ein skalarer Gleichheitsvergleich erwartet höchstens einen inneren Wert.
> Liefert die Unterabfrage mehrere Zeilen, ist IN die passende Form
> für unsere Zugehörigkeitsfrage.

- [Aufgabe 8][a8] wählt den Kurs über seinen Titel statt eine feste ID.

### 6.2 Freiwillige Vertiefung: fehlende Buchungen mit NOT EXISTS

Die Verwaltung sucht Schüler, die überhaupt keinen Kurs gebucht haben.
Du prüfst das Fehlen passender Buchungszeilen.
Dieser Abschnitt ergänzt den Pflichtteil bei verfügbarer Zeit.

Datei `sql\tag4\11_not_exists.sql`:

<!-- file: sql/tag4/11_not_exists.sql -->

```sql
USE hogwarts;

SELECT s.id, s.first_name, s.last_name
FROM students AS s
WHERE NOT EXISTS (
    SELECT 1
    FROM bookings AS b
    WHERE b.student_id = s.id
)
ORDER BY s.id;
```

Laden: `SOURCE /work/sql/tag4/11_not_exists.sql;`

<details>
<summary>Erwartung</summary>

Ginny Weasley mit ID 7 und Alex Morgan mit ID 8.
Nora und Elias erscheinen nicht, weil sie eine Buchung haben.
Mehrere Buchungen eines anderen Schülers verändern diese Ja/Nein-Frage nicht.

</details>

- EXISTS fragt, ob die innere Auswahl mindestens eine passende Zeile findet.
- NOT EXISTS fragt, ob keine passende Zeile gefunden wird.
- b.student_id = s.id verbindet die innere mit der äußeren Auswahl.
- Diese Unterabfrage heißt deshalb korreliert.
- SELECT 1 steht für einen beliebigen Ausgabewert, nicht für eine Anzahl.
- Für EXISTS ist entscheidend, ob eine Zeile existiert.

> **⚠️ Pitfall: Den Bezug zur äußeren ID weglassen**
> Ohne b.student_id = s.id prüfst du nur, ob irgendwo Buchungen existieren.
> Diese allgemeine Antwort wäre dann für alle Schüler dieselbe.

- NOT IN und NOT EXISTS sind bei möglichen NULL-Werten zu unterscheiden.
- NOT IN mit einem NULL in der inneren Auswahl kann UNKNOWN ergeben.
- Unsere Buchungs-Fremdschlüssel sind NOT NULL. Die Begriffe bleiben getrennt.
- [Aufgabe 9][a9] fragt nach fehlenden Buchungen in einem Zeitraum.
- Frühere Buchungen dürfen dort durchaus vorhanden sein.

## 7. Eine eigene SQL-Auswertung entwickeln

Die Verwaltung möchte Kurse mit mindestens zwei verschiedenen Schülern sehen.
Du kombinierst dafür bekannte Bausteine zu einer neuen Datenfrage.

### Dein Auftrag

1. Erstelle sql/tag4/07b_distinct_students.sql.
2. Gib Kurs-ID, Titel und die Zahl verschiedener Schüler aus.
3. Behalte nur Kurse mit mindestens zwei verschiedenen Schülern.
4. Sortiere nach Kurs-ID.
5. Erkläre vor dem Ausführen, wofür eine Ergebniszeile stehen soll.

Probiere die Aufgabe zuerst selbst aus.
Die Referenz steht zum anschließenden Vergleichen im aufklappbaren Bereich.

<details>
<summary>Referenzabfrage und erwartetes Ergebnis</summary>

Datei `sql\tag4\07b_distinct_students.sql`:

<!-- file: sql/tag4/07b_distinct_students.sql -->

```sql
USE hogwarts;

SELECT c.id AS course_id, c.title,
       COUNT(DISTINCT b.student_id) AS student_count
FROM courses AS c
INNER JOIN bookings AS b ON b.course_id = c.id
GROUP BY c.id, c.title
HAVING COUNT(DISTINCT b.student_id) >= 2
ORDER BY c.id;
```

Laden: `SOURCE /work/sql/tag4/07b_distinct_students.sql;`

Arithmantik hat drei verschiedene Schüler.
Wahrsagen, Alte Runen und Pflege magischer Geschöpfe haben je zwei.
Zaubertrankpraxis erfüllt die Grenze nicht.
Jede Ergebniszeile beschreibt einen Kurs, keine einzelne Buchung.
HAVING prüft die Zahl verschiedener Schüler pro Kursgruppe.

</details>

> **💡 Merke: Eine Person ist keine Buchungszeile**
> COUNT(DISTINCT b.student_id) zählt eine Person innerhalb der Gruppe einmal.
> Mehrere Buchungen derselben Person erhöhen ihre Personenzahl nicht.
> Im heutigen Live-Bestand sind beide Zahlen je Kurs noch gleich.
> Im Übungsbestand unterscheiden sie sich absichtlich.

### Die SQL-Auswahl sichern

```powershell
git status --short
git add -- sql/tag4/07b_distinct_students.sql
git add -- sql/tag4/10_in_subquery.sql
git commit -m "Eigene Kursauswertung und IN-Unterabfrage entwickeln"
```

- Die Datei 11_not_exists.sql gehört zur freiwilligen Vertiefung.
- Füge sie nur hinzu, wenn du diesen Abschnitt bearbeitet hast.

## 8. Ausgewählte Berichte in Python verwenden

Die Verwaltung möchte Teilnehmerliste und Kursübersicht in Python weitergeben.
Du verwendest die bekannten Modelle und die Session-Fabrik aus Tag 3.
Nicht jede heutige SQL-Abfrage wird ein zweites Mal als ORM-Abfrage umgesetzt.

### 8.1 Den vorhandenen Modellstand prüfen

- tag3/db.py enthält weiterhin Engine und SessionLocal.
- tag3/models.py enthält Student, Course und Booking samt Beziehungen.
- Neue Berichte liegen in tag4. tag3 und tag4 liegen nebeneinander.
- Du erzeugst keine neuen Hauptmodelle und keine zweite Engine.
- Die Ordner funktionieren hier als Namespace-Packages ohne __init__.py.

In PowerShell im Projektordner hogwarts-sql:

```powershell
python -m pip check
python -c "from tag3.models import Student; print(Student.bookings)"
python -c "import sqlalchemy; print(sqlalchemy.__version__)"
```

<details>
<summary>Erwartung</summary>

Keine Paketkonflikte.
Das Attribut Student.bookings ist verfügbar.
Der vorhandene Unterrichtsstand verwendet SQLAlchemy 2.0.54.

</details>

> **⚠️ Pitfall: Tag 3 ohne den Beziehungsstand weiterverwenden**
> Fehlt Student.bookings, ergänze den Beziehungsstand aus [Tag 3][tag3].
> Die bisherigen Tabellen werden deshalb nicht neu angelegt.
> Es ist eine Ergänzung der ORM-Abbildung, keine neue Datenbank.

### 8.2 Die Teilnehmerliste als explizite Abfrage

Für course_register wählen wir nur die benötigten Spalten aus.
Eine Funktion bekommt die Kurs-ID und liefert eine Liste von Dictionaries.

- select_from(Booking) legt den Startpunkt ausdrücklich fest.
- join(Booking.student) nutzt die Beziehung als Join-Pfad.
- where grenzt den gewünschten Kurs über einen gebundenen Wert ein.
- label benennt die Schüler-ID im Ergebnis als student_id.
- mappings macht die ausgewählten Spalten über ihre Namen zugänglich.
- dict(row) erzeugt daraus ein normales Python-Dictionary.

### 8.3 Die Kursübersicht als gruppierte Abfrage

course_summary überträgt die bekannte Kurszählung auf SQLAlchemy.

- func.count beschreibt das SQL-Aggregat COUNT.
- outerjoin(Course.bookings) erhält leere Angebote.
- group_by bildet die Kursgruppen.
- order_by sortiert nach Kurs-ID.
- MySQL berechnet die Zahlen. Python verwendet nur die Ergebniswerte.

### 8.4 Beide Funktionen vollständig zusammenführen

Die folgende Datei enthält den vollständigen Pflichtstand.
Entwickle zuerst course_register und ergänze danach course_summary.
Die Imports stehen nur einmal am Dateianfang.

Datei `tag4\reports.py`:

<!-- file: tag4/reports.py -->

```python
from sqlalchemy import func, select

from tag3.db import SessionLocal
from tag3.models import Booking, Course, Student


def course_register(course_id: int) -> list[dict]:
    statement = (
        select(
            Student.id.label("student_id"),
            Student.first_name,
            Student.last_name,
            Booking.booking_date,
        )
        .select_from(Booking)
        .join(Booking.student)
        .where(Booking.course_id == course_id)
        .order_by(Student.id, Booking.id)
    )
    with SessionLocal() as session:
        return [dict(row) for row in session.execute(statement).mappings()]


def course_summary() -> list[dict]:
    statement = (
        select(
            Course.id.label("course_id"),
            Course.title,
            func.count(Booking.id).label("booking_count"),
        )
        .outerjoin(Course.bookings)
        .group_by(Course.id, Course.title)
        .order_by(Course.id)
    )
    with SessionLocal() as session:
        return [dict(row) for row in session.execute(statement).mappings()]
```

In der Projekt-PowerShell kannst du jede Funktion einzeln prüfen:

```powershell
python -c "from tag4.reports import course_register; print(course_register(1))"
python -c "from tag4.reports import course_summary; print(course_summary())"
```

<details>
<summary>Erwartung</summary>

course_register(1) liefert drei Dictionaries für Hermione, Nora und Elias.
Die Schlüssel sind student_id, first_name, last_name und booking_date.
booking_date enthält in Python ein date-Objekt.

course_summary liefert fünf Dictionaries mit course_id und title.
Dazu kommt booking_count mit den Werten 3, 2, 2, 2 und 0.
Zaubertrankpraxis bleibt als leeres Angebot sichtbar.
Ein course_register-Aufruf für einen fehlenden Kurs liefert eine leere Liste.

</details>

- Beide Funktionen lesen die benötigten Daten innerhalb ihrer Session.
- Danach geben sie normale Daten zurück, keine nachzuladenden Beziehungen.
- Für diese Leseberichte ist kein COMMIT nötig.
- scalars wäre für die Auswahl mehrerer Spalten hier nicht passend.
- scalars würde pro Zeile nur den ersten ausgewählten Wert liefern.

### 8.5 Die Berichte gemeinsam ausgeben

Datei `tag4\report_demo.py`:

<!-- file: tag4/report_demo.py -->

```python
from tag4.reports import course_register, course_summary


print("Arithmantik:")
for row in course_register(1):
    print(row["first_name"], row["last_name"], row["booking_date"])

print("Kursuebersicht:")
for row in course_summary():
    print(row["course_id"], row["title"], row["booking_count"])
```

```powershell
python -m tag4.report_demo
```

<details>
<summary>Erwartung</summary>

Zuerst erscheinen die drei Arithmantik-Buchungen mit Namen und Datum.
Danach folgen alle fünf Kurse mit ihren Buchungszahlen.
Die Berichte entsprechen den vorherigen SQL-Auswertungen.
Die tatsächlich erzeugte ID von Zaubertrankpraxis kann von 5 abweichen.

</details>

> **⚠️ Pitfall: Aus dem falschen Verzeichnis starten**
> Starte python -m tag4.report_demo im Projektordner hogwarts-sql.
> Wechsle dafür nicht nach tag4 und starte nicht python reports.py.
> Die qualifizierten Imports brauchen den gemeinsamen Projektordner.

### 8.6 Objektzugriff und Abfrageaufbau unterscheiden

| Ausdruck | Bedeutung |
|---|---|
| booking.student | Schülerobjekt einer konkreten Buchung lesen |
| student.bookings | Buchungsobjekte eines konkreten Schülers lesen |
| join(Booking.student) | Beziehung als Join-Pfad einer Abfrage verwenden |
| Student.bookings.any() | Eine Existenzbedingung für eine Abfrage aufbauen |

- Die ersten beiden Ausdrücke arbeiten an konkreten Modellobjekten.
- Ein solcher Zugriff kann benötigte Daten aus der Datenbank nachladen.
- Die letzten beiden Ausdrücke arbeiten an Attributen der Modellklassen.
- Sie beschreiben Bestandteile einer expliziten SQL-Abfrage.
- Die Beziehung allein ist noch kein fertiger Verwaltungsbericht.

> **⚠️ Pitfall: Alle Buchungen zum Zählen nachladen**
> len(course.bookings) zählt eine geladene Python-Sammlung.
> Unser Bericht lässt MySQL die Gruppen und deren Zahlen berechnen.
> Ladeverfahren und Performance vertiefen wir an einem späteren Tag.

- [Aufgaben 10–11][a10] übertragen die Berichte auf die Übungsmodelle.
- Die Übersicht in Aufgabe 11 enthält zusätzlich verschiedene Schüler.

### 8.7 Freiwillige Vertiefung: fehlende Buchungen im ORM

Bearbeite zuerst die SQL-Erklärung zu NOT EXISTS aus Abschnitt 6.2.
Ergänze die folgende Funktion unter course_summary in tag4/reports.py.
Die Imports aus dem Pflichtstand bleiben bestehen.

Datei `tag4\reports.py`:

<!-- file: tag4/reports.py -->

```python
def students_without_bookings() -> list[dict]:
    statement = (
        select(Student.id, Student.first_name, Student.last_name)
        .where(~Student.bookings.any())
        .order_by(Student.id)
    )
    with SessionLocal() as session:
        return [dict(row) for row in session.execute(statement).mappings()]
```

```powershell
python -c "from tag4.reports import students_without_bookings as f; print(f())"
```

<details>
<summary>Erwartung</summary>

Ginny und Alex mit ID, Vorname und Nachname.
Die Auswahl entspricht der SQL-Abfrage mit NOT EXISTS.
Die Berechnung findet in MySQL statt, nicht in einer Python-Schleife.

</details>

- Student.bookings.any() baut eine EXISTS-Bedingung auf.
- ~ negiert diese Bedingung und fragt nach fehlenden Buchungen.
- Das ist nicht Pythons any über eine bereits geladene Liste.
- [Aufgabe 12][a12] ergänzt als Transfer ein Datum in der Existenzprüfung.

## 9. Stand am Ende des Vormittags

### Den vollständigen Live-Bestand prüfen

Datei `sql\tag4\12_end_check.sql`:

<!-- file: sql/tag4/12_end_check.sql -->

```sql
USE hogwarts;

SELECT 'students' AS table_name, COUNT(*) AS row_count FROM students
UNION ALL
SELECT 'courses', COUNT(*) FROM courses
UNION ALL
SELECT 'bookings', COUNT(*) FROM bookings;

SELECT c.id, c.title, COUNT(b.id) AS booking_count
FROM courses AS c
LEFT JOIN bookings AS b ON b.course_id = c.id
GROUP BY c.id, c.title
ORDER BY c.id;
```

Laden: `SOURCE /work/sql/tag4/12_end_check.sql;`

<details>
<summary>Erwartung</summary>

Zehn Schüler, fünf Kurse und neun Buchungen.
Arithmantik hat drei Buchungen, die drei anderen alten Angebote je zwei.
Zaubertrankpraxis hat null Buchungen.
Nora und Elias behalten ihre bisherigen Buchungen.

</details>

- [ ] Die Join-Teilnehmerliste hat eine Zeile pro passender Buchung.
- [ ] LEFT JOIN zeigt Zaubertrankpraxis mit NULL auf der rechten Seite.
- [ ] COUNT(b.id) liefert für diesen Kurs 0.
- [ ] Der Datumsfilter im ON erhält Angebote ohne passenden Zeitraumtreffer.
- [ ] WHERE und HAVING erfüllen die verschiedenen Aufträge.
- [ ] Die IN-Auswahl liefert Hermione und Luna.
- [ ] Die eigene Auswertung zählt verschiedene Schüler.
- [ ] SQL und die beiden Python-Berichte liefern dieselben Inhalte.
- [ ] Der Endstand lautet 10 / 5 / 9.
- [ ] Bei Vertiefung stimmen NOT EXISTS und die dritte ORM-Auswahl überein.

Der Live-Bestand bleibt für die nächsten Unterrichtstage erhalten.
Der Nachmittag verwendet davon getrennte Tabellen in derselben Datenbank.

### Die Python-Berichte sichern

```powershell
git status --short
git add -- tag4/reports.py
git add -- tag4/report_demo.py
git add -- sql/tag4/12_end_check.sql
git commit -m "Hogwarts-Auswertungen in Python mit ORM verwenden"
```

### Fragen zum Selbstprüfen

1. Was bedeutet eine Zeile der Teilnehmerliste?
2. Wie verändert LEFT JOIN die Ausgabe eines ungebuchten Kurses?
3. Was unterscheidet COUNT(*) von COUNT(b.id) in dessen Kursgruppe?
4. Warum können Buchungszahl und Personenzahl verschieden sein?
5. Was unterscheidet WHERE von HAVING?
6. Wann eignet sich IN für eine Unterabfrage?
7. Was unterscheidet booking.student von join(Booking.student)?
8. Warum liefern die Python-Berichte Dictionaries statt ORM-Objekte?
9. Vertiefung: Warum braucht NOT EXISTS den Bezug zur äußeren Schüler-ID?

<details>
<summary>Antworten zum Vergleichen</summary>

1. Eine passende Buchung, nicht zwingend eine einmalige Person.
2. Der Kurs bleibt mit NULL-Werten für fehlende rechte Spalten erhalten.
3. COUNT(*) zählt die ergänzte Zeile als 1. COUNT(b.id) zählt 0 Buchungen.
4. Eine Person kann mehrere Buchungen haben, auch innerhalb einer Gruppe.
5. WHERE filtert Einzelzeilen. HAVING filtert die berechneten Gruppen.
6. IN prüft die Zugehörigkeit zu einem einspaltigen inneren Ergebnis.
7. Der Objektzugriff liest einen Schüler. join baut einen SQL-Abfragepfad.
8. Der Aufrufer benötigt dann keine offene Session zum Nachladen.
9. Sonst würde die Unterabfrage nur prüfen, ob irgendwo Buchungen existieren.

</details>
