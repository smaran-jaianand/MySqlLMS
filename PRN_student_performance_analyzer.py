# Student Performance Analyzer (CLI Version)
# File name: PRN_student_performance_analyzer.py (renamed to PRN_analyzer.py for deliverables)

import csv
import datetime as dt
import hashlib
import os
import sys
import getpass
from decimal import Decimal

try:
    import mysql.connector
    from mysql.connector import Error
except ImportError:
    mysql = None
    Error = Exception

# ============================
# Database Connection Function
# ============================
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "mysql",  # Change if needed
    "database": "spa_enhanced_db"
}

# ============================
# Global session — populate on successful login
# ============================
current_user = {
    "id": None, 
    "username": None,
    "role": None, 
    "student_id": None
}

import re
PRN_PATTERN = re.compile(r"^(25|26|27)0(06|07)(01|02|03|04|05|06)[123][0-9]{3}$")

def get_connection():
    try:
        if mysql is not None:
            return mysql.connector.connect(
                host=DB_CONFIG["host"],
                user=DB_CONFIG["user"],
                password=DB_CONFIG["password"],
                database=DB_CONFIG["database"]
            )
    except Exception as exc:
        if "caching_sha2_password" not in str(exc) and "Authentication plugin" not in str(exc):
            raise exc
    
    # Fallback to pymysql which natively supports caching_sha2_password without binary dependencies
    import pymysql
    return pymysql.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"]
    )

def get_base_connection():
    try:
        if mysql is not None:
            return mysql.connector.connect(
                host=DB_CONFIG["host"],
                user=DB_CONFIG["user"],
                password=DB_CONFIG["password"]
            )
    except Exception as exc:
        if "caching_sha2_password" not in str(exc) and "Authentication plugin" not in str(exc):
            raise exc

    # Fallback to pymysql which natively supports caching_sha2_password without binary dependencies
    import pymysql
    return pymysql.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"]
    )

def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def pause():
    input("\nPress Enter to continue...")

def print_title(title):
    print("\n" + "=" * 78)
    print(title.center(78))
    print("=" * 78)

def print_message(message, kind="info"):
    labels = {"info": "INFO", "success": "OK", "error": "ERROR", "warn": "WARN"}
    print(f"[{labels.get(kind, 'INFO')}] {message}")

def normalize(value):
    if isinstance(value, Decimal):
        return f"{float(value):.2f}"
    if isinstance(value, dt.datetime):
        return value.strftime("%Y-%m-%d %H:%M")
    if isinstance(value, dt.date):
        return value.strftime("%Y-%m-%d")
    if value is None:
        return ""
    return str(value)

def print_table(headers, rows):
    rows = [tuple(normalize(value) for value in row) for row in rows]
    widths = [len(header) for header in headers]
    for row in rows:
        for index, value in enumerate(row):
            widths[index] = max(widths[index], len(value))
    
    line = "+-" + "-+-".join("-" * width for width in widths) + "-+"
    header_row = "| " + " | ".join(headers[i].ljust(widths[i]) for i in range(len(headers))) + " |"
    print(line)
    print(header_row)
    print(line)
    if not rows:
        print("| " + "No records found".center(len(header_row) - 4) + " |")
    else:
        for row in rows:
            print("| " + " | ".join(row[i].ljust(widths[i]) for i in range(len(headers))) + " |")
    print(line)

def input_int(prompt, minimum=None, maximum=None):
    while True:
        try:
            inp = input(prompt).strip()
            if not inp:
                return None
            value = int(inp)
            if minimum is not None and value < minimum:
                print_message(f"Value must be at least {minimum}.", "warn")
                continue
            if maximum is not None and value > maximum:
                print_message(f"Value must be at most {maximum}.", "warn")
                continue
            return value
        except ValueError:
            print_message("Enter a valid whole number.", "warn")

def input_float(prompt, minimum=None, maximum=None):
    while True:
        try:
            inp = input(prompt).strip()
            if not inp:
                return None
            value = float(inp)
            if minimum is not None and value < minimum:
                print_message(f"Value must be at least {minimum}.", "warn")
                continue
            if maximum is not None and value > maximum:
                print_message(f"Value must be at most {maximum}.", "warn")
                continue
            return value
        except ValueError:
            print_message("Enter a valid number.", "warn")

def validate_prn(prn):
    prn = "".join(ch for ch in prn.strip() if ch.isdigit())
    if not PRN_PATTERN.fullmatch(prn):
        return None, "PRN must be 11 digits in YY0AABBCRRR format. Example: 25007011001."
    return prn, None

def log_audit(action, details=""):
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO audit_log (user_id, action, details) VALUES (%s, %s, %s)",
                    (current_user.get("id"), action, details[:1000])
                )
            conn.commit()
    except Exception as exc:
        pass

def update_overall_student_marks(student_prn):
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                # Calculate rolling average
                cursor.execute(
                    """
                    SELECT AVG(marks) as avg_marks 
                    FROM student_subjects 
                    WHERE student_prn = %s AND marks IS NOT NULL
                    """,
                    (student_prn,)
                )
                res = cursor.fetchone()
                avg_marks = res[0] if (res and res[0] is not None) else 0.00
                
                # Update students table
                cursor.execute(
                    "UPDATE students SET marks = %s WHERE prn = %s",
                    (avg_marks, student_prn)
                )
            conn.commit()
    except Exception as e:
        print_message(f"Failed to update overall student average: {e}", "warn")

