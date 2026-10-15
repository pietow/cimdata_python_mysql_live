# Komplexere Abfragen – Übungen für Tag 4

## Überblick

Die Hogwarts-Verwaltung benötigt Auswertungen ihrer Kursbuchungen.
Ihr erstellt zuerst SQL-Abfragen.
Danach nutzt ihr ausgewählte Berichte in Python.

- Aufgaben 2–8 verwenden SQL. Aufgaben 10–11 verwenden ORM.
- Aufgaben 9 und 12 bilden eine freiwillige Vertiefung.
- Bonusaufgaben: 13–15.
- Alle Datenbankabfragen nach dem Setup sind reine Leseabfragen.
- Die Tabellen ohne practice4-Präfix bleiben unangetastet.
- Neue Python-Dateien liegen in tag4. Ihr nutzt die Umgebung aus Tag 3.

- Die richtige Ergebniszeilenzahl ist ein Teil der Prüfung.
- Prüft auch Namen, Daten und gezählte Werte.
- Erläutert bei jeder Aufgabe, was eine Ergebniszeile bedeutet.


| Aufgabe | Verwaltungsauftrag |
| --- | --- |
| 1 | Unabhängigen Übungsbestand vorbereiten |
| 2 | Eine Teilnehmerliste lesen |
| 3 | Gebuchte Kurse eines Hauses finden |
| 4 | Alle Angebote mit Buchungen ab dem 3. September zeigen |
| 5 | Buchungen und verschiedene Personen zählen |
| 6 | Häuser mit Schüler- und Buchungszahlen vergleichen |
| 7 | Schüler mit mehreren verschiedenen Kursen finden |
| 8 | Kursteilnahme mit einer Unterabfrage auswählen |
| 9 | Schüler ohne Buchung seit dem 3. September ermitteln |
| 10 | Teilnehmerliste in Python verwenden |
| 11 | Kurszahlen in Python verwenden |
| 12 | Zeitbezogene Existenzfrage in Python beantworten |
| 13–15 | Lernpaare, Mittelwert und CSV als Bonus |

## Vor dem Start

- Das SQL-Setup und die Übungsmodelle stehen vollständig in Aufgabe 1.
- Keine andere Übung und keine Lösung aus früheren Tagen wird benötigt.
- Voraussetzung für Python: tag3/db.py aus dem gemeinsamen Unterricht.

```powershell
.\.venv\Scripts\Activate.ps1
python -c "import sys; print(sys.executable)"
docker compose up -d --wait
New-Item -ItemType Directory -Force -Path .\tag4
New-Item -ItemType Directory -Force -Path .\sql\tag4\practice
docker compose exec db mysql --user=dumbledore --password hogwarts
```

- Das vorhandene Datenbankpasswort eingeben.
- SOURCE-Befehle im MySQL-Client eingeben.
- Eine zweite PowerShell für Python im Projektordner öffnen.
- Falls die Aktivierung blockiert ist, das venv-Python direkt nutzen.
- In allen Python-Befehlen dann diesen Pfad statt python verwenden.

```powershell
.\.venv\Scripts\python.exe --version
```

<a id="aufgabe-1"></a>

## 1. Den Übungsbestand vorbereiten

Die Verwaltung gibt euch einen vollständigen Bestand für eure Auswertungen.
Die Daten weichen absichtlich von den Daten des Vormittags ab.

### Aufgaben

1. Legt die beiden SQL-Dateien aus dem Startmaterial an.
2. Führt das Setup einmal aus, falls die practice4-Tabellen noch fehlen.
3. Führt die Kontrolldatei aus und vergleicht die Zeilenzahlen.
4. Übernehmt practice_models.py als fertiges Startmaterial.
5. Prüft, welche Buchungen zu Hermione gehören.
6. Prüft, welcher Schüler und welches Angebot keine Buchung besitzen.

