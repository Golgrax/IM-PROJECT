-- DI KO ALAM QUERY NIYO SO THIS IS JUST A SAMPLE AND ILL SHOW SOME INSTRUCTIONS HOW TO IMPORT THIS or just type nalang in query then execute kasi pwede naman



CREATE DATABASE IF NOT EXISTS projector_reservation_db;

USE projector_reservation_db;

CREATE TABLE IF NOT EXISTS students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS projectors (
    projector_id INT AUTO_INCREMENT PRIMARY KEY,
    projector_name VARCHAR(255) NOT NULL,
    model VARCHAR(255),
    status ENUM('Available', 'Reserved', 'Under Maintenance') DEFAULT 'Available'
);

CREATE TABLE IF NOT EXISTS reservations (
    reservation_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    projector_id INT NOT NULL,
    professor_name VARCHAR(255) NOT NULL,
    date_reserved DATE NOT NULL,
    time_start TIME NOT NULL,
    time_end TIME NOT NULL,
    purpose TEXT,
    status ENUM('Pending', 'Approved', 'Rejected', 'Cancelled') DEFAULT 'Pending',
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (projector_id) REFERENCES projectors(projector_id) ON DELETE CASCADE
);


INSERT INTO students (name, password) VALUES
('Lennon', 'studentpass'),
('Bughaw', 'johnpass');

INSERT INTO projectors (projector_name, model, status) VALUES
('Epson PowerLite 1', 'EB-X05', 'Available'),
('BenQ MX-2', 'MX507', 'Available'),
('Optoma DLP 3', 'HD146X', 'Reserved'),
('Panasonic PT-RZ', 'PT-RZ570', 'Available');

INSERT INTO reservations (student_id, projector_id, professor_name, date_reserved, time_start, time_end, purpose, status) VALUES
((SELECT student_id FROM students WHERE name = 'Lennon'), (SELECT projector_id FROM projectors WHERE projector_name = 'Optoma DLP 3'), 'Prof. Alinghi', '2024-05-15', '09:00:00', '11:00:00', 'Class presentation', 'Approved');

INSERT INTO reservations (student_id, projector_id, professor_name, date_reserved, time_start, time_end, purpose, status) VALUES
((SELECT student_id FROM students WHERE name = 'Bughaw'), (SELECT projector_id FROM projectors WHERE projector_name = 'Epson PowerLite 1'), 'Dr. Lim', '2024-05-16', '14:00:00', '16:00:00', 'Research Meeting', 'Pending');