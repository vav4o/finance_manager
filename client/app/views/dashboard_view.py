import calendar
import datetime as dt
import tkinter as tk
from tkinter import messagebox, ttk

from services.account_service import create_account, delete_account, get_accounts, update_account
from services.admin_service import get_system_statistics, get_users, toggle_user_block
from services.api import ApiError
from services.budget_service import create_budget, delete_budget, get_budgets, update_budget
from services.category_service import create_category, delete_category, get_categories
from services.transaction_service import (
    create_transaction,
    delete_transaction,
    get_category_stats,
    get_monthly_stats,
    get_transactions,
    update_transaction,
)
from ui.design import STATUS_COLOR
from ui.widgets import add_entry, add_section_title, clear_window, set_entry


account_id = None
category_id = None
transaction_id = None
budget_id = None
admin_user_id = None

accounts_cache = []
categories_cache = []
transactions_cache = {}
budgets_cache = {}


def create_dashboard_view(window, user, logout):
    clear_window(window)
    window.geometry("980x850")
    window.minsize(900, 760)

    header = ttk.Frame(window, style="Header.TFrame", padding=(24, 16))
    header.pack(fill="x")

    ttk.Label(header, text="Personal Finance Manager", style="Header.TLabel").pack(side="left")

    user_text = f"{user['first_name']} {user.get('last_name') or ''}".strip()
    if user.get("role") == "admin":
        user_text = f"{user_text} (admin)"
    ttk.Label(header, text=user_text, style="HeaderName.TLabel").pack(side="left", padx=(18, 0))

    ttk.Button(header, text="Logout", command=logout).pack(side="right")

    form = ttk.Frame(window, padding=18)
    form.pack(fill="both", expand=True, padx=24, pady=24)

    if user.get("role") == "admin":
        create_admin_dashboard(form)
        return

    tabs = ttk.Notebook(form)
    tabs.pack(fill="both", expand=True)

    profile_tab = ttk.Frame(tabs, padding=18)
    accounts_tab = ttk.Frame(tabs, padding=18)
    categories_tab = ttk.Frame(tabs, padding=18)
    transactions_tab = ttk.Frame(tabs, padding=18)
    budgets_tab = ttk.Frame(tabs, padding=18)
    stats_tab = ttk.Frame(tabs, padding=18)

    tabs.add(profile_tab, text="Profile")
    tabs.add(accounts_tab, text="Accounts")
    tabs.add(categories_tab, text="Categories")
    tabs.add(transactions_tab, text="Transactions")
    tabs.add(budgets_tab, text="Budgets")
    tabs.add(stats_tab, text="Statistics")

    create_profile_tab(profile_tab, user)
    create_accounts_tab(accounts_tab)
    create_categories_tab(categories_tab)
    create_transactions_tab(transactions_tab)
    create_budgets_tab(budgets_tab)
    create_stats_tab(stats_tab)


def create_admin_dashboard(parent):
    tabs = ttk.Notebook(parent)
    tabs.pack(fill="both", expand=True)

    users_tab = ttk.Frame(tabs, padding=18)
    categories_tab = ttk.Frame(tabs, padding=18)
    stats_tab = ttk.Frame(tabs, padding=18)

    tabs.add(users_tab, text="Users")
    tabs.add(categories_tab, text="Global categories")
    tabs.add(stats_tab, text="System stats")

    create_admin_users_tab(users_tab)
    create_categories_tab(categories_tab, "Global categories")
    create_admin_stats_tab(stats_tab)


def create_profile_tab(parent, user):
    add_section_title(parent, "Profile", 0)

    fields = (
        ("Username", user.get("username", "")),
        ("Email", user.get("email", "")),
        ("First name", user.get("first_name", "")),
        ("Last name", user.get("last_name") or ""),
        ("Base currency", user.get("base_currency", "EUR")),
        ("Role", user.get("role", "")),
    )

    for row, (label, value) in enumerate(fields, start=1):
        entry = add_entry(parent, label, row)
        entry.insert(0, value)
        entry.config(state="readonly")

    profile_status = ttk.Label(parent, text="Profile editing needs a server update endpoint.", foreground=STATUS_COLOR)
    profile_status.grid(row=len(fields) + 1, column=0, columnspan=2, sticky="w", pady=(14, 0))


