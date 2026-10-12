"""
marks.py - Marks Management Module
==================================================
Handles entry, calculation, validation, and storage of academic
internal/external marks, overall percentage, and letter grades.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

from database import get_connection
from utils import (
    THEME, FONT_TITLE, FONT_SUBTITLE, FONT_HEADING, FONT_REGULAR, FONT_BOLD, FONT_SMALL,
    validate_required, validate_marks, calculate_grade
)


class MarksManagementFrame(tk.Frame):
    def __init__(self, parent, on_data_change=None):
        super().__init__(parent, bg=THEME["bg_main"])
        self.on_data_change = on_data_change

        # Selected Mark ID for updating/deleting
        self.selected_mark_id = None

        # Form Variables
        self.var_student_id = tk.StringVar()
        self.var_student_info = tk.StringVar(value="Select or enter valid Student ID")
        self.var_subject = tk.StringVar()
        self.var_internal = tk.StringVar()
        self.var_external = tk.StringVar()
        self.var_total = tk.StringVar(value="0.0")
        self.var_percentage = tk.StringVar(value="0.0 %")
        self.var_grade = tk.StringVar(value="--")

        # Search variable
        self.var_search_student = tk.StringVar()

        # Overall summary variables
        self.var_summary_subjects = tk.StringVar(value="0")
        self.var_summary_percentage = tk.StringVar(value="0.0 %")
        self.var_summary_grade = tk.StringVar(value="--")

        # Build UI
        self.create_widgets()
        self.refresh_student_ids()
        self.fetch_marks()

    def create_widgets(self):
        # 1. Header Bar
        header_frame = tk.Frame(self, bg=THEME["bg_card"], bd=1, relief=tk.SOLID)
        header_frame.pack(fill=tk.X, padx=15, pady=(15, 10))

        lbl_title = tk.Label(
            header_frame,
            text="📝 Marks Management — Academic Evaluations & Grading",
            font=FONT_SUBTITLE,
            fg=THEME["text_dark"],
            bg=THEME["bg_card"]
        )
        lbl_title.pack(side=tk.LEFT, padx=15, pady=10)

        lbl_info = tk.Label(
            header_frame,
            text="Record internal (max 30) & external (max 70) marks with auto-calculated grades",
            font=FONT_REGULAR,
            fg=THEME["text_muted"],
            bg=THEME["bg_card"]
        )
        lbl_info.pack(side=tk.RIGHT, padx=15, pady=10)

        # 2. Main Content Body
        body_frame = tk.Frame(self, bg=THEME["bg_main"])
        body_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

        # -------------------------------------------------------------
        # LEFT PANEL: FORM INPUTS & SUMMARY
        # -------------------------------------------------------------
        left_card = tk.LabelFrame(
            body_frame,
            text=" Marks Entry & Evaluation ",
            font=FONT_HEADING,
            fg=THEME["primary"],
            bg=THEME["bg_card"],
            bd=1,
            relief=tk.SOLID
        )
        left_card.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), ipadx=10, ipady=10)

        form_grid = tk.Frame(left_card, bg=THEME["bg_card"])
        form_grid.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Student ID Selector
        lbl_sid = tk.Label(form_grid, text="Student ID *:", font=FONT_REGULAR, fg=THEME["text_dark"], bg=THEME["bg_card"])
        lbl_sid.grid(row=0, column=0, sticky="w", pady=6)

        self.cmb_student_id = ttk.Combobox(
            form_grid,
            textvariable=self.var_student_id,
            font=FONT_REGULAR,
            width=22
        )
        self.cmb_student_id.grid(row=0, column=1, sticky="w", pady=6)
        self.cmb_student_id.bind("<<ComboboxSelected>>", self.on_student_change)
        self.cmb_student_id.bind("<KeyRelease>", self.on_student_change)

        # Student Name/Roll display preview
        lbl_info_badge = tk.Label(
            form_grid,
            textvariable=self.var_student_info,
            font=FONT_SMALL,
            fg=THEME["primary"],
            bg="#eff6ff",
            bd=1,
            relief=tk.SOLID,
            wraplength=200,
            justify=tk.LEFT
        )
        lbl_info_badge.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10), ipady=3)

        # Subject
        lbl_sub = tk.Label(form_grid, text="Subject *:", font=FONT_REGULAR, fg=THEME["text_dark"], bg=THEME["bg_card"])
        lbl_sub.grid(row=2, column=0, sticky="w", pady=6)

        self.cmb_subjects = ttk.Combobox(
            form_grid,
            textvariable=self.var_subject,
            values=[
                "Database Management Systems",
                "Operating Systems",
                "Computer Networks",
                "Data Structures & Algorithms",
                "Discrete Mathematics",
                "Software Engineering",
                "Web Technologies",
                "Artificial Intelligence"
            ],
            font=FONT_REGULAR,
            width=22
        )
        self.cmb_subjects.grid(row=2, column=1, sticky="w", pady=6)
        if self.cmb_subjects["values"]:
            self.cmb_subjects.set(self.cmb_subjects["values"][0])

        # Internal Marks
        lbl_int = tk.Label(form_grid, text="Internal Marks (0-30) *:", font=FONT_REGULAR, fg=THEME["text_dark"], bg=THEME["bg_card"])
        lbl_int.grid(row=3, column=0, sticky="w", pady=6)

        ent_int = tk.Entry(form_grid, textvariable=self.var_internal, font=FONT_REGULAR, bd=1, relief=tk.SOLID, width=24)
        ent_int.grid(row=3, column=1, sticky="w", pady=6)
        ent_int.bind("<KeyRelease>", lambda e: self.auto_compute())

        # External Marks
        lbl_ext = tk.Label(form_grid, text="External Marks (0-70) *:", font=FONT_REGULAR, fg=THEME["text_dark"], bg=THEME["bg_card"])
        lbl_ext.grid(row=4, column=0, sticky="w", pady=6)

        ent_ext = tk.Entry(form_grid, textvariable=self.var_external, font=FONT_REGULAR, bd=1, relief=tk.SOLID, width=24)
        ent_ext.grid(row=4, column=1, sticky="w", pady=6)
        ent_ext.bind("<KeyRelease>", lambda e: self.auto_compute())

        # Auto Calculated: Total Marks
        lbl_tot = tk.Label(form_grid, text="Total Marks (100):", font=FONT_BOLD, fg=THEME["text_dark"], bg=THEME["bg_card"])
        lbl_tot.grid(row=5, column=0, sticky="w", pady=6)

        lbl_tot_val = tk.Label(form_grid, textvariable=self.var_total, font=FONT_BOLD, fg=THEME["primary"], bg=THEME["bg_card"])
        lbl_tot_val.grid(row=5, column=1, sticky="w", pady=6)

        # Auto Calculated: Percentage
        lbl_pct = tk.Label(form_grid, text="Percentage:", font=FONT_BOLD, fg=THEME["text_dark"], bg=THEME["bg_card"])
        lbl_pct.grid(row=6, column=0, sticky="w", pady=6)

        lbl_pct_val = tk.Label(form_grid, textvariable=self.var_percentage, font=FONT_BOLD, fg=THEME["primary"], bg=THEME["bg_card"])
        lbl_pct_val.grid(row=6, column=1, sticky="w", pady=6)

        # Auto Calculated: Grade
        lbl_grd = tk.Label(form_grid, text="Grade:", font=FONT_BOLD, fg=THEME["text_dark"], bg=THEME["bg_card"])
        lbl_grd.grid(row=7, column=0, sticky="w", pady=6)

        lbl_grd_val = tk.Label(form_grid, textvariable=self.var_grade, font=("Segoe UI", 12, "bold"), fg=THEME["success"], bg=THEME["bg_card"])
        lbl_grd_val.grid(row=7, column=1, sticky="w", pady=6)

        # Action Buttons
        btn_box = tk.Frame(left_card, bg=THEME["bg_card"])
        btn_box.pack(fill=tk.X, padx=10, pady=(15, 5))

        btn_row1 = tk.Frame(btn_box, bg=THEME["bg_card"])
        btn_row1.pack(fill=tk.X, pady=3)

        btn_add = tk.Button(
            btn_row1, text="➕ Add Marks", font=FONT_BOLD, bg=THEME["success"], fg=THEME["text_light"],
            activebackground=THEME["success_hover"], activeforeground=THEME["text_light"],
            relief=tk.FLAT, cursor="hand2", command=self.add_marks
        )
        btn_add.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4), ipady=4)

        btn_upd = tk.Button(
            btn_row1, text="✏️ Update", font=FONT_BOLD, bg=THEME["warning"], fg=THEME["text_light"],
            activebackground=THEME["warning_hover"], activeforeground=THEME["text_light"],
            relief=tk.FLAT, cursor="hand2", command=self.update_marks
        )
        btn_upd.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4, ipady=4)

        btn_row2 = tk.Frame(btn_box, bg=THEME["bg_card"])
        btn_row2.pack(fill=tk.X, pady=3)

        btn_del = tk.Button(
            btn_row2, text="🗑️ Delete", font=FONT_BOLD, bg=THEME["danger"], fg=THEME["text_light"],
            activebackground=THEME["danger_hover"], activeforeground=THEME["text_light"],
            relief=tk.FLAT, cursor="hand2", command=self.delete_marks
        )
        btn_del.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4), ipady=4)

        btn_clr = tk.Button(
            btn_row2, text="🔄 Clear", font=FONT_BOLD, bg=THEME["primary"], fg=THEME["text_light"],
            activebackground=THEME["primary_hover"], activeforeground=THEME["text_light"],
            relief=tk.FLAT, cursor="hand2", command=self.clear_form
        )
        btn_clr.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4, ipady=4)

        # Student Performance Summary Badge
        summary_card = tk.LabelFrame(
            left_card,
            text=" Student Overall Performance ",
            font=FONT_SMALL,
            fg=THEME["text_dark"],
            bg="#f1f5f9",
            bd=1,
            relief=tk.SOLID
        )
        summary_card.pack(fill=tk.X, padx=10, pady=(15, 0), ipady=6)

        tk.Label(summary_card, text="Total Subjects Evaluated:", font=FONT_SMALL, bg="#f1f5f9").grid(row=0, column=0, sticky="w", padx=8, pady=2)
        tk.Label(summary_card, textvariable=self.var_summary_subjects, font=FONT_BOLD, bg="#f1f5f9").grid(row=0, column=1, sticky="w", padx=4, pady=2)

        tk.Label(summary_card, text="Cumulative Percentage:", font=FONT_SMALL, bg="#f1f5f9").grid(row=1, column=0, sticky="w", padx=8, pady=2)
        tk.Label(summary_card, textvariable=self.var_summary_percentage, font=FONT_BOLD, fg=THEME["primary"], bg="#f1f5f9").grid(row=1, column=1, sticky="w", padx=4, pady=2)

        tk.Label(summary_card, text="Overall Grade Awarded:", font=FONT_SMALL, bg="#f1f5f9").grid(row=2, column=0, sticky="w", padx=8, pady=2)
        tk.Label(summary_card, textvariable=self.var_summary_grade, font=FONT_BOLD, fg=THEME["success"], bg="#f1f5f9").grid(row=2, column=1, sticky="w", padx=4, pady=2)

        # -------------------------------------------------------------
        # RIGHT PANEL: SEARCH TOOLBAR & TREEVIEW TABLE
        # -------------------------------------------------------------
        right_card = tk.LabelFrame(
            body_frame,
            text=" Recorded Academic Marks ",
            font=FONT_HEADING,
            fg=THEME["primary"],
            bg=THEME["bg_card"],
            bd=1,
            relief=tk.SOLID
        )
        right_card.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Filter bar
        filter_bar = tk.Frame(right_card, bg=THEME["bg_card"])
        filter_bar.pack(fill=tk.X, padx=10, pady=8)

        lbl_filter = tk.Label(filter_bar, text="Filter by Student ID / Name:", font=FONT_BOLD, fg=THEME["text_dark"], bg=THEME["bg_card"])
        lbl_filter.pack(side=tk.LEFT, padx=(0, 5))

        ent_filter = tk.Entry(filter_bar, textvariable=self.var_search_student, font=FONT_REGULAR, bd=1, relief=tk.SOLID, width=22)
        ent_filter.pack(side=tk.LEFT, padx=5, ipady=2)
        ent_filter.bind("<Return>", lambda e: self.search_marks())

        btn_search = tk.Button(filter_bar, text="🔍 Search", font=FONT_BOLD, bg=THEME["primary"], fg=THEME["text_light"], relief=tk.FLAT, cursor="hand2", command=self.search_marks)
        btn_search.pack(side=tk.LEFT, padx=4, ipady=1)

        btn_show_all = tk.Button(filter_bar, text="🔄 Show All", font=FONT_REGULAR, bg=THEME["info"], fg=THEME["text_light"], relief=tk.FLAT, cursor="hand2", command=self.fetch_marks)
        btn_show_all.pack(side=tk.LEFT, padx=4, ipady=1)

        self.lbl_count = tk.Label(filter_bar, text="Records: 0", font=FONT_BOLD, fg=THEME["text_muted"], bg=THEME["bg_card"])
        self.lbl_count.pack(side=tk.RIGHT, padx=10)

        # Treeview
        table_frame = tk.Frame(right_card, bg=THEME["bg_card"])
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        scroll_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        scroll_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)

        columns = ("mark_id", "student_id", "student_name", "subject", "internal", "external", "total", "percentage", "grade")
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set
        )

        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)

        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(fill=tk.BOTH, expand=True)

        headers = {
            "mark_id": ("ID", 40),
            "student_id": ("Student ID", 80),
            "student_name": ("Student Name", 130),
            "subject": ("Subject", 180),
            "internal": ("Internal (30)", 85),
            "external": ("External (70)", 85),
            "total": ("Total (100)", 80),
            "percentage": ("Percentage", 80),
            "grade": ("Grade", 60)
        }

        for col_id, (col_name, col_width) in headers.items():
            self.tree.heading(col_id, text=col_name, anchor=tk.CENTER)
            self.tree.column(col_id, width=col_width, minwidth=40, anchor=tk.CENTER if col_width < 100 else tk.W)

        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)

    def refresh_student_ids(self):
        """Refreshes the dropdown list of active Student IDs."""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT student_id, name, roll_no FROM students ORDER BY student_id ASC")
            students = cursor.fetchall()
            conn.close()

            id_list = [s[0] for s in students]
            self.cmb_student_id["values"] = id_list
            self.students_cache = {s[0]: f"{s[1]} (Roll: {s[2]})" for s in students}
        except sqlite3.Error:
            self.students_cache = {}

    def on_student_change(self, event=None):
        """Updates the helper badge when student selection changes."""
        sid = self.var_student_id.get().strip().upper()
        if sid in self.students_cache:
            self.var_student_info.set(f"👤 {self.students_cache[sid]}")
            self.calculate_overall_summary(sid)
        else:
            # Query DB dynamically if not in cache
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT name, roll_no FROM students WHERE student_id = ?", (sid,))
                row = cursor.fetchone()
                conn.close()
                if row:
                    self.var_student_info.set(f"👤 {row[0]} (Roll: {row[1]})")
                    self.calculate_overall_summary(sid)
                else:
                    self.var_student_info.set("⚠️ Student not found in database")
                    self.reset_summary()
            except sqlite3.Error:
                self.var_student_info.set("⚠️ Unable to verify student")
                self.reset_summary()

    def auto_compute(self):
        """Computes Total, Percentage, and Grade in real-time."""
        int_str = self.var_internal.get().strip()
        ext_str = self.var_external.get().strip()

        if not int_str or not ext_str:
            self.var_total.set("0.0")
            self.var_percentage.set("0.0 %")
            self.var_grade.set("--")
            return

        valid, msg, internal, external, total = validate_marks(int_str, ext_str)
        if valid:
            percentage = round((total / 100.0) * 100, 2)
            grade = calculate_grade(total)
            self.var_total.set(f"{total:.1f}")
            self.var_percentage.set(f"{percentage:.1f} %")
            self.var_grade.set(grade)
        else:
            self.var_total.set("--")
            self.var_percentage.set("--")
            self.var_grade.set("--")

    def reset_summary(self):
        self.var_summary_subjects.set("0")
        self.var_summary_percentage.set("0.0 %")
        self.var_summary_grade.set("--")

    def calculate_overall_summary(self, student_id):
        """Calculates cumulative percentage and overall grade for a student."""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT total_marks FROM marks WHERE student_id = ?", (student_id,))
            rows = cursor.fetchall()
            conn.close()

            if not rows:
                self.reset_summary()
                return

            total_subjects = len(rows)
            sum_marks = sum(r[0] for r in rows)
            overall_pct = round(sum_marks / total_subjects, 2)
            overall_grade = calculate_grade(overall_pct)

            self.var_summary_subjects.set(str(total_subjects))
            self.var_summary_percentage.set(f"{overall_pct:.2f} %")
            self.var_summary_grade.set(overall_grade)

        except sqlite3.Error:
            self.reset_summary()

    def clear_form(self):
        self.selected_mark_id = None
        self.var_student_id.set("")
        self.var_student_info.set("Select or enter valid Student ID")
        self.var_internal.set("")
        self.var_external.set("")
        self.var_total.set("0.0")
        self.var_percentage.set("0.0 %")
        self.var_grade.set("--")
        self.reset_summary()
        self.refresh_student_ids()

    def add_marks(self):
        """Adds a new subject marks record for a student."""
        student_id = self.var_student_id.get().strip().upper()
        subject = self.var_subject.get().strip()

        if not student_id or not subject:
            messagebox.showwarning("Incomplete Form", "Student ID and Subject are mandatory.", parent=self)
            return

        valid, msg, internal, external, total = validate_marks(self.var_internal.get(), self.var_external.get())
        if not valid:
            messagebox.showwarning("Validation Error", msg, parent=self)
            return

        percentage = round((total / 100.0) * 100, 2)
        grade = calculate_grade(total)

        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Check if student exists
            cursor.execute("SELECT student_id FROM students WHERE student_id = ?", (student_id,))
            if not cursor.fetchone():
                messagebox.showerror("Error", f"Student with ID '{student_id}' does not exist.", parent=self)
                conn.close()
                return

            # Check for duplicate subject mark entry for this student
            cursor.execute(
                "SELECT mark_id FROM marks WHERE student_id = ? AND subject = ?",
                (student_id, subject)
            )
            if cursor.fetchone():
                messagebox.showwarning(
                    "Duplicate Subject",
                    f"Marks for '{subject}' have already been entered for {student_id}.\nPlease use Update instead.",
                    parent=self
                )
                conn.close()
                return

            cursor.execute("""
                INSERT INTO marks (student_id, subject, internal_marks, external_marks, total_marks, percentage, grade)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (student_id, subject, internal, external, total, percentage, grade))

            conn.commit()
            conn.close()

            messagebox.showinfo("Success", f"Marks for '{subject}' added successfully!", parent=self)
            self.fetch_marks()
            self.calculate_overall_summary(student_id)
            self.clear_form()

            if self.on_data_change:
                self.on_data_change()

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to record marks:\n{e}", parent=self)

    def update_marks(self):
        """Updates the selected marks entry."""
        if not self.selected_mark_id:
            messagebox.showwarning("Selection Required", "Please select a record from the table to update.", parent=self)
            return

        student_id = self.var_student_id.get().strip().upper()
        subject = self.var_subject.get().strip()

        valid, msg, internal, external, total = validate_marks(self.var_internal.get(), self.var_external.get())
        if not valid:
            messagebox.showwarning("Validation Error", msg, parent=self)
            return

        percentage = round((total / 100.0) * 100, 2)
        grade = calculate_grade(total)

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE marks SET
                    subject = ?, internal_marks = ?, external_marks = ?,
                    total_marks = ?, percentage = ?, grade = ?
                WHERE mark_id = ?
            """, (subject, internal, external, total, percentage, grade, self.selected_mark_id))

            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Academic marks updated successfully!", parent=self)
            self.fetch_marks()
            self.calculate_overall_summary(student_id)

            if self.on_data_change:
                self.on_data_change()

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to update marks:\n{e}", parent=self)

    def delete_marks(self):
        """Deletes the selected marks entry."""
        if not self.selected_mark_id:
            messagebox.showwarning("Selection Required", "Please select a record from the table to delete.", parent=self)
            return

        confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this mark record?", parent=self)
        if not confirm:
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM marks WHERE mark_id = ?", (self.selected_mark_id,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Marks record deleted.", parent=self)
            self.fetch_marks()
            self.clear_form()

            if self.on_data_change:
                self.on_data_change()

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to delete record:\n{e}", parent=self)

    def fetch_marks(self):
        """Fetches all marks records joined with student name."""
        self.var_search_student.set("")
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT m.mark_id, m.student_id, s.name, m.subject,
                       m.internal_marks, m.external_marks, m.total_marks,
                       m.percentage, m.grade
                FROM marks m
                LEFT JOIN students s ON m.student_id = s.student_id
                ORDER BY m.student_id ASC, m.subject ASC
            """)
            rows = cursor.fetchall()
            conn.close()

            for item in self.tree.get_children():
                self.tree.delete(item)

            for row in rows:
                self.tree.insert("", tk.END, values=row)

            self.lbl_count.config(text=f"Total Records: {len(rows)}")

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to fetch marks:\n{e}", parent=self)

    def search_marks(self):
        """Filters marks records by student ID or Name."""
        query_text = self.var_search_student.get().strip()
        if not query_text:
            self.fetch_marks()
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT m.mark_id, m.student_id, s.name, m.subject,
                       m.internal_marks, m.external_marks, m.total_marks,
                       m.percentage, m.grade
                FROM marks m
                LEFT JOIN students s ON m.student_id = s.student_id
                WHERE m.student_id LIKE ? OR s.name LIKE ?
                ORDER BY m.student_id ASC, m.subject ASC
            """, (f"%{query_text}%", f"%{query_text}%"))
            rows = cursor.fetchall()
            conn.close()

            for item in self.tree.get_children():
                self.tree.delete(item)

            for row in rows:
                self.tree.insert("", tk.END, values=row)

            self.lbl_count.config(text=f"Matches Found: {len(rows)}")

            if not rows:
                messagebox.showinfo("Search Results", "No marks records found for the search query.", parent=self)

        except sqlite3.Error as e:
            messagebox.showerror("Search Error", f"Failed to search marks:\n{e}", parent=self)

    def on_row_select(self, event):
        """Populates form when a marks record row is clicked."""
        selected_item = self.tree.focus()
        if not selected_item:
            return

        values = self.tree.item(selected_item, "values")
        if not values:
            return

        self.selected_mark_id = values[0]
        self.var_student_id.set(values[1])
        self.on_student_change()
        self.var_subject.set(values[3])
        self.var_internal.set(values[4])
        self.var_external.set(values[5])
        self.var_total.set(values[6])
        self.var_percentage.set(f"{values[7]} %")
        self.var_grade.set(values[8])