- Das Setup nicht erneut importieren, wenn die Tabellen schon existieren.
- Bei Unterbrechung prüfen, welche Anweisungen erfolgreich waren.
- Ein SOURCE-Import kann nach einem SQL-Fehler weitere Anweisungen ausführen.
- Zum erneuten Nachsehen nur die Kontrolldatei verwenden.
- Keine Daten aus students, courses oder bookings kopieren.

### Startmaterial: SQL-Setup

<!-- file: sql/tag4/90_practice_setup.sql -->
- Lokal: `.\sql\tag4\90_practice_setup.sql`.

```sql
USE hogwarts;

CREATE TABLE practice4_students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    house VARCHAR(20) NULL,
    school_year TINYINT NOT NULL,
    CONSTRAINT ck_practice4_students_school_year
        CHECK (school_year BETWEEN 1 AND 7)
) ENGINE=InnoDB;

CREATE TABLE practice4_courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE practice4_bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    booking_date DATE NOT NULL,
    CONSTRAINT fk_practice4_booking_student
        FOREIGN KEY (student_id) REFERENCES practice4_students(id),
    CONSTRAINT fk_practice4_booking_course
        FOREIGN KEY (course_id) REFERENCES practice4_courses(id)
) ENGINE=InnoDB;

START TRANSACTION;
INSERT INTO practice4_students
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

INSERT INTO practice4_courses (id, title)
VALUES
    (1, 'Arithmantik'),
    (2, 'Wahrsagen'),
    (3, 'Alte Runen'),
    (4, 'Pflege magischer Geschöpfe'),
    (5, 'Zaubertrankpraxis');

INSERT INTO practice4_bookings
    (id, student_id, course_id, booking_date)
VALUES
    (1, 1, 2, '1993-09-01'),
    (2, 2, 1, '1993-09-01'),
    (3, 2, 3, '1993-09-01'),
    (4, 3, 2, '1993-09-02'),
    (5, 4, 4, '1993-09-02'),
    (6, 5, 3, '1993-09-01'),
    (7, 6, 4, '1993-09-03'),
    (8, 2, 1, '1993-09-04'),
    (9, 7, 1, '1993-09-05'),
    (10, 5, 3, '1993-09-02');
COMMIT;
```

```text
SOURCE /work/sql/tag4/90_practice_setup.sql;
```

### Startmaterial: Kontrolle

<!-- file: sql/tag4/91_practice_check.sql -->
- Lokal: `.\sql\tag4\91_practice_check.sql`.

```sql
USE hogwarts;

SELECT 'practice4_students' AS table_name, COUNT(*) AS row_count
FROM practice4_students
UNION ALL
SELECT 'practice4_courses', COUNT(*) FROM practice4_courses
UNION ALL
SELECT 'practice4_bookings', COUNT(*) FROM practice4_bookings;

SELECT id, first_name, last_name, house, school_year
FROM practice4_students ORDER BY id;
SELECT id, title FROM practice4_courses ORDER BY id;
SELECT id, student_id, course_id, booking_date
FROM practice4_bookings ORDER BY id;
```

```text
SOURCE /work/sql/tag4/91_practice_check.sql;
```

### Startmaterial: Übungsmodelle

<!-- file: tag4/practice_models.py -->
- Lokal: `.\tag4\practice_models.py`.

```python
from datetime import date

from sqlalchemy import CheckConstraint, Date, ForeignKey, String
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.orm import relationship


class Base(DeclarativeBase):
    pass


class Student(Base):
    __tablename__ = "practice4_students"
    __table_args__ = (
        CheckConstraint(
            "school_year BETWEEN 1 AND 7",
            name="ck_practice4_students_school_year",
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
    __tablename__ = "practice4_courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    bookings: Mapped[list["Booking"]] = relationship(
        back_populates="course"
    )


class Booking(Base):
    __tablename__ = "practice4_bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("practice4_students.id"))
    course_id: Mapped[int] = mapped_column(ForeignKey("practice4_courses.id"))
    booking_date: Mapped[date] = mapped_column(Date)
    student: Mapped[Student] = relationship(back_populates="bookings")
    course: Mapped[Course] = relationship(back_populates="bookings")
```