def create_accounts_tab(parent):
    global account_name, account_type, account_currency, account_balance, accounts_table, account_status

    add_section_title(parent, "Accounts", 0)
    account_name = add_entry(parent, "Name", 1)

    ttk.Label(parent, text="Type").grid(row=2, column=0, sticky="w", pady=7)
    account_type = ttk.Combobox(parent, values=["cash", "bank", "card", "savings"], state="readonly", width=26)
    account_type.grid(row=2, column=1, sticky="ew", pady=7, padx=(12, 0))
    account_type.set("cash")

    account_currency = add_entry(parent, "Currency", 3)
    account_currency.insert(0, "EUR")

    account_balance = add_entry(parent, "Balance", 4)
    account_balance.insert(0, "0")

    buttons = ttk.Frame(parent)
    buttons.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(10, 12))
    ttk.Button(buttons, text="Add", command=add_account).pack(side="left", expand=True, fill="x", padx=(0, 5))
    ttk.Button(buttons, text="Save changes", command=save_account_changes).pack(side="left", expand=True, fill="x", padx=5)
    ttk.Button(buttons, text="Clear", command=clear_account_form).pack(side="left", expand=True, fill="x", padx=5)
    ttk.Button(buttons, text="Delete", command=remove_account).pack(side="left", expand=True, fill="x", padx=5)
    ttk.Button(buttons, text="Refresh", command=load_accounts).pack(side="left", expand=True, fill="x", padx=(5, 0))

    accounts_table = make_table(parent, ("id", "name", "type", "currency", "balance"), 6, 8)
    accounts_table.bind("<<TreeviewSelect>>", select_account)

    account_status = ttk.Label(parent, text="", foreground=STATUS_COLOR)
    account_status.grid(row=7, column=0, columnspan=2, sticky="w", pady=(10, 0))
    parent.rowconfigure(6, weight=1)
    parent.columnconfigure(1, weight=1)
    load_accounts()


def create_categories_tab(parent, title="Categories"):
    global category_name, category_type, category_color, categories_table, category_status

    add_section_title(parent, title, 0)
    category_name = add_entry(parent, "Name", 1)

    ttk.Label(parent, text="Type").grid(row=2, column=0, sticky="w", pady=7)
    category_type = ttk.Combobox(parent, values=["income", "expense"], state="readonly", width=26)
    category_type.grid(row=2, column=1, sticky="ew", pady=7, padx=(12, 0))
    category_type.set("expense")

    category_color = add_entry(parent, "Color", 3)
    category_color.insert(0, "#2563eb")

    buttons = ttk.Frame(parent)
    buttons.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(10, 12))
    ttk.Button(buttons, text="Add", command=save_category).pack(side="left", expand=True, fill="x", padx=(0, 5))
    ttk.Button(buttons, text="Clear", command=clear_category_form).pack(side="left", expand=True, fill="x", padx=5)
    ttk.Button(buttons, text="Delete", command=remove_category).pack(side="left", expand=True, fill="x", padx=5)
    ttk.Button(buttons, text="Refresh", command=load_categories).pack(side="left", expand=True, fill="x", padx=(5, 0))

    categories_table = make_table(parent, ("id", "name", "type", "color"), 5, 10)
    categories_table.bind("<<TreeviewSelect>>", select_category)

    category_status = ttk.Label(parent, text="", foreground=STATUS_COLOR)
    category_status.grid(row=6, column=0, columnspan=2, sticky="w", pady=(10, 0))
    parent.rowconfigure(5, weight=1)
    parent.columnconfigure(1, weight=1)
    load_categories()


