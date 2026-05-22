# SPA Database Schema & SQL Reference

## Database Overview

**Database Name**: `spa_enhanced_db`  
**Character Set**: utf8mb4 (Unicode support)  
**Collation**: utf8mb4_unicode_ci  
**Engine**: InnoDB (ACID compliance, foreign keys)

---

## Table Definitions

### 1. users Table (System Administrators)

```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE COLLATE utf8mb4_unicode_ci,
    password_hash CHAR(64) NOT NULL,
    role ENUM('admin', 'faculty', 'student') NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (CHAR_LENGTH(username) >= 3),
    CHECK (CHAR_LENGTH(password_hash) = 64)
) ENGINE=InnoDB;
```

**Column Details**:

| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| id | INT AUTO_INCREMENT | PRIMARY KEY | Unique identifier |
| username | VARCHAR(50) | NOT NULL, UNIQUE | Login username (3+ chars) |
| password_hash | CHAR(64) | NOT NULL | SHA256 hash (exactly 64 chars) |
| role | ENUM(...) | NOT NULL | Account type (always 'admin' for this table) |
| is_active | BOOLEAN | DEFAULT TRUE | Account status |
| created_at | TIMESTAMP | DEFAULT NOW() | When account created |

**Sample Data**:
```sql
INSERT INTO users (username, password_hash, role) 
VALUES ('admin', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'admin');
```

**Indexes**:
- PRIMARY KEY (id)
- UNIQUE (username)

---

### 2. students Table

```sql
CREATE TABLE students (
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
```

**Column Details**:

| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| prn | CHAR(11) | PRIMARY KEY | Student ID (YY0AABBCRRR format) |
| password_hash | CHAR(64) | NOT NULL | SHA256 password hash |
| name | VARCHAR(100) | NOT NULL | Student full name |
| department | VARCHAR(60) | NOT NULL | Department name |
| marks | DECIMAL(5,2) | 0-100 | Rolling average of all subjects |
| is_active | BOOLEAN | DEFAULT TRUE | Account status |
| enrolled_at | TIMESTAMP | DEFAULT NOW() | Enrollment date |

**PRN Format Validation**:
```
Pattern: YY0AABBCRRR (11 digits)
├─ YY: Year (25, 26, 27)
├─ 0: Fixed digit zero
├─ AA: Category (06, 07)
├─ BB: Branch (01-06)
├─ C: Section (1, 2, 3)
└─ RRR: Roll (000-999)

Example: 25007011001 is VALID
Example: 25008011001 is INVALID (AA must be 06 or 07)
```

**Sample Data**:
```sql
INSERT INTO students (prn, password_hash, name, department) 
VALUES (
    '25007011001',
    'e7a9ea89c8cf6c6c1a1d10d8d0b7e32c1d9b7e6a5f4c3b2a1e9d8c7b6a5f4e3d',
    'John Doe',
    'Computer Science'
);
```

**Indexes**:
- PRIMARY KEY (prn)

**Statistics Query**:
```sql
SELECT COUNT(*) as total_students, 
       AVG(marks) as avg_marks,
       MIN(marks) as min_marks,
       MAX(marks) as max_marks
FROM students;
```

---

### 3. faculty Table

```sql
CREATE TABLE faculty (
    prn CHAR(11) PRIMARY KEY,
    password_hash CHAR(64) NOT NULL,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(60) NOT NULL COLLATE utf8mb4_unicode_ci,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (prn REGEXP '^(25|26|27)0(06|07)(01|02|03|04|05|06)[123][0-9]{3}$'),
    CHECK (CHAR_LENGTH(password_hash) = 64)
) ENGINE=InnoDB;
```

**Column Details**:

| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| prn | CHAR(11) | PRIMARY KEY | Faculty ID (same format as student) |
| password_hash | CHAR(64) | NOT NULL | SHA256 password hash |
| name | VARCHAR(100) | NOT NULL | Faculty full name |
| department | VARCHAR(60) | NOT NULL | Department name |
| is_active | BOOLEAN | DEFAULT TRUE | Account status |
| created_at | TIMESTAMP | DEFAULT NOW() | Account creation date |

