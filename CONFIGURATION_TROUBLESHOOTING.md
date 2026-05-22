# SPA Configuration & Troubleshooting Guide

## Configuration

### Database Configuration

Edit the `DB_CONFIG` dictionary in `PRN_analyzer.py`:

```python
DB_CONFIG = {
    "host": "localhost",        # MySQL server address
    "user": "root",            # MySQL username
    "password": "mysql",       # MySQL password
    "database": "spa_enhanced_db"  # Database name
}
```

### Configuration Examples

#### Local Development
```python
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "spa_enhanced_db"
}
```

#### Remote MySQL Server
```python
DB_CONFIG = {
    "host": "192.168.1.100",
    "user": "spa_app_user",
    "password": "secure_password_123",
    "database": "spa_enhanced_db"
}
```

#### Docker MySQL
```python
DB_CONFIG = {
    "host": "mysql_container",
    "user": "root",
    "password": "docker_pass",
    "database": "spa_enhanced_db"
}
```

#### Cloud Database (AWS RDS)
```python
DB_CONFIG = {
    "host": "spa-db.c123456789.us-east-1.rds.amazonaws.com",
    "user": "admin",
    "password": "rds_password",
    "database": "spa_enhanced_db"
}
```

---

## Installation Troubleshooting

### Problem 1: "MySQL Server not running"

**Error Message**:
```
ERROR 2003 (HY000): Can't connect to MySQL server on 'localhost:3306'
```

**Solutions**:

1. **Check MySQL Service Status** (Windows):
   ```bash
   sc query MySQL80
   # or
   Get-Service -Name MySQL80
   ```

2. **Start MySQL Service** (Windows):
   ```bash
   net start MySQL80
   # or (PowerShell as Admin)
   Start-Service -Name MySQL80
   ```

3. **Start MySQL Service** (Linux):
   ```bash
   sudo service mysql start
   # or
   sudo systemctl start mysql
   ```

4. **Verify MySQL is Listening**:
   ```bash
   netstat -an | grep 3306
   # Should show: LISTENING on 127.0.0.1:3306
   ```

---

### Problem 2: "Access denied for user 'root'@'localhost'"

**Error Message**:
```
ERROR 1045 (28000): Access denied for user 'root'@'localhost' (using password: YES)
```

**Solutions**:

1. **Verify Password**:
   ```bash
   mysql -h localhost -u root -p
   # Enter the password you configured
   ```

2. **Test with Different User**:
   ```bash
   mysql -h localhost -u sa_admin -p
   ```

3. **Reset Root Password** (if forgotten):
   ```bash
   # Windows - Stop MySQL
   net stop MySQL80
   
   # Start with skip-grant-tables
   mysqld --skip-grant-tables
   
   # In another terminal
   mysql -u root
   FLUSH PRIVILEGES;
   ALTER USER 'root'@'localhost' IDENTIFIED BY 'newpassword';
   EXIT;
   ```

4. **Update DB_CONFIG** with correct credentials:
   ```python
   DB_CONFIG = {
       "host": "localhost",
       "user": "root",
       "password": "your_actual_password",  # Change this
       "database": "spa_enhanced_db"
   }
   ```

---

### Problem 3: "Database 'spa_enhanced_db' doesn't exist"

**Error Message**:
```
ERROR 1049 (42000): Unknown database 'spa_enhanced_db'
```

**Solution**: Run application once - it auto-creates the database

```bash
python PRN_analyzer.py
# Application will:
# 1. Detect missing database
# 2. Create spa_enhanced_db
# 3. Create all tables
# 4. Insert default admin
```

---

### Problem 4: "Cannot import mysql.connector"

**Error Message**:
```
ModuleNotFoundError: No module named 'mysql'
```

**Solution**: Install MySQL connector

```bash
pip install mysql-connector-python
```

**Alternative** (PyMySQL):
```bash
pip install pymysql
# Application uses pymysql as fallback automatically
```

---

### Problem 5: "Module 'getpass' not found"

