-- Kurse mit mindestens 2 verschiedenen Schülern finden;
-- Kurs-id, title, anzahlt der schüler
-- sortier nach Kurs-ID

SELECT c.id as course_id, c.title,
    COUNT(DISTINCT b.student_id) AS student_count
FROM courses AS c
LEFT JOIN bookings AS b  ON b.course_id = c.id
GROUP BY c.id, c.title
HAVING COUNT(DISTINCT b.student_id) >= 2
ORDER BY c.id