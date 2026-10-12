INSERT INTO students (id, first_name, last_name, house, school_year)
VALUES (1, 'Test', 'Person', NULL, 1);   -- id bereits verwendet un muss einmalig sein

UPDATE students SET first_name = NULL WHERE id = 1;

UPDATE students SET school_year = 0 WHERE id = 1;
