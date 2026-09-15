# Student Attendance Management System

A Django-based attendance management system for administrators, teachers, and students.

The project includes student management, teacher accounts, subject assignments, attendance tracking, Django Admin, CSV/XLSX import and export, dashboards, and JWT-authenticated REST APIs.

## Features

- Manage students with name, registration number, class, roll number, and email
- Enforce unique student registration numbers and email addresses
- Support 60 or more students
- Create teacher accounts with employee IDs and subject assignments
- Support seven default subjects
- Authenticate teachers with Django Authentication
- Allow students to log in with registration number and registered name
- Mark attendance as `Present` or `Absent`
- Prevent duplicate attendance for the same student, subject, and date
- Allow teachers to edit only attendance records they created
- Give administrators full access through Django Admin
- Search, filter, import, and export records from Django Admin
- Provide admin and teacher dashboards
- Provide REST APIs protected by JWT authentication
- Use SQLite for local development
- Provide a responsive custom interface

## Technology

- Python
- Django
- Django REST Framework
- Simple JWT
- django-import-export
- OpenPyXL
- SQLite

## Project Structure

```text
manage.py
README.md
requirements.txt
students_sample.csv
teachers_sample.csv

config/
    settings.py
    urls.py
    asgi.py
    wsgi.py

attendance/
    models.py
    admin.py
    views.py
    forms.py
    permissions.py
    serializers.py
    api_views.py
    api_urls.py
    resources.py
    urls.py
    migrations/
    management/commands/
        load_students.py
        seed_teachers.py
    templates/attendance/
    static/attendance/
```

## Requirements

- Python 3.12 or newer
- PowerShell, Command Prompt, macOS Terminal, or Linux shell
- Internet access for installing Python packages

Check the installed Python version:

```powershell
python --version
```

## Installation on Windows

Open PowerShell in the project directory:

```powershell
cd D:\attendness_management_system
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If the virtual environment is already present, activate it with:

```powershell
.\venv\Scripts\Activate.ps1
```

You can also run commands without activating it:

```powershell
.\venv\Scripts\python.exe manage.py check
```

## Database Setup

This project uses SQLite by default. The local database file is `db.sqlite3`.

Apply the migrations:

```powershell
python manage.py migrate
```

Check the project configuration:

```powershell
python manage.py check
```

Create an administrator account:

```powershell
python manage.py createsuperuser
```

Enter the requested username, email, and password. Django stores the administrator password as a secure hash.

## Load Sample Data

### Create teachers and subjects

Run:

```powershell
python manage.py seed_teachers
```

This creates or updates seven subjects:

```text
IPS1
FMI1
ITC
PPWC
DPOS
CN
MLC1
```

It also creates seven teacher accounts with employee IDs from `TCH-001` to `TCH-007`.

The command writes the generated credentials to `teachers.csv`. This file is local-only and must not be uploaded to GitHub because it contains passwords.

### Load students

Load the included sample student data:

```powershell
python manage.py load_students
```

The included sample file contains 60 students.

Load another CSV file:

```powershell
python manage.py load_students --file path\to\students.csv
```

Expected CSV columns:

```csv
name,regd_no,class_name,roll_no,email
Aarav Sharma,REG001,CS-A,1,aarav.sharma@example.com
```

The loader also accepts these legacy column names:

```text
Name, Regd_No, Class, roll_No, Email
```

Registration number and email must be unique. Roll numbers may repeat in different classes.

## Run the Application

Start the development server:

```powershell
python manage.py runserver
```

Open the home page:

```text
http://127.0.0.1:8000/
```

Stop the server with `CTRL+C`.

## Application URLs

| Page | URL |
| --- | --- |
| Home | `http://127.0.0.1:8000/` |
| Student login | `http://127.0.0.1:8000/student/login/` |
| Student attendance | `http://127.0.0.1:8000/attendance/` |
| Teacher login | `http://127.0.0.1:8000/teacher/login/` |
| Teacher dashboard | `http://127.0.0.1:8000/teacher/dashboard/` |
| Django Admin | `http://127.0.0.1:8000/secure-admin/` |
| Admin dashboard | `http://127.0.0.1:8000/admin-dashboard/` |
| API root | `http://127.0.0.1:8000/api/` |

## Student Login

Students do not use passwords in the current version. They log in with their registration number and exact registered name.

Example:

```text
Registration number: REG001
Name: Aarav Sharma
```

The name comparison ignores uppercase and lowercase differences, but spelling must still be correct. For example, `Aarav Sharm` will not match `Aarav Sharma`.

Student passwords are not stored in the student CSV file.

## Teacher Login

Teachers use Django username and password authentication.

After running `seed_teachers`, open the local `teachers.csv` file to see the generated credentials. One example is:

