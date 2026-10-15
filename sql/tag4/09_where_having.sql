SELECT course_id, COUNT(*) AS booking_count
FROM bookings
WHERE booking_date < '1993-09-03'
GROUP BY course_id
HAVING COUNT(*) >= 2
ORDER BY course_id;