SET @viewer_id = (SELECT id FROM users WHERE username = 'vector');


EXPLAIN ANALYZE
SELECT b.id, s.first_name, s.last_name, c.title, b.booking_date
FROM bookings as b
JOIN course_managers AS cm ON cm.course_id = b.course_id
JOIN students AS s ON b.student_id = s.id
JOIN courses AS c ON c.id = b.course_id
WHERE cm.user_id = @viewer_id
    AND b.booking_date = '1993-09-01'
ORDER BY b.id
LIMIT 20;