**Sample Data**:
```sql
INSERT INTO faculty (prn, password_hash, name, department) 
VALUES (
    '25006011001',
    'faculty_hash_64_chars_here',
    'Prof. Smith',
    'Computer Science'
);
```

---

### 4. audit_log Table

```sql
CREATE TABLE audit_log (
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
```

**Column Details**:

| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| id | INT AUTO_INCREMENT | PRIMARY KEY | Log entry ID |
| user_id | INT | FOREIGN KEY (users.id) | Admin who performed action |
| action | VARCHAR(60) | NOT NULL | Action type |
| details | VARCHAR(1000) | NULL | Additional details |
| timestamp | TIMESTAMP | DEFAULT NOW() | When action occurred |

**Action Types**:
```
Authentication
├─ LOGIN_SUCCESS
├─ LOGIN_FAILED
└─ LOGOUT

Student Management
├─ ADD_STUDENT
├─ UPDATE_STUDENT
└─ DELETE_STUDENT

User Management
├─ CREATE_USER_ACCOUNT
└─ TOGGLE_USER_STATUS

Academic Management
├─ CREATE_SUBJECT
├─ ENROLL_STUDENT
├─ UNENROLL_STUDENT
├─ ASSIGN_FACULTY
├─ UNASSIGN_FACULTY
└─ FACULTY_UPDATE_MARKS

Attendance
├─ SAVE_ATTENDANCE
└─ VIEW_ATTENDANCE

Analytics
├─ AWARD_BONUS
└─ EXPORT_HIGH_PERFORMERS

System
├─ CREATE_MYSQL_USERS
└─ VIEW_AUDIT_LOG
```

**Sample Data**:
```sql
INSERT INTO audit_log (user_id, action, details) 
VALUES (1, 'ADD_STUDENT', 'Added student 25007011001 - John Doe in Computer Science');
```

**View Last 30 Actions**:
```sql
SELECT id, action, details, timestamp 
FROM audit_log 
ORDER BY timestamp DESC, id DESC 
LIMIT 30;
```

---

### 5. subjects Table

```sql
CREATE TABLE subjects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(20) NOT NULL,
    name VARCHAR(100) NOT NULL,
    batch VARCHAR(50) NOT NULL,
    UNIQUE(code, batch)
) ENGINE=InnoDB;
```

**Column Details**:

| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| id | INT AUTO_INCREMENT | PRIMARY KEY | Subject ID |
| code | VARCHAR(20) | NOT NULL | Course code (e.g., CS101) |
| name | VARCHAR(100) | NOT NULL | Subject name |
| batch | VARCHAR(50) | NOT NULL | Academic year/batch |

**Uniqueness**:
- Combination of (code, batch) must be unique
- Can have "CS101" in batch "2025" and "2026"

**Sample Data**:
```sql
INSERT INTO subjects (code, name, batch) 
VALUES 
    ('CS101', 'Data Structures', '2025'),
    ('CS102', 'Algorithms', '2025'),
    ('MA101', 'Calculus', '2025');
```

**List All Subjects by Batch**:
```sql
SELECT id, code, name, batch 
FROM subjects 
WHERE batch = '2025' 
ORDER BY code;
```

---

### 6. student_subjects Table (Enrollment + Grades)

```sql
CREATE TABLE student_subjects (
    subject_id INT NOT NULL,
    student_prn CHAR(11) NOT NULL,
    marks DECIMAL(5,2) DEFAULT NULL,
    PRIMARY KEY (subject_id, student_prn),
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    FOREIGN KEY (student_prn) REFERENCES students(prn) 
        ON UPDATE CASCADE ON DELETE CASCADE,
    CHECK (marks IS NULL OR (marks >= 0 AND marks <= 100))
) ENGINE=InnoDB;
```

**Column Details**:

| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| subject_id | INT | FOREIGN KEY | Reference to subjects table |
| student_prn | CHAR(11) | FOREIGN KEY | Reference to students table |
| marks | DECIMAL(5,2) | 0-100 or NULL | Grade in subject (NULL = not graded) |

**Composite Primary Key**:
- Each student can enroll in each subject only once
- (subject_id, student_prn) must be unique

