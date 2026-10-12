"""
utils.py - Utility Functions & Validation Helpers
==================================================
Contains common helper functions, regex-based input validation,
grading and attendance calculation formulas, and UI theme constants.
"""

import re
from datetime import datetime

# ============================================================================
# UI THEME CONFIGURATION (Modern Professional Dark Slate / Indigo Palette)
# ============================================================================
THEME = {
    "bg_main": "#f8fafc",          # Light grayish slate canvas
    "bg_card": "#ffffff",          # Pure white cards/panels
    "sidebar_bg": "#0f172a",       # Deep navy slate for sidebar
    "sidebar_active": "#1e293b",   # Active menu background
    "header_bg": "#1e293b",        # Top bar navy
    "primary": "#2563eb",          # Royal blue primary button
    "primary_hover": "#1d4ed8",    # Darker blue
    "success": "#10b981",          # Emerald green (Add, Good status)
    "success_hover": "#059669",
    "warning": "#f59e0b",          # Amber (Update, Average status)
    "warning_hover": "#d97706",
    "danger": "#ef4444",           # Coral red (Delete, Low status)
    "danger_hover": "#dc2626",
    "info": "#06b6d4",             # Cyan
    "info_hover": "#0891b2",
    "text_dark": "#0f172a",        # Slate 900 for dark text
    "text_muted": "#64748b",       # Slate 500 for secondary text
    "text_light": "#f8fafc",       # White/off-white for dark backgrounds
    "border": "#cbd5e1",           # Border slate 300
    "entry_bg": "#ffffff",         # Input field background
}

FONT_TITLE = ("Segoe UI", 16, "bold")
FONT_SUBTITLE = ("Segoe UI", 12, "bold")
FONT_HEADING = ("Segoe UI", 10, "bold")
FONT_REGULAR = ("Segoe UI", 9)
FONT_BOLD = ("Segoe UI", 9, "bold")
FONT_SMALL = ("Segoe UI", 8)


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def validate_required(fields_dict):
    """
    Validates that none of the required fields are empty.
    Returns (True, "") or (False, "Field Name is required.")
    """
    for field_name, value in fields_dict.items():
        if value is None or str(value).strip() == "":
            return False, f"'{field_name}' cannot be empty."
    return True, ""


def validate_email(email):
    """
    Validates standard email structure using regular expressions.
    """
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if re.match(pattern, email.strip()):
        return True, ""
    return False, "Invalid email address format (e.g. student@college.edu)."


def validate_phone(phone):
    """
    Validates that the phone number contains exactly 10 digits.
    """
    cleaned = re.sub(r"[\s\-\(\)\+]", "", phone)
    # Remove leading 91 if 12 digits provided
    if len(cleaned) == 12 and cleaned.startswith("91"):
        cleaned = cleaned[2:]
    if re.fullmatch(r"\d{10}", cleaned):
        return True, cleaned
    return False, "Phone number must contain exactly 10 digits."


def validate_date(date_str):
    """
    Validates that the date is in YYYY-MM-DD format and is a valid calendar date.
    """
    try:
        parsed_date = datetime.strptime(date_str.strip(), "%Y-%m-%d")
        # Ensure DOB is not in the future
        if parsed_date > datetime.now():
            return False, "Date of Birth cannot be in the future."
        return True, ""
    except ValueError:
        return False, "Date must be in YYYY-MM-DD format (e.g. 2003-05-14)."


def validate_marks(internal_str, external_str):
    """
    Validates internal and external marks inputs.
    Internal: 0 - 30 (or 50)
    External: 0 - 70 (or 50)
    Total out of 100.
    """
    try:
        internal = float(internal_str)
        external = float(external_str)
    except ValueError:
        return False, "Marks must be numeric values.", 0.0, 0.0, 0.0

    if not (0 <= internal <= 30):
        return False, "Internal marks must be between 0 and 30.", 0.0, 0.0, 0.0

    if not (0 <= external <= 70):
        return False, "External marks must be between 0 and 70.", 0.0, 0.0, 0.0

    total = internal + external
    return True, "", internal, external, total


