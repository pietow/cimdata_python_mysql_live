# MySQL-Grundlagen – Übungen am Nachmittag

## Orientierung

- Du arbeitest an einer Hogwarts-Kursverwaltung.
- MySQL muss laufen und die Datenbank `hogwarts` muss erreichbar sein.
- Verwende ausschließlich die Tabellen mit dem Präfix `practice_`.
- Die Projekttabellen `students`, `courses`, `bookings` bleiben unberührt.

### Arbeitsweise

- Formuliere vor einer Abfrage die Datenfrage und erwartete Treffer.
- Vergleiche anschließend das Ergebnis mit deiner Vorhersage.
- Schreibe Lösungen in eigene SQL-Dateien.
- Änderungen nur an `practice_...`, nicht an den Vormittagstabellen.


<a id="aufgabe-1"></a>
## 1. Den unabhängigen Übungsbestand einrichten

- Öffne den MySQL-Client in der Datenbank `hogwarts`.
- Einmalig ausführen, wenn die drei Übungstabellen noch nicht existieren.
- Diese Definitionen benötigen keine Tabellen des Vormittags.
- Speichere in `sql/90_exercise_setup.sql`
````sql
USE hogwarts;

CREATE TABLE practice_students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    house VARCHAR(20) NULL,
    school_year TINYINT NOT NULL,
    CONSTRAINT ck_practice_students_school_year
        CHECK (school_year BETWEEN 1 AND 7)
) ENGINE=InnoDB;

CREATE TABLE practice_courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE practice_bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    booking_date DATE NOT NULL,
    CONSTRAINT fk_practice_bookings_student
        FOREIGN KEY (student_id) REFERENCES practice_students(id),
    CONSTRAINT fk_practice_bookings_course
        FOREIGN KEY (course_id) REFERENCES practice_courses(id)
) ENGINE=InnoDB;

INSERT INTO practice_students
    (id, first_name, last_name, house, school_year)
VALUES
    (1, 'Harry', 'Potter', 'Gryffindor', 3),
    (2, 'Hermione', 'Granger', 'Gryffindor', 3),
    (3, 'Ron', 'Weasley', 'Gryffindor', 3),
    (4, 'Draco', 'Malfoy', 'Slytherin', 3),
    (5, 'Luna', 'Lovegood', 'Ravenclaw', 2),
    (6, 'Cedric', 'Diggory', 'Hufflepuff', 5),
    (7, 'Ginny', 'Weasley', 'Gryffindor', 2),
    (8, 'Alex', 'Morgan', NULL, 1);

INSERT INTO practice_courses (id, title)
VALUES
    (1, 'Arithmantik'),
    (2, 'Wahrsagen'),
    (3, 'Alte Runen'),
    (4, 'Pflege magischer Geschöpfe');

INSERT INTO practice_bookings (id, student_id, course_id, booking_date)
VALUES
    (1, 1, 2, '1993-09-01'),
    (2, 2, 1, '1993-09-01'),
    (3, 2, 3, '1993-09-01'),
    (4, 3, 2, '1993-09-02'),
    (5, 4, 4, '1993-09-02'),
    (6, 5, 3, '1993-09-01'),
    (7, 6, 4, '1993-09-03');

SELECT * FROM practice_students ORDER BY id;
SELECT * FROM practice_courses ORDER BY id;
SELECT * FROM practice_bookings ORDER BY id;

````
Dann führe folgenden Befehl aus:

```sql
SOURCE /work/sql/90_exercise_setup.sql;
```


### Prüfen

```sql
SELECT * FROM practice_students ORDER BY id;
SELECT * FROM practice_courses ORDER BY id;
SELECT * FROM practice_bookings ORDER BY id;
```

- Erfolg: acht Schüler, vier Kurse, sieben Buchungen.
- Diesen Ausgangsstand nennen wir den Basisbestand.

<a id="aufgabe-2"></a>
## 2. Eine Tabellenstruktur erklären

- Zeige die Struktur von `practice_students` mit DESCRIBE.
- Erkläre Datentyp und Aufgabe der Spalten `id` und `school_year`.
- Welche Angaben dürfen NULL sein?
- Welche Spalte identifiziert die Person eindeutig?
- Erkläre, weshalb TINYINT allein Schuljahr 0 nicht ausschließt.
- Zeige die vollständige Definition mit SHOW CREATE TABLE.

**Erfolg:** Du unterscheidest Datentyp, Primärschlüssel und CHECK-Regel.

<a id="aufgabe-3"></a>
## 3. Eine Namensliste sortieren

- Verwende `practice_students`.
- Zeige ID, Vorname und Nachname.
- Sortiere Nachnamen aufsteigend, danach Vornamen aufsteigend.
- Schreibe eine zweite Abfrage mit Nachnamen absteigend.
- Die Vornamen bleiben in der zweiten Abfrage aufsteigend.

**Erfolg:** Acht Zeilen; bei gleichem Nachnamen entscheidet der Vorname.

