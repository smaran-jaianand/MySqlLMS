# SPA Quick Reference Guide

## Quick Start

### 1. Launch Application
```bash
python PRN_analyzer.py
# or
PRN_spa.exe
```

### 2. First Login (Default Admin)
```
Username: admin
Password: admin123
```

### 3. Create Test Records
- Admin Menu → Option 2: Add Student Record
- Admin Menu → Option 13: Create User Account
- Admin Menu → Option 18: Manage Academic Subjects

---

## Admin Quick Commands

| Goal | Menu Path |
|------|-----------|
| View all students | Menu 3 |
| Add new student | Menu 2 |
| Update student profile | Menu 5 |
| Delete student | Menu 6 |
| View analytics | Menu 7 |
| Check grades distribution | Menu 8 |
| See top 10 students | Menu 9 |
| Department ranking | Menu 10 |
| Award bonus marks | Menu 11 |
| Export to CSV | Menu 12 |
| Create user (any role) | Menu 13 |
| List all accounts | Menu 14 |
| Disable account | Menu 15 |
| View security logs | Menu 17 |
| Manage subjects | Menu 18 |

---

## Faculty Quick Commands

| Goal | Menu Path |
|------|-----------|
| View my subjects | Menu 1 |
| Grade students | Menu 2 |
| Mark attendance | Menu 3 → Menu 1 |
| View attendance logs | Menu 3 → Menu 2 |
| Dashboard stats | Menu 4 |
| Top performers | Menu 5 |
| Department ranking | Menu 6 |

---

## Student Quick Commands

| Goal | Menu Path |
|------|-----------|
| My academic record | Menu 1 |
| Top performers | Menu 2 |
| Department ranking | Menu 3 |

---

## Key Database Terms

| Term | Meaning |
|------|---------|
| PRN | Permanent Registration Number (11 digits) |
| Batch | Academic year (e.g., 2025) |
| Rolling Average | Average of all subject marks |
| Audit Log | Security record of all actions |
| Enrollment | Student registered in a subject |
| Assignment | Faculty teaching a subject |

---

## Valid Input Formats

### PRN Format
```
Format: YY0AABBCRRR (11 digits)
Example: 25007011001

YY = Year (25, 26, 27)
0 = Fixed zero
AA = Category (06, 07)
BB = Branch (01, 02, 03, 04, 05, 06)
C = Section (1, 2, 3)
RRR = Roll Number (000-999)
```

### Date Format
```
Format: YYYY-MM-DD
Example: 2026-05-22
Leave blank for today's date
```

### Marks Format
```
Range: 0 to 100
Can be decimal: 85.5, 92.25
NULL allowed (not graded yet)
```

---

## Error Messages & Solutions

| Error | Cause | Fix |
|-------|-------|-----|
| "Invalid credentials" | Wrong password | Re-enter password |
| "Account disabled" | User disabled | Admin must enable |
| "PRN must be 11 digits" | Wrong PRN format | Use YY0AABBCRRR format |
| "Duplicate entry" | Record exists | Use different value |
| "Cannot connect" | MySQL offline | Start MySQL server |
| "Cannot disable own account" | Admin self-disable | Ask another admin |

---

## Common Workflows

### Add & Grade a Student

1. **Create Student**: Admin → Menu 2
   - PRN: `25007011001`
   - Name: `John Doe`
   - Department: `CS`

2. **Create Subject**: Admin → Menu 18 → Option 1
   - Code: `CS101`
   - Name: `Data Structures`
   - Batch: `2025`

3. **Enroll Student**: Admin → Menu 18 → Option 2
   - Subject ID: 1
   - Student PRN: `25007011001`

4. **Assign Faculty**: Admin → Menu 18 → Option 3
   - Faculty PRN: `25006011001`
   - Subject ID: 1

5. **Grade Student**: Faculty → Menu 2
   - Subject ID: 1
   - Student PRN: `25007011001`
   - Marks: 85

---

### Track Student Attendance

1. **Faculty Mark Attendance**: Faculty → Menu 3 → Option 1
   - Subject ID: 1
   - Date: (blank for today)
   - Mark each student P or A

2. **View Attendance**: Faculty → Menu 3 → Option 2
   - Subject ID: 1
   - See summary by date

3. **Student View**: Student → Menu 1
   - See attendance % per subject

---

### Analyze Performance

