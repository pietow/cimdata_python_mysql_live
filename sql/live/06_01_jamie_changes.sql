INSERT INTO students (id, first_name, last_name, house, school_year)
VALUES (90, 'Jamie', 'Taylr', Null, 1);

SELECT id, first_name, last_name FROM students WHERE id = 90;


UPDATE students
SET last_name = 'Taylor'
WHERE id = 90;

SELECT id, first_name, last_name FROM students WHERE id = 90;

DELETE FROM students WHERE id = 90;