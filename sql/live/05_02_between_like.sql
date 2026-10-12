SELECT id, first_name, school_year
FROM students
WHERE school_year BETWEEN 1 AND 3;

SELECT id, first_name, last_name, school_year
FROM students
WHERE last_name LIKE '%Love%';