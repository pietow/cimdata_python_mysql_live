SELECT id, title FROM courses ORDER BY id;
SELECT id, username, role FROM users ORDER BY id;

SELECT c.id, c.title, u.username FROM courses AS c
LEFT JOIN course_managers AS cm ON cm.course_id = c.id
LEFT JOIN users AS u ON u.id = cm.user_id
ORDER BY c.id