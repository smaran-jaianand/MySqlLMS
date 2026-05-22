# Student Performance Analyzer (SPA) — Sample Credentials & Test Data

This file contains the credentials, relational mappings, and step-by-step walkthroughs for the core academic workflows (functions) inside the **SPA** database (`spa_enhanced_db`). You can use these accounts to login and test different roles (Admin, Faculty, Students) in the terminal application or run raw SQL queries directly.

---

## 1. System Administrative Login
Admins have full CRUD privileges for students, faculty, subjects, and audit logs.

* **Username**: `admin`
* **Password**: `admin123`

---

## 2. Faculty Logins (Professors)
Faculty can assign marks for enrolled students, take attendance, and view performance logs for their assigned subjects.
* **Default Password**: `password123` for all faculty accounts.

| PRN (Username) | Professor Name | Department | Assigned Subject Code & Name |
| :--- | :--- | :--- | :--- |
| **`25006011001`** | Dr. Rajesh Kumar | Computer Science | `CS101` (DSA), `CS102` (DBMS), `CS104` (Computer Networks) |
| **`25007021002`** | Prof. Sunita Sharma | Information Technology | `IT101` (Web Development) |
| **`26006031003`** | Dr. Amit Patel | Computer Science | `CS103` (Operating Systems) |

---

## 3. Student Logins
Students can view their own profiles, grade cards (transcripts), subject-wise performance charts, and attendance statistics.
* **Default Password**: `student123` for all student accounts.

| PRN (Username) | Student Name | Department | Enrolled Subjects & Initial Marks |
| :--- | :--- | :--- | :--- |
| **`25006011101`** | Rohan Verma | Computer Science | `CS101`: 85.00, `CS102`: 90.00, `CS104`: 88.00 (Avg: 87.67) |
| **`25006011102`** | Priya Nair | Computer Science | `CS101`: 92.00, `CS102`: 88.00, `CS104`: 94.00 (Avg: 91.33) |
| **`25007021201`** | Aarav Mehta | Information Technology | `IT101`: 78.00 (Avg: 78.00) |
| **`25007021202`** | Sneha Reddy | Information Technology | `IT101`: 84.00 (Avg: 84.00) |
| **`26006031301`** | Vikram Singh | Computer Science | `CS103`: 72.00 (Avg: 72.00) |

---

## 4. Subject Directory & Batches

| ID | Subject Code | Subject Name | Target Batch | Assigned Faculty |
| :--- | :--- | :--- | :--- | :--- |
| **1** | `CS101` | Data Structures & Algorithms | `Batch-A` | Dr. Rajesh Kumar |
| **2** | `CS102` | Database Management Systems | `Batch-A` | Dr. Rajesh Kumar |
| **3** | `IT101` | Web Development | `Batch-B` | Prof. Sunita Sharma |
| **4** | `CS103` | Operating Systems | `Batch-C` | Dr. Amit Patel |
| **5** | `CS104` | Computer Networks | `Batch-A` | Dr. Rajesh Kumar |

---

## 5. Pre-populated Student Attendance Records
The database comes pre-filled with attendance sheets for May 15, May 18, May 20, and May 22, 2026.

| Student Name | Subject Code | Date | Attendance Status |
| :--- | :--- | :--- | :--- |
| Rohan Verma | `CS101` | 2026-05-15 | Present |
| Rohan Verma | `CS101` | 2026-05-18 | Present |
| Rohan Verma | `CS101` | 2026-05-20 | Absent |
| Rohan Verma | `CS102` | 2026-05-15 | Present |
| Rohan Verma | `CS102` | 2026-05-18 | Present |
| Rohan Verma | `CS104` | 2026-05-22 | Present |
| Priya Nair | `CS101` | 2026-05-15 | Present |
| Priya Nair | `CS101` | 2026-05-18 | Present |
| Priya Nair | `CS101` | 2026-05-20 | Present |
| Priya Nair | `CS102` | 2026-05-15 | Present |
| Priya Nair | `CS102` | 2026-05-18 | Absent |
| Priya Nair | `CS104` | 2026-05-22 | Absent |
| Aarav Mehta | `IT101` | 2026-05-15 | Present |
| Aarav Mehta | `IT101` | 2026-05-18 | Present |
| Sneha Reddy | `IT101` | 2026-05-15 | Present |
| Sneha Reddy | `IT101` | 2026-05-18 | Absent |
| Vikram Singh | `CS103` | 2026-05-15 | Present |

