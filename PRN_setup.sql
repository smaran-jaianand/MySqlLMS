-- Student Performance Analyzer (SPA) Enhanced Database Schema
-- File: PRN_setup.sql

CREATE DATABASE IF NOT EXISTS spa_enhanced_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE spa_enhanced_db;

-- 1. Users Table (Mainly for Admins)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE COLLATE utf8mb4_unicode_ci,
    password_hash CHAR(64) NOT NULL,
    role ENUM('admin', 'faculty', 'student') NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (CHAR_LENGTH(username) >= 3),
    CHECK (CHAR_LENGTH(password_hash) = 64)
) ENGINE=InnoDB;

-- 2. Students Table
CREATE TABLE IF NOT EXISTS students (
    prn CHAR(11) PRIMARY KEY,
    password_hash CHAR(64) NOT NULL,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(60) NOT NULL COLLATE utf8mb4_unicode_ci,
    marks DECIMAL(5,2) NOT NULL DEFAULT 0.00,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    enrolled_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (marks >= 0 AND marks <= 100),
    CHECK (prn REGEXP '^(25|26|27)0(06|07)(01|02|03|04|05|06)[123][0-9]{3}$'),
    CHECK (CHAR_LENGTH(password_hash) = 64)
) ENGINE=InnoDB;

-- 3. Faculty Table
CREATE TABLE IF NOT EXISTS faculty (
    prn CHAR(11) PRIMARY KEY,
    password_hash CHAR(64) NOT NULL,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(60) NOT NULL COLLATE utf8mb4_unicode_ci,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (prn REGEXP '^(25|26|27)0(06|07)(01|02|03|04|05|06)[123][0-9]{3}$'),
    CHECK (CHAR_LENGTH(password_hash) = 64)
) ENGINE=InnoDB;

-- 4. Audit Log Table
CREATE TABLE IF NOT EXISTS audit_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NULL,
    action VARCHAR(60) NOT NULL,
    details VARCHAR(1000) NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_audit_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON UPDATE CASCADE
        ON DELETE SET NULL
) ENGINE=InnoDB;

-- 5. Subjects Table
CREATE TABLE IF NOT EXISTS subjects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(20) NOT NULL,
    name VARCHAR(100) NOT NULL,
    batch VARCHAR(50) NOT NULL,
    UNIQUE(code, batch)
) ENGINE=InnoDB;

-- 6. Student Subjects Junction (Enrollment + Marks)
CREATE TABLE IF NOT EXISTS student_subjects (
    subject_id INT NOT NULL,
    student_prn CHAR(11) NOT NULL,
    marks DECIMAL(5,2) DEFAULT NULL,
    PRIMARY KEY (subject_id, student_prn),
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    FOREIGN KEY (student_prn) REFERENCES students(prn) ON UPDATE CASCADE ON DELETE CASCADE,
    CHECK (marks IS NULL OR (marks >= 0 AND marks <= 100))
) ENGINE=InnoDB;

-- 7. Faculty Subjects Junction (Assignments)
CREATE TABLE IF NOT EXISTS faculty_subjects (
    faculty_prn CHAR(11) NOT NULL,
    subject_id INT NOT NULL,
    PRIMARY KEY (faculty_prn, subject_id),
    FOREIGN KEY (faculty_prn) REFERENCES faculty(prn) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 8. Attendance Table
CREATE TABLE IF NOT EXISTS attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    subject_id INT NOT NULL,
    student_prn CHAR(11) NOT NULL,
    date DATE NOT NULL,
    status ENUM('Present', 'Absent') NOT NULL,
    UNIQUE(subject_id, student_prn, date),
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    FOREIGN KEY (student_prn) REFERENCES students(prn) ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

-- 9. Database Views
CREATE OR REPLACE VIEW vw_student_grades AS
SELECT 
    prn,
    name,
    department,
    marks,
    CASE 
        WHEN marks >= 90 THEN 'A'
        WHEN marks >= 75 THEN 'B'
        WHEN marks >= 60 THEN 'C'
        WHEN marks >= 40 THEN 'D'
        ELSE 'F'
    END AS grade
FROM students;

CREATE OR REPLACE VIEW vw_department_leaderboard AS
SELECT 
    department,
    COUNT(*) AS total_students,
    ROUND(AVG(marks), 2) AS average_marks,
    MAX(marks) AS highest_marks,
    MIN(marks) AS lowest_marks
FROM students
GROUP BY department;

-- 10. Sample Insertion Data (Default Admin password is admin123 hash)
INSERT INTO users (username, password_hash, role) 
VALUES ('admin', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'admin')
ON DUPLICATE KEY UPDATE id=id;

-- 11. Application Roles and Privileges Setup
CREATE USER IF NOT EXISTS 'spa_admin'@'localhost' IDENTIFIED BY 'spa_admin123';
GRANT SELECT, INSERT, UPDATE, DELETE ON spa_enhanced_db.students TO 'spa_admin'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON spa_enhanced_db.faculty TO 'spa_admin'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON spa_enhanced_db.users TO 'spa_admin'@'localhost';
GRANT SELECT, INSERT ON spa_enhanced_db.audit_log TO 'spa_admin'@'localhost';
GRANT SELECT ON spa_enhanced_db.vw_student_grades TO 'spa_admin'@'localhost';
GRANT SELECT ON spa_enhanced_db.vw_department_leaderboard TO 'spa_admin'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON spa_enhanced_db.subjects TO 'spa_admin'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON spa_enhanced_db.student_subjects TO 'spa_admin'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON spa_enhanced_db.faculty_subjects TO 'spa_admin'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON spa_enhanced_db.attendance TO 'spa_admin'@'localhost';

CREATE USER IF NOT EXISTS 'spa_faculty'@'localhost' IDENTIFIED BY 'spa_faculty123';
GRANT SELECT, INSERT, UPDATE ON spa_enhanced_db.students TO 'spa_faculty'@'localhost';
GRANT SELECT ON spa_enhanced_db.faculty TO 'spa_faculty'@'localhost';
GRANT SELECT ON spa_enhanced_db.vw_student_grades TO 'spa_faculty'@'localhost';
GRANT SELECT ON spa_enhanced_db.vw_department_leaderboard TO 'spa_faculty'@'localhost';
GRANT INSERT ON spa_enhanced_db.audit_log TO 'spa_faculty'@'localhost';
GRANT SELECT ON spa_enhanced_db.subjects TO 'spa_faculty'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON spa_enhanced_db.student_subjects TO 'spa_faculty'@'localhost';
GRANT SELECT ON spa_enhanced_db.faculty_subjects TO 'spa_faculty'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON spa_enhanced_db.attendance TO 'spa_faculty'@'localhost';

CREATE USER IF NOT EXISTS 'spa_student'@'localhost' IDENTIFIED BY 'spa_student123';
GRANT SELECT ON spa_enhanced_db.students TO 'spa_student'@'localhost';
GRANT SELECT ON spa_enhanced_db.vw_student_grades TO 'spa_student'@'localhost';
GRANT SELECT ON spa_enhanced_db.vw_department_leaderboard TO 'spa_student'@'localhost';
GRANT INSERT ON spa_enhanced_db.audit_log TO 'spa_student'@'localhost';
GRANT SELECT ON spa_enhanced_db.subjects TO 'spa_student'@'localhost';
GRANT SELECT ON spa_enhanced_db.student_subjects TO 'spa_student'@'localhost';
GRANT SELECT ON spa_enhanced_db.faculty_subjects TO 'spa_student'@'localhost';
GRANT SELECT ON spa_enhanced_db.attendance TO 'spa_student'@'localhost';

FLUSH PRIVILEGES;
