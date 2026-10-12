"""
dashboard.py - Main Application Dashboard
==================================================
Houses the administrative shell, responsive sidebar navigation,
real-time metric KPI cards, dynamic view routing across all modules,
and an interactive 3D cyber-wave visual background effect.
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from PIL import Image, ImageTk

from database import get_connection
from utils import (
    THEME, FONT_TITLE, FONT_SUBTITLE, FONT_HEADING, FONT_REGULAR, FONT_BOLD, FONT_SMALL,
    ModernToggleSwitch
)
from student import StudentManagementFrame
from marks import MarksManagementFrame
from attendance import AttendanceManagementFrame
from profile_view import StudentProfileFrame
from reports import ReportsFrame

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
DASHBOARD_BG_PATH = os.path.join(ASSETS_DIR, "dashboard_bg.png")


class DashboardWindow:
    def __init__(self, root, current_user="admin", login_root=None):
        self.root = root
        self.current_user = current_user
        self.login_root = login_root

        self.root.title("Student Management System — University Administration Portal")
        self.root.geometry("1280x760")
        self.root.minsize(1080, 680)
        self.root.configure(bg=THEME["bg_main"])

        # Visual Background Effect Toggle State (Default ON)
        self.bg_effect_var = tk.BooleanVar(value=True)

        # Metric KPI Variables
        self.var_metric_students = tk.StringVar(value="0")
        self.var_metric_courses = tk.StringVar(value="0")
        self.var_metric_subjects = tk.StringVar(value="0")
        self.var_metric_avg_pct = tk.StringVar(value="0.0 %")

        # Live Clock Variable
        self.var_time = tk.StringVar()

        # Image cache references to prevent garbage collection
        self.bg_photo = None
        self.banner_photo = None

        # Build Master UI
        self.create_app_bar()
        self.create_layout()
        self.start_clock()

        # Default view: Overview
        self.show_overview()

    def create_app_bar(self):
        """Builds the persistent top application header with visual effect toggle."""
        top_bar = tk.Frame(self.root, bg=THEME["header_bg"], height=65)
        top_bar.pack(side=tk.TOP, fill=tk.X)
        top_bar.pack_propagate(False)

        # Title & Subtitle Left
        title_box = tk.Frame(top_bar, bg=THEME["header_bg"])
        title_box.pack(side=tk.LEFT, padx=20, pady=10)

        lbl_logo = tk.Label(
            title_box,
            text="🎓 STUDENT MANAGEMENT SYSTEM",
            font=("Segoe UI", 15, "bold"),
            fg=THEME["text_light"],
            bg=THEME["header_bg"]
        )
        lbl_logo.pack(anchor="w")

        lbl_inst = tk.Label(
            title_box,
            text="College of Engineering & Technology | Academic Management System",
            font=FONT_SMALL,
            fg=THEME["text_muted"],
            bg=THEME["header_bg"]
        )
        lbl_inst.pack(anchor="w")

        # Right Side: Clock, Visual Toggle, User Info & Logout
        right_box = tk.Frame(top_bar, bg=THEME["header_bg"])
        right_box.pack(side=tk.RIGHT, padx=20, pady=10)

        # Live Clock
        lbl_clock = tk.Label(
            right_box,
            textvariable=self.var_time,
            font=FONT_SMALL,
            fg=THEME["text_light"],
            bg=THEME["header_bg"]
        )
        lbl_clock.pack(side=tk.LEFT, padx=(0, 15))

        # -------------------------------------------------------------
        # BACKGROUND EFFECT TOGGLE SWITCH
        # -------------------------------------------------------------
        toggle_frame = tk.Frame(right_box, bg=THEME["header_bg"])
        toggle_frame.pack(side=tk.LEFT, padx=(0, 15))

        lbl_toggle = tk.Label(
            toggle_frame,
            text="✨ Wave FX:",
            font=FONT_SMALL,
            fg="#cbd5e1",
            bg=THEME["header_bg"]
        )
        lbl_toggle.pack(side=tk.LEFT, padx=(0, 5))

        self.bg_toggle = ModernToggleSwitch(
            toggle_frame,
            variable=self.bg_effect_var,
            command=self.toggle_bg_effect,
            width=40,
            height=20,
            bg_color=THEME["header_bg"],
            on_color="#8b5cf6",  # Purple accent matching wave image
            off_color="#475569"
        )
        self.bg_toggle.pack(side=tk.LEFT)

        # User Badge
        lbl_user = tk.Label(
            right_box,
            text=f"👤 Admin: {self.current_user}",
            font=FONT_BOLD,
            fg=THEME["text_light"],
            bg="#334155",
            padx=10,
            pady=4
        )
        lbl_user.pack(side=tk.LEFT, padx=(0, 12))

        btn_logout = tk.Button(
            right_box,
            text="🚪 Logout",
            font=FONT_BOLD,
            bg=THEME["danger"],
            fg=THEME["text_light"],
            activebackground=THEME["danger_hover"],
            activeforeground=THEME["text_light"],
            relief=tk.RAISED,
            bd=1,
            cursor="hand2",
            padx=10,
            pady=3,
            command=self.confirm_logout
        )
        btn_logout.pack(side=tk.LEFT)

    def toggle_bg_effect(self):
        """Toggles the visual background wallpaper effect and refreshes view."""
        # If currently on overview, re-render overview with or without background
        if hasattr(self, "current_view") and self.current_view == "Overview":
            self.show_overview()

    def start_clock(self):
        """Updates live system clock every second."""
        now = datetime.now().strftime("%A, %d %B %Y  |  %I:%M:%S %p")
        self.var_time.set(now)
        self.root.after(1000, self.start_clock)

    def create_layout(self):
        """Creates the two-column master layout (Sidebar + Dynamic Container)."""
        main_container = tk.Frame(self.root, bg=THEME["bg_main"])
        main_container.pack(fill=tk.BOTH, expand=True)

        # -------------------------------------------------------------
        # 1. LEFT SIDEBAR NAVIGATION
        # -------------------------------------------------------------
        self.sidebar = tk.Frame(main_container, bg=THEME["sidebar_bg"], width=230)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        # Navigation Header
        lbl_nav = tk.Label(
            self.sidebar,
            text="MAIN NAVIGATION",
            font=FONT_SMALL,
            fg="#94a3b8",
            bg=THEME["sidebar_bg"],
            anchor="w",
            padx=20,
            pady=15
        )
        lbl_nav.pack(fill=tk.X)

        self.nav_buttons = {}
        nav_items = [
            ("📊  Overview", self.show_overview),
            ("👨‍🎓  Students", self.show_students),
            ("📝  Marks", self.show_marks),
            ("📅  Attendance", self.show_attendance),
            ("🔍  Student Profile", self.show_profile),
            ("📑  Reports & Export", self.show_reports),
        ]

        for text, command in nav_items:
            btn = tk.Button(
                self.sidebar,
                text=text,
                font=("Segoe UI", 10, "bold"),
                fg=THEME["text_light"],
                bg=THEME["sidebar_bg"],
                activebackground=THEME["sidebar_active"],
                activeforeground=THEME["text_light"],
                anchor="w",
                padx=20,
                pady=10,
                bd=0,
                relief=tk.FLAT,
                cursor="hand2",
                command=command
            )
            btn.pack(fill=tk.X, pady=1)
            self.nav_buttons[text] = btn

        # Spacer
        spacer = tk.Frame(self.sidebar, bg=THEME["sidebar_bg"])
        spacer.pack(fill=tk.BOTH, expand=True)

        # Bottom System Buttons
        btn_sys_logout = tk.Button(
            self.sidebar,
            text="🚪  Log Out",
            font=FONT_BOLD,
            fg="#f87171",
            bg=THEME["sidebar_bg"],
            activebackground=THEME["sidebar_active"],
            activeforeground="#f87171",
            anchor="w",
            padx=20,
            pady=8,
            bd=0,
            relief=tk.FLAT,
            cursor="hand2",
            command=self.confirm_logout
        )
        btn_sys_logout.pack(fill=tk.X, pady=1)

        btn_sys_exit = tk.Button(
            self.sidebar,
            text="❌  Exit Application",
            font=FONT_BOLD,
            fg="#ef4444",
            bg=THEME["sidebar_bg"],
            activebackground=THEME["sidebar_active"],
            activeforeground="#ef4444",
            anchor="w",
            padx=20,
            pady=8,
            bd=0,
            relief=tk.FLAT,
            cursor="hand2",
            command=self.confirm_exit
        )
        btn_sys_exit.pack(fill=tk.X, pady=(1, 15))

        # -------------------------------------------------------------
        # 2. DYNAMIC CONTENT CONTAINER
        # -------------------------------------------------------------
        self.content_area = tk.Frame(main_container, bg=THEME["bg_main"])
        self.content_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def highlight_nav(self, active_title):
        """Highlights the active sidebar button."""
        for title, btn in self.nav_buttons.items():
            if active_title in title:
                btn.config(bg=THEME["primary"], fg=THEME["text_light"])
            else:
                btn.config(bg=THEME["sidebar_bg"], fg=THEME["text_light"])

    def clear_content_area(self):
        """Removes existing frame from content container."""
        for widget in self.content_area.winfo_children():
            widget.destroy()

    # -----------------------------------------------------------------
    # NAVIGATION ROUTERS
    # -----------------------------------------------------------------

    def show_overview(self):
        """Displays KPI Cards, Cyber-Wave Hero Background, and Recent Students."""
        self.current_view = "Overview"
        self.highlight_nav("Overview")
        self.clear_content_area()
        self.build_overview_view()
        self.refresh_metrics()

    def show_students(self):
        """Routes to Student Management Frame."""
        self.current_view = "Students"
        self.highlight_nav("Students")
        self.clear_content_area()
        frame = StudentManagementFrame(self.content_area, on_data_change=self.refresh_metrics)
        frame.pack(fill=tk.BOTH, expand=True)

    def show_marks(self):
        """Routes to Marks Management Frame."""
        self.current_view = "Marks"
        self.highlight_nav("Marks")
        self.clear_content_area()
        frame = MarksManagementFrame(self.content_area, on_data_change=self.refresh_metrics)
        frame.pack(fill=tk.BOTH, expand=True)

    def show_attendance(self):
        """Routes to Attendance Tracking Frame."""
        self.current_view = "Attendance"
        self.highlight_nav("Attendance")
        self.clear_content_area()
        frame = AttendanceManagementFrame(self.content_area, on_data_change=self.refresh_metrics)
        frame.pack(fill=tk.BOTH, expand=True)

    def show_profile(self):
        """Routes to 360-degree Student Profile Frame."""
        self.current_view = "Profile"
        self.highlight_nav("Profile")
        self.clear_content_area()
        frame = StudentProfileFrame(self.content_area)
        frame.pack(fill=tk.BOTH, expand=True)

    def show_reports(self):
        """Routes to Reports & Analytics Exporter Frame."""
        self.current_view = "Reports"
        self.highlight_nav("Reports")
        self.clear_content_area()
        frame = ReportsFrame(self.content_area)
        frame.pack(fill=tk.BOTH, expand=True)

    # -----------------------------------------------------------------
    # DASHBOARD OVERVIEW VIEW (WITH 3D CYBER WAVE BACKGROUND EFFECT)
    # -----------------------------------------------------------------

    def build_overview_view(self):
        overview_container = tk.Frame(self.content_area, bg=THEME["bg_main"])
        overview_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # =============================================================
        # 1. 3D HERO BANNER WITH BACKGROUND WAVE EFFECT
        # =============================================================
        use_bg = self.bg_effect_var.get() and os.path.exists(DASHBOARD_BG_PATH)

        if use_bg:
            # 3D Cyber Wave Banner using Canvas
            banner_canvas = tk.Canvas(
                overview_container,
                height=130,
                bg="#080c1b",
                highlightthickness=0,
                bd=1,
                relief=tk.SOLID
            )
            banner_canvas.pack(fill=tk.X, pady=(0, 15), padx=5)

            # Load and stretch the background wave image
            try:
                raw_img = Image.open(DASHBOARD_BG_PATH)
                # Resized to standard banner dimensions
                resized_img = raw_img.resize((1020, 130), Image.Resampling.LANCZOS)
                self.banner_photo = ImageTk.PhotoImage(resized_img)
                banner_canvas.create_image(0, 0, image=self.banner_photo, anchor="nw")
            except Exception as e:
                print(f"[Dashboard BG Error]: {e}")

            # Draw glowing cyber texts on top of the wave image
            banner_canvas.create_text(
                20, 32,
                text=f"Welcome to the Academic Administration Dashboard, {self.current_user}!",
                font=("Segoe UI", 16, "bold"),
                fill="#ffffff",
                anchor="w"
            )
            banner_canvas.create_text(
                20, 68,
                text="Real-time institutional metrics, student enrollment, academic performance, and attendance compliance.",
                font=("Segoe UI", 10),
                fill="#cbd5e1",
                anchor="w"
            )
            banner_canvas.create_text(
                20, 98,
                text="⚡ 3D Holographic View Active  |  Session Status: Secure & Encrypted",
                font=("Segoe UI", 9, "bold"),
                fill="#38bdf8",
                anchor="w"
            )
        else:
            # Clean Fallback Banner
            banner = tk.Frame(overview_container, bg=THEME["bg_card"], bd=1, relief=tk.SOLID)
            banner.pack(fill=tk.X, pady=(0, 15), ipady=10, padx=5)

            tk.Label(
                banner,
                text=f"Welcome to the Administrative Dashboard, {self.current_user}!",
                font=FONT_TITLE,
                fg=THEME["text_dark"],
                bg=THEME["bg_card"]
            ).pack(anchor="w", padx=15, pady=(2, 2))

            tk.Label(
                banner,
                text="Real-time institutional metrics, student enrollment, academic performance, and attendance status.",
                font=FONT_REGULAR,
                fg=THEME["text_muted"],
                bg=THEME["bg_card"]
            ).pack(anchor="w", padx=15)

        # =============================================================
        # 2. 4 3D KPI METRIC CARDS
        # =============================================================
        kpi_frame = tk.Frame(overview_container, bg=THEME["bg_main"])
        kpi_frame.pack(fill=tk.X, pady=(0, 15), padx=5)

        cards_data = [
            ("Total Students", self.var_metric_students, "👨‍🎓", "#2563eb", "#eff6ff"),
            ("Active Courses", self.var_metric_courses, "📚", "#d97706", "#fef3c7"),
            ("Distinct Subjects", self.var_metric_subjects, "📝", "#0891b2", "#cffafe"),
            ("Average Percentage", self.var_metric_avg_pct, "📈", "#059669", "#d1fae5"),
        ]

        for title, var, icon, color, bg_tint in cards_data:
            # 3D Raised Frame
            card = tk.Frame(kpi_frame, bg=THEME["bg_card"], bd=2, relief=tk.RAISED)
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=6, ipady=8)

            top_row = tk.Frame(card, bg=THEME["bg_card"])
            top_row.pack(fill=tk.X, padx=12, pady=(8, 2))

            tk.Label(top_row, text=title.upper(), font=FONT_SMALL, fg=THEME["text_muted"], bg=THEME["bg_card"]).pack(side=tk.LEFT)
            tk.Label(top_row, text=icon, font=("Segoe UI", 16), fg=color, bg=bg_tint, width=2, height=1).pack(side=tk.RIGHT)

            tk.Label(card, textvariable=var, font=("Segoe UI", 22, "bold"), fg=color, bg=THEME["bg_card"]).pack(anchor="w", padx=12, pady=(2, 8))

        # =============================================================
        # 3. QUICK ACTIONS SHORTCUTS (3D TACTILE BUTTONS)
        # =============================================================
        actions_card = tk.LabelFrame(
            overview_container,
            text=" Quick Administrative Shortcuts ",
            font=FONT_HEADING,
            fg=THEME["primary"],
            bg=THEME["bg_card"],
            bd=1,
            relief=tk.SOLID
        )
        actions_card.pack(fill=tk.X, pady=(0, 15), padx=5, ipady=8)

        actions_inner = tk.Frame(actions_card, bg=THEME["bg_card"])
        actions_inner.pack(fill=tk.X, padx=10, pady=5)

        actions = [
            ("➕ Add New Student", THEME["primary"], self.show_students),
            ("📝 Record Academic Marks", THEME["success"], self.show_marks),
            ("📅 Log Class Attendance", THEME["warning"], self.show_attendance),
            ("👤 View Student Profile", THEME["info"], self.show_profile),
            ("📑 Generate Reports", "#6366f1", self.show_reports),
        ]

        for text, bg_col, cmd in actions:
            btn = tk.Button(
                actions_inner,
                text=text,
                font=FONT_BOLD,
                bg=bg_col,
                fg=THEME["text_light"],
                relief=tk.RAISED,
                bd=2,
                cursor="hand2",
                command=cmd,
                padx=10,
                pady=6
            )
            btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)

        # =============================================================
        # 4. RECENT ENROLLMENT TABLE
        # =============================================================
        table_card = tk.LabelFrame(
            overview_container,
            text=" Recently Enrolled Students ",
            font=FONT_HEADING,
            fg=THEME["primary"],
            bg=THEME["bg_card"],
            bd=1,
            relief=tk.SOLID
        )
        table_card.pack(fill=tk.BOTH, expand=True, padx=5)

        table_top = tk.Frame(table_card, bg=THEME["bg_card"])
        table_top.pack(fill=tk.X, padx=10, pady=6)

        tk.Label(
            table_top,
            text="Latest student admissions recorded in the database:",
            font=FONT_REGULAR,
            fg=THEME["text_muted"],
            bg=THEME["bg_card"]
        ).pack(side=tk.LEFT)

        btn_refresh = tk.Button(
            table_top,
            text="🔄 Refresh Overview",
            font=FONT_REGULAR,
            bg=THEME["info"],
            fg=THEME["text_light"],
            relief=tk.RAISED,
            bd=1,
            cursor="hand2",
            command=self.refresh_metrics
        )
        btn_refresh.pack(side=tk.RIGHT)

        tree_frame = tk.Frame(table_card, bg=THEME["bg_card"])
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        scroll_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        self.overview_tree = ttk.Treeview(
            tree_frame,
            columns=("student_id", "name", "roll_no", "course", "branch", "semester", "phone", "email"),
            show="headings",
            yscrollcommand=scroll_y.set,
            height=6
        )
        scroll_y.config(command=self.overview_tree.yview)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.overview_tree.pack(fill=tk.BOTH, expand=True)

        cols = {
            "student_id": ("Student ID", 90),
            "name": ("Full Name", 140),
            "roll_no": ("Roll Number", 90),
            "course": ("Course", 80),
            "branch": ("Branch", 140),
            "semester": ("Semester", 70),
            "phone": ("Phone Number", 100),
            "email": ("Email Address", 160)
        }
        for cid, (cname, cwidth) in cols.items():
            self.overview_tree.heading(cid, text=cname, anchor=tk.CENTER)
            self.overview_tree.column(cid, width=cwidth, anchor=tk.CENTER if cwidth < 100 else tk.W)

    def refresh_metrics(self):
        """Calculates and refreshes the KPI metric values and overview table."""
        try:
            conn = get_connection()
            cursor = conn.cursor()

            # 1. Total Students
            cursor.execute("SELECT COUNT(*) FROM students")
            total_students = cursor.fetchone()[0]
            self.var_metric_students.set(str(total_students))

            # 2. Distinct Courses
            cursor.execute("SELECT COUNT(DISTINCT course) FROM students")
            total_courses = cursor.fetchone()[0]
            self.var_metric_courses.set(str(total_courses))

            # 3. Distinct Subjects across marks & attendance
            cursor.execute("""
                SELECT COUNT(DISTINCT subject) FROM (
                    SELECT subject FROM marks
                    UNION
                    SELECT subject FROM attendance
                )
            """)
            total_subjects = cursor.fetchone()[0]
            self.var_metric_subjects.set(str(total_subjects))

            # 4. Average Student Percentage
            cursor.execute("SELECT AVG(total_marks) FROM marks")
            avg_marks = cursor.fetchone()[0]
            if avg_marks is not None:
                self.var_metric_avg_pct.set(f"{avg_marks:.1f} %")
            else:
                self.var_metric_avg_pct.set("N/A")

            # 5. Populate Overview Table (Recent 10)
            if hasattr(self, "overview_tree"):
                for item in self.overview_tree.get_children():
                    self.overview_tree.delete(item)

                cursor.execute("""
                    SELECT student_id, name, roll_no, course, branch, semester, phone, email
                    FROM students
                    ORDER BY rowid DESC
                    LIMIT 10
                """)
                for row in cursor.fetchall():
                    self.overview_tree.insert("", tk.END, values=row)

            conn.close()

        except sqlite3.Error as e:
            print(f"[Dashboard Error]: Failed to refresh metrics: {e}")

    def confirm_logout(self):
        """Confirms and logs out current user back to login screen."""
        confirm = messagebox.askyesno("Confirm Logout", "Are you sure you want to log out?", parent=self.root)
        if confirm:
            self.root.destroy()
            if self.login_root:
                self.login_root.deiconify()
            else:
                from login import LoginWindow
                new_root = tk.Tk()
                LoginWindow(new_root)
                new_root.mainloop()

    def confirm_exit(self):
        """Confirms and exits application cleanly."""
        confirm = messagebox.askyesno("Exit Application", "Are you sure you want to exit the application?", parent=self.root)
        if confirm:
            self.root.destroy()
            if self.login_root:
                self.login_root.destroy()
