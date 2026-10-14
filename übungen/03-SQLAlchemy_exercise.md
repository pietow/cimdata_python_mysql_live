# SQLAlchemy – Übungen für Tag 3

## Überblick

Heute erweitert ihr das Kursbuchungssystem mit SQLAlchemy.
Ihr lest Schüler und Kurse. Danach speichert ihr eigene Probeangebote.
Zum Schluss verbindet ihr Schüler und Kurse über eine Buchung.

- Alle Python-Dateien liegen direkt im Ordner tag3.
- Verwendet SessionLocal und engine aus der fertigen Datei tag3/db.py.
- Arbeitet ausschließlich mit den Tabellen practice3_students,
  practice3_courses und practice3_bookings.
- Der Live-Bestand students, courses und bookings bleibt erhalten.
- Führt eure Programme aus und vergleicht das Ergebnis mit der Erwartung.
- Erklärt bei Schreibaufgaben, wo COMMIT oder ROLLBACK erfolgt.
- Am Ende bleiben acht Schüler, vier Kurse und sieben Buchungen erhalten.
- Eigene Probezeilen immer anhand ihrer erzeugten IDs entfernen.
- Nummernlücken sind erlaubt. Erwartet keine bestimmte neue ID.

| Aufgabe | Ihr übt |
| --- | --- |
| 1 | Übungsbestand und Modelle vorbereiten |
| 2 | Einen Kurs mit Core lesen |
| 3 | Schüler mit ORM filtern |
| 4 | Einen fehlenden Kurs behandeln |
| 5 | Ein Probeangebot vollständig verwalten |
| 6 | Eine Änderung zurückrollen |
| 7 | Eine vollständige Anmeldung speichern |
| 8 | Verwandte Objekte lesen |
| 9 | Eine vorhandene Buchung selbstständig umbuchen |
| 10–14 | Autoflush, Laden, Tests und größere Transaktionen |

## Vor dem Start

- In einer PowerShell im Unterrichtsprojekt arbeiten.
- Die MySQL-Sitzung für SOURCE in einer zweiten PowerShell öffnen.

```powershell
.\.venv\Scripts\Activate.ps1
python -c "import sys; print(sys.executable)"
docker compose up -d --wait
docker compose exec db mysql --user=dumbledore --password hogwarts
```

- Das lokale Passwort eingeben, das ihr seit Tag 1 verwendet.
- Wenn die Aktivierung blockiert ist, das venv-Python direkt aufrufen.
- Dann in allen Python-Befehlen diesen Pfad statt python verwenden.

```powershell
.\.venv\Scripts\python.exe --version
```

<a id="aufgabe-1"></a>

## 1. Den Übungsbestand vorbereiten

Die Verwaltung benötigt einen unabhängigen Bestand für eure Versuche.

### Aufgaben

1. Legt die beiden SQL-Dateien aus den folgenden Blöcken an.
2. Führt das Setup einmal in eurer MySQL-Sitzung aus.
3. Führt anschließend die Kontrolldatei aus.
4. Legt practice_models.py mit dem bereitgestellten Modellcode an.
5. Zeigt in den Modellen die zwei Fremdschlüssel der Buchung.
6. Erklärt, warum house den Wert None haben darf.

- Das Setup ist Startmaterial. Ihr müsst es nicht selbst entwerfen.
- Es benötigt keine Tabellen oder Übungsergebnisse aus früheren Tagen.
- Importiert es nur, wenn die drei practice3-Tabellen noch nicht existieren.
- Nach einem Fehler zuerst prüfen, welche Anweisungen ausgeführt wurden.
- Ein SQL-Fehler hält einen manuellen SOURCE-Import nicht zwingend an.
- Bei bereits vorhandenem Bestand nur die Kontrolle ausführen.

### Startmaterial: SQL-Setup

<!-- file: sql/tag3/90_practice_setup.sql -->
- Lokal: `.\sql\tag3\90_practice_setup.sql`.

