"""
profile_view.py - Comprehensive 360-Degree Student Profile Viewer
==================================================================
Presents a unified, beautiful academic dossier for a selected student:
Personal details, complete academic marks card, cumulative GPA/grade,
and subject-wise attendance compliance.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

from database import get_connection
from utils import (
    THEME, FONT_TITLE, FONT_SUBTITLE, FONT_HEADING, FONT_REGULAR, FONT_BOLD, FONT_SMALL,
    calculate_grade, get_attendance_status
)


class StudentProfileFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=THEME["bg_main"])

        self.var_search_id = tk.StringVar()

        # Build UI
        self.create_widgets()
        self.refresh_student_list()

    def create_widgets(self):
        # 1. Header Bar
        header_frame = tk.Frame(self, bg=THEME["bg_card"], bd=1, relief=tk.SOLID)
        header_frame.pack(fill=tk.X, padx=15, pady=(15, 10))

        lbl_title = tk.Label(
            header_frame,
            text="👤 Student Profile — Complete 360° Academic Dossier",
            font=FONT_SUBTITLE,
            fg=THEME["text_dark"],
            bg=THEME["bg_card"]
        )
        lbl_title.pack(side=tk.LEFT, padx=15, pady=10)

        # Student Selector in Header
        sel_box = tk.Frame(header_frame, bg=THEME["bg_card"])
        sel_box.pack(side=tk.RIGHT, padx=15, pady=10)

        tk.Label(sel_box, text="Select Student:", font=FONT_BOLD, fg=THEME["text_dark"], bg=THEME["bg_card"]).pack(side=tk.LEFT, padx=(0, 5))

        self.cmb_students = ttk.Combobox(sel_box, textvariable=self.var_search_id, font=FONT_REGULAR, width=22)
        self.cmb_students.pack(side=tk.LEFT, padx=5)
        self.cmb_students.bind("<<ComboboxSelected>>", lambda e: self.load_profile())

        btn_load = tk.Button(
            sel_box, text="Load Profile", font=FONT_BOLD, bg=THEME["primary"], fg=THEME["text_light"],
            activebackground=THEME["primary_hover"], relief=tk.FLAT, cursor="hand2", command=self.load_profile
        )
        btn_load.pack(side=tk.LEFT, padx=5, ipady=2)

        # 2. Main Content Split View
        body_frame = tk.Frame(self, bg=THEME["bg_main"])
        body_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

        # -------------------------------------------------------------
        # LEFT COLUMN: PERSONAL INFORMATION DOSSIER CARD
        # -------------------------------------------------------------
        self.card_personal = tk.LabelFrame(
            body_frame,
            text=" Personal & Contact Details ",
            font=FONT_HEADING,
            fg=THEME["primary"],
            bg=THEME["bg_card"],
            bd=1,
            relief=tk.SOLID,
            width=340
        )
        self.card_personal.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), ipadx=10, ipady=10)
        self.card_personal.pack_propagate(False)

        # Avatar Header
        avatar_frame = tk.Frame(self.card_personal, bg="#f1f5f9", bd=1, relief=tk.SOLID)
        avatar_frame.pack(fill=tk.X, padx=10, pady=(5, 15), ipady=10)

        lbl_icon = tk.Label(avatar_frame, text="🎓", font=("Segoe UI", 32), bg="#f1f5f9")
        lbl_icon.pack()

        self.lbl_profile_name = tk.Label(avatar_frame, text="Select a Student", font=FONT_SUBTITLE, fg=THEME["text_dark"], bg="#f1f5f9")
        self.lbl_profile_name.pack()

        self.lbl_profile_roll = tk.Label(avatar_frame, text="Roll Number: --", font=FONT_SMALL, fg=THEME["text_muted"], bg="#f1f5f9")
        self.lbl_profile_roll.pack()

        # Details Grid
        details_grid = tk.Frame(self.card_personal, bg=THEME["bg_card"])
        details_grid.pack(fill=tk.BOTH, expand=True, padx=10)

        self.bio_labels = {}
        fields = [
            ("Student ID:", "id"),
            ("Course:", "course"),
            ("Branch:", "branch"),
            ("Semester:", "semester"),
            ("Date of Birth:", "dob"),
            ("Gender:", "gender"),
            ("Phone:", "phone"),
            ("Email:", "email"),
            ("Address:", "address")
        ]

        for idx, (label_text, key) in enumerate(fields):
            lbl_key = tk.Label(details_grid, text=label_text, font=FONT_BOLD, fg=THEME["text_dark"], bg=THEME["bg_card"])
            lbl_key.grid(row=idx, column=0, sticky="nw", pady=4, padx=(0, 5))

            lbl_val = tk.Label(details_grid, text="--", font=FONT_REGULAR, fg=THEME["text_muted"], bg=THEME["bg_card"], wraplength=190, justify=tk.LEFT)
            lbl_val.grid(row=idx, column=1, sticky="w", pady=4)
            self.bio_labels[key] = lbl_val

        # -------------------------------------------------------------
        # RIGHT COLUMN: ACADEMICS & ATTENDANCE PERFORMANCE CARDS
        # -------------------------------------------------------------
        right_frame = tk.Frame(body_frame, bg=THEME["bg_main"])
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # 1. Academic Performance Card (Top Right)
        card_academic = tk.LabelFrame(
            right_frame,
            text=" Academic Performance & Marks ",
            font=FONT_HEADING,
            fg=THEME["primary"],
            bg=THEME["bg_card"],
            bd=1,
            relief=tk.SOLID
        )
        card_academic.pack(fill=tk.BOTH, expand=True, pady=(0, 8), padx=5)

        # Summary Bar for Academics
        acad_summary = tk.Frame(card_academic, bg="#eff6ff", bd=1, relief=tk.SOLID)
        acad_summary.pack(fill=tk.X, padx=10, pady=8, ipady=4)

        tk.Label(acad_summary, text="Overall Academic Percentage:", font=FONT_BOLD, bg="#eff6ff", fg=THEME["text_dark"]).pack(side=tk.LEFT, padx=10)
        self.lbl_acad_pct = tk.Label(acad_summary, text="--", font=("Segoe UI", 12, "bold"), bg="#eff6ff", fg=THEME["primary"])
        self.lbl_acad_pct.pack(side=tk.LEFT, padx=5)

        tk.Label(acad_summary, text="|   Overall Grade Awarded:", font=FONT_BOLD, bg="#eff6ff", fg=THEME["text_dark"]).pack(side=tk.LEFT, padx=(20, 5))
        self.lbl_acad_grade = tk.Label(acad_summary, text="--", font=("Segoe UI", 12, "bold"), bg="#eff6ff", fg=THEME["success"])
        self.lbl_acad_grade.pack(side=tk.LEFT, padx=5)

        # Marks Table
        tree_acad_frame = tk.Frame(card_academic, bg=THEME["bg_card"])
        tree_acad_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        scroll_acad = ttk.Scrollbar(tree_acad_frame, orient=tk.VERTICAL)
        self.tree_marks = ttk.Treeview(
            tree_acad_frame,
            columns=("subject", "internal", "external", "total", "percentage", "grade"),
            show="headings",
            height=4,
            yscrollcommand=scroll_acad.set
        )
        scroll_acad.config(command=self.tree_marks.yview)
        scroll_acad.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_marks.pack(fill=tk.BOTH, expand=True)

        marks_cols = {
            "subject": ("Subject", 220),
            "internal": ("Internal (30)", 90),
            "external": ("External (70)", 90),
            "total": ("Total (100)", 90),
            "percentage": ("Percentage", 90),
            "grade": ("Grade", 70)
        }
        for cid, (cname, cwidth) in marks_cols.items():
            self.tree_marks.heading(cid, text=cname, anchor=tk.CENTER)
            self.tree_marks.column(cid, width=cwidth, anchor=tk.CENTER if cid != "subject" else tk.W)

        # 2. Attendance Compliance Card (Bottom Right)
        card_att = tk.LabelFrame(
            right_frame,
            text=" Attendance Records & Compliance ",
            font=FONT_HEADING,
            fg=THEME["primary"],
            bg=THEME["bg_card"],
            bd=1,
            relief=tk.SOLID
        )
        card_att.pack(fill=tk.BOTH, expand=True, pady=(8, 0), padx=5)

        # Summary Bar for Attendance
        att_summary = tk.Frame(card_att, bg="#f0fdf4", bd=1, relief=tk.SOLID)
        att_summary.pack(fill=tk.X, padx=10, pady=8, ipady=4)

        tk.Label(att_summary, text="Cumulative Attendance:", font=FONT_BOLD, bg="#f0fdf4", fg=THEME["text_dark"]).pack(side=tk.LEFT, padx=10)
        self.lbl_att_pct = tk.Label(att_summary, text="--", font=("Segoe UI", 12, "bold"), bg="#f0fdf4", fg=THEME["primary"])
        self.lbl_att_pct.pack(side=tk.LEFT, padx=5)

        tk.Label(att_summary, text="|   Eligibility Status:", font=FONT_BOLD, bg="#f0fdf4", fg=THEME["text_dark"]).pack(side=tk.LEFT, padx=(20, 5))
        self.lbl_att_status = tk.Label(att_summary, text="--", font=("Segoe UI", 12, "bold"), bg="#f0fdf4", fg=THEME["success"])
        self.lbl_att_status.pack(side=tk.LEFT, padx=5)

        # Attendance Table
        tree_att_frame = tk.Frame(card_att, bg=THEME["bg_card"])
        tree_att_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        scroll_att = ttk.Scrollbar(tree_att_frame, orient=tk.VERTICAL)
        self.tree_att = ttk.Treeview(
            tree_att_frame,
            columns=("subject", "total_classes", "attended", "percentage", "status"),
            show="headings",
            height=4,
            yscrollcommand=scroll_att.set
        )
        scroll_att.config(command=self.tree_att.yview)
        scroll_att.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_att.pack(fill=tk.BOTH, expand=True)

        att_cols = {
            "subject": ("Subject", 220),
            "total_classes": ("Total Classes", 110),
            "attended": ("Classes Attended", 110),
            "percentage": ("Percentage", 100),
            "status": ("Eligibility Status", 110)
        }
        for cid, (cname, cwidth) in att_cols.items():
            self.tree_att.heading(cid, text=cname, anchor=tk.CENTER)
            self.tree_att.column(cid, width=cwidth, anchor=tk.CENTER if cid != "subject" else tk.W)

    def refresh_student_list(self):
        """Loads all student IDs into the top selector."""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT student_id, name, roll_no FROM students ORDER BY student_id ASC")
            students = cursor.fetchall()
            conn.close()

            student_options = [f"{s[0]} - {s[1]} ({s[2]})" for s in students]
            self.cmb_students["values"] = student_options
            if student_options:
                self.cmb_students.set(student_options[0])
                self.load_profile()
        except sqlite3.Error:
            pass

    def load_profile(self):
        """Fetches and displays complete student dossier."""
        selected_text = self.var_search_id.get().strip()
        if not selected_text:
            return

        # Extract student_id from "STU101 - Name (Roll)"
        student_id = selected_text.split()[0].upper()

        try:
            conn = get_connection()
            cursor = conn.cursor()

            # 1. Fetch Student Details
            cursor.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
            student = cursor.fetchone()

            if not student:
                messagebox.showerror("Not Found", f"Student '{student_id}' not found.", parent=self)
                conn.close()
                return

            self.lbl_profile_name.config(text=student[1])
            self.lbl_profile_roll.config(text=f"Roll No: {student[2]}")

            self.bio_labels["id"].config(text=student[0])
            self.bio_labels["course"].config(text=student[3])
            self.bio_labels["branch"].config(text=student[4])
            self.bio_labels["semester"].config(text=student[5])
            self.bio_labels["dob"].config(text=student[6])
            self.bio_labels["gender"].config(text=student[7])
            self.bio_labels["phone"].config(text=student[8])
            self.bio_labels["email"].config(text=student[9])
            self.bio_labels["address"].config(text=student[10])

            # 2. Fetch Marks Records
            cursor.execute("""
                SELECT subject, internal_marks, external_marks, total_marks, percentage, grade
                FROM marks WHERE student_id = ?
                ORDER BY subject ASC
            """, (student_id,))
            marks = cursor.fetchall()

            for item in self.tree_marks.get_children():
                self.tree_marks.delete(item)

            total_pct_sum = 0.0
            for m in marks:
                self.tree_marks.insert("", tk.END, values=(m[0], m[1], m[2], m[3], f"{m[4]:.1f}%", m[5]))
                total_pct_sum += m[4]

            if marks:
                overall_acad_pct = round(total_pct_sum / len(marks), 2)
                overall_grade = calculate_grade(overall_acad_pct)
                self.lbl_acad_pct.config(text=f"{overall_acad_pct:.2f} %")
                self.lbl_acad_grade.config(text=overall_grade)
            else:
                self.lbl_acad_pct.config(text="No marks recorded")
                self.lbl_acad_grade.config(text="--")

            # 3. Fetch Attendance Records
            cursor.execute("""
                SELECT subject, total_classes, classes_attended, attendance_percentage
                FROM attendance WHERE student_id = ?
                ORDER BY subject ASC
            """, (student_id,))
            attendance = cursor.fetchall()

            for item in self.tree_att.get_children():
                self.tree_att.delete(item)

            tot_held = 0
            tot_attended = 0
            for a in attendance:
                status = get_attendance_status(a[3])
                self.tree_att.insert("", tk.END, values=(a[0], a[1], a[2], f"{a[3]:.1f}%", status))
                tot_held += a[1]
                tot_attended += a[2]

            if attendance and tot_held > 0:
                overall_att_pct = round((tot_attended / tot_held) * 100, 2)
                att_status = get_attendance_status(overall_att_pct)
                self.lbl_att_pct.config(text=f"{overall_att_pct:.2f} % ({tot_attended}/{tot_held})")
                self.lbl_att_status.config(text=att_status)
                if att_status == "Good":
                    self.lbl_att_status.config(fg=THEME["success"])
                elif att_status == "Average":
                    self.lbl_att_status.config(fg=THEME["warning"])
                else:
                    self.lbl_att_status.config(fg=THEME["danger"])
            else:
                self.lbl_att_pct.config(text="No attendance logged")
                self.lbl_att_status.config(text="--")

            conn.close()

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to load profile:\n{e}", parent=self)
