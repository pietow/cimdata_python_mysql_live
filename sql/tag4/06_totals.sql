SELECT COUNT(*) AS booking_count,
        COUNT(DISTINCT student_id) AS student_count,
        MIN(booking_date) as first_booking,
        MAX(booking_date) as last_booking
FROM bookings;
        
SELECT COUNT(*) AS student_count, COUNT(house), AVG(school_year) FROM students