**Sample Data**:
```sql
INSERT INTO student_subjects (subject_id, student_prn, marks) 
VALUES (1, '25007011001', NULL);  -- Enrolled but not graded

INSERT INTO student_subjects (subject_id, student_prn, marks) 
VALUES (1, '25007011001', 85.50);  -- Enrolled with grade
```

**Update Student Mark**:
```sql
UPDATE student_subjects 
SET marks = 85.50 
WHERE subject_id = 1 AND student_prn = '25007011001';
```

**Get Student Subjects & Marks**:
```sql
SELECT s.code, s.name, ss.marks
FROM student_subjects ss
JOIN subjects s ON s.id = ss.subject_id
WHERE ss.student_prn = '25007011001'
ORDER BY s.code;
```

---

### 7. faculty_subjects Table (Teaching Assignments)

```sql
CREATE TABLE faculty_subjects (
    faculty_prn CHAR(11) NOT NULL,
    subject_id INT NOT NULL,
    PRIMARY KEY (faculty_prn, subject_id),
    FOREIGN KEY (faculty_prn) REFERENCES faculty(prn) 
        ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
) ENGINE=InnoDB;
```

**Column Details**:

| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| faculty_prn | CHAR(11) | FOREIGN KEY | Reference to faculty table |
| subject_id | INT | FOREIGN KEY | Reference to subjects table |

**Purpose**:
- Maps which faculty teaches which subjects
- One faculty can teach multiple subjects
- One subject can have multiple faculty

**Sample Data**:
```sql
INSERT INTO faculty_subjects (faculty_prn, subject_id) 
VALUES ('25006011001', 1);  -- Faculty teaches CS101
```

**Get Faculty Teaching Assignments**:
```sql
SELECT s.code, s.name, f.name as professor
FROM faculty_subjects fs
JOIN subjects s ON s.id = fs.subject_id
JOIN faculty f ON f.prn = fs.faculty_prn
WHERE fs.faculty_prn = '25006011001';
```

---

### 8. attendance Table

```sql
CREATE TABLE attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    subject_id INT NOT NULL,
    student_prn CHAR(11) NOT NULL,
    date DATE NOT NULL,
    status ENUM('Present', 'Absent') NOT NULL,
    UNIQUE(subject_id, student_prn, date),
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    FOREIGN KEY (student_prn) REFERENCES students(prn) 
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;
```

**Column Details**:

| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| id | INT AUTO_INCREMENT | PRIMARY KEY | Record ID |
| subject_id | INT | FOREIGN KEY | Reference to subjects table |
| student_prn | CHAR(11) | FOREIGN KEY | Reference to students table |
| date | DATE | NOT NULL | Date of class |
| status | ENUM(...) | NOT NULL | Present or Absent |

**Uniqueness**:
- Each student can have only one attendance record per subject per day
- Prevents duplicate entries

**Sample Data**:
```sql
INSERT INTO attendance (subject_id, student_prn, date, status) 
VALUES (1, '25007011001', '2026-05-22', 'Present');

-- Update if already recorded (upsert)
INSERT INTO attendance (subject_id, student_prn, date, status) 
VALUES (1, '25007011001', '2026-05-22', 'Absent')
ON DUPLICATE KEY UPDATE status = VALUES(status);
```

**Get Attendance Summary**:
```sql
SELECT date,
       SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) as present_count,
       SUM(CASE WHEN status = 'Absent' THEN 1 ELSE 0 END) as absent_count,
       COUNT(*) as total_count
FROM attendance
WHERE subject_id = 1
GROUP BY date
ORDER BY date DESC;
```

**Get Student Attendance Percentage**:
```sql
SELECT s.code, s.name,
       COUNT(a.id) as total_classes,
       SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) as attended,
       ROUND(SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) * 100.0 
             / NULLIF(COUNT(a.id), 0), 2) as attendance_percentage
FROM subjects s
LEFT JOIN attendance a ON a.subject_id = s.id
WHERE a.student_prn = '25007011001'
GROUP BY s.id, s.code, s.name;
```

---

## Views

### View 1: vw_student_grades

```sql
CREATE OR REPLACE VIEW vw_student_grades AS
SELECT prn, name, department, marks,
    CASE 
        WHEN marks >= 90 THEN 'A'
        WHEN marks >= 75 THEN 'B'
        WHEN marks >= 60 THEN 'C'
        WHEN marks >= 40 THEN 'D'
        ELSE 'F'
    END AS grade
FROM students;
```