```sql
USE hogwarts;

CREATE TABLE practice3_students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    house VARCHAR(20) NULL,
    school_year TINYINT NOT NULL,
    CONSTRAINT ck_practice3_students_school_year
        CHECK (school_year BETWEEN 1 AND 7)
) ENGINE=InnoDB;

CREATE TABLE practice3_courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE practice3_bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    booking_date DATE NOT NULL,
    CONSTRAINT fk_practice3_booking_student
        FOREIGN KEY (student_id) REFERENCES practice3_students(id),
    CONSTRAINT fk_practice3_booking_course
        FOREIGN KEY (course_id) REFERENCES practice3_courses(id)
) ENGINE=InnoDB;

START TRANSACTION;
INSERT INTO practice3_students
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

INSERT INTO practice3_courses (id, title)
VALUES
    (1, 'Arithmantik'),
    (2, 'Wahrsagen'),
    (3, 'Alte Runen'),
    (4, 'Pflege magischer Geschöpfe');

INSERT INTO practice3_bookings
    (id, student_id, course_id, booking_date)
VALUES
    (1, 1, 2, '1993-09-01'),
    (2, 2, 1, '1993-09-01'),
    (3, 2, 3, '1993-09-01'),
    (4, 3, 2, '1993-09-02'),
    (5, 4, 4, '1993-09-02'),
    (6, 5, 3, '1993-09-01'),
    (7, 6, 4, '1993-09-03');
COMMIT;
```

```text
SOURCE /work/sql/tag3/90_practice_setup.sql;
```

### Startmaterial: SQL-Kontrolle

<!-- file: sql/tag3/91_practice_check.sql -->
- Lokal: `.\sql\tag3\91_practice_check.sql`.

```sql
USE hogwarts;

SELECT 'practice3_students' AS table_name, COUNT(*) AS row_count
FROM practice3_students
UNION ALL
SELECT 'practice3_courses', COUNT(*) FROM practice3_courses
UNION ALL
SELECT 'practice3_bookings', COUNT(*) FROM practice3_bookings;

SELECT id, first_name, last_name, house, school_year
FROM practice3_students ORDER BY id;
SELECT id, title FROM practice3_courses ORDER BY id;
SELECT id, student_id, course_id, booking_date
FROM practice3_bookings ORDER BY id;
```

```text
SOURCE /work/sql/tag3/91_practice_check.sql;
```

### Startmaterial: Modelle

<!-- file: tag3/practice_models.py -->
- Lokal: `.\tag3\practice_models.py`.

```python
from datetime import date

from sqlalchemy import CheckConstraint, Date, ForeignKey, String
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.orm import relationship


class Base(DeclarativeBase):
    pass


class Student(Base):
    __tablename__ = "practice3_students"
    __table_args__ = (
        CheckConstraint(
            "school_year BETWEEN 1 AND 7",
            name="ck_practice3_students_school_year",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    house: Mapped[str | None] = mapped_column(String(20))
    school_year: Mapped[int] = mapped_column(TINYINT)
    bookings: Mapped[list["Booking"]] = relationship(
        back_populates="student"
    )


class Course(Base):
    __tablename__ = "practice3_courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    bookings: Mapped[list["Booking"]] = relationship(
        back_populates="course"
    )


class Booking(Base):
    __tablename__ = "practice3_bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("practice3_students.id"))
    course_id: Mapped[int] = mapped_column(ForeignKey("practice3_courses.id"))
    booking_date: Mapped[date] = mapped_column(Date)
    student: Mapped[Student] = relationship(back_populates="bookings")
    course: Mapped[Course] = relationship(back_populates="bookings")
```

### Erfolgskriterien

- Die Kontrolle zeigt acht Schüler, vier Kurse und sieben Buchungen.
- Schüler 2 ist Hermione Granger und hat zwei Buchungen.
- Schüler 8 ist Alex Morgan und hat kein Haus.
- Die Kurs-IDs 1–4 existieren. Kurs 999 fehlt.
- practice_models.py bildet ausschließlich practice3-Tabellen ab.
- Keine neue Haupttabelle und kein neues Schema wurden angelegt.
- Mapped[str | None] beschreibt für house Text oder None in Python.
- String(20) beschreibt die SQL-Zeichenkette mit maximal 20 Zeichen.


<a id="aufgabe-2"></a>

