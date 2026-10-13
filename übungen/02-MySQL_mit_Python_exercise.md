# MySQL mit Python – Übungen am Nachmittag

## Überblick

Die Verwaltung von Hogwarts möchte ihre Daten mit Python bearbeiten.
Du liest Kurse und Schüler, verarbeitest Eingaben und speicherst Änderungen.

- Nutze ausschließlich die Tabellen mit dem Präfix `practice2_`.
- Die Live-Tabellen und die Tag-1-Übungstabellen bleiben erhalten.
- Nach Aufgabe 1 sind alle weiteren Aufgaben unabhängig voneinander.
- Sage vor jeder Abfrage das erwartete Ergebnis voraus.
- Vergleiche die Ausgabe anschließend mit deiner Vorhersage.

### Dein Arbeitsplatz

- Arbeite im Projektordner 
- Die Datei `tag2/db.py` stellt `get_connection()` bereit.
- Speichere deine Programme direkt im Ordner `tag2`.
- SOURCE-Befehle gehören in den geöffneten MySQL-Client.
- Speichere Dateien vor dem Ausführen.
- Verwende für jeden Eingabewert die Parameter von `cursor.execute()`.
- Schließe Cursor und Verbindung nach der Arbeit.
- Bestätige Änderungen bewusst oder nimm sie mit ROLLBACK zurück.

### Unsere Tabellen

| Tabelle | Inhalt |
|---|---|
| practice2_students | Schüler mit Namen, Haus und Schuljahr |
| practice2_courses | Kurse mit ID und Titel |
| practice2_bookings | Buchung mit Schüler-ID, Kurs-ID und Datum |

- Eine Buchung verweist auf genau einen Schüler und einen Kurs.
- Namen und Kurstitel stehen in ihren jeweiligen Tabellen.
- Nora aus der Live-Anmeldung gehört nicht zu diesem Übungsbestand.

## 1. Den Übungsbestand einrichten

MySQL muss laufen. Öffne den Client, falls er noch nicht geöffnet ist.

```powershell
docker compose up -d --wait --wait-timeout 180
docker compose exec db mysql `
  --default-character-set=utf8mb4 -u dumbledore -p hogwarts
```

Lege die folgende Datei an und speichere den vollständigen Inhalt.
Führe sie einmal aus, wenn die drei Tabellen noch nicht existieren.

<!-- file: sql/tag2/90_practice_setup.sql -->
- Lokal: `.\sql\tag2\90_practice_setup.sql`.

```sql
USE hogwarts;

CREATE TABLE practice2_students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    house VARCHAR(20) NULL,
    school_year TINYINT NOT NULL,
    CONSTRAINT ck_practice2_students_school_year
        CHECK (school_year BETWEEN 1 AND 7)
) ENGINE=InnoDB;

CREATE TABLE practice2_courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE practice2_bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    booking_date DATE NOT NULL,
    CONSTRAINT fk_practice2_bookings_student
        FOREIGN KEY (student_id) REFERENCES practice2_students(id),
    CONSTRAINT fk_practice2_bookings_course
        FOREIGN KEY (course_id) REFERENCES practice2_courses(id)
) ENGINE=InnoDB;

INSERT INTO practice2_students
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

INSERT INTO practice2_courses (id, title)
VALUES
    (1, 'Arithmantik'),
    (2, 'Wahrsagen'),
    (3, 'Alte Runen'),
    (4, 'Pflege magischer Geschöpfe');

INSERT INTO practice2_bookings (id, student_id, course_id, booking_date)
VALUES
    (1, 1, 2, '1993-09-01'),
    (2, 2, 1, '1993-09-01'),
    (3, 2, 3, '1993-09-01'),
    (4, 3, 2, '1993-09-02'),
    (5, 4, 4, '1993-09-02'),
    (6, 5, 3, '1993-09-01'),
    (7, 6, 4, '1993-09-03');