### Erfolgskriterien

- Acht Schüler, fünf Kurse und zehn Buchungen.
- Alex hat kein Haus und keine Buchung.
- Ginny ist für Arithmantik gebucht.
- Zaubertrankpraxis hat keine Buchung.
- Hermione hat drei Buchungszeilen, aber nur zwei verschiedene Kurse.
- Ihre zweite Arithmantik-Buchung ist ein absichtlicher Auswertungsfall.
- Luna hat zwei Buchungen für Alte Runen, aber nur einen verschiedenen Kurs.
- Dieser Prüffall muss sie in Aufgabe 7 aus der Ergebnisliste ausschließen.
- Eine spätere Datenregel könnte solche Doppelbuchungen verhindern.
- Heute wertet ihr den vorgegebenen Bestand aus, ohne Regeln zu ändern.

<a id="aufgabe-2"></a>

## 2. Eine Teilnehmerliste für Wahrsagen lesen

Die Verwaltung braucht Namen und Buchungsdaten für Wahrsagen.

### Aufgaben

1. Erstellt sql/tag4/practice/02_register.sql.
2. Gebt Schüler-ID, Vorname, Nachname, Kurstitel und Buchungsdatum aus.
3. Verbindet die dafür benötigten Tabellen mit passenden ON-Bedingungen.
4. Wählt den Kurs über seinen Titel aus, nicht über eine erratene neue ID.
5. Sortiert nach Schüler-ID und anschließend Buchungs-ID.
6. Führt die Datei aus und erklärt euren Join-Pfad.

### Erfolgskriterien

- Zwei Zeilen: Harry Potter und Ron Weasley.
- Harrys Buchung ist vom 1. September, Rons vom 2. September 1993.
- Der Titel lautet in beiden Zeilen Wahrsagen.
- Jede Ergebniszeile steht für eine passende Buchung.

```text
SOURCE /work/sql/tag4/practice/02_register.sql;
```

<a id="aufgabe-3"></a>

## 3. Gebuchte Kurse eines Hauses finden

Die Verwaltung möchte wissen, welche Kurse von Gryffindor gebucht wurden.
Ein Kurs soll nur einmal erscheinen, auch bei mehreren passenden Buchungen.

### Aufgaben

1. Erstellt sql/tag4/practice/03_house_courses.sql.
2. Plant selbst den benötigten Join-Pfad durch die drei Übungstabellen.
3. Gebt Kurs-ID und Titel für die verlangten Angebote aus.
4. Sortiert nach Kurs-ID.
5. Begründet, warum eine Person oder ein Kurs mehrfach vorkommen könnte.

### Erfolgskriterien

- Genau drei Zeilen: Arithmantik, Wahrsagen und Alte Runen.
- Die Kurs-IDs sind 1, 2 und 3.
- Mehrere Schüler desselben Hauses erzeugen keine doppelten Kurszeilen.
- Zaubertrankpraxis erscheint nicht.

```text
SOURCE /work/sql/tag4/practice/03_house_courses.sql;
```

<a id="aufgabe-4"></a>

## 4. Alle Angebote mit Buchungen ab dem 3. September zeigen

Die Verwaltung will die Buchungen seit dem 3. September sehen.
Ein Angebot soll auch dann erscheinen, wenn es in diesem Zeitraum leer ist.

### Aufgaben

1. Erstellt sql/tag4/practice/04_recent_courses.sql.
2. Gebt Kurs-ID, Titel, Buchungs-ID und Datum aus.
3. Berücksichtigt Buchungen ab einschließlich 3. September 1993.
4. Erhaltet dabei jedes der fünf Angebote.
5. Sortiert nach Kurs-ID und Buchungs-ID.
6. Begründet, an welcher Stelle eure Datumsbedingung stehen muss.

