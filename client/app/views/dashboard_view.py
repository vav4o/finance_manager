import tkinter as tk
from tkinter import ttk

from services.account_service import create_account, delete_account, get_accounts, update_account
from services.category_service import create_category, delete_category, get_categories
from ui.design import STATUS_COLOR
from ui.widgets import add_entry, add_section_title, clear_window


account_id = None
category_id = None


def create_dashboard_view(window, user, logout):
    clear_window(window)
    window.geometry("720x650")

    header = ttk.Frame(window, style="Header.TFrame", padding=(24, 16))
    header.pack(fill="x")

    title = ttk.Label(header, text="Personal Finance Manager", style="Header.TLabel")
    title.pack(side="left")

    user_text = f"{user['first_name']} {user.get('last_name') or ''}".strip()
    user_label = ttk.Label(header, text=user_text, style="HeaderName.TLabel")
    user_label.pack(side="left", padx=(18, 0))

    logout_button = ttk.Button(header, text="Logout", command=logout)
    logout_button.pack(side="right")

    form = ttk.Frame(window, padding=18)
    form.pack(fill="both", expand=True, padx=24, pady=24)

    tabs = ttk.Notebook(form)
    tabs.pack(fill="both", expand=True)

    accounts_tab = ttk.Frame(tabs, padding=18)
    categories_tab = ttk.Frame(tabs, padding=18)

    tabs.add(accounts_tab, text="Accounts")
    tabs.add(categories_tab, text="Categories")

    create_accounts_tab(accounts_tab)
    create_categories_tab(categories_tab)


def create_accounts_tab(parent):
    global account_name, account_type, account_currency, account_balance, accounts_table, account_status

    add_section_title(parent, "Accounts", 0)

    account_name = add_entry(parent, "Name", 1)

    ttk.Label(parent, text="Type").grid(row=2, column=0, sticky="w", pady=7)
    account_type = ttk.Combobox(parent, values=["cash", "bank", "card", "savings"], state="readonly", width=26)
    account_type.grid(row=2, column=1, sticky="ew", pady=7, padx=(12, 0))
    account_type.set("cash")

    account_currency = add_entry(parent, "Currency", 3)
    account_currency.insert(0, "BGN")

    account_balance = add_entry(parent, "Balance", 4)
    account_balance.insert(0, "0")

    buttons = ttk.Frame(parent)
    buttons.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(10, 12))

    ttk.Button(buttons, text="Save", command=save_account).pack(side="left", expand=True, fill="x", padx=(0, 5))
    ttk.Button(buttons, text="Clear", command=clear_account_form).pack(side="left", expand=True, fill="x", padx=5)
    ttk.Button(buttons, text="Delete", command=remove_account).pack(side="left", expand=True, fill="x", padx=5)
    ttk.Button(buttons, text="Refresh", command=load_accounts).pack(side="left", expand=True, fill="x", padx=(5, 0))

    columns = ("id", "name", "type", "currency", "balance")
    accounts_table = ttk.Treeview(parent, columns=columns, show="headings", height=8)

    for column in columns:
        accounts_table.heading(column, text=column.title())

    accounts_table.column("id", width=40)
    accounts_table.column("name", width=120)
    accounts_table.column("type", width=80)
    accounts_table.column("currency", width=80)
    accounts_table.column("balance", width=90)

    accounts_table.grid(row=6, column=0, columnspan=2, sticky="nsew")
    accounts_table.bind("<<TreeviewSelect>>", select_account)

    account_status = ttk.Label(parent, text="", foreground=STATUS_COLOR)
    account_status.grid(row=7, column=0, columnspan=2, sticky="w", pady=(10, 0))

    parent.rowconfigure(6, weight=1)
    parent.columnconfigure(1, weight=1)

    load_accounts()


def create_categories_tab(parent):
    global category_name, category_type, category_color, categories_table, category_status

    add_section_title(parent, "Categories", 0)

    category_name = add_entry(parent, "Name", 1)

    ttk.Label(parent, text="Type").grid(row=2, column=0, sticky="w", pady=7)
    category_type = ttk.Combobox(parent, values=["income", "expense"], state="readonly", width=26)
    category_type.grid(row=2, column=1, sticky="ew", pady=7, padx=(12, 0))
    category_type.set("expense")

    category_color = add_entry(parent, "Color", 3)
    category_color.insert(0, "#2563eb")

    buttons = ttk.Frame(parent)
    buttons.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(10, 12))

    ttk.Button(buttons, text="Create", command=save_category).pack(side="left", expand=True, fill="x", padx=(0, 5))
    ttk.Button(buttons, text="Clear", command=clear_category_form).pack(side="left", expand=True, fill="x", padx=5)
    ttk.Button(buttons, text="Delete", command=remove_category).pack(side="left", expand=True, fill="x", padx=5)
    ttk.Button(buttons, text="Refresh", command=load_categories).pack(side="left", expand=True, fill="x", padx=(5, 0))

    columns = ("id", "name", "type", "color")
    categories_table = ttk.Treeview(parent, columns=columns, show="headings", height=10)

    for column in columns:
        categories_table.heading(column, text=column.title())

    categories_table.column("id", width=40)
    categories_table.column("name", width=140)
    categories_table.column("type", width=90)
    categories_table.column("color", width=100)

    categories_table.grid(row=5, column=0, columnspan=2, sticky="nsew")
    categories_table.bind("<<TreeviewSelect>>", select_category)

    category_status = ttk.Label(parent, text="", foreground=STATUS_COLOR)
    category_status.grid(row=6, column=0, columnspan=2, sticky="w", pady=(10, 0))

    parent.rowconfigure(5, weight=1)
    parent.columnconfigure(1, weight=1)

    load_categories()


