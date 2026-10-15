-- Buchungen mit Schülernamen ausgeben

-- SELECT b.id , s.first_name, b.course_id  
SELECT *
FROM bookings AS b
INNER JOIN students AS s ON s.id = b.student_id
ORDER BY b.id;
