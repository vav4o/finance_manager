from tkinter import ttk


def clear_window(window):
    for widget in window.winfo_children():
        widget.destroy()


def add_entry(parent, label, row, show=None):
    ttk.Label(parent, text=label, style="Field.TLabel").grid(row=row, column=0, sticky="w", pady=8)

    entry = ttk.Entry(parent, show=show, width=36)
    entry.grid(row=row, column=1, sticky="ew", pady=8, padx=(14, 0))

    parent.columnconfigure(1, weight=1)
    return entry


def set_entry(entry, value):
    entry.delete(0, "end")
    entry.insert(0, value)


def add_section_title(parent, text, row):
    title = ttk.Label(parent, text=text, style="Section.TLabel")
    title.grid(row=row, column=0, columnspan=2, sticky="w", pady=(0, 16))
    return title
