from tkinter import ttk


def clear_window(window):
    for widget in window.winfo_children():
        widget.destroy()


def add_entry(parent, label, row, show=None):
    ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=7)

    entry = ttk.Entry(parent, show=show, width=28)
    entry.grid(row=row, column=1, sticky="ew", pady=7, padx=(12, 0))

    parent.columnconfigure(1, weight=1)
    return entry


def add_section_title(parent, text, row):
    title = ttk.Label(parent, text=text, style="Section.TLabel")
    title.grid(row=row, column=0, columnspan=2, sticky="w", pady=(0, 12))
    return title