**Error Message**:
```
ModuleNotFoundError: No module named 'getpass'
```

**Solution**: getpass is built-in with Python - upgrade Python

```bash
python --version  # Should be 3.6+
```

---

## Application Startup Troubleshooting

### Problem 6: "Invalid database character set"

**Error Message**:
```
ERROR 1253: COLLATION 'utf8mb4_unicode_ci' is not valid
```

**Solution**: Check MySQL version and update character set

```sql
-- Check available collations
SHOW COLLATION LIKE 'utf8%';

-- Use utf8_unicode_ci if utf8mb4_unicode_ci not available
-- Modify DB_CONFIG or database creation
```

---

### Problem 7: "No records found" when adding data

**Issue**: Data added but not appearing

**Solution**: Check if data is committed

```sql
-- View students table
SELECT * FROM students;

-- If empty, data wasn't committed
-- Check for transaction errors in console
```

---

### Problem 8: "Cannot disable own admin account"

**Expected Behavior**: Admin cannot disable their own active session

```
This is intentional!
To disable your account:
1. Create another admin account
2. Login with that account
3. Disable the first admin account
```

---

## Login Issues

### Problem 9: "Invalid credentials"

**Scenarios**:

1. **Wrong Password**:
   - Re-enter password carefully
   - Password is case-sensitive
   - No extra spaces

2. **Wrong Username/PRN**:
   - Admin login: username (e.g., "admin")
   - Faculty login: PRN (e.g., "25006011001")
   - Student login: PRN (e.g., "25007011001")

3. **Account Disabled**:
   - Contact admin
   - Admin can re-enable: Menu 15 → Toggle User

4. **Typos in DB_CONFIG**:
   - Check username/password in DB_CONFIG
   - Verify database name
   - Test connection with mysql CLI

**Test Login**:
```bash
mysql -h localhost -u root -p spa_enhanced_db
# If successful, application should connect too
```

---

### Problem 10: "Account disabled" on login

**Solution**: Contact system administrator

```
Admin can re-enable:
1. Login as admin
2. Menu: 15. Toggle User Active status
3. Enter role and username/PRN
4. Account is now enabled
```

---

## Data Entry Issues

### Problem 11: "PRN must be 11 digits in YY0AABBCRRR format"

**Issue**: PRN validation error

**Valid Format**:
```
Pattern: YY0AABBCRRR (11 digits)
YY = 25, 26, or 27 (year)
0 = Fixed digit
AA = 06 or 07 (category)
BB = 01-06 (branch)
C = 1, 2, or 3 (section)
RRR = 000-999 (roll number)
```

**Examples**:
```
Valid PRNs:
- 25007011001
- 26006021234
- 27007031999

Invalid PRNs:
- 2507011001 (10 digits - too short)
- 25008011001 (AA=08, must be 06-07)
- 25007071001 (BB=07, must be 01-06)
- 25007010001 (C=0, must be 1-3)
```

---

### Problem 12: "Marks must be between 0 and 100"

**Solution**: Enter valid marks

```
Valid range: 0.00 to 100.00
Examples:
- 95.50 (valid)
- 100 (valid)
- 0 (valid)
- 75.25 (valid)
- 105 (invalid - too high)
- -5 (invalid - negative)
```

---

### Problem 13: "Duplicate entry for key"

**Common Causes**:

1. **Duplicate PRN**:
   ```
   Solution: Use different PRN
   Or: Update existing record instead
   ```

2. **Duplicate Subject Code in Batch**:
   ```
   Solution: Use different code or batch
   ```

3. **Duplicate Attendance**:
   ```
   Solution: Record already exists
   System will update if you try again
   ```

---

## Database Issues

### Problem 14: "Cannot connect after many operations"

**Cause**: Connection timeout or too many open connections

**Solution**:

1. **Restart Application**:
   ```bash
   # Exit current session
   Press Ctrl+C
   
   # Restart
   python PRN_analyzer.py
   ```

2. **Check MySQL Connection Limit**:
   ```sql
   SHOW VARIABLES LIKE 'max_connections';
   SET GLOBAL max_connections = 1000;
   ```

