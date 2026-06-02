import tkinter as tk
from tkinter import ttk
import re

from services.auth_service import login_user, register_user
from ui.design import STATUS_COLOR
from ui.widgets import add_entry, clear_window

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def create_auth_view(window, after_login):
    clear_window(window)

    title = ttk.Label(window, text="Personal Finance Manager", style="Title.TLabel")
    title.pack(pady=(26, 6))

    subtitle = ttk.Label(window, text="Login or create your account", style="Subtitle.TLabel")
    subtitle.pack(pady=(0, 20))

    form = ttk.Frame(window, padding=18)
    form.pack(fill="both", expand=True, padx=28, pady=(0, 28))

    tabs = ttk.Notebook(form)
    tabs.pack(fill="both", expand=True)

    login_tab = ttk.Frame(tabs, padding=24)
    register_tab = ttk.Frame(tabs, padding=24)

    tabs.add(login_tab, text="Login")
    tabs.add(register_tab, text="Register")

    login_username = add_entry(login_tab, "Username", 0)
    login_password = add_entry(login_tab, "Password", 1, show="*")
    login_status = ttk.Label(login_tab, text="", foreground=STATUS_COLOR)

    register_username = add_entry(register_tab, "Username", 0)
    register_email = add_entry(register_tab, "Email", 1)
    register_password = add_entry(register_tab, "Password", 2, show="*")
    register_confirm = add_entry(register_tab, "Confirm password", 3, show="*")
    register_first_name = add_entry(register_tab, "First name", 4)
    register_last_name = add_entry(register_tab, "Last name", 5)
    register_currency = add_entry(register_tab, "Base currency", 6)
    register_currency.insert(0, "BGN")
    register_status = ttk.Label(register_tab, text="", foreground=STATUS_COLOR)

    def login():
        username = login_username.get().strip()
        password = login_password.get()

        if not username or not password:
            login_status.config(text="Please enter username and password.")
            return

        try:
            user = login_user(username, password)
            login_status.config(text=f"Welcome, {user['first_name']}!")
            after_login(user)
        except Exception as exc:
            login_status.config(text=str(exc))

    def register():
        password = register_password.get()
        base_currency = register_currency.get().strip().upper()
        data = {
            "nickname": register_username.get().strip(),
            "email": register_email.get().strip(),
            "password": password,
            "first_name": register_first_name.get().strip(),
            "last_name": register_last_name.get().strip() or None,
            "base_currency": base_currency,
        }

        confirm_password = register_confirm.get()

        if not data["nickname"] or not data["email"] or not data["first_name"]:
            register_status.config(text="Please fill username, email and first name.")
            return

        if len(data["nickname"]) < 2:
            register_status.config(text="Username must be at least 2 characters.")
            return

        if not EMAIL_PATTERN.match(data["email"]):
            register_status.config(text="Please enter a valid email address.")
            return

        if len(data["first_name"]) < 2:
            register_status.config(text="First name must be at least 2 characters.")
            return

        if len(password) < 8:
            register_status.config(text="Password must be at least 8 characters.")
            return

        if len(password) > 50:
            register_status.config(text="Password must be 50 characters or fewer.")
            return

        if len(password.encode("utf-8")) > 72:
            register_status.config(text="Password is too long. Please use fewer symbols.")
            return

        if data["password"] != confirm_password:
            register_status.config(text="Passwords do not match.")
            return

        if len(base_currency) != 3 or not base_currency.isalpha():
            register_status.config(text="Base currency must be a 3-letter code.")
            return

        try:
            register_user(data)

            register_status.config(text="Account created. You can login now.")
            tabs.select(login_tab)

            login_username.delete(0, tk.END)
            login_username.insert(0, data["nickname"])
        except Exception as exc:
            register_status.config(text=str(exc))

    login_button = ttk.Button(login_tab, text="Login", command=login)
    login_button.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(18, 0))

    login_status.grid(row=3, column=0, columnspan=2, sticky="w", pady=(16, 0))

    register_button = ttk.Button(register_tab, text="Create account", command=register)
    register_button.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(18, 0))

    register_status.grid(row=8, column=0, columnspan=2, sticky="w", pady=(16, 0))
