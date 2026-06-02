from tkinter import ttk


def add_entry(parent, label, row, show=None):
    ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=7)

    entry = ttk.Entry(parent, show=show, width=28)
    entry.grid(row=row, column=1, sticky="ew", pady=7, padx=(12, 0))

    parent.columnconfigure(1, weight=1)
    return entry