def create_transactions_tab(parent):
    global transaction_account, transaction_category, transaction_amount, transaction_currency
    global transaction_date, transaction_description, transaction_notes, transaction_recurring
    global transaction_table, transaction_status, transaction_filter_type, transaction_filter_account
    global transaction_filter_category, transaction_filter_start, transaction_filter_end, transaction_filter_search
    global transaction_sort_by, transaction_sort_order, transaction_filter_limit

    add_section_title(parent, "Transactions", 0)
    transaction_account = add_combo(parent, "Account", 1)
    transaction_category = add_combo(parent, "Category", 2)
    transaction_amount = add_entry(parent, "Amount", 3)
    transaction_currency = add_entry(parent, "Currency", 4)
    transaction_currency.insert(0, "EUR")
    transaction_date = add_entry(parent, "Date", 5)
    transaction_date.insert(0, dt.date.today().isoformat())
    transaction_description = add_entry(parent, "Description", 6)
    transaction_notes = add_entry(parent, "Notes", 7)

    transaction_recurring = tk.BooleanVar(value=False)
    ttk.Checkbutton(parent, text="Recurring monthly", variable=transaction_recurring).grid(
        row=8, column=1, sticky="w", pady=7, padx=(12, 0)
    )

    filter_frame = ttk.Frame(parent)
    filter_frame.grid(row=9, column=0, columnspan=2, sticky="ew", pady=(6, 2))

    ttk.Label(filter_frame, text="Type").grid(row=0, column=0, sticky="w", padx=(0, 6))
    transaction_filter_type = ttk.Combobox(filter_frame, values=["", "income", "expense"], state="readonly", width=10)
    transaction_filter_type.grid(row=0, column=1, sticky="ew", padx=(0, 10))

    ttk.Label(filter_frame, text="Account").grid(row=0, column=2, sticky="w", padx=(0, 6))
    transaction_filter_account = ttk.Combobox(filter_frame, state="readonly", width=18)
    transaction_filter_account.grid(row=0, column=3, sticky="ew", padx=(0, 10))

    ttk.Label(filter_frame, text="Category").grid(row=0, column=4, sticky="w", padx=(0, 6))
    transaction_filter_category = ttk.Combobox(filter_frame, state="readonly", width=18)
    transaction_filter_category.grid(row=0, column=5, sticky="ew")

    ttk.Label(filter_frame, text="From").grid(row=1, column=0, sticky="w", padx=(0, 6), pady=(7, 0))
    transaction_filter_start = ttk.Entry(filter_frame, width=12)
    transaction_filter_start.grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=(7, 0))

    ttk.Label(filter_frame, text="To").grid(row=1, column=2, sticky="w", padx=(0, 6), pady=(7, 0))
    transaction_filter_end = ttk.Entry(filter_frame, width=12)
    transaction_filter_end.grid(row=1, column=3, sticky="ew", padx=(0, 10), pady=(7, 0))

    ttk.Label(filter_frame, text="Search").grid(row=1, column=4, sticky="w", padx=(0, 6), pady=(7, 0))
    transaction_filter_search = ttk.Entry(filter_frame, width=18)
    transaction_filter_search.grid(row=1, column=5, sticky="ew", pady=(7, 0))

    ttk.Label(filter_frame, text="Sort").grid(row=2, column=0, sticky="w", padx=(0, 6), pady=(7, 0))
    transaction_sort_by = ttk.Combobox(filter_frame, values=["date", "amount"], state="readonly", width=10)
    transaction_sort_by.grid(row=2, column=1, sticky="ew", padx=(0, 10), pady=(7, 0))
    transaction_sort_by.set("date")

    transaction_sort_order = ttk.Combobox(filter_frame, values=["desc", "asc"], state="readonly", width=10)
    transaction_sort_order.grid(row=2, column=3, sticky="ew", padx=(0, 10), pady=(7, 0))
    transaction_sort_order.set("desc")

    ttk.Label(filter_frame, text="Limit").grid(row=2, column=4, sticky="w", padx=(0, 6), pady=(7, 0))
    transaction_filter_limit = ttk.Entry(filter_frame, width=8)
    transaction_filter_limit.grid(row=2, column=5, sticky="w", pady=(7, 0))
    transaction_filter_limit.insert(0, "50")

    filter_frame.columnconfigure(5, weight=1)

    buttons = ttk.Frame(parent)
    buttons.grid(row=10, column=0, columnspan=2, sticky="ew", pady=(10, 12))
    ttk.Button(buttons, text="Add", command=add_transaction).pack(side="left", expand=True, fill="x", padx=(0, 5))
    ttk.Button(buttons, text="Save changes", command=save_transaction_changes).pack(side="left", expand=True, fill="x", padx=5)
    ttk.Button(buttons, text="Clear", command=clear_transaction_form).pack(side="left", expand=True, fill="x", padx=5)
    ttk.Button(buttons, text="Delete", command=remove_transaction).pack(side="left", expand=True, fill="x", padx=5)
    ttk.Button(buttons, text="Apply filters", command=load_transactions).pack(side="left", expand=True, fill="x", padx=5)
    ttk.Button(buttons, text="Reset filters", command=clear_transaction_filters).pack(side="left", expand=True, fill="x", padx=(5, 0))

    columns = ("id", "date", "account", "category", "type", "amount", "currency", "recurring", "description")
    transaction_table = make_table(parent, columns, 11, 5)
    transaction_table.bind("<<TreeviewSelect>>", select_transaction)

    transaction_status = ttk.Label(parent, text="", foreground=STATUS_COLOR)
    transaction_status.grid(row=12, column=0, columnspan=2, sticky="w", pady=(10, 0))
    parent.rowconfigure(11, weight=1)
    parent.columnconfigure(1, weight=1)
    refresh_account_category_choices()
    load_transactions()


