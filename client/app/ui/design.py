from tkinter import ttk


WINDOW_BACKGROUND = "#f4f6f8"
TEXT_COLOR = "#1f2937"
TITLE_COLOR = "#111827"
SUBTITLE_COLOR = "#6b7280"
STATUS_COLOR = "#2563eb"
FORM_BACKGROUND = "#ffffff"


def apply_design(window):
    window.configure(bg=WINDOW_BACKGROUND)

    style = ttk.Style()
    style.theme_use("clam")

    style.configure("TFrame", background=FORM_BACKGROUND)
    style.configure("TLabel", background=FORM_BACKGROUND, foreground=TEXT_COLOR, font=("Segoe UI", 10))
    style.configure("Title.TLabel", background=WINDOW_BACKGROUND, foreground=TITLE_COLOR, font=("Segoe UI", 20, "bold"))
    style.configure("Subtitle.TLabel", background=WINDOW_BACKGROUND, foreground=SUBTITLE_COLOR, font=("Segoe UI", 10))
    style.configure("TEntry", padding=6)
    style.configure("TButton", padding=8, font=("Segoe UI", 10, "bold"))
    style.configure("TNotebook", background=WINDOW_BACKGROUND, borderwidth=0)
    style.configure("TNotebook.Tab", padding=(18, 8), font=("Segoe UI", 10))
