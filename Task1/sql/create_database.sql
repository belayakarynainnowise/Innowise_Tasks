DROP DATABASE IF EXISTS students_rooms;
CREATE DATABASE students_rooms;
USE students_rooms;
DROP TABLE IF EXISTS rooms;
CREATE TABLE rooms(room_id INT PRIMARY KEY NOT NULL, room_name VARCHAR(20));
DROP TABLE IF EXISTS students;
CREATE TABLE students(student_id INT PRIMARY KEY NOT NULL, student_name VARCHAR(50), birthday DATETIME, sex CHAR, room_id INT, 
FOREIGN KEY (room_id) REFERENCES rooms(room_id));
CREATE INDEX students_sex_idx on students(sex);