3. **Kill Idle Connections**:
   ```sql
   SHOW PROCESSLIST;
   KILL <connection_id>;
   ```

---

### Problem 15: "Out of memory" or "Table is full"

**Cause**: Database size exceeded limit

**Solution**:

1. **Archive Old Data**:
   ```sql
   -- Backup old audit logs
   SELECT * FROM audit_log WHERE timestamp < DATE_SUB(NOW(), INTERVAL 6 MONTH);
   
   -- Delete old records
   DELETE FROM audit_log WHERE timestamp < DATE_SUB(NOW(), INTERVAL 1 YEAR);
   ```

2. **Optimize Tables**:
   ```sql
   OPTIMIZE TABLE students;
   OPTIMIZE TABLE attendance;
   OPTIMIZE TABLE audit_log;
   ```

3. **Check Disk Space**:
   ```bash
   # Linux/Mac
   df -h
   
   # Windows (PowerShell)
   Get-Volume
   ```

---

### Problem 16: "Slow query" or "Application freezing"

**Causes**: Large dataset or missing indexes

**Solutions**:

1. **Add Indexes**:
   ```sql
   CREATE INDEX idx_students_dept ON students(department);
   CREATE INDEX idx_attendance_date ON attendance(date);
   ```

2. **Limit Result Sets**:
   - Use search/filter instead of viewing all
   - Menu 4: Search by department instead of Menu 3: View all

3. **Archive Old Data**:
   - Remove old attendance records
   - Remove inactive users

4. **Check Performance**:
   ```sql
   SHOW PROCESSLIST;  -- See running queries
   KILL QUERY <id>;   -- Stop long-running query
   ```

---

## Feature-Specific Issues

### Problem 17: "Attendance not saving"

**Cause**: Faculty not assigned to subject

**Solution**:
1. Admin Menu 18: Manage Academic Subjects
2. Option 3: Assign Faculty to Subject
3. Try marking attendance again

---

### Problem 18: "Student marks not updating overall average"

**Cause**: Manual update needed after grade entry

**Solution**:
- Application automatically recalculates
- If not working:
  1. Exit and restart application
  2. Faculty re-enter the marks
  3. Check audit log for errors

---

### Problem 19: "Cannot export to CSV"

**Causes**:
1. File permission denied
2. Disk full
3. Invalid filename characters

**Solutions**:

1. **Check File Path**:
   ```python
   # CSV files created in current directory
   # Run from a directory with write permissions
   ```

2. **Manual Export** (SQL):
   ```sql
   SELECT * FROM students 
   INTO OUTFILE 'C:/path/to/export.csv'
   FIELDS TERMINATED BY ','
   LINES TERMINATED BY '\n';
   ```

---

### Problem 20: "Bonus marks not applying"

**Causes**:
1. Wrong department name (case-sensitive in query)
2. Marks already at 100 (LEAST caps at 100)

**Solution**:

1. **Verify Department Name**:
   ```sql
   SELECT DISTINCT department FROM students;
   ```

2. **Check Query**:
   ```sql
   SELECT COUNT(*) FROM students 
   WHERE LOWER(department) = LOWER('Computer Science');
   ```

---

## Performance Optimization

### Optimize for Large Dataset (>10,000 students)

1. **Add Indexes**:
   ```sql
   CREATE INDEX idx_students_marks ON students(marks);
   CREATE INDEX idx_students_dept ON students(department);
   CREATE INDEX idx_attendance_date ON attendance(date);
   ```

2. **Partition Tables** (MySQL 5.7+):
   ```sql
   ALTER TABLE attendance PARTITION BY RANGE(YEAR(date)) (
       PARTITION p2024 VALUES LESS THAN (2025),
       PARTITION p2025 VALUES LESS THAN (2026),
       PARTITION p2026 VALUES LESS THAN (2027)
   );
   ```

3. **Limit Result Sets** (modify application):
   ```python
   # Add LIMIT to queries
   cursor.execute("SELECT * FROM students LIMIT 100 OFFSET ?", (page*100,))
   ```

