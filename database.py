"""
database.py - Database Management Module
==================================================
Handles SQLite3 database connection, table initialization,
foreign key constraint enforcement, and sample data seeding
for the Student Management System.
"""

import sqlite3
import os

# Default database filename in current directory
DB_NAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "student_management.db")


def get_connection(db_name=DB_NAME):
    """
    Establishes and returns a SQLite3 database connection.
    Enforces foreign key support on the connection.
    """
    conn = sqlite3.connect(db_name)
    # Enable foreign key constraint support in SQLite
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(db_name=DB_NAME):
    """
    Initializes the database by creating all required tables
    if they do not already exist, and seeds the default admin user.
    """
    conn = get_connection(db_name)
    cursor = conn.cursor()

    try:
        # 1. Users Table (Authentication)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            );
        """)

        # 2. Students Table (Master Entity)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                roll_no TEXT UNIQUE NOT NULL,
                course TEXT NOT NULL,
                branch TEXT NOT NULL,
                semester TEXT NOT NULL,
                dob TEXT NOT NULL,
                gender TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT NOT NULL,
                address TEXT NOT NULL
            );
        """)

        # 3. Marks Table (Child Entity with CASCADE delete)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS marks (
                mark_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                subject TEXT NOT NULL,
                internal_marks REAL NOT NULL,
                external_marks REAL NOT NULL,
                total_marks REAL NOT NULL,
                percentage REAL NOT NULL,
                grade TEXT NOT NULL,
                FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
            );
        """)

        # 4. Attendance Table (Child Entity with CASCADE delete)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                subject TEXT NOT NULL,
                total_classes INTEGER NOT NULL,
                classes_attended INTEGER NOT NULL,
                attendance_percentage REAL NOT NULL,
                FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
            );
        """)

        # Seed default admin credentials if not already present
        cursor.execute("SELECT * FROM users WHERE username = ?", ("admin",))
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                ("admin", "admin123")
            )

        conn.commit()

        # Seed initial sample data if students table is empty
        cursor.execute("SELECT COUNT(*) FROM students")
        student_count = cursor.fetchone()[0]
        if student_count == 0:
            seed_sample_data(conn)

    except sqlite3.Error as e:
        print(f"[Database Error]: Failed to initialize database: {e}")
        conn.rollback()
        raise e
    finally:
        conn.close()


def seed_sample_data(conn):
    """
    Seeds initial sample college student records, marks, and attendance
    so the system is ready for demonstration right out of the box.
    """
    cursor = conn.cursor()
    sample_students = [
        ("STU101", "Aarav Sharma", "21CS001", "B.Tech", "Computer Science", "6th", "2003-05-14", "Male", "9876543210", "aarav.sharma@example.com", "Sector 62, Noida, UP"),
        ("STU102", "Priya Verma", "21CS002", "B.Tech", "Computer Science", "6th", "2003-08-22", "Female", "9812345678", "priya.verma@example.com", "Indirapuram, Ghaziabad, UP"),
        ("STU103", "Rohan Gupta", "21IT001", "B.Tech", "Information Technology", "6th", "2002-11-30", "Male", "9898765432", "rohan.gupta@example.com", "Rohini Sector 9, New Delhi"),
        ("STU104", "Ananya Singh", "22CS015", "B.Tech", "Computer Science", "4th", "2004-01-18", "Female", "9711223344", "ananya.singh@example.com", "South Extension, New Delhi"),
        ("STU105", "Kabir Mehta", "21EC005", "B.Tech", "Electronics & Comm", "6th", "2003-03-09", "Male", "9654321987", "kabir.mehta@example.com", "DLF Phase 3, Gurugram, HR")
    ]

    for student in sample_students:
        cursor.execute("""
            INSERT INTO students (student_id, name, roll_no, course, branch, semester, dob, gender, phone, email, address)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, student)

    sample_marks = [
        # Aarav (STU101)
        ("STU101", "Database Management Systems", 28, 65, 93, 93.0, "A+"),
        ("STU101", "Operating Systems", 26, 62, 88, 88.0, "A"),
        ("STU101", "Computer Networks", 27, 64, 91, 91.0, "A+"),
        # Priya (STU102)
        ("STU102", "Database Management Systems", 25, 58, 83, 83.0, "A"),
        ("STU102", "Operating Systems", 24, 52, 76, 76.0, "B+"),
        ("STU102", "Computer Networks", 26, 60, 86, 86.0, "A"),
        # Rohan (STU103)
        ("STU103", "Database Management Systems", 20, 42, 62, 62.0, "B"),
        ("STU103", "Operating Systems", 18, 38, 56, 56.0, "C"),
        ("STU103", "Computer Networks", 22, 45, 67, 67.0, "B"),
        # Ananya (STU104)
        ("STU104", "Data Structures & Algorithms", 29, 68, 97, 97.0, "A+"),
        ("STU104", "Discrete Mathematics", 27, 65, 92, 92.0, "A+"),
        # Kabir (STU105)
        ("STU105", "Digital Signal Processing", 15, 23, 38, 38.0, "F"),
        ("STU105", "Microprocessors", 18, 28, 46, 46.0, "D")
    ]

    for mark in sample_marks:
        cursor.execute("""
            INSERT INTO marks (student_id, subject, internal_marks, external_marks, total_marks, percentage, grade)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, mark)

    sample_attendance = [
        # Aarav (STU101)
        ("STU101", "Database Management Systems", 40, 37, 92.5),
        ("STU101", "Operating Systems", 40, 36, 90.0),
        ("STU101", "Computer Networks", 40, 38, 95.0),
        # Priya (STU102)
        ("STU102", "Database Management Systems", 40, 32, 80.0),
        ("STU102", "Operating Systems", 40, 31, 77.5),
        ("STU102", "Computer Networks", 40, 34, 85.0),
        # Rohan (STU103)
        ("STU103", "Database Management Systems", 40, 27, 67.5),
        ("STU103", "Operating Systems", 40, 26, 65.0),
        ("STU103", "Computer Networks", 40, 25, 62.5),
        # Ananya (STU104)
        ("STU104", "Data Structures & Algorithms", 40, 39, 97.5),
        ("STU104", "Discrete Mathematics", 40, 38, 95.0),
        # Kabir (STU105)
        ("STU105", "Digital Signal Processing", 40, 21, 52.5),
        ("STU105", "Microprocessors", 40, 22, 55.0)
    ]

    for att in sample_attendance:
        cursor.execute("""
            INSERT INTO attendance (student_id, subject, total_classes, classes_attended, attendance_percentage)
            VALUES (?, ?, ?, ?, ?)
        """, att)

    conn.commit()


if __name__ == "__main__":
    init_db()
    print("[Database]: Database initialized and seeded successfully.")
