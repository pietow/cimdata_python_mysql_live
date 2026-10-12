INSERT INTO bookings (id, student_id, course_id, booking_date)
VALUES (1, 1, 2, '1993-09-01');

SELECT * FROM bookings ORDER BY id;

INSERT INTO bookings (id, student_id, course_id, booking_date)
VALUES
    (2, 2, 1, '1993-09-01'),
    (3, 2, 3, '1993-09-01');

SELECT * FROM bookings WHERE student_id = 2 ORDER BY id;

INSERT INTO bookings (id, student_id, course_id, booking_date)
VALUES
    (4, 3, 2, '1993-09-02'),
    (5, 4, 4, '1993-09-02'),
    (6, 5, 3, '1993-09-01'),
    (7, 6, 4, '1993-09-03');

SELECT * FROM bookings ORDER BY id;