def create_budgets_tab(parent):
    global budget_month, budget_year, budget_category, budget_amount, budgets_table, budget_status
    global budget_progress, budget_progress_label

    add_section_title(parent, "Budgets", 0)
    today = dt.date.today()
    budget_month = add_entry(parent, "Month", 1)
    budget_month.insert(0, str(today.month))
    budget_year = add_entry(parent, "Year", 2)
    budget_year.insert(0, str(today.year))
    budget_category = add_combo(parent, "Category", 3)
    budget_amount = add_entry(parent, "Amount", 4)

    buttons = ttk.Frame(parent)
    buttons.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(10, 12))
    ttk.Button(buttons, text="Save", command=save_budget).pack(side="left", expand=True, fill="x", padx=(0, 5))
    ttk.Button(buttons, text="Clear", command=clear_budget_form).pack(side="left", expand=True, fill="x", padx=5)
    ttk.Button(buttons, text="Delete", command=remove_budget).pack(side="left", expand=True, fill="x", padx=5)
    ttk.Button(buttons, text="Refresh", command=load_budgets).pack(side="left", expand=True, fill="x", padx=(5, 0))

    budgets_table = make_table(parent, ("id", "month", "year", "category", "amount", "spent", "left", "used"), 6, 9)
    budgets_table.bind("<<TreeviewSelect>>", select_budget)

    budget_status = ttk.Label(parent, text="", foreground=STATUS_COLOR)
    budget_status.grid(row=7, column=0, columnspan=2, sticky="w", pady=(10, 0))

    budget_progress = ttk.Progressbar(parent, maximum=100, mode="determinate")
    budget_progress.grid(row=8, column=0, columnspan=2, sticky="ew", pady=(12, 0))

    budget_progress_label = ttk.Label(parent, text="Select a budget to see progress.")
    budget_progress_label.grid(row=9, column=0, columnspan=2, sticky="w", pady=(6, 0))

    parent.rowconfigure(6, weight=1)
    parent.columnconfigure(1, weight=1)
    refresh_account_category_choices()
    load_budgets()


def create_stats_tab(parent):
    global stats_month, stats_year, stats_type, stats_limit, stats_canvas, monthly_table, category_stats_table, stats_status

    add_section_title(parent, "Statistics", 0)
    today = dt.date.today()
    stats_month = add_entry(parent, "Month", 1)
    stats_month.insert(0, str(today.month))
    stats_year = add_entry(parent, "Year", 2)
    stats_year.insert(0, str(today.year))
    stats_limit = add_entry(parent, "Months back", 3)
    stats_limit.insert(0, "6")

    ttk.Label(parent, text="Type").grid(row=4, column=0, sticky="w", pady=7)
    stats_type = ttk.Combobox(parent, values=["", "income", "expense"], state="readonly", width=26)
    stats_type.grid(row=4, column=1, sticky="ew", pady=7, padx=(12, 0))

    ttk.Button(parent, text="Load statistics", command=load_stats).grid(row=5, column=0, columnspan=2, sticky="ew", pady=(10, 12))

    stats_canvas = tk.Canvas(parent, height=180, background="#ffffff", highlightthickness=1, highlightbackground="#e5e7eb")
    stats_canvas.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(0, 12))

    category_stats_table = make_table(parent, ("category", "type", "amount", "color"), 7, 5)
    monthly_table = make_table(parent, ("year", "month", "income", "expense", "net"), 8, 5)

    stats_status = ttk.Label(parent, text="", foreground=STATUS_COLOR)
    stats_status.grid(row=9, column=0, columnspan=2, sticky="w", pady=(10, 0))
    parent.rowconfigure(7, weight=1)
    parent.rowconfigure(8, weight=1)
    parent.columnconfigure(1, weight=1)
    load_stats()


def create_admin_users_tab(parent):
    global admin_users_table, admin_users_status

    add_section_title(parent, "Registered users", 0)

    buttons = ttk.Frame(parent)
    buttons.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 12))
    ttk.Button(buttons, text="Block / unblock", command=toggle_admin_user).pack(side="left", expand=True, fill="x", padx=(0, 5))
    ttk.Button(buttons, text="Refresh", command=load_admin_users).pack(side="left", expand=True, fill="x", padx=(5, 0))

    admin_users_table = make_table(parent, ("id", "username", "email", "role", "blocked"), 2, 14)
    admin_users_table.bind("<<TreeviewSelect>>", select_admin_user)

    admin_users_status = ttk.Label(parent, text="", foreground=STATUS_COLOR)
    admin_users_status.grid(row=3, column=0, columnspan=2, sticky="w", pady=(10, 0))
    parent.rowconfigure(2, weight=1)
    parent.columnconfigure(1, weight=1)
    load_admin_users()


def create_admin_stats_tab(parent):
    global admin_stats_labels, admin_stats_status

    add_section_title(parent, "System statistics", 0)
    stats_frame = ttk.Frame(parent)
    stats_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 12))

    admin_stats_labels = {}
    for index, label in enumerate(("Total users", "Active users", "Blocked users", "Transactions")):
        ttk.Label(stats_frame, text=label).grid(row=0, column=index, sticky="w", padx=(0, 18))
        value = ttk.Label(stats_frame, text="0", style="Section.TLabel")
        value.grid(row=1, column=index, sticky="w", padx=(0, 18))
        admin_stats_labels[label] = value

    ttk.Button(parent, text="Refresh", command=load_admin_stats).grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 12))

    admin_stats_status = ttk.Label(parent, text="", foreground=STATUS_COLOR)
    admin_stats_status.grid(row=3, column=0, columnspan=2, sticky="w", pady=(10, 0))
    parent.columnconfigure(1, weight=1)
    load_admin_stats()


