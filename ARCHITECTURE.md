# SPA Architecture & Design Document

## System Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│                    SPA CLI Application                        │
│                    (PRN_analyzer.py)                          │
└──────────────────────────────────────────────────────────────┘
                           ↓
        ┌──────────────────────────────────────┐
        │   Presentation Layer (CLI Menus)     │
        │                                      │
        │  - menu_admin()                      │
        │  - menu_faculty()                    │
        │  - menu_student()                    │
        └──────────────────────────────────────┘
                           ↓
        ┌──────────────────────────────────────┐
        │   Business Logic Layer               │
        │                                      │
        │  - Authentication functions         │
        │  - CRUD operations                  │
        │  - Analytics calculations           │
        │  - Audit logging                    │
        └──────────────────────────────────────┘
                           ↓
        ┌──────────────────────────────────────┐
        │   Data Access Layer (DB Functions)   │
        │                                      │
        │  - get_connection()                 │
        │  - SQL execution                    │
        │  - Transaction handling             │
        └──────────────────────────────────────┘
                           ↓
        ┌──────────────────────────────────────┐
        │   Database Layer (MySQL)             │
        │                                      │
        │  - spa_enhanced_db                  │
        │  - 8 tables + 2 views               │
        │  - Full referential integrity       │
        └──────────────────────────────────────┘
```

---

## Entity-Relationship Diagram (ERD)

```
                    ┌─────────────┐
                    │    users    │
                    ├─────────────┤
                    │ id (PK)     │
                    │ username    │──┐
                    │ password    │  │
                    │ role        │  │
                    │ is_active   │  │
                    │ created_at  │  │
                    └─────────────┘  │
                         ↑           │
                         │           │ (1:N)
                         │           │
                    ┌────┴────────────┴──┐
                    │   audit_log        │
                    ├────────────────────┤
                    │ id (PK)            │
                    │ user_id (FK)       │
                    │ action             │
                    │ details            │
                    │ timestamp          │
                    └────────────────────┘


        ┌──────────────┐              ┌──────────────┐
        │  students    │              │   faculty    │
        ├──────────────┤              ├──────────────┤
        │ prn (PK)     │              │ prn (PK)     │
        │ password     │              │ password     │
        │ name         │              │ name         │
        │ department   │              │ department   │
        │ marks        │              │ is_active    │
        │ is_active    │              │ created_at   │
        │ enrolled_at  │              └──────────────┘
        └──────┬───────┘                     │
               │                             │
         (1:N) │                             │ (1:N)
               │                             │
        ┌──────┴─────────┐          ┌───────┴──────────┐
        │ student_       │          │  faculty_        │
        │ subjects       │          │  subjects        │
        ├────────────────┤          ├──────────────────┤
        │ subject_id(FK) │          │ faculty_prn(FK)  │
        │ student_prn(FK)│          │ subject_id(FK)   │
        │ marks          │          └──────────────────┘
        └────────┬───────┘                  │
                 │                          │
            (N:1)└──────────────┬───────────┘
                                │
                         ┌──────┴───────┐
                         │  subjects    │
                         ├──────────────┤
                         │ id (PK)      │
                         │ code         │
                         │ name         │
                         │ batch        │
                         └──────┬───────┘
                                │
                          (1:N) │
                                │
                         ┌──────┴──────────┐
                         │  attendance    │
                         ├────────────────┤
                         │ id (PK)        │
                         │ subject_id(FK) │
                         │ student_prn(FK)│
                         │ date           │
                         │ status         │
                         └────────────────┘
```

---

## Data Flow Diagrams

### Flow 1: Student Login & View Record

```
Start
  ↓
Input PRN & Password
  ↓
Validate PRN Format
  ↓
Query students table
  ↓
Compare password hash
  ↓
Check is_active flag
  ↓
Populate current_user
  ↓
Log "LOGIN_SUCCESS"
  ↓
Display Student Menu
  ↓
User selects "View My Record"
  ↓
Query students table (own record)
  ↓
Query student_subjects (grades)
  ↓
Query attendance (attendance %)
  ↓
Display Record
  ↓
Continue or Logout
```

---

### Flow 2: Faculty Update Student Marks

```
Faculty logs in
  ↓
Select Menu 2: Update Marks
  ↓
Input Subject ID
  ↓
Query faculty_subjects (verify assignment)
  ↓
If not assigned → Error & return
  ↓