### Erfolgskriterien

- Sechs Ergebniszeilen mit allen fünf Kursen.
- Arithmantik erscheint mit Buchung 8 und 9.
- Pflege magischer Geschöpfe erscheint mit Cedrics Buchung 7.
- Wahrsagen, Alte Runen und Zaubertrankpraxis erscheinen mit NULL rechts.
- Ein rechter NULL-Wert bedeutet hier: kein passender Treffer im Zeitraum.

```text
SOURCE /work/sql/tag4/practice/04_recent_courses.sql;
```

<a id="aufgabe-5"></a>

## 5. Buchungen und verschiedene Personen zählen

Die Verwaltung vermutet eine doppelte Buchung.
Sie möchte Buchungszahlen und tatsächliche Personenzahlen vergleichen.

### Aufgaben

1. Erstellt sql/tag4/practice/05_course_counts.sql.
2. Berechnet zuerst die Buchungszahl und die Zahl verschiedener Schüler.
3. Erstellt danach dieselben beiden Kennzahlen je Angebot.
4. Gebt dabei Kurs-ID und Titel aus. Erhaltet auch leere Angebote.
5. Sortiert die Kursübersicht nach Kurs-ID.
6. Erklärt den Unterschied der beiden Zahlen bei Arithmantik.

### Erfolgskriterien

- Gesamtbestand: zehn Buchungen und sieben verschiedene gebuchte Schüler.
- Arithmantik und Alte Runen: je drei Buchungen und zwei verschiedene Schüler.
- Wahrsagen und Pflege magischer Geschöpfe: jeweils zweimal den Wert 2.
- Zaubertrankpraxis: zweimal den Wert 0.
- Der Schüler mit keiner Buchung gehört nicht zur Zahl gebuchter Personen.

```text
SOURCE /work/sql/tag4/practice/05_course_counts.sql;
```

<a id="aufgabe-6"></a>

## 6. Schüler und Buchungen pro Haus vergleichen

Die Verwaltung braucht eine Übersicht nach Häusern.
Auch Schüler ohne Buchung und ohne bekanntes Haus sollen berücksichtigt werden.

### Aufgaben

1. Erstellt sql/tag4/practice/06_house_summary.sql.
2. Gebt für jedes Haus die Schülerzahl und die Buchungszahl aus.
3. Zählt jeden Schüler für sein Haus genau einmal.
4. Berücksichtigt zugleich alle Buchungszeilen.
5. Erhaltet die Gruppe für das unbekannte Haus.
6. Sortiert nach house und begründet eure Zählweise.

### Erfolgskriterien

| Haus | Schüler | Buchungen |
| --- | ---: | ---: |
| NULL | 1 | 0 |
| Gryffindor | 4 | 6 |
| Hufflepuff | 1 | 1 |
| Ravenclaw | 1 | 2 |
| Slytherin | 1 | 1 |

- Hermione wird als Schülerin einmal gezählt und mit drei Buchungen erfasst.
- Die Schülerzahlen ergeben acht; die Buchungszahlen ergeben zehn.
- Keine Person wird durch den Join aus ihrer Gruppe entfernt.

```text
SOURCE /work/sql/tag4/practice/06_house_summary.sql;
```

<a id="aufgabe-7"></a>

## 7. Schüler mit mindestens zwei verschiedenen Kursen finden

Die Verwaltung möchte Schüler mit mehreren unterschiedlichen Kursen sehen.
Mehrere Buchungen für denselben Kurs dürfen die Grenze nicht erfüllen.

### Aufgaben

1. Erstellt sql/tag4/practice/07_multiple_courses.sql.
2. Gebt Schüler-ID, Vorname, Nachname und Anzahl verschiedener Kurse aus.
3. Berücksichtigt nur Schüler mit mindestens zwei verschiedenen Kursen.
4. Sortiert nach Schüler-ID.
5. Begründet, warum der Filter nicht auf einzelnen Buchungszeilen wirkt.