# ============================
# Database Auto-Initialization
# ============================
def ensure_database_setup():
    try:
        conn = get_base_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SHOW DATABASES LIKE 'spa_enhanced_db'")
                db_exists = cursor.fetchone()
                
                if not db_exists:
                    print_message("Database 'spa_enhanced_db' not found. Automatically initializing database...", "info")
                    cursor.execute("CREATE DATABASE spa_enhanced_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
                
                cursor.execute("USE spa_enhanced_db;")
                
                # Check tables
                tables_exist = True
                try:
                    cursor.execute("SELECT COUNT(*) FROM users")
                except Exception:
                    tables_exist = False
                
                if not tables_exist:
                    print_message("Tables missing. Creating schema and views...", "info")
                    cursor.execute("""
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
                    """)
                    cursor.execute("""
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
                    """)
                    cursor.execute("""
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
                    """)
                    cursor.execute("""
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
                    """)
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS subjects (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            code VARCHAR(20) NOT NULL,
                            name VARCHAR(100) NOT NULL,
                            batch VARCHAR(50) NOT NULL,
                            UNIQUE(code, batch)
                        ) ENGINE=InnoDB;
                    """)
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS student_subjects (
                            subject_id INT NOT NULL,
                            student_prn CHAR(11) NOT NULL,
                            marks DECIMAL(5,2) DEFAULT NULL,
                            PRIMARY KEY (subject_id, student_prn),
                            FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
                            FOREIGN KEY (student_prn) REFERENCES students(prn) ON UPDATE CASCADE ON DELETE CASCADE,
                            CHECK (marks IS NULL OR (marks >= 0 AND marks <= 100))
                        ) ENGINE=InnoDB;
                    """)
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS faculty_subjects (
                            faculty_prn CHAR(11) NOT NULL,
                            subject_id INT NOT NULL,
                            PRIMARY KEY (faculty_prn, subject_id),
                            FOREIGN KEY (faculty_prn) REFERENCES faculty(prn) ON UPDATE CASCADE ON DELETE CASCADE,
                            FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
                        ) ENGINE=InnoDB;
                    """)
                    cursor.execute("""
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
                    """)
                    cursor.execute("""
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
                    """)
                    cursor.execute("""
                        CREATE OR REPLACE VIEW vw_department_leaderboard AS
                        SELECT department, COUNT(*) AS total_students, ROUND(AVG(marks), 2) AS average_marks,
                               MAX(marks) AS highest_marks, MIN(marks) AS lowest_marks
                        FROM students
                        GROUP BY department;
                    """)
                    
                    # Insert default admin user if not exists
                    cursor.execute("SELECT COUNT(*) AS c FROM users WHERE username = 'admin'")
                    res = cursor.fetchone()
                    if res[0] == 0:
                        cursor.execute("""
                            INSERT INTO users (username, password_hash, role) 
                            VALUES ('admin', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'admin');
                        """)
                    conn.commit()
                    print_message("Database schema successfully auto-initialized!", "success")
        finally:
            conn.close()
    except Exception as e:
        print_message(f"Auto database setup check skipped or failed: {e}", "warn")

# ============================
# Login System
# ============================
def login():
    print_title("Student Performance Analyzer Login")
    username_or_prn = input("Username or PRN: ").strip()
    password = getpass.getpass("Password: ")

    try:
        # Check users table first (e.g. for Admin)
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id, username, password_hash, role, is_active FROM users WHERE username = %s",
                    (username_or_prn,)
                )
                user = cursor.fetchone()
                if user:
                    if user[2] == hash_password(password):
                        if not user[4]:
                            print_message("Account disabled.", "error")
                            return False
                        current_user.update({
                            "id": user[0],
                            "username": user[1],
                            "role": user[3],
                            "student_id": None
                        })
                        log_audit("LOGIN_SUCCESS", f"Admin '{user[1]}' logged in")
                        print_message(f"Welcome Admin, {user[1]}.", "success")
                        return True
                
                # Check faculty table (PRN)
                prn, err = validate_prn(username_or_prn)
                if not err:
                    cursor.execute(
                        "SELECT prn, name, password_hash, is_active FROM faculty WHERE prn = %s",
                        (prn,)
                    )
                    fac = cursor.fetchone()
                    if fac:
                        if fac[2] == hash_password(password):
                            if not fac[3]:
                                print_message("Account disabled.", "error")
                                return False
                            current_user.update({
                                "id": None,
                                "username": fac[1],
                                "role": "faculty",
                                "student_id": fac[0]
                            })
                            log_audit("LOGIN_SUCCESS", f"Faculty PRN '{fac[0]}' logged in")
                            print_message(f"Welcome Professor, {fac[1]}.", "success")
                            return True
                    
                    # Check students table (PRN)
                    cursor.execute(
                        "SELECT prn, name, password_hash, is_active FROM students WHERE prn = %s",
                        (prn,)
                    )
                    stud = cursor.fetchone()
                    if stud:
                        if stud[2] == hash_password(password):
                            if not stud[3]:
                                print_message("Account disabled.", "error")
                                return False
                            current_user.update({
                                "id": None,
                                "username": stud[1],
                                "role": "student",
                                "student_id": stud[0]
                            })
                            log_audit("LOGIN_SUCCESS", f"Student PRN '{stud[0]}' logged in")
                            print_message(f"Welcome Student, {stud[1]}.", "success")
                            return True

        print_message("Invalid credentials.", "error")
        log_audit("LOGIN_FAILED", f"Failed credentials for '{username_or_prn}'")
        return False
    except Exception as e:
        print_message(f"Login failed: {e}", "error")
        return False

def logout():
    log_audit("LOGOUT", f"{current_user.get('username')} logged out")
    print_message("Logged out successfully.", "success")
    current_user.update({"id": None, "username": None, "role": None, "student_id": None})

# ============================
# STUDENT CRUD
# ============================
def add_student():
    print_title("Add Student")
    prn = input("PRN (YY0AABBCRRR): ").strip()
    prn, error = validate_prn(prn)
    if error:
        print_message(error, "warn")
        return
    password = input("Password: ")
    name = input("Name: ").strip()
    department = input("Department: ").strip()
    if not name or not department or not password:
        print_message("All fields required.", "warn")
        return
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO students (prn, password_hash, name, department) VALUES (%s, %s, %s, %s)",
                    (prn, hash_password(password), name, department)
                )
            conn.commit()
        log_audit("ADD_STUDENT", f"Added student {prn} - {name} in {department}")
        print_message("Student added successfully.", "success")
    except Exception as exc:
        print_message(f"Could not add student: {exc}", "error")

def view_students():
    print_title("All Students")
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT prn, name, department, marks, is_active, enrolled_at FROM students")
                rows = cursor.fetchall()
                print_table(("PRN", "Name", "Department", "Rolling Marks", "Active", "Enrolled At"), rows)
    except Exception as exc:
        print_message(f"Could not load students: {exc}", "error")

def search_by_dept():
    print_title("Search by Department")
    department = input("Department: ").strip()
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT prn, name, department, marks, enrolled_at FROM students WHERE LOWER(department) = LOWER(%s) ORDER BY marks DESC, name",
                    (department,)
                )
                print_table(("PRN", "Name", "Department", "Marks", "Enrolled At"), cursor.fetchall())
    except Exception as exc:
        print_message(f"Search failed: {exc}", "error")

def update_student():
    print_title("Update Student Profile")
    prn = input("Student PRN to update: ").strip()
    prn, error = validate_prn(prn)
    if error:
        print_message(error, "warn")
        return
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT prn, name, department, is_active FROM students WHERE prn = %s", (prn,))
                student = cursor.fetchone()
                if not student:
                    print_message("Student not found.", "warn")
                    return
                
                print(f"Current Name: {student[1]}")
                name = input("New Name (leave blank to skip): ").strip() or student[1]
                print(f"Current Department: {student[2]}")
                dept = input("New Department (leave blank to skip): ").strip() or student[2]
                active_str = input("Is Active? (y/n, blank to skip): ").strip().lower()
                is_active = student[3]
                if active_str == "y":
                    is_active = True
                elif active_str == "n":
                    is_active = False
                
                cursor.execute(
                    "UPDATE students SET name = %s, department = %s, is_active = %s WHERE prn = %s",
                    (name, dept, is_active, prn)
                )
            conn.commit()
        log_audit("UPDATE_STUDENT", f"Updated student profile: {prn}")
        print_message("Student profile updated successfully.", "success")
    except Exception as exc:
        print_message(f"Could not update student: {exc}", "error")

def delete_student():
    print_title("Delete Student Account")
    prn = input("Student PRN to delete: ").strip()
    prn, error = validate_prn(prn)
    if error:
        print_message(error, "warn")
        return
    confirm = input("Type DELETE to confirm: ").strip()
    if confirm != "DELETE":
        print_message("Delete cancelled.", "info")
        return
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM students WHERE prn = %s", (prn,))
            conn.commit()
        log_audit("DELETE_STUDENT", f"Deleted student: {prn}")
        print_message("Student deleted successfully.", "success")
    except Exception as exc:
        print_message(f"Could not delete student: {exc}", "error")

def view_own_record():
    print_title("My Academic Record")
    if current_user["role"] != "student":
        print_message("Only students can view their personal transcripts.", "warn")
        return
    try:
        prn = current_user["student_id"]
        with get_connection() as conn:
            with conn.cursor() as cursor:
                # Stats
                cursor.execute("SELECT prn, name, department, marks FROM students WHERE prn = %s", (prn,))
                profile = cursor.fetchone()
                if profile:
                    print(f"Student PRN: {profile[0]}")
                    print(f"Student Name: {profile[1]}")
                    print(f"Department: {profile[2]}")
                    print(f"Rolling Average Score: {profile[3]:.2f}")
                    print("-" * 50)
                
                # Subject scores
                cursor.execute(
                    """
                    SELECT s.code, s.name, ss.marks
                    FROM student_subjects ss
                    JOIN subjects s ON s.id = ss.subject_id
                    WHERE ss.student_prn = %s
                    ORDER BY s.code
                    """,
                    (prn,)
                )
                print_table(("Subject Code", "Subject Name", "Marks Awarded"), cursor.fetchall())
                
                # Attendance
                print("\nMy Attendance Record:")
                cursor.execute(
                    """
                    SELECT s.code, s.name,
                           COUNT(a.id) AS total_classes,
                           SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) AS attended,
                           ROUND(COALESCE(SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(a.id), 0), 0), 2) AS percentage
                    FROM student_subjects ss
                    JOIN subjects s ON s.id = ss.subject_id
                    LEFT JOIN attendance a ON a.subject_id = ss.subject_id AND a.student_prn = ss.student_prn
                    WHERE ss.student_prn = %s
                    GROUP BY s.id, s.code, s.name
                    ORDER BY s.code
                    """,
                    (prn,)
                )
                attendance_rows = cursor.fetchall()
                print_table(("Subject Code", "Subject Name", "Attended / Total", "Percentage"), attendance_rows)
    except Exception as exc:
        print_message(f"Could not load your records: {exc}", "error")

# ============================
# ANALYTICS
# ============================
def dashboard():
    print_title("Live Analytics Dashboard")
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*), AVG(marks), MAX(marks), MIN(marks) FROM students")
                stats = cursor.fetchone()
                print_table(("Total Students", "Average Marks", "Highest Marks", "Lowest Marks"), [stats])

                cursor.execute(
                    """
                    SELECT
                        SUM(CASE WHEN marks >= 90 THEN 1 ELSE 0 END) AS A,
                        SUM(CASE WHEN marks >= 75 AND marks < 90 THEN 1 ELSE 0 END) AS B,
                        SUM(CASE WHEN marks >= 60 AND marks < 75 THEN 1 ELSE 0 END) AS C,
                        SUM(CASE WHEN marks >= 40 AND marks < 60 THEN 1 ELSE 0 END) AS D,
                        SUM(CASE WHEN marks < 40 THEN 1 ELSE 0 END) AS F
                    FROM students
                    """
                )
                print("\nGlobal Grade Distribution:")
                print_table(("A", "B", "C", "D", "F"), [cursor.fetchone()])
    except Exception as exc:
        print_message(f"Dashboard failed: {exc}", "error")

def view_analytics():
    print_title("Department Performance Analytics")
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT department, COUNT(*) AS students, AVG(marks), MAX(marks), MIN(marks)
                    FROM students
                    GROUP BY department
                    ORDER BY department
                    """
                )
                print_table(("Department", "Total Students", "Average Marks", "Highest Score", "Lowest Score"), cursor.fetchall())
    except Exception as exc:
        print_message(f"Analytics failed: {exc}", "error")