SELECT * FROM practice2_students ORDER BY id;
SELECT * FROM practice2_courses ORDER BY id;
SELECT * FROM practice2_bookings ORDER BY id;
```

```text
SOURCE /work/sql/tag2/90_practice_setup.sql;
```

Die erste Liste zeigt acht Schüler, die zweite vier Kurse.
Die dritte Liste zeigt sieben Buchungen.
Prüfe diese drei Ergebnisse, bevor du weiterarbeitest.

Lege zusätzlich eine eigene Datei zum erneuten Kontrollieren an.
Diese Datei verändert keine Daten und darf wiederholt geladen werden.

<!-- file: sql/tag2/91_practice_check.sql -->
- Lokal: `.\sql\tag2\91_practice_check.sql`.

```sql
USE hogwarts;

SELECT * FROM practice2_students ORDER BY id;
SELECT * FROM practice2_courses ORDER BY id;
SELECT * FROM practice2_bookings ORDER BY id;
```

```text
SOURCE /work/sql/tag2/91_practice_check.sql;
```

Falls die Tabellen bereits existieren, verwende nur die Kontrolldatei.
Lösche keine Tabellen und importiere die Beispieldaten nicht erneut.

## 2. Einen einzelnen Kurs finden

Die Verwaltung kennt eine Kurs-ID und möchte den Titel nachschlagen.

- Datei: `tag2/exercise_02.py`.
- Schreibe die Funktion `find_course(course_id)`.
- Lies ID und Titel aus `practice2_courses`.
- Übergebe die ID als Parameter.
- Verwende `fetchone()`.
- Gib die Ergebniszeile oder `None` zurück.
- Zeige bei keinem Treffer eine verständliche Meldung.
- Prüfe die Funktion mit den IDs 3 und 999.

**Erfolg:** ID 3 liefert „Alte Runen“. ID 999 wird nicht gefunden.

## 3. Eine Hausliste erstellen

Die Verwaltung braucht die Namen aller Schüler eines Hauses.

- Datei: `tag2/exercise_03.py`.
- Schreibe die Funktion `find_house(house)`.
- Verwende `practice2_students`.
- Lies ID, Vorname und Nachname.
- Filtere mit einem Parameter nach dem Haus.
- Sortiere nach der Schüler-ID.
- Gib alle Treffer als Liste zurück.
- Prüfe mit Ravenclaw und Gryffindor.

**Erfolg:** Ravenclaw liefert eine Person. Gryffindor liefert vier Personen.

## 4. Buchungen nach Datum suchen

Die Verwaltung möchte Buchungen innerhalb eines Zeitraums kontrollieren.

- Datei: `tag2/exercise_04.py`.
- Schreibe die Funktion `find_bookings(start_date, end_date)`.
- Verwende `practice2_bookings`.
- Lies alle vier Spalten und sortiere nach Buchungs-ID.
- Nutze BETWEEN und zwei Parameter.
- Übergib die Grenzen als Python-`date`-Objekte.
- Prüfe zuerst den Zeitraum vom 1. bis 1. September 1993.
- Prüfe danach den Zeitraum vom 3. bis 4. September 1993.

**Erfolg:** Die erste Suche liefert vier Buchungen, die zweite eine.

## 5. Einen Teil des Nachnamens suchen

Die Verwaltung kennt oft nur einen Teil des Namens.

- Datei: `tag2/exercise_05.py`.
- Schreibe die Funktion `find_names(part)`.
- Suche mit LIKE in `practice2_students.last_name`.
- Der Text darf an jeder Stelle im Nachnamen vorkommen.
- Baue das Suchmuster als Python-Wert und übergib es als Parameter.
- Zeige ID, Vorname und Nachname. Sortiere nach ID.
- Prüfe die Eingaben `Weas`, `Love` und `O'Neil`.
- Prüfe auch diese Eingabe als normalen Suchwert:

```text
' OR 1=1 --
```

**Erfolg:** Die Namenssuche funktioniert.
Das Apostroph erzeugt keinen SQL-Fehler.
Die letzte Eingabe verändert nicht die Bedeutung deiner SQL-Anweisung.

**Frage:** Welche Bedeutung haben % und _ innerhalb eines LIKE-Musters?

