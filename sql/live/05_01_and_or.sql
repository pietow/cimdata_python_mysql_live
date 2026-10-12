SELECT id, first_name, school_year FROM students
WHERE house = 'Gryffindor' AND school_year = 3;


SELECT id, first_name, school_year 
FROM students
WHERE last_name = 'Weasley' OR last_name = 'Granger';

SELECT id, first_name, school_year 
FROM students
WHERE (house = 'Gryffindor' OR house = 'Ravenclaw') AND school_year = 2