**Purpose**: Display students with calculated letter grades

**Grading Scale**:
- A: 90-100 (Excellent)
- B: 75-89 (Good)
- C: 60-74 (Satisfactory)
- D: 40-59 (Pass)
- F: <40 (Fail)

**Usage**:
```sql
SELECT * FROM vw_student_grades WHERE grade = 'A';
```

---

### View 2: vw_department_leaderboard

```sql
CREATE OR REPLACE VIEW vw_department_leaderboard AS
SELECT department, 
       COUNT(*) AS total_students, 
       ROUND(AVG(marks), 2) AS average_marks,
       MAX(marks) AS highest_marks, 
       MIN(marks) AS lowest_marks
FROM students
GROUP BY department;
```

**Purpose**: Department-wise performance statistics

**Columns**:
- `department`: Department name
- `total_students`: Number of enrolled students
- `average_marks`: Average score in department
- `highest_marks`: Best student score
- `lowest_marks`: Lowest student score

**Usage**:
```sql
SELECT * FROM vw_department_leaderboard 
ORDER BY average_marks DESC;
```

---

## Complex Query Examples

### Query 1: Student Academic Summary

```sql
SELECT 
    s.prn,
    s.name,
    s.department,
    s.marks as overall_average,
    (SELECT COUNT(*) FROM student_subjects 
     WHERE student_prn = s.prn AND marks IS NOT NULL) as subjects_graded,
    (SELECT COUNT(*) FROM attendance 
     WHERE student_prn = s.prn) as total_attendance_records
FROM students s
WHERE s.prn = '25007011001';
```

---

### Query 2: Faculty Subject Details

```sql
SELECT 
    f.prn as faculty_prn,
    f.name as faculty_name,
    s.code,
    s.name as subject_name,
    (SELECT COUNT(*) FROM student_subjects 
     WHERE subject_id = s.id) as students_enrolled,
    ROUND(AVG(ss.marks), 2) as class_average
FROM faculty_subjects fs
JOIN faculty f ON fs.faculty_prn = f.prn
JOIN subjects s ON fs.subject_id = s.id
LEFT JOIN student_subjects ss ON ss.subject_id = s.id
WHERE f.prn = '25006011001'
GROUP BY s.id;
```

---

### Query 3: High Performers Report

```sql
SELECT 
    s.prn,
    s.name,
    s.department,
    s.marks,
    (SELECT COUNT(*) FROM student_subjects 
     WHERE student_prn = s.prn) as total_subjects,
    (SELECT COUNT(*) FROM student_subjects 
     WHERE student_prn = s.prn AND marks >= 60) as passed_subjects
FROM students s
WHERE s.marks > (SELECT AVG(marks) FROM students)
ORDER BY s.marks DESC, s.name ASC;
```

---

### Query 4: Attendance Statistics by Student

```sql
SELECT 
    s.prn,
    s.name,
    s.department,
    COUNT(DISTINCT a.date) as classes_attended,
    (SELECT COUNT(DISTINCT date) FROM attendance) as total_classes,
    ROUND(COUNT(DISTINCT a.date) * 100.0 / 
          (SELECT COUNT(DISTINCT date) FROM attendance), 2) as attendance_percentage
FROM students s
LEFT JOIN attendance a ON a.student_prn = s.prn AND a.status = 'Present'
GROUP BY s.prn, s.name, s.department
HAVING attendance_percentage >= 75
ORDER BY attendance_percentage DESC;
```

---

### Query 5: Department Comparison

```sql
SELECT 
    d1.department,
    d1.total_students,
    d1.average_marks,
    d2.overall_average,
    ROUND(d1.average_marks - d2.overall_average, 2) as difference
FROM (
    SELECT department, COUNT(*) as total_students, 
           ROUND(AVG(marks), 2) as average_marks
    FROM students
    GROUP BY department
) d1
CROSS JOIN (
    SELECT ROUND(AVG(marks), 2) as overall_average
    FROM students
) d2
ORDER BY d1.average_marks DESC;
```

---

## Maintenance Queries

### Backup Database

