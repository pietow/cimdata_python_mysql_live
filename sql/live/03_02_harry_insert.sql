INSERT INTO students (id, first_name, last_name, house, school_year)
VALUES (1, 'Harry', 'Potter', 'Gryffindor', 3)

SELECT * FROM students;

SELECT first_name, last_name
FROM students
WHERE id = 1;