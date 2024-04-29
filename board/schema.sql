DROP TABLE IF EXISTS post;
DROP TABLE IF EXISTS student;
DROP TABLE IF EXISTS class;
DROP TABLE IF EXISTS employee;
DROP TABLE IF EXISTS teaches;

CREATE TABLE student (
	student_id INTEGER PRIMARY KEY,
    student_name TEXT NOT NULL,
    email TEXT NOT NULL,
    student_year TEXT NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE post (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  student_id INT,
  task TEXT NOT NULL,
  time_spent FLOAT,
  class_name TEXT NOT NULL,
  group_num INT,
  FOREIGN KEY (student_id) REFERENCES student(student_id) ON DELETE CASCADE
);

CREATE TABLE class (
	class_id TEXT PRIMARY KEY, 
    class_name TEXT NOT NULL
);

CREATE TABLE employee (
	employee_id INTEGER PRIMARY KEY,
    employee_name TEXT NOT NULL,
    email TEXT NOT NULL,
    office TEXT NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE teaches (
	class_fid TEXT KEY,
    employee_fid INTEGER KEY,
    FOREIGN KEY (employee_fid) REFERENCES employee(employee_id) ON DELETE CASCADE,
    FOREIGN KEY (class_fid) REFERENCES class(class_id) ON DELETE CASCADE
);

CREATE INDEX id_index ON post(id);
CREATE INDEX sid_index ON student(student_id);