import json
import os
import tkinter as tk
from tkinter import ttk
from urllib import error, parse, request


API_URL = os.getenv("FINANCE_API_URL", "http://127.0.0.1:8000")
access_token = None


def send_request(path, body=None, headers=None):
    url = f"{API_URL}{path}"
    api_request = request.Request(url, data=body, headers=headers or {})

    try:
        with request.urlopen(api_request, timeout=8) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        raise Exception(read_error(exc))
    except error.URLError:
        raise Exception("Cannot connect to the server.")


def post_json(path, data):
    body = json.dumps(data).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    return send_request(path, body=body, headers=headers)


def post_form(path, data):
    body = parse.urlencode(data).encode("utf-8")
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    return send_request(path, body=body, headers=headers)


def read_error(exc):
    try:
        data = json.loads(exc.read().decode("utf-8"))
    except Exception:
        return "Something went wrong."

    detail = data.get("detail", "Something went wrong.")
    if isinstance(detail, list):
        messages = []
        for item in detail:
            location = " ".join(str(part) for part in item.get("loc", []))
            messages.append(f"{location}: {item.get('msg')}")
        return "\n".join(messages)

    return str(detail)


def add_entry(parent, label, row, show=None):
    ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=6)

    entry = ttk.Entry(parent, show=show)
    entry.grid(row=row, column=1, sticky="ew", pady=6, padx=(12, 0))

    parent.columnconfigure(1, weight=1)
    return entry


def login():
    global access_token

    data = {
        "username": login_username.get().strip(),
        "password": login_password.get(),
    }

    if not data["username"] or not data["password"]:
        login_status.config(text="Please enter username and password.")
        return

    try:
        response = post_form("/users/login", data)
        access_token = response["access_token"]

        headers = {"Authorization": f"Bearer {access_token}"}
        user = send_request("/users/me", headers=headers)

        login_status.config(text=f"Welcome, {user['first_name']}!")
    except Exception as exc:
        login_status.config(text=str(exc))


def register():
    data = {
        "nickname": register_username.get().strip(),
        "email": register_email.get().strip(),
        "password": register_password.get(),
        "first_name": register_first_name.get().strip(),
        "last_name": register_last_name.get().strip() or None,
        "base_currency": register_currency.get().strip().upper(),
    }

    confirm_password = register_confirm.get()

    if not data["nickname"] or not data["email"] or not data["first_name"]:
        register_status.config(text="Please fill username, email and first name.")
        return

    if data["password"] != confirm_password:
        register_status.config(text="Passwords do not match.")
        return

    try:
        post_json("/users/register", data)

        register_status.config(text="Account created. You can login now.")
        tabs.select(login_tab)

        login_username.delete(0, tk.END)
        login_username.insert(0, data["nickname"])
    except Exception as exc:
        register_status.config(text=str(exc))


window = tk.Tk()
window.title("Personal Finance Manager")
window.geometry("440x520")
window.resizable(False, False)

title = ttk.Label(window, text="Personal Finance Manager", font=("Segoe UI", 18, "bold"))
title.pack(pady=(24, 8))

subtitle = ttk.Label(window, text="Login or create your account")
subtitle.pack(pady=(0, 18))

tabs = ttk.Notebook(window)
tabs.pack(fill="both", expand=True, padx=24, pady=8)

login_tab = ttk.Frame(tabs, padding=20)
register_tab = ttk.Frame(tabs, padding=20)

tabs.add(login_tab, text="Login")
tabs.add(register_tab, text="Register")

login_username = add_entry(login_tab, "Username", 0)
login_password = add_entry(login_tab, "Password", 1, show="*")

login_button = ttk.Button(login_tab, text="Login", command=login)
login_button.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(18, 0))

login_status = ttk.Label(login_tab, text="")
login_status.grid(row=3, column=0, columnspan=2, sticky="w", pady=(16, 0))

register_username = add_entry(register_tab, "Username", 0)
register_email = add_entry(register_tab, "Email", 1)
register_password = add_entry(register_tab, "Password", 2, show="*")
register_confirm = add_entry(register_tab, "Confirm password", 3, show="*")
register_first_name = add_entry(register_tab, "First name", 4)
register_last_name = add_entry(register_tab, "Last name", 5)
register_currency = add_entry(register_tab, "Base currency", 6)
register_currency.insert(0, "BGN")

register_button = ttk.Button(register_tab, text="Create account", command=register)
register_button.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(18, 0))

register_status = ttk.Label(register_tab, text="")
register_status.grid(row=8, column=0, columnspan=2, sticky="w", pady=(16, 0))

window.mainloop()
