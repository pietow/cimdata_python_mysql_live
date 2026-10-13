START TRANSACTION;

UPDATE students SET school_year = 4 WHERE id = 1;

SELECT id, first_name, school_year FROM students WHERE id = 1;

ROLLBACK;

SELECT id, first_name, school_year FROM students WHERE id = 1;