```bash
mysqldump -u root -p spa_enhanced_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Restore Database

```bash
mysql -u root -p spa_enhanced_db < backup_20260522_143022.sql
```

### View Database Size

```sql
SELECT 
    table_name,
    ROUND(((data_length + index_length) / 1024 / 1024), 2) as size_mb
FROM information_schema.TABLES
WHERE table_schema = 'spa_enhanced_db'
ORDER BY size_mb DESC;
```

### List All Tables

```sql
SHOW TABLES;
```

### View Table Structure

```sql
DESCRIBE students;
-- or
SHOW FULL COLUMNS FROM students;
```

### Count Records in Each Table

```sql
SELECT 
    'users' as table_name, COUNT(*) as record_count FROM users
UNION ALL
SELECT 'students', COUNT(*) FROM students
UNION ALL
SELECT 'faculty', COUNT(*) FROM faculty
UNION ALL
SELECT 'subjects', COUNT(*) FROM subjects
UNION ALL
SELECT 'student_subjects', COUNT(*) FROM student_subjects
UNION ALL
SELECT 'faculty_subjects', COUNT(*) FROM faculty_subjects
UNION ALL
SELECT 'attendance', COUNT(*) FROM attendance
UNION ALL
SELECT 'audit_log', COUNT(*) FROM audit_log;
```

---

## Performance Tuning

### Add Indexes for Slow Queries

```sql
-- For search by department
CREATE INDEX idx_students_dept ON students(department);

-- For attendance date range queries
CREATE INDEX idx_attendance_date ON attendance(date);

-- For audit log timestamp queries
CREATE INDEX idx_audit_timestamp ON audit_log(timestamp);
```

### Check Query Execution Plan

```sql
EXPLAIN SELECT s.* FROM student_subjects ss
JOIN subjects s ON s.id = ss.subject_id
WHERE ss.student_prn = '25007011001';
```

### Optimize Table Storage

```sql
OPTIMIZE TABLE students;
OPTIMIZE TABLE attendance;
OPTIMIZE TABLE audit_log;
```

---

## Data Integrity

### Check Foreign Key Constraints

```sql
SELECT CONSTRAINT_NAME, TABLE_NAME, REFERENCED_TABLE_NAME
FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = 'spa_enhanced_db'
AND REFERENCED_TABLE_NAME IS NOT NULL;
```

### Verify Data Consistency

```sql
-- Check students with no name
SELECT * FROM students WHERE name = '' OR name IS NULL;

-- Check invalid marks
SELECT * FROM students WHERE marks < 0 OR marks > 100;

-- Check orphaned attendance records
SELECT * FROM attendance 
WHERE subject_id NOT IN (SELECT id FROM subjects);
```

---

## Migration & Export

### Export to CSV

```sql
SELECT * FROM students 
INTO OUTFILE '/var/lib/mysql/students.csv'
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n';
```

### Import from CSV

```sql
LOAD DATA INFILE '/var/lib/mysql/students.csv'
INTO TABLE students
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
(prn, password_hash, name, department);
```

---

## User & Permissions Management

### Create Application Users

```sql
-- Admin user (full access)
CREATE USER 'spa_admin'@'localhost' IDENTIFIED BY 'strong_password';
GRANT SELECT, INSERT, UPDATE, DELETE ON spa_enhanced_db.* TO 'spa_admin'@'localhost';

-- Faculty user (limited access)
CREATE USER 'spa_faculty'@'localhost' IDENTIFIED BY 'strong_password';
GRANT SELECT, INSERT, UPDATE ON spa_enhanced_db.students TO 'spa_faculty'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON spa_enhanced_db.attendance TO 'spa_faculty'@'localhost';

-- Student user (read-only)
CREATE USER 'spa_student'@'localhost' IDENTIFIED BY 'strong_password';
GRANT SELECT ON spa_enhanced_db.students TO 'spa_student'@'localhost';
GRANT SELECT ON spa_enhanced_db.vw_student_grades TO 'spa_student'@'localhost';

FLUSH PRIVILEGES;
```

### View User Privileges

```sql
SHOW GRANTS FOR 'spa_admin'@'localhost';
```

---

**Document Version**: 1.0  
**Last Updated**: May 22, 2026  
**Compatibility**: MySQL 5.7+, MariaDB 10.3+
