SELECT id, first_name, last_name, school_year 
FROM students
ORDER BY school_year DESC, id ASC;



SELECT id, first_name, house
FROM students
WHERE house = 'Gryffindor'
ORDER BY id;