### Erfolgskriterien

- Eine Zeile: Hermione Granger mit ID 2 und dem Wert 2.
- Ihre drei Buchungszeilen ergeben nur zwei verschiedene Kurse.
- Luna erscheint trotz zweier Buchungszeilen nicht: Sie hat nur einen Kurs.
- Ein Gruppenfilter auf die reine Buchungszahl wäre deshalb falsch.
- Die Auswertung verändert keine doppelte Buchung.

```text
SOURCE /work/sql/tag4/practice/07_multiple_courses.sql;
```

<a id="aufgabe-8"></a>

## 8. Kursteilnahme mit einer Unterabfrage auswählen

Die Verwaltung möchte alle Schüler finden, die Alte Runen gebucht haben.
Den Kurstitel kennt sie; eine feste Kurs-ID soll nicht vorausgesetzt werden.

### Aufgaben

1. Erstellt sql/tag4/practice/08_course_subquery.sql.
2. Wählt IDs und Namen in der äußeren Abfrage aus practice4_students.
3. Nutzt eine unabhängige Unterabfrage als Kriterienbestand für IN.
4. Die Unterabfrage darf bookings und courses über einen Join verbinden.
5. Filtert dort nach dem Titel Alte Runen.
6. Sortiert die endgültige Liste nach Schüler-ID.

### Erfolgskriterien

- Hermione Granger mit ID 2 und Luna Lovegood mit ID 5.
- Kein Schüler erscheint mehrfach.
- Der Titel ist das Kriterium. Die Zahl 3 steht nicht als Kursfilter im Code.

```text
SOURCE /work/sql/tag4/practice/08_course_subquery.sql;
```

### Optionale 

- Erstellt zusätzlich sql/tag4/practice/08_course_exists.sql.
- Beantwortet denselben Auftrag mit einer korrelierten EXISTS-Unterabfrage.
- Vergleicht beide Ergebnisse und erklärt den Bezug zur äußeren Schüler-ID.

```text
SOURCE /work/sql/tag4/practice/08_course_exists.sql;
```

<a id="aufgabe-9"></a>

## 9. Vertiefung: Schüler ohne Buchung seit dem 3. September ermitteln

Diese Aufgabe ist freiwillig und bereitet Aufgabe 12 vor.
Voraussetzung ist die Erklärung zu NOT EXISTS aus Abschnitt 6.2.

Die Verwaltung will bei Schülern ohne Buchung seit dem 3. September nachfragen.
Frühere Buchungen dürfen vorhanden sein. Gesucht ist ihr Fehlen im Zeitraum.

### Aufgaben

1. Erstellt sql/tag4/practice/09_no_recent_booking.sql.
2. Gebt IDs und Namen der betroffenen Schüler aus.
3. Verwendet eine korrelierte Unterabfrage für die fehlenden Treffer.
4. Berücksichtigt als Zeitraum den 3. September 1993 und alle späteren Tage.
5. Sortiert nach Schüler-ID.
6. Plant den Ablauf selbst und erklärt, was „keine Buchung“ hier bedeutet.

### Erfolgskriterien

- Die IDs 1, 3, 4, 5 und 8 erscheinen.
- Harry, Ron, Draco und Luna haben nur frühere Buchungen.
- Alex erscheint ebenfalls, obwohl er überhaupt keine Buchung hat.
- Hermione, Cedric und Ginny erscheinen nicht.
- Eine ältere Buchung allein entfernt einen Schüler nicht aus dieser Liste.

```text
SOURCE /work/sql/tag4/practice/09_no_recent_booking.sql;
```

<a id="aufgabe-10"></a>

## 10. Eine Teilnehmerliste in Python verwenden

Die Verwaltung benötigt die Teilnehmer von Pflege magischer Geschöpfe in Python.

### Aufgaben

