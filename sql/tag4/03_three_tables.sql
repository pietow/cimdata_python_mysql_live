-- Teilnehmer, die in Arithmantik eingeschrieben sind

SELECT *
FROM bookings AS b
INNER JOIN students AS s ON s.id = b.student_id
INNER JOIN courses AS c ON c.id = b.course_id
WHERE c.id = 1
ORDER BY s.id, b.id;