def marks_distribution():
    print_title("Grade Band Distribution")
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
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
                    """
                )
                print_table(("Grade Band", "Count"), cursor.fetchall())
    except Exception as exc:
        print_message(f"Distribution failed: {exc}", "error")

def show_top_performers():
    print_title("Top Academic Performers (Score >= 60)")
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT prn, name, department, marks FROM students WHERE marks >= 60 ORDER BY marks DESC, name LIMIT 10"
                )
                print_table(("PRN", "Name", "Department", "Average Marks"), cursor.fetchall())
    except Exception as exc:
        print_message(f"Could not load performers: {exc}", "error")

def dept_leaderboard():
    print_title("Department Leaderboard statistics")
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT department, total_students, average_marks, highest_marks, lowest_marks FROM vw_department_leaderboard")
                print_table(("Department", "Enrolled Students", "Average Marks", "Highest", "Lowest"), cursor.fetchall())
    except Exception as exc:
        print_message(f"Leaderboard failed: {exc}", "error")

def add_bonus_marks():
    print_title("Award Departmental Bonus Marks")
    dept = input("Enter Department Name: ").strip()
    bonus = input_float("Bonus Marks (0-100): ", 0, 100)
    if bonus is None:
        return
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE students SET marks = LEAST(marks + %s, 100) WHERE LOWER(department) = LOWER(%s)",
                    (bonus, dept)
                )
                conn.commit()
                count = cursor.rowcount
        log_audit("AWARD_BONUS", f"Awarded +{bonus} bonus marks to {count} student(s) in department '{dept}'")
        print_message(f"Bonus applied successfully to {count} student(s).", "success")
    except Exception as exc:
        print_message(f"Failed to award bonus marks: {exc}", "error")

def export_high_performers():
    print_title("Export High-Performing Students to CSV")
    filename = f"high_performers_{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT prn, name, department, marks
                    FROM students
                    WHERE marks > (SELECT AVG(marks) FROM students)
                    ORDER BY marks DESC, name
                    """
                )
                rows = cursor.fetchall()
        
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(("PRN", "Name", "Department", "Rolling Average"))
            writer.writerows(rows)
        
        log_audit("EXPORT_HIGH_PERFORMERS", f"Exported {len(rows)} high performers to {filename}")
        print_message(f"Exported {len(rows)} high performer(s) successfully to {filename}.", "success")
    except Exception as exc:
        print_message(f"Export failed: {exc}", "error")

