SELECT *
FROM courses AS c
LEFT JOIN bookings AS b
    ON b.course_id = c.id AND b.booking_date >= '1993-09-03'
ORDER BY c.id, b.id