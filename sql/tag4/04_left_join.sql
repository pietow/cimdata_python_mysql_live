SELECT * 
FROM courses AS c
LEFT JOIN bookings AS b ON b.course_id = c.id
ORDER BY c.id, b.id;