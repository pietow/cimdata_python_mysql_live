INSERT INTO courses (title) VALUES ('Zaubertrankpraxis');
SET @new_course_id = LAST_INSERT_ID();
SELECT id, title FROM courses WHERE id = @new_course_id;