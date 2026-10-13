SELECT id, student_id, course_id, booking_date
FROM bookings
WHERE course_id IN (1, 3)
ORDER BY student_id;