def make_table(parent, columns, row, height):
    table = ttk.Treeview(parent, columns=columns, show="headings", height=height)
    for column in columns:
        table.heading(column, text=column.title())
        table.column(column, width=100, anchor="w")
    table.column(columns[0], width=45)
    table.grid(row=row, column=0, columnspan=2, sticky="nsew")
    return table


def add_combo(parent, label, row):
    ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=7)
    combo = ttk.Combobox(parent, state="readonly", width=26)
    combo.grid(row=row, column=1, sticky="ew", pady=7, padx=(12, 0))
    parent.columnconfigure(1, weight=1)
    return combo


def choice_label(item, include_type=False):
    text = f"{item['id']} - {item['name']}"
    if include_type:
        text = f"{text} ({item['type']})"
    return text


def selected_id(combo):
    value = combo.get()
    if not value:
        return None
    return int(value.split(" - ", 1)[0])


def refresh_account_category_choices():
    global accounts_cache, categories_cache
    try:
        accounts_cache = get_accounts()
        categories_cache = get_categories()
    except Exception:
        return

    account_values = [choice_label(account) for account in accounts_cache]
    category_values = [choice_label(category, True) for category in categories_cache]
    budget_values = ["Overall budget"] + category_values

    for combo_name, values in (
        ("transaction_account", account_values),
        ("transaction_category", category_values),
        ("transaction_filter_account", [""] + account_values),
        ("transaction_filter_category", [""] + category_values),
        ("budget_category", budget_values),
    ):
        combo = globals().get(combo_name)
        if combo:
            combo["values"] = values
            if values and not combo.get():
                combo.set(values[0])


def load_accounts():
    accounts_table.delete(*accounts_table.get_children())
    try:
        for account in get_accounts():
            accounts_table.insert("", tk.END, values=(
                account["id"], account["name"], account["type"], account["currency"], account["balance"]
            ))
        refresh_account_category_choices()
    except Exception as exc:
        account_status.config(text=str(exc))


def add_account():
    try:
        data = account_payload()
        if account_exists(data["name"]):
            account_status.config(text="This account already exists.")
            return

        create_account(data)
        account_status.config(text="Account added.")
        clear_account_form()
        load_accounts()
    except ValueError:
        account_status.config(text="Balance must be a number.")
    except Exception as exc:
        account_status.config(text=str(exc))


def save_account_changes():
    if not account_id:
        account_status.config(text="Select an account first.")
        return

    try:
        update_account(account_id, account_payload())
        account_status.config(text="Account updated.")
        clear_account_form()
        load_accounts()
    except ValueError:
        account_status.config(text="Balance must be a number.")
    except Exception as exc:
        account_status.config(text=str(exc))


def account_payload():
    name = account_name.get().strip()
    currency = account_currency.get().strip().upper()

    if not name:
        raise Exception("Please enter account name.")
    if len(name) > 50:
        raise Exception("Account name must be 50 characters or fewer.")
    if len(currency) != 3 or not currency.isalpha():
        raise Exception("Currency must be a 3-letter code.")

    return {"name": name, "type": account_type.get(), "currency": currency, "balance": float(account_balance.get())}


def account_exists(name):
    name = name.lower()
    for row_id in accounts_table.get_children():
        values = accounts_table.item(row_id, "values")
        if values[1].lower() == name:
            return True
    return False


def select_account(event):
    global account_id
    selected = accounts_table.selection()
    if not selected:
        return
    values = accounts_table.item(selected[0], "values")
    account_id = values[0]
    set_entry(account_name, values[1])
    account_type.set(values[2])
    set_entry(account_currency, values[3])
    set_entry(account_balance, values[4])


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
    set_entry(account_name, "")
    account_type.set("cash")
    set_entry(account_currency, "EUR")
    set_entry(account_balance, "0")


def load_categories():
    categories_table.delete(*categories_table.get_children())
    try:
        for category in get_categories():
            categories_table.insert("", tk.END, values=(
                category["id"], category["name"], category["type"], category.get("color") or ""
            ))
        refresh_account_category_choices()
    except Exception as exc:
        category_status.config(text=str(exc))


def save_category():
    name = category_name.get().strip()
    category_kind = category_type.get()
    data = {
        "name": name,
        "type": category_kind,
        "color": category_color.get().strip() or None,
        "icon": None,
    }
    if not name:
        category_status.config(text="Please enter category name.")
        return
    if len(name) > 50:
        category_status.config(text="Category name must be 50 characters or fewer.")
        return
    if category_exists(name, category_kind):
        category_status.config(text="This category already exists.")
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
    set_entry(category_name, values[1])
    category_type.set(values[2])
    set_entry(category_color, values[3])


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
    set_entry(category_name, "")
    category_type.set("expense")
    set_entry(category_color, "#2563eb")


