# Student Performance Analyzer (SPA) - Complete System Manual

**Version**: 1.0  
**Date**: May 2026  
**Type**: CLI-based Relational Database Management System  
**Database**: MySQL 8.0+

---

## Table of Contents

1. [System Overview](#system-overview)
2. [System Architecture](#system-architecture)
3. [Installation & Setup](#installation--setup)
4. [Database Schema](#database-schema)
5. [User Roles & Permissions](#user-roles--permissions)
6. [Complete Function Reference](#complete-function-reference)
7. [Database Queries](#database-queries)
8. [User Workflows](#user-workflows)
9. [Security & Audit](#security--audit)
10. [Troubleshooting](#troubleshooting)

---

## System Overview

### Purpose
The Student Performance Analyzer (SPA) is a comprehensive terminal-based application designed to manage student academic records, attendance, grades, and performance analytics in an educational institution. It provides role-based access for administrators, faculty, and students.

### Key Features
- **User Authentication**: Role-based login (Admin, Faculty, Student)
- **Student Management**: Full CRUD operations on student records
- **Academic Management**: Subject creation, enrollment, and grade management
- **Attendance Tracking**: Faculty can record daily attendance
- **Analytics**: Department-wise performance analysis, leaderboards, grade distributions
- **Audit Logging**: Complete security audit trail of all system actions
- **Data Export**: Export high-performing students to CSV
- **Database Initialization**: Automatic schema creation on first run

### Technology Stack
- **Language**: Python 3.x
- **Database**: MySQL/MariaDB
- **Libraries**: 
  - `mysql.connector` - MySQL connection
  - `pymysql` - Alternative MySQL driver with better authentication support
  - `hashlib` - Password hashing (SHA256)
  - `csv` - CSV export functionality
  - `datetime` - Date/time operations
  - `getpass` - Secure password input

---

## System Architecture

### Application Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    SPA Application Start                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
          ┌─────────────────────────────────────┐
          │  Ensure Database Setup (Auto Init)  │
          └─────────────────────────────────────┘
                            ↓
          ┌─────────────────────────────────────┐
          │      Authentication (Login)         │
          │  - Admin (username/password)        │
          │  - Faculty (PRN/password)           │
          │  - Student (PRN/password)           │
          └─────────────────────────────────────┘
                            ↓
          ┌─────────────────────────────────────┐
          │   Role-Based Menu (Admin/Faculty/   │
          │         Student Portal)             │
          └─────────────────────────────────────┘
                            ↓
          ┌─────────────────────────────────────┐
          │    Execute Function/Query           │
          │  - Log to Audit Trail              │
          │  - Perform DB Operation            │
          │  - Display Results                 │
          └─────────────────────────────────────┘
```

---

## Installation & Setup

### Prerequisites
1. **MySQL Server** running on localhost (port 3306)
2. **Python 3.x** installed
3. **Administrator Access** to MySQL

### Configuration

Edit the `DB_CONFIG` in `PRN_analyzer.py`:

```python
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "mysql",  # Change if needed
    "database": "spa_enhanced_db"
}
```

### Installation Steps

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Application**:
   ```bash
   python PRN_analyzer.py
   ```
   Or use precompiled executable:
   ```bash
   ./PRN_spa.exe
   ```

3. **First Run Setup**:
   - Application automatically creates database `spa_enhanced_db`
   - All tables and views are created automatically
   - Default admin account is created:
     - **Username**: `admin`
     - **Password**: `admin123`

### Database Auto-Initialization

The function `ensure_database_setup()` handles:
- Creating the database if it doesn't exist
- Creating all required tables
- Creating database views
- Inserting default admin user (if not exists)

---

## Database Schema

### Database: `spa_enhanced_db`

#### Table 1: `users`
**Purpose**: System administrator accounts

```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash CHAR(64) NOT NULL,
    role ENUM('admin', 'faculty', 'student') NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (CHAR_LENGTH(username) >= 3),
    CHECK (CHAR_LENGTH(password_hash) = 64)
);
```

**Fields**:
- `id`: Unique identifier
- `username`: Admin login username (3+ chars)
- `password_hash`: SHA256 hash of password
- `role`: Account role (always 'admin' for this table)
- `is_active`: Account status (TRUE=active, FALSE=disabled)
- `created_at`: Account creation timestamp

**Constraints**:
- Username must be unique
- Username minimum 3 characters
- Password hash must be 64 characters (SHA256)

---

#### Table 2: `students`
**Purpose**: Student profile and overall academic records

```sql
CREATE TABLE students (
    prn CHAR(11) PRIMARY KEY,
    password_hash CHAR(64) NOT NULL,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(60) NOT NULL,
    marks DECIMAL(5,2) NOT NULL DEFAULT 0.00,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    enrolled_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (marks >= 0 AND marks <= 100),
    CHECK (prn REGEXP '^(25|26|27)0(06|07)(01|02|03|04|05|06)[123][0-9]{3}$'),
    CHECK (CHAR_LENGTH(password_hash) = 64)
);
```

**Fields**:
- `prn`: Permanent Registration Number (11 digits) - Primary Key
- `password_hash`: SHA256 hash of student password
- `name`: Student full name
- `department`: Department name (e.g., "Computer Science")
- `marks`: Rolling average of all subject marks
- `is_active`: Account status
- `enrolled_at`: Enrollment date

**Constraints**:
- PRN format: `YY0AABBCRRR`
  - YY: Year (25, 26, or 27)
  - 0: Fixed zero
  - AA: Category (06 or 07)
  - BB: Branch (01-06)
  - C: Section (1, 2, or 3)
  - RRR: Roll number (000-999)
- Marks range: 0-100
- Password hash: exactly 64 characters

**Example PRN**: `25007011001`

---

#### Table 3: `faculty`
**Purpose**: Faculty/Professor records

```sql
CREATE TABLE faculty (
    prn CHAR(11) PRIMARY KEY,
    password_hash CHAR(64) NOT NULL,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(60) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (prn REGEXP '^(25|26|27)0(06|07)(01|02|03|04|05|06)[123][0-9]{3}$'),
    CHECK (CHAR_LENGTH(password_hash) = 64)
);
```

**Fields**:
- `prn`: Faculty PRN (11 digits) - Primary Key
- `password_hash`: SHA256 hash of password
- `name`: Faculty name
- `department`: Department name
- `is_active`: Account status
- `created_at`: Account creation timestamp

---

#### Table 4: `audit_log`
**Purpose**: Security audit trail for all system actions

```sql
CREATE TABLE audit_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NULL,
    action VARCHAR(60) NOT NULL,
    details VARCHAR(1000) NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_audit_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON UPDATE CASCADE ON DELETE SET NULL
);
```

**Fields**:
- `id`: Log entry ID
- `user_id`: Reference to `users.id` (NULL for non-admin)
- `action`: Type of action (e.g., "LOGIN_SUCCESS", "ADD_STUDENT")
- `details`: Additional details (max 1000 chars)
- `timestamp`: When action occurred

**Audit Actions Logged**:
- LOGIN_SUCCESS, LOGIN_FAILED, LOGOUT
- ADD_STUDENT, UPDATE_STUDENT, DELETE_STUDENT
- CREATE_USER_ACCOUNT, TOGGLE_USER_STATUS
- ENROLL_STUDENT, UNENROLL_STUDENT
- ASSIGN_FACULTY, UNASSIGN_FACULTY
- UPDATE_MARKS (faculty updates)
- SAVE_ATTENDANCE, VIEW_AUDIT_LOG
- EXPORT_HIGH_PERFORMERS, AWARD_BONUS, etc.

---

#### Table 5: `subjects`
**Purpose**: Course/Subject catalog

```sql
CREATE TABLE subjects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(20) NOT NULL,
    name VARCHAR(100) NOT NULL,
    batch VARCHAR(50) NOT NULL,
    UNIQUE(code, batch)
);
```

**Fields**:
- `id`: Subject ID
- `code`: Subject code (e.g., "CS101")
- `name`: Subject name (e.g., "Data Structures")
- `batch`: Batch year (e.g., "2025")

**Constraints**:
- Combination of code + batch must be unique

---

#### Table 6: `student_subjects`
**Purpose**: Student enrollment in subjects with grades

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
);
```

**Fields**:
- `subject_id`: Reference to `subjects.id`
- `student_prn`: Reference to `students.prn`
- `marks`: Grade in the subject (NULL = not graded yet, 0-100)

**Purpose**: Junction table linking students to subjects with their grades

---

#### Table 7: `faculty_subjects`
**Purpose**: Faculty teaching assignments

```sql
CREATE TABLE faculty_subjects (
    faculty_prn CHAR(11) NOT NULL,
    subject_id INT NOT NULL,
    PRIMARY KEY (faculty_prn, subject_id),
    FOREIGN KEY (faculty_prn) REFERENCES faculty(prn) 
        ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
);
```

**Fields**:
- `faculty_prn`: Reference to `faculty.prn`
- `subject_id`: Reference to `subjects.id`

**Purpose**: Maps which faculty teaches which subjects

---

#### Table 8: `attendance`
**Purpose**: Daily class attendance records

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
);
```

**Fields**:
- `id`: Record ID
- `subject_id`: Reference to `subjects.id`
- `student_prn`: Reference to `students.prn`
- `date`: Date of class
- `status`: Present or Absent

**Constraints**:
- Each student can only have one attendance record per subject per day
- Unique index on (subject_id, student_prn, date)

---

### Database Views

#### View 1: `vw_student_grades`
**Purpose**: Student grades with letter grades

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

**Grading Scale**:
- A: 90-100
- B: 75-89
- C: 60-74
- D: 40-59
- F: <40

---

#### View 2: `vw_department_leaderboard`
**Purpose**: Department-wise statistics

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

**Columns**:
- `department`: Department name
- `total_students`: Number of students in department
- `average_marks`: Average marks of department
- `highest_marks`: Best student score
- `lowest_marks`: Lowest student score

---

### Database Relationships Diagram

```
users (1)
  ↓ (0..N)
audit_log


faculty (1)
  ↓ (0..N)
faculty_subjects
  ↓ (N)
subjects (1)
  ↑ (0..N)
student_subjects
  ↓ (N)
students (1)
  ↓ (0..N)
attendance


students (1)
  ↓ (0..N)
student_subjects
  ↓ (N)
subjects
```

**Key Relationships**:
- **One-to-Many**: One subject has many student enrollments
- **One-to-Many**: One student has many subject enrollments
- **One-to-Many**: One faculty teaches multiple subjects
- **One-to-Many**: One subject can have multiple faculty (though typically one)
- **One-to-Many**: One subject has many attendance records
- **One-to-Many**: One student has many attendance records
- **One-to-Many**: One admin user creates multiple audit logs

---

## User Roles & Permissions

### Role 1: Administrator

**Authentication**: Username + Password (stored in `users` table)

**Permissions**:
- ✅ Full CRUD on students
- ✅ Full CRUD on faculty
- ✅ Full CRUD on users (create admins)
- ✅ Create and manage subjects
- ✅ Enroll/unenroll students
- ✅ Assign/unassign faculty
- ✅ View and manage audit logs
- ✅ Award bonus marks
- ✅ Create MySQL application users
- ✅ View all analytics and reports

**Menu Options**:
1. Live Analytics Dashboard
2. Add Student Record
3. View All Students
4. Search Students by Department
5. Update Student Profile
6. Delete Student Account
7. Department Performance Analytics
8. Grade Band Distribution Report
9. Top Academic Performers Directory
10. Department Leaderboard stats
11. Award Departmental Bonus Marks
12. Export High Performers to CSV
13. Create User Account
14. List Active System Accounts
15. Toggle User Active status
16. Create MySQL Application Users & Privileges
17. View Security Audit Logs
18. Manage Academic Subjects & Enrollments

---

### Role 2: Faculty/Professor

**Authentication**: PRN + Password (stored in `faculty` table)

**Permissions**:
- ✅ View assigned subjects
- ✅ Update student subject grades
- ✅ Mark attendance (roll call)
- ✅ View attendance history
- ✅ View analytics (read-only)
- ✅ View top performers
- ✅ View department leaderboard
- ❌ Cannot modify student records
- ❌ Cannot create users
- ❌ Cannot view audit logs

**Menu Options**:
1. View My Assigned Subjects
2. Enter / Update Student Marks
3. Manage Subject Attendance sheets
4. Live Analytics Dashboard (read-only)
5. Top Performers Catalog (read-only)
6. Department Leaderboard status (read-only)

---

### Role 3: Student

**Authentication**: PRN + Password (stored in `students` table)

**Permissions**:
- ✅ View own academic record
- ✅ View own transcripts
- ✅ View own attendance
- ✅ View top performers (read-only)
- ✅ View department leaderboard (read-only)
- ❌ Cannot modify any records
- ❌ Cannot view other students' records
- ❌ Cannot manage anything

**Menu Options**:
1. View My Academic Record & Transcripts
2. View Top Performers Catalog (read-only)
3. View Department Leaderboard status (read-only)

---

## Complete Function Reference

### Core Utility Functions

#### 1. `get_connection()`
**Purpose**: Establish database connection

```python
def get_connection():
```

**Returns**: MySQL connection object

**Details**:
- First attempts `mysql.connector`
- Falls back to `pymysql` if connector fails
- Handles authentication plugin issues
- Connected to `spa_enhanced_db` database

**Usage**: All database operations

---

#### 2. `get_base_connection()`
**Purpose**: Connect to MySQL server without selecting database

```python
def get_base_connection():
```

**Returns**: MySQL connection object (no database selected)

**Details**:
- Used for database creation
- Used in initial setup
- Same fallback mechanism as `get_connection()`

---

#### 3. `hash_password(password)`
**Purpose**: Generate SHA256 hash of password

```python
def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()
```

**Parameters**:
- `password` (str): Plain text password

**Returns**: 64-character SHA256 hex digest

**Example**:
```python
hashed = hash_password("admin123")
# Returns: "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9"
```

---

#### 4. `clear_screen()`
**Purpose**: Clear terminal screen

```python
def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")
```

**Details**:
- Windows: Uses `cls`
- Linux/Mac: Uses `clear`

---

#### 5. `pause()`
**Purpose**: Pause and wait for user input

```python
def pause():
    input("\nPress Enter to continue...")
```

---

#### 6. `print_title(title)`
**Purpose**: Display formatted title

```python
def print_title(title):
```

**Parameters**:
- `title` (str): Title text

**Output Format**:
```
==============================================================================
                           Your Title Here
==============================================================================
```

---

#### 7. `print_message(message, kind="info")`
**Purpose**: Display formatted message with status indicator

```python
def print_message(message, kind="info"):
```

**Parameters**:
- `message` (str): Message text
- `kind` (str): One of "info", "success", "error", "warn"

**Output Examples**:
```
[INFO] This is an informational message
[OK] Operation completed successfully
[ERROR] An error occurred
[WARN] Warning message
```

---

#### 8. `normalize(value)`
**Purpose**: Format database values for display

```python
def normalize(value):
```

**Parameters**:
- `value`: Any database value

**Formatting Rules**:
- Decimal → 2 decimal places
- DateTime → "YYYY-MM-DD HH:MM"
- Date → "YYYY-MM-DD"
- None → Empty string
- Other → String conversion

---

#### 9. `print_table(headers, rows)`
**Purpose**: Display data as formatted table

```python
def print_table(headers, rows):
```

**Parameters**:
- `headers` (tuple): Column headers
- `rows` (list): List of row tuples

**Output Format**:
```
+-------+--------+------+
| Name  | ID     | Mark |
+-------+--------+------+
| John  | 123456 | 85   |
| Jane  | 123457 | 92   |
+-------+--------+------+
```

**Features**:
- Auto-width calculation
- Normalizes all values
- Shows "No records found" if empty

---

#### 10. `input_int(prompt, minimum=None, maximum=None)`
**Purpose**: Get validated integer input

```python
def input_int(prompt, minimum=None, maximum=None):
```

**Parameters**:
- `prompt` (str): Input prompt text
- `minimum` (int): Minimum allowed value (optional)
- `maximum` (int): Maximum allowed value (optional)

**Returns**: Integer or None if blank

**Features**:
- Validates numeric input
- Checks min/max constraints
- Repeats on invalid input

---

#### 11. `input_float(prompt, minimum=None, maximum=None)`
**Purpose**: Get validated decimal input

```python
def input_float(prompt, minimum=None, maximum=None):
```

**Parameters**:
- `prompt` (str): Input prompt text
- `minimum` (float): Minimum allowed value (optional)
- `maximum` (float): Maximum allowed value (optional)

**Returns**: Float or None if blank

---

#### 12. `validate_prn(prn)`
**Purpose**: Validate PRN format

```python
def validate_prn(prn):
```

**Parameters**:
- `prn` (str): PRN to validate

**Returns**: Tuple of (valid_prn, error_message)

**PRN Format**: `YY0AABBCRRR` (11 digits)
- YY: Year (25, 26, 27)
- 0: Fixed zero
- AA: Category (06, 07)
- BB: Branch (01-06)
- C: Section (1, 2, 3)
- RRR: Roll (000-999)

**Example**:
```python
prn, error = validate_prn("25007011001")
if error:
    print_message(error, "warn")
```

---

#### 13. `log_audit(action, details="")`
**Purpose**: Log action to audit trail

```python
def log_audit(action, details=""):
```

**Parameters**:
- `action` (str): Action name (max 60 chars)
- `details` (str): Additional details (max 1000 chars)

**Details**:
- Inserts into `audit_log` table
- Associates with current user
- Automatically adds timestamp
- Silent on error

**Example**:
```python
log_audit("ADD_STUDENT", f"Added student {prn} - {name}")
```

---

#### 14. `update_overall_student_marks(student_prn)`
**Purpose**: Recalculate student's rolling average

```python
def update_overall_student_marks(student_prn):
```

**Parameters**:
- `student_prn` (str): Student PRN

**Operation**:
1. Calculates average of all subject marks
2. Updates `students.marks` field
3. Used after grade changes or enrollment changes

---

#### 15. `ensure_database_setup()`
**Purpose**: Auto-initialize database on first run

```python
def ensure_database_setup():
```

**Operation**:
1. Checks if `spa_enhanced_db` exists
2. Creates database if missing
3. Creates all tables
4. Creates all views
5. Inserts default admin user
6. Displays status messages

---

### Authentication Functions

#### 16. `login()`
**Purpose**: Authenticate user and establish session

```python
def login():
```

**Process**:
1. Prompts for username/PRN and password
2. Checks `users` table (admin)
3. Checks `faculty` table (faculty)
4. Checks `students` table (student)
5. Verifies password hash
6. Checks if account is active
7. Populates `current_user` dictionary
8. Logs audit entry

**Returns**: True if successful, False otherwise

**current_user dictionary**:
```python
{
    "id": 1,           # users.id (NULL for faculty/student)
    "username": "admin",  # users.username or student name
    "role": "admin",      # admin/faculty/student
    "student_id": None    # PRN for faculty/student
}
```

---

#### 17. `logout()`
**Purpose**: Clear session and log out user

```python
def logout():
```

**Operation**:
1. Logs "LOGOUT" audit entry
2. Clears `current_user` dictionary
3. Returns to login screen

---

### Student Management Functions

#### 18. `add_student()`
**Purpose**: Create new student record

```python
def add_student():
```

**Input Required**:
- PRN (validated)
- Password
- Name
- Department

**Operation**:
1. Validates PRN format
2. Hashes password
3. Inserts into `students` table
4. Logs "ADD_STUDENT" audit entry

**Constraints**:
- PRN must be valid format
- All fields required
- PRN must be unique

---

#### 19. `view_students()`
**Purpose**: Display all students

```python
def view_students():
```

**Query**: Selects all students with all details

**Display Columns**:
- PRN
- Name
- Department
- Rolling Marks
- Active (yes/no)
- Enrolled At

---

#### 20. `search_by_dept()`
**Purpose**: Find students by department

```python
def search_by_dept():
```

**Input**: Department name

**Query**: Case-insensitive department search

**Display Columns**:
- PRN
- Name
- Department
- Marks
- Enrolled At

**Sorting**: By marks (DESC) then name (ASC)

---

#### 21. `update_student()`
**Purpose**: Modify student profile

```python
def update_student():
```

**Input Required**:
- Student PRN

**Modifiable Fields**:
- Name
- Department
- Active status

**Features**:
- Shows current values
- Optional fields (blank to skip)
- Logs "UPDATE_STUDENT" audit entry

---

#### 22. `delete_student()`
**Purpose**: Remove student account

```python
def delete_student():
```

**Input Required**:
- Student PRN
- Confirmation ("DELETE")

**Operation**:
1. Prompts for confirmation
2. Cascades deletion to related records
3. Logs "DELETE_STUDENT" audit entry

**Cascade**:
- Deletes from `student_subjects`
- Deletes from `attendance`

---

#### 23. `view_own_record()`
**Purpose**: Student views their academic record (Student Portal)

```python
def view_own_record():
```

**Restrictions**: Only students can access

**Displays**:
1. **Profile**:
   - PRN
   - Name
   - Department
   - Rolling Average Score

2. **Subject Scores**:
   - Subject Code
   - Subject Name
   - Marks Awarded

3. **Attendance Record**:
   - Subject Code
   - Subject Name
   - Total Classes / Attended
   - Percentage

---

### Analytics Functions

#### 24. `dashboard()`
**Purpose**: Display overall system statistics

```python
def dashboard():
```

**Statistics Displayed**:
1. **Student Count**: Total students in system
2. **Average Marks**: System-wide average
3. **Highest Mark**: Best student score
4. **Lowest Mark**: Worst student score
5. **Grade Distribution**:
   - Count of A (90-100)
   - Count of B (75-89)
   - Count of C (60-74)
   - Count of D (40-59)
   - Count of F (<40)

---

#### 25. `view_analytics()`
**Purpose**: Department performance analytics

```python
def view_analytics():
```

**Display Columns**:
- Department
- Total Students
- Average Marks
- Highest Score
- Lowest Score

**Sorted By**: Department name (ASC)

---

#### 26. `marks_distribution()`
**Purpose**: Grade band distribution report

```python
def marks_distribution():
```

**Display Columns**:
- Grade Band (A/B/C/D/F)
- Student Count

**Grading Bands**:
- A (90-100)
- B (75-89)
- C (60-74)
- D (40-59)
- F (<40)

---

#### 27. `show_top_performers()`
**Purpose**: Display top 10 students (score ≥ 60)

```python
def show_top_performers():
```

**Criteria**: marks >= 60

**Display Columns**:
- PRN
- Name
- Department
- Average Marks

**Sorted By**: Marks (DESC), Name (ASC)

---

#### 28. `dept_leaderboard()`
**Purpose**: Department ranking statistics

```python
def dept_leaderboard():
```

**Source**: `vw_department_leaderboard` view

**Display Columns**:
- Department
- Enrolled Students
- Average Marks
- Highest Mark
- Lowest Mark

---

#### 29. `add_bonus_marks()`
**Purpose**: Award bonus marks to department

```python
def add_bonus_marks():
```

**Input Required**:
- Department Name
- Bonus Marks (0-100)

**Operation**:
1. Updates all students in department
2. Caps marks at 100 (using LEAST function)
3. Reports how many students affected
4. Logs action with bonus amount

---

#### 30. `export_high_performers()`
**Purpose**: Export above-average students to CSV

```python
def export_high_performers():
```

**Export Criteria**: marks > system average

**Export Columns**:
- PRN
- Name
- Department
- Rolling Average

**File Format**: CSV (comma-separated values)

**Filename Format**: `high_performers_YYYYMMDD_HHMMSS.csv`

---

### User Management Functions

#### 31. `create_user()`
**Purpose**: Create admin/faculty/student accounts

```python
def create_user():
```

**Input Required**:
- Role (admin/faculty/student)
- PRN (for faculty/student) or Username (for admin)
- Password
- Name
- Department

**Operation**:
1. Validates role
2. Validates PRN if applicable
3. Hashes password
4. Inserts into appropriate table
5. Logs "CREATE_USER_ACCOUNT"

---

#### 32. `list_users()`
**Purpose**: Display all system accounts

```python
def list_users():
```

**Displays Three Tables**:

1. **Admins** (from `users`):
   - Username
   - Role
   - Status (active/disabled)

2. **Faculty** (from `faculty`):
   - PRN
   - Name
   - Department
   - Status

3. **Students** (from `students`):
   - PRN
   - Name
   - Department
   - Status

---

#### 33. `toggle_user()`
**Purpose**: Enable/disable user accounts

```python
def toggle_user():
```

**Input Required**:
- User Role
- Username/PRN

**Operation**:
1. Toggles `is_active` field
2. Logs action

**Safety**: Cannot disable own admin account

---

#### 34. `create_mysql_users()`
**Purpose**: Grant database privileges to app users

```python
def create_mysql_users():
```

**Creates Three MySQL Users**:

1. **spa_admin**: Full CRUD on all tables
2. **spa_faculty**: Limited access for faculty operations
3. **spa_student**: Read-only access to view data

**Permissions Granted**:
- SELECT, INSERT, UPDATE, DELETE as appropriate
- Table-level access control
- View access
- Audit log writing

---

#### 35. `view_audit_log()`
**Purpose**: Display security audit trail (last 30 entries)

```python
def view_audit_log():
```

**Display Columns**:
- ID
- Action
- Details
- Timestamp

**Sorted By**: Timestamp (DESC), then ID (DESC)

**Limit**: Last 30 entries only

---

### Academic Management Functions

#### 36. `admin_manage_academics()`
**Purpose**: Admin menu for academic operations

```python
def admin_manage_academics():
```

**Sub-functions**:
1. Create Subject
2. Enroll Student in Subject
3. Assign Faculty to Subject
4. Unenroll Student
5. Unassign Faculty
6. View Subjects Directory & Assignments

---

#### 37. `faculty_assigned_subjects()`
**Purpose**: Faculty views their assigned subjects

```python
def faculty_assigned_subjects():
```

**Displays**:
- Subject ID
- Subject Code
- Subject Name
- Batch

**From Tables**: `subjects` + `faculty_subjects` JOIN

---

#### 38. `faculty_update_marks()`
**Purpose**: Faculty submits student subject grades

```python
def faculty_update_marks():
```

**Process**:
1. Input Subject ID
2. Verify faculty is assigned to subject
3. Display enrolled students
4. Input student PRN
5. Input marks (0-100)
6. Updates `student_subjects.marks`
7. Recalculates rolling average
8. Logs "FACULTY_UPDATE_MARKS"

---

#### 39. `faculty_manage_attendance()`
**Purpose**: Faculty menu for attendance operations

```python
def faculty_manage_attendance():
```

**Sub-operations**:

1. **Mark Attendance (Roll Call)**:
   - Input Subject ID
   - Input Date (defaults to today)
   - List enrolled students
   - Mark each as Present/Absent
   - Saves to `attendance` table

2. **View Attendance History**:
   - Input Subject ID
   - Shows attendance summary by date
   - Columns: Date, Present Count, Absent Count, Total

---

### Menu Functions

#### 40. `menu_admin()`
**Purpose**: Admin dashboard menu loop

```python
def menu_admin():
```

**Features**:
- Displays admin welcome message
- 18 menu options
- Loops until logout
- Clears screen before each operation
- Waits for Enter after each operation

---

#### 41. `menu_faculty()`
**Purpose**: Faculty portal menu loop

```python
def menu_faculty():
```

**Features**:
- Displays faculty welcome message
- 6 menu options
- Loops until logout
- Includes subject management and attendance

---

#### 42. `menu_student()`
**Purpose**: Student portal menu loop

```python
def menu_student():
```

**Features**:
- Displays student welcome message
- 3 menu options (read-only)
- Loops until logout
- View own record, leaderboard, top performers

---

### Main Functions

#### 43. `main()`
**Purpose**: Application entry point

```python
def main():
```

**Operation**:
1. Calls `ensure_database_setup()`
2. Infinite loop for login
3. Routes to appropriate menu based on role
4. Handles KeyboardInterrupt (Ctrl+C)

---

#### 44. `if __name__ == "__main__"`
**Purpose**: Script execution handler

```python
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting Student Performance Analyzer...")
        sys.exit(0)
```

**Features**:
- Graceful exit on Ctrl+C
- Exit message

---

## Database Queries

All SQL queries executed by the system:

### Authentication Queries

#### Query 1: Admin Login
```sql
SELECT id, username, password_hash, role, is_active 
FROM users 
WHERE username = ?
```

---

#### Query 2: Faculty Login
```sql
SELECT prn, name, password_hash, is_active 
FROM faculty 
WHERE prn = ?
```

---

#### Query 3: Student Login
```sql
SELECT prn, name, password_hash, is_active 
FROM students 
WHERE prn = ?
```

---

### Student Management Queries

#### Query 4: Add Student
```sql
INSERT INTO students (prn, password_hash, name, department) 
VALUES (?, ?, ?, ?)
```

---

#### Query 5: View All Students
```sql
SELECT prn, name, department, marks, is_active, enrolled_at 
FROM students
```

---

#### Query 6: Search by Department
```sql
SELECT prn, name, department, marks, enrolled_at 
FROM students 
WHERE LOWER(department) = LOWER(?) 
ORDER BY marks DESC, name
```

---

#### Query 7: Update Student
```sql
UPDATE students 
SET name = ?, department = ?, is_active = ? 
WHERE prn = ?
```

---

#### Query 8: Delete Student
```sql
DELETE FROM students 
WHERE prn = ?
```

---

### Analytics Queries

#### Query 9: Dashboard Statistics
```sql
SELECT COUNT(*), AVG(marks), MAX(marks), MIN(marks) 
FROM students
```

---

#### Query 10: Grade Distribution
```sql
SELECT
    SUM(CASE WHEN marks >= 90 THEN 1 ELSE 0 END) AS A,
    SUM(CASE WHEN marks >= 75 AND marks < 90 THEN 1 ELSE 0 END) AS B,
    SUM(CASE WHEN marks >= 60 AND marks < 75 THEN 1 ELSE 0 END) AS C,
    SUM(CASE WHEN marks >= 40 AND marks < 60 THEN 1 ELSE 0 END) AS D,
    SUM(CASE WHEN marks < 40 THEN 1 ELSE 0 END) AS F
FROM students
```

---

#### Query 11: Department Analytics
```sql
SELECT department, COUNT(*) AS students, AVG(marks), MAX(marks), MIN(marks)
FROM students
GROUP BY department
ORDER BY department
```

---

#### Query 12: Grade Band Distribution
```sql
SELECT
    CASE
        WHEN marks >= 90 THEN 'A (90-100)'
        WHEN marks >= 75 THEN 'B (75-89)'
        WHEN marks >= 60 THEN 'C (60-74)'
        WHEN marks >= 40 THEN 'D (40-59)'
        ELSE 'F (<40)'
    END AS grade_band,
    COUNT(*) AS student_count
FROM students
GROUP BY grade_band
ORDER BY MIN(marks) DESC
```

---

#### Query 13: Top Performers
```sql
SELECT prn, name, department, marks 
FROM students 
WHERE marks >= 60 
ORDER BY marks DESC, name 
LIMIT 10
```

---

#### Query 14: Department Leaderboard
```sql
SELECT department, total_students, average_marks, highest_marks, lowest_marks 
FROM vw_department_leaderboard
```

---

### Subject & Grade Management Queries

#### Query 15: Create Subject
```sql
INSERT INTO subjects (code, name, batch) 
VALUES (?, ?, ?)
```

---

#### Query 16: Enroll Student
```sql
INSERT INTO student_subjects (subject_id, student_prn) 
VALUES (?, ?)
```

---

#### Query 17: Assign Faculty
```sql
INSERT INTO faculty_subjects (faculty_prn, subject_id) 
VALUES (?, ?)
```

---

#### Query 18: Update Student Marks
```sql
UPDATE student_subjects 
SET marks = ? 
WHERE subject_id = ? AND student_prn = ?
```

---

#### Query 19: Calculate Rolling Average
```sql
SELECT AVG(marks) as avg_marks 
FROM student_subjects 
WHERE student_prn = ? AND marks IS NOT NULL
```

---

#### Query 20: Update Overall Student Marks
```sql
UPDATE students 
SET marks = ? 
WHERE prn = ?
```

---

### Student View Queries

#### Query 21: Get Student Profile
```sql
SELECT prn, name, department, marks 
FROM students 
WHERE prn = ?
```

---

#### Query 22: Student Subject Scores
```sql
SELECT s.code, s.name, ss.marks
FROM student_subjects ss
JOIN subjects s ON s.id = ss.subject_id
WHERE ss.student_prn = ?
ORDER BY s.code
```

---

#### Query 23: Student Attendance
```sql
SELECT s.code, s.name,
       COUNT(a.id) AS total_classes,
       SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) AS attended,
       ROUND(COALESCE(SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(a.id), 0), 0), 2) AS percentage
FROM student_subjects ss
JOIN subjects s ON s.id = ss.subject_id
LEFT JOIN attendance a ON a.subject_id = ss.subject_id AND a.student_prn = ss.student_prn
WHERE ss.student_prn = ?
GROUP BY s.id, s.code, s.name
ORDER BY s.code
```

---

### Attendance Queries

#### Query 24: Mark Attendance
```sql
INSERT INTO attendance (subject_id, student_prn, date, status) 
VALUES (?, ?, ?, ?) 
ON DUPLICATE KEY UPDATE status = VALUES(status)
```

---

#### Query 25: View Attendance History
```sql
SELECT date,
       SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) AS present_count,
       SUM(CASE WHEN status = 'Absent' THEN 1 ELSE 0 END) AS absent_count,
       COUNT(*) AS total_count
FROM attendance
WHERE subject_id = ?
GROUP BY date
ORDER BY date DESC
```

---

### Audit & Export Queries

#### Query 26: Log Audit Entry
```sql
INSERT INTO audit_log (user_id, action, details) 
VALUES (?, ?, ?)
```

---

#### Query 27: View Audit Log
```sql
SELECT id, action, details, timestamp 
FROM audit_log 
ORDER BY timestamp DESC, id DESC 
LIMIT 30
```

---

#### Query 28: Export High Performers
```sql
SELECT prn, name, department, marks
FROM students
WHERE marks > (SELECT AVG(marks) FROM students)
ORDER BY marks DESC, name
```

---

#### Query 29: Award Bonus Marks
```sql
UPDATE students 
SET marks = LEAST(marks + ?, 100) 
WHERE LOWER(department) = LOWER(?)
```

---

### User Management Queries

#### Query 30: Create Admin User
```sql
INSERT INTO users (username, password_hash, role) 
VALUES (?, ?, ?)
```

---

#### Query 31: List Admin Users
```sql
SELECT username, role, IF(is_active, 'active', 'disabled') 
FROM users
```

---

#### Query 32: Toggle User Status
```sql
UPDATE users 
SET is_active = NOT is_active 
WHERE username = ?
```

---

#### Query 33: Faculty Assigned Subjects
```sql
SELECT s.id, s.code, s.name, s.batch 
FROM subjects s
JOIN faculty_subjects fs ON fs.subject_id = s.id
WHERE fs.faculty_prn = ?
ORDER BY s.code
```

---

## User Workflows

### Workflow 1: Admin - Adding a New Student

1. **Start Application**
   ```bash
   python PRN_analyzer.py
   # or
   PRN_spa.exe
   ```

2. **Login**
   - Username: `admin`
   - Password: `admin123`

3. **Navigate Menu**
   - Select: "2. Add Student Record"

4. **Enter Details**
   - PRN: `25007011001` (valid format)
   - Password: `student123`
   - Name: `John Doe`
   - Department: `Computer Science`

5. **Confirmation**
   - System displays: "[OK] Student added successfully."
   - Audit log recorded

---

### Workflow 2: Faculty - Recording Attendance

1. **Login**
   - PRN: `25006011001`
   - Password: `faculty123`

2. **Navigate Menu**
   - Select: "3. Manage Subject Attendance sheets"

3. **Mark Attendance**
   - Select: "1. Roll Call (Mark Attendance Sheet)"
   - Input Subject ID
   - Input Date (or blank for today)
   - For each student, mark P (Present) or A (Absent)

4. **Confirmation**
   - Records saved to `attendance` table
   - Audit logged

---

### Workflow 3: Student - Viewing Academic Record

1. **Login**
   - PRN: `25007011001`
   - Password: `student123`

2. **Navigate Menu**
   - Select: "1. View My Academic Record & Transcripts"

3. **View Information**
   - Personal profile displayed
   - All enrolled subjects with marks
   - Attendance percentage per subject

---

### Workflow 4: Faculty - Updating Student Marks

1. **Login as Faculty**

2. **Navigate Menu**
   - Select: "2. Enter / Update Student Marks"

3. **Process**
   - Input Subject ID
   - System displays enrolled students
   - Input student PRN to update
   - Input marks (0-100)

4. **Result**
   - Student marks updated
   - Student rolling average recalculated
   - Audit logged

---

### Workflow 5: Admin - Analyzing Performance

1. **Login as Admin**

2. **View Dashboard**
   - Select: "1. Live Analytics Dashboard"
   - View total students, avg, min, max
   - View grade distribution

3. **Department Analytics**
   - Select: "7. Department Performance Analytics"
   - View performance by department

4. **Export High Performers**
   - Select: "12. Export High Performers to CSV"
   - Creates CSV file with above-average students

---

## Security & Audit

### Password Security

**Hashing Algorithm**: SHA256

**Process**:
1. User enters password
2. Plain text converted to bytes
3. SHA256 hash computed
4. 64-character hex digest stored
5. Never stored/transmitted as plain text

**Example**:
```python
password = "admin123"
hashed = hashlib.sha256(password.encode("utf-8")).hexdigest()
# Result: 240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9
```

---

### Account Status

All user tables have `is_active` field:
- `TRUE`: Account active, can login
- `FALSE`: Account disabled, login denied

**Disable Mechanism**:
- Admin can toggle status via "15. Toggle User Active status"
- Prevents unauthorized access
- Audit logged

---

### Session Management

**Global Session Variable**:
```python
current_user = {
    "id": None,           # Admin user ID
    "username": None,     # Display name
    "role": None,         # admin/faculty/student
    "student_id": None    # PRN for non-admin
}
```

**Session Lifecycle**:
1. Created on successful login
2. Used to enforce permissions
3. Cleared on logout

---

### Audit Logging

**Tracked Actions**:

| Action | Type | Details |
|--------|------|---------|
| LOGIN_SUCCESS | Authentication | User and role |
| LOGIN_FAILED | Authentication | Username attempted |
| LOGOUT | Authentication | User logged out |
| ADD_STUDENT | Student Mgmt | PRN, Name, Department |
| UPDATE_STUDENT | Student Mgmt | Updated fields |
| DELETE_STUDENT | Student Mgmt | Student PRN |
| CREATE_USER_ACCOUNT | User Mgmt | Role and username |
| TOGGLE_USER_STATUS | User Mgmt | User toggled |
| ENROLL_STUDENT | Academic | Subject and student |
| UNENROLL_STUDENT | Academic | Subject and student |
| ASSIGN_FACULTY | Academic | Faculty and subject |
| UNASSIGN_FACULTY | Academic | Faculty and subject |
| FACULTY_UPDATE_MARKS | Grading | Subject, student, marks |
| SAVE_ATTENDANCE | Attendance | Subject and date |
| AWARD_BONUS | Analytics | Department and amount |
| EXPORT_HIGH_PERFORMERS | Export | Record count |

**Log Retention**: 30 most recent entries displayed (all stored)

---

### Database-Level Security

**Constraints Enforced**:
- PRN format validation (REGEXP constraint)
- Marks range (0-100)
- Password hash length (64 chars)
- Username minimum length (3 chars)
- Unique constraints on PRN, username

**Foreign Keys**:
- Referential integrity maintained
- Cascading deletes for related records
- Prevents orphaned records

---

## Troubleshooting

### Issue 1: "Cannot connect to database"

**Causes**:
- MySQL server not running
- Wrong host/password in DB_CONFIG
- Database doesn't exist

**Solutions**:
1. Start MySQL Server:
   ```bash
   # Windows
   net start MySQL80
   # Linux
   sudo service mysql start
   ```

2. Verify credentials:
   ```bash
   mysql -h localhost -u root -p
   ```

3. Check DB_CONFIG settings

4. Run application again (auto-creates DB)

---

### Issue 2: "Invalid PRN format"

**Cause**: PRN doesn't match required format

**Valid Format**: `YY0AABBCRRR` (11 digits)
- YY: 25, 26, or 27
- A: 06 or 07
- B: 01-06
- C: 1, 2, or 3
- R: 000-999

**Example Valid PRN**: `25007011001`

**Invalid Examples**:
- `2507011001` (missing digit)
- `25008011001` (AA not 06-07)
- `25007071001` (BB not 01-06)

---

### Issue 3: "Duplicate entry for key"

**Cause**: Trying to create duplicate record

**Examples**:
- PRN already exists in system
- Subject code already in batch
- Duplicate attendance entry for same day

**Solution**:
- Use different PRN
- Use different subject code
- Update existing record instead of inserting

---

### Issue 4: "Access denied for user"

**Cause**: MySQL permissions issue

**Solution**:
1. Create MySQL application users:
   - Admin menu: "16. Create MySQL Application Users"
   - Enter password for app users
   - Type "CONFIRM" to execute

2. Or manually grant privileges:
   ```sql
   GRANT SELECT, INSERT, UPDATE, DELETE ON spa_enhanced_db.* TO 'spa_admin'@'localhost' IDENTIFIED BY 'password';
   FLUSH PRIVILEGES;
   ```

---

### Issue 5: "No records found"

**Cause**: Query returned empty result

**Solution**:
- Check if records exist
- Verify search criteria
- Use "View All" option
- Add records if necessary

---

### Issue 6: "Cannot disable own account"

**Cause**: Admin trying to disable self

**Solution**:
- Ask another admin to disable account
- Use different admin account

---

### Issue 7: "Marks calculation showing 0"

**Cause**: No subject marks entered

**Solution**:
1. Faculty updates student subject marks
2. Faculty menu: "2. Enter / Update Student Marks"
3. Mark updates for at least one subject
4. System recalculates rolling average

---

### Issue 8: "Attendance not saving"

**Cause**: Not assigned to subject or permission denied

**Solution**:
1. Verify faculty is assigned to subject
2. Admin: Menu "18. Manage Academic Subjects"
3. Assign faculty to subject
4. Try attendance recording again

---

## Performance Considerations

### Database Indexing

**Indexes Created**:
- `users.username` (UNIQUE)
- `students.prn` (PRIMARY KEY)
- `faculty.prn` (PRIMARY KEY)
- `subjects.id` (PRIMARY KEY)
- `attendance.subject_id, student_prn, date` (UNIQUE)

---

### Query Optimization

**Slow Query Scenarios**:
1. **Large student base** (>10,000):
   - Dashboard aggregations may be slow
   - Consider materialized view

2. **High attendance volume**:
   - Attendance view might be slow
   - Add index on (student_prn, date)

3. **Department analytics**:
   - GROUP BY operations are efficient
   - Already indexed properly

---

### Recommendations

1. **Backup Database Regularly**:
   ```bash
   mysqldump -u root -p spa_enhanced_db > backup.sql
   ```

2. **Monitor Audit Log Size**:
   - Archive old audit logs periodically
   - Currently displays last 30 only

3. **Optimize CSV Exports**:
   - May be slow with 100K+ records
   - Consider pagination for large exports

---

## Maintenance

### Database Cleanup

**Remove Inactive Users**:
```sql
-- View inactive accounts
SELECT * FROM students WHERE is_active = FALSE;
SELECT * FROM faculty WHERE is_active = FALSE;
SELECT * FROM users WHERE is_active = FALSE;

-- Archive or delete as needed
DELETE FROM students WHERE is_active = FALSE AND enrolled_at < DATE_SUB(NOW(), INTERVAL 1 YEAR);
```

---

### Backup & Recovery

**Backup Command**:
```bash
mysqldump -u root -p spa_enhanced_db > spa_enhanced_db_$(date +%Y%m%d_%H%M%S).sql
```

**Restore Command**:
```bash
mysql -u root -p spa_enhanced_db < spa_enhanced_db_20260522_120000.sql
```

---

## Conclusion

The Student Performance Analyzer is a comprehensive system for managing academic records. This manual covers:

✅ System architecture and design  
✅ Complete database schema with relationships  
✅ All functions and methods with parameters  
✅ SQL queries and their purposes  
✅ User workflows and best practices  
✅ Security and audit mechanisms  
✅ Troubleshooting common issues  

For further development or customization, refer to specific function documentation above.

---

**Support & Questions**:
- Review the audit logs for system activity
- Check constraints and validation rules
- Refer to database views for complex queries
- Use test data for development

**Last Updated**: May 22, 2026  
**System Version**: 1.0
