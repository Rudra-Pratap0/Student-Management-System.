"""
test_system.py - Automated Unit & Integration Test Suite
=========================================================
Verifies database initialization, foreign key cascade constraints,
validation rules, CRUD operations, calculations, and reporting queries.
"""

import os
import sqlite3
import unittest

from database import init_db, get_connection
from utils import (
    validate_required, validate_email, validate_phone, validate_date,
    validate_marks, validate_attendance, calculate_grade, get_attendance_status
)


class TestStudentManagementSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Use a temporary test database
        cls.test_db = "test_student_mgmt.db"
        if os.path.exists(cls.test_db):
            os.remove(cls.test_db)
        init_db(cls.test_db)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_db):
            try:
                os.remove(cls.test_db)
            except Exception:
                pass

    def test_01_database_tables_and_admin(self):
        """Verify all tables exist and admin user is created."""
        conn = get_connection(self.test_db)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [t[0] for t in cursor.fetchall()]
        self.assertIn("users", tables)
        self.assertIn("students", tables)
        self.assertIn("marks", tables)
        self.assertIn("attendance", tables)

        cursor.execute("SELECT username, password FROM users WHERE username = 'admin'")
        admin = cursor.fetchone()
        self.assertIsNotNone(admin)
        self.assertEqual(admin[0], "admin")
        self.assertEqual(admin[1], "admin123")
        conn.close()

    def test_02_validation_utilities(self):
        """Verify input validation rules."""
        # Email
        self.assertTrue(validate_email("student@college.edu")[0])
        self.assertTrue(validate_email("test.user@domain.co.in")[0])
        self.assertFalse(validate_email("invalid_email.com")[0])
        self.assertFalse(validate_email("abc@")[0])

        # Phone
        self.assertTrue(validate_phone("9876543210")[0])
        self.assertTrue(validate_phone("+91 9876543210")[0])
        self.assertFalse(validate_phone("12345")[0])
        self.assertFalse(validate_phone("987654321012")[0])

        # Date
        self.assertTrue(validate_date("2003-05-14")[0])
        self.assertFalse(validate_date("14-05-2003")[0])
        self.assertFalse(validate_date("2099-01-01")[0])  # future date

        # Marks
        valid, _, _, _, total = validate_marks("25", "60")
        self.assertTrue(valid)
        self.assertEqual(total, 85.0)
        self.assertFalse(validate_marks("35", "60")[0])  # internal > 30
        self.assertFalse(validate_marks("25", "75")[0])  # external > 70
        self.assertFalse(validate_marks("abc", "60")[0])  # non-numeric

        # Attendance
        valid, _, _, _, pct = validate_attendance("40", "32")
        self.assertTrue(valid)
        self.assertEqual(pct, 80.0)
        self.assertFalse(validate_attendance("40", "45")[0])  # attended > total
        self.assertFalse(validate_attendance("0", "0")[0])   # total <= 0

    def test_03_academic_formulas(self):
        """Verify grading and attendance status logic."""
        self.assertEqual(calculate_grade(95), "A+")
        self.assertEqual(calculate_grade(85), "A")
        self.assertEqual(calculate_grade(75), "B+")
        self.assertEqual(calculate_grade(65), "B")
        self.assertEqual(calculate_grade(55), "C")
        self.assertEqual(calculate_grade(45), "D")
        self.assertEqual(calculate_grade(35), "F")

        self.assertEqual(get_attendance_status(85.0), "Good")
        self.assertEqual(get_attendance_status(75.0), "Good")
        self.assertEqual(get_attendance_status(70.0), "Average")
        self.assertEqual(get_attendance_status(60.0), "Average")
        self.assertEqual(get_attendance_status(55.0), "Low")

    def test_04_student_crud(self):
        """Verify student record insertion, duplicate checks, and updates."""
        conn = get_connection(self.test_db)
        cursor = conn.cursor()

        # Insert new student
        cursor.execute("""
            INSERT INTO students VALUES (
                'TEST001', 'Test Student', '99CS001', 'B.Tech', 'Computer Science',
                '5th', '2002-04-12', 'Male', '9899001122', 'test@college.edu', 'Delhi'
            )
        """)
        conn.commit()

        # Duplicate ID check
        with self.assertRaises(sqlite3.IntegrityError):
            cursor.execute("""
                INSERT INTO students VALUES (
                    'TEST001', 'Another Name', '99CS002', 'B.Tech', 'Computer Science',
                    '5th', '2002-04-12', 'Male', '9899001123', 'test2@college.edu', 'Delhi'
                )
            """)

        # Duplicate Roll No check
        with self.assertRaises(sqlite3.IntegrityError):
            cursor.execute("""
                INSERT INTO students VALUES (
                    'TEST002', 'Another Name', '99CS001', 'B.Tech', 'Computer Science',
                    '5th', '2002-04-12', 'Male', '9899001123', 'test2@college.edu', 'Delhi'
                )
            """)

        # Update student
        cursor.execute("UPDATE students SET name = 'Updated Name' WHERE student_id = 'TEST001'")
        conn.commit()

        cursor.execute("SELECT name FROM students WHERE student_id = 'TEST001'")
        self.assertEqual(cursor.fetchone()[0], "Updated Name")
        conn.close()

    def test_05_marks_crud(self):
        """Verify marks entry and relations."""
        conn = get_connection(self.test_db)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO marks (student_id, subject, internal_marks, external_marks, total_marks, percentage, grade)
            VALUES ('TEST001', 'Software Engineering', 25, 65, 90, 90.0, 'A+')
        """)
        conn.commit()

        cursor.execute("SELECT total_marks, grade FROM marks WHERE student_id = 'TEST001'")
        mark = cursor.fetchone()
        self.assertEqual(mark[0], 90.0)
        self.assertEqual(mark[1], "A+")
        conn.close()

    def test_06_attendance_crud(self):
        """Verify attendance entry."""
        conn = get_connection(self.test_db)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO attendance (student_id, subject, total_classes, classes_attended, attendance_percentage)
            VALUES ('TEST001', 'Software Engineering', 40, 36, 90.0)
        """)
        conn.commit()

        cursor.execute("SELECT attendance_percentage FROM attendance WHERE student_id = 'TEST001'")
        att = cursor.fetchone()
        self.assertEqual(att[0], 90.0)
        conn.close()

    def test_07_foreign_key_cascade_delete(self):
        """Verify that deleting a student deletes all associated marks and attendance records."""
        conn = get_connection(self.test_db)
        cursor = conn.cursor()

        # Verify child records exist
        cursor.execute("SELECT COUNT(*) FROM marks WHERE student_id = 'TEST001'")
        self.assertGreater(cursor.fetchone()[0], 0)
        cursor.execute("SELECT COUNT(*) FROM attendance WHERE student_id = 'TEST001'")
        self.assertGreater(cursor.fetchone()[0], 0)

        # Delete student
        cursor.execute("DELETE FROM students WHERE student_id = 'TEST001'")
        conn.commit()

        # Child records must now be deleted by ON DELETE CASCADE
        cursor.execute("SELECT COUNT(*) FROM marks WHERE student_id = 'TEST001'")
        self.assertEqual(cursor.fetchone()[0], 0)
        cursor.execute("SELECT COUNT(*) FROM attendance WHERE student_id = 'TEST001'")
        self.assertEqual(cursor.fetchone()[0], 0)
        conn.close()


if __name__ == "__main__":
    unittest.main()