def category_exists(name, category_kind):
    name = name.lower()
    for row_id in categories_table.get_children():
        values = categories_table.item(row_id, "values")
        if values[1].lower() == name and values[2] == category_kind:
            return True
    return False


def load_transactions():
    global transactions_cache

    transactions_cache = {}
    transaction_table.delete(*transaction_table.get_children())
    try:
        filters = transaction_filters()
        for transaction in get_transactions(filters):
            transactions_cache[str(transaction["id"])] = transaction
            account = transaction.get("account") or {}
            category = transaction.get("category") or {}
            transaction_table.insert("", tk.END, values=(
                transaction["id"],
                str(transaction.get("date", ""))[:10],
                account.get("name", transaction["account_id"]),
                category.get("name", transaction["category_id"]),
                category.get("type", ""),
                transaction["amount"],
                transaction["currency"],
                "yes" if transaction.get("is_recurring") else "no",
                transaction["description"],
            ))
        refresh_account_category_choices()
    except Exception as exc:
        transaction_status.config(text=str(exc))


def transaction_filters():
    return {
        "limit": int(transaction_filter_limit.get() or 50),
        "transaction_type": transaction_filter_type.get(),
        "account_id": selected_id(transaction_filter_account),
        "category_id": selected_id(transaction_filter_category),
        "start_date": format_filter_date(transaction_filter_start.get(), False),
        "end_date": format_filter_date(transaction_filter_end.get(), True),
        "search": transaction_filter_search.get().strip(),
        "sort_by": transaction_sort_by.get() or "date",
        "sort_order": transaction_sort_order.get() or "desc",
    }


def format_filter_date(value, end_of_day):
    value = value.strip()
    if not value:
        return None
    try:
        dt.datetime.fromisoformat(value)
    except ValueError:
        dt.datetime.fromisoformat(f"{value}T00:00:00")
    if "T" in value:
        return value
    suffix = "T23:59:59" if end_of_day else "T00:00:00"
    return f"{value}{suffix}"


def clear_transaction_filters():
    transaction_filter_type.set("")
    transaction_filter_account.set("")
    transaction_filter_category.set("")
    set_entry(transaction_filter_start, "")
    set_entry(transaction_filter_end, "")
    set_entry(transaction_filter_search, "")
    transaction_sort_by.set("date")
    transaction_sort_order.set("desc")
    set_entry(transaction_filter_limit, "50")
    load_transactions()


def add_transaction(ignore_budget_limit=False):
    try:
        data = transaction_payload()
        create_transaction(data, ignore_budget_limit=ignore_budget_limit)
        transaction_status.config(text="Transaction added.")
        clear_transaction_form()
        load_accounts()
        load_transactions()
    except ApiError as exc:
        if exc.status == 409:
            confirmed = messagebox.askyesno("Budget exceeded", f"{exc}\n\nSave anyway?")
            if confirmed:
                add_transaction(ignore_budget_limit=True)
            else:
                transaction_status.config(text="Transaction not saved.")
        else:
            transaction_status.config(text=str(exc))
    except ValueError as exc:
        transaction_status.config(text=str(exc))
    except Exception as exc:
        transaction_status.config(text=str(exc))


def save_transaction_changes():
    if not transaction_id:
        transaction_status.config(text="Select a transaction first.")
        return

    try:
        update_transaction(transaction_id, transaction_payload())
        transaction_status.config(text="Transaction updated.")
        clear_transaction_form()
        load_accounts()
        load_transactions()
    except ValueError as exc:
        transaction_status.config(text=str(exc))
    except Exception as exc:
        transaction_status.config(text=str(exc))


def transaction_payload():
    if not transaction_account.get() or not transaction_category.get():
        raise ValueError("Select account and category.")
    description = transaction_description.get().strip()
    currency = transaction_currency.get().strip().upper()
    if not description:
        raise ValueError("Please enter description.")
    if len(currency) != 3 or not currency.isalpha():
        raise ValueError("Currency must be a 3-letter code.")
    try:
        date_value = dt.datetime.fromisoformat(transaction_date.get().strip())
    except ValueError:
        date_value = dt.datetime.fromisoformat(f"{transaction_date.get().strip()}T00:00:00")
    return {
        "account_id": selected_id(transaction_account),
        "category_id": selected_id(transaction_category),
        "amount": float(transaction_amount.get()),
        "currency": currency,
        "date": date_value.isoformat(),
        "description": description,
        "notes": transaction_notes.get().strip() or None,
        "is_recurring": transaction_recurring.get(),
    }


