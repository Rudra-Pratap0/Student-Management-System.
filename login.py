"""
login.py - Administrator Authentication Screen
==================================================
Features a 3D elevated split-card layout, holographic cyber-ID
branding graphic, interactive 3D toggle switch, and secure
credential verification with SQLite.
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from PIL import Image, ImageTk

from database import get_connection, init_db
from utils import (
    THEME, FONT_TITLE, FONT_SUBTITLE, FONT_HEADING, FONT_REGULAR, FONT_BOLD, FONT_SMALL,
    ModernToggleSwitch
)

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
HERO_IMAGE_PATH = os.path.join(ASSETS_DIR, "login_hero.png")


class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Management System — Administrator Authentication")
        self.root.geometry("900x560")
        self.root.resizable(False, False)
        self.root.configure(bg="#0a0f1d")  # Deep cyber slate background

        # Center window on screen
        self.center_window()

        # State variable for password visibility toggle
        self.show_password_var = tk.BooleanVar(value=False)

        # Build UI Components with 3D effects and Hero image
        self.create_widgets()

    def center_window(self):
        self.root.update_idletasks()
        width = 900
        height = 560
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def create_widgets(self):
        # =============================================================
        # 1. 3D OUTER DROP-SHADOW & MAIN CONTAINER
        # =============================================================
        # Multi-layered 3D shadow frames creating physical depth
        shadow_2 = tk.Frame(self.root, bg="#020617")
        shadow_2.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=834, height=484)

        shadow_1 = tk.Frame(self.root, bg="#0f172a")
        shadow_1.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=826, height=476)

        # Main Split Canvas / Card
        self.main_card = tk.Frame(self.root, bg=THEME["bg_card"], bd=1, relief=tk.SOLID)
        self.main_card.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=820, height=470)

        # =============================================================
        # 2. LEFT SIDE: 3D HOLOGRAPHIC HERO PANEL
        # =============================================================
        left_hero = tk.Frame(self.main_card, bg="#091428", width=380)
        left_hero.pack(side=tk.LEFT, fill=tk.BOTH)
        left_hero.pack_propagate(False)

        # Header tag on left panel
        lbl_brand_tag = tk.Label(
            left_hero,
            text="🎓 CAMPUS ID VERIFICATION",
            font=("Segoe UI", 9, "bold"),
            fg="#38bdf8",
            bg="#091428"
        )
        lbl_brand_tag.pack(anchor="w", padx=25, pady=(25, 5))

        lbl_hero_title = tk.Label(
            left_hero,
            text="Student Management\nSystem Portal",
            font=("Segoe UI", 16, "bold"),
            fg="#ffffff",
            bg="#091428",
            justify=tk.LEFT
        )
        lbl_hero_title.pack(anchor="w", padx=25, pady=(0, 10))

        # Hero Graphic Display
        self.hero_img_label = tk.Label(left_hero, bg="#091428")
        self.hero_img_label.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        self.load_hero_image()

        # Footer Badge
        lbl_security = tk.Label(
            left_hero,
            text="🔒 256-Bit Encrypted Session | University Security",
            font=FONT_SMALL,
            fg="#94a3b8",
            bg="#091428"
        )
        lbl_security.pack(side=tk.BOTTOM, pady=20)

        # =============================================================
        # 3. RIGHT SIDE: 3D ELEVATED AUTHENTICATION FORM
        # =============================================================
        right_panel = tk.Frame(self.main_card, bg=THEME["bg_card"], width=440)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Inner form wrapper
        form_inner = tk.Frame(right_panel, bg=THEME["bg_card"])
        form_inner.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)

        # Title & Subtitle
        lbl_title = tk.Label(
            form_inner,
            text="Admin Authentication",
            font=("Segoe UI", 18, "bold"),
            fg=THEME["text_dark"],
            bg=THEME["bg_card"]
        )
        lbl_title.pack(anchor="w", pady=(0, 4))

        lbl_sub = tk.Label(
            form_inner,
            text="Sign in to access student dossiers, marks, and attendance logs",
            font=FONT_SMALL,
            fg=THEME["text_muted"],
            bg=THEME["bg_card"],
            wraplength=340,
            justify=tk.LEFT
        )
        lbl_sub.pack(anchor="w", pady=(0, 20))

        # -------------------------------------------------------------
        # Username Input (with 3D border feel)
        # -------------------------------------------------------------
        lbl_user = tk.Label(
            form_inner,
            text="Administrator Username",
            font=FONT_BOLD,
            fg=THEME["text_dark"],
            bg=THEME["bg_card"]
        )
        lbl_user.pack(anchor="w", pady=(0, 3))

        user_border = tk.Frame(form_inner, bg="#cbd5e1", bd=1, relief=tk.SOLID)
        user_border.pack(fill=tk.X, pady=(0, 15))

        self.entry_username = tk.Entry(
            user_border,
            font=("Segoe UI", 10),
            bd=0,
            relief=tk.FLAT,
            bg="#f8fafc"
        )
        self.entry_username.pack(fill=tk.X, ipady=7, padx=8)
        self.entry_username.focus_set()

        # -------------------------------------------------------------
        # Password Input (with 3D border feel)
        # -------------------------------------------------------------
        lbl_pwd = tk.Label(
            form_inner,
            text="Password",
            font=FONT_BOLD,
            fg=THEME["text_dark"],
            bg=THEME["bg_card"]
        )
        lbl_pwd.pack(anchor="w", pady=(0, 3))

        pwd_border = tk.Frame(form_inner, bg="#cbd5e1", bd=1, relief=tk.SOLID)
        pwd_border.pack(fill=tk.X, pady=(0, 10))

        self.entry_password = tk.Entry(
            pwd_border,
            font=("Segoe UI", 10),
            bd=0,
            relief=tk.FLAT,
            show="*",
            bg="#f8fafc"
        )
        self.entry_password.pack(fill=tk.X, ipady=7, padx=8)

        # -------------------------------------------------------------
        # INTERACTIVE 3D TOGGLE SWITCH FOR PASSWORD VISIBILITY
        # -------------------------------------------------------------
        toggle_row = tk.Frame(form_inner, bg=THEME["bg_card"])
        toggle_row.pack(fill=tk.X, pady=(4, 20))

        self.pwd_toggle = ModernToggleSwitch(
            toggle_row,
            variable=self.show_password_var,
            command=self.toggle_password,
            width=44,
            height=22,
            bg_color=THEME["bg_card"],
            on_color=THEME["primary"],
            off_color="#cbd5e1",
            knob_color="#ffffff"
        )
        self.pwd_toggle.pack(side=tk.LEFT, padx=(0, 8))

        self.lbl_toggle_text = tk.Label(
            toggle_row,
            text="Show Password",
            font=FONT_SMALL,
            fg=THEME["text_muted"],
            bg=THEME["bg_card"],
            cursor="hand2"
        )
        self.lbl_toggle_text.pack(side=tk.LEFT)
        self.lbl_toggle_text.bind("<Button-1>", lambda e: self.pwd_toggle.toggle())

        # -------------------------------------------------------------
        # 3D TACTILE PUSH BUTTONS (Raised with click depression)
        # -------------------------------------------------------------
        btn_box = tk.Frame(form_inner, bg=THEME["bg_card"])
        btn_box.pack(fill=tk.X, pady=(5, 12))

        # 3D Sign In Button
        self.btn_login = tk.Button(
            btn_box,
            text="⚡ Log In",
            font=("Segoe UI", 10, "bold"),
            bg=THEME["primary"],
            fg=THEME["text_light"],
            activebackground=THEME["primary_hover"],
            activeforeground=THEME["text_light"],
            relief=tk.RAISED,
            bd=2,
            cursor="hand2",
            command=self.handle_login
        )
        self.btn_login.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, padx=(0, 6))

        # 3D Exit Button
        self.btn_exit = tk.Button(
            btn_box,
            text="Exit",
            font=("Segoe UI", 10, "bold"),
            bg="#dc2626",
            fg=THEME["text_light"],
            activebackground="#b91c1c",
            activeforeground=THEME["text_light"],
            relief=tk.RAISED,
            bd=2,
            cursor="hand2",
            command=self.root.destroy
        )
        self.btn_exit.pack(side=tk.RIGHT, fill=tk.X, expand=True, ipady=6, padx=(6, 0))

        # Hint Footer Box
        hint_box = tk.Frame(form_inner, bg="#f1f5f9", bd=1, relief=tk.SOLID)
        hint_box.pack(fill=tk.X, pady=(10, 0), ipady=5)

        lbl_hint = tk.Label(
            hint_box,
            text="🔑 Default Credentials:  admin  /  admin123",
            font=FONT_SMALL,
            fg=THEME["text_muted"],
            bg="#f1f5f9"
        )
        lbl_hint.pack()

        # Keyboard Bindings
        self.root.bind("<Return>", lambda event: self.handle_login())

    def load_hero_image(self):
        """Loads and smoothly resizes the 3D holographic hero image."""
        try:
            if os.path.exists(HERO_IMAGE_PATH):
                pil_img = Image.open(HERO_IMAGE_PATH)
                # Resize smoothly to fit left panel
                pil_img = pil_img.resize((350, 200), Image.Resampling.LANCZOS)
                self.hero_photo = ImageTk.PhotoImage(pil_img)
                self.hero_img_label.config(image=self.hero_photo)
            else:
                self.hero_img_label.config(
                    text="🎓\nSMART IDENTITY",
                    font=("Segoe UI", 24, "bold"),
                    fg="#38bdf8"
                )
        except Exception as e:
            print(f"[Login Image Error]: {e}")
            self.hero_img_label.config(
                text="🎓\nSMART IDENTITY",
                font=("Segoe UI", 24, "bold"),
                fg="#38bdf8"
            )

    def toggle_password(self):
        """Toggles masking on password entry via the 3D toggle switch."""
        if self.show_password_var.get():
            self.entry_password.config(show="")
            self.lbl_toggle_text.config(text="Hide Password", fg=THEME["primary"])
        else:
            self.entry_password.config(show="*")
            self.lbl_toggle_text.config(text="Show Password", fg=THEME["text_muted"])

    def handle_login(self):
        """Authenticates user against SQLite database."""
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()

        if not username or not password:
            messagebox.showwarning(
                "Incomplete Input",
                "Please enter both Username and Password to proceed.",
                parent=self.root
            )
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Parameterized query protects against SQL injection
            cursor.execute(
                "SELECT user_id, username FROM users WHERE username = ? AND password = ?",
                (username, password)
            )
            user_row = cursor.fetchone()
            conn.close()

            if user_row:
                messagebox.showinfo(
                    "Login Successful",
                    f"Welcome back, {username}! Access granted.",
                    parent=self.root
                )
                self.open_dashboard(username)
            else:
                messagebox.showerror(
                    "Access Denied",
                    "Invalid Username or Password.\nPlease check your credentials and try again.",
                    parent=self.root
                )
                self.entry_password.delete(0, tk.END)
                self.entry_password.focus_set()

        except sqlite3.Error as e:
            messagebox.showerror(
                "Database Error",
                f"An error occurred while connecting to the database:\n{e}",
                parent=self.root
            )

    def open_dashboard(self, username):
        """Transitions from login screen to the main dashboard."""
        self.root.unbind("<Return>")
        self.root.withdraw()

        from dashboard import DashboardWindow
        dashboard_root = tk.Toplevel()
        dashboard_root.protocol("WM_DELETE_WINDOW", self.root.destroy)
        DashboardWindow(dashboard_root, current_user=username, login_root=self.root)


if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = LoginWindow(root)
    root.mainloop()