## 6. Eine Änderung zur Probe ausführen

Die Verwaltung möchte Alex vorläufig dem Haus Ravenclaw zuordnen.
Diese Änderung soll anschließend vollständig verschwinden.

- Datei: `tag2/exercise_06.py`.
- Verwende `practice2_students` und Schüler-ID 8.
- Ändere das Haus mit einem parametrisierten UPDATE.
- Lies die Person innerhalb derselben Verbindung erneut.
- Nimm die Änderung mit ROLLBACK zurück.
- Öffne eine neue Verbindung und prüfe das Haus nochmals.
- Gib auch die Anzahl der geänderten Zeilen aus.

**Erfolg:** Vor ROLLBACK erscheint Ravenclaw.
Nach ROLLBACK ist das Haus wieder unbekannt.
In Python wird SQL-NULL als `None` gelesen.

## 7. Ein Kursangebot dauerhaft speichern und entfernen

Die Verwaltung möchte „Astronomie - Probeangebot“ testweise veröffentlichen.

- Datei: `tag2/exercise_07.py`.
- Verwende `practice2_courses`.
- Lege das Angebot ohne vorgegebene ID an.
- Übernimm die tatsächlich erzeugte ID aus `lastrowid`.
- Bestätige das INSERT mit COMMIT.
- Öffne eine neue Verbindung und lies genau diesen Kurs.
- Entferne danach nur diesen Kurs anhand seiner ID.
- Bestätige auch DELETE.
- Prüfe mit einer weiteren Abfrage, dass der Kurs entfernt wurde.
- Rolle bei einem Datenbankfehler die noch offenen Änderungen zurück.

**Erfolg:** Eine neue Verbindung findet das gespeicherte Angebot.
Nach der Bereinigung bleiben die vier ursprünglichen Kurse.

**Bei einem Abbruch:** Prüfe zuerst deine ausgegebene Kurs-ID.
Füge dasselbe Probeangebot nicht ungeprüft erneut ein.

## 8. Eine vollständige Anmeldung speichern

Lea Sommer soll als neue Schülerin aufgenommen werden.
Gleichzeitig soll eine Kursbuchung für sie entstehen.
Beide Änderungen bilden einen gemeinsamen Vorgang.

- Datei: `tag2/exercise_08.py`.
- Schreibe eine Funktion `register_student(...)`.
- Verwende `practice2_students` und `practice2_bookings`.
- Übernimm Vorname, Nachname, Haus, Schuljahr und Kurs-ID als Parameter.
- Lege die Person ohne vorgegebene ID an.
- Verwende ihre erzeugte ID direkt für die Buchung.
- Verwende als Buchungsdatum den 4. September 1993.
- Bestätige erst nach beiden erfolgreichen INSERTs.
- Bei einem Datenbankfehler: ROLLBACK und Fehler weitergeben.
- Gib bei Erfolg Schüler-ID und Buchungs-ID zurück.

Prüfe zuerst eine Anmeldung mit Kurs-ID 999.

- Person: Lea Sommer, Haus unbekannt, Schuljahr 1.
- Erkläre die Fehlermeldung.
- Weise nach, dass weder Lea noch ihre Buchung gespeichert wurden.

Prüfe danach eine Anmeldung derselben Person mit Kurs-ID 1.

- Lies die gespeicherte Buchung über eine neue Verbindung.
- Prüfe ihre Schüler-ID und Kurs-ID.
- Entferne danach genau diese Probebuchung und ihre neue Schülerzeile.
- Lösche zuerst die Buchung, danach die Person.
- Verwende die zurückgegebenen IDs.
- Bestätige die Bereinigung gemeinsam.

**Erfolg:** Der Fehlerfall hinterlässt keine halbe Anmeldung.
Der Erfolgsfall speichert beide Zeilen.
Nach der Bereinigung enthält der Bestand wieder acht, vier und sieben Zeilen.

## 9. Bonus: Eine Ergebniszeile als Dictionary lesen

Die Verwaltung möchte in Python mit verständlichen Feldnamen arbeiten.