def select_transaction(event):
    global transaction_id
    selected = transaction_table.selection()
    if not selected:
        return
    values = transaction_table.item(selected[0], "values")
    transaction_id = values[0]
    transaction = transactions_cache.get(str(transaction_id))

    if transaction:
        transaction_account.set(find_account_choice(transaction["account_id"]))
        transaction_category.set(find_category_choice_by_id(transaction["category_id"]))
        set_entry(transaction_date, str(transaction.get("date", ""))[:10])
        set_entry(transaction_amount, transaction["amount"])
        set_entry(transaction_currency, transaction["currency"])
        transaction_recurring.set(bool(transaction.get("is_recurring")))
        set_entry(transaction_description, transaction["description"])
        set_entry(transaction_notes, transaction.get("notes") or "")
        return

    set_entry(transaction_date, values[1])
    set_entry(transaction_amount, values[5])
    set_entry(transaction_currency, values[6])
    transaction_recurring.set(values[7] == "yes")
    set_entry(transaction_description, values[8])


def remove_transaction():
    if not transaction_id:
        transaction_status.config(text="Select a transaction first.")
        return
    try:
        delete_transaction(transaction_id)
        clear_transaction_form()
        load_accounts()
        load_transactions()
        transaction_status.config(text="Transaction deleted.")
    except Exception as exc:
        transaction_status.config(text=str(exc))


def clear_transaction_form():
    global transaction_id
    transaction_id = None
    set_entry(transaction_amount, "")
    set_entry(transaction_currency, "EUR")
    set_entry(transaction_date, dt.date.today().isoformat())
    set_entry(transaction_description, "")
    set_entry(transaction_notes, "")
    transaction_recurring.set(False)


def load_budgets():
    global budgets_cache

    budgets_cache = {}
    budgets_table.delete(*budgets_table.get_children())
    try:
        month = int(budget_month.get())
        year = int(budget_year.get())
        for budget in get_budgets(month, year):
            budgets_cache[str(budget["id"])] = budget
            category = budget.get("category") or {}
            amount = float(budget["amount"])
            spent = float(budget.get("spent_amount") or 0)
            used_percent = budget_used_percent(spent, amount)
            budgets_table.insert("", tk.END, values=(
                budget["id"], budget["month"], budget["year"], category.get("name", "Overall"),
                amount, spent, amount - spent, f"{used_percent:.0f}%"
            ))
        refresh_account_category_choices()
        clear_budget_progress()
    except Exception as exc:
        budget_status.config(text=str(exc))


def save_budget():
    global budget_id
    try:
        category = None if budget_category.get() == "Overall budget" else selected_id(budget_category)
        data = {
            "category_id": category,
            "amount": float(budget_amount.get()),
            "month": int(budget_month.get()),
            "year": int(budget_year.get()),
        }
        update_budget(budget_id, data) if budget_id else create_budget(data)
        clear_budget_form()
        load_budgets()
        budget_status.config(text="Budget saved.")
    except Exception as exc:
        budget_status.config(text=str(exc))


def select_budget(event):
    global budget_id
    selected = budgets_table.selection()
    if not selected:
        return
    values = budgets_table.item(selected[0], "values")
    budget_id = values[0]
    set_entry(budget_month, values[1])
    set_entry(budget_year, values[2])
    budget_category.set("Overall budget" if values[3] == "Overall" else find_category_choice(values[3]))
    set_entry(budget_amount, values[4])
    show_budget_progress(values)


def remove_budget():
    if not budget_id:
        budget_status.config(text="Select a budget first.")
        return
    try:
        delete_budget(budget_id)
        clear_budget_form()
        load_budgets()
        budget_status.config(text="Budget deleted.")
    except Exception as exc:
        budget_status.config(text=str(exc))


def clear_budget_form():
    global budget_id
    today = dt.date.today()
    budget_id = None
    set_entry(budget_month, str(today.month))
    set_entry(budget_year, str(today.year))
    if budget_category["values"]:
        budget_category.set(budget_category["values"][0])
    set_entry(budget_amount, "")
    clear_budget_progress()


def budget_used_percent(spent, amount):
    if amount <= 0:
        return 0
    return (spent / amount) * 100


def show_budget_progress(values):
    amount = float(values[4])
    spent = float(values[5])
    remaining = float(values[6])
    percent = budget_used_percent(spent, amount)
    budget_progress["value"] = min(percent, 100)

    state = "OK"
    color = "#16a34a"
    if percent >= 100:
        state = "Exceeded"
        color = "#dc2626"
    elif percent >= 80:
        state = "Near limit"
        color = "#f59e0b"

    budget_progress_label.config(
        text=f"{state}: {spent:.2f} / {amount:.2f} used ({percent:.0f}%), remaining {remaining:.2f}",
        foreground=color,
    )


def clear_budget_progress():
    budget_progress["value"] = 0
    budget_progress_label.config(text="Select a budget to see progress.", foreground=STATUS_COLOR)