# ============================
# USER MANAGEMENT
# ============================
def create_user():
    print_title("Create User Account")
    role = input("Role (admin/faculty/student): ").strip().lower()
    if role not in ("admin", "faculty", "student"):
        print_message("Invalid role specified.", "warn")
        return
    
    prn_or_user = input("Enter PRN (for faculty/student) or Username (for admin): ").strip()
    password = getpass.getpass("Password: ")
    name = input("Enter Name: ").strip()
    dept = input("Enter Department: ").strip()
    
    if not prn_or_user or not password or not name or not dept:
        print_message("All fields are mandatory.", "warn")
        return
        
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                if role == "admin":
                    cursor.execute(
                        "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
                        (prn_or_user, hash_password(password), "admin")
                    )
                elif role == "faculty":
                    prn, err = validate_prn(prn_or_user)
                    if err:
                        print_message(err, "warn")
                        return
                    cursor.execute(
                        "INSERT INTO faculty (prn, password_hash, name, department) VALUES (%s, %s, %s, %s)",
                        (prn, hash_password(password), name, dept)
                    )
                elif role == "student":
                    prn, err = validate_prn(prn_or_user)
                    if err:
                        print_message(err, "warn")
                        return
                    cursor.execute(
                        "INSERT INTO students (prn, password_hash, name, department) VALUES (%s, %s, %s, %s)",
                        (prn, hash_password(password), name, dept)
                    )
            conn.commit()
        log_audit("CREATE_USER_ACCOUNT", f"Created {role} user '{prn_or_user}'")
        print_message("User account created successfully.", "success")
    except Exception as exc:
        print_message(f"Could not create user: {exc}", "error")

