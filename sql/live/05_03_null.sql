SELECT id, first_name, house
FROM students
WHERE house IS NULL;

SELECT id, first_name, house
FROM students
WHERE house <> 'Gryffindor';

SELECT id, first_name, house
FROM students
WHERE house <> 'Gryffindor' OR house IS NULL;