def find_category_choice(name):
    for category in categories_cache:
        if category["name"] == name:
            return choice_label(category, True)
    return ""


def find_account_choice(account_id):
    for account in accounts_cache:
        if account["id"] == account_id:
            return choice_label(account)
    return ""


def find_category_choice_by_id(category_id):
    for category in categories_cache:
        if category["id"] == category_id:
            return choice_label(category, True)
    return ""


def load_stats():
    category_stats_table.delete(*category_stats_table.get_children())
    monthly_table.delete(*monthly_table.get_children())
    stats_canvas.delete("all")
    try:
        category_stats = get_category_stats(
            month=int(stats_month.get()),
            year=int(stats_year.get()),
            transaction_type=stats_type.get(),
        )
        monthly_stats = get_monthly_stats(limit_months=int(stats_limit.get()))

        for item in category_stats:
            category_stats_table.insert("", tk.END, values=(
                item["category_name"], item["type"], item["total_amount"], item.get("color") or ""
            ))
        for item in monthly_stats:
            income = float(item.get("income") or 0)
            expense = float(item.get("expense") or 0)
            monthly_table.insert("", tk.END, values=(item["year"], item["month"], income, expense, income - expense))

        draw_stats(category_stats, monthly_stats)
        stats_status.config(text="Statistics loaded.")
    except Exception as exc:
        stats_status.config(text=str(exc))


def draw_stats(category_stats, monthly_stats):
    width = max(stats_canvas.winfo_width(), 700)
    stats_canvas.create_text(16, 16, text="Category totals", anchor="w", fill="#111827", font=("Segoe UI", 10, "bold"))
    total = sum(float(item["total_amount"]) for item in category_stats) or 1
    x = 16
    colors = ["#2563eb", "#16a34a", "#dc2626", "#f59e0b", "#7c3aed", "#0891b2"]
    for index, item in enumerate(category_stats[:6]):
        value = float(item["total_amount"])
        bar_width = int((value / total) * 260)
        y = 38 + index * 22
        color = item.get("color") or colors[index % len(colors)]
        stats_canvas.create_rectangle(x, y, x + bar_width, y + 14, fill=color, outline="")
        stats_canvas.create_text(x + 270, y + 7, text=f"{item['category_name']} {value:.2f}", anchor="w", fill="#1f2937")

    stats_canvas.create_text(width - 300, 16, text="Monthly income / expense", anchor="w", fill="#111827", font=("Segoe UI", 10, "bold"))
    max_total = max([max(float(item.get("income") or 0), float(item.get("expense") or 0)) for item in monthly_stats] or [1])
    start_x = width - 300
    for index, item in enumerate(monthly_stats[:8]):
        base_y = 160
        x_pos = start_x + index * 34
        income_h = int((float(item.get("income") or 0) / max_total) * 90)
        expense_h = int((float(item.get("expense") or 0) / max_total) * 90)
        stats_canvas.create_rectangle(x_pos, base_y - income_h, x_pos + 12, base_y, fill="#16a34a", outline="")
        stats_canvas.create_rectangle(x_pos + 14, base_y - expense_h, x_pos + 26, base_y, fill="#dc2626", outline="")
        stats_canvas.create_text(x_pos + 13, 172, text=calendar.month_abbr[int(item["month"])], fill="#6b7280", font=("Segoe UI", 8))


def load_admin_users():
    admin_users_table.delete(*admin_users_table.get_children())
    try:
        for user in get_users():
            if str(user["role"]).lower() == "admin":
                continue

            admin_users_table.insert("", tk.END, values=(
                user["id"], user["username"], user["email"], user["role"], "yes" if user["is_blocked"] else "no"
            ))
        admin_users_status.config(text="Users loaded.")
    except Exception as exc:
        admin_users_status.config(text=str(exc))


def load_admin_stats():
    try:
        stats = get_system_statistics()
        admin_stats_labels["Total users"].config(text=stats["users"]["total"])
        admin_stats_labels["Active users"].config(text=stats["users"]["active"])
        admin_stats_labels["Blocked users"].config(text=stats["users"]["blocked"])
        admin_stats_labels["Transactions"].config(text=stats["transactions"]["total_registered"])
        admin_stats_status.config(text="Statistics loaded.")
    except Exception as exc:
        admin_stats_status.config(text=str(exc))


def select_admin_user(event):
    global admin_user_id
    selected = admin_users_table.selection()
    if selected:
        admin_user_id = admin_users_table.item(selected[0], "values")[0]


def toggle_admin_user():
    if not admin_user_id:
        admin_users_status.config(text="Select a user first.")
        return
    try:
        toggle_user_block(admin_user_id)
        load_admin_users()
        admin_users_status.config(text="User status changed.")
    except Exception as exc:
        admin_users_status.config(text=str(exc))

