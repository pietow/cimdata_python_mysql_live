SELECT c.id AS course_id, c.title, COUNT(b.id) AS booking_count
FROM courses AS c
LEFT JOIN bookings AS b ON b.course_id = c.id
GROUP BY c.id, c.title
ORDER BY c.id;