- Datei: `tag2/exercise_09.py`.
- Lies Luna mit ID 5 aus `practice2_students`.
- Verwende `connection.cursor(dictionary=True)`.
- Wähle ID, Vorname, Nachname und Haus.
- Gib Vorname, Nachname und Haus über ihre Dictionary-Schlüssel aus.
- Berücksichtige auch den Fall ohne Treffer.

**Erfolg:** Die Ausgabe lautet `Luna Lovegood Ravenclaw`.
Du greifst auf die Werte über Spaltennamen zu.

## 10. Bonus: Mehrere Angebote gemeinsam einfügen

Die Verwaltung erhält zwei neue Probeangebote gleichzeitig.

- Datei: `tag2/exercise_10.py`.
- Verwende `practice2_courses`.
- Die Titel lauten „Astronomie - Probe A“ und „Astronomie - Probe B“.
- Füge beide mit `executemany()` und Parametersätzen ein.
- Zeige die Zahl der eingefügten Zeilen.
- Nimm danach beide Änderungen mit einem ROLLBACK zurück.
- Prüfe den unveränderten Kursbestand.

**Erfolg:** Im Probelauf werden zwei Zeilen eingefügt.
Dauerhaft bleiben ausschließlich die vier ursprünglichen Kurse.

**Frage:** Führt `executemany()` automatisch einen COMMIT aus?

## 11. Bonus: Einen COMMIT von außen beobachten

Ein zweites Programm soll neue Kursangebote erst nach der Freigabe sehen.

- Datei: `tag2/exercise_11.py`.
- Öffne zwei Verbindungen zur Datenbank.
- Nenne sie `writer` und `observer`.
- Setze beim Beobachter `autocommit = True`.
- Füge über `writer` ein Probeangebot in `practice2_courses` ein.
- Merke die erzeugte ID. Führe noch keinen COMMIT aus.
- Prüfe mit beiden Verbindungen, ob diese ID sichtbar ist.
- Bestätige die Änderung über `writer`.
- Prüfe die Sichtbarkeit über `observer` nochmals.
- Entferne das eigene Probeangebot und bestätige die Bereinigung.

**Erfolg:** Vor COMMIT sieht nur die eigene Verbindung das Angebot.
Nach COMMIT findet auch der Beobachter die Zeile.
Nach der Bereinigung findet er sie nicht mehr.

**Frage:** Warum sind zwei Cursor derselben Verbindung kein Ersatz
für zwei getrennte Verbindungen?

## 12. Bonus: Einen optionalen Kurswunsch zurücknehmen

Mika Winter soll zunächst erfasst werden.
Ein zusätzlicher Kurswunsch ist in diesem Vorgang optional.
Der gesamte Ablauf bleibt ein Probelauf.

- Datei: `tag2/exercise_12.py`.
- Verwende `practice2_students` und `practice2_bookings`.
- Starte eine Transaktion.
- Füge Mika Winter mit Haus NULL und Schuljahr 1 ein.
- Setze danach einen SAVEPOINT.
- Versuche eine Buchung für Mika mit Kurs-ID 999.
- Fange den erwarteten Fremdschlüsselfehler ab.
- Nimm den optionalen Teilschritt bis zum SAVEPOINT zurück.
- Entferne die Markierung mit RELEASE SAVEPOINT.
- Prüfe innerhalb der Verbindung, dass Mika weiterhin vorhanden ist.
- Beende den Probelauf mit einem vollständigen ROLLBACK.
- Prüfe, dass danach auch Mika nicht dauerhaft gespeichert ist.

**Erfolg:** Die Person bleibt nach ROLLBACK TO innerhalb der Sitzung sichtbar.
Nach dem vollständigen ROLLBACK sind beide Änderungen verschwunden.

**Frage:** Warum passt diese Teilrücknahme nicht zur verbindlichen Anmeldung
aus Aufgabe 8?

## 13. Bonus: Harry vollständig in einen anderen Kurs umbuchen

Harry besucht Wahrsagen. Er möchte stattdessen Arithmantik belegen.
Beim Wechsel müssen die Buchung, die freien Plätze und der Verlauf passen.