Query student_subjects (show enrolled)
  ↓
Input Student PRN
  ↓
Input Marks (0-100)
  ↓
UPDATE student_subjects.marks
  ↓
Call update_overall_student_marks()
  ↓
Recalculate average from subject_subjects
  ↓
UPDATE students.marks (rolling average)
  ↓
COMMIT transaction
  ↓
Log "FACULTY_UPDATE_MARKS"
  ↓
Display Success
```

---

### Flow 3: Admin Analytics Dashboard

```
Admin logs in
  ↓
Select Menu 1: Dashboard
  ↓
Query 1: COUNT & AVG & MAX & MIN marks
  ↓
Query 2: Grade distribution (A/B/C/D/F)
  ↓
Display Statistics
  ↓
Display Grade Band
  ↓
Return to Menu
```

---

### Flow 4: Attendance Recording

```
Faculty logs in
  ↓
Select Menu 3 (Attendance)
  ↓
Select Option 1 (Roll Call)
  ↓
Input Subject ID
  ↓
Query faculty_subjects (verify)
  ↓
Input Date (or default today)
  ↓
Query student_subjects (get enrolled)
  ↓
For each student:
  │
  ├→ Display name & PRN
  │
  ├→ Input P or A
  │
  └→ INSERT into attendance table
      (ON DUPLICATE KEY UPDATE)
  ↓
COMMIT all records
  ↓
Log "SAVE_ATTENDANCE"
  ↓
Display Success
```

---

## Database Connection Management

```
Application Start
  ↓
┌─ ensure_database_setup()
│   ├→ get_base_connection()
│   ├→ Check if spa_enhanced_db exists
│   ├→ Create DB if missing
│   ├→ Create all tables
│   ├→ Create views
│   ├→ Insert default admin
│   └→ Close connection
│
├─ Loop: User Login
│   ├→ Input credentials
│   ├→ get_connection() to spa_enhanced_db
│   ├→ Query appropriate table
│   ├→ Verify password hash
│   ├→ Check is_active
│   └→ Close connection
│
├─ Loop: User Operations
│   ├→ get_connection()
│   ├→ Execute query/transaction
│   ├→ COMMIT or handle error
│   ├→ Close connection
│   └→ Log audit entry
│
└─ Application Exit
    └→ All connections closed
```

---

## Transaction Management

### Standard Transaction Flow

```
with get_connection() as conn:
    with conn.cursor() as cursor:
        
        # Execute one or more queries
        cursor.execute("INSERT...", (params))
        cursor.execute("UPDATE...", (params))
        cursor.execute("DELETE...", (params))
        
        # Commit all changes
    conn.commit()  # Executed outside with block

    # If exception occurs:
    # → Rollback happens automatically
    # → except block handles error
```

### Example: Update Student Marks

```sql
START TRANSACTION;

UPDATE student_subjects 
SET marks = 85 
WHERE subject_id = 1 AND student_prn = '25007011001';

SELECT AVG(marks) as avg_marks 
FROM student_subjects 
WHERE student_prn = '25007011001' 
AND marks IS NOT NULL;

UPDATE students 
SET marks = 83.50 
WHERE prn = '25007011001';

COMMIT;
```

---

## Authentication Flow

```
User enters credentials
  ↓
┌─ Check Admin (users table)
│   ├→ Query by username
│   ├→ Hash password
│   ├→ Compare hashes
│   ├→ Check is_active
│   └→ Return user data
│
├─ If not found, Check Faculty (faculty table)
│   ├→ Validate PRN format
│   ├→ Query by PRN
│   ├→ Hash password
│   ├→ Compare hashes
│   ├→ Check is_active
│   └→ Return faculty data
│
├─ If not found, Check Student (students table)
│   ├→ Validate PRN format
│   ├→ Query by PRN
│   ├→ Hash password
│   ├→ Compare hashes
│   ├→ Check is_active
│   └→ Return student data
│
└─ If all fail: Login Failed
    └→ Log "LOGIN_FAILED"
