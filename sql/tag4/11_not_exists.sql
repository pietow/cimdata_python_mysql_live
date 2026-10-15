SELECT *
FROM students AS s
WHERE NOT EXISTS (
    SELECT 1 FROM bookings AS b WHERE b.student_id = s.id
)
ORDER BY s.id;