## 2. Einen Kurs mit Core lesen

Die Verwaltung fragt nach dem Kurstitel zur ID 3.

### Aufgaben

1. Erstellt tag3/practice_core.py.
2. Beschreibt practice3_courses als Core-Table mit id und title.
3. Baut eine select-Abfrage mit einem benannten Parameter wanted_id.
4. Übergebt beim Ausführen den Wert 3 als Dictionary.
5. Gebt ID und Titel innerhalb der Connection aus.
6. Probiert die ID 999. Setzt danach den Wert wieder auf 3.

### Erfolgskriterien

- ID 3 liefert: 3 Alte Runen.
- ID 999 liefert keine Ergebniszeile.
- Der Parameterwert wird nicht in einen SQL-String eingebaut.
- Die Daten bleiben unverändert.

```powershell
python .\tag3\practice_core.py
```

<a id="aufgabe-3"></a>

## 3. Schüler nach Haus filtern

Die Verwaltung braucht eine Liste aller Schüler aus Gryffindor.
Danach soll sie auch die Schüler ohne Haus sehen.

### Aufgaben

1. Erstellt tag3/practice_filter.py.
2. Importiert Student aus practice_models.
3. Öffnet eine Session mit SessionLocal.
4. Wählt die Gryffindor-Schüler mit select und where aus.
5. Sortiert die Ausgabe nach der Schüler-ID.
6. Gebt ID, Vorname und Nachname aus.
7. Ergänzt eine zweite Abfrage mit house.is_(None).
8. Gebt dort ID und Vorname mit dem Hinweis „Ohne Haus“ aus.

### Erfolgskriterien

- Die erste Liste enthält Harry, Hermione, Ron und Ginny.
- Ihre IDs sind in dieser Reihenfolge 1, 2, 3 und 7.
- Die zweite Liste enthält nur Alex mit ID 8.
- Ihr lest die ORM-Attribute während die Session offen ist.

```powershell
python .\tag3\practice_filter.py
```

<a id="aufgabe-4"></a>

## 4. Einen fehlenden Kurs behandeln

Die Verwaltung soll bei einer unbekannten ID eine klare Antwort erhalten.

### Aufgaben

1. Erstellt tag3/practice_get.py.
2. Verwendet das Course-Modell aus practice_models.
3. Ladet nacheinander die IDs 3 und 999 mit session.get.
4. Gebt bei einem Treffer ID und Titel aus.
5. Gebt bei None die ID und „Nicht gefunden“ aus.
6. Erklärt, warum ihr vor dem Zugriff auf title prüfen müsst.

### Erfolgskriterien

- ID 3 liefert Alte Runen.
- ID 999 liefert „Nicht gefunden“.
- Es entsteht kein AttributeError.
- Es wird kein fehlender Datensatz automatisch angelegt.

```powershell
python .\tag3\practice_get.py
```

<a id="aufgabe-5"></a>

## 5. Ein Probeangebot vollständig verwalten

Die Verwaltung möchte eine Runenwerkstatt testweise in den Katalog nehmen.
Nach der Prüfung soll das Probeangebot wieder verschwinden.

### Aufgaben

1. Erstellt tag3/practice_course_operations.py.
2. Importiert Course aus practice_models und SessionLocal aus db.
3. Schreibt create_course(title). Die Funktion gibt die neue ID zurück.
4. Schreibt get_course(course_id). Sie liefert ein Tupel oder None.
5. Schreibt rename_course(course_id, title). Sie liefert True oder False.
6. Schreibt delete_course(course_id). Sie liefert True oder False.
7. Verwendet bei Schreibfunktionen SessionLocal.begin.
8. Erstellt tag3/practice_crud.py für euren vollständigen Testablauf.
9. Legt „Runenwerkstatt - Probe“ an und merkt euch die erzeugte ID.
10. Lest dieses Angebot über eine neue Session.
11. Ändert genau dieses Angebot in „Runenwerkstatt“ und lest es erneut.
12. Entfernt es anschließend anhand seiner ID. Nutzt dafür finally.
13. Fragt dieselbe ID noch einmal ab.

### Erfolgskriterien