```

---

## Permission Model

```
┌─────────────────────────────────────────────┐
│          Authentication (Who are you?)      │
│                                             │
│  ┌──────────────┐                          │
│  │   Verified?  │                          │
│  └──────┬───────┘                          │
│         ├─ NO → Deny Access               │
│         └─ YES → Next                      │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│      Authorization (What can you do?)       │
│                                             │
│  Check current_user["role"]                │
│  ├─ admin → Full access                    │
│  ├─ faculty → Limited operations           │
│  └─ student → Read-only own data           │
│                                             │
│  Execute function with permission checks   │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│      Audit Logging (What did you do?)       │
│                                             │
│  Insert into audit_log table               │
│  ├─ user_id                                │
│  ├─ action                                 │
│  ├─ details                                │
│  └─ timestamp                              │
└─────────────────────────────────────────────┘
```

---

## Constraint Enforcement

### Database Constraints

```
Table: students
├─ CHECK (marks >= 0 AND marks <= 100)
├─ CHECK (prn REGEXP '^(25|26|27)0(06|07)(01|02|03|04|05|06)[123][0-9]{3}$')
├─ PRIMARY KEY (prn)
└─ UNIQUE (prn)

Table: student_subjects
├─ CHECK (marks IS NULL OR (marks >= 0 AND marks <= 100))
├─ PRIMARY KEY (subject_id, student_prn)
├─ FOREIGN KEY (subject_id) → subjects(id)
└─ FOREIGN KEY (student_prn) → students(prn)

Table: attendance
├─ UNIQUE (subject_id, student_prn, date)
├─ FOREIGN KEY (subject_id) → subjects(id)
└─ FOREIGN KEY (student_prn) → students(prn)
```

### Application-Level Validation

```
Input Validation
├─ PRN format: validate_prn()
├─ Marks range: input_float(min=0, max=100)
├─ Password length: >= 1 character
├─ Names: not empty
└─ Role: admin/faculty/student only

Business Logic Validation
├─ Faculty can only grade assigned subjects
├─ Faculty can only mark attendance for assigned subjects
├─ Students can only view own data
├─ Admin can do anything
└─ Cannot disable self (for admin)

Database Validation
├─ Constraints prevent invalid data
├─ Triggers maintain referential integrity
├─ Cascading deletes clean up related data
└─ Unique constraints prevent duplicates
```

---

## Error Handling Strategy

```
try:
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
        conn.commit()
    
    log_audit("ACTION", "Success details")
    print_message("Success message", "success")

except IntegrityError as e:
    # Duplicate, foreign key, constraint violation
    print_message("Duplicate entry or constraint violation", "error")
    
except OperationalError as e:
    # Connection lost, invalid SQL
    print_message("Database connection error", "error")
    
except ValueError as e:
    # Invalid input (parsed numbers)
    print_message("Invalid input format", "warn")
    
except Exception as e:
    # Any other error
    print_message(f"Unexpected error: {e}", "error")
```

---

## Performance Optimization

### Indexing Strategy

```
Clustered Indexes (Primary Keys)
├─ users.id
├─ students.prn
├─ faculty.prn
├─ subjects.id
├─ attendance.id
└─ audit_log.id

Secondary Indexes
├─ users.username (UNIQUE)
├─ subjects.code + batch (UNIQUE)
├─ attendance (subject_id, student_prn, date) UNIQUE
└─ audit_log.timestamp (for sorting)
```

### Query Optimization

```
Avoid N+1 queries:
├─ Use JOINs instead of loops
├─ Fetch all data in one query
└─ Example: Faculty viewing marks
    GOOD: SELECT s.*, ss.* FROM subjects s 
          JOIN student_subjects ss
    BAD:  Loop through subjects, query each separately

Use appropriate WHERE clauses:
├─ Filter early in query
├─ Reduce result set size
└─ Let database optimize

Use aggregation functions:
├─ COUNT() instead of counting in app
├─ AVG(), MAX(), MIN() in database
└─ GROUP BY instead of manual grouping
```

---

## Scalability Considerations

### Current Limitations

```
Single-threaded CLI application
├─ One user at a time
├─ No concurrent access
└─ Suitable for single-admin usage

Local MySQL connection only
├─ Not distributed
├─ Network access not configured
└─ Fine for small institution

Memory management
├─ All queries fetch to memory
├─ Large result sets may slow down
└─ Pagination not implemented
```

### Potential Improvements

```
For Medium to Large Scale:

1. Add pagination:
   ├─ LIMIT & OFFSET in queries
   ├─ Browse data in pages
   └─ Reduce memory footprint

2. Add connection pooling:
   ├─ Reuse connections
   ├─ Faster response
   └─ Handle more users

3. Add async operations:
   ├─ Background processing
   ├─ Non-blocking I/O
   └─ Better responsiveness

