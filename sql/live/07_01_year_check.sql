ALTER TABLE students
ADD CONSTRAINT ck_students_school_year
CHECK (school_year BETWEEN 1 AND 7);

SHOW CREATE TABLE students;