- Nach dem Anlegen ist das Angebot in einer neuen Session sichtbar.
- Der Rückgabewert von get_course enthält ID und Titel.
- rename_course und delete_course melden True bei Erfolg.
- Eine fehlende ID liefert None beim Lesen und False beim Ändern.
- Nach dem Löschen liefert get_course für eure erzeugte ID None.
- Am Ende sind wieder nur die ursprünglichen vier Kurse vorhanden.
- Die gebuchten Kurse 1–4 werden nicht gelöscht oder umbenannt.

```powershell
python .\tag3\practice_crud.py
```

<a id="aufgabe-6"></a>

## 6. Ein Haus nur zur Probe ändern

Die Verwaltung will Alex Ravenclaw zuordnen, die Änderung aber verwerfen.

### Aufgaben

1. Erstellt tag3/practice_rollback.py.
2. Ladet Schüler 8 aus practice3_students über das ORM.
3. Gebt den ursprünglichen Wert von house aus.
4. Setzt house auf Ravenclaw und ruft flush auf.
5. Gebt den geänderten Wert innerhalb der Transaktion aus.
6. Ruft rollback auf. Verwendet hier keinen begin-Kontext mit Auto-COMMIT.
7. Öffnet eine neue Session und lest Alex erneut.
8. Erklärt den Unterschied zwischen flush und commit.

### Erfolgskriterien

- Vorher: None.
- Innerhalb der Transaktion: Ravenclaw.
- Nach ROLLBACK und erneutem Lesen: None.
- Die Änderung wurde an MySQL gesendet und anschließend zurückgesetzt.

```powershell
python .\tag3\practice_rollback.py
```

<a id="aufgabe-7"></a>

## 7. Schüler und Buchung gemeinsam speichern

Mila Hart möchte sich anmelden und Arithmantik buchen.
Eine Anmeldung ohne gültige Buchung darf nicht gespeichert bleiben.

### Aufgaben

1. Erstellt tag3/practice_registration.py.
2. Verwendet Student und Booking aus practice_models.
3. Schreibt register_student mit Vorname, Nachname, Kurs-ID und Datum.
4. Legt den Schüler mit house=None und school_year=1 an.
5. Verwendet für Schüler und Buchung denselben begin-Kontext.
6. Ruft nach dem Anlegen des Schülers flush auf und verwendet seine ID.
7. Gebt nach Erfolg die Schüler-ID und die Buchungs-ID zurück.
8. Erstellt tag3/practice_registration_demo.py.
9. Zählt zuerst Schüler und Buchungen und merkt euch beide Werte.
10. Versucht Milas Anmeldung mit Kurs 999 am 5. September 1993.
11. Fangt IntegrityError außerhalb der Operationsfunktion ab.
12. Prüft in einer neuen Session, dass beide Zeilenzahlen gleich bleiben.
13. Wiederholt die Anmeldung mit Kurs 1 und demselben Datum.
14. Prüft Schüler, Kurs und Datum über die zurückgegebenen IDs.
15. Entfernt in finally zuerst die eigene Buchung und dann Mila.
16. Ruft nach dem Entfernen der Buchung flush auf.
17. Kontrolliert erneut beide Zeilenzahlen.

### Erfolgskriterien

- Nach dem Fehlerfall: acht Schüler und sieben Buchungen.
- Nach dem Erfolgsfall: neun Schüler und acht Buchungen.
- Mila hat eine Buchung für Arithmantik am 5. September 1993.
- Nach dem Aufräumen: acht Schüler und sieben Buchungen.
- Die vier Kurse und alle ursprünglichen Datensätze bleiben erhalten.
- Zwischen dem Anlegen des Schülers und der Buchung steht kein COMMIT.
- Neue IDs werden übernommen und nicht geraten.

```powershell
python .\tag3\practice_registration_demo.py
```

<a id="aufgabe-8"></a>

## 8. Hermiones gebuchte Kurse ausgeben

Die Verwaltung möchte Hermiones Buchungen mit lesbaren Namen sehen.

### Aufgaben