def list_users():
    print_title("Active System Accounts Directory")
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                # Admin accounts
                print("\nAdmins:")
                cursor.execute("SELECT username, role, IF(is_active, 'active', 'disabled') FROM users")
                print_table(("Username", "Role", "Status"), cursor.fetchall())
                
                # Faculty accounts
                print("\nFaculty Professors:")
                cursor.execute("SELECT prn, name, department, IF(is_active, 'active', 'disabled') FROM faculty")
                print_table(("PRN", "Name", "Department", "Status"), cursor.fetchall())
                
                # Student accounts
                print("\nStudents:")
                cursor.execute("SELECT prn, name, department, IF(is_active, 'active', 'disabled') FROM students")
                print_table(("PRN", "Name", "Department", "Status"), cursor.fetchall())
    except Exception as exc:
        print_message(f"Could not list users: {exc}", "error")

def toggle_user():
    print_title("Toggle User Active / Disable status")
    role = input("User Role (admin/faculty/student): ").strip().lower()
    username_or_prn = input("Username or PRN: ").strip()
    
    if role == "admin" and username_or_prn.lower() == current_user["username"].lower():
        print_message("You cannot disable your own active session.", "warn")
        return
        
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                changed = 0
                if role == "admin":
                    cursor.execute("UPDATE users SET is_active = NOT is_active WHERE username = %s", (username_or_prn,))
                    changed = cursor.rowcount
                elif role == "faculty":
                    prn, _ = validate_prn(username_or_prn)
                    cursor.execute("UPDATE faculty SET is_active = NOT is_active WHERE prn = %s", (prn,))
                    changed = cursor.rowcount
                elif role == "student":
                    prn, _ = validate_prn(username_or_prn)
                    cursor.execute("UPDATE students SET is_active = NOT is_active WHERE prn = %s", (prn,))
                    changed = cursor.rowcount
            conn.commit()
        if changed:
            log_audit("TOGGLE_USER_STATUS", f"Toggled status of '{username_or_prn}'")
            print_message("Account status toggled successfully.", "success")
        else:
            print_message("No matching account found.", "warn")
    except Exception as exc:
        print_message(f"Could not toggle status: {exc}", "error")

def create_mysql_users():
    print_title("Grant Privileges to MySQL App Users")
    password = getpass.getpass("Enter password for spa app users: ")
    confirm = input("Type CONFIRM to execute: ").strip()
    if confirm != "CONFIRM":
        print_message("Operation aborted.", "info")
        return
    
    statements = [
        "CREATE USER IF NOT EXISTS 'spa_admin'@'localhost' IDENTIFIED BY %s",
        "GRANT SELECT, INSERT, UPDATE, DELETE ON spa_enhanced_db.students TO 'spa_admin'@'localhost'",
        "GRANT SELECT, INSERT, UPDATE, DELETE ON spa_enhanced_db.faculty TO 'spa_admin'@'localhost'",
        "GRANT SELECT, INSERT, UPDATE, DELETE ON spa_enhanced_db.users TO 'spa_admin'@'localhost'",
        "GRANT SELECT, INSERT ON spa_enhanced_db.audit_log TO 'spa_admin'@'localhost'",
        "GRANT SELECT ON spa_enhanced_db.vw_student_grades TO 'spa_admin'@'localhost'",
        "GRANT SELECT ON spa_enhanced_db.vw_department_leaderboard TO 'spa_admin'@'localhost'",
        "GRANT SELECT, INSERT, UPDATE, DELETE ON spa_enhanced_db.subjects TO 'spa_admin'@'localhost'",
        "GRANT SELECT, INSERT, UPDATE, DELETE ON spa_enhanced_db.student_subjects TO 'spa_admin'@'localhost'",
        "GRANT SELECT, INSERT, UPDATE, DELETE ON spa_enhanced_db.faculty_subjects TO 'spa_admin'@'localhost'",
        "GRANT SELECT, INSERT, UPDATE, DELETE ON spa_enhanced_db.attendance TO 'spa_admin'@'localhost'",
        
        "CREATE USER IF NOT EXISTS 'spa_faculty'@'localhost' IDENTIFIED BY %s",
        "GRANT SELECT, INSERT, UPDATE ON spa_enhanced_db.students TO 'spa_faculty'@'localhost'",
        "GRANT SELECT ON spa_enhanced_db.faculty TO 'spa_faculty'@'localhost'",
        "GRANT INSERT ON spa_enhanced_db.audit_log TO 'spa_faculty'@'localhost'",
        "GRANT SELECT ON spa_enhanced_db.vw_student_grades TO 'spa_faculty'@'localhost'",
        "GRANT SELECT ON spa_enhanced_db.vw_department_leaderboard TO 'spa_faculty'@'localhost'",
        "GRANT SELECT ON spa_enhanced_db.subjects TO 'spa_faculty'@'localhost'",
        "GRANT SELECT, INSERT, UPDATE, DELETE ON spa_enhanced_db.student_subjects TO 'spa_faculty'@'localhost'",
        "GRANT SELECT ON spa_enhanced_db.faculty_subjects TO 'spa_faculty'@'localhost'",
        "GRANT SELECT, INSERT, UPDATE, DELETE ON spa_enhanced_db.attendance TO 'spa_faculty'@'localhost'",
        
        "CREATE USER IF NOT EXISTS 'spa_student'@'localhost' IDENTIFIED BY %s",
        "GRANT SELECT ON spa_enhanced_db.students TO 'spa_student'@'localhost'",
        "GRANT INSERT ON spa_enhanced_db.audit_log TO 'spa_student'@'localhost'",
        "GRANT SELECT ON spa_enhanced_db.vw_student_grades TO 'spa_student'@'localhost'",
        "GRANT SELECT ON spa_enhanced_db.vw_department_leaderboard TO 'spa_student'@'localhost'",
        "GRANT SELECT ON spa_enhanced_db.subjects TO 'spa_student'@'localhost'",
        "GRANT SELECT ON spa_enhanced_db.student_subjects TO 'spa_student'@'localhost'",
        "GRANT SELECT ON spa_enhanced_db.faculty_subjects TO 'spa_student'@'localhost'",
        "GRANT SELECT ON spa_enhanced_db.attendance TO 'spa_student'@'localhost'",
        
        "FLUSH PRIVILEGES"
    ]
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                for stmt in statements:
                    if "%s" in stmt:
                        cursor.execute(stmt, (password,))
                    else:
                        cursor.execute(stmt)
            conn.commit()
        log_audit("CREATE_MYSQL_USERS", "Created database application users and schemas grants")
        print_message("Database roles and privileges granted successfully.", "success")
    except Exception as exc:
        print_message(f"Grant privileges failed: {exc}", "error")

