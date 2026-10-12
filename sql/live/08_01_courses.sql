USE hogwarts;

CREATE TABLE courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) NOT NULL
);

DESCRIBE courses;

INSERT INTO courses (id, title)
VALUES
    (1, 'Arithmantik'),
    (2, 'Wahrsagen'),
    (3, 'Alte Runen'),
    (4, 'Pflege magischer Geschöpfe');

SELECT id, title FROM courses ORDER BY title;