---

## Security Hardening

### Change Default Admin Password

1. **Login as admin**
2. **Exit to command line** (Ctrl+C)
3. **Update MySQL directly**:
   ```bash
   mysql -u root -p spa_enhanced_db
   ```
   ```sql
   UPDATE users 
   SET password_hash = SHA2('newpassword', 256) 
   WHERE username = 'admin';
   ```

4. **Update DB_CONFIG** if password changed:
   ```python
   DB_CONFIG = {
       "user": "root",
       "password": "newpassword",  # Update here
       ...
   }
   ```

---

### Enable SSL for Database Connection

1. **Generate SSL Certificates** (MySQL):
   ```bash
   # MySQL generates certs automatically
   # or use existing certs
   ```

2. **Enable SSL in Config**:
   ```python
   # For mysql.connector
   config = {
       "host": "localhost",
       "user": "root",
       "password": "password",
       "database": "spa_enhanced_db",
       "ssl_ca": "/path/to/ca.pem",
       "ssl_cert": "/path/to/cert.pem",
       "ssl_key": "/path/to/key.pem"
   }
   ```

---

## Backup & Recovery

### Regular Backups

**Daily Backup Script** (Windows batch):
```batch
@echo off
set BACKUP_DIR=C:\Backups\SPA
set TIMESTAMP=%date:~10,4%%date:~4,2%%date:~7,2%_%time:~0,2%%time:~3,2%%time:~6,2%

mkdir %BACKUP_DIR% 2>nul

"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump" ^
    -u root -p^password ^
    spa_enhanced_db > %BACKUP_DIR%\spa_backup_%TIMESTAMP%.sql

echo Backup completed: %BACKUP_DIR%\spa_backup_%TIMESTAMP%.sql
```

**Daily Backup Script** (Linux cron):
```bash
# Add to crontab -e
0 2 * * * mysqldump -u root -p'password' spa_enhanced_db > /backups/spa_$(date +\%Y\%m\%d_\%H\%M\%S).sql
```

---

### Restore from Backup

```bash
# Restore entire database
mysql -u root -p spa_enhanced_db < backup_20260522_143022.sql

# Restore specific table
mysql -u root -p spa_enhanced_db -e "SOURCE /path/to/table_backup.sql"
```

---

## Monitoring & Maintenance

### Check System Health

```sql
-- Check database size
SELECT 
    ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) as size_mb
FROM information_schema.TABLES
WHERE table_schema = 'spa_enhanced_db';

-- Check record counts
SELECT 'students' as tbl, COUNT(*) as cnt FROM students
UNION ALL
SELECT 'attendance', COUNT(*) FROM attendance
UNION ALL
SELECT 'audit_log', COUNT(*) FROM audit_log;

-- Check for orphaned records
SELECT * FROM attendance 
WHERE student_prn NOT IN (SELECT prn FROM students);

-- Check slow queries
SHOW FULL PROCESSLIST;
```

---

### Maintenance Schedule

| Task | Frequency | Command |
|------|-----------|---------|
| Backup database | Daily | mysqldump |
| Check disk space | Weekly | df -h |
| Optimize tables | Monthly | OPTIMIZE TABLE |
| Review audit logs | Weekly | SELECT from audit_log |
| Remove old logs | Quarterly | DELETE old audit_log |
| Update indexes | As needed | ANALYZE TABLE |

---

## Support Resources

**Quick Checks**:
1. Check SYSTEM_MANUAL.md for function details
2. Check QUICK_REFERENCE.md for common tasks
3. Review DATABASE_SCHEMA.md for SQL help
4. Check audit logs for error messages

**MySQL Help**:
```bash
# Get help for MySQL commands
mysql --help
mysql -u root -p -e "HELP SELECT"
```

**Python Debugging**:
```bash
# Run with error traceback
python -u PRN_analyzer.py 2>&1 | tee log.txt
```

---

**Version**: 1.0  
**Last Updated**: May 22, 2026