def view_audit_log():
    print_title("System Security Audit Logs (Last 30)")
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id, action, details, timestamp FROM audit_log ORDER BY timestamp DESC, id DESC LIMIT 30"
                )
                print_table(("ID", "Action", "Details", "Timestamp"), cursor.fetchall())
    except Exception as exc:
        print_message(f"Could not load audit log: {exc}", "error")

# ============================
# NEW ACADEMICS & ATTENDANCE WORKFLOWS
# ============================
def admin_manage_academics():
    while True:
        clear_screen()
        print_title("Academic Management")
        print("1. Create Subject")
        print("2. Enroll Student in Subject")
        print("3. Assign Faculty to Subject")
        print("4. Unenroll Student")
        print("5. Unassign Faculty")
        print("6. View Subjects Directory & Assignments")
        print("0. Back")
        
        choice = input("\nChoice: ").strip()
        if choice == "1":
            code = input("Subject Code (e.g. CS101): ").strip()
            name = input("Subject Name: ").strip()
            batch = input("Batch (e.g. 2025): ").strip()
            if not code or not name or not batch:
                print_message("All fields required.", "warn")
                pause()
                continue
            try:
                with get_connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute("INSERT INTO subjects (code, name, batch) VALUES (%s, %s, %s)", (code, name, batch))
                    conn.commit()
                log_audit("CREATE_SUBJECT", f"Created subject {code} ({batch})")
                print_message("Subject created successfully.", "success")
            except Exception as e:
                print_message(f"Error creating subject: {e}", "error")
            pause()
            
        elif choice == "2":
            sub_id = input_int("Enter Subject ID: ")
            student_prn = input("Enter Student PRN: ").strip()
            try:
                with get_connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute("INSERT INTO student_subjects (subject_id, student_prn) VALUES (%s, %s)", (sub_id, student_prn))
                    conn.commit()
                update_overall_student_marks(student_prn)
                log_audit("ENROLL_STUDENT", f"Enrolled student {student_prn} in subject ID {sub_id}")
                print_message("Student enrolled successfully.", "success")
            except Exception as e:
                print_message(f"Error enrolling student: {e}", "error")
            pause()
            
        elif choice == "3":
            fac_prn = input("Enter Faculty PRN: ").strip()
            sub_id = input_int("Enter Subject ID: ")
            try:
                with get_connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute("INSERT INTO faculty_subjects (faculty_prn, subject_id) VALUES (%s, %s)", (fac_prn, sub_id))
                    conn.commit()
                log_audit("ASSIGN_FACULTY", f"Assigned faculty {fac_prn} to subject ID {sub_id}")
                print_message("Faculty assigned successfully.", "success")
            except Exception as e:
                print_message(f"Error assigning faculty: {e}", "error")
            pause()
            
        elif choice == "4":
            sub_id = input_int("Enter Subject ID: ")
            student_prn = input("Enter Student PRN: ").strip()
            try:
                with get_connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute("DELETE FROM student_subjects WHERE subject_id = %s AND student_prn = %s", (sub_id, student_prn))
                    conn.commit()
                update_overall_student_marks(student_prn)
                log_audit("UNENROLL_STUDENT", f"Unenrolled student {student_prn} from subject ID {sub_id}")
                print_message("Student unenrolled.", "success")
            except Exception as e:
                print_message(f"Error: {e}", "error")
            pause()
            
        elif choice == "5":
            fac_prn = input("Enter Faculty PRN: ").strip()
            sub_id = input_int("Enter Subject ID: ")
            try:
                with get_connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute("DELETE FROM faculty_subjects WHERE faculty_prn = %s AND subject_id = %s", (fac_prn, sub_id))
                    conn.commit()
                log_audit("UNASSIGN_FACULTY", f"Unassigned faculty {fac_prn} from subject ID {sub_id}")
                print_message("Faculty assignment removed.", "success")
            except Exception as e:
                print_message(f"Error: {e}", "error")
            pause()
            
        elif choice == "6":
            try:
                with get_connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute("SELECT id, code, name, batch FROM subjects ORDER BY code")
                        print("\n--- Subjects ---")
                        print_table(("ID", "Code", "Name", "Batch"), cursor.fetchall())
                        
                        cursor.execute(
                            """
                            SELECT fs.subject_id, s.code, f.name AS fac_name 
                            FROM faculty_subjects fs
                            JOIN subjects s ON s.id = fs.subject_id
                            JOIN faculty f ON f.prn = fs.faculty_prn
                            """
                        )
                        print("\n--- Faculty Assignments ---")
                        print_table(("Subject ID", "Code", "Faculty Professor"), cursor.fetchall())
            except Exception as e:
                print_message(f"Error listing details: {e}", "error")
            pause()
            
        elif choice == "0":
            break