def load_accounts():
    accounts_table.delete(*accounts_table.get_children())

    try:
        for account in get_accounts():
            values = (
                account["id"],
                account["name"],
                account["type"],
                account["currency"],
                account["balance"],
            )
            accounts_table.insert("", tk.END, values=values)
    except Exception as exc:
        account_status.config(text=str(exc))


def save_account():
    global account_id

    try:
        name = account_name.get().strip()
        currency = account_currency.get().strip().upper()
        data = {
            "name": name,
            "type": account_type.get(),
            "currency": currency,
            "balance": float(account_balance.get()),
        }

        if not name:
            account_status.config(text="Please enter account name.")
            return

        if len(name) > 50:
            account_status.config(text="Account name must be 50 characters or fewer.")
            return

        if len(currency) != 3 or not currency.isalpha():
            account_status.config(text="Currency must be a 3-letter code.")
            return

        if account_id:
            update_account(account_id, data)
            account_status.config(text="Account updated.")
        else:
            create_account(data)
            account_status.config(text="Account created.")

        clear_account_form()
        load_accounts()
    except ValueError:
        account_status.config(text="Balance must be a number.")
    except Exception as exc:
        account_status.config(text=str(exc))


def select_account(event):
    global account_id

    selected = accounts_table.selection()
    if not selected:
        return

    values = accounts_table.item(selected[0], "values")
    account_id = values[0]

    account_name.delete(0, tk.END)
    account_name.insert(0, values[1])
    account_type.set(values[2])
    account_currency.delete(0, tk.END)
    account_currency.insert(0, values[3])
    account_balance.delete(0, tk.END)
    account_balance.insert(0, values[4])


def remove_account():
    if not account_id:
        account_status.config(text="Select an account first.")
        return

    try:
        delete_account(account_id)
        clear_account_form()
        load_accounts()
        account_status.config(text="Account deleted.")
    except Exception as exc:
        account_status.config(text=str(exc))


def clear_account_form():
    global account_id

    account_id = None
    account_name.delete(0, tk.END)
    account_type.set("cash")
    account_currency.delete(0, tk.END)
    account_currency.insert(0, "BGN")
    account_balance.delete(0, tk.END)
    account_balance.insert(0, "0")


def load_categories():
    categories_table.delete(*categories_table.get_children())

    try:
        for category in get_categories():
            values = (
                category["id"],
                category["name"],
                category["type"],
                category["icon_color"] or "",
            )
            categories_table.insert("", tk.END, values=values)
    except Exception as exc:
        category_status.config(text=str(exc))


def save_category():
    name = category_name.get().strip()
    data = {
        "name": name,
        "type": category_type.get(),
        "icon_color": category_color.get().strip() or None,
    }

    if not name:
        category_status.config(text="Please enter category name.")
        return

    if len(name) > 50:
        category_status.config(text="Category name must be 50 characters or fewer.")
        return

    try:
        create_category(data)
        clear_category_form()
        load_categories()
        category_status.config(text="Category created.")
    except Exception as exc:
        category_status.config(text=str(exc))


def select_category(event):
    global category_id

    selected = categories_table.selection()
    if not selected:
        return

    values = categories_table.item(selected[0], "values")
    category_id = values[0]

    category_name.delete(0, tk.END)
    category_name.insert(0, values[1])
    category_type.set(values[2])
    category_color.delete(0, tk.END)
    category_color.insert(0, values[3])


def remove_category():
    if not category_id:
        category_status.config(text="Select a category first.")
        return

    try:
        delete_category(category_id)
        clear_category_form()
        load_categories()
        category_status.config(text="Category deleted.")
    except Exception as exc:
        category_status.config(text=str(exc))


def clear_category_form():
    global category_id

    category_id = None
    category_name.delete(0, tk.END)
    category_type.set("expense")
    category_color.delete(0, tk.END)
    category_color.insert(0, "#2563eb")
