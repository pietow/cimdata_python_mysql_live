SELECT student_id FROM bookings WHERE course_id = 3 ORDER BY student_id;

SELECT id, first_name
FROM students
WHERE id IN (
    SELECT student_id FROM bookings WHERE course_id = 3
)
ORDER BY id;