def faculty_assigned_subjects():
    print_title("My Assigned Subjects")
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT s.id, s.code, s.name, s.batch 
                    FROM subjects s
                    JOIN faculty_subjects fs ON fs.subject_id = s.id
                    WHERE fs.faculty_prn = %s
                    ORDER BY s.code
                    """,
                    (current_user["student_id"],)
                )
                print_table(("Subject ID", "Code", "Name", "Batch"), cursor.fetchall())
    except Exception as e:
        print_message(f"Error loading subjects: {e}", "error")

def faculty_update_marks():
    print_title("Submit Student Subject Grades")
    sub_id = input_int("Enter Subject ID: ")
    if not sub_id:
        return
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                # Check assigned
                cursor.execute(
                    "SELECT 1 FROM faculty_subjects WHERE faculty_prn = %s AND subject_id = %s",
                    (current_user["student_id"], sub_id)
                )
                if not cursor.fetchone():
                    print_message("You are not assigned to teach this subject.", "error")
                    return
                
                # Fetch students
                cursor.execute(
                    """
                    SELECT ss.student_prn, st.name, ss.marks
                    FROM student_subjects ss
                    JOIN students st ON st.prn = ss.student_prn
                    WHERE ss.subject_id = %s
                    """,
                    (sub_id,)
                )
                students = cursor.fetchall()
                if not students:
                    print_message("No students enrolled in this subject.", "warn")
                    return
                
                print_table(("PRN", "Name", "Subject Marks"), students)
                student_prn = input("\nEnter student PRN to update: ").strip()
                student_prn, err = validate_prn(student_prn)
                if err:
                    print_message(err, "warn")
                    return
                
                marks = input_float("Enter marks (0-100): ", 0, 100)
                if marks is None:
                    return
                
                cursor.execute(
                    "UPDATE student_subjects SET marks = %s WHERE subject_id = %s AND student_prn = %s",
                    (marks, sub_id, student_prn)
                )
            conn.commit()
        update_overall_student_marks(student_prn)
        log_audit("FACULTY_UPDATE_MARKS", f"Updated student {student_prn} marks in subject ID {sub_id} to {marks}")
        print_message("Subject marks updated successfully.", "success")
    except Exception as e:
        print_message(f"Failed: {e}", "error")

def faculty_manage_attendance():
    while True:
        clear_screen()
        print_title("Attendance Management")
        print("1. Roll Call (Mark Attendance Sheet)")
        print("2. View Subject Attendance History Logs")
        print("0. Back")
        
        choice = input("\nChoice: ").strip()
        if choice == "1":
            sub_id = input_int("Enter Subject ID: ")
            if not sub_id:
                continue
            try:
                with get_connection() as conn:
                    with conn.cursor() as cursor:
                        # Check assignment
                        cursor.execute(
                            "SELECT 1 FROM faculty_subjects WHERE faculty_prn = %s AND subject_id = %s",
                            (current_user["student_id"], sub_id)
                        )
                        if not cursor.fetchone():
                            print_message("You are not assigned to teach this subject.", "error")
                            pause()
                            continue
                        
                        date_str = input("Date (YYYY-MM-DD, blank for today): ").strip()
                        if not date_str:
                            date_str = dt.date.today().strftime("%Y-%m-%d")
                        
                        cursor.execute(
                            """
                            SELECT ss.student_prn, st.name
                            FROM student_subjects ss
                            JOIN students st ON st.prn = ss.student_prn
                            WHERE ss.subject_id = %s
                            """,
                            (sub_id,)
                        )
                        students = cursor.fetchall()
                        if not students:
                            print_message("No students enrolled.", "warn")
                            pause()
                            continue
                        
                        print(f"\nRecording roll call sheet on {date_str}:")
                        for s in students:
                            print(f"Student: {s[1]} ({s[0]})")
                            status = ""
                            while status not in ["p", "a"]:
                                status = input("Status (P = Present, A = Absent): ").strip().lower()
                            db_status = "Present" if status == "p" else "Absent"
                            
                            cursor.execute(
                                """
                                INSERT INTO attendance (subject_id, student_prn, date, status)
                                VALUES (%s, %s, %s, %s)
                                ON DUPLICATE KEY UPDATE status = VALUES(status)
                                """,
                                (sub_id, s[0], date_str, db_status)
                            )
                    conn.commit()
                log_audit("SAVE_ATTENDANCE", f"Saved roll call sheet for subject ID {sub_id} on {date_str}")
                print_message("Attendance sheet saved successfully.", "success")
            except Exception as e:
                print_message(f"Error marking attendance: {e}", "error")
            pause()
            
        elif choice == "2":
            sub_id = input_int("Enter Subject ID: ")
            if not sub_id:
                continue
            try:
                with get_connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute(
                            "SELECT 1 FROM faculty_subjects WHERE faculty_prn = %s AND subject_id = %s",
                            (current_user["student_id"], sub_id)
                        )
                        if not cursor.fetchone():
                            print_message("Unauthorized.", "error")
                            pause()
                            continue
                        
                        cursor.execute(
                            """
                            SELECT date,
                                   SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) AS present_count,
                                   SUM(CASE WHEN status = 'Absent' THEN 1 ELSE 0 END) AS absent_count,
                                   COUNT(*) AS total_count
                            FROM attendance
                            WHERE subject_id = %s
                            GROUP BY date
                            ORDER BY date DESC
                            """,
                            (sub_id,)
                        )
                        print_table(("Date", "Present Count", "Absent Count", "Total Logs"), cursor.fetchall())
            except Exception as e:
                print_message(f"Error: {e}", "error")
            pause()
            
        elif choice == "0":
            break

# ============================
# MENUS
# ============================
def menu_admin():
    while True:
        clear_screen()
        print_title(f"Admin Dashboard | Welcome, {current_user['username']}")
        print("1. Live Analytics Dashboard")
        print("2. Add Student Record")
        print("3. View All Students")
        print("4. Search Students by Department")
        print("5. Update Student Profile")
        print("6. Delete Student Account")
        print("7. Department Performance Analytics")
        print("8. Grade Band Distribution Report")
        print("9. Top Academic Performers Directory")
        print("10. Department Leaderboard stats")
        print("11. Award Departmental Bonus Marks")
        print("12. Export High Performers to CSV")
        print("13. Create User Account")
        print("14. List Active System Accounts")
        print("15. Toggle User Active status")
        print("16. Create MySQL Application Users & Privileges")
        print("17. View Security Audit Logs")
        print("18. Manage Academic Subjects & Enrollments")
        print("0. Logout")
        
        choice = input("\nSelect Option: ").strip()
        clear_screen()
        
        if choice == "1":
            dashboard()
        elif choice == "2":
            add_student()
        elif choice == "3":
            view_students()
        elif choice == "4":
            search_by_dept()
        elif choice == "5":
            update_student()
        elif choice == "6":
            delete_student()
        elif choice == "7":
            view_analytics()
        elif choice == "8":
            marks_distribution()
        elif choice == "9":
            show_top_performers()
        elif choice == "10":
            dept_leaderboard()
        elif choice == "11":
            add_bonus_marks()
        elif choice == "12":
            export_high_performers()
        elif choice == "13":
            create_user()
        elif choice == "14":
            list_users()
        elif choice == "15":
            toggle_user()
        elif choice == "16":
            create_mysql_users()
        elif choice == "17":
            view_audit_log()
        elif choice == "18":
            admin_manage_academics()
        elif choice == "0":
            logout()
            break
        else:
            print_message("Invalid option.", "warn")
        pause()

def menu_faculty():
    while True:
        clear_screen()
        print_title(f"Faculty Portal | Welcome, Prof. {current_user['username']}")
        print("1. View My Assigned Subjects")
        print("2. Enter / Update Student Marks")
        print("3. Manage Subject Attendance sheets")
        print("4. Live Analytics Dashboard")
        print("5. Top Performers Catalog")
        print("6. Department Leaderboard status")
        print("0. Logout")
        
        choice = input("\nSelect Option: ").strip()
        clear_screen()
        
        if choice == "1":
            faculty_assigned_subjects()
        elif choice == "2":
            faculty_update_marks()
        elif choice == "3":
            faculty_manage_attendance()
        elif choice == "4":
            dashboard()
        elif choice == "5":
            show_top_performers()
        elif choice == "6":
            dept_leaderboard()
        elif choice == "0":
            logout()
            break
        else:
            print_message("Invalid option.", "warn")
        pause()

def menu_student():
    while True:
        clear_screen()
        print_title(f"Student Portal | Welcome, {current_user['username']}")
        print("1. View My Academic Record & Transcripts")
        print("2. View Top Performers Catalog")
        print("3. View Department Leaderboard status")
        print("0. Logout")
        
        choice = input("\nSelect Option: ").strip()
        clear_screen()
        
        if choice == "1":
            view_own_record()
        elif choice == "2":
            show_top_performers()
        elif choice == "3":
            dept_leaderboard()
        elif choice == "0":
            logout()
            break
        else:
            print_message("Invalid option.", "warn")
        pause()

def main():
    ensure_database_setup()
    while True:
        clear_screen()
        if not login():
            pause()
            continue
        
        role = current_user["role"]
        if role == "admin":
            menu_admin()
        elif role == "faculty":
            menu_faculty()
        elif role == "student":
            menu_student()
        else:
            print_message("Unknown session role.", "error")
            pause()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting Student Performance Analyzer...")
        sys.exit(0)