---

## 6. Walkthrough of Core Functions (Academics & Linkages)

This section demonstrates how to use the built-in application menus or raw SQL statements to perform the core administrative and faculty linkages.

### Function 1: Assigning / Creating a Subject
Allows system administrators to add a course subject to the directory.

* **CLI Workflow (Admin Role)**:
  1. Log in with Admin credentials (`admin` / `admin123`).
  2. Choose Option `18` (`Manage Academic Subjects & Enrollments`).
  3. Select Sub-option `1` (`Create Subject`).
  4. Input parameters:
     - `Subject Code`: `CS104`
     - `Subject Name`: `Computer Networks`
     - `Batch`: `Batch-A`
* **Underlying SQL Query**:
  ```sql
  INSERT INTO subjects (code, name, batch) VALUES ('CS104', 'Computer Networks', 'Batch-A');
  ```

---

### Function 2: Assigning Faculty to a Subject
Binds a professor to a class/subject, authorizing them to grade enrolled students and mark attendance.

* **CLI Workflow (Admin Role)**:
  1. Under Option `18` (`Academic Management`), select Sub-option `3` (`Assign Faculty to Subject`).
  2. Input parameters:
     - `Faculty PRN`: `25006011001`
     - `Subject ID`: `5` (The ID corresponding to `CS104`)
* **Underlying SQL Query**:
  ```sql
  INSERT INTO faculty_subjects (faculty_prn, subject_id) VALUES ('25006011001', 5);
  ```

---

### Function 3: Enrolling Students in a Subject
Enrolls a student in a course subject, mapping them to the grading sheets and attendance rosters.

* **CLI Workflow (Admin Role)**:
  1. Under Option `18` (`Academic Management`), select Sub-option `2` (`Enroll Student in Subject`).
  2. Input parameters:
     - `Subject ID`: `5`
     - `Student PRN`: `25006011101`
  3. *(Repeat for PRN `25006011102`)*
* **Underlying SQL Query**:
  ```sql
  INSERT INTO student_subjects (subject_id, student_prn) VALUES (5, '25006011101');
  INSERT INTO student_subjects (subject_id, student_prn) VALUES (5, '25006011102');
  ```

---

### Function 4: Submitting & Updating Student Marks
Authorized faculty professors can enter or update grades for students enrolled in their assigned subjects. Once updated, the student's rolling average across all enrolled subjects is automatically recalculated.

* **CLI Workflow (Faculty Role)**:
  1. Log in with Faculty credentials (e.g., `25006011001` / `password123`).
  2. Select Option `2` (`Enter / Update Student Marks`).
  3. Input parameters:
     - `Subject ID`: `5`
     - `Student PRN`: `25006011101`
     - `Marks (0-100)`: `88`
* **Underlying SQL Query**:
  ```sql
  -- Update marks in junction table
  UPDATE student_subjects SET marks = 88.00 WHERE subject_id = 5 AND student_prn = '25006011101';

  -- Recalculate student overall rolling average
  UPDATE students SET marks = (
      SELECT COALESCE(AVG(marks), 0.00) 
      FROM student_subjects 
      WHERE student_prn = '25006011101' AND marks IS NOT NULL
  ) WHERE prn = '25006011101';
  ```

---

### Function 5: Marking Attendance (Roll Call Sheet)
Faculty can record the daily attendance roll call for all students enrolled in a subject.

* **CLI Workflow (Faculty Role)**:
  1. Select Option `3` (`Manage Subject Attendance sheets`).
  2. Select Sub-option `1` (`Roll Call`).
  3. Input parameters:
     - `Subject ID`: `5`
     - `Date`: `2026-05-22` (or press Enter for today's date)
     - Mark status for each student in the list (`P` for Present, `A` for Absent).
* **Underlying SQL Query**:
  ```sql
  -- Upsert statement ensures attendance can be revised if marked incorrectly
  INSERT INTO attendance (subject_id, student_prn, date, status) 
  VALUES (5, '25006011101', '2026-05-22', 'Present')
  ON DUPLICATE KEY UPDATE status = VALUES(status);
  ```