<a id="aufgabe-4"></a>
## 4. Eine einzelne Person und ein Haus auswählen

- Suche zunächst nur die Person mit ID 5.
- Zeige ID, Vorname und Nachname.
- Suche danach alle Schüler aus Gryffindor.
- Zeige ID, Vorname und Haus; sortiere nach ID.
- Verwende `practice_students`.

**Erfolg:** Die erste Abfrage zeigt genau eine Person.
Die zweite zeigt nur Zeilen, deren Haus zum Filter passt.

<a id="aufgabe-5"></a>
## 5. Mehrere Datenfragen beantworten

- Schreibe jeweils eine eigene Abfrage auf `practice_students`.
- Zeige ID, Vorname und die für die Suche nötigen Angaben.
- Sortiere Ergebnisse jeweils nach ID.

1. Nachname Granger oder Weasley; nutze OR.
2. Schuljahr 1 bis 2; nutze BETWEEN.
3. Nachname enthält irgendwo `Love`; nutze LIKE.
4. Schuljahr 2 und Haus Gryffindor oder Ravenclaw; nutze Klammern.

**Erfolg:** Du kannst für jede Ergebniszeile die Bedingung begründen.

<a id="aufgabe-6"></a>
## 6. Unbekannte Häuser berücksichtigen

- Verwende `practice_students`; zeige ID, Vorname und Haus.
- Sortiere nach ID und schreibe drei unabhängige Abfragen:

1. Schüler mit bekanntem Haus.
2. Schüler mit bekanntem anderem Haus als Gryffindor.
3. Wie 2, aber zusätzlich Schüler mit unbekanntem Haus.

- Erkläre den Unterschied zwischen `= NULL` und `IS NULL`.

**Erfolg:** Alex erscheint nur in der dritten dieser Auswahlen.

<a id="aufgabe-7"></a>
## 7. Eine Kontaktliste für einen Buchungstag erstellen

- Verwende `practice_bookings`.
- Suche Buchungen vom 1. September 1993.
- Zeige nur Schüler-IDs, jede einmal.
- Verwende DISTINCT und sortiere aufsteigend.
- Vergleiche mit einer Abfrage ohne DISTINCT.

**Erfolg:** Du erklärst doppelte Ergebniswerte anhand der Buchungen.
Die gespeicherten Buchungen werden nicht verändert.

<a id="aufgabe-8"></a>
## 8. Buchungen ausgewählter Kurse anzeigen

- Verwende `practice_bookings`.
- Suche alle Buchungen für Kurs 1 oder Kurs 3.
- Nutze IN, zeige alle vier Spalten und sortiere nach Buchungs-ID.
- Formuliere dieselbe Bedingung zusätzlich mit OR.

**Erfolg:** Beide Abfragen liefern dieselben Buchungen.

<a id="aufgabe-9"></a>
## 9. Eine Buchung verständlich erklären

- Die Verwaltung fragt: Wer hat mit Buchung 6 welchen Kurs gebucht?
- Suche Buchung 6 in `practice_bookings`.
- Notiere Schüler-ID, Kurs-ID und Datum.
- Suche den Namen in `practice_students` anhand der Schüler-ID.
- Suche den Titel in `practice_courses` anhand der Kurs-ID.
- Formuliere einen Antwortsatz mit Name, Kurstitel und Datum.

**Erfolg:** Drei einfache SELECT-Abfragen beantworten die Frage.
Ein JOIN ist nicht erforderlich.

<a id="aufgabe-10"></a>
## 10. Einen Namen gezielt korrigieren

- Diese Aufgabe benötigt keine Änderungen aus anderen Aufgaben.
- Verwende ausschließlich `practice_students`.
- Lege eine Probezeile mit ID 90 an:
- Vorname Jamie, Nachname Taylr, Haus NULL, Schuljahr 1.
- Prüfe die Zeile mit SELECT.
- Korrigiere nur diesen Nachnamen zu Taylor.
- Prüfe die Änderung erneut.
- Entferne abschließend nur die Probezeile mit ID 90.
- Prüfe, dass die acht ursprünglichen Schüler noch vorhanden sind.

**Erfolg:** Der Tippfehler ist korrigiert; der Basisbestand bleibt erhalten.

**Bei Wiederaufnahme:** Existiert Probezeile 90 bereits, prüfe ihren Stand.
Füge sie nicht ein zweites Mal ein.

<a id="aufgabe-11"></a>
## 11. Automatische IDs verwenden

- Diese Aufgabe benötigt keinen Probeeintrag aus Aufgabe 10.
- Verwende `practice_courses`.
- Lege den Probekurs „Astronomie – Probeangebot“ ohne explizite ID an.
- Merke seine ID direkt danach mit LAST_INSERT_ID in derselben Verbindung.
- Zeige den Kurs anhand dieser ID.
- Ändere den Titel zu „Astronomie – Testangebot“ und prüfe das Ergebnis.
- Entferne den Probekurs anhand seiner ID.
- Prüfe, dass die ursprünglichen vier Kurse erhalten sind.