1. Erstellt tag4/practice_register.py.
2. Verwendet SessionLocal aus tag3.db und Modelle aus tag4.practice_models.
3. Schreibt course_register(course_id), die eine Liste von Dictionaries liefert.
4. Verwendet einen expliziten Join über die Beziehung Booking.student.
5. Liefert Schüler-ID, Vorname, Nachname und Buchungsdatum.
6. Sortiert nach Schüler-ID und Buchungs-ID.
7. Lest alle Daten innerhalb der Session aus.
8. Ruft die Funktion mit Kurs 4 und mit Kurs 999 auf.

### Erfolgskriterien

- Kurs 4 liefert Draco Malfoy und Cedric Diggory.
- Ihre Daten sind der 2. und 3. September 1993.
- Die Dictionary-Schlüssel sind student_id, first_name, last_name,
  booking_date.
- Kurs 999 liefert eine leere Liste ohne Ausnahme.
- Es werden keine ORM-Objekte zum späteren Nachladen zurückgegeben.

```powershell
python -m tag4.practice_register
```

<a id="aufgabe-11"></a>

## 11. Die beiden Kurszahlen in Python verwenden

Die Verwaltung benötigt die Übersicht aus Aufgabe 5 für ein Python-Programm.

### Aufgaben

1. Erstellt tag4/practice_summary.py.
2. Schreibt course_summary, die eine Liste von Dictionaries liefert.
3. Nutzt die vorhandenen Course- und Booking-Modelle der Übungen.
4. Berechnet beide Kennzahlen in MySQL mit einer ORM-Abfrage.
5. Erhaltet alle fünf Kurse, auch Zaubertrankpraxis.
6. Sortiert nach Kurs-ID und gebt alle vier Werte pro Zeile aus.
7. Vergleicht die Werte mit eurer SQL-Auswertung aus Aufgabe 5.

### Erfolgskriterien

- Die Schlüssel sind course_id, title, booking_count und student_count.
- Arithmantik und Alte Runen liefern jeweils die Werte 3 und 2.
- Wahrsagen und Pflege magischer Geschöpfe liefern jeweils 2 und 2.
- Zaubertrankpraxis liefert 0 und 0.
- Keine Python-Schleife lädt pro Kurs seine Buchungen zum Zählen nach.

```powershell
python -m tag4.practice_summary
```

<a id="aufgabe-12"></a>

## 12. Vertiefung: Die zeitbezogene Existenzfrage in Python beantworten

Diese Aufgabe ist freiwillig und setzt Aufgabe 9 voraus.
Voraussetzung ist die ORM-Erklärung aus Abschnitt 8.4.

Die Verwaltung möchte die Nachfrageliste aus Aufgabe 9 wiederverwenden.
Das Startdatum soll ein Parameter der Python-Funktion werden.

### Aufgaben

1. Erstellt tag4/practice_missing.py.
2. Schreibt students_without_recent_bookings(from_date).
3. Übergebt ein datetime.date als Startdatum.
4. Verwendet die Beziehung Student.bookings für eine Existenzbedingung.
5. Gebt ID, Vorname und Nachname als Liste von Dictionaries zurück.
6. Sortiert nach Schüler-ID.
7. Testet zuerst den 3. September 1993.
8. Testet zusätzlich den 6. September 1993.
9. Erklärt den Unterschied zur allgemeinen Frage nach ganz fehlenden Buchungen.

### Erfolgskriterien

- Ab 3. September: IDs 1, 3, 4, 5 und 8.
- Ab 6. September: alle acht Schüler.
- Die Funktion bezieht das Datum in die Existenzprüfung ein.
- SQL und ORM liefern für denselben Zeitraum dieselben Schüler.
- Kein bereits geladenes Buchungsobjekt wird in Python durchgesucht.

```powershell
python -m tag4.practice_missing
```

## Bonusaufgaben