1. **Dashboard**: Admin → Menu 1
   - Total students
   - Average marks
   - Grade distribution

2. **By Department**: Admin → Menu 7
   - Each department's average
   - Highest and lowest

3. **Top Performers**: Admin → Menu 9
   - Top 10 students with marks ≥ 60

4. **Export**: Admin → Menu 12
   - CSV file of above-average students

---

## Database Views

### vw_student_grades
Shows each student with letter grade:
```
PRN | Name | Department | Marks | Grade
25007011001 | John Doe | CS | 85.00 | B
```

### vw_department_leaderboard
Department statistics:
```
Department | Total Students | Avg Marks | Highest | Lowest
CS | 45 | 75.5 | 98 | 42
```

---

## Important Passwords to Remember

| User | PRN/Username | Default Password |
|------|--------------|------------------|
| Admin | admin | admin123 |
| Faculty Sample | 25006011001 | (set during creation) |
| Student Sample | 25007011001 | (set during creation) |

⚠️ **Change default admin password after first login!**

---

## Grading Scale

| Grade | Range | Meaning |
|-------|-------|---------|
| A | 90-100 | Excellent |
| B | 75-89 | Good |
| C | 60-74 | Satisfactory |
| D | 40-59 | Pass |
| F | <40 | Fail |

---

## System Tables Summary

| Table | Purpose | Owner |
|-------|---------|-------|
| `users` | Admin accounts | Admins |
| `students` | Student profiles | Admins |
| `faculty` | Faculty profiles | Admins |
| `subjects` | Course catalog | Admins |
| `student_subjects` | Enrollments & grades | Admins/Faculty |
| `faculty_subjects` | Teaching assignments | Admins |
| `attendance` | Daily roll call | Faculty |
| `audit_log` | Security trail | System |

---

## Tips & Best Practices

1. **Always backup database regularly**
   ```bash
   mysqldump -u root -p spa_enhanced_db > backup.sql
   ```

2. **Disable inactive accounts** instead of deleting
   - Preserves historical data
   - Can re-enable if needed

3. **Use export feature** for reports
   - Creates CSV files
   - Can open in Excel

4. **Check audit logs** periodically
   - See who did what and when
   - Security monitoring

5. **Mark attendance daily**
   - Faculty should mark same day
   - Easier to remember attendance

6. **Award bonus marks carefully**
   - Applies to entire department
   - Caps at 100 marks

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Ctrl+C | Exit application |
| Enter | Confirm input |
| Enter (blank) | Skip optional field |

---

## File Output Locations

**CSV Exports**: Same directory as executable
```
high_performers_20260522_143022.csv
```

**Format**: 
```csv
PRN,Name,Department,Rolling Average
25007011001,John Doe,CS,85.50
25007011002,Jane Smith,CS,92.00
```

---

## Default Port & Connection

```
MySQL Host: localhost
MySQL Port: 3306
Database: spa_enhanced_db
Charset: utf8mb4
```

---

## Role Capabilities Matrix

```
Feature                    | Admin | Faculty | Student
--------------------------|-------|---------|--------
Add Student               | ✓     | ✗       | ✗
Grade Students            | ✗     | ✓       | ✗
Mark Attendance           | ✗     | ✓       | ✗
View All Records          | ✓     | ✗       | ✗
View Own Record           | ✓     | ✓       | ✓
View Analytics            | ✓     | ✓(RO)   | ✓(RO)
Manage Users              | ✓     | ✗       | ✗
Export Data               | ✓     | ✗       | ✗
View Audit Log            | ✓     | ✗       | ✗
```

Legend: ✓=Can do, ✗=Cannot, RO=Read-only

---

## Session Timeout

**No automatic timeout**. User must:
- Click "0. Logout" to logout
- Press Ctrl+C to exit
- Close application window

---

## Troubleshooting Quick Links

**Problem** | **Quick Fix**
--|--
Can't connect | Start MySQL, check host
Forgot password | Admin menu 15, toggle & reset
Duplicate entry | Different value or update
Invalid PRN | Use format YY0AABBCRRR
Attendance not saved | Check faculty assignment
Marks not updating | Faculty must update per subject

---

## Support Information

- Check the full SYSTEM_MANUAL.md for detailed help
- Review audit logs for action history
- Verify database schema with SHOW TABLES
- Test with sample data before production use

---

**Version**: 1.0  
**Last Updated**: May 22, 2026
