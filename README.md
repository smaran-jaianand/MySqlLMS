# Student Performance Analyzer (CLI Version)

A standalone, fully relational database management terminal application. This project provides full access to academic management, student profiles, grading reports, and class attendance registers.

## Project Structure
- `setup_db.py`: Connects to local MySQL and configures all schemas, constraints, defaults, views, and initial roles/permissions.
- `analyzer.py`: The executable's source terminal script.
- `dist/PRN_spa.exe`: The single-file packaged standalone executable.
- `requirements.txt`: List of dependencies.
- `build_cli.bat`: Script to package the application.

## Prerequisites
- **MySQL Server** running locally.
- **Python 3.x** (if running from source).
- Python package `pymysql` (if running from source).

## Installation & Setup

### 1. Database Setup
Ensure your MySQL server is running, then execute the database setup script to initialize the database:
```bash
python setup_db.py
```
This will recreate the `spa_db` database, configure the views and tables, and insert the default admin account:
* **Admin Username**: `admin`
* **Admin Password**: `admin123`

### 2. Run the Application
You can run the application directly using the precompiled executable:
```bash
dist\PRN_spa.exe
```
Or run from source:
```bash
python analyzer.py
```