### Überblick

- Plane etwa 45–60 Minuten ein.
- Verwende den Übungsbestand aus Aufgabe 1.
- Lege zusätzlich die folgenden drei Tabellen an.
- Ihre Daten sind ein eigener kleiner Bestand für diese Aufgabe.
- Die normalen Schüler, Kurse und Buchungen werden nicht verändert.
- Kurs 1 hat zwei freie Plätze. Kurs 2 hat fünf freie Plätze.
- Harry hat die Buchungs-ID 1 und besucht zunächst Kurs 2.
- Ein Wechsel gibt einen Platz frei und belegt einen anderen.
- Die Gesamtzahl der freien Plätze muss sieben bleiben.

### Ausgangsdaten einrichten

Speichere diese Datei. Lade sie einmal bei noch nicht vorhandenen Tabellen.

<!-- file: sql/tag2/92_transfer_setup.sql -->
- Lokal: `.\sql\tag2\92_transfer_setup.sql`.

```sql
USE hogwarts;

CREATE TABLE practice2_transfer_courses (
    id INT PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    free_places INT NOT NULL,
    CONSTRAINT ck_transfer_free_places CHECK (free_places >= 0)
) ENGINE=InnoDB;

CREATE TABLE practice2_transfer_bookings (
    id INT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    CONSTRAINT fk_transfer_student
        FOREIGN KEY (student_id) REFERENCES practice2_students(id),
    CONSTRAINT fk_transfer_course
        FOREIGN KEY (course_id) REFERENCES practice2_transfer_courses(id)
) ENGINE=InnoDB;

CREATE TABLE practice2_transfer_changes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    course_id INT NOT NULL,
    action VARCHAR(10) NOT NULL,
    changed_at DATETIME NOT NULL,
    CONSTRAINT ck_transfer_action
        CHECK (action IN ('RELEASE', 'RESERVE')),
    CONSTRAINT fk_transfer_change_booking
        FOREIGN KEY (booking_id) REFERENCES practice2_transfer_bookings(id),
    CONSTRAINT fk_transfer_change_course
        FOREIGN KEY (course_id) REFERENCES practice2_transfer_courses(id)
) ENGINE=InnoDB;

INSERT INTO practice2_transfer_courses (id, title, free_places)
VALUES (1, 'Arithmantik', 2), (2, 'Wahrsagen', 5);

INSERT INTO practice2_transfer_bookings (id, student_id, course_id)
VALUES (1, 1, 2);

SELECT * FROM practice2_transfer_courses ORDER BY id;
SELECT * FROM practice2_transfer_bookings ORDER BY id;
SELECT * FROM practice2_transfer_changes ORDER BY id;
```

```text
SOURCE /work/sql/tag2/92_transfer_setup.sql;
```

### Deine Aufgabe

- Datei: tag2/exercise_13.py.
- Nutze get_connection() aus tag2/db.py.
- Schreibe move_booking(booking_id, target_course_id, fail_after_release=False).
- Verwende eine Verbindung für den gesamten Wechsel.
- Starte die Transaktion vor der ersten Abfrage.
- Lies die aktuelle Buchung mit ihrer Kurs-ID.
- Lehne eine fehlende Buchung und denselben Zielkurs ab.
- Lies die freien Plätze der beiden Kurse.
- Lehne einen fehlenden oder vollen Zielkurs ab.
- Verwende bei diesen Abfragen FOR UPDATE.
- Lies die Kurse in aufsteigender ID-Reihenfolge.
- Schreibe einen RELEASE-Eintrag für den bisherigen Kurs.
- Schreibe einen RESERVE-Eintrag für den neuen Kurs.
- Beide Einträge nennen Buchungs-ID, Kurs-ID und Änderungszeit.
- Erhöhe die freien Plätze des bisherigen Kurses um eins.
- Verringere die freien Plätze des neuen Kurses um eins.
- Stelle die bestehende Buchung auf den neuen Kurs um.
- Prüfe nach jedem UPDATE: Genau eine Zeile wurde geändert.
- Bestätige erst nach allen fünf erfolgreichen Schreibschritten.
- Bei Datenbankfehlern und fachlicher Ablehnung: ROLLBACK.
- Gib den Fehler anschließend an den Aufrufer weiter.
- Übergib alle variablen Werte als Parameter.