```text
Username: harsh
Password: TCH-001
Subject: IPS1
```

The generated teacher passwords are initial passwords only. Change them before sharing the project with other users. Never upload `teachers.csv` to a public repository.

## Attendance Workflow

1. Log in through the teacher login page.
2. Open the teacher dashboard.
3. Select an assigned subject.
4. Select the attendance date.
5. Choose `Present` or `Absent` for each student.
6. Save the attendance.
7. Review the attendance summary on the dashboard.

The database prevents duplicate entries for the same student, subject, and date.

## User Roles

### Administrator

A Django superuser has full access to:

- Students
- Teachers
- Teacher profiles
- Subjects
- Attendance records
- Imports and exports
- Admin dashboard

### Teacher

A teacher is an active Django user with staff access and a `TeacherProfile`.

Teachers can:

- Log in through the teacher login page
- View their assigned subjects
- Mark attendance
- Edit attendance records they created
- View attendance summaries

Teachers cannot manage students, teachers, subjects, or attendance records created by another teacher.

## Django Admin

Open:

```text
http://127.0.0.1:8000/secure-admin/
```

Log in with the administrator account created by `createsuperuser`.

Django Admin supports:

- Add, edit, delete, and view students
- Search by name, registration number, class, roll number, and email
- Filter students by class
- Manage teacher users and employee IDs
- Assign one or more subjects to teachers
- Search subjects and teachers
- View and manage attendance records
- Filter attendance by class, subject, teacher, date, and status
- Import and export student, subject, and attendance data

### Import students from CSV or Excel

1. Open Django Admin.
2. Select `Students`.
3. Click `Import`.
4. Choose a CSV or XLSX file.
5. Review the import preview.
6. Confirm the import.

The same import/export functionality is available for the registered models that support resources.

## Data Model

### Student

- `name`
- `regd_no`, unique
- `class_name`
- `roll_no`
- `email`, unique

### TeacherProfile

- One-to-one link to a Django `User`
- Unique `employee_id`

### Subject

- Unique subject `code`
- Subject `name`
- Multiple assigned teachers

### AttendanceRecord

- `student`
- `teacher`, the user who created the record
- `subject`
- `date`
- `status`: `present` or `absent`
- Unique student, subject, and date combination

## REST API

The API is available under:

```text
http://127.0.0.1:8000/api/
```

### JWT token endpoints

Obtain a token:

```text
POST /api/token/
```

Request body:

```json
{
  "username": "harsh",
  "password": "TCH-001"
}
```

Refresh an expired access token:

```text
POST /api/token/refresh/
```

Request body:

```json
{
  "refresh": "your-refresh-token"
}
```

Send the access token with API requests:

```text
Authorization: Bearer your-access-token
```

### API resources

| Resource | Endpoint | Description |
| --- | --- | --- |
| Students | `/api/students/` | List and manage students |
| Teachers | `/api/teachers/` | View active staff teachers |
| Subjects | `/api/subjects/` | List and manage subjects |
| Attendance | `/api/attendance/` | Create and manage attendance |

Student and subject write operations require an administrator. Attendance creation automatically records the authenticated teacher.

Example attendance request:

```json
{
  "student": 1,
  "subject": 3,
  "date": "2026-09-15",
  "status": "present"
}
```

## Useful Commands

```powershell
# Check the project
python manage.py check

# Create migrations after changing models
python manage.py makemigrations

# Apply database migrations
python manage.py migrate

# Create an administrator
python manage.py createsuperuser

# Create seven teachers and seven subjects
python manage.py seed_teachers

# Load the sample students
python manage.py load_students

# Load students from another CSV
python manage.py load_students --file path\to\students.csv

# Start the development server
python manage.py runserver
```

## Troubleshooting

### Django cannot be imported

Activate the virtual environment:

```powershell
.\venv\Scripts\Activate.ps1
python manage.py runserver
```

### CSRF verification failed

Refresh the login page with `CTRL+F5`. The login pages are configured not to cache old CSRF tokens. Also confirm that browser cookies are enabled and that you are using `127.0.0.1` consistently.

### Student login fails

Check the registration number and exact spelling of the student name. For example:

```text
REG001 + Aarav Sharma
```

### Migrations are pending

Run:

```powershell
python manage.py makemigrations
python manage.py migrate
```

### Seed command fails

Apply migrations before seeding:

```powershell
python manage.py migrate
python manage.py seed_teachers
```

## Security Notes

- Do not upload `teachers.csv` to GitHub.
- Do not upload `.env` files or database passwords.
- Do not commit `db.sqlite3` if it contains private data.
- Change all generated teacher passwords before sharing the project.
- Keep `DJANGO_SECRET_KEY` outside source control when using a shared environment.
- Use the provided `.env.example` only as a configuration reference.
