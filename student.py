"""
student.py - Student Management Module
==================================================
Implements full CRUD (Create, Read, Update, Delete) operations,
field validations, search filtering, and Treeview display
for college student records.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

from database import get_connection
from utils import (
    THEME, FONT_TITLE, FONT_SUBTITLE, FONT_HEADING, FONT_REGULAR, FONT_BOLD, FONT_SMALL,
    validate_required, validate_email, validate_phone, validate_date
)


class StudentManagementFrame(tk.Frame):
    def __init__(self, parent, on_data_change=None):
        super().__init__(parent, bg=THEME["bg_main"])
        self.on_data_change = on_data_change

        # Form string variables
        self.var_student_id = tk.StringVar()
        self.var_name = tk.StringVar()
        self.var_roll_no = tk.StringVar()
        self.var_course = tk.StringVar()
        self.var_branch = tk.StringVar()
        self.var_semester = tk.StringVar()
        self.var_dob = tk.StringVar()
        self.var_gender = tk.StringVar()
        self.var_phone = tk.StringVar()
        self.var_email = tk.StringVar()
        self.var_address = tk.StringVar()

        # Search variables
        self.var_search_by = tk.StringVar(value="Student ID")
        self.var_search_text = tk.StringVar()

        # Build UI
        self.create_widgets()
        self.fetch_students()

    def create_widgets(self):
        # 1. Header Bar
        header_frame = tk.Frame(self, bg=THEME["bg_card"], bd=1, relief=tk.SOLID)
        header_frame.pack(fill=tk.X, padx=15, pady=(15, 10))

        lbl_title = tk.Label(
            header_frame,
            text="👨‍🎓 Student Management System — Student Master Records",
            font=FONT_SUBTITLE,
            fg=THEME["text_dark"],
            bg=THEME["bg_card"]
        )
        lbl_title.pack(side=tk.LEFT, padx=15, pady=10)

        lbl_info = tk.Label(
            header_frame,
            text="Manage enrollment, personal, and academic contact information",
            font=FONT_REGULAR,
            fg=THEME["text_muted"],
            bg=THEME["bg_card"]
        )
        lbl_info.pack(side=tk.RIGHT, padx=15, pady=10)

        # 2. Main Content Split (Left: Input Form, Right: Treeview & Search)
        body_frame = tk.Frame(self, bg=THEME["bg_main"])
        body_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

        # -------------------------------------------------------------
        # LEFT PANEL: FORM INPUTS & BUTTONS
        # -------------------------------------------------------------
        left_card = tk.LabelFrame(
            body_frame,
            text=" Student Information Form ",
            font=FONT_HEADING,
            fg=THEME["primary"],
            bg=THEME["bg_card"],
            bd=1,
            relief=tk.SOLID
        )
        left_card.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), ipadx=10, ipady=10)

        # Scrollable container for the form if screen is small
        form_grid = tk.Frame(left_card, bg=THEME["bg_card"])
        form_grid.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        fields = [
            ("Student ID *:", self.var_student_id, "entry", "e.g. STU101"),
            ("Full Name *:", self.var_name, "entry", "e.g. Rahul Sharma"),
            ("Roll Number *:", self.var_roll_no, "entry", "e.g. 21CS045"),
            ("Course *:", self.var_course, "combo", ["B.Tech", "BCA", "MCA", "M.Tech", "B.Sc", "B.Com"]),
            ("Branch *:", self.var_branch, "combo", [
                "Computer Science", "Information Technology", "Electronics & Comm",
                "Mechanical Engg", "Civil Engg", "AI & Data Science"
            ]),
            ("Semester *:", self.var_semester, "combo", ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th"]),
            ("Date of Birth *:", self.var_dob, "entry", "YYYY-MM-DD"),
            ("Gender *:", self.var_gender, "combo", ["Male", "Female", "Other"]),
            ("Phone Number *:", self.var_phone, "entry", "10-digit number"),
            ("Email Address *:", self.var_email, "entry", "name@example.com"),
            ("Address *:", self.var_address, "entry", "City, State")
        ]

        self.entry_widgets = {}

        for row_idx, item in enumerate(fields):
            label_text, var, widget_type, meta = item

            lbl = tk.Label(
                form_grid,
                text=label_text,
                font=FONT_REGULAR,
                fg=THEME["text_dark"],
                bg=THEME["bg_card"]
            )
            lbl.grid(row=row_idx, column=0, sticky="w", pady=4, padx=(0, 8))

            if widget_type == "entry":
                ent = tk.Entry(
                    form_grid,
                    textvariable=var,
                    font=FONT_REGULAR,
                    bd=1,
                    relief=tk.SOLID,
                    width=24
                )
                ent.grid(row=row_idx, column=1, sticky="w", pady=4)
                self.entry_widgets[label_text] = ent
            elif widget_type == "combo":
                cmb = ttk.Combobox(
                    form_grid,
                    textvariable=var,
                    values=meta,
                    state="readonly",
                    font=FONT_REGULAR,
                    width=22
                )
                cmb.grid(row=row_idx, column=1, sticky="w", pady=4)
                if meta:
                    cmb.set(meta[0])
                self.entry_widgets[label_text] = cmb

        # Action Buttons Container
        btn_container = tk.Frame(left_card, bg=THEME["bg_card"])
        btn_container.pack(fill=tk.X, padx=10, pady=(15, 5))

        # Row 1 of Buttons
        btn_row1 = tk.Frame(btn_container, bg=THEME["bg_card"])
        btn_row1.pack(fill=tk.X, pady=3)

        self.btn_add = tk.Button(
            btn_row1,
            text="➕ Add Student",
            font=FONT_BOLD,
            bg=THEME["success"],
            fg=THEME["text_light"],
            activebackground=THEME["success_hover"],
            activeforeground=THEME["text_light"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.add_student
        )
        self.btn_add.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4), ipady=4)

        self.btn_update = tk.Button(
            btn_row1,
            text="✏️ Update",
            font=FONT_BOLD,
            bg=THEME["warning"],
            fg=THEME["text_light"],
            activebackground=THEME["warning_hover"],
            activeforeground=THEME["text_light"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.update_student
        )
        self.btn_update.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4, ipady=4)

        # Row 2 of Buttons
        btn_row2 = tk.Frame(btn_container, bg=THEME["bg_card"])
        btn_row2.pack(fill=tk.X, pady=3)

        self.btn_delete = tk.Button(
            btn_row2,
            text="🗑️ Delete",
            font=FONT_BOLD,
            bg=THEME["danger"],
            fg=THEME["text_light"],
            activebackground=THEME["danger_hover"],
            activeforeground=THEME["text_light"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.delete_student
        )
        self.btn_delete.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4), ipady=4)

        self.btn_clear = tk.Button(
            btn_row2,
            text="🔄 Clear Form",
            font=FONT_BOLD,
            bg=THEME["primary"],
            fg=THEME["text_light"],
            activebackground=THEME["primary_hover"],
            activeforeground=THEME["text_light"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.clear_form
        )
        self.btn_clear.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4, ipady=4)

        # -------------------------------------------------------------
        # RIGHT PANEL: SEARCH TOOLBAR & TREEVIEW TABLE
        # -------------------------------------------------------------
        right_card = tk.LabelFrame(
            body_frame,
            text=" Enrolled Students Records ",
            font=FONT_HEADING,
            fg=THEME["primary"],
            bg=THEME["bg_card"],
            bd=1,
            relief=tk.SOLID
        )
        right_card.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Search Bar Frame
        search_bar = tk.Frame(right_card, bg=THEME["bg_card"])
        search_bar.pack(fill=tk.X, padx=10, pady=8)

        lbl_search = tk.Label(
            search_bar,
            text="Search By:",
            font=FONT_BOLD,
            fg=THEME["text_dark"],
            bg=THEME["bg_card"]
        )
        lbl_search.pack(side=tk.LEFT, padx=(0, 5))

        search_options = ["Student ID", "Name", "Roll Number", "Course", "Branch"]
        cmb_search_by = ttk.Combobox(
            search_bar,
            textvariable=self.var_search_by,
            values=search_options,
            state="readonly",
            font=FONT_REGULAR,
            width=14
        )
        cmb_search_by.pack(side=tk.LEFT, padx=5)

        ent_search = tk.Entry(
            search_bar,
            textvariable=self.var_search_text,
            font=FONT_REGULAR,
            bd=1,
            relief=tk.SOLID,
            width=22
        )
        ent_search.pack(side=tk.LEFT, padx=5, ipady=2)
        ent_search.bind("<Return>", lambda e: self.search_students())

        btn_search = tk.Button(
            search_bar,
            text="🔍 Search",
            font=FONT_BOLD,
            bg=THEME["primary"],
            fg=THEME["text_light"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.search_students
        )
        btn_search.pack(side=tk.LEFT, padx=4, ipady=1)

        btn_reset = tk.Button(
            search_bar,
            text="🔄 Show All",
            font=FONT_REGULAR,
            bg=THEME["info"],
            fg=THEME["text_light"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.fetch_students
        )
        btn_reset.pack(side=tk.LEFT, padx=4, ipady=1)

        self.lbl_record_count = tk.Label(
            search_bar,
            text="Total Records: 0",
            font=FONT_BOLD,
            fg=THEME["text_muted"],
            bg=THEME["bg_card"]
        )
        self.lbl_record_count.pack(side=tk.RIGHT, padx=10)

        # Treeview Table
        table_frame = tk.Frame(right_card, bg=THEME["bg_card"])
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Vertical & Horizontal Scrollbars
        scroll_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        scroll_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)

        columns = (
            "student_id", "name", "roll_no", "course", "branch",
            "semester", "dob", "gender", "phone", "email", "address"
        )
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

        # Column Headings & Widths
        headers = {
            "student_id": ("Student ID", 80),
            "name": ("Full Name", 130),
            "roll_no": ("Roll No.", 85),
            "course": ("Course", 70),
            "branch": ("Branch", 120),
            "semester": ("Sem", 45),
            "dob": ("DOB", 85),
            "gender": ("Gender", 65),
            "phone": ("Phone", 95),
            "email": ("Email", 150),
            "address": ("Address", 140)
        }

        for col_id, (col_name, col_width) in headers.items():
            self.tree.heading(col_id, text=col_name, anchor=tk.CENTER)
            self.tree.column(col_id, width=col_width, minwidth=40, anchor=tk.CENTER if col_width < 100 else tk.W)

        # Bind row selection to form population
        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)

    # -----------------------------------------------------------------
    # CRUD OPERATIONS
    # -----------------------------------------------------------------

    def clear_form(self):
        """Resets all input fields and enables primary key editing."""
        self.var_student_id.set("")
        self.var_name.set("")
        self.var_roll_no.set("")
        self.var_course.set("B.Tech")
        self.var_branch.set("Computer Science")
        self.var_semester.set("1st")
        self.var_dob.set("")
        self.var_gender.set("Male")
        self.var_phone.set("")
        self.var_email.set("")
        self.var_address.set("")

        # Re-enable Student ID entry if it was locked during row selection
        if "Student ID *:" in self.entry_widgets:
            self.entry_widgets["Student ID *:"].config(state="normal")
            self.entry_widgets["Student ID *:"].focus_set()

    def validate_inputs(self):
        """Validates all inputs before database execution."""
        # 1. Required fields
        fields_to_check = {
            "Student ID": self.var_student_id.get(),
            "Full Name": self.var_name.get(),
            "Roll Number": self.var_roll_no.get(),
            "Course": self.var_course.get(),
            "Branch": self.var_branch.get(),
            "Semester": self.var_semester.get(),
            "Date of Birth": self.var_dob.get(),
            "Gender": self.var_gender.get(),
            "Phone Number": self.var_phone.get(),
            "Email Address": self.var_email.get(),
            "Address": self.var_address.get(),
        }
        valid, msg = validate_required(fields_to_check)
        if not valid:
            messagebox.showwarning("Validation Error", msg, parent=self)
            return False

        # 2. Date format
        valid, msg = validate_date(self.var_dob.get())
        if not valid:
            messagebox.showwarning("Validation Error", msg, parent=self)
            return False

        # 3. Phone validation
        valid, phone_result = validate_phone(self.var_phone.get())
        if not valid:
            messagebox.showwarning("Validation Error", phone_result, parent=self)
            return False
        self.var_phone.set(phone_result)

        # 4. Email validation
        valid, msg = validate_email(self.var_email.get())
        if not valid:
            messagebox.showwarning("Validation Error", msg, parent=self)
            return False

        return True

    def add_student(self):
        """Inserts a new student record into SQLite."""
        if not self.validate_inputs():
            return

        student_id = self.var_student_id.get().strip().upper()
        roll_no = self.var_roll_no.get().strip().upper()

        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Check for duplicate student_id
            cursor.execute("SELECT student_id FROM students WHERE student_id = ?", (student_id,))
            if cursor.fetchone():
                messagebox.showerror(
                    "Duplicate Entry",
                    f"A student with ID '{student_id}' already exists.",
                    parent=self
                )
                conn.close()
                return

            # Check for duplicate roll_no
            cursor.execute("SELECT roll_no FROM students WHERE roll_no = ?", (roll_no,))
            if cursor.fetchone():
                messagebox.showerror(
                    "Duplicate Entry",
                    f"A student with Roll Number '{roll_no}' already exists.",
                    parent=self
                )
                conn.close()
                return

            cursor.execute("""
                INSERT INTO students (
                    student_id, name, roll_no, course, branch, semester,
                    dob, gender, phone, email, address
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                student_id,
                self.var_name.get().strip(),
                roll_no,
                self.var_course.get().strip(),
                self.var_branch.get().strip(),
                self.var_semester.get().strip(),
                self.var_dob.get().strip(),
                self.var_gender.get().strip(),
                self.var_phone.get().strip(),
                self.var_email.get().strip(),
                self.var_address.get().strip()
            ))

            conn.commit()
            conn.close()

            messagebox.showinfo(
                "Success",
                f"Student '{student_id}' added successfully!",
                parent=self
            )
            self.fetch_students()
            self.clear_form()

            if self.on_data_change:
                self.on_data_change()

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to add student:\n{e}", parent=self)

    def update_student(self):
        """Updates an existing student record."""
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning(
                "Selection Required",
                "Please select a student from the table to update.",
                parent=self
            )
            return

        if not self.validate_inputs():
            return

        student_id = self.var_student_id.get().strip()
        roll_no = self.var_roll_no.get().strip().upper()

        confirm = messagebox.askyesno(
            "Confirm Update",
            f"Are you sure you want to update records for Student ID '{student_id}'?",
            parent=self
        )
        if not confirm:
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Ensure roll number is not taken by another student
            cursor.execute(
                "SELECT student_id FROM students WHERE roll_no = ? AND student_id != ?",
                (roll_no, student_id)
            )
            if cursor.fetchone():
                messagebox.showerror(
                    "Duplicate Roll Number",
                    f"Roll Number '{roll_no}' is already assigned to another student.",
                    parent=self
                )
                conn.close()
                return

            cursor.execute("""
                UPDATE students SET
                    name = ?, roll_no = ?, course = ?, branch = ?,
                    semester = ?, dob = ?, gender = ?, phone = ?,
                    email = ?, address = ?
                WHERE student_id = ?
            """, (
                self.var_name.get().strip(),
                roll_no,
                self.var_course.get().strip(),
                self.var_branch.get().strip(),
                self.var_semester.get().strip(),
                self.var_dob.get().strip(),
                self.var_gender.get().strip(),
                self.var_phone.get().strip(),
                self.var_email.get().strip(),
                self.var_address.get().strip(),
                student_id
            ))

            conn.commit()
            conn.close()

            messagebox.showinfo("Success", f"Student '{student_id}' updated successfully!", parent=self)
            self.fetch_students()

            if self.on_data_change:
                self.on_data_change()

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to update student:\n{e}", parent=self)

    def delete_student(self):
        """Deletes a student and cascades to marks and attendance."""
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning(
                "Selection Required",
                "Please select a student from the table to delete.",
                parent=self
            )
            return

        student_id = self.var_student_id.get().strip()
        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to permanently delete Student '{student_id}'?\n"
            f"All associated Marks and Attendance records will also be removed.",
            parent=self
        )
        if not confirm:
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", f"Student '{student_id}' deleted successfully.", parent=self)
            self.fetch_students()
            self.clear_form()

            if self.on_data_change:
                self.on_data_change()

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to delete student:\n{e}", parent=self)

    def fetch_students(self):
        """Reloads all student records from database into Treeview."""
        self.var_search_text.set("")
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT student_id, name, roll_no, course, branch,
                       semester, dob, gender, phone, email, address
                FROM students
                ORDER BY student_id ASC
            """)
            rows = cursor.fetchall()
            conn.close()

            # Clear existing rows in treeview
            for item in self.tree.get_children():
                self.tree.delete(item)

            for row in rows:
                self.tree.insert("", tk.END, values=row)

            self.lbl_record_count.config(text=f"Total Records: {len(rows)}")

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to fetch students:\n{e}", parent=self)

    def search_students(self):
        """Filters students in Treeview based on search query."""
        search_by = self.var_search_by.get()
        search_term = self.var_search_text.get().strip()

        if not search_term:
            self.fetch_students()
            return

        col_map = {
            "Student ID": "student_id",
            "Name": "name",
            "Roll Number": "roll_no",
            "Course": "course",
            "Branch": "branch"
        }
        db_col = col_map.get(search_by, "student_id")

        try:
            conn = get_connection()
            cursor = conn.cursor()

            query = f"""
                SELECT student_id, name, roll_no, course, branch,
                       semester, dob, gender, phone, email, address
                FROM students
                WHERE {db_col} LIKE ?
                ORDER BY student_id ASC
            """
            cursor.execute(query, (f"%{search_term}%",))
            rows = cursor.fetchall()
            conn.close()

            for item in self.tree.get_children():
                self.tree.delete(item)

            for row in rows:
                self.tree.insert("", tk.END, values=row)

            self.lbl_record_count.config(text=f"Matches Found: {len(rows)}")

            if not rows:
                messagebox.showinfo("Search Results", "No matching student records found.", parent=self)

        except sqlite3.Error as e:
            messagebox.showerror("Search Error", f"Failed to execute search:\n{e}", parent=self)

    def on_row_select(self, event):
        """Populates the input form when a row in the Treeview is selected."""
        selected_item = self.tree.focus()
        if not selected_item:
            return

        values = self.tree.item(selected_item, "values")
        if not values:
            return

        self.var_student_id.set(values[0])
        self.var_name.set(values[1])
        self.var_roll_no.set(values[2])
        self.var_course.set(values[3])
        self.var_branch.set(values[4])
        self.var_semester.set(values[5])
        self.var_dob.set(values[6])
        self.var_gender.set(values[7])
        self.var_phone.set(values[8])
        self.var_email.set(values[9])
        self.var_address.set(values[10])

        # Lock student_id during edit so primary key cannot be casually mutated
        if "Student ID *:" in self.entry_widgets:
            self.entry_widgets["Student ID *:"].config(state="disabled")