### Den Fehlerfall nachweisen

- Bei fail_after_release=True: Brich nach der ersten Platzänderung ab.
- Löse dafür einen ValueError aus.
- Zu diesem Zeitpunkt wurden bereits beide Verlaufseinträge eingefügt.
- Fange den Fehler beim Aufruf ab.
- Prüfe alle drei Tabellen über eine neue Verbindung.

**Erfolg:** Harry bleibt in Kurs 2. Die freien Plätze bleiben bei 2 und 5.
Die beiden neuen Verlaufseinträge sind ebenfalls verschwunden.

### Den Erfolg und den Rückweg prüfen

- Rufe die Funktion ohne absichtlichen Fehler mit Buchung 1 und Zielkurs 1 auf.
- Lies alle drei Tabellen über eine neue Verbindung.
- Buche Harry danach mit derselben Funktion wieder auf Kurs 2 um.
- Lösche den Verlauf der beiden erfolgreichen Wechsel nicht.
- Zeige den abschließenden Bestand.

| Zeitpunkt | Freie Plätze Kurs 1 / 2 | Harrys Kurs | Verlaufseinträge |
|---|---|---|---|
| Vorher | 2 / 5 | 2 | 0 |
| Nach dem absichtlichen Fehler | 2 / 5 | 2 | 0 |
| Nach dem ersten Erfolg | 1 / 6 | 1 | 2 |
| Nach der Rückbuchung | 2 / 5 | 2 | 4 |

**Erfolg:** Alle fünf Änderungen bilden einen gemeinsamen Vorgang.
Der Fehlerfall hinterlässt weder falsche Platzanzahlen noch Verlaufseinträge.
Die Rückbuchung stellt Buchung und Plätze wieder her.
Ihr Verlauf bleibt erhalten.

Diese Kontrolldatei darf mehrfach ausgeführt werden.

<!-- file: sql/tag2/93_transfer_check.sql -->
- Lokal: `.\sql\tag2\93_transfer_check.sql`.

```sql
USE hogwarts;

SELECT id, title, free_places FROM practice2_transfer_courses ORDER BY id;
SELECT id, student_id, course_id FROM practice2_transfer_bookings ORDER BY id;
SELECT id, booking_id, course_id, action, changed_at
FROM practice2_transfer_changes ORDER BY id;
```

```text
SOURCE /work/sql/tag2/93_transfer_check.sql;
```

### Dateien für diese Aufgabe sichern

Führe zuerst den Fehlerfall und den erfolgreichen Wechsel aus.
Prüfe den Bestand. Sichere danach die neue Lösung und die SQL-Dateien.

```powershell
git status --short
git add -- tag2/exercise_13.py
git add -- sql/tag2/92_transfer_setup.sql sql/tag2/93_transfer_check.sql
git diff --cached --check
git diff --cached
git commit -m "Kurswechsel mit Commit und Rollback ueben"
```

### Fragen zum Ergebnis

- Warum brauchen auch die Verlaufseinträge dieselbe Transaktion?
- Was wäre nach einem COMMIT zwischen den beiden Platzänderungen falsch?
- Warum ist die Rückbuchung ein neuer Vorgang und kein ROLLBACK?
- Warum reicht eine erfolgreiche execute()-Ausführung allein nicht aus?
- Warum werden Sperren für den Wechsel benötigt?

### Zusätzliche Prüfung

- Prüfe Buchungs-ID 999, Zielkurs 999 und denselben Zielkurs.
- Jeder Versuch soll abgelehnt werden und den Bestand erhalten.
- Führe das Hauptprogramm nur einmal für die beschriebene Ergebnisfolge aus.
- Ein weiterer vollständiger Lauf erzeugt vier weitere Verlaufseinträge.


