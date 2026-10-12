"""
reports.py - Reports Generation & Export Module
==================================================
Generates institutional summaries, merit rankings, and attendance
shortage defaulter lists with 1-click export to CSV and formatted Text.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import csv
from datetime import datetime

from database import get_connection
from utils import (
    THEME, FONT_TITLE, FONT_SUBTITLE, FONT_HEADING, FONT_REGULAR, FONT_BOLD, FONT_SMALL,
    calculate_grade, get_attendance_status
)


class ReportsFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=THEME["bg_main"])

        self.current_report_type = tk.StringVar(value="Complete Student Directory")
        self.report_data = []  # Stores (headers, rows)
        self.current_headers = []
        self.current_rows = []

        self.create_widgets()
        self.generate_report()

    def create_widgets(self):
        # 1. Header Bar
        header_frame = tk.Frame(self, bg=THEME["bg_card"], bd=1, relief=tk.SOLID)
        header_frame.pack(fill=tk.X, padx=15, pady=(15, 10))

        lbl_title = tk.Label(
            header_frame,
            text="📑 Academic Reports & Analytics — Institutional Records & Export",
            font=FONT_SUBTITLE,
            fg=THEME["text_dark"],
            bg=THEME["bg_card"]
        )
        lbl_title.pack(side=tk.LEFT, padx=15, pady=10)

        lbl_info = tk.Label(
            header_frame,
            text="Generate audit reports and export to CSV or printable text",
            font=FONT_REGULAR,
            fg=THEME["text_muted"],
            bg=THEME["bg_card"]
        )
        lbl_info.pack(side=tk.RIGHT, padx=15, pady=10)

        # 2. Main Body Container
        body_frame = tk.Frame(self, bg=THEME["bg_main"])
        body_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

        # Control & Selection Card
        ctrl_card = tk.LabelFrame(
            body_frame,
            text=" Report Parameters & Export Options ",
            font=FONT_HEADING,
            fg=THEME["primary"],
            bg=THEME["bg_card"],
            bd=1,
            relief=tk.SOLID
        )
        ctrl_card.pack(fill=tk.X, pady=(0, 10), padx=5, ipady=5)

        ctrl_inner = tk.Frame(ctrl_card, bg=THEME["bg_card"])
        ctrl_inner.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(ctrl_inner, text="Select Report Type:", font=FONT_BOLD, fg=THEME["text_dark"], bg=THEME["bg_card"]).pack(side=tk.LEFT, padx=(0, 8))

        report_options = [
            "Complete Student Directory",
            "Student Academic Performance Report",
            "Top-Performing Students (Merit List)",
            "Student Attendance Summary Report",
            "Attendance Shortage Warning List (< 75%)"
        ]
        cmb_type = ttk.Combobox(
            ctrl_inner,
            textvariable=self.current_report_type,
            values=report_options,
            state="readonly",
            font=FONT_REGULAR,
            width=38
        )
        cmb_type.pack(side=tk.LEFT, padx=5)
        cmb_type.bind("<<ComboboxSelected>>", lambda e: self.generate_report())

        btn_generate = tk.Button(
            ctrl_inner, text="🔄 Generate", font=FONT_BOLD, bg=THEME["primary"], fg=THEME["text_light"],
            activebackground=THEME["primary_hover"], relief=tk.FLAT, cursor="hand2", command=self.generate_report
        )
        btn_generate.pack(side=tk.LEFT, padx=8, ipady=2)

        # Export Buttons
        btn_export_csv = tk.Button(
            ctrl_inner, text="📥 Export as CSV", font=FONT_BOLD, bg=THEME["success"], fg=THEME["text_light"],
            activebackground=THEME["success_hover"], relief=tk.FLAT, cursor="hand2", command=self.export_csv
        )
        btn_export_csv.pack(side=tk.RIGHT, padx=5, ipady=2)

        btn_export_txt = tk.Button(
            ctrl_inner, text="📄 Export as TXT", font=FONT_BOLD, bg=THEME["info"], fg=THEME["text_light"],
            activebackground=THEME["info_hover"], relief=tk.FLAT, cursor="hand2", command=self.export_txt
        )
        btn_export_txt.pack(side=tk.RIGHT, padx=5, ipady=2)

        # 3. Report Data Table Card
        table_card = tk.LabelFrame(
            body_frame,
            text=" Generated Report Preview ",
            font=FONT_HEADING,
            fg=THEME["primary"],
            bg=THEME["bg_card"],
            bd=1,
            relief=tk.SOLID
        )
        table_card.pack(fill=tk.BOTH, expand=True, padx=5)

        # Status Bar above table
        status_bar = tk.Frame(table_card, bg="#f8fafc", bd=1, relief=tk.SOLID)
        status_bar.pack(fill=tk.X, padx=10, pady=6, ipady=2)

        self.lbl_report_title = tk.Label(status_bar, text="Report:", font=FONT_BOLD, bg="#f8fafc", fg=THEME["text_dark"])
        self.lbl_report_title.pack(side=tk.LEFT, padx=10)

        self.lbl_row_count = tk.Label(status_bar, text="Records: 0", font=FONT_BOLD, bg="#f8fafc", fg=THEME["text_muted"])
        self.lbl_row_count.pack(side=tk.RIGHT, padx=10)

        # Table container
        self.table_container = tk.Frame(table_card, bg=THEME["bg_card"])
        self.table_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Dynamic Treeview
        self.tree = None
        self.scroll_y = None
        self.scroll_x = None

    def create_dynamic_tree(self, headers):
        """Re-initializes the Treeview according to dynamic column headers."""
        if self.tree:
            self.tree.destroy()
        if self.scroll_y:
            self.scroll_y.destroy()
        if self.scroll_x:
            self.scroll_x.destroy()

        self.scroll_y = ttk.Scrollbar(self.table_container, orient=tk.VERTICAL)
        self.scroll_x = ttk.Scrollbar(self.table_container, orient=tk.HORIZONTAL)

        col_ids = [f"col_{i}" for i in range(len(headers))]
        self.tree = ttk.Treeview(
            self.table_container,
            columns=col_ids,
            show="headings",
            yscrollcommand=self.scroll_y.set,
            xscrollcommand=self.scroll_x.set
        )

        self.scroll_y.config(command=self.tree.yview)
        self.scroll_x.config(command=self.tree.xview)

        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(fill=tk.BOTH, expand=True)

        for cid, head in zip(col_ids, headers):
            self.tree.heading(cid, text=head, anchor=tk.CENTER)
            self.tree.column(cid, minwidth=70, width=130, anchor=tk.CENTER)

    def generate_report(self):
        """Fetches data from database according to selected report type."""
        rtype = self.current_report_type.get()
        self.lbl_report_title.config(text=f"Report: {rtype}")

        try:
            conn = get_connection()
            cursor = conn.cursor()

            if rtype == "Complete Student Directory":
                headers = ["Student ID", "Name", "Roll No", "Course", "Branch", "Semester", "DOB", "Gender", "Phone", "Email"]
                cursor.execute("""
                    SELECT student_id, name, roll_no, course, branch, semester, dob, gender, phone, email
                    FROM students ORDER BY student_id ASC
                """)
                rows = cursor.fetchall()

            elif rtype == "Student Academic Performance Report":
                headers = ["Student ID", "Student Name", "Roll No", "Course", "Branch", "Subjects", "Avg Percentage", "Overall Grade"]
                cursor.execute("""
                    SELECT s.student_id, s.name, s.roll_no, s.course, s.branch,
                           COUNT(m.mark_id) as subjects_count,
                           AVG(m.total_marks) as avg_pct
                    FROM students s
                    LEFT JOIN marks m ON s.student_id = m.student_id
                    GROUP BY s.student_id
                    ORDER BY s.student_id ASC
                """)
                raw = cursor.fetchall()
                rows = []
                for r in raw:
                    sub_count = r[5] or 0
                    pct = round(r[6], 2) if r[6] is not None else 0.0
                    grade = calculate_grade(pct) if sub_count > 0 else "N/A"
                    rows.append((r[0], r[1], r[2], r[3], r[4], str(sub_count), f"{pct:.2f}%", grade))

            elif rtype == "Top-Performing Students (Merit List)":
                headers = ["Rank", "Student ID", "Student Name", "Roll No", "Course", "Branch", "Avg Percentage", "Grade"]
                cursor.execute("""
                    SELECT s.student_id, s.name, s.roll_no, s.course, s.branch,
                           AVG(m.total_marks) as avg_pct
                    FROM students s
                    INNER JOIN marks m ON s.student_id = m.student_id
                    GROUP BY s.student_id
                    HAVING COUNT(m.mark_id) > 0
                    ORDER BY avg_pct DESC
                """)
                raw = cursor.fetchall()
                rows = []
                for rank, r in enumerate(raw, 1):
                    pct = round(r[5], 2)
                    grade = calculate_grade(pct)
                    rows.append((f"#{rank}", r[0], r[1], r[2], r[3], r[4], f"{pct:.2f}%", grade))

            elif rtype == "Student Attendance Summary Report":
                headers = ["Student ID", "Student Name", "Roll No", "Course", "Total Classes", "Classes Attended", "Attendance %", "Status"]
                cursor.execute("""
                    SELECT s.student_id, s.name, s.roll_no, s.course,
                           SUM(a.total_classes) as tot_classes,
                           SUM(a.classes_attended) as tot_attended
                    FROM students s
                    LEFT JOIN attendance a ON s.student_id = a.student_id
                    GROUP BY s.student_id
                    ORDER BY s.student_id ASC
                """)
                raw = cursor.fetchall()
                rows = []
                for r in raw:
                    held = r[4] or 0
                    att = r[5] or 0
                    pct = round((att / held) * 100, 2) if held > 0 else 0.0
                    status = get_attendance_status(pct) if held > 0 else "N/A"
                    rows.append((r[0], r[1], r[2], r[3], str(held), str(att), f"{pct:.2f}%", status))

            elif rtype == "Attendance Shortage Warning List (< 75%)":
                headers = ["Student ID", "Student Name", "Roll No", "Course", "Total Classes", "Attended", "Attendance %", "Shortage Status"]
                cursor.execute("""
                    SELECT s.student_id, s.name, s.roll_no, s.course,
                           SUM(a.total_classes) as tot_classes,
                           SUM(a.classes_attended) as tot_attended
                    FROM students s
                    INNER JOIN attendance a ON s.student_id = a.student_id
                    GROUP BY s.student_id
                    HAVING SUM(a.total_classes) > 0 AND ((SUM(a.classes_attended) * 100.0) / SUM(a.total_classes)) < 75.0
                    ORDER BY ((SUM(a.classes_attended) * 100.0) / SUM(a.total_classes)) ASC
                """)
                raw = cursor.fetchall()
                rows = []
                for r in raw:
                    held = r[4]
                    att = r[5]
                    pct = round((att / held) * 100, 2)
                    status = "DEBARRED RISK (<60%)" if pct < 60.0 else "WARNING (<75%)"
                    rows.append((r[0], r[1], r[2], r[3], str(held), str(att), f"{pct:.2f}%", status))

            conn.close()

            self.current_headers = headers
            self.current_rows = rows
            self.create_dynamic_tree(headers)

            for row in rows:
                self.tree.insert("", tk.END, values=row)

            self.lbl_row_count.config(text=f"Total Records: {len(rows)}")

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to generate report:\n{e}", parent=self)

    def export_csv(self):
        """Exports currently displayed report rows to a CSV file."""
        if not self.current_rows:
            messagebox.showwarning("Export Warning", "No data to export.", parent=self)
            return

        default_filename = f"{self.current_report_type.get().replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile=default_filename,
            filetypes=[("CSV files", "*.csv"), ("All Files", "*.*")],
            title="Export Report to CSV",
            parent=self
        )

        if not file_path:
            return

        try:
            with open(file_path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                # Write Title Metadata
                writer.writerow(["Student Management System - Institutional Report"])
                writer.writerow([f"Report: {self.current_report_type.get()}"])
                writer.writerow([f"Generated On: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])
                writer.writerow([])
                # Write Headers
                writer.writerow(self.current_headers)
                # Write Rows
                writer.writerows(self.current_rows)

            messagebox.showinfo("Export Successful", f"Report successfully exported to:\n{file_path}", parent=self)

        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to save CSV file:\n{e}", parent=self)

    def export_txt(self):
        """Exports report into a beautifully aligned, human-readable text document."""
        if not self.current_rows:
            messagebox.showwarning("Export Warning", "No data to export.", parent=self)
            return

        default_filename = f"{self.current_report_type.get().replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile=default_filename,
            filetypes=[("Text files", "*.txt"), ("All Files", "*.*")],
            title="Export Report to Text Document",
            parent=self
        )

        if not file_path:
            return

        try:
            with open(file_path, mode="w", encoding="utf-8") as f:
                # Header
                f.write("=" * 90 + "\n")
                f.write("               STUDENT MANAGEMENT SYSTEM - OFFICIAL REPORT\n")
                f.write(f" Report Type:   {self.current_report_type.get()}\n")
                f.write(f" Generated:     {datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')}\n")
                f.write(f" Total Records: {len(self.current_rows)}\n")
                f.write("=" * 90 + "\n\n")

                # Compute column widths
                col_widths = [len(h) for h in self.current_headers]
                for row in self.current_rows:
                    for idx, val in enumerate(row):
                        col_widths[idx] = max(col_widths[idx], len(str(val)))

                # Pad widths slightly
                col_widths = [w + 3 for w in col_widths]

                # Format Header Line
                header_line = "".join(h.ljust(w) for h, w in zip(self.current_headers, col_widths))
                f.write(header_line + "\n")
                f.write("-" * len(header_line) + "\n")

                # Format Rows
                for row in self.current_rows:
                    row_line = "".join(str(val).ljust(w) for val, w in zip(row, col_widths))
                    f.write(row_line + "\n")

                f.write("-" * len(header_line) + "\n")
                f.write("\n*** End of Official College Record ***\n")

            messagebox.showinfo("Export Successful", f"Report formatted and saved to:\n{file_path}", parent=self)

        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to save text file:\n{e}", parent=self)