1. Erstellt tag3/practice_relationships.py.
2. Wählt die Booking-Objekte für Schüler 2 aus.
3. Sortiert nach der Buchungs-ID.
4. Lest Vorname und Nachname über booking.student.
5. Lest den Kurstitel über booking.course.
6. Gebt Namen, Kurstitel und Buchungsdatum aus.
7. Bleibt dabei innerhalb der offenen Session.
8. Erklärt den Unterschied zwischen student_id und student.

### Erfolgskriterien

```text
Hermione Granger Arithmantik 1993-09-01
Hermione Granger Alte Runen 1993-09-01
```

- Ihr schreibt keine zusätzliche manuelle SELECT-Abfrage pro Kurstitel.
- relationship übernimmt den Objektzugriff; SQL kann dabei nachgeladen werden.
- Die Daten bleiben unverändert.

```powershell
python .\tag3\practice_relationships.py
```

<a id="aufgabe-9"></a>

## 9. Eine vorhandene Buchung umbuchen

Diese Pflichtaufgabe verlangt Transfer. Plant zuerst euren Lösungsweg.
Die Verwaltung möchte eine vorhandene Buchung auf einen anderen Kurs umbuchen.
Bei einem ungültigen Zielkurs muss die bisherige Buchung erhalten bleiben.

### Auftrag

- Erstellt tag3/practice_rebooking.py mit rebook(booking_id, course_id).
- Bei Erfolg liefert die Funktion True, bei fehlender Buchung False.
- Ein ungültiger Zielkurs soll IntegrityError auslösen.
- Behandelt diesen Fehler erst außerhalb der Operationsfunktion.
- Verwendet dieselben Session- und Transaktionsmuster wie bisher.
- Erstellt tag3/practice_rebooking_demo.py für euren Prüfablauf.
- Legt dafür eine eigene Probebuchung für Harry und Wahrsagen an.
- Datum der Probebuchung: 6. September 1993.
- Merkt euch ihre erzeugte ID; verändert keine ursprüngliche Buchung.
- Bucht eure Probebuchung zuerst auf Alte Runen um.
- Versucht danach denselben Vorgang mit dem ungültigen Kurs 999.
- Entfernt in finally nur eure eigene Probebuchung anhand ihrer ID.
- Prüft danach auch den Fall der inzwischen fehlenden Buchungs-ID.

### Erfolgskriterien

- Nach dem Anlegen gibt es acht Schüler, vier Kurse und acht Buchungen.
- Das erste Umbuchen liefert True; eine neue Session liest Kurs-ID 3.
- Schüler-ID, Buchungs-ID und Datum bleiben beim Umbuchen gleich.
- Der ungültige Zielkurs löst den erwarteten Datenbankfehler aus.
- Nach dem Fehler liest eine neue Session weiterhin Kurs-ID 3.
- Umbuchen erzeugt keine zusätzliche Buchung und keinen neuen Schüler.
- Nach dem Aufräumen liefert rebook für eure erzeugte ID False.
- Der Grundbestand beträgt wieder acht Schüler, vier Kurse, sieben Buchungen.
- Alle ursprünglichen Buchungen bleiben unverändert.

### Begründet euren Ablauf

- Welche Modellklasse braucht die Operationsfunktion?
- Welches gespeicherte Attribut verändert ihr?
- Welche Datenbankregel lehnt Kurs 999 ab?
- Warum prüft ihr das Ergebnis jeweils in einer neuen Session?

```powershell
python .\tag3\practice_rebooking_demo.py
```

## Bonusaufgaben

Bearbeitet die folgenden Aufgaben, wenn die Pflichtaufgaben abgeschlossen sind.
Ihr könnt sie nach Interesse auswählen. Aufgabe 12 benötigt Aufgaben 5, 7 und 9.

<a id="aufgabe-10"></a>

## 10. Autoflush beobachten

Die Verwaltung möchte verstehen, wann SQLAlchemy vorgemerkte Daten sendet.

### Aufgaben

