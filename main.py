"""
main.py - Application Entry Point & Launcher
==================================================
Initializes the SQLite database, configures modern ttk widget
styles and DPI scaling for Windows, and launches the Admin Login portal.
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox

# Ensure current script directory is in python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import init_db
from login import LoginWindow
from utils import THEME


def set_dpi_awareness():
    """Enables Windows Per-Monitor DPI awareness for crisp fonts."""
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass


def setup_application_styles(root):
    """Configures modern visual styles for standard ttk widgets."""
    style = ttk.Style(root)

    # Use available modern theme
    available_themes = style.theme_names()
    if "clam" in available_themes:
        style.theme_use("clam")
    elif "vista" in available_themes:
        style.theme_use("vista")

    # Treeview Styling
    style.configure(
        "Treeview",
        background="#ffffff",
        foreground=THEME["text_dark"],
        rowheight=26,
        fieldbackground="#ffffff",
        font=("Segoe UI", 9)
    )
    style.configure(
        "Treeview.Heading",
        background="#1e293b",
        foreground="#ffffff",
        font=("Segoe UI", 9, "bold"),
        relief="flat"
    )
    style.map(
        "Treeview.Heading",
        background=[("active", "#334155")]
    )
    style.map(
        "Treeview",
        background=[("selected", THEME["primary"])],
        foreground=[("selected", "#ffffff")]
    )

    # Combobox Styling
    style.configure(
        "TCombobox",
        fieldbackground="#ffffff",
        background="#ffffff"
    )


def main():
    # Set Windows DPI awareness for high-resolution displays
    set_dpi_awareness()

    # 1. Initialize SQLite Database & Tables
    try:
        init_db()
    except Exception as e:
        # Fallback tkinter alert if DB creation fails
        temp_root = tk.Tk()
        temp_root.withdraw()
        messagebox.showerror(
            "Fatal Error",
            f"Failed to initialize SQLite Database:\n{e}\n\nPlease verify file permissions."
        )
        sys.exit(1)

    # 2. Initialize Main Tkinter Root
    root = tk.Tk()
    root.title("Student Management System")

    # Apply widget styling
    setup_application_styles(root)

    # 3. Launch Administrator Authentication
    app = LoginWindow(root)

    # 4. Start Tkinter Main Event Loop
    root.mainloop()


if __name__ == "__main__":
    main()
