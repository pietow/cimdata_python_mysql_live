INSERT INTO students (id, first_name, last_name, house, school_year)
VALUES (2, 'Hermione', 'Granger', 'Gryffindor', 3);

SELECT * FROM students ORDER BY id;

INSERT INTO students (id, first_name, last_name, house, school_year)
VALUES
    (3, 'Ron', 'Weasley', 'Gryffindor', 3),
    (4, 'Draco', 'Malfoy', 'Slytherin', 3),
    (5, 'Luna', 'Lovegood', 'Ravenclaw', 2),
    (6, 'Cedric', 'Diggory', 'Hufflepuff', 5),
    (7, 'Ginny', 'Weasley', 'Gryffindor', 2),
    (8, 'Alex', 'Morgan', NULL, 1);

SELECT * FROM students ORDER BY id;
