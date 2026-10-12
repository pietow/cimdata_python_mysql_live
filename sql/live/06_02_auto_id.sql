INSERT INTO students (first_name, last_name, house, school_year)
VALUES ('Robin', 'Taylor', NULL, 1);

SET @robin_id = LAST_INSERT_ID();

SELECT @robin_id;

SELECT id, first_name, school_year
FROM students
WHERE id = @robin_id;

UPDATE students SET school_year = 2 WHERE id = @robin_id;

SELECT id, first_name, school_year
FROM students
WHERE id = @robin_id;

DELETE FROM students WHERE id = @robin_id;

SELECT id, first_name, school_year
FROM students
WHERE id = @robin_id;