1. Erstellt tag3/practice_autoflush.py.
2. Schaltet engine.echo vorübergehend ein.
3. Fügt den neuen Kurs „Autoflush - Probe“ zu einer Session hinzu.
4. Gebt seine ID aus, ohne selbst flush aufzurufen.
5. Sucht den neuen Kurs mit einer ORM-select-Abfrage nach seinem Titel.
6. Gebt seine ID erneut aus und beobachtet INSERT und SELECT im Log.
7. Rollt zurück und schaltet echo in finally wieder aus.
8. Prüft in einer neuen Session, dass der Kurs nicht gespeichert wurde.

### Erfolgskriterien

- Vor der Abfrage ist die ID None.
- Vor dem SELECT sendet SQLAlchemy einen INSERT.
- Nach der Abfrage hat das Objekt eine ID.
- Die abschließende Suche nach ROLLBACK liefert eine leere Liste.
- Erklärt, warum Autoflush kein COMMIT bedeutet.

```powershell
python .\tag3\practice_autoflush.py
```

<a id="aufgabe-11"></a>

## 11. Alle Buchungen mit weniger Nachladeabfragen anzeigen

Die Verwaltung möchte alle Schüler und ihre gebuchten Kurstitel ausgeben.

### Aufgaben

1. Erstellt tag3/practice_eager_loading.py.
2. Gebt zuerst alle Schüler und ihre Kurstitel über relationships aus.
3. Aktiviert echo und beobachtet die zusätzlichen SELECT-Abfragen.
4. Ergänzt selectinload für Student.bookings und Booking.course.
5. Vergleicht die Abfragezahl mit der ersten Variante.
6. Zählt nur SELECTs auf practice3-Tabellen, keine Treiberinitialisierung.
7. Schaltet echo in finally wieder aus.

### Erfolgskriterien

- Beide Varianten zeigen dieselben Schüler und gebuchten Kurse.
- Ginny und Alex erscheinen ebenfalls, mit einer leeren Kursliste.
- Die gebündelte Variante verwendet hier drei Tabellen-SELECTs.
- Alle Attribute werden innerhalb der Session gelesen.
- Erklärt, welche Nachladeabfragen gebündelt wurden.

```powershell
python .\tag3\practice_eager_loading.py
```

<a id="aufgabe-12"></a>

## 12. Die Operationsfunktionen automatisiert prüfen

Die Verwaltung möchte nach Änderungen dieselben Abläufe erneut testen können.
Verwendet pytest, das wir später auch für die API-Tests einsetzen.

### Startmaterial für den Testbonus

<!-- file: requirements-tag3-tests.txt -->
- Lokal: `.\requirements-tag3-tests.txt`.

```text
-r requirements-tag3.txt
pytest
```

```powershell
python -m pip install -r requirements-tag3-tests.txt
python -m pip check
python -m pytest --version
```

### Aufgaben

1. Erstellt tag3/test_practice_operations.py mit pytest-Testfunktionen.
2. Verwendet eure Funktionen aus Aufgaben 5, 7 und 9.
3. Testet Anlegen, Lesen, Umbenennen und Löschen eines Probeangebots.
4. Nutzt als ersten Titel „O'Neil - Testkurs“.
5. Prüft jeden gespeicherten Titel mit einer neuen Session.
6. Prüft None und False für die anschließend gelöschte Kurs-ID.
7. Entfernt eure Probezeile auch dann, wenn eine Assertion fehlschlägt.
8. Testet die Anmeldung bei Kurs 999 mit pytest.raises(IntegrityError).
9. Vergleicht danach Schüler- und Buchungszahl mit dem Ausgangswert.
10. Testet Umbuchen mit einer eigenen Probebuchung wie in Aufgabe 9.
11. Prüft Erfolg, ungültigen Zielkurs und fehlende Buchungs-ID.
12. Prüft nach dem Fehler Zielkurs, Schüler-ID und Buchungsdatum erneut.
13. Entfernt die Probebuchung in finally und kontrolliert den Grundbestand.
14. Führt die Tests ohne andere gleichzeitig schreibende Programme aus.

### Erfolgskriterien

- Drei Testfunktionen laufen erfolgreich durch; pytest meldet 3 passed.
- Ein Apostroph im Titel wird korrekt gespeichert.
- Nach der ungültigen Anmeldung bleibt kein neuer Schüler zurück.
- Nach der ungültigen Umbuchung bleibt die vorige Kurszuordnung erhalten.
- Der Bestand beträgt weiterhin acht Schüler, vier Kurse, sieben Buchungen.
- Erklärt, warum diese Tests eine laufende MySQL-Datenbank benötigen.