4. Archive old data:
   ├─ Move historical records
   ├─ Reduce active dataset
   └─ Faster queries

5. Add caching:
   ├─ Cache analytics results
   ├─ Reduce repeated queries
   └─ Faster dashboard load
```

---

## Security Best Practices

### Implemented

```
✓ Password hashing (SHA256)
✓ Input validation (PRN format, ranges)
✓ SQL parameterized queries (prevent injection)
✓ Role-based access control
✓ Audit logging of all actions
✓ Session management (current_user dict)
✓ Account status checking (is_active)
✓ Constraint enforcement
```

### Recommendations

```
To enhance security further:

1. Use bcrypt instead of SHA256:
   ├─ More secure hashing
   ├─ Built-in salt
   └─ Resistant to GPU attacks

2. Add password expiration:
   ├─ Force password changes
   ├─ Reduce compromised account impact
   └─ Industry best practice

3. Add 2FA (Two-Factor Authentication):
   ├─ OTP via email or SMS
   ├─ More secure login
   └─ Additional user layer

4. Add API rate limiting:
   ├─ Prevent brute force attacks
   ├─ Limit rapid operations
   └─ Protect against abuse

5. Encrypt database connection:
   ├─ Use SSL/TLS
   ├─ Secure data in transit
   └─ Prevent man-in-the-middle

6. Regular security audits:
   ├─ Review audit logs regularly
   ├─ Monitor suspicious activities
   └─ Implement alerting system
```

---

## Code Structure

```
PRN_analyzer.py
│
├─ CONFIGURATION
│  └─ DB_CONFIG, PRN_PATTERN, current_user
│
├─ UTILITY FUNCTIONS (Shared)
│  ├─ get_connection()
│  ├─ get_base_connection()
│  ├─ hash_password()
│  ├─ clear_screen()
│  ├─ print_title()
│  ├─ print_message()
│  ├─ print_table()
│  ├─ input_int() / input_float()
│  ├─ validate_prn()
│  └─ log_audit()
│
├─ CORE FUNCTIONS
│  ├─ ensure_database_setup()
│  ├─ update_overall_student_marks()
│  └─ login() / logout()
│
├─ CRUD OPERATIONS
│  ├─ add_student()
│  ├─ view_students()
│  ├─ search_by_dept()
│  ├─ update_student()
│  ├─ delete_student()
│  └─ view_own_record()
│
├─ ANALYTICS
│  ├─ dashboard()
│  ├─ view_analytics()
│  ├─ marks_distribution()
│  ├─ show_top_performers()
│  ├─ dept_leaderboard()
│  ├─ add_bonus_marks()
│  └─ export_high_performers()
│
├─ USER MANAGEMENT
│  ├─ create_user()
│  ├─ list_users()
│  ├─ toggle_user()
│  ├─ create_mysql_users()
│  └─ view_audit_log()
│
├─ ACADEMICS
│  ├─ admin_manage_academics()
│  ├─ faculty_assigned_subjects()
│  ├─ faculty_update_marks()
│  └─ faculty_manage_attendance()
│
├─ MENUS
│  ├─ menu_admin()
│  ├─ menu_faculty()
│  └─ menu_student()
│
└─ MAIN
   ├─ main()
   └─ if __name__ == "__main__"
```

---

## Deployment Architecture

```
Development Environment
├─ Local MySQL (localhost:3306)
├─ Single Python interpreter
└─ Test data

Production Environment (Recommended)
├─ Dedicated MySQL server
│  ├─ Regular backups
│  ├─ Replication (optional)
│  └─ Monitoring
│
├─ Application server
│  ├─ Python environment
│  ├─ PRN_spa.exe or Python runtime
│  └─ Connection pooling
│
├─ Security
│  ├─ SSL/TLS for DB connection
│  ├─ Firewall rules
│  └─ User authentication via AD/LDAP
│
└─ Monitoring
   ├─ Database performance monitoring
   ├─ Application logging
   └─ Audit trail review
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | May 22, 2026 | Initial release |

---

## References

- **Python Version**: 3.6+
- **MySQL Version**: 5.7+ or 8.0+
- **Libraries**: mysql.connector, pymysql, hashlib, csv, datetime, getpass

---

**Document Version**: 1.0  
**Last Updated**: May 22, 2026  
**Author**: DBMS Assignment Team