def validate_attendance(total_classes_str, classes_attended_str):
    """
    Validates attendance numbers.
    Classes attended cannot exceed total classes.
    """
    try:
        total = int(total_classes_str)
        attended = int(classes_attended_str)
    except ValueError:
        return False, "Total classes and attended classes must be positive whole numbers.", 0, 0, 0.0

    if total <= 0:
        return False, "Total classes must be greater than zero.", 0, 0, 0.0

    if attended < 0:
        return False, "Classes attended cannot be negative.", 0, 0, 0.0

    if attended > total:
        return False, "Classes attended cannot exceed total classes held.", 0, 0, 0.0

    percentage = round((attended / total) * 100, 2)
    return True, "", total, attended, percentage


# ============================================================================
# ACADEMIC CALCULATION FORMULAS
# ============================================================================

def calculate_grade(total_marks):
    """
    Calculates academic letter grade based on college standards:
    90 - 100 : A+
    80 - 89  : A
    70 - 79  : B+
    60 - 69  : B
    50 - 59  : C
    40 - 49  : D
    Below 40 : F
    """
    marks = float(total_marks)
    if marks >= 90:
        return "A+"
    elif marks >= 80:
        return "A"
    elif marks >= 70:
        return "B+"
    elif marks >= 60:
        return "B"
    elif marks >= 50:
        return "C"
    elif marks >= 40:
        return "D"
    else:
        return "F"


def get_attendance_status(percentage):
    """
    Classifies attendance percentage:
    >= 75% : Good (Eligible for university exams)
    60% - 74% : Average (Warning zone)
    < 60% : Low (Shortage / Debarred risk)
    """
    pct = float(percentage)
    if pct >= 75.0:
        return "Good"
    elif pct >= 60.0:
        return "Average"
    else:
        return "Low"


# ============================================================================
# CUSTOM 3D TOGGLE SWITCH WIDGET
# ============================================================================

import tkinter as tk

class ModernToggleSwitch(tk.Canvas):
    """
    An interactive, animated-feel 3D pill toggle switch widget for Tkinter.
    Features rounded pill track, 3D knob drop shadow, and smooth toggling.
    """
    def __init__(self, parent, variable=None, command=None,
                 width=46, height=24, bg_color="#ffffff",
                 on_color="#2563eb", off_color="#cbd5e1", knob_color="#ffffff"):
        super().__init__(parent, width=width, height=height,
                         bg=bg_color, highlightthickness=0, bd=0, cursor="hand2")
        self.variable = variable or tk.BooleanVar(value=False)
        self.command = command
        self.width = width
        self.height = height
        self.on_color = on_color
        self.off_color = off_color
        self.knob_color = knob_color

        self.radius = height // 2
        self.bind("<Button-1>", self.toggle)
        self.render()

    def render(self):
        self.delete("all")
        is_on = self.variable.get()
        track_color = self.on_color if is_on else self.off_color

        r = self.radius
        w = self.width
        h = self.height

        # 3D Pill Track
        self.create_oval(0, 0, 2 * r, h, fill=track_color, outline=track_color, tags="track")
        self.create_oval(w - 2 * r, 0, w, h, fill=track_color, outline=track_color, tags="track")
        self.create_rectangle(r, 0, w - r, h, fill=track_color, outline=track_color, tags="track")

        # Knob Dimensions & Shadow
        pad = 2
        knob_size = h - 2 * pad
        kx = w - pad - knob_size if is_on else pad

        # 3D Knob Drop Shadow
        self.create_oval(
            kx + 1, pad + 1, kx + knob_size + 1, pad + knob_size + 1,
            fill="#94a3b8" if not is_on else "#1d4ed8", outline="", tags="shadow"
        )
        # Main Knob
        self.create_oval(
            kx, pad, kx + knob_size, pad + knob_size,
            fill=self.knob_color, outline="#f1f5f9", tags="knob"
        )

    def toggle(self, event=None):
        new_val = not self.variable.get()
        self.variable.set(new_val)
        self.render()
        if self.command:
            self.command()

    def set(self, val):
        self.variable.set(bool(val))
        self.render()