```powershell
python -m pytest .\tag3\test_practice_operations.py -v
```

<a id="aufgabe-13"></a>

## 13. Einen Kurs mit mehreren Buchungen gemeinsam anlegen

Diese Aufgabe verlangt Transfer: Eine einzelne Anmeldung wird zur Gruppe.

Die Verwaltung plant eine Runenwerkstatt für Harry und Luna.
Kurs und Buchungen sollen gemeinsam entstehen.

### Aufgaben

1. Erstellt tag3/practice_group.py.
2. Schreibt create_group_course(title, student_ids).
3. Legt in einer Transaktion einen neuen Course an und führt flush aus.
4. Legt für jede übergebene Schüler-ID eine Booking an.
5. Nutzt dabei course=course und das Datum 6. September 1993.
6. Gebt die Kurs-ID erst nach erfolgreicher Transaktion zurück.
7. Testet zuerst „Gruppenkurs - Fehler“ mit den Schüler-IDs 1 und 999.
8. Prüft, dass weder dieser Kurs noch eine neue Buchung übrig bleiben.
9. Testet „Runenwerkstatt - Gruppe“ mit den Schüler-IDs 1 und 5.
10. Prüft zwei Buchungen mit demselben neuen Kurs: Harry und Luna.
11. Entfernt in finally eure eigenen Buchungen, dann den erzeugten Kurs.
12. Kontrolliert den Grundbestand erneut.

### Erfolgskriterien

- Eine ungültige Schüler-ID rollt den gesamten Gruppenkurs zurück.
- Erfolg erzeugt genau einen Kurs und zwei Buchungen.
- Es wird keine neue Schülerzeile angelegt.
- Die Buchungen werden über ein gemeinsames Kursobjekt verknüpft.
- Nach dem Aufräumen beträgt der Bestand wieder acht, vier und sieben.

```powershell
python .\tag3\practice_group.py
```

### Transferfrage

- Was passiert, wenn die übergebene Schülerliste leer ist?
- Ist ein Kurs ohne Buchungen für eine geplante Runenwerkstatt sinnvoll?
- Beschreibt zuerst das aktuelle Verhalten. Begründet dann eure Entscheidung.

<a id="aufgabe-14"></a>

## 14. Nach einem Flush-Fehler dieselbe Session weiterverwenden

Die Verwaltung möchte einen fehlgeschlagenen Buchungsversuch behandeln.
Danach soll dieselbe Session eine vorhandene Kurszeile lesen können.

### Aufgaben

1. Erstellt tag3/practice_recovery.py.
2. Öffnet eine normale Session ohne begin-Kontext für die ganze Arbeit.
3. Merkt eine Booking für Schüler 1 und Kurs 999 vor.
4. Ruft flush auf und fangt IntegrityError ab.
5. Ruft im Fehlerfall session.rollback auf.
6. Lest anschließend in derselben Session Kurs 1 und gebt den Titel aus.
7. Erklärt, warum nach dem Fehler ein rollback nötig ist.

### Erfolgskriterien

- Der ungültige Kurs erzeugt den erwarteten Datenbankfehler.
- Nach rollback kann dieselbe Session Arithmantik lesen.
- Es wurde keine zusätzliche Buchung gespeichert.
- Ohne rollback würde ein Folgezugriff PendingRollbackError auslösen.

```powershell
python .\tag3\practice_recovery.py
```

## Abschlusskontrolle

Führt die Kontrolldatei aus Aufgabe 1 erneut aus.

```text
SOURCE /work/sql/tag3/91_practice_check.sql;
```

- Acht Schüler, vier Kurse und sieben Buchungen.
- Alex hat weiterhin kein Haus.
- Die vier ursprünglichen Kurstitel sind unverändert.
- Keine Probeangebote und keine neuen Schüler bleiben zurück.
- Die Tabellen ohne practice3-Präfix wurden nicht verändert.