**Erfolg:** Du verwendest die tatsächliche ID, keine angenommene Zahl.

**Bei Wiederaufnahme:** Suche zuerst nach deinem Probekurs.
Füge ihn nicht zusätzlich erneut ein.

<a id="aufgabe-12"></a>
## 12. Eine eigene Übungstabelle anlegen

- Diese Aufgabe verändert keine Tabelle des Basisbestands.
- Erstelle eine neue Tabelle namens `practice_rooms`.
- Sie hat eine automatisch vergebene ganzzahlige Primärschlüssel-ID.
- `name` erlaubt bis zu 80 Zeichen und ist ein Pflichtwert.
- Verwende wie im Vormittag InnoDB.
- Füge „Nordturm“ und „Bibliothek“ als zwei Räume ein.
- Zeige die Räume alphabetisch sortiert an.
- Prüfe die Tabellenstruktur mit DESCRIBE.

**Erfolg:** Eine eigene Tabelle mit zwei Räumen.
Keine spätere Aufgabe braucht diese Tabelle.

**Bei Wiederaufnahme:** Vorhandene Tabelle und Daten erst prüfen.
CREATE und INSERT nicht ungeprüft wiederholen.

<a id="aufgabe-13"></a>
## 13. Regeln und Fehlermeldungen verstehen

- Die folgenden Anweisungen sollen scheitern.
- Sage vorab die verletzte Regel voraus.
- Führe die Anweisungen einzeln aus und lies die Fehlermeldungen.

```sql
INSERT INTO practice_students
    (id, first_name, last_name, house, school_year)
VALUES (1, 'Test', 'Person', NULL, 1);

UPDATE practice_students SET first_name = NULL WHERE id = 1;

UPDATE practice_students SET school_year = 0 WHERE id = 1;
```

- Prüfe Harrys Datensatz nach jedem Versuch.

**Erfolg:** Du ordnest PRIMARY KEY, NOT NULL und CHECK den Fehlern zu.
Harrys gültige Angaben bleiben erhalten.

<a id="aufgabe-14"></a>
## 14. Gültige und ungültige Buchungen unterscheiden

- Verwende `practice_bookings` und den unveränderten Basisbestand.
- Lege eine Probebuchung mit ID 90 an:
- Schüler 8, Kurs 1, Datum 1993-09-04.
- Prüfe die Buchung und entferne sie anschließend anhand ihrer ID.
- Versuche danach diese ungültige Buchung einzufügen:

```sql
INSERT INTO practice_bookings (student_id, course_id, booking_date)
VALUES (999, 1, '1993-09-04');
```

- Erkläre, welche Regel die ungültige Buchung zurückweist.
- Prüfe danach alle Buchungen.

**Erfolg:** Die gültige Probezuordnung war möglich.
Der ungültige Verweis scheitert; am Ende bleiben sieben Buchungen.

**Bei Wiederaufnahme:** Eine vorhandene Probebuchung 90 zuerst prüfen.
Sie ist unabhängig von Schüler-Probezeile 90 in Aufgabe 10.

<a id="aufgabe-15"></a>
## 15. Die Aufteilung der Daten erklären

- Du benötigst nur den Basisbestand, keine Änderung aus anderen Aufgaben.
- Warum steht Hermiones Name nicht in jeder Buchung?
- Was müsste bei mehrfach gespeicherten Namen geändert werden?
- Welche widersprüchlichen Angaben könnten dadurch entstehen?
- Warum verwenden wir keine Spalten `course_1`, `course_2`, `course_3`?
- Erkläre den Nutzen getrennter Tabellen in eigenen Worten.

**Erfolg:** Du begründest die Aufteilung anhand einer konkreten Änderung.
Die formalen Normalformen musst du heute noch nicht erklären.

<a id="aufgabe-16"></a>
## 16. Bonus: Eine Zuordnung mit JOIN lesen

- JOIN wird an Tag 4 vertieft; diese Aufgabe ist freiwillig.
- Das Muster verbindet passende Zeilen über ihre Schlüsselwerte.
- ON beschreibt, welche beiden Werte übereinstimmen müssen.
- AS vergibt hier kurze Namen für Tabellen.

```sql
SELECT s.last_name, b.booking_date
FROM practice_students AS s
INNER JOIN practice_bookings AS b ON s.id = b.student_id
WHERE b.booking_date = '1993-09-01'
ORDER BY s.last_name, b.id;
```

- Führe das Muster aus und erkläre den zweimaligen Nachnamen Granger.
- Übertrage es auf `practice_courses` und `practice_bookings`.
- Zeige für Buchungen vom 2. September Kurstitel und Buchungsdatum.
- Sortiere nach Buchungs-ID.

**Erfolg:** Eine Abfrage verbindet Kurstitel mit passenden Buchungen.
Keine gespeicherten Zeilen werden verändert.


