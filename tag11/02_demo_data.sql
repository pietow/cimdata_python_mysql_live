-- Tag 11: bereitgestellter Datenaufbau für den SQL-Planvergleich.
-- Als fertiges Werkzeug ausführen; sein Nachbau ist kein Lernziel.
-- Nur perf_bookings in dieser MySQL-Verbindung wird neu aufgebaut.
-- Eine Wiederholung entfernt auch zuvor angelegte Demo-Indizes.
DROP TEMPORARY TABLE IF EXISTS perf_bookings;

CREATE TEMPORARY TABLE perf_bookings (
    id INT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    booking_date DATE NOT NULL
) ENGINE=InnoDB;

-- Technischer Anhang für Interessierte:
-- digits liefert die Ziffern 0 bis 9; vier Kombinationen ergeben 10.000 IDs.
-- MOD und FLOOR verteilen künstliche Schülernummern, Kurse und Datum.
-- Die Nummern beziehen sich nicht auf echte students- oder courses-Zeilen.
INSERT INTO perf_bookings (id, student_id, course_id, booking_date)
WITH digits AS (
    SELECT 0 AS n UNION ALL SELECT 1 UNION ALL SELECT 2
    UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5
    UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8
    UNION ALL SELECT 9
), numbers AS (
    SELECT 1 + a.n + 10 * b.n + 100 * c.n + 1000 * d.n AS n
    FROM digits AS a CROSS JOIN digits AS b
    CROSS JOIN digits AS c CROSS JOIN digits AS d
)
SELECT n, 1 + MOD(n, 500), 1 + MOD(FLOOR(n / 365), 5),
       DATE_ADD('1993-01-01', INTERVAL MOD(n, 365) DAY)
FROM numbers;
