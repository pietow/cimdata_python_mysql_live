CREATE TABLE bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id int NOT NULL,
    course_id int NOT NULL,
    booking_date DATE NOT NULL,
    CONSTRAINT fk_bookings_student
        FOREIGN KEY (student_id) REFERENCES students(id),
    CONSTRAINT fk_bookings_course
        FOREIGN KEY (course_id) REFERENCES courses(id)
)