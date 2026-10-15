SELECT c.id AS course_id, c.title, COUNT(b.id) AS booking_count
FROM courses AS c
LEFT JOIN bookings AS b ON b.course_id = c.id
-- WHERE booking_date < '1993-09-03'
GROUP BY c.id, c.title
HAVING COUNT(b.id) >= 3
ORDER BY c.id;