Die folgenden Aufgaben sind freiwillig. Bearbeitet zuerst den Pflichtteil.
Für Aufgabe 15 benötigt ihr die Datei aus Aufgabe 11.

<a id="aufgabe-13"></a>

## 13. Mögliche Lernpaare im selben Haus auflisten

Die Verwaltung sucht Paare von Schülern desselben bekannten Hauses.
Jedes Paar soll genau einmal erscheinen.
Niemand bildet ein Paar mit sich selbst.

### Aufgaben

1. Erstellt sql/tag4/practice/13_house_pairs.sql.
2. Nutzt die Schülertabelle zweimal mit verschiedenen Aliasen.
3. Gebt die beiden Schüler-IDs, Vornamen und das gemeinsame Haus aus.
4. Vermeidet Selbstpaare und umgekehrte Duplikate.
5. Sortiert nach der ersten und dann der zweiten ID.

### Erfolgskriterien

- Genau sechs Paare aus Harry, Hermione, Ron und Ginny.
- ID-Paare: 1/2, 1/3, 1/7, 2/3, 2/7 und 3/7.
- Das Paar 2/1 erscheint nicht zusätzlich zu 1/2.
- Ein unbekanntes Haus gilt nicht als bekanntes gemeinsames Haus.

```text
SOURCE /work/sql/tag4/practice/13_house_pairs.sql;
```

<a id="aufgabe-14"></a>

## 14. Schüler über dem mittleren Schuljahr finden

Die Verwaltung möchte die Schüler oberhalb des mittleren Schuljahrs sehen.
Ein vorher von Hand berechneter Grenzwert soll nicht im Code stehen.

### Aufgaben

1. Erstellt sql/tag4/practice/14_average_year.sql.
2. Berechnet den Mittelwert in einer skalaren Unterabfrage.
3. Wählt Schüler mit einem höheren school_year aus.
4. Gebt ID, Vorname, Nachname und Schuljahr aus.
5. Sortiert nach Schüler-ID.

### Erfolgskriterien

- Die IDs 1, 2, 3, 4 und 6 erscheinen.
- Der innere Mittelwert ist 2,75.
- Der Vergleich verwendet die Unterabfrage und keinen fest eingetragenen Wert.

```text
SOURCE /work/sql/tag4/practice/14_average_year.sql;
```

<a id="aufgabe-15"></a>

## 15. Die Kursübersicht als CSV speichern

Die Verwaltung möchte die Kursübersicht in einer Tabellenkalkulation öffnen.

### Aufgaben

1. Erstellt tag4/practice_csv.py.
2. Verwendet eure fertige Funktion course_summary aus Aufgabe 11.
3. Schreibt exports/course_summary.csv im Unterrichtsprojekt.
4. Verwendet die Schlüssel der Dictionaries als Kopfzeile.
5. Verwendet UTF-8 mit BOM (`encoding="utf-8-sig"`), damit Excel die Umlaute richtig anzeigt, und das Semikolon als Trennzeichen.
6. Prüft Kopfzeile, fünf Datenzeilen und die Werte des leeren Angebots.

### Erfolgskriterien

- Keine zusätzliche ORM-Abfrage nur für den Export.
- Spalten: course_id, title, booking_count und student_count.
- Umlaute sind lesbar. Zwischen den Zeilen entstehen keine Leerzeilen.
- Zaubertrankpraxis hat in den beiden Zahlenspalten den Wert 0.
- Ein erneuter Start ersetzt nur die von euch erzeugte Exportdatei.

```powershell
python -m tag4.practice_csv
```

## Abschlusskontrolle

- Führt die Kontrolldatei aus Aufgabe 1 erneut aus.

```text
SOURCE /work/sql/tag4/91_practice_check.sql;
```

- Acht Schüler, fünf Kurse und zehn Buchungen.
- Alle ursprünglich gegebenen Werte und Buchungen sind unverändert.
- Die Tabellen ohne practice4-Präfix wurden nicht verwendet.

